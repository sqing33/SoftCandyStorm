# 内容数据 Schema 设计

## 目标

内容 Schema 是 AI 内容生成、Harness 校验、Bevy GameCore 加载、Python 训练环境读取之间的共同契约。

本项目所有正式内容都必须结构化。AI 可以生成候选内容，但必须符合 Schema，才能进入后续校验和仿真。

## 格式选择

首版推荐使用 JSON。

原因：

- AI 生成稳定。
- Python Gymnasium/SB3 读取方便。
- Rust 侧可用 `serde` 解析。
- JSON Schema 校验生态成熟。
- 便于 Harness 输出 diff 和错误报告。

后续如果 Bevy 资源系统需要，可以从 JSON 转换为 RON。

## 目录约定

```text
content/
  characters/
  weapons/
  passives/
  evolutions/
  enemies/
  bosses/
  waves/
  maps/
  events/

harness/
  generated_candidates/
  validated_candidates/
  simulated_candidates/
  accepted_content/
  rejected_content/
```

正式游戏只读取 `content/` 或 `accepted_content/` 中被版本锁定的内容。AI 新生成内容只能进入 `generated_candidates/`。

## 通用字段

所有内容对象都需要：

```json
{
  "id": "rainbow-candy-shot",
  "name": "彩虹糖弹",
  "version": 1,
  "rarity": "common",
  "tags": ["projectile", "starter"],
  "description": "向最近敌人发射彩色糖弹。",
  "visual_description": "小颗圆形彩虹糖，带白色高光和短拖尾。",
  "sfx_description": "轻快的 pop 声。",
  "unlock": {
    "type": "default"
  }
}
```

### id 规范

- 使用英文小写和短横线。
- 不使用中文、空格、下划线。
- 稳定后不要重命名。
- 重命名视为删除旧内容并新增新内容。

### rarity

允许值：

- `common`
- `rare`
- `epic`
- `legendary`
- `boss`
- `debug`

### tags

标签用于：

- AI 生成避免重复
- Bot 升级选择
- Harness 平衡分组
- 图鉴和 UI 筛选

常用标签：

- `projectile`
- `orbit`
- `aoe`
- `burst`
- `zone`
- `summon`
- `control`
- `defense`
- `boss-killer`
- `economy`
- `beginner`
- `high-risk`

## 角色 Schema

```json
{
  "id": "jar-keeper",
  "name": "糖罐守护员",
  "version": 1,
  "rarity": "common",
  "tags": ["balanced", "beginner"],
  "description": "新上任的糖罐守护员。",
  "base_stats": {
    "max_health": 120,
    "move_speed": 180,
    "pickup_radius": 72,
    "damage_multiplier": 1.0,
    "cooldown_multiplier": 1.0,
    "xp_multiplier": 1.0,
    "regen_per_second": 0.0
  },
  "initial_loadout": {
    "weapons": ["rainbow-candy-shot"],
    "passives": []
  },
  "trait": {
    "id": "sweet-starter",
    "description": "每 5 级额外获得少量糖晶。",
    "rules": []
  },
  "visual_description": "戴小糖罐帽的圆润守护员，颜色以奶白和粉色为主。",
  "sfx_description": "轻快脚步和糖罐轻响。",
  "unlock": {
    "type": "default"
  }
}
```

## 武器 Schema

```json
{
  "id": "rainbow-candy-shot",
  "name": "彩虹糖弹",
  "version": 1,
  "rarity": "common",
  "type": "projectile",
  "tags": ["projectile", "starter", "single-target"],
  "description": "向最近敌人发射彩色糖弹。",
  "targeting": {
    "mode": "nearest_enemy",
    "range": 420
  },
  "base_stats": {
    "damage": 14,
    "cooldown_ms": 620,
    "projectile_speed": 560,
    "projectile_count": 1,
    "pierce": 1,
    "area_radius": 14,
    "duration_ms": 0
  },
  "scaling": {
    "max_level": 5,
    "damage_per_level": 6,
    "cooldown_multiplier_per_level": 0.92,
    "range_per_level": 18,
    "area_per_level": 1,
    "projectile_count_bonus_levels": [3, 5]
  },
  "balance_budget": {
    "role": "starter",
    "single_target_dps": 20,
    "group_dps": 12,
    "performance_cost": "low"
  },
  "visual_description": "小颗圆形彩虹糖弹，命中时弹出糖屑。",
  "sfx_description": "清脆 pop 声。",
  "unlock": {
    "type": "default"
  }
}
```

