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
- `--reward-profile standard|late-survival|long-run-retention`：选择 Rust `gym-bridge` 侧 reward shaping。`late-survival` 只作为 closed-loop 长局修复实验入口，会在 180 秒后逐步加强生存、安全风险下降、低血量、边界、敌群、危险区和 Boss 压力相关 reward / penalty，并提高 300 秒存活终局奖励。`long-run-retention` 用于修复 late-survival 扩展训练暴露出的中窗 retention 回归，会从 60 秒后逐步加强生存、安全风险下降、低血量、边界、敌群、危险区和 Boss 压力相关 reward / penalty，并放大重复动作惩罚，帮助观察 60-180 秒安全保持和动作多样性。两者都是训练实验入口，不是验收捷径，也不能替代 deterministic high-pressure 60 / 180 / 300 多图门禁。
- `--map-id`：在训练模式下指定训练后评估地图，避免 high-pressure 或 curriculum 实验仍默认用 `frosting-grassland` 做短局 gate。
- `--model-in`：从已有 SB3 模型 warm start 继续训练，用于课程学习、失败策略修复和后续规则 Bot 轨迹蒸馏实验。

其中 `high-pressure` 当前对应 `soda-creek`、`caramel-workshop`、`cracked-star-jar`，用于复查 observation v2 PPO 在 300 秒高压地图中的泛化失败。

针对 late-window 300 秒失败，应优先使用真实 closed-loop 训练 reward，而不是只依赖 evaluation-only adapter：

```bash
python3 python/train/train_sb3.py --algorithm ppo --reward-profile late-survival --train-map-preset high-pressure --train-map-selection random --train-seconds 300 --eval-seconds 60
```

针对 60-180 秒 retention 回归和 action 偏置，可以先用 `long-run-retention` 做小规模 closed-loop 修复实验：

```bash
python3 python/train/train_sb3.py --algorithm ppo --reward-profile long-run-retention --train-map-preset high-pressure --train-map-selection random --train-seconds 300 --eval-seconds 60
```

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

`tools/analyze_route_recovery_traces.py` 可读取这些 sampled trace，提取最负的 `route_recovery` 热点，并按地图、时间窗、压力标签和动作统计；它用于定位路线恢复训练失败面，不能替代 Replay 或 high-pressure gate。

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

Gym reward breakdown 已新增 `opening_edge_risk_delta`，用于在 opening 阶段奖励降低“贴边 + 敌压”的状态风险；它和 `corner_risk_delta` 一样是 state-based delta shaping，不绑定具体动作，目标是修复 seed `62405` 这类沿右边界进入角落的回归，同时避免重演 action-specific 惩罚导致的动作塌缩。但首个 stage 02 opening-edge-delta continuation 没有通过 60 秒 hard gate：从 stage 01 `corner_risk_delta` checkpoint warm start，继续使用 seed replay `62400-62409`、`--learning-rate 0.0001 --ent-coef 0.02` 和 `1024` timesteps 后，`soda-creek` 60 秒 high-pressure 10 seed 胜率从上一轮 seed replay 的 90% 回落到 50%，失败 seed 为 `62400` / `62401` / `62403` / `62405` / `62409`，其中多数仍是 action `4` 高占比 opening 早死。报告位于 `harness/reports/2026-05-27_rl_curriculum_stage02_opening_edge_delta_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_026_stage02_opening_edge_delta_opening_regression.json`。结论：单独增加边界风险 delta 不足以保留 stage 01 opening 修复，不能进入 stage 03；下一步应对 5 个失败 seed 做 failed-only snapshot trace，并优先比较 stage 01 成功路径、成功轨迹 replay / 行为约束或分离 opening policy。

stage 02 opening-edge-delta trace compare 已对 5 个失败 seed 复跑 failed-only snapshot trace，并和 stage 01 `corner_risk_delta` 同 seed 成功轨迹对比。stage 02 在 seed `62401` / `62409` 从未切到 action `7`，seed `62400` / `62403` 只在 terminal sample 才切到 action `7`，seed `62405` 虽较早切到 action `7` 但仍在左下角被最近敌人贴身击杀；stage 01 同 seed 胜利轨迹的共同点不是“完全不贴边”，而是更早且持续的撤离段把最终 `enemy_pressure_risk` 降到低值。报告位于 `harness/reports/2026-05-27_rl_curriculum_stage02_opening_edge_delta_trace_compare_001/summary.md`。结论：下一轮优先尝试成功轨迹 replay / 行为约束或分离 opening policy，而不是继续只堆 scalar reward。

