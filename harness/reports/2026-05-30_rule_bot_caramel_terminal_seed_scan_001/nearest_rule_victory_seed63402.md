# Behavior Clone Trace Dataset Comparison

- Gate decision: `trace_dataset_nearest_neighbor_recorded_watch_only`
- Trace samples: `1473`
- Offline candidates: `8630`
- Same map only: `True`
- Offline window: `210.0` to `300.0`
- Phase duration conditioning: `None`
- Nearest target matches online action ratio: `0.4182`
- Online normalized action entropy: `0.8591`
- Nearest distance average: `2.45622`

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
    "to_action": 0
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
    "count": 235,
    "ratio": 0.1595
  },
  "0": {
    "count": 100,
    "ratio": 0.0679
  },
  "2": {
    "count": 105,
    "ratio": 0.0713
  },
  "6": {
    "count": 85,
    "ratio": 0.0577
  },
  "1": {
    "count": 202,
    "ratio": 0.1371
  },
  "3": {
    "count": 219,
    "ratio": 0.1487
  },
  "5": {
    "count": 164,
    "ratio": 0.1113
  },
  "4": {
    "count": 112,
    "ratio": 0.076
  },
  "8": {
    "count": 251,
    "ratio": 0.1704
  }
}
```

## Time Buckets

| Window | Samples | Online Top | Nearest Top | Match Ratio | Avg Distance |
|---|---:|---|---|---:|---:|
| `0-30` | `181` | `5` `0.4530` | `5` `0.3867` | `0.3536` | `2.581312` |
| `30-60` | `180` | `7` `0.7222` | `8` `0.3667` | `0.5389` | `2.887281` |
| `60-90` | `180` | `2` `0.2333` | `5` `0.2500` | `0.2278` | `2.131211` |
| `90-120` | `180` | `3` `0.4167` | `3` `0.3833` | `0.5167` | `2.322200` |
| `120-150` | `179` | `7` `0.4637` | `7` `0.2849` | `0.3575` | `2.238986` |
| `150-180` | `180` | `3` `0.3167` | `2` `0.2500` | `0.2556` | `2.424244` |
| `180-210` | `180` | `8` `0.2833` | `7` `0.2444` | `0.5667` | `2.343423` |
| `210-240` | `180` | `8` `0.3278` | `8` `0.2778` | `0.4833` | `2.650551` |
| `240-270` | `33` | `3` `0.3333` | `1` `0.2424` | `0.6667` | `2.830671` |

## Examples

- step `1` time `0.0333` online `2` conditioned_progress `0.0` nearest action `7` distance `2.139444` offline_time `293.8498`
- step `5` time `0.1667` online `2` conditioned_progress `0.000444` nearest action `0` distance `2.299743` offline_time `238.6887`
- step `10` time `0.3333` online `2` conditioned_progress `0.001` nearest action `0` distance `2.298974` offline_time `238.6887`
- step `15` time `0.5` online `2` conditioned_progress `0.001556` nearest action `0` distance `2.299128` offline_time `238.6887`
- step `20` time `0.6667` online `2` conditioned_progress `0.002111` nearest action `0` distance `2.300211` offline_time `238.6887`
- step `25` time `0.8333` online `2` conditioned_progress `0.002667` nearest action `0` distance `2.302227` offline_time `238.6887`
- step `30` time `1.0` online `2` conditioned_progress `0.003222` nearest action `0` distance `2.305176` offline_time `238.6887`
- step `35` time `1.1667` online `2` conditioned_progress `0.003778` nearest action `0` distance `2.309061` offline_time `238.6887`
- step `40` time `1.3333` online `2` conditioned_progress `0.004333` nearest action `2` distance `2.324679` offline_time `265.8567`
- step `45` time `1.5` online `2` conditioned_progress `0.004889` nearest action `6` distance `2.330991` offline_time `242.8562`
- step `50` time `1.6667` online `2` conditioned_progress `0.005444` nearest action `6` distance `2.337266` offline_time `242.8562`
- step `55` time `1.8333` online `2` conditioned_progress `0.006` nearest action `6` distance `2.344536` offline_time `242.8562`

## Limitations

- Nearest-neighbor trace comparison is diagnostic evidence only.
- It does not prove policy quality, Replay stability, balance, or fun.
