"""Build the Armenian player for the narrated drawing lesson.

Run after the video renderer has written ../video/lesson.json:
    python3 video_page.py

Only the standard library is required. --lesson and --output can point to a
temporary fixture when checking the page without changing the published file.
"""
from __future__ import annotations

import argparse
from html import escape
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def stamp(seconds: float) -> str:
    value = max(0, int(seconds))
    hours, rest = divmod(value, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours}:{minutes:02}:{secs:02}" if hours else f"{minutes:02}:{secs:02}"


def finite_time(value: object, name: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise ValueError(f"Invalid {name}: {value!r}")
    return number


def render_page(lesson: dict) -> str:
    title = str(lesson.get("title") or "Ինչպես գծել կուրսայինի բոլոր թերթերը")
    duration = finite_time(lesson["duration"], "duration")
    if duration <= 0:
        raise ValueError("The video duration must be positive")
    chapters = lesson["chapters"]
    scenes = lesson["scenes"]
    if not chapters or not scenes:
        raise ValueError("A lesson needs chapters and scenes")
    ids = {str(c["id"]) for c in chapters}
    if len(ids) != len(chapters):
        raise ValueError("Duplicate chapter IDs")
    previous = -1.0
    for scene in scenes:
        start = finite_time(scene["start"], "scene start")
        length = finite_time(scene["duration"], "scene duration")
        if str(scene["chapter"]) not in ids or start < previous or start + length > duration + 1:
            raise ValueError(f"Invalid scene timeline: {scene['id']}")
        previous = start

    chapter_buttons = []
    transcript = []
    data_chapters = []
    data_scenes = []
    for index, chapter in enumerate(chapters):
        cid = str(chapter["id"])
        start = finite_time(chapter["start"], "chapter start")
        end = finite_time(chapter["end"], "chapter end")
        if start >= end or end > duration + 1:
            raise ValueError(f"Invalid chapter timeline: {cid}")
        ctitle = str(chapter["title"])
        chapter_buttons.append(
            f'<button class="chapter" type="button" data-seek="{start:.3f}" data-chapter="{escape(cid, quote=True)}">'
            f'<span class="chapter-number">{index + 1:02}</span>'
            f'<span class="chapter-copy"><b>{escape(ctitle)}</b><span>{stamp(start)} · {stamp(end - start)}</span></span>'
            '<span class="play-mark" aria-hidden="true">▶</span></button>'
        )
        records = []
        for scene in scenes:
            if str(scene["chapter"]) != cid:
                continue
            scene_id = str(scene["id"])
            scene_start = float(scene["start"])
            scene_title = str(scene["title"])
            speech = str(scene.get("speech", ""))
            note = str(scene.get("note", ""))
            formula = str(scene.get("formula", ""))
            extra = (f'<p class="scene-note">{escape(note)}</p>' if note else "")
            extra += (f'<p class="formula">{escape(formula)}</p>' if formula else "")
            records.append(
                f'<article class="scene" id="scene-{escape(scene_id, quote=True)}" data-scene="{escape(scene_id, quote=True)}">'
                f'<button type="button" class="scene-seek" data-seek="{scene_start:.3f}">'
                f'<time>{stamp(scene_start)}</time><span>{escape(scene_title)}</span>'
                '<span aria-hidden="true">↗</span></button>'
                f'<p class="speech">{escape(speech)}</p>{extra}</article>'
            )
            data_scenes.append(dict(id=scene_id, chapter=cid, title=scene_title,
                                    start=scene_start, duration=float(scene["duration"])))
        transcript.append(
            f'<details class="transcript-chapter" data-transcript-chapter="{escape(cid, quote=True)}">'
            f'<summary><span>{index + 1:02} · {escape(ctitle)}</span><span class="chapter-time">{stamp(start)}</span></summary>'
            f'<div class="scene-list">{"".join(records)}</div></details>'
        )
        data_chapters.append(dict(id=cid, title=ctitle, start=start, end=end))

    payload = json.dumps(dict(duration=duration, chapters=data_chapters, scenes=data_scenes),
                         ensure_ascii=False).replace("<", "\\u003c")
    return (TEMPLATE.replace("@@TITLE@@", escape(title))
            .replace("@@DURATION@@", stamp(duration))
            .replace("@@CHAPTER_COUNT@@", str(len(chapters)))
            .replace("@@SCENE_COUNT@@", str(len(scenes)))
            .replace("@@CHAPTERS@@", "".join(chapter_buttons))
            .replace("@@TRANSCRIPT@@", "".join(transcript))
            .replace("@@DATA@@", payload))


TEMPLATE = r'''<!doctype html>
<html lang="hy">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Կուրսայինի բոլոր չորս գծագրերի հայերեն տեսադասը՝ քայլերի պատճառներով, չափերով և ստուգումներով։">
<meta name="theme-color" content="#142d3b">
<title>@@TITLE@@ · Տարբերակ 1</title>
<style>
:root{color-scheme:light;--bg:#f4f2eb;--paper:#fffef9;--ink:#192b35;--muted:#536771;--line:#d5dedc;--accent:#126b64;--soft:#e7f3ed;--night:#142d3b;--gold:#f0cf7c}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:22px}
body{margin:0;color:var(--ink);background:var(--bg);font:16px/1.6 "Noto Sans Armenian","Arial Unicode MS",system-ui,sans-serif}
a{color:var(--accent);text-underline-offset:3px}
button,input,select{font:inherit}
button,a,input,select,summary{-webkit-tap-highlight-color:transparent}
button{cursor:pointer}
:focus-visible{outline:3px solid #c38313;outline-offset:4px}
.skip{position:absolute;left:16px;top:-100px;z-index:10;background:var(--paper);padding:10px 14px;border-radius:8px}
.skip:focus{top:12px}
.wrap{width:min(1400px,100%);margin:auto;padding:28px 30px 64px}
.breadcrumbs{display:flex;flex-wrap:wrap;align-items:center;gap:8px;font-size:.9rem;color:var(--muted);margin-bottom:26px}
.breadcrumbs a{text-decoration:none}
.eyebrow{font-size:.76rem;font-weight:750;letter-spacing:.04em;color:var(--accent);margin:0 0 8px}
h1{font-size:clamp(1.65rem,3.1vw,2.65rem);line-height:1.3;max-width:1030px;margin:0 0 14px;letter-spacing:-.025em}
.lead{font-size:1.06rem;max-width:980px;color:var(--muted);margin:0 0 20px}
.meta{display:flex;flex-wrap:wrap;gap:8px 18px;color:var(--muted);font-size:.88rem;margin-bottom:25px}
.meta span{display:inline-flex;align-items:center;gap:7px}
.meta i{width:5px;height:5px;border-radius:50%;background:var(--accent)}
.lesson-layout{display:grid;grid-template-columns:minmax(0,1fr) 330px;gap:18px;align-items:start}
.player-card{min-width:0;border-radius:16px;background:var(--night);color:#fff;overflow:hidden;box-shadow:0 12px 35px #142d3b16}
.video-wrap{background:#08171e;aspect-ratio:16/9}
video{display:block;width:100%;height:100%;background:#08171e}
video::cue{font:500 1em "Noto Sans Armenian",sans-serif;background:#08171ee8;color:#fff}
.under-player{padding:17px 20px 18px}
.current-label{font-size:.74rem;color:#b9d0d7;display:block;margin-bottom:4px}
#current-title{font-size:1rem;line-height:1.5;margin:0;font-weight:650;min-height:1.5em}
.player-toolbar{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;margin-top:15px;padding-top:13px;border-top:1px solid #ffffff25}
.rate{display:flex;align-items:center;gap:10px;font-size:.87rem;color:#d7e3e7}
select{border:1px solid #78939c;background:#173946;color:white;border-radius:7px;padding:4px 7px}
select option{background:var(--night);color:white}
.download{display:inline-flex;align-items:center;gap:9px;color:var(--gold);font-size:.88rem;font-weight:600;text-decoration:none}
.download:hover{text-decoration:underline}
#player-message{font-size:.86rem;margin:10px 0 0;color:#f4db9b}
#player-message:empty{display:none}
.chapter-panel{border:1px solid var(--line);background:var(--paper);border-radius:16px;padding:18px 13px 12px}
.panel-heading{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:0 7px;margin-bottom:14px}
h2{font-size:1.35rem;line-height:1.4;letter-spacing:-.01em;margin:0 0 12px}
.panel-heading h2{font-size:1rem;margin:0}
#position{font-size:.8rem;color:var(--muted);font-variant-numeric:tabular-nums}
.progress{height:4px;border-radius:3px;background:#e3eae5;overflow:hidden;margin:0 7px 14px}
.progress span{display:block;width:0;height:100%;background:var(--accent);transition:width .15s linear}
.chapter{display:flex;gap:11px;align-items:flex-start;width:100%;text-align:left;background:transparent;color:var(--ink);border:1px solid transparent;border-radius:10px;padding:11px 7px;margin:3px 0}
.chapter:hover{background:#f1f4ed}
.chapter[aria-current="true"]{background:var(--soft);border-color:#b8d8ca}
.chapter-number{display:grid;place-items:center;width:27px;height:27px;flex:0 0 27px;border:1px solid var(--line);border-radius:7px;font-size:.75rem;color:var(--muted);font-variant-numeric:tabular-nums;margin-top:1px}
.chapter[aria-current="true"] .chapter-number{background:var(--accent);border-color:var(--accent);color:white}
.chapter-copy{display:grid;gap:4px;flex:1;min-width:0}
.chapter-copy b{font-size:.88rem;font-weight:650;line-height:1.5}
.chapter-copy>span{font-size:.75rem;color:var(--muted);font-variant-numeric:tabular-nums}
.play-mark{font-size:.65rem;color:var(--accent);align-self:center}
.learn-note{display:flex;gap:13px;padding:18px 20px;border:1px solid var(--line);background:var(--paper);border-radius:12px;margin:21px 0 31px;max-width:1060px;font-size:.92rem;color:var(--muted)}
.learn-note b{display:block;color:var(--ink);margin-bottom:3px}
.learn-note p{margin:0}
.note-mark{flex:0 0 28px;color:var(--accent);font-size:1.25rem;line-height:1.4}
.below-layout{display:grid;grid-template-columns:minmax(0,1fr) 330px;gap:28px;align-items:start}
.section-intro{color:var(--muted);font-size:.92rem;margin:0 0 18px}
.search-label{display:block;font-size:.86rem;font-weight:650;margin-bottom:7px}
.search-row{display:flex;gap:8px;align-items:center}
input[type=search]{width:100%;min-width:0;border:1px solid #aabdb9;background:var(--paper);border-radius:9px;padding:10px 12px;color:var(--ink)}
.clear-search{border:1px solid var(--line);background:var(--paper);border-radius:8px;color:var(--muted);padding:9px 11px;font-size:.85rem;flex-shrink:0}
#search-status{font-size:.83rem;color:var(--muted);min-height:1.5em;margin:8px 0 16px}
.transcript-chapter{border:1px solid var(--line);border-radius:11px;background:var(--paper);margin:11px 0;overflow:hidden}
summary{cursor:pointer;display:flex;align-items:center;gap:12px;padding:16px 17px;list-style:none;font-size:.95rem;font-weight:650}
summary::-webkit-details-marker{display:none}
summary::before{content:"+";width:17px;flex-shrink:0;color:var(--accent);font-size:1.2rem;line-height:1}
details[open]>summary::before{content:"−"}
summary .chapter-time{font-size:.8rem;color:var(--muted);margin-left:auto;font-weight:400;font-variant-numeric:tabular-nums;flex-shrink:0}
.scene-list{border-top:1px solid var(--line)}
.scene{padding:15px 18px 17px;border-bottom:1px solid #e1e7e2}
.scene:last-child{border-bottom:0}
.scene.is-current{background:#f0f7ee;box-shadow:inset 3px 0 var(--accent)}
.scene-seek{display:flex;align-items:baseline;gap:12px;width:100%;border:0;background:transparent;padding:0;color:var(--ink);text-align:left;font-size:.93rem;font-weight:650;line-height:1.6}
.scene-seek time{color:var(--accent);font-size:.78rem;font-weight:650;font-variant-numeric:tabular-nums;flex:0 0 47px}
.scene-seek>span:nth-child(2){flex:1}
.scene-seek>span:last-child{color:var(--accent);font-size:.85rem}
.speech{font-size:.9rem;margin:9px 0 0;color:#415761;line-height:1.85}
.scene-note{font-size:.83rem;color:var(--accent);margin:10px 0 0;padding-left:11px;border-left:2px solid #99bfb0}
.formula{font-size:.86rem;line-height:1.8;overflow-wrap:anywhere;background:#eef2e9;border-radius:6px;margin:10px 0 0;padding:7px 10px;color:#293e46}
.resources{background:#e7ece5;border:1px solid #d2dcd2;border-radius:13px;padding:21px 20px}
.resources h2{font-size:1rem}
.resources p{font-size:.86rem;color:var(--muted);margin:0 0 16px}
.resources a{display:block;padding:10px 0;border-top:1px solid #cbd7cd;text-decoration:none;font-size:.88rem}
.resources a:hover{text-decoration:underline}
.resources a b{display:block;font-weight:650}
.resources a span{display:block;color:var(--muted);font-size:.8rem;margin-top:1px}
.return-link{display:block;margin-top:17px;font-size:.87rem}
footer{padding-top:30px;margin-top:36px;border-top:1px solid var(--line);color:var(--muted);font-size:.82rem}
[hidden]{display:none!important}
@media(max-width:1050px){.lesson-layout{grid-template-columns:minmax(0,1fr) 285px}.below-layout{grid-template-columns:minmax(0,1fr) 285px}.wrap{padding-left:22px;padding-right:22px}}
@media(max-width:820px){.lesson-layout,.below-layout{grid-template-columns:1fr}.chapter-panel{padding:17px 15px}.chapter-list{display:grid;grid-template-columns:1fr 1fr;gap:4px 8px}.chapter{height:100%}.resources{max-width:none}.learn-note{margin-bottom:27px}.breadcrumbs{margin-bottom:20px}}
@media(max-width:520px){.wrap{padding:20px 13px 42px}.chapter-list{grid-template-columns:1fr}.chapter-panel{padding:16px 12px}.chapter{padding:10px 8px}.player-card{border-radius:11px}.under-player{padding:14px}.lead{font-size:.96rem}.meta{gap:6px 13px}.learn-note{padding:14px;gap:9px}.scene{padding:14px 12px}.scene-seek{gap:8px}.scene-seek time{flex-basis:43px}.speech{font-size:.87rem}summary{padding:14px 12px;font-size:.87rem}.chapter-time{display:none}.search-row{align-items:stretch}.clear-search{padding:8px}.breadcrumbs{font-size:.82rem}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.progress span{transition:none}}
@media print{body{font-size:10pt;background:white}.wrap{max-width:none;padding:0}.skip,.lesson-layout,.search-row,.search-label,#search-status,.scene-seek>span:last-child,.return-link{display:none}.below-layout{display:block}.lead{font-size:10pt}.learn-note,.resources,.transcript-chapter{border-radius:0;break-inside:avoid}details .scene-list{display:block}summary::before{content:none}h1{font-size:20pt}.scene{break-inside:avoid}.resources{margin-top:20pt}.transcript-chapter{break-inside:auto}.scene-note,.formula{font-size:9pt}}
</style>
</head>
<body>
<a class="skip" href="#lesson-video">Անցնել տեսանյութին</a>
<div class="wrap">
  <nav class="breadcrumbs" aria-label="Նավարկում"><a href="../../index.html">Համալսարան</a><span aria-hidden="true">/</span><a href="index.html">Կուրսային աշխատանք</a><span aria-hidden="true">/</span><span>Տեսադաս</span></nav>
  <header>
    <p class="eyebrow">ՄՄՏ · ԱՌԱՋԱԴՐԱՆՔ 2 · ՏԱՐԲԵՐԱԿ 1</p>
    <h1>@@TITLE@@</h1>
    <p class="lead">Գծում ենք բոլոր չորս թերթերը՝ բացատրելով յուրաքանչյուր կառուցման հիմքը։ Որտեղի՞ց վերցնել չափը, ինչո՞ւ է գիծն այս ուղղությամբ և ինչպե՞ս ստուգել արդյունքը։</p>
    <div class="meta"><span><i aria-hidden="true"></i>Հայերեն բացատրություն</span><span>@@DURATION@@ տևողություն</span><span>@@CHAPTER_COUNT@@ բաժին · @@SCENE_COUNT@@ քայլ</span></div>
  </header>
  <main>
    <div class="lesson-layout">
      <section class="player-card" aria-label="Ուսուցողական տեսանյութ">
        <div class="video-wrap">
          <video id="lesson-video" controls playsinline preload="metadata" poster="video/poster.jpg" aria-label="@@TITLE@@">
            <source src="video/drawing-guide.mp4" type="video/mp4">
            <track kind="subtitles" src="video/drawing-guide.hy.vtt" srclang="hy" label="Հայերեն">
            Ձեր դիտարկիչը չի ցուցադրում տեսանյութը։ <a href="video/drawing-guide.mp4">Ներբեռնեք այն այստեղից</a>։
          </video>
        </div>
        <div class="under-player">
          <span class="current-label">Ընթացիկ քայլը</span><p id="current-title" aria-live="polite">Սկսենք առաջին գծից</p>
          <div class="player-toolbar">
            <label class="rate" for="playback-rate">Արագություն<select id="playback-rate"><option value="0.75">0,75×</option><option value="1" selected>1×</option><option value="1.25">1,25×</option><option value="1.5">1,5×</option><option value="2">2×</option></select></label>
            <a class="download" href="video/drawing-guide.mp4" download>↓ Ներբեռնել տեսանյութը</a>
          </div>
          <p id="player-message" role="status"></p>
        </div>
      </section>
      <aside class="chapter-panel" aria-label="Տեսադասի բաժիններ">
        <div class="panel-heading"><h2>Ընտրիր բաժինը</h2><span id="position">00:00 / @@DURATION@@</span></div>
        <div class="progress" role="progressbar" aria-label="Դիտման ընթացքը" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span id="progress-fill"></span></div>
        <div class="chapter-list">@@CHAPTERS@@</div>
      </aside>
    </div>
    <div class="learn-note"><span class="note-mark" aria-hidden="true">↳</span><div><b>Դիտիր, կանգնեցրու, հետո գծիր։</b><p>Յուրաքանչյուր կառուցումից հետո կարող ես դադար տալ և նույն քայլը կատարել թղթի վրա։ Բաժինները կամ ներքևի ժամանակային նշումները սեղմելով՝ անմիջապես կանցնես անհրաժեշտ հատվածին։</p></div></div>
    <div class="below-layout">
      <section aria-labelledby="transcript-title">
        <h2 id="transcript-title">Գտիր անհրաժեշտ բացատրությունը</h2>
        <p class="section-intro">Բացիր բաժինը կամ որոնիր կետը, մեծությունը կամ բանաձևը։ Յուրաքանչյուր քայլի ժամանակային նշումը բացում է հենց այդ հատվածը։</p>
        <label class="search-label" for="transcript-search">Որոնել տեսադասի տեքստում</label>
        <div class="search-row"><input id="transcript-search" type="search" placeholder="Օրինակ՝ արագություն, նմանություն, μ, ինտեգրում" autocomplete="off" aria-controls="transcript"><button class="clear-search" id="clear-search" type="button">Մաքրել</button></div>
        <p id="search-status" role="status">Բոլոր @@SCENE_COUNT@@ քայլերը</p>
        <div id="transcript">@@TRANSCRIPT@@</div>
      </section>
      <aside>
        <div class="resources">
          <h2>Թղթի վրա գծելու համար</h2>
          <p>Տեսադասի պատկերները կառուցումը հասկանալու համար են։ Ճշգրիտ չափերի համար առանձին PDF-ը տպիր նշված չափի թղթի վրա՝ <b>100% / իրական չափ</b>, անջատելով «տեղավորել էջում» տարբերակը։</p>
          <a href="chertej_A3_1.pdf"><b>Թերթ 1 · A3</b><span>Դիրքեր և արագացումների պլան</span></a>
          <a href="chertej_A3_2.pdf"><b>Թերթ 2 · A3</b><span>Արագությունների ութ պլանները</span></a>
          <a href="chertej_A4_graf.pdf"><b>Թերթ 3 · A4</b><span>Մոմենտ, աշխատանք և էներգիա</span></a>
          <a href="chertej_A3_4.pdf"><b>Թերթ 4 · A3</b><span>Իներցիայի մոմենտի գրաֆիկը</span></a>
          <a href="bacatrutyun.html"><b>Բացատրությունը՝ կարդալու համար</b><span>Նշանակումներ, բանաձևեր և ինքնաստուգում</span></a>
          <a href="tetr.html"><b>Տետրում գրելու</b><span>Մաքուր լուծումը՝ էջ 10–22</span></a>
        </div>
        <a class="return-link" href="TMM_Variant1.html#overview">← Աշխատանքի ընդհանուր հերթականությունը</a>
      </aside>
    </div>
  </main>
  <footer>Մեխանիզմների և մեքենաների տեսություն · Տարբերակ 1<br>Հայերեն սինթեզված ձայն՝ <a href="https://huggingface.co/davit312/piper-TTS-Armenian">Gor · Piper</a></footer>
</div>
<script id="lesson-data" type="application/json">@@DATA@@</script>
<script>
(() => {
  'use strict';
  const lesson = JSON.parse(document.getElementById('lesson-data').textContent);
  const video = document.getElementById('lesson-video');
  const message = document.getElementById('player-message');
  const chapterButtons = [...document.querySelectorAll('.chapter')];
  const sceneNodes = [...document.querySelectorAll('.scene')];
  const sceneById = new Map(sceneNodes.map(node => [node.dataset.scene, node]));
  const progress = document.querySelector('.progress');
  const fill = document.getElementById('progress-fill');
  const title = document.getElementById('current-title');
  const rate = document.getElementById('playback-rate');
  const search = document.getElementById('transcript-search');
  const details = [...document.querySelectorAll('.transcript-chapter')];
  const status = document.getElementById('search-status');
  let currentSceneId = null;
  function stamp(value) {
    const t = Math.max(0, Math.floor(value || 0)), h = Math.floor(t / 3600);
    const m = Math.floor(t % 3600 / 60), s = t % 60;
    return (h ? h + ':' : '') + String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
  }
  function update() {
    const t = video.currentTime || 0;
    const duration = Number.isFinite(video.duration) && video.duration > 0 ? video.duration : lesson.duration;
    const percent = Math.max(0, Math.min(100, t / duration * 100));
    fill.style.width = percent + '%';
    progress.setAttribute('aria-valuenow', String(Math.round(percent)));
    document.getElementById('position').textContent = stamp(t) + ' / ' + stamp(duration);
    let chapter = lesson.chapters.find(c => t >= c.start && t < c.end);
    if (!chapter && t >= lesson.duration) chapter = lesson.chapters[lesson.chapters.length - 1];
    chapterButtons.forEach(button => {
      if (chapter && button.dataset.chapter === chapter.id) button.setAttribute('aria-current','true');
      else button.removeAttribute('aria-current');
    });
    let scene = null;
    for (const item of lesson.scenes) { if (item.start <= t) scene = item; else break; }
    if (scene && scene.id !== currentSceneId) {
      if (currentSceneId && sceneById.has(currentSceneId)) sceneById.get(currentSceneId).classList.remove('is-current');
      currentSceneId = scene.id;
      title.textContent = scene.title;
      const node = sceneById.get(scene.id);
      if (node) node.classList.add('is-current');
    }
  }
  function seekTo(seconds, play) {
    const point = Math.max(0, Math.min(lesson.duration - .1, Number(seconds) || 0));
    const apply = () => {
      video.currentTime = point;
      update();
      if (play) video.play().then(() => { message.textContent = ''; }).catch(() => {
        message.textContent = 'Հատվածն ընտրված է։ Սեղմիր տեսանյութի նվագարկման կոճակը։';
      });
    };
    if (video.readyState >= 1) apply();
    else { video.addEventListener('loadedmetadata', apply, {once:true}); video.load(); }
    history.replaceState(null, '', '#t=' + Math.floor(point));
  }
  document.querySelectorAll('[data-seek]').forEach(button => button.addEventListener('click', () => {
    seekTo(button.dataset.seek, true);
    video.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block:'center'});
  }));
  rate.addEventListener('change', () => { video.playbackRate = Number(rate.value); });
  video.addEventListener('ratechange', () => {
    if ([...rate.options].some(option => Number(option.value) === video.playbackRate)) rate.value = String(video.playbackRate);
  });
  video.addEventListener('timeupdate', update);
  video.addEventListener('durationchange', update);
  video.addEventListener('loadedmetadata', update);
  video.addEventListener('error', () => {
    message.textContent = 'Տեսանյութը չի բեռնվել։ Փորձիր նորից կամ օգտվիր ներբեռնման հղումից։';
  });
  const normalized = value => value.normalize('NFKC').toLocaleLowerCase('hy');
  const searchable = new Map(sceneNodes.map(node => [node, normalized(node.textContent)]));
  function filter() {
    const query = normalized(search.value.trim());
    let visible = 0;
    sceneNodes.forEach(node => {
      node.hidden = !!query && !searchable.get(node).includes(query);
      if (!node.hidden) visible++;
    });
    details.forEach(group => {
      group.hidden = ![...group.querySelectorAll('.scene')].some(node => !node.hidden);
      if (query && !group.hidden) group.open = true;
    });
    status.textContent = query ? (visible ? 'Գտնվել է ' + visible + ' քայլ' : 'Համընկնում չկա։ Փորձիր այլ բառ կամ նշան։') : 'Բոլոր ' + lesson.scenes.length + ' քայլերը';
  }
  search.addEventListener('input', filter);
  document.getElementById('clear-search').addEventListener('click', () => { search.value = ''; filter(); search.focus(); });
  const deepLink = location.hash.match(/^#t=(\d+(?:\.\d+)?)$/);
  if (deepLink) seekTo(Number(deepLink[1]), false);
  update();
})();
</script>
</body>
</html>
'''


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", type=Path, default=ROOT / "video" / "lesson.json")
    parser.add_argument("--output", type=Path, default=ROOT / "gceri_video.html")
    args = parser.parse_args()
    page = render_page(json.loads(args.lesson.read_text(encoding="utf-8")))
    assert "@@" not in page
    args.output.write_text(page, encoding="utf-8")
    print(f"Written {args.output.name} ({len(page):,} characters)")
