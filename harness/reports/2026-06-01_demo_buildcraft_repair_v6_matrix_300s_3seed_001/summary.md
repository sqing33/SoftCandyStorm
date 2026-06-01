# Harness Bot Matrix Summary

- Map: `frosting-grassland`
- Seeds: `70000`..`70002` per bot
- Duration target: `300` seconds
- Tick rate: `30`
- Bot count: `9`

## Bot Results

| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |
|---|---|---|---:|---:|---:|---:|---:|---:|
| idle | pass | idle pressure floor 0%-0% | 0.0% | 0/3 | 107.0 | 1.0 | 85.3 | 24 |
| random | repair | random robustness 0%-15% | 33.3% | 1/3 | 212.8 | 5.7 | 349.0 | 16 |
| coward | repair | low-skill rule bot 10%-35% | 0.0% | 0/3 | 194.8 | 6.3 | 287.3 | 33 |
| greedy | repair | mid-skill rule bot 25%-55% | 100.0% | 3/3 | 300.0 | 11.7 | 541.7 | 15 |
| kite | repair | high-skill rule bot 45%-75% | 100.0% | 3/3 | 300.0 | 11.0 | 546.3 | 14 |
| tank | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 190.9 | 6.0 | 270.0 | 49 |
| boss-hunter | repair | high-skill rule bot 45%-75% | 33.3% | 1/3 | 242.5 | 7.0 | 403.0 | 17 |
| zone-control | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 250.2 | 7.3 | 416.7 | 17 |
| route | repair | low-skill rule bot 10%-35% | 66.7% | 2/3 | 274.5 | 7.3 | 483.0 | 27 |

## Runs

### idle

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 108.3 | 1 | 87 | 120.1 | 24 |
| 70001 | defeat | 106.2 | 1 | 85 | 120.1 | 22 |
| 70002 | defeat | 106.5 | 1 | 84 | 120.0 | 23 |

### random

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 222.2 | 6 | 360 | 120.4 | 16 |
| 70001 | defeat | 116.1 | 3 | 121 | 120.1 | 15 |
| 70002 | victory | 300.0 | 8 | 566 | 110.7 | 15 |

### coward

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 125.0 | 3 | 115 | 121.1 | 33 |
| 70001 | defeat | 218.6 | 8 | 346 | 152.7 | 17 |
| 70002 | defeat | 240.8 | 8 | 401 | 120.3 | 17 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 12 | 538 | 99.9 | 15 |
| 70001 | victory | 300.0 | 11 | 552 | 75.3 | 13 |
| 70002 | victory | 300.0 | 12 | 535 | 77.9 | 14 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 11 | 544 | 81.3 | 12 |
| 70001 | victory | 300.0 | 11 | 552 | 98.7 | 10 |
| 70002 | victory | 300.0 | 11 | 543 | 90.0 | 14 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 133.2 | 4 | 127 | 136.1 | 39 |
| 70001 | defeat | 139.6 | 4 | 131 | 127.1 | 49 |
| 70002 | victory | 300.0 | 10 | 552 | 93.7 | 15 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 8 | 547 | 95.3 | 14 |
| 70001 | defeat | 213.9 | 7 | 333 | 127.0 | 17 |
| 70002 | defeat | 213.5 | 6 | 329 | 120.1 | 16 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 8 | 533 | 97.9 | 16 |
| 70001 | defeat | 228.5 | 7 | 370 | 120.1 | 17 |
| 70002 | defeat | 222.2 | 7 | 347 | 120.6 | 15 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 7 | 539 | 119.8 | 20 |
| 70001 | defeat | 223.5 | 7 | 357 | 136.4 | 27 |
| 70002 | victory | 300.0 | 8 | 553 | 109.1 | 18 |

## Gate Notes

- Bots outside target and needing balance review: `random`, `coward`, `greedy`, `kite`, `boss-hunter`, `route`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
