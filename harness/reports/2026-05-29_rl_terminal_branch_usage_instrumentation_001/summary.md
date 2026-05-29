# Terminal Branch Usage Instrumentation

- item_id: `rl_terminal_branch_usage_instrumentation`
- gate_decision: `tooling_validated`
- 结论: `complete`

## 变更

`TerminalConversionBranchPolicy` 现在会在 `predict()` 时记录本步实际使用 base policy 还是 terminal policy，并在 `policy_adapter.usage` 中输出：

- `total_decisions`
- `base_decisions`
- `terminal_decisions`
- `terminal_ratio`
- `by_map`
- `by_time_bucket`

多地图 comparison 顶层会把各地图的 usage 聚合为 `usage_scope = multimap_aggregate`，避免把第一张地图的分支使用量误读为全局统计。

这只用于诊断 terminal-conversion branch 实际介入量，不能替代 parent / e30 fixed-window no-regression、online action-distribution delta、failure analysis 或 repair-probe gate。

## 验证

- `env PYTHONPYCACHEPREFIX=/private/tmp/soft-candy-pycache python3 -m py_compile python/train/train_sb3.py python/train/test_train_sb3.py`
- `env UV_CACHE_DIR=/private/tmp/soft-candy-uv-cache PYTHONPYCACHEPREFIX=/private/tmp/soft-candy-pycache uv run --with pytest --with-requirements python/train/requirements.txt pytest python/train/test_train_sb3.py -q`

结果：`51 passed`。
