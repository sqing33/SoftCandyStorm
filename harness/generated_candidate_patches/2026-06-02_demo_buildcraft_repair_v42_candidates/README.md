# Demo Buildcraft Repair v42 Candidates

本批次基于 v38 继续窄修复，用于测试更温和的糖霜草地地图尺寸调整是否能保留 v41 对 RouteBot 的修复收益，同时减少对其他主动 Bot 的过度增益。

- 状态：generated candidate only
- Accepted content: false
- Runtime integrated: false
- Base pack: `harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v38_full_pack`

目标：

- 只测试 `frosting-grassland` 的地图尺寸从 `2600x1700` 调整为 `2450x1600`，观察 RouteBot 是否仍能从 v38 的 `2/3` 降到 `1/3`。
- 相比 v41 的 `2300x1500`，本批次缩图幅度更小，目标是避免 CowardBot、KiteBot、GreedyXpBot、TankBot 和 ZoneControlBot 大面积高于目标。
- 不修改刷怪距离、波次组合、武器、被动、敌人或 Boss，继续隔离地图尺寸这个单变量。

改动：

- `frosting-grassland.size.width`：`2600 -> 2450`
- `frosting-grassland.size.height`：`1700 -> 1600`
- `spawn_rules` 保持 `min_distance=320`、`max_distance=520`

下一步门禁：

1. partial candidate validation with overrides
2. materialize full content pack with overrides
3. materialized pack preflight
4. static balance budget review
5. playable content coverage audit
6. GameCore validate-content
7. isolated GameCore validate-candidates
8. 71000-71002 all-Bot smoke matrix
9. 如果 RouteBot 仍然 `2/3` 或其他 Bot 被打坏，记录 failure case 后转向下一种单变量修复
