pub mod content;
mod math;
pub mod meta;
mod rng;

pub use content::{ContentError, ContentPack, ValidationReport};
pub use math::Vec2;
pub use meta::{
    apply_demo_meta_settlement, MetaCodexEntry, MetaProgress, MetaResourceWallet, MetaRunSummary,
    MetaSettlementReport, MetaUnlockSet, RunMode,
};

use content::{
    BossDefinition, CharacterDefinition, EnemyDefinition, EnemyStatsDefinition, EventDefinition,
    EvolutionDefinition, MapDefinition, PassiveDefinition, WaveDefinition, WaveSegmentDefinition,
    WeaponDefinition,
};
use rng::RunRng;
use std::{
    cmp::Ordering,
    collections::{BTreeMap, BTreeSet},
};

const DEFAULT_TICK_RATE: u32 = 30;
const PLAYER_RADIUS: f32 = 18.0;
const CONTACT_DAMAGE_CAP_PER_SECOND: f32 = 35.0;
const HAZARD_DAMAGE_CAP_PER_SECOND: f32 = 42.0;
const MAX_VISIBLE_ENEMIES: usize = 32;
const MAX_VISIBLE_PICKUPS: usize = 16;
const MAX_VISIBLE_PROJECTILES: usize = 48;
const PLAYER_TRAIL_HISTORY_SECONDS: f32 = 90.0;
const PLAYER_TRAIL_SAMPLE_INTERVAL_SECONDS: f32 = 0.5;
const BUBBLE_RUNNER_PICKUP_BOOST_SECONDS: f32 = 1.4;
const BUBBLE_RUNNER_PICKUP_MULTIPLIER: f32 = 1.35;
const CREAM_GUARD_DAMAGE_REDUCTION_SECONDS: f32 = 2.5;
const CREAM_GUARD_DAMAGE_REDUCTION_BONUS: f32 = 0.35;
const SLOW_WEAPON_ENEMY_MULTIPLIER: f32 = 0.78;
const SLOW_WEAPON_ENEMY_DURATION_SECONDS: f32 = 0.75;
const SOUR_CONTROL_ENEMY_SLOW_MULTIPLIER: f32 = 0.58;
const SOUR_CONTROL_ENEMY_SLOW_DURATION_MULTIPLIER: f32 = 1.45;
const LONGER_SUMMONS_LIFETIME_MULTIPLIER: f32 = 1.45;
const BOOMERANG_RETURN_AFTER_LIFETIME_RATIO: f32 = 0.42;
const BOOMERANG_RETURN_SPEED_MULTIPLIER: f32 = 1.08;
const KNOCKBACK_WEAPON_DISTANCE: f32 = 46.0;
const SUMMON_TURRET_MIN_FIRE_INTERVAL_SECONDS: f32 = 0.24;

#[derive(Debug, Clone)]
pub struct RunConfig {
    pub seed: u64,
    pub map_id: String,
    pub character_id: String,
    pub starting_loadout: StartingLoadout,
    pub difficulty: Difficulty,
    pub duration_seconds: f32,
    pub ruleset_version: String,
    pub content_pack_ids: Vec<String>,
    pub tick_rate: u32,
}

impl Default for RunConfig {
    fn default() -> Self {
        Self {
            seed: 12_345,
            map_id: "frosting-grassland".to_string(),
            character_id: "jar-keeper".to_string(),
            starting_loadout: StartingLoadout {
                weapons: vec!["rainbow-candy-shot".to_string()],
                passives: Vec::new(),
            },
            difficulty: Difficulty::Normal,
            duration_seconds: 600.0,
            ruleset_version: "prototype-v0".to_string(),
            content_pack_ids: vec!["base-demo".to_string()],
            tick_rate: DEFAULT_TICK_RATE,
        }
    }
}

#[derive(Debug, Clone, Default)]
pub struct StartingLoadout {
    pub weapons: Vec<String>,
    pub passives: Vec<String>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Difficulty {
    Normal,
}

#[derive(Debug, Clone, Copy)]
pub struct FixedDt {
    seconds: f32,
}

impl FixedDt {
    pub fn from_seconds(seconds: f32) -> Self {
        Self { seconds }
    }

    pub fn from_tick_rate(tick_rate: u32) -> Self {
        Self {
            seconds: 1.0 / tick_rate.max(1) as f32,
        }
    }

