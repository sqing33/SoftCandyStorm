# Demo Buildcraft Repair v25 Manual Playtest Runbook

- Candidate id: `2026-06-02_demo_buildcraft_repair_v25_full_pack`
- Content dir: `harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack`
- Content hash: `fnv1a64:aab110776109609d`
- Review draft: `harness/playtest/drafts/2026-06-02_demo_buildcraft_repair_v25_manual_playtest_review_draft.json`
- Review packet: `harness/reports/2026-06-02_demo_buildcraft_repair_v25_manual_playtest_review_packet_001/summary.md`

## Purpose

This runbook gives a human playtester exact local commands for the required 9-run manual playtest matrix. It does not approve the candidate, fill review ratings, or promote content to `accepted_content`.

Each run should be played manually. Do not use `--demo-input` or `--simulation-speed` for human evidence.

## Common Command Shape

Recommended launcher:

```bash
python3 harness/playtest/check_v25_candidate_readiness.py --allow-incomplete
python3 harness/playtest/list_v25_human_evidence_todos.py --allow-todos
python3 harness/playtest/run_v25_manual_playtest.py --list
python3 harness/playtest/run_v25_manual_playtest.py --status
python3 harness/playtest/run_v25_manual_playtest.py --next --dry-run
python3 harness/playtest/run_v25_manual_playtest.py --next
python3 harness/playtest/run_v25_manual_playtest.py <run_id> --dry-run
python3 harness/playtest/run_v25_manual_playtest.py <run_id>
python3 harness/playtest/check_v25_manual_playtest_status.py --allow-incomplete
```

Expanded Runtime command shape:

```bash
cargo run -p game_runtime -- \
  --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack \
  --seed <seed> \
  --seconds 600 \
  --player-skill <new|skilled|build> \
  --playtest-report harness/telemetry/local/v25_manual_playtest_<run_id>.json \
  --capture-interval 2
```

After each run, replace the matching `TODO` section in the review draft with concrete observations, 1-5 ratings, tags, and next actions.

Use `check_v25_candidate_readiness.py --allow-incomplete` for the combined design-review and manual-playtest status, including the next missing playtest command.

Use `list_v25_human_evidence_todos.py --allow-todos` to list every field that still needs concrete human evidence.

Use `run_v25_manual_playtest.py --status` to see report progress and `--next` to launch the first missing local report run. These launcher shortcuts only inspect report files; use the status checker below before strict validation.

Use the status checker after a batch of runs to confirm which local reports are still missing and whether the draft still contains `TODO` placeholders.

## Run Matrix

| Run | Skill | Seed | Intent | Report |
|---|---|---:|---|---|
| `new_001` | `new` | 25001 | 不看说明直接开始 | `harness/telemetry/local/v25_manual_playtest_new_001.json` |
| `new_002` | `new` | 25002 | 尝试贪 XP | `harness/telemetry/local/v25_manual_playtest_new_002.json` |
| `new_003` | `new` | 25003 | 保守绕圈 | `harness/telemetry/local/v25_manual_playtest_new_003.json` |
| `skilled_001` | `skilled` | 25011 | 主动拉怪收 XP | `harness/telemetry/local/v25_manual_playtest_skilled_001.json` |
| `skilled_002` | `skilled` | 25012 | 主动挑战 Boss | `harness/telemetry/local/v25_manual_playtest_skilled_002.json` |
| `skilled_003` | `skilled` | 25013 | 高压波次存活 | `harness/telemetry/local/v25_manual_playtest_skilled_003.json` |
| `build_001` | `build` | 25021 | 远程投射物优先 | `harness/telemetry/local/v25_manual_playtest_build_001.json` |
| `build_002` | `build` | 25022 | 防御 / 移速优先 | `harness/telemetry/local/v25_manual_playtest_build_002.json` |
| `build_003` | `build` | 25023 | 控制 / 范围优先 | `harness/telemetry/local/v25_manual_playtest_build_003.json` |

## Commands

