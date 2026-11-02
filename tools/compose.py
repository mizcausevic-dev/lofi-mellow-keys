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
