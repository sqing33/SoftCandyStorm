use bot_policies::{BotController, BotKind};
use game_core::{
    ContentPack, Difficulty, FixedDt, GameCore, GameEvent, MetaProgress, MetaRunSummary,
    MetaSettlementReport, RunConfig, RunMetrics, StartingLoadout, TerminalKind, Vec2,
};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::BTreeSet;
use std::env;
use std::fs;
use std::io::{self, BufRead, Write};
use std::path::{Path, PathBuf};

const GYM_ACTION_COUNT: usize = 9;
const GYM_MAX_ENEMIES: usize = 8;
const GYM_MAX_PICKUPS: usize = 4;
const GYM_OBSERVATION_LEN: usize = 82;
const DEFAULT_MAP_ID: &str = "frosting-grassland";
const REQUIRED_PLAYTEST_RUN_IDS: [&str; 9] = [
    "new_001",
    "new_002",
    "new_003",
    "skilled_001",
    "skilled_002",
    "skilled_003",
    "build_001",
    "build_002",
    "build_003",
];
const ACCEPTANCE_RATING_FIELDS: [&str; 8] = [
    "fun_rating",
    "clarity_rating",
    "difficulty_rating",
    "projectile_readability",
    "hit_feedback",
    "xp_pickup_rhythm",
    "boss_spawn_clarity",
    "death_reason_clarity",
];

#[derive(Debug, Clone)]
struct SimArgs {
    seed: u64,
    map_id: String,
    seconds: f32,
    tick_rate: u32,
    bot: BotKind,
    content_dir: Option<PathBuf>,
}

impl Default for SimArgs {
    fn default() -> Self {
        Self {
            seed: 12_345,
            map_id: DEFAULT_MAP_ID.to_string(),
            seconds: 600.0,
            tick_rate: 30,
            bot: BotKind::Kite,
            content_dir: None,
        }
    }
}

#[derive(Debug, Clone)]
struct MetaSettlementArgs {
    seed: u64,
    map_id: String,
    seconds: f32,
    tick_rate: u32,
    bot: BotKind,
    content_dir: Option<PathBuf>,
    report_dir: Option<PathBuf>,
}

impl Default for MetaSettlementArgs {
    fn default() -> Self {
        Self {
            seed: 12_345,
            map_id: DEFAULT_MAP_ID.to_string(),
            seconds: 120.0,
            tick_rate: 30,
            bot: BotKind::Kite,
            content_dir: Some(PathBuf::from("content/base_demo")),
            report_dir: None,
        }
    }
}

#[derive(Debug, Clone)]
struct ValidateArgs {
    content_dir: PathBuf,
}

#[derive(Debug, Clone)]
struct BudgetArgs {
    content_dir: PathBuf,
}

impl Default for BudgetArgs {
    fn default() -> Self {
        Self {
            content_dir: PathBuf::from("content/base_demo"),
        }
    }
}

#[derive(Debug, Clone)]
struct BatchArgs {
    seed_start: u64,
    seeds: u64,
    map_id: String,
    seconds: f32,
    tick_rate: u32,
    bot: BotKind,
    content_dir: Option<PathBuf>,
    report_dir: Option<PathBuf>,
}

impl Default for BatchArgs {
    fn default() -> Self {
        Self {
            seed_start: 12_345,
            seeds: 10,
            map_id: DEFAULT_MAP_ID.to_string(),
            seconds: 600.0,
            tick_rate: 30,
            bot: BotKind::Kite,
            content_dir: Some(PathBuf::from("content/base_demo")),
            report_dir: None,
        }
    }
}

#[derive(Debug, Clone)]
struct MatrixArgs {
    seed_start: u64,
    seeds: u64,
    map_id: String,
    seconds: f32,
    tick_rate: u32,
    bots: Vec<BotKind>,
    content_dir: Option<PathBuf>,
    report_dir: Option<PathBuf>,
}

impl Default for MatrixArgs {
    fn default() -> Self {
        Self {
            seed_start: 12_345,
            seeds: 10,
            map_id: DEFAULT_MAP_ID.to_string(),
            seconds: 600.0,
            tick_rate: 30,
            bots: default_matrix_bots(),
            content_dir: Some(PathBuf::from("content/base_demo")),
            report_dir: None,
        }
    }
}

#[derive(Debug, Clone)]
struct ReplayArgs {
    replay_file: PathBuf,
    content_dir: Option<PathBuf>,
}

impl Default for ReplayArgs {
    fn default() -> Self {
        Self {
            replay_file: PathBuf::from("harness/replay/latest.json"),
            content_dir: Some(PathBuf::from("content/base_demo")),
        }
    }
}

#[derive(Debug, Clone)]
struct ReplayBatchArgs {
    replay_dir: PathBuf,
    content_dir: Option<PathBuf>,
    report_dir: Option<PathBuf>,
}

impl Default for ReplayBatchArgs {
    fn default() -> Self {
        Self {
            replay_dir: PathBuf::from("harness/replay"),
            content_dir: Some(PathBuf::from("content/base_demo")),
            report_dir: None,
        }
    }
}

#[derive(Debug, Clone)]
struct CandidateArgs {
    source_dir: PathBuf,
    validated_dir: PathBuf,
    rejected_dir: PathBuf,
    report_dir: Option<PathBuf>,
}

impl Default for CandidateArgs {
    fn default() -> Self {
        Self {
            source_dir: PathBuf::from("harness/generated_candidates"),
            validated_dir: PathBuf::from("harness/validated_candidates"),
            rejected_dir: PathBuf::from("harness/rejected_content"),
            report_dir: None,
        }
    }
}

#[derive(Debug, Clone)]
struct SimulateCandidatesArgs {
    source_dir: PathBuf,
    simulated_dir: PathBuf,
    repair_dir: PathBuf,
    report_dir: Option<PathBuf>,
    seed_start: u64,
    seeds: u64,
    seconds: f32,
    tick_rate: u32,
    bots: Vec<BotKind>,
}

#[derive(Debug, Clone)]
struct PromotePlaytestCandidatesArgs {
    source_dir: PathBuf,
    playtest_dir: PathBuf,
    repair_dir: PathBuf,
    report_dir: Option<PathBuf>,
}

impl Default for PromotePlaytestCandidatesArgs {
    fn default() -> Self {
        Self {
            source_dir: PathBuf::from("harness/simulated_candidates"),
            playtest_dir: PathBuf::from("harness/playtest_candidates"),
            repair_dir: PathBuf::from("harness/repair_queue"),
            report_dir: None,
        }
    }
}

#[derive(Debug, Clone)]
struct PromoteAcceptedCandidatesArgs {
    source_dir: PathBuf,
    accepted_dir: PathBuf,
    repair_dir: PathBuf,
    review_dir: PathBuf,
    report_dir: Option<PathBuf>,
}

impl Default for PromoteAcceptedCandidatesArgs {
    fn default() -> Self {
        Self {
            source_dir: PathBuf::from("harness/playtest_candidates"),
            accepted_dir: PathBuf::from("harness/accepted_content"),
            repair_dir: PathBuf::from("harness/repair_queue"),
            review_dir: PathBuf::from("harness/playtest_reviews"),
            report_dir: None,
        }
    }
}

#[derive(Debug, Clone)]
struct LockAcceptedContentArgs {
    accepted_dir: PathBuf,
    lock_file: PathBuf,
    runtime_content_root: PathBuf,
    report_dir: Option<PathBuf>,
}

impl Default for LockAcceptedContentArgs {
    fn default() -> Self {
        Self {
            accepted_dir: PathBuf::from("harness/accepted_content"),
            lock_file: PathBuf::from("harness/accepted_content/accepted_content.lock.json"),
            runtime_content_root: PathBuf::from("harness/accepted_content"),
            report_dir: None,
        }
    }
}

#[derive(Debug, Clone)]
struct GymBridgeArgs {
    seed: u64,
    map_id: String,
    seconds: f32,
    tick_rate: u32,
    content_dir: Option<PathBuf>,
}

impl Default for GymBridgeArgs {
    fn default() -> Self {
        Self {
            seed: 12_345,
            map_id: DEFAULT_MAP_ID.to_string(),
            seconds: 600.0,
            tick_rate: 30,
            content_dir: Some(PathBuf::from("content/base_demo")),
        }
    }
}

impl Default for SimulateCandidatesArgs {
    fn default() -> Self {
        Self {
            source_dir: PathBuf::from("harness/validated_candidates"),
            simulated_dir: PathBuf::from("harness/simulated_candidates"),
            repair_dir: PathBuf::from("harness/repair_queue"),
            report_dir: None,
            seed_start: 20_000,
            seeds: 10,
            seconds: 600.0,
            tick_rate: 30,
            bots: default_matrix_bots(),
        }
    }
}

#[derive(Debug, Clone)]
struct LoadedContent {
    pack: ContentPack,
    hash: String,
}

#[derive(Debug, Clone)]
struct SimulationRun {
    metrics: RunMetrics,
    replay: ReplayRecord,
}

#[derive(Debug, Clone)]
struct BotBatchResult {
    summary: BatchSummary,
    metrics: Vec<RunMetrics>,
    replays: Vec<ReplayRecord>,
}

