"""1.8–1.9: the A4 graph sheet, drawn in the same style as the A3 sheets (sheet.py): millimetre grid
200 × 280 with numbered edges, origin O at the bottom-left corner of the grid, x right, y up, title block.
Top: M_P(φ) with the graphical integration (midpoints, rays to the pole P) and the motor moment M_m.
Bottom (150 mm lower): A_r(φ) built from the rays, the straight A_m(φ), and ΔE = A_m + A_r.
Used by build.py / explain.py (inline) and export.py (chertej_A4_graf.svg/.png/.pdf)."""
import model as M
import calc as C
from calc import n
import sheet as SH
from sheet import SVG, draw_grid, fx

GW, GH = 200, 280            # grid, mm
VIEWBOX = '-8 -9 210 297'    # = the A4 page (210 × 297 mm), grid placed 8 mm from the left and 9 mm from the top
X0 = 40.0                    # M and A axes (x of point 0)
XP = X0 - C.OP               # integration pole P
YM = 240.0                   # φ axis of M_P(φ): 40 mm below the top of the grid
YA = YM - C.A_GAP            # φ axis of A(φ)
ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']
XS = [X0 + 20*j for j in range(9)]
SUB = lambda s: f'<tspan class="sub" dy="0.6">{s}</tspan><tspan dy="-0.6">'   # subscript (close with </tspan>)

A4_CSS = """
.sheet .ln3{stroke:#3B4448;stroke-width:.22}
.sheet .grf{stroke:#1D2326;stroke-width:.55;fill:none}
.sheet .grfa{stroke:#1D2326;stroke-width:.45}
.sheet .mm{stroke:#1D2326;stroke-width:.3;stroke-dasharray:4 1 1 1}
.sheet .chd{stroke:#46505A;stroke-width:.2;stroke-dasharray:1.6 .8}
.sheet .dE{stroke:#1F54A3;stroke-width:.5;fill:none}
.sheet .dEo{stroke:#1F54A3;stroke-width:.2}
.sheet .dEj{fill:#1F54A3}
.sheet .lbl.de{fill:#1F54A3}
.sheet .lbl.rm{font-size:2.2px;font-style:italic;fill:#39434A}
"""


def _smooth_path(svg, pts, cls):
    """Monotone (PCHIP) cubic through the points (same curve as the §4 graph, no overshoot)."""
    ms = M._pchip_slopes([p[0] for p in pts], [p[1] for p in pts])
    y = lambda v: fx(GH - v)
    d = f'M{fx(pts[0][0])} {y(pts[0][1])}'
    for k in range(len(pts)-1):
        (xa, ya), (xb, yb) = pts[k], pts[k+1]; h = (xb-xa)/3
        d += f' C{fx(xa+h)} {y(ya+ms[k]*h)} {fx(xb-h)} {y(yb-ms[k+1]*h)} {fx(xb)} {y(yb)}'
    svg.add(f'<path d="{d}" class="{cls}"/>')


def _axes(svg, y0, ytop, ybot, lab):
    svg.line((XP-2 if y0 == YM else X0-3, y0), (GW+2.5, y0), 'grfa', marker='k')
    svg.line((X0, ybot), (X0, ytop), 'grfa', marker='k')
    svg.text((X0+1.6, ytop-1.2), lab, 'lbl big', anchor='start')
    svg.text((GW+1.2, y0-3.2), 'φ', 'lbl big')


def _cluster_labels(vals):
    """Group ray numbers whose end points on the M axis are closer than 2.4 mm: one label per group."""
    order = sorted(range(8), key=lambda k: -vals[k]); groups = []
    for k in order:
        if groups and abs(vals[groups[-1][-1]] - vals[k]) < 2.4: groups[-1].append(k)
        else: groups.append([k])
    return groups


