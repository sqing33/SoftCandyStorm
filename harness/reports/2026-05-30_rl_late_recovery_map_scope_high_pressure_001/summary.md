# Late Recovery Map Scope High-Pressure Diagnostic

- Decision: `repair_diagnostic_rejected_by_300s_soda_cracked_regression`
- Scope: evaluation-only `edge_recovery_branch` for `soda-creek,caramel-workshop` wrapped by `late_recovery_filter`
- Late filter target maps: `caramel-workshop`
- Parent model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Branch model: `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_supervised_dataset_actions_001/seed63402_edge_recovery_supervised_dataset_actions.zip`
- Branch window: `25-45s`
- Late filter start: `60s`
- Map preset: `high-pressure`
- Seeds: `63400-63402`

## Gate Result

The scoped chain preserved the 60s and 180s high-pressure windows, but failed the 300s regression check against the prior `edge_recovery_branch + late_recovery_filter` chain.

- `scoped_window_regression_vs_previous_chain_60s.json`: `policy_window_regression_passed`, `0` blockers.
- `scoped_window_regression_vs_previous_chain_180s.json`: `policy_window_regression_passed`, `0` blockers.
- `scoped_window_regression_vs_previous_chain_300s.json`: `policy_window_regression_failed`, `4` blockers.

The 300s blockers show that removing late recovery from non-target maps is unsafe: `soda-creek` drops from `1.0` to `0.0` win rate and loses `95.8781s` average survival, while `cracked-star-jar` drops from `0.3333` to `0.0` win rate and loses `68.7881s` average survival. This result is diagnostic evidence and sample material only. It must not be promoted as an RL test Bot, stage 03 checkpoint, policy candidate, or acceptance evidence.

## Window Summary

| Window | Average win rate | Key result | Gate |
|---:|---:|---|---|
| `60s` | `1.0` | Three high-pressure maps all reach `1.0` win rate. | `policy_window_regression_passed` |
| `180s` | `1.0` | Three high-pressure maps all reach `1.0` win rate. | `policy_window_regression_passed` |
| `300s` | `0.0` | `soda-creek` and `cracked-star-jar` both regress because late recovery no longer applies to them. | `policy_window_regression_failed` |

## 300s Map Results

| Map | Previous chain win rate | Scoped chain win rate | Previous chain survival | Scoped chain survival |
|---|---:|---:|---:|---:|
| `soda-creek` | `1.0` | `0.0` | `300.015s` | `204.1369s` |
| `caramel-workshop` | `0.0` | `0.0` | `163.3014s` | `231.2871s` |
| `cracked-star-jar` | `0.3333` | `0.0` | `289.7397s` | `220.9516s` |

## 300s Episodes

| Map | Seed | Result | Time |
|---|---:|---|---:|
| `soda-creek` | `63400` | `defeat` | `212.183s` |
| `soda-creek` | `63401` | `defeat` | `180.743s` |
| `soda-creek` | `63402` | `defeat` | `219.4846s` |
| `caramel-workshop` | `63400` | `defeat` | `213.2166s` |
| `caramel-workshop` | `63401` | `defeat` | `235.3546s` |
| `caramel-workshop` | `63402` | `defeat` | `245.2901s` |
| `cracked-star-jar` | `63400` | `defeat` | `232.0206s` |
| `cracked-star-jar` | `63401` | `defeat` | `220.2848s` |
| `cracked-star-jar` | `63402` | `defeat` | `210.5494s` |

## Sample Validation

- `scoped_chain_edge_samples_validation.json`: `edge_recovery_samples_valid`, `8` samples, `0` warnings.
- `scoped_chain_risk_samples_validation.json`: `risk_recovery_samples_valid`, `610` samples, `5` target risk score warnings.
- `scoped_chain_mid_clean_risk_samples_validation.json`: `risk_recovery_samples_valid`, `440` clean samples, `0` warnings.
- `scoped_chain_late_clean_risk_samples_validation.json`: `risk_recovery_samples_valid`, `164` clean samples, `0` warnings.

The raw warning rows are retained for auditability. Follow-up training should prefer the clean mid / late subsets, and should treat them as repair-training input candidates only.

## Findings

- `--late-recovery-maps caramel-workshop` correctly records `target_maps: ["caramel-workshop"]` in `policy_adapter_report`, but the scoped diagnostic removes an important long-window safety adapter from `soda-creek` and `cracked-star-jar`.
- The previous `soda-creek` 300s success was not independent of late recovery; scoping late recovery away from `soda-creek` converts all three seeds from victory to defeat.
- `caramel-workshop` keeps the same `231.2871s` average survival seen in the unified chain, but still records `0.0` 300s win rate, so the scoped map change does not solve terminal conversion.
- The next repair should not be "caramel-only late filter" as a shared chain. It needs map-conditioned or state-conditioned late conversion that preserves the proven `soda-creek` and `cracked-star-jar` late safety behavior while separately addressing `caramel-workshop`.

## Next Actions

- Record `fail_20260530_019` for the 300s `soda-creek` and `cracked-star-jar` regression caused by over-scoping late recovery.
- Keep `--late-recovery-maps` as a diagnostic control, but do not use `caramel-workshop`-only late filtering as a candidate chain.
- Next probe should compare at least two map-conditioned designs: preserving late recovery on `soda-creek,cracked-star-jar` while applying a separate caramel conversion objective, or adding a stronger state-conditioned late branch that is gated by map and pressure without removing prior safety repairs.
