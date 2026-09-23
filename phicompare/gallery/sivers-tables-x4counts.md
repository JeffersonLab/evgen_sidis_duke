# sivers tables, study `x4counts`

Written by `plot-sivers_phicompare.ipynb` from `input-x4counts.csv`, Q2 = 2.4 GeV^2, tol = 1.5. Regenerate, do not edit.

## Fits loaded (gallery/input-x4counts.csv)

```
                                                                                                        file  replicas                   twin of
entry                                                                                                                                           
world                                                                     ../data_world/out-world_sivers.dat       500                         -
worldsyst                                                                 ../data_world/out-world_sivers.dat       500                         -
phifull                                                              data_phifull/out-enhanced3he_sivers.dat       500                         -
phifullsyst                                                      data_phifull/out-enhanced3hesyst_sivers.dat       500                         -
phi4seg24deg_phifullbin                              data_phi4seg24deg_phifullbin/out-enhanced3he_sivers.dat       500                         -
phi4seg24deg_phifullbinsyst                      data_phi4seg24deg_phifullbin/out-enhanced3hesyst_sivers.dat       500                         -
phi4seg24deg_phifullbin_x4counts            data_phi4seg24deg_phifullbin/out-enhanced3he_sivers_x4counts.dat       500   phi4seg24deg_phifullbin
phi4seg24deg_phifullbin_x4countssyst    data_phi4seg24deg_phifullbin/out-enhanced3hesyst_sivers_x4counts.dat       500   phi4seg24deg_phifullbin
phi4seg24deg                                                    data_phi4seg24deg/out-enhanced3he_sivers.dat       500                         -
phi4seg24degsyst                                            data_phi4seg24deg/out-enhanced3hesyst_sivers.dat       500                         -
phi4seg24deg_x4counts                                  data_phi4seg24deg/out-enhanced3he_sivers_x4counts.dat       500              phi4seg24deg
phi4seg24deg_x4countssyst                          data_phi4seg24deg/out-enhanced3hesyst_sivers_x4counts.dat       500              phi4seg24deg
phi4seg24deg_countbin800                            data_phi4seg24deg_countbin800/out-enhanced3he_sivers.dat       500                         -
phi4seg24deg_countbin800syst                    data_phi4seg24deg_countbin800/out-enhanced3hesyst_sivers.dat       500                         -
phi4seg24deg_countbin800_x4counts          data_phi4seg24deg_countbin800/out-enhanced3he_sivers_x4counts.dat       500  phi4seg24deg_countbin800
phi4seg24deg_countbin800_x4countssyst  data_phi4seg24deg_countbin800/out-enhanced3hesyst_sivers_x4counts.dat       500  phi4seg24deg_countbin800
```

## Fitted parameters, mean +- std over replicas

