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
| random | pass | random robustness 0%-15% | 0.0% | 0/3 | 107.3 | 2.0 | 88.3 | 24 |
| coward | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 261.8 | 9.0 | 447.7 | 22 |
| greedy | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 279.5 | 11.0 | 487.0 | 14 |
| kite | repair | high-skill rule bot 45%-75% | 100.0% | 3/3 | 300.0 | 10.7 | 543.0 | 15 |
| tank | repair | mid-skill rule bot 25%-55% | 100.0% | 3/3 | 300.0 | 8.7 | 538.7 | 17 |
| boss-hunter | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 271.8 | 8.3 | 471.3 | 14 |
| zone-control | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 273.4 | 7.3 | 479.0 | 20 |
| route | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 216.3 | 5.0 | 335.7 | 35 |

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
| 71000 | defeat | 107.7 | 2 | 94 | 120.2 | 18 |
| 71001 | defeat | 107.6 | 2 | 86 | 120.0 | 24 |
| 71002 | defeat | 106.7 | 2 | 85 | 120.7 | 22 |

### coward

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 241.1 | 8 | 394 | 120.2 | 22 |
| 71001 | victory | 300.0 | 11 | 536 | 56.7 | 10 |
| 71002 | defeat | 244.3 | 8 | 413 | 136.1 | 15 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 12 | 543 | 63.7 | 14 |
| 71001 | defeat | 238.4 | 9 | 380 | 120.7 | 13 |
| 71002 | victory | 300.0 | 12 | 538 | 97.9 | 13 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 11 | 549 | 57.8 | 15 |
| 71001 | victory | 300.0 | 11 | 536 | 108.1 | 11 |
| 71002 | victory | 300.0 | 10 | 544 | 118.6 | 10 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 9 | 544 | 83.9 | 13 |
| 71001 | victory | 300.0 | 9 | 534 | 49.3 | 17 |
| 71002 | victory | 300.0 | 8 | 538 | 62.5 | 12 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 215.5 | 7 | 330 | 120.3 | 14 |
| 71001 | victory | 300.0 | 9 | 549 | 113.2 | 13 |
| 71002 | victory | 300.0 | 9 | 535 | 88.7 | 12 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 7 | 548 | 70.9 | 15 |
| 71001 | defeat | 220.1 | 7 | 331 | 120.1 | 20 |
| 71002 | victory | 300.0 | 8 | 558 | 103.5 | 14 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 218.3 | 5 | 338 | 120.0 | 16 |
| 71001 | victory | 300.0 | 6 | 534 | 112.9 | 25 |
| 71002 | defeat | 130.5 | 4 | 135 | 120.0 | 35 |

## Gate Notes

- Bots outside target and needing balance review: `greedy`, `kite`, `tank`, `zone-control`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
