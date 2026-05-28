# Stage 02 Soda/Caramel Closed-loop Anchor Probe

## 结论

- Decision: `soda_caramel_closed_loop_anchor_probe_rejected_not_policy_gate`
- Start model: `harness/reports/2026-05-28_rl_curriculum_stage02_anchor_regularized_smoke_001/ppo_anchor_regularized_smoke.zip`
- Model: `ppo_soda_caramel_closed_loop_anchor_probe.zip`
- Reward profile: `late-route-recovery`
- Anchor fallback: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_fallback_probe_001/fallback.pt`
- Anchor opening: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Failure case: `harness/failed_cases/fail_20260528_088_stage02_soda_caramel_closed_loop_anchor_regression.json`
- Repair probe gate: `repair_probe_gate.md`

本 probe 不再继续 supervised sample stacking，而是从此前还能保住 `cracked-star-jar` 300 秒 `0.3333` 胜率的 anchor-regularized SB3 checkpoint 出发，只在 `soda-creek` / `caramel-workshop` 上做 `1024` timestep closed-loop `late-route-recovery` 训练。训练期间使用 current-failure fallback best 加 stage 02 opening 作为 offline KL anchor，并用 `map_time_bucket_balance` 与 `opening/mid/late = 1.5x/1.25x/1.0x` 的 time-bucket multiplier 约束漂移。

结果：该分支被拒绝。opening wrapper 保护下，60 秒仍为 `1.0/0.6667/1.0`，但 180 秒变成 `0.3333/0.6667/0.6667`，300 秒仍为 `0.0/0.0/0.0`。相对起始 anchor-regularized smoke 有 `5` 个 no-regression blockers；相对 current-failure fallback best 有 `6` 个 blockers，并丢掉 `cracked-star-jar` 300 秒 `0.3333` 胜率；相对 seed63100 stage 02 baseline 仍有 `1` 个 blocker。

## Training

| Item | Value |
| --- | --- |
| Timesteps | `1024` |
| Train maps | `soda-creek`, `caramel-workshop` |
| Train seeds | `63100-63102` |
| Train seconds | `300` |
| Reward profile | `late-route-recovery` |
| Learning rate | `0.00002` |
| Entropy coefficient | `0.02` |
| Anchor samples | `36426` |
| Anchor sample weighting | `map_time_bucket_balance` |
| Anchor bucket multipliers | opening `1.5x`, mid `1.25x`, late `1.0x` |
| Anchor final mean KL | `0.340916` |
| Anchor final argmax agreement | `0.6914` |

## Anchor Alignment

| Metric | Value | Threshold |
| --- | ---: | ---: |
| Overall mean KL | `0.34314` | `<= 0.25` |
| Overall argmax agreement | `0.6966` | `>= 0.75` |
| `soda-creek` mean KL | `0.369067` | `<= 0.35` |
| `mid_60_to_180` mean KL | `0.431042` | `<= 0.35` |

Full alignment decision: `behavior_clone_anchor_alignment_failed`.

## Repair Probe Gate

`validate_rl_repair_probe_gate.py` 汇总本次训练报告、anchor alignment、三组 window regression 和 300 秒 failure analysis 后，给出 `rl_repair_probe_gate_failed`。该 gate 记录 `16` 个 blockers 和 `1` 个 warning，确认此分支不适合继续加长训练。

## Deterministic High-pressure Results

| Window | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `1.0` | `0.6667` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.3333` | `0.6667` | `0.6667` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

## Window Regression

| Baseline | Decision | Blockers | Main regression |
| --- | --- | ---: | --- |
| anchor-regularized smoke | `policy_window_regression_failed` | `5` | `soda-creek` 180 秒与 300 秒回退，并丢掉 `cracked-star-jar` 300 秒胜率 |
| current-failure fallback best | `policy_window_regression_failed` | `6` | 多图 180 / 300 秒 survival 回退，并丢掉 `cracked-star-jar` 300 秒胜率 |
| seed63100 stage 02 baseline | `policy_window_regression_failed` | `1` | `cracked-star-jar` 300 秒 survival 回退 |

## Failure Analysis

| Map | 300s failures | Failure buckets | Dominant action |
| --- | ---: | --- | --- |
| `soda-creek` | `3` | mid `2`, late `1` | action `7` / `38.53%` |
| `caramel-workshop` | `3` | opening `1`, late `2` | action `7` / `32.55%` |
| `cracked-star-jar` | `3` | mid `1`, late `2` | action `7` / `44.02%` |

## 判断

- Closed-loop training with the existing anchor regularization path is functional, but this configuration still drifts too far from the current-failure best anchor.
- The main new blocker is mid-window drift: `mid_60_to_180` mean KL is `0.431042`, and `soda-creek` 180 秒 win rate drops relative to the start model.
- Do not continue by simply increasing PPO timesteps. The next repair needs a stricter mid-window anchor / handoff objective or an online hard no-regression guard before any longer closed-loop run.

## 输出文件

- `ppo_training_report.json`
- `ppo_evaluation_report.json`
- `ppo_known_exploits.json`
- `ppo_soda_caramel_closed_loop_anchor_probe.zip`
- `ppo_soda_caramel_closed_loop_anchor_probe_metadata.json`
- `anchor_alignment.json`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `window_regression_vs_anchor_regularized_smoke.json`
- `window_regression_vs_anchor_regularized_smoke.md`
- `window_regression_vs_current_failure_best.json`
- `window_regression_vs_current_failure_best.md`
- `window_regression_vs_seed63100_stage02.json`
- `window_regression_vs_seed63100_stage02.md`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
- `repair_probe_gate.json`
- `repair_probe_gate.md`
