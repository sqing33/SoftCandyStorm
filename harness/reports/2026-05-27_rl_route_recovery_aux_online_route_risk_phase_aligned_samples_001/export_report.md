# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `3`
- Inspected trace rows: `340`
- Negative route_recovery rows: `143`
- Boundary hotspot rows: `143`
- Outside time window rows: `180`
- Missing observation rows: `0`
- Exported samples: `143`
- Samples: `harness/reports/2026-05-27_rl_route_recovery_aux_online_route_risk_phase_aligned_samples_001/online_route_risk_phase_aligned_samples.jsonl`

## Distributions

- Maps: `{"soda-creek": 143}`
- Original actions: `{"1": 23, "5": 41, "6": 79}`
- Target actions: `{"1": 17, "2": 102, "3": 16, "5": 7, "7": 1}`
- Target labels: `{"geometry_inward_non_wallward_action": 126, "highest_scored_non_wallward_action": 17}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
