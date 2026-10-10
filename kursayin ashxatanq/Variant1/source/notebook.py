"""The notebook (copybook) pages 10–16, filled in for this variant, laid out like the teacher's template."""
import model as M
import calc as C
from calc import n, r

D_ = M.DATA
P2 = M.PA_POS
vc = {i: C.vchain(i) for i in range(8)}
v2 = vc[P2]; a2 = C.achain(P2)

# ---------------- notation ----------------
def i_(s): return f'<i>{s}</i>'
def q(sym, sub='', sup='', vec=False):
    b = f'<i>{sym}</i>'
    if vec: b = f'<span class="ov">{b}</span>'
    if sub: b += f'<sub>{sub}</sub>'
    if sup: b += f'<sup>{sup}</sup>'
    return b
def fr(a, b): return f'<span class="nf"><span>{a}</span><span>{b}</span></span>'
def L(body, cls=''): return f'<div class="nl {cls}">{body}</div>'
def num(k): return f'<span class="nn">{k})</span>'
def big(t): return f'<b class="nr">{t}</b>'
def sign(cols, mag, dirs, eqno=''):
    """the 'Մեծ. / ուղղ.' table written under a vector equation"""
    head = ''.join(f'<th>{c}</th>' for c in cols)
    return (f'<table class="nsign"><thead><tr><th></th>{head}</tr></thead><tbody>'
            f'<tr><th>Մեծ.</th>{"".join(f"<td>{m}</td>" for m in mag)}</tr>'
            f'<tr><th>ուղղ.</th>{"".join(f"<td>{d}</td>" for d in dirs)}</tr></tbody></table>')

mul = q('μ', 'l'); muv = q('μ', 'v'); mua = q('μ', 'a')
lAB, lBC, lCD, lEF, lED, lDE = (q('l', s) for s in ('AB', 'BC', 'CD', 'EF', 'ED', 'DE'))
w = {k: q('ω', str(k)) for k in range(1, 5)}; e = {k: q('ε', str(k)) for k in range(1, 5)}
MUL = n(M.MU, 5); MUV = n(M.MUV, 5); MUA = n(M.MUA, 4)
s1m = lambda x: n(x, 3)
LCD = n(M.lCD, 3); LEF = n(M.lEF, 1); LBC = n(C.LBC, 4); LAB = n(C.LAB, 4)
DE_CD = f'{n(M.ED, 0)}/{n(M.CD, 0)}'
INV1 = 'վ<sup>−1</sup>'; INV2 = 'վ<sup>−2</sup>'; MS = 'մ/վ'; MS2 = 'մ/վ<sup>2</sup>'
CW = 'ժամ. սլաքի ուղղությամբ'

def page(no, body, side='l'):
    return f'<article class="npage {side}" aria-label="Տետրի էջ {no}"><span class="npno">{no}</span>{body}</article>'

# ---------------- page 10 ----------------
cols = ['H<sub>F</sub>', 'L<sub>1</sub>', 'L<sub>2</sub>', 'l<sub>EF</sub>', 'l<sub>ED</sub>', 'n<sub>1</sub>', 'G<sub>2</sub>', 'G<sub>5</sub>', 'F<sub>re</sub><sup>max</sup>', 'I<sub>S2</sub>']
vals = [D_['HF'], D_['L1'], D_['L2'], D_['lEF'], D_['lED'], D_['n1'], D_['G2'], D_['G5'], int(D_['Fmax']*100), D_['IS2']]
p10 = page(10, f'''
<div class="nbox">Առաջադրանք N 2 <span class="nvar">(տարբերակ {M.VARIANT})</span></div>
<table class="ndata"><thead><tr>{"".join(f"<th><i>{c}</i></th>" for c in cols)}</tr></thead>
<tbody><tr><td colspan="5">·10<sup>−3</sup> մ</td><td>պտ/ր</td><td>Ն</td><td>Ն</td><td>Ն</td><td>·10<sup>−3</sup></td></tr>
<tr class="v">{"".join(f"<td>{x}</td>" for x in vals)}</tr></tbody></table>
<ol class="ncond">
<li>{lCD} = 0,9·{lED} = 0,9·{s1m(M.lED)} = {LCD} մ</li>
<li>{q('l','BS<sub>2</sub>')} = 0,5·{lBC}</li>
<li>{q('M','m')} = const</li>
<li>{q('δ')} = 0,05</li>
<li>{q('β')} = 3°÷5°, ընդ. {q('β')} = {n(M.BETA,0)}°</li>
<li>{q('α')} = {n(M.ALPHA,0)}°</li>
</ol>
<hr class="nrule">
<h4 class="nsec">§1. Մեխանիզմի սինթեզ և դիրքերի պլանի կառուցում</h4>
{L(f"{num(1)} {mul} = {fr(q('L','1'), q('L','1')+'*')} = {fr(n(M.L1,2), n(M.L1S,0))} = {big(MUL)} մ/մմ")}
{L(f"{q('H','F')}* = {fr(q('H','F'), mul)} = {fr(n(M.HF,2), MUL)} = {big(n(M.H,0))} մմ", 'ind')}
{L(f"{q('L','2')}* = {fr(q('L','2'), mul)} = {fr(n(M.L2,2), MUL)} = {big(n(M.L2S,2))} մմ", 'ind')}
''')

