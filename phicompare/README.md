# Azimuthal-acceptance comparison

What SoLID's SIDIS neutron (3He) projections lose if the detector only covers
part of the azimuth. Standing conclusions of the study.

## The error budget of the prepared fit inputs

What `prepare.py` writes into `error_tot_<amplitude>`, split into its three terms
and compared across azimuthal-acceptance configurations, one rundir per
configuration. in dir **`errors_plot/`**, script, figures and the full write-up (decomposition, pairing rule, current results)
are there: [`errors_plot/README.md`](errors_plot/README.md).

## The φ-cut fit comparison (the notebooks)

`plot-transversity_phicompare.ipynb` (Collins → transversity $h_1$) and
`plot-sivers_phicompare.ipynb` (Sivers → $f_{1T}^{\perp(1)}$) — the two
notebooks that live in this directory alongside the `data_*` rundirs they read.
Same structure in both: load every fit, build the $x$-dependent band, plot it,
tabulate the error ratio to world, and (transversity only) reduce it to a
tensor-charge number. Each fits **world + one projection**, 500 replicas, never
the projection alone.

| key | run directory | acceptance | binning | bins |
|---|---|---|---|---|
| `world` | `../data_world` | existing world data — **the reference** | — | 146 rows (Collins) / 234 (Sivers) |
| `sbs` | `../data_world` | SBS projection, **stat-only panel** | — | 455 rows |
| `phifull` | `data_phifull` | full 2π (100%) | own | 1660 |
| `phi4seg_fullbin` | `data_phi4seg24deg_phifullbin` | 4 × 24° (26.7% nominal), both arms | reused from `phifull` | 1660 |
| `phi4seg` | `data_phi4seg24deg` | 4 × 24°, both arms | own | 169 |
| `phi4segFA_fullbin` | `data_phi4seg24degFA_phifullbin` | 4 × 24°, forward angle only | reused from `phifull` | 1660 |
| `phi4segFA` | `data_phi4seg24degFA` | 4 × 24°, forward angle only | own | 239 |

**`_fullbin` versus own bins is not a detail.** A `_fullbin` run inherits
`phifull`'s 1660 bins and is comparable to it row by row; an own-bins run
re-bins under its own acceptance and shares no bin with anything, so a
`phifull`-vs-own-bins number mixes the φ-cut effect with a pure binning effect.

**How much is binning rather than acceptance** can be read off directly, since
an own-bins run and its `_fullbin` twin have the *same* acceptance and differ
only in binning:

| pair (same acceptance) | stat | stat+syst |
|---|---|---|
| `phi4seg` / `phi4seg_fullbin` | **1.15×** | **1.57×** |
| `phi4segFA` / `phi4segFA_fullbin` | **1.14×** | **1.57×** |

(1.00 would mean binning costs nothing; these are $E(g_T^{u-d})$ ratios.) So
~15% of the apparent φ-cut cost in a `phifull`-vs-own-bins stat comparison is
bin coarsening, and on Sivers $\langle k_T^2\rangle$ it is **40%** (5.61 against
4.02). **Use the `_fullbin` runs for the φ-cut effect.**

The coarsening loss is real information, not an artefact: 169 bins average over
shape the fit could otherwise use. Note the asymmetry — going the other way,
1660 → 19074 bins, changes $\langle k_T^2\rangle$ by a factor 0.999, i.e.
nothing (see "The binning comparison" below). 1660 bins already resolve the
shape; only coarsening below it costs.

**Direction, corrected 2026-09-07:** an earlier version of this file said an
own-bins run looks *better* than its `_fullbin` twin. On the runs currently on
disk it looks **worse** — `phi4seg` reaches 4.79× against `phi4seg_fullbin`'s
5.53×, `phi4segFA` 5.69× against 6.49×, and the same holds for $g_T$ and six of
the seven Sivers parameters. The warning to keep the two apart stands and is
better supported than before; only the stated direction was wrong.

