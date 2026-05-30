# Clean Risk Recovery Samples

- Decision: `risk_recovery_clean_samples_exported`
- Input samples: `1806`
- Kept samples: `634`
- Dropped samples: `1172`
- Output: `harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_late_clean_risk_samples.jsonl`
- Validation decision: `risk_recovery_samples_valid`

## Drop Reasons
- `invalid_sample`: 0
- `target_risk_reasons`: 26
- `worse_target_risk_score`: 1
- `above_max_target_risk_score`: 0
- `map_filter`: 0
- `time_window`: 1145

## Kept Target Actions
- `0`: 11
- `1`: 95
- `2`: 33
- `3`: 63
- `4`: 98
- `5`: 67
- `6`: 31
- `7`: 132
- `8`: 104

## Kept Risk Reasons
- `toward_enemy_pressure`: 248
- `toward_hazard`: 208
- `wallward_edge`: 188
- `toward_boss`: 30

## Drop Examples
- `{"line": 1, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "time_seconds": 60.0328}`
- `{"line": 2, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "time_seconds": 66.3327}`
- `{"line": 3, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "time_seconds": 66.366}`
- `{"line": 4, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "time_seconds": 66.3993}`
- `{"line": 5, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "time_seconds": 66.4327}`
- `{"line": 6, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "time_seconds": 66.466}`
- `{"line": 7, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "time_seconds": 66.4993}`
- `{"line": 8, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "time_seconds": 66.5327}`
- `{"line": 9, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "time_seconds": 66.566}`
- `{"line": 10, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_branch_late_all_high_pressure_001/caramel_branch_late_all_risk_samples.jsonl", "time_seconds": 66.5993}`

## Limitations
- Clean risk-recovery subsets are still adapter-derived repair training inputs.
- Filtering removes obvious target-risk rows; it does not prove policy quality.
- Any policy trained with this output still needs deterministic high-pressure gates and failure-case review.
