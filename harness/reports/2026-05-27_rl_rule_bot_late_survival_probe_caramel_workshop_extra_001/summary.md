# Harness Bot Matrix Summary

- Map: `caramel-workshop`
- Seeds: `62300`..`62304` per bot
- Duration target: `300` seconds
- Tick rate: `30`
- Bot count: `4`

## Bot Results

| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |
|---|---|---|---:|---:|---:|---:|---:|---:|
| tank | repair | mid-skill rule bot 25%-55% | 20.0% | 1/5 | 191.6 | 6.2 | 272.0 | 41 |
| coward | repair | low-skill rule bot 10%-35% | 0.0% | 0/5 | 196.0 | 7.4 | 300.6 | 16 |
| route | repair | low-skill rule bot 10%-35% | 0.0% | 0/5 | 205.9 | 5.6 | 303.0 | 28 |
| random | repair | random robustness 0%-15% | 40.0% | 2/5 | 189.0 | 5.6 | 301.6 | 21 |

## Runs

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 62300 | defeat | 214.9 | 7 | 332 | 136.0 | 24 |
| 62301 | victory | 300.0 | 9 | 531 | 95.7 | 17 |
| 62302 | defeat | 137.2 | 4 | 141 | 136.2 | 33 |
| 62303 | defeat | 174.6 | 6 | 226 | 136.1 | 41 |
| 62304 | defeat | 131.3 | 5 | 130 | 136.1 | 29 |

### coward

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 62300 | defeat | 220.2 | 9 | 341 | 136.7 | 10 |
| 62301 | defeat | 241.2 | 9 | 390 | 136.3 | 13 |
| 62302 | defeat | 226.6 | 9 | 351 | 120.2 | 11 |
| 62303 | defeat | 232.2 | 8 | 383 | 136.5 | 16 |
| 62304 | defeat | 59.9 | 2 | 38 | 120.5 | 12 |

### route

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 62300 | defeat | 223.7 | 5 | 341 | 120.6 | 17 |
| 62301 | defeat | 134.6 | 5 | 144 | 120.0 | 28 |
| 62302 | defeat | 223.5 | 7 | 349 | 120.2 | 19 |
| 62303 | defeat | 224.6 | 5 | 341 | 120.3 | 17 |
| 62304 | defeat | 223.0 | 6 | 340 | 120.2 | 18 |

### random

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 62300 | defeat | 222.4 | 7 | 342 | 120.4 | 17 |
| 62301 | defeat | 60.2 | 3 | 41 | 120.1 | 9 |
| 62302 | victory | 300.0 | 9 | 543 | 102.7 | 21 |
| 62303 | victory | 300.0 | 7 | 541 | 110.7 | 20 |
| 62304 | defeat | 62.5 | 2 | 41 | 120.2 | 10 |

## Gate Notes

- Bots outside target and needing balance review: `tank`, `coward`, `route`, `random`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
