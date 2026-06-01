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
| random | pass | random robustness 0%-15% | 0.0% | 0/3 | 148.9 | 4.0 | 178.7 | 22 |
| coward | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 222.5 | 7.0 | 341.0 | 37 |
| greedy | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 275.7 | 10.7 | 469.0 | 13 |
| kite | repair | high-skill rule bot 45%-75% | 100.0% | 3/3 | 300.0 | 11.0 | 535.7 | 10 |
| tank | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 185.0 | 5.7 | 262.7 | 31 |
| boss-hunter | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 245.6 | 7.0 | 418.0 | 18 |
| zone-control | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 248.4 | 6.7 | 401.7 | 22 |
| route | repair | low-skill rule bot 10%-35% | 0.0% | 0/3 | 214.8 | 6.3 | 297.0 | 55 |

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
| 70002 | defeat | 223.7 | 7 | 343 | 120.9 | 16 |

### coward

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 121.1 | 3 | 101 | 120.0 | 37 |
| 70001 | defeat | 246.3 | 7 | 402 | 152.0 | 21 |
| 70002 | victory | 300.0 | 11 | 520 | 76.8 | 10 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 227.0 | 9 | 355 | 120.5 | 12 |
| 70001 | victory | 300.0 | 11 | 524 | 108.2 | 11 |
| 70002 | victory | 300.0 | 12 | 528 | 60.7 | 13 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 11 | 543 | 49.3 | 8 |
| 70001 | victory | 300.0 | 11 | 528 | 85.6 | 9 |
| 70002 | victory | 300.0 | 11 | 536 | 50.5 | 10 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 124.8 | 4 | 118 | 136.8 | 28 |
| 70001 | defeat | 130.2 | 4 | 132 | 120.0 | 31 |
| 70002 | victory | 300.0 | 9 | 538 | 97.3 | 13 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 8 | 544 | 106.0 | 14 |
| 70001 | defeat | 136.8 | 5 | 155 | 120.1 | 18 |
| 70002 | victory | 300.0 | 8 | 555 | 87.4 | 17 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 8 | 535 | 58.4 | 16 |
| 70001 | defeat | 223.2 | 6 | 336 | 120.2 | 22 |
| 70002 | defeat | 222.1 | 6 | 334 | 120.8 | 22 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 206.9 | 7 | 228 | 143.1 | 55 |
| 70001 | defeat | 218.7 | 7 | 333 | 136.3 | 34 |
| 70002 | defeat | 218.8 | 5 | 330 | 120.7 | 17 |

## Gate Notes

- Bots outside target and needing balance review: `greedy`, `kite`, `route`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
