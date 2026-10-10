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

if __name__ == '__main__':
    print('AC0', AC0, 'AC0p', AC0P, 'BC', BC, 'AB', AB, 'lAB', LAB, 'lBC', LBC, 'lBS2', LBS2, 'BS2*', BS2S)
    print('W1', W1, 'VB4', VB4, 'VB', VB, 'PB', PB, 'aB', AB_ACC, 'PIB', PIB, 'CE*', round(CE_S, 2))
    for i in range(8):
        c = vchain(i); print(i, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in c.items()})
    c = achain(2); print('acc2', {k: (round(v, 4) if isinstance(v, float) else v) for k, v in c.items()})
