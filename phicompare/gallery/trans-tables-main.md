# trans tables, study `main`

Written by `plot-transversity_phicompare.ipynb` from `input-main.csv`, Q2 = 2.4 GeV^2, tol = 7.04. Regenerate, do not edit.

## Fits loaded (gallery/input-main.csv)

```
                                                                                                                 file  replicas twin of
entry                                                                                                                                  
world                                                                             ../data_world/out-world_collins.dat       500       -
worldsyst                                                                         ../data_world/out-world_collins.dat       500       -
sbs                                                                                   ../data_sbs/out-sbs_collins.dat       500       -
phifull                                                                      data_phifull/out-enhanced3he_collins.dat       500       -
phifullsyst                                                              data_phifull/out-enhanced3hesyst_collins.dat       500       -
phi4seg24deg_phifullbin_x4counts                    data_phi4seg24deg_phifullbin/out-enhanced3he_collins_x4counts.dat       500       -
phi4seg24deg_phifullbin_x4countssyst            data_phi4seg24deg_phifullbin/out-enhanced3hesyst_collins_x4counts.dat       500       -
phi4seg24degFA_phifullbin_x4counts                data_phi4seg24degFA_phifullbin/out-enhanced3he_collins_x4counts.dat       500       -
phi4seg24degFA_phifullbin_x4countssyst        data_phi4seg24degFA_phifullbin/out-enhanced3hesyst_collins_x4counts.dat       500       -
phi2seg48deg_phifullbin_x4counts                    data_phi2seg48deg_phifullbin/out-enhanced3he_collins_x4counts.dat       500       -
phi2seg48deg_phifullbin_x4countssyst            data_phi2seg48deg_phifullbin/out-enhanced3hesyst_collins_x4counts.dat       500       -
phi4seg24degdiag_phifullbin_x4counts            data_phi4seg24degdiag_phifullbin/out-enhanced3he_collins_x4counts.dat       500       -
phi4seg24degdiag_phifullbin_x4countssyst    data_phi4seg24degdiag_phifullbin/out-enhanced3hesyst_collins_x4counts.dat       500       -
phi4seg24deg2spin_phifullbin_x4counts          data_phi4seg24deg2spin_phifullbin/out-enhanced3he_collins_x4counts.dat       500       -
phi4seg24deg2spin_phifullbin_x4countssyst  data_phi4seg24deg2spin_phifullbin/out-enhanced3hesyst_collins_x4counts.dat       500       -
phi2seg48deg2spin_phifullbin_x4counts          data_phi2seg48deg2spin_phifullbin/out-enhanced3he_collins_x4counts.dat       500       -
phi2seg48deg2spin_phifullbin_x4countssyst  data_phi2seg48deg2spin_phifullbin/out-enhanced3hesyst_collins_x4counts.dat       500       -
```

## Fitted parameters, mean +- std over replicas

