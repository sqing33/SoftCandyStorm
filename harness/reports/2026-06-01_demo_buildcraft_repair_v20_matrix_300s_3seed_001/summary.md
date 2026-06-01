# Harness Bot Matrix Summary

- Map: `frosting-grassland`
- Seeds: `70000`..`70002` per bot
- Duration target: `300` seconds
- Tick rate: `30`
- Bot count: `9`

## Bot Results

| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |
|---|---|---|---:|---:|---:|---:|---:|---:|
| idle | pass | idle pressure floor 0%-0% | 0.0% | 0/3 | 107.3 | 1.3 | 85.7 | 24 |
| random | pass | random robustness 0%-15% | 0.0% | 0/3 | 148.7 | 4.0 | 177.0 | 22 |
| coward | repair | low-skill rule bot 10%-35% | 0.0% | 0/3 | 200.7 | 6.3 | 297.0 | 37 |
| greedy | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 250.3 | 9.7 | 413.7 | 16 |
| kite | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 280.5 | 10.7 | 491.3 | 13 |
| tank | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 185.0 | 5.7 | 263.0 | 31 |
| boss-hunter | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 244.1 | 7.3 | 417.3 | 18 |
| zone-control | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 248.3 | 7.0 | 404.7 | 21 |
| route | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 248.4 | 6.0 | 411.3 | 26 |

## Runs

### idle

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 108.7 | 1 | 87 | 120.9 | 24 |
| 70001 | defeat | 106.4 | 1 | 85 | 120.3 | 21 |
| 70002 | defeat | 106.9 | 2 | 85 | 120.6 | 23 |

### random

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 117.1 | 3 | 109 | 136.2 | 21 |
| 70001 | defeat | 106.0 | 2 | 84 | 121.0 | 22 |
| 70002 | defeat | 223.0 | 7 | 338 | 120.5 | 20 |

### coward

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 121.1 | 3 | 101 | 120.0 | 37 |
| 70001 | defeat | 249.4 | 8 | 417 | 153.6 | 15 |
| 70002 | defeat | 231.8 | 8 | 373 | 120.1 | 10 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 225.9 | 8 | 351 | 120.7 | 15 |
| 70001 | victory | 300.0 | 11 | 539 | 74.9 | 11 |
| 70002 | defeat | 225.1 | 10 | 351 | 120.1 | 16 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 12 | 533 | 96.3 | 13 |
| 70001 | victory | 300.0 | 11 | 538 | 49.5 | 10 |
| 70002 | defeat | 241.4 | 9 | 403 | 120.7 | 13 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 124.8 | 4 | 118 | 136.8 | 28 |
| 70001 | defeat | 130.2 | 4 | 132 | 120.0 | 31 |
| 70002 | victory | 300.0 | 9 | 539 | 105.1 | 13 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 9 | 545 | 92.7 | 14 |
| 70001 | defeat | 132.3 | 5 | 146 | 126.0 | 18 |
| 70002 | victory | 300.0 | 8 | 561 | 87.4 | 17 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 9 | 538 | 80.4 | 16 |
| 70001 | defeat | 222.9 | 6 | 339 | 121.2 | 19 |
| 70002 | defeat | 222.2 | 6 | 337 | 121.0 | 21 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 6 | 539 | 59.0 | 18 |
| 70001 | defeat | 218.5 | 6 | 334 | 120.2 | 26 |
| 70002 | defeat | 226.8 | 6 | 361 | 120.2 | 17 |

## Gate Notes

- Bots outside target and needing balance review: `coward`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
