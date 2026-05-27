# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-27_rl_action_distribution_multiseed_midwindow_samples_001/soda_midwindow_45_100_route_recovery_samples.jsonl`
- Samples: `389`
- Maps: `soda-creek`
- Seeds: `62404, 62406, 62410, 62414`
- Time range: `45.333` to `99.9988` seconds

## Original Actions
- `1`: 287
- `2`: 27
- `3`: 17
- `6`: 58

## Target Actions
- `1`: 11
- `2`: 42
- `3`: 68
- `5`: 251
- `7`: 17

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
