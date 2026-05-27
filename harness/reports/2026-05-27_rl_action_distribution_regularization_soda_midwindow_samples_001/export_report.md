# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `5`
- Inspected trace rows: `798`
- Negative route_recovery rows: `54`
- Boundary hotspot rows: `52`
- Outside time window rows: `708`
- Missing observation rows: `0`
- Exported samples: `51`
- Samples: `harness/reports/2026-05-27_rl_action_distribution_regularization_soda_midwindow_samples_001/soda_midwindow_route_recovery_samples.jsonl`

## Distributions

- Maps: `{"soda-creek": 51}`
- Original actions: `{"1": 24, "6": 27}`
- Target actions: `{"2": 27, "5": 24}`
- Target labels: `{"geometry_inward_non_wallward_action": 51}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
