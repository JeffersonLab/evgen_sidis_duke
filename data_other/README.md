# `data_other/` — everything that does not belong to a single run

The one input directory shared by every `<rundir>`. World data, external
projections, and the fits built from them. Nothing here is produced by
`analysis_neutron`, and nothing here is specific to one run — that is the whole
distinction. `Acceptance/` is the only other outside-a-rundir input.

## Naming convention

Anything that would collide between the two observables carries a
`_collins` / `_sivers` suffix. This directory set that rule; the rest of the repo
follows it.

| pattern | what it is |
|---|---|
| `colworld_<obs>.dat` | world data, the fit reference |
| `sbs0{1,2}_root.dat` | the **uncut** SBS projection, from its ROOT source — see below |
| `sbs_cut/` | the **cut** SBS projection and everything built from it — see below |
| `sim<set>_<obs>.dat` | fit-ready pseudodata: kinematics + `value` + `error` |
| `simsbs_<obs>.dat` | the one of those the fit scripts read **from here**, for any `<rundir>` — see below |
| `out-<opt>_<obs>.dat` | fit output, one row per replica |
| `fitlog-<date>-<time>.txt` | what `run_fits.sh` did |
| `<name>_old/` | superseded copies kept by hand for comparison |

**`simsbs_<obs>.dat` is shared input, like the world data.** Both fit scripts
resolve it here (`_DATASETS['sbs']` uses `WORLDDIR`) no matter which `<rundir>`
is passed, because it is a fixed external projection — identical for every SoLID
run, and not a product of one. That is what lets `sbs+enhanced3he` fit it
alongside a run's own `simenhanced3he.dat`, which the old rundir-relative lookup
made impossible. Build it with `./prepare.py data_other --sbs`.

There is deliberately **no `sbs+enhanced3hesyst`**: `prepare_sbs()` builds no
`fn`, `systabs` or `systrel`, so SBS has no `error_tot`, and pairing its
statistical errors with SoLID's stat+syst would weight SBS up for no reason but
the missing budget. Both fit scripts refuse the opt by name and say so.

**Layout as of 2026-09-02.** The cut SBS vintage and its whole chain — raw
`sbs0{1,2}.dat`, prepared `simsbs_*.dat`, fitted `out-sbs_*.dat`, its fitlog,
`sbs_old/`, and the two scripts that serve it — live in **`sbs_cut/`**. Only the
uncut `sbs0{1,2}_root.dat` remain at this level, because `../FOM/` reads them
from here. Since every stage takes a `<rundir>`, `sbs_cut/` simply *is* that
rundir for the cut chain: `./run_fits.sh data_other/sbs_cut sbs`. World data
stays at this level and is found regardless (`WORLDDIR` in the fit scripts, not
`<rundir>`).

**`prepare.py --sbs` reads the uncut `sbs0{1,2}_root.dat` only** (since
2026-09-02). `sbs_cut/`'s `simsbs_*.dat` were prepared from `sbs0{1,2}.dat`
before that change and are kept as they are; re-preparing that chain would mean
pointing `prepare_sbs()` back at the cut pair.

**`_old/` directories are frozen evidence, never inputs.**
`sbs_cut/sbs_old/`, `world_old/`. Nothing in the pipeline reads them; they exist so a
"did this change?" question can be answered. Delete one only when its question is
settled for good.

## The SBS projection exists twice, and the copies are not equivalent

```
sbs_cut/sbs01.dat  148 rows  π⁺ ┐ 289 total — the TMD-region selection (z, q_T cuts)
sbs_cut/sbs02.dat  141 rows  π⁻ ┘
sbs01_root.dat     233 rows  π⁺ ┐ 455 total — the full projection, from the ROOT trees
sbs02_root.dat     222 rows  π⁻ ┘
```

Both describe the same experiment (E12-09-018) in the same format and reach the
same lowest x, 0.1626. **`sbs_cut/sbs01/02.dat` is a strict subset of `sbs0{1,2}_root.dat`** —
every one of its 289 rows matches a `_root` row to better than 2e-4 in
(x, Q², z, pT); 166 `_root` rows have no partner.

**The 166 missing rows are not arbitrary. They are removed by two cuts:**

| cut | effect |
|---|---|
| `z > 0.3` | hard, no exceptions — **0 of the 44 rows with z < 0.3 survive** |
| a TMD-region cut, roughly **q_T ≲ 0.6 Q** with q_T = pT/z | of the remaining 411 rows, `pT/(z·Q^1.2) < 0.537` reproduces membership for **406, i.e. 98.8%** |

The residual five: one borderline row, and two kinematic points (× both pion
charges) at the extreme low-x, low-Q² corner — x ≈ 0.163, Q² ≈ 2.34, z ≈ 0.32 and
0.42 — which are present despite q_T/Q ≈ 1.3.

