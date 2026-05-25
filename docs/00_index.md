# 《软糖风暴》文档索引

## 项目定位

《软糖风暴》是一款可爱画风的俯视角自动攻击肉鸽生存游戏。玩家扮演糖罐守护员，在被魔法软糖风暴淹没的糖果王国中移动、躲避、拾取糖晶、升级甜点武器，并在一波波软糖怪潮中坚持到风暴眼出现。

本项目的特殊目标是：游戏不是只靠人工堆内容，而是从一开始就围绕 AI + Harness 工程设计，让 AI Agent 可以持续扩展武器、敌人、波次、地图、剧情素材，并由规则 Bot、Replay Bot、RL Bot 和自动平衡门禁进行大规模验证。

## 文档结构

- [01_游戏愿景与设计支柱.md](./01_游戏愿景与设计支柱.md)
  - 游戏定位、玩家体验、差异化、设计原则、上线愿景。

- [02_核心玩法规格.md](./02_核心玩法规格.md)
  - 一局游戏的完整循环、移动、自动攻击、经验、升级、Boss、结算。

- [03_世界观与剧情大纲.md](./03_世界观与剧情大纲.md)
  - 软糖王国、糖罐星、风暴来源、章节推进、角色和主题表达。

- [04_内容系统与素材库.md](./04_内容系统与素材库.md)
  - 武器、被动、角色、敌人、Boss、地图、事件、进化组合的内容计划。

- [05_美术与音频素材计划.md](./05_美术与音频素材计划.md)
  - 可爱视觉风格、精灵表、动画、UI、特效、音效和音乐方向。

- [06_Bevy技术架构计划.md](./06_Bevy技术架构计划.md)
  - Bevy/Rust 迁移思路、核心 crate、ECS 系统、headless 仿真、数据格式。

- [07_Harness工程计划.md](./07_Harness工程计划.md)
  - AI Agent 工作流、内容门禁、自动测试、质量指标、报告和持续改进循环。

- [08_Bot测试计划.md](./08_Bot测试计划.md)
  - Idle Bot、规则 Bot、条件反射 Bot、固定路线 Bot、Replay Bot 的设计。

- [09_AI_Bot训练计划.md](./09_AI_Bot训练计划.md)
  - Gymnasium/SB3、DQN/PPO、状态空间、动作空间、奖励函数、训练评估。

- [10_AI内容生成流水线.md](./10_AI内容生成流水线.md)
  - AI 生成内容、配置校验、仿真筛选、自动修正、内容入库流程。

- [11_测试指标与上线门禁.md](./11_测试指标与上线门禁.md)
  - 可上线游戏需要通过的稳定性、平衡性、性能、体验和人工验收标准。

- [12_阶段路线图.md](./12_阶段路线图.md)
  - 从原型、Bevy 重建、Harness、Bot、AI 内容到 Demo/上线的阶段计划。

- [13_内容数据Schema设计.md](./13_内容数据Schema设计.md)
  - 角色、武器、被动、敌人、Boss、波次、地图和事件的结构化数据契约。

- [14_GameCore接口规格.md](./14_GameCore接口规格.md)
  - GameCore 的 reset、step、snapshot、metrics、replay 和 Python Gym 接口。

- [15_经济与数值平衡模型.md](./15_经济与数值平衡模型.md)
  - 经验曲线、武器 DPS、敌人威胁、波次压力、Boss 血量和门禁阈值。

- [16_Replay与遥测设计.md](./16_Replay与遥测设计.md)
  - Replay 文件结构、回放策略、遥测事件、隐私原则和回归比较。

- [17_素材生成Prompt库.md](./17_素材生成Prompt库.md)
  - 生图提示词、spritesheet 规范、敌人/武器/UI Prompt 和素材命名。

- [18_完整游戏流程与局外成长.md](./18_完整游戏流程与局外成长.md)
  - 局外基地、章节推进、资源解锁、长期目标、游戏模式和 Demo 闭环。

- [19_Goal模式开发约定.md](./19_Goal模式开发约定.md)
  - Goal 模式的启动条件、阶段关系、执行方式、验证汇报和内容红线。

## 当前默认技术方向

- 游戏框架：Bevy / Rust
- 自动测试与训练：Python Gymnasium + Stable-Baselines3
- 内容配置：结构化数据文件，优先 Ron/TOML/JSON 之一，后续按 Bevy 生态确定
- Harness 原则：游戏核心逻辑必须可 headless 跑，渲染只是一个客户端
- 美术方向：可爱糖果、软萌怪潮、圆润高辨识度、适合批量生成和裁切

## 文档索引校验

修改 `docs/00_index.md`、`AGENTS.md` 必读清单，或新增、删除 `docs/00` 到 `docs/19` 文档后，应运行：

```bash
python3 tools/validate_docs_index.py --repo-root .
```

需要留下 Harness 证据时，生成 JSON 与 Markdown 报告：

```bash
python3 tools/validate_docs_index.py --repo-root . --report harness/reports/<report-id>/docs_index_validation.json --markdown harness/reports/<report-id>/summary.md
```

该校验只证明文档清单、索引链接和 Agent 必读编号一致，不代表每个文档需求都已经被代码、内容或素材实现。

## 关键设计判断

1. AI 不需要实时操控浏览器或游戏窗口。
2. 游戏核心必须能在无渲染环境中以固定 seed 批量模拟。
3. 真人试玩负责“好不好玩”，Harness 负责“会不会坏、是否明显失衡、是否可复现”。
4. 规则 Bot 先于 DQN/PPO 上线，RL Bot 作为高级压力测试工具。
5. AI 生成内容必须先进入候选池，通过门禁后才能进入正式内容池。
