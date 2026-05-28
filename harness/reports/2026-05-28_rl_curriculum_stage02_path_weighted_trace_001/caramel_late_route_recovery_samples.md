# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `8`
- Inspected trace rows: `968`
- Negative route_recovery rows: `153`
- Boundary hotspot rows: `150`
- Outside time window rows: `777`
- Map filtered traces: `5`
- Original action filtered rows: `0`
- Low health filtered rows: `3`
- High health filtered rows: `0`
- Pressure filtered rows: `0`
  - Low health risk filtered rows: `0`
  - Hazard pressure filtered rows: `0`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `144`
- Samples: `harness/reports/2026-05-28_rl_curriculum_stage02_path_weighted_trace_001/caramel_late_route_recovery_samples.jsonl`

## Distributions

- Maps: `{"caramel-workshop": 144}`
- Original actions: `{"3": 135, "7": 3, "8": 6}`
- Target actions: `{"0": 2, "1": 46, "4": 1, "5": 80, "7": 15}`
- Target labels: `{"geometry_inward_non_wallward_action": 10, "highest_scored_non_wallward_action": 134}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
