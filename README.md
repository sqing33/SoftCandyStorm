# 软糖风暴

《软糖风暴》是一款计划中的可爱糖果风俯视角自动攻击肉鸽生存游戏。

当前已进入 Goal 模式后的 Phase 1 起步：仓库包含设计文档，以及一版最小 headless GameCore / Harness 原型。当前原型用于验证固定 seed、固定 tick、无渲染仿真闭环，还不是正式可玩 Runtime。

## 快速入口

从这里开始读：

- [文档索引](./docs/00_index.md)
- [游戏愿景与设计支柱](./docs/01_游戏愿景与设计支柱.md)
- [核心玩法规格](./docs/02_核心玩法规格.md)
- [Bevy 技术架构计划](./docs/06_Bevy技术架构计划.md)
- [Harness 工程计划](./docs/07_Harness工程计划.md)

## 原型运行

当前可运行的 headless 仿真入口：

```bash
cargo run -p game_harness -- validate-content --content-dir content/base_demo
cargo run -p game_harness -- budget-content --content-dir content/base_demo
cargo run -p game_harness -- simulate --content-dir content/base_demo --seed 12345 --seconds 600 --bot kite
cargo run -p game_harness -- batch --content-dir content/base_demo --seed-start 12345 --seeds 10 --seconds 600 --bot kite
cargo run -p game_harness -- batch --content-dir content/base_demo --seed-start 12345 --seeds 10 --seconds 600 --bot kite --report-dir harness/reports/2026-05-25_kite_batch_001
cargo run -p game_harness -- matrix --content-dir content/base_demo --seed-start 20000 --seeds 3 --seconds 180 --bots random,coward,tank,boss-hunter --report-dir harness/reports/2026-05-25_matrix_smoke_001
cargo run -p game_harness -- replay --content-dir content/base_demo --replay-file harness/reports/2026-05-25_matrix_smoke_001/representative_replays/boss_hunter_seed_20000.json
cargo run -p game_harness -- replay-batch --content-dir content/base_demo --replay-dir harness/reports/2026-05-25_matrix_smoke_001/representative_replays --report-dir harness/reports/2026-05-25_replay_regression_smoke_001
cargo run -p game_harness -- validate-candidates --source-dir harness/generated_candidates --validated-dir harness/validated_candidates --rejected-dir harness/rejected_content --report-dir harness/reports/2026-05-25_candidates_smoke_001
cargo run -p game_harness -- simulate-candidates --source-dir harness/validated_candidates --simulated-dir harness/simulated_candidates --repair-dir harness/repair_queue --seed-start 20000 --seeds 3 --seconds 180 --bots random,coward,tank,boss-hunter --report-dir harness/reports/2026-05-25_candidate_simulation_smoke_001
cargo run -p game_runtime -- --content-dir content/base_demo --seed 12345 --seconds 600
cargo run -p game_runtime -- --content-dir content/base_demo --seed 12345 --seconds 600 --playtest-report harness/telemetry/local/runtime_manual_playtest_001.json --player-skill new
```

带 `--report-dir` 的批量命令会输出 `summary.md`、`metrics.json`、门禁失败记录，以及原型 replay JSON。
`replay-batch` 会递归扫描 replay JSON，并用 strict 模式校验 content hash、升级选项和 final metrics 是否完全复现。
`validate-candidates` 会先做 schema 校验和静态预算门禁，只有两者都通过才会复制到 `harness/validated_candidates`。
`simulate-candidates` 会对 `validated_candidates` 执行 Bot 矩阵，通过后复制到 `harness/simulated_candidates`，未通过则复制到 `harness/repair_queue`。
`game_runtime` 是最小 Bevy 可视化客户端：读取键盘输入，调用同一个 GameCore，再根据 snapshot/events 更新画面、HUD、事件反馈和占位音效。Runtime 操作：WASD/方向键移动，1/2/3 选择升级，P 暂停，R 重开。当前画面加载 `assets/prototype_topdown` 中的程序化 top-down 原型占位纹理，用于替换早期几何色块；当前音效是运行时生成的短 WAV 占位资源，用于验证事件到表现层的链路。AI 生成素材仍需走候选池、记录 prompt 和人工确认。
`game_runtime --playtest-report` 会在本地写入人工试玩捕获 JSON，记录关键可观测样本、事件计数、最终 metrics，并附带人工评分和备注字段；默认写入路径建议放在 `harness/telemetry/local/`。

素材候选后处理入口：

```bash
python3 tools/asset_postprocess.py extract-sprites asset/generated_candidates/2026-05-25_mmx_first_pass/images/runtime_spritesheet_v001_001.jpg --grid 5x5 --out-dir asset/generated_candidates/2026-05-25_mmx_first_pass/processed/runtime_spritesheet_v001 --prefix runtime_sprite --manifest asset/generated_candidates/2026-05-25_mmx_first_pass/metadata/postprocess_runtime_spritesheet_v001.json
```

常用检查：

```bash
cargo fmt --check
cargo clippy --workspace --all-targets
cargo test --workspace
```

## 当前方向

- 游戏名：《软糖风暴》
- 类型：俯视角自动攻击肉鸽生存
- 画风：可爱糖果、软糖、果冻、泡泡、棉花糖
- 技术方向：Bevy / Rust
- AI 测试方向：Python Gymnasium + Stable-Baselines3
- 工程方法：AI Agent + Harness 自动扩内容、自动测试、自动平衡筛选

## 关键原则

1. 游戏核心必须可 headless 仿真。
2. 渲染版游戏只是 GameCore 的一个客户端。
3. AI 可以生成内容，但必须通过 Harness 门禁。
4. Bot 用于发现问题，不替代真人判断乐趣。
5. 规则 Bot 先于 DQN/PPO，RL Bot 作为高级压力测试工具。
