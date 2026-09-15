# The error budget of the prepared fit inputs

What `prepare.py` writes into `error_tot_<amplitude>`, split into its three
terms and compared across azimuthal-acceptance configurations. One script,
`plot_errors.py`, and the figures it produces. Moved here from `phicompare/`
on 2026-09-03, alongside the `plot-*_phicompare.ipynb` notebooks and their
`data_*` rundirs, which stayed one level up.

## The decomposition

```
error_tot^2 = error_stat^2 + systabs^2 + (AUT * systrel)^2
```

| term | what it is | does the acceptance change it? |
|---|---|---|
| `error_stat_<amp>` | the generator's projected statistical error, one per amplitude | **yes, directly** — this is the only term a $\phi$ cut acts on |
| `systabs` | absolute systematic, $1.7\times10^{-4}$ (11 GeV) or $2.57\times10^{-4}$ (8.8 GeV) scaled by $1/(f_n\cdot 0.6\cdot 0.86)$; identical for all three amplitudes | only through the dilution $f_n$ |
| $\lvert A_{UT}\rvert\cdot$`systrel` | relative systematic, `systrel` = 7.02% flat | only through each bin's shifted mean kinematics |

**`error_stat` and `systabs` both carry the same $1/(f_n\cdot 0.6\cdot 0.86)$
scaling** — kinematic-dependent dilution $f_n$, target polarisation
$P_{^3He}=0.6$, effective neutron polarisation $P_n=0.86$. The relative term does
not: `systrel` is the quadrature of 3% target polarisation, 5% nuclear effect,
2.5% radiative correction, 3% diffractive meson and 0.2% random coincidence, and
none of those pick up $f_n$ or the polarisations. Every figure carries this as a
footnote, because reading the three curves without it invites the wrong
conclusion about which one the acceptance drives.

## Running it

```
source /usr/share/Modules/init/zsh && source ../../setup.sh
./plot_errors.py                              # the four default rundirs
./plot_errors.py data_phifull --tag=-solo     # any set of rundirs
./plot_errors.py --out /tmp                   # figures elsewhere
./plot_errors.py --counts 4                   # as if every run had 4x the counts
```

**These figures are at the luminosity the run was generated with, unless `--counts`
says otherwise.** That is worth stating because the fit scripts have a `--counts`
flag and the notebooks next door plot 4x results: nothing here saw it. The flag
lives in the fit scripts' `load()`, applied at fit time, and the prepared
`simenhanced3he.dat` these figures read carries no notion of it.

`--counts F` reproduces the same substitution here — `error_stat` divided by
$\sqrt{F}$ and $N_{acc}$ multiplied by $F$, with `systabs` and $|A_{UT}|$`systrel`
untouched, because a systematic does not shrink with beam time. Output names take
an `-xFcounts` suffix, so a 4x figure never lands on a 1x one, and every panel title
and figure footer states which runs were scaled and which were not.

**`--counts` does not scale `data_phifull`.** The full-2π run is the reference the
φ-cut runs are measured against, not a configuration whose luminosity is in
question — the same convention `plot-*_phicompare.ipynb` follows, where `phifull`
reads the nominal fits and only the φ-cut entries read `_x4counts`. Scaling it here
would make these figures disagree with the notebooks about what 4x means. It is
pinned by the default rundir list, written `data_phifull:1`; any rundir may carry
its own factor that way, and `--counts F` is the fallback for those that do not.

**What `--counts` does not move: the floor ratio.** $\delta_{stat}$ and
$\sqrt{2/N_{acc}}/(f_n P_{^3\!He} P_n)$ both scale as $1/\sqrt{F}$, so their ratio
is invariant — verified identical to four decimals at 1x and 4x. The floor section
below is therefore a statement about the estimator, not about luminosity.

What it does change is the balance in `errors-vs-bin`: the statistical term drops
toward two fixed systematics. At 4x, the statistical share of $error\_tot^2$ goes

