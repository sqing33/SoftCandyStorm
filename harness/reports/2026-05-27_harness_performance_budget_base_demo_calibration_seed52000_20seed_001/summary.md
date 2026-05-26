# Harness Performance Budget Validation

- Source: `harness/reports/2026-05-27_base_demo_bot_policy_calibration_600s_seed52000_20seed_001/metrics.json`
- Decision: `harness_performance_budget_valid`
- Bots: `9`
- Runs: `180`
- Observed max enemies: `55`
- Max enemy ceiling: `140`
- Warning enemy ceiling: `105`

## Bot Summary

| Bot | Map | Seeds | Seconds | Win Rate | Max Enemies |
|---|---|---:|---:|---:|---:|
| `idle` | `frosting-grassland` | 20 | 600 | 0.0% | 23 |
| `random` | `frosting-grassland` | 20 | 600 | 0.0% | 23 |
| `coward` | `frosting-grassland` | 20 | 600 | 10.0% | 41 |
| `greedy` | `frosting-grassland` | 20 | 600 | 50.0% | 44 |
| `kite` | `frosting-grassland` | 20 | 600 | 70.0% | 27 |
| `tank` | `frosting-grassland` | 20 | 600 | 30.0% | 55 |
| `boss-hunter` | `frosting-grassland` | 20 | 600 | 65.0% | 20 |
| `zone-control` | `frosting-grassland` | 20 | 600 | 25.0% | 21 |
| `route` | `frosting-grassland` | 20 | 600 | 15.0% | 55 |

## Errors

- None

## Warnings

- None

## Limitations

- This validates headless Harness metrics only; it does not measure Runtime FPS, GPU cost, memory growth, or frame pacing.
- A valid result supports entity-budget and no-deadlock evidence, but does not make a Release Candidate ready.
- Manual playtest, content acceptance, asset acceptance, and privacy gates remain separate release requirements.
