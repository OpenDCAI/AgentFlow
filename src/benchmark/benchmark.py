"""
Benchmark class for AgentFlow - loads and evaluates benchmark datasets.
"""

import json
import os
from typing import List, Dict, Any, Optional, Union, Callable
from abc import ABC, abstractmethod
import re
import difflib
from dataclasses import dataclass
import openai
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class BenchmarkItem:
    """Represents a single benchmark item with question and answer."""
    id: str
    question: str
    answer: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class EvaluationResult:
    """Represents the result of evaluating a prediction against ground truth."""
    item_id: str
    question: str
    ground_truth: str
    prediction: str
    score: float
    metric_name: str
    details: Optional[Dict[str, Any]] = None


class Benchmark(ABC):
    """
    Abstract base class for benchmark datasets.
    
    This class provides functionality for:
    - Loading benchmark data from JSON/JSONL files
    - Evaluating predictions against ground truth
    - Computing various evaluation metrics
    - Managing benchmark datasets
    """
    
    def __init__(self, 
                 data_path: Optional[str] = None,
                 name: Optional[str] = None,
                 description: Optional[str] = None):
        """
        Initialize the benchmark.
        
        Args:
            data_path: Path to the benchmark data file
            name: Name of the benchmark
            description: Description of the benchmark
        """
        self.name = name or "Unknown Benchmark"
        self.description = description or ""
        self.data_path = data_path
        self.items: List[BenchmarkItem] = []
        self.evaluation_results: List[EvaluationResult] = []
        
        if data_path:
            self.load_data(data_path)
    
    def load_data(self, data_path: str):
        """
        Load benchmark data from a file.
        
        Args:
            data_path: Path to the data file (JSON or JSONL)
        """
        self.data_path = data_path
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Data file not found: {data_path}")
        
        # Determine file format
        if data_path.endswith('.jsonl'):
            self._load_jsonl(data_path)
        elif data_path.endswith('.json'):
            self._load_json(data_path)
        else:
            raise ValueError(f"Unsupported file format: {data_path}")
        
        print(f"Loaded {len(self.items)} items from {data_path}")
    
    def _load_jsonl(self, file_path: str):
        """Load data from JSONL file."""
        self.items = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    item = self._parse_item(data, line_num)
                    self.items.append(item)
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON on line {line_num}: {e}")
                    continue
    
    def _load_json(self, file_path: str):
        """Load data from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.items = []
        
        # Handle different JSON structures
        if isinstance(data, list):
            # List of items
            for i, item_data in enumerate(data):
                item = self._parse_item(item_data, i + 1)
                self.items.append(item)
        elif isinstance(data, dict):
            # Single item or structured data
            if 'items' in data:
                # Structured format with items array
                for i, item_data in enumerate(data['items']):
                    item = self._parse_item(item_data, i + 1)
                    self.items.append(item)
            else:
                # Single item
                item = self._parse_item(data, 1)
                self.items.append(item)
    
    def _parse_item(self, data: Dict[str, Any], line_num: int) -> BenchmarkItem:
        """
        Parse a single item from the data.
        Override this method for custom parsing logic.
        
        Args:
            data: Raw item data
            line_num: Line number for error reporting
            
        Returns:
            Parsed BenchmarkItem
        """
        # Extract required fields
        item_id = data.get('id', f'item_{line_num}')
        question = data.get('question', '')
        answer = data.get('answer', '')
        
        # Extract metadata (all other fields)
        metadata = {k: v for k, v in data.items() 
                   if k not in ['id', 'question', 'answer']}
        
        return BenchmarkItem(
            id=item_id,
            question=question,
            answer=answer,
            metadata=metadata
        )
    
    def get_item(self, item_id: str) -> Optional[BenchmarkItem]:
        """Get a specific item by ID."""
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def get_items(self) -> List[BenchmarkItem]:
        """Get all items."""
        return self.items.copy()
    
    def get_questions(self) -> List[str]:
        """Get all questions."""
        return [item.question for item in self.items]
    
    def get_answers(self) -> List[str]:
        """Get all ground truth answers."""
        return [item.answer for item in self.items]
    
    def evaluate(self, 
                 predictions: Union[Dict[str, str], List[str]], 
                 metric: str = "exact_match",
                 concurrent: bool = True,
                 max_workers: Optional[int] = None,
                 **kwargs) -> List[EvaluationResult]:
        """
        Evaluate predictions against ground truth.
        
        Args:
            predictions: Dict mapping item_id to prediction, or list of predictions in order
            metric: Evaluation metric to use
            **kwargs: Additional arguments for the metric function
            
        Returns:
            List of evaluation results
        """
        if isinstance(predictions, list):
            if len(predictions) != len(self.items):
                raise ValueError(f"Number of predictions ({len(predictions)}) "
                               f"doesn't match number of items ({len(self.items)})")
            pred_dict = {item.id: pred for item, pred in zip(self.items, predictions)}
        else:
            pred_dict = predictions
        
        missing_ids = [item.id for item in self.items if item.id not in pred_dict]
        for missing_id in missing_ids:
            print(f"Warning: No prediction for item {missing_id}")

        items_to_evaluate = [(index, item) for index, item in enumerate(self.items) if item.id in pred_dict]

        def evaluate_single(index_item_pair):
            index, item = index_item_pair
            prediction = pred_dict[item.id]
            score = self._compute_metric(item.answer, prediction, metric, question=item.question, **kwargs)
            result = EvaluationResult(
                item_id=item.id,
                question=item.question,
                ground_truth=item.answer,
                prediction=prediction,
                score=score,
                metric_name=metric,
                details=self._get_metric_details(item.answer, prediction, metric, **kwargs)
            )
            return index, result

        if not concurrent or len(items_to_evaluate) <= 1:
            results = []
            for index_item_pair in tqdm(items_to_evaluate):
                _, result = evaluate_single(index_item_pair)
                results.append(result)
        else:
            results_dict: Dict[int, EvaluationResult] = {}
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_item = {
                    executor.submit(evaluate_single, index_item_pair): index_item_pair[1]
                    for index_item_pair in items_to_evaluate
                }
                for future in tqdm(as_completed(future_to_item), total=len(future_to_item)):
                    item = future_to_item[future]
                    try:
                        index, result = future.result()
                        results_dict[index] = result
                    except Exception as exc:
                        raise RuntimeError(f"Error evaluating item {item.id}") from exc
            results = [results_dict[index] for index, _ in items_to_evaluate]
        
        self.evaluation_results = results
        return results
    
    def _compute_metric(self, 
                       ground_truth: str, 
                       prediction: str, 
                       metric: str, 
                       question: str = None,
                       **kwargs) -> float:
        """Compute a specific metric between ground truth and prediction."""
        metric_func = self._get_metric_function(metric)
        if metric == 'llm_judgement':
            return metric_func(question, ground_truth, prediction, **kwargs)
        else:
            return metric_func(ground_truth, prediction, **kwargs)
    
    def _get_metric_function(self, metric: str) -> Callable:
        """Get the metric function by name."""
        metric_functions = {
            'exact_match': self._exact_match,
            'f1_score': self._f1_score,
            'bleu_score': self._bleu_score,
            'rouge_score': self._rouge_score,
            'similarity': self._similarity,
            'contains_answer': self._contains_answer,
            'numeric_match': self._numeric_match,
            'llm_judgement': self._llm_judgement
        }
        
        if metric not in metric_functions:
            raise ValueError(f"Unknown metric: {metric}. "
                           f"Available metrics: {list(metric_functions.keys())}")
        
        return metric_functions[metric]
    
    def _exact_match(self, ground_truth: str, prediction: str, **kwargs) -> float:
        """Exact string match."""
        return 1.0 if ground_truth.strip() == prediction.strip() else 0.0
    
    def _f1_score(self, ground_truth: str, prediction: str, **kwargs) -> float:
        """F1 score based on word overlap."""
        gt_words = set(ground_truth.lower().split())
        pred_words = set(prediction.lower().split())
        
        if not gt_words and not pred_words:
            return 1.0
        if not gt_words or not pred_words:
            return 0.0
        
        intersection = gt_words & pred_words
        precision = len(intersection) / len(pred_words)
        recall = len(intersection) / len(gt_words)
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * (precision * recall) / (precision + recall)
    
    def _bleu_score(self, ground_truth: str, prediction: str, **kwargs) -> float:
        """Simple BLEU-like score based on n-gram overlap."""
        # Simple implementation - in practice, you'd use a proper BLEU library
        gt_words = ground_truth.lower().split()
        pred_words = prediction.lower().split()
        
        if not gt_words or not pred_words:
            return 0.0
        
        # 1-gram precision
        matches = 0
        for word in pred_words:
            if word in gt_words:
                matches += 1
        
        return matches / len(pred_words)
    
    def _rouge_score(self, ground_truth: str, prediction: str, **kwargs) -> float:
        """Simple ROUGE-like score based on longest common subsequence."""
        # Simple implementation - in practice, you'd use a proper ROUGE library
        gt_words = ground_truth.lower().split()
        pred_words = prediction.lower().split()
        
        if not gt_words or not pred_words:
            return 0.0
        
        # LCS-based ROUGE-L
        lcs_length = self._lcs_length(gt_words, pred_words)
        recall = lcs_length / len(gt_words)
        precision = lcs_length / len(pred_words)
        
        if recall + precision == 0:
            return 0.0
        
        return 2 * (recall * precision) / (recall + precision)
    
    def _lcs_length(self, seq1: List[str], seq2: List[str]) -> int:
        """Compute length of longest common subsequence."""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    def _similarity(self, ground_truth: str, prediction: str, **kwargs) -> float:
        """String similarity using difflib."""
        return difflib.SequenceMatcher(None, ground_truth, prediction).ratio()
    
    def _contains_answer(self, ground_truth: str, prediction: str, **kwargs) -> float:
        """Check if prediction contains the ground truth answer."""
        return 1.0 if ground_truth.strip().lower() in prediction.strip().lower() else 0.0
    
    def _numeric_match(self, ground_truth: str, prediction: str, **kwargs) -> float:
        """Extract and compare numeric values."""
        gt_numbers = self._extract_numbers(ground_truth)
        pred_numbers = self._extract_numbers(prediction)
        
        if not gt_numbers and not pred_numbers:
            return 1.0
        if not gt_numbers or not pred_numbers:
            return 0.0
        
        # Check if any ground truth number appears in prediction
        for gt_num in gt_numbers:
            if any(abs(gt_num - pred_num) < 1e-6 for pred_num in pred_numbers):
                return 1.0
        
        return 0.0

    def _llm_judgement(self, question: str, labeled_answer: str, pred_answer: str, **kwargs) -> float:
        """Use LLM to judge the prediction."""
        # Use LLM to judge the prediction
        PROMPT = f"""You are an evaluation assistant. Please determine if the model output is equivalent to the labeled answer.

