#!/usr/bin/env python3
"""SoLID full-2pi and SBS in (x, Q2), every row as a point. No binning, no cuts.

    source /usr/share/Modules/init/zsh && source ../setup.sh
    ./plot_native_points.py

Writes two figures. Both read the same rows; neither cuts anything.

  fom-native-xQ2            both experiments as points on one set of axes
  fom-solidbin-sbspoint-xQ2 SoLID re-binned into a map, SBS as plain points

Both experiments on ONE set of axes, sharing a colour scale:

    SoLID E12-10-006  ../phicompare/data_phifull/simenhanced3he.dat
                      1660 rows, FOM from error_stat_collins, small dots
    SBS E12-09-018    ../data_sbs/sbs0{1,2}_root.dat
                      455 rows (233 pi+ / 222 pi-), FOM from its own `error`
                      column, larger markers with a crimson edge

The fill colour is the FOM on both, so it cannot also say which experiment a
point belongs to -- that is what the crimson edge and the marker size are for.

NOTHING IS RE-BINNED AND NOTHING IS CUT. Every row of every file is drawn. This
is deliberately the opposite of fom-solid-vs-sbs-2d, which re-bins both onto a
uniform 0.05 x 0.75 grid, divides by cell area to make a density, and applies
the study's W > 2.3 GeV and 0.3 < z < 0.7 selection. That figure compares the
two on common edges; this one shows each as it actually is.

The colour is a per-row FOM, 1/(dA_UT)^2, not a density -- neither file carries
bin edges, so there is nothing to divide by. Values are not comparable with
fom-solid-vs-sbs-2d's.

WHAT THE OVERLAY SHOWS THAT THE RE-BINNED MAP CANNOT.

SBS's rows are not scattered: they fall into 13 well-separated (x, Q2) groups of
4-47 rows, and within a group every row has a different z and pT. It is binned
in (x, Q2) 13 ways, each cell subdivided in (z, pT), and the x and Q2 a row
reports are that sub-bin's MEAN kinematics -- drifting up to 0.05 in x and 0.48
in Q2 across the cell. Each streak is one cell smeared by that drift, which is
why 449 distinct x values among 455 rows looks structureless in a list.

SoLID's 1660 rows fill the plane instead: adaptive binning built per (Q2, z, pT)
slice, so there is no repeated (x, Q2) grid to see.

The uniform 0.05 x 0.75 edges of fom-solid-vs-sbs-2d cut across SBS's 13 cells
and smear them into neighbours, so neither structure survives there.

The W = 2.3 GeV curve is drawn for reference and is NOT applied. 20 SBS rows sit
below it (two entire (x, Q2) groups near x ~ 0.63); the study drops 64 in total
because it also cuts 0.3 < z < 0.7, which is invisible on these axes.
"""
import os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fom_common import _p, M, SBS_FILES, SETS, XE2, QE2

# ---------------------------------------------------------------- SBS bin boxes
# The SBS (x, Q2) cells, drawn as empty boxes on fom-solidbin-sbspoint-xQ2.
#
# x: the collaboration's own binning, width 0.1 with edges on 0.1, 0.2, ... 0.7 --
#    read straight off the [xmin][xmax] columns of data_sbs/kintables/table3D_*.
#
# Q2: NOT a free binning. It follows from the spectrometer acceptance. For an
#    electron of beam energy E scattering off a nucleon at rest and detected at
#    lab angle theta,
#
#        Q2 = 4 E^2 s M x / (M x + 2 E s),      s = sin^2(theta/2)
#
#    (eliminate E' between Q2 = 4 E E' sin^2(theta/2) and x = Q2/(2 M (E - E'))).
#    Q2 rises with both theta and x, so over one x bin the acceptance region runs
#    from (theta_min, xmin) to (theta_max, xmax) -- that envelope is the box, not
#    the value at the bin centre. Using the centre understates the lowest x bin
#    badly: it gives 2.72-2.91 where the data sit at 3.11-3.32.
#
#    A SECOND ACCEPTANCE CUT trims the top edge: the scattered electron must carry
#    more than PMIN = 1 GeV. Since E' = E - Q2/(2 M x), that is
#
#        Q2 < 2 M x (E - PMIN)
#
#    a straight line through the origin in (x, Q2), and the box's upper edge is
#    whichever of the two limits is lower. It binds ONLY in the lowest x bin, and
#    only just: [0.1,0.2] goes 3.806 -> 3.753 at 11 GeV and 2.986 -> 2.927 at
#    8.8 GeV. Everywhere else theta = 37 deg is the tighter constraint. Small, but
#    it is the difference between drawing the acceptance and drawing an angle.
#
# SBS ran at two beam energies and every x bin is populated at both, so each x bin
# gets TWO boxes; the lower-Q2 one is 8.8 GeV and the upper 11 GeV. That is what
# "which beam energy" means here -- it is read off the Q2 of the cell.
#
# Checked against data_sbs/kintables: all 12 boxes contain every row of their own
# (x bin, energy) group, 1074 rows in total.
THETA = (25.0, 37.0)          # deg, the SBS electron-arm acceptance
PMIN = 1.0                    # GeV, minimum scattered-electron momentum
BEAMS = ((11.0, '-'), (8.8, '--'))
XBINS = [(round(0.1 * i, 1), round(0.1 * i + 0.1, 1)) for i in range(1, 7)]


