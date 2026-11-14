"""Rounded 'graphical chain' values exactly as a student writes them in the notebook."""
import math
import model as M
from model import sub, mag

def r(x, nd=1):
    return round(x + (1e-9 if x >= 0 else -1e-9), nd)
def n(x, nd=1):
    s = f"{r(x, nd):.{nd}f}".replace('.', ',')
    return s.replace('-', '−')

AC0 = r(M.AC0); AC0P = r(M.AC0p)
BC = r((AC0+AC0P)/2, 2); AB = r(AC0-BC, 2)
LAB = r(AB*M.MU, 4); LBC = r(BC*M.MU, 4); LCD = M.lCD; LEF = M.lEF; LED = M.lED
LBS2 = r(0.5*LBC, 4); BS2S = r(BC/2, 2)
W1 = r(M.W1, 2)
VB4 = r(W1*LAB, 4); VB = r(W1*LAB, 3)
PB_CHOSEN = 50; PIB_CHOSEN = 70          # chosen plan lengths (notebook: pb = 50 mm, πb = 70 mm)
assert r(VB/PB_CHOSEN, 5) == M.MUV
PB = r(VB/M.MUV)
AB_ACC = r(W1**2*LAB, 2)
assert r(AB_ACC/PIB_CHOSEN, 4) == M.MUA
PIB = r(AB_ACC/M.MUA)
CE_S = math.sqrt(M.CD**2+M.ED**2-2*M.CD*M.ED*math.cos(math.radians(M.ALPHA)))

def rot_sym(w, eps=1e-6):
    if abs(w) < eps: return '—'
    return '↺' if w > 0 else '↻'

def vchain(i):
    v = M.vplan(i); K = M.POS[i]['K']
    pc = r(mag(v['c'])); bc = r(mag(sub(v['c'], v['b']))); pe = r(pc/0.9)
    if pc == 0: bc = PB                       # dead position: c ≡ p, so bc = pb
    ef = r(mag(sub(v['f'], v['e']))); pf = r(mag(v['f'])); ps2 = r(mag(v['s2']))
    VC, VCB, VE, VFE, VF, VS2 = (r(x*M.MUV, 3) for x in (pc, bc, pe, ef, pf, ps2))   # as written: 3 decimals
    return dict(pb=PB, pc=pc, bc=bc, pe=pe, ef=ef, pf=pf, ps2=ps2, VC=VC, VCB=VCB, VE=VE, VFE=VFE, VF=VF, VS2=VS2,
                w2=r(VCB/LBC, 2), w3=r(VC/LCD, 2), w4=r(VFE/LEF, 2),
                w2s=rot_sym(K['w2']), w3s=rot_sym(K['w3']), w4s=rot_sym(K['w4']),
                VFs=('—' if abs(K['VF'][1]) < 1e-6 else ('↓' if K['VF'][1] < 0 else '↑')))

def achain(i):
    a = M.aplan(i); K = M.POS[i]['K']; vc = vchain(i)
    aCBn = r(vc['w2']**2*LBC, 2); aCDn = r(vc['w3']**2*LCD, 2); aFEn = r(vc['w4']**2*LEF, 2)   # a^n = ω²·l (notebook)
    bn2 = r(aCBn/M.MUA); pin3 = r(aCDn/M.MUA); en4 = r(aFEn/M.MUA)
    n2c = r(mag(sub(a['c'], a['n2']))); n3c = r(mag(sub(a['c'], a['n3']))); pic = r(mag(a['c']))
    pie = r(pic/0.9); n4f = r(mag(sub(a['f'], a['n4']))); pif = r(mag(a['f'])); pis2 = r(mag(a['s2']))
    aCBt, aCDt, aC, aE, aFEt, aF, aS2 = (r(x*M.MUA, 2) for x in (n2c, n3c, pic, pie, n4f, pif, pis2))
    return dict(pib=PIB, aCBn=aCBn, aCDn=aCDn, aFEn=aFEn, bn2=bn2, pin3=pin3, en4=en4, n2c=n2c, n3c=n3c, pic=pic,
                pie=pie, n4f=n4f, pif=pif, pis2=pis2, aCBt=aCBt, aCDt=aCDt, aC=aC, aE=aE, aFEt=aFEt, aF=aF, aS2=aS2,
                e2=r(aCBt/LBC, 1), e3=r(aCDt/LCD, 1), e4=r(aFEt/LEF, 1),
                e2s=rot_sym(K['e2'], 1e-3), e3s=rot_sym(K['e3'], 1e-3), e4s=rot_sym(K['e4'], 1e-3),
                aFs=('↓' if K['aF'][1] < 0 else '↑'))

