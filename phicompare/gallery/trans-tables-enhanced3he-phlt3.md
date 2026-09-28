# trans tables, study `enhanced3he-phlt3`

Written by `plot-transversity_phicompare.ipynb` from `input-enhanced3he-phlt3.csv`, Q2 = 2.4 GeV^2, tol = 7.04. Regenerate, do not edit.

## Fits loaded (gallery/input-enhanced3he-phlt3.csv)

```
                                                                                                                       file  replicas                             twin of
entry                                                                                                                                                                    
world                                                                                   ../data_world/out-world_collins.dat       500                                   -
worldsyst                                                                               ../data_world/out-world_collins.dat       500                                   -
sbs                                                                                         ../data_sbs/out-sbs_collins.dat       500                                   -
phifull                                                                            data_phifull/out-enhanced3he_collins.dat       500                                   -
phifullsyst                                                                    data_phifull/out-enhanced3hesyst_collins.dat       500                                   -
phi4seg24deg_phifullbin_x4counts                          data_phi4seg24deg_phifullbin/out-enhanced3he_collins_x4counts.dat       500                                   -
phi4seg24deg_phifullbin_x4countssyst                  data_phi4seg24deg_phifullbin/out-enhanced3hesyst_collins_x4counts.dat       500                                   -
phi4seg24deg_phifullbin_phlt3_x4counts              data_phi4seg24deg_phifullbin/out-enhanced3he_collins_phlt3_x4counts.dat       500    phi4seg24deg_phifullbin_x4counts
phi4seg24deg_phifullbin_phlt3_x4countssyst      data_phi4seg24deg_phifullbin/out-enhanced3hesyst_collins_phlt3_x4counts.dat       500    phi4seg24deg_phifullbin_x4counts
phi4seg24degFA_phifullbin_x4counts                      data_phi4seg24degFA_phifullbin/out-enhanced3he_collins_x4counts.dat       500                                   -
phi4seg24degFA_phifullbin_x4countssyst              data_phi4seg24degFA_phifullbin/out-enhanced3hesyst_collins_x4counts.dat       500                                   -
phi4seg24degFA_phifullbin_phlt3_x4counts          data_phi4seg24degFA_phifullbin/out-enhanced3he_collins_phlt3_x4counts.dat       500  phi4seg24degFA_phifullbin_x4counts
phi4seg24degFA_phifullbin_phlt3_x4countssyst  data_phi4seg24degFA_phifullbin/out-enhanced3hesyst_collins_phlt3_x4counts.dat       500  phi4seg24degFA_phifullbin_x4counts
```

## Fitted parameters, mean +- std over replicas

