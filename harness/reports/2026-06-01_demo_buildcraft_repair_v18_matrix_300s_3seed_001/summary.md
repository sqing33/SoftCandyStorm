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
| coward | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 218.7 | 7.3 | 341.3 | 37 |
| greedy | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 250.2 | 9.3 | 410.0 | 15 |
| kite | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 280.5 | 10.3 | 489.7 | 12 |
| tank | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 185.0 | 5.7 | 261.7 | 31 |
| boss-hunter | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 244.1 | 7.3 | 421.0 | 18 |
| zone-control | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 248.6 | 7.0 | 404.0 | 22 |
| route | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 248.0 | 5.7 | 410.7 | 26 |

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
| 70001 | defeat | 235.1 | 7 | 380 | 152.5 | 15 |
| 70002 | victory | 300.0 | 12 | 543 | 103.3 | 10 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 225.9 | 8 | 351 | 120.7 | 15 |
| 70001 | victory | 300.0 | 11 | 528 | 112.6 | 12 |
| 70002 | defeat | 224.9 | 9 | 351 | 121.0 | 15 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 11 | 533 | 91.3 | 12 |
| 70001 | victory | 300.0 | 11 | 529 | 49.3 | 10 |
| 70002 | defeat | 241.4 | 9 | 407 | 120.7 | 12 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 124.8 | 4 | 118 | 136.8 | 28 |
| 70001 | defeat | 130.2 | 4 | 132 | 120.0 | 31 |
| 70002 | victory | 300.0 | 9 | 535 | 104.9 | 13 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 9 | 551 | 92.7 | 14 |
| 70001 | defeat | 132.3 | 5 | 146 | 126.0 | 18 |
| 70002 | victory | 300.0 | 8 | 566 | 87.6 | 17 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 9 | 536 | 80.4 | 16 |
| 70001 | defeat | 223.0 | 6 | 338 | 120.9 | 20 |
| 70002 | defeat | 222.9 | 6 | 338 | 120.9 | 22 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 6 | 546 | 101.7 | 18 |
| 70001 | defeat | 218.5 | 6 | 334 | 120.2 | 26 |
| 70002 | defeat | 225.4 | 5 | 352 | 120.3 | 17 |

## Gate Notes

- All matrix bots are inside their initial prototype win-rate target ranges.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
