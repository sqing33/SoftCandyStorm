# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `18`
- Inspected trace rows: `2688`
- Negative route_recovery rows: `415`
- Boundary hotspot rows: `396`
- Outside time window rows: `2141`
- Missing observation rows: `0`
- Exported samples: `389`
- Samples: `harness/reports/2026-05-27_rl_action_distribution_multiseed_midwindow_samples_001/soda_midwindow_45_100_route_recovery_samples.jsonl`

## Distributions

- Maps: `{"soda-creek": 389}`
- Original actions: `{"1": 287, "2": 27, "3": 17, "6": 58}`
- Target actions: `{"1": 11, "2": 42, "3": 68, "5": 251, "7": 17}`
- Target labels: `{"geometry_inward_non_wallward_action": 289, "highest_scored_non_wallward_action": 100}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
