# Replay 与遥测设计

## 目标

Replay 和遥测用于把真人试玩、Bot 测试、RL 评估连接起来。

它们回答：

- 玩家为什么死？
- 新版本是否破坏旧体验？
- 哪些武器没人选？
- 哪些波次导致大量失败？
- AI 生成内容是否带来异常表现？

## Replay 定义

Replay 不是录屏，而是可复现的输入和状态记录。

Replay 应能在同版本内容和规则下重现一局。

## Replay 文件内容

必须记录：

- replay_version
- game_version
- ruleset_version
- content_hash
- run_config
- tick_rate
- action_stream
- upgrade_choices
- final_metrics

可选记录：

- event_checkpoints
- periodic_snapshots
- rng_checkpoints
- player_notes
- crash_info

## RunConfig 记录

```json
{
  "seed": 12345,
  "map_id": "frosting-grassland",
  "character_id": "jar-keeper",
  "difficulty": "normal",
  "duration_seconds": 600,
  "content_pack_ids": ["base-demo"]
}
```

## Action Stream

为了压缩，动作可以按 tick 或按变化记录。

按变化记录：

```json
[
  {
    "tick": 0,
    "movement": [0, 0]
  },
  {
    "tick": 12,
    "movement": [1, 0]
  },
  {
    "tick": 45,
    "movement": [0.7, -0.7]
  }
]
```

升级选择：

```json
[
  {
    "tick": 1260,
    "options": ["rainbow-candy-shot", "big-candy-jar", "soda-fountain"],
    "chosen_index": 2,
    "chosen_id": "soda-fountain"
  }
]
```

## Replay 回放策略

回放时可能出现内容变化导致选项不同。

模式：

- strict：选项不一致即失败。
- compatible：按 chosen_id 查找。
- tag_fallback：按标签相似度选择替代。

回归测试使用 strict 或 compatible。跨版本分析可用 tag_fallback。

## Replay 用途

### Bug 复现

记录导致崩溃、卡死、异常数值的 replay。

### 人工试玩回归

保存典型人类局：

- 新手失败
- 熟练胜利
- 贪经验失败
- Boss 击杀
- 防御流
- 远程流
- 控制流

### Bot 对比

Bot replay 可用于分析策略缺陷。

### RL 训练

后续可以用真人 replay 做模仿学习或 reward shaping 参考。

## 遥测事件

局内事件：

- run_start
- run_end
- level_up
- upgrade_chosen
- weapon_fired
- enemy_killed
- player_damaged
- boss_spawned
- boss_phase_changed
- boss_killed
- evolution_unlocked
- fps_sample

## 遥测字段

事件通用字段：

- timestamp
- run_id
- session_id，匿名
- game_version
- content_hash
- map_id
- character_id
- difficulty
- elapsed_seconds

不要记录：

- 个人身份信息
- 文件路径
- IP 地址，除非平台服务自动处理且隐私政策说明
- 用户输入的自由文本，除非明确授权

## 本地优先策略

开发阶段优先本地保存：

```text
harness/replay/
harness/telemetry/local/
```

上线前再决定是否接匿名遥测。

## 版本对比

每次内容或数值改动后，对 replay 进行对比：

- 死亡时间差异
- 等级差异
- 伤害来源差异
- Boss 击杀时间差异
- 武器伤害占比差异
- 是否从胜利变失败
- 是否从失败变胜利

明显差异不一定是 bug，但必须可解释。

## Replay 门禁

P0：

- Replay 无法解析
- Replay 回放 panic
- 同版本 strict replay 无法重现

P1：

- 代表性 replay 大量从胜利变失败
- 新手 replay 前 2 分钟死亡率显著上升
- Boss replay 出现不可躲攻击

## 人工反馈结构

真人试玩后记录：

```json
{
  "replay_id": "human_2026_001",
  "player_skill": "new",
  "fun_rating": 4,
  "clarity_rating": 3,
  "difficulty_rating": 4,
  "notes": "升级选择很有趣，但焦糖地面看不清。",
  "tags": ["visual-clarity", "difficulty"]
}
```

人工评分不用于直接门禁，但用于 AI 内容修正输入。

## 遥测隐私

如果未来上线遥测：

- 默认匿名。
- 提供关闭选项。
- 写清用途：平衡、崩溃分析、玩法改进。
- 不上传 replay 原始输入，除非玩家同意。
- 不上传个人身份信息。

当前隐私策略模板与校验器位于：

```text
harness/telemetry_privacy/telemetry_privacy_policy_template.json
harness/telemetry_privacy/validate_telemetry_privacy_policy.py
```

该策略门禁要求：

- 上传型遥测默认关闭。
- 上传和 raw replay 上传都必须有明确同意。
- 使用匿名 session id，不采集个人身份、IP、文件路径或自由文本。
- `allowed_event_fields` 不能包含禁止字段或 replay 原始输入。
- 本地数据需要有保留天数、删除和导出控制项。
- 发布前仍需要人工隐私审查、Runtime 设置开关、隐私说明文本和 Release Candidate 证据。

当前校验命令：

```bash
python3 harness/telemetry_privacy/validate_telemetry_privacy_policy.py \
  harness/telemetry_privacy/telemetry_privacy_policy_template.json \
  --report harness/reports/2026-05-26_telemetry_privacy_policy_001/telemetry_privacy_policy.json \
  --markdown harness/reports/2026-05-26_telemetry_privacy_policy_001/summary.md
```
