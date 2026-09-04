# The code, step by step

How each stage of the pipeline is actually implemented — entry points, data
formats, the design decisions behind the fast paths, and the traps. The physics
each step computes is in `physics.md`; this is its counterpart on the code side.
Study conclusions live in `phicompare/README.md`, settled investigations in
`check.md`, open problems in `bug.md`, run provenance in `runlog.md`. Written
2026-08-19; step 5 (`tmd.py`) extended 2026-08-24 with the model's provenance and
its traps.

## The shape of the whole thing

```
  Acceptance/*.root ─┐
                     ▼
  analysis_neutron <opt> <rundir> [phicut] [phiscope]      C++ / ROOT
     opt 1 ─ build bins        → <rundir>/bin_enhanced_*.dat
     opt 2 ─ fill + errors     → <rundir>/enhancedN*.root + *_hs.root
     opt 3 ─ write tables      → <rundir>/enhancedNpi{p,m}.csv
                     │
                     ▼
  prepare.py <collins|sivers> <rundir>                      Python
     inject model asymmetry, combine errors
                               → <rundir>/simenhanced3he{,syst}_<obs>.dat
                     │
   data_other/ ──────┤   (world data, shared across runs)
                     ▼
  fit{collins,sivers}.py <opt> <rundir>
     NREP bootstrap replicas × Minuit
                               → <rundir>/out-<opt>_<obs>.dat
```

**One run, one directory.** Every stage reads and writes the same `<rundir>`,
named on the command line and required — there is no default. Files that would
otherwise collide between the two observables carry a `_collins` / `_sivers`
suffix, the convention `data_other/colworld_{collins,sivers}.dat` already uses.

Each arrow is still a file on disk and no stage re-runs the one before it, so the
ordering hazard remains: `prepare.py` cannot tell that `analysis_neutron` rewrote
the CSVs underneath it. Re-run it whenever they change (`runlog_old.md`,
2026-08-17, records the day that bit). Sharing one directory at least means there
is a single mtime to look at.

---

## Step 1-3 — the generator (`analysis_neutron.C`, `SoLID_SIDIS_3He.h`, `Lsidis3.h`)

**Build.** `make O=analysis_neutron` compiles `analysis_neutron.C`, which
`#include`s `SoLID_SIDIS_3He.h`, which in turn includes `Lsidis3.h` directly
(upstream that went through an `Lsidis.h` symlink pointing outside the tree,
which a standalone repo cannot do; the symlink was removed 2026-08-27).
The makefile is generic in `$(O)`, so a new target
needs a matching `.C` plus its own `SoLID_SIDIS_*.h`. Requires ROOT 6.40.02 and
LHAPDF 6.5.6 — `source setup.sh` first (see CLAUDE.md for the C++17 / linker
flags that current toolchains need).

**CLI.** `./analysis_neutron <opt> <rundir> [phicut] [phiscope] [phiwidth] [acccut] [phisfold]`.
`opt` selects the step (1 bins, 2 fill, 3 tables); `phicut` is the *number of
sectors* to keep, `phiwidth` their *full width in degrees* (default 24, so an
older command line is unchanged), and `phiscope` (`all`/`FA`) says whether the cut
applies to every arm or the forward angle only. All three are printed at startup,
so the log records what actually ran. A combination whose sectors would overlap
(`phiwidth > 360/phicut`) is rejected before any work starts — that is what keeps
the coverage line in the banner honest (`bug_codex.md` item 12). `rundir` is required for opts 1/2/3 (opt 0 only prints rates and writes nothing) and is created if missing — before that was added, a missing directory
segfaulted the forked children and ROOT's crash handler left the parent hung in
`waitpid()` forever, looking exactly like a long computation.

**Class layout.** `Lsidis` (in `Lsidis3.h`) is the physics engine: it owns the
kinematics, the LHAPDF handles, the cross section, and the samplers.
`SoLID_SIDIS_3He.h` is the experiment layer: acceptance maps, luminosity, binning,
the error model, and the CSV writer. `analysis_neutron.C` is only a driver.

