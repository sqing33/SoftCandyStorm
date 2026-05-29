# Clean Risk Recovery Samples

- Decision: `risk_recovery_clean_samples_exported`
- Input samples: `439`
- Kept samples: `424`
- Dropped samples: `15`
- Output: `harness/reports/2026-05-29_rl_sb3_parent_late_recovery_clean_samples_001/risk_recovery_samples_clean.jsonl`
- Validation decision: `risk_recovery_samples_valid`

## Drop Reasons
- `invalid_sample`: 0
- `target_risk_reasons`: 14
- `worse_target_risk_score`: 1
- `above_max_target_risk_score`: 0

## Kept Target Actions
- `0`: 10
- `1`: 52
- `2`: 13
- `3`: 43
- `4`: 74
- `5`: 56
- `6`: 26
- `7`: 77
- `8`: 73

## Kept Risk Reasons
- `wallward_edge`: 168
- `toward_enemy_pressure`: 159
- `toward_hazard`: 124
- `toward_boss`: 6

## Drop Examples
- `{"line": 69, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_filter_probe_001/late_recovery_samples/soda-creek_edge_recovery_samples.jsonl", "target_risk_reasons": ["toward_boss"]}`
- `{"line": 113, "reason": "worse_target_risk_score", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_filter_probe_001/late_recovery_samples/soda-creek_edge_recovery_samples.jsonl", "target_risk_delta": 0.039592}`
- `{"line": 50, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_filter_probe_001/late_recovery_samples/cracked-star-jar_edge_recovery_samples.jsonl", "target_risk_reasons": ["toward_enemy_pressure"]}`
- `{"line": 52, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_filter_probe_001/late_recovery_samples/cracked-star-jar_edge_recovery_samples.jsonl", "target_risk_reasons": ["toward_enemy_pressure"]}`
- `{"line": 54, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_filter_probe_001/late_recovery_samples/cracked-star-jar_edge_recovery_samples.jsonl", "target_risk_reasons": ["toward_enemy_pressure"]}`
- `{"line": 56, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_filter_probe_001/late_recovery_samples/cracked-star-jar_edge_recovery_samples.jsonl", "target_risk_reasons": ["toward_enemy_pressure"]}`
- `{"line": 77, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_filter_probe_001/late_recovery_samples/cracked-star-jar_edge_recovery_samples.jsonl", "target_risk_reasons": ["toward_enemy_pressure"]}`
- `{"line": 79, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_filter_probe_001/late_recovery_samples/cracked-star-jar_edge_recovery_samples.jsonl", "target_risk_reasons": ["toward_enemy_pressure"]}`
- `{"line": 99, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_filter_probe_001/late_recovery_samples/cracked-star-jar_edge_recovery_samples.jsonl", "target_risk_reasons": ["idle_under_late_pressure"]}`
- `{"line": 100, "reason": "target_risk_reasons", "source": "harness/reports/2026-05-29_rl_sb3_parent_late_recovery_filter_probe_001/late_recovery_samples/cracked-star-jar_edge_recovery_samples.jsonl", "target_risk_reasons": ["idle_under_late_pressure"]}`

## Limitations
- Clean risk-recovery subsets are still adapter-derived repair training inputs.
- Filtering removes obvious target-risk rows; it does not prove policy quality.
- Any policy trained with this output still needs deterministic high-pressure gates and failure-case review.

## Behavior Clone Dry-run

`behavior_clone_dry_run.json` 验证 clean subset 可以作为 late-window repair training input 被当前监督训练入口读取：

- gate decision: `dataset_validated_not_training_gate`
- dataset samples: `424`
- observation len: `145`
- action count: `9`
- risk recovery sample records: `424`
- time phase filter: `late`, retained `424/424`
- risk recovery time window: `180-300s`, retained `424/424`
- risk recovery sample weight: `0.5`
- recovery soft target: `top_k_scores`
- soft sample count: `424`
- fallback one-hot count: `0`
- average nonzero actions: `2.4906`

该 dry-run 只证明数据能进入训练链路，不训练模型，也不构成 policy gate。

## Follow-up Constraints

- `cracked-star-jar` 占 clean samples 的 `49.53%`，存在 map sample imbalance，后续训练需要 map-conditioned 检查或按地图调权。
- `late_low_health` coverage 为 `0`，不能把这批样本当成低血量恢复的完整监督信号。
- 下一步若训练 action-separation / terminal-conversion branch，应混入 parent / e30 retention anchors，并继续跑 required multibaseline no-regression。
