use bevy::{
    asset::AssetPlugin,
    audio::{AudioBundle, AudioSource, PlaybackSettings, Volume},
    prelude::*,
};
use game_core::{
    ContentPack, Difficulty, FixedDt, GameCore, GameEvent, PlayerAction, RunConfig, RunMetrics,
    RunSnapshot, StartingLoadout, TerminalKind, TerminalState, Vec2 as CoreVec2,
};
use serde::Serialize;
use std::{fs, path::PathBuf, sync::Arc};

const DEFAULT_CONTENT_DIR: &str = "content/base_demo";
const CAMERA_Z: f32 = 999.0;
const EFFECT_Z: f32 = 35.0;
const PLAYER_Z: f32 = 20.0;
const PROJECTILE_Z: f32 = 15.0;
const ENEMY_Z: f32 = 10.0;
const PICKUP_Z: f32 = 5.0;
const MAP_Z: f32 = -20.0;
const MAP_BORDER_Z: f32 = -19.0;
const PLACEHOLDER_SAMPLE_RATE: u32 = 22_050;
const MAX_RUNTIME_EFFECTS: usize = 96;
const PLAYER_SPRITE: &str = "prototype_topdown/sprites/player_jar_keeper_v001.png";
const BOUNCY_GUMMY_SPRITE: &str = "prototype_topdown/sprites/enemy_bouncy_gummy_v001.png";
const SOUR_GUMMY_SPRITE: &str = "prototype_topdown/sprites/enemy_sour_gummy_v001.png";
const CARAMEL_SLIME_SPRITE: &str = "prototype_topdown/sprites/enemy_caramel_slime_v001.png";
const SANDWICH_COOKIE_SPRITE: &str =
    "prototype_topdown/sprites/enemy_sandwich_cookie_creep_v001.png";
const BOSS_MIXER_SPRITE: &str = "prototype_topdown/sprites/boss_runaway_sugar_mixer_v001.png";
const PICKUP_CRYSTAL_SPRITE: &str = "prototype_topdown/sprites/pickup_candy_crystal_v001.png";
const PROJECTILE_SPRITE: &str = "prototype_topdown/sprites/projectile_rainbow_candy_shot_v001.png";
const MAP_TILE_SPRITE: &str = "prototype_topdown/sprites/map_frosting_grassland_tile_v001.png";

fn main() {
    App::new()
        .insert_resource(ClearColor(Color::srgb(0.95, 0.91, 0.78)))
        .add_plugins(
            DefaultPlugins
                .set(WindowPlugin {
                    primary_window: Some(Window {
                        title: "Soft Candy Storm Runtime Prototype".to_string(),
                        resolution: (1280.0, 720.0).into(),
                        present_mode: bevy::window::PresentMode::AutoVsync,
                        ..default()
                    }),
                    ..default()
                })
                .set(AssetPlugin {
                    file_path: runtime_asset_root(),
                    ..default()
                }),
        )
        .add_systems(Startup, setup_runtime)
        .add_systems(
            Update,
            (
                step_game_core,
                play_runtime_audio.after(step_game_core),
                update_runtime_effects.after(step_game_core),
                capture_playtest_report.after(update_runtime_effects),
                sync_camera.after(step_game_core),
                sync_world_visuals.after(update_runtime_effects),
                update_hud.after(step_game_core),
            ),
        )
        .run();
}

fn runtime_asset_root() -> String {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../../assets")
        .display()
        .to_string()
}

#[cfg(test)]
fn runtime_sprite_paths() -> &'static [&'static str] {
    &[
        PLAYER_SPRITE,
        BOUNCY_GUMMY_SPRITE,
        SOUR_GUMMY_SPRITE,
        CARAMEL_SLIME_SPRITE,
        SANDWICH_COOKIE_SPRITE,
        BOSS_MIXER_SPRITE,
        PICKUP_CRYSTAL_SPRITE,
        PROJECTILE_SPRITE,
        MAP_TILE_SPRITE,
    ]
}

#[derive(Debug, Clone)]
struct RuntimeCli {
    content_dir: PathBuf,
    seed: u64,
    seconds: f32,
    tick_rate: u32,
    demo_input: bool,
    simulation_speed: f32,
    playtest_report: Option<PathBuf>,
    auto_exit_after_report: bool,
    player_skill: String,
    capture_interval_seconds: f32,
}

impl Default for RuntimeCli {
    fn default() -> Self {
        Self {
            content_dir: PathBuf::from(DEFAULT_CONTENT_DIR),
            seed: 12_345,
            seconds: 600.0,
            tick_rate: 30,
            demo_input: false,
            simulation_speed: 1.0,
            playtest_report: None,
            auto_exit_after_report: false,
            player_skill: "unrated".to_string(),
            capture_interval_seconds: 5.0,
        }
    }
}

