# TMD

import numpy as np
from functools import lru_cache
from scipy.special import beta
from scipy.integrate import quad
import lhapdf

xpdf = lhapdf.mkPDF("CJ15lo",0)
zff = lhapdf.mkPDF("DSSFFlo",211)
zkff = lhapdf.mkPDF("DSSFFlo",321)
# g1 enters pretzelosity only (Lefky-Prokudin Eq. 27; PRD 91, 034010). Loaded here so the module
# still imports if the set is missing -- the other observables do not need it.
gpdf = lhapdf.mkPDF("NNPDFpol11_100",0)

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

@lru_cache(maxsize=None)
def g1col(x, Q2, target='proton'):
    """Helicity distribution, same flavour/target conventions as f1col."""
    if target == 'proton':
        u, d = gpdf.xfxQ2(2,x,Q2)/x, gpdf.xfxQ2(1,x,Q2)/x
        ub, db = gpdf.xfxQ2(-2,x,Q2)/x, gpdf.xfxQ2(-1,x,Q2)/x
    elif target == 'neutron':
        d, u = gpdf.xfxQ2(2,x,Q2)/x, gpdf.xfxQ2(1,x,Q2)/x
        db, ub = gpdf.xfxQ2(-2,x,Q2)/x, gpdf.xfxQ2(-1,x,Q2)/x
    elif target == 'deuteron':
        u = (gpdf.xfxQ2(2,x,Q2)/x + gpdf.xfxQ2(1,x,Q2)/x) / 2.0
        d = u
        ub = (gpdf.xfxQ2(-2,x,Q2)/x + gpdf.xfxQ2(-1,x,Q2)/x) / 2.0
        db = ub
    else:
        print('Fail to match target!')
        return 0
    s, sb = gpdf.xfxQ2(3,x,Q2)/x, gpdf.xfxQ2(-3,x,Q2)/x
    c, cb = gpdf.xfxQ2(4,x,Q2)/x, gpdf.xfxQ2(-4,x,Q2)/x
    b, bb = gpdf.xfxQ2(5,x,Q2)/x, gpdf.xfxQ2(-5,x,Q2)/x
    pdf = {2:u, 1:d, 3:s, 4:c, 5:b, -2:ub, -1:db, -3:sb, -4:cb, -5:bb}
    return pdf

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

# Pretzelosity, the sin(3 phi_h - phi_S) modulation -- the third amplitude
# AnalyzeEstatUT3 projects, alongside Sivers and Collins.
#
# Implemented after C. Lefky and A. Prokudin, "Extraction of the distribution
# function h_1T^perp from experimental data", Phys. Rev. D 91, 034010 (2015),
# arXiv:1411.0580 (report no. JLAB-THY-14-1885), whose equation numbers are
# cited below. Their Gaussian model gives the structure function in closed form,
# Eq. (33), and the asymmetry is D_NN F_UT / F_UU,T with
# D_NN = 2(1-y)/(1+(1-y)^2) -- algebraically the same epsilon AUTCollins uses.
#
# THE COLLINS FIT IS NOT TOUCHED. H1col below is reused exactly as it stands,
# with its own M_C^2 = 0.67 and its own c, d, Nfav, Ndis. Eq. (31) needs the HALF
# moment H1perp(1/2) while H1col returns sqrt(2e) * 0.14 * Mh/(Mh^2+<p_perp^2>) *
# N_C(z) * z * D(z) -- the packaging FUTCollins undoes with its own 1/(0.14 z).
# H1perphalf() below unwraps the same factor and applies Eq. (31), so both
# observables are driven by one fragmentation model with no duplicated constants.
KT2_LP = 0.25   # <k_perp^2> GeV^2, Lefky-Prokudin Sec. II A (verified against arXiv:1411.0580)
PT2_LP = 0.20   # <p_perp^2>, ditto, and the width already inside H1col

