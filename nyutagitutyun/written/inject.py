#!/usr/bin/env python3
"""Inline the written model answers ("what to write on the paper") into the study page. Safe to run again after editing them."""
import json, os, re, sys
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
from content_written import WRITTEN

PAGE = os.path.join(D, '..', 'Նյութագիտություն_միջանկյալ_1.html')
html = open(PAGE, encoding='utf-8').read()

# 1) the answers: a script right after the course data, attaching q.w to each question
ids = re.findall(r'\{ id: "([^"]+)", sec:', html)
missing = [i for i in ids if i not in WRITTEN]
assert not missing, missing
js = json.dumps(WRITTEN, ensure_ascii=False).replace('</', '<\\/')
block = ('<script id="written">// Written model answers: what to write on the paper (built by written/inject.py).\n'
         'window.DATA.questions.forEach(q => q.w = (' + js + ')[q.id] || "");</script>\n')
html = re.sub(r'<script id="written">.*?</script>\n', '', html, flags=re.S)
i = html.index('<script>window.IMG=')
html = html[:i] + block + html[i:]

# 2) app hooks (applied once): written answer first in study mode, in the check/exam views and in print
hooks = [
 ("function fullAnswer(q, open){",
  """// The model written answer: what to put on the paper, with every derivation step.
const written = q => `<div class="answer prose wr">${q.w}</div>`;
const writtenDetails = q => `<details class="full"><summary>Ի՞նչ գրել թղթին (օրինակելի գրավոր պատասխան)</summary><div class="full-in">${written(q)}</div></details>`;
const planDetails = q => `<details class="full"><summary>Կարճ պլան (հիմնական կետերը)</summary><div class="full-in"><div class="answer prose">${q.a}</div></div></details>`;
function fullAnswer(q, open){"""),
 ("// Print layout: printQ = {ids, full}; the questions view then shows only these questions, each with its answer plan (and the full answer if full).",
  "// Print layout: printQ = {ids, mode}; the questions view then shows only these questions with the written answer ('w'), the short plan ('plan') or the written answer plus the lecture text ('full')."),
 ("    <div class=\"answer prose\">${q.a}</div>${printQ.full ? answerSecs(q) : ''}</article>`;",
  "    ${printQ.mode==='plan' ? `<div class=\"answer prose\">${q.a}</div>` : written(q)}${printQ.mode==='full' ? answerSecs(q) : ''}</article>`;"),
 ("function printQuestions(ids, full){ printView(() => { printQ = {ids, full}; }, () => { printQ = null; }); }",
  "function printQuestions(ids, mode){ printView(() => { printQ = {ids, mode}; }, () => { printQ = null; }); }"),
 ("${open ? `<div class=\"q-body\"><span class=\"eyebrow\">Պատասխանի պլան</span><div class=\"answer prose\">${q.a}</div>${fullAnswer(q,true)}",
  "${open ? `<div class=\"q-body\"><span class=\"eyebrow\">Ի՞նչ գրել թղթին</span>${written(q)}${planDetails(q)}${fullAnswer(q)}"),
 ("title=\"Տպել այս հարցը պատասխանով A4 թղթի վրա\">", "title=\"Տպել այս հարցի գրավոր պատասխանը A4 թղթի վրա\">"),
 ("${shown[q.id] ? `<span class=\"eyebrow\">2 · Համեմատեք</span>${checklist(q)}${fullAnswer(q)}",
  "${shown[q.id] ? `<span class=\"eyebrow\">2 · Համեմատեք</span>${checklist(q)}${writtenDetails(q)}${fullAnswer(q)}"),
 ("<h2>Գրավոր հարցեր${printQ.full?'':'․ պատասխանների պլաններ'}</h2>",
  "<h2>Գրավոր հարցեր${{w:'․ ինչ գրել թղթին',plan:'․ պատասխանների պլաններ',full:''}[printQ.mode]}</h2>"),
 ("<p class=\"lede\">Նախ <b>Սովորել</b> ռեժիմում կարդացեք հարցը և պատասխանը։",
  "<p class=\"lede\">Նախ <b>Սովորել</b> ռեժիմում կարդացեք հարցը և «Ի՞նչ գրել թղթին» պատասխանը. դա հենց այն է, ինչ պետք է գրել քննությանը՝ սահմանումներ, բանաձևեր քայլ առ քայլ, գծագրեր։"),
 ("<div class=\"row print-row\"><button type=\"button\" class=\"btn small print-btn\" data-pq=\"full\" title=\"Հարց, պատասխանի պլան, դասախոսության տեքստը և նկարները\" ${toPrint().length?'':'disabled'}>🖨 Տպել պատասխաններով (A4)</button><button type=\"button\" class=\"btn small print-btn\" data-pq=\"plan\" title=\"Միայն հարցերը և պատասխանների պլանները, կարճ\" ${toPrint().length?'':'disabled'}>🖨 Տպել միայն պլանները</button>",
  "<div class=\"row print-row\"><button type=\"button\" class=\"btn small print-btn\" data-pq=\"w\" title=\"Հարցերը և գրավոր պատասխանները՝ ինչ գրել թղթին\" ${toPrint().length?'':'disabled'}>🖨 Տպել գրավոր պատասխանները (A4)</button><button type=\"button\" class=\"btn small print-btn\" data-pq=\"plan\" title=\"Միայն հարցերը և պատասխանների պլանները, կարճ\" ${toPrint().length?'':'disabled'}>🖨 Տպել միայն պլանները</button><button type=\"button\" class=\"btn small print-btn\" data-pq=\"full\" title=\"Գրավոր պատասխանը, դասախոսության տեքստը և նկարները\" ${toPrint().length?'':'disabled'}>🖨 Տպել դասախոսության տեքստով</button>"),
 ("printQuestions(toPrint().map(q => q.id), b.dataset.pq==='full'));", "printQuestions(toPrint().map(q => q.id), b.dataset.pq));"),
 ("printQuestions([b.dataset.pq1], true));", "printQuestions([b.dataset.pq1], 'w'));"),
 ("        ${checklist(q)}${fullAnswer(q)}${rateRow(q)}`", "        ${checklist(q)}${writtenDetails(q)}${fullAnswer(q)}${rateRow(q)}`"),
]
if 'const written = q =>' not in html:
    for old, new in hooks:
        assert html.count(old) == 1, old[:70]
        html = html.replace(old, new)

