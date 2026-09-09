# Findings from the fitcollins.py / fitsivers.py review

Reviewed 2026-08-18 (item 3 added later the same day; items 8 and 9 added
2026-08-24, item 10 on 2026-08-25).
**No physics or fit behaviour has been changed.** The only edits made so far are explanatory comments
and documentation — see "Already done" at the bottom. Every numbered item below
is still open. Each item lists the evidence, a reproduction command, the measured
impact where I could measure it, and options. Decisions are yours.

Ordered by how much they affect what the numbers *mean*, not by effort. What the
same review found to be **correct** — the depolarisation factors, isospin, the
normalisation, the tensor-charge definition, the closure test — is recorded in
`check.md`, not here.

---

## 1. The "world data" is synthetic — its central values ARE the model

**What.** `data_world/colworld_collins.dat` (146 rows) and
`data_world/colworld_sivers.dat` (234
rows) have `value` columns exactly equal to the model prediction at the
reference parameters. The error bars look like real published uncertainties
(median 0.010); the central values are not measurements.

**Evidence.**

```
max |value - AUTCollins(Nu=0.4,Nd=-0.45,a=1,b=3,c=0,kt2=0.25)| = 1.5e-16   (Collins)
max |value - AUTSivers(par1)|                                  = 6.7e-09   (Sivers)
chi2 of the world dataset at those parameters                  = 4.3e-27
```

Reproduce: evaluate `tmd.AUTCollins` row by row over `data_world/colworld_collins.dat`
with `par = {'Nu':0.4,'Nd':-0.45,'a':1.0,'b':3.0,'c':0.0,'kt2':0.25}` and diff
against the `value` column.

Both files are **byte-identical to `../sidis2020/`**, so this is inherited from
the original analysis, not introduced in this working copy.

**Why it matters.** This is a legitimate and common impact-study technique — it
removes dataset tension so the result is pure error propagation. But it changes
what several outputs mean:

- **chi2 is not a goodness-of-fit.** The ~1650 values reflect injected bootstrap
  noise only. Don't quote chi2/dof anywhere.
- **The "world" curve in the plots is not an extraction.** Only its *uncertainty*
  is meaningful. The error-ratio panels (Error^world / Error) are fine — they
  compare error bars to error bars, which is exactly what an impact study wants
  — but the world band's central value is just the input model.
- **`simulate()`'s `migrad()` is a no-op.** It starts at the truth where chi2 is
  ~1e-27 and returns the starting values unchanged (`edm = 2e-22`; a 500x larger
  initial step gives the identical result). So the "truth" injected into the
  pseudodata is the hardcoded `var0 = [0.4,-0.45,1.0,3.0,0.0,0.25]`, not a fit.

**Options.** (a) Leave as is and just describe it accurately. (b) If you ever
want real tension in the fit, substitute measured HERMES/COMPASS/JLab central
values — but that turns the study from error propagation into a real
extraction, and the `tol` calibration would need revisiting.

**Doc consequence either way:** DONE 2026-08-18 (the note now lives in
`code.md`, step 4). It used
to say `simulate()` "refits par0-equivalent against world data" and that
prepare.py's `value` "never reaches the fit" — true as dataflow, but it reads as
though something is lost. Reworded to state that nothing is lost numerically
(the two agree to 1e-16, from the identical parameter set), that the recompute
exists for consistency rather than correction, and that migrad cannot move
because world chi2 at the start is ~4e-27 (Collins) / ~1e-11 (Sivers). A comment
block above `simulate()` in both fit scripts now carries the full reasoning.

---

## 2. World data is frozen (unfluctuated) in every `fitsim` replica

**What.** `_fitworld_one()` fluctuates `worldrep`. `_fitsim_one()` fluctuates
**only** `simdatarep` — it never reassigns `worldrep`, so every replica inherits
the unfluctuated copy left behind by `simulate()`. The world contribution to
chi2 is therefore an identical fixed pull in all 50 replicas. Same in both
scripts.

**Evidence.** Only three places assign these globals:

```
fitcollins.py:67-68   _fitworld_one   worldrep = world.copy(); worldrep['value'] = normal(...)   <- fluctuated
fitcollins.py:95      simulate        worldrep = world.copy()                                    <- NOT fluctuated
fitcollins.py:119-120 _fitsim_one     simdatarep = simdata.copy(); simdatarep['value'] = normal(...)
```

