# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `8`
- Inspected trace rows: `490`
- Negative route_recovery rows: `61`
- Boundary hotspot rows: `56`
- Outside time window rows: `389`
- Map filtered traces: `5`
- Original action filtered rows: `0`
- Low health filtered rows: `7`
- High health filtered rows: `0`
- Pressure filtered rows: `0`
  - Low health risk filtered rows: `0`
  - Hazard pressure filtered rows: `0`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `45`
- Samples: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_trace_001/caramel_late_route_recovery_samples.jsonl`

## Distributions

- Maps: `{"caramel-workshop": 45}`
- Original actions: `{"2": 9, "3": 33, "8": 3}`
- Target actions: `{"1": 11, "3": 9, "5": 14, "7": 2, "8": 9}`
- Target labels: `{"geometry_inward_non_wallward_action": 9, "highest_scored_non_wallward_action": 36}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
