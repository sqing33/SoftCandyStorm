# Content Candidate Review Packet

- Pack: `2026-05-26_phase4_roster_gap_full_pack`
- Candidate path: `harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack`
- Manifest: `harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack/metadata/manifest.json`
- Source patch manifest: `harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack/metadata/source_patch_manifest.json`
- Preflight report: `harness/reports/2026-05-26_phase4_roster_full_pack_preflight_001/summary.md`
- Review draft: `harness/content_review/drafts/2026-05-26_phase4_roster_gap_full_pack_design_review_draft.json`
- Contents: 8
- Missing review entries: 0

## Type Counts

| Type | Count |
|---|---:|
| `enemy` | 4 |
| `passive` | 4 |

## Contents

| Content | Type | Name | Role | Review |
|---|---|---|---|---|
| `honey-heart` | `passive` | 蜂蜜糖心 | 低速恢复 | `draft_todo` |
| `peppermint-pocket-watch` | `passive` | 薄荷怀表 | 轻量冷却平滑 | `draft_todo` |
| `jelly-lens-polish` | `passive` | 果冻镜片油 | 投射物可读性与命中可靠性 | `draft_todo` |
| `cocoa-safety-badge` | `passive` | 可可安全徽章 | 低血量防御缓冲 | `draft_todo` |
| `licorice-skipper` | `enemy` | 甘草跳跳 | 跳跃干扰怪 | `draft_todo` |
| `sugar-moth` | `enemy` | 糖粉飞蛾 | 环绕压力怪 | `draft_todo` |
| `taffy-shieldling` | `enemy` | 太妃盾糖 | 护盾阻挡怪 | `draft_todo` |
| `sprinkle-spitter` | `enemy` | 糖针吐吐 | 远程预警压力怪 | `draft_todo` |

## Content Details

### honey-heart

- File: `harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack/passives/honey-heart.json`
- Type: `passive`
- Rarity: `common`
- Tags: `recovery`, `defense`, `beginner`
- Review status: `draft_todo`
- Role: 低速恢复
- Balance risk: 回复叠加可能让防御流过于安全
- Gate focus: IdleBot 不能只靠续航活到 600 秒
- Counterplay or limit: 单级回复较低，且不提供直接输出。
- Summary preview: 缓慢恢复生命，帮助新手从小失误中恢复。 / 一颗半透明蜂蜜心形糖，中心有暖黄色糖浆光。 / 温暖轻柔的糖浆滴落声。

### peppermint-pocket-watch

- File: `harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack/passives/peppermint-pocket-watch.json`
- Type: `passive`
- Rarity: `rare`
- Tags: `cooldown`, `control`, `timing`
- Review status: `draft_todo`
- Role: 轻量冷却平滑
- Balance risk: 冷却乘区叠加可能让投射物流过度加速
- Gate focus: 武器释放频率和投射物数量必须留在性能预算内
- Counterplay or limit: 乘区数值较小，且 rare 解锁让它低于当前 common 冷却被动。
- Summary preview: 略微加快武器节奏，适合需要稳定控场的流派。 / 薄荷糖外壳的小怀表，指针像两根细糖棒。 / 清脆的滴答声和薄荷铃音。

### jelly-lens-polish

- File: `harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack/passives/jelly-lens-polish.json`
- Type: `passive`
- Rarity: `common`
- Tags: `projectile`, `readability`, `support`
- Review status: `draft_todo`
- Role: 投射物可读性与命中可靠性
- Balance risk: 投射物过大会抬高实际群体伤害
- Gate focus: 投射物尺寸流不应统治群体 DPS
- Counterplay or limit: 数值低于糖霜手套，并以 readability support 标签定位。
- Summary preview: 让投射物稍微变大，提升小尺寸命中可读性。 / 装在透明小瓶中的果冻亮油，瓶口挂着糖晶刷。 / 轻轻擦亮玻璃的 squeak 声。

### cocoa-safety-badge

