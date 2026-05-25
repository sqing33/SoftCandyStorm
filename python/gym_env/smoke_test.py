import json

from soft_candy_env import SoftCandyStormEnv


def main():
    env = SoftCandyStormEnv(seconds=2.0, tick_rate=30)
    total_reward = 0.0
    try:
        observation, info = env.reset(seed=12345, options={"seconds": 2.0, "tick_rate": 30})
        assert len(observation) == info["observation_len"]
        assert info["action_count"] == 9

        terminated = False
        truncated = False
        steps = 0
        while not terminated and not truncated and steps < 90:
            observation, reward, terminated, truncated, info = env.step(3)
            assert len(observation) == info["observation_len"]
            total_reward += reward
            steps += 1

        print(
            json.dumps(
                {
                    "status": "ok",
                    "steps": steps,
                    "terminated": terminated,
                    "truncated": truncated,
                    "time_seconds": info["time_seconds"],
                    "observation_len": info["observation_len"],
                    "action_count": info["action_count"],
                    "total_reward": round(total_reward, 4),
                },
                ensure_ascii=False,
            )
        )
    finally:
        env.close()


if __name__ == "__main__":
    main()
