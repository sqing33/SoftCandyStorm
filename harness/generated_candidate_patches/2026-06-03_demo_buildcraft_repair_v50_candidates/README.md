# 2026-06-03 Demo Buildcraft Repair v50 Candidates

本批次是 `frosting-grassland` 300 秒可玩 Demo 的内容修复候选，基线为：

```text
harness/generated_candidates/2026-06-03_demo_buildcraft_repair_v49_full_pack
```

## 修复目标

- v49 中 `KiteBot` 仍偏高，说明风筝路线过稳。
- v49 中 `ZoneControlBot` 仍偏低，说明控场构筑拿到控场后收益不稳定。
- v49 中 `RouteBot` 仍偏高，固定路线存在残留拖局问题。

## 本批次改动

- `caramel-sticky-ground`：从玩家附近随机落点改为优先高血敌人附近落点，降低空铺焦糖区域概率，但不使用最近敌人全锁定，避免变成泛用清场武器。
- `bubble-shoes`：峰值机动从 `+45 move_speed` 下调到 `+35 move_speed`，压低长期风筝安全距离。
- `star-spoon`：峰值拾取范围从 `+85 pickup_radius` 下调到 `+75 pickup_radius`，保留经济舒适度，同时降低固定路线吃经验的稳定性。

## 临时探针结论

采用本批次组合的 300 秒 / 10 seed / all Bot 临时矩阵结果：

| Bot | Win Rate | Gate |
|---|---:|---|
| idle | 0% | pass |
| random | 10% | pass |
| coward | 40% | repair |
| greedy | 30% | pass |
| kite | 60% | pass |
| tank | 30% | pass |
| boss-hunter | 70% | pass |
| zone-control | 40% | pass |
| route | 40% | repair |

`KiteBot` 与 `ZoneControlBot` 已回到目标区间；`CowardBot` 与 `RouteBot` 仍需要下一轮 repair。本批次仍是候选内容，不进入正式内容池。

