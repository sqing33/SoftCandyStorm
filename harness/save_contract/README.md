# 局外存档契约

本目录记录局外成长、图鉴、章节进度、本地数据控制和基地 UI 人工审查的契约。当前有 `save-state-v0` 和 `save-state-v1` 模板；v1 覆盖迁移历史与 `base_ui_state` 形状，但这些证据不能替代 Runtime 运行验证、人工平台路径审查或人工试玩。

这里的校验只做 JSON 存档形状、平台路径策略和人工审查记录完整性检查：

- 局外资源、解锁、图鉴和章节字段是否完整。
- 六章主线骨架是否可被存档保存，其中首章默认解锁，后续章节默认锁定。
- 计数、时间、列表和布尔字段是否为可审计类型。
- 本地数据是否默认不上传。
- 删除存档和导出存档控制项是否存在。
- 存档中是否出现明显禁止的个人身份或本地路径字段。
- 存档、设置、遥测、Replay 和崩溃报告的逻辑平台目录是否有可审计边界。
- F1-F5 基地 UI、选择入口、图鉴导航、候选内容边界和本地数据控件是否有真人审查记录。

Runtime 源码路径现在已有 v1 本地存档读写、v0 到 v1 迁移、逻辑平台数据根、显式原生平台数据根、导出和删除入口：

```bash
cargo run -p game_runtime -- --save-file harness/save/local/profile.json
cargo run -p game_runtime -- --save-file harness/save/local/profile.json --export-save harness/save/local/profile_export.json
cargo run -p game_runtime -- --save-file harness/save/local/profile.json --delete-save
cargo run -p game_runtime -- --platform-data-root platform_user_data/soft-candy-storm
cargo run -p game_runtime -- --native-platform-data-root
```

`--platform-data-root` 会把默认存档、Runtime 设置、本地遥测、Replay 和崩溃报告目录绑定到指定逻辑根；`--native-platform-data-root` 会显式改用系统原生数据目录：macOS 为 `~/Library/Application Support/Soft Candy Storm`，Windows 为 `%APPDATA%/Soft Candy Storm`，Linux / Unix 为 `${XDG_DATA_HOME:-~/.local/share}/soft-candy-storm`。`--save-file` 会读取或创建 `save-state-v1`；如果读到 `save-state-v0`，源码路径会迁移到带 `migration_history` 和 `base_ui_state` 的 v1。局后结算时写回 `MetaProgress`；`--export-save` 导出同形状 JSON；`--delete-save` 必须显式指定 save 文件，只删除该文件。

它不能替代人工平台路径审查、平台隐私审查、基地 UI 删除/导出按钮审查或人工试玩流程。

## 基地 UI 人工审查

基地 UI 人工审查模板位于：

```bash
python3 tools/validate_base_ui_manual_review.py \
  harness/save_contract/base_ui_manual_review_template.json \
  --repo-root . \
  --report harness/reports/2026-05-26_base_ui_manual_review_template_001/base_ui_manual_review.json \
  --markdown harness/reports/2026-05-26_base_ui_manual_review_template_001/summary.md
```

模板默认包含 `TODO` 和 `needs_more_review`，报告结论为 `base_ui_manual_review_invalid`。该门禁要求真人覆盖 F1 概览、F2 章节、F3 图鉴导航、F4 隐私设置、F5 角色 / 地图巡逻准备、本地数据导出 / 删除、剧情 / 素材候选内容边界和证据限制。它不运行 Bevy，不检查截图，不证明 UX 质量，也不能替代人工试玩、内容接受、素材接受、隐私或发布门禁。

## 平台路径策略

平台路径策略位于：

```bash
python3 tools/validate_save_path_policy.py \
  harness/save_contract/platform_save_path_policy_v0.json \
  --report harness/reports/2026-05-26_save_path_policy_v0_001/save_path_policy.json \
  --markdown harness/reports/2026-05-26_save_path_policy_v0_001/summary.md
```

该策略要求存档、Runtime 设置、本地遥测、Replay 和崩溃报告使用逻辑平台目录，不在存档中保存宿主绝对路径或个人身份路径，并要求删除 / 导出只作用于配置的本地数据根。当前结论为 `save_path_policy_valid`，但它只证明策略可校验；Runtime 已有显式原生平台路径解析入口，人工平台路径审查和云存档策略仍未完成。

人工平台路径审查包可用以下命令生成：

```bash
python3 harness/save_contract/create_manual_platform_path_review_packet.py \
  --review-template harness/save_contract/manual_platform_path_review_template.json \
  --repo-root . \
  --out harness/reports/2026-05-26_manual_platform_path_review_packet_001/summary.md
```

该审查包汇总平台路径策略、v0/v1 存档契约、逻辑存储根、禁止路径片段、发布要求、已知 blocker 和 7 个 TODO 检查项。它不填写人工审查结论，不提供平台批准，也不证明 Runtime 的原生路径入口已经通过平台审查或云存档支持。

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

当前计划报告 `save_migration_plan_planned`。它要求迁移保留隐私默认值、本地数据控制、图鉴进度、章节进度、完成局数和最佳存活时间，并在 v1 中新增 `migration_history` 和基地 UI 状态字段。它只是契约和 blocker 记录；Runtime 迁移代码已有源码路径，当前 smoke 已覆盖一个本地 v0 样本迁移，但人工平台路径审查、历史真实用户存档批量迁移和云存档策略仍需后续实现。

Runtime 迁移 smoke 位于：

```bash
python3 tools/run_runtime_save_migration_smoke.py \
  --repo-root . \
  --work-dir /private/tmp/soft-candy-runtime-save-migration-smoke-001 \
  --report harness/reports/2026-05-29_runtime_save_migration_smoke_001/runtime_save_migration_smoke.json \
  --markdown harness/reports/2026-05-29_runtime_save_migration_smoke_001/summary.md
```

当前报告结论为 `runtime_save_migration_smoke_valid`。它实际执行 `game_runtime --save-file <v0> --export-save <v1>`，验证原存档被改写为 `save-state-v1`、导出文件也是 `save-state-v1`、`migration_history` 记录 `completed`，并保留局外资源、解锁、章节、完成局数、最佳存活时间、隐私默认值和本地数据控制。它不替代人工平台路径审查、云存档策略或发布候选验收。
