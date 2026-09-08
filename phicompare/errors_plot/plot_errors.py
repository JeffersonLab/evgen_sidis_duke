#!/usr/bin/env python3
"""Compare the three error contributions in simenhanced3he.dat, bin by bin.

    source /usr/share/Modules/init/zsh && source ../../setup.sh
    ./phicompare/errors_plot/plot_errors.py [rundir ...] [--out DIR]

Run it from anywhere: rundirs are looked up relative to the cwd, then to this
directory, then to phicompare/ (this script's parent -- it moved into
phicompare/errors_plot/ on 2026-09-03; the rundirs stayed in phicompare/).
Figures land beside the script by default.

Default rundirs, in descending bin count: data_phifull (1660),
data_phi4seg24deg_phifullbin (1660, phifull's bins reused),
data_phi4seg24deg_countbin800 (806, its own count-table bins) and
data_phi4seg24deg (169, GenerateBinInfoFile's own bins). The last two share
the 4x24 deg acceptance with the second, so the three of them differ only in
binning -- see ../README.md for what that scan showed.
The third is the same 4x24 deg cut on its OWN bins -- 169 of them against the
other two's 1660 -- so its column shares no bin with theirs. Same x position,
different kinematics; compare the shape of its curves, never a value at a given
bin index.

prepare.py combines three terms into error_tot_<amplitude>:

    error_tot^2 = error_stat^2 + systabs^2 + (AUT * systrel)^2
                  \\___ 1 ___/   \\__ 2 __/   \\_____ 3 _____/

  1 error_stat_<amplitude>   the generator's projected statistical error, one per
                             amplitude -- the only term that knows about the
                             acceptance, and the only one a phi cut changes
  2 systabs                  absolute systematic, from the raw-asymmetry term
                             scaled by 1/(0.6 fn 0.86); same for all three
                             amplitudes, so it moves the small ones most
  3 |AUT| * systrel          relative systematic, systrel = 7.02% flat; this is
                             the only term proportional to the asymmetry itself,
                             so it tracks AUT and vanishes where AUT does

Absolute values are plotted: AUT changes sign across the bins and the axes are
logarithmic.

Two figures per invocation:
  errors-vs-bin[-TAG].png       the three terms per bin, one row per amplitude,
                                one column per rundir
  errors-ratio[-TAG].png        each systematic over the statistical error, i.e.
                                where systematics matter at all
  errors-ratio-phi[-TAG].png    each of the three terms, second rundir over the
                                first, i.e. what the phi cut costs term by term
                                (only when the two carry the same bins)
"""
import argparse, os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
PHICOMPARE = os.path.dirname(HERE)   # where the rundirs actually live


def rundir(r):
    """Resolve a run directory named relative to the cwd, this directory, or
    phicompare/, so the script works from anywhere."""
    for base in ('', HERE, PHICOMPARE):
        p = os.path.join(base, r) if base else r
        if os.path.isdir(p):
            return p
    return r
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#b8b7b2"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.titlecolor": INK,
                     "figure.facecolor": "white", "axes.facecolor": "white"})
# Pretzelosity is deliberately absent: tmd.AUTPretzelosity is still a placeholder
# whose normalisation is not established (code.md step 5), so plotting its error
# budget beside two fitted observables would invite comparison it cannot support.
AMPS = [("sivers", "Sivers"), ("collins", "Collins")]


# Stamped on every figure. Verified against SoLID_SIDIS_3He.h: Estat_prop (line
# 1076) and systabs (1231/1233) are both divided by fn * 0.6 * 0.86, while systrel
# (1225-1229) is a pure quadrature of relative uncertainties and carries none of
# them. physics.md names the constants P_3He = 0.6 (target polarisation) and
# P_n = 0.86 (effective neutron polarisation inside 3He).
NOTE = ("$\\delta_{stat}$ and systabs both carry the same $1/(f_n\\cdot 0.6\\cdot 0.86)$ scaling: "
        "kinematic-dependent dilution $f_n$, target polarisation $P_{^3He}=0.6$, "
        "effective neutron polarisation $P_n=0.86$.\n"
        "$|A_{UT}|\\cdot$systrel does not — systrel is the quadrature of the relative "
        "uncertainties alone (3% target pol, 5% nuclear, 2.5% radiative, 3% diffractive meson, "
        "0.2% random coincidence).")


