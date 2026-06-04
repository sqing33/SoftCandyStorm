#!/usr/bin/env python3
"""Shared configuration for the current playable content candidate.

This module points at the latest generated candidate that should be prepared
for human quick play and content-tour review. It does not promote the candidate
or copy files into the official runtime content pool.
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass
from pathlib import Path


CANDIDATE_ID = "2026-06-04_demo_buildcraft_repair_v51_full_pack"
CANDIDATE_LABEL = "v51"
CONTENT_HASH = "fnv1a64:50bd536bd0669e2b"
CONTENT_DIR = Path("harness/generated_candidates/2026-06-04_demo_buildcraft_repair_v51_full_pack")
DEFAULT_SECONDS = 600
DEFAULT_CAPTURE_INTERVAL = 2
REPORT_PREFIX_QUICK_PLAY = "harness/telemetry/local/v51_quick_play"
REPORT_PREFIX_CONTENT_TOUR = "harness/telemetry/local/v51_content_tour"

FORBIDDEN_MANUAL_FLAGS = {
    "--demo-input",
    "--simulation-speed",
    "--auto-exit-after-report",
}


@dataclass(frozen=True)
class QuickPlayPreset:
    preset_id: str
    title: str
    character_id: str
    map_id: str
    seed: int
    focus: str

    @property
    def report_path(self) -> Path:
        return Path(f"{REPORT_PREFIX_QUICK_PLAY}_{self.preset_id}.json")


@dataclass(frozen=True)
class ContentTourRun:
    run_id: str
    character_id: str
    map_id: str
    seed: int
    focus: str

    @property
    def report_path(self) -> Path:
        return Path(f"{REPORT_PREFIX_CONTENT_TOUR}_{self.run_id}.json")


QUICK_PLAY_PRESETS: tuple[QuickPlayPreset, ...] = (
    QuickPlayPreset("default", "默认新手局", "jar-keeper", "frosting-grassland", 55101, "糖罐守护员和糖霜草地基准体验"),
    QuickPlayPreset("speed", "速度拾取局", "bubble-courier", "soda-creek", 55102, "泡泡邮差和汽水溪谷移动压力"),
    QuickPlayPreset("summon", "召唤经营局", "pudding-crafter", "cotton-cloud-pasture", 55103, "布丁工匠和棉花云群体压力"),
    QuickPlayPreset("control", "控场路线局", "sour-plum-doctor", "caramel-workshop", 55104, "酸梅博士和焦糖工坊路线干扰"),
    QuickPlayPreset("defense", "防御近身局", "cream-knight", "jelly-platform", 55105, "奶油骑士和果冻月台环形路线"),
    QuickPlayPreset("final", "终局压力局", "jar-keeper", "cracked-star-jar", 55106, "裂星糖罐混合怪潮压力"),
)

CONTENT_TOUR_RUNS: tuple[ContentTourRun, ...] = (
    ContentTourRun("frosting_jar_keeper", "jar-keeper", "frosting-grassland", 55201, "新手基准角色和糖霜草地开局"),
    ContentTourRun("soda_bubble_courier", "bubble-courier", "soda-creek", 55202, "速度角色和汽水溪谷泡泡压力"),
    ContentTourRun("cotton_pudding_crafter", "pudding-crafter", "cotton-cloud-pasture", 55203, "召唤角色和棉花云群体压力"),
    ContentTourRun("caramel_sour_plum_doctor", "sour-plum-doctor", "caramel-workshop", 55204, "控制角色和焦糖工坊路线干扰"),
    ContentTourRun("jelly_cream_knight", "cream-knight", "jelly-platform", 55205, "防御角色和果冻月台环形路线"),
    ContentTourRun("cracked_jar_keeper", "jar-keeper", "cracked-star-jar", 55206, "最终地图混合怪潮压力"),
)


def shell_quote(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def validate_human_runtime_command(command: list[str], *, label: str) -> None:
    forbidden = sorted(flag for flag in FORBIDDEN_MANUAL_FLAGS if flag in command)
    if forbidden:
        raise ValueError(f"{label} command must not include automation flags: {', '.join(forbidden)}")


def build_runtime_command(
    *,
    character_id: str,
    map_id: str,
    seed: int,
    player_skill: str,
    report_path: Path | None,
    seconds: int = DEFAULT_SECONDS,
    capture_interval: int = DEFAULT_CAPTURE_INTERVAL,
    release: bool = False,
) -> list[str]:
    command = ["cargo", "run"]
    if release:
        command.append("--release")
    command.extend(
        [
            "-p",
            "game_runtime",
            "--",
            "--content-dir",
            str(CONTENT_DIR),
            "--character-id",
            character_id,
            "--map-id",
            map_id,
            "--seed",
            str(seed),
            "--seconds",
            str(seconds),
            "--player-skill",
            player_skill,
        ]
    )
    if report_path is not None:
        command.extend(
            [
                "--playtest-report",
                str(report_path),
                "--capture-interval",
                str(capture_interval),
            ]
        )
    return command
