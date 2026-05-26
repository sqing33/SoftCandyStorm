# RL 多地图升级选择 Ranker Smoke

## 结论

高压三图的升级选择监督样本已扩展到一个最小多地图集合，并训练出新的 supervised upgrade-choice ranker。该 checkpoint 可通过 `train_sb3.py --upgrade-choice-model` 接入 Gym upgrade action mode，并已在三张地图的 evaluation smoke 中实际记录升级决策。

本次结论为 `upgrade_choice_multimap_ranker_smoke_not_policy_gate`。它证明多地图样本、ranker 训练和 Gym action mode 组合可用，但不代表升级策略质量、RL policy acceptance 或长局修复通过。

## 数据导出

| Map | Seed Start | Seeds | Seconds | Movement Samples | Upgrade Samples | Victories |
|---|---:|---:|---:|---:|---:|---:|
| `soda-creek` | 59000 | 5 | 120 | 958 | 20 | 3 |
| `caramel-workshop` | 59100 | 5 | 120 | 1202 | 21 | 5 |
| `cracked-star-jar` | 59200 | 5 | 120 | 1204 | 23 | 5 |

合计：3364 条 movement sample、64 条 upgrade sample。movement sample 仍只用于移动监督；本报告只使用 `upgrade_sample` 训练升级选择 ranker。

## 训练摘要

- `choice_count`: 64
- `row_count`: 192
- `upgrade_vocabulary_size`: 27
- `input_len`: 172
- `epochs`: 20
- `batch_size`: 16
- `hidden_size`: 32
- `validation_choice_accuracy`: 0.6875
- `model`: `harness/reports/2026-05-27_rl_upgrade_choice_multimap_ranker_smoke_001/upgrade_choice_multimap_smoke.pt`

## Gym Evaluation Smoke

| Map | Report | Seconds | Level | Kills | Upgrade Decisions |
|---|---|---:|---:|---:|---:|
| `soda-creek` | `evaluation_soda_creek_seed57000.json` | 60.0328 | 3 | 66 | 2 |
| `caramel-workshop` | `evaluation_caramel_workshop.json` | 120.0318 | 2 | 128 | 1 |
| `cracked-star-jar` | `evaluation_cracked_star_jar.json` | 120.0318 | 4 | 168 | 3 |

另有 `evaluation_soda_creek.json` 使用 seed 59300 时 28.2666 秒提前失败，未触发升级 prompt；该记录保留为 movement policy 局限的提醒，不计为升级 action mode 失败。

## 限制

- movement action 仍由旧 behavior clone 输出，升级 ranker 只处理升级 prompt。
- 当前样本仍很小，且只来自 KiteBot。
- 仍存在未知升级 id fallback，例如 `*-level-2` 选项可能被打为 `-1000000.0`。
- 未执行 60/300 秒 high-pressure 多 seed policy acceptance；不得推进为 `rl_test_bot_candidate`。
