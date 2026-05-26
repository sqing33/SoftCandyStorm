# Manual Playtest Acceptance Review Packet

- Decision: `manual_playtest_acceptance_review_packet_needs_evidence`
- Candidate id: `current-base-demo-runtime`
- Content hash: `TODO:content-hash-after-freeze`
- Evidence files: 7 / 7
- Strict validation: `manual_review_invalid`
- RC manual playtest gate: `waiting`
- Downstream content acceptance: `content_acceptance_review_packet_needs_evidence`
- Downstream accepted content lockfile: `accepted_content_lockfile_blocked`

## Evidence

| Field | Status | Expected | Path |
|---|---|---|---|
| `manual_review_template` | `exists` | 9-run manual playtest template exists | `harness/playtest/runtime_manual_review_template.json` |
| `manual_review_source` | `exists` | human-filled 9-run review source must replace TODO values | `harness/playtest/drafts/2026-05-26_runtime_manual_playtest_review_draft.json` |
| `manual_review_packet` | `exists` | human checklist packet exists for reviewer handoff | `harness/reports/2026-05-26_runtime_manual_playtest_review_packet_001/summary.md` |
| `strict_validation_report` | `exists` | validate_manual_review.py --strict-acceptance JSON report exists | `harness/reports/2026-05-26_runtime_manual_playtest_strict_validation_current_local_001/manual_review_validation.json` |
| `release_candidate_evidence` | `exists` | manual_playtest release gate must pass only after real human acceptance | `harness/release/current_local_rc_evidence.json` |
| `content_acceptance_review_packet` | `exists` | downstream content acceptance evidence packet status is visible | `harness/reports/2026-05-26_phase4_content_acceptance_review_packet_001/content_acceptance_review_packet.json` |
| `accepted_content_lockfile_report` | `exists` | downstream accepted content lockfile status is visible | `harness/reports/2026-05-26_accepted_content_lockfile_current_local_001/accepted_content_lockfile.json` |

## Manual Review Status

- Source status: `draft_todo`
- Acceptance decision: `needs_more_runs`
- Runs: 0 completed / 9 present
- Missing run ids: None
- TODO count: `104`
- Reviewer: `TODO: human reviewer`
- Reviewed at: `TODO: YYYY-MM-DD`

## Strict Validation

- Status: `invalid`
- Decision: `manual_review_invalid`
- Strict acceptance: `True`
- Error count: `72`
- Warning count: `0`

## Blockers

- manual review source still contains TODO placeholders
- manual review has not accepted the candidate
- manual review has fewer than 9 completed playtest_pass runs
- strict manual review validation is `manual_review_invalid`
- release candidate manual_playtest gate is `waiting`

## Errors

- None

## Required Next Steps

- Run the 9 human playtest sessions and replace every TODO rating, note, tag, and next action.
- Run validate_manual_review.py --strict-acceptance and keep a manual_review_valid JSON/Markdown report.
- Update the release candidate manual_playtest gate only after real human evidence exists.
- Use the validated manual review as evidence for content acceptance and accepted content lockfile generation.

## Limitations

- This packet organizes manual playtest acceptance evidence only.
- It does not run Runtime, inspect gameplay, fill human review fields, promote content, write lockfiles, or approve release.
- Automated capture, Bot results, and fixture reviews cannot replace the real human review source.
