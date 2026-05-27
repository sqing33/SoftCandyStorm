# AI Bot 训练计划

## 目标

引入 DQN/PPO 等强化学习 Bot，用于游戏测试和平衡压力测试。

AI Bot 不作为正式游戏功能，不需要在渲染版游戏中实时运行。它运行在 headless GameCore 上，以高速度批量训练和评估。

## 为什么不直接控制窗口

窗口控制的问题：

- 慢
- 不稳定
- 难复现
- 观察信息不完整
- 无法大规模并行
- AI Agent 或脚本很难像真人一样实时移动

正确方式：

```text
GameCore snapshot -> AI policy -> action -> GameCore step -> reward/metrics
```

## 训练框架

默认选择：

- Python
- Gymnasium
- Stable-Baselines3
- DQN 作为离散动作实验
- PPO 作为更稳的主力候选

## 环境接口

Gymnasium 环境：

```python
class SoftCandyStormEnv(gym.Env):
    def reset(seed=None):
        return observation, info

    def step(action):
        return observation, reward, terminated, truncated, info
```

## 动作空间

### 第一版离散动作

9 个动作：

```text
0: 原地
1: 上
2: 右上
3: 右
4: 右下
5: 下
6: 左下
7: 左
8: 左上
```

升级选择：

第一阶段先由规则策略处理，不交给 RL。

原因：

- 降低动作空间复杂度。
- 先训练移动生存能力。
- 避免模型一开始被 Build 决策干扰。

第二阶段加入升级选择：

- action 包含移动 + 升级选择。
- 或在升级状态进入单独 action mode。

### 后续连续动作

如果使用 PPO，可以考虑连续二维移动：

```text
Box(low=-1, high=1, shape=(2,))
```

但为了稳定和可解释，先从 9 方向离散动作开始。

## 观察空间

不使用像素。使用低维结构化状态。

### 玩家状态

- 当前时间比例
- 当前生命比例
- 当前等级
- 当前经验比例
- 移动速度
- 拾取半径
- 伤害倍率
- 冷却倍率

### 敌人状态

取最近 N 个敌人，例如 N=24：

每个敌人：

- 相对 x
- 相对 y
- 相对速度 x
- 相对速度 y
- 距离
- 半径
- 生命比例
- 是否 Boss
- 行为类型 one-hot 或 id embedding

### 糖晶状态

取最近 M 个糖晶，例如 M=12：

- 相对 x
- 相对 y
- 价值
- 距离

### Build 状态

简化向量：

- 当前武器标签计数
- 当前被动标签计数
- 最高武器等级
- 是否已有防御武器
- 是否已有范围武器
- 是否已有 Boss 武器

### 地图状态

- 到上下左右边界距离
- 最近危险区方向
- 是否靠近角落

### 当前实现状态

Gym bridge 默认使用 observation v2：

- `observation_version = 2`
- `observation_len = 145`
- 保留 observation v1，长度 82，用于旧模型分析

v2 已覆盖：

- 玩家基础状态、拾取半径、伤害倍率、冷却倍率
- 最近敌人的相对位置、相对速度、距离、半径、生命、威胁、Boss/精英标记和行为嵌入
- 最近糖晶的位置、距离和价值
- build 数量、进化路径数量和最高武器等级
- 边界距离、角落接近度、最近危险区方向、Boss 汇总和地图尺寸

训练入口当前支持：

- `--train-maps`：传入逗号分隔地图列表。
- `--train-map-selection cycle|random`：控制多地图 reset 轮换方式。
- `--train-map-preset all-base-demo|high-pressure|stable-open`：使用常见 `base_demo` 地图集合。
- `--train-seconds`：覆盖训练 episode 时长，独立于 `--eval-seconds`。
- `--map-id`：在训练模式下指定训练后评估地图，避免 high-pressure 或 curriculum 实验仍默认用 `frosting-grassland` 做短局 gate。
- `--model-in`：从已有 SB3 模型 warm start 继续训练，用于课程学习、失败策略修复和后续规则 Bot 轨迹蒸馏实验。

其中 `high-pressure` 当前对应 `soda-creek`、`caramel-workshop`、`cracked-star-jar`，用于复查 observation v2 PPO 在 300 秒高压地图中的泛化失败。

Harness 还提供规则 Bot 轨迹导出入口：

```bash
cargo run -p game_harness -- export-bot-trajectories \
  --bot kite \
  --seed-start 30000 \
  --seeds 10 \
  --map-id soda-creek \
  --seconds 300 \
  --out harness/reports/local_bot_trajectories/kite_soda.jsonl
```

导出格式为 JSONL：第一行 `metadata`，中间为 `sample`，最后为 `summary`。每个 sample 包含 observation v2 和离散 movement action，可用于后续行为克隆、规则 Bot 轨迹蒸馏或 curriculum 诊断。默认导出仍只写 movement 状态；升级选择状态会从 movement sample 中跳过并计数，避免把 Build 决策混入移动生存训练。

如果需要为升级选择或阶段目标监督收集数据，可以显式加上 `--include-upgrade-samples true`。该模式会在遇到升级 prompt 时额外写入 `upgrade_sample` 记录，包含当前 observation、升级选项、规则 Bot 选择的 index 和 upgrade id；旧 movement loader 会继续跳过这些记录，Python 侧需用 `load_upgrade_choice_dataset` 单独读取。首个 `soda-creek` / KiteBot / 2 seed / 60 秒 smoke 导出了 241 条 movement sample 和 4 条 upgrade sample，只证明数据入口可用，不代表升级策略或 RL 长局修复已经完成。

若要专门覆盖 300 秒中后期状态，可在导出时使用时间窗口：

```bash
cargo run -p game_harness -- export-bot-trajectories \
  --bot kite \
  --seed-start 34000 \
  --seeds 5 \
  --map-id soda-creek \
  --seconds 300 \
  --sample-stride 10 \
  --sample-start-seconds 60 \
  --out harness/reports/local_bot_trajectories/kite_soda_late.jsonl
```

`sample-start-seconds` 和 `sample-end-seconds` 会写入 metadata 和导出报告；窗口外仍会正常推进 GameCore 与 Bot，只是不写 sample，从而保留真实中后期 Build、Boss、敌群和地图压力状态。

### 行为克隆入口

`python/train/train_behavior_clone.py` 可以从规则 Bot 轨迹 JSONL 训练一个小型 MLP movement clone，用于验证轨迹蒸馏链路：

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_export_smoke_001 \
  --epochs 2 \
  --batch-size 128 \
  --model-out python/train/models/behavior_clone_kite_high_pressure_smoke.pt \
  --report harness/reports/2026-05-26_rl_behavior_clone_kite_high_pressure_smoke_001/run_output.json
