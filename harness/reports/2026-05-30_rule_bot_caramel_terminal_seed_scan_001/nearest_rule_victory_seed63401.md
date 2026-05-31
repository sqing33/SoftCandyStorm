# Behavior Clone Trace Dataset Comparison

- Gate decision: `trace_dataset_nearest_neighbor_recorded_watch_only`
- Trace samples: `1413`
- Offline candidates: `8630`
- Same map only: `True`
- Offline window: `210.0` to `300.0`
- Phase duration conditioning: `None`
- Nearest target matches online action ratio: `0.5605`
- Online normalized action entropy: `0.8515`
- Nearest distance average: `2.416173`

## Transitions

```json
{
  "first_online_action_change": {
    "trace_index": 155,
    "time_seconds": 25.8333,
    "from_action": 2,
    "to_action": 7
  },
  "first_nearest_target_change": {
    "trace_index": 1,
    "time_seconds": 0.1667,
    "from_action": 7,
    "to_action": 0
  }
}
```

## Action Distributions

### Online

```json
{
  "2": {
    "count": 171,
    "ratio": 0.121
  },
  "7": {
    "count": 388,
    "ratio": 0.2746
  },
  "5": {
    "count": 234,
    "ratio": 0.1656
  },
  "4": {
    "count": 113,
    "ratio": 0.08
  },
  "3": {
    "count": 192,
    "ratio": 0.1359
  },
  "1": {
    "count": 199,
    "ratio": 0.1408
  },
  "8": {
    "count": 114,
    "ratio": 0.0807
  },
  "6": {
    "count": 1,
    "ratio": 0.0007
  },
  "0": {
    "count": 1,
    "ratio": 0.0007
  }
}
```

### Nearest Offline Target

```json
{
  "7": {
    "count": 327,
    "ratio": 0.2314
  },
  "0": {
    "count": 67,
    "ratio": 0.0474
  },
  "6": {
    "count": 38,
    "ratio": 0.0269
  },
  "1": {
    "count": 229,
    "ratio": 0.1621
  },
  "8": {
    "count": 173,
    "ratio": 0.1224
  },
  "3": {
    "count": 209,
    "ratio": 0.1479
  },
  "4": {
    "count": 103,
    "ratio": 0.0729
  },
  "2": {
    "count": 118,
    "ratio": 0.0835
  },
  "5": {
    "count": 149,
    "ratio": 0.1054
  }
}
```

## Time Buckets

| Window | Samples | Online Top | Nearest Top | Match Ratio | Avg Distance |
|---|---:|---|---|---:|---:|
| `0-30` | `181` | `2` `0.8564` | `2` `0.2928` | `0.3702` | `2.619800` |
| `30-60` | `180` | `7` `1.0000` | `7` `0.6611` | `0.6611` | `2.745201` |
| `60-90` | `180` | `7` `0.3222` | `1` `0.2889` | `0.5333` | `2.541743` |
| `90-120` | `180` | `3` `0.4167` | `3` `0.2944` | `0.3389` | `2.247901` |
| `120-150` | `179` | `7` `0.3073` | `1` `0.2682` | `0.5140` | `2.325378` |
| `150-180` | `180` | `8` `0.3056` | `5` `0.3000` | `0.6333` | `2.295685` |
| `180-210` | `180` | `5` `0.3000` | `5` `0.3167` | `0.6722` | `2.047122` |
| `210-240` | `153` | `7` `0.2941` | `7` `0.2288` | `0.7974` | `2.520579` |

## Examples

- step `1` time `0.0333` online `2` conditioned_progress `0.0` nearest action `7` distance `2.139444` offline_time `293.8498`
- step `5` time `0.1667` online `2` conditioned_progress `0.000444` nearest action `0` distance `2.317449` offline_time `238.6887`
- step `10` time `0.3333` online `2` conditioned_progress `0.001` nearest action `0` distance `2.308887` offline_time `238.6887`
- step `15` time `0.5` online `2` conditioned_progress `0.001556` nearest action `0` distance `2.302684` offline_time `238.6887`
- step `20` time `0.6667` online `2` conditioned_progress `0.002111` nearest action `0` distance `2.297902` offline_time `238.6887`
- step `25` time `0.8333` online `2` conditioned_progress `0.002667` nearest action `0` distance `2.423834` offline_time `238.6887`
- step `30` time `1.0` online `2` conditioned_progress `0.003222` nearest action `0` distance `2.421191` offline_time `238.6887`
- step `35` time `1.1667` online `2` conditioned_progress `0.003778` nearest action `0` distance `2.420999` offline_time `238.6887`
- step `40` time `1.3333` online `2` conditioned_progress `0.004333` nearest action `6` distance `2.483087` offline_time `242.8562`
- step `45` time `1.5` online `2` conditioned_progress `0.004889` nearest action `0` distance `2.258231` offline_time `238.6887`
- step `50` time `1.6667` online `2` conditioned_progress `0.005444` nearest action `0` distance `2.260088` offline_time `238.6887`
- step `55` time `1.8333` online `2` conditioned_progress `0.006` nearest action `0` distance `2.263462` offline_time `238.6887`

## Limitations

- Nearest-neighbor trace comparison is diagnostic evidence only.
- It does not prove policy quality, Replay stability, balance, or fun.
