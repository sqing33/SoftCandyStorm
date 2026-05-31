# Caramel Rule Victory Terminal Branch Diagnostic

- Decision: `rl_repair_probe_gate_failed`
- Scope: `caramel-workshop` terminal_conversion_branch trained from same-map rule-bot neighbor victories, nested inside per-map edge branch and all-map late_recovery_filter
- Parent model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Terminal model: `harness/reports/2026-05-31_rl_caramel_rule_victory_terminal_branch_001/ppo_caramel_rule_victory_terminal_branch.zip`
- Terminal override: `caramel-workshop:210-300s`, `min_pressure = 0.2`, `min_low_health_risk = 0.25`
- Edge branch composition: `soda-creek:0-60s`, `caramel-workshop:30-45s`
- Late filter start: all maps from `60s`
- Map preset: `high-pressure`
- Seeds: `63400-63402`

## Training Input

The SB3 terminal branch was distilled from:

- `8630` same-map `caramel-workshop` rule-bot victory movement samples in the `210-300s` window.
- `164` clean `180-300s` risk recovery rows from the current per-map chain failure states, used as low-weight safety repair input with sample weight `0.25`.

`distillation_report.json` records `dataset_action_target_override.overridden_sample_count = 8630` and `recovery_target_override.overridden_sample_count = 164`. The offline action-distribution guard passed: validation dominant action ratio was `0.1887` and normalized argmax entropy was `0.9189`.

## Window Result

| Window | `soda-creek` | `caramel-workshop` | `cracked-star-jar` | Gate |
|---:|---:|---:|---:|---|
| `60s` | `1.0` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `1.0` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `1.0` | `0.0` | `0.3333` | `multimap_comparison_recorded_needs_policy_repair` |

At `300s`, `caramel-workshop` average survival was `231.0093s`, compared with `231.2871s` for the current per-map chain baseline.

## No-Regression

`window_regression_vs_per_map_chain.json` reports `policy_window_regression_failed` with `1` blocker:

- `300s/caramel-workshop`: average survival dropped `0.2778s` beyond the allowed `0.0s`.

The branch was dispatched on `caramel-workshop`, so the failure is not a missing routing problem. In the `300s` comparison, the nested terminal branch recorded `839` terminal decisions on `caramel-workshop`, terminal ratio `0.0404`, and `0` terminal decisions on the other high-pressure maps.

## Failure Analysis

`failure_analysis_300s.json` records `5` failed policy episodes:

- `soda-creek`: `0` failures, win rate `1.0`.
- `caramel-workshop`: `3` failures, all in `late_180_to_300`, average failure survival `231.0093s`.
- `cracked-star-jar`: `2` failures, both in `late_180_to_300`, average failure survival `284.6021s`.

The repair-probe gate failed because the required per-map-chain no-regression report failed. This checkpoint must not be promoted as a policy candidate, stage 03 model, RL test Bot, RL acceptance evidence, balance gate, or release evidence.

## Next Actions

- Keep `harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/summary.md` as the current diagnostic baseline.
- Treat the new terminal branch as rejected repair evidence, despite the better offline same-map sample coverage.
- The next repair should collect closer successful `caramel-workshop` terminal trajectories or use a more constrained online / sequence objective, then rerun the same `60/180/300s` high-pressure no-regression gate.
