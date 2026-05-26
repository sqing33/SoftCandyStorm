# 剧情图鉴人工审校门禁

本目录用于记录剧情 / 图鉴候选内容的人工审校格式和校验工具。

适用对象：

- `harness/generated_candidates/*/chapters/*.json`
- `harness/generated_candidates/*/codex/*.json`

基本流程：

1. 先运行 `tools/validate_story_codex_candidates.py`，确认 generated candidate 的结构、引用和基础文案护栏通过。
2. 复制 `story_codex_manual_review_template.json`，填写审校人、时间、每个章节和图鉴条目的评分、问题和下一步。
3. 运行 `validate_story_codex_manual_review.py` 校验审校记录完整性。
4. 只有人工审校通过后，未来 story/codex UI 才能把该批内容当作 UI 候选处理。

该门禁不会把剧情或图鉴内容推进到 `accepted_content`，也不会替代未来 Runtime UI 验收。
