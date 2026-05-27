# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `15`
- Inspected trace rows: `2266`
- Negative route_recovery rows: `1782`
- Boundary hotspot rows: `1714`
- Missing observation rows: `0`
- Exported samples: `1676`
- Samples: `harness/reports/2026-05-27_rl_route_recovery_aux_multimap_boundary_samples_001/multimap_boundary_samples.jsonl`

## Distributions

- Maps: `{"caramel-workshop": 676, "cracked-star-jar": 558, "soda-creek": 442}`
- Original actions: `{"1": 364, "2": 14, "3": 627, "4": 45, "5": 117, "7": 501, "8": 8}`
- Target actions: `{"1": 35, "3": 291, "4": 222, "5": 570, "6": 30, "7": 383, "8": 145}`
- Target labels: `{"geometry_inward_non_wallward_action": 1355, "highest_scored_non_wallward_action": 321}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
