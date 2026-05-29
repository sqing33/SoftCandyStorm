# Runtime Loadout Click Zone

- Decision: `runtime_loadout_click_zone_valid`
- Scope: `game_runtime` F5 patrol loadout right-bottom segmented pointer control zone

## Implemented

- F5 巡逻准备页新增鼠标左键两段点击区，点击区只在右侧局外面板范围和控制高度内生效。
- 两段从左到右映射为切换已解锁角色和切换已解锁地图。
- 点击入口复用 `RuntimeLoadoutAction`，并继续落到现有 `select_next_runtime_character` / `select_next_runtime_map` 路径。
- 角色或地图切换后仍会重开当前巡逻、保留局外进度，并沿用现有错误提示和音效路径。
- F5 文本面板、Runtime surface contract 和基地 UI 人工审查模板已同步记录该入口。

## Verification

- `cargo test -p game_runtime`: 78 passed
- `cargo test --workspace`: 143 passed
- `cargo clippy --workspace --all-targets`: passed
- `cargo fmt --check`: passed
- `python3 harness/runtime_contract/validate_runtime_surface_contract.py ...`: `runtime_surface_contract_valid`
- `python3 tools/validate_base_ui_manual_review.py ...`: `base_ui_manual_review_invalid`，符合模板仍需真人填写的预期
- `python3 harness/runtime_contract/test_validate_runtime_surface_contract.py`: 6 passed
- `python3 tools/test_validate_base_ui_manual_review.py`: 7 passed
- `python3 tools/validate_docs_implementation_coverage.py ... --allow-incomplete`: `docs_implementation_incomplete`，符合长目标未完成的预期
- `python3 tools/test_validate_docs_implementation_coverage.py`: 5 passed
- `python3 tools/validate_progress_reports.py ...`: `progress_reports_valid`
- `python3 tools/test_validate_progress_reports.py`: 6 passed
- `python3 tools/validate_goal_evidence_consistency.py ...`: `goal_evidence_consistent`
- `python3 tools/test_validate_goal_evidence_consistency.py`: 5 passed

## Limitations

- 这是文本面板分段点击区，不是发布级视觉按钮布局。
- 当前证据来自源码形状与单测，不是真实鼠标设备人工审查。
- 该入口只循环 `MetaProgress` 中已解锁角色和地图，不解锁新内容，也不绕过内容接受门禁。
- 不替代基地 UI 人工审查、真实设备审查、人工试玩、完整视觉基地 UI 或发布门禁。
