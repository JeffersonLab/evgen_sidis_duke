// Companion to make_gallery.py -- see there for what the figures show.
//   root -l -b -q 'extract_hs.C("<fullrun>","<cutrun>","<out.txt>")'
// Both run dirs must carry the SAME step-1 bins; the 12 indices below are
// enhancedN11p entries chosen to span x, Q2, z and P_T.
// For 12 selected bins of enhancedN11p, pull the 1 deg hs_full map from two runs,
// write a 4 deg rebinned copy for display and the exact 3x3 MUT3 matrix built at
// full resolution, plus the per-bin kinematics, Nacc and E0statraw_prop.
void extract_hs(const char* A, const char* B, const char* out){
  const int NB=12; int idx[NB]={1,126,229,190,461,445,320,487,552,654,710,774};
  const int NPHI=360, REB=4, ND=NPHI/REB;
  TFile* ta=TFile::Open(Form("%s/enhancedN11p.root",A));
  TFile* tb=TFile::Open(Form("%s/enhancedN11p.root",B));
  TFile* ha=TFile::Open(Form("%s/enhancedN11p_hs.root",A));
  TFile* hb=TFile::Open(Form("%s/enhancedN11p_hs.root",B));
  TTree* TA=(TTree*)ta->Get("data"); TTree* TB=(TTree*)tb->Get("data");
  double xa,za,Q2a,Pta,Na,ea, Nb,eb;
  TA->SetBranchAddress("x",&xa); TA->SetBranchAddress("z",&za);
  TA->SetBranchAddress("Q2",&Q2a); TA->SetBranchAddress("Pt",&Pta);
  TA->SetBranchAddress("Nacc",&Na); TA->SetBranchAddress("E0statraw_prop",&ea);
  TB->SetBranchAddress("Nacc",&Nb); TB->SetBranchAddress("E0statraw_prop",&eb);

  FILE* o=fopen(out,"w");
  if(!o){ printf("cannot write %s\n",out); return; }
  for(int k=0;k<NB;k++){
    TA->GetEntry(idx[k]); TB->GetEntry(idx[k]);
    fprintf(o,"BIN %d %.6g %.6g %.6g %.6g %.8g %.8g %.10g %.10g\n",
            idx[k],xa,za,Q2a,Pta,Na,Nb,ea,eb);
    for(int s=0;s<2;s++){
      TFile* f = s?hb:ha;
      TH2D* H=(TH2D*)f->Get(Form("hs_full_%04d",idx[k]));
      if(!H){ printf("missing hs_full_%04d in %s\n",idx[k],s?B:A); fclose(o); return; }
      // MUT3 at full 1 deg resolution; phi = phih - phiS, Omega = 4 pi^2
      double G[3][3]={{0}}, tot=0;
      for(int iy=1;iy<=NPHI;iy++) for(int ix=1;ix<=NPHI;ix++) tot+=H->GetBinContent(ix,iy);
      for(int iy=1;iy<=NPHI;iy++){
        double pS=H->GetYaxis()->GetBinCenter(iy);
        for(int ix=1;ix<=NPHI;ix++){
          double ph=H->GetXaxis()->GetBinCenter(ix), w=H->GetBinContent(ix,iy);
          if(w==0) continue;
          double f0=sin(ph-pS), f1=sin(ph+pS), f2=sin(3*ph-pS), F[3]={f0,f1,f2};
          for(int a=0;a<3;a++) for(int b=0;b<3;b++) G[a][b]+=w/tot*F[a]*F[b]*4*M_PI*M_PI;
        }
      }
      for(int a=0;a<3;a++) fprintf(o,"G %.10g %.10g %.10g\n",G[a][0],G[a][1],G[a][2]);
      // 4 deg rebin for display
      TH2D* R=(TH2D*)H->Clone(Form("r%d_%d",s,k)); R->Rebin2D(REB,REB);
      for(int iy=1;iy<=ND;iy++){
        for(int ix=1;ix<=ND;ix++) fprintf(o,"%.6g ",R->GetBinContent(ix,iy));
        fprintf(o,"\n");
      }
      delete R;
    }
    printf("  bin %d done\n",idx[k]);
  }
  fclose(o); printf("wrote %s\n",out);
}
