#!/usr/bin/env python

import sys
import os
import numpy as np
import scipy as sp
import pandas as pd

import tmd

if len(sys.argv) < 3:
    print("./prepare.py <collins|sivers> <rundir>")
    print("  rundir is the run's one directory: reads analysis_neutron's")
    print("  enhancedNpi{p,m}.csv from it and writes simenhanced3he_<obs>.dat")
    print("  and simenhanced3hesyst_<obs>.dat back into it. Required -- the")
    print("  old per-stage defaults made it too easy to prepare one run's")
    print("  pseudodata from another run's projections.")
    sys.exit(0)

opt = sys.argv[1]
if opt not in ('collins', 'sivers'):
    print(f"error: unknown observable '{opt}' (expected collins or sivers)")
    sys.exit(1)
rundir = sys.argv[2]
os.makedirs(rundir, exist_ok=True)

pseudodata = {}
# pseudodata['sbs01'] = pd.read_csv('Projections_phifull/sbs01.dat', delim_whitespace=True)
# pseudodata['sbs02'] = pd.read_csv('Projections_phifull/sbs02.dat', delim_whitespace=True)
# pseudodata['clas01'] = pd.read_csv('Projections_phifull/clas01.dat', delim_whitespace=True)
# pseudodata['clas02'] = pd.read_csv('Projections_phifull/clas02.dat', delim_whitespace=True)
# pseudodata['basePpip'] = pd.read_csv('Projections_phifull/basePpip.csv', delim_whitespace=False)
# pseudodata['basePpim'] = pd.read_csv('Projections_phifull/basePpim.csv', delim_whitespace=False)
# pseudodata['baseNpip'] = pd.read_csv('Projections_phifull/baseNpip.csv', delim_whitespace=False)
# pseudodata['baseNpim'] = pd.read_csv('Projections_phifull/baseNpim.csv', delim_whitespace=False)
# pseudodata['enhancedPpip'] = pd.read_csv('Projections_phifull/enhancedPpip.csv', delim_whitespace=False)
# pseudodata['enhancedPpim'] = pd.read_csv('Projections_phifull/enhancedPpim.csv', delim_whitespace=False)
pseudodata['enhancedNpip'] = pd.read_csv(f'{rundir}/enhancedNpip.csv', delim_whitespace=False)
pseudodata['enhancedNpim'] = pd.read_csv(f'{rundir}/enhancedNpim.csv', delim_whitespace=False)

# sbs = pd.concat([pseudodata['sbs01'],pseudodata['sbs02']], axis=0, ignore_index=True)
# clas = pd.concat([pseudodata['clas01'],pseudodata['clas02']], axis=0, ignore_index=True)
# base = pd.concat([pseudodata['basePpip'],pseudodata['basePpim'],pseudodata['baseNpip'],pseudodata['baseNpim']], axis=0, ignore_index=True)
# enhanced = pd.concat([pseudodata['enhancedPpip'],pseudodata['enhancedPpim'],pseudodata['enhancedNpip'],pseudodata['enhancedNpim']], axis=0, ignore_index=True)
# base3he = pd.concat([pseudodata['baseNpip'],pseudodata['baseNpim']], axis=0, ignore_index=True)
enhanced3he = pd.concat([pseudodata['enhancedNpip'],pseudodata['enhancedNpim']], axis=0, ignore_index=True)

# A bin that the acceptance cannot populate at all ends step 2 with Nacc = 0, and
# the C++ side divides by it: stat and systabs come back as -nan. Such a row has no
# information in it, but left in place it makes every chi2 NaN and the fit
# meaningless -- unlike a merely starved bin, whose huge-but-finite error just
# gives it ~zero weight. Drop them here, at the CSV -> fit-input boundary, so the
# raw Projections_* files stay untouched as the provenance record.
# First seen in Projections_phi2seg24degFA_phifullbin (32 rows): the 2x24deg
# forward-angle cut cannot fill some of the bins it inherited from phifull.
# No-op for every dataset generated before that one.
_bad = ~np.isfinite(enhanced3he['stat']) | ~np.isfinite(enhanced3he['systabs'])
if _bad.any():
    print(f'dropping {int(_bad.sum())} of {len(enhanced3he)} rows with non-finite stat/systabs '
          f'(Nacc = 0 bins in {rundir})')
    enhanced3he = enhanced3he[~_bad].reset_index(drop=True)

def simulatecollins(data, var):
    val = []
    for i in range(0,len(data)):
        x, y, z, Q2, pT, target, hadron = data.loc[i]['x'], data.loc[i]['y'], data.loc[i]['z'], data.loc[i]['Q2'], data.loc[i]['pT'], data.loc[i]['target'], data.loc[i]['hadron']
        val.append(tmd.AUTCollins(x, y, Q2, z, pT, target, hadron, var))
    data['value'] = val
    return

def simulatesivers(data, var):
    val = []
    for i in range(0,len(data)):
        x, y, z, Q2, pT, target, hadron = data.loc[i]['x'], data.loc[i]['y'], data.loc[i]['z'], data.loc[i]['Q2'], data.loc[i]['pT'], data.loc[i]['target'], data.loc[i]['hadron']
        val.append(tmd.AUTSivers(x, Q2, z, pT, target, hadron, var))
    data['value'] = val
    return

