# Harness Bot Matrix Summary

- Map: `caramel-workshop`
- Seeds: `62300`..`62304` per bot
- Duration target: `300` seconds
- Tick rate: `30`
- Bot count: `4`

## Bot Results

| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |
|---|---|---|---:|---:|---:|---:|---:|---:|
| greedy | repair | mid-skill rule bot 25%-55% | 0.0% | 0/5 | 225.4 | 9.6 | 347.0 | 21 |
| kite | repair | high-skill rule bot 45%-75% | 0.0% | 0/5 | 215.9 | 8.4 | 334.6 | 17 |
| boss-hunter | repair | high-skill rule bot 45%-75% | 0.0% | 0/5 | 214.9 | 6.6 | 326.8 | 16 |
| zone-control | repair | mid-skill rule bot 25%-55% | 0.0% | 0/5 | 225.8 | 6.6 | 346.6 | 16 |

## Runs

### greedy

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 62300 | defeat | 220.1 | 10 | 336 | 120.2 | 21 |
| 62301 | defeat | 232.4 | 10 | 364 | 120.5 | 17 |
| 62302 | defeat | 228.7 | 9 | 360 | 120.0 | 14 |
| 62303 | defeat | 227.8 | 10 | 350 | 120.7 | 14 |
| 62304 | defeat | 217.9 | 9 | 325 | 120.4 | 16 |

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 62300 | defeat | 216.0 | 9 | 340 | 120.1 | 13 |
| 62301 | defeat | 213.4 | 8 | 333 | 120.1 | 8 |
| 62302 | defeat | 217.4 | 8 | 328 | 121.1 | 13 |
| 62303 | defeat | 214.8 | 9 | 326 | 120.5 | 17 |
| 62304 | defeat | 217.7 | 8 | 346 | 121.0 | 15 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 62300 | defeat | 216.0 | 6 | 332 | 120.3 | 9 |
| 62301 | defeat | 213.2 | 8 | 332 | 120.4 | 16 |
| 62302 | defeat | 215.3 | 7 | 325 | 120.4 | 14 |
| 62303 | defeat | 215.0 | 6 | 321 | 121.5 | 15 |
| 62304 | defeat | 215.2 | 6 | 324 | 120.7 | 14 |

### zone-control

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 62300 | defeat | 223.5 | 7 | 355 | 120.3 | 15 |
| 62301 | defeat | 231.4 | 7 | 357 | 120.3 | 14 |
| 62302 | defeat | 219.9 | 6 | 330 | 120.5 | 16 |
| 62303 | defeat | 227.4 | 6 | 346 | 120.3 | 14 |
| 62304 | defeat | 227.1 | 7 | 345 | 136.8 | 13 |

## Gate Notes

- Bots outside target and needing balance review: `greedy`, `kite`, `boss-hunter`, `zone-control`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
