use game_core::{PlayerAction, RunSnapshot, Vec2};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BotKind {
    Idle,
    Random,
    Coward,
    Greedy,
    Kite,
    Tank,
    BossHunter,
    ZoneControl,
    Route,
}

impl BotKind {
    pub fn parse(value: &str) -> Option<Self> {
        match value {
            "idle" => Some(Self::Idle),
            "random" => Some(Self::Random),
            "coward" => Some(Self::Coward),
            "greedy" | "greedy-xp" => Some(Self::Greedy),
            "kite" => Some(Self::Kite),
            "tank" => Some(Self::Tank),
            "boss-hunter" | "bosshunter" => Some(Self::BossHunter),
            "zone-control" | "zone" => Some(Self::ZoneControl),
            "route" => Some(Self::Route),
            _ => None,
        }
    }

    pub fn as_str(self) -> &'static str {
        match self {
            Self::Idle => "idle",
            Self::Random => "random",
            Self::Coward => "coward",
            Self::Greedy => "greedy",
            Self::Kite => "kite",
            Self::Tank => "tank",
            Self::BossHunter => "boss-hunter",
            Self::ZoneControl => "zone-control",
            Self::Route => "route",
        }
    }

    pub fn all_names() -> &'static str {
        "idle|random|coward|greedy|kite|tank|boss-hunter|zone-control|route"
    }
}

#[derive(Debug, Clone)]
pub struct BotController {
    kind: BotKind,
    rng: PolicyRng,
    route_angle: f32,
}

impl BotController {
    pub fn new(kind: BotKind, seed: u64) -> Self {
        Self {
            kind,
            rng: PolicyRng::new(seed ^ 0x05ee_db07_u64),
            route_angle: 0.0,
        }
    }

    pub fn next_action(&mut self, snapshot: &RunSnapshot) -> PlayerAction {
        if !snapshot.upgrade_options.is_empty() {
            return PlayerAction {
                movement: Vec2::ZERO,
                upgrade_choice: Some(upgrade_choice_for_bot(self.kind, snapshot, &mut self.rng)),
            };
        }

        let movement = match self.kind {
            BotKind::Idle => Vec2::ZERO,
            BotKind::Random => self.random_movement(),
            BotKind::Coward => coward_movement(snapshot),
            BotKind::Greedy => greedy_movement(snapshot),
            BotKind::Kite => kite_movement(snapshot),
            BotKind::Tank => tank_movement(snapshot),
            BotKind::BossHunter => boss_hunter_movement(snapshot),
            BotKind::ZoneControl => zone_control_movement(snapshot),
            BotKind::Route => self.route_movement(snapshot),
        };

        PlayerAction {
            movement,
            upgrade_choice: None,
        }
    }

    fn random_movement(&mut self) -> Vec2 {
        let action = self.rng.range_usize(9);
        discrete_direction(action)
    }

