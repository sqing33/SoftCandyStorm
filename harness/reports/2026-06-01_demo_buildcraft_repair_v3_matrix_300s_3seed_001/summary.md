# Harness Bot Matrix Summary

- Map: `frosting-grassland`
- Seeds: `70000`..`70002` per bot
- Duration target: `300` seconds
- Tick rate: `30`
- Bot count: `9`

## Bot Results

| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |
|---|---|---|---:|---:|---:|---:|---:|---:|
| idle | pass | idle pressure floor 0%-0% | 0.0% | 0/3 | 103.3 | 2.0 | 78.7 | 21 |
| random | pass | random robustness 0%-15% | 0.0% | 0/3 | 182.9 | 6.0 | 249.7 | 22 |
| coward | repair | low-skill rule bot 10%-35% | 0.0% | 0/3 | 109.6 | 3.0 | 96.7 | 28 |
| greedy | repair | mid-skill rule bot 25%-55% | 0.0% | 0/3 | 208.7 | 7.7 | 290.3 | 27 |
| kite | repair | high-skill rule bot 45%-75% | 100.0% | 3/3 | 300.0 | 10.3 | 533.3 | 12 |
| tank | repair | mid-skill rule bot 25%-55% | 0.0% | 0/3 | 143.1 | 4.0 | 143.7 | 43 |
| boss-hunter | repair | high-skill rule bot 45%-75% | 33.3% | 1/3 | 243.3 | 7.0 | 383.3 | 16 |
| zone-control | repair | mid-skill rule bot 25%-55% | 0.0% | 0/3 | 119.9 | 3.7 | 110.3 | 23 |
| route | repair | low-skill rule bot 10%-35% | 0.0% | 0/3 | 160.5 | 4.7 | 170.3 | 50 |

## Runs

### idle

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 104.8 | 2 | 80 | 120.2 | 21 |
| 70001 | defeat | 102.7 | 2 | 78 | 136.1 | 19 |
| 70002 | defeat | 102.5 | 2 | 78 | 120.2 | 19 |

### random

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 105.7 | 3 | 81 | 120.4 | 22 |
| 70001 | defeat | 222.1 | 8 | 333 | 121.0 | 21 |
| 70002 | defeat | 220.9 | 7 | 335 | 120.7 | 13 |

### coward

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 125.0 | 3 | 117 | 120.4 | 28 |
| 70001 | defeat | 78.3 | 2 | 58 | 120.0 | 6 |
| 70002 | defeat | 125.4 | 4 | 115 | 120.2 | 27 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 230.3 | 8 | 337 | 120.1 | 27 |
| 70001 | defeat | 170.2 | 7 | 207 | 120.4 | 25 |
| 70002 | defeat | 225.7 | 8 | 327 | 120.7 | 22 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | victory | 300.0 | 11 | 536 | 90.2 | 12 |
| 70001 | victory | 300.0 | 10 | 536 | 97.3 | 8 |
| 70002 | victory | 300.0 | 10 | 528 | 108.3 | 8 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 155.2 | 4 | 178 | 120.1 | 28 |
| 70001 | defeat | 124.9 | 4 | 98 | 136.0 | 43 |
| 70002 | defeat | 149.0 | 4 | 155 | 120.3 | 32 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 214.5 | 7 | 305 | 120.7 | 16 |
| 70001 | victory | 300.0 | 8 | 534 | 55.5 | 15 |
| 70002 | defeat | 215.4 | 6 | 311 | 120.5 | 13 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 114.0 | 3 | 100 | 120.1 | 20 |
| 70001 | defeat | 128.1 | 4 | 124 | 120.1 | 23 |
| 70002 | defeat | 117.6 | 4 | 107 | 120.1 | 20 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 70000 | defeat | 223.1 | 6 | 319 | 120.3 | 24 |
| 70001 | defeat | 128.0 | 4 | 88 | 120.0 | 50 |
| 70002 | defeat | 130.6 | 4 | 104 | 120.2 | 47 |

## Gate Notes

- Bots outside target and needing balance review: `coward`, `greedy`, `kite`, `tank`, `boss-hunter`, `zone-control`, `route`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
