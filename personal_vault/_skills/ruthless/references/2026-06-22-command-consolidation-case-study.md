# 2026-06-22: Command Consolidation — ops-context-update + ops-weekly-connections → ops-weekly-report

## Symptoms
- `/ops-context-update`: Scanned 7 days, drafted 3 themes, waited for Warren confirm, wrote CONTEXT.md §5. Ran exactly 1 time in its life. No cron was ever created despite SOUL.md claiming "Mon 07:00." Every scan it did was already done by `/ops-weekly-report`.
- `/ops-weekly-connections`: Scanned 10+ sources, wrote to a separate log file (`weekly_connections_log.md`), fed themes into context-update. Every cross-domain check overlapped with what the weekly report already synthesized.
- Weekly report already had: all source scans (11 files), Cross-Domain Connections section (merged from weekly-connections on 22/06), and was the natural owner for the CONTEXT §5 update.

## Analysis
| Check | ops-context-update | ops-weekly-connections | ops-weekly-report |
|-------|-------------------|----------------------|-------------------|
| Scan source logs | ✅ | ✅ | ✅ (11 files) |
| Find cross-domain patterns | ❌ | ✅ | ✅ (merged section) |
| Draft themes for CONTEXT §5 | ✅ | ✅ (fed into) | ✅ (Phase 7) |
| Auto-update CONTEXT.md | ❌ (waits for confirm) | ❌ | ✅ (no confirm) |
| Write separate log file | ❌ | ✅ (weekly_connections_log.md) | ❌ (1 file only) |
| Scan from scratch | ✅ (duplicate) | ✅ (duplicate) | ✅ (original) |

**Verdict:** Both commands were doing work the weekly report already covered. ops-context-update added a manual confirm gate that was never used. ops-weekly-connections wrote a separate log file nobody read.

## Execution
1. Patched `ops-weekly-report` SKILL.md: added Phase 7 (auto-update CONTEXT.md §5), replaced "Feed into Monday's /ops-context-update" with "CONTEXT §5 themes (auto-updated in Phase 7)"
2. Deleted `ops-context-update` skill (absorbed_into=ops-weekly-report)
3. Archived `weekly_connections_log.md` (status→archived, kept for W23-W26 historical reference)
4. Patched 13 vault files: a deprecated command-index file, HERMES_COMMANDS, USER_GUIDE, CONTEXT.md (4 places), OPERATION_INDEX, _CONNECTIONS_Hub, weekly_ops_synthesis.md, SOUL.md, ops/SKILL.md, observer-mode reference
5. Deleted 4 dead artifacts: _kilo/MIGRATION_PLAN.md, _kilo/ACTIVITY_LOG.md, _kilo/memory/project_opdata-command-sync.md, _cases/closed/2026-05_ruthless-cases-audit.md

## Result
- 3 commands → 1 command (ops-weekly-report)
- 2 skills deleted
- 1 log file archived
- 0 confirm gates removed
- ~85 lines of stale references cleaned from vault

## Lessons
1. **If a command requires manual confirm to write data already available in another command's output, it's redundant.** The confirm gate is a workaround for not trusting the data flow, not a feature.
2. **Separate log files for derivative analysis proliferate quickly.** Connections (weekly_connections_log.md) + synthesis (weekly_ops_synthesis.md) = 2 files doing same thing. Keep 1.
3. **Warren's pattern is clear:** He asks "thẳng thắng advise — có dư thừa ko?" → expects conclusion-first Vietnamese → wants merge/delete over keep. Don't hesitate.
4. **Clean all vault references at once.** 13 files had stale references to deleted commands. One sweep is cheaper than 13 individual fixes.