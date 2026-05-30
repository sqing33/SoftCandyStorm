# Stage 01 Opening Route Recovery Conservative Sweep

- Decision: `limited_followup_not_stage02`
- Best run: `learning_rate=5e-7`, `256` PPO timesteps, `opening-route-recovery`
- Start model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Output model: `harness/reports/2026-05-30_rl_stage01_opening_route_recovery_lr5e7_probe_001/stage01_opening_route_recovery_lr5e7.zip`

## Sweep Results

| Variant | Parent No-Regression | Blockers | Notable Result |
|---|---|---:|---|
| `lr=5e-6` | `policy_window_regression_failed` | `1` | 60s and 180s passed; 300s `cracked-star-jar` average survival dropped `1.956s`. |
| `lr=2e-6` | `policy_window_regression_failed` | `2` | 60s `caramel-workshop` improved to `1.0`, but 180s / 300s `caramel-workshop` had tiny survival regressions. |
| `lr=1e-6` | `policy_window_regression_failed` | `1` | 300s `cracked-star-jar` recovered to `0.3333`, but 300s `caramel-workshop` average survival dropped `0.1444s`. |
| `lr=5e-7` | `policy_window_regression_passed` | `0` | 60s `caramel-workshop` improved to `1.0`; 60s / 180s / 300s parent no-regression passed. |

## Best Run Fixed Windows

| Window | Average Policy Win Rate | Average Survival |
|---|---:|---:|
| 60s | `0.8889` | `57.5106s` |
| 180s | `0.6667` | `141.7209s` |
| 300s | `0.0` | `165.5783s` |

## Interpretation

The sweep shows that `opening-route-recovery` can be made parent-preserving by lowering the learning rate to `5e-7`. This is useful repair evidence, but it does not clear stage 01 because `soda-creek` 60s remains `0.6667` and the known opening failure surface is still present. The 300s window also remains `0.0/0.0/0.0`, so this checkpoint is not a policy candidate and must not enter stage 02.

## Next Step

Use the `5e-7` checkpoint only as a parent-preserving diagnostic baseline. The next stage 01 attempt should add a target-specific seed `63402` opening objective or action-distribution guard on top of this conservative setting, then rerun 60/180/300 second same-seed parent no-regression.
