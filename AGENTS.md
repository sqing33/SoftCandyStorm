# 《软糖风暴》Agent 指南

## 语言要求

- 始终使用中文回答用户，包括解释、总结、计划、进度汇报和最终结果。
- 代码、变量名、文件内技术标识、提交 type/scope 使用英文。
- 文档正文默认中文，除非是代码、Schema、命令、Prompt 或外部接口。

## 当前阶段

本仓库当前处于规划 / 设计阶段。除非用户明确要求开始实现，否则不要编写运行时代码或初始化正式工程。

如果用户明确要求进入 Goal 模式，按 `docs/19_Goal模式开发约定.md` 执行；Goal 模式允许围绕用户目标推进实现，但仍必须遵守 Harness、内容候选池和 GameCore/Runtime 边界。

## 必读顺序

1. `docs/00_index.md`
2. `docs/01_游戏愿景与设计支柱.md`
3. `docs/02_核心玩法规格.md`
4. `docs/06_Bevy技术架构计划.md`
5. `docs/07_Harness工程计划.md`

再按任务读取对应文档：

- 剧情、内容、美术：`03`、`04`、`05`
- Bot / RL：`08`、`09`
- AI 内容流水线：`10`
- 上线门禁：`11`
- 路线图：`12`
- Schema、接口、平衡、Replay、素材、局外循环：`13`、`14`、`15`、`16`、`17`、`18`

## 设计默认值

- 游戏框架：Bevy / Rust。
- 训练栈：Python Gymnasium + Stable-Baselines3。
- 游戏风格：可爱糖果肉鸽，不是暗黑科幻。
- Harness 策略：先做 headless 仿真，再做渲染表现。
- 内容生成：AI 只能生成候选内容，由 Harness 决定是否推进。

## 禁止事项

- 不要依赖浏览器控制作为主要游戏测试方法。
- 不要让生成内容绕过验证。
- 不要把 RL Bot 表现当作“游戏好玩”的证明。
- 不要把运行时渲染逻辑混入 GameCore。
- 不要在规则 Bot 基线存在前就从 DQN 开始。

## 阶段规则

当前默认阶段是 Plan / Design。除非用户明确要求进入实现阶段，否则只允许修改文档、计划、规范和任务拆解。

Goal 模式是一种显式执行方式，不会因普通讨论自动开启。只有用户明确说要进入或使用 Goal 模式时，才可以按目标跨入实现、内容、Harness 或 Bot 工作。

### Plan / Design 阶段

允许：

- 修改 `docs/`
- 修改 `README.md`
- 修改 `AGENTS.md`
- 增加设计草案、Schema、Prompt、路线图

禁止：

- 初始化正式代码工程
- 添加游戏运行时代码
- 添加训练脚本
- 引入依赖
- 生成大批素材进入正式目录

### Prototype 阶段

用户明确要求开始实现后才进入。

优先顺序：

1. 建立 Bevy workspace。
2. 实现 headless GameCore。
3. 实现规则 Bot。
4. 实现 Harness 批量仿真。
5. 再做 Bevy Runtime 可视化。

### Content 阶段

AI 只能把新内容写入候选目录，不能直接进入正式内容池。

推荐路径：

```text
generated_candidates -> validated_candidates -> simulated_candidates -> playtest_candidates -> accepted_content
```

### Release 阶段

任何发布候选必须通过：

- 编译
- 单元测试
- Harness 批量仿真
- Replay 回归
- 性能门禁
- 人工试玩验收

## 文件所有权规范

后续多 Agent 协作时，按目录划分责任。

### 文档与计划

- 目录：`docs/`
- 负责：设计 Agent、产品 Agent、叙事 Agent
- 规则：改动设计结论时必须同步更新 `docs/00_index.md` 或相关引用。

### 游戏核心

- 目录：未来的 `crates/game_core/`
- 负责：核心逻辑 Agent
- 规则：不得依赖渲染、窗口、音频或真实输入设备。

### 运行时表现

