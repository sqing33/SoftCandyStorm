# 2026-06-05 Demo Buildcraft Repair v60 Candidates

本批次是 `frosting-grassland` 300 秒可玩 Demo 的路线反制修复候选，基线为：

```text
harness/generated_candidates/2026-06-04_demo_buildcraft_repair_v51_full_pack
```

## 修复目标

- v51 已让大多数 Bot 回到门禁内，但 `RouteBot` 为 40%，高于低技能 Bot 10%-35% 目标。
- v55/v58 的路线回声能把 `RouteBot` 降到 30%，但概率事件和后段压力组合让 `RandomBot`、`KiteBot` 或 `GreedyXpBot` 回归。
- GameCore 现已修复 `chance=1.0` 确定性内容事件消耗 RNG 的问题，因此 v60 转向短窗口确定性事件，避免新增随机序列扰动。

## 本批次改动

- 新增事件 `route-memory-caramel-glint`。
- 事件只在 216-232 秒窗口触发一次，`chance` 固定为 1.0。
- 效果是轻量 `route_echo_hazard`：
  - 每次只生成 1 个旧路线焦糖闪印。
  - 活跃 7 秒，每 2.8 秒采样一次。
  - 回看 22 秒历史路线，触发半径 80。
  - 危险区半径 44，持续 2.4 秒，只减速到 0.78，不造成直接伤害。

## 设计意图

v60 不再尝试提高全局后段压力，也不覆盖已有概率事件。它只在 v51 诊断中的 216-228 秒升级与 Boss 入场附近给固定路线一个可读提醒，目标是让 `RouteBot` 少赢 1 局，同时不把 `RandomBot`、`GreedyXpBot`、`ZoneControlBot` 或 `KiteBot` 推出目标区间。

这个事件的可读性定位是“旧路线被焦糖短暂记住”。真实玩家可以通过改变移动节奏避开；不会因为直接伤害而造成不可避免失败。

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
