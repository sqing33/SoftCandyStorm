# v51 可玩内容导览

- Candidate id: `2026-06-04_demo_buildcraft_repair_v51_full_pack`
- Content hash: `fnv1a64:50bd536bd0669e2b`
- Content dir: `harness/generated_candidates/2026-06-04_demo_buildcraft_repair_v51_full_pack`
- Decision: `playable_content_guide_candidate_only`
- Candidate only: `True`
- Accepted content: `False`
- Runtime integrated: `False`

## 内容数量

| 类型 | 当前数量 | Demo 目标 | 达标 |
|---|---:|---:|---|
| `characters` | 5 | 1 | `True` |
| `maps` | 6 | 1 | `True` |
| `weapons` | 17 | 12 | `True` |
| `passives` | 17 | 8 | `True` |
| `enemies` | 12 | 12 | `True` |
| `bosses` | 6 | 3 | `True` |
| `waves` | 6 | 1 | `True` |
| `evolutions` | 17 | - | - |
| `events` | 5 | - | - |

## 快速试玩入口

- `python3 harness/playtest/play_current_candidate.py --dry-run`
- `python3 harness/playtest/play_current_candidate.py`
- `python3 harness/playtest/play_current_candidate.py --list`

| Preset | Character | Map | Seed | Focus | Launcher |
|---|---|---|---:|---|---|
| `default` | `jar-keeper` | `frosting-grassland` | 55101 | 糖罐守护员和糖霜草地基准体验 | `python3 harness/playtest/play_current_candidate.py default` |
| `speed` | `bubble-courier` | `soda-creek` | 55102 | 泡泡邮差和汽水溪谷移动压力 | `python3 harness/playtest/play_current_candidate.py speed` |
| `summon` | `pudding-crafter` | `cotton-cloud-pasture` | 55103 | 布丁工匠和棉花云群体压力 | `python3 harness/playtest/play_current_candidate.py summon` |
| `control` | `sour-plum-doctor` | `caramel-workshop` | 55104 | 酸梅博士和焦糖工坊路线干扰 | `python3 harness/playtest/play_current_candidate.py control` |
| `defense` | `cream-knight` | `jelly-platform` | 55105 | 奶油骑士和果冻月台环形路线 | `python3 harness/playtest/play_current_candidate.py defense` |
| `final` | `jar-keeper` | `cracked-star-jar` | 55106 | 裂星糖罐混合怪潮压力 | `python3 harness/playtest/play_current_candidate.py final` |

## 角色 / 地图巡游入口

- `python3 harness/playtest/run_current_content_tour.py --list`
- `python3 harness/playtest/run_current_content_tour.py --next --dry-run`
- `python3 harness/playtest/run_current_content_tour.py --next`

| Run | Character | Map | Seed | Focus | Launcher |
|---|---|---|---:|---|---|
| `frosting_jar_keeper` | `jar-keeper` | `frosting-grassland` | 55201 | 新手基准角色和糖霜草地开局 | `python3 harness/playtest/run_current_content_tour.py frosting_jar_keeper` |
| `soda_bubble_courier` | `bubble-courier` | `soda-creek` | 55202 | 速度角色和汽水溪谷泡泡压力 | `python3 harness/playtest/run_current_content_tour.py soda_bubble_courier` |
| `cotton_pudding_crafter` | `pudding-crafter` | `cotton-cloud-pasture` | 55203 | 召唤角色和棉花云群体压力 | `python3 harness/playtest/run_current_content_tour.py cotton_pudding_crafter` |
| `caramel_sour_plum_doctor` | `sour-plum-doctor` | `caramel-workshop` | 55204 | 控制角色和焦糖工坊路线干扰 | `python3 harness/playtest/run_current_content_tour.py caramel_sour_plum_doctor` |
| `jelly_cream_knight` | `cream-knight` | `jelly-platform` | 55205 | 防御角色和果冻月台环形路线 | `python3 harness/playtest/run_current_content_tour.py jelly_cream_knight` |
| `cracked_jar_keeper` | `jar-keeper` | `cracked-star-jar` | 55206 | 最终地图混合怪潮压力 | `python3 harness/playtest/run_current_content_tour.py cracked_jar_keeper` |

## 角色入口

