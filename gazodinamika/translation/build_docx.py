#!/usr/bin/env python3
"""Build the editable book from parts/*.html.

Requires python-docx, lxml, Pillow and Pandoc 3.x. Example:
    python build_docx.py --pandoc /path/to/pandoc
Text and tables remain editable; Pandoc converts TeX to native Word equations.
The small inline SVG uses figs/heat_engine_word.png as its Word fallback.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import subprocess
import tempfile
from zipfile import ZipFile

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor
from lxml import etree, html
from PIL import Image

D = Path(__file__).resolve().parent
MATH = re.compile(r'\\\((.*?)\\\)|\\\[(.*?)\\\]', re.S)
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'}


def native_math(root, pandoc):
    """Convert unique expressions in one batch, rejecting conversion fallbacks."""
    expressions = list(dict.fromkeys(
        next(g for g in m.groups() if g is not None)
        for text in root.itertext() for m in MATH.finditer(text)))
    version = json.loads(subprocess.check_output(
        [pandoc, '-f', 'markdown', '-t', 'json'], input=b''))['pandoc-api-version']
    ast = {'pandoc-api-version': version, 'meta': {}, 'blocks': [
        {'t': 'Para', 'c': [{'t': 'Math', 'c': [{'t': 'InlineMath'}, expr]}]}
        for expr in expressions]}
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / 'math.docx'
        subprocess.run([pandoc, '-f', 'json', '-t', 'docx', '-o', str(out)],
                       input=json.dumps(ast).encode(), check=True)
        with ZipFile(out) as z:
            tree = etree.fromstring(z.read('word/document.xml'))
    paragraphs = tree.xpath('/w:document/w:body/w:p', namespaces=NS)
    if len(paragraphs) != len(expressions):
        raise ValueError('Unexpected equation conversion count')
    result = {}
    for expr, para in zip(expressions, paragraphs):
        equations = para.xpath('.//m:oMath', namespaces=NS)
        fallback = ''.join(para.xpath('.//w:t/text()', namespaces=NS)).strip('\u200b \n')
        if len(equations) != 1 or fallback:
            raise ValueError(f'Equation was not converted to native Word math: {expr}')
        eq = equations[0]
        # Armenian subscripts need a font with Armenian coverage; math symbols
        # retain Cambria Math through the document's math settings.
        for run in eq.xpath('.//m:r', namespaces=NS):
            if any('\u0530' <= c <= '\u058f' for c in ''.join(run.itertext())):
                rp = run.find(qn('w:rPr'))
                if rp is None:
                    rp = OxmlElement('w:rPr')
                    run.insert(1 if run.find(qn('m:rPr')) is not None else 0, rp)
                fonts = OxmlElement('w:rFonts')
                fonts.set(qn('w:ascii'), 'Noto Serif Armenian')
                fonts.set(qn('w:hAnsi'), 'Noto Serif Armenian')
                rp.append(fonts)
        result[expr] = eq
    return result


class Book:
    def __init__(self, equations):
        self.doc = Document()
        self.equations = equations
        self.math_count = 0
        self.images = 0
        section = self.doc.sections[0]
        section.page_width, section.page_height = Mm(210), Mm(297)
        section.top_margin = section.bottom_margin = Mm(20)
        section.left_margin, section.right_margin = Mm(20), Mm(18)
        self.width = section.page_width - section.left_margin - section.right_margin
        styles = self.doc.styles
        for style in styles:
            if style.type == 1:
                style.font.name = 'Noto Serif Armenian'
                style.font.color.rgb = RGBColor(0, 0, 0)
            for border in style.element.xpath('.//w:pBdr'):
                border.getparent().remove(border)
        normal = styles['Normal']
        normal.font.size = Pt(11.5)
        pf = normal.paragraph_format
        pf.line_spacing = 1.25
        pf.space_after = Pt(6)
        pf.first_line_indent = Mm(5)
        pf.widow_control = True
        for level, size in [(1, 17), (2, 14), (3, 12), (4, 11.5)]:
            s = styles[f'Heading {level}']
            s.font.name = 'Noto Sans Armenian'
            s.font.size = Pt(size)
            s.font.bold = True
            s.paragraph_format.first_line_indent = 0
            s.paragraph_format.keep_with_next = True
            s.paragraph_format.space_before = Pt(14)
            s.paragraph_format.space_after = Pt(8)
            s.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if level == 1:
                s.paragraph_format.page_break_before = True
        for name in ['Title', 'Subtitle', 'Caption']:
            styles[name].font.name = 'Noto Sans Armenian'
            styles[name].paragraph_format.first_line_indent = 0
            styles[name].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        styles['Title'].font.size = Pt(24)
        styles['Title'].font.bold = True
        styles['Subtitle'].font.size = Pt(12)
        styles['Subtitle'].font.italic = False
        styles['Caption'].font.size = Pt(10)
        styles['Caption'].font.italic = False
        styles['Caption'].paragraph_format.keep_with_next = False
        lang = OxmlElement('w:lang')
        lang.set(qn('w:val'), 'hy-AM')
        normal.element.get_or_add_rPr().append(lang)
        self.doc.core_properties.title = 'Թերմոդինամիկա և ջերմափոխանակում'
        self.doc.core_properties.author = 'Ա. Ռ. Բարսեղյան'
        self.doc.core_properties.language = 'hy-AM'
        self.doc.core_properties.subject = 'Դասախոսությունների համառոտագիր'

    def text(self, p, text, bold=None, italic=None, sub=None, underline=None):
        if not text:
            return
        start = 0
        for m in MATH.finditer(text):
            self.run(p, text[start:m.start()], bold, italic, sub, underline)
            expr = next(g for g in m.groups() if g is not None)
            p._p.append(deepcopy(self.equations[expr]))
            self.math_count += 1
            start = m.end()
        self.run(p, text[start:], bold, italic, sub, underline)

    @staticmethod
    def run(p, text, bold, italic, sub, underline):
        if text:
            r = p.add_run(re.sub(r'\s+', ' ', text))
            r.bold, r.italic = bold, italic
            r.font.subscript, r.underline = sub, underline

    def inline(self, p, node, **fmt):
        self.text(p, node.text, **fmt)
        for child in node:
            if child.tag == 'br':
                p.add_run().add_break()
            else:
                cf = dict(fmt)
                for tag, prop in [('b', 'bold'), ('strong', 'bold'), ('i', 'italic'),
                                  ('em', 'italic'), ('sub', 'sub'), ('u', 'underline')]:
                    if child.tag == tag:
                        cf[prop] = True
                self.inline(p, child, **cf)
            self.text(p, child.tail, **fmt)

    def paragraph(self, node, style=None):
        p = self.doc.add_paragraph(style=style)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if not style else None
        if 'ni' in node.get('class', '').split():
            p.paragraph_format.first_line_indent = 0
        self.inline(p, node)
        return p

    def table(self, node):
        caption = node.find('caption')
        if caption is not None:
            p = self.paragraph(caption, 'Caption')
            p.paragraph_format.keep_with_next = True
        rows = node.xpath('./tr|./thead/tr|./tbody/tr')
        cols = max(sum(int(c.get('colspan', 1)) for c in r) for r in rows)
        table = self.doc.add_table(rows=len(rows), cols=cols)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        ratios = [0.36, 0.38, 0.26] if node.get('class') == 'gloss' else [1 / cols] * cols
        if cols == 7:
            ratios = [.21, .14, .13, .13, .13, .13, .13]
        if cols == 6 and len(rows) == 10:
            ratios = [.25, .08, .17, .25, .08, .17]
        for col, ratio in zip(table.columns, ratios):
            col.width = int(self.width * ratio)
        occupied = set()
        for i, row in enumerate(rows):
            trpr = table.rows[i]._tr.get_or_add_trPr()
            trpr.append(OxmlElement('w:cantSplit'))
            if all(c.tag == 'th' for c in row):
                trpr.append(OxmlElement('w:tblHeader'))
            j = 0
            for source in row:
                while (i, j) in occupied:
                    j += 1
                rs, cs = int(source.get('rowspan', 1)), int(source.get('colspan', 1))
                cell = table.cell(i, j)
                if rs > 1 or cs > 1:
                    cell = cell.merge(table.cell(i + rs - 1, j + cs - 1))
                for a in range(i, i + rs):
                    for b in range(j, j + cs):
                        occupied.add((a, b))
                cell.width = int(self.width * sum(ratios[j:j + cs]))
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                p = cell.paragraphs[0]
                pf = p.paragraph_format
                pf.first_line_indent = 0
                pf.space_after = pf.space_before = Pt(3)
                pf.line_spacing = 1.1
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if cols == 3 or j == 0 else WD_ALIGN_PARAGRAPH.CENTER
                self.inline(p, source, bold=(source.tag == 'th' or
                            'sec' in row.get('class', '').split() or
                            (node.get('class') == 'gloss' and j == 1)))
                for run in p.runs:
                    run.font.size = Pt(9 if cols >= 7 else 9.5)
                pr = cell._tc.get_or_add_tcPr()
                borders = OxmlElement('w:tcBorders')
                for edge in ['top', 'left', 'bottom', 'right']:
                    e = OxmlElement('w:' + edge)
                    for key, val in [('val', 'single'), ('sz', '4'), ('color', 'D9D9D9')]:
                        e.set(qn('w:' + key), val)
                    borders.append(e)
                pr.append(borders)
                margins = OxmlElement('w:tcMar')
                for edge in ['top', 'left', 'bottom', 'right']:
                    e = OxmlElement('w:' + edge)
                    e.set(qn('w:w'), '65')
                    e.set(qn('w:type'), 'dxa')
                    margins.append(e)
                pr.append(margins)
                if source.tag == 'th' or row.get('class') == 'sec':
                    shade = OxmlElement('w:shd')
                    shade.set(qn('w:fill'), 'EEF1F5')
                    pr.append(shade)
                j += cs
        spacer = self.doc.add_paragraph()
        spacer.paragraph_format.space_after = Pt(2)
        spacer.paragraph_format.line_spacing = Pt(2)

    def figure(self, node):
        for source in node:
            if source.tag not in ['img', 'svg']:
                continue
            path = D / source.get('src') if source.tag == 'img' else D / 'figs/heat_engine_word.png'
            with Image.open(path) as image:
                w, h = image.size
            limit = re.search(r'max-height:\s*([\d.]+)mm', source.get('style', ''))
            max_h = float(limit[1]) if limit else 95
            width = min(160, max_h * w / h, w * 25.4 / (300 if source.tag == 'img' else 384))
            p = self.doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = 0
            p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(str(path), width=Mm(width))
            self.images += 1
        caption = node.find('figcaption')
        if caption is not None:
            self.paragraph(caption, 'Caption')

    def block(self, node):
        tag, cls = node.tag, node.get('class', '')
        if tag in ['h1', 'h2', 'h3', 'h4']:
            self.paragraph(node, 'Heading ' + tag[1])
        elif tag == 'p':
            self.paragraph(node)
        elif tag in ['ul', 'ol']:
            for i, li in enumerate(node, 1):
                p = self.doc.add_paragraph()
                p.paragraph_format.first_line_indent = Mm(-4)
                p.paragraph_format.left_indent = Mm(7)
                if cls != 'toc':
                    p.add_run(f'{i}. ' if tag == 'ol' else '• ')
                self.inline(p, li)
        elif tag == 'table':
            self.table(node)
        elif tag == 'figure':
            self.figure(node)
        elif cls == 'eq':
            p = self.doc.add_paragraph()
            pf = p.paragraph_format
            pf.first_line_indent = 0
            pf.keep_together = True
            pf.space_before = pf.space_after = Pt(5)
            pf.tab_stops.add_tab_stop(int(self.width / 2), WD_TAB_ALIGNMENT.CENTER)
            pf.tab_stops.add_tab_stop(self.width, WD_TAB_ALIGNMENT.RIGHT)
            p.add_run('\t')
            self.inline(p, node.find('./div[@class="m"]'))
            n = node.find('./div[@class="n"]')
            if n is not None and n.text:
                p.add_run('\t' + n.text).font.size = Pt(10)
        elif cls == 'title-page':
            for source in node:
                c = source.get('class')
                style = 'Title' if c == 'main' else 'Subtitle'
                p = self.paragraph(source, style)
                p.paragraph_format.keep_with_next = True
                p.paragraph_format.space_before = Mm({'org': 20, 'author': 24, 'main': 18, 'sub': 4, 'bottom': 40}.get(c, 4))
                if c == 'bottom':
                    p.paragraph_format.keep_with_next = False
                    for r in p.runs:
                        r.font.size = Pt(9.5)
        elif tag == 'div':
            for child in node:
                self.block(child)
        else:
            raise ValueError(f'Unsupported block: {tag} {cls}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pandoc', default='pandoc')
    parser.add_argument('--output', type=Path, default=D / 'gazadinamika_hy.docx')
    args = parser.parse_args()
    source = '\n'.join(p.read_text(encoding='utf-8') for p in sorted((D / 'parts').glob('*.html')))
    root = html.fragment_fromstring(source, create_parent='div')
    book = Book(native_math(root, args.pandoc))
    for node in root:
        book.block(node)
    expected_math = sum(len(MATH.findall(t)) for t in root.itertext())
    expected_images = len(root.xpath('.//img|.//svg'))
    assert book.math_count == expected_math, (book.math_count, expected_math)
    assert book.images == expected_images, (book.images, expected_images)
    book.doc.save(args.output)
    print(f'{args.output}: {book.math_count} editable equations, {book.images} illustrations')


if __name__ == '__main__':
    main()
