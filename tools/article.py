"""Factual article draft. Not published."""

from __future__ import annotations

from tools.statements import AUDITION, ON_PICTURE, PREVIEW_LINE, PROCESSING, PROGRAM, PUBLICATION, WARNING

TITLE = "Lo-Fi Mellow Keys is a note-only MIDI study pack"
SUBTITLE = "Eight short studies of gentle voicings, a matched byte check, and a simple-synth preview that is not a master"
TAGS = ["midi", "lofi", "piano", "music-production", "composition"]
TAG_LINE = "Tags: " + ", ".join(TAGS)

PARAGRAPHS = [
    "DRAFT. " + PUBLICATION,
    TAG_LINE,
    "The pack is eight keys studies in 4/4. Tempos are integers from 60 to 90 BPM. Every study is 8 bars. That length was chosen before the notes. Sixteen bars at 60 BPM would last 64 seconds, and sixteen bars at 90 BPM would last 42.7 seconds. Both are outside the 10 to 40 second preview window. Eight bars at 72 BPM is 26.7 seconds. Each study has two keys variations. That is the core: sixteen files. Each study also has two melodic answers. Those sixteen files are references. They are not part of the core count, and they are not merged into the keys files.",
    "A variation has to change the keys. Paper Window holds a close voicing on beat 1, shortens, then holds again. Late Seventh enters on the and of 1. Open Fifths leaves the odd bars empty. Minor Ninth is the only study with a flagged pitch: C#4 in variation A, bar 6, outside D natural minor. Variation B of that study stays on C natural. Suspended Room lets the third in late, and variation B never states it. Low Register sits lower and later. Two-Note Shell is two notes on beat 4. Cadence Hold attacks twice a bar, while variation B holds one chord for two bars.",
    "Keys stay between MIDI 48 and 76, with at most four notes sounding. The highest voice is on the nominal grid. Each lower voice is 20 ticks later, and never more than 60. performed start equals nominal start plus offset. Duration is measured from the performed start. The answer offset is 0, so its pocket is the written rhythm. Offsets are not chosen independently for every note. Nothing in the generator draws a pitch, a start, or a velocity at random. C4 is 60. The resolution is 960 ticks per quarter note.",
    PROGRAM,
    PROCESSING + " The preview synth uses a sine plus a quiet triangle for the keys and a quieter sine for the answer. If the float mix is hot, one constant gain brings it down. That mapping is documented. It is not a program change.",
    "The primary preview is study 01, Paper Window, variation A, for all 8 bars: the keys file and melodic answer A together. The other studies are in the MIDI and are not in that audio file. "
    + PREVIEW_LINE
    + ". The film takes its audio from that preview file and shows the words "
    + ON_PICTURE
    + " on the picture and in the WebVTT captions.",
    AUDITION
    + " The validator reopened the MIDI bytes and compared them with the canonical score. That is a structural check. The sample peak written beside the preview is the peak of the integer mix. It is not a true-peak reading. Nothing in this build is claimed as a master.",
    "The stills are procedural illustrations of a quiet piano roll on warm paper. Longer holds are sage. They are not photographs of a session or of performers.",
    "When a public URL exists, use either the combined arrangement or the separate parts. " + WARNING,
    "Call to action: the MIDI, the matched report, and the preview belong together. Do not publish this draft to Medium, Instagram, or X from the draft files alone.",
]


def markdown() -> str:
    body = "\n\n".join(PARAGRAPHS)
    return f"# {TITLE}\n\n{SUBTITLE}\n\n{body}\n"


def plain_text() -> str:
    lines = [TITLE, "", SUBTITLE, "", *PARAGRAPHS, ""]
    return "\n".join(lines) + "\n"
