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
- **No plotting.** No notebooks, no `plot_kincoverage.py`, no `start_jupyter.sh`,
  no `seedtest_*.py`. `code.md` step 7 keeps the arithmetic they used, because two
  of its fudge factors are traps for whatever replaces them.
- **No fit outputs, no pseudodata.** Everything under a `<rundir>` is produced by
  a run you launch.

`check.md`, `bug.md`, `bug_codex.md` and `runlog_old.md` came across verbatim and
still describe the upstream tree — they name directories and scripts that do not
exist here. Treat them as evidence, not as a map of this repo.

**`README.md`, `physics.md`, `code.md`, this file and
`SIDIS_MUT3_comparison/` (its write-up and figures, not its run directories) are
published** to `github.com/JeffersonLab/evgen_sidis_duke`, together with the
code, the `makefile`, the setup scripts, `Acceptance/` and `data_other/`. The working notes
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
| `phicompare.md` | the azimuthal-acceptance study's standing conclusions |
| `phicompare_old.md` | the inherited upstream conclusions of that study, frozen |
| `bug.md` | open, actionable problems |
| `bug_codex.md` | a one-off external review (2026-08-18); a record, not a live list — anything still open lives in `bug.md` |
| `runlog.md` | run provenance for this repo, newest first |
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

Only two inputs come from outside it: `Acceptance/` (SoLID acceptance maps) and
`data_other/` (world data, shared across all runs, as
`colworld_{collins,sivers}.dat`).

Inside a run directory, anything that would collide between the two observables
carries a `_collins` / `_sivers` suffix — the convention `data_other/` set.

### 1. Generate pseudodata (C++)

```
./analysis_neutron <opt> <rundir> [phicut] [phiscope] [phiwidth] [acccut] [phisfold]
#   opt 0 = total rate       -> prints only, takes no rundir
#   opt 1 = kinematic bins   -> <rundir>/bin_enhanced_*.dat
#   opt 2 = projection files -> <rundir>/enhancedN*.root
#                            +  <rundir>/enhancedN*_hs.root (per-bin hs + hs_full maps)
#   opt 3 = text tables      -> <rundir>/enhancedNpi{p,m}.csv
```

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
./prepare.py    <collins|sivers> <rundir>   # enhancedNpi{p,m}.csv -> simenhanced3he*_<obs>.dat
./fitcollins.py <opt>            <rundir>   # simenhanced3he*_collins.dat -> out-*_collins.dat
./fitsivers.py  <opt>            <rundir>   # simenhanced3he*_sivers.dat  -> out-*_sivers.dat
```

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

## Run logging

After any production run of `analysis_neutron`, `prepare.py`, `fitsivers.py` or
`fitcollins.py` — log it in `runlog.md` (newest entry first), **even if not
asked**: command, timing, output locations, and anything notable (bugs hit,
environment issues, unexpected results). When a run changes a study's
conclusions, update `phicompare.md` too.

## Interpreting results — the three standing warnings

Full reasoning in `physics.md` and `phicompare.md`; these are the ones that get
violated in practice.

1. **Never quote a `fitworld` vs `fitsim` *parameter* comparison as a precision
   statement.** They fix different parameters. Compare bands or g_T.
2. **Improvement factors carry ~±20% run-to-run noise** — three fits of the same
   dataset gave 10.0x, 12.4x, 14.0x. Quote a range.
3. **`tol` (7.04 Collins / 1.5 Sivers) sets every absolute band width** and is a
   calibration, not a derivation. It cancels in error ratios.