(`fitsivers.py` lines 72-73 / 102 / 125-126 are the same pattern.)

Confirmed at runtime: after `simulate()`, `worldrep['value'] == world['value']`
is True, and across replicas 0 and 1 the world values do not change while the
simdata values do.

**Measured impact.** A patched copy that also fluctuates world, run on
`datacollins_phi6seg24deg` (50 replicas):

| param | as shipped | world fluctuated | ratio |
|---|---|---|---|
| Nu | +-0.1407 | +-0.2019 | **1.44x** |
| Nd | +-0.1591 | +-0.2265 | **1.42x** |
| a | +-0.0464 | +-0.0779 | **1.68x** |
| b | +-0.1137 | +-0.1189 | 1.05x |
| kt2 | +-0.0027 | +-0.0030 | 1.12x |
| gT(u-d) truncated 0.05<x<0.6 | +-0.00366 | +-0.00387 | 1.06x |

**Reading.** Per-parameter bands are optimistic by ~1.4-1.7x. The truncated
tensor charge is nearly unaffected (1.06x) because inside the measured range
SoLID dominates — so **the headline gT impact numbers are robust**, while
parameter-level errors and the xh1 bands outside SoLID coverage are tighter than
a fully consistent bootstrap would give.

**Is it a bug?** Ambiguous, and that is why I did not touch it. Freezing world
is defensible if you treat published central values as given. But it is
inconsistent with `fitworld()`, which fluctuates the same dataset — and the two
feed the same plots, where `fitworld` output is now the ratio denominator. So
the improvement factors currently divide a fluctuated-world band by a
frozen-world band.

**Fix if wanted:** three lines in `_fitsim_one()` of each script —
declare `global worldrep`, then `worldrep = world.copy()` and
`worldrep['value'] = np.random.normal(world['value'], world['error'])`.
All fits would need re-running (~35 min for the full set of 16).

---

## 3. Starved bins in the `_phifullbin` datasets (2-sector FA run worst)

**What.** A `_phifullbin` run inherits `phifull`'s complete step-1 bin list,
including bins its tighter acceptance cannot populate. The own-bins runs never
have this problem — `GenerateBinInfoFile`'s statistics threshold drops those bins
at step 1, which is exactly why `Projections_phi4seg24deg` has 169 clean rows.

**Evidence.** Bins whose projected `stat` exceeds 0.5 (>50% uncertainty on an
asymmetry), pi+ / pi-:

| run | pi+ | pi- | worst stat | min Nacc |
|---|---|---|---|---|
| `Projections_phifull` | 2 | 1 | 1.2 | 4.2e2 |
| `Projections_phi6seg24deg_phifullbin` | 4 | 1 | 1.5e2 | 1.8e1 |
| `Projections_phi4seg24deg_phifullbin` | **58** | **24** | **7.6e15** | **4.0** |
| `Projections_phi6seg24deg` (own bins) | 0 | 0 | 0.81 | 6.3e3 |
| `Projections_phi4seg24deg` (own bins) | 0 | 0 | 0.57 | 1.7e4 |
| `Projections_phi2seg24degFA_phifullbin` | **370** | **241** | 2.4e17 (+32 `-nan`) | **0** |
| `Projections_phi2seg24degFA` (own bins) | 1 | 0 | 0.79 | 3.5e4 |

The worst 4-sector bin retains **4 accepted events**. The 2-sector forward-angle
run (added 2026-08-19) is far worse: 611 of 1660 rows above 50% uncertainty, and
**32 bins with zero accepted events**, whose `stat`/`systabs` come back `-nan` —
a NaN error makes the whole chi2 NaN, so unlike merely starved bins these could
not degrade gracefully.

**Does it corrupt the fits? No.** Checked `datacollins_*/simenhanced3he.dat`:
no NaN, no inf, and no single bin dominates the chi2 (max weight share 0.6%).
A bin with a huge `error` simply contributes ~zero to chi2, so it is dead weight
rather than a poison pill.

**But it changes what the row count means.** Rows carrying <1e-6 of the total
chi2 weight:

| dataset | dead rows / 1660 |
|---|---|
| `datacollins_phifull` | 20 (1.2%) |
| `datacollins_phi6seg24deg_phifullbin` | 21 (1.3%) |
| `datacollins_phi4seg24deg_phifullbin` | **98 (5.9%)** |

