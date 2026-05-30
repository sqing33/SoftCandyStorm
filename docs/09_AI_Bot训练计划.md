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
- `--reward-profile standard|late-survival|long-run-retention|late-route-recovery|late-win-conversion|opening-route-recovery`：选择 Rust `gym-bridge` 侧 reward shaping。`late-survival` 只作为 closed-loop 长局修复实验入口，会在 180 秒后逐步加强生存、安全风险下降、低血量、边界、敌群、危险区和 Boss 压力相关 reward / penalty，并提高 300 秒存活终局奖励。`long-run-retention` 用于修复 late-survival 扩展训练暴露出的中窗 retention 回归，会从 60 秒后逐步加强生存、安全风险下降、低血量、边界、敌群、危险区和 Boss 压力相关 reward / penalty，并放大重复动作惩罚，帮助观察 60-180 秒安全保持和动作多样性。`late-route-recovery` 从 120 秒后逐步放大路线恢复、低血量、危险区、Boss 压力和轻量重复动作惩罚，用于 180-300 秒 closed-loop 路线修复消融。`late-win-conversion` 只在 240 秒后 ramp up，强化 final-minute route recovery、重复动作惩罚和 victory / defeat terminal signal，用于当前“能进 late 但不能把 300 秒窗口转成胜利”的探针。`opening-route-recovery` 只在 60 秒内放大路线恢复、安全风险、低血量、边界、敌群与重复动作信号，用于 seed `63402` 这类开局贴边后 action lock 的 closed-loop 修复探针。它们都是训练实验入口，不是验收捷径，也不能替代 deterministic high-pressure 60 / 180 / 300 多图门禁。
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

针对 late-window 存活已经有局部信号、但 240-300 秒无法转换为胜利的策略，可以用 `late-win-conversion` 做 final-minute closed-loop 探针：

```bash
python3 python/train/train_sb3.py --algorithm ppo --reward-profile late-win-conversion --train-map-preset high-pressure --train-map-selection random --train-seconds 300 --eval-seconds 60
```

首个 `late-win-conversion` 蒸馏探针把 current-failure fallback best teacher 蒸馏为 SB3 PPO 后继续 2048 timestep closed-loop 训练，但 60 秒 `soda-creek` 从 `1.0` 回落到 `0.3333`，180 秒回落到 `0.0`，300 秒仍为 `0.0/0.0/0.3333`。该结果记录为 `fail_20260528_080`，说明 final-minute reward profile 只能作为诊断入口，不能单独替代 opening retention、staged opening protection 或 KL / behavior-clone anchor。

为避免下一轮蒸馏再次丢失 staged opening 行为，`distill_behavior_clone_to_sb3.py` 已支持 `--opening-model` 和 `--opening-seconds`。当 teacher 是“SB3 opening + behavior-clone fallback”组合时，蒸馏脚本会按样本 `time_seconds` 选择 opening 或 fallback 概率目标；这仍只是初始化工具，必须继续经过 60 / 180 / 300 秒 high-pressure 与 no-regression 检查。

首个 opening-aware `late-win-conversion` 蒸馏探针确认该工具能正确记录 opening teacher，但 checkpoint 仍被拒绝：60 秒为 `0.6667/0.6667/1.0`，180 秒为 `0.3333/0.6667/0.6667`，300 秒三图仍为 `0.0/0.0/0.0`。相对 current-failure fallback best 触发 `8` 个 no-regression blockers，且丢掉 `cracked-star-jar` 300 秒 `0.3333` 胜率；相对 seed63100 baseline 仍有 `4` 个 blockers。该结果记录为 `fail_20260528_081`，说明 opening-aware distillation 只能修正 teacher 入口，不能替代 KL / behavior-clone anchor、per-map constrained repair 或显式 retention 保护。

为把 KL / behavior-clone anchor 从口头建议变成可审计证据，`compare_sb3_to_behavior_clone_anchor.py` 已提供 SB3 candidate 对 behavior-clone anchor 的离线对齐诊断。它会在轨迹样本上逐步设置 `time_seconds` / `map_id` / `seed`，输出整体、按地图和按时间窗的 KL divergence、argmax agreement 与阈值 blockers；也支持同样的 `--opening-model` anchor wrapper。该报告只用于判断 closed-loop 续训是否偏离 anchor，不能替代 high-pressure 对比、window no-regression 或 RL acceptance。

首个 opening-aware PPO anchor alignment 报告显示，候选相对“SB3 stage 02 opening + current-failure fallback”anchor 的 overall mean KL 为 `0.353364`，高于诊断阈值 `0.25`，overall argmax agreement 为 `0.6899`，低于阈值 `0.75`。分桶看，`opening_lt_60` argmax agreement 只有 `0.4742`，`mid_60_to_180` mean KL 达到 `0.436179`。这解释了为什么该 checkpoint 动作熵更高但仍破坏 `soda-creek` 60 秒和多图 180 秒窗口；后续需要真正的 KL / behavior-clone anchor 训练约束，而不是只做无约束 PPO 续训。

`train_sb3.py` 现在提供 closed-loop PPO 的 behavior-clone anchor KL regularization 入口。训练时传入 `--anchor-model` 和一个或多个 `--anchor-dataset` 后，脚本会把 PPO 训练切成若干 chunk，并在每个 chunk 后用离线 anchor 样本最小化当前 SB3 policy 相对 anchor 概率分布的 KL；`--anchor-opening-model` 可复用 SB3 opening + behavior-clone fallback 组合，避免 stage 02 续训再次丢掉 opening policy。训练报告会记录每个 chunk 的 validation KL、argmax agreement 和最终 `anchor_regularization.final_validation`。这只是漂移约束和修复训练工具，checkpoint 仍必须再跑 anchor alignment、60 / 180 / 300 秒 high-pressure、no-regression 和 RL acceptance。

anchor KL 训练现支持 `--anchor-sample-weighting time_bucket_balance` 与 `--anchor-sample-weighting map_time_bucket_balance`。前者按 opening / mid / late / post 样本桶反比加权，后者按 `map_id + time bucket` 组合加权，用于避免全量 anchor 数据被某一阶段或地图主导；报告会在 `anchor_regularization.sample_weighting` 中记录每组样本数、权重倍数和均值。训练入口也支持 `--anchor-include-time-buckets opening_lt_60,mid_60_to_180,...` 与 `--anchor-time-bucket-weights bucket=weight,...`，用于把 KL 约束限定到特定阶段或为 opening / mid / late 设置不同 anchor 强度。该能力只改变离线 KL 约束强度，不代表 checkpoint 通过，也不能替代全量 alignment 与窗口 no-regression。

首个 anchor-regularized PPO smoke 从 opening-aware distilled PPO 重新训练 `1024` timesteps，并使用 `8192` 条 anchor 样本做每 `512` timestep 一次的 KL 约束。训练内 validation KL 降到 `0.265304`、argmax agreement 达到 `0.8462`，但全量 `36426` 样本 anchor alignment 仍失败：overall mean KL `0.346885`，argmax agreement `0.7044`。窗口对比相对上一轮 opening-aware PPO 只剩 `1` 个 no-regression blocker，但相对 current-failure fallback best 仍有 `7` 个 blockers，相对 seed63100 baseline 仍有 `4` 个 blockers；300 秒 `soda-creek` / `caramel-workshop` 仍为 `0.0` 胜率。该结果记录为 `fail_20260528_082`，说明 anchor 方向有改善信号但需要全量 / 分桶 / 更强约束。

full-dataset + `map_time_bucket_balance` 的更强 anchor 探针也已失败。该 run 使用全量 `36426` 样本、`weight=2.0`、每 `512` timestep 做 `2` 个 KL epoch，opening bucket mean KL 从上一轮 `0.335834` 降到 `0.25152`，但 overall mean KL 仍为 `0.332669`、argmax agreement `0.6977`，mid `60-180s` mean KL 仍为 `0.420859`。60 / 180 / 300 秒结果为 `0.6667/0.6667/1.0`、`0.6667/0.6667/0.6667`、`0.0/0.0/0.0`，相对 current-failure fallback best 有 `8` 个 no-regression blockers，并丢掉 cracked-star-jar 300 秒 `0.3333` 胜率。记录 `fail_20260528_083`；下一步不应继续提高全局 anchor weight，应拆 phase-specific anchor、显式 opening freeze/wrapper 与 mid/late constrained repair。

phase-specific anchor multiplier smoke 同样失败。该 run 使用全量 `36426` 样本、`map_time_bucket_balance`、全局 `weight=1.0`，并对 opening / mid / late 施加 `1.5x / 1.25x / 0.75x` multiplier。训练内 final validation 为 mean KL `0.342834`、argmax agreement `0.6798`；全量 anchor alignment 为 overall mean KL `0.345606`、argmax agreement `0.6841`。opening mean KL 降到 `0.220892`，但 opening argmax agreement 仍只有 `0.5769`，mid `60-180s` mean KL 仍为 `0.440395`。60 / 180 / 300 秒结果仍为 `0.6667/0.6667/1.0`、`0.6667/0.6667/0.6667`、`0.0/0.0/0.0`；相对 opening-aware probe 剩 `1` 个 blocker，相对 current-failure fallback best 仍有 `8` 个 blockers，相对 seed63100 baseline 有 `5` 个 blockers。记录 `fail_20260528_084`；下一步应把 opening freeze/wrapper 与 mid/late constrained repair 拆成两个独立目标，而不是继续做单次全量 anchor multiplier。

显式 opening wrapper 诊断证明短窗可隔离但不能解除中后期问题。该 probe 使用 `stage_02_late_180_to_300.zip` 作为前 `60s` opening wrapper，之后切到 `ppo_phase_specific_anchor_smoke.zip`，不训练新 checkpoint。60 秒结果为 `1.0/0.6667/1.0`，修掉了 phase-specific anchor PPO 的 `soda-creek` 60 秒 blocker；但 180 秒变成 `0.3333/0.6667/0.6667`，300 秒仍为 `0.0/0.0/0.0`。相对无 wrapper 的 phase-specific anchor PPO 有 `3` 个 blockers，相对 current-failure fallback best 有 `5` 个 blockers，相对 seed63100 baseline 有 `2` 个 blockers。记录 `fail_20260528_085`；下一步应聚焦 60-180 秒 handoff 与 fallback constrained repair，尤其是 `soda-creek` seed `63101` 在 `70.1326s` 和 seed `63100` 在 `163.5393s` 的 post-wrapper death。

handoff splice wrapper 进一步证明 mid specialist 不能直接拼进候选策略。该 evaluation-only probe 使用 stage 02 SB3 opening 负责前 `60s`，用 current-failure trace incremental fallback 负责 `60-180s`，再切回 current-failure best fallback 负责 `180s` 后窗口。60 秒保持 `1.0/0.6667/1.0`，180 秒 `cracked-star-jar` 从 current best 的 `0.6667` 提到 `1.0`，但 `soda-creek` 180 秒平均存活相对 current best 下降 `6.2791s`；300 秒仍为 `0.0/0.0/0.0`，并丢掉 current best 的 `cracked-star-jar` 300 秒 `0.3333` 胜率。相对 current best 有 `4` 个 blockers，相对 seed63100 baseline 仍有 `1` 个 strict blocker。记录 `fail_20260528_086`；下一步不能直接 splice，应把 current-failure best 作为硬 retention anchor，单独处理 late win-conversion 或 closed-loop constrained repair。

handoff splice late trace 进一步把失败面收窄到 late-window route recovery。复跑该 splice 的 `300s` high-pressure trace 得到 `9` 条失败局、`1686` 个 sampled rows，其中 negative `route_recovery` rows 为 `965`（`57.24%`），boundary-edge hotspots 为 `884`。`180-300s` late slice 导出 `207` 条有效 edge recovery samples，分布为 `soda-creek` `43`、`caramel-workshop` `61`、`cracked-star-jar` `103`；原始动作集中在 action `3` 和 `5`。这批样本只能作为下一轮低权重 repair input，不能作为 policy gate；若继续叠样本仍丢掉 `cracked-star-jar` 300 秒胜利，应转向 closed-loop constrained repair。

handoff splice late low-weight fallback probe 证实单纯低权重叠样本仍不能解除 long-run blocker。该 run 沿用 current-failure fallback best 的训练底座，只以 `0.2x` 路径权重混入上述 `207` 条 late route-recovery samples；训练集变为 `36633` 条，edge recovery samples 为 `2900`，final validation accuracy 为 `0.7659`。60 秒保持 `1.0/0.6667/1.0`，180 秒为 `0.6667/0.6667/0.6667`，但 300 秒三图仍为 `0.0/0.0/0.0`。相对 current-failure fallback best 有 `5` 个 blockers，并丢掉 `cracked-star-jar` 300 秒 `0.3333` 胜率；相对 seed63100 stage 02 baseline 仍有 `2` 个 blockers。记录 `fail_20260528_087`，结论是 handoff splice late samples 只能保留为诊断素材，下一步应转向 closed-loop constrained repair 或 per-map late objective，并把 current best 作为硬 retention anchor。

