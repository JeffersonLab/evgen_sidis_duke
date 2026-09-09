# `data_sbs/` — the SBS neutron projection

Everything this repo holds from **SBS E12-09-018** (`n(e,e'h)X`, transversely
polarised ³He). A shared input like the world data: the fit scripts resolve it
here (`SBSDIR`) whatever `<rundir>` you pass, because it is a fixed external
projection, identical for every SoLID run and not a product of one.

**Two moves, both on 2026-09-09.** The SBS files left `data_other/` (which is now
`data_world/`, world data only) for this directory; then everything under
`sbs_root/` was lifted one level up, so this directory is flat. Any path of the
form `data_other/sbs*` or `data_sbs/sbs_root/*` predates that and is stale.

## Layout

```
kintables/                    the SOURCE tables from the collaboration -- see below
kintables.tar.gz              the delivered archive, as received

sbs0{1,2}_root.dat            455 rows, pi+/pi-, the UNCUT projection via ../dump_sbs.C
simsbs_{collins,sivers}.dat   fit-ready, built by ./prepare.py data_sbs --sbs
out-sbs_{collins,sivers}.dat  world+SBS fits, with _r1lt0.3 twins
fitlog-*.txt                  what run_fits.sh did
```

## `kintables/` is the source; the `_root` files are derived from it

The old ROOT-derived dumps are exactly the new 3D tables, merged over beam energy:

```
sbs01_root.dat  233 rows  pi+  =  table3D_piplus11  (123) + table3D_piplus88  (110)
sbs02_root.dat  222 rows  pi-  =  table3D_piminus11 (116) + table3D_piminus88 (106)
```

Checked row by row after sorting on (x, Q², z, p_T): the average bin kinematics
⟨x⟩ ⟨Q²⟩ ⟨z⟩ ⟨p_T⟩ **and** the projected uncertainty agree with
`max|difference| = 0` — bit-exact, not merely close. `sbs0{1,2}_root.dat` carries
no number the tables lack.

### What the tables add

| | |
|---|---|
| **bin edges** | `[xmin,xmax] [zmin,zmax] [ptmin,ptmax]`, widths 0.1 / 0.1 / 0.2. The `_root` files have **none** — which is why `../FOM/plot_native_points.py` falls back to a per-row FOM instead of a density |
| **three more hadrons** | π⁰, K⁺, K⁻ alongside π± |
| **energies kept apart** | `11` = 11.0 GeV, `88` = 8.8 GeV. The `_root` files merged both with no column saying which |
| **the collaboration's asymmetry** | `A_UT` for Collins and Sivers at every bin |
| **per-amplitude errors** | `dA_UT` separately for Collins and Sivers |
| **1D and 2D projections** | nine binnings the 3D tables do not carry |

**`y` is not in the tables, but is recoverable exactly** — each file is one beam
energy, so `y = Q² / (2 M E x)`. Checked against the `_root` files' own `y` on all
233 π⁺ rows: agreement to 1e-5, the printing precision. A merged file cannot be
split back apart, so the per-energy split is a gain.

**The per-amplitude errors are not a reason to switch.** Over all 1074 rows of all
ten 3D tables, `(dSivers − dCollins)/dCollins` has median −0.005% and worst case
1.04%; only 2 rows exceed 1%. The χ² weight changes by at most a factor 1.02.
Expected: both are statistical uncertainties on azimuthal moments of the same
event sample, differing only through moment-matrix conditioning, not through
counts. The reasons to prefer the tables are the bin edges, the asymmetry, the
energy split and the extra hadrons.

### Formats

**`table3D_<hadron><energy>_projected.txt`** — one header line, then whitespace
columns with `[...]` around the edges:

```
[xmin][xmax][zmin][zmax][ptmin][ptmax]  <x> <Q^2> <z> <pT>  A_UT +/- dA_UT (Collins)  A_UT +/- dA_UT (Sivers)
```

6 x-bins × 5 z-bins × 5–6 p_T-bins, only populated cells listed (85–123 rows).
Strip `[`/`]` and read 14 numbers; the `+/-` are literal text.

**`table1D2D_<hadron>_<energy>.txt`** — a 3-line preamble, then nine labelled
sections (`1D Binning in xbj`, `2D binning in xbj, z`, …), each with its own
column header. Section-aware parsing required; there is no single table.

**Filename trap:** the π⁰ 1D2D files are `pi0_11`/`pi0_88`, the 3D files
`pi011`/`pi088`. The underscore is inconsistent upstream; match the actual name.

## The projection exists twice, and the copies are not equivalent

```
sbs0{1,2}.dat    148 + 141 = 289 rows — the TMD-region selection (z, q_T cuts)
                 UPSTREAM ONLY, not in this repo: https://github.com/TianboLiu/LiuSIDIS/tree/master/SoLID/sidis2020/data
sbs0{1,2}_root.dat  233 + 222 = 455 rows — the full projection, tracked here
```

Same experiment, same format, same lowest x (0.1626). **The cut pair is a strict
subset of `sbs0{1,2}_root.dat`** — all 289 rows match a `_root` row to better than
2e-4 in (x, Q², z, p_T); 166 `_root` rows have no partner.

