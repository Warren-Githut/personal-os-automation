"""
Voice → Markdown processor for Personal_OS vault.
Usage: python process_voice.py <audio_file> [--model tiny|base|small|medium]
Output: Markdown note saved to _inbox/processed/, path printed to stdout.
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path.home() / ".env", override=True)

PERSONAL_CORRECTIONS = {
    r"\bgg\b": "GG",
    r"\bmos\b": "MOS",
    r"\bdcf\b": "DCF",
    r"\broe\b": "ROE",
    r"\bdca\b": "DCA",
    r"\bclob\b": "CLOB",
    r"\bebit ?da\b": "EBITDA",
    r"p&l|p and l": "P&L",
    r"\bkyc\b": "KYC",
}


def fix_terms(text: str) -> str:
    for pattern, replacement in PERSONAL_CORRECTIONS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def transcribe(audio_path: Path, model_size: str = "small") -> str:
    import os
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        return _transcribe_groq(audio_path, groq_key)
    return _transcribe_local(audio_path, model_size)


def _transcribe_groq(audio_path: Path, api_key: str) -> str:
    from groq import Groq
    client = Groq(api_key=api_key)
    print("  Using Groq Whisper large-v3...", file=sys.stderr)
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            file=(audio_path.name, f),
            model="whisper-large-v3",
            language="vi",
            response_format="text",
        )
    raw = result if isinstance(result, str) else result.text
    print("  Detected language: vi", file=sys.stderr)
    return fix_terms(raw)


def _transcribe_local(audio_path: Path, model_size: str) -> str:
    from faster_whisper import WhisperModel
    print(f"  Using local Whisper (Groq key not found). Model: {model_size}", file=sys.stderr)
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(audio_path), language="vi", beam_size=5)
    print(f"  Detected language: {info.language} ({info.language_probability:.0%})", file=sys.stderr)
    raw = " ".join(seg.text.strip() for seg in segments)
    return fix_terms(raw)


def build_note(audio_path: Path, transcript: str) -> str:
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    return f"""---
date: {date_str}
time: {time_str}
source: voice
file: {audio_path.name}
tags: [inbox, voice, unprocessed]
type: unclassified
priority: normal
---

# Voice Note — {audio_path.stem}

## Transcript
{transcript}

## Key Points
-

## Action Items
- [ ]

## Context / Follow-up

"""


def main():
    parser = argparse.ArgumentParser(description="Transcribe voice note to Markdown")
    parser.add_argument("audio", help="Path to audio file (.m4a, .mp3, .wav, .ogg)")
    parser.add_argument("--model", default="small", choices=["tiny", "base", "small", "medium"],
                        help="Whisper model size (default: small)")
    parser.add_argument("--delete-source", action="store_true",
                        help="Delete source audio file after successful transcription")
    args = parser.parse_args()

    audio_path = Path(args.audio).resolve()
    if not audio_path.exists():
        print(f"Error: File not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Transcribing {audio_path.name} with model={args.model}...", file=sys.stderr)
    transcript = transcribe(audio_path, args.model)

    note_content = build_note(audio_path, transcript)

    vault_root = Path(__file__).parent.parent
    out_dir = vault_root / "_inbox" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"__tmp_{audio_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    out_file.write_text(note_content, encoding="utf-8")

    if args.delete_source:
        if len(transcript.strip()) >= 10:
            audio_path.unlink(missing_ok=True)
            print(f"  Source deleted: {audio_path.name}", file=sys.stderr)
        else:
            print(f"  ⚠️ Transcript too short — source file kept: {audio_path.name}", file=sys.stderr)

    print(out_file)


if __name__ == "__main__":
    main()
