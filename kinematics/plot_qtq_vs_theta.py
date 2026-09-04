#!/usr/bin/env python3
"""qT/Q against the lab polar angle of the detected hadron, for SIDIS off a
PROTON AT REST, at one fixed (Ebeam, Q2, x, z) point.

    default point:  Ebeam = 10.6 GeV,  Q2 = 5 GeV^2,  x = 0.5,  z = 0.5,  pi+

qT is the transverse momentum of the virtual photon in the frame where the
target and the hadron are collinear, so qT = PhT/z and

    qT/Q = PhT / (z sqrt(Q2))

the same definition ../FOM/plot_fom_solid_vs_sbs.py uses. TMD factorisation is
the qT << Q corner; qT/Q ~ 1 and above is where it is not expected to hold (see
../physics.md and Lsidis3.h:CalculateRfactor for the collinearity criterion this
repo applies instead).

WHY THE PLOT IS A CURVE AND NOT A POINT.  Fixing Ebeam, Q2, x, z fixes the whole
event except the hadron's direction around the virtual photon: the scattered
electron is fully determined, the virtual photon direction is fully determined,
and the hadron's ENERGY is fixed at E_h = z*nu, hence its momentum |P_h| too.
The one remaining freedom is where that fixed-length momentum points, i.e.
(PhT, phi_h). Every lab angle theta_h therefore maps to a definite PhT, hence to
a definite qT/Q. The map is two-valued in the scattering plane -- the hadron can
tilt toward the beam (and past it, to the scattered-electron side) or away from
it -- which is why the left panel uses a SIGNED in-plane angle.

SIGN CONVENTION (left panel).  Right-handed lab frame: +z along the beam, +y up,
hence +x to BEAM LEFT (left as seen looking downstream) and -x to BEAM RIGHT.
The azimuth of the scattering plane is free, and is fixed here by putting the
scattered electron on beam left; the virtual photon is then on beam right.

The plotted angle is POSITIVE for a hadron on BEAM RIGHT and NEGATIVE for one on
BEAM LEFT. So the curve descends from beam left (where the hadron is on the
electron's side), crosses zero at the beam line, touches qT/Q = 0 at
theta_h = theta_q where the hadron is collinear with the virtual photon, and
climbs again further to beam right.

The right panel is the measurable, unsigned lab angle, with one curve per
azimuth phi_h around the virtual photon (phi_h = 0 is the hadron transverse
momentum along the transverse part of the SCATTERED electron, which is
Lsidis3.h's phih offset). The out-of-plane curves fill the band between the two
in-plane branches.

WHY THE CEILING LANDS NEAR qT/Q = 1 HERE.  Drop the hadron mass and expand
W'^2 = (q + P - P_h)^2 to first order in PhT^2:

    W'^2  ~  M^2 + (1-z)(W^2 - M^2) - PhT^2/z ,      W^2 - M^2 = Q^2 (1-x)/x

so requiring a recoil no lighter than a nucleon, W'^2 > M^2, gives

    PhT_max^2 ~ z(1-z) Q^2 (1-x)/x    ->    (qT/Q)_max ~ sqrt( (1-x)(1-z) / (x z) )

which is EXACTLY 1 at x = z = 0.5, whatever Q^2 and whatever the beam energy.
The default point sits on that line by coincidence, and the two ceilings the
script draws straddle it: 0.92 where Lsidis3.h's FUUT stops returning a cross
section (Lsidis3.h:744, W' > MXminp), 1.06 where its kinematics stop altogether
(Lsidis3.h:533, W' > m_pi0). The approximation runs ~10% high here (Q^2/nu^2 = 0.18 is not
negligible and the target-mass terms are dropped), so the printed ceilings are
the exact ones -- the formula only explains the scale, and it tracks them to
5-20% over the range this script can reach. Away from x = z = 0.5 the ceiling
moves fast: (x, z) = (0.2, 0.4) at Q2 = 3 gives 2.45 against an exact 2.33,
(0.6, 0.7) at Q2 = 5 gives 0.53 against an exact 0.45.

KINEMATICS are Lsidis3.h:CalculateFinalStateKinematics rewritten for a target at
rest (no boost): massless beam electron, cos(theta_e) = 1 - Q2/(2 E E'),
E_h = z*nu with z the energy fraction in the target rest frame, and the hadron
built in the frame with z-axis along q. Validated against Lsidis3.h itself --
see check_against_lsidis.C in this directory.

    source /usr/share/Modules/init/zsh && source ../setup.sh && ./plot_qtq_vs_theta.py
    ./plot_qtq_vs_theta.py --x 0.3 --Q2 3 --z 0.4 --hadron K+
"""
import os, argparse
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))

