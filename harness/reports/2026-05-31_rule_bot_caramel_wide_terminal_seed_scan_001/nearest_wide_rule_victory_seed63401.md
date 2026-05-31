# Behavior Clone Trace Dataset Comparison

- Gate decision: `trace_dataset_nearest_neighbor_recorded_watch_only`
- Trace samples: `1413`
- Offline candidates: `45853`
- Same map only: `True`
- Offline window: `210.0` to `300.0`
- Phase duration conditioning: `None`
- Nearest target matches online action ratio: `0.5534`
- Online normalized action entropy: `0.8515`
- Nearest distance average: `2.252513`

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
    "to_action": 3
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
    "count": 292,
    "ratio": 0.2067
  },
  "3": {
    "count": 129,
    "ratio": 0.0913
  },
  "0": {
    "count": 67,
    "ratio": 0.0474
  },
  "2": {
    "count": 184,
    "ratio": 0.1302
  },
  "8": {
    "count": 155,
    "ratio": 0.1097
  },
  "1": {
    "count": 232,
    "ratio": 0.1642
  },
  "6": {
    "count": 84,
    "ratio": 0.0594
  },
  "5": {
    "count": 162,
    "ratio": 0.1146
  },
  "4": {
    "count": 108,
    "ratio": 0.0764
  }
}
```

## Time Buckets

| Window | Samples | Online Top | Nearest Top | Match Ratio | Avg Distance |
|---|---:|---|---|---:|---:|
| `0-30` | `181` | `2` `0.8564` | `2` `0.6906` | `0.7901` | `2.360525` |
| `30-60` | `180` | `7` `1.0000` | `7` `0.3889` | `0.3889` | `2.486245` |
| `60-90` | `180` | `7` `0.3222` | `7` `0.3833` | `0.6000` | `2.335292` |
| `90-120` | `180` | `3` `0.4167` | `1` `0.1778` | `0.2944` | `2.160268` |
| `120-150` | `179` | `7` `0.3073` | `7` `0.2067` | `0.4581` | `2.198449` |
| `150-180` | `180` | `8` `0.3056` | `5` `0.2444` | `0.5444` | `2.157412` |
| `180-210` | `180` | `5` `0.3000` | `1` `0.2444` | `0.6889` | `1.903049` |
| `210-240` | `153` | `7` `0.2941` | `1` `0.2353` | `0.6797` | `2.447159` |

## Examples

- step `1` time `0.0333` online `2` conditioned_progress `0.0` nearest action `7` distance `2.139444` offline_time `293.8498`
- step `5` time `0.1667` online `2` conditioned_progress `0.000444` nearest action `3` distance `2.298825` offline_time `229.02`
- step `10` time `0.3333` online `2` conditioned_progress `0.001` nearest action `3` distance `2.289969` offline_time `229.02`
- step `15` time `0.5` online `2` conditioned_progress `0.001556` nearest action `3` distance `2.282876` offline_time `229.02`
- step `20` time `0.6667` online `2` conditioned_progress `0.002111` nearest action `3` distance `2.276774` offline_time `229.02`
- step `25` time `0.8333` online `2` conditioned_progress `0.002667` nearest action `0` distance `2.336062` offline_time `241.6893`
- step `30` time `1.0` online `2` conditioned_progress `0.003222` nearest action `0` distance `2.32321` offline_time `241.6893`
- step `35` time `1.1667` online `2` conditioned_progress `0.003778` nearest action `0` distance `2.312198` offline_time `241.6893`
- step `40` time `1.3333` online `2` conditioned_progress `0.004333` nearest action `2` distance `2.312456` offline_time `280.1865`
- step `45` time `1.5` online `2` conditioned_progress `0.004889` nearest action `3` distance `2.186206` offline_time `229.02`
- step `50` time `1.6667` online `2` conditioned_progress `0.005444` nearest action `3` distance `2.18511` offline_time `229.02`
- step `55` time `1.8333` online `2` conditioned_progress `0.006` nearest action `3` distance `2.185152` offline_time `229.02`

## Limitations

- Nearest-neighbor trace comparison is diagnostic evidence only.
- It does not prove policy quality, Replay stability, balance, or fun.
