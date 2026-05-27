# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `15`
- Inspected trace rows: `2182`
- Negative route_recovery rows: `218`
- Boundary hotspot rows: `194`
- Outside time window rows: `1767`
- Map filtered traces: `10`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `190`
- Samples: `harness/reports/2026-05-27_rl_late_boundary_handoff_cracked_star_samples_001/cracked_star_handoff_60_90_recovery_samples.jsonl`

## Distributions

- Maps: `{"cracked-star-jar": 190}`
- Original actions: `{"2": 88, "3": 86, "8": 16}`
- Target actions: `{"1": 34, "3": 29, "6": 41, "7": 86}`
- Target labels: `{"geometry_inward_non_wallward_action": 127, "highest_scored_non_wallward_action": 63}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