#[derive(Resource)]
struct RuntimeState {
    content: ContentPack,
    content_dir: PathBuf,
    config: RunConfig,
    core: GameCore,
    dt: FixedDt,
    dt_seconds: f32,
    accumulator: f32,
    latest_snapshot: RunSnapshot,
    last_event: String,
    last_event_kind: RuntimeEventKind,
    pending_sounds: Vec<RuntimeSound>,
    effects: Vec<RuntimeEffect>,
    capture: RuntimeCaptureState,
    demo_input: bool,
    simulation_speed: f32,
    auto_exit_after_report: bool,
    paused: bool,
    run_number: u32,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum RuntimeEventKind {
    Neutral,
    Combat,
    Pickup,
    Upgrade,
    Damage,
    Terminal,
    System,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum RuntimeSound {
    Fire,
    Pickup,
    Upgrade,
    Damage,
    Terminal,
    System,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum RuntimeEffectKind {
    ProjectileHit,
    XpDrop,
    XpCollect,
    PlayerDamage,
    BossSpawn,
}

#[derive(Debug, Clone)]
struct RuntimeEffect {
    kind: RuntimeEffectKind,
    position: CoreVec2,
    ttl_seconds: f32,
    total_seconds: f32,
    intensity: f32,
}

#[derive(Debug, Clone)]
struct RuntimeCaptureState {
    report_path: Option<PathBuf>,
    player_skill: String,
    capture_interval_seconds: f32,
    next_sample_seconds: f32,
    event_counts: RuntimeEventCounts,
    samples: Vec<RuntimeTelemetrySample>,
    finished: bool,
}

#[derive(Debug, Clone, Default, Serialize)]
struct RuntimeEventCounts {
    enemy_spawned: u32,
    boss_spawned: u32,
    weapon_fired: u32,
    enemy_hit: u32,
    enemy_killed: u32,
    xp_dropped: u32,
    xp_collected: u32,
    level_up: u32,
    upgrade_offered: u32,
    upgrade_chosen: u32,
    player_damaged: u32,
    run_ended: u32,
}

#[derive(Debug, Clone, Serialize)]
struct RuntimeTelemetrySample {
    time_seconds: f32,
    health: f32,
    max_health: f32,
    level: u32,
    xp: f32,
    xp_to_next_level: f32,
    kills: u32,
    visible_enemies: usize,
    visible_pickups: usize,
    visible_projectiles: usize,
    active_effects: usize,
    upgrade_options: usize,
    last_event_kind: &'static str,
}

#[derive(Debug, Clone, Serialize)]
struct RuntimePlaytestReport {
    kind: &'static str,
    report_version: u32,
    player_skill: String,
    input_mode: &'static str,
    simulation_speed: f32,
    auto_exit_after_report: bool,
    run_number: u32,
    content_dir: String,
    run_config: RuntimeRunConfigReport,
    event_counts: RuntimeEventCounts,
    samples: Vec<RuntimeTelemetrySample>,
    final_metrics: RuntimeMetricsReport,
    manual_review: RuntimeManualReviewTemplate,
}

#[derive(Debug, Clone, Serialize)]
struct RuntimeRunConfigReport {
    seed: u64,
    map_id: String,
    character_id: String,
    difficulty: &'static str,
    duration_seconds: f32,
    tick_rate: u32,
    ruleset_version: String,
    content_pack_ids: Vec<String>,
    starting_weapons: Vec<String>,
    starting_passives: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
struct RuntimeMetricsReport {
    seed: u64,
    tick_rate: u32,
    duration_seconds: f32,
    terminal: Option<RuntimeTerminalReport>,
    kills: u32,
    level: u32,
    xp_collected: f32,
    xp_dropped: f32,
    damage_dealt_by_weapon: f32,
    damage_taken: f32,
    max_enemy_count: usize,
    max_projectile_count: usize,
    upgrade_choices: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
struct RuntimeTerminalReport {
    kind: &'static str,
    time_seconds: f32,
    reason: String,
    final_level: u32,
    kills: u32,
}

#[derive(Debug, Clone, Serialize)]
struct RuntimeManualReviewTemplate {
    fun_rating: Option<u8>,
    clarity_rating: Option<u8>,
    difficulty_rating: Option<u8>,
    projectile_readability: Option<String>,
    hit_feedback: Option<String>,
    xp_pickup_rhythm: Option<String>,
    boss_spawn_clarity: Option<String>,
    death_reason_clarity: Option<String>,
    notes: String,
    tags: Vec<String>,
    next_actions: Vec<String>,
}

#[derive(Resource)]
struct RuntimeSounds {
    fire: Handle<AudioSource>,
    pickup: Handle<AudioSource>,
    upgrade: Handle<AudioSource>,
    damage: Handle<AudioSource>,
    terminal: Handle<AudioSource>,
    system: Handle<AudioSource>,
}

#[derive(Resource)]
struct RuntimeSprites {
    player: Handle<Image>,
    bouncy_gummy: Handle<Image>,
    sour_gummy: Handle<Image>,
    caramel_slime: Handle<Image>,
    sandwich_cookie: Handle<Image>,
    boss_mixer: Handle<Image>,
    pickup_crystal: Handle<Image>,
    projectile: Handle<Image>,
    map_tile: Handle<Image>,
}

#[derive(Component)]
struct RuntimeVisual;

#[derive(Component)]
struct RuntimeCamera;

#[derive(Component)]
struct HudText;

#[derive(Component)]
struct UpgradeText;

#[derive(Component)]
struct TerminalText;

type TerminalTextFilter = (With<TerminalText>, Without<HudText>, Without<UpgradeText>);

fn setup_runtime(
    mut commands: Commands,
    mut audio_sources: ResMut<Assets<AudioSource>>,
    asset_server: Res<AssetServer>,
) {
    let cli = parse_runtime_cli(std::env::args().skip(1));
    let content = ContentPack::load_from_dir(&cli.content_dir).unwrap_or_else(|error| {
        panic!(
            "failed to load runtime content from `{}`: {error}",
            cli.content_dir.display()
        )
    });
    let config = run_config_from_cli(&cli);
    let core = GameCore::reset_with_content(config.clone(), content.clone())
        .expect("runtime content must pass the same GameCore validation as headless runs");
    let latest_snapshot = core.snapshot();
    let dt = FixedDt::from_tick_rate(cli.tick_rate);

    commands.spawn((Camera2dBundle::default(), RuntimeCamera));
    commands.spawn((
        TextBundle::from_section(
            "",
            TextStyle {
                font_size: 18.0,
                color: Color::srgb(0.20, 0.14, 0.10),
                ..default()
            },
        )
        .with_style(Style {
            position_type: PositionType::Absolute,
            left: Val::Px(14.0),
            top: Val::Px(12.0),
            ..default()
        }),
        HudText,
    ));
    commands.spawn((
        TextBundle::from_section(
            "",
            TextStyle {
                font_size: 18.0,
                color: Color::srgb(0.18, 0.08, 0.16),
                ..default()
            },
        )
        .with_style(Style {
            position_type: PositionType::Absolute,
            left: Val::Px(14.0),
            bottom: Val::Px(16.0),
            ..default()
        }),
        UpgradeText,
    ));
    commands.spawn((
        TextBundle::from_section(
            "",
            TextStyle {
                font_size: 28.0,
                color: Color::srgb(0.52, 0.09, 0.17),
                ..default()
            },
        )
        .with_style(Style {
            position_type: PositionType::Absolute,
            left: Val::Px(14.0),
            top: Val::Px(82.0),
            ..default()
        }),
        TerminalText,
    ));

    commands.insert_resource(RuntimeState {
        content,
        content_dir: cli.content_dir.clone(),
        config,
        core,
        dt,
        dt_seconds: dt.seconds(),
        accumulator: 0.0,
        latest_snapshot,
        last_event: "run started".to_string(),
        last_event_kind: RuntimeEventKind::System,
        pending_sounds: vec![RuntimeSound::System],
        effects: Vec::new(),
        capture: RuntimeCaptureState::from_cli(&cli),
        demo_input: cli.demo_input,
        simulation_speed: cli.simulation_speed,
        auto_exit_after_report: cli.auto_exit_after_report,
        paused: false,
        run_number: 1,
    });
    commands.insert_resource(create_runtime_sounds(&mut audio_sources));
    commands.insert_resource(load_runtime_sprites(&asset_server));
}

fn step_game_core(
    time: Res<Time>,
    keyboard: Res<ButtonInput<KeyCode>>,
    mut state: ResMut<RuntimeState>,
) {
    let dt = state.dt;
    if keyboard.just_pressed(KeyCode::KeyP) {
        state.paused = !state.paused;
        state.last_event = if state.paused {
            "paused".to_string()
        } else {
            "resumed".to_string()
        };
        state.last_event_kind = RuntimeEventKind::System;
        state.pending_sounds.push(RuntimeSound::System);
    }
    if keyboard.just_pressed(KeyCode::KeyR) {
        reset_runtime_run(&mut state);
        return;
    }

    if state.core.is_terminal() {
        state.latest_snapshot = state.core.snapshot();
        return;
    }
    if state.paused {
        state.latest_snapshot = state.core.snapshot();
        return;
    }

    let snapshot = state.core.snapshot();
    let upgrade_choice = if state.demo_input {
        demo_upgrade_choice(&snapshot)
    } else {
        upgrade_choice_from_keyboard(&keyboard, &snapshot)
    };

    if !snapshot.upgrade_options.is_empty() {
        state.accumulator = 0.0;
        if let Some(choice) = upgrade_choice {
            let result = state.core.step(
                PlayerAction {
                    movement: CoreVec2::ZERO,
                    upgrade_choice: Some(choice),
                },
                dt,
            );
            apply_runtime_feedback(&mut state, &result.events, &result.snapshot);
            state.latest_snapshot = result.snapshot;
        } else {
            state.latest_snapshot = snapshot;
        }
        return;
    }

    let frame_seconds = (time.delta_seconds() * state.simulation_speed).min(0.25);
    state.accumulator = (state.accumulator + frame_seconds).min(0.25);
    let movement = if state.demo_input {
        demo_movement(&snapshot)
    } else {
        movement_from_keyboard(&keyboard)
    };
    while state.accumulator >= state.dt_seconds && !state.core.is_terminal() {
        let result = state.core.step(
            PlayerAction {
                movement,
                upgrade_choice: None,
            },
            dt,
        );
        state.accumulator -= state.dt_seconds;
        apply_runtime_feedback(&mut state, &result.events, &result.snapshot);
        state.latest_snapshot = result.snapshot;

        if !state.latest_snapshot.upgrade_options.is_empty() {
            state.accumulator = 0.0;
            break;
        }
    }
}

fn update_runtime_effects(time: Res<Time>, mut state: ResMut<RuntimeState>) {
    let dt = time.delta_seconds();
    for effect in &mut state.effects {
        effect.ttl_seconds -= dt;
    }
    state.effects.retain(|effect| effect.ttl_seconds > 0.0);
}

fn capture_playtest_report(mut state: ResMut<RuntimeState>) {
    if !state.capture.enabled() {
        return;
    }

    let snapshot = state.latest_snapshot.clone();
    let metrics = state.core.metrics();
    let should_finish = metrics.terminal.is_some() && !state.capture.finished;
    let should_sample = state
        .capture
        .should_sample(snapshot.time_seconds, should_finish);

    if !should_sample {
        return;
    }

    let sample = RuntimeTelemetrySample::from_snapshot(
        &snapshot,
        state.effects.len(),
        state.last_event_kind,
    );
    state.capture.record_sample(sample, snapshot.time_seconds);

    let report = RuntimePlaytestReport::from_state(&state, metrics);
    let report_written = match write_runtime_playtest_report(&state.capture, &report) {
        Ok(()) => true,
        Err(error) => {
            eprintln!("failed to write runtime playtest report: {error}");
            false
        }
    };

    if should_finish && report_written {
        state.capture.finished = true;
        if state.auto_exit_after_report {
            std::process::exit(0);
        }
    }
}

fn play_runtime_audio(
    mut commands: Commands,
    mut state: ResMut<RuntimeState>,
    sounds: Res<RuntimeSounds>,
) {
    let pending = std::mem::take(&mut state.pending_sounds);
    for sound in pending {
        commands.spawn(AudioBundle {
            source: sounds.handle(sound).clone(),
            settings: PlaybackSettings::DESPAWN.with_volume(sound.volume()),
        });
    }
}

fn movement_from_keyboard(keyboard: &ButtonInput<KeyCode>) -> CoreVec2 {
    let mut x = 0.0;
    let mut y = 0.0;

    if keyboard.pressed(KeyCode::KeyA) || keyboard.pressed(KeyCode::ArrowLeft) {
        x -= 1.0;
    }
    if keyboard.pressed(KeyCode::KeyD) || keyboard.pressed(KeyCode::ArrowRight) {
        x += 1.0;
    }
    if keyboard.pressed(KeyCode::KeyW) || keyboard.pressed(KeyCode::ArrowUp) {
        y += 1.0;
    }
    if keyboard.pressed(KeyCode::KeyS) || keyboard.pressed(KeyCode::ArrowDown) {
        y -= 1.0;
    }

    CoreVec2::new(x, y).normalized_or_zero()
}

fn upgrade_choice_from_keyboard(
    keyboard: &ButtonInput<KeyCode>,
    snapshot: &RunSnapshot,
) -> Option<usize> {
    if snapshot.upgrade_options.is_empty() {
        return None;
    }

    for (key, index) in [
        (KeyCode::Digit1, 0usize),
        (KeyCode::Digit2, 1usize),
        (KeyCode::Digit3, 2usize),
    ] {
        if keyboard.just_pressed(key) && index < snapshot.upgrade_options.len() {
            return Some(index);
        }
    }
    None
}

fn demo_upgrade_choice(snapshot: &RunSnapshot) -> Option<usize> {
    if snapshot.upgrade_options.is_empty() {
        None
    } else {
        Some(0)
    }
}

fn demo_movement(snapshot: &RunSnapshot) -> CoreVec2 {
    let player_position = snapshot.player.position;
    if let Some(enemy) = snapshot.visible_enemies.iter().min_by(|left, right| {
        player_position
            .distance(left.position)
            .partial_cmp(&player_position.distance(right.position))
            .unwrap_or(std::cmp::Ordering::Equal)
    }) {
        let away = player_position - enemy.position;
        if away.length_squared() < 110.0 * 110.0 {
            return away.normalized_or_zero();
        }
    }

    if let Some(pickup) = snapshot.visible_pickups.iter().min_by(|left, right| {
        player_position
            .distance(left.position)
            .partial_cmp(&player_position.distance(right.position))
            .unwrap_or(std::cmp::Ordering::Equal)
    }) {
        let toward_pickup = pickup.position - player_position;
        if toward_pickup.length_squared() > 12.0 * 12.0 {
            return toward_pickup.normalized_or_zero();
        }
    }

    let angle = snapshot.time_seconds * 0.75;
    CoreVec2::new(angle.cos(), angle.sin()).normalized_or_zero()
}

fn sync_camera(state: Res<RuntimeState>, mut query: Query<&mut Transform, With<RuntimeCamera>>) {
    let Ok(mut transform) = query.get_single_mut() else {
        return;
    };

    transform.translation.x = state.latest_snapshot.player.position.x;
    transform.translation.y = state.latest_snapshot.player.position.y;
    transform.translation.z = CAMERA_Z;
}

fn sync_world_visuals(
    mut commands: Commands,
    state: Res<RuntimeState>,
    sprites: Res<RuntimeSprites>,
    visuals: Query<Entity, With<RuntimeVisual>>,
) {
    for entity in &visuals {
        commands.entity(entity).despawn_recursive();
    }

    let snapshot = &state.latest_snapshot;
    commands.spawn((
        SpriteBundle {
            texture: sprites.map_tile.clone(),
            sprite: Sprite {
                color: Color::WHITE,
                custom_size: Some(Vec2::new(snapshot.map.width, snapshot.map.height)),
                ..default()
            },
            transform: Transform::from_xyz(0.0, 0.0, MAP_Z),
            ..default()
        },
        RuntimeVisual,
    ));
    spawn_map_borders(&mut commands, snapshot);

    for pickup in &snapshot.visible_pickups {
        let size = (pickup.radius * 2.0).max(24.0);
        commands.spawn((
            SpriteBundle {
                texture: sprites.pickup_crystal.clone(),
                sprite: Sprite {
                    color: Color::WHITE,
                    custom_size: Some(Vec2::splat(size)),
                    ..default()
                },
                transform: Transform::from_xyz(pickup.position.x, pickup.position.y, PICKUP_Z),
                ..default()
            },
            RuntimeVisual,
        ));
    }

    for projectile in &snapshot.visible_projectiles {
        commands.spawn((
            SpriteBundle {
                texture: sprites.projectile.clone(),
                sprite: Sprite {
                    color: Color::WHITE,
                    custom_size: Some(Vec2::splat((projectile.radius * 2.0).max(18.0))),
                    ..default()
                },
                transform: Transform::from_xyz(
                    projectile.position.x,
                    projectile.position.y,
                    PROJECTILE_Z,
                ),
                ..default()
            },
            RuntimeVisual,
        ));
    }

    for enemy in &snapshot.visible_enemies {
        let texture = sprites
            .enemy(enemy.enemy_id.as_str(), enemy.is_boss)
            .clone();
        commands.spawn((
            SpriteBundle {
                texture,
                sprite: Sprite {
                    color: enemy_tint(enemy.is_boss, enemy.is_elite),
                    custom_size: Some(Vec2::splat(enemy.radius * 2.0)),
                    ..default()
                },
                transform: Transform::from_xyz(enemy.position.x, enemy.position.y, ENEMY_Z),
                ..default()
            },
            RuntimeVisual,
        ));
    }

    for effect in &state.effects {
        let (color, size) = effect_visual_style(effect);
        commands.spawn((
            SpriteBundle {
                sprite: Sprite {
                    color,
                    custom_size: Some(Vec2::splat(size)),
                    ..default()
                },
                transform: Transform::from_xyz(effect.position.x, effect.position.y, EFFECT_Z),
                ..default()
            },
            RuntimeVisual,
        ));
    }

    commands.spawn((
        SpriteBundle {
            texture: sprites.player.clone(),
            sprite: Sprite {
                color: player_tint(snapshot.player.health, snapshot.player.max_health),
                custom_size: Some(Vec2::splat(42.0)),
                ..default()
            },
            transform: Transform::from_xyz(
                snapshot.player.position.x,
                snapshot.player.position.y,
                PLAYER_Z,
            ),
            ..default()
        },
        RuntimeVisual,
    ));
}

fn spawn_map_borders(commands: &mut Commands, snapshot: &RunSnapshot) {
    let thickness = 10.0;
    let color = Color::srgb(0.49, 0.36, 0.20);
    for (x, y, width, height) in [
        (
            0.0,
            snapshot.map.height * 0.5,
            snapshot.map.width,
            thickness,
        ),
        (
            0.0,
            -snapshot.map.height * 0.5,
            snapshot.map.width,
            thickness,
        ),
        (
            -snapshot.map.width * 0.5,
            0.0,
            thickness,
            snapshot.map.height,
        ),
        (
            snapshot.map.width * 0.5,
            0.0,
            thickness,
            snapshot.map.height,
        ),
    ] {
        commands.spawn((
            SpriteBundle {
                sprite: Sprite {
                    color,
                    custom_size: Some(Vec2::new(width, height)),
                    ..default()
                },
                transform: Transform::from_xyz(x, y, MAP_BORDER_Z),
                ..default()
            },
            RuntimeVisual,
        ));
    }
}

fn load_runtime_sprites(asset_server: &AssetServer) -> RuntimeSprites {
    RuntimeSprites {
        player: asset_server.load(PLAYER_SPRITE),
        bouncy_gummy: asset_server.load(BOUNCY_GUMMY_SPRITE),
        sour_gummy: asset_server.load(SOUR_GUMMY_SPRITE),
        caramel_slime: asset_server.load(CARAMEL_SLIME_SPRITE),
        sandwich_cookie: asset_server.load(SANDWICH_COOKIE_SPRITE),
        boss_mixer: asset_server.load(BOSS_MIXER_SPRITE),
        pickup_crystal: asset_server.load(PICKUP_CRYSTAL_SPRITE),
        projectile: asset_server.load(PROJECTILE_SPRITE),
        map_tile: asset_server.load(MAP_TILE_SPRITE),
    }
}

impl RuntimeSprites {
    fn enemy(&self, enemy_id: &str, is_boss: bool) -> &Handle<Image> {
        if is_boss {
            return &self.boss_mixer;
        }
        match enemy_id {
            "sour-gummy" => &self.sour_gummy,
            "caramel-slime" => &self.caramel_slime,
            "sandwich-cookie-creep" => &self.sandwich_cookie,
            _ => &self.bouncy_gummy,
        }
    }
}

fn enemy_tint(_is_boss: bool, is_elite: bool) -> Color {
    if is_elite {
        Color::srgb(1.0, 0.82, 1.0)
    } else {
        Color::WHITE
    }
}

fn player_tint(health: f32, max_health: f32) -> Color {
    let ratio = if max_health > 0.0 {
        (health / max_health).clamp(0.0, 1.0)
    } else {
        0.0
    };
    if ratio < 0.30 {
        Color::srgb(1.0, 0.55, 0.48)
    } else {
        Color::WHITE
    }
}

fn update_hud(
    state: Res<RuntimeState>,
    mut hud_query: Query<&mut Text, With<HudText>>,
    mut upgrade_query: Query<&mut Text, (With<UpgradeText>, Without<HudText>)>,
    mut terminal_query: Query<&mut Text, TerminalTextFilter>,
) {
    let snapshot = &state.latest_snapshot;
    if let Ok(mut text) = hud_query.get_single_mut() {
        let mode = if state.paused { "Paused" } else { "Playing" };
        text.sections[0].value = format!(
            "Run {}  {}  Time {:05.1}s  HP {:03.0}/{:03.0}  Lv {}  XP {:.0}/{:.0}  Kills {}  Enemies {}  {}\n{}  [{}]\nControls: WASD/Arrows move | 1/2/3 upgrade | P pause | R restart",
            state.run_number,
            mode,
            snapshot.time_seconds,
            snapshot.player.health.max(0.0),
            snapshot.player.max_health,
            snapshot.player.level,
            snapshot.player.xp,
            snapshot.player.xp_to_next_level,
            snapshot.metrics_partial.kills,
            snapshot.visible_enemies.len(),
            snapshot.map.map_id,
            state.last_event,
            state.last_event_kind.label(),
        );
    }

    if let Ok(mut text) = upgrade_query.get_single_mut() {
        text.sections[0].value = if snapshot.upgrade_options.is_empty() {
            String::new()
        } else {
            let options = snapshot
                .upgrade_options
                .iter()
                .enumerate()
                .map(|(index, option)| {
                    format!("{}. {} [{}]", index + 1, option.id, option.tags.join(","))
                })
                .collect::<Vec<_>>()
                .join("\n");
            format!("Upgrade paused - press 1/2/3\n{options}")
        };
    }

    if let Ok(mut text) = terminal_query.get_single_mut() {
        text.sections[0].value = if state.paused {
            "Paused".to_string()
        } else {
            state
                .core
                .metrics()
                .terminal
                .as_ref()
                .map(|terminal| {
                    let title = match terminal.kind {
                        TerminalKind::Victory => "Victory",
                        TerminalKind::Defeat => "Defeat",
                        TerminalKind::Timeout => "Timeout",
                        TerminalKind::Aborted => "Aborted",
                        TerminalKind::InvalidState => "Invalid",
                    };
                    format!(
                        "{title}  {:.1}s  Lv {}  Kills {}\nPress R to restart",
                        terminal.time_seconds, terminal.final_level, terminal.kills
                    )
                })
                .unwrap_or_default()
        };
    }
}

fn apply_runtime_feedback(state: &mut RuntimeState, events: &[GameEvent], snapshot: &RunSnapshot) {
    state.capture.event_counts.observe(events);
    let feedback = feedback_for_events(events);
    state.last_event = feedback.message;
    state.last_event_kind = feedback.kind;
    for sound in feedback.sounds {
        push_unique_sound(&mut state.pending_sounds, sound);
    }
    for effect in effects_for_events(events, snapshot) {
        push_runtime_effect(state, effect);
    }
}

struct RuntimeFeedback {
    message: String,
    kind: RuntimeEventKind,
    sounds: Vec<RuntimeSound>,
}

fn feedback_for_events(events: &[GameEvent]) -> RuntimeFeedback {
    RuntimeFeedback {
        message: describe_events(events),
        kind: event_kind_for_events(events),
        sounds: sounds_for_events(events),
    }
}

fn describe_events(events: &[GameEvent]) -> String {
    events
        .iter()
        .rev()
        .find_map(describe_event)
        .unwrap_or_else(|| "storm active".to_string())
}

fn event_kind_for_events(events: &[GameEvent]) -> RuntimeEventKind {
    events
        .iter()
        .rev()
        .find_map(|event| match event {
            GameEvent::RunEnded { .. } => Some(RuntimeEventKind::Terminal),
            GameEvent::PlayerDamaged { .. } => Some(RuntimeEventKind::Damage),
            GameEvent::UpgradeOffered { .. }
            | GameEvent::UpgradeChosen { .. }
            | GameEvent::LevelUp { .. } => Some(RuntimeEventKind::Upgrade),
            GameEvent::XpCollected { .. } => Some(RuntimeEventKind::Pickup),
            GameEvent::WeaponFired { .. }
            | GameEvent::EnemyKilled { .. }
            | GameEvent::BossSpawned { .. } => Some(RuntimeEventKind::Combat),
            GameEvent::EnemySpawned { .. }
            | GameEvent::EnemyHit { .. }
            | GameEvent::XpDropped { .. } => None,
        })
        .unwrap_or(RuntimeEventKind::Neutral)
}

fn sounds_for_events(events: &[GameEvent]) -> Vec<RuntimeSound> {
    let mut sounds = Vec::new();
    for event in events {
        let sound = match event {
            GameEvent::RunEnded { .. } => Some(RuntimeSound::Terminal),
            GameEvent::PlayerDamaged { .. } => Some(RuntimeSound::Damage),
            GameEvent::UpgradeOffered { .. }
            | GameEvent::UpgradeChosen { .. }
            | GameEvent::LevelUp { .. } => Some(RuntimeSound::Upgrade),
            GameEvent::XpCollected { .. } => Some(RuntimeSound::Pickup),
            GameEvent::WeaponFired { .. } => Some(RuntimeSound::Fire),
            GameEvent::BossSpawned { .. } => Some(RuntimeSound::Terminal),
            GameEvent::EnemySpawned { .. }
            | GameEvent::EnemyHit { .. }
            | GameEvent::EnemyKilled { .. }
            | GameEvent::XpDropped { .. } => None,
        };
        if let Some(sound) = sound {
            push_unique_sound(&mut sounds, sound);
        }
    }
    sounds.truncate(3);
    sounds
}

fn push_unique_sound(sounds: &mut Vec<RuntimeSound>, sound: RuntimeSound) {
    if !sounds.contains(&sound) {
        sounds.push(sound);
    }
}

fn describe_event(event: &GameEvent) -> Option<String> {
    match event {
        GameEvent::EnemySpawned { enemy_id, .. } => Some(format!("spawned {enemy_id}")),
        GameEvent::BossSpawned { boss_id, .. } => Some(format!("boss {boss_id}")),
        GameEvent::WeaponFired {
            weapon_id,
            projectile_count,
        } => Some(format!("fired {weapon_id} x{projectile_count}")),
        GameEvent::EnemyKilled { enemy_id, .. } => Some(format!("defeated {enemy_id}")),
        GameEvent::XpCollected { value, .. } => Some(format!("xp +{value:.0}")),
        GameEvent::LevelUp { level } => Some(format!("level {level}")),
        GameEvent::UpgradeOffered { .. } => Some("upgrade offered".to_string()),
        GameEvent::UpgradeChosen { option_id } => Some(format!("upgrade {option_id}")),
        GameEvent::PlayerDamaged { amount } => Some(format!("damage {amount:.1}")),
        GameEvent::RunEnded { terminal } => Some(format!("ended {}", terminal.kind.as_str())),
        GameEvent::EnemyHit { .. } | GameEvent::XpDropped { .. } => None,
    }
}

fn effects_for_events(events: &[GameEvent], snapshot: &RunSnapshot) -> Vec<RuntimeEffect> {
    let mut effects = Vec::new();
    for event in events {
        let effect =
            match event {
                GameEvent::EnemyHit {
                    entity_id, damage, ..
                } => enemy_position(snapshot, *entity_id).map(|position| {
                    RuntimeEffect::new(RuntimeEffectKind::ProjectileHit, position, *damage, 0.16)
                }),
                GameEvent::XpDropped { entity_id, value } => pickup_position(snapshot, *entity_id)
                    .map(|position| {
                        RuntimeEffect::new(RuntimeEffectKind::XpDrop, position, *value, 0.42)
                    }),
                GameEvent::XpCollected { value, .. } => Some(RuntimeEffect::new(
                    RuntimeEffectKind::XpCollect,
                    snapshot.player.position,
                    *value,
                    0.26,
                )),
                GameEvent::PlayerDamaged { amount } => Some(RuntimeEffect::new(
                    RuntimeEffectKind::PlayerDamage,
                    snapshot.player.position,
                    *amount,
                    0.22,
                )),
                GameEvent::BossSpawned { entity_id, .. } => boss_position(snapshot, *entity_id)
                    .map(|position| {
                        RuntimeEffect::new(RuntimeEffectKind::BossSpawn, position, 1.0, 0.72)
                    }),
                GameEvent::EnemySpawned { .. }
                | GameEvent::WeaponFired { .. }
                | GameEvent::EnemyKilled { .. }
                | GameEvent::LevelUp { .. }
                | GameEvent::UpgradeOffered { .. }
                | GameEvent::UpgradeChosen { .. }
                | GameEvent::RunEnded { .. } => None,
            };
        if let Some(effect) = effect {
            effects.push(effect);
        }
    }
    effects
}

fn enemy_position(snapshot: &RunSnapshot, entity_id: u64) -> Option<CoreVec2> {
    snapshot
        .visible_enemies
        .iter()
        .find(|enemy| enemy.entity_id == entity_id)
        .map(|enemy| enemy.position)
}

fn pickup_position(snapshot: &RunSnapshot, entity_id: u64) -> Option<CoreVec2> {
    snapshot
        .visible_pickups
        .iter()
        .find(|pickup| pickup.entity_id == entity_id)
        .map(|pickup| pickup.position)
}

fn boss_position(snapshot: &RunSnapshot, entity_id: u64) -> Option<CoreVec2> {
    snapshot
        .boss
        .as_ref()
        .filter(|boss| boss.entity_id == entity_id)
        .map(|boss| boss.position)
        .or_else(|| enemy_position(snapshot, entity_id))
}

fn push_runtime_effect(state: &mut RuntimeState, effect: RuntimeEffect) {
    state.effects.push(effect);
    if state.effects.len() > MAX_RUNTIME_EFFECTS {
        let overflow = state.effects.len() - MAX_RUNTIME_EFFECTS;
        state.effects.drain(0..overflow);
    }
}

fn effect_visual_style(effect: &RuntimeEffect) -> (Color, f32) {
    let fade = effect.fade();
    let growth = 1.0 - fade;
    match effect.kind {
        RuntimeEffectKind::ProjectileHit => (
            Color::srgba(1.0, 0.88, 0.20, 0.72 * fade),
            20.0 + growth * 28.0 + effect.intensity.min(10.0),
        ),
        RuntimeEffectKind::XpDrop => (
            Color::srgba(0.18, 0.86, 1.0, 0.62 * fade),
            18.0 + growth * 18.0 + effect.intensity.min(12.0) * 0.35,
        ),
        RuntimeEffectKind::XpCollect => (
            Color::srgba(0.35, 1.0, 0.48, 0.72 * fade),
            28.0 + growth * 32.0 + effect.intensity.min(16.0) * 0.25,
        ),
        RuntimeEffectKind::PlayerDamage => (
            Color::srgba(1.0, 0.20, 0.18, 0.78 * fade),
            50.0 + growth * 24.0 + effect.intensity.min(12.0) * 1.5,
        ),
        RuntimeEffectKind::BossSpawn => (
            Color::srgba(1.0, 0.32, 0.72, 0.45 * fade),
            150.0 + growth * 80.0,
        ),
    }
}

impl RuntimeEffect {
    fn new(
        kind: RuntimeEffectKind,
        position: CoreVec2,
        intensity: f32,
        total_seconds: f32,
    ) -> Self {
        Self {
            kind,
            position,
            ttl_seconds: total_seconds,
            total_seconds,
            intensity,
        }
    }

    fn fade(&self) -> f32 {
        if self.total_seconds > 0.0 {
            (self.ttl_seconds / self.total_seconds).clamp(0.0, 1.0)
        } else {
            0.0
        }
    }
}

fn reset_runtime_run(state: &mut RuntimeState) {
    let core = GameCore::reset_with_content(state.config.clone(), state.content.clone())
        .expect("runtime reset must use already validated content");
    state.core = core;
    state.latest_snapshot = state.core.snapshot();
    state.accumulator = 0.0;
    state.last_event = "run restarted".to_string();
    state.last_event_kind = RuntimeEventKind::System;
    state.pending_sounds.clear();
    state.pending_sounds.push(RuntimeSound::System);
    state.effects.clear();
    state.capture.reset_for_next_run();
    state.paused = false;
    state.run_number += 1;
}

impl RuntimeEventKind {
    fn label(self) -> &'static str {
        match self {
            Self::Neutral => "status",
            Self::Combat => "combat",
            Self::Pickup => "pickup",
            Self::Upgrade => "upgrade",
            Self::Damage => "damage",
            Self::Terminal => "terminal",
            Self::System => "system",
        }
    }
}

impl RuntimeSounds {
    fn handle(&self, sound: RuntimeSound) -> &Handle<AudioSource> {
        match sound {
            RuntimeSound::Fire => &self.fire,
            RuntimeSound::Pickup => &self.pickup,
            RuntimeSound::Upgrade => &self.upgrade,
            RuntimeSound::Damage => &self.damage,
            RuntimeSound::Terminal => &self.terminal,
            RuntimeSound::System => &self.system,
        }
    }
}

impl RuntimeSound {
    fn volume(self) -> Volume {
        match self {
            Self::Fire => Volume::new(0.18),
            Self::Pickup => Volume::new(0.22),
            Self::Upgrade => Volume::new(0.34),
            Self::Damage => Volume::new(0.30),
            Self::Terminal => Volume::new(0.36),
            Self::System => Volume::new(0.20),
        }
    }
}

fn create_runtime_sounds(audio_sources: &mut Assets<AudioSource>) -> RuntimeSounds {
    RuntimeSounds {
        fire: add_tone(audio_sources, 880.0, 0.055, 0.45),
        pickup: add_tone(audio_sources, 1320.0, 0.070, 0.35),
        upgrade: add_tone(audio_sources, 660.0, 0.140, 0.45),
        damage: add_tone(audio_sources, 180.0, 0.090, 0.55),
        terminal: add_tone(audio_sources, 440.0, 0.240, 0.50),
        system: add_tone(audio_sources, 520.0, 0.060, 0.30),
    }
}

fn add_tone(
    audio_sources: &mut Assets<AudioSource>,
    frequency_hz: f32,
    seconds: f32,
    amplitude: f32,
) -> Handle<AudioSource> {
    audio_sources.add(AudioSource {
        bytes: Arc::from(make_tone_wav(frequency_hz, seconds, amplitude).into_boxed_slice()),
    })
}

fn make_tone_wav(frequency_hz: f32, seconds: f32, amplitude: f32) -> Vec<u8> {
    let sample_count = (PLACEHOLDER_SAMPLE_RATE as f32 * seconds).max(1.0) as u32;
    let data_bytes = sample_count * 2;
    let mut bytes = Vec::with_capacity(44 + data_bytes as usize);
    bytes.extend_from_slice(b"RIFF");
    bytes.extend_from_slice(&(36 + data_bytes).to_le_bytes());
    bytes.extend_from_slice(b"WAVEfmt ");
    bytes.extend_from_slice(&16u32.to_le_bytes());
    bytes.extend_from_slice(&1u16.to_le_bytes());
    bytes.extend_from_slice(&1u16.to_le_bytes());
    bytes.extend_from_slice(&PLACEHOLDER_SAMPLE_RATE.to_le_bytes());
    bytes.extend_from_slice(&(PLACEHOLDER_SAMPLE_RATE * 2).to_le_bytes());
    bytes.extend_from_slice(&2u16.to_le_bytes());
    bytes.extend_from_slice(&16u16.to_le_bytes());
    bytes.extend_from_slice(b"data");
    bytes.extend_from_slice(&data_bytes.to_le_bytes());

    for index in 0..sample_count {
        let t = index as f32 / PLACEHOLDER_SAMPLE_RATE as f32;
        let fade = 1.0 - (index as f32 / sample_count as f32);
        let sample = (t * frequency_hz * std::f32::consts::TAU).sin() * amplitude * fade;
        let pcm = (sample * i16::MAX as f32) as i16;
        bytes.extend_from_slice(&pcm.to_le_bytes());
    }

    bytes
}

fn run_config_from_cli(cli: &RuntimeCli) -> RunConfig {
    RunConfig {
        seed: cli.seed,
        map_id: "frosting-grassland".to_string(),
        character_id: "jar-keeper".to_string(),
        starting_loadout: StartingLoadout {
            weapons: vec!["rainbow-candy-shot".to_string()],
            passives: Vec::new(),
        },
        difficulty: Difficulty::Normal,
        duration_seconds: cli.seconds,
        ruleset_version: "prototype-v0".to_string(),
        content_pack_ids: vec!["base-demo".to_string()],
        tick_rate: cli.tick_rate,
    }
}

fn difficulty_label(difficulty: Difficulty) -> &'static str {
    match difficulty {
        Difficulty::Normal => "normal",
    }
}

fn parse_runtime_cli(args: impl IntoIterator<Item = String>) -> RuntimeCli {
    let mut cli = RuntimeCli::default();
    let mut args = args.into_iter();

    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--content-dir" => {
                if let Some(value) = args.next() {
                    cli.content_dir = PathBuf::from(value);
                }
            }
            "--seed" => {
                if let Some(value) = args.next() {
                    cli.seed = value.parse().unwrap_or(cli.seed);
                }
            }
            "--seconds" => {
                if let Some(value) = args.next() {
                    cli.seconds = value.parse().unwrap_or(cli.seconds);
                }
            }
            "--tick-rate" => {
                if let Some(value) = args.next() {
                    cli.tick_rate = value.parse().unwrap_or(cli.tick_rate);
                }
            }
            "--demo-input" => {
                cli.demo_input = true;
            }
            "--simulation-speed" => {
                if let Some(value) = args.next() {
                    if let Ok(speed) = value.parse::<f32>() {
                        if speed.is_finite() && speed > 0.0 {
                            cli.simulation_speed = speed;
                        }
                    }
                }
            }
            "--playtest-report" => {
                if let Some(value) = args.next() {
                    cli.playtest_report = Some(PathBuf::from(value));
                }
            }
            "--auto-exit-after-report" => {
                cli.auto_exit_after_report = true;
            }
            "--player-skill" => {
                if let Some(value) = args.next() {
                    cli.player_skill = value;
                }
            }
            "--capture-interval" => {
                if let Some(value) = args.next() {
                    cli.capture_interval_seconds =
                        value.parse().unwrap_or(cli.capture_interval_seconds);
                }
            }
            _ => {}
        }
    }

