# LLM Parsing for Broker Report PDFs → Auto-fill Weekly Template — Revised Plan

## 1. CONTEXT
- **Current state:** `fetch_broker_reports.py` already downloads PDFs from TCBS tracking links and extracts raw text via pymupdf. The pipeline produces weekly skeleton entries for 2026-W25 in `10_PULSE/020_VNStock_Weekly_Outlook.md`, but those entries are mostly `[...]` placeholders.
- **Reference quality:** `2026-W24` is treated as the closest available gold-standard weekly entry. The schema is the weekly template format, and the quality threshold is ≥80% field fill rate and tone/layout alignment with the latest manual weekly entry.
- **Available resources:** PDF text extraction works; Gmail API and cron are working; existing vault format and template block are validated.

## 2. GOAL
Implement LLM-based parsing for weekly broker report PDFs that:
- consumes existing extracted PDF text,
- returns structured JSON aligned to the weekly template,
- populates `generate_entry()` with real data instead of `[...]`,
- appends complete weekly entries to `020_VNStock_Weekly_Outlook.md`,
- keeps all other routes unchanged.

## 3. SCOPE
**In scope:**
- `parse_pdf_to_weekly_template()` in `scripts/fetch_broker_reports.py`
- Weekly template schema and prompt versioning
- JSON validation and anti-hallucination filtering
- `generate_entry()` updated to accept structured weekly data
- Integration into `process_message()` for the weekly route only
- Simple evaluation harness for weekly entry quality

**Out of scope:**
- Daily/macro/sector format changes
- PDF download/decryption logic beyond current skip/fallback behavior
- Cron/Telegram/Email delivery
- General LLM provider management outside this parser

## 4. STEPS
1. Prompt + schema + few-shot + provider requirement  
2. Prompt versioning + evaluation harness  
3. Implement `parse_pdf_to_weekly_template()`  
4. Modify `generate_entry()` for weekly structured output  
5. Integrate into `process_message()`  
6. Edge-case checklist and handlers  
7. Test with existing Bonnejed weekly PDFs  
8. Commit revised plan and implementation

## 5. LLM PROVIDER DECISION
- Current Hermes sidecar/provider is **Nous**.
- Verified Nous provider record exists in auth/profile config with inference base URL and refresh token.
- Tests show:
  - `stepfun/step-3.7-flash:free` returns 200 with text.
  - `nousresearch/hermes-4-70b` returns 404 on chat completions.
  - OpenRouter-style key handling would require credential handling not currently present.
- **Decision:** Route `call_llm()` through the provider info already present in Hermes profile config for this profile, with a single safe model fallback. Do not hardcode `openrouter`. Do not add new secret handling in this pass.

## 6. PROMPT / SCHEMA / FEW-SHOT
- Few-shot must come from `2026-W24` manual entry already in `010_PULSE/020_VNStock_Weekly_Outlook.md`.
- JSON schema must map exactly to weekly template sections.
- Prompt must include:
  - extraction rules,
  - token budget,
  - anti-hallucination rule,
  - Vietnamese financial terminology guidance.
- Prompt file path: `scripts/prompts/weekly_parser_v1.md`.

## 7. EVALUATION HARNESS
- Add `scripts/eval_weekly_entry.py`.
- Inputs: generated weekly markdown + gold-standard 2026-W24 section.
- Metrics:
  - field coverage = filled fields / total template fields
  - skeleton rate = fields equal to `[...]` or empty
  - hallucination flags = field value not present or strongly implied in source text
- Output: score report only, not approval gate that blocks ingestion.

## 8. EDGE-CASE CHECKLIST
- Mixed VN/EN PDF
- Missing section
- Table parsing / bullet extraction
- Currency / date formats
- Multiple PDFs with overlapping or conflicting data
- LLM timeout or malformed JSON
- Encrypted PDF skipped upstream

## 9. SUCCESS CRITERIA
1. Functional: weekly entries generated from existing Bonnejed PDFs with ≥4 macro bullets, ≥4 sector rows, ≥10 watchlist rows when source supports it, and non-empty short/long/avoid strategy bullets when text supports it.
2. Quality: field coverage ≥80% and tone/structure aligned with 2026-W24 manual.
3. Reliability: failure path falls back to skeleton and logs a clear warning.

## 10. ESTIMATE
Revised from ~2.5h to **6–8h** across code + prompt + tests.
