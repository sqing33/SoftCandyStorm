# Stage 01 Opening Route Recovery Probe

- Decision: `repair_failed`
- Reward profile: `opening-route-recovery`
- Start model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Output model: `harness/reports/2026-05-30_rl_stage01_opening_route_recovery_probe_001/stage01_opening_route_recovery.zip`
- Training: `512` PPO timesteps on `soda-creek`, seeds `63400-63402`, 60 second training window

## Result

The repair profile improved the short fixed-window picture but did not clear the stage 01 gate.

| Window | Average Policy Win Rate | Average Survival | Gate |
|---|---:|---:|---|
| 60s | `0.7778` | `55.2328s` | `multimap_comparison_recorded_not_balance_gate` |
| 180s | `0.6667` | `138.3691s` | `multimap_comparison_recorded_not_balance_gate` |
| 300s | `0.0` | `174.9455s` | `multimap_comparison_recorded_needs_policy_repair` |

Compared with the same-seed parent baseline, `validate_policy_window_regression.py` returned `policy_window_regression_failed` with `5` blockers:

- `180s/cracked-star-jar`: win-rate delta `-0.3333`
- `180s/cracked-star-jar`: average survival dropped `31.0702s`
- `180s/soda-creek`: average survival dropped `0.0445s`
- `60s/caramel-workshop`: average survival dropped `0.5667s`
- `60s/soda-creek`: average survival dropped `0.0667s`

## Interpretation

This run is useful diagnostic evidence: action `7` becomes dominant again in the 60s comparison, and 300s average survival improves over the parent baseline on all three high-pressure maps. It is still not a usable checkpoint because strict parent no-regression fails and 300s win rate remains `0.0/0.0/0.0`.

## Next Step

Do not enter stage 02 from this checkpoint. The next stage 01 repair should keep the opening-route-recovery signal but add a stricter parent-preservation / action-distribution guard around `cracked-star-jar` 180s and the tiny 60s survival regressions, then rerun 60/180/300 second same-seed parent no-regression.
