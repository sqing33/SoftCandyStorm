# Demo Buildcraft Repair v46 Candidates

本批次基于 v38 继续窄修复，用于测试更温和的 RouteBot 成型前冲刺扰动是否能保留 v45 的 RouteBot 修复方向，同时减少对其他 Bot 的副作用。

- 状态：generated candidate only
- Accepted content: false
- Runtime integrated: false
- Base pack: `harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v38_full_pack`

目标：

- 只覆盖 `frosting-grassland-standard` 波次，不修改地图尺寸、刷怪距离、武器、被动、敌人、Boss 或事件。
- 把原 `90-210` 秒长段拆成 `90-105`、`105-135` 和 `135-210` 三段。
- 仅在 `105-135` 秒短窗口加入少量 `spicy-gummy`，测试 RouteBot 彩虹糖弹成型前的轻量冲刺扰动。
- 不提高 `licorice-skipper` 权重，避免复现 v45 的 dash/jump 组合过宽副作用。
- `90-105` 和 `135-210` 秒沿用 v38 原权重。

改动：

- `frosting-grassland-standard.version`：`24 -> 28`
- `105-135`：新增 `spicy-gummy 0.05`
- `105-135`：仅降低 `bouncy-gummy` 权重以容纳冲刺敌人
- 其他中期段：沿用 v38 的 `90-210` 原权重

下一步门禁：

1. partial candidate validation with overrides
2. materialize full content pack with overrides
3. materialized pack preflight
4. static balance budget review
5. playable content coverage audit
6. GameCore validate-content
7. isolated GameCore validate-candidates
8. 71000-71002 all-Bot smoke matrix
9. 如果 RouteBot 回到 `2/3` 或其他 Bot 被打坏，记录 failure case 后继续调低或换变量
