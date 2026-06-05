use bevy::{
    asset::AssetPlugin,
    audio::{AudioBundle, AudioSource, PlaybackSettings, Volume},
    prelude::*,
    window::PrimaryWindow,
};
use game_core::{
    BossSnapshot, BuildItemSnapshot, BuildSnapshot, ContentPack, Difficulty, EnemySnapshot,
    FixedDt, GameCore, GameEvent, HazardSnapshot, MetaCodexEntry, MetaProgress, MetaRunSummary,
    MetaSettlementReport, PlayerAction, RunConfig, RunMetrics, RunSnapshot, StartingLoadout,
    StatusEffectSnapshot, TerminalKind, TerminalState, UpgradeOptionSnapshot, Vec2 as CoreVec2,
};
use serde::{Deserialize, Serialize};
use std::{
    collections::{BTreeMap, BTreeSet},
    env, fs,
    path::{Path, PathBuf},
    sync::Arc,
};

const DEFAULT_CONTENT_DIR: &str = "content/base_demo";
const DEFAULT_MAP_ID: &str = "frosting-grassland";
const DEFAULT_PLATFORM_DATA_ROOT: &str = "platform_user_data/soft-candy-storm";
const NATIVE_PLATFORM_APP_DIR_MACOS: &str = "Soft Candy Storm";
const NATIVE_PLATFORM_APP_DIR_UNIX: &str = "soft-candy-storm";
const PLATFORM_SAVE_ROOT: &str = "saves";
const PLATFORM_SETTINGS_ROOT: &str = "settings";
const PLATFORM_TELEMETRY_ROOT: &str = "telemetry";
const PLATFORM_REPLAY_ROOT: &str = "replay";
const PLATFORM_CRASH_REPORT_ROOT: &str = "crash-reports";
const PLATFORM_EXPORT_ROOT: &str = "exports";
const DEFAULT_SAVE_ID: &str = "local-demo-profile";
const DEFAULT_PROFILE_ID: &str = "local-player";
const RUNTIME_SETTINGS_FILE_NAME: &str = "runtime_privacy_settings.json";
const RUNTIME_SAVE_FILE_NAME: &str = "profile.json";
const RUNTIME_SAVE_EXPORT_FILE_NAME: &str = "profile_export.json";
const RUNTIME_LOCAL_DATA_EXPORT_FILE_NAME: &str = "local_data_export.json";
const RUNTIME_SAVE_V0_CONTRACT_ID: &str = "save-state-v0";
const RUNTIME_SAVE_V1_CONTRACT_ID: &str = "save-state-v1";
const RUNTIME_SAVE_V0_SCHEMA_VERSION: u32 = 1;
const RUNTIME_SAVE_V1_SCHEMA_VERSION: u32 = 2;
const RUNTIME_SAVE_MIGRATION_ID: &str = "save-state-v0-to-v1";
const RUNTIME_SAVE_TIMESTAMP: &str = "2026-05-26T00:00:00Z";
const STORY_CODEX_UI_CANDIDATE_MANIFEST_CONTRACT_ID: &str = "story-codex-ui-candidate-manifest-v0";
const STORY_CODEX_UI_CANDIDATE_STAGE: &str = "story_codex_ui_candidate";
const ASSET_RUNTIME_CANDIDATE_MANIFEST_CONTRACT_ID: &str = "asset-runtime-candidate-manifest-v0";
const ASSET_RUNTIME_CANDIDATE_STAGE: &str = "asset_runtime_candidate";
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
const MAX_PROFILED_FRAME_SECONDS: f32 = 0.10;
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
const META_PANEL_WIDTH: f32 = 430.0;
const META_PANEL_RIGHT_MARGIN: f32 = 14.0;
const META_PANEL_TAB_CONTROL_HEIGHT: f32 = 64.0;
const META_PANEL_TAB_CONTROL_ZONE_COUNT: usize = 5;
const META_PANEL_HEADER: &str = "糖罐守护站  F1 概览 | F2 章节 | F3 图鉴 | F4 设置 | F5 巡逻";
const META_PANEL_TAB_CLICK_HINT: &str = "页签点击区: 概览  章节  图鉴  设置  巡逻";
const OVERVIEW_POINTER_CONTROL_HEIGHT: f32 = 96.0;
const OVERVIEW_POINTER_CONTROL_ZONE_COUNT: usize = 4;
const CODEX_POINTER_CONTROL_HEIGHT: f32 = 96.0;
const CODEX_POINTER_CONTROL_ZONE_COUNT: usize = 5;
const SETTINGS_POINTER_CONTROL_HEIGHT: f32 = 112.0;
const SETTINGS_POINTER_CONTROL_ZONE_COUNT: usize = 7;
const LOADOUT_POINTER_CONTROL_HEIGHT: f32 = 96.0;
const LOADOUT_POINTER_CONTROL_ZONE_COUNT: usize = 2;
const CHAPTER_POINTER_CONTROL_HEIGHT: f32 = 96.0;
const CHAPTER_POINTER_CONTROL_ZONE_COUNT: usize = 3;
const UPGRADE_POINTER_CONTROL_HEIGHT: f32 = 190.0;
const UPGRADE_POINTER_CONTROL_ZONE_COUNT: usize = 3;
const LOADOUT_UNLOCKED_CHARACTER_LABEL_LIMIT: usize = 8;
const LOADOUT_UNLOCKED_MAP_LABEL_LIMIT: usize = 8;
const GAMEPAD_LEFT_STICK_DEADZONE: f32 = 0.15;

fn main() {
    let raw_args = std::env::args().skip(1).collect::<Vec<_>>();
    let prelaunch_cli = parse_runtime_cli(raw_args);
    match run_runtime_prelaunch_actions(&prelaunch_cli) {
        Ok(true) => return,
        Ok(false) => {}
        Err(error) => {
            eprintln!("runtime privacy/data action failed: {error}");
            std::process::exit(2);
        }
    }

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
                update_runtime_meta_settlement.after(step_game_core),
                capture_playtest_report.after(update_runtime_meta_settlement),
                sync_camera.after(step_game_core),
                sync_world_visuals.after(update_runtime_effects),
                update_hud.after(update_runtime_meta_settlement),
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
    accepted_lock_file: Option<PathBuf>,
    accepted_content_id: Option<String>,
    content_pack_ids: Vec<String>,
    character_id: String,
    seed: u64,
    map_id: String,
    seconds: f32,
    tick_rate: u32,
    demo_input: bool,
    simulation_speed: f32,
    playtest_report: Option<PathBuf>,
    auto_exit_after_report: bool,
    player_skill: String,
    capture_interval_seconds: f32,
    platform_data_root: PathBuf,
    runtime_settings_file: Option<PathBuf>,
    local_data_dirs: Vec<PathBuf>,
    explicit_local_data_dirs: Vec<PathBuf>,
    export_local_data: Option<PathBuf>,
    delete_local_data: bool,
    print_privacy_notice: bool,
    save_file: Option<PathBuf>,
    explicit_save_file: bool,
    export_save: Option<PathBuf>,
    delete_save: bool,
    story_codex_ui_candidate_manifest: Option<PathBuf>,
    asset_runtime_candidate_manifest: Option<PathBuf>,
    unlock_all_content: bool,
}

impl Default for RuntimeCli {
    fn default() -> Self {
        let platform_paths =
            RuntimePlatformPaths::from_data_root(PathBuf::from(DEFAULT_PLATFORM_DATA_ROOT));
        Self {
            content_dir: PathBuf::from(DEFAULT_CONTENT_DIR),
            accepted_lock_file: None,
            accepted_content_id: None,
            content_pack_ids: vec!["base-demo".to_string()],
            character_id: "jar-keeper".to_string(),
            seed: 12_345,
            map_id: DEFAULT_MAP_ID.to_string(),
            seconds: 600.0,
            tick_rate: 30,
            demo_input: false,
            simulation_speed: 1.0,
            playtest_report: None,
            auto_exit_after_report: false,
            player_skill: "unrated".to_string(),
            capture_interval_seconds: 5.0,
            platform_data_root: platform_paths.data_root.clone(),
            runtime_settings_file: Some(platform_paths.runtime_settings_file.clone()),
            local_data_dirs: vec![
                platform_paths.local_telemetry_dir.clone(),
                platform_paths.local_replay_dir.clone(),
                platform_paths.crash_report_dir.clone(),
            ],
            explicit_local_data_dirs: Vec::new(),
            export_local_data: None,
            delete_local_data: false,
            print_privacy_notice: false,
            save_file: Some(platform_paths.save_file.clone()),
            explicit_save_file: false,
            export_save: None,
            delete_save: false,
            story_codex_ui_candidate_manifest: None,
            asset_runtime_candidate_manifest: None,
            unlock_all_content: false,
        }
    }
}

#[derive(Debug, Clone)]
struct RuntimePlatformPaths {
    data_root: PathBuf,
    save_file: PathBuf,
    runtime_settings_file: PathBuf,
    local_telemetry_dir: PathBuf,
    local_replay_dir: PathBuf,
    crash_report_dir: PathBuf,
}