soda / caramel focused closed-loop anchor probe 说明现有离线 KL anchor 还不足以保护 handoff / mid retention。该 run 从 anchor-regularized smoke checkpoint 出发，只在 `soda-creek` 与 `caramel-workshop` 上做 `1024` timestep `late-route-recovery` 训练，并用 current-failure fallback best + stage 02 opening 作为 full `36426` 样本 anchor。训练内 final anchor validation mean KL 为 `0.340916`、argmax agreement 为 `0.6914`；全量 alignment 仍失败，overall mean KL `0.34314`，mid `60-180s` mean KL `0.431042`。opening wrapper 保护下，60 秒为 `1.0/0.6667/1.0`，但 180 秒回落到 `0.3333/0.6667/0.6667`，300 秒三图仍为 `0.0/0.0/0.0`，且 action `7` 重新主导失败局。记录 `fail_20260528_088`；下一步不应继续扩大 PPO timesteps，应先解决 mid-window anchor drift，或增加在线 hard no-regression guard。

为避免后续 RL repair probe 继续靠人工阅读分散报告判断是否能加长训练，`tools/validate_rl_repair_probe_gate.py` 已提供统一门禁：输入训练报告、anchor alignment、一个或多个 window regression 报告，以及可选 failure analysis，输出 `rl_repair_probe_gate_passed_for_limited_followup`、`rl_repair_probe_gate_failed` 或 `rl_repair_probe_gate_invalid`。该 gate 明确不是 acceptance；只要发现 anchor blockers、window regression blockers，或报告使用 `candidate` / `release` / `acceptance` 等过度措辞，就会拒绝。首个真实运行用于上述 soda / caramel closed-loop anchor probe，结果为 `rl_repair_probe_gate_failed`，记录 `16` 个 blockers 和 `1` 个 warning。

为把上述 gate 暴露的 `mid_60_to_180` drift 从聚合指标拆成可审查样本，`tools/export_anchor_drift_samples.py` 已提供离线样本导出入口。它会在同一批 behavior-clone / trajectory 数据上加载 SB3 candidate 与 behavior-clone anchor，逐条输出 anchor / candidate action 分布、argmax、KL、top actions、地图、seed 和时间桶；支持 `--time-bucket`、`--map-id`、`--min-kl`、`--only-disagreement`、`--top` 与 `--include-observation`。该工具只产出 repair diagnostics，不能替代 anchor alignment、window no-regression、repair-probe gate 或 RL acceptance。

soda / caramel closed-loop anchor probe 的首个真实导出检查 `36426` 条样本，在 `mid_60_to_180` 中筛出 `2888` 条 `KL >= 0.35` 且 argmax 不一致的样本，并导出 KL 最高的 `200` 条。Top 200 的 mean KL 为 `2.228259`、max KL 为 `3.513148`，全部为 argmax disagreement；其中 `cracked-star-jar` `128` 条、`soda-creek` `40` 条、`caramel-workshop` `32` 条，top examples 反复出现 anchor action `8` 与 candidate action `4` / `5` 的分歧。报告位于 `harness/reports/2026-05-28_rl_curriculum_stage02_soda_caramel_closed_loop_anchor_probe_001/mid_anchor_drift_samples.md`；下一步应把它作为 handoff / mid-window anchor objective 的定位材料，而不是继续增加 PPO timesteps。

`train_sb3.py` 的 anchor regularization 路径现在可以读取带 `observation` 的 `anchor_drift_sample` JSONL：普通 `train_behavior_clone.py` 数据入口默认仍会拒绝这类诊断样本，只有 `--anchor-dataset` 在 PPO anchor KL regularization 中会显式启用读取。使用方式是先用 `export_anchor_drift_samples.py --include-observation` 导出 top drift rows，再把该 JSONL 作为额外 `--anchor-dataset` 或单独 mid-window anchor dataset；训练报告会把它计入 `anchor_drift_sample_records` 和 `anchor_drift_diagnostic` sample source。本次已生成 `mid_anchor_drift_training_samples.jsonl`，包含 `200` 条带 observation 的 top drift rows，并用 loader 验证为 `observation_len = 145`、`action_count = 9`。该能力只是把高漂移样本纳入 KL 约束的工具入口，仍不能跳过 repair-probe gate 或 no-regression。

`tools/validate_anchor_regularization_input.py` 提供 anchor regularization 输入预检：它会调用真实 `prepare_anchor_regularization`，但不执行 PPO learn。首个真实 preflight 使用 `mid_anchor_drift_training_samples.jsonl`、current-failure fallback best 和 stage 02 opening anchor，确认 `200/200` 条样本保留在 `mid_60_to_180`，anchor target 与记录的 anchor action argmax agreement 为 `1.0`，并记录 map/time-bucket balance 权重。报告位于 `harness/reports/2026-05-28_rl_curriculum_stage02_soda_caramel_closed_loop_anchor_probe_001/mid_anchor_regularization_input_preflight.md`；它只是训练前输入门，不是 PPO 结果或放行证据。

`train_sb3.py` 现在支持 anchor validation guard：当使用 PPO anchor regularization 时，可设置 `--anchor-guard-max-validation-kl` 和 `--anchor-guard-min-argmax-agreement`。训练会在每个 PPO chunk 后的 KL repair epoch 记录 `validation_guard`，一旦离线 anchor validation 超过阈值就停止后续 chunk，并在训练报告中写入 `aborted_by_anchor_validation_guard` / `trained_anchor_validation_guard_failed_not_policy_gate`。该 guard 只阻止明显漂移的续训继续加长，仍不能替代 fixed-window no-regression、repair-probe gate 或 RL acceptance。

首个 mid-anchor guarded PPO smoke 从上一版 `ppo_anchor_regularized_smoke.zip` 出发，只使用 top `200` drift rows 作为 `mid_60_to_180` anchor dataset，并设置 `max_validation_kl = 0.25`、`min_argmax_agreement = 0.85`。该分支被 guard 拒绝：请求 `512` timesteps，实际在首个 `256` chunk 后停止，validation mean KL 为 `2.310775`、argmax agreement 为 `0.0`。已记录 `fail_20260528_089`；由于训练期 guard 已失败，没有继续跑 fixed-window no-regression。

`compare_sb3_to_behavior_clone_anchor.py` 现在提供显式 `--include-anchor-drift-samples`，可在训练前用带 observation 的 `anchor_drift_sample` JSONL 对 start model 做 anchor alignment 预检。默认仍拒绝这类诊断行，避免 drift diagnostics 被误当作普通 behavior-clone 轨迹。

首个 start-model drift-row alignment precheck 使用上一版 `ppo_anchor_regularized_smoke.zip`、current-failure fallback anchor 与 stage 02 opening wrapper，对 `200` 条 `mid_60_to_180` drift rows 做训练前对齐检查。该预检失败：overall mean KL 为 `2.26528`，argmax agreement 为 `0.0`，三张图分桶 mean KL 均超过 `0.25` 阈值。已记录 `fail_20260528_090`；下一步不应从这个 start model 直接用 top-200 drift rows 做更长 PPO，而应混入更宽 anchor 数据、降低 PPO 更新压力，或寻找更接近的起点。

已有 SB3 checkpoint 起点 sweep 也未找到合格替代。`phase_specific_anchor_smoke` 在这批 drift rows 上是最接近的现有起点，但 overall mean KL 仍为 `2.14298`、argmax agreement 仍为 `0.0`；`opening_aware_distilled`、`anchor_map_bucket_full_smoke`、`soda_caramel_closed_loop_anchor`、`anchor_regularized_smoke` 和 `stage02_late_180_to_300` 也全部失败。已记录 `fail_20260528_091`；下一步应增加更宽的 supervised SB3 re-alignment / distillation 或混合 full-anchor + drift rows，而不是只换一个旧 checkpoint 继续 PPO。

`distill_behavior_clone_to_sb3.py` 现在也提供显式 `--include-anchor-drift-samples`，可把带 observation 的 `anchor_drift_sample` 行用于 supervised SB3 re-alignment / distillation 初始化。默认仍拒绝 drift diagnostics，避免它们绕过普通轨迹语义；该能力只是修复初始化入口，后续仍必须重新跑 anchor alignment、high-pressure no-regression、repair-probe gate 和 RL acceptance。

`distill_behavior_clone_to_sb3.py` 也支持重复传入 `--sample-path-weight PATH=WEIGHT`，用于让 broad full-anchor 数据中的小型 repair slice（例如 top drift rows）在 supervised SB3 初始化里具备可审计权重。路径匹配语义与 behavior-clone 训练一致，报告会记录命中数量和权重分布；该能力仍只是初始化工具，不构成 policy gate。

`distill_behavior_clone_to_sb3.py` 的报告现在会输出 `validation_slices`，按 `sample_source` 和每个 `--sample-path-weight` 命中路径拆分 validation loss / argmax accuracy / entropy。下一轮调 drift 权重时，应同时观察 drift slice 与 full-anchor aggregate，避免局部修复被总 loss 掩盖或反过来破坏 broad anchor。

`distill_behavior_clone_to_sb3.py` 现在还提供 supervised distillation 的 action-distribution guard。报告会在 validation overall、`sample_source`、`--sample-path-weight` 命中路径以及 `map_id + time bucket` 分桶上记录预测 argmax 动作分布、dominant action ratio 和 normalized argmax entropy；传入 `--action-distribution-guard-max-dominant-ratio` / `--action-distribution-guard-min-normalized-entropy` 后，脚本会把过度动作集中的 checkpoint 标为 `sb3_distillation_action_distribution_guard_failed_not_policy_gate`。该 guard 只阻止继续推进明显动作塌缩的蒸馏产物，不能替代 60 / 180 / 300 秒 high-pressure、e30 + parent no-regression、failure analysis 或 repair-probe gate。

首个 full-anchor + top drift rows `40x` supervised SB3 re-alignment 已被 anchor alignment 拒绝。该 probe 把 top drift rows overall mean KL 从旧起点的 `2.26528` 降到 `0.200915`，但 argmax agreement 只有 `0.785`，且 `soda-creek` / `caramel-workshop` 分桶仍超阈值；full-anchor 对齐更差，overall mean KL 为 `0.434754`、argmax agreement 为 `0.6385`。已记录 `fail_20260528_092`，因此不得从该 checkpoint 继续 guarded PPO 或 fixed-window no-regression。

将同一 full-anchor + top drift rows `40x` supervised re-alignment 扩展到 `30` epochs 后，离线对齐明显改善：top drift rows overall mean KL 为 `0.017394`、argmax agreement 为 `0.985`，full-anchor overall mean KL 为 `0.105281`、argmax agreement 为 `0.8282`，两项 anchor alignment 均通过。但固定窗口 high-pressure 仍失败：60 秒 / 180 秒为 `0.3333/0.6667/0.6667` watch，300 秒三图胜率全为 `0.0`，gate 为 `multimap_comparison_recorded_needs_policy_repair`。已记录 `fail_20260528_093`；结论是 supervised re-alignment 能修离线 anchor underfit，但不能替代 300 秒 closed-loop long-run conversion repair，也不得进入 RL acceptance 或 policy candidate。

从 e30 checkpoint 做 `512` timestep `late-win-conversion` guarded closed-loop probe 后，训练期 anchor guard 与离线 full-anchor alignment 仍通过，60 秒 / 180 秒提升到 `0.6667/0.6667/1.0`，300 秒 `cracked-star-jar` 恢复到 `0.3333` 胜率；但 `soda-creek` 与 `caramel-workshop` 300 秒仍为 `0.0`，且相对 e30 的 no-regression 检查发现 `caramel-workshop` 180 秒 dominant action ratio 增加 `0.265`。已记录 `fail_20260529_001`，repair-probe gate 为 `rl_repair_probe_gate_failed`；下一步不能直接加长同配置，应先保护 `caramel-workshop` 180 秒动作分布并保留 300 秒三图门禁。

缩短到 `256` timestep、降低学习率并提高 mid-window anchor 权重后，e30 mid-anchor guarded probe 通过训练期 anchor guard、top drift rows / full-anchor alignment 和相对 e30 的 60 / 180 / 300 秒 no-regression；`caramel-workshop` 180 秒 dominant action ratio 只从 `0.2646` 增至 `0.2871`，repair-probe gate 为 `rl_repair_probe_gate_passed_for_limited_followup`。但 300 秒 high-pressure 三图胜率仍全部为 `0.0`，且上一轮 `cracked-star-jar` 300 秒 `0.3333` 的恢复信号消失。已记录 `fail_20260529_002`；该 checkpoint 只能作为有限后续探索起点，不能进入 RL acceptance 或 policy candidate。

