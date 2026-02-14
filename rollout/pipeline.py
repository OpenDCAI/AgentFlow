#!/usr/bin/env python3
"""
Rollout Pipeline - Main execution pipeline for running agents on benchmarks

This module provides the main RolloutPipeline class that handles:
1. Loading benchmark data
2. Setting up agent runner with sandbox
3. Running agent on tasks (sequential or parallel)
4. Evaluating results
5. Saving outputs
"""

import json
import os
import sys
import asyncio
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import time
from datetime import datetime
import concurrent.futures

from .core import (
    RolloutConfig,
    BenchmarkItem,
    TaskResult,
    RolloutSummary,
    Evaluator,
    load_benchmark_data,
    get_timestamp
)
from .core.runner import AgentRunner


class RolloutPipeline:
    """
    Main Rollout Pipeline for benchmark execution.
    
    Usage:
        config = RolloutConfig.from_json("config.json")
        pipeline = RolloutPipeline(config)
        summary = pipeline.run()
    """

    def __init__(self, config: RolloutConfig, output_dir: Optional[str] = None):
        """
        Initialize pipeline.
        
        Args:
            config: Rollout configuration
            output_dir: Override output directory
        """
        self.config = config
        self.output_dir = output_dir or config.output_dir or "rollout_results"

        if self.config.trajectory_only:
            # Trajectory-only mode is for inference logging, so disable evaluation
            # and guarantee trajectory persistence in results output.
            self.config.evaluate_results = False
            self.config.save_results = True
            self.config.save_trajectories = True
        
        # Validate config
        errors = config.validate()
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize output files
        timestamp = get_timestamp()
        benchmark_name = config.benchmark_name or "benchmark"
        
        self.results_file = os.path.join(self.output_dir, f"results_{benchmark_name}_{timestamp}.jsonl")
        self.eval_file = os.path.join(self.output_dir, f"evaluation_{benchmark_name}_{timestamp}.json")
        self.summary_file = os.path.join(self.output_dir, f"summary_{benchmark_name}_{timestamp}.json")
        
        print(f"💾 Output files:")
        print(f"   Results: {self.results_file}")
        if self.config.evaluate_results:
            print(f"   Evaluation: {self.eval_file}")
        if self.config.save_summary:
            print(f"   Summary: {self.summary_file}")
        
        # Results storage
        self.results: List[TaskResult] = []
        self.benchmark_items: List[BenchmarkItem] = []

    def load_benchmark(self) -> List[BenchmarkItem]:
        """Load benchmark data"""
        if not self.config.data_path:
            raise ValueError("data_path not specified in config")
        
        print(f"\n📂 Loading benchmark from: {self.config.data_path}")
        
        raw_data = load_benchmark_data(self.config.data_path)
        
        # Convert to BenchmarkItem
        items = [BenchmarkItem.from_dict(item) for item in raw_data]
        
        # Filter by task_ids if specified
        if self.config.task_ids:
            task_id_set = set(self.config.task_ids)
            items = [item for item in items if item.id in task_id_set]
            print(f"   Filtered to {len(items)} specific tasks")
        
        # Limit number of tasks if specified
        if self.config.number_of_tasks is not None:
            items = items[:self.config.number_of_tasks]
            print(f"   Limited to first {len(items)} tasks")
        
        print(f"   Loaded {len(items)} tasks")
        self.benchmark_items = items
        return items

    async def run_async(self) -> RolloutSummary:
        """Run pipeline asynchronously"""
        start_time = time.time()
        
        # Load benchmark
        if not self.benchmark_items:
            self.load_benchmark()
        
        print(f"\n{'='*80}")
        print(f"🚀 Rollout Pipeline")
        print(f"{'='*80}")
        print(f"Total tasks: {len(self.benchmark_items)}")
        print(f"Model: {self.config.model_name}")
        print(f"Max turns: {self.config.max_turns}")
        print(f"Parallel: {self.config.parallel}")
        print(f"{'='*80}\n")
        
        # Create runner
        runner = AgentRunner(self.config, worker_id="main_runner")
        
        try:
            # Start runner
            print("Starting runner...")
            success = await runner.start()
            if not success:
                raise RuntimeError("Failed to start runner")
            
            # Run tasks
            if self.config.parallel and self.config.max_workers > 1:
                await self._run_parallel(runner)
            else:
                await self._run_sequential(runner)
            
        finally:
            # Stop runner
            print("\n🔌 Stopping runner...")
            await runner.stop()
        
        # Evaluate results
        evaluation = None
        if self.config.evaluate_results and self.results:
            print("\n📊 Evaluating results...")
            evaluator_model_name = self.config.evaluator_model_name or self.config.model_name
            evaluator_api_key = self.config.evaluator_api_key or self.config.api_key
            evaluator_base_url = self.config.evaluator_base_url or self.config.base_url
            evaluator = Evaluator(
                metric=self.config.evaluation_metric,
                model_name=evaluator_model_name,
                api_key=evaluator_api_key,
                base_url=evaluator_base_url,
                temperature=self.config.evaluator_temperature,
                max_retries=self.config.evaluator_max_retries,
                extra_params=self.config.evaluator_extra_params,
            )
            evaluation = evaluator.evaluate(self.results)
            
            # Save evaluation
            with open(self.eval_file, 'w', encoding='utf-8') as f:
                json.dump(evaluation, f, indent=2, ensure_ascii=False)
            print(f"   Evaluation saved to: {self.eval_file}")
        
        # Calculate summary
        total_time = time.time() - start_time
        successful = sum(1 for r in self.results if r.success)
        avg_score = evaluation.get("average_score", 0.0) if evaluation else 0.0
        
        summary = RolloutSummary(
            benchmark_name=self.config.benchmark_name or "benchmark",
            total_tasks=len(self.results),
            successful_tasks=successful,
            failed_tasks=len(self.results) - successful,
            average_score=avg_score,
            metric=self.config.evaluation_metric,
            total_time_seconds=total_time,
            results_file=self.results_file,
            evaluation_file=self.eval_file if self.config.evaluate_results else None
        )
        
        # Save summary (optional)
        if self.config.save_summary:
            with open(self.summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Print summary
        print(f"\n\n{'='*80}")
        print(f"🎉 Rollout Complete!")
        print(f"{'='*80}")
        print(f"Total tasks: {summary.total_tasks}")
        print(f"Successful: {summary.successful_tasks}")
        print(f"Failed: {summary.failed_tasks}")
        print(f"Average score: {summary.average_score:.3f}")
        print(f"Total time: {summary.total_time_seconds:.1f}s")
        print(f"Results: {self.results_file}")
        print(f"{'='*80}\n")
        
        return summary

    async def _run_sequential(self, runner: AgentRunner) -> None:
        """Run tasks sequentially"""
        for idx, item in enumerate(self.benchmark_items, 1):
            print(f"\n[{idx}/{len(self.benchmark_items)}]", end=" ")
            
            result = await runner.run_task(item)
            self.results.append(result)
            
            # Save result immediately
            if self.config.save_results:
                self._save_result(result)

    async def _run_parallel(self, runner: AgentRunner) -> None:
        """Run tasks in parallel using thread pool"""
        # Note: For true parallelism, we'd need multiple runner instances
        # This implementation uses sequential execution with async for simplicity
        # True parallel would require multiple sandbox sessions
        
        print(f"⚠️ Parallel mode with max_workers={self.config.max_workers}")
        print("   Note: Using sequential execution (parallel requires multiple sandbox sessions)")
        
        await self._run_sequential(runner)

    def _save_result(self, result: TaskResult) -> None:
        """Save single result to file"""
        if self.config.trajectory_only:
            payload: Dict[str, Any] = {
                "task_id": result.task_id,
                "success": result.success,
                "trajectory": result.trajectory.to_dict() if result.trajectory else None
            }
            if result.error:
                payload["error"] = result.error
        else:
            payload = result.to_dict()
        with open(self.results_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def run(self) -> RolloutSummary:
        """Run pipeline (sync wrapper)"""
        return asyncio.run(self.run_async())


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Rollout Pipeline - Run agents on benchmarks")
    
    parser.add_argument("--config", type=str, required=True,
                       help="Configuration file path (.json or .yaml)")
    parser.add_argument("--data", type=str, default=None,
                       help="Benchmark data file path (overrides config)")
    parser.add_argument("--output-dir", type=str, default=None,
                       help="Output directory (overrides config)")
    parser.add_argument("--model", type=str, default=None,
                       help="Model name (overrides config)")
    parser.add_argument("--max-tasks", type=int, default=None,
                       help="Maximum number of tasks to run")
    parser.add_argument("--task-ids", type=str, nargs="+", default=None,
                       help="Specific task IDs to run")
    parser.add_argument("--no-eval", action="store_true",
                       help="Skip evaluation")
    parser.add_argument("--parallel", action="store_true",
                       help="Run tasks in parallel")
    parser.add_argument("--max-workers", type=int, default=None,
                       help="Maximum parallel workers")
    parser.add_argument("--metric", type=str, default=None,
                       choices=["exact_match", "f1_score", "contains_answer", "numeric_match", "llm_judgement"],
                       help="Evaluation metric (overrides config)")
    
    args = parser.parse_args()
    
    # Load configuration
    print(f"Loading configuration: {args.config}")
    if args.config.endswith('.json'):
        config = RolloutConfig.from_json(args.config)
    elif args.config.endswith('.yaml') or args.config.endswith('.yml'):
        config = RolloutConfig.from_yaml(args.config)
    else:
        raise ValueError("Configuration file must be .json or .yaml format")
    
    # Apply overrides
    if args.data:
        config.data_path = args.data
    if args.model:
        config.model_name = args.model
    if args.max_tasks:
        config.number_of_tasks = args.max_tasks
    if args.task_ids:
        config.task_ids = args.task_ids
    if args.no_eval:
        config.evaluate_results = False
    if args.parallel:
        config.parallel = True
    if args.max_workers:
        config.max_workers = args.max_workers
    if args.metric:
        config.evaluation_metric = args.metric
    
    # Determine output directory
    output_dir = args.output_dir or config.output_dir or "rollout_results"
    
    print(f"Output directory: {output_dir}")
    
    # Run pipeline
    pipeline = RolloutPipeline(config=config, output_dir=output_dir)
    
    try:
        summary = pipeline.run()
        
        print(f"\n🏁 Final Summary:")
        for key, value in summary.to_dict().items():
            print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"❌ Run failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
