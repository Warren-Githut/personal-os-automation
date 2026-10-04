# marketingskills (coreyhaines31) — F&B Adapt Insights

## Source
GitHub: `coreyhaines31/marketingskills` — README read via curl fallback (2026-07-17, [HIGH]).
48 AI agent skills cho SaaS/tech founders (Claude Code, Codex, Cursor). Agent Skills spec (agentskills.io).

## What it is
Collection of markdown skills for marketing tasks: CRO, copywriting, SEO, ads, analytics, growth, retention, strategy. `product-marketing` skill = foundation (all others read it first).

## Relevant skills for L'Usine (F&B offline)
| Skill | L'Usine use | Fit |
|-------|-------------|-----|
| `marketing-council` | Simulated board of advisors → **y hệt promo-eval 4-lens (Byron Sharp/Ogilvy/Hormozi/Godin)** | ✅ High |
| `marketing-loops` | Recurring self-running marketing workflow → **chính là Agent Marketing Manager con đề xuất** | ✅ High |
| `copywriting` + `social` | Caption IG/FB, copy promo chuẩn brand | ✅ High |
| `image` | Sinh POSM/LTO artwork → wrap bằng SOP_030 Brand Gate | ✅ Med |
| `ab-testing` | **Đã có trong promo-eval §3.5** (Treatment/Control net incremental) | ✅ Done |
| `referrals` / `community` | Loyalty program L'Usine (đã có `Loyalty_Redemption_2026_Tracker.md`) | ✅ Med |
| `ads` / `ad-creative` | GrabFood/Lazada ads | ✅ Med |

## Low fit (SaaS/web bias — DROP for L'Usine)
- `cro`, `signup`, `onboarding`, `popups`, `paywalls` — web conversion only.
- `seo-audit`, `ai-seo`, `programmatic-seo`, `schema` — L'Usine local, SEO kém trọng.
- `revops`, `sales-enablement`, `competitors` — B2B SaaS bias.

## Key insight (durable)
promo-eval của Warren **đã cover 80%** cái marketing-council + ab-testing + loops.
Repo này = **tham khảo framework, không phải giải pháp thay thế**.
→ Khi Warren gửi repo marketing SaaS: adapt framework, KHÔNG cài nguyên xi. Fork 5-6 skill relevant + Việt hóa.

## Adapt plan (proposed, zone 🟡 chưa làm)
- `marketing-council` → merge vào promo-eval (thêm perspective)
- `copywriting`+`social` → skill `lusine-copy`
- `image` → `lusine-posm-gen` (SOP_030 template)
- `marketing-loops` → cron Agent Marketing Manager
- `referrals` → `lusine-loyalty`