用同一 mid-anchor checkpoint 在新 seed 窗口 `63200-63202` 复跑当前 high-pressure 固定窗口 smoke 后，结论仍是 repair。60 秒三图胜率为 `0.6667/1.0/1.0`，说明 `soda-creek` opening / short-window retention 仍不稳定；180 秒为 `0.3333/1.0/0.6667`，其中 `soda-creek` 低于规则 Bot watch 阈值；300 秒三图仍为 `0.0/0.0/0.0`，gate 为 `multimap_comparison_recorded_needs_policy_repair`。已记录 `fail_20260529_020`，报告位于 `harness/reports/2026-05-29_rl_current_high_pressure_smoke_001/summary.md`；这只是当前证据刷新，不能作为 RL acceptance、stage 03 或 policy candidate。

为避免下一轮 RL probe 继续把 60 / 180 / 300 秒窗口混成一句“继续修”，`tools/create_rl_fixed_window_action_plan.py` 已把当前 high-pressure 复查拆成固定窗口失败分析和三阶段行动计划。当前计划位于 `harness/reports/2026-05-30_rl_current_high_pressure_fixed_window_action_plan_001/summary.md`，结论为 `rl_fixed_window_action_plan_ready`：stage 01 先修 `soda-creek` opening retention，stage 02 修 `soda-creek` / `cracked-star-jar` handoff 与 mid-window retention，stage 03 再处理三张高压图的 late conversion。每个阶段都强制保留 60 / 180 / 300 秒 validation commands；该计划不训练模型、不批准 checkpoint，也不改变 RL acceptance blocked 状态。

首个 `stage_01_opening_lt_60` 按计划从 e30 mid-anchor guarded checkpoint 继续 `256` timestep 后，没有解除固定窗口 blocker：60 秒 `soda-creek` 仍有 seed `63402` 在约 `37.13s` opening 死亡，180 秒 `caramel-workshop` 仍为 watch，300 秒三图仍全为 `0.0` 胜率；同 seed parent no-regression 还因 `300s/cracked-star-jar` dominant action ratio 增加 `0.2034 > 0.2` 失败。已记录 `fail_20260530_001`，报告位于 `harness/reports/2026-05-30_rl_current_high_pressure_stage01_opening_probe_001/summary.md`；该 checkpoint 不得进入 stage 02、stage 03、RL 测试 Bot 或 acceptance。

随后用同一 parent 显式循环训练 seeds `63400-63402` 的 `stage01_seed_replay` probe 也失败：60 秒 `soda-creek` seed `63402` 仍在约 `37.27s` opening 死亡，180 秒 `soda-creek` 从 parent 的 `0.6667` 回落到 `0.3333`，平均存活下降 `11.4358s`，300 秒三图仍全为 `0.0`。已记录 `fail_20260530_002`，报告位于 `harness/reports/2026-05-30_rl_current_high_pressure_stage01_seed_replay_probe_001/summary.md`；下一步应先 trace seed `63402` 的 observation / action score 差异，而不是继续从该 checkpoint 进入 stage 02。

seed `63402` 的 trace 诊断已确认 seed replay candidate 与 parent 在目标 seed 上几乎没有行为差异：两者都在 60 秒 `soda-creek` 中于约 `37.3s` 死亡，采样 action mix 均为 action `5` `69.91%`、action `2` `18.58%`、action `4` `11.50%`，没有采样 action `3` 或 `7`。同窗口成功 seeds 平均 action `7` 为 `56.87%`、action `3` 为 `15.39%`；candidate seed `63402` 从 `11.3334s` 到死亡持续 action `5`，首次高压贴边帧在 `31.9999s`，`boundary_edge_risk = 1.0`、`enemy_pressure_risk = 0.671`、action `5` score 为 `0.7658`。报告位于 `harness/reports/2026-05-30_rl_stage01_seed63402_trace_diagnostic_001/summary.md`；下一轮 stage 01 修复应针对“贴边 + 敌压上升时的 action 5 锁定”与成功 seed 的 action `7` / `3` 逃逸触发，而不是继续单纯 replay seed。

首个 `opening-route-recovery` 小步 probe 从 e30 mid-anchor guarded parent 继续 `512` timestep，并显式训练 `soda-creek` seeds `63400-63402`。它把 60 秒 high-pressure 平均胜率恢复到 `0.7778`，180 秒平均胜率恢复到 `0.6667`，且 300 秒三图平均存活均高于 parent；但 300 秒胜率仍为 `0.0/0.0/0.0`，同 seed parent no-regression 仍失败：`180s/cracked-star-jar` 胜率下降 `0.3333`、平均存活下降 `31.0702s`，另有 `60s/soda-creek`、`60s/caramel-workshop` 和 `180s/soda-creek` 的平均存活微回归。已记录 `fail_20260530_003`，报告位于 `harness/reports/2026-05-30_rl_stage01_opening_route_recovery_probe_001/summary.md`；该 checkpoint 不得进入 stage 02。下一轮应保留 opening route recovery 信号，但加入 parent-preservation / online action-distribution guard，避免修开局时破坏 `cracked-star-jar` 180 秒 retention。

保守学习率 sweep 进一步证明该方向需要极小步长才能保护 parent：`5e-6` 只剩 `300s/cracked-star-jar` 平均存活 `-1.956s` blocker，`2e-6` 只剩 `caramel-workshop` 180 / 300 秒微存活 blockers，`1e-6` 曾把 `cracked-star-jar` 300 秒恢复到 `0.3333` 胜率但仍有 `300s/caramel-workshop` `-0.1444s` blocker。最终 `5e-7` 版本通过同 seed 60 / 180 / 300 秒 parent no-regression，60 秒 `caramel-workshop` 从 `0.6667` 提到 `1.0`，但 `soda-creek` 60 秒仍为 `0.6667`，300 秒三图仍全 `0.0`。已记录 `fail_20260530_004`，报告位于 `harness/reports/2026-05-30_rl_stage01_opening_route_recovery_lr5e7_probe_001/summary.md`；该 checkpoint 只能作为 parent-preserving 诊断起点，不得进入 stage 02。下一轮必须在 `5e-7` 设置上叠加 seed `63402` target objective 或 online action-distribution guard。

从该 mid-anchor parent 继续 `256` timestep 并把 `late_180_to_300` anchor 权重提高到 `1.5` 后，训练期 anchor guard 和离线 alignment 仍通过，相对原始 e30 baseline 的 no-regression 也通过；但相对 mid-anchor parent 的窗口回归失败：`soda-creek` 180 秒平均存活下降 `6.857s`，`caramel-workshop` 300 秒平均存活下降 `5.19s`，300 秒三图胜率仍全为 `0.0`。已记录 `fail_20260529_003`；下一轮必须把 parent-preservation 纳入硬门禁，不能只与旧 e30 baseline 比较。

`validate_rl_repair_probe_gate.py` 已支持 `--required-window-regression e30=...` / `parent=...` 的多基线硬门禁写法；后续从 limited-followup parent 继续的 RL probe 必须同时提供原始 baseline 和 parent-preservation regression report，任何 parent 回归都应阻止继续加长或推进。

用 required multibaseline gate 约束后，从 mid-anchor parent 重新做 opening/mid retention + late conversion 小步 probe：训练期 anchor guard、drift-row alignment 和 full-anchor alignment 均通过，且 `cracked-star-jar` 300 秒胜率恢复到 `0.6667`。但该 checkpoint 相对 e30 与 parent 都回归：`caramel-workshop` 180 秒 dominant action ratio 分别增加 `0.2638` / `0.2413`，`soda-creek` 300 秒平均存活分别下降 `24.3608s` / `27.2947s`，且相对 parent 的 `cracked-star-jar` 60 秒胜率下降 `0.3333`。已记录 `fail_20260529_004`；该结果证明 final-minute conversion 有信号，但必须走 per-map 或 split-policy 约束，不能用单一 shared PPO continuation 换取局部恢复。

首个 per-map late split diagnostic 已验证工具入口但拒绝当前组合。该 run 使用 mid-anchor parent 作为 base，只在 `cracked-star-jar` 的 `240s` 后切到 opening/mid retention + late branch；相对 e30 和 parent 的 required window regression 均通过，repair-probe gate 也只给出 limited-followup。但 300 秒 high-pressure 仍为 `0.0/0.0/0.0`，failure analysis 记录 9 个失败局，且 `cracked-star-jar` 两个 late failure 分别死在 `230.5203s` 和 `237.9885s`，早于 `240s` split 阈值。已记录 `fail_20260529_005`；结论是 split-policy 可以继续用于诊断，但当前 `240s` dispatch 只是保留 already-failing parent，不能作为 repair 或 acceptance 证据。

把同一 per-map split 提前到 `180s` 后仍未恢复 300 秒转换。该 run 继续通过 e30 / parent required window regression 和 limited-followup repair gate，但 300 秒仍为 `0.0/0.0/0.0`，`cracked-star-jar` 平均存活只从 `175.125s` 微增到 `175.2584s`，两个 late death 仍在 `230.5203s` 和 `238.3886s` 发生。已记录 `fail_20260529_006`；下一步不应继续只调 split 秒数，而应检查 parent-to-late handoff state distribution，或做训练期 per-map constrained repair。

handoff state distribution 诊断确认 split 失败不是因为 late branch 接不住陌生 parent 状态，而是当前 late branch 在 handoff 窗口几乎没有策略差异。该诊断复现 `cracked-star-jar` 180s split 的 3 个失败 trace，并在 `120s` 到 `240s` 的 `458` 个 observation 上同时计算 parent 与 late branch action score；overall base-to-late mean KL 只有 `0.000491`、argmax agreement 为 `0.9978`，post-split argmax agreement 为 `1.0`。已记录 `fail_20260529_007`；下一步应转向训练期 per-map constrained repair，或用 parent late-state trace 训练显式 action-separation / terminal-conversion 分支。

首个 `cracked-star-jar` 单图训练期 constrained repair 仍未把 300 秒窗口转成胜利。该 probe 从 mid-anchor parent 出发，只在 `cracked-star-jar` 上做 `late-win-conversion` 小步 PPO，请求 `128`、实际 `256` timestep，并把 opening / mid anchor 权重设为 `2.0`、late 权重降到 `0.25`。训练期 guard、full-anchor alignment（mean KL `0.105798`、argmax agreement `0.8286`）、drift-row alignment（mean KL `0.019888`、argmax agreement `0.965`）、e30 / parent required window regression 和 repair-probe gate 均通过或仅给 limited-followup；但 standalone `cracked-star-jar` 300 秒评估仍是 `0.0` 胜率、平均存活 `220.1403s`，split-policy 300 秒三图仍为 `0.0/0.0/0.0`，handoff state distribution 的 mean KL 也只有 `0.000541` 且 argmax agreement `1.0`。已记录 `fail_20260529_008`；下一步不能继续单图小步 continuation，应直接基于 parent late-state trace 训练 action-separation / terminal-conversion 分支，并继续保留 e30 + parent 多基线 no-regression。

对 mid-anchor parent 追加 evaluation-only `late_recovery_filter` wrapper 后，`soda-creek` 300 秒出现 `0.3333` 局部胜率，但 `caramel-workshop` 与 `cracked-star-jar` 仍为 `0.0`，总体 gate 仍是 `multimap_comparison_recorded_needs_policy_repair`，failure analysis 记录 `8` 个失败局。该 wrapper 导出 `439` 条 `risk_recovery_supervision_sample`，三图合并校验为 `risk_recovery_samples_valid`，风险原因主要为 `wallward_edge`、`toward_enemy_pressure` 和 `toward_hazard`，但有 `1` 条 target risk score 警告。已记录 `fail_20260529_009`；该结果证明 parent late-state 存在可提取修复信号，但手写 adapter 不是 policy acceptance 证据，下一步应把样本转成真实 action-separation / terminal-conversion 训练输入，并保留 clean subset / 低权重消融与多基线回归门禁。

parent late recovery 样本已先做 clean subset 预检：`439` 条中保留 `424` 条，剔除 `14` 条 target 仍有风险原因和 `1` 条 target risk score 更差的样本；clean subset 再次通过 `risk_recovery_samples_valid`。行为克隆 dry-run 确认这 `424` 条样本能以 `risk_recovery_sample_weight = 0.5`、`late` phase filter、`180-300s` time window 和 `top_k_scores` soft target 进入训练管线，`fallback_one_hot_count = 0`。但 dry-run 同时标记 map sample imbalance，且 `late_low_health` coverage 为 `0`；因此下一步训练必须混入 parent / e30 retention anchors，并用多基线 no-regression 审查，而不能只用 clean adapter rows 训练。

