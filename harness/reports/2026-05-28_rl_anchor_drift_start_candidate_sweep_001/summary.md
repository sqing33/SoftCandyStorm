# RL Anchor Drift Start Candidate Sweep

- Decision: `anchor_drift_start_candidate_sweep_failed`
- Gate decision: `no_existing_sb3_start_checkpoint_close_enough`
- Dataset: `harness/reports/2026-05-28_rl_curriculum_stage02_soda_caramel_closed_loop_anchor_probe_001/mid_anchor_drift_training_samples.jsonl`
- Anchor fallback model: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_fallback_probe_001/fallback.pt`
- Anchor opening model: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Failure case: `harness/failed_cases/fail_20260528_091_stage02_anchor_drift_start_candidate_sweep.json`

This sweep compared existing SB3 checkpoints against the same `200` mid-window `anchor_drift_sample` rows used by the start alignment precheck. Every candidate failed the strict pre-training alignment thresholds: mean KL must be `<= 0.25`, argmax agreement must be `>= 0.85`, and each map bucket mean KL must be `<= 0.25`.

| Candidate | Overall mean KL | Argmax agreement | Soda KL | Caramel KL | Cracked KL |
| --- | ---: | ---: | ---: | ---: | ---: |
| `phase_specific_anchor_smoke` | `2.14298` | `0.0` | `1.961594` | `2.196015` | `2.186405` |
| `opening_aware_distilled` | `2.20213` | `0.0` | `1.996777` | `2.244401` | `2.255736` |
| `anchor_map_bucket_full_smoke` | `2.204643` | `0.0` | `2.015695` | `2.255433` | `2.250991` |
| `opening_aware_late_win_conversion` | `2.21949` | `0.0` | `2.021765` | `2.272698` | `2.267977` |
| `soda_caramel_closed_loop_anchor` | `2.228259` | `0.0` | `2.028737` | `2.286731` | `2.275991` |
| `anchor_regularized_smoke` | `2.26528` | `0.0` | `2.054458` | `2.317458` | `2.318117` |
| `stage02_late_180_to_300` | `3.550567` | `0.0` | `3.464685` | `3.280005` | `3.645045` |

`phase_specific_anchor_smoke` is the least-bad existing SB3 start point on this diagnostic slice, but it is still far outside the threshold and has zero argmax agreement. This means the next repair should not simply pick a different existing checkpoint and run longer PPO on the top-200 rows.

## Next

- Treat the top-200 drift rows as diagnostic pressure points, not as a standalone PPO objective.
- Add a supervised SB3 re-alignment or distillation step on broader anchor data before any guarded PPO continuation.
- If PPO is attempted again, use mixed full-anchor + drift rows, smaller update pressure, and the validation guard.
- Continue to require full anchor alignment, deterministic 60 / 180 / 300 high-pressure no-regression, repair-probe gate, and RL acceptance evidence.

## Files

- `phase_specific_anchor_alignment.json`
- `opening_aware_distilled_alignment.json`
- `anchor_map_bucket_full_alignment.json`
- `opening_aware_late_win_conversion_alignment.json`
- `soda_caramel_closed_loop_anchor_alignment.json`
- `anchor_regularized_smoke_alignment.json`
- `stage02_late_180_to_300_alignment.json`
