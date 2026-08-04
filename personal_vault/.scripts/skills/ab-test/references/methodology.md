# ab-test Methodology

## Test Types

### 1. Parser A/B (`ab_parser.py`)

Compares 2 parser strategies on the same vault files:

| Variant | Strategy | Behavior |
|---------|----------|----------|
| A (Strict SOP) | `YamlValidator.validate(filepath, content, vault_path=vault_path)` | Schema-aware: required fields per vault section |
| B (Lenient) | Any valid YAML frontmatter = pass | Accepts all files with frontmatter regardless of fields |

**Winner criteria:**
- `valid_pct_diff > 5%` → winner (higher validity wins)
- `abs(valid_pct_diff) <= 5% AND speed_diff <= 0.5ms` → EQUAL
- Otherwise DEPENDS

**Example result:** B (lenient) accepts 52.6% more files (60% vs 7.4%)

### 2. Prompt Template A/B (`ab_prompt.py`)

Structural analysis (no LLM call) comparing 2 template variants across 5 scoring criteria:

| Criterion | Score | Checks |
|-----------|-------|--------|
| Verbosity | +1 | template length > 100 chars |
| Output format | +1 | contains bullet/list/json/markdown |
| Role assignment | +1 | contains "you are"/"expert"/"analyst" |
| Specific verb | +1 | contains extract/summarize/analyze/identify/list/compare/evaluate |
| Context/scoping | +1 | length > 50 AND contains ":" |

**2 test cases:**
- `summary`: concise vs detailed summary templates
- `frontmatter`: simple extraction vs structured analysis templates

**Winner:** Aggregated across all test cases (majority wins).

### 3. Vault Structure A/B (`ab_vault_struct.py`)

Analyzes current vault structure and classifies as:

| Pattern | Criteria | Recommendation |
|---------|----------|----------------|
| FOLDER-HEAVY | avg_depth > 4 AND avg_files_per_dir < 5 | Flatten: reduce depth to ~3 |
| TAG-HEAVY | avg_depth <= 3 AND avg_files_per_dir > 10 | Categorize: split overloaded dirs |
| BALANCED | Neither of above | EQUAL — no change needed |

**Metrics analyzed:**
- Total files, total directories
- Average file depth, max depth
- Files per directory (avg, dense >20, sparse =1)
- Average links per file (connectivity proxy)

## Report Format

All A/B tests return:

```json
{
  "status": "PASS",         // or "FAIL" if BOTH_BAD
  "type": "parser",         // parser|prompt|vault
  "winner": "B",            // A | B | EQUAL | DEPENDS | BOTH_BAD
  "reason": "...",
  "details": { ... },       // type-specific full result
  "execution_time_ms": 135
}
```

## When to Run

- **Parser A/B**: After parser code changes, before deploying new parser to production
- **Prompt A/B**: When designing new prompt templates or refining existing ones
- **Vault struct A/B**: Quarterly vault health check or after major reorganization

## Cross-Skill Dependency

`ab-test` imports `utils.py` from `battle-test` at runtime via sys.path.
See `battle-test/references/architecture.md` for the import pattern.
