"""Build the variant-1 reducer layout in SVG, A3 PDF, PNG and an HTML viewer.

Run: python3 'meqenamaseri tesutyun/source/harmanadasum.py'
Requires reportlab and pymupdf. REDUCER_FONT can name a Unicode TrueType font;
the defaults include the Armenian-capable Arial Unicode font on the owner's Mac.
All geometry is in paper millimetres, Cartesian, from the grid's bottom-left.
SCALE converts actual millimetres to paper millimetres. Axial stations are explicit
preliminary layout choices, not dimensions supplied by the assignment/textbook.
The coursework's sheet.py supplies the visual convention, not a code dependency.
"""

from pathlib import Path
import html
import math
import os
import re

import pymupdf
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent.parent
NAME = 'harmanadasum_A3'
PW, PH, GW, GH = 420, 297, 380, 270
GX, GY = 22, 9.5                 # grid origin from the page's top-left
SCALE = .5
PAPER = '#FFFDF8'
INK = '#1D2326'
BLUE = '#1F54A3'
X1, X2 = 110., 210.              # shafts I/III and II, paper mm
YI, YII = 105., 170.             # stage centre planes, paper mm
BEARINGS = {
    1: dict(code='36306', d=30, D=72, B=19, C=26.9, C0=20.4),
    2: dict(code='36307', d=35, D=80, B=21, C=35., C0=27.4),
    3: dict(code='309', d=45, D=100, B=25, C=52.7, C0=30.),
}
SUPPORTS = {
    'A₁': (1, X1, 68.75), 'B₁': (1, X1, 133.5),
    'A₂': (2, X2, 69.25), 'B₂': (2, X2, 203.75),
    'A₃': (3, X1, 148.5), 'B₃': (3, X1, 202.75),
}


def n(v, places=2):
    return f'{v:.{places}f}'.rstrip('0').rstrip('.').replace('.', ',')


def f(v):
    return f'{v:.6f}'.rstrip('0').rstrip('.') or '0'


def stage(label, z, module, cosine, widths, x, y):
    d = [module * teeth / cosine for teeth in z]
    return [dict(label=label, part=i+1, z=z[i], m=module, d=d[i],
                 da=d[i]+2*module, df=d[i]-2.5*module,
                 b=widths[i], x=x[i], y=y) for i in range(2)]


GEARS = stage('I', (37, 156), 2., .965, (85, 80), (X1, X2), YI)
GEARS += stage('II', (33, 127), 2.5, 1., (55, 50), (X2, X1), YII)


class Drawing:
    def __init__(self):
        self.items = []
        self.layer = 'drawing'

    def line(self, a, b, color=INK, width=.25, dash=()):
        self.items.append((self.layer, 'line', (a, b, color, width, dash)))

    def rect(self, x, y, w, h, color=INK, width=.3, fill=None, dash=()):
        self.items.append((self.layer, 'rect', (x, y, w, h, color, width, fill, dash)))

    def poly(self, points, color=INK, width=.3, fill=None, closed=False):
        self.items.append((self.layer, 'poly', (points, color, width, fill, closed)))

    def text(self, x, y, text, size=2.7, color=INK, anchor='middle', rotate=0, mask=False):
        self.items.append((self.layer, 'text', (x, y, text, size, color, anchor, rotate, mask)))

    def arrow(self, p, direction):
        dx, dy = direction
        norm = math.hypot(dx, dy)
        dx, dy = dx/norm, dy/norm
        self.poly([p, (p[0]+1.65*dx+.42*dy, p[1]+1.65*dy-.42*dx),
                   (p[0]+1.65*dx-.42*dy, p[1]+1.65*dy+.42*dx)],
                  color=INK, width=.1, fill=INK, closed=True)

    def hdim(self, x0, x1, y, label, ref=None):
        if ref is not None:
            for x in (x0, x1):
                self.line((x, ref), (x, y+2), width=.14)
        self.line((x0, y), (x1, y), width=.17)
        self.arrow((x0, y), (1, 0)); self.arrow((x1, y), (-1, 0))
        self.text((x0+x1)/2, y+2.6, label, size=2.65, mask=True)

    def vdim(self, y0, y1, x, label, ref):
        for y in (y0, y1):
            self.line((ref, y), (x+(-2 if x < ref else 2), y), width=.14)
        self.line((x, y0), (x, y1), width=.17)
        self.arrow((x, y0), (0, 1)); self.arrow((x, y1), (0, -1))
        self.text(x-2.5, (y0+y1)/2, label, size=2.55, rotate=90, mask=True)

    def leader(self, a, elbow, end, label, anchor='start'):
        self.poly([a, elbow, end], width=.18)
        self.text(end[0], end[1]+2.5, label, size=2.65, anchor=anchor, mask=True)


