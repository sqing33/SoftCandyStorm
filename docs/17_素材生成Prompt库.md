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

### Runtime 俯视角玩家与 Boss 出场音频

批次路径：

```text
asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/
```

该批次来自 `harness/asset_review/mmx_asset_generation_plan_template.json`，生成前计划报告为：

```text
harness/reports/2026-05-26_mmx_asset_generation_plan_template_001/summary.md
```

生成内容：

- `player_jar_keeper_topdown_v005_001`、`player_jar_keeper_topdown_v005_002`：玩家糖罐守护者俯视角 sprite 候选，包含原图、透明 PNG 后处理和 128/64/32 小尺寸预览。
- `voice_boss_arrival_cn_v002`：中文 Boss 出场提示语音候选，文本为“警报！裂星糖罐核心苏醒了！”。计划声线 `Chinese_female_news_anchor` 不存在，实际使用 `Chinese (Mandarin)_News_Anchor`。
- `sting_boss_arrival_v002_source`：Boss 出场音乐源候选，约 72.9 秒，只能作为剪辑来源。
- `sting_boss_arrival_v002_trim8s`：从音乐源剪出的 8 秒 Boss 出场 sting 候选，仍需人工听感、响度和语音叠放审查。
- `boss_arrival_voice_sting_mix_v001`：Boss 语音叠放 8 秒 sting 的听感预览候选，已记录 loudnorm 探测值，仍需人工确认语音清晰度和混音比例。

已生成 strict metadata 报告：

```text
harness/reports/2026-05-26_mmx_runtime_topdown_audio_plan_metadata_001/summary.md
```

已生成覆盖全部 6 个素材 id 的人工审查草稿：

```text
harness/asset_review/drafts/2026-05-26_mmx_runtime_topdown_audio_plan_review_draft.json
```

已生成真人审查包：

```text
harness/reports/2026-05-26_mmx_runtime_topdown_audio_review_packet_001/summary.md
```

草稿校验报告当前为 `asset_candidate_manual_review_invalid`，原因是 TODO 评分尚未由真人填写；这正是预期状态，不能作为人工通过证据。

结论：该批次全部仍在 `generated_candidates`，不得直接进入正式 Runtime 素材。

### 升级反馈图标、TTS 与 jingle

批次路径：

```text
asset/generated_candidates/2026-05-26_mmx_level_up_feedback_pack/
```

该批次来自独立生成前计划：

```text
harness/asset_review/mmx_level_up_feedback_plan.json
```

计划报告：

```text
harness/reports/2026-05-26_mmx_level_up_feedback_plan_001/summary.md
```

生成内容：

- `ui_level_up_spark_icon_v001_001`：升级反馈 UI 图标候选，包含原图、透明 PNG 后处理和 128/64/32 小尺寸预览。
- `voice_level_up_cn_v001`：中文升级提示语音候选，文本为“糖晶能量升级完成！选择新的糖果魔法吧！”，仍需人工确认是否太长、是否适合频繁升级触发。
- `jingle_level_up_v001_source`：升级 jingle 音乐源候选，约 78.2 秒，只能作为剪辑来源。
- `jingle_level_up_v001_trim3s`：从音乐源剪出的 3.2 秒升级 jingle 候选，仍需人工听感、响度和重复触发疲劳审查。

已生成 strict metadata 报告：

```text
harness/reports/2026-05-26_mmx_level_up_feedback_pack_metadata_001/summary.md
```

已生成覆盖全部 4 个素材 id 的人工审查草稿：

```text
harness/asset_review/drafts/2026-05-26_mmx_level_up_feedback_pack_review_draft.json
```

已生成真人审查包：

```text
harness/reports/2026-05-26_mmx_level_up_feedback_review_packet_001/summary.md
```

草稿校验报告当前为 `asset_candidate_manual_review_invalid`，原因是 TODO 评分尚未由真人填写；这正是预期状态，不能作为人工通过证据。

结论：该批次全部仍在 `generated_candidates`，不得直接进入正式 Runtime 素材。

## 生图后处理流程

1. 生成图片。
2. 保存到项目素材候选目录。
3. 如果是 chroma-key 背景，做抠图。
4. 检查透明边缘。
5. 裁切 spritesheet。
6. 生成 manifest。
7. 放入 `asset/generated_candidates`。
8. 通过人工审查、Runtime preview、听感 / 响度和最终接受门禁后，才能进入 accepted asset 内容池。

## mmx 生成前计划门禁

任何新的 `mmx image generate`、`mmx speech synthesize` 或 `mmx music generate` 作业，先写入生成计划：

```text
harness/asset_review/mmx_asset_generation_plan_template.json
```

并运行：

