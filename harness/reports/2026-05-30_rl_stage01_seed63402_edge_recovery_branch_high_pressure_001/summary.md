# Stage 01 Seed 63402 Edge Recovery Branch High Pressure

- Decision: `parent_no_regression_passed_but_300s_policy_repair_needed`
- Base model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Branch model: `harness/reports/2026-05-30_rl_stage01_seed63402_edge_recovery_supervised_dataset_actions_001/seed63402_edge_recovery_supervised_dataset_actions.zip`
- Adapter: `edge_recovery_branch`
- Scope: high-pressure maps, seeds `63400-63402`, windows `60s`, `180s`, `300s`

## Results

| Window | Parent avg win | Branch avg win | Key result |
|---|---:|---:|---|
| `60s` | `0.7778` | `0.8889` | `soda-creek` improved `0.6667 -> 1.0` |
| `180s` | `0.6667` | `0.7778` | `soda-creek` improved `0.6667 -> 1.0` |
| `300s` | `0.0` | `0.0` | no 300s victories; `soda-creek` average survival improved `143.0974s -> 221.8073s` |

## Gate

`validate_policy_window_regression.py` passed across `60s`, `180s`, and `300s` with no blockers. The branch did not regress non-target maps, because dispatch is limited to `soda-creek` and the opening window.

The branch still fails the policy repair gate at `300s`: high-pressure `soda-creek`, `caramel-workshop`, and `cracked-star-jar` all remain at `0.0` policy win rate. This confirms the branch is useful as a narrow stage 01 opening repair, but it does not solve late-window route recovery or win conversion.

## Validation

- `parent_comparison_60s.json`, `branch_comparison_60s.json`
- `parent_comparison_180s.json`, `branch_comparison_180s.json`
- `parent_comparison_300s.json`, `branch_comparison_300s.json`
- `window_regression_60_180_300s.json`: `policy_window_regression_passed`.
- `policy_adapter_scope.json`: `policy_adapter_scope_passed`; `18 / 108848` branch decisions, all non-zero branch usage stayed within `soda-creek` and `opening_lt_60`.
- `repair_probe_gate_adapter_scope_smoke.json`: `rl_repair_probe_gate_passed_for_limited_followup` with required window regression and required adapter scope inputs.
- `branch_samples_60s_soda-creek_validation.json`: `edge_recovery_samples_valid`.
- `branch_samples_180s_soda-creek_validation.json`: `edge_recovery_samples_valid`.
- `branch_samples_300s_soda-creek_validation.json`: `edge_recovery_samples_valid`.
- Failure case: `harness/failed_cases/fail_20260530_014_stage01_edge_recovery_branch_long_window_gap.json`.
- `progress_validation.json`: progress references valid.
- `docs_implementation_coverage_validation.json`: coverage ledger structurally valid with incomplete docs allowed for active Goal mode.
- `roadmap_phase_audit_validation.json`: roadmap audit structurally valid with incomplete phases allowed for active Goal mode.
- `goal_evidence_consistency.json`: Goal evidence references consistent.
- `goal_blockers_audit.json`: current blockers recorded with `--allow-blockers`.
- `failure_case_validation.json`: failure case records valid.
- `git diff --check`: passed.
