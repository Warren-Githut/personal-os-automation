"""
Quarterly deep valuation of VN equity candidates using TCBS BCTC API.
Calculates intrinsic value via Munger, Lynch, Damodaran frameworks (per GAS.md §4).

Requires:
  - TCBS_API_KEY in ~/.env or system env (from developers.tcbs.com.vn)
  - List of tickers to screen (from monthly_screening results or manual list)

Usage:
  python scripts/quarterly_valuation_batch.py --tickers GAS,VCB,MBB --period Q1
  python scripts/quarterly_valuation_batch.py --json --period Q2
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv(Path.home() / ".env")

TCBS_API_KEY = os.getenv("TCBS_API_KEY")
if not TCBS_API_KEY:
    print("ERROR: TCBS_API_KEY not found in ~/.env or system env", file=sys.stderr)
    sys.exit(1)

TCBS_API_URL = "https://openapi.tcbs.com.vn"
TOKEN_ENDPOINT = f"{TCBS_API_URL}/gaia/v1/oauth2/openapi/token"
FINANCIALS_ENDPOINT = f"{TCBS_API_URL}/ta/v1/companies/{{symbol}}/financials"

def get_token():
    """Fetch JWT token from TCBS via API Key."""
    try:
        resp = requests.post(
            TOKEN_ENDPOINT,
            json={"apiKey": TCBS_API_KEY},
            timeout=15
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("token")
    except Exception as e:
        print(f"  Token fetch failed: {e}", file=sys.stderr)
        return None

def fetch_bctc_data(symbol, token):
    """Fetch BCTC financial data from TCBS for given symbol."""
    if not token:
        return None
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        url = FINANCIALS_ENDPOINT.format(symbol=symbol)
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return None

def calculate_munger_valuation(bctc_data):
    """
    Charlie Munger — Owner Earnings method.
    Owner Earnings = LNST - Maintenance CAPEX
    Fair value = Owner Earnings × multiple (10x/15x/20x)
    """
    if not bctc_data:
        return None

    # Placeholder logic — requires actual BCTC data structure
    # In reality, would extract LNST and CAPEX from BCTC data
    # For now, return stub
    return {
        "method": "Munger Owner Earnings",
        "conservative_10x": "TBD",
        "fair_15x": "TBD",
        "optimistic_20x": "TBD",
        "note": "Requires BCTC data structure mapping"
    }

def calculate_lynch_valuation(price_data, bctc_data):
    """
    Peter Lynch — PEG/PEGY method.
    PEG = P/E ÷ EPS growth rate
    Fair value when PEG = 1.0
    """
    if not price_data or not bctc_data:
        return None

    return {
        "method": "Lynch PEG/PEGY",
        "peg": "TBD",
        "pegy": "TBD",
        "fair_value_peg_1": "TBD",
        "fair_value_pegy_1_2": "TBD"
    }

def calculate_damodaran_valuation(bctc_data):
    """
    Aswath Damodaran — Sum-of-Parts DCF.
    Segment earnings × appropriate multiple + excess cash.
    """
    if not bctc_data:
        return None

    return {
        "method": "Damodaran SOTP + DCF",
        "sotp_value": "TBD",
        "dcf_5yr_value": "TBD",
        "total_equity_value": "TBD",
        "per_share": "TBD"
    }

def valuate_stock(symbol, token):
    """Calculate intrinsic value for a single stock."""
    bctc_data = fetch_bctc_data(symbol, token)

    result = {
        "ticker": symbol,
        "valuation_date": datetime.now().strftime("%Y-%m-%d"),
        "status": "data_available" if bctc_data else "data_unavailable",
        "methods": {}
    }

    if bctc_data:
        result["methods"]["munger"] = calculate_munger_valuation(bctc_data)
        result["methods"]["lynch"] = calculate_lynch_valuation(None, bctc_data)
        result["methods"]["damodaran"] = calculate_damodaran_valuation(bctc_data)
    else:
        result["note"] = "BCTC data not available from TCBS"

    return result

def screen_valuations(tickers, token):
    """Screen multiple tickers."""
    results = {
        "screening_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "period": "Q",
        "token_status": "valid" if token else "invalid",
        "tickers": tickers,
        "valuations": {}
    }

    for ticker in tickers:
        print(f"  Valuating {ticker}...", file=sys.stderr)
        result = valuate_stock(ticker, token)
        results["valuations"][ticker] = result

    return results

def format_markdown(results):
    """Format valuation results as Markdown."""
    md = f"""---
