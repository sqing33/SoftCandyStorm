# 遥测隐私策略门禁

本目录用于把 `docs/16_Replay与遥测设计.md` 中的隐私原则落成可校验策略。

当前项目仍以本地 replay / telemetry 为主，任何未来上传型遥测都必须先通过策略审查。

基本流程：

1. 复制 `telemetry_privacy_policy_template.json`，为目标版本填写策略。
2. 运行 `validate_telemetry_privacy_policy.py` 检查默认关闭、显式同意、匿名 session、禁止字段、保留周期和玩家控制项。
3. 用 `runtime_privacy_settings_contract_v0.json` 约束 Runtime 设置页必须提供的关闭开关、隐私说明、删除本地数据和导出本地数据入口。
4. 运行 `validate_runtime_privacy_settings_contract.py` 检查设置契约是否绑定隐私策略和 v0 存档契约。
5. 真人隐私审查人复制 `manual_privacy_review_template.json`，填写默认关闭、明确同意、raw replay 单独同意、禁止字段、删除 / 导出、本地保留和 Runtime 证据限制等检查项。
6. 运行 `validate_manual_privacy_review.py` 校验人工审查记录完整性。
7. 只有策略、设置契约和人工隐私审查都通过后，才能把上传型匿名遥测纳入 Release Candidate 证据；Replay 原始输入不得默认上传。

设置契约校验示例：

```bash
python3 harness/telemetry_privacy/validate_runtime_privacy_settings_contract.py \
  harness/telemetry_privacy/runtime_privacy_settings_contract_v0.json \
  --policy harness/telemetry_privacy/telemetry_privacy_policy_template.json \
  --save-contract harness/save_contract/save_state_v0_template.json \
  --report harness/reports/2026-05-26_runtime_privacy_settings_contract_001/runtime_privacy_settings_contract.json \
  --markdown harness/reports/2026-05-26_runtime_privacy_settings_contract_001/summary.md
```

该门禁不替代法律审查，也不代表遥测实现已经接入 Runtime。`runtime_privacy_settings_contract_valid` 只证明预期设置页和数据控制项有可校验契约；真实上传链路、发布级导出 / 删除按钮、平台路径和人工隐私审查仍需要后续验证。

人工隐私审查校验示例：

```bash
python3 harness/telemetry_privacy/validate_manual_privacy_review.py \
  harness/telemetry_privacy/reviews/<review>.json \
  --repo-root . \
  --report harness/reports/<report-id>/manual_privacy_review.json \
  --markdown harness/reports/<report-id>/summary.md
```

`manual_privacy_review_template.json` 默认包含 `TODO` 和 `needs_more_review`，不能作为通过证据。人工审查通过也不等于法律批准、上传链路完成或 Release Candidate ready。

当前 Runtime 已实现 CLI 级本地数据控制，并提供 `F4` Bevy 设置页用于显式切换上传型同意项：

```bash
cargo run -p game_runtime -- --print-privacy-notice
cargo run -p game_runtime -- --runtime-settings-file harness/telemetry/local/runtime_settings.json --export-local-data harness/telemetry/local/export.json
cargo run -p game_runtime -- --local-data-dir harness/telemetry/local/manual-smoke --delete-local-data
```

这些命令只处理本地目录，导出默认包括 `harness/telemetry/local/` 和 `harness/replay/`，也可以用 `--local-data-dir <path>` 增加目录。导出会写入 JSON 并附带当前隐私设置；删除必须显式传入至少一个 `--local-data-dir`，只移除这些目录内的文件和空子目录。运行 Runtime 时，`F4` 设置页可用 `7/8/9` 切换上传匿名遥测、raw replay 上传和崩溃报告上传；传入 `--runtime-settings-file` 时切换结果会写回 JSON，未传入时只在当前会话生效。上传传输仍未实现，任何上传型遥测进入 RC 前仍需要人工隐私审查和真实 Runtime 验证。