| rundir | amplitude | 1x | 4x | in the `-x4counts` figure |
|---|---|---|---|---|
| `data_phifull` | Sivers | 80.4% | *(50.7%)* | 80.4% — reference, not scaled |
| `data_phifull` | Collins | 25.3% | *(7.8%)* | 25.3% — reference, not scaled |
| `data_phi4seg24deg_phifullbin` | Sivers | 98.9% | 95.6% | 95.6% |
| `data_phi4seg24deg_phifullbin` | Collins | 90.7% | 71.0% | 71.0% |
| `data_phi4seg24deg_countbin800` | Sivers | 97.0% | 89.0% | 89.0% |
| `data_phi4seg24deg_countbin800` | Collins | 82.1% | 53.3% | 53.3% |
| `data_phi4seg24deg` | Sivers | 89.9% | 69.1% | 69.1% |
| `data_phi4seg24deg` | Collins | 38.9% | **13.7%** | 13.7% |

The `data_phifull` 4x column is parenthesised because **the figures do not scale
it** — it is shown only to answer the question directly. Taken on its own it is the
sharpest statement of why more beam time does so little for Collins: full 2π Collins
would be **92% systematics-limited at 4x**, against 75% at nominal, so there is
almost no statistical error left to remove. That is the per-bin picture behind the
fitted result that 4x the counts shrinks the Collins $g_T$ band only to ~0.9 of its
value (`../../runlog.md`, 2026-09-08). Sivers keeps headroom everywhere, which is
why it is the one that responds to beam time.

To see it in a figure, ask for it explicitly:
`./plot_errors.py --counts 4 data_phifull` — one rundir, no pin, its own suffix.

Rundirs resolve against the cwd, then this directory, then `phicompare/` (this
script's parent, and where the rundirs actually live — it moved one level
below them), so it runs from anywhere. Each must contain `simenhanced3he.dat`
from `prepare.py`; the script names the missing file and the command that
would produce it rather than failing on a KeyError. Figures land beside the
script as `.png` + `.pdf`.

Defaults, in descending bin count — all in `../`:

| rundir | bins | binning |
|---|---|---|
| `data_phifull` | 1660 | its own, full 2π |
| `data_phi4seg24deg_phifullbin` | 1660 | `phifull`'s, reused |
| `data_phi4seg24deg_countbin800` | 806 | its own, from an opt-4 count table |
| `data_phi4seg24deg` | 169 | its own, from `GenerateBinInfoFile` |

The last three share the 4×24° acceptance and **differ only in binning**, which
is what makes the per-term table below readable as a binning scan.

## The figures

| file | shows |
|---|---|
| `errors-vs-bin` | the three terms per bin, plus the $\sqrt{2/N_{acc}}$ counting limit |
| `errors-ratio` | each systematic over the statistical error — where systematics matter at all |
| `errors-ratio-phi` | each term, cut over full, for the one pair of rundirs that shares a binning |

**Layout: the rundirs are a 2×2 block per amplitude.** Four of them in a single
row made a figure 30 inches wide that nothing could read side by side; two columns
halve the width and double the height, leaving each panel the same size. Every
panel is titled with its amplitude and rundir, because with a 2×2 block the
rundirs are no longer aligned in columns and a column header would be ambiguous.
A fifth rundir simply starts a third row; unused panels are hidden.

**The dashed line is the statistical floor for this estimator**, and it is nearly
saturated:

$$\delta_{stat}^{floor} \;=\; \frac{\sqrt{2/N_{acc}}}{f_n \, P_{^3\!He} \, P_n}
\qquad P_{^3\!He}=0.6,\; P_n=0.86$$

$\sqrt{2/N_{acc}}$ alone is the error of a plain counting asymmetry over the bin's
accepted events, the $\sqrt{2}$ being the cost of the $\sin$ modulation. Every
estimator in `SoLID_SIDIS_3He.h` is then divided by $f_n P_{^3\!He} P_n$ before it
is written (`Estat_prop`, line 1236), so a like-for-like floor carries the same
scaling.

