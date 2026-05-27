# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-27_rl_route_recovery_aux_online_route_risk_phase_aligned_samples_001/online_route_risk_phase_aligned_samples.jsonl`
- Samples: `143`
- Maps: `soda-creek`
- Seeds: `62400, 62402, 62403`
- Time range: `20.0` to `46.7996` seconds

## Original Actions
- `1`: 23
- `5`: 41
- `6`: 79

## Target Actions
- `1`: 17
- `2`: 102
- `3`: 16
- `5`: 7
- `7`: 1

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
