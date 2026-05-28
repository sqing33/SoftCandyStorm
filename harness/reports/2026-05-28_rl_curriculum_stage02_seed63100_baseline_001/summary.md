# Stage 02 Seed 63100 Baseline

## 结论

- Gate decision: `stage02_seed63100_baseline_recorded`
- Model: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Seed start: `63100`
- Seeds: `3`
- Purpose: fixed-window no-regression baseline for later probes

本报告补录 stage 02 PPO checkpoint 在 `seed_start 63100`、high-pressure 三图、`60s/180s/300s` 固定窗口下的 baseline。此前部分 window regression 报告把 stage 02 的 `seed_start 62800` 对比结果与后续 `63100` probe 直接比较；这种跨 seed 摘要比较只能作为诊断，不能作为严格 no-regression。

## Deterministic High-pressure Baseline

| Window | Soda | Caramel | Cracked |
| --- | ---: | ---: | ---: |
| `60s` | `1.0` | `0.6667` | `1.0` |
| `180s` | `0.3333` | `0.6667` | `0.6667` |
| `300s` | `0.0` | `0.0` | `0.0` |

## 平均存活

| Window | Soda | Caramel | Cracked |
| --- | ---: | ---: | ---: |
| `60s` | `60.0328` | `49.3329` | `60.0328` |
| `180s` | `115.7803` | `129.3174` | `157.4948` |
| `300s` | `133.105` | `154.2116` | `198.259` |

## 判断

- Stage 02 在 `63100-63102` seed 窗口本身仍有明显缺口，尤其是 300 秒三图全 `0.0` 胜率。
- 后续 `63100-63102` probe 的 no-regression 应使用本目录报告，而不是 stage 02 原始 `62800-62802` 报告。
- 该 baseline 不改变当前 RL acceptance 状态：stage 02 仍不是 RL test Bot candidate。

## 输出文件

- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