    cli
}

impl RuntimeCaptureState {
    fn from_cli(cli: &RuntimeCli) -> Self {
        Self {
            report_path: cli.playtest_report.clone(),
            player_skill: cli.player_skill.clone(),
            capture_interval_seconds: cli.capture_interval_seconds.max(0.5),
            next_sample_seconds: 0.0,
            event_counts: RuntimeEventCounts::default(),
            samples: Vec::new(),
            finished: false,
        }
    }

    fn enabled(&self) -> bool {
        self.report_path.is_some()
    }

    fn should_sample(&self, time_seconds: f32, force: bool) -> bool {
        force || time_seconds + f32::EPSILON >= self.next_sample_seconds
    }

    fn record_sample(&mut self, sample: RuntimeTelemetrySample, time_seconds: f32) {
        self.samples.push(sample);
        while time_seconds + f32::EPSILON >= self.next_sample_seconds {
            self.next_sample_seconds += self.capture_interval_seconds;
        }
    }

    fn reset_for_next_run(&mut self) {
        self.next_sample_seconds = 0.0;
        self.event_counts = RuntimeEventCounts::default();
        self.samples.clear();
        self.finished = false;
    }
}

impl RuntimeEventCounts {
    fn observe(&mut self, events: &[GameEvent]) {
        for event in events {
            match event {
                GameEvent::EnemySpawned { .. } => self.enemy_spawned += 1,
                GameEvent::BossSpawned { .. } => self.boss_spawned += 1,
                GameEvent::WeaponFired { .. } => self.weapon_fired += 1,
                GameEvent::EnemyHit { .. } => self.enemy_hit += 1,
                GameEvent::EnemyKilled { .. } => self.enemy_killed += 1,
                GameEvent::XpDropped { .. } => self.xp_dropped += 1,
                GameEvent::XpCollected { .. } => self.xp_collected += 1,
                GameEvent::LevelUp { .. } => self.level_up += 1,
                GameEvent::UpgradeOffered { .. } => self.upgrade_offered += 1,
                GameEvent::UpgradeChosen { .. } => self.upgrade_chosen += 1,
                GameEvent::PlayerDamaged { .. } => self.player_damaged += 1,
                GameEvent::RunEnded { .. } => self.run_ended += 1,
            }
        }
    }
}

