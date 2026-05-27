# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-27_rl_route_recovery_aux_focused_boundary_samples_001/focused_boundary_samples.jsonl`
- Samples: `134`
- Maps: `soda-creek`
- Seeds: `62300`
- Time range: `6.6667` to `60.0328` seconds

## Original Actions
- `3`: 82
- `5`: 52

## Target Actions
- `1`: 7
- `5`: 22
- `7`: 63
- `8`: 42

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
