/* Gas-dynamics lecture visuals. Air constants as in the lectures: R = 287 J/(kg·K), k = 1,4. */
(function(){
'use strict';
const {C, S, H, T, setT, attrs, svg, pts, arrow, axes, clamp, lerp, fmt, ctl, slider, seg, btn, out, anim} = window.VZ;
const VIZ = window.VIZ;
const R = 287, K = 1.4, CV = R / (K - 1), CP = K * R / (K - 1);
const kJ = v => fmt(v / 1000, Math.abs(v) < 10000 ? 1 : 0);

/* cylinder with piston: x, y = top-left of the barrel, w, h; returns update(level 0..1, tempColor) */
function cylinder(p, x, y, w, h, o){
  o = o || {};
  const g = S('g', {}, p);
  const gas = S('rect', {x:x + 3, y:y, width:w - 6, height:h, fill:C.accS}, g);
  S('path', {d:`M${x} ${y - 6} V${y + h} H${x + w} V${y - 6}`, fill:'none', stroke:C.ink, 'stroke-width':3, 'stroke-linejoin':'round'}, g);
  if (o.insulated) S('path', {d:`M${x - 6} ${y - 6} V${y + h + 6} H${x + w + 6} V${y - 6}`, fill:'none', stroke:C.muted, 'stroke-width':5, 'stroke-dasharray':'2 3'}, g);
  const piston = S('rect', {x:x + 3, width:w - 6, height:10, rx:2, fill:C.muted}, g);
  const rod = S('rect', {x:x + w / 2 - 3, width:6, fill:C.muted}, g);
  const wt = o.weight ? S('rect', {x:x + w / 2 - 22, width:44, height:18, rx:3, fill:C.ink}, g) : null;
  return function(level, fill){
    const py = y + h - level * h;
    attrs(gas, {y:py + 10, height:Math.max(0, y + h - py - 10)});
    if (fill) gas.style.fill = fill;
    attrs(piston, {y:py});
    attrs(rod, {y:py - 34, height:34});
    if (wt) attrs(wt, {y:py - 52});
    return py;
  };
}
// gas tint from temperature ratio: cool = accent-soft, hot = heat-soft
const tint = r => r > 1.04 ? C.heatS : r < .96 ? C.accS : 'var(--sunk)';
function flames(p, x, y, w, on){
  const g = S('g', {}, p);
  for (let i = 0; i < 3; i++){ const cx = x + w * (i + 1) / 4;
    S('path', {d:`M${cx - 6} ${y + 16} Q${cx - 7} ${y + 4} ${cx} ${y - 4} Q${cx + 7} ${y + 4} ${cx + 6} ${y + 16}Z`, fill:C.heat, opacity:.85}, g); }
  g.style.display = on ? '' : 'none'; return g;
}

/* ---------- 1.2 parameters: molecules hitting the walls ---------- */
VIZ.molecules = {kind:'a', cap:'Ճնշումը՝ մոլեկուլների <b>հարվածների միջին արդյունքն</b> է անոթի պատերին, ջերմաստիճանը՝ նրանց համընթաց շարժման միջին կինետիկ էներգիայի չափը։ Փոխեք \\(T\\)-ն և ծավալը. \\(p=\\frac23 n\\frac{m\\bar w^2}{2}\\)՝ \\(n\\)-ը միավոր ծավալում մոլեկուլների թիվն է։',
f(st){
  const W = 560, Hh = 230, s = svg(st, W, Hh, 'Մոլեկուլներ անոթում'), x0 = 20, y0 = 30, bh = 170, N = 34;
  let v = 1, Tk = 300, hits = 0, rate = 0, acc = 0;
  const box = S('rect', {x:x0, y:y0, height:bh, fill:'var(--sunk)', stroke:C.ink, 'stroke-width':2.5}, s);
  const pist = S('rect', {y:y0 - 4, width:12, height:bh + 8, rx:2, fill:C.muted}, s);
  const flash = S('rect', {y:y0, width:4, height:bh, fill:C.heat, opacity:0}, s);
  const rnd = window.VZ.rnd(7), M = [];
  for (let i = 0; i < N; i++){ const a = rnd() * 6.283, sp = .6 + rnd() * .8;
    M.push({x:rnd(), y:rnd(), vx:Math.cos(a) * sp, vy:Math.sin(a) * sp, c:S('circle', {r:4.2, fill:C.acc}, s)}); }
  // gauge
  const gx = 470; S('rect', {x:gx, y:y0, width:26, height:bh, rx:4, fill:'var(--sunk)', stroke:C.line}, s);
  const gb = S('rect', {x:gx + 3, width:20, rx:3, fill:C.heat}, s);
  T(s, gx + 13, y0 - 10, 'p', {'text-anchor':'middle', 'font-weight':600});
  const lab = T(s, x0, 18, '', {fill:C.muted});
  const c = ctl(st);
  slider(c, 'T, Կ', 100, 900, 10, 300, v => v + ' Կ', x => { Tk = x; });
  slider(c, 'Ծավալ', .5, 1.5, .05, 1, x => '×' + fmt(x, 2), x => { v = x; });
  const o = out(st);
  const A = anim(st, (dt) => {
    const bw = 280 * v, sp = 170 * Math.sqrt(Tk / 300);
    attrs(box, {width:bw}); attrs(pist, {x:x0 + bw}); attrs(flash, {x:x0 + bw - 4});
    for (const m of M){
      m.x += m.vx * sp * dt / bw; m.y += m.vy * sp * dt / bh;
      if (m.x > 1){ m.x = 2 - m.x; m.vx = -Math.abs(m.vx); hits++; }
      if (m.x < 0){ m.x = -m.x; m.vx = Math.abs(m.vx); }
      if (m.y > 1){ m.y = 2 - m.y; m.vy = -Math.abs(m.vy); }
      if (m.y < 0){ m.y = -m.y; m.vy = Math.abs(m.vy); }
      attrs(m.c, {cx:x0 + 5 + m.x * (bw - 10), cy:y0 + 5 + m.y * (bh - 10)});
    }
    acc += dt;
    if (acc > .25){ rate = lerp(rate, hits / acc, rate ? .35 : 1); hits = 0; acc = 0; }
    flash.setAttribute('opacity', clamp(rate / 160, 0, .6));
    const pr = (Tk / 300) / v;
    attrs(gb, {height:clamp(pr / 6, 0, 1) * (bh - 6), y:y0 + bh - 3 - clamp(pr / 6, 0, 1) * (bh - 6)});
    setT(lab, 'Հարվածներ մխոցին՝ ≈ ' + Math.round(rate) + ' վ^{-1}');
    o.innerHTML = `<i>n</i> ∝ 1/ծավալ = <b class="mono">${fmt(1 / v, 2)}</b> · միջին կինետիկ էներգիա ∝ <i>T</i> = <b class="mono">${fmt(Tk / 300, 2)}</b> → <b>p/p<sub>0</sub> = <span class="mono">${fmt(pr, 2)}</span></b> <span class="vz-mut">(սկզբնական վիճակ՝ 300 Կ, ծավալ ×1)</span>`;
  }, c);
}};

/* ---------- 1.2 absolute, gauge and vacuum pressure ---------- */
VIZ.pgauge = {kind:'i', cap:'Վիճակի պարամետր է միայն <b>բացարձակ</b> ճնշումը. \\(p_{\\text{բաց}}=p_{\\text{մթն}}+p_{\\text{ավել}}\\) (մանոմետր) կամ \\(p_{\\text{բաց}}=p_{\\text{մթն}}-p_{\\text{վակ}}\\) (վակուումաչափ)։',
f(st){
  const s = svg(st, 560, 210, 'Ճնշման սանդղակ'), Y = v => 190 - v / 3 * 165, x = 150;
  arrow(s, x - 30, Y(0), x - 30, 12, C.muted, 1.2, 6);
  for (let v = 0; v <= 3; v += .5){ S('line', {x1:x - 34, x2:x - 26, y1:Y(v), y2:Y(v), stroke:C.muted}, s); T(s, x - 40, Y(v) + 4, fmt(v, 1), {'text-anchor':'end', fill:C.muted, 'font-size':11}); }
  T(s, x - 40, 14, 'բար', {'text-anchor':'end', fill:C.muted, 'font-size':11});
  T(s, x - 22, Y(0) + 15, '0՝ բացարձակ վակուում', {fill:C.muted, 'font-size':11});
  const col = S('rect', {x, width:60, fill:C.accS, stroke:C.acc}, s);
  S('line', {x1:x - 26, x2:520, y1:Y(1), y2:Y(1), stroke:C.ink, 'stroke-dasharray':'5 4'}, s);
  T(s, 520, Y(1) - 6, 'p_{մթն} ≈ 1 բար = 10^{5} Պա', {'text-anchor':'end'});
  const br = S('path', {fill:'none', 'stroke-width':2}, s), bl = T(s, x + 96, 0, '', {'font-weight':600});
  const pl = T(s, x + 30, 0, '', {'text-anchor':'middle', 'font-weight':600});
  const o = out(st);
  function upd(p){
    attrs(col, {y:Y(p), height:Y(0) - Y(p)});
    attrs(pl, {y:Y(p) - 6}); setT(pl, 'p_{բաց} = ' + fmt(p, 2));
    const a = Y(1), b = Y(p), over = p >= 1, cc = over ? C.heat : C.acc;
    attrs(br, {d:`M${x + 70} ${a} H${x + 82} V${b} H${x + 70}`, stroke:cc});
    attrs(bl, {y:(a + b) / 2 + 4, fill:cc}); setT(bl, over ? 'p_{ավել} = ' + fmt(p - 1, 2) + ' բար (մանոմետր)' : 'p_{վակ} = ' + fmt(1 - p, 2) + ' բար (վակուումաչափ)');
    o.innerHTML = over ? `\\(p_{\\text{բաց}}=p_{\\text{մթն}}+p_{\\text{ավել}}\\): <span class="mono">${fmt(p, 2)} = 1 + ${fmt(p - 1, 2)}</span> բար = <span class="mono">${fmt(p * 1e5, 0)}</span> Պա`
      : `\\(p_{\\text{բաց}}=p_{\\text{մթն}}-p_{\\text{վակ}}\\): <span class="mono">${fmt(p, 2)} = 1 − ${fmt(1 - p, 2)}</span> բար = <span class="mono">${fmt(p * 1e5, 0)}</span> Պա`;
    if (window.renderMathInElement) renderMathInElement(o, {delimiters:[{left:'\\(', right:'\\)', display:false}], throwOnError:false});
  }
  slider(ctl(st), 'Բացարձակ ճնշում', .1, 3, .05, 1.8, v => fmt(v, 2) + ' բար', upd);
  upd(1.8);
}};

/* ---------- 1.3 isochore, isobar, isotherm and a cycle ---------- */
VIZ.pv3 = {kind:'a', cap:'\\(p\\text{–}\\upsilon\\) դիագրամում իզոբարը հորիզոնական է, իզոխորը՝ ուղղաձիգ, իզոթերմը՝ հիպերբոլ։ Երեքից կազմված փակ պրոցեսը համակարգը վերադարձնում է սկզբնական վիճակին՝ <b>ցիկլ</b>։',
f(st){
  const s = svg(st, 560, 250, 'p–υ դիագրամ'), A = axes(s, {x:50, y:20, w:440, h:200, xr:[0, 2.6], yr:[0, 2.6], xl:'υ', yl:'p'});
  const P = [[1, 2], [2.2, 2], [2.2, 2 / 2.2]];
  const segs = [
    {n:'1–2 իզոբար (p = const), ընդարձակում', c:C.heat, f:t => [lerp(1, 2.2, t), 2]},
    {n:'2–3 իզոխոր (υ = const), ճնշման նվազում', c:C.acc, f:t => [2.2, lerp(2, 2 / 2.2, t)]},
    {n:'3–1 իզոթերմ (pυ = const), սեղմում', c:C.good, f:t => { const v = lerp(2.2, 1, t); return [v, 2 / v]; }}];
  S('path', {d:A.fn(v => 2 / v, .78, 2.55), fill:'none', stroke:C.line, 'stroke-dasharray':'4 4'}, s);
  const paths = segs.map(g => { const r = []; for (let i = 0; i <= 40; i++){ const q = g.f(i / 40); r.push([A.X(q[0]), A.Y(q[1])]); }
    return S('path', {d:pts(r), fill:'none', stroke:g.c, 'stroke-width':2.5}, s); });
  segs.forEach(g => { const a = g.f(.45), b = g.f(.55); arrow(s, A.X(a[0]), A.Y(a[1]), A.X(b[0]), A.Y(b[1]), g.c, 2, 9); });
  P.forEach((q, i) => { S('circle', {cx:A.X(q[0]), cy:A.Y(q[1]), r:4, fill:C.ink}, s); T(s, A.X(q[0]) + (i ? 8 : -14), A.Y(q[1]) - 8, String(i + 1), {'font-weight':700}); });
  const dot = S('circle', {r:7, fill:C.surf, 'stroke-width':3}, s), lab = T(s, 280, 16, '', {'text-anchor':'middle', 'font-weight':600});
  anim(st, (dt, t) => {
    const u = (t / 2.2) % 3, i = Math.floor(u), q = segs[i].f(u - i);
    attrs(dot, {cx:A.X(q[0]), cy:A.Y(q[1]), stroke:segs[i].c});
    paths.forEach((p, j) => p.setAttribute('stroke-width', j === i ? 4 : 2));
    setT(lab, segs[i].n); lab.style.fill = segs[i].c;
  }, ctl(st));
}};

/* ---------- 1.4 heat and work ---------- */
VIZ.heatwork = {kind:'a', cap:'Էներգիայի փոխանցման երկու եղանակ. <b>ջերմության ձևով</b>՝ տաք մարմնից սառը, մինչև ջերմային հավասարակշռություն, և <b>աշխատանքի ձևով</b>՝ մարմնի (մխոցի) տեղափոխությամբ. մարմնի կատարած աշխատանքը դրական է, մարմնի վրա կատարվածը՝ բացասական։',
f(st){
  const s = svg(st, 600, 230, 'Ջերմություն և աշխատանք');
  T(s, 150, 18, 'Ջերմության ձևով', {'text-anchor':'middle', 'font-weight':600});
  T(s, 450, 18, 'Աշխատանքի ձևով', {'text-anchor':'middle', 'font-weight':600});
  const hot = S('rect', {x:40, y:60, width:100, height:110, rx:6, stroke:C.ink}, s), cold = S('rect', {x:160, y:60, width:100, height:110, rx:6, stroke:C.ink}, s);
  const th = T(s, 90, 190, '', {'text-anchor':'middle'}), tc = T(s, 210, 190, '', {'text-anchor':'middle'}), eq = T(s, 150, 214, '', {'text-anchor':'middle', 'font-weight':600, fill:C.good});
  const dots = []; for (let i = 0; i < 9; i++) dots.push(S('circle', {r:3.5, fill:C.heat}, s));
  S('line', {x1:300, y1:30, x2:300, y2:220, stroke:C.line}, s);
  const cyl = cylinder(s, 400, 70, 100, 130, {weight:true}), wl = T(s, 520, 0, '', {'font-weight':600});
  const wa = S('g', {}, s);
  anim(st, (dt, t) => {
    const u = t % 9, tau = Math.min(u, 6), d = Math.exp(-tau / 1.6), TH = 80 - 30 * (1 - d), TC = 20 + 30 * (1 - d);
    const mix = (a, b, r) => `color-mix(in srgb, ${a} ${Math.round(r * 100)}%, ${b})`;
    hot.style.fill = mix('var(--heat)', 'var(--surface)', .15 + .6 * (TH - 20) / 60); cold.style.fill = mix('var(--heat)', 'var(--surface)', .15 + .6 * (TC - 20) / 60);
    setT(th, 'T₁ = ' + fmt(TH, 0) + ' °C'); setT(tc, 'T₂ = ' + fmt(TC, 0) + ' °C');
    setT(eq, d < .06 ? 'T₁ = T₂ → ջերմային հավասարակշռություն' : 'ջերմություն՝ տաքից դեպի սառը');
    eq.style.fill = d < .06 ? C.good : C.heat;
    dots.forEach((c, i) => { const ph = (t * .7 + i / 9) % 1; c.setAttribute('cx', 110 + ph * 80); c.setAttribute('cy', 75 + (i * 37) % 85); c.setAttribute('opacity', d < .06 ? 0 : Math.sin(ph * Math.PI)); });
    const w = (t % 6) / 6, up = w < .5, lev = up ? .35 + .4 * (w / .5) : .75 - .4 * ((w - .5) / .5);
    const py = cyl(lev, 'var(--accent-soft)');
    while (wa.firstChild) wa.removeChild(wa.firstChild);
    arrow(wa, 380, py + (up ? 10 : -30), 380, py + (up ? -30 : 10), up ? C.good : C.bad, 2.5, 9);
    attrs(wl, {y:py - 10}); setT(wl, up ? 'ℓ > 0' : 'ℓ < 0'); wl.style.fill = up ? C.good : C.bad;
  }, ctl(st));
}};

/* ---------- 2.1 gas laws ---------- */
VIZ.gaslaws = {kind:'i', cap:'Բոյլ–Մարիոտի (\\(T=\\text{const}\\)), Գեյ-Լյուսակի (\\(p=\\text{const}\\)) և Շառլի (\\(\\upsilon=\\text{const}\\)) օրենքները. ձախում՝ գլանը, աջում՝ նույն պրոցեսը \\(p\\text{–}\\upsilon\\) դիագրամում (1 կգ օդ, սկզբում 1 բար, 300 Կ)։',
f(st){
  const s = svg(st, 600, 250, 'Գազի օրենքներ'), p0 = 1, T0 = 300, v0 = R * T0 / 1e5;
  const cyl = cylinder(s, 50, 50, 110, 170, {weight:true});
  const A = axes(s, {x:270, y:24, w:300, h:196, xr:[0, 2], yr:[0, 2.4], xl:'υ, մ³/կգ', yl:'p, բար'});
  [.5, 1, 1.5].forEach(v => T(s, A.X(v), A.Y(0) + 14, fmt(v, 1), {'text-anchor':'middle', fill:C.muted, 'font-size':10}));
  [1, 2].forEach(v => T(s, A.X(0) - 6, A.Y(v) + 4, String(v), {'text-anchor':'end', fill:C.muted, 'font-size':10}));
  const curve = S('path', {fill:'none', stroke:C.acc, 'stroke-width':2.5}, s), p1 = S('circle', {r:4, fill:C.muted}, s), dot = S('circle', {r:6, fill:C.heat}, s);
  const gl = T(s, 105, 240, '', {'text-anchor':'middle'});
  const c = ctl(st), sc = H('div', {class:'vz-ctl'}, st), o = out(st);
  let mode = 'b';
  function draw(x){
    let p = p0, v = v0, Tk = T0;
    if (mode === 'b'){ v = v0 * x; p = p0 / x; } else if (mode === 'g'){ Tk = x; v = v0 * x / T0; } else { Tk = x; p = p0 * x / T0; }
    attrs(curve, {d:mode === 'b' ? A.fn(u => p0 * v0 / u, .37, 1.95) : mode === 'g' ? `M${A.X(.05)} ${A.Y(p0)}H${A.X(1.95)}` : `M${A.X(v0)} ${A.Y(.05)}V${A.Y(2.35)}`});
    attrs(p1, {cx:A.X(v0), cy:A.Y(p0)}); attrs(dot, {cx:A.X(v), cy:A.Y(p)});
    cyl(clamp(v / 2, .1, .95), tint(Tk / T0));
    setT(gl, 'p = ' + fmt(p, 2) + ' բար, T = ' + fmt(Tk, 0) + ' Կ');
    o.innerHTML = mode === 'b' ? `\\(p_1\\upsilon_1=p_2\\upsilon_2\\): <span class="mono">${fmt(p0, 2)}·${fmt(v0, 3)} = ${fmt(p, 2)}·${fmt(v, 3)}</span> (բար·մ³/կգ) — ծավալը փոխվում է ճնշմանը հակադարձ համեմատական`
      : mode === 'g' ? `\\(\\upsilon_1/\\upsilon_2=T_1/T_2\\): <span class="mono">${fmt(v0 / v, 3)} = ${fmt(T0 / Tk, 3)}</span> — ծավալը համեմատական է բացարձակ ջերմաստիճանին`
      : `\\(p_1/p_2=T_1/T_2\\): <span class="mono">${fmt(p0 / p, 3)} = ${fmt(T0 / Tk, 3)}</span> — ճնշումը համեմատական է բացարձակ ջերմաստիճանին`;
    if (window.renderMathInElement) renderMathInElement(o, {delimiters:[{left:'\\(', right:'\\)', display:false}], throwOnError:false});
  }
  function build(){
    sc.innerHTML = '';
    if (mode === 'b') slider(sc, 'υ₂/υ₁', .5, 1.9, .02, 1.4, v => fmt(v, 2), draw), draw(1.4);
    else slider(sc, 'T, Կ', 150, 600, 5, 450, v => v + ' Կ', draw), draw(450);
  }
  seg(c, [['b', 'Բոյլ–Մարիոտ'], ['g', 'Գեյ-Լյուսակ'], ['c', 'Շառլ']], mode, m => { mode = m; build(); });
  build();
}};

/* ---------- 2.2 gas constant: work of 1 kg at p = const per 1 K ---------- */
VIZ.gasR = {kind:'i', cap:'\\(R\\)-ի ֆիզիկական իմաստը. 1 կգ գազը հաստատուն ճնշման տակ տաքացնելիս մխոցը բարձրանում է, և գազը կատարում է \\(\\ell=p(\\upsilon_2-\\upsilon_1)=R(T_2-T_1)\\) աշխատանք. \\(\\Delta T=1\\) Կ-ի դեպքում \\(\\ell=R\\)։ Ներքևում՝ \\(R\\)-ը տարբեր գազերի համար։',
f(st){
  const s = svg(st, 600, 240, 'Գազային հաստատուն'), p = 1e5, T1 = 300;
  const cyl = cylinder(s, 60, 40, 110, 160, {weight:true}); const fl = flames(s, 70, 206, 90, true);
  const L1 = S('line', {x1:40, x2:190, stroke:C.muted, 'stroke-dasharray':'4 3'}, s), lb = T(s, 196, 0, '', {fill:C.muted});
  const gx = 300; T(s, gx, 30, 'R, Ջ/(կգ·Կ)', {'font-weight':600});
  [['օդ', 287.05], ['H₂', 4124], ['CO₂', 188.9]].forEach(([n, v], i) => {
    const y = 50 + i * 34, w = Math.log10(v) / Math.log10(5000) * 215;
    T(s, gx, y + 14, n); S('rect', {x:gx + 40, y, width:w, height:20, rx:3, fill:i ? C.line : C.acc}, s);
    T(s, gx + 46 + w, y + 14, fmt(v, v > 1000 ? 0 : 2).replace(',00', ''), {'font-size':11});
  });
  T(s, gx, 162, 'սանդղակը լոգարիթմական է', {fill:C.muted, 'font-size':10});
  const o = out(st);
  function draw(dT){
    const v1 = R * T1 / p, v2 = R * (T1 + dT) / p, y1 = 40 + 160 - v1 / 1.3 * .75 * 160;
    cyl(v2 / 1.3 * .75, dT > 0 ? C.heatS : 'var(--sunk)');
    attrs(L1, {y1, y2:y1}); attrs(lb, {y:y1 + 4}); setT(lb, 'υ₁');
    fl.style.display = dT > 0 ? '' : 'none';
    o.innerHTML = `p = 1 բար = const, T₁ = 300 Կ → T₂ = <b class="mono">${fmt(T1 + dT, 0)}</b> Կ. υ₁ = <span class="mono">${fmt(v1, 4)}</span>, υ₂ = <span class="mono">${fmt(v2, 4)}</span> մ³/կգ<br>ℓ = p(υ₂ − υ₁) = <b class="mono">${fmt(p * (v2 - v1), 0)}</b> Ջ/կգ = R·ΔT = 287·${dT}${dT === 1 ? ' → <b>ℓ = R</b>' : ''}`;
  }
  slider(ctl(st), 'ΔT', 0, 100, 1, 1, v => v + ' Կ', draw); draw(1);
}};

/* ---------- 2.3 real gas corrections ---------- */
VIZ.realgas = {kind:'a', cap:'Վան դեր Վաալսի ուղղումները. \\(b\\)՝ մոլեկուլների <b>սեփական ծավալը</b> (շարժման համար մնում է \\(\\upsilon-b\\)), \\(a/\\upsilon^2\\)՝ <b>միջմոլեկուլային ձգողությունը</b>, որը թուլացնում է պատին հարվածը։',
f(st){
  const s = svg(st, 600, 240, 'Իրական գազ');
  T(s, 150, 18, 'b՝ սեփական ծավալ', {'text-anchor':'middle', 'font-weight':600, fill:C.heat});
  T(s, 450, 18, 'a/υ²՝ ձգողություն', {'text-anchor':'middle', 'font-weight':600, fill:C.acc});
  S('rect', {x:30, y:32, width:240, height:160, fill:'var(--sunk)', stroke:C.ink, 'stroke-width':2}, s);
  S('rect', {x:330, y:32, width:240, height:160, fill:'var(--sunk)', stroke:C.ink, 'stroke-width':2}, s);
  const r = window.VZ.rnd(3), A = [], B = [];
  for (let i = 0; i < 9; i++) A.push({x:50 + r() * 200, y:52 + r() * 120, vx:r() - .5, vy:r() - .5, c:S('circle', {r:13, fill:C.heatS, stroke:C.heat, 'stroke-width':1.5}, s)});
  for (let i = 0; i < 7; i++) B.push({x:380 + r() * 160, y:60 + r() * 110, c:S('circle', {r:7, fill:C.acc}, s)});
  const m = S('circle', {r:7, fill:C.bad}, s), ar = S('g', {}, s);
  T(s, 300, 214, '(p + a/υ^{2})(υ − b) = RT', {'text-anchor':'middle', 'font-size':15, 'font-weight':600});
  T(s, 300, 233, 'իդեալական գազում a = 0, b = 0 → pυ = RT', {'text-anchor':'middle', fill:C.muted, 'font-size':11});
  anim(st, (dt, t) => {
    for (const q of A){ q.x += q.vx * 40 * dt; q.y += q.vy * 40 * dt;
      if (q.x < 45 || q.x > 255) q.vx *= -1; if (q.y < 47 || q.y > 177) q.vy *= -1;
      q.x = clamp(q.x, 45, 255); q.y = clamp(q.y, 47, 177); attrs(q.c, {cx:q.x, cy:q.y}); }
    B.forEach((q, i) => attrs(q.c, {cx:q.x + Math.sin(t * 1.3 + i) * 4, cy:q.y + Math.cos(t + i) * 4}));
    const u = (t % 3) / 3, mx = 400 + 162 * Math.sin(u * Math.PI), my = 112;
    attrs(m, {cx:mx, cy:my});
    while (ar.firstChild) ar.removeChild(ar.firstChild);
    if (mx > 520) [[-1, -.6], [-1, 0], [-1, .6]].forEach(([dx, dy]) => arrow(ar, mx - 9, my + dy * 6, mx - 9 + dx * 26, my + dy * 26, C.acc, 1.6, 6));
  }, ctl(st));
}};

/* ---------- 2.4 mixtures: Dalton ---------- */
VIZ.dalton = {kind:'a', cap:'Խառնուրդում յուրաքանչյուր գազ իրեն պահում է այնպես, կարծես <b>միայնակ զբաղեցնում է ամբողջ ծավալը</b>, և ստեղծում է պարցիալ ճնշում. \\(p=\\sum p_i\\)։ Ներքևում՝ օդի զանգվածային բաժինները։',
f(st){
  const s = svg(st, 600, 250, 'Դալտոնի օրենք'), r = window.VZ.rnd(11), boxes = [[20, 'գազ 1', C.acc, 10, 0], [215, 'գազ 2', C.heat, 0, 6], [410, 'խառնուրդ', C.ink, 10, 6]];
  const P = [];
  boxes.forEach(([x, n, c, n1, n2], i) => {
    S('rect', {x, y:30, width:170, height:120, fill:'var(--sunk)', stroke:C.ink, 'stroke-width':2}, s);
    T(s, x + 85, 20, n, {'text-anchor':'middle', 'font-weight':600});
    for (let j = 0; j < n1 + n2; j++){ const a = r() * 6.28; P.push({x:x + 8 + r() * 154, y:38 + r() * 104, x0:x, vx:Math.cos(a), vy:Math.sin(a), c:S('circle', {r:4, fill:j < n1 ? C.acc : C.heat}, s)}); }
    const bx = x + 60, by = 160;
    if (i < 2){ S('rect', {x:bx, y:by, width:50, height:i ? 12 : 20, fill:i ? C.heat : C.acc}, s); T(s, bx + 58, by + 12, i ? 'p₂' : 'p₁'); }
    else { S('rect', {x:bx, y:by, width:50, height:20, fill:C.acc}, s); S('rect', {x:bx, y:by + 20, width:50, height:12, fill:C.heat}, s); T(s, bx + 58, by + 20, 'p = p₁ + p₂'); }
  });
  T(s, 20, 222, 'Օդ, զանգվածային բաժին q_{i}', {'font-weight':600});
  const fr = [['N₂ 0,7552', .7552, C.acc], ['O₂ 0,2314', .2314, C.heat], ['', .0134, C.line]]; let x = 230;
  fr.forEach(([n, q, c]) => { S('rect', {x, y:208, width:q * 350, height:20, fill:c}, s); if (n) T(s, x + 6, 222, n, {fill:'var(--surface)', 'font-size':11, 'font-weight':600}); x += q * 350; });
  T(s, 580, 244, 'Σq_{i} = 1', {'text-anchor':'end', fill:C.muted, 'font-size':11});
  anim(st, dt => { for (const q of P){ q.x += q.vx * 50 * dt; q.y += q.vy * 50 * dt;
    if (q.x < q.x0 + 5 || q.x > q.x0 + 165) q.vx *= -1; if (q.y < 35 || q.y > 145) q.vy *= -1; attrs(q.c, {cx:q.x, cy:q.y}); } }, ctl(st));
}};

/* ---------- 2.5 heat capacity: c_p > c_v ---------- */
VIZ.cpcv = {kind:'i', cap:'Միևնույն \\(\\Delta T\\)-ի համար \\(p=\\text{const}\\)-ում պետք է ավելի շատ ջերմություն, քան \\(\\upsilon=\\text{const}\\)-ում. ջերմության մի մասը ծախսվում է ընդարձակման աշխատանքի վրա։ Տարբերությունը \\(c_p-c_\\upsilon=R\\) (Մայեր)։ Օդ՝ \\(c_\\upsilon=R/(k-1)\\), \\(c_p=kR/(k-1)\\)։',
f(st){
  const s = svg(st, 600, 260, 'cp և cv');
  T(s, 105, 18, 'υ = const', {'text-anchor':'middle', 'font-weight':600}); T(s, 285, 18, 'p = const', {'text-anchor':'middle', 'font-weight':600});
  const c1 = cylinder(s, 50, 60, 110, 140), c2 = cylinder(s, 230, 60, 110, 140, {weight:true});
  const pinA = S('rect', {x:42, width:12, height:6, fill:C.ink}, s), pinB = S('rect', {x:158, width:12, height:6, fill:C.ink}, s);
  flames(s, 60, 206, 90, true); flames(s, 240, 206, 90, true);
  const bx = 380, sc = 140 / (CP * 100); T(s, bx, 40, 'q, կՋ/կգ', {'font-weight':600});
  const b1 = S('rect', {x:bx, y:60, height:24, fill:C.heat}, s), b2a = S('rect', {x:bx, y:120, height:24, fill:C.heat}, s), b2b = S('rect', {y:120, height:24, fill:C.good}, s);
  const t1 = T(s, bx, 100, ''), t2 = T(s, bx, 160, ''), t3 = T(s, bx, 178, '', {fill:C.good});
  T(s, bx, 214, '■ Δu = c_{υ}ΔT', {fill:C.heat, 'font-size':11}); T(s, bx, 230, '■ ընդարձակման աշխատանք RΔT', {fill:C.good, 'font-size':11});
  function draw(dT){
    const y = c1(.55, tint(1 + dT / 300)); attrs(pinA, {y:y - 7}); attrs(pinB, {y:y - 7});
    c2(.55 * (300 + dT) / 300, tint(1 + dT / 300));
    attrs(b1, {width:CV * dT * sc}); attrs(b2a, {width:CV * dT * sc}); attrs(b2b, {x:bx + CV * dT * sc, width:R * dT * sc});
    setT(t1, 'q_{υ} = c_{υ}ΔT = ' + kJ(CV * dT)); setT(t2, 'q_{p} = c_{p}ΔT = ' + kJ(CP * dT)); setT(t3, 'q_{p} − q_{υ} = RΔT = ' + kJ(R * dT));
  }
  slider(ctl(st), 'ΔT', 0, 100, 1, 60, v => v + ' Կ', draw); draw(60);
}};

/* ---------- 2.5 degrees of freedom ---------- */
VIZ.dof = {kind:'a', cap:'Կինետիկ տեսությունից՝ \\(c_{\\upsilon\\mu}=\\frac{y}{2}R_\\mu\\), \\(c_{p\\mu}=\\left(1+\\frac{y}{2}\\right)R_\\mu\\), \\(k=(y+2)/y\\), որտեղ \\(y\\)-ը ազատության աստիճանների թիվն է (համընկնում է փորձին միայն միատոմ գազերի համար)։',
f(st){
  const s = svg(st, 600, 220, 'Ազատության աստիճաններ'), G = [];
  const D = [['միատոմ', 3, [[0, 0]]], ['երկատոմ', 5, [[-14, 0], [14, 0]]], ['եռատոմ', 6, [[-16, 8], [16, 8], [0, -14]]]];
  D.forEach(([n, y, at], i) => {
    const cx = 100 + i * 200; T(s, cx, 22, n, {'text-anchor':'middle', 'font-weight':600});
    const g = S('g', {}, s); if (at.length > 1) at.forEach((a, j) => { const b = at[(j + 1) % at.length]; if (at.length > 2 || j === 0) S('line', {x1:a[0], y1:a[1], x2:b[0], y2:b[1], stroke:C.muted, 'stroke-width':4}, g); });
    at.forEach(a => S('circle', {cx:a[0], cy:a[1], r:10, fill:i ? C.acc : C.heat}, g)); G.push([g, cx, i]);
    [['y', String(y)], ['c_{υμ}', fmt(y / 2, 1) + ' R_{μ}'], ['c_{pμ}', fmt(1 + y / 2, 1) + ' R_{μ}'], ['k', fmt((y + 2) / y, 2)]].forEach(([a, b], r) => {
      T(s, cx - 10, 130 + r * 20, a + ' =', {'text-anchor':'end', fill:C.muted}); T(s, cx - 4, 130 + r * 20, b, {'font-weight':r === 3 ? 700 : 400}); });
  });
  anim(st, (dt, t) => G.forEach(([g, cx, i]) => g.setAttribute('transform', `translate(${cx + Math.sin(t * 1.5 + i) * 18} ${68 + Math.cos(t * 1.2 + i * 2) * 10}) rotate(${i ? t * 70 * (i === 2 ? -1 : 1) : 0})`)), ctl(st));
}};

/* ---------- 3.1 first law ---------- */
VIZ.firstlaw = {kind:'i', cap:'Համակարգին հաղորդված ջերմությունը ծախսվում է <b>ներքին էներգիայի փոփոխման</b> և <b>արտաքին ուժերի դեմ աշխատանքի</b> վրա. \\(Q=\\Delta U+L\\)։ Փոխեք, թե \\(Q\\)-ի որ մասն է դառնում աշխատանք։',
f(st){
  const s = svg(st, 600, 250, 'Առաջին օրենք'), cyl = cylinder(s, 80, 50, 120, 150, {weight:true}); flames(s, 90, 206, 100, true);
  T(s, 140, 242, 'Q', {'text-anchor':'middle', 'font-weight':700, fill:C.heat});
  const bx = 300; T(s, bx, 40, 'Q = ΔU + L', {'font-size':15, 'font-weight':700});
  S('rect', {x:bx, y:60, width:260, height:26, fill:C.heat}, s); T(s, bx + 6, 78, 'Q = 100%', {fill:'var(--surface)', 'font-weight':600});
  const bu = S('rect', {x:bx, y:110, height:26, fill:C.warn}, s), bl = S('rect', {y:110, height:26, fill:C.good}, s);
  const tu = T(s, bx, 156, '', {fill:C.warn, 'font-weight':600}), tl = T(s, bx, 174, '', {fill:C.good, 'font-weight':600});
  const P = []; for (let i = 0; i < 14; i++) P.push(S('circle', {r:3.5}, s));
  let f = .4, py = 0;
  const c = ctl(st);
  slider(c, 'L-ի բաժինը', 0, 100, 5, 40, v => v + '%', v => { f = v / 100; A.draw(); });
  const A = anim(st, (dt, t) => {
    py = cyl(.35 + .45 * f, `color-mix(in srgb, var(--heat) ${Math.round(15 + 45 * (1 - f))}%, var(--surface))`);
    attrs(bu, {width:260 * (1 - f)}); attrs(bl, {x:bx + 260 * (1 - f), width:260 * f});
    setT(tu, 'ΔU = ' + Math.round(100 * (1 - f)) + '%՝ ջերմաստիճանի աճ'); setT(tl, 'L = ' + Math.round(100 * f) + '%՝ մխոցի տեղափոխություն');
    P.forEach((c, i) => { const ph = (t * .45 + i / P.length) % 1, toL = (i / P.length) < f, x = 100 + (i * 53) % 80;
      const y = ph < .5 ? 205 - ph * 2 * 80 : toL ? lerp(125, py - 10, (ph - .5) * 2) : 125 + Math.sin(ph * 20 + i) * 8;
      attrs(c, {cx:toL && ph > .5 ? lerp(x, 140, (ph - .5) * 2) : x, cy:y, fill:toL && ph > .5 ? C.good : ph > .5 ? C.warn : C.heat, opacity:ph > .92 ? (1 - ph) * 12 : 1}); });
  }, c);
}};

/* ---------- 3.2 internal energy: path independent ---------- */
VIZ.upath = {kind:'a', cap:'1 և 2 վիճակների միջև երկու տարբեր ուղի (\\(a\\) և \\(b\\)). \\(\\Delta u=c_\\upsilon(T_2-T_1)\\)-ը <b>նույնն է</b> (վիճակի ֆունկցիա), իսկ աշխատանքը (կորի տակ մակերեսը) և ջերմությունը՝ <b>տարբեր</b> (պրոցեսի ֆունկցիաներ)։ 1 կգ օդ։',
f(st){
  const s = svg(st, 600, 250, 'Ներքին էներգիա'), A = axes(s, {x:50, y:20, w:300, h:200, xr:[0, 2], yr:[0, 2.6], xl:'υ, մ³/կգ', yl:'p, բար'});
  const p1 = 2, v1 = .6, p2 = 1, v2 = 1.6, T1 = p1 * 1e5 * v1 / R, T2 = p2 * 1e5 * v2 / R, du = CV * (T2 - T1);
  const ways = [{n:'a', c:C.heat, P:[[v1, p1], [v2, p1], [v2, p2]]}, {n:'b', c:C.acc, P:[[v1, p1], [v1, p2], [v2, p2]]}];
  ways.forEach(w => { w.area = S('path', {d:pts([[A.X(v1), A.Y(0)], ...w.P.map(q => [A.X(q[0]), A.Y(q[1])]), [A.X(v2), A.Y(0)]]) + 'Z', fill:w.c, opacity:.13}, s);
    w.line = S('path', {d:pts(w.P.map(q => [A.X(q[0]), A.Y(q[1])])), fill:'none', stroke:w.c, 'stroke-width':2.5}, s);
    T(s, A.X(w.P[1][0]) + (w.n === 'a' ? 6 : -16), A.Y(w.P[1][1]) + (w.n === 'a' ? -6 : 16), w.n, {'font-weight':700, fill:w.c}); });
  [[v1, p1, '1'], [v2, p2, '2']].forEach(([v, p, n]) => { S('circle', {cx:A.X(v), cy:A.Y(p), r:4.5, fill:C.ink}, s); T(s, A.X(v) - 14, A.Y(p) - 6, n, {'font-weight':700}); });
  const dot = S('circle', {r:7, fill:C.surf, 'stroke-width':3}, s);
  const tx = 390, rows = [['', 'a', 'b'], ['Δu, կՋ/կգ', kJ(du), kJ(du)], ['ℓ, կՋ/կգ', kJ(p1 * 1e5 * (v2 - v1)), kJ(p2 * 1e5 * (v2 - v1))], ['q = Δu + ℓ', kJ(du + p1 * 1e5 * (v2 - v1)), kJ(du + p2 * 1e5 * (v2 - v1))]];
  rows.forEach((r, i) => r.forEach((c, j) => T(s, tx + [0, 110, 160][j], 50 + i * 26, c, {'font-weight':i === 0 || (i === 1 && j) ? 700 : 400, fill:j === 0 ? C.muted : i === 0 ? (j === 1 ? C.heat : C.acc) : C.ink})));
  T(s, tx, 168, 'T₁ = ' + fmt(T1, 0) + ' Կ, T₂ = ' + fmt(T2, 0) + ' Կ', {fill:C.muted});
  T(s, tx, 190, 'Δu-ն նույնն է, ℓ-ն և q-ն՝ ոչ', {'font-weight':600, fill:C.good});
  anim(st, (dt, t) => {
    const k = Math.floor(t / 3) % 2, w = ways[k], u = Math.min(1, (t % 3) / 2.2), seg1 = u < .5, a = w.P[seg1 ? 0 : 1], b = w.P[seg1 ? 1 : 2], r = seg1 ? u * 2 : u * 2 - 1;
    attrs(dot, {cx:A.X(lerp(a[0], b[0], r)), cy:A.Y(lerp(a[1], b[1], r)), stroke:w.c});
    ways.forEach((x, j) => { x.area.setAttribute('opacity', j === k ? .22 : .06); x.line.setAttribute('stroke-width', j === k ? 4 : 2); });
  }, ctl(st));
}};

/* ---------- 3.3 work = area under the curve ---------- */
VIZ.pdv = {kind:'i', cap:'Գազի աշխատանքը \\(\\ell=\\int p\\,d\\upsilon\\)՝ \\(p\\text{–}\\upsilon\\) դիագրամում <b>կորի տակ մակերեսը</b>. ընդարձակման ժամանակ դրական է, սեղմման ժամանակ՝ բացասական։ Մասնավոր դեպքերի բանաձևերը՝ ըստ դասախոսության (1 կգ օդ, 1 բար, 300 Կ)։',
f(st){
  const s = svg(st, 600, 250, 'Աշխատանք'), A = axes(s, {x:50, y:20, w:320, h:200, xr:[0, 2.4], yr:[0, 2.6], xl:'υ, մ³/կգ', yl:'p, բար'});
  const p1 = 1, v1 = R * 300 / 1e5;
  const area = S('path', {}, s), line = S('path', {fill:'none', stroke:C.ink, 'stroke-width':2.5}, s), dot = S('circle', {r:6, fill:C.heat}, s);
  S('circle', {cx:A.X(v1), cy:A.Y(p1), r:4, fill:C.ink}, s); T(s, A.X(v1) - 12, A.Y(p1) - 8, '1', {'font-weight':700});
  const l2 = T(s, 0, 0, '2', {'font-weight':700}), big = T(s, 470, 60, '', {'text-anchor':'middle', 'font-size':20, 'font-weight':700}), sub = T(s, 470, 84, '', {'text-anchor':'middle', fill:C.muted});
  const fx = T(s, 470, 130, '', {'text-anchor':'middle', 'font-size':13}), o = out(st);
  let mode = 'p', r = 1.8;
  const pr = (v) => mode === 'p' ? p1 : mode === 'T' ? p1 * v1 / v : p1 * Math.pow(v1 / v, K);
  function ell(){ const v2 = v1 * r; if (mode === 'p') return p1 * 1e5 * (v2 - v1); if (mode === 'T') return R * 300 * Math.log(r); const T2 = 300 * Math.pow(1 / r, K - 1); return R / (K - 1) * (300 - T2); }
  const c = ctl(st);
  seg(c, [['p', 'իզոբար'], ['T', 'իզոթերմ'], ['s', 'ադիաբատ']], mode, m => { mode = m; An.t = 0; An.draw(); });
  slider(c, 'υ₂/υ₁', .4, 2.6, .05, 1.8, v => fmt(v, 2), v => { r = v; An.t = 0; An.draw(); });
  const An = anim(st, (dt, t) => {
    const v2 = v1 * r, u = Math.min(1, (t % 4) / 2.5), ve = lerp(v1, v2, u);
    attrs(line, {d:A.fn(pr, v1, v2)});
    const L = ell(), pos = L >= 0;
    attrs(area, {d:A.fn(pr, v1, ve, 60) + `L${A.X(ve)} ${A.Y(0)}L${A.X(v1)} ${A.Y(0)}Z`, fill:pos ? C.good : C.bad, opacity:.25});
    attrs(dot, {cx:A.X(ve), cy:A.Y(pr(ve))}); attrs(l2, {x:A.X(v2) + 6, y:A.Y(pr(v2)) - 8});
    setT(big, 'ℓ = ' + kJ(L) + ' կՋ/կգ'); big.style.fill = pos ? C.good : C.bad;
    setT(sub, pos ? 'ընդարձակում (dυ > 0)' : 'սեղմում (dυ < 0)');
    setT(fx, mode === 'p' ? 'ℓ = p(υ₂ − υ₁)' : mode === 'T' ? 'ℓ = RT ln(υ₂/υ₁)' : 'ℓ = R(T₁ − T₂)/(k − 1)');
  }, c, 2.5);
}};

/* ---------- 3.4 mean heat capacity ---------- */
VIZ.cmean = {kind:'a', cap:'Ջերմությունը \\(q=\\int_{T_1}^{T_2}c\\,dT\\)՝ \\(c(T)\\) գրաֆիկի տակ մակերեսը։ Գծային \\(c(T)\\)-ի դեպքում այն հավասար է ուղղանկյան մակերեսին, որի բարձրությունը իսկական ջերմունակությունն է միջին ջերմաստիճանում՝ \\(q=c_{T_{\\text{մ}}}(T_2-T_1)\\)։',
f(st){
  const s = svg(st, 600, 250, 'Միջին ջերմունակություն'), A = axes(s, {x:50, y:20, w:420, h:200, xr:[0, 10], yr:[0, 10], xl:'T', yl:'c'});
  const cf = x => 3 + .5 * x;
  S('path', {d:A.fn(cf, .3, 9.8, 2), fill:'none', stroke:C.ink, 'stroke-width':2}, s); T(s, A.X(9.8), A.Y(cf(9.8)) - 8, 'c(T)', {'text-anchor':'end'});
  const sh = S('path', {fill:C.heat, opacity:.28, stroke:C.heat, 'stroke-width':1.5}, s), gl = S('g', {}, s), lab = T(s, 490, 80, '', {'font-weight':600});
  let a = 2, b = 8;
  const c = ctl(st);
  slider(c, 'T₁', .5, 5, .1, 2, v => fmt(v, 1), v => { a = v; An.draw(); });
  slider(c, 'T₂', 5.5, 9.5, .1, 8, v => fmt(v, 1), v => { b = v; An.draw(); });
  const An = anim(st, (dt, t) => {
    const ss = x => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); }, ph = t % 6, w = ss((ph - 1) / 1.5) - ss((ph - 4) / 1.5);
    const tm = (a + b) / 2, ya = lerp(cf(a), cf(tm), w), yb = lerp(cf(b), cf(tm), w);
    attrs(sh, {d:pts([[A.X(a), A.Y(0)], [A.X(a), A.Y(ya)], [A.X(b), A.Y(yb)], [A.X(b), A.Y(0)]]) + 'Z'});
    while (gl.firstChild) gl.removeChild(gl.firstChild);
    S('line', {x1:A.X(tm), x2:A.X(tm), y1:A.Y(0), y2:A.Y(cf(tm)), stroke:C.muted, 'stroke-dasharray':'4 3'}, gl);
    S('circle', {cx:A.X(tm), cy:A.Y(cf(tm)), r:4, fill:C.ink}, gl);
    [[a, 'T₁'], [tm, 'T_{մ}'], [b, 'T₂']].forEach(([x, n]) => T(gl, A.X(x), A.Y(0) + 15, n, {'text-anchor':'middle'}));
    T(gl, A.X(tm) + 6, A.Y(cf(tm)) - 8, 'c_{Tմ}', {});
    setT(lab, w < .5 ? '∫c dT' : 'c_{Tմ}·(T₂ − T₁)');
    T(gl, 490, 104, 'մակերեսը նույնն է', {fill:C.muted});
  }, c);
}};

