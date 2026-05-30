# Clean Risk Recovery Samples

- Decision: `risk_recovery_clean_samples_exported`
- Input samples: `610`
- Kept samples: `440`
- Dropped samples: `170`
- Output: `harness/reports/2026-05-30_rl_late_recovery_map_scope_high_pressure_001/scoped_chain_mid_clean_risk_samples.jsonl`
- Validation decision: `risk_recovery_samples_valid`

## Drop Reasons
- `invalid_sample`: 0
- `target_risk_reasons`: 1
- `worse_target_risk_score`: 5
- `above_max_target_risk_score`: 0
- `map_filter`: 0
- `time_window`: 164

## Kept Target Actions
- `0`: 15
- `1`: 42
- `2`: 7
- `3`: 38
- `4`: 93
- `5`: 67
- `6`: 12
- `7`: 135
- `8`: 31

## Kept Risk Reasons
- `wallward_edge`: 202
- `toward_enemy_pressure`: 172
- `toward_hazard`: 75

## Drop Examples
- `{"line": 93, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-30_rl_late_recovery_map_scope_high_pressure_001/scoped_chain_risk_samples.jsonl", "target_risk_delta": 0.06299}`
- `{"line": 94, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-30_rl_late_recovery_map_scope_high_pressure_001/scoped_chain_risk_samples.jsonl", "target_risk_delta": 0.081772}`
- `{"line": 95, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-30_rl_late_recovery_map_scope_high_pressure_001/scoped_chain_risk_samples.jsonl", "target_risk_delta": 0.089818}`
- `{"line": 96, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-30_rl_late_recovery_map_scope_high_pressure_001/scoped_chain_risk_samples.jsonl", "target_risk_reasons": ["toward_enemy_pressure"]}`
- `{"line": 306, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-30_rl_late_recovery_map_scope_high_pressure_001/scoped_chain_risk_samples.jsonl", "target_risk_delta": 0.191435}`
- `{"line": 351, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_late_recovery_map_scope_high_pressure_001/scoped_chain_risk_samples.jsonl", "time_seconds": 180.5429}`
- `{"line": 352, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_late_recovery_map_scope_high_pressure_001/scoped_chain_risk_samples.jsonl", "time_seconds": 184.1104}`
- `{"line": 353, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_late_recovery_map_scope_high_pressure_001/scoped_chain_risk_samples.jsonl", "time_seconds": 184.5104}`
- `{"line": 354, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_late_recovery_map_scope_high_pressure_001/scoped_chain_risk_samples.jsonl", "time_seconds": 184.5438}`
- `{"line": 355, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_late_recovery_map_scope_high_pressure_001/scoped_chain_risk_samples.jsonl", "time_seconds": 184.5771}`

## Limitations
- Clean risk-recovery subsets are still adapter-derived repair training inputs.
- Filtering removes obvious target-risk rows; it does not prove policy quality.
- Any policy trained with this output still needs deterministic high-pressure gates and failure-case review.
