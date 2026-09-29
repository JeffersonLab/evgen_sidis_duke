# sivers tables, study `enhanced3he-main`

Written by `plot-sivers_phicompare.ipynb` from `input-enhanced3he-main.csv`, Q2 = 2.4 GeV^2, tol = 1.5. Regenerate, do not edit.

## Fits loaded (gallery/input-enhanced3he-main.csv)

```
                                                                                                          file  replicas twin of
entry                                                                                                                           
world                                                                       ../data_world/out-world_sivers.dat       500       -
worldsyst                                                                   ../data_world/out-world_sivers.dat       500       -
phifull                                                                data_phifull/out-enhanced3he_sivers.dat       500       -
phifullsyst                                                        data_phifull/out-enhanced3hesyst_sivers.dat       500       -
phi4seg24degFA_phifullbin_x4counts          data_phi4seg24degFA_phifullbin/out-enhanced3he_sivers_x4counts.dat       500       -
phi4seg24degFA_phifullbin_x4countssyst  data_phi4seg24degFA_phifullbin/out-enhanced3hesyst_sivers_x4counts.dat       500       -
```

## Fitted parameters, mean +- std over replicas

```
                                                       Nu                au                bu                Nd                ad                bd               kt2                  chi2
run                                                                                                                                                                                        
world                                   -0.0387 +- 0.0019  0.6663 +- 0.1130  4.1564 +- 1.0440  0.0576 +- 0.0154  0.4381 +- 0.2504  3.8314 +- 3.1709  0.1592 +- 0.0300   226.1234 +- 20.8210
worldsyst                               -0.0387 +- 0.0019  0.6663 +- 0.1130  4.1564 +- 1.0440  0.0576 +- 0.0154  0.4381 +- 0.2504  3.8314 +- 3.1709  0.1592 +- 0.0300   226.1234 +- 20.8210
phifull                                 -0.0374 +- 0.0064  0.6315 +- 0.0472  4.1441 +- 0.8068  0.0499 +- 0.0051  0.3714 +- 0.0485  3.3170 +- 0.5645  0.1600 +- 0.0016  1650.3382 +- 56.9493
phifullsyst                             -0.0373 +- 0.0066  0.6277 +- 0.0475  4.1453 +- 0.8341  0.0497 +- 0.0057  0.3633 +- 0.0589  3.3128 +- 0.6192  0.1600 +- 0.0038  1650.6999 +- 56.9243
phi4seg24degFA_phifullbin_x4counts      -0.0365 +- 0.0076  0.6155 +- 0.0683  4.1965 +- 0.8923  0.0490 +- 0.0058  0.3585 +- 0.0636  3.3814 +- 0.6327  0.1602 +- 0.0034  1650.9649 +- 56.9105
phi4seg24degFA_phifullbin_x4countssyst  -0.0364 +- 0.0076  0.6150 +- 0.0668  4.1997 +- 0.8971  0.0489 +- 0.0060  0.3563 +- 0.0637  3.3760 +- 0.6655  0.1602 +- 0.0051  1651.1828 +- 56.9094
```

## Error(world) / Error at representative x (larger = better)

```
                                                    x=0.05  x=0.1  x=0.2  x=0.3  x=0.4  x=0.5  x=0.6
variant   run                                quark                                                  
stat      phifull                            u        3.37   6.35   7.19   7.93   6.28   5.14   4.63
                                             d        8.89  46.54  56.69  47.77  34.14  28.86  31.28
          phi4seg24degFA_phifullbin_x4counts u        2.64   3.60   4.36   5.28   4.59   4.00   3.79
                                             d        5.58  23.40  33.28  29.73  23.12  21.06  24.18
stat+syst phifull                            u        2.83   4.76   5.89   7.27   5.96   4.95   4.51
                                             d        5.59  20.98  35.17  39.21  30.04  25.87  28.35
          phi4seg24degFA_phifullbin_x4counts u        2.49   3.31   4.08   5.09   4.47   3.91   3.68
                                             d        4.68  16.00  26.32  27.21  21.57  19.70  22.68
```

## Parameter replica-spread ratios

```
--- stat: std(world)/std, larger = better (NOT a precision comparison -- different params fixed, see above) ---
  world                                Nu=1.00  au=1.00  bu=1.00  Nd=1.00  ad=1.00  bd=1.00  kt2=1.00
  phifull                              Nu=0.29  au=2.39  bu=1.29  Nd=3.00  ad=5.17  bd=5.62  kt2=18.58
  phi4seg24degFA_phifullbin_x4counts   Nu=0.25  au=1.66  bu=1.17  Nd=2.68  ad=3.94  bd=5.01  kt2=8.84

--- stat+syst: std(world)/std, larger = better (NOT a precision comparison -- different params fixed, see above) ---
  world                                Nu=1.00  au=1.00  bu=1.00  Nd=1.00  ad=1.00  bd=1.00  kt2=1.00
  phifull                              Nu=0.28  au=2.38  bu=1.25  Nd=2.71  ad=4.25  bd=5.12  kt2=7.80
  phi4seg24degFA_phifullbin_x4counts   Nu=0.25  au=1.69  bu=1.16  Nd=2.56  ad=3.93  bd=4.76  kt2=5.86

--- stat: replica-std ratio to SoLID full-2pi (like-for-like -- this is the phi-cut effect) ---
  phifull                              Nu=1.000  au=1.000  bu=1.000  Nd=1.000  ad=1.000  bd=1.000  kt2=1.000   (vs phifull)
  phi4seg24degFA_phifullbin_x4counts   Nu=1.188  au=1.445  bu=1.106  Nd=1.123  ad=1.312  bd=1.121  kt2=2.102   (vs phifull)

--- stat+syst: replica-std ratio to SoLID full-2pi (like-for-like -- this is the phi-cut effect) ---
  phifull                              Nu=1.000  au=1.000  bu=1.000  Nd=1.000  ad=1.000  bd=1.000  kt2=1.000   (vs phifull)
  phi4seg24degFA_phifullbin_x4counts   Nu=1.150  au=1.406  bu=1.076  Nd=1.056  ad=1.083  bd=1.075  kt2=1.330   (vs phifull)

--- systematics penalty: std(stat+syst) / std(stat) ---
  phifull                              Nu=1.03  au=1.01  bu=1.03  Nd=1.11  ad=1.21  bd=1.10  kt2=2.38
  phi4seg24degFA_phifullbin_x4counts   Nu=1.00  au=0.98  bu=1.01  Nd=1.04  ad=1.00  bd=1.05  kt2=1.51

Ratios marginally below 1.0 are 500-replica sampling noise (3.2%), not a
real reduction -- adding systematics cannot shrink an error. Use them as
the scale for how much of the near-1.0 numbers above is meaningful.
```