source-filtered risk recovery distillation sweep 已确认 learned branch 入口可用但当前权重扫描全部拒绝推进。`distill_behavior_clone_to_sb3.py` 可保留普通 retention / edge recovery rows 的 `teacher_probs` 目标，只对 clean parent late-state `risk_recovery_supervision` rows 使用 `top_k_scores` soft target 覆写；`risk` source filter 下 `w10` / `w7` / `w5` 都通过 drift 与 full-anchor alignment，其中 `w10` 让 `cracked-star-jar` 300 秒恢复到 `0.3333` 胜率，但 repair gate 因 e30 与 parent 多基线回归失败并记录 `14` 个 blockers。`w7` 和 `w5` 分别降到 `3` / `4` 个 blockers，但 300 秒三图都回到 `0.0/0.0/0.0`。已记录 `fail_20260529_010`；下一步不应继续提高全局 risk sample weight，而应按地图 / 阶段拆目标，显式保护 `soda-creek` opening / mid 和 `caramel-workshop` 180 秒，只把 clean risk rows 用在匹配失败地图与 late window 的 action-separation / terminal-conversion 训练输入上。

为支持上述 map / phase scoped objective，`distill_behavior_clone_to_sb3.py` 已新增 `--recovery-target-maps`、`--recovery-target-min-seconds` 和 `--recovery-target-max-seconds`，用于把 recovery target override 限定到指定地图和时间窗。首个 scope filter smoke 只在 `cracked-star-jar` 的 `180-300s` `risk_recovery_supervision` rows 上启用 `top_k_scores`：覆写 `210` 条 soft target，按地图保留 `214` 条其他 risk rows，按 source 保留 `2693` 条 edge recovery rows，`fallback_one_hot_count = 0`。该 smoke 只验证训练输入和报告字段，不是 policy gate；下一步仍需基于该作用域运行完整 distillation、anchor alignment、60 / 180 / 300 秒 high-pressure 和 e30 + parent no-regression。

`tools/filter_risk_recovery_samples.py` 也已支持 `--map-id`、`--min-seconds` 和 `--max-seconds`，可从 clean risk recovery rows 中导出真正的 map / phase scoped 子集。首个 cracked late scope 导出从 `424` 条 clean parent risk rows 中保留 `210` 条 `cracked-star-jar` `180-300s` 样本，按地图剔除 `214` 条 `soda-creek` / `caramel-workshop` 样本，并再次通过 `risk_recovery_samples_valid`；后续 scoped distillation 应使用该子集作为加权 repair input，避免非目标地图 risk rows 继续被全局权重放大。

首个完整 scoped risk distillation 已完成但仍被拒绝。该 run 只把 `cracked-star-jar` `180-300s` 的 `210` 条 clean risk rows 以 `10x` 权重加入，并继续用 `40x` mid-anchor drift rows 保护离线对齐；drift-row alignment mean KL 为 `0.020786`、argmax agreement `0.97`，full-anchor alignment mean KL 为 `0.125045`、argmax agreement `0.8121`，均通过阈值。但 300 秒 high-pressure 仍为 `0.0/0.0/0.0`，`cracked-star-jar` 平均存活虽升到 `224.5857s` 也没有转成胜利；required multibaseline gate 仍失败，vs e30 有 `2` 个 blockers，vs parent 有 `6` 个 blockers，主要集中在 `soda-creek` 60/180 秒保留和 `cracked-star-jar` dominant action ratio。已记录 `fail_20260529_011`；下一步不能继续简单提高 scoped risk weight，应进一步拆出 terminal-conversion branch 或更窄 late-state subset，并把 `soda-creek` opening / mid 与 parent preservation 作为硬门禁。

继续把 scoped subset 收窄到 `cracked-star-jar` `210-240s` 后，训练输入只保留 `121` 条 terminal-window risk rows，主要 risk reasons 为 `toward_enemy_pressure` `56`、`toward_hazard` `56`、`wallward_edge` `22`。该 run 的 drift-row alignment mean KL 为 `0.021656`、argmax agreement `0.975`，full-anchor alignment mean KL 降到 `0.113096`、argmax agreement `0.8204`；60 / 180 秒平均胜率均提升到 `0.7778`，且 e30 / parent required no-regression 各只剩 `60s/caramel-workshop` dominant action ratio 一个 blocker。但 300 秒三图仍为 `0.0/0.0/0.0`，repair gate 仍失败并记录 `2` 个 blockers。已记录 `fail_20260529_012`；该子集是目前较好的 scoped repair input，但不能作为继续加长或 acceptance 依据，下一步应加入 action-distribution guard、降低 scoped weight 或设计显式 terminal-conversion branch。

降低同一 terminal-window subset 的权重到 `7x` 并没有解除 blocker，反而让 `soda-creek` 保留明显回归。`w7` 的 drift-row alignment mean KL 为 `0.01972`、argmax agreement `0.98`，full-anchor mean KL 为 `0.10967`、argmax agreement `0.8222`，离线指标略优于 `w10`；但 180 秒 `soda-creek` 胜率回到 `0.3333`，300 秒 `soda-creek` 平均存活降到 `93.0391s`，repair gate blockers 从 `2` 增至 `6`，且 `60s/caramel-workshop` dominant action ratio 仍超阈值。已记录 `fail_20260529_013`；下一步不要继续做简单降权扫描，应先加 action-distribution guard 或拆出显式 terminal-conversion branch。

将 action-distribution guard 应用回 terminal-window `w10` 后，结论进一步收窄：全作用域 guard 会被 `anchor_drift_diagnostic` / 对应 sample path 的 `36` 条 validation rows 拦下，dominant action `8` ratio 为 `0.8889`、normalized argmax entropy 为 `0.1872`，但这是刻意集中的 top drift 修复切片，不是在线 `caramel-workshop` 60 秒 blocker。新增 `--action-distribution-guard-scope` 后，只检查 `overall,map_time_buckets` 的 guard 通过：`caramel-workshop::opening_lt_60` 离线 dominant action ratio 为 `0.3167`、normalized argmax entropy 为 `0.7524`。因此离线 map/time action-distribution guard 可作为蒸馏证据闸门，但不能替代 online fixed-window no-regression；下一步应转向显式 terminal-conversion branch，或补充 baseline/candidate online action-distribution delta 专门门禁。

`validate_policy_window_regression.py` 已补上 baseline/candidate online action-distribution delta 专门门禁：在 60 / 180 / 300 秒 fixed-window comparison 中读取每张图的完整 `policy.summary.action_distribution`，除原有 win rate、平均存活、dominant ratio 外，还可用单动作 ratio 增幅、完整分布 L1 delta 和 normalized entropy drop 阻断在线分布漂移。用 e30 checkpoint 对 terminal-window `w10` 复跑后，该门禁记录 `17` 个 blockers，其中 `60s/caramel-workshop` 同时触发 dominant ratio `+0.2268`、action `7` ratio `+0.2421`、L1 delta `0.7526` 和 entropy delta `-0.2752`。这确认当前 blocker 是在线策略分布漂移，不应再依赖离线 validation guard 或继续单参数降权。

`train_sb3.py` 现在提供显式 terminal-conversion branch 评估入口：`--terminal-conversion-model` / `--terminal-conversion-maps` / `--terminal-conversion-min-seconds` / `--terminal-conversion-max-seconds` 可把独立 terminal model 限定到目标地图和终局窗口，`--terminal-conversion-min-pressure` 与 `--terminal-conversion-min-low-health-risk` 可进一步要求 online diagnostics 命中压力或低血量风险后才切换。该 wrapper 是后续 terminal-conversion probe 的调度工具，不是 policy gate；任何真实 checkpoint 仍必须继续跑 full-anchor alignment、三窗 high-pressure、e30 + parent no-regression、online action-distribution delta、failure analysis 和 repair-probe gate。

真实 terminal-conversion branch probe 已完成并记录 `fail_20260529_014`。e30-base 版本只在 `cracked-star-jar 210-240s` 切到 terminal-window w10 model，能通过 e30 no-regression 和 online action-distribution delta，但 300 秒三图仍为 `0.0/0.0/0.0`，且相对 mid-anchor parent 有 `9` 个 preservation blockers。parent-base 版本保住了 60/180 秒 parent 表现，也通过相对 e30 的 no-regression，但 300 秒仍全为 `0.0`，并且 `cracked-star-jar 300s` 平均存活相对 parent 下降 `0.4779s`，repair gate 仍失败。结论是现有 terminal-window w10 model 缺少足够 terminal action separation / win conversion；后续不应继续只调 dispatch 秒数，而应重新训练真正的 terminal-conversion branch，或先导出成功终局状态并构造更明确的 pressure / low-health conversion target。

为给真正 terminal-conversion branch 提供正例目标，新增 `tools/filter_bot_trajectory_samples.py`，可从规则 Bot trajectory JSONL 中按终局结果、地图、Bot、时间窗、血量和动作过滤 movement sample，并保留 metadata / episode / summary 行。首个 smoke 从 `harness/reports/2026-05-27_rl_rule_bot_late_survival_trajectory_001` 的 8 个 JSONL 中筛出 `cracked-star-jar` 胜利局 `210-240s` 的 `358` 条样本，覆盖 `2` 个 KiteBot 胜利 episode；`train_behavior_clone.py --dry-run` 判定 `dataset_validated_not_training_gate`，observation_len 为 `145`，late_low_health ratio 为 `0.581`，但诊断标记同动作持续率 `0.7612` 为 watch。报告位于 `harness/reports/2026-05-29_terminal_conversion_victory_sample_filter_smoke_001/summary.md`。这只是 terminal-conversion 训练输入，不是 learned branch、fixed-window gate、repair-probe gate 或 RL acceptance 证据；后续必须混入 parent / e30 retention anchors 和 risk / drift repair rows，再重新跑 full-anchor alignment、60 / 180 / 300 秒 high-pressure、online action-distribution delta 与多基线 no-regression。

`distill_behavior_clone_to_sb3.py` 已新增 `--dataset-action-target-path`，用于在 `target-mode teacher_probs` 下仅对匹配路径样本使用 dataset action one-hot target，其余样本继续保持 teacher probabilities；报告会写入 `target.dataset_action_target_override` 的路径、命中样本数和平均非零动作数。首轮 terminal victory target 消融显示：全局 `target-mode dataset_actions` 会让 full-anchor mean KL 升到 `0.405769`、opening mean KL 升到 `1.676031`，不可接受；路径覆写 `w20` 和 `w10` 分别因 full-anchor argmax agreement `0.7781`、`0.7973` 失败；`w5` 则通过 drift alignment、full-anchor alignment 和 parent window regression，`dataset_action_target_override.overridden_sample_count = 358`，但 300 秒 high-pressure 三图仍为 `0.0/0.0/0.0`，且相对 e30 在 `300s/soda-creek` 触发 action `1` ratio `+0.2234` online blocker。已记录 `fail_20260529_015`，报告位于 `harness/reports/2026-05-29_rl_sb3_terminal_victory_path_target_w5_e30_001/summary.md`；该能力可以保留为训练工具，但当前 checkpoint 不能推进为 policy candidate、stage 03 或 RL acceptance。下一步应扩大成功终局样本到多图 / 更多 seed，或加入 pressure / low-health conversion target，而不是继续只扫单一权重或 dispatch 秒数。

多图 terminal victory target 已完成首轮扩展。复用同一过滤工具从 late-survival trajectory 源中抽取所有 high-pressure 地图的 victory episode，在 `210-240s` 保留 `1437` 条 movement samples、`8` 个 victory episode，覆盖 `soda-creek` `5` 局、`cracked-star-jar` `2` 局和 `caramel-workshop` `1` 局；behavior-clone dry-run 判定 `dataset_validated_not_training_gate`，observation_len 为 `145`，late_low_health ratio 为 `0.7543`。诊断仍标记 `high_action_persistence` 和 `map_sample_imbalance` 为 watch，尤其 `soda-creek` 样本占比 `0.6256`、`caramel-workshop` 只有 `1` 个 episode。报告位于 `harness/reports/2026-05-29_terminal_conversion_multimap_victory_samples_001/summary.md`。该数据集只是下一轮 terminal branch 训练输入，不是 model、fixed-window gate 或 acceptance 证据。

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

首个 `route_recovery` supervision sample 报告位于 `harness/reports/2026-05-27_rl_route_recovery_supervision_samples_001/summary.md`。该报告复跑 300 秒 high-pressure 三图 failed-only trace 并写入 observation，从 `735` 个负 `route_recovery` 采样点中导出 `689` 条贴边恢复样本，覆盖 `soda-creek`、`caramel-workshop` 和 `cracked-star-jar`；`tools/validate_edge_recovery_samples.py` 判定 `edge_recovery_samples_valid`，behavior clone dry-run 判定 `dataset_validated_not_training_gate`，health ratio 最低 `0.2867`。这些样本可以进入下一轮监督修复实验，但仍不是 policy checkpoint、不是 Replay，也不是 high-pressure gate 通过证据。