- 目录：未来的 `crates/game_runtime/`
- 负责：Runtime Agent、美术集成 Agent
- 规则：只能通过 GameCore 的 action/snapshot/events 交互。

### 内容配置

- 目录：未来的 `content/` 和 `harness/generated_candidates/`
- 负责：内容 Agent、平衡 Agent
- 规则：候选内容不得跳过 Schema 和 Harness 门禁。

### Harness

- 目录：未来的 `crates/game_harness/`、`harness/`
- 负责：测试 Agent、评估 Agent
- 规则：不能通过降低门禁阈值掩盖内容或代码问题。

### Bot 与 RL

- 目录：未来的 `crates/bot_policies/`、`python/`
- 负责：Bot Agent、RL Agent
- 规则：规则 Bot 是基线，DQN/PPO 是高级测试，不替代人工乐趣判断。

### 素材

- 目录：未来的 `assets/`、`asset/generated_candidates/`
- 负责：素材 Agent
- 规则：正式素材必须保存 prompt、来源、版本和后处理说明。
- 可使用 `mmx` CLI 的生图、TTS、music 能力制作素材候选；生成结果只能先进入 `asset/generated_candidates/`，不得直接覆盖正式 Runtime 素材。
- 每批 `mmx` 素材候选必须记录 prompt、命令/模型、生成时间、原始输出、后处理步骤、审查结论和后续处理建议。

## AI 内容生成红线

- AI 生成内容只能进入候选池。
- 未通过 Schema 的内容不得进入仿真。
- 未通过仿真的内容不得进入人工试玩候选。
- 未经人工确认的内容不得进入正式内容池。
- AI 不得删除失败内容的拒绝原因。
- AI 不得为了让内容通过而放宽门禁。
- AI 不得生成与当前可爱糖果风明显冲突的内容，除非用户明确要求探索新风格。

## 失败复盘规范

任何 bug、平衡失败、Bot exploit、训练异常、Replay 回归失败，都必须记录为 failure case。

建议字段：

```json
{
  "case_id": "fail_20260522_001",
  "category": "balance",
  "content_id": "caramel-overflow-wave",
  "seed": 12345,
  "bot": "KiteBot",
  "time_seconds": 87.4,
  "symptom": "前期敌人密度过高导致不可避免接触伤害",
  "root_cause": "快速怪和减速怪在 90 秒前同时高权重生成",
  "fix": "降低快速怪权重并推迟减速怪出现时间",
  "validation": "重新运行 50 seed 后前 2 分钟死亡率回到目标区间"
}
```

复盘要求：

- 能写 seed 就写 seed。
- 能写 Bot 就写 Bot。
- 能保存 replay 就保存 replay。
- 能写指标就不要只写主观描述。
- 修复后必须说明用什么验证。

新增或修改 failure case 后，应运行：

```bash
python3 tools/validate_failure_cases.py harness/failed_cases
```

该校验只检查字段完整性、`case_id` 与文件名前缀、可审计文本和基础类型；它不能替代修复后的仿真、Replay 或人工复核。

## Git 规范

本项目预计会长期由人类和多个 AI Agent 协作开发。Git 规范的目标不是形式主义，而是保证每一次改动都能被追踪、复盘、回滚和交接。

### 基本原则

- 提交信息使用中文。
- 每次提交只表达一个清晰意图，避免把无关修改混在一起。
- 先读状态再操作：提交、切分、回滚、合并前必须先看 `git status --short`。
- 不要改动与当前任务无关的文件。
- 不要替用户清理、重排、格式化或回滚你没有负责的改动。
- 如果工作区已有改动，默认认为它们来自用户或其他 Agent，必须保留。
- 文档、内容、代码、Harness、训练脚本可以分别提交，不要强行塞进一个大提交。

### 提交时机

长时间 Goal 模式或多模块开发时，不要把多个小时的工作堆到最后一次提交。每完成一个可解释、可验证的功能边界，就应考虑提交。