def preparecollins():
    global sbs, clas, base, enhanced
    par0 = {'Nu':0.4, 'Nd':-0.45, 'a':1.0, 'b':3.0, 'c':0., 'kt2':0.25}
    # simulatecollins(sbs,par0)
    # simulatecollins(clas,par0)
    # simulatecollins(base,par0)
    # simulatecollins(enhanced,par0)
    # simulatecollins(base3he,par0)
    simulatecollins(enhanced3he,par0)
    # sbsrep = sbs.copy()
    # clasrep = clas.copy()
    # baserep = base.copy()
    # baserep['error'] = base['stat']
    # basesystrep = base.copy()
    # basesystrep['error'] = (base['stat']**2+base['systabs']**2+base['value']**2*base['systrel']**2)**0.5
    # enhancedrep = enhanced.copy()
    # enhancedrep['error'] = enhanced['stat']
    # enhancedsystrep = enhanced.copy()
    # enhancedsystrep['error'] = (enhanced['stat']**2+enhanced['systabs']**2+enhanced['value']**2*enhanced['systrel']**2)**0.5
    # base3herep = base3he.copy()
    # base3herep['error'] = base3he['stat']
    # base3hesystrep = base3he.copy()
    # base3hesystrep['error'] = (base3he['stat']**2+base3he['systabs']**2+base3he['value']**2*base3he['systrel']**2)**0.5
    enhanced3herep = enhanced3he.copy()
    enhanced3herep['error'] = enhanced3he['stat']
    enhanced3hesystrep = enhanced3he.copy()
    enhanced3hesystrep['error'] = (enhanced3he['stat']**2+enhanced3he['systabs']**2+enhanced3he['value']**2*enhanced3he['systrel']**2)**0.5
    # sbsrep.to_csv('datacollins_phifull/simsbs.dat', sep='\t', index=False)
    # clasrep.to_csv('datacollins_phifull/simclas.dat', sep='\t', index=False)
    # baserep.to_csv('datacollins_phifull/simbase.dat', sep='\t', index=False)
    # basesystrep.to_csv('datacollins_phifull/simbasesyst.dat', sep='\t', index=False)
    # enhancedrep.to_csv('datacollins_phifull/simenhanced.dat', sep='\t', index=False)
    # enhancedsystrep.to_csv('datacollins_phifull/simenhancedsyst.dat', sep='\t', index=False)
    # base3herep.to_csv('datacollins_phifull/simbase3he.dat', sep='\t', index=False)
    # base3hesystrep.to_csv('datacollins_phifull/simbase3hesyst.dat', sep='\t', index=False)
    enhanced3herep.to_csv(f'{rundir}/simenhanced3he_{opt}.dat', sep='\t', index=False)
    enhanced3hesystrep.to_csv(f'{rundir}/simenhanced3hesyst_{opt}.dat', sep='\t', index=False)
    return

def preparesivers():
    global sbs, clas, base, enhanced
    par1 = {'Nu': -0.03851696777000435,'au': 0.6624828400702693,'bu': 4.103081356761233,'cu': 0.0,'Nd': 0.05141101415846694,'ad': 0.3984321190429335,'bd': 3.1988043553441288,'cd': 0.0,'Nub': 0.0,'Ndb': 0.0,'kt2': 0.16000000088572233}
    # simulatesivers(sbs,par1)
    # simulatesivers(clas,par1)
    # simulatesivers(base,par1)
    # simulatesivers(enhanced,par1)
    # simulatesivers(base3he,par1)
    simulatesivers(enhanced3he,par1)
    # sbsrep = sbs.copy()
    # clasrep = clas.copy()
    # baserep = base.copy()
    # baserep['error'] = base['stat']
    # basesystrep = base.copy()
    # basesystrep['error'] = (base['stat']**2+base['systabs']**2+base['value']**2*base['systrel']**2)**0.5
    # enhancedrep = enhanced.copy()
    # enhancedrep['error'] = enhanced['stat']
    # enhancedsystrep = enhanced.copy()
    # enhancedsystrep['error'] = (enhanced['stat']**2+enhanced['systabs']**2+enhanced['value']**2*enhanced['systrel']**2)**0.5
    # base3herep = base3he.copy()
    # base3herep['error'] = base3he['stat']
    # base3hesystrep = base3he.copy()
    # base3hesystrep['error'] = (base3he['stat']**2+base3he['systabs']**2+base3he['value']**2*base3he['systrel']**2)**0.5
    enhanced3herep = enhanced3he.copy()
    enhanced3herep['error'] = enhanced3he['stat']
    enhanced3hesystrep = enhanced3he.copy()
    enhanced3hesystrep['error'] = (enhanced3he['stat']**2+enhanced3he['systabs']**2+enhanced3he['value']**2*enhanced3he['systrel']**2)**0.5
    # sbsrep.to_csv('datasivers_phifull/simsbs.dat', sep='\t', index=False)
    # clasrep.to_csv('datasivers_phifull/simclas.dat', sep='\t', index=False)
    # baserep.to_csv('datasivers_phifull/simbase.dat', sep='\t', index=False)
    # basesystrep.to_csv('datasivers_phifull/simbasesyst.dat', sep='\t', index=False)
    # enhancedrep.to_csv('datasivers_phifull/simenhanced.dat', sep='\t', index=False)
    # enhancedsystrep.to_csv('datasivers_phifull/simenhancedsyst.dat', sep='\t', index=False)
    # base3herep.to_csv('datasivers_phifull/simbase3he.dat', sep='\t', index=False)
    # base3hesystrep.to_csv('datasivers_phifull/simbase3hesyst.dat', sep='\t', index=False)
    enhanced3herep.to_csv(f'{rundir}/simenhanced3he_{opt}.dat', sep='\t', index=False)
    enhanced3hesystrep.to_csv(f'{rundir}/simenhanced3hesyst_{opt}.dat', sep='\t', index=False)
    return




if __name__ == "__main__":
    if opt == 'collins':
        print(f"Preparing pseudodata sets for Collins asymmetry ... ({rundir})", end='\n')
        preparecollins()
    elif opt == 'sivers':
        print(f"Preparing pseudodata sets for Sivers asymmetry ... ({rundir})", end='\n')
        preparesivers()

    exit
