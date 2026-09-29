# trans tables, study `enhanced-main`

Written by `plot-transversity_phicompare.ipynb` from `input-enhanced-main.csv`, Q2 = 2.4 GeV^2, tol = 7.04. Regenerate, do not edit.

## Fits loaded (gallery/input-enhanced-main.csv)

```
                                                         file  replicas twin of
entry                                                                          
world                     ../data_world/out-world_collins.dat       500       -
worldsyst                 ../data_world/out-world_collins.dat       500       -
phifull              data_phifull/out-enhanced3he_collins.dat       500       -
phifullsyst      data_phifull/out-enhanced3hesyst_collins.dat       500       -
phifull+nh3             data_phifull/out-enhanced_collins.dat       500       -
phifull+nh3syst     data_phifull/out-enhancedsyst_collins.dat       500       -
```

## Fitted parameters, mean +- std over replicas

```
                               Nu                 Nd                 a                 b                  c               kt2            Nu_err            Nd_err             a_err             b_err             c_err           kt2_err                  chi2                 ndof               edm
run                                                                                                                                                                                                                                                                                                   
world            0.4007 +- 0.0125  -0.4511 +- 0.0311  1.0008 +- 0.0537  3.0103 +- 0.3782   0.0000 +- 0.0000  0.2496 +- 0.0224  0.0123 +- 0.0010  0.0313 +- 0.0014  0.0558 +- 0.0010  0.3842 +- 0.0075        nan +- nan  0.0207 +- 0.0006   140.5382 +- 16.0417   141.0000 +- 0.0000  0.0000 +- 0.0000
worldsyst        0.4007 +- 0.0125  -0.4511 +- 0.0311  1.0008 +- 0.0537  3.0103 +- 0.3782   0.0000 +- 0.0000  0.2496 +- 0.0224  0.0123 +- 0.0010  0.0313 +- 0.0014  0.0558 +- 0.0010  0.3842 +- 0.0075        nan +- nan  0.0207 +- 0.0006   140.5382 +- 16.0417   141.0000 +- 0.0000  0.0000 +- 0.0000
phifull          0.4087 +- 0.0658  -0.4597 +- 0.0737  1.0027 +- 0.0264  2.9954 +- 0.0393  -0.0006 +- 0.2103  0.2500 +- 0.0010  0.0089 +- 0.0117  0.0098 +- 0.0132  0.0083 +- 0.0034  0.0299 +- 0.0022  0.0337 +- 0.0525  0.0010 +- 0.0000  1652.8844 +- 56.9147  1800.0000 +- 0.0000  0.0018 +- 0.0088
phifullsyst      0.4369 +- 0.1528  -0.4911 +- 0.1711  1.0099 +- 0.0538  2.9775 +- 0.0848   0.0143 +- 0.4444  0.2500 +- 0.0022  0.0355 +- 0.0379  0.0395 +- 0.0426  0.0201 +- 0.0108  0.0549 +- 0.0113  0.1420 +- 0.2021  0.0023 +- 0.0000  1653.2022 +- 56.8598  1800.0000 +- 0.0000  0.0018 +- 0.0063
phifull+nh3      0.4112 +- 0.0658  -0.4626 +- 0.0739  1.0039 +- 0.0266  2.9956 +- 0.0372  -0.0104 +- 0.2073  0.2500 +- 0.0009  0.0085 +- 0.0114  0.0095 +- 0.0129  0.0080 +- 0.0033  0.0284 +- 0.0021  0.0316 +- 0.0505  0.0010 +- 0.0000  2203.8213 +- 66.0262  2351.0000 +- 0.0000  0.0017 +- 0.0068
phifull+nh3syst  0.4391 +- 0.1463  -0.4939 +- 0.1641  1.0114 +- 0.0526  2.9786 +- 0.0768  -0.0055 +- 0.4252  0.2500 +- 0.0021  0.0339 +- 0.0372  0.0380 +- 0.0418  0.0191 +- 0.0102  0.0515 +- 0.0111  0.1259 +- 0.1777  0.0022 +- 0.0000  2204.0717 +- 65.9794  2351.0000 +- 0.0000  0.0016 +- 0.0060
```

## Error(world) / Error at representative x (larger = better)

```
                             x=0.05  x=0.1  x=0.2  x=0.3  x=0.4  x=0.5  x=0.6
variant   run         quark                                                  
stat      phifull     u        4.02   6.17   7.00  11.44  15.99  15.78  14.58
                      d       13.26  32.46  32.80  28.93  22.10  17.41  15.07
          phifull+nh3 u        4.44   8.46   9.99  15.28  18.45  17.07  15.56
                      d       13.66  35.52  36.55  32.34  24.41  18.95  16.26
stat+syst phifull     u        2.96   3.53   3.44   5.65   9.51  10.03   8.77
                      d        7.34  13.30  14.51  14.49  13.35  10.72   8.84
          phifull+nh3 u        3.10   4.59   4.68   7.44  11.31  11.12   9.65
                      d        7.91  14.52  15.49  15.54  14.78  12.04   9.93
```

## Tensor charge gT, full and truncated (0.05 < x < 0.6)

```
                            gT(u)              gT(d)           gT(u-d)    gT trunc (u-d)
run                                                                                     
world            0.5475 +- 0.1175  -0.3766 +- 0.1715  0.9241 +- 0.2111  0.7654 +- 0.1701
worldsyst        0.5475 +- 0.1175  -0.3766 +- 0.1715  0.9241 +- 0.2111  0.7654 +- 0.1701
phifull          0.5470 +- 0.0158  -0.3760 +- 0.0098  0.9230 +- 0.0200  0.7651 +- 0.0107
phifullsyst      0.5469 +- 0.0239  -0.3757 +- 0.0181  0.9225 +- 0.0274  0.7652 +- 0.0195
phifull+nh3      0.5469 +- 0.0130  -0.3760 +- 0.0094  0.9229 +- 0.0194  0.7651 +- 0.0087
phifull+nh3syst  0.5467 +- 0.0197  -0.3757 +- 0.0168  0.9223 +- 0.0278  0.7651 +- 0.0162
```

## Truncated gT(u-d): error and world/this

```
--- stat ---
  world                                E(gT u-d) = 0.1701   world/this =   1.00x
  phifull                              E(gT u-d) = 0.0107   world/this =  15.86x
  phifull+nh3                          E(gT u-d) = 0.0087   world/this =  19.65x
--- stat+syst ---
  world                                E(gT u-d) = 0.1701   world/this =   1.00x
  phifull                              E(gT u-d) = 0.0195   world/this =   8.71x
  phifull+nh3                          E(gT u-d) = 0.0162   world/this =  10.52x
```
