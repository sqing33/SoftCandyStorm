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
        content_dir="content/base_demo",
        harness_cmd=None,
        cwd=None,
    ):
        self.seed_value = seed
        self.seconds = seconds
        self.tick_rate = tick_rate
        self.map_ids = self._normalize_map_ids(map_ids, map_id)
        self.map_selection = map_selection
        if self.map_selection not in {"cycle", "random"}:
            raise ValueError("map_selection must be `cycle` or `random`")
        self.map_id = self.map_ids[0]
        self.episode_index = 0
        self.content_dir = content_dir
        self.cwd = Path(cwd) if cwd is not None else Path(__file__).resolve().parents[2]
        self.harness_cmd = harness_cmd or self._default_harness_cmd()
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
        return self._observation(response["observation"]), response["info"]

    def step(self, action):
        response = self._request({"command": "step", "action": int(action)})
        return (
            self._observation(response["observation"]),
            float(response["reward"]),
            bool(response["terminated"]),
            bool(response["truncated"]),
            response["info"],
        )

    def close(self):
        if self.process is None:
            return
        if self.process.poll() is None:
            try:
                self._request({"command": "close"})
            except RuntimeError:
                pass
            try:
                self.process.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                self.process.terminate()
                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.process.kill()
        self.process = None

    def __del__(self):
        self.close()
