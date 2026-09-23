# trans tables, study `r1lt0.3`

Written by `plot-transversity_phicompare.ipynb` from `input-r1lt0.3.csv`, Q2 = 2.4 GeV^2, tol = 7.04. Regenerate, do not edit.

## Fits loaded (gallery/input-r1lt0.3.csv)

```
                                                                                                                       file  replicas                           twin of
entry                                                                                                                                                                  
world                                                                                   ../data_world/out-world_collins.dat       500                                 -
worldsyst                                                                               ../data_world/out-world_collins.dat       500                                 -
sbs                                                                                         ../data_sbs/out-sbs_collins.dat       500                                 -
sbs_r1lt0.3                                                                         ../data_sbs/out-sbs_collins_r1lt0.3.dat       500                               sbs
phifull                                                                            data_phifull/out-enhanced3he_collins.dat       500                                 -
phifullsyst                                                                    data_phifull/out-enhanced3hesyst_collins.dat       500                                 -
phifull_r1lt0.3                                                            data_phifull/out-enhanced3he_collins_r1lt0.3.dat       500                           phifull
phifull_r1lt0.3syst                                                    data_phifull/out-enhanced3hesyst_collins_r1lt0.3.dat       500                           phifull
phi4seg24deg_phifullbin_x4counts                          data_phi4seg24deg_phifullbin/out-enhanced3he_collins_x4counts.dat       500                                 -
phi4seg24deg_phifullbin_x4countssyst                  data_phi4seg24deg_phifullbin/out-enhanced3hesyst_collins_x4counts.dat       500                                 -
phi4seg24deg_phifullbin_r1lt0.3_x4counts          data_phi4seg24deg_phifullbin/out-enhanced3he_collins_r1lt0.3_x4counts.dat       500  phi4seg24deg_phifullbin_x4counts
phi4seg24deg_phifullbin_r1lt0.3_x4countssyst  data_phi4seg24deg_phifullbin/out-enhanced3hesyst_collins_r1lt0.3_x4counts.dat       500  phi4seg24deg_phifullbin_x4counts
```

## Fitted parameters, mean +- std over replicas

