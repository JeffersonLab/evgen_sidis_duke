// The upstream SBS projection trees -> sbs01_root.dat / sbs02_root.dat.
//
// Writes exactly the format of sbs01.dat / sbs02.dat -- tab separated, header
//     Q2  x  y  z  pT  obs  target  hadron  value  error
// with obs = AUTsivers (the legacy label those files carry on every row
// regardless of observable), target = neutron, and value = 0 for the model to
// fill. So anything that reads sbs01/sbs02 reads these unchanged.
//
//   sbs01_root.dat   pi+   sbs_neutron_pip_11.root + sbs_neutron_pip_8.root
//   sbs02_root.dat   pi-   sbs_neutron_pim_11.root + sbs_neutron_pim_8.root
//
// The `_root` suffix marks the provenance: straight from the four ROOT trees
// that `LiuSIDIS/SoLID/FOM_comparison/fom.C` chains, 455 rows. The plain
// sbs01.dat / sbs02.dat are a 289-row thinned subset of the same trees -- see
// README.md. The two are NOT interchangeable.
//
//   root -l -b -q 'dump_sbs.C()'                          // from the repo root
//   root -l -b -q 'dump_sbs.C("<srcdir>", "<outdir>")'    // from anywhere else
//
// <srcdir> holds sbs_neutron_pi{p,m}_{8,11}.root. Those are not in this
// repository; they live in LiuSIDIS/SoLID/FOM_comparison.
//
// PyROOT cannot be used on this machine -- ROOT 6.40 is built for python 3.12
// and the system interpreter is 3.9 -- so this runs under `root -l -b -q`, the
// same pattern as ../SIDIS_MUT3_comparison/dump_estat.C.
//
// No cuts are applied. Consumers cut for themselves, so the cuts live in exactly
// one place per study and cannot drift.
#include <cstdio>
#include "TFile.h"
#include "TTree.h"
#include "TString.h"

static long long dump_one(const char* srcdir, const char* f1, const char* f2,
                          const char* hadron, const char* outfile) {
  FILE* out = fopen(outfile, "w");
  if (!out) { printf("dump_sbs: cannot write %s\n", outfile); return -1; }
  fprintf(out, "Q2\tx\ty\tz\tpT\tobs\ttarget\thadron\tvalue\terror\n");

  const char* files[2] = {f1, f2};
  long long total = 0;
  for (int k = 0; k < 2; k++) {
    TString path = TString(srcdir) + "/" + files[k];
    TFile* f = TFile::Open(path);
    if (!f || f->IsZombie()) {
      printf("dump_sbs: cannot open %s\n", path.Data()); fclose(out); return -1;
    }
    TTree* t = (TTree*) f->Get("data");
    if (!t) {
      printf("dump_sbs: no tree 'data' in %s\n", path.Data());
      f->Close(); fclose(out); return -1;
    }
    // The `y` branch in these files is NEVER FILLED -- every row holds the same
    // uninitialised value (6.9e-310). fom.C never reads y, so it went unnoticed.
    // Reconstruct it from the inelasticity relation Q2 = x*y*(s - M^2) with a
    // fixed target, s - M^2 = 2*M*Ebeam:
    //     y = Q2 / (2 * M * Ebeam * x)
    // M = 0.93827 is fom.C's own constant, and it reproduces the `y` column of
    // the existing sbs01.dat to the last digit (0.7643338432983204 on its first
    // row), so these files and those agree on y by construction.
    const double Mp = 0.93827;
    double x, z, Q2, Pt, Estat, Ebeam, y;
    t->SetBranchAddress("x",  &x);
    t->SetBranchAddress("z",  &z);
    t->SetBranchAddress("Q2", &Q2);
    t->SetBranchAddress("Pt", &Pt);        // NB the branch is Pt, not pT
    t->SetBranchAddress("Estat", &Estat);
    t->SetBranchAddress("Ebeam", &Ebeam);
    for (Long64_t i = 0; i < t->GetEntries(); i++) {
      t->GetEntry(i);
      y = Q2 / (2.0 * Mp * Ebeam * x);
      fprintf(out, "%.10g\t%.10g\t%.10g\t%.10g\t%.10g\tAUTsivers\tneutron\t%s\t0\t%.10g\n",
              Q2, x, y, z, Pt, hadron, Estat);
      total++;
    }
    printf("dump_sbs:   %-28s %6lld entries\n", files[k], t->GetEntries());
    f->Close();
  }
  fclose(out);
  printf("dump_sbs: wrote %lld rows (%s) to %s\n", total, hadron, outfile);
  return total;
}

// NB the defaults assume this macro is run from the repository root, and that
// the output belongs in data_sbs/ -- sbs0{1,2}_root.dat are the UNCUT
// projection and are read from there by FOM/plot_fom_solid_vs_sbs.py. Pass both
// explicitly if you run it from anywhere else.
void dump_sbs(const char* srcdir = "../LiuSIDIS/SoLID/FOM_comparison",
              const char* outdir = "data_sbs") {
  long long a = dump_one(srcdir, "sbs_neutron_pip_11.root", "sbs_neutron_pip_8.root",
                         "pi+", Form("%s/sbs01_root.dat", outdir));
  long long b = dump_one(srcdir, "sbs_neutron_pim_11.root", "sbs_neutron_pim_8.root",
                         "pi-", Form("%s/sbs02_root.dat", outdir));
  if (a > 0 && b > 0) printf("dump_sbs: %lld rows total\n", a + b);
}