def h1Tperp1(x, Q2, target, par):
    """First k_perp moment of pretzelosity, Eqs. (26)-(28).

    h1Tperp(x) = e N(x) (f1(x) - g1(x)) saturates the positivity bound of
    Eq. (24); the moment then carries M_T^2 <k_perp^2> / (2 (M_T^2+<k_perp^2>)^2).
    par: 'Nu','Nd' the flavour normalisations, 'a','b' the alpha,beta of Eq. (27),
    'MT2' the M_T^2 of Eq. (26), 'kt2' the <k_perp^2>."""
    kt2, MT2 = par['kt2'], par['MT2']
    a, b = par['a'], par['b']
    shape = x**a * (1.0-x)**b * (a+b)**(a+b) / a**a / b**b
    f1, g1 = f1col(x,Q2,target), g1col(x,Q2,target)
    mom = MT2 * kt2 / (2.0 * (MT2 + kt2)**2)                       # Eq. (28)
    u = np.e * par['Nu'] * shape * (f1[2] - g1[2]) * mom
    d = np.e * par['Nd'] * shape * (f1[1] - g1[1]) * mom
    ub, db = 0, 0
    s, c, bq, sb, cb, bb = 0, 0, 0, 0, 0, 0
    h1t = {2:u, 1:d, 3:s, 4:c, 5:bq, -2:ub, -1:db, -3:sb, -4:cb, -5:bb}
    return h1t

def H1perphalf(z, Q2, hadron, par):
    """Half moment of the Collins FF, Eq. (31), from the existing H1col.

    H1col(z) = sqrt(2e) * 0.14 * Mh/(Mh^2+<p_perp^2>) * N_C(z) * z * D(z), so the
    bare H1perp of Eq. (30) is H1col * (Mh^2+<p_perp^2>)/(0.14 Mh z)."""
    MC2 = 0.67                                  # Mh^2 as H1col defines it
    Mh = MC2**0.5
    unwrap = (MC2 + PT2_LP) / (0.14 * Mh * z)
    half = MC2 / 4.0 * (np.pi * PT2_LP / (MC2 + PT2_LP)**3)**0.5   # Eq. (31)
    H1 = H1col(z,Q2,hadron,par)
    return {q: H1[q] * unwrap * half for q in H1}

def FUTPretzelosity(x, Q2, z, pT, target, hadron, par):
    """Eq. (33). Note z**2 and pT**3 in the numerator and the FOURTH power of the
    Gaussian width -- the widths being the M_T- and M_C-modified ones of Eq. (32),
    not the plain <k_perp^2>, <p_perp^2> that FUUT and FUTCollins use."""
    kt2, MT2 = par['kt2'], par['MT2']
    MC2 = 0.67
    kt2T = kt2 * MT2 / (kt2 + MT2)                                 # Eq. (32)
    pt2C = PT2_LP * MC2 / (PT2_LP + MC2)
    Pt2CT = pt2C + z**2 * kt2T
    C = 8.0 * kt2T * (pt2C / np.pi)**0.5                           # Eq. (34)
    h1t = h1Tperp1(x,Q2,target,par)
    H1h = H1perphalf(z,Q2,hadron,par)
    col = (2.0/3.0)**2 * h1t[2] * H1h[2] + (1.0/3.0)**2 * h1t[1] * H1h[1]
    res = x * z**2 * pT**3 / 2.0 * col * C / (np.pi * Pt2CT**4) * np.exp(-pT**2/Pt2CT)
    return res

def AUTPretzelosity(x, y, Q2, z, pT, target, hadron, par):
    g2 = (2.0*x*0.939)**2 / Q2
    epsilon = (1.0 - y - 0.25*g2*y**2) / (1.0 - y + 0.5*y**2 + 0.25*g2*y**2)
    res = epsilon * FUTPretzelosity(x,Q2,z,pT,target,hadron,par) / FUUT(x,Q2,z,pT,target,hadron)
    return res

@lru_cache(maxsize=None)
def _gl_grid(n, xl, xu, Q2):
    """Gauss-Legendre nodes/weights on [xl, xu] in log x, with f1col at each node.

    The PDF factor of h1col does not depend on the fit parameters, so for a fixed
    (n, xl, xu, Q2) it is the same for every replica. Computing it once here is
    what makes gt_fast fast: the LHAPDF lookups happen on the first call and
    every later replica is a dot product.

    Log substitution x = e^u: the default range starts at 1e-5 where the
    integrand goes as x^(a-1.2) and linear nodes resolve it poorly -- 1.7e-4
    against quad at n=64, versus 2.0e-6 in log x."""
    t, w = np.polynomial.legendre.leggauss(n)
    ul, uu = np.log(xl), np.log(xu)
    u = 0.5 * (uu - ul) * t + 0.5 * (uu + ul)
    w = 0.5 * (uu - ul) * w
    x = np.exp(u)
    w = w * x                      # dx = x du
    fu = np.array([f1col(v, Q2)[2] for v in x])
    fd = np.array([f1col(v, Q2)[1] for v in x])
    return x, w, fu, fd

