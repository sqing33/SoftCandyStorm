# RL Rule Bot Late Survival Trajectory Export

- Decision: `late_survival_trajectory_dataset_dry_run_valid`
- Scope: 真实规则 Bot `180-300s` late-window 轨迹导出与 behavior clone dry-run
- Dataset records: `12007` movement samples
- Episodes represented: `31`
- Observation: v2, len `145`
- Sample stride: `5`
- Source type: `trajectory` only

## Boundary

本报告只证明 late-window 规则 Bot 轨迹已经导出，并且 `train_behavior_clone.py --dry-run` 可以读取这些样本。它不是训练结果、不是 RL policy gate、不是 seeded stochastic watch 通过，也不是 acceptance evidence。

`rl_policy_multimap_generalization_gap` 仍然存在。任何后续 late repair 模型仍必须重新通过 deterministic high-pressure `60s / 180s / 300s` 多图对比，才能讨论 stage 03 或 RL 测试 Bot 候选。

## Exported Files

| File | Bot | Map | Seeds | Samples | Victories |
|---|---|---|---:|---:|---:|
| `kite_soda_creek_late_180_300.jsonl` | `kite` | `soda-creek` | 5 | 3128 | 4 |
| `kite_cracked_star_jar_late_180_300.jsonl` | `kite` | `cracked-star-jar` | 5 | 2276 | 2 |
| `tank_caramel_workshop_seed62301_late_180_300.jsonl` | `tank` | `caramel-workshop` | 1 | 720 | 1 |
| `greedy_cracked_star_jar_late_180_300.jsonl` | `greedy` | `cracked-star-jar` | 5 | 1551 | 0 |
| `greedy_caramel_workshop_late_180_300.jsonl` | `greedy` | `caramel-workshop` | 5 | 1360 | 0 |
| `coward_caramel_workshop_seed62300_62303_late_180_300.jsonl` | `coward` | `caramel-workshop` | 4 | 1202 | 0 |
| `route_caramel_workshop_late_180_300.jsonl` | `route` | `caramel-workshop` | 5 | 1050 | 0 |
| `greedy_soda_creek_seed62302_late_180_300.jsonl` | `greedy` | `soda-creek` | 1 | 720 | 1 |

The clean primary teacher subset is `kite` on `soda-creek`, `kite` on `cracked-star-jar`, and `tank` seed `62301` on `caramel-workshop`. The `greedy`, `coward`, and `route` files are non-random contrast data for late pressure and near-failure states.

## Dry Run

`python3 python/train/train_behavior_clone.py --dataset harness/reports/2026-05-27_rl_rule_bot_late_survival_trajectory_001 --dry-run --architecture gru --context-frames 8 --map-conditioning one_hot --time-phase-conditioning one_hot --time-phase-filter late --report harness/reports/2026-05-27_rl_rule_bot_late_survival_trajectory_001/behavior_clone_dry_run_late.json`

Key results:

- `sample_count`: `12007`
- `phase_distribution`: `late = 100%`
- `map_distribution`: `caramel-workshop 36.08%`, `cracked-star-jar 31.87%`, `soda-creek 32.05%`
- `late_low_health_ratio`: `50.04%`
- `sample_source_distribution`: `trajectory = 100%`
- `edge_recovery_sample_records`: `0`
- `risk_recovery_sample_records`: `0`
- `action_distribution`: largest action ratio is action `3` at `15.16%`
- `diagnosis_flags`: `high_action_persistence` watch

## Next Validation

1. Decide whether the first late model trains on clean teacher only or clean plus contrast samples.
2. Train a late submodel with explicit dataset mix reporting.
3. Package with the existing opening / mid strategy only if the new late checkpoint passes dry-run and training diagnostics.
4. Re-run deterministic high-pressure `60s`, `180s`, and `300s` comparisons before any stage 03 or acceptance decision.
