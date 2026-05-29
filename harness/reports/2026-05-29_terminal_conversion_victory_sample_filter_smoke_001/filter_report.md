# Bot Trajectory Sample Filter

- Decision: `bot_trajectory_samples_filtered`
- Output: `harness/reports/2026-05-29_terminal_conversion_victory_sample_filter_smoke_001/cracked_victory_terminal_210_240.jsonl`
- Source files: `8`
- Source samples: `12007`
- Kept samples: `358`
- Kept episodes: `2`

## Filters

- `terminal`: `victory`
- `map_ids`: `['cracked-star-jar']`
- `bots`: `None`
- `min_seconds`: `210.0`
- `max_seconds`: `240.0`
- `min_health_ratio`: `None`
- `max_health_ratio`: `None`
- `actions`: `None`
- `max_samples_per_episode`: `None`
- `max_total_samples`: `None`

## Maps

- `cracked-star-jar`: 2

## Dropped Samples

- `time_after_max`: 719
- `time_before_min`: 359

## Limitations

- This filter only preserves existing bot trajectory movement samples.
- Victory-window samples are training input, not policy acceptance evidence.
- Filtered samples still require behavior-clone or SB3 training plus fixed-window high-pressure gates.
