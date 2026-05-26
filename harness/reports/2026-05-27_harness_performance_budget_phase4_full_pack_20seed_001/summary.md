# Harness Performance Budget Validation

- Source: `harness/reports/2026-05-27_phase4_full_pack_release_probe_matrix_20seed_001/metrics.json`
- Decision: `harness_performance_budget_valid`
- Bots: `9`
- Runs: `180`
- Observed max enemies: `75`
- Max enemy ceiling: `140`
- Warning enemy ceiling: `105`

## Bot Summary

| Bot | Map | Seeds | Seconds | Win Rate | Max Enemies |
|---|---|---:|---:|---:|---:|
| `idle` | `frosting-grassland` | 20 | 600 | 0.0% | 23 |
| `random` | `frosting-grassland` | 20 | 600 | 0.0% | 23 |
| `coward` | `frosting-grassland` | 20 | 600 | 20.0% | 75 |
| `greedy` | `frosting-grassland` | 20 | 600 | 65.0% | 52 |
| `kite` | `frosting-grassland` | 20 | 600 | 65.0% | 56 |
| `tank` | `frosting-grassland` | 20 | 600 | 80.0% | 73 |
| `boss-hunter` | `frosting-grassland` | 20 | 600 | 45.0% | 42 |
| `zone-control` | `frosting-grassland` | 20 | 600 | 45.0% | 39 |
| `route` | `frosting-grassland` | 20 | 600 | 15.0% | 64 |

## Errors

- None

## Warnings

- None

## Limitations

- This validates headless Harness metrics only; it does not measure Runtime FPS, GPU cost, memory growth, or frame pacing.
- A valid result supports entity-budget and no-deadlock evidence, but does not make a Release Candidate ready.
- Manual playtest, content acceptance, asset acceptance, and privacy gates remain separate release requirements.