**The hot loop and its optimisation.** The naive call is
`sidis.GenerateEvent(mode, method)`, which samples kinematics *and* evaluates
PDFs/FFs in one shot. `Lsidis3.h` adds a backward-compatible split:

```cpp
sidis.GenerateEventKinematics(1);          // sampling only, no LHAPDF
if (cuts fail) continue;                   // W, W', R-factor, acceptance
weight = sidis.GetWeightFromCurrentState(0);   // now pay for PDFs/FFs
```

Since most sampled events fail the acceptance cut and LHAPDF evaluation dominates
the per-event cost, running the cheap cuts first is worth ~1.7-1.8x. **Converted
throughout `SoLID_SIDIS_3He.h`; `SoLID_SIDIS_NH3.h` (proton) still uses the
one-shot call everywhere.**

**Parallelism.** `RunGroupsInParallel()` in `analysis_neutron.C` splits each step
into four groups (N11p/N11m/N8p/N8m) across `fork()`ed children — processes, not
threads, because ROOT's `gRandom` and its current-file/current-directory globals
are not thread-safe. Utilisation runs 185-360% depending on how evenly the bins
divide; the largest group (N11p, 782 bins) is the tail.

**What `phiscope=FA` actually widens.** Only the electron has a large-angle
acceptance in `SoLID_SIDIS_3He.h` (`GetAcceptance_e` sums `acc_FA_e` and
`acc_LA_e`, the latter for `mom > 3.5`); every hadron is forward-angle only —
`acc_LA_pip`/`pim`/`kp`/`km` are loaded at the top of the file but never read. So
`FA` widens the *electron's* coverage, not the event's: the SIDIS coincidence is
still gated by the hadron's `phi_nsector` × 24°. `phiscope=FA` with `phicut=0` is
a no-op and says so. (Confirmed by a φ scan — `check.md`.)

**Binning (opt 1).** `GenerateBinInfoFile()` builds a 4-D binning in
(Q², z, P_T, x). Two axes are a fixed grid, two are adaptive, and everything is
driven by one quantity: the **integrated rate per bin**.

The fixed grids, hardcoded and identical for every run:

```cpp
Q2list[7] = {1, 2, 3, 4, 5, 6, 8};                        // 6 slices, GeV^2
zlist[9]  = {0.3, 0.35, ..., 0.7};                        // 8 slices of 0.05
Ptlist[7] = {0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.6};          // candidate edges
statlist[6] = {1.9e7, 1.1e7, 5.0e6, 3.0e6, 2.0e6, 2.0e6}; // rate target per Q2 slice
```

The target falls with Q² because the rate does — high-Q² bins are allowed to hold
fewer counts rather than becoming impossibly wide.

**P_T is adaptive by merging upward.** For each (Q², z) cell, P_T starts at 0 and
the loop tries successive `Ptlist` edges. It throws `Nsim = 1e6` events, fills a
7000-bin histogram in x weighted by `weight * acc`, and scales to expected counts
by `lumi * time * eff / Nsim`. If the total is below `statlist[Qi]` the cell is
too empty: discard, widen P_T to the next edge, retry. Sparse P_T slices are
therefore absorbed into their neighbours. The final slice uses a relaxed
`0.25 * statlist[Qi]` so the high-P_T tail is not merged away entirely.

**x is adaptive by accumulation.** Once a P_T range is accepted, the code walks
the 7000 x-bins (each 1e-4 wide over 0-0.7) and closes a bin whenever the running
integral exceeds the target:

```cpp
if (hx->Integral(xi, xj) > statlist[Qi] || xj == 7000){ ...write...; xi = xj + 1; }
```

So x bins are deliberately unequal in width — wide where the rate is thin, narrow
where it is dense, each holding ≈`statlist[Qi]` counts. In `data_phifull` the
first N11p bin spans x ∈ [0.0000, 0.1005] and the next four are [0.1005, 0.1136],
[0.1136, 0.1240], [0.1240, 0.1332], [0.1332, 0.1416].

Three consequences:

- **Bin edges depend on the acceptance**, because the histogram is filled with
  `weight * acc`. Change the acceptance and both the P_T merging decisions and the
  x split points move. That is why "own bins" and `_phifullbin` are different
  objects, and why only the latter compares 1:1 with a baseline.
- **It explains the 4π bin explosion.** With `acccut=off`, `acc = 1` raises the
  rate ~10x, so far fewer P_T slices merge and each x range fills its quota much
  sooner: 1660 bins → 20614 (`runlog.md`, 2026-08-27).
- **The last bin of every (Q², z, P_T) cell is a remainder.** `xj == 7000`
  force-closes it whether or not the target was met, so the highest-x bin can hold
  well under `statlist`. Those are the starved bins that appear as spikes in the
  `Estat`-vs-bin figures and as the low-`Nacc` tail — min `Nacc` 417.8 at phifull,
  4.03 in the 4×24° `_phifullbin` run.

Note `Nsim = 1e6` here against up to `1e7` in step 2: step 1 only needs the shape
well enough to place edges.

**Errors (opt 2).** `AnalyzeEstatUT3()` fills a (φ_h, φ_S) histogram `hs`,
builds the 3×3 azimuthal moment matrix, calls `TMatrixD::Invert()`, and turns the
result into `Estat[3]` (see `physics.md` step 3 for the formula). A second
`Lsidis` instance configured as a bare neutron runs in the same loop to give the
dilution `fn`. Watch for: when a bin has `Nacc == 0` the division produces `-nan`
in `stat`/`systabs` — first seen in the 2×24° FA run, 32 bins.

**Two azimuthal histograms, and both are kept per bin.** The loop fills:

| name | axes | used by |
|---|---|---|
| `hs` | 36 × 18, φ_h ∈ [−π,π] × **\|φ_S\|** ∈ [0,π] | MUT3 → `Estat` |
| `hs_full` | 36 × 36, φ_h ∈ [−π,π] × **φ_S** ∈ [−π,π] | MUT3 when `phisfold=full`; otherwise diagnostic only |

`hs` is folded onto `|φ_S|`, so MUT3 evaluates `sin(φ_h − |φ_S|)` rather than
`sin(φ_h − φ_S)`; those differ wherever φ_S < 0. `hs_full` keeps the unfolded
distribution so that approximation can be examined — and it has been:
**folding is safe, changing `Estat` by ≤2% in 90% of bins and by >2× in exactly
one bin of 782** (`check.md`, 2026-08-26). `phifull` is ±φ_S symmetric to the
noise floor; the φ-cut runs are not, but the error cancels anyway.

Switching MUT3 onto `hs_full` is now the `[phisfold] = full` argument rather than
an edit. It moves three things together: the `j <= 18` bound becomes 36, the bin
centres become signed φ_S, and the angular area Ω becomes 4π². **The third is the
trap** — `Estatraw` is the only Ω-sensitive estimator, because it squares the
inverse, and its historical prefactor `2π²·π²` equals Ω²/2 at the folded Ω only.
Left alone under `full` it returns half the correct error; the code now uses the
general `Ω²/2`. `Estatraw_diag` and `Estatraw_prop` need no change, Ω cancelling
in both. Every `Estat` on record was computed the folded way, and `fold` remains
the default.

MUT3 collapses `hs` to three numbers and both histograms are then deleted, so
without saving them the distributions cannot be re-examined short of re-running
the step. They are written as `hs_NNNN` and `hs_full_NNNN` into
`<savefile>_hs.root` — one file per forked group, since the four children cannot
share a `TFile`. The index matches the tree entry and the `bin_enhanced_*.dat`
row 1:1, and each title carries the bin's Q²/z/P_T/x ranges so the file browses on
its own.

Verified on a 3-bin run: both integrals equal the tree's `Nacc` to a ratio of
exactly 1.0 (all three are Σ`weight`·`acc` under the same scaling), and folding
`hs_full` onto `|φ_S|` reproduces `hs` bin-for-bin to 1.75e-10. Cost is ~23 KB
per bin, so ~38 MB across a full 1660-bin run.