#[derive(Debug, Clone, Serialize)]
struct MetaSettlementSmokeReport {
    report_version: u32,
    content_dir: String,
    bot: String,
    run_summary: MetaRunSummary,
    settlement: MetaSettlementReport,
    progress_after: MetaProgress,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ReplayRecord {
    replay_version: String,
    game_version: String,
    ruleset_version: String,
    content_hash: String,
    run_config: ReplayRunConfig,
    bot: String,
    tick_rate: u32,
    action_stream: Vec<ReplayActionFrame>,
    upgrade_choices: Vec<ReplayUpgradeChoice>,
    final_metrics: ReplayFinalMetrics,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ReplayRunConfig {
    seed: u64,
    map_id: String,
    character_id: String,
    starting_loadout: ReplayStartingLoadout,
    difficulty: String,
    duration_seconds: f32,
    content_pack_ids: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ReplayStartingLoadout {
    weapons: Vec<String>,
    passives: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ReplayActionFrame {
    tick: u64,
    movement: [f32; 2],
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ReplayUpgradeChoice {
    tick: u64,
    options: Vec<String>,
    chosen_index: usize,
    chosen_id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ReplayFinalMetrics {
    seed: u64,
    duration_seconds: f32,
    terminal: String,
    terminal_reason: String,
    kills: u32,
    level: u32,
    xp_collected: f32,
    xp_dropped: f32,
    damage_taken: f32,
    damage_dealt_by_weapon: f32,
    max_enemy_count: usize,
    max_projectile_count: usize,
    upgrade_choices: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
struct ReplayCheckReport {
    replay_file: String,
    status: &'static str,
    content_hash: String,
    expected_content_hash: String,
    bot: String,
    seed: u64,
    mismatches: Vec<String>,
    final_metrics: Option<ReplayFinalMetrics>,
}

#[derive(Debug, Clone, Serialize)]
struct ReplayBatchReport {
    replay_dir: String,
    content_hash: String,
    replay_count: usize,
    passed_count: usize,
    failed_count: usize,
    reports: Vec<ReplayCheckReport>,
}

#[derive(Debug, Clone, Serialize)]
struct CandidatePipelineReport {
    source_dir: String,
    validated_dir: String,
    rejected_dir: String,
    candidate_count: usize,
    validated_count: usize,
    rejected_count: usize,
    candidates: Vec<CandidateReview>,
}

#[derive(Debug, Clone, Serialize)]
struct StaticBudgetReport {
    status: &'static str,
    content_dir: String,
    weapon_budgets: Vec<WeaponBudgetReview>,
    enemy_budgets: Vec<EnemyBudgetReview>,
    wave_budgets: Vec<WaveBudgetReview>,
    warnings: Vec<String>,
    errors: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
struct WeaponBudgetReview {
    id: String,
    role: String,
    theoretical_single_target_dps: f32,
    declared_single_target_dps: f32,
    declared_group_dps: f32,
    performance_cost: String,
    status: &'static str,
    notes: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
struct EnemyBudgetReview {
    id: String,
    threat: f32,
    computed_threat: f32,
    speed_damage_pressure: f32,
    performance_cost: f32,
    status: &'static str,
    notes: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
struct WaveBudgetReview {
    id: String,
    max_spawn_pressure: f32,
    max_alive_pressure: f32,
    max_alive: usize,
    status: &'static str,
    notes: Vec<String>,
}

struct EnemyBudgetInput<'a> {
    id: &'a str,
    health: f32,
    move_speed: f32,
    contact_damage_per_second: f32,
    declared_threat: f32,
    performance_cost: f32,
}

#[derive(Debug, Clone, Serialize)]
struct CandidateReview {
    id: String,
    source: String,
    decision: &'static str,
    destination: String,
    object_count: Option<usize>,
    warnings: Vec<String>,
    errors: Vec<String>,
    budget_report: Option<StaticBudgetReport>,
}

#[derive(Debug, Clone, Serialize)]
struct CandidateSimulationReport {
    source_dir: String,
    simulated_dir: String,
    repair_dir: String,
    candidate_count: usize,
    simulated_count: usize,
    repair_count: usize,
    candidates: Vec<CandidateSimulationReview>,
}

#[derive(Debug, Clone, Serialize)]
struct CandidatePlaytestPromotionReport {
    source_dir: String,
    playtest_dir: String,
    repair_dir: String,
    candidate_count: usize,
    playtest_count: usize,
    repair_count: usize,
    candidates: Vec<CandidatePlaytestPromotionReview>,
}

#[derive(Debug, Clone, Serialize)]
struct CandidatePlaytestPromotionReview {
    id: String,
    source: String,
    decision: &'static str,
    destination: String,
    object_count: Option<usize>,
    content_hash: Option<String>,
    errors: Vec<String>,
    review_pack: Option<String>,
    next_step: String,
}

#[derive(Debug, Clone, Serialize)]
struct CandidateAcceptanceReport {
    source_dir: String,
    accepted_dir: String,
    repair_dir: String,
    review_dir: String,
    candidate_count: usize,
    accepted_count: usize,
    repair_count: usize,
    waiting_count: usize,
    candidates: Vec<CandidateAcceptanceReview>,
}

#[derive(Debug, Clone, Serialize)]
struct CandidateAcceptanceReview {
    id: String,
    source: String,
    decision: &'static str,
    destination: Option<String>,
    object_count: Option<usize>,
    content_hash: Option<String>,
    review_file: Option<String>,
    completed_run_count: usize,
    average_rating: Option<f32>,
    errors: Vec<String>,
    next_step: String,
}

#[derive(Debug, Clone, Serialize)]
struct AcceptedContentLockReport {
    lock_version: u32,
    status: &'static str,
    accepted_dir: String,
    lock_file: String,
    runtime_content_root: String,
    candidate_count: usize,
    locked_count: usize,
    blocked_count: usize,
    entries: Vec<AcceptedContentLockEntry>,
    errors: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
struct AcceptedContentLockEntry {
    id: String,
    source: String,
    runtime_content_dir: String,
    content_hash: Option<String>,
    object_count: Option<usize>,
    acceptance_gate: Option<String>,
    manual_review_file: Option<String>,
    completed_run_count: Option<usize>,
    average_rating: Option<f32>,
    status: &'static str,
    errors: Vec<String>,
}

#[derive(Debug, Clone)]
struct AcceptanceGateMetadata {
    manual_review_file: String,
    completed_run_count: usize,
    average_rating: Option<f32>,
}

#[derive(Debug, Clone)]
struct ManualAcceptanceGate {
    decision: ManualAcceptanceDecision,
    completed_run_count: usize,
    average_rating: Option<f32>,
    errors: Vec<String>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum ManualAcceptanceDecision {
    Accept,
    Repair,
    Waiting,
}

impl ManualAcceptanceDecision {
    fn as_str(self) -> &'static str {
        match self {
            Self::Accept => "accepted",
            Self::Repair => "repair",
            Self::Waiting => "waiting",
        }
    }
}

#[derive(Debug, Clone, Serialize)]
struct CandidateSimulationReview {
    id: String,
    source: String,
    decision: &'static str,
    destination: String,
    report_dir: String,
    gate_status: &'static str,
    failed_bots: Vec<String>,
    matrix_summary: Vec<CandidateBotSummary>,
}

#[derive(Debug, Clone, Serialize)]
struct CandidateBotSummary {
    bot: String,
    gate_status: &'static str,
    win_rate: f32,
    victories: usize,
    seeds: u64,
    average_duration_seconds: f32,
    average_level: f32,
    average_kills: f32,
    max_enemy_count: usize,
}

#[derive(Debug, Deserialize)]
struct GymBridgeRequest {
    command: String,
    seed: Option<u64>,
    map_id: Option<String>,
    seconds: Option<f32>,
    tick_rate: Option<u32>,
    action: Option<usize>,
}

#[derive(Debug, Serialize)]
struct GymBridgeResponse {
    command: String,
    status: String,
    observation: Option<Vec<f32>>,
    reward: f32,
    terminated: bool,
    truncated: bool,
    info: GymBridgeInfo,
    error: Option<String>,
}

#[derive(Debug, Serialize)]
struct GymBridgeInfo {
    seed: u64,
    map_id: String,
    tick_rate: u32,
    tick: u64,
    time_seconds: f32,
    health: f32,
    level: u32,
    kills: u32,
    xp_collected: f32,
    damage_taken: f32,
    upgrade_options: Vec<String>,
    events: Vec<String>,
    terminal: Option<GymTerminalInfo>,
    reward_breakdown: GymRewardBreakdown,
    content_hash: String,
    observation_len: usize,
    action_count: usize,
}

#[derive(Debug, Serialize, Clone, Copy, Default)]
struct GymRewardBreakdown {
    survival: f32,
    kill: f32,
    xp: f32,
    level: f32,
    damage_taken: f32,
    terminal: f32,
    total: f32,
}

#[derive(Debug, Serialize)]
struct GymTerminalInfo {
    kind: String,
    reason: String,
    time_seconds: f32,
    final_level: u32,
    kills: u32,
}

struct GymBridgeState {
    content: LoadedContent,
    core: GameCore,
    seed: u64,
    map_id: String,
    seconds: f32,
    tick_rate: u32,
    tick: u64,
}

fn main() {
    let mut args = env::args().skip(1);
    let Some(command) = args.next() else {
        print_help();
        return;
    };

    match command.as_str() {
        "simulate" => match parse_sim_args(args.collect()) {
            Ok(args) => run_simulation(args),
            Err(message) => {
                eprintln!("error: {message}");
                print_help();
                std::process::exit(2);
            }
        },
        "validate-content" => match parse_validate_args(args.collect()) {
            Ok(args) => run_validate(args),
            Err(message) => {
                eprintln!("error: {message}");
                print_help();
                std::process::exit(2);
            }
        },
        "budget-content" => match parse_budget_args(args.collect()) {
            Ok(args) => run_budget(args),
            Err(message) => {
                eprintln!("error: {message}");
                print_help();
                std::process::exit(2);
            }
        },
        "batch" => match parse_batch_args(args.collect()) {
            Ok(args) => run_batch(args),
            Err(message) => {
                eprintln!("error: {message}");
                print_help();
                std::process::exit(2);
            }
        },
        "matrix" => match parse_matrix_args(args.collect()) {
            Ok(args) => run_matrix(args),
            Err(message) => {
                eprintln!("error: {message}");
                print_help();
                std::process::exit(2);
            }
        },
        "replay" => match parse_replay_args(args.collect()) {
            Ok(args) => run_replay(args),
            Err(message) => {
                eprintln!("error: {message}");
                print_help();
                std::process::exit(2);
            }
        },
        "replay-batch" => match parse_replay_batch_args(args.collect()) {
            Ok(args) => run_replay_batch(args),
            Err(message) => {
                eprintln!("error: {message}");
                print_help();
                std::process::exit(2);
            }
        },
        "validate-candidates" => match parse_candidate_args(args.collect()) {
            Ok(args) => run_validate_candidates(args),
            Err(message) => {
                eprintln!("error: {message}");
                print_help();
                std::process::exit(2);
            }
        },
        "simulate-candidates" => match parse_simulate_candidates_args(args.collect()) {
            Ok(args) => run_simulate_candidates(args),
            Err(message) => {
                eprintln!("error: {message}");
                print_help();
                std::process::exit(2);
            }
        },
        "promote-playtest-candidates" => {
            match parse_promote_playtest_candidates_args(args.collect()) {
                Ok(args) => run_promote_playtest_candidates(args),
                Err(message) => {
                    eprintln!("error: {message}");
                    print_help();
                    std::process::exit(2);
                }
            }
        }
        "promote-accepted-candidates" => {
            match parse_promote_accepted_candidates_args(args.collect()) {
                Ok(args) => run_promote_accepted_candidates(args),
                Err(message) => {
                    eprintln!("error: {message}");
                    print_help();
                    std::process::exit(2);
                }
            }
        }
        "lock-accepted-content" => match parse_lock_accepted_content_args(args.collect()) {
            Ok(args) => run_lock_accepted_content(args),
            Err(message) => {
                eprintln!("error: {message}");
                print_help();
                std::process::exit(2);
            }
        },
        "meta-settlement" => match parse_meta_settlement_args(args.collect()) {
            Ok(args) => run_meta_settlement(args),
            Err(message) => {
                eprintln!("error: {message}");
                print_help();
                std::process::exit(2);
            }
        },
        "gym-bridge" => match parse_gym_bridge_args(args.collect()) {
            Ok(args) => run_gym_bridge(args),
            Err(message) => {
                eprintln!("error: {message}");
                print_help();
                std::process::exit(2);
            }
        },
        "--help" | "-h" | "help" => print_help(),
        _ => {
            eprintln!("error: unknown command `{command}`");
            print_help();
            std::process::exit(2);
        }
    }
}

fn parse_sim_args(values: Vec<String>) -> Result<SimArgs, String> {
    let mut parsed = SimArgs::default();
    let mut index = 0;
    while index < values.len() {
        let key = &values[index];
        let value = values
            .get(index + 1)
            .ok_or_else(|| format!("missing value for `{key}`"))?;
        match key.as_str() {
            "--seed" => {
                parsed.seed = value
                    .parse()
                    .map_err(|_| format!("invalid --seed `{value}`"))?;
            }
            "--map-id" => {
                parsed.map_id = value.to_string();
            }
            "--seconds" => {
                parsed.seconds = value
                    .parse()
                    .map_err(|_| format!("invalid --seconds `{value}`"))?;
            }
            "--tick-rate" => {
                parsed.tick_rate = value
                    .parse()
                    .map_err(|_| format!("invalid --tick-rate `{value}`"))?;
            }
            "--bot" => {
                parsed.bot = BotKind::parse(value).ok_or_else(|| {
                    format!("invalid --bot `{value}`; use {}", BotKind::all_names())
                })?;
            }
            "--content-dir" => {
                parsed.content_dir = Some(PathBuf::from(value));
            }
            _ => return Err(format!("unknown flag `{key}`")),
        }
        index += 2;
    }

    if parsed.seconds <= 0.0 {
        return Err("--seconds must be positive".to_string());
    }
    if parsed.tick_rate == 0 {
        return Err("--tick-rate must be greater than zero".to_string());
    }

    Ok(parsed)
}

fn parse_meta_settlement_args(values: Vec<String>) -> Result<MetaSettlementArgs, String> {
    let mut parsed = MetaSettlementArgs::default();
    let mut index = 0;
    while index < values.len() {
        let key = &values[index];
        let value = values
            .get(index + 1)
            .ok_or_else(|| format!("missing value for `{key}`"))?;
        match key.as_str() {
            "--seed" => {
                parsed.seed = value
                    .parse()
                    .map_err(|_| format!("invalid --seed `{value}`"))?;
            }
            "--map-id" => {
                parsed.map_id = value.to_string();
            }
            "--seconds" => {
                parsed.seconds = value
                    .parse()
                    .map_err(|_| format!("invalid --seconds `{value}`"))?;
            }
            "--tick-rate" => {
                parsed.tick_rate = value
                    .parse()
                    .map_err(|_| format!("invalid --tick-rate `{value}`"))?;
            }
            "--bot" => {
                parsed.bot = BotKind::parse(value).ok_or_else(|| {
                    format!("invalid --bot `{value}`; use {}", BotKind::all_names())
                })?;
            }
            "--content-dir" => {
                parsed.content_dir = Some(PathBuf::from(value));
            }
            "--report-dir" => {
                parsed.report_dir = Some(PathBuf::from(value));
            }
            _ => return Err(format!("unknown flag `{key}`")),
        }
        index += 2;
    }

    if parsed.seconds <= 0.0 {
        return Err("--seconds must be positive".to_string());
    }
    if parsed.tick_rate == 0 {
        return Err("--tick-rate must be greater than zero".to_string());
    }

    Ok(parsed)
}

fn parse_validate_args(values: Vec<String>) -> Result<ValidateArgs, String> {
    let mut content_dir = PathBuf::from("content/base_demo");
    let mut index = 0;
    while index < values.len() {
        let key = &values[index];
        let value = values
            .get(index + 1)
            .ok_or_else(|| format!("missing value for `{key}`"))?;
        match key.as_str() {
            "--content-dir" => {
                content_dir = PathBuf::from(value);
            }
            _ => return Err(format!("unknown flag `{key}`")),
        }
        index += 2;
    }
    Ok(ValidateArgs { content_dir })
}

fn parse_budget_args(values: Vec<String>) -> Result<BudgetArgs, String> {
    let mut parsed = BudgetArgs::default();
    let mut index = 0;
    while index < values.len() {
        let key = &values[index];
        let value = values
            .get(index + 1)
            .ok_or_else(|| format!("missing value for `{key}`"))?;
        match key.as_str() {
            "--content-dir" => {
                parsed.content_dir = PathBuf::from(value);
            }
            _ => return Err(format!("unknown flag `{key}`")),
        }
        index += 2;
    }
    Ok(parsed)
}

fn parse_batch_args(values: Vec<String>) -> Result<BatchArgs, String> {
    let mut parsed = BatchArgs::default();
    let mut index = 0;
    while index < values.len() {
        let key = &values[index];
        let value = values
            .get(index + 1)
            .ok_or_else(|| format!("missing value for `{key}`"))?;
        match key.as_str() {
            "--seed-start" => {
                parsed.seed_start = value
                    .parse()
                    .map_err(|_| format!("invalid --seed-start `{value}`"))?;
            }
            "--seeds" => {
                parsed.seeds = value
                    .parse()
                    .map_err(|_| format!("invalid --seeds `{value}`"))?;
            }
            "--map-id" => {
                parsed.map_id = value.to_string();
            }
            "--seconds" => {
                parsed.seconds = value
                    .parse()
                    .map_err(|_| format!("invalid --seconds `{value}`"))?;
            }
            "--tick-rate" => {
                parsed.tick_rate = value
                    .parse()
                    .map_err(|_| format!("invalid --tick-rate `{value}`"))?;
            }
            "--bot" => {
                parsed.bot = BotKind::parse(value).ok_or_else(|| {
                    format!("invalid --bot `{value}`; use {}", BotKind::all_names())
                })?;
            }
            "--content-dir" => {
                parsed.content_dir = Some(PathBuf::from(value));
            }
            "--report-dir" => {
                parsed.report_dir = Some(PathBuf::from(value));
            }
            _ => return Err(format!("unknown flag `{key}`")),
        }
        index += 2;
    }

    if parsed.seeds == 0 {
        return Err("--seeds must be greater than zero".to_string());
    }
    if parsed.seconds <= 0.0 {
        return Err("--seconds must be positive".to_string());
    }
    if parsed.tick_rate == 0 {
        return Err("--tick-rate must be greater than zero".to_string());
    }

    Ok(parsed)
}

fn parse_matrix_args(values: Vec<String>) -> Result<MatrixArgs, String> {
    let mut parsed = MatrixArgs::default();
    let mut index = 0;
    while index < values.len() {
        let key = &values[index];
        let value = values
            .get(index + 1)
            .ok_or_else(|| format!("missing value for `{key}`"))?;
        match key.as_str() {
            "--seed-start" => {
                parsed.seed_start = value
                    .parse()
                    .map_err(|_| format!("invalid --seed-start `{value}`"))?;
            }
            "--seeds" => {
                parsed.seeds = value
                    .parse()
                    .map_err(|_| format!("invalid --seeds `{value}`"))?;
            }
            "--map-id" => {
                parsed.map_id = value.to_string();
            }
            "--seconds" => {
                parsed.seconds = value
                    .parse()
                    .map_err(|_| format!("invalid --seconds `{value}`"))?;
            }
            "--tick-rate" => {
                parsed.tick_rate = value
                    .parse()
                    .map_err(|_| format!("invalid --tick-rate `{value}`"))?;
            }
            "--bots" => {
                parsed.bots = parse_bot_list(value)?;
            }
            "--content-dir" => {
                parsed.content_dir = Some(PathBuf::from(value));
            }
            "--report-dir" => {
                parsed.report_dir = Some(PathBuf::from(value));
            }
            _ => return Err(format!("unknown flag `{key}`")),
        }
        index += 2;
    }

    if parsed.seeds == 0 {
        return Err("--seeds must be greater than zero".to_string());
    }
    if parsed.seconds <= 0.0 {
        return Err("--seconds must be positive".to_string());
    }
    if parsed.tick_rate == 0 {
        return Err("--tick-rate must be greater than zero".to_string());
    }
    if parsed.bots.is_empty() {
        return Err("--bots must include at least one bot".to_string());
    }

    Ok(parsed)
}

fn parse_replay_args(values: Vec<String>) -> Result<ReplayArgs, String> {
    let mut parsed = ReplayArgs::default();
    let mut index = 0;
    while index < values.len() {
        let key = &values[index];
        let value = values
            .get(index + 1)
            .ok_or_else(|| format!("missing value for `{key}`"))?;
        match key.as_str() {
            "--replay-file" => {
                parsed.replay_file = PathBuf::from(value);
            }
            "--content-dir" => {
                parsed.content_dir = Some(PathBuf::from(value));
            }
            _ => return Err(format!("unknown flag `{key}`")),
        }
        index += 2;
    }
    Ok(parsed)
}

fn parse_replay_batch_args(values: Vec<String>) -> Result<ReplayBatchArgs, String> {
    let mut parsed = ReplayBatchArgs::default();
    let mut index = 0;
    while index < values.len() {
        let key = &values[index];
        let value = values
            .get(index + 1)
            .ok_or_else(|| format!("missing value for `{key}`"))?;
        match key.as_str() {
            "--replay-dir" => {
                parsed.replay_dir = PathBuf::from(value);
            }
            "--content-dir" => {
                parsed.content_dir = Some(PathBuf::from(value));
            }
            "--report-dir" => {
                parsed.report_dir = Some(PathBuf::from(value));
            }
            _ => return Err(format!("unknown flag `{key}`")),
        }
        index += 2;
    }
    Ok(parsed)
}

fn parse_candidate_args(values: Vec<String>) -> Result<CandidateArgs, String> {
    let mut parsed = CandidateArgs::default();
    let mut index = 0;
    while index < values.len() {
        let key = &values[index];
        let value = values
            .get(index + 1)
            .ok_or_else(|| format!("missing value for `{key}`"))?;
        match key.as_str() {
            "--source-dir" => {
                parsed.source_dir = PathBuf::from(value);
            }
            "--validated-dir" => {
                parsed.validated_dir = PathBuf::from(value);
            }
            "--rejected-dir" => {
                parsed.rejected_dir = PathBuf::from(value);
            }
            "--report-dir" => {
                parsed.report_dir = Some(PathBuf::from(value));
            }
            _ => return Err(format!("unknown flag `{key}`")),
        }
        index += 2;
    }
    Ok(parsed)
}

fn parse_simulate_candidates_args(values: Vec<String>) -> Result<SimulateCandidatesArgs, String> {
    let mut parsed = SimulateCandidatesArgs::default();
    let mut index = 0;
    while index < values.len() {
        let key = &values[index];
        let value = values
            .get(index + 1)
            .ok_or_else(|| format!("missing value for `{key}`"))?;
        match key.as_str() {
            "--source-dir" => {
                parsed.source_dir = PathBuf::from(value);
            }
            "--simulated-dir" => {
                parsed.simulated_dir = PathBuf::from(value);
            }
            "--repair-dir" => {
                parsed.repair_dir = PathBuf::from(value);
            }
            "--report-dir" => {
                parsed.report_dir = Some(PathBuf::from(value));
            }
            "--seed-start" => {
                parsed.seed_start = value
                    .parse()
                    .map_err(|_| format!("invalid --seed-start `{value}`"))?;
            }
            "--seeds" => {
                parsed.seeds = value
                    .parse()
                    .map_err(|_| format!("invalid --seeds `{value}`"))?;
            }
            "--seconds" => {
                parsed.seconds = value
                    .parse()
                    .map_err(|_| format!("invalid --seconds `{value}`"))?;
            }
            "--tick-rate" => {
                parsed.tick_rate = value
                    .parse()
                    .map_err(|_| format!("invalid --tick-rate `{value}`"))?;
            }
            "--bots" => {
                parsed.bots = parse_bot_list(value)?;
            }
            _ => return Err(format!("unknown flag `{key}`")),
        }
        index += 2;
    }

    if parsed.seeds == 0 {
        return Err("--seeds must be greater than zero".to_string());
    }
    if parsed.seconds <= 0.0 {
        return Err("--seconds must be positive".to_string());
    }
    if parsed.tick_rate == 0 {
        return Err("--tick-rate must be greater than zero".to_string());
    }
    if parsed.bots.is_empty() {
        return Err("--bots must include at least one bot".to_string());
    }

    Ok(parsed)
}

fn parse_promote_playtest_candidates_args(
    values: Vec<String>,
) -> Result<PromotePlaytestCandidatesArgs, String> {
    let mut parsed = PromotePlaytestCandidatesArgs::default();
    let mut index = 0;
    while index < values.len() {
        let key = &values[index];
        let value = values
            .get(index + 1)
            .ok_or_else(|| format!("missing value for `{key}`"))?;
        match key.as_str() {
            "--source-dir" => {
                parsed.source_dir = PathBuf::from(value);
            }
            "--playtest-dir" => {
                parsed.playtest_dir = PathBuf::from(value);
            }
            "--repair-dir" => {
                parsed.repair_dir = PathBuf::from(value);
            }
            "--report-dir" => {
                parsed.report_dir = Some(PathBuf::from(value));
            }
            _ => return Err(format!("unknown flag `{key}`")),
        }
        index += 2;
    }
    Ok(parsed)
}

fn parse_promote_accepted_candidates_args(
    values: Vec<String>,
) -> Result<PromoteAcceptedCandidatesArgs, String> {
    let mut parsed = PromoteAcceptedCandidatesArgs::default();
    let mut index = 0;
    while index < values.len() {
        let key = &values[index];
        let value = values
            .get(index + 1)
            .ok_or_else(|| format!("missing value for `{key}`"))?;
        match key.as_str() {
            "--source-dir" => {
                parsed.source_dir = PathBuf::from(value);
            }
            "--accepted-dir" => {
                parsed.accepted_dir = PathBuf::from(value);
            }
            "--repair-dir" => {
                parsed.repair_dir = PathBuf::from(value);
            }
            "--review-dir" => {
                parsed.review_dir = PathBuf::from(value);
            }
            "--report-dir" => {
                parsed.report_dir = Some(PathBuf::from(value));
            }
            _ => return Err(format!("unknown flag `{key}`")),
        }
        index += 2;
    }
    Ok(parsed)
}

fn parse_lock_accepted_content_args(
    values: Vec<String>,
) -> Result<LockAcceptedContentArgs, String> {
    let mut parsed = LockAcceptedContentArgs::default();
    let mut index = 0;
    while index < values.len() {
        let key = &values[index];
        let value = values
            .get(index + 1)
            .ok_or_else(|| format!("missing value for `{key}`"))?;
        match key.as_str() {
            "--accepted-dir" => {
                parsed.accepted_dir = PathBuf::from(value);
            }
            "--lock-file" => {
                parsed.lock_file = PathBuf::from(value);
            }
            "--runtime-content-root" => {
                parsed.runtime_content_root = PathBuf::from(value);
            }
            "--report-dir" => {
                parsed.report_dir = Some(PathBuf::from(value));
            }
            _ => return Err(format!("unknown flag `{key}`")),
        }
        index += 2;
    }
    Ok(parsed)
}

fn parse_gym_bridge_args(values: Vec<String>) -> Result<GymBridgeArgs, String> {
    let mut parsed = GymBridgeArgs::default();
    let mut index = 0;
    while index < values.len() {
        let key = &values[index];
        let value = values
            .get(index + 1)
            .ok_or_else(|| format!("missing value for `{key}`"))?;
        match key.as_str() {
            "--seed" => {
                parsed.seed = value
                    .parse()
                    .map_err(|_| format!("invalid --seed `{value}`"))?;
            }
            "--map-id" => {
                parsed.map_id = value.to_string();
            }
            "--seconds" => {
                parsed.seconds = value
                    .parse()
                    .map_err(|_| format!("invalid --seconds `{value}`"))?;
            }
            "--tick-rate" => {
                parsed.tick_rate = value
                    .parse()
                    .map_err(|_| format!("invalid --tick-rate `{value}`"))?;
            }
            "--content-dir" => {
                parsed.content_dir = Some(PathBuf::from(value));
            }
            _ => return Err(format!("unknown flag `{key}`")),
        }
        index += 2;
    }

    if parsed.seconds <= 0.0 {
        return Err("--seconds must be positive".to_string());
    }
    if parsed.tick_rate == 0 {
        return Err("--tick-rate must be greater than zero".to_string());
    }

    Ok(parsed)
}

fn parse_bot_list(value: &str) -> Result<Vec<BotKind>, String> {
    if value == "all" {
        return Ok(default_matrix_bots());
    }

    value
        .split(',')
        .map(|raw| {
            let name = raw.trim();
            BotKind::parse(name)
                .ok_or_else(|| format!("invalid bot `{name}`; use {}", BotKind::all_names()))
        })
        .collect()
}

fn default_matrix_bots() -> Vec<BotKind> {
    vec![
        BotKind::Idle,
        BotKind::Random,
        BotKind::Coward,
        BotKind::Greedy,
        BotKind::Kite,
        BotKind::Tank,
        BotKind::BossHunter,
        BotKind::ZoneControl,
        BotKind::Route,
    ]
}

fn run_simulation(args: SimArgs) {
    let content = load_content_or_exit(args.content_dir.as_ref());
    let run = simulate_once(
        &content.pack,
        &content.hash,
        args.seed,
        &args.map_id,
        args.seconds,
        args.tick_rate,
        args.bot,
    );
    print_metrics_json(&run.metrics, args.bot, &args.map_id);
}

fn simulate_once(
    content: &ContentPack,
    content_hash: &str,
    seed: u64,
    map_id: &str,
    seconds: f32,
    tick_rate: u32,
    bot: BotKind,
) -> SimulationRun {
    let config = harness_run_config(seed, map_id, seconds, tick_rate);
    let replay_run_config = ReplayRunConfig::from_config(&config);
    let ruleset_version = config.ruleset_version.clone();
    let mut core = match GameCore::reset_with_content(config, content.clone()) {
        Ok(core) => core,
        Err(error) => {
            eprintln!("error: {error}");
            std::process::exit(1);
        }
    };
    let dt = FixedDt::from_tick_rate(tick_rate);
    let max_steps = (seconds * tick_rate as f32) as usize + 10_000;
    let mut steps = 0usize;
    let mut controller = BotController::new(bot, seed);
    let mut action_stream = Vec::new();
    let mut upgrade_choices = Vec::new();
    let mut last_movement: Option<[f32; 2]> = None;

    while !core.is_terminal() && steps < max_steps {
        let snapshot = core.snapshot();
        let action = controller.next_action(&snapshot);
        let movement = [action.movement.x, action.movement.y];

        if movement_changed(last_movement, movement) {
            action_stream.push(ReplayActionFrame {
                tick: steps as u64,
                movement,
            });
            last_movement = Some(movement);
        }

        if let Some(chosen_index) = action.upgrade_choice {
            let options = snapshot
                .upgrade_options
                .iter()
                .map(|option| option.id.clone())
                .collect::<Vec<_>>();
            let chosen_id = options
                .get(chosen_index)
                .cloned()
                .unwrap_or_else(|| "invalid-choice".to_string());
            upgrade_choices.push(ReplayUpgradeChoice {
                tick: steps as u64,
                options,
                chosen_index,
                chosen_id,
            });
        }

        core.step(action, dt);
        steps += 1;
    }

    let metrics = core.metrics();
    let replay = ReplayRecord {
        replay_version: "prototype-replay-v0".to_string(),
        game_version: "prototype-v0".to_string(),
        ruleset_version,
        content_hash: content_hash.to_string(),
        run_config: replay_run_config,
        bot: bot.as_str().to_string(),
        tick_rate,
        action_stream,
        upgrade_choices,
        final_metrics: ReplayFinalMetrics::from_metrics(&metrics),
    };

    SimulationRun { metrics, replay }
}

fn harness_run_config(seed: u64, map_id: &str, seconds: f32, tick_rate: u32) -> RunConfig {
    RunConfig {
        seed,
        map_id: map_id.to_string(),
        character_id: "jar-keeper".to_string(),
        starting_loadout: StartingLoadout {
            weapons: vec!["rainbow-candy-shot".to_string()],
            passives: Vec::new(),
        },
        difficulty: Difficulty::Normal,
        duration_seconds: seconds,
        ruleset_version: "prototype-v0".to_string(),
        content_pack_ids: vec!["base-demo".to_string()],
        tick_rate,
    }
}

fn print_metrics_json(metrics: &RunMetrics, bot: BotKind, map_id: &str) {
    let terminal_kind = metrics
        .terminal
        .as_ref()
        .map(|terminal| terminal.kind.as_str())
        .unwrap_or("not_terminal");
    let terminal_reason = metrics
        .terminal
        .as_ref()
        .map(|terminal| terminal.reason.as_str())
        .unwrap_or("step_limit_reached");

    println!("{{");
    println!("  \"seed\": {},", metrics.seed);
    println!("  \"bot\": \"{}\",", bot.as_str());
    println!("  \"map_id\": \"{}\",", map_id);
    println!("  \"tick_rate\": {},", metrics.tick_rate);
    println!("  \"duration_seconds\": {:.3},", metrics.duration_seconds);
    println!("  \"terminal\": \"{}\",", terminal_kind);
    println!("  \"reason\": \"{}\",", terminal_reason);
    println!("  \"kills\": {},", metrics.kills);
    println!("  \"level\": {},", metrics.level);
    println!("  \"xp_collected\": {:.3},", metrics.xp_collected);
    println!("  \"xp_dropped\": {:.3},", metrics.xp_dropped);
    println!(
        "  \"damage_dealt_by_weapon\": {:.3},",
        metrics.damage_dealt_by_weapon
    );
    println!("  \"damage_taken\": {:.3},", metrics.damage_taken);
    println!("  \"max_enemy_count\": {},", metrics.max_enemy_count);
    println!(
        "  \"max_projectile_count\": {},",
        metrics.max_projectile_count
    );
    println!("  \"upgrade_choices\": [");
    for (index, choice) in metrics.upgrade_choices.iter().enumerate() {
        let suffix = if index + 1 == metrics.upgrade_choices.len() {
            ""
        } else {
            ","
        };
        println!("    \"{}\"{}", choice, suffix);
    }
    println!("  ]");
    println!("}}");
}

fn run_batch(args: BatchArgs) {
    let content = load_content_or_exit(args.content_dir.as_ref());
    let result = run_bot_batch(
        &content,
        args.bot,
        args.seed_start,
        args.seeds,
        &args.map_id,
        args.seconds,
        args.tick_rate,
    );

    if let Some(report_dir) = &args.report_dir {
        write_report_or_exit(report_dir, &result);
    }

    print_batch_json(&result.summary, &result.metrics);
}

fn run_meta_settlement(args: MetaSettlementArgs) {
    let content = load_content_or_exit(args.content_dir.as_ref());
    let config = harness_run_config(args.seed, &args.map_id, args.seconds, args.tick_rate);
    let run = simulate_once(
        &content.pack,
        &content.hash,
        args.seed,
        &args.map_id,
        args.seconds,
        args.tick_rate,
        args.bot,
    );
    let run_summary = MetaRunSummary::from_metrics(
        format!("{}_seed_{}", args.bot.as_str(), args.seed),
        &config,
        &run.metrics,
    );
    let mut progress = MetaProgress::demo_start();
    let settlement = progress.apply_run_summary(&run_summary);
    let content_dir = args
        .content_dir
        .as_ref()
        .map(|path| path.display().to_string())
        .unwrap_or_else(|| "builtin:base-demo".to_string());
    let report = MetaSettlementSmokeReport {
        report_version: 1,
        content_dir,
        bot: args.bot.as_str().to_string(),
        run_summary,
        settlement,
        progress_after: progress,
    };

    if let Some(report_dir) = &args.report_dir {
        if let Err(error) = write_meta_settlement_report(report_dir, &report) {
            eprintln!(
                "error: failed to write meta settlement report `{}`: {error}",
                report_dir.display()
            );
            std::process::exit(1);
        }
    }

    match serde_json::to_string_pretty(&report) {
        Ok(json) => println!("{json}"),
        Err(error) => {
            eprintln!("error: failed to render meta settlement report: {error}");
            std::process::exit(1);
        }
    }
}

fn run_matrix(args: MatrixArgs) {
    let content = load_content_or_exit(args.content_dir.as_ref());
    let mut matrix_results = Vec::new();

    for bot in &args.bots {
        matrix_results.push(run_bot_batch(
            &content,
            *bot,
            args.seed_start,
            args.seeds,
            &args.map_id,
            args.seconds,
            args.tick_rate,
        ));
    }

    if let Some(report_dir) = &args.report_dir {
        write_matrix_report_or_exit(report_dir, &matrix_results);
    }

    print_matrix_json(&matrix_results);
}

fn run_replay(args: ReplayArgs) {
    let content = load_content_or_exit(args.content_dir.as_ref());
    let report = replay_check_report(&content, &args.replay_file);
    let failed = report.status != "ok";
    print_replay_check_report(&report);

    if failed {
        std::process::exit(1);
    }
}

fn run_replay_batch(args: ReplayBatchArgs) {
    let content = load_content_or_exit(args.content_dir.as_ref());
    let report = match replay_batch_report(&content, &args.replay_dir) {
        Ok(report) => report,
        Err(error) => {
            eprintln!(
                "error: failed to run replay batch `{}`: {error}",
                args.replay_dir.display()
            );
            std::process::exit(1);
        }
    };

    if let Some(report_dir) = &args.report_dir {
        if let Err(error) = write_replay_batch_report(report_dir, &report) {
            eprintln!(
                "error: failed to write replay batch report `{}`: {error}",
                report_dir.display()
            );
            std::process::exit(1);
        }
    }

    match serde_json::to_string_pretty(&report) {
        Ok(json) => println!("{json}"),
        Err(error) => {
            eprintln!("error: failed to render replay batch report: {error}");
            std::process::exit(1);
        }
    }

    if report.failed_count > 0 {
        std::process::exit(1);
    }
}

fn run_validate_candidates(args: CandidateArgs) {
    let report = match validate_candidate_dirs(&args) {
        Ok(report) => report,
        Err(error) => {
            eprintln!("error: failed to validate candidates: {error}");
            std::process::exit(1);
        }
    };

    if let Some(report_dir) = &args.report_dir {
        if let Err(error) = write_candidate_report(report_dir, &report) {
            eprintln!(
                "error: failed to write candidate report `{}`: {error}",
                report_dir.display()
            );
            std::process::exit(1);
        }
    }

    match serde_json::to_string_pretty(&report) {
        Ok(json) => println!("{json}"),
        Err(error) => {
            eprintln!("error: failed to render candidate report: {error}");
            std::process::exit(1);
        }
    }
}

fn run_simulate_candidates(args: SimulateCandidatesArgs) {
    let report = match simulate_candidate_dirs(&args) {
        Ok(report) => report,
        Err(error) => {
            eprintln!("error: failed to simulate candidates: {error}");
            std::process::exit(1);
        }
    };

    if let Some(report_dir) = &args.report_dir {
        if let Err(error) = write_candidate_simulation_report(report_dir, &report) {
            eprintln!(
                "error: failed to write candidate simulation report `{}`: {error}",
                report_dir.display()
            );
            std::process::exit(1);
        }
    }

    match serde_json::to_string_pretty(&report) {
        Ok(json) => println!("{json}"),
        Err(error) => {
            eprintln!("error: failed to render candidate simulation report: {error}");
            std::process::exit(1);
        }
    }
}

fn run_promote_playtest_candidates(args: PromotePlaytestCandidatesArgs) {
    let report = match promote_playtest_candidate_dirs(&args) {
        Ok(report) => report,
        Err(error) => {
            eprintln!("error: failed to promote playtest candidates: {error}");
            std::process::exit(1);
        }
    };

    if let Some(report_dir) = &args.report_dir {
        if let Err(error) = write_candidate_playtest_promotion_report(report_dir, &report) {
            eprintln!(
                "error: failed to write playtest promotion report `{}`: {error}",
                report_dir.display()
            );
            std::process::exit(1);
        }
    }

    match serde_json::to_string_pretty(&report) {
        Ok(json) => println!("{json}"),
        Err(error) => {
            eprintln!("error: failed to render playtest promotion report: {error}");
            std::process::exit(1);
        }
    }
}

fn run_promote_accepted_candidates(args: PromoteAcceptedCandidatesArgs) {
    let report = match promote_accepted_candidate_dirs(&args) {
        Ok(report) => report,
        Err(error) => {
            eprintln!("error: failed to promote accepted candidates: {error}");
            std::process::exit(1);
        }
    };

    if let Some(report_dir) = &args.report_dir {
        if let Err(error) = write_candidate_acceptance_report(report_dir, &report) {
            eprintln!(
                "error: failed to write accepted candidate report `{}`: {error}",
                report_dir.display()
            );
            std::process::exit(1);
        }
    }

    match serde_json::to_string_pretty(&report) {
        Ok(json) => println!("{json}"),
        Err(error) => {
            eprintln!("error: failed to render accepted candidate report: {error}");
            std::process::exit(1);
        }
    }
}

fn run_lock_accepted_content(args: LockAcceptedContentArgs) {
    let report = match lock_accepted_content_dirs(&args) {
        Ok(report) => report,
        Err(error) => {
            eprintln!("error: failed to lock accepted content: {error}");
            std::process::exit(1);
        }
    };

    if let Some(report_dir) = &args.report_dir {
        if let Err(error) = write_accepted_content_lock_report(report_dir, &report) {
            eprintln!(
                "error: failed to write accepted content lock report `{}`: {error}",
                report_dir.display()
            );
            std::process::exit(1);
        }
    }

    match serde_json::to_string_pretty(&report) {
        Ok(json) => println!("{json}"),
        Err(error) => {
            eprintln!("error: failed to render accepted content lock report: {error}");
            std::process::exit(1);
        }
    }

    if report.blocked_count > 0 {
        std::process::exit(1);
    }
}

fn run_budget(args: BudgetArgs) {
    let pack = match ContentPack::load_from_dir(&args.content_dir) {
        Ok(pack) => pack,
        Err(error) => {
            eprintln!("error: {error}");
            std::process::exit(1);
        }
    };
    let report = evaluate_static_budget(&pack, args.content_dir.display().to_string());
    match serde_json::to_string_pretty(&report) {
        Ok(json) => println!("{json}"),
        Err(error) => {
            eprintln!("error: failed to render budget report: {error}");
            std::process::exit(1);
        }
    }
    if !report.errors.is_empty() {
        std::process::exit(1);
    }
}

fn run_gym_bridge(args: GymBridgeArgs) {
    let content = load_content_or_exit(args.content_dir.as_ref());
    let mut state = GymBridgeState::new(
        content,
        args.seed,
        args.map_id.clone(),
        args.seconds,
        args.tick_rate,
    );
    let stdin = io::stdin();
    let mut stdout = io::stdout().lock();

    for line in stdin.lock().lines() {
        let line = match line {
            Ok(line) => line,
            Err(error) => {
                eprintln!("error: failed to read gym bridge request: {error}");
                std::process::exit(1);
            }
        };
        if line.trim().is_empty() {
            continue;
        }

        let request = match serde_json::from_str::<GymBridgeRequest>(&line) {
            Ok(request) => request,
            Err(error) => {
                let response = state
                    .error_response("parse_error", format!("failed to parse request: {error}"));
                write_json_line_or_exit(&mut stdout, &response);
                continue;
            }
        };

        let should_close = request.command == "close";
        let response = state.handle_request(request);
        write_json_line_or_exit(&mut stdout, &response);
        if should_close {
            break;
        }
    }
}

impl GymBridgeState {
    fn new(
        content: LoadedContent,
        seed: u64,
        map_id: String,
        seconds: f32,
        tick_rate: u32,
    ) -> Self {
        let core = reset_gym_core(&content.pack, seed, &map_id, seconds, tick_rate);
        Self {
            content,
            core,
            seed,
            map_id,
            seconds,
            tick_rate,
            tick: 0,
        }
    }

    fn reset(&mut self, seed: u64, map_id: String, seconds: f32, tick_rate: u32) {
        self.core = reset_gym_core(&self.content.pack, seed, &map_id, seconds, tick_rate);
        self.seed = seed;
        self.map_id = map_id;
        self.seconds = seconds;
        self.tick_rate = tick_rate;
        self.tick = 0;
    }

    fn handle_request(&mut self, request: GymBridgeRequest) -> GymBridgeResponse {
        match request.command.as_str() {
            "spec" => self.response("spec", None, 0.0, Vec::new(), GymRewardBreakdown::default()),
            "reset" => {
                let seed = request.seed.unwrap_or(self.seed);
                let map_id = request.map_id.unwrap_or_else(|| self.map_id.clone());
                let seconds = request.seconds.unwrap_or(self.seconds);
                let tick_rate = request.tick_rate.unwrap_or(self.tick_rate);
                if seconds <= 0.0 {
                    return self.error_response("reset", "seconds must be positive".to_string());
                }
                if tick_rate == 0 {
                    return self.error_response(
                        "reset",
                        "tick_rate must be greater than zero".to_string(),
                    );
                }
                self.reset(seed, map_id, seconds, tick_rate);
                self.response(
                    "reset",
                    Some(gym_observation(&self.core.snapshot())),
                    0.0,
                    Vec::new(),
                    GymRewardBreakdown::default(),
                )
            }
            "step" => {
                let Some(action_index) = request.action else {
                    return self.error_response("step", "step request missing action".to_string());
                };
                if action_index >= GYM_ACTION_COUNT {
                    return self.error_response(
                        "step",
                        format!("action must be in 0..{}", GYM_ACTION_COUNT),
                    );
                }
                self.step(action_index)
            }
            "close" => self.response(
                "close",
                None,
                0.0,
                Vec::new(),
                GymRewardBreakdown::default(),
            ),
            other => self.error_response("unknown_command", format!("unknown command `{other}`")),
        }
    }

    fn step(&mut self, action_index: usize) -> GymBridgeResponse {
        if self.core.is_terminal() {
            return self.response(
                "step",
                Some(gym_observation(&self.core.snapshot())),
                0.0,
                Vec::new(),
                GymRewardBreakdown::default(),
            );
        }

        let snapshot = self.core.snapshot();
        let action = if snapshot.upgrade_options.is_empty() {
            game_core::PlayerAction {
                movement: gym_discrete_movement(action_index),
                upgrade_choice: None,
            }
        } else {
            game_core::PlayerAction {
                movement: Vec2::ZERO,
                upgrade_choice: Some(0),
            }
        };
        let result = self
            .core
            .step(action, FixedDt::from_tick_rate(self.tick_rate));
        self.tick += 1;
        let reward_breakdown = gym_reward_breakdown(
            &result.reward_hint,
            &result.events,
            result.terminal.as_ref(),
        );

        self.response(
            "step",
            Some(gym_observation(&result.snapshot)),
            reward_breakdown.total,
            result.events,
            reward_breakdown,
        )
    }

    fn response(
        &self,
        command: &str,
        observation: Option<Vec<f32>>,
        reward: f32,
        events: Vec<GameEvent>,
        reward_breakdown: GymRewardBreakdown,
    ) -> GymBridgeResponse {
        let metrics = self.core.metrics();
        GymBridgeResponse {
            command: command.to_string(),
            status: "ok".to_string(),
            observation,
            reward,
            terminated: metrics.terminal.is_some(),
            truncated: false,
            info: self.info(events, reward_breakdown),
            error: None,
        }
    }

    fn error_response(&self, command: &str, error: String) -> GymBridgeResponse {
        GymBridgeResponse {
            command: command.to_string(),
            status: "error".to_string(),
            observation: None,
            reward: 0.0,
            terminated: self.core.metrics().terminal.is_some(),
            truncated: false,
            info: self.info(Vec::new(), GymRewardBreakdown::default()),
            error: Some(error),
        }
    }

    fn info(&self, events: Vec<GameEvent>, reward_breakdown: GymRewardBreakdown) -> GymBridgeInfo {
        let snapshot = self.core.snapshot();
        let metrics = self.core.metrics();
        GymBridgeInfo {
            seed: self.seed,
            map_id: self.map_id.clone(),
            tick_rate: self.tick_rate,
            tick: self.tick,
            time_seconds: snapshot.time_seconds,
            health: snapshot.player.health,
            level: snapshot.player.level,
            kills: metrics.kills,
            xp_collected: metrics.xp_collected,
            damage_taken: metrics.damage_taken,
            upgrade_options: snapshot
                .upgrade_options
                .iter()
                .map(|option| option.id.clone())
                .collect(),
            events: events
                .iter()
                .map(gym_event_label)
                .map(str::to_string)
                .collect(),
            terminal: metrics.terminal.map(|terminal| GymTerminalInfo {
                kind: terminal.kind.as_str().to_string(),
                reason: terminal.reason,
                time_seconds: terminal.time_seconds,
                final_level: terminal.final_level,
                kills: terminal.kills,
            }),
            reward_breakdown,
            content_hash: self.content.hash.clone(),
            observation_len: GYM_OBSERVATION_LEN,
            action_count: GYM_ACTION_COUNT,
        }
    }
}

fn reset_gym_core(
    content: &ContentPack,
    seed: u64,
    map_id: &str,
    seconds: f32,
    tick_rate: u32,
) -> GameCore {
    let config = RunConfig {
        seed,
        map_id: map_id.to_string(),
        character_id: "jar-keeper".to_string(),
        starting_loadout: StartingLoadout {
            weapons: vec!["rainbow-candy-shot".to_string()],
            passives: Vec::new(),
        },
        difficulty: Difficulty::Normal,
        duration_seconds: seconds,
        ruleset_version: "prototype-v0".to_string(),
        content_pack_ids: vec!["base-demo".to_string()],
        tick_rate,
    };
    match GameCore::reset_with_content(config, content.clone()) {
        Ok(core) => core,
        Err(error) => {
            eprintln!("error: failed to reset gym bridge: {error}");
            std::process::exit(1);
        }
    }
}

fn gym_discrete_movement(action: usize) -> Vec2 {
    match action {
        0 => Vec2::ZERO,
        1 => Vec2::new(0.0, 1.0),
        2 => Vec2::new(1.0, 1.0).normalized_or_zero(),
        3 => Vec2::new(1.0, 0.0),
        4 => Vec2::new(1.0, -1.0).normalized_or_zero(),
        5 => Vec2::new(0.0, -1.0),
        6 => Vec2::new(-1.0, -1.0).normalized_or_zero(),
        7 => Vec2::new(-1.0, 0.0),
        8 => Vec2::new(-1.0, 1.0).normalized_or_zero(),
        _ => Vec2::ZERO,
    }
}

fn gym_reward_breakdown(
    hint: &game_core::RewardHint,
    events: &[GameEvent],
    terminal: Option<&game_core::TerminalState>,
) -> GymRewardBreakdown {
    let kill_delta = events
        .iter()
        .filter(|event| matches!(event, GameEvent::EnemyKilled { .. }))
        .count() as f32;
    let survival = hint.survival_delta * 0.01;
    let kill = kill_delta * 0.05;
    let xp = hint.xp_delta * 0.02;
    let level = hint.level_delta as f32 * 0.5;
    let damage_taken = -hint.damage_taken_delta * 0.05;

    let terminal = if let Some(terminal) = terminal {
        match terminal.kind {
            TerminalKind::Victory => 5.0,
            TerminalKind::Defeat => -2.0,
            TerminalKind::Timeout => 0.0,
            TerminalKind::Aborted => -1.0,
            TerminalKind::InvalidState => -5.0,
        }
    } else {
        0.0
    };

    let total = survival + kill + xp + level + damage_taken + terminal;
    GymRewardBreakdown {
        survival,
        kill,
        xp,
        level,
        damage_taken,
        terminal,
        total,
    }
}

fn gym_observation(snapshot: &game_core::RunSnapshot) -> Vec<f32> {
    let mut values = Vec::with_capacity(GYM_OBSERVATION_LEN);
    let duration = (snapshot.time_seconds + snapshot.remaining_seconds).max(1.0);
    let max_dim = snapshot.map.width.max(snapshot.map.height).max(1.0);
    let half_width = (snapshot.map.width * 0.5).max(1.0);
    let half_height = (snapshot.map.height * 0.5).max(1.0);
    let player = &snapshot.player;

    values.push(snapshot.time_seconds / duration);
    values.push(snapshot.remaining_seconds / duration);
    values.push(ratio(player.health, player.max_health));
    values.push((player.level as f32 / 20.0).min(1.0));
    values.push(ratio(player.xp, player.xp_to_next_level));
    values.push(player.position.x / half_width);
    values.push(player.position.y / half_height);
    values.push(player.velocity.length() / player.move_speed.max(1.0));

    for enemy in snapshot.visible_enemies.iter().take(GYM_MAX_ENEMIES) {
        let relative = enemy.position - player.position;
        values.push(relative.x / snapshot.map.width.max(1.0));
        values.push(relative.y / snapshot.map.height.max(1.0));
        values.push(relative.length() / max_dim);
        values.push(ratio(enemy.health, enemy.max_health));
        values.push((enemy.threat / 100.0).min(1.0));
        values.push(if enemy.is_boss { 1.0 } else { 0.0 });
    }
    while values.len() < 8 + GYM_MAX_ENEMIES * 6 {
        values.push(0.0);
    }

    for pickup in snapshot.visible_pickups.iter().take(GYM_MAX_PICKUPS) {
        let relative = pickup.position - player.position;
        values.push(relative.x / snapshot.map.width.max(1.0));
        values.push(relative.y / snapshot.map.height.max(1.0));
        values.push(relative.length() / max_dim);
        values.push((pickup.value / 10.0).min(1.0));
    }
    while values.len() < 8 + GYM_MAX_ENEMIES * 6 + GYM_MAX_PICKUPS * 4 {
        values.push(0.0);
    }

    values.push((player.position.x + half_width) / snapshot.map.width.max(1.0));
    values.push((half_width - player.position.x) / snapshot.map.width.max(1.0));
    values.push((player.position.y + half_height) / snapshot.map.height.max(1.0));
    values.push((half_height - player.position.y) / snapshot.map.height.max(1.0));
    values.push((snapshot.build.weapons.len() as f32 / 6.0).min(1.0));
    values.push((snapshot.build.passives.len() as f32 / 6.0).min(1.0));
    values.push((snapshot.build.tags.len() as f32 / 12.0).min(1.0));
    values.push((snapshot.visible_enemies.len() as f32 / 32.0).min(1.0));
    values.push((snapshot.visible_pickups.len() as f32 / 16.0).min(1.0));
    values.push((snapshot.visible_projectiles.len() as f32 / 48.0).min(1.0));

    debug_assert_eq!(values.len(), GYM_OBSERVATION_LEN);
    values
}

fn ratio(value: f32, max: f32) -> f32 {
    if max <= 0.0 {
        0.0
    } else {
        (value / max).clamp(0.0, 1.0)
    }
}

fn gym_event_label(event: &GameEvent) -> &'static str {
    match event {
        GameEvent::EnemySpawned { .. } => "enemy_spawned",
        GameEvent::BossSpawned { .. } => "boss_spawned",
        GameEvent::BossPhaseChanged { .. } => "boss_phase_changed",
        GameEvent::BossAbilityUsed { .. } => "boss_ability_used",
        GameEvent::WeaponFired { .. } => "weapon_fired",
        GameEvent::EnemyHit { .. } => "enemy_hit",
        GameEvent::EnemyKilled { .. } => "enemy_killed",
        GameEvent::XpDropped { .. } => "xp_dropped",
        GameEvent::XpCollected { .. } => "xp_collected",
        GameEvent::LevelUp { .. } => "level_up",
        GameEvent::UpgradeOffered { .. } => "upgrade_offered",
        GameEvent::UpgradeChosen { .. } => "upgrade_chosen",
        GameEvent::PlayerDamaged { .. } => "player_damaged",
        GameEvent::ContentEventTriggered { .. } => "content_event_triggered",
        GameEvent::RunEnded { .. } => "run_ended",
    }
}

fn write_json_line_or_exit<T: Serialize>(writer: &mut impl Write, value: &T) {
    if let Err(error) = serde_json::to_writer(&mut *writer, value)
        .and_then(|()| writer.write_all(b"\n").map_err(serde_json::Error::io))
        .and_then(|()| writer.flush().map_err(serde_json::Error::io))
    {
        eprintln!("error: failed to write gym bridge response: {error}");
        std::process::exit(1);
    }
}

fn replay_run_config_to_config(replay: &ReplayRecord) -> Result<RunConfig, String> {
    let difficulty = match replay.run_config.difficulty.as_str() {
        "normal" => Difficulty::Normal,
        value => return Err(format!("unsupported replay difficulty `{value}`")),
    };

    Ok(RunConfig {
        seed: replay.run_config.seed,
        map_id: replay.run_config.map_id.clone(),
        character_id: replay.run_config.character_id.clone(),
        starting_loadout: StartingLoadout {
            weapons: replay.run_config.starting_loadout.weapons.clone(),
            passives: replay.run_config.starting_loadout.passives.clone(),
        },
        difficulty,
        duration_seconds: replay.run_config.duration_seconds,
        ruleset_version: replay.ruleset_version.clone(),
        content_pack_ids: replay.run_config.content_pack_ids.clone(),
        tick_rate: replay.tick_rate,
    })
}

fn replay_check_report(content: &LoadedContent, replay_file: &Path) -> ReplayCheckReport {
    let replay_text = match fs::read_to_string(replay_file) {
        Ok(text) => text,
        Err(error) => {
            return ReplayCheckReport {
                replay_file: replay_file.display().to_string(),
                status: "failed",
                content_hash: content.hash.clone(),
                expected_content_hash: String::new(),
                bot: "unknown".to_string(),
                seed: 0,
                mismatches: vec![format!("failed to read replay: {error}")],
                final_metrics: None,
            };
        }
    };
    let replay = match serde_json::from_str::<ReplayRecord>(&replay_text) {
        Ok(replay) => replay,
        Err(error) => {
            return ReplayCheckReport {
                replay_file: replay_file.display().to_string(),
                status: "failed",
                content_hash: content.hash.clone(),
                expected_content_hash: String::new(),
                bot: "unknown".to_string(),
                seed: 0,
                mismatches: vec![format!("failed to parse replay: {error}")],
                final_metrics: None,
            };
        }
    };

    if replay.content_hash != content.hash {
        let loaded_hash = content.hash.clone();
        return ReplayCheckReport {
            replay_file: replay_file.display().to_string(),
            status: "failed",
            content_hash: loaded_hash.clone(),
            expected_content_hash: replay.content_hash.clone(),
            bot: replay.bot.clone(),
            seed: replay.run_config.seed,
            mismatches: vec![format!(
                "content_hash mismatch: replay expected `{}`, loaded `{}`",
                replay.content_hash, loaded_hash
            )],
            final_metrics: None,
        };
    }

    let config = match replay_run_config_to_config(&replay) {
        Ok(config) => config,
        Err(message) => {
            return ReplayCheckReport {
                replay_file: replay_file.display().to_string(),
                status: "failed",
                content_hash: content.hash.clone(),
                expected_content_hash: replay.content_hash.clone(),
                bot: replay.bot.clone(),
                seed: replay.run_config.seed,
                mismatches: vec![message],
                final_metrics: None,
            };
        }
    };

    match replay_once(&content.pack, config, &replay) {
        Ok(metrics) => {
            let mut mismatches = compare_replay_metrics(&replay.final_metrics, &metrics);
            if !mismatches.is_empty() {
                mismatches.insert(
                    0,
                    "strict replay final metrics did not match recorded metrics".to_string(),
                );
            }

            ReplayCheckReport {
                replay_file: replay_file.display().to_string(),
                status: if mismatches.is_empty() {
                    "ok"
                } else {
                    "failed"
                },
                content_hash: content.hash.clone(),
                expected_content_hash: replay.content_hash.clone(),
                bot: replay.bot.clone(),
                seed: replay.run_config.seed,
                mismatches,
                final_metrics: Some(ReplayFinalMetrics::from_metrics(&metrics)),
            }
        }
        Err(error) => ReplayCheckReport {
            replay_file: replay_file.display().to_string(),
            status: "failed",
            content_hash: content.hash.clone(),
            expected_content_hash: replay.content_hash.clone(),
            bot: replay.bot.clone(),
            seed: replay.run_config.seed,
            mismatches: vec![error],
            final_metrics: None,
        },
    }
}

fn replay_batch_report(
    content: &LoadedContent,
    replay_dir: &Path,
) -> io::Result<ReplayBatchReport> {
    let mut replay_files = Vec::new();
    collect_replay_files(replay_dir, &mut replay_files)?;
    replay_files.sort();

    let reports = replay_files
        .iter()
        .map(|replay_file| replay_check_report(content, replay_file))
        .collect::<Vec<_>>();
    let passed_count = reports
        .iter()
        .filter(|report| report.status == "ok")
        .count();
    let failed_count = reports.len().saturating_sub(passed_count);

    Ok(ReplayBatchReport {
        replay_dir: replay_dir.display().to_string(),
        content_hash: content.hash.clone(),
        replay_count: reports.len(),
        passed_count,
        failed_count,
        reports,
    })
}

fn collect_replay_files(path: &Path, replay_files: &mut Vec<PathBuf>) -> io::Result<()> {
    if !path.exists() {
        return Ok(());
    }
    for entry in fs::read_dir(path)? {
        let entry = entry?;
        let path = entry.path();
        if path.is_dir() {
            collect_replay_files(&path, replay_files)?;
        } else if path
            .extension()
            .is_some_and(|extension| extension == "json")
        {
            replay_files.push(path);
        }
    }
    Ok(())
}

fn replay_once(
    content: &ContentPack,
    config: RunConfig,
    replay: &ReplayRecord,
) -> Result<RunMetrics, String> {
    let tick_rate = config.tick_rate;
    let mut core = match GameCore::reset_with_content(config, content.clone()) {
        Ok(core) => core,
        Err(error) => return Err(format!("failed to reset replay: {error}")),
    };
    let dt = FixedDt::from_tick_rate(tick_rate);
    let max_steps = (replay.run_config.duration_seconds * tick_rate as f32) as usize + 10_000;
    let mut steps = 0usize;
    let mut action_index = 0usize;
    let mut upgrade_index = 0usize;
    let mut movement = Vec2::ZERO;

    while !core.is_terminal() && steps < max_steps {
        while action_index < replay.action_stream.len()
            && replay.action_stream[action_index].tick <= steps as u64
        {
            let frame = &replay.action_stream[action_index];
            movement = Vec2::new(frame.movement[0], frame.movement[1]);
            action_index += 1;
        }

        let snapshot = core.snapshot();
        let mut upgrade_choice = None;
        if !snapshot.upgrade_options.is_empty() {
            if upgrade_index >= replay.upgrade_choices.len() {
                let actual_options = snapshot
                    .upgrade_options
                    .iter()
                    .map(|option| option.id.clone())
                    .collect::<Vec<_>>();
                return Err(format!(
                    "unrecorded upgrade prompt at tick {}: {:?}",
                    steps, actual_options
                ));
            }

            let expected = &replay.upgrade_choices[upgrade_index];
            let actual_options = snapshot
                .upgrade_options
                .iter()
                .map(|option| option.id.clone())
                .collect::<Vec<_>>();
            if actual_options != expected.options {
                return Err(format!(
                    "upgrade options mismatch at tick {}: expected {:?}, got {:?}",
                    steps, expected.options, actual_options
                ));
            }
            upgrade_choice = Some(expected.chosen_index);
            movement = Vec2::ZERO;
            upgrade_index += 1;
        }

        core.step(
            game_core::PlayerAction {
                movement,
                upgrade_choice,
            },
            dt,
        );
        steps += 1;
    }

    if upgrade_index != replay.upgrade_choices.len() {
        return Err(format!(
            "replay ended before consuming all upgrade choices: consumed {}, expected {}",
            upgrade_index,
            replay.upgrade_choices.len()
        ));
    }

    Ok(core.metrics())
}

fn compare_replay_metrics(expected: &ReplayFinalMetrics, actual: &RunMetrics) -> Vec<String> {
    let mut mismatches = Vec::new();
    let actual_terminal = actual
        .terminal
        .as_ref()
        .map(|terminal| terminal.kind.as_str())
        .unwrap_or("not_terminal");
    let actual_reason = actual
        .terminal
        .as_ref()
        .map(|terminal| terminal.reason.as_str())
        .unwrap_or("step_limit_reached");

    if expected.terminal != actual_terminal {
        mismatches.push(format!(
            "terminal mismatch: expected `{}`, got `{}`",
            expected.terminal, actual_terminal
        ));
    }
    if expected.terminal_reason != actual_reason {
        mismatches.push(format!(
            "terminal_reason mismatch: expected `{}`, got `{}`",
            expected.terminal_reason, actual_reason
        ));
    }
    if !float_close(expected.duration_seconds, actual.duration_seconds, 0.05) {
        mismatches.push(format!(
            "duration_seconds mismatch: expected {:.3}, got {:.3}",
            expected.duration_seconds, actual.duration_seconds
        ));
    }
    if expected.kills != actual.kills {
        mismatches.push(format!(
            "kills mismatch: expected {}, got {}",
            expected.kills, actual.kills
        ));
    }
    if expected.level != actual.level {
        mismatches.push(format!(
            "level mismatch: expected {}, got {}",
            expected.level, actual.level
        ));
    }
    if !float_close(expected.damage_taken, actual.damage_taken, 0.05) {
        mismatches.push(format!(
            "damage_taken mismatch: expected {:.3}, got {:.3}",
            expected.damage_taken, actual.damage_taken
        ));
    }
    if expected.max_enemy_count != actual.max_enemy_count {
        mismatches.push(format!(
            "max_enemy_count mismatch: expected {}, got {}",
            expected.max_enemy_count, actual.max_enemy_count
        ));
    }
    if expected.upgrade_choices != actual.upgrade_choices {
        mismatches.push(format!(
            "upgrade_choices mismatch: expected {:?}, got {:?}",
            expected.upgrade_choices, actual.upgrade_choices
        ));
    }

    mismatches
}

fn float_close(left: f32, right: f32, tolerance: f32) -> bool {
    (left - right).abs() <= tolerance
}

fn print_replay_check_report(report: &ReplayCheckReport) {
    match serde_json::to_string_pretty(report) {
        Ok(json) => println!("{json}"),
        Err(error) => {
            eprintln!("error: failed to render replay check report: {error}");
            std::process::exit(1);
        }
    }
}

fn write_replay_batch_report(report_dir: &Path, report: &ReplayBatchReport) -> io::Result<()> {
    fs::create_dir_all(report_dir)?;
    let json = serde_json::to_string_pretty(report).map_err(io::Error::other)?;
    fs::write(
        report_dir.join("replay_regression.json"),
        format!("{json}\n"),
    )?;
    fs::write(
        report_dir.join("summary.md"),
        render_replay_batch_summary(report),
    )?;
    Ok(())
}

fn render_replay_batch_summary(report: &ReplayBatchReport) -> String {
    let mut output = String::new();
    output.push_str("# Replay Regression Summary\n\n");
    output.push_str(&format!("- Replay dir: `{}`\n", report.replay_dir));
    output.push_str(&format!("- Content hash: `{}`\n", report.content_hash));
    output.push_str(&format!(
        "- Result: `{}` passed, `{}` failed, `{}` total\n\n",
        report.passed_count, report.failed_count, report.replay_count
    ));
    output.push_str("| Replay | Status | Bot | Seed | Mismatches |\n");
    output.push_str("|---|---|---|---:|---:|\n");
    for replay in &report.reports {
        output.push_str(&format!(
            "| {} | {} | {} | {} | {} |\n",
            replay.replay_file,
            replay.status,
            replay.bot,
            replay.seed,
            replay.mismatches.len()
        ));
    }
    output
}

fn summarize_batch(
    bot: BotKind,
    seed_start: u64,
    seeds: u64,
    map_id: &str,
    seconds: f32,
    tick_rate: u32,
    results: &[RunMetrics],
) -> BatchSummary {
    let victories = results
        .iter()
        .filter(|metrics| {
            metrics
                .terminal
                .as_ref()
                .is_some_and(|terminal| terminal.kind == TerminalKind::Victory)
        })
        .count();
    let average_duration = results
        .iter()
        .map(|metrics| metrics.duration_seconds)
        .sum::<f32>()
        / results.len() as f32;
    let average_level = results
        .iter()
        .map(|metrics| metrics.level as f32)
        .sum::<f32>()
        / results.len() as f32;
    let average_kills = results
        .iter()
        .map(|metrics| metrics.kills as f32)
        .sum::<f32>()
        / results.len() as f32;
    let max_enemy_count = results
        .iter()
        .map(|metrics| metrics.max_enemy_count)
        .max()
        .unwrap_or(0);

    BatchSummary {
        bot,
        seed_start,
        seeds,
        map_id: map_id.to_string(),
        seconds,
        tick_rate,
        victories,
        average_duration,
        average_level,
        average_kills,
        max_enemy_count,
    }
}

fn run_bot_batch(
    content: &LoadedContent,
    bot: BotKind,
    seed_start: u64,
    seeds: u64,
    map_id: &str,
    seconds: f32,
    tick_rate: u32,
) -> BotBatchResult {
    let mut metrics = Vec::new();
    let mut replays = Vec::new();

    for offset in 0..seeds {
        let seed = seed_start + offset;
        let run = simulate_once(
            &content.pack,
            &content.hash,
            seed,
            map_id,
            seconds,
            tick_rate,
            bot,
        );
        metrics.push(run.metrics);
        replays.push(run.replay);
    }

    let summary = summarize_batch(bot, seed_start, seeds, map_id, seconds, tick_rate, &metrics);
    BotBatchResult {
        summary,
        metrics,
        replays,
    }
}

#[derive(Debug, Clone)]
struct BatchSummary {
    bot: BotKind,
    seed_start: u64,
    seeds: u64,
    map_id: String,
    seconds: f32,
    tick_rate: u32,
    victories: usize,
    average_duration: f32,
    average_level: f32,
    average_kills: f32,
    max_enemy_count: usize,
}

impl BatchSummary {
    fn win_rate(&self) -> f32 {
        self.victories as f32 / self.seeds as f32
    }
}

impl ReplayRunConfig {
    fn from_config(config: &RunConfig) -> Self {
        Self {
            seed: config.seed,
            map_id: config.map_id.clone(),
            character_id: config.character_id.clone(),
            starting_loadout: ReplayStartingLoadout {
                weapons: config.starting_loadout.weapons.clone(),
                passives: config.starting_loadout.passives.clone(),
            },
            difficulty: match config.difficulty {
                Difficulty::Normal => "normal",
            }
            .to_string(),
            duration_seconds: config.duration_seconds,
            content_pack_ids: config.content_pack_ids.clone(),
        }
    }
}

impl ReplayFinalMetrics {
    fn from_metrics(metrics: &RunMetrics) -> Self {
        let terminal = metrics
            .terminal
            .as_ref()
            .map(|terminal| terminal.kind.as_str())
            .unwrap_or("not_terminal")
            .to_string();
        let terminal_reason = metrics
            .terminal
            .as_ref()
            .map(|terminal| terminal.reason.clone())
            .unwrap_or_else(|| "step_limit_reached".to_string());

        Self {
            seed: metrics.seed,
            duration_seconds: metrics.duration_seconds,
            terminal,
            terminal_reason,
            kills: metrics.kills,
            level: metrics.level,
            xp_collected: metrics.xp_collected,
            xp_dropped: metrics.xp_dropped,
            damage_taken: metrics.damage_taken,
            damage_dealt_by_weapon: metrics.damage_dealt_by_weapon,
            max_enemy_count: metrics.max_enemy_count,
            max_projectile_count: metrics.max_projectile_count,
            upgrade_choices: metrics.upgrade_choices.clone(),
        }
    }
}

fn print_batch_json(summary: &BatchSummary, results: &[RunMetrics]) {
    println!("{{");
    println!("  \"bot\": \"{}\",", summary.bot.as_str());
    println!("  \"map_id\": \"{}\",", summary.map_id);
    println!("  \"seed_start\": {},", summary.seed_start);
    println!("  \"seeds\": {},", summary.seeds);
    println!("  \"seconds\": {:.3},", summary.seconds);
    println!("  \"tick_rate\": {},", summary.tick_rate);
    println!("  \"victories\": {},", summary.victories);
    println!("  \"win_rate\": {:.3},", summary.win_rate());
    println!(
        "  \"average_duration_seconds\": {:.3},",
        summary.average_duration
    );
    println!("  \"average_level\": {:.3},", summary.average_level);
    println!("  \"average_kills\": {:.3},", summary.average_kills);
    println!("  \"max_enemy_count\": {},", summary.max_enemy_count);
    println!("  \"runs\": [");
    for (index, metrics) in results.iter().enumerate() {
        let suffix = if index + 1 == results.len() { "" } else { "," };
        let terminal_kind = metrics
            .terminal
            .as_ref()
            .map(|terminal| terminal.kind.as_str())
            .unwrap_or("not_terminal");
        println!(
            "    {{ \"seed\": {}, \"terminal\": \"{}\", \"duration_seconds\": {:.3}, \"level\": {}, \"kills\": {} }}{}",
            metrics.seed, terminal_kind, metrics.duration_seconds, metrics.level, metrics.kills, suffix
        );
    }
    println!("  ]");
    println!("}}");
}

fn print_matrix_json(matrix_results: &[BotBatchResult]) {
    println!("{{");
    println!("  \"kind\": \"bot_matrix\",");
    println!("  \"bots\": [");
    for (bot_index, result) in matrix_results.iter().enumerate() {
        let bot_suffix = if bot_index + 1 == matrix_results.len() {
            ""
        } else {
            ","
        };
        let summary = &result.summary;
        let target = win_rate_target(summary.bot);
        println!("    {{");
        println!("      \"bot\": \"{}\",", summary.bot.as_str());
        println!("      \"map_id\": \"{}\",", summary.map_id);
        println!("      \"seed_start\": {},", summary.seed_start);
        println!("      \"seeds\": {},", summary.seeds);
        println!("      \"seconds\": {:.3},", summary.seconds);
        println!("      \"tick_rate\": {},", summary.tick_rate);
        println!("      \"victories\": {},", summary.victories);
        println!("      \"win_rate\": {:.3},", summary.win_rate());
        println!("      \"gate_status\": \"{}\",", gate_status(summary));
        println!("      \"gate_target\": {{");
        println!("        \"label\": \"{}\",", target.label);
        println!("        \"min_win_rate\": {:.3},", target.min);
        println!("        \"max_win_rate\": {:.3}", target.max);
        println!("      }},");
        println!(
            "      \"average_duration_seconds\": {:.3},",
            summary.average_duration
        );
        println!("      \"average_level\": {:.3},", summary.average_level);
        println!("      \"average_kills\": {:.3},", summary.average_kills);
        println!("      \"max_enemy_count\": {},", summary.max_enemy_count);
        println!("      \"runs\": [");
        for (run_index, metrics) in result.metrics.iter().enumerate() {
            let run_suffix = if run_index + 1 == result.metrics.len() {
                ""
            } else {
                ","
            };
            let terminal_kind = metrics
                .terminal
                .as_ref()
                .map(|terminal| terminal.kind.as_str())
                .unwrap_or("not_terminal");
            println!(
                "        {{ \"seed\": {}, \"terminal\": \"{}\", \"duration_seconds\": {:.3}, \"level\": {}, \"kills\": {}, \"damage_taken\": {:.3}, \"max_enemy_count\": {} }}{}",
                metrics.seed,
                terminal_kind,
                metrics.duration_seconds,
                metrics.level,
                metrics.kills,
                metrics.damage_taken,
                metrics.max_enemy_count,
                run_suffix
            );
        }
        println!("      ]");
        println!("    }}{}", bot_suffix);
    }
    println!("  ]");
    println!("}}");
}

fn write_report_or_exit(report_dir: &Path, result: &BotBatchResult) {
    if let Err(error) = write_report(report_dir, result) {
        eprintln!(
            "error: failed to write report `{}`: {error}",
            report_dir.display()
        );
        std::process::exit(1);
    }
}

fn write_report(report_dir: &Path, result: &BotBatchResult) -> io::Result<()> {
    let replay_dir = report_dir.join("representative_replays");
    fs::create_dir_all(&replay_dir)?;
    fs::write(
        report_dir.join("summary.md"),
        render_summary(&result.summary, &result.metrics),
    )?;
    fs::write(
        report_dir.join("metrics.json"),
        render_metrics_json(&result.summary, &result.metrics),
    )?;
    fs::write(report_dir.join("accepted.json"), "[]\n")?;
    fs::write(report_dir.join("rejected.json"), "[]\n")?;
    fs::write(
        report_dir.join("failure_cases.json"),
        render_failure_cases(&result.summary, &result.metrics),
    )?;
    write_replay_files(&replay_dir, result.summary.bot.as_str(), &result.replays)?;
    Ok(())
}

fn write_matrix_report_or_exit(report_dir: &Path, matrix_results: &[BotBatchResult]) {
    if let Err(error) = write_matrix_report(report_dir, matrix_results) {
        eprintln!(
            "error: failed to write matrix report `{}`: {error}",
            report_dir.display()
        );
        std::process::exit(1);
    }
}

fn write_matrix_report(report_dir: &Path, matrix_results: &[BotBatchResult]) -> io::Result<()> {
    let replay_dir = report_dir.join("representative_replays");
    fs::create_dir_all(&replay_dir)?;
    fs::write(
        report_dir.join("summary.md"),
        render_matrix_summary(matrix_results),
    )?;
    fs::write(
        report_dir.join("metrics.json"),
        render_matrix_metrics_json(matrix_results),
    )?;
    fs::write(report_dir.join("accepted.json"), "[]\n")?;
    fs::write(report_dir.join("rejected.json"), "[]\n")?;
    fs::write(
        report_dir.join("failure_cases.json"),
        render_matrix_failure_cases(matrix_results),
    )?;
    for result in matrix_results {
        write_replay_files(&replay_dir, result.summary.bot.as_str(), &result.replays)?;
    }
    Ok(())
}

fn render_summary(summary: &BatchSummary, results: &[RunMetrics]) -> String {
    let mut output = String::new();
    output.push_str("# Harness Batch Summary\n\n");
    output.push_str(&format!("- Bot: `{}`\n", summary.bot.as_str()));
    output.push_str(&format!("- Map: `{}`\n", summary.map_id));
    output.push_str(&format!(
        "- Seeds: `{}`..`{}`\n",
        summary.seed_start,
        summary.seed_start + summary.seeds.saturating_sub(1)
    ));
    output.push_str(&format!(
        "- Duration target: `{:.0}` seconds\n",
        summary.seconds
    ));
    output.push_str(&format!("- Tick rate: `{}`\n", summary.tick_rate));
    output.push_str(&format!(
        "- Win rate: `{:.1}%` ({}/{})\n",
        summary.win_rate() * 100.0,
        summary.victories,
        summary.seeds
    ));
    output.push_str(&format!(
        "- Average survival: `{:.1}` seconds\n",
        summary.average_duration
    ));
    output.push_str(&format!(
        "- Average level: `{:.1}`\n",
        summary.average_level
    ));
    output.push_str(&format!(
        "- Average kills: `{:.1}`\n",
        summary.average_kills
    ));
    output.push_str(&format!(
        "- Max enemy count: `{}`\n\n",
        summary.max_enemy_count
    ));

    output.push_str("## Runs\n\n");
    output.push_str("| Seed | Terminal | Duration | Level | Kills |\n");
    output.push_str("|---:|---|---:|---:|---:|\n");
    for metrics in results {
        let terminal_kind = metrics
            .terminal
            .as_ref()
            .map(|terminal| terminal.kind.as_str())
            .unwrap_or("not_terminal");
        output.push_str(&format!(
            "| {} | {} | {:.1} | {} | {} |\n",
            metrics.seed, terminal_kind, metrics.duration_seconds, metrics.level, metrics.kills
        ));
    }

    output.push_str("\n## Gate Notes\n\n");
    let target = win_rate_target(summary.bot);
    if is_inside_target(summary) {
        output.push_str(&format!(
            "- `{}` batch currently sits inside the initial {} win-rate target (`{:.0}%`-`{:.0}%`).\n",
            summary.bot.as_str(),
            target.label,
            target.min * 100.0,
            target.max * 100.0
        ));
    } else {
        output.push_str(&format!(
            "- `{}` batch is outside the initial {} win-rate target (`{:.0}%`-`{:.0}%`) and needs balance repair.\n",
            summary.bot.as_str(),
            target.label,
            target.min * 100.0,
            target.max * 100.0
        ));
    }
    output.push_str("- This report is a prototype Harness artifact; accepted/rejected content lists are placeholders until candidate promotion is implemented.\n");
    output
}

fn render_matrix_summary(matrix_results: &[BotBatchResult]) -> String {
    let mut output = String::new();
    output.push_str("# Harness Bot Matrix Summary\n\n");

    if let Some(first_result) = matrix_results.first() {
        let first_summary = &first_result.summary;
        output.push_str(&format!("- Map: `{}`\n", first_summary.map_id));
        output.push_str(&format!(
            "- Seeds: `{}`..`{}` per bot\n",
            first_summary.seed_start,
            first_summary
                .seed_start
                .saturating_add(first_summary.seeds.saturating_sub(1))
        ));
        output.push_str(&format!(
            "- Duration target: `{:.0}` seconds\n",
            first_summary.seconds
        ));
        output.push_str(&format!("- Tick rate: `{}`\n", first_summary.tick_rate));
        output.push_str(&format!("- Bot count: `{}`\n\n", matrix_results.len()));
    }

    output.push_str("## Bot Results\n\n");
    output.push_str("| Bot | Gate | Target | Win Rate | Victories | Avg Survival | Avg Level | Avg Kills | Max Enemies |\n");
    output.push_str("|---|---|---|---:|---:|---:|---:|---:|---:|\n");
    for result in matrix_results {
        let summary = &result.summary;
        let target = win_rate_target(summary.bot);
        output.push_str(&format!(
            "| {} | {} | {} {:.0}%-{:.0}% | {:.1}% | {}/{} | {:.1} | {:.1} | {:.1} | {} |\n",
            summary.bot.as_str(),
            gate_status(summary),
            target.label,
            target.min * 100.0,
            target.max * 100.0,
            summary.win_rate() * 100.0,
            summary.victories,
            summary.seeds,
            summary.average_duration,
            summary.average_level,
            summary.average_kills,
            summary.max_enemy_count
        ));
    }

    output.push_str("\n## Runs\n\n");
    for result in matrix_results {
        let summary = &result.summary;
        output.push_str(&format!("### {}\n\n", summary.bot.as_str()));
        output.push_str(
            "| Seed | Terminal | Duration | Level | Kills | Damage Taken | Max Enemies |\n",
        );
        output.push_str("|---:|---|---:|---:|---:|---:|---:|\n");
        for metrics in &result.metrics {
            let terminal_kind = metrics
                .terminal
                .as_ref()
                .map(|terminal| terminal.kind.as_str())
                .unwrap_or("not_terminal");
            output.push_str(&format!(
                "| {} | {} | {:.1} | {} | {} | {:.1} | {} |\n",
                metrics.seed,
                terminal_kind,
                metrics.duration_seconds,
                metrics.level,
                metrics.kills,
                metrics.damage_taken,
                metrics.max_enemy_count
            ));
        }
        output.push('\n');
    }

    output.push_str("## Gate Notes\n\n");
    let repair_bots = matrix_results
        .iter()
        .filter(|result| !is_inside_target(&result.summary))
        .map(|result| result.summary.bot.as_str())
        .collect::<Vec<_>>();
    if repair_bots.is_empty() {
        output.push_str(
            "- All matrix bots are inside their initial prototype win-rate target ranges.\n",
        );
    } else {
        output.push_str(&format!(
            "- Bots outside target and needing balance review: `{}`.\n",
            repair_bots.join("`, `")
        ));
    }
    output.push_str("- `accepted.json` and `rejected.json` are placeholders until candidate promotion is implemented.\n");
    output.push_str(
        "- `representative_replays/` contains prototype replay JSON for each matrix run.\n",
    );
    output
}

fn render_metrics_json(summary: &BatchSummary, results: &[RunMetrics]) -> String {
    let mut output = String::new();
    output.push_str("{\n");
    output.push_str(&format!("  \"bot\": \"{}\",\n", summary.bot.as_str()));
    output.push_str(&format!("  \"map_id\": \"{}\",\n", summary.map_id));
    output.push_str(&format!("  \"seed_start\": {},\n", summary.seed_start));
    output.push_str(&format!("  \"seeds\": {},\n", summary.seeds));
    output.push_str(&format!("  \"seconds\": {:.3},\n", summary.seconds));
    output.push_str(&format!("  \"tick_rate\": {},\n", summary.tick_rate));
    output.push_str(&format!("  \"victories\": {},\n", summary.victories));
    output.push_str(&format!("  \"win_rate\": {:.3},\n", summary.win_rate()));
    output.push_str(&format!(
        "  \"average_duration_seconds\": {:.3},\n",
        summary.average_duration
    ));
    output.push_str(&format!(
        "  \"average_level\": {:.3},\n",
        summary.average_level
    ));
    output.push_str(&format!(
        "  \"average_kills\": {:.3},\n",
        summary.average_kills
    ));
    output.push_str(&format!(
        "  \"max_enemy_count\": {},\n",
        summary.max_enemy_count
    ));
    output.push_str("  \"runs\": [\n");
    for (index, metrics) in results.iter().enumerate() {
        let suffix = if index + 1 == results.len() { "" } else { "," };
        let terminal_kind = metrics
            .terminal
            .as_ref()
            .map(|terminal| terminal.kind.as_str())
            .unwrap_or("not_terminal");
        output.push_str(&format!(
            "    {{ \"seed\": {}, \"terminal\": \"{}\", \"duration_seconds\": {:.3}, \"level\": {}, \"kills\": {}, \"damage_taken\": {:.3}, \"max_enemy_count\": {} }}{}\n",
            metrics.seed,
            terminal_kind,
            metrics.duration_seconds,
            metrics.level,
            metrics.kills,
            metrics.damage_taken,
            metrics.max_enemy_count,
            suffix
        ));
    }
    output.push_str("  ]\n");
    output.push_str("}\n");
    output
}

fn render_matrix_metrics_json(matrix_results: &[BotBatchResult]) -> String {
    let mut output = String::new();
    output.push_str("{\n");
    output.push_str("  \"kind\": \"bot_matrix\",\n");
    output.push_str("  \"bots\": [\n");
    for (bot_index, result) in matrix_results.iter().enumerate() {
        let bot_suffix = if bot_index + 1 == matrix_results.len() {
            ""
        } else {
            ","
        };
        let summary = &result.summary;
        let target = win_rate_target(summary.bot);
        output.push_str("    {\n");
        output.push_str(&format!("      \"bot\": \"{}\",\n", summary.bot.as_str()));
        output.push_str(&format!("      \"map_id\": \"{}\",\n", summary.map_id));
        output.push_str(&format!("      \"seed_start\": {},\n", summary.seed_start));
        output.push_str(&format!("      \"seeds\": {},\n", summary.seeds));
        output.push_str(&format!("      \"seconds\": {:.3},\n", summary.seconds));
        output.push_str(&format!("      \"tick_rate\": {},\n", summary.tick_rate));
        output.push_str(&format!("      \"victories\": {},\n", summary.victories));
        output.push_str(&format!("      \"win_rate\": {:.3},\n", summary.win_rate()));
        output.push_str(&format!(
            "      \"gate_status\": \"{}\",\n",
            gate_status(summary)
        ));
        output.push_str("      \"gate_target\": {\n");
        output.push_str(&format!("        \"label\": \"{}\",\n", target.label));
        output.push_str(&format!("        \"min_win_rate\": {:.3},\n", target.min));
        output.push_str(&format!("        \"max_win_rate\": {:.3}\n", target.max));
        output.push_str("      },\n");
        output.push_str(&format!(
            "      \"average_duration_seconds\": {:.3},\n",
            summary.average_duration
        ));
        output.push_str(&format!(
            "      \"average_level\": {:.3},\n",
            summary.average_level
        ));
        output.push_str(&format!(
            "      \"average_kills\": {:.3},\n",
            summary.average_kills
        ));
        output.push_str(&format!(
            "      \"max_enemy_count\": {},\n",
            summary.max_enemy_count
        ));
        output.push_str("      \"runs\": [\n");
        for (run_index, metrics) in result.metrics.iter().enumerate() {
            let run_suffix = if run_index + 1 == result.metrics.len() {
                ""
            } else {
                ","
            };
            let terminal_kind = metrics
                .terminal
                .as_ref()
                .map(|terminal| terminal.kind.as_str())
                .unwrap_or("not_terminal");
            output.push_str(&format!(
                "        {{ \"seed\": {}, \"terminal\": \"{}\", \"duration_seconds\": {:.3}, \"level\": {}, \"kills\": {}, \"damage_taken\": {:.3}, \"max_enemy_count\": {} }}{}\n",
                metrics.seed,
                terminal_kind,
                metrics.duration_seconds,
                metrics.level,
                metrics.kills,
                metrics.damage_taken,
                metrics.max_enemy_count,
                run_suffix
            ));
        }
        output.push_str("      ]\n");
        output.push_str(&format!("    }}{}\n", bot_suffix));
    }
    output.push_str("  ]\n");
    output.push_str("}\n");
    output
}

fn render_failure_cases(summary: &BatchSummary, results: &[RunMetrics]) -> String {
    let cases = failure_case_entries(summary, results);
    render_failure_case_json(&cases)
}

fn render_matrix_failure_cases(matrix_results: &[BotBatchResult]) -> String {
    let mut cases = Vec::new();
    for result in matrix_results {
        cases.extend(failure_case_entries(&result.summary, &result.metrics));
    }
    render_failure_case_json(&cases)
}

fn failure_case_entries<'a>(
    summary: &'a BatchSummary,
    results: &'a [RunMetrics],
) -> Vec<(&'a BatchSummary, &'a RunMetrics, &'static str)> {
    if is_inside_target(summary) {
        return Vec::new();
    }

    let rate = summary.win_rate();
    let target = win_rate_target(summary.bot);
    let symptom = if rate < target.min {
        "win_rate_below_target"
    } else {
        "win_rate_above_target"
    };
    let representative = if rate < target.min {
        results.iter().find(|metrics| {
            metrics
                .terminal
                .as_ref()
                .map_or(true, |terminal| terminal.kind != TerminalKind::Victory)
        })
    } else {
        results.iter().find(|metrics| {
            metrics
                .terminal
                .as_ref()
                .is_some_and(|terminal| terminal.kind == TerminalKind::Victory)
        })
    }
    .or_else(|| results.first());

    representative
        .map(|metrics| vec![(summary, metrics, symptom)])
        .unwrap_or_default()
}

fn render_failure_case_json(cases: &[(&BatchSummary, &RunMetrics, &'static str)]) -> String {
    let mut output = String::new();
    output.push_str("[\n");
    for (index, (summary, metrics, symptom)) in cases.iter().enumerate() {
        let suffix = if index + 1 == cases.len() { "" } else { "," };
        let terminal_kind = metrics
            .terminal
            .as_ref()
            .map(|terminal| terminal.kind.as_str())
            .unwrap_or("not_terminal");
        output.push_str(&format!(
            "  {{ \"case_id\": \"{}_seed_{}\", \"category\": \"balance\", \"content_id\": \"{}\", \"seed\": {}, \"bot\": \"{}\", \"time_seconds\": {:.3}, \"symptom\": \"{}: aggregate win rate {:.3}, representative run ended as {}\", \"root_cause\": \"prototype balance or bot policy requires review\", \"fix\": \"adjust content numbers or bot policy after reviewing matrix metrics\", \"validation\": \"rerun game_harness matrix with the same seed range\" }}{}\n",
            sanitize_id(summary.bot.as_str()),
            metrics.seed,
            summary.map_id,
            metrics.seed,
            summary.bot.as_str(),
            metrics.duration_seconds,
            symptom,
            summary.win_rate(),
            terminal_kind,
            suffix
        ));
    }
    output.push_str("]\n");
    output
}

#[derive(Debug, Clone, Copy)]
struct WinRateTarget {
    label: &'static str,
    min: f32,
    max: f32,
}

fn win_rate_target(bot: BotKind) -> WinRateTarget {
    match bot {
        BotKind::Idle => WinRateTarget {
            label: "idle pressure floor",
            min: 0.0,
            max: 0.0,
        },
        BotKind::Random => WinRateTarget {
            label: "random robustness",
            min: 0.0,
            max: 0.15,
        },
        BotKind::Coward | BotKind::Route => WinRateTarget {
            label: "low-skill rule bot",
            min: 0.10,
            max: 0.35,
        },
        BotKind::Greedy | BotKind::Tank | BotKind::ZoneControl => WinRateTarget {
            label: "mid-skill rule bot",
            min: 0.25,
            max: 0.55,
        },
        BotKind::Kite | BotKind::BossHunter => WinRateTarget {
            label: "high-skill rule bot",
            min: 0.45,
            max: 0.75,
        },
    }
}

fn is_inside_target(summary: &BatchSummary) -> bool {
    let target = win_rate_target(summary.bot);
    let win_rate = summary.win_rate();
    win_rate >= target.min && win_rate <= target.max
}

fn gate_status(summary: &BatchSummary) -> &'static str {
    if is_inside_target(summary) {
        "pass"
    } else {
        "repair"
    }
}

fn sanitize_id(value: &str) -> String {
    value.replace('-', "_")
}

fn movement_changed(previous: Option<[f32; 2]>, current: [f32; 2]) -> bool {
    match previous {
        Some(previous) => {
            previous[0].to_bits() != current[0].to_bits()
                || previous[1].to_bits() != current[1].to_bits()
        }
        None => true,
    }
}

fn write_replay_files(
    replay_dir: &Path,
    bot_name: &str,
    replays: &[ReplayRecord],
) -> io::Result<()> {
    for replay in replays {
        let file_name = format!(
            "{}_seed_{}.json",
            sanitize_id(bot_name),
            replay.run_config.seed
        );
        let json = serde_json::to_string_pretty(replay).map_err(io::Error::other)?;
        fs::write(replay_dir.join(file_name), format!("{json}\n"))?;
    }
    Ok(())
}

fn load_content_or_exit(content_dir: Option<&PathBuf>) -> LoadedContent {
    match content_dir {
        Some(path) => match load_content_from_path(path) {
            Ok(content) => content,
            Err(error) => {
                eprintln!(
                    "error: failed to load content `{}`: {error}",
                    path.display()
                );
                std::process::exit(1);
            }
        },
        None => LoadedContent {
            pack: ContentPack::base_demo(),
            hash: "builtin:base-demo".to_string(),
        },
    }
}

fn load_content_from_path(path: &Path) -> io::Result<LoadedContent> {
    let pack = ContentPack::load_from_dir(path).map_err(io::Error::other)?;
    let hash = content_hash_for_dir(path)?;
    Ok(LoadedContent { pack, hash })
}

fn content_hash_for_dir(path: &Path) -> io::Result<String> {
    const FNV_OFFSET: u64 = 0xcbf2_9ce4_8422_2325;

    let mut files = Vec::new();
    collect_content_files(path, &mut files)?;
    files.sort();

    let mut hash = FNV_OFFSET;
    for file in files {
        let relative = file.strip_prefix(path).unwrap_or(&file);
        hash = fnv1a_update(hash, relative.to_string_lossy().as_bytes());
        hash = fnv1a_update(hash, &[0]);
        let bytes = fs::read(&file)?;
        hash = fnv1a_update(hash, &bytes);
        hash = fnv1a_update(hash, &[0xff]);
    }

    Ok(format!("fnv1a64:{hash:016x}"))
}

fn collect_content_files(path: &Path, files: &mut Vec<PathBuf>) -> io::Result<()> {
    for entry in fs::read_dir(path)? {
        let entry = entry?;
        let path = entry.path();
        if path.is_dir() {
            collect_content_files(&path, files)?;
        } else if path
            .extension()
            .is_some_and(|extension| extension == "json")
            && !is_harness_gate_metadata_file(&path)
        {
            files.push(path);
        }
    }
    Ok(())
}

fn is_harness_gate_metadata_file(path: &Path) -> bool {
    path.file_name()
        .and_then(|name| name.to_str())
        .is_some_and(|name| {
            matches!(
                name,
                "acceptance_gate.json"
                    | "acceptance_repair.json"
                    | "manual_review.json"
                    | "playtest_gate.json"
                    | "rejection.json"
                    | "repair.json"
            )
        })
}

fn fnv1a_update(mut hash: u64, bytes: &[u8]) -> u64 {
    const FNV_PRIME: u64 = 0x0000_0100_0000_01b3;

    for byte in bytes {
        hash ^= u64::from(*byte);
        hash = hash.wrapping_mul(FNV_PRIME);
    }
    hash
}

fn evaluate_static_budget(pack: &ContentPack, content_dir: String) -> StaticBudgetReport {
    let mut warnings = Vec::new();
    let mut errors = Vec::new();

    let weapon_budgets = pack
        .weapons
        .values()
        .map(|weapon| {
            let cooldown_seconds = weapon.base_stats.cooldown_ms / 1000.0;
            let theoretical_single_target_dps =
                weapon.base_stats.damage * weapon.base_stats.projectile_count as f32
                    / cooldown_seconds.max(0.001);
            let mut notes = Vec::new();
            let mut failed = false;
            let lower_bound = weapon.balance_budget.single_target_dps * 0.65;
            let upper_bound = weapon.balance_budget.single_target_dps * 1.35;

            if theoretical_single_target_dps > upper_bound {
                failed = true;
                notes.push(format!(
                    "理论单体 DPS {:.2} 高于声明预算 {:.2} 的 1.35 倍上限 {:.2}",
                    theoretical_single_target_dps,
                    weapon.balance_budget.single_target_dps,
                    upper_bound
                ));
            }
            if theoretical_single_target_dps < lower_bound {
                failed = true;
                notes.push(format!(
                    "理论单体 DPS {:.2} 低于声明预算 {:.2} 的 0.65 倍下限 {:.2}",
                    theoretical_single_target_dps,
                    weapon.balance_budget.single_target_dps,
                    lower_bound
                ));
            }
            if weapon.balance_budget.group_dps > weapon.balance_budget.single_target_dps * 2.5 {
                warnings.push(format!(
                    "weapon `{}` group DPS budget {:.2} is much higher than single-target budget {:.2}",
                    weapon.id,
                    weapon.balance_budget.group_dps,
                    weapon.balance_budget.single_target_dps
                ));
                notes.push("群体 DPS 预算显著高于单体预算，需要后续 Bot 仿真确认".to_string());
            }
            if !matches!(
                weapon.balance_budget.performance_cost.as_str(),
                "low" | "medium" | "high"
            ) {
                failed = true;
                notes.push(format!(
                    "performance_cost `{}` 非法，应为 low/medium/high",
                    weapon.balance_budget.performance_cost
                ));
            }
            if weapon.base_stats.projectile_count > 12 {
                failed = true;
                notes.push(format!(
                    "projectile_count {} 超过首版静态性能上限 12",
                    weapon.base_stats.projectile_count
                ));
            }
            if weapon.base_stats.area_radius > 180.0 {
                warnings.push(format!(
                    "weapon `{}` area radius {:.1} is high",
                    weapon.id, weapon.base_stats.area_radius
                ));
                notes.push("范围半径较大，后续需要可读性和性能复查".to_string());
            }

            if failed {
                errors.push(format!(
                    "weapon `{}` failed static budget: {}",
                    weapon.id,
                    notes.join("; ")
                ));
            }

            WeaponBudgetReview {
                id: weapon.id.clone(),
                role: weapon.balance_budget.role.clone(),
                theoretical_single_target_dps,
                declared_single_target_dps: weapon.balance_budget.single_target_dps,
                declared_group_dps: weapon.balance_budget.group_dps,
                performance_cost: weapon.balance_budget.performance_cost.clone(),
                status: if failed { "failed" } else { "ok" },
                notes,
            }
        })
        .collect::<Vec<_>>();

    let enemy_budgets = pack
        .enemies
        .values()
        .map(|enemy| {
            evaluate_enemy_budget(
                EnemyBudgetInput {
                    id: enemy.id(),
                    health: enemy.common.stats.health,
                    move_speed: enemy.common.stats.move_speed,
                    contact_damage_per_second: enemy.common.stats.contact_damage_per_second,
                    declared_threat: enemy.spawn_budget.threat,
                    performance_cost: enemy.spawn_budget.performance_cost,
                },
                &mut warnings,
                &mut errors,
            )
        })
        .collect::<Vec<_>>();

    let boss_budgets = pack
        .bosses
        .values()
        .map(|boss| {
            let computed_threat = computed_enemy_threat(
                boss.common.stats.health,
                boss.common.stats.move_speed,
                boss.common.stats.contact_damage_per_second,
            );
            let mut notes = Vec::new();
            let mut failed = false;
            if !(450.0..=2400.0).contains(&boss.common.stats.health) {
                failed = true;
                notes.push(format!(
                    "Boss HP {:.1} 超出首版静态范围 450-2400",
                    boss.common.stats.health
                ));
            }
            if boss.common.stats.xp_value < 60.0 || boss.common.stats.xp_value > 160.0 {
                failed = true;
                notes.push(format!(
                    "Boss XP {:.1} 超出文档建议范围 60-160",
                    boss.common.stats.xp_value
                ));
            }
            if failed {
                errors.push(format!(
                    "boss `{}` failed static budget: {}",
                    boss.id(),
                    notes.join("; ")
                ));
            }
            EnemyBudgetReview {
                id: boss.id().to_string(),
                threat: computed_threat,
                computed_threat,
                speed_damage_pressure: boss.common.stats.move_speed
                    * boss.common.stats.contact_damage_per_second
                    / 100.0,
                performance_cost: 4.0,
                status: if failed { "failed" } else { "ok" },
                notes,
            }
        })
        .collect::<Vec<_>>();

    let mut all_enemy_budgets = enemy_budgets;
    all_enemy_budgets.extend(boss_budgets);

    let wave_budgets = pack
        .waves
        .values()
        .map(|wave| evaluate_wave_budget(pack, wave, &mut warnings, &mut errors))
        .collect::<Vec<_>>();

    StaticBudgetReport {
        status: if errors.is_empty() { "ok" } else { "failed" },
        content_dir,
        weapon_budgets,
        enemy_budgets: all_enemy_budgets,
        wave_budgets,
        warnings,
        errors,
    }
}

fn evaluate_enemy_budget(
    input: EnemyBudgetInput<'_>,
    warnings: &mut Vec<String>,
    errors: &mut Vec<String>,
) -> EnemyBudgetReview {
    let computed_threat = computed_enemy_threat(
        input.health,
        input.move_speed,
        input.contact_damage_per_second,
    );
    let speed_damage_pressure = input.move_speed * input.contact_damage_per_second / 100.0;
    let mut notes = Vec::new();
    let mut failed = false;

    if input.declared_threat <= 0.0 || !input.declared_threat.is_finite() {
        failed = true;
        notes.push(format!(
            "declared threat {:.2} 非正或非有限",
            input.declared_threat
        ));
    }
    if input.declared_threat > computed_threat * 1.8
        || input.declared_threat < computed_threat * 0.45
    {
        warnings.push(format!(
            "enemy `{}` declared threat {:.2} differs from computed threat {:.2}",
            input.id, input.declared_threat, computed_threat
        ));
        notes.push(format!(
            "声明威胁 {:.2} 与计算威胁 {:.2} 差异较大",
            input.declared_threat, computed_threat
        ));
    }
    if input.move_speed >= 85.0 && input.contact_damage_per_second >= 6.0 {
        failed = true;
        notes.push(format!(
            "高速 {:.1} + 高接触伤害 {:.1} 组合超过首版安全线",
            input.move_speed, input.contact_damage_per_second
        ));
    }
    if speed_damage_pressure > 8.0 {
        failed = true;
        notes.push(format!(
            "speed_damage_pressure {:.2} 超过首版上限 8.0",
            speed_damage_pressure
        ));
    }
    if !(0.5..=5.0).contains(&input.performance_cost) {
        failed = true;
        notes.push(format!(
            "performance_cost {:.2} 超出首版静态范围 0.5-5.0",
            input.performance_cost
        ));
    }

    if failed {
        errors.push(format!(
            "enemy `{}` failed static budget: {}",
            input.id,
            notes.join("; ")
        ));
    }

    EnemyBudgetReview {
        id: input.id.to_string(),
        threat: input.declared_threat,
        computed_threat,
        speed_damage_pressure,
        performance_cost: input.performance_cost,
        status: if failed { "failed" } else { "ok" },
        notes,
    }
}

fn computed_enemy_threat(health: f32, move_speed: f32, contact_damage_per_second: f32) -> f32 {
    let health_factor = (health / 18.0).sqrt().max(0.4);
    let speed_factor = (move_speed / 60.0).max(0.35);
    let damage_factor = (contact_damage_per_second / 4.5).max(0.25);
    health_factor * speed_factor * damage_factor
}

fn evaluate_wave_budget(
    pack: &ContentPack,
    wave: &game_core::content::WaveDefinition,
    warnings: &mut Vec<String>,
    errors: &mut Vec<String>,
) -> WaveBudgetReview {
    let mut max_spawn_pressure: f32 = 0.0;
    let mut max_alive_pressure: f32 = 0.0;
    let mut max_alive = 0usize;
    let mut notes = Vec::new();
    let mut failed = false;

    for segment in &wave.segments {
        let average_threat = weighted_average_threat(pack, &segment.enemy_pool);
        let spawn_count_per_second =
            segment.spawn_count as f32 / (segment.spawn_interval_ms / 1000.0);
        let spawn_pressure = spawn_count_per_second * average_threat;
        let alive_pressure = segment.max_alive as f32 * average_threat;
        max_spawn_pressure = max_spawn_pressure.max(spawn_pressure);
        max_alive_pressure = max_alive_pressure.max(alive_pressure);
        max_alive = max_alive.max(segment.max_alive);

        let expected_level = pressure_level_for_time(segment.start_second);
        if !pressure_budget_allows(expected_level, spawn_pressure, alive_pressure) {
            failed = true;
            notes.push(format!(
                "{:.0}-{:.0}s {} pressure 超出首版静态预算: spawn {:.2}, alive {:.2}",
                segment.start_second,
                segment.end_second,
                expected_level,
                spawn_pressure,
                alive_pressure
            ));
        }
    }

    if max_alive > 140 {
        failed = true;
        notes.push(format!("max_alive {max_alive} 超过首版静态性能上限 140"));
    } else if max_alive > 105 {
        warnings.push(format!(
            "wave `{}` max_alive {} is near the prototype performance ceiling",
            wave.id, max_alive
        ));
        notes.push("同屏敌人数接近性能风险线，需要 Bot 仿真确认".to_string());
    }

    if failed {
        errors.push(format!(
            "wave `{}` failed static budget: {}",
            wave.id,
            notes.join("; ")
        ));
    }

    WaveBudgetReview {
        id: wave.id.clone(),
        max_spawn_pressure,
        max_alive_pressure,
        max_alive,
        status: if failed { "failed" } else { "ok" },
        notes,
    }
}

fn weighted_average_threat(
    pack: &ContentPack,
    enemy_pool: &[game_core::content::EnemyPoolEntryDefinition],
) -> f32 {
    let mut weighted = 0.0;
    let mut total_weight = 0.0;
    for entry in enemy_pool {
        if let Some(enemy) = pack.enemies.get(&entry.enemy_id) {
            weighted += enemy.spawn_budget.threat * entry.weight;
            total_weight += entry.weight;
        }
    }
    if total_weight > 0.0 {
        weighted / total_weight
    } else {
        0.0
    }
}

fn pressure_level_for_time(start_second: f32) -> &'static str {
    if start_second < 90.0 {
        "early"
    } else if start_second < 210.0 {
        "mid_low"
    } else if start_second < 300.0 {
        "boss"
    } else if start_second < 480.0 {
        "mid_high"
    } else {
        "late"
    }
}

fn pressure_budget_allows(level: &str, spawn_pressure: f32, alive_pressure: f32) -> bool {
    let (spawn_limit, alive_limit) = match level {
        "early" => (1.2, 45.0),
        "mid_low" => (3.2, 85.0),
        "boss" => (3.8, 130.0),
        "mid_high" => (6.5, 180.0),
        _ => (8.0, 260.0),
    };
    spawn_pressure <= spawn_limit && alive_pressure <= alive_limit
}

fn validate_candidate_dirs(args: &CandidateArgs) -> io::Result<CandidatePipelineReport> {
    fs::create_dir_all(&args.source_dir)?;
    fs::create_dir_all(&args.validated_dir)?;
    fs::create_dir_all(&args.rejected_dir)?;

    let mut entries = fs::read_dir(&args.source_dir)?
        .collect::<Result<Vec<_>, _>>()?
        .into_iter()
        .filter(|entry| entry.path().is_dir())
        .collect::<Vec<_>>();
    entries.sort_by_key(|entry| entry.file_name());

    let mut candidates = Vec::new();
    for entry in entries {
        let source_path = entry.path();
        let candidate_id = entry.file_name().to_string_lossy().to_string();
        let validation = ContentPack::load_from_dir(&source_path)
            .and_then(|pack| pack.validate().map(|report| (pack, report)));

        match validation {
            Ok((pack, validation_report)) => {
                let budget_report =
                    evaluate_static_budget(&pack, source_path.display().to_string());
                let mut warnings = validation_report.warnings;
                warnings.extend(budget_report.warnings.clone());

                if budget_report.errors.is_empty() {
                    let destination = args.validated_dir.join(&candidate_id);
                    copy_dir_all(&source_path, &destination)?;
                    candidates.push(CandidateReview {
                        id: candidate_id,
                        source: source_path.display().to_string(),
                        decision: "validated",
                        destination: destination.display().to_string(),
                        object_count: Some(pack.object_count()),
                        warnings,
                        errors: Vec::new(),
                        budget_report: Some(budget_report),
                    });
                } else {
                    let destination = args.rejected_dir.join(&candidate_id);
                    copy_dir_all(&source_path, &destination)?;
                    let errors = budget_report.errors.clone();
                    write_rejection_reason(&destination, &candidate_id, "static_budget", &errors)?;
                    candidates.push(CandidateReview {
                        id: candidate_id,
                        source: source_path.display().to_string(),
                        decision: "rejected",
                        destination: destination.display().to_string(),
                        object_count: Some(pack.object_count()),
                        warnings,
                        errors,
                        budget_report: Some(budget_report),
                    });
                }
            }
            Err(error) => {
                let destination = args.rejected_dir.join(&candidate_id);
                copy_dir_all(&source_path, &destination)?;
                let errors = vec![error.to_string()];
                write_rejection_reason(&destination, &candidate_id, "schema_error", &errors)?;
                candidates.push(CandidateReview {
                    id: candidate_id,
                    source: source_path.display().to_string(),
                    decision: "rejected",
                    destination: destination.display().to_string(),
                    object_count: None,
                    warnings: Vec::new(),
                    errors,
                    budget_report: None,
                });
            }
        }
    }

    let validated_count = candidates
        .iter()
        .filter(|candidate| candidate.decision == "validated")
        .count();
    let rejected_count = candidates
        .iter()
        .filter(|candidate| candidate.decision == "rejected")
        .count();

    Ok(CandidatePipelineReport {
        source_dir: args.source_dir.display().to_string(),
        validated_dir: args.validated_dir.display().to_string(),
        rejected_dir: args.rejected_dir.display().to_string(),
        candidate_count: candidates.len(),
        validated_count,
        rejected_count,
        candidates,
    })
}

fn simulate_candidate_dirs(args: &SimulateCandidatesArgs) -> io::Result<CandidateSimulationReport> {
    fs::create_dir_all(&args.source_dir)?;
    fs::create_dir_all(&args.simulated_dir)?;
    fs::create_dir_all(&args.repair_dir)?;

    let mut entries = fs::read_dir(&args.source_dir)?
        .collect::<Result<Vec<_>, _>>()?
        .into_iter()
        .filter(|entry| entry.path().is_dir())
        .collect::<Vec<_>>();
    entries.sort_by_key(|entry| entry.file_name());

    let base_report_dir = args
        .report_dir
        .clone()
        .unwrap_or_else(|| PathBuf::from("harness/reports/candidate_simulation"));
    fs::create_dir_all(&base_report_dir)?;

    let mut candidates = Vec::new();
    for entry in entries {
        let source_path = entry.path();
        let candidate_id = entry.file_name().to_string_lossy().to_string();
        let content = load_content_from_path(&source_path)?;
        let matrix_results = args
            .bots
            .iter()
            .map(|bot| {
                run_bot_batch(
                    &content,
                    *bot,
                    args.seed_start,
                    args.seeds,
                    DEFAULT_MAP_ID,
                    args.seconds,
                    args.tick_rate,
                )
            })
            .collect::<Vec<_>>();
        let failed_bots = matrix_results
            .iter()
            .filter(|result| !is_inside_target(&result.summary))
            .map(|result| result.summary.bot.as_str().to_string())
            .collect::<Vec<_>>();
        let passed = failed_bots.is_empty();
        let destination = if passed {
            args.simulated_dir.join(&candidate_id)
        } else {
            args.repair_dir.join(&candidate_id)
        };
        copy_dir_all(&source_path, &destination)?;

        let candidate_report_dir = base_report_dir.join(&candidate_id);
        write_matrix_report(&candidate_report_dir, &matrix_results)?;
        if !passed {
            write_repair_reason(
                &destination,
                &candidate_id,
                &failed_bots,
                &candidate_report_dir,
            )?;
        }

        candidates.push(CandidateSimulationReview {
            id: candidate_id,
            source: source_path.display().to_string(),
            decision: if passed { "simulated" } else { "repair" },
            destination: destination.display().to_string(),
            report_dir: candidate_report_dir.display().to_string(),
            gate_status: if passed { "pass" } else { "repair" },
            failed_bots,
            matrix_summary: matrix_results
                .iter()
                .map(|result| CandidateBotSummary {
                    bot: result.summary.bot.as_str().to_string(),
                    gate_status: gate_status(&result.summary),
                    win_rate: result.summary.win_rate(),
                    victories: result.summary.victories,
                    seeds: result.summary.seeds,
                    average_duration_seconds: result.summary.average_duration,
                    average_level: result.summary.average_level,
                    average_kills: result.summary.average_kills,
                    max_enemy_count: result.summary.max_enemy_count,
                })
                .collect(),
        });
    }

    let simulated_count = candidates
        .iter()
        .filter(|candidate| candidate.decision == "simulated")
        .count();
    let repair_count = candidates
        .iter()
        .filter(|candidate| candidate.decision == "repair")
        .count();

    Ok(CandidateSimulationReport {
        source_dir: args.source_dir.display().to_string(),
        simulated_dir: args.simulated_dir.display().to_string(),
        repair_dir: args.repair_dir.display().to_string(),
        candidate_count: candidates.len(),
        simulated_count,
        repair_count,
        candidates,
    })
}

fn promote_playtest_candidate_dirs(
    args: &PromotePlaytestCandidatesArgs,
) -> io::Result<CandidatePlaytestPromotionReport> {
    fs::create_dir_all(&args.source_dir)?;
    fs::create_dir_all(&args.playtest_dir)?;
    fs::create_dir_all(&args.repair_dir)?;

    let mut entries = fs::read_dir(&args.source_dir)?
        .collect::<Result<Vec<_>, _>>()?
        .into_iter()
        .filter(|entry| entry.path().is_dir())
        .collect::<Vec<_>>();
    entries.sort_by_key(|entry| entry.file_name());

    let mut candidates = Vec::new();
    for entry in entries {
        let source_path = entry.path();
        let candidate_id = entry.file_name().to_string_lossy().to_string();
        let loaded =
            ContentPack::load_from_dir(&source_path).and_then(|pack| pack.validate().map(|_| pack));

        match loaded {
            Ok(pack) => {
                let budget_report =
                    evaluate_static_budget(&pack, source_path.display().to_string());
                let content_hash = content_hash_for_dir(&source_path)?;
                if budget_report.errors.is_empty() {
                    let destination = args.playtest_dir.join(&candidate_id);
                    copy_dir_all(&source_path, &destination)?;
                    write_playtest_gate(&destination, &candidate_id, &content_hash)?;
                    candidates.push(CandidatePlaytestPromotionReview {
                        id: candidate_id,
                        source: source_path.display().to_string(),
                        decision: "playtest",
                        destination: destination.display().to_string(),
                        object_count: Some(pack.object_count()),
                        content_hash: Some(content_hash),
                        errors: Vec::new(),
                        review_pack: Some(
                            "harness/playtest/runtime_manual_review_pack.md".to_string(),
                        ),
                        next_step: "run human playtest review and fill candidate playtest notes before acceptance"
                            .to_string(),
                    });
                } else {
                    let destination = args.repair_dir.join(&candidate_id);
                    copy_dir_all(&source_path, &destination)?;
                    let errors = budget_report.errors.clone();
                    write_playtest_repair_reason(
                        &destination,
                        &candidate_id,
                        "static_budget_regression",
                        &errors,
                    )?;
                    candidates.push(CandidatePlaytestPromotionReview {
                        id: candidate_id,
                        source: source_path.display().to_string(),
                        decision: "repair",
                        destination: destination.display().to_string(),
                        object_count: Some(pack.object_count()),
                        content_hash: Some(content_hash),
                        errors,
                        review_pack: None,
                        next_step: "repair candidate before promoting to playtest_candidates"
                            .to_string(),
                    });
                }
            }
            Err(error) => {
                let destination = args.repair_dir.join(&candidate_id);
                copy_dir_all(&source_path, &destination)?;
                let errors = vec![error.to_string()];
                write_rejection_reason(&destination, &candidate_id, "schema_error", &errors)?;
                candidates.push(CandidatePlaytestPromotionReview {
                    id: candidate_id,
                    source: source_path.display().to_string(),
                    decision: "repair",
                    destination: destination.display().to_string(),
                    object_count: None,
                    content_hash: None,
                    errors,
                    review_pack: None,
                    next_step: "repair candidate schema before promoting to playtest_candidates"
                        .to_string(),
                });
            }
        }
    }

    let playtest_count = candidates
        .iter()
        .filter(|candidate| candidate.decision == "playtest")
        .count();
    let repair_count = candidates
        .iter()
        .filter(|candidate| candidate.decision == "repair")
        .count();

    Ok(CandidatePlaytestPromotionReport {
        source_dir: args.source_dir.display().to_string(),
        playtest_dir: args.playtest_dir.display().to_string(),
        repair_dir: args.repair_dir.display().to_string(),
        candidate_count: candidates.len(),
        playtest_count,
        repair_count,
        candidates,
    })
}

fn promote_accepted_candidate_dirs(
    args: &PromoteAcceptedCandidatesArgs,
) -> io::Result<CandidateAcceptanceReport> {
    fs::create_dir_all(&args.source_dir)?;
    fs::create_dir_all(&args.accepted_dir)?;
    fs::create_dir_all(&args.repair_dir)?;
    fs::create_dir_all(&args.review_dir)?;

    let mut entries = fs::read_dir(&args.source_dir)?
        .collect::<Result<Vec<_>, _>>()?
        .into_iter()
        .filter(|entry| entry.path().is_dir())
        .collect::<Vec<_>>();
    entries.sort_by_key(|entry| entry.file_name());

    let mut candidates = Vec::new();
    for entry in entries {
        let source_path = entry.path();
        let candidate_id = entry.file_name().to_string_lossy().to_string();
        let loaded =
            ContentPack::load_from_dir(&source_path).and_then(|pack| pack.validate().map(|_| pack));

        let pack = match loaded {
            Ok(pack) => pack,
            Err(error) => {
                let destination = args.repair_dir.join(&candidate_id);
                copy_dir_all(&source_path, &destination)?;
                let errors = vec![error.to_string()];
                write_acceptance_repair_reason(
                    &destination,
                    &candidate_id,
                    "schema_error",
                    &errors,
                    "repair candidate schema before accepted_content promotion",
                )?;
                candidates.push(CandidateAcceptanceReview {
                    id: candidate_id,
                    source: source_path.display().to_string(),
                    decision: "repair",
                    destination: Some(destination.display().to_string()),
                    object_count: None,
                    content_hash: None,
                    review_file: None,
                    completed_run_count: 0,
                    average_rating: None,
                    errors,
                    next_step: "repair candidate schema before accepted_content promotion"
                        .to_string(),
                });
                continue;
            }
        };

        let budget_report = evaluate_static_budget(&pack, source_path.display().to_string());
        let content_hash = content_hash_for_dir(&source_path)?;
        let mut gate_errors = validate_playtest_gate(&source_path, &candidate_id, &content_hash);
        gate_errors.extend(budget_report.errors);
        if !gate_errors.is_empty() {
            let destination = args.repair_dir.join(&candidate_id);
            copy_dir_all(&source_path, &destination)?;
            write_acceptance_repair_reason(
                &destination,
                &candidate_id,
                "pre_acceptance_gate_regression",
                &gate_errors,
                "repair candidate before rerunning promote-accepted-candidates",
            )?;
            candidates.push(CandidateAcceptanceReview {
                id: candidate_id,
                source: source_path.display().to_string(),
                decision: "repair",
                destination: Some(destination.display().to_string()),
                object_count: Some(pack.object_count()),
                content_hash: Some(content_hash),
                review_file: None,
                completed_run_count: 0,
                average_rating: None,
                errors: gate_errors,
                next_step: "repair candidate before accepted_content promotion".to_string(),
            });
            continue;
        }

        let Some(review_file) =
            find_manual_acceptance_review_file(&source_path, &args.review_dir, &candidate_id)
        else {
            candidates.push(CandidateAcceptanceReview {
                id: candidate_id.clone(),
                source: source_path.display().to_string(),
                decision: "waiting",
                destination: None,
                object_count: Some(pack.object_count()),
                content_hash: Some(content_hash),
                review_file: None,
                completed_run_count: 0,
                average_rating: None,
                errors: vec![format!(
                    "missing manual acceptance review for `{candidate_id}` in `{}`",
                    args.review_dir.display()
                )],
                next_step: "complete human playtest review before accepted_content promotion"
                    .to_string(),
            });
            continue;
        };

        let manual_gate =
            evaluate_manual_acceptance_review(&review_file, &candidate_id, &content_hash);
        match manual_gate.decision {
            ManualAcceptanceDecision::Accept => {
                let destination = args.accepted_dir.join(&candidate_id);
                copy_dir_all(&source_path, &destination)?;
                write_acceptance_gate(
                    &destination,
                    &candidate_id,
                    &content_hash,
                    &review_file,
                    manual_gate.completed_run_count,
                    manual_gate.average_rating,
                )?;
                candidates.push(CandidateAcceptanceReview {
                    id: candidate_id,
                    source: source_path.display().to_string(),
                    decision: manual_gate.decision.as_str(),
                    destination: Some(destination.display().to_string()),
                    object_count: Some(pack.object_count()),
                    content_hash: Some(content_hash),
                    review_file: Some(review_file.display().to_string()),
                    completed_run_count: manual_gate.completed_run_count,
                    average_rating: manual_gate.average_rating,
                    errors: manual_gate.errors,
                    next_step: "version-lock accepted candidate before runtime integration"
                        .to_string(),
                });
            }
            ManualAcceptanceDecision::Repair => {
                let destination = args.repair_dir.join(&candidate_id);
                copy_dir_all(&source_path, &destination)?;
                write_acceptance_repair_reason(
                    &destination,
                    &candidate_id,
                    "manual_playtest_repair",
                    &manual_gate.errors,
                    "repair candidate based on human playtest findings",
                )?;
                candidates.push(CandidateAcceptanceReview {
                    id: candidate_id,
                    source: source_path.display().to_string(),
                    decision: manual_gate.decision.as_str(),
                    destination: Some(destination.display().to_string()),
                    object_count: Some(pack.object_count()),
                    content_hash: Some(content_hash),
                    review_file: Some(review_file.display().to_string()),
                    completed_run_count: manual_gate.completed_run_count,
                    average_rating: manual_gate.average_rating,
                    errors: manual_gate.errors,
                    next_step: "repair candidate and rerun playtest gate".to_string(),
                });
            }
            ManualAcceptanceDecision::Waiting => {
                candidates.push(CandidateAcceptanceReview {
                    id: candidate_id,
                    source: source_path.display().to_string(),
                    decision: manual_gate.decision.as_str(),
                    destination: None,
                    object_count: Some(pack.object_count()),
                    content_hash: Some(content_hash),
                    review_file: Some(review_file.display().to_string()),
                    completed_run_count: manual_gate.completed_run_count,
                    average_rating: manual_gate.average_rating,
                    errors: manual_gate.errors,
                    next_step: "complete missing human review evidence before acceptance"
                        .to_string(),
                });
            }
        }
    }

    let accepted_count = candidates
        .iter()
        .filter(|candidate| candidate.decision == "accepted")
        .count();
    let repair_count = candidates
        .iter()
        .filter(|candidate| candidate.decision == "repair")
        .count();
    let waiting_count = candidates
        .iter()
        .filter(|candidate| candidate.decision == "waiting")
        .count();

    Ok(CandidateAcceptanceReport {
        source_dir: args.source_dir.display().to_string(),
        accepted_dir: args.accepted_dir.display().to_string(),
        repair_dir: args.repair_dir.display().to_string(),
        review_dir: args.review_dir.display().to_string(),
        candidate_count: candidates.len(),
        accepted_count,
        repair_count,
        waiting_count,
        candidates,
    })
}

fn lock_accepted_content_dirs(
    args: &LockAcceptedContentArgs,
) -> io::Result<AcceptedContentLockReport> {
    fs::create_dir_all(&args.accepted_dir)?;

    let mut entries = fs::read_dir(&args.accepted_dir)?
        .collect::<Result<Vec<_>, _>>()?
        .into_iter()
        .filter(|entry| entry.path().is_dir())
        .collect::<Vec<_>>();
    entries.sort_by_key(|entry| entry.file_name());

    let mut locked_entries = Vec::new();
    let mut errors = Vec::new();
    for entry in entries {
        let source_path = entry.path();
        let candidate_id = entry.file_name().to_string_lossy().to_string();
        let mut entry_errors = Vec::new();

        let pack = match ContentPack::load_from_dir(&source_path) {
            Ok(pack) => Some(pack),
            Err(error) => {
                entry_errors.push(format!("content validation failed: {error}"));
                None
            }
        };
        if let Some(pack) = &pack {
            let budget_report = evaluate_static_budget(pack, source_path.display().to_string());
            entry_errors.extend(budget_report.errors);
        }

        let content_hash = match content_hash_for_dir(&source_path) {
            Ok(hash) => Some(hash),
            Err(error) => {
                entry_errors.push(format!("content hash failed: {error}"));
                None
            }
        };

        let gate_path = source_path.join("acceptance_gate.json");
        let gate_metadata = match &content_hash {
            Some(hash) => validate_acceptance_gate(&gate_path, &candidate_id, hash),
            None => Err(vec![
                "content hash missing before acceptance gate validation".to_string(),
            ]),
        };
        let gate_metadata = match gate_metadata {
            Ok(metadata) => Some(metadata),
            Err(gate_errors) => {
                entry_errors.extend(gate_errors);
                None
            }
        };

        let runtime_content_dir = args.runtime_content_root.join(&candidate_id);
        let status = if entry_errors.is_empty() {
            "locked"
        } else {
            "blocked"
        };
        if status == "blocked" {
            errors.push(format!(
                "accepted candidate `{candidate_id}` cannot be version-locked"
            ));
        }

        locked_entries.push(AcceptedContentLockEntry {
            id: candidate_id,
            source: source_path.display().to_string(),
            runtime_content_dir: runtime_content_dir.display().to_string(),
            content_hash,
            object_count: pack.as_ref().map(ContentPack::object_count),
            acceptance_gate: gate_path.is_file().then(|| gate_path.display().to_string()),
            manual_review_file: gate_metadata
                .as_ref()
                .map(|metadata| metadata.manual_review_file.clone()),
            completed_run_count: gate_metadata
                .as_ref()
                .map(|metadata| metadata.completed_run_count),
            average_rating: gate_metadata
                .as_ref()
                .and_then(|metadata| metadata.average_rating),
            status,
            errors: entry_errors,
        });
    }

    let locked_count = locked_entries
        .iter()
        .filter(|entry| entry.status == "locked")
        .count();
    let blocked_count = locked_entries
        .iter()
        .filter(|entry| entry.status == "blocked")
        .count();

    let report = AcceptedContentLockReport {
        lock_version: 1,
        status: if blocked_count == 0 {
            "locked"
        } else {
            "blocked"
        },
        accepted_dir: args.accepted_dir.display().to_string(),
        lock_file: args.lock_file.display().to_string(),
        runtime_content_root: args.runtime_content_root.display().to_string(),
        candidate_count: locked_entries.len(),
        locked_count,
        blocked_count,
        entries: locked_entries,
        errors,
    };

    if report.blocked_count == 0 {
        write_accepted_content_lock_file(&args.lock_file, &report)?;
    }

    Ok(report)
}

fn find_manual_acceptance_review_file(
    candidate_dir: &Path,
    review_dir: &Path,
    candidate_id: &str,
) -> Option<PathBuf> {
    [
        review_dir.join(format!("{candidate_id}.json")),
        review_dir.join(candidate_id).join("manual_review.json"),
        candidate_dir.join("manual_review.json"),
    ]
    .into_iter()
    .find(|path| path.is_file())
}

fn validate_playtest_gate(
    candidate_dir: &Path,
    candidate_id: &str,
    content_hash: &str,
) -> Vec<String> {
    let gate_path = candidate_dir.join("playtest_gate.json");
    let Ok(text) = fs::read_to_string(&gate_path) else {
        return vec![format!(
            "missing or unreadable playtest gate `{}`",
            gate_path.display()
        )];
    };
    let Ok(gate) = serde_json::from_str::<Value>(&text) else {
        return vec![format!(
            "invalid playtest gate JSON `{}`",
            gate_path.display()
        )];
    };

    let mut errors = Vec::new();
    if json_string_field(&gate, "candidate_id") != Some(candidate_id) {
        errors.push("playtest gate candidate_id does not match directory".to_string());
    }
    if json_string_field(&gate, "decision") != Some("playtest") {
        errors.push("playtest gate decision must be `playtest`".to_string());
    }
    if json_string_field(&gate, "content_hash") != Some(content_hash) {
        errors.push("playtest gate content_hash does not match current content".to_string());
    }
    let requires_manual_review = gate
        .get("required_review")
        .and_then(|review| review.get("manual_review"))
        .and_then(Value::as_bool)
        .unwrap_or(false);
    if !requires_manual_review {
        errors.push("playtest gate must require manual_review".to_string());
    }
    errors
}

fn validate_acceptance_gate(
    gate_path: &Path,
    candidate_id: &str,
    content_hash: &str,
) -> Result<AcceptanceGateMetadata, Vec<String>> {
    let text = fs::read_to_string(gate_path).map_err(|error| {
        vec![format!(
            "missing or unreadable acceptance gate `{}`: {error}",
            gate_path.display()
        )]
    })?;
    let gate = serde_json::from_str::<Value>(&text).map_err(|error| {
        vec![format!(
            "invalid acceptance gate JSON `{}`: {error}",
            gate_path.display()
        )]
    })?;

    let mut errors = Vec::new();
    if json_string_field(&gate, "candidate_id") != Some(candidate_id) {
        errors.push("acceptance gate candidate_id does not match directory".to_string());
    }
    if json_string_field(&gate, "decision") != Some("accept_candidate") {
        errors.push("acceptance gate decision must be `accept_candidate`".to_string());
    }
    if json_string_field(&gate, "content_hash") != Some(content_hash) {
        errors.push("acceptance gate content_hash does not match current content".to_string());
    }
    if json_string_field(&gate, "category") != Some("human_playtest_passed") {
        errors.push("acceptance gate category must be `human_playtest_passed`".to_string());
    }
    let manual_review_file = json_string_field(&gate, "manual_review_file")
        .map(str::to_string)
        .unwrap_or_else(|| {
            errors.push("acceptance gate must include manual_review_file".to_string());
            String::new()
        });
    if !manual_review_file.is_empty() && !Path::new(&manual_review_file).is_file() {
        errors.push(format!(
            "acceptance gate manual_review_file does not exist: `{manual_review_file}`"
        ));
    }
    let completed_run_count = gate
        .get("completed_run_count")
        .and_then(Value::as_u64)
        .map(|value| value as usize)
        .unwrap_or_else(|| {
            errors.push("acceptance gate must include completed_run_count".to_string());
            0
        });
    if completed_run_count < REQUIRED_PLAYTEST_RUN_IDS.len() {
        errors.push(format!(
            "acceptance gate completed_run_count must be at least {}",
            REQUIRED_PLAYTEST_RUN_IDS.len()
        ));
    }
    let average_rating = gate
        .get("average_rating")
        .and_then(Value::as_f64)
        .map(|value| value as f32);
    if average_rating.is_none() {
        errors.push("acceptance gate must include average_rating".to_string());
    }

    if errors.is_empty() {
        Ok(AcceptanceGateMetadata {
            manual_review_file,
            completed_run_count,
            average_rating,
        })
    } else {
        Err(errors)
    }
}

fn evaluate_manual_acceptance_review(
    review_file: &Path,
    candidate_id: &str,
    content_hash: &str,
) -> ManualAcceptanceGate {
    let text = match fs::read_to_string(review_file) {
        Ok(text) => text,
        Err(error) => {
            return ManualAcceptanceGate {
                decision: ManualAcceptanceDecision::Waiting,
                completed_run_count: 0,
                average_rating: None,
                errors: vec![format!(
                    "failed to read manual acceptance review `{}`: {error}",
                    review_file.display()
                )],
            };
        }
    };
    match serde_json::from_str::<Value>(&text) {
        Ok(review) => evaluate_manual_acceptance_review_value(&review, candidate_id, content_hash),
        Err(error) => ManualAcceptanceGate {
            decision: ManualAcceptanceDecision::Waiting,
            completed_run_count: 0,
            average_rating: None,
            errors: vec![format!(
                "failed to parse manual acceptance review `{}`: {error}",
                review_file.display()
            )],
        },
    }
}

fn evaluate_manual_acceptance_review_value(
    review: &Value,
    candidate_id: &str,
    content_hash: &str,
) -> ManualAcceptanceGate {
    let mut repair_errors = Vec::new();
    let mut waiting_errors = Vec::new();
    let mut seen_run_ids = BTreeSet::new();
    let mut completed_run_count = 0usize;
    let mut rating_sum = 0.0f32;
    let mut rating_count = 0usize;

    match acceptance_string_field(review, "candidate_id") {
        Some(value) if value == candidate_id => {}
        Some(_) => {
            repair_errors.push("manual review candidate_id does not match candidate".to_string())
        }
        None => waiting_errors.push("manual review must include candidate_id".to_string()),
    }
    match acceptance_string_field(review, "content_hash") {
        Some(value) if value == content_hash => {}
        Some(_) => {
            repair_errors.push("manual review content_hash does not match candidate".to_string())
        }
        None => waiting_errors.push("manual review must include content_hash".to_string()),
    }
    if acceptance_string_field(review, "reviewer").is_none() {
        waiting_errors.push("manual review must include reviewer".to_string());
    }
    if acceptance_string_field(review, "reviewed_at").is_none() {
        waiting_errors.push("manual review must include reviewed_at".to_string());
    }
    if acceptance_string_field(review, "summary").is_none() {
        waiting_errors.push("manual review must include summary".to_string());
    }

    match acceptance_string_field(review, "acceptance_decision")
        .or_else(|| acceptance_string_field(review, "decision"))
    {
        Some("accept_candidate") => {}
        Some("repair") => {
            repair_errors.push("manual review top-level decision is `repair`".to_string());
        }
        Some("needs_more_runs") | Some("playtest_pass") => {
            waiting_errors.push(
                "manual review requires top-level `acceptance_decision: accept_candidate`"
                    .to_string(),
            );
        }
        Some(value) => waiting_errors.push(format!(
            "manual review has unsupported acceptance decision `{value}`"
        )),
        None => waiting_errors
            .push("manual review must include `acceptance_decision: accept_candidate`".to_string()),
    }

    let Some(runs) = review.get("runs").and_then(Value::as_array) else {
        return ManualAcceptanceGate {
            decision: ManualAcceptanceDecision::Waiting,
            completed_run_count,
            average_rating: None,
            errors: merge_gate_errors(repair_errors, {
                waiting_errors.push("manual review must include runs array".to_string());
                waiting_errors
            }),
        };
    };

    for run in runs {
        let Some(run_id) = review_string_field(run, "run_id") else {
            waiting_errors.push("manual review run is missing run_id".to_string());
            continue;
        };
        seen_run_ids.insert(run_id.to_string());

        let mut run_complete = true;
        match review_string_field(run, "gate_decision")
            .or_else(|| review_string_field(run, "decision"))
        {
            Some("playtest_pass") => {}
            Some("repair") => {
                repair_errors.push(format!("run `{run_id}` gate_decision is `repair`"));
                run_complete = false;
            }
            Some("needs_more_runs") => {
                waiting_errors.push(format!("run `{run_id}` needs more runs"));
                run_complete = false;
            }
            Some(value) => {
                waiting_errors.push(format!(
                    "run `{run_id}` has unsupported gate_decision `{value}`"
                ));
                run_complete = false;
            }
            None => {
                waiting_errors.push(format!("run `{run_id}` is missing gate_decision"));
                run_complete = false;
            }
        }

        for field in ACCEPTANCE_RATING_FIELDS {
            match review_rating_field(run, field) {
                Some(value) if (1..=5).contains(&value) => {
                    rating_sum += value as f32;
                    rating_count += 1;
                    if value < 3 {
                        repair_errors.push(format!("run `{run_id}` rating `{field}` is below 3"));
                        run_complete = false;
                    }
                }
                Some(value) => {
                    repair_errors.push(format!(
                        "run `{run_id}` rating `{field}` is outside 1-5: {value}"
                    ));
                    run_complete = false;
                }
                None => {
                    waiting_errors.push(format!("run `{run_id}` is missing rating `{field}`"));
                    run_complete = false;
                }
            }
        }

        if review_string_field(run, "notes").is_none() {
            waiting_errors.push(format!("run `{run_id}` must include non-empty notes"));
            run_complete = false;
        }
        if review_array_len(run, "next_actions").unwrap_or(0) == 0 {
            waiting_errors.push(format!("run `{run_id}` must include next_actions"));
            run_complete = false;
        }
        if run_complete {
            completed_run_count += 1;
        }
    }

    for required in REQUIRED_PLAYTEST_RUN_IDS {
        if !seen_run_ids.contains(required) {
            waiting_errors.push(format!(
                "manual review is missing required run `{required}`"
            ));
        }
    }

    let average_rating = (rating_count > 0).then_some(rating_sum / rating_count as f32);
    let decision = if !repair_errors.is_empty() {
        ManualAcceptanceDecision::Repair
    } else if !waiting_errors.is_empty() {
        ManualAcceptanceDecision::Waiting
    } else {
        ManualAcceptanceDecision::Accept
    };

    ManualAcceptanceGate {
        decision,
        completed_run_count,
        average_rating,
        errors: merge_gate_errors(repair_errors, waiting_errors),
    }
}

fn merge_gate_errors(mut repair_errors: Vec<String>, waiting_errors: Vec<String>) -> Vec<String> {
    repair_errors.extend(waiting_errors);
    repair_errors
}

fn json_string_field<'a>(value: &'a Value, key: &str) -> Option<&'a str> {
    value
        .get(key)
        .and_then(Value::as_str)
        .map(str::trim)
        .filter(|value| !value.is_empty())
}

fn acceptance_string_field<'a>(value: &'a Value, key: &str) -> Option<&'a str> {
    json_string_field(value, key).or_else(|| {
        value
            .get("human_review")
            .and_then(|review| json_string_field(review, key))
    })
}

fn review_field<'a>(value: &'a Value, key: &str) -> Option<&'a Value> {
    value
        .get(key)
        .or_else(|| {
            value
                .get("manual_review")
                .and_then(|review| review.get(key))
        })
        .or_else(|| {
            value
                .get("manual_review_fields")
                .and_then(|review| review.get(key))
        })
}

fn review_string_field<'a>(value: &'a Value, key: &str) -> Option<&'a str> {
    review_field(value, key)
        .and_then(Value::as_str)
        .map(str::trim)
        .filter(|value| !value.is_empty())
}

