# Demo Buildcraft Repair v34 Candidates

本批次基于 v31 继续窄修复，用于确认 BossHunter 的最小可控修复幅度，不继承 v32 的 225-300 秒波次调整，也不继承 v33 的冷却和射速增强。

- 状态：generated candidate only
- Accepted content: false
- Runtime integrated: false
- Base pack: `harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v31_full_pack`

目标：

- 只测试 `candy-crystal-lance` 的最小伤害修复，观察 BossHunterBot 是否能从 v31 的 0/3 回到目标区间。
- 不改 `frosting-grassland-standard` 波次，避免复现 v32 的 CowardBot、TankBot 和 ZoneControlBot 扰动。
- 不推进 RouteBot 修复；RouteBot 仍作为独立问题记录。

改动：

- `candy-crystal-lance` v5：伤害 `29 -> 30`，冷却保持 `1080ms`，射速保持 `620`，射程保持 `550`，声明单体预算 `27 -> 28`。

下一步门禁：

1. partial candidate validation with overrides
2. materialize full content pack with overrides
3. materialized pack preflight
4. static balance budget review
5. playable content coverage audit
6. GameCore validate-content
7. 71000-71002 all-Bot smoke matrix
8. 如果 smoke 通过，再跑 71000-71009 和 70000-70009 扩样
