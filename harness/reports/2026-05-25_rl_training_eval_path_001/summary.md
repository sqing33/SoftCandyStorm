# RL Training Evaluation Output Summary

- Updated `python/train/train_sb3.py` so real SB3 training can write a model zip, metadata, training report, evaluation report, and known exploit notes.
- Added smoke controls: `--timesteps`, `--eval-episodes`, and `--eval-seconds`.
- Verified dependency-light bridge dry-run with `python3 python/train/train_sb3.py --dry-run --algorithm dqn --steps 30 --report harness/reports/2026-05-25_rl_training_eval_path_001/dry_run.json`.
- Verified dependency check report with `python3 python/train/train_sb3.py --check-deps --report harness/reports/2026-05-25_rl_training_eval_path_001/dependency_check.json`.
- Verified Python syntax with `python3 -m py_compile python/train/train_sb3.py python/gym_env/soft_candy_env.py python/gym_env/smoke_test.py`.
- `python3 -m pytest` was not available because system Python has no `pytest` module.

## Dependency Status

- System Python: `Python 3.9.6`
- Missing in system Python: `gymnasium`, `numpy`, `stable_baselines3`
- A temporary `uv run --with gymnasium --with numpy --with stable-baselines3 ... --check-deps` attempt began downloading SB3/Torch dependencies but was stopped after it exceeded a reasonable smoke wait.

## Gate Notes

- No real RL model was produced in this report.
- Do not record RL Bot capability as complete until a model, metadata, evaluation report, known exploit notes, and rule Bot comparison all exist.
