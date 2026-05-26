# Content Final Acceptance Validation

- Source: `harness/content_review/content_final_acceptance_template.json`
- Decision: `content_final_acceptance_invalid`
- Candidate: `2026-05-26_phase4_roster_gap_full_pack`
- Gate decision: `needs_more_review`
- Simulation candidate manifest: `None`
- Accepted content lockfile: `None`
- Observations: 2
- Unresolved issues: 1

## Errors

- reviewer must not contain TODO or placeholder markers
- summary must not contain TODO or placeholder markers
- checks.accepts_content_pack must be true
- checks.accepted_content_only_after_reviews must be true
- checks.lockfile_valid must be true
- concrete_observations must not contain TODO or placeholder markers
- unresolved_issues must not contain TODO or placeholder markers
- source_simulation_candidate_manifest must not contain TODO or placeholder markers
- accepted_content_lockfile_report must not contain TODO or placeholder markers

## Warnings

- None

## Limitations

- This validator checks final content acceptance record completeness only.
- It does not run Harness simulation, copy candidate content, compute content hashes, or approve release readiness.
- Accepted content still needs release candidate, package, privacy, playtest, and Runtime smoke gates before release.
