"""Variant 1 — six-link linkage: synthesis, positions, velocity & acceleration plans, sheet layout."""
import math

# ---------------- task data (variant 1) ----------------
VARIANT = 1
DATA = dict(HF=70, L1=350, L2=150, lEF=200, lED=210, n1=210, G2=38, G5=175, IS2=350, Fmax=78)
HF = DATA['HF']/1000; L1 = DATA['L1']/1000; L2 = DATA['L2']/1000
lEF = DATA['lEF']/1000; lED = DATA['lED']/1000; n1 = DATA['n1']
FMAX = DATA['Fmax']*100.0
lCD = 0.9*lED
ALPHA = 50.0          # angle CDE of the bell-crank (link 3)
BETA = 3.0            # chosen from 3..5 deg
L1S = 200.0           # drawing length chosen for L1
MU = L1/L1S           # 0.00175 m/mm
MUV = 0.01852         # (m/s)/mm  = V_B/pb with pb = 50 mm (notebook §2, 6), checked in calc.py
MUA = 0.2909          # (m/s^2)/mm = a_B/πb with πb = 70 mm (notebook §3, 3), checked in calc.py
MUF = 200.0           # N/mm
NPOS = 8

# ---------------- helpers ----------------
def circ_int(c1, r1, c2, r2):
    dx, dy = c2[0]-c1[0], c2[1]-c1[1]; d = math.hypot(dx, dy)
    a = (r1*r1-r2*r2+d*d)/(2*d); h = math.sqrt(max(r1*r1-a*a, 0))
    ux, uy = dx/d, dy/d; px, py = c1[0]+a*ux, c1[1]+a*uy
    return (px-h*uy, py+h*ux), (px+h*uy, py-h*ux)
def rot(p, ang_deg, s=1.0):
    a = math.radians(ang_deg); c, sn = math.cos(a), math.sin(a)
    return ((p[0]*c-p[1]*sn)*s, (p[0]*sn+p[1]*c)*s)
def sub(p, q): return (p[0]-q[0], p[1]-q[1])
def add(p, q): return (p[0]+q[0], p[1]+q[1])
def scl(p, s): return (p[0]*s, p[1]*s)
def mag(v): return math.hypot(v[0], v[1])
def cross_k(w, r): return (-w*r[1], w*r[0])
def solve2(a11, a12, a21, a22, b1, b2):
    det = a11*a22-a12*a21; return ((b1*a22-a12*b2)/det, (a11*b2-b1*a21)/det)
def ang(v): return math.degrees(math.atan2(v[1], v[0]))

# ---------------- synthesis (drawing mm, D at origin, y up) ----------------
H = HF/MU; L2S = L2/MU; EF = lEF/MU; ED = lED/MU; CD = lCD/MU
D = (0.0, 0.0); A = (L1S, -L2S)
_b = math.radians(BETA)
E0p = (-ED*math.sin(_b), -ED*math.cos(_b))
F0p = (0.0, E0p[1]-math.sqrt(EF**2-E0p[0]**2))
F0 = (0.0, F0p[1]+H)
_p1, _p2 = circ_int(D, ED, F0, EF); E0 = _p1 if _p1[0] < _p2[0] else _p2
C0 = rot(E0, ALPHA, CD/ED); C0p = rot(E0p, ALPHA, CD/ED)
AC0 = math.dist(A, C0); AC0p = math.dist(A, C0p)
ABS = (AC0-AC0p)/2; BCS = (AC0+AC0p)/2
PSI = ang(E0p)-ang(E0)
TH0 = ang(sub(C0, A)); TH0P = ang(sub(A, C0p))
B0 = (A[0]+ABS*math.cos(math.radians(TH0)), A[1]+ABS*math.sin(math.radians(TH0)))
B0p = (A[0]+ABS*math.cos(math.radians(TH0P)), A[1]+ABS*math.sin(math.radians(TH0P)))
PHI_W = (TH0-TH0P) % 360; PHI_I = 360-PHI_W
AD = math.hypot(L1, L2)

W1 = math.pi*n1/30

