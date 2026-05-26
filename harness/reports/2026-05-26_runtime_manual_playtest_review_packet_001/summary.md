# Manual Playtest Review Packet

- Template: `harness/playtest/runtime_manual_review_template.json`
- Draft: `harness/playtest/drafts/2026-05-26_runtime_manual_playtest_review_draft.json`
- Candidate id: `current-base-demo-runtime`
- Content hash: `TODO:content-hash-after-freeze`
- Acceptance decision: `needs_more_runs`
- Runs: 9 / 9
- Missing draft runs: 0

## Rating Fields

- `fun_rating`
- `clarity_rating`
- `difficulty_rating`
- `projectile_readability`
- `hit_feedback`
- `xp_pickup_rhythm`
- `boss_spawn_clarity`
- `death_reason_clarity`

## Runs

| Run | Skill | Intent | Review | Gate |
|---|---|---|---|---|
| `new_001` | `new` | 不看说明直接开始 | `draft_todo` | `needs_more_runs` |
| `new_002` | `new` | 尝试贪 XP | `draft_todo` | `needs_more_runs` |
| `new_003` | `new` | 保守绕圈 | `draft_todo` | `needs_more_runs` |
| `skilled_001` | `skilled` | 主动拉怪收 XP | `draft_todo` | `needs_more_runs` |
| `skilled_002` | `skilled` | 主动挑战 Boss | `draft_todo` | `needs_more_runs` |
| `skilled_003` | `skilled` | 高压波次存活 | `draft_todo` | `needs_more_runs` |
| `build_001` | `build` | 远程投射物优先 | `draft_todo` | `needs_more_runs` |
| `build_002` | `build` | 防御/移速优先 | `draft_todo` | `needs_more_runs` |
| `build_003` | `build` | 控制/范围优先 | `draft_todo` | `needs_more_runs` |

## Run Details

### new_001

- Skill: `new`
- Intent: 不看说明直接开始
- Review status: `draft_todo`
- Required observations:
  - 是否理解移动
  - 是否理解拾取糖晶
  - 是否理解升级三选一

### new_002

- Skill: `new`
- Intent: 尝试贪 XP
- Review status: `draft_todo`
- Required observations:
  - 是否知道为什么受伤
  - 如果死亡是否知道主要原因
  - XP 节奏是否诱导过度冒险

### new_003

- Skill: `new`
- Intent: 保守绕圈
- Review status: `draft_todo`
- Required observations:
  - 前 2 分钟是否至少看到 2-3 次升级机会
  - 保守玩法是否太无聊
  - 怪潮压力是否逐步增加

### skilled_001

- Skill: `skilled`
- Intent: 主动拉怪收 XP
- Review status: `draft_todo`
- Required observations:
  - 命中反馈是否清楚
  - XP 拾取是否顺畅
  - 升级选择是否有纠结

### skilled_002

- Skill: `skilled`
- Intent: 主动挑战 Boss
- Review status: `draft_todo`
- Required observations:
  - Boss 出场是否明显
  - Boss 威胁方向是否明确
  - Boss 战是否拖沓

### skilled_003

- Skill: `skilled`
- Intent: 高压波次存活
- Review status: `draft_todo`
- Required observations:
  - 屏幕压力是否压迫但不烦
  - 受伤反馈是否及时
  - 性能体感是否稳定

### build_001

- Skill: `build`
- Intent: 远程投射物优先
- Review status: `draft_todo`
- Required observations:
  - projectile 可读性
  - 单体输出反馈
  - 远程 Build 是否有明确优势和代价

### build_002

- Skill: `build`
- Intent: 防御/移速优先
- Review status: `draft_todo`
- Required observations:
  - 受伤反馈
  - 逃生空间
  - 容错感

### build_003

- Skill: `build`
- Intent: 控制/范围优先
- Review status: `draft_todo`
- Required observations:
  - 地面效果可读性
  - 敌群可读性
  - 性能体感

## Allowed Tags

- `visual-clarity`
- `difficulty`
- `xp-rhythm`
- `upgrade-choice`
- `weapon-feedback`
- `boss-readability`
- `damage-feedback`
- `performance`
- `input-feel`
- `fun`

## Allowed Run Gates

- `repair`
- `playtest_pass`
- `needs_more_runs`

## Missing Draft Runs

- None

## Limitations

- This packet organizes manual playtest review evidence only.
- It does not run Runtime, inspect gameplay, fill ratings, or approve a candidate.
- TODO review fields must be filled by a human before strict acceptance validation can pass.
- Automated runtime capture reports cannot replace the human observations listed here.
