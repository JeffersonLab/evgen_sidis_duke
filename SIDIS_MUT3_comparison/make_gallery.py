#!/usr/bin/env python3
"""The two phi-cut gallery figures, for one (full 2pi, phi-cut) pair of runs.

    source /usr/share/Modules/init/zsh && source ../setup.sh
    ./make_gallery.py <fullrun> <cutrun> [--tag=-SUFFIX]

e.g. ./make_gallery.py data_phifull_phisunfold_bin1deg \\
                       data_4seg24deg_phifullbin_phisunfold_bin1deg \\
                       --tag=-phisunfold-bin1deg

  hs-phifull-vs-4seg24deg[-TAG]   where the azimuth is sampled: the (phi_h, phi_S)
                                  map of 12 kinematic bins, uncut against cut
  hs-summary-phicut-cost[-TAG]    what that costs: surviving yield, error
                                  inflation against pure counting, and the
                                  conditioning of MUT3 behind the difference

Both runs must carry the same step-1 bins, or the 12 bin indices point at
different kinematics in each and nothing below means anything. The maps and the
3x3 MUT3 matrices come from extract_hs.C; the matrices are built at the full
histogram resolution, the maps are rebinned to 4 deg for display only.
"""
import argparse, os, subprocess, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def rundir(r):
    """Accept a run named relative to this directory or to the repo root."""
    for base in (HERE, REPO):
        p = os.path.join(base, r)
        if os.path.isdir(p):
            return p
    return None
ND = 90                       # display map is 90x90 (4 deg cells)
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#b8b7b2"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.titlecolor": INK,
                     "figure.facecolor": "white", "axes.facecolor": "white"})


def extract(full, cut, txt):
    """metas, uncut maps, cut maps, uncut MUT3, cut MUT3."""
    if not os.path.exists(txt):
        for r in (full, cut):
            if rundir(r) is None:
                sys.exit(f"run directory not found: {r}\n"
                         f"(run dirs are not in the repository; regenerate with ../analysis_neutron)")
        cmd = ["root", "-l", "-b", "-q",
               f'{os.path.join(HERE,"extract_hs.C")}("{rundir(full)}",'
               f'"{rundir(cut)}","{txt}")']
        r = subprocess.run(cmd, capture_output=True, text=True)
        if not os.path.exists(txt):
            sys.exit(f"extract_hs.C failed:\n{r.stdout}{r.stderr}")
    L = open(txt).read().split("\n")
    M, A, B, GA, GB = [], [], [], [], []
    i = 0
    while i < len(L):
        if not L[i].startswith("BIN"):
            i += 1
            continue
        M.append([float(v) for v in L[i].split()[1:]])   # idx x z Q2 Pt Na Nb ea eb
        i += 1
        for G, MAP in ((GA, A), (GB, B)):
            G.append(np.array([[float(v) for v in L[i + r].split()[1:]] for r in range(3)]))
            i += 3
            MAP.append(np.array([[float(v) for v in L[i + r].split()] for r in range(ND)]))
            i += ND
    return (np.array(M), np.array(A), np.array(B), np.array(GA), np.array(GB))


