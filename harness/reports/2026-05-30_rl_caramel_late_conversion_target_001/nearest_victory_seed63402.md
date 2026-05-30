# Behavior Clone Teacher Sequence Diagnostic

- Gate decision: `teacher_sequence_diagnostic_recorded_watch_only`
- Trace samples: `1473`
- Offline candidates: `180`
- Same map only: `True`
- Phase duration conditioning: `300.0`

## Windows

| Window | Samples | Online | Nearest | Match Ratio | Avg Distance |
|---|---:|---|---|---:|---:|
| `210.0-300.0` | `213` | `8` 0.3099, `1` 0.1596, `2` 0.0188, `3` 0.2723, `5` 0.1878, `6` 0.0141, `7` 0.0188, `4` 0.0188 | `7` 0.0329, `1` 0.6009, `2` 0.1737, `8` 0.0704, `3` 0.0094, `6` 0.0657, `5` 0.0188, `4` 0.0282 | `0.1690` | `3.694926` |

## Examples

### `210.0-300.0`

- trace `1260` time `210.0159` online `8` nearest `7` seed `62301` offline_time `236.0214` distance `2.900263`
  - online sequence: `209.5158:8 209.6825:8 209.8492:8 210.0159:8 210.1826:8 210.3493:8 210.516:8`
  - teacher sequence: `235.5214:7 235.6881:7 235.8547:7 236.0214:7 236.1882:7 236.3549:7 236.5216:7`
- trace `1261` time `210.1826` online `8` nearest `7` seed `62301` offline_time `236.3549` distance `3.410375`
  - online sequence: `209.6825:8 209.8492:8 210.0159:8 210.1826:8 210.3493:8 210.516:8 210.6827:8`
  - teacher sequence: `235.8547:7 236.0214:7 236.1882:7 236.3549:7 236.5216:7 236.6883:7 236.855:7`
- trace `1262` time `210.3493` online `8` nearest `1` seed `62301` offline_time `212.5164` distance `3.379928`
  - online sequence: `209.8492:8 210.0159:8 210.1826:8 210.3493:8 210.516:8 210.6827:8 210.8494:8`
  - teacher sequence: `212.0163:1 212.183:1 212.3497:1 212.5164:1 212.6831:1 212.8498:1 213.0165:1`
- trace `1263` time `210.516` online `8` nearest `7` seed `62301` offline_time `236.6883` distance `3.582837`
  - online sequence: `210.0159:8 210.1826:8 210.3493:8 210.516:8 210.6827:8 210.8494:8 211.0161:8`
  - teacher sequence: `236.1882:7 236.3549:7 236.5216:7 236.6883:7 236.855:7 237.0217:6 237.1884:6`
- trace `1264` time `210.6827` online `8` nearest `1` seed `62301` offline_time `212.183` distance `3.074877`
  - online sequence: `210.1826:8 210.3493:8 210.516:8 210.6827:8 210.8494:8 211.0161:8 211.1828:8`
  - teacher sequence: `211.6829:1 211.8496:1 212.0163:1 212.183:1 212.3497:1 212.5164:1 212.6831:1`
- trace `1265` time `210.8494` online `8` nearest `1` seed `62301` offline_time `212.183` distance `3.054115`
  - online sequence: `210.3493:8 210.516:8 210.6827:8 210.8494:8 211.0161:8 211.1828:8 211.3495:8`
  - teacher sequence: `211.6829:1 211.8496:1 212.0163:1 212.183:1 212.3497:1 212.5164:1 212.6831:1`

## Limitations

- Teacher sequence inspection is diagnostic evidence only.
- Nearest observations may come from different episodes and do not prove policy quality.
- This does not replace deterministic high-pressure gates, Replay, or human playtest.
