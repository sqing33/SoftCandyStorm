# Clean Risk Recovery Samples

- Decision: `risk_recovery_clean_samples_exported`
- Input samples: `162`
- Kept samples: `158`
- Dropped samples: `4`
- Output: `harness/reports/2026-05-30_rl_caramel_late_conversion_diagnostic_001/caramel_180s_mid_clean_risk_samples.jsonl`
- Validation decision: `risk_recovery_samples_valid`

## Drop Reasons
- `invalid_sample`: 0
- `target_risk_reasons`: 1
- `worse_target_risk_score`: 3
- `above_max_target_risk_score`: 0
- `map_filter`: 0
- `time_window`: 0

## Kept Target Actions
- `0`: 6
- `1`: 18
- `2`: 4
- `3`: 11
- `4`: 33
- `5`: 12
- `6`: 4
- `7`: 54
- `8`: 16

## Kept Risk Reasons
- `wallward_edge`: 72
- `toward_enemy_pressure`: 68
- `toward_hazard`: 19

## Drop Examples
- `{"line": 93, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_180s_caramel-workshop.jsonl", "target_risk_delta": 0.06299}`
- `{"line": 94, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_180s_caramel-workshop.jsonl", "target_risk_delta": 0.081772}`
- `{"line": 95, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_180s_caramel-workshop.jsonl", "target_risk_delta": 0.089818}`
- `{"line": 96, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_180s_caramel-workshop.jsonl", "target_risk_reasons": ["toward_enemy_pressure"]}`

## Limitations
- Clean risk-recovery subsets are still adapter-derived repair training inputs.
- Filtering removes obvious target-risk rows; it does not prove policy quality.
- Any policy trained with this output still needs deterministic high-pressure gates and failure-case review.