```
                                                      Nu                au                bu                Nd                ad                bd               kt2                  chi2
run                                                                                                                                                                                       
world                                  -0.0387 +- 0.0019  0.6663 +- 0.1130  4.1564 +- 1.0440  0.0576 +- 0.0154  0.4381 +- 0.2504  3.8314 +- 3.1709  0.1592 +- 0.0300   226.1234 +- 20.8210
worldsyst                              -0.0387 +- 0.0019  0.6663 +- 0.1130  4.1564 +- 1.0440  0.0576 +- 0.0154  0.4381 +- 0.2504  3.8314 +- 3.1709  0.1592 +- 0.0300   226.1234 +- 20.8210
phifull                                -0.0374 +- 0.0064  0.6315 +- 0.0472  4.1441 +- 0.8068  0.0499 +- 0.0051  0.3714 +- 0.0485  3.3170 +- 0.5645  0.1600 +- 0.0016  1650.3382 +- 56.9493
phifullsyst                            -0.0373 +- 0.0066  0.6277 +- 0.0475  4.1453 +- 0.8341  0.0497 +- 0.0057  0.3633 +- 0.0589  3.3128 +- 0.6192  0.1600 +- 0.0038  1650.6999 +- 56.9243
phi4seg24deg_phifullbin                -0.0350 +- 0.0093  0.5979 +- 0.0870  4.3763 +- 1.1593  0.0486 +- 0.0081  0.3482 +- 0.0723  3.4120 +- 0.9666  0.1604 +- 0.0065  1652.2206 +- 56.9074
phi4seg24deg_phifullbinsyst            -0.0350 +- 0.0093  0.5984 +- 0.0853  4.3713 +- 1.1716  0.0484 +- 0.0083  0.3460 +- 0.0744  3.4240 +- 0.9770  0.1604 +- 0.0076  1652.3225 +- 56.9097
phi4seg24deg_phifullbin_x4counts       -0.0361 +- 0.0085  0.6087 +- 0.0756  4.2501 +- 1.0429  0.0489 +- 0.0064  0.3563 +- 0.0677  3.4047 +- 0.7111  0.1602 +- 0.0034  1651.1967 +- 56.8811
phi4seg24deg_phifullbin_x4countssyst   -0.0360 +- 0.0085  0.6075 +- 0.0764  4.2584 +- 1.0382  0.0489 +- 0.0068  0.3540 +- 0.0676  3.3818 +- 0.7655  0.1602 +- 0.0052  1651.4236 +- 56.8739
phi4seg24deg                           -0.0347 +- 0.0095  0.5972 +- 0.0846  4.4298 +- 1.1994  0.0476 +- 0.0091  0.3396 +- 0.0690  3.4951 +- 1.0797  0.1609 +- 0.0091   163.1970 +- 17.4786
phi4seg24degsyst                       -0.0351 +- 0.0098  0.5970 +- 0.0819  4.3600 +- 1.2562  0.0469 +- 0.0105  0.3254 +- 0.0823  3.5167 +- 1.1387  0.1607 +- 0.0127   163.5987 +- 17.4971
phi4seg24deg_x4counts                  -0.0357 +- 0.0088  0.6068 +- 0.0755  4.3052 +- 1.0874  0.0493 +- 0.0065  0.3631 +- 0.0564  3.3575 +- 0.8073  0.1604 +- 0.0050   162.1797 +- 17.4540
phi4seg24deg_x4countssyst              -0.0358 +- 0.0095  0.6009 +- 0.0781  4.2646 +- 1.2004  0.0481 +- 0.0088  0.3416 +- 0.0724  3.4040 +- 0.9593  0.1604 +- 0.0111   162.8339 +- 17.4656
phi4seg24deg_countbin800               -0.0345 +- 0.0096  0.5954 +- 0.0889  4.4508 +- 1.2072  0.0480 +- 0.0084  0.3474 +- 0.0748  3.4941 +- 1.0012  0.1599 +- 0.0067   799.7405 +- 41.6659
phi4seg24deg_countbin800syst           -0.0344 +- 0.0097  0.5939 +- 0.0913  4.4506 +- 1.2102  0.0477 +- 0.0090  0.3423 +- 0.0778  3.5009 +- 1.0518  0.1598 +- 0.0083   799.8831 +- 41.6797
phi4seg24deg_countbin800_x4counts      -0.0359 +- 0.0082  0.6142 +- 0.0735  4.3050 +- 1.0088  0.0491 +- 0.0063  0.3633 +- 0.0664  3.4061 +- 0.7233  0.1599 +- 0.0035   798.6997 +- 41.6375
phi4seg24deg_countbin800_x4countssyst  -0.0357 +- 0.0084  0.6115 +- 0.0751  4.3145 +- 1.0382  0.0489 +- 0.0071  0.3586 +- 0.0700  3.4057 +- 0.8210  0.1597 +- 0.0060   798.9940 +- 41.6781
```

## Error(world) / Error at representative x (larger = better)

