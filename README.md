# Lo-Fi Mellow Keys

Original note-only MIDI studies of gentle keys voicings. Eight studies, two variations of the keys. Each study is 8 bars, chosen before the notes. The melodic answer is cataloged separately and is not part of the core count. It is not merged into the keys files.

This repository is the pack. The GitHub repository is https://github.com/mizcausevic-dev/lofi-mellow-keys and it is public. The catalog page is https://mizcausevic-dev.github.io/lofi-mellow-keys/ .

## What you can open

- `index.html` is the file catalog. The roll is drawn from the fetched MIDI bytes, split at C4.
- `media.html` is the stills page. The film sits under the pictures.
- `midi/arrangement.mid` is a Format 1 preview arrangement of study 01, variation A: keys and melodic answer.
- Individual Format 0 parts live under `midi/`.
- `midi/validation-Cursor.json` is the report from reopening those exact bytes.
- `preview/preview.mp3` is the primary music preview. It is 26.697 seconds in the encoded file. preview, not a master.
- `film/preview.mp4` and `film/preview.vtt` are the film. On-picture and caption text is `preview, not master`.
- `art/hero.jpg` is a 1280x720 illustration. `art/square.jpg` is 1080x1080. Neither is a photograph.

Use either the combined arrangement or the separate parts. Do not stack the part files on top of the combined file.

## Studies

- s01 Paper Window: 72 BPM, 8 bars, C major, tonic reference C.
- s02 Late Shells: 66 BPM, 8 bars, F major, tonic reference F.
- s03 Open Fifths: 80 BPM, 8 bars, G major, tonic reference G.
- s04 Minor Ninth: 64 BPM, 8 bars, D natural minor, tonic reference D.
- s05 Suspended Room: 76 BPM, 8 bars, A mixolydian, tonic reference A.
- s06 Low Register: 60 BPM, 8 bars, Eb major, tonic reference Eb.
- s07 Two-Note Shell: 84 BPM, 8 bars, Bb major, tonic reference Bb.
- s08 Cadence Hold: 70 BPM, 8 bars, E major, tonic reference E.

Core files: 16. Reference files: 16.

Keys use MIDI 48 to 76, at most four notes at once. Notes below 60 are shown as the lower hand. Notes from 60 up are the upper hand. The melodic answer is monophonic, MIDI 60 to 81, a reference, and not part of the core count. C4 is 60. PPQ is 960. Meter is 4/4. Keys use a fixed roll. The highest voice has offset 0. Each lower voice is 20 ticks later, so three notes use 40, 20, and 0 from low to high, and the one four-note chord uses 60, 40, 20, and 0. performed_start = nominal_start + offset. Duration is measured from the performed start. The melodic answer offset is 0. Its pocket is in the written rhythm. Offsets are bounded and shared by voice position. They are not chosen independently for every note. Seeds identify studies and are not random draws. Generator 1.0.0.

Eight bars was chosen before the notes. Sixteen bars at 60 BPM is 64 seconds and sixteen bars at 90 BPM is 42.7 seconds, both outside 10 to 40 seconds. Eight bars at 72 BPM is 26.7 seconds. Every study uses that 8-bar container.

Pitch instability, noise, saturation, and filtering are not in the MIDI files. The renderer does not apply them.

## Preview path

The preview renders the canonical notes for `s01.keys.a` and `s01.answer.a` with `simple-synth-1.0.0`. Tempo authority is the encoded microsecond value in the MIDI, 833333 us per quarter note. Sample positions use `floor(seconds * 44100 + 0.5)` from tick 0. Intervals are not summed. Sample-exact repeating loops at an arbitrary BPM are not promised.

The synth mapping is a sine plus a quiet triangle for the keys and a quieter sine for the answer. No program changes are encoded. A conventional GM player will normally use its default piano program for pitched channels unless configured otherwise; compatible GM channel 10 percussion is treated separately. Player behavior may vary. The mapping is not encoded in the MIDI.

Encoded MP3 settings: libmp3lame, 192 kbps. Film audio is AAC at 160 kbps re-encoded from that MP3, so the decoded film audio is not byte-identical to the MP3. Film duration probe: 26.667 seconds. MP3 container probe 26.697 seconds. MP4 probe 26.667 seconds. The film ends on a video frame, so it is slightly shorter than the MP3 container. The music is the same preview, not a different excerpt. The picture is a still illustration with rasterized disclosure text. DejaVu Sans Bold from the build machine supplies the glyphs. The font file is not in this pack.

No human listening audition was performed for this build. A sample peak is recorded in the preview manifest. It is the peak of the integer mix.

## Build

From the repository root, with Python 3.11+ and ffmpeg (libmp3lame, aac, libx264):

```bash
python3 tools/build_pack.py
python3 -m http.server 43191
```

The page is static. It is served with Python's HTTP server so the MIDI and media keep working relative paths. There is no application server and no package install. Standard library only.

`build/` holds the intermediate WAV, the procedural PPM, and the film plate. Those files are gitignored. The delivered audio is the MP3.

## Checks the validator actually runs

File existence, parse, PPQ, tempo, 4/4, end-of-track boundary, note pairing, ranges, monophonic melodic answer, keys polyphony cap of four, the offset equation, note-off before note-on at a shared tick, absence of program changes and other channel messages, departure flags against the declared pitch-class set, agreement with the canonical score, and agreement between `arrangement.mid` and the two source files. A negative overlap fixture is written under this pack directory and must be rejected.

## Drafts and publication

Social captions, the X post, and the Medium article are drafts. They are not access controls. If this repository is public, the drafts are public. Do not treat them as posted to Instagram, X, or Medium.

Prepared repository description: Original note-only MIDI studies of mellow lo-fi keys, with matched validation and a simple-synth preview.

Prepared topics: midi, lofi, piano, music-production, composition.

No release tag was created. `index.html` keeps its name because players and links depend on it. This page is the file catalog the pack requires. GitHub Pages serves the `gh-pages` branch.

## Limitations

Variation compatibility is per study and is written on the page. Variation A and variation B of a study are alternatives. Pair answer A with keys A, and answer B with keys B. The arrangement is only study 01. Stacking it with the part files doubles those notes. These studies are original.
