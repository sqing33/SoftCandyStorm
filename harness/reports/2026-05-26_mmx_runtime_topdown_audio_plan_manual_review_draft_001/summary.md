# Asset Candidate Manual Review Validation

- Source: `harness/asset_review/drafts/2026-05-26_mmx_runtime_topdown_audio_plan_review_draft.json`
- Decision: `asset_candidate_manual_review_invalid`
- Gate decision: `needs_more_review`
- Assets reviewed: 5 / 5
- Repair items: 5
- Global risks: 1

## Errors

- player_jar_keeper_topdown_v005_001: style_fit must be an integer from 1 to 5
- player_jar_keeper_topdown_v005_001: gameplay_readability must be an integer from 1 to 5
- player_jar_keeper_topdown_v005_001: provenance_confidence must be an integer from 1 to 5
- player_jar_keeper_topdown_v005_001: technical_readiness must be an integer from 1 to 5
- player_jar_keeper_topdown_v005_001: small_size_readability must be an integer from 1 to 5
- player_jar_keeper_topdown_v005_001: alpha_edge_quality must be an integer from 1 to 5
- player_jar_keeper_topdown_v005_002: style_fit must be an integer from 1 to 5
- player_jar_keeper_topdown_v005_002: gameplay_readability must be an integer from 1 to 5
- player_jar_keeper_topdown_v005_002: provenance_confidence must be an integer from 1 to 5
- player_jar_keeper_topdown_v005_002: technical_readiness must be an integer from 1 to 5
- player_jar_keeper_topdown_v005_002: small_size_readability must be an integer from 1 to 5
- player_jar_keeper_topdown_v005_002: alpha_edge_quality must be an integer from 1 to 5
- voice_boss_arrival_cn_v002: style_fit must be an integer from 1 to 5
- voice_boss_arrival_cn_v002: gameplay_readability must be an integer from 1 to 5
- voice_boss_arrival_cn_v002: provenance_confidence must be an integer from 1 to 5
- voice_boss_arrival_cn_v002: technical_readiness must be an integer from 1 to 5
- voice_boss_arrival_cn_v002: audio_clarity must be an integer from 1 to 5
- voice_boss_arrival_cn_v002: loudness_readiness must be an integer from 1 to 5
- voice_boss_arrival_cn_v002: duration_fit must be an integer from 1 to 5
- sting_boss_arrival_v002_source: style_fit must be an integer from 1 to 5
- sting_boss_arrival_v002_source: gameplay_readability must be an integer from 1 to 5
- sting_boss_arrival_v002_source: provenance_confidence must be an integer from 1 to 5
- sting_boss_arrival_v002_source: technical_readiness must be an integer from 1 to 5
- sting_boss_arrival_v002_source: audio_clarity must be an integer from 1 to 5
- sting_boss_arrival_v002_source: loudness_readiness must be an integer from 1 to 5
- sting_boss_arrival_v002_source: duration_fit must be an integer from 1 to 5
- sting_boss_arrival_v002_trim8s: style_fit must be an integer from 1 to 5
- sting_boss_arrival_v002_trim8s: gameplay_readability must be an integer from 1 to 5
- sting_boss_arrival_v002_trim8s: provenance_confidence must be an integer from 1 to 5
- sting_boss_arrival_v002_trim8s: technical_readiness must be an integer from 1 to 5
- sting_boss_arrival_v002_trim8s: audio_clarity must be an integer from 1 to 5
- sting_boss_arrival_v002_trim8s: loudness_readiness must be an integer from 1 to 5
- sting_boss_arrival_v002_trim8s: duration_fit must be an integer from 1 to 5

## Warnings

- None

## Limitations

- This validator checks manual review record completeness only.
- It cannot judge visual quality, listening quality, licensing, or in-engine feel.
- An asset_candidate decision does not promote assets into Runtime, accepted_content, or release assets.
