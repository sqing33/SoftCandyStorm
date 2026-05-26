# Story Codex UI Candidate Manifest Validation

- Source: `harness/story_review/story_codex_ui_candidate_manifest_template.json`
- Decision: `story_codex_ui_candidate_manifest_invalid`
- Candidate: `2026-05-26_story_codex_seed_pack`
- Chapters: 6
- Codex entries: 26
- Manual review: `None` / `None`

## Errors

- promoted_at must not contain TODO or placeholder markers
- manual_review_file must not contain TODO or placeholder markers

## Warnings

- None

## Limitations

- This validator checks UI candidate manifest completeness only.
- A valid UI candidate manifest does not promote content into accepted_content.
- A valid UI candidate manifest does not prove Runtime UI integration, final human acceptance, or release readiness.
