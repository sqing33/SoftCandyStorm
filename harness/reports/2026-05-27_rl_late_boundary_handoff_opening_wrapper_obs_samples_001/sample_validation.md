# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-27_rl_late_boundary_handoff_opening_wrapper_obs_samples_001/handoff_60_90_recovery_samples.jsonl`
- Samples: `713`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `62400, 62401, 62402, 62403, 62404`
- Time range: `60.3328` to `89.999` seconds

## Original Actions
- `1`: 50
- `2`: 107
- `3`: 213
- `8`: 343

## Target Actions
- `0`: 111
- `1`: 150
- `2`: 5
- `3`: 55
- `4`: 134
- `5`: 1
- `6`: 48
- `7`: 159
- `8`: 50

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
