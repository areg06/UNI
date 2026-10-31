"""M_P(φ) graph (§4) as inline SVG, shared by build.py and explain.py. Style it with the .mpg classes."""
import model as M
import calc as C
from calc import n


def mp_graph():
    """M_P(φ) as drawn on paper: φ axis 8 × 20 mm, |M_P|max = 80 mm (1 svg unit = 1 mm)."""
    x0, y0 = 26, 22
    pts = [(x0 + 20*j, y0 - C.MP[j]['Mmm']) for j in range(9)]
    ms = M._pchip_slopes([p[0] for p in pts], [p[1] for p in pts])   # monotone: no overshoot between points
    d = f'M{pts[0][0]},{pts[0][1]:.2f}'
    for k in range(8):
        (xa, ya), (xb, yb), h = pts[k], pts[k+1], 20/3
        d += f' C{xa+h:.2f},{ya+ms[k]*h:.2f} {xb-h:.2f},{yb-ms[k+1]*h:.2f} {xb},{yb:.2f}'
    ymin = max(p[1] for p in pts); jmin = min(range(9), key=lambda j: C.MP[j]['Mmm'])
    out = [f'<svg class="mpg" viewBox="0 0 206 118" role="img" aria-label="Բերված մոմենտի գրաֆիկը">',
           f'<line class="ax" x1="{x0-6}" y1="{y0}" x2="{x0+170}" y2="{y0}"/><line class="ax" x1="{x0}" y1="{y0+86}" x2="{x0}" y2="6"/>',
           f'<path class="ar" d="M{x0+170},{y0} l-3,-1.2 v2.4z M{x0},6 l-1.2,3 h2.4z"/>',
           f'<text x="{x0+3}" y="8" class="lb">M<tspan class="sb" dy="1">P</tspan></text><text x="{x0+168}" y="{y0-3}" class="lb">φ</text>']
    for j, (x, y) in enumerate(pts):
        out.append(f'<line class="gr" x1="{x}" y1="{y0}" x2="{x}" y2="{y:.2f}"/>' if abs(y - y0) > 1 else '')
        out.append(f'<text x="{x}" y="{y0-2.5}" class="tk">{j}</text><circle class="dt" cx="{x}" cy="{y:.2f}" r="1.1"/>')
    out.append(f'<path class="cv" d="{d}"/>')
    xm = pts[jmin][0]
    out.append(f'<line class="dm" x1="{xm+6}" y1="{y0}" x2="{xm+6}" y2="{ymin:.2f}"/><text class="dmt" x="{xm+8}" y="{(y0+ymin)/2:.1f}">{n(-C.MP[jmin]["Mmm"],0)} մմ</text>')
    out.append(f'<line class="dm" x1="{x0}" y1="{y0+92}" x2="{x0+160}" y2="{y0+92}"/><text class="dmt c" x="{x0+80}" y="{y0+90}">8 × 20 մմ = 160 մմ</text>')
    out.append('</svg>')
    return ''.join(out)


# the teacher's method for ps₂·cos α₂: projection of ps₂ on the vertical through p (+ below p, − above)
PROJ_SVG = '''<svg class="projg" viewBox="0 0 200 92" role="img" aria-label="ps₂-ի պրոյեկցիան ուղղաձիգի վրա">
<g transform="translate(14,0)"><text x="0" y="10" class="cap">սուր անկյուն → «+»</text>
<line class="ax" x1="24" y1="18" x2="24" y2="88"/><circle class="dt" cx="24" cy="24" r="1.4"/><text x="16" y="27" class="lb">p</text>
<line class="vc" x1="24" y1="24" x2="58" y2="70"/><text x="60" y="73" class="lb">s₂</text>
<line class="pj" x1="58" y1="70" x2="24" y2="70"/><line class="hl" x1="24" y1="24" x2="24" y2="70"/>
<text x="27" y="50" class="hlt" transform="rotate(90 27 50)">ps₂·cos α₂</text>
<path class="g2" d="M70,24 v18"/><path class="ar2" d="M70,44 l-1.6,-4 h3.2z"/><text x="73" y="36" class="lb">G₂</text></g>
<g transform="translate(110,0)"><text x="0" y="10" class="cap">բութ անկյուն → «−»</text>
<line class="ax" x1="24" y1="18" x2="24" y2="88"/><circle class="dt" cx="24" cy="70" r="1.4"/><text x="16" y="73" class="lb">p</text>
<line class="vc" x1="24" y1="70" x2="60" y2="30"/><text x="62" y="30" class="lb">s₂</text>
<line class="pj" x1="60" y1="30" x2="24" y2="30"/><line class="hl" x1="24" y1="30" x2="24" y2="70"/>
<text x="27" y="40" class="hlt" transform="rotate(90 27 40)">−(ps₂·cos α₂)</text>
<path class="g2" d="M72,52 v18"/><path class="ar2" d="M72,72 l-1.6,-4 h3.2z"/><text x="75" y="64" class="lb">G₂</text></g>
</svg>'''
