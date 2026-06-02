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
| coward | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 249.9 | 8.7 | 422.0 | 14 |
| greedy | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 249.1 | 10.0 | 408.3 | 39 |
| kite | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 273.1 | 10.3 | 479.7 | 17 |
| tank | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 245.8 | 7.7 | 404.3 | 22 |
| boss-hunter | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 272.2 | 8.7 | 469.0 | 14 |
| zone-control | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 245.9 | 6.7 | 407.3 | 21 |
| route | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 246.7 | 6.0 | 403.7 | 25 |

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
| 71000 | defeat | 220.0 | 8 | 350 | 120.6 | 14 |
| 71001 | victory | 300.0 | 10 | 546 | 49.3 | 11 |
| 71002 | defeat | 229.7 | 8 | 370 | 120.3 | 12 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 12 | 533 | 56.5 | 15 |
| 71001 | defeat | 229.6 | 9 | 360 | 121.3 | 14 |
| 71002 | defeat | 217.8 | 9 | 332 | 121.0 | 39 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 219.3 | 9 | 354 | 120.3 | 17 |
| 71001 | victory | 300.0 | 11 | 544 | 99.5 | 12 |
| 71002 | victory | 300.0 | 11 | 541 | 49.9 | 11 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 226.8 | 7 | 353 | 120.1 | 20 |
| 71001 | victory | 300.0 | 9 | 539 | 94.8 | 15 |
| 71002 | defeat | 210.6 | 7 | 321 | 143.5 | 22 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 216.5 | 8 | 330 | 120.1 | 14 |
| 71001 | victory | 300.0 | 9 | 542 | 75.9 | 13 |
| 71002 | victory | 300.0 | 9 | 535 | 83.0 | 13 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 218.6 | 5 | 342 | 126.4 | 15 |
| 71001 | defeat | 219.0 | 7 | 328 | 121.5 | 21 |
| 71002 | victory | 300.0 | 8 | 552 | 112.7 | 14 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 6 | 539 | 103.8 | 16 |
| 71001 | defeat | 221.0 | 6 | 339 | 120.5 | 21 |
| 71002 | defeat | 219.1 | 6 | 333 | 127.1 | 25 |

## Gate Notes

- All matrix bots are inside their initial prototype win-rate target ranges.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
