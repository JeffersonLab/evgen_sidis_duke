#!/usr/bin/env python3
"""Figure of merit, SoLID 3He against SBS -- the right panel of Fig. 1 (p. 3) of
the SoLID pre-CDR, solid-precdr-2019Nov.pdf (DocDB 282).

    FOM(bin) = sum over rows in the bin of 1 / (dA_UT)^2, divided by the bin width

"the sum of the inverse square of the statistical uncertainties of the single
spin asymmetry (roughly proportional to statistics)", with W > 2.3 GeV and
0.3 < z < 0.7 applied to every dataset. Statistical errors only.

INPUTS
  SoLID full 2pi        error_stat_collins  ../phicompare/data_phifull/simenhanced3he.dat
  SoLID 4x24 (2pi bins) error_stat_collins  ../phicompare/data_phi4seg24deg_phifullbin/...
  SBS                   error               ../data_other/sbs0{1,2}_root.dat

The SBS curve is the SAME INPUT the published figure used: the four trees
sbs_neutron_pi{p,m}_{8,11}.root that fom.C chains, 455 entries, converted to
sbs01/sbs02 format by ../data_other/dump_sbs.C. `../data_other/simsbs_collins.dat`
and the plain sbs01/sbs02.dat are NOT used: those are a thinned 289-row subset of
the same trees, holding only 15 of the 102 rows they carry in 0.15 < x < 0.25,
which made that point read 6.9x low. See README.md and ../data_other/README.md.

BIN EDGES are fom.C's, not uniform, and NOT the same for the two experiments:
SoLID stops its last bin at 0.65, SBS at 0.78. fom.C then multiplies SBS's
0.55-0.78 bin by 2.3 -- a hand normalisation that happens to cancel that bin's
0.23 width, i.e. it redraws the point at a 0.1-wide density. Reproduced here so
the panel matches the publication, and flagged on the figure and in the console
so nobody mistakes it for a measurement.

All inputs carry the 1/(f_n * 0.6 * 0.86) dilution-and-polarisation scaling, so
they are the same kind of quantity. No file carries W; it is computed here as
W = sqrt(M^2 + Q^2 (1/x - 1)).

  source /usr/share/Modules/init/zsh && source ../setup.sh && ./plot_fom_solid_vs_sbs.py
"""
import os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fom_common import (HERE, _p, M, XE_SOLID, XE_SBS, QE, SBS_FUDGE, ZE, PE,
                        XE2, QE2, QTQE, SBS_FILES, SETS, load, fom)



# ---------------------------------------------------------------- load
print('Figure of merit, SoLID 3He vs SBS:')
loaded = []
for short, label, path, errcol, colour, marker, xe, fud in SETS:
    d, ec = load(path, errcol, short)
    d['qTQ'] = d['pT'] / (d['z'] * np.sqrt(d['Q2']))    # qT/Q, qT = pT/z
    loaded.append((short, label, d, ec, colour, marker, xe, fud))

CUTS = r'statistical errors only'
# The bounds the SoLID generator actually runs inside -- not a cut this script
# applies, and not true of SBS (its Q2 reaches 9.5, past the SoLID ceiling of 8):
# Wp > 1.6 GeV is SoLID_SIDIS_3He.h's current-fragmentation cut (see ../physics.md);
# 1 < Q2 < 8 GeV^2 and pT < 1.6 GeV are GenerateBinInfoFile's Q2list/Ptlist ranges.
GENCOND = (r"$W>2.3$ GeV, $W'>1.6$ GeV, $0.3<z<0.7$, $1<Q^2<8$ GeV$^2$, "
           r"$p_T<1.6$ GeV")
# ---------------------------------------------------------------- 1D in x
fig, ax = plt.subplots(figsize=(6.8, 5.4))
table = {}
for short, label, d, ec, colour, marker, xe, fud in loaded:
    f, n = fom(d, ec, 'x', xe, fud)
    table[short] = (f, n)
    ax.errorbar(f[:, 0], f[:, 3], xerr=[f[:, 0] - f[:, 1], f[:, 2] - f[:, 0]],
                fmt=marker, color=colour, markersize=6 if marker == 'D' else 7,
                elinewidth=1.4, capsize=0, linestyle='none', label=label)
ax.set_yscale('log')
ax.set_xlim(0, 0.8)
ax.set_ylim(1e4, 2e9)
ax.set_xlabel(r'$x$', size=14)
ax.set_ylabel(r'FOM: $(\delta A_{UT})^{-2}\,/\,\Delta x$', size=14)
ax.tick_params(axis='both', which='both', direction='in', top=True, right=True, labelsize=12)
ax.legend(loc='lower left', frameon=True, fontsize=9)
ax.text(0.97, 0.965, CUTS.replace(', ', ',\n', 1), transform=ax.transAxes,
        ha='right', va='top', fontsize=9, color='0.3')
ax.text(0.97, 0.845, GENCOND.replace(', ', ',\n', 1), transform=ax.transAxes,
        ha='right', va='top', fontsize=7, color='0.45')
