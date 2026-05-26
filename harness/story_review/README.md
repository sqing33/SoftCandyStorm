# 剧情图鉴人工审校门禁

本目录用于记录剧情 / 图鉴候选内容的人工审校格式和校验工具。

适用对象：

- `harness/generated_candidates/*/chapters/*.json`
- `harness/generated_candidates/*/codex/*.json`

基本流程：

1. 先运行 `tools/validate_story_codex_candidates.py`，确认 generated candidate 的结构、引用和基础文案护栏通过。
2. 复制 `story_codex_manual_review_template.json`，或用 `create_story_codex_review_draft.py` 从候选包生成覆盖所有章节和图鉴条目的 TODO 草稿。
3. 填写审校人、时间、每个章节和图鉴条目的评分、问题和下一步。
4. 运行 `validate_story_codex_manual_review.py` 校验审校记录完整性。
5. 只有人工审校通过后，未来 story/codex UI 才能把该批内容当作 UI 候选处理。
6. 如果人工审校结论为 `ui_candidate`，可运行 `promote_story_codex_ui_candidate.py` 复制到 `harness/story_review/ui_candidates/`，作为后续 Runtime UI 接入候选。

该门禁和 UI 候选晋级都不会把剧情或图鉴内容推进到 `accepted_content`，也不会替代未来 Runtime UI 验收。

草稿生成示例：

```bash
python3 harness/story_review/create_story_codex_review_draft.py \
  harness/generated_candidates/2026-05-26_story_codex_seed_pack \
  --repo-root . \
  --candidate-validation-report harness/reports/2026-05-26_story_codex_candidate_validation_001/summary.md \
  --out harness/story_review/drafts/2026-05-26_story_codex_seed_pack_review_draft.json
```

生成的草稿包含 `draft_notice` 和 `TODO` 占位，默认 `gate_decision` 为 `needs_more_review`。它只用于防止漏审，不能作为人工审校通过证据。

UI 候选晋级示例：

```bash
python3 harness/story_review/promote_story_codex_ui_candidate.py \
  harness/story_review/reviews/<review>.json \
  --repo-root . \
  --out-dir harness/story_review/ui_candidates \
  --report harness/reports/<report-id>/story_codex_ui_candidate.json \
  --markdown harness/reports/<report-id>/summary.md
```

晋级前必须先有真人填写并通过校验的 `ui_candidate` 审校记录；自动草稿、`needs_more_review` 或 `repair` 结论都不能晋级。
