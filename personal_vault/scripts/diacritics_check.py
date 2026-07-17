#!/usr/bin/env python3
"""
diacritics_check.py -- Pre-commit hook to detect latinized Vietnamese (no diacritics) in .md files.

Detects Vietnamese text written WITHOUT full diacritics (e.g., "bao hiem" instead of "bao hiem").
If >=5 Vietnamese-like words found and >15% of all words match Vietnamese patterns
but zero Vietnamese diacritics present -> reject.

Usage:
    python scripts/diacritics_check.py              # scan staged .md files (pre-commit mode)
    python scripts/diacritics_check.py path/to/file  # scan specific file(s)
    python scripts/diacritics_check.py --fix         # (reserved for future auto-fix)

Exit code:
    0 = pass
    1 = fail (latinized Vietnamese detected)
"""

import re
import sys
import subprocess
from pathlib import Path

# Vietnamese diacritics -- all characters with tone marks
VIETNAMESE_DIACRITICS = set(
    "àáảãạăằẳẵắặâấầẩẫậđèéẻẽẹêềếểễệìíỉĩị"
    "òóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ"
    "ÀÁẢÃẠĂẰẲẴẮẶÂẤẦẨẪẬĐÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊ"
    "ÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴ"
)

# High-specificity Vietnamese words when written WITHOUT diacritics (teencode).
# These are unlikely to appear in English text, making false positives rare.
LATINIZED_VIETNAMESE_WORDS = frozenset({
    # Core function words (highest specificity)
    "khong", "duoc", "cua", "nguoi", "phai", "cac", "nhung", "nhieu",
    "hoac", "giua", "truoc", "luon", "duoi", "dung",
    # Content words
    "bao", "hiem", "dong", "thong", "chinh", "tinh", "nam", "tai", "sau",
    "voi", "cho", "co", "va", "mot", "ben", "qua", "khi", "den",
    "tu", "di", "lam", "nao", "neu", "thi", "ve", "hay", "ma",
    "rat", "len", "xuong", "vao",
    # Pronouns/demonstratives
    "toi", "ban", "anh", "chi", "em", "ay", "day", "do",
    # Quantifiers/prepositions
    "khac", "moi", "lon", "nho", "ca", "toan", "so", "tren",
    "trong", "ngoai", "can", "trai",
    # Time
    "tuan", "thang", "gio", "phut", "giay", "hom", "ngay",
    # Other common
    "dau", "tien", "sau", "cuoi", "dau", "giay",
    "thong", "tin", "tuc", "van", "ban", "phap", "luat",
    "hop", "dong", "so", "nhom",
})

# Files/directories to always skip
SKIP_DIRS = {
    ".git", "node_modules", ".smart-env", ".obsidian",
    ".playwright-mcp", "__pycache__",
}

# File patterns to skip
SKIP_PATTERNS = [re.compile(p) for p in [
    r"\.json$", r"\.txt$", r"\.log$", r"\.png$", r"\.jpg$",
    r"\.jpeg$", r"\.gif$", r"\.svg$", r"\.ico$", r"\.zip$",
    r"\.yaml$", r"\.yml$",
]]


def should_skip(path):
    """Return True if path should be skipped (binary, vendor, etc.)."""
    p = Path(path)
    for part in p.parts:
        if part in SKIP_DIRS:
            return True
    for pattern in SKIP_PATTERNS:
        if pattern.search(str(path)):
            return True
    return False


def has_vietnamese_diacritics(text):
    """Check if text contains any Vietnamese diacritic character (including 'd')."""
    return bool(set(text) & VIETNAMESE_DIACRITICS)


def strip_frontmatter(text):
    """Remove YAML frontmatter (between --- markers)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return text
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is not None:
        return "\n".join(lines[end_idx + 1:])
    return text


def extract_words(text):
    """Extract lowercase alphabetic words from text."""
    return re.findall(r"[a-zA-Z]+", text.lower())


def score_file(text):
    """
    Score file for latinized Vietnamese.

    Returns (is_latinized: bool, details: dict).

    Logic:
    1. If file has any Vietnamese diacritic character (including d) -> PASS
    2. If no diacritics found:
       a. Extract words
       b. Count how many match the LATINIZED_VIETNAMESE_WORDS set
       c. If >=5 matches AND ratio > 15% of total words -> FAIL (latinized)
       d. Otherwise -> PASS (likely English or non-Vietnamese)
    """
    content = strip_frontmatter(text)

    # Pass immediately if any diacritics found
    if has_vietnamese_diacritics(content):
        dc_count = sum(1 for c in content if c in VIETNAMESE_DIACRITICS)
        return False, {"reason": "co vietnamese diacritics", "diacritic_count": dc_count}

    words = extract_words(content)
    if not words:
        return False, {"reason": "empty or no text content"}

    # Count matches in our latinized Vietnamese word set
    vietnamese_like = sum(1 for w in words if w in LATINIZED_VIETNAMESE_WORDS)
    total_words = len(words)
    ratio = vietnamese_like / total_words if total_words > 0 else 0

    result = {
        "total_words": total_words,
        "vietnamese_like_words": vietnamese_like,
        "vietnamese_ratio": round(ratio, 3),
        "diacritic_count": 0,
    }

    # Threshold: >=5 matching words AND >15% of total
    if vietnamese_like >= 5 and ratio > 0.15:
        result["reason"] = (
            "latinized Vietnamese detected (khong co dau, "
            f"{vietnamese_like}/{total_words} words match Vietnamese patterns)"
        )
        return True, result

    return False, result


def get_staged_md_files():
    """Get list of staged .md files from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True, text=True, check=True,
            encoding="utf-8",
        )
        files = result.stdout.strip().split("\n")
        return [f for f in files if f.endswith(".md") and not should_skip(f)]
    except subprocess.CalledProcessError:
        print("[diacritics_check] WARNING: not a git repo", file=sys.stderr)
        return []


def main():
    args = sys.argv[1:]

    if args:
        # Scan specified files
        files = [f for f in args if not should_skip(f)]
    else:
        # Git pre-commit mode -- scan staged .md files
        files = get_staged_md_files()

    if not files:
        print("[diacritics_check] PASS: No .md files to check")
        sys.exit(0)

    failed = False

    for filepath in files:
        try:
            text = Path(filepath).read_text(encoding="utf-8")
        except FileNotFoundError:
            print(f"[diacritics_check] SKIP (not found): {filepath}")
            continue
        except Exception as e:
            print(f"[diacritics_check] ERROR reading {filepath}: {e}", file=sys.stderr)
            continue

        is_latinized, details = score_file(text)

        if is_latinized:
            ratio_pct = details.get("vietnamese_ratio", 0) * 100
            print(f"[diacritics_check] FAIL: {filepath}")
            print(f"       Reason: {details.get('reason')}")
            print(f"       Vietnamese-like words: {details.get('vietnamese_like_words')} / {details.get('total_words')} ({ratio_pct:.0f}%)")
            print(f"       Action: Add Vietnamese diacritics or mark as non-Vietnamese")
            failed = True
        else:
            reason = details.get("reason", "ok")
            print(f"[diacritics_check] PASS: {filepath} -- {reason}")

    if failed:
        print()
        print("[diacritics_check] ==================== REJECTED ====================")
        print("[diacritics_check] One or more files contain latinized Vietnamese (no diacritics).")
        print("[diacritics_check] Add full Vietnamese diacritics before committing.")
        print("[diacritics_check] To bypass: git commit --no-verify (not recommended)")
        print("[diacritics_check] ====================================================")
        sys.exit(1)

    print("[diacritics_check] PASS: All checks passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