impl RuntimeTelemetrySample {
    fn from_snapshot(
        snapshot: &RunSnapshot,
        active_effects: usize,
        last_event_kind: RuntimeEventKind,
    ) -> Self {
        Self {
            time_seconds: snapshot.time_seconds,
            health: snapshot.player.health,
            max_health: snapshot.player.max_health,
            level: snapshot.player.level,
            xp: snapshot.player.xp,
            xp_to_next_level: snapshot.player.xp_to_next_level,
            kills: snapshot.metrics_partial.kills,
            visible_enemies: snapshot.visible_enemies.len(),
            visible_pickups: snapshot.visible_pickups.len(),
            visible_projectiles: snapshot.visible_projectiles.len(),
            active_effects,
            upgrade_options: snapshot.upgrade_options.len(),
            last_event_kind: last_event_kind.label(),
        }
    }
}

impl RuntimePlaytestReport {
    fn from_state(state: &RuntimeState, metrics: RunMetrics) -> Self {
        Self {
            kind: "runtime_playtest_capture",
            report_version: 1,
            player_skill: state.capture.player_skill.clone(),
            input_mode: if state.demo_input { "demo" } else { "keyboard" },
            simulation_speed: state.simulation_speed,
            auto_exit_after_report: state.auto_exit_after_report,
            run_number: state.run_number,
            content_dir: state.content_dir.display().to_string(),
            run_config: RuntimeRunConfigReport::from_config(&state.config),
            event_counts: state.capture.event_counts.clone(),
            samples: state.capture.samples.clone(),
            final_metrics: RuntimeMetricsReport::from_metrics(metrics),
            manual_review: RuntimeManualReviewTemplate::default_for_runtime(),
        }
    }
}

