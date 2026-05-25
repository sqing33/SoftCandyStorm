use bevy::prelude::*;
use game_core::{
    ContentPack, Difficulty, FixedDt, GameCore, GameEvent, PlayerAction, RunConfig, RunSnapshot,
    StartingLoadout, TerminalKind, Vec2 as CoreVec2,
};
use std::path::PathBuf;

const DEFAULT_CONTENT_DIR: &str = "content/base_demo";
const CAMERA_Z: f32 = 999.0;
const PLAYER_Z: f32 = 20.0;
const ENEMY_Z: f32 = 10.0;
const PICKUP_Z: f32 = 5.0;
const MAP_Z: f32 = -20.0;
const MAP_BORDER_Z: f32 = -19.0;

fn main() {
    App::new()
        .insert_resource(ClearColor(Color::srgb(0.95, 0.91, 0.78)))
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: "Soft Candy Storm Runtime Prototype".to_string(),
                resolution: (1280.0, 720.0).into(),
                present_mode: bevy::window::PresentMode::AutoVsync,
                ..default()
            }),
            ..default()
        }))
        .add_systems(Startup, setup_runtime)
        .add_systems(
            Update,
            (
                step_game_core,
                sync_camera.after(step_game_core),
                sync_world_visuals.after(step_game_core),
                update_hud.after(step_game_core),
            ),
        )
        .run();
}

#[derive(Debug, Clone)]
struct RuntimeCli {
    content_dir: PathBuf,
    seed: u64,
    seconds: f32,
    tick_rate: u32,
}

impl Default for RuntimeCli {
    fn default() -> Self {
        Self {
            content_dir: PathBuf::from(DEFAULT_CONTENT_DIR),
            seed: 12_345,
            seconds: 600.0,
            tick_rate: 30,
        }
    }
}

#[derive(Resource)]
struct RuntimeState {
    content: ContentPack,
    config: RunConfig,
    core: GameCore,
    dt: FixedDt,
    dt_seconds: f32,
    accumulator: f32,
    latest_snapshot: RunSnapshot,
    last_event: String,
    paused: bool,
    run_number: u32,
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

fn setup_runtime(mut commands: Commands) {
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
        config,
        core,
        dt,
        dt_seconds: dt.seconds(),
        accumulator: 0.0,
        latest_snapshot,
        last_event: "run started".to_string(),
        paused: false,
        run_number: 1,
    });
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
    let upgrade_choice = upgrade_choice_from_keyboard(&keyboard, &snapshot);

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
            state.last_event = describe_events(&result.events);
            state.latest_snapshot = result.snapshot;
        } else {
            state.latest_snapshot = snapshot;
        }
        return;
    }

    state.accumulator = (state.accumulator + time.delta_seconds()).min(0.25);
    let movement = movement_from_keyboard(&keyboard);
    while state.accumulator >= state.dt_seconds && !state.core.is_terminal() {
        let result = state.core.step(
            PlayerAction {
                movement,
                upgrade_choice: None,
            },
            dt,
        );
        state.accumulator -= state.dt_seconds;
        state.last_event = describe_events(&result.events);
        state.latest_snapshot = result.snapshot;

        if !state.latest_snapshot.upgrade_options.is_empty() {
            state.accumulator = 0.0;
            break;
        }
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
    visuals: Query<Entity, With<RuntimeVisual>>,
) {
    for entity in &visuals {
        commands.entity(entity).despawn_recursive();
    }

    let snapshot = &state.latest_snapshot;
    commands.spawn((
        SpriteBundle {
            sprite: Sprite {
                color: Color::srgb(0.82, 0.94, 0.68),
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
        commands.spawn((
            SpriteBundle {
                sprite: Sprite {
                    color: Color::srgb(0.25, 0.78, 0.96),
                    custom_size: Some(Vec2::splat((pickup.radius * 1.6).max(8.0))),
                    ..default()
                },
                transform: Transform::from_xyz(pickup.position.x, pickup.position.y, PICKUP_Z),
                ..default()
            },
            RuntimeVisual,
        ));
    }

    for enemy in &snapshot.visible_enemies {
        commands.spawn((
            SpriteBundle {
                sprite: Sprite {
                    color: enemy_color(enemy.is_boss, enemy.is_elite),
                    custom_size: Some(Vec2::splat(enemy.radius * 2.0)),
                    ..default()
                },
                transform: Transform::from_xyz(enemy.position.x, enemy.position.y, ENEMY_Z),
                ..default()
            },
            RuntimeVisual,
        ));
    }

    commands.spawn((
        SpriteBundle {
            sprite: Sprite {
                color: player_color(snapshot.player.health, snapshot.player.max_health),
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

fn enemy_color(is_boss: bool, is_elite: bool) -> Color {
    if is_boss {
        Color::srgb(0.92, 0.20, 0.38)
    } else if is_elite {
        Color::srgb(0.74, 0.27, 0.91)
    } else {
        Color::srgb(1.0, 0.45, 0.58)
    }
}

fn player_color(health: f32, max_health: f32) -> Color {
    let ratio = if max_health > 0.0 {
        (health / max_health).clamp(0.0, 1.0)
    } else {
        0.0
    };
    if ratio < 0.30 {
        Color::srgb(1.0, 0.55, 0.48)
    } else {
        Color::srgb(1.0, 0.93, 0.98)
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
            "Run {}  {}  Time {:05.1}s  HP {:03.0}/{:03.0}  Lv {}  XP {:.0}/{:.0}  Kills {}  Enemies {}  {}\n{}",
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
            format!("Upgrade\n{options}")
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
                        "{title}  {:.1}s  Lv {}  Kills {}",
                        terminal.time_seconds, terminal.final_level, terminal.kills
                    )
                })
                .unwrap_or_default()
        };
    }
}

fn describe_events(events: &[GameEvent]) -> String {
    events
        .iter()
        .rev()
        .find_map(describe_event)
        .unwrap_or_else(|| "storm active".to_string())
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

fn reset_runtime_run(state: &mut RuntimeState) {
    let core = GameCore::reset_with_content(state.config.clone(), state.content.clone())
        .expect("runtime reset must use already validated content");
    state.core = core;
    state.latest_snapshot = state.core.snapshot();
    state.accumulator = 0.0;
    state.last_event = "run restarted".to_string();
    state.paused = false;
    state.run_number += 1;
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
            _ => {}
        }
    }

    cli
}

#[cfg(test)]
mod tests {
    use super::{parse_runtime_cli, player_color, run_config_from_cli, DEFAULT_CONTENT_DIR};
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
        ]);

        assert_eq!(cli.content_dir, PathBuf::from("content/custom"));
        assert_eq!(cli.seed, 9);
        assert_eq!(cli.seconds, 120.0);
        assert_eq!(cli.tick_rate, 20);
    }

    #[test]
    fn keeps_runtime_cli_defaults_for_bad_values() {
        let cli = parse_runtime_cli(["--seed".to_string(), "bad".to_string()]);

        assert_eq!(cli.content_dir, PathBuf::from(DEFAULT_CONTENT_DIR));
        assert_eq!(cli.seed, 12_345);
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
    fn low_health_changes_player_color() {
        assert_ne!(player_color(100.0, 100.0), player_color(20.0, 100.0));
    }
}
