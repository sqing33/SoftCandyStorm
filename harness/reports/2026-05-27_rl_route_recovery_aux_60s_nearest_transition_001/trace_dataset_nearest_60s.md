# Behavior Clone Trace Dataset Comparison

- Gate decision: `trace_dataset_nearest_neighbor_recorded_watch_only`
- Trace samples: `182`
- Offline candidates: `1848`
- Same map only: `True`
- Offline window: `0.0` to `60.0`
- Phase duration conditioning: `300.0`
- Nearest target matches online action ratio: `0.5714`
- Online normalized action entropy: `0.3759`
- Nearest distance average: `1.576151`

## Transitions

```json
{
  "first_online_action_change": {
    "trace_index": 68,
    "time_seconds": 22.6667,
    "from_action": 3,
    "to_action": 5
  },
  "first_nearest_target_change": {
    "trace_index": 21,
    "time_seconds": 7.0,
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
    "count": 108,
    "ratio": 0.5934
  },
  "5": {
    "count": 67,
    "ratio": 0.3681
  },
  "7": {
    "count": 5,
    "ratio": 0.0275
  },
  "1": {
    "count": 2,
    "ratio": 0.011
  }
}
```

### Nearest Offline Target

```json
{
  "3": {
    "count": 95,
    "ratio": 0.522
  },
  "5": {
    "count": 36,
    "ratio": 0.1978
  },
  "4": {
    "count": 5,
    "ratio": 0.0275
  },
  "8": {
    "count": 25,
    "ratio": 0.1374
  },
  "2": {
    "count": 17,
    "ratio": 0.0934
  },
  "7": {
    "count": 1,
    "ratio": 0.0055
  },
  "6": {
    "count": 3,
    "ratio": 0.0165
  }
}
```

## Time Buckets

| Window | Samples | Online Top | Nearest Top | Match Ratio | Avg Distance |
|---|---:|---|---|---:|---:|
| `0-5` | `15` | `3` `1.0000` | `3` `1.0000` | `1.0000` | `0.482732` |
| `5-10` | `15` | `3` `1.0000` | `3` `0.6667` | `0.6667` | `1.349488` |
| `10-15` | `15` | `3` `1.0000` | `3` `0.9333` | `0.9333` | `1.451195` |
| `15-20` | `15` | `3` `1.0000` | `3` `1.0000` | `1.0000` | `1.550432` |
| `20-25` | `15` | `3` `0.5333` | `3` `0.8000` | `0.4667` | `1.663851` |
| `25-30` | `16` | `5` `1.0000` | `3` `0.6875` | `0.0000` | `1.767452` |
| `30-35` | `15` | `5` `1.0000` | `8` `0.8000` | `0.0000` | `2.020581` |
| `35-40` | `15` | `5` `1.0000` | `5` `0.7333` | `0.7333` | `1.808758` |
| `40-45` | `15` | `5` `0.9333` | `5` `0.9333` | `0.9333` | `1.600573` |
| `45-50` | `15` | `3` `0.6000` | `2` `0.4000` | `0.4000` | `1.524377` |
| `50-55` | `15` | `3` `1.0000` | `3` `0.5333` | `0.5333` | `2.022882` |
| `55-60` | `15` | `3` `1.0000` | `2` `0.6000` | `0.2667` | `1.645669` |
| `60-65` | `1` | `3` `1.0000` | `2` `1.0000` | `0.0000` | `1.772180` |

## Examples

- step `1` time `0.0333` online `3` conditioned_progress `0.000111` nearest action `3` distance `0.000111` offline_time `0.0`
- step `10` time `0.3333` online `3` conditioned_progress `0.001111` nearest action `3` distance `0.22428` offline_time `0.3333`
- step `20` time `0.6667` online `3` conditioned_progress `0.002222` nearest action `3` distance `0.237201` offline_time `0.3333`
- step `30` time `1.0` online `3` conditioned_progress `0.003333` nearest action `3` distance `0.22687` offline_time `1.0`
- step `40` time `1.3333` online `3` conditioned_progress `0.004444` nearest action `3` distance `0.299418` offline_time `0.6667`
- step `50` time `1.6667` online `3` conditioned_progress `0.005556` nearest action `3` distance `0.2698` offline_time `1.0`
- step `60` time `2.0` online `3` conditioned_progress `0.006667` nearest action `3` distance `0.293656` offline_time `1.0`
- step `70` time `2.3333` online `3` conditioned_progress `0.007778` nearest action `3` distance `0.341658` offline_time `1.0`
- step `80` time `2.6667` online `3` conditioned_progress `0.008889` nearest action `3` distance `0.327216` offline_time `1.6667`
- step `90` time `3.0` online `3` conditioned_progress `0.01` nearest action `3` distance `0.366852` offline_time `1.6667`
- step `100` time `3.3333` online `3` conditioned_progress `0.011111` nearest action `3` distance `0.653329` offline_time `1.0`
- step `110` time `3.6667` online `3` conditioned_progress `0.012222` nearest action `3` distance `0.799487` offline_time `1.0`

## Limitations

- Nearest-neighbor trace comparison is diagnostic evidence only.
- It does not prove policy quality, Replay stability, balance, or fun.