fn review_rating_field(value: &Value, key: &str) -> Option<i64> {
    review_field(value, key).and_then(Value::as_i64)
}

fn review_array_len(value: &Value, key: &str) -> Option<usize> {
    review_field(value, key)
        .and_then(Value::as_array)
        .map(Vec::len)
}

fn copy_dir_all(source: &Path, destination: &Path) -> io::Result<()> {
    fs::create_dir_all(destination)?;
    for entry in fs::read_dir(source)? {
        let entry = entry?;
        let source_path = entry.path();
        let destination_path = destination.join(entry.file_name());
        if source_path.is_dir() {
            copy_dir_all(&source_path, &destination_path)?;
        } else {
            fs::copy(&source_path, &destination_path)?;
        }
    }
    Ok(())
}

fn write_rejection_reason(
    destination: &Path,
    candidate_id: &str,
    category: &str,
    errors: &[String],
) -> io::Result<()> {
    let reason = serde_json::json!({
        "candidate_id": candidate_id,
        "decision": "rejected",
        "category": category,
        "errors": errors,
        "next_step": "repair candidate content in generated_candidates before revalidation"
    });
    let json = serde_json::to_string_pretty(&reason).map_err(io::Error::other)?;
    fs::write(destination.join("rejection.json"), format!("{json}\n"))
}

