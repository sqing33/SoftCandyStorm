# Replay 与遥测设计

## 目标

Replay 和遥测用于把真人试玩、Bot 测试、RL 评估连接起来。

它们回答：

- 玩家为什么死？
- 新版本是否破坏旧体验？
- 哪些武器没人选？
- 哪些波次导致大量失败？
- AI 生成内容是否带来异常表现？

## Replay 定义

Replay 不是录屏，而是可复现的输入和状态记录。

Replay 应能在同版本内容和规则下重现一局。

## Replay 文件内容

必须记录：

- replay_version
- game_version
- ruleset_version
- content_hash
- run_config
- tick_rate
- action_stream
- upgrade_choices
- final_metrics

可选记录：

- event_checkpoints
- periodic_snapshots
- rng_checkpoints
- player_notes
- crash_info

## RunConfig 记录

```json
{
  "seed": 12345,
  "map_id": "frosting-grassland",
  "character_id": "jar-keeper",
  "difficulty": "normal",
  "duration_seconds": 600,
  "content_pack_ids": ["base-demo"]
}
```

## Action Stream

为了压缩，动作可以按 tick 或按变化记录。

按变化记录：

```json
[
  {
    "tick": 0,
    "movement": [0, 0]
  },
  {
    "tick": 12,
    "movement": [1, 0]
  },
  {
    "tick": 45,
    "movement": [0.7, -0.7]
  }
]
```

升级选择：

```json
[
  {
    "tick": 1260,
    "options": ["rainbow-candy-shot", "big-candy-jar", "soda-fountain"],
    "chosen_index": 2,
    "chosen_id": "soda-fountain"
  }
]
```

## Replay 回放策略

回放时可能出现内容变化导致选项不同。

模式：

- strict：选项不一致即失败。
- compatible：按 chosen_id 查找。
- tag_fallback：按标签相似度选择替代。

回归测试使用 strict 或 compatible。跨版本分析可用 tag_fallback。

## Replay 用途

### Bug 复现

记录导致崩溃、卡死、异常数值的 replay。

### 人工试玩回归

保存典型人类局：

- 新手失败
- 熟练胜利
- 贪经验失败
- Boss 击杀
- 防御流
- 远程流
- 控制流

### Bot 对比

Bot replay 可用于分析策略缺陷。

### RL 训练

后续可以用真人 replay 做模仿学习或 reward shaping 参考。

## 遥测事件

局内事件：

- run_start
- run_end
- level_up
- upgrade_chosen
- weapon_fired
- enemy_killed
- player_damaged
- boss_spawned
- boss_phase_changed
- boss_killed
- evolution_unlocked
- fps_sample

## 遥测字段

事件通用字段：

- timestamp
- run_id
- session_id，匿名
- game_version
- content_hash
- map_id
- character_id
- difficulty
- elapsed_seconds

不要记录：

- 个人身份信息
- 文件路径
- IP 地址，除非平台服务自动处理且隐私政策说明
- 用户输入的自由文本，除非明确授权

## 本地优先策略

开发阶段优先本地保存：

```text
harness/replay/
harness/telemetry/local/
```

上线前再决定是否接匿名遥测。

当前 Runtime 已提供本地数据控制 CLI：

```bash
cargo run -p game_runtime -- --print-privacy-notice
cargo run -p game_runtime -- --runtime-settings-file harness/telemetry/local/runtime_settings.json --export-local-data harness/telemetry/local/export.json
cargo run -p game_runtime -- --local-data-dir harness/telemetry/local/manual-smoke --delete-local-data
```

默认导出数据目录为 `harness/telemetry/local/` 和 `harness/replay/`，也可以重复传入 `--local-data-dir <path>` 指定额外本地数据目录。导出会读取配置目录并写成 JSON；删除必须显式传入至少一个 `--local-data-dir`，且只移除这些显式目录中的文件和空子目录。Runtime 仍没有网络上传传输层，试玩 capture 报告只会写入当前隐私设置摘要。

当前 Runtime / Gym 运行级 smoke 可用同一工具刷新：

