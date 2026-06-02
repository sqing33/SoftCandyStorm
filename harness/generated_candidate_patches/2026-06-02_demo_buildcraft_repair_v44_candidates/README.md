# Demo Buildcraft Repair v44 Candidates

本批次基于 v38 继续窄修复，用于测试 Boss 出场后的短窗口远程糖针压力是否能降低 RouteBot 固定椭圆路线胜率，同时保持其他 Bot 的目标区间。

- 状态：generated candidate only
- Accepted content: false
- Runtime integrated: false
- Base pack: `harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v38_full_pack`

目标：

- 只覆盖 `frosting-grassland-standard` 波次，不修改地图尺寸、刷怪距离、武器、被动、敌人或 Boss。
- 把原 `225-300` 秒长段拆成 `225-255` 和 `255-300` 两段。
- 在 `225-255` 秒短窗口提高 `sprinkle-spitter` 权重，用会在玩家位置生成短时伤害 hazard 的远程敌人测试固定路线抗压。
- 相应下调普通追逐、慢速厚血、跳跃和环绕敌人的权重，避免复现 v43 把 ZoneControlBot 抬高的侧向收益。
- `255-300` 秒回到 v38 原权重，避免把整段后半程变成全局压力上调。

改动：

- `frosting-grassland-standard.version`：`24 -> 26`
- `225-255`：`sprinkle-spitter 0.09 -> 0.19`
- `225-255`：降低 `bouncy-gummy`、`sour-gummy`、`sandwich-cookie-creep`、`sticky-bear-gummy`、`soda-bubble`、`licorice-skipper` 和 `sugar-moth`
- `255-300`：沿用 v38 的 `225-300` 原权重

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
