# Opening Mid Boundary Retention Reward Profile

## 目标

为 `retention63405` lane 增加训练期入口：`opening-mid-boundary-retention` 覆盖 `0-180s`，同时保留 opening boundary escape 与 mid-window route/path retention 信号，避免把 seed `63405` 误转成纯 late low-health 修复。

## 实现

- Rust `gym-bridge` 新增 `GymRewardProfile::OpeningMidBoundaryRetention`，CLI 字符串为 `opening-mid-boundary-retention`。
- profile scale 在 `0-180s` 为 `1.0`，`180s` 后关闭。
- opening boundary escape 只在 `0-60s` 生效；route recovery、安全、边界、低血量、敌压、危险区和 action-repeat 信号覆盖 `0-180s`。
- Python Gym wrapper 与 `train_sb3.py --reward-profile` choices 已接入该 profile。

## 验证

- `cargo test -p game_harness gym_opening_mid_boundary_retention_profile_spans_opening_and_mid`
- `cargo test -p game_harness gym_reward_profile_parses_profiles`
- `uv run --with pytest python -m pytest python/gym_env/test_soft_candy_env.py -q`
- `uv run --with pytest --with-requirements python/train/requirements.txt python -m pytest python/train/test_train_sb3.py -k "reward_profile" -q`
- `python/train/train_sb3.py --dry-run --algorithm ppo --steps 90 --reward-profile opening-mid-boundary-retention --train-maps caramel-workshop --train-seeds 63405 --train-seed-selection cycle --train-seconds 180 --eval-seconds 180`

Dry-run 写入 `dry_run.json`：`reward_profile` 为 `opening-mid-boundary-retention`，`map_id` 为 `caramel-workshop`，`seed` 为 `63405`，`observation_len` 为 `145`，`action_count` 为 `9`。

## 结论

结论：`simulate`，但仅表示训练入口和 dry-run plumbing 可用。它不是 policy candidate、stage 03 或 RL acceptance；任何真实 checkpoint 仍必须按 `lane_action_plan_seed63405` 通过 seed `63405` retention preflight、`60s/caramel-workshop` hard preflight、parent no-regression、10 seed follow-up 和 failure-case review。
