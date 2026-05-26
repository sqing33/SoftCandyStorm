# Release Candidate Evidence Validation

- Source: `harness/release/current_local_rc_evidence.json`
- Candidate: `current-local-2026-05-26`
- Release stage: `prototype-local`
- Decision: `release_candidate_not_ready`
- Required gates: 17
- Provided gates: 17

## Gate Summary

| Gate | Status | Evidence | Synthetic |
|---|---|---:|---|
| `content_frozen` | `waiting` | 2 | False |
| `compile` | `pass` | 2 | False |
| `unit_tests` | `pass` | 1 | False |
| `headless_simulation` | `waiting` | 1 | False |
| `multi_seed_no_deadlock` | `waiting` | 1 | False |
| `content_schema` | `pass` | 2 | False |
| `static_budget` | `pass` | 3 | False |
| `bot_matrix` | `fail` | 2 | False |
| `replay_regression` | `pass` | 1 | False |
| `performance` | `waiting` | 1 | False |
| `manual_playtest` | `waiting` | 5 | False |
| `asset_provenance` | `pass` | 1 | False |
| `asset_manual_review` | `waiting` | 6 | False |
| `story_codex_review` | `waiting` | 4 | False |
| `telemetry_privacy` | `waiting` | 18 | False |
| `failure_case_review` | `waiting` | 2 | False |
| `release_package` | `waiting` | 4 | False |

## Blockers

- content_frozen: gate status is `waiting`
- headless_simulation: gate status is `waiting`
- multi_seed_no_deadlock: gate status is `waiting`
- bot_matrix: gate status is `fail`
- performance: gate status is `waiting`
- manual_playtest: gate status is `waiting`
- asset_manual_review: gate status is `waiting`
- story_codex_review: gate status is `waiting`
- telemetry_privacy: gate status is `waiting`
- failure_case_review: gate status is `waiting`
- release_package: gate status is `waiting`

## Errors

- None

## Warnings

- None

## Limitations

- This validator checks release evidence completeness only; it does not run compile, tests, harness, replay, performance, or manual playtests.
- Historical smoke reports are only acceptable when they directly cover the current release candidate and are marked non-synthetic.
- A ready decision requires every required gate to be present, passing, and backed by existing evidence paths.
