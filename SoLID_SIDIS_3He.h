#ifndef _SOLID_SIDIS_3HE_H_
#define _SOLID_SIDIS_3HE_H_

#include <fstream>
#include <cmath>
#include <string>
#include <cstdio>
#include "TFile.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TH2F.h"
#include "TCanvas.h"
#include "TStyle.h"
#include "TTree.h"
#include "TChain.h"
#include "TMatrixD.h"

#include "Lsidis3.h"

// Setting: helium-3 Np:Nn = 2:1, absolute number corresponds to lumi 10^36 neutrons cm^{-2} s^{-1}
const double Np = 2.0;
const double Nn = 1.0;

// Acceptance 
TFile * file_e = new TFile("Acceptance/acceptance_solid_SIDIS_He3_electron_1e7_201701_output_final.root", "r");
TFile * file_pim = new TFile("Acceptance/acceptance_solid_SIDIS_He3_pim_1e7_201701_output_final.root", "r");
TFile * file_pip = new TFile("Acceptance/acceptance_solid_SIDIS_He3_pip_1e7_201701_output_final.root", "r");
TFile * file_km = new TFile("Acceptance/acceptance_solid_SIDIS_He3_km_1e7_201701_output_final.root", "r"); 
TFile * file_kp = new TFile("Acceptance/acceptance_solid_SIDIS_He3_kp_1e7_201701_output_final.root", "r"); 
TH2F * acc_FA_e = (TH2F *) file_e->Get("acceptance_ThetaP_forwardangle");
TH2F * acc_LA_e = (TH2F *) file_e->Get("acceptance_ThetaP_largeangle");
TH2F * acc_FA_pim = (TH2F *) file_pim->Get("acceptance_ThetaP_forwardangle");
TH2F * acc_LA_pim = (TH2F *) file_pim->Get("acceptance_ThetaP_largeangle");
TH2F * acc_FA_pip = (TH2F *) file_pip->Get("acceptance_ThetaP_forwardangle");
TH2F * acc_LA_pip = (TH2F *) file_pip->Get("acceptance_ThetaP_largeangle");
TH2F * acc_FA_km = (TH2F *) file_km->Get("acceptance_ThetaP_forwardangle");
TH2F * acc_LA_km = (TH2F *) file_km->Get("acceptance_ThetaP_largeangle");
TH2F * acc_FA_kp = (TH2F *) file_kp->Get("acceptance_ThetaP_forwardangle");
TH2F * acc_LA_kp = (TH2F *) file_kp->Get("acceptance_ThetaP_largeangle");

double Rfactor0 = 1.0e5;
double pimin = 0.0;

//Azimuthal segmentation: false = full 2pi coverage (default, matches the "phifull" runs)
//phi_nsector sectors of phi_sector_width deg, evenly spaced and centred on phi = 0.
//The count comes from analysis_neutron.C's [phicut] argument and the width from
//its [phiwidth] argument; the width defaults to 24 deg, which is what every run
//logged in runlog.md before 2026-08-24 used.
//  6 x 24 deg -> centres at 0, +-60, +-120, 180 (40.0% of 2pi)
//  4 x 24 deg -> centres at 0, +-90, 180        (26.7% of 2pi)
//  2 x 24 deg -> centres at 0, 180              (13.3% of 2pi)
//  4 x 12 deg -> centres at 0, +-90, 180        (13.3% of 2pi -- same coverage
//                                                as 2 x 24, spread over four
//                                                narrower sectors)
//Coverage is phi_nsector * phi_sector_width / 360 only while the sectors stay
//disjoint, i.e. phi_sector_width <= 360/phi_nsector. Wider than that and they
//overlap, the formula lies, and the cut degenerates towards full acceptance;
//analysis_neutron.C rejects such a combination up front. Applied to the electron
//and to every hadron.
bool use_phi_cut = false;
int phi_nsector = 6;//number of active sectors; set from the [phicut] CLI arg
double phi_sector_width = 24.0;//full sector width in deg; set from [phiwidth]

//Where the segmentation sits, set from analysis_neutron.C's [phiscope] argument:
//  false ("all", default) - in front of every detector, so the cut applies to the
//                           electron and the hadron alike. What the 4- and
//                           6-sector runs already logged in runlog.md did.
//  true  ("FA")           - in front of the FORWARD-ANGLE detector only. A
//                           large-angle electron is then kept at any phi.
//Only the electron has a large-angle acceptance here (GetAcceptance_e sums
//acc_FA_e and acc_LA_e); every hadron is forward-angle only -- acc_LA_pip/pim/
//kp/km are loaded at the top of this file but never read -- so a hadron stays
//inside the cut in both modes. A SIDIS event needs both legs, so this option
//widens the electron's azimuthal coverage, not the event's: the coincidence is
//still gated by the hadron's phi_nsector * phi_sector_width.
bool phi_cut_fa_only = false;

//How the test works: collapse the whole azimuth onto a single sector, then ask
//how far the track is from that sector's centre.
//
//  fmod(a, b) is the floating-point remainder of a/b: it subtracts whole
//  multiples of b from a until what is left is smaller than b in magnitude, and
//  it keeps the SIGN OF a (so fmod(-170,90) = -80, not +10). Here it folds any
//  lab phi into an offset from the sector centre immediately below it.
//
//Step 1  d = fmod(phi, spacing)      offset from the centre BELOW phi, in
//                                    (-spacing, +spacing)
//Step 2  the two if()s               re-express d as the SIGNED DISTANCE TO THE
//                                    NEAREST centre, in [-spacing/2, +spacing/2]
//Step 3  fabs(d) < width/2           keep if within half a sector width
//
//Worked examples, phi_nsector = 4 with the default phi_sector_width = 24
//(spacing 90 deg, keep within +-12 deg). Narrowing the width to 12 would keep
//the same centres and tighten the verdict column to +-6 deg:
//
//   phi    fmod(phi,90)   after wrap   |d|    verdict
//     5          5            -          5    keep  (centre 0)
//    45         45            -         45    cut   (midway between centres)
//    80         80         -=90 -> -10   10    keep  (centre 90)
//   100         10            -         10    keep  (centre 90)
//   178         88         -=90 ->  -2    2    keep  (centre 180)
//  -170        -80         +=90 -> +10   10    keep  (centre -180)
//
//The phi=80 row is why step 2 exists: 80 deg is only 10 deg from the centre at
//90, but fmod reports 80 because it measures from the centre below. Without the
//wrap that track would be cut by mistake. The phi=-170 row shows the mirror case
//for negative phi, handled by the second if().
//
//For even phi_nsector, 180 deg is always a sector centre (180 is a whole
//multiple of both 90 and 60), so the cut is symmetric about the beamline.
//Switching 6 -> 4 sectors MOVES the centres, it does not merely narrow them:
//phi = 90 deg is kept by 4 sectors and cut by 6.
//
//Verified against a 360k-point scan: coverage comes out as
//phi_nsector * phi_sector_width / 360 exactly (26.67% for 4 x 24 deg, 40.00% for
//6 x 24 deg, 13.33% for 4 x 12 deg). The comparison is strict
//(<), so a track exactly on a sector edge is cut -- though in practice the
//round trip through the direction cosines in TLorentzVector::Phi() perturbs
//such a track by ~4e-15 deg, which decides the boundary either way. That is a
//measure-zero set with no physical consequence.
bool InPhiSector(const TLorentzVector p){//is the track inside an active azimuthal sector?
  if (!use_phi_cut || phi_nsector < 1) return true;
  const double spacing = 360.0 / phi_nsector;//centre-to-centre gap between sectors
  double d = fmod(p.Phi() / M_PI * 180.0, spacing);//lab phi is in (-180, 180]
  if (d >  0.5 * spacing) d -= spacing;//fold down to the centre above
  if (d < -0.5 * spacing) d += spacing;//fold up to the centre below
  return fabs(d) < 0.5 * phi_sector_width;//distance to the nearest sector centre
}


//Set false by analysis_neutron.C's [acccut] argument to remove the detector
//entirely: every GetAcceptance_* below then returns 1.0, so the theta ranges, the
//momentum thresholds, the azimuthal sectors and the acceptance maps are all
//bypassed and the run covers a perfect 4pi with unit efficiency. The physics cuts
//in the event loops (W, W', R-factor, hadron threshold) are untouched -- this
//switches off the *apparatus*, not the kinematics. Use it to separate what the
//acceptance costs from what the kinematics cost; it is not a physical
//configuration.
bool use_acc_cut = true;

//Selects the azimuthal map the moment matrix is built from, via
//analysis_neutron.C's [phisfold]. Both maps are booked at the same bin width,
//set by NPHI where they are created; only the phi_S range differs.
//  true  (DEFAULT) - hs_full, signed phi_S over [-pi,pi], Omega = 4pi^2
//  false           - hs, folded onto |phi_S| in [0,pi],   Omega = 2pi^2
//Folding makes MUT3 evaluate sin(phi_h - |phi_S|) rather than sin(phi_h - phi_S),
//which differs for every event with phi_S < 0; unfolding removes that
//approximation, which is why it is the default. Pass phisfold=fold to reproduce
//anything generated before 2026-08-27.
//The angular area travels with the choice, and the row-norm Estatraw is the one
//estimator that cares: it squares the inverse, so its historical hardcoded
//2pi^2 * pi^2 is Omega^2/2 at the folded Omega only. The general Omega^2/2 is
//used instead; Estatraw_diag and Estatraw_prop are Omega-independent.
//Measured effect of the folding alone, at 1 deg bins: 3.8e-3 max on the three
//test bins, consistent with <=2% in 90% of bins at 10 deg (check.md 2026-08-26).
//NB SIDIS_MUT3_comparison_base.md Section 2 is written for the folded Omega=2pi^2.
bool use_unfolded_phiS = true;
double thetamin = 8.0;
double GetAcceptance_e(const TLorentzVector p, const char * detector = "all"){//Get electron acceptance
  if (!use_acc_cut) return 1.0;
  double theta = p.Theta() / M_PI * 180.0;
  if (theta < thetamin || theta > 30.0) return 0;
  const bool inphi = InPhiSector(p);
  //With phi_cut_fa_only the segmentation gates the FA term alone, so fall through
  //to the LA term below instead of rejecting the track outright.
  if (!inphi && !phi_cut_fa_only) return 0;
  double mom = p.P();
  double acc = 0;
  if (inphi && (strcmp(detector, "FA") == 0 || strcmp(detector, "all") == 0))
    acc += acc_FA_e->GetBinContent(acc_FA_e->GetXaxis()->FindBin(theta), acc_FA_e->GetYaxis()->FindBin(mom));
  if (mom > 3.5 && (strcmp(detector, "LA") == 0 || strcmp(detector, "all") == 0))
    acc += acc_LA_e->GetBinContent(acc_LA_e->GetXaxis()->FindBin(theta), acc_LA_e->GetYaxis()->FindBin(mom));
  if (theta > thetamin && theta < 8.0 && mom > 2.0) return 0.5;
  return acc;
}