**SBS is a reference, not a SoLID configuration**: no systematics model of its
own, so it is stat-only and absent from every stat+syst panel.

**The stat+syst panels of this comparison are not reliable, and matched
binning does not save them.** The per-bin systematic is treated as
uncorrelated, so it dilutes as $1/N_{\rm bins}$ — and it suppresses a
systematics-limited run's error far more than a stat-limited one's, which
`phifull` and the φ-cut runs respectively are. The stat-only panels are sound.
Details, numbers and the correction are in "The binning comparison" at the end
of this file; the own-bins runs carry an additional, separate distortion on top.

### Running it


```
source /usr/share/Modules/init/zsh && source ../setup.sh
jupyter nbconvert --to notebook --execute --inplace plot-transversity_phicompare.ipynb
jupyter nbconvert --to notebook --execute --inplace plot-sivers_phicompare.ipynb
```

Each rebuilds every band from its `out-*.dat` fits on disk — nothing here reruns
`fitcollins.py`/`fitsivers.py`; run those first if a rundir's fit is missing or
stale. Needs `matplotlib`, `pandas`, and `tmd.py` on the path (`sys.path` is set
to the repo root in cell 1).

### The figures

All in `gallery/`, `.pdf` only:

| file | shows |
|---|---|
| `trans-phicompare.pdf` / `sivers-phicompare.pdf` | $xh_1(x)$ / $xf_{1T}^{\perp(1)}(x)$ bands, every run, stat only |
| `trans-phicompare-syst.pdf` / `sivers-phicompare-syst.pdf` | same, stat+syst |
| `trans-doveru-phicompare.pdf` | $-h_1^d(x)/h_1^u(x)$, stat+syst (transversity only) |
| `gt-phicompare.pdf` | truncated tensor charge $g_T$, every run, stat vs stat+syst (transversity only) |

**Each band figure is drawn at one $Q^2$, 2.4 GeV²**, named in `Q2LIST` and
labelled on the panel. The plotting loops over that list, so extra $Q^2$ can be
added back by editing the one line; further entries appear as central curves in
lighter, thinner strokes (weight rather than linestyle, since solid/dashed already
carries $u$/$d$) with the error band on the first only. $u$ and $d$ are labelled on
the curves themselves, each placed by the **sign** of its own lobe, so it reads
correctly for transversity ($u>0$, $d<0$) and for Sivers, where the signs are
reversed.

Only one $Q^2$ is drawn because **nothing in the comparison depends on it** — see
"Why the error ratios do not depend on $Q^2$" below.

The *curves* do move with $Q^2$, by 1.0× to 4.4× the SoLID band half-width across
$0.1 < x < 0.6$; they look close together only because the axis spans $\pm0.45$
while the shifts are $\sim0.03$. **Quote the $Q^2$ with any $g_T$ or band value.**
Full reasoning in `../physics.md`, step 5, "Neither distribution has a $Q^2$
evolution of its own".

### What it currently shows

Truncated $g_T(u-d)$, $0.05<x<0.6$, statistical only — the single-number version
of "how much does SoLID improve on current knowledge":

| run | $E(g_T^{u-d})$ | world / this |
|---|---|---|
| world | 0.1701 | 1.00× |
| sbs | 0.0395 | 4.31× |
| `phifull` | 0.0107 | **15.86×** |
| `phi4seg_fullbin` | 0.0308 | 5.53× |
| `phi4seg` | 0.0355 | 4.79× |
| `phi4segFA_fullbin` | 0.0262 | 6.49× |
| `phi4segFA` | 0.0299 | 5.69× |

Stat+syst version tops out lower, at **8.71×** for `phifull` — its factor
roughly halves once systematics are added (retaining 55% of the stat-only
value), the largest relative hit of the five. The two `_fullbin` configs barely
move (92%); the two own-bins configs sit in between (66-68%). Consistent with
`errors_plot/README.md`'s finding that Collins is systematics-limited at full
acceptance (73.6% of bins) while a φ cut inflates the statistical term past the
systematics, so the cut configurations have less systematic error left to add.