```bash
python3 tools/run_runtime_gym_current_smoke.py \
  --repo-root . \
  --runtime-capture harness/telemetry/local/runtime_gym_current_smoke_001.json \
  --report harness/reports/2026-05-29_runtime_gym_current_smoke_001/runtime_gym_current_smoke.json \
  --markdown harness/reports/2026-05-29_runtime_gym_current_smoke_001/summary.md \
  --seconds 120 \
  --seed 12345 \
  --simulation-speed 30 \
  --capture-interval 5
```

当前报告结论为 `runtime_gym_current_smoke_valid`：Gym wrapper 经由 `game_harness gym-bridge` 完成 2 秒短局 smoke，Runtime 使用 `--demo-input` 生成 120 秒本地 capture，随后由 `tools/validate_runtime_performance_capture.py` 校验 frame metrics、samples、terminal、实体数量和隐私默认值。该报告只证明本机 Runtime capture 与 Gym bridge 技术链路当前可运行，不能替代真人试玩、Steam Deck / 多硬件性能、内存增长分析、真实鼠标 / 手柄输入审查或发布级隐私验收。

更长的 Runtime 本机资源探针可用 `tools/run_runtime_resource_probe.py` 刷新。当前 `harness/reports/2026-05-30_runtime_resource_probe_10min_001/summary.md` 记录了一次 600 秒 demo-input run：capture 由本次运行刷新，`release-local` 性能校验通过，隐私上传默认关闭，峰值 RSS 为 164.14 MiB / 2048 MiB。该报告只证明当前本机一次 Runtime 子进程没有超过 RSS 阈值，不替代长期泄漏观察、GPU profiling、多硬件或人工输入设备审查。

Runtime 局外面板提供 `F4` 隐私与本地数据设置页：

- `7`：切换上传匿名遥测。
- `8`：切换上传原始 Replay。
- `9`：切换上传崩溃报告。

三个开关默认关闭，只有玩家显式操作才会开启。Runtime `F4` 设置页也提供文本面板原型级的右下七段点击区：从左到右映射为匿名遥测、raw replay、崩溃报告、导出存档、删除存档、导出本地数据和删除本地数据。点击区复用 `7/8/9/E/X/L/K` 的同一套 Runtime action；删除存档和删除本地数据仍必须再次触发同一个删除 action 才会执行，切换面板、切换隐私项或执行其他数据操作会取消确认态。启动时传入 `--runtime-settings-file <path>` 后，设置页会把切换结果写回该 JSON；未传入设置文件时只在当前会话生效。该页面会显示上传传输层 `not_implemented`，避免把开关误解为真实上传能力。它仍不是发布级视觉按钮、真实鼠标设备审查、平台路径审查或隐私法律审查通过证据。

## 版本对比

每次内容或数值改动后，对 replay 进行对比：

- 死亡时间差异
- 等级差异
- 伤害来源差异
- Boss 击杀时间差异
- 武器伤害占比差异
- 是否从胜利变失败
- 是否从失败变胜利

明显差异不一定是 bug，但必须可解释。

## Replay 门禁

P0：

- Replay 无法解析
- Replay 回放 panic
- 同版本 strict replay 无法重现

P1：

- 代表性 replay 大量从胜利变失败
- 新手 replay 前 2 分钟死亡率显著上升
- Boss replay 出现不可躲攻击

## 人工反馈结构

真人试玩后记录：

```json
{
  "replay_id": "human_2026_001",
  "player_skill": "new",
  "fun_rating": 4,
  "clarity_rating": 3,
  "difficulty_rating": 4,
  "notes": "升级选择很有趣，但焦糖地面看不清。",
  "tags": ["visual-clarity", "difficulty"]
}
```

人工评分不用于直接门禁，但用于 AI 内容修正输入。

## 遥测隐私

如果未来上线遥测：

- 默认匿名。
- 提供关闭选项。
- 写清用途：平衡、崩溃分析、玩法改进。
- 不上传 replay 原始输入，除非玩家同意。
- 不上传个人身份信息。

当前隐私策略模板与校验器位于：