# ---------------- page 11 ----------------
p11 = page(11, f'''
{L(f"EF = {fr(lEF, mul)} = {fr(n(M.lEF,2), MUL)} = {big(n(M.EF,2))} մմ", 'ind')}
{L(f"ED = {fr(lED, mul)} = {fr(n(M.lED,2), MUL)} = {big(n(M.ED,0))} մմ", 'ind')}
{L(f"CD = {fr(lCD, mul)} = {fr(LCD, MUL)} = {big(n(M.CD,0))} մմ", 'ind')}
{L(f'''{num(2)} <span class="nsys">± <span class="nbr"><span>AB<sub>0</sub> + B<sub>0</sub>C<sub>0</sub> = AC<sub>0</sub></span><span>B<sub>0</sub>′C<sub>0</sub>′ − AB<sub>0</sub>′ = AC<sub>0</sub>′</span></span></span>
   <span class="nsys"><span class="nbr p"><span>AB<sub>0</sub> = AB<sub>0</sub>′</span><span>B<sub>0</sub>C<sub>0</sub> = B<sub>0</sub>′C<sub>0</sub>′</span></span></span>''')}
{L(f'''<span class="nsys">± <span class="nbr"><span>AB + BC = {n(C.AC0)}</span><span>BC − AB = {n(C.AC0P)}</span></span></span>
   <span class="nside">2·BC = {n(C.AC0+C.AC0P)}; BC = {big(n(C.BC,2))} մմ<br>AB = {n(C.AC0)} − {n(C.BC,2)} = {big(n(C.AB,2))} մմ</span>''', 'ind')}
{L(f"{lAB} = AB·{mul} = {n(C.AB,2)}·{MUL} = {big(LAB)} մ", 'ind')}
{L(f"{lBC} = BC·{mul} = {n(C.BC,2)}·{MUL} = {big(LBC)} մ", 'ind')}
<hr class="nrule">
<h4 class="nsec">§2. Արագությունների պլանների կառուցում</h4>
{L(f"{num(1)} {q('V','B')} = {w[1]}·{lAB} = {fr('π·'+q('n','1'), '30')}·{lAB} = {fr('3,14·'+str(D_['n1']), '30')}·{LAB} = {n(C.W1,2)}·{LAB} = {big(n(C.VB,3))} {MS}")}
{L(f"{q('V','B',vec=True)} ⊥ AB ({w[1]}-ի ուղղությամբ, {CW})", 'ind')}
{L(f"{num(2)} {q('V','C',vec=True)} = {q('V','B',vec=True)} + {q('V','CB',vec=True)} &nbsp;(1)"
   f"<span class='nside'>{q('V','CB',vec=True)} ⊥ BC<br>{q('V','C',vec=True)} ⊥ CD</span>")}
{sign([q('V','C',vec=True), q('V','B',vec=True), q('V','CB',vec=True)], ['−', '+', '−'], ['+ (⊥CD)', '+ (⊥AB)', '+ (⊥BC)'])}
''', 'r')

