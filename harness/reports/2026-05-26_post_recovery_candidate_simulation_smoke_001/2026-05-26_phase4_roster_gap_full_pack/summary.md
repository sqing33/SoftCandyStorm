# Harness Bot Matrix Summary

- Map: `frosting-grassland`
- Seeds: `31000`..`31002` per bot
- Duration target: `180` seconds
- Tick rate: `30`
- Bot count: `4`

## Bot Results

| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |
|---|---|---|---:|---:|---:|---:|---:|---:|
| random | repair | random robustness 0%-15% | 33.3% | 1/3 | 132.1 | 2.7 | 144.7 | 22 |
| coward | repair | low-skill rule bot 10%-35% | 100.0% | 3/3 | 180.0 | 6.0 | 256.3 | 10 |
| tank | repair | mid-skill rule bot 25%-55% | 100.0% | 3/3 | 180.0 | 7.0 | 258.0 | 12 |
| boss-hunter | repair | high-skill rule bot 45%-75% | 100.0% | 3/3 | 180.0 | 7.0 | 257.3 | 11 |

## Runs

### random

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 31000 | victory | 180.0 | 5 | 256 | 98.9 | 17 |
| 31001 | defeat | 108.1 | 2 | 90 | 120.8 | 20 |
| 31002 | defeat | 108.2 | 1 | 88 | 121.0 | 22 |

### coward

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 31000 | victory | 180.0 | 6 | 258 | 0.0 | 7 |
| 31001 | victory | 180.0 | 6 | 256 | 9.7 | 10 |
| 31002 | victory | 180.0 | 6 | 255 | 1.6 | 10 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 31000 | victory | 180.0 | 7 | 260 | 0.0 | 10 |
| 31001 | victory | 180.0 | 7 | 254 | 0.0 | 10 |
| 31002 | victory | 180.0 | 7 | 260 | 0.0 | 12 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 31000 | victory | 180.0 | 7 | 258 | 0.0 | 8 |
| 31001 | victory | 180.0 | 7 | 259 | 0.0 | 9 |
| 31002 | victory | 180.0 | 7 | 255 | 0.0 | 11 |

## Gate Notes

- Bots outside target and needing balance review: `random`, `coward`, `tank`, `boss-hunter`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
