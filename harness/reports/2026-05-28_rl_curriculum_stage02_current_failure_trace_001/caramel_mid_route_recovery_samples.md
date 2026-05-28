# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `8`
- Inspected trace rows: `490`
- Negative route_recovery rows: `171`
- Boundary hotspot rows: `165`
- Outside time window rows: `252`
- Map filtered traces: `5`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- High health filtered rows: `0`
- Pressure filtered rows: `0`
  - Low health risk filtered rows: `0`
  - Hazard pressure filtered rows: `0`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `163`
- Samples: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_trace_001/caramel_mid_route_recovery_samples.jsonl`

## Distributions

- Maps: `{"caramel-workshop": 163}`
- Original actions: `{"3": 111, "4": 3, "5": 45, "8": 4}`
- Target actions: `{"0": 1, "1": 63, "3": 10, "4": 3, "5": 83, "8": 3}`
- Target labels: `{"geometry_inward_non_wallward_action": 41, "highest_scored_non_wallward_action": 122}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
