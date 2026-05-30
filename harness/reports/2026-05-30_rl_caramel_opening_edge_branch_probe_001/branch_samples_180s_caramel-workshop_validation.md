# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-30_rl_caramel_opening_edge_branch_probe_001/branch_samples_180s_caramel-workshop.jsonl`
- Samples: `153`
- Maps: `caramel-workshop`
- Seeds: `63401, 63402`
- Time range: `6.6333` to `54.9662` seconds

## Original Actions
- `2`: 1
- `5`: 2
- `7`: 1
- `8`: 149

## Target Actions
- `0`: 150
- `3`: 1
- `7`: 2

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
