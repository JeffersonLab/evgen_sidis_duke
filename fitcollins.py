#!/usr/bin/env python

import sys
import os
import numpy as np
import scipy as sp
import pandas as pd
from iminuit import Minuit
from numpy import random
import multiprocessing as mp

# Worker processes for the replica pool, overridden by -w below. The default is
# deliberately small rather than "every core": os.cpu_count() is the machine's
# core count, not this job's allocation, and on a shared node like ifarm taking
# all of it is how you become the reason someone else's job crawls. run_fits.sh
# computes the right number for the host and passes it with -w; a bare
# ./fitcollins.py gets this conservative default.
NWORKERS = 4

# Replica-ensemble knobs. The default is 500 replicas seeded 0..499 (50 until
# 2026-08-24, then 200, then 500 on 2026-08-31 -- see WHAT Nrep BUYS YOU below;
# at ~3.6 s per replica that is ~30 min for a Collins fit, against ~12 min at 200).
# NREP=50 and NREP=200 reproduce the earlier output files byte for byte, since
# replica i's draw depends only on i.
# SEED0 shifts the whole ensemble onto a disjoint stretch of the seed line, so
# runs with different SEED0 are statistically independent ensembles of the same
# fit -- and one NREP=500 run is ten independent 50-replica ensembles, which is
# how the study below was done.
#
# WHAT Nrep BUYS YOU. The error bars downstream are the standard deviation of
# these Nrep fits, so they inherit the sampling uncertainty of a standard
# deviation estimated from Nrep samples:
#
#     sigma(s) / s  =  1 / sqrt(2 (Nrep - 1))
#
#     Nrep =  50  ->  10.1%      Nrep = 200  ->  5.0%
#     Nrep = 100  ->   7.1%      Nrep = 500  ->  3.2%
#
# At the old default Nrep = 50 every quoted error bar -- and every improvement
# factor built from one -- carried ~10% of pure replica noise, and a *ratio* of
# two such error bars ~sqrt(2) x that, ~14%. Three fits of the identical dataset
# gave truncated gT improvements of 10.0x, 12.4x and 14.0x for that reason. The
# default is now 500, which cuts those to 3.2% and 4.5%; results from a 50- or
# 200-replica run are still valid, just noisier, so a factor quoted from one
# needs a range.
#
# Measured, not assumed: on datacollins_phifull the across-ensemble scatter of
# the gT error is 0.098 at Nrep = 50 against the 0.101 predicted above, so the
# formula holds despite the replica distribution being bimodal (~18% of replicas
# land in a second minimum with larger Nu compensated by negative c). The
# bimodality inflates the scatter of individual *parameters* to ~1.55x the
# formula, but leaves gT and the h1 bands on it. Full evidence: check.md.
# Defaults; -n/-s below override them. Command line only -- see the check next
# to the parser for why the environment is no longer read.
NREP  = 500
SEED0 = 0

import tmd

OBS = 'collins'
WORLDDIR = 'data_other'   # world data is shared across runs, not a product of one

if len(sys.argv) < 3:
    print(f"./fit{OBS}.py <opt> <rundir> [-n NREP] [-s SEED0] [-w NWORKERS]")
    print(f"  rundir is the run's one directory: reads prepare.py's")
    print(f"  simenhanced3he.dat from it and writes out-*_{OBS}.dat back.")
    print(f"  World data is shared across runs and lives in {WORLDDIR}/.")
    print("  opts: world")
    print("        enhanced3he  enhanced3hesyst")
    print("        sbs  clas  base  basesyst  enhanced  enhancedsyst")
    print("        sbs+clas  sbs+clas+base  sbs+clas+basesyst")
    print("        sbs+clas+enhanced  sbs+clas+enhancedsyst")
    print("    (the last three lines need the combined proton+neutron sets,")
    print("     which are not generated yet -- the proton path is pending)")
    sys.exit(0)

opt = sys.argv[1]
rundir = sys.argv[2]

