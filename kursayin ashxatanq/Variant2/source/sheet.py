"""SVG of the A3 sheet (sheet mm, origin at bottom-left of the grid)."""
import math
import model as M
from model import S, sub, add, scl, mag, ang

GH = M.GRID_H
def fx(v): return f"{v:.2f}".rstrip('0').rstrip('.')
def X(p): return fx(p[0])
def Y(p): return fx(GH-p[1])
def num(v, nd=1):
    s = f"{v:.{nd}f}".replace('.', ',')
    return s.replace('-', '−')

class SVG:
    def __init__(self, prefix):
        self.p = prefix; self.layers = {}; self.cur = None
    def layer(self, name): self.cur = self.layers.setdefault(name, [])
    def add(self, s): self.cur.append(s)
    def line(self, a, b, cls, marker=None, extra=''):
        m = f' marker-end="url(#{self.p}-ar-{marker})"' if marker else ''
        self.add(f'<line x1="{X(a)}" y1="{Y(a)}" x2="{X(b)}" y2="{Y(b)}" class="{cls}"{m}{extra}/>')
    def poly(self, pts, cls, closed=False):
        d = 'M' + ' L'.join(f'{X(p)} {Y(p)}' for p in pts) + (' Z' if closed else '')
        self.add(f'<path d="{d}" class="{cls}"/>')
    def arc(self, c, r, a0, a1, cls, n=48):
        pts = [(c[0]+r*math.cos(math.radians(a0+(a1-a0)*k/n)), c[1]+r*math.sin(math.radians(a0+(a1-a0)*k/n))) for k in range(n+1)]
        self.poly(pts, cls)
    def circle(self, c, r, cls):
        self.add(f'<circle cx="{X(c)}" cy="{Y(c)}" r="{fx(r)}" class="{cls}"/>')
    def text(self, p, s, cls='lbl', anchor='middle', rotate=None, size=None):
        tr = f' transform="rotate({rotate} {X(p)} {Y(p)})"' if rotate is not None else ''
        fs = f' font-size="{size}"' if size else ''
        self.add(f'<text x="{X(p)}" y="{Y(p)}" class="{cls}" text-anchor="{anchor}" dominant-baseline="central"{fs}{tr}>{s}</text>')
    def point(self, p, key, label, r=0.55, cls='jt'):
        self.add(f'<circle id="{self.p}-pt-{key}" cx="{X(p)}" cy="{Y(p)}" r="{r}" class="pt {cls}" '
                 f'data-k="{label}" data-x="{num(p[0])}" data-y="{num(p[1])}"/>')

def unit(v):
    m = mag(v); return (v[0]/m, v[1]/m) if m > 1e-9 else (0.0, 0.0)
def polar(c, r, a): return (c[0]+r*math.cos(math.radians(a)), c[1]+r*math.sin(math.radians(a)))
def auto_off(q, nbrs, dist=3.0, default=(-0.7, 0.7)):
    sx = sy = 0.0
    for n in nbrs:
        u = unit(sub(n, q)); sx += u[0]; sy += u[1]
    u = unit((-sx, -sy))
    if u == (0.0, 0.0): u = unit(default)
    return (q[0]+u[0]*dist, q[1]+u[1]*dist)

def hatch(svg, a, b, side, n_len=2.2, step=1.6):
    """short hatch strokes along segment a-b, on the given side (unit normal)."""
    L = mag(sub(b, a)); u = unit(sub(b, a)); k = 0.0
    while k <= L:
        s = add(a, scl(u, k)); e = add(s, add(scl(side, n_len), scl(u, -n_len*0.7)))
        svg.line(s, e, 'hatch'); k += step

def ground(svg, c, up=True):
    sgn = 1 if up else -1
    base_l = (c[0]-5.5, c[1]+sgn*6.0); base_r = (c[0]+5.5, c[1]+sgn*6.0)
    svg.poly([c, (c[0]-3.2, c[1]+sgn*6.0), (c[0]+3.2, c[1]+sgn*6.0)], 'sup', closed=True)
    svg.line(base_l, base_r, 'thick')
    hatch(svg, base_l, base_r, (0.0, float(sgn)))

