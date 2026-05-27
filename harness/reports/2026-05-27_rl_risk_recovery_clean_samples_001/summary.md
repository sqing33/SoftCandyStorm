# Clean Risk Recovery Samples

- Decision: `risk_recovery_clean_samples_exported`
- Input samples: `780`
- Kept samples: `702`
- Dropped samples: `78`
- Output: `harness/reports/2026-05-27_rl_risk_recovery_clean_samples_001/risk_recovery_samples_clean.jsonl`
- Validation decision: `risk_recovery_samples_valid`

## Drop Reasons
- `invalid_sample`: 0
- `target_risk_reasons`: 73
- `worse_target_risk_score`: 5
- `above_max_target_risk_score`: 0

## Behavior Clone Dry Run

- Report: `behavior_clone_dry_run.json`
- Gate decision: `dataset_validated_not_training_gate`
- Risk recovery rows: `702`
- Time phase filter: `late`, retained `702/702`
- Risk recovery time window: `180-300s`, retained `702/702`
- Recovery soft target: `top_k_scores`, soft samples `702`, fallback one-hot `0`

## Kept Target Actions
- `1`: 72
- `2`: 59
- `3`: 144
- `4`: 77
- `5`: 147
- `6`: 36
- `7`: 94
- `8`: 73

## Kept Risk Reasons
- `toward_enemy_pressure`: 368
- `toward_hazard`: 169
- `wallward_edge`: 147
- `toward_boss`: 59

## Drop Examples
- `{"line": 120, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_recovery_samples_001/risk_recovery_samples_soda-creek.jsonl", "target_risk_reasons": ["toward_enemy_pressure"]}`
- `{"line": 124, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_recovery_samples_001/risk_recovery_samples_soda-creek.jsonl", "target_risk_reasons": ["toward_enemy_pressure"]}`
- `{"line": 173, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_recovery_samples_001/risk_recovery_samples_soda-creek.jsonl", "target_risk_delta": 0.013189}`
- `{"line": 174, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_recovery_samples_001/risk_recovery_samples_soda-creek.jsonl", "target_risk_delta": 0.038882}`
- `{"line": 175, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_recovery_samples_001/risk_recovery_samples_soda-creek.jsonl", "target_risk_reasons": ["toward_enemy_pressure"]}`
- `{"line": 184, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_recovery_samples_001/risk_recovery_samples_soda-creek.jsonl", "target_risk_reasons": ["idle_under_late_pressure"]}`
- `{"line": 185, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_recovery_samples_001/risk_recovery_samples_soda-creek.jsonl", "target_risk_reasons": ["idle_under_late_pressure"]}`
- `{"line": 29, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_recovery_samples_001/risk_recovery_samples_cracked-star-jar.jsonl", "target_risk_reasons": ["idle_under_late_pressure"]}`
- `{"line": 30, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_recovery_samples_001/risk_recovery_samples_cracked-star-jar.jsonl", "target_risk_reasons": ["idle_under_late_pressure"]}`
- `{"line": 31, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_recovery_samples_001/risk_recovery_samples_cracked-star-jar.jsonl", "target_risk_reasons": ["idle_under_late_pressure"]}`

## Limitations
- Clean risk-recovery subsets are still adapter-derived repair training inputs.
- Filtering removes obvious target-risk rows; it does not prove policy quality.
- Any policy trained with this output still needs deterministic high-pressure gates and failure-case review.
