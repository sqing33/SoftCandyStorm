---
name: soft-candy-storm-context
description: 当任务涉及《软糖风暴》项目时使用：包括项目入门、决定读取哪些文档、遵守当前阶段规则、Git 规范、目录所有权、AI 内容红线，以及 Bevy + Harness + RL 默认技术路线。
---

# 软糖风暴项目上下文

当任务涉及《软糖风暴》时使用本 Skill，尤其是开始计划、修改文档、实现代码、生成内容、审查 Harness 输出或协调多个 Agent 之前。

## 项目根目录

本 Skill 放在项目内 `.agents/skills/`，所有路径都以仓库根目录为基准。

如果当前目录不确定，先寻找包含 `AGENTS.md` 且标题提到 `《软糖风暴》` 的目录。

## 必读文档

总是先读：

1. `AGENTS.md`
2. `docs/00_index.md`
3. `docs/01_游戏愿景与设计支柱.md`
4. `docs/02_核心玩法规格.md`
5. `docs/06_Bevy技术架构计划.md`
6. `docs/07_Harness工程计划.md`

再按任务读取：

- 剧情、内容、美术：`docs/03_*`、`docs/04_*`、`docs/05_*`
- Bot / RL：`docs/08_*`、`docs/09_*`
- AI 内容流水线：`docs/10_*`
- 上线门禁：`docs/11_*`
- 路线图：`docs/12_*`
- Schema、接口、平衡、Replay、素材、局外循环：`docs/13_*` 到 `docs/18_*`

## 当前阶段

默认阶段是 Plan / Design。

除非用户明确要求开始实现：

- 只修改文档、计划、规范、Prompt 和任务拆解。
- 不初始化正式代码工程。
- 不添加运行时代码、训练脚本、依赖或大批生成素材。

## 默认技术方向

- 游戏框架：Bevy / Rust。
- 核心规则：GameCore 必须可 headless 测试，渲染只是一个客户端。
- 训练栈：Python Gymnasium + Stable-Baselines3。
- 风格：可爱糖果肉鸽，不是暗黑科幻。
- AI 生成内容必须先进候选池，再通过 Harness 门禁。

## 目录边界

遵守 `AGENTS.md` 的文件所有权规范。

关键边界：

- `docs/`：计划和设计。
- 未来 `crates/game_core/`：无渲染核心逻辑。
- 未来 `crates/game_runtime/`：Bevy 渲染、输入、UI、音频。
- 未来 `content/`：正式内容。
- 未来 `harness/generated_candidates/`：AI 生成候选内容。
- 未来 `python/`：Gymnasium/SB3 训练与评估。

## Git 规则

严格遵守 `AGENTS.md`。

重点：

- 提交信息使用中文。
- 格式：`<type>(<scope>): <描述>`。
- 暂存、提交或回滚前先看 `git status --short`。
- 除非用户明确要求，禁止 `git reset --hard`、`git push --force`、`git rebase`、`git clean -fdx`、`git checkout -- .`。
- 保留用户和其他 Agent 的改动。

## 沟通规则

- 对用户使用中文。
- 代码标识符、命令、Schema key、Git type/scope 保持英文。
- 如果验证命令无法运行，说明原因。

