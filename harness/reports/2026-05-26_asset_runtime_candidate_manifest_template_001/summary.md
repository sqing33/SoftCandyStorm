# Asset Runtime Candidate Manifest Validation

- Source: `harness/asset_review/asset_runtime_candidate_manifest_template.json`
- Decision: `asset_runtime_candidate_manifest_invalid`
- Candidate batch: `TODO: asset candidate batch id`
- Assets: 1 / 1
- Manual review: `None` / `None`

## Errors

- candidate_batch_id must not contain TODO or placeholder markers
- promoted_at must not contain TODO or placeholder markers
- source_candidate_batch must not contain TODO or placeholder markers
- manual_review_file must not contain TODO or placeholder markers
- candidate_metadata_report must not contain TODO or placeholder markers
- TODO: asset id from manifest: id must not contain TODO or placeholder markers
- TODO: asset id from manifest: path must not contain TODO or placeholder markers
- TODO: asset id from manifest path does not exist: images/TODO.png

## Warnings

- None

## Limitations

- This validator checks Runtime candidate manifest completeness only.
- A valid asset Runtime candidate manifest does not promote assets into accepted_content.
- A valid asset Runtime candidate manifest does not prove Runtime integration, listening quality, licensing, or release readiness.
