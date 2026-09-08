#!/usr/bin/env python3
"""Build a bin file in bin_*.dat format from a count table (count_*.dat).

    ./make_bins_from_count.py <count_file> [-o OUT] [-N TARGET] [--drop-below F]

Reads the fine (x, Q2, z, pT) grid of N_acc that `./analysis_neutron 4 <rundir>`
writes, and merges those cells into a set of 4D boxes each holding roughly
TARGET of N_acc (default 1e6). The output is the 8-column format
`AnalyzeEstatUT3` reads:

    Q2l  Q2u  zl  zu  Ptl  Ptu  xl  xu

one header line, then whitespace-separated numbers -- the reader skips the first
line and parses with `>>`, so column widths do not matter but the ORDER does.

IT NEVER OVERWRITES bin_enhanced_*.dat. The default output name is derived from
the input (count_N11p.dat -> bin_count_N11p.dat), and the program refuses to
write a path whose basename starts with "bin_enhanced".

HOW THE BOXES ARE CHOSEN. A k-d decomposition, not the nested fixed lists that
GenerateBinInfoFile uses. Start from the whole occupied grid; while a box holds
more than 1.5 x TARGET, split it in two along one axis at the point that most
evenly divides N_acc, and recurse. Leaves are the output bins.

Why this rather than copying GenerateBinInfoFile's Q2->z->Pt->x nesting: that
scheme fixes the Q2 and z edges up front, so wherever the yield is concentrated
it can only adapt in Pt and x, and it drops whole (Q2, z, Pt) slabs that miss a
stats threshold -- exactly the "missing cells with good N_acc" this is meant to
avoid. The k-d split adapts on every axis and, being a recursive bisection of
one covering box, PARTITIONS the occupied grid: every populated cell lands in
exactly one output bin, which the program verifies before writing by summing the
leaves back to the table total.

CHOOSING THE SPLIT AXIS. The axis the box spans the most cells on, so boxes stay
compact rather than degenerating into slabs one cell thick. Ties break toward
the axis with the larger N_acc imbalance to fix, since that is the split that
buys the most.

WHY THE DEFAULT IS 1e6. The target sets how many bins come out, and the bins
are what AnalyzeEstatUT3 then loops over -- so it is really a choice about the
cost of the NEXT step, not about this program. Against the 1660-bin production
set whose step 2 takes ~1h33m:

    target    bins, all 4 files    step-2 estimate
    1e5             ~223,000       ~208 h
    1e6              ~22,300        ~21 h
    1e7               ~2,230         ~2 h

and the estimate is a floor: AnalyzeEstatUT3 breaks early at Nrec > 100000 on
today's fat bins but would run its full 1e7 events on every thin one.

WHAT COMES OUT IS NOT UNIFORM. Leaves land mostly in [0.75, 1.5] x TARGET, but
two kinds fall below: a box whose cells are all in one grid cell cannot be split
at all, and a box can hold less than the target once its neighbours are carved
away. Both are reported, and --drop-below discards them if you would rather have
fewer, cleaner bins -- at the cost of the yield they carry, which is printed so
the trade is explicit.
"""
import os, sys, argparse
import numpy as np
import pandas as pd


