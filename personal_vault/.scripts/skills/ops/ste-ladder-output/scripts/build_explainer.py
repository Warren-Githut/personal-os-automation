#!/usr/bin/env python
"""
build_explainer.py — Render a narrated explainer video from a scene manifest.

Pipeline (all local, no API key, no paid service):
    manifest.json  ->  per-scene HTML  ->  Chrome headless PNG frames
                   ->  edge-tts narration (Vietnamese or English)
                   ->  ffmpeg segments   ->  concat  ->  final .mp4

Input manifest (JSON):
    {
      "title": "LU7 Doanh thu W40",
      "out": "C:/abs/path/out.mp4",
      "theme": "dark",                      # dark | light
      "width": 1280, "height": 720, "fps": 30,
      "voice": "vi-VN-HoaiMyNeural",
      "tail_seconds": 0.4,                  # silence padded after each line
      "scenes": [
        {
          "narration": "Doanh thu net la 128 trieu dong.",
          "html": "<h1>128.4M</h1>",        # inline, wrapped by the base shell
          "html_file": "C:/abs/path/x.html" # optional, wins over "html"
        }
      ]
    }

Every scene's narration length drives that scene's on-screen duration, so the
picture always matches the voice. No manual timing to get wrong.

Usage:
    python build_explainer.py manifest.json
    python build_explainer.py manifest.json --keep-work   # keep frame/segment files
"""

from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# --------------------------------------------------------------------------
# Tool discovery. Windows-first, because that is where this runs.
# --------------------------------------------------------------------------
FFMPEG_CANDIDATES = [
    r"C:/Users/khoans/AppData/Local/hermes/tools/ffmpeg-9.0.1-win32-x64/bin/ffmpeg",
    "ffmpeg",
]
FFPROBE_CANDIDATES = [
    r"C:/Users/khoans/AppData/Local/hermes/tools/ffmpeg-9.0.1-win32-x64/bin/ffprobe",
    "ffprobe",
]
CHROME_CANDIDATES = [
    r"C:/Program Files/Google/Chrome/Application/chrome.exe",
    r"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    r"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
]

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "card": "#161b22",
        "fg": "#e6edf3",
        "muted": "#8b949e",
        "accent": "#7ee787",
        "border": "#30363d",
    },
    "light": {
        "bg": "#ffffff",
        "card": "#f6f8fa",
        "fg": "#1f2328",
        "muted": "#656d76",
        "accent": "#1a7f37",
        "border": "#d0d7de",
    },
}

BASE_CSS = """
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; }
  html, body { margin:0; padding:0; height:100%; }
  body {
    background: __BG__; color: __FG__;
    font-family: "Segoe UI", "Noto Sans", Arial, sans-serif;
    display:flex; align-items:center; justify-content:center;
  }
  .stage { width:__W__px; height:__H__px; padding:64px 80px;
           display:flex; flex-direction:column; justify-content:center; }
  h1 { font-size:76px; margin:0 0 20px; line-height:1.12; color:__ACCENT__; }
  h2 { font-size:52px; margin:0 0 20px; line-height:1.18; }
  p  { font-size:34px; margin:0 0 16px; line-height:1.42; color:__FG__; }
  .muted { color:__MUTED__; font-size:28px; }
  ul { font-size:34px; line-height:1.6; margin:0; padding-left:38px; }
  li { margin-bottom:12px; }
  .card { background:__CARD__; border:1px solid __BORDER__; border-radius:16px;
          padding:32px 40px; margin-top:20px; }
  .num { font-size:104px; font-weight:700; color:__ACCENT__; line-height:1.05; }
  .row { display:flex; gap:24px; align-items:baseline; flex-wrap:wrap; }
  .bar { height:24px; background:__CARD__; border:1px solid __BORDER__;
         border-radius:12px; overflow:hidden; margin-top:28px; }
  .bar > span { display:block; height:100%; background:__ACCENT__; }
  table { border-collapse:collapse; font-size:30px; }
  td, th { padding:12px 22px; border-bottom:1px solid __BORDER__; text-align:left; }
  th { color:__MUTED__; font-weight:600; }
</style>
"""


class BuildError(RuntimeError):
    """Raised with a message meant to be shown verbatim to the operator."""


