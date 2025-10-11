"""
AgentFlow - Main execution script using Environment and Benchmark modules.

This script provides a unified interface for running agents on different benchmarks
using the Environment and Benchmark classes.
"""

import openai
import json
import os
import argparse
import concurrent.futures
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import our custom modules
from envs import (
    MathEnvironment, 
    PythonEnvironment, 
    RAGEnvironment, 
    WebEnvironment,
    Environment
)
from benchmark import Benchmark, create_benchmark


# Configuration
@dataclass
class AgentConfig:
    """Configuration for agent execution."""
    model_name: str = "gpt-4.1-2025-04-14"
    max_turns: int = 20
    max_retries: int = 3
    max_workers: int = 1
    save_results: bool = True
    evaluate_results: bool = True
    evaluation_metric: str = "exact_match"


# System prompts
SYSTEM_PROMPT_GENERIC = """You are a helpful assistant. You need to use tools to solve the problem.

## Available Tools

{tool_descriptions}

## Tool Usage Strategy

**For Multi-Step Analysis:**
1. Break complex problems into logical steps
2. Use ONE tool at a time to gather information
3. Verify findings through different approaches when possible
"""


class AgentRunner:
    """
    Main agent runner that coordinates Environment and Benchmark.
    
    This class handles:
    - Loading benchmarks
    - Setting up environments
    - Running agents on benchmark tasks
    - Evaluating results
    - Saving outputs
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize the agent runner."""
        self.config = config
        self.environment: Optional[Environment] = None
        self.benchmark: Optional[Benchmark] = None
        self.results: List[Dict[str, Any]] = []
        
        # Validate OpenAI configuration
        self._validate_openai_config()
    
    def _validate_openai_config(self):
        """Validate OpenAI API configuration."""
        openai.api_key = os.environ.get("OPENAI_API_KEY", "")
        openai.base_url = os.environ.get("OPENAI_API_URL", os.environ.get("OPENAI_API_BASE", ""))
        
        if not openai.api_key:
            print("Warning: OPENAI_API_KEY is not set. Some features may not work properly.")
        if not openai.base_url:
            print("Warning: OPENAI_API_URL or OPENAI_API_BASE is not set. Some features may not work properly.")
    
    def setup_environment(self, mode: str, **kwargs) -> Environment:
        """
        Setup environment based on mode.
        
        Args:
            mode: Environment mode ("math", "py", "rag", "web")
            **kwargs: Additional configuration for the environment
            
        Returns:
            Configured environment
        """
        print(f"Setting up {mode} environment...")
        
        if mode == "math":
            self.environment = MathEnvironment(**kwargs)
        elif mode == "py":
            self.environment = PythonEnvironment(**kwargs)
        elif mode == "rag":
            self.environment = RAGEnvironment(**kwargs)
        elif mode == "web":
            self.environment = WebEnvironment(**kwargs)
        else:
            raise ValueError(f"Unknown mode: {mode}")
        
        print(f"Environment setup complete. Available tools: {self.environment.list_tools()}")
        return self.environment
    
    def load_benchmark(self, data_path: str, name: Optional[str] = None, **kwargs) -> Benchmark:
        """
        Load benchmark from data file.
        
        Args:
            data_path: Path to benchmark data
            name: Name of the benchmark
            **kwargs: Additional configuration (filtered for benchmark)
            
        Returns:
            Loaded benchmark
        """
        print(f"Loading benchmark from {data_path}...")
        
        # Filter kwargs to only include benchmark-relevant parameters
        benchmark_kwargs = {k: v for k, v in kwargs.items() 
                           if k in ['description']}
        
        self.benchmark = create_benchmark(
            data_path=data_path,
            name=name or f"Benchmark_{os.path.basename(data_path)}",
            **benchmark_kwargs
        )
        
        print(f"Benchmark loaded: {len(self.benchmark.items)} items")
        return self.benchmark
    
    def run_single_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run agent on a single task.
        
        Args:
            task: Task dictionary with 'id' and 'question'
            
        Returns:
            Result dictionary
        """
        if not self.environment:
            raise ValueError("Environment not set up")
        
        task_id = task["id"]
        question = task["question"]
        
        print(f"\n{'='*60}")
        print(f"Processing Task {task_id}")
        print(f"Question: {question}")
        print(f"{'='*60}")
        
        try:
            # Run multi-turn conversation
            messages = self._run_conversation(question, task_id)
            
            # Extract final answer
            final_answer = self._extract_final_answer(messages)
            
            result = {
                "task_id": task_id,
                "question": question,
                "answer": final_answer,
                "messages": messages,
                "success": True,
                "error": None
            }
            
            print(f"✓ Task {task_id} completed successfully")
            print(f"Answer: {final_answer[:100]}...")
            
        except Exception as e:
            print(f"✗ Task {task_id} failed: {str(e)}")
            result = {
                "task_id": task_id,
                "question": question,
                "answer": "",
                "messages": [],
                "success": False,
                "error": str(e)
            }
        
        return result
    
    def _run_conversation(self, question: str, task_id: str) -> List[Dict[str, Any]]:
        """
        Run multi-turn conversation with the agent.
        
        Args:
            question: User question
            task_id: Task identifier
            
        Returns:
            List of messages from the conversation
        """
        # Prepare system prompt
        system_prompt = SYSTEM_PROMPT_GENERIC.replace(
            "{tool_descriptions}", 
            self.environment.get_tool_descriptions()
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
        
        # Initialize OpenAI client
        client = openai.OpenAI(
            api_key=openai.api_key,
            base_url=openai.base_url
        )
        
        turn_count = 0
        
        while turn_count < self.config.max_turns:
            retry = 0
            
            while retry < self.config.max_retries:
                try:
                    # Get response from OpenAI
                    response = client.chat.completions.create(
                        model=self.config.model_name,
                        messages=messages,
                        tools=self.environment.get_tool_schemas()
                    )
                    
                    assistant_message = response.choices[0].message
                    # Convert to dict format for consistency
                    messages.append(assistant_message.model_dump())
                    
                    if assistant_message.tool_calls:
                        # Execute tool calls
                        for tool_call in assistant_message.tool_calls:
                            tool_name = tool_call.function.name
                            tool_args = json.loads(tool_call.function.arguments)
                            
                            print(f"🔧 Using tool: {tool_name}")
                            print(f"   Arguments: {tool_args}")
                            
                            # Execute tool
                            tool_result = self.environment.execute_tool(
                                tool_name, 
                                tool_args
                            )
                            
                            print(f"   Result: {tool_result[:100]}...")
                            
                            # Add tool result to conversation
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_name,
                                "content": tool_result
                            })
                        
                        # Continue conversation after tool use
                        turn_count += 1
                        break
                    
                    else:
                        # No tool calls, conversation complete
                        print(f"💬 Final answer at turn {turn_count}")
                        return messages
                
                except Exception as e:
                    print(f"⚠️  Retry {retry + 1}/{self.config.max_retries}: {str(e)}")
                    retry += 1
                    if retry >= self.config.max_retries:
                        raise e
            
            turn_count += 1
        
        print(f"⚠️  Max turns ({self.config.max_turns}) reached")
        return messages
    
    def _extract_final_answer(self, messages: List[Dict[str, Any]]) -> str:
        """
        Extract final answer from conversation messages.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Final answer string
        """
        # Find the last assistant message without tool calls
        for message in reversed(messages):
            # Handle both dict and object types
            if hasattr(message, 'role'):
                # OpenAI message object
                if (message.role == "assistant" and 
                    not hasattr(message, 'tool_calls') or not message.tool_calls):
                    return getattr(message, 'content', "")
            else:
                # Dict format
                if (message.get("role") == "assistant" and 
                    not message.get("tool_calls")):
                    return message.get("content", "")
        
        return "No final answer found"
    
    def run_benchmark(self, parallel: bool = False) -> List[Dict[str, Any]]:
        """
        Run agent on all benchmark tasks.
        
        Args:
            parallel: Whether to run tasks in parallel
            
        Returns:
            List of results
        """
        if not self.benchmark:
            raise ValueError("Benchmark not loaded")
        
        print(f"\n🚀 Starting benchmark execution...")
        print(f"   Tasks: {len(self.benchmark.items)}")
        print(f"   Parallel: {parallel}")
        print(f"   Max workers: {self.config.max_workers}")
        
        # Prepare tasks
        tasks = [
            {"id": item.id, "question": item.question}
            for item in self.benchmark.items
        ]
        
        if parallel and len(tasks) > 1:
            # Run in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                futures = [
                    executor.submit(self.run_single_task, task) 
                    for task in tasks
                ]
                
                self.results = []
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    self.results.append(result)
        else:
            # Run sequentially
            self.results = []
            for task in tasks:
                result = self.run_single_task(task)
                self.results.append(result)
        
        print(f"\n✅ Benchmark execution completed!")
        print(f"   Successful: {sum(1 for r in self.results if r['success'])}")
        print(f"   Failed: {sum(1 for r in self.results if not r['success'])}")
        
        return self.results
    
    def evaluate_results(self) -> Dict[str, Any]:
        """
        Evaluate results against benchmark ground truth.
        
        Returns:
            Evaluation summary
        """
        if not self.benchmark or not self.results:
            raise ValueError("No benchmark or results to evaluate")
        
        print(f"\n📊 Evaluating results...")
        
        # Prepare predictions
        predictions = {}
        for result in self.results:
            if result["success"]:
                predictions[result["task_id"]] = result["answer"]
        
        # Run evaluation
        evaluation_results = self.benchmark.evaluate(
            predictions, 
            metric=self.config.evaluation_metric
        )
        
        # Get summary
        summary = self.benchmark.get_summary()
        
        print(f"📈 Evaluation Summary:")
        print(f"   Metric: {summary.get('metric', 'unknown')}")
        print(f"   Average Score: {summary.get('average_score', 0.0):.3f}")
        print(f"   Perfect Matches: {summary.get('perfect_matches', 0)}")
        print(f"   Total Items: {summary.get('total_items', 0)}")
        
        return summary
    
    def save_results(self, output_dir: str = "results") -> str:
        """
        Save results to files.
        
        Args:
            output_dir: Output directory
            
        Returns:
            Path to saved results
        """
        if not self.results:
            print("No results to save")
            return ""
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output filename
        benchmark_name = self.benchmark.name if self.benchmark else "unknown"
        output_file = os.path.join(output_dir, f"result_{benchmark_name}.jsonl")
        
        # Save results
        with open(output_file, "w", encoding="utf-8") as f:
            for result in self.results:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
        
        print(f"💾 Results saved to: {output_file}")
        
        # Save evaluation results if available
        if self.config.evaluate_results and self.benchmark.evaluation_results:
            eval_file = os.path.join(output_dir, f"evaluation_{benchmark_name}.json")
            self.benchmark.save_results(eval_file)
            print(f"📊 Evaluation results saved to: {eval_file}")
        
        return output_file
    
    def run(self, mode: str, data_path: str, **kwargs) -> Dict[str, Any]:
        """
        Complete run pipeline.
        
        Args:
            mode: Environment mode
            data_path: Path to benchmark data
            **kwargs: Additional configuration
            
        Returns:
            Run summary
        """
        print(f"🎯 Starting AgentFlow run...")
        print(f"   Mode: {mode}")
        print(f"   Data: {data_path}")
        
        # Setup environment
        self.setup_environment(mode, **kwargs)
        
        # Load benchmark
        self.load_benchmark(data_path, **kwargs)
        
        # Run benchmark
        self.run_benchmark(parallel=kwargs.get('parallel', False))
        
        # Evaluate results
        if self.config.evaluate_results:
            evaluation_summary = self.evaluate_results()
        else:
            evaluation_summary = None
        
        # Save results
        if self.config.save_results:
            output_file = self.save_results()
        else:
            output_file = ""
        
        # Return summary
        summary = {
            "mode": mode,
            "data_path": data_path,
            "total_tasks": len(self.results),
            "successful_tasks": sum(1 for r in self.results if r["success"]),
            "failed_tasks": sum(1 for r in self.results if not r["success"]),
            "evaluation": evaluation_summary,
            "output_file": output_file
        }
        
        print(f"\n🎉 Run completed successfully!")
        print(f"   Summary: {summary}")
        
        return summary


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AgentFlow - Agent execution with Environment and Benchmark")
    
    # Required arguments
    parser.add_argument("--mode", type=str, choices=["math", "py", "rag", "web"], 
                       required=True, help="Environment mode")
    parser.add_argument("--data", type=str, required=True, 
                       help="Path to benchmark data file")
    
    # Optional arguments
    parser.add_argument("--model", type=str, default="gpt-4.1-2025-04-14",
                       help="OpenAI model name")
    parser.add_argument("--max-turns", type=int, default=20,
                       help="Maximum conversation turns")
    parser.add_argument("--max-retries", type=int, default=3,
                       help="Maximum retries per turn")
    parser.add_argument("--max-workers", type=int, default=1,
                       help="Maximum parallel workers")
    parser.add_argument("--output-dir", type=str, default="results",
                       help="Output directory for results")
    parser.add_argument("--no-eval", action="store_true",
                       help="Skip evaluation")
    parser.add_argument("--no-save", action="store_true",
                       help="Skip saving results")
    parser.add_argument("--parallel", action="store_true",
                       help="Run tasks in parallel")
    parser.add_argument("--metric", type=str, default="exact_match",
                       choices=["exact_match", "f1_score", "similarity", "contains_answer", "numeric_match", "llm_judgement"],
                       help="Evaluation metric")
    
    # Environment-specific arguments
    parser.add_argument("--web-search-top-k", type=int, default=5,
                       help="Web search top-k results")
    parser.add_argument("--web-search-type", type=str, default="search",
                       choices=["search", "news", "images"],
                       help="Web search type")
    parser.add_argument("--kb-path", type=str,
                       help="Knowledge base path for RAG mode")
    parser.add_argument("--emb-model", type=str, default="text-embedding-3-small",
                       help="Embedding model used for RAG mode")
    parser.add_argument("--emb-batchsize", type=int, default=512,
                       help="Batchsize of embedding for RAG mode")
    parser.add_argument("--index-path", type=str, default='',
                       help="Index path for RAG mode")
    parser.add_argument("--use-faiss", action="store_true",
                       help="Whether to use Faiss for RAG mode")
    parser.add_argument("--load-index", action="store_true",
                       help="Whether to load exsiting index for RAG mode")
    
    args = parser.parse_args()

    # python src/run.py --mode rag --data src/data/rag_demo.jsonl --kb-path src/data/kb_demo.json --index-path src/index/ --metric llm_judgement --load-index
    
    # Create configuration
    config = AgentConfig(
        model_name=args.model,
        max_turns=args.max_turns,
        max_retries=args.max_retries,
        max_workers=args.max_workers,
        save_results=not args.no_save,
        evaluate_results=not args.no_eval,
        evaluation_metric=args.metric
    )
    
    # Prepare environment-specific arguments
    env_kwargs = {}
    if args.mode == "web":
        env_kwargs.update({
            "web_search_top_k": args.web_search_top_k,
            "web_search_type": args.web_search_type
        })
    elif args.mode == "rag" and args.kb_path:
        from tools.rag_tools import get_rag_index_class
        use_faiss_flag = args.use_faiss
        IndexClass = get_rag_index_class(use_faiss=use_faiss_flag)
        rag_index = None
        client = openai.OpenAI(
            api_key=openai.api_key,
            base_url=openai.base_url 
        )
        if args.load_index:
            try:
                print(f"Attempting to load RAG index from {args.index_path}")
                rag_index = IndexClass.load_index(args.index_path, client)
            except FileNotFoundError:
                print(f"No existing index found at {args.index_path}. Will build a new one.")
        
        if rag_index is None:
            if not args.kb_path:
                raise ValueError("--kb-path is required to build a new RAG index.")
            
            print(f"Building new RAG index from {args.kb_path}...")
            rag_index = IndexClass(client, model=args.emb_model)
            rag_index.build_index(file_path=args.kb_path, batch_size=args.emb_batchsize)
            
            if args.index_path:
                rag_index.save_index(args.index_path)

        env_kwargs["rag_index"] = rag_index    # will pass it to RAGEnvironment

    # Create and run agent
    runner = AgentRunner(config)
    
    try:
        summary = runner.run(
            mode=args.mode,
            data_path=args.data,
            parallel=args.parallel,
            **env_kwargs
        )
        
        print(f"\n🏁 Final Summary:")
        for key, value in summary.items():
            print(f"   {key}: {value}")
            
    except Exception as e:
        print(f"❌ Run failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()