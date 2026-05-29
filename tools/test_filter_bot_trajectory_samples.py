import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from filter_bot_trajectory_samples import build_report  # noqa: E402


def write_jsonl(path, records):
    path.write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )


def read_jsonl(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def sample(seed, time_seconds, action, health_ratio=0.7, map_id="cracked-star-jar"):
    return {
        "record_type": "sample",
        "seed": seed,
        "map_id": map_id,
        "bot": "kite",
        "tick": int(time_seconds * 30),
        "time_seconds": time_seconds,
        "health_ratio": health_ratio,
        "level": 8,
        "kills": 200,
        "action": action,
        "movement": [0.0, 1.0],
        "observation": [0.1, 0.2, 0.3],
    }


def episode(seed, terminal, map_id="cracked-star-jar"):
    return {
        "record_type": "episode",
        "seed": seed,
        "map_id": map_id,
        "bot": "kite",
        "terminal": terminal,
        "reason": "victory" if terminal == "victory" else "player_health_depleted",
        "duration_seconds": 300.0 if terminal == "victory" else 225.0,
        "kills": 300,
        "level": 9,
        "damage_taken": 80.0,
        "samples": 2,
        "upgrade_samples": 0,
        "skipped_upgrade_samples": 0,
    }


def test_filters_victory_terminal_window_samples(tmp_path):
    source = tmp_path / "trajectories.jsonl"
    out = tmp_path / "filtered.jsonl"
    write_jsonl(
        source,
        [
            {
                "record_type": "metadata",
                "dataset_version": "bot-trajectory-v0",
                "bot": "kite",
                "map_id": "cracked-star-jar",
                "observation_version": 2,
                "observation_len": 3,
                "action_count": 9,
                "content_hash": "abc",
            },
            sample(1, 205.0, 1),
            sample(1, 220.0, 2),
            episode(1, "victory"),
            sample(2, 220.0, 3),
            episode(2, "player_health_depleted"),
        ],
    )

    report = build_report(
        [source],
        out=out,
        terminal_filter="victory",
        map_ids={"cracked-star-jar"},
        min_seconds=210.0,
        max_seconds=240.0,
    )
    records = read_jsonl(out)

    assert report["decision"] == "bot_trajectory_samples_filtered"
    assert report["kept_sample_count"] == 1
    assert report["kept_episode_count"] == 1
    assert report["dropped_samples"] == {"time_before_min": 1}
    assert records[0]["record_type"] == "metadata"
    assert records[1]["record_type"] == "sample"
    assert records[1]["seed"] == 1
    assert records[1]["time_seconds"] == 220.0
    assert records[2]["record_type"] == "episode"
    assert records[-1]["record_type"] == "summary"


def test_empty_filter_requires_allow_empty(tmp_path):
    source = tmp_path / "trajectories.jsonl"
    out = tmp_path / "filtered.jsonl"
    write_jsonl(
        source,
        [
            sample(1, 220.0, 2),
            episode(1, "player_health_depleted"),
        ],
    )

    report = build_report([source], out=out, terminal_filter="victory")

    assert report["decision"] == "bot_trajectory_samples_filter_invalid"
    assert report["errors"] == ["no samples matched the requested filters"]
    assert not out.exists()


def test_max_total_samples_updates_episode_sample_count(tmp_path):
    source = tmp_path / "trajectories.jsonl"
    out = tmp_path / "filtered.jsonl"
    write_jsonl(
        source,
        [
            sample(1, 220.0, 2),
            sample(1, 221.0, 3),
            sample(1, 222.0, 4),
            episode(1, "victory"),
        ],
    )

    report = build_report([source], out=out, max_total_samples=2)
    records = read_jsonl(out)
    episodes = [record for record in records if record["record_type"] == "episode"]
    samples = [record for record in records if record["record_type"] == "sample"]

    assert report["kept_sample_count"] == 2
    assert len(samples) == 2
    assert episodes == [
        {
            **episode(1, "victory"),
            "filtered_sample_count": 2,
        }
    ]
