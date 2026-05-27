# Recovery Soft Target Training Support

## 结论

- Gate decision: `tooling_validated_not_policy_gate`
- Tool: `python/train/train_behavior_clone.py`
- Mode: `--recovery-soft-target top_k_scores`
- Test: `uv run --with-requirements python/train/requirements.txt --with pytest python -m pytest python/train/test_train_behavior_clone.py`
- Dry-run: `soft_target_dry_run.json`

行为克隆训练现在支持对 `edge_recovery_supervision_sample` 和 `risk_recovery_supervision_sample` 使用 soft/top-k target。默认仍为 `none`，旧训练命令保持硬标签行为；只有显式传入 `--recovery-soft-target top_k_scores` 时才启用。

## 行为

- `--recovery-soft-target-primary-mass` 控制 repair target action 的主质量，默认 `0.65`
- `--recovery-soft-target-top-k` 控制包含 target action 在内的最大动作数，默认 `3`
- `original_action` 会从 soft target 候选里排除，避免把 wallward 或风险动作重新训练回去
- `action_scores.top_actions` 支持整数或字符串 action id，兼容现有 trace 导出
- dry-run 报告会写出 `recovery_soft_targets`，便于训练前审查覆盖情况

## Dry Run

使用当前 opening 混合数据集验证：

- Sample count: `5760`
- Edge recovery samples: `372`
- Soft sample count: `372`
- Fallback one-hot count: `0`
- Average nonzero actions: `1.1172`
- Primary mass: `0.6`
- Top-k: `3`

## 判断

该能力只证明训练工具可以表达 soft/top-k repair target，不证明任何 policy 可推进。下一步需要用同一 opening 训练集训练一个 soft target 消融，再用 60 秒 high-pressure 三图 deterministic gate 验证是否避免 action `3` / action `6` 偏置迁移。

## 输出文件

- `soft_target_dry_run.json`
