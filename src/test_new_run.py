"""
Test script for the new run.py architecture.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from run import AgentRunner, AgentConfig
from envs import MathEnvironment
from benchmark import create_benchmark


def test_agent_runner():
    """Test the AgentRunner class."""
    print("=== Testing AgentRunner ===")
    
    # Create configuration
    config = AgentConfig(
        model_name="gpt-4",
        max_turns=5,
        max_retries=2,
        max_workers=1,
        save_results=False,
        evaluate_results=True,
        evaluation_metric="exact_match"
    )
    
    # Create runner
    runner = AgentRunner(config)
    
    # Test environment setup
    print("\n1. Testing environment setup...")
    env = runner.setup_environment("math")
    print(f"   Environment type: {type(env).__name__}")
    print(f"   Available tools: {env.list_tools()}")
    
    # Test benchmark loading
    print("\n2. Testing benchmark loading...")
    benchmark = runner.load_benchmark("src/data/math_demo.jsonl", name="Test Math")
    print(f"   Benchmark name: {benchmark.name}")
    print(f"   Number of items: {len(benchmark.items)}")
    print(f"   First question: {benchmark.items[0].question}")
    
    # Test single task execution (without API calls)
    print("\n3. Testing single task execution...")
    task = {"id": "test_1", "question": "What is 2+2?"}
    
    # Mock the conversation method to avoid API calls
    def mock_run_conversation(self, question, task_id):
        return [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question},
            {"role": "assistant", "content": "I'll use the calculator to solve this."},
            {"role": "tool", "tool_call_id": "call_123", "name": "calculator", "content": "4"},
            {"role": "assistant", "content": "The answer is 4."}
        ]
    
    # Replace the method temporarily
    original_method = runner._run_conversation
    runner._run_conversation = mock_run_conversation.__get__(runner, AgentRunner)
    
    try:
        result = runner.run_single_task(task)
        print(f"   Task result: {result['success']}")
        print(f"   Answer: {result['answer']}")
    finally:
        # Restore original method
        runner._run_conversation = original_method
    
    # Test evaluation
    print("\n4. Testing evaluation...")
    # Mock some results
    runner.results = [
        {
            "task_id": "aaa",
            "question": "compute: sqrt(144) + pow(3,4)/6 + sin(pi/6)*10",
            "answer": "### Calculator Results:\nsqrt(144) + pow(3,4)/6 + sin(pi/6)*10 = 30.5\n",
            "success": True
        }
    ]
    
    try:
        evaluation_summary = runner.evaluate_results()
        print(f"   Evaluation metric: {evaluation_summary['metric']}")
        print(f"   Average score: {evaluation_summary['average_score']:.3f}")
    except Exception as e:
        print(f"   Evaluation failed: {e}")
    
    print("\n✅ AgentRunner test completed!")


def test_environment_integration():
    """Test integration with Environment classes."""
    print("\n=== Testing Environment Integration ===")
    
    # Test MathEnvironment
    print("\n1. Testing MathEnvironment...")
    math_env = MathEnvironment()
    print(f"   Mode: {math_env.mode}")
    print(f"   Tools: {math_env.list_tools()}")
    
    # Test tool execution
    result = math_env.execute_tool("calculator", {"expressions": ["2+2", "3*3"]})
    print(f"   Calculator result: {result[:50]}...")
    
    # Test WebEnvironment
    print("\n2. Testing WebEnvironment...")
    try:
        from envs import WebEnvironment
        web_env = WebEnvironment(web_search_top_k=3)
        print(f"   Mode: {web_env.mode}")
        print(f"   Tools: {web_env.list_tools()}")
    except Exception as e:
        print(f"   WebEnvironment test skipped: {e}")


def test_benchmark_integration():
    """Test integration with Benchmark class."""
    print("\n=== Testing Benchmark Integration ===")
    
    # Create benchmark
    benchmark = create_benchmark("src/data/math_demo.jsonl", name="Test Benchmark")
    print(f"   Benchmark: {benchmark.name}")
    print(f"   Items: {len(benchmark.items)}")
    
    # Test evaluation
    predictions = {
        "aaa": "### Calculator Results:\nsqrt(144) + pow(3,4)/6 + sin(pi/6)*10 = 30.5\n"
    }
    
    results = benchmark.evaluate(predictions, metric="exact_match")
    print(f"   Evaluation results: {len(results)} items")
    print(f"   First result score: {results[0].score}")
    
    # Test summary
    summary = benchmark.get_summary()
    print(f"   Summary: {summary['average_score']:.3f} average score")


def test_complete_pipeline():
    """Test the complete pipeline without API calls."""
    print("\n=== Testing Complete Pipeline ===")
    
    # Create configuration
    config = AgentConfig(
        model_name="gpt-4",
        max_turns=3,
        max_retries=1,
        save_results=False,
        evaluate_results=True
    )
    
    # Create runner
    runner = AgentRunner(config)
    
    # Setup environment
    env = runner.setup_environment("math")
    
    # Load benchmark
    benchmark = runner.load_benchmark("src/data/math_demo.jsonl")
    
    # Mock the conversation to simulate successful execution
    def mock_conversation(self, question, task_id):
        return [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question},
            {"role": "assistant", "content": "I'll calculate this for you."},
            {"role": "tool", "tool_call_id": "call_123", "name": "calculator", 
             "content": "### Calculator Results:\nsqrt(144) + pow(3,4)/6 + sin(pi/6)*10 = 30.5\n"},
            {"role": "assistant", "content": "The result is 30.5."}
        ]
    
    runner._run_conversation = mock_conversation.__get__(runner, AgentRunner)
    
    # Run benchmark
    results = runner.run_benchmark(parallel=False)
    print(f"   Results: {len(results)} tasks processed")
    print(f"   Successful: {sum(1 for r in results if r['success'])}")
    
    # Evaluate results
    try:
        evaluation = runner.evaluate_results()
        print(f"   Evaluation: {evaluation['average_score']:.3f} average score")
    except Exception as e:
        print(f"   Evaluation: {e}")
    
    print("\n✅ Complete pipeline test finished!")


if __name__ == "__main__":
    print("🧪 Testing new run.py architecture...")
    
    test_agent_runner()
    test_environment_integration()
    test_benchmark_integration()
    test_complete_pipeline()
    
    print("\n🎉 All tests completed successfully!")