Gym reward breakdown 已新增 `route_recovery`，用于在移动动作帧根据当前边界、敌人、危险区和 Boss 压力估算恢复方向：朝远离风险的方向移动给小额正奖励，继续朝贴边/危险源方向移动给小额负奖励，升级选择帧保持 0。它比早期 `corner_action_risk` 更通用，也比纯状态 delta 更直接地给动作选择反馈；但它仍只是 closed-loop 训练塑形信号，必须通过 high-pressure 60 / 180 / 300 秒多图对比验证，不能单独作为 RL policy acceptance。

首个 `route_recovery` closed-loop smoke 已完成：从 `late-survival` extended checkpoint warm start，使用 `long-run-retention` profile、升级选择 ranker、high-pressure 三图和 2048 timesteps 训练后，60 秒三图为 33.33% / 100% / 100%，180 秒为 33.33% / 0% / 33.33%，300 秒三图全部 0%。`route_recovery` 在所有窗口都保持负值，说明 reward 能捕捉不安全移动，但短 continuation 没学到稳定恢复路线；报告位于 `harness/reports/2026-05-27_rl_route_recovery_reward_profile_smoke_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_038_route_recovery_reward_profile_regression.json`。下一步不应直接放大该权重或只堆 timesteps，应先对最负的 failed-only trace 做路线恢复样本或分阶段策略诊断。

`route_recovery` trace 热点分析已完成，报告位于 `harness/reports/2026-05-27_rl_route_recovery_trace_hotspots_001/summary.md`。300 秒 high-pressure failed-only traces 中，`735 / 966` 个采样点为负 `route_recovery`；`boundary_edge` 出现在 `721` 个负样本，action `4` 出现在 `401` 个贴边热点行，最坏样本集中在 `cracked-star-jar` seed `62300` 的 120-185 秒。下一步应把这些贴边热点转为监督恢复或 policy constraint 实验，而不是继续泛化加权。

`train_sb3.py --trace-include-observation` 可在 sampled trace 行中显式写入 policy observation，用于后续修复样本提取；默认关闭，避免普通诊断 trace 体积膨胀。`tools/export_route_recovery_samples.py` 会从带 observation 的 `route_recovery` 贴边热点中导出 `edge_recovery_supervision_sample`，`target_source = route_recovery_trace_hotspot`，供 `train_behavior_clone.py` 作为 `repair_training_input` 读取。该导出只处理 sampled trace 中原动作继续顶边、目标动作不再顶边的样本，并且必须继续通过 `tools/validate_edge_recovery_samples.py`；它是监督修复材料，不是 Replay、不是 RL policy acceptance，也不能解除 high-pressure 多图门禁。

首个完整 `danger_action_change` staged GRU context8 候选改善了短窗动作分布：60 秒 high-pressure 中 `soda-creek` 从 0% 提升到 40%，normalized entropy 从 0.2356 提升到 0.6104，dominant action ratio 从 0.7911 降到 0.5226。但 300 秒三图仍全部为 0% 胜率，说明动作变化点加权只能修复短窗偏置，不能替代升级选择、阶段目标、路线规划或 PPO 闭环优化。

`python/train/distill_behavior_clone_to_sb3.py` 已提供 PPO 蒸馏初始化入口：它从规则 Bot 轨迹读取 observation，用 behavior clone teacher 输出 soft action probability，再监督训练 SB3 PPO `MlpPolicy` 并保存标准 `.zip` 与 metadata。蒸馏入口现在支持 `--teacher-temperature` 与 `--uniform-target-mix`，用于在 teacher probability 过尖或动作偏置过重时显式提高 target entropy；这些旋钮只属于 repair 实验，不是 policy gate。首个 256 样本 smoke 已证明 distilled `.zip` 可以被 `train_sb3.py --evaluate-model` 加载，但 1 epoch 模型仍为动作 3 deterministic smoke，不是策略通过证据；后续应在更大数据上蒸馏后继续 PPO 环境训练，并跑 high-pressure 60/300 秒对比。

首个全量蒸馏 + PPO warm-start 候选使用 21726 条 phase-aligned 样本和 action-change staged GRU teacher，5 epoch 蒸馏后 validation argmax accuracy 为 0.6916；随后在 high-pressure 三图上 warm-start PPO 2048 timesteps。结果仍为 `repair`：60 秒三图均触发 action distribution repair，300 秒三图全部 0% 胜率且 action 3 dominant ratio 为 0.7728 / 0.7631 / 0.8494。结论：蒸馏入口可用，但短 PPO 训练会继承 / 放大当前 teacher 的动作偏置；下一步应改 teacher targets、增加 entropy / curriculum，或纳入升级与阶段目标监督。

