#!/usr/bin/env python3
"""
stock_price_sync.py — Fetch live prices → sync to vault files.
Schedule: Mon-Fri 15:30 via Hermes cron (no_agent=True).

Updates:
  1. Candidates_Watchlist.md  → cột Giá
  2. Holdings.md              → cột Current price
  3. 030-Companies/*/Thesis.md → frontmatter current_price

Ticker list is AUTO-DETECTED from Candidates_Watchlist.md + Holdings.md
(no hardcoded list). Add a ticker to either file → next run picks it up.

Telegram report (HORION_Stock_Bot) with color:
  🟢 up / 🔴 down / 🟡 reference (vs last run, cached in .last_prices.json)
"""
import json, os, re, sys, time, urllib.request, urllib.error
from datetime import datetime

# ─── Config ──────────────────────────────────────────────────────────────
VAULT = "C:/Users/khoans/Documents/Personal_OS/personal_vault"
WIKI = f"{VAULT}/30_KNOWLEDGE_BASE/wiki/03_Investing/VN_Equities"
WATCHLIST = f"{WIKI}/Candidates_Watchlist.md"
HOLDINGS = f"{WIKI}/Holdings.md"
COMPANIES = f"{WIKI}/030-Companies"

# ─── Telegram (HORION_Stock_Bot) ────────────────────────────────────────
BOT_TOKEN = os.environ.get("HORION_STOCK_BOT_TOKEN")
CHAT_ID = "2117653672"
LAST_PRICES = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".last_prices.json")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
TIMEOUT = 10
EPOCH = 1672531200

# ─── Ticker auto-detection (replaces hardcoded TICKERS) ──────────────────

def extract_watchlist_tickers():
    """Quét bảng Candidates_Watchlist.md → tập mã (cột Mã).
    Handle cả single-pipe (| Mã |) và double-pipe (|| Mã |) trong cùng 1 table."""
    tickers = set()
    if not os.path.exists(WATCHLIST):
        return tickers
    with open(WATCHLIST, encoding="utf-8") as f:
        lines = f.read().split("\n")
    table_section = False
    for line in lines:
        if line.strip().startswith("|") and "Mã" in line and "Ngành" in line:
            table_section = True
            continue
        if table_section and line.strip().startswith("|") and "---" in line:
            continue
        if table_section and line.strip().startswith("|"):
            cols = line.split("|")
            # ticker có thể ở col 1 (single pipe) hoặc col 2 (double pipe)
            for c in (1, 2):
                if len(cols) > c:
                    raw = cols[c].strip()
                    t = re.sub(r'[^A-Za-z]', '', raw.split("[")[0].strip())
                    if t and 1 <= len(t) <= 4:
                        tickers.add(t.upper())
                        break
        elif table_section and not line.strip().startswith("|"):
            table_section = False
    return tickers

def extract_holdings_tickers():
    """Quét bảng Holdings.md → tập mã (cột Ticker)."""
    tickers = set()
    if not os.path.exists(HOLDINGS):
        return tickers
    with open(HOLDINGS, encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("|") and "Ticker" not in line and "---" not in line:
                cols = [c.strip() for c in line.split("|")]
                if len(cols) >= 2 and cols[1].isalpha() and 1 <= len(cols[1]) <= 4:
                    tickers.add(cols[1].upper())
    return tickers

def build_ticker_list():
    """Union watchlist + holdings."""
    return sorted(extract_watchlist_tickers() | extract_holdings_tickers())

# ─── Price Fetch (mirrors fetch_financials.py) ───────────────────────────

def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read())
    except Exception:
        return None

def get_price(ticker):
    now = int(time.time())
    data = fetch_json(
        f"https://services.entrade.com.vn/chart-api/v2/ohlcs/stock"
        f"?symbol={ticker}&from={EPOCH}&to={now}&resolution=1D"
    )
    if data and "c" in data:
        closes = [c for c in data["c"] if c is not None and c > 0]
        if len(closes) >= 20:
            return closes[-1]
    data = fetch_json(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}.VN"
        f"?range=2y&interval=1d"
    )
    if data:
        chart = data.get("chart", {}).get("result", [])
        if chart:
            q = chart[0].get("indicators", {}).get("quote", [{}])[0]
            closes = [c for c in q.get("close", []) if c is not None and c > 0]
            if len(closes) >= 20:
                return closes[-1]
    return None

def fetch_all(tickers):
    prices = {}
    failed = []
    for t in tickers:
        p = get_price(t)
        if p is not None:
            prices[t] = round(p, 1)
        else:
            failed.append(t)
    return prices, failed