impl RuntimeRunConfigReport {
    fn from_config(config: &RunConfig) -> Self {
        Self {
            seed: config.seed,
            map_id: config.map_id.clone(),
            character_id: config.character_id.clone(),
            difficulty: difficulty_label(config.difficulty),
            duration_seconds: config.duration_seconds,
            tick_rate: config.tick_rate,
            ruleset_version: config.ruleset_version.clone(),
            content_pack_ids: config.content_pack_ids.clone(),
            starting_weapons: config.starting_loadout.weapons.clone(),
            starting_passives: config.starting_loadout.passives.clone(),
        }
    }
}

impl RuntimeMetricsReport {
    fn from_metrics(metrics: RunMetrics) -> Self {
        Self {
            seed: metrics.seed,
            tick_rate: metrics.tick_rate,
            duration_seconds: metrics.duration_seconds,
            terminal: metrics.terminal.map(RuntimeTerminalReport::from_terminal),
            kills: metrics.kills,
            level: metrics.level,
            xp_collected: metrics.xp_collected,
            xp_dropped: metrics.xp_dropped,
            damage_dealt_by_weapon: metrics.damage_dealt_by_weapon,
            damage_taken: metrics.damage_taken,
            max_enemy_count: metrics.max_enemy_count,
            max_projectile_count: metrics.max_projectile_count,
            upgrade_choices: metrics.upgrade_choices,
        }
    }
}