double GetAcceptance_pip(const TLorentzVector p){//Get pi+ acceptance
  if (!use_acc_cut) return 1.0;
  double theta = p.Theta() / M_PI * 180.0;
  if (theta < thetamin || theta > 18.0) return 0;
  if (!InPhiSector(p)) return 0;
  double mom = p.P();
  if (mom < pimin) return 0;
  double acc = 0;
  acc += acc_FA_pip->GetBinContent(acc_FA_pip->GetXaxis()->FindBin(theta), acc_FA_pip->GetYaxis()->FindBin(mom));
  if (theta > thetamin && theta < 8.0 && mom > 2.0) return 0.5;
  return acc;
}

double GetAcceptance_pim(const TLorentzVector p){//Get pi- acceptance
  if (!use_acc_cut) return 1.0;
  double theta = p.Theta() / M_PI * 180.0;
  if (theta < thetamin || theta > 18.0) return 0;
  if (!InPhiSector(p)) return 0;
  double mom = p.P();
  if (mom < pimin) return 0;
  double acc = 0;
  acc += acc_FA_pim->GetBinContent(acc_FA_pim->GetXaxis()->FindBin(theta), acc_FA_pim->GetYaxis()->FindBin(mom));
  if (theta > thetamin && theta < 8.0 && mom > 2.0) return 0.5;
  return acc;
}

double PKmax = 6.0;
double GetAcceptance_kp(const TLorentzVector p){//Get k+ acceptance
  if (!use_acc_cut) return 1.0;
  double theta = p.Theta() / M_PI * 180.0;
  if (theta < 8.0 || theta > 18.0) return 0;
  if (!InPhiSector(p)) return 0;
  double mom = p.P();
  if (mom > PKmax) return 0;
  double acc = 0;
  acc += acc_FA_kp->GetBinContent(acc_FA_kp->GetXaxis()->FindBin(theta), acc_FA_kp->GetYaxis()->FindBin(mom));
  return acc;
}

double GetAcceptance_km(const TLorentzVector p){//Get k- acceptance
  if (!use_acc_cut) return 1.0;
  double theta = p.Theta() / M_PI * 180.0;
  if (theta < 8.0 || theta > 18.0) return 0;
  if (!InPhiSector(p)) return 0;
  double mom = p.P();
  if (mom > PKmax) return 0;
  double acc = 0;
  acc += acc_FA_km->GetBinContent(acc_FA_km->GetXaxis()->FindBin(theta), acc_FA_km->GetYaxis()->FindBin(mom));
  return acc;
}

double GetAcceptance_hadron(const TLorentzVector p, const char * hadron){//Get hadron acceptance
  if (strcmp(hadron, "pi+") == 0) return GetAcceptance_pip(p);
  else if (strcmp(hadron, "pi-") == 0) return GetAcceptance_pim(p);
  else if (strcmp(hadron, "K+") == 0) return GetAcceptance_kp(p);
  else if (strcmp(hadron, "K-") == 0) return GetAcceptance_km(p);
  else return 0;
}

int GetTotalRate(const double Ebeam, const char * hadron){//Estimate the total rate
  Lsidis sidis;
  TLorentzVector l(0, 0, Ebeam, Ebeam);
  TLorentzVector P(0, 0, 0, 0.938272);
  sidis.SetNucleus(Np, Nn);
  sidis.SetHadron(hadron);
  if (strcmp(hadron, "pi+") == 0 || strcmp(hadron, "pi-") == 0) sidis.ChangeTMDpars(0.604, 0.114);
  if (strcmp(hadron, "K+") == 0 || strcmp(hadron, "K-") == 0) sidis.ChangeTMDpars(0.604, 0.131);
  sidis.SetInitialState(l, P);
  sidis.SetPDFset("CJ15lo");
  sidis.SetFFset("DSSFFlo");
  double lumi = 1.0e+10 * pow(0.197327, 2);
  double Xmin[6] = {0.0, 1.0, 0.3, 0.0, -M_PI, -M_PI};
  double Xmax[6] = {0.7, 10.0, 0.7, 1.8, M_PI, M_PI};
  sidis.SetRange(Xmin, Xmax);
  double sum = 0.0;
  Long64_t Nsim = 100000000;
  double weight = 0.0;
  TLorentzVector lp(0, 0, 0, 0);
  TLorentzVector Ph(0, 0, 0, 0);
  for (Long64_t i = 0; i < Nsim; i++){
    //if (i%(Nsim/5) == 0) std::cout << i << std::endl;
    if (sidis.GenerateEventKinematics(1)){//kinematics only; defer PDF/FF evaluation until after the (cheap) acceptance cut
      if (sidis.GetVariable("W") < 2.3) continue;
      if (sidis.GetVariable("Wp") < 1.6) continue;
      sidis.CalculateRfactor();
      if (sidis.GetVariable("Rfactor") > Rfactor0) continue;
      lp = sidis.GetLorentzVector("lp");
      Ph = sidis.GetLorentzVector("Ph");
      double acc = GetAcceptance_e(lp) * GetAcceptance_hadron(Ph, hadron);
      if (acc > 0){
        weight = sidis.GetWeightFromCurrentState(0);
        sum += weight * acc;
      }
    }
  }
  //printf("\n");
  printf("Total rate: %.4E  (%.1f GeV %s)\n\n", sum * lumi / Nsim, Ebeam, hadron);
  return 0;
}

