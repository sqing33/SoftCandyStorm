# Harness Bot Matrix Summary

- Map: `frosting-grassland`
- Seeds: `70000`..`70002` per bot
- Duration target: `300` seconds
- Tick rate: `30`
- Bot count: `9`

## Bot Results

| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |
|---|---|---|---:|---:|---:|---:|---:|---:|
| idle | pass | idle pressure floor 0%-0% | 0.0% | 0/3 | 107.0 | 1.0 | 85.3 | 24 |
| random | repair | random robustness 0%-15% | 33.3% | 1/3 | 212.8 | 5.7 | 346.0 | 16 |
| coward | repair | low-skill rule bot 10%-35% | 0.0% | 0/3 | 191.2 | 6.3 | 276.3 | 45 |
| greedy | repair | mid-skill rule bot 25%-55% | 100.0% | 3/3 | 300.0 | 11.7 | 540.3 | 14 |
| kite | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 275.1 | 10.0 | 487.0 | 13 |
| tank | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 190.9 | 5.7 | 274.0 | 49 |
| boss-hunter | repair | high-skill rule bot 45%-75% | 0.0% | 0/3 | 203.1 | 5.7 | 310.3 | 20 |
| zone-control | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 275.0 | 8.3 | 482.0 | 18 |
| route | repair | low-skill rule bot 10%-35% | 66.7% | 2/3 | 274.5 | 7.0 | 487.0 | 27 |

## Runs

### idle

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 108.3 | 1 | 87 | 120.1 | 24 |
| 70001 | defeat | 106.2 | 1 | 85 | 120.1 | 22 |
| 70002 | defeat | 106.5 | 1 | 84 | 120.0 | 23 |

### random

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 222.3 | 6 | 363 | 121.3 | 16 |
| 70001 | defeat | 116.1 | 3 | 121 | 120.1 | 15 |
| 70002 | victory | 300.0 | 8 | 554 | 69.9 | 15 |

### coward

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 120.2 | 3 | 93 | 136.4 | 45 |
| 70001 | defeat | 224.1 | 8 | 360 | 152.6 | 17 |
| 70002 | defeat | 229.5 | 8 | 376 | 120.4 | 12 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 12 | 537 | 105.3 | 14 |
| 70001 | victory | 300.0 | 11 | 550 | 98.1 | 13 |
| 70002 | victory | 300.0 | 12 | 534 | 77.3 | 12 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 11 | 551 | 80.0 | 13 |
| 70001 | victory | 300.0 | 11 | 549 | 74.0 | 11 |
| 70002 | defeat | 225.2 | 8 | 361 | 120.5 | 12 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 133.2 | 4 | 127 | 136.1 | 39 |
| 70001 | defeat | 139.6 | 4 | 131 | 127.1 | 49 |
| 70002 | victory | 300.0 | 9 | 564 | 82.6 | 15 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 289.0 | 8 | 514 | 120.1 | 14 |
| 70001 | defeat | 106.8 | 3 | 88 | 120.3 | 20 |
| 70002 | defeat | 213.5 | 6 | 329 | 120.1 | 16 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 8 | 544 | 105.6 | 16 |
| 70001 | victory | 300.0 | 9 | 546 | 97.3 | 17 |
| 70002 | defeat | 225.1 | 8 | 356 | 136.1 | 18 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 7 | 551 | 110.8 | 20 |
| 70001 | defeat | 223.5 | 7 | 356 | 136.4 | 27 |
| 70002 | victory | 300.0 | 7 | 554 | 103.3 | 18 |

## Gate Notes

- Bots outside target and needing balance review: `random`, `coward`, `greedy`, `boss-hunter`, `zone-control`, `route`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
