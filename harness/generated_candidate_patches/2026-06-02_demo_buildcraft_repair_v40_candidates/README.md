# Demo Buildcraft Repair v40 Candidates

本批次基于 v38 继续窄修复，用于测试彩虹糖弹射程成长削弱是否能降低 RouteBot 固定椭圆路线胜率。

- 状态：generated candidate only
- Accepted content: false
- Runtime integrated: false
- Base pack: `harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v38_full_pack`

目标：

- 只测试 `rainbow-candy-shot` 的射程成长从 `18` 降到 `10`，观察 RouteBot 是否能从 v38 的 `2/3` 降到 `1/3`。
- 保留基础伤害、冷却、弹体数、5 级弹体节点、地图刷怪距离和波次组合，避免复现 v3 的基础武器过砍和 v39 的全局刷怪扰动。
- 重点验证是否能削弱固定路线远距离自动清怪收益，同时保留普通开局手感。

改动：

- `rainbow-candy-shot`：`scaling.range_per_level` 从 `18` 调整为 `10`。
- `rainbow-candy-shot`：描述补充“射程成长更克制”，其余战斗数值保持 v38。

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
