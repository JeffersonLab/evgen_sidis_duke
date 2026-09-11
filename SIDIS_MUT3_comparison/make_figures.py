#!/usr/bin/env python3
"""Regenerate every figure in SIDIS_MUT3_comparison/.

    source /usr/share/Modules/init/zsh && source ../setup.sh   # ROOT + LHAPDF
    ./make_figures.py                    # all figures whose run dirs are present
    ./make_figures.py --list             # show which figures can be built
    ./make_figures.py binwidth           # just one, by name

Each figure reads the per-bin Estat branches through dump_estat.C, cached as
text under --cache so a re-plot does not re-open the trees.  The run directories
themselves are NOT in the repository (6.7 GB); a figure whose inputs are missing
is reported and skipped rather than failing the run.  See
SIDIS_MUT3_comparison_base.md and _other.md for what each one shows.
"""
import argparse, os, subprocess, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

HERE = os.path.dirname(os.path.abspath(__file__))

BLUE, ORANGE, AQUA, PURPLE = "#2a78d6", "#eb6834", "#1baf7a", "#8a5cd1"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#b8b7b2"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.titlecolor": INK,
                     "figure.facecolor": "white", "axes.facecolor": "white"})
GRP = ["N11p", "N11m", "N8p", "N8m"]
AMP = ["Sivers", "Collins", "Pretzelosity"]

# ---------------------------------------------------------------- data access

