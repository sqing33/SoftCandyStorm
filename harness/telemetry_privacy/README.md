# 遥测隐私策略门禁

本目录用于把 `docs/16_Replay与遥测设计.md` 中的隐私原则落成可校验策略。

当前项目仍以本地 replay / telemetry 为主，任何未来上传型遥测都必须先通过策略审查。

基本流程：

1. 复制 `telemetry_privacy_policy_template.json`，为目标版本填写策略。
2. 运行 `validate_telemetry_privacy_policy.py` 检查默认关闭、显式同意、匿名 session、禁止字段、保留周期和玩家控制项。
3. 用 `runtime_privacy_settings_contract_v0.json` 约束 Runtime 设置页必须提供的关闭开关、隐私说明、删除本地数据和导出本地数据入口。
4. 运行 `validate_runtime_privacy_settings_contract.py` 检查设置契约是否绑定隐私策略和 v0 存档契约。
5. 只有策略和设置契约都通过后，才能把上传型匿名遥测纳入 Release Candidate 证据；Replay 原始输入不得默认上传。

设置契约校验示例：

```bash
python3 harness/telemetry_privacy/validate_runtime_privacy_settings_contract.py \
  harness/telemetry_privacy/runtime_privacy_settings_contract_v0.json \
  --policy harness/telemetry_privacy/telemetry_privacy_policy_template.json \
  --save-contract harness/save_contract/save_state_v0_template.json \
  --report harness/reports/2026-05-26_runtime_privacy_settings_contract_001/runtime_privacy_settings_contract.json \
  --markdown harness/reports/2026-05-26_runtime_privacy_settings_contract_001/summary.md
```

该门禁不替代法律审查，也不代表遥测实现已经接入 Runtime。`runtime_privacy_settings_contract_valid` 只证明预期设置页和数据控制项有可校验契约；真实 Bevy UI、持久化、删除、导出和上传链路仍需要 Runtime 验证。
