# The physics, and how it maps onto the code

What this pipeline computes, in the order the physics happens, with the file and
formula behind each step. Companion documents: `phicompare.md` (results of the
azimuthal study), `bug.md` (open problems), `code.md` (implementation detail), `check.md`
(settled investigations),
`runlog.md` (provenance). Written 2026-08-19; Step 5's model citations corrected
2026-08-24 after checking the code against the papers (`check.md`).

## Overview

**The question.** SoLID will measure single-spin asymmetries in semi-inclusive
deep-inelastic scattering (SIDIS) off a transversely polarised ³He target — an
effective polarised *neutron*. Two of the asymmetry's azimuthal modulations carry
the physics of interest: the **Collins** term gives access to **transversity**
$h_1(x)$, the **Sivers** term to the **Sivers function** $f_{1T}^\perp$. The
projection's headline deliverable is the **tensor charge**
$g_T = \int (h_1^u - h_1^d)\,dx$, and how much SoLID data shrinks its uncertainty
relative to existing world data.

**How the code answers it.** Nothing here is a measurement, so the pipeline
manufactures pseudodata and then fits it. That splits cleanly in two, and the
split is worth internalising because it is where most confusion starts:

| stage | language | what it decides | what it does *not* decide |
|---|---|---|---|
| generation | C++/ROOT (`analysis_neutron.C`, `SoLID_SIDIS_3He.h`, `Lsidis3.h`) | *where* SoLID can measure and *how precisely*: kinematic bins, accepted counts, statistical and systematic error bars | any asymmetry value — the CSVs it writes have `value` hardcoded to `0.0` |
| extraction | Python (`prepare.py`, `tmdlib/tmd.py`, `fitcollins.py`, `fitsivers.py`, notebooks) | *what* the asymmetry is: the TMD model, the assumed-true parameters, the fit, the bands | anything about the detector or the rates |

The chain: cross section → rates through the acceptance → error bars → model
asymmetry at those kinematics → fit → $h_1$ band → $g_T$.

---

## Step 1 — the cross section that sets the rates

`Lsidis3.h`. A leading-order parton model with Gaussian transverse-momentum
dependence. The only structure function evaluated is the unpolarised one
(`Lsidis3.h:685`):

$$F_{UU,T} = x \sum_q e_q^2\, f_1^q(x,Q^2)\, D_1^{q\to h}(z,Q^2)\,
\frac{e^{-P_T^2/\langle P_T^2\rangle}}{\pi \langle P_T^2\rangle},
\qquad \langle P_T^2\rangle = z^2\langle k_T^2\rangle + \langle p_T^2\rangle$$

and the cross section is (`Lsidis3.h:703`, `mode = 0`)

$$\frac{d\sigma}{dx\,dy\,dz\,dP_T^2\,d\phi_h\,d\phi_S}
= \frac{\alpha_{em}^2\, y}{2xQ^2(1-\varepsilon)}\left(1 + \frac{\gamma^2}{2x}\right) F_{UU,T}.$$

`mode = 0` means **no azimuthal modulations at all** — deliberate. The generator's
job is to predict how many events land in each bin, not what asymmetry they carry.

- PDFs `CJ15lo`, fragmentation functions `DSSFFlo`, both through LHAPDF.
- Isospin is handled by summing proton and neutron terms weighted by `Np`, `Nn`
  (`SetNucleus`); ³He is entered as 2 protons + 1 neutron.
- Gaussian widths: $\langle k_T^2\rangle = 0.604$, $\langle p_T^2\rangle = 0.114$
  GeV² for pions (`SoLID_SIDIS_3He.h:782`; class defaults 0.57 / 0.12).
- Phase-space cuts applied per event: $W > 2.3$, $W' > 1.6$ GeV, and an
  **R-factor** cut (`Lsidis3.h:552`, threshold `Rfactor0` in
  `SoLID_SIDIS_3He.h:38`) — a rapidity-based criterion that the detected hadron
  comes from current fragmentation, which is what makes the TMD factorisation
  above legitimate. Note the threshold is set to $10^5$ in these runs, so as
  configured it removes very little; the machinery is there to tighten it.

