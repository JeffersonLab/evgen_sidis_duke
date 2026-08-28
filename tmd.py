# TMD

import numpy as np
from functools import lru_cache
from scipy.special import beta
from scipy.integrate import quad
import lhapdf

xpdf = lhapdf.mkPDF("CJ15lo",0)
zff = lhapdf.mkPDF("DSSFFlo",211)
zkff = lhapdf.mkPDF("DSSFFlo",321)

# f1col/D1col are pure functions of (x or z, Q2, target/hadron) - independent of
# any fit parameter. In a Minuit fit the kinematics of each data row are fixed for
# the whole run while only the model parameters vary, so the same LHAPDF queries
# repeat tens of thousands of times across replicas and minimizer iterations.
# Caching collapses that to one LHAPDF call per unique row. Safe: callers only
# read the returned dict, never mutate it.
#
# Worth 5.7x on the fit path, measured 2026-08-20 by removing it and running
# ./fitcollins.py enhanced3he datacollins_phifull: 2m30s with, 14m17s without.
# That same run also proves it changes nothing -- the uncached output was
# byte-identical to the cached one. (Only ~1.2-1.3x on the notebook h1col/gt
# paths, where per-call arithmetic dominates.) Evidence: check.md.
@lru_cache(maxsize=None)
def f1col(x, Q2, target='proton'):
    if target == 'proton':
        u, d = xpdf.xfxQ2(2,x,Q2)/x, xpdf.xfxQ2(1,x,Q2)/x
        ub, db = xpdf.xfxQ2(-2,x,Q2)/x, xpdf.xfxQ2(-1,x,Q2)/x
    elif target == 'neutron':
        d, u = xpdf.xfxQ2(2,x,Q2)/x, xpdf.xfxQ2(1,x,Q2)/x
        db, ub = xpdf.xfxQ2(-2,x,Q2)/x, xpdf.xfxQ2(-1,x,Q2)/x
    elif target == 'deuteron':
        u = (xpdf.xfxQ2(2,x,Q2)/x + xpdf.xfxQ2(1,x,Q2)/x) / 2.0
        d = (xpdf.xfxQ2(2,x,Q2)/x + xpdf.xfxQ2(1,x,Q2)/x) / 2.0
        ub = (xpdf.xfxQ2(-2,x,Q2)/x + xpdf.xfxQ2(-1,x,Q2)/x) / 2.0
        db = (xpdf.xfxQ2(-2,x,Q2)/x + xpdf.xfxQ2(-1,x,Q2)/x) / 2.0
    else:
        print('Fail to match target!')
        return 0
    s, sb = xpdf.xfxQ2(3,x,Q2)/x, xpdf.xfxQ2(-3,x,Q2)/x
    c, cb = xpdf.xfxQ2(4,x,Q2)/x, xpdf.xfxQ2(-4,x,Q2)/x
    b, bb = xpdf.xfxQ2(5,x,Q2)/x, xpdf.xfxQ2(-5,x,Q2)/x
    pdf = {2:u, 1:d, 3:s, 4:c, 5:b, -2:ub, -1:db, -3:sb, -4:cb, -5:bb}
    return pdf

