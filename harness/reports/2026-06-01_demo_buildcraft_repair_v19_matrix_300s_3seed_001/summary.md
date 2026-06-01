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
| coward | repair | low-skill rule bot 10%-35% | 0.0% | 0/3 | 200.6 | 6.7 | 298.3 | 37 |
| greedy | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 275.3 | 10.7 | 477.7 | 16 |
| kite | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 280.5 | 10.3 | 491.7 | 15 |
| tank | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 185.0 | 5.7 | 260.3 | 31 |
| boss-hunter | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 244.1 | 7.3 | 412.7 | 18 |
| zone-control | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 248.9 | 7.3 | 409.3 | 22 |
| route | repair | low-skill rule bot 10%-35% | 66.7% | 2/3 | 272.8 | 6.3 | 476.3 | 26 |

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
| 70001 | defeat | 249.0 | 8 | 418 | 152.4 | 14 |
| 70002 | defeat | 231.9 | 9 | 376 | 120.7 | 10 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 226.0 | 8 | 350 | 120.6 | 14 |
| 70001 | victory | 300.0 | 11 | 534 | 74.9 | 11 |
| 70002 | victory | 300.0 | 13 | 549 | 96.1 | 16 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 11 | 530 | 95.3 | 13 |
| 70001 | victory | 300.0 | 11 | 539 | 50.2 | 10 |
| 70002 | defeat | 241.4 | 9 | 406 | 120.7 | 15 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 124.8 | 4 | 118 | 136.8 | 28 |
| 70001 | defeat | 130.2 | 4 | 132 | 120.0 | 31 |
| 70002 | victory | 300.0 | 9 | 531 | 97.3 | 13 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 9 | 539 | 92.7 | 14 |
| 70001 | defeat | 132.3 | 5 | 146 | 126.0 | 18 |
| 70002 | victory | 300.0 | 8 | 553 | 86.8 | 17 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 9 | 549 | 80.4 | 16 |
| 70001 | defeat | 223.2 | 6 | 339 | 120.5 | 19 |
| 70002 | defeat | 223.4 | 7 | 340 | 120.9 | 22 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 6 | 542 | 59.0 | 18 |
| 70001 | defeat | 218.5 | 6 | 334 | 120.2 | 26 |
| 70002 | victory | 300.0 | 7 | 553 | 115.9 | 17 |

## Gate Notes

- Bots outside target and needing balance review: `coward`, `greedy`, `route`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