首个 `route_recovery` behavior clone smoke 已完成，报告位于 `harness/reports/2026-05-27_rl_route_recovery_behavior_clone_smoke_001/summary.md`。该 smoke 只用上述 `689` 条 repair 样本训练 1 epoch MLP，validation accuracy 为 `0.6522`、validation entropy 为 `2.193724` nats，并写出 checkpoint；结论仍是 `behavior_clone_smoke_only_not_policy_gate`。它只证明新样本可以进入监督训练路径，不能作为可玩 policy、stage 03 或 RL acceptance 证据。

首个 `route_recovery` auxiliary staged smoke 已完成，报告位于 `harness/reports/2026-05-27_rl_route_recovery_aux_staged_smoke_001/summary.md`。该 smoke 将 phase-aligned KiteBot 高压轨迹与 route_recovery repair 样本混合：opening 排除 repair 样本，mid 保留 `342` 条 `60-180s` 样本，late 经 phase filter 后保留 `40` 条 `180s+` 样本，并完成 GRU context8 三段训练与 staged checkpoint 打包。但 5 秒 `soda-creek` 加载 smoke 中 deterministic policy 151/151 帧选择 action `7`，已记录 `fail_20260527_039_route_recovery_aux_staged_smoke_action_collapse.json`；该 checkpoint 只能作为混合数据和打包链路证据，不能推进为策略候选。

`route_recovery` auxiliary entropy retry 已完成，报告位于 `harness/reports/2026-05-27_rl_route_recovery_aux_entropy_retry_001/summary.md`。该重试保留同一批 phase-aligned KiteBot 轨迹和 `689` 条 route_recovery repair 样本，将三段 GRU context8 子模型从 1 epoch 提到 5 epoch，并把 `entropy_regularization` 提到 `0.08`，同时保留 inverse-frequency class weighting、`danger_action_change` 和 `edge_recovery_sample_weight = 4.0`。离线 validation accuracy 提升到 opening `0.6030`、mid `0.6431`、late `0.5816`，但 5 秒 `soda-creek` 加载 smoke 中 deterministic policy 仍然 151/151 帧选择 action `3`，评估 gate 仍为 `evaluation_recorded_needs_action_bias_repair`，已记录 `fail_20260527_040_route_recovery_aux_entropy_retry_action_collapse.json`。结论：只提高 epoch 和 entropy 正则会把塌缩动作从 `7` 转成 `3`，仍不能作为策略候选；下一步应检查 target/action 分布、teacher soft targets、uniform target mix 或显式 policy constraint，而不是继续单纯堆训练轮数。

`python/train/diagnose_behavior_clone_policy.py` 已提供行为克隆离线预测分布诊断：读取 movement dataset 与 `.pt` / staged checkpoint，按 episode 顺序重放 observation、设置 map/time context，并输出 target action、predicted action、mean policy scores、按 phase/map/sample source 分组的分布和 action-bias finding。首份诊断已写入 `harness/reports/2026-05-27_rl_route_recovery_aux_entropy_retry_001/offline_policy_diagnostic.json`：完整混合数据 `22415` 条样本上 overall accuracy 为 `0.6180`，dominant predicted action 只有 `15.06%`，normalized predicted action entropy 为 `0.9434`，未触发 offline action-bias repair。这说明 entropy retry 的 5 秒在线 action `3` 塌缩不是全局离线 checkpoint 塌缩，下一步应更具体地检查 Gym 初始短窗状态分布、history padding、map/start context 或 online dispatch，而不是只看训练集整体动作分布。

staged behavior clone 的 absolute-time dispatch 已进一步补齐到子模型内部特征：当 checkpoint 配置 `phase_duration_seconds = 300` 时，`StagedBehaviorClonePolicy` 会把该 duration 传给子 `BehaviorClonePolicy`，子模型会用 `time_seconds / phase_duration_seconds` 覆盖输入中的进度特征和 `time_phase_conditioning`，避免 5 秒短窗把 observation progress 误读成完整 300 秒进度。修复报告位于 `harness/reports/2026-05-27_rl_route_recovery_aux_absolute_time_conditioning_fix_001/summary.md`，测试覆盖 `time_phase_conditioning = one_hot` 的绝对时间上下文。但复跑同一 5 秒 `soda-creek` smoke 后仍为 action `3` 151/151 帧，gate 仍是 `evaluation_recorded_needs_action_bias_repair`。结论：时间特征错配是需要修的真实问题，但不是这次 action collapse 的唯一根因；下一步应比较在线 5 秒 trace 与最近离线 opening 轨迹，检查 closed-loop GRU history / teacher target 缺口。

`python/train/compare_behavior_clone_trace_to_dataset.py` 已提供在线 trace 与离线 behavior clone 数据集的最近邻诊断。首份报告位于 `harness/reports/2026-05-27_rl_route_recovery_aux_absolute_time_conditioning_fix_001/trace_dataset_nearest_opening.json`：把同一 5 秒 `soda-creek` 在线 trace 按 `time_seconds / 300` 重新条件化后，只和同图 `0-60s` opening 样本比较，151 个在线样本中 nearest offline target 有 147 个也是 action `3`，nearest target 与 online action 匹配率为 `0.9735`。这说明该 5 秒 smoke 的 action `3` 低熵不主要来自全局离线 checkpoint 塌缩，也不明显违背最近 opening teacher target；它更像短 toy window 落在极窄开局动作邻域。该 checkpoint 仍不能作为策略候选，因为 5 秒熵为 0 且没有证明 60/180/300 秒恢复能力；下一步应拉长短窗或做 60 秒分段近邻诊断，检查 teacher 在何时从持续 action `3` 转向恢复动作，以及 GRU history 是否能跟上。

60 秒分段近邻诊断进一步定位到 transition / recovery 问题，而不是纯 5 秒动作塌缩。报告位于 `harness/reports/2026-05-27_rl_route_recovery_aux_60s_nearest_transition_001/summary.md`：同一 checkpoint 在 `soda-creek` seed `62300` 活到 60.0328 秒，但受到 `84.1101` 伤害，route_recovery reward 为 `-2.2598`，最终贴在右边界。stride-10 sampled trace 中，nearest teacher 在 `7.0s` 已第一次从 action `3` 切到 action `5`，online policy 直到 `22.6667s` 才首次从 action `3` 切出；`25-35s` 出现最大错位，online 几乎全为 action `5`，而 nearest teacher 主要偏 action `3` 或 `8`。下一轮不应继续只调 epoch / entropy，应聚焦 `20-35s` 和 `55-60s` 的 teacher 轨迹、GRU hidden history、恢复动作监督和 action-change 约束。

`python/train/inspect_behavior_clone_teacher_sequences.py` 可把上述近邻分布进一步展开成 teacher episode 前后动作序列。首份报告位于 `harness/reports/2026-05-27_rl_route_recovery_aux_teacher_sequence_windows_001/summary.md`：`25-30s` online 纯 action `5`，nearest KiteBot seed `48003` 多数仍是 action `3` 并夹少量 `1/4/5`；`30-35s` online 仍纯 action `5`，nearest route_recovery repair seed `62301/62302` 多数是 action `8`；`55-60s` online 纯 action `3`，nearest 同时间 KiteBot seed `48009` 在 `54.9995-57.3328s` 连续 action `2`。下一轮修复应把这些窗口转成 focused repair：提高 `30-35s` action `8` 恢复序列权重，补 `55-60s` 右边界 action `2` teacher snippets，并比较 GRU history 在 teacher-prefix / online-prefix 下的分歧。

`python/train/probe_behavior_clone_history_context.py` 已补充 GRU history context probe：对同一目标 observation 分别用 cold、online-prefix 和 nearest teacher-prefix 三种历史前缀读取 staged behavior clone action scores。首份报告位于 `harness/reports/2026-05-27_rl_route_recovery_aux_history_context_probe_001/summary.md`：`30-35s` 中 cold / online-prefix 全部 top action `5`，teacher-prefix 也有 `13/15` 个样本 top `5`；`55-60s` 中 cold / online-prefix 全部 top action `3`，但 teacher-prefix 的 top action 分布变为 action `2` 占 `0.6000`、action `3` 占 `0.2667`、action `4` 占 `0.1333`。结论：问题更像 online history 把策略稳定在继续向右的错误恢复上下文，而 teacher history 能把一部分样本推向恢复动作；该报告仍是 watch-only 诊断，不能替代 deterministic high-pressure gate 或 RL acceptance。

基于同一 60 秒 trace，已导出 focused boundary repair 样本，报告位于 `harness/reports/2026-05-27_rl_route_recovery_aux_focused_boundary_samples_001/summary.md`。导出器没有直接复制 nearest teacher action，而是只保留 `route_recovery < 0`、`boundary.edge_risk >= 0.75`、原始动作继续顶边、目标动作不再顶边的 sampled frame；共得到 `134` 条 `edge_recovery_supervision_sample`，原始动作 action `3` 有 `82` 条、action `5` 有 `52` 条，目标动作集中在 action `7/8/5/1`。`tools/validate_edge_recovery_samples.py` 判定 `edge_recovery_samples_valid`，behavior clone dry-run 判定 `dataset_validated_not_training_gate`。这批样本只是 focused repair training input，不能当作策略通过证据；后续训练后仍必须重新跑 high-pressure 多图对比和 RL acceptance。

首个 focused boundary opening retrain 报告位于 `harness/reports/2026-05-27_rl_route_recovery_aux_focused_boundary_opening_001/summary.md`。该 smoke 只重训 opening 子模型，mid / late 沿用 entropy retry；opening 训练集中只有 `17` 条 focused repair 样本进入 phase filter。5 秒 `soda-creek` seed `62300` 不再纯 action `3`，而是 action `3` 占 `0.6755`、action `5` 占 `0.3245`；但 60 秒同 seed 在 `42.3664s` 死亡，damage_taken `120.2898`，action `7` 占 `0.7828`，gate 为 `evaluation_recorded_needs_action_bias_repair`，已记录 `fail_20260527_041_route_recovery_aux_focused_boundary_opening_regression.json`。结论：focused 样本能打破 5 秒低熵，但样本覆盖太窄会把策略推向新的单向撤离偏置；下一轮必须先扩展多 seed / 多图 `20-60s` 边界恢复覆盖并检查 target action balance，不能只放大这 134 条样本权重。

多图多 seed boundary trace 扩展已完成，报告位于 `harness/reports/2026-05-27_rl_route_recovery_aux_multimap_boundary_samples_001/summary.md`。使用 entropy retry staged checkpoint 在 high-pressure 三图各跑 seed `62400-62404` 的 60 秒 deterministic trace：`soda-creek` win_rate `0.4`，`cracked-star-jar` win_rate `0.6`，`caramel-workshop` 虽为 `1.0` 但平均 damage_taken `62.8534` 且 route_recovery 仍为负。从 15 条 trace 导出 `1676` 条有效 `edge_recovery_supervision_sample`，覆盖三图，target action 分布为 action `5/7/3/4/8/1/6`，比单 seed focused 样本更宽。该批次仍只是 repair training input；下一步训练必须显式控制窗口和 target balance，并先跑 60 秒三图 gate。

基于多图 boundary samples 的 controlled opening retrain 报告位于 `harness/reports/2026-05-27_rl_route_recovery_aux_multimap_boundary_opening_001/summary.md`。本轮只重训 opening 子模型，`0-60s` opening 训练集中有 `5617` 条样本，其中 `229` 条为 edge recovery repair input；使用 `inverse_frequency`、`edge_recovery_sample_weight = 2.0` 和 `entropy_regularization = 0.01` 后，60 秒 high-pressure 三图 gate 仍为 `multimap_comparison_recorded_needs_policy_repair`。策略没有回到上一轮 action `3/7`，但转成新的 action `6` dominant bias：`soda-creek` action `6` 占 `0.7726` 且 win_rate `0.4`，`caramel-workshop` action `6` 占 `0.7349`，`cracked-star-jar` action `6` 占 `0.7227`。已记录 `fail_20260527_042_route_recovery_aux_multimap_boundary_opening_action6_bias.json`；下一步必须先做 class weighting / repair weight 消融，不能进入 stage 03、180/300 秒长窗或 RL acceptance。

