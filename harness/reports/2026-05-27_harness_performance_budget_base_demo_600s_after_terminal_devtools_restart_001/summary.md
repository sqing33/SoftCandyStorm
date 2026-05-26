# Harness Performance Budget Validation

- Source: `harness/reports/2026-05-27_base_demo_all_bot_matrix_600s_after_terminal_devtools_restart_001/metrics.json`
- Decision: `harness_performance_budget_valid`
- Bots: `9`
- Runs: `45`
- Observed max enemies: `59`
- Max enemy ceiling: `140`
- Warning enemy ceiling: `105`

## Bot Summary

| Bot | Map | Seeds | Seconds | Win Rate | Max Enemies |
|---|---|---:|---:|---:|---:|
| `idle` | `frosting-grassland` | 5 | 600 | 0.0% | 23 |
| `random` | `frosting-grassland` | 5 | 600 | 0.0% | 23 |
| `coward` | `frosting-grassland` | 5 | 600 | 0.0% | 22 |
| `greedy` | `frosting-grassland` | 5 | 600 | 60.0% | 33 |
| `kite` | `frosting-grassland` | 5 | 600 | 100.0% | 31 |
| `tank` | `frosting-grassland` | 5 | 600 | 100.0% | 20 |
| `boss-hunter` | `frosting-grassland` | 5 | 600 | 100.0% | 33 |
| `zone-control` | `frosting-grassland` | 5 | 600 | 100.0% | 28 |
| `route` | `frosting-grassland` | 5 | 600 | 40.0% | 59 |

## Errors

- None

## Warnings

- None

## Limitations

- This validates headless Harness metrics only; it does not measure Runtime FPS, GPU cost, memory growth, or frame pacing.
- A valid result supports entity-budget and no-deadlock evidence, but does not make a Release Candidate ready.
- Manual playtest, content acceptance, asset acceptance, and privacy gates remain separate release requirements.