| 角色 | 标签 | 初始武器 | 初始被动 | 特性 |
|---|---|---|---|---|
| 泡泡邮差 (`bubble-courier`) | mobility, pickup, intermediate | 汽水泡泡 (`soda-bubble-pop`) | - | 移动后短时间提升拾取范围。 |
| 奶油骑士 (`cream-knight`) | defense, beginner, close | 棉花糖护盾 (`marshmallow-shield`) | - | 受击后获得短暂减伤。 |
| 糖罐守护员 (`jar-keeper`) | balanced, beginner | 彩虹糖弹 (`rainbow-candy-shot`) | - | 每 5 级额外获得少量糖晶。 |
| 布丁工匠 (`pudding-crafter`) | summon, area-control, intermediate | 布丁炮台 (`pudding-turret`) | - | 召唤物持续时间增加。 |
| 酸梅博士 (`sour-plum-doctor`) | control, boss-safe, advanced | 酸梅喷雾 (`sour-plum-spray`) | - | 减速效果增强。 |

## 构筑路线

| 进化 | 基础武器 | 搭配被动 | 触发 | 角色定位 | 说明 |
|---|---|---|---|---|---|
| 焦糖漩涡 (`caramel-vortex`) | 焦糖黏地 (`caramel-sticky-ground`) Lv.5 | 酸味调节器 (`sour-tuner`) Lv.3 | `boss_chest` | `control / slow, zone, control, evolution` | 焦糖黏地进化为更大的焦糖漩涡，长期封锁危险路线。 |
| 可可护徽晶枪 (`cocoa-guard-crystal-lance`) | 糖晶长枪 (`candy-crystal-lance`) Lv.5 | 可可安全徽章 (`cocoa-safety-badge`) Lv.3 | `boss_chest` | `boss-killer / projectile, boss-killer, pierce, defense, evolution` | 糖晶长枪进化为带可可护徽轨迹的双段晶枪，保持 Boss 单体压力，同时给防御流一个清晰输出终点。 |
| 汽泡终场烟花 (`fizzy-grand-finale`) | 汽泡引线糖 (`fizzy-fuse-pop`) Lv.5 | 跳跳糖引线 (`crackling-sugar-fuse`) Lv.3 | `boss_chest` | `aoe-clear / burst, high-risk, aoe, boss-killer, evolution` | 汽泡引线糖进化为终场烟花，爆发范围更大但节奏仍有空窗。 |
| 蜂蜜薄荷舒心风 (`honey-mint-comfort-storm`) | 薄荷旋风 (`mint-cyclone`) Lv.5 | 蜂蜜糖心 (`honey-heart`) Lv.3 | `boss_chest` | `control / control, orbit, recovery, defense, evolution` | 薄荷旋风进化为更宽的蜂蜜薄荷风圈，帮助近身防御流缓解怪潮推进，但仍需要走位维持安全距离。 |
| 宝藏果豆星环 (`jellybean-treasure-orbit`) | 果豆磁环 (`jellybean-magnet`) Lv.5 | 太妃口袋地图 (`taffy-pocket-map`) Lv.3 | `boss_chest` | `economy / orbit, economy, evolution` | 果豆磁环进化为宝藏星环，稳定清理靠近的敌人。 |
| 棉花堡垒 (`marshmallow-fortress`) | 棉花糖护盾 (`marshmallow-shield`) Lv.5 | 大号糖罐 (`big-candy-jar`) Lv.3 | `boss_chest` | `defense / defense, orbit, evolution` | 棉花糖护盾进化为持续护城环，扩大近身安全区。 |
| 跳跳糖连锁反应 (`popping-candy-chain-reaction`) | 跳跳糖地雷 (`popping-candy-mine`) Lv.5 | 星星勺子 (`star-spoon`) Lv.3 | `boss_chest` | `aoe-clear / trap, burst, evolution` | 跳跳糖地雷进化为连锁爆点，在守护员附近连续爆裂。 |
| 布丁要塞 (`pudding-bastion`) | 布丁炮台 (`pudding-turret`) Lv.5 | 防粘围裙 (`nonstick-apron`) Lv.3 | `boss_chest` | `summon / summon, turret, evolution` | 布丁炮台进化为布丁要塞，生成多点自动火力。 |
| 彩虹糖流星雨 (`rainbow-candy-meteor`) | 彩虹糖弹 (`rainbow-candy-shot`) Lv.5 | 糖晶放大镜 (`candy-crystal-lens`) Lv.3 | `boss_chest` | `starter / projectile, aoe, evolution` | 彩虹糖弹进化为周期性流星雨。 |
| 雪花糖暴风 (`snowcone-blizzard`) | 雪花糖扇 (`snowcone-fan`) Lv.5 | 冰霜吸管 (`frosty-straw`) Lv.3 | `boss_chest` | `control / zone, control, slow, evolution` | 雪花糖扇进化为更持久的暴风控制区。 |
| 汽泡怀表巡游 (`soda-bubble-clock-parade`) | 汽水泡泡 (`soda-bubble-pop`) Lv.5 | 薄荷怀表 (`peppermint-pocket-watch`) Lv.3 | `boss_chest` | `starter / starter, projectile, bubble, timing, evolution` | 汽水泡泡进化为按节拍排队出发的泡泡巡游，移动角色能更稳定地清理身侧小怪。 |
| 汽水火山 (`soda-volcano`) | 汽水喷泉 (`soda-fountain`) Lv.5 | 泡泡鞋 (`bubble-shoes`) Lv.3 | `boss_chest` | `aoe-clear / aoe, burst, evolution` | 汽水喷泉进化为连续喷发的汽水火山，覆盖更大敌群。 |
| 酸梅诊疗云 (`sour-plum-clinic-cloud`) | 酸梅喷雾 (`sour-plum-spray`) Lv.5 | 果冻镜片油 (`jelly-lens-polish`) Lv.3 | `boss_chest` | `control / starter, control, slow, zone, evolution` | 酸梅喷雾进化为更大的诊疗云团，持续压慢怪潮并让控场路线在 Boss 前后更稳定。 |
| 星糖棱镜 (`star-sugar-prism`) | 星糖射线 (`star-sugar-ray`) Lv.5 | 糖霜手套 (`frosting-gloves`) Lv.3 | `boss_chest` | `boss-killer / beam, boss-killer, evolution` | 星糖射线进化为棱镜折射光束，同时锁定多个高血目标。 |
| 糖鼓终曲 (`sugar-drum-crescendo`) | 糖鼓 (`sugar-drum`) Lv.5 | 节拍丝带 (`rhythm-ribbon`) Lv.3 | `boss_chest` | `aoe-clear / burst, aoe, rhythm, evolution` | 糖鼓进化为连续扩散的终曲糖波。 |
| 旋糖风车 (`sugar-windmill`) | 棒棒糖回旋镖 (`lollipop-boomerang`) Lv.5 | 奶油发条 (`cream-clockwork`) Lv.3 | `boss_chest` | `pierce-clear / boomerang, pierce, evolution` | 棒棒糖回旋镖进化为旋糖风车，长时间切穿敌群。 |
| 威化城墙护轨 (`wafer-castle-rail`) | 威化护轨 (`wafer-guard-rail`) Lv.5 | 棉花糖背心 (`marshmallow-vest`) Lv.3 | `boss_chest` | `defense / orbit, defense, evolution` | 威化护轨进化为城墙式护轨，强化贴身保护。 |

