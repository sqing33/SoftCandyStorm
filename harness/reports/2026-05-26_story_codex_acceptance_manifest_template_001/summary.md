# Story Codex Acceptance Manifest Validation

- Source: `harness/story_review/story_codex_acceptance_manifest_template.json`
- Decision: `story_codex_acceptance_manifest_invalid`
- Candidate: `2026-05-26_story_codex_seed_pack`
- Chapters: 6
- Codex entries: 26
- UI candidate manifest: `None`
- Runtime UI review: `None`
- Final acceptance: `None`

## Errors

- accepted_at must not contain TODO or placeholder markers
- source_ui_candidate_manifest must not contain TODO or placeholder markers
- runtime_ui_review_file must not contain TODO or placeholder markers
- final_human_acceptance_file must not contain TODO or placeholder markers

## Warnings

- None

## Limitations

- This validator checks final story/codex acceptance evidence only.
- A valid acceptance manifest may mark story/codex text accepted, but it does not prove Runtime integration.
- A valid acceptance manifest is not release readiness and cannot bypass future packaging, privacy, playtest, or Runtime smoke gates.
