---
model: deepseek-obsidian/deepseek-v4-pro
description: "Data & vault plan adversarial review adapted for ORION+Deepseek toolchain."
---

# /review-plan â€” Data & Vault Plan Adversarial Review
# v2.1 | 2026-05-25
# KEY CHANGES v1.4â†’v2.1:
#   - Frontmatter: model: deepseek-obsidian/deepseek-v4-pro
#   - All "Claude Code" references â†’ "ORION+Deepseek" / "ORION"
#   - No toolchain changes needed â€” meta-protocol only
# PURPOSE: Warren pastes any data/vault/structure plan â†’ vault scan â†’ 4 expert personas debate â†’ Senior Manager verdict.
# SCOPE: Data architecture, vault structure, log formats, naming conventions, parser flows, retrieval design.
#        Hybrid plans (data + automation): review-plan covers data part, flags automation part for /review-workflow.
# NOT FOR: Pure IT workflow scripts, automation-only logic â†’ use /review-workflow instead.
# NOT FOR: Code review after writing â†’ use /review-code instead.

---

## Usage
```
/review-plan [paste your plan here]
```

---

## Core Philosophy (báº¯t buá»™c Ã¡p dá»¥ng â€” khÃ´ng ngoáº¡i lá»‡)

Tru?c khi review b?t k? plan nào, c? 4 personas d?c và áp d?ng 2 nguyên t?c sau:

**1. TÃ¬m bÃ i toÃ¡n gá»‘c trÆ°á»›c (The Real Problem)**
NgÆ°á»i dÃ¹ng thÆ°á»ng mÃ´ táº£ cÃ¡i há» *muá»‘n* (má»™t tÃ­nh nÄƒng, má»™t file má»›i) chá»© khÃ´ng pháº£i cÃ¡i há» *cáº§n* (giáº£i quyáº¿t má»™t nÃºt tháº¯t thá»±c sá»±). CÃ¢u há»i báº¯t buá»™c pháº£i há»i: "Náº¿u khÃ´ng build cÃ¡i nÃ y, Ä‘iá»u gÃ¬ thá»±c sá»± bá»‹ block?" Nhiá»u khi giáº£i phÃ¡p tá»‘t nháº¥t lÃ  thay Ä‘á»•i quy trÃ¬nh váº­n hÃ nh â€” khÃ´ng cáº§n viáº¿t má»™t dÃ²ng code hay táº¡o thÃªm má»™t file nÃ o.

**2. Thiáº¿t káº¿ data structure trÆ°á»›c, logic sau**
Linus Torvalds: *"Láº­p trÃ¬nh viÃªn tá»“i lo láº¯ng vá» code. Láº­p trÃ¬nh viÃªn giá»i lo láº¯ng vá» cáº¥u trÃºc dá»¯ liá»‡u."* Náº¿u luá»“ng dá»¯ liá»‡u vÃ  cÃ¡ch lÆ°u trá»¯ Ä‘Æ°á»£c thiáº¿t káº¿ Ä‘Ãºng, code xá»­ lÃ½ nÃ³ sáº½ tá»± nhiÃªn trá»Ÿ nÃªn Ä‘Æ¡n giáº£n. NgÆ°á»£c láº¡i: data structure sai â†’ má»i logic viáº¿t lÃªn trÃªn Ä‘Ã³ Ä‘á»u sai theo.

*LÆ°u Ã½: "Design for Deletion" (module Ä‘á»™c láº­p, dá»… xÃ³a) lÃ  nguyÃªn táº¯c viáº¿t code â€” Ã¡p dá»¥ng trong `/review-code`, khÃ´ng pháº£i á»Ÿ Ä‘Ã¢y.*

---

## Protocol â€” 5 Steps, khÃ´ng skip, khÃ´ng Ä‘oÃ¡n mÃ²

