# sivers tables, study `morebin`

Written by `plot-sivers_phicompare.ipynb` from `input-morebin.csv`, Q2 = 2.4 GeV^2, tol = 1.5. Regenerate, do not edit.

## Fits loaded (gallery/input-morebin.csv)

```
                                                                            file  replicas twin of
entry                                                                                             
world                                         ../data_world/out-world_sivers.dat       500       -
worldsyst                                     ../data_world/out-world_sivers.dat       500       -
sbs                                               ../data_sbs/out-sbs_sivers.dat       500       -
phifull                                  data_phifull/out-enhanced3he_sivers.dat       500       -
phifullsyst                          data_phifull/out-enhanced3hesyst_sivers.dat       500       -
phifull_countbin1e6          data_phifull_countbin1e6/out-enhanced3he_sivers.dat       500       -
phifull_countbin1e6syst  data_phifull_countbin1e6/out-enhanced3hesyst_sivers.dat       500       -
```

## Fitted parameters, mean +- std over replicas

```
                                        Nu                au                bu                Nd                ad                bd               kt2                    chi2
run                                                                                                                                                                           
world                    -0.0387 +- 0.0019  0.6663 +- 0.1130  4.1564 +- 1.0440  0.0576 +- 0.0154  0.4381 +- 0.2504  3.8314 +- 3.1709  0.1592 +- 0.0300     226.1234 +- 20.8210
worldsyst                -0.0387 +- 0.0019  0.6663 +- 0.1130  4.1564 +- 1.0440  0.0576 +- 0.0154  0.4381 +- 0.2504  3.8314 +- 3.1709  0.1592 +- 0.0300     226.1234 +- 20.8210
sbs                      -0.0357 +- 0.0081  0.6078 +- 0.0642  4.2252 +- 1.0423  0.0470 +- 0.0088  0.3318 +- 0.0861  3.4107 +- 0.7871  0.1591 +- 0.0150     449.2308 +- 30.6505
phifull                  -0.0374 +- 0.0064  0.6315 +- 0.0472  4.1441 +- 0.8068  0.0499 +- 0.0051  0.3714 +- 0.0485  3.3170 +- 0.5645  0.1600 +- 0.0016    1650.3382 +- 56.9493
phifullsyst              -0.0373 +- 0.0066  0.6277 +- 0.0475  4.1453 +- 0.8341  0.0497 +- 0.0057  0.3633 +- 0.0589  3.3128 +- 0.6192  0.1600 +- 0.0038    1650.6999 +- 56.9243
phifull_countbin1e6      -0.0374 +- 0.0060  0.6333 +- 0.0426  4.1483 +- 0.7750  0.0502 +- 0.0047  0.3764 +- 0.0469  3.2878 +- 0.5248  0.1599 +- 0.0016  19071.0768 +- 204.1544
phifull_countbin1e6syst  -0.0374 +- 0.0061  0.6329 +- 0.0429  4.1453 +- 0.7813  0.0502 +- 0.0048  0.3759 +- 0.0492  3.2806 +- 0.5301  0.1599 +- 0.0019  19071.1062 +- 204.1458
```

## Error(world) / Error at representative x (larger = better)

```
                                     x=0.05  x=0.1  x=0.2  x=0.3  x=0.4  x=0.5  x=0.6
variant   run                 quark                                                  
stat      sbs                 u        3.98   3.15   2.60   3.53   3.24   2.92   2.86
                              d        3.42   4.17  12.43  18.58  15.41  14.60  17.35
          phifull             u        3.37   6.35   7.19   7.93   6.28   5.14   4.63
                              d        8.89  46.54  56.69  47.77  34.14  28.86  31.28
          phifull_countbin1e6 u        3.43   6.07   7.09   7.83   6.43   5.29   4.67
                              d        8.97  47.30  56.70  47.35  33.46  28.63  31.56
stat+syst phifull             u        2.83   4.76   5.89   7.27   5.96   4.95   4.51
                              d        5.59  20.98  35.17  39.21  30.04  25.87  28.35
          phifull_countbin1e6 u        3.32   5.89   6.96   7.75   6.35   5.22   4.59
                              d        8.11  41.56  52.56  46.01  32.98  28.35  31.28
```

## Parameter replica-spread ratios

```
--- stat: std(world)/std, larger = better (NOT a precision comparison -- different params fixed, see above) ---
  world                                Nu=1.00  au=1.00  bu=1.00  Nd=1.00  ad=1.00  bd=1.00  kt2=1.00
  sbs                                  Nu=0.23  au=1.76  bu=1.00  Nd=1.76  ad=2.91  bd=4.03  kt2=2.00
  phifull                              Nu=0.29  au=2.39  bu=1.29  Nd=3.00  ad=5.17  bd=5.62  kt2=18.58
  phifull_countbin1e6                  Nu=0.31  au=2.66  bu=1.35  Nd=3.26  ad=5.34  bd=6.04  kt2=18.59

--- stat+syst: std(world)/std, larger = better (NOT a precision comparison -- different params fixed, see above) ---
  world                                Nu=1.00  au=1.00  bu=1.00  Nd=1.00  ad=1.00  bd=1.00  kt2=1.00
  phifull                              Nu=0.28  au=2.38  bu=1.25  Nd=2.71  ad=4.25  bd=5.12  kt2=7.80
  phifull_countbin1e6                  Nu=0.31  au=2.64  bu=1.34  Nd=3.21  ad=5.09  bd=5.98  kt2=15.42

--- stat: replica-std ratio to SoLID full-2pi (like-for-like -- this is the phi-cut effect) ---
  sbs                                  Nu=1.270  au=1.360  bu=1.292  Nd=1.706  ad=1.777  bd=1.394  kt2=9.308   (vs phifull)
  phifull                              Nu=1.000  au=1.000  bu=1.000  Nd=1.000  ad=1.000  bd=1.000  kt2=1.000   (vs phifull)
  phifull_countbin1e6                  Nu=0.945  au=0.901  bu=0.961  Nd=0.922  ad=0.968  bd=0.930  kt2=0.999   (vs phifull)

--- stat+syst: replica-std ratio to SoLID full-2pi (like-for-like -- this is the phi-cut effect) ---
  phifull                              Nu=1.000  au=1.000  bu=1.000  Nd=1.000  ad=1.000  bd=1.000  kt2=1.000   (vs phifull)
  phifull_countbin1e6                  Nu=0.923  au=0.902  bu=0.937  Nd=0.843  ad=0.836  bd=0.856  kt2=0.506   (vs phifull)

--- systematics penalty: std(stat+syst) / std(stat) ---
  phifull                              Nu=1.03  au=1.01  bu=1.03  Nd=1.11  ad=1.21  bd=1.10  kt2=2.38
  phifull_countbin1e6                  Nu=1.01  au=1.01  bu=1.01  Nd=1.02  ad=1.05  bd=1.01  kt2=1.21

Ratios marginally below 1.0 are 500-replica sampling noise (3.2%), not a
real reduction -- adding systematics cannot shrink an error. Use them as
the scale for how much of the near-1.0 numbers above is meaningful.
```
