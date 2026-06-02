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
| random | pass | random robustness 0%-15% | 0.0% | 0/3 | 107.2 | 2.0 | 87.7 | 24 |
| coward | repair | low-skill rule bot 10%-35% | 100.0% | 3/3 | 300.0 | 11.3 | 543.7 | 17 |
| greedy | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 271.7 | 10.7 | 467.7 | 19 |
| kite | repair | high-skill rule bot 45%-75% | 100.0% | 3/3 | 300.0 | 11.0 | 544.0 | 12 |
| tank | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 273.4 | 8.0 | 470.3 | 19 |
| boss-hunter | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 271.8 | 8.3 | 468.3 | 14 |
| zone-control | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 239.7 | 6.3 | 405.7 | 18 |
| route | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 216.4 | 5.0 | 336.3 | 35 |

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
| 71000 | defeat | 107.3 | 2 | 92 | 120.4 | 18 |
| 71001 | defeat | 107.6 | 2 | 86 | 120.0 | 24 |
| 71002 | defeat | 106.7 | 2 | 85 | 120.7 | 22 |

### coward

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 11 | 554 | 116.5 | 17 |
| 71001 | victory | 300.0 | 12 | 537 | 49.3 | 12 |
| 71002 | victory | 300.0 | 11 | 540 | 107.4 | 12 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 12 | 545 | 94.6 | 14 |
| 71001 | victory | 300.0 | 11 | 532 | 92.0 | 12 |
| 71002 | defeat | 215.0 | 9 | 326 | 120.1 | 19 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 11 | 550 | 53.0 | 11 |
| 71001 | victory | 300.0 | 11 | 533 | 74.0 | 12 |
| 71002 | victory | 300.0 | 11 | 549 | 97.2 | 10 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 220.2 | 6 | 334 | 120.8 | 19 |
| 71001 | victory | 300.0 | 9 | 537 | 97.5 | 14 |
| 71002 | victory | 300.0 | 9 | 540 | 74.5 | 14 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 215.5 | 7 | 329 | 120.3 | 14 |
| 71001 | victory | 300.0 | 9 | 530 | 100.8 | 13 |
| 71002 | victory | 300.0 | 9 | 546 | 74.6 | 12 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 119.0 | 3 | 117 | 120.2 | 18 |
| 71001 | victory | 300.0 | 8 | 528 | 91.2 | 14 |
| 71002 | victory | 300.0 | 8 | 572 | 74.0 | 14 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 218.7 | 5 | 337 | 120.0 | 16 |
| 71001 | victory | 300.0 | 6 | 537 | 107.1 | 25 |
| 71002 | defeat | 130.5 | 4 | 135 | 120.3 | 35 |

## Gate Notes

- Bots outside target and needing balance review: `coward`, `greedy`, `kite`, `tank`, `zone-control`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
