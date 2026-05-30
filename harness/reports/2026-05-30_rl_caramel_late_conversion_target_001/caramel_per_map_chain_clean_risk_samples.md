# Clean Risk Recovery Samples

- Decision: `risk_recovery_clean_samples_exported`
- Input samples: `374`
- Kept samples: `164`
- Dropped samples: `210`
- Output: `harness/reports/2026-05-30_rl_caramel_late_conversion_target_001/caramel_per_map_chain_clean_risk_samples.jsonl`
- Validation decision: `risk_recovery_samples_valid`

## Drop Reasons
- `invalid_sample`: 1
- `target_risk_reasons`: 0
- `worse_target_risk_score`: 0
- `above_max_target_risk_score`: 0
- `map_filter`: 0
- `time_window`: 209

## Kept Target Actions
- `0`: 3
- `1`: 38
- `2`: 3
- `3`: 10
- `4`: 17
- `5`: 33
- `6`: 6
- `7`: 42
- `8`: 12

## Kept Risk Reasons
- `wallward_edge`: 102
- `toward_hazard`: 54
- `toward_enemy_pressure`: 7
- `toward_boss`: 3

## Drop Examples
- `{"line": 1, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_late_conversion_target_001/caramel_per_map_chain_risk_samples.jsonl", "time_seconds": 60.0328}`
- `{"line": 2, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_late_conversion_target_001/caramel_per_map_chain_risk_samples.jsonl", "time_seconds": 66.3327}`
- `{"line": 3, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_late_conversion_target_001/caramel_per_map_chain_risk_samples.jsonl", "time_seconds": 66.366}`
- `{"line": 4, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_late_conversion_target_001/caramel_per_map_chain_risk_samples.jsonl", "time_seconds": 66.3993}`
- `{"line": 5, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_late_conversion_target_001/caramel_per_map_chain_risk_samples.jsonl", "time_seconds": 66.4327}`
- `{"line": 6, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_late_conversion_target_001/caramel_per_map_chain_risk_samples.jsonl", "time_seconds": 66.466}`
- `{"line": 7, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_late_conversion_target_001/caramel_per_map_chain_risk_samples.jsonl", "time_seconds": 66.4993}`
- `{"line": 8, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_late_conversion_target_001/caramel_per_map_chain_risk_samples.jsonl", "time_seconds": 66.5327}`
- `{"line": 9, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_late_conversion_target_001/caramel_per_map_chain_risk_samples.jsonl", "time_seconds": 66.566}`
- `{"line": 10, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_late_conversion_target_001/caramel_per_map_chain_risk_samples.jsonl", "time_seconds": 66.5993}`

## Limitations
- Clean risk-recovery subsets are still adapter-derived repair training inputs.
- Filtering removes obvious target-risk rows; it does not prove policy quality.
- Any policy trained with this output still needs deterministic high-pressure gates and failure-case review.
