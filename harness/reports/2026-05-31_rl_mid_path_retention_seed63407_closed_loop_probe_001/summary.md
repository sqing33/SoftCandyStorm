# Mid Path Retention Seed 63407 Closed-Loop Probe

## 目标

把 `caramel-workshop:63407` 的 `60-180s` path retention 信号从 evaluation-only wrapper 转成真实训练期 `mid-path-retention` objective，验证裸 SB3 checkpoint 是否能修复 target seed，同时保住同 seed parent 的 high-pressure 三窗表现。

## 配置

- Parent：`harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Candidate：`ppo_mid_path_retention_seed63407_probe.zip`
- Reward profile：`mid-path-retention`
- Train map / seed：`caramel-workshop:63407`
- Timesteps：`256`
- Anchor guard：通过，final validation mean KL `0.10678`，argmax agreement `0.8255`
- Evaluation：deterministic policy，default upgrade first option

## Target Follow-Up

`caramel-workshop` seeds `63400-63409`、`300s` 单图 follow-up 中，candidate 相对 parent 有局部修复信号：

| Metric | Parent | Candidate | Delta |
|---|---:|---:|---:|
| Win rate | 0.0 | 0.1 | +0.1 |
| Average survival seconds | 188.1405 | 198.7068 | +10.5663 |
| Damage taken average | 120.3943 | 117.7401 | -2.6542 |
| Average kills | 275.6 | 301.5 | +25.9 |
| Normalized action entropy | 0.8154 | 0.8305 | +0.0151 |

`window_regression_caramel_300s_10seed.json` 使用 action-distribution delta 门禁后仍判定 `policy_window_regression_passed`，blockers 为 `0`。最大单动作 ratio 增幅为 action `3` 的 `+0.0322`，动作分布 L1 delta 为 `0.188`。

## Seed Outcomes

| Seed | Parent | Candidate |
|---:|---|---|
| 63400 | defeat @ 98.8655s | defeat @ 213.7834s |
| 63401 | defeat @ 220.3848s | defeat @ 212.0497s |
| 63402 | defeat @ 41.3330s | defeat @ 40.0997s |
| 63403 | defeat @ 213.7167s | defeat @ 213.8167s |
| 63404 | defeat @ 214.4835s | defeat @ 213.0499s |
| 63405 | defeat @ 214.5169s | defeat @ 138.6673s |
| 63406 | defeat @ 227.1529s | defeat @ 219.4179s |
| 63407 | defeat @ 218.5177s | victory @ 300.0150s |
| 63408 | defeat @ 221.2850s | defeat @ 221.3183s |
| 63409 | defeat @ 211.1495s | defeat @ 214.8503s |

修复确实命中 target seed `63407`，但没有修复 seed `63402` opening death，并且 seed `63405` 明显回退。

## High-Pressure Parent Preservation

同 seed `63400-63402` high-pressure 三图 `60/180/300s` 对比显示，candidate 没有通过 parent-preservation gate：

| Window | Map | Parent win | Candidate win | Survival delta |
|---|---|---:|---:|---:|
| 60s | soda-creek | 0.6667 | 0.6667 | +0.0333 |
| 60s | caramel-workshop | 0.6667 | 0.3333 | -4.5555 |
| 60s | cracked-star-jar | 1.0 | 1.0 | 0.0 |
| 180s | soda-creek | 0.6667 | 0.6667 | +0.0666 |
| 180s | caramel-workshop | 0.3333 | 0.6667 | +20.7592 |
| 180s | cracked-star-jar | 1.0 | 1.0 | 0.0 |
| 300s | soda-creek | 0.0 | 0.0 | +0.9224 |
| 300s | caramel-workshop | 0.0 | 0.0 | +35.1165 |
| 300s | cracked-star-jar | 0.0 | 0.0 | +0.3111 |

`window_regression_high_pressure_vs_parent.json` 判定为 `policy_window_regression_failed`，blockers 为：

- `60s/caramel-workshop`: win rate delta `-0.3334`
- `180s/cracked-star-jar`: action distribution L1 delta `0.4646` > `0.45`
- `300s/caramel-workshop`: action distribution L1 delta `0.5872` > `0.45`

## 结论

结论：`repair`，但拒绝推进为 policy candidate、stage 03 或 RL test Bot。

`mid-path-retention` 训练期 objective 能把 target seed `63407` 转胜，并在 10 seed caramel follow-up 中相对 parent 得到局部改善；但单 seed 256 timestep continuation 已经破坏 high-pressure parent-preservation，尤其重新打开 `60s/caramel-workshop` 短窗回归并引入动作分布漂移。因此该分支只能作为“60-180s path retention objective 有信号”的诊断证据。

## 下一步

- 不要继续加长该 checkpoint。
- 下一轮如果继续 closed-loop，应加入训练中 `60s/caramel-workshop` hard preflight 或多地图/多 seed early-stop。
- 需要把 `63402` opening repair 与 `63407` mid-path retention 分开处理，避免单一 shared PPO continuation 在两个 seed failure mode 之间搬运回归。