def read_count(path):
    """Parse a count_*.dat into (Nacc grid, origins, widths, index offsets).

    Grid geometry comes from the file's own '#widths'/'#origins' header lines
    rather than being hardcoded, so a table written with different binning still
    reads correctly here.
    """
    widths, origins = {}, {}
    with open(path) as f:
        for line in f:
            if not line.startswith('#'):
                break
            t = line[1:].split()
            if t and t[0] == 'widths':
                for k, v in zip(t[1::2], t[2::2]):
                    widths[k] = float(v)
            elif t and t[0] == 'origins':
                for k, v in zip(t[1::2], t[2::2]):
                    origins[k] = float(v)
    need_w = ('dx', 'dQ2', 'dz', 'dPt')
    need_o = ('x', 'Q2', 'z', 'Pt')
    if not all(k in widths for k in need_w) or not all(k in origins for k in need_o):
        sys.exit(f'error: {path} has no #widths/#origins header; not a count table?')
    w = np.array([widths[k] for k in need_w])
    o = np.array([origins[k] for k in need_o])

    # comment='#' strips the header block, and the first line after it is the
    # column-name row -- pandas takes it as the header, so columns are addressed
    # BY NAME. Positional indices would silently shift the day a column is added
    # or removed, which has already happened once (the phi columns).
    df = pd.read_csv(path, sep='\t', comment='#')
    need = ['xlo', 'Q2lo', 'zlo', 'pTlo', 'Nacc', 'Nmc']
    missing = [c for c in need if c not in df.columns]
    if missing:
        sys.exit(f'error: {path} is missing column(s) {missing}; found {list(df.columns)}')
    lo = df[['xlo', 'Q2lo', 'zlo', 'pTlo']].to_numpy(float)
    nacc = df['Nacc'].to_numpy(float)
    nmc = df['Nmc'].to_numpy(float)
    # Low edges -> integer indices. round(), not floor(): the edges were written
    # as origin + k*width in %e, so they carry float noise that floor() would
    # occasionally push a cell one bin down.
    idx = np.rint((lo - o) / w).astype(np.int64)
    return idx, nacc, nmc, o, w


def build_grid(idx, nacc, nmc):
    """Dense 4D arrays over the occupied index range, plus the index offset."""
    base = idx.min(axis=0)
    shape = tuple((idx.max(axis=0) - base + 1).tolist())
    ncell = int(np.prod(shape, dtype=np.int64))
    if ncell > 400_000_000:
        sys.exit(f'error: occupied index range is {shape} = {ncell} cells; refusing to allocate')
    g = np.zeros(shape)
    m = np.zeros(shape)
    k = tuple((idx - base).T)
    np.add.at(g, k, nacc)
    np.add.at(m, k, nmc)
    return g, m, base


