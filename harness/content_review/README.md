# 内容候选设计人工审查门禁

本目录用于记录 AI 内容候选在进入仿真、试玩或最终接受前的人工设计审查格式和校验工具。

适用对象：

- `harness/generated_candidates/<full-pack>/metadata/manifest.json`
- `harness/generated_candidates/<full-pack>/metadata/source_patch_manifest.json`

基本流程：

1. 先运行 `tools/validate_materialized_content_pack.py`，确认完整候选包仍是 generated candidate，且内容计数和引用关系可预检。
2. 可以复制 `content_candidate_design_review_template.json` 手工填写，也可以用 `create_content_candidate_design_review_draft.py` 从候选包生成覆盖新增候选 id 的草稿。
3. 真人审查人必须替换草稿中的 `TODO` 占位，填写每个新增内容的主题差异、流派潜力、反制可读性、美术 / 音效可读性和下一步。
4. 运行 `validate_content_candidate_design_review.py` 校验审查记录完整性。
5. 只有人工设计审查通过且 `gate_decision=simulate_candidate` 后，候选才可以进入后续仿真或人工试玩候选流程；这仍不等于进入 `accepted_content`。
6. 若需要记录“设计审查通过、等待正式 Harness 仿真”的 staging，可运行 `promote_content_simulation_candidate.py` 并继续用 `validate_content_simulation_candidate_manifest.py` 校验生成的 `simulation_candidate_manifest.json`。

生成审查草稿示例：

```bash
python3 harness/content_review/create_content_candidate_design_review_draft.py \
  harness/generated_candidates/<full-pack> \
  --repo-root . \
  --preflight-report harness/reports/<preflight-report>/summary.md \
  --out harness/content_review/drafts/<full-pack>_design_review_draft.json
```

生成审查包示例：

```bash
python3 harness/content_review/create_content_candidate_review_packet.py \
  harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack \
  --repo-root . \
  --preflight-report harness/reports/2026-05-26_phase4_roster_full_pack_preflight_001/summary.md \
  --review-draft harness/content_review/drafts/2026-05-26_phase4_roster_gap_full_pack_design_review_draft.json \
  --out harness/reports/2026-05-26_phase4_roster_content_review_packet_001/summary.md
```

审查包会汇总 `source_patch_manifest.contents`、候选文件摘要、预检报告、TODO 审查草稿状态、平衡风险和门禁关注点，方便真人逐项审查。它不填写评分、不校验人工结论、不运行 Schema / 预算 / 仿真，也不晋级候选。

校验示例：

```bash
python3 harness/content_review/validate_content_candidate_design_review.py \
  harness/content_review/reviews/<review>.json \
  --repo-root . \
  --report harness/reports/<report-id>/content_design_review.json \
  --markdown harness/reports/<report-id>/summary.md
```

该门禁不会替代 Schema、静态预算、Bot 仿真、Replay 回归、人工试玩或 accepted content 锁定。

Simulation candidate staging 示例：

```bash
python3 harness/content_review/promote_content_simulation_candidate.py \
  harness/content_review/reviews/<review>.json \
  --repo-root . \
  --out-dir harness/content_review/simulation_candidates \
  --report harness/reports/<report-id>/content_simulation_candidate.json \
  --markdown harness/reports/<report-id>/summary.md

python3 harness/content_review/validate_content_simulation_candidate_manifest.py \
  harness/content_review/simulation_candidates/<full-pack>/simulation_candidate_manifest.json \
  --repo-root . \
  --report harness/reports/<report-id>/content_simulation_candidate_manifest.json \
  --markdown harness/reports/<report-id>/summary.md
```

该 staging 只说明人工设计审查允许进入后续仿真候选；它不会写入 `validated_candidates`、`simulated_candidates`、`playtest_candidates`、`accepted_content` 或 Runtime。
