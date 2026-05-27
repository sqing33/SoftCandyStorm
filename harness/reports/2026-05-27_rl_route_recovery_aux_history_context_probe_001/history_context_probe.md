# Behavior Clone History Context Probe

- Gate decision: `history_context_probe_recorded_watch_only`
- Model: `harness/reports/2026-05-27_rl_route_recovery_aux_entropy_retry_001/staged.pt`
- Trace samples: `182`
- Prefix frames: `7`

## Windows

| Window | Samples | Online | Nearest | Cold Top | Online-Prefix Top | Teacher-Prefix Top |
|---|---:|---|---|---|---|---|
| `30.0-35.0` | `15` | `5` 1.0000 | `3` 0.0667, `8` 0.8000, `4` 0.1333 | `5` 1.0000 | `5` 1.0000 | `5` 0.8667, `6` 0.1333 |
| `55.0-60.0` | `15` | `3` 1.0000 | `5` 0.1333, `3` 0.2667, `2` 0.6000 | `3` 1.0000 | `3` 1.0000 | `4` 0.1333, `3` 0.2667, `2` 0.6000 |

## Examples

### `30.0-35.0`

- trace `91` time `30.3332` online `5` nearest `3` distance `1.771698`
  - `cold` top `5` score `0.569483` online_score `0.569483` nearest_score `0.022466`
  - `online_prefix` top `5` score `0.571831` online_score `0.571831` nearest_score `0.024836`
  - `teacher_prefix` top `5` score `0.507306` online_score `0.507306` nearest_score `0.124946`
- trace `92` time `30.6665` online `5` nearest `8` distance `1.897194`
  - `cold` top `5` score `0.522194` online_score `0.522194` nearest_score `0.001726`
  - `online_prefix` top `5` score `0.532767` online_score `0.532767` nearest_score `0.001767`
  - `teacher_prefix` top `5` score `0.547163` online_score `0.547163` nearest_score `0.001306`
- trace `93` time `30.9999` online `5` nearest `8` distance `2.089435`
  - `cold` top `5` score `0.498381` online_score `0.498381` nearest_score `0.001923`
  - `online_prefix` top `5` score `0.508195` online_score `0.508195` nearest_score `0.001888`
  - `teacher_prefix` top `5` score `0.513913` online_score `0.513913` nearest_score `0.001764`
- trace `94` time `31.3332` online `5` nearest `8` distance `2.111145`
  - `cold` top `5` score `0.520004` online_score `0.520004` nearest_score `0.001351`
  - `online_prefix` top `5` score `0.515487` online_score `0.515487` nearest_score `0.001583`
  - `teacher_prefix` top `5` score `0.527455` online_score `0.527455` nearest_score `0.001445`
- trace `95` time `31.6665` online `5` nearest `8` distance `2.112812`
  - `cold` top `5` score `0.518494` online_score `0.518494` nearest_score `0.001376`
  - `online_prefix` top `5` score `0.516464` online_score `0.516464` nearest_score `0.001462`
  - `teacher_prefix` top `5` score `0.52658` online_score `0.52658` nearest_score `0.001461`

### `55.0-60.0`

- trace `166` time `55.3328` online `3` nearest `5` distance `1.884418`
  - `cold` top `3` score `0.482556` online_score `0.482556` nearest_score `0.10464`
  - `online_prefix` top `3` score `0.500821` online_score `0.500821` nearest_score `0.067493`
  - `teacher_prefix` top `4` score `0.339159` online_score `0.308892` nearest_score `0.265997`
- trace `167` time `55.6662` online `3` nearest `5` distance `1.889023`
  - `cold` top `3` score `0.481032` online_score `0.481032` nearest_score `0.104589`
  - `online_prefix` top `3` score `0.494423` online_score `0.494423` nearest_score `0.080614`
  - `teacher_prefix` top `4` score `0.339382` online_score `0.307901` nearest_score `0.266461`
- trace `168` time `55.9995` online `3` nearest `3` distance `1.654736`
  - `cold` top `3` score `0.43116` online_score `0.43116` nearest_score `0.43116`
  - `online_prefix` top `3` score `0.440572` online_score `0.440572` nearest_score `0.440572`
  - `teacher_prefix` top `3` score `0.379875` online_score `0.379875` nearest_score `0.379875`
- trace `169` time `56.3328` online `3` nearest `2` distance `1.768087`
  - `cold` top `3` score `0.461851` online_score `0.461851` nearest_score `0.23417`
  - `online_prefix` top `3` score `0.458859` online_score `0.458859` nearest_score `0.166136`
  - `teacher_prefix` top `2` score `0.363116` online_score `0.360673` nearest_score `0.363116`
- trace `170` time `56.6661` online `3` nearest `2` distance `1.768212`
  - `cold` top `3` score `0.460924` online_score `0.460924` nearest_score `0.2349`
  - `online_prefix` top `3` score `0.466048` online_score `0.466048` nearest_score `0.190682`
  - `teacher_prefix` top `2` score `0.363583` online_score `0.360012` nearest_score `0.363583`

## Limitations

- History context probing is diagnostic evidence only.
- It compares observation history prefixes, not supervised training or policy acceptance.
- It does not replace deterministic high-pressure gates, Replay, or human playtest.
