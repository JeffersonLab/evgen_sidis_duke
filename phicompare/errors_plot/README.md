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
```

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

| rundir | amplitude | median | min | max |
|---|---|---|---|---|
| `data_phifull` | Sivers | 1.07× | **1.00×** | 5.46× |
| `data_phifull` | Collins | 1.06× | **1.00×** | 3.27× |
| `data_phi4seg24deg_phifullbin` | Sivers | 1.13× | **1.00×** | 239.7× |
| `data_phi4seg24deg_phifullbin` | Collins | 1.21× | **1.00×** | 224.7× |
| `data_phi4seg24deg_countbin800` | Sivers | 1.07× | **1.00×** | 4.59× |
| `data_phi4seg24deg_countbin800` | Collins | 1.11× | **1.00×** | 2.84× |
| `data_phi4seg24deg` | Sivers | 1.05× | **1.00×** | 2.65× |
| `data_phi4seg24deg` | Collins | 1.04× | **1.00×** | 2.55× |

**The minimum is exactly 1.00 in all eight cases** — no bin falls below the floor
and the best bins sit on it. That is the check that the expression above is the
right floor for this estimator, not merely a convenient reference.

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