@lru_cache(maxsize=None)
def D1col(z, Q2, hadron='pi+'):
    u, d, s, c, b = 0, 0, 0, 0, 0
    ub, db, sb, cb, bb = 0, 0, 0, 0, 0
    if hadron == 'pi+' or hadron == 'h+':
        u, d, s, c, b = zff.xfxQ2(2,z,Q2)/z, zff.xfxQ2(1,z,Q2)/z, zff.xfxQ2(3,z,Q2)/z, zff.xfxQ2(4,z,Q2)/z, zff.xfxQ2(5,z,Q2)/z
        ub, db, sb, cb, bb = zff.xfxQ2(-2,z,Q2)/z, zff.xfxQ2(-1,z,Q2)/z, zff.xfxQ2(-3,z,Q2)/z, zff.xfxQ2(-4,z,Q2)/z, zff.xfxQ2(-5,z,Q2)/z
    elif hadron == 'pi-' or hadron == 'h-':
        ub, db, sb, cb, bb = zff.xfxQ2(2,z,Q2)/z, zff.xfxQ2(1,z,Q2)/z, zff.xfxQ2(3,z,Q2)/z, zff.xfxQ2(4,z,Q2)/z, zff.xfxQ2(5,z,Q2)/z
        u, d, s, c, b = zff.xfxQ2(-2,z,Q2)/z, zff.xfxQ2(-1,z,Q2)/z, zff.xfxQ2(-3,z,Q2)/z, zff.xfxQ2(-4,z,Q2)/z, zff.xfxQ2(-5,z,Q2)/z
    elif hadron == 'k+' or hadron == 'K+':
        u, d, s, c, b = zkff.xfxQ2(2,z,Q2)/z, zkff.xfxQ2(1,z,Q2)/z, zkff.xfxQ2(3,z,Q2)/z, zkff.xfxQ2(4,z,Q2)/z, zkff.xfxQ2(5,z,Q2)/z
        ub, db, sb, cb, bb = zkff.xfxQ2(-2,z,Q2)/z, zkff.xfxQ2(-1,z,Q2)/z, zkff.xfxQ2(-3,z,Q2)/z, zkff.xfxQ2(-4,z,Q2)/z, zkff.xfxQ2(-5,z,Q2)/z   
    elif hadron == 'k-' or hadron == 'K-':
        u, d, s, c, b = zkff.xfxQ2(-2,z,Q2)/z, zkff.xfxQ2(-1,z,Q2)/z, zkff.xfxQ2(-3,z,Q2)/z, zkff.xfxQ2(-4,z,Q2)/z, zkff.xfxQ2(-5,z,Q2)/z
        ub, db, sb, cb, bb = zkff.xfxQ2(2,z,Q2)/z, zkff.xfxQ2(1,z,Q2)/z, zkff.xfxQ2(3,z,Q2)/z, zkff.xfxQ2(4,z,Q2)/z, zkff.xfxQ2(5,z,Q2)/z
    else:
        print('Fail to match hadron!')
        return 0
    ff = {2:u, 1:d, 3:s, 4:c, 5:b, -2:ub, -1:db, -3:sb, -4:cb, -5:bb}
    return ff

def FUUT(x, Q2, z, pT, target, hadron):
    kt2, pt2 = 0.25, 0.20
    Pt2 = pt2 + z*z*kt2
    pdf = f1col(x,Q2,target)
    ff = D1col(z,Q2,hadron)
    col = (2.0/3.0)**2 * (pdf[2]*ff[2] + pdf[-2]*ff[-2] + pdf[4]*ff[4] + pdf[-4]*ff[-4]) \
        + (1.0/3.0)**2 * (pdf[1]*ff[1] + pdf[-1]*ff[-1] + pdf[3]*ff[3] + pdf[-3]*ff[-3] + pdf[5]*ff[5] + pdf[-5]*ff[-5])
    res = x * col * np.exp(-pT**2 / Pt2) / (np.pi*Pt2)
    return res

def f1Tperp1(x, Q2, target, par):
    pdf = f1col(x,Q2)
    A = par['Nu'] * (1.0+par['cu']*x) * x**par['au'] * (1.0-x)**par['bu'] * (par['au']+par['bu'])**(par['au']+par['bu']) / par['au']**par['au'] / par['bu']**par['bu'] * pdf[2]
    B = par['Nd'] * (1.0+par['cd']*x) * x**par['ad'] * (1.0-x)**par['bd'] * (par['ad']+par['bd'])**(par['ad']+par['bd']) / par['ad']**par['ad'] / par['bd']**par['bd'] * pdf[1]
    Ab = par['Nub'] * pdf[-2]
    Bb = par['Ndb'] * pdf[-1]
    if target == 'proton':
        u, d = A, B
        ub, db = Ab, Bb
    elif target == 'neutron':
        u, d = B, A
        ub, db = Bb, Ab
    elif target == 'deuteron':
        u, d = (A+B)/2.0, (A+B)/2.0
        ub, db = (Ab+Bb)/2.0, (Ab+Bb)/2.0
    s, sb, c, cb, b, bb = 0, 0, 0, 0, 0, 0
    f1t1 = {2:u, 1:d, 3:s, 4:c, 5:b, -2:ub, -1:db, -3:sb, -4:cb, -5:bb}
    return f1t1

