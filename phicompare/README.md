# Azimuthal-acceptance comparison

What SoLID's SIDIS neutron (3He) projections lose if the detector covers only
part of the azimuth (the SoLID Light question). Standing conclusions of the study.

**Naming.** A run is named by its directory without the `data_` prefix:
`phi4seg24deg_phifullbin` is `data_phi4seg24deg_phifullbin/`. A `_phifullbin` run
reuses `phifull`'s step-1 bins, so it pairs row by row with `phifull` and with
every other `_phifullbin` run.

## Conclusions at a glance

Truncated $g_T^{u-d}$, world/this (bigger is better), statistical, unless stated.

- **What a φ cut costs.** 4 × 24° on both arms (26.7% per arm): 5.5× against
  15.9× for full 2π, i.e. 2.9× the error. Almost all of it is event count (13.5×
  fewer events per bin); per event it costs about 5%. → "Why less azimuth costs
  almost nothing per event".
- **More beam time is a weak substitute.** 4× the counts: 5.5× → 8.6× (error
  ×0.64, not ×0.5).
- **A forward-angle-only cut** (large-angle electrons keep 2π): 9.8× against 8.6×
  at 4x.
- **Layout matters at equal coverage.**
  - 2 × 48° is about 2× worse than 4 × 24°: Sivers and Collins become degenerate.
  - 4 × 24° on pairs 45° apart loses 8% on $g_T$ and 27% on Sivers $d$: it
    samples the hadron's lab azimuth badly at high $p_T$.
  - Use three or more evenly spaced sectors. → "Where the azimuth is sampled",
    "Why layout matters at high $p_T$".
- **Target spin direction.**
  - With three or more evenly spaced sectors, no spin angle and no split between
    angles changes anything: derived, and measured with 4 × 24° at spin 0 + 45.
  - For 2 × 48°, splitting between spin 0 and 90 removes the $\phi_S$ degeneracy
    but not the high-$p_T$ one, and stays worse than 4 × 24°.
  - → "Why no spin angle can help 4 × 24°", "When a spin split does help".
- **Compare layouts with the fit**, or with $\sum(A_{UT}/\sigma)^2$ per $p_T$ bin.
  Event counts, $\sum 1/\sigma^2$ and all-bin medians of the per-event error have
  each ranked layouts wrongly here.
- **Binning.** Use `_phifullbin` runs for the φ-cut effect: own bins alone cost
  15%. About 800 bins saturate; more buy nothing.
- **SBS in the fit** adds nothing at full 2π. With 4 × 24° it recovers about 1/6
  of the loss at 1x counts (5.5× → 6.5×), but only 3% at 4x (8.6× → 8.9×).
- **R1 < 0.3** removes most high-$p_T$ rows and reverses some rankings: the
  45°-pair and 2 × 48° spin-split layouts beat 4 × 24° under it.
- **$P_h < 3$ GeV** costs a factor 1.19 on $g_T$ for 4 × 24° at 4x (8.6× → 7.2×)
  and 1.17 for its FA variant (9.8× → 8.4×), exactly the 28% of statistical weight
  it removes, but triples the Sivers `kt2` spread. → "The hadron-momentum cut".
- **The stat+syst panels are not quotable.** The per-bin systematic is treated as
  uncorrelated, so it dilutes as $1/N_{\rm bins}$.
- **$Q^2$ changes no ratio here.** Quote $Q^2$ = 2.4 GeV² with any absolute
  value.
- **SBS helps Sivers at high $x$ but not Collins:** the depolarisation factor ε.

## The error budget of the prepared fit inputs

What `prepare.py` writes into `error_tot_<amplitude>`, split into its three terms
and compared across azimuthal-acceptance configurations, one rundir per
configuration. Script, figures and the full write-up (decomposition, pairing
rule, current results) are in [`errors_plot/README.md`](errors_plot/README.md).

## The φ-cut fit comparison (the notebooks)

Two notebooks draw every study: `plot-transversity_phicompare.ipynb` (Collins →
transversity $h_1$, tensor charge $g_T$) and `plot-sivers_phicompare.ipynb`
(Sivers → $f_{1T}^{\perp(1)}$, parameter spreads). They are kept structurally
identical, like `fitcollins.py`/`fitsivers.py`: change one, change the other. Each
loads a study's fits, builds the $x$-dependent bands, plots them, and tabulates the
error ratio to world. Every fit is **world + one projection**, 500 replicas, never
the projection alone.

**A study is one input file, `gallery/input-<study>.csv`**, one row per curve. A study's
name starts with the fit family it draws, `enhanced3he-` for every study so far, and
every output file carries the full name:

| column | meaning |
|---|---|
| `run` | run directory without `data_`; `world` / `sbs` for `../data_world` / `../data_sbs` |
| `fit` | `enhanced3he`, `sbsenhanced3he`, `world` or `sbs` |
| `counts` | 1, or 4 for the `-c 4` fit (`_x4counts`) |
| `cut` | `-`, or the fit's cut suffixes without the underscore, joined by `+` in the order the fit scripts append them: `r1lt0.3` (`-t 0.3`), `phlt3` (`-p 3`), `r1lt0.3+phlt3`. A new fit-script cut needs no notebook change; a misordered or mistyped token names a missing file and the notebook stops there |
| `color`, `label` | a named matplotlib colour (no `#`, which starts a comment), and the descriptive legend text |

- The rows set the drawing order. A `# title:` line adds a LaTeX fragment to the
  band-figure titles. A `# note:` line is printed along the bottom of every figure;
  write it as plain text, since unicode such as π and × works there, while math
  mode drops spaces. Other `#` lines are comments.
- **In a `label`, spaces inside `$\rm …$` are dropped** (`SoLID Light` renders as
  "SoLIDLight"). Write `~` for each space.
- **A later row with the same `run` and `fit` as an earlier row is that row's
  twin**, its 4x or cut version. It is drawn as the dashed edges of its band,
  and a separate table ratios it to its base row.
- Each entry is named in the tables by its run plus the fit-file suffixes, e.g.
  `phi4seg24deg_phifullbin_x4counts` or `sbs+phifull`, so a row names the file it
  came from.
- A stat+syst panel appears only when the study has stat+syst fits on disk.

The studies:

| study | question | fits |
|---|---|---|
| `enhanced3he-main` | the default: the 4 × 24° forward-angle-only layout (full large-angle coverage) at 4x against full 2π at 1x, with its $P_h<3$ GeV twin | world, `phifull` (1x); `phi4seg24degFA_phifullbin` (4x) with a `phlt3` twin |
| `enhanced3he-phlt3` | the 4 × 24° cut and its forward-angle-only variant at 4x against full 2π at 1x, and what a $P_h<3$ GeV cut costs the former | world, SBS, `phifull`; `phi4seg24deg_phifullbin` (4x) with a `phlt3` twin, `phi4seg24degFA_phifullbin` (4x) |
| `enhanced3he-x4counts` | what 4× the counts buys, on three binnings | `phifull`; `phi4seg24deg_phifullbin`, `phi4seg24deg`, `phi4seg24deg_countbin800`, each at 1x with a 4x twin |
| `enhanced3he-r1lt0.3` | what the R1 < 0.3 cut costs | SBS, `phifull`, `phi4seg24deg_phifullbin` (4x), each with an R1-cut twin |
| `enhanced3he-morebin` | the binning alone | `phifull`, `phifull_countbin1e6` |
| `enhanced3he-spin` | how the spin orientation changes each φ-cut layout | world, SBS, `phifull` (1x); `phi4seg24deg`, `phi4seg24degdiag`, `phi4seg24deg2spin`, `phi2seg48deg`, `phi2seg48deg2spin`, all `_phifullbin` at 4x |
| `enhanced3he-sbscombined` | SoLID + SBS in one fit, stat only | `sbs+phifull` (1x), `sbs+phi4seg24deg_phifullbin` and `sbs+phi4seg24deg` (4x) |

2π and SBS stay at 1x in `enhanced3he-phlt3`: 2π is the reference the cut is measured against,
and `--counts` never scales SBS (more SoLID beam time gives SBS no more events).

The runs:

| run | acceptance | bins |
|---|---|---|
| `../data_world` | existing world data, **the reference** | 146 rows (Collins) / 234 (Sivers) |
| `../data_sbs` | SBS projection, **stat-only panel** | 455 rows |
| `phifull` | full 2π (100%) | 1660, own |
| `phi4seg24deg_phifullbin` | 4 × 24° (26.7%), both arms | 1660 |
| `phi4seg24degFA_phifullbin` | 4 × 24°, forward angle only (large-angle e⁻ keeps 2π) | 1660 |
| `phi2seg48deg_phifullbin` | 2 × 48° (26.7%), both arms | 1655 (5 singular bins dropped) |
| `phi4seg24degdiag_phifullbin` | 4 × 24° on the pairs 0/180 and 45/−135 (26.7%), both arms | 1660 |
| `phi4seg24deg2spin_phifullbin` | 4 × 24°, beam time split between target spin 0° and 45° | 1659 (bin 134 singular) |
| `phi2seg48deg2spin_phifullbin` | 2 × 48°, beam time split between target spin 0° and 90° | 1657 (3 singular bins dropped) |
| `phi4seg24deg` | 4 × 24°, both arms | 169, own |
| `phi4seg24degFA` | 4 × 24°, forward angle only | 239, own (in no current study) |
| `phi4seg24deg_countbin800` | 4 × 24°, both arms | 806, from the count table |
| `phifull_countbin1e6` | full 2π | 19074, from the count table |

**`_phifullbin` versus own bins is not a detail.** A `_phifullbin` run inherits
`phifull`'s 1660 bins and is comparable to it row by row. An own-bins run
re-bins under its own acceptance and shares no bin with anything, so a
`phifull`-vs-own-bins number mixes the φ-cut effect with a pure binning effect.

**How much is binning rather than acceptance** can be read off directly, since
an own-bins run and its `_phifullbin` twin have the *same* acceptance and differ
only in binning:

| pair (same acceptance) | stat | stat+syst |
|---|---|---|
| `phi4seg24deg` / `phi4seg24deg_phifullbin` | **1.15×** | **1.57×** |
| `phi4seg24degFA` / `phi4seg24degFA_phifullbin` | **1.14×** | **1.57×** |

(1.00 would mean binning costs nothing; these are $E(g_T^{u-d})$ ratios.) So
~15% of the apparent φ-cut cost in a `phifull`-vs-own-bins stat comparison is
bin coarsening, and on Sivers $\langle k_T^2\rangle$ it is **40%** (5.61 against
4.02). **Use the `_phifullbin` runs for the φ-cut effect.**