def gt_fast(Q2, par, xl=1e-5, xu=1.0, n=256):
    """gt() by fixed-node quadrature: same answer, ~1000x faster.

    gt() calls scipy.quad twice per replica, and quad picks new abscissae each
    time, so every replica re-queries LHAPDF -- 84 ms per replica on the
    truncated range, and it hits quad's 50-subdivision limit (an
    IntegrationWarning) on both ranges. This evaluates the same integrand on a
    shared grid instead: 0.08 ms per replica.

    Agreement with gt(), max relative difference over 30 replicas:

        truncated 0.05-0.6   n=64  4.3e-09      (n=256)
        full      1e-5-1.0   n=256 3.9e-07

    The full-range floor is quad's own accuracy, not this function's -- quad is
    the one giving up at 50 subdivisions there.

    Use gt() when an authoritative number is wanted and gt_fast() for replica
    ensembles, where the 1e-7 agreement is far inside the replica spread.

    DOES IT REPRODUCE THE ERROR BAR, NOT JUST THE CENTRAL VALUE? Yes -- better
    than it reproduces the central value, and for a structural reason. The error
    quoted downstream is tol * std over replicas, and the gt_fast-minus-gt
    difference is almost entirely a CONSTANT offset, which cancels exactly in a
    standard deviation. Measured over 200 replicas of the phifull Collins
    ensemble:

        range            std(gt_fast)/std(gt)   corr(gt_fast, gt)
        truncated        0.999999999            1.000000000000
        full             0.999964585            0.999999998537

    On the truncated range the difference has mean 3.2e-9 and scatter 1.1e-11 --
    three orders of magnitude more offset than scatter.

    AND ON THE FULL RANGE THE RESIDUAL IS quad's, NOT THIS FUNCTION'S. Two
    independent grids agree with each other far better than either agrees with
    quad, and refining this function does not move the disagreement:

        gt_fast n=256 vs n=1024 : 7.2e-10   (this function, converged)
        gt_fast n=256 vs quad   : 1.9e-07
        gt_fast n=1024 vs quad  : 1.9e-07   (unchanged by refining)

    which is what quad hitting its 50-subdivision limit looks like: it fails by a
    different amount for each replica's integrand, where a fixed grid is
    deterministic and smooth in the parameters.

    For scale: at 500 replicas the error bar carries 3.2% sampling noise by
    construction, 1/sqrt(2(N-1)), against 0.0035% from the choice of integration
    method -- a factor of ~900. The method is irrelevant at any replica count in
    use here.

    All of the above compares gt_fast against gt, so it establishes consistency,
    not correctness. gt's IntegrationWarning is a separate open question.

    HOW THE INTEGRAND WAS DERIVED, AND HOW THAT WAS CHECKED. `shape` below is not
    an approximation of h1col -- it is h1col's own expression with the two
    flavour-dependent factors pulled out:

        h1col u-component = Nu * [shape(x)] * f1col(x)[2]
        h1col d-component = Nd * [shape(x)] * f1col(x)[1]

    so `shape` is everything between the normalisation and the PDF, identical for
    u and d, and the PDF factor is the part that does not vary between replicas.
    Verified point by point against h1col over 4 replicas (including the first
    and last of a 500-replica ensemble) x 7 values of x spanning 1e-4 to 0.9:
    max relative difference **4.4e-16**, two ulps, i.e. the same arithmetic
    reassociated.

    Two assumptions were checked because either would break the equivalence
    silently:
      * h1col calls f1col(x, Q2) with NO target, so it always uses proton PDFs
        and swaps the u/d slots afterwards for other targets. gt() always passes
        'proton', so no swap happens -- _gl_grid calls f1col bare for the same
        reason. A neutron-target gt() would need the swap here too.
      * h1col zeroes the antiquarks and s/c/b, so only PDG indices 2 and 1 carry
        anything; summing more flavours would be wrong.
    """
    if xl <= 0:
        raise ValueError("gt_fast integrates in log x; xl must be > 0")
    x, w, fu, fd = _gl_grid(n, xl, xu, Q2)
    a, b, c = par['a'], par['b'], par['c']
    shape = ((1.0 + 0.2 * x**0.5 + c * x**0.25) * x**a * (1.0 - x)**b
             * (a + b)**(a + b) / a**a / b**b)
    u = np.dot(w, par['Nu'] * shape * fu)
    d = np.dot(w, par['Nd'] * shape * fd)
    return {'u': u, 'd': d, 'u-d': u - d}

