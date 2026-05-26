# PPO Time-Phase Balance Closed-Loop 10k

## 结论

从阶段平衡 teacher 的 distilled PPO zip 出发，经过 high-pressure 三图随机采样的 10k timestep PPO 闭环训练后，短窗动作塌缩有所缓解，60 秒 high-pressure 三图 gate 通过；但 300 秒仍为 `multimap_comparison_recorded_needs_policy_repair`。`soda-creek` 与 `caramel-workshop` 长局胜率均为 0%，不能推进为 RL 测试 Bot。

对应 failure case：`harness/failed_cases/fail_20260527_017_time_phase_balance_ppo_closed_loop_gap.json`。

## Training

- Warm start: `harness/reports/2026-05-27_rl_sb3_distill_time_phase_balance_teacher_001/ppo_time_phase_balance_distilled.zip`
- Model: `ppo_time_phase_balance_closed_loop_10k.zip`
- Timesteps: `10240` actual / `10000` requested
- Train maps: `high-pressure`
- Map selection: `random`
- Train seconds: `300`
- `ent_coef`: `0.02`
- Algorithm parameters source: `warm_start_metadata_with_overrides`
- Initial evaluation map: `soda-creek`
- Initial 60-second evaluation win rate: `0.3333`
- Initial normalized action entropy: `0.5271`

## 60 秒对比

命令输出：`comparison_60s.json`

| Map | Policy Win Rate | Avg Survival | Normalized Entropy | Dominant Action | Rule Bot Best |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.6 | 52.7929 | 0.4327 | `1` / 61.28% | 1.0 |
| `caramel-workshop` | 0.8 | 55.9395 | 0.3988 | `1` / 72.48% | 1.0 |
| `cracked-star-jar` | 1.0 | 60.0328 | 0.4268 | `1` / 64.85% | 1.0 |

60 秒 gate 为 `multimap_comparison_recorded_not_balance_gate`，但三图动作都偏向 action `1`。

## 300 秒对比

命令输出：`comparison_300s.json`

| Map | Policy Win Rate | Avg Survival | Normalized Entropy | Dominant Action | Rule Bot Best |
|---|---:|---:|---:|---|---:|
| `soda-creek` | 0.0 | 91.3940 | 0.6456 | `7` / 39.03% | 0.333 |
| `caramel-workshop` | 0.0 | 180.7884 | 0.4196 | `3` / 67.40% | 0.667 |
| `cracked-star-jar` | 0.3333 | 178.8437 | 0.6419 | `1` / 31.01% | 0.667 |

300 秒结果说明：PPO 闭环可以移动失败面并缓解单一 action 3 塌缩，但没有形成稳定长局目标。下一步应优先做长局课程 / 奖励目标或 movement + upgrade 联合训练，而不是继续把同一蒸馏 zip 做短步数 warm-start。