M = 0.938272                                   # proton mass, GeV
MH = {'pi+': 0.13957, 'pi-': 0.13957, 'K+': 0.493677, 'K-': 0.493677}
MPI0 = 0.1349766                               # Lsidis3.h's own W' threshold

# Lightest recoil X allowed in gamma* p -> h X by baryon number, charge and
# strangeness. This, not |P_h|, is what really caps PhT at a fixed (Q2, x, z).
# These are Lsidis3.h's OWN MXminp, verbatim from Lsidis::SetHadron
# (Lsidis3.h:219-262), so the ceiling drawn here is the generator's, not a
# reinvention of it. The header applies them in FUUT (Lsidis3.h:744, :747):
# above this W' the structure function is set to zero, i.e. the event survives
# the kinematics but carries no cross section.
MP, MPION, MKAON, MLAMBDA = 0.938272081, 0.13957018, 0.493677, 1.115683
MX_MIN = {'pi+': MP, 'pi-': MP + MPION,          # X = n, X = p pi+
          'K+': MLAMBDA, 'K-': MP + MKAON}       # X = Lambda, X = p K+
MX_LABEL = {'pi+': r'$M_p$', 'pi-': r'$M_p + m_\pi$',
            'K+': r'$M_\Lambda$', 'K-': r'$M_p + m_K$'}

# SoLID hadron acceptance: forward angle only, 8-18 deg (../SoLID_SIDIS_3He.h,
# GetAcceptance_pip/pim). The electron adds the large-angle arm out to 30 deg.
SOLID_HADRON_THETA = (8.0, 18.0)


def kinematics(E, Q2, x, z, Mh):
    """Everything fixed by (E, Q2, x, z), in the lab with the target at rest.

    Returns a dict; 'qhat', 'ex', 'ey' are the orthonormal frame the hadron is
    built in (ex in the lepton plane toward the scattered electron, qhat along
    the virtual photon).
    """
    nu = Q2 / (2.0 * M * x)
    Ep = E - nu                                                # scattered e-
    if Ep <= 0:
        raise SystemExit(f'unphysical: E\' = {Ep:.3f} GeV <= 0 (nu = {nu:.3f})')
    y = nu / E
    cte = 1.0 - Q2 / (2.0 * E * Ep)
    if abs(cte) > 1:
        raise SystemExit(f'unphysical: cos(theta_e) = {cte:.4f}')
    ste = np.sqrt(1.0 - cte * cte)

    l = np.array([0.0, 0.0, E])
    lp = Ep * np.array([ste, 0.0, cte])       # +x = beam left (free choice)
    q = l - lp
    qmag = np.linalg.norm(q)                                   # = sqrt(nu^2+Q2)
    qhat = q / qmag

    W2 = M * M + 2.0 * M * nu - Q2
    if W2 < (M + MPI0) ** 2:
        raise SystemExit(f'unphysical: W2 = {W2:.3f} GeV^2 below threshold')

    Eh = z * nu                                                # z = E_h/nu
    if Eh <= Mh:
        raise SystemExit(f'unphysical: E_h = {Eh:.3f} GeV <= Mh = {Mh:.3f}')
    ph = np.sqrt(Eh * Eh - Mh * Mh)

    ex = lp - np.dot(lp, qhat) * qhat            # toward e', i.e. beam left
    ex = ex / np.linalg.norm(ex)
    ey = np.cross(qhat, ex)
    # W'^2 = (q + P - P_h)^2 = wp2_const + 2 |q| pL
    wp2_const = (M * M - Q2 + Mh * Mh + 2.0 * M * nu
                 - 2.0 * M * Eh - 2.0 * nu * Eh)
    return dict(wp2_const=wp2_const, Mh=Mh, nu=nu, y=y, Ep=Ep, qmag=qmag,
                Q=np.sqrt(Q2), W=np.sqrt(W2),
                theta_e=np.degrees(np.arccos(cte)),
                theta_q=np.degrees(np.arccos(qhat[2])),
                Eh=Eh, ph=ph, l=l, lp=lp, q=q, qhat=qhat, ex=ex, ey=ey)