```
                                                            Nu                 Nd                 a                 b                  c               kt2            Nu_err            Nd_err             a_err             b_err             c_err           kt2_err                  chi2                 ndof               edm
run                                                                                                                                                                                                                                                                                                                                
world                                         0.4007 +- 0.0125  -0.4511 +- 0.0311  1.0008 +- 0.0537  3.0103 +- 0.3782   0.0000 +- 0.0000  0.2496 +- 0.0224  0.0123 +- 0.0010  0.0313 +- 0.0014  0.0558 +- 0.0010  0.3842 +- 0.0075        nan +- nan  0.0207 +- 0.0006   140.5382 +- 16.0417   141.0000 +- 0.0000  0.0000 +- 0.0000
worldsyst                                     0.4007 +- 0.0125  -0.4511 +- 0.0311  1.0008 +- 0.0537  3.0103 +- 0.3782   0.0000 +- 0.0000  0.2496 +- 0.0224  0.0123 +- 0.0010  0.0313 +- 0.0014  0.0558 +- 0.0010  0.3842 +- 0.0075        nan +- nan  0.0207 +- 0.0006   140.5382 +- 16.0417   141.0000 +- 0.0000  0.0000 +- 0.0000
sbs                                           0.5301 +- 0.3334  -0.5991 +- 0.3811  1.0265 +- 0.0842  2.9069 +- 0.2391  -0.0026 +- 0.6624  0.2506 +- 0.0097  0.0936 +- 0.1250  0.1065 +- 0.1427  0.0345 +- 0.0134  0.1432 +- 0.0814  0.1828 +- 0.1102  0.0123 +- 0.0002   450.6328 +- 30.5383   595.0000 +- 0.0000  0.0005 +- 0.0018
phifull                                       0.4087 +- 0.0658  -0.4597 +- 0.0737  1.0027 +- 0.0264  2.9954 +- 0.0393  -0.0006 +- 0.2103  0.2500 +- 0.0010  0.0089 +- 0.0117  0.0098 +- 0.0132  0.0083 +- 0.0034  0.0299 +- 0.0022  0.0337 +- 0.0525  0.0010 +- 0.0000  1652.8844 +- 56.9147  1800.0000 +- 0.0000  0.0018 +- 0.0088
phifullsyst                                   0.4369 +- 0.1528  -0.4911 +- 0.1711  1.0099 +- 0.0538  2.9775 +- 0.0848   0.0143 +- 0.4444  0.2500 +- 0.0022  0.0355 +- 0.0379  0.0395 +- 0.0426  0.0201 +- 0.0108  0.0549 +- 0.0113  0.1420 +- 0.2021  0.0023 +- 0.0000  1653.2022 +- 56.8598  1800.0000 +- 0.0000  0.0018 +- 0.0063
phi4seg24deg_phifullbin_x4counts              0.4213 +- 0.1142  -0.4737 +- 0.1278  1.0058 +- 0.0390  2.9867 +- 0.0891   0.0051 +- 0.3309  0.2500 +- 0.0020  0.0214 +- 0.0245  0.0237 +- 0.0276  0.0176 +- 0.0063  0.0679 +- 0.0062  0.0844 +- 0.1293  0.0021 +- 0.0000  1653.3453 +- 56.7972  1800.0000 +- 0.0000  0.0019 +- 0.0071
phi4seg24deg_phifullbin_x4countssyst          0.4557 +- 0.1915  -0.5123 +- 0.2147  1.0138 +- 0.0589  2.9619 +- 0.1389   0.0075 +- 0.5104  0.2500 +- 0.0028  0.0463 +- 0.0470  0.0517 +- 0.0528  0.0262 +- 0.0112  0.0901 +- 0.0177  0.1800 +- 0.2600  0.0030 +- 0.0000  1653.5931 +- 56.7940  1800.0000 +- 0.0000  0.0022 +- 0.0080
phi4seg24deg_phifullbin_phlt3_x4counts        0.4163 +- 0.1195  -0.4680 +- 0.1332  1.0034 +- 0.0403  2.9869 +- 0.0953   0.0346 +- 0.3625  0.2498 +- 0.0031  0.0246 +- 0.0274  0.0271 +- 0.0309  0.0201 +- 0.0074  0.0752 +- 0.0076  0.1083 +- 0.1653  0.0033 +- 0.0001  1198.6515 +- 49.9465  1345.0000 +- 0.0000  0.0015 +- 0.0067
phi4seg24deg_phifullbin_phlt3_x4countssyst    0.4500 +- 0.1989  -0.5061 +- 0.2238  1.0109 +- 0.0599  2.9616 +- 0.1473   0.0440 +- 0.5398  0.2497 +- 0.0043  0.0557 +- 0.0610  0.0622 +- 0.0688  0.0304 +- 0.0145  0.1020 +- 0.0252  0.2222 +- 0.3226  0.0047 +- 0.0001  1199.0207 +- 50.0106  1345.0000 +- 0.0000  0.0014 +- 0.0057
phi4seg24degFA_phifullbin_x4counts            0.4304 +- 0.1311  -0.4838 +- 0.1466  1.0089 +- 0.0470  2.9836 +- 0.0740  -0.0003 +- 0.3824  0.2500 +- 0.0019  0.0274 +- 0.0313  0.0305 +- 0.0352  0.0173 +- 0.0089  0.0501 +- 0.0081  0.1063 +- 0.1592  0.0020 +- 0.0000  1653.0983 +- 56.8291  1800.0000 +- 0.0000  0.0020 +- 0.0081
phi4seg24degFA_phifullbin_x4countssyst        0.4573 +- 0.1916  -0.5139 +- 0.2144  1.0153 +- 0.0634  2.9658 +- 0.1111   0.0088 +- 0.5237  0.2500 +- 0.0028  0.0523 +- 0.0592  0.0582 +- 0.0662  0.0261 +- 0.0153  0.0698 +- 0.0226  0.1901 +- 0.2656  0.0029 +- 0.0000  1653.3759 +- 56.8507  1800.0000 +- 0.0000  0.0013 +- 0.0060
phi4seg24degFA_phifullbin_phlt3_x4counts      0.4150 +- 0.1289  -0.4665 +- 0.1437  1.0024 +- 0.0457  2.9850 +- 0.0758   0.0586 +- 0.4003  0.2500 +- 0.0029  0.0286 +- 0.0317  0.0318 +- 0.0357  0.0193 +- 0.0097  0.0551 +- 0.0083  0.1348 +- 0.2023  0.0031 +- 0.0000  1189.4704 +- 50.2434  1336.0000 +- 0.0000  0.0014 +- 0.0072
phi4seg24degFA_phifullbin_phlt3_x4countssyst  0.4419 +- 0.1984  -0.4966 +- 0.2227  1.0082 +- 0.0648  2.9658 +- 0.1166   0.0876 +- 0.5694  0.2501 +- 0.0043  0.0532 +- 0.0598  0.0592 +- 0.0669  0.0280 +- 0.0155  0.0769 +- 0.0245  0.2200 +- 0.3167  0.0045 +- 0.0001  1189.8494 +- 50.2097  1336.0000 +- 0.0000  0.0010 +- 0.0038
```

