#!/usr/bin/env python3
"""
RAG Data Synthesis Pipeline

Clean implementation using the new sandbox.
"""

import json
import os
import sys
import asyncio
import hashlib
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Ensure both the synthesis package directory and project root are importable.
# This allows running via either:
#   - python -m synthesis.pipeline
#   - python synthesis/pipeline.py
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import (
    SynthesisConfig,
    SandboxWorker,
    TrajectorySampler,
    TrajectorySelector,
    QASynthesizer,
)
from core.global_skill_selector import GlobalSkillSelector
from core.skills import (
    PHASE_DATA_SYNTHESIS,
    PHASE_ENV_EXPLORATION,
    PHASE_TRAJECTORY_SELECTION,
    collect_qa_examples_from_skills,
    load_skill_catalog,
)


def generate_source_id(seed_content: str, seed_idx: int) -> str:
    """Generate unique source ID for a seed"""
    content_hash = hashlib.md5(seed_content.encode('utf-8')).hexdigest()[:8]
    return f"src_{seed_idx:04d}_{content_hash}"


def _results_dirname_for_config(config: SynthesisConfig) -> str:
    rts = [str(x).strip() for x in (config.resource_types or []) if str(x).strip()]
    if not rts:
        return "ds_synthesized_qa"
    return "_".join(rts) + "_synthesized_qa"


