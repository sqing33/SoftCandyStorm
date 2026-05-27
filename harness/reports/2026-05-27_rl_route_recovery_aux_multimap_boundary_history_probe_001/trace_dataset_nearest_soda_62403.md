# Behavior Clone Trace Dataset Comparison

- Gate decision: `trace_dataset_nearest_neighbor_recorded_watch_only`
- Trace samples: `142`
- Offline candidates: `2213`
- Same map only: `True`
- Offline window: `0.0` to `60.0`
- Phase duration conditioning: `300.0`
- Nearest target matches online action ratio: `0.9225`
- Online normalized action entropy: `0.3387`
- Nearest distance average: `2.350806`

## Transitions

```json
{
  "first_online_action_change": {
    "trace_index": 10,
    "time_seconds": 3.3333,
    "from_action": 3,
    "to_action": 5
  },
  "first_nearest_target_change": {
    "trace_index": 10,
    "time_seconds": 3.3333,
    "from_action": 3,
    "to_action": 5
  }
}
```

## Action Distributions

### Online

```json
{
  "3": {
    "count": 10,
    "ratio": 0.0704
  },
  "5": {
    "count": 29,
    "ratio": 0.2042
  },
  "6": {
    "count": 103,
    "ratio": 0.7254
  }
}
```

### Nearest Offline Target

```json
{
  "3": {
    "count": 14,
    "ratio": 0.0986
  },
  "5": {
    "count": 22,
    "ratio": 0.1549
  },
  "4": {
    "count": 7,
    "ratio": 0.0493
  },
  "6": {
    "count": 99,
    "ratio": 0.6972
  }
}
```

## Time Buckets

| Window | Samples | Online Top | Nearest Top | Match Ratio | Avg Distance |
|---|---:|---|---|---:|---:|
| `0-10` | `30` | `5` `0.6667` | `5` `0.5000` | `0.8333` | `1.140514` |
| `10-20` | `30` | `6` `0.7000` | `6` `0.7000` | `0.9333` | `1.950472` |
| `20-30` | `31` | `6` `1.0000` | `6` `1.0000` | `1.0000` | `2.822448` |
| `30-40` | `30` | `6` `1.0000` | `6` `0.9333` | `0.9333` | `2.967995` |
| `40-50` | `21` | `6` `1.0000` | `6` `0.9048` | `0.9048` | `3.073770` |

## Examples

- step `1` time `0.0333` online `3` conditioned_progress `0.000111` nearest action `3` distance `0.000111` offline_time `0.0`
- step `10` time `0.3333` online `3` conditioned_progress `0.001111` nearest action `3` distance `0.292279` offline_time `0.3333`
- step `20` time `0.6667` online `3` conditioned_progress `0.002222` nearest action `3` distance `0.29249` offline_time `0.6667`
- step `30` time `1.0` online `3` conditioned_progress `0.003333` nearest action `3` distance `0.292794` offline_time `1.0`
- step `40` time `1.3333` online `3` conditioned_progress `0.004444` nearest action `3` distance `0.489747` offline_time `2.0`
- step `50` time `1.6667` online `3` conditioned_progress `0.005556` nearest action `3` distance `0.462489` offline_time `2.0`
- step `60` time `2.0` online `3` conditioned_progress `0.006667` nearest action `3` distance `0.896587` offline_time `2.6667`
- step `70` time `2.3333` online `3` conditioned_progress `0.007778` nearest action `3` distance `0.639466` offline_time `4.0`
- step `80` time `2.6667` online `3` conditioned_progress `0.008889` nearest action `3` distance `0.681876` offline_time `4.3333`
- step `90` time `3.0` online `3` conditioned_progress `0.01` nearest action `3` distance `0.692882` offline_time `4.6667`
- step `100` time `3.3333` online `5` conditioned_progress `0.011111` nearest action `5` distance `1.189112` offline_time `5.3333`
- step `110` time `3.6667` online `5` conditioned_progress `0.012222` nearest action `5` distance `1.196455` offline_time `5.3333`

## Limitations

- Nearest-neighbor trace comparison is diagnostic evidence only.
- It does not prove policy quality, Replay stability, balance, or fun.
