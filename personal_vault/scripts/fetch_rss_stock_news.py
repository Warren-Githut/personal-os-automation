"""
Fetch VN stock news from RSS (VnExpress + cafef) -> filter by age+relevance -> personal vault.
Only includes:
  - Articles < 24h old from trigger time
  - Content tied to: macro/micro economics, interest rates, watched tickers, long-term structural themes
Excludes: product launches, consumer goods, lifestyle features.

Usage:
  python scripts/fetch_rss_stock_news.py             # news from 24h ago
  python scripts/fetch_rss_stock_news.py --since HH   # news since HH:00 today (e.g. --since 08)

Output:
  Prepends to personal_vault/10_PULSE/022_VNStock_Daily_Outlook.md
  Errors -> personal_vault/scripts/_rss_fetch_log.txt
"""
import json
import logging
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

# --- Paths ---
VAULT_ROOT = Path(__file__).resolve().parents[1]
PULSE_FILE = VAULT_ROOT / "10_PULSE" / "022_VNStock_Daily_Outlook.md"
LOG_FILE = VAULT_ROOT / "scripts" / "_rss_fetch_log.txt"
FETCH_STOCK_SCRIPT = VAULT_ROOT / "scripts" / "fetch_stock.py"

RSS_SOURCES = {
    "VnExpress Kinh doanh": "https://vnexpress.net/rss/kinh-doanh.rss",
    "cafef Thị trường CK": "https://cafef.vn/thi-truong-chung-khoan.rss",
}
TIMEOUT = 20

# Tickers for price snapshot
PRICE_TICKERS = ["GAS", "NLG", "NVL", "FPT"]

# --- Relevance: WATCHED TICKERS + COMPANY NAMES ---
WATCHED_TICKERS = {"GAS", "NLG", "NVL", "FPT"}
WATCHED_COMPANIES = {
    "petrolimex", "gas", "petrovietnam", "pvn", "bsr", "pvd", "pvs",
    "novaland", "nam long", "nlg", "nvl",
    "fpt", "masan", "msn",
    "vietcombank", "vcb", "bidv", "viettinbank", "ctg",
    "techcombank", "tcb", "mbbank", "mbb", "vpbank", "vpb",
    "sacombank", "stb", "acb",
    "vinfast", "vingroup", "vhm", "vic",
    "becamex", "bcm",
}

# --- Relevance: MACRO + SECTOR KEYWORDS ---
MACRO_KEYWORDS = {
    "gdp", "cpi", "lam phat", "lạm phát", "lai suat", "lãi suất",
    "tang truong", "tăng trưởng", "tin dung", "tín dụng",
    "xuat khau", "xuất khẩu", "nhap khau", "nhập khẩu",
    "dau tu", "đầu tư", "dau tu cong", "đầu tư công",
    "thue", "thuế", "thue thu nhap", "thuế thu nhập",
    "ngan hang nha nuoc", "ngân hàng nhà nước",
    "vi mo", "vĩ mô", "kinh te", "kinh tế",
    "trai phieu", "trái phiếu",
}

STOCK_KEYWORDS = {
    "vn-index", "chung khoan", "chứng khoán", "co phieu", "cổ phiếu",
    "thanh khoan", "thanh khoản", "nang hang", "nâng hạng",
    "khoi ngoai", "khối ngoại", "ban rong", "bán ròng", "mua rong",
    "etf", "ipo", "dau tu nuoc ngoai", "đầu tư nước ngoài",
    "co phan hoa", "cổ phần hóa", "thoai von", "thoái vốn",
    "von hoa", "vốn hóa", "dinh gia", "định giá",
    "co tuc", "cổ tức", "esop",
    "hose", "hsx", "vn30",
}

SECTOR_KEYWORDS = {
    "ngan hang", "ngân hàng", "tai chinh", "tài chính",
    "bat dong san", "bất động sản",
    "dau khi", "dầu khí", "nang luong", "năng lượng",
    "dien", "điện", "dien luc", "điện lực",
    "cong nghe", "công nghệ", "ban dan", "bán dẫn",
    "hoa chat", "hóa chất", "phan bon", "phân bón",
    "thep", "thép", "xi mang", "xi măng",
    "hang khong", "hàng không",
    "ban le", "bán lẻ",
}

EXCLUDE_KEYWORDS = {
    "ra mat", "ra mắt", "san pham moi", "sản phẩm mới",
    "khuyen mai", "khuyến mãi", "giam gia", "giảm giá",
    "omachi", "my tom", "mì tôm",
    "do choi", "đồ chơi", "thoi trang", "thời trang",
    "lam dep", "làm đẹp", "am thuc", "ẩm thực",
    "the thao", "thể thao", "world cup",
    "xe hoi", "xe hơi", "oto",
    "cay xang", "cây xăng", "xang e10", "xang dau",
    "dua gai", "trung tam thuong mai",
}