impl RuntimeTerminalReport {
    fn from_terminal(terminal: TerminalState) -> Self {
        Self {
            kind: terminal.kind.as_str(),
            time_seconds: terminal.time_seconds,
            reason: terminal.reason,
            final_level: terminal.final_level,
            kills: terminal.kills,
        }
    }
}

impl RuntimeManualReviewTemplate {
    fn default_for_runtime() -> Self {
        Self {
            fun_rating: None,
            clarity_rating: None,
            difficulty_rating: None,
            projectile_readability: None,
            hit_feedback: None,
            xp_pickup_rhythm: None,
            boss_spawn_clarity: None,
            death_reason_clarity: None,
            notes: "人工试玩后补充：是否看得清、是否知道为什么死、升级选择是否有纠结、是否有再来一局冲动。".to_string(),
            tags: Vec::new(),
            next_actions: Vec::new(),
        }
    }
}

fn write_runtime_playtest_report(
    capture: &RuntimeCaptureState,
    report: &RuntimePlaytestReport,
) -> std::io::Result<()> {
    let Some(path) = &capture.report_path else {
        return Ok(());
    };
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }
    let json = serde_json::to_string_pretty(report)?;
    fs::write(path, format!("{json}\n"))
}

#[cfg(test)]
mod tests {
    use super::{
        demo_movement, demo_upgrade_choice, effects_for_events, event_kind_for_events,
        make_tone_wav, parse_runtime_cli, player_tint, run_config_from_cli, runtime_asset_root,
        runtime_sprite_paths, sounds_for_events, RuntimeCaptureState, RuntimeEffectKind,
        RuntimeEventCounts, RuntimeEventKind, RuntimeSound, DEFAULT_CONTENT_DIR,
    };
    use game_core::{
        BossSnapshot, EnemyBehavior, EnemySnapshot, GameCore, GameEvent, PickupSnapshot,
        PickupType, RunConfig, Vec2 as CoreVec2,
    };
    use std::path::PathBuf;