## Step 2 — acceptance and accepted yield

`SoLID_SIDIS_3He.h`. Each sampled event is weighted by the product of the
electron and hadron acceptances, read from the `Acceptance/*.root` maps
(`GetAcceptance_e` sums forward- and large-angle; hadrons are forward-angle
only), optionally restricted to azimuthal sectors (the `phicut`/`phiscope`
options plus `phiwidth` — see `phicompare.md`). The accepted yield per bin is

$$N_{acc} = \mathcal{L}\, T\, \epsilon \times \big\langle \mathrm{acc}\cdot d\sigma \big\rangle,$$

with $\mathcal{L} = 10^{10}$ (in GeV units via the $0.197327^2$ conversion),
$T$ = 48 days at 11 GeV or 21 days at 8.8 GeV, $\epsilon = 0.85$.

Bins in $(x, Q^2, z, p_T)$ are built adaptively in step 1 so each holds a
comparable number of events; step 2 fills them; step 3 writes the CSV.

## Step 3 — the statistical error on the asymmetry

This is the least obvious step and the one that matters most for the azimuthal
study. The transverse-spin asymmetry is not one number per bin: three modulations
have to be separated from the same $(\phi_h, \phi_S)$ distribution,

$$A_{UT} \supset A^{\sin(\phi_h-\phi_S)}\ (\text{Sivers}) ,\quad
A^{\sin(\phi_h+\phi_S)}\ (\text{Collins}) ,\quad
A^{\sin(3\phi_h-\phi_S)}\ (\text{pretzelosity}).$$

`AnalyzeEstatUT3()` (`SoLID_SIDIS_3He.h:838-861`) therefore histograms the
accepted events in $(\phi_h, |\phi_S|)$, builds the 3×3 matrix of azimuthal
moments $M_{ij} = 2\pi^2\langle \sin_i \sin_j\rangle$, **inverts it**, and takes

$$\delta A_i = \frac{1}{f_n\, P_{^3He}\, P_n}
\sqrt{\frac{2\pi^2}{N_{acc}} \sum_j (M^{-1})_{ij}^2 \cdot \pi^2 },
\qquad P_{^3He} = 0.6,\ P_n = 0.86 .$$

Three things ride on this form:

- **$f_n$, the neutron dilution.** Computed by running a second `Lsidis` instance
  configured as a bare neutron (`SetNucleus(0,1)`) over the same events, so
  $f_n$ = neutron yield / ³He yield. The proton pair in ³He dilutes the signal.
- **$P_{^3He} = 0.6$, $P_n = 0.86$** — target polarisation and the effective
  neutron polarisation inside ³He.
- **The matrix inverse, not $1/\sqrt{N}$.** Restricting the azimuthal acceptance
  makes the three modulations harder to tell apart, the matrix ill-conditioned,
  and the error grows far faster than counting statistics. Measured: a 2×24°
  sector layout gives errors 12× worse than $1/\sqrt{N}$ predicts, while 6×24°
  and 4×24° stay within 5–32%. See `phicompare.md`.

## Step 4 — systematics

Hardcoded in the CSV writer (`SoLID_SIDIS_3He.h:975-990`), split into a relative
and an absolute piece:

| source | value |
|---|---|
| target polarisation | 3% |
| nuclear effects | 5% |
| radiative corrections | 2.5% |
| diffractive mesons | 3% |
| random coincidence | 0.2% |
| **quadrature total (`systrel`)** | **≈ 7.0%** |
| raw-asymmetry floor (`systabs`) | $1.7\times10^{-4}/(P_{^3He} f_n P_n)$ at 11 GeV; $2.57\times10^{-4}$ at 8.8 GeV |

`prepare.py` combines them into the fit's error:
$\delta = \sqrt{\mathrm{stat}^2 + \mathrm{systabs}^2 + A^2\,\mathrm{systrel}^2}$,
and writes each dataset twice — stat-only and stat+syst.

## Step 5 — the asymmetry model (Python)

