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
| coward | repair | low-skill rule bot 10%-35% | 0.0% | 0/3 | 200.5 | 6.3 | 296.7 | 37 |
| greedy | repair | mid-skill rule bot 25%-55% | 0.0% | 0/3 | 226.7 | 9.0 | 356.0 | 16 |
| kite | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 279.6 | 10.0 | 489.0 | 14 |
| tank | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 185.0 | 5.7 | 259.7 | 31 |
| boss-hunter | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 245.6 | 7.0 | 422.0 | 18 |
| zone-control | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 248.4 | 6.7 | 403.7 | 21 |
| route | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 248.4 | 6.0 | 410.0 | 26 |

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
| 70002 | defeat | 223.0 | 7 | 338 | 120.6 | 18 |

### coward

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 121.1 | 3 | 101 | 120.0 | 37 |
| 70001 | defeat | 248.6 | 8 | 416 | 152.8 | 17 |
| 70002 | defeat | 231.8 | 8 | 373 | 120.1 | 10 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 226.0 | 8 | 351 | 120.7 | 15 |
| 70001 | defeat | 229.2 | 9 | 366 | 120.1 | 11 |
| 70002 | defeat | 225.1 | 10 | 351 | 120.1 | 16 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 11 | 531 | 95.3 | 13 |
| 70001 | victory | 300.0 | 11 | 542 | 50.2 | 10 |
| 70002 | defeat | 238.9 | 8 | 394 | 120.7 | 14 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 124.8 | 4 | 118 | 136.8 | 28 |
| 70001 | defeat | 130.2 | 4 | 132 | 120.0 | 31 |
| 70002 | victory | 300.0 | 9 | 529 | 106.5 | 13 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 8 | 552 | 93.3 | 14 |
| 70001 | defeat | 136.8 | 5 | 155 | 120.1 | 18 |
| 70002 | victory | 300.0 | 8 | 559 | 87.4 | 17 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 8 | 535 | 58.4 | 16 |
| 70001 | defeat | 222.9 | 6 | 339 | 120.9 | 19 |
| 70002 | defeat | 222.2 | 6 | 337 | 121.0 | 21 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 6 | 537 | 59.0 | 18 |
| 70001 | defeat | 218.5 | 6 | 334 | 120.2 | 26 |
| 70002 | defeat | 226.9 | 6 | 359 | 120.2 | 17 |

## Gate Notes

- Bots outside target and needing balance review: `coward`, `greedy`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
