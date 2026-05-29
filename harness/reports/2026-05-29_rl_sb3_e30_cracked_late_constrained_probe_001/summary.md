# SB3 E30 Cracked Late Constrained Probe

## 结论

- Decision: `sb3_e30_cracked_late_constrained_probe_rejected_no_conversion`
- Parent model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Candidate model: `ppo_cracked_late_constrained_probe.zip`
- Training map: `cracked-star-jar`
- Reward profile: `late-win-conversion`
- Requested timesteps: `128`
- Actual timesteps: `256`
- Anchor time-bucket weights: opening `2.0`, mid `2.0`, late `0.25`
- Repair probe gate: `rl_repair_probe_gate_passed_for_limited_followup`
- Failure case: `harness/failed_cases/fail_20260529_008_sb3_e30_cracked_late_constrained_probe_no_conversion.json`

该 probe 试图把上一轮结论从“不要继续只调 split 秒数”推进到训练期 per-map constrained repair：只在 `cracked-star-jar` 上做小步 `late-win-conversion` PPO 续训，同时用较高 opening/mid anchor 权重保护 parent 的短中窗行为，并降低 late anchor 权重让模型有机会学习 300 秒转换。

结果仍应拒绝。训练期 anchor guard、离线 anchor alignment、e30 / parent 多基线 window regression 和 repair probe gate 都没有触发回归 blocker；但 300 秒 high-pressure 三图仍为 `0.0/0.0/0.0`，`cracked-star-jar` 平均存活只停在 `175.2584s` 的 split-policy 结果和 `220.1403s` 的 standalone 单图评估，仍没有形成胜局转换。handoff state distribution 也显示 candidate 与 parent 在 `120-240s` inherited states 上几乎没有 action-surface separation，post-split argmax agreement 为 `1.0`。

## Anchor 与 No-regression

| Check | Decision | Key metric |
| --- | --- | --- |
| Training guard | `anchor_validation_guard_passed` | validation mean KL `0.108746`, argmax agreement `0.8239` |
| Full-anchor alignment | `behavior_clone_anchor_alignment_within_thresholds` | mean KL `0.105798`, argmax agreement `0.8286` |
| Drift-row alignment | `behavior_clone_anchor_alignment_within_thresholds` | mean KL `0.019888`, argmax agreement `0.965` |
| Regression vs e30 | `policy_window_regression_passed` | blockers `0` |
| Regression vs parent | `policy_window_regression_passed` | blockers `0` |
| Repair gate | `rl_repair_probe_gate_passed_for_limited_followup` | warnings `1`, remaining failures |

## Fixed-window High-pressure

| Window | `soda-creek` | `caramel-workshop` | `cracked-star-jar` | Summary |
| --- | ---: | ---: | ---: | --- |
| `60s` | `0.6667` | `0.6667` | `1.0` | 短窗无回归 |
| `180s` | `0.3333` | `0.6667` | `0.6667` | 中窗无回归但仍非通过 |
| `300s` | `0.0` | `0.0` | `0.0` | 仍需 repair |

## Standalone Evaluation

`ppo_evaluation_report.json` 只在 `cracked-star-jar` 上评估 candidate 本体：

- win rate: `0.0`
- average survival: `220.1403s`
- average level: `7.0`
- average kills: `473.0`
- damage taken average: `120.5501`
- dominant top action: action `1` / `0.2801`

这说明单图小步 constrained continuation 能延长 standalone 生存时间，但没有学到 300 秒终局转换。

## Handoff Distribution

`handoff_state_distribution.json` 使用 parent trace 的 `120-240s` observation 比较 parent 与 candidate：

- samples: `458`
- mean base-to-late KL: `0.000541`
- overall argmax agreement: `1.0`
- post-split argmax agreement: `1.0`
- base top action: action `8` / `28.17%`
- late top action: action `8` / `28.17%`

该结果与上一轮 rejected late branch 诊断一致：candidate 在 parent inherited states 上没有形成足够可用的 late conversion 分支。

## 判断

- 该 checkpoint 不是 policy candidate，也不是 RL acceptance 证据。
- 多基线 no-regression 通过只说明该小步 probe 没有明显破坏 parent；不能掩盖 300 秒三图仍全失败。
- 当前失败不再适合继续靠更改 split 秒数或只做单图小步 continuation 解决。
- 下一步应训练显式 parent late-state branch：直接采样 parent 在 `180-240s` 与 `240-300s` 的失败 / 近失败状态，加入 action-score separation、terminal conversion 和 strict parent-preservation 多基线门禁。

## 输出文件

- `ppo_training_report.json`
- `ppo_evaluation_report.json`
- `ppo_known_exploits.json`
- `ppo_cracked_late_constrained_probe.zip`
- `ppo_cracked_late_constrained_probe_metadata.json`
- `full_anchor_alignment.json`
- `anchor_drift_alignment.json`
- `split_comparison_60s.json`
- `split_comparison_180s.json`
- `split_comparison_300s.json`
- `split_failure_analysis_300s.json`
- `split_failure_analysis_300s.md`
- `split_window_regression_vs_e30.json`
- `split_window_regression_vs_e30.md`
- `split_window_regression_vs_mid_anchor_parent.json`
- `split_window_regression_vs_mid_anchor_parent.md`
- `handoff_state_distribution.json`
- `handoff_state_distribution.md`
- `repair_probe_gate.json`
- `repair_probe_gate.md`