## 地图与波次身份

| 地图 | 时长 | 段数 | Boss | 开局敌人 | 终局敌人 |
|---|---:|---:|---|---|---|
| 焦糖工坊 (`caramel-workshop`) | 600 | 5 | 焦糖熔炉 (`caramel-furnace`) @ 210s | 蹦蹦软糖 (`bouncy-gummy`), 焦糖史莱姆 (`caramel-slime`) | 焦糖史莱姆 (`caramel-slime`), 夹心饼怪 (`sandwich-cookie-creep`), 辣味软糖 (`spicy-gummy`), 汽水泡泡 (`soda-bubble`), 粘粘熊糖 (`sticky-bear-gummy`), 酸酸软糖 (`sour-gummy`), 蹦蹦软糖 (`bouncy-gummy`), 甘草跳跳 (`licorice-skipper`), 太妃盾糖 (`taffy-shieldling`), 糖针吐吐 (`sprinkle-spitter`) |
| 棉花云牧场 (`cotton-cloud-pasture`) | 600 | 5 | 巨型棉花团 (`giant-cotton-clump`) @ 210s | 蹦蹦软糖 (`bouncy-gummy`), 棉花糖团 (`cotton-candy-clump`) | 棉花糖团 (`cotton-candy-clump`), 粘粘熊糖 (`sticky-bear-gummy`), 汽水泡泡 (`soda-bubble`), 夹心饼怪 (`sandwich-cookie-creep`), 焦糖史莱姆 (`caramel-slime`), 酸酸软糖 (`sour-gummy`), 糖粉飞蛾 (`sugar-moth`), 糖针吐吐 (`sprinkle-spitter`), 太妃盾糖 (`taffy-shieldling`) |
| 裂星糖罐 (`cracked-star-jar`) | 600 | 5 | 裂星糖罐核心 (`cracked-star-jar-core`) @ 210s | 蹦蹦软糖 (`bouncy-gummy`), 酸酸软糖 (`sour-gummy`), 汽水泡泡 (`soda-bubble`), 棉花糖团 (`cotton-candy-clump`), 糖粉飞蛾 (`sugar-moth`), 甘草跳跳 (`licorice-skipper`) | 夹心饼怪 (`sandwich-cookie-creep`), 辣味软糖 (`spicy-gummy`), 焦糖史莱姆 (`caramel-slime`), 汽水泡泡 (`soda-bubble`), 粘粘熊糖 (`sticky-bear-gummy`), 酸酸软糖 (`sour-gummy`), 棉花糖团 (`cotton-candy-clump`), 糖粉飞蛾 (`sugar-moth`), 甘草跳跳 (`licorice-skipper`), 太妃盾糖 (`taffy-shieldling`), 糖针吐吐 (`sprinkle-spitter`) |
| 糖霜草地 (`frosting-grassland`) | 600 | 7 | 暴走搅糖机 (`runaway-sugar-mixer`) @ 210s | 蹦蹦软糖 (`bouncy-gummy`) | 蹦蹦软糖 (`bouncy-gummy`), 酸酸软糖 (`sour-gummy`), 夹心饼怪 (`sandwich-cookie-creep`), 焦糖史莱姆 (`caramel-slime`), 粘粘熊糖 (`sticky-bear-gummy`), 汽水泡泡 (`soda-bubble`), 甘草跳跳 (`licorice-skipper`), 糖粉飞蛾 (`sugar-moth`), 太妃盾糖 (`taffy-shieldling`), 糖针吐吐 (`sprinkle-spitter`) |
| 果冻月台 (`jelly-platform`) | 600 | 5 | 巨型熊糖王 (`giant-gummy-bear-king`) @ 210s | 蹦蹦软糖 (`bouncy-gummy`), 粘粘熊糖 (`sticky-bear-gummy`) | 粘粘熊糖 (`sticky-bear-gummy`), 夹心饼怪 (`sandwich-cookie-creep`), 辣味软糖 (`spicy-gummy`), 汽水泡泡 (`soda-bubble`), 焦糖史莱姆 (`caramel-slime`), 酸酸软糖 (`sour-gummy`), 蹦蹦软糖 (`bouncy-gummy`), 糖粉飞蛾 (`sugar-moth`), 甘草跳跳 (`licorice-skipper`), 太妃盾糖 (`taffy-shieldling`) |
| 汽水溪谷 (`soda-creek`) | 600 | 5 | 汽水喷泉龙 (`soda-fountain-dragon`) @ 210s | 蹦蹦软糖 (`bouncy-gummy`), 汽水泡泡 (`soda-bubble`) | 汽水泡泡 (`soda-bubble`), 辣味软糖 (`spicy-gummy`), 夹心饼怪 (`sandwich-cookie-creep`), 焦糖史莱姆 (`caramel-slime`), 酸酸软糖 (`sour-gummy`), 蹦蹦软糖 (`bouncy-gummy`), 粘粘熊糖 (`sticky-bear-gummy`), 糖针吐吐 (`sprinkle-spitter`), 糖粉飞蛾 (`sugar-moth`), 甘草跳跳 (`licorice-skipper`) |

