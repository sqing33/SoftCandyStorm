# SB3 E30 Mid-anchor Guarded Probe

## 结论

- Decision: `sb3_e30_mid_anchor_guarded_probe_limited_followup_only`
- Start model: `harness/reports/2026-05-28_rl_sb3_supervised_realign_full_anchor_drift_w40_e30_001/ppo_supervised_realign_full_anchor_drift_w40_e30.zip`
- Model: `ppo_e30_mid_anchor_guarded_probe.zip`
- Reward profile: `late-win-conversion`
- Training timesteps: `256`
- Anchor guard: `anchor_validation_guard_passed`
- Full anchor gate: `behavior_clone_anchor_alignment_within_thresholds`
- Window regression vs e30: `policy_window_regression_passed`
- Repair probe gate: `rl_repair_probe_gate_passed_for_limited_followup`
- Failure case: `harness/failed_cases/fail_20260529_002_sb3_e30_mid_anchor_guarded_probe_longrun_gap.json`

本 probe 从 e30 supervised re-alignment checkpoint 重新出发，把 closed-loop continuation 缩短到 `256` timestep，并把 anchor regularization 提高到 `2.0`、mid window 权重提高到 `2.0`，用于验证上一轮 `caramel-workshop` 180 秒 dominant action ratio 回归是否能被更窄的 mid-anchor 约束压住。

结论是：mid-anchor 约束有效，但还不是 policy repair。该分支通过训练期 anchor guard、top drift rows / full anchor alignment，以及相对 e30 的 60 / 180 / 300 秒 no-regression；`caramel-workshop` 180 秒 dominant action ratio 只从 baseline `0.2646` 增至 `0.2871`，不再触发上一轮的 `+0.265` blocker。`repair_probe_gate` 因此允许有限后续探索。

但它仍不能推进为 RL candidate：300 秒 high-pressure 三图胜率全部为 `0.0`，并且上一轮 512 timestep probe 中 `cracked-star-jar` 300 秒 `0.3333` 的恢复信号消失。这个结果说明 mid-window distribution protection 是必要约束，但会牺牲 final-minute conversion，需要下一轮在保留 mid guard 的前提下重新加入 late conversion / opening retention。

## Training And Guard

| Item | Value |
| --- | --- |
| Timesteps | `256` |
| Train maps | `high-pressure` |
| Train seeds | `63100-63102` |
| Learning rate | `0.00001` |
| Entropy coefficient | `0.02` |
| Anchor regularization weight | `2.0` |
| Anchor interval | `256` |
| Anchor epochs per interval | `2` |
| Anchor sample weighting | `map_time_bucket_balance` |
| Time bucket weights | `opening_lt_60=1.5`, `mid_60_to_180=2.0`, `late_180_to_300=1.0` |
| Anchor final mean KL | `0.107282` |
| Anchor final argmax agreement | `0.8248` |
| Final guard decision | `anchor_validation_guard_passed` |

## Anchor Alignment

| Scope | Samples | Mean KL | Argmax agreement | Decision |
| --- | ---: | ---: | ---: | --- |
| Top drift rows | `200` | `0.018432` | `0.965` | `behavior_clone_anchor_alignment_within_thresholds` |
| Full anchor + drift | `36626` | `0.104464` | `0.8306` | `behavior_clone_anchor_alignment_within_thresholds` |

## Fixed-window High-pressure

| Window | Gate | `soda-creek` | `caramel-workshop` | `cracked-star-jar` |
| --- | --- | ---: | ---: | ---: |
| `60s` | `multimap_comparison_recorded_not_balance_gate` | `0.6667` | `0.6667` | `1.0` |
| `180s` | `multimap_comparison_recorded_watch` | `0.3333` | `0.6667` | `0.6667` |
| `300s` | `multimap_comparison_recorded_needs_policy_repair` | `0.0` | `0.0` | `0.0` |

300 秒 failure analysis 记录 `9` 条失败：三张 high-pressure 地图各 `3` 条，且每张图都有 `1` 条 opening failure 与 `2` 条 late failure。这个失败面比上一轮更规整，但说明问题仍同时覆盖 opening retention 与 late conversion。

## Window Regression Vs E30

| Window | Map | Win Δ | Survival Δ | Dominant Ratio Δ | Status |
| --- | --- | ---: | ---: | ---: | --- |
| `60s` | `soda-creek` | `0.3334` | `8.2888` | `-0.088` | `pass` |
| `60s` | `caramel-workshop` | `0.0` | `0.0` | `0.0009` | `pass` |
| `60s` | `cracked-star-jar` | `0.3333` | `4.1778` | `-0.0028` | `pass` |
| `180s` | `soda-creek` | `0.0` | `32.7355` | `0.0885` | `pass` |
| `180s` | `caramel-workshop` | `0.0` | `0.0` | `0.0225` | `pass` |
| `180s` | `cracked-star-jar` | `0.0` | `3.1111` | `0.0123` | `pass` |
| `300s` | `soda-creek` | `0.0` | `2.9339` | `0.1056` | `pass` |
| `300s` | `caramel-workshop` | `0.0` | `6.5347` | `-0.1946` | `pass` |
| `300s` | `cracked-star-jar` | `0.0` | `4.7003` | `-0.1288` | `pass` |

## 判断

- e30 checkpoint 可以承受更强 mid-anchor 小步 closed-loop 续训。
- mid-anchor 配置能解决上一轮 `caramel-workshop` 180 秒 dominant action ratio blocker。
- 该分支只能作为有限后续探索起点：300 秒三图仍全部失败，且丢失上一轮 `cracked-star-jar` 300 秒恢复信号。
- 下一步应保留 mid-anchor / no-regression 保护，同时单独加入 late-window conversion 或 opening retention 约束；不能把这个 checkpoint 推进为 RL acceptance 或 policy candidate。

## 输出文件

- `ppo_training_report.json`
- `ppo_e30_mid_anchor_guarded_probe.zip`
- `ppo_e30_mid_anchor_guarded_probe_metadata.json`
- `ppo_evaluation_report.json`
- `ppo_known_exploits.json`
- `anchor_drift_alignment.json`
- `full_anchor_alignment.json`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
- `window_regression_vs_e30.json`
- `window_regression_vs_e30.md`
- `repair_probe_gate.json`
- `repair_probe_gate.md`
