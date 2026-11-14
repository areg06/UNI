"""Export the two A3 drawings: chertej_A3_1/2 .svg (vector), .png (6000 px), .pdf (true A3 scale),
and the A4 graph sheet (1.8–1.9): chertej_A4_graf .svg/.png/.pdf (true A4 scale, millimetre grid).
Run:  python3 export.py      (needs Google Chrome for PNG/PDF)"""
import os, subprocess, tempfile, shutil
import sheet as SH
import graf as GR
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(HERE, '..'))
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
FONTS = "@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400..600&family=Noto+Sans+Armenian:wdth,wght@62.5..100,400..700&family=STIX+Two+Text:ital,wght@0,400..700;1,400..700&display=swap');"
tmp = tempfile.mkdtemp(prefix='chertej_')
def chrome(args):
    ud = os.path.join(tmp, 'profile')
    try:
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', f'--user-data-dir={ud}',
                        '--virtual-time-budget=8000'] + args, timeout=60, capture_output=True)
    except subprocess.TimeoutExpired:
        pass   # headless Chrome sometimes writes the file and then does not exit
    subprocess.run(['pkill', '-f', ud], capture_output=True)
for no, raw in ((1, SH.build('sh')), (2, SH.build2('sh2'))):
    name = f'chertej_A3_{no}'
    svg = raw.replace('<svg class="sheet"', '<svg class="sheet" width="404mm" height="290mm"', 1)
    svg = svg.replace('<defs>', '<style><![CDATA[' + FONTS + SH.SHEET_CSS.replace('width:100%;height:auto;', '') + ']]></style><defs>', 1)
    open(os.path.join(OUT, name + '.svg'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n' + svg)
    png_html = os.path.join(tmp, f'png{no}.html'); pdf_html = os.path.join(tmp, f'pdf{no}.html')
    open(png_html, 'w').write('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#FFFDF8}svg{display:block}</style>'
                              + svg.replace('width="404mm" height="290mm"', 'width="1600" height="1148.5"', 1))
    open(pdf_html, 'w').write('<!doctype html><meta charset="utf-8"><style>@page{size:420mm 297mm;margin:0}html,body{margin:0;width:420mm;height:297mm;background:#FFFDF8;position:relative;overflow:hidden}svg{display:block}</style>'
                              + svg.replace('width="404mm" height="290mm"', 'width="404mm" height="290mm" style="position:absolute;left:8mm;top:3.5mm"', 1))
    if os.path.exists(CHROME):
        chrome(['--window-size=1600,1149', '--force-device-scale-factor=3.75', '--screenshot=' + os.path.join(OUT, name + '.png'), 'file://' + png_html])
        chrome(['--no-pdf-header-footer', '--print-to-pdf-no-header', '--print-to-pdf=' + os.path.join(OUT, name + '.pdf'), 'file://' + pdf_html])
svg = GR.a4_sheet().replace('<svg class="sheet a4"', '<svg class="sheet a4" width="210mm" height="297mm"', 1)
svg = svg.replace('<defs>', '<style><![CDATA[' + FONTS + SH.SHEET_CSS.replace('width:100%;height:auto;', '') + GR.A4_CSS + ']]></style><defs>', 1)
open(os.path.join(OUT, 'chertej_A4_graf.svg'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n' + svg)
a4 = os.path.join(tmp, 'a4.html')
open(a4, 'w').write('<!doctype html><meta charset="utf-8"><style>@page{size:210mm 297mm;margin:0}html,body{margin:0;width:210mm;height:297mm;overflow:hidden;background:#FFFDF8}svg{display:block}</style>' + svg)
if os.path.exists(CHROME):
    chrome(['--no-pdf-header-footer', '--print-to-pdf-no-header', '--print-to-pdf=' + os.path.join(OUT, 'chertej_A4_graf.pdf'), 'file://' + a4])
    png = os.path.join(tmp, 'a4png.html')
    open(png, 'w').write('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#FFFDF8}svg{display:block}</style>' + svg.replace('width="210mm" height="297mm"', 'width="1050" height="1485"', 1))
    chrome(['--window-size=1050,1485', '--force-device-scale-factor=4', '--screenshot=' + os.path.join(OUT, 'chertej_A4_graf.png'), 'file://' + png])
# small previews for the overview cards (macOS sips): thumb_A3_1.jpg, thumb_A3_2.jpg, thumb_A4_graf.jpg
if shutil.which('sips'):
    for src, dst in (('chertej_A3_1.png', 'thumb_A3_1.jpg'), ('chertej_A3_2.png', 'thumb_A3_2.jpg'), ('chertej_A4_graf.png', 'thumb_A4_graf.jpg')):
        if os.path.exists(os.path.join(OUT, src)):
            subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '70', '-Z', '900', os.path.join(OUT, src), '--out', os.path.join(OUT, dst)], capture_output=True)
shutil.rmtree(tmp, ignore_errors=True)
print('exported to', OUT)