def stamp(fig):
    fig.text(0.5, 0.005, NOTE, ha="center", va="bottom", fontsize=8.5, color=INK2)


def load(d):
    path = os.path.join(d, "simenhanced3he.dat")
    if not os.path.exists(path):
        sys.exit(f"error: {path} not found -- run ./prepare.py {d} first")
    d = pd.read_csv(path, sep=r"\s+")
    need = ["systrel", "systabs"] + [f"error_stat_{a}" for a, _ in AMPS] \
                                  + [f"AUT{n}" for _, n in AMPS]
    missing = [c for c in need if c not in d.columns]
    if missing:
        sys.exit(f"error: {path} is missing {missing}\n"
                 f"       (an older schema? re-run ./prepare.py {d})")
    return d


def terms(d, amp, name):
    """The three contributions to error_tot, in the order they are plotted."""
    return [("$\\delta_{stat}$",           d[f"error_stat_{amp}"].values,        BLUE),
            ("systabs",                    d["systabs"].values,                  ORANGE),
            ("$|A_{UT}|\\cdot$systrel",    (d[f"AUT{name}"] * d["systrel"]).abs().values, AQUA)]


def limits(values, room=0.0):
    """Decade-rounded (lo, hi) covering every series, so one axis fits all panels.

    `room` adds that many empty decades below the data, so the legend can sit in
    the lower half of the panel without covering a curve. It extends the axis
    rather than clipping it -- every point is still drawn.

    Derived from the data rather than hardcoded: the previous fixed ceiling of 3.0
    silently clipped the phi-cut statistical errors, which reach 822 in the worst
    starved bins. Only non-positive points are dropped, and only because the axis
    is logarithmic -- they are the zero crossings of |AUT|, where the relative
    systematic genuinely vanishes."""
    v = np.concatenate([np.asarray(y, dtype=float).ravel() for y in values])
    v = v[np.isfinite(v) & (v > 0)]
    return (10.0 ** (np.floor(np.log10(v.min())) - room),
            10.0 ** np.ceil(np.log10(v.max())))


def hadron_split(d):
    """Row index where pi+ ends and pi- begins, or None if not identifiable."""
    if "hadron" not in d.columns:
        return None
    h = d["hadron"].values
    edges = np.where(h[1:] != h[:-1])[0] + 1
    return edges[0] if len(edges) == 1 else None


def fig_terms(data, out, tag):
    n = len(data)
    ylo, yhi = limits([y for d in data.values() for a, nm in AMPS
                         for _, y, _ in terms(d, a, nm)], room=2.0)
    fig, axes = plt.subplots(len(AMPS), n, figsize=(7.6 * n, 4.0 * len(AMPS)), squeeze=False)
    for col, (rundir, d) in enumerate(data.items()):
        split = hadron_split(d)
        for row, (amp, name) in enumerate(AMPS):
            ax = axes[row][col]
            x = np.arange(len(d))
            for lab, y, c in terms(d, amp, name):
                ax.plot(x, y, lw=0.7, color=c, label=f"{lab}   median {np.median(y):.5f}")
            ax.set_yscale("log"); ax.set_ylim(ylo, yhi)
            ax.set_xlim(0, len(d))
            ax.grid(color=MUTED, lw=0.4, alpha=0.5); ax.set_axisbelow(True)
            ax.legend(fontsize=8, frameon=True, edgecolor=MUTED, labelcolor=INK2,
                      loc="lower left", framealpha=0.95)
            if split is not None:
                ax.axvline(split, color=MUTED, lw=1.0, ls=":")
                for lo, hi, t in ((0, split, "$\\pi^+$"), (split, len(d), "$\\pi^-$")):
                    ax.text((lo + hi) / 2, 0.97, t, transform=ax.get_xaxis_transform(),
                            ha="center", va="top", fontsize=9, color=INK2)
            if col == 0:
                ax.set_ylabel(f"{name}\nerror contribution")
            if row == 0:
                ax.set_title(f"{os.path.basename(rundir.rstrip('/'))}   ({len(d)} bins)",
                             fontsize=10, color=INK)
            if row == len(AMPS) - 1:
                ax.set_xlabel("bin index (as written by prepare.py)")
    fig.suptitle("The three terms of error_tot, per bin — "
                 "$error\\_tot^2 = \\delta_{stat}^2 + systabs^2 + (A_{UT}\\,systrel)^2$\n"
                 f"absolute values; one shared log axis {ylo:.0e}-{yhi:.0e} covering every "
                 "panel, nothing clipped (the bottom decades are empty, for the legend)",
                 fontsize=12, color=INK)
    fig.tight_layout(rect=[0, 0.055, 1, 0.955])
    stamp(fig)
    for e in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"errors-vs-bin{tag}.{e}"), dpi=140)
    plt.close(fig)
    print(f"  wrote errors-vs-bin{tag}.{{png,pdf}}")


