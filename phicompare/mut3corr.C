// Collins-Sivers correlation of the inverted MUT3, per bin, for one run dir.
//   root -l -b -q 'mut3corr.C("<rundir>","<out.txt>",<stride>)'
// Same matrix as SIDIS_MUT3_comparison/extract_hs.C: G_ab = <F_a F_b> * 4pi^2
// over the 1 deg hs_full map, with F = {sin(ph-pS), sin(ph+pS), sin(3ph-pS)}
// = {Sivers, Collins, pretzelosity}. The fit error on amplitude a goes as
// sqrt((G^-1)_aa), and (G^-1) off-diagonals say how much the amplitudes are
// mixed; corr_ab = C_ab/sqrt(C_aa C_bb) with C = G^-1.
// Prints one row per bin: idx Nacc cSivCol cSivPre cColPre sqrtC00 sqrtC11 sqrtC22 cond
void mut3corr(const char* dir, const char* out, int stride=20){
  const int NPHI=360;
  TFile* t=TFile::Open(Form("%s/enhancedN11p.root",dir));
  TFile* h=TFile::Open(Form("%s/enhancedN11p_hs.root",dir));
  if(!t||!h){ printf("cannot open %s\n",dir); return; }
  TTree* T=(TTree*)t->Get("data");
  double Nacc; T->SetBranchAddress("Nacc",&Nacc);
  FILE* o=fopen(out,"w");
  for(int i=0;i<T->GetEntries();i+=stride){
    T->GetEntry(i);
    TH2D* H=(TH2D*)h->Get(Form("hs_full_%04d",i));
    if(!H) continue;
    TMatrixD G(3,3); G.Zero();
    double tot=0;
    for(int iy=1;iy<=NPHI;iy++) for(int ix=1;ix<=NPHI;ix++) tot+=H->GetBinContent(ix,iy);
    if(tot<=0){ delete H; continue; }
    for(int iy=1;iy<=NPHI;iy++){
      double pS=H->GetYaxis()->GetBinCenter(iy);
      for(int ix=1;ix<=NPHI;ix++){
        double w=H->GetBinContent(ix,iy); if(w==0) continue;
        double ph=H->GetXaxis()->GetBinCenter(ix);
        double F[3]={sin(ph-pS),sin(ph+pS),sin(3*ph-pS)};
        for(int a=0;a<3;a++) for(int b=0;b<3;b++) G(a,b)+=w/tot*F[a]*F[b]*4*M_PI*M_PI;
      }
    }
    TMatrixDSym S(3); for(int a=0;a<3;a++) for(int b=0;b<3;b++) S(a,b)=G(a,b);
    TMatrixDSymEigen eig(S);
    TVectorD ev=eig.GetEigenValues();
    double emin=1e300,emax=-1e300;
    for(int a=0;a<3;a++){ emin=std::min(emin,ev(a)); emax=std::max(emax,ev(a)); }
    TMatrixD C(G); double det=0; C.Invert(&det);
    if(det==0 || C(0,0)<=0 || C(1,1)<=0 || C(2,2)<=0){ delete H; continue; }
    double s0=sqrt(C(0,0)), s1=sqrt(C(1,1)), s2=sqrt(C(2,2));
    fprintf(o,"%d %.8g %.6f %.6f %.6f %.6g %.6g %.6g %.6g\n", i, Nacc,
            C(0,1)/(s0*s1), C(0,2)/(s0*s2), C(1,2)/(s1*s2), s0, s1, s2,
            (emin>0? emax/emin : -1.0));
    delete H;
  }
  fclose(o); printf("wrote %s\n",out);
}