    pub fn seconds(self) -> f32 {
        self.seconds
    }
}

#[derive(Debug, Clone, Copy, Default)]
pub struct PlayerAction {
    pub movement: Vec2,
    pub upgrade_choice: Option<usize>,
}

#[derive(Debug, Clone)]
pub struct StepResult {
    pub snapshot: RunSnapshot,
    pub events: Vec<GameEvent>,
    pub reward_hint: RewardHint,
    pub terminal: Option<TerminalState>,
}

#[derive(Debug, Clone, Default)]
pub struct RewardHint {
    pub survival_delta: f32,
    pub kill_delta: u32,
    pub xp_delta: f32,
    pub damage_taken_delta: f32,
    pub level_delta: u32,
}

#[derive(Debug, Clone)]
pub enum GameEvent {
    EnemySpawned {
        entity_id: u64,
        enemy_id: String,
    },
    BossSpawned {
        entity_id: u64,
        boss_id: String,
    },
    BossPhaseChanged {
        entity_id: u64,
        boss_id: String,
        phase_index: usize,
    },
    BossAbilityUsed {
        entity_id: u64,
        boss_id: String,
        ability_id: String,
    },
    WeaponFired {
        weapon_id: String,
        projectile_count: u32,
    },
    EnemyHit {
        entity_id: u64,
        damage: f32,
        weapon_id: String,
    },
    EnemyKilled {
        entity_id: u64,
        enemy_id: String,
    },
    XpDropped {
        entity_id: u64,
        value: f32,
    },
    XpCollected {
        entity_id: u64,
        value: f32,
    },
    LevelUp {
        level: u32,
    },
    UpgradeOffered {
        options: Vec<String>,
    },
    UpgradeChosen {
        option_id: String,
    },
    PlayerDamaged {
        amount: f32,
    },
    ContentEventTriggered {
        event_id: String,
    },
    RunEnded {
        terminal: TerminalState,
    },
}

#[derive(Debug, Clone)]
pub struct RunSnapshot {
    pub time_seconds: f32,
    pub remaining_seconds: f32,
    pub player: PlayerSnapshot,
    pub visible_enemies: Vec<EnemySnapshot>,
    pub visible_pickups: Vec<PickupSnapshot>,
    pub visible_projectiles: Vec<ProjectileSnapshot>,
    pub active_hazards: Vec<HazardSnapshot>,
    pub boss: Option<BossSnapshot>,
    pub upgrade_options: Vec<UpgradeOptionSnapshot>,
    pub build: BuildSnapshot,
    pub map: MapSnapshot,
    pub active_event_effects: Vec<ActiveEventEffectSnapshot>,
    pub metrics_partial: MetricsPartial,
}

#[derive(Debug, Clone)]
pub struct PlayerSnapshot {
    pub position: Vec2,
    pub velocity: Vec2,
    pub health: f32,
    pub max_health: f32,
    pub level: u32,
    pub xp: f32,
    pub xp_to_next_level: f32,
    pub move_speed: f32,
    pub pickup_radius: f32,
    pub damage_multiplier: f32,
    pub cooldown_multiplier: f32,
    pub status_effects: Vec<StatusEffectSnapshot>,
}

#[derive(Debug, Clone)]
pub struct StatusEffectSnapshot {
    pub effect_id: String,
    pub kind: String,
    pub multiplier: f32,
    pub remaining_seconds: f32,
}

#[derive(Debug, Clone)]
pub struct ActiveEventEffectSnapshot {
    pub event_id: String,
    pub effect_type: String,
    pub value: f32,
    pub remaining_seconds: f32,
}

#[derive(Debug, Clone)]
pub struct EnemySnapshot {
    pub entity_id: u64,
    pub enemy_id: String,
    pub position: Vec2,
    pub velocity: Vec2,
    pub health: f32,
    pub max_health: f32,
    pub radius: f32,
    pub threat: f32,
    pub behavior: EnemyBehavior,
    pub is_boss: bool,
    pub is_elite: bool,
}

#[derive(Debug, Clone)]
pub struct PickupSnapshot {
    pub entity_id: u64,
    pub pickup_type: PickupType,
    pub position: Vec2,
    pub value: f32,
    pub radius: f32,
}

#[derive(Debug, Clone)]
pub struct ProjectileSnapshot {
    pub entity_id: u64,
    pub weapon_id: String,
    pub position: Vec2,
    pub velocity: Vec2,
    pub radius: f32,
}

#[derive(Debug, Clone)]
pub struct HazardSnapshot {
    pub position: Vec2,
    pub radius: f32,
    pub slow_multiplier: f32,
    pub damage_per_second: f32,
    pub remaining_seconds: f32,
}

#[derive(Debug, Clone)]
pub struct BossSnapshot {
    pub entity_id: u64,
    pub boss_id: String,
    pub health: f32,
    pub max_health: f32,
    pub position: Vec2,
}

#[derive(Debug, Clone)]
pub struct UpgradeOptionSnapshot {
    pub id: String,
    pub name: String,
    pub tags: Vec<String>,
    pub description: String,
}

#[derive(Debug, Clone, Default)]
pub struct BuildSnapshot {
    pub weapons: Vec<BuildItemSnapshot>,
    pub passives: Vec<BuildItemSnapshot>,
    pub evolutions: Vec<BuildItemSnapshot>,
    pub tags: Vec<String>,
    pub open_evolution_paths: Vec<String>,
}

#[derive(Debug, Clone)]
pub struct BuildItemSnapshot {
    pub id: String,
    pub level: u32,
}

#[derive(Debug, Clone)]
pub struct MapSnapshot {
    pub map_id: String,
    pub width: f32,
    pub height: f32,
}

#[derive(Debug, Clone, Default)]
pub struct MetricsPartial {
    pub kills: u32,
    pub level: u32,
    pub xp_collected: f32,
    pub max_enemy_count: usize,
}

#[derive(Debug, Clone)]
pub struct RunMetrics {
    pub seed: u64,
    pub tick_rate: u32,
    pub duration_seconds: f32,
    pub terminal: Option<TerminalState>,
    pub kills: u32,
    pub level: u32,
    pub xp_collected: f32,
    pub xp_dropped: f32,
    pub damage_dealt_by_weapon: f32,
    pub damage_taken: f32,
    pub damage_taken_by_source: BTreeMap<String, f32>,
    pub boss_damage: f32,
    pub boss_kill_times: Vec<f32>,
    pub max_enemy_count: usize,
    pub max_projectile_count: usize,
    pub upgrade_choices: Vec<String>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct TerminalState {
    pub kind: TerminalKind,
    pub time_seconds: f32,
    pub reason: String,
    pub final_level: u32,
    pub kills: u32,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TerminalKind {
    Victory,
    Defeat,
    Timeout,
    Aborted,
    InvalidState,
}

impl TerminalKind {
    pub fn as_str(self) -> &'static str {
        match self {
            TerminalKind::Victory => "victory",
            TerminalKind::Defeat => "defeat",
            TerminalKind::Timeout => "timeout",
            TerminalKind::Aborted => "aborted",
            TerminalKind::InvalidState => "invalid_state",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EnemyBehavior {
    Chase,
    Dash,
    Split,
    LeaveHazard,
    OrbitPlayer,
    Jump,
    RangedSpit,
    Shielded,
}

impl EnemyBehavior {
    fn from_type(behavior_type: &str) -> Self {
        match behavior_type {
            "dash" => Self::Dash,
            "split" => Self::Split,
            "leave_hazard" => Self::LeaveHazard,
            "orbit_player" => Self::OrbitPlayer,
            "jump" => Self::Jump,
            "ranged_spit" => Self::RangedSpit,
            "shielded" => Self::Shielded,
            _ => Self::Chase,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PickupType {
    Xp,
}

#[derive(Debug, Clone)]
pub struct GameCore {
    config: RunConfig,
    content: ContentPack,
    map: MapRuntime,
    wave_id: String,
    rng: RunRng,
    tick: u64,
    time_seconds: f32,
    next_entity_id: u64,
    player: PlayerState,
    weapons: Vec<WeaponState>,
    passives: Vec<PassiveState>,
    evolutions: Vec<EvolutionState>,
    evaluated_content_events: BTreeSet<String>,
    active_event_effects: Vec<ActiveEventEffect>,
    active_route_echo_hazards: Vec<ActiveRouteEchoHazard>,
    player_position_history: Vec<PlayerPositionSample>,
    player_position_sample_timer: f32,
    player_slow_effects: Vec<ActiveSlowEffect>,
    enemies: Vec<Enemy>,
    hazards: Vec<Hazard>,
    projectiles: Vec<Projectile>,
    pickups: Vec<Pickup>,
    spawn_timer: f32,
    spawned_boss_events: BTreeSet<usize>,
    boss_chests_available: u32,
    pending_upgrade_options: Vec<UpgradeOffer>,
    character_trait_id: Option<String>,
    bubble_runner_pickup_boost_seconds: f32,
    cream_guard_damage_reduction_seconds: f32,
    metrics: RunMetrics,
    terminal: Option<TerminalState>,
}

impl GameCore {
    pub fn reset(config: RunConfig) -> Self {
        Self::reset_with_content(config, ContentPack::base_demo())
            .expect("embedded base demo content must be valid")
    }

    pub fn reset_with_content(
        config: RunConfig,
        content: ContentPack,
    ) -> Result<Self, ContentError> {
        content.validate()?;
        let tick_rate = config.tick_rate.max(1);
        let seed = config.seed;
        let character = content
            .characters
            .get(&config.character_id)
            .ok_or_else(|| {
                ContentError::Validation(vec![format!(
                    "missing character `{}`",
                    config.character_id
                )])
            })?;
        let character_trait_id = character
            .trait_definition
            .as_ref()
            .map(|trait_definition| trait_definition.id.clone());
        let map_definition = content.maps.get(&config.map_id).ok_or_else(|| {
            ContentError::Validation(vec![format!("missing map `{}`", config.map_id)])
        })?;
        let wave_id = content
            .waves
            .values()
            .find(|wave| wave.map_id == config.map_id)
            .map(|wave| wave.id.clone())
            .ok_or_else(|| {
                ContentError::Validation(vec![format!("missing wave for map `{}`", config.map_id)])
            })?;
        let weapon_ids = if config.starting_loadout.weapons.is_empty() {
            character.initial_loadout.weapons.clone()
        } else {
            config.starting_loadout.weapons.clone()
        };
        let mut weapons = Vec::new();
        for weapon_id in weapon_ids {
            let definition = content.weapons.get(&weapon_id).ok_or_else(|| {
                ContentError::Validation(vec![format!("missing weapon `{weapon_id}`")])
            })?;
            weapons.push(WeaponState::from_definition(definition));
        }
        let passive_ids = if config.starting_loadout.passives.is_empty() {
            character.initial_loadout.passives.clone()
        } else {
            config.starting_loadout.passives.clone()
        };
        let mut player = PlayerState::from_definition(character);
        let mut passives = Vec::new();
        for passive_id in passive_ids {
            let definition = content.passives.get(&passive_id).ok_or_else(|| {
                ContentError::Validation(vec![format!("missing passive `{passive_id}`")])
            })?;
            apply_passive_definition(&mut player, &mut passives, &passive_id, definition);
        }
        let initial_player_position = player.position;

        Ok(Self {
            config,
            map: MapRuntime::from_definition(map_definition),
            wave_id,
            player,
            content,
            rng: RunRng::new(seed),
            tick: 0,
            time_seconds: 0.0,
            next_entity_id: 1,
            weapons,
            passives,
            evolutions: Vec::new(),
            evaluated_content_events: BTreeSet::new(),
            active_event_effects: Vec::new(),
            active_route_echo_hazards: Vec::new(),
            player_position_history: vec![PlayerPositionSample {
                time_seconds: 0.0,
                position: initial_player_position,
            }],
            player_position_sample_timer: 0.0,
            player_slow_effects: Vec::new(),
            enemies: Vec::new(),
            hazards: Vec::new(),
            projectiles: Vec::new(),
            pickups: Vec::new(),
            spawn_timer: 0.0,
            spawned_boss_events: BTreeSet::new(),
            boss_chests_available: 0,
            pending_upgrade_options: Vec::new(),
            character_trait_id,
            bubble_runner_pickup_boost_seconds: 0.0,
            cream_guard_damage_reduction_seconds: 0.0,
            metrics: RunMetrics {
                seed,
                tick_rate,
                duration_seconds: 0.0,
                terminal: None,
                kills: 0,
                level: 1,
                xp_collected: 0.0,
                xp_dropped: 0.0,
                damage_dealt_by_weapon: 0.0,
                damage_taken: 0.0,
                damage_taken_by_source: BTreeMap::new(),
                boss_damage: 0.0,
                boss_kill_times: Vec::new(),
                max_enemy_count: 0,
                max_projectile_count: 0,
                upgrade_choices: Vec::new(),
            },
            terminal: None,
        })
    }

    pub fn step(&mut self, action: PlayerAction, dt: FixedDt) -> StepResult {
        if self.terminal.is_some() {
            return StepResult {
                snapshot: self.snapshot(),
                events: Vec::new(),
                reward_hint: RewardHint::default(),
                terminal: self.terminal.clone(),
            };
        }

        let mut events = Vec::new();
        let mut reward_hint = RewardHint::default();

        if !self.pending_upgrade_options.is_empty() {
            if let Some(choice) = action.upgrade_choice {
                self.apply_upgrade_choice(choice, &mut events, &mut reward_hint);
            } else {
                return StepResult {
                    snapshot: self.snapshot(),
                    events,
                    reward_hint,
                    terminal: None,
                };
            }
        }

        if !self.pending_upgrade_options.is_empty() {
            return StepResult {
                snapshot: self.snapshot(),
                events,
                reward_hint,
                terminal: None,
            };
        }

        let dt_seconds = dt.seconds().max(0.0);
        if dt_seconds <= 0.0 {
            return StepResult {
                snapshot: self.snapshot(),
                events,
                reward_hint,
                terminal: None,
            };
        }

        self.tick += 1;
        self.time_seconds += dt_seconds;
        reward_hint.survival_delta = dt_seconds;

        self.update_content_events(dt_seconds, &mut events);
        self.update_player_slow_effects(dt_seconds);
        self.update_player_regen(dt_seconds);
        self.update_hazards(dt_seconds, &mut events, &mut reward_hint);
        self.update_player_movement(action.movement, dt_seconds);
        self.update_character_trait_effects(action.movement, dt_seconds);
        self.record_player_position_history(dt_seconds);
        self.update_route_echo_hazards(dt_seconds);
        self.update_wave_spawns(dt_seconds, &mut events);
        self.update_enemy_behavior(dt_seconds, &mut events);
        self.update_weapon_cooldowns(dt_seconds, &mut events);
        self.update_projectiles(dt_seconds, &mut events);
        self.resolve_contact_damage(dt_seconds, &mut events, &mut reward_hint);
        self.collect_pickups(&mut events, &mut reward_hint);
        self.process_level_ups(&mut events, &mut reward_hint);
        self.record_metrics();
        self.check_terminal_state(&mut events);

        StepResult {
            snapshot: self.snapshot(),
            events,
            reward_hint,
            terminal: self.terminal.clone(),
        }
    }

    pub fn snapshot(&self) -> RunSnapshot {
        let mut visible_enemies = self.enemies.clone();
        visible_enemies.sort_by(|left, right| {
            let left_distance = left.position.distance(self.player.position);
            let right_distance = right.position.distance(self.player.position);
            left_distance
                .partial_cmp(&right_distance)
                .unwrap_or(Ordering::Equal)
        });

        let mut visible_pickups = self.pickups.clone();
        visible_pickups.sort_by(|left, right| {
            let left_distance = left.position.distance(self.player.position);
            let right_distance = right.position.distance(self.player.position);
            left_distance
                .partial_cmp(&right_distance)
                .unwrap_or(Ordering::Equal)
        });

        let mut visible_projectiles = self.projectiles.clone();
        visible_projectiles.sort_by(|left, right| {
            let left_distance = left.position.distance(self.player.position);
            let right_distance = right.position.distance(self.player.position);
            left_distance
                .partial_cmp(&right_distance)
                .unwrap_or(Ordering::Equal)
        });

        let boss = visible_enemies
            .iter()
            .find(|enemy| enemy.is_boss)
            .map(|enemy| BossSnapshot {
                entity_id: enemy.entity_id,
                boss_id: enemy.enemy_id.clone(),
                health: enemy.health,
                max_health: enemy.max_health,
                position: enemy.position,
            });

        RunSnapshot {
            time_seconds: self.time_seconds,
            remaining_seconds: (self.config.duration_seconds - self.time_seconds).max(0.0),
            player: PlayerSnapshot {
                position: self.player.position,
                velocity: self.player.velocity,
                health: self.player.health,
                max_health: self.player.max_health,
                level: self.player.level,
                xp: self.player.xp,
                xp_to_next_level: xp_required(self.player.level),
                move_speed: self.player.move_speed,
                pickup_radius: self.player.pickup_radius,
                damage_multiplier: self.player.damage_multiplier,
                cooldown_multiplier: self.player.cooldown_multiplier,
                status_effects: self.player_status_effects(),
            },
            visible_enemies: visible_enemies
                .into_iter()
                .take(MAX_VISIBLE_ENEMIES)
                .map(EnemySnapshot::from)
                .collect(),
            visible_pickups: visible_pickups
                .into_iter()
                .take(MAX_VISIBLE_PICKUPS)
                .map(PickupSnapshot::from)
                .collect(),
            visible_projectiles: visible_projectiles
                .into_iter()
                .take(MAX_VISIBLE_PROJECTILES)
                .map(ProjectileSnapshot::from)
                .collect(),
            active_hazards: self.hazards.iter().map(HazardSnapshot::from).collect(),
            boss,
            upgrade_options: self
                .pending_upgrade_options
                .iter()
                .map(UpgradeOptionSnapshot::from)
                .collect(),
            build: self.build_snapshot(),
            map: MapSnapshot {
                map_id: self.config.map_id.clone(),
                width: self.map.width,
                height: self.map.height,
            },
            active_event_effects: self
                .active_event_effects
                .iter()
                .map(|effect| ActiveEventEffectSnapshot {
                    event_id: effect.event_id.clone(),
                    effect_type: effect.effect_type.clone(),
                    value: effect.value,
                    remaining_seconds: effect.remaining_seconds.max(0.0),
                })
                .collect(),
            metrics_partial: MetricsPartial {
                kills: self.metrics.kills,
                level: self.player.level,
                xp_collected: self.metrics.xp_collected,
                max_enemy_count: self.metrics.max_enemy_count,
            },
        }
    }

    pub fn metrics(&self) -> RunMetrics {
        let mut metrics = self.metrics.clone();
        metrics.duration_seconds = self.time_seconds;
        metrics.level = self.player.level;
        metrics.terminal = self.terminal.clone();
        metrics
    }

    pub fn is_terminal(&self) -> bool {
        self.terminal.is_some()
    }

    pub fn fixed_dt(&self) -> FixedDt {
        FixedDt::from_tick_rate(self.config.tick_rate)
    }

    fn player_status_effects(&self) -> Vec<StatusEffectSnapshot> {
        let mut effects = self
            .player_slow_effects
            .iter()
            .map(|effect| StatusEffectSnapshot {
                effect_id: "movement_slow".to_string(),
                kind: "slow".to_string(),
                multiplier: effect.multiplier,
                remaining_seconds: effect.remaining_seconds.max(0.0),
            })
            .collect::<Vec<_>>();
        if self.character_trait_id.as_deref() == Some("bubble-runner")
            && self.bubble_runner_pickup_boost_seconds > 0.0
        {
            effects.push(StatusEffectSnapshot {
                effect_id: "bubble-runner".to_string(),
                kind: "pickup_boost".to_string(),
                multiplier: BUBBLE_RUNNER_PICKUP_MULTIPLIER,
                remaining_seconds: self.bubble_runner_pickup_boost_seconds,
            });
        }
        if self.character_trait_id.as_deref() == Some("cream-guard")
            && self.cream_guard_damage_reduction_seconds > 0.0
        {
            effects.push(StatusEffectSnapshot {
                effect_id: "cream-guard".to_string(),
                kind: "damage_reduction".to_string(),
                multiplier: CREAM_GUARD_DAMAGE_REDUCTION_BONUS,
                remaining_seconds: self.cream_guard_damage_reduction_seconds,
            });
        }
        effects
    }

    fn update_player_slow_effects(&mut self, dt: f32) {
        for effect in &mut self.player_slow_effects {
            effect.remaining_seconds -= dt;
        }
        self.player_slow_effects
            .retain(|effect| effect.remaining_seconds > 0.0);
    }

    fn update_player_regen(&mut self, dt: f32) {
        if self.player.regen_per_second <= 0.0 || self.player.health <= 0.0 {
            return;
        }

        self.player.health =
            (self.player.health + self.player.regen_per_second * dt).min(self.player.max_health);
    }

    fn update_hazards(
        &mut self,
        dt: f32,
        events: &mut Vec<GameEvent>,
        reward_hint: &mut RewardHint,
    ) {
        for hazard in &mut self.hazards {
            hazard.remaining_seconds -= dt;
        }
        self.hazards.retain(|hazard| hazard.remaining_seconds > 0.0);

        let mut slow_effects = Vec::new();
        let mut hazard_damage_per_second: f32 = 0.0;
        for hazard in &self.hazards {
            if self.player.position.distance(hazard.position) <= PLAYER_RADIUS + hazard.radius {
                slow_effects.push((hazard.slow_multiplier, dt * 2.0));
                hazard_damage_per_second += hazard.damage_per_second.max(0.0);
            }
        }
        for (multiplier, duration_seconds) in slow_effects {
            self.apply_player_slow(multiplier, duration_seconds);
        }
        self.apply_player_damage(
            hazard_damage_per_second.min(HAZARD_DAMAGE_CAP_PER_SECOND),
            dt,
            "hazard",
            events,
            reward_hint,
        );
    }

    fn update_player_movement(&mut self, movement: Vec2, dt: f32) {
        let normalized = movement.clamp_length_max(1.0);
        self.player.velocity =
            normalized * self.player.move_speed * self.active_player_slow_multiplier();
        self.player.position += self.player.velocity * dt;
        self.player.position.x = self
            .player
            .position
            .x
            .clamp(-self.map.width * 0.5, self.map.width * 0.5);
        self.player.position.y = self
            .player
            .position
            .y
            .clamp(-self.map.height * 0.5, self.map.height * 0.5);
    }

    fn record_player_position_history(&mut self, dt: f32) {
        self.player_position_sample_timer -= dt;
        if self.player_position_sample_timer <= 0.0 {
            self.player_position_history.push(PlayerPositionSample {
                time_seconds: self.time_seconds,
                position: self.player.position,
            });
            self.player_position_sample_timer += PLAYER_TRAIL_SAMPLE_INTERVAL_SECONDS;
        }

        let min_time = self.time_seconds - PLAYER_TRAIL_HISTORY_SECONDS;
        self.player_position_history
            .retain(|sample| sample.time_seconds >= min_time);
    }

    fn active_player_slow_multiplier(&self) -> f32 {
        self.player_slow_effects
            .iter()
            .map(|effect| effect.multiplier)
            .fold(1.0, f32::min)
            .clamp(0.2, 1.0)
    }

    fn update_content_events(&mut self, dt: f32, events: &mut Vec<GameEvent>) {
        for effect in &mut self.active_event_effects {
            effect.remaining_seconds -= dt;
        }
        self.active_event_effects
            .retain(|effect| effect.remaining_seconds > 0.0);

        for echo in &mut self.active_route_echo_hazards {
            echo.remaining_seconds -= dt;
            echo.next_spawn_seconds -= dt;
        }
        self.active_route_echo_hazards
            .retain(|effect| effect.remaining_seconds > 0.0);

        let event_ids = self.content.events.keys().cloned().collect::<Vec<_>>();
        for event_id in event_ids {
            if self.evaluated_content_events.contains(&event_id) {
                continue;
            }
            let Some(event) = self.content.events.get(&event_id).cloned() else {
                continue;
            };
            if !self.content_event_window_is_open(&event) {
                continue;
            }

            self.evaluated_content_events.insert(event_id);
            let chance = event.trigger.chance.unwrap_or(1.0).clamp(0.0, 1.0);
            if chance >= 1.0 || (chance > 0.0 && self.rng.next_f32() <= chance) {
                self.trigger_content_event(&event, events);
            }
        }
    }

    fn content_event_window_is_open(&self, event: &EventDefinition) -> bool {
        match event.trigger.trigger_type.as_str() {
            "time_window" => {
                let start_second = event.trigger.start_second.unwrap_or(0.0);
                let end_second = event
                    .trigger
                    .end_second
                    .unwrap_or(self.config.duration_seconds);
                self.time_seconds >= start_second && self.time_seconds <= end_second
            }
            "map_entry" => self.time_seconds <= self.fixed_dt().seconds() * 1.5,
            _ => false,
        }
    }

    fn trigger_content_event(&mut self, event: &EventDefinition, events: &mut Vec<GameEvent>) {
        events.push(GameEvent::ContentEventTriggered {
            event_id: event.id.clone(),
        });

        for effect in &event.effects {
            match effect.effect_type.as_str() {
                "heal" => {
                    self.player.health =
                        (self.player.health + effect.value).min(self.player.max_health);
                }
                "xp_multiplier"
                | "spawn_rate_multiplier"
                | "pickup_radius_multiplier"
                | "damage_multiplier" => {
                    let Some(duration_seconds) = effect.duration_seconds else {
                        continue;
                    };
                    self.active_event_effects.push(ActiveEventEffect {
                        event_id: event.id.clone(),
                        effect_type: effect.effect_type.clone(),
                        value: effect.value,
                        remaining_seconds: duration_seconds,
                    });
                }
                "offer_upgrade" => {
                    self.offer_event_upgrade_options(events);
                }
                "spawn_enemy" => {
                    self.spawn_event_enemies(effect, events);
                }
                "spawn_hazard" => {
                    self.spawn_event_hazards(effect);
                }
                "route_echo_hazard" => {
                    self.active_route_echo_hazards
                        .push(ActiveRouteEchoHazard::from_effect(effect));
                }
                _ => {}
            }
        }
    }

    fn update_route_echo_hazards(&mut self, _dt: f32) {
        let mut hazard_specs = Vec::new();
        for echo in &mut self.active_route_echo_hazards {
            while echo.next_spawn_seconds <= 0.0 && hazard_specs.len() < 16 {
                hazard_specs.push(*echo);
                echo.next_spawn_seconds += echo.sample_interval_seconds;
            }
        }

        for spec in hazard_specs {
            let positions = self.route_echo_positions(
                spec.history_seconds,
                spec.trigger_radius,
                spec.spawn_count,
            );
            for position in positions {
                self.hazards.push(Hazard {
                    position,
                    radius: spec.radius,
                    remaining_seconds: spec.hazard_duration_seconds,
                    slow_multiplier: spec.slow_multiplier,
                    damage_per_second: spec.damage_per_second,
                });
            }
        }
    }

    fn route_echo_positions(
        &self,
        history_seconds: f32,
        trigger_radius: f32,
        count: u32,
    ) -> Vec<Vec2> {
        let mut positions = Vec::new();
        for index in 0..count {
            let offset_seconds = index as f32 * history_seconds.max(0.5) * 0.35;
            if let Some(position) =
                self.route_echo_position(history_seconds + offset_seconds, trigger_radius)
            {
                if positions
                    .iter()
                    .all(|existing: &Vec2| existing.distance(position) > PLAYER_RADIUS)
                {
                    positions.push(position);
                }
            }
        }
        positions
    }

    fn route_echo_position(&self, history_seconds: f32, trigger_radius: f32) -> Option<Vec2> {
        let target_time = self.time_seconds - history_seconds;
        let sample = self.player_position_history.iter().min_by(|left, right| {
            let left_delta = (left.time_seconds - target_time).abs();
            let right_delta = (right.time_seconds - target_time).abs();
            left_delta
                .partial_cmp(&right_delta)
                .unwrap_or(Ordering::Equal)
        })?;
        if (sample.time_seconds - target_time).abs() > PLAYER_TRAIL_SAMPLE_INTERVAL_SECONDS * 1.5 {
            return None;
        }
        if self.player.position.distance(sample.position) > trigger_radius {
            return None;
        }
        Some(sample.position)
    }

    fn offer_event_upgrade_options(&mut self, events: &mut Vec<GameEvent>) {
        if !self.pending_upgrade_options.is_empty() {
            return;
        }

        let upgrade_options = self.generate_upgrade_options();
        if upgrade_options.is_empty() {
            return;
        }

        let option_ids = upgrade_options
            .iter()
            .map(|option| option.snapshot.id.clone())
            .collect();
        self.pending_upgrade_options = upgrade_options;
        events.push(GameEvent::UpgradeOffered {
            options: option_ids,
        });
    }

    fn spawn_event_enemies(
        &mut self,
        effect: &content::EventEffectDefinition,
        events: &mut Vec<GameEvent>,
    ) {
        let Some(enemy_id) = effect.enemy_id.as_deref() else {
            return;
        };
        let Some(definition) = self.content.enemies.get(enemy_id).cloned() else {
            return;
        };

        let count = effect.value.round().clamp(1.0, 12.0) as u32;
        for _ in 0..count {
            if self.enemies.len() >= 160 {
                break;
            }
            let position =
                self.spawn_position_around_player(self.map.spawn_min, self.map.spawn_max);
            let enemy =
                Enemy::from_enemy_definition(self.allocate_entity_id(), position, &definition);
            events.push(GameEvent::EnemySpawned {
                entity_id: enemy.entity_id,
                enemy_id: enemy.enemy_id.clone(),
            });
            self.enemies.push(enemy);
        }
    }

    fn spawn_event_hazards(&mut self, effect: &content::EventEffectDefinition) {
        let count = effect.value.round().clamp(1.0, 8.0) as u32;
        let radius = effect.radius.unwrap_or(72.0).max(4.0);
        let duration_seconds = effect.duration_seconds.unwrap_or(6.0).max(0.1);
        let slow_multiplier = effect.slow_multiplier.unwrap_or(0.65).clamp(0.2, 1.0);
        let placement = effect.placement.as_deref().unwrap_or("near_player");

        for index in 0..count {
            let position = match placement {
                "player_forward_lane" => self.player_forward_lane_position(effect, index, count),
                _ => self.spawn_position_around_player(80.0, self.map.spawn_min.max(120.0)),
            };
            self.hazards.push(Hazard {
                position,
                radius,
                remaining_seconds: duration_seconds,
                slow_multiplier,
                damage_per_second: 0.0,
            });
        }
    }

    fn player_forward_lane_position(
        &self,
        effect: &content::EventEffectDefinition,
        index: u32,
        count: u32,
    ) -> Vec2 {
        let forward = if self.player.velocity.length() > 0.1 {
            self.player.velocity.normalized_or_zero()
        } else {
            Vec2::new(1.0, 0.0)
        };
        let lateral = Vec2::new(-forward.y, forward.x);
        let min_distance = effect.min_distance.unwrap_or(72.0).max(0.0);
        let max_distance = effect
            .max_distance
            .unwrap_or(self.map.spawn_min.max(min_distance + 96.0))
            .max(min_distance);
        let lane_width = effect.lane_width.unwrap_or(56.0).max(0.0);
        let t = if count <= 1 {
            0.5
        } else {
            index as f32 / (count - 1) as f32
        };
        let distance = min_distance + (max_distance - min_distance) * t;
        let side = match index % 3 {
            0 => 0.0,
            1 => 1.0,
            _ => -1.0,
        };
        self.clamp_to_map(self.player.position + forward * distance + lateral * lane_width * side)
    }

    fn active_event_multiplier(&self, effect_type: &str) -> f32 {
        self.active_event_effects
            .iter()
            .filter(|effect| effect.effect_type == effect_type)
            .map(|effect| effect.value)
            .fold(1.0, |current, value| current * value)
    }

    fn update_wave_spawns(&mut self, dt: f32, events: &mut Vec<GameEvent>) {
        let Some(wave) = self.content.waves.get(&self.wave_id).cloned() else {
            return;
        };

        let boss_to_spawn = wave
            .boss_events
            .iter()
            .enumerate()
            .find(|(index, event)| {
                self.time_seconds >= event.time_second && !self.spawned_boss_events.contains(index)
            })
            .map(|(index, event)| (index, event.boss_id.clone()));

        if let Some((boss_event_index, boss_id)) = boss_to_spawn {
            if let Some(definition) = self.content.bosses.get(&boss_id).cloned() {
                let position =
                    self.spawn_position_around_player(self.map.spawn_min, self.map.spawn_max);
                let boss =
                    Enemy::from_boss_definition(self.allocate_entity_id(), position, &definition);
                events.push(GameEvent::BossSpawned {
                    entity_id: boss.entity_id,
                    boss_id: boss.enemy_id.clone(),
                });
                self.enemies.push(boss);
                self.spawned_boss_events.insert(boss_event_index);
            }
        }

        let Some(segment) = wave_segment_for_time(&wave, self.time_seconds).cloned() else {
            return;
        };

        if self.enemies.len() >= segment.max_alive {
            return;
        }

        let spawn_interval = (segment.spawn_interval_ms / 1000.0)
            / self
                .active_event_multiplier("spawn_rate_multiplier")
                .max(0.1);

        self.spawn_timer -= dt;
        if self.spawn_timer > 0.0 {
            return;
        }

        self.spawn_timer += spawn_interval;
        let free_slots = segment.max_alive.saturating_sub(self.enemies.len());
        let spawn_count = segment.spawn_count.min(free_slots);
        for _ in 0..spawn_count {
            let Some(enemy_id) = pick_enemy_id(&segment, &mut self.rng) else {
                continue;
            };
            if let Some(definition) = self.content.enemies.get(&enemy_id).cloned() {
                let position =
                    self.spawn_position_around_player(self.map.spawn_min, self.map.spawn_max);
                let enemy =
                    Enemy::from_enemy_definition(self.allocate_entity_id(), position, &definition);
                events.push(GameEvent::EnemySpawned {
                    entity_id: enemy.entity_id,
                    enemy_id: enemy.enemy_id.clone(),
                });
                self.enemies.push(enemy);
            }
        }
    }

    fn update_enemy_behavior(&mut self, dt: f32, events: &mut Vec<GameEvent>) {
        let player_position = self.player.position;
        let half_width = self.map.width * 0.5;
        let half_height = self.map.height * 0.5;
        let mut new_hazards = Vec::new();
        let mut boss_actions = Vec::new();

        for enemy in &mut self.enemies {
            enemy.update_slow(dt);
            let direction = (player_position - enemy.position).normalized_or_zero();
            let mut spawned_hazards = Vec::new();
            let base_velocity = match enemy.behavior {
                EnemyBehavior::Dash | EnemyBehavior::Jump => enemy.dash_velocity(direction, dt),
                EnemyBehavior::OrbitPlayer => enemy.orbit_velocity(player_position, direction),
                EnemyBehavior::RangedSpit => {
                    let (velocity, hazards) =
                        enemy.ranged_spit_velocity_and_hazards(player_position, direction, dt);
                    spawned_hazards = hazards;
                    velocity
                }
                _ => direction * enemy.move_speed,
            };
            enemy.velocity = base_velocity * enemy.active_slow_multiplier();
            enemy.position += enemy.velocity * dt;
            enemy.position.x = enemy.position.x.clamp(-half_width, half_width);
            enemy.position.y = enemy.position.y.clamp(-half_height, half_height);
            for mut hazard in spawned_hazards {
                hazard.position.x = hazard.position.x.clamp(-half_width, half_width);
                hazard.position.y = hazard.position.y.clamp(-half_height, half_height);
                new_hazards.push(hazard);
            }

            if enemy.behavior == EnemyBehavior::LeaveHazard {
                enemy.behavior_state.hazard_cooldown_remaining -= dt;
                if enemy.behavior_state.hazard_cooldown_remaining <= 0.0 {
                    new_hazards.push(Hazard {
                        position: enemy.position,
                        radius: enemy.behavior_state.hazard_radius,
                        remaining_seconds: enemy.behavior_state.hazard_duration_seconds,
                        slow_multiplier: enemy.behavior_state.hazard_slow_multiplier,
                        damage_per_second: 0.0,
                    });
                    enemy.behavior_state.hazard_cooldown_remaining +=
                        enemy.behavior_state.hazard_interval_seconds;
                }
            }

            if enemy.is_boss {
                if let Some(definition) = self.content.bosses.get(&enemy.enemy_id) {
                    let phase_index = boss_phase_index(definition, enemy.health / enemy.max_health);
                    if phase_index != enemy.boss_phase_index {
                        enemy.boss_phase_index = phase_index;
                        enemy.boss_ability_cursor = 0;
                        enemy.boss_ability_cooldown_remaining = 0.0;
                        events.push(GameEvent::BossPhaseChanged {
                            entity_id: enemy.entity_id,
                            boss_id: enemy.enemy_id.clone(),
                            phase_index,
                        });
                    }

                    enemy.boss_ability_cooldown_remaining -= dt;
                    if enemy.boss_ability_cooldown_remaining <= 0.0 {
                        if let Some(ability_id) =
                            boss_phase_ability(definition, phase_index, enemy.boss_ability_cursor)
                        {
                            enemy.boss_ability_cursor = enemy.boss_ability_cursor.wrapping_add(1);
                            enemy.boss_ability_cooldown_remaining =
                                boss_ability_cooldown_seconds(&ability_id);
                            events.push(GameEvent::BossAbilityUsed {
                                entity_id: enemy.entity_id,
                                boss_id: enemy.enemy_id.clone(),
                                ability_id: ability_id.clone(),
                            });
                            boss_actions.extend(boss_ability_actions(
                                &ability_id,
                                enemy.position,
                                player_position,
                            ));
                        }
                    }
                }
            }
        }

        self.hazards.extend(new_hazards);
        self.apply_boss_ability_actions(boss_actions, events);
    }

    fn apply_boss_ability_actions(
        &mut self,
        actions: Vec<BossAbilityAction>,
        events: &mut Vec<GameEvent>,
    ) {
        for action in actions {
            match action {
                BossAbilityAction::SpawnEnemy {
                    enemy_id,
                    count,
                    origin,
                    radius,
                } => {
                    let Some(definition) = self.content.enemies.get(&enemy_id).cloned() else {
                        continue;
                    };
                    for _ in 0..count.min(6) {
                        let position = self.random_position_near(origin, 40.0, radius);
                        let enemy = Enemy::from_enemy_definition(
                            self.allocate_entity_id(),
                            position,
                            &definition,
                        );
                        events.push(GameEvent::EnemySpawned {
                            entity_id: enemy.entity_id,
                            enemy_id: enemy.enemy_id.clone(),
                        });
                        self.enemies.push(enemy);
                    }
                }
                BossAbilityAction::SpawnHazard {
                    count,
                    origin,
                    radius,
                    hazard_radius,
                    duration_seconds,
                    slow_multiplier,
                    damage_per_second,
                } => {
                    for _ in 0..count.min(8) {
                        let position = self.random_position_near(origin, 0.0, radius);
                        self.hazards.push(Hazard {
                            position,
                            radius: hazard_radius,
                            remaining_seconds: duration_seconds,
                            slow_multiplier,
                            damage_per_second,
                        });
                    }
                }
            }
        }
    }

    fn update_weapon_cooldowns(&mut self, dt: f32, events: &mut Vec<GameEvent>) {
        for weapon_index in 0..self.weapons.len() {
            self.weapons[weapon_index].cooldown_remaining -= dt;
            if self.weapons[weapon_index].cooldown_remaining > 0.0 {
                continue;
            }

            let targeting_mode = self.weapons[weapon_index].targeting_mode.clone();
            let range = self.weapons[weapon_index].range;
            let Some(target_position) = self.find_weapon_target_position(&targeting_mode, range)
            else {
                continue;
            };

            let weapon_id = self.weapons[weapon_index].id.clone();
            let weapon_type = self.weapons[weapon_index].weapon_type.clone();
            let count = self.weapons[weapon_index].projectile_count();
            let projectile_speed = self.weapons[weapon_index].projectile_speed;
            let damage = self.weapons[weapon_index].damage
                * self.player.damage_multiplier
                * self.active_event_multiplier("damage_multiplier");
            let radius =
                self.weapons[weapon_index].radius * self.player.projectile_size_multiplier.max(0.1);
            let pierce = self.weapons[weapon_index].pierce;
            let cooldown = self.weapons[weapon_index].cooldown * self.player.cooldown_multiplier;
            let duration = self.weapons[weapon_index].duration;
            let weapon_tags = self.weapons[weapon_index].tags.clone();
            let spawn_count = if weapon_type == "summon" {
                let active_count = self.active_summon_projectile_count(&weapon_id);
                if active_count >= count {
                    self.weapons[weapon_index].cooldown_remaining += cooldown;
                    continue;
                }
                count - active_count
            } else {
                count
            };
            let lifetime = weapon_lifetime(&weapon_type, duration)
                * self.player.effect_duration_multiplier.max(0.1)
                * self.character_weapon_lifetime_multiplier(&weapon_type);
            let (enemy_slow_multiplier, enemy_slow_duration_seconds) =
                self.enemy_slow_effect_for_weapon(&weapon_tags);
            let enemy_knockback_distance = enemy_knockback_distance_for_weapon(&weapon_tags);
            let boomerang_return_after_seconds =
                boomerang_return_after_seconds(&weapon_tags, lifetime);
            let boomerang_return_speed = if boomerang_return_after_seconds.is_some() {
                projectile_speed * BOOMERANG_RETURN_SPEED_MULTIPLIER
            } else {
                0.0
            };
            let base_direction = (target_position - self.player.position).normalized_or_zero();
            let spread_step = if spawn_count > 1 { 0.18 } else { 0.0 };
            let spread_start = -spread_step * (spawn_count.saturating_sub(1) as f32) * 0.5;
            let turret_fire_interval_seconds = if weapon_type == "summon" {
                cooldown.max(SUMMON_TURRET_MIN_FIRE_INTERVAL_SECONDS)
            } else {
                0.0
            };
            let turret_range = if weapon_type == "summon" { range } else { 0.0 };

            for projectile_index in 0..spawn_count {
                let runtime = self.weapon_projectile_runtime(WeaponProjectileRuntimeInput {
                    weapon_type: &weapon_type,
                    target_position,
                    base_direction,
                    projectile_index,
                    projectile_count: spawn_count,
                    spread_start,
                    spread_step,
                    projectile_speed,
                    pierce,
                    lifetime,
                    radius,
                });
                let pierce_remaining = if boomerang_return_after_seconds.is_some() {
                    runtime
                        .pierce_remaining
                        .max(pierce.saturating_mul(2).max(2))
                } else {
                    runtime.pierce_remaining
                };
                let projectile = Projectile {
                    entity_id: self.allocate_entity_id(),
                    weapon_id: weapon_id.clone(),
                    position: runtime.position,
                    velocity: runtime.velocity,
                    damage,
                    radius,
                    pierce_remaining,
                    lifetime: runtime.lifetime,
                    enemy_slow_multiplier,
                    enemy_slow_duration_seconds,
                    enemy_knockback_distance,
                    age_seconds: 0.0,
                    boomerang_return_after_seconds,
                    boomerang_return_speed,
                    turret_fire_interval_seconds,
                    turret_fire_cooldown_seconds: 0.0,
                    turret_range,
                };
                self.projectiles.push(projectile);
            }

            self.weapons[weapon_index].cooldown_remaining += cooldown;
            events.push(GameEvent::WeaponFired {
                weapon_id,
                projectile_count: spawn_count as u32,
            });
        }
    }

    fn active_summon_projectile_count(&self, weapon_id: &str) -> usize {
        self.projectiles
            .iter()
            .filter(|projectile| projectile.weapon_id == weapon_id && projectile.is_summon_turret())
            .count()
    }

    fn weapon_projectile_runtime(
        &self,
        input: WeaponProjectileRuntimeInput<'_>,
    ) -> ProjectileRuntime {
        match input.weapon_type {
            "orbit" => {
                let angle = std::f32::consts::TAU * input.projectile_index as f32
                    / input.projectile_count.max(1) as f32
                    + self.time_seconds * 1.7;
                let radial = Vec2::new(angle.cos(), angle.sin());
                let tangent = Vec2::new(-angle.sin(), angle.cos());
                let orbit_radius = (PLAYER_RADIUS + input.radius + 18.0)
                    .max(self.weapons_orbit_range_hint(input.radius));
                ProjectileRuntime {
                    position: self.player.position + radial * orbit_radius,
                    velocity: tangent * input.projectile_speed * 0.35,
                    pierce_remaining: input.pierce.max(2),
                    lifetime: input.lifetime,
                }
            }
            "burst" | "zone" => {
                let angle = std::f32::consts::TAU * input.projectile_index as f32
                    / input.projectile_count.max(1) as f32;
                let offset = if input.projectile_count > 1 {
                    Vec2::new(angle.cos(), angle.sin()) * input.radius * 0.65
                } else {
                    Vec2::ZERO
                };
                ProjectileRuntime {
                    position: self.clamp_to_map(input.target_position + offset),
                    velocity: Vec2::ZERO,
                    pierce_remaining: input.pierce.max(3),
                    lifetime: input.lifetime,
                }
            }
            "summon" => {
                let angle = std::f32::consts::TAU * input.projectile_index as f32
                    / input.projectile_count.max(1) as f32
                    + 0.6;
                let summon_position =
                    self.player.position + Vec2::new(angle.cos(), angle.sin()) * 44.0;
                ProjectileRuntime {
                    position: self.clamp_to_map(summon_position),
                    velocity: Vec2::ZERO,
                    pierce_remaining: input.pierce,
                    lifetime: input.lifetime,
                }
            }
            "beam" => {
                let angle = input.spread_start + input.spread_step * input.projectile_index as f32;
                let direction = input.base_direction.rotated(angle).normalized_or_zero();
                ProjectileRuntime {
                    position: self.player.position,
                    velocity: direction * input.projectile_speed,
                    pierce_remaining: input.pierce.max(4),
                    lifetime: input.lifetime,
                }
            }
            _ => {
                let angle = input.spread_start + input.spread_step * input.projectile_index as f32;
                let direction = input.base_direction.rotated(angle).normalized_or_zero();
                ProjectileRuntime {
                    position: self.player.position,
                    velocity: direction * input.projectile_speed,
                    pierce_remaining: input.pierce,
                    lifetime: input.lifetime,
                }
            }
        }
    }

    fn weapons_orbit_range_hint(&self, radius: f32) -> f32 {
        (radius * 2.0 + PLAYER_RADIUS).min(96.0)
    }

    fn character_weapon_lifetime_multiplier(&self, weapon_type: &str) -> f32 {
        if self.character_trait_id.as_deref() == Some("longer-summons") && weapon_type == "summon" {
            LONGER_SUMMONS_LIFETIME_MULTIPLIER
        } else {
            1.0
        }
    }

    fn enemy_slow_effect_for_weapon(&self, weapon_tags: &[String]) -> (f32, f32) {
        if !weapon_tags.iter().any(|tag| tag == "slow") {
            return (1.0, 0.0);
        }

        if self.character_trait_id.as_deref() == Some("sour-control") {
            (
                SOUR_CONTROL_ENEMY_SLOW_MULTIPLIER,
                SLOW_WEAPON_ENEMY_DURATION_SECONDS * SOUR_CONTROL_ENEMY_SLOW_DURATION_MULTIPLIER,
            )
        } else {
            (
                SLOW_WEAPON_ENEMY_MULTIPLIER,
                SLOW_WEAPON_ENEMY_DURATION_SECONDS,
            )
        }
    }

    fn update_projectiles(&mut self, dt: f32, events: &mut Vec<GameEvent>) {
        let player_position = self.player.position;
        let half_width = self.map.width * 0.5;
        let half_height = self.map.height * 0.5;
        for projectile in &mut self.projectiles {
            projectile.age_seconds += dt;
            if let Some(return_after_seconds) = projectile.boomerang_return_after_seconds {
                if projectile.age_seconds >= return_after_seconds {
                    let return_direction =
                        (player_position - projectile.position).normalized_or_zero();
                    if return_direction.length_squared() > 0.0 {
                        projectile.velocity =
                            return_direction * projectile.boomerang_return_speed.max(1.0);
                    }
                }
            }
            if projectile.is_summon_turret() {
                projectile.lifetime -= dt;
                projectile.turret_fire_cooldown_seconds -= dt;
                if projectile.turret_fire_cooldown_seconds <= 0.0 {
                    if let Some((target_index, _)) = self
                        .enemies
                        .iter()
                        .enumerate()
                        .filter(|(_, enemy)| {
                            enemy.health > 0.0
                                && enemy.position.distance(projectile.position)
                                    <= projectile.turret_range
                        })
                        .map(|(index, enemy)| (index, enemy.position.distance(projectile.position)))
                        .min_by(|left, right| {
                            left.1.partial_cmp(&right.1).unwrap_or(Ordering::Equal)
                        })
                    {
                        let enemy = &mut self.enemies[target_index];
                        let damage = projectile.damage
                            * enemy
                                .projectile_damage_multiplier(projectile.position, player_position);
                        enemy.health -= damage;
                        self.metrics.damage_dealt_by_weapon += damage;
                        if enemy.is_boss {
                            self.metrics.boss_damage += damage;
                        }
                        enemy.apply_slow(
                            projectile.enemy_slow_multiplier,
                            projectile.enemy_slow_duration_seconds,
                        );
                        enemy.apply_knockback(
                            player_position,
                            projectile.enemy_knockback_distance,
                            half_width,
                            half_height,
                        );
                        events.push(GameEvent::EnemyHit {
                            entity_id: enemy.entity_id,
                            damage,
                            weapon_id: projectile.weapon_id.clone(),
                        });
                        projectile.turret_fire_cooldown_seconds +=
                            projectile.turret_fire_interval_seconds;
                    }
                }
                continue;
            }
            projectile.position += projectile.velocity * dt;
            projectile.lifetime -= dt;

            if projectile.pierce_remaining == 0 {
                continue;
            }

            for enemy in &mut self.enemies {
                if enemy.health <= 0.0 {
                    continue;
                }

                let hit_distance = projectile.radius + enemy.radius;
                if projectile.position.distance(enemy.position) <= hit_distance {
                    let damage = projectile.damage
                        * enemy.projectile_damage_multiplier(projectile.position, player_position);
                    enemy.health -= damage;
                    self.metrics.damage_dealt_by_weapon += damage;
                    if enemy.is_boss {
                        self.metrics.boss_damage += damage;
                    }
                    enemy.apply_slow(
                        projectile.enemy_slow_multiplier,
                        projectile.enemy_slow_duration_seconds,
                    );
                    enemy.apply_knockback(
                        player_position,
                        projectile.enemy_knockback_distance,
                        half_width,
                        half_height,
                    );
                    projectile.pierce_remaining = projectile.pierce_remaining.saturating_sub(1);
                    events.push(GameEvent::EnemyHit {
                        entity_id: enemy.entity_id,
                        damage,
                        weapon_id: projectile.weapon_id.clone(),
                    });
                    if projectile.pierce_remaining == 0 {
                        break;
                    }
                }
            }
        }

        self.projectiles
            .retain(|projectile| projectile.lifetime > 0.0 && projectile.pierce_remaining > 0);

        let mut killed = Vec::new();
        self.enemies.retain(|enemy| {
            if enemy.health <= 0.0 {
                killed.push(enemy.clone());
                false
            } else {
                true
            }
        });

        for enemy in killed {
            self.metrics.kills += 1;
            if enemy.is_boss {
                self.boss_chests_available = self.boss_chests_available.saturating_add(1);
                self.metrics.boss_kill_times.push(self.time_seconds);
            }
            events.push(GameEvent::EnemyKilled {
                entity_id: enemy.entity_id,
                enemy_id: enemy.enemy_id.clone(),
            });
            self.spawn_split_children(&enemy, events);
            let pickup = Pickup {
                entity_id: self.allocate_entity_id(),
                pickup_type: PickupType::Xp,
                position: enemy.position,
                value: enemy.xp_value,
                radius: 10.0,
            };
            self.metrics.xp_dropped += pickup.value;
            events.push(GameEvent::XpDropped {
                entity_id: pickup.entity_id,
                value: pickup.value,
            });
            self.pickups.push(pickup);
        }

        if self.pending_upgrade_options.is_empty() {
            let evolution_options = self.generate_evolution_options();
            if !evolution_options.is_empty() {
                let option_ids = evolution_options
                    .iter()
                    .map(|option| option.snapshot.id.clone())
                    .collect::<Vec<_>>();
                self.pending_upgrade_options = evolution_options;
                events.push(GameEvent::UpgradeOffered {
                    options: option_ids,
                });
            }
        }
    }

    fn spawn_split_children(&mut self, enemy: &Enemy, events: &mut Vec<GameEvent>) {
        if enemy.behavior != EnemyBehavior::Split {
            return;
        }
        let Some(child_enemy_id) = enemy.behavior_state.split_child_enemy_id.clone() else {
            return;
        };
        let Some(definition) = self.content.enemies.get(&child_enemy_id).cloned() else {
            return;
        };

        let child_count = enemy.behavior_state.split_child_count.min(8);
        if child_count == 0 {
            return;
        }

        for child_index in 0..child_count {
            let angle = std::f32::consts::TAU * child_index as f32 / child_count as f32;
            let offset = Vec2::new(angle.cos(), angle.sin()) * (enemy.radius + 10.0);
            let mut child = Enemy::from_enemy_definition(
                self.allocate_entity_id(),
                self.clamp_to_map(enemy.position + offset),
                &definition,
            );
            let health_multiplier = enemy.behavior_state.split_child_health_multiplier.max(0.1);
            child.max_health = (child.max_health * health_multiplier).max(1.0);
            child.health = child.max_health;
            child.radius = (child.radius
                * enemy.behavior_state.split_child_radius_multiplier.max(0.25))
            .max(4.0);
            child.xp_value *= health_multiplier;
            child.threat *= health_multiplier;
            events.push(GameEvent::EnemySpawned {
                entity_id: child.entity_id,
                enemy_id: child.enemy_id.clone(),
            });
            self.enemies.push(child);
        }
    }

    fn resolve_contact_damage(
        &mut self,
        dt: f32,
        events: &mut Vec<GameEvent>,
        reward_hint: &mut RewardHint,
    ) {
        let mut total_contact_dps: f32 = 0.0;
        let mut slow_effects = Vec::new();
        for enemy in &self.enemies {
            if self.player.position.distance(enemy.position) > PLAYER_RADIUS + enemy.radius {
                continue;
            }
            total_contact_dps += enemy.contact_damage_per_second;
            if enemy.behavior_state.contact_slow_duration_seconds > 0.0 {
                slow_effects.push((
                    enemy.behavior_state.contact_slow_multiplier,
                    enemy.behavior_state.contact_slow_duration_seconds,
                ));
            }
        }
        let total_contact_dps = total_contact_dps.min(CONTACT_DAMAGE_CAP_PER_SECOND);

        for (multiplier, duration_seconds) in slow_effects {
            self.apply_player_slow(multiplier, duration_seconds);
        }

        if total_contact_dps <= 0.0 {
            return;
        }

        self.apply_player_damage(total_contact_dps, dt, "contact", events, reward_hint);
    }

    fn apply_player_damage(
        &mut self,
        damage_per_second: f32,
        dt: f32,
        source: &str,
        events: &mut Vec<GameEvent>,
        reward_hint: &mut RewardHint,
    ) {
        if damage_per_second <= 0.0 {
            return;
        }

        let damage_reduction = self.current_damage_reduction().clamp(0.0, 0.8);
        let damage = damage_per_second * dt * (1.0 - damage_reduction);
        if damage <= 0.0 {
            return;
        }

        self.player.health = (self.player.health - damage).max(0.0);
        self.metrics.damage_taken += damage;
        *self
            .metrics
            .damage_taken_by_source
            .entry(source.to_string())
            .or_insert(0.0) += damage;
        reward_hint.damage_taken_delta += damage;
        events.push(GameEvent::PlayerDamaged { amount: damage });
        if self.character_trait_id.as_deref() == Some("cream-guard") {
            self.cream_guard_damage_reduction_seconds = self
                .cream_guard_damage_reduction_seconds
                .max(CREAM_GUARD_DAMAGE_REDUCTION_SECONDS);
        }
    }

    fn apply_player_slow(&mut self, multiplier: f32, duration_seconds: f32) {
        let multiplier = multiplier.clamp(0.2, 1.0);
        if multiplier >= 1.0 || duration_seconds <= 0.0 {
            return;
        }

        if let Some(effect) = self
            .player_slow_effects
            .iter_mut()
            .find(|effect| (effect.multiplier - multiplier).abs() <= 0.001)
        {
            effect.remaining_seconds = effect.remaining_seconds.max(duration_seconds);
        } else {
            self.player_slow_effects.push(ActiveSlowEffect {
                multiplier,
                remaining_seconds: duration_seconds,
            });
        }
    }

    fn update_character_trait_effects(&mut self, movement: Vec2, dt: f32) {
        self.bubble_runner_pickup_boost_seconds =
            (self.bubble_runner_pickup_boost_seconds - dt).max(0.0);
        self.cream_guard_damage_reduction_seconds =
            (self.cream_guard_damage_reduction_seconds - dt).max(0.0);

        if self.character_trait_id.as_deref() == Some("bubble-runner")
            && movement.length_squared() > 0.05 * 0.05
        {
            self.bubble_runner_pickup_boost_seconds = self
                .bubble_runner_pickup_boost_seconds
                .max(BUBBLE_RUNNER_PICKUP_BOOST_SECONDS);
        }
    }

    fn character_pickup_radius_multiplier(&self) -> f32 {
        if self.character_trait_id.as_deref() == Some("bubble-runner")
            && self.bubble_runner_pickup_boost_seconds > 0.0
        {
            BUBBLE_RUNNER_PICKUP_MULTIPLIER
        } else {
            1.0
        }
    }

    fn current_damage_reduction(&self) -> f32 {
        let trait_bonus = if self.character_trait_id.as_deref() == Some("cream-guard")
            && self.cream_guard_damage_reduction_seconds > 0.0
        {
            CREAM_GUARD_DAMAGE_REDUCTION_BONUS
        } else {
            0.0
        };
        self.player.damage_reduction + trait_bonus
    }

    fn apply_level_up_character_trait_bonus(
        &mut self,
        events: &mut Vec<GameEvent>,
        reward_hint: &mut RewardHint,
    ) {
        if self.character_trait_id.as_deref() != Some("sweet-starter") || self.player.level % 5 != 0
        {
            return;
        }

        let bonus = (8.0 + self.player.level as f32 * 2.0).floor();
        self.player.xp += bonus;
        self.metrics.xp_collected += bonus;
        reward_hint.xp_delta += bonus;
        events.push(GameEvent::XpCollected {
            entity_id: 0,
            value: bonus,
        });
    }

    fn collect_pickups(&mut self, events: &mut Vec<GameEvent>, reward_hint: &mut RewardHint) {
        let mut collected = Vec::new();
        let pickup_radius = self.player.pickup_radius
            * self.character_pickup_radius_multiplier()
            * self
                .active_event_multiplier("pickup_radius_multiplier")
                .max(0.1);
        self.pickups.retain(|pickup| {
            let should_collect =
                self.player.position.distance(pickup.position) <= pickup_radius + pickup.radius;
            if should_collect {
                collected.push(pickup.clone());
                false
            } else {
                true
            }
        });

        for pickup in collected {
            match pickup.pickup_type {
                PickupType::Xp => {
                    let value = pickup.value
                        * self.player.xp_multiplier
                        * self.active_event_multiplier("xp_multiplier");
                    self.player.xp += value;
                    self.metrics.xp_collected += value;
                    reward_hint.xp_delta += value;
                    events.push(GameEvent::XpCollected {
                        entity_id: pickup.entity_id,
                        value,
                    });
                }
            }
        }
    }

    fn process_level_ups(&mut self, events: &mut Vec<GameEvent>, reward_hint: &mut RewardHint) {
        if !self.pending_upgrade_options.is_empty() {
            return;
        }

        let required = xp_required(self.player.level);
        if self.player.xp < required {
            return;
        }

        self.player.xp -= required;
        self.player.level += 1;
        reward_hint.level_delta += 1;
        events.push(GameEvent::LevelUp {
            level: self.player.level,
        });
        self.apply_level_up_character_trait_bonus(events, reward_hint);

        self.pending_upgrade_options = self.generate_upgrade_options();
        events.push(GameEvent::UpgradeOffered {
            options: self
                .pending_upgrade_options
                .iter()
                .map(|option| option.snapshot.id.clone())
                .collect(),
        });
    }

    fn record_metrics(&mut self) {
        self.metrics.duration_seconds = self.time_seconds;
        self.metrics.level = self.player.level;
        self.metrics.max_enemy_count = self.metrics.max_enemy_count.max(self.enemies.len());
        self.metrics.max_projectile_count = self
            .metrics
            .max_projectile_count
            .max(self.projectiles.len());
    }

    fn check_terminal_state(&mut self, events: &mut Vec<GameEvent>) {
        if self.player.health <= 0.0 {
            self.end_run(
                TerminalKind::Defeat,
                "player_health_depleted".to_string(),
                events,
            );
            return;
        }

        if self.time_seconds >= self.config.duration_seconds {
            self.end_run(
                TerminalKind::Victory,
                "duration_reached".to_string(),
                events,
            );
        }
    }

    fn end_run(&mut self, kind: TerminalKind, reason: String, events: &mut Vec<GameEvent>) {
        if self.terminal.is_some() {
            return;
        }

        let terminal = TerminalState {
            kind,
            time_seconds: self.time_seconds,
            reason,
            final_level: self.player.level,
            kills: self.metrics.kills,
        };
        self.metrics.terminal = Some(terminal.clone());
        self.terminal = Some(terminal.clone());
        events.push(GameEvent::RunEnded { terminal });
    }

    fn apply_upgrade_choice(
        &mut self,
        choice: usize,
        events: &mut Vec<GameEvent>,
        reward_hint: &mut RewardHint,
    ) {
        if choice >= self.pending_upgrade_options.len() {
            return;
        }

        let option = self.pending_upgrade_options.remove(choice);
        match option.effect {
            UpgradeEffect::WeaponLevel { weapon_id } => {
                if let Some(weapon) = self
                    .weapons
                    .iter_mut()
                    .find(|weapon| weapon.id == weapon_id)
                {
                    weapon.level = (weapon.level + 1).min(weapon.max_level);
                    weapon.damage += weapon.damage_per_level;
                    weapon.cooldown *= weapon.cooldown_multiplier_per_level;
                    weapon.range += weapon.range_per_level;
                    weapon.radius += weapon.area_per_level;
                }
            }
            UpgradeEffect::NewWeapon { weapon_id } => {
                if let Some(definition) = self.content.weapons.get(&weapon_id) {
                    self.weapons.push(WeaponState::from_definition(definition));
                }
            }
            UpgradeEffect::Evolution { evolution_id } => {
                if let Some(evolution) = self.content.evolutions.get(&evolution_id).cloned() {
                    if let Some(weapon) = self
                        .weapons
                        .iter_mut()
                        .find(|weapon| weapon.id == evolution.replaces_weapon)
                    {
                        *weapon = WeaponState::from_evolution_definition(&evolution);
                    } else {
                        self.weapons
                            .push(WeaponState::from_evolution_definition(&evolution));
                    }
                    if evolution.requirements.trigger == "boss_chest" {
                        self.boss_chests_available = self.boss_chests_available.saturating_sub(1);
                    }
                    self.evolutions.push(EvolutionState {
                        id: evolution.id.clone(),
                        level: 1,
                    });
                }
            }
            UpgradeEffect::Passive { passive_id } => {
                self.apply_passive(&passive_id);
            }
        }
        self.metrics
            .upgrade_choices
            .push(option.snapshot.id.clone());
        events.push(GameEvent::UpgradeChosen {
            option_id: option.snapshot.id,
        });
        reward_hint.level_delta += 0;
        self.pending_upgrade_options.clear();
    }

    fn generate_upgrade_options(&mut self) -> Vec<UpgradeOffer> {
        let evolution_candidates = self.generate_evolution_options();
        if !evolution_candidates.is_empty() {
            return evolution_candidates.into_iter().take(3).collect();
        }

        let mut weapon_level_candidates = Vec::new();

        for weapon in self
            .weapons
            .iter()
            .filter(|weapon| weapon.level < weapon.max_level)
        {
            let next_level = weapon.level + 1;
            let weapon_name = self
                .content
                .weapons
                .get(&weapon.id)
                .map(|definition| definition.name.clone())
                .unwrap_or_else(|| weapon.id.clone());
            weapon_level_candidates.push(UpgradeOffer {
                snapshot: UpgradeOptionSnapshot {
                    id: format!("{}-level-{next_level}", weapon.id),
                    name: format!("{weapon_name}强化"),
                    tags: weapon.tags.clone(),
                    description: "提升伤害、射程和冷却节奏。".to_string(),
                },
                effect: UpgradeEffect::WeaponLevel {
                    weapon_id: weapon.id.clone(),
                },
            });
        }

        let mut new_weapon_candidates = Vec::new();
        for weapon in self.content.weapons.values() {
            if self.weapons.iter().any(|state| state.id == weapon.id) {
                continue;
            }
            if !is_default_unlock(&weapon.unlock.unlock_type) {
                continue;
            }
            new_weapon_candidates.push(UpgradeOffer {
                snapshot: UpgradeOptionSnapshot {
                    id: weapon.id.clone(),
                    name: format!("获得{}", weapon.name),
                    tags: weapon.tags.clone(),
                    description: weapon.description.clone(),
                },
                effect: UpgradeEffect::NewWeapon {
                    weapon_id: weapon.id.clone(),
                },
            });
        }

        let mut passive_candidates = Vec::new();
        for passive in self.content.passives.values() {
            if !is_default_unlock(&passive.unlock.unlock_type) {
                continue;
            }
            if self
                .passives
                .iter()
                .any(|state| state.id == passive.id && state.level >= state.max_level)
            {
                continue;
            }
            passive_candidates.push(UpgradeOffer {
                snapshot: UpgradeOptionSnapshot {
                    id: passive.id.clone(),
                    name: passive.name.clone(),
                    tags: passive.tags.clone(),
                    description: passive.description.clone(),
                },
                effect: UpgradeEffect::Passive {
                    passive_id: passive.id.clone(),
                },
            });
        }

        let mut candidates = Vec::new();
        push_rotated_candidate(&mut weapon_level_candidates, &mut candidates, &mut self.rng);
        push_rotated_candidate(&mut new_weapon_candidates, &mut candidates, &mut self.rng);
        push_rotated_candidate(&mut passive_candidates, &mut candidates, &mut self.rng);

        if candidates.len() < 3 {
            let mut remaining = weapon_level_candidates;
            remaining.extend(new_weapon_candidates);
            remaining.extend(passive_candidates);
            let offset = self.rng.range_usize(remaining.len());
            remaining.rotate_left(offset);
            candidates.extend(remaining.into_iter().take(3 - candidates.len()));
        }

        if candidates.is_empty() {
            return Vec::new();
        }
        candidates.into_iter().take(3).collect()
    }

    fn generate_evolution_options(&self) -> Vec<UpgradeOffer> {
        self.content
            .evolutions
            .values()
            .filter(|evolution| self.can_offer_evolution(evolution))
            .map(|evolution| UpgradeOffer {
                snapshot: UpgradeOptionSnapshot {
                    id: evolution.id.clone(),
                    name: evolution.name.clone(),
                    tags: evolution.tags.clone(),
                    description: evolution.description.clone(),
                },
                effect: UpgradeEffect::Evolution {
                    evolution_id: evolution.id.clone(),
                },
            })
            .collect()
    }

    fn can_offer_evolution(&self, evolution: &EvolutionDefinition) -> bool {
        if self.evolutions.iter().any(|state| state.id == evolution.id) {
            return false;
        }
        let weapon_ready = self.weapons.iter().any(|weapon| {
            weapon.id == evolution.requirements.weapon.id
                && weapon.level >= evolution.requirements.weapon.min_level
        });
        if !weapon_ready {
            return false;
        }
        let passive_ready = match evolution.requirements.passive.as_ref() {
            Some(requirement) => self.passives.iter().any(|passive| {
                passive.id == requirement.id && passive.level >= requirement.min_level
            }),
            None => true,
        };
        if !passive_ready {
            return false;
        }
        match evolution.requirements.trigger.as_str() {
            "boss_chest" => self.boss_chests_available > 0,
            _ => true,
        }
    }

    fn apply_passive(&mut self, id: &str) {
        let Some(definition) = self.content.passives.get(id).cloned() else {
            return;
        };
        apply_passive_definition(&mut self.player, &mut self.passives, id, &definition);
    }

    fn find_weapon_target_position(&mut self, mode: &str, range: f32) -> Option<Vec2> {
        match mode {
            "boss_priority" => self
                .enemies
                .iter()
                .filter(|enemy| {
                    enemy.is_boss && enemy.position.distance(self.player.position) <= range
                })
                .min_by(|left, right| {
                    let left_distance = left.position.distance(self.player.position);
                    let right_distance = right.position.distance(self.player.position);
                    left_distance
                        .partial_cmp(&right_distance)
                        .unwrap_or(Ordering::Equal)
                })
                .map(|enemy| enemy.position)
                .or_else(|| self.find_nearest_enemy_position(range)),
            "highest_health_enemy" => self
                .enemies
                .iter()
                .filter(|enemy| enemy.position.distance(self.player.position) <= range)
                .max_by(|left, right| {
                    left.health
                        .partial_cmp(&right.health)
                        .unwrap_or(Ordering::Equal)
                })
                .map(|enemy| enemy.position),
            "random_enemy" => {
                let targets = self
                    .enemies
                    .iter()
                    .filter(|enemy| enemy.position.distance(self.player.position) <= range)
                    .map(|enemy| enemy.position)
                    .collect::<Vec<_>>();
                targets
                    .get(self.rng.range_usize(targets.len()))
                    .copied()
                    .or_else(|| self.find_nearest_enemy_position(range))
            }
            "random_direction" => {
                let angle = self.rng.range_f32(0.0, std::f32::consts::TAU);
                Some(self.player.position + Vec2::new(angle.cos(), angle.sin()) * range.max(1.0))
            }
            "movement_direction" => {
                let direction = self.player.velocity.normalized_or_zero();
                let direction = if direction.length_squared() > 0.0 {
                    direction
                } else {
                    Vec2::new(1.0, 0.0)
                };
                Some(self.player.position + direction * range.max(1.0))
            }
            "ground_near_player" | "self_centered" => {
                let angle = self.rng.range_f32(0.0, std::f32::consts::TAU);
                let distance = self.rng.range_f32(range * 0.25, range.max(1.0));
                Some(self.player.position + Vec2::new(angle.cos(), angle.sin()) * distance)
            }
            _ => self.find_nearest_enemy_position(range),
        }
    }

    fn find_nearest_enemy_position(&self, range: f32) -> Option<Vec2> {
        self.enemies
            .iter()
            .filter_map(|enemy| {
                let distance = enemy.position.distance(self.player.position);
                (distance <= range).then_some((distance, enemy.position))
            })
            .min_by(|left, right| left.0.partial_cmp(&right.0).unwrap_or(Ordering::Equal))
            .map(|(_, position)| position)
    }

    fn spawn_position_around_player(&mut self, min_distance: f32, max_distance: f32) -> Vec2 {
        let angle = self.rng.range_f32(0.0, std::f32::consts::TAU);
        let distance = self.rng.range_f32(min_distance, max_distance);
        let offset = Vec2::new(angle.cos(), angle.sin()) * distance;
        self.clamp_to_map(self.player.position + offset)
    }

    fn random_position_near(&mut self, origin: Vec2, min_distance: f32, max_distance: f32) -> Vec2 {
        let angle = self.rng.range_f32(0.0, std::f32::consts::TAU);
        let distance = self
            .rng
            .range_f32(min_distance, max_distance.max(min_distance));
        let offset = Vec2::new(angle.cos(), angle.sin()) * distance;
        self.clamp_to_map(origin + offset)
    }

    fn clamp_to_map(&self, position: Vec2) -> Vec2 {
        let mut position = position;
        position.x = position
            .x
            .clamp(-self.map.width * 0.5, self.map.width * 0.5);
        position.y = position
            .y
            .clamp(-self.map.height * 0.5, self.map.height * 0.5);
        position
    }

    fn allocate_entity_id(&mut self) -> u64 {
        let id = self.next_entity_id;
        self.next_entity_id += 1;
        id
    }

    fn build_snapshot(&self) -> BuildSnapshot {
        let mut tags = Vec::new();
        for weapon in &self.weapons {
            for tag in &weapon.tags {
                if !tags.contains(tag) {
                    tags.push(tag.clone());
                }
            }
        }
        for passive in &self.passives {
            if let Some(definition) = self.content.passives.get(&passive.id) {
                for tag in &definition.tags {
                    if !tags.contains(tag) {
                        tags.push(tag.clone());
                    }
                }
            }
        }

        BuildSnapshot {
            weapons: self
                .weapons
                .iter()
                .map(|weapon| BuildItemSnapshot {
                    id: weapon.id.clone(),
                    level: weapon.level,
                })
                .collect(),
            passives: self
                .passives
                .iter()
                .map(|passive| BuildItemSnapshot {
                    id: passive.id.clone(),
                    level: passive.level,
                })
                .collect(),
            evolutions: self
                .evolutions
                .iter()
                .map(|evolution| BuildItemSnapshot {
                    id: evolution.id.clone(),
                    level: evolution.level,
                })
                .collect(),
            tags,
            open_evolution_paths: self.open_evolution_paths(),
        }
    }

    fn open_evolution_paths(&self) -> Vec<String> {
        self.content
            .evolutions
            .values()
            .filter(|evolution| {
                if self.evolutions.iter().any(|state| state.id == evolution.id) {
                    return false;
                }
                let weapon_seen = self
                    .weapons
                    .iter()
                    .any(|weapon| weapon.id == evolution.requirements.weapon.id);
                let passive_seen =
                    evolution
                        .requirements
                        .passive
                        .as_ref()
                        .is_some_and(|requirement| {
                            self.passives
                                .iter()
                                .any(|passive| passive.id == requirement.id)
                        });
                weapon_seen || passive_seen
            })
            .map(|evolution| evolution.id.clone())
            .collect()
    }
}

fn is_default_unlock(unlock_type: &str) -> bool {
    unlock_type == "default"
}

fn xp_required(level: u32) -> f32 {
    (12.0 + level as f32 * 8.0 + (level as f32).powf(1.35) * 5.0).floor()
}

fn weapon_lifetime(weapon_type: &str, duration: f32) -> f32 {
    if duration > 0.0 {
        return duration;
    }

    match weapon_type {
        "burst" => 0.35,
        "zone" => 2.0,
        "beam" => 0.75,
        "orbit" => 1.6,
        _ => 1.2,
    }
}

fn boomerang_return_after_seconds(weapon_tags: &[String], lifetime: f32) -> Option<f32> {
    if weapon_tags.iter().any(|tag| tag == "boomerang") && lifetime > 0.2 {
        Some(lifetime * BOOMERANG_RETURN_AFTER_LIFETIME_RATIO)
    } else {
        None
    }
}

fn enemy_knockback_distance_for_weapon(weapon_tags: &[String]) -> f32 {
    if weapon_tags.iter().any(|tag| tag == "knockback") {
        KNOCKBACK_WEAPON_DISTANCE
    } else {
        0.0
    }
}

fn push_rotated_candidate(
    source: &mut Vec<UpgradeOffer>,
    target: &mut Vec<UpgradeOffer>,
    rng: &mut RunRng,
) {
    if source.is_empty() || target.len() >= 3 {
        return;
    }

    let offset = rng.range_usize(source.len());
    source.rotate_left(offset);
    target.push(source.remove(0));
}

fn apply_passive_definition(
    player: &mut PlayerState,
    passives: &mut Vec<PassiveState>,
    id: &str,
    definition: &PassiveDefinition,
) {
    if let Some(passive) = passives.iter_mut().find(|passive| passive.id == id) {
        passive.level = (passive.level + 1).min(passive.max_level);
    } else {
        passives.push(PassiveState {
            id: id.to_string(),
            level: 1,
            max_level: definition.max_level,
        });
    }

    for modifier in &definition.stat_modifiers {
        match (modifier.stat.as_str(), modifier.mode.as_str()) {
            ("max_health", "add") => {
                player.max_health += modifier.value_per_level;
                player.health = (player.health + modifier.value_per_level).min(player.max_health);
            }
            ("move_speed", "add") => {
                player.move_speed += modifier.value_per_level;
            }
            ("pickup_radius", "add") => {
                player.pickup_radius += modifier.value_per_level;
            }
            ("damage_multiplier", "add") => {
                player.damage_multiplier += modifier.value_per_level;
            }
            ("cooldown_multiplier", "add") => {
                player.cooldown_multiplier += modifier.value_per_level;
            }
            ("cooldown_multiplier", "multiply") => {
                player.cooldown_multiplier *= modifier.value_per_level;
            }
            ("xp_multiplier", "add") => {
                player.xp_multiplier += modifier.value_per_level;
            }
            ("xp_multiplier", "multiply") => {
                player.xp_multiplier *= modifier.value_per_level;
            }
            ("regen_per_second", "add") => {
                player.regen_per_second += modifier.value_per_level;
            }
            ("regen_per_second", "multiply") => {
                player.regen_per_second *= modifier.value_per_level;
            }
            ("damage_reduction", "add") => {
                player.damage_reduction += modifier.value_per_level;
            }
            ("damage_reduction", "multiply") => {
                player.damage_reduction *= modifier.value_per_level;
            }
            ("projectile_size", "add") => {
                player.projectile_size_multiplier += modifier.value_per_level;
            }
            ("projectile_size", "multiply") => {
                player.projectile_size_multiplier *= modifier.value_per_level;
            }
            ("effect_duration", "add") => {
                player.effect_duration_multiplier += modifier.value_per_level;
            }
            ("effect_duration", "multiply") => {
                player.effect_duration_multiplier *= modifier.value_per_level;
            }
            _ => {}
        }
    }
}

#[derive(Debug, Clone)]
struct PlayerState {
    position: Vec2,
    velocity: Vec2,
    health: f32,
    max_health: f32,
    level: u32,
    xp: f32,
    move_speed: f32,
    pickup_radius: f32,
    damage_multiplier: f32,
    cooldown_multiplier: f32,
    xp_multiplier: f32,
    regen_per_second: f32,
    damage_reduction: f32,
    projectile_size_multiplier: f32,
    effect_duration_multiplier: f32,
}

impl PlayerState {
    fn from_definition(definition: &CharacterDefinition) -> Self {
        Self {
            position: Vec2::ZERO,
            velocity: Vec2::ZERO,
            health: definition.base_stats.max_health,
            max_health: definition.base_stats.max_health,
            level: 1,
            xp: 0.0,
            move_speed: definition.base_stats.move_speed,
            pickup_radius: definition.base_stats.pickup_radius,
            damage_multiplier: definition.base_stats.damage_multiplier,
            cooldown_multiplier: definition.base_stats.cooldown_multiplier,
            xp_multiplier: definition.base_stats.xp_multiplier,
            regen_per_second: definition.base_stats.regen_per_second,
            damage_reduction: 0.0,
            projectile_size_multiplier: 1.0,
            effect_duration_multiplier: 1.0,
        }
    }
}

#[derive(Debug, Clone)]
struct WeaponState {
    id: String,
    weapon_type: String,
    level: u32,
    max_level: u32,
    damage: f32,
    cooldown: f32,
    cooldown_remaining: f32,
    projectile_speed: f32,
    range: f32,
    targeting_mode: String,
    radius: f32,
    pierce: u32,
    duration: f32,
    tags: Vec<String>,
    projectile_count_base: u32,
    projectile_count_bonus_levels: Vec<u32>,
    damage_per_level: f32,
    cooldown_multiplier_per_level: f32,
    range_per_level: f32,
    area_per_level: f32,
}

impl WeaponState {
    fn from_definition(definition: &WeaponDefinition) -> Self {
        Self {
            id: definition.id.clone(),
            weapon_type: definition.weapon_type.clone(),
            level: 1,
            max_level: definition.scaling.max_level,
            damage: definition.base_stats.damage,
            cooldown: definition.base_stats.cooldown_ms / 1000.0,
            cooldown_remaining: 0.2,
            projectile_speed: definition.base_stats.projectile_speed,
            range: definition.targeting.range,
            targeting_mode: definition.targeting.mode.clone(),
            radius: definition.base_stats.area_radius,
            pierce: definition.base_stats.pierce,
            duration: definition.base_stats.duration_ms / 1000.0,
            tags: definition.tags.clone(),
            projectile_count_base: definition.base_stats.projectile_count,
            projectile_count_bonus_levels: definition.scaling.projectile_count_bonus_levels.clone(),
            damage_per_level: definition.scaling.damage_per_level,
            cooldown_multiplier_per_level: definition.scaling.cooldown_multiplier_per_level,
            range_per_level: definition.scaling.range_per_level,
            area_per_level: definition.scaling.area_per_level,
        }
    }

    fn from_evolution_definition(definition: &EvolutionDefinition) -> Self {
        let base_stats = &definition.weapon_definition.base_stats;
        Self {
            id: definition.id.clone(),
            weapon_type: definition.weapon_definition.weapon_type.clone(),
            level: 1,
            max_level: 1,
            damage: base_stats.damage,
            cooldown: base_stats.cooldown_ms / 1000.0,
            cooldown_remaining: 0.2,
            projectile_speed: base_stats.projectile_speed.unwrap_or(520.0),
            range: definition.weapon_definition.targeting.range,
            targeting_mode: definition.weapon_definition.targeting.mode.clone(),
            radius: base_stats.area_radius,
            pierce: base_stats.pierce.unwrap_or(1),
            duration: base_stats.duration_ms.unwrap_or(0.0) / 1000.0,
            tags: definition.tags.clone(),
            projectile_count_base: base_stats.projectile_count,
            projectile_count_bonus_levels: Vec::new(),
            damage_per_level: 0.0,
            cooldown_multiplier_per_level: 1.0,
            range_per_level: 0.0,
            area_per_level: 0.0,
        }
    }

    fn projectile_count(&self) -> usize {
        self.projectile_count_base as usize
            + self
                .projectile_count_bonus_levels
                .iter()
                .filter(|level| self.level >= **level)
                .count()
    }
}

struct WeaponProjectileRuntimeInput<'a> {
    weapon_type: &'a str,
    target_position: Vec2,
    base_direction: Vec2,
    projectile_index: usize,
    projectile_count: usize,
    spread_start: f32,
    spread_step: f32,
    projectile_speed: f32,
    pierce: u32,
    lifetime: f32,
    radius: f32,
}

struct ProjectileRuntime {
    position: Vec2,
    velocity: Vec2,
    pierce_remaining: u32,
    lifetime: f32,
}

#[derive(Debug, Clone)]
struct PassiveState {
    id: String,
    level: u32,
    max_level: u32,
}

#[derive(Debug, Clone)]
struct EvolutionState {
    id: String,
    level: u32,
}

#[derive(Debug, Clone)]
struct ActiveEventEffect {
    event_id: String,
    effect_type: String,
    value: f32,
    remaining_seconds: f32,
}

#[derive(Debug, Clone, Copy)]
struct PlayerPositionSample {
    time_seconds: f32,
    position: Vec2,
}

#[derive(Debug, Clone, Copy)]
struct ActiveRouteEchoHazard {
    remaining_seconds: f32,
    next_spawn_seconds: f32,
    spawn_count: u32,
    sample_interval_seconds: f32,
    history_seconds: f32,
    trigger_radius: f32,
    hazard_duration_seconds: f32,
    radius: f32,
    slow_multiplier: f32,
    damage_per_second: f32,
}

impl ActiveRouteEchoHazard {
    fn from_effect(effect: &content::EventEffectDefinition) -> Self {
        Self {
            remaining_seconds: effect.duration_seconds.unwrap_or(8.0).max(0.1),
            next_spawn_seconds: 0.0,
            spawn_count: effect.value.round().clamp(1.0, 4.0) as u32,
            sample_interval_seconds: effect.sample_interval_seconds.unwrap_or(2.0).max(0.1),
            history_seconds: effect.history_seconds.unwrap_or(18.0).max(0.5),
            trigger_radius: effect.trigger_radius.unwrap_or(96.0).max(1.0),
            hazard_duration_seconds: effect.hazard_duration_seconds.unwrap_or(3.0).max(0.1),
            radius: effect.radius.unwrap_or(56.0).max(4.0),
            slow_multiplier: effect.slow_multiplier.unwrap_or(0.78).clamp(0.2, 1.0),
            damage_per_second: effect.damage_per_second.unwrap_or(0.0).max(0.0),
        }
    }
}

#[derive(Debug, Clone)]
struct ActiveSlowEffect {
    multiplier: f32,
    remaining_seconds: f32,
}

#[derive(Debug, Clone)]
struct Hazard {
    position: Vec2,
    radius: f32,
    remaining_seconds: f32,
    slow_multiplier: f32,
    damage_per_second: f32,
}

impl From<&Hazard> for HazardSnapshot {
    fn from(hazard: &Hazard) -> Self {
        Self {
            position: hazard.position,
            radius: hazard.radius,
            slow_multiplier: hazard.slow_multiplier,
            damage_per_second: hazard.damage_per_second,
            remaining_seconds: hazard.remaining_seconds,
        }
    }
}

#[derive(Debug, Clone)]
enum BossAbilityAction {
    SpawnEnemy {
        enemy_id: String,
        count: u32,
        origin: Vec2,
        radius: f32,
    },
    SpawnHazard {
        count: u32,
        origin: Vec2,
        radius: f32,
        hazard_radius: f32,
        duration_seconds: f32,
        slow_multiplier: f32,
        damage_per_second: f32,
    },
}

fn boss_phase_index(definition: &BossDefinition, health_ratio: f32) -> usize {
    let ratio = health_ratio.clamp(0.0, 1.0);
    let mut phase_index = 0;
    for (index, phase) in definition.phases.iter().enumerate() {
        if ratio <= phase.hp_threshold {
            phase_index = index;
        }
    }
    phase_index
}

fn boss_phase_ability(
    definition: &BossDefinition,
    phase_index: usize,
    cursor: usize,
) -> Option<String> {
    let phase = definition.phases.get(phase_index)?;
    if phase.abilities.is_empty() {
        None
    } else {
        Some(phase.abilities[cursor % phase.abilities.len()].clone())
    }
}

fn boss_ability_cooldown_seconds(ability_id: &str) -> f32 {
    if ability_id == "summon_caramel_slime"
        || matches!(
            ability_id,
            "lay_caramel_tracks" | "slow_pulse" | "caramel_floor_cycle"
        )
        || ability_id.contains("double")
        || ability_id.contains("multi")
    {
        3.0
    } else if ability_id.contains("summon") || ability_id.contains("split") {
        4.0
    } else {
        3.5
    }
}

fn boss_ability_actions(
    ability_id: &str,
    boss_position: Vec2,
    player_position: Vec2,
) -> Vec<BossAbilityAction> {
    match ability_id {
        "dash_charge" => vec![boss_hazard(
            player_position,
            1,
            0.0,
            104.0,
            1.25,
            0.58,
            20.0,
        )],
        "sugar_splash" => vec![
            boss_summon("sour-gummy", 2, boss_position),
            boss_hazard(player_position, 3, 150.0, 84.0, 3.2, 0.62, 10.5),
        ],
        "summon_bouncy_gummy" => vec![boss_summon("bouncy-gummy", 2, boss_position)],
        "summon_soda_bubble" => vec![boss_summon("soda-bubble", 4, boss_position)],
        "summon_caramel_slime" => vec![boss_summon("caramel-slime", 4, boss_position)],
        "summon_sticky_bear_gummy" => vec![boss_summon("sticky-bear-gummy", 2, boss_position)],
        "summon_guard_wave" => vec![boss_summon("sticky-bear-gummy", 4, boss_position)],
        "split_cotton_clumps" => vec![boss_summon("cotton-candy-clump", 3, boss_position)],
        "bubble_barrage" => vec![boss_summon("soda-bubble", 4, player_position)],
        "charged_fountain" => vec![
            boss_summon("soda-bubble", 5, player_position),
            boss_hazard(player_position, 1, 0.0, 108.0, 3.2, 0.58, 17.0),
        ],
        "lay_caramel_tracks" => vec![boss_hazard(boss_position, 3, 132.0, 64.0, 4.0, 0.52, 1.0)],
        "slow_pulse" => vec![boss_hazard(
            player_position,
            2,
            120.0,
            112.0,
            2.4,
            0.52,
            8.5,
        )],
        "caramel_floor_cycle" => vec![boss_hazard(
            player_position,
            4,
            190.0,
            92.0,
            4.2,
            0.44,
            13.0,
        )],
        "jump_shockwave" => vec![boss_hazard(player_position, 1, 24.0, 120.0, 1.2, 0.70, 0.0)],
        "double_jump_shockwave" => vec![boss_hazard(
            player_position,
            2,
            140.0,
            112.0,
            1.4,
            0.68,
            0.0,
        )],
        "sour_phase_storm" => vec![
            boss_summon("sour-gummy", 2, player_position),
            boss_hazard(player_position, 2, 150.0, 84.0, 2.4, 0.70, 0.0),
        ],
        "spicy_phase_burst" => vec![
            boss_summon("spicy-gummy", 4, player_position),
            boss_hazard(player_position, 2, 120.0, 76.0, 2.4, 0.66, 4.0),
        ],
        "bubble_phase_barrage" => vec![
            boss_summon("soda-bubble", 5, player_position),
            boss_hazard(player_position, 1, 0.0, 96.0, 3.0, 0.58, 7.0),
        ],
        "multi_flavor_storm" => vec![
            boss_summon("sour-gummy", 3, player_position),
            boss_summon("spicy-gummy", 3, player_position),
            boss_summon("soda-bubble", 3, player_position),
            boss_hazard(player_position, 3, 160.0, 90.0, 3.4, 0.55, 12.0),
        ],
        _ => Vec::new(),
    }
}

fn boss_summon(enemy_id: &str, count: u32, origin: Vec2) -> BossAbilityAction {
    BossAbilityAction::SpawnEnemy {
        enemy_id: enemy_id.to_string(),
        count,
        origin,
        radius: 180.0,
    }
}

fn boss_hazard(
    origin: Vec2,
    count: u32,
    radius: f32,
    hazard_radius: f32,
    duration_seconds: f32,
    slow_multiplier: f32,
    damage_per_second: f32,
) -> BossAbilityAction {
    BossAbilityAction::SpawnHazard {
        count,
        origin,
        radius,
        hazard_radius,
        duration_seconds,
        slow_multiplier,
        damage_per_second,
    }
}

#[derive(Debug, Clone)]
struct MapRuntime {
    width: f32,
    height: f32,
    spawn_min: f32,
    spawn_max: f32,
}

impl MapRuntime {
    fn from_definition(definition: &MapDefinition) -> Self {
        Self {
            width: definition.size.width,
            height: definition.size.height,
            spawn_min: definition.spawn_rules.min_distance,
            spawn_max: definition.spawn_rules.max_distance,
        }
    }
}

#[derive(Debug, Clone)]
struct Enemy {
    entity_id: u64,
    enemy_id: String,
    position: Vec2,
    velocity: Vec2,
    health: f32,
    max_health: f32,
    move_speed: f32,
    contact_damage_per_second: f32,
    radius: f32,
    xp_value: f32,
    threat: f32,
    behavior: EnemyBehavior,
    behavior_state: EnemyBehaviorState,
    is_boss: bool,
    is_elite: bool,
    boss_phase_index: usize,
    boss_ability_cursor: usize,
    boss_ability_cooldown_remaining: f32,
    slow_multiplier: f32,
    slow_remaining_seconds: f32,
}

impl Enemy {
    fn from_enemy_definition(entity_id: u64, position: Vec2, definition: &EnemyDefinition) -> Self {
        Self::from_stats(
            entity_id,
            position,
            definition.id(),
            &definition.common.stats,
            definition.spawn_budget.threat,
            false,
            Some(&definition.behavior),
        )
    }

    fn from_boss_definition(entity_id: u64, position: Vec2, definition: &BossDefinition) -> Self {
        let mut enemy = Self::from_stats(
            entity_id,
            position,
            definition.id(),
            &definition.common.stats,
            8.0,
            true,
            None,
        );
        enemy.behavior_state = EnemyBehaviorState::for_boss(definition);
        enemy.behavior = enemy.behavior_state.behavior;
        enemy.boss_ability_cooldown_remaining = 0.0;
        enemy
    }

    fn from_stats(
        entity_id: u64,
        position: Vec2,
        id: &str,
        stats: &EnemyStatsDefinition,
        threat: f32,
        is_boss: bool,
        behavior_definition: Option<&content::BehaviorDefinition>,
    ) -> Self {
        let mut behavior_state =
            behavior_definition.map_or_else(EnemyBehaviorState::default, EnemyBehaviorState::from);
        behavior_state.orbit_direction = if entity_id % 2 == 0 { 1.0 } else { -1.0 };
        Self {
            entity_id,
            enemy_id: id.to_string(),
            position,
            velocity: Vec2::ZERO,
            health: stats.health,
            max_health: stats.health,
            move_speed: stats.move_speed,
            contact_damage_per_second: stats.contact_damage_per_second,
            radius: stats.radius,
            xp_value: stats.xp_value,
            threat,
            behavior: behavior_state.behavior,
            behavior_state,
            is_boss,
            is_elite: false,
            boss_phase_index: 0,
            boss_ability_cursor: 0,
            boss_ability_cooldown_remaining: 0.0,
            slow_multiplier: 1.0,
            slow_remaining_seconds: 0.0,
        }
    }

    fn update_slow(&mut self, dt: f32) {
        self.slow_remaining_seconds = (self.slow_remaining_seconds - dt).max(0.0);
        if self.slow_remaining_seconds <= 0.0 {
            self.slow_multiplier = 1.0;
        }
    }

    fn active_slow_multiplier(&self) -> f32 {
        if self.slow_remaining_seconds > 0.0 {
            self.slow_multiplier.clamp(0.2, 1.0)
        } else {
            1.0
        }
    }

    fn apply_slow(&mut self, multiplier: f32, duration_seconds: f32) {
        if multiplier >= 1.0 || duration_seconds <= 0.0 {
            return;
        }
        self.slow_multiplier = self.slow_multiplier.min(multiplier.clamp(0.2, 1.0));
        self.slow_remaining_seconds = self.slow_remaining_seconds.max(duration_seconds);
    }

    fn apply_knockback(
        &mut self,
        player_position: Vec2,
        distance: f32,
        half_width: f32,
        half_height: f32,
    ) {
        if distance <= 0.0 {
            return;
        }
        let direction = (self.position - player_position).normalized_or_zero();
        if direction.length_squared() <= 0.0 {
            return;
        }
        self.position += direction * distance;
        self.position.x = self.position.x.clamp(-half_width, half_width);
        self.position.y = self.position.y.clamp(-half_height, half_height);
    }

    fn dash_velocity(&mut self, direction: Vec2, dt: f32) -> Vec2 {
        if self.behavior_state.dash_remaining_seconds > 0.0 {
            self.behavior_state.dash_remaining_seconds -= dt;
            return self.behavior_state.dash_direction
                * self.move_speed
                * self.behavior_state.dash_speed_multiplier;
        }

        if self.behavior_state.dash_charge_remaining_seconds > 0.0 {
            self.behavior_state.dash_charge_remaining_seconds -= dt;
            if self.behavior_state.dash_charge_remaining_seconds <= 0.0 {
                self.behavior_state.dash_direction = direction;
                self.behavior_state.dash_remaining_seconds =
                    self.behavior_state.dash_duration_seconds;
            }
            return Vec2::ZERO;
        }

        self.behavior_state.dash_cooldown_remaining_seconds -= dt;
        if self.behavior_state.dash_cooldown_remaining_seconds <= 0.0 {
            self.behavior_state.dash_charge_remaining_seconds =
                self.behavior_state.dash_charge_seconds;
            self.behavior_state.dash_cooldown_remaining_seconds =
                self.behavior_state.dash_cooldown_seconds;
        }

        direction * self.move_speed
    }

    fn orbit_velocity(&self, player_position: Vec2, chase_direction: Vec2) -> Vec2 {
        let from_player = self.position - player_position;
        let distance = from_player.length();
        if distance <= f32::EPSILON {
            return chase_direction * self.move_speed;
        }

        let radial = from_player / distance;
        let tangent = Vec2::new(-radial.y, radial.x) * self.behavior_state.orbit_direction.signum();
        let radius = self.behavior_state.orbit_radius.max(24.0);
        if distance > radius * 1.8 {
            return chase_direction * self.move_speed;
        }

        let distance_error = ((distance - radius) / radius).clamp(-1.0, 1.0);
        let radial_velocity = radial
            * (-distance_error * self.move_speed * self.behavior_state.orbit_approach_weight);
        let tangent_velocity =
            tangent * self.move_speed * self.behavior_state.orbit_speed_multiplier;
        (radial_velocity + tangent_velocity)
            .clamp_length_max(self.move_speed * self.behavior_state.orbit_speed_multiplier.max(1.0))
    }

    fn ranged_spit_velocity_and_hazards(
        &mut self,
        player_position: Vec2,
        chase_direction: Vec2,
        dt: f32,
    ) -> (Vec2, Vec<Hazard>) {
        let distance = self.position.distance(player_position);
        if distance > self.behavior_state.ranged_range {
            return (chase_direction * self.move_speed, Vec::new());
        }

        let velocity = if distance < self.behavior_state.ranged_range * 0.35 {
            chase_direction * -self.move_speed * 0.45
        } else {
            Vec2::ZERO
        };

        if self.behavior_state.ranged_windup_remaining_seconds > 0.0 {
            self.behavior_state.ranged_windup_remaining_seconds -= dt;
            if self.behavior_state.ranged_windup_remaining_seconds <= 0.0 {
                return (velocity, self.ranged_spit_hazards(player_position));
            }
            return (velocity, Vec::new());
        }

        self.behavior_state.ranged_cooldown_remaining_seconds -= dt;
        if self.behavior_state.ranged_cooldown_remaining_seconds <= 0.0 {
            self.behavior_state.ranged_cooldown_remaining_seconds =
                self.behavior_state.ranged_cooldown_seconds;
            if self.behavior_state.ranged_windup_seconds <= f32::EPSILON {
                return (velocity, self.ranged_spit_hazards(player_position));
            }
            self.behavior_state.ranged_windup_remaining_seconds =
                self.behavior_state.ranged_windup_seconds;
        }

        (velocity, Vec::new())
    }

    fn ranged_spit_hazards(&self, player_position: Vec2) -> Vec<Hazard> {
        let count = self.behavior_state.ranged_projectile_count.clamp(1, 8);
        let damage_per_second = if self.behavior_state.ranged_projectile_damage_per_second > 0.0 {
            self.behavior_state.ranged_projectile_damage_per_second
        } else {
            (self.contact_damage_per_second * 1.5).max(2.0)
        };

        (0..count)
            .map(|index| {
                let offset = if count == 1 {
                    Vec2::ZERO
                } else {
                    let angle = std::f32::consts::TAU * index as f32 / count as f32
                        + self.entity_id as f32 * 0.37;
                    Vec2::new(angle.cos(), angle.sin())
                        * self.behavior_state.ranged_projectile_spread_radius
                };
                Hazard {
                    position: player_position + offset,
                    radius: self.behavior_state.ranged_projectile_radius,
                    remaining_seconds: self.behavior_state.ranged_projectile_duration_seconds,
                    slow_multiplier: 1.0,
                    damage_per_second,
                }
            })
            .collect()
    }

    fn projectile_damage_multiplier(
        &self,
        projectile_position: Vec2,
        player_position: Vec2,
    ) -> f32 {
        if self.behavior != EnemyBehavior::Shielded {
            return 1.0;
        }

        let front_direction = (player_position - self.position).normalized_or_zero();
        let hit_direction = (projectile_position - self.position).normalized_or_zero();
        if front_direction == Vec2::ZERO || hit_direction == Vec2::ZERO {
            return self.behavior_state.shield_front_damage_multiplier;
        }
        if hit_direction.x * front_direction.x + hit_direction.y * front_direction.y >= 0.0 {
            self.behavior_state.shield_front_damage_multiplier
        } else {
            self.behavior_state.shield_rear_damage_multiplier
        }
    }
}

#[derive(Debug, Clone)]
struct EnemyBehaviorState {
    behavior: EnemyBehavior,
    dash_charge_seconds: f32,
    dash_charge_remaining_seconds: f32,
    dash_duration_seconds: f32,
    dash_remaining_seconds: f32,
    dash_cooldown_seconds: f32,
    dash_cooldown_remaining_seconds: f32,
    dash_speed_multiplier: f32,
    dash_direction: Vec2,
    split_child_enemy_id: Option<String>,
    split_child_count: u32,
    split_child_health_multiplier: f32,
    split_child_radius_multiplier: f32,
    hazard_interval_seconds: f32,
    hazard_cooldown_remaining: f32,
    hazard_radius: f32,
    hazard_duration_seconds: f32,
    hazard_slow_multiplier: f32,
    contact_slow_multiplier: f32,
    contact_slow_duration_seconds: f32,
    orbit_radius: f32,
    orbit_speed_multiplier: f32,
    orbit_approach_weight: f32,
    orbit_direction: f32,
    ranged_range: f32,
    ranged_windup_seconds: f32,
    ranged_windup_remaining_seconds: f32,
    ranged_cooldown_seconds: f32,
    ranged_cooldown_remaining_seconds: f32,
    ranged_projectile_count: u32,
    ranged_projectile_radius: f32,
    ranged_projectile_duration_seconds: f32,
    ranged_projectile_damage_per_second: f32,
    ranged_projectile_spread_radius: f32,
    shield_front_damage_multiplier: f32,
    shield_rear_damage_multiplier: f32,
}

impl Default for EnemyBehaviorState {
    fn default() -> Self {
        Self {
            behavior: EnemyBehavior::Chase,
            dash_charge_seconds: 0.6,
            dash_charge_remaining_seconds: 0.0,
            dash_duration_seconds: 0.25,
            dash_remaining_seconds: 0.0,
            dash_cooldown_seconds: 2.0,
            dash_cooldown_remaining_seconds: 2.0,
            dash_speed_multiplier: 2.0,
            dash_direction: Vec2::ZERO,
            split_child_enemy_id: None,
            split_child_count: 0,
            split_child_health_multiplier: 0.5,
            split_child_radius_multiplier: 0.75,
            hazard_interval_seconds: 0.8,
            hazard_cooldown_remaining: 0.0,
            hazard_radius: 40.0,
            hazard_duration_seconds: 2.0,
            hazard_slow_multiplier: 0.8,
            contact_slow_multiplier: 1.0,
            contact_slow_duration_seconds: 0.0,
            orbit_radius: 160.0,
            orbit_speed_multiplier: 1.0,
            orbit_approach_weight: 0.5,
            orbit_direction: 1.0,
            ranged_range: 260.0,
            ranged_windup_seconds: 0.55,
            ranged_windup_remaining_seconds: 0.0,
            ranged_cooldown_seconds: 2.8,
            ranged_cooldown_remaining_seconds: 2.8,
            ranged_projectile_count: 1,
            ranged_projectile_radius: 22.0,
            ranged_projectile_duration_seconds: 0.9,
            ranged_projectile_damage_per_second: 0.0,
            ranged_projectile_spread_radius: 42.0,
            shield_front_damage_multiplier: 0.7,
            shield_rear_damage_multiplier: 1.2,
        }
    }
}

impl EnemyBehaviorState {
    fn for_boss(definition: &BossDefinition) -> Self {
        let mut state = Self::default();
        let abilities = definition
            .phases
            .iter()
            .flat_map(|phase| phase.abilities.iter())
            .collect::<Vec<_>>();

        if abilities.iter().any(|ability| {
            ability.contains("dash") || ability.contains("jump") || ability.as_str() == "soft_roll"
        }) {
            state.behavior = EnemyBehavior::Dash;
            state.dash_charge_seconds = 0.75;
            state.dash_duration_seconds = 0.35;
            state.dash_cooldown_seconds = 3.2;
            state.dash_cooldown_remaining_seconds = state.dash_cooldown_seconds;
            state.dash_speed_multiplier = 2.4;
        }

        state
    }
}

impl From<&content::BehaviorDefinition> for EnemyBehaviorState {
    fn from(definition: &content::BehaviorDefinition) -> Self {
        let parameters = &definition.parameters;
        let mut state = Self {
            behavior: EnemyBehavior::from_type(&definition.behavior_type),
            ..Self::default()
        };
        state.dash_charge_seconds = behavior_parameter_f32(parameters, "charge_seconds", 0.6);
        state.dash_duration_seconds = behavior_parameter_f32(
            parameters,
            "dash_seconds",
            behavior_parameter_f32(parameters, "jump_duration_seconds", 0.25),
        );
        state.dash_cooldown_seconds = behavior_parameter_f32(parameters, "cooldown_seconds", 2.0);
        state.dash_cooldown_remaining_seconds = state.dash_cooldown_seconds;
        state.dash_speed_multiplier = behavior_parameter_f32(
            parameters,
            "dash_speed_multiplier",
            behavior_parameter_f32(parameters, "jump_speed_multiplier", 2.0),
        )
        .max(1.0);
        state.split_child_enemy_id = parameters
            .get("child_enemy_id")
            .and_then(|value| value.as_str())
            .map(str::to_string);
        state.split_child_count = behavior_parameter_u32(parameters, "child_count", 0);
        state.split_child_health_multiplier =
            behavior_parameter_f32(parameters, "child_health_multiplier", 0.5);
        state.split_child_radius_multiplier =
            behavior_parameter_f32(parameters, "child_radius_multiplier", 0.75);
        state.hazard_radius = behavior_parameter_f32(parameters, "hazard_radius", 40.0);
        state.hazard_duration_seconds =
            behavior_parameter_f32(parameters, "hazard_duration_seconds", 2.0);
        state.hazard_slow_multiplier = behavior_parameter_f32(parameters, "slow_multiplier", 0.8);
        state.hazard_interval_seconds =
            behavior_parameter_f32(parameters, "hazard_interval_seconds", 0.8).max(0.1);
        state.contact_slow_multiplier = nested_behavior_parameter_f32(
            parameters,
            "on_contact_status_effect",
            "multiplier",
            1.0,
        );
        state.contact_slow_duration_seconds = nested_behavior_parameter_f32(
            parameters,
            "on_contact_status_effect",
            "duration_seconds",
            0.0,
        );
        state.orbit_radius = behavior_parameter_f32(parameters, "orbit_radius", 160.0).max(24.0);
        state.orbit_speed_multiplier =
            behavior_parameter_f32(parameters, "orbit_speed", 1.0).clamp(0.1, 3.0);
        state.orbit_approach_weight =
            behavior_parameter_f32(parameters, "approach_weight", 0.5).clamp(0.0, 2.0);
        state.ranged_range = behavior_parameter_f32(parameters, "range", 260.0).max(32.0);
        state.ranged_windup_seconds =
            behavior_parameter_f32(parameters, "windup_seconds", 0.55).max(0.0);
        state.ranged_cooldown_seconds =
            behavior_parameter_f32(parameters, "cooldown_seconds", 2.8).max(0.1);
        state.ranged_cooldown_remaining_seconds = state.ranged_cooldown_seconds;
        state.ranged_projectile_count =
            behavior_parameter_u32(parameters, "projectile_count", 1).clamp(1, 8);
        state.ranged_projectile_radius =
            behavior_parameter_f32(parameters, "projectile_radius", 22.0).max(4.0);
        state.ranged_projectile_duration_seconds =
            behavior_parameter_f32(parameters, "projectile_duration_seconds", 0.9).max(0.1);
        state.ranged_projectile_damage_per_second =
            behavior_parameter_f32(parameters, "damage_per_second", 0.0).max(0.0);
        state.ranged_projectile_spread_radius =
            behavior_parameter_f32(parameters, "projectile_spread_radius", 42.0).max(0.0);
        state.shield_front_damage_multiplier =
            behavior_parameter_f32(parameters, "front_damage_multiplier", 0.7).clamp(0.05, 2.0);
        state.shield_rear_damage_multiplier =
            behavior_parameter_f32(parameters, "rear_damage_multiplier", 1.2).clamp(0.05, 3.0);
        state
    }
}

fn behavior_parameter_f32(parameters: &serde_json::Value, key: &str, default: f32) -> f32 {
    parameters
        .get(key)
        .and_then(|value| value.as_f64())
        .map(|value| value as f32)
        .filter(|value| value.is_finite())
        .unwrap_or(default)
}

fn behavior_parameter_u32(parameters: &serde_json::Value, key: &str, default: u32) -> u32 {
    parameters
        .get(key)
        .and_then(|value| value.as_u64())
        .map(|value| value.min(u32::MAX as u64) as u32)
        .unwrap_or(default)
}

fn nested_behavior_parameter_f32(
    parameters: &serde_json::Value,
    object_key: &str,
    value_key: &str,
    default: f32,
) -> f32 {
    parameters
        .get(object_key)
        .map(|value| behavior_parameter_f32(value, value_key, default))
        .unwrap_or(default)
}

impl From<Enemy> for EnemySnapshot {
    fn from(enemy: Enemy) -> Self {
        Self {
            entity_id: enemy.entity_id,
            enemy_id: enemy.enemy_id,
            position: enemy.position,
            velocity: enemy.velocity,
            health: enemy.health,
            max_health: enemy.max_health,
            radius: enemy.radius,
            threat: enemy.threat,
            behavior: enemy.behavior,
            is_boss: enemy.is_boss,
            is_elite: enemy.is_elite,
        }
    }
}

#[derive(Debug, Clone)]
struct Projectile {
    entity_id: u64,
    weapon_id: String,
    position: Vec2,
    velocity: Vec2,
    damage: f32,
    radius: f32,
    pierce_remaining: u32,
    lifetime: f32,
    enemy_slow_multiplier: f32,
    enemy_slow_duration_seconds: f32,
    enemy_knockback_distance: f32,
    age_seconds: f32,
    boomerang_return_after_seconds: Option<f32>,
    boomerang_return_speed: f32,
    turret_fire_interval_seconds: f32,
    turret_fire_cooldown_seconds: f32,
    turret_range: f32,
}

impl Projectile {
    fn is_summon_turret(&self) -> bool {
        self.turret_fire_interval_seconds > 0.0
    }
}

impl From<Projectile> for ProjectileSnapshot {
    fn from(projectile: Projectile) -> Self {
        Self {
            entity_id: projectile.entity_id,
            weapon_id: projectile.weapon_id,
            position: projectile.position,
            velocity: projectile.velocity,
            radius: projectile.radius,
        }
    }
}

#[derive(Debug, Clone)]
struct Pickup {
    entity_id: u64,
    pickup_type: PickupType,
    position: Vec2,
    value: f32,
    radius: f32,
}

impl From<Pickup> for PickupSnapshot {
    fn from(pickup: Pickup) -> Self {
        Self {
            entity_id: pickup.entity_id,
            pickup_type: pickup.pickup_type,
            position: pickup.position,
            value: pickup.value,
            radius: pickup.radius,
        }
    }
}

#[derive(Debug, Clone)]
struct UpgradeOffer {
    snapshot: UpgradeOptionSnapshot,
    effect: UpgradeEffect,
}

impl From<&UpgradeOffer> for UpgradeOptionSnapshot {
    fn from(offer: &UpgradeOffer) -> Self {
        offer.snapshot.clone()
    }
}

#[derive(Debug, Clone)]
enum UpgradeEffect {
    WeaponLevel { weapon_id: String },
    NewWeapon { weapon_id: String },
    Evolution { evolution_id: String },
    Passive { passive_id: String },
}

fn wave_segment_for_time(
    wave: &WaveDefinition,
    time_seconds: f32,
) -> Option<&WaveSegmentDefinition> {
    wave.segments
        .iter()
        .find(|segment| time_seconds >= segment.start_second && time_seconds < segment.end_second)
        .or_else(|| wave.segments.last())
}

fn pick_enemy_id(segment: &WaveSegmentDefinition, rng: &mut RunRng) -> Option<String> {
    let total_weight = segment
        .enemy_pool
        .iter()
        .map(|entry| entry.weight)
        .sum::<f32>();
    if total_weight <= 0.0 {
        return None;
    }
    let mut roll = rng.range_f32(0.0, total_weight);
    for entry in &segment.enemy_pool {
        if roll <= entry.weight {
            return Some(entry.enemy_id.clone());
        }
        roll -= entry.weight;
    }
    segment
        .enemy_pool
        .last()
        .map(|entry| entry.enemy_id.clone())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn run_seconds(seed: u64, seconds: f32) -> RunMetrics {
        let mut core = GameCore::reset(RunConfig {
            seed,
            duration_seconds: seconds,
            ..RunConfig::default()
        });
        let dt = core.fixed_dt();
        let mut guard = 0;
        while !core.is_terminal() && guard < 100_000 {
            let snapshot = core.snapshot();
            let action = if !snapshot.upgrade_options.is_empty() {
                PlayerAction {
                    movement: Vec2::ZERO,
                    upgrade_choice: Some(0),
                }
            } else {
                PlayerAction {
                    movement: Vec2::new(0.8, 0.6),
                    upgrade_choice: None,
                }
            };
            core.step(action, dt);
            guard += 1;
        }
        core.metrics()
    }

    fn fire_first_weapon_into_enemy(core: &mut GameCore, enemy_definition: &EnemyDefinition) {
        core.enemies.clear();
        core.projectiles.clear();
        let enemy_id = core.allocate_entity_id();
        let mut enemy =
            Enemy::from_enemy_definition(enemy_id, Vec2::new(120.0, 0.0), enemy_definition);
        enemy.health = 1000.0;
        enemy.max_health = 1000.0;
        core.enemies.push(enemy);
        core.weapons[0].cooldown_remaining = 0.0;

        core.update_weapon_cooldowns(0.0, &mut Vec::new());
        assert!(!core.projectiles.is_empty());
        core.update_projectiles(0.0, &mut Vec::new());
    }

    #[test]
    fn same_seed_produces_same_metrics() {
        let left = run_seconds(42, 45.0);
        let right = run_seconds(42, 45.0);

        assert_eq!(left.kills, right.kills);
        assert_eq!(left.level, right.level);
        assert_eq!(left.max_enemy_count, right.max_enemy_count);
        assert_eq!(left.upgrade_choices, right.upgrade_choices);
        assert_eq!(
            left.terminal.as_ref().map(|terminal| terminal.kind),
            right.terminal.as_ref().map(|terminal| terminal.kind)
        );
    }

    #[test]
    fn movement_is_normalized_and_clamped_to_map() {
        let mut core = GameCore::reset(RunConfig::default());
        let dt = FixedDt::from_seconds(1.0);
        core.step(
            PlayerAction {
                movement: Vec2::new(10.0, 0.0),
                upgrade_choice: None,
            },
            dt,
        );

        let snapshot = core.snapshot();
        assert!(snapshot.player.position.x <= 180.0 + f32::EPSILON);
        assert!(snapshot.player.position.x <= snapshot.map.width * 0.5);
    }

    #[test]
    fn invalid_upgrade_choice_waits_without_panic() {
        let mut core = GameCore::reset(RunConfig::default());
        core.pending_upgrade_options = core.generate_upgrade_options();

        core.step(
            PlayerAction {
                movement: Vec2::ZERO,
                upgrade_choice: Some(99),
            },
            FixedDt::from_tick_rate(DEFAULT_TICK_RATE),
        );

        assert!(!core.snapshot().upgrade_options.is_empty());
    }

    #[test]
    fn upgrade_options_are_layered_after_weapon_pool_expands() {
        let mut core = GameCore::reset(RunConfig::default());
        let options = core.generate_upgrade_options();

        assert!(options
            .iter()
            .any(|option| matches!(option.effect, UpgradeEffect::WeaponLevel { .. })));
        assert!(options
            .iter()
            .any(|option| matches!(option.effect, UpgradeEffect::NewWeapon { .. })));
        assert!(options
            .iter()
            .any(|option| matches!(option.effect, UpgradeEffect::Passive { .. })));
        assert_eq!(options.len(), 3);
    }

    #[test]
    fn upgrade_options_skip_discover_locked_weapons_and_passives() {
        let mut content = ContentPack::base_demo();
        for (weapon_id, weapon) in content.weapons.iter_mut() {
            if weapon_id != "rainbow-candy-shot" {
                weapon.unlock.unlock_type = "discover".to_string();
            }
        }
        for passive in content.passives.values_mut() {
            passive.unlock.unlock_type = "discover".to_string();
        }

        let mut core = GameCore::reset_with_content(RunConfig::default(), content)
            .expect("content with discover-locked upgrades should initialize");
        let options = core.generate_upgrade_options();

        assert!(!options.is_empty());
        assert!(options
            .iter()
            .all(|option| matches!(option.effect, UpgradeEffect::WeaponLevel { .. })));
        assert!(options
            .iter()
            .all(|option| option.snapshot.id.starts_with("rainbow-candy-shot-level-")));
    }

    #[test]
    fn projectile_snapshot_exposes_active_projectiles() {
        let mut core = GameCore::reset(RunConfig::default());
        let dt = FixedDt::from_tick_rate(DEFAULT_TICK_RATE);

        for _ in 0..300 {
            core.step(PlayerAction::default(), dt);
            let snapshot = core.snapshot();
            if let Some(projectile) = snapshot.visible_projectiles.first() {
                assert_eq!(projectile.weapon_id, "rainbow-candy-shot");
                assert!(projectile.entity_id > 0);
                assert!(projectile.radius > 0.0);
                assert!(projectile.velocity.length_squared() > 0.0);
                return;
            }
        }

        panic!("expected rainbow-candy-shot to create a visible projectile");
    }

    #[test]
    fn orbit_weapon_spawns_projectiles_around_player() {
        let mut core = GameCore::reset(RunConfig {
            starting_loadout: StartingLoadout {
                weapons: vec!["marshmallow-shield".to_string()],
                passives: Vec::new(),
            },
            ..RunConfig::default()
        });
        let dt = core.fixed_dt();

        for _ in 0..20 {
            core.step(PlayerAction::default(), dt);
            if let Some(projectile) = core.projectiles.first() {
                assert!(projectile.position.distance(core.player.position) > PLAYER_RADIUS);
                assert!(projectile.velocity.length_squared() > 0.0);
                assert!(projectile.lifetime > 1.0);
                return;
            }
        }

        panic!("expected marshmallow-shield to create orbit projectiles");
    }

    #[test]
    fn boomerang_weapon_returns_toward_player_after_outbound_window() {
        let mut core = GameCore::reset(RunConfig {
            starting_loadout: StartingLoadout {
                weapons: vec!["lollipop-boomerang".to_string()],
                passives: Vec::new(),
            },
            ..RunConfig::default()
        });
        core.player.velocity = Vec2::new(core.player.move_speed, 0.0);
        core.weapons[0].cooldown_remaining = 0.0;

        core.update_weapon_cooldowns(0.0, &mut Vec::new());

        let projectile = core
            .projectiles
            .iter()
            .find(|projectile| projectile.weapon_id == "lollipop-boomerang")
            .expect("lollipop boomerang should fire a projectile");
        assert!(projectile.boomerang_return_after_seconds.is_some());
        assert!(projectile.velocity.x > 0.0);

        core.update_projectiles(0.2, &mut Vec::new());
        let outbound_x = core
            .projectiles
            .iter()
            .find(|projectile| projectile.weapon_id == "lollipop-boomerang")
            .expect("boomerang should still be active")
            .position
            .x;
        assert!(outbound_x > core.player.position.x);

        core.update_projectiles(0.5, &mut Vec::new());

        let returning = core
            .projectiles
            .iter()
            .find(|projectile| projectile.weapon_id == "lollipop-boomerang")
            .expect("boomerang should still be active on return");
        assert!(returning.velocity.x < 0.0);
        assert!(returning.position.x < outbound_x);
    }

    #[test]
    fn knockback_weapon_pushes_enemy_away_from_player_on_hit() {
        let content = ContentPack::base_demo();
        let enemy_definition = content
            .enemies
            .get("soda-bubble")
            .expect("base demo should include soda-bubble")
            .clone();
        let mut core = GameCore::reset_with_content(
            RunConfig {
                starting_loadout: StartingLoadout {
                    weapons: vec!["soda-fountain".to_string()],
                    passives: Vec::new(),
                },
                ..RunConfig::default()
            },
            content,
        )
        .expect("base demo content should initialize GameCore");
        core.enemies.clear();
        let enemy_id = core.allocate_entity_id();
        let mut enemy =
            Enemy::from_enemy_definition(enemy_id, Vec2::new(120.0, 0.0), &enemy_definition);
        enemy.health = 1000.0;
        enemy.max_health = 1000.0;
        core.enemies.push(enemy);
        core.weapons[0].cooldown_remaining = 0.0;

        core.update_weapon_cooldowns(0.0, &mut Vec::new());

        assert!(core
            .projectiles
            .iter()
            .any(|projectile| projectile.enemy_knockback_distance > 0.0));
        let before = core.enemies[0].position.distance(core.player.position);
        core.update_projectiles(0.0, &mut Vec::new());
        let after = core.enemies[0].position.distance(core.player.position);

        assert!(after > before + KNOCKBACK_WEAPON_DISTANCE * 0.5);
    }

    #[test]
    fn summon_weapon_places_stationary_turret_that_auto_fires() {
        let content = ContentPack::base_demo();
        let enemy_definition = content
            .enemies
            .get("soda-bubble")
            .expect("base demo should include soda-bubble")
            .clone();
        let mut core = GameCore::reset_with_content(
            RunConfig {
                starting_loadout: StartingLoadout {
                    weapons: vec!["pudding-turret".to_string()],
                    passives: Vec::new(),
                },
                ..RunConfig::default()
            },
            content,
        )
        .expect("base demo content should initialize GameCore");
        core.enemies.clear();
        let enemy_id = core.allocate_entity_id();
        let mut enemy =
            Enemy::from_enemy_definition(enemy_id, Vec2::new(120.0, 0.0), &enemy_definition);
        enemy.health = 1000.0;
        enemy.max_health = 1000.0;
        let starting_health = enemy.health;
        core.enemies.push(enemy);
        core.weapons[0].cooldown_remaining = 0.0;

        core.update_weapon_cooldowns(0.0, &mut Vec::new());

        let turret = core
            .projectiles
            .iter()
            .find(|projectile| projectile.weapon_id == "pudding-turret")
            .expect("pudding turret should place a turret projectile");
        assert_eq!(turret.velocity, Vec2::ZERO);
        assert!(turret.is_summon_turret());
        assert!(turret.turret_range >= 400.0);

        let mut events = Vec::new();
        core.update_projectiles(0.0, &mut events);

        assert!(core.enemies[0].health < starting_health);
        assert!(events.iter().any(|event| {
            matches!(
                event,
                GameEvent::EnemyHit { weapon_id, .. } if weapon_id == "pudding-turret"
            )
        }));
    }

    #[test]
    fn summon_weapon_maintains_projectile_count_cap() {
        let content = ContentPack::base_demo();
        let enemy_definition = content
            .enemies
            .get("soda-bubble")
            .expect("base demo should include soda-bubble")
            .clone();
        let mut core = GameCore::reset_with_content(
            RunConfig {
                starting_loadout: StartingLoadout {
                    weapons: vec!["pudding-turret".to_string()],
                    passives: Vec::new(),
                },
                ..RunConfig::default()
            },
            content,
        )
        .expect("base demo content should initialize GameCore");
        core.enemies.clear();
        let enemy_id = core.allocate_entity_id();
        core.enemies.push(Enemy::from_enemy_definition(
            enemy_id,
            Vec2::new(120.0, 0.0),
            &enemy_definition,
        ));
        core.weapons[0].cooldown_remaining = 0.0;
        core.update_weapon_cooldowns(0.0, &mut Vec::new());
        core.weapons[0].cooldown_remaining = 0.0;
        core.update_weapon_cooldowns(0.0, &mut Vec::new());

        assert_eq!(
            core.projectiles
                .iter()
                .filter(|projectile| projectile.weapon_id == "pudding-turret")
                .count(),
            1
        );
    }

    #[test]
    fn zone_weapon_uses_duration_and_stationary_area() {
        let mut core = GameCore::reset(RunConfig {
            starting_loadout: StartingLoadout {
                weapons: vec!["caramel-sticky-ground".to_string()],
                passives: Vec::new(),
            },
            ..RunConfig::default()
        });
        let dt = core.fixed_dt();

        for _ in 0..20 {
            core.step(PlayerAction::default(), dt);
            if let Some(projectile) = core.projectiles.first() {
                assert_eq!(projectile.weapon_id, "caramel-sticky-ground");
                assert_eq!(projectile.velocity, Vec2::ZERO);
                assert!(projectile.lifetime > 2.0);
                return;
            }
        }

        panic!("expected caramel-sticky-ground to create a stationary zone");
    }

    #[test]
    fn can_run_from_disk_content_pack() {
        let content = ContentPack::load_from_dir("../../content/base_demo")
            .expect("base_demo content should load from disk");
        assert!(content.evolutions.contains_key("rainbow-candy-meteor"));
        assert!(content.events.contains_key("rainbow-candy-rush"));
        assert_eq!(content.object_count(), 64);
        for map_id in content.maps.keys().cloned().collect::<Vec<_>>() {
            GameCore::reset_with_content(
                RunConfig {
                    seed: 7,
                    map_id,
                    duration_seconds: 1.0,
                    ..RunConfig::default()
                },
                content.clone(),
            )
            .expect("every base_demo map should initialize with a wave");
        }
        let mut core = GameCore::reset_with_content(
            RunConfig {
                seed: 7,
                duration_seconds: 30.0,
                ..RunConfig::default()
            },
            content,
        )
        .expect("base_demo content should initialize GameCore");
        assert_eq!(
            core.snapshot().build.open_evolution_paths,
            vec!["rainbow-candy-meteor"]
        );

        let dt = core.fixed_dt();
        while !core.is_terminal() {
            let snapshot = core.snapshot();
            let action = if snapshot.upgrade_options.is_empty() {
                PlayerAction {
                    movement: Vec2::new(1.0, 0.0),
                    upgrade_choice: None,
                }
            } else {
                PlayerAction {
                    movement: Vec2::ZERO,
                    upgrade_choice: Some(0),
                }
            };
            core.step(action, dt);
        }

        assert_eq!(
            core.metrics()
                .terminal
                .as_ref()
                .map(|terminal| terminal.kind),
            Some(TerminalKind::Victory)
        );
    }

    #[test]
    fn base_demo_characters_have_valid_starting_loadouts() {
        let content = ContentPack::load_from_dir("../../content/base_demo")
            .expect("base_demo content should load from disk");

        for character_id in [
            "jar-keeper",
            "bubble-courier",
            "cream-knight",
            "sour-plum-doctor",
            "pudding-crafter",
        ] {
            let core = GameCore::reset_with_content(
                RunConfig {
                    character_id: character_id.to_string(),
                    duration_seconds: 1.0,
                    ..RunConfig::default()
                },
                content.clone(),
            )
            .expect("base demo character should initialize");
            assert_eq!(core.config.character_id, character_id);
            assert!(!core.weapons.is_empty());
        }
    }

    #[test]
    fn split_enemy_spawns_children_on_death() {
        let content = ContentPack::base_demo();
        let soda_definition = content
            .enemies
            .get("soda-bubble")
            .expect("base demo should include soda-bubble")
            .clone();
        let mut core = GameCore::reset_with_content(RunConfig::default(), content)
            .expect("base demo should initialize");
        core.enemies.clear();
        let enemy_id = core.allocate_entity_id();
        let mut enemy =
            Enemy::from_enemy_definition(enemy_id, Vec2::new(40.0, 0.0), &soda_definition);
        enemy.health = 1.0;
        core.enemies.push(enemy);
        let projectile_id = core.allocate_entity_id();
        core.projectiles.push(Projectile {
            entity_id: projectile_id,
            weapon_id: "test-shot".to_string(),
            position: Vec2::new(40.0, 0.0),
            velocity: Vec2::ZERO,
            damage: 10.0,
            radius: 24.0,
            pierce_remaining: 1,
            lifetime: 1.0,
            enemy_slow_multiplier: 1.0,
            enemy_slow_duration_seconds: 0.0,
            enemy_knockback_distance: 0.0,
            age_seconds: 0.0,
            boomerang_return_after_seconds: None,
            boomerang_return_speed: 0.0,
            turret_fire_interval_seconds: 0.0,
            turret_fire_cooldown_seconds: 0.0,
            turret_range: 0.0,
        });

        let mut events = Vec::new();
        core.update_projectiles(0.0, &mut events);

        assert!(core
            .enemies
            .iter()
            .all(|enemy| enemy.enemy_id != "soda-bubble"));
        assert_eq!(
            core.enemies
                .iter()
                .filter(|enemy| enemy.enemy_id == "bouncy-gummy")
                .count(),
            2
        );
    }

    #[test]
    fn dash_enemy_temporarily_exceeds_base_speed() {
        let content = ContentPack::base_demo();
        let spicy_definition = content
            .enemies
            .get("spicy-gummy")
            .expect("base demo should include spicy-gummy")
            .clone();
        let mut core = GameCore::reset_with_content(RunConfig::default(), content)
            .expect("base demo should initialize");
        core.enemies.clear();
        let enemy_id = core.allocate_entity_id();
        core.enemies.push(Enemy::from_enemy_definition(
            enemy_id,
            Vec2::new(80.0, 0.0),
            &spicy_definition,
        ));

        let mut saw_dash = false;
        let mut events = Vec::new();
        for _ in 0..80 {
            core.update_enemy_behavior(0.1, &mut events);
            let enemy = &core.enemies[0];
            if enemy.velocity.length() > enemy.move_speed * 1.5 {
                saw_dash = true;
                break;
            }
        }

        assert!(saw_dash);
    }

    #[test]
    fn jump_enemy_uses_burst_movement() {
        let content = ContentPack::base_demo();
        let bouncy_definition = content
            .enemies
            .get("bouncy-gummy")
            .expect("base demo should include bouncy-gummy")
            .clone();
        let mut core = GameCore::reset_with_content(RunConfig::default(), content)
            .expect("base demo should initialize");
        core.enemies.clear();
        let enemy_id = core.allocate_entity_id();
        let mut enemy =
            Enemy::from_enemy_definition(enemy_id, Vec2::new(80.0, 0.0), &bouncy_definition);
        enemy.behavior = EnemyBehavior::Jump;
        enemy.behavior_state.dash_remaining_seconds = 0.2;
        enemy.behavior_state.dash_direction = Vec2::new(-1.0, 0.0);
        enemy.behavior_state.dash_speed_multiplier = 2.0;
        core.enemies.push(enemy);

        core.update_enemy_behavior(0.1, &mut Vec::new());

        let enemy = &core.enemies[0];
        assert!(enemy.velocity.length() > enemy.move_speed * 1.5);
    }

    #[test]
    fn orbit_enemy_moves_tangentially_near_target_radius() {
        let content = ContentPack::base_demo();
        let bouncy_definition = content
            .enemies
            .get("bouncy-gummy")
            .expect("base demo should include bouncy-gummy")
            .clone();
        let mut core = GameCore::reset_with_content(RunConfig::default(), content)
            .expect("base demo should initialize");
        core.enemies.clear();
        let enemy_id = core.allocate_entity_id();
        let mut enemy =
            Enemy::from_enemy_definition(enemy_id, Vec2::new(160.0, 0.0), &bouncy_definition);
        enemy.behavior = EnemyBehavior::OrbitPlayer;
        enemy.behavior_state.orbit_radius = 160.0;
        enemy.behavior_state.orbit_approach_weight = 0.0;
        enemy.behavior_state.orbit_direction = 1.0;
        core.enemies.push(enemy);

        core.update_enemy_behavior(0.1, &mut Vec::new());

        let enemy = &core.enemies[0];
        assert!(enemy.velocity.y.abs() > enemy.velocity.x.abs());
        assert!(enemy.velocity.length() > 0.0);
    }

    #[test]
    fn ranged_spit_enemy_spawns_damage_hazard() {
        let content = ContentPack::base_demo();
        let bouncy_definition = content
            .enemies
            .get("bouncy-gummy")
            .expect("base demo should include bouncy-gummy")
            .clone();
        let mut core = GameCore::reset_with_content(RunConfig::default(), content)
            .expect("base demo should initialize");
        core.enemies.clear();
        let enemy_id = core.allocate_entity_id();
        let mut enemy =
            Enemy::from_enemy_definition(enemy_id, Vec2::new(120.0, 0.0), &bouncy_definition);
        enemy.behavior = EnemyBehavior::RangedSpit;
        enemy.behavior_state.ranged_range = 260.0;
        enemy.behavior_state.ranged_cooldown_remaining_seconds = 0.0;
        enemy.behavior_state.ranged_windup_seconds = 0.0;
        enemy.behavior_state.ranged_projectile_damage_per_second = 5.0;
        core.enemies.push(enemy);

        core.update_enemy_behavior(0.1, &mut Vec::new());

        assert!(core
            .hazards
            .iter()
            .any(|hazard| hazard.damage_per_second >= 5.0));
    }

    #[test]
    fn shielded_enemy_reduces_front_projectile_damage() {
        let content = ContentPack::base_demo();
        let bouncy_definition = content
            .enemies
            .get("bouncy-gummy")
            .expect("base demo should include bouncy-gummy")
            .clone();
        let mut core = GameCore::reset_with_content(RunConfig::default(), content)
            .expect("base demo should initialize");
        core.enemies.clear();
        let enemy_id = core.allocate_entity_id();
        let mut enemy =
            Enemy::from_enemy_definition(enemy_id, Vec2::new(60.0, 0.0), &bouncy_definition);
        enemy.behavior = EnemyBehavior::Shielded;
        enemy.behavior_state.shield_front_damage_multiplier = 0.5;
        enemy.behavior_state.shield_rear_damage_multiplier = 1.5;
        let starting_health = enemy.health;
        core.enemies.push(enemy);
        let projectile_id = core.allocate_entity_id();
        core.projectiles.push(Projectile {
            entity_id: projectile_id,
            weapon_id: "test-candy".to_string(),
            position: Vec2::new(48.0, 0.0),
            velocity: Vec2::ZERO,
            damage: 10.0,
            radius: 12.0,
            pierce_remaining: 1,
            lifetime: 1.0,
            enemy_slow_multiplier: 1.0,
            enemy_slow_duration_seconds: 0.0,
            enemy_knockback_distance: 0.0,
            age_seconds: 0.0,
            boomerang_return_after_seconds: None,
            boomerang_return_speed: 0.0,
            turret_fire_interval_seconds: 0.0,
            turret_fire_cooldown_seconds: 0.0,
            turret_range: 0.0,
        });

        core.update_projectiles(0.0, &mut Vec::new());

        let damage_taken = starting_health - core.enemies[0].health;
        assert!((damage_taken - 5.0).abs() < 0.01);
    }

    #[test]
    fn boss_abilities_emit_events_and_spawn_hazards() {
        let content = ContentPack::base_demo();
        let boss_definition = content
            .bosses
            .get("caramel-furnace")
            .expect("base demo should include caramel-furnace")
            .clone();
        let mut core = GameCore::reset_with_content(RunConfig::default(), content)
            .expect("base demo should initialize");
        core.enemies.clear();
        let boss_id = core.allocate_entity_id();
        core.enemies.push(Enemy::from_boss_definition(
            boss_id,
            Vec2::new(120.0, 0.0),
            &boss_definition,
        ));

        let mut events = Vec::new();
        core.update_enemy_behavior(0.1, &mut events);

        assert!(events.iter().any(|event| {
            matches!(
                event,
                GameEvent::BossAbilityUsed {
                    boss_id,
                    ability_id,
                    ..
                } if boss_id == "caramel-furnace" && ability_id == "lay_caramel_tracks"
            )
        }));
        assert!(!core.hazards.is_empty());
    }

    #[test]
    fn boss_phase_change_emits_event_and_uses_new_ability() {
        let content = ContentPack::base_demo();
        let boss_definition = content
            .bosses
            .get("runaway-sugar-mixer")
            .expect("base demo should include runaway-sugar-mixer")
            .clone();
        let mut core = GameCore::reset_with_content(RunConfig::default(), content)
            .expect("base demo should initialize");
        core.enemies.clear();
        let entity_id = core.allocate_entity_id();
        let mut boss =
            Enemy::from_boss_definition(entity_id, Vec2::new(120.0, 0.0), &boss_definition);
        boss.health = boss.max_health * 0.40;
        core.enemies.push(boss);

        let mut events = Vec::new();
        core.update_enemy_behavior(0.1, &mut events);

        assert!(events.iter().any(|event| {
            matches!(
                event,
                GameEvent::BossPhaseChanged {
                    boss_id,
                    phase_index: 1,
                    ..
                } if boss_id == "runaway-sugar-mixer"
            )
        }));
        assert!(events.iter().any(|event| {
            matches!(
                event,
                GameEvent::BossAbilityUsed {
                    boss_id,
                    ability_id,
                    ..
                } if boss_id == "runaway-sugar-mixer" && ability_id == "dash_charge"
            )
        }));
        assert!(core
            .hazards
            .iter()
            .any(|hazard| hazard.damage_per_second > 0.0));
    }

    #[test]
    fn multiple_boss_events_spawn_once_each() {
        let mut content = ContentPack::base_demo();
        let wave = content
            .waves
            .get_mut("frosting-grassland-standard")
            .expect("base demo should include frosting-grassland wave");
        wave.boss_events = vec![
            content::BossEventDefinition {
                time_second: 0.05,
                boss_id: "runaway-sugar-mixer".to_string(),
            },
            content::BossEventDefinition {
                time_second: 0.10,
                boss_id: "giant-gummy-bear-king".to_string(),
            },
        ];
        let mut core = GameCore::reset_with_content(
            RunConfig {
                duration_seconds: 1.0,
                ..RunConfig::default()
            },
            content,
        )
        .expect("content should initialize");
        let dt = FixedDt::from_seconds(0.05);
        let mut boss_spawns = 0;

        for _ in 0..10 {
            let result = core.step(PlayerAction::default(), dt);
            boss_spawns += result
                .events
                .iter()
                .filter(|event| matches!(event, GameEvent::BossSpawned { .. }))
                .count();
        }

        assert_eq!(boss_spawns, 2);
        assert_eq!(core.enemies.iter().filter(|enemy| enemy.is_boss).count(), 2);

        for _ in 0..5 {
            let result = core.step(PlayerAction::default(), dt);
            assert!(!result
                .events
                .iter()
                .any(|event| matches!(event, GameEvent::BossSpawned { .. })));
        }
    }

    #[test]
    fn snapshot_reports_nearest_boss_when_multiple_alive() {
        let content = ContentPack::base_demo();
        let mixer_definition = content
            .bosses
            .get("runaway-sugar-mixer")
            .expect("base demo should include runaway-sugar-mixer")
            .clone();
        let bear_definition = content
            .bosses
            .get("giant-gummy-bear-king")
            .expect("base demo should include giant-gummy-bear-king")
            .clone();
        let mut core = GameCore::reset_with_content(RunConfig::default(), content)
            .expect("base demo should initialize");
        core.enemies.clear();
        core.player.position = Vec2::ZERO;

        let mixer_id = core.allocate_entity_id();
        core.enemies.push(Enemy::from_boss_definition(
            mixer_id,
            Vec2::new(320.0, 0.0),
            &mixer_definition,
        ));
        let bear_id = core.allocate_entity_id();
        core.enemies.push(Enemy::from_boss_definition(
            bear_id,
            Vec2::new(80.0, 0.0),
            &bear_definition,
        ));

        let snapshot = core.snapshot();

        assert_eq!(
            snapshot.boss.as_ref().map(|boss| boss.boss_id.as_str()),
            Some("giant-gummy-bear-king")
        );
    }

    #[test]
    fn hazard_slow_reduces_player_movement_speed() {
        let mut core = GameCore::reset(RunConfig::default());
        core.hazards.push(Hazard {
            position: Vec2::ZERO,
            radius: 64.0,
            remaining_seconds: 1.0,
            slow_multiplier: 0.5,
            damage_per_second: 0.0,
        });
        core.update_player_slow_effects(0.1);
        core.update_hazards(0.1, &mut Vec::new(), &mut RewardHint::default());
        core.update_player_movement(Vec2::new(1.0, 0.0), 1.0);

        assert!(core.player.velocity.length() < core.player.move_speed * 0.75);
    }

    #[test]
    fn hazard_damage_reduces_player_health() {
        let mut core = GameCore::reset(RunConfig::default());
        core.hazards.push(Hazard {
            position: Vec2::ZERO,
            radius: 64.0,
            remaining_seconds: 1.0,
            slow_multiplier: 1.0,
            damage_per_second: 6.0,
        });
        let mut events = Vec::new();
        let mut reward_hint = RewardHint::default();

        core.update_hazards(0.5, &mut events, &mut reward_hint);

        assert!(core.player.health < core.player.max_health);
        assert_eq!(core.metrics.damage_taken, 3.0);
        assert_eq!(reward_hint.damage_taken_delta, 3.0);
        assert!(events
            .iter()
            .any(|event| matches!(event, GameEvent::PlayerDamaged { .. })));
    }

    #[test]
    fn player_regen_restores_health_without_exceeding_max() {
        let mut core = GameCore::reset(RunConfig::default());
        core.player.health = core.player.max_health - 1.0;
        core.player.regen_per_second = 3.0;

        core.update_player_regen(1.0);

        assert_eq!(core.player.health, core.player.max_health);
    }

    #[test]
    fn hazard_snapshot_exposes_active_hazards() {
        let mut core = GameCore::reset(RunConfig::default());
        let position = Vec2::new(24.0, -12.0);
        core.hazards.push(Hazard {
            position,
            radius: 64.0,
            remaining_seconds: 3.5,
            slow_multiplier: 0.55,
            damage_per_second: 2.5,
        });

        let snapshot = core.snapshot();

        assert_eq!(snapshot.active_hazards.len(), 1);
        let hazard = &snapshot.active_hazards[0];
        assert_eq!(hazard.position, position);
        assert_eq!(hazard.radius, 64.0);
        assert_eq!(hazard.slow_multiplier, 0.55);
        assert_eq!(hazard.damage_per_second, 2.5);
        assert_eq!(hazard.remaining_seconds, 3.5);
    }

    #[test]
    fn passive_special_stats_affect_runtime_modifiers() {
        let mut core = GameCore::reset(RunConfig::default());

        core.apply_passive("nonstick-apron");
        core.apply_passive("frosting-gloves");
        core.apply_passive("sour-tuner");

        assert!(core.player.damage_reduction > 0.0);
        assert!(core.player.projectile_size_multiplier > 1.0);
        assert!(core.player.effect_duration_multiplier > 1.0);
    }

    #[test]
    fn sweet_starter_grants_bonus_xp_on_level_milestones() {
        let mut core = GameCore::reset(RunConfig::default());
        core.player.level = 4;
        core.player.xp = xp_required(4);
        let mut events = Vec::new();
        let mut reward_hint = RewardHint::default();

        core.process_level_ups(&mut events, &mut reward_hint);

        assert_eq!(core.player.level, 5);
        assert_eq!(core.player.xp, 18.0);
        assert_eq!(core.metrics.xp_collected, 18.0);
        assert_eq!(reward_hint.xp_delta, 18.0);
        assert!(events.iter().any(|event| {
            matches!(
                event,
                GameEvent::XpCollected {
                    entity_id: 0,
                    value
                } if (*value - 18.0).abs() <= f32::EPSILON
            )
        }));
    }

    #[test]
    fn bubble_runner_movement_temporarily_boosts_pickup_radius() {
        let mut core = GameCore::reset(RunConfig {
            character_id: "bubble-courier".to_string(),
            starting_loadout: StartingLoadout::default(),
            ..RunConfig::default()
        });
        core.pickups.push(Pickup {
            entity_id: 999,
            pickup_type: PickupType::Xp,
            position: Vec2::new(118.0, 0.0),
            value: 5.0,
            radius: 5.0,
        });

        core.step(
            PlayerAction {
                movement: Vec2::new(1.0, 0.0),
                upgrade_choice: None,
            },
            core.fixed_dt(),
        );

        assert!(core.pickups.is_empty());
        assert!(core.metrics.xp_collected > 5.0);
        assert!(core.snapshot().player.status_effects.iter().any(|effect| {
            effect.kind == "pickup_boost" && effect.effect_id == "bubble-runner"
        }));
    }

    #[test]
    fn cream_guard_reduces_followup_damage_after_hit() {
        let mut core = GameCore::reset(RunConfig {
            character_id: "cream-knight".to_string(),
            starting_loadout: StartingLoadout::default(),
            ..RunConfig::default()
        });
        let mut events = Vec::new();
        let mut reward_hint = RewardHint::default();

        core.apply_player_damage(10.0, 1.0, "contact", &mut events, &mut reward_hint);
        core.apply_player_damage(10.0, 1.0, "contact", &mut events, &mut reward_hint);

        assert!((core.metrics.damage_taken - 16.5).abs() <= 0.001);
        assert!((core.player.health - (core.player.max_health - 16.5)).abs() <= 0.001);
        assert!(core.snapshot().player.status_effects.iter().any(|effect| {
            effect.kind == "damage_reduction" && effect.effect_id == "cream-guard"
        }));
    }

    #[test]
    fn sour_control_strengthens_slow_weapon_effects_on_enemies() {
        let content = ContentPack::base_demo();
        let enemy_definition = content
            .enemies
            .get("soda-bubble")
            .expect("base demo should include soda-bubble")
            .clone();
        let mut baseline_core = GameCore::reset_with_content(
            RunConfig {
                character_id: "jar-keeper".to_string(),
                starting_loadout: StartingLoadout {
                    weapons: vec!["sour-plum-spray".to_string()],
                    passives: Vec::new(),
                },
                ..RunConfig::default()
            },
            content.clone(),
        )
        .expect("base demo content should initialize GameCore");
        let mut sour_core = GameCore::reset_with_content(
            RunConfig {
                character_id: "sour-plum-doctor".to_string(),
                starting_loadout: StartingLoadout::default(),
                ..RunConfig::default()
            },
            content,
        )
        .expect("base demo content should initialize GameCore");

        fire_first_weapon_into_enemy(&mut baseline_core, &enemy_definition);
        fire_first_weapon_into_enemy(&mut sour_core, &enemy_definition);

        let baseline_enemy = &baseline_core.enemies[0];
        let sour_enemy = &sour_core.enemies[0];
        assert!((baseline_enemy.slow_multiplier - SLOW_WEAPON_ENEMY_MULTIPLIER).abs() <= 0.001);
        assert!((sour_enemy.slow_multiplier - SOUR_CONTROL_ENEMY_SLOW_MULTIPLIER).abs() <= 0.001);
        assert!(sour_enemy.slow_remaining_seconds > baseline_enemy.slow_remaining_seconds);

        sour_core.update_enemy_behavior(0.1, &mut Vec::new());
        let moving_enemy = &sour_core.enemies[0];
        assert!(
            moving_enemy.velocity.length()
                <= moving_enemy.move_speed * SOUR_CONTROL_ENEMY_SLOW_MULTIPLIER + 0.001
        );
    }

    #[test]
    fn pudding_crafter_extends_summon_projectile_lifetime() {
        let content = ContentPack::base_demo();
        let enemy_definition = content
            .enemies
            .get("soda-bubble")
            .expect("base demo should include soda-bubble")
            .clone();
        let mut core = GameCore::reset_with_content(
            RunConfig {
                character_id: "pudding-crafter".to_string(),
                starting_loadout: StartingLoadout::default(),
                ..RunConfig::default()
            },
            content,
        )
        .expect("base demo content should initialize GameCore");
        core.enemies.clear();
        let enemy_id = core.allocate_entity_id();
        core.enemies.push(Enemy::from_enemy_definition(
            enemy_id,
            Vec2::new(120.0, 0.0),
            &enemy_definition,
        ));
        core.weapons[0].cooldown_remaining = 0.0;

        core.update_weapon_cooldowns(0.0, &mut Vec::new());

        let projectile = core
            .projectiles
            .iter()
            .find(|projectile| projectile.weapon_id == "pudding-turret")
            .expect("pudding turret should fire a summon projectile");
        assert!((projectile.lifetime - 5.0 * LONGER_SUMMONS_LIFETIME_MULTIPLIER).abs() <= 0.001);
        assert_eq!(projectile.velocity, Vec2::ZERO);
        assert!(projectile.is_summon_turret());
    }

    #[test]
    fn reset_applies_starting_passive_loadout() {
        let core = GameCore::reset(RunConfig {
            starting_loadout: StartingLoadout {
                weapons: vec!["rainbow-candy-shot".to_string()],
                passives: vec!["big-candy-jar".to_string(), "nonstick-apron".to_string()],
            },
            ..RunConfig::default()
        });

        assert!(core
            .passives
            .iter()
            .any(|passive| passive.id == "big-candy-jar"));
        assert!(core.snapshot().player.max_health > 120.0);
        assert!(core.player.damage_reduction > 0.0);
    }

    #[test]
    fn upgrade_options_can_grant_new_weapons() {
        let mut core = GameCore::reset(RunConfig::default());
        core.pending_upgrade_options = vec![UpgradeOffer {
            snapshot: UpgradeOptionSnapshot {
                id: "candy-crystal-lance".to_string(),
                name: "获得糖晶长枪".to_string(),
                tags: Vec::new(),
                description: String::new(),
            },
            effect: UpgradeEffect::NewWeapon {
                weapon_id: "candy-crystal-lance".to_string(),
            },
        }];

        core.apply_upgrade_choice(0, &mut Vec::new(), &mut RewardHint::default());

        assert!(core
            .weapons
            .iter()
            .any(|weapon| weapon.id == "candy-crystal-lance"));
    }

    #[test]
    fn boss_chest_evolution_replaces_required_weapon() {
        let mut core = GameCore::reset(RunConfig::default());
        core.weapons[0].level = 5;
        core.passives.push(PassiveState {
            id: "candy-crystal-lens".to_string(),
            level: 3,
            max_level: 5,
        });
        core.boss_chests_available = 1;

        let options = core.generate_evolution_options();
        assert_eq!(options[0].snapshot.id, "rainbow-candy-meteor");
        core.pending_upgrade_options = options;
        core.apply_upgrade_choice(0, &mut Vec::new(), &mut RewardHint::default());

        let snapshot = core.snapshot();
        assert!(snapshot
            .build
            .evolutions
            .iter()
            .any(|evolution| evolution.id == "rainbow-candy-meteor"));
        assert!(snapshot
            .build
            .weapons
            .iter()
            .any(|weapon| weapon.id == "rainbow-candy-meteor"));
        assert!(!snapshot
            .build
            .open_evolution_paths
            .iter()
            .any(|id| id == "rainbow-candy-meteor"));
    }

    #[test]
    fn time_window_content_event_applies_active_effects() {
        let mut core = GameCore::reset(RunConfig::default());
        let event = core
            .content
            .events
            .get_mut("rainbow-candy-rush")
            .expect("base demo event should exist");
        event.trigger.start_second = Some(0.0);
        event.trigger.end_second = Some(10.0);
        event.trigger.chance = Some(1.0);
        core.pickups.push(Pickup {
            entity_id: 999,
            pickup_type: PickupType::Xp,
            position: Vec2::ZERO,
            value: 10.0,
            radius: 10.0,
        });

        let result = core.step(PlayerAction::default(), FixedDt::from_seconds(0.1));

        assert!(result
            .events
            .iter()
            .any(|event| matches!(event, GameEvent::ContentEventTriggered { event_id } if event_id == "rainbow-candy-rush")));
        assert!(result.reward_hint.xp_delta > 13.9);
        assert!(core.active_event_multiplier("spawn_rate_multiplier") > 1.0);
        assert!(result.snapshot.active_event_effects.iter().any(|effect| {
            effect.event_id == "rainbow-candy-rush"
                && effect.effect_type == "xp_multiplier"
                && effect.value > 1.0
                && effect.remaining_seconds > 24.0
        }));
    }

    #[test]
    fn guaranteed_content_event_does_not_advance_rng() {
        let mut core = GameCore::reset(RunConfig::default());
        let mut event = core
            .content
            .events
            .get("rainbow-candy-rush")
            .expect("base demo event should exist")
            .clone();
        event.id = "test-guaranteed-content-event".to_string();
        event.trigger.start_second = Some(0.0);
        event.trigger.end_second = Some(10.0);
        event.trigger.chance = Some(1.0);
        event.effects = Vec::new();
        core.content.events.clear();
        core.content.events.insert(event.id.clone(), event);

        let mut expected_rng = core.rng.clone();
        let mut events = Vec::new();
        core.update_content_events(0.1, &mut events);

        assert!(events.iter().any(
            |event| matches!(event, GameEvent::ContentEventTriggered { event_id } if event_id == "test-guaranteed-content-event")
        ));
        assert_eq!(core.rng.next_u32(), expected_rng.next_u32());
    }

    #[test]
    fn content_events_can_offer_upgrades_and_spawn_entities() {
        let mut core = GameCore::reset(RunConfig::default());
        let mut event = core
            .content
            .events
            .get("rainbow-candy-rush")
            .expect("base demo event should exist")
            .clone();
        event.id = "test-supply-quake".to_string();
        event.trigger.start_second = Some(0.0);
        event.trigger.end_second = Some(10.0);
        event.trigger.chance = Some(1.0);
        event.effects = vec![
            content::EventEffectDefinition {
                effect_type: "offer_upgrade".to_string(),
                value: 3.0,
                duration_seconds: None,
                enemy_id: None,
                radius: None,
                slow_multiplier: None,
                placement: None,
                min_distance: None,
                max_distance: None,
                lane_width: None,
                sample_interval_seconds: None,
                history_seconds: None,
                trigger_radius: None,
                hazard_duration_seconds: None,
                damage_per_second: None,
            },
            content::EventEffectDefinition {
                effect_type: "spawn_enemy".to_string(),
                value: 2.0,
                duration_seconds: None,
                enemy_id: Some("bouncy-gummy".to_string()),
                radius: None,
                slow_multiplier: None,
                placement: None,
                min_distance: None,
                max_distance: None,
                lane_width: None,
                sample_interval_seconds: None,
                history_seconds: None,
                trigger_radius: None,
                hazard_duration_seconds: None,
                damage_per_second: None,
            },
            content::EventEffectDefinition {
                effect_type: "spawn_hazard".to_string(),
                value: 2.0,
                duration_seconds: Some(4.0),
                enemy_id: None,
                radius: Some(48.0),
                slow_multiplier: Some(0.55),
                placement: None,
                min_distance: None,
                max_distance: None,
                lane_width: None,
                sample_interval_seconds: None,
                history_seconds: None,
                trigger_radius: None,
                hazard_duration_seconds: None,
                damage_per_second: None,
            },
        ];
        core.content.events.insert(event.id.clone(), event);

        let result = core.step(PlayerAction::default(), FixedDt::from_seconds(0.1));

        assert!(result.events.iter().any(
            |event| matches!(event, GameEvent::UpgradeOffered { options } if !options.is_empty())
        ));
        assert!(!core.snapshot().upgrade_options.is_empty());
        assert!(core
            .enemies
            .iter()
            .any(|enemy| enemy.enemy_id == "bouncy-gummy"));
        assert_eq!(core.hazards.len(), 2);
    }

    #[test]
    fn content_event_can_spawn_forward_lane_hazards() {
        let mut core = GameCore::reset(RunConfig::default());
        core.player.velocity = Vec2::new(100.0, 0.0);
        let mut event = core
            .content
            .events
            .get("caramel-quake")
            .expect("base demo event should exist")
            .clone();
        event.id = "test-forward-lane-quake".to_string();
        event.trigger.start_second = Some(0.0);
        event.trigger.end_second = Some(10.0);
        event.trigger.chance = Some(1.0);
        event.effects = vec![content::EventEffectDefinition {
            effect_type: "spawn_hazard".to_string(),
            value: 3.0,
            duration_seconds: Some(2.0),
            enemy_id: None,
            radius: Some(36.0),
            slow_multiplier: Some(0.7),
            placement: Some("player_forward_lane".to_string()),
            min_distance: Some(60.0),
            max_distance: Some(120.0),
            lane_width: Some(30.0),
            sample_interval_seconds: None,
            history_seconds: None,
            trigger_radius: None,
            hazard_duration_seconds: None,
            damage_per_second: None,
        }];
        core.content.events.insert(event.id.clone(), event);

        core.step(PlayerAction::default(), FixedDt::from_seconds(0.1));

        assert_eq!(core.hazards.len(), 3);
        assert!(core.hazards.iter().all(|hazard| hazard.position.x > 0.0));
        assert!(core
            .hazards
            .iter()
            .any(|hazard| hazard.position.y.abs() >= 29.0));
    }

    #[test]
    fn content_event_can_spawn_route_echo_hazards() {
        let mut core = GameCore::reset(RunConfig::default());
        core.time_seconds = 20.0;
        core.player.position = Vec2::ZERO;
        core.player_position_history = vec![
            PlayerPositionSample {
                time_seconds: 10.0,
                position: Vec2::ZERO,
            },
            PlayerPositionSample {
                time_seconds: 6.5,
                position: Vec2::new(48.0, 0.0),
            },
        ];

        let mut event = core
            .content
            .events
            .get("caramel-quake")
            .expect("base demo event should exist")
            .clone();
        event.id = "test-route-echo".to_string();
        event.trigger.start_second = Some(core.time_seconds);
        event.trigger.end_second = Some(core.time_seconds + 1.0);
        event.trigger.chance = Some(1.0);
        event.effects = vec![content::EventEffectDefinition {
            effect_type: "route_echo_hazard".to_string(),
            value: 2.0,
            duration_seconds: Some(2.0),
            enemy_id: None,
            radius: Some(42.0),
            slow_multiplier: Some(0.72),
            placement: None,
            min_distance: None,
            max_distance: None,
            lane_width: None,
            sample_interval_seconds: Some(0.5),
            history_seconds: Some(10.0),
            trigger_radius: Some(90.0),
            hazard_duration_seconds: Some(3.0),
            damage_per_second: Some(0.0),
        }];
        core.content.events.insert(event.id.clone(), event);

        let hazards_before = core.hazards.len();
        let result = core.step(PlayerAction::default(), FixedDt::from_seconds(0.1));
        let spawned_hazards = &core.hazards[hazards_before..];

        assert!(result
            .events
            .iter()
            .any(|event| matches!(event, GameEvent::ContentEventTriggered { event_id } if event_id == "test-route-echo")));
        assert!(!spawned_hazards.is_empty());
        assert!(spawned_hazards
            .iter()
            .any(|hazard| hazard.position.distance(Vec2::ZERO) <= 18.0));
        assert!(spawned_hazards
            .iter()
            .all(|hazard| (hazard.radius - 42.0).abs() < f32::EPSILON));
        assert!(spawned_hazards
            .iter()
            .all(|hazard| (hazard.slow_multiplier - 0.72).abs() < f32::EPSILON));
    }
}
