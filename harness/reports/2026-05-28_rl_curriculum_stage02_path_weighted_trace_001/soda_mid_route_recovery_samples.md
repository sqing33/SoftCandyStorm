# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `8`
- Inspected trace rows: `789`
- Negative route_recovery rows: `241`
- Boundary hotspot rows: `233`
- Outside time window rows: `443`
- Map filtered traces: `5`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- High health filtered rows: `0`
- Pressure filtered rows: `0`
  - Low health risk filtered rows: `0`
  - Hazard pressure filtered rows: `0`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `227`
- Samples: `harness/reports/2026-05-28_rl_curriculum_stage02_path_weighted_trace_001/soda_mid_route_recovery_samples.jsonl`

## Distributions

- Maps: `{"soda-creek": 227}`
- Original actions: `{"3": 42, "5": 20, "6": 22, "8": 143}`
- Target actions: `{"0": 18, "1": 62, "2": 5, "4": 70, "5": 54, "6": 6, "7": 12}`
- Target labels: `{"geometry_inward_non_wallward_action": 98, "highest_scored_non_wallward_action": 129}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