**$f_n$ is not a column** in `simenhanced3he.dat`. It is recovered from `systabs`,
which `CreateFile` builds as $c/(0.6 f_n 0.86)$ with $c = 1.7\times10^{-4}$ above
10 GeV and $2.57\times10^{-4}$ below (`SoLID_SIDIS_3He.h:1391-1393`), so
$f_n = c/(0.6 \cdot 0.86 \cdot systabs)$. On `data_phifull` that gives
$f_n \in 0.128\!-\!0.360$, median 0.278 — the effective neutron dilution of a
$^3$He target, which is the right order.

How close the real error sits to it:

| rundir | amplitude | median | min | max | bins below the floor |
|---|---|---|---|---|---|
| `data_phifull` | Sivers | 1.0725× | 0.9973× | 5.46× | 40 of 1660 |
| `data_phifull` | Collins | 1.0630× | 0.9973× | 3.27× | 32 of 1660 |
| `data_phi4seg24deg_phifullbin` | Sivers | 1.1282× | 0.9955× | 239.7× | 18 of 1660 |
| `data_phi4seg24deg_phifullbin` | Collins | 1.2087× | 0.9977× | 224.7× | 6 of 1660 |
| `data_phi4seg24deg_countbin800` | Sivers | 1.0724× | 0.9976× | 4.59× | 15 of 806 |
| `data_phi4seg24deg_countbin800` | Collins | 1.1119× | 0.9978× | 2.84× | 6 of 806 |
| `data_phi4seg24deg` | Sivers | 1.0485× | 0.9958× | 2.65× | 4 of 169 |
| `data_phi4seg24deg` | Collins | 1.0420× | 0.9991× | 2.55× | 1 of 169 |

**The best bins sit on the floor to within half a percent**, which is the check that
the expression above is the right floor for this estimator rather than a convenient
reference. It is not a hard bound: 122 bins of ~4500 fall below it, by at most
**0.45%** (global minimum 0.9955). That is the expected size of the mismatch between
the row-norm `MUT3` estimator and an idealised counting asymmetry, not a violation.

*(Corrected 2026-09-14. An earlier revision of this file quoted the minimum as
"exactly 1.00 in all eight cases — no bin falls below the floor". That came from
reading the ratio at two decimals, where 0.9973 prints as 1.00, and overstated the
claim into a bound the data does not support.)*

Three things the table says:

1. **The extraction is cheap in a typical bin.** The median excess is 4-21%: that
   is what fitting *three* amplitudes out of one 4D bin through the `MUT3` moment
   matrix costs over counting one asymmetry. Almost all of the distance between a
   raw $\sqrt{2/N_{acc}}$ and $\delta_{stat}$ is the $1/(f_n P_{^3\!He} P_n)\approx 7\times$
   dilution, not the extraction.
2. **The $\phi$ cut lives in the tail, not the median.** `_phifullbin` reaches
   **240×** the floor while its median is 1.13×. Restricting the azimuth does not
   uniformly inflate the statistical error; it ruins a minority of bins where the
   moment matrix becomes ill-conditioned, and leaves the rest near the floor.
   Compare `data_phi4seg24deg`, the same acceptance re-binned to 169 of its own
   bins, whose worst bin is 2.65× — coarser bins keep every cell conditioned.
3. **The floor is what more beam time moves.** $N_{acc}$ is the only quantity in
   it, so the dashed line falls as $1/\sqrt{N}$ exactly while the systematics do
   not — the same asymmetry the `--counts` study measures on the fitted bands.

On `errors-ratio` the same quantity appears as floor/$\delta_{stat}$, near 0.9 on
every panel, dipping where a bin is starved.

Pretzelosity is deliberately absent: `tmd.AUTPretzelosity` is still a placeholder
whose normalisation is not established (`../../code.md` step 5), so plotting its
error budget beside two fitted observables would invite a comparison it cannot
support.

Axes are shared across every panel of a figure and derived from the data, rounded
outward to whole decades, with extra empty decades at the bottom reserved for the
legends. Nothing is clipped — which matters here, because the $\phi$-cut
statistical error reaches **822** in the worst starved bins and the Sivers
relative term dips to $10^{-8}$ where the asymmetry crosses zero.

## The pairing rule

