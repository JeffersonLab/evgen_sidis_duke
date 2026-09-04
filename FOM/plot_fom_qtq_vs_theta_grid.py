#!/usr/bin/env python3
"""Figure of merit in (qT/Q, theta_h_lab), one map per (x, Q2) cell, the cells
tiled into one big (x, Q2) grid -- one figure per dataset.

    FOM(cell) = sum over rows of 1/(dA_UT)^2, divided by the cell area

the same FOM as plot_fom_solid_vs_sbs.py (both import fom_common), with the same
W > 2.3 GeV and 0.3 < z < 0.7 cuts. Grid cells are 1 GeV^2 in Q2 and 0.1 in x;
inside each cell the map is binned in the hadron's LAB POLAR ANGLE and in
qT/Q = pT/(z Q). Rows and columns with no data are trimmed away.

Three figures, one per dataset in fom_common.SETS, on a SHARED colour scale so
they can be read against each other:

    fom-qtq-vs-theta-grid-solid2pi.*             SoLID full 2pi
    fom-qtq-vs-theta-grid-solid-phi4seg24deg.*   SoLID 4x24 deg phi cut (2pi bins)
    fom-qtq-vs-theta-grid-sbs.*                  SBS

THE ONE THING TO KNOW BEFORE READING THESE FIGURES.  **No input file carries the
hadron's lab angle.** Every row is a kinematic bin in (x, Q2, z, pT) already
INTEGRATED OVER phi_h, and theta_h depends on phi_h: at fixed (Ebeam, Q2, x, z,
pT) the hadron's momentum is fixed in magnitude and its polar angle relative to
the virtual photon is fixed too, but where it sits in azimuth about q is not, and
that azimuth is exactly what moves it in lab angle. So one row is not a point on
these maps, it is a HORIZONTAL SEGMENT: one qT/Q, a range of theta_h.

This script therefore spreads each row's weight 1/(dA_UT)^2 UNIFORMLY over
phi_h, in PHI_N equal steps. Uniform is the natural default -- the phi_h
dependence of the yield is a modulation on top of a phi-independent FUUT -- but
it is an assumption, and it is wrong in one specific way that matters:

    the acceptance already chose the phi_h values.

SoLID's pions are accepted only in 8-18 deg (SoLID_SIDIS_3He.h:196, :209), so a
bin only has rows at all because SOME phi_h put the hadron in that band. Spread
uniformly, the same weight also lands at angles the detector never saw. The band
is shaded on the SoLID figures and the fraction of FOM inside it is printed;
--accepted-only instead keeps only the phi_h that land in the band, which is the
other end of the same approximation: a hard 8/18 deg cut with no momentum
dependence, where the real acceptance map has both.

So: the default figure answers "where COULD these events have put the hadron",
--accepted-only answers "where does SoLID's angular acceptance allow them to be".
Neither is a measurement of the lab-angle distribution; nothing in this repo's
row-level output is.

KINEMATICS, per row, target at rest, all from columns the files already carry:

    nu   = Q2 / (2 M x)             Ebeam = nu / y          E' = Ebeam - nu
    cos(theta_e)  = 1 - Q2 / (2 Ebeam E')
    cos(theta_q)  = (Ebeam - E' cos(theta_e)) / |q|,   |q| = sqrt(nu^2 + Q2)
    E_h  = z nu    ->   |P_h| = sqrt(E_h^2 - m_h^2)   ->   pL = sqrt(|P_h|^2 - pT^2)
    cos(theta_h)  = [ pT cos(phi_h) sin(theta_q) + pL cos(theta_q) ] / |P_h|

the closed form of the frame construction in ../kinematics/plot_qtq_vs_theta.py
(which is itself Lsidis3.h:CalculateFinalStateKinematics for a target at rest,
validated against the header by ../kinematics/check_against_lsidis.C). The
lepton plane is oriented with the scattered electron on beam left, so phi_h = 0
tilts the hadron back toward the beam and phi_h = 180 deg tilts it away, onto the
far side of the virtual photon.

  source /usr/share/Modules/init/zsh && source ../setup.sh && ./plot_fom_qtq_vs_theta_grid.py
  ./plot_fom_qtq_vs_theta_grid.py --accepted-only
"""
import os, sys, argparse
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fom_common import _p, M, SETS, load

