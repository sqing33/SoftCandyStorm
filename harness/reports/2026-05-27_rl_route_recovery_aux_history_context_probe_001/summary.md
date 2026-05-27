# Route Recovery Aux History Context Probe

## 结论

- Gate decision: `history_context_probe_recorded_watch_only`
- 对象：`route_recovery_aux_entropy_retry` staged GRU context8 checkpoint
- Trace：`soda-creek` seed `62300` 的 60 秒 sampled online trace
- 数据集：route_recovery repair samples + phase-aligned KiteBot high-pressure 三图轨迹
- 结论：当前证据更支持 `transition/recovery sequence context mismatch`，而不是“当前 observation 下无条件动作塌缩”。

该 probe 对同一目标 observation 分别比较：

- `cold`：无历史前缀。
- `online_prefix`：使用 online trace 中目标帧前 7 个采样帧作为 GRU history。
- `teacher_prefix`：使用最近邻 teacher episode 中目标样本前 7 个样本作为 GRU history。

## 关键发现

`30-35s` 窗口共 `15` 个样本，online action 全部为 `5`。nearest teacher target 主要是 action `8`，占 `0.8000`；但 `cold` 与 `online_prefix` 的 top action 都是 `5`，`teacher_prefix` 也有 `13/15` 个样本仍 top `5`。这说明该窗口中当前 online observation 已足以把模型推向 action `5`，history prefix 不是唯一驱动。

`55-60s` 窗口共 `15` 个样本，online action 全部为 `3`。nearest teacher target 主要是 action `2`，占 `0.6000`。`cold` 与 `online_prefix` 仍全部 top `3`，但 `teacher_prefix` 的 top action 分布变为 action `2` 占 `0.6000`、action `3` 占 `0.2667`、action `4` 占 `0.1333`。这说明同一目标 observation 在 teacher history 下会更接近恢复动作，而 online history 会把策略稳定在继续向右的 action `3`。

## 门禁解释

该报告只是诊断证据：

- 不证明 checkpoint 可作为策略候选。
- 不替代 deterministic high-pressure 60 / 180 / 300 秒多图门禁。
- 不替代 Replay 回归。
- 不替代人工试玩。

后续修复应优先围绕 `55-60s` 右边界窗口构造 teacher-prefix 一致的恢复训练，或显式比较 online-prefix / teacher-prefix 的 hidden-state 行为约束；不要继续只增加 epoch、entropy regularization 或泛化 sample weight。

## 输出文件

- `history_context_probe.json`
- `history_context_probe.md`