#[derive(Resource)]
struct RuntimeState {
    content: ContentPack,
    content_dir: PathBuf,
    content_pack_ids: Vec<String>,
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
    privacy_settings: RuntimePrivacySettings,
    platform_data_root: PathBuf,
    runtime_settings_file: Option<PathBuf>,
    save_file: Option<PathBuf>,
    local_data_dirs: Vec<PathBuf>,
    pending_data_delete_action: Option<RuntimeDataControlAction>,
    meta_panel_view: RuntimeMetaPanelView,
    base_ui_state: RuntimeBaseUiState,
    codex_selected_index: usize,
    meta_progress: MetaProgress,
    story_codex_ui_candidate: Option<RuntimeStoryCodexUiCandidateManifest>,
    asset_runtime_candidate: Option<RuntimeAssetCandidateManifest>,
    last_meta_settlement: Option<MetaSettlementReport>,
    settled_run_number: Option<u32>,
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
    BossAbility,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum RuntimeMetaPanelView {
    Overview,
    Chapters,
    Codex,
    Settings,
    Loadout,
}

fn runtime_meta_panel_view_from_key(key: &str) -> RuntimeMetaPanelView {
    match key {
        "chapters" => RuntimeMetaPanelView::Chapters,
        "codex" => RuntimeMetaPanelView::Codex,
        "settings" => RuntimeMetaPanelView::Settings,
        "loadout" => RuntimeMetaPanelView::Loadout,
        _ => RuntimeMetaPanelView::Overview,
    }
}

#[derive(Debug, Clone, Copy)]
struct RuntimeMapVisualStyle {
    display_name: &'static str,
    tile_tint: Color,
    border_color: Color,
    hazard_color: Color,
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
    frame_metrics: RuntimeFrameMetricsState,
    finished: bool,
}

#[derive(Debug, Clone, Default)]
struct RuntimeFrameMetricsState {
    frame_count: u32,
    total_frame_seconds: f32,
    min_frame_seconds: Option<f32>,
    max_frame_seconds: f32,
    slow_frame_count_45fps: u32,
    slow_frame_count_30fps: u32,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum RuntimeUploadKind {
    Telemetry,
    RawReplay,
    CrashReport,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum RuntimeDataControlAction {
    ExportSave,
    DeleteSave,
    ExportLocalData,
    DeleteLocalData,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum RuntimeSettingsAction {
    ToggleUpload(RuntimeUploadKind),
    DataControl(RuntimeDataControlAction),
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum RuntimeLoadoutAction {
    NextCharacter,
    NextMap,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum RuntimeChapterAction {
    Previous,
    Next,
    StartSelectedChapter,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum RuntimeCodexAction {
    PreviousCategory,
    NextCategory,
    PreviousEntry,
    NextEntry,
    ToggleDiscoveredOnly,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum RuntimeCodexCategory {
    Characters,
    Weapons,
    Passives,
    Enemies,
    Bosses,
    Maps,
    Evolutions,
    Events,
}

impl RuntimeCodexCategory {
    const ALL: [Self; 8] = [
        Self::Characters,
        Self::Weapons,
        Self::Passives,
        Self::Enemies,
        Self::Bosses,
        Self::Maps,
        Self::Evolutions,
        Self::Events,
    ];

    fn key(self) -> &'static str {
        match self {
            Self::Characters => "characters",
            Self::Weapons => "weapons",
            Self::Passives => "passives",
            Self::Enemies => "enemies",
            Self::Bosses => "bosses",
            Self::Maps => "maps",
            Self::Evolutions => "evolutions",
            Self::Events => "events",
        }
    }

    fn label(self) -> &'static str {
        match self {
            Self::Characters => "角色",
            Self::Weapons => "武器",
            Self::Passives => "被动",
            Self::Enemies => "敌人",
            Self::Bosses => "Boss",
            Self::Maps => "地图",
            Self::Evolutions => "进化",
            Self::Events => "事件",
        }
    }

    fn from_key(key: &str) -> Self {
        Self::ALL
            .iter()
            .copied()
            .find(|category| category.key() == key)
            .unwrap_or(Self::Characters)
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct RuntimeCodexEntryView {
    id: String,
    name: String,
    description: String,
    discovered: bool,
    first_seen_run: Option<String>,
    seen_count: u32,
    defeated_count: u32,
    used_count: u32,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
struct RuntimePrivacySettings {
    #[serde(default)]
    telemetry_upload_enabled: bool,
    #[serde(default)]
    raw_replay_upload_enabled: bool,
    #[serde(default)]
    crash_report_upload_enabled: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct RuntimeSaveStateV0 {
    schema_version: u32,
    contract_id: String,
    save_id: String,
    profile_id: String,
    created_at: String,
    updated_at: String,
    game_version: String,
    ruleset_version: String,
    content_pack_ids: Vec<String>,
    settings: RuntimePrivacySettings,
    data_controls: RuntimeSaveDataControls,
    meta_progress: MetaProgress,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct RuntimeSaveStateV1 {
    schema_version: u32,
    contract_id: String,
    save_id: String,
    profile_id: String,
    created_at: String,
    updated_at: String,
    game_version: String,
    ruleset_version: String,
    content_pack_ids: Vec<String>,
    settings: RuntimePrivacySettings,
    data_controls: RuntimeSaveDataControls,
    meta_progress: MetaProgress,
    migration_history: Vec<RuntimeSaveMigrationEntry>,
    base_ui_state: RuntimeBaseUiState,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct RuntimeSaveMigrationEntry {
    migration_id: String,
    source_save_id: String,
    source_contract_id: String,
    source_schema_version: u32,
    target_contract_id: String,
    target_schema_version: u32,
    migrated_at: String,
    status: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct RuntimeBaseUiState {
    selected_panel: String,
    last_selected_character_id: String,
    last_selected_map_id: String,
    last_selected_chapter_id: String,
    codex_view: RuntimeBaseCodexViewState,
    privacy_view: RuntimeBasePrivacyViewState,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct RuntimeBaseCodexViewState {
    selected_category: String,
    discovered_only: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct RuntimeBasePrivacyViewState {
    last_notice_version: String,
    pending_privacy_review: bool,
}

#[derive(Debug, Clone)]
struct RuntimeSaveReadResult {
    state: RuntimeSaveStateV1,
    migrated_from_v0: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct RuntimeSaveDataControls {
    local_only_by_default: bool,
    upload_requires_opt_in: bool,
    delete_save_available: bool,
    export_save_available: bool,
    export_format: String,
    retention_days: u32,
}

#[derive(Debug, Clone, Deserialize)]
struct RuntimeStoryCodexUiCandidateManifest {
    manifest_contract_id: String,
    stage: String,
    candidate_pack_id: String,
    manual_gate_decision: String,
    chapter_count: u32,
    codex_entry_count: u32,
    rules: RuntimeStoryCodexUiCandidateRules,
}

#[derive(Debug, Clone, Deserialize)]
struct RuntimeStoryCodexUiCandidateRules {
    accepted_content: bool,
    runtime_integrated: bool,
    requires_runtime_ui_review: bool,
    requires_final_human_acceptance: bool,
}

#[derive(Debug, Clone, Deserialize)]
struct RuntimeAssetCandidateManifest {
    manifest_contract_id: String,
    stage: String,
    candidate_batch_id: String,
    manual_gate_decision: String,
    asset_count: u32,
    assets: Vec<RuntimeAssetCandidateItem>,
    rules: RuntimeAssetCandidateRules,
}

#[derive(Debug, Clone, Deserialize)]
struct RuntimeAssetCandidateItem {
    id: String,
    #[serde(rename = "type")]
    asset_type: String,
    qa_status: String,
    #[serde(default)]
    allowed_candidate_uses: Vec<String>,
}

#[derive(Debug, Clone, Deserialize)]
struct RuntimeAssetCandidateRules {
    accepted_content: bool,
    runtime_integrated: bool,
    release_ready: bool,
    requires_runtime_preview: bool,
    requires_audio_loudness_review: bool,
    requires_final_human_acceptance: bool,
}

impl Default for RuntimeSaveDataControls {
    fn default() -> Self {
        Self {
            local_only_by_default: true,
            upload_requires_opt_in: true,
            delete_save_available: true,
            export_save_available: true,
            export_format: "json".to_string(),
            retention_days: 90,
        }
    }
}

impl Default for RuntimeBaseUiState {
    fn default() -> Self {
        Self {
            selected_panel: "overview".to_string(),
            last_selected_character_id: "jar-keeper".to_string(),
            last_selected_map_id: DEFAULT_MAP_ID.to_string(),
            last_selected_chapter_id: DEFAULT_MAP_ID.to_string(),
            codex_view: RuntimeBaseCodexViewState {
                selected_category: "characters".to_string(),
                discovered_only: true,
            },
            privacy_view: RuntimeBasePrivacyViewState {
                last_notice_version: "privacy-notice-v0".to_string(),
                pending_privacy_review: true,
            },
        }
    }
}

#[derive(Debug, Clone, Serialize)]
struct RuntimePrivacyReport {
    telemetry_upload_enabled: bool,
    raw_replay_upload_enabled: bool,
    crash_report_upload_enabled: bool,
    local_capture_only: bool,
    upload_transport: &'static str,
}

#[derive(Debug, Clone, Serialize)]
struct RuntimeLocalDataExport {
    kind: &'static str,
    export_version: u32,
    privacy_settings: RuntimePrivacySettings,
    local_data_dirs: Vec<String>,
    files: Vec<RuntimeLocalDataFile>,
}

#[derive(Debug, Clone, Serialize)]
struct RuntimeLocalDataFile {
    root: String,
    relative_path: String,
    encoding: &'static str,
    contents: String,
}

#[derive(Debug, Clone, Serialize)]
struct RuntimeLocalDataDeleteReport {
    kind: &'static str,
    deleted_files: usize,
    deleted_dirs: usize,
    skipped_missing_roots: Vec<String>,
    local_data_dirs: Vec<String>,
}

#[derive(Debug, Clone)]
struct RuntimeDataControlContext {
    platform_data_root: PathBuf,
    runtime_settings_file: Option<PathBuf>,
    save_file: Option<PathBuf>,
    local_data_dirs: Vec<PathBuf>,
    content_pack_ids: Vec<String>,
    privacy_settings: RuntimePrivacySettings,
}

struct RuntimeMetaPanelRenderContext<'a> {
    privacy_settings: &'a RuntimePrivacySettings,
    runtime_settings_file: Option<&'a Path>,
    story_codex_ui_candidate: Option<&'a RuntimeStoryCodexUiCandidateManifest>,
    asset_runtime_candidate: Option<&'a RuntimeAssetCandidateManifest>,
    content: &'a ContentPack,
    config: &'a RunConfig,
    base_ui_state: &'a RuntimeBaseUiState,
    codex_selected_index: usize,
}

#[derive(Debug, Clone, Default, Serialize)]
struct RuntimeEventCounts {
    enemy_spawned: u32,
    boss_spawned: u32,
    boss_phase_changed: u32,
    boss_ability_used: u32,
    weapon_fired: u32,
    enemy_hit: u32,
    enemy_killed: u32,
    xp_dropped: u32,
    xp_collected: u32,
    level_up: u32,
    upgrade_offered: u32,
    upgrade_chosen: u32,
    player_damaged: u32,
    content_event_triggered: u32,
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
    active_hazards: usize,
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
    frame_metrics: RuntimeFrameMetricsReport,
    event_counts: RuntimeEventCounts,
    samples: Vec<RuntimeTelemetrySample>,
    final_metrics: RuntimeMetricsReport,
    privacy: RuntimePrivacyReport,
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
struct RuntimeFrameMetricsReport {
    frame_count: u32,
    total_frame_seconds: f32,
    average_frame_seconds: f32,
    average_fps: f32,
    min_frame_seconds: f32,
    max_frame_seconds: f32,
    worst_frame_fps: f32,
    slow_frame_count_45fps: u32,
    slow_frame_count_30fps: u32,
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

#[derive(Debug, Clone, Deserialize)]
struct AcceptedContentLockFile {
    status: String,
    entries: Vec<AcceptedContentLockEntry>,
}

#[derive(Debug, Clone, Deserialize)]
struct AcceptedContentLockEntry {
    id: String,
    runtime_content_dir: String,
    status: String,
    content_hash: Option<String>,
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

#[derive(Component)]
struct MetaText;

type TerminalTextFilter = (
    With<TerminalText>,
    Without<HudText>,
    Without<UpgradeText>,
    Without<MetaText>,
);
type MetaTextFilter = (
    With<MetaText>,
    Without<HudText>,
    Without<UpgradeText>,
    Without<TerminalText>,
);

fn setup_runtime(
    mut commands: Commands,
    mut audio_sources: ResMut<Assets<AudioSource>>,
    asset_server: Res<AssetServer>,
) {
    let cli = resolve_runtime_content_selection(parse_runtime_cli(std::env::args().skip(1)))
        .unwrap_or_else(|error| panic!("failed to resolve runtime content selection: {error}"));
    let privacy_settings = load_runtime_privacy_settings(&cli).unwrap_or_else(|error| {
        panic!(
            "failed to load runtime privacy settings from `{}`: {error}",
            cli.runtime_settings_file
                .as_ref()
                .map(|path| path.display().to_string())
                .unwrap_or_else(|| "defaults".to_string())
        )
    });
    let runtime_save_state =
        load_runtime_save_state(&cli, &privacy_settings).unwrap_or_else(|error| {
            panic!(
                "failed to load runtime save from `{}`: {error}",
                cli.save_file
                    .as_ref()
                    .map(|path| path.display().to_string())
                    .unwrap_or_else(|| "demo defaults".to_string())
            )
        });
    let mut meta_progress = runtime_save_state.meta_progress.clone();
    let base_ui_state = runtime_save_state.base_ui_state.clone();
    let story_codex_ui_candidate = load_runtime_story_codex_ui_candidate_manifest(&cli)
        .unwrap_or_else(|error| {
            panic!("failed to load story/codex UI candidate manifest: {error}")
        });
    let asset_runtime_candidate = load_runtime_asset_candidate_manifest(&cli)
        .unwrap_or_else(|error| panic!("failed to load asset Runtime candidate manifest: {error}"));
    let content = ContentPack::load_from_dir(&cli.content_dir).unwrap_or_else(|error| {
        panic!(
            "failed to load runtime content from `{}`: {error}",
            cli.content_dir.display()
        )
    });
    if cli.unlock_all_content {
        unlock_runtime_content_for_session(&mut meta_progress, &content);
    }
    let config = run_config_from_cli(&cli, &content);
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
    commands.spawn((
        TextBundle::from_section(
            "",
            TextStyle {
                font_size: 17.0,
                color: Color::srgb(0.16, 0.12, 0.08),
                ..default()
            },
        )
        .with_style(Style {
            position_type: PositionType::Absolute,
            right: Val::Px(14.0),
            top: Val::Px(12.0),
            width: Val::Px(430.0),
            ..default()
        }),
        MetaText,
    ));

    commands.insert_resource(RuntimeState {
        content,
        content_dir: cli.content_dir.clone(),
        content_pack_ids: cli.content_pack_ids.clone(),
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
        privacy_settings,
        platform_data_root: cli.platform_data_root.clone(),
        runtime_settings_file: cli.runtime_settings_file.clone(),
        save_file: cli.save_file.clone(),
        local_data_dirs: cli.local_data_dirs.clone(),
        pending_data_delete_action: None,
        meta_panel_view: runtime_meta_panel_view_from_key(&base_ui_state.selected_panel),
        base_ui_state,
        codex_selected_index: 0,
        meta_progress,
        story_codex_ui_candidate,
        asset_runtime_candidate,
        last_meta_settlement: None,
        settled_run_number: None,
    });
    commands.insert_resource(create_runtime_sounds(&mut audio_sources));
    commands.insert_resource(load_runtime_sprites(&asset_server));
}

fn select_runtime_meta_panel(
    state: &mut RuntimeState,
    view: RuntimeMetaPanelView,
    panel_key: &'static str,
    event: &'static str,
) {
    state.meta_panel_view = view;
    state.base_ui_state.selected_panel = panel_key.to_string();
    state.pending_data_delete_action = None;
    state.last_event = event.to_string();
    state.last_event_kind = RuntimeEventKind::System;
    if let Err(error) = persist_runtime_save_if_configured(state) {
        state.last_event = format!("base UI state save failed: {error}");
        state.last_event_kind = RuntimeEventKind::System;
        state.pending_sounds.push(RuntimeSound::System);
    }
}

fn runtime_meta_panel_selection(view: RuntimeMetaPanelView) -> (&'static str, &'static str) {
    match view {
        RuntimeMetaPanelView::Overview => ("overview", "guardian station overview"),
        RuntimeMetaPanelView::Chapters => ("chapters", "chapter goals view"),
        RuntimeMetaPanelView::Codex => ("codex", "codex progress view"),
        RuntimeMetaPanelView::Settings => ("settings", "privacy settings view"),
        RuntimeMetaPanelView::Loadout => ("loadout", "patrol loadout view"),
    }
}

fn step_game_core(
    time: Res<Time>,
    keyboard: Res<ButtonInput<KeyCode>>,
    mouse_buttons: Res<ButtonInput<MouseButton>>,
    gamepad_buttons: Res<ButtonInput<GamepadButton>>,
    gamepad_axes: Res<Axis<GamepadAxis>>,
    primary_window: Query<&Window, With<PrimaryWindow>>,
    mut state: ResMut<RuntimeState>,
) {
    state.capture.record_frame(time.delta_seconds());

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
    if keyboard.just_pressed(KeyCode::F1) {
        select_runtime_meta_panel(
            &mut state,
            RuntimeMetaPanelView::Overview,
            "overview",
            "guardian station overview",
        );
    }
    if keyboard.just_pressed(KeyCode::F2) {
        select_runtime_meta_panel(
            &mut state,
            RuntimeMetaPanelView::Chapters,
            "chapters",
            "chapter goals view",
        );
    }
    if keyboard.just_pressed(KeyCode::F3) {
        select_runtime_meta_panel(
            &mut state,
            RuntimeMetaPanelView::Codex,
            "codex",
            "codex progress view",
        );
    }
    if keyboard.just_pressed(KeyCode::F4) {
        select_runtime_meta_panel(
            &mut state,
            RuntimeMetaPanelView::Settings,
            "settings",
            "privacy settings view",
        );
    }
    if keyboard.just_pressed(KeyCode::F5) {
        select_runtime_meta_panel(
            &mut state,
            RuntimeMetaPanelView::Loadout,
            "loadout",
            "patrol loadout view",
        );
    }
    let pointer_tab_view = primary_window.get_single().ok().and_then(|window| {
        runtime_meta_panel_tab_view_from_pointer(
            &mouse_buttons,
            window.cursor_position(),
            Vec2::new(window.resolution.width(), window.resolution.height()),
        )
    });
    if let Some(view) = pointer_tab_view {
        let (panel_key, event) = runtime_meta_panel_selection(view);
        select_runtime_meta_panel(&mut state, view, panel_key, event);
        return;
    }
    if state.meta_panel_view == RuntimeMetaPanelView::Overview {
        let pointer_view = primary_window.get_single().ok().and_then(|window| {
            runtime_overview_view_from_pointer(
                &mouse_buttons,
                window.cursor_position(),
                Vec2::new(window.resolution.width(), window.resolution.height()),
            )
        });
        if let Some(view) = pointer_view {
            let (panel_key, event) = runtime_meta_panel_selection(view);
            select_runtime_meta_panel(&mut state, view, panel_key, event);
            return;
        }
    }
    if state.meta_panel_view == RuntimeMetaPanelView::Chapters {
        let pointer_action = primary_window.get_single().ok().and_then(|window| {
            runtime_chapter_action_from_pointer(
                &mouse_buttons,
                window.cursor_position(),
                Vec2::new(window.resolution.width(), window.resolution.height()),
            )
        });
        if let Some(action) = runtime_chapter_action_from_keyboard(&keyboard)
            .or(pointer_action)
            .or_else(|| runtime_chapter_action_from_gamepad(&gamepad_buttons))
        {
            match apply_runtime_chapter_action(&mut state, action) {
                Ok(message) => {
                    state.last_event = message;
                    state.last_event_kind = RuntimeEventKind::System;
                    state.pending_sounds.push(RuntimeSound::System);
                }
                Err(error) => {
                    state.last_event = format!("chapter selection failed: {error}");
                    state.last_event_kind = RuntimeEventKind::System;
                    state.pending_sounds.push(RuntimeSound::Damage);
                }
            }
        }
    }
    if state.meta_panel_view == RuntimeMetaPanelView::Codex {
        let pointer_action = primary_window.get_single().ok().and_then(|window| {
            runtime_codex_action_from_pointer(
                &mouse_buttons,
                window.cursor_position(),
                Vec2::new(window.resolution.width(), window.resolution.height()),
            )
        });
        if let Some(action) = runtime_codex_action_from_keyboard(&keyboard)
            .or(pointer_action)
            .or_else(|| runtime_codex_action_from_gamepad(&gamepad_buttons))
        {
            apply_runtime_codex_action(&mut state, action);
            if let Err(error) = persist_runtime_save_if_configured(&state) {
                state.last_event = format!("codex UI state save failed: {error}");
                state.last_event_kind = RuntimeEventKind::System;
                state.pending_sounds.push(RuntimeSound::System);
            }
        }
    }
    if state.meta_panel_view == RuntimeMetaPanelView::Loadout {
        let pointer_action = primary_window.get_single().ok().and_then(|window| {
            runtime_loadout_action_from_pointer(
                &mouse_buttons,
                window.cursor_position(),
                Vec2::new(window.resolution.width(), window.resolution.height()),
            )
        });
        if let Some(action) = runtime_loadout_action_from_keyboard(&keyboard)
            .or(pointer_action)
            .or_else(|| runtime_loadout_action_from_gamepad(&gamepad_buttons))
        {
            let result = match action {
                RuntimeLoadoutAction::NextCharacter => select_next_runtime_character(&mut state)
                    .map_err(|error| format!("character selection failed: {error}")),
                RuntimeLoadoutAction::NextMap => select_next_runtime_map(&mut state)
                    .map_err(|error| format!("map selection failed: {error}")),
            };
            match result {
                Ok(message) => {
                    state.last_event = message;
                    state.last_event_kind = RuntimeEventKind::System;
                    state.pending_sounds.push(RuntimeSound::System);
                }
                Err(message) => {
                    state.last_event = message;
                    state.last_event_kind = RuntimeEventKind::System;
                    state.pending_sounds.push(RuntimeSound::Damage);
                }
            }
            return;
        }
    }
    if state.meta_panel_view == RuntimeMetaPanelView::Settings {
        let pointer_action = primary_window.get_single().ok().and_then(|window| {
            runtime_settings_action_from_pointer(
                &mouse_buttons,
                window.cursor_position(),
                Vec2::new(window.resolution.width(), window.resolution.height()),
            )
        });
        if let Some(action) = runtime_settings_action_from_keyboard(&keyboard).or(pointer_action) {
            match action {
                RuntimeSettingsAction::ToggleUpload(kind) => {
                    state.pending_data_delete_action = None;
                    let enabled = toggle_runtime_privacy_setting(&mut state.privacy_settings, kind);
                    let persistence = match persist_runtime_privacy_settings_if_configured(&state) {
                        Ok(true) => "saved",
                        Ok(false) => "session only",
                        Err(error) => {
                            state.last_event = format!("privacy settings save failed: {error}");
                            state.last_event_kind = RuntimeEventKind::System;
                            state.pending_sounds.push(RuntimeSound::System);
                            return;
                        }
                    };
                    if let Err(error) = persist_runtime_save_if_configured(&state) {
                        state.last_event =
                            format!("privacy settings {persistence}, save sync failed: {error}");
                        state.last_event_kind = RuntimeEventKind::System;
                        state.pending_sounds.push(RuntimeSound::System);
                        return;
                    }
                    state.last_event = format!(
                        "{} {} ({persistence})",
                        runtime_upload_kind_label(kind),
                        if enabled { "enabled" } else { "disabled" }
                    );
                    state.last_event_kind = RuntimeEventKind::System;
                    state.pending_sounds.push(RuntimeSound::System);
                }
                RuntimeSettingsAction::DataControl(action) => {
                    match run_runtime_data_control_action_from_state(&mut state, action) {
                        Ok(message) => {
                            state.last_event = message;
                            state.last_event_kind = RuntimeEventKind::System;
                            state.pending_sounds.push(RuntimeSound::System);
                        }
                        Err(error) => {
                            state.last_event = format!("local data action failed: {error}");
                            state.last_event_kind = RuntimeEventKind::System;
                            state.pending_sounds.push(RuntimeSound::Damage);
                        }
                    }
                }
            }
        }
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
        let pointer_choice = primary_window.get_single().ok().and_then(|window| {
            upgrade_choice_from_pointer(
                &mouse_buttons,
                window.cursor_position(),
                Vec2::new(window.resolution.width(), window.resolution.height()),
                snapshot.upgrade_options.len(),
            )
        });
        upgrade_choice_from_keyboard(&keyboard, &snapshot)
            .or(pointer_choice)
            .or_else(|| {
                upgrade_choice_from_gamepad(&gamepad_buttons, snapshot.upgrade_options.len())
            })
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
        (movement_from_keyboard(&keyboard)
            + movement_from_gamepad_buttons(&gamepad_buttons)
            + movement_from_gamepad_axes(&gamepad_axes))
        .clamp_length_max(1.0)
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

fn update_runtime_meta_settlement(mut state: ResMut<RuntimeState>) {
    settle_runtime_meta_if_needed(&mut state);
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

fn movement_from_gamepad_buttons(gamepad_buttons: &ButtonInput<GamepadButton>) -> CoreVec2 {
    let mut x = 0.0;
    let mut y = 0.0;

    if gamepad_button_type_pressed(gamepad_buttons, &[GamepadButtonType::DPadLeft]) {
        x -= 1.0;
    }
    if gamepad_button_type_pressed(gamepad_buttons, &[GamepadButtonType::DPadRight]) {
        x += 1.0;
    }
    if gamepad_button_type_pressed(gamepad_buttons, &[GamepadButtonType::DPadUp]) {
        y += 1.0;
    }
    if gamepad_button_type_pressed(gamepad_buttons, &[GamepadButtonType::DPadDown]) {
        y -= 1.0;
    }

    CoreVec2::new(x, y).normalized_or_zero()
}

fn movement_from_gamepad_axes(gamepad_axes: &Axis<GamepadAxis>) -> CoreVec2 {
    let mut strongest = CoreVec2::ZERO;

    for axis in gamepad_axes.devices() {
        if !matches!(
            axis.axis_type,
            GamepadAxisType::LeftStickX | GamepadAxisType::LeftStickY
        ) {
            continue;
        }
        let gamepad = axis.gamepad;
        let candidate = CoreVec2::new(
            gamepad_axes
                .get(GamepadAxis::new(gamepad, GamepadAxisType::LeftStickX))
                .unwrap_or(0.0),
            gamepad_axes
                .get(GamepadAxis::new(gamepad, GamepadAxisType::LeftStickY))
                .unwrap_or(0.0),
        );
        if candidate.length_squared() > strongest.length_squared() {
            strongest = candidate;
        }
    }

    if strongest.length_squared() < GAMEPAD_LEFT_STICK_DEADZONE * GAMEPAD_LEFT_STICK_DEADZONE {
        CoreVec2::ZERO
    } else {
        strongest.clamp_length_max(1.0)
    }
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

fn upgrade_choice_from_pointer(
    mouse_buttons: &ButtonInput<MouseButton>,
    cursor_position: Option<Vec2>,
    window_size: Vec2,
    option_count: usize,
) -> Option<usize> {
    if !mouse_buttons.just_pressed(MouseButton::Left) {
        return None;
    }
    upgrade_choice_from_pointer_zone(cursor_position?, window_size, option_count)
}

fn upgrade_choice_from_pointer_zone(
    cursor_position: Vec2,
    window_size: Vec2,
    option_count: usize,
) -> Option<usize> {
    if option_count == 0 || window_size.x <= 0.0 || window_size.y <= 0.0 {
        return None;
    }

    let control_right = (window_size.x - META_PANEL_WIDTH - META_PANEL_RIGHT_MARGIN * 2.0).max(1.0);
    let in_control_x = cursor_position.x >= 0.0 && cursor_position.x <= control_right;
    let in_control_y =
        cursor_position.y >= 0.0 && cursor_position.y <= UPGRADE_POINTER_CONTROL_HEIGHT;
    if !in_control_x || !in_control_y {
        return None;
    }

    let normalized_x = (cursor_position.x / control_right).clamp(0.0, 0.999);
    let zone = (normalized_x * UPGRADE_POINTER_CONTROL_ZONE_COUNT as f32).floor() as usize;
    (zone < option_count).then_some(zone)
}

fn upgrade_choice_from_gamepad(
    gamepad_buttons: &ButtonInput<GamepadButton>,
    option_count: usize,
) -> Option<usize> {
    if option_count == 0 {
        return None;
    }

    for (button, index) in [
        (GamepadButtonType::South, 0usize),
        (GamepadButtonType::East, 1usize),
        (GamepadButtonType::North, 2usize),
    ] {
        if index < option_count && gamepad_button_type_just_pressed(gamepad_buttons, &[button]) {
            return Some(index);
        }
    }
    None
}

fn format_upgrade_options(options: &[UpgradeOptionSnapshot]) -> String {
    options
        .iter()
        .enumerate()
        .map(|(index, option)| {
            format!(
                "{}. {}  {}\n   {}\n   标签 {}  id {}",
                index + 1,
                option.name,
                format_upgrade_option_state(option),
                option.description,
                format_upgrade_tags(&option.tags),
                option.id,
            )
        })
        .collect::<Vec<_>>()
        .join("\n")
}

fn format_upgrade_option_state(option: &UpgradeOptionSnapshot) -> String {
    if let Some((_, level)) = option.id.rsplit_once("-level-") {
        if !level.is_empty() && level.chars().all(|character| character.is_ascii_digit()) {
            return format!("目标 Lv.{level}");
        }
    }

    if option.tags.iter().any(|tag| tag == "evolution") {
        return "进化".to_string();
    }

    if option.name.starts_with("获得") {
        "新获得".to_string()
    } else {
        "本局强化".to_string()
    }
}

fn format_upgrade_tags(tags: &[String]) -> String {
    if tags.is_empty() {
        "无".to_string()
    } else {
        tags.iter()
            .map(|tag| runtime_tag_label(tag))
            .collect::<Vec<_>>()
            .join(" / ")
    }
}

fn runtime_tag_label(tag: &str) -> String {
    match tag {
        "aoe" | "area" => "范围",
        "auto-fire" => "自动",
        "beam" => "光束",
        "beginner" => "新手",
        "boomerang" => "回旋",
        "boss-killer" => "Boss",
        "bubble" => "泡泡",
        "burst" => "爆发",
        "close" => "近身",
        "cold" => "冰霜",
        "control" => "控制",
        "cooldown" => "冷却",
        "defense" => "防御",
        "duration" => "持续",
        "economy" => "经济",
        "evolution" => "进化",
        "health" => "生命",
        "knockback" => "击退",
        "mobility" => "机动",
        "orbit" => "环绕",
        "pickup" => "拾取",
        "pierce" => "穿透",
        "projectile" => "弹幕",
        "single-target" => "单体",
        "size" => "尺寸",
        "slow" => "减速",
        "starter" => "初始",
        "summon" => "召唤",
        "trap" => "陷阱",
        "turret" => "炮台",
        "xp" => "XP",
        "zone" => "区域",
        other => return other.replace('-', " "),
    }
    .to_string()
}

fn privacy_toggle_from_keyboard(keyboard: &ButtonInput<KeyCode>) -> Option<RuntimeUploadKind> {
    if keyboard.just_pressed(KeyCode::Digit7) {
        Some(RuntimeUploadKind::Telemetry)
    } else if keyboard.just_pressed(KeyCode::Digit8) {
        Some(RuntimeUploadKind::RawReplay)
    } else if keyboard.just_pressed(KeyCode::Digit9) {
        Some(RuntimeUploadKind::CrashReport)
    } else {
        None
    }
}

fn runtime_data_control_action_from_keyboard(
    keyboard: &ButtonInput<KeyCode>,
) -> Option<RuntimeDataControlAction> {
    if keyboard.just_pressed(KeyCode::KeyE) {
        Some(RuntimeDataControlAction::ExportSave)
    } else if keyboard.just_pressed(KeyCode::KeyX) {
        Some(RuntimeDataControlAction::DeleteSave)
    } else if keyboard.just_pressed(KeyCode::KeyL) {
        Some(RuntimeDataControlAction::ExportLocalData)
    } else if keyboard.just_pressed(KeyCode::KeyK) {
        Some(RuntimeDataControlAction::DeleteLocalData)
    } else {
        None
    }
}

fn runtime_settings_action_from_keyboard(
    keyboard: &ButtonInput<KeyCode>,
) -> Option<RuntimeSettingsAction> {
    privacy_toggle_from_keyboard(keyboard)
        .map(RuntimeSettingsAction::ToggleUpload)
        .or_else(|| {
            runtime_data_control_action_from_keyboard(keyboard)
                .map(RuntimeSettingsAction::DataControl)
        })
}

fn runtime_overview_view_from_pointer(
    mouse_buttons: &ButtonInput<MouseButton>,
    cursor_position: Option<Vec2>,
    window_size: Vec2,
) -> Option<RuntimeMetaPanelView> {
    if mouse_buttons.just_pressed(MouseButton::Left) {
        runtime_overview_view_from_pointer_zone(cursor_position?, window_size)
    } else {
        None
    }
}

fn runtime_meta_panel_tab_view_from_pointer(
    mouse_buttons: &ButtonInput<MouseButton>,
    cursor_position: Option<Vec2>,
    window_size: Vec2,
) -> Option<RuntimeMetaPanelView> {
    if mouse_buttons.just_pressed(MouseButton::Left) {
        runtime_meta_panel_tab_view_from_pointer_zone(cursor_position?, window_size)
    } else {
        None
    }
}

fn runtime_meta_panel_tab_view_from_pointer_zone(
    cursor_position: Vec2,
    window_size: Vec2,
) -> Option<RuntimeMetaPanelView> {
    if window_size.x <= 0.0 || window_size.y <= 0.0 {
        return None;
    }
    let panel_right = (window_size.x - META_PANEL_RIGHT_MARGIN).max(0.0);
    let panel_left = (panel_right - META_PANEL_WIDTH).max(0.0);
    let panel_width = (panel_right - panel_left).max(1.0);
    let control_bottom = (window_size.y - META_PANEL_TAB_CONTROL_HEIGHT).max(0.0);
    let in_panel_x = cursor_position.x >= panel_left && cursor_position.x <= panel_right;
    let in_control_y = cursor_position.y >= control_bottom && cursor_position.y <= window_size.y;
    if !in_panel_x || !in_control_y {
        return None;
    }

    let normalized_x = ((cursor_position.x - panel_left) / panel_width).clamp(0.0, 0.999);
    let zone = (normalized_x * META_PANEL_TAB_CONTROL_ZONE_COUNT as f32).floor() as usize;
    match zone {
        0 => Some(RuntimeMetaPanelView::Overview),
        1 => Some(RuntimeMetaPanelView::Chapters),
        2 => Some(RuntimeMetaPanelView::Codex),
        3 => Some(RuntimeMetaPanelView::Settings),
        _ => Some(RuntimeMetaPanelView::Loadout),
    }
}

fn runtime_overview_view_from_pointer_zone(
    cursor_position: Vec2,
    window_size: Vec2,
) -> Option<RuntimeMetaPanelView> {
    if window_size.x <= 0.0 || window_size.y <= 0.0 {
        return None;
    }
    let panel_right = (window_size.x - META_PANEL_RIGHT_MARGIN).max(0.0);
    let panel_left = (panel_right - META_PANEL_WIDTH).max(0.0);
    let panel_width = (panel_right - panel_left).max(1.0);
    let in_panel_x = cursor_position.x >= panel_left && cursor_position.x <= panel_right;
    let in_control_y =
        cursor_position.y >= 0.0 && cursor_position.y <= OVERVIEW_POINTER_CONTROL_HEIGHT;
    if !in_panel_x || !in_control_y {
        return None;
    }

    let normalized_x = ((cursor_position.x - panel_left) / panel_width).clamp(0.0, 0.999);
    let zone = (normalized_x * OVERVIEW_POINTER_CONTROL_ZONE_COUNT as f32).floor() as usize;
    match zone {
        0 => Some(RuntimeMetaPanelView::Chapters),
        1 => Some(RuntimeMetaPanelView::Codex),
        2 => Some(RuntimeMetaPanelView::Settings),
        _ => Some(RuntimeMetaPanelView::Loadout),
    }
}

fn runtime_settings_action_from_pointer(
    mouse_buttons: &ButtonInput<MouseButton>,
    cursor_position: Option<Vec2>,
    window_size: Vec2,
) -> Option<RuntimeSettingsAction> {
    if mouse_buttons.just_pressed(MouseButton::Left) {
        runtime_settings_action_from_pointer_zone(cursor_position?, window_size)
    } else {
        None
    }
}

fn runtime_settings_action_from_pointer_zone(
    cursor_position: Vec2,
    window_size: Vec2,
) -> Option<RuntimeSettingsAction> {
    if window_size.x <= 0.0 || window_size.y <= 0.0 {
        return None;
    }
    let panel_right = (window_size.x - META_PANEL_RIGHT_MARGIN).max(0.0);
    let panel_left = (panel_right - META_PANEL_WIDTH).max(0.0);
    let panel_width = (panel_right - panel_left).max(1.0);
    let in_panel_x = cursor_position.x >= panel_left && cursor_position.x <= panel_right;
    let in_control_y =
        cursor_position.y >= 0.0 && cursor_position.y <= SETTINGS_POINTER_CONTROL_HEIGHT;
    if !in_panel_x || !in_control_y {
        return None;
    }

    let normalized_x = ((cursor_position.x - panel_left) / panel_width).clamp(0.0, 0.999);
    let zone = (normalized_x * SETTINGS_POINTER_CONTROL_ZONE_COUNT as f32).floor() as usize;
    match zone {
        0 => Some(RuntimeSettingsAction::ToggleUpload(
            RuntimeUploadKind::Telemetry,
        )),
        1 => Some(RuntimeSettingsAction::ToggleUpload(
            RuntimeUploadKind::RawReplay,
        )),
        2 => Some(RuntimeSettingsAction::ToggleUpload(
            RuntimeUploadKind::CrashReport,
        )),
        3 => Some(RuntimeSettingsAction::DataControl(
            RuntimeDataControlAction::ExportSave,
        )),
        4 => Some(RuntimeSettingsAction::DataControl(
            RuntimeDataControlAction::DeleteSave,
        )),
        5 => Some(RuntimeSettingsAction::DataControl(
            RuntimeDataControlAction::ExportLocalData,
        )),
        _ => Some(RuntimeSettingsAction::DataControl(
            RuntimeDataControlAction::DeleteLocalData,
        )),
    }
}

fn runtime_loadout_action_from_keyboard(
    keyboard: &ButtonInput<KeyCode>,
) -> Option<RuntimeLoadoutAction> {
    if keyboard.just_pressed(KeyCode::KeyC) {
        Some(RuntimeLoadoutAction::NextCharacter)
    } else if keyboard.just_pressed(KeyCode::KeyM) {
        Some(RuntimeLoadoutAction::NextMap)
    } else {
        None
    }
}

fn runtime_loadout_action_from_gamepad(
    gamepad_buttons: &ButtonInput<GamepadButton>,
) -> Option<RuntimeLoadoutAction> {
    if gamepad_button_type_just_pressed(
        gamepad_buttons,
        &[GamepadButtonType::DPadLeft, GamepadButtonType::LeftTrigger],
    ) {
        Some(RuntimeLoadoutAction::NextCharacter)
    } else if gamepad_button_type_just_pressed(
        gamepad_buttons,
        &[
            GamepadButtonType::DPadRight,
            GamepadButtonType::RightTrigger,
        ],
    ) {
        Some(RuntimeLoadoutAction::NextMap)
    } else {
        None
    }
}

fn runtime_loadout_action_from_pointer(
    mouse_buttons: &ButtonInput<MouseButton>,
    cursor_position: Option<Vec2>,
    window_size: Vec2,
) -> Option<RuntimeLoadoutAction> {
    if mouse_buttons.just_pressed(MouseButton::Left) {
        runtime_loadout_action_from_pointer_zone(cursor_position?, window_size)
    } else {
        None
    }
}

fn runtime_loadout_action_from_pointer_zone(
    cursor_position: Vec2,
    window_size: Vec2,
) -> Option<RuntimeLoadoutAction> {
    if window_size.x <= 0.0 || window_size.y <= 0.0 {
        return None;
    }
    let panel_right = (window_size.x - META_PANEL_RIGHT_MARGIN).max(0.0);
    let panel_left = (panel_right - META_PANEL_WIDTH).max(0.0);
    let panel_width = (panel_right - panel_left).max(1.0);
    let in_panel_x = cursor_position.x >= panel_left && cursor_position.x <= panel_right;
    let in_control_y =
        cursor_position.y >= 0.0 && cursor_position.y <= LOADOUT_POINTER_CONTROL_HEIGHT;
    if !in_panel_x || !in_control_y {
        return None;
    }

    let normalized_x = ((cursor_position.x - panel_left) / panel_width).clamp(0.0, 0.999);
    let zone = (normalized_x * LOADOUT_POINTER_CONTROL_ZONE_COUNT as f32).floor() as usize;
    match zone {
        0 => Some(RuntimeLoadoutAction::NextCharacter),
        _ => Some(RuntimeLoadoutAction::NextMap),
    }
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
    let map_style = map_visual_style(&snapshot.map.map_id);
    commands.spawn((
        SpriteBundle {
            texture: sprites.map_tile.clone(),
            sprite: Sprite {
                color: map_style.tile_tint,
                custom_size: Some(Vec2::new(snapshot.map.width, snapshot.map.height)),
                ..default()
            },
            transform: Transform::from_xyz(0.0, 0.0, MAP_Z),
            ..default()
        },
        RuntimeVisual,
    ));
    spawn_map_borders(&mut commands, snapshot, map_style.border_color);
    spawn_active_hazards(&mut commands, snapshot, map_style.hazard_color);

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

fn spawn_map_borders(commands: &mut Commands, snapshot: &RunSnapshot, color: Color) {
    let thickness = 10.0;
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

fn spawn_active_hazards(commands: &mut Commands, snapshot: &RunSnapshot, color: Color) {
    for hazard in &snapshot.active_hazards {
        let size = (hazard.radius * 2.0).max(24.0);
        commands.spawn((
            SpriteBundle {
                sprite: Sprite {
                    color,
                    custom_size: Some(Vec2::splat(size)),
                    ..default()
                },
                transform: Transform::from_xyz(
                    hazard.position.x,
                    hazard.position.y,
                    EFFECT_Z - 2.0,
                ),
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

fn map_visual_style(map_id: &str) -> RuntimeMapVisualStyle {
    match map_id {
        "soda-creek" => RuntimeMapVisualStyle {
            display_name: "汽水溪谷",
            tile_tint: Color::srgb(0.70, 0.93, 1.0),
            border_color: Color::srgb(0.10, 0.44, 0.64),
            hazard_color: Color::srgba(0.18, 0.78, 1.0, 0.34),
        },
        "cotton-cloud-pasture" => RuntimeMapVisualStyle {
            display_name: "棉花云牧场",
            tile_tint: Color::srgb(0.96, 0.91, 1.0),
            border_color: Color::srgb(0.48, 0.36, 0.70),
            hazard_color: Color::srgba(0.94, 0.80, 1.0, 0.38),
        },
        "caramel-workshop" => RuntimeMapVisualStyle {
            display_name: "焦糖工坊",
            tile_tint: Color::srgb(0.98, 0.73, 0.46),
            border_color: Color::srgb(0.50, 0.22, 0.08),
            hazard_color: Color::srgba(0.86, 0.34, 0.05, 0.42),
        },
        "jelly-platform" => RuntimeMapVisualStyle {
            display_name: "果冻月台",
            tile_tint: Color::srgb(0.72, 0.97, 0.86),
            border_color: Color::srgb(0.08, 0.46, 0.40),
            hazard_color: Color::srgba(0.28, 0.95, 0.70, 0.36),
        },
        "cracked-star-jar" => RuntimeMapVisualStyle {
            display_name: "裂星糖罐",
            tile_tint: Color::srgb(0.84, 0.82, 1.0),
            border_color: Color::srgb(0.28, 0.22, 0.58),
            hazard_color: Color::srgba(0.80, 0.38, 1.0, 0.40),
        },
        _ => RuntimeMapVisualStyle {
            display_name: "糖霜草地",
            tile_tint: Color::srgb(0.96, 0.98, 0.78),
            border_color: Color::srgb(0.49, 0.36, 0.20),
            hazard_color: Color::srgba(0.92, 0.50, 0.18, 0.34),
        },
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

fn format_boss_status(boss: Option<&BossSnapshot>, content: &ContentPack) -> String {
    let Some(boss) = boss else {
        return "Boss 未出现".to_string();
    };

    let health = boss.health.max(0.0);
    let max_health = boss.max_health.max(0.0);
    let health_ratio = if max_health > 0.0 {
        (health / max_health * 100.0).clamp(0.0, 100.0)
    } else {
        0.0
    };
    format!(
        "Boss {} ({})  HP {:.0}/{:.0}  {:.0}%",
        runtime_boss_label(content, &boss.boss_id),
        boss.boss_id,
        health,
        max_health,
        health_ratio,
    )
}

fn format_build_status(build: &BuildSnapshot, content: &ContentPack) -> String {
    let weapons = format_build_items(&build.weapons, 3, |id| runtime_weapon_label(content, id));
    let passives = format_build_items(&build.passives, 2, |id| runtime_passive_label(content, id));
    let evolutions = format_build_items(&build.evolutions, 2, |id| {
        runtime_evolution_label(content, id)
    });
    let evolution_paths = format_evolution_path_items(&build.open_evolution_paths, 2, |id| {
        runtime_evolution_label(content, id)
    });
    let tags = format_tag_items(&build.tags, 4);
    format!(
        "Build 武器 {weapons}  被动 {passives}  进化 {evolutions}  进化线 {evolution_paths}  标签 {tags}"
    )
}

fn format_enemy_swarm_status(enemies: &[EnemySnapshot], content: &ContentPack) -> String {
    if enemies.is_empty() {
        return "敌群 无".to_string();
    }

    let mut counts = BTreeMap::<String, usize>::new();
    let mut boss_or_elite_count = 0usize;
    let mut max_threat: f32 = 0.0;
    for enemy in enemies {
        *counts.entry(enemy.enemy_id.clone()).or_default() += 1;
        if enemy.is_boss || enemy.is_elite {
            boss_or_elite_count += 1;
        }
        max_threat = max_threat.max(enemy.threat.max(0.0));
    }

    let mut entries = counts.into_iter().collect::<Vec<_>>();
    entries.sort_by(|left, right| right.1.cmp(&left.1).then_with(|| left.0.cmp(&right.0)));
    let mut visible = entries
        .iter()
        .take(3)
        .map(|(enemy_id, count)| format!("{} x{}", runtime_enemy_label(content, enemy_id), count))
        .collect::<Vec<_>>();
    if entries.len() > visible.len() {
        visible.push(format!("+{} 类", entries.len() - visible.len()));
    }

    let special = if boss_or_elite_count > 0 {
        format!("  精英/Boss {}", boss_or_elite_count)
    } else {
        String::new()
    };
    format!(
        "敌群 {}  可见 {}  最高威胁 {:.1}{}",
        visible.join(", "),
        enemies.len(),
        max_threat,
        special,
    )
}

fn format_hazard_status(
    hazards: &[HazardSnapshot],
    status_effects: &[StatusEffectSnapshot],
) -> String {
    if hazards.is_empty() && status_effects.is_empty() {
        return "地图危险 安全".to_string();
    }

    let hazard_text = if hazards.is_empty() {
        "危险区 无".to_string()
    } else {
        let max_damage = hazards
            .iter()
            .map(|hazard| hazard.damage_per_second.max(0.0))
            .fold(0.0, f32::max);
        let min_slow = hazards
            .iter()
            .map(|hazard| hazard.slow_multiplier.clamp(0.0, 1.0))
            .fold(1.0, f32::min);
        let max_remaining = hazards
            .iter()
            .map(|hazard| hazard.remaining_seconds.max(0.0))
            .fold(0.0, f32::max);
        format!(
            "危险区 {}  最高伤害 {:.0}/s  最强减速 移速 {:.0}%  最长 {:.1}s",
            hazards.len(),
            max_damage,
            min_slow * 100.0,
            max_remaining,
        )
    };
    let status_text = format_player_status_effects(status_effects);
    format!("地图危险 {hazard_text}  状态 {status_text}")
}

fn format_player_status_effects(status_effects: &[StatusEffectSnapshot]) -> String {
    let active = status_effects
        .iter()
        .filter(|effect| effect.remaining_seconds > 0.0)
        .take(3)
        .map(|effect| {
            format!(
                "{} 移速 {:.0}% {:.1}s",
                runtime_status_effect_label(&effect.kind),
                effect.multiplier.clamp(0.0, 1.0) * 100.0,
                effect.remaining_seconds,
            )
        })
        .collect::<Vec<_>>();
    if active.is_empty() {
        "无".to_string()
    } else {
        active.join(", ")
    }
}

fn runtime_status_effect_label(kind: &str) -> String {
    match kind {
        "slow" => "减速".to_string(),
        other => other.replace('-', " "),
    }
}

fn format_build_items<F>(items: &[BuildItemSnapshot], limit: usize, label: F) -> String
where
    F: Fn(&str) -> String,
{
    if items.is_empty() {
        return "无".to_string();
    }

    let mut visible = items
        .iter()
        .take(limit)
        .map(|item| format!("{} Lv.{}", label(&item.id), item.level))
        .collect::<Vec<_>>();
    if items.len() > limit {
        visible.push(format!("+{} 项", items.len() - limit));
    }
    visible.join(", ")
}

fn format_evolution_path_items<F>(items: &[String], limit: usize, label: F) -> String
where
    F: Fn(&str) -> String,
{
    if items.is_empty() {
        return "无".to_string();
    }

    let mut visible = items
        .iter()
        .take(limit)
        .map(|id| format!("{} ({id})", label(id)))
        .collect::<Vec<_>>();
    if items.len() > limit {
        visible.push(format!("+{} 项", items.len() - limit));
    }
    visible.join(", ")
}

fn format_tag_items(tags: &[String], limit: usize) -> String {
    if tags.is_empty() {
        return "无".to_string();
    }

    let mut visible = tags
        .iter()
        .take(limit)
        .map(|tag| runtime_tag_label(tag))
        .collect::<Vec<_>>();
    if tags.len() > limit {
        visible.push(format!("+{} 项", tags.len() - limit));
    }
    visible.join(", ")
}

fn format_terminal_overlay(terminal: &TerminalState) -> String {
    format!(
        "{}  {:.1}s  Lv {}  击杀 {}\n原因 {}\n按 R 重新巡逻",
        terminal_kind_label(terminal.kind),
        terminal.time_seconds,
        terminal.final_level,
        terminal.kills,
        format_terminal_reason(&terminal.reason),
    )
}

fn update_hud(
    state: Res<RuntimeState>,
    mut hud_query: Query<&mut Text, With<HudText>>,
    mut upgrade_query: Query<&mut Text, (With<UpgradeText>, Without<HudText>)>,
    mut terminal_query: Query<&mut Text, TerminalTextFilter>,
    mut meta_query: Query<&mut Text, MetaTextFilter>,
) {
    let snapshot = &state.latest_snapshot;
    if let Ok(mut text) = hud_query.get_single_mut() {
        let mode = if state.paused { "Paused" } else { "Playing" };
        let map_style = map_visual_style(&snapshot.map.map_id);
        let boss_status = format_boss_status(snapshot.boss.as_ref(), &state.content);
        let build_status = format_build_status(&snapshot.build, &state.content);
        let enemy_status = format_enemy_swarm_status(&snapshot.visible_enemies, &state.content);
        let hazard_status =
            format_hazard_status(&snapshot.active_hazards, &snapshot.player.status_effects);
        text.sections[0].value = format!(
            "Run {}  {}  Time {:05.1}s  HP {:03.0}/{:03.0}  Lv {}  XP {:.0}/{:.0}  Kills {}\nMap {} ({})\n{}\n{}\n{}\n{}\n{}  [{}]\nControls: WASD/Arrows/LeftStick/DPad move | 1/2/3 upgrade | P pause | R restart | F1-F5 station",
            state.run_number,
            mode,
            snapshot.time_seconds,
            snapshot.player.health.max(0.0),
            snapshot.player.max_health,
            snapshot.player.level,
            snapshot.player.xp,
            snapshot.player.xp_to_next_level,
            snapshot.metrics_partial.kills,
            map_style.display_name,
            snapshot.map.map_id,
            boss_status,
            enemy_status,
            hazard_status,
            build_status,
            state.last_event,
            state.last_event_kind.label(),
        );
    }

    if let Ok(mut text) = upgrade_query.get_single_mut() {
        text.sections[0].value = if snapshot.upgrade_options.is_empty() {
            String::new()
        } else {
            format!(
                "升级选择 - 按 1/2/3，点底部三段，或手柄下/右/上按钮\n{}",
                format_upgrade_options(&snapshot.upgrade_options)
            )
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
                .map(format_terminal_overlay)
                .unwrap_or_default()
        };
    }

    if let Ok(mut text) = meta_query.get_single_mut() {
        text.sections[0].value = render_meta_progress_panel(
            &state.meta_progress,
            state.last_meta_settlement.as_ref(),
            state.meta_panel_view,
            RuntimeMetaPanelRenderContext {
                privacy_settings: &state.privacy_settings,
                runtime_settings_file: state.runtime_settings_file.as_deref(),
                story_codex_ui_candidate: state.story_codex_ui_candidate.as_ref(),
                asset_runtime_candidate: state.asset_runtime_candidate.as_ref(),
                content: &state.content,
                config: &state.config,
                base_ui_state: &state.base_ui_state,
                codex_selected_index: state.codex_selected_index,
            },
        );
    }
}

fn apply_runtime_feedback(state: &mut RuntimeState, events: &[GameEvent], snapshot: &RunSnapshot) {
    state.capture.event_counts.observe(events);
    let feedback = feedback_for_events(events, &state.content);
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

fn feedback_for_events(events: &[GameEvent], content: &ContentPack) -> RuntimeFeedback {
    RuntimeFeedback {
        message: describe_events(events, content),
        kind: event_kind_for_events(events),
        sounds: sounds_for_events(events),
    }
}

fn describe_events(events: &[GameEvent], content: &ContentPack) -> String {
    events
        .iter()
        .rev()
        .find_map(|event| describe_event(event, content))
        .unwrap_or_else(|| "糖果风暴推进中".to_string())
}

fn event_kind_for_events(events: &[GameEvent]) -> RuntimeEventKind {
    events
        .iter()
        .rev()
        .find_map(|event| match event {
            GameEvent::RunEnded { .. } => Some(RuntimeEventKind::Terminal),
            GameEvent::PlayerDamaged { .. } => Some(RuntimeEventKind::Damage),
            GameEvent::BossPhaseChanged { .. } | GameEvent::BossAbilityUsed { .. } => {
                Some(RuntimeEventKind::Combat)
            }
            GameEvent::UpgradeOffered { .. }
            | GameEvent::UpgradeChosen { .. }
            | GameEvent::LevelUp { .. } => Some(RuntimeEventKind::Upgrade),
            GameEvent::XpCollected { .. } => Some(RuntimeEventKind::Pickup),
            GameEvent::ContentEventTriggered { .. } => Some(RuntimeEventKind::System),
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
            GameEvent::BossPhaseChanged { .. } | GameEvent::BossAbilityUsed { .. } => {
                Some(RuntimeSound::Terminal)
            }
            GameEvent::UpgradeOffered { .. }
            | GameEvent::UpgradeChosen { .. }
            | GameEvent::LevelUp { .. } => Some(RuntimeSound::Upgrade),
            GameEvent::XpCollected { .. } => Some(RuntimeSound::Pickup),
            GameEvent::ContentEventTriggered { .. } => Some(RuntimeSound::System),
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

fn describe_event(event: &GameEvent, content: &ContentPack) -> Option<String> {
    match event {
        GameEvent::EnemySpawned { enemy_id, .. } => Some(format!(
            "出现 {} ({enemy_id})",
            runtime_enemy_label(content, enemy_id)
        )),
        GameEvent::BossSpawned { boss_id, .. } => Some(format!(
            "Boss 出现 {} ({boss_id})",
            runtime_boss_label(content, boss_id)
        )),
        GameEvent::BossPhaseChanged {
            boss_id,
            phase_index,
            ..
        } => Some(format!(
            "Boss {} 进入第 {} 阶段",
            runtime_boss_label(content, boss_id),
            phase_index + 1
        )),
        GameEvent::BossAbilityUsed {
            boss_id,
            ability_id,
            ..
        } => Some(format!(
            "Boss {} 使用 {}",
            runtime_boss_label(content, boss_id),
            runtime_boss_ability_label(ability_id)
        )),
        GameEvent::WeaponFired {
            weapon_id,
            projectile_count,
        } => Some(format!(
            "发射 {} x{projectile_count}",
            runtime_weapon_label(content, weapon_id)
        )),
        GameEvent::EnemyKilled { enemy_id, .. } => {
            Some(format!("击败 {}", runtime_enemy_label(content, enemy_id)))
        }
        GameEvent::XpCollected { value, .. } => Some(format!("糖晶 +{value:.0}")),
        GameEvent::LevelUp { level } => Some(format!("升到 Lv.{level}")),
        GameEvent::UpgradeOffered { .. } => Some("出现升级选择".to_string()),
        GameEvent::UpgradeChosen { option_id } => Some(format!("选择 {option_id}")),
        GameEvent::PlayerDamaged { amount } => Some(format!("受伤 {amount:.1}")),
        GameEvent::ContentEventTriggered { event_id } => Some(format!(
            "事件 {} ({event_id})",
            runtime_event_label(content, event_id)
        )),
        GameEvent::RunEnded { terminal } => {
            Some(format!("本局结束 {}", terminal_kind_label(terminal.kind)))
        }
        GameEvent::EnemyHit { .. } | GameEvent::XpDropped { .. } => None,
    }
}

fn effects_for_events(events: &[GameEvent], snapshot: &RunSnapshot) -> Vec<RuntimeEffect> {
    let mut effects = Vec::new();
    for event in events {
        let effect = match event {
            GameEvent::EnemyHit {
                entity_id, damage, ..
            } => enemy_position(snapshot, *entity_id).map(|position| {
                RuntimeEffect::new(RuntimeEffectKind::ProjectileHit, position, *damage, 0.16)
            }),
            GameEvent::XpDropped { entity_id, value } => {
                pickup_position(snapshot, *entity_id).map(|position| {
                    RuntimeEffect::new(RuntimeEffectKind::XpDrop, position, *value, 0.42)
                })
            }
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
            GameEvent::BossSpawned { entity_id, .. } => {
                boss_position(snapshot, *entity_id).map(|position| {
                    RuntimeEffect::new(RuntimeEffectKind::BossSpawn, position, 1.0, 0.72)
                })
            }
            GameEvent::BossPhaseChanged { entity_id, .. }
            | GameEvent::BossAbilityUsed { entity_id, .. } => boss_position(snapshot, *entity_id)
                .map(|position| {
                    RuntimeEffect::new(RuntimeEffectKind::BossAbility, position, 1.0, 0.48)
                }),
            GameEvent::EnemySpawned { .. }
            | GameEvent::WeaponFired { .. }
            | GameEvent::EnemyKilled { .. }
            | GameEvent::ContentEventTriggered { .. }
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
        RuntimeEffectKind::BossAbility => (
            Color::srgba(0.86, 0.26, 1.0, 0.40 * fade),
            120.0 + growth * 64.0,
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
    state.last_meta_settlement = None;
    state.settled_run_number = None;
}

fn select_next_runtime_character(state: &mut RuntimeState) -> std::io::Result<String> {
    let candidates = runtime_unlocked_character_ids(&state.meta_progress, &state.content);
    let next_id =
        next_runtime_selection_id(&candidates, &state.config.character_id).ok_or_else(|| {
            std::io::Error::new(
                std::io::ErrorKind::InvalidInput,
                "no unlocked Runtime characters available",
            )
        })?;
    state.config.character_id = next_id.clone();
    state.config.starting_loadout = runtime_character_starting_loadout(&state.content, &next_id);
    state.base_ui_state.last_selected_character_id = next_id.clone();
    reset_runtime_run(state);
    persist_runtime_save_if_configured(state)?;
    let label = runtime_character_label(&state.content, &next_id);
    Ok(format!("selected character {label} ({next_id})"))
}

fn select_next_runtime_map(state: &mut RuntimeState) -> std::io::Result<String> {
    let candidates = runtime_unlocked_map_ids(&state.meta_progress, &state.content);
    let next_id =
        next_runtime_selection_id(&candidates, &state.config.map_id).ok_or_else(|| {
            std::io::Error::new(
                std::io::ErrorKind::InvalidInput,
                "no unlocked Runtime maps available",
            )
        })?;
    state.config.map_id = next_id.clone();
    state.base_ui_state.last_selected_map_id = next_id.clone();
    state.base_ui_state.last_selected_chapter_id = next_id.clone();
    reset_runtime_run(state);
    persist_runtime_save_if_configured(state)?;
    let label = runtime_map_label(&state.content, &next_id);
    Ok(format!("selected map {label} ({next_id})"))
}

fn runtime_chapter_action_from_keyboard(
    keyboard: &ButtonInput<KeyCode>,
) -> Option<RuntimeChapterAction> {
    if keyboard.just_pressed(KeyCode::KeyQ) {
        Some(RuntimeChapterAction::Previous)
    } else if keyboard.just_pressed(KeyCode::KeyE) {
        Some(RuntimeChapterAction::Next)
    } else if keyboard.just_pressed(KeyCode::KeyG) {
        Some(RuntimeChapterAction::StartSelectedChapter)
    } else {
        None
    }
}

fn runtime_chapter_action_from_gamepad(
    gamepad_buttons: &ButtonInput<GamepadButton>,
) -> Option<RuntimeChapterAction> {
    if gamepad_button_type_just_pressed(
        gamepad_buttons,
        &[GamepadButtonType::DPadLeft, GamepadButtonType::LeftTrigger],
    ) {
        Some(RuntimeChapterAction::Previous)
    } else if gamepad_button_type_just_pressed(
        gamepad_buttons,
        &[
            GamepadButtonType::DPadRight,
            GamepadButtonType::RightTrigger,
        ],
    ) {
        Some(RuntimeChapterAction::Next)
    } else if gamepad_button_type_just_pressed(gamepad_buttons, &[GamepadButtonType::South]) {
        Some(RuntimeChapterAction::StartSelectedChapter)
    } else {
        None
    }
}

fn runtime_chapter_action_from_pointer(
    mouse_buttons: &ButtonInput<MouseButton>,
    cursor_position: Option<Vec2>,
    window_size: Vec2,
) -> Option<RuntimeChapterAction> {
    if mouse_buttons.just_pressed(MouseButton::Left) {
        runtime_chapter_action_from_pointer_zone(cursor_position?, window_size)
    } else {
        None
    }
}

fn runtime_chapter_action_from_pointer_zone(
    cursor_position: Vec2,
    window_size: Vec2,
) -> Option<RuntimeChapterAction> {
    if window_size.x <= 0.0 || window_size.y <= 0.0 {
        return None;
    }
    let panel_right = (window_size.x - META_PANEL_RIGHT_MARGIN).max(0.0);
    let panel_left = (panel_right - META_PANEL_WIDTH).max(0.0);
    let panel_width = (panel_right - panel_left).max(1.0);
    let in_panel_x = cursor_position.x >= panel_left && cursor_position.x <= panel_right;
    let in_control_y =
        cursor_position.y >= 0.0 && cursor_position.y <= CHAPTER_POINTER_CONTROL_HEIGHT;
    if !in_panel_x || !in_control_y {
        return None;
    }

    let normalized_x = ((cursor_position.x - panel_left) / panel_width).clamp(0.0, 0.999);
    let zone = (normalized_x * CHAPTER_POINTER_CONTROL_ZONE_COUNT as f32).floor() as usize;
    match zone {
        0 => Some(RuntimeChapterAction::Previous),
        1 => Some(RuntimeChapterAction::Next),
        _ => Some(RuntimeChapterAction::StartSelectedChapter),
    }
}

fn apply_runtime_chapter_action(
    state: &mut RuntimeState,
    action: RuntimeChapterAction,
) -> std::io::Result<String> {
    match action {
        RuntimeChapterAction::Previous | RuntimeChapterAction::Next => {
            let candidates = runtime_chapter_ids(&state.meta_progress);
            let current = runtime_selected_chapter_id(&state.meta_progress, &state.base_ui_state)
                .unwrap_or_default();
            let current_index = candidates
                .iter()
                .position(|chapter_id| chapter_id == &current)
                .unwrap_or(0);
            let next_index = match action {
                RuntimeChapterAction::Previous => {
                    if current_index == 0 {
                        candidates.len().saturating_sub(1)
                    } else {
                        current_index - 1
                    }
                }
                RuntimeChapterAction::Next => {
                    if candidates.is_empty() {
                        0
                    } else {
                        (current_index + 1) % candidates.len()
                    }
                }
                _ => unreachable!(),
            };
            let Some(next_id) = candidates.get(next_index).cloned() else {
                return Err(std::io::Error::new(
                    std::io::ErrorKind::InvalidInput,
                    "no Runtime chapters available",
                ));
            };
            state.base_ui_state.last_selected_chapter_id = next_id.clone();
            persist_runtime_save_if_configured(state)?;
            Ok(format!("selected chapter {next_id}"))
        }
        RuntimeChapterAction::StartSelectedChapter => {
            let selected_id =
                runtime_selected_chapter_id(&state.meta_progress, &state.base_ui_state)
                    .ok_or_else(|| {
                        std::io::Error::new(
                            std::io::ErrorKind::InvalidInput,
                            "no Runtime chapter selected",
                        )
                    })?;
            let chapter = state
                .meta_progress
                .chapters
                .get(&selected_id)
                .ok_or_else(|| {
                    std::io::Error::new(
                        std::io::ErrorKind::InvalidInput,
                        "selected Runtime chapter is missing",
                    )
                })?;
            if !chapter.unlocked {
                return Err(std::io::Error::new(
                    std::io::ErrorKind::PermissionDenied,
                    "selected Runtime chapter is locked",
                ));
            }
            state.config.map_id = chapter.map_id.clone();
            state.base_ui_state.last_selected_map_id = chapter.map_id.clone();
            state.base_ui_state.last_selected_chapter_id = chapter.chapter_id.clone();
            reset_runtime_run(state);
            persist_runtime_save_if_configured(state)?;
            let label = runtime_map_label(&state.content, &state.config.map_id);
            Ok(format!("started chapter {selected_id} on {label}"))
        }
    }
}

fn settle_runtime_meta_if_needed(state: &mut RuntimeState) {
    if state.settled_run_number == Some(state.run_number) {
        return;
    }

    let metrics = state.core.metrics();
    if metrics.terminal.is_none() {
        return;
    }

    let run_id = format!(
        "runtime_run_{}_seed_{}",
        state.run_number, state.config.seed
    );
    let summary = MetaRunSummary::from_metrics(run_id, &state.config, &metrics);
    let report = state.meta_progress.apply_run_summary(&summary);
    state.last_meta_settlement = Some(report);
    state.settled_run_number = Some(state.run_number);
    if let Err(error) = persist_runtime_save_if_configured(state) {
        state.last_event = format!("save failed: {error}");
        state.last_event_kind = RuntimeEventKind::System;
    }
}

fn render_meta_progress_panel(
    progress: &MetaProgress,
    settlement: Option<&MetaSettlementReport>,
    view: RuntimeMetaPanelView,
    context: RuntimeMetaPanelRenderContext<'_>,
) -> String {
    match view {
        RuntimeMetaPanelView::Overview => {
            render_meta_overview_panel(progress, settlement, context.asset_runtime_candidate)
        }
        RuntimeMetaPanelView::Chapters => {
            render_meta_chapter_panel(progress, settlement, context.content, context.base_ui_state)
        }
        RuntimeMetaPanelView::Codex => render_meta_codex_panel(
            progress,
            settlement,
            context.story_codex_ui_candidate,
            context.content,
            &context.base_ui_state.codex_view,
            context.codex_selected_index,
        ),
        RuntimeMetaPanelView::Settings => {
            render_meta_settings_panel(context.privacy_settings, context.runtime_settings_file)
        }
        RuntimeMetaPanelView::Loadout => {
            render_meta_loadout_panel(progress, context.content, context.config)
        }
    }
}

fn render_meta_overview_panel(
    progress: &MetaProgress,
    settlement: Option<&MetaSettlementReport>,
    asset_runtime_candidate: Option<&RuntimeAssetCandidateManifest>,
) -> String {
    let discovered = meta_codex_discovered_count(progress);
    let completed_goals = meta_completed_goal_count(progress);
    let unlocked_content = meta_unlocked_content_count(progress);
    let maps = format_string_set(&progress.unlocks.maps, 3);

    let mut output = format!(
        "{}\n{}\n糖晶碎片 {}  星片 {}  风暴糖粒 {}\n章节目标 {}  图鉴发现 {}  已解锁 {}\n地图 {}\n完成巡逻 {}  最佳 {:.0}s\n",
        META_PANEL_HEADER,
        META_PANEL_TAB_CLICK_HINT,
        progress.resources.candy_crystal_shards,
        progress.resources.star_shards,
        progress.resources.storm_grains,
        completed_goals,
        discovered,
        unlocked_content,
        maps,
        progress.completed_runs,
        progress.best_survival_seconds,
    );

    if let Some(report) = settlement {
        let summary = &report.run_summary;
        output.push_str(&format!(
            "\n局后结算\n{}  存活 {}  终局 {}\n等级 {}  击杀 {}  XP {:.0}\n输出 {:.0}  Boss {:.0}  受伤 {:.1} ({})\n最终构筑 武器 {}  被动 {}\n资源 +{} 糖晶碎片  +{} 星片  +{} 风暴糖粒\n章节目标 {}\n新解锁 {}\n图鉴更新 {}\n下一步 {}",
            format_settlement_outcome(summary),
            format_settlement_duration(summary.duration_seconds),
            format_terminal_reason(&summary.terminal_reason),
            summary.level,
            summary.kills,
            summary.xp_collected,
            summary.damage_dealt_by_weapon,
            summary.boss_damage,
            summary.damage_taken,
            format_damage_sources(&summary.damage_taken_by_source, 2),
            format_weapon_levels(&summary.weapon_levels, 4),
            format_passive_set(&summary.passives_used, 3),
            report.resources_gained.candy_crystal_shards,
            report.resources_gained.star_shards,
            report.resources_gained.storm_grains,
            format_string_slice(&report.completed_goals, 2),
            format_meta_unlocks(report, 2),
            format_string_slice(&report.codex_updates, 2),
            format_settlement_next_step(report),
        ));
    } else {
        output.push_str("\n巡逻中：结算会在本局结束后更新");
    }
    if let Some(candidate) = asset_runtime_candidate {
        output.push_str(&format!(
            "\n\n素材 Runtime 候选: {}\n素材 {}  类型 {}  状态 asset_candidate 待预览\n仅显示候选状态，不替换正式 Runtime 素材；仍需 Runtime preview、音频响度审查和最终人工接受",
            candidate.candidate_batch_id,
            candidate.asset_count,
            format_asset_candidate_type_counts(candidate),
        ));
    }
    output.push_str("\n\n右下点击区: 章节  图鉴  设置  巡逻");

    output
}

fn render_meta_chapter_panel(
    progress: &MetaProgress,
    settlement: Option<&MetaSettlementReport>,
    content: &ContentPack,
    base_ui_state: &RuntimeBaseUiState,
) -> String {
    let mut lines = vec![
        META_PANEL_HEADER.to_string(),
        META_PANEL_TAB_CLICK_HINT.to_string(),
    ];
    lines.push("章节目标".to_string());
    let chapter_ids = runtime_chapter_ids(progress);
    let selected_id = runtime_selected_chapter_id(progress, base_ui_state)
        .or_else(|| chapter_ids.first().cloned())
        .unwrap_or_else(|| DEFAULT_MAP_ID.to_string());
    let selected_index = chapter_ids
        .iter()
        .position(|chapter_id| chapter_id == &selected_id)
        .unwrap_or(0);
    lines.push(format!(
        "Q/E/手柄左/右 切换章节  G/手柄确认 巡逻已解锁章节  当前 {}/{}",
        if chapter_ids.is_empty() {
            0
        } else {
            selected_index + 1
        },
        chapter_ids.len()
    ));
    lines.push("右下点击区: 上章  下章  巡逻".to_string());
    if let Some(chapter) = progress.chapters.get(&selected_id) {
        let status = if chapter.unlocked {
            "已解锁"
        } else {
            "未解锁"
        };
        lines.push(format!(
            "{} ({})  {}",
            chapter_label(content, &chapter.chapter_id),
            chapter.chapter_id,
            status
        ));
        lines.push(format!(
            "地图 {} ({})  Boss {} ({})",
            runtime_map_label(content, &chapter.map_id),
            chapter.map_id,
            runtime_boss_label(content, &chapter.boss_id),
            chapter.boss_id,
        ));
        if let Some(map) = content.maps.get(&chapter.map_id) {
            lines.push(format!(
                "地图说明 {}  标签 {}",
                map.description,
                format_upgrade_tags(&map.tags)
            ));
        }
        if let Some(boss) = content.bosses.get(&chapter.boss_id) {
            lines.push(format!("Boss说明 {}", boss.common.description));
            lines.push(format!("应对 {}", boss.common.counterplay));
        }
        let goal_lines = runtime_chapter_goal_lines(&chapter.chapter_id, &chapter.completed_goals);
        lines.push(format!("目标\n{}", goal_lines.join("\n")));
        if chapter.unlocked {
            lines.push("G 会使用该章节地图重开当前巡逻并保留局外进度".to_string());
        } else {
            lines.push("该章节仍锁定；完成前序章节目标后开放，G 不会启动锁定章节".to_string());
        }
    } else {
        lines.push("当前没有章节进度记录".to_string());
    }
    if let Some(report) = settlement {
        lines.push(format!(
            "\n本局完成 {}",
            format_string_slice(&report.completed_goals, 3)
        ));
    } else {
        lines.push("\n完成章节目标后会在这里显示本局变化".to_string());
    }
    lines.join("\n")
}

fn render_meta_codex_panel(
    progress: &MetaProgress,
    settlement: Option<&MetaSettlementReport>,
    story_codex_ui_candidate: Option<&RuntimeStoryCodexUiCandidateManifest>,
    content: &ContentPack,
    codex_view: &RuntimeBaseCodexViewState,
    selected_index: usize,
) -> String {
    let mut lines = vec![
        META_PANEL_HEADER.to_string(),
        META_PANEL_TAB_CLICK_HINT.to_string(),
    ];
    lines.push("图鉴进度".to_string());
    for (label, discovered, total) in meta_codex_category_counts(progress) {
        lines.push(format!("{label}: {discovered}/{total} 已发现"));
    }
    let category = RuntimeCodexCategory::from_key(&codex_view.selected_category);
    let entries = runtime_codex_entries(progress, content, category, codex_view.discovered_only);
    let selected_entry = entries.get(selected_index.min(entries.len().saturating_sub(1)));
    let display_mode = if codex_view.discovered_only {
        "仅已发现"
    } else {
        "全部条目"
    };
    lines.push(format!(
        "\n图鉴浏览 {}  分类 {}  条目 {}/{}",
        display_mode,
        category.label(),
        if entries.is_empty() {
            0
        } else {
            selected_index.min(entries.len() - 1) + 1
        },
        entries.len()
    ));
    lines.push(
        "Q/E 或手柄 LT/RT 切换分类  B/N、右下点击区或十字键左/右切换条目  V、鼠标中键或手柄 Y 切换过滤"
            .to_string(),
    );
    lines.push("右下点击区: <类  类>  <条目  条目>  过滤".to_string());
    if let Some(entry) = selected_entry {
        let status = if entry.discovered {
            "已发现"
        } else {
            "未发现"
        };
        let title = if entry.discovered {
            entry.name.clone()
        } else {
            "未发现条目".to_string()
        };
        let detail = if entry.discovered {
            entry.description.clone()
        } else {
            "继续巡逻、使用装备、击败敌人或解锁地图后显示说明。".to_string()
        };
        lines.push(format!("{} ({})  {}", title, entry.id, status));
        lines.push(detail);
        lines.push(format!(
            "首次 {}  见过 {}  击败 {}  使用 {}",
            entry.first_seen_run.as_deref().unwrap_or("尚未记录"),
            entry.seen_count,
            entry.defeated_count,
            entry.used_count,
        ));
    } else {
        lines.push("当前过滤条件下没有图鉴条目；按 V 查看全部条目。".to_string());
    }
    let highlights = meta_codex_recent_discoveries(progress, 5);
    lines.push(format!("\n已发现 {}", format_string_slice(&highlights, 5)));
    if let Some(report) = settlement {
        lines.push(format!(
            "本局更新 {}",
            format_string_slice(&report.codex_updates, 3)
        ));
    } else {
        lines.push("本局图鉴更新会在结算后显示".to_string());
    }
    if let Some(candidate) = story_codex_ui_candidate {
        lines.push(format!(
            "\n剧情/图鉴 UI 候选: {}",
            candidate.candidate_pack_id
        ));
        lines.push(format!(
            "章节 {}  图鉴条目 {}  状态 ui_candidate 待验收",
            candidate.chapter_count, candidate.codex_entry_count
        ));
        lines.push(
            "仅显示候选状态，不读取 generated candidate 正文；仍需 Runtime UI review 和最终人工接受"
                .to_string(),
        );
    } else {
        lines.push("\n剧情/图鉴 UI 候选: 未加载".to_string());
    }
    lines.join("\n")
}

fn runtime_codex_action_from_keyboard(
    keyboard: &ButtonInput<KeyCode>,
) -> Option<RuntimeCodexAction> {
    if keyboard.just_pressed(KeyCode::KeyQ) {
        Some(RuntimeCodexAction::PreviousCategory)
    } else if keyboard.just_pressed(KeyCode::KeyE) {
        Some(RuntimeCodexAction::NextCategory)
    } else if keyboard.just_pressed(KeyCode::KeyB) {
        Some(RuntimeCodexAction::PreviousEntry)
    } else if keyboard.just_pressed(KeyCode::KeyN) {
        Some(RuntimeCodexAction::NextEntry)
    } else if keyboard.just_pressed(KeyCode::KeyV) {
        Some(RuntimeCodexAction::ToggleDiscoveredOnly)
    } else {
        None
    }
}

fn runtime_codex_action_from_pointer(
    mouse_buttons: &ButtonInput<MouseButton>,
    cursor_position: Option<Vec2>,
    window_size: Vec2,
) -> Option<RuntimeCodexAction> {
    if mouse_buttons.just_pressed(MouseButton::Right) {
        Some(RuntimeCodexAction::PreviousEntry)
    } else if mouse_buttons.just_pressed(MouseButton::Middle) {
        Some(RuntimeCodexAction::ToggleDiscoveredOnly)
    } else if mouse_buttons.just_pressed(MouseButton::Left) {
        runtime_codex_action_from_pointer_zone(cursor_position?, window_size)
    } else {
        None
    }
}

fn runtime_codex_action_from_pointer_zone(
    cursor_position: Vec2,
    window_size: Vec2,
) -> Option<RuntimeCodexAction> {
    if window_size.x <= 0.0 || window_size.y <= 0.0 {
        return None;
    }
    let panel_right = (window_size.x - META_PANEL_RIGHT_MARGIN).max(0.0);
    let panel_left = (panel_right - META_PANEL_WIDTH).max(0.0);
    let panel_width = (panel_right - panel_left).max(1.0);
    let in_panel_x = cursor_position.x >= panel_left && cursor_position.x <= panel_right;
    let in_control_y =
        cursor_position.y >= 0.0 && cursor_position.y <= CODEX_POINTER_CONTROL_HEIGHT;
    if !in_panel_x || !in_control_y {
        return None;
    }

    let normalized_x = ((cursor_position.x - panel_left) / panel_width).clamp(0.0, 0.999);
    let zone = (normalized_x * CODEX_POINTER_CONTROL_ZONE_COUNT as f32).floor() as usize;
    match zone {
        0 => Some(RuntimeCodexAction::PreviousCategory),
        1 => Some(RuntimeCodexAction::NextCategory),
        2 => Some(RuntimeCodexAction::PreviousEntry),
        3 => Some(RuntimeCodexAction::NextEntry),
        _ => Some(RuntimeCodexAction::ToggleDiscoveredOnly),
    }
}

fn runtime_codex_action_from_gamepad(
    gamepad_buttons: &ButtonInput<GamepadButton>,
) -> Option<RuntimeCodexAction> {
    if gamepad_button_type_just_pressed(gamepad_buttons, &[GamepadButtonType::LeftTrigger]) {
        Some(RuntimeCodexAction::PreviousCategory)
    } else if gamepad_button_type_just_pressed(gamepad_buttons, &[GamepadButtonType::RightTrigger])
    {
        Some(RuntimeCodexAction::NextCategory)
    } else if gamepad_button_type_just_pressed(gamepad_buttons, &[GamepadButtonType::DPadLeft]) {
        Some(RuntimeCodexAction::PreviousEntry)
    } else if gamepad_button_type_just_pressed(gamepad_buttons, &[GamepadButtonType::DPadRight]) {
        Some(RuntimeCodexAction::NextEntry)
    } else if gamepad_button_type_just_pressed(gamepad_buttons, &[GamepadButtonType::North]) {
        Some(RuntimeCodexAction::ToggleDiscoveredOnly)
    } else {
        None
    }
}

fn gamepad_button_type_just_pressed(
    gamepad_buttons: &ButtonInput<GamepadButton>,
    button_types: &[GamepadButtonType],
) -> bool {
    gamepad_buttons
        .get_just_pressed()
        .any(|button| button_types.contains(&button.button_type))
}

fn gamepad_button_type_pressed(
    gamepad_buttons: &ButtonInput<GamepadButton>,
    button_types: &[GamepadButtonType],
) -> bool {
    gamepad_buttons
        .get_pressed()
        .any(|button| button_types.contains(&button.button_type))
}

fn apply_runtime_codex_action(state: &mut RuntimeState, action: RuntimeCodexAction) {
    let current_category =
        RuntimeCodexCategory::from_key(&state.base_ui_state.codex_view.selected_category);
    match action {
        RuntimeCodexAction::PreviousCategory | RuntimeCodexAction::NextCategory => {
            let current_index = RuntimeCodexCategory::ALL
                .iter()
                .position(|category| *category == current_category)
                .unwrap_or(0);
            let next_index = match action {
                RuntimeCodexAction::PreviousCategory => {
                    if current_index == 0 {
                        RuntimeCodexCategory::ALL.len() - 1
                    } else {
                        current_index - 1
                    }
                }
                RuntimeCodexAction::NextCategory => {
                    (current_index + 1) % RuntimeCodexCategory::ALL.len()
                }
                _ => unreachable!(),
            };
            let next_category = RuntimeCodexCategory::ALL[next_index];
            state.base_ui_state.codex_view.selected_category = next_category.key().to_string();
            state.codex_selected_index = 0;
            state.last_event = format!("codex category {}", next_category.label());
        }
        RuntimeCodexAction::PreviousEntry | RuntimeCodexAction::NextEntry => {
            let entry_count = runtime_codex_entries(
                &state.meta_progress,
                &state.content,
                current_category,
                state.base_ui_state.codex_view.discovered_only,
            )
            .len();
            if entry_count > 0 {
                state.codex_selected_index = match action {
                    RuntimeCodexAction::PreviousEntry => {
                        if state.codex_selected_index == 0 {
                            entry_count - 1
                        } else {
                            state.codex_selected_index - 1
                        }
                    }
                    RuntimeCodexAction::NextEntry => (state.codex_selected_index + 1) % entry_count,
                    _ => unreachable!(),
                };
            } else {
                state.codex_selected_index = 0;
            }
            state.last_event = format!("codex entry {}", state.codex_selected_index + 1);
        }
        RuntimeCodexAction::ToggleDiscoveredOnly => {
            state.base_ui_state.codex_view.discovered_only =
                !state.base_ui_state.codex_view.discovered_only;
            state.codex_selected_index = 0;
            state.last_event = if state.base_ui_state.codex_view.discovered_only {
                "codex filter discovered only".to_string()
            } else {
                "codex filter all entries".to_string()
            };
        }
    }
    state.last_event_kind = RuntimeEventKind::System;
    state.pending_sounds.push(RuntimeSound::System);
}

fn render_meta_settings_panel(
    settings: &RuntimePrivacySettings,
    runtime_settings_file: Option<&Path>,
) -> String {
    let persistence = runtime_settings_file
        .map(|path| format!("写回 {}", path.display()))
        .unwrap_or_else(|| "未配置设置文件，本次会话生效".to_string());
    format!(
        "{}\n{}\n隐私与本地数据\n7 上传匿名遥测: {}\n8 上传原始 Replay: {}\n9 上传崩溃报告: {}\n{}\nE 导出存档  X 删除存档\nL 导出本地数据  K 删除本地数据\n右下七段点击区: 遥测 Replay 崩溃 导出存档 删除存档 导出本地 删除本地\nX/K 删除需要再次按同一键确认，切换面板或执行其他操作会取消\n导出写入平台数据根 exports/；删除只清理当前 Runtime 配置的存档或本地 telemetry/replay/crash 目录\n上传传输层: not_implemented",
        META_PANEL_HEADER,
        META_PANEL_TAB_CLICK_HINT,
        on_off_label(settings.telemetry_upload_enabled),
        on_off_label(settings.raw_replay_upload_enabled),
        on_off_label(settings.crash_report_upload_enabled),
        persistence,
    )
}

fn render_meta_loadout_panel(
    progress: &MetaProgress,
    content: &ContentPack,
    config: &RunConfig,
) -> String {
    let character_label = runtime_character_label(content, &config.character_id);
    let map_label = runtime_map_label(content, &config.map_id);
    let mut lines = vec![
        META_PANEL_HEADER.to_string(),
        META_PANEL_TAB_CLICK_HINT.to_string(),
        "巡逻准备".to_string(),
        format!("角色 {} ({})", character_label, config.character_id),
    ];

    if let Some(character) = content.characters.get(&config.character_id) {
        lines.push(format!(
            "角色说明 {}  标签 {}",
            character.description,
            format_upgrade_tags(&character.tags),
        ));
        lines.push(format!(
            "属性 HP {:.0}  移速 {:.0}  拾取 {:.0}  伤害 x{:.2}  冷却 x{:.2}  XP x{:.2}  回复 {:.1}/s",
            character.base_stats.max_health,
            character.base_stats.move_speed,
            character.base_stats.pickup_radius,
            character.base_stats.damage_multiplier,
            character.base_stats.cooldown_multiplier,
            character.base_stats.xp_multiplier,
            character.base_stats.regen_per_second,
        ));
        if let Some(trait_definition) = &character.trait_definition {
            lines.push(format!(
                "特质 {} ({})",
                trait_definition.description, trait_definition.id
            ));
        }
    }

    lines.push(format!(
        "初始装备 {}",
        format_runtime_starting_loadout(content, &config.starting_loadout)
    ));
    lines.push(format!("地图 {} ({})", map_label, config.map_id));

    if let Some(map) = content.maps.get(&config.map_id) {
        lines.push(format!("地图说明 {}", map.description));
        lines.push(format!(
            "地图标签 {}  尺寸 {:.0}x{:.0}  音乐 {}",
            format_upgrade_tags(&map.tags),
            map.size.width,
            map.size.height,
            map.music_theme,
        ));
        let hazard_summary = if map.hazards.is_empty() {
            "无固定地形伤害".to_string()
        } else {
            format!("{} 项", map.hazards.len())
        };
        lines.push(format!("地图机制 {}", hazard_summary));
    }

    if let Some(chapter_line) =
        format_runtime_loadout_chapter_line(progress, content, &config.map_id)
    {
        lines.push(chapter_line);
    }

    lines.push("C/手柄左 切换已解锁角色  M/手柄右 切换已解锁地图".to_string());
    lines.push("右下点击区: 角色  地图".to_string());
    lines.push("切换会重开当前巡逻并保留局外进度".to_string());
    lines.push(format!(
        "已解锁角色 {}",
        format_runtime_unlocked_labels(
            &runtime_unlocked_character_ids(progress, content),
            |id| runtime_character_label(content, id),
            LOADOUT_UNLOCKED_CHARACTER_LABEL_LIMIT,
        ),
    ));
    lines.push(format!(
        "已解锁地图 {}",
        format_runtime_unlocked_labels(
            &runtime_unlocked_map_ids(progress, content),
            |id| runtime_map_label(content, id),
            LOADOUT_UNLOCKED_MAP_LABEL_LIMIT,
        ),
    ));

    lines.join("\n")
}

fn format_runtime_starting_loadout(content: &ContentPack, loadout: &StartingLoadout) -> String {
    if loadout.weapons.is_empty() && loadout.passives.is_empty() {
        return "使用角色默认初始装备".to_string();
    }

    format!(
        "武器 {}  被动 {}",
        format_runtime_content_id_labels(&loadout.weapons, 3, |id| runtime_weapon_label(
            content, id
        )),
        format_runtime_content_id_labels(&loadout.passives, 3, |id| runtime_passive_label(
            content, id
        )),
    )
}

fn format_runtime_loadout_chapter_line(
    progress: &MetaProgress,
    content: &ContentPack,
    map_id: &str,
) -> Option<String> {
    progress
        .chapters
        .values()
        .find(|chapter| chapter.map_id == map_id)
        .map(|chapter| {
            let status = if chapter.unlocked {
                "已解锁章节"
            } else {
                "锁定章节"
            };
            format!(
                "章节 Boss {} ({})  {}",
                runtime_boss_label(content, &chapter.boss_id),
                chapter.boss_id,
                status,
            )
        })
}

fn format_runtime_content_id_labels<F>(ids: &[String], limit: usize, label_for_id: F) -> String
where
    F: Fn(&str) -> String,
{
    if ids.is_empty() {
        return "无".to_string();
    }

    let mut visible = ids
        .iter()
        .take(limit)
        .map(|id| format!("{} ({})", label_for_id(id), id))
        .collect::<Vec<_>>();
    if ids.len() > limit {
        visible.push(format!("+{} 项", ids.len() - limit));
    }
    visible.join("、")
}

fn runtime_character_label(content: &ContentPack, character_id: &str) -> String {
    content
        .characters
        .get(character_id)
        .map(|character| character.name.clone())
        .unwrap_or_else(|| "未知角色".to_string())
}

fn runtime_map_label(content: &ContentPack, map_id: &str) -> String {
    content
        .maps
        .get(map_id)
        .map(|map| map.name.clone())
        .unwrap_or_else(|| map_visual_style(map_id).display_name.to_string())
}

fn runtime_boss_label(content: &ContentPack, boss_id: &str) -> String {
    content
        .bosses
        .get(boss_id)
        .map(|boss| boss.common.name.clone())
        .unwrap_or_else(|| "未知 Boss".to_string())
}

fn runtime_enemy_label(content: &ContentPack, enemy_id: &str) -> String {
    content
        .enemies
        .get(enemy_id)
        .map(|enemy| enemy.common.name.clone())
        .unwrap_or_else(|| enemy_id.to_string())
}

fn runtime_weapon_label(content: &ContentPack, weapon_id: &str) -> String {
    content
        .weapons
        .get(weapon_id)
        .map(|weapon| weapon.name.clone())
        .unwrap_or_else(|| weapon_id.to_string())
}

fn runtime_passive_label(content: &ContentPack, passive_id: &str) -> String {
    content
        .passives
        .get(passive_id)
        .map(|passive| passive.name.clone())
        .unwrap_or_else(|| passive_id.to_string())
}

fn runtime_evolution_label(content: &ContentPack, evolution_id: &str) -> String {
    content
        .evolutions
        .get(evolution_id)
        .map(|evolution| evolution.name.clone())
        .unwrap_or_else(|| evolution_id.to_string())
}

fn runtime_event_label(content: &ContentPack, event_id: &str) -> String {
    content
        .events
        .get(event_id)
        .map(|event| event.name.clone())
        .unwrap_or_else(|| event_id.to_string())
}

fn runtime_boss_ability_label(ability_id: &str) -> String {
    match ability_id {
        "dash_charge" => "直线冲撞",
        "summon_sour_gummy" => "召唤酸味软糖",
        "summon_bouncy_gummy" => "召唤蹦蹦软糖",
        "summon_soda_bubble" => "召唤汽水泡泡",
        "summon_caramel_slime" => "召唤焦糖史莱姆",
        "summon_sticky_bear_gummy" => "召唤黏黏熊糖",
        "summon_guard_wave" => "召唤护卫潮",
        "split_cotton_clumps" => "分裂棉花糖团",
        "bubble_barrage" => "汽水泡泡弹幕",
        "soda_fountain_burst" => "汽水喷泉爆发",
        "lay_caramel_tracks" => "铺设焦糖轨道",
        "slow_pulse" => "减速脉冲",
        "caramel_floor_cycle" => "焦糖地面循环",
        "jump_shockwave" => "跳跃震波",
        "double_jump_shockwave" => "双重跳跃震波",
        "sour_phase_storm" => "酸味风暴",
        "spicy_phase_storm" => "辣味风暴",
        "soda_phase_storm" => "汽水风暴",
        "multi_flavor_storm" => "多味风暴",
        other => return other.replace('_', " "),
    }
    .to_string()
}

fn terminal_kind_label(kind: TerminalKind) -> &'static str {
    match kind {
        TerminalKind::Victory => "胜利",
        TerminalKind::Defeat => "失败",
        TerminalKind::Timeout => "超时",
        TerminalKind::Aborted => "中止",
        TerminalKind::InvalidState => "异常",
    }
}

fn chapter_label(content: &ContentPack, chapter_id: &str) -> String {
    runtime_map_label(content, chapter_id)
}

fn runtime_chapter_ids(progress: &MetaProgress) -> Vec<String> {
    progress.chapters.keys().cloned().collect()
}

fn runtime_selected_chapter_id(
    progress: &MetaProgress,
    base_ui_state: &RuntimeBaseUiState,
) -> Option<String> {
    if progress
        .chapters
        .contains_key(&base_ui_state.last_selected_chapter_id)
    {
        Some(base_ui_state.last_selected_chapter_id.clone())
    } else {
        progress.chapters.keys().next().cloned()
    }
}

fn runtime_chapter_goal_lines(
    chapter_id: &str,
    completed_goals: &std::collections::BTreeSet<String>,
) -> Vec<String> {
    let goals = match chapter_id {
        "frosting-grassland" => vec![
            ("survive-10-minutes", "标准巡逻坚持 10 分钟"),
            ("defeat-runaway-sugar-mixer", "击败暴走搅糖机"),
            ("collect-200-candy-crystals", "收集 200 糖晶经验"),
            ("rainbow-candy-shot-level-5", "把彩虹糖弹升到 5 级"),
        ],
        _ => vec![(
            "future-chapter-goals",
            "后续章节目标待内容接受与平衡验证后开放",
        )],
    };
    goals
        .into_iter()
        .map(|(goal_id, label)| {
            let status = if completed_goals.contains(goal_id) {
                "[x]"
            } else {
                "[ ]"
            };
            format!("{status} {goal_id} - {label}")
        })
        .collect()
}

fn format_runtime_unlocked_labels(
    ids: &[String],
    label_for_id: impl Fn(&str) -> String,
    limit: usize,
) -> String {
    if ids.is_empty() {
        return "无".to_string();
    }
    let mut labels = ids
        .iter()
        .take(limit)
        .map(|id| format!("{}({})", label_for_id(id), id))
        .collect::<Vec<_>>();
    if ids.len() > limit {
        labels.push(format!("还有 {} 项", ids.len() - limit));
    }
    labels.join(", ")
}

fn meta_codex_discovered_count(progress: &MetaProgress) -> usize {
    let groups = [
        &progress.codex.characters,
        &progress.codex.weapons,
        &progress.codex.passives,
        &progress.codex.enemies,
        &progress.codex.bosses,
        &progress.codex.maps,
        &progress.codex.evolutions,
        &progress.codex.events,
    ];
    groups
        .iter()
        .map(|group| group.values().filter(|entry| entry.discovered).count())
        .sum()
}

fn meta_codex_category_counts(progress: &MetaProgress) -> Vec<(&'static str, usize, usize)> {
    vec![
        (
            "角色",
            discovered_meta_entries(&progress.codex.characters),
            progress.codex.characters.len(),
        ),
        (
            "武器",
            discovered_meta_entries(&progress.codex.weapons),
            progress.codex.weapons.len(),
        ),
        (
            "被动",
            discovered_meta_entries(&progress.codex.passives),
            progress.codex.passives.len(),
        ),
        (
            "敌人",
            discovered_meta_entries(&progress.codex.enemies),
            progress.codex.enemies.len(),
        ),
        (
            "Boss",
            discovered_meta_entries(&progress.codex.bosses),
            progress.codex.bosses.len(),
        ),
        (
            "地图",
            discovered_meta_entries(&progress.codex.maps),
            progress.codex.maps.len(),
        ),
        (
            "进化",
            discovered_meta_entries(&progress.codex.evolutions),
            progress.codex.evolutions.len(),
        ),
        (
            "事件",
            discovered_meta_entries(&progress.codex.events),
            progress.codex.events.len(),
        ),
    ]
}

fn discovered_meta_entries(group: &std::collections::BTreeMap<String, MetaCodexEntry>) -> usize {
    group.values().filter(|entry| entry.discovered).count()
}

fn meta_codex_recent_discoveries(progress: &MetaProgress, limit: usize) -> Vec<String> {
    let groups = [
        ("character", &progress.codex.characters),
        ("weapon", &progress.codex.weapons),
        ("passive", &progress.codex.passives),
        ("enemy", &progress.codex.enemies),
        ("boss", &progress.codex.bosses),
        ("map", &progress.codex.maps),
        ("evolution", &progress.codex.evolutions),
        ("event", &progress.codex.events),
    ];
    let mut items = Vec::new();
    for (label, group) in groups {
        for (id, entry) in group {
            if entry.discovered {
                items.push(format!("{label}:{id}"));
            }
        }
    }
    items.into_iter().take(limit).collect()
}

fn runtime_codex_entries(
    progress: &MetaProgress,
    content: &ContentPack,
    category: RuntimeCodexCategory,
    discovered_only: bool,
) -> Vec<RuntimeCodexEntryView> {
    let mut definitions = BTreeMap::<String, (String, String)>::new();
    match category {
        RuntimeCodexCategory::Characters => {
            for (id, item) in &content.characters {
                definitions.insert(id.clone(), (item.name.clone(), item.description.clone()));
            }
        }
        RuntimeCodexCategory::Weapons => {
            for (id, item) in &content.weapons {
                definitions.insert(id.clone(), (item.name.clone(), item.description.clone()));
            }
        }
        RuntimeCodexCategory::Passives => {
            for (id, item) in &content.passives {
                definitions.insert(id.clone(), (item.name.clone(), item.description.clone()));
            }
        }
        RuntimeCodexCategory::Enemies => {
            for (id, item) in &content.enemies {
                definitions.insert(
                    id.clone(),
                    (item.common.name.clone(), item.common.description.clone()),
                );
            }
        }
        RuntimeCodexCategory::Bosses => {
            for (id, item) in &content.bosses {
                definitions.insert(
                    id.clone(),
                    (item.common.name.clone(), item.common.description.clone()),
                );
            }
        }
        RuntimeCodexCategory::Maps => {
            for (id, item) in &content.maps {
                definitions.insert(id.clone(), (item.name.clone(), item.description.clone()));
            }
        }
        RuntimeCodexCategory::Evolutions => {
            for (id, item) in &content.evolutions {
                definitions.insert(id.clone(), (item.name.clone(), item.description.clone()));
            }
        }
        RuntimeCodexCategory::Events => {
            for (id, item) in &content.events {
                definitions.insert(id.clone(), (item.name.clone(), item.description.clone()));
            }
        }
    }

    let codex_group = runtime_codex_group(progress, category);
    for id in codex_group.keys() {
        definitions
            .entry(id.clone())
            .or_insert_with(|| (id.clone(), "当前内容包没有这个图鉴条目的说明。".to_string()));
    }

    definitions
        .into_iter()
        .filter_map(|(id, (name, description))| {
            let codex_entry = codex_group.get(&id);
            let discovered = codex_entry.is_some_and(|entry| entry.discovered);
            if discovered_only && !discovered {
                return None;
            }
            let default_entry = MetaCodexEntry::default();
            let entry = codex_entry.unwrap_or(&default_entry);
            Some(RuntimeCodexEntryView {
                id,
                name,
                description,
                discovered,
                first_seen_run: entry.first_seen_run.clone(),
                seen_count: entry.seen_count,
                defeated_count: entry.defeated_count,
                used_count: entry.used_count,
            })
        })
        .collect()
}

fn runtime_codex_group(
    progress: &MetaProgress,
    category: RuntimeCodexCategory,
) -> &BTreeMap<String, MetaCodexEntry> {
    match category {
        RuntimeCodexCategory::Characters => &progress.codex.characters,
        RuntimeCodexCategory::Weapons => &progress.codex.weapons,
        RuntimeCodexCategory::Passives => &progress.codex.passives,
        RuntimeCodexCategory::Enemies => &progress.codex.enemies,
        RuntimeCodexCategory::Bosses => &progress.codex.bosses,
        RuntimeCodexCategory::Maps => &progress.codex.maps,
        RuntimeCodexCategory::Evolutions => &progress.codex.evolutions,
        RuntimeCodexCategory::Events => &progress.codex.events,
    }
}

fn meta_completed_goal_count(progress: &MetaProgress) -> usize {
    progress
        .chapters
        .values()
        .map(|chapter| chapter.completed_goals.len())
        .sum()
}

fn meta_unlocked_content_count(progress: &MetaProgress) -> usize {
    progress.unlocks.characters.len()
        + progress.unlocks.weapons.len()
        + progress.unlocks.passives.len()
        + progress.unlocks.maps.len()
        + progress.unlocks.evolutions.len()
        + progress.unlocks.chapters.len()
        + progress.unlocks.events.len()
        + progress.unlocks.cosmetics.len()
}

fn format_string_set(values: &std::collections::BTreeSet<String>, limit: usize) -> String {
    let items = values.iter().cloned().collect::<Vec<_>>();
    format_string_items(&items, limit)
}

fn format_string_slice(values: &[String], limit: usize) -> String {
    format_string_items(values, limit)
}

fn format_string_items(values: &[String], limit: usize) -> String {
    if values.is_empty() {
        return "无".to_string();
    }

    let mut visible = values.iter().take(limit).cloned().collect::<Vec<_>>();
    if values.len() > limit {
        visible.push(format!("+{} 项", values.len() - limit));
    }
    visible.join(", ")
}

fn format_meta_unlocks(report: &MetaSettlementReport, limit: usize) -> String {
    if report.unlocked.is_empty() {
        return "无".to_string();
    }

    let values = report
        .unlocked
        .iter()
        .map(|unlock| format!("{}:{}", unlock.kind, unlock.id))
        .collect::<Vec<_>>();
    format_string_items(&values, limit)
}

fn format_settlement_outcome(summary: &MetaRunSummary) -> &'static str {
    if summary.victory {
        "胜利"
    } else {
        "失败"
    }
}

fn format_settlement_duration(seconds: f32) -> String {
    format!("{:.0}s", seconds.max(0.0))
}

fn format_terminal_reason(reason: &str) -> String {
    match reason {
        "duration_reached" => "坚持到巡逻结束".to_string(),
        "player_health_depleted" => "生命值归零".to_string(),
        "not_terminal" => "仍在巡逻".to_string(),
        other => other.to_string(),
    }
}

fn format_weapon_levels(weapon_levels: &BTreeMap<String, u32>, limit: usize) -> String {
    if weapon_levels.is_empty() {
        return "无".to_string();
    }

    let values = weapon_levels
        .iter()
        .map(|(weapon_id, level)| format!("{weapon_id} Lv.{level}"))
        .collect::<Vec<_>>();
    format_string_items(&values, limit)
}

fn format_passive_set(passives: &BTreeSet<String>, limit: usize) -> String {
    let values = passives.iter().cloned().collect::<Vec<_>>();
    format_string_items(&values, limit)
}

fn format_damage_sources(sources: &BTreeMap<String, f32>, limit: usize) -> String {
    if sources.is_empty() {
        return "无".to_string();
    }

    let values = sources
        .iter()
        .map(|(source, damage)| format!("{} {:.1}", format_damage_source(source), damage))
        .collect::<Vec<_>>();
    format_string_items(&values, limit)
}

fn format_damage_source(source: &str) -> String {
    match source {
        "contact" => "接触".to_string(),
        "hazard" => "风暴地面".to_string(),
        other => other.to_string(),
    }
}

fn format_settlement_next_step(report: &MetaSettlementReport) -> &'static str {
    if !report.unlocked.is_empty() {
        "F5 试试新角色或地图，F3 查看新增图鉴"
    } else if !report.completed_goals.is_empty() {
        "F2 查看章节目标，F5 开下一次巡逻"
    } else if report.run_summary.victory {
        "F2 挑战下一章，F5 换构筑继续巡逻"
    } else {
        "F5 调整角色或地图继续巡逻，F3 查看本局图鉴"
    }
}

fn format_asset_candidate_type_counts(candidate: &RuntimeAssetCandidateManifest) -> String {
    let mut counts: std::collections::BTreeMap<&str, usize> = std::collections::BTreeMap::new();
    for asset in &candidate.assets {
        *counts.entry(asset.asset_type.as_str()).or_insert(0) += 1;
    }
    if counts.is_empty() {
        return "无".to_string();
    }
    counts
        .into_iter()
        .map(|(asset_type, count)| format!("{asset_type}:{count}"))
        .collect::<Vec<_>>()
        .join(", ")
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

fn run_config_from_cli(cli: &RuntimeCli, content: &ContentPack) -> RunConfig {
    RunConfig {
        seed: cli.seed,
        map_id: cli.map_id.clone(),
        character_id: cli.character_id.clone(),
        starting_loadout: runtime_character_starting_loadout(content, &cli.character_id),
        difficulty: Difficulty::Normal,
        duration_seconds: cli.seconds,
        ruleset_version: "prototype-v0".to_string(),
        content_pack_ids: cli.content_pack_ids.clone(),
        tick_rate: cli.tick_rate,
    }
}

fn runtime_character_starting_loadout(
    content: &ContentPack,
    character_id: &str,
) -> StartingLoadout {
    content
        .characters
        .get(character_id)
        .map(|character| StartingLoadout {
            weapons: character.initial_loadout.weapons.clone(),
            passives: character.initial_loadout.passives.clone(),
        })
        .unwrap_or_default()
}

fn runtime_unlocked_character_ids(progress: &MetaProgress, content: &ContentPack) -> Vec<String> {
    content
        .characters
        .keys()
        .filter(|id| progress.unlocks.characters.contains(*id))
        .cloned()
        .collect()
}

fn runtime_unlocked_map_ids(progress: &MetaProgress, content: &ContentPack) -> Vec<String> {
    content
        .maps
        .keys()
        .filter(|id| progress.unlocks.maps.contains(*id))
        .cloned()
        .collect()
}

fn unlock_runtime_content_for_session(progress: &mut MetaProgress, content: &ContentPack) {
    progress
        .unlocks
        .characters
        .extend(content.characters.keys().cloned());
    progress
        .unlocks
        .weapons
        .extend(content.weapons.keys().cloned());
    progress
        .unlocks
        .passives
        .extend(content.passives.keys().cloned());
    progress.unlocks.maps.extend(content.maps.keys().cloned());
    progress
        .unlocks
        .evolutions
        .extend(content.evolutions.keys().cloned());
    progress
        .unlocks
        .events
        .extend(content.events.keys().cloned());
    progress
        .unlocks
        .chapters
        .extend(content.maps.keys().cloned());
    for (chapter_id, chapter) in &mut progress.chapters {
        if content.maps.contains_key(&chapter.map_id) || content.maps.contains_key(chapter_id) {
            chapter.unlocked = true;
        }
    }
}

fn next_runtime_selection_id(ids: &[String], current_id: &str) -> Option<String> {
    if ids.is_empty() {
        return None;
    }
    let next_index = ids
        .iter()
        .position(|id| id == current_id)
        .map(|index| (index + 1) % ids.len())
        .unwrap_or(0);
    Some(ids[next_index].clone())
}

fn runtime_native_platform_data_root() -> Option<PathBuf> {
    runtime_native_platform_data_root_for_env(
        env::consts::OS,
        env::var_os("HOME").map(PathBuf::from),
        env::var_os("XDG_DATA_HOME").map(PathBuf::from),
        env::var_os("APPDATA").map(PathBuf::from),
    )
}

fn runtime_native_platform_data_root_for_env(
    os: &str,
    home: Option<PathBuf>,
    xdg_data_home: Option<PathBuf>,
    appdata: Option<PathBuf>,
) -> Option<PathBuf> {
    match os {
        "macos" => home.map(|path| {
            path.join("Library")
                .join("Application Support")
                .join(NATIVE_PLATFORM_APP_DIR_MACOS)
        }),
        "windows" => appdata
            .or_else(|| home.map(|path| path.join("AppData").join("Roaming")))
            .map(|path| path.join(NATIVE_PLATFORM_APP_DIR_MACOS)),
        _ => xdg_data_home
            .or_else(|| home.map(|path| path.join(".local").join("share")))
            .map(|path| path.join(NATIVE_PLATFORM_APP_DIR_UNIX)),
    }
}

fn resolve_runtime_platform_paths(data_root: impl Into<PathBuf>) -> RuntimePlatformPaths {
    RuntimePlatformPaths::from_data_root(data_root.into())
}

impl RuntimePlatformPaths {
    fn from_data_root(data_root: PathBuf) -> Self {
        Self {
            save_file: data_root
                .join(PLATFORM_SAVE_ROOT)
                .join(RUNTIME_SAVE_FILE_NAME),
            runtime_settings_file: data_root
                .join(PLATFORM_SETTINGS_ROOT)
                .join(RUNTIME_SETTINGS_FILE_NAME),
            local_telemetry_dir: data_root.join(PLATFORM_TELEMETRY_ROOT),
            local_replay_dir: data_root.join(PLATFORM_REPLAY_ROOT),
            crash_report_dir: data_root.join(PLATFORM_CRASH_REPORT_ROOT),
            data_root,
        }
    }

    fn local_data_dirs(&self) -> Vec<PathBuf> {
        vec![
            self.local_telemetry_dir.clone(),
            self.local_replay_dir.clone(),
            self.crash_report_dir.clone(),
        ]
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
            "--native-platform-data-root" => {
                if let Some(native_root) = runtime_native_platform_data_root() {
                    let platform_paths = resolve_runtime_platform_paths(native_root);
                    let local_data_dirs = platform_paths.local_data_dirs();
                    cli.platform_data_root = platform_paths.data_root.clone();
                    cli.runtime_settings_file = Some(platform_paths.runtime_settings_file);
                    cli.save_file = Some(platform_paths.save_file);
                    cli.explicit_save_file = false;
                    cli.local_data_dirs = local_data_dirs;
                    cli.explicit_local_data_dirs.clear();
                }
            }
            "--platform-data-root" => {
                if let Some(value) = args.next() {
                    let platform_paths = resolve_runtime_platform_paths(value);
                    let local_data_dirs = platform_paths.local_data_dirs();
                    cli.platform_data_root = platform_paths.data_root.clone();
                    cli.runtime_settings_file = Some(platform_paths.runtime_settings_file);
                    cli.save_file = Some(platform_paths.save_file);
                    cli.explicit_save_file = false;
                    cli.local_data_dirs = local_data_dirs;
                    cli.explicit_local_data_dirs.clear();
                }
            }
            "--content-dir" => {
                if let Some(value) = args.next() {
                    cli.content_dir = PathBuf::from(value);
                }
            }
            "--accepted-lock-file" => {
                if let Some(value) = args.next() {
                    cli.accepted_lock_file = Some(PathBuf::from(value));
                }
            }
            "--accepted-content-id" => {
                if let Some(value) = args.next() {
                    cli.accepted_content_id = Some(value);
                }
            }
            "--character-id" => {
                if let Some(value) = args.next() {
                    cli.character_id = value;
                }
            }
            "--seed" => {
                if let Some(value) = args.next() {
                    cli.seed = value.parse().unwrap_or(cli.seed);
                }
            }
            "--map-id" => {
                if let Some(value) = args.next() {
                    cli.map_id = value;
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
            "--runtime-settings-file" => {
                if let Some(value) = args.next() {
                    cli.runtime_settings_file = Some(PathBuf::from(value));
                }
            }
            "--local-data-dir" => {
                if let Some(value) = args.next() {
                    let path = PathBuf::from(value);
                    cli.local_data_dirs.push(path.clone());
                    cli.explicit_local_data_dirs.push(path);
                }
            }
            "--export-local-data" => {
                if let Some(value) = args.next() {
                    cli.export_local_data = Some(PathBuf::from(value));
                }
            }
            "--delete-local-data" => {
                cli.delete_local_data = true;
            }
            "--print-privacy-notice" => {
                cli.print_privacy_notice = true;
            }
            "--save-file" => {
                if let Some(value) = args.next() {
                    cli.save_file = Some(PathBuf::from(value));
                    cli.explicit_save_file = true;
                }
            }
            "--export-save" => {
                if let Some(value) = args.next() {
                    cli.export_save = Some(PathBuf::from(value));
                }
            }
            "--delete-save" => {
                cli.delete_save = true;
            }
            "--story-codex-ui-candidate-manifest" => {
                if let Some(value) = args.next() {
                    cli.story_codex_ui_candidate_manifest = Some(PathBuf::from(value));
                }
            }
            "--asset-runtime-candidate-manifest" => {
                if let Some(value) = args.next() {
                    cli.asset_runtime_candidate_manifest = Some(PathBuf::from(value));
                }
            }
            "--unlock-all-content" => {
                cli.unlock_all_content = true;
            }
            _ => {}
        }
    }

    cli
}

fn run_runtime_prelaunch_actions(cli: &RuntimeCli) -> Result<bool, String> {
    let privacy_settings = load_runtime_privacy_settings(cli)
        .map_err(|error| format!("failed to load privacy settings: {error}"))?;
    let mut handled = false;

    if cli.print_privacy_notice {
        println!("{}", runtime_privacy_notice(&privacy_settings));
        handled = true;
    }

    if let Some(export_path) = &cli.export_local_data {
        export_runtime_local_data(cli, &privacy_settings, export_path)
            .map_err(|error| format!("failed to export local data: {error}"))?;
        println!("{}", export_path.display());
        handled = true;
    }

    if cli.delete_local_data {
        let report = delete_runtime_local_data(cli)
            .map_err(|error| format!("failed to delete local data: {error}"))?;
        println!(
            "deleted {} local files and {} empty directories",
            report.deleted_files, report.deleted_dirs
        );
        handled = true;
    }

    if let Some(export_path) = &cli.export_save {
        export_runtime_save(cli, &privacy_settings, export_path)
            .map_err(|error| format!("failed to export save: {error}"))?;
        println!("{}", export_path.display());
        handled = true;
    }

    if cli.delete_save {
        delete_runtime_save(cli).map_err(|error| format!("failed to delete save: {error}"))?;
        println!(
            "deleted save {}",
            cli.save_file
                .as_ref()
                .map(|path| path.display().to_string())
                .unwrap_or_else(|| "<missing>".to_string())
        );
        handled = true;
    }

    Ok(handled)
}

fn load_runtime_privacy_settings(cli: &RuntimeCli) -> std::io::Result<RuntimePrivacySettings> {
    let Some(path) = &cli.runtime_settings_file else {
        return Ok(RuntimePrivacySettings::default());
    };
    if !path.exists() {
        return Ok(RuntimePrivacySettings::default());
    }
    let text = fs::read_to_string(path)?;
    let settings = serde_json::from_str::<RuntimePrivacySettings>(&text).map_err(|error| {
        std::io::Error::new(std::io::ErrorKind::InvalidData, format!("{error}"))
    })?;
    Ok(settings)
}

fn write_runtime_privacy_settings(
    path: &Path,
    settings: &RuntimePrivacySettings,
) -> std::io::Result<()> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }
    let json = serde_json::to_string_pretty(settings)?;
    fs::write(path, format!("{json}\n"))
}

fn persist_runtime_privacy_settings_file(
    path: Option<&Path>,
    settings: &RuntimePrivacySettings,
) -> std::io::Result<bool> {
    let Some(path) = path else {
        return Ok(false);
    };
    write_runtime_privacy_settings(path, settings)?;
    Ok(true)
}

fn persist_runtime_privacy_settings_if_configured(state: &RuntimeState) -> std::io::Result<bool> {
    persist_runtime_privacy_settings_file(
        state.runtime_settings_file.as_deref(),
        &state.privacy_settings,
    )
}

#[allow(dead_code)]
fn load_runtime_meta_progress(
    cli: &RuntimeCli,
    privacy_settings: &RuntimePrivacySettings,
) -> std::io::Result<MetaProgress> {
    Ok(load_runtime_save_state(cli, privacy_settings)?.meta_progress)
}

fn load_runtime_story_codex_ui_candidate_manifest(
    cli: &RuntimeCli,
) -> std::io::Result<Option<RuntimeStoryCodexUiCandidateManifest>> {
    let Some(path) = &cli.story_codex_ui_candidate_manifest else {
        return Ok(None);
    };
    let text = fs::read_to_string(path)?;
    let manifest =
        serde_json::from_str::<RuntimeStoryCodexUiCandidateManifest>(&text).map_err(|error| {
            std::io::Error::new(std::io::ErrorKind::InvalidData, format!("{error}"))
        })?;
    validate_runtime_story_codex_ui_candidate_manifest(&manifest)?;
    Ok(Some(manifest))
}

fn validate_runtime_story_codex_ui_candidate_manifest(
    manifest: &RuntimeStoryCodexUiCandidateManifest,
) -> std::io::Result<()> {
    if manifest.manifest_contract_id != STORY_CODEX_UI_CANDIDATE_MANIFEST_CONTRACT_ID {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "story/codex UI candidate manifest must use story-codex-ui-candidate-manifest-v0",
        ));
    }
    if manifest.stage != STORY_CODEX_UI_CANDIDATE_STAGE {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "story/codex UI candidate manifest stage must be story_codex_ui_candidate",
        ));
    }
    if manifest.manual_gate_decision != "ui_candidate" {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "story/codex UI candidate manifest manual_gate_decision must be ui_candidate",
        ));
    }
    if manifest.candidate_pack_id.trim().is_empty() {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "story/codex UI candidate manifest candidate_pack_id must be non-empty",
        ));
    }
    if manifest.chapter_count == 0 || manifest.codex_entry_count == 0 {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "story/codex UI candidate manifest chapter_count and codex_entry_count must be positive",
        ));
    }
    if manifest.rules.accepted_content
        || manifest.rules.runtime_integrated
        || !manifest.rules.requires_runtime_ui_review
        || !manifest.rules.requires_final_human_acceptance
    {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "story/codex UI candidate manifest must keep accepted_content=false, runtime_integrated=false, requires_runtime_ui_review=true, and requires_final_human_acceptance=true",
        ));
    }
    Ok(())
}

fn load_runtime_asset_candidate_manifest(
    cli: &RuntimeCli,
) -> std::io::Result<Option<RuntimeAssetCandidateManifest>> {
    let Some(path) = &cli.asset_runtime_candidate_manifest else {
        return Ok(None);
    };
    let text = fs::read_to_string(path)?;
    let manifest =
        serde_json::from_str::<RuntimeAssetCandidateManifest>(&text).map_err(|error| {
            std::io::Error::new(std::io::ErrorKind::InvalidData, format!("{error}"))
        })?;
    validate_runtime_asset_candidate_manifest(&manifest)?;
    Ok(Some(manifest))
}

fn validate_runtime_asset_candidate_manifest(
    manifest: &RuntimeAssetCandidateManifest,
) -> std::io::Result<()> {
    if manifest.manifest_contract_id != ASSET_RUNTIME_CANDIDATE_MANIFEST_CONTRACT_ID {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "asset Runtime candidate manifest must use asset-runtime-candidate-manifest-v0",
        ));
    }
    if manifest.stage != ASSET_RUNTIME_CANDIDATE_STAGE {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "asset Runtime candidate manifest stage must be asset_runtime_candidate",
        ));
    }
    if manifest.manual_gate_decision != "asset_candidate" {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "asset Runtime candidate manifest manual_gate_decision must be asset_candidate",
        ));
    }
    if manifest.candidate_batch_id.trim().is_empty() {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "asset Runtime candidate manifest candidate_batch_id must be non-empty",
        ));
    }
    if manifest.asset_count == 0 || manifest.assets.is_empty() {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "asset Runtime candidate manifest asset_count and assets must be non-empty",
        ));
    }
    if usize::try_from(manifest.asset_count).ok() != Some(manifest.assets.len()) {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "asset Runtime candidate manifest asset_count must match assets length",
        ));
    }
    for asset in &manifest.assets {
        if asset.id.trim().is_empty()
            || asset.asset_type.trim().is_empty()
            || asset.qa_status.trim().is_empty()
            || asset.allowed_candidate_uses.is_empty()
        {
            return Err(std::io::Error::new(
                std::io::ErrorKind::InvalidData,
                "asset Runtime candidate manifest assets require id, type, qa_status, and allowed_candidate_uses",
            ));
        }
        if asset.allowed_candidate_uses.iter().any(|use_label| {
            let normalized = use_label.trim();
            normalized.is_empty()
                || matches!(
                    normalized,
                    "accepted_content" | "runtime_integrated" | "release_ready"
                )
        }) {
            return Err(std::io::Error::new(
                std::io::ErrorKind::InvalidData,
                "asset Runtime candidate manifest allowed_candidate_uses must stay in candidate-only stages",
            ));
        }
    }
    if manifest.rules.accepted_content
        || manifest.rules.runtime_integrated
        || manifest.rules.release_ready
        || !manifest.rules.requires_runtime_preview
        || !manifest.rules.requires_audio_loudness_review
        || !manifest.rules.requires_final_human_acceptance
    {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "asset Runtime candidate manifest must keep accepted_content=false, runtime_integrated=false, release_ready=false, requires_runtime_preview=true, requires_audio_loudness_review=true, and requires_final_human_acceptance=true",
        ));
    }
    Ok(())
}

fn load_runtime_save_state(
    cli: &RuntimeCli,
    privacy_settings: &RuntimePrivacySettings,
) -> std::io::Result<RuntimeSaveStateV1> {
    let Some(path) = &cli.save_file else {
        return Ok(build_runtime_save_state(
            cli,
            privacy_settings,
            &MetaProgress::demo_start(),
        ));
    };
    if !path.exists() {
        write_runtime_save_state(path, cli, privacy_settings, &MetaProgress::demo_start())?;
    }
    let result = read_runtime_save_state(path)?;
    if result.migrated_from_v0 {
        write_runtime_save_state_from_v1(path, &result.state)?;
    }
    Ok(result.state)
}

fn read_runtime_save_state(path: &Path) -> std::io::Result<RuntimeSaveReadResult> {
    let text = fs::read_to_string(path)?;
    let header = serde_json::from_str::<serde_json::Value>(&text).map_err(|error| {
        std::io::Error::new(std::io::ErrorKind::InvalidData, format!("{error}"))
    })?;
    let schema_version = header
        .get("schema_version")
        .and_then(serde_json::Value::as_u64)
        .and_then(|value| u32::try_from(value).ok());
    let contract_id = header
        .get("contract_id")
        .and_then(serde_json::Value::as_str)
        .unwrap_or_default();

    match (contract_id, schema_version) {
        (RUNTIME_SAVE_V1_CONTRACT_ID, Some(RUNTIME_SAVE_V1_SCHEMA_VERSION)) => {
            let state = serde_json::from_str::<RuntimeSaveStateV1>(&text).map_err(|error| {
                std::io::Error::new(std::io::ErrorKind::InvalidData, format!("{error}"))
            })?;
            validate_runtime_save_state_v1(&state)?;
            Ok(RuntimeSaveReadResult {
                state,
                migrated_from_v0: false,
            })
        }
        (RUNTIME_SAVE_V0_CONTRACT_ID, Some(RUNTIME_SAVE_V0_SCHEMA_VERSION)) => {
            let state = serde_json::from_str::<RuntimeSaveStateV0>(&text).map_err(|error| {
                std::io::Error::new(std::io::ErrorKind::InvalidData, format!("{error}"))
            })?;
            Ok(RuntimeSaveReadResult {
                state: migrate_runtime_save_v0_to_v1(state),
                migrated_from_v0: true,
            })
        }
        _ => Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "runtime save must use save-state-v0 schema_version 1 or save-state-v1 schema_version 2",
        )),
    }
}

fn migrate_runtime_save_v0_to_v1(source: RuntimeSaveStateV0) -> RuntimeSaveStateV1 {
    RuntimeSaveStateV1 {
        schema_version: RUNTIME_SAVE_V1_SCHEMA_VERSION,
        contract_id: RUNTIME_SAVE_V1_CONTRACT_ID.to_string(),
        save_id: source.save_id.clone(),
        profile_id: source.profile_id,
        created_at: source.created_at,
        updated_at: RUNTIME_SAVE_TIMESTAMP.to_string(),
        game_version: source.game_version,
        ruleset_version: source.ruleset_version,
        content_pack_ids: source.content_pack_ids,
        settings: source.settings,
        data_controls: source.data_controls,
        meta_progress: source.meta_progress,
        migration_history: vec![RuntimeSaveMigrationEntry {
            migration_id: RUNTIME_SAVE_MIGRATION_ID.to_string(),
            source_save_id: source.save_id,
            source_contract_id: RUNTIME_SAVE_V0_CONTRACT_ID.to_string(),
            source_schema_version: RUNTIME_SAVE_V0_SCHEMA_VERSION,
            target_contract_id: RUNTIME_SAVE_V1_CONTRACT_ID.to_string(),
            target_schema_version: RUNTIME_SAVE_V1_SCHEMA_VERSION,
            migrated_at: RUNTIME_SAVE_TIMESTAMP.to_string(),
            status: "completed".to_string(),
        }],
        base_ui_state: RuntimeBaseUiState::default(),
    }
}

fn validate_runtime_save_state_v1(save: &RuntimeSaveStateV1) -> std::io::Result<()> {
    if save.schema_version != RUNTIME_SAVE_V1_SCHEMA_VERSION
        || save.contract_id != RUNTIME_SAVE_V1_CONTRACT_ID
    {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "runtime save must use save-state-v1 schema_version 2",
        ));
    }
    if !save.data_controls.local_only_by_default || !save.data_controls.upload_requires_opt_in {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "runtime save must preserve local-only and upload opt-in controls",
        ));
    }
    if save.migration_history.is_empty() {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "runtime save-state-v1 requires migration_history",
        ));
    }
    Ok(())
}

fn build_runtime_save_state(
    cli: &RuntimeCli,
    privacy_settings: &RuntimePrivacySettings,
    progress: &MetaProgress,
) -> RuntimeSaveStateV1 {
    RuntimeSaveStateV1 {
        schema_version: RUNTIME_SAVE_V1_SCHEMA_VERSION,
        contract_id: RUNTIME_SAVE_V1_CONTRACT_ID.to_string(),
        save_id: DEFAULT_SAVE_ID.to_string(),
        profile_id: DEFAULT_PROFILE_ID.to_string(),
        created_at: RUNTIME_SAVE_TIMESTAMP.to_string(),
        updated_at: RUNTIME_SAVE_TIMESTAMP.to_string(),
        game_version: "prototype-v0".to_string(),
        ruleset_version: "prototype-v0".to_string(),
        content_pack_ids: cli.content_pack_ids.clone(),
        settings: privacy_settings.clone(),
        data_controls: RuntimeSaveDataControls::default(),
        meta_progress: progress.clone(),
        migration_history: vec![RuntimeSaveMigrationEntry {
            migration_id: RUNTIME_SAVE_MIGRATION_ID.to_string(),
            source_save_id: DEFAULT_SAVE_ID.to_string(),
            source_contract_id: RUNTIME_SAVE_V0_CONTRACT_ID.to_string(),
            source_schema_version: RUNTIME_SAVE_V0_SCHEMA_VERSION,
            target_contract_id: RUNTIME_SAVE_V1_CONTRACT_ID.to_string(),
            target_schema_version: RUNTIME_SAVE_V1_SCHEMA_VERSION,
            migrated_at: RUNTIME_SAVE_TIMESTAMP.to_string(),
            status: "completed".to_string(),
        }],
        base_ui_state: RuntimeBaseUiState::default(),
    }
}

fn write_runtime_save_state_from_v1(path: &Path, save: &RuntimeSaveStateV1) -> std::io::Result<()> {
    validate_runtime_save_state_v1(save)?;
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }
    let json = serde_json::to_string_pretty(save)?;
    fs::write(path, format!("{json}\n"))
}

