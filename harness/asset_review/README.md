# 素材候选人工审查门禁

本目录用于记录 AI / `mmx` 素材候选的人工审查格式和校验工具。

适用对象：

- `asset/generated_candidates/<batch>/metadata/manifest.json`

基本流程：

1. 新 `mmx` 批次生成前先运行 `validate_mmx_asset_generation_plan.py`，确认计划中的命令、输出路径和后续审查链路都只指向候选目录。
2. 生成和后处理完成后运行 `tools/validate_asset_candidates.py`，确认候选批次 metadata、文件引用、prompt/source/postprocess provenance 和候选池标记有效。
3. 可以复制 `asset_candidate_manual_review_template.json` 手工填写，也可以用 `create_asset_candidate_review_draft.py` 从候选 manifest 生成覆盖所有素材 id 的草稿。
4. 可以运行 `create_asset_review_packet.py` 把候选 manifest、metadata 报告和人工审查草稿整理成 Markdown 审查包，方便真人逐项打开文件和填写评分。
5. 真人审查人必须替换草稿中的 `TODO` 占位，填写审查人、时间、每个素材的评分、问题、允许用途和下一步。
6. 运行 `validate_asset_candidate_manual_review.py` 校验审查记录完整性。
7. 只有人工审查通过且 `gate_decision=asset_candidate` 后，才可以运行 `promote_asset_runtime_candidate.py` 复制到 `harness/asset_review/runtime_candidates/`，作为后续 Runtime/UI 接入候选继续处理；这仍不等于进入正式素材或 `accepted_content`。
8. 对生成的 `runtime_candidate_manifest.json` 继续运行 `validate_asset_runtime_candidate_manifest.py`，确认它仍绑定有效人工审查、候选 metadata 报告、源候选 manifest、文件路径和候选池规则。
9. Runtime 候选必须分别填写并通过 `asset_runtime_preview_review_template.json`、`asset_audio_loudness_review_template.json` 和 `asset_final_acceptance_template.json`，对应校验器分别为 `validate_asset_runtime_preview_review.py`、`validate_asset_audio_loudness_review.py` 和 `validate_asset_final_acceptance.py`。
10. 可以运行 `create_asset_acceptance_review_packet.py` 汇总最终接受 manifest 需要的 Runtime candidate manifest、Runtime preview review、音频响度 / 听感审查和 final human acceptance 证据，帮助真人补齐缺口。
11. Runtime 候选通过 Runtime preview、音频响度 / 听感审查和 final human acceptance 后，才可以写入 `asset_acceptance_manifest_template.json` 对应的最终接受 manifest，并运行 `validate_asset_acceptance_manifest.py`。

mmx 生成计划示例：

```bash
python3 harness/asset_review/validate_mmx_asset_generation_plan.py \
  harness/asset_review/mmx_asset_generation_plan_template.json \
  --repo-root . \
  --report harness/reports/<report-id>/mmx_asset_generation_plan.json \
  --markdown harness/reports/<report-id>/summary.md
```

该计划校验不会调用 `mmx`，只证明作业准备遵守候选池、命令 provenance 和人工审查纪律。

生成审查草稿示例：

```bash
python3 harness/asset_review/create_asset_candidate_review_draft.py \
  asset/generated_candidates/<batch> \
  --repo-root . \
  --metadata-report harness/reports/<asset-validation-report>/summary.md \
  --out harness/asset_review/drafts/<batch>_review_draft.json
```

生成审查包示例：

```bash
python3 harness/asset_review/create_asset_review_packet.py \
  asset/generated_candidates/<batch> \
  --repo-root . \
  --metadata-report harness/reports/<asset-validation-report>/summary.md \
  --review-draft harness/asset_review/drafts/<batch>_review_draft.json \
  --out harness/reports/<report-id>/summary.md
```

审查包只是把 manifest、文件链接、QA 状态和草稿 TODO 集中到一个 Markdown 文件，方便真人审查；它不校验人工评分，不判断美术 / 听感质量，也不能作为通过证据。

