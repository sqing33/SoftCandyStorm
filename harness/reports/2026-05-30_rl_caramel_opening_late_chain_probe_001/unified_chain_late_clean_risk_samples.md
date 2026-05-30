# Clean Risk Recovery Samples

- Decision: `risk_recovery_clean_samples_exported`
- Input samples: `2165`
- Kept samples: `727`
- Dropped samples: `1438`
- Output: `harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_late_clean_risk_samples.jsonl`
- Validation decision: `risk_recovery_samples_valid`

## Drop Reasons
- `invalid_sample`: 0
- `target_risk_reasons`: 27
- `worse_target_risk_score`: 3
- `above_max_target_risk_score`: 0
- `map_filter`: 0
- `time_window`: 1408

## Kept Target Actions
- `0`: 10
- `1`: 103
- `2`: 44
- `3`: 76
- `4`: 103
- `5`: 80
- `6`: 36
- `7`: 161
- `8`: 114

## Kept Risk Reasons
- `toward_enemy_pressure`: 304
- `wallward_edge`: 218
- `toward_hazard`: 207
- `toward_boss`: 36

## Drop Examples
- `{"line": 1, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_risk_samples.jsonl", "time_seconds": 60.0328}`
- `{"line": 2, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_risk_samples.jsonl", "time_seconds": 66.3327}`
- `{"line": 3, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_risk_samples.jsonl", "time_seconds": 66.366}`
- `{"line": 4, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_risk_samples.jsonl", "time_seconds": 66.3993}`
- `{"line": 5, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_risk_samples.jsonl", "time_seconds": 66.4327}`
- `{"line": 6, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_risk_samples.jsonl", "time_seconds": 66.466}`
- `{"line": 7, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_risk_samples.jsonl", "time_seconds": 66.4993}`
- `{"line": 8, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_risk_samples.jsonl", "time_seconds": 66.5327}`
- `{"line": 9, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_risk_samples.jsonl", "time_seconds": 66.566}`
- `{"line": 10, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/unified_chain_risk_samples.jsonl", "time_seconds": 66.5993}`

## Limitations
- Clean risk-recovery subsets are still adapter-derived repair training inputs.
- Filtering removes obvious target-risk rows; it does not prove policy quality.
- Any policy trained with this output still needs deterministic high-pressure gates and failure-case review.
