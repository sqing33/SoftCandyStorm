# Clean Risk Recovery Samples

- Decision: `risk_recovery_clean_samples_exported`
- Input samples: `1806`
- Kept samples: `1139`
- Dropped samples: `667`
- Output: `harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_mid_clean_risk_samples.jsonl`
- Validation decision: `risk_recovery_samples_valid`

## Drop Reasons
- `invalid_sample`: 0
- `target_risk_reasons`: 1
- `worse_target_risk_score`: 5
- `above_max_target_risk_score`: 0
- `map_filter`: 0
- `time_window`: 661

## Kept Target Actions
- `0`: 36
- `1`: 126
- `2`: 39
- `3`: 110
- `4`: 180
- `5`: 126
- `6`: 47
- `7`: 413
- `8`: 62

## Kept Risk Reasons
- `toward_enemy_pressure`: 551
- `wallward_edge`: 524
- `toward_hazard`: 75

## Drop Examples
- `{"line": 93, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "target_risk_delta": 0.06299}`
- `{"line": 94, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "target_risk_delta": 0.081772}`
- `{"line": 95, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "target_risk_delta": 0.089818}`
- `{"line": 96, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "target_risk_reasons": ["toward_enemy_pressure"]}`
- `{"line": 723, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "target_risk_delta": 0.191435}`
- `{"line": 768, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "time_seconds": 180.5429}`
- `{"line": 769, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "time_seconds": 184.1104}`
- `{"line": 770, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "time_seconds": 184.5104}`
- `{"line": 771, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "time_seconds": 184.5438}`
- `{"line": 772, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "time_seconds": 184.5771}`

## Limitations
- Clean risk-recovery subsets are still adapter-derived repair training inputs.
- Filtering removes obvious target-risk rows; it does not prove policy quality.
- Any policy trained with this output still needs deterministic high-pressure gates and failure-case review.
