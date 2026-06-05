# v61 Human Evidence TODOs

- Candidate id: `2026-06-05_demo_buildcraft_repair_v61_full_pack`
- Content hash: `fnv1a64:66fa99c902f3af87`
- Decision: `human_evidence_todos_pending`
- Design draft: `harness/content_review/drafts/2026-06-05_demo_buildcraft_repair_v61_full_pack_design_review_draft.json`
- Playtest draft: `harness/playtest/drafts/2026-06-05_demo_buildcraft_repair_v61_manual_playtest_review_draft.json`
- Design TODOs: `14`
- Playtest TODOs: `68`

## Design Review

### Top Level

- `$.reviewer`: TODO: human reviewer
- `$.reviewed_at`: TODO: YYYY-MM-DD
- `$.summary`: TODO: human reviewer must summarize theme fit, novelty, counterplay, readability, risks, and next gate.
- `$.batch_risks[0]`: TODO: list unresolved design, balance, theme, readability, or production risks.
- `$.next_actions[0]`: TODO: fill every rating with integer 1-5 and replace notes with concrete human observations.
- `$.next_actions[1]`: TODO: run harness/content_review/validate_content_candidate_design_review.py after the draft is fully reviewed.

### route-memory-caramel-ring

- Type: `event`
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
- `$.summary`: TODO: human reviewer must summarize current-candidate playtest findings and final decision.

### new_frosting_jar_keeper

- Skill: `new`
- Intent: 不看说明直接开局，确认新手是否理解移动、拾取糖晶和第一次升级
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
- `$.runs[0].manual_review.tags[0]`: TODO: choose tags such as fun, unclear, too_easy, too_hard, readable, confusing
- `$.runs[0].manual_review.next_actions[0]`: TODO: record concrete code, content, balance, asset, or documentation action.

### speed_soda_bubble_courier

- Skill: `skilled`
- Intent: 主动利用速度穿插收 XP，确认泡泡邮差和汽水溪谷的移动压力
- TODOs: `11`
- Required observations:
  - 移动优势是否明显
  - 泡泡敌人压力是否清楚
  - 贪 XP 后是否知道受伤原因
- `$.runs[1].manual_review.fun_rating`: TODO: 1-5
- `$.runs[1].manual_review.clarity_rating`: TODO: 1-5
- `$.runs[1].manual_review.difficulty_rating`: TODO: 1-5
- `$.runs[1].manual_review.projectile_readability`: TODO: 1-5
- `$.runs[1].manual_review.hit_feedback`: TODO: 1-5
- `$.runs[1].manual_review.xp_pickup_rhythm`: TODO: 1-5
- `$.runs[1].manual_review.boss_spawn_clarity`: TODO: 1-5
- `$.runs[1].manual_review.death_reason_clarity`: TODO: 1-5
- `$.runs[1].manual_review.notes`: TODO: human reviewer must record concrete moment-to-moment observation.
- `$.runs[1].manual_review.tags[0]`: TODO: choose tags such as fun, unclear, too_easy, too_hard, readable, confusing
- `$.runs[1].manual_review.next_actions[0]`: TODO: record concrete code, content, balance, asset, or documentation action.

### summon_cotton_pudding_crafter

- Skill: `build`
- Intent: 优先召唤和经济构筑，确认布丁工匠在群体压力下是否有成型目标
- TODOs: `11`
- Required observations:
  - 召唤物反馈是否清楚
  - 经济构筑是否有成长感
  - 棉花云敌群是否可读
- `$.runs[2].manual_review.fun_rating`: TODO: 1-5
- `$.runs[2].manual_review.clarity_rating`: TODO: 1-5
- `$.runs[2].manual_review.difficulty_rating`: TODO: 1-5
- `$.runs[2].manual_review.projectile_readability`: TODO: 1-5
- `$.runs[2].manual_review.hit_feedback`: TODO: 1-5
- `$.runs[2].manual_review.xp_pickup_rhythm`: TODO: 1-5
- `$.runs[2].manual_review.boss_spawn_clarity`: TODO: 1-5
- `$.runs[2].manual_review.death_reason_clarity`: TODO: 1-5
- `$.runs[2].manual_review.notes`: TODO: human reviewer must record concrete moment-to-moment observation.
- `$.runs[2].manual_review.tags[0]`: TODO: choose tags such as fun, unclear, too_easy, too_hard, readable, confusing
- `$.runs[2].manual_review.next_actions[0]`: TODO: record concrete code, content, balance, asset, or documentation action.

