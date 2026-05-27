# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-27_rl_late_boundary_handoff_cracked_star_samples_001/cracked_star_handoff_60_90_recovery_samples.jsonl`
- Samples: `190`
- Maps: `cracked-star-jar`
- Seeds: `62400, 62401, 62402, 62403, 62404`
- Time range: `60.3328` to `89.999` seconds

## Original Actions
- `2`: 88
- `3`: 86
- `8`: 16

## Target Actions
- `1`: 34
- `3`: 29
- `6`: 41
- `7`: 86

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
