# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-27_rl_action_distribution_regularization_soda_midwindow_samples_001/soda_midwindow_route_recovery_samples.jsonl`
- Samples: `51`
- Maps: `soda-creek`
- Seeds: `62404`
- Time range: `50.3329` to `79.9991` seconds

## Original Actions
- `1`: 24
- `6`: 27

## Target Actions
- `2`: 27
- `5`: 24

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