```bash
python3 harness/asset_review/validate_mmx_asset_generation_plan.py \
  harness/asset_review/mmx_asset_generation_plan_template.json \
  --repo-root . \
  --report harness/reports/<plan-report>/mmx_asset_generation_plan.json \
  --markdown harness/reports/<plan-report>/summary.md
```

生成计划必须明确：

- 目标批次路径只能是 `asset/generated_candidates/<batch>/`。
- `project_rules.candidate_only=true`，且 `accepted_content=false`、`runtime_integrated=false`、`release_ready=false`。
- 每条 `mmx` 命令必须使用 `--output json --non-interactive --quiet`，并记录输出路径。
- 命令不得内联 API key，不得把媒体流直接写 stdout。
- 计划必须列出 `tools/validate_asset_candidates.py --require-commands` 和人工审查草稿生成命令。

当前示例计划报告：

```text
harness/reports/2026-05-26_mmx_asset_generation_plan_template_001/summary.md
```

该报告结论为 `mmx_asset_generation_plan_valid`，只证明后续生成作业的目录、命令和审查链路计划有效；它不代表素材已经生成、通过 metadata 校验、通过人工审查或可以进入 Runtime。

## 候选素材 Metadata 校验

每个 `asset/generated_candidates/<batch>/metadata/manifest.json` 都必须证明该批次仍是候选素材，而不是正式接入内容。

推荐在生成或后处理后运行：

```bash
python3 tools/validate_asset_candidates.py asset/generated_candidates/<batch> \
  --report /tmp/asset_candidate_validation.json \
  --markdown /tmp/asset_candidate_validation.md
```

新 `mmx` 批次应额外使用：

```bash
python3 tools/validate_asset_candidates.py asset/generated_candidates/<batch> \
  --require-commands
```

历史批次如果原始 shell history 不可追溯，只能补记由 manifest prompt 和输出路径重建的命令模板，并必须在 `command_provenance.status` 中标明 `reconstructed_from_manifest` 或类似状态，不能把重建命令伪装成原始命令。

校验范围：

- `project_rules.candidate_only` 必须为 `true`。
- `project_rules.accepted_content` 必须为 `false`。
- `project_rules.runtime_integrated` 必须为 `false`。
- 素材路径、预览路径和后处理 manifest 必须能解析到真实文件。
- 每个素材要有 `qa_status`、`qa_notes`，并记录 prompt、source 或 postprocess provenance。
- 新 `mmx` 批次必须记录实际生成命令，避免后续无法复现。

该校验只检查来源与候选池纪律，不替代人工美术、听感或小尺寸可读性审查。

## 候选音频技术探针

含 TTS、music、SFX 的素材候选批次可以额外运行：

```bash
python3 harness/asset_review/audit_asset_audio_technical.py \
  asset/generated_candidates/<batch-or-root> \
  --report harness/reports/<report-id>/asset_audio_technical_probe.json \
  --markdown harness/reports/<report-id>/summary.md
```

该探针使用 `ffprobe` 或 Python `wave` 读取本地音频文件，核对 manifest 中的 `duration_seconds`、`sample_rate_hz` 和 `channels`，并列出每个音频候选的实际时长、采样率和声道数。

当前全量候选报告：

```text
harness/reports/2026-05-26_asset_audio_technical_probe_001/summary.md
```

报告结论为 `asset_audio_technical_probe_valid`，覆盖 `asset/generated_candidates` 下 9 个候选批次的 14 个音频文件。它只证明文件存在和技术 metadata 没有明显漂移，不能替代人工听感、响度、循环疲劳、Runtime preview、final human acceptance、accepted_content 或 release gate。

## 候选素材人工审查

metadata 校验通过后，素材仍不能直接接入正式目录。人工审查记录应使用：

```text
harness/asset_review/asset_candidate_manual_review_template.json
```

也可以从 manifest 生成覆盖所有素材 id 的审查草稿：

```bash
python3 harness/asset_review/create_asset_candidate_review_draft.py \
  asset/generated_candidates/<batch> \
  --repo-root . \
  --metadata-report harness/reports/<asset-validation-report>/summary.md \
  --out harness/asset_review/drafts/<batch>_review_draft.json
```

草稿只用于防止漏审，不能替代真人听感、美术、小尺寸和授权审查。草稿里的 `TODO` 必须由真人替换后，才能进入人工审查校验。

并通过：

```bash
python3 harness/asset_review/validate_asset_candidate_manual_review.py \
  harness/asset_review/<review-file>.json \
  --repo-root . \
  --report /tmp/asset_manual_review.json \
  --markdown /tmp/asset_manual_review.md
```

如果真人审查结论为 `asset_candidate`，再运行：

```bash
python3 harness/asset_review/promote_asset_runtime_candidate.py \
  harness/asset_review/<review-file>.json \
  --repo-root . \
  --out-dir harness/asset_review/runtime_candidates \
  --report /tmp/asset_runtime_candidate.json \
  --markdown /tmp/asset_runtime_candidate.md
```

