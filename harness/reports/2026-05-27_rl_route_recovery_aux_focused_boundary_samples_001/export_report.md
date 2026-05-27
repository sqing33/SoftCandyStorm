# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `1`
- Inspected trace rows: `182`
- Negative route_recovery rows: `146`
- Boundary hotspot rows: `140`
- Missing observation rows: `0`
- Exported samples: `134`
- Samples: `harness/reports/2026-05-27_rl_route_recovery_aux_focused_boundary_samples_001/focused_boundary_samples.jsonl`

## Distributions

- Maps: `{"soda-creek": 134}`
- Original actions: `{"3": 82, "5": 52}`
- Target actions: `{"1": 7, "5": 22, "7": 63, "8": 42}`
- Target labels: `{"geometry_inward_non_wallward_action": 95, "highest_scored_non_wallward_action": 39}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
