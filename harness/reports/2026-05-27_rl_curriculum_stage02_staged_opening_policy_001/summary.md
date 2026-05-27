# RL Curriculum Stage 02 Staged Opening Policy

- Decision: `stage02_staged_opening_mid_regression`
- Opening model: `harness/reports/2026-05-27_rl_curriculum_stage01_corner_risk_delta_smoke_001/stage01_corner_risk_delta_smoke.zip`
- Fallback model: `harness/reports/2026-05-27_rl_curriculum_stage02_opening_edge_delta_001/stage02_opening_edge_delta.zip`
- Opening duration: `60s`
- Failure case: `harness/failed_cases/fail_20260527_027_stage02_staged_opening_mid_regression.json`

## Change Under Test

- Used the stage 01 `corner_risk_delta` checkpoint only for the first `60s`.
- Switched to the stage 02 `opening_edge_delta` checkpoint after the opening window.
- This is an evaluation-only staged SB3 wrapper. It does not train a new checkpoint and is not policy acceptance evidence by itself.

## 60s Opening Gate

| Map | Win Rate | Avg Survival | Dominant Action | Entropy |
|---|---:|---:|---|---:|
| `soda-creek` | 100.00% | 60.0328s | `7` / 49.37% | 0.4951 |
| `caramel-workshop` | 100.00% | 60.0328s | `7` / 38.71% | 0.5161 |
| `cracked-star-jar` | 100.00% | 60.0328s | `4` / 33.10% | 0.5715 |

The staged wrapper preserves the stage 01 opening behavior across the same `62400-62409` high-pressure seed window that the stage 02 edge-delta continuation failed.

## 180s Mid-Window Regression

| Map | Win Rate | Avg Survival | Dominant Action | Entropy |
|---|---:|---:|---|---:|
| `soda-creek` | 66.67% | 158.5170s | `7` / 45.44% | 0.5193 |
| `caramel-workshop` | 100.00% | 180.0095s | `7` / 45.24% | 0.5075 |
| `cracked-star-jar` | 100.00% | 180.0095s | `4` / 50.22% | 0.4465 |

`soda-creek` failure:

- seed `62201` died at `115.5319s`
- bucket: `mid_60_to_180`
- terminal reason: `player_health_depleted`
- level: `4`
- kills: `168`
- damage taken: `120.1636`
- dominant action: `7` / `59.32%`

## Conclusion

Separating the opening policy is a useful diagnostic direction: it restores the 60-second high-pressure opening gate to 100% across all three maps. It does not solve stage 02, because the fallback model still fails in the `soda-creek` mid-window after the 60-second handoff.

This checkpoint cannot enter stage 03 and is not RL policy acceptance evidence. The next repair should focus on the handoff and `60-180s` recovery window, not on adding another opening-only scalar reward.

## Next

- Generate failed-only trace for staged policy `soda-creek` seed `62201`.
- Compare frames around the 60-second handoff and the 115-second death window.
- Try mid-window replay, behavior constraints, or a dedicated mid policy only after preserving the 60-second opening gate.
