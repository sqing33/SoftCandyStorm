# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `8`
- Inspected trace rows: `3745`
- Negative route_recovery rows: `1542`
- Boundary hotspot rows: `1513`
- Outside time window rows: `1855`
- Map filtered traces: `0`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- High health filtered rows: `0`
- Pressure filtered rows: `0`
  - Low health risk filtered rows: `0`
  - Hazard pressure filtered rows: `0`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `1473`
- Samples: `harness/reports/2026-05-28_rl_curriculum_stage02_staged_opening_fallback_trace_001/mid_route_recovery_samples.jsonl`

## Distributions

- Maps: `{"caramel-workshop": 580, "cracked-star-jar": 487, "soda-creek": 406}`
- Original actions: `{"1": 3, "2": 434, "3": 15, "4": 714, "7": 307}`
- Target actions: `{"0": 284, "1": 53, "2": 1, "3": 147, "4": 126, "5": 173, "6": 104, "7": 97, "8": 488}`
- Target labels: `{"geometry_inward_non_wallward_action": 705, "highest_scored_non_wallward_action": 768}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