持续实现超过 45 到 60 分钟时，必须主动检查是否已经形成可提交边界；如果已经完成一个功能、报告、素材批次或文档结论，应先提交再继续下一块。用户要求“继续一直做”不等于允许累积无提交的大块改动。

开始下一项功能前，必须先提交已经完成且通过相应检查的当前功能；如果暂不提交，必须在进度说明中写明原因和剩余阻塞点。

应该提交的典型时机：

- 完成一个独立子系统或 crate，例如 `game_core`、`bot_policies`、`game_harness`、`game_runtime`。
- 完成一条 Harness 门禁链路，例如 schema 校验、静态预算、Bot 矩阵、Replay 回归或候选池晋级。
- 完成一批内容候选、验证报告、failure case 或项目进度记录。
- 从一个职责域切换到另一个职责域前，例如从 GameCore 切到 Runtime，或从代码切到文档。
- 运行了与该改动匹配的检查，并确认当前暂存内容能被清楚说明。

不应该提交的情况：

- 编译、测试或关键门禁仍在失败，且失败不是本次提交要刻意记录的已知现象。
- 暂存区混有无关文件、调试临时文件或其他 Agent/用户的改动。
- 还没看过 `git diff` 和 `git diff --cached`，无法说明提交具体包含什么。

如果一次工作已经跨过多个功能边界，应先按功能切分提交，再继续开发下一块。提交不是结束 Goal 模式，而是给后续协作留下可审计的进度锚点。

### 提交信息格式

格式：

```text
<type>(<scope>): <描述>
```

示例：

```text
docs(plan): 补充 Bevy 技术架构计划
feat(core): 增加 GameCore 固定步长模拟
fix(bot): 修复 GreedyXpBot 卡边界问题
test(harness): 增加波次压力预算测试
refactor(content): 拆分武器配置与进化配置
chore(repo): 初始化 Rust workspace 配置
```

### type 列表

- `feat`：新增功能、玩法系统、内容能力、工具能力
- `fix`：修复 bug、错误数值、错误引用、崩溃、测试失败
- `refactor`：不改变行为的结构调整
- `docs`：文档、设计稿、计划、注释说明
- `test`：测试、仿真用例、Bot 验证、门禁规则
- `chore`：依赖、构建、脚本、仓库配置、杂项维护
- `style`：格式、命名、排版，不改变行为
- `perf`：性能优化、批量模拟加速、渲染优化
- `content`：新增或调整游戏内容配置，如武器、敌人、波次、剧情素材
- `balance`：数值平衡调整
- `asset`：美术、音频、spritesheet、提示词、素材清单

### scope 建议

常用 scope：

- `docs`：文档体系
- `core`：纯游戏逻辑 / GameCore
- `runtime`：Bevy 渲染、输入、音频、UI
- `content`：内容配置
- `harness`：批量测试、报告、门禁
- `bot`：规则 Bot、Replay Bot、测试策略
- `rl`：Gymnasium、DQN、PPO、训练脚本
- `asset`：美术与音频资产
- `build`：构建、CI、workspace、依赖
- `release`：发布、打包、版本准备

如果 scope 不明确，优先选择影响最大的子系统。

### 提交描述要求

- 描述使用中文短句，不要用句号结尾。
- 描述要写“做了什么”，不要写“更新一下”“修改文件”这种无信息内容。
- 不要使用纯英文模板提交，例如 `update`, `fix bug`, `wip`。
- 不要提交含糊的 AI 痕迹描述，例如 `ai changes`, `codex update`。

推荐：

```text
docs(harness): 增加内容候选池门禁说明
balance(enemy): 降低前两分钟软糖怪接触伤害
feat(bot): 增加固定路线 Bot 设计文档
```

不推荐：

```text
update
fix
wip
改了一些东西
AI 自动修改
```

### 分支规范

如果项目进入正式 Git 开发阶段，建议分支命名：

```text
feat/<短描述>
fix/<短描述>
docs/<短描述>
content/<短描述>
harness/<短描述>
experiment/<短描述>
```

