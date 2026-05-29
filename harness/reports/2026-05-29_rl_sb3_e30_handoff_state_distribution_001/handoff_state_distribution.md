# SB3 Handoff State Distribution

- Decision: `sb3_handoff_state_distribution_recorded`
- Base model: `harness/reports/2026-05-29_rl_sb3_e30_mid_anchor_guarded_probe_001/ppo_e30_mid_anchor_guarded_probe.zip`
- Late model: `harness/reports/2026-05-29_rl_sb3_e30_opening_mid_retention_late_probe_001/ppo_e30_opening_mid_retention_late_probe.zip`
- Trace count: `3`
- Samples: `458`
- Window: `120.0` to `240.0` seconds

## Overall

- Mean base-to-late KL: `0.000491`
- Argmax agreement: `0.9978`
- Base top action: `8` / 28.17%
- Late top action: `8` / 28.17%

## Window Summary

| Window | Samples | Mean KL | Argmax Agreement | Base Top | Late Top | Health Mean | Boundary Min Mean |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `post_split` | 220 | 0.000362 | 1.0 | `5` / 31.36% | `5` / 31.36% | 54.6584 | 63.348 |
| `pre_split` | 238 | 0.00061 | 0.9958 | `8` / 31.93% | `8` / 31.93% | 74.6637 | 15.6039 |

## Findings

- No automatic finding thresholds were triggered.

## Top KL Examples

- seed `63102` time `166.5066` trace `3` base `3` late `3` KL `0.001746` health `94.0031`
- seed `63102` time `155.0042` trace `3` base `3` late `3` KL `0.001726` health `94.0031`
- seed `63102` time `162.0057` trace `3` base `3` late `3` KL `0.001687` health `94.0031`
- seed `63102` time `162.5058` trace `3` base `3` late `3` KL `0.001685` health `94.0031`
- seed `63102` time `175.0084` trace `3` base `3` late `3` KL `0.001681` health `94.0031`
- seed `63102` time `155.5043` trace `3` base `3` late `3` KL `0.001671` health `94.0031`
- seed `63102` time `165.5064` trace `3` base `3` late `3` KL `0.001654` health `94.0031`
- seed `63102` time `154.0039` trace `3` base `3` late `3` KL `0.001596` health `94.0031`
- seed `63102` time `166.0065` trace `3` base `3` late `3` KL `0.001574` health `94.0031`
- seed `63102` time `157.0046` trace `3` base `3` late `3` KL `0.001552` health `94.0031`
- seed `63102` time `164.0061` trace `3` base `3` late `3` KL `0.00155` health `94.0031`
- seed `63102` time `174.0082` trace `3` base `3` late `3` KL `0.0015` health `94.0031`

## Limitations

- This compares policy scores on sampled trace observations only.
- Trace observations are produced by Gym evaluation and are not full Replay snapshots.
- This diagnostic does not train, repair, or approve a policy candidate.