**So the two vintages are for different jobs.** `sbs_cut/sbs01/02.dat` is the
TMD-fit-ready selection: the q_T ≲ 0.6 Q cut is what keeps a TMD factorisation
analysis inside its region of validity, which is exactly right for `prepare.py`
and the fits. `sbs0{1,2}_root.dat` is the full projection, which is what a rate
or figure-of-merit count needs — **summing 1/err² over the plain files silently
imposes a transverse-momentum cut the published figure never applied**, and that
is why the x ≈ 0.2 FOM point came out 6.9× low (15 rows against 102).

Use `_root` for anything that counts or sums over rows; use the plain files for
TMD fitting.

`sbs0{1,2}_root.dat` are built by `dump_sbs.C` from the four trees that
`LiuSIDIS/SoLID/FOM_comparison/fom.C` chains — the same input the SoLID pre-CDR
figure used:

```
source /usr/share/Modules/init/zsh && source setup.sh          # from the repo root
root -l -b -q dump_sbs.C                                       # defaults: ../LiuSIDIS/... -> data_other/
root -l -b -q 'dump_sbs.C("/path/to/FOM_comparison", "data_other")'
```

`dump_sbs.C` lives at the **repository root** and writes into this directory. Its
defaults assume it is run from the root; pass both arguments otherwise.

`sbs_neutron_pi{p,m}_{8,11}.root` are **not in this repository**; the committed
`.dat` files are, so nothing downstream needs ROOT or that external tree.

**Two traps in those ROOT files**, both handled by `dump_sbs.C` and both worth
knowing if you ever read them directly:

- The transverse-momentum branch is **`Pt`**, not `pT`. Either way it is
  transverse to the **virtual photon**, not to the beam — see `../physics.md`
  step 1, *What $P_T$ is measured against*.
- **The `y` branch is never filled** — every row of all four files holds the same
  uninitialised value, ~6.9e-310. `fom.C` never reads `y`, so it went unnoticed.
  `dump_sbs.C` reconstructs it as `y = Q2 / (2 M E_beam x)` with `M = 0.93827`,
  which reproduces the `y` column of the existing `sbs01.dat` to the last digit.

## The `obs` column lies

Every raw projection row is labelled `AUTsivers` regardless of observable — a
legacy label, carried through by `dump_sbs.C` so the formats match exactly.
`prepare.py --sbs` rewrites it to match the file it writes. One consequence bit
once already: `sbs_old/simsbs_collins.dat` carries `obs = AUTsivers` on all 289
rows because it was written by a path that never relabelled it, and its `value`
column follows an older, smaller Collins parameter set. See `runlog.md`
(2026-09-01).

## `value` is model output, not data

The raw projections ship `value = 0`; `prepare.py` fills it from `tmd.py` at each
row's kinematics. So `sim*.dat`'s `value` is **truth from a model**, and only
`error` is the experiment's.

**The fits do not read it.** `simulate()` in `fitcollins.py`/`fitsivers.py` refits
the world data and overwrites `simdata['value']` with the model at that best fit,
so a `sim*.dat` `value` column reaches nothing but the comparison plots. That is
why two SBS fits run against different `value` columns agree to minimiser noise.
Only kinematics and `error` matter to a fit.

## Scripts here

| script | where | does |
|---|---|---|
| `dump_sbs.C` | repo root | the four SBS ROOT trees → `data_other/sbs0{1,2}_root.dat` |
| `plot_simsbs_new_vs_old.py` | `sbs_cut/` | `simsbs_*.dat` against `sbs_old/`, → `simsbs-new-vs-old.{png,pdf}` |
| `plot-transversity_replica.ipynb` | here | world and SBS fits, old against new |

Run from this directory with `source /usr/share/Modules/init/zsh && source ../setup.sh`
first. The figure-of-merit study that consumes `sbs0{1,2}_root.dat` lives in
`../FOM/`.

## Producing and consuming

```
./prepare.py  data_other --sbs           # sbs0{1,2}_root.dat -> simsbs_{collins,sivers}.dat
./run_fits.sh data_other world           # -> data_other/out-world_{collins,sivers}.dat
./run_fits.sh data_other sbs             # -> data_other/out-sbs_*.dat  (world + UNCUT SBS)
./run_fits.sh data_other/sbs_cut sbs     # -> sbs_cut/out-sbs_{collins,sivers}.dat  (world + SBS)
```

**The `sbs` fit opt is world + SBS, not SBS alone** — ndof 429 = 146 + 289 − 6.
Never label its output SBS-only.

Log every one of these in `../runlog.md`, newest first.
