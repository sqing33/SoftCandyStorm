# Caramel Terminal Branch Per-Map Chain Diagnostic

- Decision: `rl_repair_probe_gate_failed`
- Scope: evaluation-only `terminal_conversion_branch` for `caramel-workshop`, nested inside per-map `edge_recovery_branch` and all-map `late_recovery_filter`
- Parent model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Terminal model: `harness/reports/2026-05-29_rl_sb3_terminal_victory_multimap_path_target_w1_e30_001/ppo_terminal_victory_multimap_path_target_w1_e30.zip`
- Terminal override: `caramel-workshop:210-300s`, `min_pressure = 0.2`, `min_low_health_risk = 0.25`
- Edge branch composition: `soda-creek:0-60s`, `caramel-workshop:30-45s`
- Late filter start: all maps from `60s`
- Map preset: `high-pressure`
- Seeds: `63400-63402`
- Reward profile: `opening-boundary-escape`

## Result

The terminal branch was actually dispatched on `caramel-workshop`, but it did not convert the map to a 300 second victory. At `300s`, `caramel-workshop` remained at `0.0` win rate and average survival dropped from the previous per-map chain baseline `231.2871s` to `228.9533s`.

| Window | `soda-creek` | `caramel-workshop` | `cracked-star-jar` | Gate |
|---:|---:|---:|---:|---|
| `60s` | `1.0` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `1.0` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `1.0` | `0.0` | `0.3333` | `multimap_comparison_recorded_needs_policy_repair` |

## Branch Usage

Nested adapter provenance is now present in the comparison reports. In the `300s` comparison, the terminal branch recorded:

- `caramel-workshop`: `796 / 20604` terminal decisions, terminal ratio `0.0386`.
- `caramel-workshop` late bucket: `796 / 4404` terminal decisions, terminal ratio `0.1807`.
- `soda-creek` and `cracked-star-jar`: `0` terminal decisions, confirming the map-specific scope.

The edge branch still only dispatched `1` time on `caramel-workshop` in the opening bucket, preserving the narrow opening repair behavior.

## No-Regression

`window_regression_vs_per_map_chain.json` reports `policy_window_regression_failed` with `1` blocker:

- `300s/caramel-workshop`: average survival dropped `2.3338s` beyond the allowed `0.0s`.

This means the existing multimap victory terminal branch is not only failing to convert `caramel-workshop`, it slightly regresses the current best per-map chain diagnostic.

## Conclusion

This run rules out "terminal branch was not called" as the remaining explanation. The branch was called in the intended late-pressure `caramel-workshop` states, but the current terminal model did not provide a usable conversion sequence. The next repair should not keep tuning this same terminal dispatch window or thresholds; it should collect or train a `caramel-workshop`-specific late conversion target closer to the actual failure states, then re-run the same 60 / 180 / 300 second no-regression gate against the per-map chain baseline.

This report is diagnostic evidence only. It must not be promoted as a policy candidate, stage 03 checkpoint, RL test Bot, or RL acceptance evidence.
