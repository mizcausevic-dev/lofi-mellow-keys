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