So part of what I reported earlier as "the phi-cut cost" at 4 sectors is bins
being silently dropped, not merely degraded. The fitted numbers stand; the
interpretation needs this footnote.

**Related observation.** Statistical precision degrades *faster* than the
accepted rate alone predicts. Median stat ratio over healthy bins (all three runs
under 50% uncertainty): 6x24 deg gives 2.61/2.61 (pi+/pi-) against a naive
1/sqrt(rate) expectation of 2.50 (+4%), but 4x24 deg gives 4.69/4.64 against
3.75 — **25% worse than naive scaling**. `stat` is not a pure 1/sqrt(Nacc)
relation (even in `phifull`, `stat*sqrt(Nacc)` varies by 74% bin to bin); the
extra degradation is consistent with the cut reshaping the kinematics sampled
inside each bin — median `pT` per bin shifts 4.3% under the 6-sector cut and
8.2% under the 4-sector cut, up to ~50% in the worst bin.

**Status.** Partly addressed 2026-08-19: `prepare.py` now drops rows whose
`stat`/`systabs` are non-finite (the zero-`Nacc` bins), because those would make
the chi2 NaN outright. The *starved-but-finite* bins are still passed through,
so the item stays open.

**Remaining options.** (a) Leave it and cite the healthy-bin subset when quoting
the cost of a cut. (b) Also apply a `stat` cut in `prepare.py` (e.g. drop rows
with `stat > 0.5`) so the dead rows never reach the fit — changes nothing
numerically but makes the effective dataset size honest. (c) Treat the own-bins
runs as primary, accepting that they are not bin-matched to `phifull`.

Visualised in `nacc_phicut_vs_phifull.html` and
`AUTstat_phicut_vs_phifull.html`.

---

## 4. Collins fragmentation function is held completely fixed

`H1col()` hardcodes `Nfav = 1.0`, `Ndis = -1.0`, `c = -2.36`, `d = 2.12`,
`Mh^2 = 0.67`. None of them is fitted, so **no Collins-FF uncertainty propagates
into the transversity bands**. The projection assumes the Collins function is
perfectly known.

This is a real contributor to the optimism that the `tol = 7.04` inflation
factor is compensating for. If you ever want to retire the unexplained `tol`,
floating `Nfav`/`Ndis` (with the |dNn D| <= 2D positivity bound) is the
principled place to start.

Note `Nfav = 1.0` sits exactly at the positivity limit.

---

## 5. `fitcollins.py` imposes no parameter limits; no Soffer bound anywhere

`fitcollins.py` passes `limit=[None,None,None,None,None,None]` to Minuit, while
`fitsivers.py` bounds the normalizations to (-1,1) and the shape parameters to
(0,3)/(0,10). Nothing in either script enforces the Soffer bound
|h1| <= (f1+g1)/2.

In practice the fits land at |N| ~ 0.4-0.5 so nothing is violated, and the
closure test passes — but the Collins fit is unguarded, and a future dataset or
a bad replica could wander into unphysical territory without any complaint.

Cheap mitigation: mirror the sivers limits into fitcollins.

---

## 6. The transversity form is rigid (context for `tol`)

`h1col()` sets antiquark transversity identically to zero, and u and d share the
same `a`, `b`, `c` — only the normalizations `Nu`, `Nd` differ. Three effective
shape parameters for two flavours.

That rigidity is exactly the standard reason a bootstrap replica spread
understates the true uncertainty, and therefore the standard justification for a
tolerance factor. It is consistent with `tol = 7.04` being an empirical
inflation calibrated so the world band matches a published extraction — see the
`tol` entry in `check.md`.

---

## 7. Minor: Minuit initial step sizes are tiny

Both scripts pass `error=[1e-4]*N` as the initial step. Harmless in the current
setup because every fit starts at (or extremely near) the truth, but it would
under-explore on a real dataset with genuine tension. Worth revisiting only if
item 1 changes.

---

## 8. Latent: `tmd.H1col()` crashes on kaons

**What.** `H1col(z, Q2, hadron, par)` (`tmdlib/tmd.py:128`) matches only
`pi+`/`h+` and `pi-`/`h-`. There is no `else`, so a kaon argument leaves `u`,
`d`, `ub`, `db` unassigned and the function dies building its return dict:

```
UnboundLocalError: local variable 'u' referenced before assignment
```

