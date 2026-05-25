# RL Training Smoke Config Summary

- Config: `python/train/rl_training_config.json`
- Training entry: `python/train/train_sb3.py`
- Report template: `python/train/rl_training_report_template.json`
- Dry-run reports:
  - `harness/reports/2026-05-25_rl_training_smoke_config_001/dqn_dry_run.json`
  - `harness/reports/2026-05-25_rl_training_smoke_config_001/ppo_dry_run.json`
- Dependency report: `harness/reports/2026-05-25_rl_training_smoke_config_001/dependency_check.json`

## Gate Notes

- DQN and PPO configs both parse and can dry-run through the Python Gym bridge.
- Dry-run uses the same `game_harness gym-bridge` process and headless GameCore as the Gym bridge smoke.
- Current Python environment is missing `gymnasium`, `numpy`, and `stable_baselines3`; therefore no real model training was attempted.
- This report proves the training entry, config contract, dependency check, report output path, and dry-run environment loop. It does not prove RL Bot skill.

## Next Validation

- Install `gymnasium`, `numpy`, and `stable-baselines3`.
- Run `python3 python/train/train_sb3.py --algorithm dqn` for a short model smoke.
- Evaluate the saved model against rule Bot baselines before adding RL Bot to nightly gates.
