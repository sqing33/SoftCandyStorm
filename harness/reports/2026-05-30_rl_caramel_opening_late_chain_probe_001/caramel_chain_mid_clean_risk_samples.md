# Clean Risk Recovery Samples

- Decision: `risk_recovery_clean_samples_exported`
- Input samples: `373`
- Kept samples: `207`
- Dropped samples: `166`
- Output: `harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/caramel_chain_mid_clean_risk_samples.jsonl`
- Validation decision: `risk_recovery_samples_valid`

## Drop Reasons
- `invalid_sample`: 0
- `target_risk_reasons`: 0
- `worse_target_risk_score`: 2
- `above_max_target_risk_score`: 0
- `map_filter`: 0
- `time_window`: 164

## Kept Target Actions
- `0`: 6
- `1`: 21
- `2`: 3
- `3`: 20
- `4`: 54
- `5`: 18
- `6`: 4
- `7`: 70
- `8`: 11

## Kept Risk Reasons
- `wallward_edge`: 83
- `toward_enemy_pressure`: 81
- `toward_hazard`: 49

## Drop Examples
- `{"line": 69, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/caramel_chain_risk_samples_300s.jsonl", "target_risk_delta": 0.191435}`
- `{"line": 114, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/caramel_chain_risk_samples_300s.jsonl", "time_seconds": 180.5429}`
- `{"line": 115, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/caramel_chain_risk_samples_300s.jsonl", "time_seconds": 184.1104}`
- `{"line": 116, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/caramel_chain_risk_samples_300s.jsonl", "time_seconds": 184.5104}`
- `{"line": 117, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/caramel_chain_risk_samples_300s.jsonl", "time_seconds": 184.5438}`
- `{"line": 118, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/caramel_chain_risk_samples_300s.jsonl", "time_seconds": 184.5771}`
- `{"line": 119, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/caramel_chain_risk_samples_300s.jsonl", "time_seconds": 184.6105}`
- `{"line": 120, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/caramel_chain_risk_samples_300s.jsonl", "time_seconds": 184.7772}`
- `{"line": 121, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/caramel_chain_risk_samples_300s.jsonl", "time_seconds": 184.8105}`
- `{"line": 122, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_caramel_opening_late_chain_probe_001/caramel_chain_risk_samples_300s.jsonl", "time_seconds": 184.8439}`

## Limitations
- Clean risk-recovery subsets are still adapter-derived repair training inputs.
- Filtering removes obvious target-risk rows; it does not prove policy quality.
- Any policy trained with this output still needs deterministic high-pressure gates and failure-case review.
