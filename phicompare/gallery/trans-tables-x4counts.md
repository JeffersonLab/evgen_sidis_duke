# trans tables, study `x4counts`

Written by `plot-transversity_phicompare.ipynb` from `input-x4counts.csv`, Q2 = 2.4 GeV^2, tol = 7.04. Regenerate, do not edit.

## Fits loaded (gallery/input-x4counts.csv)

```
                                                                                                         file  replicas                   twin of
entry                                                                                                                                            
world                                                                     ../data_world/out-world_collins.dat       500                         -
worldsyst                                                                 ../data_world/out-world_collins.dat       500                         -
phifull                                                              data_phifull/out-enhanced3he_collins.dat       500                         -
phifullsyst                                                      data_phifull/out-enhanced3hesyst_collins.dat       500                         -
phi4seg24deg_phifullbin                              data_phi4seg24deg_phifullbin/out-enhanced3he_collins.dat       500                         -
phi4seg24deg_phifullbinsyst                      data_phi4seg24deg_phifullbin/out-enhanced3hesyst_collins.dat       500                         -
phi4seg24deg_phifullbin_x4counts            data_phi4seg24deg_phifullbin/out-enhanced3he_collins_x4counts.dat       500   phi4seg24deg_phifullbin
phi4seg24deg_phifullbin_x4countssyst    data_phi4seg24deg_phifullbin/out-enhanced3hesyst_collins_x4counts.dat       500   phi4seg24deg_phifullbin
phi4seg24deg                                                    data_phi4seg24deg/out-enhanced3he_collins.dat       500                         -
phi4seg24degsyst                                            data_phi4seg24deg/out-enhanced3hesyst_collins.dat       500                         -
phi4seg24deg_x4counts                                  data_phi4seg24deg/out-enhanced3he_collins_x4counts.dat       500              phi4seg24deg
phi4seg24deg_x4countssyst                          data_phi4seg24deg/out-enhanced3hesyst_collins_x4counts.dat       500              phi4seg24deg
phi4seg24deg_countbin800                            data_phi4seg24deg_countbin800/out-enhanced3he_collins.dat       500                         -
phi4seg24deg_countbin800syst                    data_phi4seg24deg_countbin800/out-enhanced3hesyst_collins.dat       500                         -
phi4seg24deg_countbin800_x4counts          data_phi4seg24deg_countbin800/out-enhanced3he_collins_x4counts.dat       500  phi4seg24deg_countbin800
phi4seg24deg_countbin800_x4countssyst  data_phi4seg24deg_countbin800/out-enhanced3hesyst_collins_x4counts.dat       500  phi4seg24deg_countbin800
```

## Fitted parameters, mean +- std over replicas