**Tables (opt 3).** Writes one CSV per hadron, columns
`i,Ebeam,x,y,z,Q2,pT,obs,value,stat,systrel,systabs,target,hadron,Experiment,Nacc`.
**`pT` is transverse to the virtual photon, not to the beam** — see
`physics.md` step 1, *What $P_T$ is measured against*; it is also why no row
here can give you the hadron's lab angle.
`value` is **hardcoded `0.0`** — the C++ computes no asymmetry. `Nacc` was added
2026-08-17; anything prepared before that lacks the column.

## Step 4 — `prepare.py`

```
./prepare.py <collins|sivers> <rundir>
```

Reads `<rundir>/enhancedNpi{p,m}.csv`, concatenates π⁺ and π⁻, and does three
things: drops rows whose `stat`/`systabs` are non-finite (the `Nacc == 0` bins —
they would make the whole χ² NaN, unlike merely starved bins which just get ~zero
weight); fills `value` by evaluating `tmd.py` at each row's kinematics with
a fixed truth parameter set (`par0` Collins, `par1` Sivers); and collapses
`stat`/`systrel`/`systabs` into a single `error` column, written twice — stat-only
and stat+syst. Output is tab-separated `simenhanced3he_<obs>.dat` /
`simenhanced3hesyst_<obs>.dat`, the suffix letting Collins and Sivers share one
run directory.

The other dataset combinations (sbs/clas/base/proton) are commented out here —
their inputs were never generated in this tree — but the code for them is intact
in the commented block near the top of the file.

**Dataflow wrinkle.** `fit*.py`'s `simulate()` recomputes `value` before fitting,
so what `prepare.py` wrote never reaches the fit. Numerically it is a no-op (same
parameters, agreement to 1e-16); the recompute exists so the pseudodata and the
world data describe one truth model rather than two. Practical consequence: in
`data*/**.dat` the kinematics and `error` columns are what matter downstream.

## Step 5 — `tmd.py`

Pure model code, no I/O beyond LHAPDF. Layers, bottom up:

| function | returns | notes |
|---|---|---|
| `f1col(x, Q2, target)` | dict of unpolarised PDFs by PDG id | `@lru_cache`d, CJ15lo |
| `g1col(x, Q2, target)` | dict of helicity PDFs | `@lru_cache`d, NNPDFpol11_100; **pretzelosity only** |
| `D1col(z, Q2, hadron)` | dict of fragmentation functions | `@lru_cache`d |
| `FUUT(...)` | unpolarised structure function | Gaussian TMD, widths hardcoded 0.25 / 0.20 |
| `h1col`, `f1Tperp1` | transversity, Sivers first moment $f_{1T}^{\perp(1)}$ | fit-parameterised; `par` dict in, dict out |
| `H1col` | Collins FF | takes `par` and **ignores it** — every constant is fixed |
| `FUTCollins`, `FUTSivers` | polarised structure functions | numerator widths differ from `FUUT`'s — see below |
| `h1Tperp1`, `H1perphalf`, `FUTPretzelosity` | pretzelosity moment, Collins FF half moment, its structure function | **placeholder — see below** |
| `AUTCollins(x,y,Q2,z,pT,...)`, `AUTSivers(x,Q2,z,pT,...)`, `AUTPretzelosity(x,y,Q2,z,pT,...)` | the asymmetries | Collins and pretzelosity carry the depolarisation factor, Sivers does not |
| `gt(Q2, par, xl, xu)` | `{'u','d','u-d'}` | `scipy.quad` of `h1col` per flavour |

The `lru_cache` on `f1col`/`D1col` is the biggest single speedup in the Python
stage — **5.7x** on the fit path (2m30s vs 14m17s for the same 50-replica fit).
It is safe because both are pure functions of `(x-or-z, Q2, target/hadron)`,
independent of the fit parameters that `migrad()` varies, and callers only read
the returned dicts; removing it produces byte-identical output. It buys far less
in the notebooks (1.2-1.3x), where `h1col`'s own arithmetic dominates rather than
the LHAPDF lookup. Both the correctness test and the timings are in `check.md`,
along with the symlink trap that made a first attempt at this measurement
meaningless.