## 敌人反制

| 敌人 | 行为 | 标签 | 反制提示 |
|---|---|---|---|
| 蹦蹦软糖 (`bouncy-gummy`) | `chase` | basic, swarm | 保持移动即可摆脱，适合用基础投射物清理。 |
| 焦糖史莱姆 (`caramel-slime`) | `leave_hazard` | control, sticky | 保持移动并优先清掉路线附近的焦糖怪。 |
| 棉花糖团 (`cotton-candy-clump`) | `chase` | swarm, aoe-check, soft | 用汽水喷泉等范围武器清理成团目标，避免被慢慢挤到地图边缘。 |
| 甘草跳跳 (`licorice-skipper`) | `jump` | jump, disruptor, midgame | 跳跃前会压低身体并亮起糖粉，横向移动可以躲开落点。 |
| 夹心饼怪 (`sandwich-cookie-creep`) | `chase` | tank, blocker | 用穿透或范围武器提前削血，不要让它堵住退路。 |
| 汽水泡泡 (`soda-bubble`) | `split` | split, swarm, soda | 不要把泡泡怪集中在身边击杀，尽量用范围伤害提前清掉分裂压力。 |
| 酸酸软糖 (`sour-gummy`) | `chase` | fast, sour | 提前拉开距离，避免被快速贴身。 |
| 辣味软糖 (`spicy-gummy`) | `dash` | dash, burst-danger, spicy | 观察蓄力后横向躲开，避免直线后撤被冲刺追上。 |
| 糖针吐吐 (`sprinkle-spitter`) | `ranged_spit` | ranged, warning, projectile-pressure | 吐糖针前会鼓起身体并对准玩家，保持横向移动即可规避。 |
| 粘粘熊糖 (`sticky-bear-gummy`) | `chase` | control, slow, bear | 优先保持距离或用控制武器打断贴身，不要在窄路被熊糖围住。 |
| 糖粉飞蛾 (`sugar-moth`) | `orbit_player` | orbit, flanker, visual-clarity | 生命很低，环绕半径稳定，玩家向内切或用范围武器可清理。 |
| 太妃盾糖 (`taffy-shieldling`) | `shielded` | shielded, blocker, tank | 移动慢且背面更脆，玩家绕开正面或用范围伤害处理。 |

