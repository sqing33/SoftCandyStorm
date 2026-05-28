# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `8`
- Inspected trace rows: `789`
- Negative route_recovery rows: `54`
- Boundary hotspot rows: `51`
- Outside time window rows: `709`
- Map filtered traces: `5`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- High health filtered rows: `0`
- Pressure filtered rows: `0`
  - Low health risk filtered rows: `0`
  - Hazard pressure filtered rows: `0`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `50`
- Samples: `harness/reports/2026-05-28_rl_curriculum_stage02_path_weighted_trace_001/soda_late_route_recovery_samples.jsonl`

## Distributions

- Maps: `{"soda-creek": 50}`
- Original actions: `{"5": 15, "8": 35}`
- Target actions: `{"1": 21, "4": 29}`
- Target labels: `{"geometry_inward_non_wallward_action": 44, "highest_scored_non_wallward_action": 6}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
