# 胜利路径目标覆写 w20 对照

- item_id: `rl_sb3_terminal_victory_path_target_w20_e30`
- gate_decision: `behavior_clone_anchor_alignment_failed`
- 结论: `repair`

## 结果

该探针保留 `target-mode teacher_probs`，只对 `cracked-star-jar` 胜利终局 `210-240s` 样本路径使用 dataset action one-hot target，并将该路径权重设为 `20x`。`dataset_action_target_override.overridden_sample_count = 358`。

## Blockers

- `anchor_drift_alignment.json`: 通过，mean KL `0.030720`，argmax agreement `0.975`
- `full_anchor_alignment.json`: 失败，overall argmax agreement `0.7781 < 0.8`
- `opening_lt_60`: mean KL `0.287821 > 0.25`

## 结论

路径级 target override 比全局 dataset action 明显安全，但 `20x` 仍过重，会破坏 full-anchor retention。该结果只作为权重消融证据，不进入在线 branch 对比。