VN_TZ = timezone(timedelta(hours=7))

# --- Logging ---
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)

RSS_DATE_FMTS = [
    "%a, %d %b %Y %H:%M:%S %z",
    "%a, %d %b %Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%S",
]


def parse_rss_date(date_str: str) -> datetime | None:
    """Try multiple formats for RSS date strings."""
    date_str = date_str.strip()
    for fmt in RSS_DATE_FMTS:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def is_relevant(title: str, cutoff: datetime) -> bool:
    """Check if article passes age + relevance filters."""
    tl = title.lower().strip()

    # EXCLUDE: skip obvious noise
    for kw in EXCLUDE_KEYWORDS:
        if kw in tl:
            return False

    # INCLUDE: watched tickers
    for t in WATCHED_TICKERS:
        # Match whole word or compound
        if re.search(rf'\b{re.escape(t)}\b', tl):
            return True

    # INCLUDE: watched company names
    for c in WATCHED_COMPANIES:
        if c in tl:
            return True

    # INCLUDE: macro keywords
    for kw in MACRO_KEYWORDS:
        if kw in tl:
            return True

    # INCLUDE: stock market keywords
    for kw in STOCK_KEYWORDS:
        if kw in tl:
            return True

    # INCLUDE: sector keywords
    for kw in SECTOR_KEYWORDS:
        if kw in tl:
            return True

    return False


