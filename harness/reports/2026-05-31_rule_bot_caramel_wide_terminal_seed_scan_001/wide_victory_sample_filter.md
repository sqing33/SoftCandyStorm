# Bot Trajectory Sample Filter

- Decision: `bot_trajectory_samples_filtered`
- Output: `/private/tmp/soft-candy-caramel-wide-trajectories-63300-63500/caramel_rule_bot_wide_victory_210_300_samples.jsonl`
- Source files: `6`
- Source samples: `107661`
- Kept samples: `45853`
- Kept episodes: `85`

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

- `caramel-workshop`: 85

## Limitations

- This filter only preserves existing bot trajectory movement samples.
- Victory-window samples are training input, not policy acceptance evidence.
- Filtered samples still require behavior-clone or SB3 training plus fixed-window high-pressure gates.