**Only rundirs with the same bin count can be compared row by row.** A
`_phifullbin` run inherits `data_phifull`'s 1660 bins and pairs 1:1 with it; an
own-bins run re-bins under its own acceptance and shares no bin with anything.
Column titles carry the bin count so a mismatch is visible on the figure, and
`errors-ratio-phi` refuses to plot a ratio unless two rundirs match, naming the
pair it used.

## What it currently shows

| rundir | bins | amplitude | stat | systabs | $\lvert A_{UT}\rvert$systrel | statistical share of $error\_tot^2$ |
|---|---|---|---|---|---|---|
| `data_phifull` | 1660 | Sivers | 0.00369 | 0.00130 | 0.00088 | 80.4% |
| | | Collins | 0.00354 | 0.00130 | 0.00582 | **25.3%** |
| `data_phi4seg24deg_phifullbin` | 1660 | Sivers | 0.01777 | 0.00130 | 0.00077 | 98.9% |
| | | Collins | 0.01652 | 0.00130 | 0.00534 | 90.7% |
| `data_phi4seg24deg_countbin800` | 806 | Sivers | 0.00887 | 0.00119 | 0.00077 | 97.0% |
| | | Collins | 0.00893 | 0.00119 | 0.00428 | 82.1% |
| `data_phi4seg24deg` | 169 | Sivers | 0.00478 | 0.00134 | 0.00073 | 89.9% |
| | | Collins | 0.00474 | 0.00134 | 0.00515 | 38.9% |

Four things worth carrying away:

1. **At full azimuth, Collins is systematics-limited.** Its relative term exceeds
   the statistical error in 73.6% of bins, leaving only a quarter of its total
   error variance statistical. Sivers is at 17.2% of bins, Pretzelosity at none —
   the difference is simply that Collins is the largest asymmetry, and this term
   is the only one proportional to $A_{UT}$.
2. **A $\phi$ cut reverses that**, not by improving the systematics but by
   inflating the statistical term past them: Collins drops to 2.9% of bins
   systematics-dominated. Cut runs therefore look "cleaner" in the ratio figure
   precisely because they are statistically worse.
3. **The cut acts on one term only.** `errors-ratio-phi` measures
   $\delta_{stat}$ up by 3.78 (Sivers) and 4.32 (Collins) at the median, matching
   the ROOT-tree measurement in
   `../../SIDIS_MUT3_comparison/SIDIS_MUT3_comparison_other.md`;
   `systabs` flat at 1.000 ± 0.5%; the relative term at 0.94-0.96, moving only
   because the surviving events shift each bin's mean kinematics.
4. **Only `stat` responds to the binning, and it responds as $\sqrt{N_{bins}}$.**
   The three 4×24° rows have one acceptance between them, so any difference is
   binning alone. `systabs` stays 0.0012-0.0013 and $\lvert A_{UT}\rvert$systrel
   0.0043-0.0053 across a 10× change in bin count, while Collins `stat` runs
   0.00474 (169) → 0.00893 (806) → 0.01652 (1660): ratios 1.88 and 1.85 against
   $\sqrt{806/169}=2.18$ and $\sqrt{1660/806}=1.44$.

   **The consequence is that "systematics-limited" is not a property of a
   configuration.** Collins' statistical share of the same 4×24° data reads 38.9%,
   82.1% or 90.7% depending only on how it was binned. Quote a stat share only
   with the bin count attached. This is the per-bin origin of the 1/N_bins
   dilution documented in `../README.md`: the systematic per bin barely moves, so
   splitting bins buries it under a growing statistical term — and the fit, which
   treats each bin's systematic as independent, then averages it away.

## Choosing a binning: where the three terms balance

The figures exist partly to answer "how many bins?", so here is the recipe they
give, worked through for `phi4seg24deg` — the one acceptance that exists at three
binnings, so binning is the only thing that varies.

**Balance the statistical term against the two systematics combined**,
$syst\_tot = \sqrt{systabs^2 + (A_{UT}\,systrel)^2}$, and read off where
$stat/syst\_tot = 1$. Because $stat \propto \sqrt{N_{bins}}$ at fixed counts, any
one binning extrapolates to the balance point as