fn write_runtime_save_state(
    path: &Path,
    cli: &RuntimeCli,
    privacy_settings: &RuntimePrivacySettings,
    progress: &MetaProgress,
) -> std::io::Result<()> {
    write_runtime_save_state_with_base_ui(path, cli, privacy_settings, progress, None)
}

fn write_runtime_save_state_with_base_ui(
    path: &Path,
    cli: &RuntimeCli,
    privacy_settings: &RuntimePrivacySettings,
    progress: &MetaProgress,
    base_ui_state: Option<&RuntimeBaseUiState>,
) -> std::io::Result<()> {
    let mut save = build_runtime_save_state(cli, privacy_settings, progress);
    if path.exists() {
        let existing = read_runtime_save_state(path)?;
        save.save_id = existing.state.save_id;
        save.profile_id = existing.state.profile_id;
        save.created_at = existing.state.created_at;
        save.game_version = existing.state.game_version;
        save.ruleset_version = existing.state.ruleset_version;
        save.content_pack_ids = existing.state.content_pack_ids;
        save.data_controls = existing.state.data_controls;
        save.migration_history = existing.state.migration_history;
        save.base_ui_state = existing.state.base_ui_state;
    }
    if let Some(base_ui_state) = base_ui_state {
        save.base_ui_state = base_ui_state.clone();
    }
    write_runtime_save_state_from_v1(path, &save)
}