def stepped_shaft(dr, x, steps):
    left = [(x-steps[0][2]*SCALE/2, steps[0][0])]
    right = [(x+steps[0][2]*SCALE/2, steps[0][0])]
    for i, (a, b, diameter) in enumerate(steps):
        if i:
            left.append((x-diameter*SCALE/2, a))
            right.append((x+diameter*SCALE/2, a))
        left.append((x-diameter*SCALE/2, b))
        right.append((x+diameter*SCALE/2, b))
    dr.poly(left+list(reversed(right)), color='#56626A', width=.28,
            fill=PAPER, closed=True)


def build_drawing():
    dr = Drawing()
    dr.layer = 'grid'
    for x in range(GW+1):
        color, width = ('#D97A52', .28) if x % 50 == 0 else (
            ('#E6A283', .15) if x % 10 == 0 else (
                ('#F0C4AE', .10) if x % 5 == 0 else ('#F6DDD0', .065)))
        dr.line((x, 0), (x, GH), color, width)
    for y in range(GH+1):
        color, width = ('#D97A52', .28) if y % 50 == 0 else (
            ('#E6A283', .15) if y % 10 == 0 else (
                ('#F0C4AE', .10) if y % 5 == 0 else ('#F6DDD0', .065)))
        dr.line((0, y), (GW, y), color, width)
    for x in range(0, GW+1, 10):
        dr.text(x, -3.5, str(x), size=2.2, color='#A34E2C')
    for y in range(0, GH+1, 10):
        dr.text(-2.5, y, str(y), size=2.2, color='#A34E2C', anchor='end')
    dr.text(-8, -3.5, 'O', size=2.4, color='#A34E2C')

    dr.layer = 'housing'
    left = min(g['x']-g['da']*SCALE/2 for g in GEARS)-2.5
    right = max(g['x']+g['da']*SCALE/2 for g in GEARS)+2.5
    # Radial clearance: chosen 5 actual mm. Wall delta_1: calculated 8 mm.
    dr.rect(left-4, 64, right-left+8, 145, color='#7C878C', width=.35)
    dr.rect(left, 68, right-left, 137, color='#7C878C', width=.2)
    dr.text(43, 197, 'δ₁ = 8', size=2.6, color='#56626A', mask=True)
    dr.text(42, 73, '5 մմ բացակ', size=2.3, color='#56626A', mask=True)

    dr.layer = 'shafts'
    stepped_shaft(dr, X1, [(36, 60, 25), (60, 79, 30), (79, 128.75, 35), (128.75, 139, 30)])
    stepped_shaft(dr, X2, [(61, 64, 30), (64, 79, 35), (79, 193.5, 40), (193.5, 209, 35)])
    stepped_shaft(dr, X1, [(141.5, 156, 45), (156, 187, 50), (187, 213, 45), (213, 237, 40)])

    dr.layer = 'gears'
    for g in GEARS:
        x, y, b = g['x'], g['y'], g['b']*SCALE
        dr.rect(x-g['da']*SCALE/2, y-b/2, g['da']*SCALE, b, width=.45)
        for sign in (-1, 1):
            dr.line((x+sign*g['d']*SCALE/2, y-b/2-1),
                    (x+sign*g['d']*SCALE/2, y+b/2+1), BLUE, .22, (4, 1, .6, 1))
            dr.line((x+sign*g['df']*SCALE/2, y-b/2),
                    (x+sign*g['df']*SCALE/2, y+b/2), '#7C878C', .14)

    dr.layer = 'supports'
    for name, (shaft, x, y) in SUPPORTS.items():
        b = BEARINGS[shaft]
        outer, inner, height = b['D']*SCALE/2, b['d']*SCALE/2, b['B']*SCALE
        for a in (x-outer, x+inner):
            width = outer-inner
            dr.rect(a, y-height/2, width, height, width=.32, fill=PAPER)
            if shaft in (1, 2):
                # Schematic angular-contact symbol, not the actual raceway section.
                # Its direction reverses between opposite supports.
                direction = 1 if name.startswith('A') else -1
                dr.line((a+.6, y-direction*(height/2-.6)),
                        (a+width-.6, y+direction*(height/2-.6)), width=.28)
                dr.line((a+.6, y+direction*(height/2-.6)),
                        (a+width-.6, y-direction*(height/2-.6)), '#7C878C', .14, (1, .6))
            else:
                dr.line((a+.5, y-height/2+.5), (a+width-.5, y+height/2-.5), width=.25)
                dr.line((a+.5, y+height/2-.5), (a+width-.5, y-height/2+.5), width=.25)
        offset = -outer-4 if shaft != 2 else outer+4
        dr.text(x+offset, y, name, size=2.8, anchor='end' if shaft != 2 else 'start', mask=True)
    # Mark the undetailed inner-support region without inventing a bearing carrier.
    dr.rect(X1-29, 126.5, 58, 30, color='#8A959A', width=.18, dash=(1.8, 1))

    dr.layer = 'axes'
    for x in (X1, X2):
        dr.line((x, 29), (x, 241), '#46505A', .18, (6, 1.2, 1, 1.2))
    for y in (YI, YII):
        dr.line((18, y), (300, y), '#8A959A', .15, (6, 1.2, 1, 1.2))

    dr.layer = 'dimensions'
    dr.hdim(X1, X2, 244, 'a<sub>w</sub><sup>I</sup> = a<sub>w</sub><sup>II</sup> = 200', ref=211)
    for g in GEARS:
        x, y = g['x'], g['y']
        dr.hdim(x-g['d']*SCALE/2, x+g['d']*SCALE/2, y+3,
                f'd<sub>{g["part"]}</sub><sup>{g["label"]}</sup> = {n(g["d"])}')
    # Gear face-width dimensions, placed beyond each relevant gear outline.
    dr.vdim(YI-85*SCALE/2, YI+85*SCALE/2, 78, 'b<sub>w1</sub><sup>I</sup> = 85', X1-GEARS[0]['da']*SCALE/2)
    dr.vdim(YI-80*SCALE/2, YI+80*SCALE/2, 302, 'b<sub>w2</sub><sup>I</sup> = 80', X2+GEARS[1]['da']*SCALE/2)
    dr.vdim(YII-55*SCALE/2, YII+55*SCALE/2, 242, 'b<sub>w1</sub><sup>II</sup> = 55', X2+GEARS[2]['da']*SCALE/2)
    dr.vdim(YII-50*SCALE/2, YII+50*SCALE/2, 15, 'b<sub>w2</sub><sup>II</sup> = 50', X1-GEARS[3]['da']*SCALE/2)

    dr.layer = 'labels'
    dr.text(190, 261, 'ՀԱՄԱՌԱՆՑՔ ՌԵԴՈՒԿՏՈՐԻ ՆԱԽՆԱԿԱՆ ՀԱՐՄԱՐԱԴԱՍՈՒՄ', size=4.)
    dr.text(190, 254.5, 'Առաջադրանք 2 · տարբերակ 1 · A3 · M 1:2 · չափերը՝ իրական մմ-ով', size=2.9)
    dr.text(260, 95, 'I · շեղատամ', size=3.)
    dr.text(71, 164, 'II · ուղղատամ', size=3.)
    for g in GEARS:
        x,y=g['x'],g['y']
        dr.line((x-.7,y),(x+.7,y),BLUE,.25)
        dr.line((x,y-.7),(x,y+.7),BLUE,.25)
        dr.text(x+2.5,y-4.5,f'O<sub>{g["part"]}</sub><sup>{g["label"]}</sup>',
                size=2.4,color=BLUE,anchor='start',mask=True)
    dr.text(X1, 31, 'I · Մուտք', size=3., mask=True)
    dr.text(X1, 240, 'III · Ելք', size=3., mask=True)
    dr.text(X2+14, 216, 'II', size=3., mask=True)
    dr.leader((X1-18, 66), (72, 53), (57, 53), '36306', anchor='end')
    dr.leader((X2+20, 68), (256, 53), (271, 53), '36307')
    dr.leader((X1+25, 203), (155, 221), (168, 221), '309')
    dr.text(190, 45, 'Անիվների ու առանցքակալների գաբարիտները՝ մասշտաբով։', size=2.7)
    dr.text(190, 39, 'Առանցքային դիրքերն ընդունված են այս նախնական հարմարադասման համար։', size=2.6)
    dr.text(190, 24, 'Կետագծով նշված ներքին հենարանների հանգույցը դեռ պետք է կառուցել։', size=2.5, color='#56626A')

    dr.layer = 'notes'
    dr.line((309, 55), (309, 234), '#AAB2B4', .2)
    notes = [
        (236, 'Ատամնազույգեր', 3.1),
        (229, 'I · z = 37 / 156 · m<sub>n</sub> = 2', 2.6),
        (223, 'd = 76,68 / 323,32', 2.6),
        (217, 'b = 85 / 80 · β = 15,20°', 2.6),
        (207, 'II · z = 33 / 127 · m = 2,5', 2.6),
        (201, 'd = 82,5 / 317,5', 2.6),
        (195, 'b = 55 / 50 · β = 0°', 2.6),
        (183, 'Միջին սերիայի առանցքակալներ', 2.8),
        (176, 'I · 36306 · 30 × 72 × 19', 2.5),
        (170, 'II · 36307 · 35 × 80 × 21', 2.5),
        (164, 'III · 309 · 45 × 100 × 25', 2.5),
        (157, 'I և II՝ շառավղա-հենարանային', 2.4),
        (151, 'III՝ շառավղային', 2.4),
        (139, 'Լիսեռներ՝ d / dառ / dան', 2.8),
        (132, 'I · 25 / 30 / 35', 2.6),
        (126, 'II · 30 / 35 / 40', 2.6),
        (120, 'III · 40 / 45 / 50', 2.6),
        (108, 'Սև՝ գագաթային եզրագիծ', 2.5),
        (102, 'Կապույտ՝ բաժանարար տրամագիծ', 2.4),
        (96, 'Մոխրագույն՝ ոտքային եզրագիծ', 2.4),
        (84, 'Ցանցի բջիջը՝ 1 × 1 մմ', 2.7),
        (77, '1 մմ թուղթ = 2 մմ իրական չափ', 2.5),
        (65, 'Հենարանների նշանները պայմանական են։', 2.2),
        (59, 'Արտադրական հավաքական գծագիր չէ։', 2.3),
    ]
    for y, text, size in notes:
        dr.text(315, y, text, size=size, anchor='start')

    dr.layer = 'frame'
    dr.line((20, 12), (120, 12), width=.4)
    for x in range(20, 121, 10):
        dr.line((x, 10.5), (x, 13.5), width=.25)
    dr.text(70, 17, '100 մմ թղթի վրա', size=2.7)
    dr.text(20, 4, 'Տպել A3 · 100% / «Իրական չափ» · Չհարմարեցնել էջին', size=2.45, anchor='start')
    dr.rect(280, 3, 100, 16, width=.4, fill=PAPER)
    dr.line((280, 11), (380, 11), width=.25)
    dr.line((348, 3), (348, 19), width=.25)
    dr.text(314, 15, 'Մեքենամասերի տեսություն', size=2.6)
    dr.text(314, 7, 'Ռեդուկտորի հարմարադասում', size=2.6)
    dr.text(364, 15, 'Տարբերակ 1', size=2.6)
    dr.text(364, 7, 'A3 · M 1:2', size=2.6)
    return dr


