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

导出格式为 JSONL：第一行 `metadata`，中间为 `sample`，最后为 `summary`。每个 sample 包含 observation v2 和离散 movement action，可用于后续行为克隆、规则 Bot 轨迹蒸馏或 curriculum 诊断。Phase 1 只导出 movement 状态；升级选择状态会跳过并计数，避免把 Build 决策混入移动生存训练。

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

3 帧 danger-weighted behavior clone 已完成训练，输入长度为 435，validation accuracy 为 86.87%。该结果仍只是训练 smoke：当前本机 Rust 可执行文件启动被 `spctl` 拒绝，`game_harness gym-bridge` 在 `_dyld_start` 阶段阻塞，60/300 秒 Gym 对比未完成。因此序列上下文模型尚未通过任何 policy gate。

在本地新生成 Mach-O binary 启动问题恢复前，不应继续解读 RL/Gym/Harness 运行结果。恢复交接包由 `tools/create_local_binary_launch_recovery_packet.py` 生成，用来固定当前诊断、failure case 和恢复后重跑清单；它不是 RL policy gate 通过证据。恢复后必须先让 `tools/diagnose_local_binary_launch.py` 返回 `local_binary_launch_ok`，再依次重跑 `game_harness --help`、`cargo test --workspace`，最后重跑 context3 behavior clone 的 60/300 秒 high-pressure 对比。

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

当前 `behavior_clone_kite_context3_danger_weighted_smoke` manifest 只能是 `blocked_by_local_binary_launch`：它有训练 smoke 和上下文输入证据，但缺少恢复后的 60/300 秒 high-pressure 对比，也仍引用本机二进制启动 failure case。即使未来某个模型通过该门禁，它也只代表“可以作为 RL 测试 Bot 候选”，不代表游戏好玩、内容平衡、人工试玩或发布通过。

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
