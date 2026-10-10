"""bacatrutyun.html: a from-zero explanation of task 2 (variant 1), in the same style as the other subject's explanation page.
Run:  python3 explain.py   → ../bacatrutyun.html"""
import math, os
import model as M
import calc as C
from model import S, sub, add, scl, mag, ang

P2 = M.PA_POS
v2 = C.vchain(P2); a2 = C.achain(P2)

def t(x, nd=1):
    """number for KaTeX: decimal comma, unicode minus"""
    s = f"{C.r(x, nd):.{nd}f}".replace('.', '{,}')
    return s
def h(x, nd=1):
    """number for plain text"""
    return f"{C.r(x, nd):.{nd}f}".replace('.', ',').replace('-', '−')

COL = dict(s1='#d9480f', s2='#2b8a3e', s3='#7048e8', s4='#1971c2', s5='#c2255c', muted='#555', line='#000', soft='#eef3ff')

def markers(pid):
    out = '<defs>'
    for k, c in COL.items():
        out += (f'<marker id="{pid}-{k}" viewBox="0 0 10 10" refX="9.5" refY="5" markerWidth="7" markerHeight="7" '
                f'markerUnits="userSpaceOnUse" orient="auto"><path d="M0,0.8 L10,5 L0,9.2 z" fill="{c}"/></marker>')
    return out + '</defs>'

def f2(v): return f'{v:.1f}'

# ---------------- figure 1: the mechanism in the thick position ----------------
def mech_svg():
    Y = lambda p: (p[0], 270 - p[1])
    P = M.POS[P2]
    A, D = S(M.A), S(M.D); B, Cc, E, F, S2 = (S(P[k]) for k in ('B', 'C', 'E', 'F', 'S2'))
    def L(a, b, col, w=1.6, dash='', mk=None):
        a, b = Y(a), Y(b)
        d = f' stroke-dasharray="{dash}"' if dash else ''
        m = f' marker-end="url(#m1-{mk})"' if mk else ''
        return f'<line x1="{f2(a[0])}" y1="{f2(a[1])}" x2="{f2(b[0])}" y2="{f2(b[1])}" stroke="{col}" stroke-width="{w}"{d}{m} stroke-linecap="round"/>'
    def arc(c, r, a0, a1, col, w=0.6, dash='3 2', n=40):
        pts = [Y((c[0]+r*math.cos(math.radians(a0+(a1-a0)*k/n)), c[1]+r*math.sin(math.radians(a0+(a1-a0)*k/n)))) for k in range(n+1)]
        return f'<polyline points="{" ".join(f"{f2(p[0])},{f2(p[1])}" for p in pts)}" fill="none" stroke="{col}" stroke-width="{w}" stroke-dasharray="{dash}"/>'
    def T(p, s, size=7, col='#000', anchor='middle', weight='400', italic=False):
        p = Y(p); st = ' font-style="italic"' if italic else ''
        return f'<text x="{f2(p[0])}" y="{f2(p[1])}" font-size="{size}" fill="{col}" text-anchor="{anchor}" dominant-baseline="central" font-weight="{weight}"{st}>{s}</text>'
    def J(p, r=2.2):
        p = Y(p); return f'<circle cx="{f2(p[0])}" cy="{f2(p[1])}" r="{r}" fill="#fff" stroke="#000" stroke-width="1"/>'
    def num(p, k, col):
        q = Y(p); return (f'<circle cx="{f2(q[0])}" cy="{f2(q[1])}" r="5" fill="{col}"/>'
                          f'<text x="{f2(q[0])}" y="{f2(q[1])}" font-size="6.5" fill="#fff" text-anchor="middle" dominant-baseline="central" font-weight="700">{k}</text>')
    def ground(c, up):
        s = 1 if up else -1; q = Y(c)
        out = f'<path d="M{f2(q[0])} {f2(q[1])} L{f2(q[0]-4)} {f2(q[1]-s*7)} L{f2(q[0]+4)} {f2(q[1]-s*7)} Z" fill="#fff" stroke="#000" stroke-width="0.9"/>'
        out += f'<line x1="{f2(q[0]-7)}" y1="{f2(q[1]-s*7)}" x2="{f2(q[0]+7)}" y2="{f2(q[1]-s*7)}" stroke="#000" stroke-width="1.1"/>'
        for k in range(8):
            x = q[0]-6.5+k*1.8
            out += f'<line x1="{f2(x)}" y1="{f2(q[1]-s*7)}" x2="{f2(x-2)}" y2="{f2(q[1]-s*10)}" stroke="#000" stroke-width="0.6"/>'
        return out
    o = [f'<svg viewBox="0 6 340 262" role="img" aria-label="Մեխանիզմը 2-րդ դիրքում՝ օղակների համարներով">', markers('m1')]
    o.append(L((90, 262), (90, 14), '#888', 0.7, '6 2 1 2'))                      # slider guide
    o.append(T((95, 18), 'yy', 6.5, '#555', 'start', italic=True))
    o.append(arc(D, M.ED, ang(sub(M.E0, M.D))-6, ang(sub(M.E0p, M.D))+6, '#999'))
    o.append(arc(D, M.CD, ang(sub(M.C0, M.D))-6, ang(sub(M.C0p, M.D))+6, '#999'))
    o.append(arc(A, M.ABS, 0, 360, '#999', n=72))
    q = [Y(D), Y(Cc), Y(E)]
    o.append(f'<polygon points="{" ".join(f"{f2(p[0])},{f2(p[1])}" for p in q)}" fill="{COL["s3"]}" fill-opacity=".09" stroke="none"/>')
    o.append(L(D, Cc, COL['s3'], 2.6)); o.append(L(D, E, COL['s3'], 2.6)); o.append(L(Cc, E, COL['s3'], 0.7, '3 2'))
    o.append(L(A, B, COL['s1'], 2.8)); o.append(L(B, Cc, COL['s2'], 2.6)); o.append(L(E, F, COL['s4'], 2.6))
    rail = [(86.5, 70), (86.5, 14)]; o.append(L(rail[0], rail[1], '#000', 1.0))
    for k in range(18):
        y = 68-k*3.1; o.append(L((86.5, y), (83.5, y-2.2), '#000', 0.5))
    fq = Y(F); o.append(f'<rect x="{f2(fq[0]-4)}" y="{f2(fq[1]-6.5)}" width="8" height="13" fill="#fff" stroke="{COL["s5"]}" stroke-width="2"/>')
    o.append(ground(A, False)); o.append(ground(D, True))
    for p in (A, D, B, Cc, E, F): o.append(J(p))
    q = Y(S2); o.append(f'<circle cx="{f2(q[0])}" cy="{f2(q[1])}" r="1.8" fill="#000"/>')
    # angle α at D
    a0, a1 = ang(sub(E, D)), ang(sub(Cc, D)); o.append(arc(D, 26, a0, a1, '#000', 0.7, ''))
    o.append(T(add(D, (2, -32)), 'α = 50°', 6.5))
    # ω1 arrow (clockwise) around A
    pts = [(A[0]+11*math.cos(math.radians(a)), A[1]+11*math.sin(math.radians(a))) for a in range(250, 130, -10)]
    o.append(f'<polyline points="{" ".join(f"{f2(Y(p)[0])},{f2(Y(p)[1])}" for p in pts)}" fill="none" stroke="{COL["s1"]}" stroke-width="1.2" marker-end="url(#m1-s1)"/>')
    o.append(T(add(A, (-19, 2)), 'ω<tspan font-size="4.5" dy="1.5">1</tspan>', 7.5, COL['s1'], italic=True))
    # labels
    for p, s, d in ((A, 'A', (8, -4)), (D, 'D', (-7, 4)), (B, 'B', (4, 7)), (Cc, 'C', (-6, -5)), (E, 'E', (-7, 0)), (F, 'F', (9, 0)), (S2, 'S₂', (0, 6))):
        o.append(T(add(p, d), s, 8, '#000', italic=True))
    for p, k, col in ((add(scl(add(A, B), 0.5), (9, 0)), 1, COL['s1']), (add(scl(add(B, Cc), 0.5), (0, -7)), 2, COL['s2']), (add(scl(add(D, Cc), 0.5), (8, 2)), 3, COL['s3']),
                      (add(scl(add(D, E), 0.5), (-8, 0)), 3, COL['s3']), (add(scl(add(E, F), 0.5), (-8, 0)), 4, COL['s4']), (add(F, (-12, 0)), 5, COL['s5'])):
        o.append(num(p, k, col))
    o.append(T((200, 30), 'մեխանիզմը 2-րդ (հաստ) դիրքում', 7, '#555'))
    o.append('</svg>')
    return ''.join(o)

