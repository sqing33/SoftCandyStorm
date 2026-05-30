# Stage 01 Opening Boundary Escape Probe

- Decision: `repair_failed`
- Profile: `opening-boundary-escape`
- Start model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`

## Results

| Variant | Parent No-Regression | Blockers | 60s `soda-creek` | 300s Result |
|---|---|---:|---:|---|
| `lr=5e-7` | `policy_window_regression_passed` | `0` | `0.6667` | `0.0/0.0/0.0` |
| `lr=1e-6` | `policy_window_regression_failed` | `1` | `0.6667` | `0.0/0.0/0.3333` |

The `5e-7` run is parent-preserving but too weak to improve the target `soda-creek` 60s opening blocker. The `1e-6` run restores `cracked-star-jar` 300s to `0.3333`, but fails strict parent no-regression on `300s/caramel-workshop` average survival by `0.1444s`.

The training reward breakdown confirms the new signal is active: `opening_boundary_escape` averaged `-0.4239` in the `5e-7` run and `-0.3658` in the `1e-6` run. That means the profile records pressure-gated edge escape feedback, but the current PPO update still does not convert seed `63402` into the successful action `7` / `3` escape pattern.

## Gate

This checkpoint must not enter stage 02. The next stage 01 repair should stop relying on scalar reward alone and add a target-specific supervision or guard for the seed `63402` high-pressure edge-lock frames.
