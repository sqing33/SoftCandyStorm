# Stage 01 Seed 63402 Guard Anchor Strength Probe

- Decision: `repair_failed`
- Start model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Guard samples: `harness/reports/2026-05-30_rl_stage01_seed63402_target_guard_samples_001/seed63402_target_guard_samples.jsonl`
- Checkpoint: `harness/reports/2026-05-30_rl_stage01_seed63402_guard_anchor_strength_probe_001/stage01_seed63402_guard_anchor_strong.zip`
- Reward profile: `opening-boundary-escape`

## Results

| Check | Result |
|---|---|
| Guard anchor configuration | `17` opening samples, target action `7`, anchor weight `1.0`, `20` KL epochs, anchor lr `0.001` |
| PPO anchor validation | final validation KL `0.178923`, argmax agreement `1.0`; validation guard was not configured |
| Offline guard alignment | `behavior_clone_anchor_alignment_within_thresholds`, mean KL `0.16974`, argmax agreement `1.0`, `0` blockers |
| 60s high-pressure | average win rate `0.7778`; `soda-creek` only `0.3333`, seed `63402` still defeated at `45.2330s` |
| 180s high-pressure | average win rate `0.5556`; `soda-creek` `0.0`, `cracked-star-jar` `0.6667` |
| 300s high-pressure | `0.0/0.0/0.0`; average survival `160.1956s` |
| Parent no-regression | `policy_window_regression_failed`, `8` blockers |

## Blockers

- `60s/soda-creek`: win rate `-0.3334`, average survival `-7.7221s`.
- `180s/soda-creek`: win rate `-0.6667`, average survival `-56.1942s`.
- `180s/cracked-star-jar`: win rate `-0.3333`, average survival `-8.7352s`.
- `300s/soda-creek`: average survival `-83.3869s`.
- `300s/cracked-star-jar`: average survival `-13.5474s`.

## Conclusion

The stronger local guard objective can force the SB3 policy to match the `17` offline guard rows, but that alignment does not transfer safely to closed-loop play. The checkpoint shifts online behavior toward action `1` / `8`, fails to repair the target `soda-creek` opening seed, and causes parent no-regression failures across the 60 / 180 / 300 second windows.

This checkpoint must not enter stage 02, stage 03, RL test Bot candidacy, or acceptance. The next attempt should not simply raise guard strength again; it needs an online preflight for seed `63402`, a broader successful-opening retention anchor, or a staged / constrained repair that checks target improvement and parent preservation before full-window evaluation.

## Validation

- `failure_case_validation.json`: `failure_cases_valid`.
- `docs_coverage_validation.json`: `docs_implementation_incomplete` with no validation errors.
- `progress_validation.json`: `progress_reports_valid`.
- `roadmap_validation.json`: `roadmap_phase_audit_incomplete` with no validation errors.
- `goal_consistency.json`: `goal_evidence_consistent`.
- `blocker_audit.json`: `goal_blockers_present` for known manual evidence, Release Candidate, release package, docs coverage, and roadmap blockers.
- `git diff --check`: passed.