def sbs_q2(E, x, theta_deg):
    """Q2 for beam energy E, Bjorken x, electron lab angle theta. Nucleon at rest."""
    s = np.sin(np.radians(theta_deg) / 2.0)**2
    return 4.0 * E**2 * s * M * x / (M * x + 2.0 * E * s)


def sbs_q2_pmin(E, x, pmin=PMIN):
    """Largest Q2 leaving the scattered electron above pmin: E' = E - Q2/(2 M x)."""
    return 2.0 * M * x * (E - pmin)


def sbs_boxes():
    """(xlo, xhi, Q2lo, Q2hi, E, linestyle) for every SBS cell.

    Both edges rise with x, so the corner-to-corner envelope over the x bin is
    (theta_min, xlo) to (theta_max, xhi) -- with the top edge additionally capped
    by the E' > PMIN limit, which is also rising in x and so also evaluated at xhi.
    """
    return [(xlo, xhi,
             sbs_q2(E, xlo, THETA[0]),
             min(sbs_q2(E, xhi, THETA[1]), sbs_q2_pmin(E, xhi)),
             E, ls)
            for xlo, xhi in XBINS for E, ls in BEAMS]


OUT = _p('fom-native-xQ2')
OUT2 = _p('fom-solidbin-sbspoint-xQ2')
SOLID_FILE = next(s[2] for s in SETS if s[0] == 'SoLID 2pi')   # path, not hardcoded
SOLID_ERR = next(s[3] for s in SETS if s[0] == 'SoLID 2pi')


def read(paths, errcol, what):
    paths = [paths] if isinstance(paths, str) else list(paths)
    missing = [q for q in paths if not os.path.exists(q)]
    if missing:
        hint = ("\n       rebuild with: cd .. && root -l -b -q dump_sbs.C"
                if any('_root.dat' in q for q in missing)
                else "\n       run ./prepare.py on that rundir first")
        sys.exit(f"error: missing {missing}  (input for '{what}'){hint}")
    d = pd.concat([pd.read_csv(q, sep=r'\s+') for q in paths], ignore_index=True)
    d['fom'] = 1.0 / d[errcol]**2
    d['W'] = np.sqrt(M**2 + d['Q2'] * (1.0 / d['x'] - 1.0))    # reference curve only
    print(f"  {what:14s} {len(d):5d} rows   x {d['x'].min():.4f}-{d['x'].max():.4f}"
          f"   Q2 {d['Q2'].min():.4f}-{d['Q2'].max():.4f}"
          f"   FOM/row median {d['fom'].median():.3e}   sum {d['fom'].sum():.4e}")
    return d


