# Nested JSON Regex Pitfall

## Symptom

`re.findall(r"<!-- gf_data: ({[^}]+}) -->", text)` returns only partial JSON when the object contains nested objects (e.g. `{"channel_mix": {"LU3": 4.2, ...}}`).

The regex `[^}]+` stops at the **first** `}` inside the nested structure, producing truncated JSON that fails `json.loads()`.

## Root Cause

`[^}]+` is a character class that matches any character EXCEPT `}`. When a JSON object contains another object as a value, the inner `}` terminates the match prematurely.

## Fix Pattern: Brace Counter

Replace the regex with a depth-counting scanner:

```python
def extract_nested_json(text, marker='<!-- gf_data:'):
    """Extract JSON objects from marker comments, handling nested braces."""
    for m in re.finditer(re.escape(marker) + r'\s*\{', text):
        start = m.end() - 1  # position of opening {
        depth = 1
        pos = start + 1
        while depth > 0 and pos < len(text):
            if text[pos] == '{': depth += 1
            elif text[pos] == '}': depth -= 1
            pos += 1
        if depth == 0:
            try:
                yield json.loads(text[start:pos])
            except json.JSONDecodeError:
                continue
```

## Detection

If extracting JSON from embedded comments, check whether any value in the JSON is itself an object (e.g. `"channel_mix": {"LU3":...}`, `"options": {"key":...}`). If yes, the simple regex `{[^}]+}` WILL fail.

## Prevention

When designing embedded JSON formats, if nested objects might be added later, use the brace counter pattern from the start rather than the simple regex.

## Applied In

- `grabfood_parser.py` v1.3 — `load_prev_week_data()`: found + fixed during GrabFood weekly log redesign
- `gen_grabfood_dashboard.py` v1.0 — `extract_gf_data()`: same fix applied