    #[test]
    fn parses_runtime_cli_overrides() {
        let cli = parse_runtime_cli([
            "--content-dir".to_string(),
            "content/custom".to_string(),
            "--seed".to_string(),
            "9".to_string(),
            "--seconds".to_string(),
            "120".to_string(),
            "--tick-rate".to_string(),
            "20".to_string(),
            "--demo-input".to_string(),
            "--simulation-speed".to_string(),
            "4".to_string(),
            "--auto-exit-after-report".to_string(),
        ]);

        assert_eq!(cli.content_dir, PathBuf::from("content/custom"));
        assert_eq!(cli.seed, 9);
        assert_eq!(cli.seconds, 120.0);
        assert_eq!(cli.tick_rate, 20);
        assert!(cli.demo_input);
        assert_eq!(cli.simulation_speed, 4.0);
        assert!(cli.auto_exit_after_report);
    }

    #[test]
    fn parses_runtime_playtest_capture_options() {
        let cli = parse_runtime_cli([
            "--playtest-report".to_string(),
            "harness/telemetry/local/report.json".to_string(),
            "--player-skill".to_string(),
            "new".to_string(),
            "--capture-interval".to_string(),
            "2.5".to_string(),
        ]);

        assert_eq!(
            cli.playtest_report,
            Some(PathBuf::from("harness/telemetry/local/report.json"))
        );
        assert_eq!(cli.player_skill, "new");
        assert_eq!(cli.capture_interval_seconds, 2.5);
    }

    #[test]
    fn keeps_runtime_cli_defaults_for_bad_values() {
        let cli = parse_runtime_cli([
            "--seed".to_string(),
            "bad".to_string(),
            "--simulation-speed".to_string(),
            "-1".to_string(),
        ]);

        assert_eq!(cli.content_dir, PathBuf::from(DEFAULT_CONTENT_DIR));
        assert_eq!(cli.seed, 12_345);
        assert_eq!(cli.simulation_speed, 1.0);
    }

    #[test]
    fn builds_runtime_run_config_from_cli() {
        let cli = parse_runtime_cli(["--seed".to_string(), "77".to_string()]);
        let config = run_config_from_cli(&cli);

        assert_eq!(config.seed, 77);
        assert_eq!(config.map_id, "frosting-grassland");
        assert_eq!(config.starting_loadout.weapons, ["rainbow-candy-shot"]);
    }

    #[test]
    fn low_health_changes_player_tint() {
        assert_ne!(player_tint(100.0, 100.0), player_tint(20.0, 100.0));
    }

