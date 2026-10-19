<script>
(function(){
const D = window.DATA, IMG = window.IMG || {};
const $ = (s, el=document) => el.querySelector(s);
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const strip = h => h.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();
const shuffle = a => { a = a.slice(); for (let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];} return a; };

/* ---------- storage (per-viewer convenience; app works without it) ---------- */
const KEY = 'gaz-mt1-v1';
let S = { read:{}, rate:{}, known:{}, quiz:[], sup:true, draft:{}, chk:{} };
try { const raw = localStorage.getItem(KEY); if (raw) S = Object.assign(S, JSON.parse(raw)); } catch(e){}
S.draft = S.draft || {}; S.chk = S.chk || {}; S.qmode = S.qmode || 'study';
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch(e){} };

const ICONS = {
  home:'<path d="M3 10.5 12 4l9 6.5V20h-6v-6H9v6H3z"/>',
  lectures:'<path d="M4 5h6a3 3 0 0 1 3 3v12a2 2 0 0 0-2-2H4zM20 5h-6a3 3 0 0 0-3 3"/><path d="M20 5v13h-7"/>',
  questions:'<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6V14M12 17.2v.1"/>',
  cards:'<rect x="3" y="6" width="14" height="13" rx="2"/><path d="M7 3h12a2 2 0 0 1 2 2v11"/>',
  quiz:'<path d="M4 6h16M4 12h10M4 18h7"/><path d="m15 17 2 2 4-4"/>',
  exam:'<circle cx="12" cy="13" r="8"/><path d="M12 9v4l3 2M9 2h6"/>',
  diagram:'<path d="M4 3v17h17"/><path d="M5 6c4 1 7 5 9 9M8 14h12M5 9l5 5"/>'
};
const VIEWS = [
  ['home','Գլխավոր'],['lectures','Դասախոսություններ'],['questions','Գրավոր հարցեր'],
  ['exam','Քննության փորձ'],['cards','Քարտեր'],['diagram','Գազադին. հաշվիչ'],['quiz','Թեստ']
];
function buildNav(cur){
  $('#nav').innerHTML = VIEWS.map(([id,t]) => `<a href="#${id}" ${cur===id?'aria-current="page"':''}><svg class="ic" viewBox="0 0 24 24">${ICONS[id]}</svg>${t}</a>`).join('');
  $('#mnav').innerHTML = VIEWS.map(([id,t]) => `<a href="#${id}" ${cur===id?'aria-current="page"':''}>${t}</a>`).join('');
}

const lecById = id => D.lectures.find(l => l.id === +id);
const TOPICS = D.groups, TORDER = Object.keys(D.groups).map(Number);
const RATE_T = ['Չգնահատված','Չգիտեմ','Մասամբ','Գիտեմ'];
const rateOf = id => S.rate[id] || 0;

/* ---------- figures ---------- */
function figHTML(f){
  const [id, cap] = f; if (!IMG[id]) return '';
  return `<figure><div class="plate" data-zoom="${id}" role="button" tabindex="0" aria-label="Մեծացնել նկարը"><img src="${IMG[id]}" alt="${esc(cap)}" loading="lazy"></div><figcaption><b>Նկ․</b> ${esc(cap)}</figcaption></figure>`;
}
document.addEventListener('click', e => {
  const z = e.target.closest('[data-zoom]');
  if (z){ const id = z.dataset.zoom; $('#lb-img').src = IMG[id]; $('#lb-cap').textContent = z.querySelector('img').alt; $('#lb').hidden = false; }
  const go = e.target.closest('[data-go]');
  if (go){ e.preventDefault(); location.hash = go.dataset.go; }
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') $('#lb').hidden = true;
  if ((e.key === 'Enter' || e.key === ' ') && e.target.matches('[data-zoom]')) { e.preventDefault(); e.target.click(); }
});
$('#lb').addEventListener('click', e => { if (e.target.id !== 'lb-img') $('#lb').hidden = true; });
const wrapTables = html => html.replace(/<table class="tbl">/g,'<div class="tbl-wrap"><table class="tbl">').replace(/<\/table>/g,'</table></div>');

/* ---------- HOME ---------- */
function viewHome(){
  const qs = D.questions;
  const rated = qs.filter(q => rateOf(q.id)===3).length;
  const readN = D.lectures.filter(l => S.read[l.id]).length;
  const knownN = D.cards.filter((c,i) => S.known[i]).length;
  const best = S.quiz.length ? Math.max(...S.quiz.map(r => Math.round(100*r.s/r.n))) : null;
  const groups = TORDER.map(t => {
    const items = qs.filter(q => q.t===t);
    const lec = [...new Set(items.map(q=>q.l))].map(n=>'Թեմա '+n).join(', ');
    return `<div class="topic"><div><h3>${TOPICS[t]}</h3><p>${items.length} հարց · ${lec}</p></div>
      <div class="segbar" title="${items.map(q=>q.id+': '+RATE_T[rateOf(q.id)]).join('\n')}">${items.map(q=>`<i class="r${rateOf(q.id)}"></i>`).join('')}</div></div>`;
  }).join('');
  const weak = qs.filter(q => rateOf(q.id) < 3).sort((a,b) => (rateOf(a.id)||1.5) - (rateOf(b.id)||1.5)).slice(0,4);
  return `<div class="view">
    <header class="view-head"><span class="eyebrow">Առաջին միջանկյալ · թեմաներ 1–4, 6</span><h1>Ուսումնական վահանակ</h1>
    <p class="lede">Քննությունը գրավոր է․ հիմնական աշխատանքը ծրագրի հարցերին գրավոր պատասխանելն է։ Կարդացեք դասախոսությունը, գրեք պատասխանը, ստուգեք այն և գնահատեք ձեզ։ Այստեղ կտեսնեք, թե որ թեմաներն են դեռ թույլ։</p></header>
    <div class="stats">
      <div class="stat"><b>${readN}/${D.lectures.length}</b><span>թեմա կարդացված</span></div>
      <div class="stat"><b>${rated}/${qs.length}</b><span>հարց «Գիտեմ»</span></div>
      <div class="stat"><b>${knownN}/${D.cards.length}</b><span>քարտ սովորած</span></div>
      <div class="stat"><b>${qs.filter(q=>(S.draft[q.id]||'').trim()).length}/${qs.length}</b><span>հարց գրավոր պատասխանված</span></div>
    </div>
    <section class="panel"><div class="row" style="justify-content:space-between;margin-bottom:6px"><h2 style="font-size:19px">Պատրաստվածություն ըստ թեմաների</h2>
      <div class="legend"><span><i style="background:var(--good)"></i>Գիտեմ</span><span><i style="background:var(--warn)"></i>Մասամբ</span><span><i style="background:var(--bad)"></i>Չգիտեմ</span><span><i style="background:var(--sunk);border:1px solid var(--line)"></i>Չգնահատված</span></div></div>
      <div class="topics">${groups}</div></section>
    ${weak.length ? `<section class="qgroup"><h2 style="font-size:19px">Հաջորդը կրկնել</h2>${weak.map(q=>`<a class="hit" href="#questions" data-open="${q.id}" style="text-decoration:none;color:inherit"><b>${q.id} · ${RATE_T[rateOf(q.id)]}</b>${esc(q.q)}</a>`).join('')}</section>` : `<section class="panel"><b>Բոլոր հարցերը նշված են «Գիտեմ»։</b> Անցեք <a href="#exam">քննության փորձին</a>։</section>`}
    <section class="qgroup"><h2 style="font-size:19px">Ինչպես պարապել</h2>
    <div class="steps">
      <div class="step"><b>Կարդալ</b>Թեմաների կոնսպեկտ և նկարներ<a href="#lectures">Դասախոսություններ</a></div>
      <div class="step"><b>Սովորել → Գրել</b>Կարդացեք պատասխանը, հետո գրեք և ստուգեք<a href="#questions">Գրավոր հարցեր</a></div>
      <div class="step"><b>Ամրացնել</b>Սահմանումներ և թվեր քարտերով<a href="#cards">Քարտեր</a></div>
      <div class="step"><b>Փորձել</b>3 պատահական հարց, 45 րոպե<a href="#exam">Քննության փորձ</a></div>
      <div class="step"><b>Լրացուցիչ</b>${D.quiz.length} արագ թեստային հարց<a href="#quiz">Թեստ</a></div>
    </div></section>
  </div>`;
}
document.addEventListener('click', e => { const a = e.target.closest('[data-open]'); if (a) openQ = a.dataset.open; });

