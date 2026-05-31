# Caramel Selective Ranked Victory Terminal Branch W0.5 Diagnostic

- Decision: `rl_repair_probe_gate_failed`
- Scope: `caramel-workshop` terminal conversion branch distilled from the six ranked high-match victory episodes, nested inside the current per-map edge branch plus all-map late recovery filter
- Parent model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Terminal model: `harness/reports/2026-05-31_rl_caramel_selective_ranked_victory_terminal_branch_w05_001/ppo_caramel_selective_ranked_victory_terminal_branch_w05.zip`
- Selective dataset: `harness/reports/2026-05-31_rule_bot_caramel_wide_terminal_seed_scan_001/caramel_selective_ranked_victory_210_300_samples.jsonl`
- Terminal override: `caramel-workshop:210-300s`, `min_pressure = 0.2`, `min_low_health_risk = 0.25`
- Edge branch composition: `soda-creek:0-60s`, `caramel-workshop:30-45s`
- Late filter start: all maps from `60s`
- Map preset: `high-pressure`
- Seeds: `63400-63402`

## Training Input

The SB3 terminal branch was distilled from:

- `3237` selective ranked `caramel-workshop` rule-bot victory movement samples in the `210-300s` window, weighted at `0.5x`.
- `164` clean `180-300s` risk recovery rows from the current per-map chain failure states, used as low-weight safety repair input at `0.25x`.

`distillation_report.json` records `dataset_action_target_override.overridden_sample_count = 3237` and `recovery_target_override.overridden_sample_count = 164`. The offline action-distribution guard passed: validation dominant action ratio was `0.1647` and normalized argmax entropy was `0.9372`. The selective trajectory validation slice also passed with dominant action `3` at ratio `0.1732` and normalized entropy `0.9338`.

## Window Result

| Window | `soda-creek` | `caramel-workshop` | `cracked-star-jar` | Gate |
|---:|---:|---:|---:|---|
| `60s` | `1.0` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `180s` | `1.0` | `1.0` | `1.0` | `multimap_comparison_recorded_not_balance_gate` |
| `300s` | `1.0` | `0.0` | `0.3333` | `multimap_comparison_recorded_needs_policy_repair` |

At `300s`, `caramel-workshop` average survival was `230.8648s`, compared with `231.2871s` for the current per-map chain baseline. The terminal branch was dispatched on `caramel-workshop`: `832 / 20776` total decisions and `832 / 4576` late-window decisions.

`policy_adapter_scope_terminal_300s.json` now validates the nested terminal branch scope as `policy_adapter_scope_passed`: `832 / 73851` effective decisions used the terminal branch, all within `caramel-workshop` and `late_180_to_300`. `terminal_conversion_probe_gate.json` requires that scope report, but still fails on conversion and no-regression blockers.

## No-Regression

`window_regression_vs_per_map_chain.json` reports `policy_window_regression_failed` with `1` blocker:

- `300s/caramel-workshop`: average survival dropped `0.4223s` beyond the allowed `0.0s`.

Compared with the prior full neighbor terminal branch, the selective branch kept the same `300s` win-rate shape but had a larger caramel survival drop (`0.4223s` vs `0.2778s`). The lower sample count and stronger nearest action agreement did not translate into online conversion.

## Failure Analysis

`failure_analysis_300s.json` records `5` failed policy episodes:

- `soda-creek`: `0` failures, win rate `1.0`.
- `caramel-workshop`: `3` failures, all in `late_180_to_300`, average failure survival `230.8648s`.
- `cracked-star-jar`: `2` failures, both in `late_180_to_300`, average failure survival `284.6021s`.

The repair-probe gate failed because the required per-map-chain no-regression report failed. This checkpoint must not be promoted as a policy candidate, stage 03 model, RL test Bot, RL acceptance evidence, balance gate, or release evidence.

## Next Actions

- Keep `harness/reports/2026-05-30_rl_per_map_edge_branch_late_all_high_pressure_001/summary.md` as the current diagnostic baseline.
- Treat the selective ranked terminal branch as rejected repair evidence, despite its better offline action-target agreement.
- Stop testing simple supervised terminal-path imitation variants from rule-bot victories until the next objective changes the online sequence problem, for example by collecting direct successful traces on target seeds, adding a constrained online objective, or adding sequence-level terminal conversion validation before branch evaluation.
