# trans tables, study `sbscombined`

Written by `plot-transversity_phicompare.ipynb` from `input-sbscombined.csv`, Q2 = 2.4 GeV^2, tol = 7.04. Regenerate, do not edit.

## Fits loaded (gallery/input-sbscombined.csv)

```
                                                                                                      file  replicas twin of
entry                                                                                                                       
world                                                                  ../data_world/out-world_collins.dat       500       -
sbs+phifull                                                    data_phifull/out-sbsenhanced3he_collins.dat       500       -
sbs+phi4seg24deg_phifullbin_x4counts  data_phi4seg24deg_phifullbin/out-sbsenhanced3he_collins_x4counts.dat       500       -
sbs+phi4seg24deg_x4counts                        data_phi4seg24deg/out-sbsenhanced3he_collins_x4counts.dat       500       -
```

## Fitted parameters, mean +- std over replicas

```
                                                    Nu                 Nd                 a                 b                 c               kt2            Nu_err            Nd_err             a_err             b_err             c_err           kt2_err                  chi2                 ndof               edm
run                                                                                                                                                                                                                                                                                                                       
world                                 0.4007 +- 0.0125  -0.4511 +- 0.0311  1.0008 +- 0.0537  3.0103 +- 0.3782  0.0000 +- 0.0000  0.2496 +- 0.0224  0.0123 +- 0.0010  0.0313 +- 0.0014  0.0558 +- 0.0010  0.3842 +- 0.0075        nan +- nan  0.0207 +- 0.0006   140.5382 +- 16.0417   141.0000 +- 0.0000  0.0000 +- 0.0000
sbs+phifull                           0.4063 +- 0.0618  -0.4570 +- 0.0693  1.0019 +- 0.0251  2.9967 +- 0.0358  0.0054 +- 0.2034  0.2500 +- 0.0011  0.0085 +- 0.0112  0.0094 +- 0.0126  0.0081 +- 0.0034  0.0290 +- 0.0021  0.0338 +- 0.0557  0.0010 +- 0.0000  2106.3210 +- 64.2837  2255.0000 +- 0.0000  0.0027 +- 0.0233
sbs+phi4seg24deg_phifullbin_x4counts  0.4176 +- 0.1278  -0.4695 +- 0.1426  1.0040 +- 0.0448  2.9877 +- 0.0808  0.0469 +- 0.3964  0.2501 +- 0.0022  0.0266 +- 0.0285  0.0296 +- 0.0321  0.0184 +- 0.0084  0.0594 +- 0.0067  0.1207 +- 0.1762  0.0021 +- 0.0000  2106.6600 +- 64.3631  2255.0000 +- 0.0000  0.0017 +- 0.0062
sbs+phi4seg24deg_x4counts             0.4119 +- 0.0904  -0.4633 +- 0.1013  1.0040 +- 0.0318  2.9944 +- 0.0713  0.0128 +- 0.2813  0.2500 +- 0.0022  0.0166 +- 0.0204  0.0183 +- 0.0230  0.0156 +- 0.0058  0.0565 +- 0.0045  0.0692 +- 0.1179  0.0022 +- 0.0000   619.1954 +- 36.6806   764.0000 +- 0.0000  0.0021 +- 0.0183
```

## Error(world) / Error at representative x (larger = better)

```
                                                    x=0.05  x=0.1  x=0.2  x=0.3  x=0.4  x=0.5  x=0.6
variant run                                  quark                                                  
stat    sbs+phifull                          u        4.09   6.45   7.42  11.81  16.59  16.86  15.83
                                             d       13.53  31.77  32.40  28.74  23.28  18.91  16.54
        sbs+phi4seg24deg_phifullbin_x4counts u        2.95   3.71   3.78   5.93   8.29   8.28   7.61
                                             d        7.58  15.19  17.45  14.52  11.20   9.00   7.80
        sbs+phi4seg24deg_x4counts            u        2.96   3.99   3.89   5.96   8.41   8.57   8.01
                                             d        7.62  15.85  18.20  14.84  11.32   9.18   8.09
```

## Tensor charge gT, full and truncated (0.05 < x < 0.6)

```
                                                 gT(u)              gT(d)           gT(u-d)    gT trunc (u-d)
run                                                                                                          
world                                 0.5475 +- 0.1175  -0.3766 +- 0.1715  0.9241 +- 0.2111  0.7654 +- 0.1701
sbs+phifull                           0.5469 +- 0.0155  -0.3760 +- 0.0096  0.9229 +- 0.0201  0.7650 +- 0.0107
sbs+phi4seg24deg_phifullbin_x4counts  0.5468 +- 0.0240  -0.3758 +- 0.0175  0.9225 +- 0.0286  0.7650 +- 0.0192
sbs+phi4seg24deg_x4counts             0.5469 +- 0.0237  -0.3758 +- 0.0164  0.9226 +- 0.0302  0.7651 +- 0.0209
```

## Truncated gT(u-d): error and world/this

```
--- stat ---
  world                                E(gT u-d) = 0.1701   world/this =   1.00x
  sbs+phifull                          E(gT u-d) = 0.0107   world/this =  15.86x
  sbs+phi4seg24deg_phifullbin_x4counts E(gT u-d) = 0.0192   world/this =   8.88x
  sbs+phi4seg24deg_x4counts            E(gT u-d) = 0.0209   world/this =   8.14x
```
