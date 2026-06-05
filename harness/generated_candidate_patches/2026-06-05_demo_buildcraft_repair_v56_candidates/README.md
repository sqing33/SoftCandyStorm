# 2026-06-05 Demo Buildcraft Repair v56 Candidates

本批次是 `frosting-grassland` 300 秒可玩 Demo 的路线反制修复候选，基线为：

```text
harness/generated_candidates/2026-06-04_demo_buildcraft_repair_v51_full_pack
```

## 修复目标

- v51/v54 中 `RouteBot` 胜率为 40%，高于低技能规则 Bot 10%-35% 的目标上限。
- v55 新增独立事件后，`RouteBot` 降到 30%，但 `RandomBot` 升到 20%、`KiteBot` 升到 90%，说明独立新增事件带来矩阵回归。
- v56 继续保留路线回声思路，但不新增第 6 个事件，而是覆盖已有 `caramel-quake`，减少额外事件随机序列副作用。

## 本批次改动

- 覆盖事件 `caramel-quake`，版本从 1 升到 2。
- 保留原有焦糖危险区和 `caramel-slime` 生成。
- 将触发概率从 0.06 调整到 0.10。
- 追加 `route_echo_hazard`，仅当玩家贴近约 23 秒前的历史位置时，生成短暂焦糖回声印。
- 焦糖回声印持续 3 秒，半径 50，只减速到 0.80，不造成直接伤害。

## 设计意图

v56 不是普通加压，也不是终局怪潮增强。它试图把 v55 证明有效的“重复路线反制”并入已有焦糖地震事件，让固定循环路线更容易被短暂打断，同时避免 v55 独立事件让 Random/Kite 结果漂出门禁。

## 候选边界

- `candidate_only`: true
- `accepted_content`: false
- `runtime_integrated`: false

本批次只能进入 `generated_candidate_patches` 到 `generated_candidates` 的候选流程。它不能复制到 `content/base_demo`、`accepted_content` 或 Runtime 正式内容目录。

## 下一步门禁

1. partial candidate validation with event override coverage
2. materialize full content pack with events overlay
3. materialized pack preflight
4. static balance budget review
5. GameCore validate-content
6. isolated GameCore validate-candidates
7. 300 秒 / 10 seed / all Bot 矩阵
8. 若通过，再更新可玩内容覆盖和人工试玩材料
9. 若失败，记录 failure case，保留拒绝原因后继续 repair
