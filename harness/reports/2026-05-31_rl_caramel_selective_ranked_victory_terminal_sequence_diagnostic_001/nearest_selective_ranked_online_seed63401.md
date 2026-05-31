# Behavior Clone Trace Dataset Comparison

- Gate decision: `trace_dataset_nearest_neighbor_recorded_watch_only`
- Trace samples: `1413`
- Offline candidates: `3237`
- Same map only: `True`
- Offline window: `210.0` to `300.0`
- Phase duration conditioning: `None`
- Nearest target matches online action ratio: `0.8634`
- Online normalized action entropy: `0.8508`
- Nearest distance average: `2.425201`

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
    "to_action": 2
  }
}
```

## Action Distributions

### Online

```json
{
  "2": {
    "count": 176,
    "ratio": 0.1246
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
    "count": 109,
    "ratio": 0.0771
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
    "count": 342,
    "ratio": 0.242
  },
  "2": {
    "count": 214,
    "ratio": 0.1515
  },
  "3": {
    "count": 158,
    "ratio": 0.1118
  },
  "1": {
    "count": 194,
    "ratio": 0.1373
  },
  "4": {
    "count": 111,
    "ratio": 0.0786
  },
  "8": {
    "count": 126,
    "ratio": 0.0892
  },
  "6": {
    "count": 34,
    "ratio": 0.0241
  },
  "5": {
    "count": 234,
    "ratio": 0.1656
  }
}
```

## Time Buckets

| Window | Samples | Online Top | Nearest Top | Match Ratio | Avg Distance |
|---|---:|---|---|---:|---:|
| `0-30` | `181` | `2` `0.8564` | `2` `0.7735` | `0.9116` | `2.479025` |
| `30-60` | `180` | `7` `1.0000` | `7` `0.8222` | `0.8222` | `2.864071` |
| `60-90` | `180` | `7` `0.3222` | `7` `0.3000` | `0.7389` | `2.587573` |
| `90-120` | `180` | `3` `0.4167` | `3` `0.3778` | `0.9333` | `2.340390` |
| `120-150` | `179` | `7` `0.3073` | `7` `0.3296` | `0.9274` | `2.347853` |
| `150-180` | `180` | `8` `0.3056` | `8` `0.2778` | `0.8944` | `2.305551` |
| `180-210` | `180` | `5` `0.3000` | `5` `0.3222` | `0.8611` | `1.994330` |
| `210-240` | `153` | `7` `0.2941` | `1` `0.2026` | `0.8105` | `2.492119` |

## Examples

- step `1` time `0.0333` online `2` conditioned_progress `0.0` nearest action `7` distance `2.73355` offline_time `258.1919`
- step `5` time `0.1667` online `2` conditioned_progress `0.000444` nearest action `2` distance `2.607132` offline_time `265.8567`
- step `10` time `0.3333` online `2` conditioned_progress `0.001` nearest action `2` distance `2.59785` offline_time `265.8567`
- step `15` time `0.5` online `2` conditioned_progress `0.001556` nearest action `2` distance `2.590498` offline_time `265.8567`
- step `20` time `0.6667` online `2` conditioned_progress `0.002111` nearest action `2` distance `2.584158` offline_time `265.8567`
- step `25` time `0.8333` online `2` conditioned_progress `0.002667` nearest action `2` distance `2.694771` offline_time `265.8567`
- step `30` time `1.0` online `2` conditioned_progress `0.003222` nearest action `2` distance `2.690048` offline_time `265.8567`
- step `35` time `1.1667` online `2` conditioned_progress `0.003778` nearest action `2` distance `2.687755` offline_time `265.8567`

## Limitations

- Nearest-neighbor trace comparison is diagnostic evidence only.
- It does not prove policy quality, Replay stability, balance, or fun.
