#!/usr/bin/env python3
"""Merge parts/*.html into one HTML file and print it to PDF with headless Chrome."""
import glob, os, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__))
parts = sorted(glob.glob(os.path.join(D, 'parts', '*.html')))
body = '\n'.join(open(p, encoding='utf-8').read() for p in parts)
tpl = open(os.path.join(D, 'template.html'), encoding='utf-8').read()
html = tpl.replace('<!--BODY-->', body)
out_html = os.path.join(D, 'gazadinamika_hy.html')
open(out_html, 'w', encoding='utf-8').write(html)
pdf = os.path.join(os.path.dirname(D), 'Ջերմադինամիկա_և_ջերմափոխանցում_ՀԱՅ.pdf')
chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
if '--html-only' not in sys.argv:
    subprocess.run([chrome, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                    '--virtual-time-budget=30000', '--run-all-compositor-stages-before-draw',
                    f'--print-to-pdf={pdf}', 'file://' + out_html], check=True)
    print('PDF:', pdf)
