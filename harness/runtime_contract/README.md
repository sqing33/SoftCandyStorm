# Runtime 源码形状契约

本目录记录 Runtime 在二进制执行恢复前可静态检查的用户界面和本地数据控制边界。

当前本机 Rust/Mach-O 二进制启动仍被阻塞，因此这里的校验只做源码形状检查：

- CLI 是否保留隐私设置、本地数据导出 / 删除、存档导出 / 删除入口。
- Runtime 是否保留 F1/F2/F3/F4 局外面板视图。
- F4 设置页是否仍显示上传匿名遥测、raw replay 上传、崩溃报告上传和 `not_implemented` 上传传输提示。
- 上传同意是否仍由 `7/8/9` 显式切换。
- 删除本地数据和删除存档是否仍需要显式路径。

它不能替代 `cargo test`、Bevy Runtime smoke、人工试玩或平台路径审查。恢复二进制启动后，仍必须用运行级验证证明这些入口真实可用。

校验示例：

```bash
python3 harness/runtime_contract/validate_runtime_surface_contract.py \
  harness/runtime_contract/runtime_surface_contract_v0.json \
  --repo-root . \
  --report harness/reports/2026-05-26_runtime_surface_contract_001/runtime_surface_contract.json \
  --markdown harness/reports/2026-05-26_runtime_surface_contract_001/summary.md
```
