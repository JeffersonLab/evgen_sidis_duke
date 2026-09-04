// Validation of plot_qtq_vs_theta.py against Lsidis3.h itself.
//
// The python script rewrites Lsidis::CalculateFinalStateKinematics for a target
// at rest so it can scan (Pt, phi_h) without ROOT. This program runs the real
// thing over the same grid and prints the largest disagreement in the hadron
// lab angle, its momentum, and the scattered-electron angle. Anything above
// ~1e-4 deg, or any rejected point, means the two have drifted apart.
//
//   source /usr/share/Modules/init/zsh && source ../setup.sh
//   g++ --std=c++17 -I$LHAPDFSYS/include $(root-config --cflags) \
//       -o check_against_lsidis check_against_lsidis.C \
//       $(root-config --libs) $(lhapdf-config --cflags --libs)
//   ./check_against_lsidis            # from this directory
//
// Not built by the makefile: that one is generic in a single $(O).C at the repo
// root and this is a one-off check, not part of the pipeline.
#include <cstdio>
#include <cmath>
#include "TLorentzVector.h"
#include "../Lsidis3.h"

int main(){
  const double M = 0.938272, E = 10.6, Q2 = 5.0, x = 0.5, z = 0.5;
  const double nu = Q2 / (2.0 * M * x), y = nu / E;

  Lsidis sidis;
  TLorentzVector l(0, 0, E, E), P(0, 0, 0, M);
  sidis.SetNucleus(1, 0);          // proton; kinematics do not depend on it
  sidis.SetHadron("pi+");
  sidis.SetInitialState(l, P);

  // Same construction as the python side, repeated here so the two are
  // independent: beam along +z, scattered electron in the +x half-plane.
  const double Ep = E - nu, cte = 1.0 - Q2 / (2.0 * E * Ep);
  const double ste = sqrt(1.0 - cte * cte);
  TLorentzVector lp(Ep * ste, 0, Ep * cte, Ep), q = l - lp;
  TVector3 qhat = q.Vect().Unit();
  TVector3 ex = (lp.Vect() - lp.Vect().Dot(qhat) * qhat).Unit();
  TVector3 ey = qhat.Cross(ex);
  const double Mh = 0.13957, Eh = z * nu, ph = sqrt(Eh * Eh - Mh * Mh);

  // Lsidis3.h also cuts on the recoil mass, W'^2 = (q + P - Ph)^2 > m_pi0^2,
  // which here bites long before Pt reaches |P_h| -- the ceiling the python
  // script plots. Scan only inside it, so every point should be accepted.
  const double wp2c = M * M - Q2 + Mh * Mh + 2.0 * M * nu
                    - 2.0 * M * Eh - 2.0 * nu * Eh;
  const double Mpi0 = 0.1349766;
  const double pLmin = (Mpi0 * Mpi0 - wp2c) / (2.0 * q.Vect().Mag());
  const double Ptmax = sqrt(ph * ph - pLmin * pLmin);
  printf("scanning Pt up to %.4f GeV (|P_h| = %.4f, W' > m_pi0)\n", Ptmax, ph);

  double dth = 0, dp = 0, dthe = 0;
  int n = 0, bad = 0;
  for (int i = 0; i <= 200; i++){
    double Pt = Ptmax * i / 201.0;
    double pL = sqrt(ph * ph - Pt * Pt);
    for (int j = 0; j < 24; j++){
      double phih = 2.0 * M_PI * j / 24.0;
      sidis.SetVariables(x, y, z, Pt, phih, 0.0);
      sidis.CalculateFinalStateKinematics();
      TLorentzVector Ph = sidis.GetLorentzVector("Ph");
      if (Ph.E() == 0){ bad++; continue; }   // GetLorentzVector's unphysical flag
      TLorentzVector LP = sidis.GetLorentzVector("lp");
      TVector3 mine = Pt * cos(phih) * ex + Pt * sin(phih) * ey + pL * qhat;
      dth  = std::max(dth,  fabs(Ph.Theta() - mine.Theta()) * 180.0 / M_PI);
      dp   = std::max(dp,   fabs(Ph.P() - ph));
      dthe = std::max(dthe, fabs(LP.Theta() - lp.Theta()) * 180.0 / M_PI);
      n++;
    }
  }
  printf("compared %d (Pt, phi_h) points, %d rejected by Lsidis\n", n, bad);
  printf("  max |d theta_h|  = %.3e deg\n", dth);
  printf("  max |d |P_h||    = %.3e GeV\n", dp);
  printf("  max |d theta_e'| = %.3e deg\n", dthe);
  // Tolerances are TLorentzVector rotation round-off, not physics.
  return (bad == 0 && dth < 1e-4 && dp < 1e-6 && dthe < 1e-6) ? 0 : 1;
}