Every other layer of the model *does* handle kaons — `D1col()` loads
`DSSFFlo` id 321 and matches `k+`/`K+`/`k-`/`K-`, and `FUUT()` passes `hadron`
straight through — so the Collins numerator is the single place a kaon channel
would fail. `f1Tperp1()`/`FUTSivers()` have no such branch and would work.

**Reproduce** (with the standard env prefix):

```python
import sys; sys.path.insert(0,'.')
from tmdlib import tmd
tmd.H1col(0.4, 2.4, 'k+', {'Nu':0.4,'Nd':-0.45,'a':1.,'b':3.,'c':0.,'kt2':0.25})
```

**Impact today: none.** Everything produced so far is π⁺/π⁻ only; the generator
writes `enhancedNpi{p,m}.csv` and nothing downstream asks for a kaon. It is
listed here because it is a crash, not a wrong number, and because the SoLID
SIDIS program does include kaon channels — the failure would appear the first
time someone extends `prepare.py` past pions, and the traceback points at an
unassigned local rather than at "kaon Collins is not implemented".

**Options.**

(a) Raise deliberately — add an `else: raise ValueError(f'H1col: unsupported
hadron {hadron}')`, mirroring the `print('Fail to match hadron!')` style already
in `D1col()`. Costs nothing, changes no result, and turns a confusing crash into
a clear one. Recommended if nothing else is done.

(b) Implement kaon Collins FFs — a physics decision, not a patch: Anselmino
*et al.* (arXiv:1303.3822) fit pions only, so a kaon favoured/unfavoured
parametrisation would have to come from somewhere else and would need its own
`M_h`. Do this only if kaon pseudodata is actually going into a fit.

Related, same function, same reason to look at it once: `H1col` accepts a `par`
argument and ignores it entirely (the Collins FF is fully fixed), and it shadows
its own polynomial coefficients `c` and `d` with flavour slots a few lines later.
Both are documented in `code.md` step 5; neither affects results.

---

## 9. The Sivers pseudodata carries the **Collins** statistical error

**What.** `AnalyzeEstatUT3()` computes three different statistical errors, one per
azimuthal modulation, by inverting the 3×3 moment matrix
(`SoLID_SIDIS_3He.h:853-874`). The row index is the modulation:

| row | modulation | branch |
|---|---|---|
| 0 | sin(φ_h − φ_S) — **Sivers** | `E0stat` |
| 1 | sin(φ_h + φ_S) — **Collins** | `E1stat` |
| 2 | sin(3φ_h − φ_S) — pretzelosity | `E2stat` |

`CreateFileSivers()` binds **`E1stat`** to the CSV's `stat` column
(`SoLID_SIDIS_3He.h:981`) — the Collins error, despite the function's name. Since
`prepare.py` reads the same `enhancedNpi{p,m}.csv` for *both* observables
(`prepare.py:33-34`), the Collins datasets are correct and **every Sivers dataset
in this repo has the wrong modulation's error bar**. `E0stat` is written to the
ROOT files and never read again.

**Evidence.** Median over all bins of both hadrons, from the `Projections_*`
ROOT files:

| run | med E0 (Sivers) | med E1 (Collins) | med E0/E1 | max E0/E1 |
|---|---|---|---|---|
| `phifull` | 0.00472 | 0.00449 | **1.049** | 1.75 |
| `phi6seg24deg_phifullbin` | 0.01289 | 0.01195 | 1.034 | 1.78 |
| `phi4seg24deg_phifullbin` | 0.02598 | 0.02687 | 1.047 | 1.91 |
| `phi4seg12degFA_phifullbin` | 0.05114 | 0.05321 | **1.183** | 14.34 |
| `phi2seg24degFA_phifullbin` | 0.38254 | 0.30795 | 1.179 | 3.92 |

**Reproduce.** `root -l -b -q` a macro that chains `<run>/enhancedN*.root` and
compares the `E0stat` and `E1stat` branches; the ratio above is `E0stat/E1stat`
over rows where both are finite and `E1stat > 0`.

**Impact.** E0 > E1 at the median in every configuration, so the Sivers stat
errors are **too small by ~3-5% at full 2π and ~18% in the narrow-azimuth runs**,
with individual bins off by up to 14×. Sivers improvement factors are optimistic
by the same amount. Two things blunt it: `tol = 1.5` for Sivers was calibrated
against published uncertainties and will have absorbed part of a uniform bias,
and the stat-only and stat+syst variants are affected equally, so their *ratio*
is unaffected. Collins — every transversity and g_T number in this repo — is
untouched.