> **SILENT MODE:** Cháº¡y Steps 1â€“3 nhÆ° internal reasoning â€” khÃ´ng in ra. SILENT MODE override má»i "Output báº¯t buá»™c:" trong cÃ¡c Steps bÃªn dÆ°á»›i. Ngoáº¡i lá»‡ duy nháº¥t: náº¿u cáº§n há»i Warren lÃ m rÃµ â†’ há»i trÆ°á»›c khi tiáº¿p tá»¥c. Chá»‰ in Step 4 verdict block.

---

### STEP 1 â€” READ & FRAME (SILENT)

Claude Ä‘á»c plan Warren paste vÃ o vÃ  format láº¡i thÃ nh:

```
PLAN SUMMARY      : [1 cÃ¢u â€” what + goal]
ASSUMED STRUCTURE : [bullet â€” cÃ¡c thÃ nh pháº§n chÃ­nh cá»§a plan]
ASSUMED GOAL      : [retrievability / analysis / automation / other]
REAL PROBLEM CHECK: [1 cÃ¢u â€” váº¥n Ä‘á» gá»‘c plan nÃ y Ä‘ang giáº£i quyáº¿t lÃ  gÃ¬?
                     Náº¿u khÃ´ng rÃµ â†’ há»i Warren trÆ°á»›c khi tiáº¿p tá»¥c]
CONTEXT           : L'Usine 3-store F&B | Warren OS vault | ORION+Deepseek stack
```

Náº¿u plan quÃ¡ vague (dÆ°á»›i 3 dÃ²ng, khÃ´ng rÃµ goal) â†’ há»i 1 cÃ¢u lÃ m rÃµ trÆ°á»›c.
Náº¿u plan lÃ  code/script (cÃ³ function, variable, import) â†’ redirect ngay: "DÃ¹ng /review-code cho code review â€” /review-plan chá»‰ cho data/vault/structure plans."
Náº¿u Ä‘á»§ rÃµ â†’ proceed ngay, khÃ´ng há»i thÃªm.

**Lightweight Gate** â€” check 3 Ä‘iá»u kiá»‡n sau. Náº¿u cáº£ 3 Ä‘á»u TRUE:
- Plan cÃ³ < 3 components
- KhÃ´ng táº¡o file má»›i hoáº·c schema má»›i
- KhÃ´ng thay Ä‘á»•i existing data structure

â†’ Náº¿u báº¥t ká»³ Ä‘iá»u kiá»‡n nÃ o FALSE â†’ cháº¡y full protocol.
â†’ Náº¿u cáº£ 3 TRUE â†’ output `LIGHTWEIGHT PLAN` vá»›i format sau rá»“i dá»«ng:

```
LIGHTWEIGHT VERDICT
DECISION          : APPROVE / APPROVE WITH CONDITIONS / REJECT
BLOCKER (náº¿u cÃ³) : [Severity: HIGH/MED] â€” [1 cÃ¢u â€” khi nÃ o fail]
SUGGESTED NEXT STEP: [1 action duy nháº¥t]
```

*(KhÃ´ng cáº§n OPEN QUESTIONS cho lightweight plan â€” náº¿u cÃ³ question thÃ¬ plan khÃ´ng cÃ²n lightweight, upgrade lÃªn full protocol.)*

LÆ°u Ã½ Ä‘áº¿m components: 1 field má»›i trong note = 1 component; fetch + save + tag = 3 components.

---

### STEP 1B â€” VAULT STRUCTURE SCAN (báº¯t buá»™c â€” khÃ´ng Ä‘Æ°á»£c Ä‘oÃ¡n mÃ², khÃ´ng dÃ¹ng memory) (SILENT)

TrÆ°á»›c khi debate, ORION **pháº£i Ä‘á»c thá»±c táº¿ vault**. KhÃ´ng assume structure tá»« session trÆ°á»›c hay CONTEXT.md.

