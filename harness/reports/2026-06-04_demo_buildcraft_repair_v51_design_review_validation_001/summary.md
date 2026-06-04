# Content Candidate Design Review Validation

- Source: `harness/content_review/drafts/2026-06-04_demo_buildcraft_repair_v51_full_pack_design_review_draft.json`
- Decision: `content_candidate_design_review_invalid`
- Gate decision: `needs_more_review`
- Contents reviewed: 1 / 1
- Repair items: 1
- Batch risks: 1

## Errors

- reviewer must not contain TODO or placeholder markers
- reviewed_at must not contain TODO or placeholder markers
- summary must not contain TODO or placeholder markers
- frosting-grassland-standard: theme_fit must be an integer from 1 to 5
- frosting-grassland-standard: novelty must be an integer from 1 to 5
- frosting-grassland-standard: build_potential must be an integer from 1 to 5
- frosting-grassland-standard: counterplay_clarity must be an integer from 1 to 5
- frosting-grassland-standard: visual_audio_fit must be an integer from 1 to 5
- frosting-grassland-standard: balance_risk must be one of high, low, medium
- frosting-grassland-standard: notes must not contain TODO or placeholder markers
- frosting-grassland-standard: required_changes must not contain TODO or placeholder markers
- batch_risks must not contain TODO or placeholder markers
- next_actions must not contain TODO or placeholder markers

## Warnings

- None

## Limitations

- This validator checks content design review completeness only.
- It does not run Schema, static budget, simulation, replay, or playtest gates.
- A simulate_candidate decision does not promote content into accepted_content or Runtime.
