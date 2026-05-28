# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `8`
- Inspected trace rows: `3553`
- Negative route_recovery rows: `551`
- Boundary hotspot rows: `533`
- Outside time window rows: `2880`
- Map filtered traces: `0`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- High health filtered rows: `0`
- Pressure filtered rows: `0`
  - Low health risk filtered rows: `0`
  - Hazard pressure filtered rows: `0`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `527`
- Samples: `harness/reports/2026-05-28_rl_curriculum_stage02_late_recovery_samples_001/late_route_recovery_samples.jsonl`

## Distributions

- Maps: `{"caramel-workshop": 195, "cracked-star-jar": 132, "soda-creek": 200}`
- Original actions: `{"2": 217, "3": 27, "4": 158, "7": 125}`
- Target actions: `{"0": 20, "1": 5, "3": 119, "4": 26, "5": 23, "6": 186, "7": 30, "8": 118}`
- Target labels: `{"geometry_inward_non_wallward_action": 439, "highest_scored_non_wallward_action": 88}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
