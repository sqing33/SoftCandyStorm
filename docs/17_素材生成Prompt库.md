# 素材生成 Prompt 库

## 目标

本文件保存《软糖风暴》的 AI 生图、生音效、生文案提示词规范。它不是一次性灵感文档，而是后续素材 Agent 的工作协议。

## 总体视觉关键词

```text
cute candy roguelite, soft gummy candy, jelly texture, rounded shapes, bright pastel colors, high contrast outline, top-down game asset, readable at small size, cheerful but action-ready
```

中文概念：

- 可爱
- 糖果
- 软糖
- 果冻
- 泡泡
- 棉花糖
- 焦糖
- 圆润
- 高辨识度
- 小尺寸可读
- 明亮但不刺眼

## 通用负面约束

```text
no text, no watermark, no logo, no realistic gore, no horror, no dark sci-fi, no thin fragile details, no busy background, no shadows crossing sprite boundaries
```

中文约束：

- 不要文字
- 不要水印
- 不要恐怖血腥
- 不要复杂背景
- 不要过细轮廓
- 不要暗黑科幻
- 不要让阴影跨过格子边界

## Spritesheet 通用 Prompt

```text
Create a clean top-down 2D game spritesheet for a cute candy roguelite game.
Theme: soft gummy candy storm, jelly monsters, candy weapons, pastel fantasy.
Style: rounded cartoon shapes, high contrast outline, readable at 32-64px, consistent lighting, cheerful action game style.
Layout: isolated sprites in a clear grid, each sprite centered in its own cell with generous padding.
Background: perfectly flat solid #00ff00 chroma-key background for removal.
Constraints: no text, no labels, no watermark, no shadows crossing cells, no overlapping sprites.
```

## 主角 Prompt

```text
Top-down cute game character sprite, a trainee candy jar keeper, small rounded body, tiny candy jar hat, cream white and soft pink palette, cheerful determined expression, simple readable silhouette, high contrast outline, isolated on flat #00ff00 background, no text.
```

动作帧补充：

```text
Create 4-direction walking animation frames: idle, step left, step right, hit reaction. Keep the same character design and proportions in every frame.
```

## 普通敌人 Prompt

### 蹦蹦软糖

```text
Cute top-down gummy monster sprite, round translucent jelly body, tiny feet, happy chaotic expression, pastel green and pink variants, readable silhouette, high contrast outline, isolated on flat #00ff00 background, no text.
```

### 酸酸软糖

```text
Cute sour gummy monster sprite, small fast-looking yellow jelly body, sour sugar crystals on surface, tiny sharp corners, playful mischievous face, high contrast outline, isolated on flat #00ff00 background, no text.
```

### 粘粘熊糖

```text
Cute gummy bear enemy sprite, soft bear ears, sticky jelly texture, orange-pink candy body, looks clingy but not scary, top-down game asset, high contrast outline, isolated on flat #00ff00 background, no text.
```

### 夹心饼怪

```text
Cute sandwich cookie monster sprite, chunky round-square cookie body with cream filling, slow tank enemy, small candy eyes, readable top-down silhouette, high contrast outline, isolated on flat #00ff00 background, no text.
```

### 汽水泡泡

```text
Cute soda bubble enemy sprite, translucent blue bubble body, fizzy highlights, tiny face inside, fragile and bouncy, top-down game asset, high contrast outline, isolated on flat #00ff00 background, no text.
```

### 焦糖史莱姆

```text
Cute caramel slime enemy sprite, glossy brown-orange sticky body, small dripping trail, soft rounded shape, mischievous face, readable top-down game sprite, high contrast outline, isolated on flat #00ff00 background, no text.
```

## Boss Prompt

### 暴走搅糖机

```text
Cute but imposing top-down boss sprite, runaway candy mixer machine, round pink body, spinning sugar arms, candy splashes, toy-like design, not scary, high contrast outline, readable at 128px, isolated on flat #00ff00 background, no text.
```

### 巨型熊糖王

```text
Large cute gummy bear king boss sprite, translucent red and gold jelly body, tiny crown made of sugar crystals, heavy rounded silhouette, playful but powerful, top-down game asset, high contrast outline, isolated on flat #00ff00 background, no text.
```

### 裂星糖罐核心

