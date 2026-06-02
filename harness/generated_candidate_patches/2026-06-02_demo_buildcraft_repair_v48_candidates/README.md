# Demo Buildcraft Repair v48 Candidates

本批次基于 v38 继续窄修复，用于测试 Boss 入场窗口的现有敌人池重分配是否能降低 RouteBot 固定椭圆路线胜率，同时保持其他 Bot 的目标区间。

- 状态：generated candidate only
- Accepted content: false
- Runtime integrated: false
- Base pack: `harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v38_full_pack`

目标：

- 只覆盖 `frosting-grassland-standard` 波次，不修改地图尺寸、刷怪距离、武器、被动、敌人、Boss 或事件。
- 只调整 `210-225` 秒 Boss 入场窗口的既有敌人权重。
- 用更多 `sour-gummy`、`licorice-skipper` 和 `sugar-moth` 打断固定路线，同时降低 `bouncy-gummy` 和 `sandwich-cookie-creep`，避免过度提高整体血量压力。
- `225` 秒后回到 v38 原权重，避免把整段后半程都变成全局压力上调。

改动：

- `frosting-grassland-standard.version`：`24 -> 29`
- `210-225`：`bouncy-gummy 0.30 -> 0.19`
- `210-225`：`sour-gummy 0.12 -> 0.18`
- `210-225`：`sandwich-cookie-creep 0.16 -> 0.14`
- `210-225`：`licorice-skipper 0.10 -> 0.14`
- `210-225`：`sugar-moth 0.07 -> 0.10`
- 其他波段：沿用 v38 原权重

探针结果：

- `/tmp/scs_route_tune/postboss_210_225_l14_m10_sour18`
- 300 秒 / 3 seed / all Bot 临时矩阵中 9 个 Bot 全部通过目标区间。

下一步门禁：

1. partial candidate validation with overrides
2. materialize full content pack with overrides
3. materialized pack preflight
4. static balance budget review
5. playable content coverage audit
6. GameCore validate-content
7. isolated GameCore validate-candidates
8. 71000-71002 all-Bot smoke matrix
9. 如果正式 v48 与探针结果不一致，记录 failure case 后继续修复
