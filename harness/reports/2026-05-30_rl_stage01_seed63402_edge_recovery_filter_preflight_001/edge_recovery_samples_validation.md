# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_filter_preflight_001/edge_recovery_samples.jsonl`
- Samples: `76`
- Maps: `soda-creek`
- Seeds: `63400, 63401, 63402`
- Time range: `6.8333` to `58.9661` seconds

## Original Actions
- `1`: 1
- `2`: 3
- `3`: 2
- `4`: 2
- `5`: 6
- `6`: 20
- `7`: 4
- `8`: 38

## Target Actions
- `0`: 23
- `1`: 38
- `3`: 6
- `4`: 1
- `5`: 3
- `7`: 5

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
