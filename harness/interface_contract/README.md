# GameCore API 契约

本目录记录 GameCore 对 Runtime、Harness、Replay Bot 和 Python Gym 暴露的公开接口契约。

当前本机 Rust/Mach-O 二进制启动仍被阻塞，因此这里的校验只做源码形状检查：

- 公共 `struct` 是否存在。
- 必需字段是否仍存在。
- 公共 `enum` 变体是否仍存在。
- `GameCore` 必需方法是否仍存在。
- 契约版本、迁移要求和源码路径是否完整。

它不能替代 `cargo test`、Harness replay 回归或 Gym smoke。恢复二进制启动后，仍必须用运行级验证证明接口语义可用。