```
                                                         Nu                 Nd                 a                 b                  c               kt2            Nu_err            Nd_err             a_err             b_err             c_err           kt2_err                  chi2                 ndof               edm
run                                                                                                                                                                                                                                                                                                                             
world                                      0.4007 +- 0.0125  -0.4511 +- 0.0311  1.0008 +- 0.0537  3.0103 +- 0.3782   0.0000 +- 0.0000  0.2496 +- 0.0224  0.0123 +- 0.0010  0.0313 +- 0.0014  0.0558 +- 0.0010  0.3842 +- 0.0075        nan +- nan  0.0207 +- 0.0006   140.5382 +- 16.0417   141.0000 +- 0.0000  0.0000 +- 0.0000
worldsyst                                  0.4007 +- 0.0125  -0.4511 +- 0.0311  1.0008 +- 0.0537  3.0103 +- 0.3782   0.0000 +- 0.0000  0.2496 +- 0.0224  0.0123 +- 0.0010  0.0313 +- 0.0014  0.0558 +- 0.0010  0.3842 +- 0.0075        nan +- nan  0.0207 +- 0.0006   140.5382 +- 16.0417   141.0000 +- 0.0000  0.0000 +- 0.0000
sbs                                        0.5301 +- 0.3334  -0.5991 +- 0.3811  1.0265 +- 0.0842  2.9069 +- 0.2391  -0.0026 +- 0.6624  0.2506 +- 0.0097  0.0936 +- 0.1250  0.1065 +- 0.1427  0.0345 +- 0.0134  0.1432 +- 0.0814  0.1828 +- 0.1102  0.0123 +- 0.0002   450.6328 +- 30.5383   595.0000 +- 0.0000  0.0005 +- 0.0018
phifull                                    0.4087 +- 0.0658  -0.4597 +- 0.0737  1.0027 +- 0.0264  2.9954 +- 0.0393  -0.0006 +- 0.2103  0.2500 +- 0.0010  0.0089 +- 0.0117  0.0098 +- 0.0132  0.0083 +- 0.0034  0.0299 +- 0.0022  0.0337 +- 0.0525  0.0010 +- 0.0000  1652.8844 +- 56.9147  1800.0000 +- 0.0000  0.0018 +- 0.0088
phifullsyst                                0.4369 +- 0.1528  -0.4911 +- 0.1711  1.0099 +- 0.0538  2.9775 +- 0.0848   0.0143 +- 0.4444  0.2500 +- 0.0022  0.0355 +- 0.0379  0.0395 +- 0.0426  0.0201 +- 0.0108  0.0549 +- 0.0113  0.1420 +- 0.2021  0.0023 +- 0.0000  1653.2022 +- 56.8598  1800.0000 +- 0.0000  0.0018 +- 0.0063
phi4seg24deg_phifullbin_x4counts           0.4213 +- 0.1142  -0.4737 +- 0.1278  1.0058 +- 0.0390  2.9867 +- 0.0891   0.0051 +- 0.3309  0.2500 +- 0.0020  0.0214 +- 0.0245  0.0237 +- 0.0276  0.0176 +- 0.0063  0.0679 +- 0.0062  0.0844 +- 0.1293  0.0021 +- 0.0000  1653.3453 +- 56.7972  1800.0000 +- 0.0000  0.0019 +- 0.0071
phi4seg24deg_phifullbin_x4countssyst       0.4557 +- 0.1915  -0.5123 +- 0.2147  1.0138 +- 0.0589  2.9619 +- 0.1389   0.0075 +- 0.5104  0.2500 +- 0.0028  0.0463 +- 0.0470  0.0517 +- 0.0528  0.0262 +- 0.0112  0.0901 +- 0.0177  0.1800 +- 0.2600  0.0030 +- 0.0000  1653.5931 +- 56.7940  1800.0000 +- 0.0000  0.0022 +- 0.0080
phi4seg24degFA_phifullbin_x4counts         0.4304 +- 0.1311  -0.4838 +- 0.1466  1.0089 +- 0.0470  2.9836 +- 0.0740  -0.0003 +- 0.3824  0.2500 +- 0.0019  0.0274 +- 0.0313  0.0305 +- 0.0352  0.0173 +- 0.0089  0.0501 +- 0.0081  0.1063 +- 0.1592  0.0020 +- 0.0000  1653.0983 +- 56.8291  1800.0000 +- 0.0000  0.0020 +- 0.0081
phi4seg24degFA_phifullbin_x4countssyst     0.4573 +- 0.1916  -0.5139 +- 0.2144  1.0153 +- 0.0634  2.9658 +- 0.1111   0.0088 +- 0.5237  0.2500 +- 0.0028  0.0523 +- 0.0592  0.0582 +- 0.0662  0.0261 +- 0.0153  0.0698 +- 0.0226  0.1901 +- 0.2656  0.0029 +- 0.0000  1653.3759 +- 56.8507  1800.0000 +- 0.0000  0.0013 +- 0.0060
phi2seg48deg_phifullbin_x4counts           0.4768 +- 0.2346  -0.5364 +- 0.2639  1.0165 +- 0.0636  2.9410 +- 0.1972   0.0090 +- 0.5829  0.2498 +- 0.0054  0.0614 +- 0.0645  0.0686 +- 0.0725  0.0327 +- 0.0141  0.1267 +- 0.0292  0.2308 +- 0.3544  0.0057 +- 0.0001  1649.0806 +- 56.5865  1795.0000 +- 0.0000  0.0019 +- 0.0055
phi2seg48deg_phifullbin_x4countssyst       0.4930 +- 0.2642  -0.5548 +- 0.2976  1.0192 +- 0.0688  2.9274 +- 0.2213   0.0094 +- 0.6259  0.2498 +- 0.0059  0.0706 +- 0.0774  0.0790 +- 0.0866  0.0346 +- 0.0150  0.1372 +- 0.0362  0.2332 +- 0.3489  0.0063 +- 0.0001  1649.2045 +- 56.5615  1795.0000 +- 0.0000  0.0020 +- 0.0084
phi4seg24degdiag_phifullbin_x4counts       0.4252 +- 0.1208  -0.4781 +- 0.1351  1.0071 +- 0.0413  2.9853 +- 0.0899   0.0005 +- 0.3496  0.2500 +- 0.0023  0.0236 +- 0.0274  0.0262 +- 0.0308  0.0175 +- 0.0073  0.0638 +- 0.0075  0.0932 +- 0.1477  0.0024 +- 0.0000  1653.2691 +- 56.8758  1800.0000 +- 0.0000  0.0016 +- 0.0055
phi4seg24degdiag_phifullbin_x4countssyst   0.4516 +- 0.1819  -0.5077 +- 0.2039  1.0132 +- 0.0584  2.9663 +- 0.1256   0.0106 +- 0.5041  0.2500 +- 0.0031  0.0466 +- 0.0484  0.0519 +- 0.0544  0.0257 +- 0.0126  0.0822 +- 0.0174  0.1833 +- 0.2678  0.0033 +- 0.0001  1653.5028 +- 56.8570  1800.0000 +- 0.0000  0.0017 +- 0.0050
phi4seg24deg2spin_phifullbin_x4counts      0.4205 +- 0.1100  -0.4728 +- 0.1227  1.0060 +- 0.0369  2.9886 +- 0.0905   0.0011 +- 0.3155  0.2500 +- 0.0020  0.0201 +- 0.0230  0.0222 +- 0.0258  0.0173 +- 0.0060  0.0677 +- 0.0063  0.0799 +- 0.1299  0.0021 +- 0.0000  1652.3106 +- 56.6688  1799.0000 +- 0.0000  0.0016 +- 0.0064
phi4seg24deg2spin_phifullbin_x4countssyst  0.4528 +- 0.1877  -0.5089 +- 0.2100  1.0132 +- 0.0577  2.9645 +- 0.1387   0.0143 +- 0.5099  0.2499 +- 0.0028  0.0497 +- 0.0528  0.0553 +- 0.0592  0.0273 +- 0.0131  0.0909 +- 0.0193  0.1914 +- 0.2788  0.0030 +- 0.0000  1652.5830 +- 56.6709  1799.0000 +- 0.0000  0.0017 +- 0.0055
phi2seg48deg2spin_phifullbin_x4counts      0.4303 +- 0.1332  -0.4838 +- 0.1488  1.0083 +- 0.0445  2.9823 +- 0.0919  -0.0028 +- 0.3719  0.2498 +- 0.0030  0.0243 +- 0.0275  0.0270 +- 0.0309  0.0180 +- 0.0072  0.0608 +- 0.0072  0.0959 +- 0.1485  0.0030 +- 0.0001  1650.2132 +- 56.8185  1797.0000 +- 0.0000  0.0021 +- 0.0068
phi2seg48deg2spin_phifullbin_x4countssyst  0.4575 +- 0.2004  -0.5143 +- 0.2242  1.0138 +- 0.0622  2.9617 +- 0.1329   0.0167 +- 0.5296  0.2497 +- 0.0040  0.0496 +- 0.0510  0.0553 +- 0.0571  0.0265 +- 0.0127  0.0805 +- 0.0192  0.1928 +- 0.2753  0.0040 +- 0.0001  1650.4412 +- 56.7838  1797.0000 +- 0.0000  0.0018 +- 0.0060
```

