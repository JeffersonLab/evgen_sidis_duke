# The azimuthal cut and the \(\phi_S\) folding — `MUT3` study, part two

Companion to
[`SIDIS_MUT3_comparison_base.md`](SIDIS_MUT3_comparison_base.md), which derives
the `MUT3` error formulas and tests them by switching the detector off. **Section
numbers in the text below refer to that document**, not to this one: Section 3 is
the basis transformation, Section 5 the row-norm/diagonal dichotomy, Section 7
the \(4\pi\) test. Figure numbering continues from it — its figures are 1-3,
this document's are 4 and 5.

Everything here is measured on `Estatraw_prop`, the independent Appendix-II
route, so what follows tests the acceptance rather than the estimator.

---

## The two variations Section 7 left open (2026-08-27)

Section 7 varied one thing — whether the detector is there. This document varies
the two that remain: the **azimuthal sector cut** (`phicut`), and the
**\(\phi_S\) treatment** (`phisfold`) that Section 7 could only flag as a
caveat.

### Method

Four runs, a full 2\(\times\)2: acceptance \(\times\) \(\phi_S\) treatment.
All four reuse the baseline's step-1 bins by symlink, so all four carry the same
**1660 bins** and pair 1:1 with each other and with Figure 1.

The azimuthal histograms are booked at **1 deg**, not the 10 deg of Section 7:
`NPHI` in `SoLID_SIDIS_3He.h` is 360 rather than 36. It is a compile-time
constant, not a command-line argument, so these runs required a rebuild. Cost
scales as \(N_\phi^2\) — the cells per bin are \(N_\phi^2\cdot 3/2\) — which is
why the four runs together hold **6.0 GB** of `_hs.root` — 2.5 GB per full-2\(\pi\)
run, 566 MB per cut run — against 43 MB for the 10 deg baseline. They are the
reason `SIDIS_MUT3_comparison/data_*/` is not in the repository.

| run | `phicut` | `phisfold` | coverage |
|---|---|---|---|
| `data_phifull_phisfold_bin1deg` | 0 | `fold` | full 2\(\pi\) |
| `data_phifull_phisunfold_bin1deg` | 0 | `full` | full 2\(\pi\) |
| `data_4seg24deg_phifullbin_phisfold_bin1deg` | 4 | `fold` | 26.67% |
| `data_4seg24deg_phifullbin_phisunfold_bin1deg` | 4 | `full` | 26.67% |

### Result 1 — the two constructions still agree

\(\max|E^{\rm prop}/E^{\rm diag}-1|\) is \(6.0\times10^{-14}\),
\(1.1\times10^{-13}\), \(3.0\times10^{-13}\) and \(3.6\times10^{-12}\) across
the four runs. Section 3's basis transformation therefore cancels under a cut
azimuth and an unfolded \(\phi_S\) as well, at a 100\(\times\) finer histogram.
The one order of magnitude of drift is the cut runs' worse-conditioned \(G\),
not a difference in construction.

### Result 2 — folding \(\phi_S\) is a no-op, except where the bin is starved

\(E^{\rm prop}(\text{unfold})/E^{\rm prop}(\text{fold})\), 4980 amplitudes each:

| run pair | median | p95 deviation | \(>\)2% off 1 | max |
|---|---|---|---|---|
| full 2\(\pi\) | 0.99999 | 0.34% | **0.04%** | 1.030 |
| 4\(\times\)24 deg | 1.00038 | 0.95% | **1.95%** | 9.739 |

This settles Section 7's caveat quantitatively. At full azimuth the folded and
signed maps are interchangeable: two amplitudes in 4980 move by more than 2%,
the worst by 3%. Under the cut the support is diagonal in
\((\phi_h,\phi_S)\), folding mixes genuinely different regions, and the tail
opens — but it stays a tail, and it is a **starvation** effect rather than a
geometric one. The three worst amplitudes are all one bin, N11p bin 508, which
retains **Nacc = 16.1** events under the cut against \(4.6\times10^5\) at full
acceptance; the next worst, N8p bin 134, has Nacc = 49.4. Nothing with a
populated histogram moves.

So the historical `fold` behaviour was harmless at 2\(\pi\), which is where every
published projection was produced, and is harmless under a cut except in bins
whose errors are already meaningless.

### Result 3 — what the \(\phi\) cut costs, and how much of it is just counting

\(E^{\rm prop}(4\times24\deg)/E^{\rm prop}(2\pi)\), both folded, paired per bin:

| quantity | median | p68 | p95 | max |
|---|---|---|---|---|
| error ratio, all amplitudes | **4.13** | 5.82 | 17.0 | 3461 |
| accepted-event fraction Nacc(cut)/Nacc(2\(\pi\)) | 0.0706 | — | 0.159 (p95) | — |
| counting-only expectation \(\sqrt{1/f}\) | 3.76 | — | 13.1 | — |
| **excess beyond counting** | **1.05** | 1.23 | 2.25 | 20.5 |

