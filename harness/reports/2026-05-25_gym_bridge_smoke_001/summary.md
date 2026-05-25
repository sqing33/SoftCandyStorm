# Python Gym Bridge Smoke Summary

- Command: `python3 python/gym_env/smoke_test.py`
- Report copy: `harness/reports/2026-05-25_gym_bridge_smoke_001/gym_bridge_smoke.json`
- Bridge command: `cargo run -q -p game_harness -- gym-bridge`
- Protocol: JSONL over stdin/stdout
- Action space: `9` discrete movement actions
- Observation length: `82`
- Episode config: seed `12345`, duration `2s`, tick rate `30`

## Gate Notes

- The Python wrapper calls the Rust `game_harness gym-bridge` process, so observations and rewards come from the same headless GameCore used by Harness and Bot tests.
- The smoke reached a terminal state in `61` steps with `terminated: true` and `truncated: false`.
- Upgrade choices remain rule-handled by the bridge for this first RL phase; RL action currently controls movement only.
- This validates the bridge contract, not model training quality.

## Next Validation

- Add a small DQN/PPO training config once Gymnasium, NumPy and Stable-Baselines3 are installed in the Python environment.
- Add saved model metadata only after a real training run exists.
- Keep rule Bot matrix and Replay regression as the regular CI-quality baseline.