int MakeKinematicCoveragePlots(const double Ebeam, const char * savefile, const char * hadron = "pi+"){
  Lsidis sidis;
  TLorentzVector l(0, 0, Ebeam, Ebeam);
  TLorentzVector P(0, 0, 0, 0.938272);
  sidis.SetNucleus(Np,Nn);
  sidis.SetHadron(hadron);
  if (strcmp(hadron, "pi+") == 0 || strcmp(hadron, "pi-") == 0) sidis.ChangeTMDpars(0.604, 0.114);
  if (strcmp(hadron, "K+") == 0 || strcmp(hadron, "K-") == 0) sidis.ChangeTMDpars(0.604, 0.131); 
  sidis.SetInitialState(l, P);
  sidis.SetPDFset("CJ15lo");
  sidis.SetFFset("DSSFFlo");
  double Xmin[6] = {0.0, 1.0, 0.3, 0.0, -M_PI, -M_PI};
  double Xmax[6] = {0.7, 9.0, 0.7, 2.0, M_PI, M_PI};
  sidis.SetRange(Xmin, Xmax);
  TFile * fs = new TFile(savefile, "RECREATE");
  gStyle->SetOptStat(0);
  //(x, Q2)
  TH2D * xQ2_FA = new TH2D("xQ2_FA", "", 700, 0.0, 0.7, 900, 0.0, 9.0);
  xQ2_FA->GetXaxis()->SetTitle("x");
  xQ2_FA->GetYaxis()->SetTitle("Q^{2} / GeV^{2}");
  TH2D * xQ2_LA = new TH2D("xQ2_LA", "", 700, 0.0, 0.7, 900, 0.0, 9.0);
  xQ2_LA->GetXaxis()->SetTitle("x");
  xQ2_LA->GetYaxis()->SetTitle("Q^{2} / GeV^{2}");
  //(x, W)
  TH2D * xW_FA = new TH2D("xW_FA", "", 700, 0.0, 0.7, 500, 2.0, 4.5);
  xW_FA->GetXaxis()->SetTitle("x");
  xW_FA->GetYaxis()->SetTitle("W / GeV");
  TH2D * xW_LA = new TH2D("xW_LA", "", 700, 0.0, 0.7, 500, 2.0, 4.5);
  xW_LA->GetXaxis()->SetTitle("x");
  xW_LA->GetYaxis()->SetTitle("W / GeV");
  //(x, Wp)
  TH2D * xWp_FA = new TH2D("xWp_FA", "", 700, 0.0, 0.7, 500, 1.5, 4.0);
  xWp_FA->GetXaxis()->SetTitle("x");
  xWp_FA->GetYaxis()->SetTitle("W' / GeV");
  TH2D * xWp_LA = new TH2D("xWp_LA", "", 700, 0.0, 0.7, 500, 1.5, 4.0);
  xWp_LA->GetXaxis()->SetTitle("x");
  xWp_LA->GetYaxis()->SetTitle("W' / GeV");
  //(x, z)
  TH2D * xz_FA = new TH2D("xz_FA", "", 700, 0.0, 0.7, 600, 0.2, 0.8);
  xz_FA->GetXaxis()->SetTitle("x");
  xz_FA->GetYaxis()->SetTitle("z");
  TH2D * xz_LA = new TH2D("xz_LA", "", 700, 0.0, 0.7, 600, 0.2, 0.8);
  xz_LA->GetXaxis()->SetTitle("x");
  xz_LA->GetYaxis()->SetTitle("z");
  //(x, Pt)
  TH2D * xPt_FA = new TH2D("xPt_FA", "", 700, 0.0, 0.7, 800, 0.0, 2.0);
  xPt_FA->GetXaxis()->SetTitle("x");
  xPt_FA->GetYaxis()->SetTitle("P_{T} / GeV");
  TH2D * xPt_LA = new TH2D("xPt_LA", "", 700, 0.0, 0.7, 800, 0.0, 2.0);
  xPt_LA->GetXaxis()->SetTitle("x");
  xPt_LA->GetYaxis()->SetTitle("P_{T} / GeV");
  //(z, Pt)
  TH2D * zPt_FA = new TH2D("zPt_FA", "", 600, 0.2, 0.8, 800, 0.0, 2.0);
  zPt_FA->GetXaxis()->SetTitle("z");
  zPt_FA->GetYaxis()->SetTitle("P_{T} / GeV");
  TH2D * zPt_LA = new TH2D("zPt_LA", "", 600, 0.2, 0.8, 800, 0.0, 2.0);
  zPt_LA->GetXaxis()->SetTitle("z");
  zPt_LA->GetYaxis()->SetTitle("P_{T} / GeV");
  //(z, Q2)
  TH2D * zQ2_FA = new TH2D("zQ2_FA", "", 600, 0.2, 0.8, 900, 0.0, 9.0);
  zQ2_FA->GetXaxis()->SetTitle("z");
  zQ2_FA->GetYaxis()->SetTitle("Q^{2} / GeV^{2}");
  TH2D * zQ2_LA = new TH2D("zQ2_LA", "", 600, 0.2, 0.8, 900, 0.0, 9.0);
  zQ2_LA->GetXaxis()->SetTitle("z");
  zQ2_LA->GetYaxis()->SetTitle("Q^{2} / GeV^{2}");
  //(z, W)
  TH2D * zW_FA = new TH2D("zW_FA", "", 600, 0.2, 0.8, 500, 2.0, 4.5);
  zW_FA->GetXaxis()->SetTitle("z");
  zW_FA->GetYaxis()->SetTitle("W / GeV");
  TH2D * zW_LA = new TH2D("zW_LA", "", 600, 0.2, 0.8, 500, 2.0, 4.5);
  zW_LA->GetXaxis()->SetTitle("z");
  zW_LA->GetYaxis()->SetTitle("W / GeV");
  //(z, Wp)
  TH2D * zWp_FA = new TH2D("zWp_FA", "", 600, 0.2, 0.8, 500, 1.5, 4.0);
  zWp_FA->GetXaxis()->SetTitle("z");
  zWp_FA->GetYaxis()->SetTitle("W' / GeV");
  TH2D * zWp_LA = new TH2D("zWp_LA", "", 600, 0.2, 0.8, 500, 1.5, 4.0);
  zWp_LA->GetXaxis()->SetTitle("z");
  zWp_LA->GetYaxis()->SetTitle("W' / GeV");
  //(Pt, Q2)
  TH2D * PtQ2_FA = new TH2D("PtQ2_FA", "", 800, 0.0, 2.0, 900, 0.0, 9.0);
  PtQ2_FA->GetXaxis()->SetTitle("P_{T} / GeV");
  PtQ2_FA->GetYaxis()->SetTitle("Q^{2} / GeV^{2}");
  TH2D * PtQ2_LA = new TH2D("PtQ2_LA", "", 800, 0.0, 2.0, 900, 0.0, 9.0);
  PtQ2_LA->GetXaxis()->SetTitle("P_{T} / GeV");
  PtQ2_LA->GetYaxis()->SetTitle("Q^{2} / GeV^{2}");
  //(Pt, W)
  TH2D * PtW_FA = new TH2D("PtW_FA", "", 800, 0.0, 2.0, 500, 2.0, 4.5);
  PtW_FA->GetXaxis()->SetTitle("P_{T} / GeV");
  PtW_FA->GetYaxis()->SetTitle("W / GeV");
  TH2D * PtW_LA = new TH2D("PtW_LA", "", 800, 0.0, 2.0, 500, 2.0, 4.5);
  PtW_LA->GetXaxis()->SetTitle("P_{T} / GeV");
  PtW_LA->GetYaxis()->SetTitle("W / GeV");
  //(Pt, Wp)
  TH2D * PtWp_FA = new TH2D("PtWp_FA", "", 800, 0.0, 2.0, 500, 1.5, 4.0);
  PtWp_FA->GetXaxis()->SetTitle("P_{T} / GeV");
  PtWp_FA->GetYaxis()->SetTitle("W' / GeV");
  TH2D * PtWp_LA = new TH2D("PtWp_LA", "", 800, 0.0, 2.0, 500, 1.5, 4.0);
  PtWp_LA->GetXaxis()->SetTitle("P_{T} / GeV");
  PtWp_LA->GetYaxis()->SetTitle("W' / GeV");
  //(W, Q2)
  TH2D * WQ2_FA = new TH2D("WQ2_FA", "", 500, 2.0, 4.5, 900, 0.0, 9.0);
  WQ2_FA->GetXaxis()->SetTitle("W / GeV");
  WQ2_FA->GetYaxis()->SetTitle("Q^{2} / GeV^{2}");
  TH2D * WQ2_LA = new TH2D("WQ2_LA", "", 500, 2.0, 4.5, 900, 0.0, 9.0);
  WQ2_LA->GetXaxis()->SetTitle("W / GeV");
  WQ2_LA->GetYaxis()->SetTitle("Q^{2} / GeV^{2}");
  //(Wp, Q2)
  TH2D * WpQ2_FA = new TH2D("WpQ2_FA", "", 500, 1.5, 4.0, 900, 0.0, 9.0);
  WpQ2_FA->GetXaxis()->SetTitle("W' / GeV");
  WpQ2_FA->GetYaxis()->SetTitle("Q^{2} / GeV^{2}");
  TH2D * WpQ2_LA = new TH2D("WpQ2_LA", "", 500, 1.5, 4.0, 900, 0.0, 9.0);
  WpQ2_LA->GetXaxis()->SetTitle("W' / GeV");
  WpQ2_LA->GetYaxis()->SetTitle("Q^{2} / GeV^{2}");
  double x, Q2, z, Pt, W, Wp;
  double weight, acc_FA, acc_LA;
  TLorentzVector lp, Ph;
  for (Long64_t i = 0; i < 100000000; i++){
    if (i % 1000000 == 0) std::cout << i << " %" << std::endl;
    if (sidis.GenerateEventKinematics(1)){//kinematics only; defer PDF/FF evaluation until after the (cheap) acceptance cut
      z = sidis.GetVariable("z");
      if (z < 0.3 || z > 0.7) continue;
      Q2 = sidis.GetVariable("Q2");
      if (Q2 < 1.0) continue;
      W = sidis.GetVariable("W");
      if (W < 2.3) continue;
      Wp = sidis.GetVariable("Wp");
      if (Wp < 1.6) continue;
      x = sidis.GetVariable("x");
      Pt = sidis.GetVariable("Pt");
      lp = sidis.GetLorentzVector("lp");
      Ph = sidis.GetLorentzVector("Ph");
      acc_FA = GetAcceptance_e(lp, "FA") * GetAcceptance_hadron(Ph, hadron);
      acc_LA = GetAcceptance_e(lp, "LA") * GetAcceptance_hadron(Ph, hadron);
      if (acc_FA > 0 || acc_LA > 0){
      weight = sidis.GetWeightFromCurrentState(0);
      if (weight > 0){
      if (acc_FA > 0){
	xQ2_FA->Fill(x, Q2, acc_FA);
	xW_FA->Fill(x, W, acc_FA);
	xz_FA->Fill(x, z, acc_FA);
	xPt_FA->Fill(x, Pt, acc_FA);
	xWp_FA->Fill(x, Wp, acc_FA);
	zPt_FA->Fill(z, Pt, acc_FA);
	zQ2_FA->Fill(z, Q2, acc_FA);
	zW_FA->Fill(z, W, acc_FA);
	zWp_FA->Fill(z, Wp, acc_FA);
	PtQ2_FA->Fill(Pt, Q2, acc_FA);
	PtW_FA->Fill(Pt, W, acc_FA);
	PtWp_FA->Fill(Pt, Wp, acc_FA);
	WQ2_FA->Fill(W, Q2, acc_FA);
	WpQ2_FA->Fill(Wp, Q2, acc_FA);
      }
      if (acc_LA > 0){
	xQ2_LA->Fill(x, Q2, acc_LA);
	xW_LA->Fill(x, W, acc_LA);
	xz_LA->Fill(x, z, acc_LA);
	xPt_LA->Fill(x, Pt, acc_LA);
	xWp_LA->Fill(x, Wp, acc_LA);
	zPt_LA->Fill(z, Pt, acc_LA);
	zQ2_LA->Fill(z, Q2, acc_LA);
	zW_LA->Fill(z, W, acc_LA);
	zWp_LA->Fill(z, Wp, acc_LA);
	PtQ2_LA->Fill(Pt, Q2, acc_LA);
	PtW_LA->Fill(Pt, W, acc_LA);
	PtWp_LA->Fill(Pt, Wp, acc_LA);
	WQ2_LA->Fill(W, Q2, acc_LA);
	WpQ2_LA->Fill(Wp, Q2, acc_LA);
      }
      }
      }
    }
  }
  xQ2_FA->Divide(xQ2_FA); xQ2_FA->Scale(100);
  xQ2_LA->Divide(xQ2_LA); xQ2_LA->Scale(100);
  xW_FA->Divide(xW_FA); xW_FA->Scale(100);
  xW_LA->Divide(xW_LA); xW_LA->Scale(100);
  xz_FA->Divide(xz_FA); xz_FA->Scale(100);
  xz_LA->Divide(xz_LA); xz_LA->Scale(100);
  xPt_FA->Divide(xPt_FA); xPt_FA->Scale(100);
  xPt_LA->Divide(xPt_LA); xPt_LA->Scale(100);
  xWp_FA->Divide(xWp_FA); xWp_FA->Scale(100);
  xWp_LA->Divide(xWp_LA); xWp_LA->Scale(100);
  zW_FA->Divide(zW_FA); zW_FA->Scale(100);
  zW_LA->Divide(zW_LA); zW_LA->Scale(100);
  zQ2_FA->Divide(zQ2_FA); zQ2_FA->Scale(100);
  zQ2_LA->Divide(zQ2_LA); zQ2_LA->Scale(100);
  zWp_FA->Divide(zWp_FA); zWp_FA->Scale(100);
  zWp_LA->Divide(zWp_LA); zWp_LA->Scale(100);
  zPt_FA->Divide(zPt_FA); zPt_FA->Scale(100);
  zPt_LA->Divide(zPt_LA); zPt_LA->Scale(100);
  PtQ2_FA->Divide(PtQ2_FA); PtQ2_FA->Scale(100);
  PtQ2_LA->Divide(PtQ2_LA); PtQ2_LA->Scale(100);
  WQ2_FA->Divide(WQ2_FA); WQ2_FA->Scale(100);
  WQ2_LA->Divide(WQ2_LA); WQ2_LA->Scale(100);
  PtW_FA->Divide(PtW_FA); PtW_FA->Scale(100);
  PtW_LA->Divide(PtW_LA); PtW_LA->Scale(100);
  PtWp_FA->Divide(PtWp_FA); PtWp_FA->Scale(100);
  PtWp_LA->Divide(PtWp_LA); PtWp_LA->Scale(100);
  WpQ2_FA->Divide(WpQ2_FA); WpQ2_FA->Scale(100);
  WpQ2_LA->Divide(WpQ2_LA); WpQ2_LA->Scale(100);
  fs->Write();
  return 0;
}

