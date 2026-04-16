"""
Global skill selection (run once per pipeline).
Two-stage LLM retrieval: (1) pick skill groups, (2) pick skills within selected groups.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from .config import SynthesisConfig
from .skills import (
    PHASE_DATA_SYNTHESIS,
    PHASE_ENV_EXPLORATION,
    PHASE_TRAJECTORY_SELECTION,
    SkillSpec,
    assemble_phase_injections,
    build_category_catalog,
    load_skill_catalog,
    normalize_selected_group_names,
    normalize_selected_skill_ids,
)
from .utils import chat_completion, create_openai_client, extract_json_object


class GlobalSkillSelector:
    """Select global skills once, then produce phase injections."""

    def __init__(self, config: SynthesisConfig):
        self.config = config
        self.settings = config.skill_settings()
        self.client = create_openai_client(api_key=config.api_key, base_url=config.base_url)

    def run_once(self, user_need_text: str) -> Dict[str, Any]:
        skills = load_skill_catalog(self.config.skills_root, group=None)
        if not skills:
            return {
                "enabled": False,
                "reason": "empty_skill_catalog",
                "selected_groups": [],
                "selected_skill_ids": [],
                "injections": {
                    PHASE_ENV_EXPLORATION: "",
                    PHASE_TRAJECTORY_SELECTION: "",
                    PHASE_DATA_SYNTHESIS: "",
                },
                "catalog_size": 0,
            }

        include = self.settings.get("include", [])
        exclude = {str(x).strip() for x in self.settings.get("exclude", []) if str(x).strip()}

        all_ids = [s.skill_id for s in skills if s.skill_id not in exclude]
        if include:
            selected_ids = normalize_selected_skill_ids(
                include,
                all_ids,
                max_count=self.settings["max_global_skills"],
            )
            selected_groups = sorted({s.group for s in skills if s.skill_id in selected_ids})
            injections = assemble_phase_injections(
                skills,
                selected_ids,
                max_ref_chars=self.settings["max_ref_chars"],
            )
            return {
                "enabled": True,
                "selection_mode": "explicit_include",
                "selected_groups": selected_groups,
                "selected_skill_ids": selected_ids,
                "injections": injections,
                "catalog_size": len(skills),
            }

        selected_groups = self._select_groups(user_need_text, skills)
        candidate_skills = [s for s in skills if s.group in set(selected_groups) and s.skill_id not in exclude]
        valid_ids = [s.skill_id for s in candidate_skills]

        selected_ids = self._select_skills(user_need_text, candidate_skills, valid_ids)

        min_k = self.settings["min_global_skills"]
        if len(selected_ids) < min_k:
            for s in candidate_skills:
                if s.skill_id not in selected_ids:
                    selected_ids.append(s.skill_id)
                if len(selected_ids) >= min_k:
                    break

        selected_ids = selected_ids[: self.settings["max_global_skills"]]

        injections = assemble_phase_injections(
            skills,
            selected_ids,
            max_ref_chars=self.settings["max_ref_chars"],
        )

        return {
            "enabled": True,
            "selection_mode": "llm_global",
            "selected_groups": selected_groups,
            "selected_skill_ids": selected_ids,
            "injections": injections,
            "catalog_size": len(skills),
        }

    def _select_groups(self, user_need_text: str, skills: List[SkillSpec]) -> List[str]:
        catalog = build_category_catalog(skills, max_desc_chars=220)
        valid_groups = sorted(list(set([s.group for s in skills])))

        prompt = self._build_group_prompt(user_need_text, catalog)
        try:
            resp = chat_completion(
                self.client,
                model=self.config.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.settings["temperature"],
                response_format={"type": "json_object"},
            )
            obj = json.loads(extract_json_object(resp.choices[0].message.content or "{}"))
            selected = normalize_selected_group_names(
                obj.get("selected_groups", []),
                valid_groups,
                max_count=self.settings["max_category_count"],
            )
            if selected:
                return selected
        except Exception:
            pass

        inferred = self.config.skill_group_name()
        if inferred and inferred in valid_groups:
            return [inferred]

        return valid_groups[: self.settings["max_category_count"]]

    def _select_skills(self, user_need_text: str, candidate_skills: List[SkillSpec], valid_ids: List[str]) -> List[str]:
        if not candidate_skills:
            return []

        prompt = self._build_skill_prompt(user_need_text, candidate_skills)
        try:
            resp = chat_completion(
                self.client,
                model=self.config.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.settings["temperature"],
                response_format={"type": "json_object"},
            )
            obj = json.loads(extract_json_object(resp.choices[0].message.content or "{}"))
            selected = normalize_selected_skill_ids(
                obj.get("selected_skill_ids", []),
                valid_ids,
                max_count=self.settings["max_global_skills"],
            )
            if selected:
                return selected
        except Exception:
            pass

        return valid_ids[: max(1, self.settings["min_global_skills"])]

    def _build_group_prompt(self, user_need_text: str, catalog: List[Dict[str, str]]) -> str:
        rows = []
        for c in catalog:
            rows.append(
                f"group={c['group']} | skill_count={c['skill_count']}\n{c['summary']}"
            )
        catalog_text = "\n\n".join(rows)

        max_categories = self.settings["max_category_count"]
        return f"""You are selecting skill groups for a QA-synthesis pipeline.

[User Need]
{user_need_text}

[Skill Group Catalog]
{catalog_text}

Return strict JSON:
{{
  "selected_groups": ["group_name_1", "group_name_2"],
  "reason": "short reason"
}}

Rules:
- Select at least 1 and at most {max_categories} groups.
- Use exact group names from catalog.
"""

    def _build_skill_prompt(self, user_need_text: str, skills: List[SkillSpec]) -> str:
        max_desc_chars = self.settings["max_desc_chars"]
        rows = []
        for s in skills:
            desc = (s.description or s.definition or "").strip()
            if max_desc_chars > 0 and len(desc) > max_desc_chars:
                desc = desc[:max_desc_chars].rstrip() + "..."
            rows.append(f"- id={s.skill_id} | group={s.group} | name={s.name} | description={desc}")

        min_k = self.settings["min_global_skills"]
        max_k = self.settings["max_global_skills"]

        return f"""You are selecting GLOBAL skills for a 3-phase QA-synthesis pipeline.

[User Need]
{user_need_text}

[Candidate Skills]
{"\n".join(rows)}

Return strict JSON:
{{
  "selected_skill_ids": ["skill_id_1", "skill_id_2"],
  "reason": "short reason"
}}

Rules:
- Select at least {min_k} and at most {max_k} skill IDs.
- Use exact IDs from candidate list.
- Chosen skills should jointly support all three phases: {PHASE_ENV_EXPLORATION}, {PHASE_TRAJECTORY_SELECTION}, {PHASE_DATA_SYNTHESIS}.
"""
