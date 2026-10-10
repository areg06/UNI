import math
import model as M
import sheet as SH
import calc as C
import notebook as NB
from calc import n, r
from model import S, sub, add, mag, scl

# ---------------- html helpers ----------------
def v(sym, sub_=None, sup=None, vec=False, up=False):
    b = sym if up else f'<i>{sym}</i>'
    if vec: b = f'<span class="vec">{b}</span>'
    if sub_: b += f'<sub>{sub_}</sub>'
    if sup: b += f'<sup>{sup}</sup>'
    return b
def fr(a, b): return f'<span class="frac"><span>{a}</span><span>{b}</span></span>'
class Eq:
    k = 0
    @classmethod
    def __call__(cls, body, note=''):
        cls.k += 1
        nt = f'<span class="eq-note">{note}</span>' if note else ''
        return f'<div class="eq"><div class="eq-b">{body}{nt}</div><div class="eq-n">({cls.k})</div></div>'
eq = Eq()
def res(x): return f'<b class="res">{x}</b>'

mu_l = v('μ', 'l'); mu_V = v('μ', 'V'); mu_a = v('μ', 'a'); mu_F = v('μ', 'F')
VB, VC, VCB, VE, VFE, VF, VS2 = (v('V', s) for s in ('B', 'C', 'CB', 'E', 'FE', 'F', 'S₂'))
vVB, vVC, vVCB, vVE, vVFE, vVF, vVD, vVCD = (v('V', s, vec=True) for s in ('B', 'C', 'CB', 'E', 'FE', 'F', 'D', 'CD'))
w1, w2, w3, w4 = (v('ω', s) for s in '1234')
e2, e3, e4 = (v('ε', s) for s in '234')
lAB, lBC, lCD, lEF, lED, lBS2 = (v('l', s) for s in ('AB', 'BC', 'CD', 'EF', 'ED', 'BS₂'))
def a_(s, sup=None, vec=False): return v('a', s, sup, vec)

P2 = M.PA_POS
VAR = M.VARIANT; D_ = M.DATA
MUT = n(M.MU, 5)                       # μ_l as written in the notebook
MUVT = n(M.MUV, 5); MUAT = n(M.MUA, 4)  # μ_V, μ_a as written in the notebook
def si(mm): return n(mm/1000, 3)        # mm -> m, e.g. 0,210
LCDT = n(M.lCD, 3)
WK = ' class="wkrow"'
vc2 = C.vchain(2); ac2 = C.achain(2)

# ---------------- sheet svg ----------------
sheet_svg = SH.build('sh')
sheet2_svg = SH.build2('sh2')
syn_svg = SH.build('syn', only={'grid', 'constr', 'synonly', 'base', 'xlabels', 'dims'}, viewbox='4 2 336 264',
                   title_attr='Եզրային դիրքերի կառուցումը')

def pt_sheet(p): return f'<td class="n">{n(p[0])}</td><td class="n">{n(p[1])}</td>'

# key points table
Dp, Ap = S(M.D), S(M.A)
key_rows = [
    ('D', Dp, 'D', 'լծակի անշարժ հոդ, ուղղորդն անցնում է D-ով'),
    ('A', Ap, 'A', f'կռունկի անշարժ հոդ (D-ից {n(M.L1S,0)} մմ աջ, {n(M.L2S)} մմ ցածր)'),
    ('E₀′', S(M.E0p), 'E0p', 'E-ի ստորին եզրային դիրք (β = 3° ուղղաձիգից)'),
    ('F₀′', S(M.F0p), 'F0p', 'սողնակի ստորին եզրային դիրք'),
    ('F₀', S(M.F0), 'F0', f'սողնակի վերին եզրային դիրք (F₀′-ից {n(M.H)} մմ վեր)'),
    ('E₀', S(M.E0), 'E0', 'E-ի վերին եզրային դիրք'),
    ('C₀', S(M.C0), 'C0', 'C-ի եզրային դիրք (ձգված)'),
    ('C₀′', S(M.C0p), 'C0p', 'C-ի եզրային դիրք (ծալված)'),
    ('B₀', S(M.B0), 'B0', 'A–B₀–C₀ մեկ ուղղի վրա, 0-րդ դիրք'),
    ('B₀′', S(M.B0p), 'B0p', 'C₀′–A–B₀′ մեկ ուղղի վրա'),
]
key_tbl = ''.join(f'<tr data-pt="{k}"><th scope="row">{lab}</th>{pt_sheet(p)}<td class="t">{note}</td></tr>' for lab, p, k, note in key_rows)

pos_tbl = ''
for i, q in enumerate(M.POS):
    Bq, Cq, Eq_, Fq, S2q = S(q['B']), S(q['C']), S(q['E']), S(q['F']), S(q['S2'])
    stroke = 'աշխ.' if 1 <= i <= 4 else ('պարապ' if i >= 5 else 'եզր.')
    pos_tbl += (f'<tr data-pt="B{i} C{i} E{i} F{i}"{WK if i == P2 else ""}><th scope="row">{i}</th>'
                f'<td class="n">{45*i}°</td>{pt_sheet(Bq)}{pt_sheet(Cq)}{pt_sheet(Eq_)}<td class="n">{n(Fq[1])}</td>'
                f'{pt_sheet(S2q)}<td class="t">{stroke}</td></tr>')

# plan tables (absolute coordinates on the sheet)
def vplan_tbl(i):
    vv = M.vplan(i); pole = M.PV2[i]; ch = C.vchain(i)
    names = [('p', 'p (a, d)', None, None), ('b', 'b', ch['pb'], ('V_B', C.VB)), ('c', 'c', ch['pc'], ('V_C', ch['VC'])),
             ('e', 'e', ch['pe'], ('V_E', ch['VE'])), ('f', 'f', ch['pf'], ('V_F', ch['VF'])), ('s2', 's₂', ch['ps2'], ('V_S₂', ch['VS2']))]
    rows = ''
    for k, lab, ln, val in names:
        p = add(pole, vv[k])
        if i == 0 and k in ('c', 'e', 'f'):
            rows += f'<tr data-pt="v{i}p"><th scope="row">{lab}</th><td class="n" colspan="2">≡ p</td><td class="n">0</td><td class="n">0</td></tr>'
            continue
        lv = '—' if ln is None else n(ln)
        vl = '—' if val is None else n(val[1], 3)
        rows += f'<tr data-pt="v{i}{k}"><th scope="row">{lab}</th>{pt_sheet(p)}<td class="n">{lv}</td><td class="n">{vl}</td></tr>'
    return rows
def aplan_tbl():
    aa = M.aplan(P2); pole = M.PA; ch = ac2
    names = [('pi', 'π (a, d)', None, None), ('b', 'b', ch['pib'], C.AB_ACC), ('n2', 'n₂', ch['bn2'], ch['aCBn']),
             ('c', 'c', ch['pic'], ch['aC']), ('n3', 'n₃', ch['pin3'], ch['aCDn']), ('e', 'e', ch['pie'], ch['aE']),
             ('n4', 'n₄', ch['en4'], ch['aFEn']), ('f', 'f', ch['pif'], ch['aF']), ('s2', 's₂', ch['pis2'], ch['aS2'])]
    seg = dict(b='πb', n2='bn₂', c='πc', n3='πn₃', e='πe', n4='en₄', f='πf', s2='πs₂')
    rows = ''
    for k, lab, ln, val in names:
        p = add(pole, aa[k])
        lv = '—' if ln is None else f'{seg[k]} = {n(ln)}'
        vl = '—' if val is None else n(val, 2)
        rows += f'<tr data-pt="a2{k}"><th scope="row">{lab}</th>{pt_sheet(p)}<td class="n">{lv}</td><td class="n">{vl}</td></tr>'
    return rows

# F_re diagram table
wF = M.FMAX/M.MUF
fre_rows = ''
for i, q in enumerate(M.POS):
    s = q['sF']/M.H; work = 1 <= i <= 4
    f = M.fre_shape(s) if work else 0.0
    Fq = S(q['F']); xe = M.DIAG_X + wF*f
    kind = 'աշխատանքային' if work else ('եզրային (F₀)' if i == 0 else 'պարապ')
    fre_rows += (f'<tr{WK if i == P2 else ""}><th scope="row">{i}</th><td class="t">{kind}</td><td class="n">{n(q["sF"])}</td>'
                 f'<td class="n">{n(q["sF"]*M.MU, 4)}</td><td class="n">{n(s, 2)}</td>'
                 f'<td class="n">{"≈ " + format(int(round(M.FMAX*f, -1)), ",").replace(",", " ") if f > 0 else "0"}</td>'
                 f'<td class="n">{n(wF*f)}</td><td class="n">{n(xe)}</td><td class="n">{n(Fq[1])}</td></tr>')

# all-positions tables
vel_rows = ''
for i in range(8):
    c = C.vchain(i)
    vel_rows += (f'<tr{WK if i == P2 else ""}><th scope="row">{i}</th><td class="n">{45*i}°</td>'
                 f'<td class="n">{n(c["pc"])}</td><td class="n">{n(c["VC"],3)}</td>'
                 f'<td class="n">{n(c["bc"])}</td><td class="n">{n(c["VCB"],3)}</td>'
                 f'<td class="n">{n(c["pe"])}</td><td class="n">{n(c["VE"],3)}</td>'
                 f'<td class="n">{n(c["ef"])}</td><td class="n">{n(c["VFE"],3)}</td>'
                 f'<td class="n">{n(c["pf"])}</td><td class="n">{n(c["VF"],3)} {c["VFs"]}</td>'
                 f'<td class="n">{n(c["ps2"])}</td><td class="n">{n(c["VS2"],3)}</td>'
                 f'<td class="n">{n(c["w2"],2)} {c["w2s"]}</td><td class="n">{n(c["w3"],2)} {c["w3s"]}</td><td class="n">{n(c["w4"],2)} {c["w4s"]}</td></tr>')
acc_rows = ''
for i in range(8):
    c = C.achain(i)
    acc_rows += (f'<tr{WK if i == P2 else ""}><th scope="row">{i}</th>'
                 f'<td class="n">{n(c["aCBn"],2)}</td><td class="n">{n(c["aCBt"],2)}</td><td class="n">{n(c["aCDn"],2)}</td>'
                 f'<td class="n">{n(c["aCDt"],2)}</td><td class="n">{n(c["aC"],2)}</td><td class="n">{n(c["aE"],2)}</td>'
                 f'<td class="n">{n(c["aFEn"],2)}</td><td class="n">{n(c["aFEt"],2)}</td><td class="n">{n(c["aF"],2)} {c["aFs"]}</td>'
                 f'<td class="n">{n(c["aS2"],2)}</td><td class="n">{n(c["e2"],1)} {c["e2s"]}</td><td class="n">{n(c["e3"],1)} {c["e3s"]}</td>'
                 f'<td class="n">{n(c["e4"],1)} {c["e4s"]}</td></tr>')
rel_v = ''
for i in range(8):
    vv = M.vplan(i)
    rel_v += f'<tr><th scope="row">{i}</th>' + ''.join(f'<td class="n">{n(vv[k][0])}; {n(vv[k][1])}</td>' for k in ('b', 'c', 'e', 'f', 's2')) + '</tr>'
rel_a = ''
for i in range(8):
    aa = M.aplan(i)
    rel_a += f'<tr><th scope="row">{i}</th>' + ''.join(f'<td class="n">{n(aa[k][0])}; {n(aa[k][1])}</td>' for k in ('b', 'n2', 'c', 'n3', 'e', 'n4', 'f', 's2')) + '</tr>'

# ---------------- numbers used in text ----------------
E0s, E0ps, F0s, F0ps, C0s, C0ps = S(M.E0), S(M.E0p), S(M.F0), S(M.F0p), S(M.C0), S(M.C0p)
S2w = S(M.POS[P2]['S2'])
AD = M.AD
grash_l = C.LAB + AD; grash_r = C.LBC + M.lCD
om3_1, om3_2, om3_3 = C.vchain(1)['w3'], C.vchain(2)['w3'], C.vchain(3)['w3']

def ptxt(p): return f'({n(p[0])}; {n(p[1])})'

