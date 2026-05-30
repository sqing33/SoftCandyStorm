# Per-Map Edge Branch + All-Map Late Filter High-Pressure Diagnostic

- Decision: `repair_diagnostic_passed_no_regression_but_caramel_late_gap_remains`
- Scope: evaluation-only `edge_recovery_branch` with per-map branch windows, wrapped by all-map `late_recovery_filter`
- Parent model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Branch model: `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_supervised_dataset_actions_001/seed63402_edge_recovery_supervised_dataset_actions.zip`
- Branch composition: `soda-creek:0-60s`, `caramel-workshop:30-45s`
- Late filter start: `60s`
- Map preset: `high-pressure`
- Seeds: `63400-63402`
- Reward profile: `opening-boundary-escape`

## Gate Result

`window_regression_vs_previous_chain.json` reports `policy_window_regression_passed` against the prior chained diagnostic for 60, 180, and 300 second windows. There are `0` blockers.

This is repair diagnostic evidence only. The chained policy is still a deterministic wrapper stack and must not be promoted as an RL test Bot, stage 03 checkpoint, policy candidate, or acceptance evidence.

## Window Summary

| Window | Average win rate | Key result | Gate |
|---:|---:|---|---|
| `60s` | `1.0` | All three high-pressure maps reach `1.0`; caramel improves from the previous chain by `+0.3333`. | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `1.0` | All three high-pressure maps reach `1.0`; caramel improves from the previous chain by `+0.3333`. | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `0.4444` | `soda-creek` remains `1.0`, `cracked-star-jar` remains `0.3333`, `caramel-workshop` remains `0.0`. | `multimap_comparison_recorded_needs_policy_repair` |

## 300s Map Results

| Map | Previous chain win rate | Candidate win rate | Previous chain survival | Candidate survival |
|---|---:|---:|---:|---:|
| `soda-creek` | `1.0` | `1.0` | `300.015s` | `300.015s` |
| `caramel-workshop` | `0.0` | `0.0` | `163.3014s` | `231.2871s` |
| `cracked-star-jar` | `0.3333` | `0.3333` | `289.7397s` | `289.7397s` |

## Sample Validation

- `per_map_chain_edge_samples_validation.json`: `edge_recovery_samples_valid`, `21` samples, `0` warnings.
- `per_map_chain_risk_samples_validation.json`: `risk_recovery_samples_valid`, `2184` raw risk samples, `7` target risk score warnings.
- `per_map_chain_mid_clean_risk_samples_validation.json`: `risk_recovery_samples_valid`, `1360` clean mid samples, `0` warnings.
- `per_map_chain_late_clean_risk_samples_validation.json`: `risk_recovery_samples_valid`, `784` clean late samples, `0` warnings.

The raw risk sample warnings are retained as diagnostic rows. The clean subsets remove obvious target-risk rows and remain repair-training input candidates only.

## Findings

- Per-map branch windows preserve the proven `soda-creek` opening repair while allowing the narrow `caramel-workshop` opening intervention.
- Keeping all-map late recovery preserves the previous `cracked-star-jar` 300s result and avoids the scoped-late regression.
- `caramel-workshop` average survival improves to `231.2871s`, matching the best prior caramel-opening diagnostic, but still records `0.0` 300s win rate.
- The next blocker is not branch composition plumbing; it is `caramel-workshop` late terminal conversion after the opening repair has been preserved.

## Next Actions

- Record `fail_20260530_021` for the remaining `caramel-workshop` late terminal conversion gap under per-map branch composition.
- Treat the `2184` raw risk rows and clean mid / late subsets as repair-training inputs only.
- Next repair should train or diagnose a `caramel-workshop` late conversion objective while preserving this per-map branch composition and the prior 60 / 180 / 300 second no-regression evidence.
