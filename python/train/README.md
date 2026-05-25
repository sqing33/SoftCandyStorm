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
python3 -m pip install gymnasium numpy stable-baselines3
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

Do not record RL Bot training as complete until a model file, metadata file, evaluation report, and known exploit notes exist.
