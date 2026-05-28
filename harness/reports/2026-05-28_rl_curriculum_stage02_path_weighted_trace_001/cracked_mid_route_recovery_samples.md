# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `8`
- Inspected trace rows: `602`
- Negative route_recovery rows: `211`
- Boundary hotspot rows: `205`
- Outside time window rows: `312`
- Map filtered traces: `6`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- High health filtered rows: `0`
- Pressure filtered rows: `0`
  - Low health risk filtered rows: `0`
  - Hazard pressure filtered rows: `0`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `202`
- Samples: `harness/reports/2026-05-28_rl_curriculum_stage02_path_weighted_trace_001/cracked_mid_route_recovery_samples.jsonl`

## Distributions

- Maps: `{"cracked-star-jar": 202}`
- Original actions: `{"3": 42, "5": 30, "8": 130}`
- Target actions: `{"0": 37, "1": 14, "2": 30, "4": 53, "5": 28, "7": 40}`
- Target labels: `{"geometry_inward_non_wallward_action": 85, "highest_scored_non_wallward_action": 117}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
