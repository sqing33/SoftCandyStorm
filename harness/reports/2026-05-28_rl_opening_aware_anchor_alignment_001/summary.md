# Opening-aware PPO Anchor Alignment

## 结论

- Gate decision: `behavior_clone_anchor_alignment_failed`
- Candidate: `harness/reports/2026-05-28_rl_curriculum_stage02_opening_aware_late_win_conversion_probe_001/ppo_opening_aware_late_win_conversion_probe.zip`
- Anchor fallback: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_fallback_probe_001/fallback.pt`
- Anchor opening: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Dataset samples: `36426`
- Report: `anchor_alignment.json`

本报告用 `compare_sb3_to_behavior_clone_anchor.py` 复查 opening-aware PPO 候选相对“SB3 stage 02 opening + current-failure fallback behavior-clone”anchor 的离线漂移。诊断阈值是 overall mean KL `<= 0.25`、overall argmax agreement `>= 0.75`、单个地图 / 时间窗 mean KL `<= 0.5`。该阈值只用于 repair 诊断，不是 RL acceptance。

结果：anchor alignment 失败。overall mean KL 为 `0.353364`，超过 `0.25`；overall argmax agreement 为 `0.6899`，低于 `0.75`。虽然单个地图和时间窗 mean KL 未超过 `0.5`，但 opening 的 argmax agreement 只有 `0.4742`，mid-window `60-180s` mean KL 达到 `0.436179`。这说明 closed-loop 续训后的 PPO 确实偏离了 anchor，尤其是开局 argmax 和中窗分布。

## Overall Metrics

| Metric | Value |
| --- | ---: |
| Sample count | `36426` |
| Mean KL | `0.353364` |
| Max KL | `3.474885` |
| Argmax agreement | `0.6899` |
| Anchor entropy | `0.962823` |
| Candidate entropy | `1.510319` |

## By Map

| Map | Samples | Mean KL | Argmax Agreement | Candidate Entropy |
| --- | ---: | ---: | ---: | ---: |
| `caramel-workshop` | `12192` | `0.327616` | `0.6858` | `1.459947` |
| `cracked-star-jar` | `12495` | `0.352043` | `0.6961` | `1.478870` |
| `soda-creek` | `11739` | `0.381511` | `0.6877` | `1.596110` |

## By Time Bucket

| Time Bucket | Samples | Mean KL | Argmax Agreement | Candidate Entropy |
| --- | ---: | ---: | ---: | ---: |
| `opening_lt_60` | `5590` | `0.312955` | `0.4742` | `1.533160` |
| `mid_60_to_180` | `11813` | `0.436179` | `0.6468` | `1.498399` |
| `late_180_to_300` | `19023` | `0.313811` | `0.7801` | `1.511009` |

## Blockers

- overall mean_kl `0.353364` exceeds `0.25`
- overall argmax_agreement `0.6899` below `0.75`

## 判断

- opening-aware distillation 让 teacher 入口正确，但 closed-loop PPO 仍会把 policy 推离 anchor。
- `opening_lt_60` 的 argmax agreement 过低，解释了 `soda-creek` 60 秒 no-regression 失败。
- `mid_60_to_180` 的 KL 最高，解释了 180 秒多图平均存活回归。
- 后续如果继续 PPO closed-loop，应先做真正的 KL / behavior-clone anchor 训练约束，或改回 supervised / per-map constrained repair；单纯提高 entropy 不足以保护窗口。
