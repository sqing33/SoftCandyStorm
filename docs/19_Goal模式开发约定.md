# Goal 模式开发约定

## 目标

Goal 模式用于把已经完成规划的方向推进到可交付结果。它不是新的项目阶段，而是一种由用户显式开启的工作方式：当用户给出清晰目标后，Agent 可以持续执行、验证、修正并汇报，直到目标完成、被阻塞或用户中止。

Goal 模式的重点不是把工作切成最小原型，而是围绕用户给出的目标保持连续推进。

## 启动条件

只有用户明确表达类似以下意图时，才视为进入 Goal 模式：

```text
进入 goal 模式，实现 GameCore
用 goal 模式把 Harness 跑起来
开启 goal 模式，做完第一版可玩原型
```

普通讨论、规划、分析、文档补充、路线图整理，不自动进入 Goal 模式。

如果用户只是说“下一步怎么做”“分析一下”“规划一下”，仍按 Plan / Design 阶段处理。

## 与阶段规则的关系

默认状态仍是 Plan / Design。未进入 Goal 模式前，Agent 不应初始化正式工程、编写运行时代码、添加训练脚本或生成正式素材。

进入 Goal 模式后，Agent 可以根据目标需要跨入 Prototype、Content、Harness、Bot 或 Runtime 工作，但必须遵守以下边界：

- 不能让生成内容绕过 Schema、预算、仿真和人工确认。
- 不能把 AI 生成内容直接写入正式内容池。
- 不能为了通过门禁而降低门禁阈值。
- 不能把运行时渲染逻辑混入 GameCore。
- 不能用 RL Bot 表现代替人工试玩结论。
- 不能在规则 Bot 基线存在前以 DQN/PPO 作为主要测试方案。

Goal 模式允许推进实现，不等于允许跳过项目红线。

## 执行方式

Goal 模式中，Agent 应围绕用户目标主动推进：

1. 先读取与目标相关的项目文档和当前工作区状态。
2. 明确本轮目标、约束、验收方式和可能影响的文件范围。
3. 直接实施需要的代码、文档、内容或 Harness 改动。
4. 运行与改动匹配的验证命令。
5. 根据验证结果修正问题。
6. 最终汇报完成内容、验证结果、剩余风险和下一步。

如果目标需要跨多个系统，优先保持 GameCore、Runtime、Harness、Bot、Content 的边界清晰，而不是为了短期跑通把职责混在一起。

## 结束条件

Goal 模式在以下情况结束：

- 用户给出的目标已经完成并通过对应验证。
- 同一阻塞条件连续出现，Agent 无法继续推进。
- 用户明确要求停止、暂停或切回规划。
- 目标范围被用户重新定义，需要开启新的 Goal。

结束时应说明当前状态，而不是只说“完成”。

## 最终汇报要求

每次 Goal 模式完成或中断时，最终回复至少包含：

- 实际完成了什么。
- 改动了哪些主要文件或目录。
- 运行了哪些验证命令。
- 哪些验证通过、哪些没有运行或失败。
- 是否生成了候选内容。
- 是否产生 failure case 或需要补充复盘。
- 下一步最自然的推进方向。

如果验证命令因为环境、依赖、耗时或权限无法运行，必须明确说明原因。

## 内容生成要求

Goal 模式可以生成游戏内容，但默认只能进入候选链路：

```text
generated_candidates -> validated_candidates -> simulated_candidates -> playtest_candidates -> accepted_content
```

只有经过 Schema 校验、预算检查、Harness 仿真、Replay/回归检查和人工确认后，内容才可以进入正式内容池。

失败内容应保留拒绝原因，不得被静默删除。

## Git 要求

Goal 模式不改变 Git 规范：

- 操作前先看 `git status --short`。
- 不改与目标无关的文件。
- 不回滚用户或其他 Agent 的改动。
- 精确暂存相关文件。
- 提交信息使用中文，格式为 `<type>(<scope>): <描述>`。

如果 Goal 模式跨多个系统，应按文档、代码、内容、Harness、素材分别提交，避免把无关改动塞进一个提交。

## 证据一致性要求

Goal 模式长跑时，除了为具体功能运行对应测试，还要维护跨账本一致性。每当修改 `harness/progress.json`、`harness/docs_implementation_coverage.json`、`harness/roadmap_audit/roadmap_phase_audit.json`、`harness/release/current_local_rc_evidence.json` 或 `harness/release/current_local_package_manifest.json` 后，应运行：

```bash
python3 tools/validate_goal_evidence_consistency.py --repo-root .
```

如果需要留下可交接报告，应写入 `harness/reports/<report-id>/goal_evidence_consistency.json` 和对应 `summary.md`。该报告只证明账本之间没有互相矛盾；它不能替代编译、Harness、Replay、性能、人工试玩、素材审查、隐私审查、法律 / 合规审查或发布包 smoke。

当 Goal 长跑已经积累多个未完成项时，还应运行阻塞优先级审计，把宿主环境、人工证据、Release Candidate、发布包、docs 覆盖和 roadmap 状态排成下一步队列：

```bash
python3 tools/audit_goal_blockers.py \
  --repo-root . \
  --report harness/reports/<blocker-report>/goal_blocker_priority_audit.json \
  --markdown harness/reports/<blocker-report>/summary.md \
  --allow-blockers
```

该报告只负责排序和交接，不解决阻塞本身。若输出 `goal_blockers_present`，后续实现必须继续保持对应 docs、release 和 roadmap 状态为 partial / blocked，直到真实验证或真人证据补齐。
