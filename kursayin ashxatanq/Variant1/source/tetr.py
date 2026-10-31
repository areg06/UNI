"""Builds ../tetr.html: what to write in the copybook, page by page (pages 10–18 from notebook.py + tips)."""
import os
import model as M
import calc as C
import notebook as NB
from calc import n

VAR = M.VARIANT
P2 = M.PA_POS
rot = lambda s: s.replace('↻', '<span class="rot">↻</span>').replace('↺', '<span class="rot">↺</span>')

# (anchor, page html, title, what is on it, where the numbers come from)
PAGES = [
    ('p10', NB.p10, 'Էջ 10', 'Առաջադրանքը և §1-ի սկիզբը',
     ['«Առաջադրանք N 2» վերնագիրը՝ շրջանակի մեջ',
      'Տվյալների աղյուսակը՝ միայն ձեր տարբերակի տողը',
      'Լրացուցիչ պայմանները 1–6',
      '§1 վերնագիրը, 1) μ<sub>l</sub>, H<sub>F</sub>*, L<sub>2</sub>*'],
     'Թվերը առաջադրանքի աղյուսակից են։ μ<sub>l</sub>-ը ընտրված է այնպես, որ մեխանիզմը տեղավորվի A3 թերթում։'),
    ('p11', NB.p11, 'Էջ 11', '§1-ի շարունակությունը և §2-ի սկիզբը',
     ['EF, ED, CD գծագրային երկարությունները',
      '2) AB և BC համակարգը և լուծումը',
      'l<sub>AB</sub>, l<sub>BC</sub> իրական երկարությունները',
      '§2 վերնագիրը, 1) V<sub>B</sub>, 2) (1) հավասարումը նշանների աղյուսակով'],
     f'AC₀ = {n(C.AC0)} մմ և AC₀′ = {n(C.AC0P)} մմ <b>չափեք թերթ 1-ից</b> (թերթ 1-ի 8-րդ քայլը), նոր միայն գրեք համակարգը։'),
    ('p12', NB.p12, 'Էջ 12', '§2. նմանություն, V<sub>F</sub>, մասշտաբ, դիրք 2',
     ['3) pe-ի բանաձևը նմանությամբ, DE/CD = 1,111',
      '4) (4) հավասարումը V<sub>F</sub>-ի համար՝ աղյուսակով',
      '5) bs₂ = cs₂, 6) μ<sub>V</sub>, pb = 50 մմ',
      f'7) դիրք {P2}-ի բոլոր արագությունները և ω₂'],
     'pc, pf, ps₂, bc, ef հատվածները <b>չափեք թերթ 2-ի</b> «Դիրք 2» պլանից։ pe-ն չի չափվում, հաշվվում է pc·1,111։'),
    ('p13', NB.p13, 'Էջ 13', '§2. ω₃, ω₄ և 8 դիրքերի աղյուսակը',
     ['ω₃ և ω₄՝ դիրք 2-ի համար',
      'Աղյուսակը՝ 0–7 դիրքերի արագություններով և ω-ներով',
      'Պտտման ուղղությունները (↻ / ↺)'],
     'Աղյուսակի տողերը ներդիրի (13ա) հաշվարկներից են։ Ընդգծված տողը՝ աշխատանքային (2-րդ) դիրքն է։'),
    ('p13a', NB.insert, 'Էջ 13ա', 'Ներդիր. 7-րդ կետը բոլոր դիրքերի համար',
     ['Յուրաքանչյուր դիրքի համար՝ չափված հատվածները և արագությունները',
      'ω₂, ω₃, ω₄ և նրանց ուղղությունները'],
     'Սա էջ 13-ի աղյուսակի հաշվարկն է։ Եթե դասախոսը չի պահանջում բոլոր դիրքերի մանրամասն հաշվարկը, կարող եք այն անել սևագրում և տետրում գրել միայն աղյուսակը։ Հատվածները չափեք թերթ 2-ի համապատասխան պլանից։'),
    ('p14', NB.p14, 'Էջ 14', '§3. արագացումների պլանի սկիզբը',
     ['§3 վերնագիրը, «դիրք 2-ի համար»',
      '1) a<sub>B</sub>, ինչու է a<sub>B</sub><sup>t</sup> = 0',
      '2) C կետի երկու վեկտորական հավասարումը՝ նշանների աղյուսակներով',
      'a<sub>CB</sub><sup>n</sup> և a<sub>CD</sub><sup>n</sup>'],
     'ω₂ և ω₃ արժեքները վերցրեք էջ 12–13-ից (դիրք 2)։'),
    ('p15', NB.p15, 'Էջ 15', '§3. մասշտաբը և պլանի կառուցումը',
     ['(3) հավասարումը, 3) μ<sub>a</sub>, πb = 70 մմ',
      'bn₂ և πn₃ հատվածները (մմ)',
      '4) πe՝ նմանությամբ, 5) ∠cπe = 50°',
      '6) a<sub>F</sub>-ի հավասարումը, a<sub>FE</sub><sup>n</sup>, en₄'],
     'bn₂, πn₃, en₄ հատվածները <b>հաշվվում են</b> (չեն չափվում). դրանցով կառուցեք արագացումների պլանը թերթ 1-ի աջ ներքևում։'),
    ('p16', NB.p16, 'Էջ 16', '§3. արագացումները և անկյունային արագացումները',
     ['a<sub>C</sub>, a<sub>E</sub>, a<sub>F</sub>, a<sub>S₂</sub>',
      'Շոշափող արագացումները a<sup>t</sup>',
      'ε₂, ε₃, ε₄ և նրանց ուղղությունները'],
     'πc, πf, πs₂, n₂c, n₃c, n₄f հատվածները <b>չափեք թերթ 1-ի</b> արագացումների պլանից։ n₃c-ն և n₄f-ը գրեթե զրո են. սա սխալ չէ։'),
    ('p17', NB.p17, 'Էջ 17', '§4. բերված մոմենտի բանաձևը',
     ['§4 վերնագիրը և հզորությունների հավասարությունը',
      '1) M<sub>P</sub>-ի բանաձևը G₂, G₅, F<sub>r</sub> ուժերով',
      '2) μ<sub>F</sub> և F<sub>r</sub> = y<sub>j</sub>·μ<sub>F</sub>',
      '3) V = հատված·μ<sub>V</sub>, μ<sub>V</sub>/ω₁ և (5) բանաձևը'],
     'G₂, G₅՝ առաջադրանքի աղյուսակից։ α₅ = 0° 1–4 դիրքերում, 180°՝ 5–7-ում։ F<sub>r</sub> ≠ 0 միայն 2, 3, 4 դիրքերում (1-ում ուժը դեռ չի սկսվել)։'),
    ('p18', NB.p18, 'Էջ 18', '§4. աղյուսակը և մասշտաբները',
     ['Դիրք 2-ի հաշվարկը՝ օրինակ',
      'Աղյուսակը 0–8 դիրքերի համար',
      '4) μ<sub>M</sub> և μ<sub>φ</sub>',
      '5) գծագրական չափերը (M<sub>P</sub>)<sup>գծ</sup>'],
     'ps₂·cos α₂-ը <b>չափեք թերթ 2-ի պլաններից</b>. s₂-ից իջեցրեք ուղղահայաց p-ով անցնող ուղղաձիգին (p-ից ներքև՝ +, վերև՝ −)։ pf-ը՝ նույն պլաններից, y<sub>j</sub>-ն՝ թերթ 1-ի F<sub>re</sub> գրաֆիկից։ Ստուգում. 2–4 դիրքերում M<sub>P</sub> &lt; 0, մեծագույնը՝ 2-րդ կամ 3-րդ դիրքում։'),
]

