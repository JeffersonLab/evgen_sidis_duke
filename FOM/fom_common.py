#!/usr/bin/env python3
"""Shared definitions for the FOM study: the datasets, the bin edges, the cuts,
and the FOM itself.

    FOM(bin) = sum over rows in the bin of 1 / (dA_UT)^2, divided by the bin width

This module holds nothing but definitions -- importing it draws no figure and
reads no file. It exists so that the FOM definition and the cuts live in ONE
place while more than one script draws from them (README.md: "the FOM
definition and the cuts must stay in one place"). Its two consumers:

    plot_fom_solid_vs_sbs.py            the five SoLID-vs-SBS figures
    plot_fom_qtq_vs_theta_grid.py       the (x, Q2) grid of qT/Q vs theta_h maps

The commentary on WHY each dataset, edge array and fudge factor is what it is
lives in plot_fom_solid_vs_sbs.py's docstring and in README.md.
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
def _p(*a): return os.path.join(HERE, *a)

M = 0.938272                                   # proton mass, GeV

# ---------------------------------------------------------------- fom.C edges
# double xSOLID[9] = {0.0, 0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 1.0};
# double xSBS[9]   = {0.0, 0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.78, 1.0};
# double Q2SOLID[9]= {0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0};
XE_SOLID = np.array([0.0, 0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 1.0])
XE_SBS   = np.array([0.0, 0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.78, 1.0])
QE       = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0])
# hxSBS->SetBinContent(7, hxSBS->GetBinContent(7) * 2.3);  ROOT bin 7 -> index 6
SBS_FUDGE = (6, 2.3)

# z and pT are NOT in fom.C -- it makes no such projection. They are also not
# continuous in these files: one row per kinematic bin means both cluster into
# discrete bands, z into 8 clusters with means at 0.33, 0.37, 0.43 ... 0.67 and
# pT into bands ~0.2 apart. Edges finer than the clusters slice between them and
# paint white stripes that read as missing coverage but are an artefact. These
# widths match the bands.
ZE = np.arange(0.30, 0.7001, 0.05)
PE = np.arange(0.00, 1.2001, 0.20)
XE2  = np.arange(0.05, 0.7001, 0.05)           # 2D maps only
QE2  = np.arange(1.00, 10.001, 0.75)
QTQE = np.arange(0.00, 2.0001, 0.10)           # qT/Q = pT/(z*Q); its own 1D figure

SBS_FILES = [_p('..', 'data_other', 'sbs01_root.dat'),
             _p('..', 'data_other', 'sbs02_root.dat')]

# (short, label, path, errcol, colour, marker, x edges, x-bin fudge)
SETS = [
    ('SoLID 2pi', r'SoLID E12-10-006 with $^3$He',
     _p('..', 'phicompare', 'data_phifull', 'simenhanced3he.dat'),
     'error_stat_collins', 'blue', 'o', XE_SOLID, None),
    ('4x24 2pibin', r'SoLID $4\times24^\circ$ $\phi$ cut ($2\pi$ bins)',
     _p('..', 'phicompare', 'data_phi4seg24deg_phifullbin', 'simenhanced3he.dat'),
     'error_stat_collins', 'green', 's', XE_SOLID, None),
    ('SBS', r'SBS E12-09-018 with $^3$He',
     SBS_FILES, 'error', 'red', '^', XE_SBS, SBS_FUDGE),
]


def load(path, errcol, what):
    """Read one .dat, or several concatenated (the SBS pair is split by charge)."""
    paths = [path] if isinstance(path, str) else list(path)
    missing = [q for q in paths if not os.path.exists(q)]
    if missing:
        hint = ("\n       rebuild with:  cd ../data_other && root -l -b -q dump_sbs.C"
                if any('_root.dat' in q for q in missing) else "")
        sys.exit(f"error: missing {missing}\n       (input for '{what}'){hint}")
    d = pd.concat([pd.read_csv(q, sep=r'\s+') for q in paths], ignore_index=True)
    d['W'] = np.sqrt(M**2 + d['Q2'] * (1.0 / d['x'] - 1.0))
    n0 = len(d)
    d = d[(d['W'] > 2.3) & (d['z'] > 0.3) & (d['z'] < 0.7)]
    d = d[np.isfinite(d[errcol]) & (d[errcol] > 0)]
    print(f'  {what:12s} {n0:5d} rows -> {len(d):5d} after W > 2.3 and 0.3 < z < 0.7')
    return d.reset_index(drop=True), errcol


def fom(d, errcol, var, edges, fudge=None):
    """Sum 1/err^2 in each bin of `var`, divided by the bin width.

    Returns (array of [centre, lo, hi, value], list of row counts). `fudge` is
    fom.C's hand scaling of one bin, applied after the width division.
    """
    w = 1.0 / d[errcol].values**2
    idx = np.digitize(d[var].values, edges) - 1
    rows, counts = [], []
    for b in range(len(edges) - 1):
        m = idx == b
        if not m.any():
            continue
        v = w[m].sum() / (edges[b + 1] - edges[b])
        if fudge is not None and b == fudge[0]:
            v *= fudge[1]
        rows.append((0.5 * (edges[b] + edges[b + 1]), edges[b], edges[b + 1], v))
        counts.append(int(m.sum()))
    return np.array(rows), counts