# ---------------- page 12 ----------------
p12 = page(12, f'''
{L(f"{num(3)} {fr(q('V','C'), lCD)} = {fr(q('V','E'), lDE)}; &nbsp; {fr('(pc)·'+muv, 'CD·'+mul)} = {fr('(pe)·'+muv, 'DE·'+mul)}")}
{L(f"pe = (pc)·{fr('DE','CD')} &nbsp;(3) &nbsp;[մմ], &nbsp; {fr('DE','CD')} = {fr(n(M.ED,0), n(M.CD,0))} = 1,111", 'ind')}
{L(f"∠cpe = {q('α')} = {n(M.ALPHA,0)}°, &nbsp; c → p → e ({CW}, ինչպես C → D → E)", 'ind sm')}
{L(f"{num(4)} {q('V','F',vec=True)} = {q('V','E',vec=True)} + {q('V','FE',vec=True)} &nbsp;(4)"
   f"<span class='nside'>{q('V','FE',vec=True)} ⊥ EF<br>{q('V','F',vec=True)} ∥ yy</span>")}
{sign([q('V','F',vec=True), q('V','E',vec=True), q('V','FE',vec=True)], ['−', '+', '−'], ['+ (∥yy)', '+', '+ (⊥EF)'])}
{L(f"{num(5)} bs<sub>2</sub> = cs<sub>2</sub>")}
{L(f"{num(6)} {muv} = {fr(q('V','B'), 'pb')} = {fr(w[1]+'·'+lAB, 'pb')} = {fr(n(C.VB,3), '50')} = {big(MUV)} [{fr('մ·վ<sup>−1</sup>', 'մմ')}]; &nbsp; ընդ. <u>pb = 50 մմ</u>")}
<p class="ncap">{num(7)} դիրք {P2} (հաստ դիրքը). մյուս դիրքերը՝ էջ 13-ի աղյուսակում և ներդիրում</p>
{L(f"{q('V','C')} = (pc)·{muv} = {n(v2['pc'])}·{MUV} = {big(n(v2['VC'],3))} [{MS}]", 'ind')}
{L(f"pe = {n(v2['pc'])}·1,111 = {n(v2['pe'])} մմ; &nbsp; {q('V','E')} = (pe)·{muv} = {n(v2['pe'])}·{MUV} = {big(n(v2['VE'],3))} {MS}", 'ind')}
{L(f"{q('V','F')} = (pf)·{muv} = {n(v2['pf'])}·{MUV} = {big(n(v2['VF'],3))} {MS}", 'ind')}
{L(f"{q('V','S<sub>2</sub>')} = (ps<sub>2</sub>)·{muv} = {n(v2['ps2'])}·{MUV} = {big(n(v2['VS2'],3))} {MS}", 'ind')}
{L(f"{q('V','CB')} = (bc)·{muv} = {n(v2['bc'])}·{MUV} = {big(n(v2['VCB'],3))} {MS}", 'ind')}
{L(f"{q('V','FE')} = (ef)·{muv} = {n(v2['ef'])}·{MUV} = {big(n(v2['VFE'],3))} {MS}", 'ind')}
{L(f"{w[2]} = {q('V','CB')}/{lBC} = {n(v2['VCB'],3)}/{LBC} = {big(n(v2['w2'],2))} [{INV1}] {v2['w2s']}", 'ind')}
''')

# ---------------- page 13 ----------------
rows = ''
for i in list(range(8)):
    c = vc[i]
    lab = '0 (8)' if i == 0 else str(i)
    rows += (f'<tr{" class=wk" if i == P2 else ""}><th>{lab}</th>'
             + ''.join(f'<td>{n(c[k],3)}</td>' for k in ('VC', 'VE', 'VF', 'VCB', 'VFE', 'VS2'))
             + ''.join(f'<td>{n(c[k],2)}</td>' for k in ('w2', 'w3', 'w4')) + '</tr>')
p13 = page(13, f'''
{L(f"{w[3]} = {fr(q('V','C'), lCD)} = {fr(n(v2['VC'],3), LCD)} = {big(n(v2['w3'],2))} {INV1} {v2['w3s']}", 'ind')}
{L(f"{w[4]} = {fr(q('V','FE'), lEF)} = {fr(n(v2['VFE'],3), LEF)} = {big(n(v2['w4'],2))} {INV1} {v2['w4s']}", 'ind')}
<table class="ntbl"><thead>
<tr><th rowspan="2"><i>i</i></th><th>{q('V','C')}</th><th>{q('V','E')}</th><th>{q('V','F')}</th><th>{q('V','CB')}</th><th>{q('V','FE')}</th><th>{q('V','S<sub>2</sub>')}</th><th>{w[2]}</th><th>{w[3]}</th><th>{w[4]}</th></tr>
<tr><th colspan="6">մ/վ</th><th colspan="3">{INV1}</th></tr></thead><tbody>{rows}</tbody></table>
<p class="nnote">Ընդգծված տողը՝ հաստ (2-րդ) դիրքը։ Պտտման ուղղությունները (↻ {CW}, ↺ հակառակ). {w[2]}: {" ".join(vc[i]['w2s'] for i in range(8))}; {w[3]}: {" ".join(vc[i]['w3s'] for i in range(8))}; {w[4]}: {" ".join(vc[i]['w4s'] for i in range(8))} (0…7 դիրքեր)։</p>
''', 'r')