```
                                                     Nu                 Nd                 a                 b                  c               kt2            Nu_err            Nd_err             a_err             b_err             c_err           kt2_err                  chi2                 ndof               edm
run                                                                                                                                                                                                                                                                                                                         
world                                  0.4007 +- 0.0125  -0.4511 +- 0.0311  1.0008 +- 0.0537  3.0103 +- 0.3782   0.0000 +- 0.0000  0.2496 +- 0.0224  0.0123 +- 0.0010  0.0313 +- 0.0014  0.0558 +- 0.0010  0.3842 +- 0.0075        nan +- nan  0.0207 +- 0.0006   140.5382 +- 16.0417   141.0000 +- 0.0000  0.0000 +- 0.0000
worldsyst                              0.4007 +- 0.0125  -0.4511 +- 0.0311  1.0008 +- 0.0537  3.0103 +- 0.3782   0.0000 +- 0.0000  0.2496 +- 0.0224  0.0123 +- 0.0010  0.0313 +- 0.0014  0.0558 +- 0.0010  0.3842 +- 0.0075        nan +- nan  0.0207 +- 0.0006   140.5382 +- 16.0417   141.0000 +- 0.0000  0.0000 +- 0.0000
phifull                                0.4087 +- 0.0658  -0.4597 +- 0.0737  1.0027 +- 0.0264  2.9954 +- 0.0393  -0.0006 +- 0.2103  0.2500 +- 0.0010  0.0089 +- 0.0117  0.0098 +- 0.0132  0.0083 +- 0.0034  0.0299 +- 0.0022  0.0337 +- 0.0525  0.0010 +- 0.0000  1652.8844 +- 56.9147  1800.0000 +- 0.0000  0.0018 +- 0.0088
phifullsyst                            0.4369 +- 0.1528  -0.4911 +- 0.1711  1.0099 +- 0.0538  2.9775 +- 0.0848   0.0143 +- 0.4444  0.2500 +- 0.0022  0.0355 +- 0.0379  0.0395 +- 0.0426  0.0201 +- 0.0108  0.0549 +- 0.0113  0.1420 +- 0.2021  0.0023 +- 0.0000  1653.2022 +- 56.8598  1800.0000 +- 0.0000  0.0018 +- 0.0063
phi4seg24deg_phifullbin                0.4605 +- 0.2095  -0.5181 +- 0.2363  1.0133 +- 0.0589  2.9528 +- 0.1810   0.0242 +- 0.5495  0.2500 +- 0.0038  0.0550 +- 0.0555  0.0614 +- 0.0624  0.0319 +- 0.0126  0.1245 +- 0.0215  0.2209 +- 0.3270  0.0041 +- 0.0001  1653.9528 +- 56.8292  1800.0000 +- 0.0000  0.0018 +- 0.0057
phi4seg24deg_phifullbinsyst            0.4802 +- 0.2483  -0.5405 +- 0.2808  1.0166 +- 0.0660  2.9356 +- 0.2143   0.0272 +- 0.6107  0.2500 +- 0.0043  0.0700 +- 0.0747  0.0784 +- 0.0840  0.0353 +- 0.0147  0.1399 +- 0.0345  0.2473 +- 0.3657  0.0047 +- 0.0001  1654.0919 +- 56.8278  1800.0000 +- 0.0000  0.0016 +- 0.0043
phi4seg24deg_phifullbin_x4counts       0.4213 +- 0.1142  -0.4737 +- 0.1278  1.0058 +- 0.0390  2.9867 +- 0.0891   0.0051 +- 0.3309  0.2500 +- 0.0020  0.0214 +- 0.0245  0.0237 +- 0.0276  0.0176 +- 0.0063  0.0679 +- 0.0062  0.0844 +- 0.1293  0.0021 +- 0.0000  1653.3453 +- 56.7972  1800.0000 +- 0.0000  0.0019 +- 0.0071
phi4seg24deg_phifullbin_x4countssyst   0.4557 +- 0.1915  -0.5123 +- 0.2147  1.0138 +- 0.0589  2.9619 +- 0.1389   0.0075 +- 0.5104  0.2500 +- 0.0028  0.0463 +- 0.0470  0.0517 +- 0.0528  0.0262 +- 0.0112  0.0901 +- 0.0177  0.1800 +- 0.2600  0.0030 +- 0.0000  1653.5931 +- 56.7940  1800.0000 +- 0.0000  0.0022 +- 0.0080
phi4seg24deg                           0.4420 +- 0.1737  -0.4970 +- 0.1956  1.0093 +- 0.0485  2.9667 +- 0.1661   0.0212 +- 0.4712  0.2502 +- 0.0044  0.0413 +- 0.0447  0.0459 +- 0.0501  0.0288 +- 0.0107  0.1150 +- 0.0153  0.1716 +- 0.2627  0.0044 +- 0.0001   164.3005 +- 17.5198   309.0000 +- 0.0000  0.0017 +- 0.0050
phi4seg24degsyst                       0.5103 +- 0.3105  -0.5745 +- 0.3512  1.0197 +- 0.0747  2.9054 +- 0.2754   0.0381 +- 0.6804  0.2501 +- 0.0077  0.0851 +- 0.1089  0.0958 +- 0.1230  0.0368 +- 0.0115  0.1758 +- 0.0606  0.1673 +- 0.1533  0.0086 +- 0.0002   164.9924 +- 17.6058   309.0000 +- 0.0000  0.0011 +- 0.0031
phi4seg24deg_x4counts                  0.4092 +- 0.0785  -0.4601 +- 0.0875  1.0024 +- 0.0269  2.9937 +- 0.0816   0.0086 +- 0.2416  0.2501 +- 0.0023  0.0141 +- 0.0165  0.0155 +- 0.0185  0.0159 +- 0.0046  0.0639 +- 0.0038  0.0585 +- 0.1002  0.0022 +- 0.0000   163.7788 +- 17.4951   309.0000 +- 0.0000  0.0013 +- 0.0077
phi4seg24deg_x4countssyst              0.4950 +- 0.2934  -0.5572 +- 0.3315  1.0175 +- 0.0770  2.9216 +- 0.2284   0.0765 +- 0.6968  0.2501 +- 0.0070  0.0830 +- 0.1069  0.0934 +- 0.1212  0.0358 +- 0.0162  0.1445 +- 0.0613  0.2011 +- 0.2551  0.0076 +- 0.0002   164.7636 +- 17.5909   309.0000 +- 0.0000  0.0010 +- 0.0028
phi4seg24deg_countbin800               0.4566 +- 0.2075  -0.5135 +- 0.2334  1.0132 +- 0.0595  2.9616 +- 0.1741   0.0311 +- 0.5412  0.2499 +- 0.0038  0.0528 +- 0.0530  0.0588 +- 0.0595  0.0307 +- 0.0121  0.1187 +- 0.0210  0.2166 +- 0.3212  0.0039 +- 0.0001   801.3310 +- 41.6603   946.0000 +- 0.0000  0.0018 +- 0.0052
phi4seg24deg_countbin800syst           0.4860 +- 0.2575  -0.5468 +- 0.2905  1.0187 +- 0.0682  2.9368 +- 0.2219   0.0204 +- 0.6164  0.2498 +- 0.0048  0.0682 +- 0.0755  0.0763 +- 0.0850  0.0344 +- 0.0139  0.1452 +- 0.0362  0.2183 +- 0.3412  0.0049 +- 0.0001   801.5361 +- 41.6812   946.0000 +- 0.0000  0.0018 +- 0.0052
phi4seg24deg_countbin800_x4counts      0.4241 +- 0.1243  -0.4769 +- 0.1389  1.0072 +- 0.0429  2.9885 +- 0.0889   0.0089 +- 0.3560  0.2500 +- 0.0020  0.0230 +- 0.0249  0.0255 +- 0.0280  0.0176 +- 0.0069  0.0647 +- 0.0063  0.0959 +- 0.1481  0.0020 +- 0.0000   800.7769 +- 41.6594   946.0000 +- 0.0000  0.0028 +- 0.0108
phi4seg24deg_countbin800_x4countssyst  0.4633 +- 0.2160  -0.5207 +- 0.2421  1.0150 +- 0.0633  2.9570 +- 0.1656   0.0234 +- 0.5542  0.2498 +- 0.0034  0.0538 +- 0.0544  0.0600 +- 0.0609  0.0291 +- 0.0127  0.1058 +- 0.0227  0.2143 +- 0.3187  0.0034 +- 0.0001   801.1275 +- 41.6626   946.0000 +- 0.0000  0.0019 +- 0.0055
```