```
                                                            Nu                 Nd                 a                 b                  c               kt2            Nu_err            Nd_err             a_err             b_err             c_err           kt2_err                  chi2                 ndof               edm
run                                                                                                                                                                                                                                                                                                                                
world                                         0.4007 +- 0.0125  -0.4511 +- 0.0311  1.0008 +- 0.0537  3.0103 +- 0.3782   0.0000 +- 0.0000  0.2496 +- 0.0224  0.0123 +- 0.0010  0.0313 +- 0.0014  0.0558 +- 0.0010  0.3842 +- 0.0075        nan +- nan  0.0207 +- 0.0006   140.5382 +- 16.0417   141.0000 +- 0.0000  0.0000 +- 0.0000
worldsyst                                     0.4007 +- 0.0125  -0.4511 +- 0.0311  1.0008 +- 0.0537  3.0103 +- 0.3782   0.0000 +- 0.0000  0.2496 +- 0.0224  0.0123 +- 0.0010  0.0313 +- 0.0014  0.0558 +- 0.0010  0.3842 +- 0.0075        nan +- nan  0.0207 +- 0.0006   140.5382 +- 16.0417   141.0000 +- 0.0000  0.0000 +- 0.0000
sbs                                           0.5301 +- 0.3334  -0.5991 +- 0.3811  1.0265 +- 0.0842  2.9069 +- 0.2391  -0.0026 +- 0.6624  0.2506 +- 0.0097  0.0936 +- 0.1250  0.1065 +- 0.1427  0.0345 +- 0.0134  0.1432 +- 0.0814  0.1828 +- 0.1102  0.0123 +- 0.0002   450.6328 +- 30.5383   595.0000 +- 0.0000  0.0005 +- 0.0018
sbs_r1lt0.3                                   0.5368 +- 0.3401  -0.6045 +- 0.3821  1.0282 +- 0.0795  2.9042 +- 0.2689  -0.0142 +- 0.6719  0.2508 +- 0.0100  0.0992 +- 0.1433  0.1140 +- 0.1639  0.0363 +- 0.0100  0.1611 +- 0.1018  0.2027 +- 0.1401  0.0159 +- 0.0003   315.8054 +- 25.2782   460.0000 +- 0.0000  0.0003 +- 0.0010
phifull                                       0.4087 +- 0.0658  -0.4597 +- 0.0737  1.0027 +- 0.0264  2.9954 +- 0.0393  -0.0006 +- 0.2103  0.2500 +- 0.0010  0.0089 +- 0.0117  0.0098 +- 0.0132  0.0083 +- 0.0034  0.0299 +- 0.0022  0.0337 +- 0.0525  0.0010 +- 0.0000  1652.8844 +- 56.9147  1800.0000 +- 0.0000  0.0018 +- 0.0088
phifullsyst                                   0.4369 +- 0.1528  -0.4911 +- 0.1711  1.0099 +- 0.0538  2.9775 +- 0.0848   0.0143 +- 0.4444  0.2500 +- 0.0022  0.0355 +- 0.0379  0.0395 +- 0.0426  0.0201 +- 0.0108  0.0549 +- 0.0113  0.1420 +- 0.2021  0.0023 +- 0.0000  1653.2022 +- 56.8598  1800.0000 +- 0.0000  0.0018 +- 0.0063
phifull_r1lt0.3                               0.4244 +- 0.1195  -0.4775 +- 0.1340  1.0064 +- 0.0438  2.9841 +- 0.0648   0.0054 +- 0.3602  0.2498 +- 0.0028  0.0231 +- 0.0254  0.0258 +- 0.0287  0.0162 +- 0.0073  0.0469 +- 0.0054  0.0939 +- 0.1386  0.0028 +- 0.0000   922.1828 +- 44.6832  1068.0000 +- 0.0000  0.0021 +- 0.0074
phifull_r1lt0.3syst                           0.4719 +- 0.2108  -0.5311 +- 0.2374  1.0183 +- 0.0676  2.9537 +- 0.1224  -0.0018 +- 0.5689  0.2497 +- 0.0050  0.0591 +- 0.0577  0.0662 +- 0.0649  0.0292 +- 0.0150  0.0754 +- 0.0210  0.2190 +- 0.2995  0.0051 +- 0.0001   922.6043 +- 44.6524  1068.0000 +- 0.0000  0.0028 +- 0.0252
phi4seg24deg_phifullbin_x4counts              0.4213 +- 0.1142  -0.4737 +- 0.1278  1.0058 +- 0.0390  2.9867 +- 0.0891   0.0051 +- 0.3309  0.2500 +- 0.0020  0.0214 +- 0.0245  0.0237 +- 0.0276  0.0176 +- 0.0063  0.0679 +- 0.0062  0.0844 +- 0.1293  0.0021 +- 0.0000  1653.3453 +- 56.7972  1800.0000 +- 0.0000  0.0019 +- 0.0071
phi4seg24deg_phifullbin_x4countssyst          0.4557 +- 0.1915  -0.5123 +- 0.2147  1.0138 +- 0.0589  2.9619 +- 0.1389   0.0075 +- 0.5104  0.2500 +- 0.0028  0.0463 +- 0.0470  0.0517 +- 0.0528  0.0262 +- 0.0112  0.0901 +- 0.0177  0.1800 +- 0.2600  0.0030 +- 0.0000  1653.5931 +- 56.7940  1800.0000 +- 0.0000  0.0022 +- 0.0080
phi4seg24deg_phifullbin_r1lt0.3_x4counts      0.4802 +- 0.2403  -0.5405 +- 0.2716  1.0173 +- 0.0671  2.9367 +- 0.1798   0.0114 +- 0.5954  0.2497 +- 0.0056  0.0668 +- 0.0748  0.0748 +- 0.0842  0.0338 +- 0.0157  0.1171 +- 0.0334  0.2228 +- 0.3452  0.0059 +- 0.0001   854.3845 +- 42.5031   999.0000 +- 0.0000  0.0016 +- 0.0051
phi4seg24deg_phifullbin_r1lt0.3_x4countssyst  0.4999 +- 0.2740  -0.5631 +- 0.3104  1.0210 +- 0.0728  2.9219 +- 0.2067   0.0043 +- 0.6351  0.2498 +- 0.0068  0.0712 +- 0.0842  0.0802 +- 0.0954  0.0334 +- 0.0134  0.1307 +- 0.0442  0.1792 +- 0.2687  0.0074 +- 0.0002   854.6060 +- 42.5183   999.0000 +- 0.0000  0.0016 +- 0.0053
```

