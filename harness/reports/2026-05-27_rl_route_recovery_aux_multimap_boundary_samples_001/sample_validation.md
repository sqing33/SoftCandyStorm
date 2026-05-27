# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-27_rl_route_recovery_aux_multimap_boundary_samples_001/multimap_boundary_samples.jsonl`
- Samples: `1676`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `62400, 62401, 62402, 62403, 62404`
- Time range: `4.6667` to `60.0328` seconds

## Original Actions
- `1`: 364
- `2`: 14
- `3`: 627
- `4`: 45
- `5`: 117
- `7`: 501
- `8`: 8

## Target Actions
- `1`: 35
- `3`: 291
- `4`: 222
- `5`: 570
- `6`: 30
- `7`: 383
- `8`: 145

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
