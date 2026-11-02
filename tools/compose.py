"""Original lo-fi keys studies.

Container lengths were chosen before any note was written. Every study is
8 bars of 4/4. Sixteen bars at 60 BPM would last 64 seconds, and sixteen bars
at 90 BPM would last 42.7 seconds. Both sit outside the 10 to 40 second preview
window, so 8 bars was fixed first. Eight bars at 72 BPM last 26.7 seconds.

Nothing in this module draws a note at random. Seeds name studies. Keys use a
fixed roll: the highest voice is on the nominal grid, and each lower voice is
20 ticks later, never more than 60. performed_start = nominal_start + offset.
Duration is measured from the performed start. The melodic answer uses offset
0. Its pocket is the written rhythm.

The melodic answer is a reference part. It is not part of the core count.
"""

from __future__ import annotations

from tools.midi_io import BAR_TICKS_4_4, PPQ, bpm_to_us, effective_bpm

GENERATOR_VERSION = "1.0.0"
PACK_ID = "lofi-mellow-keys"
PACK_NAME = "Lo-Fi Mellow Keys"
BAR = BAR_TICKS_4_4
HAND_SPLIT = 60
ROLL = 20
ALLOWED_OFFSETS = (0, 20, 40, 60)


class Part:
    def __init__(self, study, part_id, role, variation, core, channel, slug, mono, poly, lo, hi):
        self.study = study
        self.part_id = part_id
        self.role = role
        self.variation = variation
        self.core = core
        self.channel = channel
        self.file_slug = slug
        self.monophonic = mono
        self.max_poly = poly
        self.lo = lo
        self.hi = hi
        self.container_ticks = study["bars"] * BAR
        self.notes = []

    def add(self, nominal, duration, pitch, velocity, offset=0, departure=False):
        if offset not in ALLOWED_OFFSETS:
            raise ValueError(f"{self.part_id} offset {offset}")
        if self.role == "melodic-answer" and offset != 0:
            raise ValueError(f"{self.part_id} answer offset")
        performed = nominal + offset
        end = performed + duration
        if nominal < 0 or performed < 0 or duration <= 0 or end > self.container_ticks:
            raise ValueError(f"{self.part_id} boundary {nominal}+{offset}+{duration}")
        if performed != nominal + offset:
            raise ValueError(f"{self.part_id} offset math")
        if not self.lo <= pitch <= self.hi:
            raise ValueError(f"{self.part_id} pitch {pitch}")
        if not 1 <= velocity <= 127:
            raise ValueError(f"{self.part_id} velocity {velocity}")
        active = 1
        for other in self.notes:
            o0 = other["performed_start"]
            o1 = o0 + other["duration"]
            if performed < o1 and o0 < end:
                if other["pitch"] == pitch or self.monophonic:
                    raise ValueError(f"{self.part_id} overlap {pitch}@{performed}")
                active += 1
        if active > self.max_poly:
            raise ValueError(f"{self.part_id} poly {active}")
        self.notes.append({
            "nominal_start": nominal,
            "offset": offset,
            "performed_start": performed,
            "duration": duration,
            "pitch": pitch,
            "velocity": velocity,
            "channel": self.channel,
            "departure": departure,
        })

    def finish(self):
        ordered = sorted(self.notes, key=lambda note: (note["performed_start"], note["pitch"]))
        minimum = 8 if self.core else 2
        if len(ordered) < minimum:
            raise ValueError(f"{self.part_id} too few notes")
        for index, note in enumerate(ordered, 1):
            if note["performed_start"] != note["nominal_start"] + note["offset"]:
                raise ValueError(f"{self.part_id} revalidate")
            note["id"] = f"{self.part_id}.n{index:04d}"
        return {
            "id": self.part_id,
            "study_id": self.study["id"],
            "slug": self.study["slug"],
            "role": self.role,
            "variation": self.variation,
            "core": self.core,
            "channel": self.channel,
            "file_slug": self.file_slug,
            "path": f"midi/{self.study['slug']}/{self.file_slug}.mid",
            "monophonic": self.monophonic,
            "max_poly": self.max_poly,
            "container_ticks": self.container_ticks,
            "container_bars": self.study["bars"],
            "bpm": self.study["bpm"],
            "tempo_us": self.study["tempo_us"],
            "notes": ordered,
        }


def keys(study, variation):
    return Part(
        study, f"{study['id']}.keys.{variation}", "keys", variation, True, 0,
        f"keys-{variation}", False, 4, 48, 76,
    )


def answer(study, variation):
    return Part(
        study, f"{study['id']}.answer.{variation}", "melodic-answer", variation, False, 1,
        f"answer-{variation}", True, 1, 60, 81,
    )


def _pair(study):
    return keys(study, "a"), keys(study, "b"), answer(study, "a"), answer(study, "b")