fig.tight_layout(rect=[0, 0.035, 1, 1])
for ext in ('png', 'pdf'):
    q = _p(f'fom-solid-vs-sbs.{ext}')
    fig.savefig(q, dpi=150 if ext == 'png' else None)
    print(f'wrote {q}')

names = [s for s, *_ in loaded]
allbins = sorted({(round(r[1], 3), round(r[2], 3)) for s in names for r in table[s][0]})
print(f"\n  {'x bin':>11s}" + ''.join(f'{nm+" FOM":>16s}{"n":>5s}' for nm in names))
for lo, hi in allbins:
    cells = ''
    for nm in names:
        f, n = table[nm]
        j = [k for k, r in enumerate(f) if round(r[1], 3) == lo and round(r[2], 3) == hi]
        cells += f'{f[j[0]][3]:16.3e}{n[j[0]]:5d}' if j else f'{"-":>16s}{"-":>5s}'
    print(f"  {lo:.2f}-{hi:.2f}{cells}")

# ------------------------------------------------------------ 1D in qT/Q
# qT/Q separates the TMD current-fragmentation region (small qT/Q) from where
# TMD factorisation is not expected to hold -- see ../physics.md and
# tmd.CalculateRfactor. No fom.C precedent for this axis, so no per-bin fudge
# and one edge array for every dataset (unlike the x panel above).
fig2q, ax = plt.subplots(figsize=(6.8, 5.4))
table_q = {}
for short, label, d, ec, colour, marker, xe, fud in loaded:
    f, n = fom(d, ec, 'qTQ', QTQE)
    table_q[short] = (f, n)
    ax.errorbar(f[:, 0], f[:, 3], xerr=[f[:, 0] - f[:, 1], f[:, 2] - f[:, 0]],
                fmt=marker, color=colour, markersize=6 if marker == 'D' else 7,
                elinewidth=1.4, capsize=0, linestyle='none', label=label)
ax.set_yscale('log')
ax.set_xlim(QTQE[0], QTQE[-1])
ax.set_xlabel(r'$q_T/Q$', size=14)
ax.set_ylabel(r'FOM: $(\delta A_{UT})^{-2}\,/\,\Delta(q_T/Q)$', size=14)
ax.tick_params(axis='both', which='both', direction='in', top=True, right=True, labelsize=12)
ax.legend(loc='upper right', frameon=True, fontsize=9)
fig2q.text(0.5, 0.005, CUTS + '\n' + GENCOND, ha='center', va='bottom', fontsize=8, color='0.35')
fig2q.tight_layout(rect=[0, 0.06, 1, 1])
for ext in ('png', 'pdf'):
    q = _p(f'fom-solid-vs-sbs-qtQ.{ext}')
    fig2q.savefig(q, dpi=150 if ext == 'png' else None)
    print(f'wrote {q}')

names_q = [s for s, *_ in loaded]
print(f"\n  {'qT/Q bin':>11s}" + ''.join(f'{nm+" FOM":>16s}{"n":>5s}' for nm in names_q))
for i in range(len(QTQE) - 1):
    lo, hi = QTQE[i], QTQE[i + 1]
    cells = ''
    for nm in names_q:
        f, n = table_q[nm]
        j = [k for k, r in enumerate(f) if abs(r[1] - lo) < 1e-9 and abs(r[2] - hi) < 1e-9]
        cells += f'{f[j[0]][3]:16.3e}{n[j[0]]:5d}' if j else f'{"-":>16s}{"-":>5s}'
    print(f"  {lo:.2f}-{hi:.2f}{cells}")

# ---------------------------------------------------------------- 2D maps
def fom2d(d, errcol, v1, v2, e1, e2):
    w = 1.0 / d[errcol].values**2
    H, _, _ = np.histogram2d(d[v1].values, d[v2].values, bins=[e1, e2], weights=w)
    H = H / np.outer(np.diff(e1), np.diff(e2))
    return np.ma.masked_where(H <= 0, H)


def map_figure(v1, v2, e1, e2, xlabel, ylabel, cblabel, title, fname, overlay=None):
    maps = [(s, lab, fom2d(d, ec, v1, v2, e1, e2)) for s, lab, d, ec, *_ in loaded]
    vmax = max(m.max() for _, _, m in maps)
    vmin = max(min(m.min() for _, _, m in maps), vmax / 1e7)
    fig, axes = plt.subplots(2, 2, figsize=(11.4, 8.6), sharex=True, sharey=True)
    g1, g2 = np.meshgrid(e1, e2, indexing='ij')
    for axx, (s, lab, H) in zip(axes.ravel(), maps):
        pc = axx.pcolormesh(g1, g2, H, norm=LogNorm(vmin=vmin, vmax=vmax),
                            cmap='viridis', shading='flat')
        if overlay is not None:
            axx.plot(*overlay, color='w', ls='--', lw=1.4)
            axx.plot(*overlay, color='k', ls='--', lw=0.7)
        axx.set_title(lab, fontsize=11)
        axx.set_xlim(e1[0], e1[-1]); axx.set_ylim(e2[0], e2[-1])
        axx.tick_params(direction='in', top=True, right=True, labelsize=10)
    for axx in axes[-1]: axx.set_xlabel(xlabel, size=13)
    for axx in axes[:, 0]: axx.set_ylabel(ylabel, size=13)
    cb = fig.colorbar(pc, ax=axes, fraction=0.045, pad=0.02)
    cb.set_label(cblabel, size=12)
    fig.suptitle(title, fontsize=11.5)
    for ext in ('png', 'pdf'):
        q = _p(f'{fname}.{ext}')
        fig.savefig(q, dpi=150 if ext == 'png' else None, bbox_inches='tight')
        print(f'wrote {q}')
    print(f"  {'dataset':13s} {'cells':>6s} {'max FOM':>12s} {'total sum 1/err^2':>19s}")
    for (s, lab, H), (_, _, d, ec, *_) in zip(maps, loaded):
        print(f"  {s:13s} {H.count():6d} {H.max():12.3e} {(1/d[ec]**2).sum():19.4e}")
    print()


