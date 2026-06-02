# Demo Buildcraft Repair v39 Candidates

本批次基于 v38 继续窄修复，用于测试糖霜草地更贴近的刷怪距离是否能降低 RouteBot 固定椭圆路线胜率。

- 状态：generated candidate only
- Accepted content: false
- Runtime integrated: false
- Base pack: `harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v38_full_pack`

目标：

- 只测试 `frosting-grassland` 的 `spawn_rules` 距离微调，观察 RouteBot 是否能从 v38 的 `2/3` 降到 `1/3`。
- 保持 v38 已收住的 BossHunter 结果，不再调整 `candy-crystal-lance`、波次或敌人池。
- 避免复现 v32 中对 CowardBot、TankBot 和 ZoneControlBot 的明显扰动。

改动：

- `frosting-grassland`：`spawn_rules.min_distance` 从 `320` 调整为 `300`。
- `frosting-grassland`：`spawn_rules.max_distance` 从 `520` 调整为 `500`。

下一步门禁：

1. partial candidate validation with overrides
2. materialize full content pack with overrides
3. materialized pack preflight
4. static balance budget review
5. playable content coverage audit
6. GameCore validate-content
7. isolated GameCore validate-candidates
8. 71000-71002 all-Bot smoke matrix
9. 如果 RouteBot 仍然 `2/3` 或更高，记录 failure case 并转向下一种单变量修复；如果其他 Bot 被打坏，回滚本方向