## Error(world) / Error at representative x (larger = better)

```
                                                   x=0.05  x=0.1  x=0.2  x=0.3  x=0.4  x=0.5  x=0.6
variant   run                               quark                                                  
stat      phifull                           u        4.02   6.17   7.00  11.44  15.99  15.78  14.58
                                            d       13.26  32.46  32.80  28.93  22.10  17.41  15.07
          phi4seg24deg_phifullbin           u        3.30   2.83   2.44   3.57   4.19   3.81   3.40
                                            d        5.12   8.65  10.45   7.51   5.07   3.95   3.39
          phi4seg24deg_phifullbin_x4counts  u        2.82   3.51   3.53   5.70   7.53   7.14   6.50
                                            d        7.16  15.39  17.74  13.22   9.29   7.38   6.47
          phi4seg24deg                      u        3.35   2.87   2.46   3.57   4.14   3.81   3.46
                                            d        5.19   9.02   9.93   7.01   4.88   3.92   3.44
          phi4seg24deg_x4counts             u        2.96   3.90   3.75   5.81   7.34   7.01   6.52
                                            d        7.20  16.25  18.13  13.08   9.09   7.30   6.51
          phi4seg24deg_countbin800          u        3.39   3.10   2.80   3.87   4.24   3.86   3.49
                                            d        5.67   9.19  11.16   7.82   5.21   4.08   3.53
          phi4seg24deg_countbin800_x4counts u        3.03   3.90   4.10   6.28   7.58   7.10   6.52
                                            d        8.01  16.78  19.79  14.19   9.65   7.61   6.66
stat+syst phifull                           u        2.96   3.53   3.44   5.65   9.51  10.03   8.77
                                            d        7.34  13.30  14.51  14.49  13.35  10.72   8.84
          phi4seg24deg_phifullbin           u        3.55   2.84   2.32   3.31   3.86   3.47   3.05
                                            d        4.84   7.34   8.59   6.85   4.73   3.63   3.06
          phi4seg24deg_phifullbin_x4counts  u        3.05   3.05   2.74   4.37   6.03   5.61   4.89
                                            d        5.80  10.21  11.71  10.17   7.58   5.84   4.90
          phi4seg24deg                      u        4.46   2.97   2.30   2.79   2.97   2.71   2.42
                                            d        3.96   4.27   4.46   4.30   3.57   2.92   2.49
          phi4seg24deg_x4counts             u        4.48   3.05   2.30   3.04   3.81   3.64   3.23
                                            d        4.12   4.56   4.80   4.94   4.62   3.91   3.32
          phi4seg24deg_countbin800          u        3.73   3.03   2.54   3.29   3.51   3.20   2.87
                                            d        5.22   7.31   8.13   6.18   4.32   3.40   2.92
          phi4seg24deg_countbin800_x4counts u        3.31   3.08   2.77   4.02   4.78   4.41   3.93
                                            d        6.06   9.74  10.36   8.22   5.97   4.69   4.01
```