# ------------------------------------------------------------------- binning
# The grid the panels are laid out on: 1 GeV^2 in Q2, 0.1 in x. Both run over
# the full range any dataset here can reach; empty rows and columns are trimmed
# before drawing, so widening these costs nothing.
XGRID = np.arange(0.0, 1.0001, 0.1)
QGRID = np.arange(0.0, 10.001, 1.0)

# The axes INSIDE each panel. Panels are small, so these are deliberately
# coarser than the 1D edges in fom_common.
TE = np.arange(0.0, 45.001, 1.5)               # hadron lab polar angle, deg
RE = np.arange(0.0, 2.0001, 0.10)              # qT/Q = pT/(z Q); fom_common.QTQE width

PHI_N = 180                                    # phi_h samples per row

MH = {'pi+': 0.13957, 'pi-': 0.13957, 'K+': 0.493677, 'K-': 0.493677}

# SoLID pion acceptance, forward angle only: SoLID_SIDIS_3He.h GetAcceptance_pip
# (:196) and _pim (:209) return 0 outside. NOT applicable to SBS.
HAD_ACC = (8.0, 18.0)

SLUG = {'SoLID 2pi': 'solid2pi', '4x24 2pibin': 'solid-phi4seg24deg', 'SBS': 'sbs'}
IS_SOLID = {'SoLID 2pi': True, '4x24 2pibin': True, 'SBS': False}


def expand(d, errcol, what):
    """One row -> PHI_N samples of theta_h at that row's fixed qT/Q.

    Returns (x, Q2, theta_h_deg, qT/Q, weight) flat arrays of length
    n_good * PHI_N, each sample carrying 1/PHI_N of its row's 1/err^2.
    """
    x, Q2, z, pT, y = (d[c].values.astype(float) for c in ('x', 'Q2', 'z', 'pT', 'y'))
    mh = np.array([MH[h] for h in d['hadron'].values])
    w = 1.0 / d[errcol].values**2

    nu = Q2 / (2.0 * M * x)
    # The SoLID files carry the beam energy; the SBS ones do not, so it has to
    # be recovered as nu/y. DO NOT use nu/y where the column exists: x, Q2 and y
    # are all bin AVERAGES there, and the average of a ratio is not the ratio of
    # the averages, so nu/y misses the SoLID beam energy by up to 0.35 GeV on 11.
    # For SBS the recovery is clean -- y was evidently built from the same
    # per-row x and Q2, and nu/y returns exactly 8.80 and 11.00 GeV -- and the
    # print says so on every run rather than leaving it assumed.
    if 'Ebeam' in d.columns:
        E = d['Ebeam'].values.astype(float)
    else:
        E = nu / y
        print(f'  {what:13s} no Ebeam column; recovered as nu/y, '
              f'{E.min():.2f} to {E.max():.2f} GeV')
    Ep = E - nu
    Eh = z * nu

    with np.errstate(invalid='ignore', divide='ignore'):
        cte = 1.0 - Q2 / (2.0 * E * Ep)
        ph = np.sqrt(Eh**2 - mh**2)
    ok = (Ep > 0) & (np.abs(cte) <= 1) & (Eh > mh) & np.isfinite(ph) & (ph >= pT)
    if not ok.all():
        print(f'  {what:13s} dropped {int((~ok).sum())} of {len(ok)} rows: '
              f'no real hadron momentum at that (Ebeam, Q2, x, z, pT)')
    x, Q2, z, pT, ph, nu, E, Ep, cte, w = (a[ok] for a in
                                           (x, Q2, z, pT, ph, nu, E, Ep, cte, w))

    qmag = np.sqrt(nu**2 + Q2)
    ctq = (E - Ep * cte) / qmag                # virtual photon polar angle
    stq = np.sqrt(np.maximum(1.0 - ctq**2, 0.0))
    pL = np.sqrt(np.maximum(ph**2 - pT**2, 0.0))

    phi = (np.arange(PHI_N) + 0.5) * 2.0 * np.pi / PHI_N
    cth = ((pT[:, None] * np.cos(phi)[None, :] * stq[:, None]
            + (pL * ctq)[:, None]) / ph[:, None])
    theta = np.degrees(np.arccos(np.clip(cth, -1.0, 1.0)))

    rep = lambda a: np.repeat(a, PHI_N)
    return (rep(x), rep(Q2), theta.ravel(), rep(pT / (z * np.sqrt(Q2))),
            rep(w / PHI_N))


