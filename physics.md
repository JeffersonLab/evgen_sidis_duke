# The physics, and how it maps onto the code

What this pipeline computes, in the order the physics happens, with the file and
formula behind each step. Companion documents: `phicompare/README.md` (results of the
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
| generation | C++/ROOT (`analysis.C`, `SoLID_SIDIS.h`, `Lsidis3.h`) | *where* SoLID can measure and *how precisely*: kinematic bins, accepted counts, statistical and systematic error bars | any asymmetry value — the CSVs it writes have `value` hardcoded to `0.0` |
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
  GeV² for pions (`ChangeTMDpars` at every `Lsidis` set-up in `SoLID_SIDIS.h`;
  class defaults 0.57 / 0.12).
- Phase-space cuts applied per event: $W > 2.3$ and $W' > 1.6$ GeV. An
  **R-factor** cut (`Lsidis3.h:603`, threshold `Rfactor0` in
  `SoLID_SIDIS.h`) is coded alongside them — the *collinearity*
  $R = (P_h\cdot k_f)/(P_h\cdot k_i)$, a rapidity-based criterion that the
  detected hadron comes from current fragmentation, which is what makes the TMD
  factorisation above legitimate:

  > M. Boglione, J. Collins, L. Gamberg, J. O. Gonzalez-Hernandez, T. C. Rogers,
  > N. Sato, *Kinematics of Current Region Fragmentation in Semi-Inclusive
  > Deeply Inelastic Scattering*, Phys. Lett. B **766** (2017) 245–253,
  > [arXiv:1611.10329](https://arxiv.org/abs/1611.10329).

  **It is not actually applied.** `Rfactor0` $=10^5$, while $R$ over
  `data_phifull`'s 1660 bins reaches at most $\approx 85$ (with the
  $k_T^2=M_{iT}^2=M_{fT}^2=0.5$ defaults every call site uses) or
  $\approx 202$ (with `CheckCurrentCut`'s more physical 0.16/0.4/0.4). Nothing
  is ever rejected, so **$W' > 1.6$ is the only current-fragmentation cut
  operating**. See the discussion below before changing it.

**What $P_T$ is measured against — it is not the beam.** Every $P_T$ above, and
the `Pt` branch and `pT` column downstream of it, is the hadron momentum
transverse to the **virtual photon**:

$$P_T = |\vec P_h|\,\sin\alpha, \qquad \alpha = \angle(\vec P_h,\ \vec q)$$

the Trento convention `Lsidis3.h:86` advertises. It is built that way at
`Lsidis3.h:516`, whose transverse components are `Pt*cos/sin(...)` in a frame
rotated to put $\vec q$ on the $z$ axis (`:514-515`).

**That frame is the lab frame.** The target is `TLorentzVector P(0, 0, 0,
0.938272)` at every call site in `SoLID_SIDIS.h` (every function that sets up an
`Lsidis`) — a nucleon at rest, no Fermi motion — so
`Lsidis3.h:487`'s `Pl_2.Boost(-PP.BoostVector())` is the identity and everything
downstream of it differs from the lab by a *rotation only*. Lab frame and target
rest frame are the same frame throughout this pipeline.

**The trap.** $\vec q$ itself sits at a lab angle $\theta_q$ of a few to ~25°, so
transverse-to-$q$ and transverse-to-beam are far apart. On a typical row
(E = 11 GeV, $Q^2$ = 2 GeV², x = 0.15, z = 0.4, $P_T$ = 0.30 GeV) the
beam-transverse momentum $|\vec P_h|\sin\theta_h$ runs **0.028 to 0.624 GeV** as
$\phi_h$ turns, while $P_T$ stays fixed at 0.300. That invariance under $\phi_h$
is why $P_T$ is the right variable — and why a row cannot tell you the hadron's
lab angle, which is the whole subject of `FOM/README.md`'s grid section.

## Step 2 — acceptance and accepted yield

`SoLID_SIDIS.h`. Each sampled event is weighted by the product of the
electron and hadron acceptances, read from the `Acceptance/*.root` maps
(`GetAcceptance_e` sums forward- and large-angle; hadrons are forward-angle
only), optionally restricted to azimuthal sectors (the `phicut`/`phiscope`
options plus `phiwidth` — see `phicompare/README.md`). The accepted yield per bin is

$$N_{acc} = \mathcal{L}\, T\, \epsilon \times \big\langle \mathrm{acc}\cdot d\sigma \big\rangle,$$

with $\mathcal{L} = 10^{10}$ (in GeV units via the $0.197327^2$ conversion),
$T$ = 48 days at 11 GeV or 21 days at 8.8 GeV, $\epsilon = 0.85$ for He3. NH3's
values are in "The NH3 target" below.

Bins in $(x, Q^2, z, p_T)$ are built adaptively in step 1 so each holds a
comparable number of events; step 2 fills them; step 3 writes the CSV.

The He3 maps do not depend on lab φ, so a (θ, p) lookup is exact. The NH3 maps
do, strongly; see "The NH3 acceptance" below.

## Step 3 — the statistical error on the asymmetry

This is the least obvious step and the one that matters most for the azimuthal
study. The transverse-spin asymmetry is not one number per bin: three modulations
have to be separated from the same $(\phi_h, \phi_S)$ distribution,

$$A_{UT} \supset A^{\sin(\phi_h-\phi_S)}\ (\text{Sivers}) ,\quad
A^{\sin(\phi_h+\phi_S)}\ (\text{Collins}) ,\quad
A^{\sin(3\phi_h-\phi_S)}\ (\text{pretzelosity}).$$

`AnalyzeEstatUT3()` (`SoLID_SIDIS.h`) therefore histograms the
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
- **Missing: the 0.85 dilution from the N2 gas.** The SoLID wiki gives the He3
  error as $1/\sqrt{N}/0.85/0.2/0.6/0.86$, where 0.85 is the dilution from "add
  N2 gas about 0.1amg" and 0.2 is the neutron's share, i.e. $f_n$ here (SoLID
  wiki, "Full simulation and file sharing", section *luminosity and radiation
  thickness*,
  `https://solid.jlab.org/wiki/index.php?title=Full_simulation_and_file_sharing#luminosity_and_radiation_thickness`).
  The code divides by $f_n \cdot 0.6 \cdot 0.86$ only, and so does `systabs`. $f_n$
  comes from pure ³He (`SetNucleus(2, 1)`), and no N2 or glass enters the yield,
  so the 0.85 appears nowhere. As coded, every He3 statistical error and `systabs`
  term is therefore 1/0.85 = 1.18× smaller than the wiki's. Ratios between He3
  configurations are unaffected, since the factor is common to all of them; that
  covers the phicompare φ-cut comparisons and twin ratios. Absolute band widths and
  improvement factors against world data are affected.
- **On NH3 the prefactor is $1/(f_p\,P_p)$**, with $P_p = 0.7$ and $f_p$ the
  polarised-proton share; see "The NH3 target".
- **The matrix inverse, not $1/\sqrt{N}$.** Restricting the azimuthal acceptance
  makes the three modulations harder to tell apart, the matrix ill-conditioned,
  and the error grows far faster than counting statistics. Measured: a 2×24°
  sector layout gives errors 12× worse than $1/\sqrt{N}$ predicts, while 6×24°
  and 4×24° stay within 5–32%. See `phicompare/README.md`.

### ³He or neutron? The chain from counts to $\delta A^n$

**Everything inside the square root is a ³He quantity.** `AnalyzeEstatUT3` runs
`sidis.SetNucleus(tgt.Np, tgt.Nn)` with `Np = 2.0, Nn = 1.0` (`TARGET_3HE` in
`SoLID_SIDIS.h`),
so the events, their weights, $N_{acc}$ and the $(\phi_h,\phi_S)$ histogram that
becomes $M$ are all ³He. ($N_{acc}$ is `hvar->Fill(1., weight*acc)`, read back as
`GetBinContent(2)` — ROOT numbers bins from 1, so the `Fill` argument and the
`GetBinContent` index differ by one throughout this histogram.) `Estatraw` is therefore the uncertainty on
the **raw ³He asymmetry amplitude**, before any polarisation or dilution is undone.

The second instance, `sidis_pol.SetNucleus(tgt.polNp, tgt.polNn)` = `(0, 1)` on
3he (`sidis_n` until 2026-09-28), exists for one purpose: it fills
`hvar->Fill(0., weight_pol*acc)`, so that
$f_n$ = `GetBinContent(1)/GetBinContent(2)` = neutron yield / ³He yield. It never
enters the moment matrix.

The prefactor is what converts that ³He error into a neutron error, in two steps:

$$\underbrace{\texttt{Estatraw}}_{\delta A_{raw},\ \text{³He counts}}
\;\xrightarrow{\ \div\,P_{^3He}\ }\;
\delta A_{UT}^{^3\!He}
\;\xrightarrow{\ \div\,(f_n P_n)\ }\;
\underbrace{\texttt{Estat}}_{\delta A_{UT}^{n}}
\qquad
\texttt{Estat} = \frac{\texttt{Estatraw}}{f_n\,P_{^3He}\,P_n}$$

On `data_phifull` the two factors are $P_{^3He} = 0.6$ and
$f_n P_n = 0.278 \times 0.86 = 0.239$, so the whole prefactor is $\approx 7$.
That is nearly all of the gap between $\delta A^n$ and the raw counting floor
$\sqrt{2/N_{acc}}$ — see `phicompare/errors_plot/README.md`, where
$\sqrt{2/N_{acc}}/(f_n P_{^3He} P_n)$ is drawn and $\delta_{stat}$ sits a median
1.04–1.21× above it, with the best bins on the floor to within half a percent
(122 bins of ~4500 dip below it by at most 0.45%).

### The proton term is dropped from the central value

The general relation between the two asymmetries is a polarisation- and
cross-section-weighted sum over the nucleons,

$$A_{UT}^{^3\!He} = P_n f_n A_{UT}^{n} + P_p f_p A_{UT}^{p},
\qquad P_n \simeq 0.86,\ P_p \simeq -0.028,\ f_n + f_p = 1,$$

$P_p$ being small and negative because the two protons sit mostly in a spin
singlet. Inverting,

$$A_{UT}^{n} = \frac{A_{UT}^{^3\!He} - P_p f_p A_{UT}^{p}}{P_n f_n},$$

$$\left(\delta A^{n}\right)^2 =
\frac{\left(\delta A^{^3\!He}\right)^2 + \left(P_p f_p\,\delta A^{p}\right)^2}
     {\left(P_n f_n\right)^2}
\;+\; \left(A^{n}\right)^2
\left[\left(\frac{\delta P_n}{P_n}\right)^2 + \left(\frac{\delta f_n}{f_n}\right)^2\right].$$

The statistical part is a pure $1/(P_n f_n)$ amplification; the normalisation
uncertainties on $P_n$ and $f_n$ enter multiplied by $A^n$ itself, so they are
relative rather than absolute — which is why they live in `systrel` (3% target
polarisation + 5% nuclear effect) and not in `Estat`.

**This pipeline sets $P_p = 0$.** `Estat` implements the first term with
$\delta A^p = 0$, and `tmd.py` has no ³He branch at all — only `proton`, `neutron`
and `deuteron`, so `AUTCollins(..., 'neutron', ...)` is a *free* neutron asymmetry
and `prepare.py` writes it as `value` directly.

Size of what is dropped, with $P_n f_n = +0.239$ against $P_p f_p = -0.020$ and
$|A^p/A^n| \approx 1$ in the models used here:

| amplitude | proton term / neutron term, median | 90th pct |
|---|---|---|
| Collins | 7.9% | 12.3% |
| Sivers | 11.1% | 38.0% |

**It biases nothing in this repo.** The pseudodata and the fit function use the
identical convention — and `simulate()` overwrites `value` from the model at the
world-data best fit before any replica runs — so the omission cancels exactly.

It matters the moment the convention is crossed: comparing against real ³He data,
or quoting a projected $A^n$ as something measurable. There the proton term is a
**coherent shift of known sign**, not a variance, so folding it into a symmetric
5% nuclear systematic understates it. The correction is available — `tmd.py` can
already produce $A^p$ via `AUTCollins(..., 'proton', ...)` — and would be a
subtraction of $P_p f_p A^p$, leaving only $\delta A^p$'s contribution in the
error.

## What φ_S is in this generator — the maps carry no spin physics

`Lsidis3.h:88` declares φ_S as "azimuthal angle of transverse polarization in
Trento convention", i.e. the azimuth of the target spin's transverse component
S⊥ about **q**, from the lepton plane. **But no spin direction is ever assigned.**
`Slepton`, `SNL` and `SNT` are set to 0 in the constructor
(`Lsidis3.h:174-176`) and never written again, and `dsigma()` implements only
`mode == 0`, "No azimuthal modulations", returning `FUUT()` alone. The event
weight does not depend on φ_S at all — the same fact behind the C++ writing
`"AUT", 0.0`.

φ_S is instead sampled uniformly on (−π, π] and used *geometrically*:
`CalculateFinalStateKinematics` derives the lepton-plane azimuth from it and
rotates the event into the lab.

**The implied spin direction is lab +x̂**, transverse to the beam and fixed.
Both headers set the beam along lab +ẑ with the target at rest, so
`Pl_2.Theta() = Pl_2.Phi() = 0` and the frame-setting rotations at
`Lsidis3.h:490-491` are the identity — the code's internal frame *is* the lab.
Line 494 places the scattered lepton at azimuth 0 and rotates the lepton system
by `phil(φ_S)` about ẑ.

Verified by closure against the Trento definition itself: computing φ_S from the
generated final-state vectors about **q̂**, measured from the lepton plane
(Bacchetta *et al.*, hep-ph/0410050 eq. 5), with **S = lab +x̂** returns the input
φ_S exactly — at every θ_q tested (0.107–0.377) and every φ_S including ±π/3 and
±2π/3. S = +ŷ does not. φ_h reconstructs identically in the same test, which
validates the reconstruction rather than just the answer.

**φ_S is not simply minus the electron's lab azimuth.** It is defined about **q**,
not about the beam, and the `cos θ_q` factor in lines 496-497 is exactly that
frame conversion:

    tan φ_lab(e⁻) = −cos(θ_q) · tan φ_S

This reduces to φ_S = −φ_lab only as θ_q → 0. At θ_q = 0.377 (x = 0.55, y = 0.35)
and φ_S = π/4 the two differ by 0.036 rad = 2.1°. Beware testing this at
φ_S = 0, ±π/2, ±π only — the sign-flip form is exact there for *any* θ_q, so those
points agree trivially and hide the discrepancy.

That is what forces the mechanism in §3 rather than merely correlating with it,
and it **predicts the stripe positions exactly**. The φ cut tests *lab* azimuth
(`InPhiSector` → `p.Phi()`), keeping electron lab φ near 0, ±90°, 180° at
`phicut=4`. At precisely those values tan φ_S is 0 or ∞, so the mapping is exact
regardless of θ_q and the stripes sit at φ_S = 0, ∓90°, 180° — where they are
observed. Only the stripe *widths* are distorted: differentiating the relation, a
sector near φ_lab = 0 or 180° maps to a φ_S stripe wider by 1/cos θ_q (7.6% at
the largest θ_q here), one near ±90° to a stripe narrower by cos θ_q.

Two consequences: **these maps are pure acceptance**, so read no asymmetry into
them, and MUT3 is a pure geometry object — which is exactly right for a
statistical-error projection. And **there is no spin sign convention in play
yet**: with no polarized structure function there is nothing to get right. If one
is ever added, the Trento declaration above becomes load-bearing and would need
checking against `tmd.py`, where the asymmetry currently lives.

*(Moved here on 2026-08-31 from the azimuthal-acceptance study, now
`phicompare/README.md`: it describes what the generator
computes, not a conclusion about azimuthal cuts. The closure test against the
Trento definition is kept with it rather than split into `check.md`, because the
claim and its evidence are one argument.)*

The lab +x̂ direction is only the default. `[spinangle]` places the spin elsewhere, or splits the
beam time between several settings, by shifting the φ sectors rather than the
spin; how that works and when it is exact is in `code.md`.

## The NH3 acceptance — a lab-fixed field, and which way it points

*Written 2026-09-28 for the NH3 (proton) target, which is being added
(`plan_nh3.md`, working tree only). Nothing below is used by any He3 result.*

**The He3 maps are flat in lab φ; the NH3 maps are not.** Mean forward-angle
acceptance of the `acceptance_ThetaPhiP_forwardangle` TH3F over θ 8–18°, in
twelve 30° bins of lab φ from −180°. The mean is over the map's (θ, p) cells,
unweighted.

| map | p (GeV) | φ profile | min/max |
|---|---|---|---|
| He3 π⁺ (`201701`) | 1–3 | 0.41 0.41 0.41 0.41 0.41 0.41 0.41 0.42 0.41 0.42 0.41 0.42 | 0.98 |
| He3 e⁻ (`201701`) | 2–5 | 0.45 0.45 0.44 0.44 0.45 0.45 0.45 0.45 0.44 0.44 0.45 0.44 | 0.98 |
| NH3 π⁺ (`202012`) | 1–3 | 0.52 0.60 0.31 **0.00** 0.02 0.34 0.25 0.11 **0.00** 0.04 0.11 0.25 | 0.00 |
| NH3 π⁻ (`202012`) | 1–3 | 0.25 0.11 0.04 **0.00** 0.01 0.19 0.52 0.37 **0.02** 0.32 0.60 0.53 | 0.00 |
| NH3 e⁻ (`202012`) | 2–5 | 0.43 0.29 0.14 **0.00** 0.06 0.35 0.58 0.36 **0.01** 0.52 0.60 0.59 | 0.00 |

Reading the table:

- **He3's 2D (θ, p) lookup is exact.** Its maps do not depend on φ, which is also
  what makes the `[spinangle]` sector-shift shortcut valid (`code.md`).
- **Every NH3 map is blind in two wedges, near φ ≈ −75° and +75°.** These are the
  shadows of the polarised target's magnet coils.
- **The two pion charges are mirror images of each other.** The transverse
  holding field bends π⁺ and π⁻ opposite ways.

So for NH3 the 2D maps are wrong, not merely coarse: they average the wedges
away, and where the wedges sit relative to the spin shapes every bin's φ_S
coverage even at full azimuth. NH3 needs the 3D (θ, φ, p) lookup. It also breaks
the `[spinangle]` shortcut outright: rotating the spin means rotating the magnet,
and the wedges turn with it.

**The map frame.** The `202012` NH3 maps were produced with the target field and
spin along +x̂ and the SoLID solenoid field along +ẑ (Z. Zhao, 2026-09-25). The generator's spin is also +x̂ (previous section). So the map is
read at the generator's own `p.Phi()`, with no offset. Upstream NH3 used the
`201710` maps, which are not in this repo; any difference from upstream NH3
numbers is partly that change of maps.

**Checked end to end (2026-09-28).** For four NH3 11 GeV π⁺ bins (Q² 1–4,
z 0.3–0.45, P_T 0–0.4), the pipeline's `hs_full` was compared with an independent
calculation that shares no code with `Lsidis`. That calculation throws e and π
in the bin's (x, Q², z, P_T) box with the spin fixed at lab +x̂. It takes φ_h and
φ_S from the Trento vector definitions (hep-ph/0410050, eqs. 4–5) and reads the
maps at each track's lab (θ, φ, p). The two (φ_h, φ_S) maps agree with a
correlation of 0.97–0.99. Adding an offset δ to the map φ, the agreement peaks
sharply at δ = 0: it is 0.25–0.31 at ±30° and 0.04–0.64 at 180°. So the
generator's spin, the map's frame and the lookup agree.

**The 3D lookup reads empty map cells as zero acceptance.** A map cell with no
generated event is stored as 0. At the maps' 0.5° × 2° × 0.1 GeV this lowers
the NH3 forward-angle acceptance by about 20% per arm, as upstream NH3 did too.
It is kept by decision; `bug.md` item 14 has the evidence and the size. Run on
He3 with the 3D lookup forced on, the same effect gives `Nacc` × 0.95 and Estat
× 1.025 against the 2D lookup, with `fn` unchanged to 10⁻³. That is the
map-level prediction (0.972 × 0.974 per arm) and nothing else, which also
validates the 3D code path.

**The NH3 total rate matches upstream NH3 (2026-09-28).** Upstream's
`SoLID_SIDIS_NH3.h` (`../LiuSIDIS/SoLID/sidis2020`) was run on the same `202012`
maps, with `GetTotalRate`'s Q² and P_T maxima set to He3's 10 and 1.8. It needed
three toolchain fixes, none in the code path of the rate: `std::ifstream`,
`std::isnan`, and the 4-argument `TH2::Integral`. Its `Lsidis3.h` is ours up to
comments. `./analysis nh3 0` was run six times and upstream five, each at 1e8
events. The only intended difference is the unrounded pol lumi 0.84441, which
predicts ours higher by 0.04%:

| channel | ours (Hz) | upstream (Hz) | ours / upstream − 1 |
|---|---|---|---|
| 11 GeV π⁺ | 286.75 ± 0.06% | 287.14 ± 0.11% | −0.14% ± 0.12% |
| 8.8 GeV π⁺ | 202.21 ± 0.17% | 201.76 ± 0.28% | +0.22% ± 0.32% |
| 11 GeV π⁻ | 199.73 ± 0.11% | 199.00 ± 0.23% | +0.37% ± 0.25% |
| 8.8 GeV π⁻ | 132.29 ± 0.15% | 131.50 ± 0.31% | +0.60% ± 0.34% |

Errors are the standard error of the mean over runs; a single 1e8-event run
scatters by 0.15–0.6%. The weighted mean difference is **+0.04% ± 0.10%**, with
χ² = 6.7 for 4 dof against the predicted +0.04%. PDF deferral changes only the
random sequence, and the map vintage is common to both sides, so nothing else is
left to explain. These rates carry the 3D maps' empty-cell bias on both sides
(`bug.md` item 14); they are not a statement of the true NH3 rate.

**The maps confirm the field's axis by themselves.** B is an axial vector, and
reversing it is equivalent to flipping every charge. A mirror in a plane that
contains the field axis and the beam reverses both fields, so combined with
charge conjugation it is a symmetry of the apparatus, if the geometry is mirror
symmetric. That gives a testable prediction for each candidate axis:

- field in the x–z plane (mirror y → −y): π⁺(θ, φ, p) = π⁻(θ, −φ, p)
- field in the y–z plane (mirror x → −x): π⁺(θ, φ, p) = π⁻(θ, 180° − φ, p)

The test statistic is Σ|π⁺ − π⁻(T)| / mean over θ 8–18°, p 1–7 GeV and every φ
cell. It comes out **0.65** for φ → −φ, against 1.30 for φ → 180° − φ, and 1.04
and 1.10 for the two non-mirror controls (φ → φ + 180° and the identity). So the
field lies along the maps' φ = 0/180° axis, as stated. The sign along that axis
is not tested, and does not need to be (below).

The mirror holds bin by bin except in one place. At θ 12–14°, p 2–3 GeV, in 20°
bins of φ from −180°:

```
π⁺(φ)   0.79 0.81 0.80 0.65 0.23 0.00 0.00 0.13 0.83 0.47 0.04 0.00 0.00 0.00 0.00 0.00 0.04 0.48
π⁻(−φ)  0.80 0.82 0.83 0.62 0.23 0.03 0.04 0.78 0.80 0.46 0.04 0.00 0.00 0.00 0.00 0.00 0.04 0.48
```

At φ ≈ −40° to −20°, π⁺ sees 0.13 where the mirrored π⁻ sees 0.78. Something in
the GEMC geometry there is not mirror symmetric (a port, support or coil cut-out,
not yet identified). It is one bin in 18 at this θ and p.

**Field and spin reversal leave the projected errors unchanged.** Three reversals
are worth distinguishing:

- **(a) Target field and spin to −x̂, solenoid still +ẑ.** This is the original
  setup rotated by 180° about the beam, a proper rotation: B_target → −x̂,
  B_solenoid stays +ẑ, spin → −x̂. Each event maps to the same event rotated, with
  φ_h and φ_S unchanged, because both are measured from the spin and the lepton
  plane. The coverage and the errors are identical; only the lab-φ wedges move by
  180°. It assumes the geometry is symmetric under that rotation.
- **(b) Target field and spin to −x̂, solenoid to −ẑ.** This is the original
  reflected in the x–z plane (y → −y). A reflection flips the in-plane components
  of an axial vector, so B_x → −B_x, B_z → −B_z and the spin +x̂ → −x̂, while
  charges are unchanged. Each event maps to its mirror image,
  (φ_h, φ_S) → (−φ_h, −φ_S). The coverage is mirrored, but sin(φ_h−φ_S),
  sin(φ_h+φ_S) and sin(3φ_h−φ_S) are all odd under that flip, so every product
  sin_i·sin_j is even: the moment matrix M, and all three errors, are unchanged.
  It assumes a y-mirror-symmetric geometry, which the maps confirm except near
  φ ≈ −30°.
- **(c) The experiment's own spin flip.** The polarised NH3 target reverses its
  spin by changing the DNP microwave frequency, with the field left at +x̂. The
  lab acceptance is untouched and φ_S → φ_S + 180° for every event. That flips
  the sign of all three sines and again leaves M and the errors unchanged.

So one spin-+x̂ configuration gives the right errors for a two-spin-state
measurement, and the unknown sign in the axis test does not matter. A field
reversal, (a) or (b), is a systematics check, not a change to the projected
precision, apart from the one non-mirror region near φ ≈ −30°.

## The NH3 target — numbers, and where each comes from

*Written 2026-09-28 with the first NH3 run (`phicompare/data_phifull`, `P`
files; `runlog.md`). The code, with the full derivation in comments, is
`TARGET_NH3` in `SoLID_SIDIS.h`.*

**Normalisation: the same convention as He3.** `lumi` is the polarised
luminosity, and `Np`/`Nn` count every proton and neutron in the target per
polarised nucleus. Only lumi·Np and lumi·Nn are physical. The source is the SoLID
wiki, "Full simulation and file sharing", section *luminosity and radiation
thickness*: 100 nA on 2.826 cm of NH3 at 0.819 g/cm³, packing fraction 0.55, in
liquid He4. The wiki gives nucleon luminosities only; the proton/neutron split
below is stoichiometry (NH3 = 10 p + 7 n, He4 = 2 p + 2 n). In units of 1e35 cm⁻² s⁻¹:

| component | nucleons | protons | neutrons |
|---|---|---|---|
| NH3 | 4.785 | 2.815 | 1.970 |
| LHe4 in the cell | 0.69 | 0.345 | 0.345 |
| LHe4, the two outer layers | 0.47 | 0.235 | 0.235 |
| total | 5.945 | 3.395 | 2.550 |

The polarised protons are the 3 H of each NH3, so the polarised luminosity is
4.785/17·3 = **0.84441e35** (the wiki rounds it to 0.844). Per polarised proton
that gives Np = 10/3 + 1.16/2/0.84441 = 4.020 and Nn = 7/3 + 1.16/2/0.84441 =
3.020. The code carries them as those expressions. Two numbers on the wiki are
deliberately not used:
- The Al windows, about 1e35 more nucleons, are left out, as in the wiki's 5.945
  total.
- The wiki's Z/A = 0.583 is the eDIS generator's single-nucleus input, and it is
  mis-averaged. Np/(Np+Nn) = 0.571 here is the true proton fraction.

Against upstream NH3 (lumi 1e35, polarised count 0.844), lumi·Np is 0.04%
higher. The measured rate difference, +0.04% ± 0.10% (above), is consistent
with that.

**Polarised nucleon and dilution.** `sidis_pol` is `SetNucleus(1, 0)`: one
polarised proton per unit of lumi. Only the H protons are polarised; the 7/3
protons in ¹⁴N and those in He4 are not, and any ¹⁴N polarisation is neglected.
The dilution f_p = polarised-proton yield / whole-target yield is computed per
bin from cross sections, exactly as f_n is for He3. In the first run its median
is 0.172 (11 GeV π⁺), 0.145 (π⁻), 0.169 / 0.143 (8.8 GeV), against the wiki's
0.142 without windows and 0.121 with. The π⁺ values are higher because
u-quark dominance favours the proton for π⁺. The g2p *measured* dilution, 0.13,
which the wiki also quotes, is not used.

**Polarisation: P_p = 0.7**, in beam (`pol1`; `pol2` = 1). The wiki gave 80% until
2026-09-25, when it was updated to "70% in-beam polarization". So
Estat = Estatraw / (f_p · 0.7) and systabs = c / (0.7 f_p).

**Taken from upstream NH3, source not yet recorded.** These come from
`../LiuSIDIS/SoLID/sidis2020/SoLID_SIDIS_NH3.h` as written there. Their original
source (proposal or CDR table) must be found and cited here before any NH3
projection is quoted:
- beam time 55 d at 11 GeV and 27.5 d at 8.8 GeV
- `systabs` 7.78e-4 / 1.1e-3
- the binning targets `statlist` = {1.0e7, 6.4e6, 3.2e6, 1.6e6, 1.2e6, 1.0e6} and
  the last-P_T-bin factor 0.2

**Kinematic ranges are He3's**, including `GetTotalRate`'s Q² ≤ 10 and
P_T ≤ 1.8 (upstream NH3 used 8 and 1.6).

**The acceptance** is the 3D lookup of the previous section, full azimuth only,
with the empty-cell bias of `bug.md` item 14.

**Downstream, NH3 enters only in combination with He3.** `prepare.py --combined`
writes `simenhanced.dat`, with the He3 and NH3 rows each evaluated for their own
nucleon (neutron / proton asymmetries from the same `PAR`). The `enhanced` /
`enhancedsyst` fit opts fit it with the world data. There is no NH3-only
prepared set or fit opt, by choice.

## Step 4 — systematics

Hardcoded in the CSV writer (`CreateFile` in `SoLID_SIDIS.h`; the two `systabs`
constants are `TARGET_3HE` fields), split into a relative
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

On NH3 the same five relative terms apply, with the 5% one read as dilution
rather than nuclear effects. `systabs` is $7.78\times10^{-4}/(0.7\,f_p)$ at 11 GeV
and $1.1\times10^{-3}/(0.7\,f_p)$ at 8.8 GeV, both upstream NH3's.

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

### Neither distribution has a $Q^2$ evolution of its own

Both are built as **[a parameter block in $x$ alone] × $f_1(x,Q^2)$**:

```python
def h1col(x, Q2, target, par):
    pdf = f1col(x, Q2)
    A = par['Nu'] * (1 + 0.2\sqrt{x} + c x^{1/4}) x^a (1-x)^b * norm * pdf[2]
```

$Q^2$ appears **nowhere except inside `f1col`**. Three consequences, each verified
rather than argued:

1. **Every error ratio is exactly $Q^2$-independent.** The same factor
   $f_1(x,Q^2)$ multiplies every replica, so it scales the replica spread and
   cancels identically in a ratio. Measured: world/`phifull` for $xh_1^u$ at
   $x=0.25$ is **8.3633643878 at $Q^2 = 2.4$, 5.0 and 7.5 alike** — identical to
   ten decimals. The lower panel of every band figure draws all three and they
   coincide exactly.
2. **The curves themselves do move, and by more than the SoLID band.** Over
   $Q^2 = 2.4 \to 7.5$, $xh_1^u$ shifts $+2.9\%$ at $x=0.1$ and $-27\%$ at
   $x=0.6$ — which is 1.0× to **4.4×** the SoLID 2π band half-width. It looks
   small on the figures only because the axis spans $\pm0.45$ while the shifts are
   $\sim 0.03$, and the world band ($\sim 0.1$) dominates the eye. **Any $g_T$ or
   band value must be quoted with its $Q^2$**; the notebooks use 2.4.
3. **The fit has no $Q^2$-sensitive parameter**, so finer $Q^2$ binning cannot
   help it. That is the underlying reason the 4× $Q^2$ re-binning of the SBS
   projection changed nothing (`runlog.md`, 2026-09-11).

**This is a modelling choice, not a prediction.** Real transversity evolves as a
flavour **non-singlet** — no gluon mixing — while $f_1$ is a singlet that mixes
with the gluon, so the two do not share an evolution. The underlying PDF evolution
here is not weak either: at fixed $x$, $u(x,Q^2)$ runs **+16% at $x=0.05$ to −40%
at $x=0.6$** over $Q^2 = 1.5 \to 10$, crossing zero near $x \approx 0.15$ where sea
growth and valence depletion cancel. Tying $h_1$ to that is an approximation the
fits never test, because no data in them constrains it.

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
| target configuration, acceptance, yields, binning, error model, systematics | `SoLID_SIDIS.h` | `Target`, `LoadTarget()`, `AnalyzeEstatUT3()`, `GetAcceptance_*` |
| run driver, target choice, 4-way parallelism, φ options | `analysis.C` | `main()` |
| asymmetry model: PDFs, FFs, $h_1$, $f_{1T}^\perp$, $H_1^\perp$, $g_T$ | `tmdlib/tmd.py` | `AUTCollins()`, `AUTSivers()`, `gt()` |
| pseudodata assembly, truth injection, error combination | `prepare.py` | `simulatecollins()`, `simulatesivers()` |
| χ², replicas, minimisation | `fitcollins.py`, `fitsivers.py` | `fitfunc()`, `fitsim()` |
| bands, $g_T$, `tol`, plots | downstream of the fits; not in this repo (`code.md` step 7) | `h1calc()`, `gtcalc()`, `gttruncate()` |

## Two loose ends found while writing this

Neither has been changed; both are decisions someone should make deliberately.

- **The two stages do not share a TMD width.** The generator uses
  $\langle k_T^2\rangle = 0.604$, $\langle p_T^2\rangle = 0.114$ GeV² for pions
  (`ChangeTMDpars` in `SoLID_SIDIS.h`, class defaults 0.57 / 0.12), while `tmd.py`'s
  `FUUT`/`FUTSivers` use 0.25 and 0.20 and `FUTCollins` uses
  $p_t^2 = 0.67\cdot0.20/(0.67+0.20) = 0.154$. So the model that predicts the
  *rates* and the model that predicts the *asymmetry* describe different
  transverse-momentum distributions. Closure is unaffected — truth injection and
  fit both come from `tmd.py` — but any statement that couples a rate to an
  asymmetry (a $p_T$-dependence study, for instance) inherits the mismatch.
- **The R-factor cut is switched off, not merely loose.** `Rfactor0 = 1e5`
  (`SoLID_SIDIS.h`) against a quantity whose interesting range is order 1
  and which never exceeds ~200 anywhere in the dataset, so the
  current-fragmentation criterion rejects **nothing**. The machinery
  (`Lsidis3.h:603`) is there to tighten it, but the gap is deliberate rather
  than a mis-set threshold — the literature values are five to six orders of
  magnitude away:

  | source | criterion | fraction of `data_phifull`'s 1660 bins it would cut |
  |---|---|---|
  | Boglione *et al.* 2017 ([arXiv:1611.10329](https://arxiv.org/abs/1611.10329)) | $R \lesssim 0.2$ | 56% (defaults) / 73% (0.16, 0.4, 0.4) |
  | Boglione *et al.* 2022 ([arXiv:2201.12197](https://arxiv.org/abs/2201.12197)) | $R_0, R_1, R_2 < 0.3$ | 44% / 59% on $R_1$ alone |
  | this repo | $R < 10^5$ | 0% |

  So applying either published criterion would remove **44% to 73%** of the
  bins, not trim a tail — and would reduce every yield in
  `phicompare/README.md` and every FOM in `FOM/README.md` accordingly. Whether
  the projections should carry a meaningful cut is a physics choice, and a
  consequential one.

- **The 2022 successor supersedes the hard cut, not the formula.** The
  collinearity is unchanged — it is $R_1$, Eq. 2.2 of

  > M. Boglione, M. Diefenthaler, S. Dolan, L. Gamberg, W. Melnitchouk,
  > D. Pitonyak, A. Prokudin, N. Sato, Z. Scalyer, *New tool for kinematic
  > regime estimation in semi-inclusive deep-inelastic scattering*,
  > JHEP **04** (2022) 084, [arXiv:2201.12197](https://arxiv.org/abs/2201.12197).

  What changed is that a single ratio cut is no longer regarded as adequate.
  $R_1$ now sits in a set — $R_0$ hardness, $R_1$ collinearity, $R_1'$ target
  proximity, $R_2$ transverse hardness — and the recommended practice is to
  compute a Monte-Carlo **affinity**, the fraction of a bin's cross section
  coming from the TMD region, rather than to accept or reject the bin. The tool
  is open, so SoLID's bins could be scored rather than guessed at:
  [github.com/QCDHUB/SIDIS-Affinity](https://github.com/QCDHUB/SIDIS-Affinity)
  ([Colab](https://colab.research.google.com/github/QCDHUB/SIDIS-Affinity/blob/main/interactive_affinity_tool.ipynb)).
  That paper also gives a cut-based shortcut, its Eq. 4.1 —
  $Q^2 > 1.4$ GeV², $0.2 < z < 0.74$,
  $P_{hT} < \min(0.2\,Q,\ 0.7\,zQ + 0.5\ \mathrm{GeV})$ — and reports
  $q_T/Q \lesssim 0.4$ as the region with $\geq 68\%$ TMD affinity. **Caveat:**
  those numbers are tuned on EIC kinematics; at SoLID's $Q^2 \approx 1$–8 GeV²
  the 2017 paper already warns the region boundaries "start to fade", so they
  are guidance, not a prescription to apply as written.

- **$q_T/Q = P_T/(zQ)$, and that is the definition the literature uses.**
  Checked against

  > J. O. Gonzalez-Hernandez, T. C. Rogers, N. Sato, B. Wang, "Challenges with
  > Large Transverse Momentum in Semi-Inclusive Deeply Inelastic Scattering",
  > Phys. Rev. D 98 (2018) 114005, [arXiv:1808.04396](https://arxiv.org/abs/1808.04396),
  > doi:10.1103/PhysRevD.98.114005.

  Its Eq. 1 is $\mathbf{q}_T = -\mathbf{P}_{H,T}/z$, with $\mathbf{P}_{H,T}$ the
  Breit-frame hadron transverse momentum: "in a frame where the incoming and
  outgoing hadrons are back-to-back, $\mathbf{q}_T$ is the transverse momentum of
  the virtual photon", and $z \equiv P_H\cdot P/(P\cdot q)$. Both ingredients
  match this pipeline **exactly, not to leading order**:

  | ingredient | where | why it matches |
  |---|---|---|
  | $P_{hT}$ | transverse to **q** by construction — see *What $P_T$ is measured against* in Step 1 | the target rest frame reaches the Breit frame by a pure boost **along q** ($\beta = \nu/\lvert q\rvert$), and transverse components are invariant under it |
  | $z$ | `Lsidis3.h:516`, hadron energy `z * Pq_1.E()`; `Pq_1.E()` $=\nu$ from `:496` in the target rest frame (`:487`) | $z = E_h/\nu = (P\cdot P_H)/(P\cdot q)$, the paper's definition |

  Dividing by $Q$ instead of $zQ$ is the error worth guarding against: the
  paper's Eq. 8, $\lvert k^2\rvert/Q^2 = 1-\hat z+\hat z\,q_T^2/Q^2$, is what
  makes $q_T/Q$ "the relevant Lorentz invariant measure of the size of transverse
  momentum", and $P_{hT}/Q$ understates it by $1/z \approx 2$ at these
  kinematics.

  **Mass-correction footnote.** The paper drops masses — it assumes "$x$ and
  $1/Q$ are small enough that both the proton, final state hadron, and lepton
  masses can be dropped in phase space factors" — and cautions that "the values
  of $Q$ for the experiments we examine here can be quite low. In the future,
  target and hadron mass effects should be examined in greater detail." At SoLID
  kinematics $\gamma = 2xM/Q$ runs 0.11 to 0.44, so that caution applies here.
  Sizing it by recomputing $q_T/Q$ with the generator's own mass-corrected
  light-cone fraction `zn` (`Lsidis3.h:541`) in place of $z$: the axis shifts
  **+0.8% to +10.1%, median +2.6%**, growing with $Q^2$ (median +1.8% at
  $Q^2 = 1$–2 GeV², +4.1% at 6–8); 22 of 447 rows leave $q_T/Q<0.3$, 11 of 618
  leave $q_T/Q<0.4$. `zn` is **not** a competing definition — it is the
  Nachtmann-type fraction `CalculateRfactor` uses, and the paper's Eq. 3
  $\zeta$ is a partonic variable, different again — so that spread measures the
  ambiguity the paper leaves open, not a correction to apply. It is a
  few-percent systematic on the axis, smaller than the ±20% run-to-run noise on
  improvement factors, and it cancels between datasets, which all share it.

- **No $q_T$ cut is applied anywhere in this pipeline.** `Ptlist` in
  `GenerateBinInfoFile` tops out at 1.6 GeV — an absolute $P_T$ bound, not a
  $q_T/Q$ one — and `AnalyzeEstatUT3` bounds $z$, $Q^2$ and $P_T$ only through
  each bin's `SetRange`. Measured on `data_phifull`, $q_T/Q = P_T/(zQ)$ runs to
  1.97 with a median of 0.52 and **43% of bins above 0.6**. By the 2022 paper's
  $q_T/Q \lesssim 0.4$ guide, a substantial part of the SoLID pseudodata lies
  outside the region where TMD factorisation is expected to hold. For contrast,
  the SBS projection in `data_sbs/sbs0{1,2}.dat` *does* carry such a cut
  (roughly $q_T \lesssim 0.6\,Q$) — see `data_world/README.md`, which is why
  those files must not be used for rate or figure-of-merit counting.

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