def voicing(part, bar_index, beat, duration, pitches, departures=()):
    nominal = bar_index * BAR + beat
    ordered = sorted(pitches)
    count = len(ordered)
    outside = set(departures)
    for index, pitch in enumerate(ordered):
        offset = (count - 1 - index) * ROLL
        velocity = part.study["contour"][bar_index] + (8 if index == count - 1 else 0)
        part.add(nominal, duration, pitch, velocity, offset, (pitch % 12) in outside)


def line(part, events):
    for bar_index, beat, duration, pitch, velocity in events:
        part.add(bar_index * BAR + beat, duration, pitch, velocity, 0, False)


def _s01(study):
    a, b, aa, bb = _pair(study)
    # Beat 1. Bars 0-3 hold, 4-6 shorten, bar 7 holds again.
    plan_a = [
        (0, 0, 2400, (52, 55, 59, 62)),
        (1, 0, 2400, (52, 55, 60)),
        (2, 0, 2400, (53, 57, 60)),
        (3, 0, 2400, (53, 55, 59)),
        (4, 0, 1680, (52, 59, 64)),
        (5, 0, 1680, (52, 57, 60)),
        (6, 0, 1680, (53, 57, 62)),
        (7, 0, 3000, (52, 55, 60)),
    ]
    plan_b = [
        (0, 960, 960, (55, 59, 62)),
        (1, 960, 960, (55, 60, 64)),
        (2, 960, 960, (57, 60, 64)),
        (3, 960, 960, (55, 59, 65)),
        (4, 960, 960, (59, 64, 67)),
        (5, 960, 960, (57, 60, 67)),
        (6, 960, 960, (57, 62, 65)),
        (7, 960, 960, (55, 60, 64)),
    ]
    for bar_index, beat, duration, pitches in plan_a:
        voicing(a, bar_index, beat, duration, pitches)
    for bar_index, beat, duration, pitches in plan_b:
        voicing(b, bar_index, beat, duration, pitches)
    line(aa, [(0, 1920, 720, 67, 46), (2, 1920, 720, 69, 50), (4, 1920, 720, 67, 48), (6, 1920, 720, 64, 52)])
    line(bb, [(1, 2880, 360, 72, 44), (3, 2880, 360, 71, 46), (5, 2880, 360, 69, 48), (7, 2880, 360, 67, 50)])
    return [a, b, aa, bb]


def _s02(study):
    a, b, aa, bb = _pair(study)
    plan_a = [
        (0, 480, 1920, (57, 60, 64)),
        (1, 480, 1920, (57, 62, 65)),
        (2, 480, 1920, (58, 62, 65)),
        (3, 480, 1920, (55, 60, 64)),
        (4, 480, 1920, (53, 58, 65)),
        (5, 480, 1920, (52, 57, 64)),
        (6, 480, 1920, (55, 58, 62)),
        (7, 480, 2400, (53, 57, 64)),
    ]
    plan_b = [
        (0, 0, 720, (60, 64, 65)),
        (1, 0, 720, (62, 65, 69)),
        (2, 0, 720, (62, 65, 70)),
        (3, 0, 720, (64, 67, 72)),
        (4, 0, 720, (58, 65, 70)),
        (5, 0, 720, (60, 64, 69)),
        (6, 0, 720, (58, 62, 67)),
        (7, 0, 720, (60, 64, 65)),
    ]
    for item in plan_a:
        voicing(a, *item)
    for item in plan_b:
        voicing(b, *item)
    line(aa, [(1, 1440, 480, 69, 44), (3, 1440, 480, 70, 46), (5, 1440, 480, 72, 48), (7, 1440, 480, 69, 50)])
    line(bb, [(0, 960, 1440, 65, 42), (4, 960, 1440, 64, 46)])
    return [a, b, aa, bb]


def _s03(study):
    a, b, aa, bb = _pair(study)
    plan_a = [
        (0, 0, 3360, (55, 62)),
        (2, 0, 3360, (50, 57)),
        (4, 0, 3360, (52, 59)),
        (6, 0, 3360, (48, 55)),
    ]
    plan_b = [
        (0, 1920, 480, (59, 62, 67)),
        (1, 1920, 480, (54, 57, 62)),
        (2, 1920, 480, (59, 64, 67)),
        (3, 1920, 480, (60, 64, 67)),
        (4, 1920, 480, (55, 59, 62)),
        (5, 1920, 480, (57, 62, 66)),
        (6, 1920, 480, (52, 59, 64)),
        (7, 1920, 480, (55, 60, 64)),
    ]
    for item in plan_a:
        voicing(a, *item)
    for item in plan_b:
        voicing(b, *item)
    line(aa, [(0, 960, 960, 74, 44), (4, 960, 960, 71, 48)])
    line(bb, [(1, 0, 480, 67, 42), (3, 0, 480, 69, 44), (5, 0, 480, 71, 46), (7, 0, 480, 67, 48)])
    return [a, b, aa, bb]


