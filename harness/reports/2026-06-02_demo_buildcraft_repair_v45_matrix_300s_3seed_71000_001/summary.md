# Harness Bot Matrix Summary

- Map: `frosting-grassland`
- Seeds: `71000`..`71002` per bot
- Duration target: `300` seconds
- Tick rate: `30`
- Bot count: `9`

## Bot Results

| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |
|---|---|---|---:|---:|---:|---:|---:|---:|
| idle | pass | idle pressure floor 0%-0% | 0.0% | 0/3 | 107.1 | 1.0 | 85.7 | 24 |
| random | pass | random robustness 0%-15% | 0.0% | 0/3 | 107.1 | 2.0 | 86.0 | 24 |
| coward | repair | low-skill rule bot 10%-35% | 66.7% | 2/3 | 278.6 | 9.3 | 491.3 | 17 |
| greedy | repair | mid-skill rule bot 25%-55% | 66.7% | 2/3 | 255.2 | 10.3 | 418.0 | 55 |
| kite | repair | high-skill rule bot 45%-75% | 100.0% | 3/3 | 300.0 | 10.7 | 535.3 | 19 |
| tank | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 227.5 | 7.0 | 362.7 | 42 |
| boss-hunter | repair | high-skill rule bot 45%-75% | 33.3% | 1/3 | 254.4 | 8.3 | 424.0 | 18 |
| zone-control | repair | mid-skill rule bot 25%-55% | 0.0% | 0/3 | 221.3 | 6.3 | 337.3 | 23 |
| route | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 246.6 | 6.7 | 406.0 | 29 |

## Runs

### idle

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 106.0 | 1 | 84 | 120.7 | 21 |
| 71001 | defeat | 106.7 | 1 | 86 | 121.1 | 21 |
| 71002 | defeat | 108.6 | 1 | 87 | 120.4 | 24 |

### random

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 104.8 | 2 | 83 | 120.7 | 20 |
| 71001 | defeat | 107.4 | 2 | 87 | 121.1 | 22 |
| 71002 | defeat | 109.1 | 2 | 88 | 120.5 | 24 |

### coward

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 10 | 556 | 61.5 | 17 |
| 71001 | victory | 300.0 | 10 | 534 | 115.4 | 15 |
| 71002 | defeat | 235.8 | 8 | 384 | 120.0 | 12 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 12 | 541 | 79.5 | 17 |
| 71001 | victory | 300.0 | 12 | 541 | 77.2 | 19 |
| 71002 | defeat | 165.6 | 7 | 172 | 120.6 | 55 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | victory | 300.0 | 11 | 537 | 111.2 | 19 |
| 71001 | victory | 300.0 | 10 | 536 | 49.3 | 10 |
| 71002 | victory | 300.0 | 11 | 533 | 64.3 | 11 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 215.4 | 7 | 326 | 120.4 | 19 |
| 71001 | victory | 300.0 | 9 | 539 | 90.2 | 18 |
| 71002 | defeat | 167.2 | 5 | 223 | 142.2 | 42 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 234.1 | 8 | 379 | 120.4 | 18 |
| 71001 | victory | 300.0 | 9 | 533 | 67.0 | 12 |
| 71002 | defeat | 229.1 | 8 | 360 | 120.0 | 16 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 222.8 | 7 | 340 | 127.3 | 23 |
| 71001 | defeat | 222.7 | 6 | 344 | 120.6 | 16 |
| 71002 | defeat | 218.6 | 6 | 328 | 121.1 | 18 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 71000 | defeat | 221.9 | 6 | 346 | 120.4 | 16 |
| 71001 | victory | 300.0 | 7 | 537 | 93.2 | 24 |
| 71002 | defeat | 218.1 | 7 | 335 | 133.4 | 29 |

## Gate Notes

- Bots outside target and needing balance review: `coward`, `greedy`, `kite`, `boss-hunter`, `zone-control`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