def find_font():
    candidates = [os.environ.get('REDUCER_FONT', ''),
                  '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
                  '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            pdfmetrics.registerFont(TTFont('DrawingUnicode', candidate))
            armenian=Path('/System/Library/Fonts/NotoSansArmenian.ttc')
            if armenian.exists():
                # This macOS collection stores the regular 400-weight face at index 6.
                pdfmetrics.registerFont(TTFont('DrawingArmenian',str(armenian),subfontIndex=6))
            return
    raise RuntimeError('Set REDUCER_FONT to an Armenian-capable Unicode TrueType font.')


def text_runs(text, size):
    """Small sub/sup runs keep mathematical indices portable in SVG and PDF."""
    runs = []
    for match in re.finditer(r'<(sub|sup)>(.*?)</\1>|([^<]+)', text):
        if match[3]:
            runs.append((match[3],size,0))
        else:
            runs.append((match[2],size*.7,size*(-.3 if match[1]=='sub' else .5)))
    result=[]
    for run,run_size,offset in runs:
        for fragment in re.findall(r'[\u0530-\u058f]+|[^\u0530-\u058f]+',run):
            font=('DrawingArmenian' if 0x530<=ord(fragment[0])<=0x58f
                  and 'DrawingArmenian' in pdfmetrics.getRegisteredFontNames() else 'DrawingUnicode')
            result.append((fragment,run_size,offset,font))
    return result


def text_width(text, size):
    return sum(pdfmetrics.stringWidth(run, font, run_size)
               for run,run_size,_,font in text_runs(text,size))


def svg_style(color, width, fill=None, dash=()):
    return (f' stroke="{color}" stroke-width="{f(width)}" fill="{fill or "none"}"'
            + (f' stroke-dasharray="{" ".join(map(f, dash))}"' if dash else ''))


def make_svg(dr):
    layers = {}
    for layer, kind, args in dr.items:
        parts = layers.setdefault(layer, [])
        if kind == 'line':
            a, b, color, width, dash = args
            parts.append(f'<line x1="{f(a[0])}" y1="{f(GH-a[1])}" x2="{f(b[0])}" y2="{f(GH-b[1])}"{svg_style(color,width,dash=dash)}/>')
        elif kind == 'rect':
            x, y, w, h, color, width, fill, dash = args
            parts.append(f'<rect x="{f(x)}" y="{f(GH-y-h)}" width="{f(w)}" height="{f(h)}"{svg_style(color,width,fill,dash)}/>')
        elif kind == 'poly':
            points, color, width, fill, closed = args
            path = 'M'+' L'.join(f'{f(x)} {f(GH-y)}' for x,y in points)+(' Z' if closed else '')
            parts.append(f'<path d="{path}"{svg_style(color,width,fill)}/>')
        else:
            x, y, text, size, color, anchor, rotate, mask = args
            w = text_width(text, size)
            start = {'start': 0, 'middle': -w/2, 'end': -w}[anchor]
            parts.append(f'<g transform="translate({f(x)} {f(GH-y)}) rotate({f(-rotate)})">')
            if mask:
                parts.append(f'<rect x="{f(start-.65)}" y="{f(-size*.62)}" width="{f(w+1.3)}" height="{f(size*1.12)}" fill="{PAPER}"/>')
            cursor=start
            for run,run_size,offset,font in text_runs(text,size):
                parts.append(f'<text x="{f(cursor)}" y="{f(-offset)}" dominant-baseline="central" font-size="{f(run_size)}" fill="{color}">{html.escape(run)}</text>')
                cursor+=pdfmetrics.stringWidth(run,font,run_size)
            parts.append('</g>')
    body = ''.join(f'<g data-layer="{key}">{"".join(parts)}</g>' for key,parts in layers.items())
    return (f'<svg id="layout" xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297" role="img" aria-labelledby="drawing-title drawing-desc">'
            '<title id="drawing-title">Ռեդուկտորի նախնական հարմարադասում՝ A3, M 1:2</title>'
            '<desc id="drawing-desc">Համառանցք երկաստիճան ռեդուկտոր, 200 մմ միջառանցքային հեռավորություն, միջին սերիայի 36306, 36307 և 309 առանցքակալներ։ Ցանցը՝ մեկ միլիմետր։</desc>'
            '<style>text{font-family:"Noto Sans Armenian","Arial Unicode MS",Arial,sans-serif}g[hidden]{display:none}</style>'
            f'<rect width="420" height="297" fill="{PAPER}"/>'
            f'<g transform="translate({GX} {GY})">{body}</g></svg>')


def make_pdf(dr):
    path = OUT / f'{NAME}.pdf'
    c = canvas.Canvas(str(path), pagesize=(PW*mm, PH*mm), pageCompression=1,
                      initialFontName='DrawingUnicode')
    c.setTitle('Ռեդուկտորի նախնական հարմարադասում · A3 · M 1:2')
    c.setAuthor('UNI · Տարբերակ 1')
    c.setFillColor(HexColor(PAPER)); c.rect(0, 0, PW*mm, PH*mm, stroke=0, fill=1)
    c.translate(GX*mm, (PH-GY-GH)*mm); c.scale(mm, mm)
    for layer, kind, args in dr.items:
        c.saveState()
        if kind == 'text':
            x, y, text, size, color, anchor, rotate, mask = args
            w = text_width(text, size)
            start = {'start': 0, 'middle': -w/2, 'end': -w}[anchor]
            c.translate(x, y); c.rotate(rotate)
            if mask:
                c.setFillColor(HexColor(PAPER))
                c.rect(start-.65, -size*.5, w+1.3, size*1.12, stroke=0, fill=1)
            c.setFillColor(HexColor(color))
            cursor=start
            for run,run_size,offset,font in text_runs(text,size):
                c.setFont(font,run_size)
                c.drawString(cursor, -run_size*.34+offset, run)
                cursor+=pdfmetrics.stringWidth(run,font,run_size)
        else:
            if kind == 'line':
                a, b, color, width, dash = args
                c.setStrokeColor(HexColor(color)); c.setLineWidth(width); c.setDash(dash)
                c.line(*a, *b)
            elif kind == 'rect':
                x,y,w,h,color,width,fill,dash = args
                c.setStrokeColor(HexColor(color)); c.setLineWidth(width); c.setDash(dash)
                if fill:c.setFillColor(HexColor(fill))
                c.rect(x,y,w,h,stroke=1,fill=int(bool(fill)))
            else:
                points,color,width,fill,closed = args
                c.setStrokeColor(HexColor(color)); c.setLineWidth(width)
                if fill:c.setFillColor(HexColor(fill))
                p=c.beginPath();p.moveTo(*points[0])
                for point in points[1:]:p.lineTo(*point)
                if closed:p.close()
                c.drawPath(p,stroke=1,fill=int(bool(fill)))
        c.restoreState()
    c.showPage();c.save()
    doc=pymupdf.open(path)
    assert len(doc)==1
    assert abs(doc[0].rect.width/mm-PW)<.001 and abs(doc[0].rect.height/mm-PH)<.001
    doc[0].get_pixmap(dpi=300, alpha=False).save(OUT/f'{NAME}.png')


PAGE_CSS = r'''
:root{color-scheme:light;--ink:#1d2326;--muted:#59676e;--line:#d8dfe1;--blue:#1f54a3}
*{box-sizing:border-box}body{margin:0;background:#f4f5f3;color:var(--ink);font:16px/1.6 "Noto Sans Armenian",Arial,sans-serif}
main{max-width:1500px;margin:auto;padding:28px 24px}a{color:var(--blue)}h1{font-size:clamp(1.5rem,3vw,2.1rem);margin:12px 0 6px}h2{font-size:1.2rem;margin:0 0 12px}
p{margin:8px 0 18px}.intro{max-width:950px;color:var(--muted)}.bar{display:flex;gap:12px;flex-wrap:wrap;align-items:center;justify-content:space-between;margin:20px 0 10px}
.downloads,.zoom{display:flex;gap:6px;flex-wrap:wrap}button,.downloads a{font:inherit;font-size:.9rem;border:1px solid var(--line);background:#fff;color:var(--ink);padding:7px 13px;border-radius:5px;text-decoration:none;cursor:pointer}
button[aria-pressed=true]{background:var(--ink);color:white;border-color:var(--ink)}button:focus-visible,a:focus-visible,input:focus-visible{outline:3px solid #9cc2fb;outline-offset:3px}
.layers{display:flex;gap:18px;flex-wrap:wrap;font-size:.9rem;margin:12px 0}.layers label{cursor:pointer}.layers input{accent-color:var(--blue)}
.sheet-scroll{overflow:auto;max-height:82vh;border:1px solid #cdd4d7;background:#e5e7e3}.sheet-inner{width:100%;min-width:700px}.sheet-inner svg{display:block;width:100%;height:auto}
.readout{display:flex;gap:20px;flex-wrap:wrap;padding:9px 12px;background:white;border:1px solid var(--line);border-top:0;font-size:.85rem;font-variant-numeric:tabular-nums;min-height:42px}
.tip{font-size:.87rem;color:var(--muted)}.info{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:28px}.card{padding:22px;background:#fff;border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%;font-size:.87rem}th,td{padding:7px 9px;text-align:left;border-bottom:1px solid var(--line);font-variant-numeric:tabular-nums}th{font-weight:600}.table-wrap{overflow:auto}ol{padding-left:24px}li{margin:9px 0}
.measure-overlay{pointer-events:none}.measure-overlay line,.measure-overlay circle{stroke:#c12a3b;stroke-width:.35;fill:white}.measure-overlay line{stroke-dasharray:2 1}
@media(max-width:850px){main{padding:18px 12px}.info{grid-template-columns:1fr}.card{padding:17px}.sheet-scroll{max-height:70vh}}
@page{size:A3 landscape;margin:0}@media print{html,body{margin:0;background:white;width:420mm;height:297mm}main{padding:0;max-width:none}main>*:not(.sheet-scroll){display:none!important}.sheet-scroll{border:0;max-height:none;overflow:visible}.sheet-inner{width:420mm!important;min-width:0}.sheet-inner svg{width:420mm;height:297mm}.measure-overlay{display:none}}
'''

PAGE_JS = r'''
(() => {
 const svg=document.getElementById('layout'),inner=document.querySelector('.sheet-inner'),scroller=document.querySelector('.sheet-scroll');
 const fmt=v=>v.toFixed(2).replace('.',',');
 document.querySelectorAll('[data-toggle]').forEach(input=>input.addEventListener('change',()=>{
  svg.querySelectorAll('[data-layer="'+input.dataset.toggle+'"]').forEach(g=>g.toggleAttribute('hidden',!input.checked));
 }));
 document.querySelectorAll('[data-zoom]').forEach(button=>button.addEventListener('click',()=>{
  const x=(scroller.scrollLeft+scroller.clientWidth/2)/scroller.scrollWidth,y=(scroller.scrollTop+scroller.clientHeight/2)/scroller.scrollHeight;
  const z=Number(button.dataset.zoom);inner.style.width=100*z+'%';inner.style.minWidth=700*z+'px';
  document.querySelectorAll('[data-zoom]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
  scroller.scrollLeft=x*scroller.scrollWidth-scroller.clientWidth/2;scroller.scrollTop=y*scroller.scrollHeight-scroller.clientHeight/2;
 }));
 const position=e=>{const p=svg.createSVGPoint();p.x=e.clientX;p.y=e.clientY;const m=svg.getScreenCTM();if(!m)return null;const q=p.matrixTransform(m.inverse());return {x:q.x-22,y:270-(q.y-9.5)};};
 const valid=p=>p&&p.x>=0&&p.x<=380&&p.y>=0&&p.y<=270;
 svg.addEventListener('pointermove',e=>{const p=position(e);document.getElementById('coordinates').textContent=valid(p)?'Թղթի վրա՝ x = '+fmt(p.x)+', y = '+fmt(p.y)+' մմ':'Կուրսորը ցանցից դուրս է';});
 const ns='http://www.w3.org/2000/svg',overlay=document.createElementNS(ns,'g');overlay.setAttribute('class','measure-overlay');svg.append(overlay);
 let first=null;
 document.getElementById('clear-measure').addEventListener('click',()=>{first=null;overlay.replaceChildren();document.getElementById('distance').textContent='Չափելու համար ընտրեք երկու կետ։';});
 svg.addEventListener('click',e=>{
  const p=position(e);if(!valid(p))return;
  const point=document.createElementNS(ns,'circle');point.setAttribute('cx',p.x+22);point.setAttribute('cy',270-p.y+9.5);point.setAttribute('r','.8');
  if(!first){overlay.replaceChildren();overlay.append(point);first=p;document.getElementById('distance').textContent='Ընտրեք երկրորդ կետը։';return;}
  const line=document.createElementNS(ns,'line');line.setAttribute('x1',first.x+22);line.setAttribute('y1',270-first.y+9.5);line.setAttribute('x2',p.x+22);line.setAttribute('y2',270-p.y+9.5);overlay.append(line,point);
  const d=Math.hypot(p.x-first.x,p.y-first.y);document.getElementById('distance').textContent='Հեռավորություն՝ '+fmt(d)+' մմ թուղթ = '+fmt(2*d)+' մմ իրական չափ';first=null;
 });
})();
'''


def make_page(svg):
    points = [('O₁ (I)',X1,YI),('O₂ (I)',X2,YI),('O₁ (II)',X2,YII),('O₂ (II)',X1,YII)]
    points += [(key,x,y) for key,(_,x,y) in SUPPORTS.items()]
    rows = ''.join(f'<tr><td>{key}</td><td>{n(x)}</td><td>{n(y)}</td></tr>' for key,x,y in points)
    return f'''<!doctype html><html lang="hy"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ռեդուկտորի հարմարադասում · A3</title><style>{PAGE_CSS}</style></head><body><main>
<a href="index.html">← Մեքենամասերի տեսություն</a><h1>Ռեդուկտորի հարմարադասում</h1>
<p class="intro">Էսքիզի տրամաբանությամբ՝ երկու ատամնազույգ, աստիճանավոր լիսեռներ և հենարաններ։ 1-ին և 3-րդ լիսեռները համառանցք են։ A3 թերթ՝ 420 × 297 մմ, ցանց՝ 1 × 1 մմ, մասշտաբ՝ <b>1:2</b>։</p>
<div class="bar"><div class="downloads"><a href="{NAME}.pdf" download>PDF · A3</a><a href="{NAME}.svg" download>SVG · վեկտորային</a><a href="{NAME}.png" download>PNG · 300 dpi</a></div>
<div class="zoom" role="group" aria-label="Մեծացում"><button data-zoom="1" aria-pressed="true">Ամբողջը</button><button data-zoom="2" aria-pressed="false">×2</button><button data-zoom="3" aria-pressed="false">×3</button><button id="clear-measure">Մաքրել չափումը</button></div></div>
<div class="layers">{''.join(f'<label><input type="checkbox" data-toggle="{key}" checked> {label}</label>' for key,label in [('grid','Ցանց'),('dimensions','Չափեր'),('housing','Իրան'),('supports','Հենարաններ')])}</div>
<div class="sheet-scroll" tabindex="0" aria-label="Մեծացվող A3 գծագիր"><div class="sheet-inner">{svg}</div></div>
<div class="readout"><span id="coordinates">Կոորդինատները՝ ցանցի ձախ ստորին O կետից։</span><span id="distance" aria-live="polite">Չափելու համար ընտրեք երկու կետ։</span></div>
<p class="tip">Մեծացրեք՝ մանրամասները տեսնելու համար։ Երկու կետի չափումը գործում է նաև հպումով։ Տպելու համար ներբեռնեք PDF-ը և ընտրեք A3, 100% / «Իրական չափ»։ 100 մմ սանդղակը տպված թղթի վրա պետք է չափվի ճիշտ 100 մմ։</p>
<div class="info"><section class="card"><h2>Ինչպես գծել նույն թերթը</h2><ol>
<li>Ցանցի ձախ ստորին անկյունն ընդունեք O։ Քաշեք ուղղաձիգ առանցքները՝ x = 110 և x = 210 մմ։ Թղթի վրա 100 մմ-ը համապատասխանում է իրական 200 մմ միջառանցքային հեռավորությանը։</li>
<li>I աստիճանի կենտրոնների հորիզոնականը՝ y = 105 մմ, II աստիճանինը՝ y = 170 մմ։ Փոքր անիվը I աստիճանում ձախ է, II-ում՝ աջ։</li>
<li>Ամեն անիվի գագաթային տրամագիծն ու լայնությունը բաժանեք 2-ի և գծեք ուղղանկյունը։ Կապույտ կետագիծը բաժանարար տրամագիծն է. այդ տրամագծերը նշված են չափագծերի վրա։</li>
<li>Գծեք լիսեռներն ու աղյուսակում նշված առանցքակալները՝ բոլոր իրական չափերը բաժանելով 2-ի։ Հենարանների պայմանական նշանները ցույց են տալիս դիրքն ու գաբարիտը։</li>
<li>Ավելացրեք իրանի նախնական եզրագիծը։ Անիվի և պատի շառավղային բացակն այստեղ ընտրված է 5 մմ, իրանի պատը՝ 8 մմ։</li></ol>
<p class="tip">Անիվների, լիսեռների և առանցքակալների տվյալները՝ <a href="kinematik_hashvark.html">տետրում</a>։ Հարմարադասման սկզբունքը՝ <a href="EUDV31.pdf#page=87">ձեռնարկի §7.2-ում</a>։</p></section>
<section class="card"><h2>Կետերի կոորդինատները թղթի վրա</h2><div class="table-wrap"><table><thead><tr><th>Կետ</th><th>x, մմ</th><th>y, մմ</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="tip">O՝ անիվի կենտրոն։ Փակագծի հռոմեական թիվը՝ աստիճանը, ստորին 1/2-ը՝ փոքր/մեծ անիվը։ A և B՝ լիսեռների հենարանների կենտրոնները։</p></section>
<section class="card"><h2>Ինչն է հաշվարկված, ինչը՝ ընտրված</h2><p>Անիվների տրամագծերն ու լայնությունները, 200 մմ միջառանցքային հեռավորությունը, լիսեռների տրամագծերը և առանցքակալների գաբարիտները վերցված են մեր հաշվարկից։</p>
<p>Ատամնազույգերի և հենարանների առանցքային դիրքերը նախնական ընտրված են այս թերթի համար։ Ներքին հենարանների ամրացումը, առանցքակալների կարգավորումը և հավաքման եղանակը պետք է ճշտել կառուցվածքը մշակելիս։</p>
<p>Կափարիչներն ու կնքումներն այս սկզբնական թերթում դեռ մանրամասնված չեն։ 36306 և 36307 առանցքակալների 12° կոնտակտի անկյունն ու հենարանների վերջնական տեղադրությունը մնում են ստուգման ենթակա։</p></section>
<section class="card"><h2>Ընտրված դասավորության երկարությունները</h2><div class="table-wrap"><table><tr><th>Մեծություն</th><th>Իրական չափը, մմ</th></tr>
<tr><td>Ատամնազույգերի կենտրոնական հարթությունների միջև</td><td>130</td></tr>
<tr><td>I լիսեռի A₁–B₁ հենարանների միջև</td><td>129,5</td></tr>
<tr><td>II լիսեռի A₂–B₂ հենարանների միջև</td><td>269</td></tr>
<tr><td>III լիսեռի A₃–B₃ հենարանների միջև</td><td>108,5</td></tr></table></div>
<p class="tip">Այս երկարությունները նկարագրված նախնական դասավորության արդյունքն են։ Կառուցվածքը վերջնականացնելուց հետո դրանցով կարելի է սկսել հենարանային հակազդումների և ամրության ստուգումները։</p></section></div>
</main><script>{PAGE_JS}</script></body></html>'''


def verify_geometry(dr):
    for pair in (GEARS[:2],GEARS[2:]):
        assert math.isclose(sum(g['d'] for g in pair)/2, 200, abs_tol=1e-10)
        assert math.isclose(abs(pair[1]['x']-pair[0]['x'])/SCALE, 200)
    for gear in GEARS:
        assert 0 < gear['x']-gear['da']*SCALE/2 < gear['x']+gear['da']*SCALE/2 < 309
    assert math.isclose((SUPPORTS['B₁'][2]-SUPPORTS['A₁'][2])/SCALE,129.5)
    assert math.isclose((SUPPORTS['B₂'][2]-SUPPORTS['A₂'][2])/SCALE,269)
    assert math.isclose((SUPPORTS['B₃'][2]-SUPPORTS['A₃'][2])/SCALE,108.5)
    face_gap = (YII-55*SCALE/2)-(YI+85*SCALE/2)
    assert face_gap > 0
    for _,kind,args in dr.items:
        if kind == 'text':
            assert all(ord(ch) in pdfmetrics.getFont(font).face.charToGlyph
                       for run,_,_,font in text_runs(args[2],args[3]) for ch in run),args[2]


def main():
    find_font()
    dr=build_drawing();verify_geometry(dr)
    svg=make_svg(dr)
    (OUT/f'{NAME}.svg').write_text('<?xml version="1.0" encoding="utf-8"?>\n'+svg)
    (OUT/f'{NAME}.html').write_text(make_page(svg))
    make_pdf(dr)
    print('Built A3 420 × 297 mm at 1:2; grid spacing = 1 paper mm.')
    print('Validated gear centre distances, layout spans, page size and font coverage.')
    for ext in ['html','svg','pdf','png']:
        p=OUT/f'{NAME}.{ext}';print(p.relative_to(OUT.parent),p.stat().st_size,'bytes')


if __name__ == '__main__':
    main()