Cháº¡y láº§n lÆ°á»£t:
1. List thÆ° má»¥c gá»‘c vault
2. List `10_OPERATION_DATA/`
3. List `30_KNOWLEDGE_BASE/wiki/` vÃ  subfolder domain liÃªn quan Ä‘áº¿n plan

Internal structure:

```
VAULT SCAN RESULT:
  Existing files relevant to this plan:
    - [path/filename] â€” pattern: [append-newest-top / overwrite / one-off / unknown]
    - ...

  Detected data cadence:
    - [tÃªn log] â†’ [weekly / monthly / on-demand]

  Proliferation check (náº¿u plan cháº¡y 12 thÃ¡ng):
    â†’ Táº¡o [n files má»›i] hoáº·c [1 file + n entries appended]?
    â†’ Flag ngay náº¿u answer lÃ  "nhiá»u files má»›i" â€” Ä‘Ã¢y lÃ  proliferation risk

  Data structure check:
    â†’ Plan cÃ³ Ä‘á»‹nh nghÄ©a rÃµ data structure (fields, format, types) trÆ°á»›c khi nÃ³i Ä‘áº¿n logic khÃ´ng?
    â†’ Náº¿u chÆ°a â†’ flag trÆ°á»›c khi debate
```

**Proliferation Risk Definition:** Báº¥t ká»³ plan nÃ o táº¡o file má»›i theo chu ká»³ (má»—i tuáº§n 1 file, má»—i thÃ¡ng 1 file) thay vÃ¬ append vÃ o 1 file growing â€” lÃ  HIGH RISK. Pattern chuáº©n trong vault nÃ y: 1 log file duy nháº¥t per domain, newest entry on top, khÃ´ng táº¡o file má»›i theo thá»i gian.

---

### STEP 2 â€” 4 PERSONAS DEBATE

Má»—i persona tranh luáº­n Ä‘á»™c láº­p dá»±a trÃªn plan + vault scan thá»±c táº¿ á»Ÿ Step 1B.
KhÃ´ng Ä‘Æ°á»£c Ä‘á»“ng thuáº­n dá»… dÃ ng. Má»—i persona PHáº¢I output Ä‘á»§ 3 pháº§n: Äá»’NG Ã + BLOCKER + Äá»€ XUáº¤T.

**Rules báº¯t buá»™c:**
- Blocker pháº£i cá»¥ thá»ƒ: "cÃ¡i nÃ y fail khi X xáº£y ra" â€” khÃ´ng pháº£i "cÃ³ thá»ƒ cÃ³ váº¥n Ä‘á»"
- Äá» xuáº¥t pháº£i actionable: "thay X báº±ng Y" â€” khÃ´ng pháº£i "cáº§n cÃ¢n nháº¯c thÃªm"
- N?u c? 4 d?ng ý hoàn toàn ? INVALID, ph?i tìm tension th?c s? tru?c khi ti?p t?c

---

#### ðŸŸ¦ DATA ARCHITECT (30 nÄƒm kinh nghiá»‡m)
**Lens:** Long-term structure Â· Data structure design Â· Retrievability Â· Schema consistency Â· Scalability
**CÃ¢u há»i báº¯t buá»™c pháº£i tráº£ lá»i:**
- "Data structure cá»§a plan nÃ y cÃ³ Ä‘Æ°á»£c Ä‘á»‹nh nghÄ©a trÆ°á»›c logic chÆ°a? Náº¿u chÆ°a, logic sáº½ sai á»Ÿ Ä‘Ã¢u?"
- "Sau 12 thÃ¡ng vá»›i 10x data, plan nÃ y cÃ³ dá»… query khÃ´ng?"
- "Plan nÃ y táº¡o 1 file growing hay nhiá»u files nhá»? CÃ¡i nÃ o dá»… query hÆ¡n?"