def draw_grid(svg):
    for step, cls in ((1, 'g1'), (5, 'g5'), (10, 'g10'), (50, 'g50')):
        d = []
        for x in range(0, M.GRID_W+1, step):
            if step < 50 and x % (step*5 if step < 10 else 50) == 0 and step != 10: continue
            if step == 10 and x % 50 == 0: continue
            d.append(f'M{x} 0V{GH}')
        for y in range(0, GH+1, step):
            if step < 50 and y % (step*5 if step < 10 else 50) == 0 and step != 10: continue
            if step == 10 and y % 50 == 0: continue
            d.append(f'M0 {GH-y}H{M.GRID_W}')
        svg.add(f'<path d="{"".join(d)}" class="{cls}"/>')
    for x in range(0, M.GRID_W+1, 10):
        svg.add(f'<text x="{x}" y="{GH+3.6}" class="ax{" ax5" if x % 50 == 0 else ""}" text-anchor="middle">{x}</text>')
    for y in range(0, GH+1, 10):
        svg.add(f'<text x="-2.2" y="{GH-y}" class="ax{" ax5" if y % 50 == 0 else ""}" text-anchor="end" dominant-baseline="central">{y}</text>')
    svg.add(f'<text x="-9.5" y="{GH+3.6}" class="ax ax5" text-anchor="middle">O</text>')

def draw_vplans(svg, poles, caps={}):
    dir_lbl = dict(pb='⊥AB', bc='⊥BC', pc='⊥CD', pe='⊥DE', ef='⊥EF', pf='∥ուղղ.')
    for i, pole in poles.items():
        v = M.vplan(i); pt = {k: add(pole, vv) for k, vv in v.items()}
        svg.add(f'<g class="plan vp" data-plan="v{i}">')
        if i == 0:
            svg.line(pt['p'], pt['b'], 'vec', marker='v')
            svg.point(pt['b'], f'v{i}b', f'b (պլան {i})'); svg.point(pt['s2'], f'v{i}s2', f's₂ (պլան {i})')
            svg.point(pt['p'], f'v{i}p', f'p (պլան {i})', r=0.7)
            svg.text(add(pt['b'], (2.6, 1.2)), 'b', 'lbl vl', anchor='start')
            svg.text(add(pt['s2'], (2.4, 0)), 's₂', 'lbl vl', anchor='start')
            svg.text(add(pt['p'], (0, -3.2)), 'p (a, c, d, e, f)', 'lbl vl sm')
            mid = scl(add(pt['p'], pt['b']), 0.5); svg.text(add(mid, (-3.4, 8)), '⊥AB', 'lbl dir', rotate=None)
            svg.text(caps.get(i, add(pt['p'], (0, -9.5))), f'Դիրք {i}', 'lbl vl cap')
            svg.add('</g>'); continue
        svg.line(pt['b'], pt['c'], 'vecr', marker='v')
        svg.line(pt['c'], pt['e'], 'vtri')
        svg.line(pt['e'], pt['f'], 'vecr', marker='v')
        for k in ('b', 'c', 'e', 'f'):
            svg.line(pt['p'], pt[k], 'vec', marker='v')
        svg.line(pt['p'], pt['s2'], 'vecs', marker='v')
        nb = dict(p=[pt['b'], pt['c'], pt['e'], pt['f']], b=[pt['p'], pt['c']], c=[pt['p'], pt['b'], pt['e']],
                  e=[pt['p'], pt['c'], pt['f']], f=[pt['p'], pt['e']], s2=[pt['p'], pt['b'], pt['c']])
        names = dict(p='p (a, d)', b='b', c='c', e='e', f='f', s2='s₂')
        for k in ('b', 'c', 'e', 'f', 's2', 'p'):
            svg.point(pt[k], f'v{i}{k}', f'{names[k]} (պլան {i})', r=0.7 if k == 'p' else 0.55)
            o = add(pt[k], M.VLBL[(i, k)]) if (i, k) in M.VLBL else auto_off(pt[k], nb[k], dist=3.4 if k != 'p' else 4.4)
            svg.text(o, names[k], 'lbl vl')
        cen = scl((sum(p[0] for p in pt.values()), sum(p[1] for p in pt.values())), 1/len(pt))
        placed = []
        for seg, (a, b) in dict(pb=('p', 'b'), bc=('b', 'c'), pc=('p', 'c'), pe=('p', 'e'), ef=('e', 'f'), pf=('p', 'f')).items():
            A_, B_ = pt[a], pt[b]
            if mag(sub(B_, A_)) < 12: continue                      # too short to carry a label
            u = unit(sub(B_, A_)); nrm = (-u[1], u[0])
            mid = add(A_, scl(sub(B_, A_), 0.38 if seg in ('bc', 'pb') else 0.5))
            side = 1 if (nrm[0]*(mid[0]-cen[0])+nrm[1]*(mid[1]-cen[1])) >= 0 else -1
            if any(mag(sub(add(mid, scl(nrm, 1.9*side)), q)) < 3.5 for q in placed): side = -side
            placed.append(add(mid, scl(nrm, 1.9*side)))
            rot_ = -math.degrees(math.atan2(u[1], u[0]))
            if rot_ > 90: rot_ -= 180
            if rot_ < -90: rot_ += 180
            svg.text(add(mid, scl(nrm, 1.9*side)), dir_lbl[seg], 'lbl dir', rotate=fx(rot_))
        bb = [min(p[1] for p in pt.values()), min(p[0] for p in pt.values()), max(p[0] for p in pt.values())]
        svg.text(caps.get(i, ((bb[1]+bb[2])/2, bb[0]-6.0)), f'Դիրք {i}', 'lbl vl cap')
        svg.add('</g>')

