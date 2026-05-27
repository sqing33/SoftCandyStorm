# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-27_rl_late_route_action4_midlate_late_boundary_samples_001/late_boundary_recovery_samples.jsonl`
- Samples: `1001`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `62400, 62401, 62402, 62403, 62404`
- Time range: `180.0095` to `225.0191` seconds

## Original Actions
- `2`: 1
- `3`: 293
- `4`: 124
- `5`: 262
- `6`: 43
- `7`: 223
- `8`: 55

## Target Actions
- `1`: 304
- `2`: 18
- `3`: 202
- `4`: 97
- `5`: 14
- `6`: 86
- `7`: 227
- `8`: 53

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