target-entropy 蒸馏候选使用 `--teacher-temperature 1.5 --uniform-target-mix 0.05`，把全量 target entropy 提高到 1.186717，并在 60 秒 high-pressure 三图达到 80% / 80% / 80% 胜率且不再触发 compare 内部 action-bias repair。但 300 秒三图仍全部 0% 胜率，长局中 action 6 dominant ratio 在 caramel / cracked 达到 0.8237 / 0.8119。结论：target entropy 是短窗修复方向，但不能替代升级 / 阶段目标监督或 warm-start 后的 PPO entropy / curriculum。

`train_sb3.py` 的 warm-start 路径现在允许 `--model-in ... --ent-coef <value>` 覆盖 PPO entropy coefficient，也允许 `--model-in ... --learning-rate <value>` 覆盖学习率；加载模型后会刷新 SB3 learning-rate schedule，并在训练报告中把 `algorithm_parameters_source` 标记为 `warm_start_metadata_with_overrides`。该能力用于可审计地测试 PPO 探索和小步修复；默认不改变旧模型行为，也不能绕过 high-pressure 对比和 RL acceptance。

`train_sb3.py` 现在还支持训练期 seed replay：`--train-seeds <a,b,c>` 或 `--train-seed-start <N> --train-seed-count <M>` 会把指定 seed 集合传给 Gym 环境，让 PPO/DQN 训练 reset 显式覆盖已知 opening / mid-window 回归 seed；`--seed-start` 仍只用于评估和规则 Bot 对比。该能力用于 stage 02 opening retention / regularization 实验，不能替代 60 秒 opening gate、180 秒三图对比或 failure case 审查。

首个 `ent_coef = 0.02` 的 target-entropy warm-start 候选改善了 60 秒动作分布：high-pressure 三图 normalized entropy 为 0.5801 / 0.5823 / 0.5307，dominant action ratio 均低于 0.45；但短窗胜率仍只有 80% / 60% / 80%，300 秒三图仍全部 0%。结论：entropy coefficient 是短窗动作多样性修复方向，但不能解决 movement-only policy 的长局目标缺失。

升级选择监督入口已经补上最小数据链路：`export-bot-trajectories --include-upgrade-samples true` 会在不破坏 movement dataset 的前提下输出 `upgrade_sample`，`train_behavior_clone.py` 的 movement loader 默认跳过并统计这些记录，`load_upgrade_choice_dataset` / `summarize_upgrade_choice_dataset` 可单独读取升级选择样本。当前 smoke 报告位于 `harness/reports/2026-05-27_rl_upgrade_choice_export_smoke_001/summary.md`；后续应扩大多地图升级样本覆盖、改进升级词表和阶段目标监督，而不是继续只调 movement entropy。

`python/train/train_upgrade_choice.py` 已提供首个监督升级选择 ranker smoke：它把每次升级 prompt 展开为一行一个候选升级，输入为 observation + upgrade id one-hot，目标为规则 Bot 选择的 upgrade。首个 4 choice / 12 row smoke 能写出 checkpoint 和报告，gate 为 `upgrade_choice_training_smoke_not_policy_gate`；它只证明模型管线，不代表升级策略质量。

Gym bridge 现在支持在 `step` 请求中传入 `upgrade_choice`。`SoftCandyStormEnv` 可接收 `upgrade_policy`，在 pending upgrade prompt 时用上一帧 observation 和 `upgrade_options` 调用 ranker，并把选择写进 bridge payload。`train_sb3.py --upgrade-choice-model` 会加载 ranker，并在 training、evaluation 与 comparison 路径中使用同一升级选择策略；报告会记录 `upgrade_policy`、`upgrade_policy_decisions` 和 `upgrade_policy_decision_count`。首个 60 秒 `soda-creek` smoke 实际穿过 1 次升级 prompt，报告位于 `harness/reports/2026-05-27_rl_upgrade_choice_gym_action_mode_smoke_001/summary.md`；gate 为 `gym_upgrade_action_mode_smoke_not_policy_gate`，仍不能作为 RL policy acceptance 或长局修复证据。

首个 `--upgrade-choice-model` 训练集成 smoke 已证明真实 PPO training path 会加载多地图升级 ranker，并在训练后的 120 秒 `soda-creek` evaluation 中记录 3 次升级选择。报告位于 `harness/reports/2026-05-27_rl_upgrade_choice_training_integration_smoke_001/summary.md`；gate 为 `upgrade_choice_training_integration_smoke_not_policy_gate`。这只证明 closed-loop training 不再被固定为默认第一个升级选项，不代表升级策略质量、长局修复或 RL acceptance。

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

