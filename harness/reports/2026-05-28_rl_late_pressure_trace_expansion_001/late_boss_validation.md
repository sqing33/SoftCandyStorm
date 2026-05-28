# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-28_rl_late_pressure_trace_expansion_001/late_boss_recovery_samples.jsonl`
- Samples: `32`
- Maps: `caramel-workshop, cracked-star-jar, soda-creek`
- Seeds: `62500, 62505, 62507, 62509`
- Time range: `210.0159` to `221.3517` seconds

## Original Actions
- `3`: 2
- `4`: 30

## Target Actions
- `1`: 1
- `8`: 31

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
