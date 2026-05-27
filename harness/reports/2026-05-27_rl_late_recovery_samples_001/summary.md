# RL Late Recovery Samples

- Decision: `late_recovery_samples_recorded_not_policy_gate`
- Combined samples: `harness/reports/2026-05-27_rl_late_recovery_samples_001/risk_recovery_samples_all.jsonl`
- Source policy: `harness/reports/2026-05-27_rl_behavior_clone_edge_aux_handoff_window_staged_gru_context8_001/staged.pt`
- Opening wrapper: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip`
- Source failure case: `harness/failed_cases/fail_20260527_031_edge_aux_handoff_window_late_gap.json`
- Source trace: `harness/reports/2026-05-27_rl_behavior_clone_edge_aux_handoff_window_late_trace_001/summary.md`

## Sample Set

The run exports `1079` `risk_recovery_supervision_sample` rows from 300 second high-pressure evaluation with `--late-recovery-filter --late-recovery-min-seconds 180`.

| Map | Samples | Time Range | Edge | Hazard | Boss | Enemy | Idle | Adapter Win Rate |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| `caramel-workshop` | 228 | 180.0095-227.6197 | 82 | 41 | 32 | 7 | 69 | 0.00 |
| `cracked-star-jar` | 406 | 180.0095-284.2522 | 44 | 88 | 53 | 131 | 126 | 0.00 |
| `soda-creek` | 445 | 180.0095-290.6173 | 44 | 12 | 69 | 220 | 107 | 0.00 |

## Interpretation

The samples cover the late-window mixed-pressure failure surface seen in the failed-only trace: edge-pinned actions, hazard-facing movement, Boss / enemy pressure, and idle-under-pressure cases all appear in the exported rows.

This is still adapter-produced repair material. The evaluation with the adapter remains `0%` win rate on all three maps, so this report does not advance stage 03 or RL acceptance.

## Verification

- `uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py ... --late-recovery-filter ...` for each high-pressure map.
- Behavior clone dry-run validation is recorded separately in `behavior_clone_dry_run.json`.
