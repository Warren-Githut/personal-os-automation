# Source Ranking & Independence Audit (cho deep-research)

> Dùng ở Bước 2 (Width sweep) + Bước 3 (Contradiction). Giúp Bố không bị "ảo tưởng
> consensus" — 5 bài báo copy từ 1 press release chỉ tính = 1 nguồn.

## Tier uy tín (cao → thấp)
| Tier | Loại nguồn | Ví dụ | Weight |
|------|-----------|-------|--------|
| T1 | Academic peer-reviewed | Semantic Scholar, arXiv, PubMed, OpenAlex | 1.0 |
| T2 | Official / Gov / Report | WB, IMF, GSO VN, báo cáo ngành uy tín | 0.9 |
| T3 | News chính thống | Reuters, Bloomberg, VnExpress (tin sự kiện) | 0.6 |
| T4 | Blog / Opinion / Substack | cá nhân, không peer-review | 0.3 |
| T5 | Social / Forum | Reddit, FB, TikTok | 0.1 (chỉ làm context, KHÔNG cite) |

## Quality score (tùy chọn, cho premier profile)
```
quality_score = 0.4*tier + 0.3*utility + 0.2*citation_authority + 0.1*pagerank_centrality
```
- `tier`: từ bảng trên
- `utility`: nguồn trực tiếp trả lời atomic item của Bố đến mức nào (0–1)
- `citation_authority`: nguồn được nguồn khác trích dẫn nhiều (OpenAlex/Semantic Scholar)
- `pagerank_centrality`: độ kết nối trong corpus (dùng execute_code tính)

## Independence audit (QUAN TRỌNG)
- **Syndication ≠ consensus.** 5 bài báo reprint cùng 1 press release → **tính = 1 nguồn**.
- Cách làm: sau width sweep, cluster các URL theo `canonical_source` (domain gốc / tác giả gốc).
- Trong contradiction graph (bước 3): chỉ đếm weight của nguồn gốc, không đếm bản copy.
- Output: `independence.json` = {cluster_id, canonical_url, copies:[...], weight_used}

## Red flags — nguồn KHÔNG dùng để cite
- Không ghi tác giả / ngày / nguồn gốc
- Là quảng cáo ngụy trang bài báo
- Mâu thuẫn nội bộ (tự mâu thuẫn với chính nó)
- Bị retracted (rút lại) — check OpenAlex `retracted:true`

## Ví dụ
```
Query: "AI ảnh hưởng F&B VN"
Width sweep ra 8 kết quả:
- 3 bài từ VnExpress copy cùng 1 bản tin AFP → cluster A, weight 0.6 (không ×3)
- 2 paper arXiv về automation → T1, weight 1.0 ×2
- 1 blog cá nhân → T4, weight 0.3
- 2 forum → T5, KHÔNG cite
→ Corpus thực tế: 4 nguồn đếm (A, 2 paper, 1 blog), forum là context thôi.
```
