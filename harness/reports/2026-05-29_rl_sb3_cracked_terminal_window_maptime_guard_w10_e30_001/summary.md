# SB3 Cracked Terminal Window Map-Time Guard W10 E30

## 结论

- Decision: `action_distribution_guard_passed`
- Scope: `overall,map_time_buckets`
- Checked slices: `10`
- Model: `ppo_cracked_terminal_window_maptime_guard_w10_e30.zip`

该 probe 复用 terminal-window `w10` distillation 配置，但将 action-distribution guard 限定到 `overall` 与 `map_time_buckets`，避免把刻意集中的 `anchor_drift_diagnostic` 小切片误判为策略塌缩。

## Guard 结果

配置：

- max dominant ratio: `0.45`
- min normalized argmax entropy: `0.55`
- min sample count: `24`
- scope: `overall,map_time_buckets`

结果：

- guard decision: `action_distribution_guard_passed`
- blockers: `0`
- overall dominant action: action `3`, ratio `0.1693`
- `caramel-workshop::opening_lt_60`: dominant action `2`, ratio `0.3167`, normalized argmax entropy `0.7524`
- `caramel-workshop::mid_60_to_180`: dominant action `3`, ratio `0.2041`, normalized argmax entropy `0.9126`

## 解读

map/time 离线动作分布没有复现上一轮在线 `60s/caramel-workshop` dominant action ratio blocker。该结果说明 action-distribution guard 可以记录并阻止明显离线动作塌缩，但它不能替代 online fixed-window no-regression。terminal-window `w10` 仍以既有 high-pressure / no-regression 结果为准：300 秒三图仍未转胜，且 `60s/caramel-workshop` 在线 dominant-action blocker 仍需通过在线窗口门禁处理。

## 下一步

- 不继续做单参数 terminal-window weight 扫描。
- 若继续该方向，应转向显式 terminal-conversion branch，或实现能比较 baseline/candidate online action distribution delta 的专门门禁。
- 任何后续 checkpoint 仍必须跑 full-anchor alignment、60 / 180 / 300 秒 high-pressure、e30 + parent no-regression、failure analysis 和 repair-probe gate。
