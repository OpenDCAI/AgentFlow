"""
Instruction markdown parsing for the synthesis pipeline.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


_KNOWN_KEYS = {
    "description",
    "seed_description",
    "sampling_tips",
    "selecting_tips",
    "synthesis_tips",
    "qa_examples",
}


def parse_qa_syn_instruction_md(text: str) -> Dict[str, Any]:
    """Parse key-block markdown into a structured dict."""
    raw = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = raw.split("\n")

    blocks: Dict[str, List[str]] = {}
    current_key: Optional[str] = None
    current: List[str] = []

    def _flush():
        nonlocal current_key, current
        if current_key is None:
            current = []
            return
        while current and not current[0].strip():
            current.pop(0)
        while current and not current[-1].strip():
            current.pop()
        blocks[current_key] = list(current)
        current = []

    key_line_re = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")
    for ln in lines:
        m = key_line_re.match(ln)
        if m and m.group(1) in _KNOWN_KEYS and (not ln.startswith("    ")):
            _flush()
            current_key = m.group(1)
            trailing = m.group(2)
            current = []
            if trailing.strip():
                current.append(trailing)
            continue
        if current_key is None:
            continue
        current.append(ln)
    _flush()

    out: Dict[str, Any] = {}
    for k in ("description", "seed_description", "sampling_tips", "selecting_tips", "synthesis_tips"):
        if k in blocks:
            out[k] = _normalize_block_text(blocks[k])

    if "qa_examples" in blocks:
        ex = _parse_qa_examples(blocks["qa_examples"])
        if ex:
            out["qa_examples"] = ex

    return out


def _normalize_block_text(lines: List[str]) -> str:
    if not lines:
        return ""
    non_empty = [ln for ln in lines if ln.strip()]
    if not non_empty:
        return ""
    indents = []
    for ln in non_empty:
        m = re.match(r"^(\s+)", ln)
        indents.append(len(m.group(1)) if m else 0)
    trim = min(indents) if indents else 0
    norm = [ln[trim:] if len(ln) >= trim else ln for ln in lines]
    return "\n".join(norm).strip()


def _parse_qa_examples(lines: List[str]) -> List[Dict[str, str]]:
    text = _normalize_block_text(lines)
    if not text:
        return []

    examples: List[Dict[str, str]] = []

    q_matches = list(re.finditer(r'"question"\s*:\s*"([^"]+)"', text))
    a_matches = list(re.finditer(r'"answer"\s*:\s*"([^"]+)"', text))
    if q_matches and a_matches and len(q_matches) == len(a_matches):
        for q, a in zip(q_matches, a_matches):
            examples.append({"question": q.group(1).strip(), "answer": a.group(1).strip()})
        return [e for e in examples if e["question"] and e["answer"]]

    cur: Dict[str, str] = {}
    for ln in text.split("\n"):
        m = re.match(r"^\s*-\s*question\s*:\s*(.*)$", ln, flags=re.IGNORECASE)
        if m:
            if cur.get("question") and cur.get("answer"):
                examples.append({"question": cur["question"], "answer": cur["answer"]})
            cur = {"question": m.group(1).strip(), "answer": ""}
            continue
        m = re.match(r"^\s*answer\s*:\s*(.*)$", ln, flags=re.IGNORECASE)
        if m and cur:
            cur["answer"] = m.group(1).strip()
            continue
    if cur.get("question") and cur.get("answer"):
        examples.append({"question": cur["question"], "answer": cur["answer"]})

    return [e for e in examples if e["question"] and e["answer"]]