_xx = np.linspace(XE2[0], XE2[-1], 200)
map_figure('x', 'Q2', XE2, QE2, r'$x$', r'$Q^2$  (GeV$^2$)',
           r'FOM: $(\delta A_{UT})^{-2}\,/\,(\Delta x\,\Delta Q^2)$',
           r'Figure of merit in $(x,\,Q^2)$   —   ' + CUTS + r'   (dashed: $W=2.3$ GeV)' + '\n' + GENCOND,
           'fom-solid-vs-sbs-2d',
           overlay=(_xx, (2.3**2 - M**2) * _xx / (1 - _xx)))
map_figure('z', 'pT', ZE, PE, r'$z$', r'$p_T$  (GeV)',
           r'FOM: $(\delta A_{UT})^{-2}\,/\,(\Delta z\,\Delta p_T)$',
           r'Figure of merit in $(z,\,p_T)$   —   ' + CUTS + '\n' + GENCOND,
           'fom-solid-vs-sbs-2d-zpt')

# ------------------------------------------------- 1D projections, four panels
# Each panel is a sum over every OTHER variable, so the four are four views of
# the same total statistics. x uses each dataset's own fom.C edges (SoLID and SBS
# genuinely differ in the last bin); Q2 uses fom.C's; z and pT are ours.
PANELS = [('x',  None, r'$x$',              r'$\Delta x$'),
          ('Q2', QE,   r'$Q^2$  (GeV$^2$)', r'$\Delta Q^2$'),
          ('z',  ZE,   r'$z$',              r'$\Delta z$'),
          ('pT', PE,   r'$p_T$  (GeV)',     r'$\Delta p_T$')]

fig3, axes3 = plt.subplots(2, 2, figsize=(11.0, 8.2))
for axx, (var, ed, xlabel, dlabel) in zip(axes3.ravel(), PANELS):
    for short, label, d, ec, colour, marker, xe, fud in loaded:
        e = xe if ed is None else ed
        f, n = fom(d, ec, var, e, fud if ed is None else None)
        if not len(f):
            continue
        axx.errorbar(f[:, 0], f[:, 3], xerr=[f[:, 0] - f[:, 1], f[:, 2] - f[:, 0]],
                     fmt=marker, color=colour, markersize=6 if marker == 'D' else 6.5,
                     elinewidth=1.3, capsize=0, linestyle='none', label=label)
    axx.set_yscale('log')
    axx.set_xlim(0 if ed is None else ed[0], 0.8 if ed is None else ed[-1])
    axx.set_xlabel(xlabel, size=13)
    axx.set_ylabel(r'FOM: $(\delta A_{UT})^{-2}\,/\,$' + dlabel, size=12)
    axx.tick_params(axis='both', which='both', direction='in', top=True, right=True, labelsize=11)
    axx.grid(alpha=0.25, which='major')

# Each panel keeps its OWN y range on purpose: the four quantities are FOM per
# dx, per dQ2, per dz and per dpT -- different units, so levels must not be read
# across panels. Within a panel the four datasets share the axis, which is what
# this figure is for.
for axx in axes3.ravel():
    ys = np.concatenate([l.get_ydata() for l in axx.get_lines() if len(l.get_ydata())])
    ys = ys[ys > 0]
    axx.set_ylim(10**np.floor(np.log10(ys.min()) - 0.15),
                 10**np.ceil(np.log10(ys.max()) + 0.15))

h, l = axes3[0][0].get_legend_handles_labels()
fig3.legend(h, l, loc='lower center', ncol=4, frameon=False, fontsize=10,
            bbox_to_anchor=(0.5, -0.005))
fig3.suptitle(r'Figure of merit projected onto each variable   —   ' + CUTS + '\n' + GENCOND, fontsize=11)
fig3.tight_layout(rect=[0, 0.045, 1, 0.94])
for ext in ('png', 'pdf'):
    q = _p(f'fom-solid-vs-sbs-1d4.{ext}')
    fig3.savefig(q, dpi=150 if ext == 'png' else None)
    print(f'wrote {q}')
