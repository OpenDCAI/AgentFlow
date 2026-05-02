"""
Trajectory selector: LLM-based ranking when skill is enabled, rule-based fallback otherwise.
"""

import json
from typing import Any, Dict, List, Optional, Tuple

from .config import SynthesisConfig
from .models import Trajectory, TrajectoryNode
from .skills import PHASE_TRAJECTORY_SELECTION
from .utils import chat_completion, create_openai_client, extract_json_object


class TrajectorySelector:
    """Select high-quality trajectories from exploration tree."""

    def __init__(self, config: SynthesisConfig):
        self.config = config
        self.available_tool_total: int = 0
        self.client = create_openai_client(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
        )

        self.skill_settings = self.config.skill_settings()
        runtime_skill = self.config.runtime.get("skill", {})
        selected_ids = runtime_skill.get("selected_skill_ids", [])
        self.global_selected_skill_ids = [str(x).strip() for x in selected_ids if str(x).strip()]
        self.skill_enabled = bool(self.skill_settings.get("enabled", False)) and bool(self.global_selected_skill_ids)
        self.last_selection_record: Dict[str, Any] = {}

    def select_trajectories(
        self,
        nodes: Dict[str, TrajectoryNode],
        root_id: str,
        seed_data: str,
        source_id: str,
        max_selected_traj: int = None,
    ) -> List[Trajectory]:
        """Select high-quality trajectories from tree."""
        if max_selected_traj is None:
            max_selected_traj = self.config.max_selected_traj

        print(f"\n{'='*60}")
        print(f"Selecting Trajectories (max: {max_selected_traj})")
        print(f"{'='*60}\n")

        leaf_nodes = [node for node in nodes.values() if not node.children_ids]
        print(f"Found {len(leaf_nodes)} leaf nodes")

        valid_leaves = [node for node in leaf_nodes if node.depth >= self.config.min_depth]
        print(f"Valid leaves (depth >= {self.config.min_depth}): {len(valid_leaves)}")
        if not valid_leaves:
            print("⚠️  No trajectories meet depth requirement")
            return []

        candidate_paths: List[List[TrajectoryNode]] = []
        for leaf in valid_leaves:
            path = self._build_path_to_root(leaf, nodes, root_id)
            if path:
                candidate_paths.append(path)

        print(f"Built {len(candidate_paths)} candidate paths")

        if self.skill_enabled:
            llm_selected = self._select_with_llm(candidate_paths, seed_data, source_id, max_selected_traj)
            if llm_selected:
                print(f"\n✅ Selected {len(llm_selected)} trajectories (LLM+global-skills)")
                return llm_selected
            print("⚠️ LLM-based selection failed, fallback to rule-based scoring")

        selected = self._score_and_select(candidate_paths, seed_data, source_id, max_selected_traj)
        print(f"\n✅ Selected {len(selected)} trajectories (rule fallback)")
        return selected

    def _select_with_llm(
        self,
        paths: List[List[TrajectoryNode]],
        seed_data: str,
        source_id: str,
        max_selected: int,
    ) -> List[Trajectory]:
        candidates = self._build_candidate_payload(paths)
        prompt = self._build_llm_selection_prompt(seed_data, candidates, max_selected)

        try:
            resp = chat_completion(
                self.client,
                model=self.config.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            content = resp.choices[0].message.content or "{}"
            obj = json.loads(extract_json_object(content))
        except Exception as e:
            self.last_selection_record = {
                "phase": PHASE_TRAJECTORY_SELECTION,
                "status": "llm_error",
                "error": str(e),
                "skill_ids": self.global_selected_skill_ids,
            }
            return []

        raw_ids = obj.get("selected_trajectory_ids", [])
        if not isinstance(raw_ids, list):
            self.last_selection_record = {
                "phase": PHASE_TRAJECTORY_SELECTION,
                "status": "invalid_output",
                "skill_ids": self.global_selected_skill_ids,
            }
            return []

        id_to_path = {f"cand_{idx}": path for idx, path in enumerate(paths)}
        picked_paths: List[Tuple[str, List[TrajectoryNode]]] = []
        for rid in raw_ids:
            cid = str(rid).strip()
            if cid in id_to_path and all(cid != prev for prev, _ in picked_paths):
                picked_paths.append((cid, id_to_path[cid]))
            if len(picked_paths) >= max_selected:
                break

        if not picked_paths:
            self.last_selection_record = {
                "phase": PHASE_TRAJECTORY_SELECTION,
                "status": "empty_selection",
                "skill_ids": self.global_selected_skill_ids,
            }
            return []

        out: List[Trajectory] = []
        for rank, (cid, path) in enumerate(picked_paths):
            traj = Trajectory(
                trajectory_id=f"{source_id}_traj_{rank}",
                nodes=path,
                seed_data=seed_data,
                source_id=source_id,
                total_depth=len(path),
                metadata={
                    "selection_method": "llm_global_skill",
                    "selection_skill_ids": list(self.global_selected_skill_ids),
                    "candidate_id": cid,
                },
            )
            out.append(traj)

        self.last_selection_record = {
            "phase": PHASE_TRAJECTORY_SELECTION,
            "status": "ok",
            "skill_ids": self.global_selected_skill_ids,
            "selected_trajectory_ids": [cid for cid, _ in picked_paths],
        }
        return out

    def _build_candidate_payload(self, paths: List[List[TrajectoryNode]]) -> List[Dict[str, Any]]:
        payload: List[Dict[str, Any]] = []
        for idx, path in enumerate(paths):
            tools = []
            for node in path:
                if node.action:
                    tools.append(str(node.action.get("tool_name", "")))
            payload.append(
                {
                    "id": f"cand_{idx}",
                    "depth": len(path),
                    "tool_set": sorted(list(set([t for t in tools if t]))),
                    "preview": self._path_preview(path),
                }
            )
        return payload

    def _path_preview(self, path: List[TrajectoryNode], max_steps: int = 4, obs_chars: int = 200) -> str:
        lines: List[str] = []
        for i, node in enumerate(path[:max_steps], 1):
            lines.append(f"Step {i}: intent={node.intent}")
            if node.action:
                lines.append(f"  tool={node.action.get('tool_name', '')}")
            obs = str(node.observation or "")
            if len(obs) > obs_chars:
                obs = obs[:obs_chars].rstrip() + "..."
            lines.append(f"  obs={obs}")
        return "\n".join(lines)

    def _build_llm_selection_prompt(
        self,
        seed_data: str,
        candidates: List[Dict[str, Any]],
        max_selected: int,
    ) -> str:
        return f"""You are selecting the best exploration trajectories for downstream QA synthesis.

[Seed Data]
{seed_data}

[Trajectory Selection Goals]
- Prefer trajectories with high evidence quality, non-trivial reasoning dependency, and minimal shortcuts.
- Prefer trajectories that better satisfy the selection guidance.
- Avoid selecting highly redundant trajectories.
{f"- Additional selecting guidance: {self.config.selecting_tips}" if self.config.selecting_tips else ""}

[Candidate Trajectories]
{json.dumps(candidates, ensure_ascii=False, indent=2)}

Return strict JSON:
{{
  "selected_trajectory_ids": ["cand_0", "cand_3"],
  "reason": "short explanation"
}}

Rules:
- Select at most {max_selected} trajectory IDs.
- selected_trajectory_ids must be from candidate IDs exactly.
"""

    def _build_path_to_root(
        self,
        leaf: TrajectoryNode,
        nodes: Dict[str, TrajectoryNode],
        root_id: str,
    ) -> List[TrajectoryNode]:
        """Build path from leaf to root"""
        path = []
        current = leaf

        while current.node_id != root_id:
            path.append(current)
            if current.parent_id is None:
                break
            current = nodes[current.parent_id]

        path.reverse()
        return path

    def _score_and_select(
        self,
        paths: List[List[TrajectoryNode]],
        seed_data: str,
        source_id: str,
        max_selected: int,
    ) -> List[Trajectory]:
        """Score and select best paths, avoiding highly similar paths"""
        all_avg_lengths = []
        for path in paths:
            avg_length = sum(len(node.observation) for node in path) / len(path) if path else 0
            all_avg_lengths.append(avg_length)

        min_length = min(all_avg_lengths) if all_avg_lengths else 0
        max_length = max(all_avg_lengths) if all_avg_lengths else 1
        length_range = max_length - min_length if max_length > min_length else 1

        scored_paths = []
        for idx, path in enumerate(paths):
            score = self._score_path(path, all_avg_lengths[idx], min_length, length_range)
            scored_paths.append((score, idx, path))

        scored_paths.sort(reverse=True, key=lambda x: x[0])

        selected_trajectories = []
        selected_path_sets = []

        similarity_threshold = getattr(self.config, 'path_similarity_threshold', 0.7)

        for score, idx, path in scored_paths:
            if len(selected_trajectories) >= max_selected:
                break

            current_path_set = {node.node_id for node in path}
            is_too_similar = False

            for selected_set in selected_path_sets:
                intersection = len(current_path_set & selected_set)
                union = len(current_path_set | selected_set)
                jaccard_similarity = intersection / union if union > 0 else 0.0

                if jaccard_similarity > similarity_threshold:
                    is_too_similar = True
                    print(f"  ⚠️  Trajectory {idx} too similar ({jaccard_similarity:.2f} > {similarity_threshold:.2f}), skipping")
                    break

            if not is_too_similar:
                trajectory = Trajectory(
                    trajectory_id=f"{source_id}_traj_{idx}",
                    nodes=path,
                    seed_data=seed_data,
                    source_id=source_id,
                    total_depth=len(path),
                    metadata={"selection_method": "rule_fallback"},
                )
                selected_trajectories.append(trajectory)
                selected_path_sets.append(current_path_set)
                print(f"  Selected Trajectory {len(selected_trajectories)}: ID={trajectory.trajectory_id}, depth={len(path)}, score={score:.2f}")

        self.last_selection_record = {
            "phase": PHASE_TRAJECTORY_SELECTION,
            "status": "fallback",
            "skill_ids": self.global_selected_skill_ids,
        }
        return selected_trajectories

    def _score_path(
        self,
        path: List[TrajectoryNode],
        avg_obs_length: Optional[float] = None,
        min_length: float = 0,
        length_range: float = 1,
    ) -> float:
        """Score a path"""
        depth_score = min(len(path) / 5.0, 1.0) * 40

        if avg_obs_length is None:
            avg_obs_length = sum(len(node.observation) for node in path) / len(path) if path else 0
        normalized_length = (avg_obs_length - min_length) / length_range if length_range > 0 else 0
        info_score = normalized_length * 30

        tool_names = set()
        for node in path:
            if node.action:
                tool_names.add(node.action.get("tool_name", ""))
        total_tools = len(self.config.available_tools) if self.config.available_tools else self.available_tool_total
        diversity_score = len(tool_names) / max(total_tools, 1) * 30

        return depth_score + info_score + diversity_score
