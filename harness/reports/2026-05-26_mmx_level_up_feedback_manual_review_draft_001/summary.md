# Asset Candidate Manual Review Validation

- Source: `harness/asset_review/drafts/2026-05-26_mmx_level_up_feedback_pack_review_draft.json`
- Decision: `asset_candidate_manual_review_invalid`
- Gate decision: `needs_more_review`
- Assets reviewed: 4 / 4
- Repair items: 4
- Global risks: 1

## Errors

- ui_level_up_spark_icon_v001_001: style_fit must be an integer from 1 to 5
- ui_level_up_spark_icon_v001_001: gameplay_readability must be an integer from 1 to 5
- ui_level_up_spark_icon_v001_001: provenance_confidence must be an integer from 1 to 5
- ui_level_up_spark_icon_v001_001: technical_readiness must be an integer from 1 to 5
- ui_level_up_spark_icon_v001_001: small_size_readability must be an integer from 1 to 5
- ui_level_up_spark_icon_v001_001: alpha_edge_quality must be an integer from 1 to 5
- voice_level_up_cn_v001: style_fit must be an integer from 1 to 5
- voice_level_up_cn_v001: gameplay_readability must be an integer from 1 to 5
- voice_level_up_cn_v001: provenance_confidence must be an integer from 1 to 5
- voice_level_up_cn_v001: technical_readiness must be an integer from 1 to 5
- voice_level_up_cn_v001: audio_clarity must be an integer from 1 to 5
- voice_level_up_cn_v001: loudness_readiness must be an integer from 1 to 5
- voice_level_up_cn_v001: duration_fit must be an integer from 1 to 5
- jingle_level_up_v001_source: style_fit must be an integer from 1 to 5
- jingle_level_up_v001_source: gameplay_readability must be an integer from 1 to 5
- jingle_level_up_v001_source: provenance_confidence must be an integer from 1 to 5
- jingle_level_up_v001_source: technical_readiness must be an integer from 1 to 5
- jingle_level_up_v001_source: audio_clarity must be an integer from 1 to 5
- jingle_level_up_v001_source: loudness_readiness must be an integer from 1 to 5
- jingle_level_up_v001_source: duration_fit must be an integer from 1 to 5
- jingle_level_up_v001_trim3s: style_fit must be an integer from 1 to 5
- jingle_level_up_v001_trim3s: gameplay_readability must be an integer from 1 to 5
- jingle_level_up_v001_trim3s: provenance_confidence must be an integer from 1 to 5
- jingle_level_up_v001_trim3s: technical_readiness must be an integer from 1 to 5
- jingle_level_up_v001_trim3s: audio_clarity must be an integer from 1 to 5
- jingle_level_up_v001_trim3s: loudness_readiness must be an integer from 1 to 5
- jingle_level_up_v001_trim3s: duration_fit must be an integer from 1 to 5

## Warnings

- None

## Limitations

- This validator checks manual review record completeness only.
- It cannot judge visual quality, listening quality, licensing, or in-engine feel.
- An asset_candidate decision does not promote assets into Runtime, accepted_content, or release assets.
