# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_late_retention_map_repair_samples_001/caramel_late_route_recovery_samples.jsonl`
- Samples: `46`
- Maps: `caramel-workshop`
- Seeds: `63100, 63102`
- Time range: `180.0095` to `221.0182` seconds

## Original Actions
- `1`: 3
- `3`: 15
- `5`: 12
- `7`: 5
- `8`: 11

## Target Actions
- `0`: 3
- `1`: 26
- `4`: 6
- `5`: 4
- `7`: 7

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
