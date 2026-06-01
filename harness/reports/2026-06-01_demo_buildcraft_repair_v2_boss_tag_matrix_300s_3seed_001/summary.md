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
| random | pass | random robustness 0%-15% | 0.0% | 0/3 | 183.8 | 4.7 | 253.7 | 22 |
| coward | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 219.3 | 7.0 | 330.3 | 37 |
| greedy | repair | mid-skill rule bot 25%-55% | 100.0% | 3/3 | 300.0 | 11.3 | 522.0 | 13 |
| kite | repair | high-skill rule bot 45%-75% | 100.0% | 3/3 | 300.0 | 10.0 | 521.3 | 15 |
| tank | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 243.9 | 7.3 | 393.3 | 30 |
| boss-hunter | repair | high-skill rule bot 45%-75% | 0.0% | 0/3 | 154.0 | 4.7 | 197.0 | 21 |
| zone-control | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 273.2 | 7.0 | 452.0 | 17 |
| route | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 242.8 | 6.3 | 392.7 | 55 |

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
| 70000 | defeat | 222.1 | 5 | 337 | 120.2 | 17 |
| 70001 | defeat | 106.0 | 2 | 84 | 121.0 | 22 |
| 70002 | defeat | 223.4 | 7 | 340 | 122.4 | 18 |

### coward

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 121.1 | 3 | 101 | 120.2 | 37 |
| 70001 | victory | 300.0 | 11 | 515 | 74.0 | 10 |
| 70002 | defeat | 236.9 | 7 | 375 | 120.3 | 16 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 11 | 524 | 49.9 | 13 |
| 70001 | victory | 300.0 | 11 | 524 | 100.5 | 10 |
| 70002 | victory | 300.0 | 12 | 518 | 53.8 | 10 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 10 | 521 | 49.3 | 8 |
| 70001 | victory | 300.0 | 10 | 519 | 49.5 | 15 |
| 70002 | victory | 300.0 | 10 | 524 | 49.3 | 10 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 9 | 522 | 119.1 | 19 |
| 70001 | defeat | 131.7 | 4 | 138 | 120.2 | 30 |
| 70002 | victory | 300.0 | 9 | 520 | 49.3 | 14 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 214.7 | 6 | 341 | 120.3 | 12 |
| 70001 | defeat | 136.8 | 5 | 155 | 120.1 | 18 |
| 70002 | defeat | 110.6 | 3 | 95 | 120.5 | 21 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 8 | 513 | 74.2 | 16 |
| 70001 | victory | 300.0 | 7 | 511 | 62.9 | 17 |
| 70002 | defeat | 219.6 | 6 | 332 | 120.3 | 16 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 210.5 | 7 | 310 | 120.2 | 55 |
| 70001 | defeat | 218.0 | 6 | 343 | 127.3 | 28 |
| 70002 | victory | 300.0 | 6 | 525 | 89.0 | 17 |

## Gate Notes

- Bots outside target and needing balance review: `greedy`, `kite`, `tank`, `boss-hunter`, `zone-control`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
