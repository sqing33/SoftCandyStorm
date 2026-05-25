# RL Policy Action Score 诊断 Smoke 001

日期：2026-05-26

## 目标

为 SB3 policy 评估报告增加 `action_score_diagnostic` 字段，用聚合方式记录策略对各动作的概率或分数，辅助诊断 deterministic argmax 为什么偏向某个动作。

## 覆盖范围

- PPO: 使用 `policy.get_distribution` 记录动作概率。
- DQN: 使用 `policy.q_net` 记录 q-value。
- Episode 与 Summary 都包含 `mean_scores`、`mean_top_actions`、`top_action_distribution`、`dominant_top_action` 和 `mean_chosen_action_score`。

## Smoke 结果

| Algorithm | Model | Score Kind | Samples | Mean Top Actions | Dominant Top Action |
| --- | --- | --- | ---: | --- | --- |
| PPO | `ppo_phase1_multimap_repeat_penalty_ent002_100000_eval60.zip` | `probability` | 151 | 7 = 0.3069, 4 = 0.2995, 6 = 0.0825 | 7 = 68.87% |
| DQN | `dqn_phase1_reward_shaping_5000_eval60.zip` | `q_value` | 151 | 3 = 0.3420, 8 = 0.3308, 4 = 0.3303 | 3 = 84.11% |

## 验证

- `python3 -m py_compile python/train/train_sb3.py`
- `python3 -m json.tool harness/reports/2026-05-26_rl_policy_action_score_diagnostic_smoke_001/ppo_action_score_diagnostic_smoke.json`
- `python3 -m json.tool harness/reports/2026-05-26_rl_policy_action_score_diagnostic_smoke_001/dqn_action_score_diagnostic_smoke.json`

## 结论

诊断字段可用于后续复查 `fail_20260526_011`：当 deterministic 评估持续偏动作 7 时，可以直接看到平均概率、最高概率动作分布，以及备选动作与主动作之间的差距。
