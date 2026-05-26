# Story Codex Acceptance Review Packet

- Source: `harness/story_review/story_codex_acceptance_manifest_template.json`
- Decision: `story_codex_acceptance_review_packet_needs_evidence`
- Candidate pack: `2026-05-26_story_codex_seed_pack`
- Chapters: 6
- Codex entries: 26
- Evidence files: 0 / 3
- Placeholder evidence: 3
- Missing evidence: 0
- Placeholder manifest fields: 1

## Manifest Fields

| Field | Status | Value |
|---|---|---|
| `candidate_pack_id` | `filled` | `2026-05-26_story_codex_seed_pack` |
| `accepted_at` | `placeholder` | `TODO: YYYY-MM-DDTHH:MM:SSZ` |

## Required Evidence

| Field | Status | Expected | Required checks |
|---|---|---|---|
| `source_ui_candidate_manifest` | `placeholder` | `story_codex_ui_candidate_manifest_valid` | None |
| `runtime_ui_review_file` | `placeholder` | `story_codex_runtime_ui_review / runtime_ui_review_pass` | `f3_entry_visible`, `no_generated_candidate_text_loaded`, `no_runtime_integration_claim`, `layout_readable` |
| `final_human_acceptance_file` | `placeholder` | `story_codex_final_acceptance / accepted_content` | `accepts_story_codex_text`, `accepted_content_only_after_reviews`, `release_ready`, `runtime_integrated` |

## Evidence Paths

- `source_ui_candidate_manifest`: `harness/story_review/ui_candidates/<candidate>/ui_candidate_manifest.json` -> `None`
- `runtime_ui_review_file`: `harness/story_review/runtime_ui_reviews/<human-runtime-ui-review>.json` -> `None`
- `final_human_acceptance_file`: `harness/story_review/final_acceptance/<human-final-acceptance>.json` -> `None`

## Required Next Steps

- Fill or replace the UI candidate manifest evidence after human story/codex review passes.
- Fill or replace Runtime UI review evidence with concrete F3 visibility and text-loading observations.
- Fill or replace final human acceptance evidence only after prior reviews pass.
- Run harness/story_review/validate_story_codex_acceptance_manifest.py after every TODO is removed.

## Limitations

- This packet organizes final story/codex acceptance evidence only.
- It does not validate the acceptance manifest as passing.
- It does not copy candidate story/codex text, mark Runtime integration, or approve release readiness.
