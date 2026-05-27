# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `9`
- Inspected trace rows: `1100`
- Negative route_recovery rows: `471`
- Boundary hotspot rows: `463`
- Outside time window rows: `539`
- Original action filtered rows: `209`
- Missing observation rows: `0`
- Exported samples: `254`
- Samples: `harness/reports/2026-05-27_rl_late_route_action4_samples_001/mid_late_action4_samples.jsonl`

## Distributions

- Maps: `{"caramel-workshop": 158, "cracked-star-jar": 31, "soda-creek": 65}`
- Original actions: `{"4": 254}`
- Target actions: `{"3": 88, "5": 25, "7": 6, "8": 135}`
- Target labels: `{"geometry_inward_non_wallward_action": 141, "highest_scored_non_wallward_action": 113}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
