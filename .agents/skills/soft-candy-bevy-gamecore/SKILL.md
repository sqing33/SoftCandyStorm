---
name: soft-candy-bevy-gamecore
description: 当实现、重构、审查或规划《软糖风暴》的 Rust Bevy GameCore 时使用：ECS 组件和系统、固定步长仿真、确定性 seed、headless 执行、runtime 集成、Bot action、snapshot、metrics 或 replay。
---

# 软糖风暴 Bevy GameCore

用于所有涉及《软糖风暴》Rust/Bevy 核心玩法仿真的工作。

## 必读文档

实现前读取：

1. `AGENTS.md`
2. `docs/06_Bevy技术架构计划.md`
3. `docs/14_GameCore接口规格.md`
4. `docs/13_内容数据Schema设计.md`
5. `docs/15_经济与数值平衡模型.md`

如果涉及 Bot 或 RL 集成，再读：

- `docs/08_Bot测试计划.md`
- `docs/09_AI_Bot训练计划.md`
- `docs/16_Replay与遥测设计.md`

## 核心规则

GameCore 是唯一玩法真相。

它必须：

- 可 headless 运行
- 固定 tick
- seed 确定性
- 独立于渲染、音频、窗口和真实输入设备
- 可被 Bevy Runtime、Harness、Bot、Replay 和 Python Gym bridge 调用

## 架构边界

`game_core` 负责：

- 世界初始化
- 玩家移动
- 敌人生成和行为
- 武器
- 投射物
- 碰撞
- 伤害
- 掉落
- 升级
- Boss 阶段
- 终局状态
- metrics
- replay 数据

`game_runtime` 负责：

- 窗口
- 渲染
- 摄像机
- 输入设备
- UI
- 音频
- 动画
- 粒子

Runtime 必须把玩家输入转换成 `PlayerAction`，调用 GameCore，再根据 snapshots/events 渲染。Runtime 不得直接修改生命、经验、敌人、波次、武器或结算结果。

## 接口要求

遵守 `docs/14_GameCore接口规格.md`。

GameCore 语义必须包含：

- `reset(config) -> snapshot`
- `step(action, fixed_dt) -> StepResult`
- `snapshot() -> RunSnapshot`
- `metrics() -> RunMetrics`
- `is_terminal() -> bool`

所有 Bot 和 RL 控制都应通过 `PlayerAction`。

## 确定性规则

- 使用 seed 管理的 RNG 资源。
- GameCore 不使用墙钟时间。
- 不在受控 RNG 外调用随机 API。
- fixed tick 必须记录在 metrics 和 replay 中。
- 同版本同 hash 的 replay 不能复现时，视为 bug。

## 实现顺序

从零开始时：

1. Workspace 和 crates。
2. `game_core` 数据类型和 RunConfig。
3. 固定步长 schedule。
4. 移动、敌人追踪、伤害。
5. 武器冷却和简单投射物。
6. XP、升级、升级选项。
7. 波次和终局状态。
8. Metrics。
9. 规则 Bot 客户端。
10. Bevy runtime 可视化。

不要从渲染优先的玩法实现开始。

## 验证

Rust/Bevy 工作优先运行：

```bash
cargo fmt --check
cargo clippy --workspace --all-targets
cargo test --workspace
```

当 Harness 存在后，还要运行项目文档或脚本定义的快速仿真命令。

如果某项验证因为阶段尚未到达而无法运行，需要明确说明。

## 禁止事项

- 不要把玩法真相放进 Bevy 渲染代码。
- 不要让 Runtime 绕过 GameCore。
- 不要引入非确定性随机。
- 不要把浏览器自动化当成玩法测试。
- 不要在规则 Bot 基线存在前实现 RL。