# ---------------- §4: reduced moment on the crank (power balance, teacher's projection method) ----------------
# M_P = G2·V_S2·cos α2/ω1 + G5·V_F·cos α5/ω1 − F_r·V_F/ω1, with V = segment·μ_V, so every term is (N·mm)·μ_V/ω1.
# ps2·cos α2 is not measured as an angle: project ps2 on the vertical of the velocity plan (down from p = +, up = −).
G2, G5 = M.DATA['G2'], M.DATA['G5']
KM = r(M.MUV/W1, 7)                       # μ_V/ω1, m/mm: turns N·mm of the plan into N·m
FRE_MAX_MM = r(M.FMAX/M.MUF)              # y_max of the F_re diagram, mm (μ_F = F_max / y_max)
def mchain(j):
    i = j % 8; v = M.vplan(i); c = vchain(i); q = M.POS[i]
    ys2 = r(-v['s2'][1])                                 # ps2·cos α2, mm, signed (down = +)
    pf = c['pf']; down = q['K']['VF'][1] < 0 or pf == 0
    work = 1 <= i <= 4                                   # slider goes down: working stroke
    yF = r(M.FMAX/M.MUF*M.fre_shape(q['sF']/M.H)) if work else 0.0   # F_re ordinate at this position, mm
    Fr = r(yF*M.MUF, 0)
    t2 = r(G2*ys2*KM, 2); t5 = r((1 if down else -1)*G5*pf*KM, 2); tr = r(Fr*pf*KM, 2)
    return dict(ys2=ys2, ps2=c['ps2'], pf=pf, a5=0 if down else 180, yF=yF, Fr=Fr, t2=t2, t5=t5, tr=tr, M=r(t2+t5-tr, 1))
MP = [mchain(j) for j in range(9)]
MP_MAX = max(abs(x['M']) for x in MP)
MP_YMAX = 80                                             # mm for |M_P|max (teacher: 70…80 mm)
MU_M = r(MP_MAX/MP_YMAX, 2)                              # (N·m)/mm
MU_PHI = r(2*3.14/160, 3)                                # rad/mm, one crank turn = 160 mm
for x in MP: x['Mmm'] = r(x['M']/MU_M, 1)

# ---------------- 1.8–1.9: work graphs and kinetic-energy increment (teacher's A4 sheet, graphical integration) ----------------
# A4 sheet: M_P(φ) on top, A(φ) 150 mm below it. Integration pole P at OP = 40 mm left of 0 on the φ axis of M_P.
# For each interval j-1…j: read the curve at the midpoint (ym, mm), ray from P to (0, ym) has slope ym/OP;
# the parallel through (j-1)' reaches the vertical of j at y'_j = y'_(j-1) + ym·20/OP (20 mm = one interval).
OP = 40                                                  # mm, polar distance (teacher: 40 mm)
A_GAP = 150                                              # mm between the φ axes of M_P(φ) and A(φ)
def _mid_ordinates():
    ys = [x['Mmm'] for x in MP]; ms = M._pchip_slopes([20*j for j in range(9)], ys)
    return [r((ys[k]+ys[k+1])/2 + 20*(ms[k]-ms[k+1])/8, 1) for k in range(8)]   # the drawn curve at the midpoint
