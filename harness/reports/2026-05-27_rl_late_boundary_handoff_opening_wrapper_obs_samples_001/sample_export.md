# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `15`
- Inspected trace rows: `6843`
- Negative route_recovery rows: `789`
- Boundary hotspot rows: `743`
- Outside time window rows: `5528`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `713`
- Samples: `harness/reports/2026-05-27_rl_late_boundary_handoff_opening_wrapper_obs_samples_001/handoff_60_90_recovery_samples.jsonl`

## Distributions

- Maps: `{"caramel-workshop": 253, "cracked-star-jar": 190, "soda-creek": 270}`
- Original actions: `{"1": 50, "2": 107, "3": 213, "8": 343}`
- Target actions: `{"0": 111, "1": 150, "2": 5, "3": 55, "4": 134, "5": 1, "6": 48, "7": 159, "8": 50}`
- Target labels: `{"geometry_inward_non_wallward_action": 338, "highest_scored_non_wallward_action": 375}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