def a4_sheet(prefix='sh3'):
    svg = SVG(prefix, gh=GH)
    svg.layer('grid'); draw_grid(svg, GW, GH)

    # ---------------- top: M_P(φ) ----------------
    svg.layer('mp')
    svg.text((120, 274), 'Բերված մոմենտի գրաֆիկը', 'lbl ttl')
    svg.text((120, 269), f'μ{SUB("M")} = {n(C.MU_M, 2)} Ն·մ/մմ,   μ</tspan>{SUB("φ")} = {n(C.MU_PHI, 3)} ռադ/մմ</tspan>', 'lbl sm')
    _axes(svg, YM, 262, YM-86, f'M{SUB("P")}, Ն·մ</tspan>')
    for j, x in enumerate(XS):
        svg.line((x, YM-.8), (x, YM+.8), 'ln3')
        up = C.MP[j]['Mmm'] < 1.5
        svg.text((x+(-1.4 if j == 8 else 1.3), YM+(2.2 if up else -2.4)), str(j), 'lbl num')
    pm = [(XS[j], YM + C.MP[j]['Mmm']) for j in range(9)]
    for j, p in enumerate(pm):
        if abs(p[1]-YM) > .8: svg.line((p[0], YM), p, 'ln3')
    _smooth_path(svg, pm, 'grf')
    for j, p in enumerate(pm): svg.point(p, f'm{j}', f'Mₚ, դիրք {j}  (y = {n(C.MP[j]["Mmm"])} մմ)')
    svg.text((XS[2]+2.5, pm[2][1]-1.5), f'M{SUB("P")}(φ)</tspan>', 'lbl big', anchor='start')

    svg.layer('integ')                                              # pole, midpoints, rays I…VIII
    svg.point((XP, YM), 'P', 'P՝ ինտեգրման բևեռ', r=.7)
    svg.text((XP+1.4, YM+2.4), 'P', 'lbl big')
    svg.text(((XP+X0)/2, YM+2.2), f'OP = {C.OP} մմ', 'lbl xs')
    for k in range(8):
        xm = X0 + 20*k + 10; ym = YM + C.YMID[k]
        svg.line((xm, YM), (xm, ym), 'proj'); svg.line((xm, ym), (X0, ym), 'proj')
        svg.line((XP, YM), (X0, ym), 'ln3')
        svg.point((xm, ym), f'k{k+1}', f'{k}–{k+1} միջնակետը կորի վրա  (y = {n(C.YMID[k])} մմ)', r=.45)
        svg.point((X0, ym), f'q{k+1}', f'{ROMAN[k]} ճառագայթի ծայրը M առանցքի վրա', r=.45)
    for g in _cluster_labels(C.YMID):
        y = sum(YM + C.YMID[k] for k in g)/len(g)
        svg.text((X0-1.2, y-(2.6 if len(g) > 1 else 0)), ', '.join(ROMAN[k] for k in sorted(g)), 'lbl rm', anchor='end')

    svg.layer('mm')                                                 # M_m from the ray parallel to A_m
    ymm = YM + C.YMM
    svg.line((XP, YM), (X0, ymm), 'mm'); svg.line((X0, ymm), (XS[8], ymm), 'mm')
    svg.point((X0, ymm), 'Mm', f'Mₘ  (y = {n(C.YMM)} մմ)', r=.55)
    svg.text((XS[8]-1, ymm+2.2), f'M{SUB("m")} = {n(C.M_M)} Ն·մ</tspan>', 'lbl sm', anchor='end')

    # ---------------- bottom: A(φ), ΔE(φ) ----------------
    svg.layer('a')
    svg.text((120, 147.5), 'Աշխատանքների և կինետիկ էներգիայի աճի գրաֆիկները', 'lbl ttl')
    svg.text((120, 142.5), f'μ{SUB("A")} = μ</tspan>{SUB("ΔE")} = μ</tspan>{SUB("M")}·μ</tspan>{SUB("φ")}·OP = {n(C.MU_A, 2)} Ջ/մմ</tspan>', 'lbl sm')
    _axes(svg, YA, YA+70, YA-66, f'A, ΔE, Ջ')
    pr = [(XS[j], YA + C.AR[j]) for j in range(9)]
    pa = [(XS[j], YA + C.AM[j]) for j in range(9)]
    pe = [(XS[j], YA + C.DE[j]) for j in range(9)]
    for j in range(9):
        lo = min(pr[j][1], pe[j][1], YA); hi = max(pa[j][1], pe[j][1], YA)
        if j: svg.line((XS[j], lo), (XS[j], hi), 'ln3')
        svg.text((XS[j]+(-1.6 if j in (0, 8) else 1.3), YA+(-2.4 if j == 0 else 2.2)), str(j), 'lbl num')
    for k in range(8):                                              # chords parallel to the rays
        svg.line(pr[k], pr[k+1], 'chd')
        if abs(C.AR[k+1]-C.AR[k]) > 4:
            mx, my = (pr[k][0]+pr[k+1][0])/2, (pr[k][1]+pr[k+1][1])/2
            svg.text((mx+2.2, my+.8), ROMAN[k+0], 'lbl rm', anchor='start')
    _smooth_path(svg, pr, 'grf')
    for j in range(1, 9):
        svg.point(pr[j], f'r{j}', f'{j}′  (Aᵣ, y = {n(C.AR[j])} մմ)')
        left = j in (1, 8)
        svg.text((pr[j][0]+(-1.4 if left else 1.2), pr[j][1]-2.4), f'{j}′', 'lbl sm', anchor='end' if left else 'start')
    svg.text((XS[5], pr[5][1]-6.5), f'A{SUB("r")}(φ)</tspan>', 'lbl big')
    svg.line(pa[0], pa[8], 'curve')                                 # A_m: straight line 0 → 8″
    svg.line((XS[8]+3, pr[8][1]), (XS[8]+3, pa[8][1]), 'proj')      # 8′ mirrored up → 8″
    svg.point(pa[8], 'a8', f'8″  (Aₘ, y = {n(C.AM[8])} մմ)')
    svg.text((XS[8]-1.4, pa[8][1]+2.4), '8″', 'lbl sm', anchor='end')
    svg.text((XS[6]-2, pa[6][1]+4.0), f'A{SUB("m")}(φ)</tspan>', 'lbl big', anchor='end')

    svg.layer('de')
    _smooth_path(svg, pe, 'dE')
    for j in range(9): svg.point(pe[j], f'e{j}', f'ΔE, դիրք {j}  (y = {n(C.DE[j])} մմ)', r=.5, cls='dEj')
    jm = C.J_MIN
    svg.text((XS[jm]+3, pe[jm][1]-3.4), 'ΔE(φ)', 'lbl big de', anchor='start')

    # ---------------- title block (as on the A3 sheets) ----------------
    svg.layer('title')
    x0 = GW - 100
    svg.add(f'<rect x="{x0}" y="{GH-19}" width="100" height="16" class="tbox"/>')
    svg.add(f'<line x1="{x0+60}" y1="{GH-19}" x2="{x0+60}" y2="{GH-3}" class="tbl"/><line x1="{x0}" y1="{GH-11}" x2="{GW}" y2="{GH-11}" class="tbl"/>')
    svg.text((x0+30, 14.8), 'Առաջադրանք N2. Դինամիկա', 'lbl xs')
    svg.text((x0+30, 6.8), f'M{SUB("P")}(φ), A(φ), ΔE(φ) գրաֆիկներ</tspan>', 'lbl xs')
    svg.text((x0+80, 14.8), f'Տարբերակ {M.VARIANT}', 'lbl sm'); svg.text((x0+80, 6.8), 'Թերթ 3 (A4)', 'lbl sm')

    order = ['grid', 'integ', 'mm', 'mp', 'a', 'de', 'title']
    body = ''.join(f'<g data-layer="{k}">' + ''.join(svg.layers.get(k, [])) + '</g>' for k in order)
    defs = (f'<defs><marker id="{prefix}-ar-k" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="2.6" markerHeight="2.6" '
            f'markerUnits="userSpaceOnUse" orient="auto"><path d="M0 1.2L10 5L0 8.8z" class="mk-k"/></marker></defs>')
    return (f'<svg class="sheet a4" id="{prefix}" viewBox="{VIEWBOX}" data-gw="{GW}" data-gh="{GH}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="A4 թերթ. բերված մոմենտի, աշխատանքների և կինետիկ էներգիայի աճի գրաֆիկները">'
            f'<rect x="-8" y="-9" width="210" height="297" class="paper"/>' + defs + body + '</svg>')


if __name__ == '__main__':
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'graf_preview.html')
    open(out, 'w').write(f'<!doctype html><meta charset="utf-8"><style>{SH.SHEET_CSS}{A4_CSS}body{{margin:0}}.sheet{{width:210mm}}</style>{a4_sheet()}')
    print('wrote', out)