class weighting / repair weight 消融报告位于 `harness/reports/2026-05-27_rl_route_recovery_aux_multimap_boundary_opening_ablation_001/summary.md`。移除 `inverse_frequency` 后，action `6` 过补偿明显缓解：`no_class_weight_2_0` 在 `soda-creek` 的 action `6` 占比降到 `0.4355`，`cracked-star-jar` 降到 `0.3797`，但 `soda-creek` win_rate 仍只有 `0.4`，`caramel-workshop` action `6` 仍接近阈值 `0.6985`。`weight=1.0` 进一步降低 caramel action `6`，但 cracked win_rate 回落到 `0.4`。结论：`inverse_frequency` 是 action `6` bias 的主要诱因之一，后续应默认取消 class weighting；但单纯调 edge recovery 权重不能修复路线恢复，还需要诊断 online-prefix 历史、teacher soft target 或多动作分布目标。

`no_class_weight_2_0` 的 history probe 报告位于 `harness/reports/2026-05-27_rl_route_recovery_aux_multimap_boundary_history_probe_001/summary.md`。离线全数据预测没有 action collapse，dominant predicted action `3` 仅占 `0.1732`，normalized predicted entropy 为 `0.9336`；但在线 `soda-creek` seed `62403` trace 的 nearest offline target 与在线动作匹配率 `0.9225`，且 `20-40s` / `40-50s` 最近邻目标也几乎都是 action `6`。cold、online-prefix、teacher-prefix 在中后段都选择 action `6`，说明剩余问题不是单纯 GRU history 锁死，而是策略进入了离线数据中本身以 action `6` 为 target、但无法有效 route recovery 的状态邻域。下一步应从失败在线 trace 导出 `20-47s` 的 route-risk repair samples，或改用 soft target / top-k target，不应继续只调权重。

在线 route-risk repair samples 已导出，报告位于 `harness/reports/2026-05-27_rl_route_recovery_aux_online_route_risk_samples_001/summary.md`。该批次从 `no_class_weight_2_0` 的 `soda-creek` 失败 seed `62400/62402/62403` 中截取 `20-47s`，得到 `143` 条有效 edge recovery repair samples；原始动作主要是 action `6`、`5`、`1`，目标动作则高度偏向 action `2`，占 `0.7133`。这说明它精准覆盖了 action `6` 邻域，但不能高权重直接混入，否则可能把偏置转成 action `2`。下一轮训练只能低权重/消融使用，并继续以 60 秒三图 deterministic gate 验证。

phase-aligned 在线 route-risk 样本报告位于 `harness/reports/2026-05-27_rl_route_recovery_aux_online_route_risk_phase_aligned_samples_001/summary.md`。由于这些样本来自 60 秒 eval trace，raw observation 的 normalized progress 会让 `20-47s` 样本被 opening filter 排除；导出工具现支持 `--phase-duration-seconds 300`，将 progress 重写为 `time_seconds / 300`。重导后 `143` 条在线样本能全部进入 opening 混合 dry-run；混合训练集为 `5760` 条，edge recovery samples 为 `372` 条，整体 action `2` ratio 为 `0.1052`。该批次可用于低权重训练消融，但仍不是 policy gate。

在线 route-risk opening 低权重消融报告位于 `harness/reports/2026-05-27_rl_route_recovery_aux_online_route_risk_opening_ablation_001/summary.md`。该轮保留 `class_weighting = none`，将 phase-aligned 在线样本以默认权重混入 opening 训练；60 秒 high-pressure 三图结果为 `soda-creek` `0.4`、`caramel-workshop` `0.8`、`cracked-star-jar` `0.8`。它压低了上一轮 action `6` 过补偿，但 deterministic policy 转为 action `3` dominant：三图 action `3` ratio 分别为 `0.5911`、`0.5227`、`0.4837`，且 `soda-creek` 平均存活降到 `40.8197s`。该结果记录为 `fail_20260527_043`，下一步不应继续堆单标签 route-risk 样本，而应转向 soft/top-k target 或 per-state action constraint。

`train_behavior_clone.py` 现支持 `--recovery-soft-target top_k_scores`，用于让 `edge_recovery_supervision_sample` / `risk_recovery_supervision_sample` 表达 soft/top-k repair target，而不是单一硬标签。工具报告位于 `harness/reports/2026-05-27_rl_recovery_soft_target_training_support_001/summary.md`；当前 opening 混合数据 dry-run 覆盖 `372/372` 条 recovery samples，`fallback_one_hot_count = 0`。该能力只解决训练表达问题，下一步仍必须训练 soft target opening 消融并跑 60 秒三图 deterministic gate。

soft/top-k recovery target opening 消融报告位于 `harness/reports/2026-05-27_rl_recovery_soft_target_opening_ablation_001/summary.md`。`soft_topk_0_6` 将 `soda-creek` 60 秒 win rate 从硬标签 route-risk ablation 的 `0.4` 提升到 `0.6`，平均存活提升到 `49.0996s`；但 `caramel-workshop` action `3` ratio 达到 `0.7582`，整体 gate 为 `multimap_comparison_recorded_needs_policy_repair`。该结果记录为 `fail_20260527_044`，仍不能进入 180/300 秒评估；下一步应尝试 per-map action diversity constraint、动作分布正则或更宽的 safe-action teacher target。

soft/top-k + `entropy_regularization = 0.05` 消融报告位于 `harness/reports/2026-05-27_rl_recovery_soft_target_entropy_opening_ablation_001/summary.md`。更高熵正则让 offline validation entropy 升到 `1.464027`，但 deterministic 60 秒三图仍由 action `3` dominant，且 `soda-creek` win rate 从 `0.6` 回退到 `0.4`。该结果记录为 `fail_20260527_045`，说明单独提高 per-sample entropy regularization 太间接；下一步应实现显式 action-distribution regularization、per-map action diversity constraint 或更宽的 safe-action teacher target。

`train_behavior_clone.py` 现支持 `--action-distribution-regularization` 与 `--action-distribution-target`，可用 global 或 per-map target 约束 batch 平均预测动作分布。动作分布正则 opening 消融报告位于 `harness/reports/2026-05-27_rl_action_distribution_regularization_opening_ablation_001/summary.md`。`per_map_uniform_0_2` 在 60 秒 high-pressure 三图中消除了 compare 内部 action-bias repair，`caramel-workshop` action `3` ratio 从 `0.7561` 降到 `0.6562`；但 180 秒探针中 `soda-creek` win rate 仍为 `0.0`，整体 gate 为 `multimap_comparison_recorded_needs_policy_repair`。该结果记录为 `fail_20260527_046`，说明动作分布正则能缓解短窗 argmax 偏置，但不能替代状态条件化路线恢复、升级后目标或闭环 PPO/curriculum。

基于 `per_map_uniform_0_2` 的 `soda-creek` 180 秒失败 trace，已导出 `50-80s` 中窗 route recovery repair samples，报告位于 `harness/reports/2026-05-27_rl_action_distribution_regularization_soda_midwindow_samples_001/summary.md`。本轮得到 `51` 条有效样本，全部来自 seed `62404`，原动作分布为 action `1/6`，目标动作为 action `5/2`；validator 判定 `edge_recovery_samples_valid`。由于 staged policy 以 `300s` 分段，`50-60s` 样本进入 opening dry-run，`60-80s` 的 `24` 条样本进入 mid dry-run。下一轮训练必须按 phase 拆开处理，不能只重训 opening。

phase-split retrain 报告位于 `harness/reports/2026-05-27_rl_action_distribution_phase_split_retrain_001/summary.md`。同时重训 opening/mid 的 `phase_split_soda_mid` 可把 180 秒 `soda-creek` win rate 从 `0.0` 拉到 `0.4`，但 60 秒 `caramel-workshop` 和 `cracked-star-jar` 重新触发 action `3` bias repair，且 180 秒 `cracked-star-jar` 降到 `0.2`；只重训 mid 的两档保住了 60 秒短窗，却仍让 180 秒 `soda-creek` 停在 `0.0`。该结果记录为 `fail_20260527_047`，说明单 seed `50-80s` 样本不足，下一步应先扩展多 seed `45-100s` midwindow repair coverage。

多 seed `45-100s` midwindow repair coverage 已扩展，报告位于 `harness/reports/2026-05-27_rl_action_distribution_multiseed_midwindow_samples_001/summary.md`。使用 `per_map_uniform_0_2` 在 `soda-creek` 跑 `62400-62419` 共 20 个 seed 的 180 秒失败 trace 后，导出 `389` 条有效 route recovery repair samples，覆盖 seed `62404`、`62406`、`62410`、`62414`；其中 `60-100s` mid dry-run 可用 `281` 条 soft recovery samples，明显高于上一轮单 seed 的 `24` 条。该批样本仍只是 repair training input；下一步应优先做 mid-only staged 消融，保留旧 opening 子模型，避免重演 opening 重训导致的多图短窗 action-bias 回归。

多 seed mid-only staged 消融报告位于 `harness/reports/2026-05-27_rl_action_distribution_multiseed_midonly_ablation_001/summary.md`。`mid_only_multiseed_w1` 与 `mid_only_multiseed_w4` 都保住了 60 秒三图短窗，但 180 秒 `soda-creek` 仍为 `0.0` win rate；`w4` 只把平均存活小幅抬到 `61.6816s`，同时 `cracked-star-jar` 180 秒回落到 `0.4`。该结果记录为 `fail_20260527_048`，说明边界顶墙样本扩量仍不足以解决中长窗策略缺口；下一步应补充非贴边危险状态、45 秒前早死诊断或 per-map/per-phase target，而不是继续提高 recovery weight。

`soda-creek` 20 seed 失败分布诊断报告位于 `harness/reports/2026-05-27_rl_action_distribution_soda_failure_distribution_001/summary.md`。18 局失败中有 `14` 局在 60 秒前死亡，opening failure ratio 为 `77.78%`；sampled route recovery hotspots 也以 opening action `3` 贴边为主，`opening_lt_60` 有 `1473` 条负 route_recovery 热点，其中 action `3` 占 `1270` 条。结论：midwindow 样本有效但不是最大 blocker；下一轮应针对 `20-45s` 多 seed opening edge-risk/action `3` 做低权重受控消融，并保留严格 60 秒三图 hard gate。

基于上述诊断，`tools/export_route_recovery_samples.py` 已支持 `--original-actions`，可按原始 policy action 精确导出 repair samples。首个 `20-45s` opening action `3` 样本包位于 `harness/reports/2026-05-27_rl_action_distribution_opening_action3_samples_001/summary.md`：导出 `587` 条有效样本，覆盖 18 个失败 seed，目标动作分布为 action `5/7/8/1`。混合 opening dry-run 后 soft recovery samples 为 `724` 条，但 `soda-creek` 样本占比升到 `40.85%`；后续训练必须低权重、保留 per-map 动作分布正则，并先通过 60 秒三图 hard gate。

低权重 opening action `3` 消融报告位于 `harness/reports/2026-05-27_rl_action_distribution_opening_action3_low_weight_ablation_001/summary.md`。`opening_action3_w0_5_windowed` 使用 `edge_recovery_sample_weight=0.5`、`20-45s` repair window 和 `per_map_uniform_present` 正则，保住 60 秒 hard gate，并把 `soda-creek` 180 秒 win rate 从 `0.0` 提升到 `0.6`；但 300 秒 high-pressure 三图仍全为 `0.0`，记录 `fail_20260527_049`。结论：opening 早死可修，但中后期仍缺 late survival、Boss/hazard pressure、升级后目标选择和长期路线规划，不能推进 stage 03 或 RL acceptance。

基于该 checkpoint 的 300 秒 failed-only trace 诊断位于 `harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_trace_001/summary.md`。15 条失败里 12 条死在 `late_180_to_300`，所有 terminal frames 都贴边且低血量，`boundary_edge` route recovery hotspots 为 `6839` 条；late bucket 的负 route recovery 主要来自 action `1`。下一步应导出 late risk-recovery samples 或做闭环 late survival curriculum，保留当前 opening 子模型，只替换 late 子模型或训练中后期目标策略。

当前 checkpoint 对应的 late recovery 样本批次位于 `harness/reports/2026-05-27_rl_action_distribution_opening_action3_late_recovery_samples_001/summary.md`。`--late-recovery-filter` 导出 `780` 条 `risk_recovery_supervision_sample`，全部位于 `180-300s` late 窗口；adapter 仅把 `soda-creek` / `cracked-star-jar` 300 秒 win rate 拉到 `0.2`，`caramel-workshop` 仍为 `0.0`。该批样本只能用于 late-only 受控消融，不能视作 policy repair 完成。

late-only risk recovery 消融报告位于 `harness/reports/2026-05-27_rl_action_distribution_opening_action3_lateonly_ablation_001/summary.md`。`late_risk_current_w4` 保留当前 opening 和原 mid，只替换 late 子模型，60 秒与 180 秒 regression 均保住；但 300 秒 `soda-creek` / `caramel-workshop` 仍为 `0.0`，`cracked-star-jar` 只到 `0.2`，记录 `fail_20260527_050`。结论：离线 late risk samples 可以小幅提高 entropy 和单图胜率，但仍不能替代 closed-loop late survival / curriculum、升级后目标选择或长期路线规划。

