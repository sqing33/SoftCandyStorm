# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-28_rl_late_pressure_trace_expansion_001/late_boundary_recovery_samples.jsonl`
- Samples: `1076`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `62500, 62503, 62505, 62506, 62507, 62508, 62509`
- Time range: `180.0095` to `224.2523` seconds

## Original Actions
- `3`: 470
- `4`: 515
- `7`: 91

## Target Actions
- `1`: 190
- `2`: 69
- `3`: 89
- `8`: 728

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
