# Demo Buildcraft Repair v33 Candidates

本批次基于 v31 继续窄修复，用于隔离验证 BossHunter 修复，不继承 v32 的 225-300 秒波次调整。

- 状态：generated candidate only
- Accepted content: false
- Runtime integrated: false
- Base pack: `harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v31_full_pack`

目标：

- 用比 v32 更小的 `candy-crystal-lance` 可靠性修复，观察 BossHunterBot 是否能回到目标区间。
- 不改 `frosting-grassland-standard` 波次，避免再次扰动 CowardBot、TankBot 和 ZoneControlBot。
- 不推进 RouteBot 修复；本批次只拆分变量，确认 Boss 武器修复本身的影响。

改动：

- `candy-crystal-lance` v5：伤害 `29 -> 30`，冷却 `1080ms -> 1060ms`，声明单体预算 `27 -> 28`。

下一步门禁：

1. partial candidate validation with overrides
2. materialize full content pack with overrides
3. materialized pack preflight
4. static balance budget review
5. playable content coverage audit
6. GameCore validate-content
7. 71000-71002 all-Bot smoke matrix
8. 如果 smoke 通过，再跑 71000-71009 和 70000-70009 扩样
