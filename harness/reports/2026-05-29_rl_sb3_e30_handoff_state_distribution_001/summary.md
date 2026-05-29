# SB3 E30 Handoff State Distribution Diagnostic

## 结论

- Decision: `sb3_e30_handoff_state_distribution_recorded_no_policy_separation`
- Base model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Late branch: `harness/reports/2026-05-29_rl_sb3_e30_opening_mid_retention_late_probe_001/ppo_e30_opening_mid_retention_late_probe.zip`
- Trace source: `cracked-star-jar` 180s split policy, 300s evaluation, failed episodes only
- Trace count: `3`
- Handoff samples: `458`
- Handoff window: `120s` to `240s`
- Failure case: `harness/failed_cases/fail_20260529_007_sb3_e30_handoff_state_no_policy_separation.json`

该诊断复现 `cracked-star-jar` 的 180s split policy，并在带 observation 的失败 trace 上同时计算 parent 和 late branch 的 action score，用于判断 split 失败是因为 late branch 接不住 parent 交来的状态，还是因为 late branch 在 handoff window 内没有形成有效策略差异。

结果显示不是状态分布陌生导致的接力失败，而是 late branch 在 handoff 状态上几乎没有区别于 parent。120-240 秒窗口 overall base-to-late mean KL 只有 `0.000491`，argmax agreement 为 `0.9978`；post-split 的 220 个样本中 argmax agreement 为 `1.0`，base / late top action distribution 完全一致。也就是说，`180s` dispatch 介入了正确时间段，但没有提供新的行动面。

## Handoff Distribution

| Window | Samples | Mean Base-to-late KL | Argmax Agreement | Base Top | Late Top | Health Mean | Boundary Min Mean |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `pre_split` | `238` | `0.000610` | `0.9958` | `8` / `31.93%` | `8` / `31.93%` | `74.6637` | `15.6039` |
| `post_split` | `220` | `0.000362` | `1.0000` | `5` / `31.36%` | `5` / `31.36%` | `54.6584` | `63.3480` |

## Split Reproduction

Focused trace run 复现了上一轮 180s split 的失败面：

| Seed | Result | Survival | Dominant Action |
| --- | --- | ---: | --- |
| `63100` | defeat | `56.8661s` | `5` / `54.40%` |
| `63101` | defeat | `230.5203s` | `5` / `33.00%` |
| `63102` | defeat | `238.3886s` | `1` / `38.18%` |

300 秒 `cracked-star-jar` focused eval 仍为 `0.0` win rate，平均存活 `175.2584s`。

## 判断

- 继续移动 split 秒数没有充分依据；当前 base / late pair 在 120-240 秒 handoff 状态上几乎等价。
- late branch 之前的 `cracked-star-jar` 300 秒恢复信号更可能来自完整轨迹早中期分布变化，而不是可以单独移植的 late-only 行动能力。
- 下一步应转向训练期 per-map constrained repair，或构造只针对 parent late states 的分支训练，并显式要求 action-score separation / terminal conversion，同时继续跑 e30 与 parent 多基线 no-regression gate。
- 该诊断不是 policy candidate，也不是 RL acceptance 证据。

## 输出文件

- `split_180_eval_300s.json`
- `split_180_traces/*.json`
- `handoff_state_distribution.json`
- `handoff_state_distribution.md`
