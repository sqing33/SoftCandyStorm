# GameCore Determinism And Snapshot Contract

## 结论

- Decision: `gamecore_determinism_snapshot_contract_valid`
- Scope: `crates/game_core`
- Contract: `harness/interface_contract/gamecore_api_contract_v0.json`
- Source-shape contract: `gamecore_api_contract_valid`

本报告刷新 docs/14 所需的 GameCore 接口证据。它覆盖三类自动检查：公开 API 源码形状、固定 seed 指标复现、Snapshot 对投射物 / hazard / Boss 观察面的暴露。

## Commands

```bash
cargo test -p game_core same_seed_produces_same_metrics -- --nocapture
cargo test -p game_core snapshot -- --nocapture
python3 tools/validate_gamecore_api_contract.py harness/interface_contract/gamecore_api_contract_v0.json --repo-root . --report harness/reports/2026-05-29_gamecore_determinism_snapshot_contract_001/gamecore_api_contract.json --markdown harness/reports/2026-05-29_gamecore_determinism_snapshot_contract_001/gamecore_api_contract.md
python3 tools/test_validate_gamecore_api_contract.py
```

## Results

| Check | Result |
| --- | --- |
| `same_seed_produces_same_metrics` | `1 passed` |
| Snapshot tests | `3 passed` |
| API contract validator | `gamecore_api_contract_valid` |
| API contract validator unit tests | `4 passed` |

Snapshot test coverage:

- `projectile_snapshot_exposes_active_projectiles`
- `hazard_snapshot_exposes_active_hazards`
- `snapshot_reports_nearest_boss_when_multiple_alive`

## 判断

- 固定 seed 语义已有定向单测证据，当前同 seed metrics 可复现。
- Snapshot 面已覆盖 projectile、hazard 和 nearest boss 三类 Runtime / Bot / Gym 观察入口。
- 源码形状契约仍只证明接口字段和边界存在，不替代 Replay 长局回归、Runtime 人工可读性或 Gym high-pressure 策略通过。