示例：

```text
feat/bevy-game-core
harness/bot-batch-report
content/first-weapon-pack
experiment/ppo-survival-bot
```

分支名使用英文小写和短横线，避免空格和中文，便于脚本、CI 和跨平台工具处理。

### 禁止的 Git 操作

除非用户明确要求并说明目标，否则禁止执行：

```bash
git reset --hard
git push --force
git push --force-with-lease
git rebase
git branch -D
git checkout -- .
git checkout -- <path>
git clean -fd
git clean -fdx
```

原因：

- 这些操作可能删除用户或其他 Agent 的未提交工作。
- AI Agent 不应擅自重写历史或清空工作区。
- 回滚应优先使用可审计方式。

### 回滚规范

- 已提交内容需要撤销时，优先使用 `git revert`。
- 未提交内容需要撤销时，必须先确认这些改动确实由当前 Agent 产生，且用户明确要求撤销。
- 如果文件里混有当前 Agent 和用户的修改，不要整文件回滚；应手动保留用户修改，只撤销自己负责的部分。

推荐：

```bash
git revert <commit>
```

不推荐：

```bash
git reset --hard HEAD~1
```

### 暂存规范

提交前必须确认暂存内容：

```bash
git status --short
git diff
git diff --cached
```

暂存建议：

- 优先精确暂存相关文件。
- 不要无脑 `git add .`，除非确认所有改动都属于当前任务。
- 文档、代码、素材、生成内容应尽量分开提交。

可以使用：

```bash
git add <path>
```

谨慎使用：

```bash
git add .
```

### AI Agent 协作规范

当多个 Agent 可能并行工作时：

- 每个 Agent 只负责明确的文件或模块范围。
- 不要重写别人刚改过的文件，除非任务要求集成。
- 发现冲突或不明改动时，先读文件和 diff，再决定如何兼容。
- 不要因为测试失败就随意删除别人的功能。
- 不能通过放宽测试、删除门禁来掩盖问题。

### 提交前检查

不同阶段至少执行对应检查。

文档阶段：

```bash
find docs -name "*.md" -maxdepth 1 -print
```

Rust/Bevy 阶段：

```bash
cargo fmt --check
cargo clippy --workspace --all-targets
cargo test --workspace
```

Harness 阶段：

```bash
cargo run -p game_harness -- simulate --quick
```

Python/RL 阶段：

```bash
python -m pytest
```

如果某项检查因环境缺失无法运行，最终回复和提交说明中必须明确写出未运行原因。

### 内容与素材提交规范

AI 生成内容不得直接进入正式内容目录。推荐流程：

```text
generated_candidates -> validated_candidates -> simulated_candidates -> accepted_content
```

提交时要区分：

- `content(...)`：游戏内容配置
- `asset(...)`：图片、音频、spritesheet、提示词
- `balance(...)`：只调数值
- `docs(...)`：只改说明

素材文件体积较大时：

- 不要提交无用中间版本。
- 保留最终可追踪源文件或生成提示词。
- 如果未来接 Git LFS，再将大素材纳入 LFS 规范。

### 版本标签规范

未来可用标签：

```text
prototype-v0.1
demo-v0.1
playtest-v0.1
rc-v1.0
release-v1.0
```

标签只用于可运行、可复现、说明完整的版本。

### 不同类型改动的提交建议

文档：

```text
docs(plan): 增加 AI Bot 训练计划
```

游戏核心：

```text
feat(core): 实现固定步长 GameCore 仿真
```

规则 Bot：

```text
feat(bot): 增加 KiteBot 走位策略
```

内容生成：

```text
content(weapon): 增加第一批糖果武器候选
```

平衡调整：

```text
balance(wave): 降低糖霜草地前期刷怪压力
```

素材：

```text
asset(sprite): 增加第一版软糖怪 spritesheet
```

Harness：

```text
test(harness): 增加武器理论 DPS 预算门禁
```
