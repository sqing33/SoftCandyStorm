# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-27_rl_late_route_action4_samples_001/mid_late_action4_samples.jsonl`
- Samples: `254`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `62300, 62301, 62302`
- Time range: `60.9994` to `214.1501` seconds

## Original Actions
- `4`: 254

## Target Actions
- `3`: 88
- `5`: 25
- `7`: 6
- `8`: 135

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
