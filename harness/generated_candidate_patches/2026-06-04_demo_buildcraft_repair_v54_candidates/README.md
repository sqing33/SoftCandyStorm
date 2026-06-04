# 2026-06-04 Demo Buildcraft Repair v54 Candidates

本批次是 `frosting-grassland` 300 秒可玩 Demo 的终局波次修复候选，基线为：

```text
harness/generated_candidates/2026-06-04_demo_buildcraft_repair_v51_full_pack
```

## 修复目标

- v51 中 `RouteBot` 仍为 40%，高于低技能规则 Bot 10%-35% 的目标上限。
- 诊断显示失败 seed 基本在 240 秒前结束，胜利 seed 的 240-300 秒窗口敌人压力和 Boss 压力很低。
- v52/v53 已证明 Boss 入场危险事件、路线危险地块和前方路线事件会误伤 `RandomBot`、`GreedyXpBot`、`TankBot` 或 `ZoneControlBot`，因此本批次不新增机制、不改地图、不改正式内容。

## 本批次改动

- 只覆盖 `frosting-grassland-standard` 波次，不修改角色、武器、被动、敌人、Boss、地图、事件或 Runtime 正式内容。
- 将 v51 的 `255-300` 秒拆成 `255-270` 与 `270-300` 两段。
- `255-270` 秒保持 v51 形状，作为 Boss 后半段过渡窗口。
- `270-300` 秒小幅缩短刷怪间隔到 `860ms`，`max_alive` 提高到 `80`，加入已有敌人 `spicy-gummy`，并略提高终局扰动敌人的占比。
- 270-300 秒静态估算 `spawn_pressure` 约 `3.75`，仍低于 Boss 段 `3.8` 上限；`alive_pressure` 约 `129`，仍低于 Boss 段 `130` 上限。

## 候选边界

- `candidate_only`: true
- `accepted_content`: false
- `runtime_integrated`: false

本批次只能进入 `generated_candidate_patches` 到 `generated_candidates` 的候选流程。它不能复制到 `content/base_demo`、`accepted_content` 或 Runtime 正式素材目录。

## 下一步门禁

1. partial candidate validation with overrides
2. materialize full content pack with overrides
3. materialized pack preflight
4. static balance budget review
5. GameCore validate-content
6. isolated GameCore validate-candidates
7. 300 秒 / 10 seed / all Bot 矩阵
8. 若通过，再更新可玩内容覆盖和人工试玩材料
9. 若失败，记录 failure case，保留拒绝原因后继续 repair
