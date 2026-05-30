# Route Recovery Supervision Samples

- Decision: `route_recovery_samples_exported`
- Source traces: `1`
- Inspected trace rows: `113`
- Negative route_recovery rows: `4`
- Route recovery filter: `any`
- Route recovery matched rows: `17`
- Boundary hotspot rows: `17`
- Outside time window rows: `96`
- Map filtered traces: `0`
- Original action filtered rows: `0`
- Low health filtered rows: `0`
- High health filtered rows: `0`
- Pressure filtered rows: `0`
  - Enemy pressure filtered rows: `0`
  - Low health risk filtered rows: `0`
  - Hazard pressure filtered rows: `0`
  - Boss pressure filtered rows: `0`
- Missing observation rows: `0`
- Exported samples: `17`
- Samples: `harness/reports/2026-05-30_rl_stage01_seed63402_target_guard_samples_001/seed63402_target_guard_samples.jsonl`

## Distributions

- Maps: `{"soda-creek": 17}`
- Original actions: `{"5": 17}`
- Target actions: `{"7": 17}`
- Target labels: `{"preferred_non_wallward_action": 17}`

## Limitations

- Samples are extracted only from sampled trace rows that include observation vectors.
- The export targets boundary-pinned rows matching the requested time, pressure, action, and map filters, not all unsafe movement.
- A successful export is repair training material, not RL policy acceptance.

## Follow-up Validation

- `sample_validation.json`: `edge_recovery_samples_valid`, `17` samples, no errors or warnings.
- `behavior_clone_dry_run.json`: `dataset_validated_not_training_gate`, `17` samples read as `edge_recovery_supervision`, observation length `145`, target action distribution `{"7": 17}`.
- These checks only prove the repair rows are structurally usable; the next policy still needs deterministic high-pressure 60 / 180 / 300 second parent no-regression.
