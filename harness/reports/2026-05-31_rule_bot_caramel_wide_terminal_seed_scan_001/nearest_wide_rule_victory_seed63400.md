# Behavior Clone Trace Dataset Comparison

- Gate decision: `trace_dataset_nearest_neighbor_recorded_watch_only`
- Trace samples: `1281`
- Offline candidates: `45853`
- Same map only: `True`
- Offline window: `210.0` to `300.0`
- Phase duration conditioning: `None`
- Nearest target matches online action ratio: `0.4176`
- Online normalized action entropy: `0.7585`
- Nearest distance average: `2.401258`

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
    "count": 202,
    "ratio": 0.1577
  },
  "2": {
    "count": 100,
    "ratio": 0.0781
  },
  "0": {
    "count": 113,
    "ratio": 0.0882
  },
  "1": {
    "count": 187,
    "ratio": 0.146
  },
  "3": {
    "count": 205,
    "ratio": 0.16
  },
  "8": {
    "count": 83,
    "ratio": 0.0648
  },
  "6": {
    "count": 156,
    "ratio": 0.1218
  },
  "4": {
    "count": 77,
    "ratio": 0.0601
  },
  "5": {
    "count": 158,
    "ratio": 0.1233
  }
}
```

## Time Buckets

| Window | Samples | Online Top | Nearest Top | Match Ratio | Avg Distance |
|---|---:|---|---|---:|---:|
| `0-30` | `181` | `7` `0.7403` | `7` `0.2652` | `0.3315` | `2.736621` |
| `30-60` | `180` | `7` `0.5167` | `0` `0.2167` | `0.2333` | `2.592696` |
| `60-90` | `180` | `5` `0.3500` | `1` `0.2278` | `0.4000` | `2.836271` |
| `90-120` | `180` | `3` `0.3056` | `5` `0.1778` | `0.3667` | `2.266381` |
| `120-150` | `179` | `7` `0.3575` | `5` `0.2570` | `0.3743` | `2.271357` |
| `150-180` | `180` | `3` `0.4000` | `3` `0.3389` | `0.5278` | `1.903089` |
| `180-210` | `180` | `3` `0.4167` | `3` `0.3056` | `0.7111` | `2.156310` |
| `210-240` | `21` | `5` `1.0000` | `3` `0.5714` | `0.2381` | `2.774094` |

## Examples

- step `1` time `0.0333` online `2` conditioned_progress `0.0` nearest action `7` distance `2.139444` offline_time `293.8498`
- step `5` time `0.1667` online `2` conditioned_progress `0.000444` nearest action `2` distance `2.302291` offline_time `240.8558`
- step `10` time `0.3333` online `2` conditioned_progress `0.001` nearest action `2` distance `2.29033` offline_time `240.8558`
- step `15` time `0.5` online `2` conditioned_progress `0.001556` nearest action `2` distance `2.280856` offline_time `240.8558`
- step `20` time `0.6667` online `2` conditioned_progress `0.002111` nearest action `2` distance `2.272639` offline_time `240.8558`
- step `25` time `0.8333` online `2` conditioned_progress `0.002667` nearest action `2` distance `2.264819` offline_time `240.8558`
- step `30` time `1.0` online `2` conditioned_progress `0.003222` nearest action `0` distance `2.281762` offline_time `241.6893`
- step `35` time `1.1667` online `2` conditioned_progress `0.003778` nearest action `0` distance `2.27395` offline_time `241.6893`
- step `40` time `1.3333` online `2` conditioned_progress `0.004333` nearest action `1` distance `2.27115` offline_time `217.3508`
- step `45` time `1.5` online `2` conditioned_progress `0.004889` nearest action `1` distance `2.265321` offline_time `217.3508`
- step `50` time `1.6667` online `2` conditioned_progress `0.005444` nearest action `1` distance `2.25146` offline_time `217.3508`
- step `55` time `1.8333` online `2` conditioned_progress `0.006` nearest action `1` distance `2.24872` offline_time `217.3508`

## Limitations

- Nearest-neighbor trace comparison is diagnostic evidence only.
- It does not prove policy quality, Replay stability, balance, or fun.
