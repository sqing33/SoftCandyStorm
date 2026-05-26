# Asset Runtime Preview Review Validation

- Source: `harness/asset_review/asset_runtime_preview_review_template.json`
- Decision: `asset_runtime_preview_review_invalid`
- Candidate batch: `TODO: asset candidate batch id`
- Gate decision: `needs_more_review`
- Runtime candidate manifest: `None`
- Observations: 2
- Unresolved issues: 1

## Errors

- candidate_batch_id must not contain TODO or placeholder markers
- reviewer must not contain TODO or placeholder markers
- summary must not contain TODO or placeholder markers
- checks.all_assets_visible_or_audible must be true
- checks.small_size_readable must be true
- checks.no_placeholder_leak must be true
- checks.no_runtime_integration_claim must be true
- concrete_observations must not contain TODO or placeholder markers
- unresolved_issues must not contain TODO or placeholder markers
- source_runtime_candidate_manifest must not contain TODO or placeholder markers

## Warnings

- None

## Limitations

- This validator checks human Runtime preview review record completeness only.
- It does not load asset files, inspect pixels or waveforms, integrate Runtime content, or approve final acceptance.
- A valid Runtime preview review is not release readiness and cannot bypass audio or final human acceptance.
