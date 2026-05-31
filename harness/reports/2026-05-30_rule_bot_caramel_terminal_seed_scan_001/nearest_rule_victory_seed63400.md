# Behavior Clone Trace Dataset Comparison

- Gate decision: `trace_dataset_nearest_neighbor_recorded_watch_only`
- Trace samples: `1281`
- Offline candidates: `8630`
- Same map only: `True`
- Offline window: `210.0` to `300.0`
- Phase duration conditioning: `None`
- Nearest target matches online action ratio: `0.5527`
- Online normalized action entropy: `0.7585`
- Nearest distance average: `2.528792`

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
    "count": 368,
    "ratio": 0.2873
  },
  "2": {
    "count": 75,
    "ratio": 0.0585
  },
  "1": {
    "count": 220,
    "ratio": 0.1717
  },
  "3": {
    "count": 255,
    "ratio": 0.1991
  },
  "5": {
    "count": 111,
    "ratio": 0.0867
  },
  "4": {
    "count": 80,
    "ratio": 0.0625
  },
  "8": {
    "count": 90,
    "ratio": 0.0703
  },
  "6": {
    "count": 44,
    "ratio": 0.0343
  },
  "0": {
    "count": 38,
    "ratio": 0.0297
  }
}
```

## Time Buckets

| Window | Samples | Online Top | Nearest Top | Match Ratio | Avg Distance |
|---|---:|---|---|---:|---:|
| `0-30` | `181` | `7` `0.7403` | `7` `0.6243` | `0.7017` | `2.919077` |
| `30-60` | `180` | `7` `0.5167` | `7` `0.5000` | `0.6556` | `2.767171` |
| `60-90` | `180` | `5` `0.3500` | `1` `0.3000` | `0.3167` | `2.916589` |
| `90-120` | `180` | `3` `0.3056` | `3` `0.3000` | `0.7611` | `2.389528` |
| `120-150` | `179` | `7` `0.3575` | `5` `0.2570` | `0.4972` | `2.426199` |
| `150-180` | `180` | `3` `0.4000` | `3` `0.3222` | `0.4056` | `1.975223` |
| `180-210` | `180` | `3` `0.4167` | `3` `0.3056` | `0.5944` | `2.269768` |
| `210-240` | `21` | `5` `1.0000` | `3` `0.8571` | `0.0000` | `2.830948` |

## Examples

- step `1` time `0.0333` online `2` conditioned_progress `0.0` nearest action `7` distance `2.139444` offline_time `293.8498`
- step `5` time `0.1667` online `2` conditioned_progress `0.000444` nearest action `2` distance `2.345198` offline_time `239.3555`
- step `10` time `0.3333` online `2` conditioned_progress `0.001` nearest action `2` distance `2.344766` offline_time `239.3555`
- step `15` time `0.5` online `2` conditioned_progress `0.001556` nearest action `2` distance `2.34803` offline_time `239.3555`
- step `20` time `0.6667` online `2` conditioned_progress `0.002111` nearest action `2` distance `2.352827` offline_time `239.3555`
- step `25` time `0.8333` online `2` conditioned_progress `0.002667` nearest action `2` distance `2.350824` offline_time `239.3555`
- step `30` time `1.0` online `2` conditioned_progress `0.003222` nearest action `2` distance `2.382902` offline_time `253.0251`
- step `35` time `1.1667` online `2` conditioned_progress `0.003778` nearest action `2` distance `2.386068` offline_time `253.0251`
- step `40` time `1.3333` online `2` conditioned_progress `0.004333` nearest action `2` distance `2.442196` offline_time `260.6913`
- step `45` time `1.5` online `2` conditioned_progress `0.004889` nearest action `2` distance `2.452938` offline_time `260.6913`
- step `50` time `1.6667` online `2` conditioned_progress `0.005444` nearest action `2` distance `2.444611` offline_time `260.6913`
- step `55` time `1.8333` online `2` conditioned_progress `0.006` nearest action `2` distance `2.457093` offline_time `260.6913`

## Limitations

- Nearest-neighbor trace comparison is diagnostic evidence only.
- It does not prove policy quality, Replay stability, balance, or fun.
