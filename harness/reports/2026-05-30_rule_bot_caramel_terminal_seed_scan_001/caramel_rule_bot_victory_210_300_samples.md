# Bot Trajectory Sample Filter

- Decision: `bot_trajectory_samples_filtered`
- Output: `harness/reports/2026-05-30_rule_bot_caramel_terminal_seed_scan_001/caramel_rule_bot_victory_210_300_samples.jsonl`
- Source files: `6`
- Source samples: `21610`
- Kept samples: `8630`
- Kept episodes: `16`

## Filters

- `terminal`: `victory`
- `map_ids`: `['caramel-workshop']`
- `bots`: `None`
- `min_seconds`: `210.0`
- `max_seconds`: `300.0`
- `min_health_ratio`: `None`
- `max_health_ratio`: `None`
- `actions`: `None`
- `max_samples_per_episode`: `None`
- `max_total_samples`: `None`

## Maps

- `caramel-workshop`: 16

## Limitations

- This filter only preserves existing bot trajectory movement samples.
- Victory-window samples are training input, not policy acceptance evidence.
- Filtered samples still require behavior-clone or SB3 training plus fixed-window high-pressure gates.
