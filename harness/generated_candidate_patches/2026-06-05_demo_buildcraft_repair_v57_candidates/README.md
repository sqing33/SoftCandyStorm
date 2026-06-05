# 2026-06-05 Demo Buildcraft Repair v57 Candidates

本批次是 `frosting-grassland` 300 秒可玩 Demo 的路线反制修复候选，基线为：

```text
harness/generated_candidates/2026-06-04_demo_buildcraft_repair_v51_full_pack
```

## 修复目标

- v55 独立新增路线回声事件能把 `RouteBot` 从 40% 降到 30%，但让 `RandomBot` 和 `KiteBot` 门禁回归。
- v56 把路线回声并入 `caramel-quake` 后，`RandomBot` 和 `KiteBot` 回到门禁内，但 `RouteBot` 回到 40%，说明 240 秒焦糖地震槽位太晚或太保守。
- v57 改用已有 `rainbow-candy-rush` 事件槽位，它本来就在 180 秒后判定，更贴近 v51 诊断出的 180-240 秒路线稳定窗口。

## 本批次改动

- 覆盖事件 `rainbow-candy-rush`，版本从 1 升到 2。
- 保留原有糖晶收益和刷怪风险收益效果。
- 将触发概率从 0.08 调整到 0.14。
- 追加 `route_echo_hazard`，在玩家反复贴近 18 秒前旧路线时生成短暂焦糖回声印。
- 焦糖回声印持续 3.2 秒，半径 54，只减速到 0.82，不造成直接伤害。

## 设计意图

v57 继续避免新增独立事件 id，减少 v55 的额外事件随机序列副作用；同时把路线回声放在更早的已有事件槽里，让固定循环路线在 180-220 秒附近被打断，而不是等到 240 秒后才开始处理。

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