# ---------------- sections ----------------
header = f'''
<header class="wrap hdr">
  <div class="stamp">
    <div class="stamp-main">
      <p class="eyebrow">Մեխանիզմների և մեքենաների տեսություն</p>
      <h1>Վեցօղակ լծակավոր մեխանիզմի կինեմատիկան</h1>
      <p class="lede">Ձեր տարբերակի ամբողջական լուծումը՝ թվերը, տետրի §1–§3 բաժինների բանաձևերը՝ բացատրություններով, և A3 միլիմետրական թերթի գծագիրը՝ յուրաքանչյուր կետի x, y կոորդինատներով։ Կառուցման մեթոդը նույնն է, ինչ օրինակի թերթում։</p>
    </div>
    <dl class="stamp-cells">
      <div><dt>Առաջադրանք</dt><dd>N2</dd></div>
      <div><dt>Տարբերակ</dt><dd><mark>{VAR}</mark></dd></div>
      <div><dt>Թերթ</dt><dd>A3, միլիմետրական</dd></div>
      <div><dt>Մասշտաբ</dt><dd>{mu_l} = {MUT} մ/մմ</dd></div>
    </dl>
  </div>
  <nav class="toc" aria-label="Բովանդակություն">
    <a href="#data">Տվյալներ</a><a href="#results">Արդյունքներ</a><a href="#sheet">A3 թերթ</a><a href="#copybook">Տետր</a><a href="bacatrutyun.html">Բացատրություն ↗</a><a href="#s1">§1 Սինթեզ</a><a href="#s2">§2 Արագություններ</a><a href="#s3">§3 Արագացումներ</a><a href="#fre">F<sub>re</sub> գրաֆիկ</a><a href="#tables">Աղյուսակներ</a>
  </nav>
</header>'''

data_sec = f'''
<section class="wrap sec" id="data">
  <h2>Տվյալներ</h2>
  <div class="grid2">
    <div class="prose">
      <p>Մեխանիզմը վեցօղակ է. <b>ABCD</b> կռունկա-ճոճաթևային քառօղակին միացված է <b>DEF</b> խումբը, որը լծակի ճոճումը վերածում է սողնակի ուղղաձիգ շարժման։</p>
      <ul class="links">
        <li><span class="ln">1</span><span><b>AB</b>՝ կռունկ, պտտվում է A-ի շուրջը <i>n</i><sub>1</sub> = {D_['n1']} պտ/րոպ, ժամացույցի սլաքի ուղղությամբ (↻)</span></li>
        <li><span class="ln">2</span><span><b>BC</b>՝ շարժաթև, ծանրության կենտրոնը՝ S<sub>2</sub></span></li>
        <li><span class="ln">3</span><span><b>CDE</b>՝ լծակ (ճոճաթև). կոշտ եռանկյուն, ճոճվում է D-ի շուրջը, ∠CDE = α = 50°</span></li>
        <li><span class="ln">4</span><span><b>EF</b>՝ շարժաթև</span></li>
        <li><span class="ln">5</span><span><b>F</b>՝ սողնակ, շարժվում է D-ով անցնող ուղղաձիգ ուղղորդով</span></li>
        <li><span class="ln">0</span><span>անշարժ օղակ՝ A, D հոդերը և ուղղորդը</span></li>
      </ul>
    </div>
    <div class="prose">
      <h3>Լրացուցիչ պայմաններ</h3>
      <ol class="conds">
        <li>{lCD} = 0,9·{lED} = 0,9·{si(D_['lED'])} = <b>{LCDT} մ</b>. CD լծակի երկարությունը</li>
        <li>{lBS2} = 0,5·{lBC}. 2 օղակի զանգվածի կենտրոնը</li>
        <li><i>M</i><sub>m</sub> = const. շարժիչ ուժերի մոմենտը</li>
        <li><i>δ</i> = 0,05. շարժման անհավասարաչափության գործակիցը</li>
        <li><i>β</i> = 3°÷5°. ընդունում ենք <b>β = 3°</b></li>
        <li><i>α</i> = 50°. ∠CDE (նկարից)</li>
      </ol>
    </div>
  </div>
  <div class="tscroll">
    <table class="task">
      <caption>Աղյուսակի {VAR}-ին տող</caption>
      <thead>
        <tr><th scope="col">Նշանակում</th><th scope="col"><i>H</i><sub>F</sub></th><th scope="col"><i>L</i><sub>1</sub></th><th scope="col"><i>L</i><sub>2</sub></th><th scope="col"><i>l</i><sub>EF</sub></th><th scope="col"><i>l</i><sub>ED</sub></th><th scope="col"><i>n</i><sub>1</sub></th><th scope="col"><i>G</i><sub>2</sub></th><th scope="col"><i>G</i><sub>5</sub></th><th scope="col"><i>I</i><sub>S₂</sub></th><th scope="col"><i>F</i><sub>re</sub><sup>max</sup></th></tr>
      </thead>
      <tbody>
        <tr class="unit"><th scope="row">Միավոր</th><td>մմ</td><td>մմ</td><td>մմ</td><td>մմ</td><td>մմ</td><td>պտ/րոպ</td><td>Ն</td><td>Ն</td><td>10⁻³ կգ·մ²</td><td>10² Ն</td></tr>
        <tr class="val"><th scope="row"><mark>{VAR}</mark></th>{''.join(f'<td>{D_[k]}</td>' for k in ('HF','L1','L2','lEF','lED','n1','G2','G5','IS2','Fmax'))}</tr>
        <tr class="si"><th scope="row">SI</th>{''.join(f'<td>{si(D_[k])} մ</td>' for k in ('HF','L1','L2','lEF','lED'))}<td>{D_['n1']} պտ/րոպ</td><td>{D_['G2']} Ն</td><td>{D_['G5']} Ն</td><td>{n(D_['IS2']/1000,2)} կգ·մ²</td><td>{D_['Fmax']*100} Ն</td></tr>
      </tbody>
    </table>
  </div>
  <p class="note">Այս թերթի (կինեմատիկայի) համար պետք են <i>H</i><sub>F</sub>, <i>L</i><sub>1</sub>, <i>L</i><sub>2</sub>, {lEF}, {lED}, {lCD}, <i>n</i><sub>1</sub>, <i>α</i>, <i>β</i> և F<sub>re</sub> գրաֆիկի ձևը։ <i>G</i><sub>2</sub>, <i>G</i><sub>5</sub>, <i>I</i><sub>S₂</sub>, <i>M</i><sub>m</sub>, <i>δ</i> մեծությունները պետք են հաջորդ բաժիններում (ուժային հաշվարկ, թափանիվ)։ <i>I</i><sub>S₂</sub>-ի միավորի աստիճանը լուսանկարում վատ է երևում (10⁻³ կամ 10⁻¹). ստուգեք ձեր թերթում, երբ հասնեք ուժային հաշվարկին։</p>
</section>'''

# ---------------- step-by-step derivation of the key results ----------------
def qe(body, note=''):
    """unnumbered equation line (the numbered ones belong to §1–§3)"""
    nt = f'<span class="eq-note">{note}</span>' if note else ''
    return f'<div class="eq"><div class="eq-b">{body}{nt}</div><div class="eq-n"></div></div>'
def step(title, result, why, body, where=''):
    wh = f'<p class="where"><b>Գծագրում՝</b> {where}</p>' if where else ''
    return (f'<li class="cstep"><div class="cstep-h"><h3>{title}</h3><p class="cstep-r">{result}</p></div>'
            f'<p class="why">{why}</p>{body}{wh}</li>')
psi_e0 = r(-M.ang(M.E0)-90, 1)                 # DE₀ from the vertical, deg
ac0_dx, ac0_dy = r(Ap[0]-C0s[0]), r(Ap[1]-C0s[1]); ac0p_dx, ac0p_dy = r(Ap[0]-C0ps[0]), r(Ap[1]-C0ps[1])
b0_dn, b0p_dn = r(180+M.TH0, 1), r(-M.TH0P, 1)  # B₀ / B₀′ below the horizontal through A, deg
W1SQ = r(C.W1**2, 2)
psi_sub = (f'<ol class="sub">'
           f'<li><b>Ստորին դիրք.</b> DE-ն ուղղաձիգից շեղում ենք β = {n(M.BETA,0)}° → E₀′{ptxt(E0ps)}։ E₀′-ից EF* = {n(M.EF)} մմ շառավղով աղեղը հատում է ուղղորդը F₀′{ptxt(F0ps)} կետում։</li>'
           f'<li><b>Վերին դիրք.</b> F₀′-ից բարձրանում ենք H<sub>F</sub>* = {n(M.H)} մմ → F₀{ptxt(F0s)}։ F₀-ից {n(M.EF)} մմ աղեղը հատում է E-ի հետագիծը (D կենտրոնով, R = {n(M.ED)} մմ շրջանագիծը) E₀{ptxt(E0s)} կետում։</li>'
           f'<li><b>Անկյունը.</b> DE₀-ն ուղղաձիգից շեղված է {n(psi_e0)}°, DE₀′-ը՝ {n(M.BETA,0)}°։</li></ol>')
