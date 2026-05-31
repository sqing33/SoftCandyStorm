# Behavior Clone Trace Dataset Comparison

- Gate decision: `trace_dataset_nearest_neighbor_recorded_watch_only`
- Trace samples: `1473`
- Offline candidates: `45853`
- Same map only: `True`
- Offline window: `210.0` to `300.0`
- Phase duration conditioning: `None`
- Nearest target matches online action ratio: `0.4915`
- Online normalized action entropy: `0.8591`
- Nearest distance average: `2.319987`

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
    "count": 182,
    "ratio": 0.1236
  },
  "0": {
    "count": 64,
    "ratio": 0.0434
  },
  "5": {
    "count": 244,
    "ratio": 0.1656
  },
  "6": {
    "count": 222,
    "ratio": 0.1507
  },
  "2": {
    "count": 98,
    "ratio": 0.0665
  },
  "1": {
    "count": 146,
    "ratio": 0.0991
  },
  "3": {
    "count": 225,
    "ratio": 0.1527
  },
  "4": {
    "count": 125,
    "ratio": 0.0849
  },
  "8": {
    "count": 167,
    "ratio": 0.1134
  }
}
```

## Time Buckets

| Window | Samples | Online Top | Nearest Top | Match Ratio | Avg Distance |
|---|---:|---|---|---:|---:|
| `0-30` | `181` | `5` `0.4530` | `5` `0.3425` | `0.5304` | `2.514243` |
| `30-60` | `180` | `7` `0.7222` | `6` `0.4333` | `0.5333` | `2.724707` |
| `60-90` | `180` | `2` `0.2333` | `5` `0.2167` | `0.2667` | `2.091015` |
| `90-120` | `180` | `3` `0.4167` | `3` `0.3444` | `0.4389` | `2.228553` |
| `120-150` | `179` | `7` `0.4637` | `7` `0.2626` | `0.5475` | `2.125619` |
| `150-180` | `180` | `3` `0.3167` | `1` `0.2556` | `0.4444` | `2.264976` |
| `180-210` | `180` | `8` `0.2833` | `6` `0.2444` | `0.6167` | `2.176693` |
| `210-240` | `180` | `8` `0.3278` | `3` `0.2722` | `0.5889` | `2.400449` |
| `240-270` | `33` | `3` `0.3333` | `0` `0.2424` | `0.3030` | `2.491714` |

## Examples

- step `1` time `0.0333` online `2` conditioned_progress `0.0` nearest action `7` distance `2.139444` offline_time `293.8498`
- step `5` time `0.1667` online `2` conditioned_progress `0.000444` nearest action `0` distance `2.299743` offline_time `238.6887`
- step `10` time `0.3333` online `2` conditioned_progress `0.001` nearest action `0` distance `2.298974` offline_time `238.6887`
- step `15` time `0.5` online `2` conditioned_progress `0.001556` nearest action `5` distance `2.294235` offline_time `233.0208`
- step `20` time `0.6667` online `2` conditioned_progress `0.002111` nearest action `5` distance `2.28541` offline_time `233.0208`
- step `25` time `0.8333` online `2` conditioned_progress `0.002667` nearest action `5` distance `2.277582` offline_time `233.0208`
- step `30` time `1.0` online `2` conditioned_progress `0.003222` nearest action `6` distance `2.268629` offline_time `261.8576`
- step `35` time `1.1667` online `2` conditioned_progress `0.003778` nearest action `6` distance `2.260047` offline_time `261.8576`
- step `40` time `1.3333` online `2` conditioned_progress `0.004333` nearest action `0` distance `2.221226` offline_time `247.3572`
- step `45` time `1.5` online `2` conditioned_progress `0.004889` nearest action `0` distance `2.216098` offline_time `247.3572`
- step `50` time `1.6667` online `2` conditioned_progress `0.005444` nearest action `0` distance `2.21207` offline_time `247.3572`
- step `55` time `1.8333` online `2` conditioned_progress `0.006` nearest action `0` distance `2.209148` offline_time `247.3572`

## Limitations

- Nearest-neighbor trace comparison is diagnostic evidence only.
- It does not prove policy quality, Replay stability, balance, or fun.