# Replica knobs as flags: ./fitcollins.py <opt> <rundir> [-n NREP] [-s SEED0].
# Parsed by hand rather than with argparse so the positional interface and the
# no-argument help above stay exactly as they were, and so an unrecognised
# trailing argument is an error instead of being silently ignored -- a mistyped
# flag must not quietly run 500 replicas.
#
# NREP, SEED0 and NWORKERS used to be environment variables. They are not read from the
# environment any more, and a leftover `NREP=10 ./fitcollins.py ...` -- the form every
# command in runlog.md before 2026-08-31 uses -- would otherwise silently run 500
# replicas instead of 10 and look like it had reproduced the logged run. Refuse it.
for _v, _f in (('NREP', '-n'), ('SEED0', '-s'), ('NWORKERS', '-w')):
    if _v in os.environ:
        sys.exit(f"error: {_v} is no longer read from the environment; "
                 f"pass {_f} {os.environ[_v]} on the command line instead")
_rest = sys.argv[3:]
def _flag(names, current, low):
    global _rest
    while any(n in _rest for n in names):
        n = next(n for n in names if n in _rest)
        i = _rest.index(n)
        if i + 1 >= len(_rest):
            sys.exit(f"error: {n} needs a value")
        v = _rest[i + 1]
        if not v.isdigit() or int(v) < low:
            sys.exit(f"error: {n} must be an integer >= {low}, got '{v}'")
        current = int(v)
        del _rest[i:i + 2]
    return current
def _fflag(names, current):
    """Like _flag but for a positive float. _flag validates with isdigit(),
    which rejects '0.3'."""
    global _rest
    while any(n in _rest for n in names):
        n = next(n for n in names if n in _rest)
        i = _rest.index(n)
        if i + 1 >= len(_rest):
            sys.exit(f"error: {n} needs a value")
        try:
            v = float(_rest[i + 1])
        except ValueError:
            v = -1.0
        if not v > 0:
            sys.exit(f"error: {n} must be a positive number, got '{_rest[i + 1]}'")
        current = v
        del _rest[i:i + 2]
    return current

NREP     = _flag(('-n', '--nrep'),    NREP,     1)
SEED0    = _flag(('-s', '--seed0'),   SEED0,    0)
NWORKERS = _flag(('-w', '--workers'), NWORKERS, 1)
# --tmdcut R: keep only simulated rows with collinearity R1 < R, the
# current-fragmentation criterion of arXiv:1611.10329 (tmd.CalculateRfactor).
# arXiv:2201.12197 uses 0.3, the 2017 paper ~0.2. Default None = no cut.
#
# IT NEVER TOUCHES THE WORLD DATA. The filter lives at the top of fitsim() and
# nowhere else; fitworld() does not call it, and `world` is loaded once below,
# before any of this. That is structural, not a naming convention: opt 'world'
# is the only branch that calls fitworld, every other opt calls fitsim.
TMDCUT   = _fflag(('-t', '--tmdcut'), None)
if _rest:
    sys.exit(f"error: unrecognised argument(s): {' '.join(_rest)}\n"
             f"usage: ./fitcollins.py <opt> <rundir> [-n NREP] [-s SEED0] [-w NWORKERS]"
             f" [-t TMDCUT]")
if TMDCUT is not None and opt == 'world':
    sys.exit("error: --tmdcut does not apply to opt 'world' -- the world data is "
             "never cut. Drop the flag, or pick a simulated opt.")

os.makedirs(rundir, exist_ok=True)

# Datasets load on demand rather than at import. Loading all nine up front meant
# that `world` -- which needs none of the SoLID sets -- still died with a pandas
# FileNotFoundError before the opt was even examined, once the six combined
# proton+neutron sets left the repo. Each entry is (directory, filename, what);
# a directory of None means "this run's rundir".
_COMBINED = 'combined proton+neutron set; not generated yet -- proton path pending'
_PREPARED = 'run this first: ./prepare.py {rundir}'
_DATASETS = {
    'world':           (WORLDDIR, f'colworld_{OBS}.dat',           'world data'),
    # neutron-only SBS projection, prepared into data_other/ alongside the world
    # data it is compared against; run it as `./fitcollins.py sbs data_other`.
    'sbs':             (None,     f'simsbs_{OBS}.dat',             'run this first: prepare the SBS projection into {rundir}'),
    'clas':            (None,     'simclas.dat',                   _COMBINED),
    'base':            (None,     'simbase.dat',                   _COMBINED),
    'basesyst':        (None,     'simbasesyst.dat',               _COMBINED),
    'enhanced':        (None,     'simenhanced.dat',               _COMBINED),
    'enhancedsyst':    (None,     'simenhancedsyst.dat',           _COMBINED),
    # Since 2026-08-31 prepare.py writes ONE file for all three amplitudes, with
    # per-amplitude columns, so both entries read the same path and differ only in
    # which error column load() maps onto 'error'.
    'enhanced3he':     (None,     'simenhanced3he.dat',            _PREPARED),
    'enhanced3hesyst': (None,     'simenhanced3he.dat',            _PREPARED),
}
_loaded = {}