## Error(twin) / Error(base row) at representative x

```
                                                   x=0.05  x=0.1  x=0.2  x=0.3  x=0.4  x=0.5  x=0.6
variant   twin                              quark                                                  
stat      phi4seg24deg_phifullbin_x4counts  u        1.17   0.81   0.69   0.63   0.56   0.53   0.52
                                            d        0.71   0.56   0.59   0.57   0.55   0.54   0.52
          phi4seg24deg_x4counts             u        1.13   0.74   0.66   0.61   0.56   0.54   0.53
                                            d        0.72   0.55   0.55   0.54   0.54   0.54   0.53
          phi4seg24deg_countbin800_x4counts u        1.12   0.80   0.68   0.62   0.56   0.54   0.53
                                            d        0.71   0.55   0.56   0.55   0.54   0.54   0.53
stat+syst phi4seg24deg_phifullbin_x4counts  u        1.17   0.93   0.85   0.76   0.64   0.62   0.62
                                            d        0.83   0.72   0.73   0.67   0.62   0.62   0.63
          phi4seg24deg_x4counts             u        1.00   0.98   1.00   0.92   0.78   0.74   0.75
                                            d        0.96   0.94   0.93   0.87   0.77   0.75   0.75
          phi4seg24deg_countbin800_x4counts u        1.13   0.98   0.92   0.82   0.73   0.73   0.73
                                            d        0.86   0.75   0.78   0.75   0.72   0.72   0.73
```

## Tensor charge gT, full and truncated (0.05 < x < 0.6)

