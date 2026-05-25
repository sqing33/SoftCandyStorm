# Phase 4 名录缺口候选

本批次用于回应 `docs/12_阶段路线图.md` 暴露出的 Phase 4 名录数量缺口：Phase 4 目标写的是 12 个被动和 12 个敌人，而当前 `content/base_demo` 名录包含 8 个被动和 8 个普通敌人。

本目录中的内容仅为 AI 生成候选内容，不是 validated content、simulated content、playtest content 或 accepted content。

## 候选内容

- 4 个被动候选：
  - `honey-heart`
  - `peppermint-pocket-watch`
  - `jelly-lens-polish`
  - `cocoa-safety-badge`
- 4 个普通敌人候选：
  - `licorice-skipper`
  - `sugar-moth`
  - `taffy-shieldling`
  - `sprinkle-spitter`

## 门禁状态

- Partial Python validation：通过。
- Full `game_harness validate-candidates`：未运行，受本机 Mach-O 启动阻塞影响。
- Bot simulation：未运行。
- Replay regression：未运行。
- Human review：未运行。

本机二进制启动能力恢复后，下一步应把该候选合并为完整内容包变体，再运行正常 Harness 候选流水线。