def draw_title(svg, sheet_no, what):
    svg.add(f'<rect x="277" y="{GH-19}" width="100" height="16" class="tbox"/>')
    svg.add(f'<line x1="337" y1="{GH-19}" x2="337" y2="{GH-3}" class="tbl"/><line x1="277" y1="{GH-11}" x2="377" y2="{GH-11}" class="tbl"/>')
    svg.text((307, 14.8), 'Առաջադրանք N2. Կինեմատիկա', 'lbl xs'); svg.text((307, 6.8), what, 'lbl xs')
    svg.text((357, 14.8), f'Տարբերակ {M.VARIANT}', 'lbl sm'); svg.text((357, 6.8), f'Թերթ {sheet_no} / 2', 'lbl sm')

def build(prefix='sh', only=None, exclude=('synonly',), viewbox='-14 -6 404 290', title_attr='A3 թերթի գծագիրը'):
    svg = SVG(prefix)
    Dp = S(M.D); Ap = S(M.A)
    P = [dict(B=S(q['B']), C=S(q['C']), E=S(q['E']), F=S(q['F']), S2=S(q['S2'])) for q in M.POS]
    E0, E0p, F0, F0p, C0, C0p = S(M.E0), S(M.E0p), S(M.F0), S(M.F0p), S(M.C0), S(M.C0p)
    B0, B0p = S(M.B0), S(M.B0p)
    W = 2  # working position

    svg.layer('grid'); draw_grid(svg)

    # ---------- synthesis / construction ----------
    svg.layer('constr')
    svg.line(Dp, (Dp[0], 5.0), 'axis')                                   # slider guide through D
    svg.arc(Dp, M.ED, ang(M.E0)-5, ang(M.E0p)+5, 'con')                 # path of E
    svg.arc(Dp, M.CD, ang(M.C0)-5, ang(M.C0p)+5, 'con')                 # path of C
    svg.line(Ap, C0, 'dd'); svg.line(C0p, B0p, 'dd')                     # dead positions A-B0-C0, C0'-A-B0'
    for a, b in ((Dp, E0), (Dp, E0p), (Dp, C0), (Dp, C0p)):
        svg.line(a, b, 'con2')
    svg.line(E0, F0, 'con2'); svg.line(E0p, F0p, 'con2')
    svg.arc(E0p, M.EF, ang(sub(F0p, E0p))-6, ang(sub(F0p, E0p))+6, 'con')  # arc giving F0'
    svg.arc(F0, M.EF, ang(sub(E0, F0))-6, ang(sub(E0, F0))+6, 'con')      # arc giving E0
    # beta
    svg.line(Dp, polar(Dp, 131, ang(M.E0p)), 'con2')
    svg.arc(Dp, 127, -90, ang(M.E0p), 'mark', n=8)
    svg.text((80.5, 124.5), f'β={num(M.BETA,0)}°', 'lbl sm', anchor='end')
    # psi
    svg.arc(Dp, 48, ang(M.E0), ang(M.E0p), 'mark')
    svg.text(polar(Dp, 54, ang(M.E0)-4), f'ψ={num(M.PSI,1)}°', 'lbl sm', anchor='end')
    for key, p, lab in (('E0', E0, 'E₀'), ('E0p', E0p, 'E₀′'), ('F0', F0, 'F₀'), ('F0p', F0p, 'F₀′'),
                        ('C0', C0, 'C₀'), ('C0p', C0p, 'C₀′'), ('B0', B0, 'B₀'), ('B0p', B0p, 'B₀′')):
        svg.point(p, key, lab, r=0.6, cls='jt ext')

    svg.circle(Ap, M.ABS, 'con')
    # ---------- base (supports, always visible) ----------
    svg.layer('base')
    ground(svg, Dp, up=True); ground(svg, Ap, up=False)
    svg.point(Dp, 'D', 'D', r=1.2, cls='jt big'); svg.point(Ap, 'A', 'A', r=1.2, cls='jt big')
    # ---------- synthesis-figure-only marks ----------
    svg.layer('synonly')
    svg.arc(Dp, 34, ang(M.E0p), ang(M.C0p), 'mark')
    svg.text(polar(Dp, 39.5, (ang(M.E0p)+ang(M.C0p))/2), f'α={num(M.ALPHA,0)}°', 'lbl sm')
    # ---------- all positions ----------
    svg.layer('pos')
    for i, q in enumerate(P):
        if i == W: continue
        svg.add(f'<g class="posg" data-pos="{i}">')
        svg.line(q['B'], q['C'], 'ln'); svg.line(Dp, q['C'], 'ln'); svg.line(Dp, q['E'], 'ln'); svg.line(q['E'], q['F'], 'ln')
        svg.line(Ap, q['B'], 'ln')
        for key in ('B', 'C', 'E', 'F'):
            svg.point(q[key], f'{key}{i}', f'{key}{i}', r=0.5)
        svg.add('</g>')

    # ---------- working position ----------
    svg.layer('work')
    q = P[W]
    svg.add(f'<g class="posg" data-pos="{W}">')
    for a, b in ((Ap, q['B']), (q['B'], q['C']), (Dp, q['C']), (Dp, q['E']), (q['E'], q['F'])):
        svg.line(a, b, 'wk')
    F2 = q['F']
    svg.add(f'<rect x="{fx(F2[0]-3.5)}" y="{fx(GH-F2[1]-5.5)}" width="7" height="11" class="slider"/>')
    rail_top = (86.5, F0[1]+9); rail_bot = (86.5, F0p[1]-9)
    svg.line(rail_top, rail_bot, 'thick'); hatch(svg, rail_bot, rail_top, (-1.0, 0.0))
    for key in ('B', 'C', 'E', 'F'):
        svg.point(q[key], f'{key}{W}', f'{key}{W}', r=1.0, cls='jt big')
    svg.point(q['S2'], 'S2', 'S₂ (դիրք 2)', r=0.7, cls='jt s2')
    svg.add('</g>')
    # alpha at working position
    svg.arc(Dp, 60, ang(sub(q['E'], Dp)), ang(sub(q['C'], Dp)), 'mark')
    svg.text((92.3, 189.5), f'α={num(M.ALPHA,0)}°', 'lbl sm', anchor='start')

    # ---------- labels ----------
    svg.layer('xlabels')
    svg.text((Dp[0]-4.2, Dp[1]+2.2), 'D', 'lbl big')
    svg.text((Ap[0]+5.8, Ap[1]-3.2), 'A', 'lbl big')
    svg.text(polar(Ap, M.ABS+9.5, ang(sub(B0, Ap))+9), 'B₀', 'lbl')
    svg.text(polar(Ap, M.ABS+9.0, ang(sub(B0p, Ap))-12), 'B₀′', 'lbl')
    svg.text(add(C0, (-5.2, 0.6)), 'C₀', 'lbl'); svg.text(add(C0p, (4.6, 2.4)), 'C₀′', 'lbl')
    svg.text(add(E0, (-3.4, 3.6)), 'E₀', 'lbl')
    svg.text((94.0, E0p[1]+0.9), 'E₀′', 'lbl', anchor='start'); svg.line((93.4, E0p[1]+0.5), (E0p[0]+1.0, E0p[1]), 'ext')
    svg.text((64.5, F0[1]+2.0), 'F₀', 'lbl'); svg.text((64.5, F0p[1]-2.2), 'F₀′', 'lbl')
    svg.layer('labels')
    # crank numbers
    for i, qq in enumerate(P):
        a = ang(sub(qq['B'], Ap))
        svg.text(polar(Ap, M.ABS+3.4, a), str(i), 'lbl num')
    svg.text(add(P[W]['B'], (-4.6, 2.8)), 'B', 'lbl')
    # C numbers (grouped)
    def grp(key, groups, r, dr=4.2, center=Dp, extra_ang=0.0):
        for idxs, text in groups:
            a = sum(ang(sub(P[i][key], center)) for i in idxs)/len(idxs)
            svg.text(polar(center, r+dr, a+extra_ang), text, 'lbl num')
    grp('C', [((0,), '0'), ((1, 7), '1,7'), ((2, 6), '2,6'), ((3,), '3'), ((5,), '5'), ((4,), '4')], M.CD, dr=4.4)
    svg.text(add(P[W]['C'], (-4.6, -1.4)), 'C', 'lbl')
    grp('E', [((0,), '0'), ((1, 7), '1,7'), ((3,), '3')], M.ED, dr=4.0)
    svg.text(add(P[W]['E'], (-4.2, -3.4)), '2,6', 'lbl num')
    svg.text(polar(Dp, M.ED-4.6, ang(sub(P[5]['E'], Dp))-2.2), '5', 'lbl num')
    svg.text(polar(Dp, M.ED-4.6, -91.2), '4', 'lbl num')
    svg.text(add(P[W]['E'], (-3.8, 2.6)), 'E', 'lbl')
    svg.text(add(P[W]['S2'], (0.8, 3.6)), 'S₂', 'lbl')
    svg.text(add(P[W]['F'], (-7.0, 1.8)), 'F', 'lbl')
    # F numbers
    Fy = [qq['F'][1] for qq in P]
    svg.text((95.2, Fy[0]+1.6), '0', 'lbl num', anchor='start')
    svg.text((95.2, (Fy[1]+Fy[7])/2+1.8), '1,7', 'lbl num', anchor='start')
    svg.text((95.2, Fy[2]+1.6), '2', 'lbl num', anchor='start')
    svg.text((95.2, Fy[6]-1.6), '6', 'lbl num', anchor='start')
    svg.text((95.2, Fy[3]+1.6), '3', 'lbl num', anchor='start')
    svg.text((95.2, min(Fy[4], Fy[5])-2.4), '4,5', 'lbl num', anchor='start')

    # ---------- dimensions & notes ----------
    svg.layer('dims')
    # L1
    y1 = M.L1_DIM_Y
    svg.line((Ap[0], Ap[1]-M.ABS-2), (Ap[0], y1-3), 'ext')
    svg.line((Dp[0]+0.1, y1), (Ap[0], y1), 'dim', marker='k', extra='')
    svg.line((Ap[0], y1), (Dp[0]+0.1, y1), 'dim', marker='k')
    svg.text(((Dp[0]+Ap[0])/2, y1+2.4), f'L₁*={num(M.L1S,0)}', 'lbl sm')
    # L2
    x2 = M.L2_DIM_X
    svg.line((Dp[0]+6.5, Dp[1]), (x2+3, Dp[1]), 'ext'); svg.line((Ap[0]+7, Ap[1]), (x2+3, Ap[1]), 'ext')
    svg.line((x2, Dp[1]), (x2, Ap[1]), 'dim', marker='k'); svg.line((x2, Ap[1]), (x2, Dp[1]), 'dim', marker='k')
    svg.text((x2-2.6, (Dp[1]+Ap[1])/2), f'L₂*={num(M.L2S,1)}', 'lbl sm', rotate=-90)
    # H_F
    xh = M.HF_DIM_X
    svg.line((86.0, F0[1]), (xh-3, F0[1]), 'ext'); svg.line((86.0, F0p[1]), (xh-3, F0p[1]), 'ext')
    svg.line((xh, F0[1]), (xh, F0p[1]), 'dim', marker='k'); svg.line((xh, F0p[1]), (xh, F0[1]), 'dim', marker='k')
    svg.text((xh-2.6, (F0[1]+F0p[1])/2), f'H<tspan class="sub" dy="0.9">F</tspan><tspan dy="-0.9">*={num(M.H,1)}</tspan>', 'lbl sm', rotate=-90)
    svg.text((200, 265.2), 'Մեխանիզմի դիրքերի պլանը', 'lbl ttl')
    svg.text((200, 260.6), f'μ<tspan class="sub" dy="0.9">l</tspan><tspan dy="-0.9"> = {num(M.MU,5)} մ/մմ</tspan>', 'lbl')

    # ---------- F_re diagram ----------
    svg.layer('diag')
    x0 = M.DIAG_X; wF = M.FMAX/M.MUF; ytop = F0[1]; ybot = F0p[1]
    svg.line((x0, ytop), (x0, ybot-6), 'thick', marker='k')
    svg.line((x0, ytop), (x0+wF+7, ytop), 'thick', marker='k')
    svg.line((x0+wF, ytop), (x0+wF, ybot), 'con2'); svg.line((x0, ybot), (x0+wF, ybot), 'con2')
    curve = [(x0+wF*M.fre_shape(k/60), ytop-M.H*k/60) for k in range(61)]
    svg.poly(curve, 'curve')
    for i, qq in enumerate(P):
        yF = qq['F'][1]
        work = 1 <= i <= 4
        xe = x0 + (wF*M.fre_shape(M.POS[i]['sF']/M.H) if work else 0.0)
        svg.line((qq['F'][0]+4.0, yF), (max(xe, x0), yF), 'proj')
        if work and xe > x0 + 0.5:
            svg.point((xe, yF), f'Fre{i}', f'F_re, դիրք {i}', r=0.55, cls='jt')
    svg.text((x0+wF+9.5, ytop+0.2), 'F<tspan class="sub" dy="0.9">re</tspan>', 'lbl', anchor='start')
    svg.text((x0-3.4, ybot-6.5), 'S<tspan class="sub" dy="0.9">F</tspan>', 'lbl', anchor='end')
    svg.text((x0+wF, ytop+2.6), f'{num(M.FMAX,0)} Ն', 'lbl xs')
    svg.text((x0+wF/2+2, 5.0), f'μ<tspan class="sub" dy="0.9">F</tspan><tspan dy="-0.9"> = {num(M.MUF,0)} Ն/մմ</tspan>', 'lbl sm')

    # ---------- acceleration plan ----------
    svg.layer('aplan')
    a = M.aplan(M.PA_POS); pt = {k: add(M.PA, vv) for k, vv in a.items()}
    svg.add('<g class="plan ap" data-plan="a2">')
    def av(p1, p2, cls='acc'):
        svg.line(pt[p1], pt[p2], cls, marker='a' if mag(sub(pt[p2], pt[p1])) > 4 else None)
    svg.line(pt['b'], pt['c'], 'atri')
    av('pi', 'b'); av('b', 'n2', 'accr'); av('n2', 'c', 'accr'); av('pi', 'n3', 'accr'); av('n3', 'c', 'accr')
    av('pi', 'c'); av('pi', 'e'); svg.line(pt['c'], pt['e'], 'atri'); av('e', 'n4', 'accr'); av('n4', 'f', 'accr')
    av('pi', 'f'); av('pi', 's2', 'accs')
    names = dict(pi='π (a, d)', b='b', n2='n₂', c='c', n3='n₃', e='e', n4='n₄', f='f', s2='s₂')
    offs = dict(pi=(4.4, -3.0), b=(3.0, -2.0), n2=(3.2, 1.4), c=(-3.0, -1.6), n3=(-3.3, 2.2), e=(3.4, -0.6), n4=(-4.2, 1.2), f=(3.0, 2.4), s2=(-3.4, -0.4))
    for k in ('b', 'n2', 'c', 'n3', 'e', 'n4', 'f', 's2', 'pi'):
        svg.point(pt[k], f'a2{k}', f'{names[k]} (արագ. պլան 2)', r=0.7 if k == 'pi' else 0.55, cls='jt ajt')
        svg.text(add(pt[k], offs[k]), names[k], 'lbl al', anchor='start' if offs[k][0] > 0 else 'end')
    q1 = add(pt['n2'], scl(sub(pt['c'], pt['n2']), 0.25)); q2 = add(pt['pi'], scl(sub(pt['b'], pt['pi']), 0.25))
    svg.text(add(q1, (2.6, 0)), '⊥BC', 'lbl dir', rotate=fx(-ang(sub(pt['c'], pt['n2']))+180))
    svg.text(add(q2, (-2.6, 0)), 'B→A', 'lbl dir', rotate=fx(-ang(sub(pt['b'], pt['pi']))-180))
    cx, cy = M.PA_CAP
    svg.text((cx, cy), 'Արագացումների պլան', 'lbl al ttl2', anchor='start')
    svg.text((cx, cy-5.0), f'դիրք {M.PA_POS} (հաստ դիրք)', 'lbl al sm', anchor='start')
    svg.text((cx, cy-10.6), f'μ<tspan class="sub" dy="0.9">a</tspan><tspan dy="-0.9"> = {num(M.MUA,4)} (մ/վ²)/մմ</tspan>', 'lbl al sm', anchor='start')
    svg.text((cx, cy-15.4), 'πb = 70 մմ', 'lbl al sm', anchor='start')
    svg.add('</g>')

    svg.layer('title'); draw_title(svg, 1, 'Դիրքեր, F<tspan class="sub" dy="0.6">re</tspan><tspan dy="-0.6">, արագացումներ</tspan>')

    order = ['grid', 'constr', 'synonly', 'pos', 'diag', 'work', 'base', 'dims', 'labels', 'xlabels', 'aplan', 'title']
    return _wrap(svg, prefix, order, only, exclude, viewbox, title_attr)

