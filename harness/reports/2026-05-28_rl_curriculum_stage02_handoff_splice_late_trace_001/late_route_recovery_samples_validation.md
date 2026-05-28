# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-28_rl_curriculum_stage02_handoff_splice_late_trace_001/late_route_recovery_samples.jsonl`
- Samples: `207`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `63100, 63101, 63102`
- Time range: `180.0095` to `259.025` seconds

## Original Actions
- `3`: 106
- `4`: 1
- `5`: 78
- `8`: 22

## Target Actions
- `0`: 9
- `1`: 129
- `3`: 9
- `4`: 5
- `5`: 44
- `7`: 10
- `8`: 1

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
