# Regex Nested Brace Pitfall

## Symptom

A regex like `[^}]+` inside a capture group fails to match the full JSON object when the JSON contains nested `{}` braces (e.g. `{"channel_mix":{"LU3":4.2}}`). Only the first `}` is matched, truncating the result.

## Root Cause

The character class `[^}]+` greedily matches characters EXCEPT `}`. As soon as it hits the first `}` (even if it's inside a nested object), the match stops. For flat JSON this works fine, but any nested object breaks it.

## Fix: Brace Counter

Replace the `[^}]+` regex with a simple depth-tracking loop:

```python
m = re.search(r"<!-- gf_data:\s*\{", text)
if not m: return None
start = m.end() - 1  # position of opening {
depth = 1
pos = start + 1
while depth > 0 and pos < len(text):
    if text[pos] == '{': depth += 1
    elif text[pos] == '}': depth -= 1
    pos += 1
if depth == 0:
    return json.loads(text[start:pos])
return None
```

## Detection

If you're using a regex pattern like `{[^}]+}` or `({[^}]+})` to extract JSON, test it against a string with nested objects:

```python
test = '{"a":{"b":1}}'
m = re.search(r'({[^}]+})', test)
print(m.group(1))  # BUG: prints {"a":{"b":1}}? NO — prints {"a":{"b":1} (truncated!)
#                                                       actually stops at first }
```

## Prevention

Any time the target content can contain nested braces (JSON, nested dicts, template blocks), use a brace counter instead of a regex capture group. This applies to:

- JSON blocks in HTML comments: `<!-- gf_data: {...} -->`
- Template literals: `{{...}}` or `{{...}}` that can nest
- Any braces-delimited data where nesting is possible

## Real-World Impact

In session 2026-07-06, `load_prev_week_data()` in `grabfood_parser.py` used `[^}]+` to parse `<!-- gf_data: {...} -->` blocks. When the JSON block was augmented with nested `channel_mix: {"LU3":4.2}` objects, the regex captured only `{"week":"2026-W27","channel_mix":{"LU3":4.2`, truncating after the first `}` in the nested object. This caused `json.loads()` to fail, which returned `None` — meaning the recommendation engine had no previous-week data and defaulted to "organic, ổn định" for all stores.
