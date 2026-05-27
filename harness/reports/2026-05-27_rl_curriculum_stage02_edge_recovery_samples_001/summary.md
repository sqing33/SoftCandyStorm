# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-27_rl_curriculum_stage02_edge_recovery_samples_001/edge_recovery_samples.jsonl`
- Samples: `2215`
- Maps: `soda-creek`
- Seeds: `62201`
- Time range: `6.8333` to `178.7759` seconds

## Original Actions
- `2`: 35
- `4`: 1760
- `5`: 1
- `6`: 24
- `7`: 378
- `8`: 17

## Target Actions
- `0`: 392
- `1`: 38
- `3`: 1759
- `5`: 23
- `7`: 1
- `8`: 2

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
