# Harness Bot Matrix Summary

- Map: `caramel-workshop`
- Seeds: `12345`..`12347` per bot
- Duration target: `600` seconds
- Tick rate: `30`
- Bot count: `3`

## Bot Results

| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |
|---|---|---|---:|---:|---:|---:|---:|---:|
| kite | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 479.4 | 20.0 | 1543.7 | 40 |
| boss-hunter | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 472.2 | 20.0 | 1548.7 | 41 |
| tank | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 462.8 | 18.0 | 1462.0 | 24 |

## Runs

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 12345 | victory | 600.0 | 25 | 2176 | 43.5 | 34 |
| 12346 | victory | 600.0 | 25 | 2072 | 80.3 | 40 |
| 12347 | defeat | 238.2 | 10 | 383 | 121.2 | 9 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 12345 | victory | 600.0 | 25 | 2161 | 103.1 | 41 |
| 12346 | defeat | 216.7 | 9 | 323 | 137.2 | 19 |
| 12347 | victory | 600.0 | 26 | 2162 | 92.3 | 31 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 12345 | victory | 600.0 | 23 | 2151 | 91.5 | 24 |
| 12346 | defeat | 232.6 | 9 | 365 | 153.4 | 12 |
| 12347 | defeat | 555.8 | 22 | 1870 | 120.3 | 24 |

## Gate Notes

- All matrix bots are inside their initial prototype win-rate target ranges.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
