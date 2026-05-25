use serde::Deserialize;
use std::collections::{BTreeMap, HashSet};
use std::fmt;
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Default)]
pub struct ContentPack {
    pub characters: BTreeMap<String, CharacterDefinition>,
    pub weapons: BTreeMap<String, WeaponDefinition>,
    pub passives: BTreeMap<String, PassiveDefinition>,
    pub evolutions: BTreeMap<String, EvolutionDefinition>,
    pub enemies: BTreeMap<String, EnemyDefinition>,
    pub bosses: BTreeMap<String, BossDefinition>,
    pub waves: BTreeMap<String, WaveDefinition>,
    pub maps: BTreeMap<String, MapDefinition>,
    pub events: BTreeMap<String, EventDefinition>,
}

impl ContentPack {
    pub fn base_demo() -> Self {
        let mut pack = Self::default();

        pack.characters.insert(
            "jar-keeper".to_string(),
            CharacterDefinition {
                id: "jar-keeper".to_string(),
                name: "糖罐守护员".to_string(),
                version: 1,
                rarity: "common".to_string(),
                tags: vec!["balanced".to_string(), "beginner".to_string()],
                description: "新上任的糖罐守护员。".to_string(),
                base_stats: CharacterBaseStats {
                    max_health: 120.0,
                    move_speed: 180.0,
                    pickup_radius: 72.0,
                    damage_multiplier: 1.0,
                    cooldown_multiplier: 1.0,
                    xp_multiplier: 1.0,
                    regen_per_second: 0.0,
                },
                initial_loadout: InitialLoadoutDefinition {
                    weapons: vec!["rainbow-candy-shot".to_string()],
                    passives: Vec::new(),
                },
                trait_definition: Some(CharacterTraitDefinition {
                    id: "sweet-starter".to_string(),
                    description: "每 5 级额外获得少量糖晶。".to_string(),
                    rules: Vec::new(),
                }),
                visual_description: "戴小糖罐帽的圆润守护员，颜色以奶白和粉色为主。".to_string(),
                sfx_description: "轻快脚步和糖罐轻响。".to_string(),
                unlock: UnlockDefinition {
                    unlock_type: "default".to_string(),
                },
            },
        );

        pack.weapons.insert(
            "rainbow-candy-shot".to_string(),
            WeaponDefinition {
                id: "rainbow-candy-shot".to_string(),
                name: "彩虹糖弹".to_string(),
                version: 1,
                rarity: "common".to_string(),
                weapon_type: "projectile".to_string(),
                tags: vec![
                    "projectile".to_string(),
                    "starter".to_string(),
                    "single-target".to_string(),
                ],
                description: "向最近敌人发射彩色糖弹。".to_string(),
                targeting: TargetingDefinition {
                    mode: "nearest_enemy".to_string(),
                    range: 420.0,
                },
                base_stats: WeaponBaseStats {
                    damage: 14.0,
                    cooldown_ms: 620.0,
                    projectile_speed: 560.0,
                    projectile_count: 1,
                    pierce: 1,
                    area_radius: 14.0,
                    duration_ms: 0.0,
                },
                scaling: WeaponScaling {
                    max_level: 5,
                    damage_per_level: 6.0,
                    cooldown_multiplier_per_level: 0.92,
                    range_per_level: 18.0,
                    area_per_level: 1.0,
                    projectile_count_bonus_levels: vec![3, 5],
                },
                balance_budget: WeaponBalanceBudget {
                    role: "starter".to_string(),
                    single_target_dps: 20.0,
                    group_dps: 12.0,
                    performance_cost: "low".to_string(),
                },
                visual_description: "小颗圆形彩虹糖弹，命中时弹出糖屑。".to_string(),
                sfx_description: "清脆 pop 声。".to_string(),
                unlock: UnlockDefinition {
                    unlock_type: "default".to_string(),
                },
            },
        );

        pack.evolutions.insert(
            "rainbow-candy-meteor".to_string(),
            EvolutionDefinition {
                id: "rainbow-candy-meteor".to_string(),
                name: "彩虹糖流星雨".to_string(),
                version: 1,
                rarity: "epic".to_string(),
                tags: vec![
                    "projectile".to_string(),
                    "aoe".to_string(),
                    "evolution".to_string(),
                ],
                description: "彩虹糖弹进化为周期性流星雨。".to_string(),
                requirements: EvolutionRequirementsDefinition {
                    weapon: ContentLevelRequirementDefinition {
                        id: "rainbow-candy-shot".to_string(),
                        min_level: 5,
                    },
                    passive: Some(ContentLevelRequirementDefinition {
                        id: "candy-crystal-lens".to_string(),
                        min_level: 3,
                    }),
                    trigger: "boss_chest".to_string(),
                },
                replaces_weapon: "rainbow-candy-shot".to_string(),
                weapon_definition: EvolutionWeaponDefinition {
                    weapon_type: "burst".to_string(),
                    targeting: TargetingDefinition {
                        mode: "random_enemy".to_string(),
                        range: 620.0,
                    },
                    base_stats: EvolutionWeaponBaseStats {
                        damage: 42.0,
                        cooldown_ms: 900.0,
                        projectile_speed: None,
                        projectile_count: 8,
                        pierce: None,
                        area_radius: 42.0,
                        duration_ms: None,
                    },
                },
                visual_description: "多颗彩虹糖从天空坠落，形成小型糖果爆炸。".to_string(),
                sfx_description: "连续 sparkle pop。".to_string(),
                unlock: UnlockDefinition {
                    unlock_type: "discover".to_string(),
                },
            },
        );

        for passive in [
            passive_add(
                "big-candy-jar",
                "大号糖罐",
                &["defense", "health"],
                "提升最大生命。",
                "max_health",
                22.0,
            ),
            passive_add(
                "star-spoon",
                "星星勺子",
                &["economy", "pickup"],
                "扩大糖晶拾取范围。",
                "pickup_radius",
                18.0,
            ),
            passive_add(
                "bubble-shoes",
                "泡泡鞋",
                &["mobility"],
                "提升移动速度。",
                "move_speed",
                10.0,
            ),
            passive_add(
                "candy-crystal-lens",
                "糖晶放大镜",
                &["economy", "xp"],
                "提升糖晶经验收益。",
                "xp_multiplier",
                0.12,
            ),
            passive_multiply(
                "cream-clockwork",
                "奶油发条",
                &["cooldown"],
                "缩短武器冷却。",
                "cooldown_multiplier",
                0.92,
            ),
        ] {
            pack.passives.insert(passive.id.clone(), passive);
        }

        for enemy in [
            enemy_definition(
                "bouncy-gummy",
                "蹦蹦软糖",
                "gummy",
                &["basic", "swarm"],
                18.0,
                60.0,
                4.5,
                13.0,
                2.0,
                1.0,
            ),
            enemy_definition(
                "sour-gummy",
                "酸酸软糖",
                "gummy",
                &["fast", "sour"],
                12.0,
                92.0,
                3.5,
                11.0,
                3.0,
                1.4,
            ),
            enemy_definition(
                "sandwich-cookie-creep",
                "夹心饼怪",
                "cookie",
                &["tank", "blocker"],
                65.0,
                38.0,
                8.0,
                18.0,
                6.0,
                2.4,
            ),
            enemy_definition(
                "caramel-slime",
                "焦糖史莱姆",
                "caramel",
                &["control", "sticky"],
                35.0,
                45.0,
                4.0,
                15.0,
                4.0,
                2.0,
            ),
        ] {
            pack.enemies.insert(enemy.common.id.clone(), enemy);
        }

        pack.bosses.insert(
            "runaway-sugar-mixer".to_string(),
            BossDefinition {
                common: EnemyCommonDefinition {
                    id: "runaway-sugar-mixer".to_string(),
                    name: "暴走搅糖机".to_string(),
                    version: 1,
                    rarity: "boss".to_string(),
                    tags: vec!["boss".to_string(), "dash".to_string(), "summon".to_string()],
                    description: "失控的搅糖机器，会一边冲撞一边甩出软糖。".to_string(),
                    stats: EnemyStatsDefinition {
                        health: 900.0,
                        move_speed: 38.0,
                        contact_damage_per_second: 20.0,
                        radius: 48.0,
                        xp_value: 80.0,
                        score_value: 500,
                    },
                    counterplay: "冲撞前会出现红色预警线，冲撞后短暂硬直。".to_string(),
                    visual_description: "圆滚滚的粉色搅糖机，带夸张搅拌臂。".to_string(),
                    sfx_description: "机械搅拌声和糖浆飞溅声。".to_string(),
                },
                phases: vec![
                    BossPhaseDefinition {
                        hp_threshold: 1.0,
                        abilities: vec![
                            "dash_charge".to_string(),
                            "summon_bouncy_gummy".to_string(),
                        ],
                    },
                    BossPhaseDefinition {
                        hp_threshold: 0.45,
                        abilities: vec![
                            "dash_charge".to_string(),
                            "sugar_splash".to_string(),
                            "summon_bouncy_gummy".to_string(),
                        ],
                    },
                ],
            },
        );

        pack.maps.insert(
            "frosting-grassland".to_string(),
            MapDefinition {
                id: "frosting-grassland".to_string(),
                name: "糖霜草地".to_string(),
                version: 1,
                tags: vec!["beginner".to_string(), "open".to_string()],
                description: "覆盖糖霜的开阔草地，新手守护员第一次面对软糖风暴的地方。".to_string(),
                size: MapSizeDefinition {
                    width: 2600.0,
                    height: 1700.0,
                },
                bounds: BoundsDefinition {
                    bounds_type: "rectangle".to_string(),
                },
                spawn_rules: SpawnRulesDefinition {
                    mode: "around_player".to_string(),
                    min_distance: 320.0,
                    max_distance: 520.0,
                },
                hazards: Vec::new(),
                visual_description: "奶白糖霜草地、棒棒糖路标、饼干小路。".to_string(),
                music_theme: "bright_xylophone".to_string(),
            },
        );

        pack.events.insert(
            "rainbow-candy-rush".to_string(),
            EventDefinition {
                id: "rainbow-candy-rush".to_string(),
                name: "彩虹糖潮".to_string(),
                version: 1,
                rarity: "rare".to_string(),
                tags: vec![
                    "event".to_string(),
                    "risk-reward".to_string(),
                    "xp".to_string(),
                ],
                description: "短时间内糖晶掉落增加，但敌人生成也会加快。".to_string(),
                trigger: EventTriggerDefinition {
                    trigger_type: "time_window".to_string(),
                    start_second: Some(180.0),
                    end_second: Some(480.0),
                    chance: Some(0.08),
                },
                effects: vec![
                    EventEffectDefinition {
                        effect_type: "xp_multiplier".to_string(),
                        value: 1.4,
                        duration_seconds: Some(25.0),
                    },
                    EventEffectDefinition {
                        effect_type: "spawn_rate_multiplier".to_string(),
                        value: 1.25,
                        duration_seconds: Some(25.0),
                    },
                ],
                visual_description: "天空落下彩虹糖晶，地面出现亮色糖光。".to_string(),
                sfx_description: "连续亮晶晶铃声。".to_string(),
            },
        );

        pack.waves.insert(
            "frosting-grassland-standard".to_string(),
            WaveDefinition {
                id: "frosting-grassland-standard".to_string(),
                name: "糖霜草地标准波次".to_string(),
                version: 1,
                map_id: "frosting-grassland".to_string(),
                duration_seconds: 600.0,
                segments: base_demo_wave_segments(),
                boss_events: vec![BossEventDefinition {
                    time_second: 210.0,
                    boss_id: "runaway-sugar-mixer".to_string(),
                }],
                pressure_budget: PressureBudgetDefinition {
                    early: "low".to_string(),
                    middle: "medium".to_string(),
                    late: "high".to_string(),
                },
            },
        );

        pack
    }