Sivers has no tensor-charge analogue, so its compact summary is the replica
spread of the fitted parameters themselves. `kt2` is the one to watch — it sets
the transverse-momentum width, which a φ cut degrades most directly. **Do not
read the "vs world" parameter columns as a precision comparison**: `fitworld()` and
`fitsim()` fix *different* parameters (world floats 7, SoLID floats 9), so
individual parameter spreads are not on equal footing even when the observable
itself is far better constrained. The band ratios above are the comparison
that marginalises correctly; the run-to-run parameter column (SoLID configuration
against `phifull`, both `fitsim`) is the one that isolates the φ-cut effect
cleanly.

Three standing warnings apply to every number pulled from these notebooks — see
`../CLAUDE.md`: don't quote a `fitworld` vs `fitsim` *parameter* as a precision
statement (compare bands or $g_T$ instead); improvement factors carry ~±20%
run-to-run noise; `tol` sets every absolute band width and cancels only in
ratios.

## The binning comparison (`*_phicompare_morebin.ipynb`)

`plot-transversity_phicompare_morebin.ipynb` and
`plot-sivers_phicompare_morebin.ipynb` are copies of the two above, retargeted
to a different question: **what does the binning alone do?** They compare

| key | run directory | bins |
|---|---|---|
| `phifull` | `data_phifull` | 1660 |
| `countbin` | `data_phifull_countbin1e6` | **19074** |

Same pseudodata, same full-2π acceptance, same 500 replicas — the *only*
difference is the bin file. `data_phifull_countbin1e6`'s bins came from
`../make_bins_from_count.py` at `-N 1e6` over the opt-4 count table (see
`../runlog.md`, 2026-09-06/07). `world` and `SBS` are kept as reference.

They write to **`gallery_countbin1e6/`**, not `gallery/`. That is not cosmetic:
pointed at `gallery/` they overwrite the six tracked φ-cut figures with a
different comparison, which is what happened on their first run.

### What it found: statistically nothing, and a systematics artifact

**Statistically the finer binning buys nothing**, which is the expected answer —
rebinning the same events creates no information. $g_T(u-d)$ error 0.0107 →
0.0116 (15.9x → 14.7x over world), inside the ±20% run-to-run noise; the Sivers
parameter errors land at 0.90–1.00 of the baseline against a 3.2% replica floor.

**The stat+syst "improvement" is an artifact of the error model and must not be
quoted.** It looks large — $g_T$ 0.0195 → 0.0134, i.e. 8.7x → 12.7x, and the
Sivers $\langle k_T^2\rangle$ error halves — but it comes entirely from treating
a correlated systematic as independent per bin.

`../prepare.py:110` builds `error_tot` $=\sqrt{\text{stat}^2 + \text{systabs}^2 +
A^2\,\text{systrel}^2}$ **per bin**, and the χ² sums bins in quadrature, so the
relative systematic enters as if uncorrelated. Split a bin into $k$ sub-bins:
the statistical error grows as $\sqrt{k}$ while $\sigma_{\rm syst}=A\,$`systrel`
stays the same size, so the fit's effective variance becomes

$$\sigma^2_{\rm eff} = \text{stat}^2 + \frac{\text{syst}^2}{k}$$

— the statistical term preserved, the systematic term **divided by $k$**.

The notebooks' own "systematics penalty" row measures exactly that. Converting
$\text{std(stat+syst)}/\text{std(stat)}$ to the implied systematic *variance*
share gives ratios of 5.7x, 4.5x, 10.4x and 10.1x for `Nd`, `ad`, `bd` and
`kt2` — against a bin-count ratio of **11.5x**. The systematic is falling as
$1/N_{\rm bins}$, to within the accuracy of the comparison.

