# Anchor Regularization Input Preflight

- Decision: `anchor_regularization_input_valid`
- Gate decision: `anchor_regularization_input_valid_not_policy_gate`
- Algorithm: `ppo`
- Anchor model: `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_fallback_probe_001/fallback.pt`
- Anchor opening model: `harness/reports/2026-05-28_rl_late_survival_contrast_pressure_curriculum_plan_001/stages/stage_02_late_180_to_300/stage_02_late_180_to_300.zip`
- Dataset samples: `200`
- Observation len: `145`
- Action count: `9`
- Anchor drift samples: `200`
- Time bucket filter: `include_time_buckets`
- Sample weighting: `map_time_bucket_balance`
- Target argmax agreement with dataset actions: `1.0`

## Sample Sources

| Source | Samples | Ratio |
| --- | ---: | ---: |
| `anchor_drift_diagnostic` | `200` | `1.0` |

## Limitations

- This preflight validates offline anchor regularization inputs only.
- It does not train a PPO checkpoint.
- It is not high-pressure, no-regression, repair-probe, or RL acceptance evidence.
