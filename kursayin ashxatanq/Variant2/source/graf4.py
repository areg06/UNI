"""1.10: sheet 4 (A3, horizontal), same style as the other sheets (sheet.py): grid 380 × 270, origin O at the
bottom-left corner of the grid, x right, y up.
Right: I_P(φ) turned by 90° (methodology fig. 14): φ axis vertical (0 at the top, 20 mm per position, downwards),
I_P axis horizontal (to the right, I_P max = 80 mm). Left: ΔT(φ) (= ΔE of sheet 3, μ_ΔT = μ_A), on the level of the
free place under I_P(φ), where the energy–mass diagram ΔT(I_P) will be built in the next stage.
Used by build.py / explain.py (inline) and export.py (chertej_A3_3.svg/.png/.pdf)."""
import model as M
import calc as C
from calc import n
from sheet import SVG, draw_grid, fx, GH
from graf import A4_CSS, SUB

GW = M.GRID_W
VIEWBOX = '-14 -6 404 290'
XT0 = 30.0                   # ΔT(φ): ΔT axis (x of point 0)
YT = 75.0                    # ΔT(φ): φ axis
XI = 250.0                   # I_P(φ): φ axis (vertical)
YI0 = 255.0                  # I_P(φ): position 0 (I_P axis), position j at YI0 − 20·j
A3_4_CSS = A4_CSS


def _smooth_param(svg, ts, vs, to_xy, cls):
    """PCHIP curve through (t, v) points, drawn through the mapping to_xy(t, v) -> sheet (x, y)."""
    ms = M._pchip_slopes(ts, vs)
    P = lambda t, v: (lambda p: f'{fx(p[0])} {fx(GH - p[1])}')(to_xy(t, v))
    d = 'M' + P(ts[0], vs[0])
    for k in range(len(ts)-1):
        h = (ts[k+1]-ts[k])/3
        d += f' C{P(ts[k]+h, vs[k]+ms[k]*h)} {P(ts[k+1]-h, vs[k+1]-ms[k+1]*h)} {P(ts[k+1], vs[k+1])}'
    svg.add(f'<path d="{d}" class="{cls}"/>')