int MakeRateDistributionPlots(const double Ebeam, const char * savefile, const char * hadron = "pi+"){
  double lumi = 1.0e+10 * pow(0.197327, 2);
  Lsidis sidis;
  TLorentzVector l(0, 0, Ebeam, Ebeam);
  TLorentzVector P(0, 0, 0, 0.938272);
  sidis.SetNucleus(Np,Nn);
  sidis.SetHadron(hadron);
  if (strcmp(hadron, "pi+") == 0 || strcmp(hadron, "pi-") == 0) sidis.ChangeTMDpars(0.604, 0.114);
  if (strcmp(hadron, "K+") == 0 || strcmp(hadron, "K-") == 0) sidis.ChangeTMDpars(0.604, 0.131);
  sidis.SetInitialState(l, P);
  sidis.SetPDFset("CJ15lo");
  sidis.SetFFset("DSSFFlo");
  double Xmin[6] = {0.0, 1.0, 0.3, 0.0, -M_PI, -M_PI};
  double Xmax[6] = {0.7, 10.0, 0.7, 2.0, M_PI, M_PI};
  sidis.SetRange(Xmin, Xmax);
  TFile * fs = new TFile(savefile, "RECREATE");
  gStyle->SetOptStat(0);
  //(x, Q2)
  TH2D * xQ2 = new TH2D("xQ2", "", 700, 0.0, 0.7, 900, 0.0, 9.0);
  xQ2->GetXaxis()->SetTitle("x");
  xQ2->GetYaxis()->SetTitle("Q^{2} / GeV^{2}");
  //(x, W)
  TH2D * xW = new TH2D("xW", "", 700, 0.0, 0.7, 500, 2.0, 4.5);
  xW->GetXaxis()->SetTitle("x");
  xW->GetYaxis()->SetTitle("W / GeV");
  //(x, Wp)
  TH2D * xWp = new TH2D("xWp", "", 700, 0.0, 0.7, 500, 1.5, 4.0);
  xWp->GetXaxis()->SetTitle("x");
  xWp->GetYaxis()->SetTitle("W' / GeV");
  //(x, z)
  TH2D * xz = new TH2D("xz", "", 700, 0.0, 0.7, 600, 0.2, 0.8);
  xz->GetXaxis()->SetTitle("x");
  xz->GetYaxis()->SetTitle("z");
  //(x, Pt)
  TH2D * xPt = new TH2D("xPt", "", 700, 0.0, 0.7, 800, 0.0, 2.0);
  xPt->GetXaxis()->SetTitle("x");
  xPt->GetYaxis()->SetTitle("P_{T} / GeV");
  //(z, Pt)
  TH2D * zPt = new TH2D("zPt", "", 600, 0.2, 0.8, 800, 0.0, 2.0);
  zPt->GetXaxis()->SetTitle("z");
  zPt->GetYaxis()->SetTitle("P_{T} / GeV");
  //(z, Q2)
  TH2D * zQ2 = new TH2D("zQ2", "", 600, 0.2, 0.8, 900, 0.0, 9.0);
  zQ2->GetXaxis()->SetTitle("z");
  zQ2->GetYaxis()->SetTitle("Q^{2} / GeV^{2}");
  //(z, W)
  TH2D * zW = new TH2D("zW", "", 600, 0.2, 0.8, 500, 2.0, 4.5);
  zW->GetXaxis()->SetTitle("z");
  zW->GetYaxis()->SetTitle("W / GeV");
  //(z, Wp)
  TH2D * zWp = new TH2D("zWp", "", 600, 0.2, 0.8, 500, 1.5, 4.0);
  zWp->GetXaxis()->SetTitle("z");
  zWp->GetYaxis()->SetTitle("W' / GeV");
  //(Pt, Q2)
  TH2D * PtQ2 = new TH2D("PtQ2", "", 800, 0.0, 2.0, 900, 0.0, 9.0);
  PtQ2->GetXaxis()->SetTitle("P_{T} / GeV");
  PtQ2->GetYaxis()->SetTitle("Q^{2} / GeV^{2}");
  //(Pt, W)
  TH2D * PtW = new TH2D("PtW", "", 800, 0.0, 2.0, 500, 2.0, 4.5);
  PtW->GetXaxis()->SetTitle("P_{T} / GeV");
  PtW->GetYaxis()->SetTitle("W / GeV");
  //(Pt, Wp)
  TH2D * PtWp = new TH2D("PtWp", "", 800, 0.0, 2.0, 500, 1.5, 4.0);
  PtWp->GetXaxis()->SetTitle("P_{T} / GeV");
  PtWp->GetYaxis()->SetTitle("W' / GeV");
  //(W, Q2)
  TH2D * WQ2 = new TH2D("WQ2", "", 500, 2.0, 4.5, 900, 0.0, 9.0);
  WQ2->GetXaxis()->SetTitle("W / GeV");
  WQ2->GetYaxis()->SetTitle("Q^{2} / GeV^{2}");
  //(Wp, Q2)
  TH2D * WpQ2 = new TH2D("WpQ2", "", 500, 1.5, 4.0, 900, 0.0, 9.0);
  WpQ2->GetXaxis()->SetTitle("W' / GeV");
  WpQ2->GetYaxis()->SetTitle("Q^{2} / GeV^{2}");
  double x, Q2, z, Pt, W, Wp;
  double weight, acc;
  TLorentzVector lp, Ph;
  Long64_t Nsim = 100000000;
  for (Long64_t i = 0; i < Nsim; i++){
    if (i % 10000000 == 0) std::cout << i << " %" << std::endl;
    if (sidis.GenerateEventKinematics(1)){//kinematics only; defer PDF/FF evaluation until after the (cheap) acceptance cut
      z = sidis.GetVariable("z");
      if (z < 0.3 || z > 0.7) continue;
      Q2 = sidis.GetVariable("Q2");
      if (Q2 < 1.0) continue;
      W = sidis.GetVariable("W");
      if (W < 2.3) continue;
      Wp = sidis.GetVariable("Wp");
      if (Wp < 1.6) continue;
      x = sidis.GetVariable("x");
      Pt = sidis.GetVariable("Pt");
      lp = sidis.GetLorentzVector("lp");
      Ph = sidis.GetLorentzVector("Ph");
      acc = GetAcceptance_e(lp, "all") * GetAcceptance_hadron(Ph, hadron);
      if (acc > 0){
	sidis.CalculateRfactor();
	if (sidis.GetVariable("Rfactor") > Rfactor0) continue;
	weight = sidis.GetWeightFromCurrentState(0);
	if (weight > 0){
	xQ2->Fill(x, Q2, weight * acc);
	xW->Fill(x, W, weight * acc);
	xz->Fill(x, z, weight * acc);
	xPt->Fill(x, Pt, weight * acc);
	xWp->Fill(x, Wp, weight * acc);
	zPt->Fill(z, Pt, weight * acc);
	zQ2->Fill(z, Q2, weight * acc);
	zW->Fill(z, W, weight * acc);
	zWp->Fill(z, Wp, weight * acc);
	PtQ2->Fill(Pt, Q2, weight * acc);
	PtW->Fill(Pt, W, weight * acc);
	PtWp->Fill(Pt, Wp, weight * acc);
	WQ2->Fill(W, Q2, weight * acc);
	WpQ2->Fill(Wp, Q2, weight * acc);
	}
      }
    }
  }
  xQ2->Scale(lumi/Nsim);
  xW->Scale(lumi/Nsim);
  xz->Scale(lumi/Nsim);
  xPt->Scale(lumi/Nsim);
  xWp->Scale(lumi/Nsim);
  zW->Scale(lumi/Nsim);
  zQ2->Scale(lumi/Nsim);
  zWp->Scale(lumi/Nsim);
  zPt->Scale(lumi/Nsim);
  PtQ2->Scale(lumi/Nsim);
  WQ2->Scale(lumi/Nsim);
  PtW->Scale(lumi/Nsim);
  PtWp->Scale(lumi/Nsim);
  WpQ2->Scale(lumi/Nsim);
  fs->Write();
  return 0;
}

