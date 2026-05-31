# Behavior Clone Trace Dataset Comparison

- Gate decision: `trace_dataset_nearest_neighbor_recorded_watch_only`
- Trace samples: `1466`
- Offline candidates: `3237`
- Same map only: `True`
- Offline window: `210.0` to `300.0`
- Phase duration conditioning: `None`
- Nearest target matches online action ratio: `0.8172`
- Online normalized action entropy: `0.8532`
- Nearest distance average: `2.490466`

## Transitions

```json
{
  "first_online_action_change": {
    "trace_index": 39,
    "time_seconds": 6.5,
    "from_action": 2,
    "to_action": 4
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
    "count": 85,
    "ratio": 0.058
  },
  "4": {
    "count": 124,
    "ratio": 0.0846
  },
  "3": {
    "count": 261,
    "ratio": 0.178
  },
  "5": {
    "count": 317,
    "ratio": 0.2162
  },
  "7": {
    "count": 334,
    "ratio": 0.2278
  },
  "8": {
    "count": 143,
    "ratio": 0.0975
  },
  "1": {
    "count": 193,
    "ratio": 0.1317
  },
  "6": {
    "count": 9,
    "ratio": 0.0061
  }
}
```

### Nearest Offline Target

```json
{
  "7": {
    "count": 304,
    "ratio": 0.2074
  },
  "2": {
    "count": 123,
    "ratio": 0.0839
  },
  "3": {
    "count": 275,
    "ratio": 0.1876
  },
  "4": {
    "count": 127,
    "ratio": 0.0866
  },
  "1": {
    "count": 144,
    "ratio": 0.0982
  },
  "5": {
    "count": 266,
    "ratio": 0.1814
  },
  "6": {
    "count": 58,
    "ratio": 0.0396
  },
  "8": {
    "count": 169,
    "ratio": 0.1153
  }
}
```

## Time Buckets

| Window | Samples | Online Top | Nearest Top | Match Ratio | Avg Distance |
|---|---:|---|---|---:|---:|
| `0-30` | `181` | `5` `0.4530` | `5` `0.3923` | `0.7845` | `2.654504` |
| `30-60` | `180` | `7` `0.7222` | `7` `0.6444` | `0.9111` | `2.817265` |
| `60-90` | `180` | `2` `0.2333` | `4` `0.2167` | `0.6944` | `2.348759` |
| `90-120` | `180` | `3` `0.4167` | `3` `0.4000` | `0.9056` | `2.435928` |
| `120-150` | `179` | `7` `0.4637` | `7` `0.3575` | `0.7933` | `2.247129` |
| `150-180` | `180` | `3` `0.3167` | `3` `0.3222` | `0.7944` | `2.446918` |
| `180-210` | `180` | `8` `0.2833` | `7` `0.2722` | `0.9278` | `2.301766` |
| `210-240` | `180` | `1` `0.3500` | `1` `0.2333` | `0.7111` | `2.655651` |
| `240-270` | `26` | `5` `1.0000` | `5` `0.9231` | `0.9231` | `2.584260` |

## Examples

- step `1` time `0.0333` online `2` conditioned_progress `0.0` nearest action `7` distance `2.73355` offline_time `258.1919`
- step `5` time `0.1667` online `2` conditioned_progress `0.000444` nearest action `2` distance `2.522428` offline_time `265.8567`
- step `10` time `0.3333` online `2` conditioned_progress `0.001` nearest action `2` distance `2.523326` offline_time `265.8567`
- step `15` time `0.5` online `2` conditioned_progress `0.001556` nearest action `2` distance `2.525153` offline_time `265.8567`
- step `20` time `0.6667` online `2` conditioned_progress `0.002111` nearest action `2` distance `2.527897` offline_time `265.8567`
- step `25` time `0.8333` online `2` conditioned_progress `0.002667` nearest action `2` distance `2.531547` offline_time `265.8567`
- step `30` time `1.0` online `2` conditioned_progress `0.003222` nearest action `2` distance `2.536094` offline_time `265.8567`
- step `35` time `1.1667` online `2` conditioned_progress `0.003778` nearest action `2` distance `2.541529` offline_time `265.8567`

## Limitations

- Nearest-neighbor trace comparison is diagnostic evidence only.
- It does not prove policy quality, Replay stability, balance, or fun.
