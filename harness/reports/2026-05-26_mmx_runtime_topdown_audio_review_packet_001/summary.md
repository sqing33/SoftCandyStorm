# Asset Candidate Review Packet

- Batch: `2026-05-26_mmx_runtime_topdown_audio_plan`
- Candidate path: `asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan`
- Manifest: `asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/metadata/manifest.json`
- Metadata report: `harness/reports/2026-05-26_mmx_runtime_topdown_audio_plan_metadata_001/summary.md`
- Review draft: `harness/asset_review/drafts/2026-05-26_mmx_runtime_topdown_audio_plan_review_draft.json`
- Assets: 6
- Missing files: 0
- Missing review entries: 0

## Assets

| Asset | Type | QA | Review | Files |
|---|---|---|---|---:|
| `player_jar_keeper_topdown_v005_001` | `image` | `needs_visual_review` | `draft_todo` | 7 |
| `player_jar_keeper_topdown_v005_002` | `image` | `repair_review` | `draft_todo` | 7 |
| `voice_boss_arrival_cn_v002` | `speech` | `needs_listening_review` | `draft_todo` | 1 |
| `sting_boss_arrival_v002_source` | `music` | `repair_trim` | `draft_todo` | 1 |
| `sting_boss_arrival_v002_trim8s` | `music` | `needs_listening_review` | `draft_todo` | 3 |
| `boss_arrival_voice_sting_mix_v001` | `music` | `needs_listening_review` | `draft_todo` | 3 |

## player_jar_keeper_topdown_v005_001

- Type: `image`
- QA status: `needs_visual_review`
- Review status: `draft_todo`
- Allowed candidate uses: `concept_reference`

### QA Notes

- 已生成透明 PNG 和 128/64/32 小尺寸预览。
- 需要人工确认是否真正符合严格俯视角。
- 需要检查边缘透明、伪文字、水印和 32px 可读性。

### Files

- `source_path` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/images/player_jar_keeper_topdown_v005_001.jpg](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/images/player_jar_keeper_topdown_v005_001.jpg)
- `processed_path` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/processed/topdown_v005_clean/player_jar_keeper_topdown_v005_001_clean.png](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/processed/topdown_v005_clean/player_jar_keeper_topdown_v005_001_clean.png)
- `runtime_32_path` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/review_previews/topdown_v005/runtime_32/player_jar_keeper_topdown_v005_001_clean_runtime_32.png](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/review_previews/topdown_v005/runtime_32/player_jar_keeper_topdown_v005_001_clean_runtime_32.png)
- `postprocess_manifest` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/metadata/preview_topdown_v005.json](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/metadata/preview_topdown_v005.json)
- `preview_paths` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/review_previews/topdown_v005/preview_128/player_jar_keeper_topdown_v005_001_clean_preview_128.png](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/review_previews/topdown_v005/preview_128/player_jar_keeper_topdown_v005_001_clean_preview_128.png)
- `preview_paths` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/review_previews/topdown_v005/preview_64/player_jar_keeper_topdown_v005_001_clean_preview_64.png](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/review_previews/topdown_v005/preview_64/player_jar_keeper_topdown_v005_001_clean_preview_64.png)
- `preview_paths` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/review_previews/topdown_v005/preview_32/player_jar_keeper_topdown_v005_001_clean_preview_32.png](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/review_previews/topdown_v005/preview_32/player_jar_keeper_topdown_v005_001_clean_preview_32.png)

## player_jar_keeper_topdown_v005_002

- Type: `image`
- QA status: `repair_review`
- Review status: `draft_todo`
- Allowed candidate uses: `concept_reference`

### QA Notes

- component cleanup 保留最大组件，移除了 1px 离散组件。
- 需要人工确认是否裁掉有效边缘元素。
- 需要人工确认 32px 下角色身份和糖罐主题是否清晰。

### Files