# ─── Candidates_Watchlist.md — update cột Giá ────────────────────────────

def fmt_price(val):
    """Format price: Entrade API inconsistent — returns thousands (77=77k)
    for some tickers, actual VND (22150=22.150) for others.
    Heuristic: raw < 1000 → thousands format (x1000); else already VND."""
    if val < 1000:
        val = val * 1000
    return f"{val:,.0f}".replace(",", ".")

def update_watchlist(prices):
    if not os.path.exists(WATCHLIST):
        return "WATCHLIST: file not found"

    with open(WATCHLIST, encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    changed = False
    updated_tickers = set()
    table_section = False
    new_lines = []
    margin_col = 6  # default: Giá at col 6 (double-pipe table with empty leading cell)
    ticker_col = 2

    for line in lines:
        if line.strip().startswith("|") and "Mã" in line and "Ngành" in line:
            table_section = True
            cols = line.split("|")
            if cols[1].strip() == "Mã":
                ticker_col, margin_col = 1, 5
            elif len(cols) >= 3 and cols[2].strip() == "Mã":
                ticker_col, margin_col = 2, 6
            new_lines.append(line)
            continue
        if table_section and line.strip().startswith("|") and "---" in line:
            new_lines.append(line)
            continue
        if table_section and line.strip().startswith("|"):
            cols = line.split("|")
            if len(cols) > max(ticker_col, margin_col):
                ticker_raw = cols[ticker_col].strip()
                raw_ticker = ticker_raw.split("[")[0].strip()
                raw_ticker = re.sub(r'[^A-Za-z]', '', raw_ticker)
                if raw_ticker in prices:
                    old_price_raw = cols[margin_col]
                    new_price = fmt_price(prices[raw_ticker])
                    old_stripped = old_price_raw.strip()
                    if old_stripped != new_price:
                        leading = len(old_price_raw) - len(old_price_raw.lstrip())
                        trailing = len(old_price_raw) - len(old_price_raw.rstrip())
                        cols[margin_col] = " " * leading + new_price + " " * trailing
                        line = "|".join(cols)
                        changed = True
                        updated_tickers.add(raw_ticker)
            new_lines.append(line)
        else:
            if table_section and not line.strip().startswith("|"):
                table_section = False
            new_lines.append(line)

    new_text = "\n".join(new_lines)
    today = datetime.now().strftime("%Y-%m-%d")
    new_text = re.sub(
        r'^(last_updated:\s*).*', rf'\g<1>{today}',
        new_text, flags=re.MULTILINE
    )

    if changed:
        with open(WATCHLIST, "w", encoding="utf-8") as f:
            f.write(new_text)
        return f"WATCHLIST: updated {len(updated_tickers)} ticker prices ({', '.join(sorted(updated_tickers))})"
    return "WATCHLIST: no changes needed"


# ─── Holdings.md — update cột Current price ──────────────────────────────

def update_holdings(prices):
    if not os.path.exists(HOLDINGS):
        return "HOLDINGS: file not found"

    with open(HOLDINGS, encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    changed = False
    table_section = False
    new_lines = []

    for line in lines:
        if line.strip().startswith("|") and "Ticker" in line and "Shares" in line:
            table_section = True
            new_lines.append(line)
            continue
        if table_section and line.strip().startswith("|") and "---" in line:
            new_lines.append(line)
            continue
        if table_section and line.strip().startswith("|"):
            cols = [c.strip() for c in line.split("|")]
            if len(cols) >= 4:
                ticker = cols[1].strip().upper()
                if ticker in prices:
                    new_price = fmt_price(prices[ticker])
                    if len(cols) > 4:
                        old_p = cols[4].strip()
                        if old_p != new_price:
                            cols[4] = f" {new_price} "
                            line = "|".join(cols)
                            changed = True
            new_lines.append(line)
        else:
            if table_section and not line.strip().startswith("|"):
                table_section = False
            new_lines.append(line)

    if changed:
        with open(HOLDINGS, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))
        return "HOLDINGS: updated"

    data_rows = [l for l in lines if l.strip().startswith("|")
                 and "Ticker" not in l and "---" not in l
                 and len(l.split("|")) >= 4]
    if not data_rows:
        return "HOLDINGS: table empty -- nothing to update"
    return "HOLDINGS: no changes needed"


# ─── 030-Companies/*/Thesis.md — update frontmatter current_price ────────

def find_thesis_dirs():
    """Find all ticker dirs and their Thesis.md paths."""
    if not os.path.exists(COMPANIES):
        return {}
    result = {}
    for d in sorted(os.listdir(COMPANIES)):
        match = re.match(r'\d+-([A-Z]+)', d)
        if not match:
            continue
        ticker = match.group(1)
        thesis = os.path.join(COMPANIES, d, "Thesis.md")
        if os.path.exists(thesis):
            result[ticker] = thesis
    return result

def upsert_frontmatter_field(text, field, value):
    """Add or update a YAML frontmatter field."""
    pattern = re.compile(rf'^{re.escape(field)}:\s*.*', re.MULTILINE)
    if pattern.search(text):
        return pattern.sub(f'{field}: {value}', text)
    if text.startswith("---"):
        first_nl = text.index("\n", 3)
        return text[:first_nl + 1] + f'{field}: {value}\n' + text[first_nl + 1:]
    return text

def update_thesis_frontmatter(prices):
    thesis_files = find_thesis_dirs()
    if not thesis_files:
        return "THESIS: no company dirs found"

    changed = []
    today = datetime.now().strftime("%Y-%m-%d")

    for ticker, path in thesis_files.items():
        if ticker not in prices:
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()

        new_price = prices[ticker]
        new_price_str = f"{new_price:,.0f}".replace(",", "")

        before = text
        text = upsert_frontmatter_field(text, "current_price", new_price_str)
        text = upsert_frontmatter_field(text, "last_updated", today)
        if text != before:
            changed.append(ticker)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)

    if changed:
        return f"THESIS: updated {len(changed)} ticker(s): {', '.join(changed)}"
    return "THESIS: no changes needed"


