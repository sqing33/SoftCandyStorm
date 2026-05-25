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
    BossDefinition, CharacterDefinition, EnemyDefinition, EnemyStatsDefinition, MapDefinition,
    WaveDefinition, WaveSegmentDefinition, WeaponDefinition,
};
use rng::RunRng;
use std::cmp::Ordering;

const DEFAULT_TICK_RATE: u32 = 30;
const PLAYER_RADIUS: f32 = 18.0;
const CONTACT_DAMAGE_CAP_PER_SECOND: f32 = 35.0;
const MAX_VISIBLE_ENEMIES: usize = 32;
const MAX_VISIBLE_PICKUPS: usize = 16;
const MAX_VISIBLE_PROJECTILES: usize = 48;

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
    pub boss: Option<BossSnapshot>,
    pub upgrade_options: Vec<UpgradeOptionSnapshot>,
    pub build: BuildSnapshot,
    pub map: MapSnapshot,
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
    enemies: Vec<Enemy>,
    projectiles: Vec<Projectile>,
    pickups: Vec<Pickup>,
    spawn_timer: f32,
    boss_spawned: bool,
    pending_upgrade_options: Vec<UpgradeOffer>,
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

        Ok(Self {
            config,
            map: MapRuntime::from_definition(map_definition),
            wave_id,
            player: PlayerState::from_definition(character),
            content,
            rng: RunRng::new(seed),
            tick: 0,
            time_seconds: 0.0,
            next_entity_id: 1,
            weapons,
            passives: Vec::new(),
            enemies: Vec::new(),
            projectiles: Vec::new(),
            pickups: Vec::new(),
            spawn_timer: 0.0,
            boss_spawned: false,
            pending_upgrade_options: Vec::new(),
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

        self.update_player_movement(action.movement, dt_seconds);
        self.update_wave_spawns(dt_seconds, &mut events);
        self.update_enemy_behavior(dt_seconds);
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

        let boss = self
            .enemies
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

    fn update_player_movement(&mut self, movement: Vec2, dt: f32) {
        let normalized = movement.clamp_length_max(1.0);
        self.player.velocity = normalized * self.player.move_speed;
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

    fn update_wave_spawns(&mut self, dt: f32, events: &mut Vec<GameEvent>) {
        let Some(wave) = self.content.waves.get(&self.wave_id).cloned() else {
            return;
        };

        let boss_to_spawn = wave
            .boss_events
            .iter()
            .find(|event| self.time_seconds >= event.time_second && !self.boss_spawned)
            .map(|event| event.boss_id.clone());

        if let Some(boss_id) = boss_to_spawn {
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
                self.boss_spawned = true;
            }
        }

        let Some(segment) = wave_segment_for_time(&wave, self.time_seconds).cloned() else {
            return;
        };

        if self.enemies.len() >= segment.max_alive {
            return;
        }

        let spawn_interval = segment.spawn_interval_ms / 1000.0;

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

    fn update_enemy_behavior(&mut self, dt: f32) {
        for enemy in &mut self.enemies {
            let direction = (self.player.position - enemy.position).normalized_or_zero();
            enemy.velocity = direction * enemy.move_speed;
            enemy.position += enemy.velocity * dt;
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
            let count = self.weapons[weapon_index].projectile_count();
            let projectile_speed = self.weapons[weapon_index].projectile_speed;
            let damage = self.weapons[weapon_index].damage * self.player.damage_multiplier;
            let radius =
                self.weapons[weapon_index].radius * self.player.projectile_size_multiplier.max(0.1);
            let pierce = self.weapons[weapon_index].pierce;
            let cooldown = self.weapons[weapon_index].cooldown * self.player.cooldown_multiplier;
            let lifetime = 1.2 * self.player.effect_duration_multiplier.max(0.1);
            let base_direction = (target_position - self.player.position).normalized_or_zero();
            let spread_step = if count > 1 { 0.18 } else { 0.0 };
            let spread_start = -spread_step * (count.saturating_sub(1) as f32) * 0.5;

            for projectile_index in 0..count {
                let angle = spread_start + spread_step * projectile_index as f32;
                let direction = base_direction.rotated(angle).normalized_or_zero();
                let projectile = Projectile {
                    entity_id: self.allocate_entity_id(),
                    weapon_id: weapon_id.clone(),
                    position: self.player.position,
                    velocity: direction * projectile_speed,
                    damage,
                    radius,
                    pierce_remaining: pierce,
                    lifetime,
                };
                self.projectiles.push(projectile);
            }

            self.weapons[weapon_index].cooldown_remaining += cooldown;
            events.push(GameEvent::WeaponFired {
                weapon_id,
                projectile_count: count as u32,
            });
        }
    }

    fn update_projectiles(&mut self, dt: f32, events: &mut Vec<GameEvent>) {
        for projectile in &mut self.projectiles {
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
                    enemy.health -= projectile.damage;
                    self.metrics.damage_dealt_by_weapon += projectile.damage;
                    projectile.pierce_remaining = projectile.pierce_remaining.saturating_sub(1);
                    events.push(GameEvent::EnemyHit {
                        entity_id: enemy.entity_id,
                        damage: projectile.damage,
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
            events.push(GameEvent::EnemyKilled {
                entity_id: enemy.entity_id,
                enemy_id: enemy.enemy_id.clone(),
            });
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
    }

    fn resolve_contact_damage(
        &mut self,
        dt: f32,
        events: &mut Vec<GameEvent>,
        reward_hint: &mut RewardHint,
    ) {
        let total_contact_dps = self
            .enemies
            .iter()
            .filter(|enemy| {
                self.player.position.distance(enemy.position) <= PLAYER_RADIUS + enemy.radius
            })
            .map(|enemy| enemy.contact_damage_per_second)
            .sum::<f32>()
            .min(CONTACT_DAMAGE_CAP_PER_SECOND);

        if total_contact_dps <= 0.0 {
            return;
        }

        let damage_reduction = self.player.damage_reduction.clamp(0.0, 0.8);
        let damage = total_contact_dps * dt * (1.0 - damage_reduction);
        self.player.health = (self.player.health - damage).max(0.0);
        self.metrics.damage_taken += damage;
        reward_hint.damage_taken_delta += damage;
        events.push(GameEvent::PlayerDamaged { amount: damage });
    }

    fn collect_pickups(&mut self, events: &mut Vec<GameEvent>, reward_hint: &mut RewardHint) {
        let mut collected = Vec::new();
        self.pickups.retain(|pickup| {
            let should_collect = self.player.position.distance(pickup.position)
                <= self.player.pickup_radius + pickup.radius;
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
                    let value = pickup.value * self.player.xp_multiplier;
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
        let mut candidates = Vec::new();

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
            candidates.push(UpgradeOffer {
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

        for weapon in self.content.weapons.values() {
            if self.weapons.iter().any(|state| state.id == weapon.id) {
                continue;
            }
            candidates.push(UpgradeOffer {
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

        for passive in self.content.passives.values() {
            if self
                .passives
                .iter()
                .any(|state| state.id == passive.id && state.level >= state.max_level)
            {
                continue;
            }
            candidates.push(UpgradeOffer {
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

        if candidates.is_empty() {
            return Vec::new();
        }
        let offset = self.rng.range_usize(candidates.len());
        candidates.rotate_left(offset);
        candidates.into_iter().take(3).collect()
    }

    fn add_or_level_passive(&mut self, id: &str, max_level: u32) {
        if let Some(passive) = self.passives.iter_mut().find(|passive| passive.id == id) {
            passive.level = (passive.level + 1).min(passive.max_level);
        } else {
            self.passives.push(PassiveState {
                id: id.to_string(),
                level: 1,
                max_level,
            });
        }
    }

    fn apply_passive(&mut self, id: &str) {
        let Some(definition) = self.content.passives.get(id).cloned() else {
            return;
        };
        self.add_or_level_passive(id, definition.max_level);
        for modifier in definition.stat_modifiers {
            match (modifier.stat.as_str(), modifier.mode.as_str()) {
                ("max_health", "add") => {
                    self.player.max_health += modifier.value_per_level;
                    self.player.health =
                        (self.player.health + modifier.value_per_level).min(self.player.max_health);
                }
                ("move_speed", "add") => {
                    self.player.move_speed += modifier.value_per_level;
                }
                ("pickup_radius", "add") => {
                    self.player.pickup_radius += modifier.value_per_level;
                }
                ("damage_multiplier", "add") => {
                    self.player.damage_multiplier += modifier.value_per_level;
                }
                ("cooldown_multiplier", "add") => {
                    self.player.cooldown_multiplier += modifier.value_per_level;
                }
                ("cooldown_multiplier", "multiply") => {
                    self.player.cooldown_multiplier *= modifier.value_per_level;
                }
                ("xp_multiplier", "add") => {
                    self.player.xp_multiplier += modifier.value_per_level;
                }
                ("xp_multiplier", "multiply") => {
                    self.player.xp_multiplier *= modifier.value_per_level;
                }
                ("damage_reduction", "add") => {
                    self.player.damage_reduction += modifier.value_per_level;
                }
                ("damage_reduction", "multiply") => {
                    self.player.damage_reduction *= modifier.value_per_level;
                }
                ("projectile_size", "add") => {
                    self.player.projectile_size_multiplier += modifier.value_per_level;
                }
                ("projectile_size", "multiply") => {
                    self.player.projectile_size_multiplier *= modifier.value_per_level;
                }
                ("effect_duration", "add") => {
                    self.player.effect_duration_multiplier += modifier.value_per_level;
                }
                ("effect_duration", "multiply") => {
                    self.player.effect_duration_multiplier *= modifier.value_per_level;
                }
                _ => {}
            }
        }
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
        let mut position = self.player.position + offset;
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
            evolutions: Vec::new(),
            tags,
            open_evolution_paths: self.open_evolution_paths(),
        }
    }

    fn open_evolution_paths(&self) -> Vec<String> {
        self.content
            .evolutions
            .values()
            .filter(|evolution| {
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

fn xp_required(level: u32) -> f32 {
    (12.0 + level as f32 * 8.0 + (level as f32).powf(1.35) * 5.0).floor()
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
            damage_reduction: 0.0,
            projectile_size_multiplier: 1.0,
            effect_duration_multiplier: 1.0,
        }
    }
}

#[derive(Debug, Clone)]
struct WeaponState {
    id: String,
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
            tags: definition.tags.clone(),
            projectile_count_base: definition.base_stats.projectile_count,
            projectile_count_bonus_levels: definition.scaling.projectile_count_bonus_levels.clone(),
            damage_per_level: definition.scaling.damage_per_level,
            cooldown_multiplier_per_level: definition.scaling.cooldown_multiplier_per_level,
            range_per_level: definition.scaling.range_per_level,
            area_per_level: definition.scaling.area_per_level,
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

#[derive(Debug, Clone)]
struct PassiveState {
    id: String,
    level: u32,
    max_level: u32,
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
    is_boss: bool,
    is_elite: bool,
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
        )
    }

    fn from_boss_definition(entity_id: u64, position: Vec2, definition: &BossDefinition) -> Self {
        Self::from_stats(
            entity_id,
            position,
            definition.id(),
            &definition.common.stats,
            8.0,
            true,
        )
    }

    fn from_stats(
        entity_id: u64,
        position: Vec2,
        id: &str,
        stats: &EnemyStatsDefinition,
        threat: f32,
        is_boss: bool,
    ) -> Self {
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
            behavior: EnemyBehavior::Chase,
            is_boss,
            is_elite: false,
        }
    }
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
    fn can_run_from_disk_content_pack() {
        let content = ContentPack::load_from_dir("../../content/base_demo")
            .expect("base_demo content should load from disk");
        assert!(content.evolutions.contains_key("rainbow-candy-meteor"));
        assert!(content.events.contains_key("rainbow-candy-rush"));
        assert_eq!(content.object_count(), 21);
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
}