fn write_repair_reason(
    destination: &Path,
    candidate_id: &str,
    failed_bots: &[String],
    report_dir: &Path,
) -> io::Result<()> {
    let reason = serde_json::json!({
        "candidate_id": candidate_id,
        "decision": "repair",
        "category": "bot_matrix",
        "failed_bots": failed_bots,
        "report_dir": report_dir.display().to_string(),
        "next_step": "repair candidate balance in validated_candidates or generated_candidates, then rerun simulate-candidates"
    });
    let json = serde_json::to_string_pretty(&reason).map_err(io::Error::other)?;
    fs::write(destination.join("repair.json"), format!("{json}\n"))
}

fn write_playtest_repair_reason(
    destination: &Path,
    candidate_id: &str,
    category: &str,
    errors: &[String],
) -> io::Result<()> {
    let reason = serde_json::json!({
        "candidate_id": candidate_id,
        "decision": "repair",
        "category": category,
        "errors": errors,
        "next_step": "repair candidate content before rerunning promote-playtest-candidates"
    });
    let json = serde_json::to_string_pretty(&reason).map_err(io::Error::other)?;
    fs::write(destination.join("repair.json"), format!("{json}\n"))
}

fn write_playtest_gate(
    destination: &Path,
    candidate_id: &str,
    content_hash: &str,
) -> io::Result<()> {
    let gate = serde_json::json!({
        "candidate_id": candidate_id,
        "decision": "playtest",
        "content_hash": content_hash,
        "category": "bot_simulation_passed",
        "required_review": {
            "manual_review": true,
            "review_pack": "harness/playtest/runtime_manual_review_pack.md",
            "forbidden_next_step": "accepted_content_without_human_review"
        },
        "next_step": "run a human playtest capture and record manual review before any accepted_content promotion"
    });
    let json = serde_json::to_string_pretty(&gate).map_err(io::Error::other)?;
    fs::write(destination.join("playtest_gate.json"), format!("{json}\n"))
}