def find_tool(candidates: list[str], label: str) -> str:
    for cand in candidates:
        if Path(cand).is_file():
            return cand
        found = shutil.which(cand)
        if found:
            return found
    raise BuildError(
        f"Cannot find {label}. Tried: {candidates}. "
        f"Install it or add its absolute path to the candidate list in this script."
    )


def find_chrome() -> str:
    for cand in CHROME_CANDIDATES:
        if Path(cand).is_file():
            return cand
    raise BuildError(
        "Cannot find Chrome/Edge. Tried: " + ", ".join(CHROME_CANDIDATES)
    )


def run(cmd: list[str], what: str) -> str:
    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-6:]
        raise BuildError(
            f"{what} failed (exit {proc.returncode}).\n  cmd: {' '.join(cmd[:6])} ...\n"
            + "\n".join("  " + line for line in tail)
        )
    return proc.stdout


def media_duration(ffprobe: str, path: Path) -> float:
    out = run(
        [
            ffprobe, "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        f"ffprobe {path.name}",
    )
    return float(out.strip())


def build_shell(theme: dict, width: int, height: int, body: str) -> str:
    css = (
        BASE_CSS.replace("__BG__", theme["bg"])
        .replace("__FG__", theme["fg"])
        .replace("__MUTED__", theme["muted"])
        .replace("__ACCENT__", theme["accent"])
        .replace("__CARD__", theme["card"])
        .replace("__BORDER__", theme["border"])
        .replace("__W__", str(width))
        .replace("__H__", str(height))
    )
    return (
        "<!DOCTYPE html><html lang=\"vi\"><head><meta charset=\"utf-8\">"
        f"<style>{css}</style></head>"
        f'<body><div class="stage">{body}</div></body></html>'
    )


async def _synth_one(text: str, voice: str, dest: Path) -> bool:
    import edge_tts

    last = ""
    for attempt in range(5):
        try:
            await edge_tts.Communicate(text, voice).save(str(dest))
            if dest.exists() and dest.stat().st_size > 3000:
                return True
            last = f"file too small ({dest.stat().st_size if dest.exists() else 0}B)"
        except Exception as exc:  # NoAudioReceived is the common transient one
            last = f"{type(exc).__name__}: {exc}"
        # Edge TTS throttles bursts; back off before retrying.
        await asyncio.sleep(1.5 * (attempt + 1))
    print(f"    ! tts failed after 5 attempts: {last}", file=sys.stderr)
    return False


async def synth_all(scenes: list[dict], voice: str, out_dir: Path) -> list[Path]:
    made: list[Path] = []
    for i, scene in enumerate(scenes, 1):
        text = (scene.get("narration") or "").strip()
        if not text:
            print(f"    scene {i}: no narration -> 0.9s silent still")
            made.append(out_dir / f"a{i}.mp3")
            made[-1].write_bytes(b"")
            continue
        dest = out_dir / f"a{i}.mp3"
        print(f"    scene {i}: tts ({voice})")
        if await _synth_one(text, voice, dest):
            made.append(dest)
        else:
            print(f"    scene {i}: tts unavailable -> 0.9s silent still")
            dest.write_bytes(b"")
            made.append(dest)
        await asyncio.sleep(0.6)
    return made


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("manifest", help="path to manifest.json")
    ap.add_argument("--keep-work", action="store_true",
                    help="keep frames/segments/audio instead of deleting them")
    args = ap.parse_args()

    manifest_path = Path(args.manifest).resolve()
    if not manifest_path.is_file():
        print(f"ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        return 2
    spec = json.loads(manifest_path.read_text(encoding="utf-8"))

    scenes = spec.get("scenes") or []
    if not scenes:
        print("ERROR: manifest has no scenes.", file=sys.stderr)
        return 2

    width = int(spec.get("width", 1280))
    height = int(spec.get("height", 720))
    fps = int(spec.get("fps", 30))
    voice = spec.get("voice", "vi-VN-HoaiMyNeural")
    tail = float(spec.get("tail_seconds", 0.4))
    theme = THEMES.get(spec.get("theme", "dark"), THEMES["dark"])

    out_path = Path(spec["out"])
    if not out_path.is_absolute():
        out_path = (manifest_path.parent / out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        ffmpeg = find_tool(FFMPEG_CANDIDATES, "ffmpeg")
        ffprobe = find_tool(FFPROBE_CANDIDATES, "ffprobe")
        chrome = find_chrome()
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3

    work = Path(tempfile.mkdtemp(prefix="explainer_"))
    print(f"  tools : ffmpeg={Path(ffmpeg).name} chrome={Path(chrome).name}")
    print(f"  output: {out_path}")
    print(f"  scenes: {len(scenes)}  ({width}x{height}@{fps})")

    try:
        # 1. HTML per scene ------------------------------------------------
        print("  [1/5] writing scene HTML")
        html_files: list[Path] = []
        for i, scene in enumerate(scenes, 1):
            if scene.get("html_file"):
                src = Path(scene["html_file"])
                body = src.read_text(encoding="utf-8")
            else:
                body = scene.get("html") or ""
            page = work / f"scene{i}.html"
            page.write_text(build_shell(theme, width, height, body), encoding="utf-8")
            html_files.append(page)

        # 2. Narration ------------------------------------------------------
        print("  [2/5] narration")
        audio = asyncio.run(synth_all(scenes, voice, work))

        # 3. Frames ---------------------------------------------------------
        print("  [3/5] chrome headless frames")
        frames: list[Path] = []
        for i, page in enumerate(html_files, 1):
            png = work / f"frame{i}.png"
            cmd = [
                chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
                "--hide-scrollbars", f"--window-size={width},{height}",
                "--virtual-time-budget=1500",
                # Chrome needs a native path here; a /c/... MSYS path fails silently.
                f"--screenshot={png.as_posix()}",
                page.as_uri(),
            ]
            run(cmd, f"chrome screenshot scene {i}")
            if not png.is_file() or png.stat().st_size < 1000:
                raise BuildError(
                    f"scene {i}: chrome produced no frame at {png}. "
                    f"On Windows the screenshot path must look like C:/... not /c/..."
                )
            frames.append(png)

        # 4. Segments -------------------------------------------------------
        print("  [4/5] ffmpeg segments")
        segs: list[Path] = []
        for i, (png, aud) in enumerate(zip(frames, audio), 1):
            dur = 0.9
            if aud.stat().st_size > 0:
                dur = media_duration(ffprobe, aud) + tail
            seg = work / f"seg{i}.mp4"
            vf = (
                f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color={theme['bg']},"
                "format=yuv420p"
            )
            cmd = [ffmpeg, "-y", "-loop", "1", "-i", str(png)]
            if aud.stat().st_size > 0:
                cmd += ["-i", str(aud)]
            cmd += [
                "-t", f"{dur:.3f}", "-vf", vf, "-r", str(fps),
                "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            ]
            if aud.stat().st_size > 0:
                cmd += ["-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-shortest"]
            else:
                cmd += ["-an"]
            cmd.append(str(seg))
            run(cmd, f"ffmpeg segment {i}")
            segs.append(seg)

        # 5. Concat ---------------------------------------------------------
        print("  [5/5] concat")
        listing = work / "segments.txt"
        listing.write_text(
            "\n".join(f"file '{s.as_posix()}'" for s in segs) + "\n", encoding="utf-8"
        )
        run(
            [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
             "-c", "copy", str(out_path)],
            "ffmpeg concat",
        )

        total = media_duration(ffprobe, out_path)
        size_kb = out_path.stat().st_size / 1024
        print(f"\nOK  {out_path}")
        print(f"    {total:.2f}s  {width}x{height}@{fps}  {size_kb:.0f} KB")
        if not args.keep_work:
            shutil.rmtree(work, ignore_errors=True)
        else:
            print(f"    work dir kept: {work}")
        return 0
    except BuildError as exc:
        print(f"\nFAILED: {exc}", file=sys.stderr)
        if args.keep_work:
            print(f"work dir kept for inspection: {work}", file=sys.stderr)
        else:
            shutil.rmtree(work, ignore_errors=True)
        return 1
    except Exception as exc:  # noqa: BLE001 - surface everything to the operator
        print(f"\nUNEXPECTED {type(exc).__name__}: {exc}", file=sys.stderr)
        shutil.rmtree(work, ignore_errors=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())