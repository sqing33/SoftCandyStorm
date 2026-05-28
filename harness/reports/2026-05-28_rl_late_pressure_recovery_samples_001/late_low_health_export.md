# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `9`
- Inspected trace rows: `966`
- Negative route_recovery rows: `42`
- Boundary hotspot rows: `42`
- Outside time window rows: `922`
- Map filtered traces: `0`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- High health filtered rows: `0`
- Pressure filtered rows: `35`
  - Low health risk filtered rows: `35`
  - Hazard pressure filtered rows: `0`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `7`
- Samples: `harness/reports/2026-05-28_rl_late_pressure_recovery_samples_001/late_low_health_recovery_samples.jsonl`

## Distributions

- Maps: `{"cracked-star-jar": 7}`
- Original actions: `{"4": 7}`
- Target actions: `{"8": 7}`
- Target labels: `{"geometry_inward_non_wallward_action": 7}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