def FUTSivers(x, Q2, z, pT, target, hadron, par):
    kt2, pt2 = par['kt2'], 0.20
    Pt2 = pt2 + z*z*kt2
    fac = -2.0*z*0.939*pT/Pt2
    f1t1 = f1Tperp1(x,Q2,target,par)
    ff = D1col(z,Q2,hadron)
    col = (2.0/3.0)**2 * (f1t1[2]*ff[2] + f1t1[-2]*ff[-2] + f1t1[4]*ff[4] + f1t1[-4]*ff[-4]) \
        + (1.0/3.0)**2 * (f1t1[1]*ff[1] + f1t1[-1]*ff[-1] + f1t1[3]*ff[3] + f1t1[-3]*ff[-3] + f1t1[5]*ff[5] + f1t1[-5]*ff[-5])
    res = x * fac * col * np.exp(-pT**2/Pt2) / (np.pi*Pt2)
    return res

def AUTSivers(x, Q2, z, pT, target, hadron, par):
    res = FUTSivers(x,Q2,z,pT,target,hadron,par) / FUUT(x,Q2,z,pT,target,hadron)
    return res

def h1col(x, Q2, target, par):
    pdf = f1col(x,Q2)
    A = par['Nu'] * (1.0 + 0.2*x**0.5 + par['c']*x**0.25) * x**par['a'] * (1.0-x)**par['b'] * (par['a']+par['b'])**(par['a']+par['b']) / par['a']**par['a'] / par['b']**par['b'] * pdf[2]
    B = par['Nd'] * (1.0 + 0.2*x**0.5 + par['c']*x**0.25) * x**par['a'] * (1.0-x)**par['b'] * (par['a']+par['b'])**(par['a']+par['b']) / par['a']**par['a'] / par['b']**par['b'] * pdf[1]
    if target == 'proton':
        u, d = A, B
    elif target == 'neutron':
        u, d = B, A
    elif target == 'deuteron':
        u, d = (A+B)/2.0, (A+B)/2.0
    ub, db = 0, 0
    s, c, b, sb, cb, bb = 0, 0, 0, 0, 0, 0
    h1 = {2:u, 1:d, 3:s, 4:c, 5:b, -2:ub, -1:db, -3:sb, -4:cb, -5:bb}
    return h1

def H1col(z, Q2, hadron, par):
    ff = D1col(z,Q2)
    Nfav = 1.0
    Ndis = -1.0
    c = -2.36
    d = 2.12
    Mh = 0.67**0.5
    factor = (2.0*np.e)**0.5 * 0.14 * Mh / (Mh**2 + 0.20)
    FAV = factor * Nfav * ((1.0 - c - d) + c*z + d*z**2) * z * ff[2]
    DIS = factor * Ndis * ((1.0 - c - d) + c*z + d*z**2) * z * ff[1]
    if hadron == 'pi+' or hadron == 'h+':
        u, d = FAV, DIS
        ub, db = DIS, FAV
    elif hadron == 'pi-' or hadron == 'h-':
        u, d = DIS, FAV
        ub, db = FAV, DIS
    s, c, b, sb, cb, bb = 0, 0, 0, 0, 0, 0
    H1 = {2:u, 1:d, 3:s, 4:c, 5:b, -2:ub, -1:db, -3:sb, -4:cb, -5:bb}
    return H1

def FUTCollins(x, Q2, z, pT, target, hadron, par):
    kt2 = par['kt2']
    pt2 = 0.67 * 0.20 / (0.67 + 0.20)
    Pt2 = pt2 + z**2 * kt2
    factor = pt2 * pT / (0.14 * z * Pt2)
    h1 = h1col(x,Q2,target,par)
    H1 = H1col(z,Q2,hadron,par)
    col = (2.0/3.0)**2 * h1[2] * H1[2] + (1.0/3.0)**2 * h1[1] * H1[1]
    res = x * factor * col * np.exp(-pT**2/Pt2) / (np.pi*Pt2)
    return res

def AUTCollins(x, y, Q2, z, pT, target, hadron, par):
    g2 = (2.0*x*0.939)**2 / Q2
    epsilon = (1.0 - y - 0.25*g2*y**2) / (1.0 - y + 0.5*y**2 + 0.25*g2*y**2)
    res = epsilon * FUTCollins(x,Q2,z,pT,target,hadron,par) / FUUT(x,Q2,z,pT,target,hadron)
    return res

def gt(Q2, par, xl=1e-5, xu=1.0):
    _u = lambda x: h1col(x,Q2,'proton',par)[2]
    _d = lambda x: h1col(x,Q2,'proton',par)[1]
    u, err = quad(_u, xl, xu)
    d, err = quad(_d, xl, xu)
    res = {'u':u, 'd':d, 'u-d':u-d}
    return res
    