### new_001

```bash
python3 harness/playtest/run_v25_manual_playtest.py new_001
cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25001 --seconds 600 --player-skill new --playtest-report harness/telemetry/local/v25_manual_playtest_new_001.json --capture-interval 2
```

### new_002

```bash
python3 harness/playtest/run_v25_manual_playtest.py new_002
cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25002 --seconds 600 --player-skill new --playtest-report harness/telemetry/local/v25_manual_playtest_new_002.json --capture-interval 2
```

### new_003

```bash
python3 harness/playtest/run_v25_manual_playtest.py new_003
cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25003 --seconds 600 --player-skill new --playtest-report harness/telemetry/local/v25_manual_playtest_new_003.json --capture-interval 2
```

### skilled_001

```bash
python3 harness/playtest/run_v25_manual_playtest.py skilled_001
cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25011 --seconds 600 --player-skill skilled --playtest-report harness/telemetry/local/v25_manual_playtest_skilled_001.json --capture-interval 2
```

### skilled_002

```bash
python3 harness/playtest/run_v25_manual_playtest.py skilled_002
cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25012 --seconds 600 --player-skill skilled --playtest-report harness/telemetry/local/v25_manual_playtest_skilled_002.json --capture-interval 2
```

### skilled_003

```bash
python3 harness/playtest/run_v25_manual_playtest.py skilled_003
cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25013 --seconds 600 --player-skill skilled --playtest-report harness/telemetry/local/v25_manual_playtest_skilled_003.json --capture-interval 2
```

### build_001

```bash
python3 harness/playtest/run_v25_manual_playtest.py build_001
cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25021 --seconds 600 --player-skill build --playtest-report harness/telemetry/local/v25_manual_playtest_build_001.json --capture-interval 2
```

### build_002

```bash
python3 harness/playtest/run_v25_manual_playtest.py build_002
cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25022 --seconds 600 --player-skill build --playtest-report harness/telemetry/local/v25_manual_playtest_build_002.json --capture-interval 2
```

### build_003

```bash
python3 harness/playtest/run_v25_manual_playtest.py build_003
cargo run -p game_runtime -- --content-dir harness/generated_candidates/2026-06-02_demo_buildcraft_repair_v25_full_pack --seed 25023 --seconds 600 --player-skill build --playtest-report harness/telemetry/local/v25_manual_playtest_build_003.json --capture-interval 2
```

## Validation After Human Review

When the human-filled draft has no TODO placeholders and every run has concrete ratings, validate it with:

```bash
python3 harness/playtest/validate_manual_review.py \
  harness/playtest/drafts/2026-06-02_demo_buildcraft_repair_v25_manual_playtest_review_draft.json \
  --strict-acceptance \
  --report harness/reports/2026-06-02_demo_buildcraft_repair_v25_manual_playtest_strict_validation_001/manual_review_validation.json \
  --markdown harness/reports/2026-06-02_demo_buildcraft_repair_v25_manual_playtest_strict_validation_001/summary.md
```

Expected current state before human review: validation should fail because the draft still contains `TODO` fields and `acceptance_decision` is `needs_more_runs`.

Before strict validation, check local evidence status with:

```bash
python3 harness/playtest/check_v25_manual_playtest_status.py \
  --report harness/reports/2026-06-02_demo_buildcraft_repair_v25_manual_playtest_status_001/manual_playtest_status.json \
  --markdown harness/reports/2026-06-02_demo_buildcraft_repair_v25_manual_playtest_status_001/summary.md
```

The current pre-human state is `manual_playtest_incomplete`: 0 / 9 local reports exist and the review draft still contains `TODO` placeholders.

## Limitations

- This is a command runbook only.
- It does not run the 9 manual playtests.
- It does not replace content design review.
- It does not approve `playtest_candidates` or `accepted_content`.
- Human review must still record fun, clarity, difficulty, projectile readability, hit feedback, XP rhythm, Boss clarity, death reason clarity, notes, tags, and next actions.