- File: `harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack/passives/cocoa-safety-badge.json`
- Type: `passive`
- Rarity: `rare`
- Tags: `defense`, `low-health`, `beginner`
- Review status: `draft_todo`
- Role: 低血量防御缓冲
- Balance risk: 可能与防粘围裙重叠，让 TankBot 过于稳定
- Gate focus: TankBot 胜率和接触承伤
- Counterplay or limit: 固定减伤低于防粘围裙；在低血量条件逻辑实现前应保持 repair 候选。
- Summary preview: 提供少量减伤，作为低血量保护机制的候选基础。 / 圆形可可糖徽章，边缘有奶油白色软垫。 / 柔和的徽章叮声和可可粉扑声。

### licorice-skipper

- File: `harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack/enemies/licorice-skipper.json`
- Type: `enemy`
- Rarity: `common`
- Tags: `jump`, `disruptor`, `midgame`
- Review status: `draft_todo`
- Role: 跳跃干扰怪
- Balance risk: 跳跃时机不可读会造成不公平接触伤害
- Gate focus: 死亡原因清晰度和中前期压力
- Counterplay or limit: 跳跃前有可见压低动作，接触伤害保持中等。
- Summary preview: 会短距离跳跃切入路线的甘草糖敌人，用来打断固定绕圈。 / 细长甘草糖卷成弹簧状，顶部有白色糖粉和小眼睛。 / 有弹性的 twang 声和轻微糖粉散落声。

### sugar-moth

- File: `harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack/enemies/sugar-moth.json`
- Type: `enemy`
- Rarity: `common`
- Tags: `orbit`, `flanker`, `visual-clarity`
- Review status: `draft_todo`
- Role: 环绕压力怪
- Balance risk: 环绕怪过多会困住低移速玩家
- Gate focus: CowardBot 路线安全和视觉清晰度
- Counterplay or limit: 生命较低，环绕轨迹可预测。
- Summary preview: 绕着玩家外圈飘动的糖粉飞蛾，逼迫玩家留意侧向空间。 / 白糖粉翅膀的小飞蛾，翅膀边缘是淡粉色糖晶颗粒。 / 轻柔扑翅声和细砂糖沙沙声。

### taffy-shieldling

- File: `harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack/enemies/taffy-shieldling.json`
- Type: `enemy`
- Rarity: `rare`
- Tags: `shielded`, `blocker`, `tank`
- Review status: `draft_todo`
- Role: 护盾阻挡怪
- Balance risk: 阻挡怪过多会让投射物流派显得无效
- Gate focus: 投射物流派清怪时间和路线压缩
- Counterplay or limit: 移动慢，成功清理后给予较高 XP 奖励。
- Summary preview: 外层裹着半硬太妃糖壳的慢速敌人，会挡住一部分投射物路线。 / 盾牌形太妃糖壳，正面有奶油反光，背后露出软糖身体。 / 脆糖壳 crack 声和软糖弹跳声。

### sprinkle-spitter

- File: `harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack/enemies/sprinkle-spitter.json`
- Type: `enemy`
- Rarity: `rare`
- Tags: `ranged`, `warning`, `projectile-pressure`
- Review status: `draft_todo`
- Role: 远程预警压力怪
- Balance risk: 远程吐针会增加投射物可读性压力
- Gate focus: 投射物可读性和活跃投射物数量
- Counterplay or limit: 移速较低，每次吐针前有清晰蓄力。
- Summary preview: 会停顿后吐出短距离糖针的远程压力敌人，测试弹幕可读性。 / 小号撒糖针瓶形软糖，瓶口有彩色糖针，身体圆润不恐怖。 / 短促 puff 声和糖针轻响。

## Missing Review Entries

- None

## Limitations

- This packet organizes content design review evidence only.
- It does not validate human ratings, run Schema or static budget gates, simulate content, or promote candidates.
- TODO review fields must be filled by a human before design-review validation can pass.
- A valid design review still does not write to validated_candidates, simulated_candidates, playtest_candidates, accepted_content, or Runtime.
