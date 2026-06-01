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
| random | pass | random robustness 0%-15% | 0.0% | 0/3 | 148.6 | 4.0 | 177.3 | 22 |
| coward | repair | low-skill rule bot 10%-35% | 0.0% | 0/3 | 206.0 | 6.7 | 312.3 | 37 |
| greedy | repair | mid-skill rule bot 25%-55% | 100.0% | 3/3 | 300.0 | 11.0 | 532.0 | 18 |
| kite | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 277.7 | 9.7 | 480.3 | 14 |
| tank | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 185.0 | 5.7 | 258.7 | 31 |
| boss-hunter | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 245.6 | 7.0 | 417.0 | 18 |
| zone-control | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 247.9 | 7.3 | 400.0 | 22 |
| route | repair | low-skill rule bot 10%-35% | 66.7% | 2/3 | 272.8 | 6.3 | 464.0 | 26 |

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
| 70002 | defeat | 222.8 | 7 | 339 | 120.0 | 20 |

### coward

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 121.1 | 3 | 101 | 120.0 | 37 |
| 70001 | defeat | 255.5 | 8 | 434 | 152.3 | 14 |
| 70002 | defeat | 241.4 | 9 | 402 | 120.1 | 10 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 11 | 533 | 93.7 | 18 |
| 70001 | victory | 300.0 | 11 | 539 | 97.8 | 11 |
| 70002 | victory | 300.0 | 11 | 524 | 49.9 | 12 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 11 | 529 | 107.1 | 13 |
| 70001 | victory | 300.0 | 10 | 542 | 50.2 | 10 |
| 70002 | defeat | 233.2 | 8 | 370 | 120.1 | 14 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 124.8 | 4 | 118 | 136.8 | 28 |
| 70001 | defeat | 130.2 | 4 | 132 | 120.0 | 31 |
| 70002 | victory | 300.0 | 9 | 526 | 104.9 | 13 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 8 | 543 | 106.0 | 14 |
| 70001 | defeat | 136.8 | 5 | 155 | 120.1 | 18 |
| 70002 | victory | 300.0 | 8 | 553 | 86.8 | 17 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 9 | 537 | 58.4 | 16 |
| 70001 | defeat | 220.5 | 6 | 328 | 120.8 | 22 |
| 70002 | defeat | 223.2 | 7 | 335 | 121.0 | 21 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 6 | 531 | 58.4 | 18 |
| 70001 | defeat | 218.5 | 6 | 335 | 120.2 | 26 |
| 70002 | victory | 300.0 | 7 | 526 | 113.9 | 17 |

## Gate Notes

- Bots outside target and needing balance review: `coward`, `greedy`, `route`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