### control_caramel_sour_plum_doctor

- Skill: `skilled`
- Intent: 优先控场和减速路线，确认焦糖工坊路线干扰是否有趣而不烦
- TODOs: `11`
- Required observations:
  - 控场效果是否看得懂
  - 路线干扰是否公平
  - 后半段压力是否过度
- `$.runs[3].manual_review.fun_rating`: TODO: 1-5
- `$.runs[3].manual_review.clarity_rating`: TODO: 1-5
- `$.runs[3].manual_review.difficulty_rating`: TODO: 1-5
- `$.runs[3].manual_review.projectile_readability`: TODO: 1-5
- `$.runs[3].manual_review.hit_feedback`: TODO: 1-5
- `$.runs[3].manual_review.xp_pickup_rhythm`: TODO: 1-5
- `$.runs[3].manual_review.boss_spawn_clarity`: TODO: 1-5
- `$.runs[3].manual_review.death_reason_clarity`: TODO: 1-5
- `$.runs[3].manual_review.notes`: TODO: human reviewer must record concrete moment-to-moment observation.
- `$.runs[3].manual_review.tags[0]`: TODO: choose tags such as fun, unclear, too_easy, too_hard, readable, confusing
- `$.runs[3].manual_review.next_actions[0]`: TODO: record concrete code, content, balance, asset, or documentation action.

### defense_jelly_cream_knight

- Skill: `build`
- Intent: 优先防御和近身容错，确认奶油骑士在环形路线中的受伤反馈
- TODOs: `11`
- Required observations:
  - 防御成长是否能感受到
  - 近身受伤反馈是否及时
  - 果冻月台路线是否清晰
- `$.runs[4].manual_review.fun_rating`: TODO: 1-5
- `$.runs[4].manual_review.clarity_rating`: TODO: 1-5
- `$.runs[4].manual_review.difficulty_rating`: TODO: 1-5
- `$.runs[4].manual_review.projectile_readability`: TODO: 1-5
- `$.runs[4].manual_review.hit_feedback`: TODO: 1-5
- `$.runs[4].manual_review.xp_pickup_rhythm`: TODO: 1-5
- `$.runs[4].manual_review.boss_spawn_clarity`: TODO: 1-5
- `$.runs[4].manual_review.death_reason_clarity`: TODO: 1-5
- `$.runs[4].manual_review.notes`: TODO: human reviewer must record concrete moment-to-moment observation.
- `$.runs[4].manual_review.tags[0]`: TODO: choose tags such as fun, unclear, too_easy, too_hard, readable, confusing
- `$.runs[4].manual_review.next_actions[0]`: TODO: record concrete code, content, balance, asset, or documentation action.

### final_cracked_jar_keeper

- Skill: `skilled`
- Intent: 挑战最终地图混合怪潮，确认首发包终局压力、Boss 出场和死亡原因
- TODOs: `11`
- Required observations:
  - Boss 出场是否明显
  - 混合怪潮是否可读
  - 死亡或胜利原因是否清楚
- `$.runs[5].manual_review.fun_rating`: TODO: 1-5
- `$.runs[5].manual_review.clarity_rating`: TODO: 1-5
- `$.runs[5].manual_review.difficulty_rating`: TODO: 1-5
- `$.runs[5].manual_review.projectile_readability`: TODO: 1-5
- `$.runs[5].manual_review.hit_feedback`: TODO: 1-5
- `$.runs[5].manual_review.xp_pickup_rhythm`: TODO: 1-5
- `$.runs[5].manual_review.boss_spawn_clarity`: TODO: 1-5
- `$.runs[5].manual_review.death_reason_clarity`: TODO: 1-5
- `$.runs[5].manual_review.notes`: TODO: human reviewer must record concrete moment-to-moment observation.
- `$.runs[5].manual_review.tags[0]`: TODO: choose tags such as fun, unclear, too_easy, too_hard, readable, confusing
- `$.runs[5].manual_review.next_actions[0]`: TODO: record concrete code, content, balance, asset, or documentation action.

## Next Actions

- Fill every TODO field with concrete human observations before strict validation.
- Keep current candidate content in generated_candidates until design review and manual playtest evidence pass.

## Limitations

- This report lists TODO fields only.
- It does not fill human evidence, validate ratings, run the game, judge fun, or promote content.
