# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `8`
- Inspected trace rows: `358`
- Negative route_recovery rows: `125`
- Boundary hotspot rows: `118`
- Outside time window rows: `163`
- Map filtered traces: `6`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- High health filtered rows: `0`
- Pressure filtered rows: `0`
  - Low health risk filtered rows: `0`
  - Hazard pressure filtered rows: `0`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `116`
- Samples: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_trace_001/cracked_mid_route_recovery_samples.jsonl`

## Distributions

- Maps: `{"cracked-star-jar": 116}`
- Original actions: `{"3": 46, "5": 65, "8": 5}`
- Target actions: `{"0": 1, "1": 88, "3": 5, "4": 3, "5": 19}`
- Target labels: `{"geometry_inward_non_wallward_action": 61, "highest_scored_non_wallward_action": 55}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