```

该入口只学习 Phase 1 movement action，不处理升级选择，也不替代 PPO/DQN 评估。任何 behavior clone 模型都必须先进入 Gym 评估、动作分布诊断和规则 Bot 对比，才能作为 RL 测试 Bot 候选。

`--dataset` 可以重复传入，用于组合不同时间窗口的数据集。例如可以把 0-60 秒 expanded 数据和 60-300 秒 lategame 数据放在同一次训练中，避免只学中后期而丢失开局状态。

训练后的 behavior clone checkpoint 可以通过 `train_sb3.py --behavior-clone-model` 接入现有 Gym 评估和规则 Bot 对比：

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_sb3.py \
  --compare-rule-bots \
  --behavior-clone-model python/train/models/behavior_clone_kite_high_pressure_smoke.pt \
  --eval-episodes 2 \
  --eval-seconds 10 \
  --map-id soda-creek \
  --rule-bots random,kite,tank \
  --report harness/reports/2026-05-26_rl_behavior_clone_kite_eval_smoke_001/comparison.json
```

该 adapter 会输出 action probability 诊断，因此 behavior clone 的 deterministic 动作塌缩可以和 SB3 policy 使用同一套 `action_entropy_bits`、`normalized_action_entropy` 和 `action_score_diagnostic` 字段审查。

当轨迹数据动作分布明显偏斜时，可以用 `--class-weighting inverse_frequency` 做最小修复尝试：

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_export_smoke_001 \
  --epochs 20 \
  --batch-size 128 \
  --class-weighting inverse_frequency \
  --model-out python/train/models/behavior_clone_kite_high_pressure_weighted_smoke.pt \
  --report harness/reports/2026-05-26_rl_behavior_clone_kite_weighted_smoke_001/run_output.json
```

首轮 weighted smoke 表明：离线 validation accuracy 可以提升，但 deterministic Gym policy 仍可能塌缩到单一动作。因此 class weighting 只能作为诊断旋钮，不能当作轨迹蒸馏已修复的证据。

当长局失败集中在低血量或中后期危险状态时，可以用 `--sample-weighting danger` 做多图危险状态重采样。该模式会基于 sample 的 `health_ratio` 与 `time_seconds` 提高采样概率，而不是只给某一张地图追加样本：

```bash
uv run --with-requirements python/train/requirements.txt python python/train/train_behavior_clone.py \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_expanded_001 \
  --dataset harness/reports/2026-05-26_rl_rule_bot_trajectory_lategame_001 \
  --sample-weighting danger \
  --epochs 20