def page_sec(pid, body, title, sub, items, src):
    lis = ''.join(f'<li>{t}</li>' for t in items)
    return f'''
<section class="tp" id="{pid}" aria-labelledby="{pid}-h">
  <div class="tp-head">
    <div><h2 id="{pid}-h">{title}</h2><p>{sub}</p></div>
    <label class="done"><input type="checkbox" data-page="{pid}"><span>Գրված է</span></label>
  </div>
  <div class="tp-grid">
    <div class="tp-page">{rot(body)}</div>
    <aside class="tp-tips">
      <h3>Այս էջում</h3>
      <ol>{lis}</ol>
      <h3>Որտեղից են թվերը</h3>
      <p>{src}</p>
    </aside>
  </div>
</section>'''

nav = ''.join(f'<a href="#{pid}" data-nav="{pid}"><span class="ck" aria-hidden="true"></span>{t}<small>{s}</small></a>' for pid, _, t, s, _, _ in PAGES)
body = ''.join(page_sec(*p) for p in PAGES)

intro = f'''
<section class="intro" id="top">
  <p class="kicker">Տետր · էջ 10–18</p>
  <h1>Ինչ գրել տետրում</h1>
  <p class="lede">Ստորև յուրաքանչյուր տետրի էջն է՝ լրացված ձեր տարբերակի թվերով, ճիշտ այն հերթականությամբ և նշանակումներով, ինչ օրինակում։ Կողքին գրված է, թե ինչ կա էջում և որտեղից վերցնել չափվող թվերը։ Արտագրելուց հետո նշեք «Գրված է»։</p>
  <div class="rules">
    <div><b>Թավ և ընդգծված</b><span>վերջնական արդյունքն է. տետրում նույնպես ընդգծեք։</span></div>
    <div><b>Չափվող հատվածներ</b><span>(pc, bc, pf, πc…) վերցվում են A3 թերթերից. ձեր չափումը կարող է տարբերվել ±0,5 մմ-ով, այդ դեպքում վերահաշվեք նույն բանաձևով։</span></div>
    <div><b>Հաշվվող հատվածներ</b><span>pe, πe, bn₂, πn₃, en₄՝ բանաձևով, չեն չափվում։</span></div>
    <div><b>Հերթականություն</b><span>§1-ի կետ 2-ից առաջ գծեք թերթ 1-ի դիրքերը, §2-ի կետ 7-ից առաջ՝ թերթ 2-ը, §4-ից առաջ՝ F<sub>re</sub> գրաֆիկը։</span></div>
  </div>
  <p class="prog" aria-live="polite"></p>
</section>'''