calc_steps = [
    step('1. Երկարությունների մասշտաբը', f'{mu_l} = {MUT} մ/մմ',
         f'Իրական մեխանիզմը թղթի վրա չի տեղավորվի, ուստի այն գծում ենք փոքրացված։ <i>L</i><sub>1</sub> = {si(D_["L1"])} մ հեռավորությունը գծում ենք {n(M.L1S,0)} մմ. {mu_l}-ն ցույց է տալիս, թե գծագրի 1 մմ-ը քանի մետր է իրականում։',
         qe(f"{mu_l} = {fr('իրական երկարություն', 'գծագրային երկարություն')} = {fr(v('L','1'), v('L','1')+'*')} = {fr(si(D_['L1'])+' մ', n(M.L1S,0)+' մմ')} = {res(MUT+' մ/մմ')}")
         + f'<p>Հակառակը՝ ցանկացած իրական երկարություն գծագրային դարձնելու համար այն բաժանում ենք {mu_l}-ի. օր.՝ ED* = {si(D_["lED"])} / {MUT} = {n(M.ED)} մմ։</p>'),
    step('2. Լծակի ճոճման անկյունը', f'<i>ψ</i> = {n(M.PSI)}°',
         'CDE լծակը ճոճվում է երկու եզրային դիրքերի միջև։ Այդ դիրքերը որոշվում են սողնակի ամենացածր (F₀′) և ամենաբարձր (F₀) դիրքերով։ ψ-ն այդ երկու դիրքերում DE-ի միջև եղած անկյունն է։',
         psi_sub + qe(f"<i>ψ</i> = ∠E₀DE₀′ = {n(psi_e0)}° − {n(M.BETA,0)}° = {res(n(M.PSI)+'°')}"),
         'անկյունաչափով չափեք E₀DE₀′ անկյունը։'),
    step('3. Կռունկ AB և շարժաթև BC', f'AB* = {n(C.AB,2)} մմ, BC* = {n(C.BC,2)} մմ',
         'Լծակի եզրային դիրքերում կռունկը և շարժաթևը մեկ ուղղի վրա են։ Ձգված դիրքում դրանք գումարվում են (A—B—C), ծալված դիրքում՝ իրար վրա են ծալվում (B—A—C)։ Այսպիսով A-ից մինչև C₀ և C₀′ երկու հեռավորությունը տալիս են երկու հավասարում՝ երկու անհայտով։',
         f'<p>C₀-ն և C₀′-ը ստանում ենք DE₀-ն և DE₀′-ը {n(M.ALPHA,0)}°-ով պտտելով (լծակը կոշտ է), DC* = {n(M.CD)} մմ. C₀{ptxt(C0s)}, C₀′{ptxt(C0ps)}, A{ptxt(Ap)}։</p>'
         + qe(f"AC₀ = √({n(ac0_dx)}² + {n(ac0_dy)}²) = {n(C.AC0)} մմ,&nbsp;&nbsp; AC₀′ = √({n(ac0p_dx)}² + {n(ac0p_dy)}²) = {n(C.AC0P)} մմ", 'կամ չափեք քանոնով')
         + qe(f'<span class="sys"><span>AB + BC = {n(C.AC0)}</span><span>BC − AB = {n(C.AC0P)}</span></span>&nbsp; ⇒ &nbsp;BC = {fr(n(C.AC0)+" + "+n(C.AC0P), "2")} = {res(n(C.BC,2)+" մմ")},&nbsp;&nbsp; AB = {n(C.AC0)} − {n(C.BC,2)} = {res(n(C.AB,2)+" մմ")}')
         + '<p>Իրական երկարությունները ստանալու համար գծագրայինը բազմապատկում ենք մասշտաբով.</p>'
         + qe(f"{lAB} = {n(C.AB,2)}·{MUT} = {res(n(C.LAB,4)+' մ')},&nbsp;&nbsp; {lBC} = {n(C.BC,2)}·{MUT} = {res(n(C.LBC,4)+' մ')}")),
    step('4. Կռունկի անկյունային արագությունը', f'{w1} = {n(C.W1,2)} ռադ/վ',
         f'<i>n</i><sub>1</sub>-ը տրված է պտույտ/րոպե-ով, իսկ հաշվարկի համար պետք է ռադ/վ։ Մեկ պտույտը 2π ռադ է, մեկ րոպեն՝ 60 վ. հետևաբար {w1} = 2π<i>n</i><sub>1</sub>/60 = π<i>n</i><sub>1</sub>/30։',
         qe(f"{w1} = {fr('π·'+v('n','1'), '30')} = {fr('3,1416·'+str(D_['n1']), '30')} = {res(n(C.W1,2)+' ռադ/վ')}")),
    step('5. B կետի արագությունը և արագությունների մասշտաբը', f'{VB} = {n(C.VB,3)} մ/վ, pb = {n(C.PB)} մմ',
         'B կետը պտտվում է A-ի շուրջը AB շառավղով, ուստի նրա արագությունը հավասար է անկյունային արագության և շառավղի արտադրյալին։ Այն ուղղահայաց է AB-ին և ուղղված է պտույտի կողմը (↻)։ Կռունկը պտտվում է հավասարաչափ, ուստի V<sub>B</sub>-ն բոլոր դիրքերում նույնն է։',
         qe(f"{VB} = {w1}·{lAB} = {n(C.W1,2)}·{n(C.LAB,4)} = {res(n(C.VB,3)+' մ/վ')}")
         + f'<p>Արագությունների պլանում V<sub>B</sub>-ն պատկերում ենք pb հատվածով։ Տետրի օրինակի պես ընդունում ենք <b>pb = 50 մմ</b>, որից էլ ստացվում է մասշտաբը.</p>'
         + qe(f"{mu_V} = {fr(VB, 'pb')} = {fr(n(C.VB,3), '50')} = {res(MUVT+' (մ/վ)/մմ')}"),
         'pb հատվածը տարեք p բևեռից ⊥ AB։'),
    step('6. B կետի արագացումը և արագացումների մասշտաբը', f'{a_("B")} = {n(C.AB_ACC,2)} մ/վ², πb = {n(C.PIB)} մմ',
         f'{w1} = const, ուստի շոշափող արագացում չկա (ε<sub>1</sub> = 0)։ Մնում է միայն նորմալ (կենտրոնաձիգ) արագացումը, որը միշտ ուղղված է B-ից դեպի պտտման կենտրոն A։',
         qe(f"{a_('B')} = {w1}²·{lAB} = {n(C.W1,2)}²·{n(C.LAB,4)} = {n(W1SQ,2)}·{n(C.LAB,4)} = {res(n(C.AB_ACC,2)+' մ/վ²')}")
         + f'<p>Տետրի օրինակի պես ընդունում ենք <b>πb = 70 մմ</b>.</p>'
         + qe(f"{mu_a} = {fr(a_('B'), 'πb')} = {fr(n(C.AB_ACC,2), '70')} = {res(MUAT+' (մ/վ²)/մմ')}", 'πb ∥ AB, B → A'),
         'πb հատվածը տարեք π բևեռից AB-ին զուգահեռ, B-ից A ուղղությամբ։'),
    step('7. Աշխատանքային և պարապ ընթացքների անկյունները', f'{n(M.PHI_W)}° / {n(M.PHI_I)}°',
         'Աշխատանքային ընթացքում սողնակը F₀-ից իջնում է F₀′, պարապ ընթացքում վերադառնում է։ Պետք է պարզել, թե այդ ընթացքում կռունկը քանի աստիճան է պտտվում։ Սկիզբը B₀ դիրքն է (AC₀ ուղղի վրա), վերջը՝ B₀′ (C₀′A ուղղի շարունակության վրա)։',
         f'<p>A-ով տանենք հորիզոնական. AB₀-ն ձախ կողմում է, հորիզոնականից {n(b0_dn)}° ցածր, AB₀′-ը՝ աջ կողմում, {n(b0p_dn)}° ցածր։ Ժամացույցի սլաքի ուղղությամբ B₀-ից B₀′ կռունկը նախ բարձրանում է {n(b0_dn)}°-ով մինչև հորիզոնական, անցնում վերևի կիսաշրջանը (180°), ապա իջնում {n(b0p_dn)}°։</p>'
         + qe(f"<i>φ</i><sub>աշխ</sub> = {n(b0_dn)}° + 180° + {n(b0p_dn)}° = {res(n(M.PHI_W)+'°')},&nbsp;&nbsp; <i>φ</i><sub>պ</sub> = 360° − {n(M.PHI_W)}° = {res(n(M.PHI_I)+'°')}")
         + qe(f"<i>K</i> = {fr(v('φ','աշխ'), v('φ','պ'))} = {fr(n(M.PHI_W), n(M.PHI_I))} = {n(M.PHI_W/M.PHI_I,2)}", 'K &gt; 1. պարապ ընթացքն ավելի արագ է')),
]
calc_html = ('<h3 class="calc-title">Ինչպես են ստացվել այս թվերը</h3>'
             '<p class="hint prose">Յուրաքանչյուր քայլում՝ ինչու ենք այդպես հաշվում, բանաձևը և տեղադրված թվերը։ Մանրամասն կառուցումը՝ §1–§3 բաժիններում։</p>'
             '<ol class="calc">' + ''.join(calc_steps) + '</ol>')

results_sec = f'''
<section class="wrap sec" id="results">
  <h2>Հիմնական արդյունքներ</h2>
  <dl class="kv">
    <div><dt>Երկարությունների մասշտաբ</dt><dd>{mu_l} = {MUT} մ/մմ</dd></div>
    <div><dt>Կռունկ AB</dt><dd>{lAB} = {n(C.LAB,4)} մ <span>AB* = {n(C.AB,2)} մմ</span></dd></div>
    <div><dt>Շարժաթև BC</dt><dd>{lBC} = {n(C.LBC,4)} մ <span>BC* = {n(C.BC,2)} մմ</span></dd></div>
    <div><dt>Լծակի ճոճման անկյուն</dt><dd><i>ψ</i> = {n(M.PSI)}°</dd></div>
    <div><dt>Կռունկի անկյունային արագություն</dt><dd>{w1} = {n(C.W1,2)} ռադ/վ</dd></div>
    <div><dt>B կետի արագություն</dt><dd>{VB} = {n(C.VB,3)} մ/վ</dd></div>
    <div><dt>Արագությունների մասշտաբ</dt><dd>{mu_V} = {MUVT} (մ/վ)/մմ <span>pb = {n(C.PB)} մմ</span></dd></div>
    <div><dt>B կետի արագացում</dt><dd>{a_('B')} = {n(C.AB_ACC,2)} մ/վ²</dd></div>
    <div><dt>Արագացումների մասշտաբ</dt><dd>{mu_a} = {MUAT} (մ/վ²)/մմ <span>πb = {n(C.PIB)} մմ</span></dd></div>
    <div><dt>Ընթացքների անկյուններ</dt><dd>{n(M.PHI_W)}° / {n(M.PHI_I)}° <span>աշխատանքային / պարապ</span></dd></div>
  </dl>
  {calc_html}
</section>'''

order_items = [
    f'Թերթը դրեք հորիզոնական։ O(0; 0) կետը ցանցի ներքևի ձախ անկյունն է։ Ներքևի աջ անկյունում (x = 277…377, y = 3…19) թողեք տեղ հիմնական մակագրության համար։',
    f'Նշեք <b>D{ptxt(Dp)}</b>։ D-ով տարեք ուղղաձիգ կետագիծ մինչև y = 5. դա 5 սողնակի ուղղորդն է։ Գծեք հենարանի նշանը։',
    f'Նշեք <b>A{ptxt(Ap)}</b>։ Ստուգեք. A-ն D-ից {n(M.L1S,0)} մմ աջ է և {n(M.L2S)} մմ ցածր։',
    f'Կարկինով D կենտրոնից գծեք երկու աղեղ. <b>R = {n(M.ED)} մմ</b> (E կետի հետագիծ, ձախ ներքևում) և <b>R = {n(M.CD)} մմ</b> (C կետի հետագիծ, աջ ներքևում)։',
    f'D-ից ուղղաձիգից 3° ձախ տարեք ճառագայթ → <b>E₀′{ptxt(E0ps)}</b>։ E₀′-ից R = {n(M.EF)} մմ աղեղով հատեք ուղղորդը → <b>F₀′{ptxt(F0ps)}</b>։',
    f'F₀′-ից {n(M.H)} մմ վեր → <b>F₀{ptxt(F0s)}</b>։ F₀-ից R = {n(M.EF)} մմ աղեղով հատեք E-ի հետագիծը → <b>E₀{ptxt(E0s)}</b>։',
    f'Անկյունաչափով DE₀-ից և DE₀′-ից 50° աջ (ժամացույցի սլաքի հակառակ ուղղությամբ) → <b>C₀{ptxt(C0s)}</b> և <b>C₀′{ptxt(C0ps)}</b>։ Կարկինով ավելի հեշտ է. E₀-ից և E₀′-ից R = CE* = {n(C.CE_S)} մմ աղեղով հատեք C-ի հետագիծը։',
    f'Քանոնով չափեք AC₀ ≈ {n(C.AC0)} մմ և AC₀′ ≈ {n(C.AC0P)} մմ, հաշվեք AB = {n(C.AB,2)} մմ, BC = {n(C.BC,2)} մմ (§1, կետ 3)։',
    f'A-ից գծեք R = {n(C.AB,2)} մմ շրջանագիծ։ B₀-ն AC₀ հատվածի և շրջանագծի հատումն է, B₀′-ը՝ C₀′A ուղղի շարունակության վրա, A-ից այն կողմ։',
    f'B₀-ից սկսած շրջանագիծը ժամացույցի սլաքի ուղղությամբ բաժանեք 8 հավասար մասի (45°-ական). B₁…B₇ (աղյուսակ ներքևում)։',
    f'Յուրաքանչյուր Bᵢ-ից R = {n(C.BC,2)} մմ աղեղով հատեք C-ի հետագիծը → Cᵢ. Cᵢ-ից R = {n(C.CE_S)} մմ աղեղով հատեք E-ի հետագիծը → Eᵢ. Eᵢ-ից R = {n(M.EF)} մմ աղեղով հատեք ուղղորդը → Fᵢ։ Ստուգեք աղյուսակով։',
    f'Բոլոր դիրքերը գծեք բարակ, 2-րդ դիրքը՝ հաստ, սողնակը՝ ուղղանկյունով։ B₂C₂-ի մեջտեղում նշեք <b>S₂{ptxt(S2w)}</b>։ Գծեք L₁*, L₂*, H<sub>F</sub>* չափերը, գրեք {mu_l}։',
    f'F<sub>re</sub> գրաֆիկ. S<sub>F</sub> առանցքը՝ x = {n(M.DIAG_X,0)} ուղղաձիգ F₀-ի մակարդակից (y = {n(F0s[1])}) ներքև, F<sub>re</sub> առանցքը՝ y = {n(F0s[1])} ուղղով դեպի աջ. {int(M.FMAX)} Ն = {n(wF)} մմ։ Յուրաքանչյուր Fᵢ-ից տարեք հորիզոնական կետագիծ դեպի կորը։',
    f'Արագացումների պլան (հաստ դիրքը՝ 2, πb = 70 մմ). բևեռը՝ <b>π{ptxt(M.PA)}</b>, մակագրությունը՝ աջից։ Կետերը՝ աղյուսակում։',
    f'Գրեք տառային նշումները, մասշտաբները ({mu_l}, {mu_a}, {mu_F}) և լրացրեք հիմնական մակագրությունը (Թերթ 1 / 2)։ Վերջում ընդգծեք հիմնական գծերը։',
]
order2_items = [
    'Նույն ցանցը, ներքևի աջ անկյունում՝ մակագրության տեղ։ Վերևում (y ≈ 263) գրեք «Արագությունների պլաններ» և μ<sub>V</sub> = ' + MUVT + ' (մ/վ)/մմ, pb = 50 մմ։',
    'Թերթը բաժանեք 4 × 2 վանդակի բարակ կետագծերով. ուղղաձիգները՝ x = 96,5; 189,5; 282,5, հորիզոնականը՝ y = 137։ Վերևի շարքում՝ դիրքեր 0–3, ներքևում՝ 4–7։',
] + [f'Դիրք {i}. բևեռը՝ <b>p{ptxt(M.PV2[i])}</b>' + ('. pb = 50 մմ ⊥ AB, c, e, f-ը համընկնում են p-ի հետ, s₂-ը pb-ի մեջտեղում' if i == 0 else
     f'. pb = 50 մմ ⊥ AB → c (⊥BC և ⊥CD հատում) → e (pe = {n(C.vchain(i)["pe"])} մմ, ∠cpe = 50°) → f (⊥EF և ուղղաձիգի հատում) → s₂ (bc-ի մեջտեղ)') + f'։ Ներքևում գրեք «Դիրք {i}»։'
     for i in range(8)] + [
    'Ստուգեք բոլոր պլանների կետերը աղյուսակներով, ընդգծեք վեկտորները, լրացրեք մակագրությունը (Թերթ 2 / 2)։',
]
def _chk(sheet, items):
    return ''.join(f'<li><label class="stp"><input type="checkbox" data-step="s{sheet}-{k}"><span>{t}</span></label></li>' for k, t in enumerate(items, 1))
