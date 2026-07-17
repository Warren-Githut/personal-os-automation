#!/usr/bin/env python3
"""
Fetch broker reports from Gmail → extract PDF text → classify → append to vault pulse files.
Top 10 VN securities companies.
"""

import base64
import json
import os
import re
import sys
import tempfile
import time
import threading
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

# SSRF Protection: Allowed PDF domains only
ALLOWED_PDF_DOMAINS = {
    'static.tcbs.com.vn',
    'vps.com.vn',
    'vndirect.com.vn',
    'ssi.com.vn',
    'hsc.com.vn',
    'vci.com.vn',
    'kisvn.com',
    'tps.com.vn',
    'mas.com.vn',
    'bvsc.com.vn',
    'fpts.com.vn',
    'mbs.com.vn',
}


def is_safe_pdf_url(url: str) -> bool:
    """Validate URL against SSRF: HTTPS only, allowed domain, no private IPs."""
    from urllib.parse import urlparse
    import ipaddress
    import socket

    try:
        parsed = urlparse(url)
    except Exception:
        return False

    if parsed.scheme != 'https':
        return False

    hostname = parsed.hostname or ''
    if hostname not in ALLOWED_PDF_DOMAINS:
        return False

    try:
        ip_str = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_str)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            print(f"    ⛔ Blocked SSRF: {hostname} resolves to private/reserved IP {ip}")
            return False
    except Exception as e:
        print(f"    ⛔ Blocked SSRF: Failed to resolve {hostname}: {e}")
        return False

    return True


# Simple Token Bucket Rate Limiter
class TokenBucket:
    def __init__(self, rate: int, per_seconds: int):
        self.rate = rate
        self.per = per_seconds
        self.tokens = float(rate)
        self.last = time.time()
        self.lock = threading.Lock()

    def take(self):
        with self.lock:
            now = time.time()
            elapsed = now - self.last
            self.tokens = min(self.rate, self.tokens + elapsed * self.rate / self.per)
            if self.tokens < 1:
                wait = (1 - self.tokens) * self.per / self.rate
                time.sleep(wait)
                self.tokens = 0
            else:
                self.tokens -= 1
            self.last = now


# Rate limiters (configure conservatively)
GMAIL_RATE_LIMITER = TokenBucket(rate=15, per_seconds=60)      # 15 req/min
OPENROUTER_RATE_LIMITER = TokenBucket(rate=30, per_seconds=60)  # 30 req/min

# Add google-workspace scripts to path
GW_SCRIPTS = Path("C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/skills/productivity/google-workspace/scripts")
sys.path.insert(0, str(GW_SCRIPTS))
from google_api import build_service

VAULT_ROOT = Path("C:/Users/khoans/Documents/Personal_OS/personal_vault")
PULSE_DIR = VAULT_ROOT / "10_PULSE"
INBOX_PROCESSED = VAULT_ROOT / "_inbox" / "02_processed_archived"

# Top 10 VN securities (name, domain)
BROKERS = [
    ("VPS", "vps.com.vn"),
    ("VNDirect", "vndirect.com.vn"),
    ("SSI", "ssi.com.vn"),
    ("TCBS", "tcbs.com.vn"),
    ("HSC", "hsc.com.vn"),
    ("VCI", "vci.com.vn"),
    ("KIS", "kisvn.com"),
    ("TPS", "tps.com.vn"),
    ("MAS", "mas.com.vn"),
    ("BVSC", "bvsc.com.vn"),
    ("FPTS", "fpts.com.vn"),
    ("MB Securities", "mbs.com.vn"),
]

# Known forwarders/analysts who forward broker reports
FORWARDERS = [
    ("Jed Bonne", "bonnejed@gmail.com"),  # Actual email from Gmail
]

# Additional email sources (personal analysts, newsletters, etc.)
EXTRA_SOURCES = [
    ("Bonnejed", "bonnejed@gmail.com"),
]

# LLM Client Configuration
MAX_TOKENS_PER_RUN = 8000
LLM_TIMEOUT_SECONDS = 60


def _get_openrouter_key() -> str:
    """Get OpenRouter API key from auth.json."""
    import json
    auth_path = Path("C:/Users/khoans/AppData/Local/hermes/profiles/personal_profile/auth.json")
    if auth_path.exists():
        with open(auth_path) as f:
            data = json.load(f)
        # Try to get the key from openrouter credential
        for cred in data.get("credential_pool", {}).get("openrouter", []):
            if cred.get("source") == "env:OPENROUTER_API_KEY":
                # The key is stored in the env var, we need to get it from the actual value
                # For now, we'll need to read it from the env or another source
                pass
    # Fallback: try to get from environment
    import os
    key = os.getenv("OPENROUTER_API_KEY")
    if key:
        return key
    # Try to read directly from the .env file
    env_path = Path("C:/Users/khoans/AppData/Local/hermes/profiles/personal_profile/.env")
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.startswith("OPENROUTER_API_KEY="):
                    return line.strip().split("=", 1)[1]
    raise RuntimeError("OpenRouter API key not found")