def split_boxes(g, target):
    """k-d bisection of the grid into boxes each holding roughly `target`.

    Iterative with an explicit stack -- a recursive version blows Python's
    recursion limit on the deep, narrow trees a 12.6e6-cell grid produces.
    """
    full = tuple((0, s) for s in g.shape)
    stack, leaves, unsplittable = [full], [], 0
    limit = 1.5 * target
    while stack:
        box = stack.pop()
        sl = tuple(slice(a, b) for a, b in box)
        sub = g[sl]
        # Recomputed from the grid every time, NOT carried down as (parent - sibling):
        # that subtraction compounds rounding over ~17 levels and produced boxes
        # with totals like -2e-07, which then slipped past a ">= 0" filter.
        tot = float(sub.sum())
        if tot <= 0.0:
            continue                       # empty box: no yield to measure, drop it
        widths = [b - a for a, b in box]
        if all(wd <= 1 for wd in widths):
            leaves.append((box, tot))
            if tot > limit:
                unsplittable += 1          # one grid cell holding more than the target
            continue
        if tot <= limit:
            leaves.append((box, tot))
            continue
        best = None
        for ax in range(4):
            if widths[ax] <= 1:
                continue
            # Cumulative yield along this axis; the cut goes where it first
            # passes half, which is the most even division available.
            prof = sub.sum(axis=tuple(a for a in range(4) if a != ax))
            c = np.cumsum(prof)
            j = int(np.searchsorted(c, 0.5 * tot)) + 1
            j = min(max(j, 1), widths[ax] - 1)          # keep both sides non-empty
            imbalance = abs(2.0 * c[j - 1] - tot)
            key = (widths[ax], -imbalance)
            if best is None or key > best[0]:
                best = (key, ax, j)
        if best is None:
            leaves.append((box, tot))
            continue
        _, ax, j = best
        lo, hi = box[ax]
        a = list(box); a[ax] = (lo, lo + j)
        b = list(box); b[ax] = (lo + j, hi)
        stack.append(tuple(a))
        stack.append(tuple(b))
    if unsplittable:
        print(f'  note: {unsplittable} bins exceed 1.5x target because a single '
              f'count-table cell already does -- the grid resolution is the floor')
    return leaves


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('count_file')
    ap.add_argument('-o', '--out', default=None,
                    help='output path (default: count_X.dat -> bin_count_X.dat beside it)')
    ap.add_argument('-N', '--target', type=float, default=1.0e6,
                    help='target N_acc per output bin (default 1e6)')
    ap.add_argument('--drop-below', type=float, default=0.0, metavar='F',
                    help='discard bins holding less than F*target (default 0 = keep all)')
    a = ap.parse_args()

    out = a.out
    if out is None:
        d, b = os.path.split(a.count_file)
        out = os.path.join(d, 'bin_' + b)   # count_N11p.dat -> bin_count_N11p.dat
    if os.path.basename(out).startswith('bin_enhanced'):
        sys.exit(f'error: refusing to write {out} -- that is a generated bin file, '
                 'pick another name with -o')

    idx, nacc, nmc, origin, width = read_count(a.count_file)
    total = nacc.sum()
    print(f'  {a.count_file}: {len(nacc)} cells, total Nacc {total:.4e}')
    print(f'  grid origins {origin}  widths {width}')

    g, mgrid, base = build_grid(idx, nacc, nmc)
    print(f'  occupied index box {g.shape} = {int(np.prod(g.shape, dtype=np.int64))} cells')

    leaves = split_boxes(g, a.target)
    tots = np.array([t for _, t in leaves])
    # Partition check: every populated cell must land in exactly one leaf.
    if not np.isclose(tots.sum(), total, rtol=1e-9):
        sys.exit(f'error: leaves sum to {tots.sum():.6e} but the table totals '
                 f'{total:.6e} -- the split lost or double-counted cells')
    print(f'  {len(leaves)} bins; leaf Nacc sums to {tots.sum():.4e} = table total (partition verified)')

    keep = tots >= a.drop_below * a.target
    if not keep.all():
        lost = tots[~keep].sum()
        print(f'  --drop-below {a.drop_below}: discarding {int((~keep).sum())} bins '
              f'carrying {lost:.3e} ({100*lost/total:.3f}% of Nacc)')

    rows = []
    for (box, tot), k in zip(leaves, keep):
        if not k:
            continue
        e = [(origin[i] + (base[i] + box[i][0]) * width[i],
              origin[i] + (base[i] + box[i][1]) * width[i]) for i in range(4)]
        # e is ordered (x, Q2, z, Pt); the file wants Q2, z, Pt, x.
        sl = tuple(slice(lo_, hi_) for lo_, hi_ in box)
        rows.append((e[1][0], e[1][1], e[2][0], e[2][1], e[3][0], e[3][1],
                     e[0][0], e[0][1], tot, float(mgrid[sl].sum())))
    rows.sort()

    with open(out, 'w') as f:
        f.write('Q2l\t Q2u\t zl\t zu\t Ptl\t Ptu\t xl\t xu\n')
        for r in rows:
            # More decimals than GenerateBinInfoFile's %.1f: at dQ2 = 0.05 that
            # format collapses 1.05 and 1.15 onto "1.1". The reader parses with
            # >> so the extra digits are free.
            f.write(f'{r[0]:.3f}\t {r[1]:.3f}\t {r[2]:.3f}\t {r[3]:.3f}\t '
                    f'{r[4]:.3f}\t {r[5]:.3f}\t {r[6]:.4f}\t {r[7]:.4f}\n')

    kept = np.array([r[8] for r in rows])
    kmc  = np.array([r[9] for r in rows])
    q = np.percentile(kept, [10, 50, 90])
    qm = np.percentile(kmc, [10, 50, 90])
    print(f'  wrote {out}: {len(rows)} bins')
    print(f'  Nacc per bin: min {kept.min():.3e}  p10 {q[0]:.3e}  median {q[1]:.3e}  '
          f'p90 {q[2]:.3e}  max {kept.max():.3e}')
    print(f'  within [0.75,1.5]x target: {100*np.mean((kept>=0.75*a.target)&(kept<=1.5*a.target)):.1f}%')
    print(f'  MC events behind each bin: min {kmc.min():.0f}  p10 {qm[0]:.0f}  '
          f'median {qm[1]:.0f}  p90 {qm[2]:.0f}   ({100*np.mean(kmc>=100):.1f}% have >=100)')


if __name__ == '__main__':
    main()
