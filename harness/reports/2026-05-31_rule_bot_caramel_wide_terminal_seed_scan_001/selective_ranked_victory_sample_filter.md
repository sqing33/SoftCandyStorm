# Bot Trajectory Sample Filter

- Decision: `bot_trajectory_samples_filtered`
- Output: `harness/reports/2026-05-31_rule_bot_caramel_wide_terminal_seed_scan_001/caramel_selective_ranked_victory_210_300_samples.jsonl`
- Source files: `1`
- Source samples: `45853`
- Kept samples: `3237`
- Kept episodes: `6`

## Filters

- `terminal`: `victory`
- `map_ids`: `['caramel-workshop']`
- `seeds`: `['63333', '63348', '63412', '63417', '63488', '63489']`
- `bots`: `['greedy', 'route']`
- `min_seconds`: `210.0`
- `max_seconds`: `300.0`
- `min_health_ratio`: `None`
- `max_health_ratio`: `None`
- `actions`: `None`
- `max_samples_per_episode`: `None`
- `max_total_samples`: `None`

## Maps

- `caramel-workshop`: 6

## Limitations

- This filter only preserves existing bot trajectory movement samples.
- Victory-window samples are training input, not policy acceptance evidence.
- Filtered samples still require behavior-clone or SB3 training plus fixed-window high-pressure gates.
