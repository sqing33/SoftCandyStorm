# Runtime 人工试玩审查包

## 目标

本审查包用于把 Runtime capture 的技术报告转化为真人试玩结论。Bot、demo input、Replay 和 Harness 只能证明链路、稳定性、平衡风险和可复现性；它们不能替代“是否好玩、是否看得清、是否知道为什么失败”的人类判断。

## 推荐启动命令

```bash
cargo run -p game_runtime -- --content-dir content/base_demo --seed 12345 --seconds 600 --playtest-report harness/telemetry/local/runtime_manual_playtest_<run_id>.json --player-skill new --capture-interval 2
```

约束：

- 人工评分不要使用 `--demo-input`。
- 人工评分不要使用 `--simulation-speed`。
- 如果只验证报告写盘或终局退出，可以使用 `--auto-exit-after-report`；正式人工试玩建议让窗口自然停留，方便补记观察。
- 试玩结束后，把本地报告复制到 `harness/reports/<date>_runtime_manual_playtest_<run_id>/`，并补一份 `summary.md`。

## 最小覆盖矩阵

每个可发布候选至少完成 9 局：

| run id | 玩家视角 | 目标 | 必看事项 |
|---|---|---|---|
| `new_001` | 新手 | 不看说明直接开始 | 是否理解移动、拾取、升级 |
| `new_002` | 新手 | 尝试贪 XP | 是否知道为什么受伤或死亡 |
| `new_003` | 新手 | 保守绕圈 | 前 2 分钟是否至少看到 2-3 次升级机会 |
| `skilled_001` | 熟练 | 主动拉怪收 XP | 命中反馈、XP 节奏、升级纠结感 |
| `skilled_002` | 熟练 | 主动挑战 Boss | Boss 出场提示、体型、威胁方向是否清楚 |
| `skilled_003` | 熟练 | 高压波次存活 | 屏幕压力是否压迫但不烦 |
| `build_001` | 流派 | 远程投射物优先 | projectile 可读性、单体输出反馈 |
| `build_002` | 流派 | 防御/移速优先 | 受伤反馈、逃生空间、容错感 |
| `build_003` | 流派 | 控制/范围优先 | 地面效果、敌群可读性、性能体感 |

## 评分字段

使用 1-5 分：

- `1`：不可接受，阻断推进。
- `2`：明显问题，需要 repair。
- `3`：可试玩但有风险。
- `4`：达到当前原型目标。
- `5`：明显优秀，可以作为后续标杆。

必填字段：

- `fun_rating`：是否有再来一局冲动。
- `clarity_rating`：是否看得清角色、敌人、弹幕、拾取物和升级界面。
- `difficulty_rating`：压力是否合理，死亡是否可接受。
- `projectile_readability`：投射物方向、速度、命中是否能理解。
- `hit_feedback`：命中、击杀、受伤、终局反馈是否足够。
- `xp_pickup_rhythm`：拾取糖晶是否顺畅，是否鼓励移动决策。
- `boss_spawn_clarity`：Boss 出场是否被注意到，威胁是否明确。
- `death_reason_clarity`：如果死亡，是否知道主要原因。
- `notes`：一句以上具体观察，不写空泛评价。
- `tags`：从固定标签中选，也可以补充新标签。
- `next_actions`：必须能转化为代码、内容、素材、数值或文档行动。

推荐标签：

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

## 门禁结论

每局人工试玩结论只能使用：

- `repair`：存在明确问题，先修再测。
- `playtest_pass`：当前原型目标可接受，但仍不是最终发布通过。
- `needs_more_runs`：样本不足或观察互相矛盾。

不能使用：

- `accept_release`：单次人工试玩不能直接放行发布。
- `accept_content`：素材或内容仍必须走候选池、Schema、预算和 Harness。

## 失败案例记录

如果出现死亡原因不清、Boss 提示看不见、受伤反馈误导、性能明显卡顿、升级选项看不懂或玩家无法理解目标，需要补 failure case。建议字段：

```json
{
  "case_id": "fail_20260525_manual_001",
  "category": "manual_playtest",
  "run_id": "new_002",
  "seed": 12345,
  "player_skill": "new",
  "time_seconds": 118.4,
  "symptom": "玩家连续受伤但没有意识到被焦糖怪贴身",
  "root_cause": "受伤闪烁和敌人贴身轮廓不够明显",
  "fix": "增强受伤方向提示和近身敌人描边",
  "validation": "重新运行 new_002 和 skilled_003，确认 death_reason_clarity 至少 4 分"
}
```

## 汇总要求

完成一批人工试玩后，在对应 `harness/reports/.../summary.md` 中写：

- 覆盖了哪些 run id。
- 哪些字段低于 3 分。
- 是否出现 P0/P1 问题。
- 哪些问题需要进入 `harness/failed_cases/`。
- 下一步是 `repair`、`needs_more_runs` 还是 `playtest_pass`。

如果候选要从 `playtest_candidates` 推进到 `accepted_content`，还必须按 `harness/playtest/content_acceptance_review_template.json` 补齐 9 局人工试玩证据、内容 hash、审查人、审查日期和 `accept_candidate` 总结论。

## 自动完整性检查

可以先从 9 局矩阵生成 TODO 草稿：

```bash
python3 harness/playtest/create_manual_playtest_review_draft.py \
  --template harness/playtest/runtime_manual_review_template.json \
  --candidate-id current-base-demo-runtime \
  --content-hash TODO:content-hash-after-freeze \
  --out harness/playtest/drafts/2026-05-26_runtime_manual_playtest_review_draft.json
```

该草稿只用于防漏项，默认 `needs_more_runs`，真人填写评分和观察前必须保持校验失败。

人工填写完成后，可以用纯 Python 校验器检查字段是否齐全：

```bash
python3 harness/playtest/validate_manual_review.py \
  harness/playtest/content_acceptance_review_template.json \
  --strict-acceptance \
  --report harness/reports/<date>_manual_review_validation/report.json \
  --markdown harness/reports/<date>_manual_review_validation/summary.md
```

该工具只检查证据完整性，不会替代人工判断；空模板、空评分、少于 9 局、非法门禁或缺少 `notes` / `next_actions` 都会失败。

严格校验报告生成后，可以再汇总最终接受证据包：

```bash
python3 harness/playtest/create_manual_playtest_acceptance_review_packet.py \
  --repo-root . \
  --report harness/reports/<date>_manual_playtest_acceptance_review_packet/manual_playtest_acceptance_review_packet.json \
  --markdown harness/reports/<date>_manual_playtest_acceptance_review_packet/summary.md
```

该证据包会同时展示人工试玩源记录、严格校验、Release Candidate `manual_playtest` gate、内容接受证据包和 accepted content lockfile 状态。当前本地证据包仍为 `manual_playtest_acceptance_review_packet_needs_evidence`，因为草稿含 TODO、严格校验为 `manual_review_invalid`、RC gate 为 `waiting`。它不运行 Runtime、不填写真人评分、不把内容推进到 `accepted_content`。