def load(name):
    if name not in _loaded:
        where, fname, what = _DATASETS[name]
        where = rundir if where is None else where
        path = os.path.join(where, fname)
        if not os.path.exists(path):
            print(f"error: opt '{opt}' needs {fname}")
            print(f"looked in: {where}/")
            print(f"({what.format(rundir=rundir)})")
            sys.exit(1)
        df = pd.read_csv(path, delim_whitespace=True)
        # prepare.py's file carries AUTSivers/AUTCollins/AUTPretzelosity and
        # error_{stat,tot}_<amplitude> rather than the single 'value'/'error' pair
        # the rest of this script speaks. Map this run's amplitude onto those two
        # names here, at the one place the file is read, so nothing downstream
        # changes. The world data already has 'value'/'error' and is left alone.
        if name in ('enhanced3he', 'enhanced3hesyst'):
            df['value'] = df[f'AUT{OBS.capitalize()}']
            df['error'] = df[f'error_tot_{OBS}'] if name.endswith('syst') \
                          else df[f'error_stat_{OBS}']
        _loaded[name] = df
    return _loaded[name]

# Every opt fits the world data, on its own (fitworld) or alongside SoLID
# pseudodata (fitsim), so this one is not deferred.
world = load('world')
_NWORLD = len(world)   # asserted unchanged in fitsim(); world must never be cut



# One replica's output row: the fitted parameters, then migrad's parabolic error
# on each in the same order, then chi2.
#
# THE _err COLUMNS ARE NOT THE PROJECTED UNCERTAINTY. That is the spread of the
# parameter across the Nrep replicas -- the standard deviation of a column here --
# which is what code.md step 7 turns into a band. These are each individual fit's
# own error estimate, useful for spotting replicas migrad struggled on (an _err
# far off the column's typical value) and for comparing the two notions. A
# parameter held fixed by the `fix=` list reports 0.
PARS = ('Nu','Nd','a','b','c','kt2')
COLS = list(PARS) + [p + '_err' for p in PARS] + ['chi2', 'ndof', 'edm']

def _row(Min, ndata):
    """One replica's row. ndata is how many data rows entered this fit's chi2.

    ndof counts the free parameters only, so it differs between fitworld (c is
    held fixed there) and fitsim (nothing fixed) -- which is why it is stored per
    replica rather than left for a reader to reconstruct. chi2/ndof should sit
    near 1 and the spread of chi2 across replicas near sqrt(2 ndof).

    edm is migrad's estimated distance to the minimum: convergence quality, not
    an uncertainty. It should be tiny (1e-10 or below at errordef=1); a replica
    with a large edm stopped short and its parameters -- and its _err -- are
    worth less than the rest.

    A FIXED PARAMETER GETS nan, NOT A NUMBER. migrad never varies it, so it has
    no error to report and iminuit echoes back the starting step size from the
    `error=` array -- 1e-4 for every parameter here. Written out that way it is
    indistinguishable from a genuinely tiny uncertainty, and 'c = 0.000 +/-
    0.0001' is a wrong statement rather than a missing one. nan makes any
    arithmetic on the column fail loudly instead."""
    nfree = sum(1 for p in Min.parameters if not Min.fixed[p])
    return ([Min.values[p] for p in PARS]
            + [float('nan') if Min.fixed[p] else Min.errors[p] for p in PARS]
            + [Min.fval, ndata - nfree, Min.fmin.edm])

worldrep = 0
simdata = 0
simdatarep = 0
var0 = 0

def fitfunc0(var):
    par = {'Nu':var[0], 'Nd':var[1], 'a':var[2], 'b':var[3], 'c':var[4], 'kt2':var[5]}
    res = []
    x, y, Q2, z, pT, target, hadron, value, error = worldrep['x'].values, worldrep['y'].values, worldrep['Q2'].values, worldrep['z'].values, worldrep['pT'].values, worldrep['target'].values, worldrep['hadron'].values, worldrep['value'].values, worldrep['error'].values
    for i in range(len(worldrep)):
        res.append( (tmd.AUTCollins(x[i],y[i],Q2[i],z[i],pT[i],target[i],hadron[i],par) - value[i])**2 / error[i]**2)
    return np.sum(res)