**Options.**

(a) **Write all three errors as separate columns** (`stat_sivers`, `stat_collins`,
`stat_pretz`) and have `prepare.py` select by observable. Most informative, makes
the pretzelosity projection possible later, and the extra columns are inert for
anything that does not ask for them.

(b) **Parameterise the branch name** — `CreateFileSivers(..., const char* statbranch)`
— and call it twice per hadron, writing a Collins CSV and a Sivers CSV. Smallest
diff; costs a second set of CSVs and a `prepare.py` path to choose between them.

(c) Rename the function to what it does and leave the physics alone. Only
defensible if the Sivers projections are dropped.

**Cost of fixing.** The code change is small; the re-run is not. Step 3 →
`prepare.py sivers` → `fitsivers.py` for every configuration, and the Sivers
panels of both `*_phicompare` notebooks. The `tol = 1.5` calibration should also
be revisited, since its input errors would change.

Also present, identically, in `SoLID_SIDIS_NH3.h:800,813` — the proton path binds
`E1stat` too, so the same fix is needed there before it is ever run.

The full column-by-column audit that turned this up — and found the other fifteen
columns clean — is the 2026-08-24 entry in `check.md`.

---

## 10. `Estatraw` propagates the error as a row norm instead of a diagonal

**What.** `AnalyzeEstatUT3()` builds the moment matrix, inverts it, and then
(`SoLID_SIDIS_3He.h:871`, identically `SoLID_SIDIS_NH3.h:705`) takes

```cpp
Estatraw[i] = sqrt(2.0 * M_PI * M_PI / Nacc * (pow(MUT3(i,0),2) + pow(MUT3(i,1), 2) + pow(MUT3(i,2), 2)) * M_PI * M_PI);
```

i.e. the **sum of squares of row `i` of `M^-1`**. The least-squares error is the
**`i`-th diagonal element** of the inverse. The two coincide only when the matrix
is diagonal, and the code applies the formula precisely where it is not.

**Analytic statement.** Write the model as `A = sum_k p_k f_k` with

```
f_1 = sin(phi_h - phi_S)    f_2 = sin(phi_h + phi_S)    f_3 = sin(3 phi_h - phi_S)
```

The code's matrix is `M = 2 pi^2 <f_i f_j>`, the Gram matrix under the accepted-
event measure. Put `K = <f f^T>^-1`, so after `Invert()` the matrix holds
`M^-1 = K / (2 pi^2)`. Every power of pi then cancels and the two candidate
errors are

```
delta_code,i^2    = (1 / 2N) * sum_j K_ij^2 = (K^2)_ii / (2N)      <- as implemented
delta_correct,i^2 = K_ii / N                                        <- weighted least squares
```

so exactly

```
delta_code,i^2 / delta_correct,i^2 = (K^2)_ii / (2 K_ii)
                                   = K_ii/2  +  (1 / 2 K_ii) sum_{j != i} K_ij^2
```

Reading the two terms:

- The **correlation term** is a sum of squares, hence `>= 0` always, and grows as
  the three modulations become harder to separate. It is the code implicitly
  assuming the projections are uncorrelated — true only for an orthogonal basis.
- The **scale term** is `>= 1` whenever `<f_i^2> <= 1/2`, the generic case (it is
  exactly 1/2 under flat full coverage).
- **Equality holds iff `K = 2 * I`**: the three modulations orthogonal under the
  event measure with `<f_i^2> = 1/2`. That is exactly the ideal case of Appendix
  II of PR-10-006, where both forms reduce to `sqrt(2/N)` (its Eqs. 9 and 15).

**Confirmed for the flat case — the two forms are identical.** Worked through
explicitly, because this is the case the formula was validated against. With
`rho` flat on `[-pi,pi]^2` every cross term vanishes (`<f_i f_j>` reduces to
`<cos(...)>` of a non-zero harmonic in `phi_h` or `phi_S`) and every square
averages to 1/2, so

```
G = I/2      K = 2I      M = 2 pi^2 G = pi^2 I      M^-1 = I / pi^2
```

Substituting into the two candidate expressions, with `N = Nacc`:

