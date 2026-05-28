# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_unavailable`
- Source traces: `9`
- Inspected trace rows: `966`
- Negative route_recovery rows: `42`
- Boundary hotspot rows: `42`
- Outside time window rows: `922`
- Map filtered traces: `0`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- High health filtered rows: `0`
- Pressure filtered rows: `42`
  - Low health risk filtered rows: `0`
  - Hazard pressure filtered rows: `42`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `0`
- Samples: `harness/reports/2026-05-28_rl_late_pressure_recovery_samples_001/late_hazard_recovery_samples.jsonl`

## Distributions

- Maps: `{}`
- Original actions: `{}`
- Target actions: `{}`
- Target labels: `{}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned negative route_recovery hotspots, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.
