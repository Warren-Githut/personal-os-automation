---
name: writing-great-skills
description: Reference để viết/sửa Hermes skill cho predictability. Steal methodology từ mattpocock/skills (writing-great-skills, 182k★ MIT). User-invoked only.
disable-model-invocation: true
version: 1.0.0
trigger: Trước khi tạo skill mới / patch skill dài / review skill loạn / thấy skill bị sprawl hoặc premature-completion.
---

# Writing Great Skills (Warren-adapted)

> Steal từ `mattpocock/skills` (runtime-locked Claude Code plugin → chỉ lấy methodology, encode thành structural checklist để fit hy3:free).

## Root virtue: Predictability
Skill tồn tại để **bóc determinism ra từ hệ thống stochastic**. Predictability = agent chạy **cùng 1 process** mỗi lần — KHÔNG phải ra cùng 1 output. Mọi lever dưới phục vụ điều này.

## Information Hierarchy Ladder (đưa info xuống tầng nào)
1. **In-skill step** — action có thứ tự trong SKILL.md, tier chính. Mỗi step KẾT THÚC bằng 1 **completion criterion**: điều kiện nói "xong". Phải **checkable** (agent phân biệt xong/chưa?) + **exhaustive** ("mọi model đã xét" không phải "tạo list thay đổi"). Criterion mờ → agent **premature completion** (nghĩ "xong" khi chưa).
2. **In-skill reference** — định nghĩa/rule trong SKILL.md, tra when needed. Peer-set phẳng là OK.
3. **External reference** — đẩy ra file riêng, load qua **context pointer** khi cần (progressive disclosure). Giữ top legible.

→ Push quá ít xuống = top phình; push quá nhiều = hide material agent cần. **Progressive disclosure**: inline gì mọi branch cần, push Behind pointer gì chỉ 1 số branch cần.

## Leading Words
Từ compact đã nằm trong pretraining (vd: *lesson*, *fog of war*, *tracer bullet*). Lặp lại xuyên suốt → anchor cả vùng behaviour bằng ít token. Hunt để collapse 3 chỗ nói 1 ý → 1 token. Vd: "fast, deterministic, low-overhead" → *tight*.

## 6 Failure Modes (checklist review)
- **Premature completion** — kết thúc step trước khi xong. Fix: sharpen completion criterion trước; chỉ nếu mờ + thấy vội → split (hide post-completion steps).
- **Duplication** — 1 ý ở nhiều chỗ. Fix: collapse về 1 SSOT.
- **Sediment** — lớp stale tích tụ vì thêm an toàn/xóa nguy hiểm. Fix: kỷ luật prune.
- **Sprawl** — skill quá dài dù mỗi dòng sống. Fix: disclosure + split by branch/sequence.
- **No-op** — dòng model đã obey by default → trả tiền nói rỗng. Test: dòng có đổi behaviour vs default? Weak word ("be thorough") → stronger ("relentless").
- **Negation** — cấm = backfire (nói con voi → dễ nhớ hơn). Fix: state **positive** (hành vi đích), chỉ giữ prohibition làm **hard guardrail** khi không thể nói positive, và luôn pair với "làm gì thay thế".

## Invocation Tradeoff
- **Model-invoked**: có `description` → agent tự fire + skill khác reach được. Tốn **context load** (description nằm mỗi turn).
- **User-invoked**: `disable-model-invocation: true` → chỉ Bố gõ tên. Zero context load, nhưng tốn **cognitive load** (Bố phải nhớ tồn tại).
- Khi user-invoked nhiều quá → **router section** trong `using-agent-skills` (mục "Ask Hermes — Warren Router") đặt tên + khi nào route.

## Warren hard rules (KHÔNG đụng)
- ANCHORS/SOUL prohibition (raw/ READ-ONLY, v.v.) = hard guardrail → GIỮ nguyên, chỉ pair positive. KHÔNG sweep.
- Mọi skill mới = user-invoked nếu chỉ Bố gõ. Backup vào `vault/_archives/skills/` sau edit.
- **Reviewer-node gate bắt buộc trong mọi parser/data skill (2026-07-24, Bố approve):** Skill/parser có output dạng SỐ hoặc analysis từ data (Excel/CSV/PDF/vault) → workflow SKILL.md PHẢI có bước spawn `reviewer-node` (fresh context, qua `delegate_task`) trước khi báo Warren. KHÔNG chỉ dựa global `safenet` §D — phải GHI THẲNG vào SKILL.md để structural guarantee (ai đọc cũng thấy). Rule này sinh ra từ `stock-fill` (cũ `stock-pnl-ingest`) — từng quên embed critic → Bố bắt thêm Step 5.5. Pair với `verify-parser-output` cho parser.
