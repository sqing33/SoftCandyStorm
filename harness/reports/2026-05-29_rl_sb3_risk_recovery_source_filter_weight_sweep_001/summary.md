# SB3 Risk Recovery Source-filter Weight Sweep

## 结论

- Decision: `sb3_risk_recovery_source_filter_weight_sweep_rejected`
- Clean risk samples: `424`
- Distillation mode: teacher probabilities for retention anchors, `top_k_scores` override for `risk_recovery_supervision` only
- Drift anchor weight: `40x`
- Risk sample weights tested: `5x`, `7x`, `10x`
- Required baselines: e30 supervised re-align and mid-anchor parent
- Final repair gate: `rl_repair_probe_gate_failed`
- Failure case: `harness/failed_cases/fail_20260529_010_sb3_risk_recovery_source_filter_weight_sweep.json`

本 sweep 验证了一个更精确的 learned branch 入口：`distill_behavior_clone_to_sb3.py` 现在可以保留普通 retention / edge recovery 样本的 teacher probability target，只对 clean parent late-state `risk_recovery_supervision` rows 覆写为 repair soft target。该入口能让离线 anchor alignment 维持在阈值内，但 clean risk samples 仍没有形成可接受的 300 秒多图转换。

## Tooling

- `feat(rl): 支持蒸馏修复样本目标覆写`
- `feat(rl): 支持蒸馏修复样本来源过滤`

新增参数：

- `--recovery-target-mode top_k_scores`
- `--recovery-target-sources risk`
- `--recovery-soft-target-primary-mass 0.65`
- `--recovery-soft-target-top-k 3`

相关测试：

- `python/train/test_distill_behavior_clone_to_sb3.py`
- `python/train/test_train_behavior_clone.py`

## Probe Matrix

| Probe | Distill Inputs | Full Anchor | 300s Result | Repair Gate |
| --- | --- | --- | --- | --- |
| broad recovery `w10` | edge + risk override | failed: `opening_lt_60 mean_kl 0.263164 > 0.25` | not run | rejected preflight |
| risk-only dataset `w10` | no edge retention data | failed: overall agreement `0.7817 < 0.8` | not run | rejected preflight |
| source-filtered `w10` | edge retained, risk override | pass: mean KL `0.135749`, agreement `0.8078` | `0.0 / 0.0 / 0.3333` | failed, `14` blockers |
| source-filtered `w7` | edge retained, risk override | pass: mean KL `0.123632`, agreement `0.8175` | `0.0 / 0.0 / 0.0` | failed, `3` blockers |
| source-filtered `w5` | edge retained, risk override | pass: mean KL `0.116269`, agreement `0.8236` | `0.0 / 0.0 / 0.0` | failed, `4` blockers |

Map order for 300s result: `soda-creek / caramel-workshop / cracked-star-jar`.

## Findings

- `w10` is the only learned candidate in this sweep that produced a 300 秒 victory signal: `cracked-star-jar` reached `0.3333` win rate and `270.4527s` average survival.
- That `w10` gain is not usable: e30 and parent required no-regression both failed, including `caramel-workshop` 180 秒 win rate regression and large `soda-creek` / `caramel-workshop` 300 秒 survival drops.
- `w7` and `w5` reduce blockers and preserve offline anchor alignment, but they lose all 300 秒 wins. They are better retention experiments, not terminal-conversion fixes.
- All accepted-alignment source-filtered probes still fail repair gate, so none can become a policy candidate, RL acceptance evidence, or stage 03 input.

## Next Step

Do not keep raising global risk sample weight. The next repair should split the objective by map or phase: preserve `soda-creek` opening/mid and `caramel-workshop` 180 秒 explicitly, while using the clean risk rows only for late-window action separation on states that match the actual failing map/time bucket.

## Output Directories

- `harness/reports/2026-05-29_rl_sb3_recovery_target_override_w10_e30_001`
- `harness/reports/2026-05-29_rl_sb3_risk_recovery_override_w10_e30_001`
- `harness/reports/2026-05-29_rl_sb3_risk_recovery_source_filtered_w10_e30_001`
- `harness/reports/2026-05-29_rl_sb3_risk_recovery_source_filtered_w7_e30_001`
- `harness/reports/2026-05-29_rl_sb3_risk_recovery_source_filtered_w5_e30_001`