Per amplitude the cost is Sivers **3.78**, Collins **4.32**, Pretzelosity
**4.32** — Sivers is the cheapest, as in `phicompare.md`. 11.4% of amplitudes
lose more than 10\(\times\) and 0.86% more than 100\(\times\); the extreme values
belong to bins holding as few as 4.03 events.

Two things are worth separating here.

**The cut keeps 7.1% of the events, not 26.7%.** The nominal coverage
\(4\times24/360\) applies to *one* azimuth. With `phiscope=all` the sectors are
required of the electron and of the hadron alike, and the median survival is
0.0706 — consistent with the two being independent, \(0.267^2=0.071\). Quoting
26.7% as the event cost of this configuration is wrong by a factor of nearly 4.

**Once that is accounted for, the lever-arm penalty at the median is only 5%.**
Against the 4\(\pi\) comparison in `runlog.md`, where removing the detector
entirely left a 1.24\(\times\) median excess beyond counting, cutting the azimuth
of an already-cut detector costs almost nothing extra *at the median* — the
SoLID acceptance has already spent most of the azimuthal lever arm. The tail is
a different story: p95 is 2.25 and the worst bin 20.5, so the cut does destroy
the azimuthal fit in individual bins, and those are the bins the \(\chi^2\)
notices.

### Result 4 — the row-norm bias roughly doubles under the cut

\(E^{\rm raw}/E^{\rm prop}\), production against Appendix II:

| run | median | p95 | max | fraction \(>1\) |
|---|---|---|---|---|
| phifull, fold | 1.1372 | 2.306 | 6.95 | 98.76% |
| phifull, unfold | 1.1376 | 2.310 | 6.96 | 98.78% |
| 4\(\times\)24 deg, fold | **1.3732** | 3.833 | 41.7 | 99.70% |
| 4\(\times\)24 deg, unfold | **1.3718** | 3.860 | 341.4 | 99.70% |

The 1.137 at full azimuth reproduces Section 7's 1.1348 at a 100\(\times\) finer
histogram, so **the defect is insensitive to the azimuthal bin width** — as it
must be, since it is a property of \(G\), not of how \(G\) is sampled. Cutting
the azimuth then drives it from 13% to 37% at the median and from 6.9\(\times\) to
41\(\times\) in the worst bin.

This is the direction Section 5 predicts: the row norm equals the diagonal only
when \(G\propto I\), and cutting the azimuth is precisely what makes \(G\)
off-diagonal. It also means **the defect is worst exactly where it matters most
for the \(\phi\)-coverage study** — every improvement factor quoted for a cut
configuration in `phicompare.md` is built on errors overstated by more than a
third at the median.

### Figures

Same layout as Figures 1-3: an amplitude per main panel, a ratio panel beneath,
four groups concatenated as N11p, N11m, N8p, N8m. A vector `.pdf` sits beside
each `.png`.

![Estatraw_prop per bin, four 1 deg runs](estatraw_prop-vs-bin-bin1deg.png)

**Figure 4 — `Estatraw_prop` per bin for all four runs.** The two full-azimuth
curves lie on top of one another and the two cut curves lie on top of one
another, which is Result 2 rendered as a picture: the pairs differ only in the
\(\phi_S\) treatment and are indistinguishable. The half-decade gap between the
pairs is Result 3. In the ratio panels the fold/unfold trace is pinned to unity
while the cut/uncut trace floats at ~4 with excursions past \(10^2\).

![Estatraw_prop, unfold over fold](estatraw_prop-foldratio-bin1deg.png)

**Figure 5 — the \(\phi_S\) unfold/fold ratio alone, on a zoomed axis.** The
trace hidden at unity in Figure 4. Full azimuth (blue) is flat to a few parts in
\(10^3\); the cut (orange) is flat too, punctuated by isolated spikes. Those
spikes are the starved bins of Result 2 — the axis is clipped at 1.6, so N11p
bin 508's 9.7\(\times\) runs off the top of all three panels.

---

## Verdict

Two conclusions, both one-directional.

**The \(\phi_S\) folding is not a source of error.** At full azimuth the folded
and signed maps agree to a few parts in \(10^3\); under a cut they part company
only in bins holding tens of events, whose errors are already meaningless. The
historical `fold` behaviour can be reproduced or abandoned without moving any
published number.

**The row-norm defect of Section 5 is worst exactly where the \(\phi\)-coverage
study lives.** It does not care about the azimuthal bin width — 1.137 at 1 deg
against 1.135 at 10 deg — but cutting the azimuth drives it from 13% to 37% at
the median and to 41\(\times\) in the worst bin. Every improvement factor quoted
for a cut configuration is built on errors overstated by more than a third at the
median, so switching production to `Estatraw_diag` matters more for
`phicompare.md` than it does for the \(2\pi\) baseline.

A third result is a measurement rather than a defect: the `4 x 24 deg`
configuration keeps **7.1% of accepted events, not the nominal 26.7%**, because
`phiscope=all` demands the sectors of the electron and the hadron alike. Priced
against that, its error inflation is almost entirely counting statistics —
1.05\(\times\) excess at the median, though 20.5\(\times\) in the worst bin.
