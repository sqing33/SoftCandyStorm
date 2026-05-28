# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_invalid`
- Source: `harness/reports/2026-05-28_rl_late_pressure_recovery_samples_001/late_hazard_recovery_samples.jsonl`
- Samples: `0`
- Maps: ``
- Seeds: ``
- Time range: `None` to `None` seconds

## Original Actions

## Target Actions

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
