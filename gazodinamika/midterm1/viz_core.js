/* Lecture visuals: core helpers (shared by gazodinamika and nyutagitutyun; keep the two copies identical).
   Each visual only draws what the lecture text of its section already says; it adds no new content.
   window.VIZ[id] = {kind, cap, f(stage, arg)}; window.VIZMAP["lectureId:sectionIndex"] = ["id" or "id:arg", ...]. */
(function(){
'use strict';
const NS = 'http://www.w3.org/2000/svg';
const RM = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
const VIZ = window.VIZ = window.VIZ || {};
window.VIZMAP = window.VIZMAP || {};

// colors are theme tokens, so drawings follow light/dark mode
const C = {ink:'var(--ink)', muted:'var(--muted)', line:'var(--line)', surf:'var(--surface)', sunk:'var(--sunk)', bg:'var(--bg)',
  acc:'var(--accent)', accS:'var(--accent-soft)', heat:'var(--heat)', heatS:'var(--heat-soft)',
  good:'var(--good)', goodS:'var(--good-soft)', warn:'var(--warn)', warnS:'var(--warn-soft)', bad:'var(--bad)', badS:'var(--bad-soft)'};
const CSSPROP = {fill:1, stroke:1, 'stop-color':1, color:1};

function attrs(e, a){
  for (const k in a){ const v = a[k]; if (v == null) continue;
    if (k === 'text') e.textContent = v;
    else if (CSSPROP[k] && typeof v === 'string' && v.indexOf('var(') >= 0) e.style.setProperty(k, v);
    else e.setAttribute(k, v); }
  return e;
}
const S = (tag, a, p) => { const e = attrs(document.createElementNS(NS, tag), a || {}); if (p) p.appendChild(e); return e; };
function H(tag, a, p){
  const e = document.createElement(tag);
  for (const k in (a || {})){ const v = a[k]; if (v == null) continue;
    if (k === 'text') e.textContent = v; else if (k === 'html') e.innerHTML = v; else if (k === 'class') e.className = v; else e.setAttribute(k, v); }
  if (p) p.appendChild(e); return e;
}
// wide drawings keep a minimum width on phones (the figure scrolls sideways instead of shrinking the text)
function svg(host, w, h, label){
  const s = S('svg', {viewBox:`0 0 ${w} ${h}`, class:'vz-svg', role:'img', 'aria-label':label || '', preserveAspectRatio:'xMidYMid meet'}, host);
  if (w >= 500) s.style.minWidth = Math.round(w * .78) + 'px';
  return s;
}

// text with _{sub} and ^{sup}
function T(p, x, y, str, a){
  const t = S('text', Object.assign({x, y, 'font-size':12, fill:C.ink}, a || {}), p);
  setT(t, str); return t;
}
function setT(t, str){
  while (t.firstChild) t.removeChild(t.firstChild);
  const parts = String(str).split(/([_^]\{[^}]*\})/);
  let shift = 0;
  for (const s of parts){ if (!s) continue;
    const m = s.match(/^([_^])\{([^}]*)\}$/);
    if (m){ const d = m[1] === '_' ? 4 : -6; S('tspan', {dy:d - shift, 'font-size':'.72em', text:m[2]}, t); shift = d; }
    else { S('tspan', {dy:-shift, text:s}, t); shift = 0; } }
}
const pts = a => a.map((p, i) => (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join('');
function arrow(p, x1, y1, x2, y2, col, w, head){
  col = col || C.ink; w = w || 1.6; head = head || 7;
  const g = S('g', {}, p), a = Math.atan2(y2 - y1, x2 - x1);
  S('line', {x1, y1, x2:x2 - Math.cos(a) * head * .6, y2:y2 - Math.sin(a) * head * .6, stroke:col, 'stroke-width':w, 'stroke-linecap':'round'}, g);
  S('polygon', {points:[[x2, y2], [x2 - head * Math.cos(a - .42), y2 - head * Math.sin(a - .42)], [x2 - head * Math.cos(a + .42), y2 - head * Math.sin(a + .42)]].map(q => q.join(',')).join(' '), fill:col}, g);
  return g;
}
// axes: o = {x, y, w, h, xr:[a,b], yr:[a,b], xl, yl}; returns scale functions
function axes(p, o){
  const X = v => o.x + (v - o.xr[0]) / (o.xr[1] - o.xr[0]) * o.w, Y = v => o.y + o.h - (v - o.yr[0]) / (o.yr[1] - o.yr[0]) * o.h;
  const g = S('g', {}, p);
  arrow(g, o.x, o.y + o.h, o.x + o.w + 10, o.y + o.h, C.muted, 1.2, 6);
  arrow(g, o.x, o.y + o.h, o.x, o.y - 10, C.muted, 1.2, 6);
  if (o.xl) T(g, o.x + o.w + 8, o.y + o.h + 16, o.xl, {'text-anchor':'end', fill:C.muted});
  if (o.yl) T(g, o.x + 6, o.y - 4, o.yl, {fill:C.muted});
  const fn = (f, a, b, n) => { const r = []; n = n || 80; for (let i = 0; i <= n; i++){ const v = a + (b - a) * i / n; r.push([X(v), Y(f(v))]); } return pts(r); };
  return {X, Y, g, fn, o};
}
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const fmt = (v, d) => (d == null ? 0 : d) >= 0 ? (+v).toFixed(d == null ? 0 : d).replace('.', ',').replace('-', '−') : String(v);
// seeded random, so drawings look the same on every render
function rnd(seed){ let s = seed >>> 0 || 1; return () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296; }
// computed color of a token, for canvas drawing
const col = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim() || '#888';

/* controls */
const ctl = host => H('div', {class:'vz-ctl'}, host);
function slider(host, label, min, max, step, val, show, on){
  const w = H('label', {class:'vz-sl'}, host); H('span', {html:label}, w);
  const i = H('input', {type:'range', min, max, step, value:val}, w), o = H('output', {class:'mono'}, w);
  const upd = () => { o.textContent = show ? show(+i.value) : i.value; if (on) on(+i.value); };
  i.addEventListener('input', upd); o.textContent = show ? show(+val) : val;
  return {el:i, get:() => +i.value, set:v => { i.value = v; upd(); }};
}
function seg(host, opts, val, on){
  const w = H('div', {class:'vz-seg', role:'group'}, host);
  const bs = opts.map(([v, t]) => { const b = H('button', {type:'button', html:t}, w); b.onclick = () => { pick(v); on(v); }; return [v, b]; });
  function pick(v){ bs.forEach(([x, b]) => b.setAttribute('aria-pressed', String(x === v))); }
  pick(val); return {pick};
}
function btn(host, label, on){ const b = H('button', {type:'button', class:'vz-btn', html:label}, host); b.onclick = on; return b; }
const out = host => H('div', {class:'vz-out'}, host);

/* animation loop: runs only while visible; starts paused if the user prefers reduced motion */
function anim(host, step, c){
  let on = !RM, vis = false, last = 0, t = 0, raf = 0;
  const b = c ? H('button', {type:'button', class:'vz-btn vz-play'}, c) : null;
  const io = 'IntersectionObserver' in window ? new IntersectionObserver(es => { vis = es[es.length - 1].isIntersecting; kick(); }) : null;
  if (io) io.observe(host); else vis = true;
  function frame(now){
    raf = 0;
    if (!host.isConnected){ if (io) io.disconnect(); return; }
    if (!on || !vis) return;
    const dt = last ? Math.min(.05, (now - last) / 1000) : 0; last = now; t += dt; step(dt, t);
    raf = requestAnimationFrame(frame);
  }
  function kick(){ if (on && vis && !raf){ last = 0; raf = requestAnimationFrame(frame); } }
  function lbl(){ if (b){ b.textContent = on ? '❚❚ Դադար' : '▶ Նվագարկել'; b.setAttribute('aria-pressed', String(on)); } }
  if (b) b.onclick = () => { on = !on; lbl(); kick(); };
  lbl(); step(0, 0);
  return {get t(){ return t; }, set t(v){ t = v; }, draw(){ step(0, t); }, play(){ on = true; lbl(); kick(); }};
}

const st = document.createElement('style');
st.textContent = `
.viz{margin:14px 0 4px;background:var(--surface);border:1px solid var(--line);border-radius:var(--r,10px);padding:12px 14px 10px;display:flex;flex-direction:column;gap:8px}
.vz-stage{display:flex;flex-direction:column;gap:10px;min-width:0;overflow-x:auto}
.vz-svg{width:100%;height:auto;display:block;font-family:var(--f-body);overflow:visible;user-select:none;-webkit-user-select:none}
.vz-svg text{font-family:var(--f-body)}
.vz-cv{width:100%;height:auto;display:block;border-radius:6px;background:var(--sunk)}
.vz-row{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-start}
.vz-row>*{flex:1 1 240px;min-width:0}
.vz-ctl{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;font-size:13.5px}
.vz-sl{display:flex;align-items:center;gap:8px;flex:1 1 230px;min-width:0}
.vz-sl span{color:var(--muted);white-space:nowrap}
.vz-sl input{flex:1;min-width:70px;accent-color:var(--accent);margin:0}
.vz-sl output{min-width:5.2em;text-align:right;font-size:13px}
.vz-seg{display:inline-flex;flex-wrap:wrap;border:1px solid var(--line);border-radius:8px;overflow:hidden;background:var(--surface)}
.vz-seg button{border:0;border-right:1px solid var(--line);background:transparent;padding:6px 10px;font-size:13px;line-height:1.3}
.vz-seg button:last-child{border-right:0}
.vz-seg button[aria-pressed="true"]{background:var(--accent);color:var(--accent-ink)}
.vz-btn{border:1px solid var(--line);background:var(--surface);border-radius:8px;padding:5px 11px;font-size:13px;font-weight:600}
.vz-btn:hover{border-color:var(--muted)}
.vz-play{min-width:7.5em}
.vz-out{font-size:13.5px;line-height:1.55}
.vz-out .mono{font-size:13px}
.vz-out table{border-collapse:collapse;font-size:13px}
.vz-out td,.vz-out th{padding:2px 10px 2px 0;text-align:left;vertical-align:top}
.viz figcaption{font-size:13px;color:var(--muted);line-height:1.45}
.vz-tag{display:inline-block;font-size:11px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;color:var(--accent);background:var(--accent-soft);border-radius:4px;padding:1px 6px;margin-right:4px}
.vz-good{color:var(--good)} .vz-bad{color:var(--bad)} .vz-heat{color:var(--heat)} .vz-acc{color:var(--accent)} .vz-mut{color:var(--muted)}
`;
document.head.appendChild(st);

/* section hook used by app.js */
window.vizHTML = function(lid, i){
  return (window.VIZMAP[lid + ':' + i] || []).map(v => {
    const [id, arg] = v.split(':'), z = VIZ[id]; if (!z) return '';
    const cap = typeof z.cap === 'function' ? z.cap(arg) : z.cap;
    return `<figure class="viz"><div class="vz-stage" data-viz="${v}"></div><figcaption><span class="vz-tag">${{a:'Անիմացիա', i:'Ինտերակտիվ', s:'Սխեմա'}[z.kind]}</span> ${cap}</figcaption></figure>`;
  }).join('');
};
window.mountViz = function(root){
  (root || document).querySelectorAll('[data-viz]:not([data-on])').forEach(el => {
    el.setAttribute('data-on', '1');
    const v = el.getAttribute('data-viz'), k = v.indexOf(':'), id = k < 0 ? v : v.slice(0, k), arg = k < 0 ? undefined : v.slice(k + 1);
    try { VIZ[id].f(el, arg); } catch (e){ console.error('viz', v, e); el.closest('figure').remove(); }
  });
};
window.VZ = {NS, RM, C, S, H, T, setT, attrs, svg, pts, arrow, axes, clamp, lerp, fmt, rnd, col, ctl, slider, seg, btn, out, anim};
})();
