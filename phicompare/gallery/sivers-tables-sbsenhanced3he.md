# sivers tables, study `sbsenhanced3he`

Written by `plot-sivers_phicompare.ipynb` from `input-sbsenhanced3he.csv`, Q2 = 2.4 GeV^2, tol = 1.5. Regenerate, do not edit.

## Fits loaded (gallery/input-sbsenhanced3he.csv)

```
                                                                                                     file  replicas twin of
entry                                                                                                                      
world                                                                  ../data_world/out-world_sivers.dat       500       -
sbs+phifull                                                    data_phifull/out-sbsenhanced3he_sivers.dat       500       -
sbs+phi4seg24deg_phifullbin_x4counts  data_phi4seg24deg_phifullbin/out-sbsenhanced3he_sivers_x4counts.dat       500       -
sbs+phi4seg24deg_x4counts                        data_phi4seg24deg/out-sbsenhanced3he_sivers_x4counts.dat       500       -
```

## Fitted parameters, mean +- std over replicas

```
                                                     Nu                au                bu                Nd                ad                bd               kt2                  chi2
run                                                                                                                                                                                      
world                                 -0.0387 +- 0.0019  0.6663 +- 0.1130  4.1564 +- 1.0440  0.0576 +- 0.0154  0.4381 +- 0.2504  3.8314 +- 3.1709  0.1592 +- 0.0300   226.1234 +- 20.8210
sbs+phifull                           -0.0375 +- 0.0061  0.6325 +- 0.0457  4.1345 +- 0.7774  0.0500 +- 0.0046  0.3758 +- 0.0432  3.3100 +- 0.5135  0.1600 +- 0.0016  2104.1759 +- 64.4775
sbs+phi4seg24deg_phifullbin_x4counts  -0.0364 +- 0.0077  0.6142 +- 0.0742  4.2089 +- 0.9032  0.0493 +- 0.0058  0.3633 +- 0.0605  3.3576 +- 0.6358  0.1602 +- 0.0033  2104.7534 +- 64.5711
sbs+phi4seg24deg_x4counts             -0.0359 +- 0.0078  0.6113 +- 0.0660  4.2508 +- 0.9233  0.0496 +- 0.0057  0.3669 +- 0.0563  3.3237 +- 0.6561  0.1602 +- 0.0045   617.4845 +- 36.4799
```

## Error(world) / Error at representative x (larger = better)

```
                                                    x=0.05  x=0.1  x=0.2  x=0.3  x=0.4  x=0.5  x=0.6
variant run                                  quark                                                  
stat    sbs+phifull                          u        3.54   6.66   7.36   8.75   6.90   5.61   5.06
                                             d        9.11  46.49  57.67  50.52  38.29  32.73  35.36
        sbs+phi4seg24deg_phifullbin_x4counts u        2.69   3.72   4.45   5.17   4.35   3.82   3.67
                                             d        5.54  23.14  34.06  30.27  23.17  20.93  23.80
        sbs+phi4seg24deg_x4counts            u        2.53   3.67   4.09   4.52   3.93   3.49   3.43
                                             d        4.35  20.01  29.22  27.55  21.27  19.47  22.57
```

## Parameter replica-spread ratios

```
--- stat: std(world)/std, larger = better (NOT a precision comparison -- different params fixed, see above) ---
  world                                Nu=1.00  au=1.00  bu=1.00  Nd=1.00  ad=1.00  bd=1.00  kt2=1.00
  sbs+phifull                          Nu=0.31  au=2.48  bu=1.34  Nd=3.32  ad=5.80  bd=6.18  kt2=18.87
  sbs+phi4seg24deg_phifullbin_x4counts Nu=0.24  au=1.52  bu=1.16  Nd=2.68  ad=4.14  bd=4.99  kt2=9.09
  sbs+phi4seg24deg_x4counts            Nu=0.24  au=1.71  bu=1.13  Nd=2.72  ad=4.44  bd=4.83  kt2=6.64

--- stat: replica-std ratio to SoLID full-2pi (like-for-like -- this is the phi-cut effect) ---
  sbs+phifull                          Nu=1.000  au=1.000  bu=1.000  Nd=1.000  ad=1.000  bd=1.000  kt2=1.000   (vs sbs+phifull)
  sbs+phi4seg24deg_phifullbin_x4counts Nu=1.267  au=1.626  bu=1.162  Nd=1.240  ad=1.403  bd=1.238  kt2=2.075   (vs sbs+phifull)
  sbs+phi4seg24deg_x4counts            Nu=1.275  au=1.447  bu=1.188  Nd=1.221  ad=1.306  bd=1.278  kt2=2.843   (vs sbs+phifull)

Ratios marginally below 1.0 are 500-replica sampling noise (3.2%), not a
real reduction -- adding systematics cannot shrink an error. Use them as
the scale for how much of the near-1.0 numbers above is meaningful.
```