def wp2(k, Pt):
    """Invariant mass squared of the recoiling system X in gamma* p -> h X.

    W'^2 = (q + P - P_h)^2. It depends on Pt only through the longitudinal
    momentum pL, not on phi_h, so the limits it sets are horizontal lines in
    qT/Q. Lsidis3.h cuts on it twice, and the two are far apart:

      Lsidis3.h:406, :533   W' > m_pi0     kinematics; physics_control = false
      Lsidis3.h:744, :747   W' > MXminp    FUUT returns 0, so no cross section

    The first is the edge of the generated phase space, the second is the
    physical one. Both are drawn.
    """
    pL = np.sqrt(np.maximum(k['ph'] ** 2 - np.asarray(Pt, float) ** 2, 0.0))
    return k['wp2_const'] + 2.0 * k['qmag'] * pL


def ptmax_for(k, Wmin):
    """Largest Pt with W' >= Wmin; None if even Pt = 0 is below it."""
    pL = (Wmin * Wmin - k['wp2_const']) / (2.0 * k['qmag'])
    if pL >= k['ph']:
        return None
    return k['ph'] if pL <= 0 else np.sqrt(k['ph'] ** 2 - pL ** 2)


def hadron(k, Pt, phi):
    """Lab hadron 3-momentum for transverse momentum Pt at azimuth phi (rad)."""
    Pt = np.atleast_1d(Pt).astype(float)
    pL = np.sqrt(np.maximum(k['ph'] ** 2 - Pt ** 2, 0.0))      # along q
    return (np.outer(Pt * np.cos(phi), k['ex'])
            + np.outer(Pt * np.sin(phi), k['ey'])
            + np.outer(pL, k['qhat']))


def theta_lab(P):
    """Unsigned lab polar angle, deg."""
    return np.degrees(np.arccos(P[:, 2] / np.linalg.norm(P, axis=1)))


