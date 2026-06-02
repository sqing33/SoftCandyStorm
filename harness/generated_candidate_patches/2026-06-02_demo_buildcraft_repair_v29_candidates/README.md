# Demo Buildcraft Repair v29 Candidates

本批次基于 v28 full pack，修复静态预算报告中的敌人威胁声明 warning：

- `sprinkle-spitter` 的 `spawn_budget.threat` 从 `2.05` 调整为 `1.75`
- 保留远程吐糖针的压力定位，不修改生命、速度、伤害、行为或正式内容池
- 调整后的威胁仍高于基础接触威胁，但落在静态预算允许偏差范围内

状态：

- generated candidate only
- accepted content: false
- runtime integrated: false

本批次是显式覆盖已有敌人候选的修复补丁，校验和物化时必须使用 `--allow-overrides`。不得复制到 `content/base_demo`、`accepted_content` 或 Runtime 正式内容目录。
