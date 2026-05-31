# RL Failure Lane Trace Plan

- Decision: `rl_failure_lane_trace_plan_ready`
- Source: `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/failure_analysis_caramel_300s_10seed.json`
- Lanes: `2`
- Tasks: `2`

## Tasks

| Lane | Map | Type | Priority | Seeds | Trace Window | Eval Range | Extra Scan Seeds | Required Preflight |
|---|---|---|---:|---|---|---|---|---|
| `late_terminal_survival_conversion` | `caramel-workshop` | `late_terminal_trace_preflight` | 1 | 63400, 63401, 63403, 63404, 63405, 63406, 63408, 63409 | 180.0-240.8193s | seed `63400` x `10` | 63402, 63407 | late terminal conversion probe plus 300s caramel no-regression gate |
| `opening_repair` | `caramel-workshop` | `opening_trace_preflight` | 1 | 63402 | 0.0-60.0s | seed `63402` x `1` | none | 60s caramel window target preflight plus target seed trace comparison |

## Details

### `late_terminal_survival_conversion` / `caramel-workshop`
- Trace dir: `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/failure_lane_traces/late_terminal_survival_conversion/caramel-workshop`
- Trace goal: capture late low-health, hazard, and terminal conversion failures
- Repair shape: state-conditioned terminal conversion branch
- Failure time seconds: `{"average": 216.6965, "max": 225.8193, "min": 210.8827}`
- Dominant actions: `{"3": 1, "5": 3, "7": 3, "8": 1}`
- Suggested args: `--algorithm ppo --compare-rule-bots --map-id caramel-workshop --eval-seconds 300 --trace-dir harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/failure_lane_traces/late_terminal_survival_conversion/caramel-workshop --trace-failed-only --trace-sample-stride 15 --trace-include-observation --model harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/ppo_opening_mid_boundary_retention_seed63405_probe.zip --seed-start 63400 --eval-episodes 10`

### `opening_repair` / `caramel-workshop`
- Trace dir: `harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/failure_lane_traces/opening_repair/caramel-workshop`
- Trace goal: capture target opening defeat and parent/candidate divergence before more PPO
- Repair shape: opening boundary escape or early-route branch
- Failure time seconds: `{"average": 40.0997, "max": 40.0997, "min": 40.0997}`
- Dominant actions: `{"5": 1}`
- Suggested args: `--algorithm ppo --compare-rule-bots --map-id caramel-workshop --eval-seconds 300 --trace-dir harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/failure_lane_traces/opening_repair/caramel-workshop --trace-failed-only --trace-sample-stride 15 --trace-include-observation --model harness/reports/2026-05-31_rl_opening_mid_boundary_retention_seed63405_probe_001/ppo_opening_mid_boundary_retention_seed63405_probe.zip --seed-start 63402 --eval-episodes 1`

## Limitations

- This report creates trace and preflight tasks only; it does not run simulation or train a policy.
- Non-contiguous lane seeds may require scanning extra seeds because train_sb3 comparison uses seed_start plus eval_episodes.
- A trace plan is repair routing evidence, not RL acceptance or candidate promotion evidence.
