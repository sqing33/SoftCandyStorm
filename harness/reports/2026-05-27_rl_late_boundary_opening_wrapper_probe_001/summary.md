# Late Boundary Opening Wrapper Probe

## 结论

- Gate decision: `late_boundary_opening_wrapper_probe_recorded_needs_fallback_repair`
- Opening model: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip`
- Fallback model: `harness/reports/2026-05-27_rl_late_boundary_closed_loop_curriculum_smoke_001/ppo_late_boundary_closed_loop_curriculum_smoke.zip`
- Opening seconds: `60`
- Upgrade ranker: `harness/reports/2026-05-27_rl_upgrade_choice_multimap_ranker_smoke_001/upgrade_choice_multimap_smoke.pt`
- Failure case: `harness/failed_cases/fail_20260527_055_late_boundary_opening_wrapper_fallback_gap.json`

本轮是 evaluation-only probe：使用已知能保 opening 的 stage01 SB3 opening wrapper 负责前 `60` 秒，再切到上一轮 closed-loop late boundary fallback。目标是验证上一轮回归是否主要来自 opening/mid retention，还是 fallback 本身仍无法处理 60 秒后的高压状态。

结果显示 opening wrapper 有明确诊断价值，但不是修复：60 秒从 closed-loop smoke 的 `0.4/0.8/1.0` 提升到 `1.0/1.0/0.8`，180 秒从 `0.2/0.4/0.8` 提升到 `0.4/0.8/0.6`；但 300 秒只有 `0.0/0.0/0.2`，仍低于 late-only behavior clone 的 `0.0/0.0/0.4`。该组合不能进入 stage 03、RL acceptance、playtest 或 release。

## Regression Probes

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `1.0` | `1.0` | `0.8` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.4` | `0.8` | `0.6` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.0` | `0.0` | `0.2` | `multimap_comparison_recorded_needs_policy_repair` |

对照上一轮 closed-loop smoke，opening wrapper 清除了 300 秒失败分析中的 opening death，但 fallback 接手后仍大量死在 `60-180s` 与 `180-300s`。这说明下一步不能只训练一个 late model，也不能只把 opening wrapper 接上旧 fallback；fallback 必须针对 handoff 状态和 mid/late recovery 重新训练或约束。

## 300s Failure Analysis

| Map | Win rate | Avg survival | Failure buckets | Dominant action | Entropy |
| --- | ---: | ---: | --- | --- | ---: |
| `soda-creek` | `0.0` | `130.4360s` | mid `4`, late `1` | action `7` `0.4096` | `0.5375` |
| `caramel-workshop` | `0.0` | `200.4405s` | mid `1`, late `4` | action `7` `0.4130` | `0.5524` |
| `cracked-star-jar` | `0.2` | `184.9634s` | mid `2`, late `2` | action `7` `0.5511` | `0.4428` |

300 秒共有 `14` 个死亡局，且没有 opening bucket 死亡。`soda-creek` 的失败主要转移到 `60-180s`，`caramel-workshop` 主要仍在 `180-300s`，`cracked-star-jar` 则 mid/late 各半。dominant action 全部转为 action `7`，说明 fallback 在 handoff 后仍容易进入单方向路线，而不是根据压力恢复到可持续路径。

## 下一步

- 不把该 wrapper 组合当作 policy 修复，只作为 handoff/mid/late 诊断证据。
- 下一轮应从 wrapper 组合的 failed-only trace 导出 `60-180s` handoff recovery 样本，尤其关注 `soda-creek` action `7` 中窗死亡。
- closed-loop 方向应训练 fallback 接手后的状态分布，而不是只训练 episode 起点或只训练 180 秒后的 late window。
- acceptance 仍必须回到无 adapter 或明确合法 staged policy 的 deterministic high-pressure 60/180/300 秒多图门禁。

## 输出文件

- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
