# Behavior Clone Trace Dataset Comparison

- Gate decision: `trace_dataset_nearest_neighbor_recorded_watch_only`
- Trace samples: `1281`
- Offline candidates: `3237`
- Same map only: `True`
- Offline window: `210.0` to `300.0`
- Phase duration conditioning: `None`
- Nearest target matches online action ratio: `0.8509`
- Online normalized action entropy: `0.7585`
- Nearest distance average: `2.550705`

## Transitions

```json
{
  "first_online_action_change": {
    "trace_index": 47,
    "time_seconds": 7.8333,
    "from_action": 2,
    "to_action": 7
  },
  "first_nearest_target_change": {
    "trace_index": 1,
    "time_seconds": 0.1667,
    "from_action": 7,
    "to_action": 2
  }
}
```

## Action Distributions

### Online

```json
{
  "2": {
    "count": 50,
    "ratio": 0.039
  },
  "7": {
    "count": 454,
    "ratio": 0.3544
  },
  "4": {
    "count": 53,
    "ratio": 0.0414
  },
  "3": {
    "count": 309,
    "ratio": 0.2412
  },
  "5": {
    "count": 194,
    "ratio": 0.1514
  },
  "8": {
    "count": 64,
    "ratio": 0.05
  },
  "0": {
    "count": 1,
    "ratio": 0.0008
  },
  "1": {
    "count": 156,
    "ratio": 0.1218
  }
}
```

### Nearest Offline Target

```json
{
  "7": {
    "count": 402,
    "ratio": 0.3138
  },
  "2": {
    "count": 81,
    "ratio": 0.0632
  },
  "1": {
    "count": 133,
    "ratio": 0.1038
  },
  "8": {
    "count": 109,
    "ratio": 0.0851
  },
  "6": {
    "count": 13,
    "ratio": 0.0101
  },
  "3": {
    "count": 312,
    "ratio": 0.2436
  },
  "4": {
    "count": 43,
    "ratio": 0.0336
  },
  "5": {
    "count": 188,
    "ratio": 0.1468
  }
}
```

## Time Buckets

| Window | Samples | Online Top | Nearest Top | Match Ratio | Avg Distance |
|---|---:|---|---|---:|---:|
| `0-30` | `181` | `7` `0.7403` | `7` `0.5912` | `0.8177` | `2.925880` |
| `30-60` | `180` | `7` `0.5167` | `7` `0.4556` | `0.8278` | `2.766732` |
| `60-90` | `180` | `5` `0.3500` | `7` `0.4222` | `0.7944` | `3.042057` |
| `90-120` | `180` | `3` `0.3056` | `3` `0.3333` | `0.8000` | `2.370364` |
| `120-150` | `179` | `7` `0.3575` | `7` `0.3296` | `0.9497` | `2.399975` |
| `150-180` | `180` | `3` `0.4000` | `3` `0.3944` | `0.9111` | `2.019681` |
| `180-210` | `180` | `3` `0.4167` | `3` `0.4111` | `0.8500` | `2.281342` |
| `210-240` | `21` | `5` `1.0000` | `5` `0.9048` | `0.9048` | `2.944834` |

## Examples

- step `1` time `0.0333` online `2` conditioned_progress `0.0` nearest action `7` distance `2.73355` offline_time `258.1919`
- step `5` time `0.1667` online `2` conditioned_progress `0.000444` nearest action `2` distance `2.580627` offline_time `265.8567`
- step `10` time `0.3333` online `2` conditioned_progress `0.001` nearest action `2` distance `2.577144` offline_time `265.8567`
- step `15` time `0.5` online `2` conditioned_progress `0.001556` nearest action `2` distance `2.576245` offline_time `265.8567`
- step `20` time `0.6667` online `2` conditioned_progress `0.002111` nearest action `2` distance `2.576811` offline_time `265.8567`
- step `25` time `0.8333` online `2` conditioned_progress `0.002667` nearest action `2` distance `2.569985` offline_time `265.8567`
- step `30` time `1.0` online `2` conditioned_progress `0.003222` nearest action `2` distance `2.604729` offline_time `265.8567`
- step `35` time `1.1667` online `2` conditioned_progress `0.003778` nearest action `2` distance `2.6088` offline_time `265.8567`
- step `40` time `1.3333` online `2` conditioned_progress `0.004333` nearest action `2` distance `2.468726` offline_time `265.8567`
- step `45` time `1.5` online `2` conditioned_progress `0.004889` nearest action `2` distance `2.470006` offline_time `265.8567`
- step `50` time `1.6667` online `2` conditioned_progress `0.005444` nearest action `2` distance `2.469195` offline_time `265.8567`
- step `55` time `1.8333` online `2` conditioned_progress `0.006` nearest action `2` distance `2.473197` offline_time `265.8567`

## Limitations

- Nearest-neighbor trace comparison is diagnostic evidence only.
- It does not prove policy quality, Replay stability, balance, or fun.
