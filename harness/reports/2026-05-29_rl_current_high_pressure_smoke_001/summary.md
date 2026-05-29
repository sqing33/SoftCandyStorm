# Current High-pressure Smoke Recheck

## 结论

- Decision: `current_high_pressure_smoke_recorded_needs_policy_repair`
- Model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Map preset: `high-pressure`
- Maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`
- Seed start: `63200`
- Episodes per map/window: `3`
- Action selection: deterministic
- Failure case: `harness/failed_cases/fail_20260529_020_current_high_pressure_smoke_gap.json`

本次复查只刷新当前 checkpoint 在固定 high-pressure 窗口下的运行证据，不是 RL policy acceptance，也不是 balance gate。结果保持阻塞：60 秒已暴露 `soda-creek` opening / short-window 不稳定，300 秒三图全部为 `0.0` 胜率。

## Fixed-window Results

| Window | Gate | `soda-creek` | `caramel-workshop` | `cracked-star-jar` |
| --- | --- | ---: | ---: | ---: |
| `60s` | `multimap_comparison_recorded_not_balance_gate` | `0.6667` | `1.0` | `1.0` |
| `180s` | `multimap_comparison_recorded_watch` | `0.3333` | `1.0` | `0.6667` |
| `300s` | `multimap_comparison_recorded_needs_policy_repair` | `0.0` | `0.0` | `0.0` |

## Survival Snapshot

| Window | `soda-creek` | `caramel-workshop` | `cracked-star-jar` |
| --- | ---: | ---: | ---: |
| `60s` average survival | `56.4773s` | `60.0328s` | `60.0328s` |
| `180s` average survival | `116.1581s` | `180.0095s` | `145.7838s` |
| `300s` average survival | `115.5860s` | `215.6949s` | `192.2798s` |

## 判断

- 当前 mid-anchor guarded checkpoint 仍不能作为 RL 测试 Bot 候选。
- 60 秒 `soda-creek` 回落说明 opening / short-window retention 仍需硬保护。
- 180 秒 `soda-creek` 低于规则 Bot watch 阈值，`cracked-star-jar` 也仍不稳定。
- 300 秒三图全 0 胜率，确认 long-run conversion blocker 未解除。
- 后续应围绕失败前状态的 conversion target、per-map objective 或 split policy 做小步 probe，并继续保留 60 / 180 / 300 秒 high-pressure 与多基线 no-regression。

## 输出文件

- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
