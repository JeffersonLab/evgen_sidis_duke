# The `MUT3` statistical-error study

Whether the projected statistical errors this pipeline writes are the ones
Appendix II of [PR-10-006](https://hallaweb.jlab.org/collab/PAC/PAC35/PR-10-006-SoLID-Transversity.pdf)
prescribes — and what the acceptance does to them.

`AnalyzeEstatUT3` in `../SoLID_SIDIS_3He.h` builds a normal matrix $G$
(`MUT3`) per kinematic bin from the accepted azimuthal density in
$(\phi_h,\phi_S)$, inverts it, and forecasts the Sivers, Collins and
Pretzelosity uncertainties from the result. **Production takes the squared row
norms of $G^{-1}$; the covariance requires its diagonal.** The two agree only
when $G\propto I$ — flat, full coverage — and the study measures what that costs
under the real acceptance.

**Headline:** under the SoLID $2\pi$ acceptance the production form overestimates
by 13% at the median and up to $6.7\times$; with the detector switched off the two
forms agree to $3\times10^{-5}$; under a $4\times24^\circ$ azimuthal cut the
overestimate roughly doubles, to 37% at the median. Nothing downstream has been
switched over — the corrected values are recorded alongside, per bin, as
`Estatraw_diag` and `Estatraw_prop`.

## Where this is going (2026-08-30)

**The plan is to make `Estatraw_prop`, the 1 deg histogram and the unfolded
$\phi_S$ the defaults.**

Two of the three already are, and the third is one line:

| | state |
|---|---|
| 1 deg histogram | **already default** — `NPHI = 360` in `../SoLID_SIDIS_3He.h` |
| unfolded $\phi_S$ | **already default** — `use_unfolded_phiS = true`, i.e. `phisfold=full` |
| `Estatraw_prop` | **not yet** — see below |

`AnalyzeEstatUT3` writes all three estimators, but the hand-off to everything
downstream is `opt 3`'s CSV writer, which binds its `stat` column to **`E1stat`**
(Collins), and `Estat` is built from the production `Estatraw`. Switching means
pointing that `SetBranchAddress` at `E1stat_prop` instead. Nothing moves until
`analysis_neutron 3` → `prepare.py` → the fits are re-run.

Two things to settle when it is switched:

- **`Estat_prop` uses a `-1.0` sentinel, and `Estatraw_prop` can now be `nan`.**
  The line reads `(Estatraw_prop[i] >= 0.0) ? Estatraw_prop[i]/fn/0.6/0.86 : -1.0`,
  and `nan >= 0.0` is false — so a singular bin would reach the CSV as a
  **negative error**, not as `nan`. `Estatraw` itself now returns `NAN` there.
  The sentinel should go before `_prop` feeds anything.
- **Expect the errors to drop**, by ~13% at the median under the full $2\pi$
  acceptance and ~37% under a $4\times24^\circ$ cut, so every improvement factor
  built from them rises. `Estatraw_diag` would do equally well — the two agree to
  $10^{-12}$ — so this is a choice of construction, not of value.

## Documents

| file | holds |
|---|---|
| `SIDIS_MUT3_comparison_base.md` | the derivation: are the paper's matrix and the code's the same object, what the code actually computes, and the $4\pi$ test that isolates the acceptance. Figures 1-3 |
| `SIDIS_MUT3_comparison_other.md` | the acceptance study: the azimuthal cut, the $\phi_S$ folding, the histogram bin width, and the per-bin conditioning behind all of it. Standalone — it does not depend on `SIDIS_MUT3_comparison_base.md`. Figures 1-5 |

## Figures

Each is a `.png` and a `.pdf`; the write-ups embed the `.png`.

| file | shows | in |
|---|---|---|
| `estatraw-vs-bin-phifull` | the three estimators per bin under the SoLID acceptance | `SIDIS_MUT3_comparison_base.md` |
| `estatraw-vs-bin-4pi_phifullbin` | the same with the detector off, on the same bins | `SIDIS_MUT3_comparison_base.md` |
| `estatraw-vs-bin-4pi` | the same at $4\pi$ with its own binning | `SIDIS_MUT3_comparison_base.md` |
| `estatraw_prop-vs-bin-bin1deg` | four runs: acceptance $\times$ $\phi_S$ treatment | `SIDIS_MUT3_comparison_other.md` |
| `estatraw_prop-foldratio-bin1deg` | the $\phi_S$ unfold/fold ratio, zoomed | `SIDIS_MUT3_comparison_other.md` |
| `estatraw_prop-binwidth` | 1 deg against 10 deg azimuthal histogram, both acceptances | `SIDIS_MUT3_comparison_other.md` |
| `hs-phifull-vs-4seg24deg-phisunfold-bin1deg` | where the azimuth is sampled, 12 bins, uncut against cut | `SIDIS_MUT3_comparison_other.md` |
| `hs-summary-phicut-cost-phisunfold-bin1deg` | what the cut costs per bin, and the conditioning behind it | `SIDIS_MUT3_comparison_other.md` |

## Regenerating them

Both scripts need the repo environment (`source /usr/share/Modules/init/zsh`,
then `source ../setup.sh`) plus `matplotlib`, and both cache their text dumps in
`.dumps/`. **Delete `.dumps/` after re-running a step 2**, or a figure will be
redrawn from stale text.

```
./make_figures.py --list        # which figures their run dirs can build
./make_figures.py               # all that can be built
./make_figures.py binwidth      # one, by name

./make_gallery.py data_phifull_phisunfold_bin1deg \
                  data_4seg24deg_phifullbin_phisunfold_bin1deg \
                  --tag=-phisunfold-bin1deg
```

`make_figures.py` pulls the per-bin `Estat*` branches through `dump_estat.C`.
`make_gallery.py` takes one (full $2\pi$, $\phi$-cut) run pair and pulls the
`hs_full` maps and per-bin `MUT3` matrices through `extract_hs.C`; **both runs
must carry the same step-1 bins**, or its twelve bin indices point at different
kinematics in each.

## The run directories are not in the repository

6.7 GB of `.root`, gitignored, regenerated with `../analysis_neutron` (see
`../CLAUDE.md` for the CLI and `../runlog.md` for the commands as they were run).
A figure whose inputs are absent is skipped with a message rather than failing.

| run | acceptance | `phisfold` | `NPHI` | bins | size |
|---|---|---|---|---|---|
| `data_phifull_phisfold_bin10deg` | SoLID, full $2\pi$ | fold | 36 | 1660 | 43 MB |
| `data_4pi_phifullbin_phisfold_bin10deg` | none (`acccut off`) | fold | 36 | 1660 | 50 MB |
| `data_4pi_phisfold_bin10deg` | none (`acccut off`) | fold | 36 | 20614 | 612 MB |
| `data_phifull_phisfold_bin1deg` | SoLID, full $2\pi$ | fold | 360 | 1660 | 2.5 GB |
| `data_phifull_phisunfold_bin1deg` | SoLID, full $2\pi$ | full | 360 | 1660 | 2.5 GB |
| `data_4seg24deg_phifullbin_phisfold_bin1deg` | SoLID, $4\times24^\circ$ | fold | 360 | 1660 | 566 MB |
| `data_4seg24deg_phifullbin_phisunfold_bin1deg` | SoLID, $4\times24^\circ$ | full | 360 | 1660 | 566 MB |
| `data_4seg24deg_phifullbin_phisunfold_bin10deg` | SoLID, $4\times24^\circ$ | full | 36 | 1660 | 16 MB |

Every run but `data_4pi_phisfold_bin10deg` carries the same 1660 bins
(782 N11p + 536 N11m + 204 N8p + 138 N8m) and so pairs 1:1 with the others.
**`data_4pi_phisfold_bin10deg` pairs with nothing** — at $4\pi$ the adaptive
binning subdivides $12.4\times$ further, into its own 20614 bins.

`NPHI` is a compile-time constant in `../SoLID_SIDIS_3He.h`, not a command-line
argument, so the `_bin1deg` / `_bin10deg` suffix is the only record of which
binary produced a directory.
