# Route Recovery Auxiliary Teacher Sequence Windows

- Gate decision: `teacher_sequence_diagnostic_recorded_watch_only`
- Tool: `python/train/inspect_behavior_clone_teacher_sequences.py`
- Input trace: `harness/reports/2026-05-27_rl_route_recovery_aux_60s_nearest_transition_001/online_60s_trace/soda-creek_seed62300_trace.json`
- Sequence report: `harness/reports/2026-05-27_rl_route_recovery_aux_teacher_sequence_windows_001/teacher_sequence_windows.json`
- Markdown detail: `harness/reports/2026-05-27_rl_route_recovery_aux_teacher_sequence_windows_001/teacher_sequence_windows.md`
- Related failure case: `harness/failed_cases/fail_20260527_040_route_recovery_aux_entropy_retry_action_collapse.json`

## Purpose

The previous 60 second nearest-neighbor diagnostic showed mismatch windows at `25-35s` and `55-60s`, but only gave action distributions. This pass inspects the nearest teacher episode snippets around those windows so the next repair can target concrete action sequences instead of generic entropy or epoch tuning.

The diagnostic uses same-map offline candidates from `0-60s`, reconditions trace progress with `time_seconds / 300`, and records online and teacher action sequences with a radius of 4 sampled rows around each representative mismatch.

## Window Summary

| Window | Online top | Nearest top | Match ratio | Main nearest source |
|---|---|---|---:|---|
| `25-30s` | action `5` at 1.0000 | action `3` at 0.6875, action `8` at 0.2500 | 0.0000 | KiteBot `soda-creek` seed `48003` plus route recovery seed `62302` |
| `30-35s` | action `5` at 1.0000 | action `8` at 0.8000 | 0.0000 | route recovery repair seed `62301/62302` plus KiteBot seed `48003` |
| `55-60s` | action `3` at 1.0000 | action `2` at 0.6000 | 0.2667 | KiteBot `soda-creek` seed `48009` plus route recovery seed `62301` |

## Sequence Findings

In `25-30s`, the policy holds a pure action `5` sequence while the nearest KiteBot teacher around seed `48003` alternates mostly `3`, with brief `1/4/5` changes. This means the online rollout is not just delayed; it is taking a lower-health downward corridor while nearby teacher snippets mostly keep moving right or briefly adjust.

In `30-35s`, the strongest nearest source shifts to route recovery repair samples. Those snippets are dominated by action `8` after an earlier action `5`, while online stays action `5` for the whole sampled context. This is the clearest supervision mismatch and likely needs targeted action-change / recovery sequence weighting, not more global entropy.

In `55-60s`, online returns to a pure action `3` sequence near the right boundary. The nearest same-time KiteBot teacher seed `48009` shows a clean action `2` sequence from `54.9995s` to `57.3328s`, only then returning to `3`. This gives a concrete late-opening recovery target for the next repair.

## Decision

This checkpoint remains rejected as a policy candidate. The useful next step is to convert these windows into a focused repair experiment:

- increase weight for sequence transitions where online repeats `5` but nearest teacher or repair samples favor `8` in `30-35s`;
- add or upsample same-map `55-60s` teacher snippets where action `2` moves away from the right-boundary pressure;
- compare GRU history with and without forced teacher-prefix context before retraining.

## Limitations

- This is still single-map, single-seed diagnostic evidence.
- Nearest-neighbor sequence snippets can guide repair, but they do not prove policy quality.
- This does not replace deterministic 60 / 180 / 300 second high-pressure gates, Replay, or human playtest.