def _s04(study):
    a, b, aa, bb = _pair(study)
    plan_a = [
        (0, 960, 1800, (53, 57, 64), ()),
        (1, 960, 1800, (53, 58, 62), ()),
        (2, 960, 1800, (58, 62, 65), ()),
        (3, 960, 1800, (52, 55, 60), ()),
        (4, 960, 1800, (50, 57, 62), ()),
        (5, 960, 1800, (55, 58, 62), ()),
        (6, 960, 1800, (52, 57, 61), (1,)),
        (7, 960, 2400, (50, 57, 65), ()),
    ]
    plan_b = [
        (0, 2880, 600, (62, 65)),
        (1, 2880, 600, (58, 65)),
        (2, 2880, 600, (58, 65)),
        (3, 2880, 600, (60, 64)),
        (4, 2880, 600, (57, 62)),
        (5, 2880, 600, (58, 62)),
        (6, 2880, 600, (55, 60)),
        (7, 2880, 600, (62, 65)),
    ]
    for bar_index, beat, duration, pitches, departures in plan_a:
        voicing(a, bar_index, beat, duration, pitches, departures)
    for item in plan_b:
        voicing(b, *item)
    line(aa, [(0, 2880, 600, 69, 44), (3, 2880, 600, 67, 46), (7, 2880, 600, 65, 50)])
    line(bb, [(2, 0, 960, 72, 42), (6, 0, 960, 69, 46)])
    return [a, b, aa, bb]


def _s05(study):
    a, b, aa, bb = _pair(study)
    plan_a = [
        (0, 1920, 1440, (57, 62, 64)),
        (1, 1920, 1440, (59, 64, 69)),
        (2, 1920, 1440, (62, 66, 69)),
        (3, 1920, 1440, (59, 66, 71)),
        (4, 1920, 1440, (57, 61, 64)),
        (5, 1920, 1440, (62, 66, 69)),
        (6, 1920, 1440, (59, 64, 67)),
        (7, 1920, 1600, (57, 64, 69)),
    ]
    plan_b = [
        (0, 0, 480, (64, 69)),
        (1, 0, 480, (62, 69)),
        (2, 0, 480, (62, 66)),
        (3, 0, 480, (59, 66)),
        (4, 0, 480, (64, 69)),
        (5, 0, 480, (62, 69)),
        (6, 0, 480, (67, 71)),
        (7, 0, 480, (64, 69)),
    ]
    for item in plan_a:
        voicing(a, *item)
    for item in plan_b:
        voicing(b, *item)
    line(aa, [(0, 0, 480, 76, 44), (4, 0, 480, 73, 48), (7, 0, 480, 69, 50)])
    line(bb, [(1, 2880, 360, 71, 42), (3, 2880, 360, 69, 44), (5, 2880, 360, 66, 46)])
    return [a, b, aa, bb]


def _s06(study):
    a, b, aa, bb = _pair(study)
    plan_a = [
        (0, 1440, 1680, (51, 58, 63)),
        (1, 1440, 1680, (48, 55, 60)),
        (2, 1440, 1680, (56, 60, 63)),
        (3, 1440, 1680, (58, 62, 65)),
        (4, 1440, 1680, (51, 55, 58)),
        (5, 1440, 1680, (48, 55, 63)),
        (6, 1440, 1680, (56, 63, 67)),
        (7, 1440, 1920, (51, 58, 63)),
    ]
    plan_b = [
        (0, 0, 2880, (58, 63, 67)),
        (1, 0, 2880, (60, 63, 67)),
        (2, 0, 2880, (56, 63, 68)),
        (3, 0, 2880, (58, 65, 70)),
        (4, 0, 2880, (63, 67, 70)),
        (5, 0, 2880, (60, 67, 72)),
        (6, 0, 2880, (63, 68, 72)),
        (7, 0, 3200, (58, 63, 67)),
    ]
    for item in plan_a:
        voicing(a, *item)
    for item in plan_b:
        voicing(b, *item)
    line(aa, [(0, 0, 960, 70, 42), (2, 0, 960, 68, 44), (4, 0, 960, 67, 46), (6, 0, 960, 63, 48)])
    line(bb, [(1, 1920, 1440, 72, 42), (5, 1920, 1440, 70, 46)])
    return [a, b, aa, bb]