为支持真正的分阶段策略实验，训练入口已支持 `--time-phase-filter opening|mid|late`，并新增 `create_staged_behavior_clone_policy.py` 将三段子模型打包成 staged checkpoint；旧 staged checkpoint 默认按当前 observation 的归一化时间进度选择 opening / mid / late 子策略。打包时可传入 `--phase-duration-seconds 300`，让在线 Gym 评估改用 `time_seconds / 300` 做绝对时间分段，避免 60 秒短窗在 36 秒就因为进度达到 0.6 而提前切到 late 子模型。首个 packaging smoke 已证明 staged checkpoint 可通过 `train_sb3.py --behavior-clone-model` 加载并比较规则 Bot，但 1 epoch 子策略仍有动作偏置 repair，不能作为策略通过证据。

clean teacher late survival 候选用 `--phase-duration-seconds 300` 重新打包后完成 deterministic high-pressure 60 / 180 / 300 秒复测：60 秒为 `soda-creek` 70%、`caramel-workshop` 100%、`cracked-star-jar` 80%，180 秒为 66.67%、100%、33.33%，300 秒三图仍全部 0%。结论：absolute-time dispatch 修复的是评估分段机制，但 clean teacher-only late replacement 仍缺少 opening / mid retention 和 long-run recovery objective，不能进入 stage 03 或 RL acceptance。

为补足 `caramel-workshop` clean teacher 覆盖，额外扫描 TankBot seed `62305-62324` 和 `62400-62449`。第一段 0/20 胜利，第二段只有 seed `62405` 胜利；该 seed 达到 300 秒、512 kills、level 8 且只受到 11.266667 damage。导出它的 180-300 秒轨迹后，expanded clean teacher dry-run 从 6124 条样本提升到 6843 条，`caramel-workshop` 占比从 11.76% 提升到 21.03%。这只是数据覆盖证据，后续仍必须训练新 late 子模型并复跑 deterministic 60 / 180 / 300 秒对比。

expanded clean teacher late 子模型训练后 validation_accuracy 从 0.7200 提升到 0.7633，但 deterministic high-pressure 结果没有修复：60 秒仍为 70% / 100% / 80%，180 秒为 66.67% / 100% / 33.33%，300 秒三图仍全部 0%。结论：新增 caramel clean teacher 只改善离线覆盖，不足以修复 online long-run recovery；下一步不要继续单独训练 clean teacher-only late replacement，应加入 opening/mid retention、contrastive 约束或 closed-loop late survival 目标后再复跑 gate。

late risk + clean teacher mix 候选把 phase-aligned 规则轨迹、expanded clean teacher 成功轨迹、edge recovery 样本和 risk recovery 样本一起训练 late 子模型，validation_accuracy 达到 0.8025。配合 stage01 opening wrapper 后，60 秒为 100% / 100% / 90%，180 秒三图均 100%，但 300 秒三图仍全部 0%，且 9 个失败全部落在 `late_180_to_300`。结论：失败面已收窄到 late-window long-run recovery，下一步应转向 closed-loop late survival、路线规划约束、升级选择交互或更明确的 hazard + boss pressure 目标，而不是继续只加离线 imitation 样本。

首个 `late-survival` reward profile closed-loop PPO smoke 已完成：从 stage01 `corner_risk_delta` checkpoint warm start，使用 high-pressure 三图、300 秒 episode、`62300-62308` 训练 seed 和 1024 timesteps。60 秒 high-pressure 三图 3 seed 均为 100%，180 秒为 66.67% / 100% / 100%，但 300 秒三图仍全部 0%，multi-map gate 为 `multimap_comparison_recorded_needs_policy_repair`。失败分析显示 9 个 300 秒失败中 8 个落在 `late_180_to_300`，另有 `soda-creek` seed `62301` opening 早死。报告位于 `harness/reports/2026-05-27_rl_closed_loop_late_survival_reward_profile_smoke_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_035_closed_loop_late_survival_reward_profile_gap.json`。结论：真实 closed-loop reward profile 链路可用，但 smoke 规模不足以解除 long-run blocker；下一步应扩大 late-survival 训练并加入低血量恢复、hazard + boss pressure 路线目标和 opening retention 检查。