fn persist_runtime_save_if_configured(state: &RuntimeState) -> std::io::Result<()> {
    let Some(path) = &state.save_file else {
        return Ok(());
    };
    let cli = RuntimeCli {
        content_pack_ids: state.content_pack_ids.clone(),
        ..RuntimeCli::default()
    };
    write_runtime_save_state_with_base_ui(
        path,
        &cli,
        &state.privacy_settings,
        &state.meta_progress,
        Some(&state.base_ui_state),
    )
}

fn export_runtime_save(
    cli: &RuntimeCli,
    privacy_settings: &RuntimePrivacySettings,
    output_path: &Path,
) -> std::io::Result<()> {
    let save = load_runtime_save_state(cli, privacy_settings)?;
    write_runtime_save_state_from_v1(output_path, &save)
}

fn delete_runtime_save(cli: &RuntimeCli) -> std::io::Result<()> {
    if !cli.explicit_save_file {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidInput,
            "delete save requires --save-file",
        ));
    }
    let Some(path) = &cli.save_file else {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidInput,
            "delete save requires --save-file",
        ));
    };
    if path.exists() {
        fs::remove_file(path)?;
    }
    Ok(())
}

fn runtime_can_upload(settings: &RuntimePrivacySettings, kind: RuntimeUploadKind) -> bool {
    match kind {
        RuntimeUploadKind::Telemetry => settings.telemetry_upload_enabled,
        RuntimeUploadKind::RawReplay => settings.raw_replay_upload_enabled,
        RuntimeUploadKind::CrashReport => settings.crash_report_upload_enabled,
    }
}

