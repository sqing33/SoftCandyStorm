# Behavior Clone History Context Probe

- Gate decision: `history_context_probe_recorded_watch_only`
- Model: `harness/reports/2026-05-27_rl_route_recovery_aux_multimap_boundary_opening_ablation_001/no_class_weight_2_0/staged.pt`
- Trace samples: `142`
- Prefix frames: `7`

## Windows

| Window | Samples | Online | Nearest | Cold Top | Online-Prefix Top | Teacher-Prefix Top |
|---|---:|---|---|---|---|---|
| `0.0-20.0` | `60` | `3` 0.1667, `5` 0.4833, `6` 0.3500 | `3` 0.1667, `5` 0.3667, `4` 0.1167, `6` 0.3500 | `3` 0.1500, `5` 0.5000, `6` 0.3500 | `3` 0.1667, `5` 0.4833, `6` 0.3500 | `3` 0.2500, `6` 0.5167, `5` 0.1000, `4` 0.1333 |
| `20.0-40.0` | `61` | `6` 1.0000 | `6` 0.9672, `3` 0.0328 | `6` 1.0000 | `6` 1.0000 | `6` 1.0000 |
| `40.0-47.0` | `21` | `6` 1.0000 | `3` 0.0952, `6` 0.9048 | `6` 1.0000 | `6` 1.0000 | `6` 1.0000 |

## Examples

### `0.0-20.0`

- trace `0` time `0.0333` online `3` nearest `3` distance `0.000111`
  - `cold` top `3` score `0.491451` online_score `0.491451` nearest_score `0.491451`
  - `online_prefix` top `3` score `0.491451` online_score `0.491451` nearest_score `0.491451`
  - `teacher_prefix` top `3` score `0.491451` online_score `0.491451` nearest_score `0.491451`
- trace `1` time `0.3333` online `3` nearest `3` distance `0.292279`
  - `cold` top `3` score `0.745412` online_score `0.745412` nearest_score `0.745412`
  - `online_prefix` top `3` score `0.682492` online_score `0.682492` nearest_score `0.682492`
  - `teacher_prefix` top `3` score `0.682495` online_score `0.682495` nearest_score `0.682495`
- trace `2` time `0.6667` online `3` nearest `3` distance `0.29249`
  - `cold` top `3` score `0.736873` online_score `0.736873` nearest_score `0.736873`
  - `online_prefix` top `3` score `0.713172` online_score `0.713172` nearest_score `0.713172`
  - `teacher_prefix` top `3` score `0.722618` online_score `0.722618` nearest_score `0.722618`
- trace `3` time `1.0` online `3` nearest `3` distance `0.292794`
  - `cold` top `3` score `0.726617` online_score `0.726617` nearest_score `0.726617`
  - `online_prefix` top `3` score `0.735054` online_score `0.735054` nearest_score `0.735054`
  - `teacher_prefix` top `3` score `0.74848` online_score `0.74848` nearest_score `0.74848`
- trace `4` time `1.3333` online `3` nearest `3` distance `0.489747`
  - `cold` top `3` score `0.826399` online_score `0.826399` nearest_score `0.826399`
  - `online_prefix` top `3` score `0.804262` online_score `0.804262` nearest_score `0.804262`
  - `teacher_prefix` top `3` score `0.84348` online_score `0.84348` nearest_score `0.84348`

### `20.0-40.0`

- trace `60` time `20.0` online `6` nearest `6` distance `2.459713`
  - `cold` top `6` score `0.720728` online_score `0.720728` nearest_score `0.720728`
  - `online_prefix` top `6` score `0.711235` online_score `0.711235` nearest_score `0.711235`
  - `teacher_prefix` top `6` score `0.682882` online_score `0.682882` nearest_score `0.682882`
- trace `61` time `20.3334` online `6` nearest `6` distance `2.481441`
  - `cold` top `6` score `0.643211` online_score `0.643211` nearest_score `0.643211`
  - `online_prefix` top `6` score `0.693894` online_score `0.693894` nearest_score `0.693894`
  - `teacher_prefix` top `6` score `0.658684` online_score `0.658684` nearest_score `0.658684`
- trace `62` time `20.6667` online `6` nearest `6` distance `2.472526`
  - `cold` top `6` score `0.492994` online_score `0.492994` nearest_score `0.492994`
  - `online_prefix` top `6` score `0.643751` online_score `0.643751` nearest_score `0.643751`
  - `teacher_prefix` top `6` score `0.615263` online_score `0.615263` nearest_score `0.615263`
- trace `63` time `21.0` online `6` nearest `6` distance `2.509551`
  - `cold` top `6` score `0.505329` online_score `0.505329` nearest_score `0.505329`
  - `online_prefix` top `6` score `0.594239` online_score `0.594239` nearest_score `0.594239`
  - `teacher_prefix` top `6` score `0.613423` online_score `0.613423` nearest_score `0.613423`
- trace `64` time `21.3334` online `6` nearest `6` distance `2.535458`
  - `cold` top `6` score `0.491068` online_score `0.491068` nearest_score `0.491068`
  - `online_prefix` top `6` score `0.570101` online_score `0.570101` nearest_score `0.570101`
  - `teacher_prefix` top `6` score `0.6166` online_score `0.6166` nearest_score `0.6166`

### `40.0-47.0`

- trace `121` time `40.3331` online `6` nearest `3` distance `2.967865`
  - `cold` top `6` score `0.665504` online_score `0.665504` nearest_score `0.005835`
  - `online_prefix` top `6` score `0.658544` online_score `0.658544` nearest_score `0.005936`
  - `teacher_prefix` top `6` score `0.586087` online_score `0.586087` nearest_score `0.002278`
- trace `122` time `40.6664` online `6` nearest `3` distance `2.969809`
  - `cold` top `6` score `0.680543` online_score `0.680543` nearest_score `0.005357`
  - `online_prefix` top `6` score `0.667406` online_score `0.667406` nearest_score `0.005641`
  - `teacher_prefix` top `6` score `0.593998` online_score `0.593998` nearest_score `0.002205`
- trace `123` time `40.9997` online `6` nearest `6` distance `3.00688`
  - `cold` top `6` score `0.665815` online_score `0.665815` nearest_score `0.665815`
  - `online_prefix` top `6` score `0.670553` online_score `0.670553` nearest_score `0.670553`
  - `teacher_prefix` top `6` score `0.634726` online_score `0.634726` nearest_score `0.634726`
- trace `124` time `41.333` online `6` nearest `6` distance `3.105936`
  - `cold` top `6` score `0.678718` online_score `0.678718` nearest_score `0.678718`
  - `online_prefix` top `6` score `0.677882` online_score `0.677882` nearest_score `0.677882`
  - `teacher_prefix` top `6` score `0.646741` online_score `0.646741` nearest_score `0.646741`
- trace `125` time `41.6664` online `6` nearest `6` distance `3.125139`
  - `cold` top `6` score `0.669215` online_score `0.669215` nearest_score `0.669215`
  - `online_prefix` top `6` score `0.684116` online_score `0.684116` nearest_score `0.684116`
  - `teacher_prefix` top `6` score `0.653013` online_score `0.653013` nearest_score `0.653013`

## Limitations

- History context probing is diagnostic evidence only.
- It compares observation history prefixes, not supervised training or policy acceptance.
- It does not replace deterministic high-pressure gates, Replay, or human playtest.