**The cut pair is deliberately not kept here.** Every one of its rows is already
in the tracked `_root` files, so carrying it would duplicate tracked data. Fetch
it from upstream if you need the cut chain; the local copy this repo once held was
byte-identical to the upstream `sbs0{1,2}.dat`, verified before deletion.

The 166 are removed by two cuts:

| cut | effect |
|---|---|
| `z > 0.3` | hard — **0 of the 44 rows with z < 0.3 survive** |
| TMD-region, roughly **q_T ≲ 0.6 Q** with q_T = p_T/z | of the remaining 411, `pT/(z·Q^1.2) < 0.537` reproduces membership for **406, i.e. 98.8%** |

The residual five: one borderline row, and two kinematic points (× both charges)
at the extreme low-x, low-Q² corner — x ≈ 0.163, Q² ≈ 2.34, z ≈ 0.32 and 0.42 —
present despite q_T/Q ≈ 1.3.

**So the two vintages are for different jobs.** The cut pair is the TMD-fit-ready
selection: the q_T ≲ 0.6 Q cut keeps a TMD factorisation analysis inside its
region of validity. The `_root` pair is the full projection, which is what a rate
or figure-of-merit count needs — **summing 1/err² over the cut files silently
imposes a transverse-momentum cut the published figure never applied**, and that
is why the x ≈ 0.2 FOM point once came out 6.9× low (15 rows against 102).

Use `_root` for anything that counts or sums over rows; use the cut pair for TMD
fitting. `prepare.py --sbs` reads the **uncut** `_root` pair only (since
2026-09-02). To run the cut chain, put the upstream `sbs0{1,2}.dat` in a
directory of its own and point the stages at it — since every stage takes a
`<rundir>`, that directory simply *is* the rundir.

## `value` is model output, not data

The raw projections ship `value = 0` — verified, all 455 rows. `prepare.py` fills
it from `tmd.py` at each row's kinematics, so `simsbs_*.dat`'s `value` is **truth
from this repo's model**, not an SBS number. Only `error` is the experiment's.
(The `kintables/` `A_UT` columns *are* the collaboration's own prediction — a
different quantity, and one this pipeline has never used.)

**The fits do not read `value`.** `simulate()` refits the world data and
overwrites `simdata['value']` with the model at that best fit, so the column
reaches nothing but the comparison plots. Only kinematics and `error` matter.

## The `obs` column lies

Every raw projection row is labelled `AUTsivers` regardless of observable — a
legacy label, carried through by `dump_sbs.C` so the formats match.
`prepare.py --sbs` rewrites it to match the file it writes. It bit once: a
superseded `simsbs_collins.dat` carried `obs = AUTsivers` on all 289 rows and a
`value` from an older, smaller Collins parameter set. See `../runlog.md`
(2026-09-01) — the file itself is gone, deleted with the cut chain on 2026-09-09.

## Regenerating the `_root` pair

```
source /usr/share/Modules/init/zsh && source setup.sh      # from the repo root
root -l -b -q dump_sbs.C                                   # -> data_sbs/
root -l -b -q 'dump_sbs.C("/path/to/FOM_comparison", "data_sbs")'
```

`dump_sbs.C` lives at the **repository root** and now defaults to writing here.
It reads the four trees `LiuSIDIS/SoLID/FOM_comparison/fom.C` chains — the same
input the SoLID pre-CDR figure used. `sbs_neutron_pi{p,m}_{8,11}.root` are **not
in this repository**; the `.dat` files are, so nothing downstream needs ROOT.

**Two traps in those ROOT files**, both handled by `dump_sbs.C`:

- The transverse-momentum branch is **`Pt`**, not `pT` — and either way it is
  transverse to the **virtual photon**, not the beam (`../physics.md` step 1).
- **The `y` branch is never filled** — every row of all four files holds the same
  uninitialised ~6.9e-310. `fom.C` never reads `y`, so it went unnoticed.
  `dump_sbs.C` reconstructs `y = Q²/(2 M E x)` with M = 0.93827.

## Producing and consuming

```
./prepare.py  data_sbs --sbs           # sbs0{1,2}_root.dat -> simsbs_{collins,sivers}.dat
./run_fits.sh data_sbs sbs             # -> data_sbs/out-sbs_*.dat        (world + UNCUT SBS)
```

**The `sbs` fit opt is world + SBS, not SBS alone** — ndof 429 = 146 + 289 − 6 for
the cut chain. Never label its output SBS-only.

There is deliberately **no `sbs+enhanced3hesyst`**: `prepare_sbs()` builds no
`fn`, `systabs` or `systrel`, so SBS has no `error_tot`, and pairing its
statistical errors with SoLID's stat+syst would weight SBS up for no reason but
the missing budget. Both fit scripts refuse the opt by name and say so.

`--counts` never scales SBS: more SoLID beam time does not give SBS more events.

Log every run in `../runlog.md`, newest first.

## Scripts

| script | where | does |
|---|---|---|
| `dump_sbs.C` | repo root | the four SBS ROOT trees → `data_sbs/sbs0{1,2}_root.dat` |

The figure-of-merit study that consumes `sbs0{1,2}_root.dat` is in `../FOM/`.