- `source_path` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/images/player_jar_keeper_topdown_v005_002.jpg](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/images/player_jar_keeper_topdown_v005_002.jpg)
- `processed_path` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/processed/topdown_v005_clean/player_jar_keeper_topdown_v005_002_clean.png](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/processed/topdown_v005_clean/player_jar_keeper_topdown_v005_002_clean.png)
- `runtime_32_path` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/review_previews/topdown_v005/runtime_32/player_jar_keeper_topdown_v005_002_clean_runtime_32.png](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/review_previews/topdown_v005/runtime_32/player_jar_keeper_topdown_v005_002_clean_runtime_32.png)
- `postprocess_manifest` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/metadata/preview_topdown_v005.json](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/metadata/preview_topdown_v005.json)
- `preview_paths` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/review_previews/topdown_v005/preview_128/player_jar_keeper_topdown_v005_002_clean_preview_128.png](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/review_previews/topdown_v005/preview_128/player_jar_keeper_topdown_v005_002_clean_preview_128.png)
- `preview_paths` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/review_previews/topdown_v005/preview_64/player_jar_keeper_topdown_v005_002_clean_preview_64.png](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/review_previews/topdown_v005/preview_64/player_jar_keeper_topdown_v005_002_clean_preview_64.png)
- `preview_paths` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/review_previews/topdown_v005/preview_32/player_jar_keeper_topdown_v005_002_clean_preview_32.png](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/review_previews/topdown_v005/preview_32/player_jar_keeper_topdown_v005_002_clean_preview_32.png)

## voice_boss_arrival_cn_v002

- Type: `speech`
- QA status: `needs_listening_review`
- Review status: `draft_todo`
- Allowed candidate uses: `audio_candidate`

### QA Notes

- 计划声线 Chinese_female_news_anchor 不存在，实际使用 Chinese (Mandarin)_News_Anchor。
- 需要人工确认中文发音、语气、响度和战斗音效上方可读性。
- 接入前需要字幕/无障碍替代和可关闭设置。

### Files

- `path` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/audio/voice_boss_arrival_cn_v002.mp3](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/audio/voice_boss_arrival_cn_v002.mp3)

## sting_boss_arrival_v002_source

- Type: `music`
- QA status: `repair_trim`
- Review status: `draft_todo`
- Allowed candidate uses: `audio_candidate`

### QA Notes

- 生成结果约 72.9 秒，长于 8 秒 Boss 出场 sting 目标。
- 原始长版本仅可作为音乐剪辑来源候选，不可直接接入 Boss 出场事件。
- 已生成 8 秒剪辑候选 processed/audio_v002/sting_boss_arrival_v002_trim8s.mp3。

### Files

- `path` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/music/sting_boss_arrival_v002_source.mp3](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/music/sting_boss_arrival_v002_source.mp3)

## sting_boss_arrival_v002_trim8s

- Type: `music`
- QA status: `needs_listening_review`
- Review status: `draft_todo`
- Allowed candidate uses: `audio_candidate`

### QA Notes

- 长度符合 6-10 秒 Boss 出场 sting 目标。
- 仍需人工听感审查起落点、可爱紧张感、结尾和与 Boss 语音叠放效果。
- 正式接入前需要响度统一和触发频率检查。

### Files

- `path` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/processed/audio_v002/sting_boss_arrival_v002_trim8s.mp3](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/processed/audio_v002/sting_boss_arrival_v002_trim8s.mp3)
- `source_path` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/music/sting_boss_arrival_v002_source.mp3](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/music/sting_boss_arrival_v002_source.mp3)
- `postprocess_manifest` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/metadata/postprocess_audio_v002.json](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/metadata/postprocess_audio_v002.json)

## boss_arrival_voice_sting_mix_v001

- Type: `music`
- QA status: `needs_listening_review`
- Review status: `draft_todo`
- Allowed candidate uses: `audio_candidate`

### QA Notes

- 该文件是 Boss 语音叠放 8 秒 sting 的听感预览，不替代单独语音或音乐源。
- loudnorm 探测值已记录，但不能证明听感通过。
- 仍需人工确认语音清晰度、音乐遮挡、ducking 需求、字幕时序和可关闭设置。

### Files

- `path` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/processed/audio_mix_v001/boss_arrival_voice_sting_mix_v001.mp3](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/processed/audio_mix_v001/boss_arrival_voice_sting_mix_v001.mp3)
- `source_path` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/processed/audio_v002/sting_boss_arrival_v002_trim8s.mp3](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/processed/audio_v002/sting_boss_arrival_v002_trim8s.mp3)
- `postprocess_manifest` `exists`: [asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/metadata/audio_mix_v001.json](asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/metadata/audio_mix_v001.json)

## Missing Files

- None

## Missing Review Entries

- None

## Limitations

- This packet organizes review evidence only.
- It does not validate human ratings, judge art/audio quality, promote Runtime candidates, or mark assets as accepted_content.
- TODO review fields must be filled by a human before manual review validation can pass.