def grid_hist(cols, accepted_only):
    """4D histogram over (x, Q2, theta_h, qT/Q), weighted by the FOM.

    Returns (H, fom_in_band, fom_total) with H a FOM DENSITY: divided by the
    panel cell area d(theta) d(qT/Q), so panel colours are comparable to each
    other and to plot_fom_solid_vs_sbs.py's 2D maps. The two scalars are FOM
    sums over the whole phi_h-uniform spread, not row counts -- their ratio is
    the printed in-band fraction, and it does not depend on `accepted_only`.
    """
    x, Q2, theta, qtq, w = cols
    band = (theta >= HAD_ACC[0]) & (theta <= HAD_ACC[1])
    fom_in, fom_all = w[band].sum(), w.sum()
    if accepted_only:
        x, Q2, theta, qtq, w = (a[band] for a in (x, Q2, theta, qtq, w))
    H, _ = np.histogramdd(np.column_stack([x, Q2, theta, qtq]),
                          bins=[XGRID, QGRID, TE, RE], weights=w)
    H /= np.diff(TE)[None, None, :, None] * np.diff(RE)[None, None, None, :]
    return H, fom_in, fom_all


def figure(short, label, H, vmin, vmax, accepted_only, tag):
    """The grid: one panel per occupied (x, Q2) cell, Q2 up, x right."""
    occ = H.sum(axis=(2, 3)) > 0
    xi = np.flatnonzero(occ.any(axis=1))
    qi = np.flatnonzero(occ.any(axis=0))[::-1]          # highest Q2 on top
    if not len(xi) or not len(qi):
        print(f'  {short}: no occupied cell, no figure'); return

    fig, axes = plt.subplots(len(qi), len(xi), squeeze=False, sharex=True,
                             sharey=True,
                             figsize=(1.45 * len(xi) + 2.6, 1.45 * len(qi) + 2.2))
    g1, g2 = np.meshgrid(TE, RE, indexing='ij')
    for r, jq in enumerate(qi):
        for c, jx in enumerate(xi):
            ax = axes[r][c]
            h = H[jx, jq]
            if h.sum() <= 0:                    # in the grid, but no data in it
                ax.set_facecolor('0.93')
            else:
                pc = ax.pcolormesh(g1, g2, np.ma.masked_where(h <= 0, h),
                                   norm=LogNorm(vmin=vmin, vmax=vmax),
                                   cmap='viridis', shading='flat')
                if IS_SOLID[short] and not accepted_only:
                    ax.axvspan(*HAD_ACC, facecolor='none', edgecolor='0.55',
                               lw=0.8, ls='--', zorder=3)
            ax.set_xlim(TE[0], TE[-1]); ax.set_ylim(RE[0], RE[-1])
            ax.tick_params(direction='in', top=True, right=True, labelsize=8)
            if r == 0:
                ax.set_title(f'{XGRID[jx]:.1f}–{XGRID[jx + 1]:.1f}', fontsize=9)
            if c == len(xi) - 1:
                ax.yaxis.set_label_position('right')
                ax.set_ylabel(f'{QGRID[jq]:.0f}–{QGRID[jq + 1]:.0f}',
                              rotation=270, labelpad=11, fontsize=9)

    fig.supxlabel(r'hadron lab polar angle  $\theta_h$  [deg]'
                  '\n' r'panel columns: $x$ in steps of 0.1', size=11)
    fig.supylabel(r'$q_T/Q = p_T/(z\,Q)$' '\n'
                  r'panel rows: $Q^2$ in steps of 1 GeV$^2$', size=11)
    cb = fig.colorbar(pc, ax=axes, fraction=0.030, pad=0.045)
    cb.set_label(r'FOM: $(\delta A_{UT})^{-2}/(\Delta\theta_h\,\Delta(q_T/Q))$',
                 size=10)
    sub = (r'$\phi_h$ restricted to $\theta_h\in[8^\circ,18^\circ]$'
           if accepted_only else
           r"each row's FOM spread uniformly over $\phi_h$"
           + (r';  dashed: SoLID $8^\circ\!-\!18^\circ$ hadron acceptance'
              if IS_SOLID[short] else ''))
    fig.suptitle(f'{label}\n' + r'FOM in $(\theta_h,\,q_T/Q)$ per $(x,\,Q^2)$ cell'
                 '   —   ' + sub + r';  $W>2.3$ GeV, $0.3<z<0.7$, statistical only',
                 fontsize=10.5)
    for ext in ('png', 'pdf'):
        q = _p(f'fom-qtq-vs-theta-grid-{SLUG[short]}{tag}.{ext}')
        fig.savefig(q, dpi=150 if ext == 'png' else None, bbox_inches='tight')
        print(f'wrote {q}')
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--accepted-only', action='store_true',
                    help='keep only the phi_h that put the hadron in '
                         '8-18 deg, instead of spreading over all phi_h')
    a = ap.parse_args()
    tag = '-acc' if a.accepted_only else ''

    print('FOM in (theta_h, qT/Q) per (x, Q2) cell:')
    grids = []
    for short, label, path, errcol, *_ in SETS:
        d, ec = load(path, errcol, short)
        cols = expand(d, ec, short)
        lost = (cols[2] > TE[-1]).sum() + (cols[3] > RE[-1]).sum()
        if lost:
            print(f'  {short:13s} {lost} of {len(cols[2])} phi samples fall '
                  f'outside the panel axes and are not drawn')
        H, w_in, w_all = grid_hist(cols, a.accepted_only)
        grids.append((short, label, H, w_in, w_all))

    # One colour scale for all three figures -- that is what makes them
    # comparable, and it is the whole point of drawing them the same way.
    vmax = max(H.max() for _, _, H, _, _ in grids)
    vmin = max(min(H[H > 0].min() for _, _, H, _, _ in grids), vmax / 1e6)
    print(f'\n  shared colour scale: {vmin:.3e} to {vmax:.3e}\n')

    for short, label, H, w_in, w_all in grids:
        figure(short, label, H, vmin, vmax, a.accepted_only, tag)

    # ---------------------------------------------------------------- tables
    for short, label, H, w_in, w_all in grids:
        # Undo the density division to report a plain sum 1/err^2 per cell.
        tot = (H * np.diff(TE)[None, None, :, None]
                 * np.diff(RE)[None, None, None, :]).sum(axis=(2, 3))
        occ = tot > 0
        xi = np.flatnonzero(occ.any(axis=1))
        qi = np.flatnonzero(occ.any(axis=0))[::-1]
        print(f'\n  {label}   —   sum 1/err^2 per (x, Q2) cell'
              + ('  (in-band part only)' if a.accepted_only else '')
              + f'   [{int(occ.sum())} cells occupied]')
        print('      Q2 \\ x  ' + ''.join(f'{XGRID[j]:.1f}-{XGRID[j+1]:.1f}'.rjust(11)
                                          for j in xi))
        for j in qi:
            print(f'    {QGRID[j]:4.0f}-{QGRID[j+1]:<4.0f}'
                  + ''.join((f'{tot[i, j]:11.3e}' if tot[i, j] > 0 else f'{"-":>11s}')
                            for i in xi))
        frac = w_in / w_all if w_all > 0 else float('nan')
        print(f'    total {w_all:.4e};  fraction of the phi_h-uniform spread '
              f'inside {HAD_ACC[0]:g}-{HAD_ACC[1]:g} deg: {frac:.3f}')


if __name__ == '__main__':
    main()
