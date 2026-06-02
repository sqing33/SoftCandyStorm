# Demo Buildcraft Repair v45 Candidates

本批次基于 v38 继续窄修复，用于测试 RouteBot 在彩虹糖弹成型前的早期稳定性扰动是否能降低固定椭圆路线胜率，同时保持其他 Bot 的目标区间。

- 状态：generated candidate only
- Accepted content: false
- Runtime integrated: false
- Base pack: `harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v38_full_pack`

目标：

- 只覆盖 `frosting-grassland-standard` 波次，不修改地图尺寸、刷怪距离、武器、被动、敌人、Boss 或事件。
- 把原 `90-210` 秒长段拆成 `90-150` 和 `150-210` 两段。
- 在 `90-150` 秒短窗口加入少量 `spicy-gummy`，并略微提高 `licorice-skipper` 权重，在 RouteBot 升满彩虹糖弹前测试冲刺 / 跳跃扰动。
- 相应下调 `bouncy-gummy`、`sour-gummy`、`sticky-bear-gummy` 和 `sugar-moth`，避免总压力变成简单全局抬高。
- `150-210` 秒回到 v38 原权重，避免影响 Boss 入场前整段节奏。

改动：

- `frosting-grassland-standard.version`：`24 -> 27`
- `90-150`：新增 `spicy-gummy 0.07`
- `90-150`：`licorice-skipper 0.08 -> 0.13`
- `90-150`：相应降低基础追逐和环绕敌人权重
- `150-210`：沿用 v38 的 `90-210` 原权重

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
