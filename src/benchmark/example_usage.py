"""
Example usage of the Benchmark class for AgentFlow.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmark import Benchmark, create_benchmark


def example_basic_usage():
    """Basic benchmark usage example."""
    print("=== Basic Benchmark Usage ===")
    
    # Create benchmark from data file
    benchmark = create_benchmark(
        data_path="../data/math_demo.jsonl",
        name="Math Demo",
        description="Simple math calculation benchmark"
    )
    
    print(f"Benchmark name: {benchmark.name}")
    print(f"Total items: {len(benchmark.items)}")
    print(f"First question: {benchmark.items[0].question}")
    print(f"First answer: {benchmark.items[0].answer}")
    
    # Get all questions and answers
    questions = benchmark.get_questions()
    answers = benchmark.get_answers()
    print(f"Questions: {questions}")
    print(f"Answers: {answers}")


def example_evaluation():
    """Example of evaluating predictions."""
    print("\n=== Evaluation Example ===")
    
    # Load benchmark
    benchmark = create_benchmark(
        data_path="../data/math_demo.jsonl",
        name="Math Demo"
    )
    
    # Create some predictions (in this case, perfect predictions)
    predictions = {
        "aaa": "### Calculator Results:\nsqrt(144) + pow(3,4)/6 + sin(pi/6)*10 = 30.5\n"
    }
    
    # Evaluate with different metrics
    print("Evaluating with exact match...")
    results = benchmark.evaluate(predictions, metric="exact_match")
    for result in results:
        print(f"Item {result.item_id}: Score = {result.score}")
    
    print("\nEvaluating with F1 score...")
    results = benchmark.evaluate(predictions, metric="f1_score")
    for result in results:
        print(f"Item {result.item_id}: Score = {result.score}")
        print(f"Details: {result.details}")
    
    print("\nEvaluating with similarity...")
    results = benchmark.evaluate(predictions, metric="similarity")
    for result in results:
        print(f"Item {result.item_id}: Score = {result.score}")


def example_wrong_predictions():
    """Example with wrong predictions to show different metrics."""
    print("\n=== Wrong Predictions Example ===")
    
    benchmark = create_benchmark(
        data_path="../data/math_demo.jsonl",
        name="Math Demo"
    )
    
    # Create wrong predictions
    wrong_predictions = {
        "aaa": "The answer is 25.5"  # Wrong answer
    }
    
    # Test different metrics
    metrics = ["exact_match", "f1_score", "similarity", "contains_answer", "numeric_match"]
    
    for metric in metrics:
        print(f"\nEvaluating with {metric}...")
        results = benchmark.evaluate(wrong_predictions, metric=metric)
        for result in results:
            print(f"Score: {result.score}")
            if result.details:
                print(f"Details: {result.details}")


def example_multiple_items():
    """Example with multiple items."""
    print("\n=== Multiple Items Example ===")
    
    # Create a custom benchmark with multiple items
    benchmark = Benchmark(name="Custom Test", description="Test with multiple items")
    
    # Add items manually
    items_data = [
        {"id": "q1", "question": "What is 2+2?", "answer": "4"},
        {"id": "q2", "question": "What is 3*3?", "answer": "9"},
        {"id": "q3", "question": "What is 10/2?", "answer": "5"}
    ]
    
    for item_data in items_data:
        item = benchmark._parse_item(item_data, 1)
        benchmark.items.append(item)
    
    print(f"Created benchmark with {len(benchmark.items)} items")
    
    # Create predictions (some correct, some wrong)
    predictions = {
        "q1": "4",      # Correct
        "q2": "8",      # Wrong
        "q3": "5"       # Correct
    }
    
    # Evaluate
    results = benchmark.evaluate(predictions, metric="exact_match")
    
    print("\nEvaluation results:")
    for result in results:
        status = "✓" if result.score == 1.0 else "✗"
        print(f"{status} {result.question} -> {result.prediction} (Score: {result.score})")
    
    # Get summary
    summary = benchmark.get_summary()
    print(f"\nSummary: {summary}")


def example_save_load_results():
    """Example of saving and loading results."""
    print("\n=== Save/Load Results Example ===")
    
    benchmark = create_benchmark(
        data_path="../data/math_demo.jsonl",
        name="Math Demo"
    )
    
    # Evaluate
    predictions = {"aaa": "### Calculator Results:\nsqrt(144) + pow(3,4)/6 + sin(pi/6)*10 = 30.5\n"}
    results = benchmark.evaluate(predictions, metric="f1_score")
    
    # Save results
    benchmark.save_results("example_results.json")
    
    # Create new benchmark and load results
    new_benchmark = Benchmark(name="Loaded Benchmark")
    new_benchmark.load_results("example_results.json")
    
    print(f"Loaded benchmark: {new_benchmark.name}")
    print(f"Loaded {len(new_benchmark.evaluation_results)} results")
    
    # Clean up
    import os
    if os.path.exists("example_results.json"):
        os.remove("example_results.json")


def example_custom_metric():
    """Example of using custom evaluation logic."""
    print("\n=== Custom Metric Example ===")
    
    benchmark = create_benchmark(
        data_path="../data/math_demo.jsonl",
        name="Math Demo"
    )
    
    # Add a custom metric function
    def custom_math_metric(ground_truth: str, prediction: str, **kwargs) -> float:
        """Custom metric that checks if the final numeric answer matches."""
        gt_numbers = benchmark._extract_numbers(ground_truth)
        pred_numbers = benchmark._extract_numbers(prediction)
        
        if not gt_numbers or not pred_numbers:
            return 0.0
        
        # Check if the last number in ground truth matches any number in prediction
        last_gt_number = gt_numbers[-1]
        return 1.0 if any(abs(last_gt_number - pred_num) < 1e-6 for pred_num in pred_numbers) else 0.0
    
    # Store original method
    original_get_metric_function = benchmark._get_metric_function
    
    # Register the custom metric
    def custom_get_metric_function(metric):
        if metric == 'custom_math':
            return custom_math_metric
        else:
            return original_get_metric_function(metric)
    
    benchmark._get_metric_function = custom_get_metric_function
    
    # Test with custom metric
    predictions = {"aaa": "The result is 30.5"}  # Contains the correct final answer
    results = benchmark.evaluate(predictions, metric="custom_math")
    
    print(f"Custom metric score: {results[0].score}")


if __name__ == "__main__":
    # Run all examples
    example_basic_usage()
    example_evaluation()
    example_wrong_predictions()
    example_multiple_items()
    example_save_load_results()
    example_custom_metric()
    
    print("\n=== All examples completed ===")