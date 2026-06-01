# Edge Recovery Sample Validation

- Decision: `edge_recovery_samples_valid`
- Source: `harness/reports/2026-05-31_rl_opening_micro_window_branch_probe_001/micro_window_caramel_300s_10seed_edge_samples.jsonl`
- Samples: `1`
- Maps: `caramel-workshop`
- Seeds: `63402`
- Time range: `19.5334` to `19.5334` seconds

## Original Actions
- `5`: 1

## Target Actions
- `7`: 1

## Notes
- This validator checks sample structure and edge-action consistency only.
- A valid result means samples may be used for repair training inputs, not RL policy acceptance.
- Final policies still require deterministic high-pressure, multimap, failure-case, and acceptance checks.
