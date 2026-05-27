# Opening Action3 Late Recovery Samples

## 结论

- Gate decision: `late_recovery_samples_recorded_not_policy_gate`
- Source checkpoint: `harness/reports/2026-05-27_rl_action_distribution_opening_action3_low_weight_ablation_001/opening_action3_w0_5_windowed/staged.pt`
- Source trace: `harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_trace_001/summary.md`
- Source failure case: `harness/failed_cases/fail_20260527_049_action_distribution_opening_action3_late_gap.json`
- Adapter comparison: `adapter_comparison_300s.json`

本轮基于新的 opening action `3` 低权重 staged checkpoint，使用 `--late-recovery-filter --late-recovery-min-seconds 180` 导出 `risk_recovery_supervision_sample`。导出结果只作为 late repair training input，不是 policy gate、playtest 或 release 证据。

## Adapter Probe

| Map | Adapter win rate | Avg survival | Dominant action | Entropy | Samples |
| --- | ---: | ---: | --- | ---: | ---: |
| `soda-creek` | `0.2` | `183.8447s` | action `1` `0.4142` | `0.7724` | `257` |
| `caramel-workshop` | `0.0` | `227.5196s` | action `1` `0.3465` | `0.7894` | `115` |
| `cracked-star-jar` | `0.2` | `220.0559s` | action `1` `0.4377` | `0.7569` | `408` |

Adapter overall gate 仍为 `multimap_comparison_recorded_needs_policy_repair`。它能把 `soda-creek` 和 `cracked-star-jar` 从 300 秒 `0.0` 拉到 `0.2`，但 `caramel-workshop` 仍为 `0.0`，所以不能把 adapter 结果当作修复完成。

## Sample Set

| Map | Samples | Time range |
| --- | ---: | --- |
| `soda-creek` | `257` | `180.0095-293.9831s` |
| `caramel-workshop` | `115` | `180.0095-243.7564s` |
| `cracked-star-jar` | `408` | `180.0095-297.6156s` |

总计 `780` 条样本，dry-run 判定 `dataset_validated_not_training_gate`。`time_phase_filter=late` 后仍保留 `780/780`，`risk_recovery_min/max_seconds=180/300` 后仍保留 `780/780`，说明样本全部位于 late 窗口。

## Distributions

Risk reasons:

- `toward_enemy_pressure`: `422`
- `toward_hazard`: `185`
- `wallward_edge`: `158`
- `toward_boss`: `65`

Original action distribution:

- action `1`: `83`
- action `2`: `116`
- action `3`: `105`
- action `4`: `103`
- action `5`: `64`
- action `6`: `125`
- action `7`: `83`
- action `8`: `101`

Target action distribution:

- action `0`: `32`
- action `1`: `79`
- action `2`: `63`
- action `3`: `144`
- action `4`: `89`
- action `5`: `147`
- action `6`: `46`
- action `7`: `101`
- action `8`: `79`

## 判断

- 这批样本覆盖当前 checkpoint 的 180-300 秒 mixed-pressure failure surface，尤其是 enemy/hazard/wallward edge。
- adapter 仍未通过 300 秒三图，说明这些样本必须进入受控 late-only 消融，不能直接推进。
- 下一步应保留 `opening_action3_w0_5_windowed` opening 子模型，只重训 late 子模型；先跑 60 秒 hard gate 与 180 秒 regression，再跑 300 秒三图。

## 输出文件

- `adapter_comparison_300s.json`
- `behavior_clone_dry_run.json`
- `risk_recovery_samples_soda-creek.jsonl`
- `risk_recovery_samples_caramel-workshop.jsonl`
- `risk_recovery_samples_cracked-star-jar.jsonl`
