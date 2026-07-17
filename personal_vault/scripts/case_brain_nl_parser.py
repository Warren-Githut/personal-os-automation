#!/usr/bin/env python3
"""
case_brain_nl_parser.py

Minimal-brain-dump parser for L'Usine cases.
Handles four prefixes:
- [new case]
- [update case <fuzzy_name>] ... (append thread)
- [edit case <fuzzy_name>] ...  (in-place edit)
- [close case <fuzzy_name>]

Design constraints:
- No extra dependencies required
- Case-insensitive match
- Fuzzy title match: token overlap over slug + title (no difflib needed)
"""

from __future__ import annotations

import re
from pathlib import Path


VAULT_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_DIR = VAULT_ROOT / "_cases" / "active"
CLOSED_DIR = VAULT_ROOT / "_cases" / "closed"


SECTION_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Vấn đề": ("vấn đề", "van de", "vande", "vấn", "van", "issue", "problem"),
    "Bối cảnh": ("bối cảnh", "boi canh", "boicanh", "bối", "boi", "context", "background"),
    "Giải pháp đề xuất": (
        "giải pháp đề xuất",
        "giai pháp đề xuất",
        "giaiphapdexuat",
        "giải pháp",
        "giai pháp",
        "solution",
        "options",
        "approach",
    ),
    "Thành công": ("thành công", "thanh cong", "thanhcong", "success", "kết quả mong", "ket qua mong", "kết quả", "ket qua"),
}

FIELD_KEYWORDS: dict[str, tuple[str, ...]] = {
    "priority": ("priority", "ưu tiên", "uu tien", "uutien", "mức ưu tiên", "muc uu tien", "mucuutien"),
    "store": ("store", "cửa hàng", "cua hang", "cua", "store nào", "store nao", "store nào", "store nao"),
    "follow_up": ("follow up", "follow_up", "follow-up", "hẹn follow", "hen follow", "hẹn ngày", "ngày follow", "ngay follow", "due", "deadline"),
    "followup_event_id": ("followup_event_id", "calendar event", "event id", "event"),
    "tags": ("tags", "tag", "nhãn", "nhan", "labels"),
    "stakeholders": ("stakeholders", "liên quan", "lien quan", "lienquan", "người liên quan", "nguoi lien quan", "nguoilienquan"),
    "owner": ("owner", "người phụ trách", "nguoi phu trach", "nguoiphutrach", "phụ trách", "phu trach", "phutrach"),
    "title": ("title", "tiêu đề", "tieu de", "tiêu", "tieu"),
}


def detect_prefix(text: str) -> tuple[str, str, str]:
    normalized = text.strip()
    lowered = normalized.lower()

    # [new case] has no closing bracket - special handling
    if lowered.startswith("[new case"):
        remainder = normalized[len("[new case"):].lstrip(" ")
        if remainder.startswith("]"):
            payload = remainder[1:].lstrip(" ")
        else:
            payload = remainder
        return "[new case", "", payload

    for prefix in ("[close case", "[update case", "[edit case"):
        if lowered.startswith(prefix):
            remainder = normalized[len(prefix):].lstrip(" ")
            if remainder.startswith("]"):
                query = ""
                payload = remainder[1:].lstrip(" ")
            else:
                bracket_idx = remainder.find("]")
                if bracket_idx >= 0:
                    query = remainder[:bracket_idx].strip()
                    payload = remainder[bracket_idx + 1:].lstrip(" ")
                else:
                    query = remainder.strip()
                    payload = ""
            return prefix, query, payload

    return "", "", normalized


def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.split(" ")


def remove_common_prefix(slug: str) -> str:
    # Handles YYYY-MM-DD_ and YYYY-MM_ prefixes
    cleaned = re.sub(r"^\d{4}-\d{2}(?:-\d{2})?_", "", slug)
    return cleaned.replace("-", " ")


def overlap_score(query_tokens: list[str], target: str) -> float:
    target_tokens = tokenize(target)
    if not query_tokens or not target_tokens:
        return 0.0
    matches = sum(1 for token in query_tokens if token in target_tokens)
    return matches / max(len(query_tokens), len(target_tokens))


def find_case_files() -> list[Path]:
    return sorted(
        [p for p in list(ACTIVE_DIR.glob("*.md")) + list(CLOSED_DIR.glob("*.md")) if p.is_file()]
    )


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    content = path.read_text(encoding="utf-8")
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            front = content[3:end].strip()
            body = content[end + 3 :].lstrip("\n")
            data: dict[str, str] = {}
            for line in front.splitlines():
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                data[key.strip()] = value.strip()
            return data, body
    return {}, content


def format_frontmatter(data: dict[str, str]) -> str:
    lines = ["---"]
    for key in (
        "status",
        "store",
        "opened",
        "updated",
        "priority",
        "follow_up",
        "followup_event_id",
        "stakeholders",
        "owner",
        "title",
        "tags",
        "slug",
    ):
        if key in data:
            lines.append(f"{key}: {data[key]}")
    lines.append("---")
    return "\n".join(lines)


def _match_keywords(text: str, keyword_dict: dict[str, tuple[str, ...]]) -> str | None:
    normalized = text.strip().lower()
    for key, keywords in keyword_dict.items():
        if any(keyword in normalized for keyword in keywords):
            return key
    return None


def detect_section(text: str) -> str | None:
    return _match_keywords(text, SECTION_KEYWORDS)


def detect_field(text: str) -> str | None:
    return _match_keywords(text, FIELD_KEYWORDS)


def extract_update_text(payload: str) -> str:
    return payload.strip()


def find_case_by_query(query: str) -> Path | None:
    query_tokens = tokenize(query)
    if not query_tokens:
        return None

    candidates = find_case_files()
    best: tuple[float, Path | None] = (-1.0, None)
    for path in candidates:
        _, body = parse_frontmatter(path)
        # Extract title from first heading
        title = ""
        for line in body.splitlines():
            if line.strip().startswith("#"):
                title = line.strip().lstrip("# ")
                break

        slug_score = overlap_score(query_tokens, remove_common_prefix(path.stem))
        title_score = overlap_score(query_tokens, title)
        score = max(slug_score, title_score)
        if score > best[0]:
            best = (score, path)

    return best[1] if best and best[0] >= 0.35 else None


def build_update_entry(payload: str) -> str:
    from datetime import datetime

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"### {stamp} — Warren\n{payload.strip()}\n"


def split_frontmatter_and_body(case_text: str) -> tuple[str, str]:
    if case_text.startswith("---"):
        end = case_text.find("---", 3)
        if end != -1:
            front = case_text[: end + 3]
            body = case_text[end + 3 :].lstrip("\n")
            return front, body
    return "---\nstatus: active\n---\n", case_text


def inject_update_entry(body: str, entry: str) -> str:
    cleaned = body.strip()
    if not cleaned:
        return f"{entry}\n"
    return f"{entry}\n{cleaned}\n"


if __name__ == "__main__":
    print("case_brain_nl_parser loaded.")
