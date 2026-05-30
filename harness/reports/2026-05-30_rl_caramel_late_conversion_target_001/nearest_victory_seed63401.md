# Behavior Clone Teacher Sequence Diagnostic

- Gate decision: `teacher_sequence_diagnostic_recorded_watch_only`
- Trace samples: `1413`
- Offline candidates: `180`
- Same map only: `True`
- Phase duration conditioning: `300.0`

## Windows

| Window | Samples | Online | Nearest | Match Ratio | Avg Distance |
|---|---:|---|---|---:|---:|
| `210.0-300.0` | `153` | `3` 0.1699, `4` 0.0588, `5` 0.1242, `7` 0.2941, `2` 0.0784, `8` 0.1046, `1` 0.1699 | `7` 0.0261, `2` 0.3399, `1` 0.5686, `8` 0.0327, `4` 0.0327 | `0.1569` | `3.389727` |

## Examples

### `210.0-300.0`

- trace `1260` time `210.0159` online `3` nearest `7` seed `62301` offline_time `235.0212` distance `2.645768`
  - online sequence: `209.5158:4 209.6825:4 209.8492:4 210.0159:3 210.1826:3 210.3493:3 210.516:3`
  - teacher sequence: `234.5211:8 234.6878:8 234.8545:8 235.0212:7 235.1879:7 235.3546:7 235.5214:7`
- trace `1261` time `210.1826` online `3` nearest `2` seed `62301` offline_time `214.5169` distance `3.211575`
  - online sequence: `209.6825:4 209.8492:4 210.0159:3 210.1826:3 210.3493:3 210.516:3 210.6827:3`
  - teacher sequence: `214.0168:2 214.1835:2 214.3502:2 214.5169:2 214.6836:2 214.8503:2 215.017:2`
- trace `1262` time `210.3493` online `3` nearest `2` seed `62301` offline_time `214.5169` distance `3.213213`
  - online sequence: `209.8492:4 210.0159:3 210.1826:3 210.3493:3 210.516:3 210.6827:3 210.8494:3`
  - teacher sequence: `214.0168:2 214.1835:2 214.3502:2 214.5169:2 214.6836:2 214.8503:2 215.017:2`
- trace `1263` time `210.516` online `3` nearest `2` seed `62301` offline_time `214.1835` distance `3.178154`
  - online sequence: `210.0159:3 210.1826:3 210.3493:3 210.516:3 210.6827:3 210.8494:3 211.0161:3`
  - teacher sequence: `213.6833:1 213.8501:2 214.0168:2 214.1835:2 214.3502:2 214.5169:2 214.6836:2`
- trace `1264` time `210.6827` online `3` nearest `2` seed `62301` offline_time `214.1835` distance `3.173342`
  - online sequence: `210.1826:3 210.3493:3 210.516:3 210.6827:3 210.8494:3 211.0161:3 211.1828:3`
  - teacher sequence: `213.6833:1 213.8501:2 214.0168:2 214.1835:2 214.3502:2 214.5169:2 214.6836:2`
- trace `1265` time `210.8494` online `3` nearest `2` seed `62301` offline_time `214.1835` distance `3.222862`
  - online sequence: `210.3493:3 210.516:3 210.6827:3 210.8494:3 211.0161:3 211.1828:3 211.3495:4`
  - teacher sequence: `213.6833:1 213.8501:2 214.0168:2 214.1835:2 214.3502:2 214.5169:2 214.6836:2`

## Limitations

- Teacher sequence inspection is diagnostic evidence only.
- Nearest observations may come from different episodes and do not prove policy quality.
- This does not replace deterministic high-pressure gates, Replay, or human playtest.