# ---------------- insert: step 7 for every position ----------------
def pos_block(i):
    c = vc[i]
    if i == 0:
        return (f'<div class="npos"><h5>Դիրք 0 (8)</h5>'
                f'<p>A, B, C մեկ ուղղի վրա են ⇒ c ≡ p, e ≡ p, f ≡ p</p>'
                f'<p>{q("V","C")} = {q("V","E")} = {q("V","F")} = {q("V","FE")} = 0</p>'
                f'<p>bc = pb = 50 մմ; {q("V","CB")} = 50·{MUV} = {big(n(c["VCB"],3))}</p>'
                f'<p>ps<sub>2</sub> = {n(c["ps2"])}; {q("V","S<sub>2</sub>")} = {big(n(c["VS2"],3))}</p>'
                f'<p>{w[2]} = {n(c["VCB"],3)}/{LBC} = {big(n(c["w2"],2))} {c["w2s"]}; {w[3]} = {w[4]} = 0</p></div>')
    return (f'<div class="npos{" wk" if i == P2 else ""}"><h5>Դիրք {i}</h5>'
            f'<p>pc = {n(c["pc"])} → {q("V","C")} = {big(n(c["VC"],3))}</p>'
            f'<p>pe = {n(c["pc"])}·1,111 = {n(c["pe"])} → {q("V","E")} = {big(n(c["VE"],3))}</p>'
            f'<p>pf = {n(c["pf"])} → {q("V","F")} = {big(n(c["VF"],3))} {c["VFs"]}</p>'
            f'<p>ps<sub>2</sub> = {n(c["ps2"])} → {q("V","S<sub>2</sub>")} = {big(n(c["VS2"],3))}</p>'
            f'<p>bc = {n(c["bc"])} → {q("V","CB")} = {big(n(c["VCB"],3))}</p>'
            f'<p>ef = {n(c["ef"])} → {q("V","FE")} = {big(n(c["VFE"],3))}</p>'
            f'<p>{w[2]} = {n(c["VCB"],3)}/{LBC} = {big(n(c["w2"],2))} {c["w2s"]}</p>'
            f'<p>{w[3]} = {n(c["VC"],3)}/{LCD} = {big(n(c["w3"],2))} {c["w3s"]}</p>'
            f'<p>{w[4]} = {n(c["VFE"],3)}/{LEF} = {big(n(c["w4"],2))} {c["w4s"]}</p></div>')
insert = page('13ա', f'''
<p class="ncap">Ներդիր. 7-րդ կետը բոլոր դիրքերի համար (հատվածները՝ մմ, պլաններից չափված, արագությունները՝ մ/վ, ω-ն՝ {INV1}, {muv} = {MUV})</p>
<div class="nposg">{"".join(pos_block(i) for i in range(8))}</div>
''', 'l wide')