def dump(run, cache):
    """Run dump_estat.C on <run> unless its text dump is already cached."""
    txt = os.path.join(cache, run + ".txt")
    if os.path.exists(txt):
        return txt
    rundir = os.path.join(HERE, run)
    if not os.path.isdir(rundir):
        return None
    os.makedirs(cache, exist_ok=True)
    macro = os.path.join(HERE, "dump_estat.C")
    r = subprocess.run(["root", "-l", "-b", "-q", f'{macro}("{rundir}","{txt}")'],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(txt):
        print(f"  dump_estat failed for {run}:\n{r.stdout}{r.stderr}", file=sys.stderr)
        return None
    return txt


def load(run, cache):
    """-> dict of per-amplitude arrays, or None if the run directory is absent.

    X is a global bin index: the four group trees concatenated in GRP order,
    which is the horizontal axis of every figure here."""
    txt = dump(run, cache)
    if txt is None:
        return None
    d = np.loadtxt(txt)
    grp, idx, i = d[:, 0].astype(int), d[:, 1].astype(int), d[:, 2].astype(int)
    counts = [(grp == k).sum() // 3 for k in range(4)]
    off = np.cumsum([0] + counts)
    return dict(X=off[grp] + idx, i=i, raw=d[:, 3], diag=d[:, 4], prop=d[:, 5],
                Nacc=d[:, 6], fn=d[:, 7], off=off)


def have(runs, cache):
    return all(os.path.isdir(os.path.join(HERE, r)) or
               os.path.exists(os.path.join(cache, r + ".txt")) for r in runs)

# ------------------------------------------------------------- shared drawing

def group_labels(ax, off):
    for g in range(4):
        ax.text((off[g] + off[g + 1]) / 2, 0.97, GRP[g], transform=ax.get_xaxis_transform(),
                ha="center", va="top", fontsize=8, color=INK2)


def frame(ax, off):
    ax.set_xlim(0, off[-1])
    ax.grid(color=MUTED, lw=0.4, alpha=0.5)
    ax.set_axisbelow(True)
    for b in off[1:-1]:
        ax.axvline(b, color=MUTED, lw=1.0, ls=":")


def save(fig, name, out):
    fig.savefig(os.path.join(out, name + ".png"), dpi=140)
    fig.savefig(os.path.join(out, name + ".pdf"))
    plt.close(fig)
    print(f"  wrote {name}.{{png,pdf}}")


def series(d, k):
    m = d["i"] == k
    o = np.argsort(d["X"][m])
    return m, o, d["X"][m][o]

# ------------------------------------------------------------------- figure 1

# _base.md figures 1-3: the three estimators per bin, one run per figure.
# Axes are deliberately shared across the three so they can be compared directly.
EST_YLO, EST_YHI = 3.0e-5, 1.2e-1
EST_RLO, EST_RHI = 0.85, 9.0
ESTIMATORS = [
    ("data_phifull_phisfold_bin10deg", "estatraw-vs-bin-phifull",
     "SoLID acceptance (2$\\pi$), 1660 bins", 0.8,
     "$E^{raw}$ sits above $E^{diag}$ in essentially every bin — a systematic offset, not a few outliers."),
    ("data_4pi_phifullbin_phisfold_bin10deg", "estatraw-vs-bin-4pi_phifullbin",
     "4$\\pi$ (acccut off), same 1660 bins", 0.8,
     "All three coincide: the acceptance, not the binning, is what separates them."),
    ("data_4pi_phisfold_bin10deg", "estatraw-vs-bin-4pi",
     "4$\\pi$ (acccut off), own 20614 bins", 0.45,
     "All three coincide here too. Own binning, so these bins correspond to no other run."),
]


def fig_estimators(run, name, lab, lw, note, cache, out):
    d = load(run, cache)
    if d is None:
        return False
    fig = plt.figure(figsize=(15, 14))
    gs = GridSpec(6, 1, height_ratios=[3, 1.15] * 3, hspace=0.10, figure=fig)
    axes = [fig.add_subplot(gs[r]) for r in range(6)]
    for k in range(3):
        A, R = axes[2 * k], axes[2 * k + 1]
        m, o, x = series(d, k)
        raw, dg, pr = d["raw"][m][o], d["diag"][m][o], d["prop"][m][o]
        A.plot(x, raw, lw=lw, color=BLUE, label="$E^{raw}$ (row norm, production)")
        A.plot(x, dg, lw=lw, color=ORANGE, label="$E^{diag}$ (least squares)")
        A.plot(x, pr, lw=lw * 0.7, color=AQUA, ls="--", label="$E^{prop}$ (PR-10-006 App. II)")
        A.set_yscale("log"); A.set_ylim(EST_YLO, EST_YHI)
        A.set_ylabel(f"$E_{k}$statraw  ({AMP[k]})"); A.set_xticklabels([])
        group_labels(A, d["off"])
        r1, r2 = raw / dg, dg / pr
        R.plot(x, r1, lw=lw, color=BLUE, label=f"$E^{{raw}}/E^{{diag}}$   median {np.median(r1):.5f}")
        R.plot(x, r2, lw=lw, color=AQUA, label=f"$E^{{diag}}/E^{{prop}}$   median {np.median(r2):.5f}")
        R.axhline(1.0, color=INK2, lw=1.0, ls=":")
        R.set_yscale("log"); R.set_ylim(EST_RLO, EST_RHI); R.set_ylabel("ratio", fontsize=8.5)
        R.set_yticks([1, 2, 4, 8]); R.set_yticklabels(["1", "2", "4", "8"], fontsize=8)
        R.legend(fontsize=8, frameon=True, edgecolor=MUTED, labelcolor=INK2, loc="upper left", ncol=2)
        if k < 2:
            R.set_xticklabels([])
        frame(A, d["off"]); frame(R, d["off"])
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h[:3], l[:3], fontsize=9, frameon=True, edgecolor=MUTED, labelcolor=INK2,
               loc="upper center", bbox_to_anchor=(0.5, 0.928), ncol=3)
    axes[5].set_xlabel("bin index (four groups concatenated in the order shown)")
    fig.suptitle(f"$E$statraw per bin, with ratio panels — {run}\n{lab}   ·   "
                 f"main and ratio y-axes identical across all three figures\n{note}",
                 fontsize=12, color=INK)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.885, bottom=0.045)
    save(fig, name, out)
    return True

# ------------------------------------------------- _other.md figures 1 and 2

