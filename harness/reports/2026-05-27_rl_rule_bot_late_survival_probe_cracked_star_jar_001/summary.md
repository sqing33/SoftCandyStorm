# Harness Bot Matrix Summary

- Map: `cracked-star-jar`
- Seeds: `62300`..`62304` per bot
- Duration target: `300` seconds
- Tick rate: `30`
- Bot count: `4`

## Bot Results

| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |
|---|---|---|---:|---:|---:|---:|---:|---:|
| greedy | repair | mid-skill rule bot 25%-55% | 0.0% | 0/5 | 231.7 | 11.4 | 485.8 | 34 |
| kite | repair | high-skill rule bot 45%-75% | 40.0% | 2/5 | 256.0 | 10.6 | 570.4 | 24 |
| boss-hunter | repair | high-skill rule bot 45%-75% | 0.0% | 0/5 | 218.5 | 7.2 | 454.8 | 25 |
| zone-control | repair | mid-skill rule bot 25%-55% | 0.0% | 0/5 | 209.1 | 7.4 | 417.0 | 26 |

## Runs

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 62300 | defeat | 234.9 | 12 | 501 | 120.4 | 22 |
| 62301 | defeat | 223.4 | 11 | 463 | 120.6 | 34 |
| 62302 | defeat | 254.6 | 12 | 558 | 121.1 | 22 |
| 62303 | defeat | 222.1 | 11 | 438 | 120.1 | 31 |
| 62304 | defeat | 223.4 | 11 | 469 | 121.5 | 33 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 62300 | defeat | 227.1 | 9 | 506 | 121.2 | 21 |
| 62301 | defeat | 221.6 | 9 | 492 | 120.4 | 24 |
| 62302 | victory | 300.0 | 13 | 662 | 96.1 | 20 |
| 62303 | victory | 300.0 | 13 | 679 | 80.0 | 19 |
| 62304 | defeat | 231.4 | 9 | 513 | 120.4 | 22 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 62300 | defeat | 218.4 | 7 | 452 | 120.5 | 25 |
| 62301 | defeat | 217.8 | 8 | 471 | 120.2 | 20 |
| 62302 | defeat | 217.6 | 7 | 439 | 121.0 | 20 |
| 62303 | defeat | 218.9 | 6 | 452 | 120.9 | 24 |
| 62304 | defeat | 219.6 | 8 | 460 | 120.7 | 25 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 62300 | defeat | 131.2 | 5 | 216 | 120.1 | 20 |
| 62301 | defeat | 236.3 | 8 | 495 | 120.4 | 17 |
| 62302 | defeat | 224.9 | 8 | 425 | 120.6 | 26 |
| 62303 | defeat | 225.8 | 7 | 486 | 120.8 | 24 |
| 62304 | defeat | 227.3 | 9 | 463 | 120.6 | 25 |

## Gate Notes

- Bots outside target and needing balance review: `greedy`, `kite`, `boss-hunter`, `zone-control`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