## Error(world) / Error at representative x (larger = better)

```
                                                          x=0.05  x=0.1  x=0.2  x=0.3  x=0.4  x=0.5  x=0.6
variant   run                                      quark                                                  
stat      sbs                                      u        3.67   2.92   2.35   2.94   3.96   4.18   3.80
                                                   d        3.34   3.22   3.74   5.00   6.34   5.50   4.30
          phifull                                  u        4.02   6.17   7.00  11.44  15.99  15.78  14.58
                                                   d       13.26  32.46  32.80  28.93  22.10  17.41  15.07
          phi4seg24deg_phifullbin_x4counts         u        2.82   3.51   3.53   5.70   7.53   7.14   6.50
                                                   d        7.16  15.39  17.74  13.22   9.29   7.38   6.47
          phi4seg24deg_phifullbin_phlt3_x4counts   u        2.94   3.38   3.23   4.90   6.46   6.36   5.92
                                                   d        6.47  12.46  16.30  12.59   8.70   6.88   6.02
          phi4seg24degFA_phifullbin_x4counts       u        2.93   3.64   3.71   6.16  10.11  10.63   9.46
                                                   d        7.70  15.73  18.23  16.25  13.74  11.11   9.41
          phi4seg24degFA_phifullbin_phlt3_x4counts u        2.98   3.37   3.30   5.42   9.14  10.08   9.14
                                                   d        6.71  12.38  16.02  15.08  12.95  10.60   9.06
stat+syst phifull                                  u        2.96   3.53   3.44   5.65   9.51  10.03   8.77
                                                   d        7.34  13.30  14.51  14.49  13.35  10.72   8.84
          phi4seg24deg_phifullbin_x4counts         u        3.05   3.05   2.74   4.37   6.03   5.61   4.89
                                                   d        5.80  10.21  11.71  10.17   7.58   5.84   4.90
          phi4seg24deg_phifullbin_phlt3_x4counts   u        3.30   2.91   2.48   3.71   5.17   5.09   4.56
                                                   d        5.26   8.04  10.06   9.27   7.01   5.46   4.61
          phi4seg24degFA_phifullbin_x4counts       u        3.09   3.14   2.88   4.62   7.84   8.40   7.26
                                                   d        6.11  10.38  11.98  11.68  10.89   8.86   7.26
          phi4seg24degFA_phifullbin_phlt3_x4counts u        3.34   2.96   2.58   4.03   6.94   7.89   6.97
                                                   d        5.27   7.89   9.88  10.47  10.13   8.40   6.92
```

## Error(twin) / Error(base row) at representative x

```
                                                          x=0.05  x=0.1  x=0.2  x=0.3  x=0.4  x=0.5  x=0.6
variant   twin                                     quark                                                  
stat      phi4seg24deg_phifullbin_phlt3_x4counts   u        0.96   1.04   1.09   1.16   1.17   1.12   1.10
                                                   d        1.11   1.24   1.09   1.05   1.07   1.07   1.07
          phi4seg24degFA_phifullbin_phlt3_x4counts u        0.98   1.08   1.12   1.14   1.11   1.05   1.03
                                                   d        1.15   1.27   1.14   1.08   1.06   1.05   1.04
stat+syst phi4seg24deg_phifullbin_phlt3_x4counts   u        0.92   1.05   1.10   1.18   1.17   1.10   1.07
                                                   d        1.10   1.27   1.16   1.10   1.08   1.07   1.06
          phi4seg24degFA_phifullbin_phlt3_x4counts u        0.93   1.06   1.12   1.15   1.13   1.07   1.04
                                                   d        1.16   1.31   1.21   1.12   1.07   1.06   1.05
```