def _wrap(svg, prefix, order, only, exclude, viewbox, title_attr):
    body = []
    for name in order:
        if only is not None and name not in only: continue
        if only is None and name in exclude: continue
        body.append(f'<g data-layer="{name}">' + ''.join(svg.layers.get(name, [])) + '</g>')
    defs = (f'<defs>'
            f'<marker id="{prefix}-ar-k" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="2.6" markerHeight="2.6" markerUnits="userSpaceOnUse" orient="auto"><path d="M0 1.2L10 5L0 8.8z" class="mk-k"/></marker>'
            f'<marker id="{prefix}-ar-v" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="2.8" markerHeight="2.8" markerUnits="userSpaceOnUse" orient="auto"><path d="M0 1.2L10 5L0 8.8z" class="mk-v"/></marker>'
            f'<marker id="{prefix}-ar-a" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="2.8" markerHeight="2.8" markerUnits="userSpaceOnUse" orient="auto"><path d="M0 1.2L10 5L0 8.8z" class="mk-a"/></marker>'
            f'</defs>')
    return (f'<svg class="sheet" id="{prefix}" viewBox="{viewbox}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title_attr}">'
            f'<rect x="-14" y="-6" width="404" height="290" class="paper"/>' + defs + ''.join(body) + '</svg>')

