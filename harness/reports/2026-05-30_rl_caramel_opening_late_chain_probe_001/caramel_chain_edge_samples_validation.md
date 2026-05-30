# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/caramel_chain_edge_samples_300s.jsonl`
- Samples: `1`
- Maps: `caramel-workshop`
- Seeds: `63402`
- Time range: `31.2665` to `31.2665` seconds

## Original Actions
- `5`: 1

## Target Actions
- `7`: 1

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