继续从该 smoke checkpoint 训练 5120 timesteps、降低学习率到 `0.0001` 并覆盖 `62300-62320` 后，300 秒 `cracked-star-jar` 从 0% 提升到 33.33%，但 `soda-creek` 和 `caramel-workshop` 仍为 0%，整体 300 秒平均胜率只有 11.11%；同时 180 秒三图从 66.67% / 100% / 100% 回落到 33.33% / 100% / 66.67%，并出现 action `4` 偏置。报告位于 `harness/reports/2026-05-27_rl_closed_loop_late_survival_reward_profile_extended_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_036_extended_late_survival_reward_profile_regression.json`。结论：只扩大 closed-loop late-survival timesteps 会产生少量长窗信号，但带来中窗 retention 回归；下一步需要显式 mid-window retention、动作多样性约束和低血量 / hazard / boss pressure 路线目标，而不是继续只堆训练步数。

首个 `long-run-retention` reward profile smoke 从 late-survival extended checkpoint warm start，并从 60 秒后强化 survival / safety / low-health / boundary / enemy / hazard / boss pressure 和重复动作惩罚。2048 timesteps 后，60 秒 high-pressure 三图只有 66.67% / 66.67% / 100%，180 秒为 33.33% / 66.67% / 100%，300 秒三图全部 0%；相比上一轮 extended，`cracked-star-jar` 300 秒从 33.33% 回落到 0%。报告位于 `harness/reports/2026-05-27_rl_closed_loop_long_run_retention_reward_profile_smoke_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_037_long_run_retention_reward_profile_regression.json`。结论：早启动 retention reward 和 action-repeat penalty 没有提供足够路线目标，反而暴露 opening / mid / late 全窗口失败；下一步不应继续只堆 long-run-retention timesteps，应结合 opening retention、显式路线 / recovery objective、低血量脱险、hazard + boss pressure 和 upgrade-choice 交互。

首个完整 staged GRU context8 候选分别训练 opening、mid、late 三段子策略并用相对路径打包；结果仍为 `repair`：60 秒 high-pressure 中 `soda-creek` 只有 20% 胜率且动作 3 占 76.72%，300 秒中 `soda-creek` 为 0%、`caramel-workshop` 和 `cracked-star-jar` 各 33.33%。这说明只按时间切换子模型不足以形成长局规划，下一步需要阶段目标监督、升级选择数据、更多 opening 覆盖或 PPO 蒸馏。

为排查 staged 子策略的数据窗口错配，已重新导出 300 秒 high-pressure 三图 10 seed phase-aligned 轨迹，使 `opening` 覆盖 0-60 秒而不是 60 秒短局中的前 12 秒。该修复把 opening 样本从 1080 提升到 5388，但 phase-aligned staged GRU context8 仍为 `repair`：60 秒 `soda-creek` 0% 胜率、动作 3 占 79.11%，300 秒 `soda-creek` 和 `caramel-workshop` 均为 0%。结论是补 opening 覆盖不足以修复 movement-only imitation，下一步应引入阶段目标监督、升级选择数据、teacher soft targets 或 PPO 蒸馏初始化。

stage 02 的 staged opening wrapper 进一步验证了“分离开局策略”这个方向：评估时前 60 秒使用 stage 01 `corner_risk_delta` checkpoint，60 秒后切回 stage 02 `opening_edge_delta` checkpoint。60 秒 high-pressure 三图 10 seed 全部为 100% 胜率，说明 stage 01 opening 行为可以被保留；但 180 秒三图 3 seed 中 `soda-creek` seed `62201` 在 115.5319 秒死亡，`soda-creek` 胜率只有 66.67%。该结果只证明 staged evaluation 有诊断价值，不是新训练 checkpoint，也不是 RL policy acceptance；stage 02 仍需修复 60 秒 handoff 后的中局压力恢复，不能进入 stage 03。该 wrapper 现已允许 `--opening-model` 与 `--behavior-clone-model` 组合，用于诊断“SB3 opening + handoff-only behavior clone fallback”，但这种组合仍必须通过 deterministic high-pressure 对比，不能作为 acceptance 捷径。

首个 `SB3 opening + edge-aux behavior clone fallback` probe 使用 stage01 `corner_risk_delta` checkpoint 负责前 60 秒，并在之后切到 edge-aux entropy/class staged behavior clone。60 秒 high-pressure 三图 10 seed 全部为 100%，说明新组合入口能保住 opening；但 180 秒 high-pressure 三图 3 seed 中 `soda-creek` 与 `cracked-star-jar` 均只有 66.67%，两个失败都发生在 seed `62201` 的 `mid_60_to_180` 窗口。报告位于 `harness/reports/2026-05-27_rl_behavior_clone_edge_aux_staged_opening_handoff_probe_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_030_edge_aux_staged_opening_handoff_gap.json`。结论：blocker 已从 opening retention 收窄到 handoff/mid recovery，但仍不能进入 stage 03。

