import argparse
import random
from datetime import datetime, timezone
from pathlib import Path

try:
    from python.train.train_behavior_clone import (
        dependency_status,
        load_upgrade_choice_dataset,
        require_dependencies,
        summarize_upgrade_choice_dataset,
        write_report,
    )
except ModuleNotFoundError:
    from train_behavior_clone import (
        dependency_status,
        load_upgrade_choice_dataset,
        require_dependencies,
        summarize_upgrade_choice_dataset,
        write_report,
    )


def build_upgrade_vocabulary(dataset):
    seen = set()
    vocabulary = []
    for sample in dataset["samples"]:
        for option in sample["upgrade_options"]:
            if option not in seen:
                seen.add(option)
                vocabulary.append(option)
    return sorted(vocabulary)


def normalize_chosen_upgrade(sample):
    options = sample["upgrade_options"]
    chosen_index = sample.get("chosen_index")
    chosen_id = sample.get("chosen_upgrade_id")
    if chosen_index is not None:
        if chosen_index < 0 or chosen_index >= len(options):
            raise ValueError(
                f"chosen_index {chosen_index} is outside upgrade option range for seed {sample.get('seed')}"
            )
        indexed_id = options[chosen_index]
        if chosen_id is None:
            chosen_id = indexed_id
        elif chosen_id != indexed_id:
            raise ValueError(
                f"chosen_upgrade_id `{chosen_id}` does not match chosen_index {chosen_index}"
            )
    if chosen_id is None:
        raise ValueError("upgrade_sample must include chosen_upgrade_id or chosen_index")
    if chosen_id not in options:
        raise ValueError(f"chosen_upgrade_id `{chosen_id}` is not present in upgrade_options")
    return chosen_id


def build_upgrade_choice_rows(dataset, vocabulary=None):
    if vocabulary is None:
        vocabulary = build_upgrade_vocabulary(dataset)
    option_to_index = {option: index for index, option in enumerate(vocabulary)}
    features = []
    labels = []
    group_ids = []
    row_options = []
    group_chosen = []
    group_metadata = []
    observation_len = None

    for group_id, sample in enumerate(dataset["samples"]):
        observation = [float(value) for value in sample["observation"]]
        if observation_len is None:
            observation_len = len(observation)
        elif len(observation) != observation_len:
            raise ValueError("upgrade choice dataset contains mixed observation lengths")
        chosen_id = normalize_chosen_upgrade(sample)
        group_chosen.append(chosen_id)
        group_metadata.append(
            {
                "seed": sample.get("seed"),
                "map_id": sample.get("map_id"),
                "time_seconds": sample.get("time_seconds"),
                "level": sample.get("level"),
                "kills": sample.get("kills"),
            }
        )
        for option in sample["upgrade_options"]:
            option_features = [0.0] * len(vocabulary)
            option_features[option_to_index[option]] = 1.0
            features.append(observation + option_features)
            labels.append(1.0 if option == chosen_id else 0.0)
            group_ids.append(group_id)
            row_options.append(option)

    positive_rows = sum(1 for label in labels if label > 0.5)
    if positive_rows != len(dataset["samples"]):
        raise ValueError("each upgrade sample must produce exactly one positive option row")
    return {
        "features": features,
        "labels": labels,
        "group_ids": group_ids,
        "row_options": row_options,
        "group_chosen": group_chosen,
        "group_metadata": group_metadata,
        "vocabulary": vocabulary,
        "observation_len": observation_len or 0,
        "input_len": (observation_len or 0) + len(vocabulary),
    }


def summarize_upgrade_choice_rows(rows):
    row_count = len(rows["labels"])
    positive_count = sum(1 for label in rows["labels"] if label > 0.5)
    option_rows = {}
    for option in rows["row_options"]:
        option_rows[option] = option_rows.get(option, 0) + 1
    return {
        "choice_count": len(rows["group_chosen"]),
        "row_count": row_count,
        "positive_row_count": positive_count,
        "negative_row_count": row_count - positive_count,
        "observation_len": rows["observation_len"],
        "upgrade_vocabulary_size": len(rows["vocabulary"]),
        "input_len": rows["input_len"],
        "option_row_distribution": ratio_counts(option_rows, row_count),
    }


