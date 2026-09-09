# SIDIS event generator with impact study

**This code repo is based on https://github.com/TianboLiu/LiuSIDIS/blob/master/SoLID/sidis2020 with the following main update**
**1. fix the stat error matrix MUT3 definition and obtain smaller error for acceptance not 4pi**
**2. use phi_S(-180,180)deg instead of abs(phi_S)(0,180) for MUT3 calculation with uneven acceptance**
**3. use 360x360 bin in phi_H and and phi_S instead of 36x18 bin for more accurate stat error estimation**
**4. speed up code to read PDF only after acceptance cut in SoLID_SIDIS_3He.h, use lru_cache in tmd.py, and use fast integrate for tensor charge error calculation in its plot notebook**
**5. speed up code to run C++ in forked child process and python fitting in multiprocessing**
**6. add phi acceptance cut for SoLID light study**
**7. add 3 AUT related asymmetry errors and fitting errors in output**
**8. use a single output dir and reduce number of output files**
**9. add AUTPretzelosity as a placeholder in tmd.py**

## What it does

Generates SoLID pseudodata for the 3He (neutron) target, fits TMD asymmetries
(Sivers / Collins) to world data + SoLID pseudodata, and writes the per-replica
parameter tables the impact plots are built from.

Two stages: **C++/ROOT** (event generation, acceptance folding, binning) →
**Python** (fitting). They talk only through files on disk.

**Scope.** This is the neutron (3He) path only. The proton (NH3) path — its
`analysis_proton.C` and `SoLID_SIDIS_NH3.h` — is not here yet; the fit options
that need combined proton+neutron datasets are wired up and will report what they
are missing if invoked.

## Where to read what

| file | for |
|---|---|
| this file | getting it built and running |
| `physics.md` | the physics: what each step computes, and the formula behind it |
| `code.md` | the implementation: entry points, formats, performance, traps |
| `CLAUDE.md` | the same operational reference, written for coding agents |
| `SIDIS_MUT3_comparison/` | the `MUT3` statistical-error study: `_base.md` derives how the code's `Estatraw` compares with Appendix II of PR-10-006 and tests it with the detector switched off; `_other.md` continues into the azimuthal cut and the \(\phi_S\) folding. Figures included, with `make_figures.py` to regenerate them; the run directories behind them are not (6.7 GB) |
| `phicompare/README.md` | the azimuthal-acceptance study: what a partial-$\phi$ detector costs, in two forms — the `plot-{transversity,sivers}_phicompare.ipynb` notebooks (band and tensor-charge comparisons across five acceptance configurations) and `errors_plot/` (the three-term error budget behind them) |
| `FOM/README.md` | the SoLID-vs-SBS figure of merit: reproduces the pre-CDR's own comparison figure, then extends it to $Q^2$, $z$, $p_T$ and $q_T/Q$ |
| `data_world/README.md` | the shared inputs every run reads: world data, the two SBS projection vintages (and why they are not interchangeable), and why the `value` column in prepared fit inputs is model output, not data |

**Working notes are not published here.** `physics.md` and `code.md` cite
`check.md` (settled investigations and their evidence), `bug.md` and
`bug_codex.md` (open problems and a one-off external review),
`phicompare_old.md` (the azimuthal-acceptance study's frozen upstream
conclusions — the current ones are `phicompare/README.md`, published) and
`runlog.md` / `runlog_old.md` (run provenance). Those files live in the working
tree, not in this repository; a citation to one is a pointer to evidence, not to
a file you will find here.

## Setup

```
source setup.csh    # tcsh
source setup.sh     # bash/zsh
```

Loads ROOT 6.40.02 (via `module`) and the LHAPDF 6.5.6 environment, including
`PYTHONPATH` for the LHAPDF python bindings. Each shell invocation is
independent — source the script and run your commands in the *same* shell.

Python packages not installed by default here: `pandas` and **`iminuit<2`**
specifically (the fit scripts use the v1-only `Minuit.from_array_func`). See
`CLAUDE.md` for the exact install lines and the environment traps.

## Build

```
make O=analysis_neutron     # 3He (neutron), uses SoLID_SIDIS_3He.h
make clean
```

The makefile is generic in `$(O)`: a new target needs a matching `<name>.C` and
its own `SoLID_SIDIS_*.h`. `SoLID_SIDIS_3He.h` includes `Lsidis3.h` directly.

If a build stops with `No rule to make target`, a stale auto-generated `.d` file
is still listing a header that has since been removed — `make clean` and retry.

## Run the pipeline

**One run lives in one directory.** Every stage takes the same `<rundir>` on the
command line and both reads and writes there. It is **required** — there is no
default, because a forgotten argument used to mean silently reading or
overwriting whichever run was there last. It is created if missing.

The only input from outside `<rundir>` is `Acceptance/` (the SoLID acceptance
maps) and `data_world/` (world data, shared across all runs).

### 1. Generate pseudodata (C++)

