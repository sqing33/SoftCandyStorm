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
