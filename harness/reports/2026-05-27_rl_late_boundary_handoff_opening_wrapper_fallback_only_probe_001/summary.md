# Late Boundary Handoff Fallback-only Probe

## 结论

- Gate decision: `late_boundary_handoff_fallback_only_probe_recorded_needs_policy_repair`
- Variant: `mid_fallback_only`
- Opening wrapper: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip`
- Fallback model: `harness/reports/2026-05-27_rl_late_boundary_handoff_opening_wrapper_midonly_ablation_001/handoff_60_90_mid_w0_5/mid.pt`
- Upgrade ranker: `harness/reports/2026-05-27_rl_upgrade_choice_multimap_ranker_smoke_001/upgrade_choice_multimap_smoke.pt`
- Failure case: `harness/failed_cases/fail_20260527_059_late_boundary_handoff_fallback_only_gap.json`

本轮不训练新模型，只做 evaluation-only probe：前 60 秒仍使用 stage01 opening wrapper，60 秒后不再进入 staged `opening/mid/late` dispatcher，而是直接切到上一轮训练出的 `mid.pt`，用同一组 high-pressure 三图和 seed `62400-62404` 跑 60 / 180 / 300 秒 deterministic 对比。

结果是 repair：60 秒仍保持 `1.0/1.0/0.8`，但 180 秒降到 `0.4/0.8/0.2`，300 秒三图全为 `0.0`。相较上一轮 staged fallback 的 `180s 0.6/1.0/0.4` 与 `300s 0.2/0.2/0.0`，fallback-only 更差，说明问题不是 staged late 子模型或 phase dispatch 单独造成；`mid.pt` 直接接手后仍无法稳定跨图恢复。

## Regression Probes

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s wrapper + mid fallback` | `1.0` | `1.0` | `0.8` | `multimap_comparison_recorded_not_balance_gate` |
| `180s wrapper + mid fallback` | `0.4` | `0.8` | `0.2` | `multimap_comparison_recorded_watch` |
| `300s wrapper + mid fallback` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

## 300s Failure Analysis

| Map | Win rate | Avg survival | Failure buckets | Dominant action | Entropy |
| --- | ---: | ---: | --- | --- | ---: |
| `soda-creek` | `0.0` | `138.8802s` | mid `3`, late `2` | action `7` `38.02%` | `0.7251` |
| `caramel-workshop` | `0.0` | `204.5947s` | mid `1`, late `4` | action `7` `36.58%` | `0.7793` |
| `cracked-star-jar` | `0.0` | `124.1025s` | mid `4`, late `1` | action `7` `61.49%` | `0.5071` |

失败分析共记录 `15` 个死亡局，且 opening bucket 为 `0`。这和上一轮一致地确认 opening wrapper 已把 60 秒前死亡压下去，但 fallback 接手后的 mid / late 路径仍不可靠；`cracked-star-jar` 的 action `7` 占比最高，是最明显的 fallback regression 面。

## 下一步

- 不推进 `mid.pt` fallback-only 组合到 stage 03、RL acceptance、playtest 或 release。
- 不继续只把 `60-90s` handoff 样本加权到同一个 mid clone；当前证据显示它没有形成可泛化 fallback。
- 下一轮应转向 `cracked-star-jar` 专项 handoff 样本，或训练 late-window low-health / hazard / Boss pressure recovery；如果继续 fallback 方向，应把 action `7` 顶边压制和跨图 route recovery 写成显式训练/评估约束。

## 输出文件

- `mid_fallback_only/high_pressure_60s_wrapper_comparison.json`
- `mid_fallback_only/high_pressure_180s_wrapper_comparison.json`
- `mid_fallback_only/high_pressure_300s_wrapper_comparison.json`
- `mid_fallback_only/failure_analysis_300s.json`
- `mid_fallback_only/failure_analysis_300s.md`
