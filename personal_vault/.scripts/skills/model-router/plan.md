# Implementation Plan: DeepSeek Model Router (Option B)

## Overview

Build Hermes skill `model-router` — tự động routing giữa DeepSeek V4 Flash (default) và V4 Pro (khi cần), kèm cost quota 10%, daily report, slash commands `/model-router on/off/override`.

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Skill type** | SKILL.md (instructions) + Python scripts | Hermes đọc SKILL.md làm system instruction; scripts handle state + report |
| **Routing mechanism** | SKILL.md hướng dẫn Hermes tự quyết định model mỗi turn | Không cần plugin/sdk — skill content là instruction cho Hermes |
| **Pro spawn** | Hermes CLI `--model` override | Đã confirm trong interview |
| **Quota storage** | JSON file (`scripts/quota_state.json`) | Đơn giản nhất, ko cần DB |
| **Slash commands** | Hermes native `/command` | Tận dụng Hermes command system có sẵn |
| **Daily report** | Cronjob (cronjob tool) gọi daily_report.py | Tách biệt khỏi core routing |

## Dependency Graph

```
quota.py (state management)
    │
    ├── router.py (routing decision)
    │       │
    │       └── SKILL.md embed routing rules
    │
    ├── commands.py (/model-router on/off/override)
    │
    ├── daily_report.py (report generation)
    │       │
    │       └── cronjob (scheduled trigger)
    │
    └── test_router.py (smoke tests)
```

## Task List

### Phase 1: Foundation (Skill Skeleton + Quota State)

- [ ] **Task 1.1: Create skill directory + update SKILL.md**
  - **Acceptance:** `skills/model-router/` exists, SKILL.md có frontmatter + routing instructions
  - **Verify:** `hermes skill validate model-router` passes
  - **Files:** `skills/model-router/SKILL.md`
  - **Size:** S (1 file)

- [ ] **Task 1.2: Create quota.py — state management**
  - **Acceptance:** `quota_state.json` CRUD hoạt động: init, increment Pro, check %, reset monthly
  - **Verify:** `python3 scripts/quota.py --check` trả về đúng state
  - **Files:** `skills/model-router/scripts/quota.py`, `skills/model-router/scripts/quota_state.json`
  - **Size:** S (2 files)

**Checkpoint: Foundation**
- [ ] Skill validated
- [ ] Quota state read/write works
- [ ] Monthly reset logic verified

### Phase 2: Core Routing Logic

- [ ] **Task 2.1: Create router.py — routing decision engine**
  - **Acceptance:** Detect 3 triggers (tool-chain ≥3, factual accuracy, Flash failure). Decide Flash vs Pro. Increment quota.
  - **Verify:** Unit test với mock trigger conditions
  - **Files:** `skills/model-router/scripts/router.py`
  - **Size:** M (1 file, ~80-120 lines)

- [ ] **Task 2.2: Create commands.py — slash commands**
  - **Acceptance:** `/model-router on` bật routing, `/model-router off` tắt (all Flash), `/model-router override` nới threshold 20%
  - **Verify:** Test từng command output
  - **Files:** `skills/model-router/scripts/commands.py`
  - **Size:** S (1 file, ~50 lines)

**Checkpoint: Core Logic**
- [ ] Router quyết định đúng model cho từng trigger
- [ ] 3 slash commands hoạt động
- [ ] Quota increment + check sau mỗi decision

### Phase 3: Daily Report + Integration

- [ ] **Task 3.1: Create daily_report.py**
  - **Acceptance:** Generate 1-line report format: `📊 Model Router: 8% Pro (32/400) | Quota: 10%`
  - **Verify:** `python3 scripts/daily_report.py` in ra đúng format
  - **Files:** `skills/model-router/scripts/daily_report.py`
  - **Size:** XS (1 file, ~30 lines)

- [ ] **Task 3.2: Wire cronjob for daily report**
  - **Acceptance:** Cronjob chạy mỗi sáng, inject report vào morning brief + Telegram
  - **Verify:** Cronjob triggers, output đúng
  - **Files:** cronjob config (via `cronjob` tool)
  - **Size:** XS

- [ ] **Task 3.3: Create smoke tests**
  - **Acceptance:** Test quota read/write, routing decision, commands
  - **Verify:** `pytest tests/` passes
  - **Files:** `skills/model-router/tests/test_router.py`
  - **Size:** S (1 file)

**Checkpoint: Integration**
- [ ] Daily report cronjob active
- [ ] Smoke tests pass
- [ ] End-to-end: chat → router decide → tag → quota track

### Phase 4: Deploy + Verify

- [ ] **Task 4.1: Install skill + verify in warren-profile**
  - **Acceptance:** `hermes skill install .` works, skill shows in `hermes skill list`
  - **Verify:** Skill loaded, routing rules active
  - **Files:** None (config change via hermes CLI)
  - **Size:** XS

- [ ] **Task 4.2: Test proxy support cho DeepSeek V4 Pro**
  - **Acceptance:** `curl` tới proxy với `model=deepseek-v4-pro` trả về 200
  - **Verify:** API call test
  - **Files:** None
  - **Size:** XS

**Checkpoint: Complete**
- [ ] Skill installed and active
- [ ] Proxy support confirmed
- [ ] All success criteria from spec met

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Proxy port 8787 ko support `deepseek-v4-pro` | **High** — routing fail | Test ngay Phase 1 trước khi build tiếp. Nếu fail → config thêm 1 provider riêng cho Pro. |
| Hermes CLI `--model` flag ko work như expected | **Medium** — Pro spawn fail | Test CLI flag trước. Alternative: spawn Pro session qua API call thay vì CLI. |
| SKILL.md instructions ko đủ mạnh để Hermes tự routing | **Medium** — Hermes ignore rule | Embed routing rule trong instructions cực kỳ explicit, test với sample message. |
| Quota file bị corrupt | **Low** — mất counter | Auto-reset file nếu parse fail + log warning. |

## Task Sizing

| Task | Size | Est. Time |
|------|------|-----------|
| 1.1 Skill skeleton | S | 5 min |
| 1.2 quota.py | S | 10 min |
| 2.1 router.py | M | 20 min |
| 2.2 commands.py | S | 10 min |
| 3.1 daily_report.py | XS | 5 min |
| 3.2 Wire cronjob | XS | 5 min |
| 3.3 Smoke tests | S | 10 min |
| 4.1 Install + verify | XS | 5 min |
| 4.2 Test proxy | XS | 2 min |
| **Total** | | **~72 min** |

## Open Questions

- **Proxy support:** Confirm trước khi build router. Nếu proxy ko support Pro → add 1 provider riêng trong config.
