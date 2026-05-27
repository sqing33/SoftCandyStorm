# Behavior Clone Trace Dataset Comparison

- Gate decision: `trace_dataset_nearest_neighbor_recorded_watch_only`
- Trace samples: `151`
- Offline candidates: `1848`
- Same map only: `True`
- Offline window: `0.0` to `60.0`
- Phase duration conditioning: `300.0`
- Nearest target matches online action ratio: `0.9735`
- Online normalized action entropy: `0.0`
- Nearest distance average: `0.76155`

## Action Distributions

### Online

```json
{
  "3": {
    "count": 151,
    "ratio": 1.0
  }
}
```

### Nearest Offline Target

```json
{
  "3": {
    "count": 147,
    "ratio": 0.9735
  },
  "5": {
    "count": 4,
    "ratio": 0.0265
  }
}
```

## Examples

- step `1` time `0.0333` online `3` conditioned_progress `0.000111` nearest action `3` distance `0.000111` offline_time `0.0`
- step `2` time `0.0667` online `3` conditioned_progress `0.000222` nearest action `3` distance `0.229375` offline_time `0.3333`
- step `3` time `0.1` online `3` conditioned_progress `0.000333` nearest action `3` distance `0.227688` offline_time `0.3333`
- step `4` time `0.1333` online `3` conditioned_progress `0.000444` nearest action `3` distance `0.226594` offline_time `0.3333`
- step `5` time `0.1667` online `3` conditioned_progress `0.000556` nearest action `3` distance `0.226105` offline_time `0.3333`
- step `6` time `0.2` online `3` conditioned_progress `0.000667` nearest action `3` distance `0.226226` offline_time `0.3333`
- step `7` time `0.2333` online `3` conditioned_progress `0.000778` nearest action `3` distance `0.22696` offline_time `0.3333`
- step `8` time `0.2667` online `3` conditioned_progress `0.000889` nearest action `3` distance `0.227351` offline_time `0.3333`
- step `9` time `0.3` online `3` conditioned_progress `0.001` nearest action `3` distance `0.229304` offline_time `0.3333`
- step `10` time `0.3333` online `3` conditioned_progress `0.001111` nearest action `3` distance `0.23185` offline_time `0.3333`
- step `11` time `0.3667` online `3` conditioned_progress `0.001222` nearest action `3` distance `0.234973` offline_time `0.3333`
- step `12` time `0.4` online `3` conditioned_progress `0.001333` nearest action `3` distance `0.238654` offline_time `0.3333`

## Limitations

- Nearest-neighbor trace comparison is diagnostic evidence only.
- It does not prove policy quality, Replay stability, balance, or fun.