```
./analysis_neutron <opt> <rundir> [phicut] [phiscope] [phiwidth] [acccut] [phisfold]
#   opt 0 = total rate       -> prints only, no rundir needed
#   opt 1 = kinematic bins   -> <rundir>/bin_enhanced_*.dat
#   opt 2 = projection files -> <rundir>/enhancedN*.root
#                            +  <rundir>/enhancedN*_hs.root (per-bin hs + hs_full maps)
#   opt 3 = text tables      -> <rundir>/enhancedNpi{p,m}.csv
#   phicut   = number of azimuthal sectors kept, evenly spaced and centred on
#              phi = 0 (0/unset = full 2pi)
#   phiscope = all (default) or FA (cut the forward angle only)
#   phiwidth = full width of one sector in degrees (default 24)
#   acccut   = on (default) or off; off removes the detector entirely (every
#              acceptance returns 1.0) -- a diagnostic, not a configuration
#   phisfold = full (default) or fold; which azimuthal map the moment matrix is
#              built from, signed phi_S or |phi_S|
```

Run it with no arguments for the full help, which is the authoritative
description of every option. The azimuthal maps `hs`/`hs_full` are booked at the
bin width set by `NPHI` in `SoLID_SIDIS_3He.h` (currently 360 bins = 1 deg);
cost scales as `NPHI^2`.

Coverage is `phicut x phiwidth / 360`, so `4 x 12 deg` and `2 x 24 deg` keep the
same total azimuth but sample it in different places. Overlapping configurations
are rejected: `phiwidth > 360/phicut` exits 1.

### 2. Prepare fit inputs (Python)

```
./prepare.py <rundir>          # the neutron SoLID path
./prepare.py <rundir> --sbs    # or: the external SBS projection instead
```

Reads `<rundir>/enhancedNpi{p,m}.csv`, fills the Sivers/Collins/Pretzelosity
`value` columns by evaluating `tmd.py` at each row's kinematics (the C++ writes
`0.0` there), merges pi+/pi-, and writes **one file**,
`<rundir>/simenhanced3he.dat`, carrying every amplitude and both
`error_stat_<obs>` and `error_tot_<obs>` — step 3's `enhanced3he` and
`enhanced3hesyst` opts read the same file, just a different error column.
**Re-run it whenever step 1-3 is re-run** — nothing downstream can tell that
the CSVs moved underneath it.

`--sbs` is a different path for a different input: it turns an external SBS
projection (`sbs0{1,2}_root.dat`, not generated by this pipeline) into the same
kind of fit-ready file, one per observable. See `data_world/README.md`.

### 3. Fit (Python)

```
./fitcollins.py <opt> <rundir>
./fitsivers.py  <opt> <rundir>
```

Run either with no arguments to list the opts. Each fit runs 500 bootstrap
replicas in parallel (`-n NREP`; `-s SEED0` shifts the ensemble) and writes
`<rundir>/out-<opt>_<obs>.dat`, the raw per-replica parameter table. The central
value and error are **not** computed here — they are the mean and standard
deviation across replicas, taken downstream (`code.md` step 7).

`-t R` restricts the *simulated* dataset to rows with collinearity
`R1 < R` (`tmd.CalculateRfactor`, the current-fragmentation region — see
`physics.md`) before fitting; world data is never touched by it, by
construction, not convention (`code.md` step 6). Output then lands in
`out-<opt>_<obs>_r1lt<R>.dat`, beside the unfiltered result.

`./run_fits.sh <rundir> [opt ...]` runs both scripts back to back with a
preflight check (ROOT, LHAPDF, the PDF sets, `iminuit<2`) and halves the worker
count on an `ifarm` host; `-h` for its flags, which mirror the two scripts'.

Datasets load only when the chosen opt needs them. World data comes from
`data_world/colworld_<obs>.dat`; everything else from `<rundir>`. A missing file
reports the opt, the dataset and where it looked, then exits 1.

**Watch the naming:** `enhanced3he` is the **neutron-only** subset, while the
unsuffixed `enhanced` is the **combined** proton+neutron set — which is why those
opts cannot run yet.

## Directory naming

`<rundir>` should carry a suffix naming the condition it was produced under:

| suffix | meaning |
|---|---|
| `_phifull` | full 2pi acceptance — the baseline |
| `_phi<N>seg<W>deg` | N sectors of W degrees — e.g. `_phi6seg24deg`, `_phi4seg24deg`, `_phi4seg12degFA` (trailing `FA` = cut applied to the forward angle only) |
| `_phifullbin` | reused `_phifull`'s step-1 bins instead of regenerating |
| `_4pi` | `acccut=off` — detector removed |
| `_phisfold` / `_phisfull` | which `[phisfold]` the moment matrix was built with |
| `_bin<N>deg` | the azimuthal histogram bin width `NPHI` was compiled with |

Only a `_phifullbin` run pairs 1:1 with `_phifull`, so **only those are a fair
like-for-like comparison**. An own-bins run re-bins under its own acceptance, so
its row counts and chi2 are not comparable across runs.

Within a run directory, files that would collide between the two observables
carry a `_collins` / `_sivers` suffix — the convention `data_world/` already uses.

## Run logging

After any production run of an `analysis_*` step, `prepare.py`, `fitsivers.py`
or `fitcollins.py`, add an entry to a run log (newest first): command, timing,
output locations, and anything notable. It is the provenance record for every
number in the plots. The log for the runs behind the published projections
(`runlog.md`) is kept in the working tree, not here.