```

危险状态重采样仍然只是训练策略，必须通过 60/300 秒 high-pressure 对比证明没有移动失败面。

当 `sequence_diagnostics` 暴露 `high_action_persistence` 时，可以使用 `--sample-weighting action_change` 或 `--sample-weighting danger_action_change` 对同一 episode 内动作发生变化的样本加权。该旋钮用于诊断和缓解长段持续方向带来的确定性偏置；它不能替代动作分布门禁，也不能因为离线 entropy 更高就推进为 RL 测试 Bot。

当 opening / mid / late 样本比例明显失衡时，可以使用 `--sample-weighting time_phase_balance`，或组合模式 `time_phase_balance_danger`、`time_phase_balance_action_change`、`time_phase_balance_danger_action_change`。该模式只在训练采样层面按阶段反比加权，帮助 movement policy 做 curriculum 修复；它不改变 Gym observation，也不能替代 60/300 秒 high-pressure 对比。

首个 `time_phase_balance_danger_action_change` curriculum smoke 使用 phase-aligned high-pressure 轨迹跑通 1 epoch GRU context8 训练，并完成 5 秒 `soda-creek` Gym 加载评估。报告位于 `harness/reports/2026-05-27_rl_behavior_clone_time_phase_balance_curriculum_smoke_001/summary.md`；gate 仍为 `behavior_clone_smoke_only_not_policy_gate`，只证明采样倍率和在线加载路径，不代表长局 movement policy 修复。

完整 `time_phase_balance_danger_action_change` GRU context8 候选已完成 20 epoch 训练和 high-pressure 三图 60/300 秒对比。60 秒三图 gate 通过，300 秒三图动作分布也不再塌缩，但 `soda-creek` 胜率仍为 0%，整体 gate 为 `multimap_comparison_recorded_needs_policy_repair`。报告位于 `harness/reports/2026-05-27_rl_behavior_clone_time_phase_balance_curriculum_full_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_015_time_phase_balance_soda_longrun_gap.json`。结论：阶段平衡采样改善动作分布，但仍不能替代长局目标、升级协同或 PPO 闭环。

把该阶段平衡 GRU teacher 蒸馏为 SB3 PPO zip 的入口也已验证：teacher argmax agreement 为 0.8898，validation policy entropy 为 1.295753，但 10 秒 `soda-creek` deterministic Gym 加载评估仍 action `3` 100% 塌缩。报告位于 `harness/reports/2026-05-27_rl_sb3_distill_time_phase_balance_teacher_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_016_time_phase_balance_distillation_action_collapse.json`。结论：supervised distillation zip 只是初始化产物，必须进入 PPO 闭环或进一步提高 target entropy，不能单独当作修复。

从该 distilled zip 出发的 10k timestep PPO 闭环训练已完成：训练使用 high-pressure 三图随机采样、300 秒 episode、`ent_coef=0.02`。60 秒 high-pressure 三图 gate 通过，但 300 秒 `soda-creek` 与 `caramel-workshop` 胜率均为 0%，整体 gate 仍为 `multimap_comparison_recorded_needs_policy_repair`。报告位于 `harness/reports/2026-05-27_rl_ppo_time_phase_balance_closed_loop_10k_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_017_time_phase_balance_ppo_closed_loop_gap.json`。结论：短 PPO 闭环能缓解 deterministic 塌缩，但仍不能替代长局课程、奖励目标或 movement + upgrade 联合训练。

`tools/analyze_rl_policy_failures.py` 已提供 RL 对比失败分析入口，可从 `train_sb3.py --compare-rule-bots` 的 multimap JSON 中提取每图失败 seed、死亡时间桶、终局原因、dominant action 和 reward 摘要。首个分析报告位于 `harness/reports/2026-05-27_rl_failure_analysis_time_phase_balance_ppo_300s_001/summary.md`：`soda-creek` 失败以 opening 早死为主，`caramel-workshop` 失败以 late 180-300 秒为主，说明下一步课程应区分早期避险和中后期恢复，而不是继续用单一平均胜率调参。

`tools/create_rl_curriculum_plan.py` 可把上述失败分析转成 staged PPO curriculum manifest。首份计划位于 `harness/reports/2026-05-27_rl_curriculum_time_bucket_plan_001/summary.md`，从阶段平衡 PPO 10k 闭环模型出发生成 3 个串联阶段：opening 60 秒修 `soda-creek` / `cracked-star-jar` 早死，mid 180 秒修 `caramel-workshop`，late 300 秒修三张高压图。该报告只生成待执行训练与对比命令，不代表 PPO 已完成修复，也不能作为 RL policy gate。

stage 01 opening 课程已按计划跑完 5120 actual timesteps，并完成 60 秒 high-pressure 三图对比。`caramel-workshop` 与 `cracked-star-jar` 均为 100% 胜率，但 `soda-creek` 只有 66.67%，seed `62101` 在 29.1666 秒因 `player_health_depleted` 死亡；报告位于 `harness/reports/2026-05-27_rl_curriculum_time_bucket_stage01_opening_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_018_curriculum_stage01_soda_opening_gap.json`。结论：stage 01 缓解了旧动作塌缩，但 opening 修复仍不完整，不能直接当作后续课程已通过的前置证据。

从 stage 01 继续 20k timesteps 的 opening retry 也已完成，并用 10 seed 60 秒 high-pressure 复查。`soda-creek` 提升到 80% 胜率，但仍有 seed `62406` / `62409` 在 opening 阶段死亡，失败局 dominant action 转向 `4`；报告位于 `harness/reports/2026-05-27_rl_curriculum_time_bucket_stage01_retry_20k_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_019_curriculum_stage01_retry_soda_opening_gap.json`。结论：单纯延长 generic opening PPO 不足以解除 `soda-creek` 开局 blocker，stage 02 不应被解释为建立在已修复 opening 之上。

`train_sb3.py` 现在支持 `--trace-dir`、`--trace-failed-only` 和 `--trace-sample-stride`，可在训练后评估、单模型评估或规则 Bot 对比中为 policy episode 输出采样轨迹。轨迹记录 step、tick、time、action、reward、health、level、kills、xp、damage、events、terminal、reward_breakdown 和 action score top actions；它来自 Gym evaluation info，不是完整 Replay，也不包含完整 GameCore snapshot。

首个 retry trace 报告位于 `harness/reports/2026-05-27_rl_curriculum_stage01_retry_trace_001/summary.md`。该报告对 `soda-creek` seed `62406` 到 `62409` 复跑 60 秒 evaluation，并只写失败局 trace：seed `62406` / `62409` 均在死亡前持续选择 action `4`，最终 chosen action score 约 `0.87` / `0.85`，说明 failure 不是随机抖动，而是策略在部分开局稳定沿坏路径前进。下一步应比较失败与成功 seed 的地图压力，并考虑给 trace 增加玩家位置、边界距离和最近敌人压力等 GameCore snapshot 字段。

Gym bridge 的 trace diagnostics 已补充玩家位置 / 速度、地图尺寸、边界距离、最近敌人、附近敌人计数和 low-health / boundary / enemy / hazard / boss / safety 风险分数。带 diagnostics 的复跑报告位于 `harness/reports/2026-05-27_rl_curriculum_stage01_retry_snapshot_trace_001/summary.md`：两个失败 seed 都走到 `soda-creek` 右下角，终点 `boundary.min_distance = 0`、`boundary.edge_risk = 1`、`enemy_pressure_risk = 1`、`nearest_enemy.hitbox_distance = 0`，同时仍高置信选择 action `4`。结论更具体：stage 01 retry 的 opening blocker 是 bottom-right 贴边被围，而不是单纯动作熵不足。

同一 seed 段的成功/失败 snapshot trace 对比位于 `harness/reports/2026-05-27_rl_curriculum_stage01_retry_snapshot_compare_001/summary.md`。四个 episode 都会早期接触边界，因此“贴边”本身不是唯一失败条件；失败 seed 的差异是到达右下角后持续 action `4`，而成功 seed 最终转为 action `7` 并在 60 秒截止前把 `enemy_pressure_risk` 拉回 `0`。下一轮修复应针对“右下角 `boundary.min_distance = 0` 且敌压上升时继续 action `4`”的状态-动作组合，而不是泛泛继续加 PPO timesteps。

Gym reward breakdown 已新增 `corner_action_risk`，用于审计 `soda-creek` 开局右下角敌压状态下继续 action `4` 的坏路径。保持旧 stage 01 retry policy 不变，对 seed `62406` 到 `62409` 复跑 60 秒 evaluation 后，平均 `corner_action_risk = -0.6767`；失败 seed `62406` / `62409` 最终帧仍为 action `4` 且 `corner_action_risk = -0.006`，成功 seed 最终转为 action `7` 且最终帧无该惩罚。报告位于 `harness/reports/2026-05-27_rl_curriculum_stage01_retry_corner_reward_001/summary.md`。该结果只证明 reward instrumentation 能捕获已知坏路径，不能证明旧模型已修复；下一步必须基于该 reward warm start 重训，并重新跑 60 秒 high-pressure 10 seed 对比。

首个 `corner_action_risk` 20k warm-start 重训没有修复 stage 01，反而形成新的 action `8` 塌缩。训练评估中 `soda-creek` 5 局胜率为 0%、action `8` 占比 92.90%；同 seed 60 秒 high-pressure 10 seed 对比中 `soda-creek` / `caramel-workshop` / `cracked-star-jar` 胜率为 10% / 80% / 70%，三图均以 action `8` 为 dominant action。报告位于 `harness/reports/2026-05-27_rl_curriculum_stage01_corner_reward_retrain_20k_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_020_corner_reward_retrain_action8_collapse.json`。结论：该 checkpoint 只能作为 repair regression 证据，不能进入 stage 02；下一步应降低或重构 action-specific shaping，并先做 cheap deterministic smoke。

方向化 `corner_action_risk` smoke 把惩罚改为“任意对角动作继续推入当前受压角落”并将权重降到 `-0.003`。2048 timestep warm-start smoke 避免了 action `8` 塌缩，但仍没有通过 stage 01：同 seed 60 秒 high-pressure 10 seed 中 `soda-creek` / `caramel-workshop` / `cracked-star-jar` 胜率为 70% / 90% / 100%，`soda-creek` 仍有 3 个 opening death，低于 retry 20k 的 80%。报告位于 `harness/reports/2026-05-27_rl_curriculum_stage01_corner_reward_directional_smoke_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_021_directional_corner_reward_smoke_soda_gap.json`。结论：方向化 shaping 是避免 action `8` 回归的正向信号，但仍只是 smoke-only repair evidence。

状态化 `corner_risk_delta` smoke 已把开局角落修复从 action-specific 惩罚改为“角落敌压风险是否下降”的 delta reward。2048 timestep warm-start 后，60 秒 high-pressure 10 seed deterministic 与 stochastic 对比均在 `soda-creek` / `caramel-workshop` / `cracked-star-jar` 达到 100% 胜率，`soda-creek` 不再出现 opening death；动作熵也没有塌缩，deterministic entropy 为 0.4951 / 0.5161 / 0.5715，stochastic entropy 为 0.8257 / 0.8462 / 0.8340。报告位于 `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/summary.md`。结论：stage 01 opening 短窗 blocker 可作为已修复证据进入 stage 02 mid-window 实验；这仍不是 180 秒、300 秒长局稳定性或 RL policy acceptance 通过。

基于 `corner_risk_delta` checkpoint 的首个 stage 02 mid-window 实验没有通过。该实验只在 `caramel-workshop` 训练 180 秒 / 5120 actual timesteps，目标图训练评估为 100% 胜率；但 180 秒 high-pressure 三图 3 seed 对比中 `soda-creek` 胜率掉到 33.33%，seed `62202` 在 52.7995 秒 opening 死亡，seed `62201` 在 177.0755 秒 mid-window 死亡；`caramel-workshop` 虽然 100% 胜率，但 action `2` 占比 77.81%，触发 action-bias repair。报告位于 `harness/reports/2026-05-27_rl_curriculum_stage02_corner_risk_delta_mid_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_022_stage02_corner_risk_delta_mid_regression.json`。结论：不能进入 stage 03；stage 02 需要加入 opening retention / mixed seed 约束，避免修中局时破坏 stage 01。

stage 02 mixed retention 尝试把训练地图改为 `soda-creek` + `caramel-workshop`，缓解了目标图 action `2` 塌缩：`caramel-workshop` 训练评估 180 秒 3 局全胜，dominant action `7` 为 57.93%。但 60 秒 opening 回归中 `soda-creek` 只剩 80% 胜率，seed `62405` / `62407` 分别在 47.3663 秒 / 55.7328 秒死亡；180 秒三图 3 seed 中 `soda-creek` 也只有 66.67%。报告位于 `harness/reports/2026-05-27_rl_curriculum_stage02_mixed_retention_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_023_stage02_mixed_retention_opening_regression.json`。结论：mixed retention 方向改善动作分布，但仍破坏 stage 01 opening gate；下一步需要更短 continuation、较低学习率或显式 opening replay / regularization。

stage 02 low-lr short continuation 已验证“更短 continuation + 较低学习率”不足以保护 opening gate：从 stage 01 `corner_risk_delta` checkpoint warm-start，只训练 `1024` timesteps，并用 `--learning-rate 0.0001 --ent-coef 0.02` 在 `soda-creek` + `caramel-workshop` 上继续训练。60 秒 high-pressure 10 seed opening 回归中 `soda-creek` 仍为 80% 胜率，seed `62400` 在 24.5666 秒死亡、seed `62407` 在 50.0996 秒死亡；`caramel-workshop` / `cracked-star-jar` 仍为 100%。报告位于 `harness/reports/2026-05-27_rl_curriculum_stage02_low_lr_short_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_024_stage02_low_lr_short_opening_regression.json`。结论：60 秒 hard gate 失败，未运行 180 秒三图对比，不能进入 stage 03；下一步应做 explicit opening replay / regularization，而不是继续只调学习率或 timesteps。

stage 02 seed-replay short continuation 把 `62400-62409` opening gate seeds 显式用于训练 reset，仍从 stage 01 `corner_risk_delta` checkpoint warm-start，配置为 `1024` timesteps、`--learning-rate 0.0001 --ent-coef 0.02`、`soda-creek` + `caramel-workshop` random map selection。60 秒 high-pressure 10 seed opening 回归中 `soda-creek` 提升到 90% 胜率，但 seed `62405` 仍在 47.3330 秒死亡；`caramel-workshop` / `cracked-star-jar` 均为 100%。报告位于 `harness/reports/2026-05-27_rl_curriculum_stage02_seed_replay_short_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_025_stage02_seed_replay_short_opening_regression.json`。结论：seed replay 是有效方向但仍未通过 60 秒 hard gate，不能进入 stage 03；下一步应聚焦 seed `62405` failed-only trace 或更强 opening regularization。

seed `62405` trace compare 已对比 stage 01 `corner_risk_delta` 成功轨迹和 stage 02 `seed_replay_short` 失败轨迹。stage 01 在右下角压力升高后于 29.6666 秒从 action `4` 切到 action `7` 沿底边向左撤离，并以 60.0328 秒胜利结束；stage 02 则先用 action `2` 顶到右上角，再从 20.6667 秒开始持续 action `4` 沿右边界下行，直到 47.3330 秒在右下角死亡，采样轨迹中没有 action `7`。报告位于 `harness/reports/2026-05-27_rl_curriculum_stage02_seed62405_trace_compare_001/summary.md`。结论：下一轮不能只增加 seed replay，应针对“右边界 / 右下角敌压升高时切换离角落动作”做 targeted opening regularization。

首个完整 `danger_action_change` staged GRU context8 候选改善了短窗动作分布：60 秒 high-pressure 中 `soda-creek` 从 0% 提升到 40%，normalized entropy 从 0.2356 提升到 0.6104，dominant action ratio 从 0.7911 降到 0.5226。但 300 秒三图仍全部为 0% 胜率，说明动作变化点加权只能修复短窗偏置，不能替代升级选择、阶段目标、路线规划或 PPO 闭环优化。

`python/train/distill_behavior_clone_to_sb3.py` 已提供 PPO 蒸馏初始化入口：它从规则 Bot 轨迹读取 observation，用 behavior clone teacher 输出 soft action probability，再监督训练 SB3 PPO `MlpPolicy` 并保存标准 `.zip` 与 metadata。蒸馏入口现在支持 `--teacher-temperature` 与 `--uniform-target-mix`，用于在 teacher probability 过尖或动作偏置过重时显式提高 target entropy；这些旋钮只属于 repair 实验，不是 policy gate。首个 256 样本 smoke 已证明 distilled `.zip` 可以被 `train_sb3.py --evaluate-model` 加载，但 1 epoch 模型仍为动作 3 deterministic smoke，不是策略通过证据；后续应在更大数据上蒸馏后继续 PPO 环境训练，并跑 high-pressure 60/300 秒对比。

首个全量蒸馏 + PPO warm-start 候选使用 21726 条 phase-aligned 样本和 action-change staged GRU teacher，5 epoch 蒸馏后 validation argmax accuracy 为 0.6916；随后在 high-pressure 三图上 warm-start PPO 2048 timesteps。结果仍为 `repair`：60 秒三图均触发 action distribution repair，300 秒三图全部 0% 胜率且 action 3 dominant ratio 为 0.7728 / 0.7631 / 0.8494。结论：蒸馏入口可用，但短 PPO 训练会继承 / 放大当前 teacher 的动作偏置；下一步应改 teacher targets、增加 entropy / curriculum，或纳入升级与阶段目标监督。

target-entropy 蒸馏候选使用 `--teacher-temperature 1.5 --uniform-target-mix 0.05`，把全量 target entropy 提高到 1.186717，并在 60 秒 high-pressure 三图达到 80% / 80% / 80% 胜率且不再触发 compare 内部 action-bias repair。但 300 秒三图仍全部 0% 胜率，长局中 action 6 dominant ratio 在 caramel / cracked 达到 0.8237 / 0.8119。结论：target entropy 是短窗修复方向，但不能替代升级 / 阶段目标监督或 warm-start 后的 PPO entropy / curriculum。

`train_sb3.py` 的 warm-start 路径现在允许 `--model-in ... --ent-coef <value>` 覆盖 PPO entropy coefficient，也允许 `--model-in ... --learning-rate <value>` 覆盖学习率；加载模型后会刷新 SB3 learning-rate schedule，并在训练报告中把 `algorithm_parameters_source` 标记为 `warm_start_metadata_with_overrides`。该能力用于可审计地测试 PPO 探索和小步修复；默认不改变旧模型行为，也不能绕过 high-pressure 对比和 RL acceptance。

`train_sb3.py` 现在还支持训练期 seed replay：`--train-seeds <a,b,c>` 或 `--train-seed-start <N> --train-seed-count <M>` 会把指定 seed 集合传给 Gym 环境，让 PPO/DQN 训练 reset 显式覆盖已知 opening / mid-window 回归 seed；`--seed-start` 仍只用于评估和规则 Bot 对比。该能力用于 stage 02 opening retention / regularization 实验，不能替代 60 秒 opening gate、180 秒三图对比或 failure case 审查。

首个 `ent_coef = 0.02` 的 target-entropy warm-start 候选改善了 60 秒动作分布：high-pressure 三图 normalized entropy 为 0.5801 / 0.5823 / 0.5307，dominant action ratio 均低于 0.45；但短窗胜率仍只有 80% / 60% / 80%，300 秒三图仍全部 0%。结论：entropy coefficient 是短窗动作多样性修复方向，但不能解决 movement-only policy 的长局目标缺失。

升级选择监督入口已经补上最小数据链路：`export-bot-trajectories --include-upgrade-samples true` 会在不破坏 movement dataset 的前提下输出 `upgrade_sample`，`train_behavior_clone.py` 的 movement loader 默认跳过并统计这些记录，`load_upgrade_choice_dataset` / `summarize_upgrade_choice_dataset` 可单独读取升级选择样本。当前 smoke 报告位于 `harness/reports/2026-05-27_rl_upgrade_choice_export_smoke_001/summary.md`；后续应扩大多地图升级样本覆盖、改进升级词表和阶段目标监督，而不是继续只调 movement entropy。

`python/train/train_upgrade_choice.py` 已提供首个监督升级选择 ranker smoke：它把每次升级 prompt 展开为一行一个候选升级，输入为 observation + upgrade id one-hot，目标为规则 Bot 选择的 upgrade。首个 4 choice / 12 row smoke 能写出 checkpoint 和报告，gate 为 `upgrade_choice_training_smoke_not_policy_gate`；它只证明模型管线，不代表升级策略质量。

Gym bridge 现在支持在 `step` 请求中传入 `upgrade_choice`。`SoftCandyStormEnv` 可接收 `upgrade_policy`，在 pending upgrade prompt 时用上一帧 observation 和 `upgrade_options` 调用 ranker，并把选择写进 bridge payload。`train_sb3.py --upgrade-choice-model` 会加载 ranker 并在 evaluation / comparison 报告中记录 `upgrade_policy`、`upgrade_policy_decisions` 和 `upgrade_policy_decision_count`。首个 60 秒 `soda-creek` smoke 实际穿过 1 次升级 prompt，报告位于 `harness/reports/2026-05-27_rl_upgrade_choice_gym_action_mode_smoke_001/summary.md`；gate 为 `gym_upgrade_action_mode_smoke_not_policy_gate`，仍不能作为 RL policy acceptance 或长局修复证据。

多地图升级选择 ranker smoke 已使用 high-pressure 三图各 5 seed / 120 秒导出 64 条 upgrade sample，训练出 27 个升级词表项的 checkpoint，并在 `soda-creek`、`caramel-workshop`、`cracked-star-jar` 的 Gym evaluation smoke 中实际记录升级决策。报告位于 `harness/reports/2026-05-27_rl_upgrade_choice_multimap_ranker_smoke_001/summary.md`；gate 为 `upgrade_choice_multimap_ranker_smoke_not_policy_gate`。该结果仍只证明多地图数据、训练和 action mode 组合链路，不代表升级策略质量或长局修复。

把多地图升级 ranker 与旧 movement behavior clone 组合后，high-pressure 三图 60 秒 / 300 秒对比仍为 repair：ranker 在多局中被调用，但 movement policy deterministic action `3` 占比为 100%，300 秒三图胜率全部为 0%。报告位于 `harness/reports/2026-05-27_rl_upgrade_choice_joint_high_pressure_compare_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_014_upgrade_ranker_joint_action_bias.json`。结论：升级 action mode 不是当前主瓶颈，下一步必须修 movement policy、阶段目标或联合 curriculum。

更有效的第一步是扩大轨迹覆盖。当前 expanded smoke 使用 high-pressure 三图、5 seed、60 秒、`sample_stride = 5`，共 5312 条 movement sample。训练出的 unweighted behavior clone 在 10 秒 high-pressure 三图对比中通过短窗动作门禁：

- `soda-creek`：normalized action entropy 0.6126，最大动作占比 32.0%。
- `caramel-workshop`：normalized action entropy 0.4859，最大动作占比 44.5%。
- `cracked-star-jar`：normalized action entropy 0.3370，最大动作占比 69.5%。

结论：数据覆盖比单纯 loss 权重更能缓解 deterministic 塌缩，但这仍只是 10 秒 smoke，不代表 60/300 秒高压泛化通过。

后续验证结果：

- 60 秒 high-pressure 三图、5 seed：平均胜率 66.67%，三图动作熵约 0.61 / 0.62 / 0.61，短中局可作为继续实验信号。
- 300 秒 high-pressure 三图、3 seed：三图胜率均为 0%，`cracked-star-jar` 最大动作占比 75.19%，结论为 repair。

因此 expanded behavior clone 仍不能作为 RL 测试 Bot，只能作为后续长局数据扩展、序列模型或 PPO 蒸馏初始化候选。

使用 `--sample-start-seconds 60` 生成 300 秒中后期轨迹，并与原 0-60 秒 expanded 数据组合训练后，长局表现明显改善：

- 60 秒 high-pressure 三图、5 seed：三图胜率均为 100%，动作熵约 0.87，最大动作占比不超过 30.45%。
- 300 秒 high-pressure 三图、3 seed：平均胜率 22.22%，平均存活 231.3046 秒；`soda-creek` 和 `caramel-workshop` 胜率为 33.33%，但 `cracked-star-jar` 仍为 0%，gate 仍为 repair。

结论：中后期轨迹覆盖可以显著改善长局存活与动作分布，但最终图仍需要定向数据、危险状态重采样或序列上下文，不能把该模型推进为 RL 测试 Bot。

针对 `cracked-star-jar` 增加 120-300 秒最终图定向轨迹后，最终图 300 秒胜率从 0% 提升到 66.67%，但 `soda-creek` 回归到 0%，说明单图补强会移动失败面。后续应做多图危险状态重采样或序列上下文，而不是继续单图堆样本。

使用 `--sample-weighting danger` 在 expanded、lategame 和最终图定向轨迹的组合数据上做多图危险状态重采样后，短局表现继续保持健康：

- 60 秒 high-pressure 三图、5 seed：三图胜率均为 100%，normalized action entropy 约 0.87 / 0.91 / 0.92。
- 300 秒 high-pressure 三图、3 seed：平均胜率 55.56%，`soda-creek` 和 `caramel-workshop` 均为 66.67%，`cracked-star-jar` 为 33.33%；三图动作熵均约 0.90 以上。

结论：危险状态重采样比单图补强更稳，能避免 `soda-creek` 回归到 0%，但最终图仍明显低于 KiteBot 规则基线 100% 胜率。因此该模型只能记为 watch，不能推进为 RL 测试 Bot。下一步应转向序列上下文、分阶段 policy 或结合 PPO 蒸馏初始化，而不是继续堆单帧 MLP 样本。

训练入口已支持 `--context-frames <N>`，用于把同一 episode 内最近 N 帧 observation 拼接成 behavior clone 输入。默认 `N=1`，兼容旧模型；当 `N>1` 时，训练报告会记录 `context_frames`、`base_observation_len` 和 `input_observation_len`。在线 Gym 评估会在每个 episode reset 时清空 clone 的上下文缓存，避免跨 seed 泄漏状态。

序列上下文的第一步应先用小规模 smoke 证明链路可用，再训练 3-5 帧模型并复查 60/300 秒 high-pressure 对比。如果仍低于规则 Bot，后续再考虑 GRU/Transformer 或分阶段 policy。

3 帧 danger-weighted behavior clone 已完成训练，输入长度为 435，validation accuracy 为 86.87%。用户恢复 Developer Mode / Developer Tool 权限并重启后，`tools/diagnose_local_binary_launch.py` 在当前 Codex 会话返回 `local_binary_launch_ok`，`target/debug/game_harness --help` 可正常启动，`cargo test --workspace` 全绿，RL 依赖也可通过 `uv run --with-requirements python/train/requirements.txt` 加载。`spctl -a -vv target/debug/game_harness` 仍会对 ad-hoc binary 返回 `rejected`，但当前执行链路和 Gym 评估已不再卡在本机启动策略上。

恢复后已补跑 context3 behavior clone 的 high-pressure 三图对比：

- 60 秒 high-pressure 三图、5 seed、`seed-start 42000`：三图胜率均为 100%，normalized action entropy 为 0.8740 / 0.9206 / 0.9074，最大动作占比不超过 29.19%，短窗动作分布健康。
- 300 秒 high-pressure 三图、3 seed、`seed-start 43000`：`soda-creek` 胜率 66.67%，`caramel-workshop` 胜率 0%，`cracked-star-jar` 胜率 33.33%；`caramel-workshop` 触发 `zero_policy_win_rate` repair。额外 `seed-start 45000` 窗口为 `watch`，显示 `soda-creek` 与 `cracked-star-jar` 仍可能低于规则 Bot 基线。

结论：3 帧上下文修复了短窗动作塌缩，但没有解决 300 秒长局泛化，尤其是 `caramel-workshop` 中后期压力。该模型只能保持 `repair`，不能推进为 `rl_test_bot_candidate`。对应 failure case 为 `harness/failed_cases/fail_20260526_027_behavior_clone_context3_caramel_gap.json`。

继续把同一批 high-pressure 轨迹训练为 5 帧 danger-weighted MLP 后，离线 validation accuracy 为 86.74%，短窗仍健康：

- 60 秒 high-pressure 三图、5 seed：三图胜率均为 100%，normalized action entropy 为 0.9116 / 0.9119 / 0.9063，最大动作占比不超过 21.40%。
- 300 秒 high-pressure 三图、3 seed、同 context3 seed 窗口：`soda-creek` 胜率 66.67%，`caramel-workshop` 胜率 0%，`cracked-star-jar` 胜率 33.33%；`caramel-workshop` 仍触发 `zero_policy_win_rate` repair。
- 额外 seed 窗口中 `cracked-star-jar` 可到 100%，但 `caramel-workshop` 仍为 0%，说明失败面集中在 caramel-workshop 中后期恢复路径，而不是 observation 短窗动作熵。

结论：简单把 MLP context 从 3 帧堆到 5 帧不是修复方向。下一步应停止堆同构短序列输入，改为收集 `caramel-workshop` 180-300 秒恢复轨迹，或尝试 GRU / Transformer、分阶段 policy、PPO 蒸馏初始化。对应 failure case 为 `harness/failed_cases/fail_20260527_001_behavior_clone_context5_caramel_gap.json`。

按上述方向导出 `caramel-workshop` 180-300 秒 KiteBot 恢复轨迹后，新增 2041 条 movement sample，使训练集中的 `caramel-workshop` 占比从约 31.5% 前的低位提高到 31.53%。用该数据训练 5 帧 danger-weighted MLP 后：

- 60 秒 high-pressure 三图、5 seed：三图胜率均为 100%，短窗动作分布仍健康。
- 300 秒 high-pressure 三图、3 seed、同 seed 窗口：`caramel-workshop` 从 0% 提升到 66.67%，但 `soda-creek` 降到 33.33%，`cracked-star-jar` 回归到 0%。

结论：目标图恢复轨迹能修补 `caramel-workshop`，但同构 MLP 会把失败面移动到其他高压图。该模型仍是 `repair`，不能推进为 RL 测试 Bot；后续必须引入地图条件化、分阶段 policy 或真正的序列模型，而不是继续追加单图恢复样本。对应 failure case 为 `harness/failed_cases/fail_20260527_002_behavior_clone_caramel_recovery_regression.json`。

地图 one-hot 条件化已经接入 behavior clone 训练和 Gym 评估：训练入口支持 `--map-conditioning one_hot`，checkpoint 记录 map vocabulary，在线评估会在每个 episode reset 后把当前 `map_id` 注入 policy；旧 checkpoint 默认 `map_conditioning=none` 并已通过兼容 smoke。使用同一批 expanded、lategame、cracked lategame 和 caramel recovery 轨迹训练 5 帧 danger-weighted map-conditioned MLP 后，离线 validation accuracy 为 85.51%，输入长度从 725 扩展到 728。

- 60 秒 high-pressure 三图、5 seed：三图胜率均为 100%，normalized action entropy 为 0.8893 / 0.8893 / 0.8824，最大动作占比不超过 24.34%。
- 300 秒 high-pressure 三图、3 seed、同 seed 窗口：不再出现 0% 胜率，`soda-creek` 为 66.67%，`caramel-workshop` 为 33.33%，`cracked-star-jar` 为 33.33%；但 `caramel-workshop` 与 `cracked-star-jar` 仍低于最强规则 Bot 基线，multi-map gate 为 `watch`。

结论：地图条件化是正向修复方向，能消除 caramel-recovery 模型的 0% 跨图回归，但同构 MLP 仍没有达到 `rl_test_bot_candidate` 门槛。下一步应转向分阶段 policy、GRU / Transformer 或 PPO 蒸馏初始化，并继续使用三图 300 秒同 seed high-pressure 对比防止回归。对应 failure case 为 `harness/failed_cases/fail_20260527_003_behavior_clone_map_conditioned_watch.json`。

训练入口现已支持 `--architecture gru`，用于把 `--context-frames` 保持为时间序列输入，而不是像旧 MLP 一样把多帧 observation 直接拼平成一个长向量。GRU checkpoint 会记录 `architecture`、`sequence_input_len`、`context_frames` 和 map-conditioning vocabulary，`train_sb3.py --behavior-clone-model` 可以直接加载并通过同一套 Gym evaluation / rule Bot comparison 评估。该能力只是修复方向的技术入口；任何 GRU 候选仍必须通过 60/300 秒 high-pressure 三图对比、RL policy acceptance manifest 和 failure case 审查，不能因为模型结构更复杂就直接推进。

首个 `gru context8 + map-conditioning one_hot + danger sampling` 候选使用 expanded、lategame、cracked lategame 和 caramel recovery 轨迹训练，离线 validation accuracy 为 87.90%，但 Gym 对比显示该方向需要重新诊断：60 秒 high-pressure 三图只有 80% 胜率，300 秒三图同 seed 对比全部为 0% 胜率，multi-map gate 为 `repair`。这说明 GRU 支持链路可用，但当前训练目标 / 超参没有解决长局泛化，反而比 map-conditioned MLP watch 结果更差。后续应先做序列模型诊断、动作分布约束、分阶段 policy 或 PPO 蒸馏初始化，而不是直接扩大 GRU 训练轮数。对应 failure case 为 `harness/failed_cases/fail_20260527_005_behavior_clone_gru_context8_regression.json`。

序列模型诊断已经接入 behavior clone dry-run 与训练报告。`sequence_diagnostics` 会记录：

- context padding 与 fully seeded sample 比例，用来判断 `context_frames` 是否主要由重复首帧填充。
- sequence span 秒数，用来确认 GRU 看到的是足够长的真实时间窗口，而不是过密或过短的局部片段。
- action transition / same action ratio，用来识别规则 Bot 轨迹是否本身存在动作持续性偏置。
- per-map sample ratio、动作分布和晚期低血量覆盖，用来解释地图条件化模型是否因为数据覆盖不均而移动失败面。

下一次 GRU、Transformer 或分阶段 policy 实验前，应先保存该诊断报告；若出现 `high_context_padding`、`high_action_persistence`、`low_late_low_health_coverage` 或 `map_sample_imbalance`，应先补轨迹窗口、调整 sample stride 或拆分阶段 policy，再考虑扩大训练轮数。

行为克隆入口还支持 `--entropy-regularization <weight>` 作为动作分布约束实验。训练目标会在 cross entropy 上减去平均 policy entropy，用小权重惩罚过度自信的动作分布；报告同时保留 `train_loss`、`train_cross_entropy_loss`、`train_entropy_nats` 和 `validation_entropy_nats`，避免把正则化后的目标误读为普通模仿损失改善。该旋钮只能作为动作塌缩诊断和修复尝试，不能替代 60 / 300 秒 high-pressure 对比或 RL policy acceptance。

首个完整 `entropy_regularization = 0.02` 的 `gru context8 + map-conditioning one_hot + danger sampling` 候选使用同一批 expanded、lategame、cracked lategame 和 caramel recovery 轨迹训练，离线 validation accuracy 为 87.84%，validation entropy 为 0.437509。60 秒 high-pressure 三图结果为 `soda-creek` 80%、`caramel-workshop` 100%、`cracked-star-jar` 80%；300 秒三图结果为 `soda-creek` 0%、`caramel-workshop` 33.33%、`cracked-star-jar` 0%，multi-map gate 仍为 `repair`。结论：entropy regularization 能改善动作分布可读性，但没有解决 movement-only imitation 的长局策略缺口；下一步应转向分阶段 policy、PPO 蒸馏初始化或把升级 / 阶段目标纳入训练，而不是继续扩大同一 GRU 轮数。

训练入口还新增 `--time-phase-conditioning one_hot`，用于把 Gym observation 的归一化时间进度显式拆成 opening / mid / late 三段 one-hot 特征。默认阈值为 0.2 和 0.6，在线评估也从当前 observation 计算同一组特征，旧 checkpoint 默认 `none` 保持兼容。当前 high-pressure 轨迹 dry-run 中 opening / mid / late 样本占比分别为 4.92% / 42.51% / 52.56%，说明阶段条件化可以把中后期分布显式暴露给 policy；但该 dry-run 只证明特征管线，不代表分阶段策略已经通过。

首个完整 time-phase GRU context8 候选在 60 秒 high-pressure 三图中达到 100% / 80% / 100%，动作熵保持健康；但 300 秒三图为 `soda-creek` 0%、`caramel-workshop` 0%、`cracked-star-jar` 33.33%，multi-map gate 仍为 `repair`。结论：阶段进度 one-hot 能改善短窗行为，但不能替代阶段目标、升级监督或 PPO 蒸馏；下一轮应真正拆分阶段 policy 或把阶段目标纳入训练损失。

为支持真正的分阶段策略实验，训练入口已支持 `--time-phase-filter opening|mid|late`，并新增 `create_staged_behavior_clone_policy.py` 将三段子模型打包成 staged checkpoint；在线 Gym 评估会按当前 observation 的时间进度选择 opening / mid / late 子策略。首个 packaging smoke 已证明 staged checkpoint 可通过 `train_sb3.py --behavior-clone-model` 加载并比较规则 Bot，但 1 epoch 子策略仍有动作偏置 repair，不能作为策略通过证据。

首个完整 staged GRU context8 候选分别训练 opening、mid、late 三段子策略并用相对路径打包；结果仍为 `repair`：60 秒 high-pressure 中 `soda-creek` 只有 20% 胜率且动作 3 占 76.72%，300 秒中 `soda-creek` 为 0%、`caramel-workshop` 和 `cracked-star-jar` 各 33.33%。这说明只按时间切换子模型不足以形成长局规划，下一步需要阶段目标监督、升级选择数据、更多 opening 覆盖或 PPO 蒸馏。

为排查 staged 子策略的数据窗口错配，已重新导出 300 秒 high-pressure 三图 10 seed phase-aligned 轨迹，使 `opening` 覆盖 0-60 秒而不是 60 秒短局中的前 12 秒。该修复把 opening 样本从 1080 提升到 5388，但 phase-aligned staged GRU context8 仍为 `repair`：60 秒 `soda-creek` 0% 胜率、动作 3 占 79.11%，300 秒 `soda-creek` 和 `caramel-workshop` 均为 0%。结论是补 opening 覆盖不足以修复 movement-only imitation，下一步应引入阶段目标监督、升级选择数据、teacher soft targets 或 PPO 蒸馏初始化。

## RL Policy Acceptance Gate

训练报告、行为克隆 validation accuracy、短局动作熵和单次 Gym 对比都不能单独把模型推进为 RL 测试 Bot。每个候选 policy 必须先写入 acceptance manifest，再由纯 Python 门禁统一检查：

```bash
python3 tools/validate_rl_policy_acceptance.py \
  python/train/rl_policy_acceptance_template.json \
  --repo-root .
