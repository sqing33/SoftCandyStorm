# RL 升级选择 Gym 动作模式 Smoke

## 结论

`train_sb3.py --evaluate-model` 已能加载 `train_upgrade_choice.py` 产出的升级选择 ranker，并在 Gym bridge 的 pending upgrade prompt 中通过 `upgrade_choice` 字段把选择传给 `game_harness gym-bridge`。

本次结论为 `gym_upgrade_action_mode_smoke_not_policy_gate`。它只证明升级选择 action mode plumbing 可用，不代表 RL policy、behavior clone 或升级 ranker 已通过长局压力测试。

## 命令

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py \
  --algorithm ppo \
  --evaluate-model \
  --behavior-clone-model python/train/models/behavior_clone_kite_high_pressure_smoke.pt \
  --upgrade-choice-model harness/reports/2026-05-27_rl_upgrade_choice_training_smoke_001/upgrade_choice_smoke.pt \
  --eval-episodes 1 \
  --eval-seconds 60 \
  --seed-start 57000 \
  --map-id soda-creek \
  --report harness/reports/2026-05-27_rl_upgrade_choice_gym_action_mode_smoke_001/evaluation.json
```

## 关键结果

- `policy_kind`: `behavior_clone`
- `upgrade_policy.mode`: `upgrade_choice_ranker`
- `map_id`: `soda-creek`
- `episodes`: 1
- `average_survival_seconds`: 60.0328
- `level`: 2
- `kills`: 67
- `upgrade_policy_decision_count`: 1
- 首次升级选择：`rainbow-candy-shot-level-2`

本次升级 prompt 的另外两个选项 `lollipop-boomerang` 与 `big-candy-jar` 对当前 ranker 仍是未知 id，因此被打为 `unknown_option_score = -1000000.0`。这说明 unknown option fallback 生效，但也说明当前 smoke 模型词表很小，不能据此判断真实升级策略质量。

## 范围限制

- movement action 仍由 behavior clone 输出；升级 ranker 只处理升级 prompt。
- 该 smoke 未进行 high-pressure 60/300 秒多地图对比。
- 该 smoke 未更新 RL policy acceptance manifest，也不得作为 `rl_test_bot_candidate` 证据。
