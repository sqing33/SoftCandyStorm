# Stage 02 Late Repair Probe

## 结论

- Gate decision: `late_repair_probe_rejected_opening_regression`
- Model: `staged.pt`
- Late submodel: `late.pt`
- Source samples: `harness/reports/2026-05-28_rl_curriculum_stage02_late_recovery_samples_001/late_route_recovery_samples.jsonl`
- Failure case: `harness/failed_cases/fail_20260528_066_stage02_late_repair_probe_opening_regression.json`

本实验只用 stage 02 的 527 条 late route-recovery repair samples 训练新的 GRU context8 late 子模型，并保留既有 opening / mid 子模型打包成 staged behavior clone。该实验是 repair probe，不是 RL acceptance evidence。

结果：probe 被拒绝。它没有修复 300 秒窗口，反而破坏了短窗 opening 表现。60 秒 high-pressure 三图从 stage 02 PPO 的 `1.0/1.0/1.0` 降到 `0.3333/1.0/0.6667`；300 秒三图为 `0.0/0.0/0.0`，且 9/9 全失败。

## Deterministic High-pressure Results

| Probe | Soda | Caramel | Cracked | Gate |
| --- | ---: | ---: | ---: | --- |
| `60s` | `0.3333` | `1.0` | `0.6667` | `multimap_comparison_recorded_watch` |
| `180s` | `0.3333` | `1.0` | `0.6667` | `multimap_comparison_recorded_watch` |
| `300s` | `0.0` | `0.0` | `0.0` | `multimap_comparison_recorded_needs_policy_repair` |

## Failure Analysis

| Probe | Total failures | Key buckets | Dominant issue |
| --- | ---: | --- | --- |
| `60s` | `3` | soda opening `2`, cracked opening `1` | action `3` dominates early failures |
| `300s` | `9` | soda opening `2` / late `1`, caramel late `3`, cracked opening `1` / late `2` | action `3` early, action `1` late |

该 probe 证明 late route-recovery samples 是有效训练输入，但单独使用时训练上下文不足。新的 late 子模型过拟合 repair labels，并让阶段行为失稳，因此不能作为候选策略。

## Next

Do not continue this checkpoint with more epochs. The next repair should mix these late route-recovery rows with clean late survival trajectories and explicit no-regression checks, or move back to closed-loop PPO reward shaping. Any new experiment must keep the same 60 / 180 / 300 秒三窗比较。

## 输出文件

- `late_training.json`
- `late.pt`
- `packaging.json`
- `staged.pt`
- `comparison_60s.json`
- `comparison_180s.json`
- `comparison_300s.json`
- `failure_analysis_60s.json`
- `failure_analysis_60s.md`
- `failure_analysis_300s.json`
- `failure_analysis_300s.md`