`late-route-recovery` closed-loop reward profile smoke 位于 `harness/reports/2026-05-27_rl_late_route_recovery_reward_profile_smoke_001/summary.md`。该 profile 从 120 秒后放大路线恢复、低血量、危险区、Boss 压力和轻量重复动作惩罚；2048 timestep continuation 保住了 60 秒三图无 repair，并把 180 秒 `caramel-workshop` 拉到 `0.6667`，但 180 秒 `cracked-star-jar` 为 `0.0`，300 秒三图仍全部 `0.0`，记录 `fail_20260527_051`。300 秒 trace 中 `841/1100` 条采样行为负 route recovery，主要是 boundary_edge 下继续 action `4`，说明下一步应针对 mid/late 贴边 action `4` 做 action-specific repair 或更明确的 boundary escape curriculum，而不是只继续加权。

mid/late action `4` 样本包位于 `harness/reports/2026-05-27_rl_late_route_action4_samples_001/summary.md`。本轮用 `late-route-recovery` checkpoint 重新跑三图 300 秒 failed-only evaluation traces，并启用 observation 输出；从 `60-300s` action `4` 贴边负 route-recovery 热点导出 `254` 条 `edge_recovery_supervision_sample`，覆盖三图，目标动作以 action `8` / `3` 为主。`tools/validate_edge_recovery_samples.py` 判定有效，behavior clone dry-run 判定 `dataset_validated_not_training_gate`。该样本包只适合小权重 mid/late 消融，不能当作策略通过证据。

action `4` mid/late 低权重消融报告位于 `harness/reports/2026-05-27_rl_late_route_action4_midlate_ablation_001/summary.md`。该轮保留 `opening_action3_w0_5_windowed` opening 子模型，只重训 mid 与 late，使用 `edge_recovery_sample_weight=0.5`、soft/top-k recovery target、`per_map_uniform_present` 动作分布正则，并取消 `inverse_frequency` class weighting。结果保住 60 秒短窗，但 180 秒 `soda-creek` 从上一轮 late-only 的 `0.6` 回落到 `0.4`，300 秒三图全部 `0.0`，记录 `fail_20260527_052`。结论：小权重 action4 supervision 没有形成长局路线恢复能力，且 late phase 只有 `48` 条 action4 样本；下一步应扩展 180-300 秒 late boundary escape 覆盖或转向 closed-loop late survival / boundary escape curriculum，而不是继续单纯提高该样本权重。

基于 `action4_w0_5` 失败面，late boundary recovery 样本包位于 `harness/reports/2026-05-27_rl_late_route_action4_midlate_late_boundary_samples_001/summary.md`。该报告复跑 300 秒 high-pressure 三图 5 seed failed-only observation traces，从 `180-300s` 贴边负 route-recovery 行导出 `1001` 条 late `edge_recovery_supervision_sample`，覆盖 `caramel-workshop` `441` 条、`cracked-star-jar` `370` 条、`soda-creek` `190` 条；原始动作覆盖 action `3/5/7/4/8/6/2`，不再局限于 action `4`。validator 判定有效，behavior clone dry-run 判定 `dataset_validated_not_training_gate` 且 late phase 占 `100%`。该批样本仍只是 repair training input；后续训练应先做 late-only 小权重或 closed-loop boundary escape curriculum，并继续保留 60/180/300 秒三图门禁。

`train_sb3.py --evaluate-model` 的单模型评估报告现在会直接写入 `findings` 与 `gate_decision`，复用已有 `policy_quality_findings` 识别 dominant action、低动作熵和 terminal reward dominance。该字段只用于把 evaluation smoke 中的 action collapse 标成 `evaluation_recorded_needs_action_bias_repair` 或 watch，不是 RL acceptance；正式候选仍必须走 high-pressure comparison 和 `validate_rl_policy_acceptance.py`。

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

`train_behavior_clone.py` 进一步支持 `--sample-path-weight PATH=WEIGHT`，可对特定 JSONL 文件或目录前缀的样本施加额外乘法权重，并在 `sample_weights.sample_path_weights` 中记录匹配数量。该能力用于把 map-specific repair samples、clean survival anchors 或 cracked retention anchors 拆开调权，避免所有 repair rows 共用一个 `edge_recovery_sample_weight`。它只改变监督采样概率，不改变样本内容；任何使用该能力得到的 checkpoint 仍必须重新跑 60/180/300 秒 deterministic high-pressure 对比、同 seed no-regression 和 failure case 审查。

首个路径级调权 fallback probe 使用该能力保持全局 `edge_recovery_sample_weight = 0.25`，同时把 `cracked-star-jar` 两包 late-survival anchors 提到 `1.4x`，并把 `caramel-workshop` opening / late map-specific repair samples 降到 `0.75x`。训练报告位于 `harness/reports/2026-05-28_rl_curriculum_stage02_path_weighted_fallback_probe_001/summary.md`：该策略保住 `cracked-star-jar` 300 秒胜率 `0.3333`，但同 seed no-regression 仍失败，blockers 为 `cracked-star-jar 180s` 平均存活回退 `9.1443s`、`soda-creek 300s` 平均存活回退 `2.2886s`；`soda-creek` / `caramel-workshop` 300 秒胜率仍为 `0.0`。该结果记录为 `fail_20260528_076`，说明路径级调权是诊断工具，不是 acceptance 证据；下一步应继续拆 map/time-window 约束或回到 closed-loop constraint repair。

对该 path-weighted fallback 复跑 300 秒 failed-only trace 后，当前失败面样本进一步收窄。报告位于 `harness/reports/2026-05-28_rl_curriculum_stage02_path_weighted_trace_001/summary.md`：8 条失败 trace、2359 个 sampled rows 中有 1724 个 negative route_recovery rows，占 `73.08%`；按 map/time-window 导出 `soda-creek 60-180s` 227 条、`soda-creek 180-300s` 50 条、`cracked-star-jar 60-180s` 202 条、`caramel-workshop <60s` 202 条、`caramel-workshop 180-300s` 144 条修复样本，均通过 `edge_recovery_samples_valid`。合并 dry-run 读取 825 条 `edge_recovery_supervision` 并生成 top-k soft targets；这些仍只是下一轮 repair training input，不是 Replay、policy gate 或 acceptance evidence。

使用上述 825 条 current-failure samples 训练的新 fallback 分支报告位于 `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_fallback_probe_001/summary.md`。该实验回到 late-retention 数据底座，保持全局 `edge_recovery_sample_weight = 0.25`，把 `cracked-star-jar` late-survival anchors 降到 `1.2x`，并对 `caramel-workshop` opening / late repair samples 使用 `0.75x`。结果相对 seed 63100 stage 02 baseline 的 60/180/300 秒同 seed no-regression 全部通过，300 秒平均存活分别提高 `soda-creek +39.0285s`、`caramel-workshop +7.735s`、`cracked-star-jar +20.1075s`，但 `soda-creek` 和 `caramel-workshop` 300 秒胜率仍为 `0.0`，总失败仍有 8 局。记录 `fail_20260528_077`，结论是 current-failure supervision 可作为当前最佳诊断分支，但仍不能推进 stage 03、`rl_test_bot_candidate` 或 acceptance。

对 current-failure fallback 分支再次复跑 300 秒 failed-only trace 后，报告位于 `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_trace_001/summary.md`：8 条失败 trace、1369 个 sampled rows 中有 926 个 negative route_recovery rows，占 `67.64%`，主压力仍为 `boundary_edge`。本轮按 map/time-window 导出 `soda-creek <60s` 104 条、`soda-creek 60-180s` 163 条、`soda-creek 180-300s` 50 条、`caramel-workshop <60s` 102 条、`caramel-workshop 60-180s` 163 条、`caramel-workshop 180-300s` 45 条、`cracked-star-jar 60-180s` 116 条、`cracked-star-jar 180-300s` 29 条 repair samples，合计 772 条并全部通过 `edge_recovery_samples_valid`。合并 dry-run 可读取全部样本并生成 top-k soft targets；这些仍只是更窄的 repair input，不是 Replay、policy gate 或 acceptance evidence。

使用这 772 条 current-failure trace samples 替换上一轮 825 条 path-weighted trace samples 后，新 fallback 探针记录于 `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_trace_fallback_probe_001/summary.md`。该 checkpoint 对 seed 63100 stage 02 baseline 的 60/180/300 秒同 seed no-regression 通过，但相对上一版 current-failure fallback best 回归：300 秒 `cracked-star-jar` 胜率从 `0.3333` 降到 `0.0`，`soda-creek` / `caramel-workshop` / `cracked-star-jar` 300 秒平均存活分别下降 `18.2827s` / `7.246s` / `7.3324s`，三图 300 秒胜率全部为 `0.0`。记录 `fail_20260528_078`，结论是更窄样本可用于后续增量 repair，但不能 wholesale 替换上一版 best，也不能推进 stage 03 或 acceptance。

保留上一版 path-weighted trace 数据底座、再以 `0.5x` 目录权重增量混入这 772 条 current-failure trace samples 后，增量探针记录于 `harness/reports/2026-05-28_rl_curriculum_stage02_current_failure_trace_incremental_probe_001/summary.md`。该 checkpoint 60 秒为 `1.0/0.6667/1.0`，180 秒为 `0.6667/0.6667/1.0`，但 300 秒仍为 `0.3333/0.0/0.0`，gate 仍是 `multimap_comparison_recorded_needs_policy_repair`。相对 seed 63100 baseline，`caramel-workshop` 300 秒平均存活回退 `0.4445s` 触发 strict no-regression blocker；相对 previous best，`caramel-workshop` 平均存活回退且 `cracked-star-jar` 300 秒胜率从 `0.3333` 掉到 `0.0`。记录 `fail_20260528_079`，结论是 current-failure trace samples 即使增量混入也不能解除 long-run blocker；后续应回到上一版 best 作为 retention anchor，并转向 closed-loop constrained repair 或 per-map late win-conversion objective。

为避免 repair 样本污染 opening 子模型，行为克隆入口还提供 `--edge-recovery-min-seconds` 和 `--edge-recovery-max-seconds`。这两个参数只过滤 `edge_recovery_supervision_sample`，不会移除正常规则 Bot 轨迹样本；因此 staged clone 可以在训练 opening 子模型时排除 handoff repair 样本，在训练 mid / handoff 子模型时再显式引入 60 秒后的 edge recovery 约束。首个 handoff-only dataset smoke 位于 `harness/reports/2026-05-27_rl_edge_recovery_handoff_only_dataset_smoke_001/summary.md`：opening dry-run 保留 5388 条规则轨迹且 edge repair 样本为 0，mid dry-run 保留 10710 条样本，其中 799 条为 60 秒后的 edge recovery repair 样本。该报告只证明数据切分入口可用，不代表训练策略或 RL gate 通过。

首个 `edge_recovery_sample_weight = 4.0` 的 staged GRU context8 混合候选使用 phase-aligned 三图 KiteBot 轨迹与 `2215` 条 edge recovery 样本训练三段子策略，但没有通过 60 秒 opening hard gate：`soda-creek` 10 seed 胜率只有 `40%`，action `3` 占 `87.27%`，action entropy 为 `0.7851` bits。报告位于 `harness/reports/2026-05-27_rl_behavior_clone_edge_recovery_aux_staged_gru_context8_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_028_edge_recovery_aux_opening_regression.json`。因此未运行 180 秒 handoff 对比，也不能进入 stage 03；下一轮必须先修 opening action `3` collapse。

加入 `inverse_frequency` class weighting 与 `entropy_regularization = 0.02` 后，动作分布明显改善但仍未通过 opening hard gate：`soda-creek` 60 秒 10 seed 胜率为 `50%`，action `3` 占比降到 `66.58%`，action entropy 提高到 `1.6725` bits；`caramel-workshop` 与 `cracked-star-jar` 均为 `90%`。报告位于 `harness/reports/2026-05-27_rl_behavior_clone_edge_aux_entropy_class_staged_gru_context8_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_029_edge_aux_entropy_class_opening_gap.json`。结论：class / entropy 可以缓解 action collapse，但不能替代 opening retention 或 handoff-only 约束。

在 `opening_action3_w0_5_windowed` 修复 60 秒短窗后，后续 late-window 实验继续暴露 300 秒长局缺口。780 条 `risk_recovery_supervision_sample` 的 late-only 消融保住 60/180 秒 regression，但 300 秒只把 `cracked-star-jar` 提到 `0.2`，`soda-creek` 与 `caramel-workshop` 仍为 `0.0`；`late-route-recovery` closed-loop smoke 证明 reward/profile 链路可用，但 300 秒三图仍全失败。随后 254 条 action4 贴边修复样本的 mid/late 消融保住 60 秒短窗，却让 180 秒 `soda-creek` 回落到 `0.4`，300 秒三图仍全为 `0.0`。这些结果都只能作为 repair 证据，不能进入 stage 03 或 RL acceptance。

