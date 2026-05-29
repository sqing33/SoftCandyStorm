# SB3 Distillation Action Distribution Guard Support

## 结论

- Decision: `tooling_support_validated`
- Scope: `python/train/distill_behavior_clone_to_sb3.py`
- Test: `python/train/test_distill_behavior_clone_to_sb3.py`

`distill_behavior_clone_to_sb3.py` 现在会在 supervised SB3 distillation 的 validation slices 中记录预测 argmax 动作分布、dominant action ratio、argmax action entropy 和 normalized argmax action entropy。分桶覆盖：

- overall validation set
- `sample_source`
- `--sample-path-weight` 命中路径
- `map_id::time_bucket`

新增 CLI guard：

- `--action-distribution-guard-max-dominant-ratio`
- `--action-distribution-guard-min-normalized-entropy`
- `--action-distribution-guard-min-sample-count`

当任意满足最小样本数的 slice 超过 dominant action ratio 或低于 normalized entropy 阈值时，distillation report 会写入 `action_distribution_guard_failed`，并把 `gate_decision` 标为 `sb3_distillation_action_distribution_guard_failed_not_policy_gate`。

## 验证

已通过：

```bash
env UV_CACHE_DIR=/private/tmp/soft-candy-uv-cache PYTHONPYCACHEPREFIX=/private/tmp/soft-candy-pycache uv run --with pytest --with-requirements python/train/requirements.txt pytest python/train/test_distill_behavior_clone_to_sb3.py
```

结果：`12 passed`。

## 限制

- 该 guard 是离线 distillation evidence guard，不是 RL acceptance。
- 该 guard 不能证明 300 秒 high-pressure 已修复。
- 后续 terminal-window repair 仍必须运行 anchor alignment、60 / 180 / 300 秒 high-pressure、e30 + parent no-regression、failure analysis 和 repair-probe gate。
