# v25 Human Evidence TODOs

- Decision: `human_evidence_todos_pending`
- Design draft: `harness/content_review/drafts/2026-06-02_demo_buildcraft_repair_v25_full_pack_design_review_draft.json`
- Playtest draft: `harness/playtest/drafts/2026-06-02_demo_buildcraft_repair_v25_manual_playtest_review_draft.json`
- Design TODOs: `14`
- Playtest TODOs: `101`

## Design Review

### Top Level

- `$.reviewer`: TODO: human reviewer
- `$.reviewed_at`: TODO: YYYY-MM-DD
- `$.summary`: TODO: human reviewer must summarize theme fit, novelty, counterplay, readability, risks, and next gate.
- `$.batch_risks[0]`: TODO: list unresolved design, balance, theme, readability, or production risks.
- `$.next_actions[0]`: TODO: fill every rating with integer 1-5 and replace notes with concrete human observations.
- `$.next_actions[1]`: TODO: run harness/content_review/validate_content_candidate_design_review.py after the draft is fully reviewed.

### pudding-turret

- Type: `weapon`
- TODOs: `8`
- `$.content_reviews[0].theme_fit`: TODO: 1-5
- `$.content_reviews[0].novelty`: TODO: 1-5
- `$.content_reviews[0].build_potential`: TODO: 1-5
- `$.content_reviews[0].counterplay_clarity`: TODO: 1-5
- `$.content_reviews[0].visual_audio_fit`: TODO: 1-5
- `$.content_reviews[0].balance_risk`: TODO: low|medium|high
- `$.content_reviews[0].notes`: TODO: human reviewer must record concrete design observation before validation.
- `$.content_reviews[0].required_changes[0]`: TODO: record concrete revision, simulation concern, acceptance blocker, or rejection reason.

## Manual Playtest

### Top Level

- `$.reviewer`: TODO: human reviewer
- `$.summary`: TODO: human reviewer must summarize 9-run playtest findings and final acceptance decision.

### new_001

- Skill: `new`
- Intent: 不看说明直接开始
- TODOs: `11`
- Required observations:
  - 是否理解移动
  - 是否理解拾取糖晶
  - 是否理解升级三选一
- `$.runs[0].manual_review.fun_rating`: TODO: 1-5
- `$.runs[0].manual_review.clarity_rating`: TODO: 1-5
- `$.runs[0].manual_review.difficulty_rating`: TODO: 1-5
- `$.runs[0].manual_review.projectile_readability`: TODO: 1-5
- `$.runs[0].manual_review.hit_feedback`: TODO: 1-5
- `$.runs[0].manual_review.xp_pickup_rhythm`: TODO: 1-5
- `$.runs[0].manual_review.boss_spawn_clarity`: TODO: 1-5
- `$.runs[0].manual_review.death_reason_clarity`: TODO: 1-5
- `$.runs[0].manual_review.notes`: TODO: human reviewer must record concrete moment-to-moment observation.
- `$.runs[0].manual_review.tags[0]`: TODO: choose allowed tag
- `$.runs[0].manual_review.next_actions[0]`: TODO: record concrete code, content, balance, asset, or documentation action.

### new_002

- Skill: `new`
- Intent: 尝试贪 XP
- TODOs: `11`
- Required observations:
  - 是否知道为什么受伤
  - 如果死亡是否知道主要原因
  - XP 节奏是否诱导过度冒险
- `$.runs[1].manual_review.fun_rating`: TODO: 1-5
- `$.runs[1].manual_review.clarity_rating`: TODO: 1-5
- `$.runs[1].manual_review.difficulty_rating`: TODO: 1-5
- `$.runs[1].manual_review.projectile_readability`: TODO: 1-5
- `$.runs[1].manual_review.hit_feedback`: TODO: 1-5
- `$.runs[1].manual_review.xp_pickup_rhythm`: TODO: 1-5
- `$.runs[1].manual_review.boss_spawn_clarity`: TODO: 1-5
- `$.runs[1].manual_review.death_reason_clarity`: TODO: 1-5
- `$.runs[1].manual_review.notes`: TODO: human reviewer must record concrete moment-to-moment observation.
- `$.runs[1].manual_review.tags[0]`: TODO: choose allowed tag
- `$.runs[1].manual_review.next_actions[0]`: TODO: record concrete code, content, balance, asset, or documentation action.

