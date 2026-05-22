# Bevy 技术架构计划

## 总体判断

《软糖风暴》如果以 AI 开发和 Harness 为核心，Bevy 的优势在于：

- 强类型帮助 AI 发现错误。
- ECS 天然适合仿真、Bot 和批量测试。
- 渲染可以和核心逻辑分离。
- 所有关键逻辑都可以文本化，便于 Agent 修改和 review。

代价：

- UI、动画、编辑器体验不如 Godot/Unity 省心。
- 前期工程搭建更硬。
- Rust 对 AI Agent 的编译反馈更严格，迭代时需要更强 Harness。

## 架构原则

核心原则：

> 游戏本体、Bot、Harness、AI 训练都应该调用同一个 GameCore。

不要让渲染层成为唯一真相。

错误架构：

```text
Bevy App + Render + Input + Scene Logic
然后 Bot 试图模拟按键
```

推荐架构：

```text
GameCore ECS Logic
  ├─ Bevy Runtime Client
  ├─ Headless Simulation Client
  ├─ Bot Evaluation Client
  └─ Python Gym Bridge
```

## 推荐目录结构

```text
soft-candy-storm/
  crates/
    game_core/
      src/
        lib.rs
        components/
        systems/
        resources/
        events/
        metrics/
        content/
    game_runtime/
      src/
        main.rs
        rendering/
        input/
        ui/
        audio/
    game_harness/
      src/
        main.rs
        batch_runner.rs
        reports.rs
        gates.rs
    bot_policies/
      src/
        lib.rs
        idle.rs
        reflex.rs
        route.rs
        replay.rs
    content_tools/
      src/
        validate.rs
        budget.rs
        diff.rs
  content/
    weapons/
    passives/
    enemies/
    waves/
    maps/
    characters/
  python/
    gym_env/
    train/
    evaluate/
  docs/
  harness/
    reports/
    generated_candidates/
    accepted_content/
```

中文项目名可以是《软糖风暴》，仓库目录为了跨工具兼容，建议最终代码仓库使用 ASCII 名：

```text
soft-candy-storm
```

当前文档目录仍可使用中文名。

## Crate 职责

### game_core

不依赖窗口，不依赖玩家输入设备，不依赖具体渲染。

负责：

- 世界初始化
- 角色属性
- 移动
- 敌人生成
- 敌人行为
- 武器冷却和释放
- 投射物
- 碰撞
- 伤害
- 掉落
- 升级
- Boss 阶段
- 结算
- metrics 收集

禁止：

- 读取键盘
- 播放音效
- 创建窗口
- 依赖鼠标坐标
- 写死具体图片资源

### game_runtime

Bevy 正式运行客户端。

负责：

- 窗口
- 渲染
- 玩家输入
- 摄像机
- UI
- 音效
- 动画
- 粒子
- 资源加载

它应该把输入转换成 GameCore 的 Action，而不是直接改核心状态。

### game_harness

批量测试和报告工具。

负责：

- 加载内容候选
- 跑多 seed
- 跑多 Bot
- 汇总指标
- 执行门禁
- 输出 JSON/Markdown 报告
- 保存失败 replay

### bot_policies

所有非学习型 Bot。

负责：

- IdleBot
- RandomBot
- ReflexBot
- KiteBot
- GreedyXpBot
- BossHunterBot
- RouteBot
- ReplayBot

### content_tools

内容校验和预算。

负责：

- schema 校验
- id 唯一性
- 引用检查
- 数值区间检查
- 理论 DPS 预算
- 波次压力预算
- 与已有内容相似度检查

## ECS 组件设计

### 基础组件

- Position
- Velocity
- Radius
- Health
- Damage
- Team
- Lifetime
- ExperienceValue
- Pickup
- ScoreValue

### 玩家组件

- Player
- PlayerStats
- PlayerBuild
- Level
- Experience
- PickupRadius
- Invulnerability

### 敌人组件

- Enemy
- EnemyKind
- EnemyBehavior
- ContactDamage
- Boss
- Elite

### 武器组件

- WeaponSlot
- WeaponCooldown
- WeaponLevel
- WeaponOwner
- Projectile
- AreaEffect
- Orbiting
- Summon

### 地图/波次组件

- WaveSchedule
- SpawnPoint
- SpawnBudget
- MapBounds
- HazardZone

### Metrics 组件/资源

- RunMetrics
- DamageBreakdown
- WeaponMetrics
- EnemyMetrics
- PerformanceMetrics

## 系统设计

推荐系统顺序：

```text
1. apply_controller_actions
2. update_player_movement
3. update_wave_spawns
4. update_enemy_behavior
5. update_weapon_cooldowns
6. spawn_weapon_effects
7. update_projectiles
8. update_area_effects
9. resolve_collisions
10. apply_damage
11. collect_pickups
12. process_level_ups
13. update_boss_phases
14. cleanup_dead_entities
15. record_metrics
16. check_terminal_state
```

这个顺序需要固定，保证 headless 仿真可复现。

## Action 接口

Bot 和玩家都输出 Action。

建议：

```text
Action {
  movement: Vec2,
  upgrade_choice: Option<usize>,
  active_skill: Option<SkillId>
}
```

首版只有 movement 和 upgrade_choice。

## Snapshot 接口

Bot、Harness 和 Python 训练都读取 Snapshot。

Snapshot 不应暴露完整 ECS 世界，而是暴露稳定的观察数据：

- 时间
- 玩家位置
- 玩家生命
- 玩家等级
- 当前经验
- 当前 Build
- 最近 N 个敌人的相对位置、速度、半径、血量
- 最近 N 个糖晶的相对位置和价值
- Boss 状态
- 当前升级选项
- 地图边界

## 内容数据格式

候选格式：

- Ron：Rust/Bevy 生态友好
- TOML：人工可读强
- JSON：AI 和 Python 生态最友好

建议：

首版用 JSON，因为：

- AI 生成稳定
- Python 读取容易
- schema 校验成熟

后续如果 Bevy 资源系统需要，可转换为 Ron。

## Headless 仿真

Headless 仿真必须支持：

- 固定 seed
- 固定 dt
- 无渲染
- 无音频
- 无窗口
- 多倍速
- 批量运行
- 输出 metrics
- 保存 replay

命令示例：

```bash
cargo run -p game_harness -- simulate --seeds 100 --bots reflex,kite,greedy --duration 600
```

## Python Bridge

Python 训练层不应该直接控制窗口。

推荐方式：

1. Rust 侧提供 headless environment。
2. Python 通过 FFI、进程通信或批处理接口调用。
3. 首版可以先用 subprocess + JSON line 协议，简单稳定。
4. 性能瓶颈出现后再考虑 PyO3。

JSON line 协议示例：

```text
Python -> Rust: {"cmd":"reset","seed":123}
Rust -> Python: {"obs":[...],"done":false}
Python -> Rust: {"cmd":"step","action":3}
Rust -> Python: {"obs":[...],"reward":0.12,"done":false,"info":{...}}
```

## 最小迁移路径

1. 保留当前 Phaser 原型作为玩法参考。
2. 新建 Bevy workspace。
3. 先实现 game_core 的 headless 10 分钟仿真。
4. 再实现 Bevy 渲染客户端。
5. 接入规则 Bot。
6. 接入 Harness 报告。
7. 接入 Python Gym。

不要第一天就追求完整美术和 RL。

