# v52 RouteBot 诊断报告

- 决策：`repair_diagnostic_no_candidate`
- 基线：`harness/generated_candidates/2026-06-04_demo_buildcraft_repair_v51_full_pack`
- 地图：`frosting-grassland`
- 矩阵：300 秒 / 10 seed / all Bot / seed `72000-72009`
- 结论：本轮没有生成可推进的 v52 内容候选；继续微调波次权重或轻量拖尾怪会在 `RouteBot`、`RandomBot`、`GreedyXpBot` 之间来回转移问题。

## 背景

v51 已经通过 partial candidate validation、materialize、preflight、static budget、`game_harness validate-content` 和 isolated `validate-candidates`，并在 300 秒 / 10 seed all Bot 矩阵中让 `CowardBot` 回到目标区间。但 `RouteBot` 仍为 40%，高于低技能 Bot 10%-35% 目标。

本轮目标是继续修复固定椭圆路线残留，同时不牵连正常可玩体验。

## 探针结果

| Probe | 改动 | 结果 | 结论 |
|---|---|---|---|
| A: `late_mix_a` | 只提高 255-300 秒 `licorice-skipper` / `sugar-moth` / `sprinkle-spitter` 路线压力 | `route` 40%，`random` 10%，其它通过 | 后半段加压未命中 RouteBot，只改变随机高 roll |
| B: `boss_entry_blend_b` | 轻微调整 210-225 秒 Boss 入场敌人结构，保留 v51 后半段 | `route` 40%，其它通过 | 结构调整安全但仍不足 |
| C: `caramel_trail_c` | 新增 `caramel-trail-dot` 拖尾慢区怪，210-300 秒少量混入 | `route` 20%，但 `random` 20%，`greedy` 10% | 机制方向有效，但过量且误伤经济节奏 |
| D: `caramel_trail_d_late_only` | 弱化拖尾怪，只在 255-300 秒 3% 混入 | `route` 40%，其它通过 | 安全但无效 |
| E: `caramel_trail_e_late_mild` | 225-255 秒 2%、255-300 秒 4% 混入中等拖尾怪 | `route` 40%，其它通过 | 中等后半段混入仍无效 |
| F: `caramel_trail_f_entry_tiny` | 只在 210-225 秒 2% 混入弱拖尾怪 | `route` 30%，但 `random` 20%，`greedy` 20% | Boss 入场是关键窗口，但拖尾会改变随机 / 经济 Bot 拓扑 |

## 判断

- 纯敌人权重调整已经到达边际：A、B、D、E 都无法把 `RouteBot` 从 40% 稳定压回目标。
- `leave_hazard` 拖尾机制能打断固定路线：C 和 F 都能把 `RouteBot` 降到目标内。
- 现有拖尾机制不够精确：有效强度会同时让 `RandomBot` 超过 15% 或让 `GreedyXpBot` 低于 25%。
- 不应把任何 v52 临时探针推进为 `generated_candidate_patches`、`generated_candidates`、`simulated_candidates`、`playtest_candidates` 或 Runtime 正式内容。

## 下一步

下一轮不要继续只调敌人权重。优先做一个更窄的可读路线扰动机制，满足：

- 只在 Boss 入场或固定路线安全窗口生效。
- 不额外喂给随机 / 经济 Bot 明显收益。
- 玩家能从视觉上看懂并主动绕开。
- 先作为 GameCore 内容机制单独提交，再用内容候选接入 `frosting-grassland-standard`。

推荐方向：

- 支持 content event 的 deterministic route-lane hazard，但需要可读预警和有限持续时间。
- 支持波次内短窗口 hazard 事件，而不是全局随机事件。
- 支持敌人或 Boss 技能按玩家重复路线生成低伤害、低 XP、低持续的路线阻断。

## 证据

临时探针报告位于 `/private/tmp/soft_candy/`，未进入正式候选目录：

- `/private/tmp/soft_candy/v52_probe_late_mix_a_matrix_300s_10seed_72000/summary.md`
- `/private/tmp/soft_candy/v52_probe_boss_entry_blend_b_matrix_300s_10seed_72000/summary.md`
- `/private/tmp/soft_candy/v52_probe_caramel_trail_c_matrix_300s_10seed_72000/summary.md`
- `/private/tmp/soft_candy/v52_probe_caramel_trail_d_late_only_matrix_300s_10seed_72000/summary.md`
- `/private/tmp/soft_candy/v52_probe_caramel_trail_e_late_mild_matrix_300s_10seed_72000/summary.md`
- `/private/tmp/soft_candy/v52_probe_caramel_trail_f_entry_tiny_matrix_300s_10seed_72000/summary.md`

本报告只记录诊断结论，不接受内容、不放宽门禁、不替代人工试玩。
