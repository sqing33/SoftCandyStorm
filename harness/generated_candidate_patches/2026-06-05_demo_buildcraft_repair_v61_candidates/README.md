# 2026-06-05 Demo Buildcraft Repair v61 Candidates

本批次是 `frosting-grassland` 300 秒可玩 Demo 的路线反制修复候选，基线为：

```text
harness/generated_candidates/2026-06-04_demo_buildcraft_repair_v51_full_pack
```

## 修复目标

- v60 的确定性短窗口事件不会扰乱 `KiteBot`、`RandomBot`、`GreedyXpBot` 或 `ZoneControlBot`，但 `RouteBot` 仍为 40%。
- v60 窗口诊断显示，RouteBot 胜利 seed `72000` 和 `72009` 在 216-232 秒附近几乎没有被 route echo hazard 命中。
- v61 保留 `chance=1.0` 的确定性触发，但把路线回声调到更接近 v55 的有效形状，同时不引入后段波次压力。

## 本批次改动

- 新增事件 `route-memory-caramel-ring`。
- 事件在 212-232 秒窗口确定性触发一次，`chance` 固定为 1.0。
- 效果是中等强度 `route_echo_hazard`：
  - 每次生成 2 个旧路线焦糖环。
  - 活跃 14 秒，每 2.2 秒采样一次。
  - 回看 18 秒历史路线，触发半径 116。
  - 危险区半径 52，持续 3 秒，只减速到 0.80，不造成直接伤害。

## 设计意图

v61 的目标不是提高全局难度，而是专门覆盖 RouteBot 在 212-232 秒的重复路线稳定窗口。它比 v60 更早、更宽，并增加单次生成数量，以便覆盖 `72000` 和 `72009` 这两个 v60 几乎未命中的胜利 seed。

真实玩家应能通过离开旧路线、改变绕圈节奏或短暂转向来规避焦糖环；该事件不造成直接伤害，因此不会把路线反制变成不可读的秒杀机制。

## 候选边界

- `candidate_only`: true
- `accepted_content`: false
- `runtime_integrated`: false

本批次只能进入 `generated_candidate_patches` 到 `generated_candidates` 的候选流程。它不能复制到 `content/base_demo`、`accepted_content` 或 Runtime 正式内容目录。

## 下一步门禁

1. partial candidate validation with event coverage
2. materialize full content pack with events overlay
3. materialized pack preflight
4. static balance budget review
5. GameCore validate-content
6. isolated GameCore validate-candidates
7. 先跑 `route`、`kite`、`random`、`greedy`、`zone-control` 关键 Bot 矩阵
8. 关键 Bot 通过后再跑 300 秒 / 10 seed / all Bot 矩阵
9. 若失败，记录 failure case，保留拒绝原因后继续 repair