## Error(world) / Error at representative x (larger = better)

```
                                                       x=0.05  x=0.1  x=0.2  x=0.3  x=0.4  x=0.5  x=0.6
variant   run                                   quark                                                  
stat      sbs                                   u        3.67   2.92   2.35   2.94   3.96   4.18   3.80
                                                d        3.34   3.22   3.74   5.00   6.34   5.50   4.30
          phifull                               u        4.02   6.17   7.00  11.44  15.99  15.78  14.58
                                                d       13.26  32.46  32.80  28.93  22.10  17.41  15.07
          phi4seg24deg_phifullbin_x4counts      u        2.82   3.51   3.53   5.70   7.53   7.14   6.50
                                                d        7.16  15.39  17.74  13.22   9.29   7.38   6.47
          phi4seg24degFA_phifullbin_x4counts    u        2.93   3.64   3.71   6.16  10.11  10.63   9.46
                                                d        7.70  15.73  18.23  16.25  13.74  11.11   9.41
          phi2seg48deg_phifullbin_x4counts      u        3.43   2.91   2.38   3.38   4.07   3.74   3.32
                                                d        4.99   6.41   5.86   5.29   4.56   3.83   3.33
          phi4seg24degdiag_phifullbin_x4counts  u        2.90   3.59   3.51   5.64   7.71   7.38   6.67
                                                d        7.72  14.99  14.15  12.40   9.71   7.77   6.74
          phi4seg24deg2spin_phifullbin_x4counts u        2.82   3.57   3.64   5.84   7.44   6.97   6.34
                                                d        7.21  15.38  17.34  13.04   9.17   7.27   6.36
          phi2seg48deg2spin_phifullbin_x4counts u        2.98   3.63   3.41   5.43   8.00   7.91   7.08
                                                d        7.21  11.81  10.71  10.32   9.66   8.25   7.15
stat+syst phifull                               u        2.96   3.53   3.44   5.65   9.51  10.03   8.77
                                                d        7.34  13.30  14.51  14.49  13.35  10.72   8.84
          phi4seg24deg_phifullbin_x4counts      u        3.05   3.05   2.74   4.37   6.03   5.61   4.89
                                                d        5.80  10.21  11.71  10.17   7.58   5.84   4.90
          phi4seg24degFA_phifullbin_x4counts    u        3.09   3.14   2.88   4.62   7.84   8.40   7.26
                                                d        6.11  10.38  11.98  11.68  10.89   8.86   7.26
          phi2seg48deg_phifullbin_x4counts      u        3.63   2.91   2.31   3.21   3.83   3.51   3.09
                                                d        4.69   5.75   5.39   4.98   4.33   3.62   3.12
          phi4seg24degdiag_phifullbin_x4counts  u        2.99   3.14   2.83   4.50   6.51   6.23   5.45
                                                d        6.21  10.46  10.60   9.92   8.25   6.53   5.49
          phi4seg24deg2spin_phifullbin_x4counts u        3.07   3.04   2.80   4.47   6.02   5.51   4.81
                                                d        5.83  10.18  11.49  10.05   7.51   5.78   4.85
          phi2seg48deg2spin_phifullbin_x4counts u        3.10   3.08   2.69   4.18   6.40   6.44   5.62
                                                d        5.83   8.57   8.18   7.97   7.76   6.68   5.66
```

