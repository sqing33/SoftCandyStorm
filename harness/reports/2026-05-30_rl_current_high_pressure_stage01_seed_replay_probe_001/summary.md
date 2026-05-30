# RL Stage 01 Seed Replay Probe

- Decision: `stage01_seed_replay_probe_failed`
- Initial model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Candidate: `harness/reports/2026-05-30_rl_current_high_pressure_stage01_seed_replay_probe_001/stage01_seed_replay.zip`
- Training: `512` timesteps, `soda-creek`, train seeds `63400-63402`, reward profile `standard`
- Failure case: `harness/failed_cases/fail_20260530_002_stage01_seed_replay_regression.json`

## Fixed-window Results

| Window | Gate | soda-creek | caramel-workshop | cracked-star-jar |
|---|---|---:|---:|---:|
| `60s` | `multimap_comparison_recorded_not_balance_gate` | 0.6667 | 1.0 | 1.0 |
| `180s` | `multimap_comparison_recorded_watch` | 0.3333 | 1.0 | 1.0 |
| `300s` | `multimap_comparison_recorded_needs_policy_repair` | 0.0 | 0.0 | 0.0 |

## Parent No-regression

- Decision: `policy_window_regression_failed`
- Blockers:
  - `180s/soda-creek: win_rate_delta -0.3334 below required 0.0`
  - `180s/soda-creek: average_survival_seconds dropped 11.4358s beyond allowed 5.0s`

## Findings

- Replaying seeds `63400-63402` did not clear the `soda-creek` opening failure; seed `63402` still died around `37.27s`.
- The candidate repaired `caramel-workshop` 180s relative to the parent but regressed `soda-creek` 180s.
- The 300s high-pressure gate remains fully blocked across all three maps.

## Next Actions

- Do not run stage 02 from this checkpoint.
- Trace seed `63402` with observations and compare it against successful same-window seeds before the next training attempt.
- Use a narrower opening retention objective or action-distribution guard, then rerun same-seed 60/180/300s parent no-regression.
