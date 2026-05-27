# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `15`
- Inspected trace rows: `8173`
- Negative route_recovery rows: `1055`
- Boundary hotspot rows: `1027`
- Outside time window rows: `6816`
- Original action filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `1001`
- Samples: `harness/reports/2026-05-27_rl_late_route_action4_midlate_late_boundary_samples_001/late_boundary_recovery_samples.jsonl`

## Distributions

- Maps: `{"caramel-workshop": 441, "cracked-star-jar": 370, "soda-creek": 190}`
- Original actions: `{"2": 1, "3": 293, "4": 124, "5": 262, "6": 43, "7": 223, "8": 55}`
- Target actions: `{"1": 304, "2": 18, "3": 202, "4": 97, "5": 14, "6": 86, "7": 227, "8": 53}`
- Target labels: `{"geometry_inward_non_wallward_action": 838, "highest_scored_non_wallward_action": 163}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
