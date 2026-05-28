# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `8`
- Inspected trace rows: `3745`
- Negative route_recovery rows: `404`
- Boundary hotspot rows: `399`
- Outside time window rows: `3242`
- Map filtered traces: `0`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- High health filtered rows: `0`
- Pressure filtered rows: `0`
  - Low health risk filtered rows: `0`
  - Hazard pressure filtered rows: `0`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `395`
- Samples: `harness/reports/2026-05-28_rl_curriculum_stage02_staged_opening_fallback_trace_001/late_route_recovery_samples.jsonl`

## Distributions

- Maps: `{"caramel-workshop": 156, "cracked-star-jar": 176, "soda-creek": 63}`
- Original actions: `{"2": 184, "3": 24, "4": 178, "7": 9}`
- Target actions: `{"0": 7, "1": 19, "2": 2, "3": 8, "4": 34, "5": 74, "6": 105, "7": 43, "8": 103}`
- Target labels: `{"geometry_inward_non_wallward_action": 253, "highest_scored_non_wallward_action": 142}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
