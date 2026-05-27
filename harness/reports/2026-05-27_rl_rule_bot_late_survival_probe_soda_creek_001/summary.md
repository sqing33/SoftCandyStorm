# Harness Bot Matrix Summary

- Map: `soda-creek`
- Seeds: `62300`..`62304` per bot
- Duration target: `300` seconds
- Tick rate: `30`
- Bot count: `4`

## Bot Results

| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |
|---|---|---|---:|---:|---:|---:|---:|---:|
| greedy | repair | mid-skill rule bot 25%-55% | 20.0% | 1/5 | 192.6 | 9.8 | 459.8 | 39 |
| kite | repair | high-skill rule bot 45%-75% | 80.0% | 4/5 | 284.4 | 12.0 | 742.2 | 22 |
| boss-hunter | repair | high-skill rule bot 45%-75% | 0.0% | 0/5 | 215.8 | 6.8 | 501.6 | 23 |
| zone-control | repair | mid-skill rule bot 25%-55% | 0.0% | 0/5 | 162.3 | 5.6 | 337.8 | 29 |

## Runs

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 62300 | defeat | 35.7 | 3 | 34 | 120.0 | 9 |
| 62301 | defeat | 159.8 | 10 | 317 | 120.0 | 20 |
| 62302 | victory | 300.0 | 13 | 781 | 101.0 | 24 |
| 62303 | defeat | 238.7 | 12 | 614 | 120.3 | 39 |
| 62304 | defeat | 228.7 | 11 | 553 | 120.6 | 30 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 62300 | victory | 300.0 | 14 | 823 | 92.3 | 22 |
| 62301 | victory | 300.0 | 12 | 772 | 54.4 | 10 |
| 62302 | victory | 300.0 | 12 | 793 | 54.4 | 9 |
| 62303 | defeat | 222.1 | 10 | 533 | 120.5 | 22 |
| 62304 | victory | 300.0 | 12 | 790 | 51.0 | 8 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 62300 | defeat | 214.2 | 6 | 482 | 120.5 | 18 |
| 62301 | defeat | 216.2 | 7 | 508 | 137.1 | 22 |
| 62302 | defeat | 215.8 | 7 | 494 | 120.4 | 23 |
| 62303 | defeat | 216.2 | 6 | 517 | 121.5 | 21 |
| 62304 | defeat | 216.7 | 8 | 507 | 120.2 | 19 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 62300 | defeat | 219.1 | 6 | 513 | 120.4 | 17 |
| 62301 | defeat | 34.2 | 2 | 38 | 120.0 | 11 |
| 62302 | defeat | 220.5 | 7 | 471 | 136.1 | 29 |
| 62303 | defeat | 122.9 | 5 | 191 | 120.1 | 18 |
| 62304 | defeat | 214.6 | 8 | 476 | 120.2 | 18 |

## Gate Notes

- Bots outside target and needing balance review: `greedy`, `kite`, `boss-hunter`, `zone-control`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