def position(theta, Cprev):
    B = (A[0]+ABS*math.cos(math.radians(theta)), A[1]+ABS*math.sin(math.radians(theta)))
    q1, q2 = circ_int(B, BCS, D, CD)
    C = q1 if math.dist(q1, Cprev) < math.dist(q2, Cprev) else q2
    E = rot(C, -ALPHA, ED/CD)
    F = (0.0, E[1]-math.sqrt(EF**2-E[0]**2))
    S2 = ((B[0]+C[0])/2, (B[1]+C[1])/2)
    return dict(B=B, C=C, E=E, F=F, S2=S2, theta=theta)

def kinematics(P):
    rAB = scl(sub(P['B'], A), MU); rCB = scl(sub(P['C'], P['B']), MU); rCD = scl(sub(P['C'], D), MU)
    rED = scl(sub(P['E'], D), MU); rFE = scl(sub(P['F'], P['E']), MU)
    VB = cross_k(-W1, rAB)                      # crank turns clockwise
    w2, w3 = solve2(-rCB[1], rCD[1], rCB[0], -rCD[0], -VB[0], -VB[1])
    VC = cross_k(w3, rCD); VCB = cross_k(w2, rCB); VE = cross_k(w3, rED)
    w4 = VE[0]/rFE[1]; VFE = cross_k(w4, rFE); VF = add(VE, VFE)
    VS2 = scl(add(VB, VC), 0.5)
    aB = scl(rAB, -W1*W1)
    rhs = sub(scl(rCD, -w3*w3), sub(aB, scl(rCB, w2*w2)))
    e2, e3 = solve2(-rCB[1], rCD[1], rCB[0], -rCD[0], rhs[0], rhs[1])
    aCBn = scl(rCB, -w2*w2); aCBt = cross_k(e2, rCB); aCDn = scl(rCD, -w3*w3); aCDt = cross_k(e3, rCD)
    aC = add(aCDn, aCDt); aE = add(scl(rED, -w3*w3), cross_k(e3, rED))
    aFEn = scl(rFE, -w4*w4); e4 = (aE[0]+aFEn[0])/rFE[1]; aFEt = cross_k(e4, rFE)
    aF = add(add(aE, aFEn), aFEt); aS2 = scl(add(aB, aC), 0.5)
    return dict(VB=VB, VC=VC, VCB=VCB, VE=VE, VFE=VFE, VF=VF, VS2=VS2, w2=w2, w3=w3, w4=w4,
                aB=aB, aCBn=aCBn, aCBt=aCBt, aCDn=aCDn, aCDt=aCDt, aC=aC, aE=aE, aFEn=aFEn,
                aFEt=aFEt, aF=aF, aS2=aS2, e2=e2, e3=e3, e4=e4)

POS = []; _Cp = C0
for i in range(NPOS):
    P = position(TH0-360.0/NPOS*i, _Cp); _Cp = P['C']
    P['K'] = kinematics(P); P['i'] = i
    P['sF'] = F0[1]-P['F'][1]
    POS.append(P)
POS0P = position(TH0P, C0p)

# transmission angle / pressure angle over a full turn
GAMMA_MIN = 180.0; EF_INC_MAX = 0.0; _Cp = C0
for k in range(3600):
    P = position(TH0-0.1*k, _Cp); _Cp = P['C']
    u = sub(P['B'], P['C']); v = sub(D, P['C'])
    g = math.degrees(math.acos(max(-1, min(1, (u[0]*v[0]+u[1]*v[1])/(mag(u)*mag(v))))))
    GAMMA_MIN = min(GAMMA_MIN, g, 180-g)
    EF_INC_MAX = max(EF_INC_MAX, math.degrees(math.asin(abs(P['E'][0])/EF)))

# ---------------- F_re diagram (shape digitised from the task sheet) ----------------
FRE_PTS = [(0.0, 0.0), (0.28, 0.0), (0.44, 0.49), (0.63, 0.83), (0.79, 0.99), (0.87, 1.0), (0.94, 0.96), (1.0, 0.89)]
def _pchip_slopes(xs, ys):
    n = len(xs); h = [xs[i+1]-xs[i] for i in range(n-1)]; dl = [(ys[i+1]-ys[i])/h[i] for i in range(n-1)]
    m = [0.0]*n; m[0] = dl[0]; m[-1] = dl[-1]
    for i in range(1, n-1):
        if dl[i-1]*dl[i] <= 0: m[i] = 0.0
        else:
            w1 = 2*h[i]+h[i-1]; w2 = h[i]+2*h[i-1]; m[i] = (w1+w2)/(w1/dl[i-1]+w2/dl[i])
    return m