fn write_acceptance_gate(
    destination: &Path,
    candidate_id: &str,
    content_hash: &str,
    review_file: &Path,
    completed_run_count: usize,
    average_rating: Option<f32>,
) -> io::Result<()> {
    let gate = serde_json::json!({
        "candidate_id": candidate_id,
        "decision": "accept_candidate",
        "content_hash": content_hash,
        "category": "human_playtest_passed",
        "manual_review_file": review_file.display().to_string(),
        "completed_run_count": completed_run_count,
        "average_rating": average_rating,
        "required_next_step": "version-lock accepted candidate before runtime integration"
    });
    let json = serde_json::to_string_pretty(&gate).map_err(io::Error::other)?;
    fs::write(
        destination.join("acceptance_gate.json"),
        format!("{json}\n"),
    )
}

fn write_acceptance_repair_reason(
    destination: &Path,
    candidate_id: &str,
    category: &str,
    errors: &[String],
    next_step: &str,
) -> io::Result<()> {
    let reason = serde_json::json!({
        "candidate_id": candidate_id,
        "decision": "repair",
        "category": category,
        "errors": errors,
        "next_step": next_step
    });
    let json = serde_json::to_string_pretty(&reason).map_err(io::Error::other)?;
    fs::write(
        destination.join("acceptance_repair.json"),
        format!("{json}\n"),
    )
}

