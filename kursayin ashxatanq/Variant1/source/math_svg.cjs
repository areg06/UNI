// Optional print helper: npm install mathjax-full@3.2.2
// Read [{tex, display}] from stdin; return self-contained SVGs as JSON.
const fs = require('node:fs');
const path = require('node:path');
const root = process.argv[2] || 'mathjax-full';
const get = p => require(root.startsWith('.') || path.isAbsolute(root) ? path.join(root, p) : `${root}/${p}`);
const {mathjax} = get('js/mathjax.js');
const {TeX} = get('js/input/tex.js');
const {SVG} = get('js/output/svg.js');
const {liteAdaptor} = get('js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler} = get('js/handlers/html.js');
const {AllPackages} = get('js/input/tex/AllPackages.js');
const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const doc = mathjax.document('', {
  InputJax: new TeX({packages: AllPackages}),
  OutputJax: new SVG({fontCache: 'none'})
});
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const result = input.map(({tex, display}, index) => {
  const node = doc.convert(tex, {display, em: 16, ex: 8, containerWidth: 1040});
  const svg = adaptor.firstChild(node);
  const markup = adaptor.outerHTML(svg);
  if (markup.includes('data-mml-node="merror"')) throw new Error(`Formula ${index}: ${tex}`);
  return {svg: markup, width: adaptor.getAttribute(svg, 'width'),
    height: adaptor.getAttribute(svg, 'height'), style: adaptor.getAttribute(svg, 'style') || ''};
});
process.stdout.write(JSON.stringify(result));