`gt`'s signature differs from the reference project's (`gt(par)` there, fixed at
Q² = 2.4): the version here takes `Q2` and integration limits, which is what makes
truncated tensor charges possible. It always evaluates `h1col` with
`target='proton'`, which is what a tensor charge means.

**Where the hardcoded numbers come from.** Every constant in this file — the
Collins polynomial `c=-2.36, d=2.12`, `Nfav=1.0`, `Ndis=-1.0`, `Mh²=0.67`, and
the Gaussian widths 0.25 / 0.20 — is Anselmino *et al.* (arXiv:1303.3822),
Table 3 and eq. (8). It is *not* KPSY15, whatever an older draft of `physics.md`
said; see `physics.md` step 5 and the 2026-08-24 entry in `check.md` for the
equation-by-equation check.

**Four implementation traps in this file**, none of them visible from the call
site:

1. **`H1col(z, Q2, hadron, par)` ignores `par` entirely.** The Collins FF is
   fully fixed, so no fragmentation uncertainty can propagate; passing a
   different `par` returns the identical value. The signature invites the
   opposite conclusion.
2. **`H1col` handles pions only.** Only `pi+/h+` and `pi-/h-` are matched; a
   kaon argument falls through every branch and raises
   `UnboundLocalError: local variable 'u' referenced before assignment`. `FUUT`
   and `D1col` do support kaons, so a kaon channel dies only once it reaches the
   Collins numerator. Tracked as `bug.md` item 8.
3. **`H1col` shadows both its polynomial coefficients.** `c = -2.36` and
   `d = 2.12` are reused a few lines later as flavour slots (`u, d = FAV, DIS`
   and `s, c, b, ... = 0, ...`). Harmless today because the polynomial is already
   evaluated by then, and a live grenade for anyone editing it.
4. **`h1col` and `f1Tperp1` call `f1col(x, Q2)` without a target**, i.e. always
   proton PDFs, then swap the `u`/`d` slots for a neutron and average them for a
   deuteron. Correct (that *is* the isospin relation), but it means the `target`
   argument of these two functions never reaches LHAPDF.

**`AUTPretzelosity` is a placeholder. Do not quote a pretzelosity projection from
it.** Added 2026-08-31 so the third amplitude has *something* behind it; the
kinematics are right, the normalisation is not established.