    fn route_movement(&mut self, snapshot: &RunSnapshot) -> Vec2 {
        self.route_angle = (self.route_angle + 0.045) % std::f32::consts::TAU;
        let radius_x = snapshot.map.width * 0.28;
        let radius_y = snapshot.map.height * 0.24;
        let target = Vec2::new(
            self.route_angle.cos() * radius_x,
            self.route_angle.sin() * radius_y,
        );
        (target - snapshot.player.position).normalized_or_zero() * 0.88
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn empty_snapshot() -> RunSnapshot {
        RunSnapshot {
            time_seconds: 0.0,
            remaining_seconds: 600.0,
            player: game_core::PlayerSnapshot {
                position: Vec2::ZERO,
                velocity: Vec2::ZERO,
                health: 100.0,
                max_health: 100.0,
                level: 1,
                xp: 0.0,
                xp_to_next_level: 25.0,
                move_speed: 180.0,
                pickup_radius: 72.0,
                damage_multiplier: 1.0,
                cooldown_multiplier: 1.0,
            },
            visible_enemies: Vec::new(),
            visible_pickups: Vec::new(),
            visible_projectiles: Vec::new(),
            active_hazards: Vec::new(),
            boss: None,
            upgrade_options: Vec::new(),
            build: game_core::BuildSnapshot::default(),
            map: game_core::MapSnapshot {
                map_id: "frosting-grassland".to_string(),
                width: 2600.0,
                height: 1700.0,
            },
            metrics_partial: game_core::MetricsPartial::default(),
        }
    }

    #[test]
    fn idle_bot_stands_still() {
        let mut bot = BotController::new(BotKind::Idle, 1);
        let action = bot.next_action(&empty_snapshot());
        assert_eq!(action.movement, Vec2::ZERO);
        assert_eq!(action.upgrade_choice, None);
    }

    #[test]
    fn random_bot_is_seed_deterministic() {
        let mut left = BotController::new(BotKind::Random, 7);
        let mut right = BotController::new(BotKind::Random, 7);
        let snapshot = empty_snapshot();

        for _ in 0..16 {
            assert_eq!(
                left.next_action(&snapshot).movement,
                right.next_action(&snapshot).movement
            );
        }
    }

    #[test]
    fn route_bot_outputs_normalized_action() {
        let mut bot = BotController::new(BotKind::Route, 2);
        let action = bot.next_action(&empty_snapshot());
        assert!(action.movement.length() <= 1.0 + f32::EPSILON);
    }

    #[test]
    fn tank_prioritizes_cooldown_until_health_is_low() {
        let mut snapshot = empty_snapshot();
        snapshot.upgrade_options = vec![
            game_core::UpgradeOptionSnapshot {
                id: "cream-clockwork".to_string(),
                name: "奶油发条".to_string(),
                tags: vec!["cooldown".to_string()],
                description: "缩短武器冷却。".to_string(),
            },
            game_core::UpgradeOptionSnapshot {
                id: "big-candy-jar".to_string(),
                name: "大号糖罐".to_string(),
                tags: vec!["defense".to_string(), "health".to_string()],
                description: "提升最大生命。".to_string(),
            },
        ];

        let mut bot = BotController::new(BotKind::Tank, 3);
        assert_eq!(bot.next_action(&snapshot).upgrade_choice, Some(0));

        snapshot.player.health = 40.0;
        assert_eq!(bot.next_action(&snapshot).upgrade_choice, Some(1));
    }

    #[test]
    fn zone_control_unlocks_basic_weapon_before_pickup_bias() {
        let mut snapshot = empty_snapshot();
        snapshot.build.weapons.push(game_core::BuildItemSnapshot {
            id: "rainbow-candy-shot".to_string(),
            level: 2,
        });
        snapshot.upgrade_options = vec![
            game_core::UpgradeOptionSnapshot {
                id: "star-spoon".to_string(),
                name: "星星勺子".to_string(),
                tags: vec!["pickup".to_string()],
                description: "扩大糖晶拾取范围。".to_string(),
            },
            game_core::UpgradeOptionSnapshot {
                id: "rainbow-candy-shot-level-3".to_string(),
                name: "彩虹糖弹 Lv3".to_string(),
                tags: vec!["projectile".to_string()],
                description: "提升彩虹糖弹。".to_string(),
            },
        ];

        let mut bot = BotController::new(BotKind::ZoneControl, 4);
        assert_eq!(bot.next_action(&snapshot).upgrade_choice, Some(1));

        snapshot.build.weapons[0].level = 3;
        assert_eq!(bot.next_action(&snapshot).upgrade_choice, Some(0));
    }
}

fn upgrade_choice_for_bot(kind: BotKind, snapshot: &RunSnapshot, rng: &mut PolicyRng) -> usize {
    if kind == BotKind::Random {
        return rng.range_usize(snapshot.upgrade_options.len());
    }

    let health_ratio = if snapshot.player.max_health > 0.0 {
        snapshot.player.health / snapshot.player.max_health
    } else {
        1.0
    };

    if health_ratio < defense_threshold(kind) {
        if let Some(index) = find_option(snapshot, &["big-candy-jar", "defense", "health"]) {
            return index;
        }
    }

    if kind == BotKind::ZoneControl && weapon_level(snapshot, "rainbow-candy-shot") < 3 {
        if let Some(index) = find_option(snapshot, &["rainbow-candy-shot"]) {
            return index;
        }
    }

    for priority in upgrade_priorities(kind) {
        if let Some(index) = find_option(snapshot, &[*priority]) {
            return index;
        }
    }

    0
}

fn defense_threshold(kind: BotKind) -> f32 {
    match kind {
        BotKind::Tank => 0.55,
        BotKind::Coward => 0.62,
        BotKind::Greedy => 0.55,
        BotKind::Kite => 0.0,
        BotKind::BossHunter => 0.55,
        BotKind::ZoneControl => 0.0,
        BotKind::Route => 0.45,
        BotKind::Idle | BotKind::Random => 0.0,
    }
}

fn upgrade_priorities(kind: BotKind) -> &'static [&'static str] {
    match kind {
        BotKind::Idle => &["big-candy-jar", "rainbow-candy-shot"],
        BotKind::Random => &[],
        BotKind::Coward => &[
            "bubble-shoes",
            "big-candy-jar",
            "rainbow-candy-shot",
            "cream-clockwork",
            "star-spoon",
        ],
        BotKind::Greedy => &[
            "star-spoon",
            "candy-crystal-lens",
            "rainbow-candy-shot",
            "cream-clockwork",
            "bubble-shoes",
        ],
        BotKind::Kite => &[
            "bubble-shoes",
            "rainbow-candy-shot",
            "star-spoon",
            "cream-clockwork",
            "big-candy-jar",
        ],
        BotKind::Tank => &[
            "cream-clockwork",
            "big-candy-jar",
            "rainbow-candy-shot",
            "bubble-shoes",
            "star-spoon",
        ],
        BotKind::BossHunter => &[
            "rainbow-candy-shot",
            "cream-clockwork",
            "bubble-shoes",
            "big-candy-jar",
            "star-spoon",
        ],
        BotKind::ZoneControl => &[
            "star-spoon",
            "rainbow-candy-shot",
            "cream-clockwork",
            "bubble-shoes",
        ],
        BotKind::Route => &["bubble-shoes", "star-spoon", "cream-clockwork"],
    }
}