int MakeRateDistributionPlotZ(const double Ebeam, const char * hadron = "pi+"){//Make z-? plot
  double lumi = 1.0e+10 * pow(0.197327, 2);
  Lsidis sidis;
  TLorentzVector l(0, 0, Ebeam, Ebeam);
  TLorentzVector P(0, 0, 0, 0.938272);
  sidis.SetNucleus(Np,Nn);
  sidis.SetHadron(hadron);
  if (strcmp(hadron, "pi+") == 0 || strcmp(hadron, "pi-") == 0) sidis.ChangeTMDpars(0.604, 0.114);
  if (strcmp(hadron, "K+") == 0 || strcmp(hadron, "K-") == 0) sidis.ChangeTMDpars(0.604, 0.131);
  sidis.SetInitialState(l, P);
  sidis.SetPDFset("CJ15lo");
  sidis.SetFFset("DSSFFlo");
  double Xmin[6] = {0.0, 1.0, 0.01, 0.0, -M_PI, -M_PI};
  double Xmax[6] = {0.7, 10.0, 0.99, 2.0, M_PI, M_PI};
  sidis.SetRange(Xmin, Xmax);
  gStyle->SetOptStat(0);
  //(Ph, z)
  TH2D * Phz = new TH2D("Phz", "", 500, 0.0, 10.0, 500, 0.0, 1.0);
  Phz->GetXaxis()->SetTitle("P_{h} / GeV");
  Phz->GetXaxis()->SetTitleSize(0.05);
  Phz->GetXaxis()->CenterTitle(true);
  Phz->GetXaxis()->SetLabelSize(0.05);
  Phz->GetYaxis()->SetTitle("z");
  Phz->GetYaxis()->SetTitleSize(0.05);
  Phz->GetYaxis()->CenterTitle(true);
  Phz->GetYaxis()->SetLabelSize(0.05);
  double x, Q2, z, Pt, W, Wp;
  double weight, acc;
  TLorentzVector lp, Ph;
  Long64_t Nsim = 100000000;
  for (Long64_t i = 0; i < Nsim; i++){
    if (i % 10000000 == 0) std::cout << i * 100 / Nsim << " %" << std::endl;
    if (sidis.GenerateEventKinematics(1)){//kinematics only; defer PDF/FF evaluation until after the (cheap) acceptance cut
      z = sidis.GetVariable("z");
      //if (z < 0.3 || z > 0.7) continue;
      Q2 = sidis.GetVariable("Q2");
      if (Q2 < 1.0) continue;
      W = sidis.GetVariable("W");
      if (W < 2.3) continue;
      Wp = sidis.GetVariable("Wp");
      if (Wp < 1.6) continue;
      x = sidis.GetVariable("x");
      Pt = sidis.GetVariable("Pt");
      lp = sidis.GetLorentzVector("lp");
      Ph = sidis.GetLorentzVector("Ph");
      acc = GetAcceptance_e(lp, "all") * GetAcceptance_hadron(Ph, hadron);
      if (acc > 0){
	//sidis.CalculateRfactor();
	//if (sidis.GetVariable("Rfactor") > Rfactor0) continue;
	weight = sidis.GetWeightFromCurrentState(0);
	if (weight > 0)
	  Phz->Fill(Ph.P(), z, weight * acc);
      }
    }
  }
  Phz->Scale(lumi/Nsim);
  TCanvas * c0 = new TCanvas("c0", "", 800, 600);
  c0->SetLogz();
  Phz->DrawClone("colz");
  c0->Print("Phz.pdf");
  return 0;
}

int GenerateBinInfoFile(const char * filename, const double Ebeam, const char * hadron){//Bin the data and create the bin info file
  FILE * fp = fopen(filename, "w");
  fprintf(fp, "Q2l\t Q2u\t zl\t zu\t Ptl\t Ptu\t xl\t xu\n");
  Lsidis sidis;
  TLorentzVector l(0, 0, Ebeam, Ebeam);
  TLorentzVector P(0, 0, 0, 0.938272);
  sidis.SetNucleus(Np,Nn);
  sidis.SetHadron(hadron);
  if (strcmp(hadron, "pi+") == 0 || strcmp(hadron, "pi-") == 0) sidis.ChangeTMDpars(0.604, 0.114);
  if (strcmp(hadron, "K+") == 0 || strcmp(hadron, "K-") == 0) sidis.ChangeTMDpars(0.604, 0.131);
  sidis.SetInitialState(l, P);
  sidis.SetPDFset("CJ15lo");
  sidis.SetFFset("DSSFFlo");
  double lumi = 1.0e+10 * pow(0.197327, 2);
  double eff = 0.85;
  double time = 48.0 * 24.0 * 3600.0;
  if (Ebeam < 10.0) time = 21.0 * 24.0 * 3600.0;
  double Nsim = 1.0e6;
  double Xmin[6] = {0.0, 0.0, 0.0, 0.0, -M_PI, -M_PI}; 
  double Xmax[6] = {0.7, 0.0, 0.0, 0.0, M_PI, M_PI};;//x, Q2, z, Pt, phih, phiS
  double weight = 0;
  double acc = 0;
  int Nx = 0;
  TLorentzVector lp(0, 0, 0, 0);
  TLorentzVector Ph(0, 0, 0, 0);
  double Q2list[7] = {1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0};
  double statlist[6] = {1.9e7, 1.1e7, 5.0e6, 3.0e6, 2.0e6, 2.0e6};
  double zlist[9] = {0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7};
  double Ptlist[7] = {0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.6};
  int xi = 1;
  for (int Qi = 0; Qi < 6; Qi++){//Q2 loop
    Xmin[1] = Q2list[Qi];
    Xmax[1] = Q2list[Qi+1];
    for (int zi = 0; zi < 8; zi++){//z loop
      Xmin[2] = zlist[zi];
      Xmax[2] = zlist[zi+1];
      Xmin[3] = Ptlist[0];
      for (int kj = 1; kj < 7;){//Pt loop
	Xmax[3] = Ptlist[kj];
	sidis.SetRange(Xmin, Xmax);
	TH1D * hx = new TH1D("hx", "hx", 7000, 0.0, 0.7);
	printf("Q2:%.1f-%.1f  z:%.2f-%.2f  Pt:%.1f-%.1f\n",
	       Xmin[1], Xmax[1], Xmin[2], Xmax[2], Xmin[3], Xmax[3]);
	for (Long64_t i = 0; i < Nsim; i++){//generate events
	  if (sidis.GenerateEventKinematics(1)){//kinematics only; defer PDF/FF evaluation until after the (cheap) acceptance cut
            if (sidis.GetVariable("W") < 2.3) continue;
            if (sidis.GetVariable("Wp") < 1.6) continue;
	    sidis.CalculateRfactor();
	    if (sidis.GetVariable("Rfactor") > Rfactor0) continue;
	    lp = sidis.GetLorentzVector("lp");
	    Ph = sidis.GetLorentzVector("Ph");
	    acc = GetAcceptance_e(lp) * GetAcceptance_hadron(Ph, hadron);
	    if (acc > 0){
	      weight = sidis.GetWeightFromCurrentState(0);
	      if (weight > 0)
		hx->Fill(sidis.GetVariable("x"), weight * acc);
	    }
	  }
	}
	hx->Scale(lumi * time * eff / Nsim);
	if ((hx->Integral(1, -1) < statlist[Qi] && kj < 6) || (hx->Integral(1, -1) < 0.25 * statlist[Qi] && kj == 6)){
	  hx->Delete();
	  kj++;
	  continue;
	}
	Nx = 0;
	xi = 1;
	for (int xj = 1; xj <= 7000; xj++){
	  if (hx->Integral(xi, xj) > statlist[Qi] || xj == 7000){
	    fprintf(fp, "%.1f\t %.1f\t %.2f\t %.2f\t %.1f\t %.1f\t %.4f\t %.4f\n",
		    Xmin[1], Xmax[1], Xmin[2], Xmax[2], Xmin[3], Xmax[3],
		    hx->GetBinLowEdge(xi), hx->GetBinLowEdge(xj+1));
	    Nx++;
	    xi = xj + 1;
	  }
	}
	std::cout << Nx << std::endl;
	hx->Delete();
	Xmin[3] = Ptlist[kj];
	kj++;
      }
    }
  }
  fclose(fp);
  return 0;
}

