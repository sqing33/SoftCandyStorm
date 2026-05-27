# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-27_rl_route_recovery_supervision_samples_001/route_recovery_samples.jsonl`
- Samples: `689`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `62300, 62301, 62302`
- Time range: `8.0` to `214.0168` seconds

## Original Actions
- `3`: 137
- `4`: 397
- `7`: 155

## Target Actions
- `1`: 47
- `2`: 151
- `3`: 103
- `5`: 61
- `7`: 5
- `8`: 322

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
