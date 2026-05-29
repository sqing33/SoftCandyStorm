# Terminal Conversion Victory Sample Filter Smoke

## Decision

`terminal_conversion_victory_samples_filtered_not_policy_gate`

This report validates a training-input tool for the next terminal-conversion branch attempt. It is not a policy gate, not an acceptance result, and does not clear the current RL blocker.

## Scope

- Source: `harness/reports/2026-05-27_rl_rule_bot_late_survival_trajectory_001`
- Filter tool: `tools/filter_bot_trajectory_samples.py`
- Target map: `cracked-star-jar`
- Terminal filter: `victory`
- Time window: `210-240s`
- Output dataset: `cracked_victory_terminal_210_240.jsonl`

## Filter Result

- Source files: `8`
- Source samples: `12007`
- Source episodes: `31`
- Kept samples: `358`
- Kept episodes: `2`
- Kept terminal distribution: `victory: 2`
- Kept bot distribution: `kite: 2`
- Dropped samples: `time_before_min: 359`, `time_after_max: 719`

The output JSONL has `362` records: one metadata row, `358` movement samples, two episode rows, and one summary row.

## Behavior Clone Dry Run

`train_behavior_clone.py --dry-run` accepted the filtered dataset:

- Status: `ok`
- Gate decision: `dataset_validated_not_training_gate`
- Sample count: `358`
- Episode count: `2`
- Observation length: `145`
- Action count: `9`
- Time range: `210.0159-239.8556s`
- Health ratio range: `0.1994-0.9687`
- Late phase ratio: `1.0`
- Late low-health ratio: `0.581`

The action distribution is non-empty across actions `1-8`, but action `0` is absent. Sequence diagnostics also flags `high_action_persistence` as `watch`, with same-action ratio `0.7612`.

## Harness Review

Passed:

- The filter preserves bot trajectory movement samples with metadata, episode rows, and summary.
- The output can be consumed by the behavior-clone dataset loader.
- The filtered rows are scoped to a real victory terminal window on `cracked-star-jar`.

Not passed:

- No model was trained in this smoke.
- No SB3 distillation, anchor alignment, fixed-window comparison, online action-distribution delta gate, replay regression, or repair-probe gate was run.
- The sample count is small and only covers two victory episodes on one map.

## Next Step

Use this filtered victory-window dataset as a narrow positive terminal-conversion target, mixed with parent/e30 retention anchors and existing risk / drift repair rows. Any learned branch must still pass full-anchor alignment, 60/180/300 second high-pressure comparisons, e30 and parent no-regression, online action-distribution delta checks, failure analysis, and the repair-probe gate.
