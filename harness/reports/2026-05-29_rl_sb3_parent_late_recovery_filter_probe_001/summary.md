# SB3 Parent Late Recovery Filter Probe

## 结论

- Decision: `sb3_parent_late_recovery_filter_probe_rejected_adapter_only`
- Parent model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Policy adapter: `late_recovery_filter`
- Evaluation: high-pressure / 300s / 3 seed / deterministic
- Gate decision: `multimap_comparison_recorded_needs_policy_repair`
- Failure analysis: `rl_policy_failure_analysis_recorded`
- Sample validation: `risk_recovery_samples_valid`
- Failure case: `harness/failed_cases/fail_20260529_009_sb3_parent_late_recovery_filter_probe_adapter_only.json`

该 probe 不训练新 checkpoint，而是把上一轮 mid-anchor parent 包上一层 deterministic `late_recovery_filter`，从 `180s` 后根据边界、hazard、Boss / enemy pressure 和低血量上下文改写高风险动作，并导出 parent late-state repair samples。

结果只能作为诊断和训练材料。adapter 让 `soda-creek` 出现 `0.3333` 的 300 秒胜率，但 `caramel-workshop` 和 `cracked-star-jar` 仍为 `0.0`，总体平均胜率只有 `0.1111`，failure analysis 仍记录 `8` 个失败局。因为该收益来自手写 wrapper，不是 learned policy 本体，所以不能作为 RL acceptance、policy candidate 或 stage 03 证据。

## 300s High-pressure

| Map | Win rate | Avg survival | Dominant action | Entropy | Samples |
| --- | ---: | ---: | --- | ---: | ---: |
| `soda-creek` | `0.3333` | `192.6578s` | `1` / `26.94%` | `0.8229` | `123` |
| `caramel-workshop` | `0.0` | `162.6801s` | `3` / `21.43%` | `0.8297` | `93` |
| `cracked-star-jar` | `0.0` | `190.7907s` | `5` / `22.13%` | `0.8552` | `223` |

`comparison_300s.json` 的 `policy_adapter.limitations` 已明确说明该 wrapper 只能产出 late-window supervision samples，不能作为 RL policy acceptance evidence。

## Failure Analysis

- Total failures: `8`
- Repair maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`
- `soda-creek`: `1` 个 opening failure，`1` 个 late failure
- `caramel-workshop`: `1` 个 opening failure，`2` 个 late failures
- `cracked-star-jar`: `1` 个 opening failure，`2` 个 late failures

和上一轮三图全失败相比，adapter 有局部收益，但它没有解决多图 300 秒转换，也没有把失败面从 repair 状态推进到 acceptance 状态。

## Risk Recovery Samples

`risk_recovery_samples_validation.json` 合并校验三图样本：

- decision: `risk_recovery_samples_valid`
- samples: `439`
- time range: `180.0095s` to `299.8817s`
- maps: `caramel-workshop`, `cracked-star-jar`, `soda-creek`
- seeds: `63100`, `63101`, `63102`

风险原因分布：

- `wallward_edge`: `173`
- `toward_enemy_pressure`: `169`
- `toward_hazard`: `124`
- `toward_boss`: `6`

目标动作风险原因分布：

- `<none>`: `425`
- `toward_enemy_pressure`: `7`
- `idle_under_late_pressure`: `6`
- `toward_boss`: `1`

校验有 `1` 条 warning：`soda-creek` seed `63102` 的一条样本 target risk score 高于 original。这不阻止样本结构通过，但后续训练应优先考虑 clean subset、低权重消融或显式 target-risk 过滤。

## 判断

- 该 adapter 不是 learned policy，也不是 RL acceptance 证据。
- `soda-creek` 的局部胜局说明 parent late-state 里存在可提取的 action repair 信号。
- `cracked-star-jar` 和 `caramel-workshop` 仍为 0% 300 秒胜率，说明仅靠 deterministic late-risk wrapper 不能完成 terminal conversion。
- 下一步应把这批 parent late-state samples 作为 action-separation / terminal-conversion 分支的诊断输入，并继续保留 e30 + parent 多基线 no-regression、risk sample validator 和 60/180/300 秒 high-pressure gate。

## 输出文件

- `comparison_300s.json`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
- `risk_recovery_samples_validation.json`
- `risk_recovery_samples_validation.md`
- `soda_late_recovery_samples_validation.json`
- `soda_late_recovery_samples_validation.md`
- `caramel_late_recovery_samples_validation.json`
- `caramel_late_recovery_samples_validation.md`
- `cracked_late_recovery_samples_validation.json`
- `cracked_late_recovery_samples_validation.md`
- `late_recovery_samples/soda-creek_edge_recovery_samples.jsonl`
- `late_recovery_samples/caramel-workshop_edge_recovery_samples.jsonl`
- `late_recovery_samples/cracked-star-jar_edge_recovery_samples.jsonl`
- `traces/`