```text
harness/telemetry_privacy/telemetry_privacy_policy_template.json
harness/telemetry_privacy/validate_telemetry_privacy_policy.py
harness/telemetry_privacy/runtime_privacy_settings_contract_v0.json
harness/telemetry_privacy/validate_runtime_privacy_settings_contract.py
harness/telemetry_privacy/upload_transport_contract_v0.json
harness/telemetry_privacy/validate_upload_transport_contract.py
harness/telemetry_privacy/manual_privacy_review_template.json
harness/telemetry_privacy/create_manual_privacy_review_packet.py
harness/telemetry_privacy/validate_manual_privacy_review.py
harness/telemetry_privacy/manual_legal_review_template.json
harness/telemetry_privacy/create_manual_legal_review_packet.py
harness/telemetry_privacy/validate_manual_legal_review.py
harness/telemetry_privacy/create_telemetry_privacy_acceptance_review_packet.py
harness/reports/2026-05-26_manual_privacy_review_packet_001/summary.md
harness/reports/2026-05-26_manual_legal_review_packet_001/summary.md
harness/reports/2026-05-26_telemetry_privacy_acceptance_review_packet_001/summary.md
```

该策略门禁要求：

- 上传型遥测默认关闭。
- 上传和 raw replay 上传都必须有明确同意。
- 使用匿名 session id，不采集个人身份、IP、文件路径或自由文本。
- `allowed_event_fields` 不能包含禁止字段或 replay 原始输入。
- 本地数据需要有保留天数、删除和导出控制项。
- Runtime 隐私设置页契约必须提供上传开关、raw replay 单独同意、崩溃报告同意、删除本地数据、导出本地数据和隐私说明入口。
- 上传传输契约必须绑定隐私策略和 Runtime 设置契约，保持默认关闭、显式同意、本地队列边界、字段白名单、raw replay 阻断和 Release Candidate 证据限制。
- 发布前仍需要填写并通过人工隐私审查、人工平台路径审查、人工法律 / 合规审查、真实 Runtime 设置页验证、隐私说明文本和 Release Candidate 证据。

Runtime 当前实现状态：

- `--platform-data-root <path>` 会把默认存档、Runtime 设置、本地遥测、Replay 和崩溃报告目录绑定到同一逻辑平台数据根；默认逻辑根为 `platform_user_data/soft-candy-storm`，并按 `saves`、`settings`、`telemetry`、`replay`、`crash-reports` 五个子目录拆分。
- `--native-platform-data-root` 会显式把同一组默认路径绑定到系统原生数据目录：macOS 为 `~/Library/Application Support/Soft Candy Storm`，Windows 为 `%APPDATA%/Soft Candy Storm`，Linux / Unix 为 `${XDG_DATA_HOME:-~/.local/share}/soft-candy-storm`。
- `--runtime-settings-file <path>` 可读取 `telemetry_upload_enabled`、`raw_replay_upload_enabled`、`crash_report_upload_enabled`，默认全部关闭。
- `--print-privacy-notice` 可输出本地优先、默认关闭、明确同意、删除 / 导出、禁止个人身份信息和 90 天保留主题。
- `--export-local-data <path>` 可导出本地遥测 / replay JSON 文件内容，并附带当前隐私设置。
- `--delete-local-data` 可删除显式传入的本地遥测 / replay 目录内容；为了避免误删开发证据，未传 `--local-data-dir` 时会拒绝执行。
- Runtime 已有 `F4` 隐私设置页，可显式切换三个上传同意项并在配置了 `--runtime-settings-file` 时写回 JSON，也可用 `E/X/L/K` 触发当前 Runtime 配置下的存档导出、存档删除、本地数据导出和本地数据删除；人工隐私审查已有模板、审查包和完整性校验器，但尚未由真人填写通过。源码层已有逻辑平台路径默认绑定和显式原生平台目录解析入口，但法律审查、上传传输、人工平台路径审查、发布级导出 / 删除按钮验证仍未完成，因此 Release Candidate 仍不得标为通过。

当前校验命令：