# ─── Telegram report (color by vs last run) ──────────────────────────────

def load_last_prices():
    if os.path.exists(LAST_PRICES):
        try:
            with open(LAST_PRICES, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_last_prices(prices):
    with open(LAST_PRICES, "w", encoding="utf-8") as f:
        json.dump(prices, f, ensure_ascii=False)

def send_telegram(text):
    if not BOT_TOKEN:
        print("[!] HORION_STOCK_BOT_TOKEN missing - skip Telegram")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = json.dumps({
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"[!] Telegram send failed: {e}")

def build_telegram_msg(prices, last):
    lines = []
    up = dn = ref = 0
    for t in sorted(prices):
        p = prices[t]
        old = last.get(t)
        if old is None or abs(p - old) < 1e-6:
            icon, ref = "🟡", ref + 1
        elif p > old:
            icon, up = "🟢", up + 1
        else:
            icon, dn = "🔴", dn + 1
        lines.append(f"{icon} <b>{t}</b>: {fmt_price(p)}")
    header = f"Giá CK {datetime.now().strftime('%Y-%m-%d')}  🟢{up} 🔴{dn} 🟡{ref}"
    return header + "\n" + "\n".join(lines)


# ─── Main ─────────────────────────────────────────────────────────────────

def main(dry_run=False):
    today = datetime.now().strftime("%Y-%m-%d %H:%M")

    tickers = build_ticker_list()
    if not tickers:
        print(f"[FAIL] PRICE SYNC {today}: no tickers found in watchlist/holdings")
        sys.exit(1)

    prices, failed = fetch_all(tickers)
    if not prices:
        print(f"[FAIL] PRICE SYNC {today}: ALL TICKERS FAILED")
        sys.exit(1)

    if dry_run:
        print(f"[DRY] Tickers ({len(tickers)}): {', '.join(tickers)}")
        print(f"[DRY] Prices: {' | '.join(f'{t}={p}' for t, p in prices.items())}")
        if failed:
            print(f" [!] Failed: {', '.join(failed)}")
        print("[DRY] No files written. No Telegram sent.")
        return

    # Update files
    results = []
    results.append(update_watchlist(prices))
    results.append(update_holdings(prices))
    results.append(update_thesis_frontmatter(prices))

    # Telegram with color
    last = load_last_prices()
    send_telegram(build_telegram_msg(prices, last))
    save_last_prices(prices)

    # Output summary (stdout = cron delivery, ASCII-only safe)
    print(f"[PRICE] SYNC {today}")
    print(f"Tickers: {' | '.join(f'{t}={p}' for t, p in prices.items())}")
    if failed:
        print(f" [!] Failed: {', '.join(failed)}")
    print("---")
    for r in results:
        print(f"  {r}")
    print(f"---\n[OK] Done -- next run Mon-Fri 15:30")

if __name__ == "__main__":
    main("--dry-run" in sys.argv)