fn find_option(snapshot: &RunSnapshot, needles: &[&str]) -> Option<usize> {
    snapshot.upgrade_options.iter().position(|option| {
        needles.iter().any(|needle| {
            option.id.contains(needle)
                || option.tags.iter().any(|tag| tag.contains(needle))
                || option.description.contains(needle)
        })
    })
}

fn weapon_level(snapshot: &RunSnapshot, weapon_id: &str) -> u32 {
    snapshot
        .build
        .weapons
        .iter()
        .find(|weapon| weapon.id == weapon_id)
        .map(|weapon| weapon.level)
        .unwrap_or(0)
}

fn greedy_movement(snapshot: &RunSnapshot) -> Vec2 {
    if let Some(enemy) = snapshot.visible_enemies.first() {
        let away = snapshot.player.position - enemy.position;
        if away.length() < 95.0 {
            return away.normalized_or_zero();
        }
    }

    best_pickup_direction(snapshot).unwrap_or(Vec2::ZERO)
}

fn coward_movement(snapshot: &RunSnapshot) -> Vec2 {
    let avoidance = avoid_enemies(snapshot, 340.0, 14);
    if avoidance.length_squared() > 0.0 {
        return avoidance.normalized_or_zero();
    }

    safe_pickup_direction(snapshot, 220.0)
        .or_else(|| {
            best_pickup_direction(snapshot).filter(|_| nearest_enemy_distance(snapshot) > 210.0)
        })
        .unwrap_or(Vec2::ZERO)
}

fn kite_movement(snapshot: &RunSnapshot) -> Vec2 {
    let avoidance = avoid_enemies(snapshot, 68.0, 3);
    let pickup_direction = best_pickup_direction(snapshot).unwrap_or(Vec2::ZERO);

    if avoidance.length_squared() > 0.0 {
        return (avoidance.normalized_or_zero() * 0.13 + pickup_direction).normalized_or_zero();
    }

    if pickup_direction.length_squared() > 0.0 {
        pickup_direction
    } else {
        Vec2::new(1.0, 0.0)
    }
}

