# Demo Buildcraft Repair v31 Candidates

本批次从 v29 基线继续窄修复，不继承 v30 的焦糖黏地增强或焦糖史莱姆提前加入。

- 状态：generated candidate only
- Accepted content: false
- Runtime integrated: false
- Base pack: `harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v29_full_pack`

目标：

- 轻微压低 KiteBot、CowardBot 和 RouteBot 依赖 `bubble-shoes` 的过稳移动收益。
- 只给 BossHunterBot 第一优先级 `star-sugar-ray` 小幅可靠性修复。
- 不改波次、不改 Boss、不改控制路线，避免复现 v30 的控制/防御过修。

改动：

- `bubble-shoes` v2：每级移动速度从 `+10` 降到 `+9`。
- `star-sugar-ray` v5：伤害 `33 -> 34`，冷却 `1260ms -> 1240ms`，声明单体预算 `26 -> 27`。

下一步门禁：

1. partial candidate validation with overrides
2. materialize full content pack with overrides
3. materialized pack preflight
4. static balance budget review
5. playable content coverage audit
6. GameCore validate-content
7. 71000-71002 all-Bot smoke matrix
8. 如果 smoke 通过，再跑 71000-71009 和 70000-70009 扩样
