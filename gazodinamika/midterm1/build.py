#!/usr/bin/env python3
"""Build the gas-dynamics midterm-1 study app (single self-contained HTML) from the content modules."""
import base64, json, os, subprocess, tempfile
from content_lectures import LECTURES, FIGS
from content_questions import GROUPS, QUESTIONS, CARDS, QUIZ

D = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(D, '..', 'translation', 'figs')
OUT = os.path.join(D, '..', 'Գազադինամիկա_միջանկյալ_1.html')

def img_uri(name):
    src = os.path.join(FIGDIR, name + '.png')
    with tempfile.NamedTemporaryFile(suffix='.webp') as t:
        subprocess.run(['cwebp', '-quiet', '-q', '82', '-resize', '900', '0', src, '-o', t.name], check=True)
        return 'data:image/webp;base64,' + base64.b64encode(open(t.name, 'rb').read()).decode()

used = {f[0] for L in LECTURES for s in L['sections'] for f in s.get('figs', [])}
IMG = {k: img_uri(v) for k, v in FIGS.items() if k in used}

data = dict(groups=GROUPS, lectures=LECTURES, questions=QUESTIONS, cards=CARDS, quiz=QUIZ)
js = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')

head = open(os.path.join(D, 'head.html'), encoding='utf-8').read()
app = open(os.path.join(D, 'app.js'), encoding='utf-8').read()
html = (head + '<script>// Course content: gas dynamics midterm 1 (24 questions). Text marked class="sup" is a textbook supplement.\n'
        + 'window.DATA = ' + js(data) + ';</script>\n<script>window.IMG=' + js(IMG) + ';</script>\n' + app)
open(OUT, 'w', encoding='utf-8').write(html)
print(OUT, len(html)//1024, 'KB', len(QUESTIONS), 'questions', len(CARDS), 'cards', len(QUIZ), 'quiz')
