# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `8`
- Inspected trace rows: `408`
- Negative route_recovery rows: `129`
- Boundary hotspot rows: `124`
- Outside time window rows: `222`
- Map filtered traces: `5`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- High health filtered rows: `0`
- Pressure filtered rows: `0`
  - Low health risk filtered rows: `0`
  - Hazard pressure filtered rows: `0`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `115`
- Samples: `harness/reports/2026-05-28_rl_curriculum_stage02_late_retention_map_repair_samples_001/soda_mid_route_recovery_samples.jsonl`

## Distributions

- Maps: `{"soda-creek": 115}`
- Original actions: `{"3": 37, "5": 22, "8": 56}`
- Target actions: `{"1": 16, "4": 47, "5": 14, "6": 7, "7": 9, "8": 22}`
- Target labels: `{"geometry_inward_non_wallward_action": 76, "highest_scored_non_wallward_action": 39}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