```text
Final boss sprite for cute candy roguelite, cracked magical candy jar star core, rainbow syrup leaking, floating crystal jar, beautiful and unstable, pastel rainbow glow, top-down readable boss asset, isolated on flat #00ff00 background, no text.
```

## 武器图标 Prompt

通用：

```text
Square game ability icon, cute candy roguelite style, centered object, rounded cartoon shape, high contrast outline, simple readable design, pastel colors, no text, no watermark.
```

### 彩虹糖弹

```text
Square ability icon of a rainbow candy projectile with a sparkling trail, cute candy roguelite style, centered, high contrast outline, no text.
```

### 棉花糖护盾

```text
Square ability icon of three fluffy marshmallow orbs forming a protective circle, cute candy roguelite style, centered, no text.
```

### 汽水喷泉

```text
Square ability icon of a fizzy soda fountain burst with blue bubbles and candy sparkles, cute candy roguelite style, no text.
```

### 焦糖黏地

```text
Square ability icon of glossy caramel puddle swirl, sticky but cute, orange brown candy colors, no text.
```

## 地图背景 Prompt

### 糖霜草地

```text
Top-down seamless game map tile background, frosting grassland in a cute candy world, cream sugar grass, lollipop signs, cookie path pieces, pastel colors, clean readable ground, no characters, no text.
```

### 汽水溪谷

```text
Top-down cute candy world map background, soda creek valley with fizzy blue streams, lemon slice stones, bubble fountains, pastel colors, clean readable ground, no characters, no text.
```

### 焦糖工坊

```text
Top-down cute candy factory map background, caramel workshop, round copper pots, syrup pipes, cookie floor tiles, warm orange candy palette, readable gameplay floor, no characters, no text.
```

## UI Prompt

### 升级卡牌

```text
Cute candy game UI card frame, rounded rectangular candy wrapper style, pastel cream base, colorful rarity border, empty center for icon and text, no actual text, clean readable mobile-friendly design.
```

### Boss 血条

```text
Cute candy game boss health bar UI, candy jar frame, syrup fill, rounded glossy style, no text, transparent or flat background.
```

## 音效 Prompt 模板

如果使用音频生成工具：

```text
Short cute game sound effect, candy pop, bright and playful, 0.2 seconds, no voice, no music bed, clean transient.
```

常用音效：

- 糖弹发射：`short candy pop projectile sound`
- 泡泡破裂：`soft bubble pop`
- 升级：`sparkly candy level up chime`
- 受击：`soft jelly hit squish`
- Boss 出场：`playful but dramatic candy machine rumble`
- 胜利：`bright candy jar magical success jingle`

## 当前 mmx 候选批次记录

### 地图选择与 Boss 出场音频

批次路径：

```text
asset/generated_candidates/2026-05-26_mmx_map_boss_audio_pass/
```

生成内容：

- `map_select_background_v001`：16:9 地图选择背景候选，仍需人工检查伪文字、地标可读性和地图卡牌覆盖效果。
- `voice_boss_arrival_v001`：中文 Boss 出场提示语音候选，文本为“警报！裂星糖罐核心苏醒了！”，仍需人工听感和响度审查。
- `sting_boss_arrival_v001`：Boss 出场音乐原始候选，约 102 秒，只能作为剪辑来源。
- `sting_boss_arrival_v001_trim8s`：从原始音乐剪出的 8 秒 Boss 出场 sting 候选，仍需人工听感、响度和语音叠放审查。

结论：该批次全部仍在 `generated_candidates`，不得直接进入正式 Runtime 素材。

## 生图后处理流程

1. 生成图片。
2. 保存到项目素材候选目录。
3. 如果是 chroma-key 背景，做抠图。
4. 检查透明边缘。
5. 裁切 spritesheet。
6. 生成 manifest。
7. 放入 `asset/generated_candidates`。
8. 人工选择后进入正式素材目录。

## 素材命名规范

```text
asset_type/content_id/version.ext
```

示例：

```text
sprites/enemy_bouncy_gummy/v001.png
sprites/boss_runaway_sugar_mixer/v001.png
icons/weapon_rainbow_candy_shot/v001.png
```

## Prompt 版本管理

每个正式素材要记录：

- prompt
- negative prompt
- 生成日期
- 选择原因
- 后处理脚本
- 对应内容 id

不要只保存图片，不保存生成来源。
