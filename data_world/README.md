# `data_world/` — the world data, shared by every run

World SIDIS data and the fits of it alone. Nothing here is produced by
`analysis_neutron`, and nothing here belongs to one `<rundir>` — that is the
distinction the directory exists to make. `Acceptance/` and `data_sbs/` are the
other two outside-a-rundir inputs.

**Renamed from `data_other/` on 2026-09-09**, when the SBS projection moved out
into `data_sbs/`. The old name meant "everything that is not a run"; once SBS
left, what remained was world data, so the name now says so. Any document or
command still naming `data_other/` predates that.

## Contents

| pattern | what it is |
|---|---|
| `colworld_<obs>.dat` | world data, the reference every fit includes |
| `out-world_<obs>.dat` | the `world` fit opt's output, one row per replica |
| `fitlog-<date>-<time>.txt` | what `run_fits.sh` did |
| `world_old/` | a superseded copy, kept by hand for comparison |
| `plot-transversity_replica.ipynb` | world and SBS fits, old against new |

Anything that would collide between the two observables carries a
`_collins` / `_sivers` suffix. This directory set that rule; the rest of the repo
follows it.

**`_old/` is frozen evidence, never an input.** Nothing in the pipeline reads
`world_old/`; it exists so a "did this change?" question can be answered. Delete
it only when its question is settled for good.

## How the fit scripts find it

`WORLDDIR` in `fitcollins.py`/`fitsivers.py` is `data_world`, resolved
independently of the `<rundir>` you pass — the world data is a fixed reference,
identical for every SoLID run. `SBSDIR` is `data_sbs` and works the same way.

`colworld_collins.dat` has 146 rows, `colworld_sivers.dat` 234. Those set the
`ndof` of every fit: rows + world − free parameters.

**The world data is never cut.** `--tmdcut` filters simulated rows only; the
filter lives inside `fitsim()` and `fitworld()` does not call it. `fitsim()`
asserts the world row count is unchanged, so a regression fails loudly rather
than quietly shrinking the reference and flattering every improvement factor.

## Producing and consuming

```
./run_fits.sh data_world world      # -> data_world/out-world_{collins,sivers}.dat
```

Log every run in `../runlog.md`, newest first.

**Do not quote a `fitworld` vs `fitsim` parameter comparison as a precision
statement** — they fix different parameters (`fitworld` holds `c` fixed,
`fitsim` frees it). Compare bands or g_T. See `../CLAUDE.md`, warning 1.

## The SBS projection is no longer here

It is in `../data_sbs/`, with its own README covering the two vintages, the
`kintables/` source tables, and why the cut and uncut copies are not
interchangeable.