It should not fall at all. `systrel` is target polarization 3% ⊕ nuclear effect
5% ⊕ radiative correction 2.5% ⊕ diffractive meson 3% ⊕ random coincidence 0.2%
= 7.02% (`../SoLID_SIDIS_3He.h`), and every term is common to all bins: if the
target polarization is 3% high, every bin's asymmetry moves together. The true
covariance carries a rank-1 term $(A_i\,\text{systrel})(A_j\,\text{systrel})$,
and $k$ copies of one coherent shift carry no new information about it. Fixing
this means a covariance matrix with those off-diagonal terms, or a nuisance
parameter for the overall scale — a change to the χ², not to the binning.

**Scope — and equal bin counts are NOT enough.** It is tempting to conclude
that the dilution cancels whenever both sides have the same $k$. It does not.
The *factor* cancels; its **impact** does not, because that depends on how
systematics-limited each side is:

| run | systematics penalty | syst share of variance |
|---|---|---|
| `phifull` | 2.38 | **82%** |
| `phi4seg_fullbin` | 1.17 | 27% |

Both have 1660 bins, yet the dilution suppresses `phifull`'s error almost
entirely and `phi4seg_fullbin`'s barely at all. So **the stat+syst φ-cut
comparison is distorted too**, even though its binning is matched. Measured on
$\langle k_T^2\rangle$: the φ cut costs a factor 4.02 in the stat panel but only
1.97 in stat+syst, and undoing the dilution (multiplying the systematic variance
by $N_{\rm eff}\approx1177$, the fully-correlated extreme) moves that 1.97 to
**~1.13**. The current stat+syst panel therefore **overstates the cost of the φ
cut** — with a properly correlated systematic both runs are systematics-limited
and losing statistics stops mattering much. The truth is between the two
extremes, since the fit can partly constrain a common normalisation from the
shape of the data, but the shipped number is at the wrong end of that range.

A check that the picture is self-consistent: the systematic's *absolute*
variance contribution is 4.66 (`phifull`) against 5.96 (`phi4seg_fullbin`) in
common units — nearly run-independent, as it must be for the same `systrel` on
the same bins.

**So: the stat-only φ-cut comparison is sound** (matched bins, matched
treatment, differences are real statistics), **and the stat+syst one is not a
number to quote.** The own-bins runs (169 and 239) are further affected, and are
already excluded for the separate bin-width reason given above.

### Does this explain the own-bins vs `_fullbin` gap? Partly, and only partly

The φ-cut table above has its own binning pair at fixed acceptance —
`phi4seg_fullbin` (1660 bins) against `phi4seg` (169), and the `FA` twins — so
the obvious question is whether the gap between them is the same artifact.

**The direction is the same.** Fewer bins means less dilution and so a larger
systematics penalty, and that is what the notebook shows, mirrored:

| pair | bins | $\langle k_T^2\rangle$ penalty |
|---|---|---|
| `countbin` / `phifull` | 19074 / 1660 | 1.21 / 2.38 |
| `phi4seg_fullbin` / `phi4seg` | 1660 / 169 | 1.17 / **1.41** |
| `phi4segFA_fullbin` / `phi4segFA` | 1660 / 239 | 1.16 / **1.42** |

Both own-bins runs sit above their 1660-bin twins at identical acceptance and
near-identical total $N_{\rm acc}$.

**The magnitude does not follow.** Taking the systematic's variance share,
$\text{penalty}^2-1$, its ratio within a pair should equal the bin ratio if
dilution were all of it:

| pair | observed | bin ratio |
|---|---|---|
| `phifull` vs `countbin` | 0.10 | 0.09 — matches |
| `phi4seg_fullbin` vs `phi4seg` | 2.68 | 9.82 — does not |
| `phi4segFA_fullbin` vs `phi4segFA` | 2.94 | 6.95 — does not |

Two explanations were tried and **falsified**, recorded so they are not
re-derived: it is not the *effective* bin count either (participation ratio
$(\sum N)^2/\sum N^2$ gives 10.3 and 9.8, no closer), and the totals are not to
blame — each pair's total $N_{\rm acc}$ agrees to 5%.

