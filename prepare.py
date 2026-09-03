#!/usr/bin/env python

import sys
import os
import numpy as np
import scipy as sp
import pandas as pd

import tmd

if len(sys.argv) < 2:
    print("./prepare.py <rundir> [--sbs]")
    print("  --sbs: sbs01_root/sbs02_root.dat -> simsbs_{collins,sivers}.dat instead")
    print("  rundir is the run's one directory: reads analysis_neutron's")
    print("  enhancedNpi{p,m}.csv from it and writes simenhanced3he.dat.")
    sys.exit(0)

rundir = sys.argv[1]
os.makedirs(rundir, exist_ok=True)

pseudodata = {}
# pseudodata['sbs01'] = pd.read_csv(f'{rundir}/sbs01.dat', delim_whitespace=True)
# pseudodata['sbs02'] = pd.read_csv(f'{rundir}/sbs02.dat', delim_whitespace=True)
# pseudodata['clas01'] = pd.read_csv('Projections_phifull/clas01.dat', delim_whitespace=True)
# pseudodata['clas02'] = pd.read_csv('Projections_phifull/clas02.dat', delim_whitespace=True)
# pseudodata['basePpip'] = pd.read_csv('Projections_phifull/basePpip.csv', delim_whitespace=False)
# pseudodata['basePpim'] = pd.read_csv('Projections_phifull/basePpim.csv', delim_whitespace=False)
# pseudodata['baseNpip'] = pd.read_csv('Projections_phifull/baseNpip.csv', delim_whitespace=False)
# pseudodata['baseNpim'] = pd.read_csv('Projections_phifull/baseNpim.csv', delim_whitespace=False)
# pseudodata['enhancedPpip'] = pd.read_csv('Projections_phifull/enhancedPpip.csv', delim_whitespace=False)
# pseudodata['enhancedPpim'] = pd.read_csv('Projections_phifull/enhancedPpim.csv', delim_whitespace=False)
# --sbs runs against data_other, which has no SoLID CSVs. These are read at
# import time, so the flag has to be honoured here rather than in __main__.
SBS = '--sbs' in sys.argv
if not SBS:
    pseudodata['enhancedNpip'] = pd.read_csv(f'{rundir}/enhancedNpip.csv', delim_whitespace=False)
    pseudodata['enhancedNpim'] = pd.read_csv(f'{rundir}/enhancedNpim.csv', delim_whitespace=False)

# sbs = pd.concat([pseudodata['sbs01'],pseudodata['sbs02']], axis=0, ignore_index=True)
# clas = pd.concat([pseudodata['clas01'],pseudodata['clas02']], axis=0, ignore_index=True)
# base = pd.concat([pseudodata['basePpip'],pseudodata['basePpim'],pseudodata['baseNpip'],pseudodata['baseNpim']], axis=0, ignore_index=True)
# enhanced = pd.concat([pseudodata['enhancedPpip'],pseudodata['enhancedPpim'],pseudodata['enhancedNpip'],pseudodata['enhancedNpim']], axis=0, ignore_index=True)
# base3he = pd.concat([pseudodata['baseNpip'],pseudodata['baseNpim']], axis=0, ignore_index=True)
enhanced3he = (None if SBS else
               pd.concat([pseudodata['enhancedNpip'],pseudodata['enhancedNpim']], axis=0, ignore_index=True))

OBSERVABLES = ('sivers', 'collins', 'pretzelosity')

# A bin that the acceptance cannot populate at all ends step 2 with Nacc = 0, and
# the C++ side divides by it: stat and systabs come back as -nan. Such a row has no
# information in it, but left in place it makes every chi2 NaN and the fit
# meaningless -- unlike a merely starved bin, whose huge-but-finite error just
# gives it ~zero weight. Drop them here, at the CSV -> fit-input boundary, so the
# raw Projections_* files stay untouched as the provenance record.
# First seen in Projections_phi2seg24degFA_phifullbin (32 rows): the 2x24deg
# forward-angle cut cannot fill some of the bins it inherited from phifull.
# No-op for every dataset generated before that one.
# Since 2026-08-30 the CSV carries one stat column per amplitude, holding the
# Appendix II errors, so the filter is on the column this run actually fits.
# Non-positive is dropped as well as non-finite: AnalyzeEstatUT3 writes -1.0 when
# the inverted MUT3 has a non-positive diagonal, and a negative error passes
# np.isfinite while poisoning any chi2 it reaches.
for o in (() if SBS else OBSERVABLES):
    _stat = f'stat_{o}'
    _bad = ~np.isfinite(enhanced3he[_stat]) | ~np.isfinite(enhanced3he['systabs']) | (enhanced3he[_stat] <= 0)
    if _bad.any():
        print(f'dropping {int(_bad.sum())} of {len(enhanced3he)} rows with non-finite or '
            f'non-positive {_stat}/systabs (Nacc = 0 or singular MUT3 bins in {rundir})')
        enhanced3he = enhanced3he[~_bad].reset_index(drop=True)