```

该门禁至少检查：

- 模型文件、模型 metadata 或训练报告存在，并且训练报告不是 `smoke_only` 结论。
- 本机二进制诊断必须是 `local_binary_launch_ok`。
- high-pressure 三图 60 秒短中局对比存在，动作分布没有明显塌缩。
- high-pressure 三图 300 秒长局对比存在，不能低于规则 Bot 基线。
- rule Bot comparison、action entropy、dominant action、failure case 和 unresolved blocker 都被同一份报告引用。
- `gate_decision` 只能是 `blocked_by_local_binary_launch`、`watch`、`repair`、`reject` 或 `rl_test_bot_candidate`，不能写成 release、playtest、balance 或 fun 通过。

当前 `behavior_clone_kite_context3_danger_weighted_smoke`、`behavior_clone_kite_context5_danger_weighted_smoke`、`behavior_clone_kite_context5_caramel_recovery_smoke`、`behavior_clone_kite_gru_context8_map_conditioned_smoke` 和 `behavior_clone_kite_gru_context8_entropy002` manifest 都只能是 `repair`，`behavior_clone_kite_context5_map_conditioned_smoke` 只能是 `watch`：它们已引用本机启动恢复诊断、60 秒短中局对比和 300 秒长局规则 Bot 对比，但长局报告仍包含 0% 胜率、跨图回归、低于规则 Bot 基线或未解决 failure case。即使未来某个模型通过该门禁，它也只代表“可以作为 RL 测试 Bot 候选”，不代表游戏好玩、内容平衡、人工试玩或发布通过。

## 奖励函数

奖励函数不能只奖励活得久，否则 Bot 可能只逃跑。

建议：

```text
reward =
  + 生存时间小奖励
  + 击杀奖励
  + 拾取糖晶奖励
  + 升级奖励
  + Boss 伤害奖励
  - 受伤惩罚
  - 靠近死亡边界惩罚
  - 长时间不拾取经验惩罚
  - 原地卡住惩罚
