# 素材候选人工审查门禁

本目录用于记录 AI / `mmx` 素材候选的人工审查格式和校验工具。

适用对象：

- `asset/generated_candidates/<batch>/metadata/manifest.json`

基本流程：

1. 先运行 `tools/validate_asset_candidates.py`，确认候选批次 metadata、文件引用、prompt/source/postprocess provenance 和候选池标记有效。
2. 复制 `asset_candidate_manual_review_template.json`，填写审查人、时间、每个素材的评分、问题、允许用途和下一步。
3. 运行 `validate_asset_candidate_manual_review.py` 校验审查记录完整性。
4. 只有人工审查通过后，素材才可以作为后续 Runtime/UI 接入候选继续处理；这仍不等于进入正式素材或 `accepted_content`。

该门禁不会替代小尺寸实机预览、听感审查、响度处理、授权复核或 Runtime smoke。