```
coded:     sqrt( 2 pi^2 / N * sum_j (M^-1)_ij^2 * pi^2 )
             = sqrt( 2 pi^2 / N * (1/pi^4) * pi^2 )      = sqrt(2/N)
proposed:  sqrt( 2 pi^2 * (M^-1)_ii / N )
             = sqrt( 2 pi^2 * (1/pi^2) / N )             = sqrt(2/N)
```

Both give `sqrt(2/N)`, matching Appendix II of PR-10-006 (Eqs. 9 and 15). This
also follows from the ratio formula above: `K = 2I` gives `K_ii/2 = 1` and a
vanishing off-diagonal sum, hence ratio exactly 1. Checked numerically to machine
precision (`max |code/correct - 1| < 1e-15`) on three grids, including the code's
own `36 x 18` `hs` bin-centre grid.

**Consequence for any validation effort: a flat-`phi` test has no discriminating
power here.** The two formulas agree exactly in that limit, so reproducing
`sqrt(2/N)` confirms only that the machinery works — it says nothing about which
error propagation is right. That is very likely why the defect survived: the
ideal case is the one that was checked. Discriminating between the two requires a
measure with genuine off-diagonal structure in `G`.

So the code agrees with the proposal in the ideal limit and departs from it —
upward, in any realistic acceptance — as soon as the matrix acquires off-diagonal
structure. The bias is conservative: projected errors too large, improvement
factors understated.

**This is not about the matrix definition.** The proposal projects with
`g = (sin phi, sin 2phi_h cos phi, cos 2phi_h sin phi)` and inverts the mixed
matrix `(M_prop)_jk = int g_j f_k`, while the code inverts the symmetric Gram of
`f` with itself. Those differ — `M_prop = T G` with `g = T f` and `T` invertible —
but `T` cancels identically in the estimator:

```
p_hat = (T G)^-1 (T J) = G^-1 J        with J_k = int A f_k
```

Both constructions therefore return the *same* three asymmetries. The defect is
solely in the error propagation applied afterwards: the proposal's
`delta_i^2 = int (dA)^2 (sum_j (M^-1)_ij g_j)^2` expands the square and keeps the
cross terms, which is `[B Cov(J) B^T]_ii`; the code's row norm drops them.

**Fix — one line.** Since `K_ii = 2 pi^2 (M^-1)_ii`:

```cpp
Estatraw[i] = sqrt(2.0 * M_PI * M_PI * MUT3(i,i) / Nacc);
```

Everything else in the block is unchanged. Worth adding alongside it, because
`TMatrixD::Invert()` returns garbage rather than failing on a near-singular
matrix, and narrow-azimuth runs are where it goes singular:

```cpp
if (!(MUT3(i,i) > 0)) std::cout << "non-positive diagonal in inverted MUT3!" << std::endl;
```

A true inverse of a positive-definite Gram matrix has a strictly positive
diagonal, so this catches a collapsed matrix directly — something the row-norm
form could not, since squaring hides the sign.

**Cost of fixing.** Every projected error bar in the repo comes from this line, so
switching it redefines every `Projections_*`, every `data*`, every `output*`, and
the standing numbers in `phicompare.md`. It also interacts with `tol`, which was
calibrated against published uncertainties computed with the current form.

The empirical size of the correction under the real acceptance was measured
without touching production — additive `E*statLS` branches in a copied header —
and is recorded in the 2026-08-25 entry of `runlog.md`.

**Status 2026-08-27 — carried in the tree, production unchanged.**
`AnalyzeEstatUT3` now writes `E{0,1,2}statraw_diag` alongside the untouched
`E{0,1,2}statraw`, so every run measures the correction without redefining
anything. The guard suggested above ships with it: a non-positive diagonal in the
inverted matrix prints the bin index.

It also writes `E{0,1,2}statraw_prop`, built by the *independent* route of
Appendix II of PR-10-006 — projecting with `g = (sin(phi), sin(2 phih) cos(phi),
cos(2 phih) sin(phi))`, inverting the mixed matrix `(M_prop)_jk = Int g_j f_k`,
and propagating `delta_i^2 = Int (dA)^2 (sum_j (M_prop^-1)_ij g_j)^2`. This is the
construction the "not about the matrix definition" paragraph above predicts must
reduce to the diagonal form once `T` cancels. **It does, to machine precision**:
`max |prop/diag - 1| = 3.3e-16`. The analytic claim in this item is therefore
confirmed numerically by two independent implementations, and the remaining
question is only whether to switch production over.

---

