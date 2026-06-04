# v53 前方路线事件诊断报告

- 决策：`repair_diagnostic_no_candidate`
- 基线：`harness/generated_candidates/2026-06-04_demo_buildcraft_repair_v51_full_pack`
- 依赖机制提交：`feat(core): 支持前方路线危险区事件`
- 地图：`frosting-grassland`
- 矩阵：300 秒 / 10 seed / all Bot / seed `72000-72009`

## 目标

v52 诊断显示，纯波次权重无法稳定修复 `RouteBot`，而 `leave_hazard` 拖尾怪虽然能打断固定路线，却会牵连 `RandomBot` 和 `GreedyXpBot`。v53 尝试使用新的 `spawn_hazard` `placement: player_forward_lane` 机制，让 Boss 入场短窗口只在玩家当前移动方向前方生成可读慢区。

## 探针结果

| Probe | 改动 | 结果 | 结论 |
|---|---|---|---|
| A: `forward_lane_event_a` | 210-225 秒必定触发，生成 3 个较强前方路线慢区 | `route` 40%，`tank` 20%，`zone-control` 20% | 未修复 RouteBot，且压低正常路径型 Bot |
| B: `forward_lane_event_b_mild` | 210-225 秒 55% 触发，生成 2 个较弱前方路线慢区 | `route` 40%，`greedy` 20%，`tank` 20%，`zone-control` 20% | 弱化后仍未命中 RouteBot，且继续牵连经济 / 控场 / 坦克 Bot |

## 判断

- `player_forward_lane` 作为 GameCore 内容机制是可用的，Rust 内容校验、Python schema contract 和定向单元测试已通过。
- 但把它直接作为 `frosting-grassland` Boss 入场事件并不能解决 v51 的 RouteBot 残留。
- 该事件更像通用路径压力，会压低 `TankBot`、`ZoneControlBot` 或 `GreedyXpBot`，不是足够精确的固定路线修复。
- 不应把 v53 临时探针推进为 `generated_candidate_patches`、`generated_candidates`、`simulated_candidates`、`playtest_candidates` 或 Runtime 正式内容。

## 下一步

下一轮内容修复需要先看 RouteBot 胜利 seed 的具体状态差异，而不是继续加 hazard：

- 对 `route` 胜利 seed `72002`、`72006`、`72008`、`72009` 导出更细粒度 200-240 秒轨迹。
- 对比 `route` 失败 seed 与 `tank` / `zone-control` 被误伤 seed，找出真正只属于固定路线的特征。
- 如果继续做机制，应考虑“重复经过同一路线才触发”的惩罚，而不是“当前前方路线”惩罚。

## 证据

临时探针报告位于 `/private/tmp/soft_candy/`，未进入正式候选目录：

- `/private/tmp/soft_candy/v53_probe_forward_lane_event_a_matrix_300s_10seed_72000/summary.md`
- `/private/tmp/soft_candy/v53_probe_forward_lane_event_b_mild_matrix_300s_10seed_72000/summary.md`

本报告只记录诊断结论，不接受内容、不放宽门禁、不替代人工试玩。