# ---------------- figure 2: extreme positions ----------------
def extreme_svg():
    Y = lambda p: (p[0], 270 - p[1])
    A, D = S(M.A), S(M.D); C0, C0p, B0, B0p, E0, E0p = (S(getattr(M, k)) for k in ('C0', 'C0p', 'B0', 'B0p', 'E0', 'E0p'))
    def L(a, b, col, w=1.6, dash=''):
        a, b = Y(a), Y(b); d = f' stroke-dasharray="{dash}"' if dash else ''
        return f'<line x1="{f2(a[0])}" y1="{f2(a[1])}" x2="{f2(b[0])}" y2="{f2(b[1])}" stroke="{col}" stroke-width="{w}"{d} stroke-linecap="round"/>'
    def T(p, s, size=7, col='#000', anchor='middle', italic=False):
        p = Y(p); st = ' font-style="italic"' if italic else ''
        return f'<text x="{f2(p[0])}" y="{f2(p[1])}" font-size="{size}" fill="{col}" text-anchor="{anchor}" dominant-baseline="central"{st}>{s}</text>'
    def J(p, r=2):
        p = Y(p); return f'<circle cx="{f2(p[0])}" cy="{f2(p[1])}" r="{r}" fill="#fff" stroke="#000" stroke-width="1"/>'
    o = ['<svg viewBox="70 4 270 146" role="img" aria-label="Եզրային դիրքերը. ձգված և ծալված">']
    o.append(L(D, C0, '#999', 0.8, '3 2')); o.append(L(D, C0p, '#999', 0.8, '3 2'))
    # stretched: A-B0-C0
    o.append(L(A, B0, COL['s1'], 2.6)); o.append(L(B0, C0, COL['s2'], 2.2))
    # folded: C0'-A-B0'
    o.append(L(C0p, A, COL['s2'], 2.2, '5 2')); o.append(L(A, B0p, COL['s1'], 2.6))
    for p in (A, D, C0, C0p, B0, B0p): o.append(J(p))
    for p, s, d in ((A, 'A', (2, -7)), (D, 'D', (-7, 3)), (C0, 'C₀', (-7, -4)), (C0p, 'C₀′', (-8, 5)), (B0, 'B₀', (0, -7)), (B0p, 'B₀′', (6, -6))):
        o.append(T(add(p, d), s, 8, '#000', italic=True))
    o.append(T((200, 150), f'AC₀ = AB + BC = {h(C.AC0)}', 7, COL['s2']))
    o.append(T((235, 186), f'AC₀′ = BC − AB = {h(C.AC0P)}', 7, COL['s2']))
    o.append('</svg>')
    return ''.join(o)

# ---------------- figure 3 / 4: plans of the thick position ----------------
def plan_svg(kind):
    if kind == 'v':
        pts = M.vplan(P2); k = 4.2; pid = 'mv'
        segs = [('p', 'b', 's1', 2.2, '', '⊥AB'), ('p', 'c', 's3', 2.2, '', '⊥CD'), ('b', 'c', 's2', 1.5, '', ''),
                ('p', 'e', 's3', 2.2, '', '⊥DE'), ('e', 'f', 's4', 1.5, '', '⊥EF'), ('p', 'f', 's5', 2.2, '', '∥ yy'), ('p', 's2', 's2', 1.1, '4 2', '')]
        names = dict(p='p (a, d)', b='b', c='c', e='e', f='f', s2='s₂')
        offs = dict(p=(-16, 0), b=(7, 1), c=(-6, -5), e=(7, 0), f=(-6, 2), s2=(-8, -4))
        tri = [('c', 'e')]
    else:
        pts = M.aplan(P2); k = 2.5; pid = 'ma'
        segs = [('pi', 'b', 's1', 2.2, '', ''), ('b', 'n2', 's2', 1.4, '', ''), ('n2', 'c', 's2', 1.4, '', ''),
                ('pi', 'n3', 's3', 1.4, '', ''), ('pi', 'c', 's3', 2.2, '', ''), ('pi', 'e', 's3', 2.2, '', ''),
                ('e', 'n4', 's4', 1.4, '', ''), ('n4', 'f', 's4', 1.4, '', ''), ('pi', 'f', 's5', 2.2, '', ''), ('pi', 's2', 's2', 1.1, '4 2', '')]
        names = dict(pi='π (a, d)', b='b', n2='n₂', c='c', n3='n₃', e='e', n4='n₄', f='f', s2='s₂')
        offs = dict(pi=(17, 2), b=(-6, 2), n2=(8, 1), c=(-7, -5), n3=(-9, 5), e=(7, 0), n4=(-8, -2), f=(6, -3), s2=(-8, 0))
        tri = [('c', 'e'), ('b', 'c')]
    P = {n_: (p[0]*k, -p[1]*k) for n_, p in pts.items()}
    xs = [p[0] for p in P.values()]; ys = [p[1] for p in P.values()]
    x0, x1, y0, y1 = min(xs)-34, max(xs)+34, min(ys)-22, max(ys)+22
    o = [f'<svg viewBox="{f2(x0)} {f2(y0)} {f2(x1-x0)} {f2(y1-y0)}" style="max-width:{int((x1-x0)*1.9)}px" role="img">', markers(pid)]
    for a, b in tri:
        o.append(f'<line x1="{f2(P[a][0])}" y1="{f2(P[a][1])}" x2="{f2(P[b][0])}" y2="{f2(P[b][1])}" stroke="#999" stroke-width="0.8" stroke-dasharray="3 2"/>')
    for a, b, col, w, dash, lab in segs:
        A_, B_ = P[a], P[b]
        if math.dist(A_, B_) < 3: continue
        d = f' stroke-dasharray="{dash}"' if dash else ''
        o.append(f'<line x1="{f2(A_[0])}" y1="{f2(A_[1])}" x2="{f2(B_[0])}" y2="{f2(B_[1])}" stroke="{COL[col]}" stroke-width="{w}"{d} marker-end="url(#{pid}-{col})"/>')
        if lab:
            mx, my = (A_[0]+B_[0])/2, (A_[1]+B_[1])/2; ux, uy = (B_[0]-A_[0]), (B_[1]-A_[1]); L_ = math.hypot(ux, uy)
            nx, ny = -uy/L_, ux/L_; rot = math.degrees(math.atan2(uy, ux))
            if rot > 90: rot -= 180
            if rot < -90: rot += 180
            o.append(f'<text x="{f2(mx+nx*6)}" y="{f2(my+ny*6)}" font-size="7" fill="#555" text-anchor="middle" dominant-baseline="central" transform="rotate({rot:.0f} {f2(mx+nx*6)} {f2(my+ny*6)})">{lab}</text>')
    for n_, p in P.items():
        o.append(f'<circle cx="{f2(p[0])}" cy="{f2(p[1])}" r="1.8" fill="#000"/>')
        dx, dy = offs[n_]
        o.append(f'<text x="{f2(p[0]+dx)}" y="{f2(p[1]+dy)}" font-size="9" text-anchor="middle" dominant-baseline="central" font-style="italic">{names[n_]}</text>')
    o.append('</svg>')
    return ''.join(o)

# ---------------- page ----------------
R = dict(
    MUL=t(M.MU, 5), L1S=t(M.L1S, 0), H=t(M.H, 0), L2S=t(M.L2S, 2), EF=t(M.EF, 2), ED=t(M.ED, 0), CD=t(M.CD, 0), CE=t(C.CE_S, 2),
    AC0=t(C.AC0), AC0P=t(C.AC0P), SUM=t(C.AC0+C.AC0P), BC=t(C.BC, 2), AB=t(C.AB, 2), LAB=t(C.LAB, 4), LBC=t(C.LBC, 4),
    PSI=t(M.PSI), PHIW=t(M.PHI_W), PHII=t(M.PHI_I), K=t(M.PHI_W/M.PHI_I, 2), GMIN=t(M.GAMMA_MIN),
    W1=t(C.W1, 2), VB=t(C.VB, 3), MUV=t(M.MUV, 5), MUA=t(M.MUA, 4), AB_ACC=t(C.AB_ACC, 2), W1SQ=t(C.W1**2, 1),
    pc=t(v2['pc']), bc=t(v2['bc']), pe=t(v2['pe']), ef=t(v2['ef']), pf=t(v2['pf']), ps2=t(v2['ps2']),
    VC=t(v2['VC'], 3), VCB=t(v2['VCB'], 3), VE=t(v2['VE'], 3), VFE=t(v2['VFE'], 3), VF=t(v2['VF'], 3), VS2=t(v2['VS2'], 3),
    w2=t(v2['w2'], 2), w3=t(v2['w3'], 2), w4=t(v2['w4'], 2),
    aCBn=t(a2['aCBn'], 2), aCDn=t(a2['aCDn'], 2), aFEn=t(a2['aFEn'], 2), bn2=t(a2['bn2']), pin3=t(a2['pin3']), en4=t(a2['en4']),
    n2c=t(a2['n2c']), n3c=t(a2['n3c']), n4f=t(a2['n4f']), pic=t(a2['pic']), pie=t(a2['pie']), pif=t(a2['pif']), pis2=t(a2['pis2']),
    aCBt=t(a2['aCBt'], 2), aCDt=t(a2['aCDt'], 2), aFEt=t(a2['aFEt'], 2), aC=t(a2['aC'], 2), aE=t(a2['aE'], 2), aF=t(a2['aF'], 2), aS2=t(a2['aS2'], 2),
    e2=t(a2['e2'], 1), e3=t(a2['e3'], 1), e4=t(a2['e4'], 1),
    VB0=t(C.vchain(0)['VCB'], 3), W20=t(C.vchain(0)['w2'], 2),
)
TXT = dict(hpc=h(v2['pc']), hVC=h(v2['VC'], 3), hpf=h(v2['pf']), hVF=h(v2['VF'], 3), hVB=h(C.VB, 3), hAB=h(C.AB, 2), hBC=h(C.BC, 2),
           hPSI=h(M.PSI), hGMIN=h(M.GAMMA_MIN), hW1=h(C.W1, 2), hMUV=h(M.MUV, 5), hMUA=h(M.MUA, 4), haF=h(a2['aF'], 2), hw3=h(v2['w3'], 2),
           hw31=h(C.vchain(1)['w3'], 2), hw33=h(C.vchain(3)['w3'], 2), hn2c=h(a2['n2c']), hn3c=h(a2['n3c']), hpe=h(v2['pe']))