What is implemented, and checked: Lefky and Prokudin, *Extraction of the
distribution function $h_{1T}^{\perp}$ from experimental data*, Phys. Rev. D 91,
034010 (2015), [arXiv:1411.0580](https://arxiv.org/abs/1411.0580)
(JLAB-THY-14-1885), eq. (33) for the
structure function and eq. (16) for the asymmetry —
$F_{UT} \propto x z^2 P_{hT}^3 / \langle P^2\rangle_{CT}^4$ with the
$M_T$- and $M_C$-modified widths of eq. (32), the constant
$C = 8\langle k_\perp^2\rangle_T \sqrt{\langle p_\perp^2\rangle_C/\pi}$ of
eq. (34), $h_{1T}^{\perp}(x) = e N(x)(f_1 - g_1)$ of eq. (27) saturating the
positivity bound, and its first moment from eq. (28). The depolarisation factor
is the same $\epsilon$ `AUTCollins` uses, which is algebraically Gao *et al.*'s
$D_{nn}$ (arXiv proceedings, SPIN2010, eq. 8). `AUTCollins` is bit-identical
before and after; the Collins fit was deliberately not touched.

**What still has to be checked before it is anything but a placeholder:**

1. **The Collins FF it convolutes against is not the one the pretzelosity fit
   used.** `H1perphalf` unwraps this file's `H1col` — $M_C^2 = 0.67$,
   `Nfav = 1.0`, `Ndis = -1.0`, the Anselmino 1303.3822 values — while Lefky and
   Prokudin fitted $N_a$, $\alpha$, $\beta$, $M_T^2$ *against* their ref. [17]
   Collins FF, which has $M_C^2 = 1.50$, $N_{fav} = 0.49$, $N_{unf} = -1$. Their
   pretzelosity normalisation is therefore not transferable to this Collins model
   without redoing the fit or rescaling.
2. **The Collins sign convention is unresolved.** Gao *et al.* eq. (6) carries an
   explicit minus, $-(\hat h \cdot k_T/M_h) h_1 \otimes H_1^\perp$, and
   `FUTSivers` does implement the matching minus of their eq. (7) while
   `FUTCollins` has none — presumably absorbed into `H1col`'s
   $\Delta^N D$-style packaging, but neither paper writes the Collins structure
   function in closed form, so it cannot be settled from them. Pretzelosity
   inherits whatever that convention is, through `H1col`.
3. **The parameters are barely constrained.** Table III gives
   $N_u = 1 \pm 1.7$, $N_d = -1 \pm 1.0$, $\alpha = 2.2 \pm 1.2$,
   $\beta = 2$ fixed, $M_T^2 = 0.21 \pm 0.8$ GeV². Their own null-signal test
   returns $P(\chi^2) = 72\%$: the world data are consistent with pretzelosity
   being zero.
4. **Nothing has been validated against a published asymmetry curve.** The checks
   done so far are internal — that $A$ now rises with $z$ rather than falling,
   that $\pi^+/\pi^-$ and proton/neutron flip sign, and that `AUTCollins` did not
   move.

Before it is used: reconcile item 1, settle item 2 against Anselmino *et al.*
(the ref. [17] of Lefky-Prokudin), then reproduce one figure from that paper.

**A z-power trap worth recording.** The first version of `FUTPretzelosity`
carried $1/z$ where eq. (33) has $z^2$ — a factor $z^3$, worth ~5.7x across the
$z$ range of the SoLID bins and ~12.7x over 0.3-0.7. It looked plausible because
it was built by analogy with `FUTCollins`, whose $1/z$ is cancelled by the
explicit $z$ inside `H1col`. Anything built by analogy in this file has to be
checked against the closed form, not against its neighbour.

**Numerator and denominator do not share TMD widths, by design.** `FUUT` uses the
fixed 0.25 / 0.20; `FUTSivers` uses `par['kt2']` as the Sivers width (fitted,
0.16 in the injected truth — narrower than the unpolarised 0.25, as it must be);
`FUTCollins` uses `par['kt2']` for transversity and a fixed
$\langle p_\perp^2\rangle_C = 0.67 \cdot 0.20/(0.67+0.20)$ for the Collins FF.
That is the Torino prescription, not an inconsistency — the separate
generator-vs-`tmd.py` width mismatch flagged in `physics.md` is.

## Step 6 — `fitcollins.py` / `fitsivers.py`

```
./fit{collins,sivers}.py <opt> <rundir>
```

`<opt>` picks the dataset combination — run either script with no arguments for
the list, or read the `elif` chain at the bottom. Outputs go to
`<rundir>/out-<opt>_<obs>.dat`, the `_collins`/`_sivers` suffix letting both
observables share one run directory.

**Datasets load on demand, through `load(name)`.** The `_DATASETS` table maps each
name to a filename and a directory: `world` comes from the shared `data_other/`,
everything else from `<rundir>`. A missing file prints the opt, the dataset and
where it looked, then exits 1 — it does not raise. This matters because six of
the nine datasets (the combined proton+neutron sets `simsbs`, `simclas`,
`simbase`, `simbasesyst`, `simenhanced`, `simenhancedsyst`) are **not in this
repo**; their opts are kept wired up for when the proton path lands. Loading
everything at import, as the scripts used to, meant `world` — which needs none of
them — died before the opt was read.

**The two scripts are deliberately kept structurally identical.** Same branches,
same `load()`/`_DATASETS`, same replica count (`NREP`, default 500), same parallel
machinery. Only `OBS`, the parameter set and the `tmd.AUT*` call differ. If you
change one, change the other.

**χ² and replicas.** `fitfunc(var)` sums `(model - value)² / error²` over the
world rows and the pseudodata rows. `fitsim(Nrep, filename)` fits `Nrep` replicas,
each fluctuating `value` by `np.random.normal(value, error)`, and writes the raw
`NREP`×7 table — `Nu,Nd,a,b,c,kt2,chi2` for Collins, the 11-parameter set for
Sivers.
**No central value or error is computed here**; that happens downstream in the
notebooks.

**Three stacked performance fixes**, the first two verified bit-identical:

1. the `lru_cache` on `f1col`/`D1col` in `tmd.py` — **5.7x**, re-measured
   2026-08-20 by removing it (2m30s vs 14m17s on the same fit), with the uncached
   output byte-identical (`check.md`);
2. hoisting `worldrep.loc[i]` out of the per-row loop — the old code did a pandas
   `.loc` lookup per row per χ² call, which was ~68% of the cost. Now each column
   is extracted once per call via `.values` and indexed positionally (~6x on top);
3. replica-level `multiprocessing.Pool` — replicas are fully independent, and the
   GIL makes threads useless here since Minuit calls back into pure-Python
   `fitfunc` on every evaluation. Net (measured 2026-08-20, when 50 was the
   default): a 50-replica fit went from ~80-90
   minutes to ~2.5 minutes.

**Seeding.** Forked workers would otherwise inherit numpy's RNG state identically
— the same footgun as `gRandom` on the C++ side. Each worker calls
`np.random.seed()` with a value derived from its replica index, so the ensemble is
deterministic and independent of which worker takes which replica, which makes a
rerun on unchanged input reproduce its output file exactly (checked on both
scripts — `check.md`). This only holds for runs made after 2026-08-17; earlier
serial output (`*_old.dat`) has independent draws and can only be compared
distribution to distribution.

**The world data is never resampled in a `fitsim` run, and never cut.** Two
separate properties of the same object, both verified empirically rather than by
reading:

```
--- fitsim path (sbs, enhanced3he, ...) ---     md5 of worldrep['value']
  raw world['value']                            12b06d2666e6
  worldrep after simulate()                     12b06d2666e6
  after _fitsim_one(0) / (1) / (2)              12b06d2666e6  (x3, unchanged)
  sim  after _fitsim_one(0) / (1) / (2)         8faaf983c8d0 / 8002ac781d07 / 48f203dcc4bc
--- fitworld path, for contrast ---
  after _fitworld_one(0) / (1) / (2)            747824277b56 / 533c8646f04b / 8d9a9bbbca27
```

`simulate()` sets `worldrep = world.copy()` once and `_fitsim_one` only ever
reassigns `simdatarep`; `_fitworld_one` *does* resample. So:

- **World still constrains the fit.** The chi2 is exactly additive,
  `total = world + sim`, and away from the minimum the world term dominates —
  at `Nu + 0.05` on the SBS set it is 91.93 of 115.95, **79%**, from 146 of 601
  rows. It is not decorative.
- **But it contributes no variance to the replica spread.** Every replica sees
  the same unfluctuated world values, so a `fitsim` band samples only the
  projection's statistical fluctuation and is narrower than a fully consistent
  bootstrap would give.
- **At `var0` the world term is identically zero**, because world's central
  values *are* the model at the reference parameters (`bug.md` item 1). So each
  replica is pulled by the fluctuated projection and anchored by a world term
  that the reference point already satisfies exactly.

This is one more reason not to read a `fitworld` vs `fitsim` band comparison as a
like-for-like precision statement — the two are built by different procedures,
not just from different data.

**The `--tmdcut` filter cannot touch it.** `-t R` keeps only simulated rows with
collinearity `R1 < R` (`tmd.CalculateRfactor`, arXiv:1611.10329). The filter sits
at the top of `fitsim()` and nowhere else; `fitworld()` has no call to it, `load()`
is untouched, and `world` is loaded once at import before any of it. `opt world`
is the only branch that calls `fitworld`, so the guarantee is structural rather
than a naming convention. Belt and braces: `_NWORLD` is captured at load and
asserted in `fitsim()`, `-t` with `opt world` is refused by both the fit scripts
and `run_fits.sh`, and cut output lands in `out-<opt>_<obs>_r1lt<R>.dat` so an
uncut result is never overwritten. `ndof` needs no special handling — `_row`
receives `len(worldrep) + len(simdatarep)` and self-corrects (verified:
146 + 285 - 6 = 425).

**Version pin.** `Minuit.from_array_func(...)` is the v1 API; `iminuit<2` is
required and modern iminuit removed it. Migrating would mean rewriting both fit
functions against a vectorised cost class — the largest open piece of tech debt
in the Python stage.

## Step 7 — turning replica tables into numbers

**The notebooks themselves are not in this repo** (see README). This section
stays because the arithmetic below is where every published central value and
error came from, and because two of the fudge factors in it are traps that any
replacement plotting code will hit as well.

The fit scripts write replica tables; **every central value and error quoted in a
plot is computed downstream of them**, not in the fits. The two workhorses:

```python
h1calc(pset, Q2, tol)   # per x: evaluate tmd.h1col once per replica
gtcalc(pset, Q2, tol, xl, xu)   # per replica: tmd.gt(...)
# central value = np.mean(...) ; error = np.std(...) * tol
```

Notebook-side details that have been checked and are worth not re-deriving
(evidence and reproduction steps in `check.md`):

- **Correlations are handled correctly.** `u-d` is formed *per replica* and the
  std taken of that, rather than adding `Eu` and `Ed` in quadrature — which
  matters, because u and d are correlated.
- **`np.std` vs pandas `.std()`.** Band/g_T errors use `np.std` (`ddof=0`) while
  parameter tables use pandas (`ddof=1`), a consistent ~1% difference at N=50.
- **The `quad` IntegrationWarning is cosmetic** — the full-range integral hits
  the subdivision limit on an integrable singularity as x → 0, but is converged
  far below the quoted error.
- **The full-range g_T is substantially extrapolation**, which is why the
  truncated 0.05 < x < 0.6 number is the one quoted.
- **`f1tcalcorr()` in the Sivers notebook — do not propagate.** A second fudge,
  and a worse one: it multiplies the **errors only** (central values untouched)
  by `exp(-1.7*(abs(x-0.4)+x-0.4)**2)`, identically 1 for x ≤ 0.4 and shrinking
  high-x bands above it (×0.76 at x = 0.6, ×0.34 at x = 0.8). It is applied to
  `world`, `base3he`, `enhanced3he` and their syst variants but **not** to `sbs`,
  `clas`, `base`, `enhanced` — and unlike `tol` it does **not** cancel in a
  ratio, so any plot comparing a 3He set against a proton set at high x has one
  side suppressed and the other not. No derivation for `-1.7` or `0.4` exists.
  Use plain `f1tcalc()` in any new plotting code, and treat high-x Sivers bands
  from that one as suspect.
- **`tol` is a flat multiplier applied at this layer only** — see the appendix in
  `physics.md` for where the value comes from and what it does not justify.

The notebooks these refer to live in the upstream `sidis2020_zwzhao` tree; each
was hardwired to a particular output directory, which is one more reason the
pipeline here collapsed to a single named `<rundir>`.

## Two families of gotcha, collected

**Provenance.** This repo carries no fit outputs at all: every `out-*.dat` is a
product of a run you launched, living in the `<rundir>` you named. The inherited
`outputcollins/` / `datacollins/` copies described in `runlog_old.md` and
`check.md` were **not** brought across, so statements there of the form "our fit
gives X" refer to directories that no longer exist here.

**Reproducibility.** Post-2026-08-17 Python fits are bit-reproducible; C++ runs
are not (no `gRandom` seed is fixed), and pre-parallel Python output is not
either. When comparing two result files, first establish whether they *could* be
identical — otherwise the only meaningful comparison is between distributions,
and the scale for that is σ/√50 = 0.14σ on a mean and 10.1% on a standard
deviation.