### new_003

- Skill: `new`
- Intent: 保守绕圈
- TODOs: `11`
- Required observations:
  - 前 2 分钟是否至少看到 2-3 次升级机会
  - 保守玩法是否太无聊
  - 怪潮压力是否逐步增加
- `$.runs[2].manual_review.fun_rating`: TODO: 1-5
- `$.runs[2].manual_review.clarity_rating`: TODO: 1-5
- `$.runs[2].manual_review.difficulty_rating`: TODO: 1-5
- `$.runs[2].manual_review.projectile_readability`: TODO: 1-5
- `$.runs[2].manual_review.hit_feedback`: TODO: 1-5
- `$.runs[2].manual_review.xp_pickup_rhythm`: TODO: 1-5
- `$.runs[2].manual_review.boss_spawn_clarity`: TODO: 1-5
- `$.runs[2].manual_review.death_reason_clarity`: TODO: 1-5
- `$.runs[2].manual_review.notes`: TODO: human reviewer must record concrete moment-to-moment observation.
- `$.runs[2].manual_review.tags[0]`: TODO: choose allowed tag
- `$.runs[2].manual_review.next_actions[0]`: TODO: record concrete code, content, balance, asset, or documentation action.

### skilled_001

- Skill: `skilled`
- Intent: 主动拉怪收 XP
- TODOs: `11`
- Required observations:
  - 命中反馈是否清楚
  - XP 拾取是否顺畅
  - 升级选择是否有纠结
- `$.runs[3].manual_review.fun_rating`: TODO: 1-5
- `$.runs[3].manual_review.clarity_rating`: TODO: 1-5
- `$.runs[3].manual_review.difficulty_rating`: TODO: 1-5
- `$.runs[3].manual_review.projectile_readability`: TODO: 1-5
- `$.runs[3].manual_review.hit_feedback`: TODO: 1-5
- `$.runs[3].manual_review.xp_pickup_rhythm`: TODO: 1-5
- `$.runs[3].manual_review.boss_spawn_clarity`: TODO: 1-5
- `$.runs[3].manual_review.death_reason_clarity`: TODO: 1-5
- `$.runs[3].manual_review.notes`: TODO: human reviewer must record concrete moment-to-moment observation.
- `$.runs[3].manual_review.tags[0]`: TODO: choose allowed tag
- `$.runs[3].manual_review.next_actions[0]`: TODO: record concrete code, content, balance, asset, or documentation action.

### skilled_002

- Skill: `skilled`
- Intent: 主动挑战 Boss
- TODOs: `11`
- Required observations:
  - Boss 出场是否明显
  - Boss 威胁方向是否明确
  - Boss 战是否拖沓
- `$.runs[4].manual_review.fun_rating`: TODO: 1-5
- `$.runs[4].manual_review.clarity_rating`: TODO: 1-5
- `$.runs[4].manual_review.difficulty_rating`: TODO: 1-5
- `$.runs[4].manual_review.projectile_readability`: TODO: 1-5
- `$.runs[4].manual_review.hit_feedback`: TODO: 1-5
- `$.runs[4].manual_review.xp_pickup_rhythm`: TODO: 1-5
- `$.runs[4].manual_review.boss_spawn_clarity`: TODO: 1-5
- `$.runs[4].manual_review.death_reason_clarity`: TODO: 1-5
- `$.runs[4].manual_review.notes`: TODO: human reviewer must record concrete moment-to-moment observation.
- `$.runs[4].manual_review.tags[0]`: TODO: choose allowed tag
- `$.runs[4].manual_review.next_actions[0]`: TODO: record concrete code, content, balance, asset, or documentation action.

### skilled_003

- Skill: `skilled`
- Intent: 高压波次存活
- TODOs: `11`
- Required observations:
  - 屏幕压力是否压迫但不烦
  - 受伤反馈是否及时
  - 性能体感是否稳定