## 11. `hs` is filled with `|phi_S|`, folding the moment matrix's measure

**What.** The accepted-event density that defines the moment matrix is booked on
a half-range `phi_S` axis and filled with the absolute value
(`SoLID_SIDIS_3He.h:808,835`, identically `SoLID_SIDIS_NH3.h:644,670`):

```cpp
TH2D * hs = new TH2D("hs", "hs", 36, -M_PI, M_PI, 18, 0, M_PI);
...
hs->Fill(sidis.GetVariable("phih"), std::abs(sidis.GetVariable("phiS")), weight * acc);
```

`MUT3` is then built from that histogram's bin centres, so every event generated
with `phi_S < 0` contributes to `<f_i f_j>` at `+|phi_S|` instead of at its own
`phi_S`. Under that reflection the basis does not map to itself:

```
f_1 = sin(phi_h - phi_S)  ->  sin(phi_h + phi_S) = f_2
f_2 = sin(phi_h + phi_S)  ->  sin(phi_h - phi_S) = f_1
f_3 = sin(3 phi_h - phi_S) -> sin(3 phi_h + phi_S)     <- not in the basis
```

so with `G = <f f^T>` and `Gtilde` the folded version actually computed,

```
Gtilde_ij - G_ij = int_{phi_S < 0} rho * [ (tau f_i)(tau f_j) - f_i f_j ]
```

Reading it off: the `(1,2)` element is **exactly** preserved (the product is
invariant under swapping `f_1` and `f_2`), the `(1,1)` and `(2,2)` diagonals pick
up equal and opposite shifts — the Collins-like and Sivers-like normalisations
partially exchange — and the `f_3` row and column are corrupted differently,
since `sin(3 phi_h + phi_S)` leaves the span altogether.

**Magnitude — small, and often exactly zero.** Checked numerically against the
unfolded measure over a range of synthetic densities:

| density | max abs deviation in `G` | error ratio fold/true |
|---|---|---|
| flat | 0 | 1 (exact) |
| `4 x 24 deg` sectors x any `b(phi_S)` | `1e-16` | 1 (exact) |
| same, sectors shifted 30 deg | `1e-16` | 1 (exact) |
| near-flat with mixed `phi_h`/`phi_S` terms | `9.8e-4` | 0.998 - 1.001 |
| `2 x 24 deg` sectors x `1 + 0.9 sin(2 phi_h - phi_S)` | `2.8e-2` | 1.01 - 1.05 |

The effect vanishes identically whenever the `phi_h` distribution kills the
harmonics the reflection acts on — which the evenly spaced sector sets used in
this repo do — and only appears once `rho` carries a genuine `phi_h`-`phi_S`
correlation. In the synthetic families reachable without the real acceptance it
stays at the sub-percent to few-percent level, i.e. **an order of magnitude below
item 10's 1.09x - 1.24x**, and well inside the +-20% run-to-run noise on
improvement factors.

**Status: documented deviation, magnitude unmeasured under the real acceptance.**
`hs` is a local in `AnalyzeEstatUT3()` and is never written out, so nothing on
disk can settle this retrospectively. Measuring it means booking a second
`36 x 36` histogram on the full `[-pi, pi]` `phi_S` range alongside the existing
one and comparing the two matrices per bin — the same additive, non-invasive
pattern used for the `E*statLS` branches (2026-08-25 `runlog.md` entry).

**If it is ever fixed**, the change is two lines (axis range and dropping the
`std::abs`), it must be made in **both** headers, and it moves every error bar —
so it should ride along with items 9 and 10 rather than trigger its own
regeneration. Note the folded form is not obviously deliberate: nothing else in
the code assumes a `phi_S`-symmetric acceptance, and a half-range axis with the
same 18 bins also halves the `phi_S` resolution of the matrix.

---

## 12. Five `simenhanced3he.dat` carry a stale `AUTPretzelosity` column