The C++ never computes an asymmetry, so `prepare.py` fills the `value` column by
evaluating `tmdlib/tmd.py` at each row's kinematics with a **fixed assumed-true
parameter set** (`par0` Collins, `par1` Sivers). Structure-function decomposition
follows Bacchetta *et al.*, JHEP 02 (2007) 093 (arXiv:hep-ph/0611265).

**The functional forms and every hardcoded constant are Torino (Anselmino
*et al.*), not KPSY15** — Collins and transversity from PRD 87 (2013) 094019
(arXiv:1303.3822), *polynomial* parametrisation and Table 3; Sivers from
arXiv:1107.4446; Gaussian widths from Anselmino *et al.* 2005 (eq. 8 of
arXiv:1303.3822). KPSY15 (Kang, Prokudin, Sun, Yuan, PRD 93 (2016) 014009,
arXiv:1505.05589) is a *different framework* — CSS/TMD evolution in $b$-space
with a collinear twist-3 Collins function $\hat H^{(3)}(z)$ and flavour-dependent
$a_q, b_q$ on $\tfrac12(f_1+g_1)$ — and it contains **no Sivers fit at all**. It
enters here only as the extraction the SoLID projection paper builds on (Ye
*et al.*, PLB 767 (2017) 91, arXiv:1609.02449) and as the source of the published
uncertainties `tol` is calibrated against. Two shape factors in the code appear
in *no* published fit; they are flagged below. Verified equation by equation
against all four papers on 2026-08-24 — evidence in `check.md`.

**Denominator** (`tmd.py:69`) — same Gaussian parton model as the C++, but note
it uses $\langle k_T^2\rangle = 0.25$, $\langle p_T^2\rangle = 0.20$ GeV² — the
values Anselmino *et al.* 2005 fit to unpolarised SIDIS — *not* the generator's
0.604 / 0.114. The two stages therefore do not share one TMD width — they come
from two unrelated frameworks. It affects the assumed-true asymmetry and the
fitted model consistently (both use `tmd.py`), so the closure property survives,
but it is a genuine inconsistency between the rate model and the asymmetry model.

**Collins → transversity** (`tmd.py:148-163`):

$$A_{UT}^{\sin(\phi_h+\phi_S)} = \varepsilon\,\frac{F_{UT}^{Collins}}{F_{UU,T}},
\qquad
\varepsilon = \frac{1-y-\tfrac14\gamma^2y^2}{1-y+\tfrac12y^2+\tfrac14\gamma^2y^2}$$

— the standard depolarisation factor $2(1-y)/[1+(1-y)^2]$ with the $\gamma^2$
mass terms kept. $F_{UT}^{Collins}$ convolutes transversity with the Collins
fragmentation function:

- $h_1^{u,d}(x) = N_{u,d}\,(1 + 0.2\sqrt{x} + c\,x^{1/4})\,x^a(1-x)^b \cdot
  \frac{(a+b)^{a+b}}{a^a b^b}\, f_1^{u,d}(x)$ — the fit's six free parameters are
  $N_u, N_d, a, b, c, \langle k_T^2\rangle$. Antiquark transversity is set to
  zero and $u$ and $d$ share $a,b,c$: a rigid form, and the standard reason a
  bootstrap spread understates the true uncertainty. Two departures from the
  Torino form this otherwise copies: **$(1 + 0.2\sqrt{x} + c\,x^{1/4})$ is in no
  published fit** — local shape freedom, and the flat direction behind the
  Collins bimodality (`check.md`) — and it multiplies $f_1$ alone where both
  Anselmino and KPSY15 use $\tfrac12(f_1 + g_1)$, which is what makes their fits
  automatically Soffer-safe and this one not (`bug.md` item 5).
