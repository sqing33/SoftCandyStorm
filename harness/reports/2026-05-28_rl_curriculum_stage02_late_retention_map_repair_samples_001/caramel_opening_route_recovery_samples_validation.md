# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_late_retention_map_repair_samples_001/caramel_opening_route_recovery_samples.jsonl`
- Samples: `102`
- Maps: `caramel-workshop`
- Seeds: `63100, 63101, 63102`
- Time range: `7.0` to `59.9994` seconds

## Original Actions
- `2`: 69
- `7`: 33

## Target Actions
- `0`: 30
- `3`: 8
- `4`: 4
- `6`: 60

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
