# Harness Bot Matrix Summary

- Map: `cracked-star-jar`
- Seeds: `12345`..`12347` per bot
- Duration target: `600` seconds
- Tick rate: `30`
- Bot count: `3`

## Bot Results

| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |
|---|---|---|---:|---:|---:|---:|---:|---:|
| kite | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 491.4 | 21.3 | 1690.7 | 36 |
| boss-hunter | pass | high-skill rule bot 45%-75% | 66.7% | 2/3 | 475.0 | 20.7 | 1646.3 | 36 |
| tank | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 364.9 | 13.7 | 1115.3 | 33 |

## Runs

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 12345 | victory | 600.0 | 25 | 2227 | 50.4 | 32 |
| 12346 | victory | 600.0 | 26 | 2168 | 79.9 | 36 |
| 12347 | defeat | 274.1 | 13 | 677 | 136.1 | 15 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 12345 | victory | 600.0 | 25 | 2302 | 105.2 | 31 |
| 12346 | victory | 600.0 | 26 | 2159 | 135.5 | 36 |
| 12347 | defeat | 225.1 | 11 | 478 | 136.4 | 27 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 12345 | defeat | 256.3 | 11 | 656 | 120.1 | 21 |
| 12346 | victory | 600.0 | 20 | 2193 | 120.5 | 33 |
| 12347 | defeat | 238.3 | 10 | 497 | 136.2 | 32 |

## Gate Notes

- All matrix bots are inside their initial prototype win-rate target ranges.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
