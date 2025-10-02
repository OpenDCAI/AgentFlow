"""
Integration test showing how Benchmark works with Environment classes.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmark import create_benchmark, Benchmark
from envs import MathEnvironment, WebEnvironment


def test_math_environment_with_benchmark():
    """Test MathEnvironment with math benchmark."""
    print("=== Math Environment + Benchmark Integration ===")
    
    # Create math environment
    math_env = MathEnvironment()
    print(f"Math environment tools: {math_env.list_tools()}")
    
    # Load math benchmark
    benchmark = create_benchmark(
        data_path="../data/math_demo.jsonl",
        name="Math Integration Test"
    )
    
    print(f"Loaded {len(benchmark.items)} benchmark items")
    
    # Simulate running the environment on benchmark questions
    predictions = {}
    for item in benchmark.items:
        print(f"\nProcessing question: {item.question}")
        
        # Use the environment to solve the question
        # In a real scenario, this would involve the full agent pipeline
        # For this test, we'll simulate by calling the calculator tool directly
        try:
            # Extract the math expression from the question
            # This is a simplified extraction - in practice, you'd use NLP
            if "compute:" in item.question:
                expression = item.question.split("compute:")[1].strip()
                # Use the calculator tool
                result = math_env.execute_tool("calculator", {"expressions": [expression]})
                predictions[item.id] = result
                print(f"Generated prediction: {result[:100]}...")
            else:
                predictions[item.id] = "Could not extract expression"
                print("Could not extract math expression")
        except Exception as e:
            predictions[item.id] = f"Error: {str(e)}"
            print(f"Error processing: {e}")
    
    # Evaluate predictions
    print("\n=== Evaluation Results ===")
    results = benchmark.evaluate(predictions, metric="exact_match")
    
    for result in results:
        status = "✓" if result.score == 1.0 else "✗"
        print(f"{status} Question: {result.question[:50]}...")
        print(f"   Ground Truth: {result.ground_truth[:50]}...")
        print(f"   Prediction: {result.prediction[:50]}...")
        print(f"   Score: {result.score}")
        print()
    
    # Get summary
    summary = benchmark.get_summary()
    print(f"Summary: {summary}")


def test_web_environment_with_benchmark():
    """Test WebEnvironment with web benchmark."""
    print("\n=== Web Environment + Benchmark Integration ===")
    
    # Create web environment
    web_env = WebEnvironment()
    print(f"Web environment tools: {web_env.list_tools()}")
    
    # Load web benchmark
    benchmark = create_benchmark(
        data_path="../data/webagent_demo.jsonl",
        name="Web Integration Test"
    )
    
    print(f"Loaded {len(benchmark.items)} benchmark items")
    
    # Simulate running the environment on benchmark questions
    predictions = {}
    for item in benchmark.items:
        print(f"\nProcessing question: {item.question}")
        
        # Simulate web search and visit process
        # In a real scenario, this would involve the full agent pipeline
        try:
            # Simulate web search
            search_result = web_env.execute_tool("web_search", {
                "queries": [item.question]
            })
            print(f"Search result: {search_result[:100]}...")
            
            # For this test, we'll create a mock prediction
            # In practice, you'd process the search results and generate an answer
            mock_prediction = f"Based on web search for '{item.question}', here is a comprehensive answer..."
            predictions[item.id] = mock_prediction
            print(f"Generated prediction: {mock_prediction[:100]}...")
            
        except Exception as e:
            predictions[item.id] = f"Error: {str(e)}"
            print(f"Error processing: {e}")
    
    # Evaluate predictions (using similarity since we don't have ground truth)
    print("\n=== Evaluation Results ===")
    # Since webagent_demo doesn't have answers, we'll create mock ground truth
    mock_ground_truth = {
        "webagent_1": "There are approximately 2,500 death row inmates in the US.",
        "webagent_3": "AI development is rapidly advancing with breakthroughs in large language models, computer vision, and autonomous systems."
    }
    
    # Add mock ground truth to benchmark items
    for item in benchmark.items:
        if item.id in mock_ground_truth:
            item.answer = mock_ground_truth[item.id]
    
    results = benchmark.evaluate(predictions, metric="similarity")
    
    for result in results:
        print(f"Question: {result.question}")
        print(f"Ground Truth: {result.ground_truth}")
        print(f"Prediction: {result.prediction[:100]}...")
        print(f"Similarity Score: {result.score:.3f}")
        print()
    
    # Get summary
    summary = benchmark.get_summary()
    print(f"Summary: {summary}")


def test_custom_benchmark():
    """Test with a custom benchmark."""
    print("\n=== Custom Benchmark Test ===")
    
    # Create a custom benchmark
    from benchmark import Benchmark
    
    benchmark = Benchmark(name="Custom Test", description="Custom benchmark for testing")
    
    # Add custom items
    custom_items = [
        {
            "id": "custom_1",
            "question": "What is the capital of France?",
            "answer": "Paris"
        },
        {
            "id": "custom_2", 
            "question": "What is 5 * 7?",
            "answer": "35"
        },
        {
            "id": "custom_3",
            "question": "What is the largest planet in our solar system?",
            "answer": "Jupiter"
        }
    ]
    
    for item_data in custom_items:
        item = benchmark._parse_item(item_data, 1)
        benchmark.items.append(item)
    
    print(f"Created custom benchmark with {len(benchmark.items)} items")
    
    # Create predictions (some correct, some wrong)
    predictions = {
        "custom_1": "Paris",  # Correct
        "custom_2": "34",     # Wrong
        "custom_3": "Jupiter" # Correct
    }
    
    # Test different metrics
    metrics = ["exact_match", "f1_score", "similarity"]
    
    for metric in metrics:
        print(f"\n--- Testing {metric} ---")
        results = benchmark.evaluate(predictions, metric=metric)
        
        for result in results:
            status = "✓" if result.score > 0.8 else "✗"
            print(f"{status} {result.question} -> {result.prediction} (Score: {result.score:.3f})")
        
        summary = benchmark.get_summary()
        print(f"Average {metric} score: {summary['average_score']:.3f}")


def test_benchmark_persistence():
    """Test saving and loading benchmark results."""
    print("\n=== Benchmark Persistence Test ===")
    
    # Create and evaluate a benchmark
    benchmark = create_benchmark(
        data_path="../data/math_demo.jsonl",
        name="Persistence Test"
    )
    
    predictions = {"aaa": "### Calculator Results:\nsqrt(144) + pow(3,4)/6 + sin(pi/6)*10 = 30.5\n"}
    results = benchmark.evaluate(predictions, metric="f1_score")
    
    # Save results
    benchmark.save_results("integration_test_results.json")
    print("Results saved")
    
    # Create new benchmark and load results
    new_benchmark = Benchmark(name="Loaded Test")
    new_benchmark.load_results("integration_test_results.json")
    
    print(f"Loaded benchmark: {new_benchmark.name}")
    print(f"Loaded {len(new_benchmark.evaluation_results)} results")
    
    # Clean up
    import os
    if os.path.exists("integration_test_results.json"):
        os.remove("integration_test_results.json")
        print("Cleanup completed")


if __name__ == "__main__":
    # Run integration tests
    test_math_environment_with_benchmark()
    test_web_environment_with_benchmark()
    test_custom_benchmark()
    test_benchmark_persistence()
    
    print("\n=== All integration tests completed ===")