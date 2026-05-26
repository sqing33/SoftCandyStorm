# 局外存档契约

本目录记录局外成长、图鉴、章节进度和本地数据控制的 v0 存档契约。

当前本机 Rust/Mach-O 二进制启动仍被阻塞，因此这里的校验只做 JSON 存档形状检查：

- 局外资源、解锁、图鉴和章节字段是否完整。
- 六章主线骨架是否可被存档保存，其中首章默认解锁，后续章节默认锁定。
- 计数、时间、列表和布尔字段是否为可审计类型。
- 本地数据是否默认不上传。
- 删除存档和导出存档控制项是否存在。
- 存档中是否出现明显禁止的个人身份或本地路径字段。

Runtime 现在已有 CLI 级 v0 存档读写能力：

```bash
cargo run -p game_runtime -- --save-file harness/save/local/profile.json
cargo run -p game_runtime -- --save-file harness/save/local/profile.json --export-save harness/save/local/profile_export.json
cargo run -p game_runtime -- --save-file harness/save/local/profile.json --delete-save
```

`--save-file` 会读取或创建 `save-state-v0`，局后结算时写回 `MetaProgress`；`--export-save` 导出同形状 JSON；`--delete-save` 必须显式指定 save 文件，只删除该文件。

它不能替代迁移版本、基地 UI 删除/导出按钮、平台隐私审查或人工试玩流程。

## 迁移计划

当前 v0 存档形状已有首个未来 schema 升级迁移契约：

```bash
python3 tools/validate_save_migration_plan.py \
  harness/save_contract/save_migration_plan_v0_to_v1.json \
  --repo-root . \
  --report /tmp/save_migration_plan.json \
  --markdown /tmp/save_migration_plan.md \
  --allow-planned
```

当前计划报告 `save_migration_plan_planned`。它要求迁移保留隐私默认值、本地数据控制、图鉴进度、章节进度、完成局数和最佳存活时间，并在未来 v1 中新增 `migration_history` 和基地 UI 状态字段。它只是契约和 blocker 记录；Runtime 迁移代码与 v1 存档校验器仍需后续实现。
