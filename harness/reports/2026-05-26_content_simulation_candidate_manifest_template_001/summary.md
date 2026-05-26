# Content Simulation Candidate Manifest Validation

- Source: `harness/content_review/content_simulation_candidate_manifest_template.json`
- Decision: `content_simulation_candidate_manifest_invalid`
- Candidate: `TODO: full content candidate pack id`
- Contents: 1 / 1
- Design review: `None` / `None`

## Errors

- candidate_pack_id must not contain TODO or placeholder markers
- promoted_at must not contain TODO or placeholder markers
- source_candidate_pack must not contain TODO or placeholder markers
- source_patch_manifest must not contain TODO or placeholder markers
- manual_design_review_file must not contain TODO or placeholder markers
- candidate_preflight_report must not contain TODO or placeholder markers
- TODO: content id from source_patch_manifest: id must not contain TODO or placeholder markers
- TODO: content id from source_patch_manifest: path must not contain TODO or placeholder markers
- TODO: content id from source_patch_manifest path does not exist: passives/TODO.json

## Warnings

- None

## Limitations

- This validator checks simulation-candidate manifest completeness only.
- A valid simulation-candidate manifest does not run Schema, budget, Bot, Replay, or playtest gates.
- A valid simulation-candidate manifest does not promote content into accepted_content or Runtime.