YMID = _mid_ordinates()                                  # ym for intervals 0-1 … 7-8, mm (signed, up = +)
AR = [0.0]                                               # A_r ordinates 0', 1', … 8', mm (down = −)
for _k in range(8): AR.append(r(AR[-1] + YMID[_k]*20/OP, 1))
AM = [r(-AR[8]*j/8, 1) for j in range(9)]                # A_m: straight line from 0 to 8'' (8'' = −8', mirrored up)
DE = [r(AM[j] + AR[j], 1) for j in range(9)]             # ΔE = A_m + A_r, mm (A_r already negative)
YMM = r(-AR[8]*OP/160, 1)                                # M_m on the M_P axis: ray from P parallel to A_m, mm
MU_A = r(MU_M*MU_PHI*OP, 2)                              # J/mm (= μ_ΔE)
A_CYCLE = r(-AR[8]*MU_A, 0)                              # J, work of the resistance (= of the motor) per cycle
M_M = r(YMM*MU_M, 1)                                     # N·m, motor moment
DE_MAX = max(DE); DE_MIN = min(DE); J_MAX = DE.index(DE_MAX); J_MIN = DE.index(DE_MIN)
DE_RANGE = r((DE_MAX-DE_MIN)*MU_A, 1)                    # J, ΔE_max − ΔE_min (for the flywheel later)

# ---------------- 1.10: reduced moment of inertia I_P(φ) (teacher's lecture + methodology table 4) ----------------
# I_P·ω1²/2 = m2·V_S2²/2 + I_S2·ω2²/2 + m5·V_F²/2  →  I_P = m2·(V_S2/ω1)² + I_S2·(ω2/ω1)² + m5·(V_F/ω1)²
# V_S2, ω2, V_F: the notebook values of §2 (vchain). Teacher: m = G/g with g = 10 m/s², I_S2 from the table × 10⁻³.
G_ACC = 10
M2 = r(G2/G_ACC, 2); M5 = r(G5/G_ACC, 2)               # kg
IS2 = M.DATA['IS2']*1e-3                                 # kg·m²
def ichain(j):
    c = vchain(j % 8)
    a = r((c['VS2']/W1)**2, 5); b = r((c['w2']/W1)**2, 5); f = r((c['VF']/W1)**2, 5)
    t2 = r(M2*a, 5); tw = r(IS2*b, 5); t5 = r(M5*f, 5)
    return dict(VS2=c['VS2'], w2=c['w2'], VF=c['VF'], a=a, b=b, f=f, t2=t2, tw=tw, t5=t5, I=r(t2+tw+t5, 5))
IP = [ichain(j) for j in range(9)]
IP_MAX = max(x['I'] for x in IP); J_IMAX = [x['I'] for x in IP].index(IP_MAX)
IP_YMAX = 80                                             # mm for I_P max (teacher: 80 mm)
MU_I = r(IP_MAX/IP_YMAX, 7)                              # (kg·m²)/mm
for x in IP: x['Imm'] = r(x['I']/MU_I, 1)

if __name__ == '__main__':
    print('AC0', AC0, 'AC0p', AC0P, 'BC', BC, 'AB', AB, 'lAB', LAB, 'lBC', LBC, 'lBS2', LBS2, 'BS2*', BS2S)
    print('W1', W1, 'VB4', VB4, 'VB', VB, 'PB', PB, 'aB', AB_ACC, 'PIB', PIB, 'CE*', round(CE_S, 2))
    for i in range(8):
        c = vchain(i); print(i, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in c.items()})
    c = achain(2); print('acc2', {k: (round(v, 4) if isinstance(v, float) else v) for k, v in c.items()})
    print('YMID', YMID); print('AR', AR); print('AM', AM); print('DE', DE)
    print('YMM', YMM, 'MU_A', MU_A, 'A', A_CYCLE, 'M_M', M_M, 'DEmax', DE_MAX, J_MAX, 'DEmin', DE_MIN, J_MIN, 'range J', DE_RANGE)
    for j, x in enumerate(IP): print('I', j, x)
    print('M2', M2, 'M5', M5, 'IS2', IS2, 'IPmax', IP_MAX, J_IMAX, 'MU_I', MU_I)
