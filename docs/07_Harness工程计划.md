# Harness 工程计划

## Harness 定义

本项目中的 Harness 不是传统测试框架，而是围绕 AI Agent 和游戏内容生产建立的工程系统。

它负责：

- 给 AI Agent 提供稳定上下文
- 限制 AI 修改范围
- 自动校验生成内容
- 批量模拟游戏局
- 收集平衡指标
- 阻止坏内容进入正式池
- 记录失败案例
- 让下一轮 AI 生成更好

## Harness 的核心目标

### 1. 防止 AI 把游戏改坏

AI 可以高频生成内容，但必须经过：

- 编译
- schema 校验
- 静态预算
- Bot 仿真
- 性能门禁
- replay 回归

### 2. 让内容扩展变成循环

```text
AI 生成候选内容
  -> Harness 校验
  -> Bot 批量测试
  -> 生成报告
  -> AI 修正
  -> 人工挑选
  -> 进入正式内容池
```

### 3. 保存项目记忆

AI 不应该依赖聊天历史。所有关键知识放到仓库：

- AGENTS.md
- docs/
- harness/progress.json
- harness/failed_cases/
- harness/reports/
- content schema
- replay 数据

## Agent 分工

### 研究 Agent

职责：

- 阅读代码
- 分析系统
- 找到实现位置
- 输出方案

权限：

- 只读

### 内容 Agent

职责：

- 生成武器
- 生成敌人
- 生成波次
- 生成地图事件
- 生成图鉴文本

权限：

- 只能写候选内容目录

### 平衡 Agent

职责：

- 读取 Harness 报告
- 调整数值
- 修正过强/过弱内容

权限：

- 写候选内容和调参建议

### 代码 Agent

职责：

- 实现明确功能
- 修复测试失败
- 重构 game_core

权限：

- 限定模块写入

### 审查 Agent

职责：

- 检查实现
- 找 bug
- 找缺测试
- 标记风险

权限：

- 只读 + 写审查报告

### 清理 Agent

职责：

- 清理重复内容
- 检查文档过期
- 删除无用候选
- 降低 AI slop

权限：

- 写清理 PR 或清理报告

## 仓库知识结构

```text
AGENTS.md
docs/
  design/
  systems/
  bot/
  ai_training/
harness/
  progress.json
  feature_list.json
  reports/
  failed_cases/
  replay/
  generated_candidates/
  accepted_content/
  rejected_content/
```

## 内容门禁

### P0 门禁：必须通过

- 编译通过
- schema 校验通过
- 引用存在
- id 唯一
- 无 NaN/无限数值
- 无负冷却
- 无负生命
- 无无法结束的局
- 无性能上限爆炸

### P1 门禁：强平衡

- 前 2 分钟死亡率不能过高
- 10 分钟胜率要在目标区间
- Boss 击杀率要在目标区间
- 武器选择率不能极端失衡
- 单个 Build 不能碾压全部内容
- IdleBot 不能轻松获胜
- 高级 Bot 不能发现无限资源漏洞

### P2 门禁：体验质量

- 内容主题清楚
- 图标可读
- 特效不遮挡
- 音效不刺耳
- 文案符合世界观
- 新内容与现有内容不重复

P2 可以人工判断。

## 关键指标

### 生存指标

- 平均存活时间
- 中位存活时间
- 前 2 分钟死亡率
- 5 分钟存活率
- 10 分钟胜率

### 战斗指标

- 击杀数
- DPS 曲线
- 武器伤害占比
- Boss 击杀时间
- 接触伤害次数
- 受伤来源

### 成长指标

- 平均等级
- 升级频率
- 经验拾取率
- 选项池多样性
- 进化达成率

### 压力指标

- 同屏敌人数
- 敌人生成速率
- 地面危险区数量
- 玩家可通行空间
- FPS/帧耗时

### 内容指标

- 武器选择率
- 被动选择率
- Build 分布
- 内容重复度
- 内容通过率

## 报告格式

每次 Harness run 输出：

```text
reports/
  2026-xx-xx_batch_x/
    summary.md
    metrics.json
    accepted.json
    rejected.json
    failure_cases.json
    representative_replays/
```

summary.md 内容：

- 本批候选数量
- 通过数量
- 拒绝数量
- 主要拒绝原因
- 最强内容
- 最弱内容
- 性能风险
- 推荐人工试玩内容
- 推荐 AI 修正任务

## 失败案例沉淀

每次出现失败，需要记录：

- 失败内容 id
- seed
- bot 类型
- 时间点
- 指标
- 截图或 replay
- 失败原因
- 修正建议

例子：

```json
{
  "case_id": "fail_wave_042",
  "content_id": "wave-caramel-overflow",
  "seed": 9182,
  "bot": "reflex",
  "time": 87.4,
  "reason": "enemy_density_spike",
  "notes": "Crawler and slime spawn weights combine into unavoidable contact damage before level 3."
}
```

## Agent 工作循环

每次 Agent 开始：

1. 读取 AGENTS.md。
2. 读取 docs 索引。
3. 读取 feature_list。
4. 读取最近 progress。
5. 选择一个任务。
6. 做最小完整改动。
7. 运行对应测试。
8. 更新 progress。
9. 如果失败，写失败案例。

## 不允许的 Agent 行为

- 直接把候选内容写入正式内容池。
- 绕过门禁。
- 同时大改多个系统。
- 修改核心逻辑但不更新测试。
- 修改数值但不跑模拟。
- 只看胜率不看体验指标。
- 让 DQN 结果替代人工乐趣判断。

## Harness 成熟度路线

### Level 1

- 文档
- 内容 schema
- 基础单元测试
- 手动模拟命令

### Level 2

- 批量 Bot 仿真
- 自动报告
- 内容门禁
- replay 保存

### Level 3

- 多 Agent 分工
- AI 内容生成闭环
- 失败自动归因
- 候选内容自动修正

### Level 4

- RL Bot 参与压力测试
- 自动平衡建议
- 每日内容批处理
- 自动生成候选更新包

### Level 5

- 上线遥测回流
- 玩家行为聚类
- 内容推荐生成
- 长期自动运营辅助