def main():
    solid = read(SOLID_FILE, SOLID_ERR, 'SoLID 2pi')
    sbs = read(SBS_FILES, 'error', 'SBS')
    print(f"  SoLID/SBS median FOM per row: {solid['fom'].median()/sbs['fom'].median():.1f}x")
    print(f"  (reference only: {int((sbs['W'] <= 2.3).sum())} SBS and "
          f"{int((solid['W'] <= 2.3).sum())} SoLID rows lie below W = 2.3; none removed)")

    # One colour scale for both -- on a single axes it is the only way the FOM
    # of the two experiments can be read against each other.
    lo = min(solid['fom'].min(), sbs['fom'].min())
    hi = max(solid['fom'].max(), sbs['fom'].max())
    norm = LogNorm(vmin=max(lo, hi / 1e7), vmax=hi)

    fig, ax = plt.subplots(figsize=(8.6, 6.6))
    xx = np.linspace(0.02, 0.72, 400)
    ax.plot(xx, (2.3**2 - M**2) * xx / (1 - xx), color='0.5', ls='--', lw=1.1, zorder=1)
    ax.text(0.985, 0.03, r'$W = 2.3$ GeV  (reference, not applied)',
            transform=ax.transAxes, ha='right', va='bottom', fontsize=8.5, color='0.4')

    # SoLID goes down first and small: 1660 points fill the plane, and drawn at
    # SBS's size they would bury it. SBS goes on top, larger, with a hard crimson
    # edge -- the edge is what identifies the experiment, since the FILL on both
    # is the shared FOM colour and cannot also encode which is which.
    sc = ax.scatter(solid['x'], solid['Q2'], c=solid['fom'], norm=norm, cmap='viridis',
                    marker='o', s=11, linewidths=0.0, alpha=0.85, zorder=2)
    for had, marker in (('pi+', 'o'), ('pi-', '^')):
        m = sbs['hadron'] == had
        ax.scatter(sbs.loc[m, 'x'], sbs.loc[m, 'Q2'], c=sbs.loc[m, 'fom'], norm=norm,
                   cmap='viridis', marker=marker, s=46, edgecolors='crimson',
                   linewidths=0.9, zorder=4)

    handles = [plt.Line2D([], [], ls='none', marker='o', ms=5, mfc='0.55', mec='none',
                          label=f"SoLID E12-10-006   {len(solid)} rows"),
               plt.Line2D([], [], ls='none', marker='o', ms=8, mfc='0.55',
                          mec='crimson', mew=1.1,
                          label=f"SBS E12-09-018 $\pi^+$   {int((sbs['hadron']=='pi+').sum())} rows"),
               plt.Line2D([], [], ls='none', marker='^', ms=8, mfc='0.55',
                          mec='crimson', mew=1.1,
                          label=f"SBS E12-09-018 $\pi^-$   {int((sbs['hadron']=='pi-').sum())} rows")]
    ax.legend(handles=handles, loc='upper left', frameon=True, fontsize=9)

    cb = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.02)
    cb.set_label(r'FOM per row:  $(\delta A_{UT})^{-2}$   (shared by both)', size=11)
    ax.set_xlim(0.02, 0.72); ax.set_ylim(0.6, 10.4)
    ax.set_xlabel(r'$x$', size=13)
    ax.set_ylabel(r'$Q^2$  (GeV$^2$)', size=13)
    ax.tick_params(direction='in', top=True, right=True, labelsize=11)
    ax.set_title('Native binning — every row of both experiments, nothing re-binned, '
                 'nothing cut', fontsize=11.5)
    fig.text(0.5, 0.005,
             r'fill colour is FOM for both; the crimson edge marks SBS.  SoLID: adaptive '
             r'bins filling the plane.  SBS: 13 $(x,Q^2)$ cells, each streak one cell '
             r'spread by its $(z,p_T)$ subdivision.',
             ha='center', va='bottom', fontsize=8.5, color='0.35')
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    for ext in ('png', 'pdf'):
        q = f'{OUT}.{ext}'
        fig.savefig(q, dpi=150 if ext == 'png' else None)
        print(f'  wrote {q}')

    fig_solidbin_sbspoint(solid, sbs)


