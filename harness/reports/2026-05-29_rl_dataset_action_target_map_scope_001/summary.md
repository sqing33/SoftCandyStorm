# Dataset Action Target Map Scope

- item_id: `rl_dataset_action_target_map_scope`
- gate_decision: `tooling_validated`
- 结论: `complete`

## 变更

`distill_behavior_clone_to_sb3.py` 新增 `--dataset-action-target-maps <map-id,...>`，用于把 `--dataset-action-target-path` 的 dataset-action hard target 覆写限制到指定地图。

这让同一个多图 victory terminal JSONL 可以支持 per-map terminal objective：

- 目标地图样本：使用 dataset action one-hot target。
- 同一路径下非目标地图样本：保留原 teacher / recovery target。
- 报告字段：`dataset_action_target_override.maps`、`map_scoped_out_sample_count` 和每个 path entry 的 `map_scoped_out_sample_count`。

该能力只是训练输入选择工具，不是 policy candidate、stage 03 或 RL acceptance 证据。任何使用该入口训练出的 terminal branch 仍必须通过 full-anchor alignment、parent/e30 fixed-window no-regression、online action-distribution delta 和 repair-probe gate。

## 验证

- `env PYTHONPYCACHEPREFIX=/private/tmp/soft-candy-pycache python3 -m py_compile python/train/distill_behavior_clone_to_sb3.py python/train/test_distill_behavior_clone_to_sb3.py`
- `env UV_CACHE_DIR=/private/tmp/soft-candy-uv-cache PYTHONPYCACHEPREFIX=/private/tmp/soft-candy-pycache uv run --with pytest --with-requirements python/train/requirements.txt pytest python/train/test_distill_behavior_clone_to_sb3.py -q`

结果：`16 passed`。
