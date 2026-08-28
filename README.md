# SoLID SIDIS impact projections (2020)

Generates SoLID pseudodata for the 3He (neutron) target, fits TMD asymmetries
(Sivers / Collins) to world data + SoLID pseudodata, and writes the per-replica
parameter tables the impact plots are built from.

Two stages: **C++/ROOT** (event generation, acceptance folding, binning) →
**Python** (fitting). They talk only through files on disk.

**Scope.** This is the neutron (3He) path only. The proton (NH3) path — its
`analysis_proton.C` and `SoLID_SIDIS_NH3.h` — is not here yet; the fit options
that need combined proton+neutron datasets are wired up and will report what they
are missing if invoked. Plotting notebooks are likewise not part of this repo;
`code.md` step 7 documents the arithmetic they used.

## Where to read what

| file | for |
|---|---|
| this file | getting it built and running |
| `physics.md` | the physics: what each step computes, and the formula behind it |
| `code.md` | the implementation: entry points, formats, performance, traps |
| `CLAUDE.md` | the same operational reference, written for coding agents |
| `SIDIS_MUT3_comparison/` | the `MUT3` statistical-error study: `_base.md` derives how the code's `Estatraw` compares with Appendix II of PR-10-006 and tests it with the detector switched off; `_other.md` continues into the azimuthal cut and the \(\phi_S\) folding. Figures included; the run directories behind them are not (6.7 GB) |

**Working notes are not published here.** `physics.md` and `code.md` cite
`check.md` (settled investigations and their evidence), `bug.md` and
`bug_codex.md` (open problems and a one-off external review),
`phicompare.md` / `phicompare_old.md` (the azimuthal-acceptance study) and
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
maps) and `data_other/` (world data, shared across all runs).

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
./prepare.py <collins|sivers> <rundir>
```

Reads `<rundir>/enhancedNpi{p,m}.csv`, fills the asymmetry `value` column by
evaluating a TMD model at each row's kinematics (the C++ writes `0.0` there),
combines the error columns, merges pi+/pi-, and writes
`<rundir>/simenhanced3he{,syst}_<obs>.dat`. **Re-run it whenever step 1-3 is
re-run** — nothing downstream can tell that the CSVs moved underneath it.

### 3. Fit (Python)

```
./fitcollins.py <opt> <rundir>
./fitsivers.py  <opt> <rundir>
```

Run either with no arguments to list the opts. Each fit runs 200 bootstrap
replicas in parallel (override with the `NREP` environment variable) and writes
`<rundir>/out-<opt>_<obs>.dat`, the raw per-replica parameter table. The central
value and error are **not** computed here — they are the mean and standard
deviation across replicas, taken downstream (`code.md` step 7).

Datasets load only when the chosen opt needs them. World data comes from
`data_other/colworld_<obs>.dat`; everything else from `<rundir>`. A missing file
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
carry a `_collins` / `_sivers` suffix — the convention `data_other/` already uses.

## Run logging

After any production run of an `analysis_*` step, `prepare.py`, `fitsivers.py`
or `fitcollins.py`, add an entry to a run log (newest first): command, timing,
output locations, and anything notable. It is the provenance record for every
number in the plots. The log for the runs behind the published projections
(`runlog.md`) is kept in the working tree, not here.
