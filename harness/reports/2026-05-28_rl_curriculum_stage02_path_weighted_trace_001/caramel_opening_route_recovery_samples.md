# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `8`
- Inspected trace rows: `968`
- Negative route_recovery rows: `217`
- Boundary hotspot rows: `211`
- Outside time window rows: `669`
- Map filtered traces: `5`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- High health filtered rows: `0`
- Pressure filtered rows: `0`
  - Low health risk filtered rows: `0`
  - Hazard pressure filtered rows: `0`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `202`
- Samples: `harness/reports/2026-05-28_rl_curriculum_stage02_path_weighted_trace_001/caramel_opening_route_recovery_samples.jsonl`

## Distributions

- Maps: `{"caramel-workshop": 202}`
- Original actions: `{"2": 137, "7": 65}`
- Target actions: `{"0": 58, "3": 19, "4": 8, "6": 117}`
- Target labels: `{"geometry_inward_non_wallward_action": 124, "highest_scored_non_wallward_action": 78}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