async def call_llm(prompt: str) -> str:
    """Call OpenRouter API using key from auth.json credential pool."""
    import json as json_lib
    import urllib.request
    import os
    import asyncio

    def _sync_call():
        # Rate limit OpenRouter
        OPENROUTER_RATE_LIMITER.take()
        # Load OpenRouter key from auth.json credential pool
        auth_path = Path("C:/Users/khoans/AppData/Local/hermes/profiles/personal_profile/auth.json")
        with open(auth_path) as f:
            data = json.load(f)

        # Get OpenRouter key from credential_pool
        openrouter_creds = data.get("credential_pool", {}).get("openrouter", [])
        api_key = None
        for cred in openrouter_creds:
            if cred.get("source") == "env:OPENROUTER_API_KEY":
                # Try to get actual key from env or .env
                api_key = os.getenv("OPENROUTER_API_KEY")
                break

        # Fallback: read from .env file directly
        if not api_key:
            env_path = Path("C:/Users/khoans/AppData/Local/hermes/profiles/personal_profile/.env")
            if env_path.exists():
                with open(env_path) as f:
                    for line in f:
                        if line.startswith("OPENROUTER_API_KEY="):
                            api_key = line.strip().split("=", 1)[1]
                            break

        if not api_key or api_key == "***":
            raise RuntimeError("OpenRouter API key not found or invalid in auth.json/.env")

        url = "https://openrouter.ai/api/v1/chat/completions"

        data = {
            "model": "deepseek/deepseek-chat-v3.1",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a financial analyst extracting structured data from Vietnamese broker reports. Output ONLY valid JSON matching the specified schema."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 4000,
            "response_format": {"type": "json_object"}
        }

        req = urllib.request.Request(
            url,
            data=json_lib.dumps(data).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

        response = urllib.request.urlopen(req, timeout=LLM_TIMEOUT_SECONDS)
        response_data = json_lib.loads(response.read().decode("utf-8"))

        if not response_data.get("choices"):
            raise RuntimeError(f"LLM returned no choices: {response_data}")

        message = response_data["choices"][0].get("message", {})
        content = message.get("content")
        if not content:
            raise RuntimeError(f"LLM returned empty content: {response_data}")

        return content.strip()

    try:
        return await asyncio.to_thread(_sync_call)
    except Exception as e:
        print(f"    ⚠️  LLM call via OpenRouter failed: {e}")
        raise


# LLM Client Configuration
MAX_TOKENS_PER_RUN = 8000
LLM_TIMEOUT_SECONDS = 60


# Keywords to search in subject/body for broker content
BROKER_KEYWORDS = [
    "tcb", "tcbs", "vndirect", "vps", "ssi", "hsc", "vci", "kis", "tps", "mas", "bvsc", "fpts",
    "hòa phát", "hp", "ma", "vnindex", "vn-index", "khối ngoại", "chứng khoán", "báo cáo",
    "nhận định", "triển vọng", "market outlook", "khuyến nghị", "target price", "cổ phiếu"
]

# Skip keywords (statements, không phải weekly report)
SKIP_KEYWORDS = [
    "sao kê", "sao kê tài khoản", "sao kê tổng hợp", "trading account statement",
    "tradingaccountstatement", "accountstatement", "sao_ke", "sao_khoan",
    "e-statement", "account statement", "kia formal", "receipt", "invoice", "hóa đơn",
    "confirmation", "xác nhận giao dịch", "trade confirmation"
]


def should_skip(subject, attachments):
    """Check if message should be skipped (statements, confirmations, etc.)"""
    subject_lower = subject.lower()
    # Check subject
    if any(k in subject_lower for k in SKIP_KEYWORDS):
        return True
    # Check attachment filenames
    for filename, _ in attachments:
        fname_lower = filename.lower()
        if any(k in fname_lower for k in SKIP_KEYWORDS):
            return True
    return False


def build_query_blocks(days=7):
    """Build 3 separate Gmail query blocks to avoid Gmail API OR-combination limit."""
    # Block 1: Direct brokers - require PDF attachment
    broker_parts = [f"from:{d}" for _, d in BROKERS]
    broker_query = f"({' OR '.join(broker_parts)}) has:attachment filename:pdf newer_than:{days}d"

    # Block 2: Forwarders + extra sources - may only have tracking links (no attachment)
    forwarder_parts = [f"from:{d}" for _, d in FORWARDERS]
    extra_parts = [f"from:{d}" for _, d in EXTRA_SOURCES]
    forwarder_query = f"({' OR '.join(forwarder_parts + extra_parts)}) newer_than:{days}d"

    # Block 3: Keywords fallback
    keyword_query = " OR ".join([f"({k})" for k in BROKER_KEYWORDS])
    keyword_query = f"({keyword_query}) newer_than:{days}d"

    return [broker_query, forwarder_query, keyword_query]


def build_query(days=7):
    """Build combined query (kept for backward compat / dry-run display)."""
    blocks = build_query_blocks(days)
    return " OR ".join(blocks)


def classify_route(text):
    """Classify: weekly, macro, sector, daily"""
    t = text.lower()
    # Weekly report indicators
    if any(k in t for k in ["tuần", "weekly", "review", "xu hướng tuần", "sector flow", "dòng tiền", "portfolio", "watchlist", "theo dõi", "khối ngoại tuần", "báo cáo tuần", "weekly report", "market outlook", "triển vọng", "chiến lược tuần"]):
        return "weekly"
    # Macro indicators
    if any(k in t for k in ["fed", "lãi suất", "interest rate", "gdp", "cpi", "inflation", "ngân hàng trung ương", "macro", "vĩ mô", "chính sách tiền tệ", "geopolitics", "địa chính trị", "usd/vnd", "dollar", "lãi suất fed"]):
        return "macro"
    # Sector indicators
    if any(k in t for k in ["ngành", "sector", "group", "nhóm", "phân tích ngành", "cập nhật ngành", "sector report", "industry"]):
        return "sector"
    # Monthly report with market outlook -> weekly
    if any(k in t for k in ["báo cáo tháng", "monthly report", "market outlook", "tổng quan thị trường", "thị trường chứng khoán", "triển vọng tháng", "monthly outlook"]):
        return "weekly"
    # Broker research reports with tickers/analysis -> weekly
    if any(k in t for k in ["khuyến nghị", "recommendation", "target price", "mục tiêu giá", "đánh giá", "phân tích", "analysis", "cổ phiếu", "stock pick"]):
        return "weekly"
    return "daily"


def extract_tickers(text):
    """Extract VN stock tickers from text"""
    known = {"GAS","NLG","NVL","FPT","VIC","VHM","VCB","BID","CTG","TCB","MBB","VPB",
             "HPG","HSG","NKG","PNJ","MWG","MSN","SAB","BVH","GMD","DHG","IMP","KDH",
             "POW","PVD","PVS","PLX","STB","EIB","MSB","SHB","ACB","TCH","OCB","LPB",
             "ABB","VND","SSI","VCI","HCM","BCM","TCM","BSI","VIX","VNM","MAS","HSC","KIS","BVSC","FPTS","TPS","VPS"}
    found = set(re.findall(r'\b([A-Z]{3})\b', text.upper()))
    return sorted([t for t in found if t in known])


def extract_pdf_text(pdf_path):
    """Extract text using pymupdf"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        if doc.is_encrypted:
            # Try common passwords for broker statements
            for pwd in ["", "12345678", "00000000"]:
                if doc.authenticate(pwd):
                    break
            else:
                return f"[ENCRYPTED: {doc.metadata.get('title', 'Unknown')}]"
        text = ""
        for page in doc:
            text += page.get_text()
        return text[:10000]  # Limit size
    except Exception as e:
        return f"[EXTRACTION ERROR: {e}]"


def extract_pdf_urls(text):
    """Extract PDF URLs from email body (tracking links to broker PDFs)"""
    # Pattern for TCBS tracking links and direct static.tcbs.com.vn PDF links
    pdf_urls = []
    
    # TCBS tracking links (awstrack.me)
    tcbs_pattern = r'https?://[^\s<>"]*\.pdf'
    urls = re.findall(tcbs_pattern, text)
    for url in urls:
        if 'static.tcbs.com.vn' in url or 'awstrack.me' in url:
            if url not in pdf_urls:
                pdf_urls.append(url)
    
    # Direct broker PDF links
    broker_pdf_domains = ['static.tcbs.com.vn', 'vps.com.vn', 'vndirect.com.vn', 'ssi.com.vn',
                          'hsc.com.vn', 'vci.com.vn', 'kisvn.com', 'tps.com.vn',
                          'mas.com.vn', 'bvsc.com.vn', 'fpts.com.vn']
    for u in urls:
        for domain in broker_pdf_domains:
            if domain in u and u not in pdf_urls:
                pdf_urls.append(u)
                break
    
    return pdf_urls


def extract_pdf_url_from_tracking(url: str) -> str:
    """Extract actual PDF URL from tracking links (e.g., awstrack.me)."""
    # Pattern: https://tracking.domain/L0/https:%2F%2Factual.pdf
    # First decode the URL, then extract
    import urllib.parse
    
    # Decode the URL first
    decoded = urllib.parse.unquote(url)
    
    # Try to find encoded URL after common tracking patterns on decoded URL
    patterns = [
        r'/L0/(https://.+)',  # awstrack.me style (after decoding)
        r'/click/(https://.+)',  # generic click tracking
        r'\?url=(https://.+)',  # query param
    ]
    
    for pattern in patterns:
        import re
        match = re.search(pattern, decoded)
        if match:
            extracted = match.group(1)
            if extracted.lower().endswith('.pdf'):
                return extracted
    
    # Fallback: try original URL patterns
    for pattern in [r'/L0/(https%3A%2F%2F.+)', r'/click/(https%3A%2F%2F.+)', r'\?url=(https%3A%2F%2F.+)']:
        match = re.search(pattern, url)
        if match:
            encoded = match.group(1)
            try:
                decoded_part = urllib.parse.unquote(encoded)
                if decoded_part.lower().endswith('.pdf'):
                    return decoded_part
            except:
                pass
    return url  # Return original if no extraction possible


def download_pdf_url(url, dest_path):
    """Download PDF from URL to local path, following redirects and extracting from tracking links."""
    # Try to extract actual PDF URL from tracking links
    actual_url = extract_pdf_url_from_tracking(url)
    if actual_url != url:
        print(f"    🔄 Extracted actual PDF URL: {actual_url}")
        url = actual_url

    # SSRF protection: validate URL before download
    if not is_safe_pdf_url(url):
        print(f"    ⛔ SSRF check failed for: {url}")
        return False

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=30) as response:
            # Follow redirects automatically (urllib does this by default)
            final_url = response.geturl()
            content_type = response.headers.get('Content-Type', '')

            # Check if we got a PDF (either by content-type or URL)
            is_pdf = 'pdf' in content_type.lower() or final_url.lower().endswith('.pdf')

            if not is_pdf:
                print(f"    ⚠️  Not a PDF (content-type: {content_type}, url: {final_url})")
                return False

            dest_path.write_bytes(response.read())
        return True
    except Exception as e:
        print(f"    ⚠️  Download failed: {url} - {e}")
        return False


def get_week_str(date_str=None):
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        dt = datetime.now()
    week_num = dt.isocalendar()[1]
    week_str = f"{dt.year}-W{week_num:02d}"
    monday = dt - timedelta(days=dt.weekday())
    sunday = monday + timedelta(days=6)
    week_range = f"tuần {monday.strftime('%d/%m')}–{sunday.strftime('%d/%m')}"
    return week_str, week_range


def generate_entry(date_str, broker, route, text, source, tickers, structured_data=None):
    week_str, week_range = get_week_str(date_str)
    tickers_str = ", ".join(tickers) if tickers else "N/A"
    
    if route == "weekly":
        # Use structured data if available, otherwise fallback to skeleton
        if structured_data:
            macro_lines = structured_data.get("macro_context", [])
            sector_rows = structured_data.get("sector_highlights", [])
            watchlist_rows = structured_data.get("watchlist", [])
            strategy = structured_data.get("strategy", {})
            
            # Build macro context
            macro_text = "\n".join(f"- {line}" for line in macro_lines) if macro_lines else f"- {broker} weekly report"
            
            # Build sector highlights table
            sector_table = "| Nhóm | Động lực | Rủi ro |\n|---|---|---|\n"
            for sector in sector_rows:
                group = sector.get("group", "")
                driver = sector.get("driver", "") or "[...]"
                risk = sector.get("risk", "") or "[...]"
                sector_table += f"| {group} | {driver} | {risk} |\n"
            
            # Build watchlist table
            watchlist_table = "| Ticker | IV est | Price | MOS% | Action |\n|---|---|---|---|---|\n"
            for item in watchlist_rows:
                ticker = item.get("ticker", "")
                iv_est = item.get("iv_est", "") or "[...]"
                price = item.get("price", "") or "[...]"
                mos_pct = item.get("mos_pct", "") or "[...]"
                action = item.get("action", "") or "[...]"
                watchlist_table += f"| {ticker} | {iv_est} | {price} | {mos_pct} | {action} |\n"
            
            # Strategy
            short = strategy.get("short", "...")
            long = strategy.get("long", "...")
            avoid = strategy.get("avoid", "...")
            
            return f"""## {week_str} ({week_range}) — {broker}

### Macro context
{macro_text}

### Sector highlights
{sector_table}

### Watchlist update
{watchlist_table}

### Holdings check (thesis intact?)
-

### Strategy
- Ngắn hạn: {short}
- Dài hạn: {long}
- Tránh: {avoid}

### Source
{source}
---
"""
        
        # Fallback to skeleton if no structured data
        ticker_rows = ""
        for t in tickers:
            ticker_rows += f"| {t} | [...] | [...] | [...] | [...]\n"
        
        return f"""## {week_str} ({week_range}) — {broker}

### Macro context
- {broker} weekly report
- Key tickers mentioned: {tickers_str}

### Sector highlights
| Nhóm | Động lực | Rủi ro |
|---|---|---|
| {broker} coverage | [...] | [...] |

### Watchlist update
| Ticker | IV est | Price | MOS% | Action |
|---|---|---|---|---|
{ticker_rows}

### Holdings check (thesis intact?)
-

### Strategy
- Ngắn hạn: [...]
- Dài hạn: [...]
- Tránh: [...]

### Source
{source}
---
"""
    
    # daily/macro/sector narrative format
    return f"""## {date_str} — {broker} {text[:60]}

### Narrative
{text[:500]}

### Impact assessment
- VN market impact: [...]
- Affected sectors: [...]
- Related tickers: [{tickers_str}]

### Watch points
- [...]

### Source
{source}
---
"""


def append_to_pulse(route, entry):
    pulse_files = {
        "weekly": "020_VNStock_Weekly_Outlook.md",
        "macro": "021_VNStock_Macro.md",
        "sector": "020_VNStock_Weekly_Outlook.md",  # append to weekly sector section
        "daily": "022_VNStock_Daily_Outlook.md",
    }
    pulse_file = PULSE_DIR / pulse_files[route]
    
    if pulse_file.exists():
        content = pulse_file.read_text(encoding="utf-8")
    else:
        content = ""
    
    # For weekly: deduplicate by week
    if route == "weekly":
        # Extract week identifier from new entry (e.g., "2026-W25 (tuần 15/06–21/06)")
        import re
        week_match = re.search(r'##\s+(20\d{2}-W\d{2}\s+\([^)]+\))', entry)
        new_week = week_match.group(1) if week_match else None
        
        if new_week:
            # Check if this week already exists with real data
            existing_week_match = re.search(rf'##\s+{re.escape(new_week)}', content)
            if existing_week_match:
                # Extract existing entry to check if it's skeleton
                existing_start = existing_week_match.start()
                next_header = re.search(r'\n##\s+20\d{2}-W\d{2}', content[existing_start + 1:])
                existing_end = existing_start + 1 + next_header.start() if next_header else len(content)
                existing_entry = content[existing_start:existing_end]
                
                # Check if existing entry has real data (not skeleton)
                skeleton_count = existing_entry.count('[...]')
                real_content_lines = [l for l in existing_entry.split('\n') if l.strip() and not l.strip().startswith('|') and '[...]' not in l]
                has_real_data = len(real_content_lines) > 5 and skeleton_count < 20
                
                if has_real_data:
                    print(f"  ⏭️  Week {new_week} already exists with real data, skipping duplicate")
                    return
                else:
                    print(f"  🔄 Week {new_week} exists as skeleton, replacing with real data")
                    # Remove existing skeleton entry
                    content = content[:existing_start] + content[existing_end:]
    
    # Find insert position (after template block for weekly)
    lines = content.split("\n")
    insert_idx = None
    
    if route == "weekly":
        in_code = False
        for i, line in enumerate(lines):
            if line.strip().startswith("```"):
                in_code = not in_code
                if not in_code:
                    insert_idx = i + 1
                    break
    else:
        for i, line in enumerate(lines):
            if line.startswith("## ") and i > 0:
                insert_idx = i
                break
    
    if insert_idx is not None:
        lines.insert(insert_idx, entry.rstrip())
    else:
        lines.append(entry.rstrip())
    new_content = "\n".join(lines)
    
    pulse_file.write_text(new_content, encoding="utf-8")
    print(f"  ✅ Appended to {pulse_files[route]}")


async def parse_pdf_to_weekly_template(pdf_texts: list, source: str) -> dict:
    """
    Parse broker report PDF texts into structured weekly template data.
    
    Args:
        pdf_texts: List of (filename, text) tuples
        source: Source identifier (e.g., "Bonnejed", "SSI")
    
    Returns:
        dict with keys: macro_context, sector_highlights, watchlist, strategy, key_tickers
    """
    if not pdf_texts:
        return FALLBACK_SKELETON
    
    # Token budget check - smart truncate
    total_chars = sum(len(text) for _, text in pdf_texts)
    if total_chars > MAX_TOKENS_PER_RUN * 4:  # rough char to token ratio
        # Smart truncate: keep first 4k + last 2k of each PDF
        truncated = []
        for filename, text in pdf_texts:
            if len(text) > 6000:
                text = text[:4000] + "\n...[TRUNCATED]...\n" + text[-2000:]
            truncated.append((filename, text))
        pdf_texts = truncated
        print(f"    📏 Truncated PDF texts for token budget")
    
    # Load prompt template
    prompt_template = load_prompt()
    
    # Build input text with source labels
    input_parts = []
    for filename, text in pdf_texts:
        input_parts.append(f"=== {filename} ===\n{text[:10000]}")
    input_text = "\n\n".join(input_parts)
    
    # Inject input into prompt
    prompt = prompt_template.replace("{INPUT_TEXT}", input_text)
    
    try:
        # Call LLM with timeout
        import asyncio
        llm_output = await asyncio.wait_for(
            call_llm(prompt),
            timeout=LLM_TIMEOUT_SECONDS
        )
        
        # Extract and validate JSON
        data = extract_json_from_llm_output(llm_output)
        data = validate_weekly_schema(data)
        data = cross_reference_with_pdf_text(data, pdf_texts)
        
        print(f"    ✅ LLM parsed {source}: {len(data['macro_context'])} macro, {len(data['sector_highlights'])} sectors, {len(data['watchlist'])} watchlist")
        return data
        
    except asyncio.TimeoutError:
        print(f"    ⚠️  LLM timeout ({LLM_TIMEOUT_SECONDS}s) for {source}")
        return FALLBACK_SKELETON
    except Exception as e:
        print(f"    ⚠️  LLM parse failed for {source}: {e}")
        return FALLBACK_SKELETON


# Fallback skeleton for when LLM fails
FALLBACK_SKELETON = {
    "macro_context": [],
    "sector_highlights": [],
    "watchlist": [],
    "strategy": {"short": "...", "long": "...", "avoid": "..."},
    "key_tickers": []
}


def load_prompt() -> str:
    """Load prompt template from versioned file."""
    prompt_path = Path("C:/Users/khoans/Documents/Personal_OS/personal_vault/scripts/prompts/weekly_parser_v1.md")
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    raise FileNotFoundError(f"Prompt file not found: {prompt_path}")


def validate_weekly_schema(data: dict) -> dict:
    """Validate and ensure all required fields exist with correct types."""
    required_keys = ["macro_context", "sector_highlights", "watchlist", "strategy", "key_tickers"]
    
    for key in required_keys:
        if key not in data:
            data[key] = [] if key != "strategy" else {"short": "", "long": "", "avoid": ""}
    
    # Ensure correct types
    if not isinstance(data["macro_context"], list):
        data["macro_context"] = []
    if not isinstance(data["sector_highlights"], list):
        data["sector_highlights"] = []
    if not isinstance(data["watchlist"], list):
        data["watchlist"] = []
    if not isinstance(data["strategy"], dict):
        data["strategy"] = {"short": "", "long": "", "avoid": ""}
    if not isinstance(data["key_tickers"], list):
        data["key_tickers"] = []
    
    # Ensure each sector entry has correct structure
    for sector in data["sector_highlights"]:
        if not isinstance(sector, dict):
            continue
        sector.setdefault("group", "")
        sector.setdefault("driver", "")
        sector.setdefault("risk", "")
    
    # Ensure each watchlist entry has correct structure
    for item in data["watchlist"]:
        if not isinstance(item, dict):
            continue
        item.setdefault("ticker", "")
        item.setdefault("iv_est", "")
        item.setdefault("price", "")
        item.setdefault("mos_pct", "")
        item.setdefault("action", "")
    
    return data


def cross_reference_with_pdf_text(data: dict, pdf_texts: list) -> dict:
    """Anti-hallucination: verify extracted data exists in source text."""
    combined_text = " ".join([pdf_text for _, pdf_text in pdf_texts]).lower()
    
    # Check watchlist tickers exist in source
    valid_tickers = []
    for item in data["watchlist"]:
        ticker = item.get("ticker", "").upper()
        if ticker and ticker in combined_text:
            valid_tickers.append(item)
    
    data["watchlist"] = valid_tickers
    
    # Check key_tickers
    valid_keys = [t for t in data["key_tickers"] if t.lower() in combined_text]
    data["key_tickers"] = valid_keys
    
    return data


def extract_json_from_llm_output(text: str) -> dict:
    """Extract JSON from LLM output, handling code blocks."""
    import json
    
    # Try to find JSON in code blocks
    import re
    code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if code_block_match:
        json_str = code_block_match.group(1)
    else:
        # Try to find first { to last }
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        if first_brace != -1 and last_brace != -1:
            json_str = text[first_brace:last_brace+1]
        else:
            json_str = text
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"    ⚠️  JSON parse error: {e}")
        print(f"    Raw output: {text[:500]}")
        raise


# Fallback skeleton for when LLM fails
FALLBACK_SKELETON = {
    "macro_context": [],
    "sector_highlights": [],
    "watchlist": [],
    "strategy": {"short": "...", "long": "...", "avoid": "..."},
    "key_tickers": []
}


def load_prompt() -> str:
    """Load prompt template from versioned file."""
    prompt_path = Path("C:/Users/khoans/Documents/Personal_OS/personal_vault/scripts/prompts/weekly_parser_v1.md")
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    raise FileNotFoundError(f"Prompt file not found: {prompt_path}")


def validate_weekly_schema(data: dict) -> dict:
    """Validate and ensure all required fields exist with correct types."""
    required_keys = ["macro_context", "sector_highlights", "watchlist", "strategy", "key_tickers"]
    
    for key in required_keys:
        if key not in data:
            data[key] = [] if key != "strategy" else {"short": "", "long": "", "avoid": ""}
    
    # Ensure correct types
    if not isinstance(data["macro_context"], list):
        data["macro_context"] = []
    if not isinstance(data["sector_highlights"], list):
        data["sector_highlights"] = []
    if not isinstance(data["watchlist"], list):
        data["watchlist"] = []
    if not isinstance(data["strategy"], dict):
        data["strategy"] = {"short": "", "long": "", "avoid": ""}
    if not isinstance(data["key_tickers"], list):
        data["key_tickers"] = []
    
    # Ensure each sector entry has correct structure
    for sector in data["sector_highlights"]:
        if not isinstance(sector, dict):
            continue
        sector.setdefault("group", "")
        sector.setdefault("driver", "")
        sector.setdefault("risk", "")
    
    # Ensure each watchlist entry has correct structure
    for item in data["watchlist"]:
        if not isinstance(item, dict):
            continue
        item.setdefault("ticker", "")
        item.setdefault("iv_est", "")
        item.setdefault("price", "")
        item.setdefault("mos_pct", "")
        item.setdefault("action", "")
    
    return data


def cross_reference_with_pdf_text(data: dict, pdf_texts: list) -> dict:
    """Anti-hallucination: verify extracted data exists in source text."""
    combined_text = " ".join([pdf_text for _, pdf_text in pdf_texts]).lower()
    
    # Check watchlist tickers exist in source
    valid_tickers = []
    for item in data["watchlist"]:
        ticker = item.get("ticker", "").upper()
        if ticker and ticker in combined_text:
            valid_tickers.append(item)
    
    data["watchlist"] = valid_tickers
    
    # Check key_tickers
    valid_keys = [t for t in data["key_tickers"] if t.lower() in combined_text]
    data["key_tickers"] = valid_keys
    
    return data


def extract_json_from_llm_output(text: str) -> dict:
    """Extract JSON from LLM output, handling code blocks."""
    import json
    
    # Try to find JSON in code blocks
    import re
    code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if code_block_match:
        json_str = code_block_match.group(1)
    else:
        # Try to find first { to last }
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        if first_brace != -1 and last_brace != -1:
            json_str = text[first_brace:last_brace+1]
        else:
            json_str = text
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"    ⚠️  JSON parse error: {e}")
        print(f"    Raw output: {text[:500]}")
        raise


async def parse_pdf_to_weekly_template(pdf_texts: list, source: str) -> dict:
    """
    Parse broker report PDF texts into structured weekly template data.
    
    Args:
        pdf_texts: List of (filename, text) tuples
        source: Source identifier (e.g., "Bonnejed", "SSI")
    
    Returns:
        dict with keys: macro_context, sector_highlights, watchlist, strategy, key_tickers
    """
    if not pdf_texts:
        return FALLBACK_SKELETON
    
    # Token budget check - smart truncate
    total_chars = sum(len(text) for _, text in pdf_texts)
    if total_chars > MAX_TOKENS_PER_RUN * 4:  # rough char to token ratio
        # Smart truncate: keep first 4k + last 2k of each PDF
        truncated = []
        for filename, text in pdf_texts:
            if len(text) > 6000:
                text = text[:4000] + "\n...[TRUNCATED]...\n" + text[-2000:]
            truncated.append((filename, text))
        pdf_texts = truncated
        print(f"    📏 Truncated PDF texts for token budget")
    
    # Load prompt template
    prompt_template = load_prompt()
    
    # Build input text with source labels
    input_parts = []
    for filename, text in pdf_texts:
        input_parts.append(f"=== {filename} ===\n{text[:10000]}")
    input_text = "\n\n".join(input_parts)
    
    # Inject input into prompt
    prompt = prompt_template.replace("{INPUT_TEXT}", input_text)
    
    try:
        # Call LLM with timeout
        import asyncio
        llm_output = await asyncio.wait_for(
            call_llm(prompt),
            timeout=LLM_TIMEOUT_SECONDS
        )
        
        # Extract and validate JSON
        data = extract_json_from_llm_output(llm_output)
        data = validate_weekly_schema(data)
        data = cross_reference_with_pdf_text(data, pdf_texts)
        
        print(f"    ✅ LLM parsed {source}: {len(data['macro_context'])} macro, {len(data['sector_highlights'])} sectors, {len(data['watchlist'])} watchlist")
        return data
        
    except asyncio.TimeoutError:
        print(f"    ⚠️  LLM timeout ({LLM_TIMEOUT_SECONDS}s) for {source}")
        return FALLBACK_SKELETON
    except Exception as e:
        print(f"    ⚠️  LLM parse failed for {source}: {e}")
        return FALLBACK_SKELETON


async def process_message(service, msg_id, source_name):
    """Process single Gmail message"""
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    
    # Get headers
    headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
    subject = headers.get("subject", "")
    date_str = headers.get("date", "")
    
    # Get email body text
    def get_body_text(payload):
        text = ""
        if "parts" in payload:
            for p in payload["parts"]:
                text += get_body_text(p)
        else:
            data = payload.get("body", {}).get("data", "")
            if data:
                try:
                    text += base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                except:
                    pass
        return text
    
    body_text = get_body_text(msg["payload"])
    
    # Skip statements (check subject)
    if should_skip(subject, []):
        print(f"  ⏭️  Skip: {subject}")
        return False
    
    print(f"  📨 {subject}")
    
    # Find PDF attachments
    attachments = []
    def find_atts(part):
        if part.get("filename", "").lower().endswith(".pdf"):
            att_id = part["body"].get("attachmentId")
            if att_id:
                attachments.append((part["filename"], att_id))
        if "parts" in part:
            for p in part["parts"]:
                find_atts(p)
    find_atts(msg["payload"])
    
    # If no attachments, try to extract PDF URLs from body
    pdf_urls = []
    if not attachments:
        pdf_urls = extract_pdf_urls(body_text)
        if pdf_urls:
            print(f"  🔗 Found {len(pdf_urls)} PDF link(s) in email body")
    
    # Skip if no PDF source at all
    if not attachments and not pdf_urls:
        print(f"  ⚠️  No PDF attachment or link")
        return False
    
    # Skip if any attachment filename matches skip keywords
    if should_skip(subject, attachments):
        print(f"  ⏭️  Skip (attachment): {subject}")
        return False
    
    # Process PDFs from attachments AND downloaded URLs
    combined_text = ""
    source_files = []
    temp_dir = VAULT_ROOT / "_tmp_broker"
    temp_dir.mkdir(exist_ok=True)
    
    # Process attachments
    for filename, att_id in attachments:
        att = service.users().messages().attachments().get(
            userId="me", messageId=msg_id, id=att_id
        ).execute()
        data = base64.urlsafe_b64decode(att["data"])
        
        pdf_path = temp_dir / f"{msg_id}_{filename}"
        pdf_path.write_bytes(data)
        
        text = extract_pdf_text(pdf_path)
        combined_text += f"\n--- {filename} ---\n{text}"
        source_files.append(filename)
        
        try:
            pdf_path.unlink()
        except:
            pass
    
    # Process PDF URLs from email body
    for i, url in enumerate(pdf_urls):
        # Extract filename from URL
        filename = url.split("/")[-1].split("?")[0]
        if not filename.endswith(".pdf"):
            filename = f"broker_report_{i+1}.pdf"
        
        pdf_path = temp_dir / f"{msg_id}_{filename}"
        print(f"  📥 Downloading: {url}")
        if download_pdf_url(url, pdf_path):
            text = extract_pdf_text(pdf_path)
            combined_text += f"\n--- {filename} (from URL) ---\n{text}"
            source_files.append(f"{filename} (URL)")
            
            try:
                pdf_path.unlink()
            except:
                pass
    
    if not combined_text.strip() or combined_text.startswith("[ENCRYPTED") or combined_text.startswith("[EXTRACTION ERROR"):
        print(f"  ⚠️  Could not extract: {combined_text[:100]}")
        return False
    
    # Classify
    route = classify_route(combined_text)
    tickers = extract_tickers(combined_text)
    
    # For weekly route, try LLM parsing to get structured data
    structured_data = None
    if route == "weekly" and combined_text.strip():
        # Prepare PDF texts for LLM parsing
        pdf_texts = []
        
        # Add attachment texts
        for filename, att_id in attachments:
            att = service.users().messages().attachments().get(
                userId="me", messageId=msg_id, id=att_id
            ).execute()
            data = base64.urlsafe_b64decode(att["data"])
            
            pdf_path = temp_dir / f"{msg_id}_{filename}"
            pdf_path.write_bytes(data)
            
            text = extract_pdf_text(pdf_path)
            pdf_texts.append((filename, text))
            
            try:
                pdf_path.unlink()
            except:
                pass
        
        # Add URL PDF texts (already have paths)
        for i, url in enumerate(pdf_urls):
            filename = url.split("/")[-1].split("?")[0]
            if not filename.endswith(".pdf"):
                filename = f"broker_report_{i+1}.pdf"
            
            pdf_path = temp_dir / f"{msg_id}_{filename}"
            if download_pdf_url(url, pdf_path):
                text = extract_pdf_text(pdf_path)
                pdf_texts.append((filename, text))
                
                try:
                    pdf_path.unlink()
                except:
                    pass
        
        # Call LLM parsing for weekly reports
        if pdf_texts:
            structured_data = await parse_pdf_to_weekly_template(pdf_texts, source_name)
    
    # Classify
    route = classify_route(combined_text)
    tickers = extract_tickers(combined_text)
    
    # Date for entry
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(date_str)
        entry_date = dt.strftime("%Y-%m-%d")
    except:
        entry_date = datetime.now().strftime("%Y-%m-%d")
    
    # Generate & append entry
    source = f"Gmail: {subject} ({', '.join(source_files)})"
    entry = generate_entry(entry_date, source_name, route, combined_text, source, tickers, structured_data)
    append_to_pulse(route, entry)
    
    print(f"  📂 Route: {route} | Tickers: {', '.join(tickers) if tickers else 'N/A'}")
    return True


def main():
    import argparse
    import asyncio
    
    parser = argparse.ArgumentParser(description="Fetch broker reports → vault")
    parser.add_argument("--days", type=int, default=7, help="Days back to search")
    parser.add_argument("--max", type=int, default=20, help="Max messages per broker")
    parser.add_argument("--dry-run", action="store_true", help="Search only, don't process")
    parser.add_argument("--label-processed", action="store_true", help="Add label 'Processed' to emails")
    args = parser.parse_args()
    
    print("🔍 Fetching broker reports...")
    query = build_query(args.days)
    print(f"   Query: {query}")

    service = build_service("gmail", "v1")

    # Execute 3 separate queries and merge results (deduplicate by message ID)
    query_blocks = build_query_blocks(args.days)
    all_messages = {}  # dict[message_id] = message
    for i, block in enumerate(query_blocks):
        print(f"   DEBUG: Block {i+1}: {block[:80]}...")
        # Rate limit Gmail API
        GMAIL_RATE_LIMITER.take()
        results = service.users().messages().list(
            userId="me", q=block, maxResults=args.max
        ).execute()
        block_messages = results.get("messages", [])
        for m in block_messages:
            all_messages[m["id"]] = m
        print(f"   Block {i+1}: {len(block_messages)} messages")

    messages = list(all_messages.values())
    print(f"📬 Found {len(messages)} unique messages")
    if messages:
        for i, m in enumerate(messages[:3]):
            print(f"   [{i}] ID: {m['id']}")
    
    if args.dry_run:
        for m in messages:
            # Identify source from sender
            msg = service.users().messages().get(userId="me", id=m["id"], format="metadata", metadataHeaders=["From"]).execute()
            headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
            from_addr = headers.get("From", "").lower()
            
            source_name = None
            for name, domain in BROKERS + EXTRA_SOURCES:
                if domain in from_addr:
                    source_name = name
                    break
            
            if source_name:
                print(f"  - {headers.get('From')} | {headers.get('Subject')} | {headers.get('Date')} | Source: {source_name}")
            else:
                print(f"  - {headers.get('From')} | {headers.get('Subject')} | {headers.get('Date')} | Source: Unknown")
        return
    
    processed = 0
    for m in messages:
        # Identify source from sender
        msg = service.users().messages().get(userId="me", id=m["id"], format="metadata", metadataHeaders=["From"]).execute()
        headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
        from_addr = headers.get("from", "").lower()
        
        source_name = None
        # Check direct brokers + extra sources
        for name, domain in BROKERS + EXTRA_SOURCES:
            if domain in from_addr:
                source_name = name
                break
        # Check forwarders if not found
        if not source_name:
            for name, domain in FORWARDERS:
                if domain in from_addr:
                    source_name = name
                    break
        
        if source_name:
            print(f"\n📧 Processing: {source_name} ({m['id']})")
            result = asyncio.run(process_message(service, m["id"], source_name))
            if result:
                processed += 1
                
                # Label as processed
                if args.label_processed:
                    service.users().messages().modify(
                        userId="me", id=m["id"],
                        body={"addLabelIds": ["Label_1", "Label_2"]}  # Need to get actual label ID
                    ).execute()
    
    print(f"\n✅ Done. Processed {processed}/{len(messages)} broker reports.")


if __name__ == "__main__":
    main()