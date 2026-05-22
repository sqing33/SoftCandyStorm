---
name: soft-candy-harness-reviewer
description: 当需要审查、验证、评分或推进《软糖风暴》的内容或代码经过 Harness 流水线时使用：Schema 检查、静态预算、Bot 矩阵、Replay 回归、失败复盘、门禁决策和报告。
---

# 软糖风暴 Harness 审查

用于判断《软糖风暴》的内容、代码、Bot 行为、平衡改动或生成素材能否进入下一阶段。

## 必读文档

审查前读取：

1. `AGENTS.md`
2. `docs/07_Harness工程计划.md`
3. `docs/10_AI内容生成流水线.md`
4. `docs/11_测试指标与上线门禁.md`
5. `docs/13_内容数据Schema设计.md`
6. `docs/15_经济与数值平衡模型.md`

如果涉及 Bot、RL 或 Replay，再读：

- `docs/08_Bot测试计划.md`
- `docs/09_AI_Bot训练计划.md`
- `docs/16_Replay与遥测设计.md`

## 审查阶段

按顺序执行：

1. Schema 与引用检查。
2. 静态预算审查。
3. Bot 仿真预期。
4. Replay 回归预期。
5. 性能和实体数量风险。
6. 主题、可读性、美术、音效审查。
7. 人工试玩建议。

不要因为后续阶段看起来不错，就跳过前置门禁。

## 门禁结论

使用以下结论之一：

- `reject`：拒绝推进，说明原因。
- `repair`：有潜力但需要修复，给出具体修改。
- `simulate`：静态检查通过，应进入 Bot/Harness 仿真。
- `playtest`：仿真预期通过，建议人工试玩。
- `accept_candidate`：可进入候选接受池，但不等于最终发布。

## 最小审查输出

必须返回：

- 门禁结论
- 被审查的 item id
- 已通过检查
- 未通过检查
- 具体风险
- 下一步验证
- 如果适用，failure case 条目

审查生成内容时，必须说明是否具备：

- 合法 Schema 字段
- tags
- balance budget
- visual description
- sound description
- counterplay

## 失败复盘规则

任何 bug、平衡失败、Bot exploit、RL 异常或 Replay 回归失败，都需要 failure case。

推荐字段：

```json
{
  "case_id": "fail_YYYYMMDD_NNN",
  "category": "balance",
  "content_id": "example-id",
  "seed": 12345,
  "bot": "KiteBot",
  "time_seconds": 87.4,
  "symptom": "发生了什么",
  "root_cause": "为什么发生",
  "fix": "修改了什么或应该修改什么",
  "validation": "如何验证"
}
```

## 禁止事项

- 不要因为内容有创意就放行。
- 不要放行绕过 GameCore 或 Harness 规则的代码。
- 不要降低门禁来让内容通过。
- 不要把 RL Bot 成功当成好玩的证明。
- 不要把人工觉得好玩当成技术安全的证明。

