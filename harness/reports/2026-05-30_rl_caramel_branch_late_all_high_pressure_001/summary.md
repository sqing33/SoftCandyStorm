# Caramel Branch + All-Map Late Filter High-Pressure Diagnostic

- Decision: `repair_diagnostic_rejected_by_soda_opening_regression`
- Scope: evaluation-only `edge_recovery_branch` for `caramel-workshop` wrapped by all-map `late_recovery_filter`
- Parent model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Branch model: `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_supervised_dataset_actions_001/seed63402_edge_recovery_supervised_dataset_actions.zip`
- Branch window: `25-45s`
- Late filter start: `60s`
- Map preset: `high-pressure`
- Seeds: `63400-63402`

## Gate Result

The all-map late filter restores the prior `cracked-star-jar` 300s behavior, but removing the `soda-creek` opening branch causes `soda-creek` to regress in all fixed windows.

- `window_regression_vs_previous_chain_60s.json`: `policy_window_regression_failed`, `2` blockers.
- `window_regression_vs_previous_chain_180s.json`: `policy_window_regression_failed`, `2` blockers.
- `window_regression_vs_previous_chain_300s.json`: `policy_window_regression_failed`, `2` blockers.

All blockers are on `soda-creek`. At 300s, win rate drops from `1.0` to `0.3333` and average survival drops by `92.0373s`. This means the previous soda-winning chain depends on both the `soda-creek` opening branch and all-map late recovery. This diagnostic must not be promoted as an RL test Bot, stage 03 checkpoint, policy candidate, or acceptance evidence.

## Window Summary

| Window | Average win rate | Key result | Gate |
|---:|---:|---|---|
| `60s` | `0.8889` | `soda-creek` drops from `1.0` to `0.6667`. | `policy_window_regression_failed` |
| `180s` | `0.8889` | `soda-creek` drops from `1.0` to `0.6667`. | `policy_window_regression_failed` |
| `300s` | `0.2222` | `soda-creek` drops from `1.0` to `0.3333`; `cracked-star-jar` remains `0.3333`; `caramel-workshop` remains `0.0`. | `policy_window_regression_failed` |

## 300s Map Results

| Map | Previous chain win rate | Candidate win rate | Previous chain survival | Candidate survival |
|---|---:|---:|---:|---:|
| `soda-creek` | `1.0` | `0.3333` | `300.015s` | `207.9777s` |
| `caramel-workshop` | `0.0` | `0.0` | `163.3014s` | `231.2871s` |
| `cracked-star-jar` | `0.3333` | `0.3333` | `289.7397s` | `289.7397s` |

## 300s Episodes

| Map | Seed | Result | Time |
|---|---:|---|---:|
| `soda-creek` | `63400` | `victory` | `300.015s` |
| `soda-creek` | `63401` | `defeat` | `286.2517s` |
| `soda-creek` | `63402` | `defeat` | `37.6664s` |
| `caramel-workshop` | `63400` | `defeat` | `213.2166s` |
| `caramel-workshop` | `63401` | `defeat` | `235.3546s` |
| `caramel-workshop` | `63402` | `defeat` | `245.2901s` |
| `cracked-star-jar` | `63400` | `defeat` | `293.5499s` |
| `cracked-star-jar` | `63401` | `victory` | `300.015s` |
| `cracked-star-jar` | `63402` | `defeat` | `275.6543s` |

## Sample Validation

- `caramel_branch_late_all_edge_samples_validation.json`: `edge_recovery_samples_valid`, `3` samples, `0` warnings.
- `caramel_branch_late_all_risk_samples_validation.json`: `risk_recovery_samples_valid`, `1806` samples, `6` target risk score warnings.
- `caramel_branch_late_all_mid_clean_risk_samples_validation.json`: `risk_recovery_samples_valid`, `1139` clean samples, `0` warnings.
- `caramel_branch_late_all_late_clean_risk_samples_validation.json`: `risk_recovery_samples_valid`, `634` clean samples, `0` warnings.

The `3` edge samples are on `caramel-workshop`; the risk samples cover `soda-creek`, `caramel-workshop`, and `cracked-star-jar`. Clean subsets remain repair-training input candidates only.

## Findings

- Keeping all-map late recovery is enough to preserve the prior `cracked-star-jar` 300s result, so the prior scoped failure on `cracked-star-jar` was caused by removing late recovery from that map.
- Removing `soda-creek` from the opening branch reintroduces the known target-seed opening death: `soda-creek:63402` fails at `37.6664s`.
- `caramel-workshop` still reaches `231.2871s` average survival but records `0.0` 300s win rate, so the caramel branch plus generic late filter still lacks terminal conversion.
- The current CLI can express one shared edge-branch window, but the evidence now points to needing map-conditioned branch composition: preserve the prior `soda-creek` opening branch, preserve all-map late safety where it helps, and add a separate caramel conversion objective.

## Next Actions

- Record `fail_20260530_020` for the soda opening regression caused by caramel-only edge branch scope.
- Do not use a single shared `--edge-recovery-branch-maps` scope to trade off soda opening repair against caramel opening repair.
- Next implementation should support explicit per-map branch composition or a small policy-composition manifest so `soda-creek` can keep its proven opening branch while `caramel-workshop` receives a separate opening / late conversion branch.