The relation that does hold is with **events per bin**, as it should:
$\sigma_{\rm syst}/\sigma_{\rm stat} \propto A\,\text{systrel}\sqrt{N_{\rm acc}}$,
so $\text{penalty}^2-1$ should track $N_{\rm acc}$ per bin. It does — for four
of the six runs:

    run                 bins   Nacc/bin   pen^2-1   ratio
    phifull             1660   1.110e+07    4.664   4.20e-07
    countbin           19074   9.689e+05    0.464   4.79e-07
    phi4seg_fullbin     1660   8.100e+05    0.369   4.55e-07
    phi4segFA_fullbin   1660   8.889e+05    0.346   3.89e-07
    phi4seg              169   7.562e+06    0.988   1.31e-07   <- own bins
    phi4segFA            239   5.923e+06    1.016   1.72e-07   <- own bins

`phifull`, `countbin` and both `_fullbin` runs share **`phifull`'s bin
boundaries** — `countbin` subdivides them, the `_fullbin` runs reuse them
verbatim — so the dilution argument transfers cleanly and the constant holds to
±10%. The own-bins runs sit 2–3x below the line because their boundaries were
chosen independently by `GenerateBinInfoFile` under the reduced acceptance: they
cover different kinematics, with different mean asymmetry per bin and different
$p_T$ leverage on $\langle k_T^2\rangle$. The dilution formula assumes a
re-partition of the *same* regions and does not carry across a different binning
geometry.

**So the own-vs-`_fullbin` gap is a mixture** — part this systematics artifact,
part the genuine binning-geometry difference the φ-cut section already warns
about. The artifact is an additional contribution on top of that warning, not a
replacement for it, and it strengthens the same conclusion: **stat+syst
comparisons are only safe between runs at equal binning.**

## How many bins 4×24° actually needs — the scan

`data_phi4seg24deg_countbin800` (806 bins from `../make_bins_from_count.py` over
an opt-4 count table taken **under the φ cut**) against the two configurations
already on disk. Statistical only — the one panel comparable across bin counts,
since the per-bin systematic dilutes as 1/N_bins:

| binning | bins | $E(g_T^{u-d})$ | vs `_fullbin` | std(kt2) | vs `_fullbin` |
|---|---|---|---|---|---|
| own bins | 169 | 0.0355 | **1.154×** | 0.00906 | **1.395×** |
| **countbin** | **806** | **0.0305** | **0.992×** | **0.00666** | **1.026×** |
| `_fullbin` | 1660 | 0.0308 | 1.000× | 0.00649 | 1.000× |

**806 is statistically identical to 1660** (0.8% and 2.6%, inside the 3.2%
replica floor) while 169 is clearly worse. The curve descends from 169, flattens
by ~800, and stays flat. So:

- **"bin until stat ≈ A·systrel" is too coarse here.** It selects 166 bins, and
  `GenerateBinInfoFile`'s own-bins run has 169 — both encode the same rule, and
  both sit in the rising part of the curve.
- **1660 bins buy nothing over 800.** ~800 is the practical choice: full
  saturation at half the bin count, hence half the step-2 cost and half the
  exposure to the dilution artifact.
- Caveat: the 806 run differs from `_fullbin` in placement as well as count, so
  this says neither matters in that range — it does not isolate placement.

Saturation begins somewhere between 169 and 806; a rung at 400 would bracket it
and has not been run. Full numbers in `../runlog.md`, 2026-09-07/08.

## Adding SBS to each configuration (`*_phicompare_sbsenhanced3he.ipynb`)

Copies of the two notebooks reading `out-sbsenhanced3he_*.dat` (fit opt
`sbs+enhanced3he`) instead of `out-enhanced3he_*.dat`, with the standalone SBS
curve dropped — it is now inside every curve. They write to
`gallery_sbsenhanced3he/`.

