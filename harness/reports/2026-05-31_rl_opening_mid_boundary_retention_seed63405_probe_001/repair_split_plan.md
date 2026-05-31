# RL Repair Split Plan

- Decision: `rl_repair_split_plan_ready`
- Repair gate: `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/repair_probe_gate.json`
- Repair gate decision: `rl_repair_probe_gate_failed`
- Lanes: `5`
- Passed lanes: `caramel10`
- Failed lanes: `retention63405, short60, parent, failure_analysis`
- Invalid lanes: `none`

## Lanes

| Label | Type | Status | Blockers | Recommendation |
|---|---|---|---:|---|
| `retention63405` | `target_seed_preflight` | `failed` | 1 | repair this target seed before rerunning full fixed-window matrices |
| `short60` | `window_target_preflight` | `failed` | 2 | treat this short-window target as an early-stop hard preflight |
| `parent` | `window_regression` | `failed` | 3 | restore parent/no-regression preservation before extending training |
| `caramel10` | `window_regression` | `passed` | 0 | keep as required evidence in the next hard gate |
| `failure_analysis` | `failure_analysis` | `failed` | 9 | split remaining failures into separate trace diagnostics before continuing |

## Blockers By Lane

### `retention63405`
- retention63405/target_seed_preflight_seed63405_retention: caramel-workshop:63405: terminal_kind is `defeat`

### `short60`
- short60/window_target_preflight_60s_caramel: 60s-caramel-short-window/caramel-workshop: win_rate 0.3333 below required 0.6667
- short60/window_target_preflight_60s_caramel: 60s-caramel-short-window/caramel-workshop: average_survival_seconds 49.2774 below required 55.0000

### `parent`
- parent/window_regression_high_pressure_vs_parent: 180s/cracked-star-jar: action_distribution_l1_delta 0.7526 beyond allowed 0.45
- parent/window_regression_high_pressure_vs_parent: 300s/caramel-workshop: action_distribution_l1_delta 0.6056 beyond allowed 0.45
- parent/window_regression_high_pressure_vs_parent: 60s/caramel-workshop: win_rate_delta -0.3334 below required 0.0

### `caramel10`
- None

### `failure_analysis`
- Remaining failures: `9`
- Repair maps: `caramel-workshop`

## Unassigned Blockers

- None

## Limitations

- This plan only groups existing repair-gate evidence; it does not rerun simulations.
- A passed lane remains repair evidence, not RL acceptance or policy-candidate approval.
- Follow-up checkpoints must rerun target preflights, fixed-window no-regression, and failure-case review.
