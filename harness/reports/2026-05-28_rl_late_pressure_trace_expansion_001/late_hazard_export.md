# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `30`
- Inspected trace rows: `10940`
- Negative route_recovery rows: `1087`
- Boundary hotspot rows: `1080`
- Outside time window rows: `9762`
- Map filtered traces: `0`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- High health filtered rows: `0`
- Pressure filtered rows: `928`
  - Low health risk filtered rows: `0`
  - Hazard pressure filtered rows: `928`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `152`
- Samples: `harness/reports/2026-05-28_rl_late_pressure_trace_expansion_001/late_hazard_recovery_samples.jsonl`

## Distributions

- Maps: `{"caramel-workshop": 99, "cracked-star-jar": 52, "soda-creek": 1}`
- Original actions: `{"3": 67, "4": 62, "7": 23}`
- Target actions: `{"1": 27, "2": 23, "3": 1, "8": 101}`
- Target labels: `{"geometry_inward_non_wallward_action": 124, "highest_scored_non_wallward_action": 28}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
