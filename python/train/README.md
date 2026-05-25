# RL Training Entry Points

This folder contains the first Stable-Baselines3 training entry point for the Python Gym bridge.

The current bridge is Phase 1 only:

- 9 discrete movement actions.
- Headless `GameCore` through `game_harness gym-bridge`.
- Upgrade choices handled by the bridge rule policy.
- DQN/PPO config is intentionally small for smoke runs.

## Dependency Check

```bash
python3 python/train/train_sb3.py --check-deps
```

Real training requires:

```bash
python3 -m pip install -r python/train/requirements.txt
```

## Dry Run

```bash
python3 python/train/train_sb3.py --dry-run --algorithm dqn --steps 90
```

Dry-run validates the config and bridge without importing Stable-Baselines3.

## Real Training

```bash
python3 python/train/train_sb3.py --algorithm dqn
python3 python/train/train_sb3.py --algorithm ppo
```

For a minimal smoke, override the training and evaluation size:

```bash
python3 python/train/train_sb3.py --algorithm dqn --timesteps 128 --eval-episodes 2 --eval-seconds 5 --report harness/reports/local_rl_training/dqn_training_smoke.json
```

Use `--model-out <path>` and `--report-dir <path>` for experiments that should not overwrite the default per-algorithm model or local training reports.

`train_sb3.py` writes the model zip, per-algorithm model metadata, a training report, an evaluation report, and known exploit notes. Do not record RL Bot training as complete until all of those files exist and the policy has been compared against rule Bot baselines.

## Policy vs Rule Bot Comparison

Compare a saved SB3 policy against rule Bot baselines with the same map, seed range, and duration:

```bash
python3 python/train/train_sb3.py --algorithm dqn --compare-rule-bots --model python/train/models/dqn_phase1_movement_survival.zip --seed-start 30000 --eval-episodes 2 --eval-seconds 5 --map-id frosting-grassland --rule-bots random,kite,tank --report harness/reports/local_rl_training/dqn_rule_bot_comparison.json
```

The comparison report records the policy summary, action distribution, rule Bot matrix output, smoke findings, limitations, and `comparison_recorded_not_balance_gate` gate decision.

Policy evaluation reports include `action_entropy_bits`, `normalized_action_entropy`, and averaged `reward_breakdown` fields so action collapse and reward-shaping issues can be inspected before treating a policy as a useful test Bot.

Training reports use `trained_needs_action_bias_repair` when the policy collapses to a dominant action or very low normalized action entropy; comparison reports use `comparison_recorded_needs_action_bias_repair` for the same condition.
