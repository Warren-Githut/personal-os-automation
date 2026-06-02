---
model: deepseek-obsidian/deepseek-v4-pro
description: "Review ideas in _ideas/ - tag keep/promote/drop. Run first Sunday each month."
updated: 2026-06-02
---

# /ideas-review - Monthly Ideas Review
# v1.0 | 2026-05-31
# PURPOSE: Review all pending ideas in _ideas/, tag as keep/promote-to-task/drop.
# CADENCE: First Sunday of each month (separated from /lint v4.0)

## Usage
```
/ideas-review
```

## Steps

### 1. Check cadence
If today != first Sunday of current month -> skip with message.

### 2. Read ideas files
- Current month: _ideas/YYYY-MM.md
- Previous month: _ideas/YYYY-{prev-MM}.md (if exists)

### 3. Find pending ideas
Entries without [KEPT], [PROMOTED], or [DROPPED] tag.

### 4. Show Warren for action
Present each pending idea with [k] Keep [p] Promote [d] Drop.

### 5. Apply actions
- Keep: append [KEPT YYYY-MM-DD]
- Promote: create task in _inbox/tasks.md + append [PROMOTED-TO-TASK YYYY-MM-DD]
- Drop: append [DROPPED YYYY-MM-DD]

### 6. Save + commit
Update files, log to activity log.