$$N^* = N_{bins}\left(\frac{syst\_tot}{stat}\right)^2 .$$

At **4× counts**:

| binning | bins | Collins $stat/syst$ | Sivers $stat/syst$ | Collins $N^*$ |
|---|---|---|---|---|
| `data_phi4seg24deg_phifullbin` | 1660 | 1.50 | 5.88 | 734 |
| **`data_phi4seg24deg_countbin800`** | **806** | **1.00** | 3.13 | 799 |
| `data_phi4seg24deg` | 169 | 0.45 | 1.56 | 852 |

All three extrapolations agree on ~730–850, so the number is a property of the
data rather than of whichever run it was read from. **806 bins sits on Collins'
balance point at 4× counts.**

### $N^*$ is not a property of the acceptance — it moves with luminosity

| | Collins $N^*$ | Sivers $N^*$ |
|---|---|---|
| 1× counts | 200 | 21 |
| 4× counts | 799 | 82 |

$stat \propto 1/\sqrt{counts}$, so $N^* \propto counts$: **four times the counts
buys four times the bins at the same per-bin balance.** At nominal luminosity the
same criterion would have picked ~200 bins for this acceptance. Any statement of
the form "this configuration wants N bins" is incomplete without the luminosity.

### The fit agrees, independently

The bin-count scan (`../../runlog.md`, 2026-09-07/08) found the $g_T$ curve
"descends from 169, flattens by ~800, and stays flat to 1660" — 806 matches 1660
inside the ±3.2% replica-sampling floor, while 169 is clearly worse. A per-bin
error-balance argument and a fitted band arrive at the same ~800 by different
routes.

### Two cautions

**The two amplitudes want different binnings, and Collins wins.** Sivers' $N^*$ is
82 against Collins' 799, because $A_{UT}^{Sivers}$ is small, so its
$A_{UT}\,systrel$ term is tiny and `systabs` dominates its systematic. They cannot
be binned separately — all three amplitudes come out of one `MUT3` inversion in the
same bins — so **Collins sets the binning and Sivers stays statistics-dominated**
($stat/syst = 3.1$ at 806). That is the benign direction: being statistics-limited
is exactly why Sivers is the amplitude that responds to more beam time, while
Collins is the one that does not.

**"Too many bins waste counts" is not right, and how it is wrong matters.** Total
statistical information is conserved under splitting — $\sum 1/\delta^2$ is
invariant — which is why 1660 bins fit as well as 806. The real cost of
over-binning is the **$1/N_{bins}$ dilution of the systematics**: `prepare.py`
puts them into `error_tot` per bin and the χ² sums in quadrature, so the fit treats
as independent what is in fact one common offset, and averages it away.

**Both systematic terms dilute, not just the relative one.** Neither is independent
bin to bin:

| term | per-bin value | where the per-bin variation comes from |
|---|---|---|
| `systrel` | **0.07021 on every row**, one distinct value | nowhere — it is the quadrature of five fixed relative uncertainties (3% target polarisation, 5% nuclear, 2.5% radiative, 3% diffractive meson, 0.2% random coincidence) |
| `systabs` | 0.00092–0.00294, a 3.2× spread | only $f_n$ and the beam energy: $systabs = c/(0.6 f_n 0.86)$ with $c = 1.7\times10^{-4}$ above 10 GeV, $2.57\times10^{-4}$ below (`SoLID_SIDIS_3He.h:1391-1393`) |

`systrel` is a single number repeated, so it is maximally correlated. `systabs`
looks like it varies, but its source is the same one constant per beam energy
carrying a *known, deterministic* $1/f_n$ modulation — a correlated error with a
shape, not an independent draw per bin. **Only $\delta_{stat}$ is genuinely
independent bin to bin.** So the whole systematic budget is subject to the
dilution, and the statistical shares quoted above overstate how
statistics-dominated these runs really are by more than the `systrel` term alone
would explain.

That is why stat+syst results must never be compared across different bin counts,
and why binning near $N^*$ — rather than as fine as possible — keeps the answer off
the artifact.

### `systabs` is a floor, and it is what makes Sivers want a coarser binning