fn tank_movement(snapshot: &RunSnapshot) -> Vec2 {
    let health_ratio = snapshot.player.health / snapshot.player.max_health;
    if health_ratio < 0.70 {
        let avoidance = avoid_enemies(snapshot, 250.0, 10);
        if avoidance.length_squared() > 0.0 {
            return avoidance.normalized_or_zero();
        }
    }

    best_pickup_direction(snapshot).unwrap_or(Vec2::ZERO) * 0.8
}

fn boss_hunter_movement(snapshot: &RunSnapshot) -> Vec2 {
    if let Some(boss) = &snapshot.boss {
        let to_boss = (boss.position - snapshot.player.position).normalized_or_zero();
        let avoidance = avoid_enemies(snapshot, 70.0, 5);
        return (to_boss * 1.45 + avoidance.normalized_or_zero() * 0.35).normalized_or_zero();
    }

    greedy_movement(snapshot)
}

fn zone_control_movement(snapshot: &RunSnapshot) -> Vec2 {
    let avoidance = avoid_enemies(snapshot, 70.0, 4);
    if avoidance.length_squared() > 0.0 {
        return avoidance.normalized_or_zero() * 0.13;
    }

    best_pickup_direction(snapshot).unwrap_or(Vec2::ZERO) * 0.40
}

fn best_pickup_direction(snapshot: &RunSnapshot) -> Option<Vec2> {
    snapshot
        .visible_pickups
        .first()
        .map(|pickup| (pickup.position - snapshot.player.position).normalized_or_zero())
}

fn safe_pickup_direction(snapshot: &RunSnapshot, danger_radius: f32) -> Option<Vec2> {
    snapshot.visible_pickups.iter().find_map(|pickup| {
        let pickup_is_safe = snapshot
            .visible_enemies
            .iter()
            .all(|enemy| enemy.position.distance(pickup.position) > danger_radius);
        pickup_is_safe.then(|| (pickup.position - snapshot.player.position).normalized_or_zero())
    })
}

fn nearest_enemy_distance(snapshot: &RunSnapshot) -> f32 {
    snapshot
        .visible_enemies
        .first()
        .map(|enemy| snapshot.player.position.distance(enemy.position))
        .unwrap_or(f32::INFINITY)
}

fn avoid_enemies(snapshot: &RunSnapshot, radius: f32, limit: usize) -> Vec2 {
    let mut avoidance = Vec2::ZERO;
    for enemy in snapshot.visible_enemies.iter().take(limit) {
        let away = snapshot.player.position - enemy.position;
        let distance = away.length();
        if distance < radius {
            let weight = ((radius - distance) / radius).max(0.05) * enemy.threat.max(1.0);
            avoidance += away.normalized_or_zero() * weight;
        }
    }
    avoidance
}

fn discrete_direction(action: usize) -> Vec2 {
    match action {
        0 => Vec2::ZERO,
        1 => Vec2::new(0.0, 1.0),
        2 => Vec2::new(1.0, 1.0).normalized_or_zero(),
        3 => Vec2::new(1.0, 0.0),
        4 => Vec2::new(1.0, -1.0).normalized_or_zero(),
        5 => Vec2::new(0.0, -1.0),
        6 => Vec2::new(-1.0, -1.0).normalized_or_zero(),
        7 => Vec2::new(-1.0, 0.0),
        _ => Vec2::new(-1.0, 1.0).normalized_or_zero(),
    }
}

#[derive(Debug, Clone)]
struct PolicyRng {
    state: u64,
}

impl PolicyRng {
    fn new(seed: u64) -> Self {
        Self {
            state: seed ^ 0x9e37_79b9_7f4a_7c15,
        }
    }

    fn next_u32(&mut self) -> u32 {
        self.state = self
            .state
            .wrapping_mul(6_364_136_223_846_793_005)
            .wrapping_add(1_442_695_040_888_963_407);
        (self.state >> 32) as u32
    }

    fn range_usize(&mut self, upper_exclusive: usize) -> usize {
        if upper_exclusive == 0 {
            0
        } else {
            (self.next_u32() as usize) % upper_exclusive
        }
    }
}