fn toggle_runtime_privacy_setting(
    settings: &mut RuntimePrivacySettings,
    kind: RuntimeUploadKind,
) -> bool {
    match kind {
        RuntimeUploadKind::Telemetry => {
            settings.telemetry_upload_enabled = !settings.telemetry_upload_enabled;
            settings.telemetry_upload_enabled
        }
        RuntimeUploadKind::RawReplay => {
            settings.raw_replay_upload_enabled = !settings.raw_replay_upload_enabled;
            settings.raw_replay_upload_enabled
        }
        RuntimeUploadKind::CrashReport => {
            settings.crash_report_upload_enabled = !settings.crash_report_upload_enabled;
            settings.crash_report_upload_enabled
        }
    }
}

fn runtime_upload_transport_enabled(settings: &RuntimePrivacySettings) -> bool {
    runtime_can_upload(settings, RuntimeUploadKind::Telemetry)
        || runtime_can_upload(settings, RuntimeUploadKind::RawReplay)
        || runtime_can_upload(settings, RuntimeUploadKind::CrashReport)
}

fn runtime_upload_kind_label(kind: RuntimeUploadKind) -> &'static str {
    match kind {
        RuntimeUploadKind::Telemetry => "telemetry upload",
        RuntimeUploadKind::RawReplay => "raw replay upload",
        RuntimeUploadKind::CrashReport => "crash report upload",
    }
}

fn runtime_privacy_notice(settings: &RuntimePrivacySettings) -> String {
    format!(
        "《软糖风暴》隐私说明\n\
遥测、Replay 和崩溃报告默认只保存在本机，用于平衡、崩溃分析和玩法改进。\n\
上传匿名遥测：{}；上传原始 Replay 输入：{}；上传崩溃报告：{}。\n\
上传功能必须由玩家明确开启，raw replay 需要单独同意；当前 Runtime 没有网络上传传输层。\n\
本地数据可以导出为 JSON，也可以删除。数据不应包含个人身份信息、IP 地址、文件路径或自由文本输入；默认保留 90 天。",
        on_off_label(settings.telemetry_upload_enabled),
        on_off_label(settings.raw_replay_upload_enabled),
        on_off_label(settings.crash_report_upload_enabled),
    )
}

fn on_off_label(enabled: bool) -> &'static str {
    if enabled {
        "已开启"
    } else {
        "关闭"
    }
}

fn export_runtime_local_data(
    cli: &RuntimeCli,
    privacy_settings: &RuntimePrivacySettings,
    output_path: &Path,
) -> std::io::Result<()> {
    let export = RuntimeLocalDataExport {
        kind: "runtime_local_data_export",
        export_version: 1,
        privacy_settings: privacy_settings.clone(),
        local_data_dirs: cli
            .local_data_dirs
            .iter()
            .map(|path| path.display().to_string())
            .collect(),
        files: collect_runtime_local_data_files(&cli.local_data_dirs)?,
    };
    if let Some(parent) = output_path.parent() {
        fs::create_dir_all(parent)?;
    }
    let json = serde_json::to_string_pretty(&export)?;
    fs::write(output_path, format!("{json}\n"))
}

fn collect_runtime_local_data_files(
    roots: &[PathBuf],
) -> std::io::Result<Vec<RuntimeLocalDataFile>> {
    let mut files = Vec::new();
    for root in roots {
        collect_runtime_local_data_from_root(root, root, &mut files)?;
    }
    files.sort_by(|left, right| {
        (&left.root, &left.relative_path).cmp(&(&right.root, &right.relative_path))
    });
    Ok(files)
}

fn collect_runtime_local_data_from_root(
    root: &Path,
    current: &Path,
    files: &mut Vec<RuntimeLocalDataFile>,
) -> std::io::Result<()> {
    if !current.exists() {
        return Ok(());
    }
    if current.is_file() {
        let contents = fs::read_to_string(current)?;
        files.push(RuntimeLocalDataFile {
            root: root.display().to_string(),
            relative_path: relative_path_string(root, current),
            encoding: "utf-8",
            contents,
        });
        return Ok(());
    }
    if !current.is_dir() {
        return Ok(());
    }

    for entry in fs::read_dir(current)? {
        let entry = entry?;
        collect_runtime_local_data_from_root(root, &entry.path(), files)?;
    }
    Ok(())
}

fn delete_runtime_local_data(cli: &RuntimeCli) -> std::io::Result<RuntimeLocalDataDeleteReport> {
    if cli.explicit_local_data_dirs.is_empty() {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidInput,
            "delete requires at least one explicit --local-data-dir",
        ));
    }

    let mut report = RuntimeLocalDataDeleteReport {
        kind: "runtime_local_data_delete_report",
        deleted_files: 0,
        deleted_dirs: 0,
        skipped_missing_roots: Vec::new(),
        local_data_dirs: cli
            .explicit_local_data_dirs
            .iter()
            .map(|path| path.display().to_string())
            .collect(),
    };

    for root in &cli.explicit_local_data_dirs {
        if !root.exists() {
            report
                .skipped_missing_roots
                .push(root.display().to_string());
            continue;
        }
        delete_runtime_local_data_root(root, &mut report)?;
    }

    Ok(report)
}

fn delete_runtime_local_data_root(
    root: &Path,
    report: &mut RuntimeLocalDataDeleteReport,
) -> std::io::Result<()> {
    if root.is_file() {
        fs::remove_file(root)?;
        report.deleted_files += 1;
        return Ok(());
    }
    if !root.is_dir() {
        return Ok(());
    }

    for entry in fs::read_dir(root)? {
        let entry = entry?;
        let path = entry.path();
        if path.is_dir() {
            delete_runtime_local_data_root(&path, report)?;
            if fs::read_dir(&path)?.next().is_none() {
                fs::remove_dir(&path)?;
                report.deleted_dirs += 1;
            }
        } else if path.is_file() {
            fs::remove_file(&path)?;
            report.deleted_files += 1;
        }
    }
    Ok(())
}

fn runtime_save_export_path(platform_data_root: &Path) -> PathBuf {
    platform_data_root
        .join(PLATFORM_EXPORT_ROOT)
        .join(RUNTIME_SAVE_EXPORT_FILE_NAME)
}

fn runtime_local_data_export_path(platform_data_root: &Path) -> PathBuf {
    platform_data_root
        .join(PLATFORM_EXPORT_ROOT)
        .join(RUNTIME_LOCAL_DATA_EXPORT_FILE_NAME)
}

impl RuntimeDataControlContext {
    fn from_state(state: &RuntimeState) -> Self {
        Self {
            platform_data_root: state.platform_data_root.clone(),
            runtime_settings_file: state.runtime_settings_file.clone(),
            save_file: state.save_file.clone(),
            local_data_dirs: state.local_data_dirs.clone(),
            content_pack_ids: state.content_pack_ids.clone(),
            privacy_settings: state.privacy_settings.clone(),
        }
    }

    fn cli(&self, explicit_save_file: bool, explicit_local_data_dirs: bool) -> RuntimeCli {
        RuntimeCli {
            platform_data_root: self.platform_data_root.clone(),
            runtime_settings_file: self.runtime_settings_file.clone(),
            save_file: self.save_file.clone(),
            explicit_save_file,
            local_data_dirs: self.local_data_dirs.clone(),
            explicit_local_data_dirs: if explicit_local_data_dirs {
                self.local_data_dirs.clone()
            } else {
                Vec::new()
            },
            content_pack_ids: self.content_pack_ids.clone(),
            ..RuntimeCli::default()
        }
    }
}

fn run_runtime_data_control_action(
    context: &RuntimeDataControlContext,
    action: RuntimeDataControlAction,
) -> std::io::Result<String> {
    match action {
        RuntimeDataControlAction::ExportSave => {
            let output_path = runtime_save_export_path(&context.platform_data_root);
            export_runtime_save(
                &context.cli(false, false),
                &context.privacy_settings,
                &output_path,
            )?;
            Ok(format!("exported save {}", output_path.display()))
        }
        RuntimeDataControlAction::DeleteSave => {
            let save_file = context
                .save_file
                .as_ref()
                .map(|path| path.display().to_string())
                .unwrap_or_else(|| "<missing>".to_string());
            delete_runtime_save(&context.cli(true, false))?;
            Ok(format!("deleted save {save_file}"))
        }
        RuntimeDataControlAction::ExportLocalData => {
            let output_path = runtime_local_data_export_path(&context.platform_data_root);
            export_runtime_local_data(
                &context.cli(false, false),
                &context.privacy_settings,
                &output_path,
            )?;
            Ok(format!("exported local data {}", output_path.display()))
        }
        RuntimeDataControlAction::DeleteLocalData => {
            let report = delete_runtime_local_data(&context.cli(false, true))?;
            Ok(format!(
                "deleted local data {} files {} dirs",
                report.deleted_files, report.deleted_dirs
            ))
        }
    }
}

fn runtime_data_control_requires_confirmation(action: RuntimeDataControlAction) -> bool {
    matches!(
        action,
        RuntimeDataControlAction::DeleteSave | RuntimeDataControlAction::DeleteLocalData
    )
}

fn runtime_data_control_confirmation_message(action: RuntimeDataControlAction) -> &'static str {
    match action {
        RuntimeDataControlAction::DeleteSave => "confirm delete save: press X again",
        RuntimeDataControlAction::DeleteLocalData => "confirm delete local data: press K again",
        RuntimeDataControlAction::ExportSave | RuntimeDataControlAction::ExportLocalData => {
            "no confirmation required"
        }
    }
}

fn run_runtime_data_control_action_from_state(
    state: &mut RuntimeState,
    action: RuntimeDataControlAction,
) -> std::io::Result<String> {
    if !runtime_data_control_requires_confirmation(action) {
        state.pending_data_delete_action = None;
        return run_runtime_data_control_action(
            &RuntimeDataControlContext::from_state(state),
            action,
        );
    }

    if state.pending_data_delete_action != Some(action) {
        state.pending_data_delete_action = Some(action);
        return Ok(runtime_data_control_confirmation_message(action).to_string());
    }

    state.pending_data_delete_action = None;
    run_runtime_data_control_action(&RuntimeDataControlContext::from_state(state), action)
}

fn relative_path_string(root: &Path, path: &Path) -> String {
    path.strip_prefix(root)
        .unwrap_or(path)
        .display()
        .to_string()
}

fn resolve_runtime_content_selection(mut cli: RuntimeCli) -> Result<RuntimeCli, String> {
    let Some(lock_file) = cli.accepted_lock_file.clone() else {
        return Ok(cli);
    };
    let text = fs::read_to_string(&lock_file)
        .map_err(|error| format!("failed to read `{}`: {error}", lock_file.display()))?;
    let lock = serde_json::from_str::<AcceptedContentLockFile>(&text)
        .map_err(|error| format!("failed to parse `{}`: {error}", lock_file.display()))?;
    if lock.status != "locked" {
        return Err(format!(
            "accepted content lock `{}` has status `{}`",
            lock_file.display(),
            lock.status
        ));
    }

    let locked_entries = lock
        .entries
        .iter()
        .filter(|entry| entry.status == "locked")
        .collect::<Vec<_>>();
    let selected = if let Some(requested_id) = &cli.accepted_content_id {
        locked_entries
            .iter()
            .find(|entry| entry.id == requested_id.as_str())
            .copied()
            .ok_or_else(|| {
                format!(
                    "accepted content id `{requested_id}` is not locked in `{}`",
                    lock_file.display()
                )
            })?
    } else if locked_entries.len() == 1 {
        locked_entries[0]
    } else {
        return Err(format!(
            "accepted content lock `{}` has {} locked entries; pass --accepted-content-id",
            lock_file.display(),
            locked_entries.len()
        ));
    };
    if selected.content_hash.as_deref().unwrap_or("").is_empty() {
        return Err(format!(
            "accepted content id `{}` is locked without content_hash",
            selected.id
        ));
    }

    cli.content_dir = PathBuf::from(&selected.runtime_content_dir);
    cli.accepted_content_id = Some(selected.id.clone());
    cli.content_pack_ids = vec![selected.id.clone()];
    Ok(cli)
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
            frame_metrics: RuntimeFrameMetricsState::default(),
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

    fn record_frame(&mut self, frame_seconds: f32) {
        if !self.enabled() || !frame_seconds.is_finite() || frame_seconds <= 0.0 {
            return;
        }
        self.frame_metrics
            .record_frame(frame_seconds.min(MAX_PROFILED_FRAME_SECONDS));
    }

    fn reset_for_next_run(&mut self) {
        self.next_sample_seconds = 0.0;
        self.event_counts = RuntimeEventCounts::default();
        self.samples.clear();
        self.frame_metrics = RuntimeFrameMetricsState::default();
        self.finished = false;
    }
}

impl RuntimeFrameMetricsState {
    fn record_frame(&mut self, frame_seconds: f32) {
        self.frame_count += 1;
        self.total_frame_seconds += frame_seconds;
        self.min_frame_seconds = Some(
            self.min_frame_seconds
                .map_or(frame_seconds, |current| current.min(frame_seconds)),
        );
        self.max_frame_seconds = self.max_frame_seconds.max(frame_seconds);
        if frame_seconds > 1.0 / 45.0 {
            self.slow_frame_count_45fps += 1;
        }
        if frame_seconds > 1.0 / 30.0 {
            self.slow_frame_count_30fps += 1;
        }
    }
}

impl RuntimeEventCounts {
    fn observe(&mut self, events: &[GameEvent]) {
        for event in events {
            match event {
                GameEvent::EnemySpawned { .. } => self.enemy_spawned += 1,
                GameEvent::BossSpawned { .. } => self.boss_spawned += 1,
                GameEvent::BossPhaseChanged { .. } => self.boss_phase_changed += 1,
                GameEvent::BossAbilityUsed { .. } => self.boss_ability_used += 1,
                GameEvent::WeaponFired { .. } => self.weapon_fired += 1,
                GameEvent::EnemyHit { .. } => self.enemy_hit += 1,
                GameEvent::EnemyKilled { .. } => self.enemy_killed += 1,
                GameEvent::XpDropped { .. } => self.xp_dropped += 1,
                GameEvent::XpCollected { .. } => self.xp_collected += 1,
                GameEvent::LevelUp { .. } => self.level_up += 1,
                GameEvent::UpgradeOffered { .. } => self.upgrade_offered += 1,
                GameEvent::UpgradeChosen { .. } => self.upgrade_chosen += 1,
                GameEvent::PlayerDamaged { .. } => self.player_damaged += 1,
                GameEvent::ContentEventTriggered { .. } => self.content_event_triggered += 1,
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
            active_hazards: snapshot.active_hazards.len(),
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
            frame_metrics: RuntimeFrameMetricsReport::from_state(&state.capture.frame_metrics),
            event_counts: state.capture.event_counts.clone(),
            samples: state.capture.samples.clone(),
            final_metrics: RuntimeMetricsReport::from_metrics(metrics),
            privacy: RuntimePrivacyReport::from_settings(&state.privacy_settings),
            manual_review: RuntimeManualReviewTemplate::default_for_runtime(),
        }
    }
}

impl RuntimePrivacyReport {
    fn from_settings(settings: &RuntimePrivacySettings) -> Self {
        Self {
            telemetry_upload_enabled: settings.telemetry_upload_enabled,
            raw_replay_upload_enabled: settings.raw_replay_upload_enabled,
            crash_report_upload_enabled: settings.crash_report_upload_enabled,
            local_capture_only: !runtime_upload_transport_enabled(settings),
            upload_transport: "not_implemented",
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

impl RuntimeFrameMetricsReport {
    fn from_state(state: &RuntimeFrameMetricsState) -> Self {
        let average_frame_seconds = if state.frame_count > 0 {
            state.total_frame_seconds / state.frame_count as f32
        } else {
            0.0
        };
        Self {
            frame_count: state.frame_count,
            total_frame_seconds: state.total_frame_seconds,
            average_frame_seconds,
            average_fps: fps_from_frame_seconds(average_frame_seconds),
            min_frame_seconds: state.min_frame_seconds.unwrap_or(0.0),
            max_frame_seconds: state.max_frame_seconds,
            worst_frame_fps: fps_from_frame_seconds(state.max_frame_seconds),
            slow_frame_count_45fps: state.slow_frame_count_45fps,
            slow_frame_count_30fps: state.slow_frame_count_30fps,
        }
    }
}

fn fps_from_frame_seconds(frame_seconds: f32) -> f32 {
    if frame_seconds > 0.0 {
        1.0 / frame_seconds
    } else {
        0.0
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
        apply_runtime_chapter_action, collect_runtime_local_data_files, delete_runtime_local_data,
        demo_movement, demo_upgrade_choice, describe_events, effects_for_events,
        event_kind_for_events, export_runtime_local_data, format_boss_status, format_build_status,
        format_enemy_swarm_status, format_hazard_status, format_terminal_overlay,
        format_upgrade_options, load_runtime_asset_candidate_manifest,
        load_runtime_privacy_settings, load_runtime_story_codex_ui_candidate_manifest,
        make_tone_wav, map_visual_style, movement_from_gamepad_axes, movement_from_gamepad_buttons,
        next_runtime_selection_id, parse_runtime_cli, persist_runtime_privacy_settings_file,
        player_tint, render_meta_progress_panel, resolve_runtime_content_selection,
        resolve_runtime_platform_paths, run_config_from_cli, run_runtime_data_control_action,
        run_runtime_data_control_action_from_state, runtime_asset_root, runtime_can_upload,
        runtime_chapter_action_from_gamepad, runtime_chapter_action_from_keyboard,
        runtime_chapter_action_from_pointer, runtime_chapter_action_from_pointer_zone,
        runtime_character_starting_loadout, runtime_codex_action_from_gamepad,
        runtime_codex_action_from_pointer, runtime_codex_action_from_pointer_zone,
        runtime_loadout_action_from_gamepad, runtime_loadout_action_from_keyboard,
        runtime_loadout_action_from_pointer, runtime_loadout_action_from_pointer_zone,
        runtime_local_data_export_path, runtime_meta_panel_tab_view_from_pointer,
        runtime_meta_panel_tab_view_from_pointer_zone, runtime_meta_panel_view_from_key,
        runtime_native_platform_data_root_for_env, runtime_overview_view_from_pointer,
        runtime_overview_view_from_pointer_zone, runtime_privacy_notice, runtime_save_export_path,
        runtime_settings_action_from_keyboard, runtime_settings_action_from_pointer,
        runtime_settings_action_from_pointer_zone, runtime_sprite_paths,
        runtime_unlocked_character_ids, runtime_unlocked_map_ids, sounds_for_events,
        toggle_runtime_privacy_setting, unlock_runtime_content_for_session,
        upgrade_choice_from_gamepad, upgrade_choice_from_pointer, upgrade_choice_from_pointer_zone,
        write_runtime_privacy_settings, write_runtime_save_state,
        write_runtime_save_state_with_base_ui, RuntimeAssetCandidateItem,
        RuntimeAssetCandidateManifest, RuntimeAssetCandidateRules, RuntimeBaseUiState,
        RuntimeCaptureState, RuntimeChapterAction, RuntimeCli, RuntimeCodexAction,
        RuntimeCodexCategory, RuntimeDataControlAction, RuntimeDataControlContext,
        RuntimeEffectKind, RuntimeEventCounts, RuntimeEventKind, RuntimeFrameMetricsReport,
        RuntimeFrameMetricsState, RuntimeLoadoutAction, RuntimeMetaPanelRenderContext,
        RuntimeMetaPanelView, RuntimePrivacyReport, RuntimePrivacySettings,
        RuntimeSaveDataControls, RuntimeSaveStateV0, RuntimeSettingsAction, RuntimeSound,
        RuntimeState, RuntimeStoryCodexUiCandidateManifest, RuntimeStoryCodexUiCandidateRules,
        RuntimeUploadKind, DEFAULT_CONTENT_DIR, DEFAULT_MAP_ID, DEFAULT_PLATFORM_DATA_ROOT,
        DEFAULT_PROFILE_ID, DEFAULT_SAVE_ID, MAX_PROFILED_FRAME_SECONDS,
        PLATFORM_CRASH_REPORT_ROOT, PLATFORM_REPLAY_ROOT, PLATFORM_SAVE_ROOT,
        PLATFORM_SETTINGS_ROOT, PLATFORM_TELEMETRY_ROOT, RUNTIME_SAVE_TIMESTAMP,
        RUNTIME_SAVE_V0_CONTRACT_ID, RUNTIME_SAVE_V0_SCHEMA_VERSION,
    };
    use bevy::prelude::{
        Axis, ButtonInput, Gamepad, GamepadAxis, GamepadAxisType, GamepadButton, GamepadButtonType,
        KeyCode, MouseButton, Vec2,
    };
    use game_core::{
        BossSnapshot, BuildItemSnapshot, BuildSnapshot, ContentPack, EnemyBehavior, EnemySnapshot,
        FixedDt, GameCore, GameEvent, HazardSnapshot, MetaProgress, MetaRunSummary, PickupSnapshot,
        PickupType, RunConfig, RunMode, StatusEffectSnapshot, TerminalKind, TerminalState,
        Vec2 as CoreVec2,
    };
    use std::{collections::BTreeMap, fs, path::PathBuf};

    #[allow(clippy::too_many_arguments)]
    fn meta_panel_context<'a>(
        privacy_settings: &'a RuntimePrivacySettings,
        runtime_settings_file: Option<&'a std::path::Path>,
        story_codex_ui_candidate: Option<&'a RuntimeStoryCodexUiCandidateManifest>,
        asset_runtime_candidate: Option<&'a RuntimeAssetCandidateManifest>,
        content: &'a ContentPack,
        config: &'a RunConfig,
        base_ui_state: &'a RuntimeBaseUiState,
        codex_selected_index: usize,
    ) -> RuntimeMetaPanelRenderContext<'a> {
        RuntimeMetaPanelRenderContext {
            privacy_settings,
            runtime_settings_file,
            story_codex_ui_candidate,
            asset_runtime_candidate,
            content,
            config,
            base_ui_state,
            codex_selected_index,
        }
    }

    fn runtime_state_for_tests() -> RuntimeState {
        let cli = RuntimeCli {
            runtime_settings_file: None,
            save_file: None,
            local_data_dirs: Vec::new(),
            ..RuntimeCli::default()
        };
        let content = ContentPack::base_demo();
        let config = run_config_from_cli(&cli, &content);
        let core = GameCore::reset_with_content(config.clone(), content.clone())
            .expect("base demo content should initialize Runtime tests");
        let latest_snapshot = core.snapshot();
        let dt = FixedDt::from_tick_rate(config.tick_rate);
        let dt_seconds = dt.seconds();
        RuntimeState {
            content,
            content_dir: cli.content_dir.clone(),
            content_pack_ids: cli.content_pack_ids.clone(),
            config,
            core,
            dt,
            dt_seconds,
            accumulator: 0.0,
            latest_snapshot,
            last_event: "run started".to_string(),
            last_event_kind: RuntimeEventKind::System,
            pending_sounds: Vec::new(),
            effects: Vec::new(),
            capture: RuntimeCaptureState::from_cli(&cli),
            demo_input: cli.demo_input,
            simulation_speed: cli.simulation_speed,
            auto_exit_after_report: cli.auto_exit_after_report,
            paused: false,
            run_number: 1,
            privacy_settings: RuntimePrivacySettings::default(),
            platform_data_root: cli.platform_data_root.clone(),
            runtime_settings_file: cli.runtime_settings_file.clone(),
            save_file: cli.save_file.clone(),
            local_data_dirs: cli.local_data_dirs.clone(),
            pending_data_delete_action: None,
            meta_panel_view: RuntimeMetaPanelView::Overview,
            base_ui_state: RuntimeBaseUiState::default(),
            codex_selected_index: 0,
            meta_progress: MetaProgress::demo_start(),
            story_codex_ui_candidate: None,
            asset_runtime_candidate: None,
            last_meta_settlement: None,
            settled_run_number: None,
        }
    }

    #[test]
    fn parses_runtime_cli_overrides() {
        let cli = parse_runtime_cli([
            "--content-dir".to_string(),
            "content/custom".to_string(),
            "--character-id".to_string(),
            "bubble-courier".to_string(),
            "--seed".to_string(),
            "9".to_string(),
            "--map-id".to_string(),
            "soda-creek".to_string(),
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
        assert_eq!(cli.character_id, "bubble-courier");
        assert_eq!(cli.seed, 9);
        assert_eq!(cli.map_id, "soda-creek");
        assert_eq!(cli.seconds, 120.0);
        assert_eq!(cli.tick_rate, 20);
        assert!(cli.demo_input);
        assert_eq!(cli.simulation_speed, 4.0);
        assert!(cli.auto_exit_after_report);
    }

    #[test]
    fn runtime_meta_panel_view_restores_from_base_ui_key() {
        assert_eq!(
            runtime_meta_panel_view_from_key("codex"),
            RuntimeMetaPanelView::Codex
        );
        assert_eq!(
            runtime_meta_panel_view_from_key("loadout"),
            RuntimeMetaPanelView::Loadout
        );
        assert_eq!(
            runtime_meta_panel_view_from_key("unknown"),
            RuntimeMetaPanelView::Overview
        );
    }

    #[test]
    fn parses_runtime_accepted_content_lock_options() {
        let cli = parse_runtime_cli([
            "--accepted-lock-file".to_string(),
            "harness/accepted_content/accepted_content.lock.json".to_string(),
            "--accepted-content-id".to_string(),
            "base-demo-smoke".to_string(),
        ]);

        assert_eq!(
            cli.accepted_lock_file,
            Some(PathBuf::from(
                "harness/accepted_content/accepted_content.lock.json"
            ))
        );
        assert_eq!(cli.accepted_content_id, Some("base-demo-smoke".to_string()));
    }

    #[test]
    fn parses_story_codex_ui_candidate_manifest_option() {
        let cli = parse_runtime_cli([
            "--story-codex-ui-candidate-manifest".to_string(),
            "harness/story_review/ui_candidates/example/ui_candidate_manifest.json".to_string(),
        ]);

        assert_eq!(
            cli.story_codex_ui_candidate_manifest,
            Some(PathBuf::from(
                "harness/story_review/ui_candidates/example/ui_candidate_manifest.json"
            ))
        );
    }

    #[test]
    fn parses_asset_runtime_candidate_manifest_option() {
        let cli = parse_runtime_cli([
            "--asset-runtime-candidate-manifest".to_string(),
            "harness/asset_review/runtime_candidates/example/runtime_candidate_manifest.json"
                .to_string(),
        ]);

        assert_eq!(
            cli.asset_runtime_candidate_manifest,
            Some(PathBuf::from(
                "harness/asset_review/runtime_candidates/example/runtime_candidate_manifest.json"
            ))
        );
    }

    #[test]
    fn loads_story_codex_ui_candidate_manifest_metadata_only() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-story-codex-runtime-manifest-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(&root).unwrap();
        let manifest_path = root.join("ui_candidate_manifest.json");
        fs::write(
            &manifest_path,
            r#"{
  "manifest_version": 1,
  "manifest_contract_id": "story-codex-ui-candidate-manifest-v0",
  "stage": "story_codex_ui_candidate",
  "candidate_pack_id": "2026-05-26_story_codex_seed_pack",
  "promoted_at": "2026-05-26T00:00:00Z",
  "source_candidate_pack": "harness/generated_candidates/2026-05-26_story_codex_seed_pack",
  "manual_review_file": "harness/story_review/ui_candidates/2026-05-26_story_codex_seed_pack/manual_review.json",
  "manual_gate_decision": "ui_candidate",
  "candidate_validation_report": "harness/reports/2026-05-26_story_codex_candidate_validation_001/summary.md",
  "chapter_count": 6,
  "codex_entry_count": 26,
  "rules": {
    "accepted_content": false,
    "runtime_integrated": false,
    "requires_runtime_ui_review": true,
    "requires_final_human_acceptance": true
  }
}
"#,
        )
        .unwrap();

        let manifest = load_runtime_story_codex_ui_candidate_manifest(&RuntimeCli {
            story_codex_ui_candidate_manifest: Some(manifest_path),
            ..RuntimeCli::default()
        })
        .unwrap()
        .unwrap();

        let _ = fs::remove_dir_all(&root);
        assert_eq!(
            manifest.candidate_pack_id,
            "2026-05-26_story_codex_seed_pack"
        );
        assert_eq!(manifest.chapter_count, 6);
        assert_eq!(manifest.codex_entry_count, 26);
        assert!(!manifest.rules.accepted_content);
        assert!(!manifest.rules.runtime_integrated);
    }

    #[test]
    fn loads_asset_runtime_candidate_manifest_metadata_only() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-asset-runtime-manifest-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(&root).unwrap();
        let manifest_path = root.join("runtime_candidate_manifest.json");
        fs::write(
            &manifest_path,
            r#"{
  "manifest_version": 1,
  "manifest_contract_id": "asset-runtime-candidate-manifest-v0",
  "stage": "asset_runtime_candidate",
  "candidate_batch_id": "2026-05-26_mmx_runtime_topdown_audio_plan",
  "promoted_at": "2026-05-26T00:00:00Z",
  "source_candidate_batch": "asset/generated_candidates/2026-05-26_mmx_runtime_topdown_audio_plan",
  "manual_review_file": "harness/asset_review/runtime_candidates/2026-05-26_mmx_runtime_topdown_audio_plan/manual_review.json",
  "manual_gate_decision": "asset_candidate",
  "candidate_metadata_report": "harness/reports/2026-05-26_mmx_runtime_topdown_audio_plan_metadata_001/summary.md",
  "asset_count": 2,
  "assets": [
    {
      "id": "player_jar_keeper_topdown_v005_001",
      "type": "image",
      "path": "images/player_jar_keeper_topdown_v005_001.png",
      "qa_status": "needs_visual_review",
      "allowed_candidate_uses": ["runtime_preview_candidate"]
    },
    {
      "id": "voice_boss_arrival_cn_v002",
      "type": "audio",
      "path": "audio/voice_boss_arrival_cn_v002.wav",
      "qa_status": "needs_audio_review",
      "allowed_candidate_uses": ["runtime_preview_candidate"]
    }
  ],
  "rules": {
    "accepted_content": false,
    "runtime_integrated": false,
    "release_ready": false,
    "requires_runtime_preview": true,
    "requires_audio_loudness_review": true,
    "requires_final_human_acceptance": true
  }
}
"#,
        )
        .unwrap();