## Error(world) / Error at representative x (larger = better)

```
                                                          x=0.05  x=0.1  x=0.2  x=0.3  x=0.4  x=0.5  x=0.6
variant   run                                      quark                                                  
stat      sbs                                      u        3.67   2.92   2.35   2.94   3.96   4.18   3.80
                                                   d        3.34   3.22   3.74   5.00   6.34   5.50   4.30
          sbs_r1lt0.3                              u        3.24   3.03   2.32   2.88   3.67   3.61   3.20
                                                   d        2.72   2.50   2.56   3.22   4.54   4.72   3.81
          phifull                                  u        4.02   6.17   7.00  11.44  15.99  15.78  14.58
                                                   d       13.26  32.46  32.80  28.93  22.10  17.41  15.07
          phifull_r1lt0.3                          u        3.12   3.88   3.82   6.30  11.05  12.38  11.06
                                                   d        7.85  11.54  11.78  13.23  14.96  13.40  11.28
          phi4seg24deg_phifullbin_x4counts         u        2.82   3.51   3.53   5.70   7.53   7.14   6.50
                                                   d        7.16  15.39  17.74  13.22   9.29   7.38   6.47
          phi4seg24deg_phifullbin_r1lt0.3_x4counts u        4.14   3.07   2.26   3.22   4.71   4.75   4.17
                                                   d        4.64   5.32   4.97   4.94   5.08   4.68   4.09
stat+syst phifull                                  u        2.96   3.53   3.44   5.65   9.51  10.03   8.77
                                                   d        7.34  13.30  14.51  14.49  13.35  10.72   8.84
          phifull_r1lt0.3                          u        3.44   3.01   2.53   3.91   7.11   8.56   7.37
                                                   d        5.00   5.95   6.22   7.07   8.94   8.96   7.41
          phi4seg24deg_phifullbin_x4counts         u        3.05   3.05   2.74   4.37   6.03   5.61   4.89
                                                   d        5.80  10.21  11.71  10.17   7.58   5.84   4.90
          phi4seg24deg_phifullbin_r1lt0.3_x4counts u        4.59   3.13   2.21   3.01   4.29   4.36   3.83
                                                   d        3.97   4.23   4.04   4.13   4.44   4.26   3.75
```

## Error(twin) / Error(base row) at representative x

```
                                                          x=0.05  x=0.1  x=0.2  x=0.3  x=0.4  x=0.5  x=0.6
variant   twin                                     quark                                                  
stat      sbs_r1lt0.3                              u        1.13   0.96   1.01   1.02   1.08   1.16   1.19
                                                   d        1.23   1.29   1.46   1.56   1.40   1.16   1.13
          phifull_r1lt0.3                          u        1.29   1.59   1.83   1.82   1.45   1.27   1.32
                                                   d        1.69   2.81   2.78   2.19   1.48   1.30   1.34
          phi4seg24deg_phifullbin_r1lt0.3_x4counts u        0.68   1.15   1.56   1.77   1.60   1.50   1.56
                                                   d        1.54   2.89   3.57   2.68   1.83   1.58   1.58
stat+syst phifull_r1lt0.3                          u        0.86   1.17   1.36   1.45   1.34   1.17   1.19
                                                   d        1.47   2.23   2.33   2.05   1.49   1.20   1.19
          phi4seg24deg_phifullbin_r1lt0.3_x4counts u        0.66   0.97   1.24   1.45   1.41   1.29   1.28
                                                   d        1.46   2.42   2.90   2.46   1.71   1.37   1.30
```