def fig_ratio(data, out, tag):
    n = len(data)
    ylo, yhi = limits([y / d[f"error_stat_{a}"].values
                       for d in data.values() for a, nm in AMPS
                       for _, y, _ in terms(d, a, nm)[1:]], room=1.5)
    fig, axes = plt.subplots(len(AMPS), n, figsize=(7.6 * n, 4.0 * len(AMPS)), squeeze=False)
    for col, (rundir, d) in enumerate(data.items()):
        split = hadron_split(d)
        for row, (amp, name) in enumerate(AMPS):
            ax = axes[row][col]
            x = np.arange(len(d))
            stat = d[f"error_stat_{amp}"].values
            for lab, y, c in terms(d, amp, name)[1:]:
                r = y / stat
                ax.plot(x, r, lw=0.7, color=c,
                        label=f"{lab} / $\\delta_{{stat}}$   median {np.median(r):.3f}, "
                              f"above 1 in {100*np.mean(r > 1):.1f}% of bins")
            ax.axhline(1.0, color=INK2, lw=1.0, ls=":")
            ax.set_yscale("log"); ax.set_ylim(ylo, yhi)
            ax.set_xlim(0, len(d))
            ax.grid(color=MUTED, lw=0.4, alpha=0.5); ax.set_axisbelow(True)
            ax.legend(fontsize=8, frameon=True, edgecolor=MUTED, labelcolor=INK2,
                      loc="lower left", framealpha=0.95)
            if split is not None:
                ax.axvline(split, color=MUTED, lw=1.0, ls=":")
            if col == 0:
                ax.set_ylabel(f"{name}\nsystematic / statistical")
            if row == 0:
                ax.set_title(f"{os.path.basename(rundir.rstrip('/'))}   ({len(d)} bins)",
                             fontsize=10, color=INK)
            if row == len(AMPS) - 1:
                ax.set_xlabel("bin index (as written by prepare.py)")
    fig.suptitle("Each systematic over the statistical error, per bin — "
                 "above the dotted line the systematic dominates\n"
                 f"one shared log axis {ylo:.0e}-{yhi:.0e}; the statistical term is the only "
                 "one the acceptance changes, so a $\\phi$ cut pushes these ratios down",
                 fontsize=12, color=INK)
    fig.tight_layout(rect=[0, 0.055, 1, 0.955])
    stamp(fig)
    for e in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"errors-ratio{tag}.{e}"), dpi=140)
    plt.close(fig)
    print(f"  wrote errors-ratio{tag}.{{png,pdf}}")