# ---------------- page 14 ----------------
p14 = page(14, f'''
<h4 class="nsec">§3. Արագացումների պլանի կառուցում</h4>
<p class="ntext">Այս կառուցումը կատարում ենք 2-րդ դիրքի համար (աշխատանքային դիրք)։</p>
{L(f"{num(1)} {q('a','B',vec=True)} = {q('a','B','n',True)} + {q('a','B','t',True)}")}
{L(f"{q('a','B','n')} = {w[1]}<sup>2</sup>·{lAB} = {n(C.W1,2)}<sup>2</sup>·{LAB} = {big(n(C.AB_ACC,2))} {MS2}; &nbsp; {q('a','B','n',True)} (B → A)", 'ind')}
{L(f"{q('a','B','t')} = {e[1]}·{lAB} = {fr('d'+w[1], 'dt')}·{lAB} = 0 &nbsp; (քանի որ {w[1]} = const)", 'ind')}
{L(f"{q('a','B',vec=True)} = {q('a','B','n',True)}", 'ind')}
{L(f"{num(2)} {q('a','C',vec=True)} = {q('a','B',vec=True)} + {q('a','CB','n',True)} + {q('a','CB','t',True)} &nbsp;(1)")}
{sign([q('a','C',vec=True), q('a','B',vec=True), q('a','CB','n',True), q('a','CB','t',True)], ['−', '+', '+', '−'], ['−', 'B→A', 'C→B', '⊥BC'])}
{L(f"{q('a','CB','n')} = {w[2]}<sup>2</sup>·{lBC} = {n(v2['w2'],2)}<sup>2</sup>·{LBC} = {big(n(a2['aCBn'],2))} {MS2}", 'ind')}
{L(f"{q('a','C',vec=True)} = {q('a','D',vec=True)} + {q('a','CD','n',True)} + {q('a','CD','t',True)} &nbsp;(2)")}
{sign([q('a','C',vec=True), q('a','D',vec=True), q('a','CD','n',True), q('a','CD','t',True)], ['−', '0', '+', '−'], ['−', '(−)', 'C→D', '⊥CD'])}
{L(f"{q('a','CD','n')} = {w[3]}<sup>2</sup>·{lCD} = {n(v2['w3'],2)}<sup>2</sup>·{LCD} = {big(n(a2['aCDn'],2))} {MS2}", 'ind')}
''')

# ---------------- page 15 ----------------
p15 = page(15, f'''
{L(f"{q('a','B',vec=True)} + {q('a','CB','n',True)} + {q('a','CB','t',True)} = {q('a','CD','n',True)} + {q('a','CD','t',True)} &nbsp;(3)")}
{L(f"{num(3)} {mua} = {fr(q('a','B'), 'πb')} = {fr(q('a','B','n'), 'πb')} = {fr(n(C.AB_ACC,2), '70')} = {big(MUA)} [{fr('մ·վ<sup>−2</sup>', 'մմ')}]; &nbsp; ընդ. <u>πb = 70 մմ</u>")}
{L(f"bn<sub>2</sub> = {fr(q('a','CB','n'), mua)} = {fr(n(a2['aCBn'],2), MUA)} = {big(n(a2['bn2']))} [մմ]", 'ind')}
{L(f"πn<sub>3</sub> = {fr(q('a','CD','n'), mua)} = {fr(n(a2['aCDn'],2), MUA)} = {big(n(a2['pin3']))} [մմ]", 'ind')}
{L(f"{num(4)} {fr(q('a','C'), lCD)} = {fr(q('a','E'), lDE)}; &nbsp; {fr('πc', 'CD')} = {fr('πe', 'DE')} ⇒")}
{L(f"πe = (πc)·{fr('DE','CD')} = {n(a2['pic'])}·1,111 = {big(n(a2['pie']))} մմ &nbsp;(4)", 'ind')}
{L(f"{num(5)} ∠cπe = {q('α')} = {n(M.ALPHA,0)}° &nbsp; (c → π → e, {CW})")}
{L(f"{num(6)} {q('a','F',vec=True)} = {q('a','E',vec=True)} + {q('a','FE','n',True)} + {q('a','FE','t',True)}")}
{sign([q('a','F',vec=True), q('a','E',vec=True), q('a','FE','n',True), q('a','FE','t',True)], ['−', '+', '+', '−'], ['∥yy', '+', 'F→E', '⊥EF'])}
{L(f"{q('a','FE','n')} = {w[4]}<sup>2</sup>·{lEF} = {n(v2['w4'],2)}<sup>2</sup>·{LEF} = {big(n(a2['aFEn'],2))} {MS2}", 'ind')}
{L(f"en<sub>4</sub> = {fr(q('a','FE','n'), mua)} = {fr(n(a2['aFEn'],2), MUA)} = {big(n(a2['en4']))} [մմ]", 'ind')}
''', 'r')