def build2(prefix='sh2', viewbox='-14 -6 404 290', title_attr='A3 թերթ 2. արագությունների պլաններ'):
    """second A3 sheet: the eight velocity plans in a 4 × 2 layout"""
    svg = SVG(prefix)
    svg.layer('grid'); draw_grid(svg)
    svg.layer('head')
    svg.text((190, 263.5), 'Արագությունների պլաններ', 'lbl ttl')
    svg.text((190, 258.0), f'μ<tspan class="sub" dy="0.9">V</tspan><tspan dy="-0.9"> = {num(M.MUV,5)} (մ/վ)/մմ,   pb = 50 մմ</tspan>', 'lbl vl')
    for y in (137.0,):                                           # row separator
        svg.add(f'<line x1="6" y1="{fx(GH-y)}" x2="374" y2="{fx(GH-y)}" class="sep"/>')
    for x in (96.5, 189.5, 282.5):                               # column separators
        svg.add(f'<line x1="{fx(x)}" y1="{fx(GH-252)}" x2="{fx(x)}" y2="{fx(GH-24)}" class="sep"/>')
    svg.layer('vplan')
    caps = {}
    for i, pole in M.PV2.items():
        caps[i] = (M.V2_COLS[i % 4], (143.0 if i < 4 else 26.5))
    draw_vplans(svg, M.PV2, caps)
    svg.layer('title'); draw_title(svg, 2, 'Արագությունների պլաններ')
    return _wrap(svg, prefix, ['grid', 'head', 'vplan', 'title'], None, (), viewbox, title_attr)

