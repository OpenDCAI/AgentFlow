"""
Instruction markdown parsing for the synthesis pipeline.

Two-stage parsing strategy:
1. Regex-based mechanical parsing (zero-cost, deterministic).
2. LLM fallback: triggered only when regex parsing is incomplete, enabling
   free-form / colloquial instruction markdown that doesn't follow the strict
   key-block format.
"""

from __future__ import annotations

import json
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


# ---------------------------------------------------------------------------
# LLM-based fallback parser
# ---------------------------------------------------------------------------

_LLM_SYSTEM_PROMPT = """\
You are a structured-data extractor for a QA-synthesis pipeline.
The user will provide an instruction document written in free-form natural language.
Extract the following fields and return them as a single JSON object with these exact keys:

- "description": (string) overall task description / purpose of this synthesis task.
- "seed_description": (string) alternative description focused on seed/input documents; \
leave empty string if not present.
- "sampling_tips": (string) guidance for the environment-exploration / sampling phase \
(how the agent should browse and collect evidence).
- "selecting_tips": (string) guidance for the trajectory-selection phase \
(how to filter and rank collected trajectories).
- "synthesis_tips": (string) guidance for the QA-synthesis phase \
(how to compose high-quality question-answer pairs).
- "qa_examples": (array of objects) example QA pairs found in the document, \
each object has exactly two keys "question" and "answer".

Rules:
- Every string value must be a non-empty string if the corresponding information is present \
in the document; otherwise use an empty string "".
- qa_examples must be a JSON array; use [] if no examples are found.
- Do NOT add any extra keys.
- Return strict JSON only, no markdown fences, no commentary.
"""

_LLM_USER_TEMPLATE = """\
Below is the instruction document. Extract the structured fields from it.

<instruction_document>
{text}
</instruction_document>
"""


def llm_parse_qa_syn_instruction_md(
    text: str,
    client: Any,
    model_name: str,
    temperature: float = 0.0,
) -> Dict[str, Any]:
    """Use an LLM to extract structured fields from a free-form instruction markdown.

    Returns a dict with the same keys as :func:`parse_qa_syn_instruction_md`.
    Returns an empty dict on any failure so callers can treat it as a no-op.

    Args:
        text: Raw instruction markdown text.
        client: An ``openai.OpenAI`` compatible client instance.
        model_name: Model identifier to use for the completion.
        temperature: Sampling temperature (default 0 for deterministic output).
    """
    from .utils import chat_completion, extract_json_object

    user_msg = _LLM_USER_TEMPLATE.format(text=(text or "").strip())

    try:
        # Try with response_format first; fall back without it if the provider
        # returns a 400 (some models / providers don't support json_object mode).
        kwargs = dict(
            model=model_name,
            messages=[
                {"role": "system", "content": _LLM_SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=temperature,
            max_retries=2,
        )
        try:
            response = chat_completion(client, response_format={"type": "json_object"}, **kwargs)
        except Exception:
            # Retry without response_format constraint
            response = chat_completion(client, **kwargs)
        raw = response.choices[0].message.content or ""
    except Exception as exc:
        print(f"⚠️ LLM instruction parsing failed ({type(exc).__name__}: {exc})")
        return {}

    # Best-effort JSON extraction
    try:
        json_str = extract_json_object(raw)
        data = json.loads(json_str)
    except Exception:
        print("⚠️ LLM instruction parsing: could not decode JSON from response.")
        return {}

    if not isinstance(data, dict):
        return {}

    # Normalise qa_examples: accept list-of-dicts or JSON string
    qa_raw = data.get("qa_examples", [])
    if isinstance(qa_raw, str):
        try:
            qa_raw = json.loads(qa_raw)
        except Exception:
            qa_raw = []
    if isinstance(qa_raw, list):
        qa_clean: List[Dict[str, str]] = []
        for item in qa_raw:
            if isinstance(item, dict):
                q = str(item.get("question") or "").strip()
                a = str(item.get("answer") or "").strip()
                if q and a:
                    qa_clean.append({"question": q, "answer": a})
        data["qa_examples"] = qa_clean
    else:
        data["qa_examples"] = []

    # Normalise all text fields to str
    for key in ("description", "seed_description", "sampling_tips", "selecting_tips", "synthesis_tips"):
        if key in data:
            data[key] = str(data[key] or "").strip()

    return data


def _merge_parsed(
    regex_parsed: Dict[str, Any],
    llm_parsed: Dict[str, Any],
) -> Dict[str, Any]:
    """Merge LLM-extracted fields into the regex-parsed dict.

    Merge strategy: regex-parsed values take priority; LLM fills in missing or
    empty fields only.

    Args:
        regex_parsed: Result from :func:`parse_qa_syn_instruction_md`.
        llm_parsed: Result from :func:`llm_parse_qa_syn_instruction_md`.

    Returns:
        A new dict with gaps filled by LLM results.
    """
    merged = dict(regex_parsed)

    for key in ("description", "seed_description", "sampling_tips", "selecting_tips", "synthesis_tips"):
        existing = merged.get(key)
        if not (existing and str(existing).strip()):
            llm_val = llm_parsed.get(key)
            if llm_val and str(llm_val).strip():
                merged[key] = str(llm_val).strip()

    # qa_examples: only fill when regex found none
    existing_qa = merged.get("qa_examples")
    if not (isinstance(existing_qa, list) and existing_qa):
        llm_qa = llm_parsed.get("qa_examples")
        if isinstance(llm_qa, list) and llm_qa:
            merged["qa_examples"] = llm_qa

    return merged
