# Asset Acceptance Review Packet

- Source: `harness/asset_review/asset_acceptance_manifest_template.json`
- Decision: `asset_acceptance_review_packet_needs_evidence`
- Candidate batch: `TODO: asset candidate batch id`
- Assets: 1 / 1
- Evidence files: 0 / 4
- Placeholder evidence: 4
- Missing evidence: 0

## Required Evidence

| Field | Status | Expected | Required checks |
|---|---|---|---|
| `source_runtime_candidate_manifest` | `placeholder` | `asset_runtime_candidate_manifest_valid` | None |
| `runtime_preview_review_file` | `placeholder` | `asset_runtime_preview_review / runtime_preview_pass` | `all_assets_visible_or_audible`, `small_size_readable`, `no_placeholder_leak`, `no_runtime_integration_claim` |
| `audio_loudness_review_file` | `placeholder` | `asset_audio_loudness_review / audio_loudness_pass` | `dialogue_clear_if_present`, `loudness_review_passed`, `no_clipping`, `loop_or_duration_fit` |
| `final_human_acceptance_file` | `placeholder` | `asset_final_acceptance / accepted_content` | `accepts_asset_batch`, `accepted_content_only_after_reviews`, `release_ready`, `runtime_integrated` |

## Evidence Paths

- `source_runtime_candidate_manifest`: `harness/asset_review/runtime_candidates/<batch>/runtime_candidate_manifest.json` -> `None`
- `runtime_preview_review_file`: `harness/asset_review/runtime_preview_reviews/<human-runtime-preview-review>.json` -> `None`
- `audio_loudness_review_file`: `harness/asset_review/audio_loudness_reviews/<human-audio-loudness-review>.json` -> `None`
- `final_human_acceptance_file`: `harness/asset_review/final_acceptance/<human-final-acceptance>.json` -> `None`

## Accepted Assets

| Asset | Type | Use | Source | Status |
|---|---|---|---|---|
| `TODO: asset id from Runtime candidate manifest` | `image` | `runtime_asset` | `images/TODO.png` | `placeholder` |

## Required Next Steps

- Fill or replace Runtime preview review evidence with concrete human observations.
- Fill or replace audio loudness/listening review evidence with concrete listening and clipping/loudness observations.
- Fill or replace final human acceptance evidence after prior reviews pass.
- Run harness/asset_review/validate_asset_acceptance_manifest.py after every TODO is removed.

## Limitations

- This packet organizes final asset acceptance evidence only.
- It does not validate the acceptance manifest as passing.
- It does not copy assets into Runtime, mark Runtime integration, or approve release readiness.