def fetch_rss(url: str) -> list[dict] | None:
    """Fetch and parse RSS items."""
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        resp.encoding = "utf-8"
    except requests.RequestException as e:
        logging.error(f"HTTP failed {url}: {e}")
        return None

    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError as e:
        logging.error(f"XML parse failed {url}: {e}")
        return None

    items = []
    for item in root.iter("item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        pub_date = item.findtext("pubDate", "") or item.findtext("dc:date", "")
        if title:
            items.append({"title": title, "link": link, "pub_date": pub_date})
    return items


def fetch_prices() -> str:
    """Live price snapshot via fetch_stock.py."""
    result_lines = []
    for ticker in PRICE_TICKERS:
        try:
            r = subprocess.run(
                [sys.executable, str(FETCH_STOCK_SCRIPT), ticker, "--json"],
                capture_output=True, text=True, timeout=30, cwd=VAULT_ROOT,
            )
            if r.returncode != 0:
                continue
            data = json.loads(r.stdout)
            q = data.get(ticker.upper())
            if not q:
                continue
            close = q.get("close", "N/A")
            change = q.get("change", 0) or 0
            pct = q.get("change_pct", 0) or 0
            direction = "+" if change >= 0 else ""
            result_lines.append(
                f"- **{ticker.upper()}**: {close:,.0f} ({direction}{change:,.0f} / {direction}{pct:.2f}%)"
            )
        except Exception as e:
            logging.warning(f"Price {ticker} failed: {e}")
    if result_lines:
        return "**Gia tham chieu:**\n" + "\n".join(result_lines)
    return ""


def format_entry(items: list[dict], price_block: str, cutoff: datetime) -> str:
    """Build markdown entry with filtered items grouped by theme."""
    today_str = datetime.now(VN_TZ).strftime("%Y-%m-%d")
    now_time = datetime.now(VN_TZ).strftime("%H:%M")
    cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M")

    lines = [f"## {today_str} ({now_time})"]
    lines.append(f"*Tin tu {cutoff_str} toi nay — VnExpress + cafef*")
    lines.append("")

    if price_block:
        lines.append(price_block)
        lines.append("")

    if not items:
        lines.append("*Khong co tin phu hop trong 24h qua.*")
        lines.append("")
        lines.append("---")
        lines.append("")
        return "\n".join(lines)

    # Group by rough theme (no strict categories, just keywords)
    def guess_theme(t: str) -> str:
        tl = t.lower()
        if any(k in tl for k in ["vn-index", "chung khoan", "co phieu", "vnindex",
                                  "thanh khoan", "nang hang", "khoi ngoai",
                                  "ban rong", "ipo"]):
            return "📈 Thi truong chung khoan"
        if any(k in tl for k in MACRO_KEYWORDS):
            return "🏛️ Kinh te vi mo"
        if any(k in tl for k in ["ngan hang", "ngân hàng", "lai suat", "lãi suất",
                                  "tin dung", "tín dụng"]):
            return "🏦 Ngan hang & Lai suat"
        if any(k in tl for k in ["dau khi", "dầu khí", "nang luong", "năng lượng",
                                  "gas", "petrolimex"]):
            return "⛽ Nang luong & Dau khi"
        if any(k in tl for k in ["bat dong san", "bất động sản", "novaland",
                                  "nvl", "nlg", "nam long"]):
            return "🏗️ Bat dong san"
        if any(k in tl for k in ["vang", "vàng", "kim loai"]):
            return "🥇 Vang & Hang hoa"
        if any(k in tl for k in ["fpt", "masan", "vinfast", "vingroup",
                                  "doanh nghiep", "doanh nghiệp",
                                  "san xuat", "sản xuất"]):
            return "🏢 Doanh nghiep"
        return "📊 Kinh te & Dau tu"

    themed: dict[str, list[dict]] = {}
    for item in items:
        theme = guess_theme(item["title"])
        themed.setdefault(theme, []).append(item)

    # Ordered output
    order = ["📈 Thi truong chung khoan", "🏛️ Kinh te vi mo",
             "🏦 Ngan hang & Lai suat", "⛽ Nang luong & Dau khi",
             "🏗️ Bat dong san", "🥇 Vang & Hang hoa", "🏢 Doanh nghiep",
             "📊 Kinh te & Dau tu"]
    for theme in order:
        items_in_theme = themed.pop(theme, [])
        if not items_in_theme:
            continue
        lines.append(f"**{theme}:**")
        for item in items_in_theme:
            lines.append(f"- [{item['title']}]({item['link']})")
        lines.append("")

    lines.append(f"_{today_str} — tu VnExpress + cafef_")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def prepend_to_file(filepath: Path, new_entry: str):
    """Prepend entry after the template marker. Keep frontmatter + template on top."""
    if filepath.exists():
        existing = filepath.read_text(encoding="utf-8")
        # Insert right after `-->` that closes the Template comment
        m = re.search(r"(-->)\n*$", existing, re.MULTILINE)
        if m:
            content = existing[:m.end()] + "\n\n" + new_entry + "\n" + existing[m.end():].lstrip("\n")
        else:
            content = new_entry + "\n\n" + existing
    else:
        content = new_entry
    filepath.write_text(content, encoding="utf-8")


def deduplicate(items: list[dict]) -> list[dict]:
    """Dedup by title."""
    seen = set()
    result = []
    for item in items:
        clean = item["title"].strip().lower()
        if clean not in seen:
            seen.add(clean)
            result.append(item)
    return result


def parse_args():
    """Parse --since HH argument."""
    import argparse
    parser = argparse.ArgumentParser(description="VN stock RSS news scraper")
    parser.add_argument("--since", type=int, default=None,
                        help="Hour today to use as cutoff (e.g. 08 = 08:00 today). Default: 24h ago")
    return parser.parse_args()


def main():
    args = parse_args()
    now = datetime.now(VN_TZ)
    if args.since is not None:
        cutoff = now.replace(hour=args.since, minute=0, second=0, microsecond=0)
    else:
        cutoff = now - timedelta(hours=24)
    logging.info(f"=== Run at {now.strftime('%H:%M %Y-%m-%d')}, cutoff >= {cutoff.strftime('%H:%M')} ===")

    # Fetch RSS
    all_items = []
    sources_ok = 0
    for name, url in RSS_SOURCES.items():
        items = fetch_rss(url)
        if items is not None:
            sources_ok += 1
            logging.info(f"{name}: {len(items)} raw items")
            all_items.extend(items)
        else:
            logging.warning(f"{name}: FAILED")

    if sources_ok == 0:
        logging.error("All RSS sources failed")
        print("ERROR: All RSS failed. See log.", file=sys.stderr)
        sys.exit(1)

    # Dedup
    all_items = deduplicate(all_items)
    logging.info(f"After dedup: {len(all_items)}")

    # Filter: age + relevance
    before_filter = len(all_items)
    filtered = []
    skipped_age = 0
    skipped_relevance = 0
    for item in all_items:
        pub_dt = parse_rss_date(item["pub_date"]) if item["pub_date"] else None
        if pub_dt is None:
            # Can't parse date? Keep with warning
            logging.warning(f"No date: {item['title'][:60]}")
            continue
        if pub_dt < cutoff:
            skipped_age += 1
            continue
        if not is_relevant(item["title"], cutoff):
            skipped_relevance += 1
            continue
        filtered.append(item)

    logging.info(f"Filter: {before_filter} -> {len(filtered)} kept ({skipped_age} age, {skipped_relevance} relevance)")

    # Prices
    price_block = fetch_prices()
    logging.info(f"Prices: {'OK' if price_block else 'skip'}")

    # Format + write
    entry = format_entry(filtered, price_block, cutoff)
    PULSE_FILE.parent.mkdir(parents=True, exist_ok=True)
    prepend_to_file(PULSE_FILE, entry)
    logging.info(f"Written: {len(filtered)} items to {PULSE_FILE.name}")
    print(f"OK — {len(filtered)} relevant news items written (filtered {skipped_age}+{skipped_relevance} out of {before_filter})")


if __name__ == "__main__":
    main()
