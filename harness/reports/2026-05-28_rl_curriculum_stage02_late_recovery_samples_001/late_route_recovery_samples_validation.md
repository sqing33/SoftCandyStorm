# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_late_recovery_samples_001/late_route_recovery_samples.jsonl`
- Samples: `527`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `62800, 62801, 62802`
- Time range: `180.0095` to `270.1556` seconds

## Original Actions
- `2`: 217
- `3`: 27
- `4`: 158
- `7`: 125

## Target Actions
- `0`: 20
- `1`: 5
- `3`: 119
- `4`: 26
- `5`: 23
- `6`: 186
- `7`: 30
- `8`: 118

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
