# Route Recovery Auxiliary Entropy Retry Smoke

- Gate decision: `evaluation_recorded_needs_action_bias_repair`
- Staged model: `harness/reports/2026-05-27_rl_route_recovery_aux_entropy_retry_001/staged.pt`
- Packaging report: `harness/reports/2026-05-27_rl_route_recovery_aux_entropy_retry_001/packaging.json`
- Evaluation report: `harness/reports/2026-05-27_rl_route_recovery_aux_entropy_retry_001/evaluation_5s_soda.json`
- Failure case: `harness/failed_cases/fail_20260527_040_route_recovery_aux_entropy_retry_action_collapse.json`

## Purpose

This smoke retries the previous route recovery auxiliary staged clone with a stronger anti-collapse setup: `epochs = 5`, `entropy_regularization = 0.08`, inverse-frequency class weighting, `danger_action_change` sample weighting, `edge_recovery_sample_weight = 4.0`, GRU context8, map one-hot conditioning, and time-phase one-hot conditioning.

The input mix is unchanged from the prior staged route recovery smoke: phase-aligned KiteBot high-pressure trajectories plus `689` route_recovery repair samples. Opening still excludes route recovery repair samples, mid keeps `342` samples from `60-180s`, and late keeps `40` samples after phase filtering.

## Training Results

| Phase | Samples | Route Recovery Samples | Validation Accuracy | Validation Entropy |
|---|---:|---:|---:|---:|
| `opening` | 5388 | 0 | 0.6030 | 1.578149 |
| `mid` | 10253 | 342 | 0.6431 | 1.376341 |
| `late` | 6467 | 40 | 0.5816 | 1.410901 |

The higher entropy setting improved validation accuracy versus the 1 epoch smoke, but the online deterministic load smoke still collapsed to a single action.

## Load Smoke

The staged checkpoint packages with absolute-time dispatch over a 300 second horizon and loads through the Gym evaluation path. A 5 second `soda-creek` smoke completed the toy duration, but the deterministic policy selected action `3` on `151/151` frames and produced `normalized_action_entropy = 0.0`.

The evaluation report records:

- `gate_decision = evaluation_recorded_needs_action_bias_repair`
- `dominant_action_bias`: action `3` accounts for `100%` of policy steps
- `low_action_entropy`

## Offline Policy Diagnostic

`offline_policy_diagnostic.json` compares the staged checkpoint against the full mixed offline dataset used for this retry. It records `gate_decision = offline_policy_diagnostic_recorded_watch_only`, overall accuracy `0.6180`, dominant predicted action `7` at only `15.06%`, and normalized predicted action entropy `0.9434`.

| Phase | Samples | Accuracy | Dominant Action | Dominant Ratio | Predicted Entropy |
|---|---:|---:|---:|---:|---:|
| `opening` | 5693 | 0.5754 | `4` | 0.1902 | 0.9159 |
| `mid` | 10253 | 0.6542 | `7` | 0.1858 | 0.9376 |
| `late` | 6469 | 0.5981 | `6` | 0.1469 | 0.9400 |

The offline diagnostic does not show global checkpoint-level action collapse. The online 5 second collapse is therefore more likely tied to the Gym load-smoke state distribution, initial short-window history, map/start context, or online dispatch path than to the whole offline target distribution.

## Decision

This retry remains a smoke-only repair artifact. It proves that the higher entropy/class-weighted training path and staged packaging can run, but it does not produce a usable policy candidate. The failure shifted from action `7` collapse in the previous smoke to action `3` collapse here, so the next repair should inspect target distributions, teacher soft targets, or policy constraints rather than only increasing epochs or entropy regularization again.

## Limitations

- This is not a high-pressure comparison.
- The 5 second toy smoke is not a gameplay, balance, or fun gate.
- The checkpoint cannot enter Stage 03, RL acceptance, or `rl_test_bot_candidate` review.
- The attached failure case must remain linked to this checkpoint.