    pub fn load_from_dir(path: impl AsRef<Path>) -> Result<Self, ContentError> {
        let path = path.as_ref();
        let pack = Self {
            characters: load_category(&path.join("characters"))?,
            weapons: load_category(&path.join("weapons"))?,
            passives: load_category(&path.join("passives"))?,
            evolutions: load_category(&path.join("evolutions"))?,
            enemies: load_category(&path.join("enemies"))?,
            bosses: load_category(&path.join("bosses"))?,
            waves: load_category(&path.join("waves"))?,
            maps: load_category(&path.join("maps"))?,
            events: load_category(&path.join("events"))?,
        };
        pack.validate()?;
        Ok(pack)
    }

    pub fn validate(&self) -> Result<ValidationReport, ContentError> {
        let mut errors = Vec::new();
        let mut warnings = Vec::new();

        validate_non_empty("characters", &self.characters, &mut errors);
        validate_non_empty("weapons", &self.weapons, &mut errors);
        validate_non_empty("enemies", &self.enemies, &mut errors);
        validate_non_empty("waves", &self.waves, &mut errors);
        validate_non_empty("maps", &self.maps, &mut errors);

        validate_ids("characters", self.characters.keys(), &mut errors);
        validate_ids("weapons", self.weapons.keys(), &mut errors);
        validate_ids("passives", self.passives.keys(), &mut errors);
        validate_ids("evolutions", self.evolutions.keys(), &mut errors);
        validate_ids("enemies", self.enemies.keys(), &mut errors);
        validate_ids("bosses", self.bosses.keys(), &mut errors);
        validate_ids("waves", self.waves.keys(), &mut errors);
        validate_ids("maps", self.maps.keys(), &mut errors);
        validate_ids("events", self.events.keys(), &mut errors);

        for character in self.characters.values() {
            validate_common(
                CommonValidation {
                    category: "character",
                    id: &character.id,
                    version: character.version,
                    rarity: &character.rarity,
                    tags: &character.tags,
                    description: &character.description,
                    visual_description: &character.visual_description,
                    sfx_description: &character.sfx_description,
                },
                &mut errors,
            );
            validate_positive("max_health", character.base_stats.max_health, &mut errors);
            validate_positive("move_speed", character.base_stats.move_speed, &mut errors);
            validate_positive(
                "pickup_radius",
                character.base_stats.pickup_radius,
                &mut errors,
            );
            validate_finite(
                "damage_multiplier",
                character.base_stats.damage_multiplier,
                &mut errors,
            );
            validate_finite(
                "cooldown_multiplier",
                character.base_stats.cooldown_multiplier,
                &mut errors,
            );
            validate_finite(
                "xp_multiplier",
                character.base_stats.xp_multiplier,
                &mut errors,
            );
            for weapon_id in &character.initial_loadout.weapons {
                if !self.weapons.contains_key(weapon_id) {
                    errors.push(format!(
                        "character `{}` references missing weapon `{}`",
                        character.id, weapon_id
                    ));
                }
            }
            for passive_id in &character.initial_loadout.passives {
                if !self.passives.contains_key(passive_id) {
                    errors.push(format!(
                        "character `{}` references missing passive `{}`",
                        character.id, passive_id
                    ));
                }
            }
        }

        for weapon in self.weapons.values() {
            validate_common(
                CommonValidation {
                    category: "weapon",
                    id: &weapon.id,
                    version: weapon.version,
                    rarity: &weapon.rarity,
                    tags: &weapon.tags,
                    description: &weapon.description,
                    visual_description: &weapon.visual_description,
                    sfx_description: &weapon.sfx_description,
                },
                &mut errors,
            );
            validate_allowed(
                "weapon.type",
                &weapon.weapon_type,
                &[
                    "projectile",
                    "orbit",
                    "burst",
                    "zone",
                    "summon",
                    "beam",
                    "special",
                ],
                &mut errors,
            );
            validate_allowed(
                "weapon.targeting.mode",
                &weapon.targeting.mode,
                &[
                    "nearest_enemy",
                    "highest_health_enemy",
                    "boss_priority",
                    "random_enemy",
                    "random_direction",
                    "movement_direction",
                    "self_centered",
                    "ground_near_player",
                ],
                &mut errors,
            );
            validate_positive(
                "weapon.targeting.range",
                weapon.targeting.range,
                &mut errors,
            );
            validate_positive("weapon.damage", weapon.base_stats.damage, &mut errors);
            validate_positive(
                "weapon.cooldown_ms",
                weapon.base_stats.cooldown_ms,
                &mut errors,
            );
            validate_positive(
                "weapon.projectile_speed",
                weapon.base_stats.projectile_speed,
                &mut errors,
            );
            validate_positive(
                "weapon.projectile_count",
                weapon.base_stats.projectile_count as f32,
                &mut errors,
            );
            validate_positive(
                "weapon.pierce",
                weapon.base_stats.pierce as f32,
                &mut errors,
            );
            validate_positive(
                "weapon.area_radius",
                weapon.base_stats.area_radius,
                &mut errors,
            );
            validate_positive(
                "weapon.scaling.max_level",
                weapon.scaling.max_level as f32,
                &mut errors,
            );
            validate_finite(
                "weapon.scaling.cooldown_multiplier_per_level",
                weapon.scaling.cooldown_multiplier_per_level,
                &mut errors,
            );
            if weapon.scaling.cooldown_multiplier_per_level <= 0.0 {
                errors.push(format!(
                    "weapon `{}` has non-positive cooldown_multiplier_per_level",
                    weapon.id
                ));
            }

            let cooldown_seconds = weapon.base_stats.cooldown_ms / 1000.0;
            if cooldown_seconds > 0.0 {
                let dps = weapon.base_stats.damage * weapon.base_stats.projectile_count as f32
                    / cooldown_seconds;
                if dps > weapon.balance_budget.single_target_dps * 1.5 {
                    warnings.push(format!(
                        "weapon `{}` theoretical dps {:.2} exceeds budget {:.2}",
                        weapon.id, dps, weapon.balance_budget.single_target_dps
                    ));
                }
            }
        }

        for passive in self.passives.values() {
            validate_common(
                CommonValidation {
                    category: "passive",
                    id: &passive.id,
                    version: passive.version,
                    rarity: &passive.rarity,
                    tags: &passive.tags,
                    description: &passive.description,
                    visual_description: &passive.visual_description,
                    sfx_description: &passive.sfx_description,
                },
                &mut errors,
            );
            validate_positive("passive.max_level", passive.max_level as f32, &mut errors);
            if passive.stat_modifiers.is_empty() {
                errors.push(format!("passive `{}` has empty stat_modifiers", passive.id));
            }
            for modifier in &passive.stat_modifiers {
                validate_allowed(
                    "passive.stat",
                    &modifier.stat,
                    &[
                        "max_health",
                        "move_speed",
                        "pickup_radius",
                        "damage_multiplier",
                        "cooldown_multiplier",
                        "xp_multiplier",
                        "regen_per_second",
                        "damage_reduction",
                        "projectile_size",
                        "effect_duration",
                    ],
                    &mut errors,
                );
                validate_allowed(
                    "passive.mode",
                    &modifier.mode,
                    &["add", "multiply", "set_min", "set_max"],
                    &mut errors,
                );
                validate_finite(
                    "passive.value_per_level",
                    modifier.value_per_level,
                    &mut errors,
                );
            }
        }

        for evolution in self.evolutions.values() {
            validate_common(
                CommonValidation {
                    category: "evolution",
                    id: &evolution.id,
                    version: evolution.version,
                    rarity: &evolution.rarity,
                    tags: &evolution.tags,
                    description: &evolution.description,
                    visual_description: &evolution.visual_description,
                    sfx_description: &evolution.sfx_description,
                },
                &mut errors,
            );
            validate_content_level_requirement(
                "evolution.weapon",
                &evolution.id,
                &evolution.requirements.weapon,
                self.weapons
                    .get(&evolution.requirements.weapon.id)
                    .map(|weapon| weapon.scaling.max_level),
                &mut errors,
            );
            if let Some(passive_requirement) = &evolution.requirements.passive {
                validate_content_level_requirement(
                    "evolution.passive",
                    &evolution.id,
                    passive_requirement,
                    self.passives
                        .get(&passive_requirement.id)
                        .map(|passive| passive.max_level),
                    &mut errors,
                );
            }
            validate_allowed(
                "evolution.trigger",
                &evolution.requirements.trigger,
                &[
                    "boss_chest",
                    "storm_chest",
                    "boss_defeat",
                    "time_window",
                    "pickup",
                ],
                &mut errors,
            );
            if !self.weapons.contains_key(&evolution.replaces_weapon) {
                errors.push(format!(
                    "evolution `{}` replaces missing weapon `{}`",
                    evolution.id, evolution.replaces_weapon
                ));
            }
            if evolution.replaces_weapon != evolution.requirements.weapon.id {
                warnings.push(format!(
                    "evolution `{}` replaces `{}` but requires weapon `{}`",
                    evolution.id, evolution.replaces_weapon, evolution.requirements.weapon.id
                ));
            }
            validate_allowed(
                "evolution.weapon_definition.type",
                &evolution.weapon_definition.weapon_type,
                &[
                    "projectile",
                    "orbit",
                    "burst",
                    "zone",
                    "summon",
                    "beam",
                    "special",
                ],
                &mut errors,
            );
            validate_allowed(
                "evolution.weapon_definition.targeting.mode",
                &evolution.weapon_definition.targeting.mode,
                &[
                    "nearest_enemy",
                    "highest_health_enemy",
                    "boss_priority",
                    "random_enemy",
                    "random_direction",
                    "movement_direction",
                    "self_centered",
                    "ground_near_player",
                ],
                &mut errors,
            );
            validate_positive(
                "evolution.weapon_definition.targeting.range",
                evolution.weapon_definition.targeting.range,
                &mut errors,
            );
            validate_positive(
                "evolution.weapon_definition.damage",
                evolution.weapon_definition.base_stats.damage,
                &mut errors,
            );
            validate_positive(
                "evolution.weapon_definition.cooldown_ms",
                evolution.weapon_definition.base_stats.cooldown_ms,
                &mut errors,
            );
            validate_positive(
                "evolution.weapon_definition.projectile_count",
                evolution.weapon_definition.base_stats.projectile_count as f32,
                &mut errors,
            );
            validate_positive(
                "evolution.weapon_definition.area_radius",
                evolution.weapon_definition.base_stats.area_radius,
                &mut errors,
            );
            if let Some(projectile_speed) = evolution.weapon_definition.base_stats.projectile_speed
            {
                validate_positive(
                    "evolution.weapon_definition.projectile_speed",
                    projectile_speed,
                    &mut errors,
                );
            }
            if let Some(pierce) = evolution.weapon_definition.base_stats.pierce {
                validate_positive(
                    "evolution.weapon_definition.pierce",
                    pierce as f32,
                    &mut errors,
                );
            }
            if let Some(duration_ms) = evolution.weapon_definition.base_stats.duration_ms {
                validate_non_negative_finite(
                    "evolution.weapon_definition.duration_ms",
                    duration_ms,
                    &mut errors,
                );
            }
        }

        for enemy in self.enemies.values() {
            validate_enemy_like(
                "enemy",
                enemy.id(),
                &enemy.common,
                &enemy.common.stats,
                &mut errors,
            );
        }

        for boss in self.bosses.values() {
            validate_enemy_like(
                "boss",
                boss.id(),
                &boss.common,
                &boss.common.stats,
                &mut errors,
            );
            if boss.phases.is_empty() {
                errors.push(format!("boss `{}` has empty phases", boss.id()));
            }
        }

        for map in self.maps.values() {
            validate_common(
                CommonValidation {
                    category: "map",
                    id: &map.id,
                    version: map.version,
                    rarity: "",
                    tags: &map.tags,
                    description: &map.description,
                    visual_description: &map.visual_description,
                    sfx_description: "",
                },
                &mut errors,
            );
            validate_positive("map.width", map.size.width, &mut errors);
            validate_positive("map.height", map.size.height, &mut errors);
            if map.spawn_rules.min_distance <= 0.0
                || map.spawn_rules.max_distance <= map.spawn_rules.min_distance
            {
                errors.push(format!("map `{}` has invalid spawn distance range", map.id));
            }
        }

        for wave in self.waves.values() {
            validate_common(
                CommonValidation {
                    category: "wave",
                    id: &wave.id,
                    version: wave.version,
                    rarity: "",
                    tags: &[],
                    description: &wave.name,
                    visual_description: "",
                    sfx_description: "",
                },
                &mut errors,
            );
            if !self.maps.contains_key(&wave.map_id) {
                errors.push(format!(
                    "wave `{}` references missing map `{}`",
                    wave.id, wave.map_id
                ));
            }
            validate_positive("wave.duration_seconds", wave.duration_seconds, &mut errors);
            if wave.segments.is_empty() {
                errors.push(format!("wave `{}` has empty segments", wave.id));
            }
            for segment in &wave.segments {
                if segment.end_second <= segment.start_second {
                    errors.push(format!(
                        "wave `{}` has segment ending before start",
                        wave.id
                    ));
                }
                validate_positive(
                    "wave.segment.spawn_interval_ms",
                    segment.spawn_interval_ms,
                    &mut errors,
                );
                validate_positive(
                    "wave.segment.spawn_count",
                    segment.spawn_count as f32,
                    &mut errors,
                );
                validate_positive(
                    "wave.segment.max_alive",
                    segment.max_alive as f32,
                    &mut errors,
                );
                if segment.enemy_pool.is_empty() {
                    errors.push(format!(
                        "wave `{}` has segment with empty enemy_pool",
                        wave.id
                    ));
                }
                for entry in &segment.enemy_pool {
                    if !self.enemies.contains_key(&entry.enemy_id) {
                        errors.push(format!(
                            "wave `{}` references missing enemy `{}`",
                            wave.id, entry.enemy_id
                        ));
                    }
                    validate_positive("wave.enemy_pool.weight", entry.weight, &mut errors);
                }
            }
            for boss_event in &wave.boss_events {
                if !self.bosses.contains_key(&boss_event.boss_id) {
                    errors.push(format!(
                        "wave `{}` references missing boss `{}`",
                        wave.id, boss_event.boss_id
                    ));
                }
                validate_finite(
                    "wave.boss_event.time_second",
                    boss_event.time_second,
                    &mut errors,
                );
                if boss_event.time_second < 0.0 || boss_event.time_second > wave.duration_seconds {
                    errors.push(format!(
                        "wave `{}` has boss event outside duration",
                        wave.id
                    ));
                }
            }
        }

        for event in self.events.values() {
            validate_common(
                CommonValidation {
                    category: "event",
                    id: &event.id,
                    version: event.version,
                    rarity: &event.rarity,
                    tags: &event.tags,
                    description: &event.description,
                    visual_description: &event.visual_description,
                    sfx_description: &event.sfx_description,
                },
                &mut errors,
            );
            validate_allowed(
                "event.trigger.type",
                &event.trigger.trigger_type,
                &[
                    "time_window",
                    "boss_defeat",
                    "level_up",
                    "random",
                    "map_entry",
                ],
                &mut errors,
            );
            validate_optional_non_negative(
                "event.trigger.start_second",
                event.trigger.start_second,
                &mut errors,
            );
            validate_optional_non_negative(
                "event.trigger.end_second",
                event.trigger.end_second,
                &mut errors,
            );
            if let (Some(start_second), Some(end_second)) =
                (event.trigger.start_second, event.trigger.end_second)
            {
                if end_second <= start_second {
                    errors.push(format!(
                        "event `{}` has trigger ending before start",
                        event.id
                    ));
                }
            }
            if let Some(chance) = event.trigger.chance {
                validate_finite("event.trigger.chance", chance, &mut errors);
                if !(0.0..=1.0).contains(&chance) {
                    errors.push(format!(
                        "event `{}` has chance outside 0..=1: {}",
                        event.id, chance
                    ));
                }
            }
            if event.effects.is_empty() {
                errors.push(format!("event `{}` has empty effects", event.id));
            }
            for effect in &event.effects {
                validate_allowed(
                    "event.effect.type",
                    &effect.effect_type,
                    &[
                        "xp_multiplier",
                        "spawn_rate_multiplier",
                        "pickup_radius_multiplier",
                        "damage_multiplier",
                        "heal",
                        "spawn_enemy",
                    ],
                    &mut errors,
                );
                validate_finite("event.effect.value", effect.value, &mut errors);
                if let Some(duration_seconds) = effect.duration_seconds {
                    validate_positive(
                        "event.effect.duration_seconds",
                        duration_seconds,
                        &mut errors,
                    );
                }
            }
        }

        if errors.is_empty() {
            Ok(ValidationReport {
                object_count: self.object_count(),
                warnings,
            })
        } else {
            Err(ContentError::Validation(errors))
        }
    }

