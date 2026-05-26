# 局外存档契约

本目录记录局外成长、图鉴、章节进度和本地数据控制的存档契约。当前有 `save-state-v0` 和计划中的 `save-state-v1` 模板；v1 只定义契约，不代表 Runtime 已实现迁移。

当前本机 Rust/Mach-O 二进制启动仍被阻塞，因此这里的校验只做 JSON 存档形状和平台路径策略检查：

- 局外资源、解锁、图鉴和章节字段是否完整。
- 六章主线骨架是否可被存档保存，其中首章默认解锁，后续章节默认锁定。
- 计数、时间、列表和布尔字段是否为可审计类型。
- 本地数据是否默认不上传。
- 删除存档和导出存档控制项是否存在。
- 存档中是否出现明显禁止的个人身份或本地路径字段。
- 存档、设置、遥测、Replay 和崩溃报告的逻辑平台目录是否有可审计边界。

Runtime 现在已有 CLI 级 v0 存档读写能力：

```bash
cargo run -p game_runtime -- --save-file harness/save/local/profile.json
cargo run -p game_runtime -- --save-file harness/save/local/profile.json --export-save harness/save/local/profile_export.json
cargo run -p game_runtime -- --save-file harness/save/local/profile.json --delete-save
```

`--save-file` 会读取或创建 `save-state-v0`，局后结算时写回 `MetaProgress`；`--export-save` 导出同形状 JSON；`--delete-save` 必须显式指定 save 文件，只删除该文件。

它不能替代迁移版本、基地 UI 删除/导出按钮、平台隐私审查或人工试玩流程。

## 平台路径策略

平台路径策略位于：

```bash
python3 tools/validate_save_path_policy.py \
  harness/save_contract/platform_save_path_policy_v0.json \
  --report harness/reports/2026-05-26_save_path_policy_v0_001/save_path_policy.json \
  --markdown harness/reports/2026-05-26_save_path_policy_v0_001/summary.md
```

该策略要求存档、Runtime 设置、本地遥测、Replay 和崩溃报告使用逻辑平台目录，不在存档中保存宿主绝对路径或个人身份路径，并要求删除 / 导出只作用于配置的本地数据根。当前结论为 `save_path_policy_valid`，但它只证明策略可校验；Runtime 仍未实现平台原生路径解析，人工平台路径审查和云存档策略也未完成。

人工平台路径审查包可用以下命令生成：

```bash
python3 harness/save_contract/create_manual_platform_path_review_packet.py \
  --review-template harness/save_contract/manual_platform_path_review_template.json \
  --repo-root . \
  --out harness/reports/2026-05-26_manual_platform_path_review_packet_001/summary.md
```

该审查包汇总平台路径策略、v0/v1 存档契约、逻辑存储根、禁止路径片段、发布要求、已知 blocker 和 7 个 TODO 检查项。它不填写人工审查结论，不提供平台批准，也不证明 Runtime 已实现平台路径解析或云存档支持。

人工平台路径审查模板位于：

```bash
python3 tools/validate_manual_platform_path_review.py \
  harness/save_contract/manual_platform_path_review_template.json \
  --repo-root . \
  --report harness/reports/2026-05-26_manual_platform_path_review_template_001/manual_platform_path_review.json \
  --markdown harness/reports/2026-05-26_manual_platform_path_review_template_001/summary.md
```

模板默认包含 `TODO` 和 `needs_more_review`，报告结论为 `manual_platform_path_review_invalid`。它只是后续真人审查的防漏项，不得作为平台审查通过、云存档批准或 Release Candidate ready 证据。

## 迁移计划

当前 v0 存档形状已有首个未来 schema 升级迁移契约，并引用 `save_state_v1_template.json` 作为目标模板：

```bash
python3 tools/validate_save_migration_plan.py \
  harness/save_contract/save_migration_plan_v0_to_v1.json \
  --repo-root . \
  --report /tmp/save_migration_plan.json \
  --markdown /tmp/save_migration_plan.md \
  --allow-planned
```

当前计划报告 `save_migration_plan_planned`。它要求迁移保留隐私默认值、本地数据控制、图鉴进度、章节进度、完成局数和最佳存活时间，并在 v1 中新增 `migration_history` 和基地 UI 状态字段。它只是契约和 blocker 记录；Runtime 迁移代码、平台路径实现和人工平台路径审查仍需后续实现。
