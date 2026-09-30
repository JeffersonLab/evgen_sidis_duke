# Run log

Production runs in this repo, **newest first**. One entry per run of
`analysis`, `prepare.py`, `fitcollins.py` or `fitsivers.py`: the command
as typed, timing, where the output landed, and anything notable.

**Entries before 2026-09-28 ran `./analysis_neutron <opt> ...`.** The driver is now
`./analysis 3he <opt> ...` (built with `make O=analysis`), with identical output;
the commands below are left as typed.

The inherited history from `../LiuSIDIS/SoLID/sidis2020_zwzhao` is frozen in
`runlog_old.md`. Commands there use the old three-directory CLI
(`[indir] [outdir]`) and will not reproduce as written — see `CLAUDE.md` for the
current one.





---

## 2026-09-29 — `phicompare` notebooks: `enhanced3he-main` re-drawn, new `enhanced-main`

```
cd phicompare
./run_phicompare.sh enhanced3he-main    # after dropping its FA P_h < 3 GeV twin
./run_phicompare.sh enhanced-main       # new study, gallery/input-enhanced-main.csv
```

jlabl5, 1m25 and 1m27, exit 0, no errors. No fit was re-run: both studies rebuild
their bands from `out-*.dat` on disk.

- **`enhanced3he-main`** reads world, `data_phifull/out-enhanced3he{,syst}_*.dat`
  and `data_phi4seg24degFA_phifullbin/out-enhanced3he{,syst}_*_x4counts.dat`. It
  ran in place, so the two notebooks on disk show it. Its three runs' numbers are
  unchanged; only the plotted set changed.
- **`enhanced-main`** is the first study to use the combined fits of the entry
  below, `data_phifull/out-enhanced{,syst}_*.dat`, beside the He3-only ones. The
  notebooks' `rowname()` needed a one-line fix first: both rows are run
  `phifull`, and the loader refuses duplicate names. A `fit=enhanced` row is now
  named `<run>+nh3`.

Truncated gT(u−d), world/this: He3 15.9× (stat) / 8.7× (stat+syst), He3 + NH3
19.7× / 10.5×. What that means and how far to trust it: `phicompare/README.md`,
"Conclusions at a glance". Committed as `8dd3b5c`.
---

## 2026-09-28 — combined He3 + NH3 fits (`enhanced`, `enhancedsyst`) on `phicompare/data_phifull`

```
ssh -n -p 5999 localhost "bash -c 'cd <repo> && setsid nohup bash -c \"date; hostname; uptime; \
  ./run_fits.sh phicompare/data_phifull enhanced enhancedsyst; echo exit \$?; date\" \
  > enhanced_combined_fits.log 2>&1 < /dev/null & disown'"
```

ifarm2402 via `gj`, at load 370-590 of 256 CPUs (ifarm2401 not reachable in one
hop). 128 workers, NREP 500, SEED0 0, counts x1, no cuts. 23:13:47 -> 23:46:48 =
**33 min**, exit 0, 4 fits OK:

| fit | wall | chi2/ndof median | ndof | edm > 1e-3 |
|---|---|---|---|---|
| `fitcollins.py enhanced` | 233 s | 0.937 | 2351 | 59 |
| `fitcollins.py enhancedsyst` | 424 s | 0.938 | 2351 | 88 |
| `fitsivers.py enhanced` | 691 s | 0.904 | 2436 | 16 |
| `fitsivers.py enhancedsyst` | 633 s | 0.904 | 2436 | 7 |

This was the first fit of `simenhanced.dat` (entry below). The ndof are world +
all 2211 SoLID rows − free parameters (146 + 2211 − 6 for Collins, 234 + 2211 − 9
for Sivers). The He3-only fits in the same directory give 0.92 / 0.88 median and
61 / 14 high-edm replicas, so fit quality is alike. `Nub_err`/`Ndb_err` are NaN in
every Sivers replica, exactly as in `out-enhanced3he_sivers.dat`.

**Outputs:** `out-enhanced{,syst}_{collins,sivers}.dat`, and the fit log
`fitlog-20260928-231347.txt`. The preflight had checked that none of the four
output names existed. **Nothing overwritten**: no tracked file changed, and every
`out-enhanced3he*` keeps its old mtime.

The NH3 rows' errors carry the empty-cell bias (`bug.md` item 14, conservative),
and the NH3 beam days, `systabs` and `statlist` still lack a recorded source
(`physics.md`, "The NH3 target"). So a combined projection drawn from these is
provisional. No figure or study uses these outputs yet.
---

## 2026-09-28 — `prepare.py --combined` on `phicompare/data_phifull`

```
./prepare.py phicompare/data_phifull --combined
```

jlabl5, 23:11, 3 s, exit 0. This is the first use of `--combined`. It read
`enhancedNpi{p,m}.csv` (He3, from 2026-08-31) and `enhancedPpi{p,m}.csv` (NH3,
the run below). It wrote one new file, **`simenhanced.dat`**: 2211 rows, 1660
neutron + 551 proton, with no row dropped. That is the input of the `enhanced` /
`enhancedsyst` fit opts.

The run was guarded to abort if `simenhanced.dat` already existed; it did not.
`simenhanced3he.dat` has the same md5 before and after, and no tracked file
changed. The output is byte-identical to the copy validated in the scratch
directory earlier the same day. There, the He3 rows equal `simenhanced3he.dat`'s,
and 12 sampled NH3 rows equal `tmd` evaluated for a proton to 1e-16 (`code.md`
Step 4).

No fit has been run on it yet. The NH3 rows' errors carry the empty-cell bias of
`bug.md` item 14 (conservative, ~1.15-1.25x), and the NH3 beam days, `systabs`
and `statlist` still lack a recorded source (`physics.md`, "The NH3 target").
---

## 2026-09-28 — first NH3 (proton) run, full 2π, into `phicompare/data_phifull`

```
./analysis nh3 1 phicompare/data_phifull > phicompare/data_phifull/nh3_opt1.log 2>&1
./analysis nh3 2 phicompare/data_phifull > phicompare/data_phifull/nh3_opt2.log 2>&1
./analysis nh3 3 phicompare/data_phifull > phicompare/data_phifull/nh3_opt3.log 2>&1
```

jlabl5, 4 forked groups. The code was the uncommitted working tree after
`plan_nh3.md` steps 1-3 (HEAD 653ca51 + the `Target` refactor, NH3 configuration
and child-stdout flush). The three stages were chained with a guard that
aborted if any of the stage's outputs, or its log, already existed; none did.

| stage | wall |
|---|---|
| opt 1 | 21:12:01 -> 21:17:49, **5m48** |
| opt 2 | 21:17:49 -> 21:46:17, **28m28** |
| opt 3 | 2 s |

**Outputs**, beside He3's `N` files in the same directory:
- `bin_enhanced_P{11,8}{p,m}.dat`
- `enhancedP*.root` (tree branch `fp`, `Nucleon` = 1)
- `enhancedP*_hs.root` (590 MB)
- `enhancedPpi{p,m}.csv` (target `proton`)
- the three `nh3_opt*.log`

**No He3 file was touched**: no tracked file changed, and the newest `N`/`out-`
file is still from 2026-09-24.

**551 bins**: 254 P11p, 177 P11m, 71 P8p, 49 P8m. The CSV has 325 π⁺ and 226 π⁻
rows, none with `Nacc` ≤ 0. The opt 2 log has all 551 per-bin lines (the first
run with the flush fix) and no singular matrix or NaN.

| group | fp median [range] | Nacc median | Estat Sivers / Collins, median |
|---|---|---|---|
| P11p | 0.172 [0.151, 0.203] | 3.2e6 | 0.0073 / 0.0076 |
| P11m | 0.145 [0.135, 0.165] | 3.2e6 | 0.0091 / 0.0092 |
| P8p | 0.169 [0.155, 0.189] | 5.1e6 | 0.0059 / 0.0059 |
| P8m | 0.143 [0.136, 0.159] | 4.4e6 | 0.0076 / 0.0076 |

What these numbers are: `physics.md`, "The NH3 target". Every `Nacc` here is low,
and every error high, by the 3D maps' empty-cell bias, kept by decision
(`bug.md` item 14). Nothing downstream reads the `P` files yet: `prepare.py` and
the fits are neutron-only.
---

## 2026-09-25 — `-p 3` on `data_phi4seg24degFA_phifullbin`, 1x and 4x

```
ssh -n -p 5999 localhost "bash -c 'cd <repo> && setsid nohup bash -c \"date; \
  ./run_fits.sh -p 3 phicompare/data_phi4seg24degFA_phifullbin && \
  ./run_fits.sh -p 3 -c 4 phicompare/data_phi4seg24degFA_phifullbin; echo exit \$?; date\" \
  > phlt3FA.log 2>&1 < /dev/null & disown'"
```

ifarm2402 via `gj` (load 64/256 at launch), 128 workers, NREP 500, SEED0 0.
19:52 -> 20:30 = **38 min**, exit 0, 8 fits OK. Fit logs
`fitlog-20260925-195219.txt` (1x) and `fitlog-20260925-201233.txt` (4x); outputs
`out-enhanced3he{,syst}_{collins,sivers}_phlt3{,_x4counts}.dat`. Nothing overwritten.

The cut kept **1196 of 1660** bins, which carry 72% of the Collins statistical
weight, against 1205 for `phi4seg24deg_phifullbin`. Compared with each uncut twin,
χ²/ndof was 0.84–0.89 (uncut 0.88–0.92) and the edm > 1e-3 counts were no worse.

`main` now draws the 4x twin under the FA row. gT(u-d) truncated, Q2 = 2.4,
cut/uncut: 1.17 stat (9.79× → 8.37×) and 1.22 stat+syst, against 1.18 predicted
from the weight alone. Sivers `kt2` spread 3.01× (stat). Written up in
`phicompare/README.md`, "The hadron-momentum cut".

## 2026-09-24 — `-p 3`: keep only bins with |P_h| < 3 GeV, three runs

```
(./run_fits.sh -p 3 phicompare/data_phifull && \
 ./run_fits.sh -p 3 -c 4 phicompare/data_phi4seg24deg) > phlt3_fits.log 2>&1
./run_fits.sh -p 3 -c 4 phicompare/data_phi4seg24deg_phifullbin >> phlt3_fits.log 2>&1
```

This is the first use of the new `-p/--phmax` flag. It is a bin-level cut on
|P_h| = sqrt((z·y·Ebeam)² − m_π²) from each row's bin means; see `code.md` step 6.
Run on jlabl5 (4 workers) because ifarm was not reachable from the agent shell.
500 replicas, SEED0 0, 12 fits, all OK. Each run wrote a
`fitlog-2026092{4-190959,4-220102,4-224435}.txt` and outputs
`out-enhanced3he{,syst}_{collins,sivers}_phlt3[_x4counts].dat`.

| rundir | counts | rows kept | wall |
|---|---|---|---|
| `data_phifull` | 1x | 1223 of 1660 | 19:10 -> 22:01, 2h51 |
| `data_phi4seg24deg` (own bins) | 4x | 126 of 169 | 22:01 -> 22:44, 43m |
| `data_phi4seg24deg_phifullbin` | 4x | 1205 of 1660 | 22:44 -> 01:36, 2h52 |

Sanity check against each uncut twin: χ²/ndof and the number of replicas with
edm > 1e-3 are unchanged (e.g. `phifull` Collins 0.89 vs 0.92, 66 vs 61). The
parameter spread (cut/uncut) grows by 1.0–1.3x, except `kt2`, which grows
1.4–3.2x. That fits the cut removing mostly high-z bins. Not yet turned into
g_T / band ratios: the phicompare notebooks do not read the `_phlt` suffix.

---

## 2026-09-23 — `data_phi2seg48deg2spin_phifullbin`: 2 x 48 deg, beam time split between spin 0 and 90 deg

```
mkdir phicompare/data_phi2seg48deg2spin_phifullbin
ln -s ../data_phifull/bin_enhanced_N{8,11}{p,m}.dat phicompare/data_phi2seg48deg2spin_phifullbin/
ssh -n -p 5999 localhost "bash -c 'cd <repo> && setsid nohup ./run_phi2seg2spin.sh > phi2seg2spin.log 2>&1 < /dev/null & disown'"
#   ./analysis_neutron 2 <D> 2 all 48 on full 0,90   1:10:05 (214% cpu)
#   ./analysis_neutron 3 <D>                         0:00.84
#   ./prepare.py <D>                                 0:01.57
#   ./run_fits.sh {,-t 0.3,-c 4,-c 4 -t 0.3} <D>
```

