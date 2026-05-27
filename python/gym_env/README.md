# Soft Candy Storm Gym Bridge

This package is the first Python-side bridge for RL experiments. It wraps the Rust `game_harness gym-bridge` JSONL process, so training code still talks to the same headless `GameCore` used by Harness, Bot policies, Replay, and Runtime.

## Smoke Test

```bash
python python/gym_env/smoke_test.py
```

The smoke test starts `cargo run -q -p game_harness -- gym-bridge`, resets a short episode, steps with a fixed discrete movement action, and verifies that the observation length matches the bridge spec. The default bridge uses observation v2.

## Environment

```python
from python.gym_env import SoftCandyStormEnv

env = SoftCandyStormEnv(seconds=600.0, tick_rate=30, observation_version=2)
obs, info = env.reset(seed=12345)
obs, reward, terminated, truncated, info = env.step(3)
env.close()
```

Observation v1 is still available for old local model analysis with `observation_version=1`. New training should use v2, which adds player stat modifiers, enemy relative velocity/radius/elite/behavior features, active hazard direction, boss summary, map dimensions, and corner proximity.

For multi-map training experiments, pass a map list and let the environment choose a map on each reset:

```python
env = SoftCandyStormEnv(
    map_ids=["frosting-grassland", "soda-creek", "caramel-workshop"],
    map_selection="cycle",
)
```

Explicit reset options such as `options={"map_id": "frosting-grassland"}` still override the training map selector, which keeps evaluation deterministic for a single map.

Training can also replay a fixed seed set on resets. This is intended for curriculum repair runs where a policy must retain known opening or mid-window regression seeds while learning another map:

```python
env = SoftCandyStormEnv(
    map_ids=["soda-creek", "caramel-workshop"],
    map_selection="random",
    seed_values=[62400, 62401, 62402, 62403],
    seed_selection="cycle",
)
```

Explicit `reset(seed=...)` still overrides the training seed selector for evaluation.

The first RL phase uses a 9-action discrete movement space:

```text
0 idle
1 up
2 up-right
3 right
4 down-right
5 down
6 down-left
7 left
8 up-left
```

Upgrade choices default to the bridge's first-option fallback. Callers can pass an `upgrade_policy` object with `choose(observation, upgrade_options)` when they need a supervised ranker to fill pending upgrade prompts during training or evaluation.

## Dependency Notes

- If `gymnasium` and `numpy` are installed, the wrapper exposes normal Gymnasium `spaces`.
- Without them, the smoke test still runs with lightweight fallback classes.
- Stable-Baselines3 training should install `gymnasium`, `numpy`, and `stable-baselines3` in the Python environment.
