#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BrowseComp-V³ rollout: load decrypted BCV3 JSON, call VLM once per sample (question + images), write per-task JSON for eval_rollout_results.py.
"""
import argparse
import base64
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Load .env from CWD if present
if load_dotenv:
    load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def _safe_name(s: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in str(s))


def _extract_domain_d1(metadata: Any) -> str:
    if not isinstance(metadata, dict):
        return "unknown"
    domain = metadata.get("domain")
    if isinstance(domain, dict):
        return str(domain.get("d1") or "unknown")
    return "unknown"


def _parse_json_field(val: Any) -> Any:
    if val is None:
        return None
    if isinstance(val, str):
        try:
            return json.loads(val)
        except Exception:
            return val
    return val


def _ensure_list(images: Any) -> List[str]:
    if not images:
        return []
    if isinstance(images, list):
        return [str(x) for x in images]
    if isinstance(images, str):
        parsed = _parse_json_field(images)
        if isinstance(parsed, list):
            return [str(x) for x in parsed]
        return [images] if images.strip() else []
    return []


def _load_sample(path: Path) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[WARN] Skip {path}: {e}", file=sys.stderr)
        return None
    if not isinstance(data, dict) or not data.get("question"):
        return None
    # Normalize metadata / sub_goals / images if stored as JSON strings
    if "metadata" in data and isinstance(data["metadata"], str):
        data["metadata"] = _parse_json_field(data["metadata"]) or {}
    if "sub_goals" in data and isinstance(data["sub_goals"], str):
        data["sub_goals"] = _parse_json_field(data["sub_goals"]) or []
    meta = data.get("metadata") or {}
    if "images" not in data and "image_paths" in data:
        data["images"] = _ensure_list(data["image_paths"])
    if "images" not in data:
        data["images"] = _ensure_list(meta.get("images")) or _ensure_list(data.get("image"))
    return data


def _collect_samples(data_dir: str, pattern: str = "*.json") -> List[Dict[str, Any]]:
    data_path = Path(data_dir)
    if not data_path.exists():
        return []
    samples = []
    for p in sorted(data_path.glob(pattern)):
        if not p.is_file():
            continue
        s = _load_sample(p)
        if s:
            samples.append(s)
    return samples


def _build_user_content(question: str, image_paths: List[str], data_root: str) -> List[Dict[str, Any]]:
    content = [{"type": "text", "text": f"Question: {question}\n"}]
    for ref in image_paths:
        ref = ref.strip()
        if ref.startswith("http://") or ref.startswith("https://"):
            content.append({
                "type": "image_url",
                "image_url": {"url": ref, "detail": "high"},
            })
            continue
        # Local path: resolve relative to data_root
        if not os.path.isabs(ref):
            ref = os.path.join(data_root, ref)
        if not os.path.exists(ref):
            continue
        try:
            raw = Path(ref).read_bytes()
            b64 = base64.b64encode(raw).decode("ascii")
            # Guess mime
            ext = (Path(ref).suffix or "").lower()
            mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}", "detail": "high"},
            })
        except Exception as e:
            print(f"[WARN] Skip image {ref}: {e}", file=sys.stderr)
    return content


def _extract_ground_truth(task: Dict[str, Any]) -> Dict[str, Any]:
    meta = task.get("metadata") or {}
    sub_goals = meta.get("sub_goals") or task.get("sub_goals") or []
    if isinstance(sub_goals, str):
        sub_goals = _parse_json_field(sub_goals) or []
    return {
        "final_answer": task.get("answer", ""),
        "sub_goals": sub_goals if isinstance(sub_goals, list) else [],
    }


def _extract_item_tags(task: Dict[str, Any]) -> Dict[str, Any]:
    meta = task.get("metadata") or {}
    return {
        "level": meta.get("level"),
        "difficulty": meta.get("difficulty"),
        "domain": meta.get("domain"),
        "fc_num": meta.get("fc_num"),
    }


def _extract_images(task: Dict[str, Any]) -> List[Any]:
    meta = task.get("metadata") or {}
    images = meta.get("images") or task.get("images") or []
    return _ensure_list(images)


def run_one(
    client: OpenAI,
    model_name: str,
    task: Dict[str, Any],
    data_root: str,
    output_dir: str,
) -> Dict[str, Any]:
    task_id = task.get("id", "unknown")
    question = task.get("question", "")
    image_paths = _extract_images(task)
    user_content = _build_user_content(question, image_paths, data_root)

    start_time = datetime.now(timezone.utc)
    status = "failed"
    final_answer = ""

    try:
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": user_content,
                }
            ],
            max_tokens=2048,
        )
        msg = resp.choices[0].message if resp.choices else None
        final_answer = (msg.content or "").strip()
        status = "success"
    except Exception as e:
        final_answer = ""
        print(f"[WARN] Task {task_id} API error: {e}", file=sys.stderr)

    end_time = datetime.now(timezone.utc)
    domain = _extract_domain_d1(task.get("metadata"))
    safe_model = _safe_name(model_name)
    safe_domain = _safe_name(domain) or "unknown"
    out_base = os.path.join(output_dir, safe_model, safe_domain)
    os.makedirs(out_base, exist_ok=True)
    safe_task_id = _safe_name(task_id)
    file_path = os.path.join(out_base, f"{safe_task_id}.json")

    log_content = {
        "execution": {
            "q_id": task_id,
            "model_name": model_name,
            "timestamp": {
                "start": start_time.isoformat().replace("+00:00", "Z"),
                "end": end_time.isoformat().replace("+00:00", "Z"),
            },
            "status": status,
            "output_file": file_path,
        },
        "item": {
            "question": question,
            "images": _extract_images(task),
            "tags": _extract_item_tags(task),
        },
        "ground_truth": _extract_ground_truth(task),
        "prediction": {
            "final_answer": final_answer,
            "subgoals": [],
        },
        "process": {
            "messages": [],
            "tool_stats": [],
        },
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(log_content, f, ensure_ascii=False, indent=2, default=str)

    return {"task_id": task_id, "status": status, "path": file_path}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="BrowseComp-V³ rollout: one VLM call per sample, write eval-compatible JSONs."
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        required=True,
        help="Directory of decrypted per-sample JSON files (e.g. output of scripts/decrypt_batch.py)",
    )
    parser.add_argument(
        "--data_root",
        type=str,
        default=".",
        help="Root for resolving relative image paths (default: current directory)",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="results",
        help="Output directory; files written as <output_dir>/<model_name>/<domain>/<id>.json",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="gpt-4o",
        help="VLM model name (OpenAI-compatible API)",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.json",
        help="Glob pattern for JSON files in data_dir",
    )
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Only build messages and verify image encoding (no API call); print content structure for first sample.",
    )
    args = parser.parse_args()

    if OpenAI is None and not args.dry_run:
        print("ERROR: openai package required. pip install openai", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_API_BASE")
    if not api_key and not args.dry_run:
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key) if not args.dry_run else None
    data_root = os.path.abspath(args.data_root or ".")
    samples = _collect_samples(args.data_dir, args.pattern)
    if not samples:
        print(f"No samples found under {args.data_dir} with pattern {args.pattern}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        task = samples[0]
        image_paths = _extract_images(task)
        user_content = _build_user_content(task.get("question", ""), image_paths, data_root)
        n_text = sum(1 for c in user_content if c.get("type") == "text")
        n_img = sum(1 for c in user_content if c.get("type") == "image_url")
        print(f"[dry_run] First sample id={task.get('id')}, content blocks: {len(user_content)} (text={n_text}, image_url={n_img})")
        for i, block in enumerate(user_content):
            t = block.get("type", "")
            if t == "text":
                print(f"  [{i}] text: {block.get('text', '')[:80]}...")
            elif t == "image_url":
                url = (block.get("image_url") or {}).get("url", "")
                print(f"  [{i}] image_url: {url[:60]}... (len={len(url)})")
        print("Images are encoded in the message. Exiting without API call.")
        return

    print(f"Running rollout: model={args.model_name}, samples={len(samples)}, output_dir={args.output_dir}")
    ok = 0
    for i, task in enumerate(samples):
        r = run_one(client, args.model_name, task, data_root, args.output_dir)
        if r["status"] == "success":
            ok += 1
        print(f"  [{i+1}/{len(samples)}] {r['task_id']} -> {r['status']}")
    print(f"Done. Success: {ok}/{len(samples)}. Output under {args.output_dir}")


if __name__ == "__main__":
    main()
