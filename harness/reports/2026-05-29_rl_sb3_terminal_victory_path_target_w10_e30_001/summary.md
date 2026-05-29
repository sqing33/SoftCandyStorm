# 胜利路径目标覆写 w10 对照

- item_id: `rl_sb3_terminal_victory_path_target_w10_e30`
- gate_decision: `behavior_clone_anchor_alignment_failed`
- 结论: `repair`

## 结果

该探针将胜利终局路径权重从 `20x` 降到 `10x`，继续只对匹配路径样本使用 dataset action one-hot target。`dataset_action_target_override.overridden_sample_count = 358`。

## Blockers

- `anchor_drift_alignment.json`: 通过，mean KL `0.028967`，argmax agreement `0.98`
- `full_anchor_alignment.json`: 失败，overall argmax agreement `0.7973 < 0.8`

## 结论

`w10` 已非常接近 full-anchor 门槛，但仍不能通过硬门禁。后续主线采用 `w5` 做更保守的 parent-preservation 和 300 秒 branch probe。
