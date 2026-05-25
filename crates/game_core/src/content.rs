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

        for character in [
            character_definition(
                "bubble-courier",
                "泡泡邮差",
                &["mobility", "pickup", "intermediate"],
                "穿梭在糖果王国邮路上的泡泡邮差，擅长高速移动和捡取糖晶。",
                100.0,
                205.0,
                88.0,
                0.95,
                0.98,
                1.08,
                "soda-bubble-pop",
                "bubble-runner",
                "移动后短时间提升拾取范围。",
                "戴邮差帽的蓝粉泡泡角色，斜挎糖信包，鞋底冒泡。",
                "轻快泡泡脚步声和小铃铛提示音。",
            ),
            character_definition(
                "cream-knight",
                "奶油骑士",
                &["defense", "beginner", "close"],
                "举着奶油纹章的小骑士，生命更高但移动略慢。",
                150.0,
                165.0,
                68.0,
                0.95,
                1.04,
                1.0,
                "marshmallow-shield",
                "cream-guard",
                "受击后获得短暂减伤。",
                "圆润奶油盔甲和小糖盾，配色以奶白和浅金为主。",
                "柔软护甲碰撞声和奶油盾轻响。",
            ),
            character_definition(
                "sour-plum-doctor",
                "酸梅博士",
                &["control", "boss-safe", "advanced"],
                "研究酸味糖雾的博士，输出略低但更擅长控场。",
                110.0,
                175.0,
                72.0,
                0.95,
                1.0,
                1.0,
                "sour-plum-spray",
                "sour-control",
                "减速效果增强。",
                "戴护目镜的紫红酸梅博士，背着小糖雾罐。",
                "酸糖 fizz 声和实验瓶轻响。",
            ),
            character_definition(
                "pudding-crafter",
                "布丁工匠",
                &["summon", "area-control", "intermediate"],
                "会搭建布丁炮台的工匠，适合围绕安全区域经营火力。",
                115.0,
                170.0,
                70.0,
                0.96,
                1.02,
                1.0,
                "pudding-turret",
                "longer-summons",
                "召唤物持续时间增加。",
                "系围裙的布丁工匠，工具包里插着奶油喷嘴和樱桃扳手。",
                "工具轻响和布丁弹跳声。",
            ),
        ] {
            pack.characters.insert(character.id.clone(), character);
        }

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

        pack.weapons.insert(
            "candy-crystal-lance".to_string(),
            WeaponDefinition {
                id: "candy-crystal-lance".to_string(),
                name: "糖晶长枪".to_string(),
                version: 1,
                rarity: "common".to_string(),
                weapon_type: "projectile".to_string(),
                tags: vec![
                    "projectile".to_string(),
                    "boss-killer".to_string(),
                    "pierce".to_string(),
                ],
                description: "周期性射出高伤害糖晶长枪，优先瞄准 Boss。".to_string(),
                targeting: TargetingDefinition {
                    mode: "boss_priority".to_string(),
                    range: 520.0,
                },
                base_stats: WeaponBaseStats {
                    damage: 26.0,
                    cooldown_ms: 1100.0,
                    projectile_speed: 620.0,
                    projectile_count: 1,
                    pierce: 3,
                    area_radius: 12.0,
                    duration_ms: 0.0,
                },
                scaling: WeaponScaling {
                    max_level: 5,
                    damage_per_level: 9.0,
                    cooldown_multiplier_per_level: 0.94,
                    range_per_level: 20.0,
                    area_per_level: 1.0,
                    projectile_count_bonus_levels: vec![5],
                },
                balance_budget: WeaponBalanceBudget {
                    role: "boss-killer".to_string(),
                    single_target_dps: 24.0,
                    group_dps: 16.0,
                    performance_cost: "low".to_string(),
                },
                visual_description: "透明糖晶凝成的细长长枪，枪尖有星形高光。".to_string(),
                sfx_description: "清脆的玻璃糖破空声。".to_string(),
                unlock: UnlockDefinition {
                    unlock_type: "default".to_string(),
                },
            },
        );

        pack.weapons.insert(
            "soda-fountain".to_string(),
            WeaponDefinition {
                id: "soda-fountain".to_string(),
                name: "汽水喷泉".to_string(),
                version: 1,
                rarity: "common".to_string(),
                weapon_type: "burst".to_string(),
                tags: vec![
                    "aoe".to_string(),
                    "burst".to_string(),
                    "knockback".to_string(),
                ],
                description: "在敌人附近喷出汽水爆发，适合清理小群敌人。".to_string(),
                targeting: TargetingDefinition {
                    mode: "random_enemy".to_string(),
                    range: 450.0,
                },
                base_stats: WeaponBaseStats {
                    damage: 16.0,
                    cooldown_ms: 950.0,
                    projectile_speed: 450.0,
                    projectile_count: 2,
                    pierce: 1,
                    area_radius: 24.0,
                    duration_ms: 0.0,
                },
                scaling: WeaponScaling {
                    max_level: 5,
                    damage_per_level: 5.0,
                    cooldown_multiplier_per_level: 0.93,
                    range_per_level: 16.0,
                    area_per_level: 3.0,
                    projectile_count_bonus_levels: vec![4],
                },
                balance_budget: WeaponBalanceBudget {
                    role: "aoe-clear".to_string(),
                    single_target_dps: 34.0,
                    group_dps: 52.0,
                    performance_cost: "medium".to_string(),
                },
                visual_description: "蓝粉色汽水泡泡向上喷发，落地时溅出糖浆泡沫。".to_string(),
                sfx_description: "短促的汽水喷发声和泡泡爆裂声。".to_string(),
                unlock: UnlockDefinition {
                    unlock_type: "default".to_string(),
                },
            },
        );

        for weapon in [
            weapon_definition(
                "marshmallow-shield",
                "棉花糖护盾",
                "orbit",
                &["defense", "orbit", "close"],
                "棉花糖球围绕守护员旋转，适合近身防御。",
                "self_centered",
                120.0,
                12.0,
                750.0,
                360.0,
                2,
                2,
                20.0,
                1600.0,
                4.0,
                0.94,
                6.0,
                2.0,
                &[3, 5],
                "defense",
                32.0,
                48.0,
                "medium",
                "几颗蓬松棉花糖球围成柔软护环，边缘有糖霜高光。",
                "轻柔的 puff 和软弹碰撞声。",
            ),
            weapon_definition(
                "lollipop-boomerang",
                "棒棒糖回旋镖",
                "projectile",
                &["boomerang", "pierce", "projectile"],
                "掷出回旋棒棒糖，穿过敌群后返回造成二次威胁。",
                "movement_direction",
                460.0,
                18.0,
                900.0,
                520.0,
                2,
                2,
                16.0,
                1400.0,
                6.0,
                0.93,
                18.0,
                1.0,
                &[4],
                "pierce-clear",
                40.0,
                58.0,
                "medium",
                "彩色螺旋棒棒糖盘带短糖丝尾迹，回旋轨迹清楚。",
                "轻快的 whoosh 和糖片划过声。",
            ),
            weapon_definition(
                "popping-candy-mine",
                "跳跳糖地雷",
                "burst",
                &["trap", "burst", "area"],
                "在守护员附近布置跳跳糖，敌人靠近后爆成小范围糖屑。",
                "ground_near_player",
                280.0,
                22.0,
                1250.0,
                220.0,
                2,
                1,
                34.0,
                2600.0,
                7.0,
                0.94,
                10.0,
                3.0,
                &[3, 5],
                "aoe-clear",
                35.0,
                68.0,
                "medium",
                "小堆彩色跳跳糖颗粒，触发时弹出星形糖屑爆点。",
                "连续 crackle pop 爆裂声。",
            ),
            weapon_definition(
                "caramel-sticky-ground",
                "焦糖黏地",
                "zone",
                &["slow", "zone", "control"],
                "在地面留下焦糖区域，持续压制经过的敌人。",
                "ground_near_player",
                260.0,
                12.0,
                1000.0,
                160.0,
                2,
                3,
                42.0,
                2800.0,
                4.0,
                0.95,
                8.0,
                4.0,
                &[4],
                "control",
                24.0,
                52.0,
                "medium",
                "金棕色焦糖圆形黏地，边缘缓慢拉丝并带亮面反光。",
                "黏稠的 splat 和低低糖浆流动声。",
            ),
            weapon_definition(
                "pudding-turret",
                "布丁炮台",
                "summon",
                &["summon", "turret", "auto-fire"],
                "召唤布丁炮台自动射击，适合经营安全区域。",
                "nearest_enemy",
                420.0,
                12.0,
                600.0,
                480.0,
                1,
                1,
                14.0,
                5000.0,
                4.0,
                0.9,
                16.0,
                1.0,
                &[3, 5],
                "summon",
                20.0,
                30.0,
                "medium",
                "圆润布丁小炮台顶着樱桃，发射奶油糖弹。",
                "轻快的 pudding plop 和小糖弹发射声。",
            ),
            weapon_definition(
                "mint-cyclone",
                "薄荷旋风",
                "orbit",
                &["control", "cold", "orbit"],
                "薄荷风围绕守护员旋转，削弱靠近敌人的推进压力。",
                "self_centered",
                150.0,
                10.0,
                700.0,
                400.0,
                2,
                3,
                24.0,
                1800.0,
                4.0,
                0.94,
                8.0,
                2.0,
                &[4],
                "control",
                29.0,
                58.0,
                "medium",
                "浅绿薄荷风带绕成螺旋，带白色冷气糖粉。",
                "清凉的 swirl 和薄荷铃声。",
            ),
            weapon_definition(
                "star-sugar-ray",
                "星糖射线",
                "beam",
                &["beam", "boss-killer", "single-target"],
                "短时间锁定高血敌人，发射稳定星糖射线。",
                "highest_health_enemy",
                560.0,
                30.0,
                1300.0,
                720.0,
                1,
                2,
                12.0,
                900.0,
                10.0,
                0.94,
                22.0,
                1.0,
                &[5],
                "boss-killer",
                23.0,
                16.0,
                "low",
                "细长星形糖光束，末端有棱镜般的彩色折射。",
                "明亮持续的 shimmer beam 声。",
            ),
            weapon_definition(
                "soda-bubble-pop",
                "汽水泡泡",
                "projectile",
                &["starter", "projectile", "bubble"],
                "发射轻快汽水泡泡，适合高机动角色边跑边清小怪。",
                "nearest_enemy",
                390.0,
                11.0,
                580.0,
                500.0,
                1,
                1,
                16.0,
                0.0,
                5.0,
                0.92,
                16.0,
                2.0,
                &[3, 5],
                "starter",
                19.0,
                16.0,
                "low",
                "浅蓝半透明汽水泡泡弹，内部有细小气泡和白色高光。",
                "轻快的 bubble pop 声。",
            ),
            weapon_definition(
                "sour-plum-spray",
                "酸梅喷雾",
                "zone",
                &["starter", "control", "slow"],
                "喷出酸梅糖雾，压低敌人的推进速度并造成持续伤害。",
                "nearest_enemy",
                360.0,
                10.0,
                650.0,
                320.0,
                2,
                3,
                28.0,
                1400.0,
                4.0,
                0.93,
                12.0,
                3.0,
                &[4],
                "control",
                31.0,
                52.0,
                "medium",
                "紫红酸梅糖雾像扇形云团散开，边缘有酸粒闪点。",
                "细密喷雾声和酸糖 fizz 声。",
            ),
        ] {
            pack.weapons.insert(weapon.id.clone(), weapon);
        }

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

        for evolution in [
            evolution_definition(
                "marshmallow-fortress",
                "棉花堡垒",
                &["defense", "orbit", "evolution"],
                "棉花糖护盾进化为持续护城环，扩大近身安全区。",
                "marshmallow-shield",
                "big-candy-jar",
                "orbit",
                "self_centered",
                190.0,
                30.0,
                650.0,
                Some(420.0),
                6,
                Some(4),
                34.0,
                Some(2400.0),
                "厚厚棉花糖城墙围绕守护员，带粉白糖霜垛口。",
                "蓬松护盾展开声和柔软撞击声。",
            ),
            evolution_definition(
                "soda-volcano",
                "汽水火山",
                &["aoe", "burst", "evolution"],
                "汽水喷泉进化为连续喷发的汽水火山，覆盖更大敌群。",
                "soda-fountain",
                "bubble-shoes",
                "burst",
                "random_enemy",
                560.0,
                48.0,
                1000.0,
                Some(280.0),
                6,
                Some(3),
                58.0,
                Some(900.0),
                "蓝粉汽水柱从地面喷起，泡泡和糖浆像火山一样外溅。",
                "强烈汽水喷发和连续泡泡爆裂声。",
            ),
            evolution_definition(
                "sugar-windmill",
                "旋糖风车",
                &["boomerang", "pierce", "evolution"],
                "棒棒糖回旋镖进化为旋糖风车，长时间切穿敌群。",
                "lollipop-boomerang",
                "cream-clockwork",
                "projectile",
                "movement_direction",
                620.0,
                38.0,
                800.0,
                Some(600.0),
                4,
                Some(6),
                22.0,
                Some(1800.0),
                "多片棒棒糖叶片组成旋转风车，留下彩糖螺旋轨迹。",
                "快速旋转的 whoosh 和清脆糖片切割声。",
            ),
            evolution_definition(
                "popping-candy-chain-reaction",
                "跳跳糖连锁反应",
                &["trap", "burst", "evolution"],
                "跳跳糖地雷进化为连锁爆点，在守护员附近连续爆裂。",
                "popping-candy-mine",
                "star-spoon",
                "burst",
                "ground_near_player",
                360.0,
                46.0,
                1100.0,
                Some(220.0),
                7,
                Some(4),
                52.0,
                Some(3000.0),
                "一串彩色跳跳糖爆点像星座一样接连亮起。",
                "密集 crackle pop 连锁爆裂声。",
            ),
            evolution_definition(
                "caramel-vortex",
                "焦糖漩涡",
                &["slow", "zone", "control", "evolution"],
                "焦糖黏地进化为更大的焦糖漩涡，长期封锁危险路线。",
                "caramel-sticky-ground",
                "sour-tuner",
                "zone",
                "ground_near_player",
                360.0,
                28.0,
                850.0,
                Some(160.0),
                4,
                Some(8),
                72.0,
                Some(3600.0),
                "厚重焦糖旋成圆形漩涡，中心有缓慢下陷的糖浆纹路。",
                "低沉黏稠的漩涡声和糖浆拉丝声。",
            ),
            evolution_definition(
                "pudding-bastion",
                "布丁要塞",
                &["summon", "turret", "evolution"],
                "布丁炮台进化为布丁要塞，生成多点自动火力。",
                "pudding-turret",
                "nonstick-apron",
                "summon",
                "nearest_enemy",
                520.0,
                26.0,
                550.0,
                Some(520.0),
                3,
                Some(2),
                18.0,
                Some(7000.0),
                "多个布丁塔组成甜点要塞，樱桃炮口轮流发光。",
                "布丁炮台连射声和奶油糖弹 plop 声。",
            ),
            evolution_definition(
                "star-sugar-prism",
                "星糖棱镜",
                &["beam", "boss-killer", "evolution"],
                "星糖射线进化为棱镜折射光束，同时锁定多个高血目标。",
                "star-sugar-ray",
                "frosting-gloves",
                "beam",
                "highest_health_enemy",
                680.0,
                70.0,
                1200.0,
                Some(760.0),
                3,
                Some(8),
                20.0,
                Some(1200.0),
                "星糖光束穿过透明糖棱镜，折射出多道彩色射线。",
                "明亮持续的 prism shimmer 和高频星糖共鸣声。",
            ),
        ] {
            pack.evolutions.insert(evolution.id.clone(), evolution);
        }

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
            passive_add(
                "nonstick-apron",
                "防粘围裙",
                &["defense", "beginner"],
                "降低接触伤害。",
                "damage_reduction",
                0.06,
            ),
            passive_add(
                "sour-tuner",
                "酸味调节器",
                &["control", "duration"],
                "延长控制和持续效果。",
                "effect_duration",
                0.1,
            ),
            passive_add(
                "frosting-gloves",
                "糖霜手套",
                &["projectile", "size"],
                "增加投射物大小。",
                "projectile_size",
                0.08,
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
                1.6,
            )
            .with_behavior(
                "leave_hazard",
                serde_json::json!({
                    "hazard_radius": 44,
                    "hazard_duration_seconds": 2.2,
                    "slow_multiplier": 0.78
                }),
            ),
            enemy_definition(
                "sticky-bear-gummy",
                "粘粘熊糖",
                "gummy",
                &["control", "slow", "bear"],
                28.0,
                52.0,
                3.7,
                14.0,
                4.0,
                1.3,
            )
            .with_behavior(
                "chase",
                serde_json::json!({
                    "on_contact_status_effect": {
                        "stat": "move_speed",
                        "multiplier": 0.82,
                        "duration_seconds": 1.2
                    }
                }),
            ),
            enemy_definition(
                "soda-bubble",
                "汽水泡泡",
                "soda",
                &["split", "swarm", "soda"],
                26.0,
                70.0,
                4.2,
                15.0,
                4.0,
                1.3,
            )
            .with_behavior(
                "split",
                serde_json::json!({
                    "child_enemy_id": "bouncy-gummy",
                    "child_count": 2,
                    "child_health_multiplier": 0.45,
                    "child_radius_multiplier": 0.72
                }),
            ),
            enemy_definition(
                "cotton-candy-clump",
                "棉花糖团",
                "cotton-candy",
                &["swarm", "aoe-check", "soft"],
                20.0,
                44.0,
                3.4,
                16.0,
                3.0,
                0.9,
            )
            .with_behavior(
                "chase",
                serde_json::json!({
                    "pack_spawn_bias": "group"
                }),
            ),
            enemy_definition(
                "spicy-gummy",
                "辣味软糖",
                "gummy",
                &["dash", "burst-danger", "spicy"],
                22.0,
                78.0,
                5.0,
                12.0,
                5.0,
                1.8,
            )
            .with_behavior(
                "dash",
                serde_json::json!({
                    "charge_seconds": 0.8,
                    "dash_seconds": 0.28,
                    "cooldown_seconds": 2.4,
                    "dash_speed_multiplier": 2.1
                }),
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
            validate_allowed(
                "enemy.behavior.type",
                &enemy.behavior.behavior_type,
                &[
                    "chase",
                    "dash",
                    "split",
                    "leave_hazard",
                    "orbit_player",
                    "jump",
                    "ranged_spit",
                    "shielded",
                ],
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
fn character_definition(
    id: &str,
    name: &str,
    tags: &[&str],
    description: &str,
    max_health: f32,
    move_speed: f32,
    pickup_radius: f32,
    damage_multiplier: f32,
    cooldown_multiplier: f32,
    xp_multiplier: f32,
    initial_weapon_id: &str,
    trait_id: &str,
    trait_description: &str,
    visual_description: &str,
    sfx_description: &str,
) -> CharacterDefinition {
    CharacterDefinition {
        id: id.to_string(),
        name: name.to_string(),
        version: 1,
        rarity: "common".to_string(),
        tags: tags.iter().map(|tag| (*tag).to_string()).collect(),
        description: description.to_string(),
        base_stats: CharacterBaseStats {
            max_health,
            move_speed,
            pickup_radius,
            damage_multiplier,
            cooldown_multiplier,
            xp_multiplier,
            regen_per_second: 0.0,
        },
        initial_loadout: InitialLoadoutDefinition {
            weapons: vec![initial_weapon_id.to_string()],
            passives: Vec::new(),
        },
        trait_definition: Some(CharacterTraitDefinition {
            id: trait_id.to_string(),
            description: trait_description.to_string(),
            rules: Vec::new(),
        }),
        visual_description: visual_description.to_string(),
        sfx_description: sfx_description.to_string(),
        unlock: UnlockDefinition {
            unlock_type: "default".to_string(),
        },
    }
}

#[allow(clippy::too_many_arguments)]
fn weapon_definition(
    id: &str,
    name: &str,
    weapon_type: &str,
    tags: &[&str],
    description: &str,
    targeting_mode: &str,
    targeting_range: f32,
    damage: f32,
    cooldown_ms: f32,
    projectile_speed: f32,
    projectile_count: u32,
    pierce: u32,
    area_radius: f32,
    duration_ms: f32,
    damage_per_level: f32,
    cooldown_multiplier_per_level: f32,
    range_per_level: f32,
    area_per_level: f32,
    projectile_count_bonus_levels: &[u32],
    role: &str,
    single_target_dps: f32,
    group_dps: f32,
    performance_cost: &str,
    visual_description: &str,
    sfx_description: &str,
) -> WeaponDefinition {
    WeaponDefinition {
        id: id.to_string(),
        name: name.to_string(),
        version: 1,
        rarity: "common".to_string(),
        weapon_type: weapon_type.to_string(),
        tags: tags.iter().map(|tag| (*tag).to_string()).collect(),
        description: description.to_string(),
        targeting: TargetingDefinition {
            mode: targeting_mode.to_string(),
            range: targeting_range,
        },
        base_stats: WeaponBaseStats {
            damage,
            cooldown_ms,
            projectile_speed,
            projectile_count,
            pierce,
            area_radius,
            duration_ms,
        },
        scaling: WeaponScaling {
            max_level: 5,
            damage_per_level,
            cooldown_multiplier_per_level,
            range_per_level,
            area_per_level,
            projectile_count_bonus_levels: projectile_count_bonus_levels.to_vec(),
        },
        balance_budget: WeaponBalanceBudget {
            role: role.to_string(),
            single_target_dps,
            group_dps,
            performance_cost: performance_cost.to_string(),
        },
        visual_description: visual_description.to_string(),
        sfx_description: sfx_description.to_string(),
        unlock: UnlockDefinition {
            unlock_type: "default".to_string(),
        },
    }
}

#[allow(clippy::too_many_arguments)]
fn evolution_definition(
    id: &str,
    name: &str,
    tags: &[&str],
    description: &str,
    weapon_id: &str,
    passive_id: &str,
    weapon_type: &str,
    targeting_mode: &str,
    targeting_range: f32,
    damage: f32,
    cooldown_ms: f32,
    projectile_speed: Option<f32>,
    projectile_count: u32,
    pierce: Option<u32>,
    area_radius: f32,
    duration_ms: Option<f32>,
    visual_description: &str,
    sfx_description: &str,
) -> EvolutionDefinition {
    EvolutionDefinition {
        id: id.to_string(),
        name: name.to_string(),
        version: 1,
        rarity: "epic".to_string(),
        tags: tags.iter().map(|tag| (*tag).to_string()).collect(),
        description: description.to_string(),
        requirements: EvolutionRequirementsDefinition {
            weapon: ContentLevelRequirementDefinition {
                id: weapon_id.to_string(),
                min_level: 5,
            },
            passive: Some(ContentLevelRequirementDefinition {
                id: passive_id.to_string(),
                min_level: 3,
            }),
            trigger: "boss_chest".to_string(),
        },
        replaces_weapon: weapon_id.to_string(),
        weapon_definition: EvolutionWeaponDefinition {
            weapon_type: weapon_type.to_string(),
            targeting: TargetingDefinition {
                mode: targeting_mode.to_string(),
                range: targeting_range,
            },
            base_stats: EvolutionWeaponBaseStats {
                damage,
                cooldown_ms,
                projectile_speed,
                projectile_count,
                pierce,
                area_radius,
                duration_ms,
            },
        },
        visual_description: visual_description.to_string(),
        sfx_description: sfx_description.to_string(),
        unlock: UnlockDefinition {
            unlock_type: "discover".to_string(),
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
            &[
                ("bouncy-gummy", 0.65),
                ("sour-gummy", 0.23),
                ("sticky-bear-gummy", 0.12),
            ],
        ),
        wave_segment(
            210.0,
            300.0,
            1050.0,
            2,
            65,
            &[
                ("bouncy-gummy", 0.5),
                ("sour-gummy", 0.18),
                ("sandwich-cookie-creep", 0.14),
                ("sticky-bear-gummy", 0.1),
                ("soda-bubble", 0.08),
            ],
        ),
        wave_segment(
            300.0,
            480.0,
            820.0,
            3,
            82,
            &[
                ("bouncy-gummy", 0.34),
                ("sour-gummy", 0.18),
                ("sandwich-cookie-creep", 0.15),
                ("caramel-slime", 0.1),
                ("sticky-bear-gummy", 0.1),
                ("soda-bubble", 0.08),
                ("cotton-candy-clump", 0.05),
            ],
        ),
        wave_segment(
            480.0,
            600.0,
            700.0,
            3,
            105,
            &[
                ("bouncy-gummy", 0.28),
                ("sour-gummy", 0.18),
                ("sandwich-cookie-creep", 0.16),
                ("caramel-slime", 0.12),
                ("sticky-bear-gummy", 0.09),
                ("soda-bubble", 0.08),
                ("cotton-candy-clump", 0.05),
                ("spicy-gummy", 0.04),
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

    fn with_behavior(mut self, behavior_type: &str, parameters: serde_json::Value) -> Self {
        self.behavior = BehaviorDefinition {
            behavior_type: behavior_type.to_string(),
            parameters,
        };
        self
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
