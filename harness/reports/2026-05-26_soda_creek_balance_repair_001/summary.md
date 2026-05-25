# Harness Bot Matrix Summary

- Map: `soda-creek`
- Seeds: `12345`..`12347` per bot
- Duration target: `600` seconds
- Tick rate: `30`
- Bot count: `3`

## Bot Results

| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |
|---|---|---|---:|---:|---:|---:|---:|---:|
| kite | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 476.6 | 20.0 | 1917.7 | 38 |
| boss-hunter | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 475.9 | 20.0 | 1897.3 | 40 |
| tank | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 344.8 | 13.0 | 1172.0 | 57 |

## Runs

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 12345 | victory | 600.0 | 24 | 2581 | 91.8 | 32 |
| 12346 | defeat | 229.7 | 11 | 592 | 120.5 | 25 |
| 12347 | victory | 600.0 | 25 | 2580 | 114.3 | 38 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 12345 | defeat | 227.6 | 11 | 610 | 120.5 | 32 |
| 12346 | victory | 600.0 | 24 | 2581 | 62.3 | 24 |
| 12347 | victory | 600.0 | 25 | 2501 | 84.9 | 40 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 12345 | victory | 600.0 | 23 | 2612 | 122.0 | 24 |
| 12346 | defeat | 191.9 | 5 | 242 | 169.1 | 57 |
| 12347 | defeat | 242.4 | 11 | 662 | 136.2 | 44 |

## Gate Notes

- All matrix bots are inside their initial prototype win-rate target ranges.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
