# Goal Blocker Priority Audit

- Decision: `goal_blockers_present`
- Blockers: 5

## Severity

| Severity | Count |
|---|---:|
| `P0` | 1 |
| `P1` | 2 |
| `P2` | 2 |

## Next Queue

### P0 `manual_evidence_gaps`

Manual review evidence is still incomplete across 20 requirement(s).

- Use the manual evidence gap audit as the human-review checklist.
- Do not mark playtest, content, story, asset, privacy, platform, base UI, or release gates as passing until their validators pass.

### P1 `release_candidate_not_ready`

Release Candidate evidence is not ready.

- Keep release_candidate_not_ready until binary-dependent gates and human gates are real pass evidence.
- After blockers clear, rerun tools/validate_release_candidate_evidence.py without --allow-not-ready.

### P1 `release_package_not_ready`

Release package manifest is not ready.

- Do not prepare a release package until Release Candidate evidence is ready.
- After a concrete package exists, rerun tools/validate_release_package_manifest.py.

### P2 `docs_implementation_incomplete`

Docs coverage remains incomplete for 18 document(s).

- Use docs coverage gaps to choose only tasks that can be honestly evidenced.
- Keep binary- and human-dependent docs partial/blocked until real validation exists.

### P2 `roadmap_incomplete`

Roadmap has 10 incomplete phase(s).

- 继续运行 600 秒 all Bot matrix、strict replay-batch 和 Gym high-pressure 对比。
- 准备 9 局人工试玩审查，并让真人填写 runtime_manual_review_pack。
- 重跑 all Bot matrix 与 strict replay-batch，并修复当前 Bot 矩阵门禁失败。
- 继续减少 progress 无 report warning。
- 先补 GameCore 对 jump、orbit_player、ranged_spit、shielded 敌人行为的可测实现，再小步修复 full pack 候选的长局压力并重跑 5 seed / 600 秒 all Bot simulate-candidates。
- 候选仿真通过且真人试玩通过后再考虑 accepted_content。

## Blockers

| Severity | Category | Blocker | Status | Source |
|---|---|---|---|---|
| `P0` | `human_review` | `manual_evidence_gaps` | `manual_evidence_gaps_present` | `harness/reports/2026-05-26_manual_evidence_gap_audit_001/manual_evidence_gap_audit.json` |
| `P1` | `release` | `release_candidate_not_ready` | `release_candidate_not_ready` | `harness/reports/2026-05-26_release_candidate_evidence_current_local_005/release_candidate_evidence.json` |
| `P1` | `release` | `release_package_not_ready` | `release_package_not_ready` | `harness/reports/2026-05-26_release_package_manifest_current_local_003/release_package_manifest.json` |
| `P2` | `coverage` | `docs_implementation_incomplete` | `docs_implementation_incomplete` | `harness/docs_implementation_coverage.json` |
| `P2` | `roadmap` | `roadmap_incomplete` | `roadmap_phase_audit_incomplete` | `harness/roadmap_audit/roadmap_phase_audit.json` |

## Errors

- None

## Limitations

- This audit prioritizes existing blocker reports only; it does not execute binaries, run Harness, fill human reviews, or approve release readiness.
- External host policy and human review blockers must be cleared outside this script before downstream gates can become passing evidence.
- Derived release, docs, and roadmap blockers should remain until their source validators report ready or complete.
