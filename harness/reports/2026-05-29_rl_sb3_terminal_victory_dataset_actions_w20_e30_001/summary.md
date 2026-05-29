# 全局 dataset action 终局胜利对照

- item_id: `rl_sb3_terminal_victory_dataset_actions_w20_e30`
- gate_decision: `behavior_clone_anchor_alignment_failed`
- 结论: `reject`

## 结果

该对照把 distillation target 全局切成 `dataset_actions`，并把胜利终局样本路径权重设为 `20x`。离线 action-distribution guard 通过，胜利样本切片 accuracy 可达 `0.9041`，但 retention 明显破坏。

## Blockers

- `anchor_drift_alignment.json`: mean KL `1.543488`，超过 `0.25`
- `full_anchor_alignment.json`: mean KL `0.405769`，argmax agreement `0.7485`
- `opening_lt_60`: mean KL `1.676031`

## 结论

全局 dataset action target 不能作为 terminal-conversion branch 路线继续推进。后续应只对明确路径样本覆写 dataset action，并保留 teacher probabilities 与 parent / e30 retention anchors。
