"""Repo-owned preview synthesizer.

This is a simple synth, not a General MIDI soundfont and not a mix engine.
It renders the canonical notes for the preview arrangement. Keys are a sine
plus a quiet triangle. The melodic answer is a quieter sine. Sample positions
are absolute:

    sample = floor(seconds * sample_rate + 0.5)

seconds = tick / 960 * encoded_microseconds_per_quarter / 1_000_000.
Intervals are not accumulated.

Pitch instability, noise, saturation, and filtering are not applied.
A linear gain change, if the mix is loud, is not saturation.
Sample peak is not true peak and is not an integrated loudness measurement.
"""

from __future__ import annotations

import math
import wave
from array import array
from pathlib import Path

SR = 44100
RENDERER_VERSION = "simple-synth-1.0.0"


def tick_to_sample(tick: int, tempo_us: int, sample_rate: int = SR) -> int:
    seconds = (tick / 960) * (tempo_us / 1_000_000)
    return int(math.floor(seconds * sample_rate + 0.5))


def container_seconds(container_ticks: int, tempo_us: int) -> float:
    return (container_ticks / 960) * (tempo_us / 1_000_000)


def _midi_freq(pitch: int) -> float:
    return 440.0 * (2.0 ** ((pitch - 69) / 12.0))


def _env(index: int, start: int, end: int, attack: float, release: float) -> float:
    t = (index - start) / SR
    remain = (end - index) / SR
    env = 1.0
    if t < attack:
        env *= t / attack
    if remain < release:
        env *= remain / release
    return env


def render_preview(parts: list[dict], tempo_us: int, container_ticks: int, wav_path: Path) -> dict:
    total = tick_to_sample(container_ticks, tempo_us)
    mix = array("d", [0.0]) * total

    def add_keys(note: dict) -> None:
        start = tick_to_sample(note["performed_start"], tempo_us)
        end = tick_to_sample(note["performed_start"] + note["duration"], tempo_us)
        end = min(total, max(end, start + 1))
        freq = _midi_freq(note["pitch"])
        inc = freq / SR
        phase = 0.0
        tri = 0.0
        amp = (note["velocity"] / 127.0) * 0.22
        for index in range(start, end):
            phase += inc
            if phase >= 1.0:
                phase -= 1.0
            tri += inc * 2.0
            if tri >= 1.0:
                tri -= 1.0
            sine = math.sin(2.0 * math.pi * phase)
            triangle = 1.0 - 4.0 * abs(tri - 0.5)
            env = _env(index, start, end, 0.03, 0.06)
            mix[index] += (sine + triangle * 0.12) * env * amp

    def add_answer(note: dict) -> None:
        start = tick_to_sample(note["performed_start"], tempo_us)
        end = tick_to_sample(note["performed_start"] + note["duration"], tempo_us)
        end = min(total, max(end, start + 1))
        freq = _midi_freq(note["pitch"])
        inc = freq / SR
        phase = 0.0
        amp = (note["velocity"] / 127.0) * 0.16
        for index in range(start, end):
            phase += inc
            if phase >= 1.0:
                phase -= 1.0
            env = _env(index, start, end, 0.045, 0.08)
            mix[index] += math.sin(2.0 * math.pi * phase) * env * amp

    roles = {
        "keys": add_keys,
        "melodic-answer": add_answer,
    }
    rendered = []
    for part in parts:
        voice = roles[part["role"]]
        for note in part["notes"]:
            voice(note)
        rendered.append({"id": part["id"], "role": part["role"], "notes": len(part["notes"])})

    peak = 0.0
    for sample in mix:
        magnitude = sample if sample >= 0 else -sample
        if magnitude > peak:
            peak = magnitude
    if peak == 0:
        raise RuntimeError("preview mix is silent")
    scale = 1.0 if peak <= 0.85 else 0.85 / peak
    pcm = array("h")
    for sample in mix:
        value = int(sample * scale * 32767.0)
        if value > 32767:
            value = 32767
        elif value < -32768:
            value = -32768
        pcm.append(value)
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(wav_path), "w") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SR)
        handle.writeframes(pcm.tobytes())
    sample_peak = max(abs(sample) for sample in pcm)
    return {
        "renderer": RENDERER_VERSION,
        "sample_rate": SR,
        "channels": 1,
        "sample_format": "signed 16-bit little-endian PCM",
        "samples": total,
        "seconds": container_seconds(container_ticks, tempo_us),
        "rounding": "sample = floor(seconds * sample_rate + 0.5), computed from tick 0; intervals are not summed",
        "sample_peak": int(sample_peak),
        "sample_peak_dbfs": 20.0 * math.log10(sample_peak / 32768.0),
        "sample_peak_note": "This is a sample peak of the integer mix after a linear scale. It is not a true-peak measurement and it is not an integrated loudness measurement.",
        "linear_scale": scale,
        "linear_scale_note": "If the float mix exceeds 0.85, one constant gain is applied. That is not saturation, filtering, noise, or pitch movement.",
        "voices": rendered,
        "mapping": {
            "keys": "sine plus a quiet triangle, 30 ms attack, held for the written duration",
            "melodic-answer": "quieter sine, 45 ms attack, held for the written duration",
        },
        "mapping_note": (
            "These voices are preview mappings. They are not encoded in the MIDI file. "
            "Pitch instability, noise, saturation, and filtering are not applied."
        ),
    }
