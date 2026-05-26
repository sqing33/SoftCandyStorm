# Harness Performance Budget Validation

- Source: `harness/reports/2026-05-26_phase4_full_pack_balance_repair_simulation_005/2026-05-26_phase4_roster_gap_full_pack/metrics.json`
- Decision: `harness_performance_budget_valid`
- Bots: `9`
- Runs: `45`
- Observed max enemies: `43`
- Max enemy ceiling: `140`
- Warning enemy ceiling: `105`

## Bot Summary

| Bot | Map | Seeds | Seconds | Win Rate | Max Enemies |
|---|---|---:|---:|---:|---:|
| `idle` | `frosting-grassland` | 5 | 600 | 0.0% | 21 |
| `random` | `frosting-grassland` | 5 | 600 | 0.0% | 22 |
| `coward` | `frosting-grassland` | 5 | 600 | 20.0% | 30 |
| `greedy` | `frosting-grassland` | 5 | 600 | 40.0% | 40 |
| `kite` | `frosting-grassland` | 5 | 600 | 60.0% | 34 |
| `tank` | `frosting-grassland` | 5 | 600 | 40.0% | 40 |
| `boss-hunter` | `frosting-grassland` | 5 | 600 | 60.0% | 35 |
| `zone-control` | `frosting-grassland` | 5 | 600 | 40.0% | 33 |
| `route` | `frosting-grassland` | 5 | 600 | 20.0% | 43 |

## Errors

- None

## Warnings

- None

## Limitations

- This validates headless Harness metrics only; it does not measure Runtime FPS, GPU cost, memory growth, or frame pacing.
- A valid result supports entity-budget and no-deadlock evidence, but does not make a Release Candidate ready.
- Manual playtest, content acceptance, asset acceptance, and privacy gates remain separate release requirements.
