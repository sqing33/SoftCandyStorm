# Late Boundary Closed-loop Curriculum Smoke

## 结论

- Gate decision: `late_boundary_closed_loop_curriculum_smoke_recorded_needs_retention_repair`
- Model: `harness/reports/2026-05-27_rl_late_boundary_closed_loop_curriculum_smoke_001/ppo_late_boundary_closed_loop_curriculum_smoke.zip`
- Warm start: `harness/reports/2026-05-27_rl_late_route_recovery_reward_profile_smoke_001/ppo_late_route_recovery_reward_profile_smoke.zip`
- Reward profile: `late-route-recovery`
- Upgrade ranker: `harness/reports/2026-05-27_rl_upgrade_choice_multimap_ranker_smoke_001/upgrade_choice_multimap_smoke.pt`
- Failure case: `harness/failed_cases/fail_20260527_054_late_boundary_closed_loop_curriculum_regression.json`

本轮尝试把 late boundary 修复从离线 behavior clone 转回真实 closed-loop PPO：从既有 `late-route-recovery` checkpoint warm start，在 high-pressure 三图上训练 `4096` timesteps，训练 seed 指向上一轮验证暴露出的 `62400-62404`，并继续使用 `late-route-recovery` reward profile、`learning_rate=0.0001`、`ent_coef=0.02` 和 upgrade ranker。

结果仍为 repair，且比 late-only 行为克隆更差：60 秒短窗没有触发 action-bias repair，但 `caramel-workshop` 从 `1.0` 回落到 `0.8`；180 秒三图回落到 `0.2/0.4/0.8`；300 秒仍为 `0.0/0.0/0.4`。这说明直接在失败 seed 上继续训练 late-route-recovery，会破坏 opening/mid retention，并没有带来可用的 300 秒修复。

## Training

- Timesteps: `4096`
- Train maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`
- Map selection: `random`
- Train seconds: `300`
- Train seeds: `62400-62404`
- Seed selection: `random`
- Learning rate: `0.0001`
- Entropy coefficient: `0.02`
- Evaluation policy: `deterministic`

训练后默认 `soda-creek` 60 秒 3 seed evaluation win rate 为 `0.6667`，normalized action entropy 为 `0.4590`。动作主要集中在 action `7`、action `4` 和 action `2`，没有单一动作 100% 塌缩，但路线恢复 reward 仍保持负值，`route_recovery = -1.548`。

## Regression Probes

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `0.4` | `0.8` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.2` | `0.4` | `0.8` | `multimap_comparison_recorded_watch` |
| `300s` | `0.0` | `0.0` | `0.4` | `multimap_comparison_recorded_needs_policy_repair` |

与 `late_boundary_w0_5` 行为克隆相比，该 closed-loop smoke 的 300 秒胜率没有更好，而 60 秒 `caramel-workshop` 和 180 秒 `soda-creek` / `caramel-workshop` 明显回落。`cracked-star-jar` 长窗仍有 `0.4`，但不能抵消前两张图的 0% 胜率和中窗回归。

## 300s Failure Analysis

| Map | Win rate | Avg survival | Failure buckets | Dominant action | Entropy |
| --- | ---: | ---: | --- | --- | ---: |
| `soda-creek` | `0.0` | `77.9831s` | opening `3`, mid `1`, late `1` | action `7` `0.4631` | `0.4336` |
| `caramel-workshop` | `0.0` | `139.9067s` | opening `1`, mid `2`, late `2` | action `4` `0.4162` | `0.5514` |
| `cracked-star-jar` | `0.4` | `247.7759s` | late `3` | action `7` `0.4692` | `0.4706` |

失败分析共记录 `13` 个死亡局。与上一轮 late-only 行为克隆相比，`soda-creek` 的平均失败存活从 `156.1263s` 降到 `77.9831s`，`caramel-workshop` 从 `225.9526s` 降到 `139.9067s`；这不是单纯 late 修复失败，而是 opening/mid retention 被 closed-loop continuation 破坏。

## 下一步

- 不继续从该 checkpoint 加 timestep。
- 下一轮 closed-loop 必须先加入 opening/mid retention 约束或 staged opening wrapper，再谈 late boundary / low-health survival。
- 如果继续 PPO，应使用保守 continuation、显式 seed replay 对照和 60/180 秒 gate 作为训练中止条件。
- 也可以先补充成功/近成功 180-300 秒轨迹，对比失败 seed 的 recovery 方向，避免 reward 继续把策略推向 action `4/7` 的局部路线。

## 输出文件

- `dry_run.json`
- `ppo_training_report.json`
- `ppo_late_boundary_closed_loop_curriculum_smoke.zip`
- `ppo_late_boundary_closed_loop_curriculum_smoke_metadata.json`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