class SynthesisPipeline:
    """Main RAG synthesis pipeline"""

    def __init__(self, config: SynthesisConfig, output_dir: str = "synthesis_results"):
        """Initialize pipeline"""
        self.config = config
        agg_output_dir = Path(__file__).resolve().parents[1] / "results" / _results_dirname_for_config(config)
        agg_output_dir.mkdir(parents=True, exist_ok=True)
        output_dir = str(agg_output_dir)
        self.output_dir = output_dir

        # Validate config
        errors = config.validate()
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Initialize output files
        self.qa_file_path = os.path.join(output_dir, "synthesized_qa.jsonl")
        self.traj_file_path = os.path.join(output_dir, "trajectories.jsonl")
        self.skills_used_path = os.path.join(output_dir, "skills_used.json")
        self.artifacts_dir = os.path.join(output_dir, "artifacts")
        os.makedirs(self.artifacts_dir, exist_ok=True)

        print(f"💾 Output files:")
        print(f"   QA: {self.qa_file_path}")
        print(f"   Trajectories: {self.traj_file_path}")
        print(f"   Skills used (one-time): {self.skills_used_path}")
        print(f"   Artifacts: {self.artifacts_dir}")

    async def run_async(self, seeds: List[Dict[str, Any]]):
        """Run synthesis pipeline asynchronously"""
        if self.config.number_of_seed is not None:
            seeds = seeds[:self.config.number_of_seed]

        print(f"\n{'='*80}")
        print(f"🚀 RAG Data Synthesis Pipeline")
        print(f"{'='*80}")
        print(f"Total seeds: {len(seeds)}")
        print(f"Model: {self.config.model_name}")
        print(f"{'='*80}\n")

        # Global skill selection runs ONCE for the whole task.
        self._apply_global_skill_selection_once(seeds)

        # Create worker
        worker = SandboxWorker(self.config, worker_id="main_worker")

        try:
            # Start worker
            print("Starting worker...")
            # Defer session creation to per-seed setup to avoid a short-lived initial session.
            success = await worker.start(create_sessions=False)
            if not success:
                print("❌ Failed to start worker")
                return

            # Create components
            sampler = TrajectorySampler(worker, self.config)
            selector = TrajectorySelector(self.config)
            synthesizer = QASynthesizer(self.config)

            # Process each seed
            for seed_idx, seed in enumerate(seeds, 1):
                seed_content = seed.get("content", "")
                seed_kwargs = seed.get("kwargs", {})
                source_id = generate_source_id(seed_content, seed_idx)

                print(f"\n{'#'*60}")
                print(f"Processing Seed {seed_idx}/{len(seeds)}")
                print(f"Source ID: {source_id}")
                print(f"Seed: {seed_content[:100]}...")
                if seed_kwargs:
                    print(f"Kwargs: {seed_kwargs}")
                print(f"{'#'*60}\n")

                try:
                    # Ensure sessions exist; reinitialize per seed for isolation
                    if self.config.resource_types:
                        existing_types = set()
                        try:
                            sessions_resp = await worker.sandbox.list_sessions()
                            if isinstance(sessions_resp, list):
                                sessions_list = sessions_resp
                            else:
                                sessions_list = sessions_resp.get("sessions", [])
                            session_names = [
                                s.get("session_name")
                                for s in sessions_list
                                if isinstance(s, dict) and s.get("session_name")
                            ]
                            print(f"ℹ️ Existing sessions: {session_names or 'None'}")
                            existing_types = {
                                s.get("resource_type")
                                for s in sessions_list
                                if isinstance(s, dict) and s.get("resource_type")
                            }
                        except Exception as e:
                            print(f"⚠️ Failed to list sessions, will recreate: {e}")

                        for resource_type in self.config.resource_types:
                            init_config = self.config.resource_init_configs.get(resource_type, {})
                            res_config = init_config.get("content", {}) if init_config else {}
                            if not isinstance(res_config, dict):
                                res_config = {}
                            res_config = dict(res_config)
                            res_config["custom_name"] = f"{resource_type}_{source_id}"
                            if resource_type in existing_types:
                                await worker.sandbox.reinitialize(resource_type, res_config)
                            else:
                                await worker.sandbox.create_session(resource_type, res_config)

                    # 1. Sample trajectory tree
                    print("📊 Step 1: Sampling trajectory tree...")
                    trajectory_tree = await sampler.sample_trajectory_tree(seed_content, seed_kwargs)

                    if not trajectory_tree or not sampler.root_id:
                        print("⚠️ No trajectories sampled, skipping seed")
                        continue

                    # 2. Select best trajectories
                    print("\n📊 Step 2: Selecting trajectories...")
                    selected_trajectories = selector.select_trajectories(
                        nodes=trajectory_tree,
                        root_id=sampler.root_id,
                        seed_data=seed_content,
                        source_id=source_id,
                        max_selected_traj=self.config.max_selected_traj
                    )

                    if not selected_trajectories:
                        print("⚠️ No trajectories selected, skipping seed")
                        continue

                    # 3. Synthesize QA pairs
                    print("\n📊 Step 3: Synthesizing QA pairs...")
                    qa_pairs = []
                    for qa_idx, trajectory in enumerate(selected_trajectories):
                        try:
                            qa = synthesizer.synthesize_qa(trajectory, qa_idx)
                            if qa:
                                qa_pairs.append(qa.to_dict())
                        except Exception as e:
                            print(f"  ⚠️ QA synthesis failed for trajectory {qa_idx}: {e}")

                    # 4. Save results
                    if qa_pairs:
                        self._save_qa_pairs(qa_pairs)
                        print(f"\n✅ Seed {seed_idx} complete! Generated {len(qa_pairs)} QA pairs")

                    trajectories_data = [traj.to_dict() for traj in selected_trajectories]
                    if trajectories_data:
                        self._save_trajectories(trajectories_data)

                except Exception as e:
                    print(f"\n❌ Error processing seed {seed_idx}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue

        finally:
            # Stop worker
            print("\n🔌 Stopping worker...")
            await worker.stop()

        print(f"\n\n{'='*80}")
        print(f"🎉 Synthesis Complete!")
        print(f"{'='*80}")
        print(f"Total seeds processed: {len(seeds)}")
        print(f"Output directory: {self.output_dir}")
        print(f"{'='*80}\n")

    def run(self, seeds: List[Dict[str, Any]]):
        """Run synthesis pipeline (sync wrapper)"""
        asyncio.run(self.run_async(seeds))

    def _save_qa_pairs(self, qa_pairs: List[Dict[str, Any]]):
        """Save QA pairs to file"""
        with open(self.qa_file_path, "a", encoding="utf-8") as f:
            for qa in qa_pairs:
                f.write(json.dumps(qa, ensure_ascii=False) + "\n")

    def _save_trajectories(self, trajectories: List[Dict[str, Any]]):
        """Save trajectories to file"""
        with open(self.traj_file_path, "a", encoding="utf-8") as f:
            for traj in trajectories:
                f.write(json.dumps(traj, ensure_ascii=False) + "\n")

    def _build_user_need_text(self, seeds: List[Dict[str, Any]]) -> str:
        runtime = self.config.runtime if isinstance(self.config.runtime, dict) else {}
        instr = runtime.get("instruction") if isinstance(runtime.get("instruction"), dict) else {}
        parsed = instr.get("parsed") if isinstance(instr.get("parsed"), dict) else {}
        extracted_complete = bool(instr.get("extracted_complete", False))

        parts: List[str] = []

        # Skill path: if required blocks were not extracted, fallback to the full
        # user-provided markdown text for global skill selection context.
        if not extracted_complete:
            raw_text = str(instr.get("text", "") or "").strip()
            if raw_text:
                return raw_text

        if parsed.get("description"):
            parts.append(f"Description:\n{parsed.get('description')}")
        if parsed.get("sampling_tips"):
            parts.append(f"Sampling Tips:\n{parsed.get('sampling_tips')}")
        if parsed.get("selecting_tips"):
            parts.append(f"Selecting Tips:\n{parsed.get('selecting_tips')}")
        if parsed.get("synthesis_tips"):
            parts.append(f"Synthesis Tips:\n{parsed.get('synthesis_tips')}")
        examples = parsed.get("qa_examples")
        if isinstance(examples, list) and examples:
            ex_lines: List[str] = []
            for i, ex in enumerate(examples, 1):
                q = str(ex.get("question", "")).strip() if isinstance(ex, dict) else ""
                a = str(ex.get("answer", "")).strip() if isinstance(ex, dict) else ""
                if q or a:
                    ex_lines.append(f"{i}. Q: {q}\n   A: {a}")
            if ex_lines:
                parts.append("QA Examples:\n" + "\n".join(ex_lines))

        if not parts and seeds:
            previews = []
            for seed in seeds[:3]:
                previews.append(str(seed.get("content", ""))[:300])
            parts.append("Seed previews:\n" + "\n".join([f"- {x}" for x in previews if x]))

        return "\n\n".join([p for p in parts if p]).strip() or "General QA synthesis task"

    def _apply_global_skill_selection_once(self, seeds: List[Dict[str, Any]]):
        settings = self.config.skill_settings()
        if not bool(settings.get("enabled", False)):
            # skill disabled: preserve original code path.
            self._save_skills_used_once({
                "enabled": False,
                "selection_mode": "disabled",
                "selected_skill_ids": [],
                "selected_groups": [],
                "injections": {
                    PHASE_ENV_EXPLORATION: "",
                    PHASE_TRAJECTORY_SELECTION: "",
                    PHASE_DATA_SYNTHESIS: "",
                },
            })
            return

        user_need_text = self._build_user_need_text(seeds)
        selector = GlobalSkillSelector(self.config)
        result = selector.run_once(user_need_text)

        # Write runtime and inject phase text into original pipeline hooks.
        if not isinstance(self.config.runtime, dict):
            self.config.runtime = {}
        self.config.runtime["skill"] = result

        base_sampling_tips = str(self.config.sampling_tips or "")
        base_selecting_tips = str(self.config.selecting_tips or "")
        base_synthesis_tips = str(self.config.synthesis_tips or "")

        injections = result.get("injections", {}) if isinstance(result, dict) else {}
        self.config.sampling_tips = self._merge_phase_guidance(
            base_sampling_tips,
            str(injections.get(PHASE_ENV_EXPLORATION, "") or ""),
        )
        self.config.selecting_tips = self._merge_phase_guidance(
            base_selecting_tips,
            str(injections.get(PHASE_TRAJECTORY_SELECTION, "") or ""),
        )
        self.config.synthesis_tips = self._merge_phase_guidance(
            base_synthesis_tips,
            str(injections.get(PHASE_DATA_SYNTHESIS, "") or ""),
        )

        # Merge skill-native QA examples (from selected SKILL.md) into synthesizer examples.
        selected_ids = result.get("selected_skill_ids", []) if isinstance(result, dict) else []
        if isinstance(selected_ids, list) and selected_ids:
            catalog = load_skill_catalog(self.config.skills_root, group=None)
            skill_examples = collect_qa_examples_from_skills(
                catalog,
                selected_ids,
                max_total=int(settings.get("max_skill_examples", 8) or 8),
                max_per_skill=2,
            )
            if skill_examples:
                merged = self._merge_qa_examples(
                    self.config.qa_examples,
                    skill_examples,
                    max_total=int(settings.get("max_total_qa_examples", 24) or 24),
                )
                self.config.qa_examples = merged
                result["qa_examples_from_skills"] = skill_examples
                result["qa_examples_total"] = len(merged)

        self._save_skill_catalog_snapshot()
        self._save_skills_used_once(result)

    def _merge_qa_examples(
        self,
        base: List[Dict[str, Any]],
        incoming: List[Dict[str, Any]],
        *,
        max_total: int,
    ) -> List[Dict[str, str]]:
        out: List[Dict[str, str]] = []
        seen = set()

        def _push(items: List[Dict[str, Any]]):
            for it in items:
                q = str(it.get("question", "")).strip()
                a = str(it.get("answer", "")).strip()
                if not q or not a:
                    continue
                key = (q, a)
                if key in seen:
                    continue
                seen.add(key)
                out.append({"question": q, "answer": a})
                if len(out) >= max_total:
                    return

        _push(base if isinstance(base, list) else [])
        if len(out) < max_total:
            _push(incoming if isinstance(incoming, list) else [])
        return out

    def _merge_phase_guidance(self, base_text: str, skill_text: str) -> str:
        b = str(base_text or "").strip()
        s = str(skill_text or "").strip()
        if b and s:
            return f"{b}\n\n{s}"
        return b or s

    def _save_skill_catalog_snapshot(self):
        try:
            catalog = load_skill_catalog(self.config.skills_root, group=None)
            data = [
                {
                    "group": s.group,
                    "skill_id": s.skill_id,
                    "name": s.name,
                    "description": s.description,
                    "skill_path": s.skill_path,
                }
                for s in catalog
            ]
            p = os.path.join(self.artifacts_dir, "skills_catalog.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save skill catalog snapshot: {e}")

    def _save_skills_used_once(self, payload: Dict[str, Any]):
        try:
            with open(self.skills_used_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            with open(os.path.join(self.artifacts_dir, "skills_used.json"), "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save one-time skills_used record: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="RAG Data Synthesis Pipeline")

    parser.add_argument("--config", type=str, required=True,
                       help="Configuration file path (.json or .yaml)")
    parser.add_argument("--seeds", type=str, default=None,
                       help="Seed data JSON file path")
    parser.add_argument("--output-dir", type=str, default=None,
                       help="Output directory")

    args = parser.parse_args()

    # Load configuration
    print(f"Loading configuration: {args.config}")
    if args.config.endswith('.json'):
        config = SynthesisConfig.from_json(args.config)
    elif args.config.endswith('.yaml') or args.config.endswith('.yml'):
        config = SynthesisConfig.from_yaml(args.config)
    else:
        raise ValueError("Configuration file must be .json or .yaml format")

    # Determine seeds file
    seeds_path = args.seeds or config.seeds_file or os.environ.get("SEEDS_FILE")
    if not seeds_path:
        raise ValueError("Missing seeds path: specify via --seeds, config file, or SEEDS_FILE env var")

    # Determine output directory
    output_dir = args.output_dir or config.output_dir or os.environ.get("OUTPUT_DIR") or "synthesis_results"

    print(f"Reading seeds from: {seeds_path}")
    print(f"Output directory: {output_dir}")

    # Load seeds from JSONL format
    seeds = []
    with open(seeds_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                seed = json.loads(line)
                # Ensure seed has required fields
                if isinstance(seed, dict):
                    if "content" not in seed:
                        raise ValueError(f"Seed missing 'content' field: {seed}")
                    if "kwargs" not in seed:
                        seed["kwargs"] = {}
                    seeds.append(seed)
                else:
                    raise ValueError(f"Each seed must be a dict with 'content' and 'kwargs' fields, got: {type(seed)}")

    print(f"Loaded {len(seeds)} seeds")

    # Run pipeline
    pipeline = SynthesisPipeline(config=config, output_dir=output_dir)
    pipeline.run(seeds)

    print("\n✅ All done!")


if __name__ == "__main__":
    main()