## Boss 机制

| Boss | 能力 | 反制提示 |
|---|---|---|
| 焦糖熔炉 (`caramel-furnace`) | caramel_floor_cycle, lay_caramel_tracks, slow_pulse, summon_caramel_slime | 焦糖地面会压缩路线，需要持续移动并提前绕开亮面预警区。 |
| 裂星糖罐核心 (`cracked-star-jar-core`) | bubble_phase_barrage, multi_flavor_storm, phase_shift_vulnerability, sour_phase_storm, spicy_phase_burst, sweet_phase_shield | 每次阶段切换都会短暂暴露核心，需要根据当前风暴颜色调整输出距离。 |
| 巨型棉花团 (`giant-cotton-clump`) | recombine_heal, soft_roll, split_cotton_clumps | 分裂阶段单体较弱，优先清掉小团可以降低重新合体后的压力。 |
| 巨型熊糖王 (`giant-gummy-bear-king`) | double_jump_shockwave, jump_shockwave, summon_guard_wave, summon_sticky_bear_gummy | 起跳阴影会提前出现，落地后短暂硬直是主要输出窗口。 |
| 暴走搅糖机 (`runaway-sugar-mixer`) | dash_charge, sugar_splash, summon_bouncy_gummy | 冲撞前会出现红色预警线，冲撞后短暂硬直。 |
| 汽水喷泉龙 (`soda-fountain-dragon`) | bubble_barrage, charged_fountain, summon_soda_bubble | 喷射前有明显蓄力，绕到侧面移动可以避开主要弹幕。 |

## 随机事件

- 焦糖地震 (`caramel-quake`)：地面短暂震动并出现焦糖危险区，要求玩家持续改变路线。
- 棉花云遮挡 (`cotton-cloud-cover`)：软云短暂遮挡战场边缘，玩家输出节奏降低但拾取收益更高。
- 彩虹糖潮 (`rainbow-candy-rush`)：短时间内糖晶掉落增加，但敌人生成也会加快。
- 酸味雨 (`sour-rain`)：短时间敌人生成更急促，但糖晶收益也会提高。
- 糖罐补给 (`sugar-jar-supply`)：限时出现糖罐补给，触发一次额外升级三选一奖励。

## 阻塞项

- `design_review_incomplete`
- `manual_playtest_incomplete`
- `final_acceptance_missing`
- `accepted_content_lockfile_blocked`

## 限制

- This guide summarizes generated candidate content for human playtest preparation only.
- It does not approve content, fill human review fields, or move files into accepted_content.
- v51 must remain out of content/base_demo and Runtime official content until human gates pass.