CSS = r'''
:root{
  --ground:#EDF0EF;--surface:#F9FBFA;--surface-2:#E3E8E7;--ink:#1B2225;--ink-2:#53616A;--ink-3:#77848B;
  --rule:#CAD3D2;--rule-2:#DCE3E2;--mm:#C45F3B;--mm-ink:#9C4424;--pen:#21539D;--verd:#206E57;--verd-soft:#D8ECE4;--hi:#F3DE5B;--hi-ink:#1B2225;
  --f-sans:"Noto Sans Armenian",system-ui,-apple-system,"Segoe UI",sans-serif;
  --f-math:"STIX Two Text","Noto Sans Armenian","Times New Roman",serif;--toph:56px;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ground:#101416;--surface:#161B1E;--surface-2:#1D2326;--ink:#E1E6E7;--ink-2:#9BA7AD;--ink-3:#75828A;
  --rule:#2B3438;--rule-2:#232A2E;--mm:#EA8A62;--mm-ink:#F2A688;--pen:#8FB4EA;--verd:#74C7AB;--verd-soft:#15291F;--hi:#6E6118;--hi-ink:#F4EBC0;
}}
:root[data-theme="dark"]{
  --ground:#101416;--surface:#161B1E;--surface-2:#1D2326;--ink:#E1E6E7;--ink-2:#9BA7AD;--ink-3:#75828A;
  --rule:#2B3438;--rule-2:#232A2E;--mm:#EA8A62;--mm-ink:#F2A688;--pen:#8FB4EA;--verd:#74C7AB;--verd-soft:#15291F;--hi:#6E6118;--hi-ink:#F4EBC0;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--f-sans);font-size:16px;line-height:1.6}
a{color:var(--pen)}
mark{background:var(--hi);color:var(--hi-ink);padding:0 .28em;border-radius:2px}
sub,sup{font-size:.72em;line-height:0}
.top{position:sticky;top:0;z-index:30;height:var(--toph);display:flex;align-items:center;gap:14px;padding:0 20px;background:var(--surface);border-bottom:1px solid var(--rule)}
.back{display:grid;place-items:center;width:34px;height:34px;border:1px solid var(--rule);border-radius:8px;color:var(--ink);text-decoration:none;flex:none}
.top-t{flex:1;min-width:0;display:flex;flex-direction:column;line-height:1.25}
.top-t b{font-size:1rem;font-weight:650;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.top-t span{font-size:.8rem;color:var(--ink-3)}
.top-work{flex:none;padding:7px 14px;border-radius:8px;border:1px solid var(--rule);color:var(--ink);text-decoration:none;font-size:.9rem;font-weight:600}
.theme-btn{flex:none;width:36px;height:36px;border:1px solid var(--rule);border-radius:8px;background:var(--surface);color:var(--ink);font-size:1.05rem;cursor:pointer}
.shell{display:grid;grid-template-columns:230px minmax(0,1fr);max-width:1480px;margin:0 auto}
.side{position:sticky;top:var(--toph);align-self:start;max-height:calc(100vh - var(--toph));overflow:auto;padding:20px 12px 30px 18px;border-right:1px solid var(--rule)}
.side h4{font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);margin:0 0 8px 10px;font-weight:600}
.side a{display:grid;grid-template-columns:20px 1fr;column-gap:8px;padding:7px 10px;border-radius:7px;color:var(--ink);text-decoration:none;font-weight:600;font-size:.95rem;line-height:1.3}
.side a small{grid-column:2;font-weight:400;font-size:.78rem;color:var(--ink-3)}
.side a:hover{background:var(--surface-2)}
.side a[aria-current="true"]{background:var(--surface-2)}
.ck{grid-row:span 2;width:18px;height:18px;margin-top:1px;border:1.5px solid var(--rule);border-radius:50%}
.side a.is-done .ck{background:var(--verd);border-color:var(--verd);box-shadow:inset 0 0 0 3px var(--surface)}
main{padding:30px 36px 90px;min-width:0}
.kicker{font-size:.74rem;letter-spacing:.09em;text-transform:uppercase;color:var(--verd);font-weight:600;margin:0 0 6px}
h1{font-size:clamp(1.6rem,3vw,2.3rem);margin:0 0 10px;line-height:1.15}
.lede{color:var(--ink-2);font-size:1.03rem;max-width:74ch;margin:0 0 18px}
.rules{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:0 0 14px}
.rules>div{padding:14px 16px;border:1px solid var(--rule);border-radius:10px;background:var(--surface);font-size:.9rem;display:flex;flex-direction:column;gap:4px}
.rules span{color:var(--ink-2)}
.prog{font-weight:600;color:var(--verd);margin:0}
.tp{margin-top:44px;padding-top:22px;border-top:1px solid var(--rule);scroll-margin-top:calc(var(--toph) + 8px)}
.tp-head{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;margin-bottom:14px}
.tp-head h2{font-size:1.6rem;margin:0;line-height:1.2}
.tp-head p{margin:2px 0 0;color:var(--ink-2)}
.done{display:inline-flex;align-items:center;gap:8px;padding:8px 14px;border:1px solid var(--rule);border-radius:999px;background:var(--surface);cursor:pointer;font-weight:600;font-size:.92rem;flex:none;user-select:none}
.done input{width:18px;height:18px;margin:0;accent-color:var(--verd)}
.done:has(input:checked){background:var(--verd-soft);border-color:var(--verd);color:var(--verd)}
.tp-grid{display:grid;grid-template-columns:minmax(0,1fr) 290px;gap:24px;align-items:start}
.tp-page .npage{min-height:0;grid-column:auto}
.tp-tips{position:sticky;top:calc(var(--toph) + 16px);padding:16px 18px;border:1px solid var(--rule);border-left:3px solid var(--verd);border-radius:10px;background:var(--surface);font-size:.92rem}
.tp-tips h3{font-size:.78rem;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-3);margin:0 0 6px}
.tp-tips h3+ol{margin-bottom:14px}
.tp-tips ol{padding-left:1.2em;margin:0;display:grid;gap:4px}
.tp-tips p{margin:0;color:var(--ink-2)}
.endnav{margin-top:50px;padding-top:20px;border-top:1px solid var(--rule);display:flex;flex-wrap:wrap;gap:12px}
.endnav a{padding:10px 16px;border:1px solid var(--rule);border-radius:10px;background:var(--surface);color:var(--ink);text-decoration:none;font-weight:600}
@media (max-width:1100px){.rules{grid-template-columns:1fr 1fr}.tp-grid{grid-template-columns:minmax(0,1fr)}.tp-tips{position:static;order:-1}}
@media (max-width:900px){
  .shell{grid-template-columns:minmax(0,1fr)}
  .side{min-width:0;top:var(--toph);z-index:25;max-height:none;display:flex;gap:4px;overflow-x:auto;padding:8px 12px;border-right:0;border-bottom:1px solid var(--rule);background:var(--ground);scrollbar-width:none}
  .side::-webkit-scrollbar{display:none}
  .side h4,.side a small{display:none}
  .side a{flex:none;white-space:nowrap;display:flex;align-items:center;gap:6px;padding:6px 11px;font-size:.88rem}
  .ck{width:14px;height:14px}
  main{padding:22px 16px 70px}
  .tp{scroll-margin-top:calc(var(--toph) + 52px)}
}
@media (max-width:560px){.rules{grid-template-columns:1fr}.top{padding:0 12px;gap:10px}.top-work{padding:7px 10px;font-size:.82rem}.tp-head{flex-direction:column;align-items:flex-start}}
@media print{.top,.side,.tp-tips,.done,.intro,.endnav{display:none}.shell{display:block}main{padding:0}.tp{border:0;margin:0;break-after:page}.tp-head{display:none}}
'''

