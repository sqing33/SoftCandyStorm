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
7. 候选最终接受必须先用 `validate_content_final_acceptance.py` 校验真人 final acceptance 记录，再用 `validate_content_acceptance_manifest.py` 汇总 simulation candidate manifest、final acceptance 和 accepted content lockfile 三段证据。

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

v25 design review 状态检查示例：

```bash
python3 harness/content_review/check_v25_design_review_status.py --allow-incomplete
```

该检查器只确认 v25 草稿是否存在、是否仍含 TODO / 占位符、`source_patch_manifest` 中的新增内容是否都有审查条目。它不替代
`validate_content_candidate_design_review.py`，也不推进候选。

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

## 最终接受证据包

候选内容进入 `accepted_content` 前，还应先生成最终接受证据包，确认所有必需证据都已存在且没有把 generated candidate 直接放行：

```bash
python3 harness/content_review/create_content_acceptance_review_packet.py \
  harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack \
  --repo-root . \
  --report harness/reports/2026-05-26_phase4_content_acceptance_review_packet_001/content_acceptance_review_packet.json \
  --markdown harness/reports/2026-05-26_phase4_content_acceptance_review_packet_001/summary.md
```

该证据包会串联完整候选包预检、静态预算、人工设计审查、设计审查包、Demo readiness、9 局人工试玩草稿和 accepted content lockfile。当前 Phase 4 报告结论为 `content_acceptance_review_packet_needs_evidence`，因为设计审查与人工试玩仍含 `TODO`，`demo_readiness` 仍是 `demo_not_ready`，accepted content lockfile 仍是 `accepted_content_lockfile_blocked`。

最终接受证据包只负责防漏和交接；它不验证真人审查、不运行 Harness 仿真、不复制候选、不写 `accepted_content`，也不批准发布。

Final content acceptance 校验示例：

```bash
python3 harness/content_review/validate_content_final_acceptance.py \
  harness/content_review/final_acceptance/<review>.json \
  --repo-root . \
  --report harness/reports/<report-id>/content_final_acceptance.json \
  --markdown harness/reports/<report-id>/summary.md
```

模板 `content_final_acceptance_template.json` 保留 TODO、占位 simulation candidate manifest 和占位 accepted content lockfile 报告路径，当前报告应为 `content_final_acceptance_invalid`。它只接受已通过 simulation-candidate staging 且 accepted content lockfile 报告为 `accepted_content_lockfile_valid` 的候选，并继续要求 `release_ready=false`、`runtime_integrated=false`。

Content acceptance manifest 校验示例：

```bash
python3 harness/content_review/validate_content_acceptance_manifest.py \
  harness/content_review/accepted/<candidate>/acceptance_manifest.json \
  --repo-root . \
  --report harness/reports/<report-id>/content_acceptance_manifest.json \
  --markdown harness/reports/<report-id>/summary.md
```

模板 `content_acceptance_manifest_template.json` 保留 TODO 和占位证据路径，当前报告应为 `content_acceptance_manifest_invalid`。它要求绑定有效 simulation candidate manifest、已通过 final human acceptance 和有效 accepted content lockfile；即使将来报告有效，也只说明内容包可以作为 accepted content 证据，不代表 Runtime 已集成、发布包 ready 或可以跳过 RC / 隐私 / 打包门禁。
