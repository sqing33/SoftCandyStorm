# RL Repair Split Plan

- Decision: `rl_repair_split_plan_ready`
- Repair gate: `harness/reports/2026-05-31_rl_mid_path_retention_seed63407_closed_loop_probe_001/repair_probe_gate_hard_preflight.json`
- Repair gate decision: `rl_repair_probe_gate_failed`
- Lanes: `5`
- Passed lanes: `target63407`
- Failed lanes: `opening63402, retention63405, short60, parent`
- Invalid lanes: `none`

## Lanes

| Label | Type | Status | Blockers | Recommendation |
|---|---|---|---:|---|
| `target63407` | `target_seed_preflight` | `passed` | 0 | keep as required evidence in the next hard gate |
| `opening63402` | `target_seed_preflight` | `failed` | 2 | repair this target seed before rerunning full fixed-window matrices |
| `retention63405` | `target_seed_preflight` | `failed` | 2 | repair this target seed before rerunning full fixed-window matrices |
| `short60` | `window_target_preflight` | `failed` | 2 | treat this short-window target as an early-stop hard preflight |
| `parent` | `window_regression` | `failed` | 3 | restore parent/no-regression preservation before extending training |

## Blockers By Lane

### `target63407`
- None

### `opening63402`
- opening63402/target_seed_preflight_seed63402_opening: caramel-workshop:63402: time_seconds 40.0997 below required 60.0000
- opening63402/target_seed_preflight_seed63402_opening: caramel-workshop:63402: terminal_kind is `defeat`

### `retention63405`
- retention63405/target_seed_preflight_seed63405_retention: caramel-workshop:63405: time_seconds 138.6673 below required 180.0000
- retention63405/target_seed_preflight_seed63405_retention: caramel-workshop:63405: terminal_kind is `defeat`

### `short60`
- short60/window_target_preflight_60s_caramel: 60s-caramel-short-window/caramel-workshop: win_rate 0.3333 below required 0.6667
- short60/window_target_preflight_60s_caramel: 60s-caramel-short-window/caramel-workshop: average_survival_seconds 49.2774 below required 55.0000

### `parent`
- parent/window_regression_high_pressure_vs_parent: 180s/cracked-star-jar: action_distribution_l1_delta 0.4646 beyond allowed 0.45
- parent/window_regression_high_pressure_vs_parent: 300s/caramel-workshop: action_distribution_l1_delta 0.5872 beyond allowed 0.45
- parent/window_regression_high_pressure_vs_parent: 60s/caramel-workshop: win_rate_delta -0.3334 below required 0.0

## Unassigned Blockers

- None

## Limitations

- This plan only groups existing repair-gate evidence; it does not rerun simulations.
- A passed lane remains repair evidence, not RL acceptance or policy-candidate approval.
- Follow-up checkpoints must rerun target preflights, fixed-window no-regression, and failure-case review.