fn write_candidate_report(report_dir: &Path, report: &CandidatePipelineReport) -> io::Result<()> {
    fs::create_dir_all(report_dir)?;
    let json = serde_json::to_string_pretty(report).map_err(io::Error::other)?;
    fs::write(
        report_dir.join("candidate_validation.json"),
        format!("{json}\n"),
    )?;
    fs::write(
        report_dir.join("summary.md"),
        render_candidate_summary(report),
    )?;
    Ok(())
}

fn write_candidate_simulation_report(
    report_dir: &Path,
    report: &CandidateSimulationReport,
) -> io::Result<()> {
    fs::create_dir_all(report_dir)?;
    let json = serde_json::to_string_pretty(report).map_err(io::Error::other)?;
    fs::write(
        report_dir.join("candidate_simulation.json"),
        format!("{json}\n"),
    )?;
    fs::write(
        report_dir.join("summary.md"),
        render_candidate_simulation_summary(report),
    )?;
    Ok(())
}

fn write_candidate_playtest_promotion_report(
    report_dir: &Path,
    report: &CandidatePlaytestPromotionReport,
) -> io::Result<()> {
    fs::create_dir_all(report_dir)?;
    let json = serde_json::to_string_pretty(report).map_err(io::Error::other)?;
    fs::write(
        report_dir.join("candidate_playtest_promotion.json"),
        format!("{json}\n"),
    )?;
    fs::write(
        report_dir.join("summary.md"),
        render_candidate_playtest_promotion_summary(report),
    )?;
    Ok(())
}