### 武器 type

允许值：

- `projectile`
- `orbit`
- `burst`
- `zone`
- `summon`
- `beam`
- `special`

### targeting mode

允许值：

- `nearest_enemy`
- `highest_health_enemy`
- `boss_priority`
- `random_enemy`
- `random_direction`
- `movement_direction`
- `self_centered`
- `ground_near_player`

## 被动 Schema

```json
{
  "id": "big-candy-jar",
  "name": "大号糖罐",
  "version": 1,
  "rarity": "common",
  "tags": ["defense", "health"],
  "description": "提升最大生命。",
  "stat_modifiers": [
    {
      "stat": "max_health",
      "mode": "add",
      "value_per_level": 22
    }
  ],
  "max_level": 5,
  "visual_description": "胖胖的玻璃糖罐，装满发光糖晶。",
  "sfx_description": "玻璃罐轻响。",
  "unlock": {
    "type": "default"
  }
}
```

### stat

允许值：

- `max_health`
- `move_speed`
- `pickup_radius`
- `damage_multiplier`
- `cooldown_multiplier`
- `xp_multiplier`
- `regen_per_second`
- `damage_reduction`
- `projectile_size`
- `effect_duration`

### mode

允许值：

- `add`
- `multiply`
- `set_min`
- `set_max`

## 进化 Schema

```json
{
  "id": "rainbow-candy-meteor",
  "name": "彩虹糖流星雨",
  "version": 1,
  "rarity": "epic",
  "tags": ["projectile", "aoe", "evolution"],
  "description": "彩虹糖弹进化为周期性流星雨。",
  "requirements": {
    "weapon": {
      "id": "rainbow-candy-shot",
      "min_level": 5
    },
    "passive": {
      "id": "candy-crystal-lens",
      "min_level": 3
    },
    "trigger": "boss_chest"
  },
  "replaces_weapon": "rainbow-candy-shot",
  "weapon_definition": {
    "type": "burst",
    "targeting": {
      "mode": "random_enemy",
      "range": 620
    },
    "base_stats": {
      "damage": 42,
      "cooldown_ms": 900,
      "projectile_count": 8,
      "area_radius": 42
    }
  },
  "visual_description": "多颗彩虹糖从天空坠落，形成小型糖果爆炸。",
  "sfx_description": "连续 sparkle pop。",
  "unlock": {
    "type": "discover"
  }
}
```

## 敌人 Schema

```json
{
  "id": "bouncy-gummy",
  "name": "蹦蹦软糖",
  "version": 1,
  "family": "gummy",
  "rarity": "common",
  "tags": ["basic", "swarm"],
  "description": "最常见的小软糖，会直接追着守护员跑。",
  "stats": {
    "health": 18,
    "move_speed": 60,
    "contact_damage_per_second": 4.5,
    "radius": 13,
    "xp_value": 2,
    "score_value": 5
  },
  "behavior": {
    "type": "chase",
    "parameters": {}
  },
  "spawn_budget": {
    "threat": 1.0,
    "performance_cost": 1.0
  },
  "counterplay": "保持移动即可摆脱，适合用基础投射物清理。",
  "visual_description": "圆滚滚半透明软糖，有白色高光。",
  "death_effect": "弹开成几颗小糖屑。",
  "sfx_description": "软软的 boing 声。"
}
```

### enemy behavior

允许值：

- `chase`
- `dash`
- `split`
- `leave_hazard`
- `orbit_player`
- `jump`
- `ranged_spit`
- `shielded`

## Boss Schema

```json
{
  "id": "runaway-sugar-mixer",
  "name": "暴走搅糖机",
  "version": 1,
  "rarity": "boss",
  "tags": ["boss", "dash", "summon"],
  "description": "失控的搅糖机器，会一边冲撞一边甩出软糖。",
  "stats": {
    "health": 900,
    "move_speed": 38,
    "contact_damage_per_second": 20,
    "radius": 48,
    "xp_value": 80,
    "score_value": 500
  },
  "phases": [
    {
      "hp_threshold": 1.0,
      "abilities": ["dash_charge", "summon_bouncy_gummy"]
    },
    {
      "hp_threshold": 0.45,
      "abilities": ["dash_charge", "sugar_splash", "summon_bouncy_gummy"]
    }
  ],
  "counterplay": "冲撞前会出现红色预警线，冲撞后短暂硬直。",
  "visual_description": "圆滚滚的粉色搅糖机，带夸张搅拌臂。",
  "sfx_description": "机械搅拌声和糖浆飞溅声。"
}
```