order_html = ('<p class="stp-bar"><span class="stp-count" aria-live="polite"></span><button type="button" class="stp-reset">Զրոյացնել</button></p>'
              '<h4 class="stp-h">Թերթ 1</h4><ol class="steps">' + _chk(1, order_items) + '</ol>'
              '<h4 class="stp-h">Թերթ 2</h4><ol class="steps">' + _chk(2, order2_items) + '</ol>')

layers = [('ly-grid', 'grid', 'Ցանց', True), ('ly-constr', 'constr', 'Կառուցում', True), ('ly-pos', 'pos', 'Դիրքեր 0–7', True),
          ('ly-work', 'work', 'Դիրք 2', True), ('ly-lbl', 'labels xlabels', 'Նշումներ', True), ('ly-dims', 'dims', 'Չափեր', True),
          ('ly-diag', 'diag', 'F<sub>re</sub> գրաֆիկ', True), ('ly-aplan', 'aplan', 'Արագաց. պլան', True)]
tools = ''.join(f'<label class="chip" for="{i}"><input type="checkbox" id="{i}" data-layers="{l}"{" checked" if c else ""}> {t}</label>' for i, l, t, c in layers)

VTH = '<thead><tr><th scope="col">Կետ</th><th scope="col">x</th><th scope="col">y</th><th scope="col">p-ից, մմ</th><th scope="col">V, մ/վ</th></tr></thead>'
vplan_tbls = ''.join(f'<div><h3 class="vel">Արագությունների պլան, դիրք {i}{" (հաստ դիրք)" if i == P2 else ""}</h3>'
                     f'<div class="tscroll"><table class="coords">{VTH}<tbody>{vplan_tbl(i)}</tbody></table></div></div>' for i in range(8))
sheet_sec = f'''
<section class="wide-sec sec" id="sheet">
  <div class="wrap">
    <h2>A3 թերթերը</h2>
    <div class="prose">
      <p>Թերթը դրեք հորիզոնական։ <b>O(0; 0)</b> կետը միլիմետրական ցանցի ներքևի ձախ անկյունն է. <i>x</i>-ը դեպի աջ, <i>y</i>-ը դեպի վեր, բոլոր կոորդինատները՝ մմ։ Գծագիրը երկու A3 թերթի վրա է. <b>թերթ 1</b>՝ դիրքերի պլան, F<sub>re</sub> գրաֆիկ և 2-րդ դիրքի արագացումների պլան, <b>թերթ 2</b>՝ 8 դիրքերի արագությունների պլանները։ Յուրաքանչյուր թերթ տեղավորվում է 377 × 267 մմ ուղղանկյան մեջ. եթե ձեր ցանցն ավելի մեծ է, կարող եք բոլոր x-երին (կամ y-երին) ավելացնել նույն թիվը։</p>
      <p class="note">Էկրանին բլոկները առանձնացված են գույներով (կապույտ՝ արագություններ, կանաչ՝ արագացումներ)։ Թղթի վրա ամեն ինչ գծեք մատիտով. օժանդակ գծերը՝ բարակ, 2-րդ դիրքը և պլանների վեկտորները՝ հաստ։ Մկնիկը թերթի վրա տանելիս ներքևում երևում են կուրսորի կոորդինատները, կետի վրա՝ կետի անունը։</p>
    </div>
  </div>
  <div class="wrap"><h3 class="sheet-h">Թերթ 1</h3>
    <div class="sheet-bar">
      <div class="chips" role="group" aria-label="Շերտեր">{tools}</div>
      <div class="zoom" role="group" aria-label="Մեծացում" data-for="1">
        <button type="button" data-zoom="1" aria-pressed="true">Ամբողջը</button><button type="button" data-zoom="2" aria-pressed="false">×2</button><button type="button" data-zoom="3.2" aria-pressed="false">×3</button>
      </div>
    </div>
  </div>
  <div class="sheet-frame" data-sheet="1">
    <div class="sheet-scroll"><div class="sheet-inner">{sheet_svg}</div></div>
    <p class="readout" aria-live="polite">Տարեք մկնիկը թերթի վրա</p>
  </div>
  <div class="wrap">
    <div class="grid2 top">
      <div class="prose">
        <h3>Գծելու հերթականությունը</h3>
        <div class="stp-wrap">{order_html}</div>
      </div>
      <div>
        <h3>Հիմնական կետերը</h3>
        <p class="hint">Տողի վրա սավառնելիս կետը նշվում է թերթի վրա։</p>
        <div class="tscroll"><table class="coords">
          <thead><tr><th scope="col">Կետ</th><th scope="col">x, մմ</th><th scope="col">y, մմ</th><th scope="col">Ինչ է</th></tr></thead>
          <tbody>{key_tbl}</tbody>
        </table></div>
      </div>
    </div>
    <h3 id="coords-pos">8 դիրքերի կետերը (թերթի կոորդինատներ, մմ)</h3>
    <p class="hint">φ-ն կռունկի պտտման անկյունն է B₀-ից, ժամացույցի սլաքի ուղղությամբ։ F-ի բոլոր դիրքերը x = 90 ուղղաձիգի վրա են։</p>
    <div class="tscroll"><table class="coords wide">
      <thead>
        <tr><th scope="col" rowspan="2">Դիրք</th><th scope="col" rowspan="2">φ</th><th scope="colgroup" colspan="2">B</th><th scope="colgroup" colspan="2">C</th><th scope="colgroup" colspan="2">E</th><th scope="col">F</th><th scope="colgroup" colspan="2">S₂</th><th scope="col" rowspan="2">Ընթացք</th></tr>
        <tr><th scope="col">x</th><th scope="col">y</th><th scope="col">x</th><th scope="col">y</th><th scope="col">x</th><th scope="col">y</th><th scope="col">y</th><th scope="col">x</th><th scope="col">y</th></tr>
      </thead>
      <tbody>{pos_tbl}</tbody>
    </table></div>
    <div class="grid2 top">
      <div>
        <h3 class="acc">Արագացումների պլան, դիրք 2</h3>
        <div class="tscroll"><table class="coords"><thead><tr><th scope="col">Կետ</th><th scope="col">x</th><th scope="col">y</th><th scope="col">Հատված, մմ</th><th scope="col">a, մ/վ²</th></tr></thead><tbody>{aplan_tbl()}</tbody></table></div>
      </div>
      <div class="prose">
        <h3>Ինչպես օգտվել պլանների աղյուսակներից</h3>
        <p>Բևեռը (p կամ π) դրեք նշված կոորդինատում, հետո մյուս կետերը։ Թղթի վրա <b>կառուցեք</b> պլանը ուղղահայացներով (§2, §3), իսկ կոորդինատներով միայն <b>ստուգեք</b>. եթե կետը 1 մմ-ից ավելի է շեղվում, ուղղությունը սխալ է տարված։</p>
        <p>Հատվածի երկարությունը բազմապատկելով մասշտաբով՝ ստանում եք արագությունը կամ արագացումը. օր.՝ {VC} = pc·{mu_V} = {n(vc2["pc"])}·{MUVT} = {n(vc2["VC"],3)} մ/վ։</p>
      </div>
    </div>
  </div>
  <div class="wrap"><h3 class="sheet-h">Թերթ 2</h3>
    <div class="sheet-bar">
      <div class="chips" role="group" aria-label="Շերտեր"></div>
      <div class="zoom" role="group" aria-label="Մեծացում" data-for="2">
        <button type="button" data-zoom="1" aria-pressed="true">Ամբողջը</button><button type="button" data-zoom="2" aria-pressed="false">×2</button><button type="button" data-zoom="3.2" aria-pressed="false">×3</button>
      </div>
    </div>
  </div>
  <div class="sheet-frame" data-sheet="2">
    <div class="sheet-scroll"><div class="sheet-inner">{sheet2_svg}</div></div>
    <p class="readout" aria-live="polite">Տարեք մկնիկը թերթի վրա</p>
  </div>
  <div class="wrap">
    <div class="grid3">{vplan_tbls}</div>
  </div>
</section>'''

vt_c = f'''<div class="tscroll"><table class="vt">
<thead><tr><th></th><th scope="col">{vVC}</th><th class="op">=</th><th scope="col">{vVB}</th><th class="op">+</th><th scope="col">{vVCB}</th></tr></thead>
<tbody><tr><th scope="row">մեծություն</th><td class="q">?</td><td></td><td class="k">{n(C.VB,3)} մ/վ</td><td></td><td class="q">?</td></tr>
<tr><th scope="row">ուղղություն</th><td class="k">⊥ CD</td><td></td><td class="k">⊥ AB</td><td></td><td class="k">⊥ BC</td></tr></tbody></table></div>'''
vt_f = f'''<div class="tscroll"><table class="vt">
<thead><tr><th></th><th scope="col">{vVF}</th><th class="op">=</th><th scope="col">{vVE}</th><th class="op">+</th><th scope="col">{vVFE}</th></tr></thead>
<tbody><tr><th scope="row">մեծություն</th><td class="q">?</td><td></td><td class="k">հայտնի (pe)</td><td></td><td class="q">?</td></tr>
<tr><th scope="row">ուղղություն</th><td class="k">∥ ուղղորդ (ուղղաձիգ)</td><td></td><td class="k">⊥ DE</td><td></td><td class="k">⊥ EF</td></tr></tbody></table></div>'''
at_c = f'''<div class="tscroll"><table class="vt">
<thead><tr><th></th><th scope="col">{a_("B",vec=True)}</th><th class="op">+</th><th scope="col">{a_("CB","n",True)}</th><th class="op">+</th><th scope="col">{a_("CB","τ",True)}</th><th class="op">=</th><th scope="col">{a_("CD","n",True)}</th><th class="op">+</th><th scope="col">{a_("CD","τ",True)}</th></tr></thead>
<tbody><tr><th scope="row">մեծություն</th><td class="k">{n(C.AB_ACC,2)}</td><td></td><td class="k">{n(ac2["aCBn"],3)}</td><td></td><td class="q">?</td><td></td><td class="k">{n(ac2["aCDn"],2)}</td><td></td><td class="q">?</td></tr>
<tr><th scope="row">ուղղություն</th><td class="k">B → A</td><td></td><td class="k">C → B</td><td></td><td class="k">⊥ BC</td><td></td><td class="k">C → D</td><td></td><td class="k">⊥ CD</td></tr></tbody></table></div>'''
at_f = f'''<div class="tscroll"><table class="vt">
<thead><tr><th></th><th scope="col">{a_("F",vec=True)}</th><th class="op">=</th><th scope="col">{a_("E",vec=True)}</th><th class="op">+</th><th scope="col">{a_("FE","n",True)}</th><th class="op">+</th><th scope="col">{a_("FE","τ",True)}</th></tr></thead>
<tbody><tr><th scope="row">մեծություն</th><td class="q">?</td><td></td><td class="k">հայտնի (πe)</td><td></td><td class="k">{n(ac2["aFEn"],2)}</td><td></td><td class="q">?</td></tr>
<tr><th scope="row">ուղղություն</th><td class="k">∥ ուղղորդ</td><td></td><td class="k">նմանությամբ</td><td></td><td class="k">F → E</td><td></td><td class="k">⊥ EF</td></tr></tbody></table></div>'''