    pub fn object_count(&self) -> usize {
        self.characters.len()
            + self.weapons.len()
            + self.passives.len()
            + self.evolutions.len()
            + self.enemies.len()
            + self.bosses.len()
            + self.waves.len()
            + self.maps.len()
            + self.events.len()
    }
}

fn passive_add(
    id: &str,
    name: &str,
    tags: &[&str],
    description: &str,
    stat: &str,
    value_per_level: f32,
) -> PassiveDefinition {
    passive_definition(id, name, tags, description, stat, "add", value_per_level)
}

fn passive_multiply(
    id: &str,
    name: &str,
    tags: &[&str],
    description: &str,
    stat: &str,
    value_per_level: f32,
) -> PassiveDefinition {
    passive_definition(
        id,
        name,
        tags,
        description,
        stat,
        "multiply",
        value_per_level,
    )
}

fn passive_definition(
    id: &str,
    name: &str,
    tags: &[&str],
    description: &str,
    stat: &str,
    mode: &str,
    value_per_level: f32,
) -> PassiveDefinition {
    PassiveDefinition {
        id: id.to_string(),
        name: name.to_string(),
        version: 1,
        rarity: "common".to_string(),
        tags: tags.iter().map(|tag| (*tag).to_string()).collect(),
        description: description.to_string(),
        stat_modifiers: vec![StatModifierDefinition {
            stat: stat.to_string(),
            mode: mode.to_string(),
            value_per_level,
        }],
        max_level: 5,
        visual_description: format!("{name}的可爱糖果风图标。"),
        sfx_description: "轻快糖果提示音。".to_string(),
        unlock: UnlockDefinition {
            unlock_type: "default".to_string(),
        },
    }
}