int AnalyzeEstatUT3(const char * readfile, const char * savefile, const double Ebeam, const char * had){//bin analysis including stat. errors
  double Hadron = 0;
  if (strcmp(had, "pi+") == 0) Hadron = 0;
  else if (strcmp(had, "pi-") == 0) Hadron = 1;
  double Nucleon = 0;
  TFile * fs = new TFile(savefile, "RECREATE");
  TTree * Ts = new TTree("data", "data");
  Ts->SetDirectory(fs);
  double Eb = Ebeam;
  double x, y, z, Q2, Pt, phih, phiS;
  double dx, dy, dz, dQ2, dPt, dphih, dphiS, dv;
  double Nacc, fn;
  double Estatraw[3], Estat[3];
  //Two alternative propagations of the same moment matrix, carried alongside the
  //production Estatraw so they can be compared bin by bin without disturbing it.
  //  _diag : the least-squares error, md Section 4 / bug.md item 10
  //  _prop : the construction of Appendix II of PR-10-006, md Section 3
  //Analytically these two are the same quantity (see the block where they are
  //filled); they are computed by independent routes precisely so that agreement
  //is evidence and disagreement is a bug. Full derivation and the numerical test
  //in SIDIS_MUT3_comparison/SIDIS_MUT3_comparison_base.md.
  double Estatraw_diag[3], Estatraw_prop[3];
  double Estat_diag[3], Estat_prop[3];
  Ts->Branch("Nucleon", &Nucleon, "Nucleon/D");
  Ts->Branch("Hadron", &Hadron, "Hadron/D");
  Ts->Branch("Ebeam", &Eb, "Ebeam/D");
  Ts->Branch("x", &x, "x/D");
  Ts->Branch("y", &y, "y/D");
  Ts->Branch("z", &z, "z/D");
  Ts->Branch("Q2", &Q2, "Q2/D");
  Ts->Branch("Pt", &Pt, "Pt/D");
  Ts->Branch("dx", &dx, "dx/D");
  Ts->Branch("dy", &dy, "dy/D");
  Ts->Branch("dz", &dz, "dz/D");
  Ts->Branch("dQ2", &dQ2, "dQ2/D");
  Ts->Branch("dPt", &dPt, "dPt/D");
  Ts->Branch("dphih", &dphih, "dphih/D");
  Ts->Branch("dphiS", &dphiS, "dphiS/D");
  Ts->Branch("dv", &dv, "dv/D");
  Ts->Branch("Nacc", &Nacc, "Nacc/D");
  Ts->Branch("fn", &fn, "fn/D");
  Ts->Branch("E0statraw", &Estatraw[0], "E0statraw/D");
  Ts->Branch("E1statraw", &Estatraw[1], "E1statraw/D");
  Ts->Branch("E2statraw", &Estatraw[2], "E2statraw/D");
  Ts->Branch("E0stat", &Estat[0], "E0stat/D");
  Ts->Branch("E1stat", &Estat[1], "E1stat/D");
  Ts->Branch("E2stat", &Estat[2], "E2stat/D");
  Ts->Branch("E0statraw_diag", &Estatraw_diag[0], "E0statraw_diag/D");
  Ts->Branch("E1statraw_diag", &Estatraw_diag[1], "E1statraw_diag/D");
  Ts->Branch("E2statraw_diag", &Estatraw_diag[2], "E2statraw_diag/D");
  Ts->Branch("E0statraw_prop", &Estatraw_prop[0], "E0statraw_prop/D");
  Ts->Branch("E1statraw_prop", &Estatraw_prop[1], "E1statraw_prop/D");
  Ts->Branch("E2statraw_prop", &Estatraw_prop[2], "E2statraw_prop/D");
  Ts->Branch("E0stat_diag", &Estat_diag[0], "E0stat_diag/D");
  Ts->Branch("E1stat_diag", &Estat_diag[1], "E1stat_diag/D");
  Ts->Branch("E2stat_diag", &Estat_diag[2], "E2stat_diag/D");
  Ts->Branch("E0stat_prop", &Estat_prop[0], "E0stat_prop/D");
  Ts->Branch("E1stat_prop", &Estat_prop[1], "E1stat_prop/D");
  Ts->Branch("E2stat_prop", &Estat_prop[2], "E2stat_prop/D");
  //Keep every bin's azimuthal maps. MUT3 below collapses hs into three numbers
  //and both histograms are then deleted, so without this the distributions
  //cannot be re-examined short of re-running the whole step. hs_full is not used
  //by MUT3 at all -- it exists only to be looked at here.
  //Separate file so the tree file's format is unchanged: one <savefile>_hs.root
  //per forked group, since the four children cannot share a TFile.
  std::string hsfilename(savefile);
  const size_t hsdot = hsfilename.rfind(".root");
  if (hsdot == std::string::npos) hsfilename += "_hs.root";
  else hsfilename.replace(hsdot, 5, "_hs.root");
  TFile * fhs = new TFile(hsfilename.c_str(), "RECREATE");
  if (fhs->IsZombie()){
    std::cout << "error: cannot open " << hsfilename << " for the azimuthal maps" << std::endl;
    return 1;
  }
  fs->cd();//keep Ts and the per-bin histograms in the tree file, as before
  Lsidis sidis;
  TLorentzVector l(0, 0, Ebeam, Ebeam);
  TLorentzVector P(0, 0, 0, 0.938272);
  sidis.SetNucleus(Np,Nn);
  sidis.SetHadron(had);
  if (strcmp(had, "pi+") == 0 || strcmp(had, "pi-") == 0) sidis.ChangeTMDpars(0.604, 0.114);
  if (strcmp(had, "K+") == 0 || strcmp(had, "K-") == 0) sidis.ChangeTMDpars(0.604, 0.131);
  sidis.SetInitialState(l, P);
  sidis.SetPDFset("CJ15lo");
  sidis.SetFFset("DSSFFlo");
  double lumi = 1.0e+10 * pow(0.197327, 2);
  double eff = 0.85;
  double time = 48.0 * 24.0 * 3600.0;
  if (Ebeam < 10.0) time = 21.0 * 24.0 * 3600.0;
  Long64_t Nsim = 0;
  Long64_t Nrec = 0;
  double Xmin[6] = {0.0, 0.0, 0.0, 0.0, -M_PI, -M_PI}; 
  double Xmax[6] = {0.7, 0.0, 0.0, 0.0, M_PI, M_PI};;//x, Q2, z, Pt, phih, phiS
  double weight = 0;
  double weight_n = 0;
  double acc = 0;
  TLorentzVector lp(0, 0, 0, 0);
  TLorentzVector Ph(0, 0, 0, 0);
  Lsidis sidis_n;
  sidis_n.SetNucleus(0, 1);
  sidis_n.SetHadron(had);
  if (strcmp(had, "pi+") == 0 || strcmp(had, "pi-") == 0) sidis_n.ChangeTMDpars(0.604, 0.114);
  if (strcmp(had, "K+") == 0 || strcmp(had, "K-") == 0) sidis_n.ChangeTMDpars(0.604, 0.131);
  sidis_n.SetInitialState(l, P);
  sidis_n.SetPDFset("CJ15lo");
  sidis_n.SetFFset("DSSFFlo");
  std::ifstream infile(readfile);
  char tmp[300];
  infile.getline(tmp, 256);
  int Nt = 0;
  while (infile >> Xmin[1] >> Xmax[1] >> Xmin[2] >> Xmax[2] >> Xmin[3] >> Xmax[3] >> Xmin[0] >> Xmax[0]){
    printf("%.4d  Q2[%.1f,%.1f]  z[%.2f,%.2f]  Pt[%.1f,%.1f]  x[%.4f,%.4f]\n",
	   Nt++, Xmin[1], Xmax[1], Xmin[2], Xmax[2], Xmin[3], Xmax[3], Xmin[0], Xmax[0]);
    sidis.SetRange(Xmin, Xmax);
    sidis_n.SetRange(Xmin, Xmax);
    TH1D * hvar = new TH1D("hvar", "hvar", 7, -0.5, 6.5);
    //Azimuthal bin width, in one place. NPHI is the number of bins across a full
    //2pi; both maps use the same width in phi_h and in phi_S, so hs -- whose y
    //axis is the half range [0,pi] -- gets NPHI/2. 360 => 1 deg (was 36 => 10 deg
    //before 2026-08-27). The MUT3 loops below read GetNbinsX/Y, so this constant
    //is the only edit needed to change it.
    //Cost scales as NPHI^2: cells per bin are NPHI*NPHI*3/2, so 1 deg is 100x the
    //10 deg maps. Measured on disk that is ~1.4 MB per bin against ~26 KB, i.e.
    //54x after ROOT compresses the mostly-empty cells -- roughly 2.3 GB for a
    //1660-bin run and 29 GB for data_4pi's 20614 bins. Accuracy bought: 4.5e-3
    //max change in Estat going 10 deg -> 1 deg, since the matrix sums the same
    //events either way and only the discretisation of f across a cell improves.
    const int NPHI = 360;
    TH2D * hs_full = new TH2D("hs_full", "hs_full", NPHI, -M_PI, M_PI, NPHI, -M_PI, M_PI);
    TH2D * hs = new TH2D("hs", "hs", NPHI, -M_PI, M_PI, NPHI / 2, 0, M_PI);
    Nsim = 0;
    Nrec = 0;
    for (Long64_t i = 0; i < 1.0e7; i++){
      Nsim++;
      if (sidis.GenerateEventKinematics(1)){//kinematics only; defer PDF/FF evaluation until after the (cheap) acceptance cut
        if (sidis.GetVariable("W") < 2.3) continue;
        if (sidis.GetVariable("Wp") < 1.6) continue;
	sidis.CalculateRfactor();
	if (sidis.GetVariable("Rfactor") > Rfactor0) continue;
	lp = sidis.GetLorentzVector("lp");
	Ph = sidis.GetLorentzVector("Ph");
	acc = GetAcceptance_e(lp) * GetAcceptance_hadron(Ph, had);
	if (acc > 0){
	  weight = sidis.GetWeightFromCurrentState(0);
	  if (weight > 0){
	    sidis_n.SetFinalState(lp, Ph);
	    sidis_n.CalculateVariables();
	    weight_n = sidis_n.GetEventWeight(0, 1);
	    Nrec++;
	    hvar->Fill(0., weight_n * acc);
	    hvar->Fill(1., weight * acc);
	    hvar->Fill(2., weight * acc * sidis.GetVariable("x"));
	    hvar->Fill(3., weight * acc * sidis.GetVariable("y"));
	    hvar->Fill(4., weight * acc * sidis.GetVariable("z"));
	    hvar->Fill(5., weight * acc * sidis.GetVariable("Q2"));
	    hvar->Fill(6., weight * acc * sidis.GetVariable("Pt"));
	    hs_full->Fill(sidis.GetVariable("phih"), sidis.GetVariable("phiS"), weight * acc);
	    hs->Fill(sidis.GetVariable("phih"), std::abs(sidis.GetVariable("phiS")), weight * acc);
	  }
	}
      }
      if (Nrec > 100000) break;
    }
    hvar->Scale(lumi * time * eff / Nsim);
    hs_full->Scale(lumi * time * eff / Nsim);
    hs->Scale(lumi * time * eff / Nsim);
    Nacc = hvar->GetBinContent(2);
    fn = hvar->GetBinContent(1) / Nacc;
    x = hvar->GetBinContent(3) / Nacc;
    y = hvar->GetBinContent(4) / Nacc;
    z = hvar->GetBinContent(5) / Nacc;
    Q2 = hvar->GetBinContent(6) / Nacc;
    Pt = hvar->GetBinContent(7) / Nacc;
    //obtain the matrix for azimuthal modulations deposition.
    //
    //Notation follows SIDIS_MUT3_comparison/SIDIS_MUT3_comparison_base.md, which
    //derives the correspondence between this code and Appendix II of PR-10-006.
    //With phi = phih - phiS the three physical modulations are
    //    f = (sin(phi), sin(2 phih - phi), sin(2 phih + phi))
    //      = (sin(phih-phiS), sin(phih+phiS), sin(3 phih - phiS)),
    //whose amplitudes are (a,b,c) = (Sivers, Collins, Pretzelosity) -- i.e.
    //(E0,E1,E2) here. That ordering is proposal Eq. 7; the prose right after it
    //swaps the Sivers and Collins labels, and the equation is what is correct.
    //The loop below builds md Section 2's weighted Gram (normal) matrix
    //    G = MUT3 = Omega * sum_k p_k f_k f_k^T,   p_k = h_k / Nacc,
    //Omega being the angular area of the histogram it is summed over.
    //
    //hmat/nxbin/nybin/OM select between the unfolded hs_full (DEFAULT,
    //Omega = 4pi^2) and the folded hs (phisfold=fold, Omega = 2pi^2). The bin
    //counts come from the histogram rather than being hardcoded, so NPHI above is
    //the only place the azimuthal binning is set. See use_unfolded_phiS at the top
    //of this file; note md Section 2 is written for the folded form.
    TH2D * const hmat   = use_unfolded_phiS ? hs_full : hs;
    const int    nxbin  = hmat->GetNbinsX();
    const int    nybin  = hmat->GetNbinsY();
    const double OM     = use_unfolded_phiS ? 4.0 * M_PI * M_PI : 2.0 * M_PI * M_PI;
    TMatrixD MUT3(3,3);
    for (int i = 0; i < 3; i++)
      for (int j = 0; j < 3; j++)
	MUT3(i,j) = 0.0;
    for (int i = 1; i <= nxbin; i++){
      for (int j = 1; j <= nybin; j++){
	phih = hmat->GetXaxis()->GetBinCenter(i);
	phiS = hmat->GetYaxis()->GetBinCenter(j);
	MUT3(0,0) += sin(phih - phiS) * sin(phih - phiS) * hmat->GetBinContent(i,j) / Nacc * OM;
	MUT3(0,1) += sin(phih - phiS) * sin(phih + phiS) * hmat->GetBinContent(i,j) / Nacc * OM;
	MUT3(0,2) += sin(phih - phiS) * sin(3.0 * phih - phiS) * hmat->GetBinContent(i,j) / Nacc * OM;
	MUT3(1,0) += sin(phih + phiS) * sin(phih - phiS) * hmat->GetBinContent(i,j) / Nacc * OM;
	MUT3(1,1) += sin(phih + phiS) * sin(phih + phiS) * hmat->GetBinContent(i,j) / Nacc * OM;
	MUT3(1,2) += sin(phih + phiS) * sin(3.0 * phih - phiS) * hmat->GetBinContent(i,j) / Nacc * OM;
	MUT3(2,0) += sin(3.0 * phih - phiS) * sin(phih - phiS) * hmat->GetBinContent(i,j) / Nacc * OM;
	MUT3(2,1) += sin(3.0 * phih - phiS) * sin(phih + phiS) * hmat->GetBinContent(i,j) / Nacc * OM;
	MUT3(2,2) += sin(3.0 * phih - phiS) * sin(3.0 * phih - phiS) * hmat->GetBinContent(i,j) / Nacc * OM;
      }
    }
    MUT3.Invert();
    for (int i = 0; i < 3; i++){
      //The row norm is the only Omega-sensitive estimator: it squares the inverse,
      //so the prefactor scales as Omega^2 while _diag and _prop below have Omega
      //cancel. The original code hardcoded 2pi^2 * pi^2, which is Omega^2/2 at the
      //folded Omega = 2pi^2 and only there -- left as-is under the unfolded
      //Omega = 4pi^2 it would come out low by a factor 2. Omega^2/2 covers both.
      //Not bit-for-bit against pre-2026-08-27 output: hoisting 2.0*M_PI*M_PI into
      //OM reassociates a multiplication, moving every Estat* by ~3e-16 (~1.5 ulp).
      const double rownorm = pow(MUT3(i,0),2) + pow(MUT3(i,1), 2) + pow(MUT3(i,2), 2);
      Estatraw[i] = sqrt(OM * OM / (2.0 * Nacc) * rownorm);
      //Estatraw_diag: md Section 4's boxed result. The covariance implied by the
      //least-chi^2 normal equations is Cov = (Omega/Nacc) G^-1, so the marginal
      //error on amplitude i is the i-th DIAGONAL element of the inverted matrix,
      //not the norm of its i-th row (md Section 5; bug.md item 10). The two agree
      //only where G is diagonal -- the flat full-coverage limit G = (Omega/2) I,
      //in which both give sqrt(2/Nacc), proposal Eqs. 9 and 15. That is exactly
      //why the row-norm form survived its original validation: the ideal case has
      //no discriminating power (md Section 7).
      if (!(MUT3(i,i) > 0))
	std::cout << "non-positive diagonal in inverted MUT3! bin " << Nt - 1
		  << " i=" << i << std::endl;
      //Omega cancels here: MUT3 ~ Omega so MUT3^-1 ~ 1/Omega. No branch needed.
      Estatraw_diag[i] = sqrt(OM * MUT3(i,i) / Nacc);
    }
    //md Section 3. Appendix II projects not with f but with
    //    u = (sin(phi), sin(2 phih) cos(phi), cos(2 phih) sin(phi)),
    //and inverts the MIXED matrix (M_paper)_jk = Int u_j f_k rather than the
    //symmetric Gram of f with itself. The two bases are related by f = T u and
    //u = S f, S = T^-1, with
    //    T = [[1,0,0],[0,1,-1],[0,1,1]],   S = [[1,0,0],[0,1/2,1/2],[0,-1/2,1/2]]
    //so that MUT3_prop below is S * MUT3. (Note the direction: u = S f, NOT
    //u = T f.) Because M_paper^-1 I_paper = (SG)^-1 S J = G^-1 J, both routes
    //return the same three amplitudes -- md Section 3 -- and, as md Section 4
    //shows, the same covariance. Built from the same histogram and the same
    //Omega as MUT3, so nothing but the estimator differs, which is what makes
    //the agreement below a test rather than a tautology.
    TMatrixD MUT3_prop(3,3), Ggg(3,3);
    for (int i = 0; i < 3; i++)
      for (int j = 0; j < 3; j++){
	MUT3_prop(i,j) = 0.0;
	Ggg(i,j) = 0.0;
      }
    for (int i = 1; i <= nxbin; i++){
      for (int j = 1; j <= nybin; j++){
	phih = hmat->GetXaxis()->GetBinCenter(i);
	phiS = hmat->GetYaxis()->GetBinCenter(j);
	const double w = hmat->GetBinContent(i,j) / Nacc * OM;
	const double phi = phih - phiS;//the Sivers angle, md/proposal notation
	const double ff[3] = {sin(phi), sin(2.0 * phih - phi), sin(2.0 * phih + phi)};//= f
	const double gg[3] = {sin(phi), sin(2.0 * phih) * cos(phi), cos(2.0 * phih) * sin(phi)};//= u
	for (int a = 0; a < 3; a++)
	  for (int b = 0; b < 3; b++){
	    MUT3_prop(a,b) += gg[a] * ff[b] * w;
	    Ggg(a,b)       += gg[a] * gg[b] * w;
	  }
      }
    }
    //Estatraw_prop: the propagation written in Appendix II itself,
    //    delta_i^2 = Int (dA)^2 (sum_j (M_paper^-1)_ij u_j)^2
    //             = [M_paper^-1 <u u^T> M_paper^-T]_ii  (times Omega/Nacc),
    //which expands the square and keeps the cross terms the row norm drops.
    //Since M_paper = S G, the S cancels and this reduces analytically to the
    //diagonal form above (md Section 4). Measured agreement across three
    //acceptance configurations: 1.2e-14 or better (md Section 7, Result 1).
    {
      const double detp = MUT3_prop.Determinant();
      if (fabs(detp) > 0.0){
	TMatrixD MPinv(MUT3_prop);
	MPinv.Invert();
	TMatrixD MPinvT(TMatrixD::kTransposed, MPinv);
	TMatrixD Cov(MPinv, TMatrixD::kMult, TMatrixD(Ggg, TMatrixD::kMult, MPinvT));
	for (int i = 0; i < 3; i++)
	  Estatraw_prop[i] = sqrt(OM / Nacc * Cov(i,i));//Omega cancels, as for _diag
      }
      else {
	std::cout << "singular MUT3_prop! bin " << Nt - 1 << std::endl;
	for (int i = 0; i < 3; i++) Estatraw_prop[i] = -1.0;
      }
    }
    //from Estatraw to Estat
    for (int i = 0; i < 3; i++){
      //Same dilution / target-polarisation / beam-polarisation scaling,
      //so the three Estat* columns are directly comparable downstream.
      Estat[i] = Estatraw[i] / fn / 0.6 / 0.86;
      Estat_diag[i] = Estatraw_diag[i] / fn / 0.6 / 0.86;
      Estat_prop[i] = (Estatraw_prop[i] >= 0.0) ? Estatraw_prop[i] / fn / 0.6 / 0.86 : -1.0;
      if (std::isnan(Estat[i]))
	std::cout << "NaN warning in Estat!" << std::endl;
    }
    Ts->Fill();
    //Save both maps before they are deleted. Index matches the tree entry and
    //the bin_enhanced_*.dat row 1:1; the title carries the kinematics so the
    //file browses without a lookup table.
    char hskey[40];
    char hstitle[300];
    snprintf(hstitle, sizeof(hstitle),
	     "bin %d  Q2[%.1f,%.1f] z[%.2f,%.2f] Pt[%.1f,%.1f] x[%.4f,%.4f]",
	     Nt - 1, Xmin[1], Xmax[1], Xmin[2], Xmax[2], Xmin[3], Xmax[3], Xmin[0], Xmax[0]);
    char hslabel[360];
    snprintf(hslabel, sizeof(hslabel), "%s (folded, feeds MUT3);#phi_{h};|#phi_{S}|", hstitle);
    hs->SetTitle(hslabel);
    snprintf(hskey, sizeof(hskey), "hs_%04d", Nt - 1);
    fhs->WriteTObject(hs, hskey);
    snprintf(hslabel, sizeof(hslabel), "%s (unfolded);#phi_{h};#phi_{S}", hstitle);
    hs_full->SetTitle(hslabel);
    snprintf(hskey, sizeof(hskey), "hs_full_%04d", Nt - 1);
    fhs->WriteTObject(hs_full, hskey);
    hvar->Delete();
    hs_full->Delete();
    hs->Delete();
  }
  fs->Write();
  fhs->Close();
  infile.close();
  return 0;
}
  
