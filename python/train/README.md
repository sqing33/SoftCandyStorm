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

`train_sb3.py` writes the model zip, model metadata, a training report, an evaluation report, and known exploit notes. Do not record RL Bot training as complete until all of those files exist and the policy has been compared against rule Bot baselines.
