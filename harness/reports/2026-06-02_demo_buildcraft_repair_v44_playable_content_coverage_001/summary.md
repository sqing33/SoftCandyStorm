# v25 可玩内容覆盖审计

- Candidate id: `2026-06-02_demo_buildcraft_repair_v25_full_pack`
- Content hash: `fnv1a64:aab110776109609d`
- Content dir: `harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v44_full_pack`
- Decision: `v25_playable_content_coverage_ready_for_human_playtest`
- Action items: `0`
- Build routes: `17`
- Quick-play presets: `6`
- Content-tour runs: `6`

## 覆盖摘要

- Characters: `5`
- Maps: `6`
- Expected build roles: `aoe-clear, boss-killer, control, defense, economy, starter, summon`
- Actual build roles: `aoe-clear, boss-killer, control, defense, economy, pierce-clear, starter, summon`
- Quick-play characters: `bubble-courier, cream-knight, jar-keeper, pudding-crafter, sour-plum-doctor`
- Quick-play maps: `caramel-workshop, cotton-cloud-pasture, cracked-star-jar, frosting-grassland, jelly-platform, soda-creek`
- Content-tour characters: `bubble-courier, cream-knight, jar-keeper, pudding-crafter, sour-plum-doctor`
- Content-tour maps: `caramel-workshop, cotton-cloud-pasture, cracked-star-jar, frosting-grassland, jelly-platform, soda-creek`

## 修复项

- 当前没有自动覆盖审计发现的内容缺口；下一步仍需要人工试玩和设计审查。

## 错误

- None

## 限制

- 这份审计只检查玩家可触达内容表面是否覆盖完整，不运行 Runtime、不判断乐趣、不接受候选。
- 发现缺口只能进入 repair/playtest 讨论，不能绕过 Schema、Harness、人工审查和 lockfile。
- v25 仍是 generated candidate，不能复制到 content/base_demo、accepted_content 或 Runtime 正式内容目录。
- AI/RL 训练线不在本审计范围内。
