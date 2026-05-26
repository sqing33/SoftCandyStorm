# RL Curriculum Stage 01 Retry Trace

- Source model: `harness/reports/2026-05-27_rl_curriculum_time_bucket_stage01_retry_20k_001/stage01_opening_retry_20k.zip`
- Decision: `rl_episode_trace_recorded_needs_opening_repair`
- Evaluation: `harness/reports/2026-05-27_rl_curriculum_stage01_retry_trace_001/evaluation.json`
- Trace directory: `harness/reports/2026-05-27_rl_curriculum_stage01_retry_trace_001/traces`

## Trace Run

The run used `train_sb3.py --trace-dir --trace-failed-only --trace-sample-stride 30` on `soda-creek`, seeds `62406` through `62409`. It wrote traces only for the two failed policy episodes:

| Seed | Result | Time | Damage | Trace |
|---:|---|---:|---:|---|
| 62406 | `defeat` | 46.1996s | 120.26 | `traces/soda-creek_seed62406_trace.json` |
| 62409 | `defeat` | 28.8332s | 120.1198 | `traces/soda-creek_seed62409_trace.json` |

## Findings

- The trace confirms the retry policy is not randomly failing the opening; both failed episodes become strongly biased toward action `4`.
- In seed `62406`, the final sampled rows keep choosing action `4` with policy probability about `0.83` to `0.87` while health falls from `107.89` at 39.9997s to `0.0` at 46.1996s.
- In seed `62409`, action `4` remains the top policy action from 22.0s through death at 28.8332s, with final chosen action score `0.8494`.
- Reward breakdown shows repeated damage ticks and only tiny boundary/enemy pressure penalties at the sampled points, so the next repair should inspect whether current observation/reward features understate this opening danger path.

## Next

- Keep `soda-creek` opening as the active RL blocker.
- Use the trace files to compare failed action `4` runs against successful seeds before changing PPO timesteps again.
- Consider adding richer trace fields from GameCore snapshots, such as player position, nearest enemy pressure, and boundary distances, if current Gym info remains too coarse.
