/* Materials-science lecture visuals, lectures 1–3, plus shared drawing helpers (3D unit cells, grain maps). */
(function(){
'use strict';
const {C, S, H, T, setT, attrs, svg, pts, arrow, axes, clamp, lerp, fmt, rnd, col, ctl, slider, seg, btn, out, anim, RM} = window.VZ;
const VIZ = window.VIZ;
const ss = x => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
const clear = g => { while (g.firstChild) g.removeChild(g.firstChild); return g; };

/* ---------- helpers: canvas and grain maps ---------- */
function rgbOf(name){
  const v = col(name); let m = v.match(/^#([0-9a-f]{6})$/i);
  if (m) return [0, 2, 4].map(i => parseInt(m[1].slice(i, i + 2), 16));
  m = v.match(/(\d+)\D+(\d+)\D+(\d+)/); return m ? [+m[1], +m[2], +m[3]] : [128, 128, 128];
}
const mixc = (a, b, t) => [0, 1, 2].map(i => Math.round(a[i] + (b[i] - a[i]) * t));
function canvas(host, w, h){
  const c = H('canvas', {class:'vz-cv', width:w, height:h}, host);
  const g = c.getContext('2d'); return {c, g, w, h, img:g.createImageData(w, h)};
}
// Voronoi grain map; sx < 1 stretches grains along x
function grains(w, h, n, seed, sx, sy, seeds){
  const r = rnd(seed), P = seeds || Array.from({length:n}, () => [r() * w, r() * h]); sx = sx || 1; sy = sy || 1;
  const lab = new Int16Array(w * h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++){
    let b = 0, bd = 1e18;
    for (let i = 0; i < P.length; i++){ const dx = (x - P[i][0]) * sx, dy = (y - P[i][1]) * sy, d = dx * dx + dy * dy; if (d < bd){ bd = d; b = i; } }
    lab[y * w + x] = b; }
  const edge = new Uint8Array(w * h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++){ const i = y * w + x, l = lab[i];
    if ((x + 1 < w && lab[i + 1] !== l) || (y + 1 < h && lab[i + w] !== l)) edge[i] = 1; }
  return {P, lab, edge, w, h};
}
// distance to the nearest grain boundary (city-block), for thick boundary films
function bdist(G, max){
  const {w, h, edge} = G, d = new Uint8Array(w * h).fill(255);
  for (let i = 0; i < w * h; i++) if (edge[i]) d[i] = 0;
  for (let k = 0; k < max; k++) for (let y = 0; y < h; y++) for (let x = 0; x < w; x++){ const i = y * w + x; if (d[i] !== k) continue;
    if (x > 0 && d[i - 1] > k + 1) d[i - 1] = k + 1; if (x + 1 < w && d[i + 1] > k + 1) d[i + 1] = k + 1;
    if (y > 0 && d[i - w] > k + 1) d[i - w] = k + 1; if (y + 1 < h && d[i + w] > k + 1) d[i + w] = k + 1; }
  return d;
}
const hash = i => { let x = (i + 1) * 2654435761 >>> 0; x ^= x >>> 13; x = Math.imul(x, 1274126177) >>> 0; return (x >>> 0) / 4294967296; };

/* ---------- helper: rotatable 3D unit cell ---------- */
const C6 = 1.633;
function cube(){ const p = []; for (const x of [-.5, .5]) for (const y of [-.5, .5]) for (const z of [-.5, .5]) p.push([x, y, z]); return p; }
const cubeEdges = () => { const p = cube(), e = []; p.forEach((a, i) => p.forEach((b, j) => { if (j > i && [0, 1, 2].filter(k => a[k] !== b[k]).length === 1) e.push([a, b]); })); return e; };
const hex = (z, r) => Array.from({length:6}, (_, k) => [r * Math.cos(k * Math.PI / 3), r * Math.sin(k * Math.PI / 3), z]);
const tri = z => [30, 150, 270].map(a => [Math.cos(a * Math.PI / 180) / Math.sqrt(3), Math.sin(a * Math.PI / 180) / Math.sqrt(3), z]);
const loop = a => a.map((p, i) => [p, a[(i + 1) % a.length]]);
const STRUCT = {
  K6:{n:'Պարզ խորանարդային, К6', cell:() => ({p:cube(), e:cubeEdges()}), cn:() => {
    const p = []; for (let x = -1; x <= 1; x++) for (let y = -1; y <= 1; y++) for (let z = -1; z <= 1; z++) if (Math.abs(x) + Math.abs(y) + Math.abs(z) <= 1) p.push([x / 2, y / 2, z / 2]);
    return {p, e:[[[-.5, 0, 0], [.5, 0, 0]], [[0, -.5, 0], [0, .5, 0]], [[0, 0, -.5], [0, 0, .5]]], d:.5}; }, cnt:'8·⅛ = 1', k:6},
  K8:{n:'Խորանարդային ծավալակենտրոնացված, К8', cell:() => ({p:cube().concat([[0, 0, 0]]), e:cubeEdges()}), cn:() => ({p:cube().concat([[0, 0, 0]]), e:cubeEdges(), d:Math.sqrt(3) / 2}), cnt:'8·⅛ + 1 = 2', k:8},
  K12:{n:'Խորանարդային նիստակենտրոնացված, К12', cell:() => ({p:cube().concat([[.5, 0, 0], [-.5, 0, 0], [0, .5, 0], [0, -.5, 0], [0, 0, .5], [0, 0, -.5]]), e:cubeEdges()}),
    cn:() => { const p = [[0, 0, 0]], s = [-.5, .5];
      for (const a of s) for (const b of s){ p.push([a, b, 0]); p.push([a, 0, b]); p.push([0, a, b]); }
      const sq = (f) => loop([[-.5, -.5], [.5, -.5], [.5, .5], [-.5, .5]].map(f));
      return {p, e:[...sq(([a, b]) => [a, b, 0]), ...sq(([a, b]) => [a, 0, b]), ...sq(([a, b]) => [0, a, b])], d:Math.SQRT1_2}; }, cnt:'8·⅛ + 6·½ = 4', k:12},
  G12:{n:'Հեքսագոնալ խիտ դասավորված, Г12', cell:() => { const b = hex(-C6 / 2, 1), t = hex(C6 / 2, 1);
      return {p:[...b, [0, 0, -C6 / 2], ...t, [0, 0, C6 / 2], ...tri(0)], e:[...loop(b), ...loop(t), ...b.map((q, i) => [q, t[i]])]}; },
    cn:() => { const a = hex(0, 1), u = tri(C6 / 2), d = tri(-C6 / 2); return {p:[[0, 0, 0], ...a, ...u, ...d], e:[...loop(a), ...loop(u), ...loop(d)], d:1}; }, cnt:'6', k:12}};
function cell3d(host, o){
  o = o || {};
  const W = o.w || 300, Hh = o.h || 260, s = svg(host, W, Hh, 'Տարրական բջիջ'), g = S('g', {}, s), cap = T(s, W / 2, Hh - 8, '', {'text-anchor':'middle', fill:C.muted, 'font-size':11});
  s.style.cursor = 'grab'; s.style.touchAction = 'none'; s.style.maxWidth = (o.max || 360) + 'px'; s.style.margin = '0 auto';
  let th = .6, ph = .38, drag = null, kind = o.kind || 'K8', mode = o.mode || 'cell', data, liquid = false;
  function set(k, m){ kind = k; mode = m || mode; liquid = false; const st = STRUCT[k]; data = mode === 'cn' ? st.cn() : st.cell(); draw(); }
  function proj(p){ const [x, y, z] = p, c = Math.cos(th), sn = Math.sin(th), x1 = x * c - y * sn, y1 = x * sn + y * c, y2 = y1 * Math.cos(ph) - z * Math.sin(ph), z2 = y1 * Math.sin(ph) + z * Math.cos(ph);
    const sc = (kind === 'G12' ? .27 : .36) * Math.min(W, Hh - 20); return [W / 2 + x1 * sc, (Hh - 20) / 2 - z2 * sc, y2]; }
  function draw(){
    clear(g);
    if (liquid){ const r = rnd(9); for (let i = 0; i < 18; i++) S('circle', {cx:W / 2 + (r() - .5) * 170, cy:(Hh - 20) / 2 + (r() - .5) * 150, r:9, fill:C.heat, opacity:.55}, g); setT(cap, 'հեղուկ՝ կանոնավոր դասավորություն չկա'); return; }
    data.e.forEach(([a, b]) => { const p = proj(a), q = proj(b); S('line', {x1:p[0], y1:p[1], x2:q[0], y2:q[1], stroke:C.muted, 'stroke-width':1.3}, g); });
    const isC = p => Math.abs(p[0]) + Math.abs(p[1]) + Math.abs(p[2]) < 1e-9;
    const A = data.p.map(p => { const q = proj(p); return {q, c:mode === 'cn' && isC(p), nb:mode === 'cn' && !isC(p) && Math.abs(Math.hypot(...p) - data.d) < 1e-6}; }).sort((a, b) => b.q[2] - a.q[2]);
    const rr = kind === 'G12' ? 10 : 12;
    A.forEach(a => S('circle', {cx:a.q[0], cy:a.q[1], r:rr * (1 - a.q[2] * .12), fill:a.c ? C.heat : a.nb ? C.good : mode === 'cn' ? C.line : C.acc, stroke:'var(--surface)', 'stroke-width':1.2, opacity:.95}, g));
    const st = STRUCT[kind];
    setT(cap, mode === 'cn' ? 'կոորդինացիոն թիվ՝ ' + st.k + ' (կանաչ՝ ամենամոտ հարևանները)' : 'ատոմ մեկ բջջում՝ ' + st.cnt);
  }
  s.addEventListener('pointerdown', e => { drag = [e.clientX, e.clientY, th, ph]; s.setPointerCapture(e.pointerId); s.style.cursor = 'grabbing'; });
  s.addEventListener('pointermove', e => { if (!drag) return; th = drag[2] - (e.clientX - drag[0]) / 90; ph = clamp(drag[3] + (e.clientY - drag[1]) / 90, -1.3, 1.3); draw(); });
  s.addEventListener('pointerup', () => { drag = null; s.style.cursor = 'grab'; });
  set(kind, mode);
  if (o.spin !== false) anim(host, dt => { if (!drag && !liquid){ th += dt * .45; draw(); } }, o.ctl);
  return {set, liquid(){ liquid = true; draw(); }};
}

/* ---------- 1.2 loads and stresses ---------- */
VIZ.loads = {kind:'a', cap:'Ուժերը լինում են <b>ստատիկ</b> (հաստատուն կամ դանդաղ աճող), <b>դինամիկ</b> (հարվածային, արագ աճող) և <b>ցիկլային</b> (կրկնվող-փոփոխական)։ Դրանք առաջացնում են ձգման, սեղմման, ծռման և ոլորման լարումներ։',
f(st){
  const s = svg(st, 640, 286, 'Ուժեր և լարումներ');
  const L = [['ստատիկ', t => Math.min(1, t / .6)], ['դինամիկ', t => t < .45 ? 0 : Math.exp(-(((t - .5) / .04) ** 2))], ['ցիկլային', t => Math.sin(t * 6 * Math.PI) * .9]];
  const cur = L.map(([n, f], i) => { const x = 20 + i * 210, A = axes(s, {x:x + 10, y:30, w:170, h:70, xr:[0, 1], yr:[-1, 1.1], xl:'t', yl:'P'});
    T(s, x + 95, 18, n, {'text-anchor':'middle', 'font-weight':600}); S('line', {x1:A.X(0), x2:A.X(1), y1:A.Y(0), y2:A.Y(0), stroke:C.line}, s);
    return {A, f, p:S('path', {fill:'none', stroke:C.heat, 'stroke-width':2.2}, s), d:S('circle', {r:4, fill:C.heat}, s)}; });
  const names = ['ձգում', 'սեղմում', 'ծռում', 'ոլորում'], G = names.map((n, i) => { T(s, 80 + i * 160, 278, n, {'text-anchor':'middle', 'font-weight':600}); return S('g', {}, s); });
  anim(st, (dt, t) => {
    const u = (t % 4) / 3.4;
    cur.forEach(c => { const e = Math.min(u, 1); attrs(c.p, {d:c.A.fn(c.f, 0, Math.max(e, .001), 120)}); attrs(c.d, {cx:c.A.X(e), cy:c.A.Y(c.f(e))}); });
    const a = .5 - .5 * Math.cos(t * 2.2), cy = 190;
    clear(G[0]); S('rect', {x:80 - 12, y:cy - 40 - a * 8, width:24, height:80 + a * 16, fill:C.accS, stroke:C.acc}, G[0]);
    arrow(G[0], 80, cy - 42 - a * 8, 80, cy - 62 - a * 8, C.bad, 2, 7); arrow(G[0], 80, cy + 42 + a * 8, 80, cy + 62 + a * 8, C.bad, 2, 7);
    clear(G[1]); S('rect', {x:240 - 12 - a * 3, y:cy - 40 + a * 8, width:24 + a * 6, height:80 - a * 16, fill:C.accS, stroke:C.acc}, G[1]);
    arrow(G[1], 240, cy - 62 + a * 8, 240, cy - 42 + a * 8, C.bad, 2, 7); arrow(G[1], 240, cy + 62 - a * 8, 240, cy + 42 - a * 8, C.bad, 2, 7);
    clear(G[2]); const b = a * 16; S('path', {d:`M340 ${cy - 8} Q400 ${cy - 8 + b * 2} 460 ${cy - 8} L460 ${cy + 8} Q400 ${cy + 8 + b * 2} 340 ${cy + 8}Z`, fill:C.accS, stroke:C.acc}, G[2]);
    S('polygon', {points:`345,${cy + 10} 337,${cy + 22} 353,${cy + 22}`, fill:C.ink}, G[2]); S('polygon', {points:`455,${cy + 10} 447,${cy + 22} 463,${cy + 22}`, fill:C.ink}, G[2]);
    arrow(G[2], 400, cy - 40, 400, cy - 12 + b, C.bad, 2, 7);
    clear(G[3]); S('rect', {x:530, y:cy - 18, width:100, height:36, rx:6, fill:C.accS, stroke:C.acc}, G[3]);
    for (let i = 0; i < 5; i++){ const x = 540 + i * 20; S('line', {x1:x, y1:cy - 18, x2:x + a * 14 * (i / 4), y2:cy + 18, stroke:C.acc}, G[3]); }
    S('path', {d:`M618 ${cy - 26} a10 26 0 1 1 0 52`, fill:'none', stroke:C.bad, 'stroke-width':2}, G[3]);
  }, ctl(st));
}};

/* ---------- 1.3 tensile test ---------- */
VIZ.tensile = {kind:'a', cap:'Ձգման փորձարկում. սկզբնական ուղղագիծ մասում՝ <b>Հուկի օրենք</b> ( E = tg α ), հետո՝ <b>հոսունության սահման</b> σ<sub>տ</sub> (կամ պայմանական σ<sub>0,2</sub>), ամենամեծ բեռին՝ <b>ժամանակավոր դիմադրություն</b> σ<sub>բ</sub>, վզիկ և խզում։ Կորը սխեմատիկ է։',
f(st){
  const s = svg(st, 640, 290, 'Ձգման դիագրամ');
  const A = axes(s, {x:250, y:24, w:350, h:220, xr:[0, .36], yr:[0, 1.15], xl:'երկարացում ε', yl:'σ'});
  let kind = 'f';
  const curve = {
    f:e => e < .012 ? e / .012 * .6 : e < .045 ? .6 + .006 * Math.sin((e - .012) * 380) : e < .25 ? .6 + .4 * Math.sin((e - .045) / .205 * Math.PI / 2) : 1 - .18 * ((e - .25) / .07) ** 1.6,
    c:e => e < .012 ? e / .012 * .6 : e < .25 ? .6 + .4 * Math.sin(((e - .012) / .238) ** .7 * Math.PI / 2) : 1 - .18 * ((e - .25) / .07) ** 1.6};
  const path = S('path', {fill:'none', stroke:C.acc, 'stroke-width':2.6}, s), dot = S('circle', {r:5.5, fill:C.heat}, s), marks = S('g', {}, s);
  const spec = S('g', {}, s), note = T(s, 425, 278, '', {'text-anchor':'middle', 'font-weight':600});
  const end = .32;
  function specimen(e, broken){
    clear(spec); const L0 = 130, L = L0 * (1 + e * 1.2), cx = 110, top = 150 - L / 2 - 30, neck = e > .25 ? (e - .25) / .07 : 0;
    S('rect', {x:cx - 30, y:top - 26, width:60, height:30, rx:4, fill:C.ink}, spec); S('rect', {x:cx - 30, y:top + L + 56, width:60, height:30, rx:4, fill:C.ink}, spec);
    const w = 18 * (1 - e * .25), wn = w * (1 - .55 * neck), mid = top + 30 + L / 2;
    if (!broken) S('path', {d:`M${cx - 26} ${top + 4} L${cx - 26} ${top + 18} Q${cx - w} ${top + 24} ${cx - w} ${top + 34} L${cx - w} ${mid - 16} Q${cx - wn} ${mid} ${cx - w} ${mid + 16} L${cx - w} ${top + L + 26} Q${cx - w} ${top + L + 36} ${cx - 26} ${top + L + 42} L${cx - 26} ${top + L + 56} L${cx + 26} ${top + L + 56} L${cx + 26} ${top + L + 42} Q${cx + w} ${top + L + 36} ${cx + w} ${top + L + 26} L${cx + w} ${mid + 16} Q${cx + wn} ${mid} ${cx + w} ${mid - 16} L${cx + w} ${top + 34} Q${cx + w} ${top + 24} ${cx + 26} ${top + 18} L${cx + 26} ${top + 4}Z`, fill:C.accS, stroke:C.acc, 'stroke-width':1.5}, spec);
    else { S('path', {d:`M${cx - 26} ${top + 4} L${cx - 26} ${top + 18} Q${cx - w} ${top + 24} ${cx - w} ${top + 34} L${cx - w} ${mid - 22} L${cx - 5} ${mid - 8} L${cx + 5} ${mid - 8} L${cx + w} ${mid - 22} L${cx + w} ${top + 34} Q${cx + w} ${top + 24} ${cx + 26} ${top + 18} L${cx + 26} ${top + 4}Z`, fill:C.accS, stroke:C.acc, 'stroke-width':1.5}, spec);
      S('path', {d:`M${cx - 26} ${top + L + 56} L${cx - 26} ${top + L + 42} Q${cx - w} ${top + L + 36} ${cx - w} ${top + L + 26} L${cx - w} ${mid + 26} L${cx - 5} ${mid + 12} L${cx + 5} ${mid + 12} L${cx + w} ${mid + 26} L${cx + w} ${top + L + 26} Q${cx + w} ${top + L + 36} ${cx + 26} ${top + L + 42} L${cx + 26} ${top + L + 56}Z`, fill:C.accS, stroke:C.acc, 'stroke-width':1.5}, spec); }
    arrow(spec, cx, top - 28, cx, top - 50, C.bad, 2.2, 8); arrow(spec, cx, top + L + 88, cx, top + L + 110, C.bad, 2.2, 8);
  }
  function mark(e, txt, dy, anchor){ const f = curve[kind]; S('circle', {cx:A.X(e), cy:A.Y(f(e)), r:3.5, fill:C.ink}, marks); T(marks, A.X(e) + (anchor === 'end' ? -6 : 6), A.Y(f(e)) + dy, txt, {'text-anchor':anchor || 'start', 'font-size':11.5, 'font-weight':600}); }
  const c = ctl(st);
  seg(c, [['f', 'Ֆիզիկական σ<sub>տ</sub>'], ['c', 'Պայմանական σ<sub>0,2</sub>']], kind, k => { kind = k; An.t = 0; An.draw(); });
  const An = anim(st, (dt, t) => {
    const f = curve[kind], ph = t % 8, e = Math.min(end, ph / 6 * end), broken = ph >= 6;
    attrs(path, {d:A.fn(f, 0, Math.max(e, 1e-4), 200)}); attrs(dot, {cx:A.X(e), cy:A.Y(f(e)), opacity:broken ? 0 : 1});
    clear(marks);
    if (e > .008){ S('path', {d:`M${A.X(0) + 26} ${A.Y(0)} A26 26 0 0 0 ${A.X(0) + 26 * Math.cos(Math.atan2(A.Y(0) - A.Y(.6), A.X(.012) - A.X(0)))} ${A.Y(0) - 26 * Math.sin(Math.atan2(A.Y(0) - A.Y(.6), A.X(.012) - A.X(0)))}`, fill:'none', stroke:C.muted}, marks); T(marks, A.X(0) + 30, A.Y(0) - 6, 'α', {fill:C.muted}); T(marks, A.X(.014) + 4, A.Y(.3), 'Հուկ՝ E = tg α', {'font-size':11, fill:C.muted}); }
    if (kind === 'f' && e > .03) mark(.03, 'σ_{տ}՝ հարթակ', -8);
    if (kind === 'c' && e > .02){ const off = .002 * 6; S('line', {x1:A.X(off), y1:A.Y(0), x2:A.X(off + .012 * 1.07), y2:A.Y(.64), stroke:C.muted, 'stroke-dasharray':'4 3'}, marks); T(marks, A.X(off) - 2, A.Y(0) + 14, '0,2%', {'font-size':10, fill:C.muted});
      let x = .013; for (; x < .1; x += .0005) if (curve.c(x) <= (x - off) / .012 * .6) break; mark(x, 'σ_{0,2}', 14); }
    if (e > .25) mark(.25, 'σ_{բ}՝ ամենամեծ բեռ', -10, 'end');
    if (e > .27) T(marks, A.X(.29), A.Y(.95) - 20, 'վզիկ', {'font-size':11, fill:C.muted});
    if (broken) mark(end, 'խզում', -8, 'end');
    specimen(e, broken);
    setT(note, broken ? 'δ = (l − l₀)/l₀·100%,   ψ = (F₀ − F)/F₀·100%' : e < .012 ? 'առաձգական դեֆորմացիա' : e < .25 ? 'պլաստիկ դեֆորմացիա' : 'վզիկի առաջացում');
  }, c);
}};

/* ---------- 1.4 hardness ---------- */
VIZ.hardness = {kind:'a', cap:'Կարծրության որոշման երեք մեթոդ. <b>Բրինել</b>՝ մխված պողպատե գնդիկ, HB = P/F (դրոշմահետքի մակերես), <b>Վիկերս</b>՝ քառանիստ ալմաստե բուրգ 136°, HV = 1,8544·P/d², <b>Ռոկվել</b>՝ ալմաստե կոն 120°, ըստ խրման խորության։',
f(st){
  const s = svg(st, 640, 260, 'Կարծրություն'), M = [['Բրինել, HB', 'b'], ['Վիկերս, HV', 'v'], ['Ռոկվել, HR', 'r']];
  const G = M.map(([n], i) => { T(s, 110 + i * 210, 18, n, {'text-anchor':'middle', 'font-weight':700}); return S('g', {}, s); });
  const D = M.map((_, i) => { T(s, 110 + i * 210, 250, ['HB = P/F', 'HV = 1,8544·P/d²', 'ըստ խորության h'][i], {'text-anchor':'middle', 'font-size':12}); return S('g', {}, s); });
  anim(st, (dt, t) => {
    const ph = t % 4, dep = ph < 1.2 ? ss(ph / 1.2) : ph < 2 ? 1 : 1 - ss((ph - 2) / 1), shown = ph > 1.2;
    M.forEach(([n, k], i) => {
      const cx = 110 + i * 210, sy = 130, g = clear(G[i]), d = clear(D[i]), pen = dep * 14;
      // specimen with the dent
      const dw = k === 'b' ? 30 : k === 'v' ? 26 : 18, dh = k === 'r' ? 18 : 12;
      S('path', {d:`M${cx - 85} ${sy} L${cx - dw} ${sy} ${k === 'b' ? `Q${cx} ${sy + dh * 2 * (shown ? 1 : dep)} ${cx + dw} ${sy}` : `L${cx} ${sy + dh * (shown ? 1 : dep)} L${cx + dw} ${sy}`} L${cx + 85} ${sy} L${cx + 85} ${sy + 50} L${cx - 85} ${sy + 50}Z`, fill:C.sunk, stroke:C.ink}, g);
      // indenter
      const y = sy - 50 + pen + 36 * dep;
      if (k === 'b') S('circle', {cx, cy:y - 2, r:dw + 2, fill:C.muted}, g);
      else { const half = k === 'v' ? Math.tan(68 * Math.PI / 180) : Math.tan(60 * Math.PI / 180), hh = 50; S('path', {d:`M${cx} ${y + 26} L${cx - hh / half * 1.0} ${y + 26 - hh} L${cx + hh / half} ${y + 26 - hh}Z`, fill:k === 'v' ? C.acc : C.heat, opacity:.85}, g);
        T(g, cx, y - 30, k === 'v' ? '136°' : '120°', {'text-anchor':'middle', 'font-size':11, fill:C.muted}); }
      arrow(g, cx, y - (k === 'b' ? 60 : 50), cx, y - (k === 'b' ? 36 : 28), C.bad, 2.2, 8); T(g, cx + 8, y - 48, 'P', {'font-weight':700, fill:C.bad});
      // top view of the imprint
      if (shown){ const vy = 212;
        if (k === 'b'){ S('circle', {cx, cy:vy, r:16, fill:C.sunk, stroke:C.ink}, d); S('line', {x1:cx - 16, x2:cx + 16, y1:vy, y2:vy, stroke:C.heat, 'stroke-width':2}, d); T(d, cx + 20, vy + 4, 'd', {fill:C.heat}); }
        else if (k === 'v'){ S('rect', {x:cx - 12, y:vy - 12, width:24, height:24, transform:`rotate(45 ${cx} ${vy})`, fill:C.sunk, stroke:C.ink}, d); S('line', {x1:cx - 17, x2:cx + 17, y1:vy, y2:vy, stroke:C.heat, 'stroke-width':2}, d); T(d, cx + 21, vy + 4, 'd', {fill:C.heat}); }
        else { S('line', {x1:cx + 26, x2:cx + 26, y1:sy, y2:sy + 18, stroke:C.heat, 'stroke-width':2}, g); T(g, cx + 31, sy + 14, 'h', {fill:C.heat, 'font-weight':700}); } }
    });
  }, ctl(st));
}};

/* ---------- 1.5 density and hysteresis ---------- */
VIZ.density = {kind:'s', cap:'Պարզ մետաղների խտությունը՝ 0,53 գ/սմ³ (լիթիում) մինչև 22,5 գ/սմ³ (իրիդիում)։ 3 գ/սմ³-ից փոքր խտությամբ մետաղները (մագնեզիում, ալյումին) <b>թեթև</b> են, տեխնիկական մետաղները հիմնականում <b>ծանր</b> են (&gt; 5 գ/սմ³)։',
f(st){
  const s = svg(st, 640, 120, 'Խտություն'), X = v => 30 + v / 24 * 580;
  S('rect', {x:X(0), y:40, width:X(3) - X(0), height:26, fill:C.accS}, s); S('rect', {x:X(5), y:40, width:X(24) - X(5), height:26, fill:C.heatS}, s);
  T(s, (X(0) + X(3)) / 2, 57, 'թեթև', {'text-anchor':'middle', 'font-size':11, 'font-weight':600}); T(s, (X(5) + X(24)) / 2, 57, 'ծանր (&gt; 5)'.replace('&gt;', '>'), {'text-anchor':'middle', 'font-size':11, 'font-weight':600});
  arrow(s, X(0), 80, X(24) + 8, 80, C.muted, 1.2, 6);
  for (let v = 0; v <= 24; v += 3) { S('line', {x1:X(v), x2:X(v), y1:76, y2:84, stroke:C.muted}, s); T(s, X(v), 98, String(v), {'text-anchor':'middle', 'font-size':10, fill:C.muted}); }
  T(s, X(24), 114, 'գ/սմ³', {'text-anchor':'end', 'font-size':10, fill:C.muted});
  [[.53, 'Li 0,53'], [3, '3'], [5, '5'], [22.5, 'Ir 22,5']].forEach(([v, n], i) => { S('line', {x1:X(v), x2:X(v), y1:30, y2:80, stroke:C.ink, 'stroke-width':i % 3 ? 1 : 2}, s); T(s, X(v), 24, n, {'text-anchor':i === 3 ? 'end' : 'middle', 'font-size':11, 'font-weight':i % 3 ? 400 : 700}); });
}};
VIZ.hyster = {kind:'a', cap:'Հիստերեզիսի օղակ. H դաշտի աճի ժամանակ մետաղը մագնիսանում է մինչև <b>հագեցում</b>, դաշտը հանելուց հետո մնում է <b>մնացորդային ինդուկցիա B<sub>r</sub></b>, այն վերացնող հակառակ դաշտը՝ <b>կոերցիտիվ ուժ H<sub>c</sub></b>։ μ = B/H՝ մագնիսական թափանցելիություն։',
f(st){
  const s = svg(st, 560, 270, 'Հիստերեզիս'), A = {X:h => 280 + h * 120, Y:b => 135 - b * 100};
  arrow(s, 60, 135, 510, 135, C.muted, 1.2, 6); arrow(s, 280, 255, 280, 18, C.muted, 1.2, 6); T(s, 505, 152, 'H', {fill:C.muted}); T(s, 288, 24, 'B', {fill:C.muted});
  const Hc = .45, a = .35, Bs = 1, hm = 1.6;
  const up = h => Bs * Math.tanh((h - Hc) / a), dn = h => Bs * Math.tanh((h + Hc) / a), ini = h => Bs * Math.tanh(h / (a * 1.6)) * .98;
  const P = []; for (let i = 0; i <= 60; i++) P.push([A.X(lerp(-hm, hm, i / 60)), A.Y(up(lerp(-hm, hm, i / 60)))]); for (let i = 0; i <= 60; i++) P.push([A.X(lerp(hm, -hm, i / 60)), A.Y(dn(lerp(hm, -hm, i / 60)))]);
  S('path', {d:pts(P), fill:'none', stroke:C.line, 'stroke-width':2}, s);
  const trace = S('path', {fill:'none', stroke:C.acc, 'stroke-width':3}, s), dot = S('circle', {r:6, fill:C.heat}, s), lab = T(s, 30, 30, '', {'font-weight':600});
  const Br = dn(0), hc = -Hc;
  S('circle', {cx:A.X(0), cy:A.Y(Br), r:4, fill:C.ink}, s); T(s, A.X(0) + 8, A.Y(Br) - 6, 'B_{r}', {'font-weight':700});
  S('circle', {cx:A.X(hc), cy:A.Y(0), r:4, fill:C.ink}, s); T(s, A.X(hc) - 8, A.Y(0) + 18, '−H_{c}', {'font-weight':700, 'text-anchor':'end'});
  T(s, A.X(hm) - 4, A.Y(Bs) - 6, 'հագեցում', {'text-anchor':'end', 'font-size':11, fill:C.muted});
  const seq = [[u => [u * hm, ini(u * hm)], 'առաջնային մագնիսացում'], [u => [lerp(hm, 0, u), dn(lerp(hm, 0, u))], 'դաշտը հանում ենք → B_{r}'], [u => [lerp(0, -Hc, u), dn(lerp(0, -Hc, u))], 'հակառակ դաշտ → B = 0 (H_{c})'],
    [u => [lerp(-Hc, -hm, u), dn(lerp(-Hc, -hm, u))], 'հագեցում հակառակ ուղղությամբ'], [u => [lerp(-hm, hm, u), up(lerp(-hm, hm, u))], 'օղակի ստորին ճյուղ']];
  anim(st, (dt, t) => {
    const u = (t / 1.6) % seq.length, i = Math.floor(u), r = u - i, tr = [];
    for (let k = 0; k <= 30; k++){ const q = seq[i][0](r * k / 30); tr.push([A.X(q[0]), A.Y(q[1])]); }
    attrs(trace, {d:pts(tr)}); const q = seq[i][0](r); attrs(dot, {cx:A.X(q[0]), cy:A.Y(q[1])}); setT(lab, seq[i][1]);
  }, ctl(st));
}};

/* ---------- 2.1 metallic bond ---------- */
VIZ.metalbond = {kind:'a', cap:'Մետաղական կապ՝ դրական իոններ և նրանց միջև քաոսային շարժվող ազատ էլեկտրոններ (<b>էլեկտրոնային գազ</b>)։ Արտաքին ուժի ազդեցությամբ մետաղում շերտերի տեղաշարժը կապը չի խզում, իոնային բյուրեղում՝ նույնանուն լիցքերը հանդիպում են իրար։',
f(st){
  const s = svg(st, 640, 230, 'Մետաղական կապ'), panels = [[20, 'մետաղական'], [340, 'իոնային']], els = [], r = rnd(4);
  const top = panels.map(([x, n], k) => { T(s, x + 140, 18, n, {'text-anchor':'middle', 'font-weight':700}); S('rect', {x, y:30, width:280, height:150, rx:8, fill:C.sunk}, s);
    const rows = []; for (let j = 0; j < 3; j++){ const g = S('g', {}, s), row = [];
      for (let i = 0; i < 6; i++){ const plus = k === 0 || (i + j) % 2 === 0, cx = x + 35 + i * 42, cy = 65 + j * 42;
        S('circle', {cx, cy, r:14, fill:plus ? C.heatS : C.accS, stroke:plus ? C.heat : C.acc}, g); T(g, cx, cy + 5, plus ? '+' : '−', {'text-anchor':'middle', 'font-weight':700, 'font-size':15}); }
      rows.push(g); }
    if (k === 0) for (let i = 0; i < 26; i++) els.push({x:x + r() * 280, y:30 + r() * 150, vx:r() - .5, vy:r() - .5, x0:x, c:S('circle', {r:2.5, fill:C.acc}, s)});
    return rows[0]; });
  const msg = [T(s, 160, 205, '', {'text-anchor':'middle', 'font-weight':600}), T(s, 480, 205, '', {'text-anchor':'middle', 'font-weight':600})], rep = S('g', {}, s);
  arrow(s, 300, 50, 330, 50, C.muted, 1.5, 6);
  anim(st, (dt, t) => {
    const ph = t % 5, sh = ph < 1 ? 0 : ph < 2 ? ss(ph - 1) : ph < 4 ? 1 : 1 - ss(ph - 4);
    top.forEach(g => g.setAttribute('transform', `translate(${sh * 42} 0)`));
    els.forEach(e => { e.x += e.vx * 120 * dt; e.y += e.vy * 120 * dt; if (e.x < e.x0 + 4 || e.x > e.x0 + 276) e.vx *= -1; if (e.y < 34 || e.y > 176) e.vy *= -1; attrs(e.c, {cx:e.x, cy:e.y}); });
    clear(rep);
    if (sh > .9){ for (let i = 0; i < 5; i++){ const x = 340 + 35 + 42 + i * 42; arrow(rep, x, 79, x, 70, C.bad, 1.6, 5); arrow(rep, x, 92, x, 101, C.bad, 1.6, 5); } }
    setT(msg[0], sh > .9 ? 'կապը չի խզվում' : ''); msg[0].style.fill = C.good;
    setT(msg[1], sh > .9 ? 'նույնանուն լիցքեր → վանողություն' : ''); msg[1].style.fill = C.bad;
  }, ctl(st));
}};

/* ---------- 2.2 crystalline vs amorphous ---------- */
VIZ.cooling = {kind:'a', cap:'Բյուրեղային մարմինը պնդանում է <b>որոշակի ջերմաստիճանում</b>, անջատելով բյուրեղացման թաքնված ջերմությունը (սառեցման կորի վրա՝ <b>հորիզոնական հարթակ</b>), ատոմները դասավորվում են կանոնավոր։ Ամորֆ մարմինը աստիճանաբար է փափկում/պնդանում, կանոնավոր դասավորություն չկա։',
f(st){
  const s = svg(st, 640, 250, 'Սառեցման կորեր'), A = axes(s, {x:40, y:24, w:300, h:190, xr:[0, 1], yr:[0, 1], xl:'ժամանակ', yl:'T'});
  const fc = u => u < .3 ? 1 - u / .3 * .45 : u < .62 ? .55 : .55 - (u - .62) / .38 * .45, fa = u => .95 * Math.exp(-u * 1.6) + .05;
  S('line', {x1:A.X(0), x2:A.X(1), y1:A.Y(.55), y2:A.Y(.55), stroke:C.line, 'stroke-dasharray':'4 4'}, s); T(s, A.X(0) - 4, A.Y(.55) + 4, 'T_{կ}', {'text-anchor':'end', 'font-size':11});
  const pc = S('path', {fill:'none', stroke:C.acc, 'stroke-width':2.6}, s), pa = S('path', {fill:'none', stroke:C.heat, 'stroke-width':2.2, 'stroke-dasharray':'6 4'}, s);
  T(s, 360, 32, '—— բյուրեղային', {fill:C.acc, 'font-size':11}); T(s, 360, 48, '– – ամորֆ', {fill:C.heat, 'font-size':11});
  const pl = T(s, A.X(.46), A.Y(.55) - 8, '', {'text-anchor':'middle', 'font-size':11, fill:C.acc});
  const r = rnd(2), at = [], bx = 470, by = 70;
  for (let j = 0; j < 5; j++) for (let i = 0; i < 6; i++) at.push({gx:bx + i * 22, gy:by + j * 22, rx:bx - 10 + r() * 130, ry:by - 10 + r() * 110, c:S('circle', {r:7, fill:C.acc}, s)});
  T(s, bx + 55, 196, '', {}); const lab = T(s, bx + 55, 200, '', {'text-anchor':'middle', 'font-size':11, 'font-weight':600});
  anim(st, (dt, t) => {
    const u = Math.min(1, (t % 7) / 5.5);
    attrs(pc, {d:A.fn(fc, 0, Math.max(u, .001), 150)}); attrs(pa, {d:A.fn(fa, 0, Math.max(u, .001), 150)});
    setT(pl, u > .35 ? 'հարթակ՝ թաքնված ջերմություն' : '');
    const order = ss((u - .3) / .32), jit = u < .3 ? 3 : 3 * (1 - order) + .6;
    at.forEach((a, i) => attrs(a.c, {cx:lerp(a.rx, a.gx, order) + Math.sin(t * 9 + i) * jit, cy:lerp(a.ry, a.gy, order) + Math.cos(t * 8 + i * 2) * jit}));
    setT(lab, u < .3 ? 'հեղուկ' : u < .62 ? 'բյուրեղացում...' : 'բյուրեղ՝ կանոնավոր դասավորություն');
  }, ctl(st));
}};

/* ---------- 2.3–2.4 unit cells ---------- */
VIZ.cell = {kind:'i', cap: a => a === 'K6'
  ? 'Պարզ խորանարդային ցանց К6. տարրական բջջի կողը՝ ցանցի պարամետր a։ Կոորդինացիոն թիվը՝ ամենամոտ և հավասար հեռավորության վրա գտնվող հարևանների թիվը՝ 6։ Պտտեք մկնիկով կամ մատով։'
  : 'Մետաղների ցանցերի հիմնական տիպերը՝ К8, К12, Г12։ «Կոորդինացիոն թիվ» ռեժիմում կանաչով են ամենամոտ հարևանները (К8-ում՝ 8, К12-ում և Г12-ում՝ 12)։ Պտտեք մկնիկով կամ մատով։',
f(st, a){
  const c = ctl(st);
  const v = cell3d(st, {kind:a === 'K6' ? 'K6' : 'K8', ctl:c, max:380});
  let k = a === 'K6' ? 'K6' : 'K8', m = 'cell';
  const o = out(st), info = {K6:'Պարզ խորանարդային՝ К6', K8:'Fe<sub>α</sub>, քրոմ, վոլֆրամ, մոլիբդեն, վանադիում, տիտան (բարձր T), ցիրկոնիում, նիոբիում', K12:'Fe<sub>γ</sub>, պղինձ, ալյումին, արծաթ, ոսկի, նիկել, կապար', G12:'կոբալտ, տիտան, մագնեզիում, ցինկ, կադմիում'};
  const upd = () => { v.set(k, m); o.innerHTML = `<b>${STRUCT[k].n}</b>. ատոմ մեկ բջջում՝ <span class="mono">${STRUCT[k].cnt}</span>, կոորդինացիոն թիվ՝ <b>${STRUCT[k].k}</b>${k !== 'K6' ? '<br><span class="vz-mut">Մետաղներ՝ ' + info[k] + '</span>' : ''}`; };
  if (a !== 'K6') seg(c, [['K8', 'К8'], ['K12', 'К12'], ['G12', 'Г12']], k, x => { k = x; upd(); });
  seg(c, [['cell', 'Տարրական բջիջ'], ['cn', 'Կոորդինացիոն թիվ']], m, x => { m = x; upd(); });
  upd();
}};

/* ---------- 2.5 polymorphism of iron, tin plague ---------- */
VIZ.polyfe = {kind:'i', cap:'Երկաթի պոլիմորֆիզմը. 910°C-ից ցածր К8 (Fe<sub>α</sub>), 910–1401°C՝ К12 (Fe<sub>γ</sub>), 1401–1539°C՝ կրկին К8 (Fe<sub>δ</sub>)։ Անագ՝ սպիտակ Sn<sub>β</sub> (7,3 գ/սմ³) ցածր ջերմաստիճանում վերածվում է գորշ Sn<sub>α</sub>-ի (5,75 գ/սմ³). ծավալը մեծանում է՝ «անագային ժանտախտ»։',
f(st){
  const row = H('div', {class:'vz-row'}, st), s = svg(row, 300, 260, 'Ջերմաչափ'), Y = v => 230 - v / 1650 * 200;
  S('rect', {x:60, y:Y(1650), width:26, height:Y(0) - Y(1650), rx:13, fill:C.sunk, stroke:C.line}, s);
  const fill = S('rect', {x:64, width:18, rx:9, fill:C.heat}, s);
  [[910, 'A₃'], [1401, 'A₄'], [1539, 'հալում']].forEach(([v, n]) => { S('line', {x1:56, x2:94, y1:Y(v), y2:Y(v), stroke:C.ink}, s); T(s, 50, Y(v) + 4, v + '°C', {'text-anchor':'end', 'font-size':11}); T(s, 100, Y(v) + 4, n, {'font-size':10, fill:C.muted}); });
  [[455, 'Fe_{α}, К8'], [1155, 'Fe_{γ}, К12'], [1470, 'Fe_{δ}, К8']].forEach(([v, n]) => T(s, 140, Y(v) + 4, n, {'font-weight':600}));
  const box = H('div', {}, row), v = cell3d(box, {kind:'K8', max:300, w:280, h:240});
  const lab = T(s, 150, 22, '', {'font-weight':700, 'font-size':14});
  let cur = '';
  function draw(t){ attrs(fill, {y:Y(t), height:Y(0) - Y(t)});
    const k = t < 910 ? 'α' : t < 1401 ? 'γ' : t < 1539 ? 'δ' : 'L';
    if (k !== cur){ cur = k; if (k === 'L') v.liquid(); else v.set(k === 'γ' ? 'K12' : 'K8', 'cell'); }
    setT(lab, k === 'L' ? 'հեղուկ երկաթ' : 'Fe_{' + k + '}՝ ' + (k === 'γ' ? 'К12' : 'К8')); }
  slider(ctl(st), 'T', 20, 1600, 5, 700, x => x + '°C', draw); draw(700);
  const t2 = svg(st, 640, 130, 'Անագ'), r = Math.cbrt(7.3 / 5.75);
  S('rect', {x:70, y:30, width:70, height:70, fill:'var(--surface)', stroke:C.ink, 'stroke-width':2}, t2); T(t2, 105, 120, 'Sn_{β}, 7,3 գ/սմ³', {'text-anchor':'middle'});
  arrow(t2, 170, 65, 260, 65, C.muted, 2, 8); T(t2, 215, 56, 'ցածր T', {'text-anchor':'middle', 'font-size':11, fill:C.muted});
  const big = 70 * r, rr = rnd(6);
  for (let i = 0; i < 40; i++) S('circle', {cx:290 + rr() * big, cy:100 - rr() * big, r:2 + rr() * 4, fill:C.muted}, t2);
  S('rect', {x:290, y:100 - big, width:big, height:big, fill:'none', stroke:C.ink, 'stroke-dasharray':'4 3'}, t2); T(t2, 290 + big / 2, 120, 'Sn_{α}, 5,75 գ/սմ³', {'text-anchor':'middle'});
  T(t2, 400, 60, 'Միևնույն զանգվածի ծավալը՝ ×' + fmt(7.3 / 5.75, 2), {'font-weight':600}); T(t2, 400, 80, 'փխրուն փոշի, իրը փշրվում է', {fill:C.muted});
}};

/* ---------- 2.6 anisotropy ---------- */
VIZ.aniso = {kind:'s', cap:'Միաբյուրեղում տարբեր ուղղություններով ատոմների խտությունը տարբեր է, ուստի հատկությունները նույնպես (<b>անիզոտրոպիա</b>)։ Ամորֆ նյութը իզոտրոպ է, իսկ տարբեր կողմնորոշմամբ հատիկներից կազմված բազմաբյուրեղը՝ գործնականում իզոտրոպ (քվազիիզոտրոպ)։',
f(st){
  const s = svg(st, 640, 230, 'Անիզոտրոպիա');
  [['միաբյուրեղ', 105], ['ամորֆ', 320], ['բազմաբյուրեղ', 535]].forEach(([n, x]) => T(s, x, 18, n, {'text-anchor':'middle', 'font-weight':700}));
  const a = 26;
  for (let j = 0; j < 7; j++) for (let i = 0; i < 7; i++) S('circle', {cx:27 + i * a, cy:40 + j * a, r:5, fill:C.acc}, s);
  S('line', {x1:20, y1:40 + 3 * a, x2:190, y2:40 + 3 * a, stroke:C.heat, 'stroke-width':2.5, opacity:.8}, s);
  S('line', {x1:27, y1:40, x2:27 + 6 * a, y2:40 + 6 * a, stroke:C.good, 'stroke-width':2.5, opacity:.8}, s);
  T(s, 105, 222, 'շարքով՝ 1/a, անկյունագծով՝ 1/(a√2)', {'text-anchor':'middle', 'font-size':11});
  const r = rnd(5); for (let i = 0; i < 46; i++) S('circle', {cx:240 + r() * 160, cy:36 + r() * 160, r:5, fill:C.acc}, s);
  T(s, 320, 222, 'կանոնավոր դասավորություն չկա', {'text-anchor':'middle', 'font-size':11});
  const G = grains(160, 160, 9, 12), g = S('g', {}, s);
  // each grain gets a short-hatched lattice at its own orientation
  G.P.forEach((p, i) => { const ang = hash(i) * Math.PI; for (let y = 0; y < 160; y += 9) for (let x = 0; x < 160; x += 9){ if (G.lab[(y | 0) * 160 + (x | 0)] !== i || G.edge[(y | 0) * 160 + (x | 0)]) continue;
    S('line', {x1:455 + x - 3 * Math.cos(ang), y1:36 + y - 3 * Math.sin(ang), x2:455 + x + 3 * Math.cos(ang), y2:36 + y + 3 * Math.sin(ang), stroke:C.acc, 'stroke-width':1.6}, g); } });
  for (let y = 0; y < 160; y += 2) for (let x = 0; x < 160; x += 2) if (G.edge[y * 160 + x]) S('rect', {x:455 + x, y:36 + y, width:2, height:2, fill:C.ink}, g);
  T(s, 535, 222, 'հատիկները՝ տարբեր կողմնորոշմամբ', {'text-anchor':'middle', 'font-size':11});
}};

/* ---------- 2.7 lattice defects ---------- */
VIZ.defects = {kind:'i', cap:'Բյուրեղային ցանցի թերություններ. <b>կետային</b> (վականսիա, միջհանգուցային ատոմ, խառնուկի ատոմ), <b>գծային</b> (եզրային դիսլոկացիա ⊥՝ ավելորդ կիսահարթության եզրը) և <b>մակերևութային</b> (հատիկների սահմաններ)։ Ատոմները մշտապես տատանվում են (~10¹³ Հց)։',
f(st){
  const s = svg(st, 640, 270, 'Թերություններ'), g = S('g', {}, s), hl = S('g', {}, s), lab = T(s, 320, 262, '', {'text-anchor':'middle', 'font-weight':600});
  let mode = 'v', A = [];
  const a = 34, cx = 320, cy = 125;
  function build(){
    A = [];
    if (mode === 'd'){
      for (let j = 0; j < 7; j++){ const top = j < 3, n = top ? 11 : 10, d = top ? 3 - j : j - 2, k = top ? lerp(.9, .97, (d - 1) / 2) : 1;
        for (let i = 0; i < n; i++) A.push({x:top ? cx + (i - 5) * a * k : cx + (i - 4.5) * a * (d === 1 ? .97 : 1), y:cy - 3 * a + j * a + (top ? 0 : -6 * Math.exp(-d)), r:9, f:top && i === 5 ? C.heat : C.acc}); }
    } else if (mode === 'g'){
      for (let j = -4; j <= 4; j++) for (let i = -6; i <= 6; i++){ const left = i < 0, ang = left ? -.28 : .22, x = i * a * .9, y = j * a * .9, X = x * Math.cos(ang) - y * Math.sin(ang), Y = x * Math.sin(ang) + y * Math.cos(ang), px = cx + X + (left ? -14 : 14), py = cy + Y;
        if (Math.abs(py - cy) < 120 && (left ? px < cx - 6 : px > cx + 6) && px > 30 && px < 610) A.push({x:px, y:py, r:9, f:C.acc}); }
    } else {
      for (let j = 0; j < 7; j++) for (let i = 0; i < 11; i++){ const x = cx + (i - 5) * a, y = cy + (j - 3) * a;
        if (mode === 'v' && i === 5 && j === 3) continue;
        const sub = mode === 'i' && ((i === 2 && j === 2) || (i === 8 && j === 4)), sub2 = mode === 'i' && i === 6 && j === 1;
        A.push({x, y, r:sub ? 12 : sub2 ? 7 : 9, f:sub || sub2 ? C.heat : C.acc}); }
      if (mode === 'n') A.push({x:cx + a / 2, y:cy + a / 2, r:6, f:C.heat});
      if (mode === 'i') A.push({x:cx - 2.5 * a, y:cy + .5 * a, r:5, f:C.good});
    }
    clear(hl);
    if (mode === 'v') S('circle', {cx, cy, r:13, fill:'none', stroke:C.heat, 'stroke-width':2, 'stroke-dasharray':'4 3'}, hl);
    if (mode === 'd'){ const y = cy - a / 2 + 4; S('line', {x1:cx - 10, x2:cx + 10, y1:y, y2:y, stroke:C.bad, 'stroke-width':3}, hl); S('line', {x1:cx, x2:cx, y1:y, y2:y - 18, stroke:C.bad, 'stroke-width':3}, hl);
      S('line', {x1:30, x2:610, y1:y, y2:y, stroke:C.bad, 'stroke-dasharray':'3 5', opacity:.6}, hl); }
    if (mode === 'g') S('path', {d:`M${cx} 0 V250`, stroke:C.bad, 'stroke-dasharray':'4 4', 'stroke-width':1.5}, hl);
    setT(lab, {v:'վականսիա՝ դատարկ հանգույց', n:'միջհանգուցային ատոմ', i:'խառնուկների ատոմներ (տեղակալված և ներդրված)', d:'եզրային դիսլոկացիա ⊥՝ ավելորդ կիսահարթության ներքին եզրը', g:'հատիկների մեծանկյուն սահման՝ դասավորությունը խախտված է'}[mode]);
    clear(g); A.forEach(p => p.c = S('circle', {r:p.r, fill:p.f}, g));
  }
  seg(ctl(st), [['v', 'վականսիա'], ['n', 'միջհանգուցային'], ['i', 'խառնուկ'], ['d', 'դիսլոկացիա ⊥'], ['g', 'հատիկի սահման']], mode, m => { mode = m; build(); An.draw(); });
  build();
  const An = anim(st, (dt, t) => A.forEach((p, i) => attrs(p.c, {cx:p.x + Math.sin(t * 13 + i * 1.7) * 1.4, cy:p.y + Math.cos(t * 11 + i * 2.3) * 1.4})), st.querySelector('.vz-ctl'));
}};

/* ---------- 3.1 free energy ---------- */
VIZ.fenergy = {kind:'i', cap: a => a === '2'
  ? 'Պոլիմորֆ մետաղի մոդիֆիկացիաների ազատ էներգիան. T<sub>կ</sub>-ից ցածր կայուն է M<sub>α</sub>-ն (փոքր F), բարձր՝ M<sub>β</sub>-ն։ Պինդ վիճակում ցանցի փոփոխությունը՝ <b>երկրորդային բյուրեղացում</b>։'
  : 'Հեղուկ և պինդ վիճակների ազատ էներգիան. T<sub>կ</sub>-ում F<sub>հ</sub> = F<sub>պ</sub>, ավելի բարձր կայուն է հեղուկը, ցածր՝ պինդը։ Բյուրեղացումը սկսվում է միայն գերսառեցված մետաղում. ΔT-ն <b>գերսառեցման աստիճանն</b> է։',
f(st, a){
  const two = a === '2', s = svg(st, 600, 250, 'Ազատ էներգիա'), A = axes(s, {x:50, y:20, w:360, h:200, xr:[0, 1], yr:[0, 1], xl:'T', yl:'F'});
  const fl = x => .95 - .85 * x, fs = x => .8 - .55 * x, Tk = (.95 - .8) / (.85 - .55);
  S('path', {d:A.fn(fl, .02, .98), fill:'none', stroke:two ? C.good : C.heat, 'stroke-width':2.5}, s); S('path', {d:A.fn(fs, .02, .98), fill:'none', stroke:C.acc, 'stroke-width':2.5}, s);
  T(s, A.X(.98), A.Y(fl(.98)) + 16, two ? 'F_{β}' : 'F_{հ}', {'text-anchor':'end', fill:two ? C.good : C.heat, 'font-weight':700}); T(s, A.X(.98), A.Y(fs(.98)) - 8, two ? 'F_{α}' : 'F_{պ}', {'text-anchor':'end', fill:C.acc, 'font-weight':700});
  S('line', {x1:A.X(Tk), x2:A.X(Tk), y1:A.Y(0), y2:A.Y(fs(Tk)), stroke:C.muted, 'stroke-dasharray':'4 3'}, s); T(s, A.X(Tk), A.Y(0) + 15, 'T_{կ}', {'text-anchor':'middle'});
  const cur = S('line', {stroke:C.ink, 'stroke-width':1.5}, s), dT = S('g', {}, s), r1 = T(s, 430, 70, '', {'font-weight':700}), r2 = T(s, 430, 94, '', {fill:C.muted});
  function draw(x){
    attrs(cur, {x1:A.X(x), x2:A.X(x), y1:A.Y(0), y2:A.Y(1)}); clear(dT);
    const liq = x > Tk;
    setT(r1, 'կայուն է՝ ' + (two ? (liq ? 'M_{β}' : 'M_{α}') : (liq ? 'հեղուկը' : 'պինդը')));
    r1.style.fill = liq ? (two ? C.good : C.heat) : C.acc;
    if (!liq && !two){ arrow(dT, A.X(Tk), A.Y(.05), A.X(x), A.Y(.05), C.bad, 1.8, 7); T(dT, (A.X(Tk) + A.X(x)) / 2, A.Y(.05) - 6, 'ΔT', {'text-anchor':'middle', fill:C.bad, 'font-weight':700}); }
    setT(r2, two ? '' : liq ? '' : 'գերսառեցում ΔT = T_{կ} − T');
  }
  slider(ctl(st), 'T', .05, .95, .01, .35, () => '', draw); draw(.35);
}};

/* ---------- 3.2 nucleation and growth ---------- */
VIZ.nucleation = {kind:'a', cap:'Բյուրեղացումը՝ <b>կենտրոնների առաջացում</b> (արագություն n) և դրանց <b>աճ</b> (արագություն c)։ Գերսառեցման աճով n-ը աճում է ավելի արագ, քան c-ն, ուստի արագ սառեցումը տալիս է <b>մանր հատիկ</b>։ Համեմատեք փոքր և մեծ ΔT-ով։',
f(st){
  const W = 200, Hh = 120, cv = canvas(st, W, Hh); cv.c.style.imageRendering = 'pixelated';
  let dT = 2, N = [], lab = new Int16Array(W * Hh), done = 0, t0 = 0, wait = 0;
  const o = out(st), c = ctl(st);
  slider(c, 'Գերսառեցում ΔT', 1, 5, 1, 2, v => ['', 'շատ փոքր', 'փոքր', 'միջին', 'մեծ', 'շատ մեծ'][v], v => { dT = v; reset(); });
  btn(c, '↺ Նորից', () => reset());
  const pal = [];
  function reset(){ N = []; pal.length = 0; lab.fill(-1); done = 0; t0 = -1; wait = 0; }
  reset();
  const liq = rgbOf('--heat-soft'), base = [rgbOf('--accent'), rgbOf('--good'), rgbOf('--warn'), rgbOf('--muted')];
  const r = rnd(1);
  anim(st, (dt, t) => {
    if (t0 < 0) t0 = t;
    const n = 1.5 * dT ** 3, cg = 8 + 4 * dT, el = t - t0;
    if (done < W * Hh){ const cnt = Math.floor(n * dt) + (r() < (n * dt) % 1 ? 1 : 0); for (let k = 0; k < cnt && N.length < 400; k++){ const x = r() * W, y = r() * Hh; if (lab[(y | 0) * W + (x | 0)] < 0){ N.push([x, y, el]); pal.push(mixc(base[N.length % 4], [255, 255, 255], .25 + .5 * r())); } }
      const img = cv.img.data; done = 0;
      for (let y = 0; y < Hh; y++) for (let x = 0; x < W; x++){ const i = y * W + x;
        if (lab[i] < 0){ let b = -1, bd = 1e9; for (let k = 0; k < N.length; k++){ const q = N[k], rr = cg * (el - q[2]); if (rr <= 0) continue; const dx = x - q[0], dy = y - q[1], d = dx * dx + dy * dy; if (d <= rr * rr && d < bd){ bd = d; b = k; } } if (b >= 0) lab[i] = b; }
        const l = lab[i], p = l < 0 ? liq : pal[l]; if (l >= 0) done++;
        img[i * 4] = p[0]; img[i * 4 + 1] = p[1]; img[i * 4 + 2] = p[2]; img[i * 4 + 3] = 255; }
      for (let y = 0; y < Hh; y++) for (let x = 0; x < W - 1; x++){ const i = y * W + x; if (lab[i] >= 0 && ((lab[i + 1] >= 0 && lab[i + 1] !== lab[i]) || (y < Hh - 1 && lab[i + W] >= 0 && lab[i + W] !== lab[i]))) { img[i * 4] = img[i * 4 + 1] = img[i * 4 + 2] = 40; } }
      cv.g.putImageData(cv.img, 0, 0);
      o.innerHTML = `Կենտրոններ՝ <b class="mono">${N.length}</b> · պինդ բաժին՝ <b class="mono">${Math.round(done / W / Hh * 100)}%</b>${done === W * Hh ? ' · <span class="vz-good">բյուրեղացումն ավարտված է՝ ' + N.length + ' հատիկ</span>' : ''}`;
    } else if (!wait) wait = t;
    else if (t - wait > 2.5){ wait = 0; reset(); }
  }, c);
}};

/* ---------- 3.3 Curie points ---------- */
VIZ.curie = {kind:'s', cap:'Մագնիսական փոխակերպում. ֆեռոմագնիսական մետաղները Կյուրիի կետում կորցնում են ֆեռոմագնիսականությունը, իսկ բյուրեղային ցանցը և հատիկային ստրուկտուրան <b>չեն փոխվում</b>։',
f(st){
  const s = svg(st, 640, 130, 'Կյուրիի կետեր'), X = v => 40 + v / 1250 * 560;
  arrow(s, X(0), 90, X(1250) + 10, 90, C.muted, 1.2, 6); for (let v = 0; v <= 1200; v += 200){ S('line', {x1:X(v), x2:X(v), y1:86, y2:94, stroke:C.muted}, s); T(s, X(v), 108, v + '°', {'text-anchor':'middle', 'font-size':10, fill:C.muted}); }
  [['Նիկել', 360], ['Երկաթ', 769], ['Կոբալտ', 1150]].forEach(([n, v], i) => { S('rect', {x:X(0), y:22 + i * 20, width:X(v) - X(0), height:14, rx:3, fill:C.acc, opacity:.25 + i * .2}, s);
    S('circle', {cx:X(v), cy:29 + i * 20, r:4, fill:C.bad}, s); T(s, X(v) + 8, 33 + i * 20, n + ' ' + v + '°C', {'font-size':11.5, 'font-weight':600}); });
  T(s, X(0) + 4, 124, 'ձախում՝ ֆեռոմագնիսական', {'font-size':10, fill:C.muted});
}};

/* ---------- 3.4 ingot ---------- */
VIZ.ingot = {kind:'a', cap:'Պողպատե ձույլի երեք գոտին (Չեռնով). <b>1</b> մանրահատիկ կեղև կաղապարի պատերին, <b>2</b> սյունաձև բյուրեղներ՝ ջերմահեռացման ուղղությամբ, <b>3</b> կենտրոնական հավասարառանցք խոշոր բյուրեղներ, վերևում՝ կծկման խոռոչ։ Աջում՝ <b>դենդրիտի</b> աճը (առաջին, երկրորդ, երրորդ կարգի առանցքներ)։',
f(st){
  const s = svg(st, 640, 280, 'Ձույլ'), x0 = 40, x1 = 300, y0 = 30, y1 = 260, g = S('g', {}, s), dg = S('g', {}, s);
  S('path', {d:`M${x0 - 14} ${y0} V${y1 + 14} H${x1 + 14} V${y0}`, fill:'none', stroke:C.ink, 'stroke-width':12}, s);
  const r = rnd(8), fine = [], col = [], eq = [];
  for (let y = y0 + 6; y < y1; y += 12){ fine.push([x0 + 6, y, 0]); fine.push([x1 - 6, y, 0]); }
  for (let x = x0 + 14; x < x1 - 6; x += 12) fine.push([x, y1 - 6, 0]);
  for (let y = y0 + 12; y < y1 - 30; y += 14){ col.push([x0 + 12, y, 1, 0]); col.push([x1 - 12, y, -1, 0]); }
  for (let x = x0 + 26; x < x1 - 26; x += 14) col.push([x, y1 - 12, 0, -1]);
  for (let i = 0; i < 16; i++) eq.push([x0 + 85 + r() * 90, y0 + 30 + r() * 130, 8 + r() * 6, r() * 6]);
  const lab = T(s, 170, 22, '', {'text-anchor':'middle', 'font-weight':700});
  T(s, 360, 30, 'դենդրիտ', {'font-weight':700});
  const branches = []; (function br(x, y, a, len, lvl){ branches.push({x, y, a, len, lvl}); if (lvl > 2) return; const n = lvl === 0 ? 7 : 4;
    for (let i = 1; i <= n; i++){ const t = i / (n + 1), bx = x + Math.cos(a) * len * t, by = y + Math.sin(a) * len * t, l = len * (lvl === 0 ? .32 : .4) * (1 - t * .5);
      br(bx, by, a + Math.PI / 2, l, lvl + 1); br(bx, by, a - Math.PI / 2, l, lvl + 1); } })(370, 150, 0, 240, 0);
  anim(st, (dt, t) => {
    const u = (t % 9) / 7.5; clear(g); clear(dg);
    const L = [x0, x1];
    fine.forEach(([x, y]) => u > 0 && S('circle', {cx:x, cy:y, r:5.5 * ss(u / .12), fill:C.acc, opacity:.8}, g));
    const gl = ss((u - .12) / .4) * 95;
    col.forEach(([x, y, dx, dy]) => { if (gl <= 0) return; const w = dx ? gl : 10, h = dy ? gl * .9 : 10; S('rect', {x:dx > 0 ? x : dx < 0 ? x - w : x - 5, y:dy < 0 ? y - h : y - 5, width:w, height:h, rx:3, fill:C.good, opacity:.6, stroke:C.surf}, g); });
    const ue = ss((u - .52) / .25);
    eq.forEach(([x, y, rr, k]) => ue > 0 && S('polygon', {points:Array.from({length:6}, (_, i) => { const a = i * Math.PI / 3 + k; return [x + rr * ue * Math.cos(a), y + rr * ue * Math.sin(a)].join(','); }).join(' '), fill:C.warn, opacity:.7, stroke:C.surf}, g));
    const uc = ss((u - .8) / .15);
    if (uc > 0) S('path', {d:`M${170 - 34 * uc} ${y0} Q170 ${y0 + 6} ${170 + 34 * uc} ${y0} L170 ${y0 + 70 * uc}Z`, fill:'var(--bg)', stroke:C.bad, 'stroke-width':1.5}, g);
    setT(lab, u < .12 ? '1 մանրահատիկ կեղև' : u < .52 ? '2 սյունաձև բյուրեղներ' : u < .8 ? '3 հավասարառանցք բյուրեղներ' : 'կծկման խոռոչ');
    const ud = (t % 9) / 7;
    branches.forEach(b => { const st0 = b.lvl * .25 + (b.lvl ? (Math.hypot(b.x - 370, b.y - 150) / 240) * .25 : 0), k = clamp((ud - st0) / .3, 0, 1); if (k <= 0) return;
      S('line', {x1:b.x, y1:b.y, x2:b.x + Math.cos(b.a) * b.len * k, y2:b.y + Math.sin(b.a) * b.len * k, stroke:[C.acc, C.good, C.warn, C.heat][b.lvl], 'stroke-width':[5, 3, 1.8, 1][b.lvl], 'stroke-linecap':'round'}, dg); });
  }, ctl(st));
}};

/* ---------- 3.5 stresses and dislocation glide ---------- */
VIZ.stress = {kind:'i', cap:'Լարումը ցանցում բաժանվում է <b>նորմալ σ</b> և <b>շոշափող τ</b> բաղադրիչների։ σ-ն կարող է առաջացնել միայն առաձգական դեֆորմացիա կամ պոկում (բեկուն քայքայում), τ-ն՝ նաև պլաստիկ դեֆորմացիա (սահք) կամ կտրում։',
f(st){
  const s = svg(st, 640, 250, 'σ և τ'), cx = 200, cy = 125, g = S('g', {}, s);
  T(s, 360, 60, 'σ՝ առաձգական դեֆորմացիա', {fill:C.heat, 'font-weight':600}); T(s, 360, 78, 'կամ պոկում (բեկուն քայքայում)', {fill:C.heat, 'font-weight':600}); T(s, 360, 110, 'τ՝ առաձգական, պլաստիկ դեֆորմացիա', {fill:C.good, 'font-weight':600}); T(s, 360, 128, '(սահք) կամ կտրում', {fill:C.good, 'font-weight':600});
  function draw(deg){
    clear(g); const a = deg * Math.PI / 180, nx = Math.cos(a), ny = -Math.sin(a), tx = Math.sin(a), ty = Math.cos(a);
    S('rect', {x:cx - 60, y:20, width:120, height:210, fill:C.sunk, stroke:C.ink}, g);
    const L = 75 / Math.max(.3, Math.abs(Math.cos(a)));
    S('line', {x1:cx - tx * 70, y1:cy - ty * 70, x2:cx + tx * 70, y2:cy + ty * 70, stroke:C.ink, 'stroke-width':2, 'stroke-dasharray':'6 4', transform:''}, g);
    arrow(g, cx, 18, cx, -14 + 20, C.bad, 2, 8); arrow(g, cx, 232, cx, 248, C.bad, 2, 8); T(g, cx + 10, 14, 'P', {fill:C.bad, 'font-weight':700});
    const F = [0, -80], sn = F[0] * nx + F[1] * ny, st2 = F[0] * tx + F[1] * ty;
    arrow(g, cx, cy, cx + F[0], cy + F[1], C.muted, 1.6, 7);
    arrow(g, cx, cy, cx + nx * sn, cy + ny * sn, C.heat, 2.6, 9); T(g, cx + nx * sn + 6, cy + ny * sn, 'σ', {fill:C.heat, 'font-weight':700, 'font-size':15});
    arrow(g, cx, cy, cx + tx * st2, cy + ty * st2, C.good, 2.6, 9); T(g, cx + tx * st2 + 6, cy + ty * st2 + 4, 'τ', {fill:C.good, 'font-weight':700, 'font-size':15});
  }
  slider(ctl(st), 'Հարթության թեքություն', 0, 80, 1, 45, v => v + '°', draw); draw(45);
}};
VIZ.slip = {kind:'a', cap:'Պլաստիկ դեֆորմացիայի <b>դիսլոկացիոն մեխանիզմը</b>. τ լարման ազդեցությամբ դիսլոկացիան ⊥ տեղաշարժվում է սահքի հարթությամբ, և բյուրեղի մի մասը սահում է մյուսի նկատմամբ մեկ միջատոմային հեռավորությամբ։',
f(st){
  const s = svg(st, 640, 272, 'Դիսլոկացիայի սահք'), g = S('g', {}, s), a = 34, nx = 14, rows = 6, x0 = 320 - (nx - 1) * a / 2, y0 = 40;
  const at = []; for (let j = 0; j < rows; j++) for (let i = 0; i < nx; i++) at.push({i, j, c:S('circle', {r:9, fill:j < 3 ? C.acc : C.accS, stroke:C.acc}, g)});
  const sym = S('g', {}, s), lab = T(s, 320, 266, '', {'text-anchor':'middle', 'font-weight':600});
  const ta = S('g', {}, s); arrow(ta, 80, 20, 180, 20, C.good, 2.4, 9); arrow(ta, 560, 232, 460, 232, C.good, 2.4, 9); T(ta, 190, 25, 'τ', {fill:C.good, 'font-weight':700}); T(ta, 450, 236, 'τ', {fill:C.good, 'font-weight':700, 'text-anchor':'end'});
  anim(st, (dt, t) => {
    const ph = t % 7, u = ph < .8 ? 0 : ph < 5.5 ? (ph - .8) / 4.7 : 1, xd = lerp(x0 - 3 * a, x0 + nx * a + 2 * a, u);
    at.forEach(p => { let x = x0 + p.i * a; const y = y0 + p.j * a * 1.0;
      if (p.j < 3){ const d = 3 - p.j, w = 18 + d * 10; x += a * (.5 - Math.atan((x - xd) / w) / Math.PI); }
      else { const d = p.j - 2, w = 18 + d * 10; x += a * .12 * Math.exp(-(((x - xd) / (w * 1.5)) ** 2)) * Math.sign(x - xd); }
      attrs(p.c, {cx:x, cy:y}); });
    clear(sym); const ys = y0 + 2.5 * a;
    if (u > 0 && u < 1){ S('line', {x1:xd - 10, x2:xd + 10, y1:ys, y2:ys, stroke:C.bad, 'stroke-width':3}, sym); S('line', {x1:xd, x2:xd, y1:ys, y2:ys - 18, stroke:C.bad, 'stroke-width':3}, sym); }
    S('line', {x1:30, x2:610, y1:ys, y2:ys, stroke:C.muted, 'stroke-dasharray':'3 5'}, sym);
    setT(lab, u === 0 ? 'սկզբնական բյուրեղ' : u < 1 ? 'դիսլոկացիան շարժվում է սահքի հարթությամբ' : 'վերին մասը սահել է մեկ միջատոմային հեռավորությամբ (աստիճան)');
  }, ctl(st));
}};

/* ---------- 3.6 work hardening ---------- */
VIZ.workhard = {kind:'i', cap:'<b>Կոփում</b>. պլաստիկ դեֆորմացիայի աճով առաջանում են նոր դիսլոկացիաներ (խտությունը՝ 10⁶–10⁸-ից մինչև 10¹² սմ⁻²), հատիկները ձգվում են դեֆորմացիայի ուղղությամբ։ Ամրությունն ու կարծրությունը աճում են, պլաստիկությունն ու մածուցիկությունը նվազում են, էլեկտրադիմադրությունը աճում է։ Սլաքները որակական են։',
f(st){
  const row = H('div', {class:'vz-row'}, st), W = 220, Hh = 150, cv = canvas(row, W, Hh), s = svg(row, 320, 200, 'Հատկություններ');
  const P = [['ամրություն', 1], ['կարծրություն', 1], ['պլաստիկություն', -1], ['մածուցիկություն', -1], ['էլեկտրադիմադրություն', 1]];
  const bars = P.map(([n, d], i) => { T(s, 0, 30 + i * 34, n, {'font-size':12}); S('rect', {x:150, y:18 + i * 34, width:150, height:14, rx:3, fill:C.sunk}, s);
    return {d, r:S('rect', {x:150, y:18 + i * 34, height:14, rx:3, fill:d > 0 ? C.heat : C.acc}, s)}; });
  const o = out(st), r = rnd(3), seeds = Array.from({length:22}, () => [r() * W, r() * Hh]), D = Array.from({length:60}, () => [r(), r()]);
  const f = rgbOf('--surface'), e = rgbOf('--ink'), ac = col('--bad');
  function draw(def){
    const k = def / 100, sx = 1 + k * 2.2, cxm = W / 2;
    const G = grains(W, Hh, 0, 0, 1 / sx, sx * .7, seeds.map(([x, y]) => [cxm + (x - cxm) * sx * .9, Hh / 2 + (y - Hh / 2) / sx]));
    const img = cv.img.data; for (let i = 0; i < W * Hh; i++){ const p = G.edge[i] ? e : f; img[i * 4] = p[0]; img[i * 4 + 1] = p[1]; img[i * 4 + 2] = p[2]; img[i * 4 + 3] = 255; }
    cv.g.putImageData(cv.img, 0, 0); cv.g.fillStyle = ac; cv.g.font = 'bold 9px sans-serif';
    const n = Math.round(4 + k * 56); for (let i = 0; i < n; i++) cv.g.fillText('⊥', D[i][0] * (W - 10), 10 + D[i][1] * (Hh - 10));
    bars.forEach(b => attrs(b.r, {width:150 * (b.d > 0 ? .25 + .7 * k : .95 - .7 * k)}));
    const ex = 6 + 6 * k;
    o.innerHTML = `Դիսլոկացիաների խտություն՝ ≈ <b class="mono">10<sup>${fmt(ex, 1)}</sup></b> սմ⁻² ${k === 0 ? '(չդեֆորմացված)' : ''}`;
  }
  slider(ctl(st), 'Պլաստիկ դեֆորմացիա', 0, 100, 5, 30, v => v + '%', draw); draw(30);
}};

/* ---------- 3.7 recovery, polygonization, recrystallization; Bochvar ---------- */
VIZ.recryst = {kind:'i', cap:'Կոփված մետաղի տաքացման ժամանակ. <b>վերադարձ</b>՝ ավելորդ վականսիաների և ցանցի աղավաղումների նվազում, <b>պոլիգոնացում</b>՝ եզրային դիսլոկացիաները դասավորվում են պատերի տեսքով (ենթահատիկներ), <b>վերաբյուրեղացում</b>՝ նոր կենտրոններից նոր հավասարառանցք հատիկների աճ։',
f(st){
  const W = 400, Hh = 220, cv = canvas(st, W, Hh), r = rnd(21), seeds = Array.from({length:16}, () => [r() * W, r() * Hh]);
  const Dp = Array.from({length:70}, () => [r(), r()]), V = Array.from({length:80}, () => [r() * W, r() * Hh]), nseeds = Array.from({length:30}, () => [r() * W, r() * Hh, r() * .6]);
  const f = rgbOf('--surface'), e = rgbOf('--ink'), nc = rgbOf('--good-soft'), bad = col('--bad'), mut = col('--muted');
  const def = grains(W, Hh, 0, 0, .45, 1.6, seeds.map(([x, y]) => [x, Hh / 2 + (y - Hh / 2) * .5])), neo = grains(W, Hh, 0, 0, 1, 1, nseeds.map(q => [q[0], q[1]]));
  let stage = 0, grow = 1;
  const lab = out(st);
  function draw(){
    const img = cv.img.data;
    for (let i = 0; i < W * Hh; i++){ let p = def.edge[i] ? e : f;
      if (stage === 3){ const x = i % W, y = (i / W) | 0, k = neo.lab[i], q = nseeds[k], d = Math.hypot(x - q[0], y - q[1]); if (d < (grow - q[2]) * 100) p = neo.edge[i] ? e : nc; }
      img[i * 4] = p[0]; img[i * 4 + 1] = p[1]; img[i * 4 + 2] = p[2]; img[i * 4 + 3] = 255; }
    cv.g.putImageData(cv.img, 0, 0);
    const g = cv.g; g.font = 'bold 12px sans-serif';
    if (stage < 3 || grow < 1.4){
      if (stage === 0){ g.fillStyle = mut; V.forEach(([x, y]) => g.fillRect(x, y, 2, 2)); }
      if (stage === 1){ g.fillStyle = mut; V.slice(0, 18).forEach(([x, y]) => g.fillRect(x, y, 2, 2)); }
      g.fillStyle = bad;
      if (stage < 2) Dp.forEach(([x, y]) => g.fillText('⊥', x * (W - 10), 10 + y * (Hh - 10)));
      if (stage === 2) [60, 150, 240, 330].forEach((x, k) => { for (let y = 14; y < Hh; y += 15) g.fillText('⊥', x + (k % 2) * 8, y); });
    }
    lab.innerHTML = ['<b>Կոփված</b> մետաղ՝ ձգված հատիկներ, շատ դիսլոկացիաներ (⊥) և վականսիաներ', '<b>Վերադարձ</b>՝ վականսիաների թիվը և ցանցի աղավաղումները նվազում են', '<b>Պոլիգոնացում</b>՝ ⊥-ները դասավորվում են պատերի տեսքով, առաջանում են ենթահատիկներ (պոլիգոններ)', '<b>Վերաբյուրեղացում</b>՝ նոր հավասարառանցք հատիկներ (կոփումը վերանում է)'][stage];
  }
  const c = ctl(st);
  seg(c, [[0, 'կոփված'], [1, 'վերադարձ'], [2, 'պոլիգոնացում'], [3, 'վերաբյուրեղացում']], 0, v => { stage = v; grow = v === 3 ? 0 : 1; draw(); });
  anim(st, dt => { if (stage === 3 && grow < 1.6){ grow += dt * .5; draw(); } });
  draw();
}};
VIZ.bochvar = {kind:'i', cap:'Բոչվարի բանաձև՝ T<sub>վ</sub> = α·T<sub>հալ</sub> (Կելվինով)։ α ≈ 0,4՝ տեխնիկապես մաքուր մետաղներ, 0,1–0,2՝ շատ մաքուր, 0,5–0,8՝ համաձուլվածքներ։ Վերաբյուրեղացման թրծումը կատարում են 200–300°C-ով բարձր։',
f(st){
  const o = out(st), c = ctl(st);
  let Tm = 1539, al = [.4, .4];
  const M = [['Fe', 1539], ['Cu', 1083], ['Ni', 1452]];
  function draw(){
    const K = Tm + 273, lo = al[0] * K, hi = al[1] * K, cc = v => fmt(v - 273, 0);
    const one = al[0] === al[1];
    o.innerHTML = `T<sub>հալ</sub> = ${Tm}°C = <span class="mono">${K}</span> Կ → T<sub>վ</sub> = ${one ? fmt(al[0], 1) : fmt(al[0], 1) + '…' + fmt(al[1], 1)}·${K} = <b class="mono">${one ? fmt(lo, 0) : fmt(lo, 0) + '…' + fmt(hi, 0)}</b> Կ ≈ <b class="mono">${one ? cc(lo) : cc(lo) + '…' + cc(hi)}</b>°C<br>`
      + `<span class="vz-mut">Վերաբյուրեղացման թրծում՝ ≈ ${one ? cc(lo + 200) + '–' + cc(lo + 300) : cc(lo + 200) + '–' + cc(hi + 300)}°C (+200–300°C)</span>`;
  }
  seg(c, M.map(([n, v]) => [v, n + ' ' + v + '°C']), Tm, v => { Tm = v; draw(); });
  seg(c, [['.4', 'տեխն. մաքուր α ≈ 0,4'], ['p', 'շատ մաքուր 0,1–0,2'], ['a', 'համաձուլվածք 0,5–0,8']], '.4', v => { al = v === 'p' ? [.1, .2] : v === 'a' ? [.5, .8] : [.4, .4]; draw(); });
  draw();
}};

/* ---------- 3.8 hot and cold working ---------- */
VIZ.hotcold = {kind:'i', cap:'«Տաք» և «սառը» մշակումը որոշվում է <b>վերաբյուրեղացման ջերմաստիճանի</b> նկատմամբ. ավելի բարձր՝ տաք (կոփում չի մնում), ավելի ցածր՝ սառը (մետաղը կոփվում է)։ Կապարի և անագի T<sub>վ</sub>-ն սենյակայինից ցածր է, ուստի 20°C-ում դրանց դեֆորմացիան տաք մշակում է։',
f(st){
  const s = svg(st, 640, 150, 'Տաք և սառը մշակում'), X = v => 40 + (v + 50) / 1050 * 560;
  let metal = 'fe', Tw = 20;
  const bar = S('rect', {y:56, height:24, rx:4}, s), lab = T(s, 320, 120, '', {'text-anchor':'middle', 'font-weight':700, 'font-size':14}), tv = S('g', {}, s);
  arrow(s, X(-50), 90, X(1000) + 8, 90, C.muted, 1.2, 6); [0, 200, 400, 600, 800, 1000].forEach(v => T(s, X(v), 104, v + '°', {'text-anchor':'middle', 'font-size':10, fill:C.muted}));
  const mk = S('path', {fill:C.ink}, s);
  function draw(){
    const tvv = metal === 'fe' ? 450 : null; clear(tv);
    if (tvv != null){ S('rect', {x:X(-50), y:56, width:X(tvv) - X(-50), height:24, fill:C.accS}, tv); S('rect', {x:X(tvv), y:56, width:X(1000) - X(tvv), height:24, fill:C.heatS}, tv);
      S('line', {x1:X(tvv), x2:X(tvv), y1:46, y2:86, stroke:C.ink, 'stroke-width':2}, tv); T(tv, X(tvv), 40, 'T_{վ} ≈ 450°C (Fe)', {'text-anchor':'middle', 'font-size':11, 'font-weight':600}); }
    else { S('rect', {x:X(-50), y:56, width:X(10) - X(-50), height:24, fill:C.accS}, tv); S('rect', {x:X(10), y:56, width:X(1000) - X(10), height:24, fill:C.heatS}, tv);
      T(tv, X(10), 40, 'T_{վ} < 20°C (Pb, Sn)', {'font-size':11, 'font-weight':600}); }
    const hot = tvv != null ? Tw > tvv : true;
    attrs(mk, {d:`M${X(Tw)} 52 l-6 -10 h12z`});
    setT(lab, hot ? 'տաք մշակում՝ կոփում չի առաջանում' : 'սառը մշակում՝ մետաղը կոփվում է'); lab.style.fill = hot ? C.heat : C.acc;
  }
  const c = ctl(st);
  seg(c, [['fe', 'Երկաթ'], ['pb', 'Կապար, անագ']], metal, v => { metal = v; draw(); });
  slider(c, 'Դեֆորմացիայի T', -20, 1000, 10, 20, v => v + '°C', v => { Tw = v; draw(); });
  draw();
}};

window.NYU_VZ = {rgbOf, mixc, canvas, grains, bdist, hash, cell3d, STRUCT, ss, clear};
})();