JS = r'''
(() => {
  const ROOT = document.documentElement, TKEY = 'tmm-theme';
  const isDark = () => (ROOT.getAttribute('data-theme') || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')) === 'dark';
  const label = () => document.querySelectorAll('[data-theme-toggle]').forEach(b => { b.textContent = isDark() ? '☀' : '☾'; b.title = isDark() ? 'Լուսավոր ռեժիմ' : 'Մութ ռեժիմ'; });
  document.addEventListener('click', e => {
    if (!e.target.closest('[data-theme-toggle]')) return;
    const t = isDark() ? 'light' : 'dark'; ROOT.setAttribute('data-theme', t);
    try { localStorage.setItem(TKEY, t); } catch (err) {}
    label();
  });
  label();

  const KEY = 'tmm-variant1-tetr';
  let done = {};
  try { done = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { done = {}; }
  const boxes = [...document.querySelectorAll('input[data-page]')], prog = document.querySelector('.prog');
  const paint = () => {
    boxes.forEach(b => { const a = document.querySelector('[data-nav="' + b.dataset.page + '"]'); if (a) a.classList.toggle('is-done', b.checked); });
    const k = boxes.filter(b => b.checked).length;
    if (prog) prog.textContent = k === boxes.length ? '✓ Բոլոր ' + k + ' էջերը գրված են' : 'Գրված է ' + k + ' / ' + boxes.length + ' էջ';
  };
  boxes.forEach(b => {
    b.checked = !!done[b.dataset.page];
    b.addEventListener('change', () => { if (b.checked) done[b.dataset.page] = 1; else delete done[b.dataset.page]; try { localStorage.setItem(KEY, JSON.stringify(done)); } catch (e) {} paint(); });
  });
  paint();

  const links = [...document.querySelectorAll('[data-nav]')], side = document.querySelector('.side');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => es.forEach(en => {
      if (!en.isIntersecting) return;
      links.forEach(a => a.setAttribute('aria-current', String(a.dataset.nav === en.target.id)));
      const cur = links.find(a => a.dataset.nav === en.target.id);
      if (cur && side && innerWidth <= 900) side.scrollLeft = cur.offsetLeft - (side.clientWidth - cur.offsetWidth) / 2;
    }), { rootMargin: '-30% 0px -60% 0px' });
    document.querySelectorAll('.tp').forEach(s => io.observe(s));
  }
})();
'''

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+Armenian:wdth,wght@62.5..100,400..700&family=STIX+Two+Text:ital,wght@0,400..700;1,400..700&display=swap">'

