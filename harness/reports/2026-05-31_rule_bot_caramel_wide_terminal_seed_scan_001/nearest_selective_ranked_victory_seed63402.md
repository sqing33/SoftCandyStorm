# Behavior Clone Trace Dataset Comparison

- Gate decision: `trace_dataset_nearest_neighbor_recorded_watch_only`
- Trace samples: `1473`
- Offline candidates: `3237`
- Same map only: `True`
- Offline window: `210.0` to `300.0`
- Phase duration conditioning: `None`
- Nearest target matches online action ratio: `0.8058`
- Online normalized action entropy: `0.8591`
- Nearest distance average: `2.4921`

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
    "ratio": 0.0577
  },
  "4": {
    "count": 128,
    "ratio": 0.0869
  },
  "3": {
    "count": 272,
    "ratio": 0.1847
  },
  "5": {
    "count": 290,
    "ratio": 0.1969
  },
  "7": {
    "count": 334,
    "ratio": 0.2267
  },
  "8": {
    "count": 190,
    "ratio": 0.129
  },
  "1": {
    "count": 164,
    "ratio": 0.1113
  },
  "6": {
    "count": 10,
    "ratio": 0.0068
  }
}
```

### Nearest Offline Target

```json
{
  "7": {
    "count": 314,
    "ratio": 0.2132
  },
  "2": {
    "count": 122,
    "ratio": 0.0828
  },
  "3": {
    "count": 284,
    "ratio": 0.1928
  },
  "4": {
    "count": 130,
    "ratio": 0.0883
  },
  "1": {
    "count": 121,
    "ratio": 0.0821
  },
  "5": {
    "count": 242,
    "ratio": 0.1643
  },
  "6": {
    "count": 59,
    "ratio": 0.0401
  },
  "8": {
    "count": 201,
    "ratio": 0.1365
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
| `210-240` | `180` | `8` `0.3278` | `8` `0.2778` | `0.6389` | `2.623630` |
| `240-270` | `33` | `3` `0.3333` | `3` `0.3030` | `0.7879` | `2.811932` |

## Examples

- step `1` time `0.0333` online `2` conditioned_progress `0.0` nearest action `7` distance `2.73355` offline_time `258.1919`
- step `5` time `0.1667` online `2` conditioned_progress `0.000444` nearest action `2` distance `2.522428` offline_time `265.8567`
- step `10` time `0.3333` online `2` conditioned_progress `0.001` nearest action `2` distance `2.523326` offline_time `265.8567`
- step `15` time `0.5` online `2` conditioned_progress `0.001556` nearest action `2` distance `2.525153` offline_time `265.8567`
- step `20` time `0.6667` online `2` conditioned_progress `0.002111` nearest action `2` distance `2.527897` offline_time `265.8567`
- step `25` time `0.8333` online `2` conditioned_progress `0.002667` nearest action `2` distance `2.531547` offline_time `265.8567`
- step `30` time `1.0` online `2` conditioned_progress `0.003222` nearest action `2` distance `2.536094` offline_time `265.8567`
- step `35` time `1.1667` online `2` conditioned_progress `0.003778` nearest action `2` distance `2.541529` offline_time `265.8567`
- step `40` time `1.3333` online `2` conditioned_progress `0.004333` nearest action `2` distance `2.324679` offline_time `265.8567`
- step `45` time `1.5` online `2` conditioned_progress `0.004889` nearest action `2` distance `2.332082` offline_time `265.8567`
- step `50` time `1.6667` online `2` conditioned_progress `0.005444` nearest action `2` distance `2.340526` offline_time `265.8567`
- step `55` time `1.8333` online `2` conditioned_progress `0.006` nearest action `2` distance `2.349997` offline_time `265.8567`

## Limitations

- Nearest-neighbor trace comparison is diagnostic evidence only.
- It does not prove policy quality, Replay stability, balance, or fun.