/* ---------- 3.5 enthalpy ---------- */
VIZ.enthalpy = {kind:'i', cap:'Գազ + մխոց + կշռաքար՝ <b>ընդլայնված համակարգ</b>. նրա էներգիան \\(i=u+p\\upsilon\\), որտեղ \\(p\\upsilon\\)-ն կշռաքարի պոտենցիալ էներգիան է («ճնշման պոտենցիալ էներգիա»)։ Իդեալական գազի համար \\(p\\upsilon=RT\\), ուստի \\(di=c_\\upsilon dT+R\\,dT=c_p\\,dT\\)։',
f(st){
  const s = svg(st, 600, 260, 'Էնթալպիա'), cyl = cylinder(s, 70, 70, 120, 150, {weight:true});
  const box = S('rect', {x:52, width:156, rx:8, fill:'none', stroke:C.acc, 'stroke-width':1.5, 'stroke-dasharray':'6 4'}, s), bl = T(s, 130, 0, 'ընդլայնված համակարգ', {'text-anchor':'middle', fill:C.acc, 'font-size':11});
  const bx = 300, sc = 200 / (CP * 800);
  T(s, bx, 40, 'p = const, 1 կգ օդ', {fill:C.muted});
  const ru = S('rect', {x:bx, y:60, height:30, fill:C.warn}, s), rp = S('rect', {y:60, height:30, fill:C.acc}, s);
  const tu = T(s, bx, 112, '', {fill:C.warn}), tp = T(s, bx, 132, '', {fill:C.acc}), ti = T(s, bx, 160, '', {'font-weight':700});
  T(s, bx, 200, 'i = u + pυ', {'font-size':16, 'font-weight':700}); T(s, bx, 222, 'Δi = c_{p}(T₂ − T₁)', {fill:C.muted});
  function draw(Tk){
    const py = cyl(.15 + .75 * Tk / 800, tint(Tk / 300)); attrs(box, {y:py - 60, height:220 + 6 - (py - 60) + 4}); attrs(bl, {y:py - 66});
    const u = CV * Tk, pv = R * Tk;
    attrs(ru, {width:u * sc * 1.0}); attrs(rp, {x:bx + u * sc, width:pv * sc});
    setT(tu, '■ u = c_{υ}T = ' + kJ(u) + ' կՋ/կգ'); setT(tp, '■ pυ = RT = ' + kJ(pv) + ' կՋ/կգ'); setT(ti, 'i = c_{p}T = ' + kJ(u + pv) + ' կՋ/կգ');
  }
  slider(ctl(st), 'T', 150, 800, 10, 300, v => v + ' Կ', draw); draw(300);
}};

window.GAZ_VZ = {R, K, CV, CP, kJ, cylinder, tint, flames};
})();
