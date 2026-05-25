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

        let mut chapters = BTreeMap::new();
        chapters.insert(
            "frosting-grassland".to_string(),
            ChapterProgress {
                chapter_id: "frosting-grassland".to_string(),
                map_id: "frosting-grassland".to_string(),
                boss_id: "runaway-sugar-mixer".to_string(),
                unlocked: true,
                completed_goals: BTreeSet::new(),
            },
        );

        Self {
            resources: MetaResourceWallet::default(),
            unlocks,
            codex: MetaCodex::default(),
            chapters,
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

        apply_frosting_grassland_goals(self, summary, &mut report);
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
    pub weapon_levels: BTreeMap<String, u32>,
    pub passives_used: BTreeSet<String>,
    pub enemies_defeated: BTreeMap<String, u32>,
    pub bosses_defeated: BTreeSet<String>,
}

impl MetaRunSummary {
    pub fn from_metrics(
        run_id: impl Into<String>,
        config: &RunConfig,
        metrics: &RunMetrics,
    ) -> Self {
        let mut weapon_levels = BTreeMap::new();
        for weapon_id in &config.starting_loadout.weapons {
            weapon_levels.insert(weapon_id.clone(), 1);
        }
        for choice in &metrics.upgrade_choices {
            if let Some((weapon_id, level)) = parse_weapon_level_choice(choice) {
                weapon_levels
                    .entry(weapon_id)
                    .and_modify(|current| *current = (*current).max(level))
                    .or_insert(level);
            }
        }

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
            weapon_levels,
            passives_used: BTreeSet::new(),
            enemies_defeated: BTreeMap::new(),
            bosses_defeated: BTreeSet::new(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetaSettlementReport {
    pub run_id: String,
    pub mode: RunMode,
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

fn apply_frosting_grassland_goals(
    progress: &mut MetaProgress,
    summary: &MetaRunSummary,
    report: &mut MetaSettlementReport,
) {
    if summary.map_id != "frosting-grassland" {
        return;
    }

    let mut earned_star_shards = 0;
    complete_goal(
        progress,
        report,
        "frosting-grassland",
        "survive-10-minutes",
        summary.duration_seconds >= 600.0,
        &mut earned_star_shards,
    );
    complete_goal(
        progress,
        report,
        "frosting-grassland",
        "defeat-runaway-sugar-mixer",
        summary.bosses_defeated.contains("runaway-sugar-mixer"),
        &mut earned_star_shards,
    );
    complete_goal(
        progress,
        report,
        "frosting-grassland",
        "collect-200-candy-crystals",
        summary.xp_collected >= 200.0,
        &mut earned_star_shards,
    );
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

    if earned_star_shards > 0 {
        progress.resources.star_shards += earned_star_shards;
        report.resources_gained.star_shards += earned_star_shards;
    }

    if summary.bosses_defeated.contains("runaway-sugar-mixer") {
        unlock(
            &mut progress.unlocks.weapons,
            report,
            "weapon",
            "marshmallow-shield",
            "defeated frosting-grassland chapter boss",
        );
        unlock(
            &mut progress.unlocks.characters,
            report,
            "character",
            "bubble-courier",
            "defeated frosting-grassland chapter boss",
        );
    }

    let chapter_boss_defeated =
        progress
            .chapters
            .get("frosting-grassland")
            .is_some_and(|chapter| {
                chapter
                    .completed_goals
                    .contains("defeat-runaway-sugar-mixer")
            });
    if chapter_boss_defeated && progress.resources.star_shards >= 2 {
        unlock(
            &mut progress.unlocks.maps,
            report,
            "map",
            "soda-creek",
            "collected enough star shards",
        );
        unlock(
            &mut progress.unlocks.chapters,
            report,
            "chapter",
            "soda-creek",
            "collected enough star shards",
        );
    }
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
) {
    if set.insert(id.to_string()) {
        report.unlocked.push(MetaUnlock {
            kind: kind.to_string(),
            id: id.to_string(),
            reason: reason.to_string(),
        });
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
            weapon_levels: BTreeMap::from([("rainbow-candy-shot".to_string(), 3)]),
            passives_used: BTreeSet::from(["big-candy-jar".to_string()]),
            enemies_defeated: BTreeMap::from([("bouncy-gummy".to_string(), 30)]),
            bosses_defeated: BTreeSet::new(),
        }
    }

    #[test]
    fn failed_run_still_grants_resources_and_codex_progress() {
        let mut progress = MetaProgress::demo_start();
        let report = progress.apply_run_summary(&base_summary());

        assert!(report.resources_gained.candy_crystal_shards > 0);
        assert_eq!(report.resources_gained.star_shards, 0);
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
        assert!(progress.unlocks.characters.contains("bubble-courier"));
        assert!(progress.resources.star_shards >= 2);
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
            max_enemy_count: 30,
            max_projectile_count: 20,
            upgrade_choices: vec!["rainbow-candy-shot-level-5".to_string()],
        };

        let summary = MetaRunSummary::from_metrics("run_metrics", &config, &metrics);

        assert!(summary.victory);
        assert_eq!(summary.weapon_levels["rainbow-candy-shot"], 5);
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
