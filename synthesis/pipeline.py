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

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core import (
    SynthesisConfig,
    SandboxWorker,
    TrajectorySampler,
    TrajectorySelector,
    QASynthesizer,
)


def generate_source_id(seed_content: str, seed_idx: int) -> str:
    """Generate unique source ID for a seed"""
    content_hash = hashlib.md5(seed_content.encode('utf-8')).hexdigest()[:8]
    return f"src_{seed_idx:04d}_{content_hash}"


class SynthesisPipeline:
    """Main RAG synthesis pipeline"""

    def __init__(self, config: SynthesisConfig, output_dir: str = "synthesis_results"):
        """Initialize pipeline"""
        self.config = config
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

        print(f"💾 Output files:")
        print(f"   QA: {self.qa_file_path}")
        print(f"   Trajectories: {self.traj_file_path}")

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