Runtime 候选晋级示例：

```bash
python3 harness/asset_review/promote_asset_runtime_candidate.py \
  harness/asset_review/reviews/<review>.json \
  --repo-root . \
  --out-dir harness/asset_review/runtime_candidates \
  --report harness/reports/<report-id>/asset_runtime_candidate.json \
  --markdown harness/reports/<report-id>/summary.md
```

Runtime 候选 manifest 校验示例：

```bash
python3 harness/asset_review/validate_asset_runtime_candidate_manifest.py \
  harness/asset_review/runtime_candidates/<batch>/runtime_candidate_manifest.json \
  --repo-root . \
  --report harness/reports/<report-id>/asset_runtime_candidate_manifest.json \
  --markdown harness/reports/<report-id>/summary.md
```

晋级前必须先有真人填写并通过校验的 `asset_candidate` 审查记录；自动草稿、`needs_more_review`、`repair` 或 `reject` 结论都不能晋级。该门禁和 Runtime 候选晋级都不会替代小尺寸实机预览、听感审查、响度处理、授权复核或 Runtime smoke。

Runtime preview review 校验示例：

```bash
python3 harness/asset_review/validate_asset_runtime_preview_review.py \
  harness/asset_review/runtime_preview_reviews/<review>.json \
  --repo-root . \
  --report harness/reports/<report-id>/asset_runtime_preview_review.json \
  --markdown harness/reports/<report-id>/summary.md
```

音频响度 / 听感审查校验示例：

```bash
python3 harness/asset_review/validate_asset_audio_loudness_review.py \
  harness/asset_review/audio_loudness_reviews/<review>.json \
  --repo-root . \
  --report harness/reports/<report-id>/asset_audio_loudness_review.json \
  --markdown harness/reports/<report-id>/summary.md
```

最终人工接受记录校验示例：

```bash
python3 harness/asset_review/validate_asset_final_acceptance.py \
  harness/asset_review/final_acceptance/<review>.json \
  --repo-root . \
  --report harness/reports/<report-id>/asset_final_acceptance.json \
  --markdown harness/reports/<report-id>/summary.md
```

三个模板当前都保留 TODO 和占位路径，报告必须分别保持 `asset_runtime_preview_review_invalid`、`asset_audio_loudness_review_invalid` 和 `asset_final_acceptance_invalid`，直到真人填写并绑定有效 Runtime 候选证据。即使三者通过，也仍只说明最终接受证据完整，不代表 Runtime 已集成或发布包 ready。

最终接受审查包示例：

```bash
python3 harness/asset_review/create_asset_acceptance_review_packet.py \
  harness/asset_review/accepted/<batch>/acceptance_manifest.json \
  --repo-root . \
  --report harness/reports/<report-id>/asset_acceptance_review_packet.json \
  --markdown harness/reports/<report-id>/summary.md
```

审查包只列出最终接受证据状态、预期 review type / decision 和必填检查项；它不会验证通过，不会复制素材，不会接入 Runtime，也不会批准发布。

最终接受 manifest 校验示例：

```bash
python3 harness/asset_review/validate_asset_acceptance_manifest.py \
  harness/asset_review/accepted/<batch>/acceptance_manifest.json \
  --repo-root . \
  --report harness/reports/<report-id>/asset_acceptance_manifest.json \
  --markdown harness/reports/<report-id>/summary.md
```

模板 `asset_acceptance_manifest_template.json` 保留 TODO、Runtime preview review、audio loudness review 和 final acceptance 占位路径，当前报告应为 `asset_acceptance_manifest_invalid`。它要求绑定有效 Runtime candidate manifest、Runtime preview review、音频响度 / 听感审查和最终人工接受记录；即使将来报告有效，也只说明素材内容可以进入 accepted asset 内容池，仍不代表 Runtime 已集成、发布包 ready 或可以跳过试玩 / 隐私 / 打包门禁。
