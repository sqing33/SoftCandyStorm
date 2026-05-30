# Clean Risk Recovery Samples

- Decision: `risk_recovery_clean_samples_exported`
- Input samples: `264`
- Kept samples: `100`
- Dropped samples: `164`
- Output: `harness/reports/2026-05-30_rl_caramel_late_conversion_diagnostic_001/caramel_300s_late_clean_risk_samples.jsonl`
- Validation decision: `risk_recovery_samples_valid`

## Drop Reasons
- `invalid_sample`: 0
- `target_risk_reasons`: 0
- `worse_target_risk_score`: 0
- `above_max_target_risk_score`: 0
- `map_filter`: 0
- `time_window`: 164

## Kept Target Actions
- `0`: 3
- `1`: 31
- `2`: 2
- `3`: 6
- `4`: 12
- `5`: 31
- `7`: 8
- `8`: 7

## Kept Risk Reasons
- `wallward_edge`: 67
- `toward_hazard`: 30
- `toward_boss`: 3
- `toward_enemy_pressure`: 2

## Drop Examples
- `{"line": 1, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_300s_caramel-workshop.jsonl", "time_seconds": 60.0328}`
- `{"line": 2, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_300s_caramel-workshop.jsonl", "time_seconds": 66.3327}`
- `{"line": 3, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_300s_caramel-workshop.jsonl", "time_seconds": 66.366}`
- `{"line": 4, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_300s_caramel-workshop.jsonl", "time_seconds": 66.3993}`
- `{"line": 5, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_300s_caramel-workshop.jsonl", "time_seconds": 66.4327}`
- `{"line": 6, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_300s_caramel-workshop.jsonl", "time_seconds": 66.466}`
- `{"line": 7, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_300s_caramel-workshop.jsonl", "time_seconds": 66.4993}`
- `{"line": 8, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_300s_caramel-workshop.jsonl", "time_seconds": 66.5327}`
- `{"line": 9, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_300s_caramel-workshop.jsonl", "time_seconds": 66.566}`
- `{"line": 10, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_edge_branch_late_filter_high_pressure_001/chain_samples_300s_caramel-workshop.jsonl", "time_seconds": 66.5993}`

## Limitations
- Clean risk-recovery subsets are still adapter-derived repair training inputs.
- Filtering removes obvious target-risk rows; it does not prove policy quality.
- Any policy trained with this output still needs deterministic high-pressure gates and failure-case review.