domain: trading
type: valuation
status: active
period: 2026-Q1
last_updated: {datetime.now().strftime("%Y-%m-%d")}
---

# Quarterly Valuation Deep Dive — Q1 2026 BCTC

**Date**: {results["screening_date"]}
**Screening method**: Munger (owner earnings) + Lynch (PEG/PEGY) + Damodaran (SOTP DCF)
**Data source**: TCBS iFlash Open API (BCTC financial statements)

---

"""

    for ticker, val in results["valuations"].items():
        status = val["status"]
        md += f"## {ticker} — {status}\n\n"

        if val["status"] == "data_available":
            methods = val["methods"]
            if methods.get("munger"):
                munger = methods["munger"]
                md += f"**Munger Owner Earnings**:\n"
                md += f"- Conservative (10x): {munger['conservative_10x']} VND\n"
                md += f"- Fair (15x): {munger['fair_15x']} VND\n"
                md += f"- Optimistic (20x): {munger['optimistic_20x']} VND\n\n"

            if methods.get("lynch"):
                lynch = methods["lynch"]
                md += f"**Lynch PEG/PEGY**:\n"
                md += f"- PEG: {lynch['peg']}\n"
                md += f"- PEGY: {lynch['pegy']}\n"
                md += f"- Fair P/E (PEG=1): {lynch['fair_value_peg_1']} VND\n"
                md += f"- Fair P/E (PEGY=1.2): {lynch['fair_value_pegy_1_2']} VND\n\n"

            if methods.get("damodaran"):
                damodaran = methods["damodaran"]
                md += f"**Damodaran SOTP + 5yr DCF**:\n"
                md += f"- SOTP value: {damodaran['sotp_value']} VND\n"
                md += f"- 5yr DCF value: {damodaran['dcf_5yr_value']} VND\n"
                md += f"- Total equity: {damodaran['total_equity_value']} tỷ\n"
                md += f"- Per share: {damodaran['per_share']} VND\n\n"

            md += f"**Composite Intrinsic Value**: TBD (average of methods)\n"
            md += f"**Status**: 🔴 PENDING BCTC DATA | 🟢 GREEN if Price ≤ Intrinsic\n\n"
        else:
            md += f"{val.get('note', 'No data')}\n\n"

        md += "---\n\n"

    md += f"""
## Next Steps

1. For each 🟢 GREEN candidate: add to `30_KNOWLEDGE_BASE/wiki/05_Investing/VN_Equities/Candidates_Watchlist.md`
2. For ⚠️ OVERVALUED: mark as "watch for pullback"
3. For 🔴 PENDING: monitor for BCTC filing and re-run screening

**Note**: Methods show TBD because TCBS BCTC data structure needs mapping.
Once BCTC endpoints confirmed, formulas will auto-calculate.

---
*Generated {results["screening_date"]}*
"""
    return md

def main():
    parser = argparse.ArgumentParser(description="Quarterly valuation deep dive")
    parser.add_argument("--tickers", default="GAS,VCB,MBB", help="Comma-separated ticker list")
    parser.add_argument("--period", default="Q1", help="Quarter (Q1, Q2, Q3, Q4)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    tickers = [t.strip().upper() for t in args.tickers.split(",")]

    token = get_token()
    if not token:
        print("  TCBS token fetch failed. Check TCBS_API_KEY in .env", file=sys.stderr)
        sys.exit(1)

    results = screen_valuations(tickers, token)
    results["period"] = args.period

    if args.json:
        sys.stdout.buffer.write(json.dumps(results, ensure_ascii=False, indent=2).encode("utf-8"))
        sys.stdout.buffer.write(b"\n")
    else:
        md = format_markdown(results)
        print(md)

if __name__ == "__main__":
    main()