def a3_sheet4(prefix='sh4'):
    svg = SVG(prefix)
    svg.layer('grid'); draw_grid(svg)
    T = [20.0*j for j in range(9)]

    # ---------------- I_P(φ), turned by 90° ----------------
    svg.layer('ip')
    svg.text((XI+45, 266), 'Բերված իներցիայի մոմենտի գրաֆիկը', 'lbl ttl')
    svg.text((XI+45, 261.5), f'μ{SUB("I")} = {n(C.MU_I*1e4, 3)}·10⁻⁴ (կգ·մ²)/մմ,   μ</tspan>{SUB("φ")} = {n(C.MU_PHI, 3)} ռադ/մմ</tspan>', 'lbl sm')
    svg.line((XI-4, YI0), (XI+96, YI0), 'thick', marker='k')                 # I_P axis (to the right)
    svg.line((XI, YI0+4), (XI, YI0-170), 'thick', marker='k')                # φ axis (downwards)
    svg.text((XI+95, YI0+3.0), f'I{SUB("P")}</tspan>', 'lbl')
    svg.text((XI-3.2, YI0-169), 'φ', 'lbl')
    pts = [(XI + C.IP[j]['Imm'], YI0 - T[j]) for j in range(9)]
    for j, p in enumerate(pts):
        svg.line((XI-.8, p[1]), (XI+.8, p[1]), 'ln3')
        svg.text((XI-2.6, p[1]), str(j), 'lbl num', anchor='end')
        svg.line((XI, p[1]), p, 'ln3')                                        # ordinate (I_P)^գծ
    _smooth_param(svg, T, [C.IP[j]['Imm'] for j in range(9)], lambda t, v: (XI+v, YI0-t), 'curve')
    for j, p in enumerate(pts): svg.point(p, f'i{j}', f'I_P, դիրք {j}  ({n(C.IP[j]["Imm"])} մմ)')
    jm = C.J_IMAX
    svg.text((pts[jm][0]+2, pts[jm][1]+2.6), f'I{SUB("P")}(φ)</tspan>', 'lbl', anchor='start')
    svg.line((XI, YI0-T[8]-6), (XI+C.IP_YMAX, YI0-T[8]-6), 'dim')                     # 80 mm dimension
    for x in (XI, XI+C.IP_YMAX): svg.line((x, YI0-T[8]-4), (x, YI0-T[8]-8), 'dim')
    svg.text((XI+C.IP_YMAX/2, YI0-T[8]-8.4), f'I{SUB("P max")} = {n(C.IP_MAX, 5)} կգ·մ² → {C.IP_YMAX} մմ</tspan>', 'lbl xs')
    svg.line((XI-10, YI0), (XI-10, YI0-T[8]), 'dim')
    for y in (YI0, YI0-T[8]): svg.line((XI-8, y), (XI-12, y), 'dim')
    svg.text((XI-11.6, YI0-T[8]/2), '8 × 20 = 160 մմ', 'lbl xs', rotate=-90)

    # ---------------- ΔT(φ) ----------------
    svg.layer('dt')
    xs = [XT0 + T[j] for j in range(9)]
    svg.text((XT0+80, YT+40), 'Կինետիկ էներգիայի աճի գրաֆիկը', 'lbl ttl')
    svg.text((XT0+80, YT+35.5), f'ΔT = ΔE (թերթ 3),   μ{SUB("ΔT")} = μ</tspan>{SUB("A")} = {n(C.MU_A, 2)} Ջ/մմ</tspan>', 'lbl sm')
    svg.line((XT0-3, YT), (XT0+168, YT), 'thick', marker='k')
    svg.line((XT0, YT-34), (XT0, YT+26), 'thick', marker='k')
    svg.text((XT0+1.6, YT+25), 'ΔT', 'lbl', anchor='start')
    svg.text((XT0+167, YT-3.2), 'φ', 'lbl')
    pe = [(xs[j], YT + C.DE[j]) for j in range(9)]
    for j, p in enumerate(pe):
        if j and abs(p[1]-YT) > .8: svg.line((p[0], YT), p, 'ln3')
        svg.text((p[0]+(-1.6 if j in (0, 8) else 1.3), YT+(2.2 if C.DE[j] < 1 else -2.4)), str(j), 'lbl num')
    _smooth_param(svg, T, [C.DE[j] for j in range(9)], lambda t, v: (XT0+t, YT+v), 'curve')
    for j, p in enumerate(pe): svg.point(p, f't{j}', f'ΔT, դիրք {j}  ({n(C.DE[j])} մմ)')
    svg.text((xs[C.J_MIN]+3, pe[C.J_MIN][1]-3), 'ΔT(φ)', 'lbl', anchor='start')

    # ---------------- title block ----------------
    svg.layer('title')
    svg.add(f'<rect x="277" y="{GH-19}" width="100" height="16" class="tbox"/>')
    svg.add(f'<line x1="337" y1="{GH-19}" x2="337" y2="{GH-3}" class="tbl"/><line x1="277" y1="{GH-11}" x2="377" y2="{GH-11}" class="tbl"/>')
    svg.text((307, 14.8), 'Առաջադրանք N2. Դինամիկա', 'lbl xs')
    svg.text((307, 6.8), f'I{SUB("P")}(φ), ΔT(φ)</tspan>', 'lbl xs')
    svg.text((357, 14.8), f'Տարբերակ {M.VARIANT}', 'lbl sm'); svg.text((357, 6.8), 'Թերթ 4 (A3)', 'lbl sm')

    order = ['grid', 'dt', 'ip', 'title']
    body = ''.join(f'<g data-layer="{k}">' + ''.join(svg.layers.get(k, [])) + '</g>' for k in order)
    defs = (f'<defs><marker id="{prefix}-ar-k" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="2.6" markerHeight="2.6" '
            f'markerUnits="userSpaceOnUse" orient="auto"><path d="M0 1.2L10 5L0 8.8z" class="mk-k"/></marker></defs>')
    return (f'<svg class="sheet a3s4" id="{prefix}" viewBox="{VIEWBOX}" data-gw="{GW}" data-gh="{GH}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="Թերթ 4. բերված իներցիայի մոմենտի և կինետիկ էներգիայի աճի գրաֆիկները">'
            f'<rect x="-14" y="-6" width="404" height="290" class="paper"/>' + defs + body + '</svg>')


if __name__ == '__main__':
    import os
    import sheet as SH
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'graf4_preview.html')
    fonts = "@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400..600&family=Noto+Sans+Armenian:wdth,wght@62.5..100,400..700&family=STIX+Two+Text:ital,wght@0,400..700;1,400..700&display=swap');"
    open(out, 'w').write(f'<!doctype html><meta charset="utf-8"><style>{fonts}{SH.SHEET_CSS}{A3_4_CSS}body{{margin:0}}.sheet{{width:404mm}}</style>{a3_sheet4()}')
    print('wrote', out)