def fig_maps(M, A, B, full, cut, out, tag):
    ext = [-np.pi, np.pi, -np.pi, np.pi]
    fig, axes = plt.subplots(4, 6, figsize=(19, 13.5))
    for k in range(12):
        idx, x, z, Q2, Pt, Na, Nb, ea, eb = M[k]
        r, c = divmod(k, 3)
        c *= 2
        for j, (H, lab, N, e) in enumerate([(A[k], "full 2$\\pi$", Na, ea),
                                            (B[k], "4$\\times$24$^{\\circ}$", Nb, eb)]):
            ax = axes[r][c + j]
            ax.imshow(H, origin="lower", extent=ext, aspect="equal", cmap="Blues",
                      vmin=0, vmax=H.max(), interpolation="nearest")
            ax.set_title(f"{lab}\n$N_{{acc}}$={N:.2e}\n$E_0^{{prop}}$={e:.4f}", fontsize=8.5)
            ax.set_xticks([-3, 0, 3]); ax.set_yticks([-3, 0, 3])
            ax.tick_params(labelsize=7, length=2)
            for s in ax.spines.values():
                s.set_linewidth(0.6)
            if j == 0:
                ax.set_ylabel("$\\phi_S$", fontsize=9)
                ax.text(-0.60, 0.5, f"bin {int(idx)}\n$x$={x:.3f}\n$z$={z:.2f}\n"
                        f"$Q^2$={Q2:.2f}\n$P_T$={Pt:.2f}\n\n$E_0^{{prop}}$ ratio\n{eb/ea:.1f}$\\times$",
                        transform=ax.transAxes, fontsize=8, va="center", ha="center", color=INK2)
            if r == 3:
                ax.set_xlabel("$\\phi_h$", fontsize=9)
    fig.suptitle("Azimuthal sampling $(\\phi_h,\\phi_S)$ per kinematic bin — enhancedN11p, hs_full\n"
                 f"{os.path.basename(full)}  vs  {os.path.basename(cut)} (identical bins).  "
                 "Each panel is normalised to its own maximum:\nthese show WHERE the azimuth is sampled, "
                 "not how much. Absolute yields and errors are in the panel titles.",
                 fontsize=12.5, color=INK, y=0.985)
    fig.tight_layout(rect=[0.035, 0, 0.995, 0.945])
    for e in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"hs-phifull-vs-4seg24deg{tag}.{e}"), dpi=150)
    plt.close(fig)
    print(f"  wrote hs-phifull-vs-4seg24deg{tag}.{{png,pdf}}")


