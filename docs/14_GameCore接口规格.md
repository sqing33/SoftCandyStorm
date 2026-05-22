# GameCore 接口规格

## 目标

GameCore 是《软糖风暴》的唯一玩法真相。Bevy 渲染版、Harness、规则 Bot、Replay Bot、Python Gymnasium 环境都必须调用同一个 GameCore。

核心原则：

```text
渲染不是逻辑，窗口不是测试入口，GameCore 才是可复现的游戏。
```

## 设计目标

GameCore 必须：

- 无窗口
- 无音频
- 无 GPU 依赖
- 可固定 seed
- 可固定 tick
- 可批量运行
- 可输出 snapshot
- 可接收 action
- 可输出 metrics
- 可保存 replay

## 核心接口

推荐抽象：

```rust
pub struct GameCore {
    world: World,
    schedule: Schedule,
}

impl GameCore {
    pub fn reset(config: RunConfig) -> RunSnapshot;
    pub fn step(action: PlayerAction, dt: FixedDt) -> StepResult;
    pub fn snapshot(&self) -> RunSnapshot;
    pub fn metrics(&self) -> RunMetrics;
    pub fn is_terminal(&self) -> bool;
}
```

具体实现可以调整，但语义必须保持。

## RunConfig

用于初始化一局。

字段：

- `seed`
- `map_id`
- `character_id`
- `starting_loadout`
- `content_pack_ids`
- `difficulty`
- `duration_seconds`
- `bot_profile`，可选
- `ruleset_version`

示例：

```json
{
  "seed": 12345,
  "map_id": "frosting-grassland",
  "character_id": "jar-keeper",
  "starting_loadout": {
    "weapons": ["rainbow-candy-shot"],
    "passives": []
  },
  "content_pack_ids": ["base-demo"],
  "difficulty": "normal",
  "duration_seconds": 600,
  "ruleset_version": "prototype-v0"
}
```

## PlayerAction

所有控制器输出同一动作。

```rust
pub struct PlayerAction {
    pub movement: Vec2,
    pub upgrade_choice: Option<usize>,
    pub active_skill: Option<SkillId>,
}
```

首版只实现：

- movement
- upgrade_choice

### movement

规范：

- `x` 和 `y` 范围为 `-1.0..=1.0`
- 长度超过 1 时归一化
- 原地为 `(0, 0)`
- Bot 可以用离散 8 方向映射到 movement

### upgrade_choice

当游戏处于升级选择状态时有效。

规则：

- `None` 表示不选择，游戏保持暂停或等待。
- 索引越界必须返回错误或忽略并记录 metrics。
- ReplayBot 如果原选项不存在，需要通过标签相似度选择替代项。

## StepResult

```rust
pub struct StepResult {
    pub snapshot: RunSnapshot,
    pub events: Vec<GameEvent>,
    pub reward_hint: RewardHint,
    pub terminal: Option<TerminalState>,
}
```

### events

事件用于：

- 渲染特效
- 播放音效
- 记录 replay
- 训练奖励
- Harness 调试

常见事件：

- `EnemySpawned`
- `WeaponFired`
- `EnemyHit`
- `EnemyKilled`
- `XpDropped`
- `XpCollected`
- `LevelUp`
- `UpgradeOffered`
- `UpgradeChosen`
- `PlayerDamaged`
- `BossSpawned`
- `BossPhaseChanged`
- `RunEnded`

## RunSnapshot

Snapshot 是 Bot 和 Python 环境观察世界的稳定接口，不应直接暴露 ECS 内部实现。

字段：

- `time_seconds`
- `remaining_seconds`
- `player`
- `visible_enemies`
- `visible_pickups`
- `active_hazards`
- `boss`
- `upgrade_options`
- `build`
- `map`
- `metrics_partial`

## PlayerSnapshot

字段：

- `position`
- `velocity`
- `health`
- `max_health`
- `level`
- `xp`
- `xp_to_next_level`
- `move_speed`
- `pickup_radius`
- `damage_multiplier`
- `cooldown_multiplier`
- `status_effects`

## EnemySnapshot

字段：

- `entity_id`
- `enemy_id`
- `position`
- `velocity`
- `health`
- `max_health`
- `radius`
- `threat`
- `behavior`
- `is_boss`
- `is_elite`

Bot/RL 不需要看所有敌人。Snapshot 可限制最近 N 个敌人，完整信息保留给 debug snapshot。

## PickupSnapshot

字段：

- `entity_id`
- `pickup_type`
- `position`
- `value`
- `radius`

## BuildSnapshot

字段：

- `weapons`
- `passives`
- `evolutions`
- `tags`
- `open_evolution_paths`

## TerminalState

结束状态：

- `Victory`
- `Defeat`
- `Timeout`
- `Aborted`
- `InvalidState`

必须记录：

- 结束时间
- 原因
- 最后一击来源
- Boss 状态
- 最终等级
- 最终 Build

## Fixed Tick

仿真必须使用固定步长。

建议：

- GameCore tick：`1/30s` 或 `1/60s`
- Harness 快速仿真：可用 `1/20s`，但必须标注
- 渲染帧率与逻辑 tick 解耦

所有平衡报告必须记录 tick rate。

## 随机数

随机数必须来自 seed 管理的 RNG。

禁止：

- 在 GameCore 中直接使用系统时间
- 在 GameCore 中使用不可控随机源
- 在不同系统中隐式创建随机源

推荐：

- `RunRng` 作为资源
- 所有随机事件从 `RunRng` 派生
- 关键随机结果写入 replay 或可由 seed 重建

## Metrics 接口

RunMetrics 字段：

- `duration_seconds`
- `victory`
- `death_reason`
- `kills`
- `level`
- `score`
- `damage_dealt_by_weapon`
- `damage_taken_by_source`
- `xp_collected`
- `xp_dropped`
- `upgrade_choices`
- `boss_damage`
- `boss_kill_times`
- `max_enemy_count`
- `max_projectile_count`
- `average_frame_cost`
- `position_heatmap`

## Replay 接口

Replay 需要记录：

- RunConfig
- content version hash
- ruleset version
- tick rate
- action stream
- upgrade choices
- optional event checkpoints
- final metrics

Replay 不是视频，是可复现输入序列。

## 错误处理

GameCore 遇到非法内容时：

- 在加载阶段拒绝。
- 不应运行到一半 panic。
- 如果运行时出现非法状态，返回 `InvalidState` 并写 failure case。

非法状态包括：

- health NaN
- position NaN
- cooldown negative beyond tolerance
- enemy count over hard cap
- no upgrade option but level-up required

## Bevy Runtime 集成

Bevy Runtime 做三件事：

1. 读取玩家输入，生成 PlayerAction。
2. 调用 GameCore step。
3. 根据 snapshot/events 更新显示。

不要让 Runtime 绕过 GameCore 直接改生命、经验、敌人或武器。

## Python Gym 集成

Gym 环境做三件事：

1. reset 时传 RunConfig。
2. step 时传离散/连续 action。
3. 从 snapshot 转 observation，从 reward_hint/metrics 转 reward。

首版可用 JSON line 协议，后续性能不足再考虑 PyO3。

