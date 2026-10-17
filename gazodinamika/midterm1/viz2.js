/* Gas-dynamics lecture visuals, topics 4 and 6, and the section map. */
(function(){
'use strict';
const {C, S, H, T, setT, attrs, svg, pts, arrow, axes, clamp, lerp, fmt, ctl, slider, seg, btn, out, anim} = window.VZ;
const {R, K, CV, CP, kJ, cylinder, tint} = window.GAZ_VZ;
const VIZ = window.VIZ;
const ss = x => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
const typeset = el => { if (window.renderMathInElement) renderMathInElement(el, {delimiters:[{left:'\\(', right:'\\)', display:false}], throwOnError:false}); };

/* ---------- 4.1 the basic processes from one state ---------- */
const FAM = [
  {id:'v', n:'իզոխոր', d:'υ = const', c:C.acc},
  {id:'p', n:'իզոբար', d:'p = const', c:C.heat},
  {id:'T', n:'իզոթերմ', d:'pυ = const', c:C.good},
  {id:'s', n:'ադիաբատ', d:'pυ^{k} = const', c:C.bad}];
VIZ.procfam = {kind:'i', cap:'Հիմնական պրոցեսները միևնույն սկզբնական վիճակից \\(p\\text{–}\\upsilon\\) դիագրամում (ընդարձակում և սեղմում)։ Ընտրեք պրոցեսը՝ այն ընդգծելու համար։',
f(st){
  const s = svg(st, 600, 250, 'Հիմնական պրոցեսներ'), A = axes(s, {x:50, y:20, w:380, h:200, xr:[0, 2.4], yr:[0, 3], xl:'υ', yl:'p'});
  const L = {v:S('path', {d:`M${A.X(1)} ${A.Y(.15)}V${A.Y(2.9)}`}, s), p:S('path', {d:`M${A.X(.15)} ${A.Y(1)}H${A.X(2.3)}`}, s),
    T:S('path', {d:A.fn(v => 1 / v, .36, 2.3)}, s), s:S('path', {d:A.fn(v => Math.pow(1 / v, K), .47, 2.3)}, s)};
  S('circle', {cx:A.X(1), cy:A.Y(1), r:5, fill:C.ink}, s); T(s, A.X(1) + 8, A.Y(1) - 8, '1', {'font-weight':700});
  const items = FAM.map((f, i) => { const g = S('g', {}, s); S('rect', {x:450, y:40 + i * 40, width:16, height:4, fill:f.c}, g);
    T(g, 474, 46 + i * 40, f.n, {'font-weight':600}); T(g, 474, 62 + i * 40, f.d, {fill:C.muted, 'font-size':11}); return g; });
  function hl(id){ FAM.forEach((f, i) => { attrs(L[f.id], {fill:'none', stroke:f.c, 'stroke-width':id === f.id ? 4.5 : 2, opacity:id && id !== f.id ? .25 : 1}); items[i].setAttribute('opacity', id && id !== f.id ? .4 : 1); }); }
  seg(ctl(st), [['', 'Բոլորը'], ...FAM.map(f => [f.id, f.n])], '', hl); hl('');
}};

/* ---------- 4.2–4.5 process lab: cylinder, p–υ, T–s, energy split ---------- */
const PROC = {
  v:{n:'Իզոխոր', sl:'T₂/T₁', r:[.5, 2], d:1.6, sc:230, st:x => ({v:1, T:x}), pv:[2, 2.3], ts:[600, 2.3]},
  p:{n:'Իզոբար', sl:'υ₂/υ₁', r:[.5, 2], d:1.6, sc:320, st:x => ({v:x, T:x}), pv:[2.3, 1.6], ts:[750, 2.3]},
  T:{n:'Իզոթերմ', sl:'υ₂/υ₁', r:[.4, 2.5], d:2, sc:85, st:x => ({v:x, T:1}), pv:[2.7, 2.8], ts:[300, 1.6]},
  s:{n:'Ադիաբատ', sl:'υ₂/υ₁', r:[.4, 2.5], d:2, sc:100, st:x => ({v:x, T:Math.pow(1 / x, K - 1)}), pv:[2.7, 3.8], ts:[300, 1.6]}};
VIZ.proc = {kind:'a', cap: a => ({
  v:'Իզոխոր պրոցես. աշխատանք չի կատարվում (\\(\\ell=0\\)), ամբողջ ջերմությունը ծախսվում է <b>ներքին էներգիայի</b> փոփոխման վրա. \\(p_2/p_1=T_2/T_1\\)։',
  p:'Իզոբար պրոցես. ջերմությունը ծախսվում է և՛ ներքին էներգիայի աճի, և՛ աշխատանքի վրա, \\(q=i_2-i_1\\). աշխատանքի բաժինը \\(\\ell/q=(k-1)/k\\approx0{,}29\\)։',
  T:'Իզոթերմ պրոցես. \\(\\Delta u=0\\), ամբողջ ջերմությունը ծախսվում է <b>աշխատանքի</b> վրա, \\(q=\\ell=RT\\ln(\\upsilon_2/\\upsilon_1)\\)։ \\(T\\text{–}s\\)-ում՝ հորիզոնական։',
  s:'Ադիաբատ պրոցես. \\(q=0\\), աշխատանքը կատարվում է ներքին էներգիայի հաշվին (\\(\\ell=-\\Delta u\\)). ընդարձակման ժամանակ գազը սառչում է, սեղմման ժամանակ՝ տաքանում։ \\(T\\text{–}s\\)-ում՝ ուղղաձիգ (իզոէնտրոպ)։'}[a]) + ' 1 կգ օդ, սկզբում 1 բար, 300 Կ։',
f(st, a){
  const P = PROC[a], T1 = 300, v1 = R * T1 / 1e5;
  const s = svg(st, 620, 330, P.n);
  const cyl = cylinder(s, 30, 70, 90, 150, {insulated:a === 's'});
  const A = axes(s, {x:170, y:24, w:190, h:190, xr:[0, P.pv[0]], yr:[0, P.pv[1]], xl:'υ/υ₁', yl:'p/p₁'});
  const B = axes(s, {x:410, y:24, w:180, h:190, xr:[-P.ts[0], P.ts[0]], yr:[0, P.ts[1]], xl:'s − s₁', yl:'T/T₁'});
  [[A, 1, 0, 'x'], [A, 1, 0, 'y'], [B, 1, 0, 'y']].forEach(([X, v, z, ax]) => ax === 'x' ? T(s, X.X(v), X.Y(0) + 14, '1', {'text-anchor':'middle', fill:C.muted, 'font-size':10}) : T(s, X.X(X.o.xr[0]) - 5, X.Y(v) + 4, '1', {'text-anchor':'end', fill:C.muted, 'font-size':10}));
  const pv = S('path', {fill:'none', stroke:C.ink, 'stroke-width':2.5}, s), ts = S('path', {fill:'none', stroke:C.ink, 'stroke-width':2.5}, s), tsA = S('path', {fill:C.heat, opacity:.18}, s);
  const d1 = S('circle', {r:6, fill:C.heat}, s), d2 = S('circle', {r:6, fill:C.heat}, s);
  [[A, 1, 1], [B, 0, 1]].forEach(([X, x, y]) => { S('circle', {cx:X.X(x), cy:X.Y(y), r:3.5, fill:C.ink}, s); T(s, X.X(x) - 12, X.Y(y) - 6, '1', {'font-weight':700}); });
  const harr = S('g', {}, s), warr = S('g', {}, s);
  // energy bars
  const by = 252, bx = 290, bw = 130, rows = [['q', C.heat], ['Δu', C.warn], ['ℓ', C.good]].map(([n, c], i) => {
    T(s, bx - 10, by + i * 26 + 13, n, {'text-anchor':'end', 'font-weight':700});
    return {r:S('rect', {y:by + i * 26, height:18, rx:2, fill:c}, s), t:T(s, 0, by + i * 26 + 13, '', {'font-size':11.5})}; });
  S('line', {x1:bx + bw, x2:bx + bw, y1:by - 6, y2:by + 76, stroke:C.muted}, s);
  T(s, bx + bw, by - 10, '0', {'text-anchor':'middle', fill:C.muted, 'font-size':10});
  const note = T(s, 20, 292, '', {fill:C.muted, 'font-size':11});
  let x = P.d;
  const state = (r) => { const q = P.st(r); q.p = q.T / q.v; q.s = CV * Math.log(q.T) + R * Math.log(q.v); return q; };
  const c = ctl(st);
  slider(c, P.sl, P.r[0], P.r[1], .02, P.d, v => fmt(v, 2), v => { x = v; An.t = 0; An.draw(); });
  const An = anim(st, (dt, t) => {
    const end = state(x), N = 50, path = [];
    for (let i = 0; i <= N; i++) path.push(state(lerp(1, x, i / N)));
    attrs(pv, {d:pts(path.map(q => [A.X(q.v), A.Y(q.p)]))});
    attrs(ts, {d:pts(path.map(q => [B.X(q.s), B.Y(q.T)]))});
    attrs(tsA, {d:pts([[B.X(0), B.Y(0)], ...path.map(q => [B.X(q.s), B.Y(q.T)]), [B.X(end.s), B.Y(0)]]) + 'Z', fill:end.s >= 0 ? C.heat : C.acc});
    const ph = t % 4.5, u = ss(ph / 2.6) * (ph < 3.6 ? 1 : 1 - ss((ph - 3.6) / .8)), cur = state(lerp(1, x, u));
    attrs(d1, {cx:A.X(cur.v), cy:A.Y(cur.p)}); attrs(d2, {cx:B.X(cur.s), cy:B.Y(cur.T)});
    const py = cyl(clamp(cur.v / 2.7, .08, .97), tint(cur.T));
    const dT = (end.T - 1) * T1, du = CV * dT, l = a === 'v' ? 0 : a === 'p' ? R * dT : a === 'T' ? R * T1 * Math.log(x) : -du, q = du + l;
    [q, du, l].forEach((val, i) => { const w = clamp(val / P.sc, -1, 1) * bw; attrs(rows[i].r, {x:w < 0 ? bx + bw + w : bx + bw, width:Math.abs(w)});
      attrs(rows[i].t, {x:w < 0 ? bx + bw + 6 : bx + bw + w + 6}); setT(rows[i].t, kJ(val) + ' կՋ/կգ'); });
    while (harr.firstChild) harr.removeChild(harr.firstChild);
    while (warr.firstChild) warr.removeChild(warr.firstChild);
    const moving = ph < 2.6;
    if (a !== 's' && Math.abs(q) > 1 && moving) for (let i = 0; i < 3; i++){ const xx = 45 + i * 30; q > 0 ? arrow(harr, xx, 252, xx, 226, C.heat, 2.4, 8) : arrow(harr, xx, 226, xx, 252, C.acc, 2.4, 8); }
    if (Math.abs(l) > 1 && moving) l > 0 ? arrow(warr, 140, py + 10, 140, py - 30, C.good, 2.4, 8) : arrow(warr, 140, py - 30, 140, py + 10, C.bad, 2.4, 8);
    setT(note, a === 's' ? 'Պատերը ջերմամեկուսացված են՝ q = 0' : q > 0 ? 'Ջերմությունը հաղորդվում է' : 'Ջերմությունը հեռացվում է');
  }, c, 2.7);
}};

/* ---------- 4.5 adiabat steeper than isotherm ---------- */
VIZ.adiso = {kind:'i', cap:'Ադիաբատն (\\(p\\upsilon^k=\\text{const}\\)) ընթանում է իզոթերմից (\\(p\\upsilon=\\text{const}\\)) <b>ավելի զառիթափ</b>. սեղմման ժամանակ ջերմաստիճանն էլ է աճում։ \\(k\\)-ն՝ ըստ կինետիկ տեսության. միատոմ 1,67, երկատոմ 1,40, եռատոմ 1,33։',
f(st){
  const s = svg(st, 620, 240, 'Ադիաբատ և իզոթերմ'), A = axes(s, {x:50, y:20, w:340, h:190, xr:[0, 2.5], yr:[0, 4], xl:'υ', yl:'p'});
  S('path', {d:A.fn(v => 1 / v, .26, 2.4), fill:'none', stroke:C.good, 'stroke-width':2, 'stroke-dasharray':'6 4'}, s);
  const ad = S('path', {fill:'none', stroke:C.bad, 'stroke-width':3}, s);
  S('circle', {cx:A.X(1), cy:A.Y(1), r:4.5, fill:C.ink}, s);
  T(s, 440, 50, '– – իզոթերմ, pυ = const', {fill:C.good}); T(s, 440, 72, '—— ադիաբատ, pυ^{k} = const', {fill:C.bad});
  const t1 = T(s, 440, 110, ''), t2 = T(s, 440, 130, ''), t4 = T(s, 440, 150, ''), t3 = T(s, 440, 176, '', {'font-weight':600});
  function draw(k){
    attrs(ad, {d:A.fn(v => Math.pow(1 / v, k), Math.pow(1 / 3.9, 1 / k), 2.4)});
    setT(t1, 'υ₁/υ₂ = 2 (սեղմում)՝'); setT(t2, 'իզոթերմ՝ p₂/p₁ = 2'); setT(t4, 'ադիաբատ՝ p₂/p₁ = 2^{k} = ' + fmt(Math.pow(2, k), 2));
    setT(t3, 'T₂/T₁ = 2^{k−1} = ' + fmt(Math.pow(2, k - 1), 2));
  }
  seg(ctl(st), [[5 / 3, 'միատոմ, k = 1,67'], [1.4, 'երկատոմ, k = 1,40'], [4 / 3, 'եռատոմ, k = 1,33']], 1.4, draw); draw(1.4);
}};

/* ---------- 4.6 polytropes ---------- */
VIZ.poly = {kind:'i', cap:'Պոլիտրոպ \\(p\\upsilon^n=\\text{const}\\)՝ ընդհանրացնող պրոցես. \\(n=0\\) իզոբար, \\(n=1\\) իզոթերմ, \\(n=k\\) ադիաբատ, \\(n=\\pm\\infty\\) իզոխոր։ Վերջնական կետի դիրքով. իզոխորից աջ՝ \\(\\ell>0\\), իզոթերմից վեր՝ \\(\\Delta u>0\\), ադիաբատից վեր՝ \\(q>0\\)։ \\(1&lt;n&lt;k\\)-ում \\(c&lt;0\\)։',
f(st){
  const s = svg(st, 640, 260, 'Պոլիտրոպներ'), A = axes(s, {x:40, y:20, w:320, h:210, xr:[0, 2.2], yr:[0, 3.2], xl:'υ', yl:'p'});
  S('path', {d:`M${A.X(1)} ${A.Y(.1)}V${A.Y(3.1)}`, stroke:C.acc, fill:'none', 'stroke-dasharray':'4 4'}, s);
  S('path', {d:`M${A.X(.2)} ${A.Y(1)}H${A.X(2.1)}`, stroke:C.heat, fill:'none', 'stroke-dasharray':'4 4'}, s);
  S('path', {d:A.fn(v => 1 / v, .33, 2.1), stroke:C.good, fill:'none', 'stroke-dasharray':'4 4'}, s);
  S('path', {d:A.fn(v => Math.pow(1 / v, K), .44, 2.1), stroke:C.bad, fill:'none', 'stroke-dasharray':'4 4'}, s);
  T(s, A.X(1) + 4, A.Y(3.1) + 4, 'n = ±∞', {fill:C.acc, 'font-size':11}); T(s, A.X(2.1), A.Y(1) - 6, 'n = 0', {fill:C.heat, 'font-size':11, 'text-anchor':'end'});
  T(s, A.X(2.12), A.Y(1 / 2.1) - 4, 'n = 1', {fill:C.good, 'font-size':11}); T(s, A.X(2.12), A.Y(Math.pow(1 / 2.1, K)) + 12, 'n = k', {fill:C.bad, 'font-size':11});
  const cur = S('path', {fill:'none', stroke:C.ink, 'stroke-width':3.5}, s), e = S('circle', {r:6, fill:C.ink}, s);
  S('circle', {cx:A.X(1), cy:A.Y(1), r:4.5, fill:C.ink}, s); T(s, A.X(1) - 14, A.Y(1) + 16, '1', {'font-weight':700});
  const lab = T(s, A.X(1.6) + 8, 0, '2', {'font-weight':700});
  const tx = 395, L = [0, 1, 2, 3, 4, 5, 6].map(i => T(s, tx, 40 + i * 24, '', {'font-size':12.5}));
  let n = 1.2;
  function draw(){
    const inf = !isFinite(n), v2 = inf ? 1 : 1.6, p2 = inf ? 1.6 : Math.pow(1 / v2, n);
    attrs(cur, {d:inf ? `M${A.X(1)} ${A.Y(.15)}V${A.Y(3.1)}` : A.fn(v => Math.pow(1 / v, n), Math.max(.12, Math.pow(1 / 3.1, 1 / Math.max(n, .01)) * (n > 0 ? 1 : 0) + (n <= 0 ? .2 : 0)), 2.1)});
    attrs(e, {cx:A.X(v2), cy:A.Y(p2)}); attrs(lab, {x:A.X(v2) + 8, y:A.Y(p2) - 6});
    const T2 = p2 * v2, dT = 300 * (T2 - 1), du = CV * dT, l = inf ? 0 : Math.abs(n - 1) < 1e-6 ? R * 300 * Math.log(v2) : R / (n - 1) * 300 * (1 - T2), q = du + l;
    const c = inf ? CV : Math.abs(n - 1) < 1e-6 ? Infinity : CV * (n - K) / (n - 1);
    const sg = v => v > 1e-6 ? '<tspan fill="var(--good)">&gt; 0</tspan>' : v < -1e-6 ? '<tspan fill="var(--bad)">&lt; 0</tspan>' : '= 0';
    const rowsTxt = [
      `n = ${inf ? '±∞ (իզոխոր)' : fmt(n, 2) + (n === 0 ? ' (իզոբար)' : n === 1 ? ' (իզոթերմ)' : Math.abs(n - K) < 1e-6 ? ' (ադիաբատ)' : '')}`,
      `c = c_{υ}(n − k)/(n − 1) = ${isFinite(c) ? fmt(c, 0) + ' Ջ/(կգ·Կ)' : '±∞'}`,
      inf ? '1 → 2՝ տաքացում υ = const' : '1 → 2՝ ընդարձակում, υ₂ = 1,6υ₁'];
    L[0].textContent = rowsTxt[0]; setT(L[1], rowsTxt[1]); L[2].textContent = rowsTxt[2]; L[2].style.fill = 'var(--muted)';
    L[3].innerHTML = `ℓ ${sg(l)}  <tspan fill="var(--muted)">(${kJ(l)} կՋ/կգ)</tspan>`;
    L[4].innerHTML = `Δu ${sg(du)}  <tspan fill="var(--muted)">(${kJ(du)} կՋ/կգ)</tspan>`;
    L[5].innerHTML = `q ${sg(q)}  <tspan fill="var(--muted)">(${kJ(q)} կՋ/կգ)</tspan>`;
    L[6].innerHTML = n > 1 && n < K ? '<tspan fill="var(--warn)" font-weight="600">1 &lt; n &lt; k՝ c &lt; 0</tspan>' : '';
  }
  const c = ctl(st), sl = slider(c, 'n', -1.5, 4, .05, 1.2, v => fmt(v, 2), v => { n = v; draw(); });
  seg(c, [[0, 'n = 0'], [1, 'n = 1'], [K, 'n = k'], [Infinity, 'n = ±∞']], -9, v => { n = v; if (isFinite(v)) sl.el.value = v; draw(); });
  draw();
}};

/* ---------- 4.7 processes in T–s ---------- */
VIZ.ts4 = {kind:'i', cap:'\\(T\\text{–}s\\) դիագրամում կորի տակ մակերեսը պրոցեսի ջերմությունն է՝ \\(q=\\int T\\,ds\\)։ Ադիաբատ՝ ուղղաձիգ (\\(q=0\\)), իզոթերմ՝ հորիզոնական, իզոխոր և իզոբար՝ լոգարիթմական կորեր. իզոբարն ավելի հարթ է, քանի որ \\(c_p>c_\\upsilon\\)։',
f(st){
  const s = svg(st, 600, 250, 'T–s'), A = axes(s, {x:50, y:20, w:340, h:200, xr:[-450, 450], yr:[0, 2], xl:'s − s₁, Ջ/(կգ·Կ)', yl:'T/T₁'});
  const F = {v:{c:C.acc, f:x => Math.exp(x / CV)}, p:{c:C.heat, f:x => Math.exp(x / CP)}, T:{c:C.good, f:() => 1}};
  const area = S('path', {opacity:.22}, s);
  Object.values(F).forEach(o => o.p = S('path', {d:A.fn(o.f, -420, 420), fill:'none', stroke:o.c, 'stroke-width':2}, s));
  const sv = S('path', {d:`M${A.X(0)} ${A.Y(.4)}V${A.Y(1.9)}`, fill:'none', stroke:C.bad, 'stroke-width':2}, s);
  [['իզոխոր', C.acc, F.v.f(-420)], ['իզոբար', C.heat, F.p.f(-420)]].forEach(([n, c, y], i) => T(s, A.X(-420), A.Y(y) + (i ? -8 : 16), n, {fill:c, 'font-size':11}));
  T(s, A.X(-420), A.Y(1) - 6, 'իզոթերմ', {fill:C.good, 'font-size':11}); T(s, A.X(0) + 5, A.Y(1.9), 'ադիաբատ', {fill:C.bad, 'font-size':11});
  S('circle', {cx:A.X(0), cy:A.Y(1), r:4.5, fill:C.ink}, s);
  const tq = T(s, 430, 80, '', {'font-weight':700, 'font-size':14}), tf = T(s, 430, 104, '', {fill:C.muted});
  function draw(id){
    Object.entries(F).forEach(([k, o]) => o.p.setAttribute('stroke-width', k === id ? 4 : 2)); sv.setAttribute('stroke-width', id === 's' ? 4 : 2);
    if (id === 's'){ attrs(area, {d:''}); setT(tq, 'q = 0'); setT(tf, 'մակերես չկա (s = const)'); return; }
    const f = F[id].f, s2 = 300;
    attrs(area, {d:A.fn(f, 0, s2, 40) + `L${A.X(s2)} ${A.Y(0)}L${A.X(0)} ${A.Y(0)}Z`, fill:F[id].c});
    const T2 = f(s2) * 300;
    setT(tq, 'q = ' + kJ(id === 'T' ? 300 * s2 : (id === 'v' ? CV : CP) * (T2 - 300)) + ' կՋ/կգ');
    setT(tf, id === 'T' ? 'q = T(s₂ − s₁)' : id === 'v' ? 'q = c_{υ}(T₂ − T₁)' : 'q = c_{p}(T₂ − T₁)');
  }
  T(s, 430, 140, 'Δs = 300 Ջ/(կգ·Կ), T₁ = 300 Կ', {fill:C.muted, 'font-size':11});
  seg(ctl(st), [['v', 'իզոխոր'], ['p', 'իզոբար'], ['T', 'իզոթերմ'], ['s', 'ադիաբատ']], 'p', draw); draw('p');
}};

/* ---------- 6.1 continuity ---------- */
VIZ.continuity = {kind:'a', cap:'Ստացիոնար հոսքում ծախսը բոլոր հատույթներում նույնն է՝ \\(G=c\\rho F=\\text{const}\\)։ Անսեղմելի հեղուկում (\\(\\rho=\\text{const}\\)) \\(cF=\\text{const}\\). նեղ հատույթում արագությունը մեծ է։',
f(st){
  const s = svg(st, 600, 220, 'Անընդհատություն'), x0 = 30, x1 = 570, cy = 105;
  let rmin = .5;
  const half = x => { const u = (x - x0) / (x1 - x0); return 70 * (1 - (1 - rmin) * Math.pow(Math.sin(Math.PI * u), 2)); };
  const wall = S('path', {fill:'var(--sunk)', stroke:C.ink, 'stroke-width':2}, s);
  const P = [], r = window.VZ.rnd(5); for (let i = 0; i < 70; i++) P.push({x:x0 + r() * (x1 - x0), e:r() * 1.8 - .9, c:S('circle', {r:2.8, fill:C.acc}, s)});
  const sec1 = S('line', {stroke:C.heat, 'stroke-width':2}, s), sec2 = S('line', {stroke:C.heat, 'stroke-width':2}, s);
  T(s, x0 + 10, 26, '1', {'font-weight':700, fill:C.heat}); T(s, 300, 26, '2', {'font-weight':700, fill:C.heat, 'text-anchor':'middle'});
  const o = out(st), c = ctl(st);
  slider(c, 'F₂/F₁', .3, 1, .02, .5, v => fmt(v, 2), v => { rmin = v; });
  anim(st, dt => {
    const top = [], bot = []; for (let x = x0; x <= x1; x += 6){ top.push([x, cy - half(x)]); bot.unshift([x, cy + half(x)]); }
    attrs(wall, {d:pts(top.concat(bot)) + 'Z'});
    attrs(sec1, {x1:x0 + 12, x2:x0 + 12, y1:cy - half(x0 + 12), y2:cy + half(x0 + 12)}); attrs(sec2, {x1:300, x2:300, y1:cy - half(300), y2:cy + half(300)});
    for (const q of P){ const h = half(q.x); q.x += 60 * (70 / h) * dt; if (q.x > x1){ q.x = x0; } attrs(q.c, {cx:q.x, cy:cy + q.e * (half(q.x) - 4)}); }
    o.innerHTML = `F₁/F₂ = <b class="mono">${fmt(1 / rmin, 2)}</b> → c₂/c₁ = <b class="mono">${fmt(1 / rmin, 2)}</b> (ρ = const). G₁ = G₂՝ զանգվածը 1–2 ծավալում չի փոխվում։`;
  }, c);
}};

/* ---------- 6.3 energy equation for a flow ---------- */
VIZ.energyeq = {kind:'i', cap:'Էներգիայի հավասարումը հոսքի համար. \\(q_{\\text{արտ}}-\\ell_{\\text{արտ}}=c_p(T_2-T_1)+\\frac{c_2^2-c_1^2}{2}\\)։ Հաղորդված արտաքին էներգիան ծախսվում է <b>էնթալպիայի և կինետիկ էներգիայի</b> փոփոխման վրա (օդ, \\(T_1=300\\) Կ, \\(c_1=100\\) մ/վ)։',
f(st){
  const s = svg(st, 620, 270, 'Էներգիայի հավասարում'), T1 = 300, c1 = 100;
  S('rect', {x:150, y:60, width:320, height:110, rx:8, fill:'var(--sunk)', stroke:C.ink, 'stroke-width':2}, s);
  S('line', {x1:150, x2:150, y1:40, y2:190, stroke:C.heat, 'stroke-width':2, 'stroke-dasharray':'5 4'}, s); S('line', {x1:470, x2:470, y1:40, y2:190, stroke:C.heat, 'stroke-width':2, 'stroke-dasharray':'5 4'}, s);
  T(s, 150, 34, '1', {'text-anchor':'middle', 'font-weight':700}); T(s, 470, 34, '2', {'text-anchor':'middle', 'font-weight':700});
  const qa = S('g', {}, s), la = S('g', {}, s), qt = T(s, 260, 216, '', {'text-anchor':'middle', fill:C.heat, 'font-weight':600}), lt = T(s, 380, 216, '', {'text-anchor':'middle', fill:C.good, 'font-weight':600});
  const bars = [60, 560].map(x => ({i:S('rect', {x:x - 20, width:40, fill:C.warn}, s), k:S('rect', {x:x - 20, width:40, fill:C.acc}, s), t:T(s, x, 258, '', {'text-anchor':'middle', 'font-size':11})}));
  T(s, 310, 252, '■ i = c_{p}T   ■ c²/2', {'text-anchor':'middle', 'font-size':11, fill:C.muted});
  const P = []; for (let i = 0; i < 22; i++) P.push({x:150 + i * 14.5, y:75 + (i * 37) % 80, c:S('circle', {r:3, fill:C.acc}, s)});
  const o = out(st), c = ctl(st);
  let q = 0, l = -200, c2 = 150, T2 = T1;
  const sc = 150 / 900e3;
  function calc(){ T2 = T1 + ((q - l) * 1000 - (c2 * c2 - c1 * c1) / 2) / CP; }
  function draw(){
    calc();
    [[T1, c1], [T2, c2]].forEach(([Tk, cc], i) => { const hi = Math.max(0, CP * Tk) * sc, hk = cc * cc / 2 * sc, b = bars[i];
      attrs(b.i, {y:240 - hi, height:hi}); attrs(b.k, {y:240 - hi - hk, height:hk}); setT(b.t, 'T = ' + fmt(Tk, 0) + ' Կ'); });
    while (qa.firstChild) qa.removeChild(qa.firstChild); while (la.firstChild) la.removeChild(la.firstChild);
    if (q > 0) [230, 260, 290].forEach(x => arrow(qa, x, 196, x, 172, C.heat, 2.4, 8));
    if (l !== 0) l > 0 ? arrow(la, 380, 170, 380, 196, C.good, 3, 9) : arrow(la, 380, 196, 380, 170, C.good, 3, 9);
    setT(qt, q ? 'q_{արտ} = ' + q + ' կՋ/կգ' : ''); setT(lt, l ? (l > 0 ? 'ℓ_{արտ} = ' + l + ' (տուրբին)' : 'ℓ_{արտ} = ' + l + ' (կոմպրեսոր)') : '');
    o.innerHTML = T2 > 0 ? `T₂ = <b class="mono">${fmt(T2, 0)}</b> Կ. <span class="mono">${q} − (${l}) = ${kJ(CP * (T2 - T1))} + ${kJ((c2 * c2 - c1 * c1) / 2)}</span> կՋ/կգ` : '<span class="vz-bad">Այդքան կինետիկ էներգիայի համար էնթալպիան չի բավականացնում</span>';
  }
  slider(c, 'q<sub>արտ</sub>', 0, 600, 10, 0, v => v + ' կՋ/կգ', v => { q = v; draw(); });
  slider(c, 'ℓ<sub>արտ</sub>', -400, 400, 10, -200, v => v + ' կՋ/կգ', v => { l = v; draw(); });
  slider(c, 'c₂', 20, 800, 10, 150, v => v + ' մ/վ', v => { c2 = v; draw(); });
  draw();
  anim(st, dt => { for (const p of P){ p.x += (60 + 0.2 * c2) * dt; if (p.x > 466) p.x = 154; attrs(p.c, {cx:p.x, cy:p.y}); } });
}};

/* ---------- 6.4 stagnation parameters ---------- */
VIZ.stag = {kind:'a', cap:'Ադիաբատ արգելակում մինչև \\(c^*=0\\). \\(T^*=T+\\frac{c^2}{2c_p}\\), \\(\\frac{T^*}{T}=1+\\frac{k-1}{2}M^2\\)։ \\(c_pT+\\frac{c^2}{2}=\\text{const}\\), ուստի <b>արագության աճը հնարավոր է միայն ջերմաստիճանի նվազման հաշվին</b> (օդ, \\(T^*=300\\) Կ)։',
f(st){
  const s = svg(st, 620, 240, 'Արգելակման պարամետրեր'), Ts = 300, xw = 420;
  S('rect', {x:xw, y:30, width:24, height:150, rx:4, fill:C.ink}, s);
  T(s, xw - 6, 205, 'c* = 0, T*, p*', {'text-anchor':'end', 'font-weight':600}); T(s, 20, 205, 'c, T, p', {'font-weight':600});
  const P = []; for (let i = 0; i < 40; i++) P.push({x:20 + (i % 10) * 40, y:50 + Math.floor(i / 10) * 37, c:S('circle', {r:4}, s)});
  const bx = 480, hb = 170; T(s, bx + 25, 22, 'c_{p}T* = const', {'text-anchor':'middle', 'font-size':11, 'font-weight':600});
  const bT = S('rect', {x:bx, width:50, fill:C.heat}, s), bK = S('rect', {x:bx, y:30, width:50, fill:C.acc}, s);
  T(s, bx + 58, 50, 'c²/2', {fill:C.acc}); T(s, bx + 58, 190, 'c_{p}T', {fill:C.heat});
  const o = out(st), c = ctl(st);
  let M = 1;
  slider(c, 'M', 0, 3, .05, 1, v => fmt(v, 2), v => { M = v; });
  anim(st, dt => {
    const tr = 1 + (K - 1) / 2 * M * M, Tk = Ts / tr, cc = M * Math.sqrt(K * R * Tk), f = 1 / tr;
    attrs(bT, {y:30 + hb * (1 - f), height:hb * f}); attrs(bK, {height:hb * (1 - f)});
    for (const p of P){ const d = xw - 8 - p.x, sp = (8 + cc * .25) * clamp(d / 90, 0, 1); p.x += Math.max(sp, 6) * dt;
      if (p.x > xw - 8) p.x -= 400; const near = clamp(1 - d / 90, 0, 1);
      attrs(p.c, {cx:p.x, cy:p.y, fill:`color-mix(in srgb, var(--heat) ${Math.round(100 * lerp(clamp(1 - (1 - f) * 3, 0, 1), 1, near))}%, var(--accent))`}); }
    o.innerHTML = `T = <b class="mono">${fmt(Tk, 1)}</b> Կ, c = <b class="mono">${fmt(cc, 0)}</b> մ/վ · T*/T = <b class="mono">${fmt(tr, 3)}</b>, p*/p = <b class="mono">${fmt(Math.pow(tr, K / (K - 1)), 3)}</b>, ρ*/ρ = <b class="mono">${fmt(Math.pow(tr, 1 / (K - 1)), 3)}</b>${Math.abs(M - 1) < .01 ? ' <span class="vz-good">(M = 1՝ 1,2 և 1,893)</span>' : ''}`;
  }, c);
}};

/* ---------- 6.5–6.6 compressor and turbine ---------- */
VIZ.turbo = {kind:'i', cap: a => a === 'k'
  ? 'Կոմպրեսորի իդեալական (ադիաբատ) աշխատանքը \\(\\ell_{\\text{կ.ադ}}=c_pT_1^*\\left(\\pi_{\\text{կ}}^{*\\frac{k-1}{k}}-1\\right)\\). արտաքին աշխատանքը ծախսվում է լրիվ էնթալպիայի բարձրացման վրա, \\(N_{\\text{կ}}=G\\ell_{\\text{կ}}\\)։'
  : 'Տուրբինի իդեալական (ադիաբատ) աշխատանքը \\(\\ell_{\\text{տ.ադ}}=c_pT_1^*\\left(1-\\pi_{\\text{տ}}^{*-\\frac{k-1}{k}}\\right)\\). լիսեռի աշխատանքը ստացվում է լրիվ էնթալպիայի նվազման հաշվին, \\(N_{\\text{տ}}=G\\ell_{\\text{տ}}\\)։',
f(st, a){
  const kmode = a === 'k', s = svg(st, 620, 240, kmode ? 'Կոմպրեսոր' : 'Տուրբին'), m = (K - 1) / K;
  const sh = kmode ? 'M30 40 L170 80 L170 160 L30 200Z' : 'M30 80 L170 40 L170 200 L30 160Z';
  S('path', {d:sh, fill:'var(--sunk)', stroke:C.ink, 'stroke-width':2}, s);
  S('rect', {x:0, y:116, width:200, height:8, fill:C.muted}, s);
  T(s, 100, 20, kmode ? 'Կոմպրեսոր' : 'Տուրբին', {'text-anchor':'middle', 'font-weight':700});
  const blades = S('g', {}, s); for (let i = 0; i < 5; i++) S('line', {x1:50 + i * 27, x2:50 + i * 27, stroke:C.acc, 'stroke-width':4}, blades);
  const t1 = T(s, 30, 225, '', {'font-size':11}), t2 = T(s, 170, 225, '', {'font-size':11, 'text-anchor':'end'});
  const A = axes(s, {x:250, y:24, w:330, h:180, xr:[1, kmode ? 30 : 10], yr:[0, kmode ? 700 : 900], xl:kmode ? 'π_{կ}*' : 'π_{տ}*', yl:'ℓ_{ադ}, կՋ/կգ'});
  const cur = S('path', {fill:'none', stroke:kmode ? C.acc : C.heat, 'stroke-width':2.5}, s), dot = S('circle', {r:6, fill:C.ink}, s), dl = T(s, 0, 0, '', {'font-weight':600});
  const o = out(st), c = ctl(st);
  let pi = kmode ? 10 : 4, T1 = kmode ? 288 : 1200;
  const L = x => CP * T1 * (kmode ? Math.pow(x, m) - 1 : 1 - Math.pow(x, -m)) / 1000;
  function draw(){
    attrs(cur, {d:A.fn(L, 1, kmode ? 30 : 10)}); const l = L(pi); attrs(dot, {cx:A.X(pi), cy:A.Y(l)}); attrs(dl, {x:A.X(pi) + 8, y:A.Y(l) - 8}); setT(dl, fmt(l, 0) + ' կՋ/կգ');
    const T2 = kmode ? T1 * Math.pow(pi, m) : T1 * Math.pow(pi, -m);
    setT(t1, 'T₁* = ' + T1 + ' Կ'); setT(t2, 'T₂* = ' + fmt(T2, 0) + ' Կ');
    o.innerHTML = `ℓ = c<sub>p</sub>|T₂* − T₁*| = <b class="mono">${fmt(l, 1)}</b> կՋ/կգ · G = 1 կգ/վ-ի դեպքում N = Gℓ = <b class="mono">${fmt(l, 0)}</b> կՎտ`;
  }
  slider(c, kmode ? 'π<sub>կ</sub>*' : 'π<sub>տ</sub>*', 1, kmode ? 30 : 10, .1, pi, v => fmt(v, 1), v => { pi = v; draw(); });
  slider(c, 'T₁*', kmode ? 200 : 800, kmode ? 400 : 1600, 5, T1, v => v + ' Կ', v => { T1 = v; draw(); });
  draw();
  anim(st, (dt, t) => [...blades.children].forEach((b, i) => { const h = kmode ? 100 - i * 9 : 64 + i * 9, y = 120, w = Math.cos(t * 6 + i) * h / 2; attrs(b, {y1:y - Math.abs(w), y2:y + Math.abs(w)}); }));
}};

/* ---------- 6.7 engine: where i* changes ---------- */
VIZ.engine = {kind:'a', cap:'Գազատուրբինային շարժիչի տարրերը և լրիվ էնթալպիան \\(i^*=c_pT^*\\) դրանցում. մուտքային սարքում և փողրակում \\(i^*=\\text{const}\\), կոմպրեսորում և այրման խցիկում \\(i^*\\)-ն աճում է, տուրբինում՝ նվազում (տուրբինը պտտում է կոմպրեսորը՝ \\(N_{\\text{տ}}\\approx N_{\\text{կ}}\\))։ Կորերը որակական են։',
f(st){
  const s = svg(st, 640, 290, 'Շարժիչ');
  const Z = [
    {n:'Մուտքային սարք', x:20, w:90, a:1, b:1, e:'q = 0, ℓ = 0 → i₁* = i₂*', sh:'M20 50 L110 40 L110 150 L20 140Z'},
    {n:'Կոմպրեսոր', x:110, w:130, a:1, b:1.8, e:'ℓ_{կ} = i₂* − i₁* = c_{p}(T₂* − T₁*)', sh:'M110 40 L240 70 L240 120 L110 150Z'},
    {n:'Այրման խցիկ', x:240, w:120, a:1.8, b:4.5, e:'q_{արտ} = i₂* − i₁* = c_{p}(T₂* − T₁*), p ≈ const', sh:'M240 70 L360 70 L360 120 L240 120Z'},
    {n:'Տուրբին', x:360, w:110, a:4.5, b:3.7, e:'ℓ_{տ} = i₁* − i₂* = c_{p}(T₁* − T₂*)', sh:'M360 70 L470 50 L470 140 L360 120Z'},
    {n:'Ելքային փողրակ', x:470, w:120, a:3.7, b:3.7, e:'i₁* = i₂*, հոսքն արագանում է', sh:'M470 50 L590 75 L590 115 L470 140Z'}];
  const zs = Z.map(z => S('path', {d:z.sh, fill:'var(--sunk)', stroke:C.ink, 'stroke-width':1.5}, s));
  S('rect', {x:130, y:92, width:330, height:6, fill:C.muted}, s); T(s, 300, 88, 'լիսեռ', {'text-anchor':'middle', fill:C.muted, 'font-size':10});
  const P = []; for (let i = 0; i < 40; i++) P.push({x:20 + (i * 571 / 40), e:((i * 7) % 10) / 10 - .5, c:S('circle', {r:2.6}, s)});
  const halfAt = x => x < 110 ? lerp(45, 55, (x - 20) / 90) : x < 240 ? lerp(55, 25, (x - 110) / 130) : x < 360 ? 25 : x < 470 ? lerp(25, 45, (x - 360) / 110) : lerp(45, 20, (x - 470) / 120);
  const A = axes(s, {x:20, y:180, w:570, h:70, xr:[20, 590], yr:[0, 5], yl:'i* = c_{p}T*'});
  const step = []; Z.forEach(z => { for (let i = 0; i <= 10; i++) step.push([A.X(z.x + z.w * i / 10), A.Y(lerp(z.a, z.b, i / 10))]); });
  S('path', {d:pts(step), fill:'none', stroke:C.heat, 'stroke-width':2.5}, s);
  const nm = T(s, 320, 20, '', {'text-anchor':'middle', 'font-weight':700}), eq = T(s, 320, 172, '', {'text-anchor':'middle'});
  const hl = S('rect', {y:180, height:70, fill:C.acc, opacity:.1}, s);
  anim(st, (dt, t) => {
    const k = Math.floor(t / 2.6) % 5, z = Z[k];
    zs.forEach((p, i) => { p.style.fill = i === k ? 'var(--accent-soft)' : 'var(--sunk)'; });
    setT(nm, z.n); setT(eq, z.e); attrs(hl, {x:A.X(z.x), width:A.X(z.x + z.w) - A.X(z.x)});
    for (const p of P){ const h = halfAt(p.x); p.x += (10 + 40000 / (h * h)) * dt; if (p.x > 588) p.x = 22;
      const zi = Z.find(q => p.x >= q.x && p.x < q.x + q.w) || Z[4], tv = lerp(zi.a, zi.b, (p.x - zi.x) / zi.w);
      attrs(p.c, {cx:p.x, cy:95 + p.e * 2 * (halfAt(p.x) - 4), fill:`color-mix(in srgb, var(--heat) ${Math.round(clamp((tv - 1) / 3.5, 0, 1) * 100)}%, var(--accent))`}); }
  }, ctl(st));
}};

/* ---------- 6.8 nozzle outflow and duct shapes ---------- */
VIZ.nozzle = {kind:'i', cap:'Ելքային փողրակում արտահոսքի արագությունը \\(c_2=\\sqrt{2\\frac{k}{k-1}RT_1^*\\left[1-\\left(\\frac{p_2}{p_1^*}\\right)^{\\frac{k-1}{k}}\\right]}\\)։ \\(p_2\\to0\\) դեպքում \\(c_2\\to c_{\\text{սահմ}}\\)։ Ենթաձայնային հոսքում արագացնող փողրակը նեղացող է, արգելակող դիֆուզորը՝ լայնացող (գերձայնայինում՝ հակառակը)։',
f(st){
  const s = svg(st, 620, 250, 'Փողրակ'), A = axes(s, {x:50, y:24, w:300, h:190, xr:[0, 1], yr:[0, 1800], xl:'p₂/p₁*', yl:'c₂, մ/վ'});
  [.5, 1].forEach(v => T(s, A.X(v), A.Y(0) + 14, fmt(v, 1), {'text-anchor':'middle', fill:C.muted, 'font-size':10}));
  [500, 1000, 1500].forEach(v => T(s, A.X(0) - 5, A.Y(v) + 4, String(v), {'text-anchor':'end', fill:C.muted, 'font-size':10}));
  const cur = S('path', {fill:'none', stroke:C.acc, 'stroke-width':2.5}, s), lim = S('line', {stroke:C.bad, 'stroke-dasharray':'5 4'}, s), lt = T(s, 0, 0, '', {fill:C.bad, 'font-size':11});
  const dot = S('circle', {r:6, fill:C.ink}, s), dl = T(s, 0, 0, '', {'font-weight':600});
  // duct shapes
  const g = S('g', {}, s), P = []; const sub = {v:true};
  const duct = (x, y, w, conv) => S('path', {d:conv ? `M${x} ${y - 30}L${x + w} ${y - 14}M${x} ${y + 30}L${x + w} ${y + 14}` : `M${x} ${y - 14}L${x + w} ${y - 30}M${x} ${y + 14}L${x + w} ${y + 30}`, stroke:C.ink, 'stroke-width':2.5, fill:'none'}, g);
  const t1 = T(s, 500, 50, '', {'text-anchor':'middle', 'font-weight':600}), t2 = T(s, 500, 150, '', {'text-anchor':'middle', 'font-weight':600});
  let T1 = 900, pr = .3;
  function shapes(){
    while (g.firstChild) g.removeChild(g.firstChild);
    duct(430, 95, 140, sub.v); duct(430, 195, 140, !sub.v);
    setT(t1, 'Փողրակ՝ ' + (sub.v ? 'նեղացող' : 'լայնացող') + ' (dc > 0)'); setT(t2, 'Դիֆուզոր՝ ' + (sub.v ? 'լայնացող' : 'նեղացող') + ' (dc < 0)');
  }
  for (let i = 0; i < 16; i++) P.push({u:(i / 16), r:(i % 4) / 3 - .5, k:i % 2, c:S('circle', {r:3, fill:C.acc}, s)});
  const f = x => Math.sqrt(2 * K / (K - 1) * R * T1 * (1 - Math.pow(x, (K - 1) / K)));
  function draw(){
    attrs(cur, {d:A.fn(f, 0, 1, 120)}); const cl = Math.sqrt(2 * K / (K - 1) * R * T1);
    attrs(lim, {x1:A.X(0), x2:A.X(1), y1:A.Y(cl), y2:A.Y(cl)}); attrs(lt, {x:A.X(.98), y:A.Y(cl) - 6, 'text-anchor':'end'}); setT(lt, 'c_{սահմ} = ' + fmt(cl, 0) + ' մ/վ');
    attrs(dot, {cx:A.X(pr), cy:A.Y(f(pr))}); attrs(dl, {x:A.X(pr) + 8, y:A.Y(f(pr)) - 8}); setT(dl, fmt(f(pr), 0) + ' մ/վ');
  }
  const c = ctl(st);
  slider(c, 'T₁*', 300, 1500, 10, T1, v => v + ' Կ', v => { T1 = v; draw(); });
  slider(c, 'p₂/p₁*', 0, 1, .01, pr, v => fmt(v, 2), v => { pr = v; draw(); });
  seg(c, [[true, 'ենթաձայնային'], [false, 'գերձայնային']], true, v => { sub.v = v; shapes(); });
  shapes(); draw();
  anim(st, dt => P.forEach(p => {
    const y0 = p.k ? 195 : 95, acc = p.k === 0;                 // top duct accelerates, bottom decelerates
    p.u += dt * (acc ? .25 + .6 * p.u : .85 - .6 * p.u) * .6; if (p.u > 1) p.u = 0;
    const narrowEnd = (p.k === 0) === sub.v, hw = narrowEnd ? lerp(26, 10, p.u) : lerp(10, 26, p.u);
    attrs(p.c, {cx:432 + p.u * 136, cy:y0 + p.r * 2 * hw, fill:acc ? C.heat : C.acc}); }));
}};

/* ---------- 6.9 Bernoulli: available work ∫υdp ---------- */
VIZ.bern = {kind:'i', cap:'Տնօրինելի աշխատանքը \\(\\int_1^2\\upsilon\\,dp\\)՝ \\(p\\text{–}\\upsilon\\) դիագրամում <b>օրդինատների առանցքի և կորի միջև</b> մակերեսը (12ba), ի տարբերություն դեֆորմացիայի աշխատանքի \\(\\int p\\,d\\upsilon\\)-ի (կորի տակ մակերես)։ Պոլիտրոպի համար \\(\\int_1^2\\upsilon\\,dp=\\frac{n}{n-1}(p_2\\upsilon_2-p_1\\upsilon_1)\\)։',
f(st){
  const s = svg(st, 600, 250, 'Բեռնուլի'), A = axes(s, {x:50, y:20, w:330, h:200, xr:[0, 1.6], yr:[0, 3], xl:'υ', yl:'p'});
  const ar = S('path', {opacity:.25}, s), cur = S('path', {fill:'none', stroke:C.ink, 'stroke-width':2.5}, s), lb = S('g', {}, s);
  const t1 = T(s, 400, 70, '', {'font-weight':700, 'font-size':14}), t2 = T(s, 400, 96, '', {fill:C.muted}), t3 = T(s, 400, 120, '', {fill:C.muted});
  let n = 1.3, mode = 'vdp'; const p1 = 1, p2 = 2.6;
  function draw(){
    const v2 = Math.pow(p1 / p2, 1 / n), vp = p => Math.pow(p1 / p, 1 / n);
    attrs(cur, {d:A.fn(v => p1 * Math.pow(1 / v, n), v2, 1)});
    if (mode === 'vdp'){ const r = []; for (let i = 0; i <= 40; i++){ const p = lerp(p1, p2, i / 40); r.push([A.X(vp(p)), A.Y(p)]); }
      attrs(ar, {d:pts([[A.X(0), A.Y(p1)], ...r, [A.X(0), A.Y(p2)]]) + 'Z', fill:C.acc}); }
    else attrs(ar, {d:A.fn(v => p1 * Math.pow(1 / v, n), v2, 1) + `L${A.X(1)} ${A.Y(0)}L${A.X(v2)} ${A.Y(0)}Z`, fill:C.heat});
    while (lb.firstChild) lb.removeChild(lb.firstChild);
    [[1, p1, '1', 6, 14], [v2, p2, '2', 6, -4], [0, p2, 'b', -12, 4], [0, p1, 'a', -12, 4]].forEach(([v, p, t, dx, dy]) => { S('circle', {cx:A.X(v), cy:A.Y(p), r:3.5, fill:C.ink}, lb); T(lb, A.X(v) + dx, A.Y(p) + dy, t, {'font-weight':700}); });
    const vdp = n / (n - 1) * (p2 * v2 - p1 * 1), pdv = (p1 * 1 - p2 * v2) / (n - 1);
    setT(t1, mode === 'vdp' ? '∫υ dp = ' + fmt(vdp, 3) : '∫p dυ = ' + fmt(pdv, 3)); t1.style.fill = mode === 'vdp' ? C.acc : C.heat;
    setT(t2, '1 → 2՝ սեղմում, p₂/p₁ = 2,6'); setT(t3, 'միավորները՝ p₁υ₁');
  }
  const c = ctl(st);
  seg(c, [['vdp', '∫υ dp (12ba)'], ['pdv', '∫p dυ']], mode, m => { mode = m; draw(); });
  slider(c, 'n', 1.05, 1.6, .01, n, v => fmt(v, 2), v => { n = v; draw(); });
  draw();
}};

/* ---------- 6.10 speed of sound ---------- */
VIZ.sound = {kind:'a', cap:'Ձայնը՝ թույլ սեղմման և նոսրացման ալիքներ։ \\(a=\\sqrt{kRT}\\approx20{,}05\\sqrt T\\)՝ կախված է միայն գազի տեսակից և ջերմաստիճանից. <b>ճնշումից կախված չէ</b>՝ փոխեք \\(p\\)-ն և համոզվեք, որ ալիքի արագությունը նույնն է։',
f(st){
  const s = svg(st, 600, 200, 'Ձայնի արագություն'), x0 = 20, x1 = 580, cy = 90;
  S('rect', {x:x0, y:40, width:x1 - x0, height:100, fill:'var(--sunk)', stroke:C.line}, s);
  const G = S('g', {}, s), front = S('line', {y1:36, y2:144, stroke:C.heat, 'stroke-width':2, 'stroke-dasharray':'4 3'}, s);
  const lab = T(s, 300, 176, '', {'text-anchor':'middle', 'font-weight':700, 'font-size':14});
  let Tk = 288, p = 1, cols = [];
  function build(){ while (G.firstChild) G.removeChild(G.firstChild); cols = []; const n = Math.round(36 * p);
    for (let i = 0; i < n; i++){ const x = x0 + 8 + i * (x1 - x0 - 16) / (n - 1); cols.push({x, d:[0, 1, 2, 3].map(j => S('circle', {cy:52 + j * 25 + (i % 2) * 12, r:3, fill:C.acc}, G))}); } }
  const c = ctl(st);
  slider(c, 'T', 150, 600, 1, 288, v => fmt(v, 0) + ' Կ', v => { Tk = v; });
  slider(c, 'p', .5, 2, .1, 1, v => fmt(v, 1) + ' բար', v => { p = v; build(); });
  btn(c, '288 Կ', () => { Tk = 288; c.querySelector('input').value = 288; c.querySelector('output').textContent = '288 Կ'; });
  btn(c, '216,65 Կ (11 կմ)', () => { Tk = 216.65; c.querySelector('input').value = 216.65; c.querySelector('output').textContent = '216,65 Կ'; });
  build();
  anim(st, (dt, t) => {
    const a = Math.sqrt(K * R * Tk), v = a * .45, L = x1 - x0, xf = x0 + ((t * v) % (L + 120)) - 60;
    attrs(front, {x1:xf, x2:xf});
    cols.forEach(cl => { const d = cl.x - xf, u = Math.exp(-d * d / 1600) * 14 * Math.sign(d); cl.d.forEach(e => e.setAttribute('cx', cl.x + u)); });
    setT(lab, 'a = √(kRT) = ' + fmt(a, 0) + ' մ/վ');
  }, c);
}};

/* ---------- 6.11 Mach number and reduced velocity ---------- */
VIZ.mach = {kind:'i', cap:'\\(M=c/a\\)՝ \\(M<1\\) ենթաձայնային, \\(M>1\\) գերձայնային, \\(M>5\\) հիպերձայնային հոսք։ Բերված արագությունը \\(\\lambda=c/a_{\\text{կր}}\\). \\(M=1\\Rightarrow\\lambda=1\\), \\(M\\to\\infty\\Rightarrow\\lambda\\to\\sqrt{\\frac{k+1}{k-1}}\\) (օդի համար 2,45)։',
f(st){
  const s = svg(st, 620, 270, 'Մախի թիվ'), Mx = 7;
  const bar = [[0, 1, 'ենթաձայնային', C.acc], [1, 5, 'գերձայնային', C.warn], [5, 7, 'հիպերձայնային', C.bad]], bx = x => 50 + x / Mx * 520;
  bar.forEach(([a, b, n, c]) => { S('rect', {x:bx(a), y:18, width:bx(b) - bx(a), height:22, fill:c, opacity:.25}, s); T(s, (bx(a) + bx(b)) / 2, 33, n, {'text-anchor':'middle', 'font-size':11, 'font-weight':600}); });
  const A = axes(s, {x:50, y:70, w:520, h:160, xr:[0, Mx], yr:[0, 3.2], xl:'M', yl:'λ'});
  for (let i = 1; i <= 7; i++) T(s, A.X(i), A.Y(0) + 14, String(i), {'text-anchor':'middle', fill:C.muted, 'font-size':10});
  [1, 2, 3].forEach(v => T(s, A.X(0) - 5, A.Y(v) + 4, String(v), {'text-anchor':'end', fill:C.muted, 'font-size':10}));
  const lam = (M, k) => Math.sqrt((k + 1) / 2 * M * M / (1 + (k - 1) / 2 * M * M));
  [[1.4, C.acc], [1.25, C.heat]].forEach(([k, c]) => { const L = Math.sqrt((k + 1) / (k - 1));
    S('path', {d:A.fn(M => lam(M, k), 0, Mx, 120), fill:'none', stroke:c, 'stroke-width':2.5}, s);
    S('line', {x1:A.X(0), x2:A.X(Mx), y1:A.Y(L), y2:A.Y(L), stroke:c, 'stroke-dasharray':'4 4'}, s);
    T(s, A.X(Mx) - 4, A.Y(L) - 5, 'k = ' + fmt(k, 2) + ', λ_{սահմ} = ' + fmt(L, 2), {'text-anchor':'end', fill:c, 'font-size':11}); });
  const mk = S('line', {y1:14, y2:A.Y(0), stroke:C.ink, 'stroke-width':1.5}, s), o = out(st);
  function draw(M){ attrs(mk, {x1:bx(M), x2:bx(M)});
    o.innerHTML = `M = <b class="mono">${fmt(M, 2)}</b> → λ = <b class="mono">${fmt(lam(M, 1.4), 3)}</b> (k = 1,4), <b class="mono">${fmt(lam(M, 1.25), 3)}</b> (k = 1,25) · ${M < 1 ? 'ենթաձայնային' : M > 5 ? 'հիպերձայնային' : M > 1 ? 'գերձայնային' : 'կրիտիկական (c = a)'}`; }
  slider(ctl(st), 'M', 0, Mx, .05, 1, v => fmt(v, 2), draw); draw(1);
}};

/* ---------- 6.12 gas-dynamic functions ---------- */
VIZ.gdf = {kind:'i', cap:'Գազադինամիկական ֆունկցիաներ. \\(\\tau(\\lambda)=T/T^*\\), \\(\\pi(\\lambda)=p/p^*\\), \\(\\varepsilon(\\lambda)=\\rho/\\rho^*\\), \\(q(\\lambda)\\)՝ ծախսի ֆունկցիա։ \\(q\\)-ն առավելագույնն է (\\(=1\\)) \\(\\lambda=1\\)-ում. յուրաքանչյուր \\(q<1\\)-ի համապատասխանում են երկու \\(\\lambda\\)՝ ենթաձայնային և գերձայնային։',
f(st){
  const s = svg(st, 620, 260, 'Գազադինամիկական ֆունկցիաներ');
  const A = axes(s, {x:50, y:20, w:400, h:210, xr:[0, 3.05], yr:[0, 1.1], xl:'λ', yl:''});
  [1, 2, 3].forEach(v => T(s, A.X(v), A.Y(0) + 14, String(v), {'text-anchor':'middle', fill:C.muted, 'font-size':10}));
  [.5, 1].forEach(v => T(s, A.X(0) - 5, A.Y(v) + 4, fmt(v, 1), {'text-anchor':'end', fill:C.muted, 'font-size':10}));
  const F = [['τ', C.heat], ['π', C.acc], ['ε', C.good], ['q', C.ink]].map(([n, c]) => ({n, c, p:S('path', {fill:'none', stroke:c, 'stroke-width':n === 'q' ? 3 : 2}, s), d:S('circle', {r:4, fill:c}, s)}));
  F.forEach((f, i) => { S('rect', {x:470, y:28 + i * 22, width:14, height:4, fill:f.c}, s); T(s, 490, 34 + i * 22, f.n + '(λ)', {fill:f.c, 'font-weight':600}); });
  const mk = S('line', {stroke:C.muted, 'stroke-dasharray':'3 3'}, s), mk2 = S('line', {stroke:C.muted, 'stroke-dasharray':'3 3'}, s), q2 = S('circle', {r:5, fill:'none', stroke:C.ink, 'stroke-width':2}, s);
  const lim = S('line', {stroke:C.bad, 'stroke-dasharray':'4 4'}, s), o = out(st);
  let k = 1.4, lam = .6, sl;
  const fn = (l) => { const t = 1 - (k - 1) / (k + 1) * l * l; if (t <= 0) return [0, 0, 0, 0]; const e = Math.pow(t, 1 / (k - 1)); return [t, Math.pow(t, k / (k - 1)), e, l * Math.pow((k + 1) / 2, 1 / (k - 1)) * e]; };
  function draw(){
    const L = Math.sqrt((k + 1) / (k - 1)); attrs(lim, {x1:A.X(L), x2:A.X(L), y1:A.Y(0), y2:A.Y(1.08)});
    F.forEach((f, i) => attrs(f.p, {d:A.fn(l => fn(l)[i], 0, Math.min(L, 3.05), 160)}));
    lam = Math.min(lam, L - .001); const v = fn(lam);
    F.forEach((f, i) => attrs(f.d, {cx:A.X(lam), cy:A.Y(v[i])}));
    attrs(mk, {x1:A.X(lam), x2:A.X(lam), y1:A.Y(0), y2:A.Y(1.08)});
    // the other λ with the same q
    let other = null; if (v[3] < .999 && v[3] > .001){ let a = lam < 1 ? 1 : 0, b = lam < 1 ? L : 1; for (let i = 0; i < 60; i++){ const m = (a + b) / 2, qm = fn(m)[3]; ((qm > v[3]) === (lam < 1)) ? a = m : b = m; } other = (a + b) / 2; }
    if (other != null){ attrs(q2, {cx:A.X(other), cy:A.Y(v[3]), opacity:1}); attrs(mk2, {x1:A.X(lam), x2:A.X(other), y1:A.Y(v[3]), y2:A.Y(v[3]), opacity:1}); }
    else { q2.setAttribute('opacity', 0); mk2.setAttribute('opacity', 0); }
    const M2 = 2 / (k + 1) * lam * lam / (1 - (k - 1) / (k + 1) * lam * lam), y = v[1] > 1e-9 ? v[3] / v[1] : Infinity;
    o.innerHTML = `λ = <b class="mono">${fmt(lam, 2)}</b> (M = <span class="mono">${fmt(Math.sqrt(M2), 2)}</span>) · τ = <span class="mono">${fmt(v[0], 4)}</span>, π = <span class="mono">${fmt(v[1], 4)}</span>, ε = <span class="mono">${fmt(v[2], 4)}</span>, q = <b class="mono">${fmt(v[3], 4)}</b>, y = q/π = <span class="mono">${isFinite(y) ? fmt(y, 3) : '∞'}</span>`
      + (other != null ? `<br><span class="vz-mut">Նույն q-ն ունի նաև λ = ${fmt(other, 3)} (${other < 1 ? 'ենթաձայնային' : 'գերձայնային'})</span>` : '');
  }
  const c = ctl(st);
  seg(c, [[1.4, 'k = 1,4'], [4 / 3, 'k = 1,33'], [1.25, 'k = 1,25']], 1.4, v => { k = v; sl.el.max = fmt(Math.min(3, Math.sqrt((k + 1) / (k - 1))) - .01, 2).replace(',', '.'); draw(); });
  sl = slider(c, 'λ', 0, 2.44, .01, .6, v => fmt(v, 2), v => { lam = v; draw(); });
  draw();
}};

/* which visuals go under which lecture section ("lectureId:sectionIndex") */
Object.assign(window.VIZMAP, {
  '1:1':['molecules', 'pgauge'], '1:2':['pv3'], '1:3':['heatwork'],
  '2:0':['gaslaws'], '2:1':['gasR'], '2:2':['realgas'], '2:3':['dalton'], '2:4':['cpcv', 'dof'],
  '3:0':['firstlaw'], '3:1':['upath'], '3:2':['pdv'], '3:3':['cmean'], '3:4':['enthalpy'],
  '4:0':['procfam'], '4:1':['proc:v'], '4:2':['proc:p'], '4:3':['proc:T'], '4:4':['proc:s', 'adiso'], '4:5':['poly'], '4:6':['ts4'],
  '6:0':['continuity'], '6:2':['energyeq'], '6:3':['stag'], '6:4':['turbo:k'], '6:5':['turbo:t'], '6:6':['engine'], '6:7':['nozzle'],
  '6:8':['bern'], '6:9':['sound'], '6:10':['mach'], '6:11':['gdf']});
})();
