# Terminal Branch Usage Real Report

- item_id: `rl_terminal_branch_usage_real_report`
- gate_decision: `repair`
- 结论: `terminal branch 已实际介入，但 300 秒 high-pressure 仍未形成胜利转换`

## 输入

- base model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- terminal model: `harness/reports/2026-05-29_rl_sb3_terminal_victory_multimap_path_target_w1_e30_001/ppo_terminal_victory_multimap_path_target_w1_e30.zip`
- maps: `soda-creek,caramel-workshop,cracked-star-jar`
- terminal window: `210-240s`
- seed_start: `63100`
- eval: `3 seeds * 300s`

## 结果

真实 comparison 已确认 `policy_adapter.usage_scope = multimap_aggregate`，顶层 usage 聚合了三张 high-pressure 地图：

- total decisions: `44904`
- terminal decisions: `2996`
- terminal ratio: `0.0667`
- late_180_to_300 terminal ratio: `0.3247`

按地图统计：

- `soda-creek`: terminal `662 / 13996`, ratio `0.0473`
- `caramel-workshop`: terminal `819 / 14257`, ratio `0.0574`
- `cracked-star-jar`: terminal `1515 / 16651`, ratio `0.091`

300 秒 high-pressure 胜率仍为：

- `soda-creek`: `0.0`
- `caramel-workshop`: `0.0`
- `cracked-star-jar`: `0.0`

## 结论

这轮证据排除了“terminal branch 没有被调用”这一诊断假设。分支在 210-240 秒窗口内确实介入，且 late bucket 内约三分之一决策使用 terminal model，但仍没有带来 300 秒胜利转换。

下一步不应继续只调 dispatch 阈值或扩大同一 victory target 权重；应改做 per-map terminal objective，或重新收集更贴近失败前状态的 conversion target，并继续保留 parent/e30 fixed-window no-regression 与 repair-probe gate。

## 验证

- `env UV_CACHE_DIR=/private/tmp/soft-candy-uv-cache PYTHONPYCACHEPREFIX=/private/tmp/soft-candy-pycache uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py --algorithm ppo --compare-rule-bots --compare-map-preset high-pressure --model harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip --terminal-conversion-model harness/reports/2026-05-29_rl_sb3_terminal_victory_multimap_path_target_w1_e30_001/ppo_terminal_victory_multimap_path_target_w1_e30.zip --terminal-conversion-maps soda-creek,caramel-workshop,cracked-star-jar --terminal-conversion-min-seconds 210 --terminal-conversion-max-seconds 240 --seed-start 63100 --eval-episodes 3 --eval-seconds 300 --rule-bots random,kite,tank --report harness/reports/2026-05-29_rl_terminal_branch_usage_real_report_001/comparison_300s.json`