The coarsening loss is real information, not an artefact: 169 bins average over
shape the fit could otherwise use. Going the other way, 1660 → 19074 bins changes
$\langle k_T^2\rangle$ by a factor 0.999, i.e. nothing (see "The binning
comparison" below). 1660 bins already resolve the shape; only coarsening below it
costs.

**Direction, corrected 2026-09-07:** an earlier version of this file said an
own-bins run looks *better* than its `_phifullbin` twin. It looks **worse**:
`phi4seg24deg` reaches 4.79× against `phi4seg24deg_phifullbin`'s 5.53×, and
`phi4seg24degFA` 5.69× against 6.49×. The same holds for $g_T$ and six of the
seven Sivers parameters.

**SBS is a reference, not a SoLID configuration**: no systematics model of its
own, so it is stat-only and absent from every stat+syst panel.

**The stat+syst panels of this comparison are not reliable, and matched
binning does not save them.** The per-bin systematic is treated as
uncorrelated, so it dilutes as $1/N_{\rm bins}$. That suppresses a
systematics-limited run's error (`phifull`) far more than a stat-limited one's
(the φ-cut runs). The stat-only panels are sound. Details, numbers and the
correction are in "The binning comparison" below; the own-bins runs carry an
additional, separate distortion on top.

### Running it

```
./run_phicompare.sh                  # every gallery/input-*.csv, both notebooks
./run_phicompare.sh enhanced3he-x4counts enhanced3he-r1lt0.3   # just these
```

It sources the environment itself and runs both notebooks for each study in
parallel, with `PHICOMPARE_STUDY=<study>`. The executed copies are discarded
except for `enhanced3he-main`, which runs last and in place, so the notebooks on disk always
show it. The six studies take about 15 min on a 4-core machine. For an
interactive look, open a notebook and set `STUDY` in its first code cell.

Nothing here reruns `fitcollins.py`/`fitsivers.py`: every band is rebuilt from the
`out-*.dat` fits on disk, so run those first if a rundir's fit is missing or
stale. Needs `matplotlib`, `pandas`, and `tmd.py` on the path (`sys.path` is set
to the repo root in the first code cell).

**Adding a study** = writing `gallery/input-<name>.csv`; no code changes.

### The outputs

Everything in `gallery/`, every name ending in the study:

| file | shows |
|---|---|
| `input-<study>.csv` | the study definition (input, hand-written) |
| `trans-phicompare-<study>.pdf` / `sivers-phicompare-<study>.pdf` | $xh_1(x)$ / $xf_{1T}^{\perp(1)}(x)$ bands, every entry, stat only; lower panel Error(world)/Error |
| `trans-phicompare-<study>-syst.pdf` / `sivers-phicompare-<study>-syst.pdf` | same, stat+syst (not for `enhanced3he-sbscombined`, which has no syst fit) |
| `trans-doveru-phicompare-<study>.pdf` | $-h_1^d(x)/h_1^u(x)$, stat+syst where it exists, else stat |
| `gt-phicompare-<study>.pdf` | truncated tensor charge $g_T$, every entry, stat vs stat+syst, with Error(world)/Error panels |
| `trans-tables-<study>.md` / `sivers-tables-<study>.md` | every table the notebook printed for that study: fits loaded, parameters, Error(world)/Error, twin ratios, $g_T$ (transversity) or parameter-spread ratios (Sivers). Regenerated, never edited |

**Each band figure is drawn at one $Q^2$, 2.4 GeV²**, named in `Q2LIST` and
labelled on the panel. The plotting loops over that list, so extra $Q^2$ can be
added back by editing the one line; further entries appear as central curves in
lighter, thinner strokes (weight rather than linestyle, since solid/dashed already
carries $u$/$d$) with the error band on the first only. $u$ and $d$ are labelled on
the curves themselves, each placed by the **sign** of its own lobe, so it reads
correctly for transversity ($u>0$, $d<0$) and for Sivers, where the signs are
reversed.

Only one $Q^2$ is drawn because **nothing in the comparison depends on it** — see
"Why the error ratios do not depend on $Q^2$" below.

The *curves* do move with $Q^2$, by 1.0× to 4.4× the SoLID band half-width across
$0.1 < x < 0.6$; they look close together only because the axis spans $\pm0.45$
while the shifts are $\sim0.03$. **Quote the $Q^2$ with any $g_T$ or band value.**
Full reasoning in `../physics.md`, step 5, "Neither distribution has a $Q^2$
evolution of its own".

With eight curves the `enhanced3he-spin` band figures' legends are crowded; the tables and the
$g_T$ figure are the easier read.

### What it currently shows

Truncated $g_T(u-d)$, $0.05<x<0.6$, statistical only — the single-number version
of "how much does SoLID improve on current knowledge". The `enhanced3he-phlt3` and `enhanced3he-spin`
studies show the 4x column for the φ-cut runs; the 1x column is the same runs' nominal fits
(`out-enhanced3he_collins.dat`; the `enhanced3he-x4counts` study shows three of them).

| run | $E(g_T^{u-d})$, 1x | world / this, 1x | world / this, 4x |
|---|---|---|---|
| world | 0.1701 | 1.00× | — |
| SBS | 0.0395 | 4.31× | — |
| `phifull` | 0.0107 | **15.86×** | — |
| `phi4seg24deg_phifullbin` | 0.0308 | 5.53× | 8.62× |
| `phi4seg24degFA_phifullbin` | 0.0262 | 6.49× | **9.79×** |
| `phi2seg48deg_phifullbin` | 0.0619 | 2.75× | 3.99× |
| `phi4seg24degdiag_phifullbin` | 0.0342 | 4.97× | 7.89× |
| `phi4seg24deg2spin_phifullbin` | 0.0299 | 5.69× | 8.80× |
| `phi2seg48deg2spin_phifullbin` | 0.0419 | 4.06× | 6.51× |
| `phi4seg24deg` (own bins) | 0.0355 | 4.79× | 7.71× |
| `phi4seg24degFA` (own bins) | 0.0299 | 5.69× | — |

The stat+syst version tops out lower, at **8.71×** for `phifull`: its factor
roughly halves once systematics are added (retaining 55% of the stat-only value),
the largest relative hit of any run. `phi4seg24deg_phifullbin` and
`phi4seg24degFA_phifullbin` barely move (92%), and the two own-bins runs sit in
between (66-68%). That matches `errors_plot/README.md`'s finding that Collins is
systematics-limited at full acceptance (73.6% of bins), while a φ cut inflates
the statistical term past the systematics, so the cut configurations have less
systematic error left to add. The stat+syst warning above applies to all of it.

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

### The hadron-momentum cut $P_h < 3$ GeV (study `enhanced3he-phlt3`)

`fitcollins.py`/`fitsivers.py -p 3` keeps the bins whose bin-mean pion momentum
$|P_h| = \sqrt{(z\,y\,E_{\rm beam})^2 - m_\pi^2}$ is below 3 GeV (`../code.md`,
step 6). It is a **bin-level** cut: a bin straddling 3 GeV is kept or dropped
whole on its mean, so this measures the sensitivity, not an event-level momentum
threshold (that would be `pimin` in `SoLID_SIDIS_3He.h` and a regenerated run).

On `phi4seg24deg_phifullbin` it drops 455 of 1660 bins, 420 of them at 11 GeV.
The dropped bins are the high-$z$, high-$y$ ones: 70% of the bins with $z>0.5$ go,
1% of those with $z<0.4$, and 48% of those with $p_T>0.6$ GeV (mean $z$ 0.55
dropped against 0.40 kept, mean $p_T$ 0.46 against 0.33 GeV). Together they carry
28% of the Collins $\sum 1/\sigma_{\rm stat}^2$. On
`phi4seg24degFA_phifullbin` it keeps 1196 of 1660 bins, and the dropped ones again
carry 28% of the weight.

| $g_T^{u-d}$ at 4x | $E$, no cut | $E$, $P_h<3$ | world/this | cut / no cut |
|---|---|---|---|---|
| 4 × 24°, stat | 0.0197 | 0.0235 | 8.62× → 7.23× | 1.19 |
| 4 × 24°, stat+syst | 0.0246 | 0.0306 | 6.90× → 5.55× | 1.24 |
| 4 × 24° FA, stat | 0.0174 | 0.0203 | 9.79× → 8.37× | 1.17 |
| 4 × 24° FA, stat+syst | 0.0225 | 0.0274 | 7.55× → 6.20× | 1.22 |

**On $g_T$ it costs statistics and nothing else:** $1/\sqrt{1-0.28} = 1.18$
against the measured 1.19 (4 × 24°) and 1.17 (FA). Losing the high-$z$ bins does
not hurt the transversity extraction beyond their share of the event weight, and
the forward-angle-only layout loses nothing extra: FA keeps its lead over 4 × 24°
under the cut (8.37× against 7.23×). By $x$, the $h_1^u$ error grows 1.09–1.17×
for $x \ge 0.2$ and the $h_1^d$ error most at $x \approx 0.1$ (1.24×; 1.27× for
FA).

**Sivers `kt2` is the exception:** its replica spread grows 3.06× (stat) and 2.35×
(stat+syst), and 3.01× and 2.30× for FA; every other Sivers parameter moves
0.93–1.14× (up to 1.12× for FA). Half the $p_T > 0.6$ GeV bins are gone, and those
bins carry the $p_T$ width.

The cut fits also exist, undrawn, for `phifull` (1x, 1223 of 1660 bins kept),
`phi4seg24deg` (own bins, 4x, 126 of 169) and `phi4seg24degFA_phifullbin` at 1x,
as `out-*_phlt3[_x4counts].dat`. Add a `phlt3` row to an input file to draw them.

## Where the azimuth is sampled, at equal coverage — why 2 × 48° loses

`phi2seg48deg_phifullbin` (2026-09-18) keeps two sectors of 48°, centred on 0°
and 180° (−24°..24° and |φ| > 156°), on both arms: **26.7%, exactly the coverage
of 4 × 24°**, on the same `phifull` bins. It came out about **half as precise**.
Truncated $g_T^{u-d}$, world / this:

| run | stat, 1x | stat, 4x | stat+syst, 4x |
|---|---|---|---|
| `phi4seg24deg_phifullbin` | 5.5× | 8.6× | 6.9× |
| `phi4seg24degFA_phifullbin` | 6.5× | 9.8× | 7.6× |
| `phi4seg24degdiag_phifullbin` | 5.0× | 7.9× | 6.6× |
| `phi4seg24deg2spin_phifullbin` | 5.7× | 8.8× | 7.1× |
| `phi2seg48deg2spin_phifullbin` | 4.1× | 6.5× | 5.3× |
| `phi2seg48deg_phifullbin` | **2.7×** | **4.0×** | **3.8×** |

The loss is heaviest in $d$ — $g_T^d$ 6.0× against 15.4× at 4x, and the Sivers
$d$ band at $x = 0.2$ 6.5× against 17.1× at 1x — i.e. in exactly the quantity a
neutron target is there to measure. A factor 2 is far outside the ±20%
run-to-run noise.

**It is not acceptance.** Bin by bin on the shared bins (1655 finite), 2 × 48°
collects **more** events than 4 × 24°, yet its errors are larger:

| per bin, `phi2seg48deg_phifullbin` / `phi4seg24deg_phifullbin` | median | 16–84% |
|---|---|---|
| `Nacc` | **1.60** | 0.44–3.03 |
| `stat_collins` | **1.84** | 0.96–5.0 |
| `stat_sivers` | **1.80** | 0.83–10 |
| `stat_pretzelosity` | **0.80** | 0.45–4.6 |

Pure counting would give $1.60^{-1/2} = 0.79$. Pretzelosity gets that; Collins
and Sivers get 1.8.

**$\sigma\sqrt{N_{\rm acc}}$ is the per-event error** -- what a bin's error
would be if every bin held the same number of events, i.e. what one accepted
event is worth. Every statistical error in `../SoLID_SIDIS_3He.h`
(`AnalyzeEstatUT3`: `Estatraw_diag`/`Estatraw_prop`, then `Estat_prop`) is

$$\sigma_a \;=\; \frac{\sqrt{\Omega\,C_{aa}/N_{\rm acc}}}{f_n\,P_{^3\!He}\,P_n},
\qquad C = {\rm MUT3}^{-1}$$

so multiplying by $\sqrt{N_{\rm acc}}$ cancels the only luminosity-dependent
factor and leaves $\sqrt{\Omega C_{aa}}/(f_n P_{^3\!He} P_n)$: the **azimuthal
geometry** through $C_{aa}$, which is what a φ cut changes, times the ³He
**dilution and polarisation**, which it does not. (Step 1 of the derivation below
traces this through the code line by line.)

Read it as a ratio between runs, never as an absolute. All these runs share
`phifull`'s bins, so $f_n$ is the same bin by bin and cancels in a ratio,
leaving the geometry alone -- which is why the ratios below reproduce the
$\sqrt{C_{aa}}$ ratios measured from the inverted matrix further down. The
absolute value is dominated by $1/(f_n \cdot 0.516)$ with $f_n \approx 0.278$
(median on `phifull`, see `errors_plot/README.md`): perfect azimuthal
coverage would give $\sqrt{2}/(f_n \cdot 0.516) \approx 9.9$, which is why
`phifull` sits just above it at 11.2.

Median over bins, larger meaning each event is worth less:

| run | Collins | Sivers | pretzelosity |
|---|---|---|---|
| `phifull` | 11.2 | 11.4 | 11.2 |
| `phi4seg24deg_phifullbin` | 13.0 | 12.7 | 13.0 |
| `phi4seg24degFA_phifullbin` | 12.7 | 12.7 | 12.8 |
| `phi2seg48deg_phifullbin` | **26.1** | **30.1** | **14.0** |

Four sectors cost ~15% per event against full 2π on this median; two sectors
cost more than **2×** on Collins and Sivers, and almost nothing on pretzelosity.

**Mechanism: two opposite sectors cannot tell Collins from Sivers.** The three
amplitudes are separated in the moment matrix by their azimuthal dependences,
$\sin(\phi_h+\phi_S)$ (Collins), $\sin(\phi_h-\phi_S)$ (Sivers) and
$\sin(3\phi_h-\phi_S)$ (pretzelosity). $\phi_S$ is the target-spin azimuth
measured from the lepton plane, so it is set by the electron's lab azimuth. With
the electron only near 0° or 180°, $\phi_S$ sits only near 0° or 180° (the
target-spin flip adds another 180°, so nothing new). There
$\sin(\phi_h+\phi_S)$ and $\sin(\phi_h-\phi_S)$ are the same function up to sign,
so the two columns become nearly degenerate and both errors blow up. Pretzelosity
escapes because its $3\phi_h$ frequency stays distinct. With 4 × 24° the stripes
at 0/180° and at ±90° pull the Sivers–Collins overlap in opposite directions and
cancel (quantified below). The limiting case is visible in step 2: `MUT3` went
**singular in 4 bins** (plus one non-finite), which the 4 × 24° run on the same
bins never did — those are the 5 rows `prepare.py` dropped.

**Checked directly in the inverted `MUT3`** (2026-09-19, `mut3corr.C` in this
directory: `root -l -b -q 'mut3corr.C("data_<run>","out.txt",20)'`, every 20th
`enhancedN11p` bin, 40 bins per run). It builds the same matrix
`../SIDIS_MUT3_comparison/extract_hs.C` does, inverts it, and reads off
$C = G^{-1}$: $\sqrt{C_{aa}}$ is the per-event error on amplitude $a$ and
$C_{ab}/\sqrt{C_{aa}C_{bb}}$ is how far two amplitudes are mixed.

| run | median \|corr(Collins, Sivers)\| | cond($G$) | $\sqrt{C_{aa}}$ vs `phi4seg24deg_phifullbin`: Siv / Col / pretz |
|---|---|---|---|
| `phifull` | 0.26 | 2.1 | 0.96 / 0.94 / 0.93 |
| `phi4seg24deg_phifullbin` | 0.39 | 3.9 | 1.00 / 1.00 / 1.00 |
| `phi4seg24degFA_phifullbin` | 0.38 | 3.5 | 1.00 / 1.00 / 1.00 |
| `phi4seg24degdiag_phifullbin` | 0.39 | 2.8 | 1.08 / 1.04 / 0.99 |
| `phi4seg24deg2spin_phifullbin` | 0.41 | 3.9 | 1.00 / 1.00 / 1.00 |
| `phi2seg48deg2spin_phifullbin` | 0.28 | 2.3 | 0.97 / 0.95 / 0.94 |
| `phi2seg48deg_phifullbin` | **0.91** | **23.2** | **2.30 / 2.26 / 1.00** |

Collins and Sivers are 91% correlated in the median 2 × 48° bin (0.999 at
worst) against 39% in 4 × 24°, and the inversion alone inflates their per-event
errors by 2.3× while leaving pretzelosity at exactly 1.00. That reproduces the
$\sigma\sqrt{N_{\rm acc}}$ ratios measured above from the prepared fit inputs
(2.37 Sivers, 2.01 Collins, 1.08 pretzelosity), so **for `phi2seg48deg_phifullbin`
the degeneracy accounts for the whole loss**. These are medians over all bins,
dominated by low $p_T$; for the 45°-pair run and the 2 × 48° spin split the
medians look fine and hide a high-$p_T$ loss (see "Why layout matters at high
$p_T$").

**One limit on the claim.** The gap closes under the R1 < 0.3 cut ($E(g_T^{u-d})$
0.0663 against 0.0653 at 1x): the cut removes most of what 4 × 24° had over
2 × 48°, and costs 2 × 48° almost nothing. Run provenance: `../runlog.md`,
2026-09-18.

**Four sectors on pairs 45° apart** (`phi4seg24degdiag_phifullbin`, 2026-09-21)
keep the same four 24° sectors on the pairs 0/180 and 45/−135, the same coverage
and sector count as `phi4seg24deg_phifullbin`. The all-bin medians barely move
(correlation 0.39, per-event errors 1.08 / 1.04 / 0.99), yet the fits lose 8% on
$g_T$ and **27% on Sivers $d$** (23.0× against 31.6× at 4x), with 15% *more*
events per bin; under R1 < 0.3 the run comes out *ahead* (4.5× against 3.7× at
4x). Both follow from one mechanism: at high $p_T$ the Sivers angle becomes the
hadron's lab azimuth, and these hadron sectors sample it badly. See "Why layout
matters at high $p_T$". (Read on 2026-09-21 as "the count of $\phi_S$ values, not
their spacing, is what matters". That reading was wrong; see below.)
Provenance: `../runlog.md`, 2026-09-21.

**A second spin setting on 4 × 24° buys nothing** (2026-09-22).
`phi4seg24deg2spin_phifullbin` keeps the even 4 × 24° sectors and splits the
beam time equally between target spin at 0° and at 45°, so its $\phi_S$ values are
$\{0, 45, 90, 135\}$ mod 180 instead of $\{0, 90\}$. Per-event errors are
**1.00 / 1.00 / 1.00** in `mut3corr.C`, with the same Nacc and a correlation of
0.41 against 0.39, and every fit ratio is within 3% of the spin-0 run:

| world / this | stat 1x | stat 4x | stat+syst 4x | stat 1x R1<0.3 | stat 4x R1<0.3 |
|---|---|---|---|---|---|
| $g_T^{u-d}$, `phi4seg24deg_phifullbin` | 5.5 | 8.6 | 6.9 | 2.6 | 3.7 |
| $g_T^{u-d}$, `phi4seg24deg2spin_phifullbin` | 5.7 | 8.8 | 7.1 | 2.6 | 3.6 |
| Sivers $d$ ($x=0.2$), `phi4seg24deg_phifullbin` | 17.1 | 31.6 | 25.4 | 6.9 | 10.2 |
| Sivers $d$ ($x=0.2$), `phi4seg24deg2spin_phifullbin` | 17.2 | 31.8 | 25.4 | 7.0 | 10.3 |

The null is not a spin setting that failed to act. In the `hs_full` maps
(`enhancedN11p`, bins 100 and 600, 15° slices of $\phi_S$) the spin-0 run has four
stripes at 0, ±90° and 180°, each with 12–13% of the weight. The split run has
eight stripes with 6–7% each: the same four plus ±45° and ±135°. So more
distinct $\phi_S$ values do not help in themselves.

**Why: the mixing is set by $\langle\cos 2\phi_S\rangle - \langle\cos 2\phi_h\rangle$,
not by how many $\phi_S$ values survive.** Averaged over a bin's accepted events,
$\langle\sin(\phi_h-\phi_S)\sin(\phi_h+\phi_S)\rangle = \tfrac12(\langle\cos 2\phi_S\rangle - \langle\cos 2\phi_h\rangle)$,
and both diagonal terms $\langle\sin^2\rangle$ sit at 0.50. So the Sivers–Collins
correlation is simply $\langle\cos 2\phi_S\rangle - \langle\cos 2\phi_h\rangle$.
Medians over the same 40 `enhancedN11p` bins as `mut3corr.C`:

| run | $\langle\cos 2\phi_S\rangle$ | $\langle\cos 2\phi_h\rangle$ | difference | measured correlation |
|---|---|---|---|---|
| `phi4seg24deg_phifullbin` | +0.01 | +0.30 | −0.29 | −0.23 |
| `phi4seg24deg2spin_phifullbin` | −0.00 | +0.30 | −0.30 | −0.26 |
| `phi4seg24degdiag_phifullbin` | +0.49 | +0.13 | +0.36 | +0.39 |
| `phi2seg48deg_phifullbin` | +0.89 | +0.01 | +0.88 | +0.90 |

Each result follows from where the $\phi_S$ stripes sit:
- **4 × 24° at spin 0:** stripes at 0/180° give $\cos 2\phi_S = +1$ and stripes
  at ±90° give −1, so they cancel.
- **At spin 45°:** the stripes move to ±45° and ±135°, where $\cos 2\phi_S = 0$.
  That is zero again, so mixing in spin 45 cannot change anything.
- **$\phi_h$ does not move with the spin**, since it is measured from the lepton
  plane, so $\langle\cos 2\phi_h\rangle$ stays at 0.30.
- **2 × 48°** keeps only the +1 stripes, which gives the near-total degeneracy.
- **The 45°-pair layout** keeps two +1 stripes and two zeros.

A spin setting is worth beam time only if it moves $\langle\cos 2\phi_S\rangle$
towards $\langle\cos 2\phi_h\rangle$; for the even 4 × 24° sectors no spin angle
does. These are all-bin medians; the high-$p_T$ behaviour is a separate question,
treated in its own section below.

### Why less azimuth costs almost nothing per event

**Coverage mostly changes how many events there are, not how much each one
tells.** The error factors as $\sigma = \sqrt{(G^{-1})_{aa}/N}$:

| factor | full 2π → 4 × 24° | effect on σ |
|---|---|---|
| $N$, events per bin | 13.5× fewer | ×√13.5 = **×3.7** |
| $G$, information per event | nearly unchanged | ×1.05 |

**1. What one event tells you.** For a modulation $A\sin\theta$, an event at angle
θ contributes information in proportion to $\sin^2\theta$. An event at θ = 90° is
very informative, and one at θ = 0 tells nothing because the modulation vanishes
there. The average per event is
$\langle\sin^2\theta\rangle = \tfrac12 - \tfrac12\langle\cos 2\theta\rangle$, which is ½ for
full 2π.

**2. Four sectors 90° apart give the same ½.** In N11p bin 100, φ_h is packed near
180°, so the four φ_S stripes give Sivers angles $\phi_h-\phi_S$ of 180°, 90°, 0°
and 270°:

| φ_S stripe | 0° | 90° | 180° | −90° |
|---|---|---|---|---|
| θ = φ_h − φ_S | 180° | 90° | 0° | 270° |
| sin²θ | 0 | 1 | 0 | 1 |

The average is exactly ½, and it is ½ for any φ_h, because angles 90° apart have
$\cos 2\theta$ alternating +, −, +, −. The same holds for the Collins angle. So the
diagonal of $G$ is ½ for 4 × 24° as for full 2π (measured 0.50). The four sectors
sample the modulation at four phases 90° apart, which estimates a sine amplitude as
efficiently per sample as the whole circle. What is lost is samples, not
information per sample.

**3. The only per-event loss is mixing, and it gives the 5%.** Fewer angle
combinations leave Sivers and Collins more correlated: ρ = 0.39 for 4 × 24°
against 0.26 for 2π. A correlation inflates each error by $1/\sqrt{1-\rho^2}$:
1.086 against 1.036. Their ratio, **0.95**, is the measured 0.96 / 0.94 (Sivers /
Collins). Pretzelosity's 0.93 comes from the same effect in the full 3 × 3 matrix.

**4. When partial coverage does hurt per event:** when the sampled phases cannot
separate the modulations.
- **2 × 48°:** φ_S sits only near 0/180°, where $\sin(\phi_h-\phi_S)$ and
  $\sin(\phi_h+\phi_S)$ are the same function up to sign. So ρ = 0.91 and the
  inflation is $1/\sqrt{1-0.91^2} = 2.4$ (measured 2.3).
- **`phi4seg24degdiag_phifullbin` and `phi2seg48deg2spin_phifullbin`:** they fail the same test at high $p_T$
  only, which the all-bin medians hide. See "Why layout matters at high $p_T$"
  below.

For SoLID Light: with three or more evenly spaced sectors, the layout costs almost
no information per event at any $p_T$, and partial coverage is paid almost
entirely in event count.

### Why no spin angle can help 4 × 24° — the derivation, traced through the code

Each step gives the argument, then **In the code**: where `analysis_neutron 2`
(`AnalyzeEstatUT3`) does it. Line numbers are for `../SoLID_SIDIS_3He.h` and
`../Lsidis3.h` as of 2026-09-23; function names are the stable handle. Steps 1–4
hold for any acceptance; the 4 × 24° symmetry enters only at step 5.

**Step 1: the error depends only on $N_{acc}$, $f_n$ and a 3 × 3 matrix $G$.** In
one bin, the three amplitudes are fitted to the accepted $(\phi_h, \phi_S)$
distribution with
$F = (\sin(\phi_h-\phi_S),\ \sin(\phi_h+\phi_S),\ \sin(3\phi_h-\phi_S))$, for
Sivers, Collins and pretzelosity. The per-event information is
$G_{ab} = \langle F_a F_b\rangle$ over the accepted events, and the statistical
error written to the fit input is

$$\sigma_a = \frac{\sqrt{(G^{-1})_{aa}/N_{acc}}}{f_n \cdot 0.6 \cdot 0.86}.$$

$f_n$ is the neutron share of the yield, and 0.6 and 0.86 are the target and
effective-neutron polarisations. **A spin setting can only change the error
through $N_{acc}$, $f_n$ or $G$.**

*In the code* (`AnalyzeEstatUT3`, starts `:1013`):
1. Every accepted event is filled into `hs_full` at its generator $(\phi_h, \phi_S)$
   with weight `weight * acc` (`:1168`). The map is booked at 1° (`NPHI = 360`,
   `:1139-1140`).
2. `hvar` bin 2 sums `weight * acc`, scaled by `lumi * time * eff / Nsim`
   (`:1175`), which gives `Nacc` (`:1178`). Bin 1 sums the neutron weight, so
   `fn = hvar[1] / Nacc` (`:1179`).
3. **Two matrices are built from the same `hs_full`, and the fit reads the second.**
   - `MUT3` (`:1208-1227`): the symmetric matrix
     $\Omega\sum_k (h_k/N_{acc})\,F_a F_b$ over the cells, with $\Omega = 4\pi^2$
     (`OM`, `:1207`). That is $\Omega\,G$. It is inverted at `:1227` and feeds
     `Estatraw` (row norm) and `Estatraw_diag` (`:1260`):
     $\sqrt{\Omega\,(\texttt{MUT3}^{-1})_{aa}/N_{acc}} = \sqrt{(G^{-1})_{aa}/N_{acc}}$.
   - `MUT3_prop` and `Ggg` (`:1274-1293`; the fill is `:1290`): the projection
     written in PR-10-006 Appendix II, with $u$ in place of $F$ on one side.
     `MUT3_prop` $= S\,\texttt{MUT3}$ for a fixed 3 × 3 matrix $S$. They feed
     `Estatraw_prop` (`:1310`).
4. **The two give the same error.** The $S$ cancels analytically, so
   `Estatraw_prop` = `Estatraw_diag`, agreeing to 1.2e-14 across three
   acceptances (the comment at `:1295`; `../SIDIS_MUT3_comparison/`). The
   derivation below therefore uses the symmetric $G$ = `MUT3`/Ω, even though the
   number that reaches the fit is computed through `MUT3_prop`.

   **Note: what $u$ and $S$ are in `MUT3_prop`** (`:1262-1293`; the derivation is
   in `../SIDIS_MUT3_comparison/`, Section 3–4). With $\phi = \phi_h - \phi_S$, the
   three modulations are written in two bases:

   | | component 1 | component 2 | component 3 | code |
   |---|---|---|---|---|
   | $f$ (= $F$) | $\sin\phi$ | $\sin(2\phi_h - \phi) = \sin(\phi_h+\phi_S)$ | $\sin(2\phi_h + \phi) = \sin(3\phi_h-\phi_S)$ | `ff[]` |
   | $u$ | $\sin\phi$ | $\sin 2\phi_h\,\cos\phi$ | $\cos 2\phi_h\,\sin\phi$ | `gg[]` |

   $u$ holds the projection functions PR-10-006 Appendix II integrates the data
   against. They are not the modulations themselves: component 2 of $f$ is
   $u_2 - u_3$, and component 3 is $u_2 + u_3$. So the bases are related by fixed
   matrices, $f = T u$ and $u = S f$:

   $$T = \begin{pmatrix}1&0&0\\0&1&-1\\0&1&1\end{pmatrix},\qquad
   S = T^{-1} = \begin{pmatrix}1&0&0\\0&\tfrac12&\tfrac12\\0&-\tfrac12&\tfrac12\end{pmatrix}.$$

   Note the direction, $u = S f$, not $u = T f$. The code comment at `:1268`
   spells this out too.

   The two matrices at `:1290-1291`, with $w$ = the cell weight × Ω/N_acc:
   - `MUT3_prop` $= \sum w\,u f^{\rm T} = S\,G_\Omega$ (the paper's mixed matrix
     $\int u_j f_k$), where $G_\Omega$ = `MUT3`;
   - `Ggg` $= \sum w\,u u^{\rm T} = S\,G_\Omega\,S^{\rm T}$.

   `Estatraw_prop` takes the diagonal of
   $\texttt{MUT3\_prop}^{-1}\,\texttt{Ggg}\,\texttt{MUT3\_prop}^{-\rm T}$ (`:1307-1310`):

   $$(S G_\Omega)^{-1}\,(S G_\Omega S^{\rm T})\,(S G_\Omega)^{-\rm T}
   = G_\Omega^{-1} S^{-1}\, S\, G_\Omega\, S^{\rm T} S^{-\rm T} G_\Omega^{-1} = G_\Omega^{-1}.$$

   $S$ cancels completely. That is why `Estatraw_prop` equals `Estatraw_diag`
   exactly, and why a singular `MUT3` also shows up as "singular MUT3_prop!".

   **For the spin argument**, $u_2 = \sin 2\phi_h \cos(\phi_h-\phi_S)$ and
   $u_3 = \cos 2\phi_h \sin(\phi_h-\phi_S)$ each carry a single $\pm\phi_S$, like $F$.
   So `MUT3_prop` and `Ggg` also contain $\phi_S$ only as $2\phi_S$, and steps 3–7
   apply to them term by term, not only through the cancellation above.
5. `Estat_prop = Estatraw_prop / fn / 0.6 / 0.86` (`:1323`). `CreateFile` writes it
   as `stat_sivers` / `stat_collins` / `stat_pretzelosity`, which `prepare.py`
   carries into `simenhanced3he.dat`.

**Step 2: write out $G$**, using $\sin a\,\sin b = \tfrac12[\cos(a-b) - \cos(a+b)]$:

| entry | $a-b$ | $a+b$ | $G_{ab}$ |
|---|---|---|---|
| $G_{11}$ | 0 | $2\phi_h - 2\phi_S$ | $\tfrac12 - \tfrac12\langle\cos(2\phi_h - 2\phi_S)\rangle$ |
| $G_{22}$ | 0 | $2\phi_h + 2\phi_S$ | $\tfrac12 - \tfrac12\langle\cos(2\phi_h + 2\phi_S)\rangle$ |
| $G_{33}$ | 0 | $6\phi_h - 2\phi_S$ | $\tfrac12 - \tfrac12\langle\cos(6\phi_h - 2\phi_S)\rangle$ |
| $G_{12}$ | $-2\phi_S$ | $2\phi_h$ | $\tfrac12\langle\cos 2\phi_S\rangle - \tfrac12\langle\cos 2\phi_h\rangle$ |
| $G_{13}$ | $-2\phi_h$ | $4\phi_h - 2\phi_S$ | $\tfrac12\langle\cos 2\phi_h\rangle - \tfrac12\langle\cos(4\phi_h - 2\phi_S)\rangle$ |
| $G_{23}$ | $-2\phi_h + 2\phi_S$ | $4\phi_h$ | $\tfrac12\langle\cos(2\phi_h - 2\phi_S)\rangle - \tfrac12\langle\cos 4\phi_h\rangle$ |

*In the code:* these are the nine `MUT3(i,j) +=` lines (`:1216-1224`), each
divided by $\Omega$. Row and column 0/1/2 are Sivers/Collins/pretzelosity.
`MUT3_prop` (`:1290`) mixes the same entries through $S$, so the same harmonics
appear in it.

**Step 3: $\phi_S$ only ever appears as $2\phi_S$.** Each $F$ contains exactly one
$\pm\phi_S$, so a product of two contains 0 or $\pm 2\phi_S$. Expanding
$\cos(n\phi_h \pm 2\phi_S) = \cos n\phi_h\cos 2\phi_S \mp \sin n\phi_h \sin 2\phi_S$,
every $\phi_S$-dependent term has one of two forms,

$$\langle g(\phi_h)\cos 2\phi_S\rangle \quad\text{or}\quad \langle g(\phi_h)\sin 2\phi_S\rangle .$$

So the spin affects $G$ only through the second harmonic of $\phi_S$.

*In the code:* nothing to find. The three `sin(...)` factors in `:1216-1224` each
carry one `phiS`. The claim is checked numerically in step 6.

**Step 4: what a spin at lab angle β changes — nothing but $\phi_S$.**
- **The same lab events are accepted, so $N_{acc}$ and $f_n$ are unchanged.** The
  sectors are fixed in the lab. The event weight is the unpolarised $F_{UU}$, and
  the acceptance maps read θ and momentum only.
- **$\phi_h$ is unchanged.** It is measured about $\vec q$ from the lepton plane,
  and neither depends on the spin.
- **$\phi_S$ shifts by +β.** It is the spin's azimuth about $\vec q$, measured from
  the lepton plane, so turning the spin by β adds β. For an electron at lab
  azimuth ψ, $\phi_S \approx \beta - \psi$. This is exact as $\theta_q \to 0$; the
  general form is $\tan\psi = -\cos\theta_q \tan(\phi_S - \beta)$ (`../physics.md`).

With 4 × 24° sectors at $c_k = 0°, 90°, 180°, 270°$, an electron in sector $k$ has
$\psi = c_k + \delta$, where δ is its offset inside the sector (±12°). So

$$\phi_S \approx \beta - c_k - \delta,\qquad 2\phi_S \approx 2\beta - k\cdot 180° - 2\delta ,$$

$$\cos 2\phi_S = (-1)^k\cos(2\beta - 2\delta),\qquad \sin 2\phi_S = (-1)^k\sin(2\beta - 2\delta).$$

**The second harmonic flips sign from one sector to the next, whatever β is.**

*In the code:*
1. `Lsidis` samples $\phi_S$ uniformly on $(-\pi, \pi]$ (`Xmin`/`Xmax`, `:1103-1104`).
   `CalculateFinalState` turns it into the scattered lepton's azimuth with the
   spin at +x̂ (`Lsidis3.h:496-501`, the `shl`/`chl` lines).
2. For a spin at β the event is treated as rotated by β about the beam. Its lab
   azimuth is `p.Phi() + spin_angle` in both branches of `InPhiSector` (`:193`,
   `:204`), and that is the only place β enters.
3. `hs_full` is filled with the generator's own `phiS` (`:1168`), which is already
   measured from the rotated spin. So the stripes land at $\beta - c_k$. The
   2 × 48° test with `spin_angle = +45` put them at +45° and −135°, matching a true
   spin vector at +45°.
4. `GetAcceptance_event` (`:329-339`) sets `spin_angle` per setting and returns
   the average over `spin_angles`. That average is what `acc` holds at `:1153`.
5. The weight comes from `GetWeightFromCurrentState(0)`, `mode == 0`: "No
   azimuthal modulations" (`Lsidis3.h:757`). The spin fields `SNT`, `SNL` and
   `Slepton` are 0 (`Lsidis3.h:174-176`), so nothing in the weight knows β.

**Step 5: the four sectors have the same contents.** Turning the lab by 90° maps
the 4 × 24° sectors onto themselves and sector $k$ onto sector $k+1$. The weight
and the rest of the acceptance do not depend on lab azimuth, so each $\phi_S$
stripe has the same event count and the same $\phi_h$ distribution. For any
$g(\phi_h)$,

$$\langle g(\phi_h)\cos 2\phi_S\rangle = \tfrac14\sum_k (-1)^k\,\langle\ldots\rangle_{\rm stripe} = \tfrac14(+1-1+1-1)\langle\ldots\rangle = 0,$$

and the same for $\sin 2\phi_S$. **This holds for every β.**

*In the code:*
- The count form of `InPhiSector` places centres every `spacing = 360/phi_nsector`
  and folds `fmod(phi, spacing)` onto the nearest one (`:202-207`). With
  `phi_nsector = 4` that is exactly symmetric under 90°.
- `GetAcceptance_e`, `_pip` and `_pim` (`:239` on) test θ and momentum, then
  `InPhiSector`, then read the `Acceptance/` maps in (θ, p). No other lab-φ
  dependence.
- The `hs_full` maps show it: four stripes of 12–13% each with the same $\phi_h$
  pattern (`enhancedN11p` bins 100 and 600, earlier in this README).
- The one small exception is not in the acceptance. The generator samples
  $\phi_S$, not ψ, so its lab density near ψ = 0/180° is 1.0035 and near ±90° is
  0.974 of uniform. That leaves a residual ⟨cos 2φ_S⟩ of about +0.01, measured.

**Step 6: $G$ no longer depends on β.** All the $\phi_S$ terms drop out, leaving

$$G_{11} = G_{22} = G_{33} = \tfrac12,\quad G_{12} = -\tfrac12\langle\cos 2\phi_h\rangle,\quad G_{13} = +\tfrac12\langle\cos 2\phi_h\rangle,\quad G_{23} = -\tfrac12\langle\cos 4\phi_h\rangle .$$

These involve only $\phi_h$, which the hadron acceptance sets and the spin does
not touch. Measured from the `hs_full` maps (40 `enhancedN11p` bins, medians):

| quantity | predicted | measured |
|---|---|---|
| $\langle\sin^2\rangle$ | 0.50 | 0.50 |
| $\langle\cos 2\phi_S\rangle$ | 0 | +0.01 (spin 0), −0.00 (spin 0 + 45) |
| raw Sivers–Collins correlation | $-\langle\cos 2\phi_h\rangle = -0.30$ | −0.23 / −0.26 |

*In the code:* `mut3corr.C` (this directory) rebuilds `MUT3` from the same
`hs_full` maps and inverts it, reproducing `:1208-1227`. The moments above are
the same weighted sums, taken without the $F_a F_b$ products.

**Step 7: mixing spin settings changes nothing either.** A beam-time split with
fractions $f_i$ gives $G_{\rm mix} = \sum_i f_i\, G(\beta_i) = G$, since every
$G(\beta_i)$ is the same. It also gives $N_{\rm mix} = \sum_i f_i N = N$ and the
same $f_n$, so $\sigma_{\rm mix} = \sigma$ for any angles and any split. That is the
measured 1.00 / 1.00 / 1.00 of `phi4seg24deg2spin_phifullbin`, and the
fit-input columns agree row by row (median ratio 1.00, 10–90% range 0.99–1.01).

*In the code:*
1. `GetAcceptance_event` returns $\tfrac1n\sum_i \mathrm{acc}(\beta_i)$ (`:339`). So
   `hs_full` (`:1168`) and `hvar` fill with the average over settings, i.e.
   $\tfrac1n\sum_i$ of the per-setting maps.
2. `time` stays at the full 48 d / 21 d. Nacc is lumi·time·Σ w·(1/n)Σᵢ accᵢ
   = Σᵢ lumi·(time/n)·Σ w·accᵢ, so the average *is* the beam-time split.
3. `MUT3` divides by that same `Nacc` (`:1216`), so it is the weighted mean of the
   per-setting matrices: $G_{\rm mix}$.

**Step 8: why 2 × 48° is different.** Its sectors sit only at 0° and 180°, so
$k = 0, 2$ and $(-1)^k = +1$ for both stripes. **Nothing cancels:**

$$\langle\cos 2\phi_S\rangle = \cos 2\beta\cdot\langle\cos 2\delta\rangle_{\pm 24°},\qquad \langle\cos 2\delta\rangle_{\pm 24°} = \frac{\sin 48°}{48° \text{ in radians}} = 0.887 .$$

- At β = 0 this gives +0.89, **exactly the measured value**. $G_{12}$ is then large,
  and Sivers and Collins are nearly degenerate (correlation 0.91). The
  inversion at `:1227` inflates both errors by 2.3×, and in a few bins `MUT3` is
  singular outright ("singular MUT3_prop!", `:1313`).
- At β = 90° it gives −0.89, so a 0 + 90 split averages to 0 and removes the
  degeneracy. The next section's run confirms it: correlation 0.28, per-event
  errors 0.97 / 0.95 / 0.94.

*In the code:* `phi_nsector = 2`, `spacing = 180` in `InPhiSector`. Everything
else is identical, which is why the same eight lines of algebra cover both.

**The rule.** A spin setting enters the statistical error only through the second
harmonic of $\phi_S$. Sectors that look the same after a 90° turn (4-fold) cancel
that harmonic themselves, so no spin angle and no split can change anything.
Sectors without that symmetry, like 2 × 48°, leave it in, and there the spin
angle matters. Whether the fit then improves also depends on where in $p_T$ the
layout puts its events (next section).

**How much 4 × 24° could gain at all.** Its only remaining mixing comes from
$\langle\cos 2\phi_h\rangle \approx 0.30$, which no spin setting reaches. Even
removing it all would buy about 5%: full 2π, with weaker mixing (correlation 0.26
against 0.39), has per-event errors only 0.96 / 0.94 / 0.93 of 4 × 24°. What
4 × 24° loses against full 2π is **event count**, about 13.5× fewer, and spin
rotation cannot recover it.

**Using $F_{UU}$ alone does not bias any of this.** The weight is $F_{UU}$ only
(step 4, item 5). With the polarised terms included, the per-event information
becomes
$\langle F_a F_b/(1 + \varepsilon A\cdot F)\rangle
= \langle F_a F_b\rangle - \varepsilon\langle F_a F_b (A\cdot F)\rangle + O(\varepsilon^2)$,
with $\varepsilon$ = polarisation × dilution.
- The first-order term averages $\sin^3$-type products. These are odd under the
  up/down mirror symmetry of the sectors, so the term is about zero.
- The second-order term is at most about 1% for the model asymmetries here
  ($|A_{\rm Collins}| \le 0.25$, $|A_{\rm Sivers}| \le 0.13$) and is the same size at
  every spin angle.
- The unpolarised $\cos\phi_h$ and $\cos 2\phi_h$ terms (Cahn, Boer–Mulders), which
  `mode == 0` also omits, would shift $\langle\cos 2\phi_h\rangle$ by a few per
  cent, but identically at every spin angle.

## When a spin split does help — 2 × 48° with spin 0 + 90°

A second spin setting pays off when the first leaves $\langle\cos 2\phi_S\rangle$
far from $\langle\cos 2\phi_h\rangle$. 2 × 48° is the case: at spin 0 every
$\phi_S$ sits near 0/180°, so $\langle\cos 2\phi_S\rangle = +0.89$ and the
correlation is 0.91. Spin 90° moves the stripes to ±90°, giving about −0.89, and a
50/50 split averages to about 0.

**Estimated from the maps** (2026-09-22). The spin-90 half was built as the
spin-0 `hs_full` with $\phi_S$ shifted by 90°. That shift is exact only as
$\theta_q \to 0$ (the $\cos\theta_q$ relation in `../physics.md`). The same shortcut
applied to 4 × 24° with 0 + 45 reproduces the real run (0.40 vs 0.41 correlation,
errors 1.00/1.00/1.00), which calibrates it. Same 40 `enhancedN11p` bins as
`mut3corr.C`, errors relative to `phi4seg24deg_phifullbin`:

| config | \|corr(Siv, Col)\| | per-event error Siv / Col / pretz |
|---|---|---|
| `phi4seg24deg_phifullbin` | 0.39 | 1.00 / 1.00 / 1.00 |
| `phi4seg24deg2spin_phifullbin` | 0.41 | 1.00 / 1.00 / 1.00 |
| `phi2seg48deg_phifullbin` | 0.91 | 2.30 / 2.26 / 1.00 |
| estimate: `phi2seg48deg_phifullbin` maps + a copy shifted 90° in φ_S | 0.29 | 0.97 / 0.94 / 0.94 |
| `phi2seg48deg2spin_phifullbin` (measured) | 0.28 | **0.97 / 0.95 / 0.94** |

**Measured** (2026-09-23, `phi2seg48deg2spin_phifullbin`). The per-bin
prediction holds and the fit does not follow it.

`mut3corr.C` gives a correlation of 0.28 and per-event errors 0.97 / 0.95 / 0.94,
matching the estimate. With 1.56× the events of 4 × 24° per bin, the prepared fit
inputs carry 1.43–1.55× the total information ($\sum 1/\sigma^2$, effective
error 0.80–0.84). Yet the fits land *between* 2 × 48° and 4 × 24°, not above both:

| world / this | stat 1x | stat 4x | stat+syst 4x | stat 1x R1<0.3 | stat 4x R1<0.3 |
|---|---|---|---|---|---|
| $g_T^{u-d}$, `phi4seg24deg_phifullbin` | 5.5 | 8.6 | 6.9 | 2.6 | 3.7 |
| $g_T^{u-d}$, `phi2seg48deg_phifullbin` | 2.7 | 4.0 | 3.8 | 2.6 | 3.2 |
| $g_T^{u-d}$, `phi2seg48deg2spin_phifullbin` | 4.1 | 6.5 | 5.3 | **3.2** | **4.7** |
| Sivers $d$ ($x=0.2$), `phi4seg24deg_phifullbin` | 17.1 | 31.6 | 25.4 | 6.9 | 10.2 |
| Sivers $d$ ($x=0.2$), `phi2seg48deg_phifullbin` | 6.5 | 10.1 | 9.9 | 6.4 | 9.0 |
| Sivers $d$ ($x=0.2$), `phi2seg48deg2spin_phifullbin` | 11.5 | 19.4 | 16.5 | **9.6** | **13.3** |

**Why: at high $p_T$ it loses per event, where the asymmetry is large.** The
information ratio against 4 × 24° by $p_T$ (Collins channel):

| $p_T$ (GeV) | 0–0.2 | 0.2–0.4 | 0.4–0.6 | 0.6–0.8 | > 0.8 |
|---|---|---|---|---|---|
| information ratio | 1.66 | 3.52 | 0.81 | 0.30 | 0.21 |

Split into event count and per-event error (medians of $\sigma\sqrt{N_{acc}}$):

| $p_T$ (GeV) | 0–0.2 | 0.2–0.4 | 0.4–0.6 | 0.6–0.8 | > 0.8 |
|---|---|---|---|---|---|
| $N_{acc}$ ratio | 1.53 | 2.30 | 0.73 | 0.56 | 0.68 |
| per-event error, Siv / Col | 0.98 / 0.99 | 0.72 / 0.78 | 1.34 / 1.01 | **2.77 / 1.51** | **3.07 / 2.03** |

At low $p_T$ the split has more events and equal or better per-event
information. At high $p_T$ it has somewhat fewer events and, above all, a
Sivers–Collins degeneracy that returns: raw correlation −0.77 / −0.91 / −0.79 in
the top $p_T$ bins, against ≈0 for 4 × 24°. The spin split fixes the degeneracy
in $\phi_S$, but at high $p_T$ a different one appears in the hadron's lab
azimuth (next section). The Collins and Sivers asymmetries grow with $p_T$, so
that is where the fit is most sensitive.

Weighting each row by its model asymmetry, $\sum (A_{UT}/\sigma)^2$, turns the
effective error from 0.80 into **1.03** (Collins) and from 0.84 into **1.14**
(Sivers), against the fits' 1.34 (gT) and 1.49 (Sivers d). The same weighting
reproduces `phi2seg48deg_phifullbin` almost exactly (2.16 / 2.67 against 2.04 / 2.63), so it
captures the direction here and most of the size; the rest presumably needs the
full parameter derivatives, not checked. **Under R1 < 0.3**, which removes most
high-$p_T$ rows, the split *beats* 4 × 24° (gT 4.7× against 3.7× at 4x).

**Lesson.** A spin split removes the $\phi_S$ degeneracy exactly as predicted.
Whether a φ-cut layout wins also depends on its per-event information *at high
$p_T$*, which medians over all bins hide. Compare layouts with the fit, or with
$\sum (A_{UT}/\sigma)^2$ and the moments per $p_T$ bin, never with
$\sum 1/\sigma^2$ or all-bin medians.

**The general rule.** Pick the spin angles so that the stripes' $\cos 2\phi_S$
values average to $\langle\cos 2\phi_h\rangle$. For sectors that already cancel
it, like 4 × 24°, spin rotation buys nothing.
Provenance: `../runlog.md`, 2026-09-22.

## Why layout matters at high $p_T$ — the hadron's lab azimuth takes over

**At low $p_T$ the hadron follows $\vec q$. At high $p_T$ it does not, and then
the Sivers and Collins angles are fixed by the lab sector positions
themselves.** This explains the Sivers loss of `phi4seg24degdiag_phifullbin`, the residual
degeneracy of `phi2seg48deg2spin_phifullbin`, and why both overtake 4 × 24° under R1 < 0.3. (Measured 2026-09-23.)

**1. How far the hadron strays from $\vec q$.** Phase space from the generator
(11 GeV, π⁺, no acceptance). $\theta_{hq}/\theta_q$ is the hadron's angle to
$\vec q$ over $\vec q$'s angle to the beam. The columns give the share of hadrons
whose lab azimuth sits within ±12° of each offset from $\vec q$'s azimuth:

| $p_T$ (GeV) | $\langle\theta_{hq}/\theta_q\rangle$ | 0° | 45° | 90° | 135° | 180° |
|---|---|---|---|---|---|---|
| 0–0.2 | 0.24 | 76.7% | 1.7% | 0.2% | 0.1% | 0.0% |
| 0.2–0.4 | 0.72 | 25.7% | 17.6% | 1.8% | 0.7% | 0.3% |
| 0.4–0.6 | 1.23 | 14.7% | 29.5% | 6.7% | 2.5% | 0.9% |
| 0.6–0.8 | 1.85 | 11.3% | 22.4% | 11.9% | 5.6% | 2.1% |
| 0.8–1.2 | 3.12 | 9.5% | 17.6% | 13.3% | 9.0% | 3.8% |

(Uniform would be 6.7% at 0° and 180°, 13.3% at the others, which count both
sides.)

**2. What that does to the angles.** Let ψ_e and φ_H be the electron's and the
hadron's lab azimuths, and β the spin angle. Then $\phi_S \approx \beta - \psi_e$.
- **Low $p_T$** ($\theta_{hq} \ll \theta_q$): the hadron sits near $\vec q$, opposite
  the electron, and $\phi_h$, its azimuth *around* $\vec q$, is free. The Sivers
  and Collins angles are spread by $\phi_h$, so every layout does well.
- **High $p_T$** ($\theta_{hq} \gg \theta_q$): the azimuth around $\vec q$ is close
  to the azimuth around the beam, so $\phi_h \approx \phi_H - \psi_e$. Then

$$\phi_h - \phi_S \approx \phi_H - \beta,\qquad \phi_h + \phi_S \approx \phi_H - 2\psi_e + \beta .$$

  Both angles are now set by *which lab sectors* the hadron and electron sit in.

**3. Each layout at high $p_T$** (spin 0 unless stated):

| layout | hadron sectors φ_H | Sivers: $\langle\sin^2(\phi_H)\rangle$ | Collins angle $\phi_H - 2\psi_e$ | prediction |
|---|---|---|---|---|
| `phi4seg24deg_phifullbin` | 0, 90, 180, 270 | 0, 1, 0, 1 → **½** | $2\psi_e \in \{0, 180°\}$: same set → ½, uncorrelated | fine |
| `phi4seg24degdiag_phifullbin` | 0, 45, 180, 225 | 0, ½, 0, ½ → **¼** | $2\psi_e \in \{0, 90°\}$ spreads it → ½ | Sivers error ×√2 |
| `phi2seg48deg2spin_phifullbin` | 0, 180 | ½ averaged over β | $2\psi_e \equiv 0$: Collins = $\phi_H + \beta$ | Siv = Col at β = 0, Siv = Col + 180° at β = 90°: degenerate |

For `phi2seg48deg2spin_phifullbin`, the Sivers–Collins overlap is ⟨sin²φ_H⟩ ≈ 0.06 at β = 0 and
−⟨cos²φ_H⟩ ≈ −0.94 at β = 90°. Averaged that is −0.44, a correlation of about
−0.89.

**4. Measured** from the `hs_full` maps (N11p, every 3rd bin, medians by $p_T$):

| layout | $p_T$ 0.6–0.8 | 0.8–1.0 | 1.0–1.2 |
|---|---|---|---|
| `phi4seg24deg_phifullbin`: $\langle\sin^2\rangle$ Siv / Col, corr | 0.50 / 0.50, +0.06 | 0.50 / 0.50, +0.02 | 0.51 / 0.51, +0.29 |
| `phi4seg24degdiag_phifullbin`: $\langle\sin^2\rangle$ Siv / Col, corr | **0.30** / 0.52, +0.24 | **0.20** / 0.44, −0.43 | **0.26** / 0.51, +0.10 |
| `phi2seg48deg2spin_phifullbin`: $\langle\sin^2\rangle$ Siv / Col, corr | 0.50 / 0.50, **−0.77** | 0.49 / 0.50, **−0.91** | 0.49 / 0.50, **−0.79** |

The 45°-pair run's Sivers $\langle\sin^2\rangle$ falls to the predicted ¼ while Collins stays near
½. The spin split's diagonal stays at ½ but its correlation reaches the predicted
−0.89. In the fit inputs this shows as per-event error ratios against 4 × 24° of
1.58 / 1.90 (`phi4seg24degdiag_phifullbin`, Sivers) and 2.77 / 3.07 (`phi2seg48deg2spin_phifullbin`, Sivers) at $p_T$ 0.6–0.8 / > 0.8.
That is the bulk of both runs' losses: the 45°-pair run has *more* events than 4 × 24° up to
$p_T$ 0.6 (Nacc ratio 1.04 / 1.89 / 1.13).

**5. Consequences.**
- **Why they win under R1 < 0.3.** The cut removes most high-$p_T$ rows, where
  they lose per event, and keeps low $p_T$, where they have more events. `phi4seg24degdiag_phifullbin`
  4.5× and `phi2seg48deg2spin_phifullbin` 4.7× beat 4 × 24°'s 3.7× there (gT, 4x).
- **The layout rule for SoLID Light.** The *hadron* sectors must sample the lab
  azimuth relative to the spin evenly, so that $\langle\cos 2(\phi_H - \beta)\rangle = 0$.
  The *electron* sector pairs must spread $2\psi_e$, so that Sivers and Collins
  separate. Three or more evenly spaced sectors satisfy both at every $p_T$ and
  every spin angle. Uneven layouts can win at low $p_T$ on event count and still
  lose the fit, because the fit's leverage sits at high $p_T$.
- **Check a new layout per $p_T$ bin**, not with all-bin medians: the medians of
  `phi4seg24degdiag_phifullbin` looked almost as good as 4 × 24° (per-event 1.08 / 1.04).

## The binning comparison (study `enhanced3he-morebin`)

The `enhanced3he-morebin` study asks **what does the binning alone do?** It compares

| run | bins |
|---|---|
| `phifull` | 1660 |
| `phifull_countbin1e6` | **19074** |

Same pseudodata, same full-2π acceptance, same 500 replicas — the *only*
difference is the bin file. `phifull_countbin1e6`'s bins came from
`../make_bins_from_count.py` at `-N 1e6` over the opt-4 count table (see
`../runlog.md`, 2026-09-06/07). `world` and `SBS` are kept as reference.

### What it found: statistically nothing, and a systematics artifact

**Statistically the finer binning buys nothing**, which is the expected answer —
rebinning the same events creates no information. $g_T(u-d)$ error 0.0107 →
0.0116 (15.9x → 14.7x over world), inside the ±20% run-to-run noise; the Sivers
parameter errors land at 0.90–1.00 of the baseline against a 3.2% replica floor.

**The stat+syst "improvement" is an artifact of the error model and must not be
quoted.** It looks large — $g_T$ 0.0195 → 0.0134, i.e. 8.7x → 12.7x, and the
Sivers $\langle k_T^2\rangle$ error halves — but it comes entirely from treating
a correlated systematic as independent per bin.

`../prepare.py:110` builds `error_tot` $=\sqrt{\text{stat}^2 + \text{systabs}^2 +
A^2\,\text{systrel}^2}$ **per bin**, and the χ² sums bins in quadrature, so the
relative systematic enters as if uncorrelated. Split a bin into $k$ sub-bins:
the statistical error grows as $\sqrt{k}$ while $\sigma_{\rm syst}=A\,$`systrel`
stays the same size, so the fit's effective variance becomes

$$\sigma^2_{\rm eff} = \text{stat}^2 + \frac{\text{syst}^2}{k}$$

— the statistical term preserved, the systematic term **divided by $k$**.

The notebooks' own "systematics penalty" row measures exactly that. Converting
$\text{std(stat+syst)}/\text{std(stat)}$ to the implied systematic *variance*
share gives ratios of 5.7x, 4.5x, 10.4x and 10.1x for `Nd`, `ad`, `bd` and
`kt2` — against a bin-count ratio of **11.5x**. The systematic is falling as
$1/N_{\rm bins}$, to within the accuracy of the comparison.

It should not fall at all. `systrel` is target polarization 3% ⊕ nuclear effect
5% ⊕ radiative correction 2.5% ⊕ diffractive meson 3% ⊕ random coincidence 0.2%
= 7.02% (`../SoLID_SIDIS_3He.h`), and every term is common to all bins: if the
target polarization is 3% high, every bin's asymmetry moves together. The true
covariance carries a rank-1 term $(A_i\,\text{systrel})(A_j\,\text{systrel})$,
and $k$ copies of one coherent shift carry no new information about it. Fixing
this means a covariance matrix with those off-diagonal terms, or a nuisance
parameter for the overall scale — a change to the χ², not to the binning.

**Scope — and equal bin counts are NOT enough.** It is tempting to conclude
that the dilution cancels whenever both sides have the same $k$. It does not.
The *factor* cancels; its **impact** does not, because that depends on how
systematics-limited each side is:

| run | systematics penalty | syst share of variance |
|---|---|---|
| `phifull` | 2.38 | **82%** |
| `phi4seg24deg_phifullbin` | 1.17 | 27% |

Both have 1660 bins, yet the dilution suppresses `phifull`'s error almost
entirely and `phi4seg24deg_phifullbin`'s barely at all. So **the stat+syst φ-cut
comparison is distorted too**, even though its binning is matched. Measured on
$\langle k_T^2\rangle$: the φ cut costs a factor 4.02 in the stat panel but only
1.97 in stat+syst, and undoing the dilution (multiplying the systematic variance
by $N_{\rm eff}\approx1177$, the fully-correlated extreme) moves that 1.97 to
**~1.13**. The current stat+syst panel therefore **overstates the cost of the φ
cut** — with a properly correlated systematic both runs are systematics-limited
and losing statistics stops mattering much. The truth is between the two
extremes, since the fit can partly constrain a common normalisation from the
shape of the data, but the shipped number is at the wrong end of that range.

A check that the picture is self-consistent: the systematic's *absolute*
variance contribution is 4.66 (`phifull`) against 5.96 (`phi4seg24deg_phifullbin`) in
common units — nearly run-independent, as it must be for the same `systrel` on
the same bins.

**So: the stat-only φ-cut comparison is sound** (matched bins, matched
treatment, differences are real statistics), **and the stat+syst one is not a
number to quote.** The own-bins runs (169 and 239) are further affected, and are
already excluded for the separate bin-width reason given above.

### Does this explain the own-bins vs `_phifullbin` gap? Partly, and only partly

The φ-cut table above has its own binning pair at fixed acceptance —
`phi4seg24deg_phifullbin` (1660 bins) against `phi4seg24deg` (169), and the `FA` twins — so
the obvious question is whether the gap between them is the same artifact.

**The direction is the same.** Fewer bins means less dilution and so a larger
systematics penalty, and that is what the notebook shows, mirrored:

| pair | bins | $\langle k_T^2\rangle$ penalty |
|---|---|---|
| `phifull_countbin1e6` / `phifull` | 19074 / 1660 | 1.21 / 2.38 |
| `phi4seg24deg_phifullbin` / `phi4seg24deg` | 1660 / 169 | 1.17 / **1.41** |
| `phi4seg24degFA_phifullbin` / `phi4seg24degFA` | 1660 / 239 | 1.16 / **1.42** |

Both own-bins runs sit above their 1660-bin twins at identical acceptance and
near-identical total $N_{\rm acc}$.

**The magnitude does not follow.** Taking the systematic's variance share,
$\text{penalty}^2-1$, its ratio within a pair should equal the bin ratio if
dilution were all of it:

| pair | observed | bin ratio |
|---|---|---|
| `phifull` vs `phifull_countbin1e6` | 0.10 | 0.09 — matches |
| `phi4seg24deg_phifullbin` vs `phi4seg24deg` | 2.68 | 9.82 — does not |
| `phi4seg24degFA_phifullbin` vs `phi4seg24degFA` | 2.94 | 6.95 — does not |

Two explanations were tried and **falsified**, recorded so they are not
re-derived: it is not the *effective* bin count either (participation ratio
$(\sum N)^2/\sum N^2$ gives 10.3 and 9.8, no closer), and the totals are not to
blame — each pair's total $N_{\rm acc}$ agrees to 5%.

The relation that does hold is with **events per bin**, as it should:
$\sigma_{\rm syst}/\sigma_{\rm stat} \propto A\,\text{systrel}\sqrt{N_{\rm acc}}$,
so $\text{penalty}^2-1$ should track $N_{\rm acc}$ per bin. It does — for four
of the six runs:

    run                        bins   Nacc/bin   pen^2-1   ratio
    phifull                    1660   1.110e+07    4.664   4.20e-07
    phifull_countbin1e6       19074   9.689e+05    0.464   4.79e-07
    phi4seg24deg_phifullbin    1660   8.100e+05    0.369   4.55e-07
    phi4seg24degFA_phifullbin  1660   8.889e+05    0.346   3.89e-07
    phi4seg24deg                169   7.562e+06    0.988   1.31e-07   <- own bins
    phi4seg24degFA              239   5.923e+06    1.016   1.72e-07   <- own bins

`phifull`, `phifull_countbin1e6` and both `_phifullbin` runs share **`phifull`'s bin
boundaries** — `phifull_countbin1e6` subdivides them, the `_phifullbin` runs reuse them
verbatim — so the dilution argument transfers cleanly and the constant holds to
±10%. The own-bins runs sit 2–3x below the line because their boundaries were
chosen independently by `GenerateBinInfoFile` under the reduced acceptance: they
cover different kinematics, with different mean asymmetry per bin and different
$p_T$ leverage on $\langle k_T^2\rangle$. The dilution formula assumes a
re-partition of the *same* regions and does not carry across a different binning
geometry.

**So the own-vs-`_phifullbin` gap is a mixture** — part this systematics artifact,
part the genuine binning-geometry difference the φ-cut section already warns
about. The artifact is an additional contribution on top of that warning, not a
replacement for it, and it strengthens the same conclusion: **stat+syst
comparisons are only safe between runs at equal binning.**

## How many bins 4×24° actually needs — the scan

`phi4seg24deg_countbin800` (806 bins from `../make_bins_from_count.py` over
an opt-4 count table taken **under the φ cut**) against the two configurations
already on disk. Statistical only — the one panel comparable across bin counts,
since the per-bin systematic dilutes as 1/N_bins:

| run | bins | $E(g_T^{u-d})$ | vs `phi4seg24deg_phifullbin` | std(kt2) | vs `phi4seg24deg_phifullbin` |
|---|---|---|---|---|---|
| `phi4seg24deg` (own bins) | 169 | 0.0355 | **1.154×** | 0.00906 | **1.395×** |
| **`phi4seg24deg_countbin800`** | **806** | **0.0305** | **0.992×** | **0.00666** | **1.026×** |
| `phi4seg24deg_phifullbin` | 1660 | 0.0308 | 1.000× | 0.00649 | 1.000× |

**806 is statistically identical to 1660** (0.8% and 2.6%, inside the 3.2%
replica floor) while 169 is clearly worse. The curve descends from 169, flattens
by ~800, and stays flat. So:

- **"bin until stat ≈ A·systrel" is too coarse here.** It selects 166 bins, and
  `GenerateBinInfoFile`'s own-bins run has 169 — both encode the same rule, and
  both sit in the rising part of the curve.
- **1660 bins buy nothing over 800.** ~800 is the practical choice: full
  saturation at half the bin count, hence half the step-2 cost and half the
  exposure to the dilution artifact.
- Caveat: the 806 run differs from `phi4seg24deg_phifullbin` in placement as well as count, so
  this says neither matters in that range — it does not isolate placement.

Saturation begins somewhere between 169 and 806; a rung at 400 would bracket it
and has not been run. Full numbers in `../runlog.md`, 2026-09-07/08.

## Adding SBS to each configuration (study `enhanced3he-sbscombined`)

The `enhanced3he-sbscombined` study reads `out-sbsenhanced3he_*.dat` (fit opt
`sbs+enhanced3he`) instead of `out-enhanced3he_*.dat`. There is no standalone SBS
curve, because SBS is inside every curve.

**SBS adds nothing at full 2π and recovers ~1/6 of what a φ cut costs at 1x
counts, but only ~3% at 4x.** $E(g_T^{u-d})$ (world/this), statistical, SoLID
alone → SoLID+SBS. The 1x column is from the `out-sbsenhanced3he_*.dat` fits; the
study plots the 4x fits for the φ-cut runs (`out-sbsenhanced3he_*_x4counts.dat`):

| run | 1x alone | 1x + SBS | 4x alone | 4x + SBS |
|---|---|---|---|---|
| `phifull` | 0.0107 (15.86×) | 0.0107 (15.86×) | — | — |
| `phi4seg24deg_phifullbin` | 0.0308 (5.53×) | **0.0260 (6.54×)** | 0.0197 (8.62×) | 0.0192 (8.88×) |
| `phi4seg24deg` | 0.0355 (4.79×) | **0.0291 (5.85×)** | 0.0221 (7.71×) | 0.0209 (8.14×) |
| `phi4seg24degFA_phifullbin` | 0.0262 (6.49×) | **0.0246 (6.90×)** | — | — |
| `phi4seg24degFA` | 0.0299 (5.69×) | **0.0260 (6.54×)** | — | — |

At full acceptance SoLID's 1660 bins swamp SBS's 455 rows; once a φ cut removes
~93% of SoLID's events, SBS's fixed contribution becomes relatively valuable. With
4× the counts SoLID dominates again, so SBS's share shrinks.
`phifull` is unchanged only to display precision — its ndof goes 1800 → 2255,
exactly +455 SBS rows, and its parameter spreads tighten 6-9%. Sivers agrees: 13
of 14 like-for-like φ-cut ratios soften.

**This study has no stat+syst panels, and that is deliberate.** There is no
`out-sbsenhanced3hesyst_*.dat` anywhere — `sbs+enhanced3hesyst` is the opt both
fit scripts refuse by name, because SBS carries no systematics model and pairing
its statistical errors with SoLID's stat+syst would weight SBS up for nothing but
the missing budget. The notebooks find no stat+syst fit for the study and draw no
stat+syst panel, rather than one showing the world reference alone.

## Why SBS helps Sivers at high x but not Collins — the ε factor

A puzzle the band figures pose directly: **SBS covers high $x$ better than SoLID,
yet at high $x$ it closes most of the gap for Sivers and almost none of it for
Collins.**

From the 500-replica fits, SoLID 2π over SBS as an error advantage (both stat):

| $x$ | Collins $u$ | Collins $d$ | Sivers $u$ | Sivers $d$ | Collins/Sivers |
|---|---|---|---|---|---|
| 0.30 | 3.89 | 5.79 | 2.25 | 2.57 | 2.01 |
| 0.40 | 4.04 | 3.49 | 1.94 | 2.22 | 1.81 |
| 0.50 | 3.78 | 3.17 | 1.76 | 1.98 | 1.86 |
| 0.60 | **3.84** | **3.50** | **1.62** | **1.80** | **2.15** |

At $x = 0.6$ SBS is within 1.6–1.8× of SoLID for Sivers but 3.5–3.8× behind for
Collins.

**The cause is the depolarisation factor, and it is kinematic rather than
instrumental.** `AUTCollins` carries $\varepsilon(x,y,Q^2)$ and `AUTSivers` does
not:

```python
AUTCollins:  res = epsilon * FUTCollins(...) / FUUT(...)
AUTSivers:   res =           FUTSivers(...) / FUUT(...)
```

A bin's information about a parameter is $(\partial A/\partial\theta)^2/\delta A^2$
— the derivative squared over the variance — so for Collins that is
$\varepsilon^2(\partial G/\partial\theta)^2/\delta A^2$ and for Sivers the same
without the $\varepsilon^2$. Checked: $(\partial A/\partial N_u)/\varepsilon$ is
$-0.09045$ at $y = 0.30, 0.50, 0.70, 0.85$ alike, so the whole $y$ dependence of
the Collins derivative *is* $\varepsilon$.

And SBS sits at high $y$:

| | $y$ median | $\varepsilon$ median | $Q^2$ median |
|---|---|---|---|
| SBS | 0.777 | **0.387** | 5.42 |
| SoLID 2π | 0.559 | **0.721** | 2.22 |

Because $y = Q^2/(2 M E x)$, **SBS reaches high $x$ only by going to high $Q^2$**,
and high $Q^2$ at fixed $x$ forces $y$ up, which pushes $\varepsilon$ down. Its
better high-$x$ coverage is bought at exactly the price that hurts Collins and
leaves Sivers untouched.

Three independent routes agree at high $x$: the fitted ratio above is **1.8–2.15**,
a single-parameter Fisher calculation gives **1.98**, and the FOM-weighted
$\langle\varepsilon^2\rangle$ ratio is **1.91**.

**The agreement is a high-$x$ statement only.** Below $x \approx 0.3$ the Fisher
estimate and the fitted ratio diverge badly (3.61 against 0.93–1.60), because the
fit also carries world-data correlations and multi-parameter degeneracies that a
one-parameter Fisher number ignores, and because SBS's $(z, p_T)$ coverage differs
from SoLID's. Quote the $\varepsilon^2$ mechanism for the high-$x$ behaviour; do
not extend it across the range.


## Why the error ratios do not depend on $Q^2$

The figures are drawn at a single $Q^2$ = 2.4 GeV². They were briefly drawn at
three (2.4, 5.0, 7.5) to check what $Q^2$ costs: in the **upper** panel the curves
separate, but in the **lower** panel — the error ratio — all three fell exactly on
top of one another, so the extra curves were removed as redundant. Measured at
$x = 0.25$, world over `phifull`:

| | $Q^2 = 2.4$ | $Q^2 = 5.0$ | $Q^2 = 7.5$ |
|---|---|---|---|
| Collins, $xh_1^u$ | 8.3633643878 | 8.3633643878 | 8.3633643878 |
| Sivers, $x(f_{1T}^{\perp u} - f_{1T}^{\perp\bar u})$ | 8.0218563739 | 8.0218563739 | 8.0218563739 |

Identical to ten decimals, for both amplitudes.

**The reason is that $Q^2$ enters both distributions only through a factor common
to every replica.** In `tmd.py` each flavour is built as

$$h_1^q(x,Q^2) = \underbrace{N_q\,(\dots x \dots)}_{\text{parameters, }x\text{ only}} \times f_1^q(x,Q^2)$$

and `f1Tperp1` the same way. The parameter block carries no $Q^2$ at all. So
varying $Q^2$ multiplies *every* replica by the same $f_1^q(x,Q^2)$; the replica
standard deviation scales with it, and it cancels exactly in a ratio of two
standard deviations.

**For Sivers this holds only because the antiquark terms are fixed at zero.** The
plotted combination is $f_{1T}^{\perp u} - f_{1T}^{\perp\bar u}$, and $u$ and
$\bar u$ carry *different* PDFs with different evolution — so the factorisation
would break if both contributed. It does not, because `fitsivers.py` fixes `Nub`
and `Ndb` (they are in the `fix=` list; all 500 replicas of every fit have
`Nub = Ndb = 0.0` exactly), which kills the $\bar q$ term and leaves a single
common factor. **Free those two parameters and the ratios would acquire a genuine
$Q^2$ dependence.**

Three consequences:

1. **The comparisons in every figure and table are $Q^2$-independent.** Choosing
   2.4 rather than 5 changes no ratio anywhere.
2. **Absolute values are not.** $xh_1^u$ shifts $+2.9\%$ at $x=0.1$ and $-27\%$ at
   $x=0.6$ over $Q^2 = 2.4 \to 7.5$ — 1.0× to 4.4× the SoLID band half-width.
   **Quote the $Q^2$ with any $g_T$ or band number**; these notebooks use 2.4.
3. **No binning can resolve a $Q^2$ dependence this model does not have.** That is
   the underlying reason the 4× finer $Q^2$ re-binning of the SBS projection
   changed nothing (`../runlog.md`, 2026-09-11), and it is a property of the
   parameterisation rather than of the data.

Full derivation, including that real transversity evolves as a flavour non-singlet
while $f_1$ is a singlet — so tying one to the other is a modelling choice the fits
never test — is in `../physics.md`, step 5.
