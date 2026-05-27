# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `14`
- Inspected trace rows: `6860`
- Negative route_recovery rows: `2616`
- Boundary hotspot rows: `2520`
- Outside time window rows: `3364`
- Original action filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `2438`
- Samples: `harness/reports/2026-05-27_rl_late_boundary_handoff_samples_001/handoff_recovery_samples.jsonl`

## Distributions

- Maps: `{"caramel-workshop": 1221, "cracked-star-jar": 655, "soda-creek": 562}`
- Original actions: `{"2": 82, "3": 92, "4": 948, "7": 1294, "8": 22}`
- Target actions: `{"0": 658, "1": 65, "2": 248, "3": 735, "4": 12, "5": 107, "6": 3, "7": 103, "8": 507}`
- Target labels: `{"geometry_inward_non_wallward_action": 1206, "highest_scored_non_wallward_action": 1232}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
