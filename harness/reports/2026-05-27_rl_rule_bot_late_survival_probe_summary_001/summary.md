# RL Rule Bot Late Survival Probe Summary

- Decision: `teacher_selection_probe_recorded`
- Scope: 规则 Bot 300 秒长局生存轨迹候选选择
- Maps: `soda-creek`, `caramel-workshop`, `cracked-star-jar`
- Seeds: `62300`..`62304`
- Duration target: `300` seconds
- Tick rate: `30`

## Boundary

本报告只整理真实规则 Bot 长局表现，用于选择后续 `180-300s` late survival trajectory 导出对象。它不是 RL policy gate、不是 seeded stochastic watch evidence、不是手写 adapter 通过证据，也不能解除 `rl_policy_multimap_generalization_gap`。

四个原始矩阵报告仍全部保留各自的 `repair` gate 结论；这些 gate 只说明本次探针中的 Bot 胜率不用于内容平衡接受。当前结论不会推进 stage 03、不会写入 RL acceptance manifest，也不会替代 deterministic high-pressure 60 / 180 / 300 秒多图对比。

## Source Reports

| Report | Map | Bots |
|---|---|---|
| `harness/reports/2026-05-27_rl_rule_bot_late_survival_probe_soda_creek_001/summary.md` | `soda-creek` | `greedy`, `kite`, `boss-hunter`, `zone-control` |
| `harness/reports/2026-05-27_rl_rule_bot_late_survival_probe_caramel_workshop_001/summary.md` | `caramel-workshop` | `greedy`, `kite`, `boss-hunter`, `zone-control` |
| `harness/reports/2026-05-27_rl_rule_bot_late_survival_probe_cracked_star_jar_001/summary.md` | `cracked-star-jar` | `greedy`, `kite`, `boss-hunter`, `zone-control` |
| `harness/reports/2026-05-27_rl_rule_bot_late_survival_probe_caramel_workshop_extra_001/summary.md` | `caramel-workshop` | `tank`, `coward`, `route`, `random` |

## Teacher Candidate Findings

| Map | Candidate | Evidence | Use |
|---|---|---|---|
| `soda-creek` | `kite` seeds `62300`, `62301`, `62302`, `62304` | 4/5 victories, average survival `284.4s` | Clean late survival teacher |
| `soda-creek` | `kite` seed `62303`, `greedy` seed `62302` | Kite near-failure at `222.1s`; Greedy victory at `300s` | Late recovery contrast / diversity |
| `cracked-star-jar` | `kite` seeds `62302`, `62303` | 2/5 victories, average survival `256.0s` | Clean late survival teacher |
| `cracked-star-jar` | `greedy` seeds `62300`..`62304` | No victories, but deaths cluster at `222.1-254.6s` | Near-failure late pressure contrast |
| `caramel-workshop` | `tank` seed `62301` | Extra probe victory at `300s` | Only clean non-random teacher found for this map |
| `caramel-workshop` | `greedy`, `coward`, `route` selected defeats | Several deaths after `220s`; Coward seed `62301` reaches `241.2s` | Near-failure recovery contrast |
| `caramel-workshop` | `random` seeds `62302`, `62303` | 2/5 victories but random policy is not skill-shaped | Watch/diversity only; do not use as primary teacher |

## Recommended Export Set

Priority 1 clean teacher windows:

- `soda-creek`: `kite`, seeds `62300`..`62304`, export `180-300s`.
- `cracked-star-jar`: `kite`, seeds `62300`..`62304`, export `180-300s`.
- `caramel-workshop`: `tank`, seed `62301`, export `180-300s`.

Priority 2 contrast windows:

- `soda-creek`: `greedy` seed `62302`, plus `kite` seed `62303`.
- `cracked-star-jar`: `greedy` seeds `62300`..`62304`.
- `caramel-workshop`: `greedy` seeds `62300`..`62304`, `coward` seeds `62300`..`62303`, and `route` seeds with deaths near `223s`.

## Next Validation

1. Export JSONL trajectories with `export-bot-trajectories --sample-start-seconds 180 --sample-end-seconds 300`.
2. Run `python/train/train_behavior_clone.py --dry-run` on the exported directory and record sample counts, map distribution, health distribution and action distribution.
3. Train only after the dry-run proves the dataset contains real late-window states; report any adapter-derived or random-policy samples separately.
4. Re-run deterministic high-pressure 60 秒 10 seed, 180 秒 3 seed, and 300 秒 3 seed comparisons before any stage 03 or acceptance decision.
