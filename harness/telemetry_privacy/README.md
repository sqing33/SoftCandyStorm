# 遥测隐私策略门禁

本目录用于把 `docs/16_Replay与遥测设计.md` 中的隐私原则落成可校验策略。

当前项目仍以本地 replay / telemetry 为主，任何未来上传型遥测都必须先通过策略审查。

基本流程：

1. 复制 `telemetry_privacy_policy_template.json`，为目标版本填写策略。
2. 运行 `validate_telemetry_privacy_policy.py` 检查默认关闭、显式同意、匿名 session、禁止字段、保留周期和玩家控制项。
3. 只有策略通过后，才能把上传型匿名遥测纳入 Release Candidate 证据；Replay 原始输入不得默认上传。

该门禁不替代法律审查，也不代表遥测实现已经接入 Runtime。
