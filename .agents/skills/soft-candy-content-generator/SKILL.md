---
name: soft-candy-content-generator
description: 当需要为《软糖风暴》生成或修改内容时使用：武器、被动、进化、敌人、Boss、波次、地图、角色、事件、图鉴文本、美术描述、音效描述或内容包候选。
---

# 软糖风暴内容生成

用于生成或修改《软糖风暴》的游戏内容。所有生成内容默认都是候选内容，不是正式内容。

## 必读文档

生成内容前读取：

1. `AGENTS.md`
2. `docs/04_内容系统与素材库.md`
3. `docs/10_AI内容生成流水线.md`
4. `docs/13_内容数据Schema设计.md`
5. `docs/15_经济与数值平衡模型.md`

如果涉及美术或音效 Prompt，再读：

- `docs/05_美术与音频素材计划.md`
- `docs/17_素材生成Prompt库.md`

## 输出位置规则

生成内容只能进入候选流程：

```text
generated_candidates -> validated_candidates -> simulated_candidates -> playtest_candidates -> accepted_content
```

除非用户在 Harness 审查后明确要求定稿，否则不要把生成内容描述为正式内容或最终内容。

## 必填信息

每个内容对象必须包含：

- 稳定的 kebab-case `id`
- `name`
- `version`
- `rarity`
- `tags`
- `description`
- 游戏类型或分类
- 数值或规则
- `balance_budget`
- `visual_description`
- `sfx_description`
- 反制方式或弱点
- 解锁或发现条件

如果一个想法没有明确预算、视觉身份和反制方式，只能作为概念，不应作为 Schema-ready 内容。

## 工作流程

1. 判断内容类型：角色、武器、被动、进化、敌人、Boss、波次、地图或事件。
2. 阅读 `docs/13_内容数据Schema设计.md` 中对应 Schema。
3. 对照 `docs/04_内容系统与素材库.md`，避免主题重复。
4. 先确定角色定位和 tags，再写数值。
5. 补充预算和反制方式。
6. 输出 JSON-like 候选内容和简短设计说明。
7. 如果需要写文件，只写入用户批准的候选目录或项目已定义的候选目录。

## 平衡护栏

- 初始武器要可靠，但不能统治全局。
- 进化武器可以明显更强，但必须有条件。
- 快速敌人不能同时拥有高接触伤害，除非有清晰反制。
- Boss 至少要有一个可读机制，不能只是血厚。
- 波次必须有时间段、敌人池、生成限制和压力预算。
- 除非用户明确要求探索新风格，否则必须保持可爱糖果主题。

## 禁止事项

- 不得绕过 Schema 或 Harness 门禁。
- 不得写入正式内容池。
- 不得生成暗黑科幻、恐怖、血腥或写实暴力内容。
- 不得输出缺少 tags 和预算的内容。
- 不得为了让内容通过而放宽平衡门禁。

