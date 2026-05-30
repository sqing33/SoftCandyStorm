# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-30_rl_stage01_seed63402_target_guard_samples_001/seed63402_target_guard_samples.jsonl`
- Samples: `17`
- Maps: `soda-creek`
- Seeds: `63402`
- Time range: `31.9999` to `37.2664` seconds

## Original Actions
- `5`: 17

## Target Actions
- `7`: 17

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