Question: {question}

Labeled Answer: {labeled_answer}

Model Output (Last few lines): {pred_answer}

Did the model give an answer equivalent to the labeled answer? Please respond with "Correct" if they are equivalent, or "Incorrect" if they are not equivalent. Do not include any other text.
"""
        os.environ["OPENAI_API_KEY"] = "sk-YJkQxboKmL0IBC1M0zOzZbVaVZifM5QvN4mLAtSLZ1V4yEDX"
        os.environ["OPENAI_API_URL"] = "http://123.129.219.111:3000/v1/"
        client = openai.OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.environ.get("OPENAI_API_URL", os.environ.get("OPENAI_API_BASE", ""))
            )
        
        response = client.chat.completions.create(
            model="gpt-4.1-2025-04-14",
            messages=[{"role": "user", "content": PROMPT}],
            temperature=0.0,
            max_tokens=100,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return response.choices[0].message.content.strip() == "Correct"
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all numbers from text."""
        # Simple regex to find numbers (including decimals)
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        return [float(match) for match in matches if match]
    
    def _get_metric_details(self, 
                           ground_truth: str, 
                           prediction: str, 
                           metric: str, 
                           **kwargs) -> Dict[str, Any]:
        """Get additional details for a metric."""
        details = {}
        
        if metric == "f1_score":
            gt_words = set(ground_truth.lower().split())
            pred_words = set(prediction.lower().split())
            intersection = gt_words & pred_words
            details = {
                "ground_truth_words": len(gt_words),
                "prediction_words": len(pred_words),
                "common_words": len(intersection),
                "common_words_list": list(intersection)
            }
        elif metric == "numeric_match":
            details = {
                "ground_truth_numbers": self._extract_numbers(ground_truth),
                "prediction_numbers": self._extract_numbers(prediction)
            }
        
        return details
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the benchmark."""
        if not self.evaluation_results:
            return {
                "name": self.name,
                "description": self.description,
                "total_items": len(self.items),
                "evaluation_status": "No evaluation performed"
            }
        
        scores = [result.score for result in self.evaluation_results]
        metric_name = self.evaluation_results[0].metric_name if self.evaluation_results else "unknown"
        
        return {
            "name": self.name,
            "description": self.description,
            "total_items": len(self.items),
            "evaluated_items": len(self.evaluation_results),
            "metric": metric_name,
            "average_score": sum(scores) / len(scores) if scores else 0.0,
            "max_score": max(scores) if scores else 0.0,
            "min_score": min(scores) if scores else 0.0,
            "perfect_matches": sum(1 for score in scores if score == 1.0)
        }
    
    def save_results(self, file_path: str):
        """Save evaluation results to a file."""
        results_data = {
            "benchmark_info": {
                "name": self.name,
                "description": self.description,
                "data_path": self.data_path,
                "total_items": len(self.items)
            },
            "evaluation_results": [
                {
                    "item_id": result.item_id,
                    "question": result.question,
                    "ground_truth": result.ground_truth,
                    "prediction": result.prediction,
                    "score": result.score,
                    "metric_name": result.metric_name,
                    "details": result.details
                }
                for result in self.evaluation_results
            ],
            "summary": self.get_summary()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"Evaluation results saved to {file_path}")
    
    def load_results(self, file_path: str):
        """Load evaluation results from a file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            results_data = json.load(f)
        
        # Load evaluation results
        self.evaluation_results = []
        for result_data in results_data.get("evaluation_results", []):
            result = EvaluationResult(
                item_id=result_data["item_id"],
                question=result_data["question"],
                ground_truth=result_data["ground_truth"],
                prediction=result_data["prediction"],
                score=result_data["score"],
                metric_name=result_data["metric_name"],
                details=result_data.get("details")
            )
            self.evaluation_results.append(result)
        
        print(f"Evaluation results loaded from {file_path}")