def _s07(study):
    a, b, aa, bb = _pair(study)
    plan_a = [
        (0, 2880, 480, (50, 53)),
        (1, 2880, 480, (53, 58)),
        (2, 2880, 480, (55, 58)),
        (3, 2880, 480, (51, 58)),
        (4, 2880, 480, (50, 57)),
        (5, 2880, 480, (53, 57)),
        (6, 2880, 480, (55, 60)),
        (7, 2880, 480, (53, 58)),
    ]
    plan_b = [
        (0, 240, 1440, (58, 62, 65)),
        (1, 240, 1440, (55, 58, 62)),
        (2, 240, 1440, (51, 58, 63)),
        (3, 240, 1440, (53, 57, 60)),
        (4, 240, 1440, (50, 57, 62)),
        (5, 240, 1440, (55, 62, 67)),
        (6, 240, 1440, (51, 58, 65)),
        (7, 240, 1680, (53, 58, 65)),
    ]
    for item in plan_a:
        voicing(a, *item)
    for item in plan_b:
        voicing(b, *item)
    line(aa, [(0, 960, 480, 70, 44), (3, 960, 480, 69, 46), (6, 960, 480, 65, 48)])
    line(bb, [(2, 1920, 720, 74, 42), (4, 1920, 720, 72, 44), (7, 1920, 720, 70, 48)])
    return [a, b, aa, bb]


def _s08(study):
    a, b, aa, bb = _pair(study)
    plan_a = [
        (0, 0, 840, (64, 68, 71)),
        (0, 1920, 1200, (68, 73)),
        (1, 0, 840, (61, 66, 69)),
        (1, 1920, 1200, (66, 73)),
        (2, 0, 840, (59, 66, 71)),
        (2, 1920, 1200, (64, 71)),
        (3, 0, 840, (56, 61, 68)),
        (3, 1920, 1200, (61, 68)),
        (4, 0, 840, (64, 68, 71)),
        (4, 1920, 1200, (69, 73)),
        (5, 0, 840, (66, 69, 73)),
        (5, 1920, 1200, (66, 73)),
        (6, 0, 840, (59, 64, 68)),
        (6, 1920, 1200, (64, 71)),
        (7, 0, 840, (64, 68, 71)),
        (7, 1920, 1400, (68, 76)),
    ]
    plan_b = [
        (0, 0, 7200, (52, 59, 64)),
        (2, 0, 7200, (57, 61, 64)),
        (4, 0, 7200, (54, 61, 66)),
        (6, 0, 7200, (52, 56, 64)),
    ]
    for item in plan_a:
        voicing(a, *item)
    for item in plan_b:
        voicing(b, *item)
    line(aa, [(1, 960, 480, 76, 44), (3, 960, 480, 73, 46), (5, 960, 480, 71, 48), (7, 960, 480, 68, 50)])
    line(bb, [(0, 2880, 1440, 76, 42), (4, 2880, 1440, 73, 46)])
    return [a, b, aa, bb]


BUILDERS = {
    "s01": _s01,
    "s02": _s02,
    "s03": _s03,
    "s04": _s04,
    "s05": _s05,
    "s06": _s06,
    "s07": _s07,
    "s08": _s08,
}


