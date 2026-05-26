# RL Time-Phase Balance Curriculum Full Candidate

## 结论

`time_phase_balance_danger_action_change` GRU context8 完整候选改善了旧 movement policy 的动作分布：60 秒 high-pressure 三图无 finding，300 秒三图的 action distribution inner gate 也全部通过。但 300 秒总 gate 仍为 `multimap_comparison_recorded_needs_policy_repair`，因为 `soda-creek` 胜率为 0%，另外两图低于规则 Bot 基线。

对应 failure case：`harness/failed_cases/fail_20260527_015_time_phase_balance_soda_longrun_gap.json`。

## 训练

- Dataset: `harness/reports/2026-05-27_rl_rule_bot_trajectory_phase_aligned_001`
- Model: `time_phase_balance_curriculum_full.pt`
- Architecture: `gru`
- Context frames: `8`
- Hidden size: `128`
- Epochs: `20`
- Map conditioning: `one_hot`
- Time phase conditioning: `one_hot`
- Sample weighting: `time_phase_balance_danger_action_change`
- Final validation accuracy: `0.8493`
- Final validation entropy: `0.483741`

## Phase Multipliers

| Phase | Train Samples | Ratio | Multiplier |
|---|---:|---:|---:|
| `opening` | 4275 | 0.2460 | 1.355244 |
| `mid` | 7953 | 0.4576 | 0.728488 |
| `late` | 5153 | 0.2965 | 1.124329 |

## 60 秒对比

命令输出：`comparison_60s.json`

| Map | Policy Win Rate | Avg Survival | Normalized Entropy | Dominant Action | Rule Bot Best |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.8 | 55.6462 | 0.7814 | `3` / 35.17% | 1.0 |
| `caramel-workshop` | 0.8 | 56.0128 | 0.8872 | `8` / 23.54% | 1.0 |
| `cracked-star-jar` | 1.0 | 60.0328 | 0.5597 | `3` / 53.47% | 1.0 |

60 秒 gate 为 `multimap_comparison_recorded_not_balance_gate`，没有 action distribution finding。

## 300 秒对比

命令输出：`comparison_300s.json`

| Map | Policy Win Rate | Avg Survival | Normalized Entropy | Dominant Action | Rule Bot Best |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 120.6072 | 0.6710 | `3` / 41.29% | 1.0 |
| `caramel-workshop` | 0.3333 | 242.5828 | 0.8383 | `3` / 31.73% | 0.667 |
| `cracked-star-jar` | 0.3333 | 187.5334 | 0.8521 | `7` / 26.24% | 0.667 |

300 秒 gate 为 `multimap_comparison_recorded_needs_policy_repair`。这说明阶段平衡采样能缓解动作塌缩，但还不能补足长局路线规划、升级协同和 `soda-creek` 中后期恢复目标。
