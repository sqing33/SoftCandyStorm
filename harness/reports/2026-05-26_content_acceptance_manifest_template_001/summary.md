# Content Acceptance Manifest Validation

- Source: `harness/content_review/content_acceptance_manifest_template.json`
- Decision: `content_acceptance_manifest_invalid`
- Candidate: `2026-05-26_phase4_roster_gap_full_pack`
- Contents: 1 / 1
- Simulation candidate manifest: `None`
- Final acceptance: `None` / `None`
- Accepted content lockfile: `None`

## Errors

- accepted_at must not contain TODO or placeholder markers
- source_simulation_candidate_manifest must not contain TODO or placeholder markers
- final_human_acceptance_file must not contain TODO or placeholder markers
- accepted_content_lockfile_report must not contain TODO or placeholder markers
- TODO: content id from source simulation candidate: id must not contain TODO or placeholder markers
- TODO: content id from source simulation candidate: path must not contain TODO or placeholder markers

## Warnings

- None

## Limitations

- This validator checks final content acceptance evidence only.
- A valid acceptance manifest may mark content accepted, but it does not prove Runtime integration.
- A valid acceptance manifest is not release readiness and cannot bypass future package, privacy, playtest, or Runtime smoke gates.
