# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `8`
- Inspected trace rows: `521`
- Negative route_recovery rows: `113`
- Boundary hotspot rows: `108`
- Outside time window rows: `338`
- Map filtered traces: `5`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- High health filtered rows: `0`
- Pressure filtered rows: `0`
  - Low health risk filtered rows: `0`
  - Hazard pressure filtered rows: `0`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `104`
- Samples: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_trace_001/soda_opening_route_recovery_samples.jsonl`

## Distributions

- Maps: `{"soda-creek": 104}`
- Original actions: `{"2": 46, "4": 22, "7": 36}`
- Target actions: `{"0": 20, "3": 25, "4": 5, "5": 8, "6": 37, "8": 9}`
- Target labels: `{"geometry_inward_non_wallward_action": 62, "highest_scored_non_wallward_action": 42}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