#[allow(clippy::too_many_arguments)]
fn enemy_definition(
    id: &str,
    name: &str,
    family: &str,
    tags: &[&str],
    health: f32,
    move_speed: f32,
    contact_damage_per_second: f32,
    radius: f32,
    xp_value: f32,
    threat: f32,
) -> EnemyDefinition {
    EnemyDefinition {
        common: EnemyCommonDefinition {
            id: id.to_string(),
            name: name.to_string(),
            version: 1,
            rarity: "common".to_string(),
            tags: tags.iter().map(|tag| (*tag).to_string()).collect(),
            description: format!("{name}会追着守护员移动。"),
            stats: EnemyStatsDefinition {
                health,
                move_speed,
                contact_damage_per_second,
                radius,
                xp_value,
                score_value: (xp_value as u32) * 3,
            },
            counterplay: "保持移动并用自动武器清理。".to_string(),
            visual_description: format!("{name}的圆润糖果轮廓。"),
            sfx_description: "软糖弹跳声。".to_string(),
        },
        family: family.to_string(),
        behavior: BehaviorDefinition {
            behavior_type: "chase".to_string(),
            parameters: serde_json::json!({}),
        },
        spawn_budget: SpawnBudgetDefinition {
            threat,
            performance_cost: 1.0,
        },
        death_effect: "弹成小糖屑。".to_string(),
    }
}

