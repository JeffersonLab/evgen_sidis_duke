# Verified checks

Investigations that have been done and should not be re-done — evidence,
numbers, and how to reproduce each. A finding lands here once it is settled and
needs no action; open, actionable problems live in `bug.md`, implementation
detail in `code.md`, physics in `physics.md`, run provenance in `runlog.md`.

Newest first.

---

## 2026-08-26 — what spin direction is φ_S defined against, and how does it map to lab azimuth?

**Answer: target spin along lab +x̂, transverse to the beam and fixed. And
`tan φ_lab(e⁻) = −cos(θ_q)·tan φ_S` — *not* φ_S = −φ_lab.**

`Lsidis3.h:88` declares φ_S as the Trento-convention azimuth of the transverse
target polarization. No spin vector is ever stored: `Slepton`, `SNL`, `SNT` are
zeroed in the constructor (`Lsidis3.h:174-176`) and never written, and `dsigma()`
implements only `mode == 0` ("No azimuthal modulations") returning `FUUT()`. So
the direction below is implied by the frame construction, not declared.

Both analysis headers set the beam along lab +ẑ with the target at rest, so
`Pl_2.Theta() = Pl_2.Phi() = 0` and the frame rotations at `Lsidis3.h:490-491`
are the identity — the code's internal frame is the lab. Line 494 places the
scattered lepton at azimuth 0, then rotates by `phil(φ_S)` about ẑ.

**Closure test.** Compute φ_S from the generated final state per Trento
(Bacchetta *et al.*, hep-ph/0410050 eq. 5) — about **q̂**, from the lepton plane:

```
phiS = atan2( (l x S).qhat , (qhat x l).(qhat x S) )
```

With `S = (1,0,0)` this returns the input φ_S exactly for every θ_q in
0.107–0.377 and every φ_S tested, including ±π/3 and ±2π/3. With `S = (0,1,0)`
it does not. Reconstructing φ_h the same way returns the input φ_h, which
validates the reconstruction itself and not merely the answer.

**The lab-azimuth relation, and the trap.** φ_S is defined about **q**, not the
beam; the `cos θ_q` factor at `Lsidis3.h:496-497` is that frame conversion:

```
shl = -cos(theta_q) sin(phiS) / sqrt(1 - sin^2(theta_q) sin^2(phiS))
chl =  cos(phiS)             / sqrt(1 - sin^2(theta_q) sin^2(phiS))
  =>  tan(phi_lab) = -cos(theta_q) tan(phiS)
```

which is φ_S = −φ_lab only as θ_q → 0. At θ_q = 0.377 (x = 0.55, y = 0.35),
φ_S = π/4 gives φ_lab = −0.7490 against −0.7854 — 0.036 rad = 2.1°.

**Do not test this at φ_S = 0, ±π/2, ±π only.** There tan φ_S is 0 or ∞ and the
sign-flip form is exact for *any* θ_q, so those points agree trivially and hide
the discrepancy. An earlier check that sampled only multiples of π/4 concluded —
wrongly — that the relation was an exact sign flip.

**Consequence for the φ-cut studies.** The sector cut acts on lab azimuth
(`InPhiSector` → `p.Phi()`), with centres at φ_lab = 0, ±90°, 180°. At exactly
those values the mapping is exact regardless of θ_q, so the surviving φ_S stripes
sit at 0, ∓90°, 180° — as observed. Only stripe *widths* distort: a sector near
φ_lab = 0 or 180° maps to a φ_S stripe wider by 1/cos θ_q (7.6% at θ_q = 0.377),
one near ±90° narrower by cos θ_q.

---

## 2026-08-26 — is `hs_full` symmetric in ±φ_S, and does folding onto |φ_S| matter?

**Question.** `AnalyzeEstatUT3` builds MUT3 from `hs`, which is filled at
`|φ_S|`, so it evaluates `sin(φ_h − |φ_S|)` rather than `sin(φ_h − φ_S)`. That is
lossless only if the distribution is symmetric under φ_S → −φ_S at fixed φ_h.
Now testable directly, since both maps are saved per bin.

**Answer: `phifull` is symmetric, the φ-cut run is not — but folding changes the
projected errors by ≤2% either way.**

All 782 `enhancedN11p` bins, median of Σ|H−H′| / Σ(H+H′) over the 36×36 map:

| reflection | `SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg` | `data_phi4seg24deg_phifullbin` |
|---|---|---|
| (φ_h, φ_S) → (φ_h, −φ_S) | 0.059 | **0.500** |
| (φ_h, φ_S) → (−φ_h, φ_S) | 0.059 | **0.500** |
| (φ_h, φ_S) → (−φ_h, −φ_S) | 0.059 | 0.038 |

`phifull`'s 0.059 is **noise, not asymmetry**: its φ_S projection is asymmetric by
only 0.012, and 0.012 × √36 = 0.072 ≈ the 2D figure, the scaling expected when
per-cell fluctuation is the only source.

The cut run keeps the **parity-like** symmetry (flip both, 0.038) and breaks each
single flip at 0.500 — an order of magnitude above that noise floor, so
structural. Its φ_S *marginal* stays symmetric (0.0095); the asymmetry is
entirely in the joint distribution. Expected from the geometry: the hadron's lab
azimuth differs from φ_h − φ_S by the electron's, and `InPhiSector` cuts that,
so the surviving support is **diagonal stripes** in (φ_h, φ_S) — invariant under
flipping both angles, not under flipping one.

**Impact on `Estat`.** Recomputing from `hs_full` with signed φ_S, same 2π²
normalisation and same formula (the folded reconstruction reproduces the tree to
0.00e+00, so the comparison is exact):

| | median | p5–p95 | min–max |
|---|---|---|---|
| `phifull` E₀ | 1.0000 | 0.993–1.007 | 0.982–1.078 |
| cut E₀ | 1.0011 | 0.982–1.021 | 0.110–1.248 |
| cut E₁ | 1.0012 | 0.992–1.015 | 0.113–1.235 |
| cut E₂ | 1.0016 | 0.988–1.019 | 0.050–1.241 |

**One bin of 782 moves by more than 2×**: bin 508, `Nacc = 16`, E₀ ≈ 3077 folded
vs 338 unfolded — meaningless at either value. The effect is small because
folding swaps `sin(φ_h−φ_S)` ↔ `sin(φ_h+φ_S)` on the negative half, so M₀₀ and
M₁₁ trade content while their sum is preserved and the error's Σ_b(M⁻¹_ab)²
largely cancels it.

**Consequence.** The folding is safe as it stands; switching MUT3 to `hs_full`
would be defensible but would move nothing. It is *not* the explanation for the
near-singular bins: of the 46 cut-run bins with E₀ > 0.5, folding accounts only
for 508. Checked specifically, bin 552 (the extreme case in `phicompare.md`) is
0.9991 folded vs 0.9830 unfolded, ratio 0.984 — its near-singularity is real.

Reproduce: for each bin compare `hs_full` against itself with the y-axis mirrored
(pair `iy` ↔ `37-iy` for 36 bins over [−π,π]), then rebuild MUT3 from both `hs`
and `hs_full` and apply the `Estatraw`/`Estat` formulas from
`SoLID_SIDIS_3He.h`.

---

## 2026-08-25 — error bars on the scatter-vs-N figures, and why the axis stops at N = 250

**Verdict: the error bars on all four `seedtest-*` figures are a 68% percentile
bootstrap over blocks, not the Gaussian `1/sqrt(2(nb-1))`. Using the Gaussian
form would assume the block values are normal, which is the very thing these
figures exist to test. With the bars drawn, the headline Collins `Nu` excess at
N = 50 reads 1.55 [1.05, 1.83] — real, since it excludes 1.0, but far softer than
the bare digit suggests.** Implemented in `seedtest_analyze.py` (`cv_ci`), reused
by `seedtest_paramsvsN.py`.

### What the plotted point is

For each ensemble size N the 500-replica pool is cut into `nb = 500 // N`
disjoint contiguous blocks. Each block stands in for one real N-replica run, and
`s_i` = the replica std within block `i` is the error bar such a run would quote
(before `tol`). The y-value is the coefficient of variation of those block
errors:

```
y = std(s_1 ... s_nb, ddof=1) / mean(s_1 ... s_nb)
```

Contiguous slicing is legitimate because replica `i` is seeded from `i` alone —
checked directly, `|rho_s| < 0.056` with `p > 0.2` against replica index across
all 20 varying parameters in both pools (2026-08-25 entry below).

### The uncertainty

`y` is a dispersion estimated from `nb` numbers, so how well it is known is set
by how few blocks there are. Resample the `nb` values `s_i` with replacement,
recompute `y`, 2000 times, take the 16th/84th percentiles:

```python
draw = per_block[rng.integers(0, nb, size=(nboot, nb))]
cv   = draw.std(axis=1, ddof=1) / draw.mean(axis=1)
return np.nanpercentile(cv, (16, 84))
```

