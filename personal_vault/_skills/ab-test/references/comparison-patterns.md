# Reference: A/B Comparison Patterns

## Overview

ab-test compares 2 variants of vault system components and recommends a winner. Three comparison types are supported.

## Comparison Types

### Parser (ab_parser.py)

Compares strict SOP validation vs lenient validation across all vault files.

| Metric | Strict SOP (A) | Lenient (B) |
|--------|---------------|-------------|
| Validation | Required fields must exist | Any frontmatter is valid |
| Speed | Slightly slower (field checks) | Faster (existence only) |
| Use case | SOP compliance audit | General file health check |

**Winner logic:** Based on validity % difference threshold (>5% delta). If close, speed breaks tie.

### Prompt Template (ab_prompt.py)

Structural template quality analysis. Scores templates on 5 criteria:
1. Instruction length (>100 chars)
2. Explicit output format (bullet, list, json, etc.)
3. Role assignment (expert, analyst, etc.)
4. Specific task verb (extract, summarize, etc.)
5. Context/scoping (colon-separated sections)

**Winner logic:** Sum of criteria scores; higher score wins.

### Vault Structure (ab_vault_struct.py)

Analyzes current vault organization and classifies:
- **FOLDER-HEAVY:** Avg depth >4, files per dir <5
- **TAG-HEAVY:** Avg depth <=3, dense dirs (>20 files) present
- **BALANCED:** Healthy midpoint

**Winner logic:** Current pattern is "A", suggested improvement is "hypothetical B".

## Output Format

```json
{
  "status": "PASS",
  "type": "parser",
  "winner": "B",
  "reason": "B (lenient) accepts 52.6% more files",
  "details": {
    "A": {"valid_pct": 7.4, "avg_time_ms": 0.02},
    "B": {"valid_pct": 60.0, "avg_time_ms": 0.01},
    "delta": {"valid_pct_diff": 52.6, "speed_diff_ms": 0.01}
  },
  "execution_time_ms": 135
}
```

## Cross-Profile Note

ab-test copies `utils.py` from battle-test into its own `scripts/` dir.
Both skills are deployed identically to warren-profile and personal_profile.
