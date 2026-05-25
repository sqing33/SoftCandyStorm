# Prototype Top-Down Runtime Assets

This pack contains programmatic placeholder assets for the Bevy Runtime prototype.

These files are not AI-generated final art. They exist to replace temporary geometry blocks with stable top-down silhouettes while `mmx` and other generated art remains in candidate review.

## Scope

- Player: `jar-keeper`
- Enemies: `bouncy-gummy`, `sour-gummy`, `caramel-slime`, `sandwich-cookie-creep`
- Boss: `runaway-sugar-mixer`
- Pickup: candy crystal XP
- Projectile: rainbow candy shot
- Map tile: frosting grassland placeholder

## Rules

- Source: `tools/generate_prototype_assets.py`
- Style: cute candy, rounded, high-contrast, top-down readable
- Runtime status: integrated by `crates/game_runtime`
- Final-art status: not final art

AI-generated candidates must still stay in `asset/generated_candidates/` until reviewed. Final promoted art must keep source, prompt or authoring notes, version, and post-processing metadata.