- $H_1^\perp(z)$ (`tmd.py:128`) is **held completely fixed** at Anselmino
  *et al.* (2013) Table 3: $\mathcal{N}^C_q(z) = N_q\,z\,[(1-a-b)+az+bz^2]$ with
  $a=-2.36$, $b=2.12$, $N_{\rm fav}=+1.00$, $N_{\rm dis}=-1.00$ (both at that
  fit's $|N^C|\le1$ bound) and Collins width $M_h^2 = 0.67$ GeV² — so no
  fragmentation uncertainty propagates into the transversity band. The
  $M_\pi = 0.14$ GeV in `H1col` cancels against `FUTCollins`; the resulting
  prefactor reproduces eq. (14) of arXiv:1303.3822 exactly.

**Sivers** (`tmd.py:79-111`):

$$A_{UT}^{\sin(\phi_h-\phi_S)} = \frac{F_{UT}^{Sivers}}{F_{UU,T}},
\qquad
f_{1T}^{\perp(1)q}(x) = N_q (1+c_q x)\, x^{a_q}(1-x)^{b_q}
\frac{(a_q+b_q)^{a_q+b_q}}{a_q^{a_q} b_q^{b_q}}\, f_1^q(x)$$

with independent $u$ and $d$ shapes and constant antiquark normalisations. The
parameter vector is $(N_u,a_u,b_u,c_u,N_d,a_d,b_d,c_d,N_{\bar u},N_{\bar d},
\langle k_T^2\rangle)$; the SoLID fit floats **9** of the 11 ($N_{\bar u}$,
$N_{\bar d}$ held), the world-only fit floats 7 (also holding $c_u$, $c_d$) —
which is why world-vs-SoLID *parameter* comparisons are meaningless and only
bands and $g_T$ may be compared. No $\varepsilon$: the Sivers asymmetry carries
no depolarisation factor, unlike Collins — Bacchetta's $\sin(\phi_h-\phi_S)$ term
is $\big(F_{UT,T} + \varepsilon F_{UT,L}\big)$, coefficient 1 on the leading-twist
piece. The $x$-shape is the Torino Sivers form (arXiv:1107.4446), including the
constant antiquark normalisations, except that **$(1+c_q x)$ is again a local
addition** with no counterpart in that fit — the same role `c` plays in Collins,
and likewise zero in the injected truth.

Isospin in both: `f1col`/`h1col` swap the $u$ and $d$ slots for a neutron target
and average them for a deuteron.

## Step 6 — the fit

`fitcollins.py` / `fitsivers.py`. One χ² over world data **plus** the SoLID
pseudodata,

$$\chi^2(\text{par}) = \sum_{\rm rows} \frac{\big[A^{\rm model}(x,y,z,Q^2,p_T;\text{par}) - A^{\rm data}\big]^2}{\delta^2},$$

minimised with Minuit (`migrad`, `iminuit<2` API). Uncertainties come from a
**bootstrap**: 50 replicas, each fluctuating every `value` by a Gaussian of width
`error` and refitting; the output `.dat` file is the raw table of 50 parameter
sets, nothing more. Replicas run in parallel worker processes, each seeded from
its replica index, so the ensemble is deterministic and reproducible.

## Step 7 — the observable

Done in the notebooks, not the fit scripts:

- **Band**: for each $x$, evaluate `tmd.h1col` once per replica, then central
  value = mean, error = std × `tol`.
- **Tensor charge** (`tmd.py:165`): $g_T = \int_{x_l}^{x_u} [h_1^u(x) - h_1^d(x)]\,dx$,
  quoted **truncated** to $0.05 < x < 0.6$ — the range SoLID actually covers, so
  the number does not depend on extrapolation. (The full-range integral also
  trips `scipy.quad`'s subdivision limit; that warning is cosmetic — the value is
  converged four orders of magnitude below the quoted error, `check.md`.)
- **`tol`** is an error-inflation factor, 7.04 for Collins and 1.5 for Sivers,
  applied to every replica standard deviation. It is a calibration against
  published uncertainties, not a derived quantity; it cancels exactly in error
  *ratios*. `check.md` has the full investigation: the world half of the Ye et al.
  Table 3 test implies 5.70 against KPSY15's own sqrt(29.7) = 5.45, the SoLID half
  implies 7.00, and every test gives a band (4.1-9.5) rather than a point. Note
  the calibration crosses frameworks — a Torino-normalised model against
  KPSY15-normalised errors — which is a further reason it is only safe in ratios.

---

## Where each piece lives

| physics | file | entry point |
|---|---|---|
| cross section, TMD Gaussians, kinematics sampling | `../../Header/Lsidis3.h` | `FUUT()`, `dsigma()`, `GenerateEventKinematics()` |
| acceptance, yields, binning, error model, systematics | `SoLID_SIDIS_3He.h` | `AnalyzeEstatUT3()`, `GetAcceptance_*` |
| run driver, 4-way parallelism, φ options | `analysis_neutron.C` | `main()` |
| asymmetry model: PDFs, FFs, $h_1$, $f_{1T}^\perp$, $H_1^\perp$, $g_T$ | `tmdlib/tmd.py` | `AUTCollins()`, `AUTSivers()`, `gt()` |
| pseudodata assembly, truth injection, error combination | `prepare.py` | `simulatecollins()`, `simulatesivers()` |
| χ², replicas, minimisation | `fitcollins.py`, `fitsivers.py` | `fitfunc()`, `fitsim()` |
| bands, $g_T$, `tol`, plots | downstream of the fits; not in this repo (`code.md` step 7) | `h1calc()`, `gtcalc()`, `gttruncate()` |

## Two loose ends found while writing this

Neither has been changed; both are decisions someone should make deliberately.

- **The two stages do not share a TMD width.** The generator uses
  $\langle k_T^2\rangle = 0.604$, $\langle p_T^2\rangle = 0.114$ GeV² for pions
  (`SoLID_SIDIS_3He.h:782`, class defaults 0.57 / 0.12), while `tmd.py`'s
  `FUUT`/`FUTSivers` use 0.25 and 0.20 and `FUTCollins` uses
  $p_t^2 = 0.67\cdot0.20/(0.67+0.20) = 0.154$. So the model that predicts the
  *rates* and the model that predicts the *asymmetry* describe different
  transverse-momentum distributions. Closure is unaffected — truth injection and
  fit both come from `tmd.py` — but any statement that couples a rate to an
  asymmetry (a $p_T$-dependence study, for instance) inherits the mismatch.
- **The R-factor cut is configured loose.** `Rfactor0 = 1e5`
  (`SoLID_SIDIS_3He.h:38`) against a quantity whose interesting range is order 1,
  so as set the current-fragmentation criterion removes very little. The
  machinery (`Lsidis3.h:552`) is there to tighten it; whether the projections
  should be made with a meaningful cut is a physics choice, and tightening it
  would reduce every yield in `phicompare.md`.

## What this pipeline is not

Five limits that matter when quoting anything from it:

1. **It is a closure test.** The world data's `value` column *is* the model at the
   reference parameters (world χ² ≈ 4e-27), so χ² is not a goodness-of-fit and the
   fit recovers the parameters it was seeded with. What the machinery measures is
   *uncertainty propagation*, which is what a projection needs — but the central
   curves carry no information. (`bug.md` item 1) Nor is the injected truth
   KPSY15's: at $Q^2 = 2.4$ GeV² `par0` gives truncated $g_T = 0.765$ against
   KPSY15's $0.55 \pm 0.14$ ($\delta u$ 0.466 vs 0.349, $\delta d$ −0.299 vs
   −0.200), so no central value from this pipeline is a tensor-charge prediction.
2. **Neutron only.** Every result so far uses ³He pseudodata; the proton (NH₃)
   generator exists but has not been run through the chain. Large $d$-quark
   improvement factors partly reflect how little neutron data the world set has.
3. **The error bars are model-rigid.** Antiquark transversity fixed to zero, $u$
   and $d$ sharing shape parameters, the Collins FF fully fixed, no Soffer bound
   imposed. Bands are narrower than a less constrained analysis would give, which
   is part of what `tol` is compensating.
4. **Improvement factors carry ~±20% run-to-run noise.** Three fits of the
   *identical* dataset gave 10.0×, 12.4× and 14.0× on truncated $g_T$ — each is a
   ratio of two 50-replica standard deviations, so quote a range, not a digit.
   (measured upstream with `plot-transversity_comparefit.ipynb`)
5. **Statistical errors are not counting errors.** Step 3's matrix inversion means
   azimuthal coverage, not just luminosity, sets the precision — the single most
   consequential thing to understand before comparing detector configurations.