fn base_demo_wave_segments() -> Vec<WaveSegmentDefinition> {
    vec![
        wave_segment(0.0, 90.0, 1250.0, 1, 35, &[("bouncy-gummy", 1.0)]),
        wave_segment(
            90.0,
            210.0,
            950.0,
            2,
            55,
            &[("bouncy-gummy", 0.75), ("sour-gummy", 0.25)],
        ),
        wave_segment(
            210.0,
            300.0,
            1050.0,
            2,
            65,
            &[
                ("bouncy-gummy", 0.65),
                ("sour-gummy", 0.2),
                ("sandwich-cookie-creep", 0.15),
            ],
        ),
        wave_segment(
            300.0,
            480.0,
            820.0,
            3,
            82,
            &[
                ("bouncy-gummy", 0.48),
                ("sour-gummy", 0.22),
                ("sandwich-cookie-creep", 0.18),
                ("caramel-slime", 0.12),
            ],
        ),
        wave_segment(
            480.0,
            600.0,
            700.0,
            3,
            105,
            &[
                ("bouncy-gummy", 0.4),
                ("sour-gummy", 0.25),
                ("sandwich-cookie-creep", 0.2),
                ("caramel-slime", 0.15),
            ],
        ),
    ]
}

fn wave_segment(
    start_second: f32,
    end_second: f32,
    spawn_interval_ms: f32,
    spawn_count: usize,
    max_alive: usize,
    enemy_pool: &[(&str, f32)],
) -> WaveSegmentDefinition {
    WaveSegmentDefinition {
        start_second,
        end_second,
        spawn_interval_ms,
        spawn_count,
        max_alive,
        enemy_pool: enemy_pool
            .iter()
            .map(|(enemy_id, weight)| EnemyPoolEntryDefinition {
                enemy_id: (*enemy_id).to_string(),
                weight: *weight,
            })
            .collect(),
    }
}

