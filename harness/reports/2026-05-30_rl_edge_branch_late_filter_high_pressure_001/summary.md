# Edge Branch + Late Filter High-Pressure Diagnostic

- Decision: `repair_diagnostic_passed_but_caramel_300s_gap_remains`
- Scope: evaluation-only `edge_recovery_branch` wrapped by `late_recovery_filter`
- Parent model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Branch model: `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_supervised_dataset_actions_001/seed63402_edge_recovery_supervised_dataset_actions.zip`
- Map preset: `high-pressure`
- Seeds: `63400-63402`
- Reward profile: `opening-boundary-escape`

## Gate Result

`window_regression_vs_edge_branch.json` reports `policy_window_regression_passed` against the prior `edge_recovery_branch` high-pressure baseline for 60, 180, and 300 second windows. There are `0` blockers.

This is repair diagnostic evidence only. The chained policy is a deterministic wrapper stack and must not be promoted as an RL test Bot, stage 03 checkpoint, policy candidate, or acceptance evidence.

## Window Summary

| Window | Average win rate | Key result | Gate |
|---:|---:|---|---|
| `60s` | `0.8889` | Matches edge-branch baseline; `soda-creek` remains `1.0` win rate. | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `0.8889` | `caramel-workshop` improves from `0.3333` to `0.6667` versus edge-branch baseline. | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.4444` | `soda-creek` improves from `0.0` to `1.0`; `cracked-star-jar` improves from `0.0` to `0.3333`; `caramel-workshop` remains `0.0`. | `multimap_comparison_recorded_needs_policy_repair` |

## 300s Map Results

| Map | Edge branch win rate | Chained win rate | Edge branch survival | Chained survival |
|---|---:|---:|---:|---:|
| `soda-creek` | `0.0` | `1.0` | `221.8073s` | `300.015s` |
| `caramel-workshop` | `0.0` | `0.0` | `120.1944s` | `163.3014s` |
| `cracked-star-jar` | `0.0` | `0.3333` | `220.9516s` | `289.7397s` |

## Sample Validation

- `chain_samples_60s_soda-creek_validation.json`: `edge_recovery_samples_valid`, `4` samples, `0` warnings.
- `chain_samples_180s_soda-creek_edge_only_validation.json`: `edge_recovery_samples_valid`, `7` samples, `0` warnings.
- `chain_samples_300s_soda-creek_edge_only_validation.json`: `edge_recovery_samples_valid`, `7` samples, `0` warnings.
- `chain_risk_samples_validation.json`: `risk_recovery_samples_valid`, `2000` samples, `6` target risk score warnings.

The risk sample warning rows are kept in the report because they are useful repair diagnostics. They do not invalidate the sample file, but they are a reminder that late filter targets are not guaranteed to monotonically reduce the validator's heuristic risk score.

## Findings

- The opening branch remains narrow: in the 300 second `soda-creek` run it dispatches `7 / 27000` decisions, all in `opening_lt_60`.
- The late filter creates a large repair-input set after 60 seconds: `2000` valid `risk_recovery_supervision_sample` rows across the 180 and 300 second reports.
- The combined wrapper strongly repairs `soda-creek` and partly repairs `cracked-star-jar` at 300 seconds, but `caramel-workshop` still has no 300 second wins.
- Because `caramel-workshop` remains at `0.0` win rate and the result depends on deterministic diagnostic adapters, the RL acceptance blocker remains active.

## Next Actions

- Record `fail_20260530_015` for the remaining `caramel-workshop` 300 second conversion gap.
- Treat the risk samples as repair-training input candidates only; do not mix them into acceptance, release, or policy-candidate manifests.
- Next repair should target `caramel-workshop` late conversion while preserving the chained 60 / 180 / 300 second no-regression evidence.