```
                                                   x=0.05  x=0.1  x=0.2  x=0.3  x=0.4  x=0.5  x=0.6
variant   run                               quark                                                  
stat      phifull                           u        3.37   6.35   7.19   7.93   6.28   5.14   4.63
                                            d        8.89  46.54  56.69  47.77  34.14  28.86  31.28
          phi4seg24deg_phifullbin           u        2.45   2.65   2.68   2.56   2.29   2.18   2.20
                                            d        4.18  12.38  17.10  12.93  10.42  10.17  11.64
          phi4seg24deg_phifullbin_x4counts  u        2.55   3.53   4.15   4.05   3.39   3.02   2.78
                                            d        5.60  23.08  31.60  23.79  18.17  17.01  19.96
          phi4seg24deg                      u        2.83   2.67   2.51   2.35   2.10   2.02   2.08
                                            d        3.92  11.38  14.55  11.63   9.31   9.14  10.77
          phi4seg24deg_x4counts             u        2.58   3.61   3.76   3.29   2.76   2.53   2.48
                                            d        4.47  20.80  25.58  20.42  15.12  14.09  16.66
          phi4seg24deg_countbin800          u        2.52   2.61   2.64   2.50   2.20   2.09   2.09
                                            d        4.06  13.36  18.41  13.53  10.34  10.00  11.79
          phi4seg24deg_countbin800_x4counts u        2.65   3.49   4.18   3.99   3.31   2.99   2.96
                                            d        5.28  24.64  34.05  24.30  17.75  16.49  19.43
stat+syst phifull                           u        2.83   4.76   5.89   7.27   5.96   4.95   4.51
                                            d        5.59  20.98  35.17  39.21  30.04  25.87  28.35
          phi4seg24deg_phifullbin           u        2.45   2.60   2.65   2.54   2.28   2.17   2.17
                                            d        3.98  10.76  16.03  12.59  10.17   9.94  11.47
          phi4seg24deg_phifullbin_x4counts  u        2.41   3.25   3.90   3.94   3.30   2.94   2.78
                                            d        4.74  15.80  25.40  21.86  16.73  15.65  18.40
          phi4seg24deg                      u        2.89   2.38   2.41   2.33   2.06   1.96   1.99
                                            d        3.38   6.35  11.59  10.34   8.60   8.49   9.63
          phi4seg24deg_x4counts             u        2.68   2.49   2.84   2.89   2.47   2.24   2.04
                                            d        3.65   7.17  13.97  15.16  12.55  11.94  13.75
          phi4seg24deg_countbin800          u        2.50   2.53   2.58   2.47   2.18   2.08   2.12
                                            d        3.82  11.18  16.38  12.84   9.90   9.60  11.20
          phi4seg24deg_countbin800_x4counts u        2.47   3.11   3.73   3.69   3.09   2.81   2.79
                                            d        4.32  15.61  23.95  20.48  15.24  14.25  16.77
```

## Error(twin) / Error(base row) at representative x

```
                                                   x=0.05  x=0.1  x=0.2  x=0.3  x=0.4  x=0.5  x=0.6
variant   twin                              quark                                                  
stat      phi4seg24deg_phifullbin_x4counts  u        0.96   0.75   0.64   0.63   0.67   0.72   0.79
                                            d        0.75   0.54   0.54   0.54   0.57   0.60   0.58
          phi4seg24deg_x4counts             u        1.10   0.74   0.67   0.71   0.76   0.80   0.84
                                            d        0.88   0.55   0.57   0.57   0.62   0.65   0.65
          phi4seg24deg_countbin800_x4counts u        0.95   0.75   0.63   0.63   0.67   0.70   0.71
                                            d        0.77   0.54   0.54   0.56   0.58   0.61   0.61
stat+syst phi4seg24deg_phifullbin_x4counts  u        1.01   0.80   0.68   0.65   0.69   0.74   0.78
                                            d        0.84   0.68   0.63   0.58   0.61   0.64   0.62
          phi4seg24deg_x4counts             u        1.08   0.96   0.85   0.81   0.83   0.88   0.97
                                            d        0.92   0.89   0.83   0.68   0.69   0.71   0.70
          phi4seg24deg_countbin800_x4counts u        1.01   0.82   0.69   0.67   0.71   0.74   0.76
                                            d        0.88   0.72   0.68   0.63   0.65   0.67   0.67
```

## Parameter replica-spread ratios