s1 = f'''
<section class="wrap sec" id="s1">
  <h2><span class="secno">§1</span> Մեխանիզմի սինթեզ և դիրքերի պլանի կառուցում</h2>
  <div class="prose">
    <h3>1) Երկարությունների մասշտաբային գործակիցը</h3>
    <p>Գծագրում <i>L</i><sub>1</sub>-ը պատկերում ենք <i>L</i><sub>1</sub>* = {n(M.L1S,0)} մմ հատվածով. այդպես ամբողջ մեխանիզմը տեղավորվում է A3 թերթի ձախ և վերին մասում, իսկ ներքևի աջ մասը մնում է պլանների համար։</p>
    {eq(f"{mu_l} = {fr(v('L','1'), v('L','1')+'*')} = {fr(si(D_['L1']), n(M.L1S,0))} = {res(MUT)} մ/մմ")}
    <p>Իրական երկարությունները բաժանելով {mu_l}-ի՝ ստանում ենք գծագրային երկարությունները.</p>
    {eq(f"{v('H','F')}* = {fr(v('H','F'), mu_l)} = {fr(si(D_['HF']), MUT)} = {res(n(M.H)+' մմ')}")}
    {eq(f"{v('L','2')}* = {fr(v('L','2'), mu_l)} = {fr(si(D_['L2']), MUT)} = {res(n(M.L2S)+' մմ')}")}
    {eq(f"EF* = {fr(lEF, mu_l)} = {fr(si(D_['lEF']), MUT)} = {res(n(M.EF)+' մմ')}")}
    {eq(f"ED* = {fr(lED, mu_l)} = {fr(si(D_['lED']), MUT)} = {res(n(M.ED)+' մմ')}")}
    {eq(f"{lCD} = 0,9·{lED} = 0,9·{si(D_['lED'])} = {LCDT} մ,&nbsp;&nbsp; CD* = {fr(LCDT, MUT)} = {res(n(M.CD)+' մմ')}")}

    <h3>2) Եզրային դիրքերի կառուցումը</h3>
    <p>Սողնակը շարժվում է D-ով անցնող ուղղաձիգով, և նրա եզրային դիրքերը համընկնում են CDE լծակի եզրային դիրքերի հետ։ Ստորին եզրային դիրքում DE-ն ուղղաձիգից շեղում ենք <b>β = 3°</b>, որպեսզի D, E, F կետերը երբեք մեկ ուղղի վրա չհայտնվեն։</p>
    <ol class="alpha">
      <li>D-ից ուղղաձիգից 3° ձախ տանում ենք DE₀′ = {n(M.ED)} մմ → <b>E₀′</b>։</li>
      <li>E₀′-ից R = EF* = {n(M.EF)} մմ աղեղով հատում ենք ուղղորդը → <b>F₀′</b> (ստորին եզրային դիրք)։</li>
      <li>F₀′-ից վերև չափում ենք {v('H','F')}* = {n(M.H)} մմ → <b>F₀</b> (վերին եզրային դիրք)։</li>
      <li>F₀-ից R = {n(M.EF)} մմ աղեղով հատում ենք E-ի հետագիծը (կենտրոնը D, R = {n(M.ED)} մմ) → <b>E₀</b>։ Լծակի ճոճման անկյունը ψ = ∠E₀DE₀′ = {n(M.PSI)}°։</li>
      <li>3 օղակը կոշտ է, ∠CDE = 50°։ DE₀-ից և DE₀′-ից 50° աջ (ժամացույցի սլաքի հակառակ ուղղությամբ) տանում ենք DC = {n(M.CD)} մմ → <b>C₀</b>, <b>C₀′</b>։</li>
      <li>A կետը D-ից {n(M.L1S,0)} մմ աջ է և {n(M.L2S)} մմ ցածր։</li>
    </ol>
  </div>
  <figure class="fig">
    <div class="fig-svg">{syn_svg}</div>
    <figcaption>Եզրային դիրքերի կառուցումը։ Բոլոր թվերը թերթի կոորդինատներով են (մմ), այնպես, ինչպես պետք է լինեն ձեր թերթի վրա։</figcaption>
  </figure>
  <div class="prose">
    <h3>3) Կռունկի և շարժաթևի երկարությունները</h3>
    <p>Լծակի եզրային դիրքերում AB կռունկը և BC շարժաթևը գտնվում են մեկ ուղղի վրա. ձգված դիրքում B₀-ն A-ի և C₀-ի միջև է (AC₀ = AB + BC), ծալված դիրքում A-ն B₀′-ի և C₀′-ի միջև է (AC₀′ = BC − AB)։ Գծագրից չափում ենք AC₀ = {n(C.AC0)} մմ, AC₀′ = {n(C.AC0P)} մմ։</p>
    {eq(f'<span class="sys"><span>AB + BC = {n(C.AC0)}</span><span>BC − AB = {n(C.AC0P)}</span></span>&nbsp; ⇒ &nbsp;2·BC = {n(C.AC0+C.AC0P)}')}
    {eq(f"BC = {res(n(C.BC,2)+' մմ')},&nbsp;&nbsp; AB = {n(C.AC0)} − {n(C.BC,2)} = {res(n(C.AB,2)+' մմ')}")}
    {eq(f"{lAB} = AB·{mu_l} = {n(C.AB,2)}·{MUT} = {res(n(C.LAB,4)+' մ')}")}
    {eq(f"{lBC} = BC·{mu_l} = {n(C.BC,2)}·{MUT} = {res(n(C.LBC,4)+' մ')}")}
    {eq(f"{lBS2} = 0,5·{lBC} = 0,5·{n(C.LBC,4)} = {n(C.LBS2,4)} մ,&nbsp;&nbsp; BS₂* = {n(C.BS2S)} մմ")}

    <h3>4) Ստուգումներ</h3>
    <p>Կռունկը լրիվ պտույտ կանի, եթե ամենակարճ և ամենաերկար օղակների գումարը փոքր է մյուս երկուսի գումարից (Գրասհոֆի պայման).</p>
    {eq(f"{v('l','AD')} = √({v('L','1')}² + {v('L','2')}²) = √({si(D_['L1'])}² + {si(D_['L2'])}²) = {n(AD,4)} մ")}
    {eq(f"{lAB} + {v('l','AD')} = {n(grash_l,4)} մ &lt; {lBC} + {lCD} = {n(grash_r,4)} մ &nbsp;✓")}
    <p>Կռունկը պտտվում է ժամացույցի սլաքի ուղղությամբ. B₀-ից B₀′ (սողնակը իջնում է, աշխատանքային ընթացք) կռունկը պտտվում է {n(M.PHI_W)}°, իսկ վերադարձին (պարապ ընթացք)՝ {n(M.PHI_I)}°։</p>
    {eq(f"<i>K</i> = {fr(v('φ','աշխ'), v('φ','պ'))} = {fr(n(M.PHI_W), n(M.PHI_I))} = {res(n(M.PHI_W/M.PHI_I,2))}", 'միջին արագության փոփոխման գործակից')}

    <h3>5) Դիրքերի պլանը</h3>
    <p>Կռունկի շրջանագիծը B₀-ից սկսած ժամացույցի սլաքի ուղղությամբ բաժանում ենք 8 հավասար մասի՝ 0, 1, …, 7 դիրքեր։ Յուրաքանչյուր դիրքի համար կարկինով գտնում ենք.</p>
    <ul class="dash">
      <li><b>Cᵢ</b>. Bᵢ կենտրոնով R = BC* = {n(C.BC,2)} մմ աղեղի և C-ի հետագծի հատումը,</li>
      <li><b>Eᵢ</b>. Cᵢ կենտրոնով R = CE* = {n(C.CE_S)} մմ աղեղի և E-ի հետագծի հատումը (որովհետև ∠CDE = 50°),</li>
      <li><b>Fᵢ</b>. Eᵢ կենտրոնով R = EF* = {n(M.EF)} մմ աղեղի և ուղղորդի հատումը,</li>
      <li><b>S₂ᵢ</b>. BᵢCᵢ հատվածի միջնակետը։</li>
    </ul>
    {eq(f"CE* = √(CD*² + ED*² − 2·CD*·ED*·cos 50°) = {res(n(C.CE_S)+' մմ')}")}
    <p>0-րդ դիրքում սողնակը վերին եզրային դիրքում է (F₀), B₀′ դիրքում՝ ստորին (F₀′)։ Աշխատանքային դիրք ընտրում ենք 2-րդը (ինչպես օրինակում). այն գծում ենք հաստ գծերով։</p>
    <aside class="aside">
      <p class="aside-h">Մեթոդի ստուգումը օրինակով</p>
      <p>Նույն կառուցումը օրինակի տետրի թվերով (<i>H</i><sub>F</sub> = 80, <i>L</i><sub>1</sub> = 320, <i>L</i><sub>2</sub> = 130, <i>l</i><sub>EF</sub> = 180, <i>l</i><sub>ED</sub> = 190) տալիս է AC₀ ≈ 178 մմ և AC₀′ ≈ 121÷122 մմ, իսկ տետրում գրված է 177 և 120։ Տարբերությունը ձեռքով գծելու ճշտության սահմաններում է։ Ուղղորդը D-ից ընդամենը 10 մմ տեղաշարժելիս AC₀-ն կփոխվեր 5÷6 մմ-ով, այսինքն՝ ուղղորդն իսկապես անցնում է D-ով։</p>
    </aside>
  </div>
</section>'''

pos2 = M.POS[2]['K']
s2 = f'''
<section class="wrap sec" id="s2">
  <h2><span class="secno">§2</span> Արագությունների պլաններ</h2>
  <div class="prose">
    <h3>1) B կետի արագությունը</h3>
    <p>Կռունկը պտտվում է հաստատուն անկյունային արագությամբ.</p>
    {eq(f"{w1} = {fr('π·'+v('n','1'), '30')} = {fr('3,1416·'+str(D_['n1']),'30')} = {res(n(C.W1,2)+' ռադ/վ')}")}
    {eq(f"{VB} = {w1}·{lAB} = {n(C.W1,2)}·{n(C.LAB,4)} = {n(C.VB4,4)} ≈ {res(n(C.VB,3)+' մ/վ')}")}
    <p>{vVB} ⊥ AB և ուղղված է {w1}-ի պտույտի կողմը (↻)։ Մեծությունը բոլոր դիրքերում նույնն է։</p>

    <h3>2) Մասշտաբը</h3>
    <p>Ընդունում ենք pb = 50 մմ (B կետի արագությունը պատկերող հատվածը).</p>
    {eq(f"{mu_V} = {fr(VB, 'pb')} = {fr(w1+'·'+lAB, 'pb')} = {fr(n(C.VB,3), '50')} = {res(MUVT+' (մ/վ)/մմ')}")}

    <h3>3) C կետի արագությունը</h3>
    <p>C կետը պատկանում է և՛ 2 օղակին (շարժվում է B-ի նկատմամբ), և՛ 3 օղակին (պտտվում է D-ի շուրջը).</p>
    {eq(f"{vVC} = {vVB} + {vVCB},&nbsp;&nbsp;&nbsp; {vVC} = {vVD} + {vVCD},&nbsp; {VB.replace('B','D')} = 0")}
    {vt_c}
    <p><b>Կառուցում.</b> p բևեռից տանում ենք pb ⊥ AB ({n(C.PB)} մմ), b կետով՝ BC-ին ուղղահայաց ուղիղ, p կետով (D-ի պատկերը p-ում է)՝ CD-ին ուղղահայաց ուղիղ։ Դրանց հատումը <b>c</b> կետն է։</p>

    <h3>4) E կետի արագությունը՝ նմանության թեորեմով</h3>
    <p>C, D, E կետերը նույն կոշտ օղակի վրա են, ուստի պլանում p(d), c, e եռանկյունը նման է D, C, E եռանկյանը և նույն կերպ է կողմնորոշված.</p>
    {eq(f"pe = pc·{fr(lED, lCD)} = {fr('pc','0,9')},&nbsp;&nbsp; pe ⊥ DE,&nbsp;&nbsp; ∠cpe = 50°")}

    <h3>5) F կետի արագությունը</h3>
    {eq(f"{vVF} = {vVE} + {vVFE}")}
    {vt_f}
    <p><b>Կառուցում.</b> e կետով տանում ենք EF-ին ուղղահայաց ուղիղ, p կետով՝ ուղղաձիգ (ուղղորդին զուգահեռ)։ Հատումը <b>f</b> կետն է։</p>

    <h3>6) S₂ կետը</h3>
    <p>BS₂ = 0,5·BC, հետևաբար <b>s₂</b>-ը bc հատվածի միջնակետն է, և {VS2} = ps₂·{mu_V}։</p>

    <h3>7) Թվային արժեքները՝ դիրք 2</h3>
    <p>Պլանից չափում ենք հատվածները (մմ) և բազմապատկում {mu_V}-ով.</p>
    {eq(f"{VC} = pc·{mu_V} = {n(vc2['pc'])}·{MUVT} = {res(n(vc2['VC'],3)+' մ/վ')}")}
    {eq(f"{VCB} = bc·{mu_V} = {n(vc2['bc'])}·{MUVT} = {res(n(vc2['VCB'],3)+' մ/վ')}")}
    {eq(f"pe = {fr(n(vc2['pc']),'0,9')} = {n(vc2['pe'])} մմ,&nbsp;&nbsp; {VE} = {n(vc2['pe'])}·{MUVT} = {res(n(vc2['VE'],3)+' մ/վ')}")}
    {eq(f"{VFE} = ef·{mu_V} = {n(vc2['ef'])}·{MUVT} = {res(n(vc2['VFE'],3)+' մ/վ')}")}
    {eq(f"{VF} = pf·{mu_V} = {n(vc2['pf'])}·{MUVT} = {res(n(vc2['VF'],3)+' մ/վ')}", 'ուղղված է ներքև')}
    {eq(f"{VS2} = ps₂·{mu_V} = {n(vc2['ps2'])}·{MUVT} = {res(n(vc2['VS2'],3)+' մ/վ')}")}

    <h3>8) Անկյունային արագությունները</h3>
    {eq(f"{w2} = {fr(VCB, lBC)} = {fr(n(vc2['VCB'],3), n(C.LBC,4))} = {res(n(vc2['w2'],2)+' ռադ/վ')} {vc2['w2s']}")}
    {eq(f"{w3} = {fr(VC, lCD)} = {fr(n(vc2['VC'],3), LCDT)} = {res(n(vc2['w3'],2)+' ռադ/վ')} {vc2['w3s']}")}
    {eq(f"{w4} = {fr(VFE, lEF)} = {fr(n(vc2['VFE'],3), si(D_['lEF']))} = {res(n(vc2['w4'],2)+' ռադ/վ')} {vc2['w4s']}")}
    <p>Ուղղությունը որոշելու համար հարաբերական արագության վեկտորը տեղափոխում ենք մեխանիզմի համապատասխան կետ. օրինակ՝ {vVCB}-ն (պլանում b-ից c) դնում ենք C կետում և նայում, թե ինչ ուղղությամբ է այն պտտում BC-ն B-ի շուրջը։ ↻՝ ժամացույցի սլաքի ուղղությամբ, ↺՝ հակառակ։</p>

    <h3>9) Մեռյալ դիրքը (0)</h3>
    <p>0-րդ դիրքում A, B, C կետերը մեկ ուղղի վրա են, ուստի ⊥AB և ⊥BC ուղղությունները համընկնում են. {VC} = {VE} = {VF} = 0, c, e, f կետերը համընկնում են p-ի հետ, {VCB} = {VB}, s₂-ը pb-ի մեջտեղում է, {w2} = {n(C.VB,3)}/{n(C.LBC,4)} = {n(C.VB/C.LBC,2)} ռադ/վ ↺։</p>
    <p class="note">Բոլոր 8 դիրքերի արժեքները՝ <a href="#tables">աղյուսակներում</a>։</p>
  </div>
</section>'''

