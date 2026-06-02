# v25 快速试玩客观摘要

- Candidate id: `2026-06-02_demo_buildcraft_repair_v25_full_pack`
- Content hash: `fnv1a64:aab110776109609d`
- Decision: `quick_play_summary_no_reports`
- Reports: `0` / `6`
- Attention items: `0`

## 快速试玩指标

| Preset | Character | Map | Report | Terminal | Time | Level | Kills | Damage Taken | Upgrades | Avg FPS | Attention |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `default` | `jar-keeper` | `frosting-grassland` | `False` | `` |  |  |  |  |  |  | 0 |
| `speed` | `bubble-courier` | `soda-creek` | `False` | `` |  |  |  |  |  |  | 0 |
| `summon` | `pudding-crafter` | `cotton-cloud-pasture` | `False` | `` |  |  |  |  |  |  | 0 |
| `control` | `sour-plum-doctor` | `caramel-workshop` | `False` | `` |  |  |  |  |  |  | 0 |
| `defense` | `cream-knight` | `jelly-platform` | `False` | `` |  |  |  |  |  |  | 0 |
| `final` | `jar-keeper` | `cracked-star-jar` | `False` | `` |  |  |  |  |  |  | 0 |

## 试玩重点

- `default`: 糖罐守护员和糖霜草地基准体验
- `speed`: 泡泡邮差和汽水溪谷移动压力
- `summon`: 布丁工匠和棉花云群体压力
- `control`: 酸梅博士和焦糖工坊路线干扰
- `defense`: 奶油骑士和果冻月台环形路线
- `final`: 裂星糖罐混合怪潮压力

## 缺失报告

- `harness/telemetry/local/v25_quick_play_default.json`
- `harness/telemetry/local/v25_quick_play_speed.json`
- `harness/telemetry/local/v25_quick_play_summon.json`
- `harness/telemetry/local/v25_quick_play_control.json`
- `harness/telemetry/local/v25_quick_play_defense.json`
- `harness/telemetry/local/v25_quick_play_final.json`

## 需要注意

- 无

## 后续行动

- 用 `python3 harness/playtest/play_v25_candidate.py` 运行默认新手局，或用 `--list` 选择其它 quick-play 预设。
- 根据 quick-play 客观指标和真人感受，整理默认体验、构筑引导、地图节奏、Boss 可读性或性能修复项。
- quick-play 只帮助快速试玩和记录；v25 是否接受仍必须走 9 局人工试玩、设计审查、最终接受和 lockfile 门禁。

## 限制

- 本工具只汇总可观测 Runtime 指标，不判断乐趣、清晰度或内容是否达标。
- 这些 quick-play 报告是便利试玩记录，不计入 9 局人工 acceptance 证据。
- 使用 demo input、simulation speed 或 auto-exit 生成的报告会被标记，不能作为真人试玩辅助证据。