对 `SB3 opening + edge-aux behavior clone fallback` 的两个失败局输出 failed-only trace 后，问题进一步收窄为“60 秒后 deterministic fallback 在边界钉死状态下仍高置信顶墙”。`soda-creek / 62201` 在 `171.2743s` 死亡，344 个采样帧中 312 个处于 `edge_risk >= 0.9`，终局位于 `(-1200, -900)` 左下角并以 0.9672 置信度选择 action `5`；`cracked-star-jar / 62201` 在 `157.3380s` 死亡，316 个采样帧中 301 个处于 `edge_risk >= 0.9`，终局位于左边界并以 0.9172 置信度选择 action `7`。报告位于 `harness/reports/2026-05-27_rl_behavior_clone_edge_aux_staged_opening_handoff_trace_001/summary.md` 和 `trace_analysis.json`。结论：下一步不应继续把精力放在 opening reward，而应训练或约束 handoff/mid fallback 在贴边时回到开阔区域；该 trace 仍只是诊断证据，不是修复、Replay 或 RL acceptance。

首个 handoff-window edge-aux staged GRU context8 候选把 edge recovery repair 样本限制在 60-180 秒后再按阶段过滤，opening 子模型保留 5388 条规则轨迹且 edge repair 样本为 0，mid / late 分别保留 799 / 1040 条 repair 样本。配合 stage01 opening wrapper 后，deterministic 60 秒三图 10 seed 和 180 秒三图 3 seed 均达到 100% 胜率，说明 seed `62201` 的 handoff gap 已被这个候选修掉；但 300 秒三图 3 seed 中 `soda-creek` 与 `caramel-workshop` 均为 0%，`cracked-star-jar` 为 33.33%，8 个失败全部落在 `late_180_to_300`。报告位于 `harness/reports/2026-05-27_rl_behavior_clone_edge_aux_handoff_window_staged_gru_context8_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_031_edge_aux_handoff_window_late_gap.json`。结论：blocker 从 handoff/mid recovery 推进到 late-window long-run recovery，但仍不能进入 stage 03 或 RL acceptance。

对 handoff-window 候选的 300 秒 late failures 输出 failed-only trace 后，8 个终局中 7 个仍处于 `edge_risk >= 0.9`，5 个带 `hazard_pressure_risk > 0`，5 个带 `boss_pressure_risk > 0`，5 个以 direct contact 结束；其中 `caramel-workshop` 三个终局全部带 hazard pressure，`soda-creek` 三个终局全部 edge-pinned。报告位于 `harness/reports/2026-05-27_rl_behavior_clone_edge_aux_handoff_window_late_trace_001/summary.md` 和 `trace_analysis.json`。结论：下一步 late repair 不能只复刻 60-180 秒离边样本，还要同时处理 hazard field、Boss / enemy pressure 和低血量恢复。

`train_sb3.py` 已新增 `--late-recovery-filter` 作为 late-window deterministic 诊断 wrapper，默认只在 180 秒后介入，并根据边界、hazard、Boss / enemy pressure 与低血量上下文改写高风险 movement action；配合 `--edge-recovery-samples-out` 会导出 `risk_recovery_supervision_sample`，供 `train_behavior_clone.py` 作为 movement repair target 读取。行为克隆入口同步提供 `--risk-recovery-sample-weight`、`--risk-recovery-min-seconds` 和 `--risk-recovery-max-seconds`，用于把 late repair 样本限制在 180-300 秒窗口并加权训练。该能力只是把 handoff-window late trace 的修复方向转成可训练材料，不是新 policy checkpoint、不是 300 秒 gate 通过证据，也不能解除 `rl_policy_multimap_generalization_gap`。

对 staged opening 的 `soda-creek` seed `62201` 进行 failed-only trace 后，失败面从“开局是否活过 60 秒”收窄为“60 秒交接后能否从边界钉死状态恢复”。交接时玩家已在 `(-1200, -900)` 左下边界，`edge_risk = 1.0`，但 `enemy_pressure_risk = 0` 且生命仍有 92.4698；fallback policy 随后在 `60-75s` 采样窗口里全部选择 action `7`，相当于持续向左顶墙，生命降到 59.7596 并重新被敌人贴上。最终 115.5319 秒死亡时仍在左边界，action `7` 置信度为 0.8487。下一轮 stage 02 应优先训练/约束 handoff recovery，而不是继续只调 opening reward。

