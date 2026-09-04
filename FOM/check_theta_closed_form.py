#!/usr/bin/env python3
"""Check plot_fom_qtq_vs_theta_grid.py's closed-form hadron lab angle against
the vector construction in ../kinematics/plot_qtq_vs_theta.py.

The grid script needs theta_h for ~300k (row, phi_h) samples, so it uses the
closed form

    cos(theta_h) = [ pT cos(phi_h) sin(theta_q) + pL cos(theta_q) ] / |P_h|

instead of building the (ex, ey, qhat) frame and rotating a vector per sample.
That is an algebraic simplification of the frame construction, not a second
model of the kinematics -- and the frame construction is in turn validated
against Lsidis3.h itself by ../kinematics/check_against_lsidis.C. So this
program closes the chain: closed form -> frame construction -> the header.

    source /usr/share/Modules/init/zsh && source ../setup.sh
    ./check_theta_closed_form.py        # exit 0 = agree

Last run (2026-09-03): 900 points over 5 kinematic points x 180 azimuths,
worst |d theta_h| = 6.3e-13 deg -- floating-point round-off.
"""
import os, sys, importlib.util
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from plot_fom_qtq_vs_theta_grid import expand, MH, PHI_N

_spec = importlib.util.spec_from_file_location(
    'kin', os.path.join(HERE, '..', 'kinematics', 'plot_qtq_vs_theta.py'))
kin = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kin)

M = 0.938272
TOL = 1e-9                                     # deg; round-off runs ~1e-12

# (Ebeam, Q2, x, z, pT) spanning both beam energies and the corners of the
# generated range -- small and large theta_q, small and large pT/|P_h|.
POINTS = [(11.0, 2.0, 0.15, 0.40, 0.30), (11.0, 5.0, 0.45, 0.60, 0.50),
          (8.8,  3.0, 0.30, 0.35, 0.15), (11.0, 1.5, 0.09, 0.55, 0.80),
          (8.8,  7.0, 0.55, 0.65, 1.00)]


def main():
    d = pd.DataFrame([dict(x=x, Q2=Q2, z=z, pT=pT, y=Q2 / (2 * M * x) / E,
                           Ebeam=E, hadron='pi+', err=1.0)
                      for E, Q2, x, z, pT in POINTS])
    theta = expand(d, 'err', 'check')[2].reshape(len(d), PHI_N)
    phi = (np.arange(PHI_N) + 0.5) * 2.0 * np.pi / PHI_N

    worst = 0.0
    for i, r in d.iterrows():
        k = kin.kinematics(r.Ebeam, r.Q2, r.x, r.z, MH['pi+'])
        ref = np.array([kin.theta_lab(kin.hadron(k, r.pT, p))[0] for p in phi])
        dmax = np.abs(ref - theta[i]).max()
        worst = max(worst, dmax)
        print(f'  E={r.Ebeam:4.1f} Q2={r.Q2:4.1f} x={r.x:5.2f} z={r.z:4.2f} '
              f'pT={r.pT:4.2f}:  theta_h {theta[i].min():6.2f}-'
              f'{theta[i].max():6.2f} deg,  max |diff| {dmax:.2e} deg')

    n = len(d) * PHI_N
    print(f'\n  {n} points, worst |d theta_h| = {worst:.3e} deg  (tol {TOL:g})')
    if worst > TOL:
        sys.exit('  MISMATCH')
    print('  agree')


if __name__ == '__main__':
    main()
