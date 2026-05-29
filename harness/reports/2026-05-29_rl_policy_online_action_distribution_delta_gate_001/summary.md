# RL Policy Online Action Distribution Delta Gate

## 结论

- Decision: `policy_window_regression_failed`
- Validator: `tools/validate_policy_window_regression.py`
- Baseline: `2026-05-28_rl_sb3_supervised_realign_full_anchor_drift_w40_e30_001`
- Candidate: `2026-05-29_rl_sb3_cracked_terminal_window_risk_distill_w10_e30_001`
- Windows: `60s`, `180s`, `300s`
- Blockers: `17`

本次补强 fixed-window no-regression validator，让它不只比较 win rate、平均存活和 dominant action ratio，也能读取 online comparison JSON 里每张图的完整 `policy.summary.action_distribution`，并计算：

- 单动作 ratio 最大增幅
- 完整动作分布 L1 delta
- normalized action entropy delta

## Smoke 结果

使用 e30 supervised re-alignment checkpoint 作为 baseline、terminal-window `w10` scoped distill 作为 candidate 复跑三窗对比。新增 action-distribution delta 门禁继续拒绝该 candidate，说明离线 map/time guard 通过并不能替代在线窗口分布回归：

- `60s/caramel-workshop`: dominant ratio `+0.2268`，action `7` ratio `+0.2421`，L1 delta `0.7526`，entropy delta `-0.2752`
- `60s/soda-creek`: action `1` ratio `+0.3702`，L1 delta `0.8214`
- `300s/soda-creek`: action `1` ratio `+0.3047`，L1 delta `0.7617`，entropy delta `-0.1548`
- `180s/caramel-workshop`: action `5` ratio `+0.2137`，L1 delta `0.7067`

该结果把原先的 `60s/caramel-workshop` dominant-action blocker 扩展成更完整的在线分布漂移证据：即使个别窗口的 win rate / survival 没有回退，动作分布仍可能明显偏离 baseline。

## 验证

已通过：

```bash
env PYTHONPYCACHEPREFIX=/private/tmp/soft-candy-pycache python3 tools/test_validate_policy_window_regression.py
```

结果：`8` tests passed。

真实报告：

- `window_regression_action_delta_vs_e30.json`
- `window_regression_action_delta_vs_e30.md`

## 限制

- 这是 repair / no-regression evidence gate，不是 RL acceptance。
- 阈值用于阻止明显在线分布漂移；它不能证明策略好玩、平衡或可发布。
- 后续 terminal-conversion branch 仍必须继续跑 full-anchor alignment、60 / 180 / 300 秒 high-pressure、e30 + parent no-regression、failure analysis 和 repair-probe gate。