    #[test]
    fn runtime_asset_root_points_to_workspace_assets() {
        let root = PathBuf::from(runtime_asset_root());

        assert!(root.ends_with("assets"));
        assert!(root.join("prototype_topdown/manifest.json").exists());
    }

    #[test]
    fn runtime_sprite_paths_exist() {
        let root = PathBuf::from(runtime_asset_root());

        for path in runtime_sprite_paths() {
            assert!(root.join(path).exists(), "missing runtime sprite {path}");
        }
    }

    #[test]
    fn capture_state_samples_on_interval_and_reset() {
        let cli = parse_runtime_cli([
            "--playtest-report".to_string(),
            "harness/telemetry/local/report.json".to_string(),
            "--capture-interval".to_string(),
            "2".to_string(),
        ]);
        let mut capture = RuntimeCaptureState::from_cli(&cli);

        assert!(capture.enabled());
        assert!(capture.should_sample(0.0, false));
        capture.record_sample(
            super::RuntimeTelemetrySample {
                time_seconds: 0.0,
                health: 100.0,
                max_health: 100.0,
                level: 1,
                xp: 0.0,
                xp_to_next_level: 10.0,
                kills: 0,
                visible_enemies: 0,
                visible_pickups: 0,
                visible_projectiles: 0,
                active_effects: 0,
                upgrade_options: 0,
                last_event_kind: "status",
            },
            0.0,
        );

        assert!(!capture.should_sample(1.0, false));
        assert!(capture.should_sample(2.0, false));
        capture.reset_for_next_run();
        assert!(capture.samples.is_empty());
        assert!(capture.should_sample(0.0, false));
    }

    #[test]
    fn event_counts_cover_runtime_capture_events() {
        let mut counts = RuntimeEventCounts::default();
        counts.observe(&[
            GameEvent::WeaponFired {
                weapon_id: "rainbow-candy-shot".to_string(),
                projectile_count: 1,
            },
            GameEvent::XpCollected {
                entity_id: 7,
                value: 3.0,
            },
            GameEvent::PlayerDamaged { amount: 2.0 },
        ]);

        assert_eq!(counts.weapon_fired, 1);
        assert_eq!(counts.xp_collected, 1);
        assert_eq!(counts.player_damaged, 1);
    }

    #[test]
    fn demo_input_chooses_first_upgrade() {
        let mut snapshot = GameCore::reset(RunConfig::default()).snapshot();
        assert_eq!(demo_upgrade_choice(&snapshot), None);

        snapshot
            .upgrade_options
            .push(game_core::UpgradeOptionSnapshot {
                id: "rainbow-candy-shot-level-2".to_string(),
                name: "彩虹糖弹 Lv2".to_string(),
                tags: vec!["projectile".to_string()],
                description: "提升彩虹糖弹。".to_string(),
            });

        assert_eq!(demo_upgrade_choice(&snapshot), Some(0));
    }

    #[test]
    fn demo_movement_prefers_pickups_when_safe() {
        let mut snapshot = GameCore::reset(RunConfig::default()).snapshot();
        snapshot.visible_pickups.push(PickupSnapshot {
            entity_id: 1,
            pickup_type: PickupType::Xp,
            position: CoreVec2::new(40.0, 0.0),
            value: 3.0,
            radius: 10.0,
        });

        let movement = demo_movement(&snapshot);
        assert!(movement.x > 0.9);
        assert!(movement.y.abs() < 0.1);
    }

    #[test]
    fn demo_movement_avoids_nearby_enemy() {
        let mut snapshot = GameCore::reset(RunConfig::default()).snapshot();
        snapshot.visible_pickups.push(PickupSnapshot {
            entity_id: 1,
            pickup_type: PickupType::Xp,
            position: CoreVec2::new(40.0, 0.0),
            value: 3.0,
            radius: 10.0,
        });
        snapshot.visible_enemies.push(EnemySnapshot {
            entity_id: 2,
            enemy_id: "bouncy-gummy".to_string(),
            position: CoreVec2::new(20.0, 0.0),
            velocity: CoreVec2::ZERO,
            health: 10.0,
            max_health: 10.0,
            radius: 16.0,
            threat: 1.0,
            behavior: EnemyBehavior::Chase,
            is_boss: false,
            is_elite: false,
        });

        let movement = demo_movement(&snapshot);
        assert!(movement.x < -0.9);
        assert!(movement.y.abs() < 0.1);
    }

    #[test]
    fn maps_events_to_runtime_feedback() {
        let events = [
            GameEvent::WeaponFired {
                weapon_id: "rainbow-candy-shot".to_string(),
                projectile_count: 1,
            },
            GameEvent::PlayerDamaged { amount: 3.0 },
        ];

        assert_eq!(event_kind_for_events(&events), RuntimeEventKind::Damage);
        assert_eq!(
            sounds_for_events(&events),
            [RuntimeSound::Fire, RuntimeSound::Damage]
        );
    }

    #[test]
    fn maps_events_to_runtime_visual_effects() {
        let mut snapshot = GameCore::reset(RunConfig::default()).snapshot();
        let enemy_position = CoreVec2::new(12.0, 24.0);
        let pickup_position = CoreVec2::new(-8.0, 16.0);
        let boss_position = CoreVec2::new(42.0, -20.0);
        snapshot.visible_enemies.push(EnemySnapshot {
            entity_id: 10,
            enemy_id: "bouncy-gummy".to_string(),
            position: enemy_position,
            velocity: CoreVec2::ZERO,
            health: 12.0,
            max_health: 20.0,
            radius: 16.0,
            threat: 1.0,
            behavior: EnemyBehavior::Chase,
            is_boss: false,
            is_elite: false,
        });
        snapshot.visible_pickups.push(PickupSnapshot {
            entity_id: 20,
            pickup_type: PickupType::Xp,
            position: pickup_position,
            value: 6.0,
            radius: 10.0,
        });
        snapshot.boss = Some(BossSnapshot {
            entity_id: 30,
            boss_id: "runaway-sugar-mixer".to_string(),
            health: 200.0,
            max_health: 200.0,
            position: boss_position,
        });

        let effects = effects_for_events(
            &[
                GameEvent::EnemyHit {
                    entity_id: 10,
                    damage: 7.0,
                    weapon_id: "rainbow-candy-shot".to_string(),
                },
                GameEvent::XpDropped {
                    entity_id: 20,
                    value: 6.0,
                },
                GameEvent::XpCollected {
                    entity_id: 20,
                    value: 6.0,
                },
                GameEvent::PlayerDamaged { amount: 3.0 },
                GameEvent::BossSpawned {
                    entity_id: 30,
                    boss_id: "runaway-sugar-mixer".to_string(),
                },
            ],
            &snapshot,
        );

        assert_eq!(effects.len(), 5);
        assert!(effects.iter().any(|effect| {
            effect.kind == RuntimeEffectKind::ProjectileHit && effect.position == enemy_position
        }));
        assert!(effects.iter().any(|effect| {
            effect.kind == RuntimeEffectKind::XpDrop && effect.position == pickup_position
        }));
        assert!(effects.iter().any(|effect| {
            effect.kind == RuntimeEffectKind::XpCollect
                && effect.position == snapshot.player.position
        }));
        assert!(effects.iter().any(|effect| {
            effect.kind == RuntimeEffectKind::PlayerDamage
                && effect.position == snapshot.player.position
        }));
        assert!(effects.iter().any(|effect| {
            effect.kind == RuntimeEffectKind::BossSpawn && effect.position == boss_position
        }));
    }

    #[test]
    fn generated_placeholder_wav_has_header() {
        let wav = make_tone_wav(440.0, 0.05, 0.25);

        assert!(wav.starts_with(b"RIFF"));
        assert_eq!(&wav[8..12], b"WAVE");
        assert_eq!(&wav[12..16], b"fmt ");
        assert_eq!(&wav[36..40], b"data");
    }
}
