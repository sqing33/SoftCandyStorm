# Asset Final Acceptance Validation

- Source: `harness/asset_review/asset_final_acceptance_template.json`
- Decision: `asset_final_acceptance_invalid`
- Candidate batch: `TODO: asset candidate batch id`
- Gate decision: `needs_more_review`
- Runtime preview review: `None`
- Audio loudness review: `None`
- Observations: 2
- Unresolved issues: 1

## Errors

- candidate_batch_id must not contain TODO or placeholder markers
- reviewer must not contain TODO or placeholder markers
- summary must not contain TODO or placeholder markers
- checks.accepts_asset_batch must be true
- checks.accepted_content_only_after_reviews must be true
- concrete_observations must not contain TODO or placeholder markers
- unresolved_issues must not contain TODO or placeholder markers
- runtime_preview_review_file must not contain TODO or placeholder markers
- audio_loudness_review_file must not contain TODO or placeholder markers
- source_runtime_candidate_manifest must not contain TODO or placeholder markers

## Warnings

- None

## Limitations

- This validator checks final asset acceptance record completeness only.
- It does not copy assets, integrate Runtime content, or approve release readiness.
- Accepted assets still need package, privacy, playtest, and Runtime smoke gates before release.