FOUR = [("data_phifull_phisfold_bin1deg", "phifull, $\\phi_S$ fold", BLUE, "-", 0.9),
        ("data_phifull_phisunfold_bin1deg", "phifull, $\\phi_S$ unfold", AQUA, "--", 0.7),
        ("data_4seg24deg_phifullbin_phisfold_bin1deg", "4$\\times$24$^\\circ$, $\\phi_S$ fold", ORANGE, "-", 0.9),
        ("data_4seg24deg_phifullbin_phisunfold_bin1deg", "4$\\times$24$^\\circ$, $\\phi_S$ unfold", PURPLE, "--", 0.7)]


def fig_fourruns(cache, out):
    D = {r[0]: load(r[0], cache) for r in FOUR}
    if any(v is None for v in D.values()):
        return False
    base = FOUR[0][0]
    off = D[base]["off"]
    assert all(np.array_equal(D[r[0]]["X"], D[base]["X"]) and
               np.array_equal(D[r[0]]["i"], D[base]["i"]) for r in FOUR), \
        "the four runs are not on the same bins"
    fig = plt.figure(figsize=(15, 14))
    gs = GridSpec(6, 1, height_ratios=[3, 1.15] * 3, hspace=0.10, figure=fig)
    axes = [fig.add_subplot(gs[r]) for r in range(6)]
    for k in range(3):
        A, R = axes[2 * k], axes[2 * k + 1]
        sel = {}
        for name, lab, col, ls, lw in FOUR:
            d = D[name]; m, o, x = series(d, k)
            y = d["prop"][m][o]; sel[name] = (x, y)
            A.plot(x, y, lw=lw, color=col, ls=ls, label=lab)
        A.set_yscale("log"); A.set_ylim(2.0e-4, 2.0e2)
        A.set_ylabel(f"$E_{k}$statraw_prop  ({AMP[k]})"); A.set_xticklabels([])
        group_labels(A, off)
        xb, yb = sel[base]
        for name, lab, col, ls, lw in FOUR[1:]:
            r = sel[name][1] / yb
            R.plot(sel[name][0], r, lw=lw, color=col, ls=ls,
                   label=f"{lab} / baseline   median {np.median(r):.4f}")
        R.axhline(1.0, color=INK2, lw=1.0, ls=":")
        R.set_yscale("log"); R.set_ylim(0.9, 4.0e3)
        R.set_ylabel("ratio to\nphifull fold", fontsize=8.5)
        R.set_yticks([1, 10, 100, 1000]); R.set_yticklabels(["1", "10", "100", "1000"], fontsize=8)
        R.legend(fontsize=8, frameon=True, edgecolor=MUTED, labelcolor=INK2, loc="upper left", ncol=3)
        if k < 2:
            R.set_xticklabels([])
        frame(A, off); frame(R, off)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h[:4], l[:4], fontsize=9, frameon=True, edgecolor=MUTED, labelcolor=INK2,
               loc="upper center", bbox_to_anchor=(0.5, 0.928), ncol=4)
    axes[5].set_xlabel("bin index (four groups concatenated in the order shown)")
    fig.suptitle("$E$statraw_prop per bin — four 1$^\\circ$-histogram runs on the same 1660 bins\n"
                 "acceptance (phifull vs 4$\\times$24$^\\circ$) $\\times$ $\\phi_S$ treatment (fold vs unfold)\n"
                 "the $\\phi$ cut costs a factor ~4 at the median; folding $\\phi_S$ costs nothing",
                 fontsize=12, color=INK)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.885, bottom=0.045)
    save(fig, "estatraw_prop-vs-bin-bin1deg", out)
    return True


