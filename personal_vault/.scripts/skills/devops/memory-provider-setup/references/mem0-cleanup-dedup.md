# Mem0 Cleanup & Dedup — Empty/Garbage Point Removal

## Problem (seen 2026-07-07)

After a `compress-memory` run pushed 23 facts to Qdrant directly, a `scroll` of
`user_id=warren` returned **49 points** — 23 real facts + **26 EMPTY garbage points**
(`text: ""`, `meta: {}`). These empty points are non-retrievable noise (often left behind
by failed/broken plugin writes, aborted sessions, or partial `mem0_add` tool calls).

They waste context budget on search and inflate counts. They must be detected and deleted.

## Why this is needed

- The Hermes `mem0_*` tools and `Memory.from_config()` do NOT expose "list all raw points"
  cleanly, and they error when the plugin is broken. Direct Qdrant REST is the reliable path.
- Direct-REST bulk push (the bypass in `cross-profile-mem0-write-via-qdrant-api.md`) does
  NOT write mem0's `hash` dedup field — so re-running a bulk push CAN create duplicates.
  Cleanup + pre-push dedup check is the safeguard.

## Workflow (verified 2026-07-07)

### 1. Scroll all points for a user_id
```python
import requests
Q = "http://localhost:6333/collections/mem0/points/scroll"
body = {"filter": {"must": [{"key": "user_id", "match": {"value": "warren"}}]},
        "limit": 100, "with_payload": True, "with_vector": False}
r = requests.post(Q, json=body, timeout=20)
pts = r.json()["result"]["points"]
```

### 2. Detect empty / garbage
```python
empties = []
for p in pts:
    pl = p.get("payload", {})
    txt = (pl.get("memory") or pl.get("text") or "").strip()
    if not txt:
        empties.append(p["id"])
print(f"total={len(pts)} empty={len(empties)}")
```

### 3. Delete empties (immediate, no undo)
```python
DEL = "http://localhost:6333/collections/mem0/points/delete"
if empties:
    d = requests.post(DEL, json={"points": empties}, timeout=20)
    print("DELETE", d.status_code)
```

### 4. Recount + verify-search a known fact
```python
c = requests.post("http://localhost:6333/collections/mem0/points/count",
    json={"filter": {"must": [{"key": "user_id", "match": {"value": "warren"}}]}}, timeout=10)
print("warren count after:", c.json()["result"]["count"])

# probe + search to confirm retrieval works
vec = requests.post("http://localhost:11434/api/embeddings",
    json={"model": "nomic-embed-text", "prompt": "dashboard revenue M triệu VND không dùng k"}).json()["embedding"]
s = requests.post("http://localhost:6333/collections/mem0/points/search",
    json={"vector": vec, "limit": 2, "with_payload": True,
          "filter": {"must": [{"key": "user_id", "match": {"value": "warren"}}]}}, timeout=10).json()
for p in s["result"]:
    print("-", p["payload"]["memory"][:80])
```
Result this session: 49 → 23, empty=0, search returned correct fact. ✅

## Dedup BEFORE bulk push (avoid creating duplicates)

If re-running `mem0_bulk_push.py`, first collect existing texts for the user_id and
skip facts already present:
```python
existing = set()
for p in pts:  # from step 1
    pl = p.get("payload", {})
    existing.add((pl.get("memory") or pl.get("text") or "").strip())
new_facts = [f for f in facts if f.strip() not in existing]
```
Then push only `new_facts`. This prevents duplicate points when `compress-memory` runs twice.

## Caution

- Deleting from Qdrant is immediate and irreversible — the Hermes mem0 layer has no recycle bin.
- Only delete points you can identify as empty/garbage (no text, no metadata). Do NOT mass-delete
  by age unless Warren approves — real facts may be old but still valid.
- Empty-point detection is safe because a real memory ALWAYS has non-empty `text`/`memory`.