fn write_candidate_acceptance_report(
    report_dir: &Path,
    report: &CandidateAcceptanceReport,
) -> io::Result<()> {
    fs::create_dir_all(report_dir)?;
    let json = serde_json::to_string_pretty(report).map_err(io::Error::other)?;
    fs::write(
        report_dir.join("candidate_acceptance.json"),
        format!("{json}\n"),
    )?;
    fs::write(
        report_dir.join("summary.md"),
        render_candidate_acceptance_summary(report),
    )?;
    Ok(())
}

fn write_accepted_content_lock_file(
    lock_file: &Path,
    report: &AcceptedContentLockReport,
) -> io::Result<()> {
    if let Some(parent) = lock_file.parent() {
        fs::create_dir_all(parent)?;
    }
    let json = serde_json::to_string_pretty(report).map_err(io::Error::other)?;
    fs::write(lock_file, format!("{json}\n"))
}

fn write_accepted_content_lock_report(
    report_dir: &Path,
    report: &AcceptedContentLockReport,
) -> io::Result<()> {
    fs::create_dir_all(report_dir)?;
    let json = serde_json::to_string_pretty(report).map_err(io::Error::other)?;
    fs::write(
        report_dir.join("accepted_content_lock.json"),
        format!("{json}\n"),
    )?;
    fs::write(
        report_dir.join("summary.md"),
        render_accepted_content_lock_summary(report),
    )?;
    Ok(())
}

