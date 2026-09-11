#!/usr/bin/env python3
"""Split the SBS projection into 4x finer Q2 bins -> data_sbs/bin4xQ2/.

    ./data_sbs/split_q2.py [--nsplit 4] [--weighted] [--out DIR]

Reads data_sbs/kintables/table3D_*_projected.txt (the collaboration's source
tables) and writes sbs0{1,2}_root.dat in dump_sbs.C's exact format, so
./prepare.py <out> --sbs consumes them unchanged.

WHAT THIS IS, AND IS NOT. The tables report ONE mean Q2 per row, having already
integrated the electron angle over the full theta = 25-37 deg acceptance: within
an (x bin, energy) group the reported Q2 varies by 2.8-10.3%, while the theta box
spans Q2 by ~50%. So the Q2 sub-structure is NOT in the data. This script models
it. It cannot add statistical reach -- see the conservation note below -- it can
only resolve y inside a bin.

WHY THE SPLIT IS EQUAL BY DEFAULT. The fraction of a cell's accepted events in
each theta sub-range is not measurable from these tables:

  - within a cell, theta is integrated out (above);
  - the two beam energies would isolate the Q2 dependence at fixed (x, z, pT)
    WITH acceptance included -- but they use staggered z bins (11 GeV at
    0.2/0.3/0.4/0.5/0.6, 8.8 GeV at 0.25/0.35/0.45/0.55/0.65), so there are ZERO
    matched cells;
  - the cross-energy N_acc slope per x bin runs the wrong way (N RISES with Q2,
    p = 0.0 to +4.5 low to high x, against the 1/Q^4 cross-section falloff),
    because changing beam energy at fixed x also changes y, W and the phase
    space, and the z/pT coverage differs. It is not a Q2 dependence.
  - there is no SBS acceptance in this repo; Acceptance/ holds SoLID maps only.

Since sum_i 1/delta_i^2 = (1/delta^2) sum_i f_i = 1/delta^2 for ANY split, the
choice of f_i cannot add or remove statistical weight -- it only redistributes it
across y. So the default takes the assumption that adds nothing, f_i = 1/4, and
the error follows from the MEASURED delta alone:

    delta_i = delta / sqrt(1/4) = 2 * delta

--weighted instead weights by the unpolarised rate dsigma/dQ2 ~ (1/x Q^4)
(1 - y + y^2/2) F_UU,T, giving f ~ 0.38/0.27/0.20/0.15. That imposes a
cross-section shape carrying NO acceptance, which is why it is not the default;
run it as a systematic check on whether the answer depends on an unmeasurable
assumption.
"""
import argparse, os, re, sys, glob
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
M = 0.938272
THETA = (25.0, 37.0)          # deg, the SBS electron-arm acceptance
PMIN = 1.0                    # GeV, minimum scattered-electron momentum
COLS = ['xmin','xmax','zmin','zmax','ptmin','ptmax','x','Q2','z','pT',
        'col','dcol','siv','dsiv']
# (file tag, beam energy, hadron, which output file)
SETS = [('piplus11',  11.0, 'pi+', 'sbs01'), ('piplus88',  8.8, 'pi+', 'sbs01'),
        ('piminus11', 11.0, 'pi-', 'sbs02'), ('piminus88', 8.8, 'pi-', 'sbs02')]


def q2_of_theta(E, x, theta_deg):
    """Q2 for beam energy E, Bjorken x, electron lab angle theta. Nucleon at rest.

    Eliminate E' between Q2 = 4 E E' sin^2(theta/2) and x = Q2/(2 M (E - E'))."""
    s = np.sin(np.radians(theta_deg) / 2.0)**2
    return 4.0 * E**2 * s * M * x / (M * x + 2.0 * E * s)


def read3d(path):
    rows = []
    for line in open(path).read().split('\n')[1:]:
        if not line.strip():
            continue
        nums = re.findall(r'-?\d+\.?\d*e?[-+]?\d*',
                          line.replace('[', ' ').replace(']', ' '))
        rows.append([float(v) for v in nums])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--nsplit', type=int, default=4)
    ap.add_argument('--weighted', action='store_true',
                    help='weight sub-bins by the unpolarised rate instead of equally')
    ap.add_argument('--out', default=os.path.join(HERE, 'bin4xQ2'))
    a = ap.parse_args()
    if a.nsplit < 1:
        sys.exit('error: --nsplit must be >= 1')
    os.makedirs(a.out, exist_ok=True)

    if a.weighted:
        sys.path.insert(0, os.path.dirname(HERE))
        import tmd

    edges = np.linspace(THETA[0], THETA[1], a.nsplit + 1)
    out = {'sbs01': [], 'sbs02': []}
    # per-parent bookkeeping for the conservation check
    check = []

    for tag, E, had, which in SETS:
        src = os.path.join(HERE, 'kintables', f'table3D_{tag}_projected.txt')
        if not os.path.exists(src):
            sys.exit(f'error: missing {src}')
        for r in read3d(src):
            d = dict(zip(COLS, r))
            # The Collins error is what the _root pair has always carried for BOTH
            # amplitudes (data_sbs/README.md); keep that, so the split is the only
            # thing that changes relative to sbs0{1,2}_root.dat.
            err = d['dcol']
            sub = []
            for lo, hi in zip(edges[:-1], edges[1:]):
                qlo, qhi = q2_of_theta(E, d['x'], lo), q2_of_theta(E, d['x'], hi)
                q2 = 0.5 * (qlo + qhi)
                y = q2 / (2.0 * M * E * d['x'])
                sub.append({'Q2': q2, 'y': y, 'qlo': qlo, 'qhi': qhi})
            if a.weighted:
                w = []
                for s in sub:
                    yy = s['y']
                    w.append(0.0 if not 0 < yy < 1 else
                             (1.0 / (d['x'] * s['Q2']**2)) * (1 - yy + 0.5 * yy * yy)
                             * tmd.FUUT(d['x'], s['Q2'], d['z'], d['pT'], 'neutron', had))
                w = np.array(w)
                f = w / w.sum() if w.sum() > 0 else np.full(len(sub), 1.0 / len(sub))
            else:
                f = np.full(len(sub), 1.0 / len(sub))
            inv = 0.0
            for s, fi in zip(sub, f):
                if fi <= 0:
                    continue
                ei = err / np.sqrt(fi)
                inv += 1.0 / ei**2
                out[which].append((s['Q2'], d['x'], s['y'], d['z'], d['pT'], had, ei))
            check.append((inv, 1.0 / err**2))

    for which in ('sbs01', 'sbs02'):
        path = os.path.join(a.out, f'{which}_root.dat')
        with open(path, 'w') as fh:
            fh.write('Q2\tx\ty\tz\tpT\tobs\ttarget\thadron\tvalue\terror\n')
            for q2, x, y, z, pt, had, e in out[which]:
                fh.write(f'{q2:.10g}\t{x:.10g}\t{y:.10g}\t{z:.10g}\t{pt:.10g}\t'
                         f'AUTsivers\tneutron\t{had}\t0\t{e:.10g}\n')
        print(f'  wrote {path}  {len(out[which])} rows')

    got = np.array([c[0] for c in check]); want = np.array([c[1] for c in check])
    rel = np.abs(got - want) / want
    print(f'  statistical information conserved: max relative deviation of '
          f'sum(1/delta_i^2) from 1/delta_parent^2 = {rel.max():.2e}  '
          f'over {len(check)} parent bins')
    if rel.max() > 1e-12:
        sys.exit('error: the split changed the total statistical weight')


if __name__ == '__main__':
    main()