**What.** `PAR['pretzelosity']` in `prepare.py` was corrected on 2026-09-02 from
`a = 2.2, MT2 = 0.21` to `a = 2.5, MT2 = 0.18`. The old pair matched no published
source; the new pair is Table III of Lefky and Prokudin, *Extraction of the
distribution function h_1T^perp from experimental data*, Phys. Rev. D **91**,
034010 (2015), [arXiv:1411.0580](https://arxiv.org/abs/1411.0580)
(JLAB-THY-14-1885), checked against both arXiv versions, which are identical
here. The five prepared files predate the fix and were **not** regenerated (held
off deliberately, 2026-09-02).

**Evidence.** The stored columns reproduce the *old* parameters exactly:

```
max |stored AUTPretzelosity - AUTPretzelosity(a=2.2, MT2=0.21)| = 9.8e-17
```

**Impact.** `AUTPretzelosity` moves by a median 31.5% (range 3.7-50.2%); mean
|A_UT| 0.00580 -> 0.00446. `error_tot_pretzelosity` moves with it, since it is
built from `AUTPretzelosity * systrel`. `AUTSivers`, `AUTCollins` and every
`error_stat_*` are untouched -- those parameters did not change.

**Nothing downstream reads either column.** The fits use Collins/Sivers, `FOM/`
uses `error_stat_collins`, and `phicompare/errors_plot/plot_errors.py` excludes pretzelosity
on purpose. So no result in this repo is wrong because of it; the files are
simply inconsistent with the code that claims to produce them.

**Affected** (all written 2026-08-31):

```
phicompare/data_phifull/simenhanced3he.dat
phicompare/data_phi4seg24deg/simenhanced3he.dat
phicompare/data_phi4seg24deg_phifullbin/simenhanced3he.dat
phicompare/data_phi4seg24degFA/simenhanced3he.dat
phicompare/data_phi4seg24degFA_phifullbin/simenhanced3he.dat
```

**Fix.** `./prepare.py <rundir>` on each; about a minute apiece. `AUTSivers` and
`AUTCollins` should come back bit-identical -- worth checking as part of the run,
since a difference there would mean something else moved too.

**Do not quote a pretzelosity projection either way** -- see `code.md` step 5.
The amplitude is a placeholder whose normalisation is not established, and the
source's own null test gives P(163.48, 175) = 72%, i.e. the world data are
consistent with pretzelosity being zero.

---

## Suggested order if you act on any of this

1. **Item 9** (Sivers carries the Collins error) — the only item that makes a
   published number wrong rather than uncertain, and the code fix is a handful of
   lines. Everything Sivers downstream needs re-running, Collins nothing.
2. **Item 10** (row norm instead of diagonal) — one line, and it moves every
   error bar in the repo. Decide it together with item 9: both change the `stat`
   column, so one regeneration can carry both. **The correct value is now
   measured per bin** (`E*statraw_diag`, and independently `E*statraw_prop`), so
   the decision no longer needs a special run — only a choice. **Item 11** (the `|phi_S|` fold)
   belongs in the same pass rather than a rank of its own: it is a two-line change
   in the same block, it moves the same `stat` column, and on the evidence so far
   its effect is an order of magnitude below item 10's. Doing it alone would cost
   a full regeneration for a sub-percent correction.
3. **Decide on item 2** (world fluctuation) — it changes published error bars,
   the fix is three lines per script, and everything downstream would need
   re-running.
4. **Item 3** (starved bins) — decide whether to filter them in `prepare.py` or
   simply footnote the 4-sector result. No re-running needed for option (a).
5. **Item 5** (mirror the sivers Minuit limits into fitcollins) — cheap
   insurance, no effect on current results.
6. **Item 8, option (a)** — one `else: raise` in `H1col`, same character of fix:
   no effect on any current number, and it removes a confusing latent crash.
7. Items 4 and 6 only if you want to attack the `tol` factor properly, which is
   a much larger piece of work.

---

## Already done (documentation only — no behaviour changed)

- **2026-08-18** — the `prepare.py` dataflow note corrected (see item 1); it now lives in `code.md`, step 4.
- **2026-08-18** — comment block added above `simulate()` in **both**
  `fitcollins.py` and `fitsivers.py`, explaining why the world-fit result is
  pushed into `simdata` (one self-consistent truth across the two datasets that
  share a chi2; the return value also starts each replica's migrad at the truth)
  and recording that it degenerates to identity here. Inline notes on the
  `par0`/`var0` lines cover why both accessors are needed —
  `Min.values` is a name-keyed live `ValueView` (needed for `par['Nu']` access in
  `tmd.*`), `Min.np_values()` is a positional ndarray snapshot (needed for
  `from_array_func(start=...)`) — that both include fixed parameters, and that
  `par0` is a view rather than a copy, safe only because it is consumed before
  `Min` goes out of scope.
- Both scripts recompile and run; no numerical output changed.