def studies():
    common = {
        "meter": "4/4",
        "bar_ticks": BAR,
        "ppq": PPQ,
        "stochastic_draws": 0,
        "bars": 8,
        "hand_split": HAND_SPLIT,
    }
    rows = [
        {**common, "id": "s01", "slug": "s01-paper-window", "title": "Paper Window", "bpm": 72,
         "tonic": "C", "tonal_reference": "C", "collection_name": "C major",
         "pitch_classes": [0, 2, 4, 5, 7, 9, 11], "departures": [], "seed": 7201,
         "spell": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
         "contour": [48, 52, 56, 60, 54, 58, 64, 70],
         "harmonic_rhythm": "One chord a bar: Em7, C, F, G7, E5, Am, Dm, C. The first chord is E G B D, with no C, so it is not a Cmaj7. The second is E G C, C major in first inversion. It is labeled C, not Am and not Em.",
         "changes": ["Em7", "C", "F", "G7", "E5", "Am", "Dm", "C"],
         "change_bars": [1, 1, 1, 1, 1, 1, 1, 1],
         "phrases": [
             {"name": "Window", "start_bar": 0, "bars": 4},
             {"name": "Answer", "start_bar": 4, "bars": 3},
             {"name": "Hold", "start_bar": 7, "bars": 1},
         ],
         "identity": "Variation A sits on beat 1. The first chord is four notes, then three. Bars 4 to 6 shorten, and bar 7 holds. Variation B starts on beat 2, uses a different inversion, and lasts one beat.",
         "limitations": "Pair keys A with answer A, and keys B with answer B. The answer is a reference file. It is not inside the keys file.",
         "voicing": "Close voicings from E3 to G4. The first chord is E3 G3 B3 D4, an Em7, not a Cmaj7. The top voice is the clearest tone. At most four notes sound.",
         "layering": "One keys track, split at C4 for display. The melodic answer is a separate monophonic reference.",
         "accent": "Contour 48, 52, 56, 60, 54, 58, 64, 70. The top voice is 8 higher. The answer stays quieter, between 44 and 52."},
        {**common, "id": "s02", "slug": "s02-late-seventh", "title": "Late Shells", "bpm": 66,
         "tonic": "F", "tonal_reference": "F", "collection_name": "F major",
         "pitch_classes": [5, 7, 9, 10, 0, 2, 4], "departures": [], "seed": 6602,
         "spell": ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"],
         "contour": [46, 50, 54, 58, 52, 56, 60, 66],
         "harmonic_rhythm": "One chord a bar in variation A: Am, Dm, Bb, C, Bb5, A5, Gm, Fmaj7. The C chord is G C E and has no Bb, so it is not a C7. The Bb chord has no A, so it is not a Bbmaj7. The A chord has no C or G, so it is not an Am7.",
         "changes": ["Am", "Dm", "Bb", "C", "Bb5", "A5", "Gm", "Fmaj7"],
         "change_bars": [1, 1, 1, 1, 1, 1, 1, 1],
         "phrases": [
             {"name": "Late", "start_bar": 0, "bars": 4},
             {"name": "Color", "start_bar": 4, "bars": 3},
             {"name": "Cadence", "start_bar": 7, "bars": 1},
         ],
         "identity": "Variation A enters on the and of 1 and holds for two beats, longer on the last bar. Variation B is on the downbeat and lasts a dotted eighth. Variation B does not put a seventh on top.",
         "limitations": "The answer plays only four notes in A and two in B. Silence is the rest of the line.",
         "voicing": "Three-note shells. Variation A does not keep a seventh in every bar. Variation B does not put the seventh on top, and it changes the low note.",
         "layering": "Keys carry the harmony. The answer is a reference and does not double the chord tones on the same attacks.",
         "accent": "Contour 46, 50, 54, 58, 52, 56, 60, 66. Top voice plus 8."},
        {**common, "id": "s03", "slug": "s03-open-fifths", "title": "Open Fifths", "bpm": 80,
         "tonic": "G", "tonal_reference": "G", "collection_name": "G major",
         "pitch_classes": [7, 9, 11, 0, 2, 4, 6], "departures": [], "seed": 8003,
         "spell": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
         "contour": [50, 50, 56, 56, 62, 62, 68, 68],
         "harmonic_rhythm": "Variation A: G, D, E5, C on even bars only. The E5 is E and B, a bare fifth, not Em. Variation B: G, D, Em, C, G, D, E5, C. The later E chord is E and B with no third, so it is not Em.",
         "changes": ["G", "D", "E5", "C"],
         "change_bars": [2, 2, 2, 2],
         "phrases": [
             {"name": "Fifth", "start_bar": 0, "bars": 4},
             {"name": "Fifth again", "start_bar": 4, "bars": 4},
         ],
         "identity": "Variation A is two-note fifths on even bars, held almost the whole bar, with odd bars empty. Variation B is a three-note chord on beat 3 of every bar, one eighth long.",
         "limitations": "Odd bars of keys A are intentional silence, not a missing file. The answer does not fill those bars in variation A.",
         "voicing": "A is a bare fifth. B adds the third and moves the register, except the E and B shell, which stays a fifth and is not labeled Em.",
         "layering": "No left-hand pad under the fifths. The answer is two notes in A and four in B.",
         "accent": "Contour 50, 50, 56, 56, 62, 62, 68, 68. Even bars match the fifths."},
        {**common, "id": "s04", "slug": "s04-minor-ninth", "title": "Minor Ninth", "bpm": 64,
         "tonic": "D", "tonal_reference": "D", "collection_name": "D natural minor",
         "pitch_classes": [2, 4, 5, 7, 9, 10, 0],
         "departures": ["Variation A bar 7 beat 2, tick 24000, uses C#4 (61) as a leading tone. It is outside D natural minor and is flagged. Variation B stays on C natural. No other study flags a departure."],
         "seed": 6404,
         "spell": ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"],
         "contour": [44, 48, 52, 56, 50, 54, 60, 66],
         "harmonic_rhythm": "F, A, E, then Gm7, Bb, Am7, Dm, Gm, A (variation A only), Dm. The first chord is the pitches F, A, and E. There is no D in that chord.",
         "changes": ["F A E", "Gm7", "Bb", "Am7", "Dm", "Gm", "A or Am", "Dm"],
         "change_bars": [1, 1, 1, 1, 1, 1, 1, 1],
         "phrases": [
             {"name": "Color", "start_bar": 0, "bars": 4},
             {"name": "Turn", "start_bar": 4, "bars": 2},
             {"name": "Leading tone", "start_bar": 6, "bars": 1},
             {"name": "Return", "start_bar": 7, "bars": 1},
         ],
         "identity": "Variation A starts on beat 2 with a three-note minor color and one flagged C#4. Variation B starts on beat 4, two notes, shorter, and never leaves the minor collection.",
         "limitations": "The C# is one chord tone in keys A. It is not a new key, and it is not in the answer.",
         "voicing": "The first chord of variation A is F3, A3, and E4. Those are the pitches that sound. There is no D in that chord. The dominant bar is the flagged C#4. B is a two-note shell.",
         "layering": "The answer has no note in bar 7, the bar that sounds the C#4 at tick 24000. It does not harmonize that pitch.",
         "accent": "Contour 44, 48, 52, 56, 50, 54, 60, 66. The leading-tone bar is step 60, not a spike."},
        {**common, "id": "s05", "slug": "s05-suspended-room", "title": "Suspended Room", "bpm": 76,
         "tonic": "A", "tonal_reference": "A", "collection_name": "A mixolydian",
         "pitch_classes": [9, 11, 1, 2, 4, 6, 7], "departures": [], "seed": 7605,
         "spell": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
         "contour": [48, 52, 56, 60, 64, 60, 56, 68],
         "harmonic_rhythm": "Asus4, E shell, D, B5, A, D, Em7 color, A.",
         "changes": ["Asus4", "E", "D", "B5", "A", "D", "Em", "A"],
         "change_bars": [1, 1, 1, 1, 1, 1, 1, 1],
         "phrases": [
             {"name": "Sus", "start_bar": 0, "bars": 4},
             {"name": "Third", "start_bar": 4, "bars": 4},
         ],
         "identity": "Variation A arrives on beat 3 and lets the third in at bar 4. Variation B is a two-note shell on the downbeat. It states major thirds on D F# and on G B, so those two shells are not suspended.",
         "limitations": "C# in variation A is inside A mixolydian. It is not a departure. Variation B has no C#.",
         "voicing": "A is three notes. B is two notes. The D F# shell and the G B shell state major thirds. The other B shells do not.",
         "layering": "The answer states E, C#, and A in variation A, and B, A, F# in variation B.",
         "accent": "Contour 48, 52, 56, 60, 64, 60, 56, 68. It rises, eases, then settles."},
        {**common, "id": "s06", "slug": "s06-low-register", "title": "Low Register", "bpm": 60,
         "tonic": "Eb", "tonal_reference": "Eb", "collection_name": "Eb major",
         "pitch_classes": [3, 5, 7, 8, 10, 0, 2], "departures": [], "seed": 6006,
         "spell": ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"],
         "contour": [42, 46, 50, 54, 48, 52, 58, 64],
         "harmonic_rhythm": "Ebmaj7, Cm7, Abmaj7, Bb7, Eb, Cm, Ab, Eb.",
         "changes": ["Ebmaj7", "Cm7", "Abmaj7", "Bb7", "Eb", "Cm", "Ab", "Eb"],
         "change_bars": [1, 1, 1, 1, 1, 1, 1, 1],
         "phrases": [
             {"name": "Low", "start_bar": 0, "bars": 4},
             {"name": "Same room", "start_bar": 4, "bars": 4},
         ],
         "identity": "Variation A sits low, on the and of 2, for under two beats. Variation B starts on beat 1 in a higher inversion and holds for most of the bar.",
         "limitations": "This is the slowest study, 8 bars at 60 BPM, 32 seconds. It is not a 16-bar file.",
         "voicing": "A stays around Eb3 to G4. B opens the spacing and reaches C5.",
         "layering": "The answer in A is four long tones on even bars. B answers only twice.",
         "accent": "Contour 42, 46, 50, 54, 48, 52, 58, 64. The softest keys in the pack."},
        {**common, "id": "s07", "slug": "s07-two-note-shell", "title": "Two-Note Shell", "bpm": 84,
         "tonic": "Bb", "tonal_reference": "Bb", "collection_name": "Bb major",
         "pitch_classes": [10, 0, 2, 3, 5, 7, 9], "departures": [], "seed": 8407,
         "spell": ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"],
         "contour": [52, 54, 56, 58, 60, 62, 64, 68],
         "harmonic_rhythm": "Bb, Bb, Gm, Eb, Bb6, F, C, Bb. Variation B uses the same plan with fuller shells.",
         "changes": ["Bb", "Bb", "Gm", "Eb", "Bb6", "F", "C", "Bb"],
         "change_bars": [1, 1, 1, 1, 1, 1, 1, 1],
         "phrases": [
             {"name": "Shell", "start_bar": 0, "bars": 4},
             {"name": "Shell answer", "start_bar": 4, "bars": 4},
         ],
         "identity": "Variation A is two notes on beat 4, an eighth long. Variation B is three notes a 16th after the downbeat, held much longer, with a longer last bar.",
         "limitations": "Beat 4 in variation A leaves the rest of the bar empty on purpose.",
         "voicing": "A is a two-note shell with no seventh. B adds the third tone and changes the low pitch.",
         "layering": "The answer sits above the shell and does not start with it.",
         "accent": "Contour 52, 54, 56, 58, 60, 62, 64, 68. A steady step, not a house curve."},
        {**common, "id": "s08", "slug": "s08-cadence-hold", "title": "Cadence Hold", "bpm": 70,
         "tonic": "E", "tonal_reference": "E", "collection_name": "E major",
         "pitch_classes": [4, 6, 8, 9, 11, 1, 3], "departures": [], "seed": 7008,
         "spell": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
         "contour": [46, 50, 54, 58, 52, 56, 62, 70],
         "harmonic_rhythm": "Variation A states a short chord then a held color every bar: E, C#, B, G#, E, F#, E, E. Variation B holds E, A, F#, E for two bars each.",
         "changes": ["E", "C#m", "B", "G#m", "E", "F#m", "E", "E"],
         "change_bars": [1, 1, 1, 1, 1, 1, 1, 1],
         "phrases": [
             {"name": "Call", "start_bar": 0, "bars": 4},
             {"name": "Hold", "start_bar": 4, "bars": 4},
         ],
         "identity": "Variation A attacks twice in every bar: a short chord on beat 1 and a two-note hold on beat 3. Variation B is one chord every two bars, held for 7200 ticks. D# is in the collection and is not used.",
         "limitations": "Variation B does not play on odd bars. That rest is written. Do not copy variation A into those bars.",
         "voicing": "A moves inner voices every bar. B is a wide shell an octave lower and stays put.",
         "layering": "The answer enters on the odd bars, where variation B is silent and variation A is between its two attacks.",
         "accent": "Contour 46, 50, 54, 58, 52, 56, 62, 70. The last hold is the clearest, still under 80."},
    ]
    for row in rows:
        if not 60 <= row["bpm"] <= 90:
            raise ValueError(row["bpm"])
        if row["bars"] != 8:
            raise ValueError(row["id"])
        seconds = row["bars"] * 4 * 60 / row["bpm"]
        if not 10 <= seconds <= 40:
            raise ValueError(f"{row['id']} lasts {seconds}")
        if sum(row["change_bars"]) != row["bars"] or len(row["change_bars"]) != len(row["changes"]):
            raise ValueError(row["id"])
        if sum(item["bars"] for item in row["phrases"]) != row["bars"]:
            raise ValueError(row["id"] + " phrases")
        if len(row["contour"]) != row["bars"]:
            raise ValueError(row["id"] + " contour")
        row["tempo_us"] = bpm_to_us(row["bpm"])
        row["effective_bpm"] = effective_bpm(row["tempo_us"])
        row["planned_seconds"] = seconds
    return rows


