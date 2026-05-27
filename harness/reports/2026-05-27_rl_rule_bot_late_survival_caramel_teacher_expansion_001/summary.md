# RL Caramel Late Survival Teacher Expansion

- Decision: `caramel_clean_teacher_expansion_recorded`
- Scope: `caramel-workshop` TankBot clean teacher search and late-window trajectory export
- New clean teacher seed: `62405`
- Output trajectory: `tank_caramel_workshop_seed62405_late_180_300.jsonl`

## Seed Scan

Two additional TankBot windows were scanned on `caramel-workshop`:

| Report | Seeds | Victories | Win Rate | Average Survival | Notes |
|---|---:|---:|---:|---:|---|
| `2026-05-27_rl_rule_bot_late_survival_probe_caramel_workshop_tank_extra_001` | 20 | 0 | 0.0% | 177.485s | No clean teacher found |
| `2026-05-27_rl_rule_bot_late_survival_probe_caramel_workshop_tank_extra_002` | 50 | 1 | 2.0% | 173.610s | Seed `62405` won |

Seed `62405` is a strong clean teacher candidate: it reached `300.01498s`, killed `512` enemies, reached level `8`, and took only `11.266667` damage.

## Export

The new teacher trajectory was exported with observation v2, `sample_stride = 5`, and a `180-300s` sample window. The export produced:

- `719` movement samples.
- `1` episode.
- `1` victory.
- `0` upgrade samples.
- `3` skipped upgrade prompts.
- `content_hash = fnv1a64:4ad1c52ac3f1285b`.

## Expanded Clean Teacher Dry Run

The expanded clean teacher dataset combines:

- `kite_soda_creek_late_180_300.jsonl`
- `kite_cracked_star_jar_late_180_300.jsonl`
- `tank_caramel_workshop_seed62301_late_180_300.jsonl`
- `tank_caramel_workshop_seed62405_late_180_300.jsonl`

Dry-run results:

| Metric | Value |
|---|---:|
| Samples | `6843` |
| Episodes | `12` |
| `caramel-workshop` share | `21.03%` |
| `soda-creek` share | `45.71%` |
| `cracked-star-jar` share | `33.26%` |
| Average health ratio | `0.6731` |
| Late low-health ratio | `51.48%` |
| Largest action ratio | action `3` / `15.42%` |

The added seed improves `caramel-workshop` representation from `11.76%` to `21.03%`, but the dataset remains smaller on that map than on `soda-creek`. It is clean trajectory data only and contains no adapter-derived repair samples.

## Boundary

This report is data coverage evidence only. It is not a trained policy, not an RL policy gate, and not `rl_test_bot_candidate` evidence. Any model using this expanded teacher set must still pass deterministic high-pressure `60s`, `180s`, and `300s` comparisons, then the normal RL policy acceptance manifest.
