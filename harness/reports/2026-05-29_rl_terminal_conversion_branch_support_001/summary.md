# RL Terminal Conversion Branch Support

## 结论

- Decision: `tool_support_added_not_policy_gate`
- Tool: `python/train/train_sb3.py`
- Adapter mode: `terminal_conversion_branch`
- Tests: `python/train/test_train_sb3.py`

本次新增显式 terminal-conversion branch 评估入口，用于替代继续调整 `terminal-window` scoped risk sample weight。该入口仍只用于诊断和 repair probe，不是 RL acceptance 或 policy candidate 证据。

## 新能力

`train_sb3.py` 现在可以在 evaluation / comparison 中通过以下参数接入独立 terminal branch：

- `--terminal-conversion-model`
- `--terminal-conversion-maps`
- `--terminal-conversion-min-seconds`
- `--terminal-conversion-max-seconds`
- `--terminal-conversion-min-pressure`
- `--terminal-conversion-min-low-health-risk`

`TerminalConversionBranchPolicy` 只在同时满足以下条件时把 base policy 切到 terminal model：

- 当前 map 在 `--terminal-conversion-maps`
- 当前时间落在 `min_seconds..=max_seconds`
- 若配置了压力阈值，则 online diagnostics 的 hazard / boss / enemy combined pressure 达标
- 若配置了低血量阈值，则 `low_health_risk` 达标

如果未配置 pressure / low-health 阈值，则该 wrapper 退化为 map + time-window branch；如果配置任一阈值，则只有显式命中阈值时才切换，避免把健康 late window 整段替换掉。

## 验证

已通过：

```bash
env UV_CACHE_DIR=/private/tmp/soft-candy-uv-cache PYTHONPYCACHEPREFIX=/private/tmp/soft-candy-pycache uv run --with pytest --with-requirements python/train/requirements.txt pytest python/train/test_train_sb3.py
```

结果：`50` tests passed。

另外通过：

```bash
env PYTHONPYCACHEPREFIX=/private/tmp/soft-candy-pycache python3 -m py_compile python/train/train_sb3.py
```

## 限制

- 本报告只证明显式 terminal branch dispatch 入口可用。
- 尚未产生新的 terminal-conversion checkpoint，也没有解除 300 秒 high-pressure blocker。
- 后续真实 probe 必须继续跑 full-anchor alignment、60 / 180 / 300 秒 high-pressure、e30 + parent no-regression、online action-distribution delta、failure analysis 和 repair-probe gate。
