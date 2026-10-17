/* Materials-science lecture visuals, lectures 4–7, and the section map. */
(function(){
'use strict';
const {C, S, H, T, setT, attrs, svg, pts, arrow, axes, clamp, lerp, fmt, rnd, col, ctl, slider, seg, btn, out, anim} = window.VZ;
const {rgbOf, mixc, canvas, grains, bdist, hash, cell3d, ss, clear} = window.NYU_VZ;
const VIZ = window.VIZ;

/* ---------- 4.2 solid solutions ---------- */
VIZ.solsol = {kind:'i', cap:'Պինդ լուծույթում պահպանվում է լուծիչ մետաղի ցանցը։ <b>Տեղակալման</b>՝ լուծիչի ատոմները մասամբ փոխարինված են (անսահմանափակ լուծելիության համար տրամագծերը պետք է տարբերվեն ոչ ավելի քան 8–15%, ցանցերը՝ նույնատիպ, վալենտականությունների տարբերությունը՝ ≤ 1)։ <b>Ներդրման</b>՝ ատոմները միջատոմային դատարկություններում (տրամագիծը ≤ լուծիչի 59%-ը, միշտ սահմանափակ)։',
f(st){
  const s = svg(st, 640, 250, 'Պինդ լուծույթ'), g = S('g', {}, s), a = 40, x0 = 60, y0 = 36, lab = T(s, 480, 70, '', {'font-weight':700}), l2 = T(s, 480, 94, '', {}), l3 = T(s, 480, 114, '', {fill:C.muted, 'font-size':11});
  let mode = 's', ratio = 10;
  const subs = [[1, 1], [4, 2], [2, 4], [6, 0], [7, 3], [3, 0]], ints = [[1, 1], [3, 2], [5, 0], [6, 3], [2, 4]];
  T(s, 480, 160, '● լուծիչ A', {fill:C.acc}); T(s, 480, 180, '● լուծվող B', {fill:C.heat});
  function draw(){
    clear(g); const R = 15;
    for (let j = 0; j < 5; j++) for (let i = 0; i < 9; i++){ const sub = mode === 's' && subs.some(([x, y]) => x === i && y === j);
      S('circle', {cx:x0 + i * a, cy:y0 + j * a, r:sub ? R * (1 + ratio / 100) : R, fill:sub ? C.heat : C.acc, opacity:.9}, g); }
    if (mode === 'i') ints.forEach(([i, j]) => S('circle', {cx:x0 + (i + .5) * a, cy:y0 + (j + .5) * a, r:R * ratio / 100, fill:C.heat}, g));
    const ok = mode === 's' ? ratio <= 15 : ratio <= 59;
    setT(lab, mode === 's' ? 'Տեղակալման A(B)' : 'Ներդրման A(B)');
    setT(l2, mode === 's' ? (ratio <= 8 ? 'տարբերություն ≤ 8%՝ հնարավոր է անսահմանափակ' : ratio <= 15 ? '8–15%՝ սահմանային' : '> 15%՝ սահմանափակ կամ չի առաջանում') : (ok ? '≤ 59%՝ կարող է ներդրվել (C, N, H, B)' : '> 59%՝ չի տեղավորվում'));
    l2.style.fill = ok ? C.good : C.bad;
    setT(l3, mode === 's' ? 'օր․ Cu–Ni (երկուսն էլ К12)' : 'օր․ ֆերիտ և աուստենիտ՝ C-ի լուծույթներ Fe-ում');
  }
  const c = ctl(st), sc = H('div', {class:'vz-ctl'}, st);
  function sl(){ sc.innerHTML = ''; if (mode === 's') slider(sc, 'Տրամագծերի տարբերություն', 0, 30, 1, ratio = 10, v => v + '%', v => { ratio = v; draw(); });
    else slider(sc, 'd<sub>B</sub>/d<sub>A</sub>', 30, 90, 1, ratio = 50, v => v + '%', v => { ratio = v; draw(); }); draw(); }
  seg(c, [['s', 'Տեղակալման'], ['i', 'Ներդրման']], mode, m => { mode = m; sl(); });
  sl();
}};

/* ---------- 4.3 chemical compound Fe3C ---------- */
VIZ.fe3c = {kind:'s', cap:'Քիմիական միացությունն ունի <b>հաստատուն բաղադրություն</b>։ Fe₃C. 3 ատոմ Fe-ին՝ 1 ատոմ C, ըստ զանգվածի՝ 93,33% Fe և 6,67% C։',
f(st){
  const s = svg(st, 640, 170, 'Fe3C');
  [[60, 60], [110, 50], [85, 100]].forEach(([x, y]) => { S('circle', {cx:x, cy:y, r:24, fill:C.acc}, s); T(s, x, y + 5, 'Fe', {'text-anchor':'middle', fill:'var(--surface)', 'font-weight':700}); });
  S('circle', {cx:140, cy:95, r:13, fill:C.ink}, s); T(s, 140, 100, 'C', {'text-anchor':'middle', fill:'var(--surface)', 'font-weight':700});
  T(s, 100, 150, 'Fe₃C', {'text-anchor':'middle', 'font-weight':700, 'font-size':15});
  const bar = (y, n, a, b) => { T(s, 210, y + 15, n, {'font-weight':600}); S('rect', {x:330, y, width:280 * a, height:22, fill:C.acc}, s); S('rect', {x:330 + 280 * a, y, width:280 * b, height:22, fill:C.ink}, s);
    T(s, 336, y + 15, 'Fe ' + fmt(a * 100, 2).replace(',00', ''), {fill:'var(--surface)', 'font-size':11, 'font-weight':600}); T(s, 606, y + 15, 'C ' + fmt(b * 100, 2).replace(',00', ''), {'text-anchor':'end', fill:'var(--surface)', 'font-size':11, 'font-weight':600}); };
  bar(40, 'ըստ ատոմների, %', .75, .25); bar(90, 'ըստ զանգվածի, %', .9333, .0667);
}};

/* ---------- 4.4 single phase vs mechanical mixture ---------- */
VIZ.mixture = {kind:'s', cap:'Անսահմանափակ լուծելիության դեպքում հեղուկը պնդանալիս դառնում է <b>պինդ լուծույթ</b>՝ միաֆազ, պարզ մետաղին նման ստրուկտուրա։ Այլ դեպքերում այն տրոհվում է երկու տարբեր ֆազերի մասնիկների՝ <b>մեխանիկական խառնուրդ</b> (ստրուկտուրային բաղադրիչ, ոչ թե ֆազ)։',
f(st){
  const row = H('div', {class:'vz-row'}, st), W = 260, Hh = 150, f = rgbOf('--accent-soft'), e = rgbOf('--ink'), h = rgbOf('--heat-soft');
  [['պինդ լուծույթ (միաֆազ)', 0], ['մեխանիկական խառնուրդ (երկֆազ)', 1]].forEach(([n, k]) => {
    const box = H('div', {}, row), cv = canvas(box, W, Hh); H('div', {class:'vz-out', html:'<b>' + n + '</b>', style:'text-align:center'}, box);
    const G = grains(W, Hh, k ? 260 : 14, 30 + k), img = cv.img.data;
    for (let i = 0; i < W * Hh; i++){ const p = G.edge[i] ? (k ? mixc(e, f, .6) : e) : k ? (hash(G.lab[i]) < .5 ? h : f) : f; img[i * 4] = p[0]; img[i * 4 + 1] = p[1]; img[i * 4 + 2] = p[2]; img[i * 4 + 3] = 255; }
    cv.g.putImageData(cv.img, 0, 0); });
}};

/* ---------- 5.1 building a diagram from cooling curves ---------- */
const TA = .35, TB = .85;                              // schematic melting points of A and B (fractions of the T axis)
const liq = x => TA + (TB - TA) * Math.pow(x, .62), sol = x => TA + (TB - TA) * Math.pow(x, 1.75);
VIZ.build = {kind:'a', cap:'Վիճակի դիագրամը կառուցում են <b>ջերմային անալիզով</b>. տարբեր բաղադրությունների սառեցման կորերի վրա գտնում են կրիտիկական կետերը (կանգառներ կամ շրջման կետեր) և միացնում դրանք։ Աբսցիսը՝ կոնցենտրացիա (A-ից B), օրդինատը՝ ջերմաստիճան։ Սխեմատիկ օրինակ՝ անսահմանափակ լուծելիություն։',
f(st){
  const s = svg(st, 660, 280, 'Դիագրամի կառուցում'), X = [0, .25, .5, .75, 1];
  const A = axes(s, {x:40, y:20, w:250, h:220, xr:[0, 1], yr:[.15, 1], xl:'ժամանակ', yl:'T'}), B = axes(s, {x:380, y:20, w:240, h:220, xr:[0, 1], yr:[.15, 1], xl:'', yl:'T'});
  T(s, B.X(0), B.Y(.15) + 16, 'A', {'text-anchor':'middle', 'font-weight':700}); T(s, B.X(1), B.Y(.15) + 16, 'B', {'text-anchor':'middle', 'font-weight':700}); T(s, B.X(.5), B.Y(.15) + 16, 'B, %', {'text-anchor':'middle', fill:C.muted, 'font-size':11});
  const cc = [C.acc, C.good, C.warn, C.heat, C.bad];
  // cooling curve of composition x: plateau for a pure metal, two inflections for an alloy
  const cool = x => { const l = liq(x), so = sol(x), pure = x === 0 || x === 1, r1 = .9, r2 = .25, t1 = (.97 - l) / r1, t2 = pure ? t1 + .18 : t1 + (l - so) / r2;
    return {f:t => t < t1 ? .97 - r1 * t : t < t2 ? (pure ? l : l - r2 * (t - t1)) : so - r1 * (t - t2), t1, t2, l, so}; };
  const curves = X.map((x, i) => ({x, c:cool(x), p:S('path', {fill:'none', stroke:cc[i], 'stroke-width':2.2}, s), g:S('g', {}, s)}));
  const L = S('path', {fill:'none', stroke:C.ink, 'stroke-width':2.5}, s), So = S('path', {fill:'none', stroke:C.ink, 'stroke-width':2.5, 'stroke-dasharray':'7 4'}, s), lbl = S('g', {}, s);
  anim(st, (dt, t) => {
    const u = (t % 11) / 9;
    curves.forEach((q, i) => { const k = clamp((u - i * .14) / .3, 0, 1), tm = k * 1.4, sx = v => A.X(v / 1.4 * .95);
      const r = []; for (let j = 0; j <= 80; j++){ const tt = tm * j / 80; r.push([sx(tt), A.Y(clamp(q.c.f(tt), .15, 1))]); } attrs(q.p, {d:pts(r)});
      clear(q.g);
      [[q.c.t1, q.c.l], [q.c.t2, q.c.so]].forEach(([tt, T0]) => { if (tm < tt) return;
        S('circle', {cx:sx(tt), cy:A.Y(T0), r:3.5, fill:cc[i]}, q.g); S('line', {x1:sx(tt), x2:B.X(q.x), y1:A.Y(T0), y2:A.Y(T0), stroke:cc[i], 'stroke-dasharray':'2 4', opacity:.6}, q.g);
        S('circle', {cx:B.X(q.x), cy:B.Y(T0), r:4.5, fill:cc[i]}, q.g); });
    });
    const k = ss((u - .85) / .12);
    attrs(L, {d:B.fn(liq, 0, Math.max(k, .001))}); attrs(So, {d:B.fn(sol, 0, Math.max(k, .001))});
    clear(lbl); if (k > .9){ T(lbl, B.X(.42), B.Y(liq(.42)) - 8, 'լիկվիդուս', {'font-size':11, 'text-anchor':'end'}); T(lbl, B.X(.62), B.Y(sol(.62)) + 16, 'սոլիդուս', {'font-size':11}); }
  }, ctl(st), 9.6);
}};

/* ---------- 5.2 Gibbs phase rule ---------- */
VIZ.gibbs = {kind:'i', cap:'Ֆազերի կանոն (ճնշումը հաստատուն)՝ <b>C = K − Ф + 1</b>։ C = 0՝ սառեցման կորի վրա հորիզոնական հարթակ, C = 1՝ բյուրեղացումը նվազող ջերմաստիճանում (երկու շրջման կետ)։ Երկակի համակարգում հարթակ հնարավոր է միայն Ф = 3-ի դեպքում։',
f(st){
  const s = svg(st, 600, 220, 'Ֆազերի կանոն'), A = axes(s, {x:300, y:20, w:270, h:170, xr:[0, 1], yr:[0, 1], xl:'ժամանակ', yl:'T'});
  const p = S('path', {fill:'none', stroke:C.acc, 'stroke-width':2.6}, s), big = T(s, 20, 70, '', {'font-size':26, 'font-weight':700}), d1 = T(s, 20, 110, '', {'font-weight':600}), d2 = T(s, 20, 134, '', {fill:C.muted});
  let K = 2, F = 2;
  const CASES = {'1,2':'պարզ մետաղի պնդացում (հեղուկ + պինդ)', '2,2':'հեղուկ + պինդ լուծույթ', '2,3':'հեղուկ + α + β (էվտեկտիկա)'};
  function draw(){
    const c = K - F + 1;
    setT(big, 'C = ' + K + ' − ' + F + ' + 1 = ' + c); big.style.fill = c < 0 ? C.bad : C.ink;
    setT(d1, c < 0 ? 'անհնար է' : c === 0 ? 'հարթակ (ինվարիանտ)' : c === 1 ? 'կորի թեքության փոփոխություն' : 'փոխակերպում չկա, միայն սառեցում');
    setT(d2, CASES[K + ',' + F] || '');
    if (c < 0){ attrs(p, {d:''}); return; }
    attrs(p, {d:A.fn(t => c === 0 ? (t < .35 ? .95 - t * 1.2 : t < .65 ? .53 : .53 - (t - .65) * 1.2) : c === 1 ? (t < .3 ? .95 - t * 1.2 : t < .7 ? .59 - (t - .3) * .35 : .45 - (t - .7) * 1.2) : .95 - t * .85, 0, 1, 200)});
  }
  const c = ctl(st);
  seg(c, [[1, 'K = 1'], [2, 'K = 2']], K, v => { K = v; draw(); });
  seg(c, [[1, 'Ф = 1'], [2, 'Ф = 2'], [3, 'Ф = 3']], F, v => { F = v; draw(); });
  draw();
}};

/* ---------- 5.3–5.4 Cu–Ni diagram and the lever rule ---------- */
// schematic liquidus/solidus between Cu 1083°C and Ni 1452°C, shaped so the lecture example (40% Ni: liquid 32%, solid 57%) lies on one tie line
const T0 = 1083, T1 = 1452, sOf = T => (T - T0) / (T1 - T0), xL = T => 100 * Math.pow(sOf(T), 1.6), xS = T => 100 * Math.pow(sOf(T), .7885);
const Tex = T0 + Math.pow(.32, 1 / 1.6) * (T1 - T0);
VIZ.cuni = {kind:'i', cap: a => (a === 'lever'
  ? '<b>Հատվածների կանոն</b>. համաձուլվածքի կետով տանում ենք հորիզոնական (կոնոդ). ձախ ծայրը (լիկվիդուսի վրա)՝ հեղուկի բաղադրություն, աջը (սոլիդուսի վրա)՝ պինդ ֆազի։ Q<sub>պինդ</sub> = (x − x<sub>հ</sub>)/(x<sub>պ</sub> − x<sub>հ</sub>), Q<sub>հեղ</sub> = (x<sub>պ</sub> − x)/(x<sub>պ</sub> − x<sub>հ</sub>)։'
  : 'Պղինձ–նիկել՝ անսահմանափակ լուծելիություն։ Լիկվիդուսից վեր՝ հեղուկ, սոլիդուսից ներքև՝ պինդ α լուծույթ, դրանց միջև՝ հեղուկ + α։ Տեղափոխեք կետը։') + ' Կորերը սխեմատիկ են (թվային արժեքները՝ միայն 1083 և 1452°C)։',
f(st, a){
  const s = svg(st, 660, 300, 'Cu–Ni'), A = axes(s, {x:60, y:20, w:330, h:240, xr:[0, 100], yr:[1000, 1520], xl:'', yl:'T'});
  T(s, A.X(50), A.Y(1000) + 16, 'Ni, %', {'text-anchor':'middle', fill:C.muted, 'font-size':11});
  const Ts = []; for (let i = 0; i <= 80; i++) Ts.push(T0 + (T1 - T0) * i / 80);
  S('path', {d:pts(Ts.map(T => [A.X(xL(T)), A.Y(T)])) + pts(Ts.slice().reverse().map(T => [A.X(xS(T)), A.Y(T)])).replace('M', 'L') + 'Z', fill:C.warnS}, s);
  S('path', {d:pts(Ts.map(T => [A.X(xL(T)), A.Y(T)])), fill:'none', stroke:C.ink, 'stroke-width':2.5}, s); S('path', {d:pts(Ts.map(T => [A.X(xS(T)), A.Y(T)])), fill:'none', stroke:C.ink, 'stroke-width':2.5, 'stroke-dasharray':'7 4'}, s);
  T(s, A.X(0) - 6, A.Y(T0) + 4, '1083', {'text-anchor':'end', 'font-size':11}); T(s, A.X(100) + 6, A.Y(T1) + 4, '1452', {'font-size':11});
  T(s, A.X(0), A.Y(1000) + 16, 'Cu', {'text-anchor':'middle', 'font-weight':700}); T(s, A.X(100), A.Y(1000) + 16, 'Ni', {'text-anchor':'middle', 'font-weight':700});
  T(s, A.X(25), A.Y(1440), 'հեղուկ (Հ)', {'font-weight':600}); T(s, A.X(60), A.Y(1080), 'α (պինդ լուծույթ)', {'font-weight':600}); T(s, A.X(63), A.Y(1335), 'Հ + α', {'font-weight':600, 'font-size':11, 'text-anchor':'middle'});
  T(s, A.X(30), A.Y(liq30()) - 6, 'լիկվիդուս', {'font-size':11, 'text-anchor':'end'});
  function liq30(){ return T0 + Math.pow(.3, 1 / 1.6) * (T1 - T0); }
  const tie = S('g', {}, s), dot = S('circle', {r:7, fill:C.bad, stroke:'var(--surface)', 'stroke-width':2}, s);
  const ox = 420, info = [0, 1, 2, 3, 4].map(i => T(s, ox, 50 + i * 24, '', {'font-size':i ? 12.5 : 14, 'font-weight':i ? 400 : 700}));
  const qb = [S('rect', {x:ox, y:190, height:22, fill:C.heat}, s), S('rect', {y:190, height:22, fill:C.acc}, s)], ql = T(s, ox, 230, '', {'font-size':11, fill:C.acc}), ql2 = T(s, ox + 110, 230, '', {'font-size':11, fill:C.heat});
  let x = 40, tc = a === 'lever' ? Tex : 1350;
  function draw(){
    attrs(dot, {cx:A.X(x), cy:A.Y(tc)}); clear(tie);
    const xl = tc >= T0 && tc <= T1 ? xL(tc) : null, xs = tc >= T0 && tc <= T1 ? xS(tc) : null;
    const reg = xl == null ? (tc > T1 ? 'L' : 'S') : x < xl ? 'L' : x > xs ? 'S' : 'LS';
    info[0].textContent = reg === 'L' ? 'Հեղուկ' : reg === 'S' ? 'Պինդ α լուծույթ' : 'Հեղուկ + α';
    info[0].style.fill = reg === 'L' ? C.heat : reg === 'S' ? C.acc : C.warn;
    const ph = reg === 'LS' ? 2 : 1;
    setT(info[1], 'Ֆազեր՝ ' + ph + ', C = 2 − ' + ph + ' + 1 = ' + (3 - ph));
    if (reg === 'LS'){
      S('line', {x1:A.X(xl), x2:A.X(xs), y1:A.Y(tc), y2:A.Y(tc), stroke:C.ink, 'stroke-width':1.5}, tie);
      S('line', {x1:A.X(xl), x2:A.X(x), y1:A.Y(tc) + 6, y2:A.Y(tc) + 6, stroke:C.acc, 'stroke-width':4}, tie); S('line', {x1:A.X(x), x2:A.X(xs), y1:A.Y(tc) - 6, y2:A.Y(tc) - 6, stroke:C.heat, 'stroke-width':4}, tie);
      [[xl, 'x_{հ}'], [xs, 'x_{պ}']].forEach(([v, n]) => { S('circle', {cx:A.X(v), cy:A.Y(tc), r:4, fill:C.ink}, tie); S('line', {x1:A.X(v), x2:A.X(v), y1:A.Y(tc), y2:A.Y(1000), stroke:C.muted, 'stroke-dasharray':'3 3'}, tie); T(tie, A.X(v), A.Y(1000) - 6, n + ' = ' + fmt(v, 0), {'text-anchor':'middle', 'font-size':11, 'font-weight':600}); });
      const qs = (x - xl) / (xs - xl), qh = 1 - qs;
      setT(info[2], 'հեղուկ՝ ' + fmt(xl, 0) + '% Ni, պինդ՝ ' + fmt(xs, 0) + '% Ni');
      setT(info[3], 'Q_{պինդ} = (' + fmt(x, 0) + ' − ' + fmt(xl, 0) + ')/(' + fmt(xs, 0) + ' − ' + fmt(xl, 0) + ') = ' + Math.round(qs * 100) + '%');
      setT(info[4], 'Q_{հեղ} = ' + Math.round(qh * 100) + '%');
      attrs(qb[1], {width:220 * qs}); attrs(qb[0], {x:ox + 220 * qs, width:220 * qh}); qb[1].setAttribute('x', ox); setT(ql, '■ պինդ α'); setT(ql2, '■ հեղուկ');
    } else { setT(info[2], 'α-ի կոնցենտրացիան = համաձուլվածքի բաղադրությունը'.slice(0, reg === 'S' ? 99 : 0) || 'բաղադրությունը՝ ' + fmt(x, 0) + '% Ni'); setT(info[3], ''); setT(info[4], ''); attrs(qb[0], {width:0}); attrs(qb[1], {width:0}); setT(ql, ''); setT(ql2, ''); }
  }
  const c = ctl(st);
  const sx = slider(c, 'Ni', 0, 100, 1, x, v => v + '%', v => { x = v; draw(); }), sT = slider(c, 'T', 1000, 1520, 1, tc, () => '↕', v => { tc = v; draw(); });
  btn(c, 'Օրինակ՝ 40% Ni', () => { x = 40; tc = Tex; sx.el.value = 40; sT.el.value = tc; sx.el.dispatchEvent(new Event('input')); draw(); });
  draw();
}};

/* ---------- 5.5 eutectic diagram with cooling curves ---------- */
VIZ.eutectic = {kind:'i', cap:'Սահմանափակ լուծելիություն և <b>էվտեկտիկա</b>՝ հաստատուն ջերմաստիճանում Հ → α + β։ Եթե լուծվածը փոքր է սահմանայինից՝ հեղուկը վերածվում է պինդ լուծույթի (C = 1, երկու շրջման կետ), եթե մեծ է՝ մնացած հեղուկը տրոհվում է α + β խառնուրդի (C = 0, հարթակ)։ Էվտեկտիկականից ձախ՝ մինչէվտեկտիկական, աջ՝ հետէվտեկտիկական։ Սխեմատիկ դիագրամ։',
f(st){
  const s = svg(st, 660, 300, 'Էվտեկտիկա'), A = axes(s, {x:50, y:20, w:320, h:240, xr:[0, 100], yr:[0, 1], xl:'', yl:'T'});
  T(s, A.X(50), A.Y(0) + 16, 'B, %', {'text-anchor':'middle', fill:C.muted, 'font-size':11});
  const ta = .82, tb = .7, te = .4, xe = 60, xa = 15, xb = 88;
  const Lq = x => x <= xe ? lerp(ta, te, x / xe) : lerp(te, tb, (x - xe) / (100 - xe));
  const solv = (x0, x1, t) => lerp(x0, x1, 1 - t / te);    // solvus from the eutectic line down to T = 0
  const P = q => q.map(([x, t]) => [A.X(x), A.Y(t)]);
  S('path', {d:pts(P([[0, ta], [xe, te], [100, tb]])), fill:'none', stroke:C.ink, 'stroke-width':2.5}, s);
  S('path', {d:pts(P([[0, ta], [xa, te], [xb, te], [100, tb]])), fill:'none', stroke:C.ink, 'stroke-width':2.5, 'stroke-dasharray':'7 4'}, s);
  S('path', {d:pts(P([[xa, te], [8, 0]])) + pts(P([[xb, te], [94, 0]])).replace('M', 'M'), fill:'none', stroke:C.ink, 'stroke-width':1.5}, s);
  [[25, .9, 'Հ'], [6, .5, 'α'], [94, .45, 'β'], [50, .18, 'α + β'], [18, .6, 'Հ + α'], [80, .55, 'Հ + β']].forEach(([x, t, n]) => T(s, A.X(x), A.Y(t), n, {'text-anchor':'middle', 'font-weight':700}));
  S('circle', {cx:A.X(xe), cy:A.Y(te), r:4, fill:C.ink}, s); T(s, A.X(xe), A.Y(te) + 16, 'E', {'text-anchor':'middle', 'font-weight':700});
  T(s, A.X(0), A.Y(0) + 16, 'A', {'text-anchor':'middle', 'font-weight':700}); T(s, A.X(100), A.Y(0) + 16, 'B', {'text-anchor':'middle', 'font-weight':700});
  const vl = S('line', {stroke:C.bad, 'stroke-dasharray':'4 3'}, s), dot = S('circle', {r:6, fill:C.bad}, s);
  const B = axes(s, {x:430, y:20, w:200, h:240, xr:[0, 1], yr:[0, 1], xl:'ժամանակ', yl:'T'}), cp = S('path', {fill:'none', stroke:C.acc, 'stroke-width':2.6}, s);
  const lab = T(s, 530, 290, '', {'text-anchor':'middle', 'font-weight':600});
  let x = 35, segs = [];
  function plan(){
    const tl = Lq(x), inA = x <= xa, inB = x >= xb, eut = !inA && !inB;
    const tsol = inA ? lerp(ta, te, x / xa) : inB ? lerp(tb, te, (100 - x) / (100 - xb)) : te;
    const fe = eut ? (x <= xe ? (x - xa) / (xe - xa) : (xb - x) / (xb - xe)) : 0;          // share of eutectic liquid (lever rule at TE)
    segs = [[.95, tl, 1], [tl, tsol, .35]]; if (eut) segs.push([te, te, 0, .1 + .5 * fe]); segs.push([tsol, 0, 1]);
    setT(lab, inA || inB ? 'պինդ լուծույթ՝ երկու շրջման կետ' : Math.abs(x - xe) < 1.5 ? 'էվտեկտիկական՝ միայն հարթակ' : (x < xe ? 'մինչէվտեկտիկական' : 'հետէվտեկտիկական') + '՝ շրջում + հարթակ');
  }
  function curve(u){ const r = []; let t = 0, T = .95; r.push([B.X(0), B.Y(T)]);
    for (const q of segs){ const dur = q[2] ? (q[0] - q[1]) / q[2] * .9 : q[3]; const n = 20; for (let i = 1; i <= n; i++){ const tt = t + dur * i / n; if (tt > u) return r; r.push([B.X(tt), B.Y(q[2] ? q[0] - (q[0] - q[1]) * i / n : q[0])]); } t += dur; } return r; }
  const c = ctl(st);
  slider(c, 'B', 2, 98, 1, x, v => v + '%', v => { x = v; plan(); An.t = 0; An.draw(); });
  plan();
  const An = anim(st, (dt, t) => {
    const u = (t % 6) / 4.5, r = curve(Math.min(u, 1.2));
    attrs(cp, {d:pts(r)}); const last = r[r.length - 1], Tc = (B.o.y + B.o.h - last[1]) / B.o.h;
    attrs(vl, {x1:A.X(x), x2:A.X(x), y1:A.Y(.97), y2:A.Y(0)}); attrs(dot, {cx:A.X(x), cy:A.Y(Tc)});
  }, c, 4.4);
}};

/* ---------- 5.6 Kurnakov ---------- */
VIZ.kurnakov = {kind:'s', cap:'Կուռնակովի օրենքը. հատկություն–բաղադրություն կախումը կապված է դիագրամի տեսակի հետ (սխեմատիկ)։',
f(st){
  const s = svg(st, 660, 214, 'Կուռնակով'), D = [
    ['մեխանիկական\nխառնուրդ', 'գծային', x => .2 + .55 * x],
    ['անսահմանափակ\nպինդ լուծույթ', 'առավելագույն/նվազագույն', x => .25 + .25 * x + .5 * Math.sin(Math.PI * x), x => .75 - .2 * x - .45 * Math.sin(Math.PI * x)],
    ['սահմանափակ\nպինդ լուծույթ', 'կորագիծ + գծային', x => x < .2 ? .2 + 1.4 * x - 1.5 * x * x : x > .8 ? .78 - .5 * (1 - x) + 1.5 * (1 - x) * (1 - x) * 0 : .42 + (x - .2) / .6 * .23],
    ['քիմիական\nմիացություն', 'եզակի (բեկման) կետ', x => x < .6 ? .2 + .5 * Math.pow(x / .6, .6) : .7 - .35 * Math.pow((x - .6) / .4, .6)]];
  D.forEach(([n, d, f, g], i) => { const A = axes(s, {x:20 + i * 162, y:30, w:130, h:110, xr:[0, 1], yr:[0, 1]});
    n.split('\n').forEach((l, j) => T(s, 20 + i * 162 + 65, 166 + j * 14, l, {'text-anchor':'middle', 'font-size':11, 'font-weight':600})); T(s, 20 + i * 162 + 65, 206, d, {'text-anchor':'middle', 'font-size':10, fill:C.muted});
    S('path', {d:A.fn(f, 0, 1, 100), fill:'none', stroke:C.heat, 'stroke-width':2.4}, s); if (g) S('path', {d:A.fn(g, 0, 1, 100), fill:'none', stroke:C.acc, 'stroke-width':2.2, 'stroke-dasharray':'5 3'}, s);
    T(s, A.X(0), A.Y(0) + 12, 'A', {'text-anchor':'middle', 'font-size':10}); T(s, A.X(1), A.Y(0) + 12, 'B', {'text-anchor':'middle', 'font-size':10});
    if (i === 2){ S('line', {x1:A.X(.2), x2:A.X(.2), y1:A.Y(0), y2:A.Y(1), stroke:C.line, 'stroke-dasharray':'3 3'}, s); S('line', {x1:A.X(.8), x2:A.X(.8), y1:A.Y(0), y2:A.Y(1), stroke:C.line, 'stroke-dasharray':'3 3'}, s); T(s, A.X(.5), A.Y(.95), 'α + β', {'text-anchor':'middle', 'font-size':10, fill:C.muted}); }
    if (i === 1){ T(s, A.X(.5), A.Y(.98), 'կարծրություն, դիմադրություն', {'text-anchor':'middle', 'font-size':9, fill:C.heat}); T(s, A.X(.5), A.Y(.12), 'հաղորդականություն', {'text-anchor':'middle', 'font-size':9, fill:C.acc}); }
    if (i === 3) T(s, A.X(.6), A.Y(.75), 'AₘBₙ', {'text-anchor':'middle', 'font-size':10}); });
}};

/* ---------- 6.1 cooling curve of pure iron ---------- */
VIZ.fecool = {kind:'a', cap:'Մաքուր երկաթի սառեցման կորը. 1539°C՝ բյուրեղացում (Fe<sub>δ</sub>, К8), 1401°C (A₄)՝ Fe<sub>δ</sub> → Fe<sub>γ</sub> (К12), 910°C (A₃)՝ Fe<sub>γ</sub> → Fe<sub>α</sub> (К8), 769°C (A₂)՝ Կյուրիի կետ (ցանցը չի փոխվում, դրանից ցածր Fe<sub>α</sub>-ն ֆեռոմագնիսական է)։',
f(st){
  const row = H('div', {class:'vz-row'}, st), s = svg(row, 380, 280, 'Երկաթի սառեցում'), A = axes(s, {x:56, y:20, w:300, h:230, xr:[0, 1], yr:[500, 1650], xl:'ժամանակ', yl:'T, °C'});
  const K = [[1539, .1, 'հալույթ → Fe_{δ}'], [1401, .06, 'Fe_{δ} → Fe_{γ}'], [910, .06, 'Fe_{γ} → Fe_{α}'], [769, .03, 'Կյուրիի կետ']];
  K.forEach(([v]) => { S('line', {x1:A.X(0), x2:A.X(1), y1:A.Y(v), y2:A.Y(v), stroke:C.line, 'stroke-dasharray':'3 4'}, s); T(s, A.X(0) - 4, A.Y(v) + 4, String(v), {'text-anchor':'end', 'font-size':10}); });
  const seq = []; let Tc = 1640;
  K.forEach(([v, d, n]) => { seq.push([Tc, v, (Tc - v) / 1100 * .55, null]); seq.push([v, v, d, n]); Tc = v; }); seq.push([769, 500, (769 - 500) / 1100 * .55, null]);
  const tot = seq.reduce((a, q) => a + q[2], 0);
  const p = S('path', {fill:'none', stroke:C.acc, 'stroke-width':2.6}, s), dot = S('circle', {r:5.5, fill:C.heat}, s), lab = T(s, 210, 14, '', {'text-anchor':'middle', 'font-weight':700});
  const box = H('div', {}, row), cell = cell3d(box, {kind:'K8', max:260, w:260, h:240, spin:true}), o = out(box);
  let state = '';
  anim(st, (dt, t) => {
    const u = Math.min(tot, (t % 10) / 8.5 * tot), r = []; let acc = 0, Tn = 1640, curName = 'հեղուկ';
    for (const q of seq){ const n = 20; for (let i = 0; i <= n; i++){ const tt = acc + q[2] * i / n; if (tt > u) break; Tn = q[0] + (q[1] - q[0]) * i / n; r.push([A.X(tt / tot), A.Y(Tn)]); if (q[3] && i > 0) curName = q[3]; }
      if (acc + q[2] > u) break; acc += q[2]; }
    attrs(p, {d:pts(r)}); const l = r[r.length - 1]; attrs(dot, {cx:l[0], cy:l[1]});
    const ph = Tn > 1539 || (Tn === 1539 && u < seq[0][2] + seq[1][2] * .5) ? 'L' : Tn > 1401 ? 'd' : Tn > 910 ? 'g' : Tn > 769 ? 'a' : 'm';
    setT(lab, {L:'հեղուկ', d:'Fe_{δ}, К8', g:'Fe_{γ}, К12', a:'Fe_{α}, К8, ոչ մագնիսական', m:'Fe_{α}, К8, ֆեռոմագնիսական'}[ph]);
    if (ph !== state){ state = ph; if (ph === 'L') cell.liquid(); else cell.set(ph === 'g' ? 'K12' : 'K8', 'cell');
      o.innerHTML = ph === 'g' ? 'C-ի լուծելիություն Fe<sub>γ</sub>-ում՝ մինչև <b>2%</b>' : ph === 'a' || ph === 'm' ? 'C-ի լուծելիություն Fe<sub>α</sub>-ում՝ մինչև <b>0,02%</b>' : ''; }
  }, ctl(st), 8.4);
}};

/* ---------- 6.2 phases of the Fe–C system ---------- */
VIZ.phases = {kind:'s', cap:'Fe–C համակարգի ֆազերը. <b>ֆերիտ</b>՝ C-ի ներդրման լուծույթ Fe<sub>α</sub>-ում (К8), <b>աուստենիտ</b>՝ C-ի ներդրման լուծույթ Fe<sub>γ</sub>-ում (К12), <b>ցեմենտիտ</b> Fe₃C, <b>գրաֆիտ</b> (հեքսագոնալ Г3)։ Ներքևում՝ առավելագույն C-ը (լոգարիթմական սանդղակ)։',
f(st){
  const s = svg(st, 660, 270, 'Ֆազեր'), P = [
    ['Ֆերիտ (Ֆ)', 'max 0,02% (727°C)', 'պլաստիկ, փափուկ', .02, g => { sq(g, 60, false); }],
    ['Աուստենիտ (Ա)', 'max 2,14% (1147°C)', '727°C-ից բարձր, HB 200–250', 2.14, g => { sq(g, 60, true); }],
    ['Ցեմենտիտ (Ց)', 'Fe₃C, 6,67%', 'HB ≈ 800, կարծր, բեկուն', 6.67, g => { [[-18, -10], [18, -10], [0, 18]].forEach(([x, y]) => S('circle', {cx:x, cy:y, r:15, fill:C.acc}, g)); S('circle', {cx:0, cy:0, r:8, fill:C.ink}, g); }],
    ['Գրաֆիտ (Գ)', '100% C', 'շատ փափուկ, ամրությունը ≈ 0', 100, g => { for (let j = 0; j < 3; j++) for (let i = 0; i < 4; i++){ const x = -36 + i * 24 + (j % 2) * 12, y = -24 + j * 24; S('polygon', {points:Array.from({length:6}, (_, k) => [x + 9 * Math.cos(k * Math.PI / 3), y + 9 * Math.sin(k * Math.PI / 3)].join(',')).join(' '), fill:'none', stroke:C.ink, 'stroke-width':1.5}, g); } }]];
  function sq(g, a, fcc){ S('rect', {x:-a / 2, y:-a / 2, width:a, height:a, fill:'none', stroke:C.muted}, g);
    [[-1, -1], [1, -1], [1, 1], [-1, 1]].forEach(([x, y]) => S('circle', {cx:x * a / 2, cy:y * a / 2, r:9, fill:C.acc}, g));
    if (fcc) [[0, -1], [1, 0], [0, 1], [-1, 0]].forEach(([x, y]) => S('circle', {cx:x * a / 2, cy:y * a / 2, r:9, fill:C.acc}, g)); else S('circle', {cx:0, cy:0, r:9, fill:C.acc}, g);
    S('circle', {cx:fcc ? 0 : 0, cy:fcc ? 0 : -a / 2 + 0, r:4.5, fill:C.ink, transform:fcc ? '' : `translate(0 ${a / 2})`}, g); }
  P.forEach(([n, c, d, v, draw], i) => { const x = 85 + i * 163; T(s, x, 18, n, {'text-anchor':'middle', 'font-weight':700}); draw(S('g', {transform:`translate(${x} 80)`}, s));
    T(s, x, 140, c, {'text-anchor':'middle', 'font-size':11.5, 'font-weight':600}); T(s, x, 158, d, {'text-anchor':'middle', 'font-size':10.5, fill:C.muted}); });
  const X = v => 40 + (Math.log10(v) + 2) / 4 * 580;
  arrow(s, X(.01), 210, X(100) + 10, 210, C.muted, 1.2, 6); [.01, .1, 1, 10, 100].forEach(v => { S('line', {x1:X(v), x2:X(v), y1:206, y2:214, stroke:C.muted}, s); T(s, X(v), 228, fmt(v, v < 1 ? (v < .1 ? 2 : 1) : 0) + '%', {'text-anchor':'middle', 'font-size':10, fill:C.muted}); });
  P.forEach(([n, , , v], i) => { S('circle', {cx:X(v), cy:210, r:6, fill:[C.acc, C.good, C.heat, C.ink][i]}, s); T(s, X(v), 196 - (i % 2) * 0, n.split(' ')[0], {'text-anchor':'middle', 'font-size':10.5, 'font-weight':600}); });
  T(s, 40, 256, 'ֆերիտ, աուստենիտ, գրաֆիտ՝ կայուն, ցեմենտիտ՝ մետաստաբիլ', {'font-size':11, fill:C.muted});
}};

/* ---------- 6.3 pearlite ---------- */
VIZ.pearlite = {kind:'a', cap:'<b>Պեռլիտ</b>՝ էվտեկտոիդ, 727°C-ում 0,8% C աուստենիտից առաջացող ֆերիտի և ցեմենտիտի մասնիկների խառնուրդ (88% ֆերիտ, 12% ցեմենտիտ)՝ թերթավոր կամ հատիկավոր։ <b>Լեդեբուրիտ</b>՝ էվտեկտիկա (4,3% C, 1147°C)՝ աուստենիտ + ցեմենտիտ, 727°C-ից ցածր՝ պեռլիտ + ցեմենտիտ։',
f(st){
  const W = 240, Hh = 140, cv = canvas(st, W, Hh), G = grains(W, Hh, 5, 44), r = rnd(5);
  const col0 = rgbOf('--accent-soft'), fe = rgbOf('--surface'), cem = rgbOf('--ink'), edge = rgbOf('--muted');
  const bpts = []; for (let i = 0; i < W * Hh; i++) if (G.edge[i] && hash(i) < .004) bpts.push([i % W, (i / W) | 0]);
  const cols = bpts.slice(0, 14).map((p, k) => ({x:p[0], y:p[1], a:hash(k + 7) * Math.PI, t0:hash(k + 3) * 1.5, g:G.lab[p[1] * W + p[0]]}));
  let mode = 'l';
  const o = out(st), c = ctl(st);
  seg(c, [['l', 'թերթավոր'], ['g', 'հատիկավոր']], mode, v => { mode = v; });
  anim(st, (dt, t) => {
    const el = (t % 9), img = cv.img.data;
    for (let y = 0; y < Hh; y++) for (let x = 0; x < W; x++){ const i = y * W + x; let p = G.edge[i] ? edge : col0;
      if (!G.edge[i]) for (const q of cols){ const rr = (el - q.t0) * 28; if (rr <= 0) continue; const dx = x - q.x, dy = y - q.y; if (dx * dx + dy * dy < rr * rr){
        const u = dx * Math.cos(q.a) + dy * Math.sin(q.a), w = ((u % 7) + 7) % 7;
        p = mode === 'l' ? (w < 7 * .12 + .3 ? cem : fe) : (hash(((x / 4) | 0) * 131 + ((y / 4) | 0)) < .12 && (x % 4 < 2) && (y % 4 < 2) ? cem : fe); break; } }
      img[i * 4] = p[0]; img[i * 4 + 1] = p[1]; img[i * 4 + 2] = p[2]; img[i * 4 + 3] = 255; }
    cv.g.putImageData(cv.img, 0, 0);
    o.innerHTML = el < 1.2 ? 'Աուստենիտ (0,8% C), 727°C-ից բարձր' : el < 6.5 ? 'Ա<sub>0,8</sub> → Ֆ<sub>0,02</sub> + Ց<sub>6,67</sub>՝ պեռլիտի գաղութներն աճում են հատիկների սահմաններից' : '<b>Պեռլիտ</b>՝ ֆերիտ (բաց) + ցեմենտիտ (մուգ)';
  }, c, 6.5);
}};

/* ---------- 6.5 / 7.1 microstructure by carbon content ---------- */
const GROUPS = [
  [0, .02, 'Տեխնիկական երկաթ', 'ֆերիտ (+ երրորդային ցեմենտիտ)'], [.02, .8, 'Մինչէվտեկտոիդային պողպատ', 'ֆերիտ + պեռլիտ'], [.8, .8, 'Էվտեկտոիդային պողպատ', 'պեռլիտ'],
  [.8, 2.14, 'Հետէվտեկտոիդային պողպատ', 'պեռլիտ + երկրորդային ցեմենտիտ'], [2.14, 4.3, 'Մինչէվտեկտիկական չուգուն', 'պեռլիտ + երկրորդային ցեմենտիտ + լեդեբուրիտ'],
  [4.3, 4.3, 'Էվտեկտիկական չուգուն', 'լեդեբուրիտ'], [4.3, 6.67, 'Հետէվտեկտիկական չուգուն', 'լեդեբուրիտ + առաջնային ցեմենտիտ']];
VIZ.steel = {kind:'i', cap: a => (a === 'steel' ? 'Պողպատների հավասարակշիռ ստրուկտուրան (դանդաղ սառեցում). C-ի աճով պեռլիտը շատանում է, 0,8%-ում միայն պեռլիտ է, ավելի շատ C-ի դեպքում պեռլիտի հատիկների շուրջ առաջանում է ցեմենտիտի ցանց։'
  : 'Fe–C համաձուլվածքների դասակարգումը ըստ ածխածնի և ստրուկտուրան սենյակային ջերմաստիճանում։') + ' Պատկերը սխեմատիկ է։',
f(st, a){
  const steel = a === 'steel', W = 260, Hh = 150, cv = canvas(st, W, Hh), G = grains(W, Hh, 34, 77), bd = bdist(G, 8);
  const fe = rgbOf('--surface'), ink = rgbOf('--ink'), cem = rgbOf('--heat-soft'), mut = rgbOf('--muted'), led = rgbOf('--warn-soft');
  const o = out(st), lg = H('div', {class:'vz-out vz-mut', html:'■ բաց՝ ֆերիտ · շերտավոր՝ պեռլիտ · նարնջագույն՝ ցեմենտիտ' + (steel ? '' : ' · կետավոր՝ լեդեբուրիտ')}, st);
  const order = G.P.map((_, i) => i).sort((x, y) => hash(x) - hash(y)), rank = new Int16Array(G.P.length); order.forEach((g, k) => rank[g] = k);
  const needles = Array.from({length:14}, (_, k) => [hash(k + 50) * W, hash(k + 90) * Hh, hash(k + 20) * Math.PI, 30 + hash(k) * 50]);
  function draw(Cp){
    const img = cv.img.data, n = G.P.length;
    const fP = Cp <= .02 ? 0 : Cp < .8 ? (Cp - .02) / .78 : 1, net = Cp > .8 ? Math.min(5, 1 + (Cp - .8) / 1.34 * 3) : 0, fL = Cp <= 2.14 ? 0 : Cp < 4.3 ? (Cp - 2.14) / 2.16 : 1;
    for (let y = 0; y < Hh; y++) for (let x = 0; x < W; x++){ const i = y * W + x, g = G.lab[i], k = rank[g]; let p;
      const isL = k < fL * n, isP = !isL && k < fP * n;
      if (isL) p = ((x + y * 3) % 6 < 2) ? cem : led; else if (isP) p = ((x * .8 + y * .6 * (hash(g) > .5 ? 1 : -1)) % 5 + 5) % 5 < 1.6 ? mut : fe; else p = fe;
      if (bd[i] < net) p = cem; if (G.edge[i] && !net) p = ink;
      img[i * 4] = p[0]; img[i * 4 + 1] = p[1]; img[i * 4 + 2] = p[2]; img[i * 4 + 3] = 255; }
    cv.g.putImageData(cv.img, 0, 0);
    if (Cp > 4.3){ cv.g.fillStyle = col('--heat'); const m = Math.round((Cp - 4.3) / 2.37 * needles.length); needles.slice(0, m).forEach(([x, y, an, l]) => { cv.g.save(); cv.g.translate(x, y); cv.g.rotate(an); cv.g.fillRect(-l / 2, -2.5, l, 5); cv.g.restore(); }); }
    if (Cp < .02){ cv.g.fillStyle = col('--heat'); for (let k = 0; k < 18; k++){ const i = Math.floor(hash(k + 300) * W * Hh); for (let j = i; j < W * Hh; j++) if (G.edge[j]){ cv.g.fillRect(j % W, (j / W) | 0, 2, 2); break; } } }
    const gr = GROUPS.find(q => q[0] === q[1] ? Math.abs(Cp - q[0]) < .005 : Cp > q[0] - 1e-9 && Cp < q[1] + 1e-9 && !(Math.abs(Cp - .8) < .005) && !(Math.abs(Cp - 4.3) < .005)) || GROUPS[0];
    o.innerHTML = `<b>${fmt(Cp, 2)}% C</b> — <b>${gr[2]}</b>՝ ${gr[3]}`;
  }
  const c = ctl(st), max = steel ? 2.14 : 6.67, sl = slider(c, 'C', 0, max, .01, steel ? .4 : 1.2, v => fmt(v, 2) + '%', draw);
  [[.4, '0,4'], [.8, '0,8'], [1.2, '1,2'], ...(steel ? [] : [[3, '3'], [4.3, '4,3'], [5.5, '5,5']])].forEach(([v, n]) => btn(c, n + '%', () => sl.set(v)));
  draw(steel ? .4 : 1.2);
}};

/* ---------- 7.2 influence of carbon and impurities ---------- */
VIZ.cinf = {kind:'i', cap:'C-ի աճով աճում են ամրությունն ու կարծրությունը, էլեկտրադիմադրությունը և կոերցիտիվ ուժը, նվազում են պլաստիկությունն ու մածուցիկությունը, մագնիսական թափանցելիությունը, կոռոզիակայունությունը, խտությունը, վատանում են եռակցելիությունը և կռելիությունը։ Սլաքները որակական են։',
f(st){
  const up = ['ամրություն', 'կարծրություն', 'էլեկտրադիմադրություն', 'կոերցիտիվ ուժ'], dn = ['պլաստիկություն', 'մածուցիկություն', 'մագն. թափանցելիություն', 'կոռոզիակայունություն', 'խտություն', 'եռակցելիություն', 'կռելիություն'];
  const s = svg(st, 660, 220, 'Ածխածնի ազդեցություն'), B = [];
  [[up, C.heat, 20, '↑ աճում են'], [dn, C.acc, 340, '↓ նվազում/վատանում են']].forEach(([L, c, x, h]) => { T(s, x, 18, h, {'font-weight':700, fill:c});
    L.forEach((n, i) => { T(s, x, 44 + i * 24, n, {'font-size':12}); S('rect', {x:x + 170, y:33 + i * 24, width:120, height:14, rx:3, fill:C.sunk}, s); B.push({r:S('rect', {x:x + 170, y:33 + i * 24, height:14, rx:3, fill:c}, s), up:c === C.heat}); }); });
  const o = out(st);
  function draw(Cp){ const k = Cp / 1.35; B.forEach(b => attrs(b.r, {width:120 * (b.up ? .2 + .75 * k : .95 - .75 * k)})); o.innerHTML = `C = <b class="mono">${fmt(Cp, 2)}%</b>`; }
  slider(ctl(st), 'C', 0, 1.35, .01, .45, v => fmt(v, 2) + '%', draw); draw(.45);
  H('div', {class:'vz-out', html:'<b class="vz-good">Mn</b>՝ ապաօքսիդացում, կապում է ծծումբը (MnS), ամրացնում է ֆերիտը · <b class="vz-good">Si</b>՝ ապաօքսիդիչ, բարձրացնում է կարծրությունն ու ամրությունը · <b class="vz-bad">P</b>՝ սառնաբեկունություն · <b class="vz-bad">S</b>՝ շիկաբեկություն (FeS էվտեկտիկան հալվում է ≈ 985°C-ում)'}, st);
}};

/* ---------- 7.3 steel grades ---------- */
VIZ.grade = {kind:'i', cap:'Պողպատների մակնիշների վերծանումը՝ ըստ դասախոսության կանոնների։ Ընտրեք մակնիշը։',
f(st){
  const G = {
    'Ст3':['Սովորական որակի կոնստրուկցիոն, խումբ А՝ երաշխավորված մեխանիկական հատկություններ', 'թիվը պայմանական համար է (մեծացմամբ աճում են C-ն և ամրությունը)', null],
    'БСт3':['Սովորական որակի, խումբ Б՝ երաշխավորված քիմիական բաղադրություն', 'թիվը պայմանական համար է', null],
    'ВСт3':['Սովորական որակի, խումբ В՝ երաշխավորված և՛ հատկություններ, և՛ բաղադրություն', 'թիվը պայմանական համար է', null],
    '08':['Որակյալ կոնստրուկցիոն', 'C՝ տոկոսի հարյուրերորդականներով → 0,08% C', .08],
    '20':['Որակյալ կոնստրուկցիոն', '0,20% C', .2],
    '45':['Որակյալ կոնստրուկցիոն', '0,45% C', .45],
    '65Г':['Որակյալ կոնստրուկցիոն, մանգանի բարձր պարունակությամբ (Г)', '0,65% C', .65],
    'У7':['Ածխածնային գործիքային', 'C՝ տոկոսի տասնորդականներով → 0,7% C', .7],
    'У10А':['Ածխածնային գործիքային, «А»՝ բարձրորակ', '1,0% C', 1],
    'У13':['Ածխածնային գործիքային', '1,3% C', 1.3]};
  const c = ctl(st), s = svg(st, 640, 110, 'Ածխածին'), X = v => 30 + v / 1.4 * 580, o = out(st);
  [[0, .3, 'ցածրածխածնային', C.accS], [.3, .65, 'միջինածխածնային', C.goodS], [.65, 1.35, 'բարձրածխածնային', C.heatS]].forEach(([a, b, n, f]) => { S('rect', {x:X(a), y:30, width:X(b) - X(a), height:24, fill:f}, s); T(s, (X(a) + X(b)) / 2, 46, n, {'text-anchor':'middle', 'font-size':11, 'font-weight':600}); });
  T(s, X(.32), 76, 'կոնստրուկցիոն (մինչև 0,65%)', {'text-anchor':'middle', 'font-size':10.5, fill:C.muted}); T(s, X(1), 76, 'գործիքային (0,65–1,35%)', {'text-anchor':'middle', 'font-size':10.5, fill:C.muted});
  [0, .3, .65, 1, 1.35].forEach(v => T(s, X(v), 98, fmt(v, 2).replace(/,?0+$/, '') + '%', {'text-anchor':'middle', 'font-size':10, fill:C.muted}));
  const mk = S('path', {fill:C.bad}, s);
  function pick(k){ const [a, b, v] = G[k]; o.innerHTML = `<b style="font-size:16px">${k}</b> — ${a}<br>${b}`; attrs(mk, {d:v == null ? '' : `M${X(v)} 30 l-7 -12 h14z`}); }
  seg(c, ['Ст3', 'БСт3', 'ВСт3', '08', '20', '45', '65Г', 'У7', 'У10А', 'У13'].map(k => [k, k]), '45', pick); pick('45');
}};

/* ---------- 7.4 cast irons ---------- */
VIZ.castiron = {kind:'i', cap:'Չուգունները ըստ ածխածնի ձևի. <b>սպիտակ</b>՝ ցեմենտիտ (մետաղե կաղապար, արագ սառեցում), <b>գորշ</b>՝ թերթավոր գրաֆիտ (ավազե կաղապար, դանդաղ սառեցում), <b>բարձրամուր</b>՝ գնդաձև գրաֆիտ (Mg կամ Ce), <b>կռելի</b>՝ փաթիլաձև գրաֆիտ (սպիտակ չուգունի թրծաթողում 900–1000°C)։ Հիմքը՝ ֆերիտային, ֆերիտապեռլիտային կամ պեռլիտային։ Պատկերը սխեմատիկ է։',
f(st){
  const W = 260, Hh = 150, cv = canvas(st, W, Hh), G = grains(W, Hh, 30, 91), bd = bdist(G, 6), o = out(st);
  const fe = rgbOf('--surface'), mut = rgbOf('--muted'), ink = rgbOf('--ink'), cem = rgbOf('--heat-soft'), led = rgbOf('--warn-soft');
  let kind = 'g', base = 'fp';
  const r = rnd(13), fl = Array.from({length:26}, () => [r() * W, r() * Hh, r() * Math.PI, 18 + r() * 26, r() * 2 - 1]), sp = Array.from({length:34}, () => [r() * W, r() * Hh, 3 + r() * 3]);
  const INFO = {w:['Սպիտակ', 'ամբողջ C-ը՝ ցեմենտիտ (40–60%), լուսավոր կտրվածք, բեկուն, HB ≈ 500, մաշակայուն', '—'],
    g:['Գորշ', 'թերթավոր գրաֆիտ, ամենատարածված ձուլման նյութը, պլաստիկ չէ, շփման փոքր գործակից', 'СЧ 12-28՝ σ<sub>բ</sub> ձգման 12 և ծռման 28 կգ/մմ²'],
    v:['Բարձրամուր', 'գնդաձև գրաֆիտ, զգալիորեն ամուր գորշից, որոշ պլաստիկություն և մածուցիկություն', 'ВЧ 42-12՝ σ<sub>բ</sub> = 42 կգ/մմ², δ = 12%'],
    k:['Կռելի', 'փաթիլաձև գրաֆիտ, որոշ պլաստիկություն և մածուցիկություն (ավտոմեքենաներ, գյուղտեխնիկա)', 'КЧ 33-8՝ σ<sub>բ</sub> = 33 կգ/մմ², δ = 8%']};
  function draw(){
    const img = cv.img.data;
    for (let y = 0; y < Hh; y++) for (let x = 0; x < W; x++){ const i = y * W + x, g = G.lab[i]; let p;
      if (kind === 'w') p = bd[i] < 4 || hash(g) < .4 ? cem : ((x + y * 3) % 6 < 2 ? cem : mut);
      else { const pear = base === 'p' || (base === 'fp' && hash(g) < .5); p = pear ? (((x * .8 + y * .6) % 5 + 5) % 5 < 1.6 ? mut : fe) : fe; if (G.edge[i]) p = mixc(ink, fe, .5); }
      img[i * 4] = p[0]; img[i * 4 + 1] = p[1]; img[i * 4 + 2] = p[2]; img[i * 4 + 3] = 255; }
    const g = cv.g; g.putImageData(cv.img, 0, 0); g.fillStyle = col('--ink'); g.strokeStyle = col('--ink');
    if (kind === 'g') fl.forEach(([x, y, a, l, b]) => { g.lineWidth = 2.6; g.beginPath(); g.moveTo(x - Math.cos(a) * l / 2, y - Math.sin(a) * l / 2); g.quadraticCurveTo(x + b * 8 * Math.sin(a), y - b * 8 * Math.cos(a), x + Math.cos(a) * l / 2, y + Math.sin(a) * l / 2); g.stroke(); });
    if (kind === 'v') sp.forEach(([x, y, rr]) => { g.beginPath(); g.arc(x, y, rr, 0, 7); g.fill(); });
    if (kind === 'k') sp.slice(0, 20).forEach(([x, y, rr], k) => { for (let j = 0; j < 7; j++){ g.beginPath(); g.arc(x + Math.cos(j * 2.4 + k) * rr * .9, y + Math.sin(j * 2.4 + k) * rr * .9, rr * .55, 0, 7); g.fill(); } });
    const I = INFO[kind];
    o.innerHTML = `<b>${I[0]} չուգուն</b>՝ ${I[1]}<br><span class="vz-mut">Մակնիշ՝ ${I[2]}</span>`;
    bs.style.display = kind === 'w' ? 'none' : '';
  }
  const c = ctl(st);
  seg(c, [['w', 'Սպիտակ'], ['g', 'Գորշ'], ['v', 'Բարձրամուր'], ['k', 'Կռելի']], kind, v => { kind = v; draw(); });
  const bs = H('div', {class:'vz-ctl'}, st);
  seg(bs, [['f', 'ֆերիտային'], ['fp', 'ֆերիտապեռլիտային'], ['p', 'պեռլիտային']], base, v => { base = v; draw(); });
  draw();
}};

/* which visuals go under which lecture section ("lectureId:sectionIndex") */
Object.assign(window.VIZMAP, {
  '1:1':['loads'], '1:2':['tensile'], '1:3':['hardness'], '1:4':['density', 'hyster'],
  '2:0':['metalbond'], '2:1':['cooling'], '2:2':['cell:K6'], '2:3':['cell'], '2:4':['polyfe'], '2:5':['aniso'], '2:6':['defects'],
  '3:0':['fenergy:1'], '3:1':['nucleation'], '3:2':['fenergy:2', 'curie'], '3:3':['ingot'], '3:4':['stress', 'slip'], '3:5':['workhard'], '3:6':['recryst', 'bochvar'], '3:7':['hotcold'],
  '4:1':['solsol'], '4:2':['fe3c'], '4:3':['mixture'],
  '5:0':['build'], '5:1':['gibbs'], '5:2':['cuni'], '5:3':['cuni:lever'], '5:4':['eutectic'], '5:5':['kurnakov'],
  '6:0':['fecool'], '6:1':['phases'], '6:2':['pearlite'], '6:4':['steel'],
  '7:0':['steel:steel'], '7:1':['cinf'], '7:2':['grade'], '7:3':['castiron']});
})();