def ratio_counts(counts, total):
    return {
        key: {
            "count": int(value),
            "ratio": round(value / max(1, total), 4),
        }
        for key, value in sorted(counts.items())
    }


def build_upgrade_choice_model(input_len, hidden_size, nn_module):
    return nn_module.Sequential(
        nn_module.Linear(input_len, hidden_size),
        nn_module.ReLU(),
        nn_module.Linear(hidden_size, 1),
    )


def row_mask_for_groups(group_ids, selected_groups):
    selected = set(int(group_id) for group_id in selected_groups)
    return [index for index, group_id in enumerate(group_ids) if group_id in selected]


def evaluate_upgrade_choice_model(model, x, y, row_indices, rows, loss_fn, torch_module):
    if not row_indices:
        return {
            "row_count": 0,
            "loss": 0.0,
            "row_accuracy": 0.0,
            "choice_count": 0,
            "choice_accuracy": 0.0,
        }
    model.eval()
    with torch_module.no_grad():
        logits = model(x[row_indices]).reshape(-1)
        labels = y[row_indices]
        loss = loss_fn(logits, labels)
        row_predictions = (logits >= 0.0).float()
        row_accuracy = (row_predictions == labels).float().mean()
        scores_by_group = {}
        for local_index, row_index in enumerate(row_indices):
            group_id = rows["group_ids"][row_index]
            scores_by_group.setdefault(group_id, []).append(
                {
                    "option": rows["row_options"][row_index],
                    "score": float(logits[local_index].item()),
                }
            )
        correct = 0
        for group_id, option_scores in scores_by_group.items():
            predicted = max(option_scores, key=lambda item: item["score"])["option"]
            if predicted == rows["group_chosen"][group_id]:
                correct += 1
        choice_count = len(scores_by_group)
    return {
        "row_count": len(row_indices),
        "loss": round(float(loss.item()), 6),
        "row_accuracy": round(float(row_accuracy.item()), 4),
        "choice_count": choice_count,
        "choice_accuracy": round(correct / max(1, choice_count), 4),
    }


