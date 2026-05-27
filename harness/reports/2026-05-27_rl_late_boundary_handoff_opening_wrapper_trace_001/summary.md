# Late Boundary Handoff Opening Wrapper Trace

## 结论

- Decision: `late_boundary_handoff_opening_wrapper_trace_recorded`
- Source comparison: `comparison_180s_trace.json`
- Trace dir: `traces_180s/`
- Opening model: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip`
- Fallback model: `harness/reports/2026-05-27_rl_late_boundary_handoff_midonly_ablation_001/handoff_mid_w0_5/staged.pt`
- Opening seconds: `60`
- Trace sample stride: `10`

本轮复跑 `stage01 opening wrapper + handoff mid-only staged fallback` 的 180 秒 high-pressure 三图 5 seed 对比，并输出 sampled trace。对比结果与上一轮 180 秒 probe 一致：三图胜率均为 `0.6`，gate 为 `multimap_comparison_recorded_not_balance_gate`。该报告只用于分析 60 秒交接状态，不是新 policy gate，也不是 RL acceptance 证据。

## Handoff Summary

| Map | Victories | Avg handoff health | Min handoff health | Edge-pinned at handoff | First fallback actions | 60-75s actions | Failure buckets |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| `soda-creek` | `3/5` | `93.0918` | `70.1997` | `5/5` | `8:3, 3:2` | `3:113, 8:96, 1:11, 5:3, 4:2` | `mid_60_to_180:2` |
| `caramel-workshop` | `3/5` | `98.5834` | `78.9833` | `5/5` | `8:3, 3:2` | `8:133, 3:62, 7:21, 5:7, 1:2` | `mid_60_to_180:2` |
| `cracked-star-jar` | `3/5` | `87.0172` | `3.7330` | `5/5` | `3:2, 2:2, 8:1` | `3:104, 2:90, 8:16, 1:15` | `mid_60_to_180:2` |

15 个 episode 在交接前最后一帧全部 `edge_risk >= 0.9`，说明 stage01 opening wrapper 虽然提高 60 秒胜率，但经常把角色交给 fallback 时已经贴在地图边界。整体 first fallback action 分布为 action `8` 七次、action `3` 六次、action `2` 两次；fallback 没有在交接点形成稳定离边策略。

## Notable Cases

- `cracked-star-jar` seed `62404` 交接时生命仅 `3.7330`，虽然属于 opening wrapper 清除 opening death 的边缘成功，但 60-75 秒窗口持续 action `2`，最终在 `78.2991s` 死亡。
- `soda-creek` seed `62401` 交接时生命 `96.8798`，首个 fallback action 为 action `3`，60-75 秒窗口保持 action `3`，敌压升到 `1.0`，最终在 `99.2322s` 死亡。
- `caramel-workshop` seed `62401` 交接时位于左下角，首个 fallback action 为 action `3` 且 60-90 秒窗口全为 action `3`，最终在 `91.3323s` 死亡。

## 下一步

- 不继续只替换 staged mid 子模型；交接状态本身高度贴边，需要 fallback policy 明确学习“从贴边交接状态回到可持续路线”。
- 下一轮若做监督修复，应优先用这些 `60-90s` trace 提取交接点后的 non-edge recovery 样本，并过滤掉已经极低血量的边缘样本，避免把绝境残局当作可学目标。
- 若继续用 opening wrapper，应把“交接时 edge-pinned 比例”和“交接后 15 秒动作分布”作为 watch 指标，而不是只看 60 秒胜率。

## 输出文件

- `comparison_180s_trace.json`
- `traces_180s/*.json`
