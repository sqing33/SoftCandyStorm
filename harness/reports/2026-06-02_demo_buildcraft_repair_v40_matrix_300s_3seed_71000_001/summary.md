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
| coward | repair | low-skill rule bot 10%-35% | 0.0% | 0/3 | 238.9 | 8.3 | 393.0 | 14 |
| greedy | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 273.7 | 10.7 | 470.3 | 21 |
| kite | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 273.0 | 10.3 | 475.3 | 17 |
| tank | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 270.2 | 8.3 | 462.3 | 22 |
| boss-hunter | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 271.8 | 8.0 | 466.7 | 14 |
| zone-control | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 247.7 | 7.7 | 403.3 | 22 |
| route | repair | low-skill rule bot 10%-35% | 66.7% | 2/3 | 273.0 | 6.0 | 468.7 | 25 |

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
| 71000 | defeat | 244.1 | 9 | 408 | 136.3 | 14 |
| 71001 | defeat | 241.3 | 8 | 400 | 120.6 | 13 |
| 71002 | defeat | 231.2 | 8 | 371 | 136.7 | 14 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 12 | 544 | 83.5 | 16 |
| 71001 | victory | 300.0 | 11 | 534 | 98.8 | 13 |
| 71002 | defeat | 221.0 | 9 | 333 | 120.1 | 21 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 219.0 | 9 | 351 | 120.3 | 17 |
| 71001 | victory | 300.0 | 10 | 534 | 49.3 | 10 |
| 71002 | victory | 300.0 | 12 | 541 | 76.0 | 13 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 9 | 533 | 119.9 | 19 |
| 71001 | victory | 300.0 | 10 | 535 | 55.0 | 17 |
| 71002 | defeat | 210.5 | 6 | 319 | 142.3 | 22 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 215.5 | 7 | 330 | 120.3 | 14 |
| 71001 | victory | 300.0 | 8 | 541 | 75.3 | 13 |
| 71002 | victory | 300.0 | 9 | 529 | 75.4 | 13 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 8 | 537 | 111.6 | 15 |
| 71001 | defeat | 218.8 | 7 | 327 | 121.2 | 22 |
| 71002 | defeat | 224.4 | 8 | 346 | 120.2 | 18 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 6 | 536 | 119.9 | 15 |
| 71001 | victory | 300.0 | 6 | 536 | 91.6 | 21 |
| 71002 | defeat | 219.1 | 6 | 334 | 127.1 | 25 |

## Gate Notes

- Bots outside target and needing balance review: `coward`, `greedy`, `tank`, `route`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
