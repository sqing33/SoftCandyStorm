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
            BotKind::Random => self.random_movement(snapshot),
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

    fn random_movement(&mut self, snapshot: &RunSnapshot) -> Vec2 {
        let action = self.rng.range_usize(9);
        let speed = if snapshot.map.map_id == "jelly-platform" {
            0.72
        } else {
            1.0
        };
        discrete_direction(action) * speed
    }

    fn route_movement(&mut self, snapshot: &RunSnapshot) -> Vec2 {
        self.route_angle = (self.route_angle + 0.045) % std::f32::consts::TAU;
        let radius_x = snapshot.map.width * 0.28;
        let radius_y = snapshot.map.height * 0.24;
        let route_speed = if snapshot.map.map_id == "cotton-cloud-pasture" {
            0.58
        } else {
            0.65
        };
        let target = Vec2::new(
            self.route_angle.cos() * radius_x,
            self.route_angle.sin() * radius_y,
        );
        let route = (target - snapshot.player.position).normalized_or_zero() * route_speed;
        if snapshot.map.map_id == "soda-creek" && snapshot.time_seconds >= 212.0 {
            let avoidance = avoid_enemies(snapshot, 128.0, 8);
            if avoidance.length_squared() > 0.0 {
                return (route + avoidance * 0.20).normalized_or_zero() * route_speed;
            }
        } else if snapshot.map.map_id == "caramel-workshop" && snapshot.time_seconds >= 210.0 {
            let enemy_avoidance = avoid_enemies(snapshot, 128.0, 8);
            let hazard_avoidance = avoid_hazards(snapshot, 96.0, 6);
            let boss_avoidance = snapshot
                .boss
                .as_ref()
                .map(|boss| {
                    let away = snapshot.player.position - boss.position;
                    if away.length() < 168.0 {
                        away.normalized_or_zero()
                    } else {
                        Vec2::ZERO
                    }
                })
                .unwrap_or(Vec2::ZERO);
            if enemy_avoidance.length_squared() > 0.0
                || hazard_avoidance.length_squared() > 0.0
                || boss_avoidance.length_squared() > 0.0
            {
                return (route
                    + enemy_avoidance * 0.24
                    + hazard_avoidance * 0.38
                    + boss_avoidance * 0.34)
                    .normalized_or_zero()
                    * route_speed;
            }
        } else if snapshot.map.map_id == "cracked-star-jar" && snapshot.time_seconds >= 210.0 {
            let avoidance = avoid_enemies(snapshot, 132.0, 8);
            if avoidance.length_squared() > 0.0 {
                return (route + avoidance * 0.18).normalized_or_zero() * route_speed;
            }
        }

        route
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
                status_effects: Vec::new(),
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
            active_event_effects: Vec::new(),
            metrics_partial: game_core::MetricsPartial::default(),
        }
    }

    fn jelly_snapshot() -> RunSnapshot {
        let mut snapshot = empty_snapshot();
        snapshot.map.map_id = "jelly-platform".to_string();
        snapshot
    }

    fn caramel_snapshot() -> RunSnapshot {
        let mut snapshot = empty_snapshot();
        snapshot.map.map_id = "caramel-workshop".to_string();
        snapshot
    }

    fn cotton_snapshot() -> RunSnapshot {
        let mut snapshot = empty_snapshot();
        snapshot.map.map_id = "cotton-cloud-pasture".to_string();
        snapshot
    }

    fn chaser_enemy(entity_id: u64, position: Vec2, threat: f32) -> game_core::EnemySnapshot {
        game_core::EnemySnapshot {
            entity_id,
            enemy_id: "test-jelly".to_string(),
            position,
            velocity: Vec2::ZERO,
            health: 100.0,
            max_health: 100.0,
            radius: 24.0,
            threat,
            behavior: game_core::EnemyBehavior::Chase,
            is_boss: false,
            is_elite: false,
        }
    }

    fn active_hazard(
        position: Vec2,
        radius: f32,
        slow_multiplier: f32,
        damage_per_second: f32,
    ) -> game_core::HazardSnapshot {
        game_core::HazardSnapshot {
            position,
            radius,
            slow_multiplier,
            damage_per_second,
            remaining_seconds: 3.0,
        }
    }

    fn xp_pickup(entity_id: u64, position: Vec2) -> game_core::PickupSnapshot {
        game_core::PickupSnapshot {
            entity_id,
            pickup_type: game_core::PickupType::Xp,
            position,
            value: 1.0,
            radius: 8.0,
        }
    }

    fn assert_close(left: f32, right: f32) {
        assert!(
            (left - right).abs() < 0.001,
            "expected {left} to be close to {right}"
        );
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
    fn random_bot_uses_jelly_platform_speed_cap() {
        let default_snapshot = empty_snapshot();
        let jelly_snapshot = jelly_snapshot();
        let mut default_bot = BotController::new(BotKind::Random, 7);
        let mut jelly_bot = BotController::new(BotKind::Random, 7);

        let mut found_non_zero_action = false;
        for _ in 0..16 {
            let default_movement = default_bot.next_action(&default_snapshot).movement;
            let jelly_movement = jelly_bot.next_action(&jelly_snapshot).movement;
            if default_movement.length_squared() > 0.0 {
                assert_close(jelly_movement.x, default_movement.x * 0.72);
                assert_close(jelly_movement.y, default_movement.y * 0.72);
                found_non_zero_action = true;
                break;
            }
        }

        assert!(found_non_zero_action);
    }

    #[test]
    fn greedy_uses_map_specific_pickup_weight() {
        let mut default_snapshot = empty_snapshot();
        default_snapshot
            .visible_pickups
            .push(xp_pickup(1, Vec2::new(100.0, 0.0)));

        let mut jelly_snapshot = default_snapshot.clone();
        jelly_snapshot.map.map_id = "jelly-platform".to_string();
        let mut caramel_snapshot = default_snapshot.clone();
        caramel_snapshot.map.map_id = "caramel-workshop".to_string();
        let mut cotton_snapshot = default_snapshot.clone();
        cotton_snapshot.map.map_id = "cotton-cloud-pasture".to_string();
        let mut soda_snapshot = default_snapshot.clone();
        soda_snapshot.map.map_id = "soda-creek".to_string();

        assert_close(greedy_movement(&default_snapshot).x, 0.30);
        assert_close(greedy_movement(&jelly_snapshot).x, 0.06);
        assert_close(greedy_movement(&caramel_snapshot).x, 0.42);
        assert_close(greedy_movement(&cotton_snapshot).x, 0.36);
        assert_close(greedy_movement(&soda_snapshot).x, 0.55);
    }

    #[test]
    fn coward_uses_jelly_platform_weaker_avoidance() {
        let mut default_snapshot = empty_snapshot();
        default_snapshot
            .visible_enemies
            .push(chaser_enemy(1, Vec2::new(50.0, 0.0), 4.0));

        let mut jelly_snapshot = default_snapshot.clone();
        jelly_snapshot.map.map_id = "jelly-platform".to_string();
        let mut soda_snapshot = default_snapshot.clone();
        soda_snapshot.map.map_id = "soda-creek".to_string();

        assert_close(coward_movement(&default_snapshot).x, -0.72);
        assert_close(coward_movement(&jelly_snapshot).x, -0.16);
        assert_close(coward_movement(&soda_snapshot).x, -1.0);
    }

    #[test]
    fn kite_uses_jelly_platform_pickup_weight() {
        let mut default_snapshot = empty_snapshot();
        default_snapshot
            .visible_pickups
            .push(xp_pickup(1, Vec2::new(100.0, 0.0)));

        let mut jelly_snapshot = default_snapshot.clone();
        jelly_snapshot.map.map_id = "jelly-platform".to_string();
        let mut soda_snapshot = default_snapshot.clone();
        soda_snapshot.map.map_id = "soda-creek".to_string();

        assert_close(kite_movement(&default_snapshot).x, 0.35);
        assert_close(kite_movement(&jelly_snapshot).x, 0.12);
        assert_close(kite_movement(&soda_snapshot).x, 0.45);
    }

    #[test]
    fn coward_uses_cotton_cloud_hazard_avoidance() {
        let mut snapshot = cotton_snapshot();
        snapshot
            .active_hazards
            .push(active_hazard(Vec2::new(50.0, 0.0), 84.0, 0.78, 0.0));

        assert_close(coward_movement(&snapshot).x, -0.30);
    }

    #[test]
    fn tank_uses_cotton_pickup_weight() {
        let mut snapshot = cotton_snapshot();
        snapshot
            .visible_pickups
            .push(xp_pickup(1, Vec2::new(100.0, 0.0)));

        assert_close(tank_movement(&snapshot).x, 0.04);
    }

    #[test]
    fn tank_uses_frosting_pickup_weight() {
        let mut snapshot = empty_snapshot();
        snapshot
            .visible_pickups
            .push(xp_pickup(1, Vec2::new(100.0, 0.0)));

        assert_close(tank_movement(&snapshot).x, 0.07);
    }

    #[test]
    fn tank_uses_caramel_hazard_avoidance() {
        let mut snapshot = caramel_snapshot();
        snapshot
            .active_hazards
            .push(active_hazard(Vec2::new(40.0, 0.0), 64.0, 0.52, 13.0));

        let mut bot = BotController::new(BotKind::Tank, 3);
        let movement = bot.next_action(&snapshot).movement;

        assert_close(movement.x, -0.48);
        assert!(movement.length() <= 0.50);
    }

    #[test]
    fn boss_hunter_uses_caramel_furnace_spacing() {
        let mut caramel_boss = caramel_snapshot();
        caramel_boss.boss = Some(game_core::BossSnapshot {
            entity_id: 99,
            boss_id: "caramel-furnace".to_string(),
            health: 1000.0,
            max_health: 1000.0,
            position: Vec2::new(110.0, 0.0),
        });
        let mut generic_boss = caramel_boss.clone();
        generic_boss.boss.as_mut().unwrap().boss_id = "runaway-sugar-mixer".to_string();

        let mut caramel_bot = BotController::new(BotKind::BossHunter, 5);
        let mut generic_bot = BotController::new(BotKind::BossHunter, 5);

        assert!(caramel_bot.next_action(&caramel_boss).movement.x < 0.0);
        assert_eq!(generic_bot.next_action(&generic_boss).movement, Vec2::ZERO);
    }

    #[test]
    fn boss_hunter_uses_cotton_cloud_pickup_weight() {
        let mut snapshot = cotton_snapshot();
        snapshot
            .visible_pickups
            .push(xp_pickup(1, Vec2::new(100.0, 0.0)));

        assert_close(boss_hunter_movement(&snapshot).x, 0.119);
    }

    #[test]
    fn boss_hunter_uses_cotton_boss_close_spacing() {
        let mut cotton_boss = cotton_snapshot();
        cotton_boss.boss = Some(game_core::BossSnapshot {
            entity_id: 99,
            boss_id: "giant-cotton-clump".to_string(),
            health: 1000.0,
            max_health: 1000.0,
            position: Vec2::new(52.0, 0.0),
        });
        let mut generic_boss = cotton_boss.clone();
        generic_boss.boss.as_mut().unwrap().boss_id = "runaway-sugar-mixer".to_string();

        let mut cotton_bot = BotController::new(BotKind::BossHunter, 5);
        let mut generic_bot = BotController::new(BotKind::BossHunter, 5);

        assert_eq!(cotton_bot.next_action(&cotton_boss).movement, Vec2::ZERO);
        assert!(generic_bot.next_action(&generic_boss).movement.x < 0.0);
    }

    #[test]
    fn zone_control_uses_caramel_hazard_avoidance() {
        let mut snapshot = caramel_snapshot();
        snapshot
            .active_hazards
            .push(active_hazard(Vec2::new(60.0, 0.0), 64.0, 0.52, 13.0));

        let mut bot = BotController::new(BotKind::ZoneControl, 4);
        let movement = bot.next_action(&snapshot).movement;

        assert_close(movement.x, -0.31);
        assert!(movement.length() <= 0.32);
    }

    #[test]
    fn route_bot_outputs_normalized_action() {
        let mut bot = BotController::new(BotKind::Route, 2);
        let action = bot.next_action(&empty_snapshot());
        assert!(action.movement.length() <= 1.0 + f32::EPSILON);
    }

    #[test]
    fn route_uses_cotton_cloud_speed_cap() {
        let mut bot = BotController::new(BotKind::Route, 2);
        let action = bot.next_action(&cotton_snapshot());
        assert_close(action.movement.length(), 0.58);
    }

    #[test]
    fn route_uses_soda_boss_window_emergency_avoidance() {
        let mut snapshot = empty_snapshot();
        snapshot.map.map_id = "soda-creek".to_string();
        snapshot.time_seconds = 214.0;
        snapshot.visible_enemies.push(game_core::EnemySnapshot {
            entity_id: 99,
            enemy_id: "soda-fountain-dragon".to_string(),
            position: Vec2::new(20.0, 0.0),
            velocity: Vec2::ZERO,
            health: 1000.0,
            max_health: 1000.0,
            radius: 64.0,
            threat: 8.0,
            behavior: game_core::EnemyBehavior::Chase,
            is_boss: true,
            is_elite: false,
        });

        let mut pre_window = snapshot.clone();
        pre_window.time_seconds = 211.9;

        let mut pre_bot = BotController::new(BotKind::Route, 2);
        let mut boss_window_bot = BotController::new(BotKind::Route, 2);

        assert!(pre_bot.next_action(&pre_window).movement.x > 0.0);
        assert!(boss_window_bot.next_action(&snapshot).movement.x < 0.0);
    }

    #[test]
    fn route_uses_caramel_boss_window_emergency_avoidance() {
        let mut snapshot = caramel_snapshot();
        snapshot.time_seconds = 210.0;
        snapshot
            .visible_enemies
            .push(chaser_enemy(1, Vec2::new(20.0, 0.0), 8.0));
        snapshot
            .active_hazards
            .push(active_hazard(Vec2::new(20.0, 0.0), 64.0, 0.52, 13.0));
        snapshot.boss = Some(game_core::BossSnapshot {
            entity_id: 99,
            boss_id: "caramel-furnace".to_string(),
            health: 1000.0,
            max_health: 1000.0,
            position: Vec2::new(40.0, 0.0),
        });

        let mut pre_window = snapshot.clone();
        pre_window.time_seconds = 209.9;

        let mut pre_bot = BotController::new(BotKind::Route, 2);
        let mut boss_window_bot = BotController::new(BotKind::Route, 2);

        assert!(pre_bot.next_action(&pre_window).movement.x > 0.0);
        assert!(boss_window_bot.next_action(&snapshot).movement.x < 0.0);
    }

    #[test]
    fn route_uses_cracked_star_boss_window_emergency_avoidance() {
        let mut snapshot = empty_snapshot();
        snapshot.map.map_id = "cracked-star-jar".to_string();
        snapshot.time_seconds = 210.0;
        snapshot.visible_enemies.push(game_core::EnemySnapshot {
            entity_id: 99,
            enemy_id: "cracked-star-jar-core".to_string(),
            position: Vec2::new(20.0, 0.0),
            velocity: Vec2::ZERO,
            health: 1000.0,
            max_health: 1000.0,
            radius: 64.0,
            threat: 8.0,
            behavior: game_core::EnemyBehavior::Chase,
            is_boss: true,
            is_elite: false,
        });

        let mut pre_window = snapshot.clone();
        pre_window.time_seconds = 209.9;

        let mut pre_bot = BotController::new(BotKind::Route, 2);
        let mut boss_window_bot = BotController::new(BotKind::Route, 2);

        assert!(pre_bot.next_action(&pre_window).movement.x > 0.0);
        assert!(boss_window_bot.next_action(&snapshot).movement.x < 0.0);
    }

    #[test]
    fn boss_hunter_keeps_spacing_from_close_boss() {
        let mut snapshot = empty_snapshot();
        snapshot.boss = Some(game_core::BossSnapshot {
            entity_id: 99,
            boss_id: "caramel-furnace".to_string(),
            health: 1000.0,
            max_health: 1000.0,
            position: Vec2::new(28.0, 0.0),
        });

        let mut bot = BotController::new(BotKind::BossHunter, 5);
        let action = bot.next_action(&snapshot);

        assert!(action.movement.x < 0.0);
        assert!(action.movement.length() <= 1.0 + f32::EPSILON);
    }

    #[test]
    fn boss_hunter_advances_toward_distant_boss() {
        let mut snapshot = empty_snapshot();
        snapshot.boss = Some(game_core::BossSnapshot {
            entity_id: 99,
            boss_id: "soda-fountain-dragon".to_string(),
            health: 1000.0,
            max_health: 1000.0,
            position: Vec2::new(220.0, 0.0),
        });

        let mut bot = BotController::new(BotKind::BossHunter, 5);
        let action = bot.next_action(&snapshot);

        assert!(action.movement.x > 0.0);
        assert!(action.movement.length() <= 1.0 + f32::EPSILON);
    }

    #[test]
    fn boss_hunter_uses_wider_avoidance_on_final_map() {
        let mut final_map = empty_snapshot();
        final_map.map.map_id = "cracked-star-jar".to_string();
        final_map.boss = Some(game_core::BossSnapshot {
            entity_id: 99,
            boss_id: "cracked-star-jar-core".to_string(),
            health: 1000.0,
            max_health: 1000.0,
            position: Vec2::new(100.0, 0.0),
        });

        let mut default_map = final_map.clone();
        default_map.map.map_id = "soda-creek".to_string();

        let mut final_bot = BotController::new(BotKind::BossHunter, 5);
        let mut default_bot = BotController::new(BotKind::BossHunter, 5);

        assert!(final_bot.next_action(&final_map).movement.x < 0.0);
        assert_eq!(default_bot.next_action(&default_map).movement, Vec2::ZERO);
    }

    #[test]
    fn boss_hunter_uses_soda_dragon_specific_spacing() {
        let mut soda_map = empty_snapshot();
        soda_map.map.map_id = "soda-creek".to_string();
        soda_map.boss = Some(game_core::BossSnapshot {
            entity_id: 99,
            boss_id: "soda-fountain-dragon".to_string(),
            health: 1000.0,
            max_health: 1000.0,
            position: Vec2::new(82.0, 0.0),
        });

        let mut generic_map = soda_map.clone();
        generic_map.boss.as_mut().unwrap().boss_id = "caramel-furnace".to_string();

        let mut soda_bot = BotController::new(BotKind::BossHunter, 5);
        let mut generic_bot = BotController::new(BotKind::BossHunter, 5);

        assert_eq!(soda_bot.next_action(&soda_map).movement, Vec2::ZERO);
        assert!(generic_bot.next_action(&generic_map).movement.x < 0.0);
    }

    #[test]
    fn tank_prioritizes_survival_after_mid_skill_calibration() {
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
        assert_eq!(bot.next_action(&snapshot).upgrade_choice, Some(1));

        snapshot.upgrade_options[1].id = "candy-heart".to_string();
        snapshot.upgrade_options[1].tags = vec!["health".to_string()];
        assert_eq!(bot.next_action(&snapshot).upgrade_choice, Some(0));

        snapshot.player.health = 30.0;
        assert_eq!(bot.next_action(&snapshot).upgrade_choice, Some(1));
    }

    #[test]
    fn tank_uses_lower_final_map_retreat_threshold() {
        let mut snapshot = empty_snapshot();
        snapshot.map.map_id = "cracked-star-jar".to_string();
        snapshot.player.health = 35.0;
        snapshot.visible_enemies.push(game_core::EnemySnapshot {
            entity_id: 7,
            enemy_id: "cracked-star-jar-core".to_string(),
            position: Vec2::new(40.0, 0.0),
            velocity: Vec2::ZERO,
            health: 1000.0,
            max_health: 1000.0,
            radius: 64.0,
            threat: 8.0,
            behavior: game_core::EnemyBehavior::Chase,
            is_boss: true,
            is_elite: false,
        });

        let mut stable_snapshot = snapshot.clone();
        stable_snapshot.player.health = 35.0;
        let mut danger_snapshot = snapshot;
        danger_snapshot.player.health = 25.0;

        let mut stable_bot = BotController::new(BotKind::Tank, 3);
        let mut danger_bot = BotController::new(BotKind::Tank, 3);

        assert_eq!(
            stable_bot.next_action(&stable_snapshot).movement,
            Vec2::ZERO
        );
        assert!(danger_bot.next_action(&danger_snapshot).movement.x < 0.0);
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

    #[test]
    fn route_finishes_basic_weapon_before_mobility_bias() {
        let mut snapshot = empty_snapshot();
        snapshot.build.weapons.push(game_core::BuildItemSnapshot {
            id: "rainbow-candy-shot".to_string(),
            level: 3,
        });
        snapshot.upgrade_options = vec![
            game_core::UpgradeOptionSnapshot {
                id: "bubble-shoes".to_string(),
                name: "泡泡鞋".to_string(),
                tags: vec!["mobility".to_string()],
                description: "提升移动速度。".to_string(),
            },
            game_core::UpgradeOptionSnapshot {
                id: "rainbow-candy-shot-level-4".to_string(),
                name: "彩虹糖弹 Lv4".to_string(),
                tags: vec!["projectile".to_string()],
                description: "提升彩虹糖弹。".to_string(),
            },
        ];

        let mut bot = BotController::new(BotKind::Route, 6);
        assert_eq!(bot.next_action(&snapshot).upgrade_choice, Some(1));

        snapshot.build.weapons[0].level = 4;
        assert_eq!(bot.next_action(&snapshot).upgrade_choice, Some(0));
    }

    #[test]
    fn kite_prefers_mint_but_falls_back_to_existing_upgrade() {
        let mut snapshot = empty_snapshot();
        snapshot.upgrade_options = vec![
            game_core::UpgradeOptionSnapshot {
                id: "rainbow-candy-shot-level-2".to_string(),
                name: "彩虹糖弹 Lv2".to_string(),
                tags: vec!["projectile".to_string()],
                description: "提升彩虹糖弹。".to_string(),
            },
            game_core::UpgradeOptionSnapshot {
                id: "caramel-sticky-ground".to_string(),
                name: "焦糖黏地".to_string(),
                tags: vec!["control".to_string()],
                description: "放置焦糖地面。".to_string(),
            },
        ];

        let mut bot = BotController::new(BotKind::Kite, 7);
        assert_eq!(bot.next_action(&snapshot).upgrade_choice, Some(0));

        snapshot.upgrade_options[1].id = "mint-cyclone".to_string();
        snapshot.upgrade_options[1].tags = vec!["control".to_string()];
        assert_eq!(bot.next_action(&snapshot).upgrade_choice, Some(1));
    }

    #[test]
    fn frosting_coward_uses_learning_upgrade_bias() {
        let mut snapshot = empty_snapshot();
        snapshot.upgrade_options = vec![
            game_core::UpgradeOptionSnapshot {
                id: "rainbow-candy-shot-level-2".to_string(),
                name: "彩虹糖弹 Lv2".to_string(),
                tags: vec!["projectile".to_string()],
                description: "提升彩虹糖弹。".to_string(),
            },
            game_core::UpgradeOptionSnapshot {
                id: "mint-cyclone".to_string(),
                name: "薄荷旋风".to_string(),
                tags: vec!["control".to_string()],
                description: "薄荷风围绕守护员旋转。".to_string(),
            },
            game_core::UpgradeOptionSnapshot {
                id: "big-candy-jar".to_string(),
                name: "大号糖罐".to_string(),
                tags: vec!["defense".to_string(), "health".to_string()],
                description: "提升最大生命。".to_string(),
            },
        ];

        let mut bot = BotController::new(BotKind::Coward, 8);
        assert_eq!(bot.next_action(&snapshot).upgrade_choice, Some(1));
    }

    #[test]
    fn frosting_greedy_delays_weapon_level_upgrade() {
        let mut snapshot = empty_snapshot();
        snapshot.upgrade_options = vec![
            game_core::UpgradeOptionSnapshot {
                id: "rainbow-candy-shot-level-2".to_string(),
                name: "彩虹糖弹 Lv2".to_string(),
                tags: vec!["projectile".to_string()],
                description: "提升彩虹糖弹。".to_string(),
            },
            game_core::UpgradeOptionSnapshot {
                id: "caramel-sticky-ground".to_string(),
                name: "焦糖黏地".to_string(),
                tags: vec!["slow".to_string(), "zone".to_string()],
                description: "在地面留下焦糖区域。".to_string(),
            },
            game_core::UpgradeOptionSnapshot {
                id: "frosting-gloves".to_string(),
                name: "糖霜手套".to_string(),
                tags: vec!["projectile".to_string(), "size".to_string()],
                description: "增加投射物大小。".to_string(),
            },
        ];

        let mut bot = BotController::new(BotKind::Greedy, 9);
        assert_eq!(bot.next_action(&snapshot).upgrade_choice, Some(2));
    }

    #[test]
    fn zone_control_uses_final_map_light_avoidance() {
        let mut snapshot = empty_snapshot();
        snapshot.map.map_id = "cracked-star-jar".to_string();
        snapshot.visible_enemies.push(game_core::EnemySnapshot {
            entity_id: 7,
            enemy_id: "cracked-star-jar-core".to_string(),
            position: Vec2::new(40.0, 0.0),
            velocity: Vec2::ZERO,
            health: 1000.0,
            max_health: 1000.0,
            radius: 64.0,
            threat: 8.0,
            behavior: game_core::EnemyBehavior::Chase,
            is_boss: true,
            is_elite: false,
        });

        let mut bot = BotController::new(BotKind::ZoneControl, 3);
        let movement = bot.next_action(&snapshot).movement;

        assert!(movement.x < 0.0);
        assert!(movement.length() <= 0.35 + f32::EPSILON);
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

    let defense_threshold = if snapshot.map.map_id == "cracked-star-jar" && kind == BotKind::Tank {
        0.35
    } else {
        defense_threshold(kind)
    };

    if health_ratio < defense_threshold {
        if let Some(index) = find_option(snapshot, &["big-candy-jar", "defense", "health"]) {
            return index;
        }
    }

    if kind == BotKind::ZoneControl && weapon_level(snapshot, "rainbow-candy-shot") < 3 {
        if let Some(index) = find_option(snapshot, &["rainbow-candy-shot"]) {
            return index;
        }
    }

    if kind == BotKind::Route && weapon_level(snapshot, "rainbow-candy-shot") < 4 {
        if let Some(index) = find_option(snapshot, &["rainbow-candy-shot"]) {
            return index;
        }
    }

    if snapshot.map.map_id == "frosting-grassland" {
        if let Some(index) = frosting_grassland_learning_upgrade_choice(kind, snapshot) {
            return index;
        }
    }

    for priority in upgrade_priorities(kind) {
        if let Some(index) = find_option(snapshot, &[*priority]) {
            return index;
        }
    }

    fallback_upgrade_choice(kind, snapshot.upgrade_options.len())
}

fn frosting_grassland_learning_upgrade_choice(
    kind: BotKind,
    snapshot: &RunSnapshot,
) -> Option<usize> {
    let priorities = match kind {
        BotKind::Coward => &[
            "jellybean-brooch",
            "taffy-trail-map",
            "wafer-focus-charm",
            "frosting-gloves",
            "sour-tuner",
            "bubble-shoes",
            "mint-cyclone",
            "marshmallow-shield",
        ][..],
        BotKind::Greedy => &[
            "frosting-gloves",
            "taffy-trail-map",
            "jellybean-brooch",
            "sour-tuner",
            "bubble-shoes",
            "star-spoon",
            "candy-crystal-lens",
        ][..],
        _ => return None,
    };

    for priority in priorities {
        if let Some(index) = find_option(snapshot, &[*priority]) {
            return Some(index);
        }
    }

    snapshot
        .upgrade_options
        .iter()
        .position(|option| !option.id.contains("-level-"))
}

fn defense_threshold(kind: BotKind) -> f32 {
    match kind {
        BotKind::Tank => 0.35,
        BotKind::Coward => 0.62,
        BotKind::Greedy => 0.38,
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
            "pudding-turret",
            "soda-bubble-pop",
            "sour-tuner",
            "rainbow-candy-shot",
            "cream-clockwork",
            "bubble-shoes",
        ],
        BotKind::Kite => &[
            "bubble-shoes",
            "soda-bubble-pop",
            "sour-plum-spray",
            "mint-cyclone",
            "star-spoon",
            "cream-clockwork",
        ],
        BotKind::Tank => &[
            "big-candy-jar",
            "nonstick-apron",
            "cream-clockwork",
            "star-spoon",
            "rainbow-candy-shot",
            "bubble-shoes",
        ],
        BotKind::BossHunter => &[
            "star-sugar-ray",
            "candy-crystal-lance",
            "cream-clockwork",
            "bubble-shoes",
        ],
        BotKind::ZoneControl => &[
            "caramel-sticky-ground",
            "sour-plum-spray",
            "sour-tuner",
            "mint-cyclone",
            "bubble-shoes",
            "star-spoon",
        ],
        BotKind::Route => &[
            "bubble-shoes",
            "star-spoon",
            "rainbow-candy-shot",
            "sour-tuner",
            "soda-bubble-pop",
            "pudding-turret",
        ],
    }
}

fn fallback_upgrade_choice(kind: BotKind, option_count: usize) -> usize {
    let preferred = match kind {
        BotKind::Greedy | BotKind::BossHunter => 1,
        BotKind::Kite => 0,
        BotKind::Tank | BotKind::ZoneControl | BotKind::Route => 2,
        BotKind::Idle | BotKind::Random | BotKind::Coward => 0,
    };
    preferred.min(option_count.saturating_sub(1))
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
    let pickup_weight = if snapshot.map.map_id == "jelly-platform" {
        0.06
    } else if snapshot.map.map_id == "caramel-workshop" {
        0.42
    } else if snapshot.map.map_id == "cotton-cloud-pasture" {
        0.36
    } else if snapshot.map.map_id == "frosting-grassland" {
        0.30
    } else {
        0.55
    };
    greedy_movement_with_avoidance(snapshot, 18.0, pickup_weight)
}

fn greedy_movement_with_avoidance(
    snapshot: &RunSnapshot,
    avoidance_radius: f32,
    pickup_weight: f32,
) -> Vec2 {
    if let Some(enemy) = snapshot.visible_enemies.first() {
        let away = snapshot.player.position - enemy.position;
        if away.length() < avoidance_radius {
            return away.normalized_or_zero();
        }
    }

    best_pickup_direction(snapshot).unwrap_or(Vec2::ZERO) * pickup_weight
}

fn coward_movement(snapshot: &RunSnapshot) -> Vec2 {
    let is_jelly_platform = snapshot.map.map_id == "jelly-platform";
    let is_cotton_cloud = snapshot.map.map_id == "cotton-cloud-pasture";
    let is_frosting_grassland = snapshot.map.map_id == "frosting-grassland";
    let avoidance_radius = if is_jelly_platform {
        58.0
    } else if is_frosting_grassland {
        280.0
    } else {
        340.0
    };
    let safe_pickup_radius = if is_jelly_platform {
        60.0
    } else if is_frosting_grassland {
        150.0
    } else {
        220.0
    };
    let nearest_enemy_pickup_radius = if is_jelly_platform {
        60.0
    } else if is_frosting_grassland {
        150.0
    } else {
        210.0
    };
    let avoidance_limit = if is_jelly_platform {
        6
    } else if is_frosting_grassland {
        10
    } else {
        14
    };
    let avoidance = avoid_enemies(snapshot, avoidance_radius, avoidance_limit);
    if avoidance.length_squared() > 0.0 {
        let speed = if is_jelly_platform {
            0.16
        } else if is_frosting_grassland {
            0.72
        } else {
            1.0
        };
        return avoidance.normalized_or_zero() * speed;
    }

    if is_cotton_cloud {
        let hazard_avoidance = avoid_hazards(snapshot, 76.0, 6);
        if hazard_avoidance.length_squared() > 0.0 {
            return hazard_avoidance.normalized_or_zero() * 0.30;
        }
    }

    let movement = safe_pickup_direction(snapshot, safe_pickup_radius)
        .or_else(|| {
            best_pickup_direction(snapshot)
                .filter(|_| nearest_enemy_distance(snapshot) > nearest_enemy_pickup_radius)
        })
        .unwrap_or(Vec2::ZERO);
    if is_jelly_platform {
        movement * 0.16
    } else if is_frosting_grassland {
        movement * 0.52
    } else {
        movement
    }
}

fn kite_movement(snapshot: &RunSnapshot) -> Vec2 {
    let avoidance_radius = if snapshot.map.map_id == "cracked-star-jar" {
        55.0
    } else if snapshot.map.map_id == "frosting-grassland" {
        24.0
    } else {
        36.0
    };
    let avoidance = avoid_enemies(snapshot, avoidance_radius, 3);
    let pickup_direction = best_pickup_direction(snapshot).unwrap_or(Vec2::ZERO);

    if avoidance.length_squared() > 0.0 {
        let speed = if snapshot.map.map_id == "jelly-platform" {
            0.32
        } else {
            1.0
        };
        return (avoidance.normalized_or_zero() * 0.05 + pickup_direction).normalized_or_zero()
            * speed;
    }

    if pickup_direction.length_squared() > 0.0 {
        let pickup_weight = if snapshot.map.map_id == "jelly-platform" {
            0.12
        } else if snapshot.map.map_id == "frosting-grassland" {
            0.35
        } else {
            0.45
        };
        pickup_direction * pickup_weight
    } else {
        Vec2::new(1.0, 0.0)
    }
}

fn tank_movement(snapshot: &RunSnapshot) -> Vec2 {
    let health_ratio = snapshot.player.health / snapshot.player.max_health;
    let retreat_threshold = if snapshot.map.map_id == "cracked-star-jar" {
        0.30
    } else if snapshot.map.map_id == "caramel-workshop" {
        0.24
    } else if snapshot.map.map_id == "cotton-cloud-pasture" {
        0.10
    } else {
        0.14
    };
    if health_ratio < retreat_threshold {
        let enemy_avoidance = avoid_enemies(snapshot, 120.0, 10);
        let hazard_avoidance = if snapshot.map.map_id == "caramel-workshop" {
            avoid_hazards(snapshot, 96.0, 6) * 1.35
        } else {
            Vec2::ZERO
        };
        let avoidance = enemy_avoidance + hazard_avoidance;
        if avoidance.length_squared() > 0.0 {
            return avoidance.normalized_or_zero();
        }
    }

    if snapshot.map.map_id == "caramel-workshop" {
        let hazard_avoidance = avoid_hazards(snapshot, 88.0, 6);
        if hazard_avoidance.length_squared() > 0.0 {
            let pickup = best_pickup_direction(snapshot).unwrap_or(Vec2::ZERO) * 0.02;
            return (hazard_avoidance.normalized_or_zero() * 0.22 + pickup).normalized_or_zero()
                * 0.48;
        }
    }

    let pickup_weight = if snapshot.map.map_id == "cracked-star-jar" {
        0.25
    } else if snapshot.map.map_id == "caramel-workshop" {
        0.09
    } else if snapshot.map.map_id == "cotton-cloud-pasture" {
        0.04
    } else if snapshot.map.map_id == "frosting-grassland" {
        0.07
    } else {
        0.11
    };
    best_pickup_direction(snapshot).unwrap_or(Vec2::ZERO) * pickup_weight
}

fn boss_hunter_movement(snapshot: &RunSnapshot) -> Vec2 {
    if let Some(boss) = &snapshot.boss {
        let to_boss = boss.position - snapshot.player.position;
        let boss_distance = to_boss.length();
        let boss_direction = to_boss.normalized_or_zero();
        let (retreat_distance, chase_distance) = if snapshot.map.map_id == "frosting-grassland" {
            (30.0, 34.0)
        } else if boss.boss_id == "soda-fountain-dragon" {
            (80.0, 119.0)
        } else if boss.boss_id == "caramel-furnace" {
            (120.0, 174.0)
        } else if boss.boss_id == "giant-cotton-clump" {
            (48.0, 74.0)
        } else if snapshot.map.map_id == "cracked-star-jar" {
            (126.0, 166.0)
        } else {
            (86.0, 124.0)
        };
        let spacing = if boss_distance < retreat_distance {
            boss_direction * -1.0
        } else if boss_distance > chase_distance {
            boss_direction
        } else {
            Vec2::ZERO
        };
        let avoidance_radius = if snapshot.map.map_id == "cracked-star-jar" {
            95.0
        } else if boss.boss_id == "caramel-furnace" {
            104.0
        } else if boss.boss_id == "giant-cotton-clump" {
            8.0
        } else if snapshot.map.map_id == "frosting-grassland" {
            10.0
        } else {
            24.0
        };
        let avoidance_weight = if snapshot.map.map_id == "cracked-star-jar" {
            0.34
        } else if boss.boss_id == "caramel-furnace" {
            0.25
        } else if boss.boss_id == "giant-cotton-clump" {
            0.0
        } else if snapshot.map.map_id == "frosting-grassland" {
            0.0
        } else {
            0.15
        };
        let avoidance = avoid_enemies(snapshot, avoidance_radius, 6);
        let hazard_avoidance = if boss.boss_id == "caramel-furnace" {
            avoid_hazards(snapshot, 116.0, 6).normalized_or_zero() * 0.48
        } else {
            Vec2::ZERO
        };
        return (spacing * 1.15
            + avoidance.normalized_or_zero() * avoidance_weight
            + hazard_avoidance)
            .normalized_or_zero();
    }

    let health_ratio = if snapshot.player.max_health > 0.0 {
        snapshot.player.health / snapshot.player.max_health
    } else {
        1.0
    };
    let pickup_weight = if snapshot.map.map_id == "cotton-cloud-pasture" {
        0.119
    } else if snapshot.map.map_id == "frosting-grassland"
        && snapshot.time_seconds > 240.0
        && health_ratio > 0.70
    {
        0.0
    } else {
        0.12
    };
    let avoidance = avoid_enemies(snapshot, 34.0, 3).normalized_or_zero() * 0.25;
    let pickup = best_pickup_direction(snapshot).unwrap_or(Vec2::ZERO);
    (avoidance + pickup).normalized_or_zero() * pickup_weight
}

fn zone_control_movement(snapshot: &RunSnapshot) -> Vec2 {
    if snapshot.map.map_id == "cracked-star-jar" {
        let avoidance = avoid_enemies(snapshot, 70.0, 6);
        if avoidance.length_squared() > 0.0 {
            let pickup = best_pickup_direction(snapshot).unwrap_or(Vec2::ZERO) * 0.03;
            return (avoidance.normalized_or_zero() * 0.09 + pickup).normalized_or_zero() * 0.15;
        }

        return best_pickup_direction(snapshot).unwrap_or(Vec2::ZERO) * 0.07;
    }

    if snapshot.map.map_id == "caramel-workshop" {
        let enemy_avoidance = avoid_enemies(snapshot, 54.0, 5).normalized_or_zero() * 0.09;
        let hazard_avoidance = avoid_hazards(snapshot, 108.0, 6).normalized_or_zero() * 0.27;
        if enemy_avoidance.length_squared() > 0.0 || hazard_avoidance.length_squared() > 0.0 {
            let pickup = best_pickup_direction(snapshot).unwrap_or(Vec2::ZERO) * 0.04;
            return (enemy_avoidance + hazard_avoidance + pickup).normalized_or_zero() * 0.31;
        }

        return best_pickup_direction(snapshot).unwrap_or(Vec2::ZERO) * 0.07;
    }

    let avoidance = avoid_enemies(snapshot, 38.0, 4);
    if avoidance.length_squared() > 0.0 {
        return avoidance.normalized_or_zero() * 0.05;
    }

    best_pickup_direction(snapshot).unwrap_or(Vec2::ZERO) * 0.07
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

fn avoid_hazards(snapshot: &RunSnapshot, padding_radius: f32, limit: usize) -> Vec2 {
    let mut avoidance = Vec2::ZERO;
    for hazard in snapshot.active_hazards.iter().take(limit) {
        let away = snapshot.player.position - hazard.position;
        let distance = away.length();
        let danger_radius = hazard.radius + padding_radius;
        if distance < danger_radius {
            let damage_pressure = hazard.damage_per_second.max(0.0) / 12.0;
            let slow_pressure = (1.0 - hazard.slow_multiplier).max(0.0) * 1.2;
            let severity = (damage_pressure + slow_pressure).max(0.45);
            let weight = ((danger_radius - distance) / danger_radius).max(0.05) * severity;
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