## Tensor charge gT, full and truncated (0.05 < x < 0.6)

```
                                                         gT(u)              gT(d)           gT(u-d)    gT trunc (u-d)
run                                                                                                                  
world                                         0.5475 +- 0.1175  -0.3766 +- 0.1715  0.9241 +- 0.2111  0.7654 +- 0.1701
worldsyst                                     0.5475 +- 0.1175  -0.3766 +- 0.1715  0.9241 +- 0.2111  0.7654 +- 0.1701
sbs                                           0.5462 +- 0.0409  -0.3760 +- 0.0417  0.9222 +- 0.0417  0.7656 +- 0.0395
sbs_r1lt0.3                                   0.5462 +- 0.0425  -0.3761 +- 0.0599  0.9223 +- 0.0593  0.7658 +- 0.0522
phifull                                       0.5470 +- 0.0158  -0.3760 +- 0.0098  0.9230 +- 0.0200  0.7651 +- 0.0107
phifullsyst                                   0.5469 +- 0.0239  -0.3757 +- 0.0181  0.9225 +- 0.0274  0.7652 +- 0.0195
phifull_r1lt0.3                               0.5466 +- 0.0221  -0.3759 +- 0.0169  0.9225 +- 0.0298  0.7649 +- 0.0238
phifull_r1lt0.3syst                           0.5463 +- 0.0282  -0.3755 +- 0.0283  0.9218 +- 0.0389  0.7649 +- 0.0371
phi4seg24deg_phifullbin_x4counts              0.5470 +- 0.0248  -0.3759 +- 0.0183  0.9229 +- 0.0298  0.7652 +- 0.0197
phi4seg24deg_phifullbin_x4countssyst          0.5469 +- 0.0268  -0.3756 +- 0.0228  0.9225 +- 0.0304  0.7654 +- 0.0246
phi4seg24deg_phifullbin_r1lt0.3_x4counts      0.5467 +- 0.0318  -0.3755 +- 0.0337  0.9222 +- 0.0491  0.7652 +- 0.0464
phi4seg24deg_phifullbin_r1lt0.3_x4countssyst  0.5466 +- 0.0341  -0.3755 +- 0.0407  0.9221 +- 0.0576  0.7652 +- 0.0528
```

## Truncated gT(u-d): error and world/this

```
--- stat ---
  world                                E(gT u-d) = 0.1701   world/this =   1.00x
  sbs                                  E(gT u-d) = 0.0395   world/this =   4.31x
  sbs_r1lt0.3                          E(gT u-d) = 0.0522   world/this =   3.26x   twin/base =  1.32
  phifull                              E(gT u-d) = 0.0107   world/this =  15.86x
  phifull_r1lt0.3                      E(gT u-d) = 0.0238   world/this =   7.15x   twin/base =  2.22
  phi4seg24deg_phifullbin_x4counts     E(gT u-d) = 0.0197   world/this =   8.62x
  phi4seg24deg_phifullbin_r1lt0.3_x4counts E(gT u-d) = 0.0464   world/this =   3.67x   twin/base =  2.35
--- stat+syst ---
  world                                E(gT u-d) = 0.1701   world/this =   1.00x
  phifull                              E(gT u-d) = 0.0195   world/this =   8.71x
  phifull_r1lt0.3                      E(gT u-d) = 0.0371   world/this =   4.59x   twin/base =  1.90
  phi4seg24deg_phifullbin_x4counts     E(gT u-d) = 0.0246   world/this =   6.90x
  phi4seg24deg_phifullbin_r1lt0.3_x4counts E(gT u-d) = 0.0528   world/this =   3.22x   twin/base =  2.14
```