def fitfunc(var):
    par = {'Nu':var[0], 'Nd':var[1], 'a':var[2], 'b':var[3], 'c':var[4], 'kt2':var[5]}
    res = []
    x, y, Q2, z, pT, target, hadron, value, error = worldrep['x'].values, worldrep['y'].values, worldrep['Q2'].values, worldrep['z'].values, worldrep['pT'].values, worldrep['target'].values, worldrep['hadron'].values, worldrep['value'].values, worldrep['error'].values
    for i in range(len(worldrep)):
        res.append( (tmd.AUTCollins(x[i],y[i],Q2[i],z[i],pT[i],target[i],hadron[i],par) - value[i])**2 / error[i]**2)
    x, y, Q2, z, pT, target, hadron, value, error = simdatarep['x'].values, simdatarep['y'].values, simdatarep['Q2'].values, simdatarep['z'].values, simdatarep['pT'].values, simdatarep['target'].values, simdatarep['hadron'].values, simdatarep['value'].values, simdatarep['error'].values
    for i in range(len(simdatarep)):
        res.append( (tmd.AUTCollins(x[i],y[i],Q2[i],z[i],pT[i],target[i],hadron[i],par) - value[i])**2 / error[i]**2)
    return np.sum(res)

def _fitworld_one(seed):
    global worldrep
    np.random.seed(seed)
    worldrep = world.copy()
    worldrep['value'] = np.random.normal(world['value'], world['error'])
    Min = Minuit.from_array_func(fitfunc0, start=var0,\
            name=['Nu','Nd','a','b','c','kt2'],\
            error=[1e-4,1e-4,1e-4,1e-4,1e-4,1e-4],\
            fix=[False,False,False,False,True,False],\
            limit=[None,None,None,None,None,None],\
            errordef=1)
    Min.print_level=0
    Min.strategy=1
    Min.migrad()
    row = _row(Min, len(worldrep))
    del Min
    return row

def fitworld(Nrep, filename):
    global var0
    var0 = [0.4, -0.45, 1.0, 3.0, 0.0, 0.25]
    # Nrep sets the precision of the error bar, not of the central value:
    # the spread of these fits is uncertain by 1/sqrt(2(Nrep-1)) -- 5.0% at the
    # default 200. See the NREP comment at the top.
    nworkers = min(NWORKERS, Nrep)
    print(f"fitworld: {Nrep} replicas across {nworkers} worker processes", flush=True)
    with mp.Pool(nworkers) as pool:
        out = pool.map(_fitworld_one, range(SEED0, SEED0 + Nrep))
    fs = pd.DataFrame(out, columns=COLS)
    # na_rep: a fixed parameter's error is nan (see _row). Pandas would write it
    # as an empty field, which reads back fine with sep='\t' but silently shifts
    # every later column for any reader that splits on whitespace -- awk,
    # np.loadtxt, delim_whitespace=True. A literal 'nan' survives both.
    fs.to_csv(filename, sep='\t', index=False, na_rep='nan')
    return