```bash
python3 harness/telemetry_privacy/validate_telemetry_privacy_policy.py \
  harness/telemetry_privacy/telemetry_privacy_policy_template.json \
  --report harness/reports/2026-05-26_telemetry_privacy_policy_001/telemetry_privacy_policy.json \
  --markdown harness/reports/2026-05-26_telemetry_privacy_policy_001/summary.md

python3 harness/telemetry_privacy/validate_runtime_privacy_settings_contract.py \
  harness/telemetry_privacy/runtime_privacy_settings_contract_v0.json \
  --policy harness/telemetry_privacy/telemetry_privacy_policy_template.json \
  --save-contract harness/save_contract/save_state_v0_template.json \
  --report harness/reports/2026-05-26_runtime_privacy_settings_contract_001/runtime_privacy_settings_contract.json \
  --markdown harness/reports/2026-05-26_runtime_privacy_settings_contract_001/summary.md

python3 harness/telemetry_privacy/validate_upload_transport_contract.py \
  harness/telemetry_privacy/upload_transport_contract_v0.json \
  --policy harness/telemetry_privacy/telemetry_privacy_policy_template.json \
  --runtime-contract harness/telemetry_privacy/runtime_privacy_settings_contract_v0.json \
  --report harness/reports/2026-05-26_upload_transport_contract_001/upload_transport_contract.json \
  --markdown harness/reports/2026-05-26_upload_transport_contract_001/summary.md

python3 harness/telemetry_privacy/create_manual_privacy_review_packet.py \
  --review-template harness/telemetry_privacy/manual_privacy_review_template.json \
  --repo-root . \
  --out harness/reports/2026-05-26_manual_privacy_review_packet_001/summary.md

python3 harness/telemetry_privacy/validate_manual_privacy_review.py \
  harness/telemetry_privacy/reviews/<review>.json \
  --repo-root . \
  --report harness/reports/<manual-privacy-review>/manual_privacy_review.json \
  --markdown harness/reports/<manual-privacy-review>/summary.md

python3 harness/telemetry_privacy/create_manual_legal_review_packet.py \
  --review-template harness/telemetry_privacy/manual_legal_review_template.json \
  --repo-root . \
  --out harness/reports/2026-05-26_manual_legal_review_packet_001/summary.md

python3 harness/telemetry_privacy/validate_manual_legal_review.py \
  harness/telemetry_privacy/reviews/<legal-review>.json \
  --repo-root . \
  --report harness/reports/<manual-legal-review>/manual_legal_review.json \
  --markdown harness/reports/<manual-legal-review>/summary.md

python3 harness/telemetry_privacy/create_telemetry_privacy_acceptance_review_packet.py \
  --repo-root . \
  --report harness/reports/2026-05-26_telemetry_privacy_acceptance_review_packet_001/telemetry_privacy_acceptance_review_packet.json \
  --markdown harness/reports/2026-05-26_telemetry_privacy_acceptance_review_packet_001/summary.md
```

上传传输契约当前结论为 `upload_transport_contract_valid` 且 `implementation_status=planned`。它只证明未来上传链路的 payload、队列、同意、raw replay 和发布证据边界可校验；不证明 Runtime 已经实现网络上传、队列 flush、平台隐私合规或法律审查。人工法律 / 合规审查包只汇总绑定证据、报告引用、辖区范围占位、上传默认关闭状态、禁止字段、发布要求和 9 个 TODO 检查项；真人填写并通过前不能作为法律、平台或 Release Candidate 通过证据。最终接受证据包当前为 `telemetry_privacy_acceptance_review_packet_needs_evidence`，因为人工隐私、平台路径和法律 / 合规审查仍是 TODO 模板，上传传输仍是 `planned`，RC `telemetry_privacy` gate 仍是 `waiting`。

Runtime 局外设置和本地数据入口还有独立源码形状契约：

```bash
python3 harness/runtime_contract/validate_runtime_surface_contract.py \
  harness/runtime_contract/runtime_surface_contract_v0.json \
  --repo-root . \
  --report harness/reports/2026-05-26_runtime_surface_contract_001/runtime_surface_contract.json \
  --markdown harness/reports/2026-05-26_runtime_surface_contract_001/summary.md
```

该契约会检查 `game_runtime` 源码中是否仍保留 `--platform-data-root`、`--native-platform-data-root`、`--character-id`、`--runtime-settings-file`、`--export-local-data`、`--delete-local-data`、`--print-privacy-notice`、`--save-file`、`--export-save`、`--delete-save`，以及 F1/F2/F3/F4/F5 局外面板、C/M 角色 / 地图选择、7/8/9 上传同意切换、`platform_user_data/soft-candy-storm` 逻辑目录、`Soft Candy Storm` / `soft-candy-storm` 原生平台目录片段和 `not_implemented` 上传传输提示。当前结论为 `runtime_surface_contract_valid`，但它只证明源码形状，不证明键盘行为、渲染 UI、人工平台路径审查通过、平台云存档或上传传输行为。