def fig_foldratio(cache, out):
    pairs = [("data_phifull_phisfold_bin1deg", "data_phifull_phisunfold_bin1deg", "phifull", BLUE),
             ("data_4seg24deg_phifullbin_phisfold_bin1deg",
              "data_4seg24deg_phifullbin_phisunfold_bin1deg", "4$\\times$24$^\\circ$", ORANGE)]
    D = {r: load(r, cache) for p in pairs for r in p[:2]}
    if any(v is None for v in D.values()):
        return False
    off = D[pairs[0][0]]["off"]
    fig = plt.figure(figsize=(15, 9))
    gs = GridSpec(3, 1, hspace=0.10, figure=fig)
    axes = [fig.add_subplot(gs[r]) for r in range(3)]
    for k in range(3):
        A = axes[k]
        for fo, un, lab, col in pairs:
            df, du = D[fo], D[un]
            m, o, x = series(df, k)
            r = du["prop"][m][o] / df["prop"][m][o]
            A.plot(x, r, lw=0.9, color=col,
                   label=f"{lab}:  unfold/fold   median {np.median(r):.5f}, "
                         f"p95 {np.percentile(np.abs(r - 1), 95) * 100:.2f}% off 1, "
                         f"max {np.abs(r - 1).max() * 100:.1f}%")
        A.axhline(1.0, color=INK2, lw=1.0, ls=":")
        A.set_yscale("log"); A.set_ylim(0.9, 1.6)
        A.set_ylabel(f"$E_{k}$statraw_prop  ({AMP[k]})", fontsize=9)
        A.set_yticks([0.95, 1.0, 1.1, 1.3, 1.5])
        A.set_yticklabels(["0.95", "1", "1.1", "1.3", "1.5"], fontsize=8)
        A.legend(fontsize=8, frameon=True, edgecolor=MUTED, labelcolor=INK2, loc="lower left")
        frame(A, off)
        if k == 0:
            group_labels(A, off)
        if k < 2:
            A.set_xticklabels([])
    axes[2].set_xlabel("bin index (four groups concatenated in the order shown)")
    fig.suptitle("$E$statraw_prop:  $\\phi_S$ unfold / fold, per bin — same 1660 bins, 1$^\\circ$ histogram\n"
                 "the ratio hidden at unity in the figure above, on a zoomed axis",
                 fontsize=12, color=INK)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.905, bottom=0.065)
    save(fig, "estatraw_prop-foldratio-bin1deg", out)
    return True

# ---------------------------------------------------- _other.md figure 3

# Two acceptances x two histogram bin widths. The pairs differ in NPHI alone --
# same bins, same phisfold, same everything else -- so each ratio is a pure
# bin-width effect, at full azimuth and under a cut.
BW = [("data_phifull_phisfold_bin10deg",  "data_phifull_phisfold_bin1deg",
       "phifull", BLUE),
      ("data_4seg24deg_phifullbin_phisunfold_bin10deg",
       "data_4seg24deg_phifullbin_phisunfold_bin1deg",
       "4$\\times$24$^\\circ$", ORANGE)]


