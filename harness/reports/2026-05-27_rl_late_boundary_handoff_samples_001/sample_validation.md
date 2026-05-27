# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-27_rl_late_boundary_handoff_samples_001/handoff_recovery_samples.jsonl`
- Samples: `2438`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `62400, 62401, 62402, 62403, 62404`
- Time range: `60.3328` to `179.6761` seconds

## Original Actions
- `2`: 82
- `3`: 92
- `4`: 948
- `7`: 1294
- `8`: 22

## Target Actions
- `0`: 658
- `1`: 65
- `2`: 248
- `3`: 735
- `4`: 12
- `5`: 107
- `6`: 3
- `7`: 103
- `8`: 507

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
