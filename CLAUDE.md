# CLAUDE.md

Guidance for Claude Code working in this repository.

## What this is

SoLID SIDIS (2020) impact-projection pipeline: generate SoLID pseudodata for the
neutron (3He) target, then fit TMD (Sivers/Collins) asymmetries to world + SoLID
pseudodata. Two independent stages: C++/ROOT (event generation, acceptance
folding, binning) → Python (fitting).

**Scope — read this before believing any other document.** This repo is a
cleaned-up extraction from `../LiuSIDIS/SoLID/sidis2020_zwzhao`, and it is
deliberately smaller than its source:

- **Neutron only.** `analysis_proton.C` and `SoLID_SIDIS_NH3.h` are not here.
  `Acceptance/` does carry the NH3 maps, ready for when they arrive.
- **Plotting is curated, not the upstream set.** `plot_kincoverage.py` and
  `seedtest_*.py` are still not here; `code.md` step 7 keeps the arithmetic they
  used, because two of its fudge factors are traps for whatever replaces them.
  What is here, one script/notebook per figure set, each documented in the
  README beside it rather than here: `SIDIS_MUT3_comparison/make_figures.py` +
  `make_gallery.py` (that study's figures), `phicompare/plot-{transversity,sivers}_phicompare.ipynb`
  + `phicompare/errors_plot/plot_errors.py` (the azimuthal-acceptance comparison
  and its error budget), `FOM/plot_fom_solid_vs_sbs.py` +
  `FOM/plot_fom_qtq_vs_theta_grid.py` (the SoLID-vs-SBS figure of merit, both
  drawing their definitions from `FOM/fom_common.py`),
  `data_world/plot-transversity_replica.ipynb` +
  `kinematics/plot_qtq_vs_theta.py` (closed-form kinematic maps, no run
  directory). `start_jupyter.sh` (repo root) launches the notebooks with this
  repo's environment.
- **No fit outputs, no pseudodata.** Everything under a `<rundir>` is produced by
  a run you launch.

`check.md`, `bug.md`, `bug_codex.md` and `runlog_old.md` came across verbatim and
still describe the upstream tree — they name directories and scripts that do not
exist here. Treat them as evidence, not as a map of this repo.

**`README.md`, `physics.md`, `code.md`, this file and
`SIDIS_MUT3_comparison/` (its write-up and figures, not its run directories) are
published** to `github.com/JeffersonLab/evgen_sidis_duke`, together with the
code, the `makefile`, the setup scripts, `Acceptance/`, `data_world/` and
`data_sbs/`. The working notes
below stay in the working tree, so a citation to one is a pointer to evidence,
not to a file a cloned repo will contain.

**Read the right document before working.** This file is operational only —
environment, commands, conventions. Everything else lives elsewhere and is kept
there deliberately:

| file | holds |
|---|---|
| `physics.md` | what the pipeline computes: the formulas, step by step, and which file implements each |
| `code.md` | how it is implemented: entry points, data formats, fast paths, traps |
| `check.md` | settled investigations — `tol`, the g_T estimator, output-dir provenance — with evidence and reproduction steps |
| `data_world/README.md` | the world data: naming, how the fit scripts resolve it, why it is never cut |
| `data_sbs/README.md` | the SBS projection: `kintables/` as the source and what it adds over the ROOT-derived pair, the two vintages and why they are not interchangeable, why `value` is model output that the fits ignore |
| `phicompare/README.md` | the azimuthal-acceptance study: standing conclusions; points at `errors_plot/README.md` for the error-budget figures |
| `phicompare/errors_plot/README.md` | the error budget of the prepared fit inputs: the three-term decomposition, the pairing rule, current results |
| `FOM/README.md` | the SoLID-vs-SBS figure of merit: the pre-CDR Fig. 1 panel rebuilt on `fom.C`'s own bin edges and SBS input, the (x,Q2) and (z,pT) maps, and the (x,Q2) grid of (theta_h, qT/Q) maps — including why the hadron lab angle in that grid is an assumption about phi_h, not a measurement |
| `phicompare_old.md` | the inherited upstream conclusions of that study, frozen |
| `bug.md` | open, actionable problems |
| `bug_codex.md` | a one-off external review (2026-08-18); a record, not a live list — anything still open lives in `bug.md` |
| `runlog.md` | run provenance for this repo, newest first |
| `data_sbs/split_q2.py` | not a doc, but the one script outside the table above: splits the SBS projection finer in Q2 on demand. Its header records why the split fraction cannot be derived from the tables |
| `runlog_old.md` | the inherited upstream run history, frozen |

Do not restate physics or implementation detail here; add it to `physics.md` or
`code.md` and link.

## Environment setup

ROOT 6.40.02 (JLab `module`) and LHAPDF 6.5.6 (env vars) are required before any
C++ binary or Python script. **An agent's shell here is `zsh`, not the login
`tcsh`** — `setup.csh` fails from it with a parse error and exit 126, which
silently short-circuits any `&&` chain. Always use this prefix, in the *same*
shell invocation as the command:

```
source /usr/share/Modules/init/zsh    # module wrapper is present but non-functional without this
source setup.sh
```

`setup.sh` is the bash/zsh port of the original `setup.csh`; keep both in sync if
a version changes. It also sets `PYTHONPATH` for the LHAPDF python bindings
(`lhapdf-config --pydir` is broken upstream).

Not installed by default on this machine:

- `pip install --user pandas`
- `pip install --user "iminuit<2"` — the fit scripts use the v1-only
  `Minuit.from_array_func`; iminuit v2+ removed it.

## Build

```
make O=analysis_neutron     # 3He (neutron), uses SoLID_SIDIS_3He.h
make clean
```

The makefile is generic in `$(O)`; a new target needs a matching `<name>.C` and
its own `SoLID_SIDIS_*.h`. `SoLID_SIDIS_3He.h` includes **`Lsidis3.h` directly**.
Upstream it included `Lsidis.h`, a symlink to `../../Header/Lsidis3.h`, which a
standalone repo cannot do; the intermediate symlink was carried for a while and
removed 2026-08-27.

Toolchain constraints that bite when editing any header (this code predates the
current ROOT/GCC): C++17 is required, `-Wgnu-static-float-init` is Clang-only,
`LHAPDFLIBS` must use `lhapdf-config --cflags --libs` (not `--ldflags`), the 2-arg
`TH2::Integral(binx1,binx2,opt)` is private — use the 4-arg form, and
`<fstream>`/`<cmath>` need explicit includes.

**Stale `.d` files hard-fail the build after a header is removed.** The makefile
auto-generates `<target>.d` and `-include`s it, so a dependency file listing a
header that no longer exists gives
`make: *** No rule to make target 'Lsidis.h', needed by 'analysis_neutron.o'` and
stops — with no hint that the fix is unrelated to your edit. Run `make clean`, or
delete the `.o`/`.d` pair, after removing or renaming any header.

When editing an event-generation loop, use the PDF-deferral pattern
(`GenerateEventKinematics` → cheap cuts → `GetWeightFromCurrentState`) rather than
one-shot `GenerateEvent`; see `code.md`.

## Run

**One run, one directory.** Every stage takes the same `<rundir>` and both reads
and writes there. It is **required everywhere** — there is no default. A
forgotten argument used to mean silently reading or overwriting whichever run was
there last, across three separate directory families. `<rundir>` is created if
missing.

Three inputs come from outside it: `Acceptance/` (SoLID acceptance maps),
`data_world/` (world data, `colworld_{collins,sivers}.dat`) and `data_sbs/` (the
SBS projection, `simsbs_{collins,sivers}.dat`). The two datasets are shared across
all runs and are read from their own directory whatever `<rundir>` you pass —
`WORLDDIR` and `SBSDIR` in the fit scripts. The SBS one is what
`sbs+enhanced3he` pairs with this run's own pseudodata.

`data_world/` was called `data_other/` until 2026-09-09, when the SBS files moved
out into `data_sbs/`; commands in `runlog.md` before that date use the old name.

Inside a run directory, anything that would collide between the two observables
carries a `_collins` / `_sivers` suffix — the convention `data_world/` set.

### 1. Generate pseudodata (C++)

```
./analysis_neutron <opt> <rundir> [phicut] [phiscope] [phiwidth] [acccut] [phisfold]
#   opt 0 = total rate       -> prints only, takes no rundir
#   opt 1 = kinematic bins   -> <rundir>/bin_enhanced_*.dat
#   opt 2 = projection files -> <rundir>/enhancedN*.root
#                            +  <rundir>/enhancedN*_hs.root (per-bin hs + hs_full maps)
#   opt 3 = text tables      -> <rundir>/enhancedNpi{p,m}.csv
#   opt 4 = count table      -> <rundir>/count_N{8,11}{p,m}.dat
```

**opt 4 is independent of 1-3.** It runs its own event scan and reads no bin
file, so it works on a fresh `<rundir>`. It writes `N_acc` on a fixed
(x, Q2, z, pT) grid of 0.01-wide bins, one row per *occupied* cell — the grid is
5.04e8 cells and at most one cell can be filled per accepted event, so the table
is stored and written sparsely. At that width most rows hold a single MC event
and carry ~100% error, which is why `dNacc` and the raw `Nmc` count are written
per row: **the table is meant to be re-binned coarser**, not read row by row.

**`phicut` = number of sectors kept**, evenly spaced and centred on φ = 0;
**`phiwidth` = full width of one sector in degrees, default 24**. Coverage is
`phicut × phiwidth / 360`:

| `phicut` | `phiwidth` | sectors | coverage |
|---|---|---|---|
| 0 / unset | — | — | full 2π |
| 2 | 24 (default) | 0, 180 | 13.33% |
| 4 | 24 (default) | 0, ±90, 180 | 26.67% |
| 6 | 24 (default) | 0, ±60, ±120, 180 | 40.00% |
| 4 | 12 | 0, ±90, 180 | 13.33% |
| 1 | — | legacy alias for 6 | 40.00% |

`phicut=1` is kept as an alias so commands recorded in `runlog_old.md` still
reproduce; prefer writing the count explicitly. `4 × 12°` matches `2 × 24°` in
total coverage but spreads it over four sectors — the pair isolates *where* the
azimuth is sampled from *how much* of it is. **Overlapping configurations are
rejected:** `phiwidth > 360/phicut` exits 1 with the spacing printed, which is
also what stops the old `phicut >= 16` trap (`bug_codex.md` item 12).
**`phiscope`** is `all` (default: cut applies to electron and hadrons alike) or
`FA` (forward angle only, so a large-angle electron is kept at any φ). All three
are printed at startup.

### 2-3. Prepare and fit (Python)

```
./prepare.py    <rundir> [--sbs]   # enhancedNpi{p,m}.csv -> simenhanced3he.dat
./fitcollins.py <opt>    <rundir>  # simenhanced3he.dat -> out-*_collins.dat
./fitsivers.py  <opt>    <rundir>  # simenhanced3he.dat -> out-*_sivers.dat
```

Both fit scripts and `run_fits.sh` take the same optional flags. Each that changes
the result writes to a **suffixed** filename, so a nominal run is never overwritten;
they compose, e.g. `out-enhanced3he_collins_r1lt0.3_x4counts.dat`.

| flag | `run_fits.sh` | does |
|---|---|---|
| `-n` / `--nrep` | `-n` | replicas (default 500) |
| `-s` / `--seed0` | `-s` | first seed; disjoint values give independent ensembles |
| `-w` / `--workers` | `-w` | worker processes |
| `-t` / `--tmdcut R` | `-t` | keep only simulated rows with collinearity R1 < R. **Never cuts the world data** — the filter is inside `fitsim()` and `fitworld()` does not call it. Suffix `_r1lt<R>` |
| `-c` / `--counts F` | `-c` | fit the SoLID pseudodata as if the run had F times the counts, i.e. `stat/sqrt(F)`. For the `*syst` opts the total error is **rebuilt** as `sqrt(stat^2/F + systabs^2 + AUT^2 systrel^2)`, not scaled whole — a systematic does not shrink with beam time. World and SBS are never scaled; refused, not ignored, on any other opt. Suffix `_x<F>counts` |
| `-S` / `--sbsdir DIR` | `-S` | read the SBS projection from `DIR`. Needed because `_DATASETS['sbs']` resolves through `SBSDIR`, **not** through `<rundir>`, so an alternative SBS binning cannot be fitted by passing it as a rundir. No suffix — point the rundir somewhere new instead |

**`--counts` is not a substitute for coverage.** Measured: 4x the counts shrinks the
`gT(u-d)` band to ~0.8 of its value, not 0.5, and the best 4x phi-cut result is
still 1.5x worse than 2pi at nominal luminosity. Why it is 0.8 rather than 0.5 is
open — world-data anchoring, the Collins bimodality and gT non-Gaussianity were each
tested and each fails. See `runlog.md` (2026-09-08).

**`prepare.py` takes no observable argument.** Since 2026-08-31 it writes ONE
`simenhanced3he.dat` carrying all three amplitudes as per-amplitude columns, and
both fit scripts read that same file — `load()` picks the run's amplitude out of
it. `--sbs` switches it to a different job entirely: `sbs01_root/sbs02_root.dat`
-> `simsbs_{collins,sivers}.dat` in `data_sbs/`, reading no SoLID CSV.

Run either fit script with no arguments to list the opts.

Three rules:

- **Re-run `prepare.py` whenever step 1-3 is re-run.** Nothing downstream can tell
  that the CSVs were overwritten in place.
- **`fitcollins.py` and `fitsivers.py` are kept structurally identical** — same
  branches, same `load()`/`_DATASETS`, same replica count, same defaults. Only
  `OBS`, the parameter set and the `tmd.AUT*` call differ. Change one, change the
  other.
- **Datasets load on demand**, through `load(name)`. Six of the nine (`simsbs`,
  `simclas`, `simbase`, `simbasesyst`, `simenhanced`, `simenhancedsyst` — the
  combined proton+neutron sets) are **not in this repo**; their opts stay wired up
  for the proton path and report what is missing rather than raising. Do not
  "fix" them by loading eagerly again: that is what made `world` — which needs
  none of them — fail before the opt was ever examined.

**Naming trap:** the `3he` suffix means **neutron-only**; the *unsuffixed*
`enhanced`/`base` opts are the **combined** proton+neutron sets, which is exactly
why they cannot run yet.

### Directory naming

The suffix names the run's distinguishing condition: `_phifull` (baseline 2π),
`_phi6seg24deg`, `_phi4seg24deg`, `_phi2seg24degFA` (trailing `FA` =
`phiscope=FA`). Runs that vary the newer options extend the same idea — `_4pi`
for `acccut=off`, `_phisfold`/`_phisfull` for the `[phisfold]` choice, `_bin10deg`
for the 36-bin azimuthal histogram — e.g.
`SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg`. The suffix spells out both numbers, so a `phicut=4 phiwidth=12`
run is `_phi4seg12deg`. A `_phifullbin` suffix means the run reused `_phifull`'s
step-1 bins via symlink — **only those pair 1:1 with the baseline**; an own-bins
run re-bins under its own acceptance, so row counts and χ² are not comparable
across runs.

### Figures (the `MUT3` study only)

```
cd SIDIS_MUT3_comparison
./make_figures.py --list     # which figures their run dirs can currently build
./make_figures.py            # all that can be built
./make_figures.py binwidth   # one, by name
```

```
./make_gallery.py <fullrun> <cutrun> --tag=-SUFFIX   # the per-bin pair figures
```

These two cover only `SIDIS_MUT3_comparison/`. **Every plotting script lives in
the directory holding the figures it writes**, and there are seven:

| script | writes | covers |
|---|---|---|
| `SIDIS_MUT3_comparison/make_figures.py` | `estatraw*`, `hs-*` | the `MUT3` estimator study |
| `SIDIS_MUT3_comparison/make_gallery.py` | `hs-*` pair figures | one (2pi, phi-cut) run pair |
| `phicompare/errors_plot/plot_errors.py` | `errors-*` | the error budget across acceptances |
| `FOM/plot_fom_solid_vs_sbs.py` | `fom-solid-vs-sbs*` | SoLID vs SBS figure of merit — see `FOM/README.md` |
| `FOM/plot_fom_qtq_vs_theta_grid.py` | `fom-qtq-vs-theta-grid-*` | the same FOM in (theta_h, qT/Q), one panel per (x,Q2) cell |
| `FOM/plot_native_points.py` | `fom-native-xQ2`, `fom-solidbin-sbspoint-xQ2` | both experiments at their own binning, nothing re-binned or cut |
| `kinematics/plot_qtq_vs_theta.py` | `qtq-vs-theta-hadron*` | qT/Q vs hadron lab angle at one fixed (E, Q2, x, z) — see `kinematics/README.md` |

`dump_sbs.C` (repo root) is not a plotting script but belongs with them: run
from the root, it regenerates `data_sbs/sbs0{1,2}_root.dat` from the upstream
SBS ROOT trees. See `data_sbs/README.md`.

All need the `setup.sh` environment plus `matplotlib`. `kinematics/` is the one
that needs nothing else: it reads no run directory, only its command line.

`make_figures.py` pulls the per-bin `Estat*` branches
through `dump_estat.C`; `make_gallery.py` takes one (full 2pi, phi-cut) run pair
and pulls the `hs_full` maps and the per-bin `MUT3` matrices through
`extract_hs.C` — it needs both runs to carry the **same step-1 bins**, or its
twelve bin indices point at different kinematics in each. Both cache their text
dumps in `SIDIS_MUT3_comparison/.dumps/` and write `.png` + `.pdf` beside the
write-ups that embed them. Both need the `setup.sh` environment plus `matplotlib`.

**A figure whose run directories are absent is skipped, not failed** (`make_figures.py`)
or exits with the missing name (`make_gallery.py`) — the run dirs are gitignored,
so a fresh clone builds nothing until you generate them. The dumps are cached:
delete `.dumps/` after re-running a step 2 or the figures will be redrawn from
stale text.

## Run logging

After any production run of `analysis_neutron`, `prepare.py`, `fitsivers.py` or
`fitcollins.py` — log it in `runlog.md` (newest entry first), **even if not
asked**: command, timing, output locations, and anything notable (bugs hit,
environment issues, unexpected results). When a run changes a study's
conclusions, update `phicompare/README.md` too.

## Interpreting results — the three standing warnings

Full reasoning in `physics.md` and `phicompare/README.md`; these are the ones that get
violated in practice.

1. **Never quote a `fitworld` vs `fitsim` *parameter* comparison as a precision
   statement.** They fix different parameters. Compare bands or g_T.
2. **Improvement factors carry ~±20% run-to-run noise** — three fits of the same
   dataset gave 10.0x, 12.4x, 14.0x. Quote a range.
3. **`tol` (7.04 Collins / 1.5 Sivers) sets every absolute band width** and is a
   calibration, not a derivation. It cancels in error ratios.
