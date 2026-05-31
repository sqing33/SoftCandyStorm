# mid-path-retention reward profile

## 结论

`mid-path-retention` 已接入 Rust `gym-bridge`、Python Gym wrapper 和 `train_sb3.py` CLI。该 profile 专门用于 60-180 秒 handoff / mid-window path retention 训练探针：60 秒前不加权，60-90 秒 ramp up，90-180 秒保持 active，180 秒后关闭，避免把 seed `63407` 的中窗路径保留信号误扩展成 180 秒后的 low-health-only 或 late conversion objective。

## 验证

- `cargo fmt --check`
- `cargo test -p game_harness gym_mid_path_retention_profile_focuses_handoff_window`
- `cargo test -p game_harness gym_reward_profile_parses_profiles`
- `uv run --with pytest pytest python/gym_env/test_soft_candy_env.py python/train/test_train_sb3.py -q`
- `python3 python/train/train_sb3.py --algorithm ppo --dry-run --steps 2 --reward-profile mid-path-retention --train-map-preset high-pressure --train-map-selection random --train-seconds 300 --eval-seconds 180 --report harness/reports/2026-05-31_rl_mid_path_retention_reward_profile_001/dry_run.json`

## 限制

该报告只证明训练目标入口和 CLI/包装器链路可用；尚未训练新 checkpoint，也不能替代 10 seed caramel target follow-up、60/180/300 秒 high-pressure no-regression、adapter provenance 或 RL acceptance。