## 波次 Schema

```json
{
  "id": "frosting-grassland-early",
  "name": "糖霜草地前期波次",
  "version": 1,
  "map_id": "frosting-grassland",
  "duration_seconds": 600,
  "segments": [
    {
      "start_second": 0,
      "end_second": 90,
      "spawn_interval_ms": 1250,
      "spawn_count": 1,
      "max_alive": 35,
      "enemy_pool": [
        {
          "enemy_id": "bouncy-gummy",
          "weight": 1.0
        }
      ]
    }
  ],
  "boss_events": [
    {
      "time_second": 210,
      "boss_id": "runaway-sugar-mixer"
    }
  ],
  "pressure_budget": {
    "early": "low",
    "middle": "medium",
    "late": "high"
  }
}
```

## 地图 Schema

```json
{
  "id": "frosting-grassland",
  "name": "糖霜草地",
  "version": 1,
  "tags": ["beginner", "open"],
  "description": "覆盖糖霜的开阔草地，新手守护员第一次面对软糖风暴的地方。",
  "size": {
    "width": 2600,
    "height": 1700
  },
  "bounds": {
    "type": "rectangle"
  },
  "spawn_rules": {
    "mode": "around_player",
    "min_distance": 320,
    "max_distance": 520
  },
  "hazards": [],
  "visual_description": "奶白糖霜草地、棒棒糖路标、饼干小路。",
  "music_theme": "bright_xylophone"
}
```

## 事件 Schema

```json
{
  "id": "rainbow-candy-rush",
  "name": "彩虹糖潮",
  "version": 1,
  "rarity": "rare",
  "tags": ["event", "risk-reward", "xp"],
  "description": "短时间内糖晶掉落增加，但敌人生成也会加快。",
  "trigger": {
    "type": "time_window",
    "start_second": 180,
    "end_second": 480,
    "chance": 0.08
  },
  "effects": [
    {
      "type": "xp_multiplier",
      "value": 1.4,
      "duration_seconds": 25
    },
    {
      "type": "spawn_rate_multiplier",
      "value": 1.25,
      "duration_seconds": 25
    }
  ],
  "visual_description": "天空落下彩虹糖晶，地面出现亮色糖光。",
  "sfx_description": "连续亮晶晶铃声。"
}
```

## Schema 校验规则

P0 错误，必须拒绝：

- JSON 无法解析
- id 不合法
- id 重复
- 引用不存在
- 必填字段缺失
- 数值为 NaN 或 Infinity
- 生命、冷却、速度、半径为负
- 波次结束时间小于开始时间
- 敌人池为空

P1 风险，需要仿真：

- 理论 DPS 超出同级 50%
- 波次压力明显高于目标区间
- 敌人速度和接触伤害组合过高
- 特效或投射物数量可能造成性能风险
- 新内容与已有内容主题重复

P2 人工审查：

- 名字是否好记
- 美术描述是否清楚
- 音效是否符合可爱糖果风
- 是否有明确反制
- 是否能形成有趣流派

## 独立 Schema 契约

仓库提供独立 JSON Schema 契约：

```text
content/schemas/
  manifest.json
  characters.schema.json
  weapons.schema.json
  passives.schema.json
  evolutions.schema.json
  enemies.schema.json
  bosses.schema.json
  maps.schema.json
  waves.schema.json
  events.schema.json
```

新增或修改正式内容、候选内容、Schema 字段或内容生成 Prompt 后，应先运行：

```bash
python3 tools/validate_content_schema_contract.py content/base_demo --schema-manifest content/schemas/manifest.json
```

验证候选完整内容包时，可同时传入多个内容目录：

```bash
python3 tools/validate_content_schema_contract.py content/base_demo harness/generated_candidates/<candidate-pack> --schema-manifest content/schemas/manifest.json
```

需要留下 Harness 证据时，生成 JSON 与 Markdown 报告：

```bash
python3 tools/validate_content_schema_contract.py content/base_demo harness/generated_candidates/<candidate-pack> --schema-manifest content/schemas/manifest.json --report harness/reports/<report-id>/content_schema_contract.json --markdown harness/reports/<report-id>/summary.md
```

该工具只覆盖 JSON Schema 契约子集、必填字段、枚举、id 规范和简单数值边界；它不替代 GameCore 内容加载、静态预算、Bot 仿真、Replay 回归或人工审查。
