"""
Fetch VN equity price via SSI iBoard public API.
Zero telemetry. Only dependency: requests.

Usage:
  python fetch_stock.py GAS
  python fetch_stock.py GAS FPT VNM
  python fetch_stock.py GAS --json        # machine-readable output
"""
import argparse
import json
import sys
from datetime import datetime

import requests

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
})

SSI_HOSE = "https://iboard-query.ssi.com.vn/stock/exchange/hose"
SSI_HNX = "https://iboard-query.ssi.com.vn/stock/exchange/hnx"

_cache: dict | None = None


def _load_all_stocks() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    stocks = {}
    for url in [SSI_HOSE, SSI_HNX]:
        try:
            resp = SESSION.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json().get("data", [])
            for item in data:
                symbol = item.get("stockSymbol")
                if symbol:
                    stocks[symbol] = item
        except Exception as e:
            print(f"  SSI fetch failed for {url}: {e}", file=sys.stderr)
    _cache = stocks
    return stocks


def fetch_quote(ticker: str) -> dict | None:
    stocks = _load_all_stocks()
    item = stocks.get(ticker.upper())
    if not item:
        print(f"  [{ticker}] Not found in SSI data", file=sys.stderr)
        return None

    best1_bid = item.get("best1Bid", 0) or 0
    best1_offer = item.get("best1Offer", 0) or 0

    return {
        "ticker": ticker.upper(),
        "company": item.get("companyNameEn", ""),
        "exchange": item.get("exchange", ""),
        "ref_price": item.get("refPrice"),
        "ceiling": item.get("ceiling"),
        "floor": item.get("floor"),
        "open": item.get("openPrice"),
        "high": item.get("highest"),
        "low": item.get("lowest"),
        "close": item.get("matchedPrice") or item.get("refPrice"),
        "volume": item.get("nmTotalTradedQty"),
        "value": item.get("nmTotalTradedValue"),
        "change": item.get("priceChange"),
        "change_pct": item.get("priceChangePercent"),
        "foreign_buy": item.get("nmFBuyVol"),
        "foreign_sell": item.get("nmFSellVol"),
        "best_bid": best1_bid,
        "best_offer": best1_offer,
        "as_of": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def print_human(quote: dict):
    t = quote["ticker"]
    close = quote["close"]
    ref = quote["ref_price"]
    chg = quote.get("change", 0) or 0
    pct = quote.get("change_pct", 0) or 0

    if close and ref:
        close_vnd = f"{close:,.0f}"
    else:
        close_vnd = "N/A"

    direction = "+" if chg >= 0 else ""
    vol = quote.get("volume", 0) or 0

    print(f"\n  {t} | {quote['company']}")
    print(f"  Price: {close_vnd} VND ({direction}{chg:,.0f} / {direction}{pct:.2f}%)")
    print(f"  Range: {quote.get('low', 'N/A'):,.0f} — {quote.get('high', 'N/A'):,.0f} | Ref: {ref:,.0f}")
    print(f"  Ceiling: {quote['ceiling']:,.0f} | Floor: {quote['floor']:,.0f}")
    print(f"  Volume: {vol:,.0f}")

    fb = quote.get("foreign_buy", 0) or 0
    fs = quote.get("foreign_sell", 0) or 0
    if fb or fs:
        net = fb - fs
        print(f"  Foreign: Buy {fb:,.0f} / Sell {fs:,.0f} / Net {net:+,.0f}")

    print(f"  As of: {quote['as_of']}")


def main():
    parser = argparse.ArgumentParser(description="Fetch VN equity quote (SSI public API, zero telemetry)")
    parser.add_argument("tickers", nargs="+", help="Stock ticker(s), e.g. GAS FPT")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of human-readable")
    args = parser.parse_args()

    results = {}
    for ticker in args.tickers:
        quote = fetch_quote(ticker)
        if quote:
            results[ticker.upper()] = quote

    if args.json:
        sys.stdout.buffer.write(json.dumps(results, ensure_ascii=False, indent=2).encode("utf-8"))
        sys.stdout.buffer.write(b"\n")
    else:
        for quote in results.values():
            print_human(quote)
        print()


if __name__ == "__main__":
    main()
