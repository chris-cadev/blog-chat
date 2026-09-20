#!/usr/bin/env python3
"""Compress wav/audio to mp3/opus via ffmpeg (MB → KB).

Usage:
    python scripts/compress_audio.py input.wav
    python scripts/compress_audio.py input.wav output.mp3 --bitrate 32k
    python scripts/compress_audio.py input.wav --format opus --bitrate 24k
    python scripts/compress_audio.py content/_drafts/handy-1789869763.wav --bitrate 32k

Defaults: mp3, 32k mono 16kHz (voice-optimized, ~2.4MB for 10min).
For KB range use 16-24k opus or 24k mp3.
Requires: ffmpeg (apt install ffmpeg)
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def fmt_size(n: int) -> str:
    for unit in ("B", "KB", "MB"):
        if n < 1024 or unit == "MB":
            return f"{n/1024:.1f}{unit}" if unit != "B" else f"{n}B"
        n //= 1  # keep int for next
    return f"{n}B"


def human_size(path: Path) -> str:
    s = path.stat().st_size
    if s < 1024:
        return f"{s}B"
    if s < 1024 * 1024:
        return f"{s/1024:.1f}KB"
    return f"{s/1024/1024:.1f}MB"


def compress(inp: Path, out: Path | None, bitrate: str, fmt: str, samplerate: int) -> Path:
    if not inp.exists():
        raise SystemExit(f"input not found: {inp}")
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg not found (apt install ffmpeg)")

    if out is None:
        ext = "opus" if fmt == "opus" else "mp3"
        out = inp.with_suffix(f".{ext}")

    out.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "opus":
        # opus: best for voice at low bitrates
        cmd = ["ffmpeg", "-y", "-i", str(inp), "-c:a", "libopus", "-b:a", bitrate, "-ac", "1", "-ar", str(samplerate), str(out)]
    else:
        cmd = ["ffmpeg", "-y", "-i", str(inp), "-c:a", "libmp3lame", "-b:a", bitrate, "-ac", "1", "-ar", str(samplerate), str(out)]

    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    print(f"{inp} {human_size(inp)} -> {out} {human_size(out)}")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", type=Path, help="wav/mp3/etc input")
    p.add_argument("output", type=Path, nargs="?", help="output file (default: input with .mp3/.opus)")
    p.add_argument("--bitrate", default="32k", help="e.g. 32k, 24k, 16k (default: 32k)")
    p.add_argument("--format", choices=("mp3", "opus"), default="mp3", help="output codec (default: mp3)")
    p.add_argument("--samplerate", type=int, default=16000, help="Hz, 16000 good for voice (default: 16000)")
    args = p.parse_args()
    compress(args.input, args.output, args.bitrate, args.format, args.samplerate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
