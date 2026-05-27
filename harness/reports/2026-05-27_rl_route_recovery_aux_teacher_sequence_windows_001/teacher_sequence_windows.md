# Behavior Clone Teacher Sequence Diagnostic

- Gate decision: `teacher_sequence_diagnostic_recorded_watch_only`
- Trace samples: `182`
- Offline candidates: `1848`
- Same map only: `True`
- Phase duration conditioning: `300.0`

## Windows

| Window | Samples | Online | Nearest | Match Ratio | Avg Distance |
|---|---:|---|---|---:|---:|
| `25.0-30.0` | `16` | `5` 1.0000 | `4` 0.0625, `3` 0.6875, `8` 0.2500 | `0.0000` | `1.767452` |
| `30.0-35.0` | `15` | `5` 1.0000 | `3` 0.0667, `8` 0.8000, `4` 0.1333 | `0.0000` | `2.020581` |
| `55.0-60.0` | `15` | `3` 1.0000 | `5` 0.1333, `3` 0.2667, `2` 0.6000 | `0.2667` | `1.645669` |

## Examples

### `25.0-30.0`

- trace `75` time `25.0` online `5` nearest `4` seed `48003` offline_time `30.6665` distance `1.807693`
  - online sequence: `23.6666:5 24.0:5 24.3333:5 24.6666:5 25.0:5 25.3333:5 25.6666:5 25.9999:5 26.3333:5`
  - teacher sequence: `29.3332:3 29.6666:3 29.9999:1 30.3332:3 30.6665:4 30.9999:3 31.3332:5 31.6665:5 31.9999:5`
- trace `76` time `25.3333` online `5` nearest `3` seed `48003` offline_time `40.9997` distance `1.624123`
  - online sequence: `24.0:5 24.3333:5 24.6666:5 25.0:5 25.3333:5 25.6666:5 25.9999:5 26.3333:5 26.6666:5`
  - teacher sequence: `39.6664:5 39.9997:3 40.3331:3 40.6664:5 40.9997:3 41.333:3 41.6664:3 41.9997:3 42.333:3`
- trace `77` time `25.6666` online `5` nearest `3` seed `48003` offline_time `38.3331` distance `1.540323`
  - online sequence: `24.3333:5 24.6666:5 25.0:5 25.3333:5 25.6666:5 25.9999:5 26.3333:5 26.6666:5 26.9999:5`
  - teacher sequence: `36.9998:3 37.3331:3 37.6664:3 37.9998:3 38.3331:3 38.6664:3 38.9997:5 39.3331:3 39.6664:5`
- trace `78` time `25.9999` online `5` nearest `3` seed `48003` offline_time `38.3331` distance `1.61126`
  - online sequence: `24.6666:5 25.0:5 25.3333:5 25.6666:5 25.9999:5 26.3333:5 26.6666:5 26.9999:5 27.3333:5`
  - teacher sequence: `36.9998:3 37.3331:3 37.6664:3 37.9998:3 38.3331:3 38.6664:3 38.9997:5 39.3331:3 39.6664:5`

### `30.0-35.0`

- trace `91` time `30.3332` online `5` nearest `3` seed `48003` offline_time `38.3331` distance `1.771698`
  - online sequence: `28.9999:5 29.3332:5 29.6666:5 29.9999:5 30.3332:5 30.6665:5 30.9999:5 31.3332:5 31.6665:5`
  - teacher sequence: `36.9998:3 37.3331:3 37.6664:3 37.9998:3 38.3331:3 38.6664:3 38.9997:5 39.3331:3 39.6664:5`
- trace `92` time `30.6665` online `5` nearest `8` seed `62302` offline_time `23.0` distance `1.897194`
  - online sequence: `29.3332:5 29.6666:5 29.9999:5 30.3332:5 30.6665:5 30.9999:5 31.3332:5 31.6665:5 31.9999:5`
  - teacher sequence: `18.0001:8 19.0001:8 20.0:8 22.0:8 23.0:8 24.0:8 25.0:8 25.9999:8 26.9999:8`
- trace `93` time `30.9999` online `5` nearest `8` seed `62302` offline_time `18.0001` distance `2.089435`
  - online sequence: `29.6666:5 29.9999:5 30.3332:5 30.6665:5 30.9999:5 31.3332:5 31.6665:5 31.9999:5 32.3332:5`
  - teacher sequence: `14.0001:5 15.0001:8 16.0001:8 17.0001:8 18.0001:8 19.0001:8 20.0:8 22.0:8 23.0:8`
- trace `94` time `31.3332` online `5` nearest `8` seed `62302` offline_time `18.0001` distance `2.111145`
  - online sequence: `29.9999:5 30.3332:5 30.6665:5 30.9999:5 31.3332:5 31.6665:5 31.9999:5 32.3332:5 32.6665:5`
  - teacher sequence: `14.0001:5 15.0001:8 16.0001:8 17.0001:8 18.0001:8 19.0001:8 20.0:8 22.0:8 23.0:8`

### `55.0-60.0`

- trace `166` time `55.3328` online `3` nearest `5` seed `62301` offline_time `13.0001` distance `1.884418`
  - online sequence: `53.9995:3 54.3328:3 54.6662:3 54.9995:3 55.3328:3 55.6662:3 55.9995:3 56.3328:3 56.6661:3`
  - teacher sequence: `9.0:5 10.0:5 11.0:5 12.0:5 13.0001:5 14.0001:5 15.0001:5 16.0001:5 17.0001:8`
- trace `167` time `55.6662` online `3` nearest `5` seed `62301` offline_time `13.0001` distance `1.889023`
  - online sequence: `54.3328:3 54.6662:3 54.9995:3 55.3328:3 55.6662:3 55.9995:3 56.3328:3 56.6661:3 56.9995:3`
  - teacher sequence: `9.0:5 10.0:5 11.0:5 12.0:5 13.0001:5 14.0001:5 15.0001:5 16.0001:5 17.0001:8`
- trace `169` time `56.3328` online `3` nearest `2` seed `48009` offline_time `56.3328` distance `1.768087`
  - online sequence: `54.9995:3 55.3328:3 55.6662:3 55.9995:3 56.3328:3 56.6661:3 56.9995:3 57.3328:3 57.6661:3`
  - teacher sequence: `54.9995:2 55.3328:2 55.6662:2 55.9995:2 56.3328:2 56.6661:2 56.9995:2 57.3328:2 57.6661:3`
- trace `170` time `56.6661` online `3` nearest `2` seed `48009` offline_time `56.3328` distance `1.768212`
  - online sequence: `55.3328:3 55.6662:3 55.9995:3 56.3328:3 56.6661:3 56.9995:3 57.3328:3 57.6661:3 57.9995:3`
  - teacher sequence: `54.9995:2 55.3328:2 55.6662:2 55.9995:2 56.3328:2 56.6661:2 56.9995:2 57.3328:2 57.6661:3`

## Limitations

- Teacher sequence inspection is diagnostic evidence only.
- Nearest observations may come from different episodes and do not prove policy quality.
- This does not replace deterministic high-pressure gates, Replay, or human playtest.