基于 action4_w0_5 失败面导出的 `1001` 条 180-300 秒 late boundary recovery samples 进一步做了 late-only 小权重消融。该候选保留当前 opening 与 mid，只替换 late 子模型；60 秒 high-pressure 三图为 `0.4/1.0/0.8`，180 秒为 `0.6/1.0/0.8`，300 秒为 `0.0/0.0/0.4`。结论是样本方向有局部价值，尤其让 `cracked-star-jar` 长窗出现恢复信号，但 `soda-creek` 和 `caramel-workshop` 仍无法 300 秒存活，且失败分析显示 dominant action 转为 action `1` 后仍集中死于 late 低血量/贴边压力。报告位于 `harness/reports/2026-05-27_rl_late_boundary_lateonly_ablation_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_053_late_boundary_lateonly_ablation_gap.json`；下一步应转向 closed-loop late boundary escape / low-health survival curriculum，或补充 180-300 秒成功/近成功 clean survival 对照样本，而不是单纯继续提高 repair 样本权重。

从 `late-route-recovery` checkpoint 继续做 closed-loop late boundary curriculum smoke 后，结论更保守：在 high-pressure 三图和 seed `62400-62404` 上继续 `4096` timesteps，没有改善 300 秒 gate，反而破坏 opening/mid retention。60 秒为 `0.4/0.8/1.0`，180 秒为 `0.2/0.4/0.8`，300 秒仍为 `0.0/0.0/0.4`；300 秒失败分析中 `soda-creek` 已有 3 个 opening 死亡，`caramel-workshop` 也出现 opening/mid 死亡。报告位于 `harness/reports/2026-05-27_rl_late_boundary_closed_loop_curriculum_smoke_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_054_late_boundary_closed_loop_curriculum_regression.json`。下一轮 closed-loop 必须先加入 opening/mid retention 约束或 staged opening wrapper，并把 60/180 秒 gate 作为训练中止条件，不能继续只在失败 seed 上加 timestep。

使用 stage01 `corner_risk_delta` SB3 opening wrapper 负责前 60 秒、再切到上述 closed-loop fallback 的 evaluation-only probe 证明：opening wrapper 能清除 opening death，但不能修复 fallback。60 秒提升到 `1.0/1.0/0.8`，180 秒为 `0.4/0.8/0.6`，300 秒仍只有 `0.0/0.0/0.2`；300 秒失败分析中 14 个死亡局全部发生在 60 秒之后，`soda-creek` 主要死在 handoff/mid，`caramel-workshop` 主要死在 late。报告位于 `harness/reports/2026-05-27_rl_late_boundary_opening_wrapper_probe_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_055_late_boundary_opening_wrapper_fallback_gap.json`。下一步应基于该 wrapper 组合导出 `60-180s` handoff recovery 样本，或训练专门接手 opening wrapper 后状态分布的 fallback。

基于上述 wrapper 失败面，已从 `60-180s`、负 `route_recovery`、贴边高风险 sampled trace 行导出 `2438` 条 handoff recovery samples，并通过 `tools/validate_edge_recovery_samples.py`。样本 100% 落在 mid phase，原动作以 action `7` 和 action `4` 为主，目标动作分布为 action `3/0/8/2/...`；其中 target action `0` 占 `26.99%`，说明后续训练必须保留 soft target 和动作分布正则，避免把 fallback 修成静止策略。报告位于 `harness/reports/2026-05-27_rl_late_boundary_handoff_samples_001/summary.md`。这批样本只是 fallback / mid-window repair input，不是 RL policy gate。

handoff recovery samples 的首个 mid-only 小权重消融没有带来在线收益。该实验只替换 staged behavior clone 的 mid 子模型，保留 `opening_action3_w0_5_windowed` opening 子模型和 `late_boundary_w0_5` late 子模型；mid 训练使用 `edge_recovery_sample_weight=0.5`、`recovery_soft_target=top_k_scores`、`entropy_regularization=0.02` 和 `action_distribution_regularization=0.2 / per_map_uniform_present`。训练集共有 `12691` 条 mid 样本，其中 `2780` 条为 handoff repair input，validation accuracy 为 `0.6608`。但 deterministic high-pressure 三图结果仍为 60 秒 `0.4/1.0/0.8`、180 秒 `0.6/1.0/0.8`、300 秒 `0.0/0.0/0.4`，与上一轮 late-only 消融没有本质改善；300 秒失败分析仍记录 `13` 个死亡局，`caramel-workshop` 全部死于 `180-300s`，`soda-creek` 和 `cracked-star-jar` 同时存在 opening 早死和 late 死亡。报告位于 `harness/reports/2026-05-27_rl_late_boundary_handoff_midonly_ablation_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_056_late_boundary_handoff_midonly_ablation_gap.json`。结论：mid-only handoff imitation 不能解除 long-run blocker，下一步应比较 opening wrapper + fallback-only 与 staged mid-only 的交接状态分布，并继续单独处理 late-window low-health、hazard 和 Boss pressure recovery。

把同一个 handoff mid-only staged fallback 接到 stage01 `corner_risk_delta` opening wrapper 后，opening death 被清除，但 fallback 仍未通过。该 evaluation-only probe 前 60 秒使用 `stage01_corner_risk_delta_smoke.zip`，60 秒后切到 `handoff_mid_w0_5/staged.pt`，并使用 upgrade ranker 填升级选择。60 秒 high-pressure 三图为 `1.0/1.0/0.8`，180 秒为 `0.6/0.6/0.6`，300 秒三图全部为 `0.0`。300 秒失败分析记录 `15` 个死亡局且 opening bucket 为 `0`：`soda-creek` 和 `caramel-workshop` 各有 `1` 个 mid 死亡、`4` 个 late 死亡，`cracked-star-jar` 有 `3` 个 mid 死亡、`2` 个 late 死亡。报告位于 `harness/reports/2026-05-27_rl_late_boundary_handoff_opening_wrapper_probe_001/summary.md`，failure case 为 `harness/failed_cases/fail_20260527_057_late_boundary_handoff_opening_wrapper_probe_gap.json`。结论：opening wrapper 能保护短窗，但 handoff mid-only fallback 没有稳定接住中后窗；下一步应输出 60 秒交接点 trace，对比位置、生命、边界风险和 fallback 初始动作分布，再决定是否训练真正的 fallback policy 约束。

60 秒交接点 trace 进一步说明，短窗胜率不能直接解释为健康交接。对 `stage01 opening wrapper + handoff_mid_w0_5 fallback` 复跑 180 秒 high-pressure 三图 5 seed 并输出 sampled trace 后，15/15 个 episode 在交接前最后一帧都处于 `edge_risk >= 0.9`。三图在 180 秒仍各为 `0.6` 胜率；`soda-creek` / `caramel-workshop` / `cracked-star-jar` 的平均交接生命分别为 `93.0918` / `98.5834` / `87.0172`，但 `cracked-star-jar` seed `62404` 交接时生命只有 `3.7330`。首个 fallback action 主要是 action `8`、`3` 和 `2`，60-75 秒窗口继续呈现单方向段：`soda-creek` action `3:113, 8:96`，`caramel-workshop` action `8:133, 3:62`，`cracked-star-jar` action `3:104, 2:90`。报告位于 `harness/reports/2026-05-27_rl_late_boundary_handoff_opening_wrapper_trace_001/summary.md`。结论：fallback 需要明确学习“从贴边交接状态回到可持续路线”，后续监督样本应优先提取 `60-90s` non-edge recovery，并过滤极低血量残局。

带 observation 的 60-90 秒复跑已形成更窄的接手修复样本池。复跑 `stage01 opening wrapper + handoff_mid_w0_5 fallback` 的 180 秒 high-pressure 三图 5 seed 后，三图仍各为 `0.6`，但 trace 可被监督训练链路消费。`tools/export_route_recovery_samples.py` 新增 `--min-health-ratio`，并从 `60-90s`、负 `route_recovery`、`boundary.edge_risk >= 0.75`、原动作继续顶边的 trace 行中导出 `713` 条样本；`min_health_ratio=0.25` 没有丢样本，导出样本的 `health_ratio` 为 `0.5002-0.6650`。`tools/validate_edge_recovery_samples.py` 判定 `edge_recovery_samples_valid`，`train_behavior_clone.py --dry-run` 判定 `dataset_validated_not_training_gate`。报告位于 `harness/reports/2026-05-27_rl_late_boundary_handoff_opening_wrapper_obs_samples_001/summary.md`。结论：这批样本只能作为 fallback / mid-window repair training input；下一步应做 fallback-only 或 mid-only 小权重消融，并继续保留 60/180/300 秒 deterministic high-pressure 三图门禁。

60-90 秒 handoff 样本的 mid-only 小权重消融仍没有通过。该消融只混入新导出的 `713` 条 handoff route-recovery 样本和三图 phase-aligned KiteBot 轨迹，不混入旧 `60-180s` handoff 样本或通用 route-recovery 样本；训练 `mid` 子模型后重新打包 staged fallback，并在 stage01 opening wrapper 下复测。60 秒保持 `1.0/1.0/0.8`，180 秒为 `0.6/1.0/0.4`，300 秒为 `0.2/0.2/0.0`，记录 `fail_20260527_058`。结果说明窄 handoff 样本带来局部收益，但 `cracked-star-jar` mid-window 回落更明显，且 300 秒仍是 repair。报告位于 `harness/reports/2026-05-27_rl_late_boundary_handoff_opening_wrapper_midonly_ablation_001/summary.md`。下一步不应继续只追加同类 `60-90s` edge 样本；应比较 fallback-only 约束、`cracked-star-jar` 专项 handoff 样本，或转向 late-window low-health / hazard / Boss pressure recovery。

fallback-only probe 证明问题不是 staged late 子模型或 phase dispatch 单独造成。该 probe 前 60 秒仍用 stage01 opening wrapper，60 秒后直接切到上一轮训练出的 `mid.pt`，不经过 staged `opening/mid/late` dispatcher。60 秒保持 `1.0/1.0/0.8`，但 180 秒降为 `0.4/0.8/0.2`，300 秒三图全为 `0.0`，记录 `fail_20260527_059`。300 秒失败分析显示 opening bucket 为 `0`，但 15 个死亡局全部落在 mid / late，且 `cracked-star-jar` action `7` 占比达到 `61.49%`。结论：不能继续只把 `60-90s` handoff 样本加权到同一个 mid clone；下一步应转向 `cracked-star-jar` 专项 handoff 样本，或 late-window low-health / hazard / Boss pressure recovery。报告位于 `harness/reports/2026-05-27_rl_late_boundary_handoff_opening_wrapper_fallback_only_probe_001/summary.md`。

`tools/export_route_recovery_samples.py` 已支持 `--map-id` 按地图导出 route-recovery 修复样本，并用该能力从现有 observation trace 中切出 `cracked-star-jar` 专项 handoff 样本。过滤 `60-90s`、负 `route_recovery`、`boundary.edge_risk >= 0.75`、`min_health_ratio = 0.25` 后得到 `190` 条样本，覆盖 seed `62400-62404`，时间范围 `60.3328-89.999s`，校验和 behavior clone dry-run 均通过。样本 target action 分布为 `7:86, 6:41, 1:34, 3:29`，这说明后续不能做全局 action `7` 惩罚或加权；必须保留 map / position conditioning、soft target 和动作分布正则。报告位于 `harness/reports/2026-05-27_rl_late_boundary_handoff_cracked_star_samples_001/summary.md`。

`cracked-star-jar` 专项样本的 mid-only 小权重消融只有局部收益，仍没有通过长窗门禁。该消融把 `190` 条专项样本与三图 phase-aligned KiteBot 轨迹混合训练 mid 子模型，然后保留既有 opening / late 子模型打包 staged fallback 并接入 stage01 opening wrapper。60 秒保持 `1.0/1.0/0.8`，180 秒为 `0.6/1.0/0.6`，300 秒三图全为 `0.0`，记录 `fail_20260527_060`。结果说明专项样本把 `cracked-star-jar` 180 秒从 `0.4` 拉回 `0.6`，并把其 300 秒平均存活推到 `174.6401s`，但三图仍无 300 秒胜局且 action `7` 继续主导。下一步应转向 late-window low-health / hazard / Boss pressure recovery，或补充 180-300 秒成功/近成功 clean survival 对照样本。报告位于 `harness/reports/2026-05-27_rl_late_boundary_handoff_cracked_star_midonly_ablation_001/summary.md`。

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
