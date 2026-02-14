#!/usr/bin/env python3
import argparse
import json
import shutil
import sys
from pathlib import Path

# Allow running from repo root: python scripts/decrypt_batch.py
_script_dir = Path(__file__).resolve().parent
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))
from encryption_utils import derive_key, decrypt_text


def _collect_image_paths(obj: dict) -> list:
    """Collect all image paths from a train.jsonl record."""
    paths = []
    raw_paths = obj.get("image_paths") or obj.get("image")
    if isinstance(raw_paths, str):
        try:
            parsed = json.loads(raw_paths)
            paths = [parsed] if isinstance(parsed, str) else list(parsed)
        except Exception:
            paths = [raw_paths] if raw_paths.strip() else []
    elif isinstance(raw_paths, list):
        paths = [str(p) for p in raw_paths]
    return [p.strip() for p in paths if p.strip()]


def main():
    parser = argparse.ArgumentParser(description="Batch decrypt BCV3 JSONL")
    parser.add_argument("--input", required=True, help="Path to train.jsonl (or archived bcv3_encrypted.jsonl)")
    parser.add_argument("--key-file", required=True, help="Path to a text file containing passphrase")
    parser.add_argument("--output-dir", required=True, help="Directory to write per-sample JSON")
    parser.add_argument("--keep-encrypted", action="store_true", help="Keep encrypted fields in output")
    parser.add_argument(
        "--copy-images",
        metavar="IMAGES_ROOT",
        default=None,
        help="If set, copy referenced images from IMAGES_ROOT (dir that contains 'images/') to output-dir so that data/images/ resolve. E.g. path/to/hf/data",
    )
    parser.add_argument("--limit", type=int, default=None, help="Decrypt only first N samples (for quick testing)")
    args = parser.parse_args()

    key_str = Path(args.key_file).read_text(encoding="utf-8").strip()
    key = derive_key(key_str)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    total = 0
    all_image_paths = set()
    with Path(args.input).open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            total += 1
            if args.limit is not None and count >= args.limit:
                break
            obj = json.loads(line)
            all_image_paths.update(_collect_image_paths(obj))

            # Detect format: archived bcv3_encrypted.jsonl vs current train.jsonl
            if "encrypted_data" in obj:
                enc = obj.get("encrypted_data", {})
                question = decrypt_text(enc.get("question", {}), key)
                answer = decrypt_text(enc.get("answer", {}), key)
            elif "encrypted_question" in obj:
                enc_q = json.loads(obj.get("encrypted_question", "{}"))
                enc_a = json.loads(obj.get("encrypted_answer", "{}"))
                question = decrypt_text(enc_q, key)
                answer = decrypt_text(enc_a, key)
            else:
                print(f"Warning: Unrecognized format in record {total}, skipping...")
                continue

            out_obj = obj.copy()
            out_obj["question"] = question
            out_obj["answer"] = answer

            if not args.keep_encrypted:
                out_obj.pop("encrypted_data", None)
                out_obj.pop("encrypted_question", None)
                out_obj.pop("encrypted_answer", None)
                out_obj.pop("trajectory", None)

            out_path = out_dir / f"{obj.get('id')}.json"
            out_path.write_text(json.dumps(out_obj, ensure_ascii=False, indent=2), encoding="utf-8")
            count += 1

    if args.copy_images:
        images_root = Path(args.copy_images)
        if not images_root.is_dir():
            print(f"Warning: --copy-images root not a directory: {images_root}", file=sys.stderr)
        else:
            copied = 0
            for rel in sorted(all_image_paths):
                src = images_root / rel
                if not src.is_file():
                    continue
                dst = out_dir / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied += 1
            print(f"Copied {copied} images to {out_dir} (referenced: {len(all_image_paths)})")

    print(f"Decrypted {count}/{total} samples and wrote to {out_dir}")

if __name__ == "__main__":
    main()
