# Runtime Settings Click Zone

- Decision: `runtime_settings_click_zone_valid`
- Scope: `game_runtime` F4 privacy and local-data right-bottom segmented pointer control zone

## Implemented

- F4 隐私与本地数据页新增鼠标左键七段点击区，点击区只在右侧局外面板范围和控制高度内生效。
- 七段从左到右映射为匿名遥测、raw replay、崩溃报告、导出存档、删除存档、导出本地数据和删除本地数据。
- 点击入口复用 `RuntimeSettingsAction`，并继续落到现有隐私设置、存档导出、本地数据导出和删除确认逻辑。
- 删除存档点击段仍需要再次触发同一删除 action 才会真正删除；没有绕过 `X/K` 的二次确认语义。
- F4 文本面板和 Runtime surface contract 已同步记录该入口，基地 UI 人工审查模板也加入对应检查项。

## Verification

- `cargo test -p game_runtime`: 75 passed
- `cargo test --workspace`: 140 passed
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
- 该入口不实现网络上传，也不改变默认本地优先隐私策略。
- 不替代人工隐私审查、法律 / 合规审查、平台路径审查、基地 UI 人工审查、Bevy smoke、人工试玩或发布门禁。