# Puts the SoLID pseudodata and the world data on a single, self-consistent truth
# before the replica fits run: fit world -> par0, then regenerate simdata['value']
# from par0 at each SoLID bin's kinematics. Both datasets enter the same chi2 in
# fitfunc(), so if their central values came from different parameter sets the fit
# would compromise between two incompatible truths -- biasing the result and
# inflating the replica spread for reasons unrelated to SoLID's statistical power.
# Regenerating here makes the tension exactly zero by construction. The returned
# par0 also starts every replica's migrad() at the truth, which keeps them off
# distant local minima.
#
# In this repo all of that degenerates to identity: world's 'value' column IS the
# model at these same start values (chi2 ~ 4e-27), so migrad cannot move, and the
# recomputed simdata['value'] matches what prepare.py wrote to 1e-16. The
# machinery is general; it is a no-op only because the world dataset is synthetic.
def simulate(data):
    global simdata, worldrep
    worldrep = world.copy()
    var0 = [0.4, -0.45, 1.0, 3.0, 0.0, 0.25]
    Min = Minuit.from_array_func(fitfunc0, start=var0,\
                name=['Nu','Nd','a','b','c','kt2'],\
                error=[1e-4,1e-4,1e-4,1e-4,1e-4,1e-4],\
                fix=[False,False,False,False,True,False],\
                limit=[None,None,None,None,None,None],\
                errordef=1)
    Min.print_level=0
    Min.strategy=1
    Min.migrad()
    par0 = Min.values        # name-keyed ValueView -- tmd.AUTCollins needs par['Nu'] etc.
    var0 = Min.np_values()   # positional ndarray -- from_array_func(start=...) needs a sequence
                             # both include fixed params (c), so downstream sees all 6.
                             # NB par0 is a live view on Min, not a copy; safe here because it
                             # is consumed below, before Min goes out of scope.
    val = []
    for i in range(len(simdata)):
        tmp = simdata.loc[i]
        x, y, Q2, z, pT, target, hadron = tmp['x'], tmp['y'], tmp['Q2'], tmp['z'], tmp['pT'], tmp['target'], tmp['hadron']
        val.append(tmd.AUTCollins(x,y,Q2,z,pT,target,hadron,par0))
    simdata['value'] = val
    return var0

def _fitsim_one(seed):
    global simdatarep
    np.random.seed(seed)
    simdatarep = simdata.copy()
    simdatarep['value'] = np.random.normal(simdata['value'], simdata['error'])
    Min = Minuit.from_array_func(fitfunc, start=var0,\
            name=['Nu','Nd','a','b','c','kt2'],\
            error=[1e-4,1e-4,1e-4,1e-4,1e-4,1e-4],\
            fix=[False,False,False,False,False,False],\
            limit=[None,None,None,None,None,None],\
            errordef=1)
    Min.print_level=0
    Min.strategy=1
    Min.migrad()
    row = _row(Min, len(worldrep) + len(simdatarep))
    del Min
    return row

def fitsim(Nrep, filename):
    """Fit world + simdata. The TMD cut, if any, is applied here and only here.

    fitworld() has no equivalent call, so the world data cannot be filtered by
    any code path. The assert below makes a future regression fail loudly rather
    than quietly shrink the reference and flatter every improvement factor.
    """
    global simdata, var0
    if TMDCUT is not None:
        _n0 = len(simdata)
        _R = tmd.CalculateRfactor(simdata['x'], simdata['Q2'],
                                  simdata['z'], simdata['pT'])
        # reset_index: simulate() and _fitsim_one index with .loc[i] over
        # range(len(simdata)), so a gapped index would mis-select rows.
        simdata = simdata[_R < TMDCUT].reset_index(drop=True)
        if len(simdata) == 0:
            sys.exit(f"error: --tmdcut {TMDCUT} left no simulated rows of {_n0}")
        print(f"TMD cut R1 < {TMDCUT:g}: kept {len(simdata)} of {_n0} simulated rows; "
              f"world {len(world)} rows (never cut)", flush=True)
        _root, _ext = os.path.splitext(filename)
        filename = f"{_root}_r1lt{TMDCUT:g}{_ext}"
    assert len(world) == _NWORLD, "world data was filtered -- it must never be"
    var0 = simulate(simdata)
    # Nrep sets the precision of the error bar, not of the central value:
    # the spread of these fits is uncertain by 1/sqrt(2(Nrep-1)) -- 5.0% at the
    # default 200. See the NREP comment at the top.
    nworkers = min(NWORKERS, Nrep)
    print(f"fitsim: {Nrep} replicas across {nworkers} worker processes", flush=True)
    with mp.Pool(nworkers) as pool:
        out = pool.map(_fitsim_one, range(SEED0, SEED0 + Nrep))
    fs = pd.DataFrame(out, columns=COLS)
    # na_rep: a fixed parameter's error is nan (see _row). Pandas would write it
    # as an empty field, which reads back fine with sep='\t' but silently shifts
    # every later column for any reader that splits on whitespace -- awk,
    # np.loadtxt, delim_whitespace=True. A literal 'nan' survives both.
    fs.to_csv(filename, sep='\t', index=False, na_rep='nan')

