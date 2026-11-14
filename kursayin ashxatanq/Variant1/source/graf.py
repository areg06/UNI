"""1.8–1.9: the A4 graph sheet (millimetre paper) as the teacher draws it, 1 svg unit = 1 mm.
Top: M_P(φ) with the graphical integration (midpoints, rays to the pole P) and the motor moment M_m.
Bottom (150 mm lower): A_r(φ) built from the rays, the straight A_m(φ), and ΔE = A_m + A_r.
Used by build.py / explain.py (inline, class "a4g") and export.py (chertej_A4_graf.svg/.png/.pdf)."""
import model as M
import calc as C
from calc import n

W, H = 210, 297
X0 = 44                      # M and A axes (x of point 0)
XP = X0 - C.OP               # integration pole P
YM = 40                      # φ axis of M_P(φ), 40 mm below the top edge
YA = YM + C.A_GAP            # φ axis of A(φ)
ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']

A4_CSS = """
.a4g{width:100%;height:auto;display:block;background:#FFFDF8;font-family:'STIX Two Text','Times New Roman',serif}
.a4g .g1{stroke:#F6DCCD;stroke-width:.1}.a4g .g5{stroke:#EBA987;stroke-width:.22}.a4g .g10{stroke:#E0865C;stroke-width:.36}
.a4g .ax{stroke:#1B1F22;stroke-width:.45;fill:none}.a4g .ar{fill:#1B1F22}
.a4g .cv{stroke:#1D3E8A;stroke-width:.7;fill:none}.a4g .dt{fill:#1D3E8A}
.a4g .cs{stroke:#5B6670;stroke-width:.22;fill:none;stroke-dasharray:1.2 .8}
.a4g .ry{stroke:#5B6670;stroke-width:.25;fill:none}
.a4g .ch{stroke:#1D3E8A;stroke-width:.25;fill:none;stroke-dasharray:2 .8}
.a4g .am{stroke:#B3261E;stroke-width:.6;fill:none}.a4g .amd{stroke:#B3261E;stroke-width:.3;fill:none;stroke-dasharray:2 1}
.a4g .de{stroke:#1E7A55;stroke-width:.7;fill:none;stroke-dasharray:3 1.2}.a4g .ded{fill:#1E7A55}
.a4g .vt{stroke:#1B1F22;stroke-width:.18}
.a4g text{fill:#1B1F22;font-size:3.6px}.a4g .tk{font-size:3px;text-anchor:middle}.a4g .sm{font-size:2.6px}
.a4g .rm{font-size:2.4px;fill:#5B6670;font-style:italic}.a4g .lb{font-size:4.2px;font-style:italic}
.a4g .lr{fill:#B3261E}.a4g .lg{fill:#1E7A55}.a4g .lbl{fill:#1D3E8A}
.a4g .ttl{font-size:4.4px;font-weight:600}.a4g .nt{font-size:3.1px}
"""


def _smooth(pts):
    """Monotone (PCHIP) cubic through the points: the same curve as the §4 graph, no overshoot."""
    ms = M._pchip_slopes([p[0] for p in pts], [p[1] for p in pts])
    d = f'M{pts[0][0]},{pts[0][1]:.2f}'
    for k in range(len(pts)-1):
        (xa, ya), (xb, yb) = pts[k], pts[k+1]; h = (xb-xa)/3
        d += f' C{xa+h:.2f},{ya+ms[k]*h:.2f} {xb-h:.2f},{yb-ms[k+1]*h:.2f} {xb},{yb:.2f}'
    return d


def _grid():
    out = []
    for k in range(1, W):
        c = 'g10' if k % 10 == 0 else 'g5' if k % 5 == 0 else 'g1'
        out.append(f'<line class="{c}" x1="{k}" y1="0" x2="{k}" y2="{H}"/>')
    for k in range(1, H):
        c = 'g10' if k % 10 == 0 else 'g5' if k % 5 == 0 else 'g1'
        out.append(f'<line class="{c}" x1="0" y1="{k}" x2="{W}" y2="{k}"/>')
    return ''.join(out)


