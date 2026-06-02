# v25 可玩内容覆盖审计

- Candidate id: `2026-06-02_demo_buildcraft_repair_v25_full_pack`
- Content hash: `fnv1a64:aab110776109609d`
- Content dir: `harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack`
- Decision: `v25_playable_content_coverage_needs_content_repair`
- Action items: `5`
- Build routes: `13`
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

| Priority | Category | Item | Affected | Evidence | Action |
|---|---|---|---|---|---|
| `P1` | `character_starter` | `character_starter_without_evolution_bubble-courier` | bubble-courier, soda-bubble-pop | starter weapons without evolution=['soda-bubble-pop'] | 为该初始武器补一条进化路线，或明确改成短期无进化的候选风险并安排试玩验证。 |
| `P1` | `character_starter` | `character_starter_without_evolution_sour-plum-doctor` | sour-plum-doctor, sour-plum-spray | starter weapons without evolution=['sour-plum-spray'] | 为该初始武器补一条进化路线，或明确改成短期无进化的候选风险并安排试玩验证。 |
| `P2` | `build_routes` | `passives_without_evolution_usage` | cocoa-safety-badge, honey-heart, jelly-lens-polish, peppermint-pocket-watch | passives without evolution usage=['cocoa-safety-badge', 'honey-heart', 'jelly-lens-polish', 'peppermint-pocket-watch'] | 判断这些被动是否只是数值补强，还是需要绑定新进化以提高升级选择纠结感。 |
| `P2` | `build_routes` | `weapons_without_evolution_routes` | candy-crystal-lance, mint-cyclone, soda-bubble-pop, sour-plum-spray | weapons without evolution=['candy-crystal-lance', 'mint-cyclone', 'soda-bubble-pop', 'sour-plum-spray'] | 评估这些武器是否应补进化，尤其是玩家初始武器和主要流派入口。 |
| `P2` | `playable_descriptors` | `passives_missing_playable_descriptors` | big-candy-jar.balance_budget, bubble-shoes.balance_budget, candy-crystal-lens.balance_budget, cocoa-safety-badge.balance_budget, crackling-sugar-fuse.balance_budget, cream-clockwork.balance_budget, frosting-gloves.balance_budget, frosty-straw.balance_budget, honey-heart.balance_budget, jelly-lens-polish.balance_budget, marshmallow-vest.balance_budget, nonstick-apron.balance_budget, peppermint-pocket-watch.balance_budget, rhythm-ribbon.balance_budget, sour-tuner.balance_budget, star-spoon.balance_budget, taffy-pocket-map.balance_budget | missing fields=['big-candy-jar.balance_budget', 'bubble-shoes.balance_budget', 'candy-crystal-lens.balance_budget', 'cocoa-safety-badge.balance_budget', 'crackling-sugar-fuse.balance_budget', 'cream-clockwork.balance_budget', 'frosting-gloves.balance_budget', 'frosty-straw.balance_budget', 'honey-heart.balance_budget', 'jelly-lens-polish.balance_budget', 'marshmallow-vest.balance_budget', 'nonstick-apron.balance_budget', 'peppermint-pocket-watch.balance_budget', 'rhythm-ribbon.balance_budget', 'sour-tuner.balance_budget', 'star-spoon.balance_budget', 'taffy-pocket-map.balance_budget'] | 补齐描述、视觉、音效、预算或需求字段，方便人工试玩前理解内容身份。 |

## 错误

- None

## 限制

- 这份审计只检查玩家可触达内容表面是否覆盖完整，不运行 Runtime、不判断乐趣、不接受候选。
- 发现缺口只能进入 repair/playtest 讨论，不能绕过 Schema、Harness、人工审查和 lockfile。
- v25 仍是 generated candidate，不能复制到 content/base_demo、accepted_content 或 Runtime 正式内容目录。
- AI/RL 训练线不在本审计范围内。
