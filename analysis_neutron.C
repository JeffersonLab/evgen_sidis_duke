#include "SoLID_SIDIS_3He.h"

#include <unistd.h>
#include <sys/wait.h>
#include <functional>
#include <vector>
#include <filesystem>

using namespace std;

// Runs each job in its own forked child process (not std::thread): ROOT's
// gRandom and the current-TFile/TDirectory globals are not thread-safe, so
// concurrent histogram/file creation in threads can silently attach output
// to the wrong file. fork() gives each job an isolated copy of that state.
// Each child reseeds gRandom so the 4 groups draw independent random streams.
void RunGroupsInParallel(const vector<function<void()>> & jobs){
  vector<pid_t> pids;
  for (size_t i = 0; i < jobs.size(); i++){
    pid_t pid = fork();
    if (pid < 0){
      perror("fork");
      exit(1);
    }
    if (pid == 0){
      gRandom->SetSeed(gRandom->GetSeed() + i + 1);
      jobs[i]();
      _exit(0);
    }
    pids.push_back(pid);
  }
  for (pid_t pid : pids) waitpid(pid, NULL, 0);
}

int main(int argc, char * argv[]){

  if (argc < 2){
    cout << "./analysis_neutron <opt> <rundir> [phicut] [phiscope] [phiwidth] [acccut] [phisfold]" << endl;
    cout << "opt = 0: total rate (no rundir needed, writes nothing)" << endl;
    cout << "     ./analysis 0" << endl;
    cout << "opt = 1: binning data and create bin info file" << endl;
    cout << "     ./analysis 1 <rundir> [phicut] [phiscope] [phiwidth]" << endl;
    cout << "opt = 2: bin analysis including Estat" << endl;
    cout << "     ./analysis 2 <rundir> [phicut] [phiscope] [phiwidth]" << endl;
    cout << "opt = 3: output file for Sivers analysis" << endl;
    cout << "     ./analysis 3 <rundir>" << endl;
    cout << "opt = 4: Nacc count table on a fine (x,Q2,z,Pt) grid -> count_N*.dat" << endl;
    cout << "     ./analysis 4 <rundir>      (independent of opts 1-3)" << endl;
    cout << "rundir: the one directory this run reads and writes; required for" << endl;
    cout << "        opt 1/2/3/4, created if missing. prepare.py and fit*.py take" << endl;
    cout << "        the same directory, so a run lives in exactly one place." << endl;
    cout << "phicut: number of azimuthal sectors to keep, each phiwidth wide" << endl;
    cout << "        0 = full 2pi coverage (default)" << endl;
    cout << "        2 = 2 sectors, centres at 0,180         (13.3% of 2pi at 24deg)" << endl;
    cout << "        4 = 4 sectors, centres at 0,+-90,180   (26.7% of 2pi at 24deg)" << endl;
    cout << "        6 = 6 sectors, centres at 0,+-60,+-120,180 (40.0% of 2pi at 24deg)" << endl;
    cout << "        1 = legacy alias for 6 (kept so older logged commands reproduce)" << endl;
    cout << "phiscope: which detector the sectors sit in front of" << endl;
    cout << "        all = forward and large angle alike (default, what 4/6-sector runs did)" << endl;
    cout << "        FA  = forward angle only; large-angle electrons keep full 2pi" << endl;
    cout << "              (hadrons are forward-angle only here, so they stay cut)" << endl;
    cout << "phiwidth: full width of one sector in degrees, default 24" << endl;
    cout << "        must satisfy phiwidth <= 360/phicut or the sectors overlap" << endl;
    cout << "        e.g. ./analysis_neutron 1 run_phi4seg12deg 4 all 12" << endl;
    cout << "             -> 4 sectors of 12deg, centres at 0,+-90,180 (13.3% of 2pi)" << endl;
    cout << "acccut: on (default) = the SoLID acceptance as usual" << endl;
    cout << "        off = no detector at all -- every acceptance returns 1.0, so" << endl;
    cout << "              theta ranges, momentum thresholds, azimuthal sectors and" << endl;
    cout << "              the Acceptance/ maps are all bypassed: perfect 4pi with" << endl;
    cout << "              unit efficiency. The W/W\'/R-factor physics cuts stay." << endl;
    cout << "              A diagnostic, not a physical configuration." << endl;
    cout << "phisfold: which azimuthal map the moment matrix is built from" << endl;
    cout << "        full (default) = hs_full, signed phi_S over [-pi,pi]. MUT3" << endl;
    cout << "              evaluates sin(phi_h - phi_S) with no approximation." << endl;
    cout << "        fold = hs, folded onto |phi_S|, so MUT3 evaluates" << endl;
    cout << "              sin(phi_h - |phi_S|). The historical behaviour -- pass this" << endl;
    cout << "              to reproduce anything generated before 2026-08-27." << endl;
    cout << "        Both maps are booked at the bin width set by NPHI in the header" << endl;
    cout << "        (currently 1 deg). Difference between the two: ~4e-3 on Estat." << endl;
    return 0;
  }

  int opt = atoi(argv[1]);

  //No default rundir. Every stage of a run -- this binary, prepare.py, fit*.py --
  //takes the same directory, so a forgotten argument used to mean silently
  //reading or overwriting whichever run was there last. opt 0 only prints rates,
  //so it needs no directory at all.
  if (opt != 0 && argc < 3){
    cout << "error: opt " << opt << " needs a rundir" << endl;
    cout << "usage: ./analysis_neutron " << opt << " <rundir> [phicut] [phiscope] [phiwidth] [acccut] [phisfold]" << endl;
    return 1;
  }
  string outdir = (argc > 2) ? argv[2] : "";

  //Without this, a missing outdir makes the TFile writes fail deep inside the
  //forked children: ROOT's crash handler then suspends each child trying to
  //spawn gdb, so the parent blocks in waitpid() forever and the run looks like
  //it is still computing. Create it up front, matching prepare.py/fit*.py which
  //both do os.makedirs(rundir, exist_ok=True).
  if (opt != 0){
    std::error_code ec;
    if (std::filesystem::exists(outdir) && !std::filesystem::is_directory(outdir)){
      cout << "error: " << outdir << " exists but is not a directory" << endl;
      return 1;
    }
    if (!std::filesystem::exists(outdir)){
      std::filesystem::create_directories(outdir, ec);
      if (ec){
	cout << "error: cannot create output directory " << outdir
	     << " (" << ec.message() << ")" << endl;
	return 1;
      }
      cout << "created output directory " << outdir << endl;
    }
  }

  int phicut = (argc > 3) ? atoi(argv[3]) : 0;
  if (phicut == 1){//"1" used to mean "on", which meant 6 sectors
    cout << "note: phicut=1 is a legacy alias for 6 sectors; using 6" << endl;
    phicut = 6;
  }
  if (phicut < 0){
    cout << "error: phicut must be >= 0 (got " << phicut << ")" << endl;
    return 1;
  }
  string phiscope = (argc > 4) ? argv[4] : "all";
  if (phiscope != "all" && phiscope != "FA"){
    cout << "error: phiscope must be \"all\" or \"FA\" (got " << phiscope << ")" << endl;
    return 1;
  }
  phi_cut_fa_only = (phiscope == "FA");

  //Sector width. Default 24 deg, the value every run logged before 2026-08-24
  //used, so an unchanged command line still reproduces its old output.
  double phiwidth = (argc > 5) ? atof(argv[5]) : 24.0;

  if (phiwidth <= 0.0){
    cout << "error: phiwidth must be > 0 (got " << phiwidth << ")" << endl;
    return 1;
  }
  //Sectors are spaced 360/phicut apart, so anything wider than that spacing
  //makes neighbouring sectors overlap: the coverage formula below then reports
  //more than 100% and the cut quietly degenerates towards full acceptance.
  //Reject it rather than let a run produce a number nobody can interpret.
  if (phicut > 0 && phiwidth > 360.0 / phicut){
    cout << "error: " << phicut << " sectors of " << phiwidth
	 << " deg overlap (spacing is " << 360.0 / phicut
	 << " deg); need phiwidth <= 360/phicut" << endl;
    return 1;
  }

  //[acccut] -- see use_acc_cut in the header. Anything other than "on"/"off" is a
  //typo the run must not silently absorb: the two give wildly different yields and
  //nothing downstream records which was used.
  if (argc > 6){
    if (strcmp(argv[6], "off") == 0) use_acc_cut = false;
    else if (strcmp(argv[6], "on") == 0) use_acc_cut = true;
    else {
      cout << "error: acccut must be \"on\" or \"off\", got \"" << argv[6] << "\"" << endl;
      return 1;
    }
  }
  //[phisfold] -- see use_unfolded_phiS in the header.
  if (argc > 7){
    if (strcmp(argv[7], "full") == 0) use_unfolded_phiS = true;
    else if (strcmp(argv[7], "fold") == 0) use_unfolded_phiS = false;
    else {
      cout << "error: phisfold must be \"fold\" or \"full\", got \"" << argv[7] << "\"" << endl;
      return 1;
    }
  }
  if (use_unfolded_phiS)
    cout << "moment matrix: hs_full, signed phi_S, Omega = 4pi^2" << endl;
  else
    cout << "moment matrix: hs, folded |phi_S|, Omega = 2pi^2" << endl;

  if (use_acc_cut)
    cout << "acceptance: SoLID maps from Acceptance/" << endl;
  else
    cout << "acceptance: OFF -- perfect 4pi, unit efficiency, no theta/momentum/phi"
	 << " cuts (diagnostic only)" << endl;

  use_phi_cut = (phicut > 0);
  if (use_phi_cut){
    phi_nsector = phicut;
    phi_sector_width = phiwidth;
    cout << "azimuthal cut: " << phi_nsector << " sectors of " << phi_sector_width
	 << " deg = " << phi_nsector * phi_sector_width / 360.0 * 100.0
	 << "% of 2pi" << endl;
    if (phi_cut_fa_only)
      cout << "               forward angle only; large-angle electrons keep full 2pi"
	   << endl;
    else
      cout << "               forward and large angle alike" << endl;
  }
  else {
    cout << "azimuthal coverage: full 2pi" << endl;
    if (phi_cut_fa_only)
      cout << "note: phiscope=FA has no effect with phicut=0" << endl;
    if (argc > 5)
      cout << "note: phiwidth has no effect with phicut=0" << endl;
  }

  gRandom->SetSeed(2);
  LHAPDF::setVerbosity(0);

  if (opt == 0){
    gRandom->SetSeed(0);
    cout << "Enhanced:" << endl;
    RunGroupsInParallel({
      [](){ GetTotalRate(11.0, "pi+"); },
      [](){ GetTotalRate(8.8, "pi+"); },
      [](){ GetTotalRate(11.0, "pi-"); },
      [](){ GetTotalRate(8.8, "pi-"); },
    });
    // pimin = 2.5;
    // cout << "Baseline:" << endl;
    // GetTotalRate(11.0, "pi+");
    // GetTotalRate(8.8, "pi+");
    // GetTotalRate(11.0, "pi-");
    // GetTotalRate(8.8, "pi-");
  }

  if (opt == 1){
    pimin = 0;
    RunGroupsInParallel({
      [&](){ GenerateBinInfoFile((outdir + "/bin_enhanced_N11p.dat").c_str(), 11.0, "pi+"); },
      [&](){ GenerateBinInfoFile((outdir + "/bin_enhanced_N8p.dat").c_str(), 8.8, "pi+"); },
      [&](){ GenerateBinInfoFile((outdir + "/bin_enhanced_N11m.dat").c_str(), 11.0, "pi-"); },
      [&](){ GenerateBinInfoFile((outdir + "/bin_enhanced_N8m.dat").c_str(), 8.8, "pi-"); },
    });
    // pimin = 2.5;
    // GenerateBinInfoFile((outdir + "/bin_base_N11p.dat").c_str(), 11.0, "pi+");
    // GenerateBinInfoFile((outdir + "/bin_base_N8p.dat").c_str(), 8.8, "pi+");
    // GenerateBinInfoFile((outdir + "/bin_base_N11m.dat").c_str(), 11.0, "pi-");
    // GenerateBinInfoFile((outdir + "/bin_base_N8m.dat").c_str(), 8.8, "pi-");
  }

  if (opt == -1){
    Rfactor0 = 0.4;
    pimin = 0;
    RunGroupsInParallel({
      [&](){ GenerateBinInfoFile((outdir + "/bin_enhanced_N11p_cut.dat").c_str(), 11.0, "pi+"); },
      [&](){ GenerateBinInfoFile((outdir + "/bin_enhanced_N8p_cut.dat").c_str(), 8.8, "pi+"); },
      [&](){ GenerateBinInfoFile((outdir + "/bin_enhanced_N11m_cut.dat").c_str(), 11.0, "pi-"); },
      [&](){ GenerateBinInfoFile((outdir + "/bin_enhanced_N8m_cut.dat").c_str(), 8.8, "pi-"); },
    });
    // pimin = 2.5;
    // GenerateBinInfoFile((outdir + "/bin_base_N11p_cut.dat").c_str(), 11.0, "pi+");
    // GenerateBinInfoFile((outdir + "/bin_base_N8p_cut.dat").c_str(), 8.8, "pi+");
    // GenerateBinInfoFile((outdir + "/bin_base_N11m_cut.dat").c_str(), 11.0, "pi-");
    // GenerateBinInfoFile((outdir + "/bin_base_N8m_cut.dat").c_str(), 8.8, "pi-");
  }


  if (opt == 2){
    pimin = 0;
    RunGroupsInParallel({
      [&](){ AnalyzeEstatUT3((outdir + "/bin_enhanced_N11p.dat").c_str(), (outdir + "/enhancedN11p.root").c_str(), 11.0, "pi+"); },
      [&](){ AnalyzeEstatUT3((outdir + "/bin_enhanced_N8p.dat").c_str(), (outdir + "/enhancedN8p.root").c_str(), 8.8, "pi+"); },
      [&](){ AnalyzeEstatUT3((outdir + "/bin_enhanced_N11m.dat").c_str(), (outdir + "/enhancedN11m.root").c_str(), 11.0, "pi-"); },
      [&](){ AnalyzeEstatUT3((outdir + "/bin_enhanced_N8m.dat").c_str(), (outdir + "/enhancedN8m.root").c_str(), 8.8, "pi-"); },
    });
    // pimin = 2.5;
    // AnalyzeEstatUT3((outdir + "/bin_base_N11p.dat").c_str(), (outdir + "/baseN11p.root").c_str(), 11.0, "pi+");
    // AnalyzeEstatUT3((outdir + "/bin_base_N8p.dat").c_str(), (outdir + "/baseN8p.root").c_str(), 8.8, "pi+");
    // AnalyzeEstatUT3((outdir + "/bin_base_N11m.dat").c_str(), (outdir + "/baseN11m.root").c_str(), 11.0, "pi-");
    // AnalyzeEstatUT3((outdir + "/bin_base_N8m.dat").c_str(), (outdir + "/baseN8m.root").c_str(), 8.8, "pi-");
  }

  // opt 4: the (x, Q2, z, Pt) count table. Independent of opts 1-3 -- it does its
  // own event scan and reads no bin file, so it can run on a fresh <rundir>.
  // Same 4-way split as opt 2, one file per (beam, charge).
  //
  // Nsim = 8e9 is set from measurement at the 0.02/0.05/0.02/0.02 widths, which
  // give a 35 x 180 x 20 x 100 = 12.6e6 cell grid -- 31x finer than the previous
  // 0.05/0.1/0.05/0.05 run, so each cell holds ~1/31 of the events.
  //
  //   probe, 11 GeV, 1e8 events: 791124 occupied cells, median 3 events/cell
  //   previous run, 1e9 events, coarse grid: 41747 cells, median 538
  //
  // Occupancy saturates near ~10% of the grid (it did at the coarse widths), so
  // ~1.2e6 cells at 11 GeV and ~0.46e6 at 8.8. Reaching a median of 100 needs
  // ~1.6e8 accepted events at 11 GeV and ~0.6e8 at 8.8; the accepted fractions
  // are 2.9% and 0.8%, so 8e9 thrown covers BOTH -- the 8.8 GeV beam is the
  // binding constraint, needing ~7.4e9 against 11 GeV's ~5.4e9.
  //
  // As at the coarse widths, "every cell above 100" is still not reachable:
  // edge-of-phase-space cells keep appearing as statistics grow. Cut on relerr
  // or Nmc, both written per row.
  if (opt == 4){
    const Long64_t NCOUNT = 8000000000LL;
    RunGroupsInParallel({
      [&](){ MakeCountTable(11.0, (outdir + "/count_N11p.dat").c_str(), "pi+", NCOUNT); },
      [&](){ MakeCountTable(8.8,  (outdir + "/count_N8p.dat").c_str(),  "pi+", NCOUNT); },
      [&](){ MakeCountTable(11.0, (outdir + "/count_N11m.dat").c_str(), "pi-", NCOUNT); },
      [&](){ MakeCountTable(8.8,  (outdir + "/count_N8m.dat").c_str(),  "pi-", NCOUNT); },
    });
  }

  if (opt == 3){
    CreateFile((outdir + "/enhancedN11p.root").c_str(), (outdir + "/enhancedN8p.root").c_str(), (outdir + "/enhancedNpip.csv").c_str());
    CreateFile((outdir + "/enhancedN11m.root").c_str(), (outdir + "/enhancedN8m.root").c_str(),(outdir + "/enhancedNpim.csv").c_str());
    // CreateFile((outdir + "/baseN11p.root").c_str(), (outdir + "/baseN8p.root").c_str(), (outdir + "/baseNpip.csv").c_str());
    // CreateFile((outdir + "/baseN11m.root").c_str(), (outdir + "/baseN8m.root").c_str(), (outdir + "/baseNpim.csv").c_str());
  }

  return 0;
}
	

	



      

  
  