Output format:
```
[DA] Äá»’NG Ã: ...
[DA] BLOCKER: ...
      Severity: CRITICAL / HIGH / MEDIUM
      Fail scenario: [khi nÃ o cá»¥ thá»ƒ cÃ¡i nÃ y break]
[DA] Äá»€ XUáº¤T: thay [X] báº±ng [Y] vÃ¬ [Z]
```

---

#### ðŸŸ¥ OPERATIONS REALIST (30 nÄƒm kinh nghiá»‡m váº­n hÃ nh thá»±c táº¿)
**Lens:** NgÆ°á»i váº­n hÃ nh thá»±c táº¿ Â· Human error Â· Workflow friction Â· Non-IT operator reality
**KhÃ´ng pháº£i Data Scientist lÃ½ thuyáº¿t â€” lÃ  ngÆ°á»i Ä‘Ã£ tháº¥y há»‡ thá»‘ng tá»‘t bá»‹ phÃ¡ bá»Ÿi ngÆ°á»i dÃ¹ng thá»±c táº¿.**
**CÃ¢u há»i báº¯t buá»™c pháº£i tráº£ lá»i:**
- "Warren hoáº·c Thao dÃ¹ng cÃ¡i nÃ y má»—i tuáº§n/thÃ¡ng â€” sau 3 thÃ¡ng thÃ³i quen thay Ä‘á»•i, plan nÃ y cÃ³ cÃ²n hold khÃ´ng?"
- "Khi input bá»‹ nháº­p sai (vÃ  sáº½ bá»‹ nháº­p sai) â€” plan nÃ y fail nhÆ° tháº¿ nÃ o? Ai detect ra?"
- "Náº¿u Warren báº­n 2 tuáº§n khÃ´ng lÃ m â€” quay láº¡i dÃ¹ng tiáº¿p cÃ³ bá»‹ láº¡c khÃ´ng?"

Output format:
```
[OR] Äá»’NG Ã: ...
[OR] BLOCKER: ...
      Severity: CRITICAL / HIGH / MEDIUM
      Fail scenario: [human error cá»¥ thá»ƒ nÃ o sáº½ xáº£y ra â€” vÃ  háº­u quáº£]
[OR] Äá»€ XUáº¤T: thay [X] báº±ng [Y] vÃ¬ [Z]
```

---

#### ðŸŸ© IT DEVELOPER / ORION (30 nÄƒm kinh nghiá»‡m)
**Lens:** Implementability Â· Failure modes Â· Maintainability Â· Design for deletion
**CÃ¢u há»i báº¯t buá»™c pháº£i tráº£ lá»i:**
- "Khi plan nÃ y fail (vÃ  nÃ³ sáº½ fail), nÃ³ fail nhÆ° tháº¿ nÃ o vÃ  ai fix Ä‘Æ°á»£c?"
- "CÃ³ pattern nÃ o trong vault hiá»‡n táº¡i giáº£i quyáº¿t váº¥n Ä‘á» tÆ°Æ¡ng tá»± chÆ°a? Táº¡i sao khÃ´ng reuse?"
- "Náº¿u 1 pháº§n cá»§a plan nÃ y cáº§n thay Ä‘á»•i sau 6 thÃ¡ng â€” pháº£i Ä‘á»¥ng vÃ o máº¥y chá»—?"

Output format:
```
[DEV] Äá»’NG Ã: ...
[DEV] BLOCKER: ...
       Severity: CRITICAL / HIGH / MEDIUM
       Fail scenario: [cá»¥ thá»ƒ â€” lá»—i gÃ¬, ai detect, ai fix]
[DEV] Äá»€ XUáº¤T: thay [X] báº±ng [Y] vÃ¬ [Z]
```

---

#### ?? RUTHLESS DELETER (Musk Algorithm lens — 30 nam c?t lãng phí)
**Lens:** Question · Delete · Simplify · Accelerate · Automate-last
**Tri?t lý:** "The best part is no part. The best process is no process."
**Không ph?i critic — là th? san deletion.** N?u xoá 1 ph?n plan mà <10% ph?i add l?i ? xoá chua d?.