def train_upgrade_choice_model(dataset, args):
    require_dependencies()
    import numpy as np
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, TensorDataset

    if len(dataset["samples"]) < 2:
        raise ValueError("upgrade choice training requires at least two upgrade_sample records")

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    rows = build_upgrade_choice_rows(dataset)
    features = torch.tensor(rows["features"], dtype=torch.float32)
    labels = torch.tensor(rows["labels"], dtype=torch.float32)

    choice_indices = np.arange(len(dataset["samples"]))
    np.random.default_rng(args.seed).shuffle(choice_indices)
    validation_count = int(round(len(choice_indices) * args.validation_split))
    validation_count = min(max(validation_count, 1), max(1, len(choice_indices) - 1))
    validation_groups = choice_indices[:validation_count].tolist()
    train_groups = choice_indices[validation_count:].tolist()
    train_rows = row_mask_for_groups(rows["group_ids"], train_groups)
    validation_rows = row_mask_for_groups(rows["group_ids"], validation_groups)

    train_dataset = TensorDataset(features[train_rows], labels[train_rows])
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)

    positive_count = float(labels[train_rows].sum().item())
    negative_count = float(len(train_rows) - positive_count)
    pos_weight = torch.tensor([negative_count / max(1.0, positive_count)], dtype=torch.float32)

    model = build_upgrade_choice_model(rows["input_len"], args.hidden_size, nn)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    plain_loss_fn = nn.BCEWithLogitsLoss()

    history = []
    for epoch in range(args.epochs):
        model.train()
        losses = []
        for batch_x, batch_y in train_loader:
            logits = model(batch_x).reshape(-1)
            loss = loss_fn(logits, batch_y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            losses.append(float(loss.item()))
        history.append(
            {
                "epoch": epoch + 1,
                "train_loss": round(sum(losses) / max(1, len(losses)), 6),
                "validation": evaluate_upgrade_choice_model(
                    model,
                    features,
                    labels,
                    validation_rows,
                    rows,
                    plain_loss_fn,
                    torch,
                ),
            }
        )

    target = Path(args.model_out)
    target.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "kind": "upgrade_choice_supervised_ranker",
            "model_state_dict": model.state_dict(),
            "upgrade_vocabulary": rows["vocabulary"],
            "observation_len": rows["observation_len"],
            "input_len": rows["input_len"],
            "hidden_size": args.hidden_size,
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "limitations": [
                "This model scores upgrade options from supervised rule Bot samples only.",
                "It is not connected to Gym upgrade action mode and is not an RL test Bot gate.",
            ],
        },
        target,
    )

    return {
        "status": "trained",
        "gate_decision": "upgrade_choice_training_smoke_not_policy_gate",
        "model_path": str(target),
        "dataset": summarize_upgrade_choice_dataset(dataset),
        "rows": summarize_upgrade_choice_rows(rows),
        "training": {
            "seed": args.seed,
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "hidden_size": args.hidden_size,
            "learning_rate": args.learning_rate,
            "validation_split": args.validation_split,
            "train_choice_count": len(train_groups),
            "validation_choice_count": len(validation_groups),
            "positive_weight": round(float(pos_weight.item()), 4),
        },
        "final": history[-1],
        "history": history,
        "limitations": [
            "Upgrade-choice training smoke proves only supervised model plumbing.",
            "The checkpoint must not be promoted until it is connected to Gym upgrade action mode and compared through RL policy acceptance.",
            "Tiny smoke datasets cannot prove upgrade strategy quality or long-run high-pressure repair.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Train a supervised upgrade-choice ranker from Soft Candy Storm upgrade_sample records."
    )
    parser.add_argument(
        "--dataset",
        action="append",
        default=None,
        help="JSONL file or directory with upgrade_sample JSONL records. Repeat to combine datasets.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check-deps", action="store_true")
    parser.add_argument("--limit-samples", type=int, default=None)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--hidden-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--validation-split", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument(
        "--model-out",
        default="python/train/models/upgrade_choice_ranker_smoke.pt",
    )
    parser.add_argument("--report", default=None)
    args = parser.parse_args()

    if args.check_deps:
        write_report(args.report, {"status": "ok", "dependencies": dependency_status()})
        return
    if args.dataset is None:
        parser.error("--dataset is required unless --check-deps is used")
    if args.epochs <= 0:
        parser.error("--epochs must be greater than zero")
    if args.batch_size <= 0:
        parser.error("--batch-size must be greater than zero")
    if args.hidden_size <= 0:
        parser.error("--hidden-size must be greater than zero")
    if not (0.0 < args.validation_split < 1.0):
        parser.error("--validation-split must be between 0 and 1")
    if args.limit_samples is not None and args.limit_samples <= 0:
        parser.error("--limit-samples must be greater than zero")

    try:
        dataset = load_upgrade_choice_dataset(args.dataset, limit=args.limit_samples)
        rows = build_upgrade_choice_rows(dataset)
        if args.dry_run:
            write_report(
                args.report,
                {
                    "status": "ok",
                    "mode": "dry_run",
                    "gate_decision": "upgrade_choice_dataset_validated_not_policy_gate",
                    "dataset": summarize_upgrade_choice_dataset(dataset),
                    "rows": summarize_upgrade_choice_rows(rows),
                    "dependencies": dependency_status(),
                    "limitations": [
                        "Dry-run validates upgrade_sample structure only.",
                        "It does not train a model or prove upgrade policy quality.",
                    ],
                },
            )
            return
        report = train_upgrade_choice_model(dataset, args)
        write_report(args.report, report)
    except (OSError, RuntimeError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
