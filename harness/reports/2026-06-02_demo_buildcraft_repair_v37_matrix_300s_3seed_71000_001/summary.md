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
| coward | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 254.9 | 9.0 | 430.3 | 17 |
| greedy | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 250.9 | 10.0 | 414.3 | 39 |
| kite | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 273.0 | 10.0 | 481.3 | 17 |
| tank | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 244.7 | 7.7 | 400.7 | 22 |
| boss-hunter | repair | high-skill rule bot 45%-75% | 100.0% | 3/3 | 300.0 | 8.7 | 538.7 | 14 |
| zone-control | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 249.3 | 7.0 | 415.3 | 22 |
| route | repair | low-skill rule bot 10%-35% | 66.7% | 2/3 | 273.0 | 6.0 | 470.3 | 25 |

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
| 71000 | victory | 300.0 | 11 | 550 | 82.5 | 14 |
| 71001 | defeat | 236.1 | 8 | 384 | 120.7 | 11 |
| 71002 | defeat | 228.7 | 8 | 357 | 120.5 | 17 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 12 | 541 | 63.5 | 15 |
| 71001 | defeat | 234.6 | 9 | 370 | 120.7 | 13 |
| 71002 | defeat | 218.0 | 9 | 332 | 120.2 | 39 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 219.0 | 9 | 351 | 120.3 | 17 |
| 71001 | victory | 300.0 | 11 | 545 | 100.5 | 11 |
| 71002 | victory | 300.0 | 10 | 548 | 50.3 | 11 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 9 | 533 | 119.9 | 19 |
| 71001 | defeat | 223.5 | 7 | 348 | 120.8 | 16 |
| 71002 | defeat | 210.6 | 7 | 321 | 143.5 | 22 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 9 | 545 | 77.4 | 14 |
| 71001 | victory | 300.0 | 8 | 524 | 62.7 | 13 |
| 71002 | victory | 300.0 | 9 | 547 | 52.1 | 10 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 8 | 534 | 119.5 | 15 |
| 71001 | defeat | 218.8 | 7 | 327 | 121.2 | 22 |
| 71002 | defeat | 229.0 | 6 | 385 | 120.3 | 14 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 6 | 541 | 112.7 | 16 |
| 71001 | victory | 300.0 | 6 | 536 | 91.6 | 21 |
| 71002 | defeat | 219.1 | 6 | 334 | 127.1 | 25 |

## Gate Notes

- Bots outside target and needing balance review: `boss-hunter`, `route`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