        let manifest = load_runtime_asset_candidate_manifest(&RuntimeCli {
            asset_runtime_candidate_manifest: Some(manifest_path),
            ..RuntimeCli::default()
        })
        .unwrap()
        .unwrap();

        let _ = fs::remove_dir_all(&root);
        assert_eq!(
            manifest.candidate_batch_id,
            "2026-05-26_mmx_runtime_topdown_audio_plan"
        );
        assert_eq!(manifest.asset_count, 2);
        assert_eq!(manifest.assets.len(), 2);
        assert!(!manifest.rules.accepted_content);
        assert!(!manifest.rules.runtime_integrated);
        assert!(!manifest.rules.release_ready);
    }

    #[test]
    fn rejects_runtime_integrated_story_codex_ui_candidate_manifest() {
        let manifest = RuntimeStoryCodexUiCandidateManifest {
            manifest_contract_id: "story-codex-ui-candidate-manifest-v0".to_string(),
            stage: "story_codex_ui_candidate".to_string(),
            candidate_pack_id: "candidate".to_string(),
            manual_gate_decision: "ui_candidate".to_string(),
            chapter_count: 1,
            codex_entry_count: 1,
            rules: RuntimeStoryCodexUiCandidateRules {
                accepted_content: false,
                runtime_integrated: true,
                requires_runtime_ui_review: true,
                requires_final_human_acceptance: true,
            },
        };

        let error =
            super::validate_runtime_story_codex_ui_candidate_manifest(&manifest).unwrap_err();

        assert_eq!(error.kind(), std::io::ErrorKind::InvalidData);
        assert!(error.to_string().contains("runtime_integrated=false"));
    }

    #[test]
    fn rejects_integrated_asset_runtime_candidate_manifest() {
        let manifest = RuntimeAssetCandidateManifest {
            manifest_contract_id: "asset-runtime-candidate-manifest-v0".to_string(),
            stage: "asset_runtime_candidate".to_string(),
            candidate_batch_id: "candidate".to_string(),
            manual_gate_decision: "asset_candidate".to_string(),
            asset_count: 1,
            assets: vec![RuntimeAssetCandidateItem {
                id: "player".to_string(),
                asset_type: "image".to_string(),
                qa_status: "needs_visual_review".to_string(),
                allowed_candidate_uses: vec!["runtime_preview_candidate".to_string()],
            }],
            rules: RuntimeAssetCandidateRules {
                accepted_content: false,
                runtime_integrated: true,
                release_ready: false,
                requires_runtime_preview: true,
                requires_audio_loudness_review: true,
                requires_final_human_acceptance: true,
            },
        };

        let error = super::validate_runtime_asset_candidate_manifest(&manifest).unwrap_err();

        assert_eq!(error.kind(), std::io::ErrorKind::InvalidData);
        assert!(error.to_string().contains("runtime_integrated=false"));
    }

    #[test]
    fn rejects_asset_runtime_candidate_with_release_use() {
        let manifest = RuntimeAssetCandidateManifest {
            manifest_contract_id: "asset-runtime-candidate-manifest-v0".to_string(),
            stage: "asset_runtime_candidate".to_string(),
            candidate_batch_id: "candidate".to_string(),
            manual_gate_decision: "asset_candidate".to_string(),
            asset_count: 1,
            assets: vec![RuntimeAssetCandidateItem {
                id: "player".to_string(),
                asset_type: "image".to_string(),
                qa_status: "needs_visual_review".to_string(),
                allowed_candidate_uses: vec!["release_ready".to_string()],
            }],
            rules: RuntimeAssetCandidateRules {
                accepted_content: false,
                runtime_integrated: false,
                release_ready: false,
                requires_runtime_preview: true,
                requires_audio_loudness_review: true,
                requires_final_human_acceptance: true,
            },
        };

        let error = super::validate_runtime_asset_candidate_manifest(&manifest).unwrap_err();

        assert_eq!(error.kind(), std::io::ErrorKind::InvalidData);
        assert!(error.to_string().contains("candidate-only stages"));
    }

