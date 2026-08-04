import sys, os, json

# Add hermes-agent venv to path (has the `mem0` lib)
venv_site = r'C:\Users\khoans\AppData\Local\hermes\hermes-agent\venv\Lib\site-packages'
sys.path.insert(0, venv_site)

# OpenAI-compatible client for mem0 LLM extraction (uses DeepSeek per config pattern)
os.environ['OPENAI_API_KEY'] = os.environ.get('DEEPSEEK_API_KEY', '')
os.environ['OPENAI_BASE_URL'] = 'https://api.deepseek.com/v1'

# === EDIT THESE ===
profile_dir = r'C:\Users\khoans\AppData\Local\hermes\profiles\personal_profile'  # or stock-profile / warren-profile
USER = 'warren_personal'  # VERIFY per profile: personal='warren_personal', stock likely 'warren_stock'
# =================

os.chdir(profile_dir)

with open('mem0.json') as f:
    config = json.load(f)

from mem0 import Memory
m = Memory.from_config(config)

facts = [
    "fact 1 durable text...",
    "fact 2 durable text...",
]

print("=== PUSHING FACTS TO MEM0 FAISS (b) ===")
added_ids = []
for i, fact in enumerate(facts):
    try:
        res = m.add(fact, user_id=USER)
        ids = [x.get('id') for x in res.get('results', []) if isinstance(x, dict)]
        added_ids.extend(ids)
        print(f"fact[{i}] added: {ids}")
    except Exception as e:
        print(f"fact[{i}] ERROR: {e}", file=sys.stderr)

print(f"=== TOTAL ADDED: {len(added_ids)} ===")
print("ADDED_IDS=" + json.dumps(added_ids))
