# RL Expanded Clean Teacher Late Survival Staged GRU Context8

- Gate decision: `repair_expanded_clean_teacher_300s_late_gap`
- Model: `harness/reports/2026-05-27_rl_behavior_clone_late_survival_clean_teacher_expanded_staged_gru_context8_001/staged.pt`
- Failure case: `harness/failed_cases/fail_20260527_033_expanded_clean_teacher_late_survival_regression.json`

## Dataset

This run extends the clean teacher late survival dataset with the additional `caramel-workshop` TankBot victory at seed `62405`. It still uses only real rule Bot `180-300s` trajectories and does not include stochastic watch evidence, adapter-derived samples, edge recovery samples, or risk recovery samples.

| Source | Samples | Episodes | Notes |
|---|---:|---:|---|
| `kite_soda_creek_late_180_300.jsonl` | 3128 | 5 | 4 victories |
| `kite_cracked_star_jar_late_180_300.jsonl` | 2276 | 5 | 2 victories |
| `tank_caramel_workshop_seed62301_late_180_300.jsonl` | 720 | 1 | 1 victory |
| `tank_caramel_workshop_seed62405_late_180_300.jsonl` | 719 | 1 | 1 victory |
| Total expanded clean teacher | 6843 | 12 | 100% clean trajectory samples |

The added seed raises `caramel-workshop` coverage from `11.76%` to `21.03%`, while `soda-creek` remains `45.71%` and `cracked-star-jar` remains `33.26%`.

## Training

The late submodel keeps the previous clean-teacher settings: GRU context8, `map-conditioning = one_hot`, `time-phase-conditioning = one_hot`, `time-phase-filter = late`, inverse-frequency class weighting, `danger_action_change` sample weighting, and `entropy_regularization = 0.02`.

| Model | Validation Accuracy | Validation Entropy |
|---|---:|---:|
| `late.pt` | 0.7633 | 0.912941 |

The staged package reuses the prior clean-teacher `opening.pt` and `mid.pt`, replaces only `late.pt`, and is packaged with `--phase-duration-seconds 300` so online phase dispatch uses absolute episode time.

## Deterministic Comparisons

| Probe | Seeds | `soda-creek` | `caramel-workshop` | `cracked-star-jar` | Gate |
|---|---:|---:|---:|---:|---|
| 60s opening | 10 | 70% | 100% | 80% | watch |
| 180s handoff | 3 | 66.67% | 100% | 33.33% | repair |
| 300s long window | 3 | 0% | 0% | 0% | repair |

The 60s and 180s probes are deterministic and use no stochastic action seed or policy adapter. The added `caramel-workshop` teacher trajectory improves offline validation accuracy, but it does not improve the online high-pressure gate.

## 300s Failure

The 300s probe fails on all three high-pressure maps. Failed-only traces are recorded under `traces/`, and failure analysis is recorded in `failure_analysis_300s.md` and `failure_analysis_300s.json`.

| Map | Failures | Average Failure Survival | Dominant Action | Entropy |
|---|---:|---:|---|---:|
| `soda-creek` | 3 | 171.7034 | `3` / 29.88% | 0.8574 |
| `caramel-workshop` | 3 | 215.6949 | `3` / 29.37% | 0.8166 |
| `cracked-star-jar` | 3 | 129.9734 | `8` / 25.11% | 0.8267 |

The failure buckets show the blocker is still not a single-map sample coverage problem: `caramel-workshop` fails entirely in `late_180_to_300`, while `soda-creek` and `cracked-star-jar` still include opening deaths.

## Interpretation

Expanded clean teacher coverage is useful dataset evidence, but clean teacher-only late replacement remains insufficient. The policy still lacks opening / mid retention and closed-loop long-run recovery behavior, and adding one more clean caramel trajectory does not repair deterministic 300-second survival.

This report does not permit stage 03, RL policy acceptance, or `rl_test_bot_candidate` promotion. The next repair should stop testing clean teacher-only late replacement by itself and instead add explicit opening/mid retention, contrastive constraints, route / low-health / hazard / boss recovery objectives, or closed-loop late survival training before rerunning deterministic high-pressure 60s, 180s, and 300s comparisons.
