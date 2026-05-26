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
| `content_frozen` | `waiting` | 0 | False |
| `compile` | `blocked` | 1 | False |
| `unit_tests` | `blocked` | 1 | False |
| `headless_simulation` | `blocked` | 1 | False |
| `multi_seed_no_deadlock` | `blocked` | 1 | False |
| `content_schema` | `blocked` | 2 | False |
| `static_budget` | `blocked` | 3 | False |
| `bot_matrix` | `blocked` | 1 | False |
| `replay_regression` | `blocked` | 1 | False |
| `performance` | `blocked` | 1 | False |
| `manual_playtest` | `waiting` | 1 | False |
| `asset_provenance` | `pass` | 1 | False |
| `asset_manual_review` | `waiting` | 2 | False |
| `story_codex_review` | `waiting` | 2 | False |
| `telemetry_privacy` | `waiting` | 9 | False |
| `failure_case_review` | `blocked` | 1 | False |
| `release_package` | `blocked` | 3 | False |

## Blockers

- content_frozen: gate status is `waiting`
- compile: gate status is `blocked`
- unit_tests: gate status is `blocked`
- headless_simulation: gate status is `blocked`
- multi_seed_no_deadlock: gate status is `blocked`
- content_schema: gate status is `blocked`
- static_budget: gate status is `blocked`
- bot_matrix: gate status is `blocked`
- replay_regression: gate status is `blocked`
- performance: gate status is `blocked`
- manual_playtest: gate status is `waiting`
- asset_manual_review: gate status is `waiting`
- story_codex_review: gate status is `waiting`
- telemetry_privacy: gate status is `waiting`
- failure_case_review: gate status is `blocked`
- release_package: gate status is `blocked`

## Errors

- None

## Warnings

- None

## Limitations

- This validator checks release evidence completeness only; it does not run compile, tests, harness, replay, performance, or manual playtests.
- Historical smoke reports are only acceptable when they directly cover the current release candidate and are marked non-synthetic.
- A ready decision requires every required gate to be present, passing, and backed by existing evidence paths.