Fixed seed (`BOOT_SEED = 0`), so reruns reproduce exactly. Bars are asymmetric and
clipped positive for the log axis. The same routine serves every panel: on
`np.std` per block (the error's scatter), on the IQR-based scale, and — since
2026-08-26, when the `seedtest-*` right panel was swapped to it — on the per-block
means (the central value's scatter). `cv_ci` divides by `abs(mean)` so a negative
observable such as `xh1d` does not return a negative CV.

### Three limitations, stated so they are not rediscovered

- **It propagates block-count uncertainty only.** That is the right scope: the
  block-to-block spread of `s_i` already contains both finite-N estimation noise
  and any real structure, and the bootstrap asks how well *that spread* is
  determined. It says nothing about error in the pool itself.
- **A percentile bootstrap on a CV is biased low at small `nb`.** At `nb = 5`
  (N = 100) the true interval is somewhat wider than drawn. **Treat the bars as a
  floor on the uncertainty, not a ceiling.**
- **`nb = 2` is degenerate.** Resampling two values draws the same one twice about
  half the time, so the interval collapses to `[0.00, y]`. Every N = 250 point
  does this. It is the bootstrap correctly reporting the point is worthless.

### Why the x-axis stops at 250, and what it would cost to go further

The quantity is a scatter *across* ensembles, so it needs at least two of them.
N = 500 gives one block and is not a missing point but an undefined one;
`block_table` drops it (`if nb < 2: continue`) and `BLOCK_SIZES` stops at 250.
Precision degrades well before that:

| N | blocks | rough uncertainty on the point |
|---|---|---|
| 10 | 50 | 10% |
| 20 | 25 | 14% |
| 25 | 20 | 16% |
| 50 | 10 | 24% |
| 100 | 5 | 35% |
| 250 | 2 | **71%** |
| 500 | 1 | undefined |

This is the quantitative form of the 2026-08-19 entry's "trust N <= 50". The
`N = 250` column was first shaded and labelled rather than left to be read as
data, and then **removed outright on 2026-08-26**: `BLOCK_SIZES` is now
`[10, 20, 25, 50, 100]`, so the smallest block count is 5 and the shading
self-disables. The reasoning below about why the axis cannot reach N = 500 is
unchanged — it now simply stops at 100.

Extending the axis needs a bigger pool, not a different method: matching the
N = 50 point's precision at N = 500 would take **~5000 replicas** (~8 h per
observable at current speeds). The cheaper direction is a larger pool at *smaller*
N — 1000 replicas would give a trustworthy N = 100 and a usable N = 250 for about
1.5 h each. **Neither is worth it for its own sake:** the finding these figures
carry (Collins `Nu`/`Nd`/`b` at ~1.55x, Sivers `au`/`cu` at 2.2-3.3x) is already
resolved at N = 10-50, and production runs at N = 200.

### Also on these figures

Series are dodged slightly in x so overlapping points and bars stay separable.
The offset is multiplicative because the axis is log, and its width is derived
from the tightest gap in `BLOCK_SIZES` — 20 and 25 sit only a factor 1.25 apart,
so a dodge tuned to the wide end would push those two groups into each other.
`dodge_spread()` recomputes it if `BLOCK_SIZES` changes. The `1/sqrt(2(N-1))`
reference line is not dodged.

### Reproduce

```
./seedtest_analyze.py collins ; ./seedtest_analyze.py sivers
./seedtest_paramsvsN.py collins ; ./seedtest_paramsvsN.py sivers
```

Numeric intervals: the `scatter lo/hi` and `IQR lo/hi` columns of `block_table`,
printed in each script's headline table and written to
`seedtest/{collins,sivers}_paramsvsN.csv`.

---

## 2026-08-25 — raw fit parameters against replica index: a Sivers flat direction, and a third Collins cluster

**Verdict: Collins has three separated clusters, not two — that one is solid. The
Sivers fit has a strong flat direction in `{N, b, c}` per flavour that inflates
parameter spreads, but it is NOT bimodal: the distribution along it is broad and
skewed, not separated. Neither affects an observable.** Script:
`seedtest_traces.py`, `seedtest_bimodal_sivers.py`; figures
`seedtest/seedtest-traces-{collins,sivers}.pdf/.png`; refit table
`seedtest/bimodal_refit_sivers_u.csv`.

**Correction notice.** A first version of this entry claimed "Sivers is bimodal
too — two independent 50/50 splits". That was wrong: the modality test had not
been calibrated against a unimodal null, and a PC1 sign cut through a broad
unimodal distribution produces a spurious ~50/50 "split". The corrected analysis
is below. The 2026-08-19 statement that Sivers shows no secondary mode stands.

### Method

`seedtest_analyze.py` reduces the 500-replica pools to error estimates; this plots
them unreduced — every raw fit parameter against its replica index, one panel
each, with a marginal histogram. No re-fitting.

```
./seedtest_traces.py collins       # -> seedtest/seedtest-traces-collins.pdf/.png
./seedtest_traces.py sivers
./seedtest_bimodal_sivers.py u 20  # refit test, ~13 min
```

### First, the check the plot exists for: no index dependence

Replica `i` is seeded from `i` alone, so the pool must be i.i.d. and a trace
against index must look like white noise. Across **all 20 varying parameters in
both pools**, Spearman rho with index is `|rho| < 0.056` with `p > 0.2`. The
seeding does what it claims. Each panel prints its own rho.

### Sivers: a flat direction, not a second mode

The parameters are strongly correlated within each flavour block:

```
Nd - cd  -0.966     Nu - bu  +0.959     bd - cd  +0.914
Nd - bd  -0.960     Nu - cu  +0.909     au - cu  -0.829
```

The principal component of the standardised block carries 70-85% of the variance
with near-equal loadings on `N`, `b`, `c` (~0.55 each) and little on `a`. That is
a genuine flat direction: more high-x weight from `(1 + c*x)` traded against a
faster `(1-x)^b` falloff and a smaller normalisation.

**But it is not two modes.** Testing the projection along that direction for
separation, against calibrated nulls (300 trials each, n = 500):

| | max-gap / median-gap | valley / peak |
|---|---|---|
| unimodal normal (null, 5-95%) | 8 - 16 | 0.50 - 1.00 |
| true 50/50 bimodal, 3-sigma (null) | 7 - 14 | 0.24 - 0.54 |
| skewed unimodal / lognormal (null) | 11 - 29 | 0.60 - 1.00 |
| **Sivers u** | 12.6 | **0.56** |
| **Sivers d** | 29.3 | **0.28** |
| **Collins `Nu`** | **5867** | **0.00** |

`valley/peak` near 0 means a real gap between two populations; near 1 means a
continuum. Sivers u sits inside the unimodal range. Sivers d is suggestive but
is also consistent with a skewed unimodal distribution, which is exactly what a
shallow ridge produces. Collins is off the scale of every null by two to three
orders of magnitude. **Only Collins is bimodal.**

### The refit test confirms a rugged ridge rather than two basins

Refitting 20 u-sector replicas from the opposite side of the ridge
(`seedtest_bimodal_sivers.py u 20`), compared with the Collins run in the
2026-08-20 entry:

| | Collins | Sivers u |
|---|---|---|
| would improve from the other start ("stuck") | 0/20 | **2/20** |
| genuinely prefer their own side | 3/20 | 12/20 |
| tie | 17/20 | 6/20 |
| median \|delta chi2\| on chi2 ~ 1650 | **0.019** | **0.334** |

Collins is a genuinely flat valley — 85% ties at 1e-5 relative. Sivers is
**17x less flat** and the refits scatter to `bu` values (1.7 to 5.2) that match
neither starting point, i.e. many shallow minima strung along the ridge rather
than two wells. The 2/20 stuck cases mean a multi-start would change a few Sivers
replicas, unlike Collins where it was ruled out.

### Why the two models differ

```
h1col     N * (1 + 0.2*sqrt(x) + c*x^0.25) * x^a (1-x)^b * P(a,b)   one (a,b,c) shared by u and d
f1Tperp1  N * (1 +              c*x      ) * x^a (1-x)^b * P(a,b)   separate (N,a,b,c) per flavour
```

Two consequences, both observed:

- **Collins' shape factor is absorbable, Sivers' is not.** `c*x^0.25` runs
  0.47 -> 0.88 over `0.05 < x < 0.6`, a factor of **1.86** — nearly constant, so
  it folds into `N` and gives the exact `corr(Nu, c) = -1.00` of the 2026-08-20
  entry. `c*x` runs 0.05 -> 0.6, a factor of **12**. Nothing to absorb, hence a
  three-way trade instead of a two-way one, and correlations of 0.91-0.97 rather
  than 1.00.
- **The flavours are independent in Sivers because the model makes them so** —
  separate parameter blocks, no shared shape. Collins shares `(a,b,c)`, which is
  why it moves as one.

### Observables are unaffected either way

Median xf1Tperp on each side of the u ridge, against the within-side replica
spread:

| x | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 |
|---|---|---|---|---|---|
| ridge-side difference | 0.1% | 0.3% | 0.2% | 1.1% | 3.1% |
| within-side replica spread | 0.6% | 0.8% | 1.7% | 4.0% | 8.0% |

The difference is smaller than the noise it sits in at every x — the same
conclusion the 2026-08-20 entry reached for Collins via g_T (0.1%).

### What to do with this

- **Nothing downstream changes.** No observable moves.
- **The standing "compare bands and g_T, never parameters" rule now has a Sivers
  justification too** — a flat direction rather than a second mode, but the same
  consequence for parameter tables.
- **Do not quote `bu`, `cu`, `bd`, `cd` errors.** Their spread is the ridge. This
  is what the 2026-08-19 entry recorded as `au` 0.223 / `cu` 0.238 "~2x the
  Gaussian expectation" and left unexplained.
- **Do not describe Sivers as bimodal.** It is not, by the calibrated test above.
- **Not investigated:** whether reparameterising `(1 + c*x)` as `S(x)/S(x0)`
  would tighten the Sivers ridge the way option 1 of the 2026-08-20 entry would
  for Collins. The ridge is not a separated-mode problem, so the payoff is
  smaller.

---

## 2026-08-24 — column-semantics audit of the C++ → Python boundary

**Verdict: one defect (the `stat` column carries the Collins error into the
Sivers fits — `bug.md` item 9), one documented approximation (`h±` world data
modelled with pion FFs), two naming traps. The other fifteen columns mean on the
Python side exactly what the C++ side wrote.**

**Why this audit exists.** Every check run on this pipeline before today was of a
kind that a wrong-but-plausible number passes: byte-for-byte reproducibility,
finite-value scans, row counts, NaN filtering, output-directory provenance. None
of them asks whether a column *means* the same thing on both sides of a stage
boundary. `bug.md` item 9 is what that gap was hiding.

### The columns of `enhancedNpi{p,m}.csv`

Written by `CreateFileSivers()` (`SoLID_SIDIS_3He.h:968`), read by `prepare.py`,
consumed by `fit{collins,sivers}.py` → `tmdlib/tmd.py`.

| column | written as | consumed as | verdict |
|---|---|---|---|
| `i` | per-file row index | dropped (`ignore_index=True` on concat, `reset_index` after the NaN filter) | ok — unique within a file, duplicated across π⁺/π⁻, and nothing depends on it |
| `Ebeam` | 11.0 or 8.8 | never read by a fit | ok — the model depends only on kinematics, so merging the two energies is correct |
| `x` | `Nacc`-weighted bin mean | `tmd` Bjorken x | ok |
| `y` | `Nacc`-weighted bin mean | depolarisation factor in `AUTCollins` | ok — matches `Q²/(x·2ME)` to 0.1% median over 986 bins, i.e. it is the standard inelasticity |
| `z` | `Nacc`-weighted bin mean | `tmd` z | ok |
| `Q2` | `Nacc`-weighted bin mean | `tmd` Q² | ok |
| `pT` | `Nacc`-weighted mean of `Lsidis` `Pt` | `exp(-pT²/⟨P_T²⟩)` in `FUUT` | ok — both are the hadron transverse momentum P_hT, same convention as `⟨P_T²⟩ = ⟨p_⊥²⟩ + z²⟨k_T²⟩` |
| `obs` | constant `AUT` | never read | ok |
| `value` | hardcoded `0.0` | overwritten by `prepare.py`, recomputed again in `simulate()` | ok — documented in `code.md` step 4 |
| `stat` | **`E1stat`** | `error` for *both* observables | **DEFECT — `bug.md` item 9.** `E1stat` is the sin(φ_h+φ_S) error, i.e. Collins. Sivers gets the wrong modulation's error |
| `systrel` | 7.0% in quadrature | `A²·systrel²` in the error sum | ok — relative, and applied to the asymmetry as intended |
| `systabs` | `1.7e-4/(0.6·f_n·0.86)` (11 GeV) | added in quadrature | ok — the `f_n` implied by inverting this column reproduces the tree's `fn` branch exactly (min 0.1280, median 0.2404, max 0.3056), so `systabs` and `stat` share one normalisation |
| `target` | constant `neutron` | `f1col(target)` | ok — the C++ generates ³He but divides the error by `f_n·P_³He·P_n`, so the quantity *is* the neutron asymmetry |
| `hadron` | `pi+` / `pi-` | `D1col(hadron)` | ok |
| `Experiment` | constant `solid` | never read | ok |
| `Nacc` | accepted yield | diagnostics only (`make_phicut_viz.py`), never a fit | ok — added 2026-08-17, absent from older files |

### The world files

Routing is correct, and the naming actively works against you:

| file | `obs` | rows | read by |
|---|---|---|---|
| `data_world/colworld_collins.dat` | `AUTcollins` ×146 | 146 | `fitcollins.py` |
| `data_world/colworld_sivers.dat` | `AUTsivers` ×234 | 234 | `fitsivers.py` |

**Trap:** the Sivers world file is also called `colworld.dat`. Both are read with
the right script; only a human reading a path is misled.

**One approximation worth knowing:** `data_world/colworld_sivers.dat` contains `h+`/`h-` rows
(COMPASS unidentified hadrons) and `neutron` target rows alongside proton and
deuteron. `tmd.D1col` and `tmd.H1col` map `h±` onto the **pion** tables, so an
inclusive-hadron measurement is modelled as pure pions. It does not crash and it
is a common simplification, but it is an assumption, not an identity.

### Reproduction

```python
import pandas as pd, numpy as np
d = pd.read_csv('Projections_phifull/enhancedNpip.csv')
print((d['y'] / (d['Q2'] / (d['x'] * 2 * 0.938272 * d['Ebeam']))).median())   # -> 1.00101
c = np.where(d['Ebeam'] > 10, 1.7e-4, 2.57e-4)
print((c / (d['systabs'] * 0.6 * 0.86)).describe())                          # -> the fn branch
```

The `stat` finding is reproduced by chaining `<run>/enhancedN*.root` and
comparing the `E0stat`/`E1stat`/`E2stat` branches — numbers in `bug.md` item 9.

### The generalisable rule

For every column crossing a stage boundary, name the quantity on both sides and
confirm they are the *same* quantity — not merely the same dtype and row count.
Sixteen columns cross this one; before today the semantics of exactly two
(`value`, `Nacc`) had been established.

---

## 2026-08-24 — the asymmetry model against its cited papers: right equations, wrong citation

**Verdict: every equation in `tmdlib/tmd.py` checks out, but the model is the
Torino (Anselmino et al.) Gaussian framework, not KPSY15 as `physics.md` claimed.
KPSY15 has no Sivers fit at all. Two shape factors in the code come from no
published fit. `physics.md` Step 5 corrected accordingly; no code changed.**

Sources read in full (HTML route, ar5iv — math recovered from MathML `alttext`,
so equations were compared verbatim, not from figures):

| paper | arXiv | role |
|---|---|---|
| Bacchetta, Diehl, Goeke, Metz, Mulders, Schlegel, JHEP 02 (2007) 093 | hep-ph/0611265 | structure-function decomposition |
| Anselmino, Boglione, D'Alesio, Melis, Murgia, Prokudin, PRD 87 (2013) 094019 | 1303.3822 | **the actual Collins/transversity model** |
| Anselmino et al., DIS 2011 proceedings | 1107.4446 | **the actual Sivers x-shape** (same form as the earlier Torino Sivers extractions) |
| Kang, Prokudin, Sun, Yuan (KPSY15), PRD 93 (2016) 014009 | 1505.05589 | *not* the implemented model |
| Ye, Sato, Allada, Liu et al., PLB 767 (2017) 91 | 1609.02449 | SoLID projection; Table 3 is the `tol` reference |

### What is verified correct

- **Collins depolarisation.** Bacchetta's cross section carries
  `+ ε sin(φh+φS) F_UT^{sin(φh+φS)}`, and
  `ε = (1−y−¼γ²y²)/(1−y+½y²+¼γ²y²)`, `γ = 2Mx/Q` — exactly `AUTCollins`
  (`tmd.py:160-164`). Ye et al. eq. (3) uses the same factor in its
  `γ → 0` form, `2(1−y)/(1+(1−y)²)`.
- **Sivers has no depolarisation factor.** Bacchetta's `sin(φh−φS)` term is
  `(F_UT,T + ε F_UT,L)`; the leading-twist piece carries coefficient 1.
- **Isospin and favoured/unfavoured assignment** match Ye et al. eqs. (4)–(7).
- **The Collins prefactor reproduces arXiv:1303.3822 eq. (14) exactly.**
  Composing `H1col` with `FUTCollins` gives
  `√(2e)·P_T·M_h³⟨p⊥²⟩/(M_h²+⟨p⊥²⟩)²`, identical to their
  `(P_T/M_h)·√(2e)·⟨p⊥²⟩_C²/⟨p⊥²⟩`; the `M_π = 0.14` cancels between the two
  functions, and `⟨p⊥²⟩_C = M_h²⟨p⊥²⟩/(M_h²+⟨p⊥²⟩)`,
  `⟨P_T²⟩ = ⟨p⊥²⟩ + z²⟨k_T²⟩` are their eq. (15).
- **Parameter counts.** Sivers floats 9 in `fitsim`, 7 in `fitworld`
  (`fitsivers.py:106,180`) — as documented.

### Where every constant actually comes from — arXiv:1303.3822, Table 3

That paper's *polynomial* Collins fit (its eq. 32, fitted to SIDIS + Belle `A_0`):

| `tmd.py` | paper |
|---|---|
| `c=-2.36, d=2.12`, `((1-c-d)+c z+d z²)·z` | eq. (32) `N^C_q(z) = N_q z[(1−a−b)+az+bz²]`, a = −2.36, b = 2.12 |
| `Nfav=1.0, Ndis=-1.0` | Table 3, `N_fav^C = 1.00`, `N_dis^C = −1.00` (at the \|N^C\| ≤ 1 bound) |
| `Mh = 0.67**0.5` | Table 3, `M_h² = 0.67` GeV² |
| `kt2=0.25, pt2=0.20` | eq. (8), from Anselmino et al. 2005 unpolarised SIDIS |
| `h(p⊥) = √(2e)(p⊥/M_h)exp(−p⊥²/M_h²)` | eq. (13) |
| Sivers `N_q x^{a_q}(1−x)^{b_q}·norm·f₁`, constant `Nub/Ndb` | 1107.4446, `N_q(x)` |

`par0` (`prepare.py:76`) is close to that paper's transversity numbers
(`N_u^T = 0.36`, `α = 1.06`, `β = 3.66` vs `Nu=0.4, a=1.0, b=3.0`), but not
identical — the code's `h1col` multiplies `f₁` where they use `½(f₁+g₁)`, so the
normalisations are not directly comparable.

### Why KPSY15 is the wrong citation

- Different framework: CSS/TMD evolution in `b`-space with a collinear twist-3
  `Ĥ^(3)(z) = N^c z^α(1−z)^β D(z)`, not a Gaussian model.
- Transversity `N_q x^{a_q}(1−x)^{b_q}·norm·½(f₁+g₁)` with **flavour-dependent**
  `a_q, b_q` (`b_u = 0.05` vs `b_d = 7.00`), where the code shares `a,b` between
  `u` and `d` and uses `f₁` alone.
- **No Sivers fit exists in KPSY15** — "the Sivers asymmetries in SIDIS. We plan
  to carry out this analysis in a future publication."

### Two factors with no published source

`(1 + 0.2√x + c x^{1/4})` in `h1col` and `(1 + c_q x)` in `f1Tperp1`. Both are
local shape freedom, both are zero in the injected truth (`c = 0`,
`cu = cd = 0`), and both are floated only in `fitsim`. The Collins one is the
degeneracy behind the bimodality (entry of 2026-08-20). Using `f₁` instead of
`½(f₁+g₁)` also drops the automatic Soffer safety both cited fits have
(`bug.md` item 5).

### Numerical consequence: the injected truth is not KPSY15's

`par0` at `Q² = 2.4` GeV² vs Ye et al. Table 3 (same scale, same `x` window):

| | `par0` | KPSY15 |
|---|---|---|
| `δu^[0.05,0.6]` | 0.466 | 0.349 ± 0.122 |
| `δd^[0.05,0.6]` | −0.299 | −0.200 ± 0.073 |
| `g_T` truncated | **0.765** | **0.55 ± 0.14** |
| `g_T` full | 0.923 | 0.64 ± 0.15 |

39–44% above KPSY15's central values, ~1.5σ of their own uncertainty. Harmless
for a closure test and for error *ratios*, but it means the `tol` calibration
compares a Torino-normalised model against KPSY15-normalised errors, and no
central value here is a tensor-charge prediction.

Reproduce (with the standard env prefix):

```python
import sys; sys.path.insert(0,'.')
from tmdlib import tmd
par0 = {'Nu':0.4,'Nd':-0.45,'a':1.0,'b':3.0,'c':0.,'kt2':0.25}
print(tmd.gt(2.4, par0, 0.05, 0.6), tmd.gt(2.4, par0, 1e-5, 1.0))
```

Side note: the full-range call raises two `scipy.quad` max-subdivision warnings
and the truncated call none — already settled as cosmetic in the entry below
(converged four orders of magnitude under the quoted error). Recorded only so the
warning is not re-investigated a third time.

---

## 2026-08-20 — why the Collins fit is bimodal, and what would prevent it

**Verdict: the transversity shape factor is redundant with its own normalisation,
so the chi2 surface has a flat direction. The two "modes" are the two ends of one
flat valley, not two competing solutions. Nothing observable is affected;
reparameterising `h1col` would remove it if the parameter tables are worth
fixing.** Scripts: `seedtest_bimodal.py`, `seedtest/bimodal_refit.csv`.

> **Amended 2026-08-25 — the pool holds three separated clusters, not two.** The
> `main`/`secondary` tables below use the `Nu > 0.5` cut, which folds a third
> population at `Nu ~ 0.26` (83 replicas, and the *best* median chi2 of the
> three) into "main". The flat-valley conclusion is unchanged — it is one
> degenerate direction sampled at three places. Detail in the 2026-08-19 entry
> below and the 2026-08-25 entry at the top.

### The degeneracy

`h1col` carries `N * (1 + 0.2*sqrt(x) + c*x^0.25)`. Over the measured window
`x^0.25` runs 0.47 (x=0.05) to 0.88 (x=0.6) — less than a factor of two — so
`c*x^0.25` is nearly constant there and is almost perfectly absorbable into `N`.
Within the main mode of the 500-replica pool:

```
corr(Nu, c) = -1.00     corr(Nu, Nd) = -1.00     corr(Nu, a) = +0.90
```

A correlation of exactly -1.00 between `Nu` and `c` is the degeneracy stated
numerically.

### The two ends give the same physics

| | Nu | Nd | a | b | c |
|---|---|---|---|---|---|
| main (412/500) | 0.399 | -0.450 | 0.997 | 3.011 | 0.001 |
| secondary (88/500) | 0.744 | -0.836 | 1.115 | 2.826 | -0.710 |

| x | 0.02 | 0.05 | 0.2 | 0.4 | 0.6 | 0.8 |
|---|---|---|---|---|---|---|
| xh1u secondary / main | 0.962 | 0.989 | **1.000** | 1.012 | 1.053 | 1.162 |

Truncated gT(u-d) differs by **0.1%** (0.7655 vs 0.7661). The two descriptions are
indistinguishable where there is data and diverge only outside it — a textbook
under-constrained extrapolation, not a physics ambiguity.

### It is one valley, not two basins

Replica noise is reproducible (seed = replica index), so any pool replica can be
refitted from a different start. Refitting 20 secondary-mode replicas from the
main-mode centroid:

- **0 of 20** found a lower chi2 from the main-mode start — the minimizer is not
  getting stuck, so a multi-start fit would not remove the mode;
- 17 of 20 tie, median |delta chi2| = **0.019 on chi2 ~ 1650** (1e-5 relative);
- in **19 of 20 the fit slid back to the secondary** (Nu 0.66-0.90) despite
  starting at the main mode, i.e. the main-mode point is not even a local minimum
  for those replicas.

Which end a replica lands at is decided by its noise draw, not by the optimizer.

### The natural experiment: fixing `c` removes it

`fitworld()` holds `c` fixed at 0 and its ensemble is unimodal — Nu spans just
0.379-0.438, 0 of 50 in any second mode. Every `fitsim` run floats `c`, and every
one is bimodal:

| run | secondary/50 | | run | secondary/50 |
|---|---|---|---|---|
| `phifull` stat | 4 | | `phi4seg` stat | 10 |
| `phifull` syst | 7 | | `phi4seg` syst | 11 |
| `phi6seg` stat | 6 | | `phi2segFA` stat | 11 |
| `phi6seg` syst | 14 | | `phi2segFA` syst | 11 |

8-28% across fourteen production files — universal, and independent of the
azimuthal configuration.

### Options, if it is worth fixing

1. **Reparameterise** the shape factor as `S(x)/S(x0)` with `x0` inside the
   measured range. `N` then means "the value at x0" and `c` only controls
   curvature; the flat direction is a coordinate artefact and this removes it
   while keeping the model's freedom. The recommended fix.
2. **Fix `c = 0`**, as the world fit does. Certain to work, but it changes what is
   being projected — floating `c` is what lets the SoLID pseudodata constrain that
   shape freedom.
3. **Limits on `c`** — crude; clips one arm of a flat valley rather than removing
   it. (Sivers-style limits do *not* help: every secondary replica already sits
   well inside them.)
4. **Multi-start minimization** — ruled out by the refit test above.

**But weigh the cost.** The bimodality affects no published observable: bands and
gT are identical between the two ends to 0.1-1%, and the measured scatter of the
gT error sits on the plain-statistics prediction. What it does is inflate
*parameter* spreads (~1.55x expectation for Nu, Nd, b) and make parameter-level
run-to-run comparisons noisy — which the standing rule already tells you not to
make. Any change to `h1col` also invalidates every existing output for
comparison. So this is a cosmetic fix for parameter tables, not a correctness fix.

---

## 2026-08-20 — `lru_cache` in `tmd.py`: changes nothing, worth 5.7x, kept

**Verdict: the cache is correctness-neutral and a 5.7x speedup on the fit path.
It stays.** It was briefly removed and then restored the same day; the removal
rested on a measurement that turned out to be invalid — see the trap below,
which is the most reusable part of this entry.

### Correctness — byte-identical

With the cache genuinely absent from `tmdlib/tmd.py`,
`./fitcollins.py enhanced3he datacollins_phifull` reproduced
`outputcollins_phifull/out-enhanced3he.dat` **byte for byte**
(md5 `870ea6f650c863abb5cff57d65991111`). So nothing mutates a cached dict, and
every result produced with the cache in place stands. The same conclusion follows
independently from `oldserial_run/eqtest/`, where the uncached old `tmdlib` and
the cached current one give identical replicas.

### Speed — 5.7x on the fit, 1.2-1.3x in the notebooks

Same command, same input, same seeds:

| | wall | CPU |
|---|---|---|
| cached | 2m30s | 528s |
| uncached | **14m17s** | 3026s |

The notebook paths gain much less — 1.2x for an `h1calc`-equivalent loop
(200 x-points x 50 replicas) and 1.3x for `gtcalc` over 10 replicas — because
there the per-call arithmetic in `h1col`, not the LHAPDF lookup, dominates. The
fit is the opposite: each `migrad()` re-evaluates the same data rows thousands of
times, which is exactly what the cache collapses.

(The `~2.1x` recorded in `runlog.md` when the cache landed was measured before
the `.values` hoisting and the replica parallelism. Those changed the balance,
but upward, not downward.)

### The trap that produced a wrong answer first

The first attempt built an uncached copy of `tmdlib` in a scratch directory and
ran the live `fitcollins.py` there **through a symlink**:

```
seedtest/cachetest/nocache/fitcollins.py -> ../../../fitcollins.py
seedtest/cachetest/nocache/tmdlib/                 # uncached copy
```

**Python resolves a cross-directory symlinked script and sets `sys.path[0]` to
the *target's* directory.** So `import tmdlib.tmd` loaded the project's cached
module, not the local uncached one: both arms of the A/B test ran the same code.
The result — byte-identical output, 1.0x speedup — was true but vacuous, and the
1.0x figure briefly made it into `code.md` and prompted removing the cache.

Verify the effect directly:

```
$ python3 probe_cross.py        # a symlink in ./ pointing at ../../../probe_root.py
sys.path[0] = /.../sidis2020_zwzhao          # NOT the directory the symlink is in
```

Note a same-directory symlink does *not* show this: `sys.path[0]` is then the
same path either way, which is why a first check of the mechanism looked fine.
**For any A/B test of an imported module, print `module.__file__` from inside the
run that is being measured** — not from a separate `python3 -c` alongside it.

---

## 2026-08-20 — chasing the `serial` vs `current` d-quark gap: a stale file, then a tail draw

The comparefit notebook's stat+syst panels showed `serial` and `current`
disagreeing by ~40% on the d-quark band error at x = 0.1-0.3. Two separate causes,
one real bug and one piece of bad luck.

### Cause 1 — the file labelled `current` was not made by the current code

`outputcollins_phifull/out-enhanced3hesyst.dat` was dated 2026-08-17 01:56 and sat
next to `out-enhanced3hesyst_progress.dat` **with the same timestamp**. That
progress file only ever existed in the pre-parallel serial code — it was removed
when the parallelisation landed later that day. So the notebook's `current` was a
serial-era, unseeded run masquerading as a current-code result. Confirmed by
comparing against pool block 0 (seeds 0-49, same input, same code): not equal.

This also corrects an over-generalisation: the byte-reproducibility check run on
2026-08-19 covered the **stat** file only. It passed there and I extended the
claim to the syst file, which had never been tested.

**Fixed** 2026-08-20: regenerated with the current code (3m10s), and the new file
equals pool block 0 exactly — which incidentally verifies the per-replica seeding
on the syst input for the first time. Old file kept out of the tree; the
`*_progress.dat` companions remain as the marker of which runs were serial-era.

**Audit of every other output file: clean.** All `phi*seg*` results are dated
2026-08-17 16:48 or later, i.e. after parallelisation; the only two serial-era
production files were the pair in `outputcollins_phifull`, both now superseded.

Effect: `current`'s stat+syst gT error moved 0.0255 -> 0.0200, improvement over
world 6.49x -> 8.29x, and its rank among the pool ensembles 70th -> 49th
percentile. **`phicompare_old.md`'s stat+syst `phifull` row changes with it.**

### Cause 2 — `serial` really is a narrow draw, and the old RNG structure is not why

With the stale file gone, a gap remained: measured against the converged
500-replica value, `current` sits at 0.99-1.09 (i.e. right on it) while `serial`
is 0.71-0.87, so **`serial`'s d-quark error is 13-29% too small** — the apparent
disagreement was one run being over-optimistic, not two runs differing.

The only structural difference left between old and new code is how replica noise
is drawn: the old script pulled all 50 replicas from one sequential stream, the
new one seeds each replica from its index. `seedtest_emulate.py` reproduces the
old draw structure at current-code speed (noise generated sequentially in the
parent, fits farmed to workers — the result depends only on the noise vector) and
ran ten such ensembles in 34m04s.

| x | emulated median (10) | pool median (10) | emu/pool | `serial` | serial/pool |
|---|---|---|---|---|---|
| 0.1 | 0.000648 | 0.000669 | 0.97 | 0.000574 | 0.86 |
| 0.2 | 0.000840 | 0.000812 | 1.04 | 0.000662 | 0.82 |
| 0.3 | 0.000849 | 0.000761 | 1.12 | 0.000578 | 0.76 |
| 0.4 | 0.000742 | 0.000726 | 1.02 | 0.000572 | 0.79 |

**The emulation was verified against the real thing first.** Pinning the old
code's stream with `random.seed(1000)` and running two replicas through the
pristine `../sidis2020` code path (uncached `tmdlib`, `.loc` fitfunc, its own
Minuit call) gives output **byte-identical** to the same two replicas produced by
the emulation. Replica 0 lands in the secondary minimum and replica 1 in the main
one, so both branches are covered. Scripts, outputs and reproduction steps:
`oldserial_run/eqtest/`. Side benefit: this re-confirms that the `lru_cache` and
`.values` optimisations are bit-exact, now on the stat+syst input too.

**The draw structure is exonerated** — sequential-stream ensembles land on the
pool median, not below it. Against all twenty reference ensembles (10 pool + 10
emulated), `serial` is narrower than 18, 19, 20 and 20 of them at
x = 0.1, 0.2, 0.3, 0.4. Since the x points are correlated this is one event, not
four: a draw below all twenty happens about 1 time in 21, so ~5%. Unusual, and
nothing more.

Secondary-mode counts settle a related red herring: emulated ensembles gave
3, 4, 8, 9, 9, 10, 10, 10, 11, 13 out of 50, so `serial`'s 12 is entirely
ordinary and the "12 vs 5" framing carried no information.

### The converged answer, and the notebook's two reference pools

`plot-transversity_comparefit.ipynb` now carries **both** 500-replica pools as
runs, so any 50-replica result can be read against a converged one:

| run | draws | truncated gT(u-d) | improvement over world |
|---|---|---|---|
| `pool500` stat | one seed per replica | 0.7651 +- 0.0130 | **12.72x** |
| `pool500` stat+syst | one seed per replica | 0.7652 +- 0.0208 | **7.96x** |
| `pool500seq` stat+syst | one sequential stream per 50 (old scheme) | 0.7651 +- 0.0219 | 7.57x |

The two stat+syst pools agree to 5% on the error and give secondary-mode
fractions of 17.6% and 17.4% — the same converged answer from the old and new
draw structures, which is the emulation result stated as a plot rather than a
table. In the consistency panel both pool curves sit flat at 1.0 while every
50-replica run wanders around them.

**Quote the converged numbers.** For `phifull` that is 12.72x (stat) and 7.96x
(stat+syst); the individual 50-replica runs span 10.02x-14.00x and 7.24x-8.48x.
`pool500seq` is stat+syst only — that is the variant the emulation was run on.

For scale on what a single run can do: `serial`'s d-quark error is ~25% below
both converged pools at x = 0.2-0.4, which would have overstated the d-quark
improvement by about 40% (its curve peaks near 17 against ~12 converged).

### What to take from it

- **Check provenance before interpreting a difference.** Half of this chase was a
  file that was not what its directory implied. A `*_progress.dat` companion means
  serial-era; the `NREP`/`SEED0` code path means reproducible.
- **A single 50-replica ensemble can be 25% off the converged error**, and the
  tails are real. Where a number matters, quote the converged value — 12.72x
  (stat) / 7.96x (stat+syst) for `phifull` — not one 50-replica run, and never a
  ratio between two of them.
- **Don't read a run-to-run ratio as a discrepancy.** Both `plot-transversity_comparefit.ipynb`
  panels now judge each fit against the pool distribution instead.

---

## 2026-08-19 — seed and Nrep dependence of the quoted errors (stat+syst, `_phifull`)

**Verdict: N = 50 buys a ~10% uncertainty on every quoted error bar, and that is
exactly what Gaussian statistics predicts — the bimodality does *not* inflate it
for the observables that get published.** Central values are stable to <0.1%.
Parameter-level errors in Collins are the exception, carrying ~1.5x the expected
scatter. Do not switch to a robust estimator; it is worse everywhere.

### Method

`NREP`/`SEED0` env knobs added to both fit scripts (defaults 50/0, verified to
reproduce the historical files byte for byte). One 500-replica pool per script,
stat+syst variant, `_phifull` input:

```
NREP=500 ./fitcollins.py enhanced3hesyst datacollins_phifull seedtest/collins500   # 28m52s
NREP=500 ./fitsivers.py  enhanced3hesyst datasivers_phifull  seedtest/sivers500    # 46m28s
./seedtest_analyze.py collins ; ./seedtest_analyze.py sivers
```

Because every replica is seeded from its own index, the pool partitions into
**disjoint, independent** ensembles: 10 blocks of 50, 20 of 25, 50 of 10. For
each block we recompute the quantity the plots quote — the replica standard
deviation — and measure how much that estimate scatters from block to block. All
"scatter" figures below are relative: the spread of the ten (or twenty, or fifty)
block values divided by their own average, so 0.10 means "wobbles by a tenth".
No refitting.

**Caveat on the large-N rows:** N = 100 gives 5 blocks and N = 250 gives 2, so
those scatter figures are themselves badly determined. Trust N <= 50. Quantified
2026-08-25 (entry at the top of this file): ~35% uncertainty at N = 100 and ~71%
at N = 250, and the figures now carry bootstrap error bars showing it.

### Collins: scatter of the error estimate, gT(u-d) truncated

| N | blocks | mean error | scatter of the error, measured | predicted by plain statistics `1/sqrt(2(N-1))` | scatter if IQR-based |
|---|---|---|---|---|---|
| 10 | 50 | 0.0027 | 0.236 | 0.236 | 0.384 |
| 20 | 25 | 0.0028 | 0.183 | 0.162 | 0.274 |
| 25 | 20 | 0.0028 | 0.131 | 0.144 | 0.217 |
| **50** | 10 | 0.0029 | **0.098** | **0.101** | 0.133 |
| 100 | 5 | 0.0029 | 0.079 | 0.071 | 0.070 |

Three readings:

- **gT tracks the Gaussian curve.** At the production N = 50 the quoted gT error
  is uncertain by ~10%, no worse than an unimodal fit would give.
- **The plain `np.std` is the right estimator.** The IQR-based alternative is
  1.3-1.6x *noisier* on gT and catastrophically so on parameters (scatter of
  1.5-2.2, i.e. the error estimate more than doubles between blocks, because the
  quartiles straddle the two modes). Do not switch.
- **Small-N bias:** the mean error grows 0.0027 -> 0.0030 from N = 10 to 250, so
  the N = 50 value sits ~3% low relative to the large-N limit. Minor next to the
  10% scatter, but it is a one-sided bias, not noise.

### Collins at N = 50, all observables

Plain statistics predicts a scatter of 0.101 for the error at this N.

| observable | error | scatter of the error | scatter of the central value |
|---|---|---|---|
| Nu | 0.154 | **0.157** | 0.066 |
| Nd | 0.173 | **0.157** | 0.066 |
| a | 0.053 | 0.112 | 0.009 |
| b | 0.092 | 0.154 | 0.007 |
| kt2 | 0.0023 | 0.087 | 0.001 |
| gT(u-d) | 0.0029 | 0.098 | **0.0007** |
| xh1u @ x=0.1 | 0.0011 | 0.143 | 0.0010 |
| xh1d @ x=0.1 | 0.0007 | 0.094 | 0.0006 |
| xh1u @ x=0.2 | 0.0022 | 0.136 | 0.0013 |
| xh1d @ x=0.2 | 0.0008 | 0.138 | 0.0006 |
| xh1u @ x=0.3 | 0.0021 | 0.095 | 0.0013 |
| xh1d @ x=0.3 | 0.0008 | 0.125 | 0.0006 |
| xh1u @ x=0.4 | 0.0018 | 0.083 | 0.0018 |
| xh1d @ x=0.4 | 0.0007 | 0.047 | 0.0014 |
| xh1u @ x=0.5 | 0.0016 | 0.087 | 0.0034 |
| xh1d @ x=0.5 | 0.0006 | 0.065 | 0.0032 |

Two patterns across the band:

- **The d-quark side is as steady as the u-quark side.** Its error bar is roughly
  a third the size (0.0006-0.0008 against 0.0011-0.0022), but that is d-quark
  transversity being a smaller quantity, not a better-known one — as a fraction
  of itself it is the worse determined of the two. Its wobble, 0.05-0.14, matches
  the u-quark's 0.08-0.14.
- **The wobble shrinks as x rises**: ~0.14 at x = 0.1 down to ~0.05-0.09 at
  x = 0.4-0.5, for both flavours. That is the two Collins solutions at work — they
  differ most at low x, where the `c*x^0.25` term does its compensating, and
  converge at high x. The mirror image shows in the last column: central values
  are rock steady at low x (0.0006-0.0013) and five times less so at x = 0.5
  (0.0032-0.0034), where the band is small and its relative position moves more.

Parameters `Nu`/`Nd`/`b` sit at ~1.55x what plain statistics predicts; gT and the
band points sit on it. That is the bimodality: it moves parameters
around without moving the observable, which is the same reason the standing rule
says to compare bands and gT rather than parameters.

### The Collins secondary mode, characterised on 500 replicas

88/500 = **17.6%** of replicas (per 50-replica block: 3, 5, 7, 8, 9, 10, 11, 11,
12, 12 — a binomial spread, which is why individual files looked like 8-14%).

| | Nu | Nd | a | b | c | chi2 |
|---|---|---|---|---|---|---|
| main (412) | 0.372 | -0.419 | 0.989 | 3.009 | +0.167 | 1652.4 |
| secondary (88) | 0.759 | -0.851 | 1.115 | 2.814 | **-0.720** | 1657.2 |

Delta-chi2 = 4.7 on ~1650, i.e. a genuinely competitive local minimum: a larger
`Nu` compensated by a negative `c` in the `(1 + 0.2*sqrt(x) + c*x^0.25)` shape
factor. **Minuit limits would not remove it** — every secondary-mode replica sits
well inside the limits `fitsivers.py` uses (Nu 0.60-0.96 within (-1,1), a
1.07-1.17 within (0,3), b 2.64-2.98 within (0,10)). So `bug.md` item 5 remains
worth doing as insurance, but it is not a fix for this.

**Amended 2026-08-25 — there are three clusters, not two.** Plotting `Nu` per
replica shows a third population *below* the main one that the `Nu > 0.5` cut
silently folds into "main":

| cluster | count | `Nu` median | chi2 median |
|---|---|---|---|
| low, `Nu < 0.32` | 83 (16.6%) | +0.261 | **1643.8** |
| main, 0.32-0.5 | 329 (65.8%) | +0.400 | 1655.4 |
| high, `Nu > 0.5` | 88 (17.6%) | +0.744 | 1657.8 |

The low cluster has the *best* median chi2 of the three, so "main" and
"secondary" are not ordered by quality. This is consistent with the flat-valley
picture above — it is one degenerate direction sampled at three places, not three
basins — but it means the `Nu > 0.5` classifier used in `seedtest_analyze.py` and
in the table above describes only one of the two boundaries. The scale involved:

```
std(Nu) over all 500 replicas      0.1586
std(Nu) within the main cluster    0.0030      <- a factor of 53
```

Essentially the whole quoted Collins `Nu` error is cluster separation. This is
the sharpest available statement of the standing rule that parameters must not be
quoted or compared — only bands and g_T.

### Sivers: no secondary mode — but the shape parameters are not clean

**0/500 replicas** in any secondary mode. That stands: the 2026-08-25 entry
re-tested it against calibrated unimodal nulls and Sivers shows no mode
separation, unlike Collins.

What does not stand is the original gloss that the error scatter "sits at the
Gaussian expectation across the board" — the `au` 0.223 and `cu` 0.238 entries
below do not, and the 2026-08-25 entry identifies why: a flat `{N, b, c}`
direction per flavour, along which parameters move freely without moving any
observable.

| observable | error at N=50 | scatter of the error | scatter of the central value |
|---|---|---|---|
| xf1T_u @ x=0.1 / 0.3 / 0.5 | 0.0001 / 0.0002 / 0.0001 | 0.082 / 0.112 / 0.101 | 0.001 / 0.002 / 0.016 |
| xf1T_d @ x=0.1 / 0.3 / 0.5 | 0.0002 / 0.0004 / 0.0004 | 0.072 / 0.106 / 0.109 | 0.001 / 0.003 / 0.014 |
| Nu / Nd | 0.0070 / 0.0062 | 0.108 / 0.077 | 0.024 / 0.027 |
| au / ad | 0.053 / 0.061 | **0.223** / 0.144 | 0.011 / 0.037 |
| cu / cd | 2.089 / 1.527 | **0.238** / 0.118 | — |

`Nub`/`Ndb` are held fixed, hence zero variance. The shape parameters `au`, `cu`
are the noisiest at ~2x the Gaussian expectation — **now explained**: those two
sit in the u-sector mode split, so their spread is mode separation rather than
statistical scatter. Do not quote them as errors.

### What to do with this

- **Quote a range, not a digit.** At N = 50 every error bar and every improvement
  factor carries ~10% (1 sigma) of pure replica noise. The 10.0x vs 12.4x spread
  seen between two same-input Collins fits is exactly this effect, not a
  difference between the fits.
- **N = 200 gets you to 5%**, N = 500 to ~3%. Cost at current speeds: ~2 h
  Collins, ~3 h Sivers per configuration. Worth it only for final published
  numbers, not for exploring configurations.
- **Keep `np.std`**; the robust alternative is worse.
- **A 500-replica pool per observable already exists** in `seedtest/`, so the
  converged errors are available without re-running: use them as the reference
  when a 50-replica result looks surprising.

---

## 2026-08-19 — three fits of the *same* dataset: how much do results move on replica noise alone?

**Verdict: central values are rock solid, error bars are not.** Three
`enhanced3he` fits of identical input agree on truncated gT(u-d) to within 2.5%
of the quoted error, but their *errors* differ by up to 40%, and the improvement
factor they imply spans 10.0x-14.0x (stat) and 6.5x-8.5x (stat+syst). Quote a
range, never a digit. Reproduce with `plot-transversity_comparefit.ipynb`
(~2.5 min, writes `gallary_comparefit/`).

### The three files

| key | stat | stat+syst | provenance |
|---|---|---|---|
| `ref` | `outputcollins/out-enhanced3he.dat` | `…3hesyst.dat` | byte-identical copy of `../sidis2020/outputcollins/` — the reference project's fit. Its input does not exist in this tree; cannot be regenerated here. |
| `serial` | `outputcollins_phifull/out-enhanced3he_old.dat` | `…3hesyst_old.dat` | this repo, `datacollins_phifull/`, pre-parallel unseeded code. Stat file = 2026-08-17 backup; **syst file regenerated 2026-08-19** with the pristine `../sidis2020/fitcollins.py` (2h16m) — a fresh draw, not a recovered original. |
| `current` | `outputcollins_phifull/out-enhanced3he.dat` | `…3hesyst.dat` | this repo, same input, seeded parallel code. Byte-reproducible on rerun. |

Rows are unpaired between files (`ref` and `serial` predate the per-replica
seeding), so only distributions compare. Scale for judging agreement at N = 50:
mean SE = 0.14 sigma, std uncertainty = 10.1%.

### Truncated gT(u-d), 0.05 < x < 0.6, tol = 7.04

world = 0.7664 +- 0.1658.

| variant | ref | serial | current | spread of world/this |
|---|---|---|---|---|
| stat | 0.7654 +- 0.0118 (14.00x) | 0.7650 +- 0.0166 (10.02x) | 0.7653 +- 0.0134 (12.38x) | **10.0x-14.0x** |
| stat+syst | 0.7645 +- 0.0229 (7.24x) | 0.7646 +- 0.0195 (8.48x) | 0.7650 +- 0.0255 (6.49x) | **6.5x-8.5x** |

Pairwise central shifts: 0.3%-2.5% of the quoted error. Pairwise error ratios:
0.81-1.40. Largest parameter mean shift over all pairs 0.40 sigma; smallest KS
p-value 0.006 (`kt2`, serial vs current stat+syst) — the lowest of ~30 such
tests run that day, which is about what chance delivers, and the optimisations
were separately verified bit-identical.

### Two structural findings

**The replica ensembles are bimodal.** `Nu`, `Nd` and `c` are two-peaked, not
broad: a minority of replicas converge to a second minimum near Nu ~ 0.65,
Nd ~ -0.75, c ~ 0.6. The count varies between ensembles like a binomial with
p ~ 0.1 — observed 4/50, 5/50, 7/50, 12/50 across the files here. The secondary
chi2 is **not** worse, so it is a genuine parameter degeneracy, not a failed
minimisation, and dropping those replicas moves gT by <= 0.0002 while changing
its error by <= 6%. Consequence: parameter standard deviations look large next to
their cores, and per-parameter comparisons between runs are noisy for a
structural reason — another argument for comparing bands and gT instead.

Note the relation is not monotone: the ensemble with *more* secondary replicas
(serial, 12/50) gave the *smaller* gT error. Two files cannot resolve this; it
needs the block study below.

**The systematics penalty is not a well-determined number.**
`std(stat+syst)/std(stat)` on gT gives 1.93x (`ref`), 1.91x (`current`) and
1.18x (`serial`). The first two agreeing was luck: it is a ratio of two
independently noisy standard deviations from *different* ensembles, so it carries
roughly twice the noise of either. Treat "systematics cost ~1.9x" as unproven —
say 1.2x-1.9x pending a proper study.

### What would settle it

A seed/Nrep study on `_phifull`. Because every replica is seeded from its own
index, **one 500-replica run is ten independent 50-replica ensembles** — no
re-running needed for the seed question. Design sketched 2026-08-19: partition
into disjoint blocks, measure the across-block scatter of each quoted error at
N = 10…250, and compare it against the Gaussian expectation 1/sqrt(2(N-1)) —
the excess is the bimodality's contribution. Needs a small patch to both scripts
(env-var `NREP`/`SEED0`, defaults preserving current behaviour). Cost: ~26 min
for the Collins stat pool, ~3.5 h for all four pools. `fitworld` can be skipped
if the same world file stays the comparison base — it cancels in comparisons
between SoLID configurations, though it leaves a common ~10% bias on absolute
improvement factors.

---

## 2026-08-19 — are the Python fits bit-reproducible? (both scripts: yes)

**Verdict: yes, on unchanged input, for any run made after the 2026-08-17
parallelisation.** Each replica seeds numpy from its own index
(`fitcollins.py:133-137`, `fitsivers.py:142`) and `pool.map` maps over
`range(Nrep)`, so the ensemble does not depend on which worker takes which
replica, nor on completion order. Nothing else in the fit is stochastic —
`migrad` is deterministic from a fixed start.

Checked by rerunning each fit to a scratch directory and comparing against the
file produced two days earlier, with the input untouched in between:

| script | command | wall | result |
|---|---|---|---|
| `fitcollins.py` | `./fitcollins.py enhanced3he datacollins_phifull <scratch>` | 2m36s | byte-identical, md5 `870ea6f650c863abb5cff57d65991111` |
| `fitsivers.py` | `./fitsivers.py enhanced3he datasivers_phifull <scratch>` | 6m34s | byte-identical, md5 `29cdd375f25d3cb69e145b12d9e57684` |

Both survived a fresh process, a fresh LHAPDF load and a different
worker-to-replica assignment. **Scope:** reproducibility of the *same* input;
change the `data*` directory and the numbers change, as they should. It does not
extend backwards — the pre-parallel serial code had no per-replica seeding, so
`*_old.dat` files hold independent draws and can only be compared distribution to
distribution (σ/√50 = 0.14σ on a mean, 10.1% on a standard deviation).

**Why it matters:** a changed fit output after a code edit is now real evidence
of a behaviour change rather than replica noise, so an optimisation can be
verified by `cmp` instead of by a statistical argument.

---

## 2026-08-19 — `outputcollins/` vs `outputcollins_phifull/`: same physics, different replica draws

`outputcollins/` is **not** a product of this repo. All 16 files are byte-identical
to `../sidis2020/outputcollins/` — inherited from the reference project along with
`datacollins/`, whose `simenhanced3he.dat` input does not exist here (nor in the
sibling any more), so those fits cannot be reproduced from anything in this tree.
`outputcollins_phifull/` is what `fitcollins.py` produced here from
`datacollins_phifull/`.

Only two opts overlap: `enhanced3he` and `enhanced3hesyst`, 50 replicas each in
both. The replica tables are not identical (different noise draws) but are
statistically consistent:

- Two-sample KS on each of Nu, Nd, a, b, c, kt2: p >= 0.068 in the stat-only pair
  (lowest is Nd), p >= 0.068 in the stat+syst pair (lowest kt2). No parameter
  shows a real shift; the one p = 0.049 t-test (`c`, stat-only) is what 12 tests
  produce by chance.
- The quantity the plots actually show, truncated gT(u-d) at Q2 = 2.4 with
  tol = 7.04:

  | file | `outputcollins` | `outputcollins_phifull` |
  |---|---|---|
  | `out-enhanced3he.dat` | 0.7654 +- 0.0118 | 0.7653 +- 0.0134 |
  | `out-enhanced3hesyst.dat` | 0.7645 +- 0.0229 | 0.7650 +- 0.0255 |

  Central values agree to within 2% of the quoted error. The error bars are
  11-13% wider in the new runs, which is inside the sampling uncertainty of a
  50-replica standard deviation (1/sqrt(2*49) = 10.1%) — not a real difference.

So the regenerated pipeline reproduces the reference project's Collins result.
Two practical consequences:

- `plot-transversity.ipynb` reading `outputcollins/` is not plotting wrong
  numbers, but it is plotting the *reference project's* fits, and it is the only
  source of `out-world.dat` and of the 14 opts (`base`, `sbs`, `clas`,
  `enhanced`, ...) that were never run here.
- `outputcollins_phifull/` still holds three leftovers:
  `out-enhanced3he_old.dat` and two `*_progress.dat` files from the removed
  live-convergence feature. They are not read by anything.

---

## 2026-08-18 — what does `phiscope=FA` actually widen?

**Verdict: the electron's coverage, not the event's.** Only the electron has a
large-angle acceptance in `SoLID_SIDIS_3He.h` — `GetAcceptance_e` sums `acc_FA_e`
and `acc_LA_e` (the latter for `mom > 3.5`) — while every hadron is forward-angle
only; `acc_LA_pip`/`pim`/`kp`/`km` are loaded at the top of the file and never
read. A SIDIS coincidence therefore stays gated by the hadron's
`phi_nsector` × 24° whatever the scope.

Checked by calling the header's own `InPhiSector()` from a throwaway program
(rather than reimplementing the geometry) and scanning φ at fixed (θ, p):

| case | `phiscope=all` | `phiscope=FA` |
|---|---|---|
| forward-angle kinematics | `phicut` coverage | `phicut` coverage |
| large-angle electron (θ ≳ 16°, p > 3.5) | 13.33% | **100%** |
| π⁺ at any angle | 13.33% | 13.33% |

The same program confirmed the sector geometry itself: 6 sectors → centres
0, ±60, ±120, 180 and 40.00% coverage; 4 sectors → 0, ±90, 180 and 26.67% —
both matching `nsector × 24/360` exactly, with the 6-sector case reproducing the
pre-generalisation behaviour. `phiscope=FA` with `phicut=0` is a no-op and says
so at startup.

**Consequence for results:** a 2×24° FA run is not "13.3% of an experiment" — its
electron leg is uncut at large angle, which is why its accepted-event
distribution shifts toward high x and high Q² rather than simply scaling down.
See `phicompare_old.md`.

---

## 2026-08-18 — physics conventions in `tmd.py` / the fit scripts (all correct)

From the same review that produced `bug.md`; these are the parts that checked out
and need no action.

- **Collins depolarization factor.** `epsilon = (1-y-g2*y^2/4)/(1-y+y^2/2+g2*y^2/4)`
  multiplying the numerator matches the standard
  `A_UT^sin(phi_h+phi_S) = [2(1-y)/(1+(1-y)^2)] F_UT/F_UU`, since
  `2(1-y)/(1+(1-y)^2) == (1-y)/(1-y+y^2/2)`. The code additionally keeps the
  `g2 = (2xM)^2/Q^2` mass correction, so it is more complete than the massless
  form. Ref: Bacchetta et al., JHEP 02 (2007) 093, arXiv:hep-ph/0611265.
- **Sivers correctly carries no epsilon.** In the same decomposition the
  sin(phi_h - phi_S) term has coefficient 1 while sin(phi_h + phi_S) carries
  epsilon. `AUTSivers = FUTSivers/FUUT` is right.
- **Isospin.** `f1col` neutron branch swaps u<->d correctly; the deuteron branch
  gives u = d = (u_p+d_p)/2 per nucleon, which is right for an isoscalar target;
  s/c/b are correctly left unswapped for both.
- **Normalization** `(a+b)^(a+b)/(a^a b^b)` correctly pins max[x^a (1-x)^b] = 1.
- **Tensor charge** `gt()` = integral of h1 dx, with antiquark h1 = 0, is the
  correct definition of delta-q; `u-d` is the isovector g_T.
- **Favored/disfavored Collins FF** assignment across pi+/pi- follows the
  standard isospin relations.
- **Closure test passes.** Injected truth vs 50-replica recovery on
  `datacollins_phifull`, all pulls within 0.2 sigma:

  | | Nu | Nd | a | b | c | kt2 |
  |---|---|---|---|---|---|---|
  | pull = (mean-truth)/std | +0.02 | -0.02 | +0.02 | +0.06 | +0.18 | +0.20 |

  The minimizer, the replica machinery and the multiprocessing parallelization
  are doing the right thing.

---

---

## 2026-08-18 — how is `tol` in the Jupyter notebooks determined?

**Verdict: `tol` is a fit tolerance factor in the standard published sense, and
7.04 is a calibration against published error bars — not a derived number.** The
term of art, the purpose, and the fact that it cancels in the error *ratios* the
notebooks plot are all confirmed verbatim in the source papers. Its *magnitude*
is only bounded, to roughly 4–9.5, by a dozen independent comparisons.

Values in use: `tol = 7.04` in every `plot-transversity*` notebook,
`tol = 1.5` in every `plot-sivers*` notebook.

### Sources

- **Ye et al.**, *Unveiling the nucleon tensor charge at Jefferson Lab: A study
  of the SoLID case*, Phys. Lett. B **767** (2017) 91, arXiv:1609.02449 — the
  SoLID projection paper this whole pipeline reproduces.
- **KPSY15** = Kang, Prokudin, Sun, Yuan, *Extraction of quark transversity
  distribution and Collins fragmentation functions with QCD evolution*,
  Phys. Rev. D **93** (2016) 014009, arXiv:1505.05589 — the global fit Ye et al.
  builds on.

Ye et al., text following their Eq. (18) (verified verbatim from the PDF):

> The factor of ∆χ² (commonly known as the tolerance factor) is introduced in
> order to accommodate possible tensions among the data sets. In the ideal
> Gaussian statistics, 68% CL corresponds to ∆χ² = 1. In the present analysis we
> use the value of ∆χ² = 29.7 quoted in the KPSY15 analysis. We stress however
> that our analysis focuses on the relative improvement after inclusion of the
> future SoLID data for which the tolerance factor drops out.

KPSY15 defines it, below their Eq. (117):

> where ∆χ² corresponds to the so-called fit tolerance T ≡ √∆χ²

and derives the value from their own fit: N = 249 d.o.f., ξ₉₀ = 278.0, hence
**∆χ² = 29.7 at 90% CL**, with **∆χ²₆₈ = 10.6** given alongside it.

### What this settles

1. **`tol` is the tolerance factor** — the variable name is the term of art, not
   an abbreviation of something else. Errors scale as √∆χ², so `tol` is `T`.
2. **Its purpose is tension between datasets**, not rigidity of the
   parameterization. This corrects the framing in `bug.md` item 6, which was
   speculation.
3. **It cancels in the ratio.** Ye et al.: *"while the absolute error bands can
   differ depending on the error analysis, the ratio of the errors is
   independent of the error analysis."* That is exactly the empirical behaviour
   the ratio panels in `plot-transversity_phicompare.ipynb` were built around —
   independent confirmation the notebook design matches the paper's.
4. **The two CLs matter.** √29.7 = 5.45 is the **90%** factor; the 68% one is
   √10.6 = 3.26. Every published number below is 90% CL, so a `tol` in the 5–9
   range only makes sense as a 90%-CL band — read as 1σ it is more than 2× too
   wide.

Ye et al.'s Fig. 2 and Table 3 are at Q² = 2.4 GeV², matching the notebooks' `Q2 = 2.4`.

### Quantitative test 1 — KPSY15's partial tensor charges

KPSY15 Eqs. (128)–(129) quote, at 90% CL and **Q² = 10 GeV²** (not 2.4):
δu^[0.0065,0.35] = +0.30 (+0.08/−0.12), δd^[0.0065,0.35] = −0.20 (+0.28/−0.11).
Computing the code's world fit over that exact range **at Q² = 10** to match:

| | code raw std | × 7.04 | KPSY15 published |
|---|---|---|---|
| δu | 0.0101 | 0.071 | +0.08 / −0.12 |
| δd | 0.0191 | 0.135 | +0.28 / −0.11 |

Right ballpark. At the notebooks' own Q² = 2.4 the raw stds are 0.0106 and
0.0196 (+5%, +3%) — the scale choice does not change the conclusion, but the
comparison is only apples-to-apples at Q² = 10.

This test alone does **not** pin 7.04: the required factor is 0.08/0.0101 = 7.9
from δu's inner error but 0.11/0.0191 = 5.8 from δd's, and symmetrizing both
asymmetric errors pushes it to ~10.

### Quantitative test 2 — Ye et al. Table 3 (the better test)

Ye et al. Table 3 quotes δu, δd and g_T at **Q² = 2.4, 90% CL**, over
0.05 < x < 0.6 and 0 < x < 1 — the same scale and the same two x ranges that
`gtcalc`/`gttruncate` compute — separately for KPSY15 (existing world data) and
for the SoLID projection. That gives twelve matched comparisons instead of two.
Implied tolerance = published error ÷ the code's raw (un-inflated) replica std:

| published column | code fit | δu[0.05,0.6] | δd[0.05,0.6] | g_T trunc | δu[0,1] | δd[0,1] | g_T full | mean |
|---|---|---|---|---|---|---|---|---|
| KPSY15 (world) | `outputcollins/out-world.dat` | 7.85 | 4.09 | 5.94 | 7.19 | 4.10 | 5.02 | **5.70** |
| SoLID | `outputcollins_phifull/out-enhanced3he.dat` | 7.32 | 8.26 | 9.46 | 6.29 | 4.92 | 5.76 | **7.00** |

Two things fall out:

- The **world-data half averages 5.70**, close to KPSY15's own √29.7 = 5.45 —
  i.e. the code's world fit, inflated by the published tolerance, reproduces the
  published world error bars.
- The **SoLID half averages 7.00**, i.e. 7.04 to two digits. So 7.04 looks
  calibrated against the *projected* SoLID column, not the world one.

Treat that second point as consistency, not derivation: the six SoLID values
span 4.9–9.5, so an average landing on 7.00 with N = 6 is suggestive, not
conclusive. Across all twelve the range is **4.09–9.46**, median 6.1.

### What is still not settled

- **7.04 is not uniquely determined.** Every test above gives a band, never a
  point. 5.8–10.2 from test 1, 4.1–9.5 from test 2. Consistent with a
  calibration; not derivable from one.
- **Sivers `tol = 1.5` is untested** — it would need a published Sivers
  extraction as its target, which has not been located.
- **The central values do not match**, so what was calibrated is the uncertainty
  scale, not the extraction. At Q² = 2.4 over 0.05 < x < 0.6 the code gives
  δu = +0.468, δd = −0.299, g_T = +0.766 against Ye/KPSY15's +0.349, −0.200,
  +0.55 — 34%, 50% and 39% high. The code's fit is a refit with its own
  simplified parameterization against synthetic world data (`bug.md` item 1),
  not a reproduction of KPSY15.
- **Consequence for `tol = 7.04` applied to g_T** (caveat b in the g_T entry
  below): the flat multiplier is now at least *empirically* defensible on the
  integrated quantity — tests 1 and 2 both compare integrated tensor charges,
  not pointwise bands. It remains uncalibrated for the pointwise x h₁(x) bands.

### Reproducing the checks

Read-only, from the project directory after `source setup.sh`:

- implied tolerances: for each `outputcollins*/out-*.dat`, build per-replica
  arrays with `tmd.gt(2.4, pset.loc[i], xl, xu)` for (0.05, 0.6) and (1e-5, 1.0),
  take `np.std` (no `tol`), and divide Ye et al. Table 3's δKPSY15 / δSoLID
  columns by it.
- test 1: same with `tmd.gt(10.0, pset.loc[i], 0.0065, 0.35)` on
  `outputcollins/out-world.dat`.
- source text: `pdftotext` on arXiv:1609.02449 and arXiv:1505.05589; the quotes
  above are at Eq. (18) and Eq. (117) respectively.

---

## 2026-08-18 — is the `g_T` error in `plot-transversity_phicompare.ipynb` estimated correctly?

**Verdict: yes, the estimator is sound and correctly implemented.** The caveats
below are real but none invalidates it, and the ones that matter numerically are
inherited from upstream (`tol`, frozen world data), not from `gtcalc` itself.

### The code under review

```python
def gtcalc(pset, Q2, tol, xl=None, xu=None):
    pset = pset.reset_index(drop=True)
    gu, gd, gt = [], [], []
    for i in range(len(pset)):
        tmp = tmd.gt(Q2, pset.loc[i]) if xl is None else tmd.gt(Q2, pset.loc[i], xl, xu)
        gu.append(tmp['u']); gd.append(tmp['d']); gt.append(tmp['u-d'])
    return {'u': np.mean(gu), 'Eu': np.std(gu) * tol,
            'd': np.mean(gd), 'Ed': np.std(gd) * tol,
            'u-d': np.mean(gt), 'Eu-d': np.std(gt) * tol}
```

with `tmd.gt()` doing `quad(h1col, xl, xu)` per flavour and returning `u-d`.

### What it gets right

**1. Correlations are propagated properly** — the single easiest thing to get
wrong here. `u-d` is formed *per replica* and the std taken of that, rather than
combining `Eu` and `Ed` in quadrature:

| | `phifull` | `world` |
|---|---|---|
| corr(du, dd) | **+0.371** | +0.011 |
| std(u-d) per-replica (what the code does) | 0.001903 | 0.023553 |
| sqrt(std_u^2 + std_d^2) (naive propagation) | 0.002174 | 0.023681 |
| ratio | **0.875** | 0.995 |

For `phifull` the u and d tensor charges are positively correlated, so naive
quadrature would **overstate** the error on g_T^(u-d) by 14%. The replica method
captures this automatically.

**2. The `IntegrationWarning` from `quad` is cosmetic.** The full-range integral
hits the 50-subdivision limit (the integrand has an integrable singularity as
x -> 0), but the value is converged:

```
default quad         0.54686563   reported abserr 5.4e-06
limit=400            0.54686584   abserr 8.1e-09
limit=400 + points   0.54686583   abserr 1.5e-08
spread across methods                2.0e-07
```

2e-7 against a g_T std of 1.9e-3 — four orders of magnitude below the quoted
error. Nothing to fix; the warning is noise in the log.

**3. The replica distribution is near-Gaussian**, so `mean +- std` is a fair
summary rather than hiding a skewed or bimodal spread. `phifull` truncated
g_T^(u-d): skew -0.02, excess kurtosis -0.27, range 0.7611-0.7701, no sign of
the secondary-minimum contamination seen in an earlier run. `world` is mildly
skewed (+0.28), nothing alarming.

### Caveats

**a. `ddof` inconsistency, ~1%.** `gtcalc`/`h1calc` use `np.std` (default
`ddof=0`, population std) while the parameter table in the same notebook uses
pandas `.std()` (default `ddof=1`, sample std). With N=50 that is
sqrt(50/49) = 1.0102, so the g_T and band errors are ~1% smaller than the
parameter-table errors for the same underlying spread. The only genuinely
actionable item here, and it is dwarfed by `tol`.

**b. `tol = 7.04` is applied as a flat multiplier to an integrated quantity.**
Whatever justifies inflating a pointwise band by 7.04 does not automatically
justify the same factor on the integral of h1 dx. Dominant term by far — 7x
beats a 1% ddof effect. See the `tol` entry above.

**c. The full-range g_T is 14% extrapolation.** Of the integral of h1^u from
1e-5 to 1: **13.9% comes from x < 0.05** (below any data), 85.4% from the
measured 0.05 < x < 0.6, and 0.7% from x > 0.6. So the full-range number's error
is partly driven by the assumed functional form rather than by data. The
notebook already says the truncated version is the honest comparison and uses it
for the headline — that judgment is correct, and these numbers back it.

**d. Conditional on the frozen world data** (`bug.md` item 2). Measured: with
world fluctuated, the truncated g_T error widens by only **1.06x**, versus
1.4-1.7x on individual parameters. So g_T specifically is robust to that bug —
but that is a property of this observable, not a general absolution.

**Model assumption, invisible in `gtcalc`:** `h1col` sets antiquark transversity
identically to zero, so `gt()` computes the integral of h1^q dx rather than of
(h1^q - h1^qbar) dx. Fine within the model, but the quoted g_T is the model's
tensor charge, not a fully general one.

### Reproducing the checks

All read-only, from the project directory after `source setup.sh`:

- correlation / ddof / shape: build per-replica arrays with
  `tmd.gt(2.4, pset.loc[i], 0.05, 0.6)` over `outputcollins_*/out-*.dat`, then
  compare `np.std(g)` against `np.hypot(np.std(u), np.std(d))`, and
  `np.std(g)` against `np.std(g, ddof=1)`.
- quad convergence: `quad(_u, 1e-5, 1.0)` vs the same with `limit=400` and with
  `points=[1e-4,1e-3,1e-2,0.1]`.
- extrapolation fraction: integrate `h1col` piecewise over
  (1e-5, 0.05), (0.05, 0.6), (0.6, 1.0).
