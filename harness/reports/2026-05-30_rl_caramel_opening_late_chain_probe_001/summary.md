# Caramel Opening + Late Chain Probe

- Decision: `repair_diagnostic_rejected_by_300s_soda_regression`
- Scope: evaluation-only `edge_recovery_branch` for `soda-creek,caramel-workshop` wrapped by `late_recovery_filter`
- Parent model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Branch model: `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_supervised_dataset_actions_001/seed63402_edge_recovery_supervised_dataset_actions.zip`
- Branch window: `25-45s`
- Late filter start: `60s`
- Map preset: `high-pressure`
- Seeds: `63400-63402`

## Gate Result

The unified chain passed 60s and 180s regression checks against the prior `edge_recovery_branch + late_recovery_filter` chain, but failed the 300s regression check.

- `unified_window_regression_vs_previous_chain_60s.json`: `policy_window_regression_passed`, `0` blockers.
- `unified_window_regression_vs_previous_chain_180s.json`: `policy_window_regression_passed`, `0` blockers.
- `unified_window_regression_vs_previous_chain_300s.json`: `policy_window_regression_failed`, `2` blockers.

The 300s blockers are both on `soda-creek`: win rate dropped from `1.0` to `0.6667`, and average survival dropped by `4.5878s`. This means the chain is useful diagnostic evidence and sample source only. It must not be promoted as an RL test Bot, stage 03 checkpoint, policy candidate, or acceptance evidence.

## Window Summary

| Window | Average win rate | Key result | Gate |
|---:|---:|---|---|
| `60s` | `1.0` | Three high-pressure maps all reach `1.0` win rate. | `policy_window_regression_passed` |
| `180s` | `1.0` | Three high-pressure maps all reach `1.0` win rate. | `policy_window_regression_passed` |
| `300s` | `0.3333` | `caramel-workshop` remains `0.0`; `soda-creek` regresses versus the previous chain. | `policy_window_regression_failed` |

## 300s Map Results

| Map | Previous chain win rate | Unified chain win rate | Previous chain survival | Unified chain survival |
|---|---:|---:|---:|---:|
| `soda-creek` | `1.0` | `0.6667` | `300.015s` | `295.4272s` |
| `caramel-workshop` | `0.0` | `0.0` | `163.3014s` | `231.2871s` |
| `cracked-star-jar` | `0.3333` | `0.3333` | `289.7397s` | `289.7397s` |

## 300s Episodes

| Map | Seed | Result | Time |
|---|---:|---|---:|
| `soda-creek` | `63400` | `victory` | `300.015s` |
| `soda-creek` | `63401` | `defeat` | `286.2517s` |
| `soda-creek` | `63402` | `victory` | `300.015s` |
| `caramel-workshop` | `63400` | `defeat` | `213.2166s` |
| `caramel-workshop` | `63401` | `defeat` | `235.3546s` |
| `caramel-workshop` | `63402` | `defeat` | `245.2901s` |
| `cracked-star-jar` | `63400` | `defeat` | `293.5499s` |
| `cracked-star-jar` | `63401` | `victory` | `300.015s` |
| `cracked-star-jar` | `63402` | `defeat` | `275.6543s` |

## Sample Validation

- `unified_chain_edge_samples_validation.json`: `edge_recovery_samples_valid`, `8` samples, `0` warnings.
- `unified_chain_risk_samples_validation.json`: `risk_recovery_samples_valid`, `2165` samples, `8` target risk score warnings.
- `unified_chain_mid_clean_risk_samples_validation.json`: `risk_recovery_samples_valid`, `1402` clean samples, `0` warnings.
- `unified_chain_late_clean_risk_samples_validation.json`: `risk_recovery_samples_valid`, `727` clean samples, `0` warnings.

The warning rows in the raw risk sample file are retained for auditability, but follow-up training should prefer the clean mid / late subsets.

## Findings

- Adding `caramel-workshop` to the branch scope and chaining the late filter improves `caramel-workshop` 300s average survival from `163.3014s` to `231.2871s`, but it still produces no 300s wins.
- The same unified chain regresses `soda-creek` 300s from `1.0` to `0.6667`, so the repair direction is not safe as a shared high-pressure wrapper.
- The branch remains sparse in the high-pressure 300s run: `2 / 26587` decisions, all in `opening_lt_60`, and none in `mid_60_to_180` or `late_180_to_300`.
- The clean risk subsets provide useful repair-input material, but the result shows that sample extraction alone is not enough to satisfy long-window no-regression.

## Next Actions

- Record `fail_20260530_018` for the unified chain's 300s `soda-creek` regression and remaining `caramel-workshop` conversion gap.
- Do not stack the caramel opening branch into the previous soda-winning chain without a 300s no-regression guard.
- Use the clean mid / late risk samples only as repair-training input candidates, not as acceptance evidence.
- Next repair should be per-map or state-conditioned enough to preserve `soda-creek` 300s while separately targeting `caramel-workshop` late conversion.
