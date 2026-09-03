# Azimuthal-acceptance comparison

What SoLID's SIDIS neutron (3He) projections lose if the detector only covers
part of the azimuth. Standing conclusions of the study.

## The error budget of the prepared fit inputs

What `prepare.py` writes into `error_tot_<amplitude>`, split into its three terms
and compared across azimuthal-acceptance configurations, one rundir per
configuration. in dir **`errors_plot/`**, script, figures and the full write-up (decomposition, pairing rule, current results)
are there: [`errors_plot/README.md`](errors_plot/README.md).

## The φ-cut fit comparison (the notebooks)

`plot-transversity_phicompare.ipynb` (Collins → transversity $h_1$) and
`plot-sivers_phicompare.ipynb` (Sivers → $f_{1T}^{\perp(1)}$) — the two
notebooks that live in this directory alongside the `data_*` rundirs they read.
Same structure in both: load every fit, build the $x$-dependent band, plot it,
tabulate the error ratio to world, and (transversity only) reduce it to a
tensor-charge number. Each fits **world + one projection**, 500 replicas, never
the projection alone.

| key | run directory | acceptance | binning | bins |
|---|---|---|---|---|
| `world` | `../data_other` | existing world data — **the reference** | — | 146 rows (Collins) / 234 (Sivers) |
| `sbs` | `../data_other` | SBS projection, **stat-only panel** | — | 455 rows |
| `phifull` | `data_phifull` | full 2π (100%) | own | 1660 |
| `phi4seg_fullbin` | `data_phi4seg24deg_phifullbin` | 4 × 24° (26.7% nominal), both arms | reused from `phifull` | 1660 |
| `phi4seg` | `data_phi4seg24deg` | 4 × 24°, both arms | own | 169 |
| `phi4segFA_fullbin` | `data_phi4seg24degFA_phifullbin` | 4 × 24°, forward angle only | reused from `phifull` | 1660 |
| `phi4segFA` | `data_phi4seg24degFA` | 4 × 24°, forward angle only | own | 239 |

**`_fullbin` versus own bins is not a detail** — a `_fullbin` run inherits
`phifull`'s 1660 bins and is comparable row by row; an own-bins run re-bins
under its own acceptance and shares no bin with anything, so it looks *better*
than its `_fullbin` twin at equal acceptance for reasons of bin width, not
physics. **SBS is a reference, not a SoLID configuration**: no systematics
model of its own, so it is stat-only and absent from every stat+syst panel.

### Running it

```
source /usr/share/Modules/init/zsh && source ../setup.sh
jupyter nbconvert --to notebook --execute --inplace plot-transversity_phicompare.ipynb
jupyter nbconvert --to notebook --execute --inplace plot-sivers_phicompare.ipynb
```

Each rebuilds every band from its `out-*.dat` fits on disk — nothing here reruns
`fitcollins.py`/`fitsivers.py`; run those first if a rundir's fit is missing or
stale. Needs `matplotlib`, `pandas`, and `tmd.py` on the path (`sys.path` is set
to the repo root in cell 1).

### The figures

All in `gallery/`, `.pdf` only:

| file | shows |
|---|---|
| `trans-phicompare.pdf` / `sivers-phicompare.pdf` | $xh_1(x)$ / $xf_{1T}^{\perp(1)}(x)$ bands, every run, stat only |
| `trans-phicompare-syst.pdf` / `sivers-phicompare-syst.pdf` | same, stat+syst |
| `trans-doveru-phicompare.pdf` | $-h_1^d(x)/h_1^u(x)$, stat+syst (transversity only) |
| `gt-phicompare.pdf` | truncated tensor charge $g_T$, every run, stat vs stat+syst (transversity only) |

### What it currently shows

Truncated $g_T(u-d)$, $0.05<x<0.6$, statistical only — the single-number version
of "how much does SoLID improve on current knowledge":

| run | $E(g_T^{u-d})$ | world / this |
|---|---|---|
| world | 0.1701 | 1.00× |
| sbs | 0.0395 | 4.31× |
| `phifull` | 0.0107 | **15.86×** |
| `phi4seg_fullbin` | 0.0308 | 5.53× |
| `phi4seg` | 0.0355 | 4.79× |
| `phi4segFA_fullbin` | 0.0262 | 6.49× |
| `phi4segFA` | 0.0299 | 5.69× |

Stat+syst version tops out lower, at **8.71×** for `phifull` — its factor
roughly halves once systematics are added (retaining 55% of the stat-only
value), the largest relative hit of the five. The two `_fullbin` configs barely
move (92%); the two own-bins configs sit in between (66-68%). Consistent with
`errors_plot/README.md`'s finding that Collins is systematics-limited at full
acceptance (73.6% of bins) while a φ cut inflates the statistical term past the
systematics, so the cut configurations have less systematic error left to add.

Sivers has no tensor-charge analogue, so its compact summary is the replica
spread of the fitted parameters themselves. `kt2` is the one to watch — it sets
the transverse-momentum width, which a φ cut degrades most directly. **Do not
read the "vs world" parameter columns as a precision comparison**: `fitworld()` and
`fitsim()` fix *different* parameters (world floats 7, SoLID floats 9), so
individual parameter spreads are not on equal footing even when the observable
itself is far better constrained. The band ratios above are the comparison
that marginalises correctly; the run-to-run parameter column (SoLID configuration
against `phifull`, both `fitsim`) is the one that isolates the φ-cut effect
cleanly.

Three standing warnings apply to every number pulled from these notebooks — see
`../CLAUDE.md`: don't quote a `fitworld` vs `fitsim` *parameter* as a precision
statement (compare bands or $g_T$ instead); improvement factors carry ~±20%
run-to-run noise; `tol` sets every absolute band width and cancels only in
ratios.
