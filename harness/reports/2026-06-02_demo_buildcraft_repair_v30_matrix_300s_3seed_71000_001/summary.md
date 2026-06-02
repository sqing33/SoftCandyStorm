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
| coward | repair | low-skill rule bot 10%-35% | 66.7% | 2/3 | 276.2 | 10.0 | 481.0 | 14 |
| greedy | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 247.7 | 10.0 | 405.3 | 39 |
| kite | repair | high-skill rule bot 45%-75% | 100.0% | 3/3 | 300.0 | 11.0 | 541.7 | 17 |
| tank | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 270.2 | 8.0 | 464.7 | 22 |
| boss-hunter | repair | high-skill rule bot 45%-75% | 33.3% | 1/3 | 259.5 | 8.3 | 436.3 | 15 |
| zone-control | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 272.9 | 7.7 | 471.0 | 22 |
| route | repair | low-skill rule bot 10%-35% | 66.7% | 2/3 | 273.0 | 6.0 | 474.0 | 25 |

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
| 71000 | victory | 300.0 | 11 | 545 | 89.0 | 14 |
| 71001 | victory | 300.0 | 11 | 535 | 74.7 | 11 |
| 71002 | defeat | 228.5 | 8 | 363 | 120.1 | 14 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 12 | 536 | 63.5 | 15 |
| 71001 | defeat | 225.1 | 9 | 347 | 120.1 | 15 |
| 71002 | defeat | 217.9 | 9 | 333 | 120.4 | 39 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 11 | 550 | 110.9 | 17 |
| 71001 | victory | 300.0 | 11 | 540 | 101.3 | 12 |
| 71002 | victory | 300.0 | 11 | 535 | 50.3 | 11 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 8 | 542 | 96.6 | 20 |
| 71001 | victory | 300.0 | 9 | 531 | 85.8 | 16 |
| 71002 | defeat | 210.6 | 7 | 321 | 143.5 | 22 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 264.4 | 9 | 452 | 120.2 | 15 |
| 71001 | victory | 300.0 | 9 | 536 | 82.7 | 13 |
| 71002 | defeat | 214.0 | 7 | 321 | 120.7 | 14 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 8 | 530 | 70.9 | 15 |
| 71001 | defeat | 218.8 | 7 | 327 | 122.2 | 22 |
| 71002 | victory | 300.0 | 8 | 556 | 85.7 | 14 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 6 | 554 | 110.3 | 16 |
| 71001 | victory | 300.0 | 6 | 534 | 89.6 | 21 |
| 71002 | defeat | 219.0 | 6 | 334 | 127.5 | 25 |

## Gate Notes

- Bots outside target and needing balance review: `coward`, `kite`, `tank`, `boss-hunter`, `zone-control`, `route`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