/* ---------- LECTURES ---------- */
let curLec = 1, lecQuery = '';
function viewLectures(){
  const l = lecById(curLec);
  const tabs = D.lectures.map(x => `<button aria-pressed="${x.id===curLec}" data-lec="${x.id}">${S.read[x.id]?'<span class="dot" title="Կարդացված"></span>':''}Թեմա ${x.id}</button>`).join('');
  let body;
  if (lecQuery.trim().length > 1){
    const q = lecQuery.trim().toLowerCase(), hits = [];
    D.lectures.forEach(L => L.sections.forEach((s,i) => { const t = strip(s.html); const k = t.toLowerCase().indexOf(q); if (k>=0 || s.h.toLowerCase().includes(q)) hits.push({L,i,s,t,k}); }));
    body = `<div class="search-hits"><p class="note">${hits.length} արդյունք «${esc(lecQuery)}»-ի համար</p>${hits.map(h => {
      const a = Math.max(0,h.k-60), frag = h.k>=0 ? (a?'…':'')+esc(h.t.slice(a,h.k+120))+'…' : esc(h.t.slice(0,140))+'…';
      const re = new RegExp(esc(lecQuery.trim()).replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'gi');
      return `<button class="hit" data-jump="${h.L.id}:${h.i}"><b>Թեմա ${h.L.id} · ${esc(h.s.h)}</b>${frag.replace(re, m=>`<mark>${m}</mark>`)}</button>`;}).join('')}</div>`;
  } else {
    body = `<article class="reader ${S.sup?'sup-on':''}">
      <header class="reader-head"><span class="print-only">Գազադինամիկա · Միջանկյալ քննություն 1</span><span class="eyebrow">Թեմա ${l.id} · ծրագրի հարցեր ${l.topics.join(', ')}</span><h2>${l.title}</h2>
      <nav class="toc">${l.sections.map((s,i)=>`<a href="#lectures" data-jump="${l.id}:${i}">${s.h}</a>`).join('')}</nav>
      <div><button type="button" class="btn small print-btn" data-print title="Տպել այս թեման A4 թղթի վրա">🖨 Տպել (A4)</button></div></header>
      ${l.sections.map((s,i) => `<section class="sec" id="s${l.id}-${i}"><h3><span class="n">${l.id}.${i+1}</span>${s.h}</h3>
        <div class="prose">${wrapTables(s.html)}</div>
        ${s.figs ? `<div class="figs">${s.figs.map(figHTML).join('')}</div>` : ''}${window.vizHTML ? vizHTML(l.id, i) : ''}</section>`).join('')}
      <footer class="reader-foot">
        <button type="button" class="btn small print-btn" data-print title="Տպել այս թեման A4 թղթի վրա">🖨 Տպել (A4)</button>
        <button class="btn ${S.read[l.id]?'':'primary'}" id="markread">${S.read[l.id]?'✓ Կարդացված է':'Նշել որպես կարդացված'}</button>
        <a class="btn" href="#questions" data-qlec="${l.id}">Հարցեր այս թեմայից</a>
        <a class="btn" href="#quiz" data-zlec="${l.id}">Թեստ այս թեմայից</a>
        ${(()=>{const k=D.lectures.indexOf(l), nx=D.lectures[k+1]; return nx?`<button class="btn" data-lec="${nx.id}">Հաջորդ թեմա →</button>`:'';})()}
      </footer></article>`;
  }
  return `<div class="view">
    <header class="view-head"><span class="eyebrow">Կոնսպեկտ</span><h1>Դասախոսություններ</h1>
    <p class="lede">Ա. Ռ. Բարսեղյանի դասախոսությունների (հայերեն թարգմանությամբ) այն թեմաները, որոնք մտնում են առաջին միջանկյալի մեջ՝ կառուցվածքավորված, բնօրինակ նկարներով (սեղմեք՝ մեծացնելու համար)։</p></header>
    <div class="row" style="justify-content:space-between">
      <input type="search" id="lecq" placeholder="Որոնել տերմին, օր․ էնթալպիա" value="${esc(lecQuery)}" style="flex:1;min-width:200px;max-width:360px">
      <label class="row" style="gap:6px;font-size:13.5px;color:var(--muted)"><input type="checkbox" id="supt" ${S.sup?'checked':''}> Ընդգծել դասագրքային լրացումները</label>
    </div>
    <div class="lec-tabs">${tabs}</div>
    ${body}
  </div>`;
}
/* ---------- print on A4 (one lecture, or questions) ---------- */
// Re-render in light colors (canvas drawings read the theme), let images load, advance animations to a full frame, print, restore.
// set/unset switch the view into its print layout and back (used by the questions print).
function printView(set, unset){
  const root = document.documentElement, prev = root.getAttribute('data-theme'), y = window.scrollY;
  root.setAttribute('data-theme', 'light'); if (set) set(); render();
  const imgs = [...document.querySelectorAll('#main img')]; imgs.forEach(i => i.loading = 'eager');
  const loaded = Promise.all(imgs.map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
  let restored = false;
  const restore = () => { if (restored) return; restored = true; window.removeEventListener('afterprint', restore);
    if (prev == null) root.removeAttribute('data-theme'); else root.setAttribute('data-theme', prev);
    if (unset) unset(); if (window.vizPrint) vizPrint.done(); render(); window.scrollTo(0, y); };
  window.addEventListener('afterprint', restore);
  Promise.race([loaded, new Promise(r => setTimeout(r, 3000))]).then(() => {
    if (window.vizPrint) vizPrint.prep();
    setTimeout(() => { window.print(); }, 150);
  });
}
function bindLectures(){
  document.querySelectorAll('[data-lec]').forEach(b => b.onclick = () => { curLec = +b.dataset.lec; lecQuery=''; render(); window.scrollTo(0,0); });
  document.querySelectorAll('[data-jump]').forEach(b => b.onclick = e => { e.preventDefault(); const [L,i] = b.dataset.jump.split(':'); curLec=+L; lecQuery=''; render(); const el = document.getElementById('s'+L+'-'+i); if (el) el.scrollIntoView({behavior:'smooth'}); });
  const q = $('#lecq'); if (q){ q.oninput = () => { lecQuery = q.value; const pos=q.selectionStart; render(); const n=$('#lecq'); n.focus(); n.setSelectionRange(pos,pos); }; }
  const st = $('#supt'); if (st) st.onchange = () => { S.sup = st.checked; save(); render(); };
  const mr = $('#markread'); if (mr) mr.onclick = () => { S.read[curLec] = !S.read[curLec]; save(); render(); };
  document.querySelectorAll('[data-qlec]').forEach(a => a.onclick = () => { qFilter = 'l'+a.dataset.qlec; });
  document.querySelectorAll('[data-zlec]').forEach(a => a.onclick = () => { quizCfg.lec = a.dataset.zlec; quiz = null; });
  document.querySelectorAll('[data-print]').forEach(b => b.onclick = () => printView());
  if (window.mountViz) mountViz();
}

/* ---------- QUESTIONS ---------- */
let openQ = null, qFilter = 'all', shown = {};
function qMatches(q){
  if (qFilter==='all') return true;
  if (qFilter[0]==='l') return q.l === +qFilter.slice(1);
  if (qFilter==='weak') return rateOf(q.id) < 3;
  return true;
}
// Key points of a model answer = its <li> items; the student ticks the ones their written answer covered.
const points = q => [...q.a.matchAll(/<li>([\s\S]*?)<\/li>/g)].map(m => m[1]);
const chk = id => (S.chk[id] = S.chk[id] || []);
function checklist(q){
  const pts = points(q), c = chk(q.id), n = pts.filter((_,k)=>c[k]).length;
  return `<div class="checklist"><div class="row" style="justify-content:space-between"><b>Ստուգեք ձեր պատասխանը․ ի՞նչ եք գրել</b><span class="mono cl-score">${n}/${pts.length}</span></div>
    ${pts.map((p,k)=>`<label class="cl-item"><input type="checkbox" data-ck="${q.id}" data-k="${k}" ${c[k]?'checked':''}><span>${p}</span></label>`).join('')}</div>`;
}
function answerSecs(q){
  const L = lecById(q.l);
  return `<div class="full-in ${S.sup?'sup-on':''}">${q.sec.map(i => { const s = L.sections[i]; return `<section class="sec"><h3><span class="n">${L.id}.${i+1}</span>${s.h}</h3><div class="prose">${wrapTables(s.html)}</div>${s.figs?`<div class="figs">${s.figs.map(figHTML).join('')}</div>`:''}</section>`; }).join('')}</div>`;
}
function fullAnswer(q, open){
  return `<details class="full" ${open?'open':''}><summary>Ամբողջական պատասխան (դասախոսության տեքստը և նկարները)</summary>
    ${answerSecs(q)}</details>`;
}
// Print layout: printQ = {ids, full}; the questions view then shows only these questions, each with its answer plan (and the full answer if full).
let printQ = null;
function qPrint(q){
  return `<article class="pq"><h3><span class="q-id">${q.id}</span><span>${esc(q.q)}</span></h3>
    <div class="answer prose">${q.a}</div>${printQ.full ? answerSecs(q) : ''}</article>`;
}
function printQuestions(ids, full){ printView(() => { printQ = {ids, full}; }, () => { printQ = null; }); }
function rateRow(q){
  const r = rateOf(q.id);
  return `<div class="rate"><span style="color:var(--muted)">Որքանո՞վ գիտեք</span>${[1,2,3].map(k=>`<button data-r="${k}" data-rq="${q.id}" aria-pressed="${r===k}">${RATE_T[k]}</button>`).join('')}</div>`;
}
function qCard(q){
  const open = openQ===q.id, r = rateOf(q.id), d = S.draft[q.id] || '';
  if (S.qmode==='study') return `<div class="q" id="q-${q.id}">
    <button class="q-head" data-tq="${q.id}" aria-expanded="${open}"><span class="q-id">${q.id}</span><span class="q-text">${esc(q.q)}</span><span class="badge r${r}">${RATE_T[r]}</span></button>
    ${open ? `<div class="q-body"><span class="eyebrow">Պատասխանի պլան</span><div class="answer prose">${q.a}</div>${fullAnswer(q,true)}
      <div class="row"><button class="btn small primary" data-tocheck="${q.id}">Սովորեցի → Ստուգել ինձ գրավոր</button><button type="button" class="btn small print-btn" data-pq1="${q.id}" title="Տպել այս հարցը պատասխանով A4 թղթի վրա">🖨 Տպել այս հարցը</button></div>${rateRow(q)}</div>` : ''}
  </div>`;
  return `<div class="q" id="q-${q.id}">
    <button class="q-head" data-tq="${q.id}" aria-expanded="${open}"><span class="q-id">${q.id}</span><span class="q-text">${esc(q.q)}</span><span class="badge r${r}">${RATE_T[r]}</span></button>
    ${open ? `<div class="q-body">
      <label class="eyebrow" for="dr-${q.id}">1 · Գրեք պատասխանը առանց նայելու</label>
      <textarea id="dr-${q.id}" data-draft="${q.id}" placeholder="Սահմանում → բացատրություն → բանաձև կամ սխեմա → օրինակներ, թվեր…">${esc(d)}</textarea>
      <div class="row" style="justify-content:space-between;font-size:13px;color:var(--muted)"><span class="wc" data-wc="${q.id}">${wc(d)}</span><span>Սևագիրը պահվում է ավտոմատ</span></div>
      ${shown[q.id] ? `<span class="eyebrow">2 · Համեմատեք</span>${checklist(q)}${fullAnswer(q)}
        <span class="eyebrow">3 · Գնահատեք ձեզ</span>${rateRow(q)}`
      : `<div><button class="btn primary small" data-show="${q.id}">Ստուգել պատասխանը</button></div>`}
    </div>` : ''}
  </div>`;
}
const wc = t => { const n = (t.trim().match(/\S+/g)||[]).length; return n ? n+' բառ' : 'Դեռ ոչինչ գրված չէ'; };
function viewQuestions(){
  const F = [['all','Բոլորը'],['weak','Չսովորածները'],...D.lectures.map(l=>['l'+l.id,'Թեմա '+l.id])];
  const groups = TORDER.map(t => {
    const items = D.questions.filter(q => q.t===t && (printQ ? printQ.ids.includes(q.id) : qMatches(q))); if (!items.length) return '';
    return `<section class="qgroup"><h2>${TOPICS[t]}</h2>${items.map(q=>printQ?qPrint(q):qCard(q)).join('')}</section>`;
  }).join('');
  if (printQ) return `<div class="view qprint"><header class="reader-head"><span class="print-only">Գազադինամիկա · Միջանկյալ քննություն 1</span><h2>Գրավոր հարցեր${printQ.full?'':'․ պատասխանների պլաններ'}</h2></header>${groups}</div>`;
  const nq = D.questions.filter(qMatches).length;
  return `<div class="view">
    <header class="view-head"><span class="eyebrow">Ծրագրի հարցաշար · 24 հարց</span><h1>Գրավոր հարցեր</h1>
    <p class="lede">Նախ <b>Սովորել</b> ռեժիմում կարդացեք հարցը և պատասխանը։ Հետո <b>Ստուգել</b> ռեժիմում գրեք պատասխանը առանց նայելու և համեմատեք հիմնական կետերի հետ։ Սեղմեք հարցի վրա՝ բացելու համար։</p></header>
    <div class="panel tip"><b>Լավ գրավոր պատասխանի կառուցվածքը</b><ol><li><b>Սահմանում</b>՝ ճշգրիտ ձևակերպմամբ (օր․ «Իզոխոր է կոչվում…»)։</li><li><b>Բանաձևեր և արտածում</b>՝ ելակետային հավասարումից մինչև վերջնական արդյունք, համարակալված քայլերով։</li><li><b>Դիագրամ</b>՝ գծեք պրոցեսը \\(p\\text{–}\\upsilon\\) կամ \\(T\\text{–}s\\) կոորդինատներում, կոմպրեսոր/տուրբին/փողրակ՝ սխեմայով։</li><li><b>Ֆիզիկական իմաստ և եզրակացություն</b>՝ ինչի վրա է ծախսվում ջերմությունը, ինչ է ցույց տալիս բանաձևը։</li></ol></div>
    <div class="modes" role="tablist">
      <button role="tab" data-qm="study" aria-selected="${S.qmode==='study'}"><b>1 · Սովորել</b><span>Կարդալ հարցերը պատասխաններով</span></button>
      <button role="tab" data-qm="check" aria-selected="${S.qmode==='check'}"><b>2 · Ստուգել</b><span>Գրել առանց նայելու, համեմատել</span></button>
    </div>
    <div class="filters">${F.map(([k,t])=>`<button data-qf="${k}" aria-pressed="${qFilter===k}">${t}</button>`).join('')}</div>
    ${nq ? `<div class="row print-row"><button type="button" class="btn small print-btn" data-pq="full" title="Հարց, պատասխանի պլան, դասախոսության տեքստը և նկարները">🖨 Տպել պատասխաններով (A4)</button><button type="button" class="btn small print-btn" data-pq="plan" title="Միայն հարցերը և պատասխանների պլանները, կարճ">🖨 Տպել միայն պլանները</button><span class="print-note">${nq} հարց՝ ընտրված ֆիլտրով</span></div>` : ''}
    ${groups || '<div class="panel">Այս ֆիլտրով հարցեր չկան։ Ընտրեք «Բոլորը»։</div>'}
  </div>`;
}
function bindQuestions(){
  document.querySelectorAll('[data-qm]').forEach(b => b.onclick = () => { S.qmode = b.dataset.qm; save(); render(); });
  document.querySelectorAll('[data-tocheck]').forEach(b => b.onclick = () => { S.qmode = 'check'; openQ = b.dataset.tocheck; shown[openQ] = false; save(); render(); document.getElementById('q-'+openQ)?.scrollIntoView({block:'start'}); });
  document.querySelectorAll('[data-qf]').forEach(b => b.onclick = () => { qFilter = b.dataset.qf; render(); });
  document.querySelectorAll('[data-tq]').forEach(b => b.onclick = () => { openQ = openQ===b.dataset.tq ? null : b.dataset.tq; render(); });
  document.querySelectorAll('[data-show]').forEach(b => b.onclick = () => { shown[b.dataset.show] = true; render(); });
  document.querySelectorAll('[data-rq]').forEach(b => b.onclick = () => { S.rate[b.dataset.rq] = +b.dataset.r; save(); render(); });
  document.querySelectorAll('[data-pq]').forEach(b => b.onclick = () => printQuestions(D.questions.filter(qMatches).map(q => q.id), b.dataset.pq==='full'));
  document.querySelectorAll('[data-pq1]').forEach(b => b.onclick = () => printQuestions([b.dataset.pq1], true));
  bindWriting();
  if (openQ){ const el = document.getElementById('q-'+openQ); if (el && !el.dataset.seen){ const r = el.getBoundingClientRect(); if (r.top<0||r.top>innerHeight-100) el.scrollIntoView({block:'start'}); } }
}

// Shared by question cards and the exam: drafts save without re-rendering (keeps focus), checkboxes update the score in place.
function bindWriting(){
  document.querySelectorAll('[data-draft]').forEach(t => t.oninput = () => {
    S.draft[t.dataset.draft] = t.value; save();
    const w = document.querySelector(`[data-wc="${t.dataset.draft}"]`); if (w) w.textContent = wc(t.value);
  });
  document.querySelectorAll('[data-ck]').forEach(b => b.onchange = () => {
    chk(b.dataset.ck)[+b.dataset.k] = b.checked; save();
    const box = b.closest('.checklist'), all = box.querySelectorAll('input'), n = [...all].filter(x=>x.checked).length;
    box.querySelector('.cl-score').textContent = n+'/'+all.length;
  });
}

/* ---------- FLASHCARDS ---------- */
let deck = null, deckLec = 'all', deckOnlyNew = false, flipped = false;
function makeDeck(){
  let idx = D.cards.map((c,i)=>i).filter(i => deckLec==='all' || D.cards[i][0]===+deckLec);
  if (deckOnlyNew) idx = idx.filter(i => !S.known[i]);
  deck = { order: shuffle(idx), pos: 0 }; flipped = false;
}
function viewCards(){
  if (!deck) makeDeck();
  const total = deck.order.length, i = deck.order[deck.pos], c = D.cards[i];
  const sel = `<select id="dlec"><option value="all">Բոլոր թեմաները</option>${D.lectures.map(l=>`<option value="${l.id}" ${deckLec==l.id?'selected':''}>Թեմա ${l.id}</option>`).join('')}</select>`;
  const known = D.cards.filter((c,k)=>S.known[k] && (deckLec==='all'||c[0]===+deckLec)).length;
  const scope = D.cards.filter(c=>deckLec==='all'||c[0]===+deckLec).length;
  return `<div class="view">
    <header class="view-head"><span class="eyebrow">${scope} քարտ · սովորած ${known}</span><h1>Քարտեր</h1>
    <p class="lede">Տերմին → սահմանում։ Սեղմեք քարտին կամ Space՝ շրջելու համար, ← «Կրկնել», → «Գիտեմ»։</p></header>
    <div class="row">${sel}<label class="row" style="gap:6px;font-size:14px"><input type="checkbox" id="donly" ${deckOnlyNew?'checked':''}> Միայն չսովորածները</label><button class="btn small" id="dshuf">Խառնել</button></div>
    ${total ? `<div class="deck">
      <div class="progress"><i style="width:${100*deck.pos/total}%"></i></div>
      <button class="card ${flipped?'flipped':''}" id="card" aria-label="Շրջել քարտը"><div class="card-in">
        <div class="face"><small>ԹԵՄԱ ${c[0]} · ${deck.pos+1}/${total}</small><div class="term">${esc(c[1])}</div><span class="hint">Սեղմեք՝ շրջելու համար</span></div>
        <div class="face back"><small>${S.known[i]?'✓ ՍՈՎՈՐԱԾ':'ՍԱՀՄԱՆՈՒՄ'}</small><div class="def">${esc(c[2])}</div></div>
      </div></button>
      <div class="deck-ctrl"><button class="btn" id="dprev" ${deck.pos?'':'disabled'}>← Նախորդ</button><button class="btn" id="dagain">Կրկնել</button><button class="btn primary" id="dknow">Գիտեմ</button></div>
    </div>` : `<div class="panel">Այս խմբում բոլոր քարտերը սովորած են։ Հանեք «Միայն չսովորածները» նշումը՝ կրկնելու համար։</div>`}
  </div>`;
}
function cardNext(knew){
  const i = deck.order[deck.pos];
  if (knew) S.known[i] = true; else { delete S.known[i]; deck.order.push(i); }
  save(); deck.pos++; flipped = false;
  if (deck.pos >= deck.order.length){ makeDeck(); }
  render();
}
function bindCards(){
  $('#dlec').onchange = e => { deckLec = e.target.value; makeDeck(); render(); };
  $('#donly').onchange = e => { deckOnlyNew = e.target.checked; makeDeck(); render(); };
  $('#dshuf').onclick = () => { makeDeck(); render(); };
  const card = $('#card'); if (!card) return;
  card.onclick = () => { flipped = !flipped; card.classList.toggle('flipped', flipped); };
  $('#dknow').onclick = () => cardNext(true);
  $('#dagain').onclick = () => cardNext(false);
  $('#dprev').onclick = () => { deck.pos = Math.max(0,deck.pos-1); flipped=false; render(); };
}
document.addEventListener('keydown', e => {
  if (route !== 'cards' || !$('#card') || e.target.matches('input,select,textarea')) return;
  if (e.key===' '){ e.preventDefault(); $('#card').click(); }
  if (e.key==='ArrowRight') cardNext(true);
  if (e.key==='ArrowLeft') cardNext(false);
});

/* ---------- QUIZ ---------- */
let quiz = null; const quizCfg = { lec:'all', n:15 };
function startQuiz(){
  let pool = D.quiz.map((q,i)=>i).filter(i => quizCfg.lec==='all' || D.quiz[i][0]===+quizCfg.lec);
  pool = shuffle(pool).slice(0, quizCfg.n==='all' ? pool.length : +quizCfg.n);
  quiz = { items: pool.map(i => ({ i, opts: shuffle(D.quiz[i][2].map((t,k)=>({t,ok:k===0}))), pick:null })), pos:0, done:false };
}
function viewQuiz(){
  const head = `<header class="view-head"><span class="eyebrow">${D.quiz.length} հարց բանկում</span><h1>Թեստ</h1></header>`;
  if (!quiz){
    const hist = S.quiz.slice(-10);
    return `<div class="view">${head}
      <div class="panel" style="display:flex;flex-direction:column;gap:16px">
        <div class="row"><label for="zlec" style="min-width:110px">Թեմա</label><select id="zlec"><option value="all">Բոլորը</option>${D.lectures.map(l=>`<option value="${l.id}" ${quizCfg.lec==l.id?'selected':''}>${l.id}. ${l.title}</option>`).join('')}</select></div>
        <div class="row"><label for="zn" style="min-width:110px">Հարցերի թիվ</label><select id="zn">${[10,15,25,'all'].map(n=>`<option value="${n}" ${quizCfg.n==n?'selected':''}>${n==='all'?'Բոլորը':n}</option>`).join('')}</select></div>
        <div><button class="btn primary" id="zstart">Սկսել թեստը</button></div>
      </div>
      ${hist.length ? `<section class="panel"><h2 style="font-size:17px;margin-bottom:10px">Վերջին արդյունքները</h2><div class="row" style="align-items:flex-end;gap:16px"><div class="hist">${hist.map(r=>`<i style="height:${Math.max(4,60*r.s/r.n)}px" title="${r.s}/${r.n} · ${r.l==='all'?'բոլորը':'թեմա '+r.l}"></i>`).join('')}</div><span class="note">${hist.map(r=>Math.round(100*r.s/r.n)+'%').join(' · ')}</span></div></section>`:''}
    </div>`;
  }
  if (quiz.done){
    const s = quiz.items.filter(x=>x.pick!==null && x.opts[x.pick].ok).length, n = quiz.items.length;
    const wrong = quiz.items.filter(x=>!x.opts[x.pick].ok);
    return `<div class="view">${head}
      <div class="panel row" style="gap:24px"><span class="score">${Math.round(100*s/n)}%</span><div><b>${s} ճիշտ ${n}-ից</b><br><span class="note">${s===n?'Կատարյալ է։':wrong.length+' սխալ․ դրանք ներքևում են՝ ճիշտ պատասխաններով։'}</span></div></div>
      ${wrong.length?`<section class="mist"><h2 style="font-size:18px">Սխալներ</h2>${wrong.map(x=>{const Q=D.quiz[x.i];return `<div><b>${esc(Q[1])}</b><br>Ձեր պատասխանը՝ ${esc(x.opts[x.pick].t)}<br>Ճիշտ է՝ <b>${esc(Q[2][0])}</b><br><span class="note">${esc(Q[3])} (Թեմա ${Q[0]})</span></div>`;}).join('')}</section>`:''}
      <div class="row"><button class="btn primary" id="zagain">Նոր թեստ</button><button class="btn" id="zsetup">Փոխել կարգավորումները</button></div></div>`;
  }
  const it = quiz.items[quiz.pos], Q = D.quiz[it.i], ans = it.pick!==null;
  return `<div class="view">${head}
    <div class="qz-top"><span>Հարց ${quiz.pos+1} / ${quiz.items.length} · Թեմա ${Q[0]}</span><span>${quiz.items.filter(x=>x.pick!==null&&x.opts[x.pick].ok).length} ճիշտ</span></div>
    <div class="progress" style="max-width:none"><i style="width:${100*quiz.pos/quiz.items.length}%"></i></div>
    <p class="qz-q">${esc(Q[1])}</p>
    <div class="qz-opts">${it.opts.map((o,k)=>`<button class="opt ${ans&&o.ok?'ok':''} ${ans&&it.pick===k&&!o.ok?'no':''}" data-pick="${k}" ${ans?'disabled':''}><span class="k">${'ԱԲԳԴ'[k]}</span><span>${esc(o.t)}</span></button>`).join('')}</div>
    ${ans?`<div class="explain"><b>${it.opts[it.pick].ok?'Ճիշտ է։':'Սխալ է։'}</b> ${esc(Q[3])}</div><div><button class="btn primary" id="znext">${quiz.pos+1<quiz.items.length?'Հաջորդը →':'Տեսնել արդյունքը'}</button></div>`:''}
  </div>`;
}
function bindQuiz(){
  if ($('#zstart')){ $('#zlec').onchange=e=>quizCfg.lec=e.target.value; $('#zn').onchange=e=>quizCfg.n=e.target.value; $('#zstart').onclick=()=>{startQuiz();render();}; }
  document.querySelectorAll('[data-pick]').forEach(b => b.onclick = () => { quiz.items[quiz.pos].pick = +b.dataset.pick; render(); });
  const nx = $('#znext'); if (nx) nx.onclick = () => {
    if (quiz.pos+1 < quiz.items.length){ quiz.pos++; } else {
      quiz.done = true; const s = quiz.items.filter(x=>x.opts[x.pick].ok).length;
      S.quiz.push({s, n:quiz.items.length, l:quizCfg.lec, t:Date.now()}); S.quiz = S.quiz.slice(-30); save();
    } render(); window.scrollTo(0,0); };
  if ($('#zagain')){ $('#zagain').onclick=()=>{startQuiz();render();}; $('#zsetup').onclick=()=>{quiz=null;render();}; }
}
document.addEventListener('keydown', e => {
  if (route!=='quiz' || !quiz || quiz.done || e.target.matches('input,select,textarea')) return;
  const k = ['1','2','3','4'].indexOf(e.key); const it = quiz.items[quiz.pos];
  if (k>=0 && it.pick===null && k<it.opts.length){ it.pick=k; render(); }
  else if (e.key==='Enter' && it.pick!==null) $('#znext')?.click();
});

/* ---------- EXAM ---------- */
let exam = null, tick = null;
function startExam(mins){
  const themes = shuffle(TORDER.slice()).slice(0,3).sort();
  exam = { qs: themes.map(t => shuffle(D.questions.filter(q=>q.t===t))[0].id), end: mins ? Date.now()+mins*60000 : null, done:false, txt:{} };
}
const fmt = ms => { const s=Math.max(0,Math.round(ms/1000)); return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0'); };
function viewExam(){
  const head = `<header class="view-head"><span class="eyebrow">Տոմս՝ 3 հարց տարբեր բաժիններից</span><h1>Քննության փորձ</h1>`;
  if (!exam) return `<div class="view">${head}<p class="lede">Ինչպես իսկական քննությունում․ 3 պատահական հարց երեք տարբեր բաժիններից, ժամաչափով։ Գրեք պատասխանները առանց նյութին նայելու։ Ավարտելուց հետո ստուգեք յուրաքանչյուրը հիմնական կետերի ցանկով, կարդացեք ամբողջական պատասխանը և գնահատեք ձեզ։ Գնահատականը կերևա «Գրավոր հարցեր» բաժնում։</p></header>
    <div class="panel row"><span>Ժամանակ՝</span><button class="btn primary" data-ex="45">45 րոպե</button><button class="btn" data-ex="30">30 րոպե</button><button class="btn" data-ex="0">Առանց ժամաչափի</button></div></div>`;
  const qs = exam.qs.map(id => D.questions.find(q=>q.id===id));
  return `<div class="view">${head}</header>
    <div class="row" style="justify-content:space-between">${exam.end&&!exam.done?`<span class="timer" id="timer">${fmt(exam.end-Date.now())}</span>`:'<span></span>'}
      ${exam.done?`<button class="btn" id="exnew">Նոր տոմս</button>`:`<button class="btn primary" id="exend">Ավարտել և ստուգել</button>`}</div>
    ${qs.map((q,k)=>`<div class="ticket"><span class="q-id">Հարց ${k+1} · №${q.id} · ${TOPICS[q.t]}</span><h3>${esc(q.q)}</h3>
      ${exam.done ? `${exam.txt[q.id]?`<div class="panel" style="white-space:pre-wrap;font-size:14.5px"><span class="eyebrow">Ձեր պատասխանը</span><br>${esc(exam.txt[q.id])}</div>`:''}
        ${checklist(q)}${fullAnswer(q)}${rateRow(q)}`
      : `<textarea id="ex-${k}" data-ext="${q.id}" placeholder="Գրեք պատասխանը այստեղ․ սահմանում, բացատրություն, բանաձև/սխեմա, թվեր…">${esc(exam.txt[q.id]||'')}</textarea>`}</div>`).join('')}
  </div>`;
}
function bindExam(){
  clearInterval(tick);
  document.querySelectorAll('[data-ex]').forEach(b => b.onclick = () => { startExam(+b.dataset.ex); render(); });
  document.querySelectorAll('[data-ext]').forEach(t => t.oninput = () => exam.txt[t.dataset.ext] = t.value);
  const fin = () => { exam.done = true; clearInterval(tick); render(); window.scrollTo(0,0); };
  if ($('#exend')) $('#exend').onclick = fin;
  if ($('#exnew')) $('#exnew').onclick = () => { exam = null; render(); };
  document.querySelectorAll('.ticket [data-rq]').forEach(b => b.onclick = () => { S.rate[b.dataset.rq] = +b.dataset.r; save(); render(); });
  bindWriting();
  if (exam && exam.end && !exam.done){
    tick = setInterval(() => { const el = $('#timer'); if (!el) return clearInterval(tick); const left = exam.end-Date.now(); el.textContent = fmt(left); el.classList.toggle('low', left<5*60000); if (left<=0) fin(); }, 1000);
  }
}

/* ---------- GAS-DYNAMIC FUNCTIONS CALCULATOR ---------- */
// Isentropic relations of an ideal gas (lecture topic 6.3): λ(M), τ, π, ε, q, y.
const G = { k:1.4, R:287.05, M:0.8, Ts:288, ps:101.325 };
const lamOfM = (M,k) => Math.sqrt((k+1)/2*M*M/(1+(k-1)/2*M*M));
const gdf = (lam,k) => {
  const tau = 1-(k-1)/(k+1)*lam*lam;
  const pi = Math.pow(Math.max(tau,0), k/(k-1)), eps = Math.pow(Math.max(tau,0), 1/(k-1));
  const q = lam*Math.pow((k+1)/2, 1/(k-1))*eps;
  return { tau, pi, eps, q, y: pi>1e-9 ? q/pi : Infinity };
};
const PX0=56, PX1=704, PY0=16, PY1=276;
function viewDiagram(){
  return `<div class="view">
    <header class="view-head"><span class="eyebrow">Հարցեր 22–24 · Թեմա 6.3</span><h1>Գազադինամիկական ֆունկցիաների հաշվիչ</h1>
    <p class="lede">Տվեք Մախի թիվը, ադիաբատի ցուցիչը և արգելակման պարամետրերը։ Հաշվիչը տալիս է բերված արագությունը, գազադինամիկական ֆունկցիաները, ձայնի տեղային և կրիտիկական արագությունները։ Օգտագործեք այն արտածումները ստուգելու և թվային խնդիրներ լուծելու համար։</p></header>
    <div class="panel" style="display:flex;flex-direction:column;gap:14px">
      <div class="gd-in">
        <label>Ադիաբատի ցուցիչ k<select id="gk">${[[1.4,'1,40 · օդ'],[1.33,'1,33 · այրման արգասիքներ'],[1.25,'1,25'],[1.67,'1,67 · միատոմ գազ']].map(([v,t])=>`<option value="${v}" ${G.k==v?'selected':''}>${t}</option>`).join('')}</select></label>
        <label>Գազային հաստատուն R, Ջ/(կգ·Կ)<input type="number" id="gR" value="${G.R}" step="0.01"></label>
        <label>Լրիվ ջերմաստիճան T*, Կ<input type="number" id="gT" value="${G.Ts}" step="1"></label>
        <label>Լրիվ ճնշում p*, կՊա<input type="number" id="gp" value="${G.ps}" step="0.1"></label>
      </div>
      <label style="display:flex;flex-direction:column;gap:4px;font-size:13px;color:var(--muted)">Մախի թիվ՝ <b class="mono" id="gMv" style="color:var(--ink);font-size:16px"></b><input type="range" id="gM" min="0" max="4" step="0.01" value="${G.M}" style="accent-color:var(--heat)"></label>
    </div>
    <div class="gd-out" id="gout"></div>
    <div class="dg-wrap"><svg class="dg gd-plot" id="gplot" viewBox="0 0 720 310" role="img" aria-label="Գազադինամիկական ֆունկցիաների գրաֆիկ"></svg></div>
    <div class="gd-leg"><span><i style="background:var(--accent)"></i>τ(λ) = T/T*</span><span><i style="background:var(--heat)"></i>π(λ) = p/p*</span><span><i style="background:var(--good)"></i>ε(λ) = ρ/ρ*</span><span><i style="background:var(--bad)"></i>q(λ)</span></div>
    <section class="panel prose" style="max-width:none"><h2 style="font-size:18px;margin-bottom:8px">Օգտագործվող բանաձևերը</h2>
      <div class="formula">\\(a=\\sqrt{kRT},\\qquad M=\\dfrac{c}{a},\\qquad a_{\\text{կր}}=\\sqrt{\\dfrac{2k}{k+1}RT^*},\\qquad \\lambda=\\dfrac{c}{a_{\\text{կր}}}\\)</div>
      <div class="formula">\\(\\lambda^2=\\dfrac{k+1}{2}\\,\\dfrac{M^2}{1+\\frac{k-1}{2}M^2},\\qquad \\tau=1-\\dfrac{k-1}{k+1}\\lambda^2,\\qquad \\pi=\\tau^{\\frac{k}{k-1}},\\qquad \\varepsilon=\\tau^{\\frac{1}{k-1}}\\)</div>
      <div class="formula">\\(q(\\lambda)=\\lambda\\left(\\dfrac{k+1}{2}\\right)^{\\frac{1}{k-1}}\\varepsilon(\\lambda),\\qquad y(\\lambda)=\\dfrac{q(\\lambda)}{\\pi(\\lambda)},\\qquad G=m\\dfrac{p^*}{\\sqrt{T^*}}\\,q(\\lambda)\\,F\\)</div>
    </section>
  </div>`;
}
const f3 = v => !isFinite(v) ? '∞' : (Math.abs(v)>=100 ? v.toFixed(1) : v.toFixed(4)).replace('.',',');
function gdUpdate(){
  const {k,R,M,Ts,ps} = G, lam = lamOfM(M,k), f = gdf(lam,k), lmax = Math.sqrt((k+1)/(k-1));
  const T = Ts*f.tau, p = ps*f.pi, a = Math.sqrt(k*R*T), c = M*a, akr = Math.sqrt(2*k/(k+1)*R*Ts);
  const m = Math.sqrt(2*k/(R*(k+1)))*Math.pow(2/(k+1),1/(k-1));
  $('#gMv').textContent = M.toFixed(2).replace('.',',') + (M<1?' · ենթաձայնային':M===1?' · ձայնային':' · գերձայնային');
  const box = (t,v) => `<div><span>${t}</span><b>${v}</b></div>`;
  $('#gout').innerHTML = [
    box('λ (բերված արագություն)', f3(lam)), box('τ(λ) = T/T*', f3(f.tau)), box('π(λ) = p/p*', f3(f.pi)), box('ε(λ) = ρ/ρ*', f3(f.eps)),
    box('q(λ)', f3(f.q)), box('y(λ) = q/π', f3(f.y)), box('T, Կ', f3(T)), box('p, կՊա', f3(p)),
    box('a = √(kRT), մ/վ', f3(a)), box('c = M·a, մ/վ', f3(c)), box('a<sub>կր</sub>, մ/վ', f3(akr)), box('λ<sub>սահմ</sub>', f3(lmax)), box('m (ծախսի գործակից)', f3(m))
  ].join('');
  // plot vs λ
  const X = l => PX0+(PX1-PX0)*l/lmax, Y = v => PY1-(PY1-PY0)*v;
  const N = 160, pts = key => Array.from({length:N+1},(_,i)=>{const l=lmax*i/N, g=gdf(l,k); return X(l).toFixed(1)+','+Y(Math.min(g[key],1.05)).toFixed(1);}).join(' ');
  const ticksX = []; for (let l=0;l<=lmax+1e-9;l+=0.2) ticksX.push(l);
  $('#gplot').innerHTML = `
    ${[0,0.2,0.4,0.6,0.8,1].map(v=>`<line class="grid" x1="${PX0}" x2="${PX1}" y1="${Y(v)}" y2="${Y(v)}"/><text class="axis" x="${PX0-8}" y="${Y(v)+4}" text-anchor="end">${String(v).replace('.',',')}</text>`).join('')}
    ${ticksX.map(l=>`<text class="axis" x="${X(l)}" y="${PY1+18}" text-anchor="middle">${l.toFixed(1).replace('.',',')}</text>`).join('')}
    <text class="axis" x="${PX1}" y="${PY1+34}" text-anchor="end">λ</text>
    <line class="ln thin" x1="${X(1)}" x2="${X(1)}" y1="${PY0}" y2="${PY1}"/><text class="axis" x="${X(1)+4}" y="${PY0+12}">λ = 1 (M = 1)</text>
    <polyline class="ln c1" points="${pts('tau')}"/><polyline class="ln c2" points="${pts('pi')}"/><polyline class="ln c3" points="${pts('eps')}"/><polyline class="ln c4" points="${pts('q')}"/>
    <line class="ln" x1="${PX0}" x2="${PX0}" y1="${PY0}" y2="${PY1}"/><line class="ln" x1="${PX0}" x2="${PX1}" y1="${PY1}" y2="${PY1}"/>
    <line class="mkl" x1="${X(lam)}" x2="${X(lam)}" y1="${PY0}" y2="${PY1}"/>
    ${['tau','pi','eps','q'].map(kk=>`<circle class="mk" cx="${X(lam)}" cy="${Y(Math.min(f[kk],1.05))}" r="5"/>`).join('')}`;
}
function bindDiagram(){
  const num = (id,key) => { const el=$(id); el.oninput = () => { const v=parseFloat(el.value); if (isFinite(v) && v>0){ G[key]=v; gdUpdate(); } }; };
  $('#gk').onchange = e => { G.k = +e.target.value; gdUpdate(); };
  num('#gR','R'); num('#gT','Ts'); num('#gp','ps');
  $('#gM').oninput = e => { G.M = +e.target.value; gdUpdate(); };
  gdUpdate();
}

/* ---------- router ---------- */
let route = 'home';
const V = { home:[viewHome,()=>{}], lectures:[viewLectures,bindLectures], questions:[viewQuestions,bindQuestions], cards:[viewCards,bindCards], quiz:[viewQuiz,bindQuiz], exam:[viewExam,bindExam], diagram:[viewDiagram,bindDiagram] };
function typeset(){ if (window.renderMathInElement) renderMathInElement($('#main'), {delimiters:[{left:'\\[',right:'\\]',display:true},{left:'\\(',right:'\\)',display:false}], throwOnError:false}); }
function render(){ buildNav(route); $('#main').innerHTML = V[route][0](); V[route][1](); typeset(); }
window.addEventListener('load', typeset);
function onHash(){
  const h = location.hash.slice(1);
  const prev = route; route = V[h] ? h : 'home';
  if (prev==='exam' && route!=='exam') clearInterval(tick);
  render(); if (prev!==route) window.scrollTo(0,0);
}
window.addEventListener('hashchange', onHash);
$('#reset').onclick = e => {
  const b = e.target;
  if (b.dataset.armed){ S = { read:{}, rate:{}, known:{}, quiz:[], sup:true, draft:{}, chk:{} }; save(); deck=null; quiz=null; exam=null; b.textContent='Զրոյացված է'; delete b.dataset.armed; render(); }
  else { b.dataset.armed='1'; b.textContent='Սեղմեք կրկին՝ հաստատելու համար'; setTimeout(()=>{ if(b.dataset.armed){delete b.dataset.armed; b.textContent='Զրոյացնել առաջընթացը';} },4000); }
};
onHash();
})();
</script>

</body></html>
