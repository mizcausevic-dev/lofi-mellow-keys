"""Booklet catalog. The roll is measured from the fetched MIDI files."""

from __future__ import annotations

import json
from pathlib import Path

from tools.screening import pack_frames, render_media
from tools.statements import AUDITION, ON_PICTURE, PREVIEW_LINE, PROCESSING, PROGRAM, PUBLICATION, WARNING


def _esc(text: object) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def write_page(path: Path, catalog: dict, report: dict, preview: dict, film: dict) -> None:
    path.write_text(render_page(catalog, report, preview, film), encoding="utf-8")
    root = path.parent
    path.with_name("media.html").write_text(render_media({
        "pack_name": catalog["pack_name"],
        "subject": "The still is a quiet piano roll on warm paper. Longer holds are sage. Short bars are graphite.",
        "colors": {
            "bg": "#efe8dc",
            "paper": "#f7f1e6",
            "ink": "#2c2824",
            "accent": "#4f6b4a",
            "muted": "#6d6560",
        },
        "frames": pack_frames(root),
        "preview_seconds": preview["seconds_encoded"],
        "film_seconds": film["duration_seconds"],
    }), encoding="utf-8")


def render_page(catalog: dict, report: dict, preview: dict, film: dict) -> str:
    rows = []
    for part in catalog["parts"]:
        kind = "core" if part["core"] else "reference"
        rows.append(
            "<tr>"
            f"<td><a href=\"{part['path']}\">{_esc(part['id'])}</a></td>"
            f"<td>{_esc(part['role'])}</td>"
            f"<td>{_esc(part['variation'])}</td>"
            f"<td>{kind}</td>"
            f"<td>{part['bpm']}</td>"
            f"<td>{part['container_bars']}</td>"
            f"<td>{part['notes']}</td>"
            "</tr>"
        )
    study_rows = []
    map_rows = []
    for study in catalog["studies"]:
        owned = [part for part in catalog["parts"] if part["study_id"] == study["id"]]
        core_ids = ", ".join(part["id"] for part in owned if part["core"])
        ref_ids = ", ".join(part["id"] for part in owned if not part["core"])
        study_rows.append(
            "<li>"
            f"<button type=\"button\" data-id=\"{study['id']}\">"
            f"{study['id'][1:]} {_esc(study['title'])}</button> "
            f"{study['bpm']} BPM, {study['bars']} bars, {_esc(study['collection_name'])}, "
            f"tonic {_esc(study['tonal_reference'])}. {study['planned_seconds']:.1f} seconds at the encoded quarter."
            "</li>"
        )
        map_rows.append(
            f"<li><strong>{study['id']}</strong> {_esc(study['title'])}. "
            f"Core: {_esc(core_ids)}. Reference: {_esc(ref_ids)}.</li>"
        )
    payload = {
        "hand_split": catalog["hand_split"],
        "studies": [
            {
                "id": study["id"],
                "title": study["title"],
                "bpm": study["bpm"],
                "bars": study["bars"],
                "collection": study["collection_name"],
                "tonic": study["tonal_reference"],
                "identity": study["identity"],
                "limitations": study["limitations"],
                "voicing": study["voicing"],
                "layering": study["layering"],
                "accent": study["accent"],
                "departures": study["departures"],
                "harmonic_rhythm": study["harmonic_rhythm"],
                "changes": study["changes"],
                "change_bars": study["change_bars"],
                "phrases": study["phrases"],
                "tempo_us": study["tempo_us"],
                "spell": study["spell"],
                "planned_seconds": study["planned_seconds"],
            }
            for study in catalog["studies"]
        ],
        "parts": [
            {
                "id": part["id"],
                "study_id": part["study_id"],
                "role": part["role"],
                "variation": part["variation"],
                "path": part["path"],
                "core": part["core"],
            }
            for part in catalog["parts"]
        ],
    }
    data = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
    seconds = f"{preview['seconds_encoded']:.2f}"
    film_seconds = f"{film['duration_seconds']:.2f}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Lo-Fi Mellow Keys</title>
  <style>
    :root {{
      --bg: #efe8dc;
      --paper: #f7f1e6;
      --ink: #2c2824;
      --sage: #4f6b4a;
      --clay: #8a6244;
      --muted: #6d6560;
      --line: rgba(44, 40, 36, .16);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; background: var(--bg); color: var(--ink);
      font-family: Georgia, "Iowan Old Style", Palatino, serif;
      line-height: 1.5;
    }}
    a {{ color: var(--sage); }}
    button, .meta, .kicker {{ font-family: ui-monospace, Menlo, Consolas, monospace; }}
    .wrap {{ width: min(880px, calc(100% - 2rem)); margin: 0 auto; padding: 28px 0 64px; }}
    header {{ display: flex; justify-content: space-between; gap: 16px; align-items: baseline; flex-wrap: wrap; }}
    .brand {{ letter-spacing: .16em; text-transform: uppercase; font-size: .72rem; color: var(--sage); text-decoration: none; }}
    nav {{ display: flex; gap: 14px; flex-wrap: wrap; font-size: .82rem; }}
    h1 {{ font-weight: 500; font-size: clamp(2.6rem, 6vw, 4.6rem); line-height: .92; margin: 18px 0 8px; }}
    h2 {{ font-weight: 500; font-size: 1.7rem; margin: 0 0 8px; }}
    .kicker {{ letter-spacing: .14em; text-transform: uppercase; color: var(--sage); font-size: .74rem; margin: 0; }}
    .lede {{ max-width: 38rem; }}
    .sheet {{ background: var(--paper); border-radius: 18px; padding: 18px 18px 8px; margin: 18px 0; }}
    .contents {{ margin: 0; padding: 0; list-style: none; }}
    .contents li {{ padding: 8px 0; border-bottom: 1px solid var(--line); }}
    button {{
      border: 1px solid var(--line); background: transparent; color: var(--ink);
      border-radius: 999px; padding: 6px 10px; cursor: pointer;
    }}
    button[aria-pressed="true"] {{ background: var(--sage); color: #f7f1e6; border-color: var(--sage); }}
    .hero img, audio, video {{ display: block; width: 100%; height: auto; }}
    .hero {{ margin: 18px 0; }}
    .hero img {{ border-radius: 16px; background: var(--paper); }}
    figcaption, .meta {{ color: var(--muted); font-size: .82rem; }}
    .switch, .phrases {{ display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0; }}
    .scroller {{ overflow-x: auto; max-width: 100%; background: var(--paper); border-radius: 16px; padding: 8px 0 12px; }}
    .ruler, .hand, .answerlane {{ position: relative; }}
    .ruler {{ height: 28px; }}
    .change {{
      position: absolute; top: 4px; height: 20px; border-left: 2px solid var(--sage);
      padding-left: 5px; font-size: 11px; white-space: nowrap; overflow: hidden;
    }}
    .hand {{ height: 120px; border-top: 1px solid var(--line); }}
    .lane-name {{
      margin: 10px 0 0; font-size: 10px; letter-spacing: .12em; text-transform: uppercase; color: var(--muted);
    }}
    .block {{ position: absolute; border-radius: 3px; min-width: 3px; }}
    .block.rh {{ background: var(--ink); }}
    .block.rh.hot, .block.lh.hot {{ background: var(--clay); }}
    .block.lh {{ background: var(--sage); }}
    .phrase-band {{
      position: absolute; top: 0; bottom: 0; background: rgba(79, 107, 74, .08); pointer-events: none;
    }}
    .answerlane {{ height: 46px; background: #e7efe2; display: none; }}
    .answerlane.on {{ display: block; }}
    .anote {{
      position: absolute; top: 16px; height: 16px; border-radius: 999px;
      background: var(--clay); color: #f7f1e6; font-size: 10px; padding: 0 4px;
    }}
    .legend {{ display: flex; gap: 14px; flex-wrap: wrap; font-size: .78rem; color: var(--muted); }}
    .swatch {{ display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 4px; }}
    .table-scroll {{ overflow-x: auto; max-width: 100%; }}
    table {{ width: 100%; border-collapse: collapse; font-size: .8rem; }}
    th, td {{ text-align: left; padding: 7px 6px; border-bottom: 1px solid var(--line); }}
    .contract {{ margin: 0; padding-left: 1.2rem; }}
    .contract li {{ margin: 6px 0; }}
    .setmap {{ margin: 0; padding-left: 1.2rem; }}
    audio, video {{ margin: 10px 0 16px; background: #1c1916; }}
    .playrow {{ display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-top: 12px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <a class="brand" href="index.html">Lo-Fi Mellow Keys</a>
      <nav>
        <a href="#studies">Studies</a>
        <a href="#roll">Roll</a>
        <a href="#files">Files</a>
        <a href="#reading">Recording</a>
        <a href="media.html">Stills</a>
        <a href="midi/arrangement.mid">Arrangement</a>
      </nav>
    </header>
    <p class="kicker">Eight studies · 8 bars · keys, then a reference answer</p>
    <h1>Lo-Fi Mellow Keys</h1>
    <p class="lede">Gentle voicings, an economical melodic answer, a small fixed roll, and one chord plan per study. The answer is a reference. It is not part of the core count.</p>
    <p class="meta">{_esc(catalog['length_choice'])}</p>
    <section id="studies">
      <h2>Studies</h2>
      <ol class="contents" id="contents">
        {''.join(study_rows)}
      </ol>
    </section>
    <article class="sheet" id="sheet">
      <p class="kicker" id="facts"></p>
      <h2 id="title">Paper Window</h2>
      <p id="identity"></p>
      <p id="rhythm"></p>
      <p id="voicing"></p>
      <p id="layering"></p>
      <p id="accent-copy"></p>
      <p class="meta" id="limits"></p>
      <p class="meta" id="departures"></p>
    </article>
    <figure class="hero">
      <img src="art/hero.jpg" width="1280" height="720" alt="Illustration of a quiet piano roll on warm paper. Longer holds are sage. Not a photograph of a studio or of performers.">
      <figcaption>Illustration, not a session photograph. The roll below is read from the MIDI, not from this picture.</figcaption>
    </figure>
    <section id="roll">
      <h2>Roll</h2>
      <p>The note positions come from the fetched MIDI. The catalog does not embed the note list.</p>
      <div class="switch">
        <button type="button" id="var-a" aria-pressed="true">Variation A</button>
        <button type="button" id="var-b" aria-pressed="false">Variation B</button>
      </div>
      <div class="phrases" id="phrases"></div>
      <div class="scroller" id="scroller">
        <div class="ruler" id="ruler"></div>
        <p class="lane-name">Upper keys, C4 and above</p>
        <div class="hand" id="right"></div>
        <p class="lane-name">Lower keys, below C4</p>
        <div class="hand" id="left"></div>
        <p class="lane-name" id="answer-label">Melodic answer, reference, not in the keys file</p>
        <div class="answerlane on" id="answerlane"></div>
      </div>
      <p class="legend">
        <span><i class="swatch" style="background:#2c2824"></i>upper keys</span>
        <span><i class="swatch" style="background:#4f6b4a"></i>lower keys</span>
        <span><i class="swatch" style="background:#8a6244"></i>velocity 64 and up</span>
        <span><i class="swatch" style="background:#8a6244"></i>answer</span>
      </p>
      <p class="meta" id="status">Reading the MIDI.</p>
      <div class="playrow">
        <button type="button" id="play">Play keys</button>
        <button type="button" id="answer-toggle" aria-pressed="true">Melodic answer</button>
        <span class="meta" id="transport-label">Space plays. J and K change study.</span>
      </div>
      <p class="meta">The play control is a browser tone for the fetched notes. It is not the preview recording.</p>
    </section>
    <section>
      <h2>File contract</h2>
      <ol class="contract">
        <li>Canonical score in <a href="score/canonical-score-Cursor.json">score/canonical-score-Cursor.json</a>.</li>
        <li>MIDI files, including <a href="midi/arrangement.mid">midi/arrangement.mid</a>.</li>
        <li>Reopened-byte validation in <a href="midi/validation-Cursor.json">midi/validation-Cursor.json</a>. Result {report['result']}.</li>
        <li>Audio preview in <a href="preview/preview.mp3">preview/preview.mp3</a>, with <a href="preview/preview-manifest-Cursor.txt">preview/preview-manifest-Cursor.txt</a>.</li>
        <li>Film in <a href="film/preview.mp4">film/preview.mp4</a> and <a href="film/preview.vtt">film/preview.vtt</a>.</li>
        <li>Stills in <a href="art/hero.jpg">art/hero.jpg</a> and <a href="art/square.jpg">art/square.jpg</a>, then the social drafts.</li>
        <li>This page is built from <a href="catalog/catalog-Cursor.json">catalog/catalog-Cursor.json</a>.</li>
      </ol>
    </section>
    <section>
      <h2>Set map</h2>
      <p>Core is keys. Reference is the melodic answer. Both variations are listed. They are alternatives, not a stack.</p>
      <ul class="setmap">{''.join(map_rows)}</ul>
    </section>
    <p>{_esc(catalog['range_statement'])}</p>
    <p>{_esc(catalog['microtiming'])}</p>
    <p>{PROCESSING}</p>
    <p>{WARNING}</p>
    <h2 id="files">Files</h2>
    <p class="meta">Validation {report['result']}. Core {catalog['core_part_count']}. References {catalog['reference_part_count']}. <a href="midi/validation-Cursor.json">validation report</a> · <a href="catalog/catalog-Cursor.json">catalog</a></p>
    <div class="table-scroll">
      <table>
        <thead><tr><th>Part</th><th>Role</th><th>Var</th><th>Count</th><th>BPM</th><th>Bars</th><th>Notes</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>
    <p class="meta">The validator checks parse, PPQ 960, tempo, 4/4, boundaries, pairing, keys range and polyphony, monophonic answer, the offset equation, departure flags, and agreement between the arrangement and the two source files.</p>
    <section id="reading">
      <p class="kicker">Recorded reading · study 01 variation A, all 8 bars</p>
      <h2>Paper Window</h2>
      <p>This MP3 is {seconds} seconds. {PREVIEW_LINE}. The film is {film_seconds} seconds and shows {ON_PICTURE}.</p>
      <audio controls preload="metadata" src="preview/preview.mp3"></audio>
      <p><a href="preview/preview.mp3">preview/preview.mp3</a></p>
      <video controls preload="metadata" poster="film/poster.jpg" width="1280" height="720">
        <source src="film/preview.mp4" type="video/mp4">
        <track kind="captions" src="film/preview.vtt" srclang="en" label="English" default>
      </video>
    </section>
    <p class="meta"><a href="articles/medium-draft-Cursor.md">Article draft</a> · <a href="articles/medium-paste-Cursor.txt">plain text</a>. Tags are on the draft. There are five.</p>
    <p>{PROGRAM}</p>
    <p>{AUDITION}</p>
    <p>{PUBLICATION}</p>
  </div>
  <script id="pack" type="application/json">{data}</script>
  <script>
    const pack = JSON.parse(document.getElementById("pack").textContent);
    const phrases = document.getElementById("phrases");
    const scroller = document.getElementById("scroller");
    const ruler = document.getElementById("ruler");
    const right = document.getElementById("right");
    const left = document.getElementById("left");
    const answerlane = document.getElementById("answerlane");
    const status = document.getElementById("status");
    let studyId = "s01";
    let variation = "a";
    let keyNotes = [];
    let answerNotes = [];
    let showAnswer = true;
    let audio = null;
    let playing = false;
    let followId = 0;
    let rollWidth = 1200;

    function study() {{
      return pack.studies.find((item) => item.id === studyId);
    }}
    function pitchName(pitch) {{
      return study().spell[pitch % 12] + (Math.floor(pitch / 12) - 1);
    }}
    function readVlq(view, offset) {{
      let value = 0;
      let byte = 0;
      do {{
        byte = view.getUint8(offset);
        offset += 1;
        value = (value << 7) | (byte & 0x7f);
      }} while (byte & 0x80);
      return [value, offset];
    }}
    function parseMidi(buffer) {{
      const view = new DataView(buffer);
      if (String.fromCharCode(view.getUint8(0), view.getUint8(1), view.getUint8(2), view.getUint8(3)) !== "MThd" || view.getUint16(12) !== 960) {{
        throw new Error("unexpected MIDI header");
      }}
      const tracks = view.getUint16(10);
      let offset = 14;
      const notes = [];
      for (let track = 0; track < tracks; track += 1) {{
        if (String.fromCharCode(view.getUint8(offset), view.getUint8(offset + 1), view.getUint8(offset + 2), view.getUint8(offset + 3)) !== "MTrk") {{
          throw new Error("missing track");
        }}
        const length = view.getUint32(offset + 4);
        offset += 8;
        const end = offset + length;
        let tick = 0;
        let running = 0;
        const open = new Map();
        while (offset < end) {{
          let delta;
          [delta, offset] = readVlq(view, offset);
          tick += delta;
          let byte = view.getUint8(offset);
          if (byte >= 0x80) {{
            running = byte;
            offset += 1;
          }}
          if (running === 0xff) {{
            offset += 1;
            let metaLen;
            [metaLen, offset] = readVlq(view, offset);
            offset += metaLen;
            continue;
          }}
          const kind = running & 0xf0;
          const data1 = byte < 0x80 ? byte : view.getUint8(offset);
          if (byte >= 0x80) offset += 1;
          let data2 = 0;
          if (kind !== 0xc0 && kind !== 0xd0) {{
            data2 = view.getUint8(offset);
            offset += 1;
          }}
          const key = (running & 0x0f) + ":" + data1;
          if (kind === 0x90 && data2 > 0) open.set(key, {{ tick: tick, velocity: data2 }});
          else if (kind === 0x80 || (kind === 0x90 && data2 === 0)) {{
            const started = open.get(key);
            if (started) {{
              notes.push({{ pitch: data1, start: started.tick, duration: tick - started.tick, velocity: started.velocity }});
              open.delete(key);
            }}
          }}
        }}
      }}
      notes.sort((a, b) => a.start - b.start || a.pitch - b.pitch);
      return notes;
    }}
    function partPath(role) {{
      const found = pack.parts.find((part) => part.study_id === studyId && part.role === role && part.variation === variation);
      if (!found) throw new Error("missing " + role);
      return found.path;
    }}
    function renderCopy() {{
      const item = study();
      document.getElementById("title").textContent = item.title;
      document.getElementById("identity").textContent = item.identity;
      document.getElementById("facts").textContent = item.id + " · " + item.bpm + " BPM · " + item.bars + " bars · " + item.collection + " · tonic " + item.tonic;
      document.getElementById("rhythm").textContent = item.harmonic_rhythm;
      document.getElementById("voicing").textContent = item.voicing;
      document.getElementById("layering").textContent = item.layering;
      document.getElementById("accent-copy").textContent = item.accent;
      document.getElementById("limits").textContent = item.limitations;
      document.getElementById("departures").textContent = item.departures.length ? item.departures.join(" ") : "No pitch in this study is flagged as a departure.";
      document.getElementById("transport-label").textContent = item.title + " " + variation.toUpperCase() + " · Space plays · J and K change study";
      for (const button of document.querySelectorAll("#contents button")) {{
        button.setAttribute("aria-pressed", button.dataset.id === studyId ? "true" : "false");
      }}
      document.getElementById("var-a").setAttribute("aria-pressed", variation === "a" ? "true" : "false");
      document.getElementById("var-b").setAttribute("aria-pressed", variation === "b" ? "true" : "false");
      phrases.innerHTML = "";
      item.phrases.forEach((phrase) => {{
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = phrase.name;
        button.addEventListener("click", () => {{
          const x = (phrase.start_bar / item.bars) * rollWidth;
          scroller.scrollTo({{ left: Math.max(0, x - 12), behavior: "smooth" }});
        }});
        phrases.appendChild(button);
      }});
    }}
    function laneNotes(host, notes, klass) {{
      host.querySelectorAll(".block, .phrase-band, .empty").forEach((node) => node.remove());
      const item = study();
      const container = item.bars * 4 * 960;
      if (!notes.length) {{
        const empty = document.createElement("p");
        empty.className = "empty lane-name";
        empty.textContent = "This hand rests in this variation.";
        host.appendChild(empty);
        return;
      }}
      const low = Math.min(...notes.map((note) => note.pitch));
      const high = Math.max(...notes.map((note) => note.pitch));
      const span = Math.max(1, high - low);
      item.phrases.forEach((phrase, index) => {{
        if (index % 2) return;
        const band = document.createElement("div");
        band.className = "phrase-band";
        band.style.left = (phrase.start_bar / item.bars) * rollWidth + "px";
        band.style.width = (phrase.bars / item.bars) * rollWidth + "px";
        host.appendChild(band);
      }});
      notes.forEach((note) => {{
        const block = document.createElement("div");
        block.className = "block " + klass + (note.velocity >= 64 ? " hot" : "");
        block.title = pitchName(note.pitch) + " · velocity " + note.velocity;
        const y = 22 + (1 - (note.pitch - low) / span) * 72;
        block.style.left = (note.start / container) * rollWidth + "px";
        block.style.width = Math.max(3, (note.duration / container) * rollWidth - 1) + "px";
        block.style.top = y + "px";
        block.style.height = (8 + (note.velocity / 127) * 14) + "px";
        host.appendChild(block);
      }});
    }}
    function draw() {{
      const item = study();
      const container = item.bars * 4 * 960;
      rollWidth = Math.max(880, item.bars * 220);
      [ruler, right, left, answerlane].forEach((node) => {{ node.style.width = rollWidth + "px"; }});
      ruler.innerHTML = "";
      let bar = 0;
      item.changes.forEach((name, index) => {{
        const span = item.change_bars[index];
        const mark = document.createElement("div");
        mark.className = "change";
        mark.textContent = name;
        mark.style.left = (bar / item.bars) * rollWidth + "px";
        mark.style.width = (span / item.bars) * rollWidth + "px";
        ruler.appendChild(mark);
        bar += span;
      }});
      const split = pack.hand_split;
      laneNotes(right, keyNotes.filter((note) => note.pitch >= split), "rh");
      laneNotes(left, keyNotes.filter((note) => note.pitch < split), "lh");
      answerlane.classList.toggle("on", showAnswer);
      document.getElementById("answer-label").hidden = !showAnswer;
      answerlane.querySelectorAll(".anote").forEach((node) => node.remove());
      if (showAnswer) {{
        answerNotes.forEach((note) => {{
          const mark = document.createElement("div");
          mark.className = "anote";
          mark.textContent = pitchName(note.pitch);
          mark.style.left = (note.start / container) * rollWidth + "px";
          answerlane.appendChild(mark);
        }});
      }}
      const lower = keyNotes.filter((note) => note.pitch < split).length;
      status.textContent = keyNotes.length + " keys notes from the file. " + lower + " are below C4. " + answerNotes.length + " answer notes.";
    }}
    async function loadStudy() {{
      stopPlayback();
      renderCopy();
      status.textContent = "Reading the MIDI.";
      try {{
        const keysRes = await fetch(partPath("keys"));
        const answerRes = await fetch(partPath("melodic-answer"));
        if (!keysRes.ok || !answerRes.ok) throw new Error("MIDI request failed");
        keyNotes = parseMidi(await keysRes.arrayBuffer());
        answerNotes = parseMidi(await answerRes.arrayBuffer());
        draw();
      }} catch (error) {{
        keyNotes = [];
        answerNotes = [];
        status.textContent = "The MIDI did not load. " + error.message;
      }}
    }}
    function freq(pitch) {{
      return 440 * Math.pow(2, (pitch - 69) / 12);
    }}
    function schedule(ctx, note, origin, amount) {{
      const item = study();
      const seconds = (tick) => tick / 960 * item.tempo_us / 1000000;
      const when = origin + seconds(note.start);
      const duration = Math.max(0.05, seconds(note.duration));
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.value = freq(note.pitch);
      const level = amount * (note.velocity / 100);
      const attack = Math.min(0.03, duration * 0.25);
      gain.gain.setValueAtTime(0.0001, when);
      gain.gain.exponentialRampToValueAtTime(Math.max(0.0002, level), when + attack);
      gain.gain.exponentialRampToValueAtTime(0.0001, when + duration);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(when);
      osc.stop(when + duration + 0.02);
    }}
    function stopPlayback() {{
      playing = false;
      cancelAnimationFrame(followId);
      if (audio) audio.close();
      audio = null;
      document.getElementById("play").textContent = "Play keys";
    }}
    function playKeys() {{
      if (!keyNotes.length) return;
      stopPlayback();
      const ctx = new AudioContext();
      audio = ctx;
      playing = true;
      document.getElementById("play").textContent = "Stop";
      const origin = ctx.currentTime + 0.05;
      keyNotes.forEach((note) => schedule(ctx, note, origin, 0.08));
      if (showAnswer) answerNotes.forEach((note) => schedule(ctx, note, origin, 0.05));
      const item = study();
      const container = item.bars * 4 * 60 / item.bpm;
      const follow = () => {{
        if (!playing || !audio) return;
        if (audio.currentTime - origin < container) followId = requestAnimationFrame(follow);
        else stopPlayback();
      }};
      follow();
    }}
    function stepStudy(direction) {{
      const index = pack.studies.findIndex((item) => item.id === studyId);
      studyId = pack.studies[(index + direction + pack.studies.length) % pack.studies.length].id;
      loadStudy();
    }}
    document.querySelectorAll("#contents button").forEach((button) => {{
      button.addEventListener("click", () => {{ studyId = button.dataset.id; loadStudy(); }});
    }});
    document.getElementById("var-a").addEventListener("click", () => {{ variation = "a"; loadStudy(); }});
    document.getElementById("var-b").addEventListener("click", () => {{ variation = "b"; loadStudy(); }});
    document.getElementById("play").addEventListener("click", () => {{ if (playing) stopPlayback(); else playKeys(); }});
    document.getElementById("answer-toggle").addEventListener("click", () => {{
      showAnswer = !showAnswer;
      document.getElementById("answer-toggle").setAttribute("aria-pressed", showAnswer ? "true" : "false");
      if (keyNotes.length) draw();
    }});
    window.addEventListener("keydown", (event) => {{
      const tag = event.target && event.target.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "AUDIO" || tag === "VIDEO") return;
      if (event.code === "Space") {{ event.preventDefault(); if (playing) stopPlayback(); else playKeys(); }}
      else if (event.key === "j" || event.key === "J") stepStudy(-1);
      else if (event.key === "k" || event.key === "K") stepStudy(1);
    }});
    loadStudy();
  </script>
</body>
</html>
"""