#[derive(Debug, Clone)]
pub struct ValidationReport {
    pub object_count: usize,
    pub warnings: Vec<String>,
}

#[derive(Debug)]
pub enum ContentError {
    Io { path: PathBuf, message: String },
    Json { path: PathBuf, message: String },
    DuplicateId { category: String, id: String },
    Validation(Vec<String>),
}

impl fmt::Display for ContentError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io { path, message } => {
                write!(f, "failed to read `{}`: {message}", path.display())
            }
            Self::Json { path, message } => {
                write!(f, "failed to parse `{}`: {message}", path.display())
            }
            Self::DuplicateId { category, id } => {
                write!(f, "duplicate id `{id}` in category `{category}`")
            }
            Self::Validation(errors) => {
                write!(f, "content validation failed: {}", errors.join("; "))
            }
        }
    }
}

impl std::error::Error for ContentError {}

pub trait ContentObject {
    fn id(&self) -> &str;
}

#[derive(Debug, Clone, Deserialize)]
pub struct UnlockDefinition {
    #[serde(rename = "type")]
    pub unlock_type: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct CharacterDefinition {
    pub id: String,
    pub name: String,
    pub version: u32,
    pub rarity: String,
    pub tags: Vec<String>,
    pub description: String,
    pub base_stats: CharacterBaseStats,
    pub initial_loadout: InitialLoadoutDefinition,
    #[serde(default, rename = "trait", alias = "trait_definition")]
    pub trait_definition: Option<CharacterTraitDefinition>,
    pub visual_description: String,
    pub sfx_description: String,
    pub unlock: UnlockDefinition,
}

impl ContentObject for CharacterDefinition {
    fn id(&self) -> &str {
        &self.id
    }
}

#[derive(Debug, Clone, Deserialize)]
pub struct CharacterBaseStats {
    pub max_health: f32,
    pub move_speed: f32,
    pub pickup_radius: f32,
    pub damage_multiplier: f32,
    pub cooldown_multiplier: f32,
    pub xp_multiplier: f32,
    pub regen_per_second: f32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct InitialLoadoutDefinition {
    pub weapons: Vec<String>,
    pub passives: Vec<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct CharacterTraitDefinition {
    pub id: String,
    pub description: String,
    pub rules: Vec<serde_json::Value>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct WeaponDefinition {
    pub id: String,
    pub name: String,
    pub version: u32,
    pub rarity: String,
    #[serde(rename = "type")]
    pub weapon_type: String,
    pub tags: Vec<String>,
    pub description: String,
    pub targeting: TargetingDefinition,
    pub base_stats: WeaponBaseStats,
    pub scaling: WeaponScaling,
    pub balance_budget: WeaponBalanceBudget,
    pub visual_description: String,
    pub sfx_description: String,
    pub unlock: UnlockDefinition,
}

impl ContentObject for WeaponDefinition {
    fn id(&self) -> &str {
        &self.id
    }
}

#[derive(Debug, Clone, Deserialize)]
pub struct TargetingDefinition {
    pub mode: String,
    pub range: f32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct WeaponBaseStats {
    pub damage: f32,
    pub cooldown_ms: f32,
    pub projectile_speed: f32,
    pub projectile_count: u32,
    pub pierce: u32,
    pub area_radius: f32,
    pub duration_ms: f32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct WeaponScaling {
    pub max_level: u32,
    pub damage_per_level: f32,
    pub cooldown_multiplier_per_level: f32,
    pub range_per_level: f32,
    pub area_per_level: f32,
    pub projectile_count_bonus_levels: Vec<u32>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct WeaponBalanceBudget {
    pub role: String,
    pub single_target_dps: f32,
    pub group_dps: f32,
    pub performance_cost: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct PassiveDefinition {
    pub id: String,
    pub name: String,
    pub version: u32,
    pub rarity: String,
    pub tags: Vec<String>,
    pub description: String,
    pub stat_modifiers: Vec<StatModifierDefinition>,
    pub max_level: u32,
    pub visual_description: String,
    pub sfx_description: String,
    pub unlock: UnlockDefinition,
}

impl ContentObject for PassiveDefinition {
    fn id(&self) -> &str {
        &self.id
    }
}

#[derive(Debug, Clone, Deserialize)]
pub struct StatModifierDefinition {
    pub stat: String,
    pub mode: String,
    pub value_per_level: f32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct EvolutionDefinition {
    pub id: String,
    pub name: String,
    pub version: u32,
    pub rarity: String,
    pub tags: Vec<String>,
    pub description: String,
    pub requirements: EvolutionRequirementsDefinition,
    pub replaces_weapon: String,
    pub weapon_definition: EvolutionWeaponDefinition,
    pub visual_description: String,
    pub sfx_description: String,
    pub unlock: UnlockDefinition,
}

impl ContentObject for EvolutionDefinition {
    fn id(&self) -> &str {
        &self.id
    }
}

#[derive(Debug, Clone, Deserialize)]
pub struct EvolutionRequirementsDefinition {
    pub weapon: ContentLevelRequirementDefinition,
    pub passive: Option<ContentLevelRequirementDefinition>,
    pub trigger: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ContentLevelRequirementDefinition {
    pub id: String,
    pub min_level: u32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct EvolutionWeaponDefinition {
    #[serde(rename = "type")]
    pub weapon_type: String,
    pub targeting: TargetingDefinition,
    pub base_stats: EvolutionWeaponBaseStats,
}

#[derive(Debug, Clone, Deserialize)]
pub struct EvolutionWeaponBaseStats {
    pub damage: f32,
    pub cooldown_ms: f32,
    #[serde(default)]
    pub projectile_speed: Option<f32>,
    pub projectile_count: u32,
    #[serde(default)]
    pub pierce: Option<u32>,
    pub area_radius: f32,
    #[serde(default)]
    pub duration_ms: Option<f32>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct EnemyDefinition {
    #[serde(flatten)]
    pub common: EnemyCommonDefinition,
    pub family: String,
    pub behavior: BehaviorDefinition,
    pub spawn_budget: SpawnBudgetDefinition,
    pub death_effect: String,
}

impl ContentObject for EnemyDefinition {
    fn id(&self) -> &str {
        &self.common.id
    }
}

impl EnemyDefinition {
    pub fn id(&self) -> &str {
        &self.common.id
    }
}

#[derive(Debug, Clone, Deserialize)]
pub struct BossDefinition {
    #[serde(flatten)]
    pub common: EnemyCommonDefinition,
    pub phases: Vec<BossPhaseDefinition>,
}

impl ContentObject for BossDefinition {
    fn id(&self) -> &str {
        &self.common.id
    }
}

impl BossDefinition {
    pub fn id(&self) -> &str {
        &self.common.id
    }
}

#[derive(Debug, Clone, Deserialize)]
pub struct EnemyCommonDefinition {
    pub id: String,
    pub name: String,
    pub version: u32,
    pub rarity: String,
    pub tags: Vec<String>,
    pub description: String,
    pub stats: EnemyStatsDefinition,
    pub counterplay: String,
    pub visual_description: String,
    pub sfx_description: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct EnemyStatsDefinition {
    pub health: f32,
    pub move_speed: f32,
    pub contact_damage_per_second: f32,
    pub radius: f32,
    pub xp_value: f32,
    pub score_value: u32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct BehaviorDefinition {
    #[serde(rename = "type")]
    pub behavior_type: String,
    pub parameters: serde_json::Value,
}

#[derive(Debug, Clone, Deserialize)]
pub struct SpawnBudgetDefinition {
    pub threat: f32,
    pub performance_cost: f32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct BossPhaseDefinition {
    pub hp_threshold: f32,
    pub abilities: Vec<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct WaveDefinition {
    pub id: String,
    pub name: String,
    pub version: u32,
    pub map_id: String,
    pub duration_seconds: f32,
    pub segments: Vec<WaveSegmentDefinition>,
    pub boss_events: Vec<BossEventDefinition>,
    pub pressure_budget: PressureBudgetDefinition,
}

impl ContentObject for WaveDefinition {
    fn id(&self) -> &str {
        &self.id
    }
}

#[derive(Debug, Clone, Deserialize)]
pub struct WaveSegmentDefinition {
    pub start_second: f32,
    pub end_second: f32,
    pub spawn_interval_ms: f32,
    pub spawn_count: usize,
    pub max_alive: usize,
    pub enemy_pool: Vec<EnemyPoolEntryDefinition>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct EnemyPoolEntryDefinition {
    pub enemy_id: String,
    pub weight: f32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct BossEventDefinition {
    pub time_second: f32,
    pub boss_id: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct PressureBudgetDefinition {
    pub early: String,
    pub middle: String,
    pub late: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct MapDefinition {
    pub id: String,
    pub name: String,
    pub version: u32,
    pub tags: Vec<String>,
    pub description: String,
    pub size: MapSizeDefinition,
    pub bounds: BoundsDefinition,
    pub spawn_rules: SpawnRulesDefinition,
    pub hazards: Vec<serde_json::Value>,
    pub visual_description: String,
    pub music_theme: String,
}

impl ContentObject for MapDefinition {
    fn id(&self) -> &str {
        &self.id
    }
}

#[derive(Debug, Clone, Deserialize)]
pub struct MapSizeDefinition {
    pub width: f32,
    pub height: f32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct BoundsDefinition {
    #[serde(rename = "type")]
    pub bounds_type: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct SpawnRulesDefinition {
    pub mode: String,
    pub min_distance: f32,
    pub max_distance: f32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct EventDefinition {
    pub id: String,
    pub name: String,
    pub version: u32,
    pub rarity: String,
    pub tags: Vec<String>,
    pub description: String,
    pub trigger: EventTriggerDefinition,
    pub effects: Vec<EventEffectDefinition>,
    pub visual_description: String,
    pub sfx_description: String,
}

impl ContentObject for EventDefinition {
    fn id(&self) -> &str {
        &self.id
    }
}

#[derive(Debug, Clone, Deserialize)]
pub struct EventTriggerDefinition {
    #[serde(rename = "type")]
    pub trigger_type: String,
    #[serde(default)]
    pub start_second: Option<f32>,
    #[serde(default)]
    pub end_second: Option<f32>,
    #[serde(default)]
    pub chance: Option<f32>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct EventEffectDefinition {
    #[serde(rename = "type")]
    pub effect_type: String,
    pub value: f32,
    #[serde(default)]
    pub duration_seconds: Option<f32>,
}

fn load_category<T>(path: &Path) -> Result<BTreeMap<String, T>, ContentError>
where
    T: for<'de> Deserialize<'de> + ContentObject,
{
    let mut values = BTreeMap::new();
    if !path.exists() {
        return Ok(values);
    }

    for entry in fs::read_dir(path).map_err(|error| ContentError::Io {
        path: path.to_path_buf(),
        message: error.to_string(),
    })? {
        let entry = entry.map_err(|error| ContentError::Io {
            path: path.to_path_buf(),
            message: error.to_string(),
        })?;
        let file_path = entry.path();
        if file_path.extension().and_then(|value| value.to_str()) != Some("json") {
            continue;
        }
        let raw = fs::read_to_string(&file_path).map_err(|error| ContentError::Io {
            path: file_path.clone(),
            message: error.to_string(),
        })?;
        let value: T = serde_json::from_str(&raw).map_err(|error| ContentError::Json {
            path: file_path.clone(),
            message: error.to_string(),
        })?;
        let id = value.id().to_string();
        if values.insert(id.clone(), value).is_some() {
            return Err(ContentError::DuplicateId {
                category: path
                    .file_name()
                    .and_then(|value| value.to_str())
                    .unwrap_or("unknown")
                    .to_string(),
                id,
            });
        }
    }

    Ok(values)
}

fn validate_non_empty<T>(category: &str, values: &BTreeMap<String, T>, errors: &mut Vec<String>) {
    if values.is_empty() {
        errors.push(format!("category `{category}` is empty"));
    }
}

fn validate_ids<'a>(
    category: &str,
    ids: impl Iterator<Item = &'a String>,
    errors: &mut Vec<String>,
) {
    let mut seen = HashSet::new();
    for id in ids {
        if !is_kebab_case(id) {
            errors.push(format!("id `{id}` in `{category}` is not kebab-case"));
        }
        if !seen.insert(id) {
            errors.push(format!("duplicate id `{id}` in `{category}`"));
        }
    }
}

struct CommonValidation<'a> {
    category: &'a str,
    id: &'a str,
    version: u32,
    rarity: &'a str,
    tags: &'a [String],
    description: &'a str,
    visual_description: &'a str,
    sfx_description: &'a str,
}

fn validate_common(common: CommonValidation<'_>, errors: &mut Vec<String>) {
    if common.id.is_empty() {
        errors.push(format!("{} has empty id", common.category));
    }
    if common.version == 0 {
        errors.push(format!("{} `{}` has version 0", common.category, common.id));
    }
    if !common.rarity.is_empty() {
        validate_allowed(
            "rarity",
            common.rarity,
            &["common", "rare", "epic", "legendary", "boss", "debug"],
            errors,
        );
    }
    if common.tags.iter().any(|tag| tag.trim().is_empty()) {
        errors.push(format!(
            "{} `{}` has an empty tag",
            common.category, common.id
        ));
    }
    if common.description.trim().is_empty() {
        errors.push(format!(
            "{} `{}` has empty description",
            common.category, common.id
        ));
    }
    if !common.visual_description.is_empty() && common.visual_description.trim().is_empty() {
        errors.push(format!(
            "{} `{}` has empty visual_description",
            common.category, common.id
        ));
    }
    if !common.sfx_description.is_empty() && common.sfx_description.trim().is_empty() {
        errors.push(format!(
            "{} `{}` has empty sfx_description",
            common.category, common.id
        ));
    }
}

fn validate_enemy_like(
    category: &str,
    id: &str,
    common: &EnemyCommonDefinition,
    stats: &EnemyStatsDefinition,
    errors: &mut Vec<String>,
) {
    validate_common(
        CommonValidation {
            category,
            id,
            version: common.version,
            rarity: &common.rarity,
            tags: &common.tags,
            description: &common.description,
            visual_description: &common.visual_description,
            sfx_description: &common.sfx_description,
        },
        errors,
    );
    validate_positive("enemy.health", stats.health, errors);
    validate_positive("enemy.move_speed", stats.move_speed, errors);
    validate_positive(
        "enemy.contact_damage_per_second",
        stats.contact_damage_per_second,
        errors,
    );
    validate_positive("enemy.radius", stats.radius, errors);
    validate_finite("enemy.xp_value", stats.xp_value, errors);
    if stats.xp_value < 0.0 {
        errors.push(format!("{category} `{id}` has negative xp_value"));
    }
    if common.counterplay.trim().is_empty() {
        errors.push(format!("{category} `{id}` has empty counterplay"));
    }
}

fn validate_content_level_requirement(
    field: &str,
    owner_id: &str,
    requirement: &ContentLevelRequirementDefinition,
    max_level: Option<u32>,
    errors: &mut Vec<String>,
) {
    if requirement.id.trim().is_empty() {
        errors.push(format!("{field} for `{owner_id}` has empty id"));
    }
    validate_positive(
        &format!("{field}.min_level"),
        requirement.min_level as f32,
        errors,
    );
    match max_level {
        Some(max_level) if requirement.min_level > max_level => {
            errors.push(format!(
                "{field} for `{owner_id}` requires `{}` level {} above max level {}",
                requirement.id, requirement.min_level, max_level
            ));
        }
        Some(_) => {}
        None => {
            errors.push(format!(
                "{field} for `{owner_id}` references missing content `{}`",
                requirement.id
            ));
        }
    }
}

fn validate_allowed(field: &str, value: &str, allowed: &[&str], errors: &mut Vec<String>) {
    if !allowed.contains(&value) {
        errors.push(format!(
            "{field} `{value}` is not allowed; expected one of {}",
            allowed.join(", ")
        ));
    }
}

fn validate_positive(field: &str, value: f32, errors: &mut Vec<String>) {
    if !value.is_finite() || value <= 0.0 {
        errors.push(format!("{field} must be positive finite, got {value}"));
    }
}

fn validate_non_negative_finite(field: &str, value: f32, errors: &mut Vec<String>) {
    if !value.is_finite() || value < 0.0 {
        errors.push(format!("{field} must be non-negative finite, got {value}"));
    }
}

fn validate_optional_non_negative(field: &str, value: Option<f32>, errors: &mut Vec<String>) {
    if let Some(value) = value {
        validate_non_negative_finite(field, value, errors);
    }
}

fn validate_finite(field: &str, value: f32, errors: &mut Vec<String>) {
    if !value.is_finite() {
        errors.push(format!("{field} must be finite, got {value}"));
    }
}

fn is_kebab_case(value: &str) -> bool {
    !value.is_empty()
        && value
            .bytes()
            .all(|byte| byte.is_ascii_lowercase() || byte.is_ascii_digit() || byte == b'-')
        && !value.starts_with('-')
        && !value.ends_with('-')
        && !value.contains("--")
}
