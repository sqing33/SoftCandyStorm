# Harness Bot Matrix Summary

- Map: `frosting-grassland`
- Seeds: `71000`..`71002` per bot
- Duration target: `300` seconds
- Tick rate: `30`
- Bot count: `9`

## Bot Results

| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |
|---|---|---|---:|---:|---:|---:|---:|---:|
| idle | pass | idle pressure floor 0%-0% | 0.0% | 0/3 | 106.8 | 1.0 | 85.3 | 22 |
| random | pass | random robustness 0%-15% | 0.0% | 0/3 | 107.3 | 2.0 | 89.0 | 24 |
| coward | repair | low-skill rule bot 10%-35% | 66.7% | 2/3 | 276.8 | 10.0 | 487.3 | 22 |
| greedy | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 272.9 | 11.0 | 475.3 | 37 |
| kite | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 276.6 | 10.3 | 487.3 | 20 |
| tank | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 270.4 | 8.7 | 474.3 | 22 |
| boss-hunter | repair | high-skill rule bot 45%-75% | 100.0% | 3/3 | 300.0 | 9.0 | 546.0 | 14 |
| zone-control | repair | mid-skill rule bot 25%-55% | 0.0% | 0/3 | 222.7 | 6.3 | 348.0 | 23 |
| route | repair | low-skill rule bot 10%-35% | 66.7% | 2/3 | 273.0 | 6.0 | 476.0 | 25 |

## Runs

### idle

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 107.4 | 1 | 87 | 120.4 | 22 |
| 71001 | defeat | 107.0 | 1 | 85 | 120.4 | 22 |
| 71002 | defeat | 106.1 | 1 | 84 | 120.4 | 22 |

### random

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 107.8 | 2 | 96 | 120.3 | 18 |
| 71001 | defeat | 107.6 | 2 | 86 | 120.0 | 24 |
| 71002 | defeat | 106.7 | 2 | 85 | 120.7 | 22 |

### coward

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 11 | 547 | 59.0 | 13 |
| 71001 | defeat | 230.5 | 7 | 366 | 126.9 | 22 |
| 71002 | victory | 300.0 | 12 | 549 | 68.7 | 10 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 12 | 545 | 76.0 | 16 |
| 71001 | victory | 300.0 | 12 | 544 | 98.7 | 16 |
| 71002 | defeat | 218.8 | 9 | 337 | 120.6 | 37 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 229.9 | 9 | 380 | 120.0 | 20 |
| 71001 | victory | 300.0 | 11 | 538 | 49.3 | 10 |
| 71002 | victory | 300.0 | 11 | 544 | 75.1 | 11 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 9 | 543 | 110.8 | 17 |
| 71001 | victory | 300.0 | 9 | 533 | 113.4 | 16 |
| 71002 | defeat | 211.0 | 8 | 347 | 152.5 | 22 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 9 | 541 | 74.2 | 14 |
| 71001 | victory | 300.0 | 9 | 550 | 76.7 | 14 |
| 71002 | victory | 300.0 | 9 | 547 | 87.8 | 14 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 222.1 | 6 | 360 | 120.6 | 17 |
| 71001 | defeat | 224.6 | 6 | 350 | 121.2 | 17 |
| 71002 | defeat | 221.5 | 7 | 334 | 120.7 | 23 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 219.0 | 6 | 338 | 120.0 | 17 |
| 71001 | victory | 300.0 | 6 | 535 | 97.9 | 21 |
| 71002 | victory | 300.0 | 6 | 555 | 107.5 | 25 |

## Gate Notes

- Bots outside target and needing balance review: `coward`, `greedy`, `tank`, `boss-hunter`, `zone-control`, `route`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
