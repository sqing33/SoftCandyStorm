# Runtime Codex Gamepad Input

- Decision: `runtime_codex_gamepad_input_valid`
- Scope: `game_runtime` F3 codex gamepad category, entry, and filter input

## Implemented

- F3 图鉴页现在在键盘和鼠标之外接受 Bevy 手柄按钮输入。
- 手柄 `LT` 映射到上一类图鉴分类，等价于 `Q`。
- 手柄 `RT` 映射到下一类图鉴分类，等价于 `E`。
- 手柄十字键左 / 右映射到上一条 / 下一条图鉴条目，等价于 `B/N`。
- 手柄 `Y` / `North` 映射到仅已发现 / 全部条目过滤切换，等价于 `V`。
- 输入 helper 读取 `ButtonInput<GamepadButton>` 中的 `GamepadButtonType`，不把 UI 动作绑定到单一物理手柄 id。
- F3 帮助文本同步展示键盘、鼠标和手柄入口。

## Verification

- `cargo test -p game_runtime`: 70 passed
- `cargo test --workspace`: 135 passed
- `cargo clippy --workspace --all-targets`: passed
- `cargo fmt --check`: passed
- `python3 harness/runtime_contract/validate_runtime_surface_contract.py ...`: `runtime_surface_contract_valid`
- `python3 harness/runtime_contract/test_validate_runtime_surface_contract.py`: 6 passed
- `python3 tools/validate_base_ui_manual_review.py ...`: `base_ui_manual_review_invalid`，符合模板仍需真人填写的预期
- `python3 tools/test_validate_base_ui_manual_review.py`: 7 passed
- `python3 tools/validate_docs_implementation_coverage.py ... --allow-incomplete`: `docs_implementation_incomplete`，符合长目标未完成的预期
- `python3 tools/test_validate_docs_implementation_coverage.py`: 5 passed
- `python3 tools/validate_progress_reports.py ...`: `progress_reports_valid`
- `python3 tools/test_validate_progress_reports.py`: 6 passed
- `python3 tools/validate_goal_evidence_consistency.py ...`: `goal_evidence_consistent`
- `python3 tools/test_validate_goal_evidence_consistency.py`: 5 passed

## Limitations

- 这是文本面板手柄输入原型，不是完整视觉可点击图鉴布局。
- 当前证据来自源码形状与单测，不是真实物理手柄人工审查。
- 只读取当前 Runtime 内容包元数据和 `MetaProgress`，不加载 generated story/codex candidate 正文。
- 不替代剧情人工审校、Runtime UI review、final human acceptance、基地 UI 人工审查、Bevy smoke 或发布门禁。
