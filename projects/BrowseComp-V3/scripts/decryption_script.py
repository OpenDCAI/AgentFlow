#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

# Allow running from repo root: python scripts/decryption_script.py
_script_dir = Path(__file__).resolve().parent
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))
from encryption_utils import derive_key, decrypt_text


def main():
    parser = argparse.ArgumentParser(description="Decrypt BCV3 encrypted JSONL")
    parser.add_argument("--input", required=True, help="Path to train.jsonl (or archived bcv3_encrypted.jsonl)")
    parser.add_argument("--key", required=True, help="Passphrase string")
    parser.add_argument("--output", required=True, help="Output JSON file")
    parser.add_argument("--keep-encrypted", action="store_true", help="Keep encrypted fields in output")
    args = parser.parse_args()

    key = derive_key(args.key)
    in_path = Path(args.input)
    out_path = Path(args.output)

    outputs = []
    total = 0
    with in_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            total += 1
            obj = json.loads(line)
            out_obj = obj.copy()

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

            out_obj["question"] = question
            out_obj["answer"] = answer

            if not args.keep_encrypted:
                out_obj.pop("encrypted_data", None)
                out_obj.pop("encrypted_question", None)
                out_obj.pop("encrypted_answer", None)
                out_obj.pop("trajectory", None)

            outputs.append(out_obj)

    out_path.write_text(json.dumps(outputs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Decrypted {len(outputs)}/{total} records and wrote to {out_path}")

if __name__ == "__main__":
    main()