## Tensor charge gT, full and truncated (0.05 < x < 0.6)

```
                                                         gT(u)              gT(d)           gT(u-d)    gT trunc (u-d)
run                                                                                                                  
world                                         0.5475 +- 0.1175  -0.3766 +- 0.1715  0.9241 +- 0.2111  0.7654 +- 0.1701
worldsyst                                     0.5475 +- 0.1175  -0.3766 +- 0.1715  0.9241 +- 0.2111  0.7654 +- 0.1701
sbs                                           0.5462 +- 0.0409  -0.3760 +- 0.0417  0.9222 +- 0.0417  0.7656 +- 0.0395
phifull                                       0.5470 +- 0.0158  -0.3760 +- 0.0098  0.9230 +- 0.0200  0.7651 +- 0.0107
phifullsyst                                   0.5469 +- 0.0239  -0.3757 +- 0.0181  0.9225 +- 0.0274  0.7652 +- 0.0195
phi4seg24deg_phifullbin_x4counts              0.5470 +- 0.0248  -0.3759 +- 0.0183  0.9229 +- 0.0298  0.7652 +- 0.0197
phi4seg24deg_phifullbin_x4countssyst          0.5469 +- 0.0268  -0.3756 +- 0.0228  0.9225 +- 0.0304  0.7654 +- 0.0246
phi4seg24deg_phifullbin_phlt3_x4counts        0.5469 +- 0.0270  -0.3758 +- 0.0202  0.9227 +- 0.0322  0.7650 +- 0.0235
phi4seg24deg_phifullbin_phlt3_x4countssyst    0.5468 +- 0.0307  -0.3755 +- 0.0243  0.9223 +- 0.0343  0.7652 +- 0.0306
phi4seg24degFA_phifullbin_x4counts            0.5468 +- 0.0230  -0.3757 +- 0.0171  0.9225 +- 0.0262  0.7652 +- 0.0174
phi4seg24degFA_phifullbin_x4countssyst        0.5467 +- 0.0256  -0.3754 +- 0.0221  0.9222 +- 0.0283  0.7653 +- 0.0225
phi4seg24degFA_phifullbin_phlt3_x4counts      0.5469 +- 0.0244  -0.3758 +- 0.0193  0.9227 +- 0.0274  0.7651 +- 0.0203
phi4seg24degFA_phifullbin_phlt3_x4countssyst  0.5469 +- 0.0276  -0.3755 +- 0.0244  0.9223 +- 0.0297  0.7653 +- 0.0274
```

## Truncated gT(u-d): error and world/this

```
--- stat ---
  world                                E(gT u-d) = 0.1701   world/this =   1.00x
  sbs                                  E(gT u-d) = 0.0395   world/this =   4.31x
  phifull                              E(gT u-d) = 0.0107   world/this =  15.86x
  phi4seg24deg_phifullbin_x4counts     E(gT u-d) = 0.0197   world/this =   8.62x
  phi4seg24deg_phifullbin_phlt3_x4counts E(gT u-d) = 0.0235   world/this =   7.23x   twin/base =  1.19
  phi4seg24degFA_phifullbin_x4counts   E(gT u-d) = 0.0174   world/this =   9.79x
  phi4seg24degFA_phifullbin_phlt3_x4counts E(gT u-d) = 0.0203   world/this =   8.37x   twin/base =  1.17
--- stat+syst ---
  world                                E(gT u-d) = 0.1701   world/this =   1.00x
  phifull                              E(gT u-d) = 0.0195   world/this =   8.71x
  phi4seg24deg_phifullbin_x4counts     E(gT u-d) = 0.0246   world/this =   6.90x
  phi4seg24deg_phifullbin_phlt3_x4counts E(gT u-d) = 0.0306   world/this =   5.55x   twin/base =  1.24
  phi4seg24degFA_phifullbin_x4counts   E(gT u-d) = 0.0225   world/this =   7.55x
  phi4seg24degFA_phifullbin_phlt3_x4counts E(gT u-d) = 0.0274   world/this =   6.20x   twin/base =  1.22
```
