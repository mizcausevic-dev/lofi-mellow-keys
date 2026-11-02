"""Procedural raster artwork and ffmpeg media steps.

The painter is original and deterministic. It draws a quiet piano roll on warm
paper. Short bars are graphite. The longer holds are sage. It is an
illustration, not a photograph of a session or of performers.

DejaVu Sans Bold is used only to rasterize the disclosure into the film and the
poster. The font file is not shipped.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ON_PICTURE = "preview, not master"


def _clamp(value: int) -> int:
    return 0 if value < 0 else 255 if value > 255 else value


def paint(width: int, height: int, framing: str) -> bytes:
    # Eight studies, two bars of height each: a short attack and a longer hold.
    levels = (
        0.34, 0.72,
        0.28, 0.64,
        0.40, 0.80,
        0.22, 0.58,
        0.36, 0.76,
        0.26, 0.62,
        0.32, 0.70,
        0.44, 0.88,
    )
    margin_x = int(width * (0.08 if framing == "wide" else 0.11))
    floor = int(height * (0.80 if framing == "square" else 0.76))
    top = int(height * (0.20 if framing == "square" else 0.26))
    span = max(1, width - margin_x * 2)
    gap = span / len(levels)
    pixels = bytearray(width * height * 3)
    for y in range(height):
        shade = y / max(1, height - 1)
        row = y * width * 3
        paper_r = 239 - int(12 * shade)
        paper_g = 232 - int(14 * shade)
        paper_b = 216 - int(16 * shade)
        for x in range(width):
            pixels[row + x * 3] = paper_r
            pixels[row + x * 3 + 1] = paper_g
            pixels[row + x * 3 + 2] = paper_b
    for staff in range(5):
        y = top + int((floor - top) * (staff + 1) / 6)
        row = y * width * 3
        for x in range(margin_x, width - margin_x):
            pixels[row + x * 3] = 214
            pixels[row + x * 3 + 1] = 204
            pixels[row + x * 3 + 2] = 186
    for index, level in enumerate(levels):
        x0 = int(margin_x + index * gap + gap * 0.22)
        x1 = int(margin_x + index * gap + gap * 0.78)
        y0 = int(floor - level * (floor - top))
        held = index % 2 == 1
        for y in range(y0, floor):
            mix = (y - y0) / max(1, floor - y0)
            if held:
                r = int(92 + 18 * mix)
                g = int(112 + 10 * mix)
                b = int(78 + 8 * mix)
            else:
                r = int(62 + 16 * mix)
                g = int(58 + 12 * mix)
                b = int(52 + 8 * mix)
            row = y * width * 3
            for x in range(max(0, x0), min(width, x1)):
                pixels[row + x * 3] = _clamp(r)
                pixels[row + x * 3 + 1] = _clamp(g)
                pixels[row + x * 3 + 2] = _clamp(b)
    return bytes(pixels)

def write_ppm(path: Path, width: int, height: int, rgb: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = f"P6\n{width} {height}\n255\n".encode("ascii")
    path.write_bytes(header + rgb)


def run(command: list[str]) -> None:
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            "command failed\n"
            + " ".join(command)
            + "\n"
            + completed.stderr[-2000:]
        )


def ppm_to_jpeg(ppm: Path, jpeg: Path, quality: int = 3) -> None:
    jpeg.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-i", str(ppm), "-frames:v", "1", "-q:v", str(quality), str(jpeg)])


def draw_disclosure(source: Path, dest: Path, textfile: Path) -> list[str]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    textfile.write_text(ON_PICTURE + "\n", encoding="utf-8")
    command = [
        "ffmpeg", "-y", "-i", str(source),
        "-vf",
        (
            f"drawtext=textfile={textfile}:fontfile={FONT}:fontsize=48:"
            "fontcolor=white:x=(w-text_w)/2:y=h-100:box=1:boxcolor=black@0.68:boxborderw=22"
        ),
        "-frames:v", "1",
        "-q:v", "3",
        str(dest),
    ]
    run(command)
    return command


def encode_mp3(wav: Path, mp3: Path) -> list[str]:
    mp3.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-y", "-i", str(wav),
        "-codec:a", "libmp3lame", "-b:a", "192k",
        str(mp3),
    ]
    run(command)
    return command


def encode_film(plate: Path, mp3: Path, mp4: Path, textfile: Path, duration: str) -> list[str]:
    mp4.parent.mkdir(parents=True, exist_ok=True)
    textfile.write_text(ON_PICTURE + "\n", encoding="utf-8")
    command = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", "24", "-i", str(plate),
        "-i", str(mp3),
        "-t", duration,
        "-vf",
        (
            "scale=1280:720,"
            f"drawtext=textfile={textfile}:fontfile={FONT}:fontsize=48:"
            "fontcolor=white:x=(w-text_w)/2:y=h-100:box=1:boxcolor=black@0.68:boxborderw=22"
        ),
        "-r", "24",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        "-shortest",
        "-movflags", "+faststart",
        str(mp4),
    ]
    run(command)
    return command


def derive_social(hero: Path, square: Path, portrait: Path, card: Path) -> dict[str, list[str]]:
    portrait.parent.mkdir(parents=True, exist_ok=True)
    card.parent.mkdir(parents=True, exist_ok=True)
    portrait_cmd = [
        "ffmpeg", "-y", "-i", str(square),
        "-vf", "crop=864:1080:108:0,scale=1080:1350",
        "-q:v", "3",
        str(portrait),
    ]
    card_cmd = [
        "ffmpeg", "-y", "-i", str(hero),
        "-vf", "scale=1600:900",
        "-q:v", "3",
        str(card),
    ]
    run(portrait_cmd)
    run(card_cmd)
    return {"portrait": portrait_cmd, "card": card_cmd}
