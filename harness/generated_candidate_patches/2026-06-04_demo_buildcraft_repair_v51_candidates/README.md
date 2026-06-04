# 2026-06-04 Demo Buildcraft Repair v51 Candidates

本批次是 `frosting-grassland` 300 秒可玩 Demo 的内容修复候选，基线为：

```text
harness/generated_candidates/2026-06-03_demo_buildcraft_repair_v50_full_pack
```

## 修复目标

- v50 中 `CowardBot` 仍偏高，说明低技能保守路线在 Boss 后半段还有过稳窗口。
- v50 中 `RouteBot` 仍偏高，固定椭圆路线仍能在部分 seed 稳定拖到胜利。
- 保留 v50 已修好的 `KiteBot` 与 `ZoneControlBot` 区间，不再使用削移动、削拾取或缩地图这类全局杠杆。

## 本批次改动

- 只覆盖 `frosting-grassland-standard` 波次，不修改地图尺寸、刷怪距离、武器、被动、敌人、Boss、事件或 Runtime 正式内容。
- 将原本 `225-300` 秒单段拆成 `225-255` 与 `255-300` 两段。
- `225-255` 秒：小幅提高 `max_alive` 到 `74`，把 `bouncy-gummy` 从 `0.30` 降到 `0.25`，提高 `licorice-skipper`、`sugar-moth` 的扰动权重。
- `255-300` 秒：小幅提高 `max_alive` 到 `76`，继续降低基础小怪占比，提高 `licorice-skipper`、`sugar-moth` 与 `sprinkle-spitter` 权重，让 Boss 后半段更能打断纯保守路线。

## 临时探针结论

采用本批次波次改动的 300 秒 / 10 seed / all Bot 临时矩阵结果：

| Bot | Win Rate | Gate |
|---|---:|---|
| idle | 0% | pass |
| random | 0% | pass |
| coward | 30% | pass |
| greedy | 30% | pass |
| kite | 60% | pass |
| tank | 30% | pass |
| boss-hunter | 70% | pass |
| zone-control | 40% | pass |
| route | 40% | repair |

`CowardBot` 已回到 10%-35% 目标区间；`RouteBot` 仍为 40%，本批次把它记录为下一轮专门 failure case，不为了硬压固定路线而牵连正常可玩体验。本批次仍是候选内容，不进入正式内容池。

## 下一步门禁

1. partial candidate validation with overrides
2. materialize full content pack with overrides
3. materialized pack preflight
4. static balance budget review
5. playable content coverage audit
6. GameCore validate-content
7. isolated GameCore validate-candidates
8. 300 秒 / 10 seed / all Bot 矩阵
9. 记录 `RouteBot` 残留 failure case 后继续下一轮修复
