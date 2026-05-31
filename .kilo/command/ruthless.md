---
model: deepseek-obsidian/deepseek-v4-pro
description: "Musk Algorithm applied to any target — file, SOP, wiki page, idea, process. 5-step ruthless deletion lens."
---

# /ruthless — Musk Algorithm Deletion Lens
# v1.0 | 2026-05-31
# PURPOSE: Apply Elon Musk's 5-step algorithm (Question · Delete · Simplify · Accelerate · Automate-last) to any target in Warren's world — files, SOPs, wiki pages, ideas, processes.
# POSITION IN WORKFLOW: Any artifact ? /ruthless ? RD verdict ? action (edit / delete / archive / restructure)
# NOT FOR: Plans that need >file review ? use /review-plan. Already-coded features ? use /review-audit.

---

## Usage

```
/ruthless [tên file, path, ho?c paste text]
```

**Auto-detect modes:**
- Match du?c file trong vault (tên ho?c path) ? d?c file ? ruthless
- Match >1 file ? list cho Warren ch?n (show path + trích 3 dòng d?u)
- Match 1 file ? show path, h?i confirm tru?c khi ch?y
- Không match file nào ? treat input nhu raw text ? ruthless tr?c ti?p (không confirm)

---

## Protocol — 5-Step Musk Algorithm (b?t bu?c, không skip, không d?o th? t?)

### STEP 1 — Question requirements

Ð?c target. Tr? l?i:
- Target này dang gi?i quy?t v?n d? gì?
- Problem có th?t không, hay là symptom?
- N?u xoá target này, h?u qu? th?c t? là gì? (c? th?, không vague)
- Ai/di?u gì b? ?nh hu?ng?

### STEP 2 — Try to delete

Identify parts c?a target có th? xoá hoàn toàn.
- Li?t kê t?ng component/section/step c?a target
- Cho verdict KEEP/DELETE t?ng cái
- T?i thi?u 1 DELETE — n?u không ? INVALID, redo
- Sau 2 retry v?n không tìm du?c DELETE ? output "?? RD UNABLE TO FIND DELETIONS — target is minimal or analysis exhausted. Keep as-is recommended unless new context emerges."

### STEP 3 — Simplify (after deletion)

Cho ph?n còn l?i:
- Có th? don gi?n hon không? (prose ? bullet? 5 steps ? 3 steps?)
- KHÔNG simplify cái l? ra ph?i delete ? Step 2

### STEP 4 — Accelerate cycle time

- T? lúc start d?n lúc có k?t qu? m?t bao lâu?
- Có th? c?t bu?c trung gian nào?
- Feedback loop bao lâu m?i bi?t dúng/sai?

### STEP 5 — Automate (last, with warning)

- Có dang automate quy trình chua verify manual không?
- N?u YES ? flag CRITICAL: "Run manual N times first, then automate."
- N?u NO ? proceed

---

## Output Format

```
??????????????????????????????????????
RUTHLESS VERDICT — [target summary 1 câu]
??????????????????????????????????????

TARGET: [tên file / path / raw text summary]
SIZE: [n dòng ho?c n ký t?]

[RD] STEP 1 — QUESTION: [câu tr? l?i 2-3 dòng — v?n d? g?c]

[RD] STEP 2 — DELETE:
  - [component 1]: KEEP / DELETE — [lý do]
  - [component 2]: KEEP / DELETE — [lý do]
  - ...

[RD] STEP 3 — SIMPLIFY: [ch? ph?n còn l?i sau Step 2]
  - [suggestion 1]
  - [suggestion 2]

[RD] STEP 4 — CYCLE TIME: [estimate] — c?t: [d? xu?t]

[RD] STEP 5 — AUTOMATION CHECK: [SAFE / RISK — broken process?]

??????????????????????????????????????
RECOMMENDED ACTION:
  ??? DELETE / ?? CUT [n] components / ?? RESTRUCTURE / ? KEEP AS-IS

REASON: [1-2 câu — d?a trên Step 2 analysis]
??????????????????????????????????????
```

### Map to actionable outcome

| Verdict | Action |
|---|---|
| ??? DELETE | Warren xoá file / xoá ph?n n?i dung |
| ?? CUT components | Warren edit file, xoá các component marked DELETE |
| ?? RESTRUCTURE | T?o plan cho restructure (/generate-plan ? /review-plan) |
| ? KEEP AS-IS | Không làm gì — target dã t?i uu |

---

## Rules

- Steps 1-5 b?t bu?c, không skip, không d?o th? t?. Automate là step cu?i cùng = di?u ki?n b?t bu?c.
- Step 2 ph?i có t?i thi?u 1 DELETE — n?u không, redo. Sau 2 retry ? escalate message.
- Không suggest automate tru?c khi verify manual workflow.
- Không modify file tr?c ti?p — ch? recommend action. Warren quy?t d?nh edit.

---

## Anti-patterns

- ? Automate Step 2-3 khi Step 1 chua hoàn thành — ph?i di dúng th? t?
- ? B? qua Step 2 (delete) d? di th?ng Simplify — sai Musk Algorithm
- ? Skip Step 4 (cycle time) vì "không liên quan d?n content file" — cycle time áp d?ng cho process, không ch? file content
- ? Modify file tr?c ti?p — /ruthless là diagnostic, không ph?i surgical tool
- ? S? d?ng khi target dã du?c /review-plan review — dã có RD persona trong review plan

---

## Integration

/ruthless là **phiên b?n standalone** c?a RUTHLESS DELETER persona trong /review-plan.
- Trong /review-plan: RD ch? dánh deletion c?a 1 plan (dã có structure + components)
- /ruthless: RD dánh b?t c? th? gì (file, SOP, wiki page, idea text) — linh ho?t hon, pre-filter

**Flow suggestion:** /ruthless ? RD recommends restructure ? /generate-plan ? /review-plan ? code

---

**v1.0 | 2026-05-31 | Created per Warren's request: standalone Musk Algorithm command for arbitrary targets.**