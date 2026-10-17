#!/usr/bin/env python3
"""Inline the lecture visuals (viz_core.js, viz.js, viz2.js) into the study page. Safe to run again after editing them."""
import os, re
D = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(D, '..', 'Նյութագիտություն_միջանկյալ_1.html')
html = open(PAGE, encoding='utf-8').read()
viz = ''.join(open(os.path.join(D, f), encoding='utf-8').read() for f in ('viz_core.js', 'viz.js', 'viz2.js'))
block = '<script id="viz">\n' + viz.replace('</', '<\\/') + '</script>\n'

# 1) the visuals script sits right before the app script (the last <script>)
html = re.sub(r'<script id="viz">.*?</script>\n', '', html, flags=re.S)
i = html.rfind('<script>')
html = html[:i] + block + html[i:]

# 2) app hooks: visuals under each lecture section, mounted after the lecture view is bound
hooks = [
    ("${s.figs ? `<div class=\"figs\">${s.figs.map(figHTML).join('')}</div>` : ''}</section>`).join('')}",
     "${s.figs ? `<div class=\"figs\">${s.figs.map(figHTML).join('')}</div>` : ''}${window.vizHTML ? vizHTML(l.id, i) : ''}</section>`).join('')}"),
    ("document.querySelectorAll('[data-zlec]').forEach(a => a.onclick = () => { quizCfg.lec = a.dataset.zlec; quiz = null; });\n}",
     "document.querySelectorAll('[data-zlec]').forEach(a => a.onclick = () => { quizCfg.lec = a.dataset.zlec; quiz = null; });\n  if (window.mountViz) mountViz();\n}")]
for (old, new), mark in zip(hooks, ('vizHTML(l.id, i)', 'mountViz()')):
    if mark not in html:
        assert html.count(old) == 1, old[:60]
        html = html.replace(old, new)
open(PAGE, 'w', encoding='utf-8').write(html)
print(PAGE, len(html) // 1024, 'KB')