## Tensor charge gT, full and truncated (0.05 < x < 0.6)

```
                                                      gT(u)              gT(d)           gT(u-d)    gT trunc (u-d)
run                                                                                                               
world                                      0.5475 +- 0.1175  -0.3766 +- 0.1715  0.9241 +- 0.2111  0.7654 +- 0.1701
worldsyst                                  0.5475 +- 0.1175  -0.3766 +- 0.1715  0.9241 +- 0.2111  0.7654 +- 0.1701
sbs                                        0.5462 +- 0.0409  -0.3760 +- 0.0417  0.9222 +- 0.0417  0.7656 +- 0.0395
phifull                                    0.5470 +- 0.0158  -0.3760 +- 0.0098  0.9230 +- 0.0200  0.7651 +- 0.0107
phifullsyst                                0.5469 +- 0.0239  -0.3757 +- 0.0181  0.9225 +- 0.0274  0.7652 +- 0.0195
phi4seg24deg_phifullbin_x4counts           0.5470 +- 0.0248  -0.3759 +- 0.0183  0.9229 +- 0.0298  0.7652 +- 0.0197
phi4seg24deg_phifullbin_x4countssyst       0.5469 +- 0.0268  -0.3756 +- 0.0228  0.9225 +- 0.0304  0.7654 +- 0.0246
phi4seg24degFA_phifullbin_x4counts         0.5468 +- 0.0230  -0.3757 +- 0.0171  0.9225 +- 0.0262  0.7652 +- 0.0174
phi4seg24degFA_phifullbin_x4countssyst     0.5467 +- 0.0256  -0.3754 +- 0.0221  0.9222 +- 0.0283  0.7653 +- 0.0225
phi2seg48deg_phifullbin_x4counts           0.5466 +- 0.0319  -0.3756 +- 0.0317  0.9221 +- 0.0490  0.7650 +- 0.0426
phi2seg48deg_phifullbin_x4countssyst       0.5465 +- 0.0329  -0.3755 +- 0.0336  0.9220 +- 0.0509  0.7650 +- 0.0450
phi4seg24degdiag_phifullbin_x4counts       0.5469 +- 0.0244  -0.3758 +- 0.0173  0.9228 +- 0.0293  0.7652 +- 0.0216
phi4seg24degdiag_phifullbin_x4countssyst   0.5468 +- 0.0266  -0.3756 +- 0.0219  0.9224 +- 0.0316  0.7653 +- 0.0259
phi4seg24deg2spin_phifullbin_x4counts      0.5469 +- 0.0247  -0.3758 +- 0.0184  0.9227 +- 0.0299  0.7651 +- 0.0193
phi4seg24deg2spin_phifullbin_x4countssyst  0.5468 +- 0.0267  -0.3755 +- 0.0232  0.9223 +- 0.0303  0.7652 +- 0.0239
phi2seg48deg2spin_phifullbin_x4counts      0.5467 +- 0.0243  -0.3757 +- 0.0196  0.9224 +- 0.0333  0.7649 +- 0.0261
phi2seg48deg2spin_phifullbin_x4countssyst  0.5465 +- 0.0275  -0.3754 +- 0.0249  0.9220 +- 0.0369  0.7649 +- 0.0322
```

