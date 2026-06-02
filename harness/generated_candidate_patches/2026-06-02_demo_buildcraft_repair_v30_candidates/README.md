# Demo Buildcraft Repair v30 Candidates

本批次是 v29 的窄修复候选，只用于继续打磨玩家可试玩的糖霜草地 300 秒 Demo。

- 状态：generated candidate only
- Accepted content: false
- Runtime integrated: false
- Base pack: `harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v29_full_pack`

目标：

- 降低 v29 在 `71000-71009` seed 窗口里 KiteBot 和 RouteBot 的过稳问题。
- 轻微提高 ZoneControlBot 在 Boss 后窗口的控制收益。
- 避免全局武器增强、Boss 削弱、XP 大改或 Harness 阈值调整。

改动：

- `caramel-sticky-ground` v2：小幅增加区域半径、成长半径和持续时间，让控制路线更能处理慢速怪潮。
- `frosting-grassland-standard` v25：在 210-300 秒少量加入 `caramel-slime`，用可读地面风险压缩固定路线和风筝安全路径。

下一步门禁：

1. partial candidate validation with overrides
2. materialize full pack with overrides
3. materialized pack preflight
4. static balance budget review
5. playable content coverage audit
6. GameCore validate-content
7. Bot matrix smoke
8. Replay regression and human review before any acceptance
