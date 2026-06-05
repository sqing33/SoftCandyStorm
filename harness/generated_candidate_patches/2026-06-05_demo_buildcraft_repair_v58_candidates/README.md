# 2026-06-05 Demo Buildcraft Repair v58 Candidates

本批次是 `frosting-grassland` 300 秒可玩 Demo 的路线反制修复候选，基线为：

```text
harness/generated_candidates/2026-06-04_demo_buildcraft_repair_v51_full_pack
```

## 修复目标

- v51 已让大多数 Bot 回到门禁内，但 `RouteBot` 仍为 40%，高于低技能 10%-35% 目标。
- v55 的独立 `route-echo-caramel-mark` 事件能把 `RouteBot` 降到 30%，但让 `RandomBot` 升到 20%、`KiteBot` 升到 90%。
- v52 的 `late_mix_a` 波次加压单独使用时不能修 `RouteBot`，但能让 `RandomBot` 和 `KiteBot` 保持门禁内。
- v58 组合这两个方向：用路线回声处理固定路线，用 255-300 秒后段远程 / 机动压力抵消 v55 的 Random/Kite 副作用。

## 本批次改动

- 新增事件 `route-echo-caramel-mark`，沿用 v55 的 188-246 秒重复路线反制窗口。
- 覆盖波次 `frosting-grassland-standard`，版本从 30 升到 31。
- 仅调整 255-300 秒段：
  - `spawn_interval_ms` 从 900 收紧到 880。
  - `max_alive` 从 76 提高到 78。
  - 降低基础追踪与安全填充权重。
  - 提高 `licorice-skipper`、`sugar-moth` 和 `sprinkle-spitter` 的路线 / 风筝压力。

## 设计意图

本批次不是单纯提高全局难度，而是把两个已有诊断结论叠加验证：

- `route-echo-caramel-mark` 负责在 188-246 秒打断固定椭圆路线。
- 255-300 秒后段压力负责防止高机动或随机高 roll 在路线回声改变随机序列后过度安全。

如果 v58 仍失败，应根据失败 Bot 类型决定后续方向：

- 若 `RouteBot` 仍高，说明独立事件效果被后段压力抵消或触发仍不可靠，应转向更确定的重复路线机制。
- 若 `RandomBot` / `KiteBot` 仍高，说明后段压力不足。
- 若 `GreedyXpBot`、`TankBot` 或 `ZoneControlBot` 偏低，说明后段压力误伤正常构筑，应拒绝本批次。

## 候选边界

- `candidate_only`: true
- `accepted_content`: false
- `runtime_integrated`: false

本批次只能进入 `generated_candidate_patches` 到 `generated_candidates` 的候选流程。它不能复制到 `content/base_demo`、`accepted_content` 或 Runtime 正式内容目录。

## 下一步门禁

1. partial candidate validation with event and wave override coverage
2. materialize full content pack with events and waves overlay
3. materialized pack preflight
4. static balance budget review
5. GameCore validate-content
6. isolated GameCore validate-candidates
7. 300 秒 / 10 seed / all Bot 矩阵
8. 若通过，再更新可玩内容覆盖和人工试玩材料
9. 若失败，记录 failure case，保留拒绝原因后继续 repair