**SBS adds nothing at full 2π and recovers ~1/6 of what a φ cut costs.**
$E(g_T^{u-d})$, statistical, SoLID alone → SoLID+SBS:

| run | alone | + SBS |
|---|---|---|
| `phifull` | 0.0107 (15.86×) | 0.0107 (15.86×) |
| `phi4seg_fullbin` | 0.0308 (5.53×) | **0.0260 (6.54×)** |
| `phi4seg` | 0.0355 (4.79×) | **0.0291 (5.85×)** |
| `phi4segFA_fullbin` | 0.0262 (6.49×) | **0.0246 (6.90×)** |
| `phi4segFA` | 0.0299 (5.69×) | **0.0260 (6.54×)** |

At full acceptance SoLID's 1660 bins swamp SBS's 455 rows; once a φ cut removes
~93% of SoLID's events, SBS's fixed contribution becomes relatively valuable.
`phifull` is unchanged only to display precision — its ndof goes 1800 → 2255,
exactly +455 SBS rows, and its parameter spreads tighten 6-9%. Sivers agrees: 13
of 14 like-for-like φ-cut ratios soften.

**These notebooks have no stat+syst panels, and that is deliberate.** There is no
`out-sbsenhanced3hesyst_*.dat` anywhere — `sbs+enhanced3hesyst` is the opt both
fit scripts refuse by name, because SBS carries no systematics model and pairing
its statistical errors with SoLID's stat+syst would weight SBS up for nothing but
the missing budget. Left running, those cells would still have written a
`*-syst.pdf` showing the world reference alone, which reads as a result and is
not one; they are switched off instead.

## Why SBS helps Sivers at high x but not Collins — the ε factor

A puzzle the band figures pose directly: **SBS covers high $x$ better than SoLID,
yet at high $x$ it closes most of the gap for Sivers and almost none of it for
Collins.**

From the 500-replica fits, SoLID 2π over SBS as an error advantage (both stat):

| $x$ | Collins $u$ | Collins $d$ | Sivers $u$ | Sivers $d$ | Collins/Sivers |
|---|---|---|---|---|---|
| 0.30 | 3.89 | 5.79 | 2.25 | 2.57 | 2.01 |
| 0.40 | 4.04 | 3.49 | 1.94 | 2.22 | 1.81 |
| 0.50 | 3.78 | 3.17 | 1.76 | 1.98 | 1.86 |
| 0.60 | **3.84** | **3.50** | **1.62** | **1.80** | **2.15** |

At $x = 0.6$ SBS is within 1.6–1.8× of SoLID for Sivers but 3.5–3.8× behind for
Collins.

**The cause is the depolarisation factor, and it is kinematic rather than
instrumental.** `AUTCollins` carries $\varepsilon(x,y,Q^2)$ and `AUTSivers` does
not:

```python
AUTCollins:  res = epsilon * FUTCollins(...) / FUUT(...)
AUTSivers:   res =           FUTSivers(...) / FUUT(...)
```

A bin's information about a parameter is $(\partial A/\partial\theta)^2/\delta A^2$
— the derivative squared over the variance — so for Collins that is
$\varepsilon^2(\partial G/\partial\theta)^2/\delta A^2$ and for Sivers the same
without the $\varepsilon^2$. Checked: $(\partial A/\partial N_u)/\varepsilon$ is
$-0.09045$ at $y = 0.30, 0.50, 0.70, 0.85$ alike, so the whole $y$ dependence of
the Collins derivative *is* $\varepsilon$.

And SBS sits at high $y$:

| | $y$ median | $\varepsilon$ median | $Q^2$ median |
|---|---|---|---|
| SBS | 0.777 | **0.387** | 5.42 |
| SoLID 2π | 0.559 | **0.721** | 2.22 |

