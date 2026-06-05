# 2026-06-04 Demo Buildcraft Repair v55 Candidates

本批次是 `frosting-grassland` 300 秒可玩 Demo 的路线反制事件候选，基线为：

```text
harness/generated_candidates/2026-06-04_demo_buildcraft_repair_v51_full_pack
```

## 修复目标

- v51 中 `RouteBot` 胜率为 40%，高于低技能规则 Bot 10%-35% 的目标上限。
- v54 只增强 270-300 秒终局压力后，`RouteBot` 仍为 40%，说明问题不是单纯终局压力不足。
- v51 的 180-240 秒诊断显示胜败组普通敌人压力差异很小，固定路线本身仍然稳定。

## 本批次改动

- 新增事件 `route-echo-caramel-mark`。
- 事件触发窗口为 188-246 秒，概率 0.14。
- 事件触发后持续 12 秒，每 2.2 秒检查一次玩家 18 秒前的位置。
- 只有当玩家当前接近旧路线时，才在旧位置生成短暂焦糖印。
- 焦糖印持续 3.2 秒，半径 54，只减速到 0.82，不造成直接伤害。

## 设计意图

这个事件不是普通随机危险区，也不是前方路线危险区。它针对的是“重复经过同一条路线”的行为：固定椭圆路线更容易踩回旧路线，正常变线玩家可以通过改线绕开。

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
7. 300 秒 / 10 seed / all Bot 矩阵
8. 若通过，再更新可玩内容覆盖和人工试玩材料
9. 若失败，记录 failure case，保留拒绝原因后继续 repair
