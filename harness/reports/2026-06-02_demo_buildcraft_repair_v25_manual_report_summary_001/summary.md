# v25 人工试玩报告客观摘要

- Candidate id: `2026-06-02_demo_buildcraft_repair_v25_full_pack`
- Content hash: `fnv1a64:aab110776109609d`
- Draft: `harness/playtest/drafts/2026-06-02_demo_buildcraft_repair_v25_manual_playtest_review_draft.json`
- Decision: `manual_report_summary_no_reports`
- Reports: `0` / `9`
- Attention items: `0`

## 运行指标

| Run | Report | Terminal | Time | Level | Kills | Damage Taken | Upgrades | Avg FPS | Attention |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `new_001` | `False` | `` |  |  |  |  |  |  | `0` |
| `new_002` | `False` | `` |  |  |  |  |  |  | `0` |
| `new_003` | `False` | `` |  |  |  |  |  |  | `0` |
| `skilled_001` | `False` | `` |  |  |  |  |  |  | `0` |
| `skilled_002` | `False` | `` |  |  |  |  |  |  | `0` |
| `skilled_003` | `False` | `` |  |  |  |  |  |  | `0` |
| `build_001` | `False` | `` |  |  |  |  |  |  | `0` |
| `build_002` | `False` | `` |  |  |  |  |  |  | `0` |
| `build_003` | `False` | `` |  |  |  |  |  |  | `0` |

## 缺失报告

- `harness/telemetry/local/v25_manual_playtest_new_001.json`
- `harness/telemetry/local/v25_manual_playtest_new_002.json`
- `harness/telemetry/local/v25_manual_playtest_new_003.json`
- `harness/telemetry/local/v25_manual_playtest_skilled_001.json`
- `harness/telemetry/local/v25_manual_playtest_skilled_002.json`
- `harness/telemetry/local/v25_manual_playtest_skilled_003.json`
- `harness/telemetry/local/v25_manual_playtest_build_001.json`
- `harness/telemetry/local/v25_manual_playtest_build_002.json`
- `harness/telemetry/local/v25_manual_playtest_build_003.json`

## 需要注意

- 无

## 填写提示

- 这份摘要只能帮真人回忆客观局面，不能替代 `fun_rating`、`clarity_rating`、可读性、死亡原因或是否想再来一局的判断。
- 若某局出现 `demo`、加速或 auto-exit 标记，请重新用人工 launcher 跑该局。
- 填写 JSON 草稿时，优先写具体瞬间，例如“第 3 次升级时远程投射物反馈不够明显”。

## 后续行动

- 用 `python3 harness/playtest/run_v25_manual_playtest.py --next` 继续运行缺失的人工试玩局。
- 这份客观摘要只能作为填写参考；评分、notes、tags 和 next_actions 必须来自真人观察。
- 9 份报告和真人填写后的 JSON 草稿都准备好后，再运行 `check_v25_manual_playtest_status.py` 和 strict validation。

## 限制

- 本工具只汇总 Runtime report 中的客观指标。
- 它不判断乐趣、清晰度、可读性、死亡原因或是否接受候选。
- 使用 demo input、simulation speed 或 auto-exit 生成的报告会被标记，且不得作为人工证据。