# Convenience functions for common use cases
def create_benchmark(data_path: str, 
                    name: Optional[str] = None,
                    description: Optional[str] = None) -> Benchmark:
    """Create a benchmark from a data file."""
    return Benchmark(data_path=data_path, name=name, description=description)


# Example usage
if __name__ == "__main__":
    # Example: Load and evaluate a benchmark
    print("Creating benchmark from math demo data...")
    benchmark = create_benchmark(
        data_path="../data/math_demo.jsonl",
        name="Math Demo",
        description="Simple math calculation benchmark"
    )
    
    print(f"Loaded {len(benchmark.items)} items")
    print(f"First item: {benchmark.items[0].question}")
    
    # Example predictions
    predictions = {
        "aaa": "### Calculator Results:\nsqrt(144) + pow(3,4)/6 + sin(pi/6)*10 = 30.5\n"
    }
    
    # Evaluate with different metrics
    print("\nEvaluating with exact match...")
    results = benchmark.evaluate(predictions, metric="exact_match")
    print(f"Exact match score: {results[0].score}")
    
    print("\nEvaluating with F1 score...")
    results = benchmark.evaluate(predictions, metric="f1_score")
    print(f"F1 score: {results[0].score}")
    
    print(f"\nSummary: {benchmark.get_summary()}")