double CheckCurrentCut(const double Ebeam, const char * hadron, const double kT2 = 0.16, const double MiT2 = 0.4, const double MfT2 = 0.4, const char * plotname = 0){
  Lsidis sidis;
  TLorentzVector l(0, 0, Ebeam, Ebeam);
  TLorentzVector P(0, 0, 0, 0.938272);
  sidis.SetNucleus(Np,Nn);
  sidis.SetHadron(hadron);
  if (strcmp(hadron, "pi+") == 0 || strcmp(hadron, "pi-") == 0) sidis.ChangeTMDpars(0.604, 0.114);
  if (strcmp(hadron, "K+") == 0 || strcmp(hadron, "K-") == 0) sidis.ChangeTMDpars(0.604, 0.131);
  sidis.SetInitialState(l, P);
  sidis.SetPDFset("CJ15lo");
  sidis.SetFFset("DSSFFlo");
  double lumi = 1.0e+10 * pow(0.197327, 2);
  double Nsim = 1.0e7;
  TH2D * h0 = new TH2D("h0", "", 1, 0.2, 0.8, 1, 0.0, 1.6);
  h0->GetXaxis()->SetTitle("z");
  h0->GetXaxis()->CenterTitle(true);
  h0->GetXaxis()->SetTitleSize(0.05);
  h0->GetXaxis()->SetTitleOffset(1.15);
  h0->GetXaxis()->SetLabelSize(0.055);
  h0->GetYaxis()->SetTitle("P_{hT} / GeV");
  h0->GetYaxis()->CenterTitle(true);
  h0->GetYaxis()->SetTitleSize(0.05);
  h0->GetYaxis()->SetTitleOffset(1.15);
  h0->GetYaxis()->SetLabelSize(0.055);
  TH2D * hall = new TH2D("hall", "Before cut", 60, 0.2, 0.8, 160, 0.0, 1.6);
  TH2D * hcut = new TH2D("hcut", "After cut", 60, 0.2, 0.8, 160, 0.0, 1.6);
  double Xmin[6] = {0.0, 1.0, 0.3, 0.0, -M_PI, -M_PI};
  double Xmax[6] = {0.7, 8.0, 0.7, 1.6, M_PI, M_PI};
  sidis.SetRange(Xmin, Xmax);
  double weight = 0;
  double acc = 0;
  TLorentzVector lp, Ph;
  for (Long64_t i = 0; i < Nsim; i++){
    if (sidis.GenerateEventKinematics(1)){//kinematics only; defer PDF/FF evaluation until after the (cheap) acceptance cut
      if (sidis.GetVariable("W") < 2.3) continue;
      if (sidis.GetVariable("Wp") < 1.6) continue;
      lp = sidis.GetLorentzVector("lp");
      Ph = sidis.GetLorentzVector("Ph");
      acc = GetAcceptance_e(lp) * GetAcceptance_hadron(Ph, hadron);
      if (acc > 0){
	weight = sidis.GetWeightFromCurrentState(0);
	if (weight > 0){
	hall->Fill(sidis.GetVariable("z"), sidis.GetVariable("Pt"), weight * acc);
	sidis.CalculateRfactor(kT2, MiT2, MfT2);
	if (sidis.GetVariable("Rfactor") < 0.4){
	  hcut->Fill(sidis.GetVariable("z"), sidis.GetVariable("Pt"), weight * acc);
	}
	}
      }
    }
  }
  hall->Scale(lumi/Nsim);
  hcut->Scale(lumi/Nsim);
  double rate = hcut->Integral(1, -1, 1, -1);
  std::cout << "All: " << hall->Integral(1, -1, 1, -1) << "   Cut: " << hcut->Integral(1, -1, 1, -1) << std::endl;
  if (plotname != 0){
    gStyle->SetOptStat(0);
    //hall->GetZaxis()->SetRangeUser(0.01, hall->GetMaximum()/0.95);
    hcut->GetZaxis()->SetRangeUser(0.01, hall->GetMaximum());
    TCanvas * c0 = new TCanvas("c0", "", 1600, 600);
    c0->SetBorderMode(0);
    c0->SetBorderSize(2);
    c0->SetFrameBorderMode(0);
    c0->Divide(2, 1);
    c0->cd(1);
    c0->cd(1)->SetLeftMargin(0.15);
    c0->cd(1)->SetBottomMargin(0.15);
    h0->Draw();
    hall->Draw("samecolz");
    c0->cd(2);
    c0->cd(2)->SetLeftMargin(0.15);
    c0->cd(2)->SetBottomMargin(0.15);
    h0->Draw();
    hcut->Draw("samecolz");
    c0->Print(plotname);
    c0->Close();
  }
  h0->Delete();
  hall->Delete();
  hcut->Delete();
  return rate;
}