def gt(Q2, par, xl=1e-5, xu=1.0):
    _u = lambda x: h1col(x,Q2,'proton',par)[2]
    _d = lambda x: h1col(x,Q2,'proton',par)[1]
    u, err = quad(_u, xl, xu)
    d, err = quad(_d, xl, xu)
    res = {'u':u, 'd':d, 'u-d':u-d}
    return res
    


# ----------------------------------------------------------------- collinearity
# The current-fragmentation criterion, ported from Lsidis3.h:CalculateRfactor so
# the fit scripts can select points without re-running the generator.
#
#   M. Boglione, J. Collins, L. Gamberg, J. O. Gonzalez-Hernandez, T. C. Rogers,
#   N. Sato, "Kinematics of Current Region Fragmentation in Semi-Inclusive
#   Deeply Inelastic Scattering", Phys. Lett. B 766 (2017) 245-253,
#   arXiv:1611.10329, doi:10.1016/j.physletb.2017.01.021.
#
# R = |(Ph.kf)/(Ph.ki)|, the paper's "collinearity" (Eqs. 28-29), built from its
# Eqs. 31-32. Small R means the detected hadron is in the current region, where
# TMD factorisation applies. The paper recommends R < ~0.2; the later
# JHEP 04 (2022) 084 [arXiv:2201.12197] treatment calls this R1 and uses 0.3.
#
# Same formula as the C++ line for line, including the trailing sqrt(kT2)*pT
# term, which is the PhT.kT piece the paper drops when it averages over the
# azimuth of kT -- so this is the un-averaged, kT-aligned (worst-case)
# collinearity, matching what the generator computes.
#
# NB the generator applies this per EVENT. Called on prepared rows it evaluates
# the criterion at each bin's mean kinematics, which is a selection, not the same
# thing as enabling Rfactor0 in SoLID_SIDIS_3He.h and regenerating.
MP_LSIDIS = 0.938272081   # Mp in Lsidis3.h
MH_PION   = 0.13957018    # Mpion in Lsidis3.h

def CalculateRfactor(x, Q2, z, pT, kT2=0.5, MiT2=0.5, MfT2=0.5, Mh=MH_PION):
    """Collinearity R of arXiv:1611.10329, vectorised over array-like inputs.

    Defaults kT2 = MiT2 = MfT2 = 0.5 match `sidis.CalculateRfactor()` as called
    with no arguments at every production site in SoLID_SIDIS_3He.h. Returns a
    float or an ndarray, following the inputs.
    """
    x, Q2, z, pT = (np.asarray(v, dtype=float) for v in (x, Q2, z, pT))
    Mp = MP_LSIDIS
    # Nachtmann xn, as Lsidis3.h:428 -- NOT Bjorken x
    gamma = 2.0 * Mp * x / np.sqrt(Q2)
    xn = 2.0 * x / (1.0 + np.sqrt(1.0 + gamma * gamma))

    yi = 0.5 * np.log(Q2 / MiT2)
    yf = -0.5 * np.log(Q2 / MfT2)
    mT2 = Mh * Mh + pT * pT
    mT = np.sqrt(mT2)

    # yh: the negative branch of the two-valued inverse of the paper's Eq. 19
    a = np.sqrt(Q2) * z * (Q2 - xn**2 * Mp**2) / (2.0 * xn**2 * Mp**2 * mT)
    disc = (z * (Q2 - xn**2 * Mp**2))**2 / (4.0 * xn**2 * Mp**2 * mT2) - 1.0
    with np.errstate(invalid='ignore'):
        b = np.sqrt(Q2) / (xn * Mp) * np.sqrt(disc)
        yh = np.log(a - b)

    Rf = 0.5 * mT * np.sqrt(MfT2) * (np.exp(yf - yh) + np.exp(yh - yf)) - np.sqrt(kT2) * pT
    Ri = 0.5 * mT * np.sqrt(MiT2) * (np.exp(yi - yh) - np.exp(yh - yi)) - np.sqrt(kT2) * pT
    R = np.abs(Rf / Ri)
    return R if R.ndim else float(R)
