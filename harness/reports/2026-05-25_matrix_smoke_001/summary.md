# Harness Bot Matrix Summary

- Seeds: `20000`..`20002` per bot
- Duration target: `180` seconds
- Tick rate: `30`
- Bot count: `4`

## Bot Results

| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |
|---|---|---|---:|---:|---:|---:|---:|---:|
| random | pass | random robustness 0%-15% | 0.0% | 0/3 | 106.8 | 2.3 | 85.7 | 22 |
| coward | pass | low-skill rule bot 10%-35% | 33.3% | 1/3 | 145.0 | 4.3 | 118.0 | 55 |
| tank | pass | mid-skill rule bot 25%-55% | 33.3% | 1/3 | 147.9 | 5.0 | 137.7 | 55 |
| boss-hunter | repair | high-skill rule bot 45%-75% | 100.0% | 3/3 | 180.0 | 5.3 | 251.3 | 26 |

## Runs

### random

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 20000 | defeat | 108.5 | 2 | 89 | 142.8 | 22 |
| 20001 | defeat | 106.3 | 3 | 85 | 120.0 | 22 |
| 20002 | defeat | 105.7 | 2 | 83 | 121.0 | 22 |

### coward

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 20000 | victory | 180.0 | 5 | 149 | 146.8 | 55 |
| 20001 | defeat | 138.0 | 4 | 111 | 143.1 | 55 |
| 20002 | defeat | 117.0 | 4 | 94 | 120.5 | 35 |

### tank

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 20000 | victory | 180.0 | 6 | 177 | 126.8 | 55 |
| 20001 | defeat | 139.3 | 5 | 132 | 142.6 | 44 |
| 20002 | defeat | 124.6 | 4 | 104 | 164.7 | 41 |

### boss-hunter

| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |
|---:|---|---:|---:|---:|---:|---:|
| 20000 | victory | 180.0 | 5 | 247 | 0.0 | 16 |
| 20001 | victory | 180.0 | 6 | 253 | 0.0 | 12 |
| 20002 | victory | 180.0 | 5 | 254 | 69.8 | 26 |

## Gate Notes

- Bots outside target and needing balance review: `boss-hunter`.
- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.
- `representative_replays/` contains prototype replay JSON for each matrix run.
