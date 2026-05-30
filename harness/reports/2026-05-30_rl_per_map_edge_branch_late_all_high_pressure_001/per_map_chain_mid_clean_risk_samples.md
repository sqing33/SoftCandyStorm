# Clean Risk Recovery Samples

- Decision: `risk_recovery_clean_samples_exported`
- Input samples: `2184`
- Kept samples: `1360`
- Dropped samples: `824`
- Output: `harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_mid_clean_risk_samples.jsonl`
- Validation decision: `risk_recovery_samples_valid`

## Drop Reasons
- `invalid_sample`: 0
- `target_risk_reasons`: 4
- `worse_target_risk_score`: 5
- `above_max_target_risk_score`: 0
- `map_filter`: 0
- `time_window`: 815

## Kept Target Actions
- `0`: 39
- `1`: 115
- `2`: 23
- `3`: 114
- `4`: 267
- `5`: 158
- `6`: 35
- `7`: 527
- `8`: 82

## Kept Risk Reasons
- `wallward_edge`: 678
- `toward_enemy_pressure`: 619
- `toward_hazard`: 75

## Drop Examples
- `{"line": 93, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_risk_samples.jsonl", "target_risk_delta": 0.06299}`
- `{"line": 94, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_risk_samples.jsonl", "target_risk_delta": 0.081772}`
- `{"line": 95, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_risk_samples.jsonl", "target_risk_delta": 0.089818}`
- `{"line": 96, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_risk_samples.jsonl", "target_risk_reasons": ["toward_enemy_pressure"]}`
- `{"line": 498, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_risk_samples.jsonl", "target_risk_reasons": ["idle_under_late_pressure"]}`
- `{"line": 499, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_risk_samples.jsonl", "target_risk_reasons": ["idle_under_late_pressure"]}`
- `{"line": 500, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_risk_samples.jsonl", "target_risk_reasons": ["idle_under_late_pressure"]}`
- `{"line": 822, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_risk_samples.jsonl", "target_risk_delta": 0.191435}`
- `{"line": 867, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_risk_samples.jsonl", "time_seconds": 180.5429}`
- `{"line": 868, "reason": "time_window", "source": "harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/per_map_chain_risk_samples.jsonl", "time_seconds": 184.1104}`

## Limitations
- Clean risk-recovery subsets are still adapter-derived repair training inputs.
- Filtering removes obvious target-risk rows; it does not prove policy quality.
- Any policy trained with this output still needs deterministic high-pressure gates and failure-case review.
