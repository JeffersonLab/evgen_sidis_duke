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
./plot_errors.py                              # the three default rundirs
./plot_errors.py data_phifull --tag=-solo     # any set of rundirs
./plot_errors.py --out /tmp                   # figures elsewhere
```

Rundirs resolve against the cwd, then this directory, then `phicompare/` (this
script's parent, and where the rundirs actually live — it moved one level
below them), so it runs from anywhere. Each must contain `simenhanced3he.dat`
from `prepare.py`; the script names the missing file and the command that
would produce it rather than failing on a KeyError. Figures land beside the
script as `.png` + `.pdf`.

Defaults: `data_phifull`, `data_phi4seg24deg_phifullbin`, `data_phi4seg24deg`
— all in `../`.

## The figures

| file | shows |
|---|---|
| `errors-vs-bin` | the three terms per bin, one row per amplitude, one column per rundir |
| `errors-ratio` | each systematic over the statistical error — where systematics matter at all |
| `errors-ratio-phi` | each term, cut over full, for the one pair of rundirs that shares a binning |

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
| `data_phi4seg24deg` | 169 | Sivers | 0.00478 | 0.00134 | 0.00073 | 89.9% |
| | | Collins | 0.00474 | 0.00134 | 0.00515 | 38.9% |

Three things worth carrying away:

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
