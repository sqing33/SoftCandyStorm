# Bot 测试计划

## Bot 的定位

Bot 不是用来替代玩家，也不是用来证明游戏好玩。Bot 是测试工具，用来在短时间内覆盖大量局面。

Bot 负责发现：

- 开局是否过难
- 某些波次是否无解
- 某些武器是否过强
- 某些敌人组合是否造成性能问题
- 某些 Build 是否自动赢
- 某些地图路线是否安全漏洞

真人负责判断：

- 手感是否舒服
- Build 是否爽
- 画面是否可读
- 压力是否有趣
- 主题是否吸引人

## Controller 接口

所有 Bot 输出统一 Action：

```text
Action {
  movement: Vec2,
  upgrade_choice: Option<usize>
}
```

输入统一 Snapshot：

```text
Snapshot {
  time,
  player_state,
  visible_enemies,
  visible_pickups,
  current_build,
  upgrade_options,
  boss_state,
  map_info
}
```

## Bot 类型

### IdleBot

行为：

- 原地不动。
- 升级时选择第一个选项或固定优先级。

用途：

- 测最低压力。
- 如果 IdleBot 能活太久，说明开局或武器过强。
- 如果 IdleBot 瞬死，也可能说明开局压力太高。

指标：

- 存活时间
- 击杀数
- 是否升级
- 敌人数峰值

### RandomBot

行为：

- 随机方向移动。
- 随机选择升级。

用途：

- 测游戏鲁棒性。
- 发现边界和碰撞 bug。
- 作为低技能玩家近似。

注意：

- RandomBot 不应用于平衡主判断。

### CowardBot

行为：

- 优先远离最近敌人。
- 不主动拾取糖晶，除非安全。
- 升级优先选择防御、移动、范围。

用途：

- 测逃跑流是否能生存。
- 测敌人追踪是否能压迫玩家。
- 测地图边界是否有安全角落。

### GreedyXpBot

行为：

- 优先追最近高价值糖晶。
- 只有危险非常近时才躲避。
- 升级优先选择经验、拾取、冷却。

用途：

- 测经济流。
- 测经验掉落密度。
- 测高成长 Build 是否过强。

### KiteBot

行为：

- 围绕敌群外侧绕圈。
- 保持与最近敌人的安全距离。
- 优先远程武器和移速。

用途：

- 测风筝流。
- 测远程投射武器强度。
- 测快速敌人是否足够威胁。

### TankBot

行为：

- 不追求完美躲避。
- 允许接触少量敌人。
- 优先生命、减伤、恢复、环绕武器。

用途：

- 测防御流。
- 测受伤反馈。
- 测回复是否过强。

### BossHunterBot

行为：

- Boss 出现后优先接近 Boss 输出。
- 平时保持基础生存。
- 升级优先选择单体、穿透、光束。

用途：

- 测 Boss 血量。
- 测单体流派。
- 测 Boss 机制是否可躲。

### ZoneControlBot

行为：

- 尽量停留在自己创建的控制区域附近。
- 优先选择焦糖、薄荷、召唤、持续区域。

用途：

- 测控制流派。
- 测区域武器是否有价值。
- 测敌人是否能突破防线。

### RouteBot

行为：

- 按预设路线移动。
- 路线可以是圆形、方形、8 字形、地图边缘巡逻。

用途：

- 测地图路线。
- 测固定路线是否形成安全漏洞。
- 测怪物从不同方向生成是否合理。

### ReplayBot

行为：

- 回放真人输入。
- 使用原始升级选择，或在选项不同的时候按相似标签选择。

用途：

- 做真实玩家回归测试。
- 检查改数值后是否破坏已有体验。
- 对比版本间死亡时间和伤害来源。

## Bot 技能等级

为了模拟不同玩家，需要把 Bot 分层：

### 低技能

- 反应慢
- 危险距离阈值低
- 升级选择随机
- 容易贪经验

### 中技能

- 能躲近处敌人
- 能绕圈
- 升级有简单优先级
- 会避开 Boss 明显攻击

### 高技能

- 保持距离
- 规划路线
- 根据 Build 选择位置
- Boss 阶段策略不同

## 升级选择策略

Bot 需要可配置升级偏好：

```text
UpgradePolicy {
  prefer_tags: ["aoe", "cooldown"],
  avoid_tags: ["summon"],
  prefer_existing_weapons: true,
  evolution_priority: high,
  defense_threshold: health < 40%
}
```

## Bot 矩阵

每次内容评估至少跑：

| Bot | Seed 数 | 用途 |
|---|---:|---|
| IdleBot | 20 | 压力下限 |
| RandomBot | 20 | 鲁棒性 |
| CowardBot | 50 | 生存压力 |
| GreedyXpBot | 50 | 成长曲线 |
| KiteBot | 50 | 远程流派 |
| TankBot | 50 | 防御流派 |
| BossHunterBot | 50 | Boss 平衡 |
| RouteBot | 20 | 地图漏洞 |

快速 CI 可减少 seed，nightly 批跑再扩大。

候选晋级和发布探针要分开解释：较小 seed 的候选仿真可以用于进入 `simulated_candidates`，但 Release Candidate 前应至少用更大样本复查关键 Bot。Phase 4 full pack 的首次 20 seed / 600 秒发布探针显示 GreedyXpBot 胜率 65.0%、TankBot 胜率 80.0%，均超过中技能 Bot 25%-55% 目标区间；后续 Bot 策略校准复测让 GreedyXpBot 回到 50.0%、TankBot 回到 25.0%，9 Bot x 20 seed 全部通过。该结论只说明 Bot matrix release gate 的自动部分恢复为 `pass`，不得把它当作人工乐趣、Runtime 性能或正式内容接受证据。

## Bot 输出指标

每局记录：

- bot 类型
- seed
- 存活时间
- 是否胜利
- 死亡原因
- 等级
- 选择记录
- Build
- 击杀数
- Boss 伤害
- 受伤来源
- 最大敌人数
- 平均帧耗时
- 地图位置热力

## Replay 数据

Replay 记录：

- 初始 seed
- 每帧或固定 tick 的 movement
- 升级选择
- 角色
- 地图
- 内容版本
- 游戏版本

Replay 用途：

- 回放真人局
- 复现 bug
- 比较版本
- 训练模仿学习，后续可选