html = f'''<!doctype html>
<html lang="hy">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Տետրում գրելու · տարբերակ {VAR}</title>
<meta name="description" content="ՄՄՏ, առաջադրանք 2, տարբերակ {VAR}. ինչ գրել տետրում՝ էջ 10–18, տող առ տող">
{FONTS}
<script>try{{var t=localStorage.getItem('tmm-theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t)}}catch(e){{}}</script>
<style>{CSS}{NB.CSS}</style>
</head>
<body>
<header class="top">
  <a class="back" href="./" aria-label="Կուրսային աշխատանքի գլխավոր էջ">←</a>
  <div class="top-t"><b>Տետրում գրելու</b><span>ՄՄՏ · առաջադրանք 2 · տարբերակ <mark>{VAR}</mark></span></div>
  <a class="top-work" href="TMM_Variant1.html">Աշխատանքը</a>
  <button class="theme-btn" type="button" data-theme-toggle aria-label="Փոխել լուսավոր/մութ ռեժիմը"></button>
</header>
<div class="shell">
<nav class="side" aria-label="Տետրի էջեր"><h4>Տետրի էջեր</h4>{nav}</nav>
<main>
{intro}
{body}
<nav class="endnav" aria-label="Այլ էջեր"><a href="TMM_Variant1.html#sheet1">A3 թերթ 1</a><a href="TMM_Variant1.html#sheet2">A3 թերթ 2</a><a href="bacatrutyun.html">Բացատրություն</a><a href="#top">↑ Վերև</a></nav>
</main>
</div>
<script>{JS}</script>
</body>
</html>
'''

HERE = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(HERE, '..', 'tetr.html'), 'w').write(html)
print('written tetr.html', len(html), 'bytes')