The two systematics do not share the work evenly, and which one dominates depends
on the amplitude and the hadron charge. Share of $syst\_tot^2$ carried by
`systabs`, on `countbin800` at 4×:

| group | Collins | Sivers |
|---|---|---|
| 11 GeV π⁺ | 7% | 22% |
| 11 GeV π⁻ | 7% | **96%** |
| 8.8 GeV π⁺ | 16% | 42% |
| 8.8 GeV π⁻ | 14% | **100%** |

**For Collins, `systabs` is never more than 16%** — the systematic budget is
$A_{UT}\,systrel$, which tracks the amplitude. **For Sivers π⁻ it is essentially
everything**, because the model's $A_{UT}^{Sivers}(\pi^-)$ is ~0.002, so its
relative term all but vanishes and only the absolute floor is left.

That matters for binning because `systabs` is a *floor*: it does not shrink when
the amplitude does. An amplitude sitting on it has a small $syst\_tot$, so
$N^* = N(syst\_tot/stat)^2$ collapses — which is the whole reason Sivers wants
fewer bins than Collins, not any property of the acceptance.

### Binning the amplitudes and the charges separately — a direction, not a result

Because the balance point depends on $|A_{UT}|$, and $A_{UT}^{Sivers} <
A_{UT}^{Collins}$ with π⁺ and π⁻ differing again inside each, one binning cannot
suit all four. $N^*$ per group, `countbin800` at 4×:

| group | bins now | Collins $N^*$ | Sivers $N^*$ | $\lvert A_{UT}^{siv}\rvert$ | $\lvert A_{UT}^{col}\rvert$ |
|---|---|---|---|---|---|
| 11 GeV π⁺ | 375 | 335 | 104 | 0.0338 | 0.0665 |
| 11 GeV π⁻ | 262 | 224 | **17** | **0.0029** | 0.0498 |
| 8.8 GeV π⁺ | 97 | 119 | 46 | 0.0316 | 0.0625 |
| 8.8 GeV π⁻ | 72 | 90 | **13** | **0.0014** | 0.0520 |
| total | 806 | **~770** | **~180** | | |

Collins wants ~770 bins and Sivers ~180 — a factor 4. Inside Sivers the charges
split again, ~150 for π⁺ against ~30 for π⁻, because the model's Sivers π⁻ is
12–23× smaller than its π⁺. Collins shows nothing comparable (335 vs 224 at 11 GeV).

**How much of this is already possible.** The charges and beam energies are
*already* binned separately — every run carries four bin files
(`bin_enhanced_N11p/N11m/N8p/N8m.dat`, here 375/262/97/72 bins) and
`../../make_bins_from_count.py` takes `-N` per file. What is unoptimised is only
the *choice* of per-file targets, which currently keeps the control run's
proportions rather than following each group's $N^*$.

Splitting Collins from Sivers is a bigger step but needs no new code: all three
amplitudes come out of **one `MUT3` inversion per bin**
(`SoLID_SIDIS_3He.h:1122-1222`), so one binning serves all three within a run.
Doing it differently means two step-2 runs into two rundirs, fitting `fitcollins.py`
on one and `fitsivers.py` on the other. Every stage already takes a `<rundir>`. The
trap to watch: `prepare.py` writes all three amplitude columns into each
`simenhanced3he.dat`, so a Sivers-binned rundir still carries Collins columns that
would be wrong to fit — the rundir name has to carry the warning.

**The caveat that should gate this.** These $N^*$ come from the *model's* $A_{UT}$,
and Sivers π⁻ being tiny is a prediction of the current parameter set, not a
measurement. Binning on it means the optimisation is only as good as that
prediction: if the true Sivers π⁻ is larger, the one channel with signal would have
been coarse-binned. It would not bias the fitted central values — the fit refits
from world data regardless — but it would cost precision exactly where it was not
expected. That argues for splitting **Collins from Sivers first**, where the factor
4 rests on the robust ordering $A_{UT}^{Collins} > A_{UT}^{Sivers}$, and treating
the π⁺/π⁻ split inside Sivers as the more speculative half.