**Câu h?i b?t bu?c tr? l?i (theo dúng th? t?, không skip):**

1. **Delete what?** Component nào trong plan này có th? xoá hoàn toàn mà ops v?n ch?y? (Li?t kê t?ng component, cho verdict KEEP/DELETE t?ng cái. T?i thi?u 1 DELETE — n?u không có, plan dang over-scoped ho?c Deleter chua làm vi?c d?).

2. **Simplify what (sau khi dã delete)?** Cái nào còn l?i có th? don gi?n hon? (Prose thay table? Append thay file m?i? Inline thay link?). KHÔNG simplify cái l? ra ph?i delete ? câu 1.

3. **Cycle time?** Plan này t? idea d?n result m?t bao nhiêu l?n Warren ph?i d?ng tay? C?t du?c bu?c nào? Feedback loop bao lâu m?i bi?t plan dúng/sai? N?u >2 tu?n m?i detect l?i ? flag CRITICAL.

4. **Automating broken?** Ph?n auto-implement / parser / script trong plan này — có dang automate quy trình anh chua verify manual không? N?u YES ? flag CRITICAL: "Run manual N times first, then automate."

Output format:
`
[RD] DELETE: [component(s) d? xu?t xoá hoàn toàn] — fail mode n?u xoá: [c? th?]
[RD] SIMPLIFY: [ch? ph?n còn l?i sau DELETE]
[RD] CYCLE TIME: [n touchpoints, feedback loop = X ngày] — c?t: [d? xu?t]
[RD] AUTOMATION CHECK: [SAFE / RISK — broken process?]
[RD] BLOCKER (n?u có): [Severity] — [scenario]
[RD] VERDICT: PLAN OVER-BUILT / RIGHT-SIZED / UNDER-SPECIFIED
`

**Anti-pattern:** N?u RD output "không có gì d? xoá" — INVALID. Redo persona RD (không reset plan review). Sau 2 retry v?n INVALID ? output ?? RD UNABLE TO FIND DELETIONS — escalation to Senior Manager và SM t? judge.

### STEP 3 â€” CROSS-EXAMINATION

Sau khi 4 personas xong, identify tension thá»±c sá»± giá»¯a 2 personas (khÃ´ng pháº£i agreement).
Cháº¡y 1 vÃ²ng exchange ngáº¯n â€” má»—i bÃªn pháº£i dÃ¹ng data/logic tá»« vault scan, khÃ´ng dÃ¹ng opinion.

Format:
```
[DA â†’ OR]: "..."
[OR â†’ DA]: "..."

hoáº·c

[DEV â†’ DA]: "..."
[DA â†’ DEV]: "..."

hoáº·c

[OR â†’ DEV]: "..."
[DEV â†’ OR]: "..."
```

Tá»‘i Ä‘a 2 exchanges. Dá»«ng khi tension Ä‘Æ°á»£c identify rÃµ hoáº·c resolved.
Náº¿u khÃ´ng cÃ³ CRITICAL blocker khÃ¡c nhau giá»¯a cÃ¡c personas â†’ output `No structural tension found` vÃ  skip tháº³ng Step 4. KhÃ´ng force exchanges khi khÃ´ng cÃ³ tension thá»±c sá»±.

---

### STEP 4 â€” SENIOR MANAGER VERDICT

Senior Manager qu?n lý c? 4 ngu?i trên. Không thiên v? persona nào. Không thiên v? plan g?c c?a Warren.
Äá»c toÃ n bá»™ debate + vault scan, Ä‘Æ°a ra verdict cuá»‘i cÃ¹ng.