- `$.runs[5].manual_review.fun_rating`: TODO: 1-5
- `$.runs[5].manual_review.clarity_rating`: TODO: 1-5
- `$.runs[5].manual_review.difficulty_rating`: TODO: 1-5
- `$.runs[5].manual_review.projectile_readability`: TODO: 1-5
- `$.runs[5].manual_review.hit_feedback`: TODO: 1-5
- `$.runs[5].manual_review.xp_pickup_rhythm`: TODO: 1-5
- `$.runs[5].manual_review.boss_spawn_clarity`: TODO: 1-5
- `$.runs[5].manual_review.death_reason_clarity`: TODO: 1-5
- `$.runs[5].manual_review.notes`: TODO: human reviewer must record concrete moment-to-moment observation.
- `$.runs[5].manual_review.tags[0]`: TODO: choose allowed tag
- `$.runs[5].manual_review.next_actions[0]`: TODO: record concrete code, content, balance, asset, or documentation action.

### build_001

- Skill: `build`
- Intent: 远程投射物优先
- TODOs: `11`
- Required observations:
  - projectile 可读性
  - 单体输出反馈
  - 远程 Build 是否有明确优势和代价
- `$.runs[6].manual_review.fun_rating`: TODO: 1-5
- `$.runs[6].manual_review.clarity_rating`: TODO: 1-5
- `$.runs[6].manual_review.difficulty_rating`: TODO: 1-5
- `$.runs[6].manual_review.projectile_readability`: TODO: 1-5
- `$.runs[6].manual_review.hit_feedback`: TODO: 1-5
- `$.runs[6].manual_review.xp_pickup_rhythm`: TODO: 1-5
- `$.runs[6].manual_review.boss_spawn_clarity`: TODO: 1-5
- `$.runs[6].manual_review.death_reason_clarity`: TODO: 1-5
- `$.runs[6].manual_review.notes`: TODO: human reviewer must record concrete moment-to-moment observation.
- `$.runs[6].manual_review.tags[0]`: TODO: choose allowed tag
- `$.runs[6].manual_review.next_actions[0]`: TODO: record concrete code, content, balance, asset, or documentation action.

### build_002

- Skill: `build`
- Intent: 防御/移速优先
- TODOs: `11`
- Required observations:
  - 受伤反馈
  - 逃生空间
  - 容错感
- `$.runs[7].manual_review.fun_rating`: TODO: 1-5
- `$.runs[7].manual_review.clarity_rating`: TODO: 1-5
- `$.runs[7].manual_review.difficulty_rating`: TODO: 1-5
- `$.runs[7].manual_review.projectile_readability`: TODO: 1-5
- `$.runs[7].manual_review.hit_feedback`: TODO: 1-5
- `$.runs[7].manual_review.xp_pickup_rhythm`: TODO: 1-5
- `$.runs[7].manual_review.boss_spawn_clarity`: TODO: 1-5
- `$.runs[7].manual_review.death_reason_clarity`: TODO: 1-5
- `$.runs[7].manual_review.notes`: TODO: human reviewer must record concrete moment-to-moment observation.
- `$.runs[7].manual_review.tags[0]`: TODO: choose allowed tag
- `$.runs[7].manual_review.next_actions[0]`: TODO: record concrete code, content, balance, asset, or documentation action.

### build_003

- Skill: `build`
- Intent: 控制/范围优先
- TODOs: `11`
- Required observations:
  - 地面效果可读性
  - 敌群可读性
  - 性能体感
- `$.runs[8].manual_review.fun_rating`: TODO: 1-5
- `$.runs[8].manual_review.clarity_rating`: TODO: 1-5
- `$.runs[8].manual_review.difficulty_rating`: TODO: 1-5
- `$.runs[8].manual_review.projectile_readability`: TODO: 1-5
- `$.runs[8].manual_review.hit_feedback`: TODO: 1-5
- `$.runs[8].manual_review.xp_pickup_rhythm`: TODO: 1-5
- `$.runs[8].manual_review.boss_spawn_clarity`: TODO: 1-5
- `$.runs[8].manual_review.death_reason_clarity`: TODO: 1-5
- `$.runs[8].manual_review.notes`: TODO: human reviewer must record concrete moment-to-moment observation.
- `$.runs[8].manual_review.tags[0]`: TODO: choose allowed tag
- `$.runs[8].manual_review.next_actions[0]`: TODO: record concrete code, content, balance, asset, or documentation action.

## Next Actions

- Fill every TODO field with concrete human observations before strict validation.
- Keep AI-generated content in generated_candidates until design review and manual playtest evidence pass.

## Limitations

- This report lists TODO fields only.
- It does not fill human evidence, validate ratings, run the game, judge fun, or promote content.