## 本地存档与数据控制

局外存档属于本地优先数据，也必须遵守遥测隐私原则。存档契约位于：

```text
harness/save_contract/save_state_v0_template.json
harness/save_contract/save_state_v1_template.json
harness/save_contract/platform_save_path_policy_v0.json
harness/save_contract/README.md
```

该契约要求：

- 上传型遥测、raw replay 上传和崩溃报告上传默认关闭。
- 存档声明 `local_only_by_default` 和 `upload_requires_opt_in`。
- 必须提供删除存档和导出存档的控制项。
- 导出格式首版固定为 JSON。
- 存档字段不得包含个人身份、IP、本地绝对路径、自由文本输入或 raw replay 输入。

当前校验命令：

```bash
python3 tools/validate_save_state_contract.py \
  harness/save_contract/save_state_v0_template.json \
  --report harness/reports/2026-05-26_save_state_contract_001/save_state_contract.json \
  --markdown harness/reports/2026-05-26_save_state_contract_001/summary.md

python3 tools/validate_save_state_contract.py \
  harness/save_contract/save_state_v1_template.json \
  --report harness/reports/2026-05-26_save_state_contract_v1_001/save_state_contract.json \
  --markdown harness/reports/2026-05-26_save_state_contract_v1_001/summary.md

python3 tools/validate_save_path_policy.py \
  harness/save_contract/platform_save_path_policy_v0.json \
  --report harness/reports/2026-05-26_save_path_policy_v0_001/save_path_policy.json \
  --markdown harness/reports/2026-05-26_save_path_policy_v0_001/summary.md

python3 harness/save_contract/create_manual_platform_path_review_packet.py \
  --review-template harness/save_contract/manual_platform_path_review_template.json \
  --repo-root . \
  --out harness/reports/2026-05-26_manual_platform_path_review_packet_001/summary.md

python3 tools/validate_manual_platform_path_review.py \
  harness/save_contract/manual_platform_path_review_template.json \
  --repo-root . \
  --report harness/reports/2026-05-26_manual_platform_path_review_template_001/manual_platform_path_review.json \
  --markdown harness/reports/2026-05-26_manual_platform_path_review_template_001/summary.md
```

该校验只证明本地存档模板具备删除 / 导出控制和隐私默认值；v1 还要求 `migration_history` 与 `base_ui_state`，平台路径策略还要求存档、设置、遥测、Replay 和崩溃报告使用逻辑平台目录并禁止宿主绝对路径。Runtime 源码现在已把默认路径绑定到同一逻辑平台数据根，并可通过 `--native-platform-data-root` 显式切换到系统原生数据目录；删除本地数据时仍必须显式传入 `--local-data-dir`，删除存档时仍必须显式传入 `--save-file`。人工平台路径审查包只汇总策略、存档契约、逻辑存储根、禁止片段和 TODO 检查项；模板当前结论仍为 `manual_platform_path_review_invalid`，真人填写并通过前不能作为发布证据。当前报告不代表运行级迁移样本、设置页人工验证、平台隐私文本、云存档或上传链路已经通过。

未来存档升级必须继续遵守这些本地优先和 opt-in 规则。当前迁移计划可用以下命令校验：

```bash
python3 tools/validate_save_migration_plan.py \
  harness/save_contract/save_migration_plan_v0_to_v1.json \
  --repo-root . \
  --report harness/reports/2026-05-26_save_migration_plan_v0_to_v1_001/save_migration_plan.json \
  --markdown harness/reports/2026-05-26_save_migration_plan_v0_to_v1_001/summary.md \
  --allow-planned
```

该计划要求迁移不得默认开启上传型遥测、raw replay 上传或崩溃报告上传，并要求局外进度、图鉴、章节和本地数据控制被保留。当前结论只是 `save_migration_plan_planned`，v1 目标模板已可校验；Runtime 迁移源码路径和一个本地 v0 样本 smoke 已通过，但历史真实用户存档批量迁移、人工平台路径审查和云存档策略仍未完成。