# One parameter set per amplitude. collins/sivers are the values the two prepare
# functions below have always used; pretzelosity is a placeholder with a reference.
PAR = {
    'collins':      {'Nu':0.4, 'Nd':-0.45, 'a':1.0, 'b':3.0, 'c':0., 'kt2':0.25},
    'sivers':       {'Nu': -0.03851696777000435,'au': 0.6624828400702693,'bu': 4.103081356761233,'cu': 0.0,'Nd': 0.05141101415846694,'ad': 0.3984321190429335,'bd': 3.1988043553441288,'cd': 0.0,'Nub': 0.0,'Ndb': 0.0,'kt2': 0.16000000088572233},
    # C. Lefky and A. Prokudin, "Extraction of the distribution function
    # h_1T^perp from experimental data", Phys. Rev. D 91, 034010 (2015),
    # arXiv:1411.0580 (report no. JLAB-THY-14-1885). Their Table III, verified
    # against arXiv v1 and v2, which are identical here:
    #     alpha = 2.5 +/- 1.5    beta = 2 fixed
    #     Nu    = 1   +/- 1.4    Nd   = -1 +/- 1.3
    #     MT2   = 0.18 +/- 0.7 GeV^2
    #     chi2min = 163.33,  chi2/ndof = 0.95
    # with their <k_perp^2> = 0.25 GeV^2 (their Sec. II A). Every error exceeds
    # 100% of its central value, and their null test gives P(163.48, 175) = 72%
    # -- the data are consistent with pretzelosity being zero. So this fixes the
    # shape and barely constrains the size; see the placeholder warning in
    # code.md step 5 before quoting anything.
    'pretzelosity': {'Nu':1.0, 'Nd':-1.0, 'a':2.5, 'b':2.0, 'MT2':0.18, 'kt2':0.25},
}

def simulate_all(data):
    """Add the three model asymmetries and their statistical and total errors.

    AUTSivers/AUTCollins/AUTPretzelosity are the model truth at each row's
    kinematics; error_stat_* is the projected statistical error the generator
    wrote; error_tot_* adds the absolute and relative systematics in quadrature,
    the same combination the *syst* file has always used for its fitted
    observable. All three go into both output files so a fit of any amplitude can
    be set up from either one."""
    aut = {o: [] for o in OBSERVABLES}
    for i in range(0,len(data)):
        x, y, z, Q2, pT, target, hadron = data.loc[i]['x'], data.loc[i]['y'], data.loc[i]['z'], data.loc[i]['Q2'], data.loc[i]['pT'], data.loc[i]['target'], data.loc[i]['hadron']
        aut['sivers'].append(tmd.AUTSivers(x, Q2, z, pT, target, hadron, PAR['sivers']))
        aut['collins'].append(tmd.AUTCollins(x, y, Q2, z, pT, target, hadron, PAR['collins']))
        aut['pretzelosity'].append(tmd.AUTPretzelosity(x, y, Q2, z, pT, target, hadron, PAR['pretzelosity']))
    for o in OBSERVABLES:
        data[f'AUT{o.capitalize()}'] = aut[o]
        data[f'error_stat_{o}'] = data[f'stat_{o}']
        data[f'error_tot_{o}'] = (data[f'stat_{o}']**2 + data['systabs']**2
                                  + data[f'AUT{o.capitalize()}']**2 * data['systrel']**2)**0.5

    data.to_csv(f'{rundir}/simenhanced3he.dat', sep='\t', index=False)

    return

def prepare_sbs():
    """sbs01_root/sbs02_root -> simsbs_<obs>.dat, one file per observable.

    The _root pair is the UNCUT SBS projection, all 455 rows straight from the
    ROOT trees (../dump_sbs.C). The cut vintage kept in data_other/sbs_cut/ --
    289 rows, z > 0.3 and q_T <~ 0.6 Q already applied -- is deliberately NOT
    read here; see data_other/README.md for why the two are not interchangeable.

    Different shape from the SoLID path above. These are external projections:
    they arrive with their own `error` column, which is kept untouched, and a
    `value` column of zeros that the model fills -- the same convention the
    generator uses when it writes 0.0 for the SoLID CSVs. There is no fn, no
    systabs and no systrel here, so there is no error_tot to build; the fit reads
    `value` and `error` directly.

    One file per observable because `value` is observable-dependent while the
    kinematics and errors are not. The `obs` column in the raw files says
    AUTsivers on every row regardless -- a legacy label -- so it is rewritten to
    match the file it lands in.
    """
    src = [f'{rundir}/sbs01_root.dat', f'{rundir}/sbs02_root.dat']
    missing = [f for f in src if not os.path.exists(f)]
    if missing:
        sys.exit(f"error: missing {missing}")
    d = pd.concat([pd.read_csv(f, sep=r'\s+') for f in src], ignore_index=True)
    print(f'read {len(d)} rows from {", ".join(os.path.basename(f) for f in src)}')
    for obs in ('collins', 'sivers'):
        out = d.copy()
        val = []
        for i in range(len(out)):
            r = out.loc[i]
            if obs == 'collins':
                val.append(tmd.AUTCollins(r['x'], r['y'], r['Q2'], r['z'], r['pT'],
                                          r['target'], r['hadron'], PAR['collins']))
            else:
                val.append(tmd.AUTSivers(r['x'], r['Q2'], r['z'], r['pT'],
                                         r['target'], r['hadron'], PAR['sivers']))
        out['value'] = val
        out['obs'] = 'AUT' + obs
        path = f'{rundir}/simsbs_{obs}.dat'
        out.to_csv(path, sep='\t', index=False, na_rep='nan')
        print(f'  {path}: {len(out)} rows, mean |value| {np.abs(out["value"]).mean():.5f}')
    return

if __name__ == "__main__":
    if SBS:
        print(f"Preparing the SBS projection ... ({rundir})", end='\n')
        prepare_sbs()
        sys.exit(0)

    print(f"Preparing pseudodata sets for asymmetry ... ({rundir})", end='\n')
    simulate_all(enhanced3he)

    exit
