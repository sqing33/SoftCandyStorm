# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `18`
- Inspected trace rows: `2688`
- Negative route_recovery rows: `628`
- Boundary hotspot rows: `619`
- Outside time window rows: `1921`
- Original action filtered rows: `17`
- Missing observation rows: `0`
- Exported samples: `587`
- Samples: `harness/reports/2026-05-27_rl_action_distribution_opening_action3_samples_001/soda_opening_20_45_action3_route_recovery_samples.jsonl`

## Distributions

- Maps: `{"soda-creek": 587}`
- Original actions: `{"3": 587}`
- Target actions: `{"1": 25, "5": 262, "7": 205, "8": 95}`
- Target labels: `{"geometry_inward_non_wallward_action": 298, "highest_scored_non_wallward_action": 289}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
