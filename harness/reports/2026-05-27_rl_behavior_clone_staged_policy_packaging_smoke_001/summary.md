# RL Behavior Clone Staged Policy Packaging Smoke

- Status: `packaged`
- Gate decision: `staged_behavior_clone_packaged_not_policy_gate`
- Model: `harness/reports/2026-05-27_rl_behavior_clone_staged_policy_packaging_smoke_001/staged.pt`
- Phase labels: `opening`, `mid`, `late`
- Phase thresholds: `0.2`, `0.6`
- Subpolicy architecture: `mlp`
- Subpolicy epochs: `1`

## Phase Training

| Phase | Samples | Validation accuracy | Model |
|---|---:|---:|---|
| `opening` | 1080 | 0.5417 | `opening.pt` |
| `mid` | 9332 | 0.4989 | `mid.pt` |
| `late` | 11538 | 0.6430 | `late.pt` |

## Packaging

- `staged.pt` references all three subpolicies with relative paths.
- Packaging validation confirmed `action_count = 9` and `base_observation_len = 145` across subpolicies.

## Load Smoke

- Command path: `train_sb3.py --compare-rule-bots --behavior-clone-model staged.pt`
- Map: `soda-creek`
- Seeds: `48000` to `48001`
- Duration: `10` seconds
- Gate decision: `comparison_recorded_needs_action_bias_repair`

## Limitations

- This is a packaging and loading smoke only, not a policy-quality result.
- The 1 epoch subpolicies show action bias and must not be promoted as an RL test Bot.
- A real staged candidate still needs full training, high-pressure 60/300 second comparison, failure-case review, and RL policy acceptance validation.