_xs = [p[0] for p in FRE_PTS]; _ys = [p[1] for p in FRE_PTS]; _ms = _pchip_slopes(_xs, _ys)
def fre_shape(s):
    s = max(0.0, min(1.0, s))
    for i in range(len(_xs)-1):
        if _xs[i] <= s <= _xs[i+1]:
            hh = _xs[i+1]-_xs[i]; t = (s-_xs[i])/hh
            h00 = 2*t**3-3*t**2+1; h10 = t**3-2*t**2+t; h01 = -2*t**3+3*t**2; h11 = t**3-t**2
            return max(0.0, h00*_ys[i]+h10*hh*_ms[i]+h01*_ys[i+1]+h11*hh*_ms[i+1])
    return 0.0

# ---------------- sheet layout (mm, origin = bottom-left corner of the grid) ----------------
GRID_W, GRID_H = 380, 270
XD, YD = 90.0, 256.0
def S(p): return (XD+p[0], YD+p[1])
# sheet 1: positions plan, F_re diagram, acceleration plan of the thick position
PA_POS = 2; PA = (250.0, 89.0)                                # acceleration-plan pole
PA_CAP = (268.0, 66.0)                                        # acceleration-plan caption (left-aligned)
DIAG_X = 120.0                                                # S_F axis of the F_re diagram
L1_DIM_Y = 133.0; L2_DIM_X = 328.0; HF_DIM_X = 72.0

def vplan(i):
    K = POS[i]['K']; s = 1/MUV
    return dict(p=(0.0, 0.0), b=scl(K['VB'], s), c=scl(K['VC'], s), e=scl(K['VE'], s),
                f=scl(K['VF'], s), s2=scl(K['VS2'], s))
def aplan(i):
    K = POS[i]['K']; s = 1/MUA
    b = scl(K['aB'], s)
    return dict(pi=(0.0, 0.0), b=b, n2=add(b, scl(K['aCBn'], s)), c=scl(K['aC'], s),
                n3=scl(K['aCDn'], s), e=scl(K['aE'], s), n4=add(scl(K['aE'], s), scl(K['aFEn'], s)),
                f=scl(K['aF'], s), s2=scl(K['aS2'], s))

# sheet 2: the 8 velocity plans, 4 per row, each centred in its cell
V2_COLS = (50.0, 143.0, 236.0, 329.0); V2_ROWS = (196.0, 78.0)
def _plan_center(i):
    pts = list(vplan(i).values()); xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return ((min(xs)+max(xs))/2, (min(ys)+max(ys))/2)
PV2 = {}
VLBL = {(5, 'c'): (-3.0, -0.4), (5, 's2'): (-3.2, 0.8), (5, 'b'): (-2.2, -2.6)}   # hand-placed labels where points crowd
for _i in range(NPOS):
    _c = _plan_center(_i); _cx = V2_COLS[_i % 4]; _cy = V2_ROWS[_i // 4]
    PV2[_i] = (round(_cx-_c[0], 1), round(_cy-_c[1], 1))

if __name__ == '__main__':
    print(f"mu={MU} H*={H:.3f} L2*={L2S:.3f} EF*={EF:.3f} ED*={ED:.3f} CD*={CD:.3f}")
    print(f"AC0={AC0:.3f} AC0'={AC0p:.3f} AB*={ABS:.3f} BC*={BCS:.3f} psi={PSI:.3f} phiW={PHI_W:.3f} gamma_min={GAMMA_MIN:.2f} EFinc={EF_INC_MAX:.2f}")
    for P in POS:
        K = P['K']
        print(P['i'], f"sF={P['sF']:.2f} s={P['sF']/H:.3f} fre={fre_shape(P['sF']/H):.3f}", f"VF={K['VF'][1]:+.4f}")
    print('sheet D', S(D), 'A', S(A), 'F0', S(F0), "F0'", S(F0p))