# 3) styles (applied once)
CSS = """/* Written answer ("what to write on the paper"): numbered steps, boxed results, fractions, sketches to draw */
.wr h4{font-size:16px;margin:14px 0 4px}
.wsteps{counter-reset:ws;list-style:none;padding-left:0!important}
.wsteps>li{counter-increment:ws;position:relative;padding-left:30px;margin:6px 0}
.wsteps>li::before{content:counter(ws);position:absolute;left:0;top:1px;width:21px;height:21px;border-radius:50%;background:var(--accent-soft);color:var(--accent);font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center}
.res{border:2px solid var(--accent);border-radius:8px;padding:10px 14px;margin:8px 0 12px;background:var(--surface);text-align:center;font-size:16.5px;overflow-x:auto}
.fx{text-align:center;margin:8px 0 12px;font-size:16px;overflow-x:auto}
.fr{display:inline-flex;flex-direction:column;vertical-align:middle;text-align:center;margin:0 2px;line-height:1.25}
.fr>span:first-child{border-bottom:1px solid currentColor;padding:0 3px}
.fr>span:last-child{padding:0 3px}
.wtbl{max-width:640px}
.sk{margin:8px 12px 12px 0;display:inline-flex;flex-direction:column;gap:4px;max-width:100%;vertical-align:top}
.sk-svg{width:300px;max-width:100%;height:auto;color:var(--ink);font-size:11px;font-family:var(--f-body)}
.sk-svg text{fill:currentColor}
.sk-svg .sm{font-size:9.5px}
.sk-svg .sub{font-size:8px;baseline-shift:sub}
.sk-svg .ax,.sk-svg .arr{stroke:currentColor;stroke-width:1.2;fill:none}
.sk-svg .axh{fill:currentColor}
.sk-svg .arr2{stroke:var(--accent);stroke-width:1.6;fill:none}
.sk-svg .cv{stroke:var(--accent);stroke-width:2.2;fill:none}
.sk-svg .cv2{stroke:var(--heat);stroke-width:2;fill:none}
.sk-svg .cv3{stroke:var(--good);stroke-width:2;fill:none}
.sk-svg .thinc{stroke:var(--accent);stroke-width:1.2;fill:none}
.sk-svg .tie{stroke:var(--bad);stroke-width:1.6;fill:none}
.sk-svg .area{fill:var(--accent-soft);stroke:none}
.sk-svg .dash{stroke:var(--muted);stroke-width:1;stroke-dasharray:3 3;fill:none}
.sk-svg .dim{stroke:var(--muted);stroke-width:1;fill:none}
.sk-svg .pt{fill:var(--accent)}
.sk-svg .wall,.sk-svg .wall2{stroke:currentColor;stroke-width:1.6;fill:none}
.sk-svg .wall2{stroke:var(--accent)}
.sk-svg .mold{fill:var(--sunk);stroke:currentColor;stroke-width:1.2}
.sk-svg .thin{stroke:var(--muted);stroke-width:1;fill:none}
.sk-svg .cavity{fill:var(--surface);stroke:currentColor;stroke-width:1.4}
.sk-svg .mark{stroke:var(--bad);stroke-width:2.4;fill:none}
.sk-svg .atom{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1}
.sk-svg .atom2{fill:var(--heat-soft);stroke:var(--heat);stroke-width:1.2}
.sk-svg .atom3{fill:var(--heat)}
.sk-svg .hole{fill:none;stroke:var(--muted);stroke-width:1;stroke-dasharray:2 2}
.sk-svg .gr{stroke:currentColor;stroke-width:2.2;fill:none;stroke-linecap:round}
.sk-svg .grf{fill:currentColor}
.sk-svg .cell{fill:var(--surface);stroke:var(--muted);stroke-width:.8}
.sk-svg .hatch{fill:var(--muted);fill-opacity:.55;stroke:var(--muted);stroke-width:.8}
.sk-svg .net{stroke:var(--surface);stroke-width:2.6}
.sk figcaption{max-width:300px}
.sk-svg.wide{width:460px}
.sk:has(.wide) figcaption{max-width:460px}
"""
PRINT = """  .wr h4{font-size:11pt;margin:8px 0 2px;break-after:avoid;page-break-after:avoid}
  .wsteps>li,.res,.fx,.sk{break-inside:avoid;page-break-inside:avoid}
  .sk-svg{width:66mm}
  .sk-svg.wide{width:110mm}
"""
if '.wsteps{' not in html:
    a = "/* Print: one lecture or the questions on A4"
    assert html.count(a) == 1
    html = html.replace(a, CSS + a)
    a = "  .pq .full-in .sec h3{font-size:11.5pt}\n"
    assert html.count(a) == 1
    html = html.replace(a, a + PRINT)

