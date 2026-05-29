# Clean Risk Recovery Samples

- Decision: `risk_recovery_clean_samples_exported`
- Input samples: `424`
- Kept samples: `210`
- Dropped samples: `214`
- Output: `harness/reports/2026-05-29_rl_sb3_risk_recovery_cracked_late_scope_samples_001/risk_recovery_samples_cracked_late.jsonl`
- Validation decision: `risk_recovery_samples_valid`

## Drop Reasons
- `invalid_sample`: 0
- `target_risk_reasons`: 0
- `worse_target_risk_score`: 0
- `above_max_target_risk_score`: 0
- `map_filter`: 214
- `time_window`: 0

## Kept Target Actions
- `0`: 1
- `1`: 31
- `2`: 5
- `3`: 17
- `4`: 45
- `5`: 14
- `6`: 19
- `7`: 45
- `8`: 33

## Kept Risk Reasons
- `toward_enemy_pressure`: 90
- `wallward_edge`: 69
- `toward_hazard`: 66
- `toward_boss`: 2

## Drop Examples
- `{"line": 1, "map_id": "soda-creek", "reason": "map_filter", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_clean_samples_001/risk_recovery_samples_clean.jsonl"}`
- `{"line": 2, "map_id": "soda-creek", "reason": "map_filter", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_clean_samples_001/risk_recovery_samples_clean.jsonl"}`
- `{"line": 3, "map_id": "soda-creek", "reason": "map_filter", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_clean_samples_001/risk_recovery_samples_clean.jsonl"}`
- `{"line": 4, "map_id": "soda-creek", "reason": "map_filter", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_clean_samples_001/risk_recovery_samples_clean.jsonl"}`
- `{"line": 5, "map_id": "soda-creek", "reason": "map_filter", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_clean_samples_001/risk_recovery_samples_clean.jsonl"}`
- `{"line": 6, "map_id": "soda-creek", "reason": "map_filter", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_clean_samples_001/risk_recovery_samples_clean.jsonl"}`
- `{"line": 7, "map_id": "soda-creek", "reason": "map_filter", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_clean_samples_001/risk_recovery_samples_clean.jsonl"}`
- `{"line": 8, "map_id": "soda-creek", "reason": "map_filter", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_clean_samples_001/risk_recovery_samples_clean.jsonl"}`
- `{"line": 9, "map_id": "soda-creek", "reason": "map_filter", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_clean_samples_001/risk_recovery_samples_clean.jsonl"}`
- `{"line": 10, "map_id": "soda-creek", "reason": "map_filter", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_clean_samples_001/risk_recovery_samples_clean.jsonl"}`

## Limitations
- Clean risk-recovery subsets are still adapter-derived repair training inputs.
- Filtering removes obvious target-risk rows; it does not prove policy quality.
- Any policy trained with this output still needs deterministic high-pressure gates and failure-case review.
