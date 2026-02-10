"""
Tests for Evaluator
"""

import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rollout.core import Evaluator, TaskResult, evaluate_results


class TestEvaluator:
    """Test Evaluator class"""

    def test_exact_match_correct(self):
        """Test exact match with correct answer"""
        evaluator = Evaluator(metric="exact_match")
        
        results = [
            TaskResult(
                task_id="1",
                question="What is 2+2?",
                predicted_answer="4",
                ground_truth="4",
                success=True
            )
        ]
        
        evaluation = evaluator.evaluate(results)
        
        assert evaluation["average_score"] == 1.0
        assert evaluation["perfect_matches"] == 1

    def test_exact_match_incorrect(self):
        """Test exact match with incorrect answer"""
        evaluator = Evaluator(metric="exact_match")
        
        results = [
            TaskResult(
                task_id="1",
                question="What is 2+2?",
                predicted_answer="5",
                ground_truth="4",
                success=True
            )
        ]
        
        evaluation = evaluator.evaluate(results)
        
        assert evaluation["average_score"] == 0.0
        assert evaluation["perfect_matches"] == 0

    def test_exact_match_normalized(self):
        """Test exact match with normalization"""
        evaluator = Evaluator(metric="exact_match")
        
        results = [
            TaskResult(
                task_id="1",
                question="Capital of France?",
                predicted_answer="The answer is Paris.",
                ground_truth="paris",
                success=True
            )
        ]
        
        evaluation = evaluator.evaluate(results)
        
        # Should match after normalization
        assert evaluation["average_score"] == 1.0

    def test_f1_score(self):
        """Test F1 score metric"""
        evaluator = Evaluator(metric="f1_score")
        
        results = [
            TaskResult(
                task_id="1",
                question="What is Python?",
                predicted_answer="Python is a programming language",
                ground_truth="Python is a popular programming language",
                success=True
            )
        ]
        
        evaluation = evaluator.evaluate(results)
        
        # Should have high but not perfect F1
        assert 0.5 < evaluation["average_score"] < 1.0

    def test_contains_answer(self):
        """Test contains_answer metric"""
        evaluator = Evaluator(metric="contains_answer")
        
        results = [
            TaskResult(
                task_id="1",
                question="What is the capital?",
                predicted_answer="The capital of France is Paris, which is a beautiful city.",
                ground_truth="Paris",
                success=True
            )
        ]
        
        evaluation = evaluator.evaluate(results)
        
        assert evaluation["average_score"] == 1.0

    def test_numeric_match(self):
        """Test numeric_match metric"""
        evaluator = Evaluator(metric="numeric_match")
        
        results = [
            TaskResult(
                task_id="1",
                question="What is 10*5?",
                predicted_answer="The answer is 50",
                ground_truth="50",
                success=True
            ),
            TaskResult(
                task_id="2",
                question="What is pi?",
                predicted_answer="Pi is approximately 3.14159",
                ground_truth="3.14",
                success=True
            )
        ]
        
        evaluation = evaluator.evaluate(results)
        
        # Both should match (50=50, 3.14159≈3.14)
        assert evaluation["average_score"] >= 0.5

    def test_failed_tasks(self):
        """Test handling of failed tasks"""
        evaluator = Evaluator(metric="exact_match")
        
        results = [
            TaskResult(
                task_id="1",
                question="Q1",
                predicted_answer="A1",
                ground_truth="A1",
                success=True
            ),
            TaskResult(
                task_id="2",
                question="Q2",
                predicted_answer="",
                ground_truth="A2",
                success=False,
                error="Timeout"
            )
        ]
        
        evaluation = evaluator.evaluate(results)
        
        assert evaluation["total_tasks"] == 2
        assert evaluation["evaluated_tasks"] == 1
        assert evaluation["average_score"] == 1.0  # Only successful task

    def test_no_ground_truth(self):
        """Test handling tasks without ground truth"""
        evaluator = Evaluator(metric="exact_match")
        
        results = [
            TaskResult(
                task_id="1",
                question="Q1",
                predicted_answer="A1",
                ground_truth=None,
                success=True
            )
        ]
        
        evaluation = evaluator.evaluate(results)
        
        assert evaluation["evaluated_tasks"] == 0


class TestEvaluateResultsFunction:
    """Test evaluate_results convenience function"""

    def test_basic_usage(self):
        """Test basic evaluate_results usage"""
        results = [
            TaskResult(
                task_id="1",
                question="Q",
                predicted_answer="answer",
                ground_truth="answer",
                success=True
            )
        ]
        
        evaluation = evaluate_results(results, metric="exact_match")
        
        assert evaluation["average_score"] == 1.0

    def test_with_custom_metric(self):
        """Test with custom metric"""
        results = [
            TaskResult(
                task_id="1",
                question="Q",
                predicted_answer="hello world",
                ground_truth="hello",
                success=True
            )
        ]
        
        evaluation = evaluate_results(results, metric="contains_answer")
        
        assert evaluation["average_score"] == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
