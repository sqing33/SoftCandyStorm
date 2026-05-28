# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-28_rl_late_pressure_recovery_samples_001/late_low_health_recovery_samples.jsonl`
- Samples: `7`
- Maps: `cracked-star-jar`
- Seeds: `62300`
- Time range: `180.0095` to `185.3773` seconds

## Original Actions
- `4`: 7

## Target Actions
- `8`: 7

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
