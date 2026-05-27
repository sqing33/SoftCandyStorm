# Late Boundary Handoff Opening Wrapper Probe

## 结论

- Gate decision: `late_boundary_handoff_opening_wrapper_probe_recorded_needs_fallback_repair`
- Opening model: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip`
- Fallback model: `harness/reports/2026-05-27_rl_late_boundary_handoff_midonly_ablation_001/handoff_mid_w0_5/staged.pt`
- Opening seconds: `60`
- Upgrade ranker: `harness/reports/2026-05-27_rl_upgrade_choice_multimap_ranker_smoke_001/upgrade_choice_multimap_smoke.pt`
- Failure case: `harness/failed_cases/fail_20260527_057_late_boundary_handoff_opening_wrapper_probe_gap.json`

本轮是 evaluation-only probe：使用已知能保 opening 的 stage01 SB3 opening wrapper 负责前 `60` 秒，再切到上一轮 handoff mid-only staged behavior clone fallback。目标是把 opening death 从结果中剥离出来，验证 handoff mid-only fallback 是否能在 opening 被保护后改善 `60-180s` 和 `180-300s`。

结果仍为 repair：60 秒 high-pressure 三图为 `1.0/1.0/0.8`，说明 opening wrapper 继续有效；180 秒为 `0.6/0.6/0.6`，相比旧 closed-loop fallback 的 `0.4/0.8/0.6` 只改善了 `soda-creek`，同时拉低 `caramel-workshop`；300 秒三图全部 `0.0`，低于上一轮 mid-only staged fallback 的 `0.0/0.0/0.4`。该 wrapper 组合不能推进 stage 03、RL acceptance、playtest 或 release。

## Regression Probes

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `1.0` | `1.0` | `0.8` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.6` | `0.6` | `0.6` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

这组结果说明：opening wrapper 能保护短窗，但 handoff mid-only fallback 没有稳定接住中后窗。与不加 wrapper 的 mid-only staged fallback 相比，60 秒从 `0.4/1.0/0.8` 提升到 `1.0/1.0/0.8`，但 300 秒 `cracked-star-jar` 从 `0.4` 回落到 `0.0`。

## 300s Failure Analysis

| Map | Win rate | Avg survival | Failure buckets | Dominant action | Entropy |
| --- | ---: | ---: | --- | --- | ---: |
| `soda-creek` | `0.0` | `195.4408s` | mid `1`, late `4` | action `3` `0.3009` | `0.8074` |
| `caramel-workshop` | `0.0` | `191.9871s` | mid `1`, late `4` | action `3` `0.3465` | `0.7830` |
| `cracked-star-jar` | `0.0` | `167.9412s` | mid `3`, late `2` | action `3` `0.2388` | `0.8339` |

失败分析共记录 `15` 个死亡局，且没有 opening bucket 死亡。死亡集中在 `60-300s`：`soda-creek` 和 `caramel-workshop` 各有 `1` 个 mid 死亡和 `4` 个 late 死亡，`cracked-star-jar` 有 `3` 个 mid 死亡和 `2` 个 late 死亡。dominant action 均为 action `3`，但 entropy 比旧 closed-loop fallback 更高，说明问题不只是低熵单动作塌缩，而是 fallback 在中后窗压力下仍缺少可持续路线恢复。

## 下一步

- 不把该 wrapper 组合当作 policy 修复，它只是 handoff / fallback 诊断证据。
- 下一步应输出 opening wrapper 交接点 trace，对比 60 秒时的位置、生命、边界风险和 fallback 初始动作分布。
- 如果继续监督路线，应训练真正的 fallback policy 约束，而不是只替换 staged behavior clone 的 mid 子模型。
- 长窗仍需要 late-window low-health / hazard / boss pressure recovery，并且必须保留 deterministic 60/180/300 秒 high-pressure 三图门禁。

## 输出文件

- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