```
--- stat: std(world)/std, larger = better (NOT a precision comparison -- different params fixed, see above) ---
  world                                Nu=1.00  au=1.00  bu=1.00  Nd=1.00  ad=1.00  bd=1.00  kt2=1.00
  phifull                              Nu=0.29  au=2.39  bu=1.29  Nd=3.00  ad=5.17  bd=5.62  kt2=18.58
  phi4seg24deg_phifullbin              Nu=0.20  au=1.30  bu=0.90  Nd=1.90  ad=3.46  bd=3.28  kt2=4.62
  phi4seg24deg_phifullbin_x4counts     Nu=0.22  au=1.49  bu=1.00  Nd=2.43  ad=3.70  bd=4.46  kt2=8.79
  phi4seg24deg                         Nu=0.20  au=1.34  bu=0.87  Nd=1.70  ad=3.63  bd=2.94  kt2=3.31
  phi4seg24deg_x4counts                Nu=0.21  au=1.50  bu=0.96  Nd=2.36  ad=4.44  bd=3.93  kt2=5.98
  phi4seg24deg_countbin800             Nu=0.19  au=1.27  bu=0.86  Nd=1.84  ad=3.35  bd=3.17  kt2=4.51
  phi4seg24deg_countbin800_x4counts    Nu=0.23  au=1.54  bu=1.03  Nd=2.45  ad=3.77  bd=4.38  kt2=8.62

--- stat+syst: std(world)/std, larger = better (NOT a precision comparison -- different params fixed, see above) ---
  world                                Nu=1.00  au=1.00  bu=1.00  Nd=1.00  ad=1.00  bd=1.00  kt2=1.00
  phifull                              Nu=0.28  au=2.38  bu=1.25  Nd=2.71  ad=4.25  bd=5.12  kt2=7.80
  phi4seg24deg_phifullbin              Nu=0.20  au=1.33  bu=0.89  Nd=1.86  ad=3.36  bd=3.25  kt2=3.96
  phi4seg24deg_phifullbin_x4counts     Nu=0.22  au=1.48  bu=1.01  Nd=2.27  ad=3.70  bd=4.14  kt2=5.82
  phi4seg24deg                         Nu=0.19  au=1.38  bu=0.83  Nd=1.47  ad=3.04  bd=2.78  kt2=2.36
  phi4seg24deg_x4counts                Nu=0.20  au=1.45  bu=0.87  Nd=1.76  ad=3.46  bd=3.31  kt2=2.71
  phi4seg24deg_countbin800             Nu=0.19  au=1.24  bu=0.86  Nd=1.72  ad=3.22  bd=3.01  kt2=3.63
  phi4seg24deg_countbin800_x4counts    Nu=0.22  au=1.51  bu=1.01  Nd=2.19  ad=3.58  bd=3.86  kt2=5.03

--- stat: replica-std ratio to SoLID full-2pi (like-for-like -- this is the phi-cut effect) ---
  phifull                              Nu=1.000  au=1.000  bu=1.000  Nd=1.000  ad=1.000  bd=1.000  kt2=1.000   (vs phifull)
  phi4seg24deg_phifullbin              Nu=1.456  au=1.843  bu=1.437  Nd=1.581  ad=1.491  bd=1.712  kt2=4.019   (vs phifull)
  phi4seg24deg_phifullbin_x4counts     Nu=1.338  au=1.602  bu=1.293  Nd=1.236  ad=1.398  bd=1.260  kt2=2.113   (vs phifull)
  phi4seg24deg                         Nu=1.495  au=1.792  bu=1.487  Nd=1.768  ad=1.423  bd=1.913  kt2=5.608   (vs phifull)
  phi4seg24deg_x4counts                Nu=1.387  au=1.600  bu=1.348  Nd=1.272  ad=1.164  bd=1.430  kt2=3.108   (vs phifull)
  phi4seg24deg_countbin800             Nu=1.507  au=1.882  bu=1.496  Nd=1.637  ad=1.544  bd=1.774  kt2=4.123   (vs phifull)
  phi4seg24deg_countbin800_x4counts    Nu=1.280  au=1.556  bu=1.250  Nd=1.227  ad=1.370  bd=1.281  kt2=2.155   (vs phifull)

--- stat+syst: replica-std ratio to SoLID full-2pi (like-for-like -- this is the phi-cut effect) ---
  phifull                              Nu=1.000  au=1.000  bu=1.000  Nd=1.000  ad=1.000  bd=1.000  kt2=1.000   (vs phifull)
  phi4seg24deg_phifullbin              Nu=1.420  au=1.795  bu=1.405  Nd=1.452  ad=1.265  bd=1.578  kt2=1.968   (vs phifull)
  phi4seg24deg_phifullbin_x4counts     Nu=1.295  au=1.609  bu=1.245  Nd=1.194  ad=1.149  bd=1.236  kt2=1.340   (vs phifull)
  phi4seg24deg                         Nu=1.491  au=1.724  bu=1.506  Nd=1.837  ad=1.399  bd=1.839  kt2=3.310   (vs phifull)
  phi4seg24deg_x4counts                Nu=1.451  au=1.644  bu=1.439  Nd=1.541  ad=1.229  bd=1.549  kt2=2.879   (vs phifull)
  phi4seg24deg_countbin800             Nu=1.472  au=1.922  bu=1.451  Nd=1.574  ad=1.321  bd=1.699  kt2=2.150   (vs phifull)
  phi4seg24deg_countbin800_x4counts    Nu=1.279  au=1.579  bu=1.245  Nd=1.236  ad=1.190  bd=1.326  kt2=1.550   (vs phifull)

--- stat: twin penalty, std(twin) / std(its base row) ---
  phi4seg24deg_phifullbin_x4counts     Nu=0.919  au=0.869  bu=0.900  Nd=0.782  ad=0.937  bd=0.736  kt2=0.526
  phi4seg24deg_x4counts                Nu=0.928  au=0.893  bu=0.907  Nd=0.720  ad=0.818  bd=0.748  kt2=0.554
  phi4seg24deg_countbin800_x4counts    Nu=0.850  au=0.827  bu=0.836  Nd=0.749  ad=0.888  bd=0.722  kt2=0.523

--- stat+syst: twin penalty, std(twin) / std(its base row) ---
  phi4seg24deg_phifullbin_x4counts     Nu=0.911  au=0.896  bu=0.886  Nd=0.822  ad=0.909  bd=0.784  kt2=0.681
  phi4seg24deg_x4counts                Nu=0.973  au=0.954  bu=0.956  Nd=0.839  ad=0.879  bd=0.842  kt2=0.870
  phi4seg24deg_countbin800_x4counts    Nu=0.869  au=0.822  bu=0.858  Nd=0.785  ad=0.900  bd=0.781  kt2=0.721

--- systematics penalty: std(stat+syst) / std(stat) ---
  phifull                              Nu=1.03  au=1.01  bu=1.03  Nd=1.11  ad=1.21  bd=1.10  kt2=2.38
  phi4seg24deg_phifullbin              Nu=1.01  au=0.98  bu=1.01  Nd=1.02  ad=1.03  bd=1.01  kt2=1.17
  phi4seg24deg_phifullbin_x4counts     Nu=1.00  au=1.01  bu=1.00  Nd=1.07  ad=1.00  bd=1.08  kt2=1.51
  phi4seg24deg                         Nu=1.03  au=0.97  bu=1.05  Nd=1.15  ad=1.19  bd=1.05  kt2=1.41
  phi4seg24deg_x4counts                Nu=1.08  au=1.03  bu=1.10  Nd=1.34  ad=1.28  bd=1.19  kt2=2.21
  phi4seg24deg_countbin800             Nu=1.01  au=1.03  bu=1.00  Nd=1.07  ad=1.04  bd=1.05  kt2=1.24
  phi4seg24deg_countbin800_x4counts    Nu=1.03  au=1.02  bu=1.03  Nd=1.12  ad=1.05  bd=1.14  kt2=1.71

Ratios marginally below 1.0 are 500-replica sampling noise (3.2%), not a
real reduction -- adding systematics cannot shrink an error. Use them as
the scale for how much of the near-1.0 numbers above is meaningful.
```
