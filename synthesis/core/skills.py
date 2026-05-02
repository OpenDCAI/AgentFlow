"""
Skill catalog loader and phase-guidance rendering for the synthesis pipeline.

Expected directory layout:
  synthesis/skills/<group>/<skill-id>/SKILL.md
  synthesis/skills/<group>/<skill-id>/references/{EXPLORATION,SELECTION,SYNTHESIS}.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import re

import yaml


PHASE_ENV_EXPLORATION = "environment_exploration"
PHASE_TRAJECTORY_SELECTION = "trajectory_selection"
PHASE_DATA_SYNTHESIS = "data_synthesis"

_PHASE_FILE_MAP: Dict[str, str] = {
    PHASE_ENV_EXPLORATION: "EXPLORATION.md",
    PHASE_TRAJECTORY_SELECTION: "SELECTION.md",
    PHASE_DATA_SYNTHESIS: "SYNTHESIS.md",
}

_PHASE_TITLE_RE = re.compile(r"^\s*#{1,6}\s*Phase\s*\d+\s*:\s*.*$", flags=re.IGNORECASE)
_SYNTHESIS_CUTOFF_KEYS = (
    "expected output format",
    "output format",
)


@dataclass(frozen=True)
class SkillSpec:
    group: str
    skill_id: str
    name: str
    description: str
    definition: str
    skill_path: str
    references: Dict[str, str]
    qa_examples: List[Dict[str, str]] = field(default_factory=list)


def _default_skills_root() -> Path:
    return Path(__file__).resolve().parents[1] / "skills"


def _extract_frontmatter(text: str) -> Dict[str, Any]:
    raw = (text or "").strip()
    if not raw.startswith("---"):
        return {}
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}
    fm = parts[1]
    try:
        data = yaml.safe_load(fm)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _extract_definition(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"^##\s+1\.\s+Capability Definition.*?$([\s\S]*?)(^##\s+|\Z)", text, flags=re.MULTILINE)
    if m:
        body = m.group(1).strip()
        lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
        if lines:
            return " ".join(lines[:2])[:450]

    m = re.search(r"^##\s+Definition\s*$([\s\S]*?)(^##\s+|\Z)", text, flags=re.MULTILINE)
    if m:
        body = m.group(1).strip()
        lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
        if lines:
            return " ".join(lines[:2])[:450]

    for ln in text.splitlines():
        s = ln.strip()
        if not s or s.startswith("#") or s.startswith("---") or s.startswith("name:") or s.startswith("description:"):
            continue
        return s[:260]
    return ""


def _strip_outer_quotes(text: str) -> str:
    s = (text or "").strip()
    if len(s) >= 2 and ((s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'")):
        return s[1:-1].strip()
    return s


def _extract_skill_qa_examples(text: str) -> List[Dict[str, str]]:
    """
    Extract QA demos from SKILL.md.
    Expected common format:
    - * **Real Question**: ...
    - * **Real Answer**: ...
    """
    if not text:
        return []

    q_re = re.compile(r"^\s*[*-]?\s*\**\s*Real Question\s*\**\s*:\s*(.+?)\s*$", flags=re.IGNORECASE)
    a_re = re.compile(r"^\s*[*-]?\s*\**\s*Real Answer\s*\**\s*:\s*(.+?)\s*$", flags=re.IGNORECASE)
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    out: List[Dict[str, str]] = []
    cur_q: Optional[str] = None

    for ln in lines:
        # markdown emphasis markers can appear around keys
        normalized = ln.replace("**", "").replace("__", "")

        mq = q_re.match(normalized)
        if mq:
            cur_q = _strip_outer_quotes(mq.group(1))
            continue

        ma = a_re.match(normalized)
        if ma and cur_q:
            answer = _strip_outer_quotes(ma.group(1))
            if cur_q and answer:
                out.append({"question": cur_q, "answer": answer})
            cur_q = None

    # deduplicate while preserving order
    seen = set()
    deduped: List[Dict[str, str]] = []
    for ex in out:
        key = (ex.get("question", "").strip(), ex.get("answer", "").strip())
        if not key[0] or not key[1] or key in seen:
            continue
        seen.add(key)
        deduped.append({"question": key[0], "answer": key[1]})
    return deduped


def _to_relpath(p: Path) -> str:
    project_root = Path(__file__).resolve().parents[2]
    try:
        return str(p.resolve().relative_to(project_root.resolve()))
    except Exception:
        return str(p)


def _iter_skill_dirs(root: Path) -> List[Tuple[str, Path]]:
    out: List[Tuple[str, Path]] = []
    for group_dir in sorted(root.iterdir()):
        if not group_dir.is_dir():
            continue
        group = group_dir.name
        for d in sorted(group_dir.iterdir()):
            if not d.is_dir():
                continue
            if (d / "SKILL.md").exists():
                out.append((group, d))
    return out


def load_skill_catalog(skills_root: Optional[str] = None, group: Optional[str] = None) -> List[SkillSpec]:
    if skills_root:
        root = Path(skills_root)
        if not root.is_absolute():
            project_root = Path(__file__).resolve().parents[2]
            root = project_root / root
    else:
        root = _default_skills_root()
    if not root.exists():
        return []

    group_filter = (str(group).strip() if group else "")
    skills: List[SkillSpec] = []

    for g, d in _iter_skill_dirs(root):
        if group_filter and g != group_filter:
            continue

        skill_file = d / "SKILL.md"
        raw = skill_file.read_text(encoding="utf-8")
        frontmatter = _extract_frontmatter(raw)

        skill_id = d.name
        name = str(frontmatter.get("name") or skill_id).strip() or skill_id
        description = str(frontmatter.get("description") or "").strip()
        definition = _extract_definition(raw)
        if not description:
            description = definition

        references: Dict[str, str] = {}
        ref_dir = d / "references"
        for phase, filename in _PHASE_FILE_MAP.items():
            ref_file = ref_dir / filename
            if ref_file.exists():
                references[phase] = ref_file.read_text(encoding="utf-8").strip()
            else:
                references[phase] = ""

        skills.append(
            SkillSpec(
                group=g,
                skill_id=skill_id,
                name=name,
                description=description,
                definition=definition,
                skill_path=_to_relpath(skill_file),
                references=references,
                qa_examples=_extract_skill_qa_examples(raw),
            )
        )

    return skills


def build_category_catalog(skills: List[SkillSpec], *, max_desc_chars: int = 220) -> List[Dict[str, str]]:
    grouped: Dict[str, List[SkillSpec]] = {}
    for s in skills:
        grouped.setdefault(s.group, []).append(s)

    catalog: List[Dict[str, str]] = []
    for group, items in sorted(grouped.items(), key=lambda x: x[0]):
        lines = []
        for s in items[:5]:
            desc = (s.description or s.definition or "").strip()
            if max_desc_chars > 0 and len(desc) > max_desc_chars:
                desc = desc[:max_desc_chars].rstrip() + "..."
            lines.append(f"- {s.skill_id}: {desc}")
        catalog.append(
            {
                "group": group,
                "skill_count": str(len(items)),
                "summary": "\n".join(lines) if lines else "(no preview)",
            }
        )
    return catalog


def normalize_selected_group_names(selected: Any, valid_groups: List[str], max_count: int) -> List[str]:
    valid = set(valid_groups)
    if max_count < 1:
        max_count = 1

    if isinstance(selected, str):
        selected = [selected]
    if not isinstance(selected, list):
        return []

    out: List[str] = []
    for item in selected:
        gid = str(item).strip()
        if not gid or gid not in valid or gid in out:
            continue
        out.append(gid)
        if len(out) >= max_count:
            break
    return out


def normalize_selected_skill_ids(selected: Any, valid_skill_ids: List[str], max_count: int) -> List[str]:
    valid = set(valid_skill_ids)
    if max_count < 1:
        max_count = 1

    if isinstance(selected, str):
        selected = [selected]
    if not isinstance(selected, list):
        return []

    out: List[str] = []
    for item in selected:
        sid = str(item).strip()
        if not sid or sid not in valid or sid in out:
            continue
        out.append(sid)
        if len(out) >= max_count:
            break
    return out



def collect_qa_examples_from_skills(
    skills: List[SkillSpec],
    selected_skill_ids: List[str],
    *,
    max_total: int = 10,
    max_per_skill: int = 2,
) -> List[Dict[str, str]]:
    if max_total <= 0 or max_per_skill <= 0:
        return []
    include_set = set([str(x).strip() for x in selected_skill_ids if str(x).strip()])
    if not include_set:
        return []

    out: List[Dict[str, str]] = []
    seen = set()
    for s in skills:
        if s.skill_id not in include_set:
            continue
        taken = 0
        for ex in s.qa_examples:
            q = str(ex.get("question", "")).strip()
            a = str(ex.get("answer", "")).strip()
            if not q or not a:
                continue
            key = (q, a)
            if key in seen:
                continue
            seen.add(key)
            out.append({"question": q, "answer": a})
            taken += 1
            if taken >= max_per_skill or len(out) >= max_total:
                break
        if len(out) >= max_total:
            break
    return out


def assemble_phase_injections(
    skills: List[SkillSpec],
    selected_skill_ids: List[str],
    *,
    max_ref_chars: int = 3000,
) -> Dict[str, str]:
    include_set = set([str(x).strip() for x in selected_skill_ids if str(x).strip()])
    if not include_set:
        return {
            PHASE_ENV_EXPLORATION: "",
            PHASE_TRAJECTORY_SELECTION: "",
            PHASE_DATA_SYNTHESIS: "",
        }

    phase_chunks: Dict[str, List[str]] = {
        PHASE_ENV_EXPLORATION: [],
        PHASE_TRAJECTORY_SELECTION: [],
        PHASE_DATA_SYNTHESIS: [],
    }

    for s in skills:
        if s.skill_id not in include_set:
            continue
        for phase in phase_chunks.keys():
            body = (s.references.get(phase) or "").strip()
            if max_ref_chars > 0 and len(body) > max_ref_chars:
                body = body[:max_ref_chars].rstrip() + "\n...(truncated)"
            cleaned = _postprocess_phase_reference(body, phase)
            if cleaned:
                phase_chunks[phase].append(f"## {s.name}\n{cleaned}".strip())

    return {
        phase: "\n\n".join(chunks).strip()
        for phase, chunks in phase_chunks.items()
    }


def _postprocess_phase_reference(text: str, phase: str) -> str:
    """
    Post-process per-phase skill text for prompt injection.

    Goals:
    - Remove repeated phase top heading from each skill.
    - Keep internal section details from each skill (strategy/criteria/rules/etc.).
    - In synthesis phase, drop `Expected Output Format` and everything after it
      because the base prompt already defines output format.
    """
    if not text:
        return ""

    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: List[str] = []

    for ln in lines:
        normalized = _normalize_title_like_line(ln)

        # Phase-specific cut-off (for synthesis output schema sections).
        if phase == PHASE_DATA_SYNTHESIS and any(normalized.startswith(k) for k in _SYNTHESIS_CUTOFF_KEYS):
            break

        # Drop repeated boilerplate phase titles.
        if _PHASE_TITLE_RE.match(ln or ""):
            continue
        if ln.startswith("  - "):
            ln = "- " + ln[4:]
        out.append(ln)

    # Normalize excessive blank lines.
    normalized: List[str] = []
    prev_blank = False
    for ln in out:
        blank = not ln.strip()
        if blank and prev_blank:
            continue
        normalized.append(ln.rstrip())
        prev_blank = blank

    while normalized and not normalized[0].strip():
        normalized.pop(0)
    while normalized and not normalized[-1].strip():
        normalized.pop()

    return "\n".join(normalized).strip()


def _normalize_title_like_line(line: str) -> str:
    """
    Normalize markdown heading/bullet/title-like lines for robust matching.
    """
    s = str(line or "").strip().lower()
    s = re.sub(r"^\s*#{1,6}\s*", "", s)
    s = re.sub(r"^\s*[*-]\s*", "", s)
    s = s.replace("**", "").replace("__", "")
    s = re.sub(r"\s+", " ", s)
    return s.strip(" :\t")
