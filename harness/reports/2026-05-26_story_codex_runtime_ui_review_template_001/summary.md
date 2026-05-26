# Story Codex Runtime UI Review Validation

- Source: `harness/story_review/story_codex_runtime_ui_review_template.json`
- Decision: `story_codex_runtime_ui_review_invalid`
- Candidate: `2026-05-26_story_codex_seed_pack`
- Gate decision: `needs_more_review`
- UI candidate manifest: `None`
- Observations: 2
- Unresolved issues: 1

## Errors

- reviewer must not contain TODO or placeholder markers
- summary must not contain TODO or placeholder markers
- checks.f3_entry_visible must be true
- checks.no_generated_candidate_text_loaded must be true
- checks.no_runtime_integration_claim must be true
- checks.layout_readable must be true
- concrete_observations must not contain TODO or placeholder markers
- unresolved_issues must not contain TODO or placeholder markers
- source_ui_candidate_manifest must not contain TODO or placeholder markers

## Warnings

- None

## Limitations

- This validator checks human Runtime UI review record completeness only.
- It does not run Bevy, inspect pixels, load story/codex body text, or approve final acceptance.
- A valid Runtime UI review is not release readiness and cannot bypass final human acceptance.
