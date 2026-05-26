# Asset Audio Loudness Review Validation

- Source: `harness/asset_review/asset_audio_loudness_review_template.json`
- Decision: `asset_audio_loudness_review_invalid`
- Candidate batch: `TODO: asset candidate batch id`
- Gate decision: `needs_more_review`
- Runtime candidate manifest: `None`
- Observations: 2
- Unresolved issues: 1

## Errors

- candidate_batch_id must not contain TODO or placeholder markers
- reviewer must not contain TODO or placeholder markers
- summary must not contain TODO or placeholder markers
- checks.dialogue_clear_if_present must be true
- checks.loudness_review_passed must be true
- checks.no_clipping must be true
- checks.loop_or_duration_fit must be true
- concrete_observations must not contain TODO or placeholder markers
- unresolved_issues must not contain TODO or placeholder markers
- source_runtime_candidate_manifest must not contain TODO or placeholder markers

## Warnings

- None

## Limitations

- This validator checks human audio loudness/listening review record completeness only.
- It does not inspect waveforms, normalize files, integrate Runtime audio, or approve final acceptance.
- A valid audio loudness review is not release readiness and cannot bypass Runtime preview or final human acceptance.
