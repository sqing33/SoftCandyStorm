# Route Recovery Auxiliary 60s Nearest Transition Diagnostic

- Gate decision: `trace_dataset_nearest_neighbor_recorded_watch_only`
- Model: `harness/reports/2026-05-27_rl_route_recovery_aux_entropy_retry_001/staged.pt`
- Evaluation report: `harness/reports/2026-05-27_rl_route_recovery_aux_60s_nearest_transition_001/evaluation_60s_soda.json`
- Sampled trace: `harness/reports/2026-05-27_rl_route_recovery_aux_60s_nearest_transition_001/online_60s_trace/soda-creek_seed62300_trace.json`
- Nearest-neighbor report: `harness/reports/2026-05-27_rl_route_recovery_aux_60s_nearest_transition_001/trace_dataset_nearest_60s.json`
- Related failure case: `harness/failed_cases/fail_20260527_040_route_recovery_aux_entropy_retry_action_collapse.json`

## Purpose

The previous 5 second diagnostic showed that action `3` matched the nearest same-map opening teacher neighborhood, so this follow-up extends the same `soda-creek` seed `62300` evaluation to 60 seconds and compares a stride-10 sampled trace against same-map `0-60s` offline samples.

The comparison uses the staged checkpoint's 300 second horizon by reconditioning trace progress as `time_seconds / 300`.

## Evaluation Result

The policy reached the 60 second toy duration, but this remains diagnostic evidence only. It is not a high-pressure comparison and it does not promote the checkpoint.

| Metric | Result |
|---|---:|
| Survival | 60.0328s |
| Terminal kind | victory |
| Damage taken | 84.1101 |
| Reward | -4.8003 |
| Action `3` ratio | 0.5913 |
| Action `5` ratio | 0.3715 |
| Normalized action entropy | 0.3751 |
| Route recovery reward | -2.2598 |
| Trace sample stride | 10 |

The final sampled trace is pinned to the right map boundary with low health risk already present. This confirms the checkpoint can leave the 5 second action `3` loop, but it still follows a risky edge-heavy path.

## Nearest Dataset Comparison

| Metric | Result |
|---|---:|
| Trace samples | 182 |
| Offline candidates | 1848 |
| Nearest target matches online action ratio | 0.5714 |
| First sampled nearest target change | 7.0000s, action `3` -> `5` |
| First sampled online action change | 22.6667s, action `3` -> `5` |
| Average nearest distance | 1.576151 |

The 5 second window was too narrow to expose the transition problem. Over the sampled 60 second trace, the offline nearest teacher neighborhood starts offering non-`3` targets well before the online policy changes action.

The largest mismatch windows are:

| Window | Online top | Nearest top | Match ratio | Interpretation |
|---|---|---|---:|---|
| `25-30s` | action `5` at 1.0000 | action `3` at 0.6875 | 0.0000 | policy moves down while nearest teacher still favors rightward recovery |
| `30-35s` | action `5` at 1.0000 | action `8` at 0.8000 | 0.0000 | policy continues down while nearest teacher favors up-left recovery |
| `55-60s` | action `3` at 1.0000 | action `2` at 0.6000 | 0.2667 | policy returns to rightward edge pressure near the end |

## Decision

This checkpoint remains watch-only repair evidence. The new diagnosis is no longer "global offline action collapse"; it is a transition and recovery problem after the first few seconds of opening movement.

Next repair should focus on the `20-35s` and `55-60s` windows: inspect teacher trajectories around those neighborhoods, compare GRU hidden-history effects, and add explicit recovery / action-change supervision before re-running deterministic high-pressure gates.

## Limitations

- This is a single-map, single-seed, 60 second diagnostic.
- The committed trace is sampled every 10 environment steps to keep report size manageable.
- It does not prove policy quality, Replay stability, balance, or fun.
- It is not a 60 / 180 / 300 second high-pressure multi-map acceptance gate.
- The checkpoint cannot enter Stage 03, RL acceptance, or `rl_test_bot_candidate` review.