def theta_signed(P):
    """In-plane lab angle, deg, positive to beam right (-x), negative to beam
    left (+x). +x is beam left because the frame is right-handed with +y up."""
    return np.degrees(np.arctan2(-P[:, 0], P[:, 2]))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--E', type=float, default=10.6, help='beam energy, GeV')
    ap.add_argument('--Q2', type=float, default=5.0, help='Q^2, GeV^2')
    ap.add_argument('--x', type=float, default=0.5, help='Bjorken x')
    ap.add_argument('--z', type=float, default=0.5, help='z = E_h/nu')
    ap.add_argument('--hadron', default='pi+', choices=sorted(MH))
    ap.add_argument('--qtqmax', type=float, default=3.0, help='y-axis top')
    ap.add_argument('--out', default=os.path.join(HERE, 'qtq-vs-theta-hadron'))
    a = ap.parse_args()

    Mh = MH[a.hadron]
    k = kinematics(a.E, a.Q2, a.x, a.z, Mh)
    Q, z = k['Q'], a.z

    # Two ceilings, both horizontal in qT/Q since W' does not depend on phi_h.
    pt_gen = ptmax_for(k, MPI0)                # where Lsidis3.h stops generating
    pt_bar = ptmax_for(k, MX_MIN[a.hadron])    # lightest allowed recoil
    if pt_gen is None:
        raise SystemExit('no phase space: W\' < M_pi0 even at Pt = 0')
    Pt = np.linspace(0.0, pt_gen, 6001)
    qtq = Pt / (z * Q)
    qtq_gen = pt_gen / (z * Q)
    qtq_bar = None if pt_bar is None else pt_bar / (z * Q)

    hlab = {'pi+': r'$\pi^+$', 'pi-': r'$\pi^-$',
            'K+': r'$K^+$', 'K-': r'$K^-$'}[a.hadron]
    tag = (f"E = {a.E} GeV,  $Q^2$ = {a.Q2} GeV$^2$,  x = {a.x},  z = {a.z},  "
           f"{hlab}   |   proton at rest")

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.2, 5.2))

    # ------------------------------------------------ left: signed, in-plane
    # phi_h = 180 deg tilts the hadron away from the beam (photon side), phi_h =
    # 0 tilts it back toward the beam and then across to the electron side.
    for phi, colour in ((np.pi, 'C0'), (0.0, 'C3')):
        t = theta_signed(hadron(k, Pt, phi))
        axL.plot(t, qtq, color=colour, lw=2)
    axL.axvline(k['theta_q'], color='0.4', ls='--', lw=1.2)
    axL.text(k['theta_q'], a.qtqmax * 0.97, r'  $\theta_q$', color='0.35',
             ha='left', va='top', fontsize=10)
    axL.axvline(-k['theta_e'], color='0.4', ls=':', lw=1.2)
    axL.text(-k['theta_e'], a.qtqmax * 0.97, r"  $-\theta_{e'}$", color='0.35',
             ha='left', va='top', fontsize=10)
    axL.axvline(0.0, color='0.85', lw=1.0, zorder=0)
    axL.set_xlabel(r'in-plane lab angle of the hadron  $\theta_h$  [deg]'
                   '\n' r'(+ = beam right, $-$ = beam left)', size=12)
    axL.set_title(r"in the lepton scattering plane ($e'$ on beam left)",
                  size=11)

    # ----------------------------------- right: unsigned lab angle, phi_h scan
    for phi_deg, colour in ((0, 'C3'), (45, 'C1'), (90, 'C2'),
                            (135, 'C4'), (180, 'C0')):
        P = hadron(k, Pt, np.radians(phi_deg))
        axR.plot(theta_lab(P), qtq, color=colour, lw=1.8,
                 label=rf'$\phi_h$ = {phi_deg}$^\circ$')
    axR.axvspan(*SOLID_HADRON_THETA, color='C7', alpha=0.15, zorder=0)
    axR.text(np.mean(SOLID_HADRON_THETA), a.qtqmax * 0.55,
             'SoLID hadron acceptance', ha='center', va='center',
             rotation=90, fontsize=9, color='0.35')
    axR.axvline(k['theta_q'], color='0.4', ls='--', lw=1.2)
    axR.legend(loc='upper right', frameon=True, fontsize=9)
    axR.set_xlabel(r'lab polar angle of the hadron  $\theta_h$  [deg]', size=12)
    axR.set_title(r'all azimuths $\phi_h$ about the virtual photon', size=11)

    for ax in (axL, axR):
        ax.axhspan(0.0, 0.3, color='C2', alpha=0.10, zorder=0)
        # The curves already stop at qtq_gen; shade what the missing mass
        # forbids so the ceiling is not mistaken for the edge of the scan.
        ax.axhspan(qtq_gen, a.qtqmax, color='0.5', alpha=0.13, zorder=0)
        ax.axhline(qtq_gen, color='0.35', lw=1.2)
        if qtq_bar is not None:
            ax.axhspan(qtq_bar, qtq_gen, color='0.5', alpha=0.10, zorder=0)
            ax.axhline(qtq_bar, color='0.35', lw=1.2, ls=':')
        ax.set_ylim(0.0, a.qtqmax)
        ax.set_ylabel(r'$q_T/Q = P_{hT}/(z\,Q)$', size=13)
        ax.tick_params(axis='both', which='both', direction='in',
                       top=True, right=True, labelsize=11)
    xl = axL.get_xlim()[0] + 0.02 * np.ptp(axL.get_xlim())
    axL.text(xl, 0.30, r'$q_T/Q < 0.3$: TMD region', va='bottom',
             fontsize=9, color='C2')
    axL.text(xl, qtq_gen + 0.01 * a.qtqmax,
             r"$W' > m_{\pi^0}$: Lsidis3.h:533 kinematic edge",
             va='bottom', fontsize=9, color='0.3')
    if qtq_bar is not None:
        axL.text(xl, qtq_bar - 0.01 * a.qtqmax,
                 r"$W' > M_X^{min}$ = " + MX_LABEL[a.hadron]
                 + f" ({MX_MIN[a.hadron]:.3f} GeV): "
                 + r"Lsidis3.h:744, $F_{UU,T} = 0$ above",
                 va='top', fontsize=9, color='0.3')

    fig.suptitle(tag, size=12)
    fig.text(0.5, 0.005,
             r'lab frame: beam along $+z$, scattered electron at $+x$ '
             r'(beam left), $+y$ up;  $\phi_h$ is the hadron azimuth about '
             r'$\vec{q}$, measured from the $e^\prime$ side',
             ha='center', va='bottom', fontsize=8, color='0.35')
    fig.tight_layout(rect=[0, 0.045, 1, 0.95])
    for ext in ('png', 'pdf'):
        p = f'{a.out}.{ext}'
        fig.savefig(p, dpi=150 if ext == 'png' else None)
        print(f'wrote {p}')

    # ------------------------------------------------------------- numbers
    print(f"""
  fixed point            E = {a.E} GeV, Q2 = {a.Q2} GeV^2, x = {a.x}, z = {a.z}, {a.hadron}
  nu = Q2/(2 M x)      = {k['nu']:.4f} GeV      y = {k['y']:.4f}
  E' = E - nu          = {k['Ep']:.4f} GeV      theta_e' = {k['theta_e']:.3f} deg
  |q| = sqrt(nu^2+Q2)  = {k['qmag']:.4f} GeV    theta_q  = {k['theta_q']:.3f} deg
  W                    = {k['W']:.4f} GeV
  E_h = z nu           = {k['Eh']:.4f} GeV      |P_h| = {k['ph']:.4f} GeV (fixed)
  qT/Q at PhT = |P_h|  = {k['ph'] / (z * Q):.3f}   (never reached, see below)
  W' > m_pi0  ceiling  = {qtq_gen:.3f}   PhT = {pt_gen:.4f} GeV  <- Lsidis3.h:533, kinematics stop
  W' > MXminp ceiling  = {'n/a' if qtq_bar is None else f'{qtq_bar:.3f}'}   PhT = {'n/a' if pt_bar is None else f'{pt_bar:.4f} GeV'}  <- Lsidis3.h:744, FUUT = 0 above
  sqrt((1-x)(1-z)/(x z)) = {np.sqrt((1 - a.x) * (1 - z) / (a.x * z)):.3f}   massless small-PhT estimate of the line above
""")
    print('  qT/Q  PhT[GeV]  theta_h in-plane [deg]      theta_h range over phi_h')
    print('                  photon side  e- side         min      max')
    for r in (0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.25, 1.5):
        pt = r * z * Q
        if pt > pt_gen:
            print(f'  {r:4.2f}  {pt:7.3f}   -- forbidden, W\' below m_pi0 --')
            continue
        flag = ('' if (pt_bar is not None and pt <= pt_bar)
                else '   (W\' below the lightest recoil)')
        tp = theta_signed(hadron(k, pt, np.pi))[0]
        tm = theta_signed(hadron(k, pt, 0.0))[0]
        phis = np.linspace(0, 2 * np.pi, 721)
        tall = np.array([theta_lab(hadron(k, pt, p))[0] for p in phis])
        print(f'  {r:4.2f}  {pt:7.3f}   {tp:10.3f}  {tm:8.3f}      '
              f'{tall.min():7.3f}  {tall.max():7.3f}{flag}')

    lo, hi = SOLID_HADRON_THETA
    ok = qtq <= (qtq_gen if qtq_bar is None else qtq_bar)   # physical rows only
    inside = []
    for phi in np.linspace(0, 2 * np.pi, 361):
        P = hadron(k, Pt, phi)
        t = theta_lab(P)
        m = ok & (t >= lo) & (t <= hi)
        if m.any():
            inside.append((qtq[m].min(), qtq[m].max()))
    if inside:
        print(f'  inside SoLID {lo:g}-{hi:g} deg for the hadron (physical rows): '
              f'qT/Q from {min(a_ for a_, _ in inside):.3f} '
              f'to {max(b for _, b in inside):.3f}')
    else:
        print(f'  no hadron direction at this point lands in {lo:g}-{hi:g} deg')


if __name__ == '__main__':
    main()
