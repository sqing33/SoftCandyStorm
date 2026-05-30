# Behavior Clone Teacher Sequence Diagnostic

- Gate decision: `teacher_sequence_diagnostic_recorded_watch_only`
- Trace samples: `1281`
- Offline candidates: `180`
- Same map only: `True`
- Phase duration conditioning: `300.0`

## Windows

| Window | Samples | Online | Nearest | Match Ratio | Avg Distance |
|---|---:|---|---|---:|---:|
| `210.0-300.0` | `21` | `5` 1.0000 | `8` 0.0476, `1` 0.5714, `2` 0.1429, `4` 0.2381 | `0.0000` | `4.546150` |

## Examples

### `210.0-300.0`

- trace `1260` time `210.0159` online `5` nearest `8` seed `62301` offline_time `239.0221` distance `4.449648`
  - online sequence: `209.5158:5 209.6825:5 209.8492:5 210.0159:5 210.1826:5 210.3493:5 210.516:5`
  - teacher sequence: `238.522:8 238.6887:8 238.8554:8 239.0221:8 239.1888:8 239.3555:1 239.5222:1`
- trace `1261` time `210.1826` online `5` nearest `1` seed `62301` offline_time `213.6833` distance `4.851069`
  - online sequence: `209.6825:5 209.8492:5 210.0159:5 210.1826:5 210.3493:5 210.516:5 210.6827:5`
  - teacher sequence: `213.1832:1 213.35:1 213.5166:1 213.6833:1 213.8501:2 214.0168:2 214.1835:2`
- trace `1262` time `210.3493` online `5` nearest `1` seed `62301` offline_time `213.6833` distance `4.82305`
  - online sequence: `209.8492:5 210.0159:5 210.1826:5 210.3493:5 210.516:5 210.6827:5 210.8494:5`
  - teacher sequence: `213.1832:1 213.35:1 213.5166:1 213.6833:1 213.8501:2 214.0168:2 214.1835:2`
- trace `1263` time `210.516` online `5` nearest `1` seed `62301` offline_time `213.6833` distance `4.823522`
  - online sequence: `210.0159:5 210.1826:5 210.3493:5 210.516:5 210.6827:5 210.8494:5 211.0161:5`
  - teacher sequence: `213.1832:1 213.35:1 213.5166:1 213.6833:1 213.8501:2 214.0168:2 214.1835:2`
- trace `1264` time `210.6827` online `5` nearest `1` seed `62301` offline_time `213.6833` distance `4.812379`
  - online sequence: `210.1826:5 210.3493:5 210.516:5 210.6827:5 210.8494:5 211.0161:5 211.1828:5`
  - teacher sequence: `213.1832:1 213.35:1 213.5166:1 213.6833:1 213.8501:2 214.0168:2 214.1835:2`
- trace `1265` time `210.8494` online `5` nearest `1` seed `62301` offline_time `216.5173` distance `4.918488`
  - online sequence: `210.3493:5 210.516:5 210.6827:5 210.8494:5 211.0161:5 211.1828:5 211.3495:5`
  - teacher sequence: `216.0172:1 216.1839:1 216.3506:1 216.5173:1 216.684:2 216.8507:4 217.0174:2`

## Limitations

- Teacher sequence inspection is diagnostic evidence only.
- Nearest observations may come from different episodes and do not prove policy quality.
- This does not replace deterministic high-pressure gates, Replay, or human playtest.
