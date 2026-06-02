# Demo Buildcraft Repair v41 Candidates

本批次基于 v38 继续窄修复，用于测试糖霜草地地图尺寸微调是否能降低 RouteBot 固定椭圆路线胜率。

- 状态：generated candidate only
- Accepted content: false
- Runtime integrated: false
- Base pack: `harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v38_full_pack`

目标：

- 只测试 `frosting-grassland` 的地图尺寸从 `2600x1700` 调整为 `2300x1500`，观察 RouteBot 是否能从 v38 的 `2/3` 降到 `1/3`。
- 不修改刷怪距离、波次组合、武器、被动、敌人或 Boss，避免复现 v39 的全局刷怪扰动和 v40 的 starter 武器扰动。
- 直接作用于 RouteBot 的固定椭圆路线半径，因为 RouteBot 的路线半径由地图宽高计算而来。

改动：

- `frosting-grassland.size.width`：`2600 -> 2300`
- `frosting-grassland.size.height`：`1700 -> 1500`
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
