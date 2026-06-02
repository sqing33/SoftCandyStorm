# v25 内容巡游客观摘要

- Candidate id: `2026-06-02_demo_buildcraft_repair_v25_full_pack`
- Content hash: `fnv1a64:aab110776109609d`
- Decision: `content_tour_summary_no_reports`
- Reports: `0` / `6`
- Attention items: `0`

## 巡游指标

| Run | Character | Map | Report | Terminal | Time | Level | Kills | Damage Taken | Upgrades | Avg FPS | Attention |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `frosting_jar_keeper` | `jar-keeper` | `frosting-grassland` | `False` | `` |  |  |  |  |  |  | 0 |
| `soda_bubble_courier` | `bubble-courier` | `soda-creek` | `False` | `` |  |  |  |  |  |  | 0 |
| `cotton_pudding_crafter` | `pudding-crafter` | `cotton-cloud-pasture` | `False` | `` |  |  |  |  |  |  | 0 |
| `caramel_sour_plum_doctor` | `sour-plum-doctor` | `caramel-workshop` | `False` | `` |  |  |  |  |  |  | 0 |
| `jelly_cream_knight` | `cream-knight` | `jelly-platform` | `False` | `` |  |  |  |  |  |  | 0 |
| `cracked_jar_keeper` | `jar-keeper` | `cracked-star-jar` | `False` | `` |  |  |  |  |  |  | 0 |

## 巡游重点

- `frosting_jar_keeper`: 新手基准角色和糖霜草地开局
- `soda_bubble_courier`: 速度角色和汽水溪谷泡泡压力
- `cotton_pudding_crafter`: 召唤角色和棉花云群体压力
- `caramel_sour_plum_doctor`: 控制角色和焦糖工坊路线干扰
- `jelly_cream_knight`: 防御角色和果冻月台环形路线
- `cracked_jar_keeper`: 最终地图混合怪潮压力

## 缺失报告

- `harness/telemetry/local/v25_content_tour_frosting_jar_keeper.json`
- `harness/telemetry/local/v25_content_tour_soda_bubble_courier.json`
- `harness/telemetry/local/v25_content_tour_cotton_pudding_crafter.json`
- `harness/telemetry/local/v25_content_tour_caramel_sour_plum_doctor.json`
- `harness/telemetry/local/v25_content_tour_jelly_cream_knight.json`
- `harness/telemetry/local/v25_content_tour_cracked_jar_keeper.json`

## 需要注意

- 无

## 后续行动

- 用 `python3 harness/playtest/run_v25_content_tour.py --next` 继续运行缺失的内容巡游局。
- 根据地图 / 角色表里的客观指标和真人感受，整理具体内容修复项：节奏、怪潮、构筑引导、Boss 可读性或性能。
- 内容巡游只帮助发现问题；v25 是否接受仍必须走 9 局人工试玩、设计审查、最终接受和 lockfile 门禁。

## 限制

- 本工具只汇总可观测 Runtime 指标，不判断乐趣、清晰度或内容是否达标。
- 这些 content-tour 报告是可选巡游记录，不计入 9 局人工 acceptance 证据。
- 使用 demo input、simulation speed 或 auto-exit 生成的报告会被标记，不能作为真人试玩辅助证据。
