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
| random | pass | random robustness 0%-15% | 0.0% | 0/3 | 148.7 | 4.0 | 177.3 | 22 |
| coward | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 218.7 | 7.0 | 342.0 | 37 |
| greedy | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 275.3 | 10.3 | 474.7 | 15 |
| kite | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 280.5 | 10.0 | 487.7 | 13 |
| tank | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 185.0 | 5.7 | 261.0 | 31 |
| boss-hunter | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 244.1 | 7.3 | 419.7 | 18 |
| zone-control | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 248.5 | 7.0 | 404.7 | 23 |
| route | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 248.0 | 5.7 | 410.0 | 26 |

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
| 70002 | defeat | 223.1 | 7 | 339 | 120.5 | 19 |

### coward

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 121.1 | 3 | 101 | 120.0 | 37 |
| 70001 | defeat | 235.1 | 7 | 380 | 152.5 | 15 |
| 70002 | victory | 300.0 | 11 | 545 | 110.7 | 10 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 225.9 | 8 | 351 | 120.7 | 15 |
| 70001 | victory | 300.0 | 11 | 527 | 112.6 | 12 |
| 70002 | victory | 300.0 | 12 | 546 | 98.9 | 15 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 11 | 534 | 106.0 | 13 |
| 70001 | victory | 300.0 | 10 | 526 | 49.3 | 10 |
| 70002 | defeat | 241.4 | 9 | 403 | 120.7 | 11 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 124.8 | 4 | 118 | 136.8 | 28 |
| 70001 | defeat | 130.2 | 4 | 132 | 120.0 | 31 |
| 70002 | victory | 300.0 | 9 | 533 | 105.1 | 13 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 9 | 551 | 92.7 | 14 |
| 70001 | defeat | 132.3 | 5 | 146 | 126.0 | 18 |
| 70002 | victory | 300.0 | 8 | 562 | 87.4 | 17 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 9 | 541 | 80.4 | 16 |
| 70001 | defeat | 223.0 | 6 | 338 | 120.9 | 20 |
| 70002 | defeat | 222.6 | 6 | 335 | 120.1 | 23 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 6 | 548 | 101.7 | 18 |
| 70001 | defeat | 218.5 | 6 | 334 | 120.2 | 26 |
| 70002 | defeat | 225.5 | 5 | 348 | 120.7 | 17 |

## Gate Notes

- Bots outside target and needing balance review: `greedy`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