def fig_binwidth(cache, out):
    D = {r: load(r, cache) for pair in BW for r in pair[:2]}
    if any(v is None for v in D.values()):
        return False
    off = D[BW[0][0]]["off"]
    for coarse, fine, lab, _ in BW:
        # the pair must differ in NPHI alone, or the ratio is not a bin-width effect
        for q in ("Nacc", "fn"):
            assert np.array_equal(D[coarse][q], D[fine][q]), f"{q} differs across the {lab} pair"
    fig = plt.figure(figsize=(15, 14))
    gs = GridSpec(6, 1, height_ratios=[3, 1.15] * 3, hspace=0.10, figure=fig)
    axes = [fig.add_subplot(gs[r]) for r in range(6)]
    for k in range(3):
        M, R = axes[2 * k], axes[2 * k + 1]
        for coarse, fine, lab, col in BW:
            m, o, x = series(D[coarse], k)
            a, b = D[coarse]["prop"][m][o], D[fine]["prop"][m][o]
            M.plot(x, a, lw=0.9, color=col, ls="-", label=f"{lab}, 10 deg (NPHI = 36)")
            M.plot(x, b, lw=0.7, color=col, ls="--", label=f"{lab}, 1 deg (NPHI = 360)")
            r = b / a
            n = np.isfinite(r)
            R.plot(x, r, lw=0.9, color=col,
                   label=f"{lab}:  1 deg / 10 deg   median {np.median(r[n]):.5f}, "
                         f"p95 {np.percentile(r[n], 95):.4f}, max {r[n].max():.3g}")
        M.set_yscale("log"); M.set_ylim(2.0e-4, 2.0e2)
        M.set_ylabel(f"$E_{k}$statraw_prop  ({AMP[k]})"); M.set_xticklabels([])
        group_labels(M, off)
        R.axhline(1.0, color=INK2, lw=1.0, ls=":")
        R.set_yscale("log"); R.set_ylim(0.8, 60)
        R.set_ylabel("1 deg / 10 deg", fontsize=8.5)
        R.set_yticks([1, 2, 5, 10, 30]); R.set_yticklabels(["1", "2", "5", "10", "30"], fontsize=8)
        R.legend(fontsize=8, frameon=True, edgecolor=MUTED, labelcolor=INK2, loc="upper left", ncol=2)
        if k < 2:
            R.set_xticklabels([])
        frame(M, off); frame(R, off)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h[:4], l[:4], fontsize=9, frameon=True, edgecolor=MUTED, labelcolor=INK2,
               loc="upper center", bbox_to_anchor=(0.5, 0.928), ncol=4)
    axes[5].set_xlabel("bin index (four groups concatenated in the order shown)")
    fig.suptitle("Azimuthal histogram bin width — $E$statraw_prop per bin, two acceptances\n"
                 "each pair differs in NPHI alone (36 vs 360), on the same 1660 bins\n"
                 "at full azimuth the ratio is flat; under the cut its tail reaches 37$\\times$",
                 fontsize=12, color=INK)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.885, bottom=0.045)
    save(fig, "estatraw_prop-binwidth", out)
    return True

# ------------------------------------------------------------------- driver

FIGURES = {
    "phifull":     ([ESTIMATORS[0][0]], lambda c, o: fig_estimators(*ESTIMATORS[0], c, o)),
    "4pi_sameBin": ([ESTIMATORS[1][0]], lambda c, o: fig_estimators(*ESTIMATORS[1], c, o)),
    "4pi":         ([ESTIMATORS[2][0]], lambda c, o: fig_estimators(*ESTIMATORS[2], c, o)),
    "fourruns":    ([r[0] for r in FOUR], fig_fourruns),
    "foldratio":   ([r[0] for r in FOUR], fig_foldratio),
    "binwidth":    ([r for pair in BW for r in pair[:2]], fig_binwidth),
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("figures", nargs="*", metavar="FIGURE",
                    help="which to build: " + ", ".join(FIGURES) + " (default: all)")
    ap.add_argument("--cache", default=os.path.join(HERE, ".dumps"),
                    help="where the text dumps live (default: ./.dumps)")
    ap.add_argument("--out", default=HERE, help="where the figures go (default: here)")
    ap.add_argument("--list", action="store_true", help="show what can be built, build nothing")
    args = ap.parse_args()

    want = args.figures or list(FIGURES)
    unknown = [n for n in want if n not in FIGURES]
    if unknown:
        sys.exit(f"unknown figure(s): {', '.join(unknown)}\nknown: {', '.join(FIGURES)}")
    if args.list:
        for n in FIGURES:
            runs, _ = FIGURES[n]
            print(f"  {n:12s} {'ready ' if have(runs, args.cache) else 'MISSING'}  <- {', '.join(runs)}")
        sys.exit(0)

    built = skipped = 0
    for n in want:
        runs, fn = FIGURES[n]
        print(f"{n}:")
        if not have(runs, args.cache):
            missing = [r for r in runs if not os.path.isdir(os.path.join(HERE, r))]
            print(f"  skipped — run directories not present: {', '.join(missing)}")
            skipped += 1
            continue
        built += 1 if fn(args.cache, args.out) else 0
    print(f"\n{built} figure(s) written, {skipped} skipped for missing input.")
    if skipped:
        print("Run directories are not in the repository; regenerate them with "
              "./analysis_neutron (see ../CLAUDE.md).")