Because $y = Q^2/(2 M E x)$, **SBS reaches high $x$ only by going to high $Q^2$**,
and high $Q^2$ at fixed $x$ forces $y$ up, which pushes $\varepsilon$ down. Its
better high-$x$ coverage is bought at exactly the price that hurts Collins and
leaves Sivers untouched.

Three independent routes agree at high $x$: the fitted ratio above is **1.8–2.15**,
a single-parameter Fisher calculation gives **1.98**, and the FOM-weighted
$\langle\varepsilon^2\rangle$ ratio is **1.91**.

**The agreement is a high-$x$ statement only.** Below $x \approx 0.3$ the Fisher
estimate and the fitted ratio diverge badly (3.61 against 0.93–1.60), because the
fit also carries world-data correlations and multi-parameter degeneracies that a
one-parameter Fisher number ignores, and because SBS's $(z, p_T)$ coverage differs
from SoLID's. Quote the $\varepsilon^2$ mechanism for the high-$x$ behaviour; do
not extend it across the range.


## Why the error ratios do not depend on $Q^2$

The figures are drawn at a single $Q^2$ = 2.4 GeV². They were briefly drawn at
three (2.4, 5.0, 7.5) to check what $Q^2$ costs: in the **upper** panel the curves
separate, but in the **lower** panel — the error ratio — all three fell exactly on
top of one another, so the extra curves were removed as redundant. Measured at
$x = 0.25$, world over `phifull`:

| | $Q^2 = 2.4$ | $Q^2 = 5.0$ | $Q^2 = 7.5$ |
|---|---|---|---|
| Collins, $xh_1^u$ | 8.3633643878 | 8.3633643878 | 8.3633643878 |
| Sivers, $x(f_{1T}^{\perp u} - f_{1T}^{\perp\bar u})$ | 8.0218563739 | 8.0218563739 | 8.0218563739 |

Identical to ten decimals, for both amplitudes.

**The reason is that $Q^2$ enters both distributions only through a factor common
to every replica.** In `tmd.py` each flavour is built as

$$h_1^q(x,Q^2) = \underbrace{N_q\,(\dots x \dots)}_{\text{parameters, }x\text{ only}} \times f_1^q(x,Q^2)$$

and `f1Tperp1` the same way. The parameter block carries no $Q^2$ at all. So
varying $Q^2$ multiplies *every* replica by the same $f_1^q(x,Q^2)$; the replica
standard deviation scales with it, and it cancels exactly in a ratio of two
standard deviations.

**For Sivers this holds only because the antiquark terms are fixed at zero.** The
plotted combination is $f_{1T}^{\perp u} - f_{1T}^{\perp\bar u}$, and $u$ and
$\bar u$ carry *different* PDFs with different evolution — so the factorisation
would break if both contributed. It does not, because `fitsivers.py` fixes `Nub`
and `Ndb` (they are in the `fix=` list; all 500 replicas of every fit have
`Nub = Ndb = 0.0` exactly), which kills the $\bar q$ term and leaves a single
common factor. **Free those two parameters and the ratios would acquire a genuine
$Q^2$ dependence.**

Three consequences:

1. **The comparisons in every figure and table are $Q^2$-independent.** Choosing
   2.4 rather than 5 changes no ratio anywhere.
2. **Absolute values are not.** $xh_1^u$ shifts $+2.9\%$ at $x=0.1$ and $-27\%$ at
   $x=0.6$ over $Q^2 = 2.4 \to 7.5$ — 1.0× to 4.4× the SoLID band half-width.
   **Quote the $Q^2$ with any $g_T$ or band number**; these notebooks use 2.4.
3. **No binning can resolve a $Q^2$ dependence this model does not have.** That is
   the underlying reason the 4× finer $Q^2$ re-binning of the SBS projection
   changed nothing (`../runlog.md`, 2026-09-11), and it is a property of the
   parameterisation rather than of the data.

Full derivation, including that real transversity evolves as a flavour non-singlet
while $f_1$ is a singlet — so tying one to the other is a modelling choice the fits
never test — is in `../physics.md`, step 5.
