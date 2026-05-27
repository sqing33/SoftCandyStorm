# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-27_rl_action_distribution_opening_action3_samples_001/soda_opening_20_45_action3_route_recovery_samples.jsonl`
- Samples: `587`
- Maps: `soda-creek`
- Seeds: `62400, 62401, 62402, 62403, 62404, 62405, 62406, 62408, 62409, 62410, 62411, 62412, 62414, 62415, 62416, 62417, 62418, 62419`
- Time range: `20.0` to `44.9997` seconds

## Original Actions
- `3`: 587

## Target Actions
- `1`: 25
- `5`: 262
- `7`: 205
- `8`: 95

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
