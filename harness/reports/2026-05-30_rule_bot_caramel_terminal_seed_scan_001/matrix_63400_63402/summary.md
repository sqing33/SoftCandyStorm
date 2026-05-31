# Harness Bot Matrix Summary

- Map: `caramel-workshop`
- Seeds: `63400`..`63402` per bot
- Duration target: `300` seconds
- Tick rate: `30`
- Bot count: `9`

## Bot Results

| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |
|---|---|---|---:|---:|---:|---:|---:|---:|
| idle | pass | idle pressure floor 0%-0% | 0.0% | 0/3 | 116.3 | 3.0 | 108.3 | 22 |
| random | pass | random robustness 0%-15% | 0.0% | 0/3 | 222.1 | 5.0 | 340.3 | 14 |
| coward | repair | low-skill rule bot 10%-35% | 0.0% | 0/3 | 199.1 | 7.7 | 298.3 | 32 |
| greedy | repair | mid-skill rule bot 25%-55% | 0.0% | 0/3 | 191.2 | 8.3 | 270.3 | 19 |
| kite | repair | high-skill rule bot 45%-75% | 0.0% | 0/3 | 222.1 | 9.3 | 340.3 | 23 |
| tank | repair | mid-skill rule bot 25%-55% | 0.0% | 0/3 | 224.7 | 7.7 | 348.0 | 19 |
| boss-hunter | repair | high-skill rule bot 45%-75% | 0.0% | 0/3 | 215.2 | 6.0 | 326.0 | 16 |
| zone-control | repair | mid-skill rule bot 25%-55% | 0.0% | 0/3 | 225.0 | 6.7 | 347.7 | 16 |
| route | repair | low-skill rule bot 10%-35% | 0.0% | 0/3 | 149.9 | 4.0 | 172.7 | 34 |

## Runs

### idle

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 63400 | defeat | 118.3 | 3 | 115 | 120.0 | 21 |
| 63401 | defeat | 114.8 | 3 | 103 | 120.5 | 22 |
| 63402 | defeat | 115.7 | 3 | 107 | 120.0 | 21 |

### random

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 63400 | defeat | 223.3 | 5 | 344 | 120.6 | 12 |
| 63401 | defeat | 218.2 | 5 | 333 | 136.2 | 12 |
| 63402 | defeat | 224.9 | 5 | 344 | 121.0 | 14 |

### coward

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 63400 | defeat | 232.6 | 10 | 381 | 136.3 | 17 |
| 63401 | defeat | 230.9 | 8 | 370 | 120.3 | 13 |
| 63402 | defeat | 134.0 | 5 | 144 | 120.8 | 32 |

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 63400 | defeat | 122.7 | 6 | 122 | 120.1 | 19 |
| 63401 | defeat | 233.0 | 10 | 360 | 120.1 | 13 |
| 63402 | defeat | 217.9 | 9 | 329 | 120.3 | 15 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 63400 | defeat | 217.9 | 9 | 325 | 120.1 | 23 |
| 63401 | defeat | 231.4 | 10 | 359 | 120.4 | 17 |
| 63402 | defeat | 216.9 | 9 | 337 | 120.2 | 17 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 63400 | defeat | 231.2 | 9 | 361 | 152.3 | 19 |
| 63401 | defeat | 221.9 | 6 | 341 | 120.4 | 11 |
| 63402 | defeat | 221.1 | 8 | 342 | 120.4 | 19 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 63400 | defeat | 215.4 | 5 | 323 | 121.0 | 14 |
| 63401 | defeat | 215.6 | 7 | 329 | 120.5 | 16 |
| 63402 | defeat | 214.6 | 6 | 326 | 121.9 | 8 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 63400 | defeat | 223.3 | 7 | 338 | 120.5 | 16 |
| 63401 | defeat | 229.9 | 7 | 355 | 137.8 | 15 |
| 63402 | defeat | 221.8 | 6 | 350 | 120.2 | 11 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 63400 | defeat | 223.5 | 5 | 341 | 121.3 | 19 |
| 63401 | defeat | 126.2 | 3 | 114 | 120.0 | 34 |
| 63402 | defeat | 100.2 | 4 | 63 | 120.1 | 30 |

## Gate Notes

- Bots outside target and needing balance review: `coward`, `greedy`, `kite`, `tank`, `boss-hunter`, `zone-control`, `route`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` was omitted from this committed diagnostic pack to keep the terminal seed scan report compact; `metrics.json` and the filtered terminal trajectory JSONL files are the retained evidence.
