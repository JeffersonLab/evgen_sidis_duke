#!/usr/bin/env python

import sys
import os
import numpy as np
import scipy as sp
import pandas as pd
from iminuit import Minuit
from numpy import random
import multiprocessing as mp

NWORKERS = os.cpu_count() or 1

# Replica-ensemble knobs. The default is 200 replicas seeded 0..199 (raised from
# 50 on 2026-08-24 -- see WHAT Nrep BUYS YOU below; the cost is ~12 min instead
# of ~2.5 min for a Collins fit). NREP=50 reproduces every output file written
# before that date byte for byte, since replica i's draw depends only on i.
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
# default is now 200, which cuts those to 5.0% and 7.1%; results from a 50-replica
# run are still valid, just noisier, so a factor quoted from one needs a range.
#
# Measured, not assumed: on datacollins_phifull the across-ensemble scatter of
# the gT error is 0.098 at Nrep = 50 against the 0.101 predicted above, so the
# formula holds despite the replica distribution being bimodal (~18% of replicas
# land in a second minimum with larger Nu compensated by negative c). The
# bimodality inflates the scatter of individual *parameters* to ~1.55x the
# formula, but leaves gT and the h1 bands on it. Full evidence: check.md.
NREP  = int(os.environ.get('NREP', 200))
SEED0 = int(os.environ.get('SEED0', 0))

import tmd

OBS = 'collins'
WORLDDIR = 'data_other'   # world data is shared across runs, not a product of one

if len(sys.argv) < 3:
    print(f"./fit{OBS}.py <opt> <rundir>")
    print(f"  rundir is the run's one directory: reads prepare.py's")
    print(f"  simenhanced3he*_{OBS}.dat from it and writes out-*_{OBS}.dat back.")
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
os.makedirs(rundir, exist_ok=True)

# Datasets load on demand rather than at import. Loading all nine up front meant
# that `world` -- which needs none of the SoLID sets -- still died with a pandas
# FileNotFoundError before the opt was even examined, once the six combined
# proton+neutron sets left the repo. Each entry is (directory, filename, what);
# a directory of None means "this run's rundir".
_COMBINED = 'combined proton+neutron set; not generated yet -- proton path pending'
_PREPARED = f'run this first: ./prepare.py {OBS} {{rundir}}'
_DATASETS = {
    'world':           (WORLDDIR, f'colworld_{OBS}.dat',           'world data'),
    'sbs':             (None,     'simsbs.dat',                    _COMBINED),
    'clas':            (None,     'simclas.dat',                   _COMBINED),
    'base':            (None,     'simbase.dat',                   _COMBINED),
    'basesyst':        (None,     'simbasesyst.dat',               _COMBINED),
    'enhanced':        (None,     'simenhanced.dat',               _COMBINED),
    'enhancedsyst':    (None,     'simenhancedsyst.dat',           _COMBINED),
    'enhanced3he':     (None,     f'simenhanced3he_{OBS}.dat',     _PREPARED),
    'enhanced3hesyst': (None,     f'simenhanced3hesyst_{OBS}.dat', _PREPARED),
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
        _loaded[name] = pd.read_csv(path, delim_whitespace=True)
    return _loaded[name]

# Every opt fits the world data, on its own (fitworld) or alongside SoLID
# pseudodata (fitsim), so this one is not deferred.
world = load('world')


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
    row = [Min.values['Nu'],Min.values['Nd'],Min.values['a'],Min.values['b'],Min.values['c'],Min.values['kt2'],Min.fval]
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
    fs = pd.DataFrame(out, columns=['Nu','Nd','a','b','c','kt2','chi2'])
    fs.to_csv(filename, sep='\t', index=False)
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
    row = [Min.values['Nu'],Min.values['Nd'],Min.values['a'],Min.values['b'],Min.values['c'],Min.values['kt2'],Min.fval]
    del Min
    return row

def fitsim(Nrep, filename):
    global simdata, var0
    var0 = simulate(simdata)
    # Nrep sets the precision of the error bar, not of the central value:
    # the spread of these fits is uncertain by 1/sqrt(2(Nrep-1)) -- 5.0% at the
    # default 200. See the NREP comment at the top.
    nworkers = min(NWORKERS, Nrep)
    print(f"fitsim: {Nrep} replicas across {nworkers} worker processes", flush=True)
    with mp.Pool(nworkers) as pool:
        out = pool.map(_fitsim_one, range(SEED0, SEED0 + Nrep))
    fs = pd.DataFrame(out, columns=['Nu','Nd','a','b','c','kt2','chi2'])
    fs.to_csv(filename, sep='\t', index=False)

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
    
    
    
    
        
        
