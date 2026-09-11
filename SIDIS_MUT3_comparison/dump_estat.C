// Dump the per-bin Estat branches of one run directory to a text file.
//
//   root -l -b -q 'dump_estat.C("<rundir>","<out.txt>")'
//
// Columns: grp idx i raw diag prop Nacc fn
//   grp  0-3 = enhancedN11p, N11m, N8p, N8m   (each a separate tree, own index)
//   idx  entry number within that tree
//   i    0-2 = Sivers, Collins, Pretzelosity
// Written at %.17g: the prop/diag comparison is a 1e-14 effect, and dumping at
// %.10g truncates it to zero.
void dump_estat(const char* dir, const char* out){
  const char* g[] = {"enhancedN11p", "enhancedN11m", "enhancedN8p", "enhancedN8m"};
  const char* a[] = {"E0statraw", "E1statraw", "E2statraw"};
  const char* b[] = {"E0statraw_diag", "E1statraw_diag", "E2statraw_diag"};
  const char* c[] = {"E0statraw_prop", "E1statraw_prop", "E2statraw_prop"};

  FILE* o = fopen(out, "w");
  if (!o){ printf("cannot write %s\n", out); return; }
  fprintf(o, "# grp idx i raw diag prop Nacc fn\n");

  for (int k = 0; k < 4; k++){
    TFile* f = TFile::Open(Form("%s/%s.root", dir, g[k]));
    if (!f || f->IsZombie()){ printf("missing %s/%s.root\n", dir, g[k]); fclose(o); return; }
    TTree* T = (TTree*) f->Get("data");
    double raw[3], diag[3], prop[3], Nacc, fn;
    for (int i = 0; i < 3; i++){
      T->SetBranchAddress(a[i], &raw[i]);
      T->SetBranchAddress(b[i], &diag[i]);
      T->SetBranchAddress(c[i], &prop[i]);
    }
    T->SetBranchAddress("Nacc", &Nacc);
    T->SetBranchAddress("fn", &fn);
    for (Long64_t m = 0; m < T->GetEntries(); m++){
      T->GetEntry(m);
      for (int i = 0; i < 3; i++)
        fprintf(o, "%d %lld %d %.17g %.17g %.17g %.17g %.17g\n",
                k, m, i, raw[i], diag[i], prop[i], Nacc, fn);
    }
    f->Close();
  }
  fclose(o);
  printf("wrote %s\n", out);
}