# 4) short plans: only the headings of each answer (q.p); the plan view and the plan print use them
from content_plan import PLAN
missing = [i for i in ids if i not in PLAN]
assert not missing, missing
block = ('<script id="plan">// Short answer plans: headings only (built by written/inject.py from content_plan.py).\n'
         'window.DATA.questions.forEach(q => q.p = (' + json.dumps(PLAN, ensure_ascii=False) + ')[q.id] || []);</script>\n')
html = re.sub(r'<script id="plan">.*?</script>\n', '', html, flags=re.S)
i = html.index('<script>window.IMG=')
html = html[:i] + block + html[i:]
plan_hooks = [
 ("const planDetails = q => `<details class=\"full\"><summary>Կարճ պլան (հիմնական կետերը)</summary><div class=\"full-in\"><div class=\"answer prose\">${q.a}</div></div></details>`;",
  "const planList = q => `<ol class=\"plan\">${q.p.map(h => `<li>${h}</li>`).join('')}</ol>`;\n"
  "const planDetails = q => `<details class=\"full\"><summary>Կարճ պլան (միայն վերնագրերը)</summary><div class=\"full-in\"><div class=\"answer prose\">${planList(q)}</div></div></details>`;"),
 ("${printQ.mode==='plan' ? `<div class=\"answer prose\">${q.a}</div>` : written(q)}",
  "${printQ.mode==='plan' ? `<div class=\"answer prose\">${planList(q)}</div>` : written(q)}"),
]
if 'const planList = q =>' not in html:
    for old, new in plan_hooks:
        assert html.count(old) == 1, old[:70]
        html = html.replace(old, new)
if '.plan{' not in html:
    a = "/* Print: one lecture or the questions on A4"
    assert html.count(a) == 1
    html = html.replace(a, ".plan{margin:0;padding-left:1.4em;display:flex;flex-direction:column;gap:4px;font-weight:500}\n" + a)

open(PAGE, 'w', encoding='utf-8').write(html)
print(PAGE, len(html) // 1024, 'KB,', len(ids), 'questions')
