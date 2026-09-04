# `kinematics/` — standalone kinematic maps

Small, self-contained pictures of SIDIS kinematics at a **single fixed
(Ebeam, Q2, x, z) point**. No run directory, no pseudodata, no fit: everything
here is closed-form kinematics, so a script in this directory reads nothing but
its own command line.

That is the rule for what belongs here. Anything that needs `<rundir>` output
belongs with the study that produced it (`SIDIS_MUT3_comparison/`,
`phicompare/`, `FOM/`), not here.

| script | writes | shows |
|---|---|---|
| `plot_qtq_vs_theta.py` | `qtq-vs-theta-hadron.{png,pdf}` | qT/Q against the hadron's lab polar angle |
| `check_against_lsidis.C` | — | validation of the above against `../Lsidis3.h` |

The same axes over the *pseudodata* rather than one fixed point live in
`../FOM/plot_fom_qtq_vs_theta_grid.py`, which tiles a FOM-weighted (θ_h, qT/Q)
map per (x, Q²) cell. It reuses the closed form derived here — and
`../FOM/check_theta_closed_form.py` checks it against `plot_qtq_vs_theta.py`'s
vector construction, so that script's validation chain ends at
`check_against_lsidis.C` below.

## `plot_qtq_vs_theta.py`

```
source /usr/share/Modules/init/zsh && source ../setup.sh
./plot_qtq_vs_theta.py                              # 10.6 GeV, Q2 = 5, x = 0.5, z = 0.5, pi+
./plot_qtq_vs_theta.py --x 0.3 --Q2 3 --z 0.4 --hadron K+
```

qT is the virtual photon's transverse momentum in the frame where target and
hadron are collinear, so `qT/Q = PhT/(z sqrt(Q2))` — the same definition
`../FOM/plot_fom_solid_vs_sbs.py` uses.

**Why it is a curve.** Fixing (E, Q2, x, z) fixes the scattered electron, the
virtual photon direction, and the hadron's *energy* `E_h = z nu`, hence `|P_h|`.
Only the hadron's direction is left free, so lab angle and qT/Q are in one-to-one
correspondence at each azimuth. Left panel: signed in-plane angle in a
right-handed lab frame (+z beam, +y up, so +x is beam left) with the scattered
electron put on beam left -- **positive = hadron on beam right**, which is the
virtual-photon side, so the curve touches qT/Q = 0 at theta_q. Right panel: the
measurable unsigned angle, one curve per phi_h.

**Two ceilings, and neither is `|P_h|`.** The recoiling system X in
`gamma* p -> h X` must have a real mass, and `W'^2 = (q + P - P_h)^2` shrinks as
PhT grows. `Lsidis3.h` cuts on W' in two different places, far apart:

| where | cut | at the default point |
|---|---|---|
| `Lsidis3.h:406`, `:533` | `W' > m_pi0`, else `physics_control = false` | qT/Q = 1.06 |
| `Lsidis3.h:744`, `:747` | `W' > MXminp`, else `FUUT` returns 0 | qT/Q = 0.92 |

The first is where the generator stops producing events at all; the second is
the physical one — `MXminp` is the lightest recoil allowed by baryon number,
charge and strangeness, set per hadron in `Lsidis::SetHadron`
(`Lsidis3.h:219-262`: `Mp` for pi+, `Mp + Mpion` for pi-, `MLambda` for K+,
`Mp + Mkaon` for K-). This script copies those values rather than re-deriving
them. Above that line an event still exists kinematically but carries no cross
section. Both are far below the naive `|P_h|/(z Q)` = 2.38, and both are
horizontal (W' does not depend on phi_h).

**Why the ceiling sits near 1 at this point.** Dropping the hadron mass and
expanding W'^2 to first order in PhT^2,

    W'^2 ~ M^2 + (1-z)(W^2 - M^2) - PhT^2/z,     W^2 - M^2 = Q^2 (1-x)/x

so W' > M_N gives `(qT/Q)_max ~ sqrt((1-x)(1-z)/(x z))`, which is **exactly 1 at
x = z = 0.5** for any Q2 and any beam energy. The default point sits on that
line by coincidence; the two exact ceilings straddle it (0.92 from `FUUT`, 1.06
from the kinematics). The estimate runs 5-20% high — it drops the
target-mass and Q2/nu^2 terms — so quote the printed exact numbers, not the
formula. It moves fast away from that point: (x, z) = (0.2, 0.4) at Q2 = 3 gives
2.33, (0.6, 0.7) at Q2 = 5 gives 0.45. The script prints both.

**Standing result at the default point** (E = 10.6, Q2 = 5, x = 0.5, z = 0.5,
pi+): nu = 5.329, E' = 5.271, theta_e' = 17.20 deg, theta_q = 15.65 deg,
W = 2.42 GeV, |P_h| = 2.661 GeV. The TMD corner qT/Q < 0.3 is the hadron within
about 7 deg of the virtual photon, i.e. lab 8.4-22.9 deg in-plane — which sits
almost exactly on SoLID's 8-18 deg hadron acceptance. Pushing to the
missing-mass edge only reaches qT/Q ~ 0.9, so **this (x, z) point cannot leave
the TMD-friendly region by much no matter where the pion goes.**

## `check_against_lsidis.C`

**The figures do not link against `Lsidis3.h`.** `plot_qtq_vs_theta.py` rewrites
`Lsidis::CalculateFinalStateKinematics` in numpy for a target at rest, which is
what lets it scan (Pt, phi_h) without ROOT or LHAPDF. The header enters only
here: this program runs the real one over the same grid and compares, so the
rewrite is checked rather than trusted.

```
source /usr/share/Modules/init/zsh && source ../setup.sh
g++ --std=c++17 -I$LHAPDFSYS/include $(root-config --cflags) \
    -o check_against_lsidis check_against_lsidis.C \
    $(root-config --libs) $(lhapdf-config --cflags --libs)
./check_against_lsidis          # exit 0 = agree
```

Last run (2026-09-03): 4824 points, 0 rejected, max |d theta_h| = 4.5e-6 deg,
max |d |P_h|| = 2.4e-7 GeV — `TLorentzVector` rotation round-off. It is not
built by the `makefile`: that one is generic in a single `$(O).C` at the repo
root, and this is a check, not part of the pipeline. The binary is gitignored.