# ---------------- page 16 ----------------
p16 = page(16, f'''
{L(f"{q('a','C')} = (πc)·{mua} = {n(a2['pic'])}·{MUA} = {big(n(a2['aC'],2))} {MS2}")}
{L(f"{q('a','E')} = (πe)·{mua} = {n(a2['pie'])}·{MUA} = {big(n(a2['aE'],2))} {MS2}")}
{L(f"{q('a','F')} = (πf)·{mua} = {n(a2['pif'])}·{MUA} = {big(n(a2['aF'],2))} {MS2} {a2['aFs']}")}
{L(f"{q('a','CB','t')} = (n<sub>2</sub>c)·{mua} = {n(a2['n2c'])}·{MUA} = {big(n(a2['aCBt'],2))} {MS2}")}
{L(f"{q('a','CD','t')} = (n<sub>3</sub>c)·{mua} = {n(a2['n3c'])}·{MUA} = {big(n(a2['aCDt'],2))} {MS2}")}
{L(f"{q('a','FE','t')} = (n<sub>4</sub>f)·{mua} = {n(a2['n4f'])}·{MUA} = {big(n(a2['aFEt'],2))} {MS2}")}
{L(f"{q('a','S<sub>2</sub>')} = (πs<sub>2</sub>)·{mua} = {n(a2['pis2'])}·{MUA} = {big(n(a2['aS2'],2))} {MS2}", 'opt')}
{L(f"{e[2]} = {fr(q('a','CB','t'), lBC)} = {fr(n(a2['aCBt'],2), LBC)} = {big(n(a2['e2'],1))} {INV2} {a2['e2s']}; &nbsp; {e[3]} = {fr(q('a','CD','t'), lCD)} = {fr(n(a2['aCDt'],2), LCD)} = {big(n(a2['e3'],1))} {INV2}")}
{L(f"{e[4]} = {fr(q('a','FE','t'), lEF)} = {fr(n(a2['aFEt'],2), LEF)} = {big(n(a2['e4'],1))} {INV2} {a2['e4s']}")}
<p class="nnote">{q('a','S<sub>2</sub>')}-ի տողը օրինակում չկա, բայց պետք կգա ուժային հաշվարկում (իներցիայի ուժ)։ n<sub>3</sub>c-ն և n<sub>4</sub>f-ը գրեթե զրո են, որովհետև 2-րդ դիրքում {w[3]}-ը մոտ է իր առավելագույնին. սա սխալ չէ։</p>
''')

SECTION = f'''
<section class="wide-sec sec" id="copybook">
  <div class="wrap">
    <h2>Տետրը (էջ 10–16)</h2>
    <div class="prose">
      <p>Ձեր տետրի էջերը՝ լրացված այս տարբերակի թվերով։ Կառուցվածքը, համարակալումը և նշանակումները նույնն են, ինչ լուսանկարներում. «…»-ի տեղում թվերն են։ Թավով գրվածը վերջնական արդյունքն է։ <b>13ա</b> ներդիրը ցույց է տալիս 7-րդ կետը բոլոր 8 դիրքերի համար. էջ 13-ի աղյուսակը լրացվում է դրանից։</p>
      <p class="note">Հատվածները (pc, bc, pf, …) չափված են A3 թերթի պլաններից. ձեր չափումները կարող են տարբերվել ±0,5 մմ-ով, դա նորմալ է. այդ դեպքում արագությունը վերահաշվեք նույն բանաձևով։ pe-ն և πe-ն չեն չափվում, հաշվվում են (3) և (4) բանաձևերով։</p>
    </div>
  </div>
  <div class="nbook">{p10}{p11}{p12}{p13}{insert}{p14}{p15}{p16}</div>
</section>'''

SECTION = SECTION.replace('↻', '<span class="rot">↻</span>').replace('↺', '<span class="rot">↺</span>')