fn write_meta_settlement_report(
    report_dir: &Path,
    report: &MetaSettlementSmokeReport,
) -> io::Result<()> {
    fs::create_dir_all(report_dir)?;
    let json = serde_json::to_string_pretty(report).map_err(io::Error::other)?;
    fs::write(report_dir.join("meta_settlement.json"), format!("{json}\n"))?;
    fs::write(
        report_dir.join("summary.md"),
        render_meta_settlement_summary(report),
    )?;
    Ok(())
}

fn render_candidate_summary(report: &CandidatePipelineReport) -> String {
    let mut output = String::new();
    output.push_str("# Candidate Validation Summary\n\n");
    output.push_str(&format!("- Source: `{}`\n", report.source_dir));
    output.push_str(&format!("- Validated: `{}`\n", report.validated_dir));
    output.push_str(&format!("- Rejected: `{}`\n", report.rejected_dir));
    output.push_str(&format!(
        "- Result: `{}` validated, `{}` rejected, `{}` total\n\n",
        report.validated_count, report.rejected_count, report.candidate_count
    ));
    output.push_str("| Candidate | Decision | Objects | Warnings | Errors |\n");
    output.push_str("|---|---|---:|---:|---:|\n");
    for candidate in &report.candidates {
        output.push_str(&format!(
            "| {} | {} | {} | {} | {} |\n",
            candidate.id,
            candidate.decision,
            candidate.object_count.unwrap_or(0),
            candidate.warnings.len(),
            candidate.errors.len()
        ));
    }
    output
}

fn render_candidate_simulation_summary(report: &CandidateSimulationReport) -> String {
    let mut output = String::new();
    output.push_str("# Candidate Simulation Summary\n\n");
    output.push_str(&format!("- Source: `{}`\n", report.source_dir));
    output.push_str(&format!("- Simulated: `{}`\n", report.simulated_dir));
    output.push_str(&format!("- Repair: `{}`\n", report.repair_dir));
    output.push_str(&format!(
        "- Result: `{}` simulated, `{}` repair, `{}` total\n\n",
        report.simulated_count, report.repair_count, report.candidate_count
    ));
    output.push_str("| Candidate | Decision | Failed Bots | Report |\n");
    output.push_str("|---|---|---:|---|\n");
    for candidate in &report.candidates {
        output.push_str(&format!(
            "| {} | {} | {} | {} |\n",
            candidate.id,
            candidate.decision,
            candidate.failed_bots.len(),
            candidate.report_dir
        ));
    }
    output
}

fn render_candidate_playtest_promotion_summary(
    report: &CandidatePlaytestPromotionReport,
) -> String {
    let mut output = String::new();
    output.push_str("# Candidate Playtest Promotion Summary\n\n");
    output.push_str(&format!("- Source: `{}`\n", report.source_dir));
    output.push_str(&format!("- Playtest: `{}`\n", report.playtest_dir));
    output.push_str(&format!("- Repair: `{}`\n", report.repair_dir));
    output.push_str(&format!(
        "- Result: `{}` playtest, `{}` repair, `{}` total\n\n",
        report.playtest_count, report.repair_count, report.candidate_count
    ));
    output.push_str("| Candidate | Decision | Objects | Errors | Next Step |\n");
    output.push_str("|---|---|---:|---:|---|\n");
    for candidate in &report.candidates {
        output.push_str(&format!(
            "| {} | {} | {} | {} | {} |\n",
            candidate.id,
            candidate.decision,
            candidate.object_count.unwrap_or(0),
            candidate.errors.len(),
            candidate.next_step
        ));
    }
    output.push_str("\n## Gate Notes\n\n");
    output.push_str("- `playtest` means the candidate is recommended for human playtest only.\n");
    output.push_str("- This command never writes to `accepted_content`.\n");
    output.push_str("- A human review is still required before any later acceptance step.\n");
    output
}

fn render_candidate_acceptance_summary(report: &CandidateAcceptanceReport) -> String {
    let mut output = String::new();
    output.push_str("# Candidate Acceptance Summary\n\n");
    output.push_str(&format!("- Source: `{}`\n", report.source_dir));
    output.push_str(&format!("- Accepted: `{}`\n", report.accepted_dir));
    output.push_str(&format!("- Repair: `{}`\n", report.repair_dir));
    output.push_str(&format!("- Reviews: `{}`\n", report.review_dir));
    output.push_str(&format!(
        "- Result: `{}` accepted, `{}` repair, `{}` waiting, `{}` total\n\n",
        report.accepted_count, report.repair_count, report.waiting_count, report.candidate_count
    ));
    output.push_str(
        "| Candidate | Decision | Runs | Average Rating | Errors | Destination | Next Step |\n",
    );
    output.push_str("|---|---|---:|---:|---:|---|---|\n");
    for candidate in &report.candidates {
        let average_rating = candidate
            .average_rating
            .map(|value| format!("{value:.2}"))
            .unwrap_or_else(|| "-".to_string());
        output.push_str(&format!(
            "| {} | {} | {} | {} | {} | {} | {} |\n",
            candidate.id,
            candidate.decision,
            candidate.completed_run_count,
            average_rating,
            candidate.errors.len(),
            candidate.destination.as_deref().unwrap_or("-"),
            candidate.next_step
        ));
    }
    output.push_str("\n## Gate Notes\n\n");
    output.push_str("- `accepted` means the candidate has complete human review evidence and is copied to `accepted_content`.\n");
    output.push_str("- `waiting` means the candidate remains in `playtest_candidates` until human review evidence is complete.\n");
    output.push_str("- This command still does not turn a candidate into a release candidate; version locking and release gates remain separate.\n");
    output
}

fn render_accepted_content_lock_summary(report: &AcceptedContentLockReport) -> String {
    let mut output = String::new();
    output.push_str("# Accepted Content Lock Summary\n\n");
    output.push_str(&format!("- Status: `{}`\n", report.status));
    output.push_str(&format!("- Accepted dir: `{}`\n", report.accepted_dir));
    output.push_str(&format!("- Lock file: `{}`\n", report.lock_file));
    output.push_str(&format!(
        "- Runtime content root: `{}`\n",
        report.runtime_content_root
    ));
    output.push_str(&format!(
        "- Result: `{}` locked, `{}` blocked, `{}` total\n\n",
        report.locked_count, report.blocked_count, report.candidate_count
    ));
    output.push_str(
        "| Candidate | Status | Objects | Content Hash | Review Runs | Average Rating | Runtime Path | Errors |\n",
    );
    output.push_str("|---|---|---:|---|---:|---:|---|---:|\n");
    for entry in &report.entries {
        let average_rating = entry
            .average_rating
            .map(|value| format!("{value:.2}"))
            .unwrap_or_else(|| "-".to_string());
        output.push_str(&format!(
            "| {} | {} | {} | {} | {} | {} | {} | {} |\n",
            entry.id,
            entry.status,
            entry.object_count.unwrap_or(0),
            entry.content_hash.as_deref().unwrap_or("-"),
            entry.completed_run_count.unwrap_or(0),
            average_rating,
            entry.runtime_content_dir,
            entry.errors.len()
        ));
    }
    output.push_str("\n## Gate Notes\n\n");
    output
        .push_str("- The lockfile is written only when every accepted candidate remains valid.\n");
    output.push_str("- Each locked entry preserves content hash, acceptance gate, manual review reference, object count, and Runtime content path.\n");
    output.push_str("- This command does not invent human review evidence and does not promote playtest candidates.\n");
    output
}

fn render_meta_settlement_summary(report: &MetaSettlementSmokeReport) -> String {
    let mut output = String::new();
    output.push_str("# Meta Settlement Summary\n\n");
    output.push_str(&format!("- Content: `{}`\n", report.content_dir));
    output.push_str(&format!("- Bot: `{}`\n", report.bot));
    output.push_str(&format!(
        "- Run: `{}` on `{}` for `{:.1}` seconds\n",
        report.run_summary.run_id, report.run_summary.map_id, report.run_summary.duration_seconds
    ));
    output.push_str(&format!(
        "- Candy crystal shards gained: `{}`\n",
        report.settlement.resources_gained.candy_crystal_shards
    ));
    output.push_str(&format!(
        "- Star shards gained: `{}`\n",
        report.settlement.resources_gained.star_shards
    ));
    output.push_str(&format!(
        "- Storm grains gained: `{}`\n",
        report.settlement.resources_gained.storm_grains
    ));
    output.push_str(&format!(
        "- Completed goals: `{}`\n",
        report.settlement.completed_goals.len()
    ));
    output.push_str(&format!(
        "- Unlocks: `{}`\n",
        report.settlement.unlocked.len()
    ));
    output.push_str(&format!(
        "- Codex updates: `{}`\n\n",
        report.settlement.codex_updates.len()
    ));
    output.push_str("## Gate Notes\n\n");
    output.push_str("- This smoke applies one headless run to `MetaProgress::demo_start()`.\n");
    output.push_str(
        "- Failed or short runs can still grant candy crystal shards and codex progress.\n",
    );
    output.push_str(
        "- Chapter star shards and unlocks are only granted when explicit chapter goals are met.\n",
    );
    output
}

fn run_validate(args: ValidateArgs) {
    match ContentPack::load_from_dir(&args.content_dir).and_then(|content| content.validate()) {
        Ok(report) => {
            println!("{{");
            println!("  \"content_dir\": \"{}\",", args.content_dir.display());
            println!("  \"status\": \"ok\",");
            println!("  \"object_count\": {},", report.object_count);
            println!("  \"warnings\": [");
            for (index, warning) in report.warnings.iter().enumerate() {
                let suffix = if index + 1 == report.warnings.len() {
                    ""
                } else {
                    ","
                };
                println!("    \"{}\"{}", escape_json(warning), suffix);
            }
            println!("  ]");
            println!("}}");
        }
        Err(error) => {
            eprintln!("error: {error}");
            std::process::exit(1);
        }
    }
}

fn print_help() {
    eprintln!("usage:");
    eprintln!("  cargo run -p game_harness -- validate-content [--content-dir content/base_demo]");
    eprintln!(
        "  cargo run -p game_harness -- simulate [--seed N] [--map-id {}] [--seconds N] [--tick-rate N] [--bot {}] [--content-dir content/base_demo]",
        DEFAULT_MAP_ID,
        BotKind::all_names()
    );
    eprintln!(
        "  cargo run -p game_harness -- meta-settlement [--seed N] [--map-id {}] [--seconds N] [--tick-rate N] [--bot {}] [--content-dir content/base_demo] [--report-dir harness/reports/local_meta_settlement]",
        DEFAULT_MAP_ID,
        BotKind::all_names()
    );
    eprintln!(
        "  cargo run -p game_harness -- batch [--seed-start N] [--seeds N] [--map-id {}] [--seconds N] [--tick-rate N] [--bot {}] [--content-dir content/base_demo] [--report-dir harness/reports/local_batch]",
        DEFAULT_MAP_ID,
        BotKind::all_names()
    );
    eprintln!(
        "  cargo run -p game_harness -- matrix [--seed-start N] [--seeds N] [--map-id {}] [--seconds N] [--tick-rate N] [--bots all|{}] [--content-dir content/base_demo] [--report-dir harness/reports/local_matrix]",
        DEFAULT_MAP_ID,
        BotKind::all_names()
    );
    eprintln!(
        "  cargo run -p game_harness -- replay --replay-file harness/reports/local_matrix/representative_replays/kite_seed_12345.json [--content-dir content/base_demo]"
    );
    eprintln!(
        "  cargo run -p game_harness -- validate-candidates [--source-dir harness/generated_candidates] [--validated-dir harness/validated_candidates] [--rejected-dir harness/rejected_content] [--report-dir harness/reports/local_candidates]"
    );
    eprintln!(
        "  cargo run -p game_harness -- simulate-candidates [--source-dir harness/validated_candidates] [--simulated-dir harness/simulated_candidates] [--repair-dir harness/repair_queue] [--seed-start N] [--seeds N] [--seconds N] [--tick-rate N] [--bots all|{}] [--report-dir harness/reports/local_candidate_simulation]",
        BotKind::all_names()
    );
    eprintln!(
        "  cargo run -p game_harness -- promote-playtest-candidates [--source-dir harness/simulated_candidates] [--playtest-dir harness/playtest_candidates] [--repair-dir harness/repair_queue] [--report-dir harness/reports/local_playtest_promotion]"
    );
    eprintln!(
        "  cargo run -p game_harness -- promote-accepted-candidates [--source-dir harness/playtest_candidates] [--accepted-dir harness/accepted_content] [--repair-dir harness/repair_queue] [--review-dir harness/playtest_reviews] [--report-dir harness/reports/local_candidate_acceptance]"
    );
    eprintln!(
        "  cargo run -p game_harness -- lock-accepted-content [--accepted-dir harness/accepted_content] [--lock-file harness/accepted_content/accepted_content.lock.json] [--runtime-content-root harness/accepted_content] [--report-dir harness/reports/local_accepted_content_lock]"
    );
    eprintln!(
        "  cargo run -p game_harness -- gym-bridge [--seed N] [--map-id {}] [--seconds N] [--tick-rate N] [--content-dir content/base_demo]",
        DEFAULT_MAP_ID
    );
}

fn escape_json(value: &str) -> String {
    value.replace('\\', "\\\\").replace('"', "\\\"")
}

#[cfg(test)]
mod tests {
    use super::{
        content_hash_for_dir, evaluate_manual_acceptance_review_value, gym_discrete_movement,
        gym_observation, gym_reward_breakdown, movement_changed, ManualAcceptanceDecision,
        GYM_OBSERVATION_LEN, REQUIRED_PLAYTEST_RUN_IDS,
    };
    use game_core::{GameCore, RewardHint, RunConfig, TerminalKind, TerminalState};
    use serde_json::{json, Value};
    use std::fs;

    #[test]
    fn movement_changed_keeps_strict_replay_precision() {
        assert!(movement_changed(Some([0.0, 1.0]), [0.0001, 1.0]));
        assert!(!movement_changed(Some([0.25, -0.5]), [0.25, -0.5]));
    }

    #[test]
    fn gym_discrete_actions_are_normalized() {
        assert_eq!(gym_discrete_movement(0), game_core::Vec2::ZERO);
        assert!(gym_discrete_movement(2).length() <= 1.0 + f32::EPSILON);
        assert!(gym_discrete_movement(6).length() <= 1.0 + f32::EPSILON);
    }

    #[test]
    fn gym_observation_has_stable_length() {
        let core = GameCore::reset(RunConfig::default());
        let observation = gym_observation(&core.snapshot());

        assert_eq!(observation.len(), GYM_OBSERVATION_LEN);
        assert!(observation.iter().all(|value| value.is_finite()));
    }

    #[test]
    fn gym_reward_breakdown_sums_components() {
        let hint = RewardHint {
            survival_delta: 2.0,
            kill_delta: 0,
            xp_delta: 3.0,
            damage_taken_delta: 4.0,
            level_delta: 1,
        };
        let terminal = TerminalState {
            kind: TerminalKind::Victory,
            time_seconds: 5.0,
            reason: "duration_reached".to_string(),
            final_level: 1,
            kills: 0,
        };
        let breakdown = gym_reward_breakdown(&hint, &[], Some(&terminal));

        assert!((breakdown.survival - 0.02).abs() < f32::EPSILON);
        assert!((breakdown.xp - 0.06).abs() < f32::EPSILON);
        assert!((breakdown.level - 0.5).abs() < f32::EPSILON);
        assert!((breakdown.damage_taken + 0.2).abs() < f32::EPSILON);
        assert!((breakdown.terminal - 5.0).abs() < f32::EPSILON);
        assert!(
            (breakdown.total
                - (breakdown.survival
                    + breakdown.kill
                    + breakdown.xp
                    + breakdown.level
                    + breakdown.damage_taken
                    + breakdown.terminal))
                .abs()
                < f32::EPSILON
        );
    }

    #[test]
    fn content_hash_ignores_harness_gate_metadata() {
        let root =
            std::env::temp_dir().join(format!("soft-candy-hash-test-{}", std::process::id()));
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(root.join("weapons")).unwrap();
        fs::write(root.join("weapons").join("example.json"), "{}\n").unwrap();

        let before = content_hash_for_dir(&root).unwrap();
        fs::write(
            root.join("playtest_gate.json"),
            "{\"decision\":\"playtest\"}\n",
        )
        .unwrap();
        fs::write(
            root.join("acceptance_gate.json"),
            "{\"decision\":\"accept_candidate\"}\n",
        )
        .unwrap();
        let after = content_hash_for_dir(&root).unwrap();

        let _ = fs::remove_dir_all(&root);
        assert_eq!(before, after);
    }

    #[test]
    fn complete_manual_acceptance_review_passes() {
        let review = complete_manual_review_json();
        let gate = evaluate_manual_acceptance_review_value(&review, "base-demo", "fnv1a64:example");

        assert_eq!(gate.decision, ManualAcceptanceDecision::Accept);
        assert_eq!(gate.completed_run_count, REQUIRED_PLAYTEST_RUN_IDS.len());
        assert!(gate.errors.is_empty());
    }

    #[test]
    fn manual_acceptance_review_waits_for_missing_run() {
        let mut review = complete_manual_review_json();
        review["runs"].as_array_mut().unwrap().pop();
        let gate = evaluate_manual_acceptance_review_value(&review, "base-demo", "fnv1a64:example");

        assert_eq!(gate.decision, ManualAcceptanceDecision::Waiting);
        assert!(gate
            .errors
            .iter()
            .any(|error| error.contains("missing required run")));
    }

    #[test]
    fn manual_acceptance_review_repairs_low_rating() {
        let mut review = complete_manual_review_json();
        review["runs"][0]["manual_review"]["fun_rating"] = json!(2);
        let gate = evaluate_manual_acceptance_review_value(&review, "base-demo", "fnv1a64:example");

        assert_eq!(gate.decision, ManualAcceptanceDecision::Repair);
        assert!(gate.errors.iter().any(|error| error.contains("below 3")));
    }

    fn complete_manual_review_json() -> Value {
        let runs = REQUIRED_PLAYTEST_RUN_IDS
            .iter()
            .map(|run_id| {
                json!({
                    "run_id": run_id,
                    "gate_decision": "playtest_pass",
                    "manual_review": {
                        "fun_rating": 4,
                        "clarity_rating": 4,
                        "difficulty_rating": 4,
                        "projectile_readability": 4,
                        "hit_feedback": 4,
                        "xp_pickup_rhythm": 4,
                        "boss_spawn_clarity": 4,
                        "death_reason_clarity": 4,
                        "notes": "人工试玩记录完整，当前原型目标可接受。",
                        "tags": ["fun"],
                        "next_actions": ["进入 accepted_content 候选池并等待版本锁定"]
                    }
                })
            })
            .collect::<Vec<_>>();
        json!({
            "candidate_id": "base-demo",
            "content_hash": "fnv1a64:example",
            "reviewer": "human-reviewer",
            "reviewed_at": "2026-05-25",
            "summary": "9 局人工试玩均达到当前原型目标。",
            "acceptance_decision": "accept_candidate",
            "runs": runs
        })
    }
}