同一 staged policy、同一 `soda-creek` seed `62201` 的 stochastic 探针连续两次活到 180 秒；带 trace 的一局在 60 秒交接时位于 `(-862.2731, -900)`，生命 113.2499，`60-75s` 采样动作覆盖 `0/3/4/6/7/8`，到 90 秒已回到 `x = -222.8753` 且低血量风险为 0。这个结果不能替代 deterministic gate，也不能作为 RL acceptance；但它说明恢复动作已经存在于 policy distribution 中，失败主要来自 deterministic argmax 在交接点压成高置信顶墙路径。后续可审计方向是 seeded stochastic 规则、温度/熵约束、动作平滑或显式 handoff recovery 行为约束。

`train_sb3.py` 的 evaluation / comparison / training 后评估路径现已支持 `--eval-stochastic --eval-random-seed <N>`，会在随机动作采样前 seed Python、NumPy、Torch 和支持 `set_random_seed` 的 policy model，并在报告中写入 `action_random_seed` 与 `action_random_seed_report`。该能力只用于复现 stochastic 探针和诊断 policy distribution 中是否存在恢复动作；不能绕过 deterministic high-pressure gate、180/300 秒多图对比、failure case 审查或 RL policy acceptance manifest。

使用同一 staged policy、`soda-creek` map seed `62201` 和 `action_random_seed = 62201` 复跑 seeded stochastic probe 后，两份无 trace evaluation JSON 字节级一致，带 trace 版本也保持相同 summary；该轨迹在 60 秒交接时位于开阔区域 `(497.8561, 133.6539)`，生命 `119.55`，最终以 `180.0095s` 胜利结束，normalized action entropy 为 `0.8275`。报告位于 `harness/reports/2026-05-27_rl_curriculum_stage02_seeded_stochastic_probe_001/summary.md`。结论仍是诊断证据：seeded stochastic 单 seed 成功不能替代 deterministic gate 或多 seed / 多图 acceptance。

进一步把 `action_random_seed = 62201` 扩展到 high-pressure 三图小矩阵后，60 秒 10 seed opening gate probe 和 180 秒 3 seed handoff probe 均为三图 100% 胜率，normalized action entropy 分别维持在约 `0.81-0.84` 区间。报告位于 `harness/reports/2026-05-27_rl_curriculum_stage02_seeded_stochastic_multimap_001/summary.md`。该结果说明 seeded stochastic 是可继续探索的 handoff repair 方向，但仍不是现有 deterministic gate 通过，也不是 stage 03 许可；若要把 stochastic 纳入门禁，必须先定义明确的多 seed、多图、可复现阈值。

`tools/validate_seeded_stochastic_gate.py` 已把上述 seeded stochastic 检查固化为 watch-only validator：要求同一 `action_random_seed`、stochastic action selection、high-pressure 三图、60 秒 10 seed、180 秒 3 seed、胜率 100%、动作熵不低于阈值且无 repair finding。当前报告返回 `seeded_stochastic_watch_ready`，但 validator 的限制说明明确写明它不能输出 RL acceptance，也不能解除 deterministic handoff blocker。

正式 `tools/validate_rl_policy_acceptance.py` 同步增加了防线：如果 evaluation / comparison 报告标记为 `action_selection = stochastic` 或包含 `action_random_seed`，则会被判定为 watch evidence only，不能用于 `rl_test_bot_candidate`。这样 seeded stochastic 方向可以继续做诊断和修复，但不会绕过 deterministic acceptance 边界。

`train_sb3.py` 还提供 `--edge-recovery-filter` 作为 deterministic handoff repair 诊断 wrapper：当 policy 在贴近地图边界时仍选择继续往墙里推的动作，它会改选当前动作分布中最高分且不继续顶墙的动作，并在报告中写入 `policy_adapter.mode = edge_recovery_filter`。该 wrapper 只用于定位 deterministic argmax 的卡墙失败面；正式 acceptance validator 会拒绝任何带 `policy_adapter` 的报告，避免把手写过滤器误当成训练策略通过。

使用 `--edge-recovery-filter --edge-recovery-distance 32` 复跑 stage 02 staged policy 后，原 deterministic 失败 seed `soda-creek / 62201` 可活到 `180.0095s`；high-pressure 三图 60 秒 10 seed 与 180 秒 3 seed 也均为 100% 胜率，但动作熵低于 seeded stochastic 路径，约 `0.56-0.72`。报告位于 `harness/reports/2026-05-27_rl_curriculum_stage02_edge_recovery_filter_probe_001/summary.md`。结论：这确认失败面是 deterministic edge-pushing handoff bug，但 wrapper 是手写 adapter，只能指导后续训练 / 行为约束，不能作为 policy acceptance。

