import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, Tuple


def parse_jsonl(path: Path) -> Iterable[dict]:
    """
    Parse a file that contains multiple JSON objects concatenated together.
    The objects may span multiple lines (pretty-printed), so we use the JSON
    decoder directly instead of splitting on newlines.
    """
    raw = path.read_text(encoding="utf-8")
    decoder = json.JSONDecoder()
    idx = 0
    length = len(raw)

    while idx < length:
        while idx < length and raw[idx].isspace():
            idx += 1
        if idx >= length:
            break
        obj, next_idx = decoder.raw_decode(raw, idx)
        yield obj
        idx = next_idx


def _new_bucket() -> Dict[str, float]:
    return {"count": 0, "final_sum": 0.0, "process_sum": 0.0}


def add_stat(bucket: Dict[str, float], final_score: float, process_score: float) -> None:
    bucket["count"] += 1
    bucket["final_sum"] += final_score
    bucket["process_sum"] += process_score


def update_buckets(record: dict, model_stats: dict) -> None:
    tags = record.get("tags", {})
    scores = record.get("score", {})
    final_score = float(scores.get("final", 0.0))
    process_score = float(scores.get("process", 0.0))

    # Domain buckets (coarse d1 and fine d1/d2)
    domain = tags.get("domain", {})
    d1 = domain.get("d1", "unknown")
    d2 = domain.get("d2")
    add_stat(model_stats["by_domain"][d1], final_score, process_score)
    if d2:
        add_stat(model_stats["by_subdomain"][f"{d1}/{d2}"], final_score, process_score)

    # Level bucket
    level = tags.get("level", "unknown")
    add_stat(model_stats["by_level"][level], final_score, process_score)

    # Difficulty bucket
    difficulty = tags.get("difficulty", "unknown")
    add_stat(model_stats["by_difficulty"][difficulty], final_score, process_score)


def summarize_bucket(title: str, bucket: Dict[str, Dict[str, float]]) -> str:
    lines = [f"{title}:"]
    for key in sorted(bucket, key=lambda x: str(x)):
        stats = bucket[key]
        count = stats["count"]
        if count == 0:
            continue
        final_avg = stats["final_sum"] / count
        process_avg = stats["process_sum"] / count
        lines.append(
            f"  - {key}: n={count}, final_avg={final_avg:.3f}, process_avg={process_avg:.3f}"
        )
    return "\n".join(lines)


def build_stats(records: Iterable[dict]) -> Dict[str, dict]:
    per_model: Dict[str, dict] = {}
    for record in records:
        model = record.get("model_name", "unknown")
        if model not in per_model:
            per_model[model] = {
                "by_domain": defaultdict(_new_bucket),
                "by_subdomain": defaultdict(_new_bucket),
                "by_level": defaultdict(_new_bucket),
                "by_difficulty": defaultdict(_new_bucket),
            }
        update_buckets(record, per_model[model])
    return per_model


def print_report(per_model: Dict[str, dict]) -> None:
    for model in sorted(per_model):
        stats = per_model[model]
        print(f"Model: {model}")
        print(summarize_bucket("Domain (d1)", stats["by_domain"]))
        print(summarize_bucket("Domain (d1/d2)", stats["by_subdomain"]))
        print(summarize_bucket("Level", stats["by_level"]))
        print(summarize_bucket("Difficulty", stats["by_difficulty"]))
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate counts and average scores by tag for an eval JSONL file."
    )
    parser.add_argument("path", type=Path, help="Path to eval.jsonl")
    args = parser.parse_args()

    records = list(parse_jsonl(args.path))
    per_model = build_stats(records)
    print_report(per_model)


if __name__ == "__main__":
    main()
