# Post Recovery RL Dependency Check

- Decision: `rl_dependencies_available_via_uv`
- Command: `uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --check-deps`
- Report: `harness/reports/2026-05-26_post_recovery_rl_deps_check_001/dependencies.json`

## Dependencies

| Module | Available |
|---|---|
| `gymnasium` | true |
| `numpy` | true |
| `stable_baselines3` | true |
| `torch` | true |

## Limitations

- This only proves the temporary `uv` environment can import the RL dependencies.
- It does not train, evaluate, or accept any RL policy.
