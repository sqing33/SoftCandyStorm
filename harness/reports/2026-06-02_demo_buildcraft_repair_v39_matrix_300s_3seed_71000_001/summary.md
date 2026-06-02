# Harness Bot Matrix Summary

- Map: `frosting-grassland`
- Seeds: `71000`..`71002` per bot
- Duration target: `300` seconds
- Tick rate: `30`
- Bot count: `9`

## Bot Results

| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |
|---|---|---|---:|---:|---:|---:|---:|---:|
| idle | pass | idle pressure floor 0%-0% | 0.0% | 0/3 | 106.9 | 1.0 | 86.0 | 22 |
| random | pass | random robustness 0%-15% | 0.0% | 0/3 | 146.8 | 4.0 | 181.7 | 22 |
| coward | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 255.3 | 7.3 | 435.7 | 15 |
| greedy | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 254.5 | 10.0 | 429.3 | 15 |
| kite | repair | high-skill rule bot 45%-75% | 100.0% | 3/3 | 300.0 | 10.7 | 542.3 | 14 |
| tank | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 271.8 | 8.7 | 472.3 | 20 |
| boss-hunter | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 274.4 | 8.3 | 477.3 | 16 |
| zone-control | repair | mid-skill rule bot 25%-55% | 0.0% | 0/3 | 222.7 | 6.0 | 342.3 | 25 |
| route | repair | low-skill rule bot 10%-35% | 66.7% | 2/3 | 274.4 | 6.0 | 471.7 | 23 |

## Runs

### idle

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 107.8 | 1 | 89 | 121.0 | 21 |
| 71001 | defeat | 106.8 | 1 | 85 | 120.1 | 22 |
| 71002 | defeat | 106.0 | 1 | 84 | 121.1 | 21 |

### random

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 111.7 | 3 | 100 | 120.1 | 18 |
| 71001 | defeat | 107.1 | 2 | 85 | 120.2 | 22 |
| 71002 | defeat | 221.6 | 7 | 360 | 120.5 | 15 |

### coward

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 237.7 | 7 | 402 | 120.4 | 14 |
| 71001 | defeat | 228.2 | 6 | 368 | 120.5 | 12 |
| 71002 | victory | 300.0 | 9 | 537 | 82.9 | 15 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 12 | 554 | 87.4 | 14 |
| 71001 | defeat | 241.4 | 9 | 391 | 120.7 | 14 |
| 71002 | defeat | 222.2 | 9 | 343 | 120.1 | 15 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 11 | 544 | 51.7 | 13 |
| 71001 | victory | 300.0 | 10 | 534 | 50.8 | 14 |
| 71002 | victory | 300.0 | 11 | 549 | 49.5 | 8 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 215.3 | 8 | 342 | 120.4 | 16 |
| 71001 | victory | 300.0 | 9 | 540 | 132.6 | 20 |
| 71002 | victory | 300.0 | 9 | 535 | 56.9 | 14 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 8 | 540 | 99.3 | 10 |
| 71001 | defeat | 223.1 | 8 | 343 | 127.2 | 15 |
| 71002 | victory | 300.0 | 9 | 549 | 107.9 | 16 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 221.0 | 5 | 356 | 121.0 | 16 |
| 71001 | defeat | 221.6 | 6 | 329 | 121.7 | 25 |
| 71002 | defeat | 225.4 | 7 | 342 | 120.9 | 23 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 6 | 539 | 115.7 | 15 |
| 71001 | victory | 300.0 | 6 | 534 | 56.7 | 15 |
| 71002 | defeat | 223.2 | 6 | 342 | 136.8 | 23 |

## Gate Notes

- Bots outside target and needing balance review: `kite`, `tank`, `zone-control`, `route`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
