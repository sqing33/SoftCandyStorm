# Demo Buildcraft Repair v47 Candidates

本批次基于 v38 继续窄修复，用于测试低经验轻冲刺敌人是否能保留 v46 对 RouteBot 固定路线的扰动，同时减少普通 `spicy-gummy` 带来的 XP 和成长节奏副作用。

- 状态：generated candidate only
- Accepted content: false
- Runtime integrated: false
- Base pack: `harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v38_full_pack`

目标：

- 新增候选敌人 `pepper-spark-gummy`，只存在于本候选补丁和物化候选包中。
- 该敌人保留可读蓄力冲刺，但 XP 降到基础小怪水平，避免喂强 Greedy、Tank 和 ZoneControl。
- 只覆盖 `frosting-grassland-standard` 波次，不修改地图尺寸、刷怪距离、武器、被动、Boss 或事件。
- 只在 `105-135` 秒短窗口加入少量 `pepper-spark-gummy`，其余中期段沿用 v38 原权重。

改动：

- 新增 `enemies/pepper-spark-gummy.json`
- `frosting-grassland-standard.version`：`24 -> 29`
- `105-135`：新增 `pepper-spark-gummy 0.05`
- `105-135`：仅降低 `bouncy-gummy` 权重以容纳轻冲刺敌人
- 其他中后期段：沿用 v38/v46 已验证结构

下一步门禁：

1. partial candidate validation with overrides
2. materialize full content pack with overrides
3. materialized pack preflight
4. static balance budget review
5. playable content coverage audit
6. GameCore validate-content
7. isolated GameCore validate-candidates
8. 71000-71002 all-Bot smoke matrix
9. 如果 RouteBot 回到 `2/3` 或其他 Bot 被打坏，记录 failure case 后继续修复
