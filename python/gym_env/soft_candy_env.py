import json
import os
import random
import shlex
import subprocess
from pathlib import Path

try:
    import gymnasium as gym
    from gymnasium import spaces
except ImportError:
    class _FallbackEnv:
        pass

    class _FallbackDiscrete:
        def __init__(self, n):
            self.n = n

        def sample(self):
            return random.randrange(self.n)

    class _FallbackBox:
        def __init__(self, low, high, shape, dtype):
            self.low = low
            self.high = high
            self.shape = shape
            self.dtype = dtype

    class _FallbackGym:
        Env = _FallbackEnv

    class _FallbackSpaces:
        Discrete = _FallbackDiscrete
        Box = _FallbackBox

    gym = _FallbackGym()
    spaces = _FallbackSpaces()

try:
    import numpy as np
except ImportError:
    np = None


class SoftCandyStormEnv(gym.Env):
    """Gymnasium wrapper around the Rust GameCore JSONL bridge."""

    metadata = {"render_modes": []}

    def __init__(
        self,
        *,
        seed=12345,
        seconds=600.0,
        tick_rate=30,
        map_id="frosting-grassland",
        map_ids=None,
        map_selection="cycle",
        observation_version=2,
        content_dir="content/base_demo",
        harness_cmd=None,
        cwd=None,
        upgrade_policy=None,
    ):
        self.seed_value = seed
        self.seconds = seconds
        self.tick_rate = tick_rate
        self.map_ids = self._normalize_map_ids(map_ids, map_id)
        self.map_selection = map_selection
        if self.map_selection not in {"cycle", "random"}:
            raise ValueError("map_selection must be `cycle` or `random`")
        self.observation_version = int(observation_version)
        self.map_id = self.map_ids[0]
        self.episode_index = 0
        self.content_dir = content_dir
        self.cwd = Path(cwd) if cwd is not None else Path(__file__).resolve().parents[2]
        self.harness_cmd = harness_cmd or self._default_harness_cmd()
        self.upgrade_policy = upgrade_policy
        self.last_info = None
        self.last_observation = None
        self.upgrade_policy_decision_count = 0
        self.process = None
        self.observation_len = None
        self.action_count = None
        self._start_bridge()

        spec = self._request({"command": "spec"})
        self.observation_len = spec["info"]["observation_len"]
        self.action_count = spec["info"]["action_count"]
        self.action_space = spaces.Discrete(self.action_count)
        self.observation_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(self.observation_len,),
            dtype=np.float32 if np is not None else "float32",
        )

    def _default_harness_cmd(self):
        raw = os.environ.get("SOFT_CANDY_HARNESS_CMD")
        if raw:
            return shlex.split(raw)
        return [
            "cargo",
            "run",
            "-q",
            "-p",
            "game_harness",
            "--",
            "gym-bridge",
        ]

    def _normalize_map_ids(self, map_ids, fallback):
        if map_ids is None:
            return [fallback]
        normalized = [map_id.strip() for map_id in map_ids if map_id.strip()]
        if not normalized:
            raise ValueError("map_ids must include at least one map id")
        return normalized

    def _select_map_id(self, explicit_map_id=None):
        if explicit_map_id is not None:
            return explicit_map_id
        if len(self.map_ids) == 1:
            return self.map_ids[0]
        if self.map_selection == "random":
            rng = random.Random(self.seed_value + self.episode_index)
            selected = rng.choice(self.map_ids)
        else:
            selected = self.map_ids[self.episode_index % len(self.map_ids)]
        self.episode_index += 1
        return selected

    def _start_bridge(self):
        cmd = [
            *self.harness_cmd,
            "--seed",
            str(self.seed_value),
            "--seconds",
            str(self.seconds),
            "--tick-rate",
            str(self.tick_rate),
            "--observation-version",
            str(self.observation_version),
            "--map-id",
            self.map_id,
            "--content-dir",
            self.content_dir,
        ]
        self.process = subprocess.Popen(
            cmd,
            cwd=self.cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

    def _request(self, payload):
        if self.process is None or self.process.poll() is not None:
            raise RuntimeError("gym bridge process is not running")
        self.process.stdin.write(json.dumps(payload, separators=(",", ":")) + "\n")
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        if not line:
            raise RuntimeError("gym bridge closed without a response")
        response = json.loads(line)
        if response.get("status") != "ok":
            raise RuntimeError(response.get("error") or "gym bridge request failed")
        return response

    def _observation(self, values):
        if np is None:
            return values
        return np.asarray(values, dtype=np.float32)

    def reset(self, *, seed=None, options=None):
        if seed is not None:
            self.seed_value = seed
        options = options or {}
        map_id = self._select_map_id(options.get("map_id"))
        payload = {
            "command": "reset",
            "seed": self.seed_value,
            "map_id": map_id,
            "seconds": options.get("seconds", self.seconds),
            "tick_rate": options.get("tick_rate", self.tick_rate),
        }
        response = self._request(payload)
        self.map_id = response["info"]["map_id"]
        self.seconds = options.get("seconds", self.seconds)
        self.tick_rate = options.get("tick_rate", self.tick_rate)
        self.last_info = response["info"]
        self.last_observation = response["observation"]
        self.upgrade_policy_decision_count = 0
        return self._observation(response["observation"]), response["info"]

    def step(self, action):
        payload = {"command": "step", "action": int(action)}
        upgrade_decision = self._upgrade_choice_for_pending_prompt()
        if upgrade_decision is not None:
            payload["upgrade_choice"] = int(upgrade_decision["choice_index"])
        response = self._request(payload)
        info = response["info"]
        if upgrade_decision is not None:
            self.upgrade_policy_decision_count += 1
            info["upgrade_policy_decision"] = upgrade_decision
            info["upgrade_policy_decision_count"] = self.upgrade_policy_decision_count
        self.last_info = info
        self.last_observation = response["observation"]
        return (
            self._observation(response["observation"]),
            float(response["reward"]),
            bool(response["terminated"]),
            bool(response["truncated"]),
            info,
        )

    def _upgrade_choice_for_pending_prompt(self):
        if self.upgrade_policy is None or not self.last_info:
            return None
        options = self.last_info.get("upgrade_options") or []
        if not options:
            return None
        observation = self.last_observation
        chooser = getattr(self.upgrade_policy, "choose", None)
        if callable(chooser):
            result = chooser(observation, options)
        elif callable(self.upgrade_policy):
            result = self.upgrade_policy(observation, options)
        else:
            raise RuntimeError("upgrade_policy must expose choose(observation, options) or be callable")
        if isinstance(result, dict):
            choice_index = int(result["choice_index"])
            decision = dict(result)
        else:
            choice_index = int(result)
            decision = {"choice_index": choice_index}
        if choice_index < 0 or choice_index >= len(options):
            raise RuntimeError(
                f"upgrade_policy returned {choice_index} for {len(options)} upgrade options"
            )
        decision.setdefault("choice_upgrade_id", options[choice_index])
        decision.setdefault("upgrade_options", list(options))
        decision.setdefault("policy_kind", type(self.upgrade_policy).__name__)
        return decision

    def close(self):
        process = getattr(self, "process", None)
        if process is None:
            return
        if process.poll() is None:
            try:
                self._request({"command": "close"})
            except RuntimeError:
                pass
            try:
                process.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
        self.process = None

    def __del__(self):
        self.close()
