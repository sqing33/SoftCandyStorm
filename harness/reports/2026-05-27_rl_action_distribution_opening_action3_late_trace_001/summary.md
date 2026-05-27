# Opening Action3 Low-Weight Late Trace Diagnostic

## 结论

- Gate decision: `late_trace_recorded_needs_late_policy_repair`
- Source checkpoint: `harness/reports/2026-05-27_rl_action_distribution_opening_action3_low_weight_ablation_001/opening_action3_w0_5_windowed/staged.pt`
- Source failure case: `harness/failed_cases/fail_20260527_049_action_distribution_opening_action3_late_gap.json`
- Comparison: `comparison_300s_trace.json`
- Policy failure analysis: `policy_failure_analysis.md`
- Route recovery hotspots: `route_recovery_hotspots.md`
- Trace mode: failed-only, sample stride `10`, observation included

本轮重放 `opening_action3_w0_5_windowed` 的 300 秒 high-pressure 三图失败，并保存 15 条 failed-only traces。结果复现了上一轮 300 秒阻塞：三图仍为 `0.0` win rate，不能推进 stage 03、RL acceptance、playtest 或 release。

## Failure Buckets

| Map | Failures | Opening <60s | Mid 60-180s | Late 180-300s | Avg failure survival | Dominant action |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `soda-creek` | `5` | `2` | `0` | `3` | `143.2769s` | action `1` `55.33%` |
| `caramel-workshop` | `5` | `0` | `0` | `5` | `218.5377s` | action `1` `42.11%` |
| `cracked-star-jar` | `5` | `1` | `0` | `4` | `183.7876s` | action `1` `58.47%` |

总计 `15` 条失败中，`12` 条位于 `late_180_to_300`，`3` 条仍是 opening 早死，`mid_60_to_180` 没有 terminal failure。当前主要缺口已经从上一轮的 60-180 秒 `soda-creek` 中窗，转移到 180-300 秒中后期 survival。

## Terminal Frame Pressure

| Map | Traces | Avg terminal time | Edge pinned | Enemy pressure | Hazard pressure | Boss pressure | Low health |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `soda-creek` | `5` | `143.2769s` | `5` | `4` | `1` | `2` | `5` |
| `caramel-workshop` | `5` | `218.5377s` | `5` | `1` | `4` | `1` | `5` |
| `cracked-star-jar` | `5` | `183.7876s` | `5` | `4` | `2` | `2` | `5` |

所有 terminal frames 都处于边界贴边和低血量状态；其中 `9/15` 伴随 enemy pressure，`7/15` 伴随 hazard pressure，`5/15` 伴随 boss pressure。下一轮不能只修 opening action `3`，也不能只惩罚单一 action；需要 late edge escape + hazard / boss / enemy pressure 联合目标。

## Route Recovery Hotspots

| Scope | Hotspots | Main actions |
| --- | ---: | --- |
| All sampled rows | `6942 / 8205` (`84.61%`) | boundary-driven |
| `opening_lt_60` | `1851` | action `3`: `831`, action `5`: `521`, action `1`: `340` |
| `mid_60_to_180` | `3911` | action `1`: `2795`, action `2`: `464`, action `7`: `464` |
| `late_180_to_300` | `1180` | action `1`: `717`, action `7`: `232`, action `6`: `129` |

压力标签分布：

- `boundary_edge`: `6839` hotspots
- `low_health`: `431` hotspots
- `hazard_pressure`: `281` hotspots
- `enemy_pressure`: `101` hotspots
- `boss_pressure`: `39` hotspots

`late_180_to_300` 的主要 route recovery 负样本来自 action `1`，但 terminal action 本身分散在 action `1/2/3/4/5/6/7`。因此下一轮更适合导出 late window risk-recovery samples 或做 closed-loop late survival curriculum，而不是硬性把 action `1` 替换成某个固定方向。

## 判断

- `opening_action3_w0_5_windowed` 已经是更好的 opening baseline，但仍保留少量 opening 早死。
- 最大 blocker 是 180-300 秒：贴边、低血量、敌群、hazard 和 boss pressure 混合出现。
- 下一步应导出 `180-240s` 或 `180-300s` late risk-recovery supervision samples，保留当前 opening 子模型，并只替换 late 子模型或进入闭环 PPO/curriculum。

## 输出文件

- `comparison_300s_trace.json`
- `policy_failure_analysis.json`
- `policy_failure_analysis.md`
- `route_recovery_hotspots.json`
- `route_recovery_hotspots.md`
- `traces/*.json`
