# Failure Case Validation

- Root: `harness/reports/2026-05-26_post_recovery_matrix_smoke_001/failure_cases.json`
- Decision: `failure_cases_valid`
- File count: 1
- Record count: 4

## Categories

- `balance`: 4

## Errors

- None

## Warnings

- harness/reports/2026-05-26_post_recovery_matrix_smoke_001/failure_cases.json: non-canonical report-local case_id `random_seed_31000`
- harness/reports/2026-05-26_post_recovery_matrix_smoke_001/failure_cases.json:1: non-canonical report-local case_id `coward_seed_31000`
- harness/reports/2026-05-26_post_recovery_matrix_smoke_001/failure_cases.json:2: non-canonical report-local case_id `tank_seed_31000`
- harness/reports/2026-05-26_post_recovery_matrix_smoke_001/failure_cases.json:3: non-canonical report-local case_id `boss_hunter_seed_31000`

## Limitations

- This validator checks failure case record structure and provenance fields only.
- It does not prove the fix is correct; validation commands or reports must still be reviewed.
