# Demo Buildcraft Repair v28 Candidates

本批次基于 v27 full pack，修复可玩内容覆盖审计中剩余的 P2 被动描述缺口：

- 为 17 个 `passives` 补充 `balance_budget`
- 每个预算包含定位、目标强度、满级影响、协同标签、反制 / 限制和 Bot 风险观察点
- 不修改任何被动数值，不推进正式内容池

状态：

- generated candidate only
- accepted content: false
- runtime integrated: false

本批次是显式覆盖已有被动候选的修复补丁，校验和物化时必须使用 `--allow-overrides`。不得复制到 `content/base_demo`、`accepted_content` 或 Runtime 正式内容目录。