int CreateFileSivers(const char * rootfile1, const char * rootfile2, const char * csvfile){//Create file for Sivers analysis use
  TChain * Ts = new TChain("data", "data");
  Ts->Add(rootfile1);
  Ts->Add(rootfile2);
  double Nucleon, Hadron, Ebeam, x, y, z, Q2, Pt, stat, systrel, systabs, fn, Nacc;
  Ts->SetBranchAddress("Nucleon", &Nucleon);
  Ts->SetBranchAddress("Hadron", &Hadron);
  Ts->SetBranchAddress("Ebeam", &Ebeam);
  Ts->SetBranchAddress("x", &x);
  Ts->SetBranchAddress("y", &y);
  Ts->SetBranchAddress("z", &z);
  Ts->SetBranchAddress("Q2", &Q2);
  Ts->SetBranchAddress("Pt", &Pt);
  Ts->SetBranchAddress("E1stat", &stat);
  Ts->SetBranchAddress("Nacc", &Nacc);
  Ts->SetBranchAddress("fn", &fn);
  FILE * file = fopen(csvfile, "w");
  fprintf(file, "i,Ebeam,x,y,z,Q2,pT,obs,value,stat,systrel,systabs,target,hadron,Experiment,Nacc\n");
  for (int i = 0; i < Ts->GetEntries(); i++){
    std::cout << i << std::endl;
    Ts->GetEntry(i);
    systrel = 0.0;
    systabs = 0.0;
    systrel += pow(0.03, 2);//target polarization
    systrel += pow(0.05, 2);//nuclear effect
    systrel += pow(0.025, 2);//radiative correction
    systrel += pow(0.03, 2);//diffractive meson
    systrel += pow(0.002, 2);//random coincidence
    if (Ebeam > 10.0)//raw asymmetry
      systabs += 1.7e-4 / 0.6 / fn / 0.86;
    else
      systabs += 2.57e-4 / 0.6 / fn / 0.86;
    systrel = sqrt(systrel);
    if (Hadron == 0)
      // fprintf(file, "%d,%.1f,%.6f,%.6f,%.6f,%.6f,%.6f,%s,%.1f,%.6f,%.6f,%.6f,%s,%s,%s\n",
	      // i, Ebeam, x, y, z, Q2, Pt, "AUT", 0.0, stat, systrel, systabs, "neutron", "pi+", "solid");
      fprintf(file, "%d,%.1f,%.6f,%.6f,%.6f,%.6f,%.6f,%s,%.1f,%.6f,%.6f,%.6f,%s,%s,%s,%.6f\n",
	      i, Ebeam, x, y, z, Q2, Pt, "AUT", 0.0, stat, systrel, systabs, "neutron", "pi+", "solid",Nacc);
    else if (Hadron == 1)
      // fprintf(file, "%d,%.1f,%.6f,%.6f,%.6f,%.6f,%.6f,%s,%.1f,%.6f,%.6f,%.6f,%s,%s,%s\n",
	     //  i, Ebeam, x, y, z, Q2, Pt, "AUT", 0.0, stat, systrel, systabs, "neutron", "pi-", "solid");
      fprintf(file, "%d,%.1f,%.6f,%.6f,%.6f,%.6f,%.6f,%s,%.1f,%.6f,%.6f,%.6f,%s,%s,%s,%.6f\n",
	      i, Ebeam, x, y, z, Q2, Pt, "AUT", 0.0, stat, systrel, systabs, "neutron", "pi-", "solid",Nacc);
  }
  fclose(file);
  return 0;
}







  
#endif




  
	
	