def _sig(notes):
    return tuple((note["performed_start"], note["pitch"], note["duration"]) for note in notes)


def assert_collections(catalog_studies, parts):
    allowed = {study["id"]: set(study["pitch_classes"]) for study in catalog_studies}
    for part in parts:
        pool = allowed[part["study_id"]]
        for note in part["notes"]:
            inside = (note["pitch"] % 12) in pool
            if note["departure"] and inside:
                raise ValueError(f"{part['id']} departure {note['pitch']} is inside the collection")
            if not note["departure"] and not inside:
                raise ValueError(f"{part['id']} note {note['pitch']} left the collection")
            if note["performed_start"] != note["nominal_start"] + note["offset"]:
                raise ValueError(f"{part['id']} offset equation")


def assert_identities(parts):
    keyed = [part for part in parts if part["role"] == "keys"]
    by = {}
    for part in keyed:
        by.setdefault(part["study_id"], {})[part["variation"]] = part
    attacks = {}
    report = []
    for study_id, vars_ in by.items():
        a_notes = vars_["a"]["notes"]
        b_notes = vars_["b"]["notes"]
        if _sig(a_notes) == _sig(b_notes):
            raise ValueError(f"{study_id} variations match")
        starts_a = tuple(note["performed_start"] for note in a_notes)
        starts_b = tuple(note["performed_start"] for note in b_notes)
        pitches_a = tuple(note["pitch"] for note in a_notes)
        pitches_b = tuple(note["pitch"] for note in b_notes)
        durations_a = tuple(note["duration"] for note in a_notes)
        durations_b = tuple(note["duration"] for note in b_notes)
        if starts_a == starts_b:
            raise ValueError(f"{study_id} start tuples match")
        if pitches_a == pitches_b:
            raise ValueError(f"{study_id} pitch tuples match")
        if durations_a == durations_b:
            raise ValueError(f"{study_id} duration tuples match")
        if starts_a in attacks:
            raise ValueError(f"{study_id} attack tuple repeats {attacks[starts_a]}")
        attacks[starts_a] = study_id
        report.append({
            "study_id": study_id,
            "a_notes": len(a_notes),
            "b_notes": len(b_notes),
            "a_attacks": len(set(starts_a)),
            "start_differs": True,
            "pitch_differs": True,
            "duration_differs": True,
        })
    return {
        "studies": report,
        "method": "Keys A and B differ in start, pitch, and duration. Variation A attack tuples are unique across the eight studies. Departures are flagged only outside the pitch-class set.",
    }