## Truncated gT(u-d): error and world/this

```
--- stat ---
  world                                E(gT u-d) = 0.1701   world/this =   1.00x
  sbs                                  E(gT u-d) = 0.0395   world/this =   4.31x
  phifull                              E(gT u-d) = 0.0107   world/this =  15.86x
  phi4seg24deg_phifullbin_x4counts     E(gT u-d) = 0.0197   world/this =   8.62x
  phi4seg24degFA_phifullbin_x4counts   E(gT u-d) = 0.0174   world/this =   9.79x
  phi2seg48deg_phifullbin_x4counts     E(gT u-d) = 0.0426   world/this =   3.99x
  phi4seg24degdiag_phifullbin_x4counts E(gT u-d) = 0.0216   world/this =   7.89x
  phi4seg24deg2spin_phifullbin_x4counts E(gT u-d) = 0.0193   world/this =   8.80x
  phi2seg48deg2spin_phifullbin_x4counts E(gT u-d) = 0.0261   world/this =   6.51x
--- stat+syst ---
  world                                E(gT u-d) = 0.1701   world/this =   1.00x
  phifull                              E(gT u-d) = 0.0195   world/this =   8.71x
  phi4seg24deg_phifullbin_x4counts     E(gT u-d) = 0.0246   world/this =   6.90x
  phi4seg24degFA_phifullbin_x4counts   E(gT u-d) = 0.0225   world/this =   7.55x
  phi2seg48deg_phifullbin_x4counts     E(gT u-d) = 0.0450   world/this =   3.78x
  phi4seg24degdiag_phifullbin_x4counts E(gT u-d) = 0.0259   world/this =   6.57x
  phi4seg24deg2spin_phifullbin_x4counts E(gT u-d) = 0.0239   world/this =   7.11x
  phi2seg48deg2spin_phifullbin_x4counts E(gT u-d) = 0.0322   world/this =   5.28x
```
