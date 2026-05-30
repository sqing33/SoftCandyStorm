# RL Stage 01 Opening Fixed-window Probe

- Decision: `stage01_opening_probe_failed`
- Initial model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Candidate: `harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/stages/stage_01_opening_lt_60/stage_01_opening_lt_60.zip`
- Training: `256` timesteps, `soda-creek`, `60s`, reward profile `late-route-recovery`
- Failure case: `harness/failed_cases/fail_20260530_001_stage01_opening_fixed_window_probe.json`

## Fixed-window Results

| Window | Gate | soda-creek | caramel-workshop | cracked-star-jar |
|---|---|---:|---:|---:|
| `60s` | `multimap_comparison_recorded_not_balance_gate` | 0.6667 | 1.0 | 1.0 |
| `180s` | `multimap_comparison_recorded_watch` | 0.6667 | 0.3333 | 1.0 |
| `300s` | `multimap_comparison_recorded_needs_policy_repair` | 0.0 | 0.0 | 0.0 |

## Parent No-regression

- Decision: `policy_window_regression_failed`
- Blocker: `300s/cracked-star-jar: dominant_action_ratio increased 0.2034 beyond allowed 0.2`

## Findings

- The short opening continuation did not clear the `soda-creek` opening failure: seed `63402` still died around `37.13s`.
- The candidate still has no 300 second high-pressure wins on any map.
- Same-seed survival mostly improved or stayed within tolerance, but the cracked-star-jar 300s action concentration blocker prevents continuing this branch.

## Next Actions

- Do not run stage 02 from this checkpoint.
- Redesign stage 01 with explicit opening retention targets and an online action-distribution guard.
- Re-run 60/180/300s same-seed parent no-regression before any handoff or late-window continuation.