def fig_ratio_phi(data, out, tag):
    """Each error term's ratio between the two configurations, bin by bin.

    Only meaningful when the two rundirs carry the SAME bins -- data_phifull
    against data_phi4seg24deg_phifullbin, which reuses phifull's step-1 bins. An
    own-bins run like data_phi4seg24deg has different kinematics at the same row
    index, so this figure is skipped unless the row counts match.

    What it separates: the phi cut changes only the statistical term directly.
    systabs moves only through the dilution fn, and |AUT| systrel only through the
    shifted mean kinematics of each bin, so any departure from 1 in those two is
    second-order."""
    items = list(data.items())
    pair = next((((a, x), (b, y)) for i, (a, x) in enumerate(items)
                 for b, y in items[i + 1:] if len(x) == len(y)), None)
    if pair is None:
        print("  ratio-phi: skipped, no two rundirs share a binning")
        return
    (n1, d1), (n2, d2) = pair
    if len(items) > 2:
        print(f"  ratio-phi: using the one pair that shares a binning, "
              f"{os.path.basename(n2)} / {os.path.basename(n1)}")
    series = {}
    for amp, name in AMPS:
        t1, t2 = terms(d1, amp, name), terms(d2, amp, name)
        series[amp] = [(lab, y2 / y1, c) for (lab, y1, c), (_, y2, _) in zip(t1, t2)]
    ylo, yhi = limits([r for v in series.values() for _, r, _ in v], room=1.5)

    fig, axes = plt.subplots(len(AMPS), 1, figsize=(15, 4.0 * len(AMPS)), squeeze=False)
    split = hadron_split(d1)
    for row, (amp, name) in enumerate(AMPS):
        ax = axes[row][0]
        x = np.arange(len(d1))
        for lab, r, c in series[amp]:
            f = np.isfinite(r)
            ax.plot(x, r, lw=0.7, color=c,
                    label=f"{lab}   median {np.median(r[f]):.3f}, "
                          f"p05-p95 {np.percentile(r[f],5):.3f}-{np.percentile(r[f],95):.3f}")
        ax.axhline(1.0, color=INK2, lw=1.0, ls=":")
        ax.set_yscale("log"); ax.set_ylim(ylo, yhi); ax.set_xlim(0, len(d1))
        ax.grid(color=MUTED, lw=0.4, alpha=0.5); ax.set_axisbelow(True)
        ax.legend(fontsize=8, frameon=True, edgecolor=MUTED, labelcolor=INK2,
                  loc="lower left", framealpha=0.95)
        ax.set_ylabel(f"{name}\ncut / full")
        if split is not None:
            ax.axvline(split, color=MUTED, lw=1.0, ls=":")
            for lo, hi, t in ((0, split, "$\\pi^+$"), (split, len(d1), "$\\pi^-$")):
                ax.text((lo + hi) / 2, 0.97, t, transform=ax.get_xaxis_transform(),
                        ha="center", va="top", fontsize=9, color=INK2)
        if row == len(AMPS) - 1:
            ax.set_xlabel("bin index (as written by prepare.py)")
    fig.suptitle(f"What the $\\phi$ cut does to each error term, per bin — "
                 f"{os.path.basename(n2.rstrip('/'))} / {os.path.basename(n1.rstrip('/'))}\n"
                 "only the statistical term is changed directly; systabs moves through the "
                 "dilution $f_n$, and $|A_{UT}|$systrel through the shifted mean kinematics",
                 fontsize=12, color=INK)
    fig.tight_layout(rect=[0, 0.065, 1, 0.94])
    stamp(fig)
    for e in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"errors-ratio-phi{tag}.{e}"), dpi=140)
    plt.close(fig)
    print(f"  wrote errors-ratio-phi{tag}.{{png,pdf}}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rundirs", nargs="*",
                    default=["data_phifull", "data_phi4seg24deg_phifullbin",
                             "data_phi4seg24deg_countbin800",
                             "data_phi4seg24deg"])
    ap.add_argument("--out", default=HERE, help="where the figures go (default: this directory)")
    ap.add_argument("--tag", default="", help="suffix for the output names")
    args = ap.parse_args()

    data = {r: load(rundir(r)) for r in args.rundirs}
    for r, d in data.items():
        print(f"{r}: {len(d)} rows")
    fig_terms(data, args.out, args.tag)
    fig_ratio(data, args.out, args.tag)
    fig_ratio_phi(data, args.out, args.tag)

    # the numbers behind the figures, so a claim can be quoted without reading pixels
    print(f"\n{'rundir':34s} {'amplitude':13s} {'stat':>9s} {'systabs':>9s} "
          f"{'|AUT|systrel':>13s} {'stat share':>11s}")
    for r, d in data.items():
        for amp, name in AMPS:
            t = [y for _, y, _ in terms(d, amp, name)]
            share = np.median(t[0]**2 / (t[0]**2 + t[1]**2 + t[2]**2))
            print(f"{os.path.basename(r):34s} {name:13s} {np.median(t[0]):9.5f} "
                  f"{np.median(t[1]):9.5f} {np.median(t[2]):13.5f} {100*share:10.1f}%")
