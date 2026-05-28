# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `8`
- Inspected trace rows: `490`
- Negative route_recovery rows: `109`
- Boundary hotspot rows: `106`
- Outside time window rows: `339`
- Map filtered traces: `5`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- High health filtered rows: `0`
- Pressure filtered rows: `0`
  - Low health risk filtered rows: `0`
  - Hazard pressure filtered rows: `0`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `102`
- Samples: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_trace_001/caramel_opening_route_recovery_samples.jsonl`

## Distributions

- Maps: `{"caramel-workshop": 102}`
- Original actions: `{"2": 69, "7": 33}`
- Target actions: `{"0": 30, "3": 8, "4": 4, "6": 60}`
- Target labels: `{"geometry_inward_non_wallward_action": 63, "highest_scored_non_wallward_action": 39}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