def compose():
    catalog_studies = studies()
    parts = []
    for study in catalog_studies:
        for part in BUILDERS[study["id"]](study):
            parts.append(part.finish())
    assert_collections(catalog_studies, parts)
    identity = assert_identities(parts)
    core = [part for part in parts if part["core"]]
    refs = [part for part in parts if not part["core"]]
    if len(core) != 16 or len(refs) != 16:
        raise ValueError((len(core), len(refs)))
    if any(part["role"] != "keys" for part in core):
        raise ValueError("core role")
    if any(part["role"] != "melodic-answer" for part in refs):
        raise ValueError("reference role")
    preview = next(study for study in catalog_studies if study["id"] == "s01")
    arrangement = {
        "id": "arrangement-preview-s01a",
        "path": "midi/arrangement.mid",
        "format": 1,
        "container_ticks": preview["bars"] * BAR,
        "bpm": preview["bpm"],
        "tempo_us": preview["tempo_us"],
        "meter": "4/4",
        "description": "Study 01 variation A keys with melodic answer A. The answer is not inside the keys file.",
        "tracks": [
            {"name": "Conductor", "source_part": None, "channel": None},
            {"name": "Keys", "source_part": "s01.keys.a", "channel": 0},
            {"name": "Melodic Answer", "source_part": "s01.answer.a", "channel": 1},
        ],
    }
    catalog = {
        "pack_id": PACK_ID,
        "pack_name": PACK_NAME,
        "catalog_version": GENERATOR_VERSION,
        "generator_version": GENERATOR_VERSION,
        "ppq": PPQ,
        "meter": {"numerator": 4, "denominator": 4, "bar_ticks": BAR},
        "pitched_range": [48, 81],
        "c4": 60,
        "hand_split": HAND_SPLIT,
        "note_policy": "Note-only MIDI. No program changes, controllers, pitch bend, aftertouch, or SysEx.",
        "microtiming": (
            "Keys use a fixed roll. The highest voice has offset 0. Each lower voice is 20 ticks later, "
            "so three notes use 40, 20, and 0 from low to high, and the one four-note chord uses 60, 40, 20, and 0. "
            "performed_start = nominal_start + offset. Duration is measured from the performed start. "
            "The melodic answer offset is 0. Its pocket is in the written rhythm. "
            "Offsets are bounded and shared by voice position. They are not chosen independently for every note."
        ),
        "processing_not_in_file": (
            "Pitch instability, noise, saturation, and filtering are not in the MIDI files. "
            "The renderer does not apply them."
        ),
        "length_choice": (
            "Eight bars was chosen before the notes. Sixteen bars at 60 BPM is 64 seconds and sixteen bars at 90 BPM is 42.7 seconds, "
            "both outside 10 to 40 seconds. Eight bars at 72 BPM is 26.7 seconds. Every study uses that 8-bar container."
        ),
        "stochastic_draws": 0,
        "seed_meaning": "Seeds identify studies. Nothing is random.",
        "core_part_count": len(core),
        "reference_part_count": len(refs),
        "core_role": "keys",
        "reference_role": "melodic-answer",
        "range_statement": (
            "Keys use MIDI 48 to 76, at most four notes at once. Notes below 60 are shown as the lower hand. "
            "Notes from 60 up are the upper hand. The melodic answer is monophonic, MIDI 60 to 81, a reference, "
            "and not part of the core count."
        ),
        "studies": [{key: study[key] for key in (
            "id", "slug", "title", "bpm", "tempo_us", "effective_bpm", "bars", "planned_seconds", "meter", "bar_ticks",
            "tonic", "tonal_reference", "collection_name", "pitch_classes", "spell", "departures", "seed",
            "harmonic_rhythm", "changes", "change_bars", "phrases", "identity", "limitations",
            "voicing", "layering", "accent", "contour", "hand_split", "stochastic_draws",
        )} for study in catalog_studies],
        "parts": [{
            "id": part["id"], "study_id": part["study_id"], "role": part["role"], "variation": part["variation"],
            "core": part["core"], "channel": part["channel"], "path": part["path"], "notes": len(part["notes"]),
            "container_bars": part["container_bars"], "bpm": part["bpm"], "monophonic": part["monophonic"],
        } for part in parts],
        "arrangement": arrangement,
        "preview_part_ids": ["s01.keys.a", "s01.answer.a"],
        "stack_warning": "Use either the combined arrangement or the separate parts. Do not stack the part files on top of the combined file.",
    }
    score = {
        "pack_id": PACK_ID,
        "generator_version": GENERATOR_VERSION,
        "ppq": PPQ,
        "parts": parts,
        "arrangement": arrangement,
        "identity_check": identity,
    }
    return {"catalog": catalog, "score": score}
