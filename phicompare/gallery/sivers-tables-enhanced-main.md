# sivers tables, study `enhanced-main`

Written by `plot-sivers_phicompare.ipynb` from `input-enhanced-main.csv`, Q2 = 2.4 GeV^2, tol = 1.5. Regenerate, do not edit.

## Fits loaded (gallery/input-enhanced-main.csv)

```
                                                        file  replicas twin of
entry                                                                         
world                     ../data_world/out-world_sivers.dat       500       -
worldsyst                 ../data_world/out-world_sivers.dat       500       -
phifull              data_phifull/out-enhanced3he_sivers.dat       500       -
phifullsyst      data_phifull/out-enhanced3hesyst_sivers.dat       500       -
phifull+nh3             data_phifull/out-enhanced_sivers.dat       500       -
phifull+nh3syst     data_phifull/out-enhancedsyst_sivers.dat       500       -
```

## Fitted parameters, mean +- std over replicas

```
                                Nu                au                bu                Nd                ad                bd               kt2                  chi2
run                                                                                                                                                                 
world            -0.0387 +- 0.0019  0.6663 +- 0.1130  4.1564 +- 1.0440  0.0576 +- 0.0154  0.4381 +- 0.2504  3.8314 +- 3.1709  0.1592 +- 0.0300   226.1234 +- 20.8210
worldsyst        -0.0387 +- 0.0019  0.6663 +- 0.1130  4.1564 +- 1.0440  0.0576 +- 0.0154  0.4381 +- 0.2504  3.8314 +- 3.1709  0.1592 +- 0.0300   226.1234 +- 20.8210
phifull          -0.0374 +- 0.0064  0.6315 +- 0.0472  4.1441 +- 0.8068  0.0499 +- 0.0051  0.3714 +- 0.0485  3.3170 +- 0.5645  0.1600 +- 0.0016  1650.3382 +- 56.9493
phifullsyst      -0.0373 +- 0.0066  0.6277 +- 0.0475  4.1453 +- 0.8341  0.0497 +- 0.0057  0.3633 +- 0.0589  3.3128 +- 0.6192  0.1600 +- 0.0038  1650.6999 +- 56.9243
phifull+nh3      -0.0377 +- 0.0055  0.6382 +- 0.0414  4.1275 +- 0.6808  0.0501 +- 0.0049  0.3738 +- 0.0453  3.2952 +- 0.5427  0.1600 +- 0.0016  2201.2105 +- 66.0933
phifull+nh3syst  -0.0374 +- 0.0058  0.6328 +- 0.0442  4.1449 +- 0.7180  0.0499 +- 0.0055  0.3660 +- 0.0551  3.2879 +- 0.6049  0.1600 +- 0.0037  2201.5910 +- 66.0917
```

## Error(world) / Error at representative x (larger = better)

```
                             x=0.05  x=0.1  x=0.2  x=0.3  x=0.4  x=0.5  x=0.6
variant   run         quark                                                  
stat      phifull     u        3.37   6.35   7.19   7.93   6.28   5.14   4.63
                      d        8.89  46.54  56.69  47.77  34.14  28.86  31.28
          phifull+nh3 u        3.53   7.43   9.34  10.88   8.53   6.74   6.10
                      d        9.05  48.49  59.67  51.19  36.92  31.01  33.46
stat+syst phifull     u        2.83   4.76   5.89   7.27   5.96   4.95   4.51
                      d        5.59  20.98  35.17  39.21  30.04  25.87  28.35
          phifull+nh3 u        2.92   5.19   6.80   8.91   7.50   6.05   5.52
                      d        5.66  21.84  36.82  41.34  32.16  27.55  29.83
```

## Parameter replica-spread ratios

```
--- stat: std(world)/std, larger = better (NOT a precision comparison -- different params fixed, see above) ---
  world                                Nu=1.00  au=1.00  bu=1.00  Nd=1.00  ad=1.00  bd=1.00  kt2=1.00
  phifull                              Nu=0.29  au=2.39  bu=1.29  Nd=3.00  ad=5.17  bd=5.62  kt2=18.58
  phifull+nh3                          Nu=0.34  au=2.73  bu=1.53  Nd=3.14  ad=5.52  bd=5.84  kt2=18.89

--- stat+syst: std(world)/std, larger = better (NOT a precision comparison -- different params fixed, see above) ---
  world                                Nu=1.00  au=1.00  bu=1.00  Nd=1.00  ad=1.00  bd=1.00  kt2=1.00
  phifull                              Nu=0.28  au=2.38  bu=1.25  Nd=2.71  ad=4.25  bd=5.12  kt2=7.80
  phifull+nh3                          Nu=0.32  au=2.56  bu=1.45  Nd=2.80  ad=4.55  bd=5.24  kt2=8.13

--- stat: replica-std ratio to SoLID full-2pi (like-for-like -- this is the phi-cut effect) ---
  phifull                              Nu=1.000  au=1.000  bu=1.000  Nd=1.000  ad=1.000  bd=1.000  kt2=1.000   (vs phifull)
  phifull+nh3                          Nu=1.000  au=1.000  bu=1.000  Nd=1.000  ad=1.000  bd=1.000  kt2=1.000   (vs phifull+nh3)

--- stat+syst: replica-std ratio to SoLID full-2pi (like-for-like -- this is the phi-cut effect) ---
  phifull                              Nu=1.000  au=1.000  bu=1.000  Nd=1.000  ad=1.000  bd=1.000  kt2=1.000   (vs phifull)
  phifull+nh3                          Nu=1.000  au=1.000  bu=1.000  Nd=1.000  ad=1.000  bd=1.000  kt2=1.000   (vs phifull+nh3)

--- systematics penalty: std(stat+syst) / std(stat) ---
  phifull                              Nu=1.03  au=1.01  bu=1.03  Nd=1.11  ad=1.21  bd=1.10  kt2=2.38
  phifull+nh3                          Nu=1.07  au=1.07  bu=1.05  Nd=1.12  ad=1.21  bd=1.11  kt2=2.32

Ratios marginally below 1.0 are 500-replica sampling noise (3.2%), not a
real reduction -- adding systematics cannot shrink an error. Use them as
the scale for how much of the near-1.0 numbers above is meaningful.
```