def fig_solidbin_sbspoint(solid, sbs):
    """SoLID re-binned into a map, SBS as plain points on top.

    SoLID goes onto fom_common's XE2 x QE2 grid -- 0.05 in x, 0.75 in Q2, the
    same edges fom-solid-vs-sbs-2d uses, so the two figures are directly
    relatable -- and is shown as a FOM DENSITY, sum(1/dA^2) over the cell divided
    by its area. That is a legitimate density here because the grid cells do not
    overlap, unlike SoLID's own 4D bins whose (x, Q2) shadows do.

    SBS carries NO FOM: it is drawn only to show where its 455 rows sit against
    SoLID's landscape. It is not re-binned -- it has no edges to re-bin with, and
    its positions are the point of putting it here.
    """
    H, _, _ = np.histogram2d(solid['x'], solid['Q2'], bins=[XE2, QE2],
                             weights=solid['fom'])
    H = H / np.outer(np.diff(XE2), np.diff(QE2))
    H = np.ma.masked_where(H <= 0, H)
    print(f"  SoLID re-binned onto {len(XE2)-1} x {len(QE2)-1} cells "
          f"({int(H.count())} populated)")

    fig, ax = plt.subplots(figsize=(8.8, 6.6))
    g1, g2 = np.meshgrid(XE2, QE2, indexing='ij')
    pc = ax.pcolormesh(g1, g2, H, norm=LogNorm(vmin=H.min(), vmax=H.max()),
                       cmap='viridis', shading='flat', zorder=1)

    xx = np.linspace(0.02, 0.72, 400)
    ax.plot(xx, (2.3**2 - M**2) * xx / (1 - xx), color='0.85', ls='--', lw=1.3, zorder=3)

    # The SBS cells themselves: empty boxes, so the density underneath stays
    # readable through them. Solid edge = 11 GeV, dashed = 8.8 GeV.
    for xlo, xhi, q2lo, q2hi, E, ls in sbs_boxes():
        ax.add_patch(Rectangle((xlo, q2lo), xhi - xlo, q2hi - q2lo,
                               facecolor='none', edgecolor='crimson', linestyle=ls,
                               linewidth=1.0, alpha=0.85, zorder=3.5))

    for had, marker, lab in (('pi+', 'o', r'$\pi^+$'), ('pi-', '^', r'$\pi^-$')):
        m = sbs['hadron'] == had
        ax.scatter(sbs.loc[m, 'x'], sbs.loc[m, 'Q2'], s=17, marker=marker,
                   color='crimson', edgecolors='none', zorder=4,
                   label=f'SBS {lab}   {int(m.sum())} rows')
    handles = ax.get_legend_handles_labels()[0] + [
        plt.Line2D([], [], color='crimson', ls=ls, lw=1.0,
                   label=f'SBS bin, {E:g} GeV  ' + r'($\theta_e$ ' + f'{THETA[0]:g}'
                         + r'$-$' + f'{THETA[1]:g}' + r'$^\circ$, $p_e>$' + f'{PMIN:g} GeV)')
        for E, ls in BEAMS]
    ax.legend(handles=handles, loc='upper left', frameon=True, fontsize=8)

    cb = fig.colorbar(pc, ax=ax, fraction=0.046, pad=0.02)
    cb.set_label(r'SoLID FOM density:  $\sum(\delta A_{UT})^{-2}/(\Delta x\,\Delta Q^2)$',
                 size=10.5)
    ax.set_xlim(0.02, 0.75); ax.set_ylim(0.6, 11.6)   # the 11 GeV top box reaches 11.1
    ax.set_xlabel(r'$x$', size=13); ax.set_ylabel(r'$Q^2$  (GeV$^2$)', size=13)
    ax.tick_params(direction='in', top=True, right=True, labelsize=11)
    ax.set_title('SoLID re-binned, SBS as points — nothing cut', fontsize=11.5)
    fig.text(0.5, 0.005,
             'SoLID on the 0.05 x 0.75 grid as a density; SBS rows at their own '
             'positions, no FOM shown.  Boxes are the SBS cells: $x$ in 0.1 steps, '
             '$Q^2$ from the\n'
             r'$\theta_e = 25-37^\circ$ and $p_e > 1$ GeV acceptance at each beam energy.  '
             '$W=2.3$ GeV drawn for reference, not applied.',
             ha='center', va='bottom', fontsize=8.5, color='0.35')
    fig.tight_layout(rect=[0, 0.055, 1, 1])
    for ext in ('png', 'pdf'):
        q = f'{OUT2}.{ext}'
        fig.savefig(q, dpi=150 if ext == 'png' else None)
        print(f'  wrote {q}')


if __name__ == '__main__':
    main()