    #[test]
    fn resolves_runtime_content_from_single_locked_entry() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-lock-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(&root).unwrap();
        let lock_file = root.join("accepted_content.lock.json");
        fs::write(
            &lock_file,
            r#"{
  "status": "locked",
  "entries": [
    {
      "id": "base-demo-smoke",
      "runtime_content_dir": "/tmp/base-demo-smoke",
      "status": "locked",
      "content_hash": "fnv1a64:example"
    }
  ]
}
"#,
        )
        .unwrap();

        let cli = resolve_runtime_content_selection(RuntimeCli {
            accepted_lock_file: Some(lock_file),
            ..RuntimeCli::default()
        })
        .unwrap();

        let _ = fs::remove_dir_all(&root);
        assert_eq!(cli.content_dir, PathBuf::from("/tmp/base-demo-smoke"));
        assert_eq!(cli.content_pack_ids, ["base-demo-smoke"]);
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
    fn runtime_frame_metrics_report_tracks_slow_frames() {
        let mut state = RuntimeFrameMetricsState::default();
        state.record_frame(1.0 / 60.0);
        state.record_frame(1.0 / 30.0);
        state.record_frame(0.05);

        let report = RuntimeFrameMetricsReport::from_state(&state);

        assert_eq!(report.frame_count, 3);
        assert!((report.average_fps - 30.0).abs() < 0.01);
        assert!((report.worst_frame_fps - 20.0).abs() < 0.01);
        assert_eq!(report.slow_frame_count_45fps, 2);
        assert_eq!(report.slow_frame_count_30fps, 1);
    }

    #[test]
    fn capture_frame_metrics_ignores_zero_and_caps_outliers() {
        let mut capture = RuntimeCaptureState::from_cli(&RuntimeCli {
            playtest_report: Some(PathBuf::from("harness/telemetry/local/report.json")),
            ..RuntimeCli::default()
        });

        capture.record_frame(0.0);
        capture.record_frame(1.0 / 60.0);
        capture.record_frame(0.25);

        let report = RuntimeFrameMetricsReport::from_state(&capture.frame_metrics);

        assert_eq!(report.frame_count, 2);
        assert!((report.max_frame_seconds - MAX_PROFILED_FRAME_SECONDS).abs() < 0.001);
        assert!((report.worst_frame_fps - 10.0).abs() < 0.01);
    }

    #[test]
    fn parses_runtime_privacy_and_data_control_options() {
        let cli = parse_runtime_cli([
            "--runtime-settings-file".to_string(),
            "harness/telemetry/local/runtime_settings.json".to_string(),
            "--local-data-dir".to_string(),
            "tmp/runtime-data".to_string(),
            "--export-local-data".to_string(),
            "tmp/export.json".to_string(),
            "--delete-local-data".to_string(),
            "--print-privacy-notice".to_string(),
        ]);

        assert_eq!(
            cli.runtime_settings_file,
            Some(PathBuf::from(
                "harness/telemetry/local/runtime_settings.json"
            ))
        );
        assert!(cli
            .local_data_dirs
            .contains(&PathBuf::from(DEFAULT_PLATFORM_DATA_ROOT).join(PLATFORM_TELEMETRY_ROOT)));
        assert!(cli
            .local_data_dirs
            .contains(&PathBuf::from(DEFAULT_PLATFORM_DATA_ROOT).join(PLATFORM_REPLAY_ROOT)));
        assert!(cli
            .local_data_dirs
            .contains(&PathBuf::from("tmp/runtime-data")));
        assert_eq!(
            cli.explicit_local_data_dirs,
            [PathBuf::from("tmp/runtime-data")]
        );
        assert_eq!(
            cli.export_local_data,
            Some(PathBuf::from("tmp/export.json"))
        );
        assert!(cli.delete_local_data);
        assert!(cli.print_privacy_notice);
    }

    #[test]
    fn runtime_platform_paths_follow_policy_roots() {
        let paths = resolve_runtime_platform_paths("platform_user_data/soft-candy-storm");

        assert_eq!(
            paths.save_file,
            PathBuf::from("platform_user_data/soft-candy-storm")
                .join(PLATFORM_SAVE_ROOT)
                .join("profile.json")
        );
        assert_eq!(
            paths.runtime_settings_file,
            PathBuf::from("platform_user_data/soft-candy-storm")
                .join(PLATFORM_SETTINGS_ROOT)
                .join("runtime_privacy_settings.json")
        );
        assert_eq!(
            paths.local_telemetry_dir,
            PathBuf::from("platform_user_data/soft-candy-storm").join(PLATFORM_TELEMETRY_ROOT)
        );
        assert_eq!(
            paths.local_replay_dir,
            PathBuf::from("platform_user_data/soft-candy-storm").join(PLATFORM_REPLAY_ROOT)
        );
        assert_eq!(
            paths.crash_report_dir,
            PathBuf::from("platform_user_data/soft-candy-storm").join(PLATFORM_CRASH_REPORT_ROOT)
        );
    }

    #[test]
    fn runtime_native_platform_data_root_uses_os_data_dirs() {
        assert_eq!(
            runtime_native_platform_data_root_for_env(
                "macos",
                Some(PathBuf::from("/Users/player")),
                None,
                None,
            ),
            Some(PathBuf::from(
                "/Users/player/Library/Application Support/Soft Candy Storm"
            ))
        );
        assert_eq!(
            runtime_native_platform_data_root_for_env(
                "windows",
                Some(PathBuf::from("C:/Users/player")),
                Some(PathBuf::from("/xdg")),
                Some(PathBuf::from("C:/Users/player/AppData/Roaming")),
            ),
            Some(PathBuf::from(
                "C:/Users/player/AppData/Roaming/Soft Candy Storm"
            ))
        );
        assert_eq!(
            runtime_native_platform_data_root_for_env(
                "linux",
                Some(PathBuf::from("/home/player")),
                Some(PathBuf::from("/home/player/.local/share")),
                None,
            ),
            Some(PathBuf::from("/home/player/.local/share/soft-candy-storm"))
        );
        assert_eq!(
            runtime_native_platform_data_root_for_env("linux", None, None, None),
            None
        );
    }

    #[test]
    fn runtime_cli_defaults_use_platform_data_roots() {
        let cli = RuntimeCli::default();

        assert_eq!(
            cli.platform_data_root,
            PathBuf::from(DEFAULT_PLATFORM_DATA_ROOT)
        );
        assert_eq!(
            cli.save_file,
            Some(
                PathBuf::from(DEFAULT_PLATFORM_DATA_ROOT)
                    .join(PLATFORM_SAVE_ROOT)
                    .join("profile.json")
            )
        );
        assert_eq!(
            cli.runtime_settings_file,
            Some(
                PathBuf::from(DEFAULT_PLATFORM_DATA_ROOT)
                    .join(PLATFORM_SETTINGS_ROOT)
                    .join("runtime_privacy_settings.json")
            )
        );
        assert!(cli
            .local_data_dirs
            .contains(&PathBuf::from(DEFAULT_PLATFORM_DATA_ROOT).join(PLATFORM_TELEMETRY_ROOT)));
        assert!(cli
            .local_data_dirs
            .contains(&PathBuf::from(DEFAULT_PLATFORM_DATA_ROOT).join(PLATFORM_REPLAY_ROOT)));
        assert!(cli
            .local_data_dirs
            .contains(&PathBuf::from(DEFAULT_PLATFORM_DATA_ROOT).join(PLATFORM_CRASH_REPORT_ROOT)));
    }

    #[test]
    fn runtime_native_platform_data_root_cli_rebinds_default_paths_when_available() {
        let Some(native_root) = super::runtime_native_platform_data_root() else {
            return;
        };
        let cli = parse_runtime_cli(["--native-platform-data-root".to_string()]);

        assert_eq!(cli.platform_data_root, native_root);
        assert_eq!(
            cli.save_file,
            Some(cli.platform_data_root.join("saves").join("profile.json"))
        );
        assert_eq!(
            cli.runtime_settings_file,
            Some(
                cli.platform_data_root
                    .join("settings")
                    .join("runtime_privacy_settings.json")
            )
        );
        assert_eq!(
            cli.local_data_dirs,
            vec![
                cli.platform_data_root.join("telemetry"),
                cli.platform_data_root.join("replay"),
                cli.platform_data_root.join("crash-reports"),
            ]
        );
    }

    #[test]
    fn runtime_platform_data_root_cli_rebinds_default_paths() {
        let cli = parse_runtime_cli([
            "--platform-data-root".to_string(),
            "tmp/platform-data".to_string(),
        ]);

        assert_eq!(cli.platform_data_root, PathBuf::from("tmp/platform-data"));
        assert_eq!(
            cli.save_file,
            Some(PathBuf::from("tmp/platform-data/saves/profile.json"))
        );
        assert_eq!(
            cli.runtime_settings_file,
            Some(PathBuf::from(
                "tmp/platform-data/settings/runtime_privacy_settings.json"
            ))
        );
        assert_eq!(
            cli.local_data_dirs,
            vec![
                PathBuf::from("tmp/platform-data/telemetry"),
                PathBuf::from("tmp/platform-data/replay"),
                PathBuf::from("tmp/platform-data/crash-reports"),
            ]
        );
    }

    #[test]
    fn parses_runtime_save_options() {
        let cli = parse_runtime_cli([
            "--save-file".to_string(),
            "harness/save/local/profile.json".to_string(),
            "--export-save".to_string(),
            "harness/save/local/export.json".to_string(),
            "--delete-save".to_string(),
        ]);

        assert_eq!(
            cli.save_file,
            Some(PathBuf::from("harness/save/local/profile.json"))
        );
        assert!(cli.explicit_save_file);
        assert_eq!(
            cli.export_save,
            Some(PathBuf::from("harness/save/local/export.json"))
        );
        assert!(cli.delete_save);
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
    fn runtime_privacy_settings_default_to_local_only() {
        let settings = RuntimePrivacySettings::default();

        assert!(!runtime_can_upload(&settings, RuntimeUploadKind::Telemetry));
        assert!(!runtime_can_upload(&settings, RuntimeUploadKind::RawReplay));
        assert!(!runtime_can_upload(
            &settings,
            RuntimeUploadKind::CrashReport
        ));

        let report = RuntimePrivacyReport::from_settings(&settings);
        assert!(report.local_capture_only);
        assert_eq!(report.upload_transport, "not_implemented");
    }

    #[test]
    fn runtime_privacy_settings_require_explicit_opt_in() {
        let settings = RuntimePrivacySettings {
            telemetry_upload_enabled: true,
            raw_replay_upload_enabled: false,
            crash_report_upload_enabled: true,
        };

        assert!(runtime_can_upload(&settings, RuntimeUploadKind::Telemetry));
        assert!(!runtime_can_upload(&settings, RuntimeUploadKind::RawReplay));
        assert!(runtime_can_upload(
            &settings,
            RuntimeUploadKind::CrashReport
        ));

        let report = RuntimePrivacyReport::from_settings(&settings);
        assert!(!report.local_capture_only);
    }

    #[test]
    fn loads_runtime_privacy_settings_file() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-settings-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(&root).unwrap();
        let settings_file = root.join("runtime_settings.json");
        fs::write(
            &settings_file,
            r#"{
  "telemetry_upload_enabled": true,
  "raw_replay_upload_enabled": false,
  "crash_report_upload_enabled": false
}
"#,
        )
        .unwrap();

        let settings = load_runtime_privacy_settings(&RuntimeCli {
            runtime_settings_file: Some(settings_file),
            ..RuntimeCli::default()
        })
        .unwrap();

        let _ = fs::remove_dir_all(&root);
        assert!(settings.telemetry_upload_enabled);
        assert!(!settings.raw_replay_upload_enabled);
        assert!(!settings.crash_report_upload_enabled);
    }

    #[test]
    fn missing_runtime_privacy_settings_file_uses_local_defaults() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-missing-settings-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        let settings_file = root.join("runtime_settings.json");

        let settings = load_runtime_privacy_settings(&RuntimeCli {
            runtime_settings_file: Some(settings_file.clone()),
            ..RuntimeCli::default()
        })
        .unwrap();

        let _ = fs::remove_dir_all(&root);
        assert!(!settings_file.exists());
        assert!(!settings.telemetry_upload_enabled);
        assert!(!settings.raw_replay_upload_enabled);
        assert!(!settings.crash_report_upload_enabled);
    }

    #[test]
    fn runtime_privacy_settings_toggle_and_persist_json() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-persist-settings-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        let settings_file = root.join("settings/runtime_settings.json");
        let mut settings = RuntimePrivacySettings::default();

        assert!(toggle_runtime_privacy_setting(
            &mut settings,
            RuntimeUploadKind::Telemetry
        ));
        assert!(!toggle_runtime_privacy_setting(
            &mut settings,
            RuntimeUploadKind::Telemetry
        ));
        assert!(toggle_runtime_privacy_setting(
            &mut settings,
            RuntimeUploadKind::RawReplay
        ));
        write_runtime_privacy_settings(&settings_file, &settings).unwrap();

        let loaded = load_runtime_privacy_settings(&RuntimeCli {
            runtime_settings_file: Some(settings_file),
            ..RuntimeCli::default()
        })
        .unwrap();

        let _ = fs::remove_dir_all(&root);
        assert!(!loaded.telemetry_upload_enabled);
        assert!(loaded.raw_replay_upload_enabled);
        assert!(!loaded.crash_report_upload_enabled);
    }

    #[test]
    fn runtime_privacy_settings_without_file_are_session_only() {
        let settings = RuntimePrivacySettings::default();

        assert!(!persist_runtime_privacy_settings_file(None, &settings).unwrap());
    }

    #[test]
    fn privacy_notice_contains_required_topics() {
        let notice = runtime_privacy_notice(&RuntimePrivacySettings::default());

        for fragment in [
            "默认只保存在本机",
            "平衡",
            "崩溃分析",
            "玩法改进",
            "明确开启",
            "raw replay",
            "导出",
            "删除",
            "个人身份信息",
            "90 天",
        ] {
            assert!(
                notice.contains(fragment),
                "missing privacy notice fragment {fragment}"
            );
        }
    }

    #[test]
    fn collects_local_data_only_from_configured_roots() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-export-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        let included = root.join("included");
        let excluded = root.join("excluded");
        fs::create_dir_all(included.join("nested")).unwrap();
        fs::create_dir_all(&excluded).unwrap();
        fs::write(included.join("report.json"), "{\"ok\":true}\n").unwrap();
        fs::write(included.join("nested/replay.json"), "{\"tick\":1}\n").unwrap();
        fs::write(excluded.join("private.json"), "{\"skip\":true}\n").unwrap();

        let files = collect_runtime_local_data_files(std::slice::from_ref(&included)).unwrap();

        let _ = fs::remove_dir_all(&root);
        assert_eq!(files.len(), 2);
        assert!(files
            .iter()
            .any(|file| file.relative_path == "report.json" && file.contents.contains("\"ok\"")));
        assert!(files
            .iter()
            .all(|file| file.root == included.display().to_string()));
        assert!(files
            .iter()
            .all(|file| !file.relative_path.contains("private.json")));
    }

    #[test]
    fn exports_local_data_json_with_privacy_settings() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-export-json-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        let data_dir = root.join("telemetry");
        let out_file = root.join("export/export.json");
        fs::create_dir_all(&data_dir).unwrap();
        fs::write(data_dir.join("sample.json"), "{\"sample\":1}\n").unwrap();

        let cli = RuntimeCli {
            local_data_dirs: vec![data_dir],
            ..RuntimeCli::default()
        };
        let settings = RuntimePrivacySettings {
            telemetry_upload_enabled: true,
            raw_replay_upload_enabled: false,
            crash_report_upload_enabled: false,
        };
        export_runtime_local_data(&cli, &settings, &out_file).unwrap();
        let export_text = fs::read_to_string(&out_file).unwrap();
        let export: serde_json::Value = serde_json::from_str(&export_text).unwrap();

        let _ = fs::remove_dir_all(&root);
        assert_eq!(export["kind"], "runtime_local_data_export");
        assert_eq!(export["privacy_settings"]["telemetry_upload_enabled"], true);
        assert_eq!(export["files"].as_array().unwrap().len(), 1);
        assert_eq!(export["files"][0]["relative_path"], "sample.json");
    }

    #[test]
    fn delete_local_data_only_removes_configured_roots() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-delete-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        let included = root.join("included");
        let excluded = root.join("excluded");
        fs::create_dir_all(included.join("nested")).unwrap();
        fs::create_dir_all(&excluded).unwrap();
        fs::write(included.join("report.json"), "{\"ok\":true}\n").unwrap();
        fs::write(included.join("nested/replay.json"), "{\"tick\":1}\n").unwrap();
        fs::write(excluded.join("private.json"), "{\"keep\":true}\n").unwrap();

        let report = delete_runtime_local_data(&RuntimeCli {
            local_data_dirs: vec![included.clone()],
            explicit_local_data_dirs: vec![included.clone()],
            ..RuntimeCli::default()
        })
        .unwrap();

        assert_eq!(report.deleted_files, 2);
        assert!(!included.join("report.json").exists());
        assert!(!included.join("nested/replay.json").exists());
        assert!(excluded.join("private.json").exists());

        let _ = fs::remove_dir_all(&root);
    }

    #[test]
    fn delete_local_data_requires_explicit_root() {
        let error = delete_runtime_local_data(&RuntimeCli::default()).unwrap_err();

        assert_eq!(error.kind(), std::io::ErrorKind::InvalidInput);
    }

    #[test]
    fn runtime_data_control_action_exports_and_deletes_local_data() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-f4-local-data-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        let platform_root = root.join("platform");
        let telemetry_dir = platform_root.join(PLATFORM_TELEMETRY_ROOT);
        let replay_dir = platform_root.join(PLATFORM_REPLAY_ROOT);
        let crash_dir = platform_root.join(PLATFORM_CRASH_REPORT_ROOT);
        fs::create_dir_all(&telemetry_dir).unwrap();
        fs::create_dir_all(&replay_dir).unwrap();
        fs::create_dir_all(&crash_dir).unwrap();
        fs::write(telemetry_dir.join("session.json"), "{\"telemetry\":true}\n").unwrap();
        fs::write(replay_dir.join("run.json"), "{\"replay\":true}\n").unwrap();
        fs::write(crash_dir.join("crash.json"), "{\"crash\":true}\n").unwrap();

        let context = RuntimeDataControlContext {
            platform_data_root: platform_root.clone(),
            runtime_settings_file: Some(
                platform_root
                    .join(PLATFORM_SETTINGS_ROOT)
                    .join("settings.json"),
            ),
            save_file: Some(platform_root.join(PLATFORM_SAVE_ROOT).join("profile.json")),
            local_data_dirs: vec![telemetry_dir.clone(), replay_dir.clone(), crash_dir.clone()],
            content_pack_ids: vec!["base-demo".to_string()],
            privacy_settings: RuntimePrivacySettings::default(),
        };

        let message =
            run_runtime_data_control_action(&context, RuntimeDataControlAction::ExportLocalData)
                .unwrap();
        let export_path = runtime_local_data_export_path(&platform_root);
        let export_json: serde_json::Value =
            serde_json::from_str(&fs::read_to_string(&export_path).unwrap()).unwrap();

        assert!(message.contains("exported local data"));
        assert_eq!(export_json["kind"], "runtime_local_data_export");
        assert_eq!(export_json["files"].as_array().unwrap().len(), 3);
        assert!(export_json["files"].as_array().unwrap().iter().any(|file| {
            file["root"] == telemetry_dir.display().to_string()
                && file["relative_path"] == "session.json"
        }));

        let message =
            run_runtime_data_control_action(&context, RuntimeDataControlAction::DeleteLocalData)
                .unwrap();

        assert!(message.contains("deleted local data 3 files"));
        assert!(!telemetry_dir.join("session.json").exists());
        assert!(!replay_dir.join("run.json").exists());
        assert!(!crash_dir.join("crash.json").exists());
        assert!(telemetry_dir.exists());
        assert!(replay_dir.exists());
        assert!(crash_dir.exists());
        let _ = fs::remove_dir_all(&root);
    }

    #[test]
    fn load_runtime_meta_progress_creates_default_save() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-save-create-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        let save_file = root.join("profile.json");
        let cli = RuntimeCli {
            save_file: Some(save_file.clone()),
            ..RuntimeCli::default()
        };

        let progress =
            super::load_runtime_meta_progress(&cli, &RuntimePrivacySettings::default()).unwrap();
        let save_text = fs::read_to_string(&save_file).unwrap();
        let save_json: serde_json::Value = serde_json::from_str(&save_text).unwrap();

        let _ = fs::remove_dir_all(&root);
        assert!(progress.unlocks.characters.contains("jar-keeper"));
        assert_eq!(save_json["contract_id"], "save-state-v1");
        assert_eq!(save_json["schema_version"], 2);
        assert_eq!(save_json["save_id"], DEFAULT_SAVE_ID);
        assert_eq!(save_json["settings"]["telemetry_upload_enabled"], false);
        assert_eq!(save_json["data_controls"]["export_format"], "json");
        assert_eq!(
            save_json["migration_history"][0]["migration_id"],
            "save-state-v0-to-v1"
        );
        assert_eq!(save_json["base_ui_state"]["selected_panel"], "overview");
    }

    #[test]
    fn runtime_save_round_trip_preserves_meta_progress() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-save-roundtrip-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        let save_file = root.join("profile.json");
        let mut progress = MetaProgress::demo_start();
        progress.resources.candy_crystal_shards = 42;
        write_runtime_save_state(
            &save_file,
            &RuntimeCli::default(),
            &RuntimePrivacySettings::default(),
            &progress,
        )
        .unwrap();

        let loaded = super::load_runtime_meta_progress(
            &RuntimeCli {
                save_file: Some(save_file.clone()),
                ..RuntimeCli::default()
            },
            &RuntimePrivacySettings::default(),
        )
        .unwrap();

        let _ = fs::remove_dir_all(&root);
        assert_eq!(loaded.resources.candy_crystal_shards, 42);
    }

    #[test]
    fn runtime_save_can_persist_base_codex_ui_state() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-save-base-ui-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        let save_file = root.join("profile.json");
        let mut base_ui_state = RuntimeBaseUiState {
            selected_panel: "codex".to_string(),
            ..RuntimeBaseUiState::default()
        };
        base_ui_state.codex_view.selected_category = "enemies".to_string();
        base_ui_state.codex_view.discovered_only = false;

        write_runtime_save_state_with_base_ui(
            &save_file,
            &RuntimeCli::default(),
            &RuntimePrivacySettings::default(),
            &MetaProgress::demo_start(),
            Some(&base_ui_state),
        )
        .unwrap();
        let save_json: serde_json::Value =
            serde_json::from_str(&fs::read_to_string(&save_file).unwrap()).unwrap();

        let _ = fs::remove_dir_all(&root);
        assert_eq!(save_json["base_ui_state"]["selected_panel"], "codex");
        assert_eq!(
            save_json["base_ui_state"]["codex_view"]["selected_category"],
            "enemies"
        );
        assert_eq!(
            save_json["base_ui_state"]["codex_view"]["discovered_only"],
            false
        );
    }

    #[test]
    fn runtime_save_migrates_v0_to_v1_and_keeps_progress() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-save-migrate-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        let save_file = root.join("profile.json");
        let mut progress = MetaProgress::demo_start();
        progress.completed_runs = 7;
        let v0 = RuntimeSaveStateV0 {
            schema_version: RUNTIME_SAVE_V0_SCHEMA_VERSION,
            contract_id: RUNTIME_SAVE_V0_CONTRACT_ID.to_string(),
            save_id: "legacy-profile".to_string(),
            profile_id: DEFAULT_PROFILE_ID.to_string(),
            created_at: RUNTIME_SAVE_TIMESTAMP.to_string(),
            updated_at: RUNTIME_SAVE_TIMESTAMP.to_string(),
            game_version: "prototype-v0".to_string(),
            ruleset_version: "prototype-v0".to_string(),
            content_pack_ids: vec!["base-demo".to_string()],
            settings: RuntimePrivacySettings::default(),
            data_controls: RuntimeSaveDataControls::default(),
            meta_progress: progress,
        };
        fs::create_dir_all(save_file.parent().unwrap()).unwrap();
        fs::write(
            &save_file,
            format!("{}\n", serde_json::to_string_pretty(&v0).unwrap()),
        )
        .unwrap();

        let loaded = super::load_runtime_meta_progress(
            &RuntimeCli {
                save_file: Some(save_file.clone()),
                ..RuntimeCli::default()
            },
            &RuntimePrivacySettings::default(),
        )
        .unwrap();
        let migrated_json: serde_json::Value =
            serde_json::from_str(&fs::read_to_string(&save_file).unwrap()).unwrap();

        let _ = fs::remove_dir_all(&root);
        assert_eq!(loaded.completed_runs, 7);
        assert_eq!(migrated_json["contract_id"], "save-state-v1");
        assert_eq!(
            migrated_json["migration_history"][0]["source_save_id"],
            "legacy-profile"
        );
        assert_eq!(migrated_json["migration_history"][0]["status"], "completed");
        assert_eq!(
            migrated_json["base_ui_state"]["codex_view"]["discovered_only"],
            true
        );
    }

    #[test]
    fn runtime_save_reads_v1_without_new_migration_entry() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-save-v1-read-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        let save_file = root.join("profile.json");
        let mut progress = MetaProgress::demo_start();
        progress.resources.star_shards = 5;
        write_runtime_save_state(
            &save_file,
            &RuntimeCli::default(),
            &RuntimePrivacySettings::default(),
            &progress,
        )
        .unwrap();
        let before_json: serde_json::Value =
            serde_json::from_str(&fs::read_to_string(&save_file).unwrap()).unwrap();

        let loaded = super::load_runtime_meta_progress(
            &RuntimeCli {
                save_file: Some(save_file.clone()),
                ..RuntimeCli::default()
            },
            &RuntimePrivacySettings::default(),
        )
        .unwrap();
        let after_json: serde_json::Value =
            serde_json::from_str(&fs::read_to_string(&save_file).unwrap()).unwrap();

        let _ = fs::remove_dir_all(&root);
        assert_eq!(loaded.resources.star_shards, 5);
        assert_eq!(
            before_json["migration_history"].as_array().unwrap().len(),
            after_json["migration_history"].as_array().unwrap().len()
        );
    }

    #[test]
    fn runtime_save_write_preserves_migrated_history() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-save-history-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        let save_file = root.join("profile.json");
        let mut progress = MetaProgress::demo_start();
        progress.completed_runs = 2;
        let v0 = RuntimeSaveStateV0 {
            schema_version: RUNTIME_SAVE_V0_SCHEMA_VERSION,
            contract_id: RUNTIME_SAVE_V0_CONTRACT_ID.to_string(),
            save_id: "legacy-profile".to_string(),
            profile_id: DEFAULT_PROFILE_ID.to_string(),
            created_at: RUNTIME_SAVE_TIMESTAMP.to_string(),
            updated_at: RUNTIME_SAVE_TIMESTAMP.to_string(),
            game_version: "prototype-v0".to_string(),
            ruleset_version: "prototype-v0".to_string(),
            content_pack_ids: vec!["base-demo".to_string()],
            settings: RuntimePrivacySettings::default(),
            data_controls: RuntimeSaveDataControls::default(),
            meta_progress: progress,
        };
        fs::create_dir_all(save_file.parent().unwrap()).unwrap();
        fs::write(
            &save_file,
            format!("{}\n", serde_json::to_string_pretty(&v0).unwrap()),
        )
        .unwrap();
        let cli = RuntimeCli {
            save_file: Some(save_file.clone()),
            ..RuntimeCli::default()
        };
        super::load_runtime_meta_progress(&cli, &RuntimePrivacySettings::default()).unwrap();
        let mut updated_progress = MetaProgress::demo_start();
        updated_progress.completed_runs = 9;
        write_runtime_save_state(
            &save_file,
            &RuntimeCli::default(),
            &RuntimePrivacySettings::default(),
            &updated_progress,
        )
        .unwrap();
        let rewritten_json: serde_json::Value =
            serde_json::from_str(&fs::read_to_string(&save_file).unwrap()).unwrap();

        let _ = fs::remove_dir_all(&root);
        assert_eq!(rewritten_json["meta_progress"]["completed_runs"], 9);
        assert_eq!(rewritten_json["save_id"], "legacy-profile");
        assert_eq!(
            rewritten_json["migration_history"][0]["source_save_id"],
            "legacy-profile"
        );
    }

    #[test]
    fn export_runtime_save_writes_json_copy() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-save-export-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        let save_file = root.join("profile.json");
        let export_file = root.join("export/profile_export.json");
        let mut progress = MetaProgress::demo_start();
        progress.completed_runs = 3;
        write_runtime_save_state(
            &save_file,
            &RuntimeCli::default(),
            &RuntimePrivacySettings::default(),
            &progress,
        )
        .unwrap();

        super::export_runtime_save(
            &RuntimeCli {
                save_file: Some(save_file),
                ..RuntimeCli::default()
            },
            &RuntimePrivacySettings::default(),
            &export_file,
        )
        .unwrap();
        let export_json: serde_json::Value =
            serde_json::from_str(&fs::read_to_string(&export_file).unwrap()).unwrap();

        let _ = fs::remove_dir_all(&root);
        assert_eq!(export_json["contract_id"], "save-state-v1");
        assert_eq!(export_json["meta_progress"]["completed_runs"], 3);
    }

    #[test]
    fn delete_runtime_save_requires_save_file() {
        let error = super::delete_runtime_save(&RuntimeCli::default()).unwrap_err();

        assert_eq!(error.kind(), std::io::ErrorKind::InvalidInput);
    }

    #[test]
    fn delete_runtime_save_removes_only_named_file() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-save-delete-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(&root).unwrap();
        let save_file = root.join("profile.json");
        let other_file = root.join("other.json");
        fs::write(&save_file, "{}\n").unwrap();
        fs::write(&other_file, "{}\n").unwrap();

        super::delete_runtime_save(&RuntimeCli {
            save_file: Some(save_file.clone()),
            explicit_save_file: true,
            ..RuntimeCli::default()
        })
        .unwrap();

        assert!(!save_file.exists());
        assert!(other_file.exists());
        let _ = fs::remove_dir_all(&root);
    }

    #[test]
    fn runtime_data_control_action_exports_and_deletes_save() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-f4-save-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        let platform_root = root.join("platform");
        let save_file = platform_root.join(PLATFORM_SAVE_ROOT).join("profile.json");
        let context = RuntimeDataControlContext {
            platform_data_root: platform_root.clone(),
            runtime_settings_file: Some(
                platform_root
                    .join(PLATFORM_SETTINGS_ROOT)
                    .join("settings.json"),
            ),
            save_file: Some(save_file.clone()),
            local_data_dirs: vec![
                platform_root.join(PLATFORM_TELEMETRY_ROOT),
                platform_root.join(PLATFORM_REPLAY_ROOT),
                platform_root.join(PLATFORM_CRASH_REPORT_ROOT),
            ],
            content_pack_ids: vec!["base-demo".to_string(), "runtime-f4-smoke".to_string()],
            privacy_settings: RuntimePrivacySettings::default(),
        };

        let message =
            run_runtime_data_control_action(&context, RuntimeDataControlAction::ExportSave)
                .unwrap();
        let export_path = runtime_save_export_path(&platform_root);
        let export_json: serde_json::Value =
            serde_json::from_str(&fs::read_to_string(&export_path).unwrap()).unwrap();

        assert!(message.contains("exported save"));
        assert!(save_file.exists());
        assert_eq!(export_json["contract_id"], "save-state-v1");
        assert_eq!(export_json["content_pack_ids"].as_array().unwrap().len(), 2);

        let message =
            run_runtime_data_control_action(&context, RuntimeDataControlAction::DeleteSave)
                .unwrap();

        assert!(message.contains("deleted save"));
        assert!(!save_file.exists());
        assert!(export_path.exists());
        let _ = fs::remove_dir_all(&root);
    }

    #[test]
    fn runtime_data_delete_action_requires_same_key_confirmation() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-f4-confirm-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(&root).unwrap();
        let save_file = root.join("profile.json");
        fs::write(&save_file, "{}\n").unwrap();

        let mut state = runtime_state_for_tests();
        state.platform_data_root = root.clone();
        state.save_file = Some(save_file.clone());

        let message = run_runtime_data_control_action_from_state(
            &mut state,
            RuntimeDataControlAction::DeleteSave,
        )
        .unwrap();
        assert!(message.contains("press X again"));
        assert!(save_file.exists());
        assert_eq!(
            state.pending_data_delete_action,
            Some(RuntimeDataControlAction::DeleteSave)
        );

        let message = run_runtime_data_control_action_from_state(
            &mut state,
            RuntimeDataControlAction::DeleteSave,
        )
        .unwrap();
        assert!(message.contains("deleted save"));
        assert!(!save_file.exists());
        assert_eq!(state.pending_data_delete_action, None);

        let _ = fs::remove_dir_all(&root);
    }

    #[test]
    fn builds_runtime_run_config_from_cli() {
        let cli = parse_runtime_cli([
            "--character-id".to_string(),
            "bubble-courier".to_string(),
            "--seed".to_string(),
            "77".to_string(),
            "--map-id".to_string(),
            "jelly-platform".to_string(),
        ]);
        let content = ContentPack::base_demo();
        let config = run_config_from_cli(&cli, &content);

        assert_eq!(config.seed, 77);
        assert_eq!(config.map_id, "jelly-platform");
        assert_eq!(config.character_id, "bubble-courier");
        assert_eq!(config.starting_loadout.weapons, ["soda-bubble-pop"]);
    }

    #[test]
    fn parse_runtime_cli_accepts_unlock_all_content() {
        let cli = parse_runtime_cli(["--unlock-all-content".to_string()]);

        assert!(cli.unlock_all_content);
    }

    #[test]
    fn runtime_selection_helpers_only_cycle_unlocked_content() {
        let mut progress = MetaProgress::demo_start();
        progress
            .unlocks
            .characters
            .insert("bubble-courier".to_string());
        progress.unlocks.maps.insert("soda-creek".to_string());
        let content = ContentPack::base_demo();

        let characters = runtime_unlocked_character_ids(&progress, &content);
        let maps = runtime_unlocked_map_ids(&progress, &content);

        assert_eq!(characters, ["bubble-courier", "jar-keeper"]);
        assert_eq!(
            next_runtime_selection_id(&characters, "jar-keeper"),
            Some("bubble-courier".to_string())
        );
        assert_eq!(maps, ["frosting-grassland", "soda-creek"]);
        assert_eq!(
            next_runtime_selection_id(&maps, "frosting-grassland"),
            Some("soda-creek".to_string())
        );
        assert_eq!(
            runtime_character_starting_loadout(&content, "bubble-courier").weapons,
            ["soda-bubble-pop"]
        );
    }

    #[test]
    fn unlock_all_content_exposes_full_runtime_roster_for_session() {
        let content = ContentPack::base_demo();
        let mut progress = MetaProgress::demo_start();

        unlock_runtime_content_for_session(&mut progress, &content);

        assert_eq!(runtime_unlocked_character_ids(&progress, &content).len(), 5);
        assert_eq!(runtime_unlocked_map_ids(&progress, &content).len(), 6);
        assert!(progress.unlocks.weapons.contains("soda-fountain"));
        assert!(progress.unlocks.passives.contains("bubble-shoes"));
        assert!(progress.unlocks.evolutions.contains("soda-volcano"));
        assert!(progress.unlocks.events.contains("rainbow-candy-rush"));
        assert!(progress.chapters.values().all(|chapter| chapter.unlocked));
    }

    #[test]
    fn runtime_meta_panel_tab_pointer_input_maps_left_click_zone() {
        let window_size = Vec2::new(1280.0, 720.0);

        let mut left = ButtonInput::<MouseButton>::default();
        left.press(MouseButton::Left);
        assert_eq!(
            runtime_meta_panel_tab_view_from_pointer(
                &left,
                Some(Vec2::new(1050.0, 700.0)),
                window_size
            ),
            Some(RuntimeMetaPanelView::Codex)
        );

        let mut right = ButtonInput::<MouseButton>::default();
        right.press(MouseButton::Right);
        assert_eq!(
            runtime_meta_panel_tab_view_from_pointer(
                &right,
                Some(Vec2::new(1050.0, 700.0)),
                window_size
            ),
            None
        );
    }

    #[test]
    fn runtime_meta_panel_tab_pointer_zone_maps_header_segments() {
        let window_size = Vec2::new(1280.0, 720.0);

        assert_eq!(
            runtime_meta_panel_tab_view_from_pointer_zone(Vec2::new(880.0, 700.0), window_size),
            Some(RuntimeMetaPanelView::Overview)
        );
        assert_eq!(
            runtime_meta_panel_tab_view_from_pointer_zone(Vec2::new(965.0, 700.0), window_size),
            Some(RuntimeMetaPanelView::Chapters)
        );
        assert_eq!(
            runtime_meta_panel_tab_view_from_pointer_zone(Vec2::new(1050.0, 700.0), window_size),
            Some(RuntimeMetaPanelView::Codex)
        );
        assert_eq!(
            runtime_meta_panel_tab_view_from_pointer_zone(Vec2::new(1135.0, 700.0), window_size),
            Some(RuntimeMetaPanelView::Settings)
        );
        assert_eq!(
            runtime_meta_panel_tab_view_from_pointer_zone(Vec2::new(1220.0, 700.0), window_size),
            Some(RuntimeMetaPanelView::Loadout)
        );
        assert_eq!(
            runtime_meta_panel_tab_view_from_pointer_zone(Vec2::new(500.0, 700.0), window_size),
            None
        );
        assert_eq!(
            runtime_meta_panel_tab_view_from_pointer_zone(Vec2::new(1050.0, 620.0), window_size),
            None
        );
    }

    #[test]
    fn runtime_overview_pointer_input_maps_left_click_zone() {
        let window_size = Vec2::new(1280.0, 720.0);

        let mut left = ButtonInput::<MouseButton>::default();
        left.press(MouseButton::Left);
        assert_eq!(
            runtime_overview_view_from_pointer(&left, Some(Vec2::new(990.0, 40.0)), window_size),
            Some(RuntimeMetaPanelView::Codex)
        );

        let mut right = ButtonInput::<MouseButton>::default();
        right.press(MouseButton::Right);
        assert_eq!(
            runtime_overview_view_from_pointer(&right, Some(Vec2::new(990.0, 40.0)), window_size),
            None
        );
    }

    #[test]
    fn runtime_overview_pointer_zone_maps_right_panel_segments() {
        let window_size = Vec2::new(1280.0, 720.0);

        assert_eq!(
            runtime_overview_view_from_pointer_zone(Vec2::new(880.0, 40.0), window_size),
            Some(RuntimeMetaPanelView::Chapters)
        );
        assert_eq!(
            runtime_overview_view_from_pointer_zone(Vec2::new(990.0, 40.0), window_size),
            Some(RuntimeMetaPanelView::Codex)
        );
        assert_eq!(
            runtime_overview_view_from_pointer_zone(Vec2::new(1100.0, 40.0), window_size),
            Some(RuntimeMetaPanelView::Settings)
        );
        assert_eq!(
            runtime_overview_view_from_pointer_zone(Vec2::new(1220.0, 40.0), window_size),
            Some(RuntimeMetaPanelView::Loadout)
        );
        assert_eq!(
            runtime_overview_view_from_pointer_zone(Vec2::new(500.0, 40.0), window_size),
            None
        );
        assert_eq!(
            runtime_overview_view_from_pointer_zone(Vec2::new(990.0, 140.0), window_size),
            None
        );
    }

    #[test]
    fn runtime_chapter_action_starts_only_unlocked_chapters() {
        let mut state = runtime_state_for_tests();

        state.base_ui_state.last_selected_chapter_id = "soda-creek".to_string();
        let locked_error =
            apply_runtime_chapter_action(&mut state, RuntimeChapterAction::StartSelectedChapter)
                .unwrap_err();

        assert_eq!(locked_error.kind(), std::io::ErrorKind::PermissionDenied);
        assert_eq!(state.config.map_id, DEFAULT_MAP_ID);
        assert_eq!(state.run_number, 1);

        state.base_ui_state.last_selected_chapter_id = "frosting-grassland".to_string();
        let message =
            apply_runtime_chapter_action(&mut state, RuntimeChapterAction::StartSelectedChapter)
                .unwrap();

        assert!(message.contains("started chapter frosting-grassland"));
        assert_eq!(state.config.map_id, "frosting-grassland");
        assert_eq!(
            state.base_ui_state.last_selected_map_id,
            "frosting-grassland"
        );
        assert_eq!(
            state.base_ui_state.last_selected_chapter_id,
            "frosting-grassland"
        );
        assert_eq!(state.run_number, 2);
    }

    #[test]
    fn runtime_chapter_keyboard_input_maps_navigation_actions() {
        let mut previous = ButtonInput::<KeyCode>::default();
        previous.press(KeyCode::KeyQ);
        assert_eq!(
            runtime_chapter_action_from_keyboard(&previous),
            Some(RuntimeChapterAction::Previous)
        );

        let mut next = ButtonInput::<KeyCode>::default();
        next.press(KeyCode::KeyE);
        assert_eq!(
            runtime_chapter_action_from_keyboard(&next),
            Some(RuntimeChapterAction::Next)
        );

        let mut start = ButtonInput::<KeyCode>::default();
        start.press(KeyCode::KeyG);
        assert_eq!(
            runtime_chapter_action_from_keyboard(&start),
            Some(RuntimeChapterAction::StartSelectedChapter)
        );

        assert_eq!(
            runtime_chapter_action_from_keyboard(&ButtonInput::<KeyCode>::default()),
            None
        );
    }

    #[test]
    fn runtime_chapter_gamepad_input_maps_navigation_actions() {
        let gamepad = Gamepad::new(0);
        let mut previous = ButtonInput::<GamepadButton>::default();
        previous.press(GamepadButton::new(gamepad, GamepadButtonType::LeftTrigger));
        assert_eq!(
            runtime_chapter_action_from_gamepad(&previous),
            Some(RuntimeChapterAction::Previous)
        );

        let mut next = ButtonInput::<GamepadButton>::default();
        next.press(GamepadButton::new(gamepad, GamepadButtonType::DPadRight));
        assert_eq!(
            runtime_chapter_action_from_gamepad(&next),
            Some(RuntimeChapterAction::Next)
        );

        let mut start = ButtonInput::<GamepadButton>::default();
        start.press(GamepadButton::new(gamepad, GamepadButtonType::South));
        assert_eq!(
            runtime_chapter_action_from_gamepad(&start),
            Some(RuntimeChapterAction::StartSelectedChapter)
        );

        assert_eq!(
            runtime_chapter_action_from_gamepad(&ButtonInput::<GamepadButton>::default()),
            None
        );
    }

    #[test]
    fn runtime_chapter_pointer_input_maps_left_click_zone() {
        let window_size = Vec2::new(1280.0, 720.0);

        let mut left = ButtonInput::<MouseButton>::default();
        left.press(MouseButton::Left);
        assert_eq!(
            runtime_chapter_action_from_pointer(&left, Some(Vec2::new(1000.0, 40.0)), window_size),
            Some(RuntimeChapterAction::Next)
        );

        let mut right = ButtonInput::<MouseButton>::default();
        right.press(MouseButton::Right);
        assert_eq!(
            runtime_chapter_action_from_pointer(&right, Some(Vec2::new(1000.0, 40.0)), window_size),
            None
        );
    }

    #[test]
    fn runtime_chapter_pointer_zone_maps_right_panel_segments() {
        let window_size = Vec2::new(1280.0, 720.0);

        assert_eq!(
            runtime_chapter_action_from_pointer_zone(Vec2::new(880.0, 40.0), window_size),
            Some(RuntimeChapterAction::Previous)
        );
        assert_eq!(
            runtime_chapter_action_from_pointer_zone(Vec2::new(1000.0, 40.0), window_size),
            Some(RuntimeChapterAction::Next)
        );
        assert_eq!(
            runtime_chapter_action_from_pointer_zone(Vec2::new(1200.0, 40.0), window_size),
            Some(RuntimeChapterAction::StartSelectedChapter)
        );
        assert_eq!(
            runtime_chapter_action_from_pointer_zone(Vec2::new(500.0, 40.0), window_size),
            None
        );
        assert_eq!(
            runtime_chapter_action_from_pointer_zone(Vec2::new(1000.0, 140.0), window_size),
            None
        );
    }

    #[test]
    fn low_health_changes_player_tint() {
        assert_ne!(player_tint(100.0, 100.0), player_tint(20.0, 100.0));
    }

    #[test]
    fn map_visual_style_distinguishes_known_maps() {
        assert_eq!(map_visual_style("soda-creek").display_name, "汽水溪谷");
        assert_eq!(
            map_visual_style("cracked-star-jar").display_name,
            "裂星糖罐"
        );
        assert_eq!(map_visual_style("unknown-map").display_name, "糖霜草地");
    }

    #[test]
    fn boss_status_renders_current_boss_health() {
        let content = ContentPack::base_demo();
        assert_eq!(format_boss_status(None, &content), "Boss 未出现");

        let boss = BossSnapshot {
            entity_id: 42,
            boss_id: "runaway-sugar-mixer".to_string(),
            health: 125.0,
            max_health: 250.0,
            position: CoreVec2::ZERO,
        };
        let status = format_boss_status(Some(&boss), &content);

        assert!(status.contains("暴走搅糖机"));
        assert!(status.contains("runaway-sugar-mixer"));
        assert!(status.contains("HP 125/250"));
        assert!(status.contains("50%"));
    }

    #[test]
    fn enemy_swarm_status_renders_visible_enemy_mix() {
        let content = ContentPack::base_demo();
        let enemies = vec![
            EnemySnapshot {
                entity_id: 1,
                enemy_id: "bouncy-gummy".to_string(),
                position: CoreVec2::ZERO,
                velocity: CoreVec2::ZERO,
                health: 10.0,
                max_health: 10.0,
                radius: 12.0,
                threat: 1.0,
                behavior: EnemyBehavior::Chase,
                is_boss: false,
                is_elite: false,
            },
            EnemySnapshot {
                entity_id: 2,
                enemy_id: "bouncy-gummy".to_string(),
                position: CoreVec2::new(10.0, 0.0),
                velocity: CoreVec2::ZERO,
                health: 10.0,
                max_health: 10.0,
                radius: 12.0,
                threat: 1.0,
                behavior: EnemyBehavior::Chase,
                is_boss: false,
                is_elite: false,
            },
            EnemySnapshot {
                entity_id: 3,
                enemy_id: "caramel-slime".to_string(),
                position: CoreVec2::new(20.0, 0.0),
                velocity: CoreVec2::ZERO,
                health: 40.0,
                max_health: 40.0,
                radius: 20.0,
                threat: 2.8,
                behavior: EnemyBehavior::Chase,
                is_boss: false,
                is_elite: true,
            },
        ];

        let status = format_enemy_swarm_status(&enemies, &content);

        assert!(status.contains("蹦蹦软糖 x2"));
        assert!(status.contains("焦糖史莱姆 x1"));
        assert!(status.contains("可见 3"));
        assert!(status.contains("最高威胁 2.8"));
        assert!(status.contains("精英/Boss 1"));
    }

    #[test]
    fn enemy_swarm_status_renders_empty_state() {
        assert_eq!(
            format_enemy_swarm_status(&[], &ContentPack::base_demo()),
            "敌群 无"
        );
    }

    #[test]
    fn build_status_renders_current_loadout_labels() {
        let content = ContentPack::base_demo();
        let build = BuildSnapshot {
            weapons: vec![
                BuildItemSnapshot {
                    id: "rainbow-candy-shot".to_string(),
                    level: 3,
                },
                BuildItemSnapshot {
                    id: "soda-bubble-pop".to_string(),
                    level: 1,
                },
            ],
            passives: vec![BuildItemSnapshot {
                id: "candy-crystal-lens".to_string(),
                level: 2,
            }],
            evolutions: vec![BuildItemSnapshot {
                id: "rainbow-candy-meteor".to_string(),
                level: 1,
            }],
            tags: vec!["projectile".to_string(), "economy".to_string()],
            open_evolution_paths: vec!["soda-volcano".to_string()],
        };
        let status = format_build_status(&build, &content);

        assert!(status.contains("Build 武器"));
        assert!(status.contains("彩虹糖弹 Lv.3"));
        assert!(status.contains("汽水泡泡 Lv.1"));
        assert!(status.contains("糖晶放大镜 Lv.2"));
        assert!(status.contains("彩虹糖流星雨 Lv.1"));
        assert!(status.contains("进化线 汽水火山 (soda-volcano)"));
        assert!(status.contains("标签 弹幕, 经济"));
    }

    #[test]
    fn hazard_status_renders_safe_state() {
        assert_eq!(format_hazard_status(&[], &[]), "地图危险 安全");
    }

    #[test]
    fn hazard_status_renders_active_zones_and_player_status() {
        let hazards = vec![
            HazardSnapshot {
                position: CoreVec2::ZERO,
                radius: 48.0,
                slow_multiplier: 0.65,
                damage_per_second: 0.0,
                remaining_seconds: 4.0,
            },
            HazardSnapshot {
                position: CoreVec2::new(10.0, 0.0),
                radius: 80.0,
                slow_multiplier: 0.45,
                damage_per_second: 12.0,
                remaining_seconds: 7.5,
            },
        ];
        let status_effects = vec![StatusEffectSnapshot {
            effect_id: "movement_slow".to_string(),
            kind: "slow".to_string(),
            multiplier: 0.6,
            remaining_seconds: 2.5,
        }];

        let status = format_hazard_status(&hazards, &status_effects);

        assert!(status.contains("危险区 2"));
        assert!(status.contains("最高伤害 12/s"));
        assert!(status.contains("最强减速 移速 45%"));
        assert!(status.contains("最长 7.5s"));
        assert!(status.contains("减速 移速 60% 2.5s"));
    }

    #[test]
    fn terminal_overlay_renders_result_and_reason() {
        let terminal = TerminalState {
            kind: TerminalKind::Defeat,
            time_seconds: 214.5,
            reason: "player_health_depleted".to_string(),
            final_level: 6,
            kills: 128,
        };
        let overlay = format_terminal_overlay(&terminal);

        assert!(overlay.contains("失败"));
        assert!(overlay.contains("214.5s"));
        assert!(overlay.contains("Lv 6"));
        assert!(overlay.contains("击杀 128"));
        assert!(overlay.contains("生命值归零"));
        assert!(overlay.contains("按 R 重新巡逻"));
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
                active_hazards: 0,
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
            GameEvent::ContentEventTriggered {
                event_id: "rainbow-candy-rush".to_string(),
            },
            GameEvent::BossPhaseChanged {
                entity_id: 11,
                boss_id: "caramel-furnace".to_string(),
                phase_index: 1,
            },
            GameEvent::BossAbilityUsed {
                entity_id: 11,
                boss_id: "caramel-furnace".to_string(),
                ability_id: "lay_caramel_tracks".to_string(),
            },
        ]);

        assert_eq!(counts.weapon_fired, 1);
        assert_eq!(counts.xp_collected, 1);
        assert_eq!(counts.player_damaged, 1);
        assert_eq!(counts.content_event_triggered, 1);
        assert_eq!(counts.boss_phase_changed, 1);
        assert_eq!(counts.boss_ability_used, 1);
    }

    #[test]
    fn meta_panel_highlights_last_settlement() {
        let mut progress = MetaProgress::demo_start();
        let summary = MetaRunSummary {
            run_id: "runtime_run_1_seed_12345".to_string(),
            mode: RunMode::StandardPatrol,
            map_id: "frosting-grassland".to_string(),
            character_id: "jar-keeper".to_string(),
            duration_seconds: 120.0,
            victory: false,
            terminal_reason: "duration_reached".to_string(),
            kills: 95,
            level: 5,
            xp_collected: 210.0,
            damage_dealt_by_weapon: 900.0,
            damage_taken: 12.5,
            damage_taken_by_source: BTreeMap::from([
                ("contact".to_string(), 9.0),
                ("hazard".to_string(), 3.5),
            ]),
            boss_damage: 0.0,
            weapon_levels: BTreeMap::from([("rainbow-candy-shot".to_string(), 1)]),
            passives_used: Default::default(),
            enemies_defeated: Default::default(),
            bosses_defeated: Default::default(),
        };
        let report = progress.apply_run_summary(&summary);
        let panel = render_meta_progress_panel(
            &progress,
            Some(&report),
            RuntimeMetaPanelView::Overview,
            meta_panel_context(
                &RuntimePrivacySettings::default(),
                None,
                None,
                None,
                &ContentPack::base_demo(),
                &RunConfig::default(),
                &RuntimeBaseUiState::default(),
                0,
            ),
        );

        assert!(panel.contains("糖罐守护站"));
        assert!(panel.contains("局后结算"));
        assert!(panel.contains("失败"));
        assert!(panel.contains("存活 120s"));
        assert!(panel.contains("等级 5"));
        assert!(panel.contains("击杀 95"));
        assert!(panel.contains("XP 210"));
        assert!(panel.contains("输出 900"));
        assert!(panel.contains("受伤 12.5"));
        assert!(panel.contains("接触 9.0"));
        assert!(panel.contains("rainbow-candy-shot Lv.1"));
        assert!(panel.contains("collect-200-candy-crystals"));
        assert!(panel.contains("discovered:jar-keeper"));
        assert!(panel.contains("下一步"));
        assert!(panel.contains("页签点击区: 概览  章节  图鉴  设置  巡逻"));
        assert!(panel.contains("右下点击区: 章节  图鉴  设置  巡逻"));
    }

    #[test]
    fn meta_panel_renders_chapter_view() {
        let mut progress = MetaProgress::demo_start();
        let summary = MetaRunSummary {
            run_id: "runtime_run_1_seed_12345".to_string(),
            mode: RunMode::StandardPatrol,
            map_id: "frosting-grassland".to_string(),
            character_id: "jar-keeper".to_string(),
            duration_seconds: 600.0,
            victory: true,
            terminal_reason: "duration_reached".to_string(),
            kills: 95,
            level: 5,
            xp_collected: 210.0,
            damage_dealt_by_weapon: 1_200.0,
            damage_taken: 4.0,
            damage_taken_by_source: BTreeMap::from([("contact".to_string(), 4.0)]),
            boss_damage: 300.0,
            weapon_levels: BTreeMap::from([("rainbow-candy-shot".to_string(), 5)]),
            passives_used: Default::default(),
            enemies_defeated: Default::default(),
            bosses_defeated: Default::default(),
        };
        let report = progress.apply_run_summary(&summary);
        let panel = render_meta_progress_panel(
            &progress,
            Some(&report),
            RuntimeMetaPanelView::Chapters,
            meta_panel_context(
                &RuntimePrivacySettings::default(),
                None,
                None,
                None,
                &ContentPack::base_demo(),
                &RunConfig::default(),
                &RuntimeBaseUiState::default(),
                0,
            ),
        );

        assert!(panel.contains("章节目标"));
        assert!(panel.contains("页签点击区: 概览  章节  图鉴  设置  巡逻"));
        assert!(panel.contains("Q/E/手柄左/右 切换章节"));
        assert!(panel.contains("G/手柄确认 巡逻已解锁章节"));
        assert!(panel.contains("右下点击区: 上章  下章  巡逻"));
        assert!(panel.contains("frosting-grassland"));
        assert!(panel.contains("地图说明 覆盖糖霜的开阔草地"));
        assert!(panel.contains("Boss说明"));
        assert!(panel.contains("应对"));
        assert!(panel.contains("survive-10-minutes"));
        assert!(panel.contains("本局完成"));
    }

    #[test]
    fn meta_panel_renders_locked_chapter_selection_detail() {
        let base_ui_state = RuntimeBaseUiState {
            last_selected_chapter_id: "soda-creek".to_string(),
            last_selected_map_id: "soda-creek".to_string(),
            ..RuntimeBaseUiState::default()
        };
        let panel = render_meta_progress_panel(
            &MetaProgress::demo_start(),
            None,
            RuntimeMetaPanelView::Chapters,
            meta_panel_context(
                &RuntimePrivacySettings::default(),
                None,
                None,
                None,
                &ContentPack::base_demo(),
                &RunConfig::default(),
                &base_ui_state,
                0,
            ),
        );

        assert!(panel.contains("汽水溪谷"));
        assert!(panel.contains("soda-creek"));
        assert!(panel.contains("汽水喷泉龙"));
        assert!(panel.contains("未解锁"));
        assert!(panel.contains("future-chapter-goals"));
        assert!(panel.contains("G 不会启动锁定章节"));
    }

    #[test]
    fn meta_panel_renders_codex_view() {
        let mut progress = MetaProgress::demo_start();
        let summary = MetaRunSummary {
            run_id: "runtime_run_1_seed_12345".to_string(),
            mode: RunMode::StandardPatrol,
            map_id: "frosting-grassland".to_string(),
            character_id: "jar-keeper".to_string(),
            duration_seconds: 120.0,
            victory: false,
            terminal_reason: "duration_reached".to_string(),
            kills: 95,
            level: 5,
            xp_collected: 210.0,
            damage_dealt_by_weapon: 900.0,
            damage_taken: 12.5,
            damage_taken_by_source: BTreeMap::from([("contact".to_string(), 12.5)]),
            boss_damage: 0.0,
            weapon_levels: BTreeMap::from([("rainbow-candy-shot".to_string(), 1)]),
            passives_used: Default::default(),
            enemies_defeated: Default::default(),
            bosses_defeated: Default::default(),
        };
        let report = progress.apply_run_summary(&summary);
        let panel = render_meta_progress_panel(
            &progress,
            Some(&report),
            RuntimeMetaPanelView::Codex,
            meta_panel_context(
                &RuntimePrivacySettings::default(),
                None,
                None,
                None,
                &ContentPack::base_demo(),
                &RunConfig::default(),
                &RuntimeBaseUiState::default(),
                0,
            ),
        );

        assert!(panel.contains("图鉴进度"));
        assert!(panel.contains("角色: 1/1 已发现"));
        assert!(panel.contains("character:jar-keeper"));
        assert!(panel.contains("本局更新"));
    }

    #[test]
    fn meta_panel_renders_browseable_codex_entry_details() {
        let mut progress = MetaProgress::demo_start();
        let summary = MetaRunSummary {
            run_id: "runtime_run_1_seed_12345".to_string(),
            mode: RunMode::StandardPatrol,
            map_id: "frosting-grassland".to_string(),
            character_id: "jar-keeper".to_string(),
            duration_seconds: 120.0,
            victory: false,
            terminal_reason: "duration_reached".to_string(),
            kills: 3,
            level: 2,
            xp_collected: 12.0,
            damage_dealt_by_weapon: 40.0,
            damage_taken: 2.0,
            damage_taken_by_source: BTreeMap::from([("contact".to_string(), 2.0)]),
            boss_damage: 0.0,
            weapon_levels: BTreeMap::from([("rainbow-candy-shot".to_string(), 1)]),
            passives_used: Default::default(),
            enemies_defeated: BTreeMap::from([("bouncy-gummy".to_string(), 3)]),
            bosses_defeated: Default::default(),
        };
        progress.apply_run_summary(&summary);
        let mut base_ui_state = RuntimeBaseUiState::default();
        base_ui_state.codex_view.selected_category =
            RuntimeCodexCategory::Enemies.key().to_string();
        base_ui_state.codex_view.discovered_only = true;

        let panel = render_meta_progress_panel(
            &progress,
            None,
            RuntimeMetaPanelView::Codex,
            meta_panel_context(
                &RuntimePrivacySettings::default(),
                None,
                None,
                None,
                &ContentPack::base_demo(),
                &RunConfig::default(),
                &base_ui_state,
                0,
            ),
        );

        assert!(panel.contains("图鉴浏览 仅已发现"));
        assert!(panel.contains("分类 敌人"));
        assert!(panel.contains("Q/E 或手柄 LT/RT 切换分类"));
        assert!(panel.contains("B/N、右下点击区或十字键左/右切换条目"));
        assert!(panel.contains("V、鼠标中键或手柄 Y 切换过滤"));
        assert!(panel.contains("右下点击区: <类  类>  <条目  条目>  过滤"));
        assert!(panel.contains("蹦蹦软糖"));
        assert!(panel.contains("bouncy-gummy"));
        assert!(panel.contains("击败 3"));
    }

    #[test]
    fn runtime_codex_gamepad_input_maps_buttons() {
        let gamepad = Gamepad::new(0);

        let mut left_trigger = ButtonInput::<GamepadButton>::default();
        left_trigger.press(GamepadButton::new(gamepad, GamepadButtonType::LeftTrigger));
        assert_eq!(
            runtime_codex_action_from_gamepad(&left_trigger),
            Some(RuntimeCodexAction::PreviousCategory)
        );

        let mut right_trigger = ButtonInput::<GamepadButton>::default();
        right_trigger.press(GamepadButton::new(gamepad, GamepadButtonType::RightTrigger));
        assert_eq!(
            runtime_codex_action_from_gamepad(&right_trigger),
            Some(RuntimeCodexAction::NextCategory)
        );

        let mut dpad_left = ButtonInput::<GamepadButton>::default();
        dpad_left.press(GamepadButton::new(gamepad, GamepadButtonType::DPadLeft));
        assert_eq!(
            runtime_codex_action_from_gamepad(&dpad_left),
            Some(RuntimeCodexAction::PreviousEntry)
        );

        let mut dpad_right = ButtonInput::<GamepadButton>::default();
        dpad_right.press(GamepadButton::new(gamepad, GamepadButtonType::DPadRight));
        assert_eq!(
            runtime_codex_action_from_gamepad(&dpad_right),
            Some(RuntimeCodexAction::NextEntry)
        );

        let mut north = ButtonInput::<GamepadButton>::default();
        north.press(GamepadButton::new(gamepad, GamepadButtonType::North));
        assert_eq!(
            runtime_codex_action_from_gamepad(&north),
            Some(RuntimeCodexAction::ToggleDiscoveredOnly)
        );

        assert_eq!(
            runtime_codex_action_from_gamepad(&ButtonInput::<GamepadButton>::default()),
            None
        );
    }

    #[test]
    fn runtime_codex_pointer_input_maps_mouse_buttons() {
        let window_size = Vec2::new(1280.0, 720.0);

        let mut left = ButtonInput::<MouseButton>::default();
        left.press(MouseButton::Left);
        assert_eq!(
            runtime_codex_action_from_pointer(&left, Some(Vec2::new(1110.0, 40.0)), window_size),
            Some(RuntimeCodexAction::NextEntry)
        );

        let mut right = ButtonInput::<MouseButton>::default();
        right.press(MouseButton::Right);
        assert_eq!(
            runtime_codex_action_from_pointer(&right, None, window_size),
            Some(RuntimeCodexAction::PreviousEntry)
        );

        let mut middle = ButtonInput::<MouseButton>::default();
        middle.press(MouseButton::Middle);
        assert_eq!(
            runtime_codex_action_from_pointer(&middle, None, window_size),
            Some(RuntimeCodexAction::ToggleDiscoveredOnly)
        );

        assert_eq!(
            runtime_codex_action_from_pointer(
                &ButtonInput::<MouseButton>::default(),
                None,
                window_size
            ),
            None
        );
    }

    #[test]
    fn runtime_codex_pointer_zone_maps_right_panel_segments() {
        let window_size = Vec2::new(1280.0, 720.0);

        assert_eq!(
            runtime_codex_action_from_pointer_zone(Vec2::new(850.0, 40.0), window_size),
            Some(RuntimeCodexAction::PreviousCategory)
        );
        assert_eq!(
            runtime_codex_action_from_pointer_zone(Vec2::new(930.0, 40.0), window_size),
            Some(RuntimeCodexAction::NextCategory)
        );
        assert_eq!(
            runtime_codex_action_from_pointer_zone(Vec2::new(1020.0, 40.0), window_size),
            Some(RuntimeCodexAction::PreviousEntry)
        );
        assert_eq!(
            runtime_codex_action_from_pointer_zone(Vec2::new(1110.0, 40.0), window_size),
            Some(RuntimeCodexAction::NextEntry)
        );
        assert_eq!(
            runtime_codex_action_from_pointer_zone(Vec2::new(1200.0, 40.0), window_size),
            Some(RuntimeCodexAction::ToggleDiscoveredOnly)
        );
        assert_eq!(
            runtime_codex_action_from_pointer_zone(Vec2::new(500.0, 40.0), window_size),
            None
        );
        assert_eq!(
            runtime_codex_action_from_pointer_zone(Vec2::new(1110.0, 140.0), window_size),
            None
        );
    }

    #[test]
    fn runtime_settings_keyboard_input_maps_privacy_and_data_controls() {
        let mut telemetry = ButtonInput::<KeyCode>::default();
        telemetry.press(KeyCode::Digit7);
        assert_eq!(
            runtime_settings_action_from_keyboard(&telemetry),
            Some(RuntimeSettingsAction::ToggleUpload(
                RuntimeUploadKind::Telemetry
            ))
        );

        let mut raw_replay = ButtonInput::<KeyCode>::default();
        raw_replay.press(KeyCode::Digit8);
        assert_eq!(
            runtime_settings_action_from_keyboard(&raw_replay),
            Some(RuntimeSettingsAction::ToggleUpload(
                RuntimeUploadKind::RawReplay
            ))
        );

        let mut crash_report = ButtonInput::<KeyCode>::default();
        crash_report.press(KeyCode::Digit9);
        assert_eq!(
            runtime_settings_action_from_keyboard(&crash_report),
            Some(RuntimeSettingsAction::ToggleUpload(
                RuntimeUploadKind::CrashReport
            ))
        );

        let mut export_save = ButtonInput::<KeyCode>::default();
        export_save.press(KeyCode::KeyE);
        assert_eq!(
            runtime_settings_action_from_keyboard(&export_save),
            Some(RuntimeSettingsAction::DataControl(
                RuntimeDataControlAction::ExportSave
            ))
        );

        let mut delete_local_data = ButtonInput::<KeyCode>::default();
        delete_local_data.press(KeyCode::KeyK);
        assert_eq!(
            runtime_settings_action_from_keyboard(&delete_local_data),
            Some(RuntimeSettingsAction::DataControl(
                RuntimeDataControlAction::DeleteLocalData
            ))
        );

        assert_eq!(
            runtime_settings_action_from_keyboard(&ButtonInput::<KeyCode>::default()),
            None
        );
    }

    #[test]
    fn runtime_settings_pointer_input_maps_left_click_zone() {
        let window_size = Vec2::new(1280.0, 720.0);

        let mut left = ButtonInput::<MouseButton>::default();
        left.press(MouseButton::Left);
        assert_eq!(
            runtime_settings_action_from_pointer(&left, Some(Vec2::new(1040.0, 40.0)), window_size),
            Some(RuntimeSettingsAction::DataControl(
                RuntimeDataControlAction::ExportSave
            ))
        );

        let mut right = ButtonInput::<MouseButton>::default();
        right.press(MouseButton::Right);
        assert_eq!(
            runtime_settings_action_from_pointer(
                &right,
                Some(Vec2::new(1040.0, 40.0)),
                window_size
            ),
            None
        );

        assert_eq!(
            runtime_settings_action_from_pointer(
                &ButtonInput::<MouseButton>::default(),
                Some(Vec2::new(1040.0, 40.0)),
                window_size
            ),
            None
        );
    }

    #[test]
    fn runtime_settings_pointer_zone_maps_right_panel_segments() {
        let window_size = Vec2::new(1280.0, 720.0);

        assert_eq!(
            runtime_settings_action_from_pointer_zone(Vec2::new(850.0, 40.0), window_size),
            Some(RuntimeSettingsAction::ToggleUpload(
                RuntimeUploadKind::Telemetry
            ))
        );
        assert_eq!(
            runtime_settings_action_from_pointer_zone(Vec2::new(920.0, 40.0), window_size),
            Some(RuntimeSettingsAction::ToggleUpload(
                RuntimeUploadKind::RawReplay
            ))
        );
        assert_eq!(
            runtime_settings_action_from_pointer_zone(Vec2::new(980.0, 40.0), window_size),
            Some(RuntimeSettingsAction::ToggleUpload(
                RuntimeUploadKind::CrashReport
            ))
        );
        assert_eq!(
            runtime_settings_action_from_pointer_zone(Vec2::new(1040.0, 40.0), window_size),
            Some(RuntimeSettingsAction::DataControl(
                RuntimeDataControlAction::ExportSave
            ))
        );
        assert_eq!(
            runtime_settings_action_from_pointer_zone(Vec2::new(1105.0, 40.0), window_size),
            Some(RuntimeSettingsAction::DataControl(
                RuntimeDataControlAction::DeleteSave
            ))
        );
        assert_eq!(
            runtime_settings_action_from_pointer_zone(Vec2::new(1165.0, 40.0), window_size),
            Some(RuntimeSettingsAction::DataControl(
                RuntimeDataControlAction::ExportLocalData
            ))
        );
        assert_eq!(
            runtime_settings_action_from_pointer_zone(Vec2::new(1230.0, 40.0), window_size),
            Some(RuntimeSettingsAction::DataControl(
                RuntimeDataControlAction::DeleteLocalData
            ))
        );
        assert_eq!(
            runtime_settings_action_from_pointer_zone(Vec2::new(500.0, 40.0), window_size),
            None
        );
        assert_eq!(
            runtime_settings_action_from_pointer_zone(Vec2::new(1040.0, 150.0), window_size),
            None
        );
    }

    #[test]
    fn runtime_settings_pointer_delete_action_uses_same_confirmation_path() {
        let root = std::env::temp_dir().join(format!(
            "soft-candy-runtime-f4-pointer-confirm-test-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(&root).unwrap();
        let save_file = root.join("profile.json");
        fs::write(&save_file, "{}\n").unwrap();

        let mut state = runtime_state_for_tests();
        state.platform_data_root = root.clone();
        state.save_file = Some(save_file.clone());
        let window_size = Vec2::new(1280.0, 720.0);
        let action =
            runtime_settings_action_from_pointer_zone(Vec2::new(1105.0, 40.0), window_size);

        assert_eq!(
            action,
            Some(RuntimeSettingsAction::DataControl(
                RuntimeDataControlAction::DeleteSave
            ))
        );
        let RuntimeSettingsAction::DataControl(data_action) = action.unwrap() else {
            panic!("delete save pointer zone must map to a data control action");
        };

        let message = run_runtime_data_control_action_from_state(&mut state, data_action).unwrap();
        assert!(message.contains("press X again"));
        assert!(save_file.exists());
        assert_eq!(
            state.pending_data_delete_action,
            Some(RuntimeDataControlAction::DeleteSave)
        );

        let message = run_runtime_data_control_action_from_state(&mut state, data_action).unwrap();
        assert!(message.contains("deleted save"));
        assert!(!save_file.exists());
        assert_eq!(state.pending_data_delete_action, None);

        let _ = fs::remove_dir_all(&root);
    }

    #[test]
    fn runtime_loadout_keyboard_input_maps_selection_actions() {
        let mut character = ButtonInput::<KeyCode>::default();
        character.press(KeyCode::KeyC);
        assert_eq!(
            runtime_loadout_action_from_keyboard(&character),
            Some(RuntimeLoadoutAction::NextCharacter)
        );

        let mut map = ButtonInput::<KeyCode>::default();
        map.press(KeyCode::KeyM);
        assert_eq!(
            runtime_loadout_action_from_keyboard(&map),
            Some(RuntimeLoadoutAction::NextMap)
        );

        assert_eq!(
            runtime_loadout_action_from_keyboard(&ButtonInput::<KeyCode>::default()),
            None
        );
    }

    #[test]
    fn runtime_loadout_gamepad_input_maps_selection_actions() {
        let gamepad = Gamepad::new(0);
        let mut character = ButtonInput::<GamepadButton>::default();
        character.press(GamepadButton::new(gamepad, GamepadButtonType::DPadLeft));
        assert_eq!(
            runtime_loadout_action_from_gamepad(&character),
            Some(RuntimeLoadoutAction::NextCharacter)
        );

        let mut map = ButtonInput::<GamepadButton>::default();
        map.press(GamepadButton::new(gamepad, GamepadButtonType::RightTrigger));
        assert_eq!(
            runtime_loadout_action_from_gamepad(&map),
            Some(RuntimeLoadoutAction::NextMap)
        );

        assert_eq!(
            runtime_loadout_action_from_gamepad(&ButtonInput::<GamepadButton>::default()),
            None
        );
    }

    #[test]
    fn runtime_loadout_pointer_input_maps_left_click_zone() {
        let window_size = Vec2::new(1280.0, 720.0);

        let mut left = ButtonInput::<MouseButton>::default();
        left.press(MouseButton::Left);
        assert_eq!(
            runtime_loadout_action_from_pointer(&left, Some(Vec2::new(900.0, 40.0)), window_size),
            Some(RuntimeLoadoutAction::NextCharacter)
        );

        let mut right = ButtonInput::<MouseButton>::default();
        right.press(MouseButton::Right);
        assert_eq!(
            runtime_loadout_action_from_pointer(&right, Some(Vec2::new(900.0, 40.0)), window_size),
            None
        );
    }

    #[test]
    fn runtime_loadout_pointer_zone_maps_right_panel_segments() {
        let window_size = Vec2::new(1280.0, 720.0);

        assert_eq!(
            runtime_loadout_action_from_pointer_zone(Vec2::new(900.0, 40.0), window_size),
            Some(RuntimeLoadoutAction::NextCharacter)
        );
        assert_eq!(
            runtime_loadout_action_from_pointer_zone(Vec2::new(1120.0, 40.0), window_size),
            Some(RuntimeLoadoutAction::NextMap)
        );
        assert_eq!(
            runtime_loadout_action_from_pointer_zone(Vec2::new(500.0, 40.0), window_size),
            None
        );
        assert_eq!(
            runtime_loadout_action_from_pointer_zone(Vec2::new(1120.0, 140.0), window_size),
            None
        );
    }

    #[test]
    fn meta_panel_hides_locked_codex_detail_until_discovered() {
        let mut base_ui_state = RuntimeBaseUiState::default();
        base_ui_state.codex_view.selected_category =
            RuntimeCodexCategory::Enemies.key().to_string();
        base_ui_state.codex_view.discovered_only = false;

        let panel = render_meta_progress_panel(
            &MetaProgress::demo_start(),
            None,
            RuntimeMetaPanelView::Codex,
            meta_panel_context(
                &RuntimePrivacySettings::default(),
                None,
                None,
                None,
                &ContentPack::base_demo(),
                &RunConfig::default(),
                &base_ui_state,
                0,
            ),
        );

        assert!(panel.contains("图鉴浏览 全部条目"));
        assert!(panel.contains("未发现条目"));
        assert!(panel.contains("bouncy-gummy"));
        assert!(panel.contains("继续巡逻、使用装备、击败敌人或解锁地图后显示说明"));
        assert!(!panel.contains("蹦蹦软糖"));
    }

    #[test]
    fn meta_panel_renders_story_codex_ui_candidate_status_without_text() {
        let candidate = RuntimeStoryCodexUiCandidateManifest {
            manifest_contract_id: "story-codex-ui-candidate-manifest-v0".to_string(),
            stage: "story_codex_ui_candidate".to_string(),
            candidate_pack_id: "2026-05-26_story_codex_seed_pack".to_string(),
            manual_gate_decision: "ui_candidate".to_string(),
            chapter_count: 6,
            codex_entry_count: 26,
            rules: RuntimeStoryCodexUiCandidateRules {
                accepted_content: false,
                runtime_integrated: false,
                requires_runtime_ui_review: true,
                requires_final_human_acceptance: true,
            },
        };
        let panel = render_meta_progress_panel(
            &MetaProgress::demo_start(),
            None,
            RuntimeMetaPanelView::Codex,
            meta_panel_context(
                &RuntimePrivacySettings::default(),
                None,
                Some(&candidate),
                None,
                &ContentPack::base_demo(),
                &RunConfig::default(),
                &RuntimeBaseUiState::default(),
                0,
            ),
        );

        assert!(panel.contains("剧情/图鉴 UI 候选"));
        assert!(panel.contains("2026-05-26_story_codex_seed_pack"));
        assert!(panel.contains("章节 6"));
        assert!(panel.contains("图鉴条目 26"));
        assert!(panel.contains("不读取 generated candidate 正文"));
        assert!(!panel.contains("糖罐星不是坏掉了"));
    }

    #[test]
    fn meta_panel_renders_asset_runtime_candidate_status_without_asset_loading() {
        let candidate = RuntimeAssetCandidateManifest {
            manifest_contract_id: "asset-runtime-candidate-manifest-v0".to_string(),
            stage: "asset_runtime_candidate".to_string(),
            candidate_batch_id: "2026-05-26_mmx_runtime_topdown_audio_plan".to_string(),
            manual_gate_decision: "asset_candidate".to_string(),
            asset_count: 2,
            assets: vec![
                RuntimeAssetCandidateItem {
                    id: "player_jar_keeper_topdown_v005_001".to_string(),
                    asset_type: "image".to_string(),
                    qa_status: "needs_visual_review".to_string(),
                    allowed_candidate_uses: vec!["runtime_preview_candidate".to_string()],
                },
                RuntimeAssetCandidateItem {
                    id: "voice_boss_arrival_cn_v002".to_string(),
                    asset_type: "audio".to_string(),
                    qa_status: "needs_audio_review".to_string(),
                    allowed_candidate_uses: vec!["runtime_preview_candidate".to_string()],
                },
            ],
            rules: RuntimeAssetCandidateRules {
                accepted_content: false,
                runtime_integrated: false,
                release_ready: false,
                requires_runtime_preview: true,
                requires_audio_loudness_review: true,
                requires_final_human_acceptance: true,
            },
        };
        let panel = render_meta_progress_panel(
            &MetaProgress::demo_start(),
            None,
            RuntimeMetaPanelView::Overview,
            meta_panel_context(
                &RuntimePrivacySettings::default(),
                None,
                None,
                Some(&candidate),
                &ContentPack::base_demo(),
                &RunConfig::default(),
                &RuntimeBaseUiState::default(),
                0,
            ),
        );

        assert!(panel.contains("素材 Runtime 候选"));
        assert!(panel.contains("2026-05-26_mmx_runtime_topdown_audio_plan"));
        assert!(panel.contains("素材 2"));
        assert!(panel.contains("audio:1"));
        assert!(panel.contains("image:1"));
        assert!(panel.contains("状态 asset_candidate 待预览"));
        assert!(panel.contains("不替换正式 Runtime 素材"));
    }

    #[test]
    fn meta_panel_renders_loadout_selection_view() {
        let mut progress = MetaProgress::demo_start();
        progress
            .unlocks
            .characters
            .insert("bubble-courier".to_string());
        progress.unlocks.maps.insert("soda-creek".to_string());
        let content = ContentPack::base_demo();
        let config = RunConfig {
            character_id: "bubble-courier".to_string(),
            map_id: "soda-creek".to_string(),
            starting_loadout: runtime_character_starting_loadout(&content, "bubble-courier"),
            ..RunConfig::default()
        };
        let panel = render_meta_progress_panel(
            &progress,
            None,
            RuntimeMetaPanelView::Loadout,
            meta_panel_context(
                &RuntimePrivacySettings::default(),
                None,
                None,
                None,
                &content,
                &config,
                &RuntimeBaseUiState::default(),
                0,
            ),
        );

        assert!(panel.contains("F5 巡逻"));
        assert!(panel.contains("巡逻准备"));
        assert!(panel.contains("泡泡邮差"));
        assert!(panel.contains("角色说明"));
        assert!(panel.contains("属性 HP"));
        assert!(panel.contains("特质 移动后短时间提升拾取范围"));
        assert!(panel.contains("汽水泡泡 (soda-bubble-pop)"));
        assert!(panel.contains("汽水溪谷"));
        assert!(panel.contains("地图说明"));
        assert!(panel.contains("地图标签"));
        assert!(panel.contains("章节 Boss 汽水喷泉龙 (soda-fountain-dragon)"));
        assert!(panel.contains("soda-bubble-pop"));
        assert!(panel.contains("C/手柄左 切换已解锁角色"));
        assert!(panel.contains("M/手柄右 切换已解锁地图"));
        assert!(panel.contains("右下点击区: 角色  地图"));
    }

    #[test]
    fn meta_panel_loadout_lists_full_demo_roster() {
        let content = ContentPack::base_demo();
        let mut progress = MetaProgress::demo_start();
        for id in content.characters.keys() {
            progress.unlocks.characters.insert(id.clone());
        }
        for id in content.maps.keys() {
            progress.unlocks.maps.insert(id.clone());
        }
        let config = RunConfig {
            character_id: "jar-keeper".to_string(),
            map_id: "frosting-grassland".to_string(),
            starting_loadout: runtime_character_starting_loadout(&content, "jar-keeper"),
            ..RunConfig::default()
        };

        let panel = render_meta_progress_panel(
            &progress,
            None,
            RuntimeMetaPanelView::Loadout,
            meta_panel_context(
                &RuntimePrivacySettings::default(),
                None,
                None,
                None,
                &content,
                &config,
                &RuntimeBaseUiState::default(),
                0,
            ),
        );

        for expected in [
            "糖罐守护员",
            "泡泡邮差",
            "奶油骑士",
            "酸梅博士",
            "布丁工匠",
            "糖霜草地",
            "汽水溪谷",
            "焦糖工坊",
            "棉花云牧场",
            "果冻月台",
            "裂星糖罐",
        ] {
            assert!(panel.contains(expected), "missing loadout label {expected}");
        }
        assert!(!panel.contains("还有"));
    }

    #[test]
    fn meta_panel_renders_privacy_settings_view() {
        let settings = RuntimePrivacySettings {
            telemetry_upload_enabled: true,
            raw_replay_upload_enabled: false,
            crash_report_upload_enabled: false,
        };
        let settings_path = PathBuf::from("harness/telemetry/local/runtime_settings.json");
        let panel = render_meta_progress_panel(
            &MetaProgress::demo_start(),
            None,
            RuntimeMetaPanelView::Settings,
            meta_panel_context(
                &settings,
                Some(settings_path.as_path()),
                None,
                None,
                &ContentPack::base_demo(),
                &RunConfig::default(),
                &RuntimeBaseUiState::default(),
                0,
            ),
        );

        assert!(panel.contains("隐私与本地数据"));
        assert!(panel.contains("上传匿名遥测: 已开启"));
        assert!(panel.contains("上传原始 Replay: 关闭"));
        assert!(panel.contains("E 导出存档"));
        assert!(panel.contains("X 删除存档"));
        assert!(panel.contains("L 导出本地数据"));
        assert!(panel.contains("K 删除本地数据"));
        assert!(panel.contains("X/K 删除需要再次按同一键确认"));
        assert!(panel.contains("exports/"));
        assert!(panel.contains("runtime_settings.json"));
        assert!(panel.contains("not_implemented"));
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
    fn upgrade_pointer_zone_maps_bottom_segments() {
        let window_size = Vec2::new(1280.0, 720.0);

        assert_eq!(
            upgrade_choice_from_pointer_zone(Vec2::new(120.0, 40.0), window_size, 3),
            Some(0)
        );
        assert_eq!(
            upgrade_choice_from_pointer_zone(Vec2::new(420.0, 40.0), window_size, 3),
            Some(1)
        );
        assert_eq!(
            upgrade_choice_from_pointer_zone(Vec2::new(720.0, 40.0), window_size, 3),
            Some(2)
        );
        assert_eq!(
            upgrade_choice_from_pointer_zone(Vec2::new(720.0, 40.0), window_size, 2),
            None
        );
        assert_eq!(
            upgrade_choice_from_pointer_zone(Vec2::new(980.0, 40.0), window_size, 3),
            None
        );
        assert_eq!(
            upgrade_choice_from_pointer_zone(Vec2::new(120.0, 260.0), window_size, 3),
            None
        );
    }

    #[test]
    fn upgrade_pointer_input_requires_left_click() {
        let window_size = Vec2::new(1280.0, 720.0);
        let mut left = ButtonInput::<MouseButton>::default();
        left.press(MouseButton::Left);
        let mut right = ButtonInput::<MouseButton>::default();
        right.press(MouseButton::Right);

        assert_eq!(
            upgrade_choice_from_pointer(&left, Some(Vec2::new(120.0, 40.0)), window_size, 3),
            Some(0)
        );
        assert_eq!(
            upgrade_choice_from_pointer(&right, Some(Vec2::new(120.0, 40.0)), window_size, 3),
            None
        );
        assert_eq!(
            upgrade_choice_from_pointer(&left, None, window_size, 3),
            None
        );
    }

    #[test]
    fn gamepad_dpad_movement_maps_cardinal_buttons() {
        let gamepad = Gamepad::new(0);
        let mut buttons = ButtonInput::<GamepadButton>::default();
        buttons.press(GamepadButton::new(gamepad, GamepadButtonType::DPadLeft));

        assert_eq!(
            movement_from_gamepad_buttons(&buttons),
            CoreVec2::new(-1.0, 0.0)
        );
    }

    #[test]
    fn gamepad_dpad_movement_normalizes_diagonals() {
        let gamepad = Gamepad::new(0);
        let mut buttons = ButtonInput::<GamepadButton>::default();
        buttons.press(GamepadButton::new(gamepad, GamepadButtonType::DPadRight));
        buttons.press(GamepadButton::new(gamepad, GamepadButtonType::DPadUp));

        let movement = movement_from_gamepad_buttons(&buttons);

        assert!((movement.x - std::f32::consts::FRAC_1_SQRT_2).abs() < 0.0001);
        assert!((movement.y - std::f32::consts::FRAC_1_SQRT_2).abs() < 0.0001);
    }

    #[test]
    fn gamepad_dpad_movement_returns_zero_without_buttons() {
        assert_eq!(
            movement_from_gamepad_buttons(&ButtonInput::<GamepadButton>::default()),
            CoreVec2::ZERO
        );
    }

    #[test]
    fn gamepad_left_stick_movement_preserves_analog_strength() {
        let gamepad = Gamepad::new(0);
        let mut axes = Axis::<GamepadAxis>::default();
        axes.set(GamepadAxis::new(gamepad, GamepadAxisType::LeftStickX), 0.5);

        assert_eq!(movement_from_gamepad_axes(&axes), CoreVec2::new(0.5, 0.0));
    }

    #[test]
    fn gamepad_left_stick_movement_applies_deadzone() {
        let gamepad = Gamepad::new(0);
        let mut axes = Axis::<GamepadAxis>::default();
        axes.set(GamepadAxis::new(gamepad, GamepadAxisType::LeftStickX), 0.05);
        axes.set(GamepadAxis::new(gamepad, GamepadAxisType::LeftStickY), 0.05);

        assert_eq!(movement_from_gamepad_axes(&axes), CoreVec2::ZERO);
    }

    #[test]
    fn gamepad_left_stick_movement_clamps_diagonal() {
        let gamepad = Gamepad::new(0);
        let mut axes = Axis::<GamepadAxis>::default();
        axes.set(GamepadAxis::new(gamepad, GamepadAxisType::LeftStickX), 1.0);
        axes.set(GamepadAxis::new(gamepad, GamepadAxisType::LeftStickY), 1.0);

        let movement = movement_from_gamepad_axes(&axes);

        assert!((movement.x - std::f32::consts::FRAC_1_SQRT_2).abs() < 0.0001);
        assert!((movement.y - std::f32::consts::FRAC_1_SQRT_2).abs() < 0.0001);
    }

    #[test]
    fn upgrade_gamepad_input_maps_face_buttons() {
        let gamepad = Gamepad::new(0);
        let mut south = ButtonInput::<GamepadButton>::default();
        south.press(GamepadButton::new(gamepad, GamepadButtonType::South));
        let mut east = ButtonInput::<GamepadButton>::default();
        east.press(GamepadButton::new(gamepad, GamepadButtonType::East));
        let mut north = ButtonInput::<GamepadButton>::default();
        north.press(GamepadButton::new(gamepad, GamepadButtonType::North));

        assert_eq!(upgrade_choice_from_gamepad(&south, 3), Some(0));
        assert_eq!(upgrade_choice_from_gamepad(&east, 3), Some(1));
        assert_eq!(upgrade_choice_from_gamepad(&north, 3), Some(2));
        assert_eq!(upgrade_choice_from_gamepad(&north, 2), None);
        assert_eq!(
            upgrade_choice_from_gamepad(&ButtonInput::<GamepadButton>::default(), 3),
            None
        );
    }

    #[test]
    fn upgrade_options_render_readable_choice_cards() {
        let options = vec![
            game_core::UpgradeOptionSnapshot {
                id: "rainbow-candy-shot-level-2".to_string(),
                name: "彩虹糖弹强化".to_string(),
                tags: vec!["projectile".to_string(), "single-target".to_string()],
                description: "提升伤害、射程和冷却节奏。".to_string(),
            },
            game_core::UpgradeOptionSnapshot {
                id: "soda-bubble-pop".to_string(),
                name: "获得汽水泡泡".to_string(),
                tags: vec!["控制".to_string()],
                description: "发射会弹跳的汽水泡泡。".to_string(),
            },
            game_core::UpgradeOptionSnapshot {
                id: "rainbow-candy-meteor".to_string(),
                name: "彩虹糖流星雨".to_string(),
                tags: vec![
                    "projectile".to_string(),
                    "aoe".to_string(),
                    "evolution".to_string(),
                ],
                description: "彩虹糖弹进化为周期性流星雨。".to_string(),
            },
        ];

        let rendered = format_upgrade_options(&options);

        assert!(rendered.contains("1. 彩虹糖弹强化"));
        assert!(rendered.contains("目标 Lv.2"));
        assert!(rendered.contains("提升伤害、射程和冷却节奏。"));
        assert!(rendered.contains("标签 弹幕 / 单体"));
        assert!(rendered.contains("id rainbow-candy-shot-level-2"));
        assert!(rendered.contains("2. 获得汽水泡泡"));
        assert!(rendered.contains("新获得"));
        assert!(rendered.contains("发射会弹跳的汽水泡泡。"));
        assert!(rendered.contains("3. 彩虹糖流星雨"));
        assert!(rendered.contains("进化"));
        assert!(rendered.contains("标签 弹幕 / 范围 / 进化"));
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
        assert_eq!(
            event_kind_for_events(&[GameEvent::ContentEventTriggered {
                event_id: "rainbow-candy-rush".to_string(),
            }]),
            RuntimeEventKind::System
        );
        assert_eq!(
            event_kind_for_events(&[GameEvent::BossAbilityUsed {
                entity_id: 30,
                boss_id: "caramel-furnace".to_string(),
                ability_id: "lay_caramel_tracks".to_string(),
            }]),
            RuntimeEventKind::Combat
        );
    }

    #[test]
    fn runtime_feedback_describes_events_with_content_labels() {
        let content = ContentPack::base_demo();

        assert_eq!(describe_events(&[], &content), "糖果风暴推进中");
        assert_eq!(
            describe_events(
                &[GameEvent::BossSpawned {
                    entity_id: 30,
                    boss_id: "runaway-sugar-mixer".to_string(),
                }],
                &content
            ),
            "Boss 出现 暴走搅糖机 (runaway-sugar-mixer)"
        );
        assert_eq!(
            describe_events(
                &[GameEvent::BossAbilityUsed {
                    entity_id: 30,
                    boss_id: "caramel-furnace".to_string(),
                    ability_id: "lay_caramel_tracks".to_string(),
                }],
                &content
            ),
            "Boss 焦糖熔炉 使用 铺设焦糖轨道"
        );
        assert_eq!(
            describe_events(
                &[GameEvent::EnemyKilled {
                    entity_id: 2,
                    enemy_id: "bouncy-gummy".to_string(),
                }],
                &content
            ),
            "击败 蹦蹦软糖"
        );
        assert_eq!(
            describe_events(
                &[GameEvent::ContentEventTriggered {
                    event_id: "rainbow-candy-rush".to_string(),
                }],
                &content
            ),
            "事件 彩虹糖潮 (rainbow-candy-rush)"
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
                GameEvent::BossAbilityUsed {
                    entity_id: 30,
                    boss_id: "runaway-sugar-mixer".to_string(),
                    ability_id: "dash_charge".to_string(),
                },
            ],
            &snapshot,
        );

        assert_eq!(effects.len(), 6);
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
        assert!(effects.iter().any(|effect| {
            effect.kind == RuntimeEffectKind::BossAbility && effect.position == boss_position
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
