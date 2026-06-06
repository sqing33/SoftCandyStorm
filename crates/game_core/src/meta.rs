use crate::{RunConfig, RunMetrics, TerminalKind};
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};

const STANDARD_PATROL_SECONDS: f32 = 600.0;

#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RunMode {
    #[default]
    StandardPatrol,
    LongPatrol,
    EndlessStorm,
    ChapterChallenge,
    DailyStorm,
    ExperimentalStorm,
}

#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct MetaResourceWallet {
    pub candy_crystal_shards: u32,
    pub star_shards: u32,
    pub storm_grains: u32,
}

impl MetaResourceWallet {
    fn add(&mut self, other: &Self) {
        self.candy_crystal_shards += other.candy_crystal_shards;
        self.star_shards += other.star_shards;
        self.storm_grains += other.storm_grains;
    }
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct MetaUnlockSet {
    pub characters: BTreeSet<String>,
    pub weapons: BTreeSet<String>,
    pub passives: BTreeSet<String>,
    pub maps: BTreeSet<String>,
    pub evolutions: BTreeSet<String>,
    pub chapters: BTreeSet<String>,
    pub events: BTreeSet<String>,
    pub cosmetics: BTreeSet<String>,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct MetaCodexEntry {
    pub discovered: bool,
    pub first_seen_run: Option<String>,
    pub seen_count: u32,
    pub defeated_count: u32,
    pub used_count: u32,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct MetaCodex {
    pub characters: BTreeMap<String, MetaCodexEntry>,
    pub weapons: BTreeMap<String, MetaCodexEntry>,
    pub passives: BTreeMap<String, MetaCodexEntry>,
    pub enemies: BTreeMap<String, MetaCodexEntry>,
    pub bosses: BTreeMap<String, MetaCodexEntry>,
    pub maps: BTreeMap<String, MetaCodexEntry>,
    pub evolutions: BTreeMap<String, MetaCodexEntry>,
    pub events: BTreeMap<String, MetaCodexEntry>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChapterProgress {
    pub chapter_id: String,
    pub map_id: String,
    pub boss_id: String,
    pub unlocked: bool,
    pub completed_goals: BTreeSet<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetaProgress {
    pub resources: MetaResourceWallet,
    pub unlocks: MetaUnlockSet,
    pub codex: MetaCodex,
    pub chapters: BTreeMap<String, ChapterProgress>,
    pub completed_runs: u32,
    pub best_survival_seconds: f32,
}

impl MetaProgress {
    pub fn demo_start() -> Self {
        let mut unlocks = MetaUnlockSet::default();
        unlocks.characters.insert("jar-keeper".to_string());
        unlocks.weapons.insert("rainbow-candy-shot".to_string());
        unlocks.maps.insert("frosting-grassland".to_string());
        unlocks.chapters.insert("frosting-grassland".to_string());

        Self {
            resources: MetaResourceWallet::default(),
            unlocks,
            codex: MetaCodex::default(),
            chapters: demo_chapter_roster(),
            completed_runs: 0,
            best_survival_seconds: 0.0,
        }
    }

    pub fn apply_run_summary(&mut self, summary: &MetaRunSummary) -> MetaSettlementReport {
        self.completed_runs += 1;
        self.best_survival_seconds = self.best_survival_seconds.max(summary.duration_seconds);

        let mut report = MetaSettlementReport {
            run_id: summary.run_id.clone(),
            mode: summary.mode,
            run_summary: summary.clone(),
            resources_gained: calculate_run_rewards(summary),
            completed_goals: Vec::new(),
            unlocked: Vec::new(),
            codex_updates: Vec::new(),
            notes: Vec::new(),
        };
        self.resources.add(&report.resources_gained);

        record_codex_use(
            &mut self.codex.characters,
            &summary.character_id,
            &summary.run_id,
            &mut report.codex_updates,
        );
        record_codex_use(
            &mut self.codex.maps,
            &summary.map_id,
            &summary.run_id,
            &mut report.codex_updates,
        );
        for weapon_id in summary.weapon_levels.keys() {
            record_codex_use(
                &mut self.codex.weapons,
                weapon_id,
                &summary.run_id,
                &mut report.codex_updates,
            );
        }
        for passive_id in &summary.passives_used {
            record_codex_use(
                &mut self.codex.passives,
                passive_id,
                &summary.run_id,
                &mut report.codex_updates,
            );
        }
        for evolution_id in &summary.evolutions_used {
            record_codex_use(
                &mut self.codex.evolutions,
                evolution_id,
                &summary.run_id,
                &mut report.codex_updates,
            );
        }
        for (enemy_id, defeated_count) in &summary.enemies_defeated {
            record_codex_defeat(
                &mut self.codex.enemies,
                enemy_id,
                *defeated_count,
                &summary.run_id,
                &mut report.codex_updates,
            );
        }
        for boss_id in &summary.bosses_defeated {
            record_codex_defeat(
                &mut self.codex.bosses,
                boss_id,
                1,
                &summary.run_id,
                &mut report.codex_updates,
            );
        }

        apply_chapter_goals(self, summary, &mut report);
        report
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetaRunSummary {
    pub run_id: String,
    pub mode: RunMode,
    pub map_id: String,
    pub character_id: String,
    pub duration_seconds: f32,
    pub victory: bool,
    pub terminal_reason: String,
    pub kills: u32,
    pub level: u32,
    pub xp_collected: f32,
    pub damage_dealt_by_weapon: f32,
    pub damage_taken: f32,
    pub damage_taken_by_source: BTreeMap<String, f32>,
    pub boss_damage: f32,
    pub weapon_levels: BTreeMap<String, u32>,
    pub passives_used: BTreeSet<String>,
    pub evolutions_used: BTreeSet<String>,
    pub enemies_defeated: BTreeMap<String, u32>,
    pub bosses_defeated: BTreeSet<String>,
}

impl MetaRunSummary {
    pub fn from_metrics(
        run_id: impl Into<String>,
        config: &RunConfig,
        metrics: &RunMetrics,
    ) -> Self {
        let mut weapon_levels = metrics.weapon_levels.clone();
        for weapon_id in &config.starting_loadout.weapons {
            weapon_levels.entry(weapon_id.clone()).or_insert(1);
        }
        for choice in &metrics.upgrade_choices {
            if let Some((weapon_id, level)) = parse_weapon_level_choice(choice) {
                weapon_levels
                    .entry(weapon_id)
                    .and_modify(|current| *current = (*current).max(level))
                    .or_insert(level);
            }
        }
        let passives_used = metrics.passive_levels.keys().cloned().collect();

        Self {
            run_id: run_id.into(),
            mode: RunMode::StandardPatrol,
            map_id: config.map_id.clone(),
            character_id: config.character_id.clone(),
            duration_seconds: metrics.duration_seconds,
            victory: is_standard_patrol_victory(config, metrics),
            terminal_reason: metrics
                .terminal
                .as_ref()
                .map(|terminal| terminal.reason.clone())
                .unwrap_or_else(|| "not_terminal".to_string()),
            kills: metrics.kills,
            level: metrics.level,
            xp_collected: metrics.xp_collected,
            damage_dealt_by_weapon: metrics.damage_dealt_by_weapon,
            damage_taken: metrics.damage_taken,
            damage_taken_by_source: metrics.damage_taken_by_source.clone(),
            boss_damage: metrics.boss_damage,
            weapon_levels,
            passives_used,
            evolutions_used: metrics.evolutions_obtained.clone(),
            enemies_defeated: metrics.enemies_defeated.clone(),
            bosses_defeated: metrics.bosses_defeated.clone(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetaSettlementReport {
    pub run_id: String,
    pub mode: RunMode,
    pub run_summary: MetaRunSummary,
    pub resources_gained: MetaResourceWallet,
    pub completed_goals: Vec<String>,
    pub unlocked: Vec<MetaUnlock>,
    pub codex_updates: Vec<String>,
    pub notes: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetaUnlock {
    pub kind: String,
    pub id: String,
    pub reason: String,
}

pub fn apply_demo_meta_settlement(
    summary: &MetaRunSummary,
) -> (MetaProgress, MetaSettlementReport) {
    let mut progress = MetaProgress::demo_start();
    let report = progress.apply_run_summary(summary);
    (progress, report)
}

fn calculate_run_rewards(summary: &MetaRunSummary) -> MetaResourceWallet {
    let survival = (summary.duration_seconds / 12.0).floor().max(0.0) as u32;
    let kill_bonus = summary.kills / 8;
    let level_bonus = summary.level.saturating_sub(1) * 3;
    let victory_bonus = if summary.victory { 40 } else { 0 };
    let boss_bonus = summary.bosses_defeated.len() as u32 * 25;
    let storm_grains = match summary.mode {
        RunMode::DailyStorm | RunMode::EndlessStorm if summary.victory => 1,
        _ => 0,
    };

    MetaResourceWallet {
        candy_crystal_shards: survival + kill_bonus + level_bonus + victory_bonus + boss_bonus,
        star_shards: 0,
        storm_grains,
    }
}

fn is_standard_patrol_victory(config: &RunConfig, metrics: &RunMetrics) -> bool {
    metrics
        .terminal
        .as_ref()
        .is_some_and(|terminal| terminal.kind == TerminalKind::Victory)
        && config.duration_seconds >= STANDARD_PATROL_SECONDS
        && metrics.duration_seconds >= STANDARD_PATROL_SECONDS
}

fn apply_chapter_goals(
    progress: &mut MetaProgress,
    summary: &MetaRunSummary,
    report: &mut MetaSettlementReport,
) {
    let Some((chapter_id, boss_id)) = chapter_for_map(&summary.map_id) else {
        return;
    };

    let mut earned_star_shards = 0;
    complete_goal(
        progress,
        report,
        chapter_id,
        "survive-10-minutes",
        summary.duration_seconds >= 600.0,
        &mut earned_star_shards,
    );
    complete_goal(
        progress,
        report,
        chapter_id,
        &format!("defeat-{boss_id}"),
        summary.bosses_defeated.contains(boss_id),
        &mut earned_star_shards,
    );
    complete_goal(
        progress,
        report,
        chapter_id,
        "collect-200-candy-crystals",
        summary.xp_collected >= 200.0,
        &mut earned_star_shards,
    );
    if chapter_id == "frosting-grassland" {
        complete_goal(
            progress,
            report,
            "frosting-grassland",
            "rainbow-candy-shot-level-5",
            summary
                .weapon_levels
                .get("rainbow-candy-shot")
                .is_some_and(|level| *level >= 5),
            &mut earned_star_shards,
        );
    }
    if let Some(evolution_id) = chapter_target_evolution_id(chapter_id) {
        complete_goal(
            progress,
            report,
            chapter_id,
            &format!("evolve-{evolution_id}"),
            summary.evolutions_used.contains(evolution_id),
            &mut earned_star_shards,
        );
    }

    if earned_star_shards > 0 {
        progress.resources.star_shards += earned_star_shards;
        report.resources_gained.star_shards += earned_star_shards;
    }

    if summary.bosses_defeated.contains(boss_id) {
        if chapter_id == "frosting-grassland" {
            unlock(
                &mut progress.unlocks.weapons,
                report,
                "weapon",
                "marshmallow-shield",
                "defeated frosting-grassland chapter boss",
            );
        }
        if let Some(character_id) = chapter_character_unlock(chapter_id) {
            unlock(
                &mut progress.unlocks.characters,
                report,
                "character",
                character_id,
                "defeated chapter boss",
            );
        }
    }

    if let Some((next_chapter, required_star_shards)) = next_chapter_unlock(chapter_id) {
        let boss_goal = format!("defeat-{boss_id}");
        let chapter_boss_defeated = progress
            .chapters
            .get(chapter_id)
            .is_some_and(|chapter| chapter.completed_goals.contains(&boss_goal));
        if chapter_boss_defeated && progress.resources.star_shards >= required_star_shards {
            unlock(
                &mut progress.unlocks.maps,
                report,
                "map",
                next_chapter,
                "collected enough star shards",
            );
            unlock_chapter(
                progress,
                report,
                next_chapter,
                "collected enough star shards",
            );
        }
    }
}

fn chapter_for_map(map_id: &str) -> Option<(&'static str, &'static str)> {
    DEMO_CHAPTER_SEQUENCE
        .iter()
        .find(|(_, map, _, _)| *map == map_id)
        .map(|(chapter_id, _, boss_id, _)| (*chapter_id, *boss_id))
}

fn next_chapter_unlock(chapter_id: &str) -> Option<(&'static str, u32)> {
    DEMO_CHAPTER_SEQUENCE
        .iter()
        .find(|(id, _, _, _)| *id == chapter_id)
        .and_then(|(_, _, _, next)| *next)
}

fn chapter_character_unlock(chapter_id: &str) -> Option<&'static str> {
    match chapter_id {
        "frosting-grassland" => Some("bubble-courier"),
        "soda-creek" => Some("cream-knight"),
        "cotton-cloud-pasture" => Some("sour-plum-doctor"),
        "caramel-workshop" => Some("pudding-crafter"),
        _ => None,
    }
}

pub fn chapter_target_evolution_id(chapter_id: &str) -> Option<&'static str> {
    match chapter_id {
        "frosting-grassland" => Some("rainbow-candy-meteor"),
        "soda-creek" => Some("soda-volcano"),
        "cotton-cloud-pasture" => Some("marshmallow-fortress"),
        "caramel-workshop" => Some("caramel-vortex"),
        "jelly-platform" => Some("sugar-windmill"),
        "cracked-star-jar" => Some("star-sugar-prism"),
        _ => None,
    }
}

type DemoChapterSpec = (
    &'static str,
    &'static str,
    &'static str,
    Option<(&'static str, u32)>,
);

const DEMO_CHAPTER_SEQUENCE: &[DemoChapterSpec] = &[
    (
        "frosting-grassland",
        "frosting-grassland",
        "runaway-sugar-mixer",
        Some(("soda-creek", 2)),
    ),
    (
        "soda-creek",
        "soda-creek",
        "soda-fountain-dragon",
        Some(("cotton-cloud-pasture", 4)),
    ),
    (
        "cotton-cloud-pasture",
        "cotton-cloud-pasture",
        "giant-cotton-clump",
        Some(("caramel-workshop", 6)),
    ),
    (
        "caramel-workshop",
        "caramel-workshop",
        "caramel-furnace",
        Some(("jelly-platform", 8)),
    ),
    (
        "jelly-platform",
        "jelly-platform",
        "giant-gummy-bear-king",
        Some(("cracked-star-jar", 10)),
    ),
    (
        "cracked-star-jar",
        "cracked-star-jar",
        "cracked-star-jar-core",
        None,
    ),
];

fn demo_chapter_roster() -> BTreeMap<String, ChapterProgress> {
    DEMO_CHAPTER_SEQUENCE
        .iter()
        .map(|(chapter_id, map_id, boss_id, _)| {
            (
                *chapter_id,
                *map_id,
                *boss_id,
                *chapter_id == "frosting-grassland",
            )
        })
        .map(|(chapter_id, map_id, boss_id, unlocked)| {
            (
                chapter_id.to_string(),
                ChapterProgress {
                    chapter_id: chapter_id.to_string(),
                    map_id: map_id.to_string(),
                    boss_id: boss_id.to_string(),
                    unlocked,
                    completed_goals: BTreeSet::new(),
                },
            )
        })
        .collect()
}

fn complete_goal(
    progress: &mut MetaProgress,
    report: &mut MetaSettlementReport,
    chapter_id: &str,
    goal_id: &str,
    achieved: bool,
    earned_star_shards: &mut u32,
) {
    if !achieved {
        return;
    }
    let Some(chapter) = progress.chapters.get_mut(chapter_id) else {
        return;
    };
    if chapter.completed_goals.insert(goal_id.to_string()) {
        report
            .completed_goals
            .push(format!("{chapter_id}:{goal_id}"));
        *earned_star_shards += 1;
    }
}

fn unlock(
    set: &mut BTreeSet<String>,
    report: &mut MetaSettlementReport,
    kind: &str,
    id: &str,
    reason: &str,
) -> bool {
    if set.insert(id.to_string()) {
        report.unlocked.push(MetaUnlock {
            kind: kind.to_string(),
            id: id.to_string(),
            reason: reason.to_string(),
        });
        true
    } else {
        false
    }
}

fn unlock_chapter(
    progress: &mut MetaProgress,
    report: &mut MetaSettlementReport,
    chapter_id: &str,
    reason: &str,
) {
    let newly_unlocked = unlock(
        &mut progress.unlocks.chapters,
        report,
        "chapter",
        chapter_id,
        reason,
    );
    if newly_unlocked || progress.unlocks.chapters.contains(chapter_id) {
        if let Some(chapter) = progress.chapters.get_mut(chapter_id) {
            chapter.unlocked = true;
        }
    }
}

fn record_codex_use(
    codex: &mut BTreeMap<String, MetaCodexEntry>,
    id: &str,
    run_id: &str,
    updates: &mut Vec<String>,
) {
    let entry = codex.entry(id.to_string()).or_default();
    let was_discovered = entry.discovered;
    entry.discovered = true;
    entry.used_count += 1;
    entry.seen_count += 1;
    if entry.first_seen_run.is_none() {
        entry.first_seen_run = Some(run_id.to_string());
    }
    if !was_discovered {
        updates.push(format!("discovered:{id}"));
    }
}

fn record_codex_defeat(
    codex: &mut BTreeMap<String, MetaCodexEntry>,
    id: &str,
    defeated_count: u32,
    run_id: &str,
    updates: &mut Vec<String>,
) {
    if defeated_count == 0 {
        return;
    }
    let entry = codex.entry(id.to_string()).or_default();
    let was_discovered = entry.discovered;
    entry.discovered = true;
    entry.seen_count += defeated_count;
    entry.defeated_count += defeated_count;
    if entry.first_seen_run.is_none() {
        entry.first_seen_run = Some(run_id.to_string());
    }
    if !was_discovered {
        updates.push(format!("discovered:{id}"));
    }
}

fn parse_weapon_level_choice(choice: &str) -> Option<(String, u32)> {
    let (weapon_id, level_text) = choice.rsplit_once("-level-")?;
    let level = level_text.parse::<u32>().ok()?;
    Some((weapon_id.to_string(), level))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{Difficulty, RunConfig, StartingLoadout, TerminalState};

    fn base_summary() -> MetaRunSummary {
        MetaRunSummary {
            run_id: "run_001".to_string(),
            mode: RunMode::StandardPatrol,
            map_id: "frosting-grassland".to_string(),
            character_id: "jar-keeper".to_string(),
            duration_seconds: 180.0,
            victory: false,
            terminal_reason: "player_health_depleted".to_string(),
            kills: 30,
            level: 4,
            xp_collected: 80.0,
            damage_dealt_by_weapon: 320.0,
            damage_taken: 18.5,
            damage_taken_by_source: BTreeMap::from([("contact".to_string(), 18.5)]),
            boss_damage: 0.0,
            weapon_levels: BTreeMap::from([("rainbow-candy-shot".to_string(), 3)]),
            passives_used: BTreeSet::from(["big-candy-jar".to_string()]),
            evolutions_used: BTreeSet::new(),
            enemies_defeated: BTreeMap::from([("bouncy-gummy".to_string(), 30)]),
            bosses_defeated: BTreeSet::new(),
        }
    }

    #[test]
    fn demo_start_contains_full_chapter_roster() {
        let progress = MetaProgress::demo_start();

        assert_eq!(progress.chapters.len(), 6);
        assert!(progress.chapters["frosting-grassland"].unlocked);
        assert!(!progress.chapters["soda-creek"].unlocked);
        assert_eq!(
            progress.chapters["cracked-star-jar"].boss_id,
            "cracked-star-jar-core"
        );
        assert!(progress.unlocks.chapters.contains("frosting-grassland"));
        assert!(!progress.unlocks.chapters.contains("soda-creek"));
    }

    #[test]
    fn failed_run_still_grants_resources_and_codex_progress() {
        let mut progress = MetaProgress::demo_start();
        let report = progress.apply_run_summary(&base_summary());

        assert!(report.resources_gained.candy_crystal_shards > 0);
        assert_eq!(report.resources_gained.star_shards, 0);
        assert_eq!(report.run_summary.duration_seconds, 180.0);
        assert_eq!(report.run_summary.damage_taken, 18.5);
        assert_eq!(
            progress
                .codex
                .enemies
                .get("bouncy-gummy")
                .map(|entry| entry.defeated_count),
            Some(30)
        );
    }

    #[test]
    fn settlement_records_passive_and_evolution_codex_progress() {
        let mut summary = base_summary();
        summary
            .evolutions_used
            .insert("rainbow-candy-meteor".to_string());
        let mut progress = MetaProgress::demo_start();
        let report = progress.apply_run_summary(&summary);

        assert!(report
            .codex_updates
            .contains(&"discovered:big-candy-jar".to_string()));
        assert!(report
            .codex_updates
            .contains(&"discovered:rainbow-candy-meteor".to_string()));
        assert_eq!(
            progress
                .codex
                .passives
                .get("big-candy-jar")
                .map(|entry| entry.used_count),
            Some(1)
        );
        assert_eq!(
            progress
                .codex
                .evolutions
                .get("rainbow-candy-meteor")
                .map(|entry| entry.used_count),
            Some(1)
        );
    }

    #[test]
    fn chapter_evolution_goal_completes_from_run_summary() {
        let mut summary = base_summary();
        summary
            .evolutions_used
            .insert("rainbow-candy-meteor".to_string());
        let mut progress = MetaProgress::demo_start();
        let report = progress.apply_run_summary(&summary);

        assert!(report
            .completed_goals
            .contains(&"frosting-grassland:evolve-rainbow-candy-meteor".to_string()));
        assert!(progress.chapters["frosting-grassland"]
            .completed_goals
            .contains("evolve-rainbow-candy-meteor"));
    }

    #[test]
    fn chapter_boss_and_star_shards_unlock_next_map() {
        let mut summary = base_summary();
        summary.run_id = "run_002".to_string();
        summary.duration_seconds = 600.0;
        summary.victory = true;
        summary.xp_collected = 210.0;
        summary
            .weapon_levels
            .insert("rainbow-candy-shot".to_string(), 5);
        summary
            .bosses_defeated
            .insert("runaway-sugar-mixer".to_string());

        let mut progress = MetaProgress::demo_start();
        let report = progress.apply_run_summary(&summary);

        assert!(report
            .completed_goals
            .contains(&"frosting-grassland:survive-10-minutes".to_string()));
        assert!(progress.unlocks.maps.contains("soda-creek"));
        assert!(progress.chapters["soda-creek"].unlocked);
        assert!(progress.unlocks.characters.contains("bubble-courier"));
        assert!(progress.resources.star_shards >= 2);
    }

    #[test]
    fn later_chapter_goals_unlock_following_map_with_star_shards() {
        let mut summary = base_summary();
        summary.run_id = "run_003".to_string();
        summary.map_id = "soda-creek".to_string();
        summary.duration_seconds = 600.0;
        summary.victory = true;
        summary.xp_collected = 220.0;
        summary
            .bosses_defeated
            .insert("soda-fountain-dragon".to_string());

        let mut progress = MetaProgress::demo_start();
        progress.resources.star_shards = 1;
        progress.unlocks.maps.insert("soda-creek".to_string());
        progress.unlocks.chapters.insert("soda-creek".to_string());
        progress.chapters.get_mut("soda-creek").unwrap().unlocked = true;
        let report = progress.apply_run_summary(&summary);

        assert!(report
            .completed_goals
            .contains(&"soda-creek:survive-10-minutes".to_string()));
        assert!(report
            .completed_goals
            .contains(&"soda-creek:defeat-soda-fountain-dragon".to_string()));
        assert!(report
            .completed_goals
            .contains(&"soda-creek:collect-200-candy-crystals".to_string()));
        assert!(progress.unlocks.maps.contains("cotton-cloud-pasture"));
        assert!(progress.chapters["cotton-cloud-pasture"].unlocked);
        assert!(progress.unlocks.characters.contains("cream-knight"));
        assert!(report
            .unlocked
            .iter()
            .any(|unlock| unlock.kind == "character" && unlock.id == "cream-knight"));
        assert_eq!(progress.resources.star_shards, 4);
    }

    #[test]
    fn chapter_bosses_unlock_remaining_demo_characters() {
        let mut progress = MetaProgress::demo_start();
        progress.resources.star_shards = 20;
        for chapter_id in ["soda-creek", "cotton-cloud-pasture", "caramel-workshop"] {
            progress.unlocks.maps.insert(chapter_id.to_string());
            progress.unlocks.chapters.insert(chapter_id.to_string());
            progress.chapters.get_mut(chapter_id).unwrap().unlocked = true;
        }

        for (map_id, boss_id) in [
            ("soda-creek", "soda-fountain-dragon"),
            ("cotton-cloud-pasture", "giant-cotton-clump"),
            ("caramel-workshop", "caramel-furnace"),
        ] {
            let mut summary = base_summary();
            summary.map_id = map_id.to_string();
            summary.bosses_defeated.insert(boss_id.to_string());
            progress.apply_run_summary(&summary);
        }

        assert!(progress.unlocks.characters.contains("cream-knight"));
        assert!(progress.unlocks.characters.contains("sour-plum-doctor"));
        assert!(progress.unlocks.characters.contains("pudding-crafter"));
    }

    #[test]
    fn short_duration_reached_does_not_complete_ten_minute_goal() {
        let mut summary = base_summary();
        summary.duration_seconds = 120.0;
        summary.victory = true;
        summary.xp_collected = 210.0;

        let mut progress = MetaProgress::demo_start();
        let report = progress.apply_run_summary(&summary);

        assert!(!report
            .completed_goals
            .contains(&"frosting-grassland:survive-10-minutes".to_string()));
        assert!(!progress.unlocks.maps.contains("soda-creek"));
    }

    #[test]
    fn run_metrics_summary_preserves_starting_weapon_and_terminal() {
        let config = RunConfig {
            seed: 1,
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
            tick_rate: 30,
        };
        let metrics = RunMetrics {
            seed: 1,
            tick_rate: 30,
            duration_seconds: 600.0,
            terminal: Some(TerminalState {
                kind: TerminalKind::Victory,
                time_seconds: 600.0,
                reason: "duration_reached".to_string(),
                final_level: 5,
                kills: 100,
            }),
            kills: 100,
            level: 5,
            xp_collected: 150.0,
            xp_dropped: 180.0,
            damage_dealt_by_weapon: 1_000.0,
            damage_taken: 10.0,
            damage_taken_by_source: BTreeMap::from([("contact".to_string(), 10.0)]),
            weapon_levels: BTreeMap::from([("rainbow-candy-shot".to_string(), 5)]),
            passive_levels: BTreeMap::from([("candy-crystal-lens".to_string(), 2)]),
            evolutions_obtained: BTreeSet::from(["rainbow-candy-meteor".to_string()]),
            boss_damage: 250.0,
            boss_kill_times: vec![580.0],
            enemies_defeated: BTreeMap::from([("bouncy-gummy".to_string(), 7)]),
            bosses_defeated: BTreeSet::from(["runaway-sugar-mixer".to_string()]),
            max_enemy_count: 30,
            max_projectile_count: 20,
            upgrade_choices: vec!["rainbow-candy-shot-level-5".to_string()],
        };

        let summary = MetaRunSummary::from_metrics("run_metrics", &config, &metrics);

        assert!(summary.victory);
        assert_eq!(summary.weapon_levels["rainbow-candy-shot"], 5);
        assert_eq!(summary.damage_dealt_by_weapon, 1_000.0);
        assert_eq!(summary.damage_taken, 10.0);
        assert_eq!(summary.damage_taken_by_source["contact"], 10.0);
        assert_eq!(summary.boss_damage, 250.0);
        assert!(summary.passives_used.contains("candy-crystal-lens"));
        assert!(summary.evolutions_used.contains("rainbow-candy-meteor"));
        assert_eq!(summary.enemies_defeated.get("bouncy-gummy"), Some(&7));
        assert!(summary.bosses_defeated.contains("runaway-sugar-mixer"));
    }

    #[test]
    fn run_metrics_summary_preserves_replaced_weapon_level_history() {
        let config = RunConfig {
            seed: 7,
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
            tick_rate: 30,
        };
        let metrics = RunMetrics {
            seed: 7,
            tick_rate: 30,
            duration_seconds: 600.0,
            terminal: Some(TerminalState {
                kind: TerminalKind::Victory,
                time_seconds: 600.0,
                reason: "duration_reached".to_string(),
                final_level: 8,
                kills: 160,
            }),
            kills: 160,
            level: 8,
            xp_collected: 220.0,
            xp_dropped: 30.0,
            damage_dealt_by_weapon: 1_500.0,
            damage_taken: 3.0,
            damage_taken_by_source: BTreeMap::new(),
            weapon_levels: BTreeMap::from([("rainbow-candy-meteor".to_string(), 1)]),
            passive_levels: BTreeMap::from([("candy-crystal-lens".to_string(), 3)]),
            evolutions_obtained: BTreeSet::from(["rainbow-candy-meteor".to_string()]),
            boss_damage: 400.0,
            boss_kill_times: vec![210.0],
            enemies_defeated: BTreeMap::new(),
            bosses_defeated: BTreeSet::new(),
            max_enemy_count: 20,
            max_projectile_count: 12,
            upgrade_choices: vec!["rainbow-candy-shot-level-5".to_string()],
        };

        let summary = MetaRunSummary::from_metrics("run_evolved", &config, &metrics);

        assert_eq!(summary.weapon_levels["rainbow-candy-shot"], 5);
        assert_eq!(summary.weapon_levels["rainbow-candy-meteor"], 1);
        assert!(summary.evolutions_used.contains("rainbow-candy-meteor"));
    }

    #[test]
    fn short_technical_duration_reached_is_not_meta_victory() {
        let config = RunConfig {
            seed: 1,
            map_id: "frosting-grassland".to_string(),
            character_id: "jar-keeper".to_string(),
            starting_loadout: StartingLoadout {
                weapons: vec!["rainbow-candy-shot".to_string()],
                passives: Vec::new(),
            },
            difficulty: Difficulty::Normal,
            duration_seconds: 120.0,
            ruleset_version: "prototype-v0".to_string(),
            content_pack_ids: vec!["base-demo".to_string()],
            tick_rate: 30,
        };
        let metrics = RunMetrics {
            seed: 1,
            tick_rate: 30,
            duration_seconds: 120.0,
            terminal: Some(TerminalState {
                kind: TerminalKind::Victory,
                time_seconds: 120.0,
                reason: "duration_reached".to_string(),
                final_level: 3,
                kills: 40,
            }),
            kills: 40,
            level: 3,
            xp_collected: 90.0,
            xp_dropped: 100.0,
            damage_dealt_by_weapon: 400.0,
            damage_taken: 8.0,
            damage_taken_by_source: BTreeMap::from([("hazard".to_string(), 8.0)]),
            weapon_levels: BTreeMap::new(),
            passive_levels: BTreeMap::new(),
            evolutions_obtained: BTreeSet::new(),
            boss_damage: 0.0,
            boss_kill_times: Vec::new(),
            enemies_defeated: BTreeMap::new(),
            bosses_defeated: BTreeSet::new(),
            max_enemy_count: 20,
            max_projectile_count: 10,
            upgrade_choices: Vec::new(),
        };

        let summary = MetaRunSummary::from_metrics("short_smoke", &config, &metrics);
        let (_progress, report) = apply_demo_meta_settlement(&summary);

        assert!(!summary.victory);
        assert_eq!(report.resources_gained.candy_crystal_shards, 21);
    }
}