晋级工具只复制候选批次、人工审查记录并写入 `runtime_candidate_manifest.json`。它不会写入正式素材目录，不会标记 `runtime_integrated`，也不会替代 Runtime 预览、听感 / 响度审查或最终人工接受。

生成 Runtime 候选后还必须运行：

```bash
python3 harness/asset_review/validate_asset_runtime_candidate_manifest.py \
  harness/asset_review/runtime_candidates/<batch>/runtime_candidate_manifest.json \
  --repo-root . \
  --report /tmp/asset_runtime_candidate_manifest.json \
  --markdown /tmp/asset_runtime_candidate_manifest.md
```

该校验要求 manifest 绑定有效 `asset_candidate` 人工审查、源候选 metadata 报告、源候选 `metadata/manifest.json`、每个素材的 id/type/path/qa_status 与允许候选用途，并确认 `accepted_content=false`、`runtime_integrated=false`、`release_ready=false`。

Runtime 可以用以下参数读取该 manifest 的安全元数据：

```bash
game_runtime --asset-runtime-candidate-manifest \
  harness/asset_review/runtime_candidates/<batch>/runtime_candidate_manifest.json
```

该入口只在 `F1` 概览显示候选批次、素材数量、类型统计和 `asset_candidate` 待预览状态。它不会读取候选图片、音频或正文文件，不替换正式 Runtime 素材，也不会把候选标记为 `accepted_content`、`runtime_integrated` 或 `release_ready`；缺少 Runtime preview、音频响度审查或最终人工接受要求的 manifest 会被拒绝。

Runtime 候选后的三类人工证据必须独立落盘并分别校验：

```bash
python3 harness/asset_review/validate_asset_runtime_preview_review.py \
  harness/asset_review/runtime_preview_reviews/<review>.json \
  --repo-root . \
  --report /tmp/asset_runtime_preview_review.json \
  --markdown /tmp/asset_runtime_preview_review.md

python3 harness/asset_review/validate_asset_audio_loudness_review.py \
  harness/asset_review/audio_loudness_reviews/<review>.json \
  --repo-root . \
  --report /tmp/asset_audio_loudness_review.json \
  --markdown /tmp/asset_audio_loudness_review.md

python3 harness/asset_review/validate_asset_final_acceptance.py \
  harness/asset_review/final_acceptance/<review>.json \
  --repo-root . \
  --report /tmp/asset_final_acceptance.json \
  --markdown /tmp/asset_final_acceptance.md
```

对应模板为 `asset_runtime_preview_review_template.json`、`asset_audio_loudness_review_template.json` 和 `asset_final_acceptance_template.json`。模板保留 TODO 时必须输出 invalid；通过也只代表人工接受证据完整，不代表 Runtime 已加载素材或发布包 ready。

若 Runtime preview、音频响度 / 听感审查和最终人工接受全部完成，再运行：

```bash
python3 harness/asset_review/create_asset_acceptance_review_packet.py \
  harness/asset_review/accepted/<batch>/acceptance_manifest.json \
  --repo-root . \
  --report /tmp/asset_acceptance_review_packet.json \
  --markdown /tmp/asset_acceptance_review_packet.md
```

该审查包会列出 `source_runtime_candidate_manifest`、`runtime_preview_review_file`、`audio_loudness_review_file` 和 `final_human_acceptance_file` 的存在状态、预期 review type / decision 和必填检查项。它只帮助真人补齐证据，不会让 manifest 通过。

```bash
python3 harness/asset_review/validate_asset_acceptance_manifest.py \
  harness/asset_review/accepted/<batch>/acceptance_manifest.json \
  --repo-root . \
  --report /tmp/asset_acceptance_manifest.json \
  --markdown /tmp/asset_acceptance_manifest.md
```

该 manifest 允许记录 `accepted_content=true`，但必须同时保持 `runtime_integrated=false`、`release_ready=false`、`generated_candidate_direct_acceptance_allowed=false`。它不会把素材复制进 Runtime，不证明发布包 ready，也不能替代小尺寸实机预览、听感复核、授权复核或最终 smoke。

审查结论允许：

- `needs_more_review`：信息不足，继续人工检查。
- `repair`：有潜力，但需要抠图、裁切、重剪、响度或重生成。
- `asset_candidate`：可作为后续 Runtime/UI 接入候选，但仍不是正式素材。
- `reject`：拒绝推进，并保留原因。

禁止把人工审查记录写成 `accepted_content`、`runtime_integrated` 或 `release_ready`。正式接入还需要 Runtime 预览、听感 / 小尺寸验证、来源记录和发布前人工确认。

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
