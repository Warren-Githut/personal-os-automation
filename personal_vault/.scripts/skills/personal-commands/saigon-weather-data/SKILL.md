---
name: saigon-weather-data
description: "Reliable weather data sourcing for Saigon/HCMC — primary sources, fallbacks when gov site doesn't parse, expected output format. Used by personal-morning-brief and any task needing Saigon weather."
version: 1.0
tags: [weather, data-source, saigon, fallback, reference]
---

# Saigon Weather Data — Source Reference

## Primary Source

```
nchmf.gov.vn (National Center for Hydro-Meteorological Forecasting)
URL: https://nchmf.gov.vn/kttvSite/vi-VN/1/sai-gon-tp-ho-chi-minh-w15.html
```

**Known issue:** This site uses heavy JavaScript rendering. `mcp_smart_fetch` often returns navigation HTML instead of weather data. The search snippet may show the last update time and temperature (e.g. "Cập nhật: 22h 08/07/2026. Nhiệt độ: 27°C") but the full page body is unreliable.

**Expected data when it works:** Temperature (°C), humidity (%), wind, rain probability, 10-day forecast.

## Fallback Sources (when primary fails)

| Priority | Source | Method | Notes |
|----------|--------|--------|-------|
| 1 | Web search | `mcp_smart_search("thời tiết Sài Gòn hôm nay {dd/mm/yyyy}")` | Snippet often shows key data |
| 2 | giaiphaphutam.com | `mcp_smart_fetch(url)` | Clean data in meta tags (daily max/min, rain mm, humidity); heavy ad content |
| 3 | vietnamnet.vn | `mcp_smart_fetch(url)` | Reliable for broad forecast (max/min, rain description) |
| 4 | nchmf.gov.vn snippet | `mcp_smart_search` result | Shows last update timestamp + temperature at that time |

## Output Format

Extract these fields for the brief:
- **Current temp:** e.g. 27°C (from last night reading) or morning temp
- **High today:** e.g. 33°C
- **Low today:** e.g. 26°C
- **Rain probability / conditions:** e.g. "mưa rào và giông chiều/tối"
- **Timestamp:** when the data was last updated

## Format example

```
HCMC: 31-34°C / 26°C. Có mây, mưa rào chiều/tối. [MOD]
```

## Pitfalls

1. **nchmf.gov.vn is the official source but often unparseable** — Always have fallbacks ready. Do NOT retry the same URL repeatedly.
2. **giaiphaphutam.com has heavy ads** — Use `mcp_smart_fetch` with `char_limit=3000` to get just the header data.
3. **vietnamnet daily forecast articles** — Search for `"Dự báo thời tiết {dd/mm/yyyy}"` to find the specific article.
4. **Temperature range width may vary** — Some sources give a range (31-34°C), others give single values.
5. **Rain probability is often descriptive** — "mưa rào và dông vài nơi" rather than a percentage. Use descriptive text, don't fabricate a percentage.

## MANDATORY VERIFY GATE (rule: never trust LLM, verify everything)

After EVERY parser run that reads Excel/CSV/PDF ([DOMAIN: weather data (temperature, rainfall)]), MUST run verify-parser-output gate BEFORE reporting numbers or committing.

1. Independent recompute (fresh script, different method).
2. Cross-assert EVERY number (giá, P&L, room, %Δ, số dư, headcount) vs LLM output.
3. Category-drop scan: count raw rows vs filtered; flag dropped (mã rỗng, dòng tổng, Loc=NaN).
4. Emit VERIFY_RESULT: PASS|FAIL + dropped count. Temp hermes-verify-*.py, clean after.
5. FAIL → LLM wrong until proven. Fix logic, re-run, re-verify.
