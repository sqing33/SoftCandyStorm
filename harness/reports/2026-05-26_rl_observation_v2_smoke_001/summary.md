# RL Observation V2 Smoke 001

日期：2026-05-26

## 目标

补齐 Gym observation 中缺失的地图、Boss、hazard 和中后期威胁表达能力，为修复 `fail_20260526_011` 的 PPO 跨地图泛化失败打基础。

## 变更

- `game_harness gym-bridge` 支持 `--observation-version 1|2`。
- 默认 observation 切到 v2，长度为 145。
- v1 保留 82 维，用于旧模型分析。
- v2 新增玩家拾取半径、伤害倍率、冷却倍率、敌人相对速度/半径/精英/行为嵌入、active hazard 最近方向、Boss 汇总、地图尺寸和角落距离。
- Python `SoftCandyStormEnv` 支持 `observation_version`，训练配置默认使用 v2。

## 验证

- `cargo fmt --check`
- `cargo test -p game_harness gym_observation_has_stable_length -- --nocapture`
- `cargo test --workspace`
- `cargo clippy --workspace --all-targets`
- `game_harness gym-bridge --observation-version 1` spec 返回 `observation_len = 82`
- `game_harness gym-bridge --observation-version 2` spec 返回 `observation_len = 145`
- `python3 python/gym_env/smoke_test.py`
- `python3 python/train/train_sb3.py --dry-run --algorithm ppo --steps 10 --report harness/reports/2026-05-26_rl_observation_v2_smoke_001/ppo_observation_v2_dry_run.json`

## Smoke 结果

```json
{
  "status": "ok",
  "mode": "dry_run",
  "algorithm": "ppo",
  "steps": 10,
  "observation_len": 145,
  "action_count": 9
}
```

## 结论

v2 observation 已能覆盖 docs/09 中“地图状态”和高压威胁表达的关键缺口。下一步应使用 v2 重新训练 PPO，而不是继续比较旧 82 维 observation 模型。
