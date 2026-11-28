"""Export the explanation to an offline A4 PDF, with vector formulas and figures.

Optional dependencies: WeasyPrint 70, fonttools, and Node + mathjax-full 3.2.2.
Run explain.py first. See ../CLAUDE.md for the complete optional export command.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

# Homebrew's Pango is outside macOS's default dynamic-library lookup path.
if Path('/opt/homebrew/lib/libpango-1.0.dylib').exists():
    os.environ.setdefault('DYLD_FALLBACK_LIBRARY_PATH', '/opt/homebrew/lib')

from weasyprint import CSS, HTML
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MATH = re.compile(r'\$\$(.*?)\$\$|\\\((.*?)\\\)', re.S)


def build_pdf(mathjax_root: str, output: Path, preview: Path | None = None) -> None:
    source = (ROOT / 'bacatrutyun.html').read_text()
    # The print document has no scripts or network dependencies.
    source = re.sub(r'<script\b[^>]*>.*?</script>', '', source, flags=re.S | re.I)
    source = re.sub(r'<link\b[^>]*>', '', source, flags=re.I)
    # SVGs are rendered as independent images by WeasyPrint. Put the page's SVG
    # class rules inside each image too, so paths keep their strokes and no fills.
    styles = '\n'.join(re.findall(r'<style>(.*?)</style>', source, re.S))
    styles = styles.split('@page')[0]
    variables = dict(re.findall(r'(--[\w-]+)\s*:\s*([^;}]+)', styles))
    styles = re.sub(r'var\((--[\w-]+)\)', lambda m: variables[m[1]], styles)
    def figure_image(match):
        svg = match[0]
        svg = svg.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ', 1) if 'xmlns=' not in svg else svg
        start = svg.index('>') + 1
        svg = svg[:start] + f'<style>{styles}</style>' + svg[start:]
        data = base64.b64encode(svg.encode()).decode()
        return f'<img class="figure-svg" alt="Գծագիր" src="data:image/svg+xml;base64,{data}">'
    source = re.sub(r'<svg\b.*?</svg>', figure_image, source, flags=re.S)
    matches = list(MATH.finditer(source))
    formulas = [{'tex': html.unescape(m[1] if m[1] is not None else m[2]),
                 'display': m[1] is not None} for m in matches]
    proc = subprocess.run(['node', str(HERE / 'math_svg.cjs'), mathjax_root],
                          input=json.dumps(formulas), text=True, capture_output=True, check=True)
    rendered = json.loads(proc.stdout)
    assert len(rendered) == len(formulas)
    replacements = []
    for m, formula, result in zip(matches, formulas, rendered):
        width = float(result['width'].removesuffix('ex')) / 2
        height = float(result['height'].removesuffix('ex')) / 2
        align = re.search(r'vertical-align:\s*([-.\d]+)ex', result['style'])
        baseline = float(align[1]) / 2 if align else 0
        data = base64.b64encode(result['svg'].encode()).decode()
        image = (f'<img class="math-svg" alt="{html.escape(formula["tex"], quote=True)}" '
                 f'src="data:image/svg+xml;base64,{data}" '
                 f'style="width:{width:.4f}em;height:{height:.4f}em;vertical-align:{baseline:.4f}em">')
        tag = 'div' if formula['display'] else 'span'
        cls = 'math-display' if formula['display'] else 'math-inline'
        replacements.append((m.start(), m.end(), f'<{tag} class="{cls}">{image}</{tag}>'))
    for start, end, replacement in reversed(replacements):
        source = source[:start] + replacement + source[end:]
    assert not MATH.search(re.sub(r'<img\b[^>]*>', '', source))
    # Repeat header rows across page breaks; source tables use their first row as a header.
    source = re.sub(r'(<table\b[^>]*>\s*)(<tr>\s*<th>.*?</tr>)',
                    r'\1<thead>\2</thead>', source, flags=re.S)
    # Resolve links from the PDF to the published site rather than local build paths.
    site = 'https://areg06.github.io/UNI/kursayin%20ashxatanq/Variant1/'
    source = re.sub(r'href="(?!https?://|#)([^"]+)"', lambda m: f'href="{site}{m[1]}"', source)

    with tempfile.TemporaryDirectory(prefix='uni-explanation-fonts-') as temp:
        font_css = ''
        mac_font = Path('/System/Library/Fonts/NotoSansArmenian.ttc')
        if mac_font.exists():
            # This TTC contains several weights: regular is face 6, bold is face 1.
            for weight, index in [(400, 6), (700, 1)]:
                dest = Path(temp) / f'armenian-{weight}.ttf'
                font = TTFont(mac_font, fontNumber=index)
                font.save(dest)
                font_css += (f'@font-face{{font-family:"UNI Armenian";font-weight:{weight};'
                             f'src:url("{dest.as_uri()}")}}\n')
            font_css += 'body,svg text{font-family:"UNI Armenian","Arial Unicode MS",sans-serif}\n'
        css = font_css + '''
          .math-display{text-align:center;margin:8pt 0;break-inside:avoid;line-height:1.1}
          .math-inline{white-space:nowrap;line-height:1}
          img.math-svg{max-width:100%;object-fit:contain;margin:0}
          .math-display img.math-svg{height:auto!important}
          img.figure-svg{display:block;width:100%;height:auto;max-height:90mm;object-fit:contain;margin:7pt auto;break-inside:avoid;break-after:avoid}
          .a3box img.figure-svg,.a4box img.figure-svg{max-height:85mm}
        '''
        # Keep font URLs available until the renderer has embedded the fonts.
        if preview:
            preview.write_text(source.replace('</head>', f'<style>{css}</style></head>'))
        HTML(string=source, base_url=str(ROOT)).write_pdf(str(output), stylesheets=[CSS(string=css)])
    print(f'{output.name}: {len(formulas)} vector formulas, {output.stat().st_size:,} bytes')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mathjax-root', default=os.environ.get('UNI_MATHJAX_ROOT', 'mathjax-full'))
    parser.add_argument('--output', type=Path, default=ROOT / 'bacatrutyun.pdf')
    parser.add_argument('--preview', type=Path, help='Optional temporary HTML for debugging')
    args = parser.parse_args()
    build_pdf(args.mathjax_root, args.output, args.preview)
