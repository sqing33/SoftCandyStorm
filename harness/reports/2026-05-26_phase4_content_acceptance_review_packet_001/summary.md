# Content Acceptance Review Packet

- Source: `harness/generated_candidates/2026-05-26_phase4_roster_gap_full_pack`
- Decision: `content_acceptance_review_packet_needs_evidence`
- Candidate pack: `2026-05-26_phase4_roster_gap_full_pack`
- Candidate kind: `full_content_pack`
- Contents: 8
- Evidence files: 7 / 7
- Demo readiness: `demo_not_ready`
- Accepted content lockfile: `accepted_content_lockfile_blocked`

## Evidence

| Field | Status | Expected | Path |
|---|---|---|---|
| `candidate_preflight_report` | `exists` | materialized full pack preflight exists | `harness/reports/2026-05-26_phase4_roster_full_pack_preflight_001/summary.md` |
| `static_budget_report` | `exists` | pure Python static budget exists | `harness/reports/2026-05-26_static_balance_budget_phase4_full_pack_001/summary.md` |
| `design_review_draft` | `exists` | human-filled design review must replace TODO values | `harness/content_review/drafts/2026-05-26_phase4_roster_gap_full_pack_design_review_draft.json` |
| `design_review_packet` | `exists` | review packet exists for human review | `harness/reports/2026-05-26_phase4_roster_content_review_packet_001/summary.md` |
| `demo_readiness_report` | `exists` | demo readiness must not be demo_ready until gates pass | `harness/reports/2026-05-26_demo_readiness_current_local_001/demo_readiness.json` |
| `manual_playtest_draft` | `exists` | 9-run human playtest must be filled by a human | `harness/playtest/drafts/2026-05-26_runtime_manual_playtest_review_draft.json` |
| `accepted_content_lockfile_report` | `exists` | non-empty lockfile only after strict human acceptance | `harness/reports/2026-05-26_accepted_content_lockfile_current_local_001/accepted_content_lockfile.json` |

## Review Status

- Design review status: `draft_todo`
- Design review gate: `needs_more_review`
- Design review TODO count: `71`
- Manual playtest status: `draft_todo`
- Manual playtest decision: `needs_more_runs`
- Manual playtest TODO count: `104`

## Type Counts

| Type | Count |
|---|---:|
| `enemy` | 4 |
| `passive` | 4 |

## Contents

| Content | Type | Name | Tags | Gate Focus |
|---|---|---|---|---|
| `honey-heart` | `passive` | 蜂蜜糖心 | `recovery`, `defense`, `beginner` | IdleBot 不能只靠续航活到 600 秒 |
| `peppermint-pocket-watch` | `passive` | 薄荷怀表 | `cooldown`, `control`, `timing` | 武器释放频率和投射物数量必须留在性能预算内 |
| `jelly-lens-polish` | `passive` | 果冻镜片油 | `projectile`, `readability`, `support` | 投射物尺寸流不应统治群体 DPS |
| `cocoa-safety-badge` | `passive` | 可可安全徽章 | `defense`, `low-health`, `beginner` | TankBot 胜率和接触承伤 |
| `licorice-skipper` | `enemy` | 甘草跳跳 | `jump`, `disruptor`, `midgame` | 死亡原因清晰度和中前期压力 |
| `sugar-moth` | `enemy` | 糖粉飞蛾 | `orbit`, `flanker`, `visual-clarity` | CowardBot 路线安全和视觉清晰度 |
| `taffy-shieldling` | `enemy` | 太妃盾糖 | `shielded`, `blocker`, `tank` | 投射物流派清怪时间和路线压缩 |
| `sprinkle-spitter` | `enemy` | 糖针吐吐 | `ranged`, `warning`, `projectile-pressure` | 投射物可读性和活跃投射物数量 |

## Blockers

- design review draft still contains TODO placeholders
- design review has not reached simulate_candidate
- manual playtest draft still contains TODO placeholders
- manual playtest has not accepted the candidate
- demo readiness is `demo_not_ready`
- accepted content lockfile is `accepted_content_lockfile_blocked`

## Errors

- None

## Required Next Steps

- Replace design review TODO values with a real human design review and validate it.
- After binary recovery, run formal Harness validate-candidates, budget-content, Bot simulation, and replay regression.
- Run and fill the 9-run manual playtest review with human ratings and notes.
- Only after strict human acceptance, generate a non-empty accepted content lockfile.

## Limitations

- This packet organizes content acceptance evidence only.
- It does not validate human reviews, simulate content, promote candidates, write accepted_content, or approve release readiness.
- Candidate content remains generated_candidates until every required gate passes.
