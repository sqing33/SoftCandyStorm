# Asset Candidate Review Packet

- Batch: `2026-05-26_mmx_level_up_feedback_pack`
- Candidate path: `asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack`
- Manifest: `asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/metadata/manifest.json`
- Metadata report: `harness/reports/2026-05-26_mmx_level_up_feedback_pack_metadata_001/summary.md`
- Review draft: `harness/asset_review/drafts/2026-05-26_mmx_level_up_feedback_pack_review_draft.json`
- Assets: 4
- Missing files: 0
- Missing review entries: 0

## Assets

| Asset | Type | QA | Review | Files |
|---|---|---|---|---:|
| `ui_level_up_spark_icon_v001_001` | `image` | `needs_visual_review` | `draft_todo` | 7 |
| `voice_level_up_cn_v001` | `speech` | `needs_listening_review` | `draft_todo` | 1 |
| `jingle_level_up_v001_source` | `music` | `repair_trim` | `draft_todo` | 1 |
| `jingle_level_up_v001_trim3s` | `music` | `needs_listening_review` | `draft_todo` | 3 |

## ui_level_up_spark_icon_v001_001

- Type: `image`
- QA status: `needs_visual_review`
- Review status: `draft_todo`
- Allowed candidate uses: `concept_reference`

### QA Notes

- 已生成透明 PNG 和 128/64/32 小尺寸预览。
- 需要人工确认是否有伪文字、水印、透明边缘残留和 32px 可读性问题。
- 当前只是升级反馈 UI 候选，不可直接接入 Runtime。

### Files

- `source_path` `exists`: [asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/images/ui_level_up_spark_icon_v001_001.jpg](asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/images/ui_level_up_spark_icon_v001_001.jpg)
- `processed_path` `exists`: [asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/processed/ui_level_up_v001_clean/ui_level_up_spark_icon_v001_001_clean.png](asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/processed/ui_level_up_v001_clean/ui_level_up_spark_icon_v001_001_clean.png)
- `runtime_32_path` `exists`: [asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/review_previews/ui_level_up_v001/runtime_32/ui_level_up_spark_icon_v001_001_clean_runtime_32.png](asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/review_previews/ui_level_up_v001/runtime_32/ui_level_up_spark_icon_v001_001_clean_runtime_32.png)
- `postprocess_manifest` `exists`: [asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/metadata/preview_ui_level_up_v001.json](asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/metadata/preview_ui_level_up_v001.json)
- `preview_paths` `exists`: [asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/review_previews/ui_level_up_v001/preview_128/ui_level_up_spark_icon_v001_001_clean_preview_128.png](asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/review_previews/ui_level_up_v001/preview_128/ui_level_up_spark_icon_v001_001_clean_preview_128.png)
- `preview_paths` `exists`: [asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/review_previews/ui_level_up_v001/preview_64/ui_level_up_spark_icon_v001_001_clean_preview_64.png](asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/review_previews/ui_level_up_v001/preview_64/ui_level_up_spark_icon_v001_001_clean_preview_64.png)
- `preview_paths` `exists`: [asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/review_previews/ui_level_up_v001/preview_32/ui_level_up_spark_icon_v001_001_clean_preview_32.png](asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/review_previews/ui_level_up_v001/preview_32/ui_level_up_spark_icon_v001_001_clean_preview_32.png)

## voice_level_up_cn_v001

- Type: `speech`
- QA status: `needs_listening_review`
- Review status: `draft_todo`
- Allowed candidate uses: `audio_candidate`

### QA Notes

- 需要人工确认中文发音、语气、响度和升级 UI 节奏。
- 3.49 秒可能偏长，若用于频繁升级提示可能需要短句或只保留首局教程。
- 接入前需要字幕、可关闭设置和与 jingle 的混音审查。

### Files

- `path` `exists`: [asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/audio/voice_level_up_cn_v001.mp3](asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/audio/voice_level_up_cn_v001.mp3)

## jingle_level_up_v001_source

- Type: `music`
- QA status: `repair_trim`
- Review status: `draft_todo`
- Allowed candidate uses: `audio_candidate`

### QA Notes

- 生成结果约 78.2 秒，长于 3 秒升级反馈目标。
- 原始长版本仅可作为音乐剪辑来源候选，不可直接接入升级事件。
- 已生成 3.2 秒剪辑候选 processed/audio_v001/jingle_level_up_v001_trim3s.mp3。

### Files

- `path` `exists`: [asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/music/jingle_level_up_v001_source.mp3](asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/music/jingle_level_up_v001_source.mp3)

## jingle_level_up_v001_trim3s

- Type: `music`
- QA status: `needs_listening_review`
- Review status: `draft_todo`
- Allowed candidate uses: `audio_candidate`

### QA Notes

- 长度符合短 UI jingle 候选目标。
- 仍需人工听感审查起落点、响度、可爱感和频繁触发疲劳。
- 正式接入前需要与升级暂停界面、TTS 和其他音效一起复核。

### Files

- `path` `exists`: [asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/processed/audio_v001/jingle_level_up_v001_trim3s.mp3](asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/processed/audio_v001/jingle_level_up_v001_trim3s.mp3)
- `source_path` `exists`: [asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/music/jingle_level_up_v001_source.mp3](asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/music/jingle_level_up_v001_source.mp3)
- `postprocess_manifest` `exists`: [asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/metadata/postprocess_audio_v001.json](asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/metadata/postprocess_audio_v001.json)

## Missing Files

- None

## Missing Review Entries

- None

## Limitations

- This packet organizes review evidence only.
- It does not validate human ratings, judge art/audio quality, promote Runtime candidates, or mark assets as accepted_content.
- TODO review fields must be filled by a human before manual review validation can pass.
