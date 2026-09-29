# trans tables, study `enhanced3he-main`

Written by `plot-transversity_phicompare.ipynb` from `input-enhanced3he-main.csv`, Q2 = 2.4 GeV^2, tol = 7.04. Regenerate, do not edit.

## Fits loaded (gallery/input-enhanced3he-main.csv)

```
                                                                                                           file  replicas twin of
entry                                                                                                                            
world                                                                       ../data_world/out-world_collins.dat       500       -
worldsyst                                                                   ../data_world/out-world_collins.dat       500       -
phifull                                                                data_phifull/out-enhanced3he_collins.dat       500       -
phifullsyst                                                        data_phifull/out-enhanced3hesyst_collins.dat       500       -
phi4seg24degFA_phifullbin_x4counts          data_phi4seg24degFA_phifullbin/out-enhanced3he_collins_x4counts.dat       500       -
phi4seg24degFA_phifullbin_x4countssyst  data_phi4seg24degFA_phifullbin/out-enhanced3hesyst_collins_x4counts.dat       500       -
```

## Fitted parameters, mean +- std over replicas

```
                                                      Nu                 Nd                 a                 b                  c               kt2            Nu_err            Nd_err             a_err             b_err             c_err           kt2_err                  chi2                 ndof               edm
run                                                                                                                                                                                                                                                                                                                          
world                                   0.4007 +- 0.0125  -0.4511 +- 0.0311  1.0008 +- 0.0537  3.0103 +- 0.3782   0.0000 +- 0.0000  0.2496 +- 0.0224  0.0123 +- 0.0010  0.0313 +- 0.0014  0.0558 +- 0.0010  0.3842 +- 0.0075        nan +- nan  0.0207 +- 0.0006   140.5382 +- 16.0417   141.0000 +- 0.0000  0.0000 +- 0.0000
worldsyst                               0.4007 +- 0.0125  -0.4511 +- 0.0311  1.0008 +- 0.0537  3.0103 +- 0.3782   0.0000 +- 0.0000  0.2496 +- 0.0224  0.0123 +- 0.0010  0.0313 +- 0.0014  0.0558 +- 0.0010  0.3842 +- 0.0075        nan +- nan  0.0207 +- 0.0006   140.5382 +- 16.0417   141.0000 +- 0.0000  0.0000 +- 0.0000
phifull                                 0.4087 +- 0.0658  -0.4597 +- 0.0737  1.0027 +- 0.0264  2.9954 +- 0.0393  -0.0006 +- 0.2103  0.2500 +- 0.0010  0.0089 +- 0.0117  0.0098 +- 0.0132  0.0083 +- 0.0034  0.0299 +- 0.0022  0.0337 +- 0.0525  0.0010 +- 0.0000  1652.8844 +- 56.9147  1800.0000 +- 0.0000  0.0018 +- 0.0088
phifullsyst                             0.4369 +- 0.1528  -0.4911 +- 0.1711  1.0099 +- 0.0538  2.9775 +- 0.0848   0.0143 +- 0.4444  0.2500 +- 0.0022  0.0355 +- 0.0379  0.0395 +- 0.0426  0.0201 +- 0.0108  0.0549 +- 0.0113  0.1420 +- 0.2021  0.0023 +- 0.0000  1653.2022 +- 56.8598  1800.0000 +- 0.0000  0.0018 +- 0.0063
phi4seg24degFA_phifullbin_x4counts      0.4304 +- 0.1311  -0.4838 +- 0.1466  1.0089 +- 0.0470  2.9836 +- 0.0740  -0.0003 +- 0.3824  0.2500 +- 0.0019  0.0274 +- 0.0313  0.0305 +- 0.0352  0.0173 +- 0.0089  0.0501 +- 0.0081  0.1063 +- 0.1592  0.0020 +- 0.0000  1653.0983 +- 56.8291  1800.0000 +- 0.0000  0.0020 +- 0.0081
phi4seg24degFA_phifullbin_x4countssyst  0.4573 +- 0.1916  -0.5139 +- 0.2144  1.0153 +- 0.0634  2.9658 +- 0.1111   0.0088 +- 0.5237  0.2500 +- 0.0028  0.0523 +- 0.0592  0.0582 +- 0.0662  0.0261 +- 0.0153  0.0698 +- 0.0226  0.1901 +- 0.2656  0.0029 +- 0.0000  1653.3759 +- 56.8507  1800.0000 +- 0.0000  0.0013 +- 0.0060
```

## Error(world) / Error at representative x (larger = better)

```
                                                    x=0.05  x=0.1  x=0.2  x=0.3  x=0.4  x=0.5  x=0.6
variant   run                                quark                                                  
stat      phifull                            u        4.02   6.17   7.00  11.44  15.99  15.78  14.58
                                             d       13.26  32.46  32.80  28.93  22.10  17.41  15.07
          phi4seg24degFA_phifullbin_x4counts u        2.93   3.64   3.71   6.16  10.11  10.63   9.46
                                             d        7.70  15.73  18.23  16.25  13.74  11.11   9.41
stat+syst phifull                            u        2.96   3.53   3.44   5.65   9.51  10.03   8.77
                                             d        7.34  13.30  14.51  14.49  13.35  10.72   8.84
          phi4seg24degFA_phifullbin_x4counts u        3.09   3.14   2.88   4.62   7.84   8.40   7.26
                                             d        6.11  10.38  11.98  11.68  10.89   8.86   7.26
```

## Tensor charge gT, full and truncated (0.05 < x < 0.6)

```
                                                   gT(u)              gT(d)           gT(u-d)    gT trunc (u-d)
run                                                                                                            
world                                   0.5475 +- 0.1175  -0.3766 +- 0.1715  0.9241 +- 0.2111  0.7654 +- 0.1701
worldsyst                               0.5475 +- 0.1175  -0.3766 +- 0.1715  0.9241 +- 0.2111  0.7654 +- 0.1701
phifull                                 0.5470 +- 0.0158  -0.3760 +- 0.0098  0.9230 +- 0.0200  0.7651 +- 0.0107
phifullsyst                             0.5469 +- 0.0239  -0.3757 +- 0.0181  0.9225 +- 0.0274  0.7652 +- 0.0195
phi4seg24degFA_phifullbin_x4counts      0.5468 +- 0.0230  -0.3757 +- 0.0171  0.9225 +- 0.0262  0.7652 +- 0.0174
phi4seg24degFA_phifullbin_x4countssyst  0.5467 +- 0.0256  -0.3754 +- 0.0221  0.9222 +- 0.0283  0.7653 +- 0.0225
```

## Truncated gT(u-d): error and world/this

```
--- stat ---
  world                                E(gT u-d) = 0.1701   world/this =   1.00x
  phifull                              E(gT u-d) = 0.0107   world/this =  15.86x
  phi4seg24degFA_phifullbin_x4counts   E(gT u-d) = 0.0174   world/this =   9.79x
--- stat+syst ---
  world                                E(gT u-d) = 0.1701   world/this =   1.00x
  phifull                              E(gT u-d) = 0.0195   world/this =   8.71x
  phi4seg24degFA_phifullbin_x4counts   E(gT u-d) = 0.0225   world/this =   7.55x
```