```
                                                  gT(u)              gT(d)           gT(u-d)    gT trunc (u-d)
run                                                                                                           
world                                  0.5475 +- 0.1175  -0.3766 +- 0.1715  0.9241 +- 0.2111  0.7654 +- 0.1701
worldsyst                              0.5475 +- 0.1175  -0.3766 +- 0.1715  0.9241 +- 0.2111  0.7654 +- 0.1701
phifull                                0.5470 +- 0.0158  -0.3760 +- 0.0098  0.9230 +- 0.0200  0.7651 +- 0.0107
phifullsyst                            0.5469 +- 0.0239  -0.3757 +- 0.0181  0.9225 +- 0.0274  0.7652 +- 0.0195
phi4seg24deg_phifullbin                0.5470 +- 0.0309  -0.3757 +- 0.0260  0.9226 +- 0.0362  0.7655 +- 0.0308
phi4seg24deg_phifullbinsyst            0.5470 +- 0.0325  -0.3756 +- 0.0275  0.9225 +- 0.0386  0.7656 +- 0.0333
phi4seg24deg_phifullbin_x4counts       0.5470 +- 0.0248  -0.3759 +- 0.0183  0.9229 +- 0.0298  0.7652 +- 0.0197
phi4seg24deg_phifullbin_x4countssyst   0.5469 +- 0.0268  -0.3756 +- 0.0228  0.9225 +- 0.0304  0.7654 +- 0.0246
phi4seg24deg                           0.5472 +- 0.0319  -0.3757 +- 0.0272  0.9229 +- 0.0426  0.7655 +- 0.0355
phi4seg24degsyst                       0.5471 +- 0.0393  -0.3755 +- 0.0389  0.9225 +- 0.0589  0.7657 +- 0.0523
phi4seg24deg_x4counts                  0.5472 +- 0.0247  -0.3760 +- 0.0184  0.9232 +- 0.0333  0.7652 +- 0.0221
phi4seg24deg_x4countssyst              0.5469 +- 0.0355  -0.3753 +- 0.0361  0.9222 +- 0.0514  0.7655 +- 0.0468
phi4seg24deg_countbin800               0.5467 +- 0.0304  -0.3754 +- 0.0247  0.9221 +- 0.0393  0.7652 +- 0.0305
phi4seg24deg_countbin800syst           0.5466 +- 0.0343  -0.3753 +- 0.0278  0.9219 +- 0.0462  0.7652 +- 0.0373
phi4seg24deg_countbin800_x4counts      0.5467 +- 0.0240  -0.3757 +- 0.0173  0.9224 +- 0.0313  0.7650 +- 0.0196
phi4seg24deg_countbin800_x4countssyst  0.5466 +- 0.0294  -0.3753 +- 0.0238  0.9219 +- 0.0377  0.7651 +- 0.0305
```

## Truncated gT(u-d): error and world/this

```
--- stat ---
  world                                E(gT u-d) = 0.1701   world/this =   1.00x
  phifull                              E(gT u-d) = 0.0107   world/this =  15.86x
  phi4seg24deg_phifullbin              E(gT u-d) = 0.0308   world/this =   5.53x
  phi4seg24deg_phifullbin_x4counts     E(gT u-d) = 0.0197   world/this =   8.62x   twin/base =  0.64
  phi4seg24deg                         E(gT u-d) = 0.0355   world/this =   4.79x
  phi4seg24deg_x4counts                E(gT u-d) = 0.0221   world/this =   7.71x   twin/base =  0.62
  phi4seg24deg_countbin800             E(gT u-d) = 0.0305   world/this =   5.57x
  phi4seg24deg_countbin800_x4counts    E(gT u-d) = 0.0196   world/this =   8.70x   twin/base =  0.64
--- stat+syst ---
  world                                E(gT u-d) = 0.1701   world/this =   1.00x
  phifull                              E(gT u-d) = 0.0195   world/this =   8.71x
  phi4seg24deg_phifullbin              E(gT u-d) = 0.0333   world/this =   5.11x
  phi4seg24deg_phifullbin_x4counts     E(gT u-d) = 0.0246   world/this =   6.90x   twin/base =  0.74
  phi4seg24deg                         E(gT u-d) = 0.0523   world/this =   3.26x
  phi4seg24deg_x4counts                E(gT u-d) = 0.0468   world/this =   3.64x   twin/base =  0.89
  phi4seg24deg_countbin800             E(gT u-d) = 0.0373   world/this =   4.56x
  phi4seg24deg_countbin800_x4counts    E(gT u-d) = 0.0305   world/this =   5.57x   twin/base =  0.82
```