CSS = r'''
.nbook{max-width:1240px;margin:22px auto 0;padding-inline:20px;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,540px),1fr));gap:22px;align-items:start}
.npage{position:relative;background-color:#FBFAF3;background-image:linear-gradient(#C9CCE6 1px,transparent 1px),linear-gradient(90deg,#C9CCE6 1px,transparent 1px);background-size:20px 20px;background-position:-1px -1px;
  color:#22388A;font-family:var(--f-math);font-size:17px;line-height:1.5;padding:46px 30px 34px 62px;box-shadow:0 1px 2px rgba(0,0,0,.12),0 6px 18px rgba(0,0,0,.08);border-radius:2px 6px 6px 2px;min-height:560px;overflow-x:auto}
.npage::before{content:"";position:absolute;top:0;bottom:0;left:46px;width:1.5px;background:#E07B7B}
.npage.r{padding:46px 62px 34px 30px;border-radius:6px 2px 2px 6px}
.npage.r::before{left:auto;right:46px}
.npage.wide{grid-column:1/-1}
.npno{position:absolute;top:12px;left:12px;width:30px;height:30px;border:1.5px solid currentColor;border-radius:50%;display:grid;place-items:center;font-size:13px;font-weight:600}
.npage.r .npno{left:auto;right:12px}
.npage sub,.npage sup{font-size:.68em}
.nbox{border:1.5px solid currentColor;padding:4px 14px;text-align:center;font-family:var(--f-sans);font-size:1.15rem;margin:0 auto 12px;width:max-content;max-width:100%}
.nvar{font-size:.8rem;opacity:.75}
.ndata{border-collapse:collapse;margin:0 0 12px;font-size:.92rem;background:rgba(251,250,243,.7)}
.ndata th,.ndata td{border:1.3px solid currentColor;padding:2px 7px;text-align:center;font-weight:400;white-space:nowrap}
.ndata tr.v td{font-weight:600}
.ncond{margin:0 0 6px;padding-left:1.6em;display:grid;gap:1px}
.nrule{border:0;border-top:1.3px solid currentColor;margin:12px -10px}
.nsec{font-family:var(--f-sans);font-size:1.02rem;font-weight:600;text-align:center;margin:4px 0 10px;color:#22388A}
.nl{padding:4px 0;min-height:40px;line-height:2.05}.nl::after{content:"";display:block;clear:both}
.nl.ind{padding-left:1.6em}
.nl.sm{font-size:.9rem;min-height:30px}
.nl.opt{opacity:.8}
.nn{display:inline-block;min-width:1.6em;font-weight:600}
.nr{font-weight:700;color:#14246B;text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px}
.nf{display:inline-flex;flex-direction:column;vertical-align:middle;text-align:center;line-height:1.2;margin:0 .1em}
.nf>span{padding:0 .2em}.nf>span:last-child{border-top:1.2px solid currentColor}
.ov{text-decoration:overline;text-decoration-thickness:1.2px}
.nsys{display:inline-flex;align-items:center;gap:4px;vertical-align:middle;margin-right:10px}
.nbr{display:inline-flex;flex-direction:column;border-left:1.5px solid currentColor;border-radius:8px 0 0 8px;padding-left:.45em;line-height:1.4}
.nbr.p{border-right:1.5px solid currentColor;border-radius:8px;padding-right:.45em}
.nside{float:right;margin-left:14px;font-size:.95rem;line-height:1.45;text-align:left}
.nsign{border-collapse:collapse;margin:2px 0 8px 1.6em;font-size:.92rem}
.nsign th,.nsign td{border:1.3px solid currentColor;padding:1px 12px;text-align:center;font-weight:400;white-space:nowrap}
.nsign thead th:first-child{border-top-color:transparent;border-left-color:transparent}
.nsign tbody th{font-family:var(--f-sans);font-size:.8rem}
.ncap{font-family:var(--f-sans);font-size:.85rem;margin:8px 0 2px}
.ntext{font-family:var(--f-sans);font-size:.95rem;margin:0 0 6px}
.rot{font-family:system-ui,-apple-system,"Segoe UI Symbol",sans-serif;font-size:.95em}
.nnote{font-family:var(--f-sans);font-size:.8rem;margin:10px 0 0;opacity:.85}
.ntbl{border-collapse:collapse;margin:14px 0 0;font-size:.9rem;background:rgba(251,250,243,.7)}
.ntbl th,.ntbl td{border:1.3px solid currentColor;padding:3px 8px;text-align:center;white-space:nowrap;font-weight:400}
.ntbl tbody th{font-weight:600}
.ntbl tr.wk td,.ntbl tr.wk th{background:rgba(243,222,91,.35);font-weight:700}
.nposg{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:4px 22px}
.npos{padding:4px 0 8px}
.npos h5{font-family:var(--f-sans);font-size:.92rem;margin:0 0 2px;font-weight:650}
.npos p{margin:0;font-size:.95rem;line-height:1.55}
.npos.wk h5{background:rgba(243,222,91,.45);display:inline-block;padding:0 6px}
@media (max-width:600px){.npage,.npage.r{padding:44px 14px 24px 40px;font-size:15px}.npage::before{left:30px}.npage.r::before{left:30px;right:auto}.npage.r .npno{left:6px;right:auto}.npno{left:6px}.nside{float:none;display:block;margin:2px 0 0 1.6em}}
'''