s3 = f'''
<section class="wrap sec" id="s3">
  <h2><span class="secno">§3</span> Արագացումների պլան (դիրք 2)</h2>
  <div class="prose">
    <h3>1) B կետի արագացումը</h3>
    <p>{w1} = const, ուստի ε<sub>1</sub> = 0, և B կետն ունի միայն նորմալ արագացում՝ ուղղված B-ից A.</p>
    {eq(f"{a_('B')} = {a_('B','n')} = {w1}²·{lAB} = {n(C.W1,2)}²·{n(C.LAB,4)} = {res(n(C.AB_ACC,2)+' մ/վ²')}")}
    <h3>2) Մասշտաբը</h3>
    {eq(f"ընդունում ենք πb = 70 մմ,&nbsp;&nbsp; {mu_a} = {fr(a_('B'), 'πb')} = {fr(n(C.AB_ACC,2),'70')} = {res(MUAT+' (մ/վ²)/մմ')}", 'πb ∥ AB, B → A')}
    <h3>3) C կետի արագացումը</h3>
    {eq(f"{a_('C',vec=True)} = {a_('B',vec=True)} + {a_('CB','n',True)} + {a_('CB','τ',True)} = {a_('D',vec=True)} + {a_('CD','n',True)} + {a_('CD','τ',True)},&nbsp; {a_('D')} = 0")}
    {at_c}
    <p>Նորմալ բաղադրիչները հաշվում ենք արագությունների պլանի արժեքներով.</p>
    {eq(f"{a_('CB','n')} = {fr(VCB+'²', lBC)} = {fr(n(vc2['VCB'],3)+'²', n(C.LBC,4))} = {n(ac2['aCBn'],3)} մ/վ²,&nbsp;&nbsp; bn₂ = {fr(n(ac2['aCBn'],3),MUAT)} = {res(n(ac2['bn2'])+' մմ')}", '∥ BC, C → B')}
    {eq(f"{a_('CD','n')} = {fr(VC+'²', lCD)} = {fr(n(vc2['VC'],3)+'²', LCDT)} = {n(ac2['aCDn'],2)} մ/վ²,&nbsp;&nbsp; πn₃ = {fr(n(ac2['aCDn'],2),MUAT)} = {res(n(ac2['pin3'])+' մմ')}", '∥ CD, C → D')}
    <p><b>Կառուցում.</b> b կետից տանում ենք bn₂ ∥ BC (C-ից B ուղղությամբ), n₂-ով՝ BC-ին ուղղահայաց ուղիղ։ π-ից տանում ենք πn₃ ∥ CD (C-ից D ուղղությամբ), n₃-ով՝ CD-ին ուղղահայաց ուղիղ։ Հատումը <b>c</b> կետն է։</p>
    <h3>4) E կետի արագացումը՝ նմանությամբ</h3>
    {eq(f"πe = πc·{fr(lED, lCD)} = {fr('πc','0,9')},&nbsp;&nbsp; ∠cπe = 50°", 'նույն կողմնորոշումը, ինչ DCE-ում')}
    <h3>5) F կետի արագացումը</h3>
    {eq(f"{a_('F',vec=True)} = {a_('E',vec=True)} + {a_('FE','n',True)} + {a_('FE','τ',True)}")}
    {at_f}
    {eq(f"{a_('FE','n')} = {fr(VFE+'²', lEF)} = {fr(n(vc2['VFE'],3)+'²', si(D_['lEF']))} = {n(ac2['aFEn'],2)} մ/վ²,&nbsp;&nbsp; en₄ = {fr(n(ac2['aFEn'],2),MUAT)} = {res(n(ac2['en4'])+' մմ')}", '∥ EF, F → E')}
    <p><b>Կառուցում.</b> e կետից տանում ենք en₄ ∥ EF (F-ից E ուղղությամբ), n₄-ով՝ EF-ին ուղղահայաց ուղիղ, π-ով՝ ուղղաձիգ։ Հատումը <b>f</b> կետն է։ <b>s₂</b>-ը bc-ի միջնակետն է։</p>
    <h3>6) Թվային արժեքները</h3>
    {eq(f"{a_('CB','τ')} = n₂c·{mu_a} = {n(ac2['n2c'])}·{MUAT} = {res(n(ac2['aCBt'],2)+' մ/վ²')}")}
    {eq(f"{a_('CD','τ')} = n₃c·{mu_a} = {n(ac2['n3c'])}·{MUAT} = {res(n(ac2['aCDt'],2)+' մ/վ²')}")}
    {eq(f"{a_('C')} = πc·{mu_a} = {n(ac2['pic'])}·{MUAT} = {res(n(ac2['aC'],2)+' մ/վ²')}")}
    {eq(f"πe = {fr(n(ac2['pic']),'0,9')} = {n(ac2['pie'])} մմ,&nbsp;&nbsp; {a_('E')} = {n(ac2['pie'])}·{MUAT} = {res(n(ac2['aE'],2)+' մ/վ²')}")}
    {eq(f"{a_('FE','τ')} = n₄f·{mu_a} = {n(ac2['n4f'])}·{MUAT} = {res(n(ac2['aFEt'],2)+' մ/վ²')}")}
    {eq(f"{a_('F')} = πf·{mu_a} = {n(ac2['pif'])}·{MUAT} = {res(n(ac2['aF'],2)+' մ/վ²')}", 'ուղղված է վեր՝ արագությանը հակառակ, սողնակը դանդաղում է')}
    {eq(f"{a_('S₂')} = πs₂·{mu_a} = {n(ac2['pis2'])}·{MUAT} = {res(n(ac2['aS2'],2)+' մ/վ²')}")}
    {eq(f"{e2} = {fr(a_('CB','τ'), lBC)} = {fr(n(ac2['aCBt'],2), n(C.LBC,4))} = {res(n(ac2['e2'],1)+' ռադ/վ²')} {ac2['e2s']}")}
    {eq(f"{e3} = {fr(a_('CD','τ'), lCD)} = {fr(n(ac2['aCDt'],2), LCDT)} = {res(n(ac2['e3'],1)+' ռադ/վ²')} {ac2['e3s']}")}
    {eq(f"{e4} = {fr(a_('FE','τ'), lEF)} = {fr(n(ac2['aFEt'],2), si(D_['lEF']))} = {res(n(ac2['e4'],1)+' ռադ/վ²')} {ac2['e4s']}")}
    <aside class="aside">
      <p class="aside-h">Ինչու են n₃c-ն և n₄f-ը գրեթե զրո</p>
      <p>2-րդ դիրքում {w3}-ը մոտ է իր առավելագույնին (1-ին դիրքում {n(om3_1,2)}, 2-րդում {n(om3_2,2)}, 3-րդում {n(om3_3,2)} ռադ/վ), ուստի {e3} ≈ 0 և {e4} ≈ 0, իսկ n₃c = {n(ac2['n3c'])} մմ, n₄f = {n(ac2['n4f'])} մմ։ Սա կառուցման սխալ չէ։ Եթե դասախոսը այլ դիրք պահանջի, բոլոր դիրքերի արժեքները <a href="#tables">աղյուսակներում</a> են։</p>
    </aside>
  </div>
</section>'''

fre_sec = f'''
<section class="wrap sec" id="fre">
  <h2>Օգտակար դիմադրության ուժի գրաֆիկը</h2>
  <div class="prose">
    <p>F<sub>re</sub> ուժը գործում է միայն աշխատանքային ընթացքում, երբ սողնակը իջնում է (F₀ → F₀′), և ուղղված է շարժմանը հակառակ (վեր)։ S<sub>F</sub> տեղափոխությունը հաշվում ենք F₀-ից։ Գրաֆիկի <b>ձևը արտագծեք առաջադրանքի թերթից</b>՝ S<sub>F</sub> առանցքը դնելով սողնակի ընթացքին զուգահեռ. այդպես Fᵢ դիրքերից հորիզոնական գծերով անմիջապես կարդում եք F<sub>re</sub>-ն։ S<sub>F</sub>-ի մասշտաբը {mu_l} է ({n(M.H)} մմ = {si(D_['HF'])} մ), ուժինը՝</p>
    {eq(f"{mu_F} = {fr(v('F','re')+'<sup>max</sup>', n(wF)+' մմ')} = {fr(str(int(M.FMAX)), n(wF))} = {res(n(M.MUF,0)+' Ն/մմ')}")}
  </div>
  <div class="tscroll"><table class="coords wide">
    <thead><tr><th scope="col">Դիրք</th><th scope="col">Ընթացք</th><th scope="col">S<sub>F</sub>*, մմ</th><th scope="col">S<sub>F</sub>, մ</th><th scope="col">S<sub>F</sub>/H<sub>F</sub></th><th scope="col">F<sub>re</sub>, Ն</th><th scope="col">F<sub>re</sub>*, մմ</th><th scope="col">կորի կետ x</th><th scope="col">y</th></tr></thead>
    <tbody>{fre_rows}</tbody>
  </table></div>
  <p class="note prose">F<sub>re</sub>-ի արժեքները մոտավոր են. կորի ձևը թվայնացված է առաջադրանքի թերթի փոքր նկարից (F<sub>re</sub> = 0, երբ S<sub>F</sub> &lt; 0,28·H<sub>F</sub>, առավելագույնը՝ ≈ 0,85·H<sub>F</sub>-ում)։ Ճշգրիտ արժեքները կարդացեք ձեր գծած գրաֆիկից։ Կինեմատիկայի համար դրանք պետք չեն, պետք կգան ուժային հաշվարկում։</p>
</section>'''

