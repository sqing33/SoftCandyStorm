# Route Recovery Auxiliary Absolute Time Conditioning Fix

- Code change: staged behavior clone policies now pass `phase_duration_seconds` to child behavior clones during evaluation.
- Evaluation report: `harness/reports/2026-05-27_rl_route_recovery_aux_absolute_time_conditioning_fix_001/evaluation_5s_soda.json`
- Trace: `harness/reports/2026-05-27_rl_route_recovery_aux_absolute_time_conditioning_fix_001/online_5s_trace/soda-creek_seed62300_trace.json`
- Related failure case: `harness/failed_cases/fail_20260527_040_route_recovery_aux_entropy_retry_action_collapse.json`

## Hypothesis

The entropy retry staged checkpoint was packaged with `phase_duration_seconds = 300`, so staged dispatch selected the opening / mid / late child policy from absolute episode time. However, each child behavior clone still computed its own `time_phase_conditioning` and context input from raw observation progress. In a 5 second smoke, `observation[0]` advances from `0.0` to almost `1.0`, which mismatches the 300 second phase-aligned training data.

## Fix

`BehaviorClonePolicy.set_step_context` now accepts `phase_duration_seconds` and derives an absolute progress override from `time_seconds / phase_duration_seconds`. During inference this override replaces the first progress feature before building MLP / GRU inputs, and the time-phase one-hot uses the same absolute progress. `StagedBehaviorClonePolicy.set_step_context` forwards its configured phase duration to all child behavior clones.

## Verification

- `python3 -m py_compile python/train/train_behavior_clone.py python/train/test_train_behavior_clone.py`
- `uv run --with-requirements python/train/requirements.txt --with pytest pytest -q python/train/test_train_behavior_clone.py`

The test suite now includes a regression check that a behavior clone with `time_phase_conditioning = one_hot` uses absolute step context instead of raw short-window observation progress.

## Result

The suspected mismatch was real but not sufficient to repair this checkpoint. Re-running the same 5 second `soda-creek` smoke after the fix still selected action `3` on `151/151` frames:

| Metric | Result |
|---|---:|
| Win rate | 1.0000 |
| Steps | 151 |
| Action `3` ratio | 1.0000 |
| Normalized action entropy | 0.0000 |
| Mean action `3` score | 0.4283 |

The gate remains `evaluation_recorded_needs_action_bias_repair`. The fix should stay because it makes staged absolute-time dispatch internally consistent, but the route_recovery entropy retry checkpoint is still not a policy candidate.

## Trace Dataset Nearest Neighbor Diagnostic

Follow-up diagnostic report: `harness/reports/2026-05-27_rl_route_recovery_aux_absolute_time_conditioning_fix_001/trace_dataset_nearest_opening.json`

The online 5 second trace was compared against same-map offline opening samples from `0-60s`, with trace progress reconditioned by `time_seconds / 300`. The nearest offline target distribution was also dominated by action `3`:

| Metric | Result |
|---|---:|
| Trace samples | 151 |
| Offline candidates | 1848 |
| Online action `3` ratio | 1.0000 |
| Nearest target action `3` ratio | 0.9735 |
| Nearest target matches online action ratio | 0.9735 |
| Online normalized action entropy | 0.0000 |
| Average nearest distance | 0.761550 |

This shifts the diagnosis: the 5 second online loop is not explained by global offline checkpoint collapse, and it is also not primarily contradicted by nearest same-map opening teacher targets. The toy-window action entropy gate is still useful as a warning, but this particular trace is mostly following a narrow opening teacher neighborhood. Further repair should inspect longer handoff / recovery windows, history padding, and whether the supervision set has enough early alternatives after the first few seconds.

## Next Step

Do not promote this checkpoint. The next useful diagnostic is a longer short-window or 60 second evaluation that checks when the teacher neighborhood stops preferring action `3`, then compares the policy history against teacher recovery alternatives around that transition.
