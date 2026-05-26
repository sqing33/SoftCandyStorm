# Harness Performance Budget Validation

- Source: `harness/reports/2026-05-27_base_demo_bot_policy_calibration_600s_seed53000_20seed_001/metrics.json`
- Decision: `harness_performance_budget_valid`
- Bots: `9`
- Runs: `180`
- Observed max enemies: `56`
- Max enemy ceiling: `140`
- Warning enemy ceiling: `105`

## Bot Summary

| Bot | Map | Seeds | Seconds | Win Rate | Max Enemies |
|---|---|---:|---:|---:|---:|
| `idle` | `frosting-grassland` | 20 | 600 | 0.0% | 23 |
| `random` | `frosting-grassland` | 20 | 600 | 5.0% | 25 |
| `coward` | `frosting-grassland` | 20 | 600 | 20.0% | 52 |
| `greedy` | `frosting-grassland` | 20 | 600 | 55.0% | 38 |
| `kite` | `frosting-grassland` | 20 | 600 | 75.0% | 18 |
| `tank` | `frosting-grassland` | 20 | 600 | 25.0% | 56 |
| `boss-hunter` | `frosting-grassland` | 20 | 600 | 65.0% | 22 |
| `zone-control` | `frosting-grassland` | 20 | 600 | 25.0% | 23 |
| `route` | `frosting-grassland` | 20 | 600 | 15.0% | 45 |

## Errors

- None

## Warnings

- None

## Limitations

- This validates headless Harness metrics only; it does not measure Runtime FPS, GPU cost, memory growth, or frame pacing.
- A valid result supports entity-budget and no-deadlock evidence, but does not make a Release Candidate ready.
- Manual playtest, content acceptance, asset acceptance, and privacy gates remain separate release requirements.