```

示例权重：

- 每秒生存：+0.01
- 击杀普通怪：+0.05
- 击杀精英：+0.3
- Boss 伤害每 1%：+0.2
- 拾取经验：+0.02 * value
- 升级：+0.5
- 受伤：-0.05 * damage
- 死亡：-2.0
- 胜利：+5.0

权重需要通过实验调整。

当前 Gym reward 已输出可观测 breakdown 字段：

- 基础成长：`survival`、`kill`、`xp`、`level`、`damage_taken`、`action_repeat`、`terminal`
- 安全塑形：`low_health`、`boundary_risk`、`enemy_pressure`、`hazard_risk`、`boss_pressure`、`safety_delta`

安全塑形只作为训练信号，不是内容平衡门禁。它的目标是减少固定方向逃生、低血量贴边、忽略危险区和 Boss 压力等 RL policy exploit；是否真正改善泛化，仍必须通过多地图规则 Bot 对比验证。`safety_delta` 使用上一帧与当前帧的聚合风险差值，风险下降给小额正奖励，风险上升给小额负奖励，避免只用静态惩罚把 policy 推向过度保守。

## DQN 使用场景

DQN 适合：

- 离散动作
- 小观察空间
- 快速基线实验
- 判断 RL 是否能学会基本躲避

DQN 风险：

- 对奖励设计敏感
- 对连续移动不自然
- 容易学到保守策略

## PPO 使用场景

PPO 适合：

- 更稳定训练
- 连续动作
- 高维状态
- 生存类控制

建议：

- DQN 用于第一阶段验证。
- PPO 作为主力 AI Bot。

## 训练阶段

### Phase 1：移动生存

固定武器，固定升级策略。

目标：

- 学会远离敌人。
- 学会拾取附近糖晶。
- 存活超过规则 RandomBot。

### Phase 2：Build 感知

观察中加入当前 Build。

目标：

- 环绕武器时敢近身。
- 远程武器时保持距离。
- 控制流时停留在区域附近。

### Phase 3：升级选择

加入升级 action。

目标：

- 学会选择有利武器。
- 学会补防御。
- 学会追求进化。

### Phase 4：内容压力测试

固定训练好的模型，用于评估新内容。

目标：

- 找到过强内容。
- 找到无解波次。
- 找到安全漏洞。

## 评估指标

AI Bot 训练不看单局表现，看分布：

- 平均存活时间
- 胜率
- 升级数
- 击杀数
- Boss 击杀率
- 不同 seed 稳定性
- 是否学到单一 exploit
- 与规则 Bot 的差异

## 反作弊/防 exploit

RL Bot 很可能发现奇怪漏洞，比如：

- 卡墙角
- 利用刷怪距离
- 引怪绕圈导致敌人无法接近
- 只逃跑不玩核心成长
- 让投射物无限穿透

这些不是坏事。RL Bot 的价值就是找 exploit。

发现后处理：

- 如果是 bug，修 GameCore。
- 如果是合理高阶技巧，保留。
- 如果破坏游戏，调整地图/刷怪/敌人行为。

## 与 Harness 集成

AI Bot 不在普通每次提交 CI 中训练。

推荐层级：

- CI：规则 Bot 快速跑。
- Nightly：规则 Bot 大规模跑 + 已训练 RL Bot 评估。
- Weekly：重新训练或微调 RL Bot。
- Release Candidate：全部 Bot + replay + 人工试玩。

训练入口的 `--compare-rule-bots` 支持 `--compare-map-preset` 聚合输出多地图对比报告。该报告可以把每张地图的 RL policy 胜率、规则 Bot 胜率、动作分布和 `repair_maps` 放在同一个 JSON 中，避免手动拼接 6 份单地图报告。

## 模型版本管理

每个训练模型保存：

- 模型文件
- 训练内容版本
- 训练 seed
- reward 配置
- 评估报告
- 已知 exploit

模型不应无说明替换。
