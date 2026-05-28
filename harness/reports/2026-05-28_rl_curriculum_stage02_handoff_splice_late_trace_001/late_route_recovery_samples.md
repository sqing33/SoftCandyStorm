# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `9`
- Inspected trace rows: `1686`
- Negative route_recovery rows: `226`
- Boundary hotspot rows: `210`
- Outside time window rows: `1374`
- Map filtered traces: `0`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- High health filtered rows: `0`
- Pressure filtered rows: `0`
  - Low health risk filtered rows: `0`
  - Hazard pressure filtered rows: `0`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `207`
- Samples: `harness/reports/2026-05-28_rl_curriculum_stage02_handoff_splice_late_trace_001/late_route_recovery_samples.jsonl`

## Distributions

- Maps: `{"caramel-workshop": 61, "cracked-star-jar": 103, "soda-creek": 43}`
- Original actions: `{"3": 106, "4": 1, "5": 78, "8": 22}`
- Target actions: `{"0": 9, "1": 129, "3": 9, "4": 5, "5": 44, "7": 10, "8": 1}`
- Target labels: `{"geometry_inward_non_wallward_action": 74, "highest_scored_non_wallward_action": 133}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