tables_sec = f'''
<section class="wrap sec" id="tables">
  <h2>Բոլոր դիրքերի աղյուսակները</h2>
  <p class="hint prose">Հատվածները՝ մմ, արագությունները՝ մ/վ, անկյունային արագությունները՝ ռադ/վ։ ↓ ↑՝ սողնակի շարժման ուղղությունը, ↻ ↺՝ պտույտի ուղղությունը։ Ընդգծված տողը աշխատանքային դիրքն է։</p>
  <div class="tscroll"><table class="coords wide">
    <caption>Արագություններ ({mu_V} = {MUVT} (մ/վ)/մմ, pb = {n(C.PB)} մմ, {VB} = {n(C.VB,3)} մ/վ)</caption>
    <thead><tr><th scope="col">Դիրք</th><th scope="col">φ</th><th scope="col">pc</th><th scope="col">{VC}</th><th scope="col">bc</th><th scope="col">{VCB}</th><th scope="col">pe</th><th scope="col">{VE}</th><th scope="col">ef</th><th scope="col">{VFE}</th><th scope="col">pf</th><th scope="col">{VF}</th><th scope="col">ps₂</th><th scope="col">{VS2}</th><th scope="col">{w2}</th><th scope="col">{w3}</th><th scope="col">{w4}</th></tr></thead>
    <tbody>{vel_rows}</tbody>
  </table></div>
  <div class="tscroll"><table class="coords wide">
    <caption>Արագացումներ (մ/վ²) և անկյունային արագացումներ (ռադ/վ²), {a_('B')} = {n(C.AB_ACC,2)} մ/վ² բոլոր դիրքերում</caption>
    <thead><tr><th scope="col">Դիրք</th><th scope="col">{a_('CB','n')}</th><th scope="col">{a_('CB','τ')}</th><th scope="col">{a_('CD','n')}</th><th scope="col">{a_('CD','τ')}</th><th scope="col">{a_('C')}</th><th scope="col">{a_('E')}</th><th scope="col">{a_('FE','n')}</th><th scope="col">{a_('FE','τ')}</th><th scope="col">{a_('F')}</th><th scope="col">{a_('S₂')}</th><th scope="col">{e2}</th><th scope="col">{e3}</th><th scope="col">{e4}</th></tr></thead>
    <tbody>{acc_rows}</tbody>
  </table></div>
  <details class="more">
    <summary>Պլանների կետերը բոլոր դիրքերի համար (բևեռի նկատմամբ)</summary>
    <p class="hint">Եթե պետք է այլ դիրքի պլան, բևեռը դրեք թերթի ազատ տեղում և յուրաքանչյուր կետի Δx; Δy (մմ) ավելացրեք բևեռի կոորդինատներին։</p>
    <div class="tscroll"><table class="coords wide">
      <caption>Արագությունների պլան, {mu_V} = {MUVT} (մ/վ)/մմ</caption>
      <thead><tr><th scope="col">Դիրք</th><th scope="col">b</th><th scope="col">c</th><th scope="col">e</th><th scope="col">f</th><th scope="col">s₂</th></tr></thead>
      <tbody>{rel_v}</tbody>
    </table></div>
    <div class="tscroll"><table class="coords wide">
      <caption>Արագացումների պլան, {mu_a} = {MUAT} (մ/վ²)/մմ</caption>
      <thead><tr><th scope="col">Դիրք</th><th scope="col">b</th><th scope="col">n₂</th><th scope="col">c</th><th scope="col">n₃</th><th scope="col">e</th><th scope="col">n₄</th><th scope="col">f</th><th scope="col">s₂</th></tr></thead>
      <tbody>{rel_a}</tbody>
    </table></div>
  </details>
</section>'''

next_sec = f'''
<section class="wrap sec" id="next">
  <h2>Հաջորդ բաժինները</h2>
  <div class="prose">
    <p>Այս էջը ընդգրկում է A3 թերթը և տետրի §1–§3 բաժինները։ Մնացած տվյալները՝ <i>G</i><sub>2</sub> = {D_['G2']} Ն, <i>G</i><sub>5</sub> = {D_['G5']} Ն, <i>I</i><sub>S₂</sub> = {n(D_['IS2']/1000,2)} կգ·մ², F<sub>re</sub>, <i>M</i><sub>m</sub> = const, <i>δ</i> = 0,05, պետք են ուժային (կինետոստատիկ) հաշվարկի և թափանիվի հաշվարկի համար։ Ձեր լուսանկարներում այդ բաժինների օրինակ չկար, ուստի դրանք այստեղ չեն ներառվել։</p>
    <p class="note">Բոլոր թվերը հաշվված են ծրագրով և ստուգված թվային ածանցմամբ։ Ձեր գծագրում չափված երկարությունները կարող են տարբերվել ±0,5 մմ-ով. դա նորմալ է։</p>
  </div>
</section>'''

CSS = r'''
:root{
  --ground:#EDF0EF;--surface:#F9FBFA;--surface-2:#E3E8E7;--ink:#1B2225;--ink-2:#53616A;--ink-3:#77848B;
  --rule:#CAD3D2;--rule-2:#DCE3E2;--mm:#C45F3B;--mm-ink:#9C4424;--mm-soft:#F4DFD4;
  --pen:#21539D;--pen-soft:#DDE7F4;--verd:#206E57;--verd-soft:#D8ECE4;--hi:#F3DE5B;--hi-ink:#1B2225;
  --f-sans:"Noto Sans Armenian",system-ui,-apple-system,"Segoe UI",sans-serif;
  --f-math:"STIX Two Text","Noto Sans Armenian","Times New Roman",serif;
  --f-mono:"JetBrains Mono","Noto Sans Armenian",ui-monospace,Menlo,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ground:#101416;--surface:#161B1E;--surface-2:#1D2326;--ink:#E1E6E7;--ink-2:#9BA7AD;--ink-3:#75828A;
  --rule:#2B3438;--rule-2:#232A2E;--mm:#EA8A62;--mm-ink:#F2A688;--mm-soft:#3A261E;
  --pen:#8FB4EA;--pen-soft:#1A2637;--verd:#74C7AB;--verd-soft:#15291F;--hi:#6E6118;--hi-ink:#F4EBC0;
}}
:root[data-theme="dark"]{
  --ground:#101416;--surface:#161B1E;--surface-2:#1D2326;--ink:#E1E6E7;--ink-2:#9BA7AD;--ink-3:#75828A;
  --rule:#2B3438;--rule-2:#232A2E;--mm:#EA8A62;--mm-ink:#F2A688;--mm-soft:#3A261E;
  --pen:#8FB4EA;--pen-soft:#1A2637;--verd:#74C7AB;--verd-soft:#15291F;--hi:#6E6118;--hi-ink:#F4EBC0;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{background:var(--ground);color:var(--ink);font-family:var(--f-sans);font-size:16px;line-height:1.62;padding-block:28px 64px}
.wrap{max-width:1180px;margin-inline:auto;padding-inline:20px}
.prose{max-width:76ch}
h1,h2,h3{font-stretch:78%;text-wrap:balance;line-height:1.2;margin:0}
h1{font-size:clamp(1.7rem,3.4vw,2.5rem);font-weight:680;letter-spacing:.005em}
h2{font-size:1.72rem;font-weight:660;margin-bottom:18px;display:flex;gap:.55em;align-items:baseline}
h3{font-size:1.14rem;font-weight:650;margin:26px 0 8px}
p{margin:0 0 12px}
a{color:var(--pen)}
a:focus-visible,button:focus-visible,summary:focus-visible,input:focus-visible+*{outline:2px solid var(--pen);outline-offset:2px}
sub,sup{font-size:.72em;line-height:0}
mark{background:var(--hi);color:var(--hi-ink);padding:0 .28em;border-radius:2px}
.eyebrow{font-size:.78rem;letter-spacing:.09em;text-transform:uppercase;color:var(--mm-ink);font-weight:600;margin-bottom:10px}
.lede{color:var(--ink-2);font-size:1.04rem;max-width:62ch;margin:14px 0 0}
.note{color:var(--ink-2);font-size:.93rem}
.hint{color:var(--ink-3);font-size:.86rem;margin-bottom:8px}

/* title block */
.stamp{display:grid;grid-template-columns:minmax(0,1fr) minmax(260px,340px);border:1.5px solid var(--ink);background:var(--surface)}
.stamp-main{padding:26px 28px 24px;border-right:1.5px solid var(--ink)}
.stamp-cells{display:grid;grid-template-columns:1fr 1fr;margin:0}
.stamp-cells>div{padding:12px 16px;border-bottom:1px solid var(--rule);display:flex;flex-direction:column;justify-content:space-between;gap:6px}
.stamp-cells>div:nth-child(odd){border-right:1px solid var(--rule)}
.stamp-cells>div:nth-child(n+3){border-bottom:0}
.stamp-cells dt{font-size:.72rem;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-3)}
.stamp-cells dd{margin:0;font-family:var(--f-math);font-size:1.3rem;font-weight:600}
.stamp-cells>div:nth-child(-n+2) dd{font-size:2.6rem;line-height:1}
.toc{display:flex;flex-wrap:wrap;gap:4px 18px;padding:12px 2px 0;font-size:.92rem}
.toc a{color:var(--ink-2);text-decoration:none;border-bottom:1px solid transparent}
.toc a:hover{color:var(--ink);border-bottom-color:var(--mm)}

.sec{margin-top:56px}
.secno{font-family:var(--f-math);font-stretch:100%;color:var(--mm-ink);font-weight:600}
.grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px 40px}
.grid2.top{align-items:start;margin-top:12px}
.grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px 28px;margin-top:10px}
@media (max-width:980px){.grid3{grid-template-columns:1fr 1fr}}
@media (max-width:760px){.grid2,.grid3{grid-template-columns:1fr}.stamp{grid-template-columns:1fr}.stamp-main{border-right:0;border-bottom:1.5px solid var(--ink)}}

.links{list-style:none;padding:0;margin:10px 0 0;display:grid;gap:6px}
.links li{display:grid;grid-template-columns:28px 1fr;gap:10px;align-items:baseline}
.links .ln{font-family:var(--f-math);font-weight:700;text-align:center;border:1.2px solid var(--ink-2);border-radius:50%;width:24px;height:24px;line-height:21px;font-size:.9rem}
.conds{margin:6px 0 0;padding-left:1.3em;display:grid;gap:4px}
.conds i,.links i{font-family:var(--f-math);font-size:1.06em}
ol.alpha{list-style:lower-alpha;padding-left:1.4em;display:grid;gap:4px}
ul.dash{padding-left:1.2em;display:grid;gap:3px}

/* task table */
.tscroll{overflow-x:auto;margin:14px 0 6px;-webkit-overflow-scrolling:touch}
table{border-collapse:collapse;font-variant-numeric:tabular-nums}
caption{caption-side:top;text-align:left;font-size:.9rem;color:var(--ink-2);padding:0 0 6px;font-weight:600}
.task{min-width:760px;width:100%;background:var(--surface);border:1.5px solid var(--ink)}
.task th,.task td{border:1px solid var(--rule);padding:7px 10px;text-align:center;white-space:nowrap}
.task thead th{font-family:var(--f-math);font-size:1.12rem;font-weight:500;background:var(--surface-2)}
.task tbody th{text-align:left;font-weight:500;color:var(--ink-2);font-size:.86rem}
.task .unit td{font-size:.82rem;color:var(--ink-2)}
.task .val td{font-family:var(--f-mono);font-size:1.12rem;font-weight:600}
.task .si td{font-family:var(--f-mono);font-size:.84rem;color:var(--ink-2)}

/* key results */
.calc-title{margin:30px 0 4px}
.calc{list-style:none;padding:0;margin:10px 0 0;display:grid;gap:14px}
.cstep{background:var(--surface);border:1px solid var(--rule);border-left:3px solid var(--mm);padding:14px 18px 10px}
.cstep-h{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:4px 18px;margin-bottom:6px}
.cstep-h h3{font-size:1.05rem}
.cstep-r{margin:0;font-family:var(--f-math);font-weight:700;color:var(--mm-ink);font-size:1.08rem}
.cstep .why{color:var(--ink-2);max-width:80ch}
.cstep ol.sub{padding-left:1.3em;display:grid;gap:4px;max-width:80ch}
.cstep .where{font-size:.88rem;color:var(--ink-3);margin:8px 0 0}
.cstep .eq:last-of-type{border-bottom:0}
.kv{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:0;margin:0;border-top:1px solid var(--rule);border-left:1px solid var(--rule)}
.kv>div{padding:12px 14px;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);background:var(--surface)}
.kv dt{font-size:.8rem;color:var(--ink-3);margin-bottom:4px}
.kv dd{margin:0;font-family:var(--f-math);font-size:1.18rem;font-weight:600}
.kv dd span{display:block;font-family:var(--f-mono);font-size:.78rem;font-weight:400;color:var(--ink-2);margin-top:2px}

/* equations */
.eq{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:14px;padding:9px 0;border-bottom:1px dashed var(--rule)}
.eq-b{font-family:var(--f-math);font-size:1.16rem;line-height:1.9;overflow-x:auto}
.eq-n{font-family:var(--f-mono);font-size:.78rem;color:var(--ink-3)}
.eq-note{display:inline-block;margin-left:.9em;font-family:var(--f-sans);font-size:.8rem;color:var(--ink-3)}
.frac{display:inline-flex;flex-direction:column;vertical-align:middle;text-align:center;line-height:1.25;margin:0 .12em;font-size:.94em}
.frac>span{padding:0 .2em}
.frac>span:last-child{border-top:1px solid currentColor}
.vec{text-decoration:overline;text-decoration-thickness:1px;text-underline-offset:0}
.res{font-weight:700;color:var(--mm-ink)}
.sys{display:inline-flex;flex-direction:column;vertical-align:middle;border-left:1.5px solid currentColor;padding-left:.45em;line-height:1.45}
.vt{margin:4px 0 10px;font-family:var(--f-math);background:var(--surface)}
.vt th,.vt td{border:1px solid var(--rule);padding:6px 12px;text-align:center;white-space:nowrap}
.vt thead th{font-size:1.14rem;font-weight:500}
.vt tbody th{font-family:var(--f-sans);font-size:.8rem;font-weight:500;color:var(--ink-2);text-align:left}
.vt .op{border:0;color:var(--ink-3);padding:6px 2px}
.vt td:empty{border-left:0;border-right:0}
.vt .q{color:var(--mm-ink);font-weight:700}
.vt .k{color:var(--ink)}

.aside{margin:22px 0 4px;padding:14px 18px;background:var(--surface);border:1px solid var(--rule);border-left:3px solid var(--mm)}
.aside-h{font-weight:650;margin-bottom:6px}
.aside p:last-child{margin-bottom:0}

/* sheet */
.sheet-bar{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px 18px;margin:18px 0 10px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{display:inline-flex;align-items:center;gap:6px;padding:4px 10px 4px 8px;border:1px solid var(--rule);border-radius:3px;background:var(--surface);font-size:.84rem;cursor:pointer;user-select:none}
.chip input{accent-color:var(--mm);margin:0}
.chip:has(input:focus-visible){outline:2px solid var(--pen);outline-offset:2px}
.zoom{display:inline-flex;border:1px solid var(--rule);border-radius:3px;overflow:hidden}
.zoom button{font:inherit;font-size:.84rem;padding:5px 12px;border:0;background:var(--surface);color:var(--ink);cursor:pointer}
.zoom button+button{border-left:1px solid var(--rule)}
.zoom button[aria-pressed="true"]{background:var(--ink);color:var(--surface)}
.sheet-frame{max-width:1500px;margin-inline:auto;padding-inline:20px}
.sheet-scroll{overflow:auto;border:1px solid var(--rule);background:var(--surface-2);max-height:90vh}
.sheet-inner{width:min(100%,calc((90vh - 2px)*404/290));margin-inline:auto}
.sheet .pt{cursor:crosshair}
.sheet .ring{fill:none;stroke:#E0531F;stroke-width:.55;pointer-events:none}
.sheet-h{margin:30px 0 0;font-size:1.2rem}
.readout{font-family:var(--f-mono);font-size:.84rem;color:var(--ink-2);margin:8px 0 0;min-height:1.6em}
ol.steps{padding-left:1.5em;display:grid;gap:7px;margin:8px 0 0}
.stp{display:grid;grid-template-columns:auto 1fr;gap:9px;align-items:start;cursor:pointer}
.stp input{width:17px;height:17px;margin:4px 0 0;accent-color:var(--mm);cursor:pointer}
.stp:has(input:checked) span{color:var(--ink-3)}
ol.steps li:has(input:checked)::marker{color:var(--ink-3)}
.stp-bar{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:6px 0 4px;padding:8px 12px;background:var(--surface);border:1px solid var(--rule);border-left:3px solid var(--mm)}
.stp-count{font-family:var(--f-mono);font-size:.86rem;color:var(--ink-2)}
.stp-reset{font:inherit;font-size:.82rem;padding:3px 10px;border:1px solid var(--rule);border-radius:3px;background:var(--surface);color:var(--ink);cursor:pointer}
.stp-h{margin:16px 0 0;font-size:1rem;color:var(--mm-ink)}
.stp-next{outline:2px solid var(--mm);outline-offset:4px;border-radius:2px}
ol.steps li::marker{font-family:var(--f-mono);color:var(--mm-ink);font-size:.86em}
ol.steps b{font-family:var(--f-mono);font-weight:600;font-size:.92em;white-space:nowrap}

.coords{background:var(--surface);font-size:.86rem;width:100%}
.coords.wide{min-width:760px}
.coords th,.coords td{border-bottom:1px solid var(--rule-2);padding:5px 9px;text-align:left;white-space:nowrap}
.coords thead th{font-size:.76rem;color:var(--ink-3);font-weight:600;border-bottom:1.5px solid var(--rule);background:var(--surface-2)}
.coords tbody th{font-family:var(--f-math);font-size:1rem;font-weight:600}
.coords td.n{font-family:var(--f-mono);text-align:right}
.coords td.t{color:var(--ink-2);white-space:normal;min-width:12ch}
.coords tbody tr[data-pt]:hover{background:var(--mm-soft)}
.coords tr.wkrow{background:var(--surface-2)}
.coords tr.wkrow th{color:var(--mm-ink)}
h3.vel{color:var(--pen)}h3.acc{color:var(--verd)}

.fig{margin:18px 0 8px}
.fig-svg{border:1px solid var(--rule);background:#FFFDF8;overflow:hidden}
.fig figcaption{font-size:.86rem;color:var(--ink-3);margin-top:6px}
details.more{margin-top:20px;border-top:1px solid var(--rule);padding-top:10px}
details.more summary{cursor:pointer;font-weight:600}
'''

