# RL Time-Phase Balance Curriculum Smoke

## 结论

`train_behavior_clone.py` 已新增 `time_phase_balance` 系列采样权重，可在 opening / mid / late 样本不均衡时按训练集阶段占比反向加权，并可与 `danger`、`action_change` 组合。本报告结论为 `behavior_clone_smoke_only_not_policy_gate`：入口和在线加载路径可用，但不是 RL policy acceptance。

## 训练 Smoke

- Dataset: `harness/reports/2026-05-27_rl_rule_bot_trajectory_phase_aligned_001`
- Model: `time_phase_balance_curriculum_smoke.pt`
- Architecture: `gru`
- Context frames: `8`
- Map conditioning: `one_hot`
- Time phase conditioning: `one_hot`
- Sample weighting: `time_phase_balance_danger_action_change`
- Epochs: `1`
- Hidden size: `16`
- Dataset samples: `21726`
- Train / validation samples: `17381` / `4345`
- Final validation accuracy: `0.3222`

## Phase Multipliers

| Phase | Train Samples | Ratio | Multiplier |
|---|---:|---:|---:|
| `opening` | 4275 | 0.2460 | 1.355244 |
| `mid` | 7953 | 0.4576 | 0.728488 |
| `late` | 5153 | 0.2965 | 1.124329 |

`action_change_sample_ratio` 为 `0.2767`，最终采样权重范围为 `0.729498` 到 `6.562896`。

## Online Loading Smoke

`evaluation_soda_creek_5s.json` 使用该 checkpoint 跑通 `train_sb3.py --evaluate-model --behavior-clone-model`：

- Map: `soda-creek`
- Duration: `5` seconds
- Episodes: `1`
- Win rate: `1.0`
- Normalized action entropy: `0.4687`
- Dominant action: `2` / `50.33%`

该 5 秒评估只证明 checkpoint 可被 Gym evaluation 加载，并不能证明长局策略质量。