`--edge-recovery-samples-out` 可在 `edge_recovery_filter` 实际替换 deterministic 动作时输出 JSONL 监督样本。每条样本包含 observation v2、原始顶墙动作、目标非顶墙动作、policy action scores、边界诊断和限制说明，角色是 `repair_training_input`。`tools/validate_edge_recovery_samples.py` 会校验原动作确实顶边、目标动作不再顶边、observation 长度一致，并明确该样本不能作为 RL policy acceptance。首份 `soda-creek / 62201` staged policy 样本报告位于 `harness/reports/2026-05-27_rl_curriculum_stage02_edge_recovery_samples_001/summary.md`：共导出并校验 `2215` 条样本，时间范围 `6.8333-178.7759s`。下一步可以把这些样本转成 handoff recovery 行为约束或监督微调输入，但最终仍必须重新通过 deterministic high-pressure 60 秒 / 180 秒 / 300 秒多图对比和正式 acceptance manifest。

`train_behavior_clone.py` 已能把 `edge_recovery_supervision_sample` 作为 movement repair target 读取，并在 dataset summary 中单独记录 `edge_recovery_sample_records` 与 `sample_source_distribution`。首个 smoke 使用上述 `2215` 条样本完成 dry-run 和 1 epoch MLP 训练，报告位于 `harness/reports/2026-05-27_rl_edge_recovery_behavior_clone_dataset_smoke_001/summary.md`；结论仍是 `behavior_clone_smoke_only_not_policy_gate`，只证明数据能进入监督训练链路，不代表策略可用。训练入口还提供 `--edge-recovery-sample-weight`，用于把这些 repair 样本与原始规则 Bot 轨迹混合时显式加权成 handoff recovery 辅助约束；该权重只影响 supervised sampling，不能绕过 deterministic high-pressure gate。

为避免 repair 样本污染 opening 子模型，行为克隆入口还提供 `--edge-recovery-min-seconds` 和 `--edge-recovery-max-seconds`。这两个参数只过滤 `edge_recovery_supervision_sample`，不会移除正常规则 Bot 轨迹样本；因此 staged clone 可以在训练 opening 子模型时排除 handoff repair 样本，在训练 mid / handoff 子模型时再显式引入 60 秒后的 edge recovery 约束。首个 handoff-only dataset smoke 位于 `harness/reports/2026-05-27_rl_edge_recovery_handoff_only_dataset_smoke_001/summary.md`：opening dry-run 保留 5388 条规则轨迹且 edge repair 样本为 0，mid dry-run 保留 10710 条样本，其中 799 条为 60 秒后的 edge recovery repair 样本。该报告只证明数据切分入口可用，不代表训练策略或 RL gate 通过。

首个 `edge_recovery_sample_weight = 4.0` 的 staged GRU context8 混合候选使用 phase-aligned 三图 KiteBot 轨迹与 `2215` 条 edge recovery 样本训练三段子策略，但没有通过 60 秒 opening hard gate：`soda-creek` 10 seed 胜率只有 `40%`，action `3` 占 `87.27%`，action entropy 为 `0.7851` bits。报告位于 `harness/reports/2026-05-27_rl_behavior_clone_edge_recovery_aux_staged_gru_context8_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_028_edge_recovery_aux_opening_regression.json`。因此未运行 180 秒 handoff 对比，也不能进入 stage 03；下一轮必须先修 opening action `3` collapse。

加入 `inverse_frequency` class weighting 与 `entropy_regularization = 0.02` 后，动作分布明显改善但仍未通过 opening hard gate：`soda-creek` 60 秒 10 seed 胜率为 `50%`，action `3` 占比降到 `66.58%`，action entropy 提高到 `1.6725` bits；`caramel-workshop` 与 `cracked-star-jar` 均为 `90%`。报告位于 `harness/reports/2026-05-27_rl_behavior_clone_edge_aux_entropy_class_staged_gru_context8_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_029_edge_aux_entropy_class_opening_gap.json`。结论：class / entropy 可以缓解 action collapse，但不能替代 opening retention 或 handoff-only 约束。

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
- 安全塑形：`low_health`、`boundary_risk`、`enemy_pressure`、`hazard_risk`、`boss_pressure`、`safety_delta`、`route_recovery`

安全塑形只作为训练信号，不是内容平衡门禁。它的目标是减少固定方向逃生、低血量贴边、忽略危险区和 Boss 压力等 RL policy exploit；是否真正改善泛化，仍必须通过多地图规则 Bot 对比验证。`safety_delta` 使用上一帧与当前帧的聚合风险差值，风险下降给小额正奖励，风险上升给小额负奖励，避免只用静态惩罚把 policy 推向过度保守。`route_recovery` 根据当前动作是否朝恢复方向移动给小额反馈，用于修复高压状态下继续贴边或冲向危险源的动作偏置。

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
