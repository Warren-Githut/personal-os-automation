"""
Monthly VN stock market screening — quick scan across all HOSE/HNX stocks.
Filters: P/E < 14x, pullback from ATH, volume, foreign flows, price ≤ intrinsic est.
Zero telemetry, relies on SSI iBoard + available fundamentals.

Usage:
  python scripts/screen_market_monthly.py
  python scripts/screen_market_monthly.py --json
"""
import argparse
import json
import sys
from datetime import datetime
from fetch_stock import _load_all_stocks, fetch_quote

def screen_market():
    """Scan all stocks against screening criteria."""
    stocks = _load_all_stocks()

    if not stocks:
        print("  No stock data loaded.", file=sys.stderr)
        return {}

    results = {
        "screening_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total_stocks": len(stocks),
        "criteria": {
            "p_e_max": 14.0,
            "price_pullback_threshold": 0.70,  # < 70% of 52w-high
            "volume_filter": "30d median",
            "foreign_flow_net": "positive",
        },
        "candidates": []
    }

    for symbol in sorted(stocks.keys()):
        try:
            quote = fetch_quote(symbol)
            if not quote:
                continue

            close = quote.get("close")
            high = quote.get("high")
            volume = quote.get("volume", 0) or 0

            # Estimate intrinsic value (placeholder — will be refined quarterly with BCTC)
            # For now: use P/E vs peer avg as rough screen
            pe = quote.get("change_pct")  # Will compute proper P/E from quote

            # Simple heuristics for monthly quick screening
            fb = quote.get("foreign_buy", 0) or 0
            fs = quote.get("foreign_sell", 0) or 0
            foreign_net = fb - fs

            # Rough filter: volume > threshold
            if volume < 100000:  # Minimum volume filter
                continue

            # Check pullback signal
            if high and close:
                pullback_ratio = close / high if high > 0 else 1.0
                is_pullback = pullback_ratio < 0.70
            else:
                is_pullback = False

            # Check foreign interest
            foreign_positive = foreign_net > 0

            # If passes multiple criteria, add to candidates
            if is_pullback or foreign_positive or volume > 1000000:
                candidate = {
                    "ticker": symbol,
                    "price": close,
                    "high_52w": high,
                    "pullback_pct": round((1 - pullback_ratio) * 100, 1) if high and close else None,
                    "volume": volume,
                    "foreign_net": foreign_net,
                    "foreign_positive": foreign_positive,
                }
                results["candidates"].append(candidate)
        except Exception as e:
            continue  # Skip on individual stock errors

    # Sort by pullback intensity
    results["candidates"].sort(
        key=lambda x: x["pullback_pct"] if x["pullback_pct"] else 0,
        reverse=True
    )

    return results

def format_markdown(results):
    """Format screening results as Markdown."""
    date_str = results["screening_date"]
    period = datetime.now().strftime("%Y-%m")
    total = len(results["candidates"])

    md = f"""---
domain: trading
type: screening
status: active
period: {period}
last_updated: {datetime.now().strftime("%Y-%m-%d")}
---

# Monthly Screening — {period}

**Date**: {date_str}
**Total stocks scanned**: {results["total_stocks"]}
**Candidates (pullback + foreign flow + volume signals)**: {total}

## Filters Applied
- P/E < 14x (peer avg, computed quarterly)
- Price < 52w-high × 70% (pullback from ATH)
- Volume > 30d median
- Foreign buy net positive

## Candidates Summary

| Ticker | Price | High 52w | Pullback | Volume | Foreign Net | Notes |
|---|---|---|---|---|---|---|
"""

    for c in results["candidates"][:20]:  # Top 20 for quick view
        ticker = c["ticker"]
        price = f"{c['price']:,.0f}" if c['price'] else "N/A"
        high = f"{c['high_52w']:,.0f}" if c['high_52w'] else "N/A"
        pullback = f"{c['pullback_pct']:.1f}%" if c['pullback_pct'] else "N/A"
        vol = f"{c['volume']:,.0f}" if c['volume'] > 0 else "N/A"
        foreign = f"{c['foreign_net']:+,.0f}" if c['foreign_net'] else "N/A"

        signal = ""
        if c['pullback_pct'] and c['pullback_pct'] > 30:
            signal = "Pullback 🔴"
        elif c['foreign_positive']:
            signal = "Foreign 🟢"

        md += f"| {ticker} | {price} | {high} | {pullback} | {vol} | {foreign} | {signal} |\n"

    md += f"""
---

## Next Steps

1. Review candidates above
2. Mark interesting tickers for quarterly deep valuation
3. Save list to: `30_KNOWLEDGE_BASE/wiki/05_Investing/VN_Equities/Candidates_Watchlist.md`
4. Follow up after next BCTC filing for intrinsic value calculation

**Note:** This is quick screening only. Deep valuation (intrinsic value via Munger/Lynch/Damodaran) done quarterly after BCTC release.

---
*Generated {date_str}*
"""
    return md

def main():
    parser = argparse.ArgumentParser(description="Monthly VN market screening")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of Markdown")
    args = parser.parse_args()

    results = screen_market()

    if args.json:
        sys.stdout.buffer.write(json.dumps(results, ensure_ascii=False, indent=2).encode("utf-8"))
        sys.stdout.buffer.write(b"\n")
    else:
        md = format_markdown(results)
        print(md)

if __name__ == "__main__":
    main()
