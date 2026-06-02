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
| coward | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 253.1 | 9.0 | 426.7 | 18 |
| greedy | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 250.3 | 10.0 | 418.7 | 39 |
| kite | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 275.4 | 10.3 | 479.7 | 20 |
| tank | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 270.1 | 8.3 | 476.7 | 22 |
| boss-hunter | repair | high-skill rule bot 45%-75% | 33.3% | 1/3 | 255.7 | 8.0 | 426.0 | 17 |
| zone-control | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 275.4 | 7.3 | 487.0 | 24 |
| route | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 246.4 | 6.0 | 408.3 | 25 |

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
| 71000 | defeat | 240.9 | 8 | 400 | 120.1 | 18 |
| 71001 | victory | 300.0 | 11 | 541 | 51.3 | 12 |
| 71002 | defeat | 218.4 | 8 | 339 | 120.1 | 8 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 12 | 547 | 97.9 | 16 |
| 71001 | victory | 300.0 | 11 | 535 | 74.0 | 13 |
| 71002 | defeat | 150.9 | 7 | 174 | 120.1 | 39 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 226.1 | 9 | 354 | 121.3 | 20 |
| 71001 | victory | 300.0 | 11 | 545 | 101.3 | 15 |
| 71002 | victory | 300.0 | 11 | 540 | 74.3 | 12 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 9 | 547 | 50.6 | 11 |
| 71001 | victory | 300.0 | 9 | 536 | 46.9 | 15 |
| 71002 | defeat | 210.3 | 7 | 347 | 139.5 | 22 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 215.4 | 7 | 325 | 120.7 | 17 |
| 71001 | defeat | 251.5 | 8 | 412 | 120.2 | 13 |
| 71002 | victory | 300.0 | 9 | 541 | 87.1 | 12 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 7 | 553 | 67.8 | 17 |
| 71001 | victory | 300.0 | 8 | 565 | 66.4 | 15 |
| 71002 | defeat | 226.2 | 7 | 343 | 127.1 | 24 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 219.0 | 6 | 338 | 120.0 | 17 |
| 71001 | defeat | 220.1 | 5 | 335 | 120.9 | 21 |
| 71002 | victory | 300.0 | 7 | 552 | 103.2 | 25 |

## Gate Notes

- Bots outside target and needing balance review: `greedy`, `tank`, `boss-hunter`, `zone-control`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
