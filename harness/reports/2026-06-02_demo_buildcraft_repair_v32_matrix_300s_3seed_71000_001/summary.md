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
| coward | repair | low-skill rule bot 10%-35% | 66.7% | 2/3 | 276.2 | 9.7 | 473.3 | 18 |
| greedy | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 250.9 | 9.7 | 416.0 | 39 |
| kite | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 273.0 | 10.3 | 480.7 | 17 |
| tank | repair | mid-skill rule bot 25%-55% | 0.0% | 0/3 | 234.7 | 7.3 | 377.0 | 22 |
| boss-hunter | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 293.8 | 9.0 | 520.0 | 14 |
| zone-control | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 272.9 | 7.7 | 474.3 | 22 |
| route | repair | low-skill rule bot 10%-35% | 66.7% | 2/3 | 273.0 | 6.0 | 471.0 | 25 |

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
| 71000 | victory | 300.0 | 11 | 527 | 75.8 | 14 |
| 71001 | victory | 300.0 | 10 | 539 | 119.7 | 11 |
| 71002 | defeat | 228.7 | 8 | 354 | 120.5 | 18 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 11 | 546 | 63.5 | 15 |
| 71001 | defeat | 234.6 | 9 | 370 | 120.7 | 13 |
| 71002 | defeat | 218.0 | 9 | 332 | 120.2 | 39 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 219.0 | 9 | 351 | 120.3 | 17 |
| 71001 | victory | 300.0 | 11 | 543 | 99.5 | 11 |
| 71002 | victory | 300.0 | 11 | 548 | 50.3 | 11 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 269.9 | 8 | 462 | 123.3 | 19 |
| 71001 | defeat | 223.5 | 7 | 348 | 120.8 | 16 |
| 71002 | defeat | 210.6 | 7 | 321 | 143.5 | 22 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 281.5 | 9 | 486 | 127.2 | 14 |
| 71001 | victory | 300.0 | 9 | 539 | 92.7 | 13 |
| 71002 | victory | 300.0 | 9 | 535 | 73.6 | 14 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 8 | 541 | 111.6 | 15 |
| 71001 | defeat | 218.8 | 7 | 327 | 121.2 | 22 |
| 71002 | victory | 300.0 | 8 | 555 | 105.7 | 14 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 6 | 547 | 112.7 | 16 |
| 71001 | victory | 300.0 | 6 | 532 | 91.6 | 21 |
| 71002 | defeat | 219.1 | 6 | 334 | 127.1 | 25 |

## Gate Notes

- Bots outside target and needing balance review: `coward`, `tank`, `zone-control`, `route`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