JS = r'''
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const sh1 = document.getElementById('sh');
  if (sh1) document.querySelectorAll('input[data-layers]').forEach(inp => {
    const apply = () => inp.dataset.layers.split(' ').forEach(name =>
      sh1.querySelectorAll('[data-layer="' + name + '"]').forEach(g => g.toggleAttribute('hidden', !inp.checked)));
    inp.addEventListener('change', apply); apply();
  });
  const fmt = v => v.toFixed(1).replace('.', ',').replace('-', '−');
  document.querySelectorAll('.sheet-frame').forEach(frame => {
    const svg = frame.querySelector('svg.sheet'); if (!svg) return;
    const scroller = frame.querySelector('.sheet-scroll'), inner = frame.querySelector('.sheet-inner'), ro = frame.querySelector('.readout');
    const zoom = document.querySelector('.zoom[data-for="' + frame.dataset.sheet + '"]');
    if (zoom) zoom.querySelectorAll('button[data-zoom]').forEach(btn => btn.addEventListener('click', () => {
      const cx = (scroller.scrollLeft + scroller.clientWidth / 2) / scroller.scrollWidth;
      const cy = (scroller.scrollTop + scroller.clientHeight / 2) / scroller.scrollHeight;
      const z = parseFloat(btn.dataset.zoom);
      inner.style.width = z === 1 ? '' : (100 * z) + '%';
      zoom.querySelectorAll('button[data-zoom]').forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
      scroller.scrollLeft = cx * scroller.scrollWidth - scroller.clientWidth / 2;
      scroller.scrollTop = cy * scroller.scrollHeight - scroller.clientHeight / 2;
    }));
    const pt = svg.createSVGPoint();
    svg.addEventListener('pointermove', e => {
      const t = e.target.closest ? e.target.closest('.pt') : null;
      if (t) { ro.textContent = t.dataset.k + ':  x = ' + t.dataset.x + ',  y = ' + t.dataset.y + ' մմ'; return; }
      const m = svg.getScreenCTM(); if (!m) return;
      pt.x = e.clientX; pt.y = e.clientY;
      const p = pt.matrixTransform(m.inverse());
      const x = p.x, y = 270 - p.y;
      ro.textContent = (x >= 0 && x <= 380 && y >= 0 && y <= 270) ? 'x = ' + fmt(x) + ',  y = ' + fmt(y) + ' մմ' : 'Կուրսորը ցանցից դուրս է';
    });
  });
  let rings = [];
  const clear = () => { rings.forEach(r => r.remove()); rings = []; };
  document.querySelectorAll('tr[data-pt]').forEach(row => {
    row.addEventListener('pointerenter', () => {
      clear();
      row.dataset.pt.split(' ').forEach(id => {
        const el = document.getElementById('sh-pt-' + id) || document.getElementById('sh2-pt-' + id); if (!el) return;
        const c = document.createElementNS(NS, 'circle');
        c.setAttribute('class', 'ring'); c.setAttribute('r', '2.8');
        c.setAttribute('cx', el.getAttribute('cx')); c.setAttribute('cy', el.getAttribute('cy'));
        el.ownerSVGElement.appendChild(c); rings.push(c);
      });
    });
    row.addEventListener('pointerleave', clear);
  });
  (() => {
    const KEY = 'tmm-variant1-steps';
    const boxes = [...document.querySelectorAll('input[data-step]')]; if (!boxes.length) return;
    const count = document.querySelector('.stp-count'), reset = document.querySelector('.stp-reset');
    let done = {};
    try { done = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { done = {}; }
    const save = () => { try { localStorage.setItem(KEY, JSON.stringify(done)); } catch (e) {} };
    const paint = () => {
      const n = boxes.filter(b => b.checked).length;
      const next = boxes.find(b => !b.checked);
      boxes.forEach(b => b.closest('li').classList.toggle('stp-next', b === next));
      if (count) count.textContent = n + ' / ' + boxes.length + ' քայլ արված' + (next ? ' · հաջորդը՝ ' + (next.dataset.step.startsWith('s1') ? 'թերթ 1' : 'թերթ 2') + ', քայլ ' + next.dataset.step.split('-')[1] : ' · ամեն ինչ պատրաստ է');
    };
    boxes.forEach(b => {
      b.checked = !!done[b.dataset.step];
      b.addEventListener('change', () => { if (b.checked) done[b.dataset.step] = 1; else delete done[b.dataset.step]; save(); paint(); });
    });
    if (reset) reset.addEventListener('click', () => { done = {}; boxes.forEach(b => b.checked = false); save(); paint(); });
    paint();
  })();
})();
'''

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400..600&family=Noto+Sans+Armenian:wdth,wght@62.5..100,400..700&family=STIX+Two+Text:ital,wght@0,400..700;1,400..700&display=swap">'

html = (f'<title>Առաջադրանք 2, տարբերակ {VAR}</title>\n<meta name="description" content="ՄՄՏ, առաջադրանք 2, տարբերակ {VAR}. սինթեզ, արագությունների և արագացումների պլաններ, A3 թերթի գծագիր՝ կոորդինատներով">\n'
        + FONTS + '\n<style>' + CSS + NB.CSS + SH.SHEET_CSS + '</style>\n'
        + header + '<main>' + data_sec + results_sec + sheet_sec + NB.SECTION + s1 + s2 + s3 + fre_sec + tables_sec + next_sec + '</main>'
        + '<script>' + JS + '</script>\n')
import os
HERE = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(HERE, f'variant{VAR}.html'), 'w').write(html)          # body for the Artifact publish
_t = html.index('</title>') + len('</title>'); _h, _rest = html[:_t], html[_t:]; _i = _rest.index('<header')
open(os.path.join(HERE, '..', f'TMM_Variant{VAR}.html'), 'w').write(
    '<!doctype html>\n<html lang="hy">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<style>body{margin:0;font:14px/1.5 system-ui,sans-serif;background:#fafafa}img{max-width:100%}[hidden]{display:none!important}</style>\n'
    + _h + _rest[:_i] + '\n</head>\n<body>\n' + _rest[_i:] + '\n</body>\n</html>\n')
print('written', len(html), 'bytes; equations:', Eq.k)