vel_rows = ''
for i in range(8):
    c = C.vchain(i)
    vel_rows += (f'<tr{" class=hl" if i == P2 else ""}><td>{i}</td><td>{h(c["VC"],3)}</td><td>{h(c["VE"],3)}</td><td>{h(c["VF"],3)} {c["VFs"]}</td>'
                 f'<td>{h(c["w2"],2)} {c["w2s"]}</td><td>{h(c["w3"],2)} {c["w3s"]}</td><td>{h(c["w4"],2)} {c["w4s"]}</td></tr>')

HTML = r'''<!doctype html>
<html lang="hy">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Առաջադրանք №2 բացատրություն</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'\\(',right:'\\)',display:false}],strict:false});"></script>
<style>
  :root{
    color-scheme: light;
    --bg:#ffffff; --card:#ffffff; --ink:#000000; --muted:#444444; --border:#cfd6e3;
    --pen:#1d3a8a; --accent:#b4232c; --soft:#eef3ff; --warn-bg:#fff6e5; --warn:#9a5b00;
    --ok-bg:#eaf7ee; --ok:#1e7a3c;
    --s1:#d9480f; --s2:#2b8a3e; --s3:#7048e8; --s4:#1971c2; --s5:#c2255c; --line:#000000;
  }
  *{box-sizing:border-box}
  body{margin:0; background:var(--bg); color:var(--ink); font:17px/1.65 "Noto Sans Armenian","Segoe UI",system-ui,sans-serif}
  .page{max-width:900px; margin:0 auto; padding:32px 16px 72px}
  h1{font-size:2rem; margin:0 0 6px; color:var(--pen)}
  .lead{color:var(--muted); margin:0 0 26px}
  h2{font-size:1.35rem; margin:0 0 12px; color:var(--pen)}
  h3{font-size:1.08rem; margin:18px 0 6px}
  .card{background:var(--card); border:1px solid var(--border); border-radius:12px; padding:20px 22px; margin:0 0 22px}
  .toc a{color:var(--pen)}
  .toc ol{margin:6px 0 0; padding-left:22px}
  .tip,.warn,.write{border-radius:8px; padding:10px 14px; margin:12px 0}
  .tip{background:var(--soft); border-left:4px solid var(--pen)}
  .warn{background:var(--warn-bg); border-left:4px solid var(--warn)}
  .write{background:var(--ok-bg); border-left:4px solid var(--ok)}
  .write::before{content:"✍ Տետրում գրիր. "; font-weight:700; color:var(--ok)}
  table{border-collapse:collapse; width:100%; font-size:.95rem}
  th,td{border:1px solid var(--border); padding:6px 9px; text-align:left; vertical-align:top}
  th{background:var(--soft)}
  tr.hl td{background:#fff3bf; font-weight:600}
  .tbl{overflow-x:auto}
  .katex-display{overflow-x:auto; overflow-y:hidden; padding:2px 0}
  svg{max-width:100%; height:auto; display:block; margin:8px auto}
  svg text{font-family:inherit}
  .chip{display:inline-block; padding:0 8px; border-radius:10px; color:#fff; font-weight:600; font-size:.9rem}
  .c1{background:var(--s1)} .c2{background:var(--s2)} .c3{background:var(--s3)} .c4{background:var(--s4)} .c5{background:var(--s5)}
  .flow{display:flex; flex-wrap:wrap; gap:6px; align-items:center; margin:10px 0}
  .flow span.box{border:1px solid var(--border); background:var(--soft); border-radius:8px; padding:4px 10px; font-size:.93rem}
  .flow span.arr{color:var(--muted)}
  .cap{font-size:.88rem; color:var(--muted); text-align:center; margin:2px 0 10px}
  .two{display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:14px; align-items:start}
  ol li, ul li{margin:4px 0}
</style>
</head>
<body>
<div class="page">
  <h1>Առաջադրանք №2 — բացատրություն զրոյից</h1>
  <p class="lead">Մեխանիզմների և մեքենաների տեսություն, տարբերակ 1: Այս էջը միայն <b>հասկանալու</b> համար է: Տետրում գրվող մաքուր լուծումը, A3 թերթերի կոորդինատները և քայլերի ստուգաթերթը մյուս ֆայլում են (<code>TMM_Variant1.html</code>, «Տետր» բաժինը՝ էջ 10–16): Կանաչ «✍» դաշտերը ցույց են տալիս, թե բացատրության որ մասը տետրի որ տողին է վերաբերում:</p>

  <div class="card toc">
    <h2>Բովանդակություն</h2>
    <ol>
      <li><a href="#task">Ինչի՞ մասին է խնդիրը</a></li>
      <li><a href="#scheme">Ինչպես կարդալ սխեման</a></li>
      <li><a href="#data">Տրված տվյալները և բոլոր նշանակումները</a></li>
      <li><a href="#ideas">Չորս գաղափար, որոնց վրա կանգնած է ամեն ինչ</a></li>
      <li><a href="#s1">Քայլ 1 — մասշտաբը և գծագրային երկարությունները</a></li>
      <li><a href="#s2">Քայլ 2 — եզրային դիրքերը, AB-ն և BC-ն</a></li>
      <li><a href="#s3">Քայլ 3 — 8 դիրքերի պլանը</a></li>
      <li><a href="#s4">Քայլ 4 — B կետի արագությունը և μ<sub>v</sub>-ն</a></li>
      <li><a href="#s5">Քայլ 5 — արագությունների պլանի կառուցումը</a></li>
      <li><a href="#s6">Քայլ 6 — թվերը, ω-ները և դրանց ուղղությունը</a></li>
      <li><a href="#s7">Քայլ 7 — արագացումների պլանը (դիրք 2)</a></li>
      <li><a href="#fre">F<sub>re</sub> գրաֆիկը և երկու A3 թերթերը</a></li>
      <li><a href="#assume">Ենթադրություններ — ճշտիր դասախոսի մոտ</a></li>
      <li><a href="#check">Ստուգաթերթ և տարածված սխալներ</a></li>
    </ol>
  </div>

  <!-- ============ TASK ============ -->
  <div class="card" id="task">
    <h2>1. Ինչի՞ մասին է խնդիրը</h2>
    <p>Պատկերացրու մամլիչ կամ դրոշմող մեքենա: Էլեկտրաշարժիչը հավասարաչափ պտտում է <b>կռունկը</b> (կարճ լծակ)՝ րոպեում 210 պտույտ: Մեզ պետք է, որ <b>սողնակը</b> (դանակ, դրոշմ) շարժվի <b>վեր ու վար</b> ուղղաձիգ ուղղորդով՝ 70 մմ ընթացքով: Պտույտը ետ ու առաջ շարժման վերածելու համար օգտագործում են <b>լծակավոր մեխանիզմ</b>. քո մեխանիզմն ունի 5 շարժական օղակ (գումարած անշարժ «հիմքը»):</p>
    <p>Առաջադրանքում պետք է անել երեք բան.</p>
    <ol>
      <li><b>Սինթեզ</b> (§1). գտնել կռունկի և շարժաթևի <b>երկարությունները</b>, որոնք տրված չեն, և գծել մեխանիզմը 8 դիրքում:</li>
      <li><b>Արագություններ</b> (§2). յուրաքանչյուր դիրքում գտնել կետերի արագությունները և օղակների անկյունային արագությունները՝ <b>արագությունների պլանի</b> օգնությամբ:</li>
      <li><b>Արագացումներ</b> (§3). մեկ՝ 2-րդ (աշխատանքային) դիրքի համար գտնել արագացումները՝ <b>արագացումների պլանով</b>:</li>
    </ol>
    <p>Ինչու՞ է սա պետք: Հաջորդ բաժնում (ուժային հաշվարկ) իներցիայի ուժերը հաշվվում են <i>F</i> = <i>m</i>·<i>a</i>-ով, ուստի առանց արագացումների հնարավոր չէ իմանալ, թե ինչ ուժեր են ազդում օղակների վրա: Իսկ թափանիվի հաշվարկին պետք են արագությունները բոլոր դիրքերում:</p>
    <div class="tip">«Պլանը» ուղղակի <b>վեկտորային գծագիր</b> է. արագությունները (կամ արագացումները) գծում ենք սլաքներով մասշտաբով, և հավասարումը լուծում ենք <b>երկրաչափորեն</b>՝ քանոնով և անկյունաչափով, առանց եռանկյունաչափության:</div>
  </div>

  <!-- ============ SCHEME ============ -->
  <div class="card" id="scheme">
    <h2>2. Ինչպես կարդալ սխեման</h2>
    <p>Ահա քո մեխանիզմը 2-րդ (հաստ) դիրքում, իսկական համամասնություններով (A3 թերթի կոորդինատներից): Յուրաքանչյուր օղակ ունի իր գույնը. նույն գույները կտեսնես պլաններում:</p>
    @@MECH@@
    <div class="tbl">
    <table>
      <tr><th>Օղակ</th><th>Անվանում</th><th>Ինչպես է շարժվում</th></tr>
      <tr><td><span class="chip c1">1</span> AB</td><td><b>կռունկ</b></td><td>լրիվ պտտվում է A-ի շուրջը, հավասարաչափ (ω<sub>1</sub> = const), ժամացույցի սլաքի ուղղությամբ</td></tr>
      <tr><td><span class="chip c2">2</span> BC</td><td><b>շարժաթև</b></td><td>բարդ (հարթ-զուգահեռ) շարժում. B-ն գնում է շրջանով, C-ն՝ աղեղով: S<sub>2</sub>-ը նրա մեջտեղն է (զանգվածի կենտրոն)</td></tr>
      <tr><td><span class="chip c3">3</span> CDE</td><td><b>լծակ (ճոճաթև)</b></td><td>կոշտ «անկյուն»՝ երկու թևով (DC և DE), ∠CDE = α = 50°: <b>Ճոճվում</b> է D-ի շուրջը՝ լրիվ չպտտվելով</td></tr>
      <tr><td><span class="chip c4">4</span> EF</td><td><b>շարժաթև</b></td><td>բարդ շարժում. E-ն գնում է աղեղով, F-ը՝ ուղիղ գծով</td></tr>
      <tr><td><span class="chip c5">5</span> F</td><td><b>սողնակ</b></td><td>համընթաց շարժում ուղղաձիգ <i>yy</i> ուղղորդով (D-ով անցնող ուղղաձիգ)</td></tr>
      <tr><td>0</td><td>հենարան (դարակ)</td><td>անշարժ. A և D հոդերը, ուղղորդը: Գծագրում նշվում են շտրիխավորված եռանկյունիներով</td></tr>
    </table>
    </div>
    <h3>Շարժման ճանապարհը</h3>
    <div class="flow">
      <span class="box">Շարժիչ</span><span class="arr">→</span>
      <span class="box"><span class="chip c1">1</span> կռունկը պտտվում է</span><span class="arr">→</span>
      <span class="box"><span class="chip c2">2</span> BC-ն հրում/քաշում է C-ն</span><span class="arr">→</span>
      <span class="box"><span class="chip c3">3</span> լծակը ճոճվում է D-ի շուրջը</span><span class="arr">→</span>
      <span class="box"><span class="chip c4">4</span> EF-ը հրում է F-ը</span><span class="arr">→</span>
      <span class="box"><span class="chip c5">5</span> սողնակը վեր-վար</span>
    </div>
    <p>Մեխանիզմը կազմված է երկու մասից. <b>ABCD քառօղակ</b> (կռունկ-ճոճաթևային), որը պտույտը դարձնում է ճոճում, և <b>DEF խումբ</b>, որը ճոճումը դարձնում է ուղղագիծ շարժում: Դրա համար էլ հաշվարկը միշտ գնում է նույն հերթականությամբ՝ <b>B → C → E → F</b>:</p>
  </div>

  <!-- ============ DATA ============ -->
  <div class="card" id="data">
    <h2>3. Տրված տվյալները</h2>
    <p>Դու առաջադրանքի աղյուսակի №1 տողն ես.</p>
    <div class="tbl">
    <table>
      <tr><th>Նշանակում</th><th>Արժեք</th><th>Ինչ է նշանակում</th></tr>
      <tr><td>\(H_F\)</td><td>70 մմ = 0,07 մ</td><td>սողնակի <b>ընթացքը</b>՝ ամենավերին և ամենաներքին դիրքերի տարբերությունը</td></tr>
      <tr><td>\(L_1\)</td><td>350 մմ</td><td>A և D հոդերի <b>հորիզոնական</b> հեռավորությունը</td></tr>
      <tr><td>\(L_2\)</td><td>150 մմ</td><td>A և D հոդերի <b>ուղղաձիգ</b> հեռավորությունը</td></tr>
      <tr><td>\(l_{EF}\)</td><td>200 մմ</td><td>4 շարժաթևի երկարությունը</td></tr>
      <tr><td>\(l_{ED}\)</td><td>210 մմ</td><td>լծակի DE թևի երկարությունը</td></tr>
      <tr><td>\(n_1\)</td><td>210 պտ/ր</td><td>կռունկի պտուտաթիվը</td></tr>
      <tr><td>\(G_2,\ G_5,\ I_{S_2},\ F_{re}^{max}\)</td><td>38 Ն, 175 Ն, 350, 7800 Ն</td><td>կշիռներ, իներցիայի մոմենտ, օգտակար դիմադրության ուժ. <b>կինեմատիկային պետք չեն</b>, պետք կգան ուժային հաշվարկում</td></tr>
    </table>
    </div>
    <p>Լրացուցիչ պայմաններ. \(l_{CD} = 0{,}9\,l_{ED} = 0{,}189\) մ, \(l_{BS_2} = 0{,}5\,l_{BC}\), \(\beta = 3°\div5°\) (ընդունում ենք 3°), \(\alpha = 50°\):</p>
    <h3>Մյուս տառերը, որոնց կհանդիպես</h3>
    <div class="tbl">
    <table>
      <tr><th>Նշանակում</th><th>Իմաստը</th></tr>
      <tr><td>\(\mu_l\) («մյու»)</td><td><b>երկարությունների մասշտաբ</b>, մ/մմ. գծագրի 1 մմ-ը քանի մետր է իրականում</td></tr>
      <tr><td>\(\mu_v,\ \mu_a\)</td><td>արագությունների ((մ/վ)/մմ) և արագացումների ((մ/վ²)/մմ) մասշտաբները</td></tr>
      <tr><td>աստղանիշ՝ \(AB^*\), \(H_F^*\)</td><td>նույն երկարությունը <b>գծագրի վրա</b>, մմ-ով</td></tr>
      <tr><td>\(p\), \(\pi\)</td><td>արագությունների և արագացումների պլանի <b>բևեռը</b>՝ «զրոյական» կետը. անշարժ կետերը (A, D) պլանում ընկնում են այստեղ</td></tr>
      <tr><td>փոքրատառ \(b, c, e, f, s_2\)</td><td>մեխանիզմի B, C, E, F, S₂ կետերի «պատկերները» պլանում. \(pc\) հատվածը = \(V_C\)-ն մասշտաբով</td></tr>
      <tr><td>\(V_{CB}\)</td><td>C-ի <b>հարաբերական</b> արագությունը B-ի նկատմամբ (կարդա՝ «C-ն B-ի նկատմամբ»)</td></tr>
      <tr><td>\(\omega_2, \omega_3, \omega_4\)</td><td>օղակների անկյունային արագությունները, վ⁻¹ (= ռադ/վ)</td></tr>
      <tr><td>\(a^n,\ a^t\)</td><td>արագացման <b>նորմալ</b> (կենտրոնաձիգ) և <b>շոշափող</b> բաղադրիչներ</td></tr>
      <tr><td>\(n_2, n_3, n_4\)</td><td>արագացումների պլանի օժանդակ կետեր՝ նորմալ բաղադրիչի ծայրը</td></tr>
      <tr><td>\(\varepsilon_2, \varepsilon_3, \varepsilon_4\)</td><td>անկյունային արագացումները, վ⁻²</td></tr>
    </table>
    </div>
  </div>

  <!-- ============ IDEAS ============ -->
  <div class="card" id="ideas">
    <h2>4. Չորս գաղափար, որոնց վրա կանգնած է ամեն ինչ</h2>
    <h3>Գաղափար 1. մասշտաբ</h3>
    <p>Ցանկացած ֆիզիկական մեծություն թղթի վրա դառնում է հատված. <b>իրական = գծագրային × μ</b>, և հակառակը՝ <b>գծագրային = իրական / μ</b>: Սա միակ բանաձևն է, որ պետք է անգիր հիշել. մնացածը դրա կիրառություններն են:</p>
    <h3>Գաղափար 2. պտտվող կետի արագությունը</h3>
    <p>Եթե կետը պտտվում է կենտրոնի շուրջը \(l\) շառավղով, նրա արագությունը</p>
    $$V = \omega\cdot l,\qquad \vec V \perp \text{շառավղին}$$
    <p>Ինչպես անվի եզրը. արագությունը միշտ շոշափող է շրջանին, այսինքն ուղղահայաց շառավղին: Այս պատճառով տետրում ամենուր գրված է «⊥AB», «⊥CD», «⊥EF»:</p>
    <h3>Գաղափար 3. երկու կետ մեկ օղակի վրա</h3>
    <p>Եթե B-ն և C-ն մեկ կոշտ ձողի ծայրերն են, C-ի արագությունը = B-ի արագություն + C-ի պտույտը B-ի շուրջը.</p>
    $$\vec V_C = \vec V_B + \vec V_{CB},\qquad \vec V_{CB}\perp BC$$
    <p>Վեկտորային հավասարումը հարթության վրա = <b>երկու</b> թվային հավասարում, ուստի կարող ենք գտնել <b>երկու</b> անհայտ: Դրա համար տետրում հավասարման տակ գծում ենք «Մեծ. / ուղղ.» աղյուսակը. «+» = հայտնի է, «−» = անհայտ: Եթե «−»-երը ճիշտ երկուսն են, հավասարումը լուծվում է:</p>
    <h3>Գաղափար 4. նմանության թեորեմ</h3>
    <p>Կոշտ օղակի կետերը պլանում կազմում են պատկեր, որը <b>նման</b> է օղակին և նույն կերպ է կողմնորոշված (պտտված 90°-ով): Այսինքն, եթե գիտես c-ն, E-ի պատկերը (e) գտնում ես առանց որևէ հավասարման՝ համամասնությամբ.</p>
    $$\frac{pe}{pc} = \frac{DE}{DC} = \frac{120}{108} = 1{,}111,\qquad \angle cpe = \angle CDE = 50°$$
  </div>

  <!-- ============ STEP 1 ============ -->
  <div class="card" id="s1">
    <h2>Քայլ 1 — Մասշտաբը և գծագրային երկարությունները</h2>
    <h3>Գաղափարը</h3>
    <p>Իրական մեխանիզմը մոտ կես մետր է, իսկ թերթը՝ 42 սմ: Պետք է փոքրացնել: \(L_1 = 0{,}35\) մ հեռավորությունը որոշում ենք գծել <b>200 մմ</b> (կլոր թիվ, որ մեխանիզմը լավ տեղավորվի). մնացած բոլոր երկարությունները հետևում են դրանից:</p>
    $$\mu_l = \frac{L_1}{L_1^*} = \frac{0{,}35}{200} = @@MUL@@\ \text{մ/մմ}$$
    <p>Հիմա յուրաքանչյուր իրական երկարություն բաժանում ենք \(\mu_l\)-ի.</p>
    $$H_F^* = \frac{0{,}07}{@@MUL@@} = @@H@@\ \text{մմ},\quad L_2^* = \frac{0{,}15}{@@MUL@@} = @@L2S@@\ \text{մմ},\quad EF^* = \frac{0{,}2}{@@MUL@@} = @@EF@@\ \text{մմ}$$
    $$ED^* = \frac{0{,}21}{@@MUL@@} = @@ED@@\ \text{մմ},\qquad CD^* = \frac{0{,}189}{@@MUL@@} = @@CD@@\ \text{մմ}$$
    <div class="tip"><b>Ինքնաստուգում.</b> \(CD^*\)-ը պետք է լինի \(ED^*\)-ի 0,9 մասը՝ 0,9·120 = 108 ✔:</div>
    <div class="write">էջ 10–11. \(\mu_l\), \(H_F^*\), \(L_2^*\), \(EF\), \(ED\) (և \(CD\)) տողերը:</div>
  </div>

  <!-- ============ STEP 2 ============ -->
  <div class="card" id="s2">
    <h2>Քայլ 2 — Եզրային դիրքերը, AB-ն և BC-ն</h2>
    <h3>Գաղափարը</h3>
    <p>\(l_{AB}\)-ն և \(l_{BC}\)-ն տրված չեն: Դրանք պետք է ընտրել այնպես, որ սողնակը վեր-վար շարժվի <b>ճիշտ 70 մմ</b>: Գաղտնիքը <b>եզրային դիրքերն</b> են. սողնակը կանգ է առնում ու ետ դառնում այն պահին, երբ կռունկը և շարժաթևը <b>մեկ ուղղի վրա</b> են:</p>
    <h3>ա) Սողնակի և լծակի եզրային դիրքերը</h3>
    <ol>
      <li><b>Ստորին դիրք.</b> DE թևը ուղղաձիգից շեղում ենք β = 3° → E₀′: E₀′-ից EF* = 114,29 մմ շառավղով աղեղը հատում է ուղղորդը → F₀′ (ամենացածր կետը):</li>
      <li><b>Վերին դիրք.</b> F₀′-ից բարձրանում ենք \(H_F^*\) = 40 մմ → F₀: F₀-ից 114,29 մմ աղեղը հատում է E-ի հետագիծը → E₀:</li>
      <li>Լծակը կոշտ է, ուստի C-ն միշտ E-ից 50° «աջ» է. E₀-ից և E₀′-ից ստանում ենք C₀ և C₀′ (կարկինով՝ \(CE^* = @@CE@@\) մմ աղեղով):</li>
    </ol>
    <p>Լծակի ճոճման անկյունը՝ \(\psi = \angle E_0DE_0' = @@PSI@@°\):</p>
    <h3>բ) Ինչու՞ են կռունկը և շարժաթևը մեկ ուղղի վրա</h3>
    @@EXTREME@@
    <p class="cap">Եզրային դիրքերում A, B, C կետերը մեկ ուղղի վրա են. ձախում՝ «ձգված», աջում՝ «ծալված»:</p>
    <p>Երբ C-ն հասնում է իր ամենահեռու կետին (C₀), A-ից C հեռավորությունը <b>ամենամեծն</b> է, և դա հնարավոր է միայն, երբ AB-ն և BC-ն մեկ գծով «ձգված» են. \(AC_0 = AB + BC\): Երբ C-ն ամենամոտ կետում է (C₀′), A-ն ընկնում է B-ի և C-ի միջև, «ծալված»՝ \(AC_0' = BC - AB\): Գծագրից չափում ենք \(AC_0\) և \(AC_0'\) ու լուծում ենք համակարգը.</p>
    $$\begin{cases} AB + BC = @@AC0@@ \\ BC - AB = @@AC0P@@ \end{cases}\quad\Rightarrow\quad 2\cdot BC = @@SUM@@$$
    $$BC = @@BC@@\ \text{մմ},\qquad AB = @@AC0@@ - @@BC@@ = @@AB@@\ \text{մմ}$$
    <p>Հավասարումները <b>գումարում</b> ենք (AB-ն կրճատվում է), դրա համար տետրում համակարգի կողքին գրված է «±»:</p>
    $$l_{AB} = AB\cdot\mu_l = @@AB@@\cdot@@MUL@@ = @@LAB@@\ \text{մ},\qquad l_{BC} = @@BC@@\cdot@@MUL@@ = @@LBC@@\ \text{մ}$$
    <div class="warn">AB-ն և BC-ն թողել եմ 2 նիշով (24,05 և 145,65), որ ստուգումը ճիշտ ստացվի. 24,05 + 145,65 = 169,7 ✔: Եթե կլորացնես 24,1 և 145,7, գումարը 169,8 կլինի: Քո չափած \(AC_0\)-ն կարող է 0,5 մմ-ով տարբերվել, դա նորմալ է. պարզապես նույն երկու տողը հաշվիր քո թվերով:</div>
    <div class="tip"><b>Ստուգում, որ կռունկը լրիվ կպտտվի</b> (Գրասհոֆի պայման). ամենակարճ + ամենաերկար &lt; մյուս երկուսի գումարը. 0,042 + 0,381 = 0,423 &lt; 0,255 + 0,189 = 0,444 ✔: Ճնշման ամենափոքր անկյունը՝ \(\gamma_{min} \approx @@GMIN@@°\) (40°-ից մի փոքր պակաս, ընդունելի է):</div>
    <div class="write">էջ 11. «±» համակարգը ընդհանուր տեսքով (AB₀ + B₀C₀ = AC₀…), հետո թվերով, 2·BC, BC, AB, \(l_{AB}\), \(l_{BC}\):</div>
  </div>

  <!-- ============ STEP 3 ============ -->
  <div class="card" id="s3">
    <h2>Քայլ 3 — 8 դիրքերի պլանը</h2>
    <p>Մեխանիզմը շարժման մեջ ուսումնասիրելու համար «լուսանկարում» ենք 8 պահ: Կռունկի շրջանագիծը (\(R = AB^* = @@AB@@\) մմ) B₀-ից սկսած բաժանում ենք <b>8 հավասար մասի</b> (45°-ական)՝ ժամացույցի սլաքի ուղղությամբ: Ամեն Bᵢ-ի համար կարկինով.</p>
    <div class="flow">
      <span class="box">Bᵢ</span><span class="arr">→ R = BC* →</span>
      <span class="box">Cᵢ (C-ի աղեղի վրա)</span><span class="arr">→ R = CE* →</span>
      <span class="box">Eᵢ (E-ի աղեղի վրա)</span><span class="arr">→ R = EF* →</span>
      <span class="box">Fᵢ (ուղղորդի վրա)</span>
    </div>
    <p>Բոլոր դիրքերը գծում ենք բարակ, իսկ <b>2-րդը՝ հաստ</b>. դա «աշխատանքային» դիրքն է, որի համար անում ենք արագացումների պլանը: 0-րդ դիրքը (B₀) մեռյալ դիրքն է, սողնակը ամենավերևում է:</p>
    <div class="tip">Կռունկը B₀-ից B₀′ պտտվում է \(@@PHIW@@°\) (սողնակը իջնում է՝ <b>աշխատանքային ընթացք</b>), վերադարձին՝ \(@@PHII@@°\) (<b>պարապ ընթացք</b>): \(K = @@PHIW@@/@@PHII@@ = @@K@@ &gt; 1\). պարապ ընթացքն ավելի արագ է: 1, 2, 3, 4 դիրքերը աշխատանքային են, 5, 6, 7-ը՝ պարապ:</div>
    <div class="write">տետրում այս քայլի համար հաշվարկ չկա, միայն թերթ 1-ի գծագիրն է: Գծելու բոլոր քայլերը նշվող վանդակներով՝ <code>TMM_Variant1.html</code>-ում:</div>
  </div>

  <!-- ============ STEP 4 ============ -->
  <div class="card" id="s4">
    <h2>Քայլ 4 — B կետի արագությունը և \(\mu_v\)-ն</h2>
    <h3>Գաղափարը</h3>
    <p>B-ն միակ կետն է, որի արագությունն <b>անմիջապես</b> հայտնի է. նա պտտվում է A-ի շուրջը հայտնի ω<sub>1</sub>-ով (Գաղափար 2): Նախ պտ/ր-ը դարձնում ենք ռադ/վ (1 պտույտ = 2π, 1 րոպե = 60 վ).</p>
    $$\omega_1 = \frac{2\pi n_1}{60} = \frac{\pi n_1}{30} = \frac{3{,}14\cdot210}{30} = @@W1@@\ \text{վ}^{-1}$$
    $$V_B = \omega_1\cdot l_{AB} = @@W1@@\cdot@@LAB@@ = @@VB@@\ \text{մ/վ},\qquad \vec V_B\perp AB$$
    <p>Կռունկը պտտվում է հավասարաչափ, ուստի \(V_B\)-ն <b>բոլոր 8 դիրքերում նույնն է</b>. փոխվում է միայն ուղղությունը:</p>
    <h3>Մասշտաբը</h3>
    <p>Տետրում գրված է «ընդ. pb = 50 մմ»՝ \(V_B\)-ն պլանում կլինի 50 մմ սլաք: Այստեղից.</p>
    $$\mu_v = \frac{V_B}{pb} = \frac{@@VB@@}{50} = @@MUV@@\ \frac{\text{մ/վ}}{\text{մմ}}$$
    <p>Այսինքն պլանի 1 մմ-ը = 0,01852 մ/վ: Ցանկացած հատված պլանում բազմապատկում ես այս թվով ու ստանում արագություն:</p>
    <div class="write">էջ 11. \(V_B\)-ի տողը և «\(\vec V_B\perp AB\) (\(\omega_1\)-ի ուղղությամբ)»: Էջ 12, կետ 6. \(\mu_v\)-ն և «ընդ. pb = 50 մմ»:</div>
  </div>

  <!-- ============ STEP 5 ============ -->
  <div class="card" id="s5">
    <h2>Քայլ 5 — Արագությունների պլանի կառուցումը (դիրք 2-ի օրինակով)</h2>
    @@VPLAN@@
    <p class="cap">Դիրք 2-ի արագությունների պլանը. գույները նույնն են, ինչ սխեմայում: Մոխրագույն կետագիծը՝ նմանության եռանկյան կողմը:</p>
    <h3>ա) b կետը</h3>
    <p>Թղթի վրա ընտրում ենք p բևեռը: Նրանից տանում ենք <b>pb = 50 մմ ⊥ AB</b>, ω<sub>1</sub>-ի պտույտի կողմը: A-ն և D-ն անշարժ են, ուստի նրանց պատկերները (a, d) ընկնում են p-ում:</p>
    <h3>բ) c կետը — հավասարում (1)</h3>
    $$\vec V_C = \vec V_B + \vec V_{CB}$$
    <div class="tbl">
    <table>
      <tr><th></th><th>\(\vec V_C\)</th><th>\(\vec V_B\)</th><th>\(\vec V_{CB}\)</th></tr>
      <tr><td>Մեծ.</td><td>− (անհայտ)</td><td>+ (@@hVB@@ մ/վ)</td><td>− (անհայտ)</td></tr>
      <tr><td>ուղղ.</td><td>+ (⊥CD, C-ն պտտվում է D-ի շուրջը)</td><td>+ (⊥AB)</td><td>+ (⊥BC)</td></tr>
    </table>
    </div>
    <p>Երկու անհայտ (երկու «−») → լուծվում է: Երկրաչափորեն. <b>b-ով</b> տանում ենք ուղիղ ⊥BC (\(V_{CB}\)-ի ուղղությունը), <b>p-ով</b>՝ ուղիղ ⊥CD (\(V_C\)-ի ուղղությունը, քանի որ D-ն p-ում է): Դրանց <b>հատումը c կետն է</b>: Վերջ. չափում ենք pc-ն և bc-ն:</p>
    <h3>գ) e կետը — նմանությամբ (3)</h3>
    <p>E-ն նույն լծակի վրա է, ինչ C-ն (Գաղափար 4). պետք չէ նոր հավասարում.</p>
    $$pe = pc\cdot\frac{DE}{CD} = @@pc@@\cdot1{,}111 = @@pe@@\ \text{մմ},\qquad \angle cpe = 50°$$
    <p>pe-ն տանում ենք ⊥DE, և c-ից e պտույտը նույն կողմն է, ինչ մեխանիզմում C-ից E (ժամացույցի սլաքով): <b>pe-ն չենք չափում, հաշվում ենք</b>:</p>
    <h3>դ) f կետը — հավասարում (4)</h3>
    $$\vec V_F = \vec V_E + \vec V_{FE}$$
    <p>\(V_F\)-ի ուղղությունը հայտնի է (սողնակը կարող է շարժվել միայն ուղղորդով՝ ∥yy), \(V_{FE}\)՝ ⊥EF: Դարձյալ երկու անհայտ մեծություն: <b>e-ով</b> տանում ենք ուղիղ ⊥EF, <b>p-ով</b>՝ ուղղաձիգ: Հատումը f-ն է:</p>
    <h3>ե) s₂ կետը</h3>
    <p>S₂-ը BC-ի մեջտեղում է, ուստի s₂-ը <b>bc հատվածի մեջտեղում է</b> (նմանություն, կետ 5՝ \(bs_2 = cs_2\)): ps₂-ը չափում ենք:</p>
    <div class="warn"><b>Մեռյալ դիրքը (0).</b> A, B, C մեկ ուղղի վրա են, ուստի ⊥AB և ⊥BC ուղիղները համընկնում են, և c-ն ընկնում է p-ի վրա. \(V_C = V_E = V_F = 0\), \(bc = pb = 50\) մմ, s₂-ը pb-ի մեջտեղում: Պլանը պարզապես մեկ սլաք է: Սա սխալ չէ. սողնակն այդ պահին կանգնած է ու շրջվում է:</div>
    <div class="write">էջ 11–12. հավասարումներ (1), (3), (4)՝ իրենց «Մեծ./ուղղ.» աղյուսակներով, կետ 5-ը (\(bs_2 = cs_2\)) և \(\angle cpe = \alpha\) տողը:</div>
  </div>

  <!-- ============ STEP 6 ============ -->
  <div class="card" id="s6">
    <h2>Քայլ 6 — Թվերը, ω-ները և դրանց ուղղությունը</h2>
    <p>Պլանից չափում ենք հատվածները (մմ) և բազմապատկում \(\mu_v\)-ով (դիրք 2).</p>
    $$V_C = pc\cdot\mu_v = @@pc@@\cdot@@MUV@@ = @@VC@@\ \text{մ/վ}\qquad V_E = pe\cdot\mu_v = @@pe@@\cdot@@MUV@@ = @@VE@@\ \text{մ/վ}$$
    $$V_F = pf\cdot\mu_v = @@pf@@\cdot@@MUV@@ = @@VF@@\ \text{մ/վ}\qquad V_{S_2} = ps_2\cdot\mu_v = @@ps2@@\cdot@@MUV@@ = @@VS2@@\ \text{մ/վ}$$
    $$V_{CB} = bc\cdot\mu_v = @@bc@@\cdot@@MUV@@ = @@VCB@@\ \text{մ/վ}\qquad V_{FE} = ef\cdot\mu_v = @@ef@@\cdot@@MUV@@ = @@VFE@@\ \text{մ/վ}$$
    <h3>Անկյունային արագությունները</h3>
    <p>Գաղափար 2-ը «հակառակ»՝ \(\omega = V/l\): Օղակի պտույտը տալիս է <b>հարաբերական</b> արագությունը (կամ անշարժ կետի նկատմամբ արագությունը).</p>
    $$\omega_2 = \frac{V_{CB}}{l_{BC}} = \frac{@@VCB@@}{@@LBC@@} = @@w2@@\ \text{վ}^{-1}$$
    $$\omega_3 = \frac{V_C}{l_{CD}} = \frac{@@VC@@}{0{,}189} = @@w3@@,\quad \omega_4 = \frac{V_{FE}}{l_{EF}} = \frac{@@VFE@@}{0{,}2} = @@w4@@\ \text{վ}^{-1}$$
    <h3>Ինչպես գտնել պտույտի ուղղությունը (↻ թե ↺)</h3>
    <ol>
      <li>Պլանից վերցրու հարաբերական արագության սլաքը, օրինակ՝ \(\vec V_{CB}\) (b-ից c):</li>
      <li>Մտովի տեղափոխիր այն մեխանիզմի <b>C</b> կետ:</li>
      <li>Նայիր, թե ինչ կողմ է այն «պտտում» C-ն B-ի շուրջը. դա \(\omega_2\)-ի ուղղությունն է:</li>
    </ol>
    <p>\(\omega_3\)-ի համար՝ \(\vec V_C\)-ն (p-ից c) դնում ես C-ում ու նայում D-ի շուրջը, \(\omega_4\)-ի համար՝ \(\vec V_{FE}\)-ն (e-ից f) դնում ես F-ում ու նայում E-ի շուրջը:</p>
    <h3>Բոլոր 8 դիրքերը</h3>
    <div class="tbl">
    <table>
      <tr><th>i</th><th>\(V_C\), մ/վ</th><th>\(V_E\)</th><th>\(V_F\)</th><th>\(\omega_2\), վ⁻¹</th><th>\(\omega_3\)</th><th>\(\omega_4\)</th></tr>
      @@VROWS@@
    </table>
    </div>
    <div class="tip"><b>Ինչ է ցույց տալիս աղյուսակը.</b> 1–4 դիրքերում \(V_F\)-ն ↓ է (սողնակը իջնում է՝ աշխատանքային ընթացք), 5–7-ում՝ ↑: 0-ում և ≈4-ում (ներքևի եզր) \(V_F \approx 0\): \(\omega_3\)-ը փոխում է նշանը 4-ի և 5-ի միջև. լծակը շրջվում է: Եթե քո աղյուսակում նույն օրինաչափությունը կա, պլանները ճիշտ են:</div>
    <div class="write">էջ 12–13. կետ 7-ի տողերը դիրք 2-ի համար, \(\omega_2, \omega_3, \omega_4\), իսկ էջ 13-ի աղյուսակում՝ բոլոր 8 տողերը (մյուս դիրքերի հաշվարկը՝ «13ա» ներդիրում):</div>
  </div>

  <!-- ============ STEP 7 ============ -->
  <div class="card" id="s7">
    <h2>Քայլ 7 — Արագացումների պլանը (դիրք 2)</h2>
    <h3>Գաղափարը</h3>
    <p>Պտտվող կետի արագացումն ունի երկու մաս.</p>
    <ul>
      <li><b>նորմալ</b> \(a^n = \omega^2\cdot l\)՝ ուղղված դեպի պտտման <b>կենտրոնը</b> (այն «թեքում» է արագությունը): Հաշվվում է, քանի որ ω-ն արդեն գիտենք §2-ից:</li>
      <li><b>շոշափող</b> \(a^t = \varepsilon\cdot l\)՝ ⊥ շառավղին (այն փոխում է արագության <b>մեծությունը</b>): Անհայտ է, որովհետև ε-ն չգիտենք:</li>
    </ul>
    <p>Ուստի յուրաքանչյուր հավասարումում հարաբերական արագացումը բաժանվում է երկու սլաքի՝ հայտնի \(a^n\) և անհայտ մեծությամբ \(a^t\):</p>
    @@APLAN@@
    <p class="cap">Դիրք 2-ի արագացումների պլանը (πb = 70 մմ): n₂, n₃, n₄՝ նորմալ բաղադրիչների ծայրերը:</p>
    <h3>ա) B կետը</h3>
    $$a_B^t = \varepsilon_1\cdot l_{AB} = \frac{d\omega_1}{dt}\cdot l_{AB} = 0\ \ (\omega_1 = \text{const})$$
    $$a_B = a_B^n = \omega_1^2\cdot l_{AB} = @@W1@@^2\cdot@@LAB@@ = @@AB_ACC@@\ \text{մ/վ}^2,\ \ B\to A$$
    $$\mu_a = \frac{a_B}{\pi b} = \frac{@@AB_ACC@@}{70} = @@MUA@@\ \frac{\text{մ/վ}^2}{\text{մմ}}\qquad (\text{ընդ. } \pi b = 70\ \text{մմ})$$
    <h3>բ) c կետը — հավասարումներ (1), (2), (3)</h3>
    <p>C-ն գրում ենք <b>երկու</b> կողմից. որպես BC-ի կետ և որպես CD-ի կետ, ու հավասարեցնում.</p>
    $$\vec a_B + \vec a_{CB}^n + \vec a_{CB}^t = \vec a_{CD}^n + \vec a_{CD}^t$$
    $$a_{CB}^n = \omega_2^2\, l_{BC} = @@w2@@^2\cdot@@LBC@@ = @@aCBn@@\ \text{մ/վ}^2 \Rightarrow bn_2 = \frac{@@aCBn@@}{@@MUA@@} = @@bn2@@\ \text{մմ}\ \ (C\to B)$$
    $$a_{CD}^n = \omega_3^2\, l_{CD} = @@w3@@^2\cdot0{,}189 = @@aCDn@@\ \text{մ/վ}^2 \Rightarrow \pi n_3 = \frac{@@aCDn@@}{@@MUA@@} = @@pin3@@\ \text{մմ}\ \ (C\to D)$$
    <p><b>Կառուցում.</b> b-ից bn₂ ∥ BC (C-ից B կողմ), n₂-ով՝ ուղիղ ⊥BC: π-ից πn₃ ∥ CD (C-ից D կողմ), n₃-ով՝ ուղիղ ⊥CD: <b>Հատումը c-ն է</b>: Նույն տրամաբանությունը, ինչ արագություններում, միայն յուրաքանչյուր կողմում մի սլաք ավել:</p>
    <h3>գ) e, f, s₂</h3>
    <p>e-ն՝ նմանությամբ. \(\pi e = \pi c\cdot1{,}111 = @@pic@@\cdot1{,}111 = @@pie@@\) մմ, \(\angle c\pi e = 50°\): f-ը՝ \(\vec a_F = \vec a_E + \vec a_{FE}^n + \vec a_{FE}^t\), որտեղ \(a_{FE}^n = \omega_4^2 l_{EF} = @@w4@@^2\cdot0{,}2 = @@aFEn@@\), \(en_4 = @@en4@@\) մմ (F→E), n₄-ով ⊥EF, π-ով ուղղաձիգ: s₂-ը՝ bc-ի մեջտեղում:</p>
    <h3>դ) Թվերը</h3>
    $$a_C = \pi c\cdot\mu_a = @@pic@@\cdot@@MUA@@ = @@aC@@,\qquad a_E = \pi e\cdot\mu_a = @@pie@@\cdot@@MUA@@ = @@aE@@\ \text{մ/վ}^2$$
    $$a_F = \pi f\cdot\mu_a = @@pif@@\cdot@@MUA@@ = @@aF@@,\qquad a_{S_2} = \pi s_2\cdot\mu_a = @@pis2@@\cdot@@MUA@@ = @@aS2@@\ \text{մ/վ}^2$$
    $$a_{CB}^t = n_2c\cdot\mu_a = @@n2c@@\cdot@@MUA@@ = @@aCBt@@\ \text{մ/վ}^2$$
    $$a_{CD}^t = n_3c\cdot\mu_a = @@n3c@@\cdot@@MUA@@ = @@aCDt@@,\qquad a_{FE}^t = n_4f\cdot\mu_a = @@n4f@@\cdot@@MUA@@ = @@aFEt@@\ \text{մ/վ}^2$$
    $$\varepsilon_2 = \frac{a_{CB}^t}{l_{BC}} = @@e2@@,\qquad \varepsilon_3 = \frac{a_{CD}^t}{l_{CD}} = @@e3@@,\qquad \varepsilon_4 = \frac{a_{FE}^t}{l_{EF}} = @@e4@@\ \text{վ}^{-2}$$
    <div class="tip"><b>Ինչու՞ են n₃c-ն և n₄f-ը գրեթե զրո (@@hn3c@@ մմ).</b> 2-րդ դիրքում լծակի ω<sub>3</sub>-ը մոտ է իր առավելագույնին (1-ում @@hw31@@, 2-ում @@hw3@@, 3-ում @@hw33@@ վ⁻¹): Առավելագույնի մոտ արագությունը գրեթե չի փոխվում, ուստի ε<sub>3</sub> ≈ 0, և c-ն ընկնում է գրեթե n₃-ի վրա: Սա կառուցման սխալ չէ:</div>
    <div class="tip"><b>Ֆիզիկական ստուգում.</b> 2-րդ դիրքում սողնակը իջնում է (\(V_F\) ↓), իսկ \(a_F\)-ն = @@haF@@ մ/վ² ուղղված է <b>վեր</b>. սողնակը արգելակվում է, քանի որ մոտենում է ներքևի եզրին: Տրամաբանական է ✔:</div>
    <div class="write">էջ 14–16. \(a_B\)-ն (\(a_B^t = 0\)-ի բացատրությամբ), (1), (2), (3) հավասարումները աղյուսակներով, \(\mu_a\)-ն «ընդ. πb = 70 մմ»-ով, \(bn_2, \pi n_3\), \(\pi e\), \(\angle c\pi e = \alpha\), (6)-ը, \(en_4\), հետո բոլոր \(a\)-երն ու \(\varepsilon\)-երը:</div>
  </div>

  <!-- ============ FRE + SHEETS ============ -->
  <div class="card" id="fre">
    <h2>F<sub>re</sub> գրաֆիկը և երկու A3 թերթերը</h2>
    <h3>F<sub>re</sub> գրաֆիկը</h3>
    <p>Սա <b>օգտակար դիմադրության ուժն</b> է՝ այն, ինչ սողնակը «հաղթահարում է» (օրինակ՝ մետաղը դրոշմելիս): Այն գործում է <b>միայն աշխատանքային ընթացքում</b> (սողնակը իջնում է) և ուղղված է շարժմանը հակառակ: Գրաֆիկի ձևը արտագծում ես առաջադրանքի թերթից՝ S<sub>F</sub> առանցքը դնելով ուղղորդին զուգահեռ, որ յուրաքանչյուր Fᵢ-ից հորիզոնական գծով անմիջապես կարդաս F<sub>re</sub>-ն: Մասշտաբը՝ \(\mu_F = 7800/39 = 200\) Ն/մմ: Կինեմատիկային պետք չէ, բայց ուժային հաշվարկում պետք կգա:</p>
    <h3>Ինչ կա ամեն թերթում</h3>
    <div class="two">
      <div class="tip"><b>Թերթ 1.</b> դիրքերի պլանը (8 դիրք, 2-րդը՝ հաստ), եզրային դիրքերի կառուցումը, L₁*, L₂*, H<sub>F</sub>* չափերը, F<sub>re</sub> գրաֆիկը և դիրք 2-ի <b>արագացումների պլանը</b>:</div>
      <div class="tip"><b>Թերթ 2.</b> <b>8 արագությունների պլան</b>, 4 × 2 վանդակներում (վերևում՝ 0–3, ներքևում՝ 4–7), բոլորը նույն μ<sub>v</sub>-ով և pb = 50 մմ:</div>
    </div>
  </div>

  <!-- ============ ASSUMPTIONS ============ -->
  <div class="card" id="assume">
    <h2>Ենթադրություններ — սրանք ճշտիր դասախոսի մոտ</h2>
    <div class="tbl">
    <table>
      <tr><th>Ինչ</th><th>Ընդունված</th><th>Կփոխի՞ արդյունքը</th></tr>
      <tr><td>β անկյունը</td><td>3° (թույլատրված 3°÷5°)</td><td>Այո, մի փոքր. կփոխվեն եզրային դիրքերը, AB-ն, BC-ն և բոլոր թվերը: Եթե դասախոսն այլ β ասի, ամեն ինչ պետք է վերահաշվել:</td></tr>
      <tr><td>Կռունկի պտույտի ուղղությունը</td><td>ժամացույցի սլաքով (↻)</td><td>Եթե սխեմայում հակառակն է, պլանները կլինեն «հայելային», իսկ աշխատանքային ու պարապ ընթացքները՝ տեղերով փոխված:</td></tr>
      <tr><td>pb և πb</td><td>50 և 70 մմ (տետրից)</td><td>Ոչ. փոխվում է միայն պլանի չափը, արագություններն ու արագացումները նույնն են:</td></tr>
      <tr><td>Աշխատանքային դիրքը</td><td>2-րդ (տետր, էջ 14)</td><td>Եթե այլ դիրք պահանջվի, բոլոր դիրքերի արագացումները արդեն կան <code>TMM_Variant1.html</code>-ի աղյուսակներում:</td></tr>
      <tr><td>\(I_{S_2}\)-ի միավորը</td><td>350·10⁻³ կգ·մ² (լուսանկարում վատ է երևում)</td><td>Կինեմատիկայի համար ոչ, ուժային հաշվարկի համար՝ այո:</td></tr>
      <tr><td>F<sub>re</sub> կորի ձևը</td><td>թվայնացված է փոքր նկարից</td><td>Կինեմատիկայի համար ոչ:</td></tr>
    </table>
    </div>
  </div>

  <!-- ============ CHECK ============ -->
  <div class="card" id="check">
    <h2>Ստուգաթերթ և տարածված սխալներ</h2>
    <h3>Տետրի հերթականությունը (ինչպես նմուշում)</h3>
    <ol>
      <li>էջ 10. տվյալների աղյուսակ, պայմաններ 1–6, §1-ի վերնագիր, \(\mu_l\), \(H_F^*\), \(L_2^*\)</li>
      <li>էջ 11. \(EF, ED, CD\), «±» համակարգը, AB, BC, \(l_{AB}, l_{BC}\), §2. \(V_B\), հավասարում (1)</li>
      <li>էջ 12. (3) նմանություն, (4), \(bs_2 = cs_2\), \(\mu_v\), կետ 7 (դիրք 2)</li>
      <li>էջ 13. \(\omega_3, \omega_4\) և 8 դիրքերի աղյուսակը (+ «13ա» ներդիր)</li>
      <li>էջ 14–16. §3. արագացումներ դիրք 2-ի համար</li>
    </ol>
    <p>Յուրաքանչյուր տողի համար՝ <b>բանաձև → տեղադրված թվեր → արդյունք՝ միավորով</b>:</p>
    <h3>Ստուգումներ, որոնք ապացուցում են, որ ճիշտ ես արել</h3>
    <ul>
      <li>\(AB + BC = AC_0\) և \(BC - AB = AC_0'\) (24,05 + 145,65 = 169,7)</li>
      <li>Գծագրում սողնակի ընթացքը ճիշտ 40 մմ է (= \(H_F^*\))</li>
      <li>Բոլոր 8 պլաններում pb = 50 մմ, և pb ⊥ համապատասխան AB-ին</li>
      <li>\(pe = 1{,}111\cdot pc\) բոլոր դիրքերում</li>
      <li>0-րդ դիրքում c, e, f ≡ p</li>
      <li>\(V_F\)-ն ↓ 1–4 դիրքերում, ↑ 5–7-ում</li>
      <li>\(a_F\)-ն 2-րդ դիրքում ուղղված է վեր (արգելակում)</li>
    </ul>
    <h3>Տարածված սխալներ</h3>
    <ul>
      <li>\(V_C\)-ն տանել ⊥BC՝ ⊥CD-ի փոխարեն: C-ն պտտվում է <b>D</b>-ի շուրջը, ուստի \(\vec V_C\perp CD\), իսկ ⊥BC-ն հարաբերական \(\vec V_{CB}\)-ի ուղղությունն է:</li>
      <li>pe-ն չափել քանոնով՝ հաշվելու փոխարեն, կամ e-ն դնել c-ի մյուս կողմում (∠cpe-ն պետք է նույն կողմ լինի, ինչ ∠CDE-ն մեխանիզմում):</li>
      <li>Նորմալ արագացումը տանել սխալ կողմ. \(a^n\)-ը միշտ դեպի <b>կենտրոն</b> է՝ C→B, C→D, F→E:</li>
      <li>Մոռանալ, որ \(a_B^t = 0\) (ω<sub>1</sub> = const), և փնտրել ε<sub>1</sub>:</li>
      <li>Տարբեր դիրքերի պլանները գծել տարբեր μ<sub>v</sub>-ով. բոլորը նույն 0,01852-ով են:</li>
      <li>Միավորներ. ω-ն վ⁻¹ (ռադ/վ), ε-ն՝ վ⁻², արագացումները՝ մ/վ²:</li>
    </ul>
  </div>

</div>
</body>
</html>
'''

out = HTML
for k, v_ in R.items(): out = out.replace(f'@@{k}@@', v_)
for k, v_ in TXT.items(): out = out.replace(f'@@{k}@@', v_)
out = (out.replace('@@MECH@@', mech_svg()).replace('@@EXTREME@@', extreme_svg())
          .replace('@@VPLAN@@', plan_svg('v')).replace('@@APLAN@@', plan_svg('a')).replace('@@VROWS@@', vel_rows))
assert '@@' not in out, out[out.index('@@')-40:out.index('@@')+40]
HERE = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(HERE, '..', 'bacatrutyun.html'), 'w').write(out)
print('written', len(out))