SHEET_CSS = """
.sheet{display:block;width:100%;height:auto;font-family:"STIX Two Text","Noto Sans Armenian","Times New Roman",serif}
.sheet .paper{fill:#FFFDF8}
.sheet .g1{stroke:#F6DDD0;stroke-width:.07;fill:none}
.sheet .g5{stroke:#F0C4AE;stroke-width:.1;fill:none}
.sheet .g10{stroke:#E6A283;stroke-width:.16;fill:none}
.sheet .g50{stroke:#D97A52;stroke-width:.3;fill:none}
.sheet .ax{font-size:2.2px;fill:#C0643E;font-family:"JetBrains Mono",ui-monospace,monospace}
.sheet .ax5{font-weight:700;fill:#A34E2C}
.sheet line,.sheet path,.sheet circle.con{fill:none}
.sheet .axis{stroke:#46505A;stroke-width:.18;stroke-dasharray:6 1.2 1 1.2}
.sheet .con{stroke:#6E7A80;stroke-width:.2}
.sheet .con2{stroke:#8A959A;stroke-width:.18;stroke-dasharray:1.6 1}
.sheet .dd{stroke:#46505A;stroke-width:.2;stroke-dasharray:5 1 1 1}
.sheet .mark{stroke:#3B4448;stroke-width:.22}
.sheet .ln{stroke:#3B4448;stroke-width:.24}
.sheet .wk{stroke:#111518;stroke-width:.75;stroke-linecap:round}
.sheet .tri{fill:rgba(17,21,24,.06);stroke:none}
.sheet .thick{stroke:#1D2326;stroke-width:.45}
.sheet .sup{fill:#FFFDF8;stroke:#1D2326;stroke-width:.4}
.sheet .hatch{stroke:#1D2326;stroke-width:.2}
.sheet .slider{fill:#FFFDF8;stroke:#111518;stroke-width:.6}
.sheet .ext{stroke:#46505A;stroke-width:.16}
.sheet .dim{stroke:#46505A;stroke-width:.18}
.sheet .proj{stroke:#6E7A80;stroke-width:.16;stroke-dasharray:1.2 .8}
.sheet .curve{stroke:#1D2326;stroke-width:.55}
.sheet .jt{fill:#1D2326;stroke:none}
.sheet .jt.big{fill:#FFFDF8;stroke:#111518;stroke-width:.4}
.sheet .jt.ext{fill:#FFFDF8;stroke:#1D2326;stroke-width:.3}
.sheet .jt.s2{fill:#1D2326}
.sheet .vec{stroke:#1F54A3;stroke-width:.5}
.sheet .vecr{stroke:#1F54A3;stroke-width:.3}
.sheet .vecs{stroke:#1F54A3;stroke-width:.22;stroke-dasharray:1.4 .8}
.sheet .vtri{stroke:#1F54A3;stroke-width:.2;stroke-dasharray:.8 .8}
.sheet .vp .jt{fill:#1F54A3}
.sheet .acc{stroke:#1E6B52;stroke-width:.5}
.sheet .accr{stroke:#1E6B52;stroke-width:.3}
.sheet .accs{stroke:#1E6B52;stroke-width:.22;stroke-dasharray:1.4 .8}
.sheet .atri{stroke:#1E6B52;stroke-width:.2;stroke-dasharray:.8 .8}
.sheet .ajt{fill:#1E6B52}
.sheet .mk-k{fill:#1D2326}.sheet .mk-v{fill:#1F54A3}.sheet .mk-a{fill:#1E6B52}
.sheet .lbl{font-size:3.1px;fill:#15191B}
.sheet .lbl.big{font-size:3.8px;font-style:italic}
.sheet .lbl.num{font-size:2.5px;fill:#39434A;font-family:"JetBrains Mono",ui-monospace,monospace}
.sheet .lbl.sm{font-size:2.6px}
.sheet .lbl.xs{font-size:2.1px;fill:#4A555B}
.sheet .lbl.ttl{font-size:3.4px;font-weight:600}
.sheet .lbl.ttl2{font-size:3.1px;font-weight:600}
.sheet .lbl.cap{font-size:3.2px;font-weight:600}
.sheet .sep{stroke:#9AA3A8;stroke-width:.2;stroke-dasharray:3 1.5}
.sheet .lbl.vl{fill:#1F54A3}
.sheet .lbl.al{fill:#1E6B52}
.sheet .lbl.dir{font-size:1.9px;fill:#56626A}
.sheet tspan.sub{font-size:72%}
.sheet .tbox{fill:#FFFDF8;stroke:#1D2326;stroke-width:.45}
.sheet .tbl{stroke:#1D2326;stroke-width:.3}
"""

if __name__ == '__main__' and False:
    s = build()
    open('sheet_preview.svg', 'w').write(s.replace('<svg ', '<svg width="1600" height="1140" ', 1).replace('<defs>', f'<style>{SHEET_CSS}</style><defs>', 1))
    print('ok', len(s))
