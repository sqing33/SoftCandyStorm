# Harness Bot Matrix Summary

- Map: `caramel-workshop`
- Seeds: `12345`..`12347` per bot
- Duration target: `600` seconds
- Tick rate: `30`
- Bot count: `3`

## Bot Results

| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |
|---|---|---|---:|---:|---:|---:|---:|---:|
| kite | repair | high-skill rule bot 45%-75% | 100.0% | 3/3 | 600.0 | 24.0 | 1943.0 | 41 |
| boss-hunter | repair | high-skill rule bot 45%-75% | 100.0% | 3/3 | 600.0 | 24.3 | 1938.0 | 42 |
| tank | repair | mid-skill rule bot 25%-55% | 100.0% | 3/3 | 600.0 | 23.3 | 1974.0 | 41 |

## Runs

### kite

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 12345 | victory | 600.0 | 24 | 1963 | 12.7 | 26 |
| 12346 | victory | 600.0 | 24 | 1954 | 0.8 | 41 |
| 12347 | victory | 600.0 | 24 | 1912 | 53.0 | 24 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 12345 | victory | 600.0 | 25 | 1957 | 30.2 | 33 |
| 12346 | victory | 600.0 | 24 | 1930 | 56.7 | 42 |
| 12347 | victory | 600.0 | 24 | 1927 | 48.7 | 30 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 12345 | victory | 600.0 | 23 | 1955 | 0.0 | 31 |
| 12346 | victory | 600.0 | 23 | 1970 | 0.2 | 25 |
| 12347 | victory | 600.0 | 24 | 1997 | 16.6 | 41 |

## Gate Notes

- Bots outside target and needing balance review: `kite`, `boss-hunter`, `tank`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