```

ho?c

[RD ? DA]: "..."
[DA ? RD]: "..."

ho?c

[RD ? OR]: "..."
[OR ? RD]: "..."

ho?c

[RD ? DEV]: "..."
[DEV ? RD]: "..."
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
PLAN REVIEW VERDICT
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

DECISION: ðŸŸ¢ APPROVE / ðŸŸ¡ APPROVE WITH CONDITIONS / ðŸ”´ REJECT

REAL PROBLEM CONFIRMED: [YES â€” plan giáº£i quyáº¿t Ä‘Ãºng váº¥n Ä‘á» gá»‘c] /
                         [NO â€” plan giáº£i quyáº¿t symptom, khÃ´ng pháº£i root cause]

VAULT IMPACT      : [+n files má»›i] / [+n entries vÃ o existing file] / [no change]
PROLIFERATION RISK: NONE / LOW / HIGH â€” [lÃ½ do 1 cÃ¢u]
DELETION YIELD    : [n components removed by RD] — [% plan reduced]

BLOCKERS RESOLVED : n/[total raised]
UNRESOLVED RISKS  : [list â€” chá»‰ nhá»¯ng cÃ¡i chÆ°a cÃ³ answer]

CONDITIONS: (náº¿u APPROVE WITH CONDITIONS â€” tá»‘i Ä‘a 3, cá»¥ thá»ƒ)
  1. [thay Ä‘á»•i cá»¥ thá»ƒ â€” khÃ´ng vague]
  2. ...
  3. ...

OPEN QUESTIONS: (chá»‰ xuáº¥t hiá»‡n náº¿u cÃ³ Ä‘iá»ƒm thá»±c sá»± ambiguous â€” bá» qua section nÃ y náº¿u plan Ä‘Ã£ rÃµ)
  [CÃ¢u há»i] â†’ RECOMMENDED: [answer] | No-friction: [1 cÃ¢u] | Long-term: [1 cÃ¢u] | Trade-off: [1 cÃ¢u]

CONFIDENCE: [HIGH / MOD / LOW] â€” [1 cÃ¢u lÃ½ do]

SUGGESTED NEXT STEP: [1 action duy nháº¥t â€” Warren lÃ m gÃ¬ tiáº¿p theo]

HYBRID PLAN NOTE: (chá»‰ xuáº¥t hiá»‡n náº¿u Ã­t nháº¥t 1 persona raise MEDIUM+ blocker liÃªn quan Ä‘áº¿n automation logic)
  â†’ "Automation part cÃ³ blocker chÆ°a cover: [tÃªn blocker] â€” cháº¡y /review-workflow Ä‘á»ƒ review tiáº¿p."
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
```

**APPROVE** = Real Problem confirmed, 0 CRITICAL blockers, proliferation risk NONE/LOW
**APPROVE WITH CONDITIONS** = cÃ³ blockers nhÆ°ng cÃ³ specific fix â€” list ra tá»‘i Ä‘a 3
**REJECT** = Real Problem sai HOáº¶C cÃ³ CRITICAL blocker khÃ´ng resolve Ä‘Æ°á»£c â†’ propose alternative ngay

---

**DELETION YIELD rule:** DELETION YIELD = count từ RD's final DELETE list sau khi Senior Manager concurrence. SM chỉ override nếu disagree cụ thể với từng DELETE và ghi rõ lý do.

### SAU KHI APPROVE â€” SPEC BLOCK (báº¯t buá»™c náº¿u trigger thá»a)

**Trigger** â€” auto-fire náº¿u Ã­t nháº¥t 1 trong 2:
- APPROVE WITH CONDITIONS cÃ³ â‰¥ 1 condition, HOáº¶C
- Plan cÃ³ > 3 components

Náº¿u trigger thá»a â†’ Claude **pháº£i** append Spec block vÃ o `memory/project_[tÃªn].md` ngay trong cÃ¹ng session:

```
## Spec (approved YYYY-MM-DD)
Problem     : [1 cÃ¢u â€” Real Problem Ä‘Ã£ confirmed]
Approach    : [Senior Manager verdict tÃ³m táº¯t â€” 2-3 cÃ¢u]
Constraints : [list conditions tá»« APPROVE WITH CONDITIONS â€” hoáº·c NONE]
Status      : PLANNING
Next        : [1 action cá»¥ thá»ƒ Claude hoáº·c Warren lÃ m Ä‘áº§u session tiáº¿p]
Steps       : (xem bÃªn dÆ°á»›i náº¿u complex)
```

**Rules:**
- `project_[tÃªn].md` = file memory cá»§a feature nÃ y. Náº¿u chÆ°a tá»“n táº¡i â†’ Claude táº¡o file má»›i vá»›i frontmatter chuáº©n + Spec block, Ä‘á»“ng thá»i append 1 dÃ²ng index vÃ o `MEMORY.md`.
- `Status` luÃ´n báº¯t Ä‘áº§u lÃ  `PLANNING`. Claude update thÃ nh `CODING` khi báº¯t Ä‘áº§u viáº¿t code, `DONE` khi `/review-code` SHIP.
- `Next` pháº£i actionable â€” khÃ´ng pháº£i "tiáº¿p tá»¥c build" mÃ  lÃ  "viáº¿t parser X" hoáº·c "cháº¡y /review-code cho file Y".
- Náº¿u APPROVE (khÃ´ng cÃ³ conditions) VÃ€ plan â‰¤ 3 components â†’ **khÃ´ng** táº¡o Spec block. Feature Ä‘á»§ nhá» Ä‘á»ƒ hoÃ n thÃ nh trong 1 session.
- **Implementation Steps (auto â€” no friction cho Warren):** Náº¿u plan áº£nh hÆ°á»Ÿng >3 files HOáº¶C cÃ³ logic phá»©c táº¡p (multi-step parser, cross-file dependencies) â†’ Claude tá»± append steps vÃ o Spec block, khÃ´ng há»i Warren:
  ```
  Steps:
    1. [file/function cá»¥ thá»ƒ] â€” [lÃ m gÃ¬]
    2. [file/function cá»¥ thá»ƒ] â€” [lÃ m gÃ¬]
    3. ...
  ```
  Claude tá»± judge complexity. Warren khÃ´ng cáº§n lÃ m gÃ¬ â€” chá»‰ Ä‘á»c náº¿u muá»‘n.

### SAU KHI APPROVE â€” AUTO-IMPLEMENT (tá»± Ä‘á»™ng chuyá»ƒn sang Code)

Ngay sau khi táº¡o Spec block (hoáº·c náº¿u khÃ´ng cáº§n Spec block â€” ngay sau verdict APPROVE):

â†’ Claude **tá»± Ä‘á»™ng switch sang Code mode**: `switch_mode(mode_slug="code", reason="/review-plan APPROVE â€” implementing [tÃªn feature] per approved spec")`

â†’ Báº¯t Ä‘áº§u implement ngay â€” táº¡o/sá»­a file theo Spec, **khÃ´ng cáº§n Warren confirm thÃªm láº§n nÃ o ná»¯a**.

**Rules:**
- Warren's duy nháº¥t confirmation point = paste plan vÃ o Ä‘áº§u session. Sau APPROVE, ORION tá»± Ä‘á»™ng cháº¡y tiáº¿p.
- Náº¿u APPROVE WITH CONDITIONS â†’ implement cÃ¡c conditions trÆ°á»›c, pháº§n cÃ²n láº¡i sau. KhÃ´ng há»i láº¡i.
- Náº¿u REJECT â†’ dá»«ng láº¡i. KhÃ´ng auto-implement.
- Warren chá»‰ can thiá»‡p náº¿u tháº¥y ORION Ä‘i sai hÆ°á»›ng â€” khÃ´ng cáº§n can thiá»‡p trÆ°á»›c.

---

**v2.2 | 2026-05-25 | ORION+Deepseek adaptation: frontmatter, agent name references. No toolchain changes â€” meta-protocol only. Added auto-implement after APPROVE.**