ifarm2402 via the `gj` tunnel, 2026-09-22 23:42 -> 2026-09-23 02:37 = **2h55**,
exit 0, 16 fits OK at 500 replicas, 128 workers, SEED0 0. Launched to test a
prediction made from the maps: splitting 2 x 48 deg between spin 0 and 90 should
remove its Sivers-Collins degeneracy (`phicompare/README.md`, "When a spin split
does help"). Banner confirmed `2 sectors of 48 deg = 26.6667% of 2pi` and
`target spin: lab phi = 0 90 deg (beam time split equally, 1/2 each)`.

**1657 of 1660 rows.** `singular MUT3_prop!` in bins 392 and 606, plus
`non-positive diagonal in inverted MUT3!` / `NaN warning in Estat!` in bins 95
and 392; `prepare.py` dropped 3 rows. Spin 0 alone on the same bins lost 5.
R1 < 0.3 kept 1011 of 1657.

**Result: the degeneracy is removed as predicted, but the fit does not improve
over 4 x 24 deg.** The per-event matrix matches the estimate (correlation 0.28,
errors 0.97/0.95/0.94), but gT world/this is 4.1 against 5.5 at 1x: between
2 x 48 deg spin 0 (2.7) and 4 x 24 deg. The layout concentrates events at low pT.
Numbers and the explanation are in `phicompare/README.md`. Comparison numbers
come from the same scratch recipe as the 2026-09-22 entry.

---

## 2026-09-22 — `data_phi4seg24deg2spin_phifullbin`: 4 x 24 deg, beam time split between spin 0 and 45 deg

```
mkdir phicompare/data_phi4seg24deg2spin_phifullbin
ln -s ../data_phifull/bin_enhanced_N{8,11}{p,m}.dat phicompare/data_phi4seg24deg2spin_phifullbin/
setsid nohup ./run_phi4seg2spin.sh > phi4seg2spin.log 2>&1 < /dev/null &
#   ./analysis_neutron 2 <D> 4 all 24 on full 0,45   1:21:15 (213% cpu)
#   ./analysis_neutron 3 <D>                         0:01.01
#   ./prepare.py <D>                                 0:09.54
#   ./run_fits.sh {,-t 0.3,-c 4,-c 4 -t 0.3} <D>
```

ifarm2402 via `gj`, 19:15 -> 22:26 = **3h10**, exit 0, 16 fits at 500 replicas,
128 workers, SEED0 0. Launched from jlabl5 (4 cores); the remote shell is tcsh,
so the launch line had to be wrapped in `bash -c`. Banner confirmed
`4 sectors of 24 deg = 26.6667% of 2pi` and
`target spin: lab phi = 0 45 deg (beam time split equally, 1/2 each)`.

**New CLI form, needed for this run.** `[spinangle]`, the 8th positional
argument: the target spin's lab azimuth, or a comma-separated list splitting the
beam time equally, averaged per event in `GetAcceptance_event`. `time` is left
at the full 48 d / 21 d on purpose. Mechanism and validity: `code.md`,
"`[spinangle]`". Verified before the run: a 360k-point scan shows spin 45 with
4 x 24 deg is identical to spin 0 with sectors at -45,45,135,-135, and over 200k
random e/pi+ pairs the `0,45` acceptance equals the mean of the two single
settings exactly.

**One row lost, 1659 of 1660:** `singular MUT3_prop! bin 134` in N11 (Q2 [1,2],
z [0.60,0.65], Pt [0.4,0.6], x [0.244,0.7]), the low-Nacc corner bin already
named in the `SoLID_SIDIS_3He.h` singular-bin comment; `prepare.py` dropped it.
R1 < 0.3 kept 860 of 1659 (the spin-0 run: 859 of 1660).

**Result: no change from spin 0 alone.** Every gT and Sivers ratio is within
3% of `phi4seg24deg_phifullbin`, and `mut3corr.C` gives per-event errors
1.00 / 1.00 / 1.00 with the same Nacc. Numbers and what this does to the
"count of phi_S values" conclusion: `phicompare/README.md`. The comparison
numbers were computed with a scratch script using the phicompare notebooks'
own formulas (`gt_fast` truncated 0.05-0.6, `f1Tperp1` at the grid x nearest 0.2);
it reproduced the 2026-09-21 values for the other two runs to the last digit
(Sivers d diag 23.1 vs 23.0). The notebooks themselves were not rerun.

---

## 2026-09-21 — `data_phi4seg24degdiag_phifullbin`: the same four sectors, moved

```
mkdir phicompare/data_phi4seg24degdiag_phifullbin
ln -s ../data_phifull/bin_enhanced_N{8,11}{p,m}.dat phicompare/data_phi4seg24degdiag_phifullbin/
setsid nohup ./run_phi4segdiag.sh > phi4segdiag.log 2>&1 < /dev/null &
#   ./analysis_neutron 2 <D> 0,45,180,-135 all 24   1:16:56 (220% cpu)
#   ./analysis_neutron 3 <D>                        0:00.78
#   ./prepare.py <D>                                0:08.48
#   ./run_fits.sh {,-t 0.3,-c 4,-c 4 -t 0.3} <D>
```

ifarm2402 via `gj`, 18:52 -> 21:51 = **3h**, exit 0, 16 fits at 500 replicas,
128 workers. Sector centres 0, 45, 180, -135 deg, 24 deg wide: the pairs 0/180
and 45/-135, **26.67% coverage and four sectors, as `phi4seg24deg`**, with the
phi_S values 45 deg apart instead of 90. `phifull`'s bins by symlink. Clean run:
**no singular `MUT3`, no NaN, all 1660 rows kept** (2 x 48 deg lost 5); R1 < 0.3
kept 963 of 1660.

**New CLI form, needed for this run.** `[phicut]` now takes a comma-separated
list of sector CENTRES in degrees as an alternative to a count; the comma is what
distinguishes them, so every command logged before today parses unchanged
(`analysis_neutron.C`, `SoLID_SIDIS_3He.h:InPhiSector`). A list whose sectors
overlap is rejected pairwise, the same guard the even form has. Verified before
the run by scanning `InPhiSector` over 360k points: the list keeps exactly
(-12,12), (33,57), (-147,-123) and (168,180]u[-180,-168) at 26.6667%, and the
even cases are unmoved (4 x 24 deg 26.6667%, 6 x 24 deg 40%, 2 x 48 deg 26.6667%).

**Result: the NUMBER of distinct phi_S values is what matters, not their
spacing.** `mut3corr.C`, 40 bins per run:

| run | phi_S mod 180 | median \|corr(Col,Siv)\| | cond(G) | sqrt(C_aa) vs `phi4seg24deg`: Siv/Col/pretz |
|---|---|---|---|---|
| `phifull` | continuum | 0.26 | 2.1 | 0.96 / 0.94 / 0.93 |
| `phi4seg24deg_phifullbin` | {0, 90} | 0.39 | 3.9 | 1.00 / 1.00 / 1.00 |
| `phi4seg24degdiag_phifullbin` | {0, 45} | **0.39** | **2.8** | **1.08 / 1.04 / 0.99** |
| `phi2seg48deg_phifullbin` | {0} | 0.91 | 23.2 | 2.30 / 2.26 / 1.00 |

Moving the second pair from 90 deg to 45 deg leaves the Collins-Sivers
correlation unchanged (0.394 against 0.393) and costs 4-8% per event; its
condition number is even slightly better. Having a second phi_S at all is what
buys the factor 2 that 2 x 48 deg loses.

Truncated gT(u-d), world/this, and the Sivers xf1Tperp(1) error at x = 0.2:

| run | stat 1x | stat 4x | stat+syst 4x | Sivers d, stat 4x |
|---|---|---|---|---|
| `phifull` (1x only) | 15.9 | - | - | 56.6 |
| `phi4seg24deg` | 5.5 | 8.6 | 6.9 | 31.6 |
| `phi4seg24degdiag` | 5.0 | 7.9 | 6.6 | 23.0 |
| `phi4seg24degFA` | 6.5 | 9.8 | 7.5 | 33.2 |
| `phi2seg48deg` | 2.7 | 4.0 | 3.8 | 10.0 |

The diagonal lands 8% below the even 4 x 24 deg on gT -- a little more than the
4% per-event penalty, and inside the +-20% run-to-run noise. **Sivers $d$ is the
exception**: 23.0 against 31.6 at 4x, a 27% loss, with 15% MORE events per bin.
Unexplained, and the one number that does distinguish the two geometries.

**Also unexplained: under R1 < 0.3 the diagonal comes out ahead** of the even
4 x 24 deg (gT world/this 4.5 against 3.7 at 4x, 3.2 against 2.6 at 1x), the
only configuration pair that reverses under the cut. The two runs keep different
row sets (963 against 859 of 1660), which is the obvious suspect, not a checked
explanation.

**A partial first attempt was killed and cleaned up.** The chain was started at
18:48, stopped at 18:51 by request, its 8 half-written `.root` files deleted, and
restarted from an empty directory at 18:52. `setsid` means the job survives the
ssh that launched it -- interrupting that ssh does not stop the run.

---

## 2026-09-18 — `data_phi2seg48deg_phifullbin`: 2 x 48 deg, same coverage as 4 x 24 deg

```
mkdir phicompare/data_phi2seg48deg_phifullbin
ln -s ../data_phifull/bin_enhanced_N{8,11}{p,m}.dat phicompare/data_phi2seg48deg_phifullbin/
setsid nohup ./run_phi2seg48.sh > phi2seg48.log 2>&1 < /dev/null &
#   ./analysis_neutron 2 phicompare/data_phi2seg48deg_phifullbin 2 all 48   1:08:26 (216% cpu)
#   ./analysis_neutron 3 phicompare/data_phi2seg48deg_phifullbin            0:00.73
#   ./prepare.py phicompare/data_phi2seg48deg_phifullbin                    0:06.60
#   ./run_fits.sh {,-t 0.3,-c 4,-c 4 -t 0.3} phicompare/data_phi2seg48deg_phifullbin
```

ifarm2402 via `gj`, 13:10 -> 15:50, exit 0. Two sectors centred on 0 and 180 deg,
+-24 deg each (-24..24 and |phi| > 156), both arms (`phiscope=all`): 26.67%, the
same nominal coverage as 4 x 24 deg. Startup banner confirmed
`2 sectors of 48 deg = 26.6667% of 2pi, forward and large angle alike`. Step 1
reused `data_phifull`'s bins by symlink. 16 fits, 128 workers, NREP 500, all OK.

**Not quite 1:1 with phifull: 1655 rows, not 1660.** Step 2 hit singular `MUT3`
in 4 bins (`singular MUT3_prop! bin 95`, `bin 136`, ...; 11 `non-positive
diagonal` and 11 `NaN warning in Estat!` lines), and `prepare.py` dropped 5 of
1660 rows as non-finite. The 4 x 24 deg run on the same bins had none. Two
opposite sectors leave too little azimuthal spread to separate the three
amplitudes in some bins -- the same weakness the fits show below. R1 < 0.3 kept
1011 of 1655 (4 x 24 deg kept 859 of 1660).

**Where the azimuth is sampled matters far more than how much.** Truncated
gT(u-d) (0.05 < x < 0.6), Q2 = 2.4, as world/this; Sivers columns are the
xf1Tperp(1) error at x = 0.2, same form. All three phi-cut runs on phifull's bins:

| run | err | cut | counts | gT err | gT world/this | Sivers u | Sivers d |
|---|---|---|---|---|---|---|---|
| 2pi | stat | - | 1x | 0.0107 | 15.9 | 7.2 | 56.6 |
| 2 x 48 | stat | - | 1x | 0.0619 | 2.7 | 2.7 | 6.5 |
| 4 x 24 | stat | - | 1x | 0.0308 | 5.5 | 2.7 | 17.1 |
| 4 x 24 FA | stat | - | 1x | 0.0262 | 6.5 | 2.8 | 18.0 |
| 2 x 48 | stat | - | 4x | 0.0426 | 4.0 | 2.4 | 10.0 |
| 4 x 24 | stat | - | 4x | 0.0197 | 8.6 | 4.1 | 31.6 |
| 4 x 24 FA | stat | - | 4x | 0.0174 | 9.8 | 4.3 | 33.2 |
| 2 x 48 | stat+syst | - | 1x | 0.0623 | 2.7 | 2.7 | 6.5 |
| 4 x 24 | stat+syst | - | 1x | 0.0333 | 5.1 | 2.6 | 16.0 |
| 2 x 48 | stat+syst | - | 4x | 0.0450 | 3.8 | 2.4 | 9.8 |
| 4 x 24 | stat+syst | - | 4x | 0.0246 | 6.9 | 3.9 | 25.3 |
| 2 x 48 | stat | R1<0.3 | 1x | 0.0663 | 2.6 | 3.0 | 6.4 |
| 4 x 24 | stat | R1<0.3 | 1x | 0.0653 | 2.6 | 2.5 | 6.9 |
| 2 x 48 | stat | R1<0.3 | 4x | 0.0530 | 3.2 | 2.5 | 8.9 |
| 4 x 24 | stat | R1<0.3 | 4x | 0.0464 | 3.7 | 2.4 | 10.2 |

At equal coverage 2 x 48 has **twice** the gT error of 4 x 24 and ~2.6x the
Sivers d error, uncut; systematics change nothing (2 x 48 is statistics-limited
throughout). The d advantage a neutron target should give nearly vanishes
(Sivers d 6.5 vs 17.1). With R1 < 0.3 the two converge (0.0663 vs 0.0653 at 1x):
the cut already throws away most of what 4 x 24 had over 2 x 48, and it costs
2 x 48 almost nothing (0.0619 -> 0.0663). The run-to-run noise on these factors
is ~+-20%; a factor 2 is well outside it.

---

## 2026-09-17/18 — 4x fits of the two FA runs, with and without R1 < 0.3

```
setsid nohup ./run_fa_x4.sh > fa_x4.log 2>&1 < /dev/null &
#   ./run_fits.sh -c 4        phicompare/data_phi4seg24degFA_phifullbin
#   ./run_fits.sh -c 4 -t 0.3 phicompare/data_phi4seg24degFA_phifullbin
#   ./run_fits.sh -c 4        phicompare/data_phi4seg24degFA
#   ./run_fits.sh -c 4 -t 0.3 phicompare/data_phi4seg24degFA
```

ifarm2402 (reached through the `gj` tunnel; ifarm2401 was at load 267/256 at the
time), 128 workers, NREP 500, SEED0 0. 23:26 -> 00:16 = **50 min**, all four
groups OK. 16 new files, `out-enhanced3he{,syst}_{collins,sivers}{,_r1lt0.3}_x4counts.dat`,
500 replicas each; nothing overwritten. This completes the 4x set the
2026-09-08 sweep started for the non-FA `4seg24deg` runs. The cut kept 896/1660
(`_phifullbin`) and 167/239 (own bins), the same as the 1x cut fits.

Band ratio 4x / 1x at Q2 = 2.4. gT(u-d) is **truncated to 0.05 < x < 0.6**, the
notebook definition, so it is not the same number as the 2026-09-08 table,
which integrates over all x. Checked: the full-x gT recomputed from the same
files gives 0.78 / 0.66 / 0.82 / 0.66, the 2026-09-08 stat values exactly. The Sivers columns are the
$xf_{1T}^{\perp(1)}$ error at x = 0.2. The non-FA rows were recomputed from the
existing fits in the same way:

| run | opt | cut | gT 1x | gT 4x | gT 4x/1x | Sivers u 4x/1x | Sivers d 4x/1x |
|---|---|---|---|---|---|---|---|
| FA, 2pi bins | stat | - | 0.0262 | 0.0174 | 0.66 | 0.65 | 0.54 |
| FA, 2pi bins | stat | R1<0.3 | 0.0546 | 0.0391 | 0.72 | 0.97 | 0.70 |
| FA, 2pi bins | stat+syst | - | 0.0286 | 0.0225 | 0.79 | 0.69 | 0.64 |
| FA, 2pi bins | stat+syst | R1<0.3 | 0.0565 | 0.0454 | 0.80 | 1.03 | 0.77 |
| FA, own bins | stat | - | 0.0299 | 0.0186 | 0.62 | 0.66 | 0.58 |
| FA, own bins | stat | R1<0.3 | 0.0543 | 0.0396 | 0.73 | 1.11 | 0.86 |
| FA, own bins | stat+syst | - | 0.0448 | 0.0414 | 0.92 | 0.84 | 0.83 |
| FA, own bins | stat+syst | R1<0.3 | 0.0604 | 0.0573 | 0.95 | 1.09 | 0.86 |
| both arms, 2pi bins | stat | - | 0.0308 | 0.0197 | 0.64 | 0.65 | 0.54 |
| both arms, 2pi bins | stat | R1<0.3 | 0.0653 | 0.0464 | 0.71 | 1.04 | 0.68 |
| both arms, own bins | stat | - | 0.0355 | 0.0221 | 0.62 | 0.67 | 0.57 |
| both arms, own bins | stat | R1<0.3 | 0.0584 | 0.0436 | 0.75 | 1.14 | 0.86 |

Collins responds to 4x the way the both-arms runs do (0.62-0.66 stat, uncut), and
FA stays slightly ahead of both-arms at equal binning, as it was at 1x.

**Unexplained: the cut Sivers u band does not shrink with 4x counts.** At x = 0.2
it is 0.97-1.14 of the 1x band in every cut fit, FA or not, while the uncut u band
drops to ~0.66 and the d band shrinks cut or uncut. Replica noise on a ratio of two
500-replica stds is ~4.5%, so 1.11-1.14 is outside it. The cut and the
luminosity scaling are both fine elsewhere, so suspect the Sivers u parameters
becoming poorly constrained once the low-x rows are gone (a flat or bimodal
direction that more statistics does not tighten). Not investigated.

---

## 2026-09-09/11 — shared-input reorganisation, a self-inflicted clobber, and the 4x SBS+SoLID fits

```
mv data_other data_world                                     # SBS had already left for data_sbs/
./prepare.py  data_sbs --sbs
./run_fits.sh data_world world                               # \
./run_fits.sh data_sbs   sbs                                 #  | recovery, see below
./run_fits.sh phicompare/data_phifull enhanced3he            #  |
./run_fits.sh phicompare/data_phifull sbs+enhanced3he        # /
./run_fits.sh -c 4 phicompare/data_phi4seg24deg_phifullbin sbs+enhanced3he
./run_fits.sh -c 4 phicompare/data_phi4seg24deg             sbs+enhanced3he
```

All on ifarm2401, 128 workers, NREP 500.

**The shared inputs are now two directories, each named for what it holds.**
`data_other/` meant "everything that is not a run"; once the SBS projection moved
to `data_sbs/`, what remained was world data, so it became `data_world/`. 28 files
repointed, with SBS-specific references sent to `data_sbs/` rather than blindly
renamed. `SBSDIR` joins `WORLDDIR` in both fit scripts. Committed `ae16273`.

**A `-n 2` smoke test overwrote seven production fits.** Verifying the repointing,
I ran 2-replica fits against real run directories to check the paths resolved. The
fit scripts have no dry-run and no overwrite guard, and `out-<opt>_<obs>.dat` is the
same filename whatever `-n` is, so seven 500-replica results were replaced by
2-replica stubs across `data_world/`, `data_sbs/` and `phicompare/data_phifull/`.
Caught only because a re-executed notebook printed "2 replicas" beside the world
entry.

Recovered by re-running the four opts above, 14:53 -> 15:21. A repo-wide sweep of
every `out-*.dat` then confirmed nothing else was short. The `_r1lt0.3` and
`_x4counts` variants were never at risk -- their suffixes give them distinct
filenames. **Verify fit-script changes into a scratch rundir, or by parsing, never
by producing output into a real one.**

**4x `sbs+enhanced3he`, which the 2026-09-08 counts sweep had not covered** (it ran
`enhanced3he` and `enhanced3hesyst` only). Four fits, 20:43 -> 21:01. `--counts`
scales only the SoLID half of the combined set -- more SoLID beam time does not give
SBS more events -- so these are SBS at fixed luminosity plus SoLID at 4x.

gT(u-d) Collins, statistical, Q2 = 2.4:

| | SoLID alone | SBS + SoLID |
|---|---|---|
| 2pi, 1x | 0.0200 | 0.0201 |
| 4x24 deg, 2pi bins, 4x | 0.0298 | 0.0286 |
| 4x24 deg, own bins, 4x | 0.0333 | 0.0302 |

Adding SBS does nothing at 2pi (0.0200 -> 0.0201) but recovers 4-9% of what a phi
cut costs -- what the FOM geometry predicts, since SBS's 12 (x,Q2) cells sit at or
above SoLID's coverage edge. Neither is enough: the best SBS + phi-cut-at-4x result
is 0.0286 against 0.0201 for SBS + 2pi at nominal luminosity, still 1.4x worse.
**Four times the counts AND the SBS projection do not substitute for azimuthal
coverage.**

**Notebooks narrowed and re-run.** `plot-*_phicompare.ipynb` went from ten entries
to five -- world, sbs, phifull, and the two phi-cut runs at 4x -- with the R1 < 0.3
curves and the 806-bin count binning left to `_x4counts` and `_morebin`. The
`_sbsenhanced3he` pair got the same treatment, and its empty d/u figure was fixed
(it looped `runs_for('syst')` in a notebook that has no syst variant, so it rendered
bare axes with a caption claiming systematics were included).

An experiment drawing the bands at three Q2 (2.4, 5.0, 7.5) was added and then
removed: in the upper panel the curves separate, but the error ratios proved exactly
Q2-independent -- 8.3633643878 for Collins and 8.0218563739 for Sivers at all three,
to ten decimals -- so the extra curves showed nothing. The finding is kept in
`phicompare/README.md` and `physics.md` step 5; the figures are back to one Q2.

---

## 2026-09-08 — `--counts`: what 4x the SoLID statistics actually buys

```
./run_fits.sh -t 0.3      phicompare/data_phi4seg24deg_countbin800   # the missing 1x baseline
./run_fits.sh -c 4        phicompare/data_phi4seg24deg{,_countbin800,_phifullbin}
./run_fits.sh -c 4 -t 0.3 phicompare/data_phi4seg24deg{,_countbin800,_phifullbin}
./fitcollins.py enhanced3he phicompare/data_phi4seg24deg -c 100     # scaling diagnostic
./fitcollins.py enhanced3he phicompare/data_phi4seg24deg -c 10000   #   "
```

New `-c COUNTS` flag on `fitcollins.py`, `fitsivers.py` and `run_fits.sh`: fit the
SoLID pseudodata as if the run had COUNTS times the counts. Every statistical
estimator in `SoLID_SIDIS_3He.h` is `sqrt(.../Nacc)`, so this is exactly
`stat/sqrt(COUNTS)`. For the `*syst` opts the total error is **rebuilt** from its
parts as `sqrt(stat^2/COUNTS + systabs^2 + AUT^2 systrel^2)` rather than scaled
whole -- scaling `error_tot` would shrink the systematic budget with beam time.
World data and the SBS projection are never scaled; the flag is refused, not
ignored, on any opt that loads neither `enhanced3he` set.

ifarm2401, 128 workers, NREP 500. Seven groups, 19:39 -> 21:04 = **1h25m**, all OK.

**Result: 4x the counts does not halve the band.** `gT(u-d)` at Q2 = 2.4,
tol = 7.04, ratio of the 4x band to the 1x band:

| run | stat, no cut | stat, R1<0.3 | stat+syst, no cut | stat+syst, R1<0.3 |
|---|---|---|---|---|
| `data_phi4seg24deg` | 0.78 | 0.66 | 0.87 | 0.96 |
| `..._countbin800` | 0.80 | 0.70 | 0.82 | 0.85 |
| `..._phifullbin` | 0.82 | 0.66 | 0.79 | 0.76 |

Sivers (`f1Tperp` band, tol = 1.5) is the same shape: 0.67-0.75 stat-only uncut,
0.86-0.90 with the cut or with systematics. Central values are unchanged to the
fourth decimal everywhere, as they must be -- only errors moved.

**Why it is not 0.5 is unresolved.** Three candidates were tested and all three
fail:

- *World data anchoring the joint fit.* The obvious test -- world-only band
  (0.2111) against world+SoLID 1x (0.0426) -- is **invalid**: `fitworld` fixes `c`
  and `fitsim` frees it, the comparison `CLAUDE.md` warning 1 forbids. Separately,
  an additive inverse-variance model `u = u_world + N k` fitted to the 100x and
  10000x points predicts 0.0164 at 1x against the 0.0426 measured, so it fails
  quantitatively too.
- *The Collins bimodality* (`fitcollins.py:47`). The secondary-minimum fraction does
  fall with counts, 14.4% -> 5.6% -> 1.0% -> 1.0%. But recomputing the band from
  primary-minimum replicas only leaves the ratio at **0.780 against 0.782** -- it
  is not the cause.
- *Nonlinear saturation of `gT`.* The replica distribution is Gaussian at 1x, 4x
  and 100x (skew -0.19 to -0.09, excess kurtosis ~0), so the band is not being
  compressed by nonlinearity.

What is left, and unexplained: the individual parameter spreads scale about as
expected -- `sd(Nu)` goes 0.1737 -> 0.0785 across 1x -> 4x, a ratio of 0.45 --
while `gT`, a combination of them, goes 0.78. `band/sd(Nu)` climbs 0.245 -> 0.424
-> 0.602 over 1x -> 4x -> 100x, so the parameter correlation structure that `gT`
projects onto changes with statistics. That is where the deficit lives; it is a
property of the fit's degeneracy directions, not of the data. **The 10000x point
is not trustworthy** (skew -1.03, excess kurtosis 9.35, `sd(kt2)` underflowing to
0.0000) and was used only for the failed additive-model check.

Practical reading: quote the measured ratios, not `1/sqrt(N)`. The standing +-20%
run-to-run noise on improvement factors covers most of the spread between the
three runs, so 0.78 / 0.80 / 0.82 are not distinguishable.

---

## 2026-09-07/08 — binning scan for 4x24 deg, rung 800: the curve is flat above ~800 bins

```
./analysis_neutron 4 phicompare/data_phi4seg24deg_countbin800 4 all 24   # count table
./make_bins_from_count.py <that dir>/count_N*.dat -N <per file>          # 806 bins
./analysis_neutron 2 phicompare/data_phi4seg24deg_countbin800 4 all 24
./analysis_neutron 3 ... ; ./prepare.py ...
./run_fits.sh phicompare/data_phi4seg24deg_countbin800                   # on ifarm2401
```

First rung of the bin-count scan planned in
`~/.claude/plans/soft-doodling-toast.md`. Question: what bin count minimises the
**real** error for the 4x24 deg configuration.

| stage | host | wall |
|---|---|---|
| count table (Nsim 8e9, `4 all 24`) | jlabl5 | 22:59:39 -> 00:33:05 = **1h33m** |
| bins (two passes, see below) | — | seconds |
| step 2 (`4 all 24`) | jlabl5 | 00:34:42 -> 01:15:41 = **41 min** |
| step 3 + prepare | jlabl5 | seconds |
| 4 fits, 500 replicas | ifarm2401, 128 workers | **14 min** (154/161/262/269 s) |

### Result: saturation is reached by ~800 bins

$E(g_T^{u-d})$ and the Sivers $\langle k_T^2\rangle$ spread, statistical only —
the only panel comparable across bin counts, since the per-bin systematic
dilutes as 1/N_bins:

| binning | bins | $E(g_T^{u-d})$ | vs `_fullbin` | std(kt2) | vs `_fullbin` |
|---|---|---|---|---|---|
| own bins | 169 | 0.0355 | **1.154x** | 0.00906 | **1.395x** |
| **countbin** | **806** | **0.0305** | **0.992x** | **0.00666** | **1.026x** |
| `_fullbin` | 1660 | 0.0308 | 1.000x | 0.00649 | 1.000x |

**806 bins is statistically indistinguishable from 1660** (0.8% and 2.6%, both
inside the 3.2% replica-sampling floor), while 169 is clearly worse. The curve
descends from 169, flattens by ~800, and stays flat to 1660.

Three consequences:

- **The `stat = A x systrel` criterion is too coarse for this configuration.** It
  selects 166 bins — and `GenerateBinInfoFile`'s own-bins run has 169, so both
  encode the same "bin until stat reaches the systematic floor" rule. Both sit in
  the rising part of the curve and cost 15-40%.
- **`_fullbin`'s 1660 bins are not better than 800.** Beyond ~800 nothing real is
  bought.
- **~800 is the practical sweet spot**: full saturation at half the bin count, so
  half the step-2 cost and half the exposure to the systematic-dilution artifact.

Caveat: the 806 run differs from `_fullbin` in *placement* as well as count, so
the agreement says neither matters in that range — it does not isolate placement.

### Verification

- φ cut applied at both opt 4 and opt 2 — banner read
  `azimuthal cut: 4 sectors of 24 deg = 26.6667% of 2pi` each time. Running step 2
  without those arguments would have silently produced a 2π run on 4seg-adapted
  bins and looked like a huge gain.
- **Total Nacc 1.3483e9 against the control's 1.345e9 — 0.2%.** Same acceptance,
  same physics, reached by a completely different binning route. The count
  table's own per-file totals also matched the `_fullbin` run's within 0.8%.
- rows = bins = 806; ndof 946 = 806 + 146 − 6 (Collins).
- The $g_T$ calculation used here reproduces the notebook's published 0.0355 and
  0.0308 exactly, which is what makes the 806 row trustworthy.

### Note for the next rung

The `-N` -> bin-count calibration is **not** the 0.968 measured on
`countbin1e6`; at these bin counts it runs 0.99-1.06, so the first pass gave 769
against a target of 800 and needed one adjustment to land 806. Compute `-N` from
the count table's own total and expect to iterate once.

**Rung 400 is the informative next step** — saturation begins somewhere between
169 and 806, and 400 would bracket it. The count table is already paid for, so
that rung is ~20 min of step 2 plus ~10 min of fits. Not run.

---

## 2026-09-06/07 — the count-table binning run end to end (steps 2, 3, prepare, fits)

```
./run_countbin_chain.sh                                    # jlabl5: steps 2, 3, prepare
./run_fits.sh phicompare/data_phifull_countbin1e6          # ifarm2401: the four fits
```

New run directory **`phicompare/data_phifull_countbin1e6`**, whose
`bin_enhanced_*.dat` are `make_bins_from_count.py` output at N = 1e6 — **19074
bins** against the 1660 of `phicompare/data_phifull`. A separate directory
because opt 2/3, `prepare.py` and the fit scripts all use hardcoded output
names, so running in place would have overwritten the baseline. `data_phifull`
was verified untouched throughout (checksums and 2026-08-27 mtimes).

| stage | host | wall |
|---|---|---|
| step 2 (`AnalyzeEstatUT3`) | jlabl5, 4 jobs | **9356 s = 2h36m** |
| step 3 (`CreateFile`) | jlabl5 | 2 s |
| `prepare.py` | jlabl5 | 9 s |
| 4 fits, 500 replicas | ifarm2401, 128 workers | **2h47m** |

**Step 2 cost 2h36m, not the 17 h first projected.** The estimate assumed thin
bins would run `AnalyzeEstatUT3`'s full 1e7 throws; the opposite happens.
`SetRange` confines sampling to the bin, so a small bin sitting inside the
acceptance has a HIGH pass fraction and reaches the `Nrec > 100000` early exit
sooner. Measured 1.24 s per bin against 7.1 s for the old fat bins — **5.7x
cheaper each**, so 11.5x more bins cost only ~1.7x the wall time.

**The fits had to move to ifarm.** At 19074 rows and 4 workers on jlabl5 they
projected to 30.6 h each, 122.6 h for four; at 128 workers on ifarm2401, 1.0 h
each. Actual: Collins 1059/1094 s, Sivers 3942/3955 s. The chain driver was
stopped after `prepare.py` and the fits relaunched on ifarm; no `out-*.dat` had
been written locally, so nothing partial survives.

**Row bookkeeping reconciles exactly at every stage** — nothing lost between the
count table and the fit:

    bin files    8654 + 5725 + 2867 + 1828       = 19074 bins
    step 3 CSVs  11521 (pip = N11p+N8p) + 7553 (pim = N11m+N8m) = 19074
    prepare      simenhanced3he.dat              = 19074 rows
    fit ndof     Collins 19074 + 146 - 6  = 19214   (world 146, 6 free)
                 Sivers  19074 + 234 - 9  = 19299   (world 234, 9 free --
                 fitsivers.py:354 fixes Nub and Ndb)

The same arithmetic on the 1660-bin baseline gives 1800 and 1885, matching its
outputs, so the world data was neither cut nor resampled in either run.

**chi2/ndof moved toward 1 with the finer binning**, as more bins should:

| | 1660 bins | 19074 bins |
|---|---|---|
| Collins | 0.9196 | **0.9922** |
| Sivers | 0.8767 | **0.9877** |

Disk: 29 GB of `_hs.root` in the new directory (1.57 MB per bin measured, against
the 1.4 MB quoted in `CLAUDE.md`).

**Not yet done:** no comparison of the new bands or g_T against the baseline.
The two runs have different bin counts, so per the standing warnings they are
comparable through bands and g_T, not parameter by parameter.

---

## 2026-09-06 — count table at 0.02/0.05/0.02/0.02, and bin files built from it

```
./analysis_neutron 4 phicompare/data_phifull                     # 8e9 events x 4 jobs
./make_bins_from_count.py phicompare/data_phifull/count_N*.dat   # N = 1e6 (default)
```

Step 4 ran 18:51:43 -> 20:38:46 EDT — **1h47m**, exit 0, on `jlabl5`, peak RSS
261 MB. Supersedes the 2026-09-04 coarse-grid table in the same directory.

**Changes to `MakeCountTable` since that run:** widths 0.05/0.1/0.05/0.05 ->
**0.02/0.05/0.02/0.02** (a 35 x 180 x 20 x 100 = 12.6e6 cell grid, 31x finer);
the `phi_h`/`phi_S` circular-mean columns removed; a `relerr` column added,
`sqrt(sum w^2)/sum w`, in which the `lumi*time*eff/Nsim` scale cancels so it is
a pure fractional error.

| file | cells | accepted of 8e9 | median Nmc | >=100 Nmc | yield in those |
|---|---|---|---|---|---|
| `count_N11p.dat` | 981420 | 232,119,962 | 187 | 79.2% | 96.60% |
| `count_N11m.dat` | 981383 | 231,868,218 | 187 | 79.2% | 96.60% |
| `count_N8p.dat` | 320598 | 63,726,834 | 153 | 70.2% | 96.35% |
| `count_N8m.dat` | 320619 | 63,647,445 | 153 | 70.2% | 96.43% |

Nsim = 8e9 was projected to give a median near 100 and delivered 187/153; the
8.8 GeV beam was the binding constraint, its accepted fraction being 0.8%
against 11 GeV's 2.9%. As at the coarse widths, ~20-30% of cells still fall
below 100 events — edge-of-phase-space cells keep appearing as statistics grow —
but they carry only ~3.5% of the yield.

**`make_bins_from_count.py` (new)** turns a count table into a bin file in
`bin_*.dat` format by k-d bisection: bisect the occupied grid along the axis it
spans most cells on, at the point most evenly dividing N_acc, until a box holds
under 1.5x the target. It is a partition, so every populated cell lands in
exactly one bin, verified before writing by summing leaves back to the table
total. It refuses to write any path starting with `bin_enhanced`.

| file | bins | median N_acc | in [0.75,1.5]x | bins with >=100 MC events |
|---|---|---|---|---|
| `bin_count_N11p.dat` | 8654 | 9.74e5 | 77.2% | 99.6% |
| `bin_count_N11m.dat` | 5725 | 9.72e5 | 77.6% | 99.8% |
| `bin_count_N8p.dat` | 2867 | 9.64e5 | 75.1% | 99.8% |
| `bin_count_N8m.dat` | 1828 | 9.85e5 | 77.2% | 99.9% |

**Target 1e6, not the 1e5 first tried.** At 1e5 the target sits *below* what many
single count-table cells already hold, so 12.6% of bins could not be split down
to size (8757 of 69531 on a test file) and the run would have produced ~223000
bins across the four files. At 1e6 that floor vanishes entirely — no bin exceeds
1.5x target in any of the four — and the set is 19074 bins, 11.5x the 1660-bin
production set, so a step 2 over it would take roughly **18 h** against 1h33m.
**Nothing has been run on these bin files yet.**

`bin_enhanced_*.dat` are untouched (mtime still 2026-08-27).

---

## 2026-09-04 (evening) — opt 4, the (x,Q2,z,pT) count table on data_phifull

```
./analysis_neutron 4 phicompare/data_phifull      # 1e9 events x 4 jobs
```

Started 23:18:19, finished 23:31:19 EDT — **13 min**, exit 0, on `jlabl5`
(4 cores; opt 4 forks exactly 4 jobs, one per beam/charge, so more cores would
not help). New in this run: `MakeCountTable` (`SoLID_SIDIS_3He.h`) and opt 4 in
`analysis_neutron.C`. Output, all new files, nothing overwritten:

| file | cells | accepted of 1e9 | size |
|---|---|---|---|
| `count_N11p.dat` | 41747 | 29,020,657 | 9.0 MB |
| `count_N11m.dat` | 41746 | 28,982,476 | 9.0 MB |
| `count_N8p.dat` | 14667 | 7,965,649 | 3.2 MB |
| `count_N8m.dat` | 14658 | 7,955,455 | 3.2 MB |

Grid 0.05 (x) x 0.1 (Q2) x 0.05 (z) x 0.05 (pT) over x[0,0.7] Q2[1,10] z[0.3,0.7]
pT[0,2] — 403200 cells, stored sparsely. Per cell: `weight*acc`-weighted means of
x, Q2, z, pT, y, W, W', the circular means of phi_h and phi_S with their
resultant lengths, and `Nacc`/`dNacc`/`Nmc`.

**Nsim = 1e9 was chosen from measurement.** The occupied-cell count saturates by
~6e7 events (31776 → 37119 → 39066 at 5e6 → 2e7 → 6e7), after which population
grows linearly; median cell held 34 events at 6e7, so 1e9 projects to ~570.
Achieved median 538 (11 GeV) / 388 (8.8 GeV).

**"at least 100 events in every cell" is not reachable**, and this run shows why:
82.6% of cells (11 GeV) and 77.3% (8.8 GeV) clear 100, with p10 = 29 and 23. New
edge-of-phase-space cells keep appearing as statistics grow. What matters is that
they carry almost no yield: **99.48% of total `Nacc` sits in cells with >=100
events**. Read the `Nmc` column before trusting a single row.

**mean R(phi_h) = 0.51, mean R(phi_S) = 0.09.** phi_S is uniform as expected —
nothing in the generation or the acceptance depends on it, and 0.09 is the
1/sqrt(N) noise floor for these cell populations. phi_h is *not*: even in this
full-2pi run the 8–18 deg hadron acceptance concentrates phi_h substantially
inside a kinematic cell, because the hadron's lab angle depends on phi_h. That is
the same effect `FOM/README.md`'s grid section documents from the other
direction, now measured per cell.

Order-of-magnitude cross-check: summed `Nacc` is 8.38e9 (N11p) + 2.75e9 (N8p),
so ~2.2e10 over both charges, against 1.84e10 across `simenhanced3he.dat`'s 1660
bins. The two do not tile the same region, so this is a consistency check, not an
equality.

---

**Directory move, 2026-08-27.** The three run directories of the MUT3 estimator
study were moved into `SIDIS_MUT3_comparison/` and renamed with a
`_phisfold_bin10deg` suffix recording the options they were produced under
(`phisfold=fold`, and the 36-bin = 10 deg azimuthal histogram). Commands in the
entries below are written with the final paths so they reproduce as read; they
were typed with the shorter names.

**The `_phifullbin` symlinks broke in the move and were repaired the same day.**
The move left eight dangling `bin_enhanced_*.dat` links — four in
`data_4pi_phifullbin_phisfold_bin10deg` and four in the unrelated
`data_phi4seg24deg_phifullbin` — all pointing at the old top-level
`data_phifull/`. Both now resolve to
`SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg/`, which carries the same
1660 bins (782 N11p + 536 N11m + 204 N8p + 138 N8m) byte-identical to the
directory they were originally built from. Existing outputs were never affected —
the links are read only during step 2 — and both directories' trees hold 1660
entries, matching the bins they now point at.

---

## 2026-09-02 (evening) — the R1 < 0.3 TMD-cut sweep: 22 fits, never logged until now

```
setsid nohup ./run_tmdcut_sweep.sh > tmdcut_sweep.log 2>&1 < /dev/null &
```

Run on `ifarm2401.jlab.org` (128 workers, half of 256) via the driver
`run_tmdcut_sweep.sh`, six `./run_fits.sh -t 0.3 <rundir> [opt]` invocations in
sequence:

```
data_other sbs
phicompare/data_phifull
phicompare/data_phi4seg24deg_phifullbin
phicompare/data_phi4seg24deg
phicompare/data_phi4seg24degFA_phifullbin
phicompare/data_phi4seg24degFA
```

Started 18:46:55, finished 20:00:22 EDT -- 1h13m, exit 0. 22 fits total (sbs:
Collins+Sivers; each of the other five: `enhanced3he` + `enhanced3hesyst` x
Collins+Sivers), all `OK`. `-t 0.3` keeps only simulated rows with collinearity
$R_1 < 0.3$ (`tmd.CalculateRfactor`, arXiv:1611.10329; see `physics.md`) --
**world data is never cut**, by construction (`code.md` step 6), verified on
all 22 outputs via `ndof = world_rows + sim_rows - n_free` recovering the exact
uncut world row count (146 Collins / 234 Sivers) every time. Output is
`out-<opt>_<obs>_r1lt0.3.dat`, beside each uncut result, never overwriting it.

Simulated rows kept, matching pre-run predictions: sbs 320/455, `phifull`
928/1660, `phi4seg_fullbin` 859/1660, `phi4seg` 106/169, `phi4segFA_fullbin`
896/1660, `phi4segFA` 167/239. The `sbs` fit used the 455-row **uncut** SBS
projection (switched from the 289-row cut vintage earlier the same day, see
above), so its 320-row cut result is not comparable to any `r1lt0.3` SBS number
from before today.

**Notable: chi2/ndof moved the wrong way.** Every one of these was already below
1 uncut (the standing unexplained low-chi2 issue); the cut pushed it *further*
down in all six configs rather than toward 1 -- e.g. Collins `phifull` 0.864,
`phi4seg` 0.418. If the discarded high-$q_T$ rows were the ones the TMD model
fits badly, chi2/ndof should have risen, not fallen. Unresolved.

**Nothing currently plots these.** The two `phicompare` notebooks were briefly
extended same-day to show the cut fits (first an `sbs_tmd` curve, then a proper
third `'cut'` variant reusing `band_plot`), then fully reverted at request. The
22 `out-*_r1lt0.3.dat` files are the only record of this run; a reader who finds
them and wonders why nothing renders them, this is why.

---

## 2026-09-02 — the SBS projection switched to its uncut source

```
root -l -b -q dump_sbs.C            # from the repo root; ~2 s
./prepare.py data_other --sbs       # ~40 s
```

`data_other/simsbs_{collins,sivers}.dat`, **455 rows** each (233 pi+ from
`sbs01_root.dat`, 222 pi- from `sbs02_root.dat`), mean |value| 0.04957 Collins /
0.02079 Sivers. No fit was run.

**`prepare.py --sbs` now reads `sbs0{1,2}_root.dat` and nothing else.** It used
to read `sbs0{1,2}.dat`. Those are the same experiment (E12-09-018) but not the
same dataset: the plain pair is a 289-row subset with `z > 0.3` and a
`q_T <~ 0.6 Q` cut already applied. Every one of its rows matches a `_root` row
to better than 2e-4; 166 `_root` rows have no partner. The 289 rows the two share
agree to 1.1e-4 (Collins) / 1.9e-5 (Sivers), which is the ROOT files' 5-figure
storage of x/Q2/z propagating through the model, not a disagreement.

| | rows | z | q_T/Q | mean abs value (Collins) |
|---|---|---|---|---|
| uncut `_root` (now the default) | 455 | 0.236-0.696 | 0.067-1.376 | 0.04957 |
| cut, in `sbs_cut/` | 289 | 0.307-0.695 | 0.067-1.315 | 0.04525 |

**Before fitting the uncut set, know what it contains.** It reaches z = 0.236 and
q_T/Q = 1.38, outside where the TMD factorisation in `tmd.py` is expected to
hold -- that is exactly what the cut vintage removes. Legitimate to fit, but the
parameters would be drawn partly from kinematics the model does not claim to
describe. See `physics.md` on the region criteria.

**Directory move (by hand, same day).** The cut chain -- `sbs0{1,2}.dat`,
`simsbs_*.dat`, `out-sbs_*.dat`, its fitlog, `sbs_old/`,
`plot_simsbs_new_vs_old.py` -- moved into `data_other/sbs_cut/`. Only the uncut
`sbs0{1,2}_root.dat` stayed at `data_other/` level, because `FOM/` reads them
there. `dump_sbs.C` moved to the **repository root**; its defaults are now
`../LiuSIDIS/SoLID/FOM_comparison` -> `data_other`. Nothing broke: every stage
takes a `<rundir>`, so `./run_fits.sh data_other/sbs_cut sbs` still fits the cut
chain and world data resolves through `WORLDDIR`, not `<rundir>`. Verified
`FOM/plot_fom_solid_vs_sbs.py` unchanged after the move (SBS 455 -> 391 rows
after cuts, x = 0.15-0.25 bin 8.504e+06 on 102 rows). `clas0{1,2}.dat` and
`clas_old/` were removed deliberately; nothing in the pipeline read them.

**One-way consequence.** `sbs_cut/`'s prepared files can no longer be
regenerated by `prepare.py` -- it would look for `sbs_cut/sbs01_root.dat`, which
does not exist. They remain valid on disk and still fit; they are simply no
longer reproducible without pointing `prepare_sbs()` back at the cut pair, or
renaming the cut files to the `_root` names inside `sbs_cut/`.

**Also fixed, no run attached.**

- **`PAR['pretzelosity']` corrected** from `a = 2.2, MT2 = 0.21` to
  `a = 2.5, MT2 = 0.18` -- Table III of Lefky and Prokudin, Phys. Rev. D **91**,
  034010 (2015), [arXiv:1411.0580](https://arxiv.org/abs/1411.0580)
  (JLAB-THY-14-1885), checked against both arXiv versions, which are identical
  here. The old pair matched no published source. The null-test figure in
  `code.md` was likewise wrong, 76% -> **72%** (P(163.48, 175)).
  **The five prepared `simenhanced3he.dat` were NOT regenerated** -- held off
  deliberately; `AUTPretzelosity` there is stale by a median 31.5%. Tracked as
  `bug.md` item 12. Nothing downstream reads the column.
- **The R-factor now carries its reference.** `Lsidis3.h:CalculateRfactor` is the
  collinearity of Boglione, Collins, Gamberg, Gonzalez-Hernandez, Rogers, Sato,
  Phys. Lett. B **766** (2017) 245 [arXiv:1611.10329], Eqs. 28-32, and the code
  matches it line for line apart from retaining the `PhT.kT` term the paper drops
  on azimuthal averaging. Measured: `Rfactor` never exceeds ~85 (production
  defaults) or ~202 (physical parameters) over `data_phifull`, against
  `Rfactor0 = 1e5` -- **the cut rejects nothing**. The published thresholds are
  ~0.2 (2017) and 0.3 (2022, JHEP 04 (2022) 084 [arXiv:2201.12197]), which would
  cut 44-73% of bins. `physics.md` corrected: it had said the cut "removes very
  little".

---

## 2026-09-01 — the SBS projection re-prepared, and a stale Collins truth found

```
./prepare.py data_other --sbs          # sbs01.dat + sbs02.dat -> simsbs_{collins,sivers}.dat
./run_fits.sh data_other sbs           # 500 replicas, 100 workers on ifarm2401; 76 s + ~110 s
```

289 rows (148 pi+ from `sbs01.dat`, 141 pi- from `sbs02.dat`). Previous copies of
all four files were kept by hand in `data_other/sbs_old/`.

**Sivers reproduced the previous file exactly; Collins did not.**

| obs | rows | max abs diff | max rel diff | bitwise equal |
|---|---|---|---|---|
| sivers | 289 | 1.041e-16 | 1.538e-13 | 275/289 |
| collins | 289 | 4.091e-02 | 9.763e-01 | 0/289 |

`sbs_old/simsbs_collins.dat` carries `obs = AUTsivers` on all 289 rows -- it was
written by a path that never relabelled the observable -- and its values follow
the same `tmd.AUTCollins` model evaluated with an older, smaller parameter set.
Refitting the six Collins parameters to it drops the residual rms 56x, from
2.31e-2 to 4.14e-4:

| | Nu | Nd | a | b | c | kt2 |
|---|---|---|---|---|---|---|
| refit to the old file | 0.175 | -0.180 | 0.779 | 2.931 | 0.583 | 0.250 |
| today's `PAR['collins']` | 0.400 | -0.450 | 1.000 | 3.000 | 0.000 | 0.250 |

`kt2` lands on 0.2504, so the model is the same and only the transversity shape
differs. The residual does not reach zero (7.6% max), so a code vintage
difference sits on top of the parameter one.

**It changed nothing downstream, and the reason is worth knowing.**
`simulate()` (`fitcollins.py:281`) refits the world data and then *overwrites*
`simdata['value']` with the model at that best fit, so a `simsbs_*.dat` `value`
column never reaches the fit -- only its kinematics and its `error` do. The two
SBS fits, one on each truth, agree to minimiser noise: Collins chi2/ndof 0.6655
both times, `Nu` mean 0.5221 against 0.5230. The `value` column is documentation,
not input. Anything that *does* read it -- the notebooks' comparison plots --
must use the new file.

`data_other/plot_simsbs_new_vs_old.py` draws the comparison
(`simsbs-new-vs-old.png` / `.pdf`) and carries the finding in its docstring.

**Still unexplained:** the SBS fits sit low, chi2/ndof = 0.665 (Collins, ndof
429) and 0.553 (Sivers, ndof 514), against world's 0.997. At ndof ~ 430 that is
~4.9 sigma below 1. Note also that the `sbs` opt fits **world + SBS**, not SBS
alone (ndof 429 = 146 + 289 - 6), so it must not be labelled SBS-only.

**Notebooks.** `phicompare/plot-{transversity,sivers}_phicompare.ipynb` now point
at the new `data_other/out-sbs_*.dat` (500 replicas, current schema) and draw SBS
in the **stat-only** panel alone. SBS is an external projection with no
systematics model of its own, so repeating its single fit unchanged in the
stat+syst panel invited reading it as a stat+syst result. The mechanism is that
`RUNS['sbs']['files']` has no `'syst'` key and every loop iterates a new
`runs_for(suffix)` helper, so a run appears in exactly the panels it has a fit
for.

The original SBS fit was briefly added beside it as `sbs_old`
(`data_other/sbs_old/out-sbs_{collins,sivers}_old.dat`, 50 and 30 replicas in the
pre-`_err`/`ndof`/`edm` schema) and then **removed again the same day at the
author's request** -- the notebooks carry `sbs` only. Recorded here because the
measurement made while choosing which file to plot is worth keeping: the
500-replica `sbs_old/out-sbs_{collins,sivers}.dat` in that same directory is
**not** a second data point. It agrees with the current fit to minimiser noise:

| | chi2/ndof | Nu mean | max row diff |
|---|---|---|---|
| collins | 0.6655 both | 0.5221 vs 0.5230 | 0.080 |
| sivers | 0.5534 both | -0.03538 vs -0.03538 | 0.008 |

**Why those two differ at all, given identical statistics.** They were not fit on
identical input: the older `simsbs_collins.dat` went through an extra float
round-trip, so 36 kinematic and 14 `error` entries differ by one ulp
(`0.34299999999999997` against `0.343`, adjacent doubles). That 1-ulp difference
is amplified because `_fitsim_one` floats all six parameters including `c`, which
is nearly degenerate with `Nu` and `a` in
`(1 + 0.2 sqrt(x) + c x^0.25) x^a (1-x)^b`. Migrad then stops loosely -- median
edm 4.4e-5 against the world fit's 6.7e-6, with 3.6% of replicas ending above
1e-3 (max 5.0) -- and those are the replicas that move: median |dNu| 2.7e-2 where
edm > 1e-3 against 3.0e-4 where edm < 1e-3, a factor 90.

The motion is along the flat direction, so nothing physical changed. At a
representative kinematic point the predicted A_UT shifts by a median 8.7e-6
relative against Nu's 7.6e-4, and the ensemble widths -- the only thing the
notebooks read -- agree to 0.03%: std(A_UT) ratio 1.000268, std(Nu) ratio 0.994.
**Do not read a parameter-level difference between two runs of this fit as a
change in the fit.** A determinism check re-fitting the same file twice was
started and stopped before finishing; it is still unconfirmed that the input ulp
difference is the *only* source.

Both notebooks re-executed clean; all six `phicompare/gallery/*.pdf`
regenerated.

---

## 2026-08-31 (night) — `gt_fast`: the tensor charge 780x faster, and three notebooks rebuilt

No generator run. `tmd.py` gained `gt_fast()` beside the untouched `gt()`, and the
notebooks were rewritten to work in this repo at all.

**Why.** `gt()` calls `scipy.quad` twice per replica and quad picks fresh
abscissae each time, so every replica re-queries LHAPDF. Measured: **83.3 ms per
replica**, and it hits quad's 50-subdivision limit -- an `IntegrationWarning` --
on both the truncated and the full range. In
`plot-transversity_phicompare.ipynb` that was **96% of the runtime**: h1calc
~1.2 min against gtcalc ~32 min for 12 parameter sets x 500 replicas.

**What `gt_fast` does.** Gauss-Legendre on a fixed grid, `n=256`, in **log x**
(the substitution matters: the default range starts at 1e-5 where the integrand
goes as x^(a-1.2), and linear nodes give only 1.7e-4 against quad at n=64 where
log gives 2.0e-6). `_gl_grid` is `lru_cache`d on (n, xl, xu, Q2) and holds the
LHAPDF values at the nodes, which do not vary between replicas -- so the PDF
lookups happen once and each replica is two dot products.

| | gt() | gt_fast() |
|---|---|---|
| per replica, truncated | 83.3 ms | **0.107 ms** (778x) |
| agreement, truncated 0.05-0.6 | -- | u 1.1e-9, d 9.2e-9, u-d 4.3e-9 |
| agreement, full 1e-5-1.0 | -- | u 8.0e-7, d 2.2e-7, u-d 3.9e-7 |

The full-range floor is **quad's** accuracy, not gt_fast's -- quad is the one
giving up at 50 subdivisions there.

**The integrand was transcribed, not re-derived**, and that was verified: `shape`
is h1col's own expression with the flavour factors (Nu/Nd and the PDF index)
pulled out, and it matches h1col point by point to **4.4e-16** -- two ulps -- over
4 replicas x 7 values of x from 1e-4 to 0.9. Two assumptions were checked because
either would break it silently: h1col calls `f1col` with no target (always proton,
which is what gt uses), and it zeroes the antiquarks and s/c/b. Both are recorded
in the `gt_fast` docstring.

**Notebook wall time, same machine, same results:**

| notebook | before | after |
|---|---|---|
| `phicompare/plot-transversity_phicompare.ipynb` | ~45 min | **1m49s** |
| `data_other/plot-transversity_replica.ipynb` | 50 s | **13 s** |

Every printed number is unchanged -- the gT improvement factors come out at
15.86x / 8.71x for phifull and identically down the table, which is the check
that matters for a 780x speedup.

`plot-sivers_phicompare.ipynb` was **not** re-run: it calls only
`tmd.f1Tperp1`, a closed form with no integration anywhere, so `gt_fast` has
nothing to act on there.

**The three notebooks could not run in this repo before today.** All read
upstream paths (`seedtest/`, `outputcollins*`, `output*`) and imported
`tmdlib.tmd`, which does not exist here. They now import the repo's `tmd`, read
the local run directories, and cover the five configurations that exist:
phifull, 4x24deg both-arms and FA, each with `_phifullbin` and own-bins variants.

**An environment trap fixed on the way.** `module load root` points
`JUPYTER_CONFIG_DIR` and `JUPYTER_PATH` into the read-only ROOT install, so any
jupyter command run after `setup.sh` dies with
`PermissionError: .../etc/notebook/migrated` before executing a cell.
`setup.sh` and `setup.csh` now set `JUPYTER_CONFIG_DIR`, `JUPYTER_DATA_DIR`,
`JUPYTER_RUNTIME_DIR` and `IPYTHONDIR` under `$HOME`; `start_jupyter.sh` (moved
to the repo root, where its `. ./setup.sh` and its Jupyter root dir both resolve)
lost the `unset` that used to work around it.

**The error bar is reproduced, not just the central value** -- checked, because
that is the quantity actually quoted (`tol * std` over replicas) and a per-replica
agreement says nothing about a spread on its own. Over 200 replicas of the
phifull Collins ensemble:

| range | std(gt_fast)/std(gt) | corr |
|---|---|---|
| truncated 0.05-0.6 | 0.999999999 | 1.000000000000 |
| full 1e-5-1.0 | 0.999964585 | 0.999999998537 |

It reproduces the error *better* than the central value, structurally: the
difference is almost entirely a constant offset (truncated: mean 3.2e-9, scatter
1.1e-11) and a constant cancels exactly in a standard deviation.

**The full-range residual is quad's, not gt_fast's.** Two independent grids agree
with each other ~270x better than either agrees with quad, and refining gt_fast
does not move the disagreement -- 7.2e-10 between n=256 and n=1024, against
1.9e-07 for either against quad. That is what a 50-subdivision failure looks
like: quad fails by a different amount per replica, where a fixed grid is smooth
in the parameters.

For scale: at 500 replicas the error bar carries **3.2%** sampling noise by
construction, against **0.0035%** from the integration method -- a factor of ~900.

**Still open:** all of the above compares gt_fast against gt, so it establishes
consistency, not correctness. `gt()`'s `IntegrationWarning` is a correctness
question in its own right -- the published gT numbers come from a quad that gives
up at 50 subdivisions -- and is not addressed by adding a faster path beside it.
This measurement mildly strengthens the case for looking at it, since the
full-range disagreement is now attributable to the quad side.

---

## 2026-08-31 (night) — `data_phi4seg24degFA_phifullbin`: FA cut on phifull's bins

17:47:46 → 19:14:21 = **1h26m35s**, exit 0, **zero** warnings, zero rows dropped
by `prepare.py`, 795 MB.

```
ln -sfn ../data_phifull/bin_enhanced_*.dat data_phi4seg24degFA_phifullbin/   # 1660 bins
./analysis_neutron 2 data_phi4seg24degFA_phifullbin 4 FA   1:26:32.84  (218% cpu)
./analysis_neutron 3 data_phi4seg24degFA_phifullbin            0.90 s
./prepare.py data_phi4seg24degFA_phifullbin                    1.52 s
```

**Step 1 was not run, by design.** `_phifullbin` means the run reuses
`data_phifull`'s step-1 bins; generating its own would make the suffix a lie and
break the 1:1 pairing the directory exists for. Queued behind the own-bins FA run
rather than run beside it -- this machine has 4 cores and each step 2 forks four
children, so concurrent runs would just halve each other.

**This is the like-for-like FA measurement.** With all 1660 phifull bins it pairs
row by row with `data_phifull` and with `data_phi4seg24deg_phifullbin`, which the
own-bins FA run cannot do:

| paired against phifull, same 1660 bins | Sivers | Collins |
|---|---|---|
| 4x24 deg, `phiscope=all` | 3.782 | 4.319 |
| 4x24 deg, `phiscope=FA` | **3.444** | **3.745** |

Median ratio of `error_stat`; p95 12.3-13.5 for FA against 16.6-17.0 for
all-scope. **Restricting the cut to the forward angle recovers about 13% of the
statistical cost** on Collins (4.32 -> 3.75) and 9% on Sivers, and shortens the
tail as well. Median `error_stat_collins` 0.01519 against 0.01652.

**No starved bins, contrary to expectation.** `runlog_old.md` records the 2x24 deg
FA `_phifullbin` run dropping 32 rows with `Nacc = 0`, and inheriting bins carved
under the full acceptance is exactly the setup that produces them -- but the
minimum `Nacc` here is **32.7**, low but populated, and `prepare.py` dropped
nothing. Four sectors of FA keep enough more than two that no phifull bin empties.

`simenhanced3he.dat`: 1660 rows, 26 columns, zero non-finite values.

**Disk.** 795 MB, the `_hs.root` maps at 1 deg dominating. The four directories
added today (`data_phi4seg24deg` 87 MB, `data_phi4seg24degFA` 186 MB, this one
795 MB, plus `data_phifull` from earlier) put the working tree well past 8 GB;
none of it is in git.

---

## 2026-08-31 (evening) — `data_phi4seg24degFA`: the same cut, forward angle only, own bins

17:29:35 → 17:47:29 = **17m54s**, exit 0, **zero** warnings, zero rows dropped by
`prepare.py`, 186 MB.

```
./analysis_neutron 1 data_phi4seg24degFA 4 FA     4:29.41  (351% cpu)
./analysis_neutron 2 data_phi4seg24degFA 4 FA    13:22.63  (207% cpu)
./analysis_neutron 3 data_phi4seg24degFA             0.79 s
./prepare.py data_phi4seg24degFA                     0.87 s
```

`phiscope=FA` puts the four sectors in front of the forward angle only; a
large-angle electron is kept at any phi. The run banner says so explicitly
("forward angle only; large-angle electrons keep full 2pi").

**239 bins** — 121 N11p + 79 N11m + 24 N8p + 15 N8m, against 169 for the same cut
at `phiscope=all`. Keeping the large-angle electrons buys 41% more bins, which is
the cleanest single number for what the FA-only restriction is worth.

**It sits between the uncut run and the all-scope cut, as it must:**

| own-bins run | bins | median `error_stat_collins` |
|---|---|---|
| `data_phifull` (no cut) | 1660 | 0.00354 |
| `data_phi4seg24deg` (4x24, all) | 169 | 0.00474 |
| `data_phi4seg24degFA` (4x24, FA) | 239 | 0.00676 |

Note the ordering: the FA run has *more* bins and a *larger* median statistical
error than the all-scope run. Not a contradiction -- more surviving events let the
adaptive binning subdivide further, so each of its 239 bins holds fewer events
than each of the other's 169. Comparing medians across runs with different
binnings compares bin widths as much as acceptances. Only the `_phifullbin`
variants are like-for-like.

`simenhanced3he.dat`: 239 rows, 26 columns, zero non-finite values, mean
`AUTCollins` -0.02434.

**No starved bins this time.** `runlog_old.md` records the 2x24 deg FA run
dropping 32 rows with `Nacc = 0`; that was a `_phifullbin` run inheriting bins
carved out under the full acceptance. This one bins under its own acceptance, so
every bin is populated by construction.

---

## 2026-08-31 (evening) — `data_phi4seg24deg`: the 4x24 deg cut on its OWN bins, full chain

16:32:48 → 16:48:56 = **16m08s**, exit 0, **zero** warnings of any kind (no
`non-positive diagonal`, no NaN, no skipped rows).

```
./analysis_neutron 1 data_phi4seg24deg 4     4:29.93  (361% cpu)
./analysis_neutron 2 data_phi4seg24deg 4    11:35.02  (201% cpu)
./analysis_neutron 3 data_phi4seg24deg          0.91 s
./prepare.py data_phi4seg24deg                  1.87 s
```

87 MB. The directory did not exist beforehand; this is a fresh generation, not a
re-run over old contents.

**169 bins** — 85 N11p + 56 N11m + 17 N8p + 11 N8m, reproducing the historical
count for this configuration exactly (`runlog_old.md` and the 2026-08-26 entry
below both give 169). Under 26.67% of the azimuth the adaptive binning has far
less rate to subdivide, so it stops at roughly a tenth of phifull's 1660.

| | rows | mean AUT | median error_stat | median error_tot |
|---|---|---|---|---|
| Sivers | 169 | -0.01850 | 0.00478 | 0.00593 |
| Collins | 169 | -0.02443 | 0.00474 | 0.00890 |
| Pretzelosity | 169 | +0.00160 | 0.00475 | 0.00495 |

`simenhanced3he.dat`: 169 rows, 26 columns, zero non-finite values.

**It pairs with nothing.** 169 rows against the 1660 of `data_phifull` and
`data_phi4seg24deg_phifullbin`, so no row-by-row comparison with either is
possible, and `phicompare/plot_errors.py` declines the ratio figure for it by
design (it checks the row counts). The comparison to make with a cut run is
always the `_phifullbin` variant.

**Its median statistical error is 3.5x SMALLER than the same cut on phifull's
bins** — 0.00474 against 0.01652 for Collins. Not a contradiction: its bins are
~10x wider in rate, so each holds far more events. Bin width and error move
together, which is exactly why row counts have to match before two runs are
compared.

**Configuration differs from the 2026-08-26 run of the same directory name.**
That one was built at `NPHI = 36` (10 deg) with folded `phi_S`; this one is the
current default, `NPHI = 360` (1 deg) with signed `phi_S`, and its CSV carries the
17-column schema with per-amplitude `stat_*`. Timings match that run closely
(4:29.93 vs 4:23.59 for step 1, 11:35.02 vs 11:26.88 for step 2), so the extra
histogram resolution costs almost nothing here -- event generation dominates.

---

## 2026-08-31 (later) — pretzelosity rebuilt from Lefky-Prokudin; steps 3 + prepare on two directories

```
./analysis_neutron 3 data_phifull                     -> enhancedNpi{p,m}.csv, 1660 rows
./analysis_neutron 3 data_phi4seg24deg_phifullbin     -> enhancedNpi{p,m}.csv, 1660 rows
./prepare.py data_phifull                     3.2 s   -> simenhanced3he.dat, 500 KB
./prepare.py data_phi4seg24deg_phifullbin     4.8 s   -> simenhanced3he.dat, 495 KB
```

Neither step-3 run printed the `no E*stat_prop` warning, so both sets of trees
carry the branches; all 1660 rows finite in both, 20 columns.

**`AUTPretzelosity` was rewritten against the literature and the first version was
wrong in shape, not just in normalisation.** Checked against Lefky and Prokudin,
*Extraction of the pretzelosity distribution* (JLAB-THY-14), and Gao *et al.*,
*Future (transverse) spin physics at Jefferson Lab* (SPIN2010). The first
implementation had been built by analogy with `FUTCollins` and carried **1/z where
eq. (33) has z^2** — a factor z^3, ~5.7x across the SoLID z range — plus one power
too few of the Gaussian width and none of the M_T/M_C-modified widths. It now
implements eq. (33) directly, with `g1col` added on **NNPDFpol11_100** so
h1Tperp(x) = e N(x) (f1 - g1) is the real parametrisation rather than a stand-in.

**The Collins fit was not touched, and that was verified:** `AUTCollins` returns
-0.193043 before and after, bit-identical. `H1perphalf` unwraps the packaging
`H1col` already applies and re-applies eq. (31), so one fragmentation model still
drives both observables with no duplicated constants.

`PAR['pretzelosity']` in `prepare.py` is now Table III: `Nu` 1, `Nd` -1,
`a` (alpha) 2.2, `b` (beta) 2, `MT2` 0.21, `kt2` 0.25.

| directory | mean A_Sivers | mean A_Collins | mean A_Pretz | median stat S / C / P |
|---|---|---|---|---|
| `data_phifull` | -0.02212 | -0.02607 | +0.00238 | 0.00369 / 0.00354 / 0.00353 |
| `data_phi4seg24deg_phifullbin` | -0.02169 | -0.02518 | +0.00230 | 0.01777 / 0.01652 / 0.01659 |

Both files: 1660 rows, 29 columns, all nine `AUT*` / `error_stat_*` /
`error_tot_*` present, zero non-finite, and `error_tot` reproduces
`sqrt(stat^2 + systabs^2 + AUT^2 systrel^2)` for all three amplitudes.

**This supersedes the pretzelosity numbers in the entry below** (mean -0.0039,
median `error_tot` 0.00411), which came from the schematic first version. Sivers
and Collins are unchanged there.

**Cross-check worth keeping.** The phi-cut cost between the two directories,
per amplitude, is Sivers **3.78**, Collins **4.32**, Pretzelosity **4.32** --
matching Result 3 of `SIDIS_MUT3_comparison/SIDIS_MUT3_comparison_other.md` to
three digits, which was measured from the ROOT trees rather than through the CSV
path.

**A trap for anyone differencing the two files row by row.** Their model
asymmetries are *not* equal despite the shared 1660 bins: the tree stores each
bin's **mean accepted kinematics**, and the azimuthal cut changes which events
survive, so x, y, z, Q2 shift by up to 16-20% and pT by more than 2x in the worst
bin. `AUTPretzelosity` differs by up to 8.4x in the extreme bin as a result.

**Still a placeholder.** `code.md` step 5 now carries the warning and the four
things to settle first: the Collins FF here is M_C^2 = 0.67 / Nfav = 1.0 while
Lefky-Prokudin fitted their normalisation against M_C^2 = 1.50 / Nfav = 0.49; the
Collins sign convention is unresolved (Gao eq. 6 carries a minus that
`FUTCollins` does not implement, while `FUTSivers` does implement eq. 7's); every
Table III parameter has >= 100% error and their null test gives P = 76%; and
nothing has been reproduced against a published curve.

**The fit step is still blocked.** `fitcollins.py` / `fitsivers.py` load
`simenhanced3he_{OBS}.dat` with a single `error` column; prepare.py writes one
unsuffixed file with per-amplitude `error_stat_*` / `error_tot_*`.

---

## 2026-08-31 — `data_phifull`: steps 3 and prepare on the new CSV schema

```
./analysis_neutron 3 data_phifull      3.3 s   -> enhancedNpi{p,m}.csv
./prepare.py data_phifull              1.5 s   -> simenhanced3he.dat
```

**What `data_phifull` is.** A separate top-level directory holding copies of the
`SIDIS_MUT3_comparison/data_phifull_phisunfold_bin1deg` trees — same sizes,
different inodes, so copies rather than links — i.e. the SoLID acceptance at full
2pi, signed `phi_S`, 1 deg histogram. It carries `E*stat_prop` and `E*stat_diag`.
It is **not** the 2026-08-27 01:15 run that was there earlier in the day, which
predated those branches; an attempt against that one wrote 986 rows of `nan` stat
columns and would have had every row dropped downstream.

**Step 3** produced 986 + 674 = **1660 rows** across the two CSVs, in the current
20-column schema (`value_*` and `stat_*` per amplitude). `stat_sivers`,
`stat_collins`, `stat_pretzelosity`, `systabs` and `Nacc` are finite in all 1660,
and the three stat columns are distinct per row.

**prepare.py** now takes only `<rundir>` — no observable argument — and writes a
single `simenhanced3he.dat` covering all three amplitudes: 1660 rows, 29 columns,
nothing dropped by the finite/positive filter.

| amplitude | mean AUT | median `error_stat` | median `error_tot` |
|---|---|---|---|
| Sivers | -0.0221 | 0.00369 | 0.00499 |
| Collins | -0.0261 | 0.00354 | 0.00798 |
| Pretzelosity | -0.0039 | 0.00353 | 0.00411 |

Checked rather than assumed: every `error_tot_*` reproduces
`sqrt(stat^2 + systabs^2 + AUT^2 systrel^2)` to floating point, `error_tot >
error_stat` in all 1660 rows, and no non-finite value anywhere. Collins picks up
the most systematic because `error_tot` scales with the asymmetry through the
relative term and Collins is the largest of the three. The largest
`error_stat_*` is ~1.0, three decades above the median — starved bins that pass
the filter and carry ~zero weight, as intended.

**AUTPretzelosity is new and its normalisation is a placeholder.** `tmd.py` gained
`h1Tperp1`/`FUTPretzelosity`/`AUTPretzelosity` mirroring the Collins family, and
`PAR['pretzelosity']` is the Collins parameter set because pretzelosity has never
been fitted here. The pT^3 shape is right — verified, the ratio to Collins scales
as pT^2 to 16.01 against 16.0 over pT 0.2 to 0.8 — but the overall constant
follows the schematic Gaussian convention of `FUTCollins`, not a derivation. Do
not quote a pretzelosity projection from it without checking that constant.

**The fit step does not follow yet.** `fitcollins.py` and `fitsivers.py` load
`simenhanced3he_{OBS}.dat` and `simenhanced3hesyst_{OBS}.dat`; prepare.py now
writes one unsuffixed `simenhanced3he.dat` instead, and the per-observable error
lives in `error_stat_<obs>` / `error_tot_<obs>` rather than in a single `error`
column. Both scripts need updating to the new schema before any fit runs.

---

## 2026-08-30 — `CreateFile` rename + `E*stat_prop` in the CSV (verification runs)

No production run. `CreateFileSivers` is now `CreateFile` — it was never
Sivers-specific, it writes the CSV both fit paths read — and the CSV carries three
new trailing columns, `E0stat_prop,E1stat_prop,E2stat_prop`, beside the existing
`stat` (which is still `E1stat`, the production row norm). Column order is
unchanged up to `Nacc`, and `prepare.py` selects by name, so nothing downstream
had to move.

New columns are written at `%.8g` rather than the `%.6f` of the older ones: these
errors span 1e-4 to 1e2, and `%.6f` leaves the smallest bins three significant
digits.

**Pre-2026-08-27 directories are handled.** `SetBranchAddress` on a missing branch
leaves the variable untouched, so a run without `E*stat_prop` would have written
uninitialised stack into the CSV. `CreateFile` now checks for the branch, writes
`nan` and says so. Only `data_phifull_phisfold_bin10deg` is old enough to need it —
the 4pi runs of 2026-08-27 10:21 already carry the branches.

```
./analysis_neutron 3 SIDIS_MUT3_comparison/data_phifull_phisfold_bin1deg      # has the branches
./analysis_neutron 3 SIDIS_MUT3_comparison/data_4pi_phisfold_bin10deg         # has them too
./analysis_neutron 3 SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg     # does not: prints the warning, writes nan
./prepare.py collins SIDIS_MUT3_comparison/data_phifull_phisfold_bin1deg      # reads the wider CSV unchanged
```

**Cross-check that the new column is what it claims:** in
`data_phifull_phisfold_bin1deg`, median `stat`/`E1stat_prop` = **1.1339**, against
the 1.137 measured on the same run's tree branches. The CSV path reproduces the
row-norm/Appendix-II ratio.

**Artifacts these left behind** — valid step-3 output, generated with the current
binary from the current trees, not stale: `enhancedNpi{p,m}.csv` in all three
directories above, plus `simenhanced3he{,syst}_collins.dat` in
`data_phifull_phisfold_bin1deg` from the `prepare.py` check.

---

## 2026-08-28 — `data_4seg24deg_phifullbin_phisunfold_bin10deg`: the 10 deg twin of the cut run

18:33:43 → 20:06:44 = **1h33m01s**, exit 0, 16 MB, **three
`non-positive diagonal in inverted MUT3` warnings** — the first this repo has
produced.

```
ln -s ../data_phifull_phisfold_bin10deg/bin_enhanced_*.dat SIDIS_MUT3_comparison/data_4seg24deg_phifullbin_phisunfold_bin10deg/
# NPHI 360 -> 36 in SoLID_SIDIS_3He.h, rebuild
./analysis_neutron 2 SIDIS_MUT3_comparison/data_4seg24deg_phifullbin_phisunfold_bin10deg 4 all 24 on full   1:33:01.51 (214% cpu)
# NPHI restored to 360, rebuilt
```

**Why the run exists.** `SIDIS_MUT3_comparison_other.md` Result 5 measured the
azimuthal histogram bin width at full 2pi and said explicitly that the test would
have to be repeated under a cut before the same conclusion could be quoted there.
This is that repeat: the same configuration as
`data_4seg24deg_phifullbin_phisunfold_bin1deg` with `NPHI = 36` instead of 360.
Timing matches its 1 deg twin (1:33:01 against 1:34:35), confirming again that
the histogram is not what step 2 spends its time on.

**The answer is that bin width matters under a cut, in the tail.**
`Estatraw_prop`(1 deg)/`Estatraw_prop`(10 deg), 4978 amplitudes:

| | full 2pi | 4x24 deg cut |
|---|---|---|
| median | 1.00096 | 1.00287 |
| p95 | 1.0157 | 1.0538 |
| p99 | 1.0296 | 1.1086 |
| max | 1.058 | **37.50** |
| min | 0.9937 | 0.8119 |
| more than 1% off | 13.3% | **26.8%** |

At the median it is still a tenth of a percent either way, but the tail opens by a
factor of 30 and a quarter of amplitudes move by more than 1%. **Result 5's
caveat was right to be there** — "10 deg is adequate" is a full-azimuth statement
and does not transfer to a sector run.

**Two amplitudes went NaN, and the production estimator hid it.** N8p bin 134
(`Nacc` = 49.4 under the cut) has a non-positive diagonal in the inverted `MUT3`
at 10 deg, so `Estatraw_diag` and `Estatraw_prop` are `nan` for i=1,2 — correctly,
the matrix is numerically singular there. `Estatraw` for the same bin is
**5.85e14**: a finite number, written without any warning, that would flow
straight through `prepare.py` into a fit. The same bin at 1 deg produces no
warning at all. Its i=0 amplitude survives in both but differs by **37x** between
the two binnings, and N11p bin 508 (`Nacc` = 16.1) differs by 17-31x.

So the starved bins that Result 2 identified as the only place folding matters are
also the only place bin width matters, and they are where the production
estimator fails silently while the corrected ones fail loudly.

**Written up the same day.** `SIDIS_MUT3_comparison_other.md` Result 5 now covers
both acceptances and drops the untested caveat; its Figure 3 was rebuilt as
`estatraw_prop-binwidth.{png,pdf}` carrying both pairs, replacing the
phifull-only `estatraw_prop-binwidth-phifull.*`.

**Code change it prompted.** `Estatraw` now returns `NAN` when the inverted
`MUT3` has a non-positive diagonal, instead of the finite 5.85e14 above. One
condition (`!(MUT3(i,i) > 0)`) now decides all three estimators, and the warning
moved with it, so `Estatraw`, `Estatraw_diag` and `Estatraw_prop` can no longer
disagree about whether a bin has an answer. `Estat` inherits it through the
`/fn/0.6/0.86` scaling. **This changes production output** for any bin that trips
the guard: such a bin now reaches `prepare.py` as `nan` and is dropped, rather
than entering a fit with an absurd weight. No existing directory in this repo has
such a bin except the one above. Built clean; not yet exercised by a run.

---

## 2026-08-27 — the four 1 deg runs: the phi cut x the phi_S folding

15:29:52 → 19:24:57 = **3h55m05s**, exit 0, **zero** `non-positive diagonal`,
`singular MUT3_prop` or NaN warnings across 6640 bins.

```
# step 1, own bins (superseded four minutes later -- see below)
./analysis_neutron 1 SIDIS_MUT3_comparison/data_phifull_phisunfold_bin1deg                      4:34.67  (352% cpu)

# step 2, all four on the canonical phifull bins, linked in first
for d in data_phifull_phisunfold_bin1deg data_4seg24deg_phifullbin_phisunfold_bin1deg \
         data_phifull_phisfold_bin1deg   data_4seg24deg_phifullbin_phisfold_bin1deg ; do
  ln -sfn ../data_phifull_phisfold_bin10deg/bin_enhanced_*.dat SIDIS_MUT3_comparison/$d/
done
./analysis_neutron 2 SIDIS_MUT3_comparison/data_phifull_phisunfold_bin1deg               0 all 24 on full    23:59.38 (239% cpu)
./analysis_neutron 2 SIDIS_MUT3_comparison/data_4seg24deg_phifullbin_phisunfold_bin1deg  4 all 24 on full  1:33:05.15 (214% cpu)
./analysis_neutron 2 SIDIS_MUT3_comparison/data_phifull_phisfold_bin1deg                 0 all 24 on fold    23:25.05 (239% cpu)
./analysis_neutron 2 SIDIS_MUT3_comparison/data_4seg24deg_phifullbin_phisfold_bin1deg    4 all 24 on fold  1:34:35.04 (213% cpu)
```

**New in this run: a 1 deg azimuthal histogram.** `NPHI` in `SoLID_SIDIS_3He.h`
was raised from 36 to 360 and the binary rebuilt at 15:18. It is a compile-time
constant, **not** a command-line argument, so a directory's `_bin1deg` suffix is
the only record of which binary produced it — nothing in the tree says. Cost
scales as NPHI^2.

**A 2x2, all on the same 1660 bins.** Acceptance (full 2pi / 4x24 deg) x
`phisfold` (`fold` / `full`). Every one of the four reuses
`data_phifull_phisfold_bin10deg`'s step-1 bins by symlink, so all four pair 1:1
with each other and with the baseline.

**The step-1 run above was thrown away.** `run_1deg.sh` generated own bins for
`data_phifull_phisunfold_bin1deg` (782 + 536 + 204 + 138 = 1660, matching the
canonical set) and had started its step 2 at 15:25:34 when `run_4x1deg.sh`
superseded it at 15:29:52 and relinked all four directories to the canonical
bins. No 1 deg directory carries its own bins.

**The cut runs cost 3.9x the wall time of the uncut ones** — 1h33m against 24m —
which is backwards from the event count. Fewer accepted events per bin means
more kinematics trials before the 100k-accepted break, so the cut runs burn the
trial budget that phifull reaches its cap inside.

| run | step 2 wall | CPU | size |
|---|---|---|---|
| `data_phifull_phisunfold_bin1deg` | 23:59.38 | 239% | 2.5 GB |
| `data_4seg24deg_phifullbin_phisunfold_bin1deg` | 1:33:05.15 | 214% | 563 MB |
| `data_phifull_phisfold_bin1deg` | 23:25.05 | 239% | 2.5 GB |
| `data_4seg24deg_phifullbin_phisfold_bin1deg` | 1:34:35.04 | 213% | 565 MB |

**6.0 GB of `_hs.root` for the four**, against 43 MB for the 10 deg baseline —
the NPHI^2 cost, paid on disk. Repo working tree is now 6.7 GB;
`SIDIS_MUT3_comparison/data_*/` is in `.gitignore` and stays out of the remote.

**Results** — measured on `Estatraw_prop`, written up in
`SIDIS_MUT3_comparison/SIDIS_MUT3_comparison_other.md` with two figures
(`estatraw_prop-vs-bin-bin1deg`, `estatraw_prop-foldratio-bin1deg`):

- `prop` vs `diag` still agree, to 6.0e-14 (phifull) and 3.6e-12 (cut).
- **Folding phi_S is a no-op.** 0.04% of amplitudes move by more than 2% at full
  azimuth, 1.95% under the cut; the three worst are all N11p bin 508, which
  keeps **16.1 events** under the cut against 4.6e5 at full acceptance.
- **The 4x24 deg cut costs 4.13x at the median** (Sivers 3.78, Collins 4.32,
  Pretzelosity 4.32; p95 17.0, max 3461) — but it keeps only **7.1% of the
  events, not the nominal 26.7%**, because `phiscope=all` demands the sectors of
  the electron and the hadron alike and 0.267^2 = 0.071. Priced against that,
  the excess beyond counting is **1.05x** at the median, p95 2.25, max 20.5.
  **Do not quote 26.7% as the event cost of this configuration.**
- **The row-norm defect roughly doubles under the cut**, `Estatraw`/`Estatraw_prop`
  1.137 → 1.373 at the median and 6.9x → 41x at the worst bin. The 1.137
  reproduces the 10 deg run's 1.135, so the defect does not care about the
  azimuthal bin width — it is a property of G, not of how G is sampled.

**Steps 3 onward were not run** for any of the four: no CSVs, no prepared data,
no fits. These directories exist to compare error estimators, not to feed a fit.

---

## 2026-08-27 — the two 4pi runs: acceptance switched off

10:21:15 → 12:01:18 = **1h40m**, exit 0, **zero** `non-positive diagonal`,
`singular MUT3_prop` or NaN warnings across 22 274 bins.

```
./analysis_neutron 1 SIDIS_MUT3_comparison/data_4pi_phisfold_bin10deg 0 all 24 off             5:10.66  (357% cpu)
./analysis_neutron 2 SIDIS_MUT3_comparison/data_4pi_phisfold_bin10deg 0 all 24 off           1:25:59.45 (229% cpu)
ln -s ../SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg/bin_enhanced_*.dat SIDIS_MUT3_comparison/data_4pi_phifullbin_phisfold_bin10deg/
./analysis_neutron 2 SIDIS_MUT3_comparison/data_4pi_phifullbin_phisfold_bin10deg 0 all 24 off  8:51.78  (236% cpu)
```

New in this run: `Estat_diag` / `Estat_prop` (the `Estatraw_*` variants carrying
the same `/fn/0.6/0.86` scaling as `Estat`), and the `[acccut]` argument — `off`
makes every `GetAcceptance_*` return 1.0, bypassing theta ranges, momentum
thresholds, azimuthal sectors and the `Acceptance/` maps. The W/W'/R-factor
physics cuts stay: it removes the *apparatus*, not the kinematics. State is
echoed at startup; anything but `on`/`off` exits 1.

**Own bins explode 12.4x at 4pi:** 20 614 (9386 N11p + 6169 N11m + 3060 N8p +
1999 N8m) against 1660 at nominal acceptance. Adaptive binning targets an
integrated rate per bin, and ~10x the rate subdivides that much further.
**`SIDIS_MUT3_comparison/data_4pi_phisfold_bin10deg` therefore pairs with nothing** — only `SIDIS_MUT3_comparison/data_4pi_phifullbin_phisfold_bin10deg`, on the
baseline's 1660 bins, is a like-for-like comparison.

**Item 10 vanishes at 4pi — the headline result.** Production `Estatraw` /
`Estatraw_diag`:

| run | median | p95 | max | within 1% |
|---|---|---|---|---|
| `SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg` (SoLID acceptance) | 1.1348 | 2.2613 | 6.7381 | — |
| `SIDIS_MUT3_comparison/data_4pi_phifullbin_phisfold_bin10deg` (4pi, same bins) | **1.00003** | 1.00209 | 1.00739 | **100.00%** |
| `SIDIS_MUT3_comparison/data_4pi_phisfold_bin10deg` (4pi, own bins) | **1.00003** | 1.00204 | 1.05136 | 99.99% |

So the row-norm/diagonal discrepancy is **entirely an acceptance effect**. With no
detector the two forms agree to 3e-5; under the real acceptance the row norm
overestimates by 13% at the median and up to 6.7x. This is `bug.md` item 10's
analytic claim — equality iff `K = 2I`, the flat full-coverage limit —
demonstrated empirically on MC rather than on paper, and it settles why the defect
survived: **validating against the ideal case has no discriminating power**, the
two agree there to 1e-5.

`Estatraw_prop` vs `Estatraw_diag` agree to 2.4e-15 (`_phifullbin`) and 3.1e-15
(own bins), consistent with the 1.2e-14 at nominal acceptance.

**What the acceptance costs**, paired 1:1 on the baseline's 1660 bins
(`SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg` vs `SIDIS_MUT3_comparison/data_4pi_phifullbin_phisfold_bin10deg`):

| quantity | median | p95 | max |
|---|---|---|---|
| acceptance fraction Nacc(SoLID)/Nacc(4pi) | 0.096 | 0.224 | 0.353 |
| error ratio E0stat(SoLID)/E0stat(4pi) | 4.38 | 21.28 | 311.9 |
| counting-only expectation sqrt(1/f) | 3.23 | 5.99 | — |
| **excess beyond counting** | **1.24** | **4.43** | **35.7** |

The SoLID acceptance keeps ~9.6% of 4pi events at the median, and costs a factor
4.4 on the Sivers error where pure counting predicts 3.2 — a **1.24x median excess
from azimuthal-lever-arm loss alone**, reaching 35.7x in the worst bin. Same
mechanism as the phi-cut study in `phicompare.md`, now measured against a perfect
detector rather than against a wider cut. The dilution `fn` is essentially
unchanged (0.2778 vs 0.2791), so this is geometry, not target composition.

**Disk: `SIDIS_MUT3_comparison/data_4pi_phisfold_bin10deg` is 612 MB**, `SIDIS_MUT3_comparison/data_4pi_phifullbin_phisfold_bin10deg` 50 MB — the `_hs.root` maps
at ~26 KB/bin x 20 614 bins dominate. Repo total is now 776 MB. A `.gitignore`
for `data_*/` is no longer optional before this goes to the JLab remote.

**Not a physical configuration.** `acccut off` is a diagnostic baseline; nothing
from these two directories should be quoted as a SoLID projection.

---

## 2026-08-27 — `data_phifull_phisfold_bin10deg`: two alternative Estat propagations added, steps 1-2

01:15:23 → 01:42:36 = **27m12s**, exit 0, **zero** `non-positive diagonal` or
`singular MUT3_prop` warnings across all 1660 bins.

```
./analysis_neutron 1 SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg      4:39.26  (350% cpu)
./analysis_neutron 2 SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg     22:33.01  (241% cpu)
```

Run as `data_phifull_test` alongside the then-current `SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg`; on
2026-08-27 that older directory was deleted and this one renamed into its place,
so the commands above are written with the final name. Timings matched the
directory it replaced (4:42.53 / 22:34.72) and the four `bin_enhanced_*.dat` were
**byte-identical** to it, so any tree difference is the new estimator code alone.
43 MB.

**The rename discarded stage 3 onward.** This run covers steps 1-2 only, so the
`enhancedNpi{p,m}.csv`, `simenhanced3he*_{collins,sivers}.dat` and the six
`out-*.dat` produced by the 2026-08-26 pipeline run below **no longer exist**.
`SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg` now holds 12 files, not 20. Re-running `analysis_neutron 3` →
`prepare.py` → the fits would restore them, and they would differ from the
2026-08-26 versions only in that they would inherit the new branches; the shared
tree content is identical.

**What was added to `AnalyzeEstatUT3`.** Two propagations carried alongside the
untouched production `Estatraw`, both built from the same `hs` histogram so only
the estimator differs:

- `E{0,1,2}statraw_diag` — `sqrt(2 pi^2 * MUT3(i,i) / Nacc)`, the weighted
  least-squares error (`bug.md` item 10), plus the non-positive-diagonal guard.
- `E{0,1,2}statraw_prop` — Appendix II of PR-10-006 built independently:
  projections `g = (sin(phi), sin(2 phih) cos(phi), cos(2 phih) sin(phi))` with
  `phi = phih - phiS`, the **mixed** matrix `(M_prop)_jk = Int g_j f_k`, and
  `delta_i^2 = Int (dA)^2 (sum_j (M_prop^-1)_ij g_j)^2 = [M^-1 <gg^T> M^-T]_ii`.

**The two agree to 1.2e-14** over all 4980 amplitudes (1660 bins × 3), ~54× double
epsilon — round-off from two genuinely different matrix routes, not a shared code
path (only 413 of 2346 values in N11p are bitwise equal). This confirms
numerically what `bug.md` item 10 argues analytically: the basis transform `T`
between the proposal's `g` and the code's `f` cancels, so the proposal's
construction *is* the diagonal fix.

**Size of the item-10 overestimate** — production `Estatraw` / `Estatraw_diag`:

| amplitude | median | p68 | p95 | max |
|---|---|---|---|---|
| E0 Sivers | 1.149 | 1.354 | 2.378 | 6.738 |
| E1 Collins | 1.128 | 1.374 | 2.182 | 6.369 |
| E2 Pretzelosity | 1.129 | 1.376 | 2.181 | 6.362 |

**98.6%** of amplitudes are overestimated; **55.8%** by more than 10%, **26.9%**
by more than 50%, **10.0%** by more than 2×. The 1.4% that go the other way do so
by at most 0.3%, consistent with round-off about the equality point. So under the
real 2π acceptance the current form is conservative by ~13% at the median and by
factors of several in the tail — the projected errors are too large and every
improvement factor built from them is understated.

**Production is unchanged.** `Estatraw` still feeds `Estat` and everything
downstream; the new branches are additive. Nothing in `Projections_*`, `data*`,
`output*` or `phicompare.md` moves as a result of this run.

**Trap worth recording:** a first pass reported the prop-vs-diag agreement as
exactly 0. That was an artifact of dumping the branches at `%.10g` before
comparing — ten significant digits truncates a 1e-16 difference. Compare at
`%.17g`, or in-process.

---

## 2026-08-26 — step 2 redo + the 4×24° pair (three runs, 2h11m)

19:22:03 → 21:33:06. Exit 0 throughout, **zero NaN warnings**. First runs to carry
the per-bin azimuthal maps (`hs`, `hs_full`), added to `AnalyzeEstatUT3` earlier
the same day.

```
./analysis_neutron 2 SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg
./analysis_neutron 1 data_phi4seg24deg 4
./analysis_neutron 2 data_phi4seg24deg 4
ln -s ../SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg/bin_enhanced_*.dat data_phi4seg24deg_phifullbin/
./analysis_neutron 2 data_phi4seg24deg_phifullbin 4
```

| run | wall | CPU | rows |
|---|---|---|---|
| `SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg` step 2 (redo) | 22:34.72 | 241% | 1660 |
| `data_phi4seg24deg` step 1 | 4:23.59 | 355% | 169 bins |
| `data_phi4seg24deg` step 2 | 11:26.88 | 195% | 169 |
| `data_phi4seg24deg_phifullbin` step 2 | **1:32:37.47** | 214% | 1660 |

Every timing tracks `runlog_old.md` for the same configuration (4m20s / 11m39s
own-bins; the `_phifullbin` step 2 there was 95m49s against 92m37s here), so the
single-`<rundir>` CLI reproduces the historical runs.

**The phifull redo is bit-for-bit reproducible.** All four groups, 1660 entries,
10 branches (`x, y, z, Q2, Pt, Nacc, fn, E0stat, E1stat, E2stat`): max relative
difference against the 17:59 run is **0**. `gRandom` is never explicitly seeded,
so ROOT's default deterministic seed makes step 2 repeatable. Consequence:
**`SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg`'s CSVs, prepared data and all six fits remain valid** — the redo
only added the maps. (**Superseded 2026-08-27:** this directory was deleted and
`data_phifull_test` renamed into its place. The trees are equivalent — identical
bins, identical shared branches — but the CSVs, prepared data and fits described
here are gone and would need regenerating.)

Beware the obvious wrong test here: `md5sum` on a `.root` file *always* differs
between runs, because ROOT stamps a creation time into the file header. Compare
tree contents, not file bytes.

**Own-bins row count reproduces exactly:** 169 = 85 N11p + 56 N11m + 17 N8p +
11 N8m, matching the historical 1660 (2π) → 334 (6×24) → **169 (4×24)** ladder.
`_phifullbin` keeps all 1660 by construction, which is why **only it pairs 1:1
with `SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg`** — `data_phi4seg24deg` re-bins under its own 26.7%
acceptance, so its row counts and χ² are not comparable across runs.

**No empty bins anywhere.** `Nacc <= 0`: 0 rows in all three. Non-finite
`E0stat`: 0. So `prepare.py` will drop nothing. Worth noting how close
`_phifullbin` runs to the edge though — its minimum `Nacc` is **4.03**, against
417.8 for phifull and 1.74e4 for own-bins. Those starved bins survive with
huge-but-finite errors and near-zero fit weight; a slightly tighter cut would
start producing the `-nan` rows seen in the 2×24° FA run.

**Maps cost more than estimated:** 43 MB of `_hs.root` for phifull (~26 KB/bin),
15 MB for `_phifullbin` (sparser histograms compress better at 26.7% acceptance),
2.3 MB for own-bins. **62 MB across the three run directories** — these belong in
a `.gitignore` before the repo goes to the JLab remote.

---

## 2026-08-26 — first full pipeline in this repo: phifull, NREP=10

The whole chain end to end into one directory, full 2π (no `phicut`), 17:59:06 →
18:30:40 = **31m34s** wall. Exit 0 at every stage.

The run was launched as `data_test` and the directory renamed to `SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg`
afterwards, to match the suffix convention in `CLAUDE.md`; the commands below are
written with the final name so they reproduce as read.

```
./analysis_neutron 1 SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg
./analysis_neutron 2 SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg
./analysis_neutron 3 SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg
./prepare.py collins SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg
./prepare.py sivers SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg
NREP=10 ./fit{collins,sivers}.py {world,enhanced3he,enhanced3hesyst} SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg
```

| stage | wall | CPU |
|---|---|---|
| `analysis_neutron 1` | 4:42.53 | 349% |
| `analysis_neutron 2` | **23:06.27** | 239% |
| `analysis_neutron 3` | 0.94 s | 57% |
| `prepare.py collins` / `sivers` | 1.66 s / 1.30 s | — |
| `fitcollins.py world` / `fitsivers.py world` | 1.66 s / 4.51 s | — |
| `fitcollins.py enhanced3he` / `fitsivers.py` | 40.99 s / 1:04.82 | — |
| `fitcollins.py enhanced3hesyst` / `fitsivers.py` | 44.60 s / 1:04.98 | — |

**Row-count chain is exact.** 1660 bins from step 1 (783 N11p + 537 N11m + 205
N8p + 139 N8m) → 1660 CSV rows (986 π⁺ + 674 π⁻) → 1660 prepared rows. Zero rows
dropped: `prepare.py` printed no `Nacc = 0` message, as expected at full 2π —
contrast the 32 dropped rows in the 2×24° FA run (`runlog_old.md`).

**Outputs** — all six were in `SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg/` (**deleted 2026-08-27**, see the
2026-08-27 entries), both observables sharing one directory
with no collision, which is what the single-`<rundir>` refactor was for:

| file | replicas | mean χ² |
|---|---|---|
| `out-world_collins.dat` | 10 | 145.1 |
| `out-world_sivers.dat` | 10 | 227.7 |
| `out-enhanced3he_collins.dat` | 10 | 1635.1 |
| `out-enhanced3he_sivers.dat` | 10 | 1632.0 |
| `out-enhanced3hesyst_collins.dat` | 10 | 1635.3 |
| `out-enhanced3hesyst_sivers.dat` | 10 | 1632.5 |

χ² ≈ N_dof throughout (world: 146/234 rows; enhanced3he: world + 1660 pseudodata
rows), which is what replica fits to model-generated data fluctuated by their own
errors must give. `simenhanced3he_collins.dat` has mean |A_UT| = 0.093 over 1660
rows, so the truth injection ran — the C++ writes `0.0` in that column.

**NREP=10 is a plumbing check, not a result.** At 10 replicas every quoted error
carries 1/sqrt(2(N-1)) = **24%** sampling noise, and a ratio of two of them ~33%.
Nothing here should be quoted. Re-run at the default 200 for numbers.

**Step 2 is 73% of the wall time, and most of that is one core.** Its cost is
~1660 bins × (up to 1e7 kinematics trials, breaking early at 100k accepted) ×
2 cross-section evaluations per accepted event — the 3He weight plus a second
bare-neutron `Lsidis` for the dilution `fn`, both through `dsigma()`/LHAPDF.
Bins that cannot reach 100k accepted events burn the full 1e7, so the expensive
bins are the high-x / high-P_T tail. Compounding it, `RunGroupsInParallel()`
splits by group, not by bin count, and the groups are uneven (783/537/205/139):
three children finished while N11p ran alone at 98.5% of one core for the last
~5 minutes, dropping the average to 239% against step 1's 349%. **Splitting the
fork by bin count would recover most of the gap** — not attempted here.

---

## 2026-08-26 — refactor verification (earlier the same day)

At the time of this entry no pseudodata existed in the repo. These were the
verification runs of the single-`<rundir>` refactor:

| command | result |
|---|---|
| `make O=analysis_neutron` | builds clean (pre-existing warnings only) |
| `./analysis_neutron 0` | runs without a rundir, creates no directory |
| `NREP=4 ./fitcollins.py world testrun` | 1.1 s, `testrun/out-world_collins.dat` |
| `NREP=4 ./fitsivers.py world testrun` | `testrun/out-world_sivers.dat` |

**Regression check.** Both outputs are **byte-identical** to the same fits run
from the upstream `sidis2020_zwzhao` scripts at `NREP=4`, `SEED0=0`
(`out-world.dat`, md5 `b919bac069db01f328e94f5c337d467e` for Collins). The world
inputs are unchanged files: `data_other/colworld_collins.dat` md5
`7a6b6930a69e855f45d1d139f426b900` equals upstream `datacollins/colworld.dat`,
and `colworld_sivers.dat` md5 `3e56d723f9482b37c44e7be1b1f4cd16` equals upstream
`data/colworld.dat`. The refactor is numerically a no-op.

χ² ≈ 145 on a 146-row world set is the expected value, not a red flag:
`_fitworld_one` resamples every replica through `np.random.normal(value, error)`,
so χ² ≈ N_dof. The χ² ≈ 0 property recorded in `bug.md` item 1 belongs to the
*unfluctuated* fit inside `simulate()`.

**Then unexercised:** steps 1-3 and `prepare.py`. Closed by the `SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg` run
above, which exercised the whole chain.

`testrun/` was deleted once `SIDIS_MUT3_comparison/data_phifull_phisfold_bin10deg` superseded it — the md5s recorded above
are the surviving evidence for the byte-identical claim.