if __name__ == "__main__":
    print(f'Running the fit to transversity function ... ({rundir})', end='\n')
    if opt == 'world':
        print('fitting world data ...', end='\n')
        fitworld(NREP, f'{rundir}/out-world_{OBS}.dat')
    elif opt == 'sbs':
        print('fitting SBS ...', end='\n')
        simdata = load('sbs').copy()
        fitsim(NREP, f'{rundir}/out-sbs_{OBS}.dat')
    elif opt == 'clas':
        print('fitting CLAS12 ...', end='\n')
        simdata = load('clas').copy()
        fitsim(NREP, f'{rundir}/out-clas_{OBS}.dat')
    elif opt == 'sbs+clas':
        print('fitting SBS+CLAS12 ...', end='\n')
        simdata = pd.concat([load('sbs'),load('clas')], axis=0, ignore_index=True)
        fitsim(NREP, f'{rundir}/out-sbsclas_{OBS}.dat')
    elif opt == 'base':
        print('fitting SoLID baseline ...', end='\n')
        simdata = load('base').copy()
        fitsim(NREP, f'{rundir}/out-base_{OBS}.dat')
    elif opt == 'basesyst':
        print('fitting SoLID baseline (including syst) ...', end='\n')
        simdata = load('basesyst').copy()
        fitsim(NREP, f'{rundir}/out-basesyst_{OBS}.dat')
    elif opt == 'enhanced':
        print('fitting SoLID enhanced ...', end='\n')
        simdata = load('enhanced').copy()
        fitsim(NREP, f'{rundir}/out-enhanced_{OBS}.dat')
    elif opt == 'enhancedsyst':
        print('fitting SoLID enhanced (including syst) ...', end='\n')
        simdata = load('enhancedsyst').copy()
        fitsim(NREP, f'{rundir}/out-enhancedsyst_{OBS}.dat')
    elif opt == 'sbs+clas+base':
        print('fitting SBS+CLAS12+SoLID baseline ...', end='\n')
        simdata = pd.concat([load('sbs'),load('clas'),load('base')], axis=0, ignore_index=True)
        fitsim(NREP, f'{rundir}/out-sbsclasbase_{OBS}.dat')
    elif opt == 'sbs+clas+basesyst':
        print('fitting SBS+CLAS12+SoLID baseline (including syst) ...', end='\n')
        simdata = pd.concat([load('sbs'),load('clas'),load('basesyst')], axis=0, ignore_index=True)
        fitsim(NREP, f'{rundir}/out-sbsclasbasesyst_{OBS}.dat')
    elif opt == 'sbs+clas+enhanced':
        print('fitting SBS+CLAS12+SoLID enhanced ...', end='\n')
        simdata = pd.concat([load('sbs'),load('clas'),load('enhanced')], axis=0, ignore_index=True)
        fitsim(NREP, f'{rundir}/out-sbsclasenhanced_{OBS}.dat')
    elif opt == 'sbs+clas+enhancedsyst':
        print('fitting SBS+CLAS12+SoLID enhancedsyst (including syst) ...', end='\n')
        simdata = pd.concat([load('sbs'),load('clas'),load('enhancedsyst')], axis=0, ignore_index=True)
        fitsim(NREP, f'{rundir}/out-sbsclasenhancedsyst_{OBS}.dat')
    # elif opt == 'base3he':
    #     print('fitting SoLID baseline 3he ...', end='\n')
    #     simdata = base3he.copy()
    #     fitsim(NREP, f'{rundir}/out-base3he_{OBS}.dat')
    # elif opt == 'base3hesyst':
    #     print('fitting SoLID baseline 3he (including syst) ...', end='\n')
    #     simdata = base3hesyst.copy()
    #     fitsim(NREP, f'{rundir}/out-base3hesyst_{OBS}.dat')
    elif opt == 'enhanced3he':
        print('fitting SoLID enhanced 3he ...', end='\n')
        simdata = load('enhanced3he').copy()
        fitsim(NREP, f'{rundir}/out-enhanced3he_{OBS}.dat')
    elif opt == 'enhanced3hesyst':
        print('fitting SoLID enhanced 3he (including syst) ...', end='\n')
        simdata = load('enhanced3hesyst').copy()
        fitsim(NREP, f'{rundir}/out-enhanced3hesyst_{OBS}.dat')
    else:
        print(f"error: unknown opt '{opt}'")
        print('run without arguments to list the opts')
        sys.exit(1)
    
    
    
    
        
        