def a4_sheet(grid=True):
    xs = [X0 + 20*j for j in range(9)]
    o = [f'<svg class="a4g" viewBox="0 0 {W} {H}" role="img" aria-label="Բերված մոմենտի, աշխատանքների և կինետիկ էներգիայի աճի գրաֆիկները A4 թերթի վրա">']
    if grid: o.append(_grid())
    # ---- top: M_P(φ) ----
    o.append(f'<line class="ax" x1="{XP-2}" y1="{YM}" x2="{X0+166}" y2="{YM}"/><line class="ax" x1="{X0}" y1="{YM+88}" x2="{X0}" y2="{YM-30}"/>')
    o.append(f'<path class="ar" d="M{X0+166},{YM} l-3,-1 v2z M{X0},{YM-30} l-1,3 h2z"/>')
    o.append(f'<text class="lb" x="{X0+2}" y="{YM-27}">M<tspan class="sm" dy="1">P</tspan></text><text class="lb" x="{X0+163}" y="{YM-2.5}">φ</text>')
    o.append(f'<circle class="dt" cx="{XP}" cy="{YM}" r=".7"/><text class="lb" x="{XP-.5}" y="{YM-2}">P</text>')
    o.append(f'<line class="vt" x1="{XP}" y1="{YM+5}" x2="{X0}" y2="{YM+5}"/><text class="sm" x="{(XP+X0)/2}" y="{YM+4}" text-anchor="middle">OP = {C.OP} մմ</text>')
    pm = [(xs[j], YM - C.MP[j]['Mmm']) for j in range(9)]
    for j, (x, y) in enumerate(pm):
        o.append(f'<text class="tk" x="{x+1.6 if j else x-2}" y="{YM-1.2 if C.MP[j]["Mmm"] < 1 else YM+3.6}">{j}</text>')
        if abs(y - YM) > .6: o.append(f'<line class="vt" x1="{x}" y1="{YM}" x2="{x}" y2="{y:.2f}"/>')
        o.append(f'<circle class="dt" cx="{x}" cy="{y:.2f}" r=".6"/>')
    o.append(f'<path class="cv" d="{_smooth(pm)}"/>')
    o.append(f'<text class="lb lbl" x="{xs[2]+3}" y="{pm[2][1]+2:.1f}">M<tspan class="sm" dy="1">P</tspan><tspan dy="-1">(φ)</tspan></text>')
    for k in range(8):                              # midpoint → curve → M axis → ray to P
        xm = X0 + 20*k + 10; ym = YM - C.YMID[k]
        o.append(f'<line class="cs" x1="{xm}" y1="{YM}" x2="{xm}" y2="{ym:.2f}"/><line class="cs" x1="{xm}" y1="{ym:.2f}" x2="{X0}" y2="{ym:.2f}"/>')
        o.append(f'<line class="ry" x1="{XP}" y1="{YM}" x2="{X0}" y2="{ym:.2f}"/>')
    lab = sorted(range(8), key=lambda k: C.YMID[k])
    used = []
    for k in lab:                                   # Roman numerals at the M axis, spread so they do not overlap
        y = YM - C.YMID[k]
        while any(abs(y - u) < 2.6 for u in used): y += 2.6 if C.YMID[k] <= 0 else -2.6
        used.append(y)
        o.append(f'<text class="rm" x="{X0-1.2}" y="{y+.9:.1f}" text-anchor="end">{ROMAN[k]}</text>')
    ymm = YM - C.YMM                                # M_m: ray from P parallel to A_m, then horizontal
    o.append(f'<line class="amd" x1="{XP}" y1="{YM}" x2="{X0}" y2="{ymm:.2f}"/><line class="am" x1="{X0}" y1="{ymm:.2f}" x2="{xs[8]}" y2="{ymm:.2f}"/>')
    o.append(f'<text class="lb lr" x="{xs[7]+4}" y="{ymm-1.6:.1f}">M<tspan class="sm" dy="1">m</tspan></text>')
    # ---- bottom: A(φ) ----
    o.append(f'<line class="ax" x1="{X0-4}" y1="{YA}" x2="{X0+166}" y2="{YA}"/><line class="ax" x1="{X0}" y1="{YA+70}" x2="{X0}" y2="{YA-70}"/>')
    o.append(f'<path class="ar" d="M{X0+166},{YA} l-3,-1 v2z M{X0},{YA-70} l-1,3 h2z"/>')
    o.append(f'<text class="lb" x="{X0+2}" y="{YA-67}">A, ΔE</text><text class="lb" x="{X0+163}" y="{YA-2.5}">φ</text>')
    pr = [(xs[j], YA - C.AR[j]) for j in range(9)]
    pa = [(xs[j], YA - C.AM[j]) for j in range(9)]
    pe = [(xs[j], YA - C.DE[j]) for j in range(9)]
    for j in range(9):
        lo = max(pr[j][1], pe[j][1], YA); hi = min(pa[j][1], pe[j][1], YA)
        o.append(f'<line class="vt" x1="{xs[j]}" y1="{hi:.2f}" x2="{xs[j]}" y2="{lo:.2f}"/>')
        o.append(f'<text class="tk" x="{xs[j]-1.6 if j else xs[j]-2}" y="{YA+3.6 if j < 3 else YA-1.2}">{j}</text>')
    for k in range(8):                              # chord k: parallel to ray k, from (k)' to (k+1)'
        o.append(f'<line class="ch" x1="{pr[k][0]}" y1="{pr[k][1]:.2f}" x2="{pr[k+1][0]}" y2="{pr[k+1][1]:.2f}"/>')
        mx, my = (pr[k][0]+pr[k+1][0])/2, (pr[k][1]+pr[k+1][1])/2
        if abs(C.AR[k+1]-C.AR[k]) > 3: o.append(f'<text class="rm" x="{mx+1.2}" y="{my:.1f}">{ROMAN[k]}</text>')
    o.append(f'<path class="cv" d="{_smooth(pr)}"/>')
    for j in range(1, 9):
        o.append(f'<circle class="dt" cx="{pr[j][0]}" cy="{pr[j][1]:.2f}" r=".6"/>')
        o.append(f'<text class="sm lbl" x="{pr[j][0]+.8}" y="{pr[j][1]+3.2:.1f}">{j}′</text>')
    o.append(f'<line class="am" x1="{pa[0][0]}" y1="{YA}" x2="{pa[8][0]}" y2="{pa[8][1]:.2f}"/>')
    o.append(f'<circle class="dt" cx="{pa[8][0]}" cy="{pa[8][1]:.2f}" r=".6" style="fill:#B3261E"/><text class="sm lr" x="{pa[8][0]+1}" y="{pa[8][1]-1:.1f}">8″</text>')
    o.append(f'<line class="amd" x1="{xs[8]+3}" y1="{YA}" x2="{xs[8]+3}" y2="{pa[8][1]:.2f}"/><line class="amd" x1="{xs[8]+3}" y1="{YA}" x2="{xs[8]+3}" y2="{pr[8][1]:.2f}"/>')
    o.append(f'<text class="lb lr" x="{xs[6]-4}" y="{pa[6][1]-2:.1f}">A<tspan class="sm" dy="1">m</tspan><tspan dy="-1">(φ)</tspan></text>')
    o.append(f'<text class="lb lbl" x="{xs[5]}" y="{pr[5][1]+7:.1f}">A<tspan class="sm" dy="1">r</tspan><tspan dy="-1">(φ)</tspan></text>')
    o.append(f'<path class="de" d="{_smooth(pe)}"/>')
    for j in range(9): o.append(f'<circle class="ded" cx="{pe[j][0]}" cy="{pe[j][1]:.2f}" r=".55"/>')
    jm = C.J_MIN
    o.append(f'<text class="lb lg" x="{xs[jm]+2}" y="{pe[jm][1]+5:.1f}">ΔE(φ)</text>')
    # ---- scales ----
    yt = YA + 76
    o.append(f'<text class="nt" x="{XP}" y="{yt}">μ<tspan class="sm" dy=".8">M</tspan><tspan dy="-.8"> = {n(C.MU_M,2)} Ն·մ/մմ,   μ</tspan><tspan class="sm" dy=".8">φ</tspan><tspan dy="-.8"> = {n(C.MU_PHI,3)} ռադ/մմ,   OP = {C.OP} մմ</tspan></text>')
    o.append(f'<text class="nt" x="{XP}" y="{yt+5}">μ<tspan class="sm" dy=".8">A</tspan><tspan dy="-.8"> = μ</tspan><tspan class="sm" dy=".8">ΔE</tspan><tspan dy="-.8"> = μ</tspan><tspan class="sm" dy=".8">M</tspan><tspan dy="-.8">·μ</tspan><tspan class="sm" dy=".8">φ</tspan><tspan dy="-.8">·OP = {n(C.MU_A,2)} Ջ/մմ,   M</tspan><tspan class="sm" dy=".8">m</tspan><tspan dy="-.8"> = {n(C.YMM)}·{n(C.MU_M,2)} = {n(C.M_M)} Ն·մ</tspan></text>')
    o.append('</svg>')
    return ''.join(o)


if __name__ == '__main__':
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'graf_preview.html')
    open(out, 'w').write(f'<!doctype html><meta charset="utf-8"><style>{A4_CSS}body{{margin:0}}.a4g{{width:210mm}}</style>{a4_sheet()}')
    print('wrote', out)