def fig_summary(M, GA, GB, out, tag):
    idxs = [int(m[0]) for m in M]
    yr = M[:, 6] / M[:, 5]                       # Nacc(cut) / Nacc(full)
    obs = M[:, 8] / M[:, 7]                      # E0prop(cut) / E0prop(full)
    stat = np.sqrt(1.0 / yr)                     # counting-only expectation
    excess = obs / stat
    cnd = np.array([np.linalg.cond(b) / np.linalg.cond(a) for a, b in zip(GA, GB)])

    fig, ax = plt.subplots(1, 3, figsize=(16, 5.2))
    o = np.argsort(yr)
    ax[0].hlines(np.arange(12), 0, yr[o], color=MUTED, lw=1)
    ax[0].plot(yr[o], np.arange(12), "o", ms=8, color=BLUE, zorder=3)
    ax[0].axvline(0.2667, color=ORANGE, lw=1.5, ls="--", label="nominal 26.7% (one arm)")
    ax[0].axvline(0.2667 ** 2, color=AQUA, lw=1.5, ls=":", label="7.1% (both arms, independent)")
    ax[0].legend(loc="lower right", fontsize=8, frameon=True, framealpha=0.95,
                 edgecolor=MUTED, labelcolor=INK2)
    ax[0].set_yticks(np.arange(12))
    ax[0].set_yticklabels([f"bin {idxs[i]}" for i in o], fontsize=8)
    ax[0].set_xlabel("surviving yield  $N_{acc}$(cut) / $N_{acc}$(full)")
    ax[0].set_title("A.  The $\\phi$ cut costs far more than its coverage", fontsize=10, loc="left")
    ax[0].set_xlim(0, 0.31); ax[0].set_ylim(-0.8, 11.8)
    ax[0].grid(axis="x", color=MUTED, lw=0.4, alpha=0.5); ax[0].set_axisbelow(True)

    lim = [1.2, 300]
    ax[1].plot(lim, lim, color=MUTED, lw=1.2, ls="--")
    ax[1].text(60, 42, "error tracks\nstatistics alone", color=INK2, fontsize=8, ha="center")
    ax[1].scatter(stat, obs, s=70, color=BLUE, zorder=3)
    for i in range(12):
        if excess[i] > 2 or excess[i] < 0.6:
            ax[1].annotate(f"{idxs[i]}", (stat[i], obs[i]), textcoords="offset points",
                           xytext=(7, -3), fontsize=8, color=INK2)
    ax[1].set_xscale("log"); ax[1].set_yscale("log"); ax[1].set_xlim(*lim); ax[1].set_ylim(*lim)
    ax[1].set_xlabel("expected from statistics alone,  $\\sqrt{N_{full}/N_{cut}}$")
    ax[1].set_ylabel("observed  $E_0^{prop}$(cut) / $E_0^{prop}$(full)")
    ax[1].set_title("B.  …and the error inflation is erratic", fontsize=10, loc="left")
    ax[1].grid(color=MUTED, lw=0.4, alpha=0.5); ax[1].set_axisbelow(True)

    ax[2].axhline(1, color=MUTED, lw=1.2, ls="--"); ax[2].axvline(1, color=MUTED, lw=1.2, ls="--")
    ax[2].scatter(cnd, excess, s=70, color=BLUE, zorder=3)
    for i in range(12):
        if cnd[i] > 3 or excess[i] > 2:
            ax[2].annotate(f"{idxs[i]}", (cnd[i], excess[i]), textcoords="offset points",
                           xytext=(7, -3), fontsize=8, color=INK2)
    ax[2].set_xscale("log"); ax[2].set_yscale("log")
    ax[2].set_xlim(0.45, 40); ax[2].set_ylim(0.2, 40)
    ax[2].set_xlabel("MUT3 conditioning blow-up,  cond(cut) / cond(full)")
    ax[2].set_ylabel("error excess beyond statistics")
    ax[2].set_title("C.  because the moment matrix degrades", fontsize=10, loc="left")
    ax[2].grid(color=MUTED, lw=0.4, alpha=0.5); ax[2].set_axisbelow(True)

    lo, hi = M[:, 1].min(), M[:, 1].max()
    fig.suptitle("4$\\times$24$^{\\circ}$ azimuthal cut vs full 2$\\pi$ — 12 bins spanning "
                 f"$x$ {lo:.3f}–{hi:.3f}, $Q^2$ {M[:,3].min():.1f}–{M[:,3].max():.1f}, "
                 f"$z$ {M[:,2].min():.2f}–{M[:,2].max():.2f}, "
                 f"$P_T$ {M[:,4].min():.2f}–{M[:,4].max():.2f} (enhancedN11p)",
                 fontsize=12, color=INK)
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    for e in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"hs-summary-phicut-cost{tag}.{e}"), dpi=150)
    plt.close(fig)
    print(f"  wrote hs-summary-phicut-cost{tag}.{{png,pdf}}")
    print(f"  medians — yield {np.median(yr):.4f}, error ratio {np.median(obs):.2f}, "
          f"counting {np.median(stat):.2f}, excess {np.median(excess):.2f}, "
          f"cond ratio {np.median(cnd):.2f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fullrun", help="run directory with the full 2pi azimuth")
    ap.add_argument("cutrun", help="run directory with the phi sector cut, SAME bins")
    ap.add_argument("--tag", default="", help="suffix for the output names, e.g. -phisunfold-bin1deg")
    ap.add_argument("--cache", default=os.path.join(HERE, ".dumps"))
    ap.add_argument("--out", default=HERE)
    args = ap.parse_args()

    os.makedirs(args.cache, exist_ok=True)
    slug = lambda r: r.replace("/", "_").strip("_")
    txt = os.path.join(args.cache, f"hs_{slug(args.fullrun)}__{slug(args.cutrun)}.txt")
    M, A, B, GA, GB = extract(args.fullrun, args.cutrun, txt)
    print(f"{len(M)} bins")
    fig_maps(M, A, B, args.fullrun, args.cutrun, args.out, args.tag)
    fig_summary(M, GA, GB, args.out, args.tag)
