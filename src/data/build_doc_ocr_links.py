import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Set


def read_ids_from_jsonl(jsonl_path: Path) -> List[str]:
	ids: List[str] = []
	with jsonl_path.open('r', encoding='utf-8') as f:
		for line in f:
			line = line.strip()
			if not line:
				continue
			try:
				obj = json.loads(line)
				item_id = obj.get('id') or obj.get('doc_id')
				if item_id:
					ids.append(str(item_id))
			except json.JSONDecodeError:
				continue
	return ids


def find_ocr_files(search_roots: List[Path]) -> Dict[str, Path]:
	"""
	Return mapping: base_name (without _ocr.json) -> absolute Path
	If duplicates exist across roots, the first found wins.
	"""
	mapping: Dict[str, Path] = {}
	for root in search_roots:
		if not root.exists():
			print(f"Warning: search root not found: {root}")
			continue
		for dirpath, _, filenames in os.walk(root):
			for fn in filenames:
				if not fn.endswith('_ocr.json'):
					continue
				base = fn[:-len('_ocr.json')]
				abs_path = Path(dirpath) / fn
				if base not in mapping:
					mapping[base] = abs_path
	return mapping


def ensure_symlink(src: Path, dst: Path):
	"""Create/update symlink dst -> src safely."""
	dst.parent.mkdir(parents=True, exist_ok=True)
	if dst.exists() or dst.is_symlink():
		try:
			if dst.is_symlink():
				existing = dst.resolve()
				if existing == src.resolve():
					return
				dst.unlink()
			else:
				# Existing regular file; remove and replace
				dst.unlink()
		except Exception as e:
			print(f"Warning: failed removing existing {dst}: {e}")
	try:
		os.symlink(src, dst)
	except FileExistsError:
		pass


def main():
	parser = argparse.ArgumentParser(description="Create symlinks for Doc OCR JSONs based on MMLongBench ids")
	parser.add_argument('--data', required=True, help='Path to AgentFlow JSONL (converted MMLongBench)')
	parser.add_argument('--search-dir', action='append', required=True,
		help='OCR JSON search root (repeatable). Example: "AgentFlow/mnt/shared-storage-user/..."')
	parser.add_argument('--output-dir', default='AgentFlow/src/data/doc_demo/output',
		help='Where to place symlinks as <id_no_ext>_ocr.json')
	args = parser.parse_args()

	data_path = Path(args.data)
	if not data_path.exists():
		print(f"Error: data file not found: {data_path}")
		sys.exit(1)

	ids = read_ids_from_jsonl(data_path)
	if not ids:
		print("Error: no ids found in JSONL")
		sys.exit(1)

	search_roots = [Path(p) for p in args.search_dir]
	ocr_index = find_ocr_files(search_roots)

	output_root = Path(args.output_dir)
	created = 0
	missing: Set[str] = set()

	for item_id in ids:
		base = Path(item_id).stem  # remove extension like .pdf
		src = ocr_index.get(base)
		if not src:
			missing.add(item_id)
			continue
		dst = output_root / f"{base}_ocr.json"
		ensure_symlink(src, dst)
		created += 1

	print(f"Symlinks created/updated: {created}")
	if missing:
		print(f"Missing OCR for {len(missing)} ids:")
		for m in sorted(missing):
			print(f"  - {m}")


if __name__ == '__main__':
	main()
