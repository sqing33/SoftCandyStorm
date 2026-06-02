# Demo Buildcraft Repair v32 Candidates

本批次基于 v31 继续窄修复，保留 v31 已经有效的移动收益收敛，不继承 v30 的焦糖黏地增强。

- 状态：generated candidate only
- Accepted content: false
- Runtime integrated: false
- Base pack: `harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v31_full_pack`

目标：

- 让 BossHunterBot 在没有稳定抽到 `star-sugar-ray` 时，也能通过 `candy-crystal-lance` 获得更可靠的 Boss 窗口输出。
- 只在 225-300 秒增加少量路线打断和远程压力，压低 RouteBot 的固定椭圆路线胜率。
- 不改全局防御、不改 Boss 血量、不降低敌人压力，避免把 RouteBot 进一步放大。

改动：

- `candy-crystal-lance` v5：伤害 `29 -> 31`，冷却 `1080ms -> 1040ms`，每级伤害 `10 -> 11`，声明单体预算 `27 -> 30`。
- `frosting-grassland-standard` v25：225-300 秒波段降低 `bouncy-gummy` 权重，把少量权重转给 `licorice-skipper`、`sugar-moth` 和 `sprinkle-spitter`。

下一步门禁：

1. partial candidate validation with overrides
2. materialize full content pack with overrides
3. materialized pack preflight
4. static balance budget review
5. playable content coverage audit
6. GameCore validate-content
7. 71000-71002 all-Bot smoke matrix
8. 如果 smoke 通过，再跑 71000-71009 和 70000-70009 扩样
