# Docs Implementation Coverage Validation

- Source: `harness/docs_implementation_coverage.json`
- Decision: `docs_implementation_incomplete`
- Docs: 20 / 20
- Incomplete docs: 18

## Doc Status

| Status | Count |
|---|---:|
| `complete` | 2 |
| `partial` | 18 |

## Item Status

| Status | Count |
|---|---:|
| `blocked` | 4 |
| `complete` | 2 |
| `partial` | 14 |

## Docs

| Doc | Status | Coverage | Incomplete |
|---|---|---:|---:|
| `docs/00_index.md` | `complete` | 1 | 0 |
| `docs/01_游戏愿景与设计支柱.md` | `partial` | 1 | 1 |
| `docs/02_核心玩法规格.md` | `partial` | 1 | 1 |
| `docs/03_世界观与剧情大纲.md` | `partial` | 1 | 1 |
| `docs/04_内容系统与素材库.md` | `partial` | 1 | 1 |
| `docs/05_美术与音频素材计划.md` | `partial` | 1 | 1 |
| `docs/06_Bevy技术架构计划.md` | `partial` | 1 | 1 |
| `docs/07_Harness工程计划.md` | `partial` | 1 | 1 |
| `docs/08_Bot测试计划.md` | `partial` | 1 | 1 |
| `docs/09_AI_Bot训练计划.md` | `partial` | 1 | 1 |
| `docs/10_AI内容生成流水线.md` | `partial` | 1 | 1 |
| `docs/11_测试指标与上线门禁.md` | `partial` | 1 | 1 |
| `docs/12_阶段路线图.md` | `partial` | 1 | 1 |
| `docs/13_内容数据Schema设计.md` | `partial` | 1 | 1 |
| `docs/14_GameCore接口规格.md` | `partial` | 1 | 1 |
| `docs/15_经济与数值平衡模型.md` | `partial` | 1 | 1 |
| `docs/16_Replay与遥测设计.md` | `partial` | 1 | 1 |
| `docs/17_素材生成Prompt库.md` | `partial` | 1 | 1 |
| `docs/18_完整游戏流程与局外成长.md` | `partial` | 1 | 1 |
| `docs/19_Goal模式开发约定.md` | `complete` | 1 | 0 |

## Errors

- None

## Warnings

- None

## Limitations

- This validator checks the coverage ledger and evidence path existence only.
- It does not execute Rust, Bevy, Harness simulations, Replay, performance tests, or manual playtests.
- A complete decision requires every docs/00-19 entry and every coverage item to be marked complete or not_applicable with existing evidence.
