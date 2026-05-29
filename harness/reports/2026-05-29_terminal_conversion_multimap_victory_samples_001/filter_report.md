# Bot Trajectory Sample Filter

- Decision: `bot_trajectory_samples_filtered`
- Output: `harness/reports/2026-05-29_terminal_conversion_multimap_victory_samples_001/victory_terminal_210_240.jsonl`
- Source files: `8`
- Source samples: `12007`
- Kept samples: `1437`
- Kept episodes: `8`

## Filters

- `terminal`: `victory`
- `map_ids`: `None`
- `bots`: `None`
- `min_seconds`: `210.0`
- `max_seconds`: `240.0`
- `min_health_ratio`: `None`
- `max_health_ratio`: `None`
- `actions`: `None`
- `max_samples_per_episode`: `None`
- `max_total_samples`: `None`

## Maps

- `caramel-workshop`: 1
- `cracked-star-jar`: 2
- `soda-creek`: 5

## Dropped Samples

- `time_after_max`: 2876
- `time_before_min`: 1438

## Limitations

- This filter only preserves existing bot trajectory movement samples.
- Victory-window samples are training input, not policy acceptance evidence.
- Filtered samples still require behavior-clone or SB3 training plus fixed-window high-pressure gates.
