"""
Evaluator - evaluates agent predictions against ground truth

Supports multiple metrics: exact_match, f1_score, contains_answer, etc.
"""

import re
import json
from typing import Dict, List, Any, Optional, Callable
from collections import Counter

from .models import TaskResult, EvaluationResult
from .utils import normalize_answer, create_openai_client, chat_completion


class Evaluator:
    """
    Evaluates agent predictions using various metrics.
    
    Supported metrics:
    - exact_match: Exact string match (after normalization)
    - f1_score: Token-level F1 score
    - contains_answer: Check if prediction contains ground truth
    - numeric_match: Compare numeric values
    - similarity: Semantic similarity (requires embedding model)
    - llm_judgement: Use LLM to judge correctness
    """

    def __init__(
        self,
        metric: str = "exact_match",
        model_name: str = "gpt-4.1-2025-04-14",
        api_key: str = "",
        base_url: str = "",
        temperature: float = 0.0,
        max_retries: int = 3,
        extra_params: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize evaluator.
        
        Args:
            metric: Evaluation metric to use
            model_name: Model for LLM-based evaluation
            api_key: API key from rollout config
            base_url: API base URL from rollout config
            temperature: Sampling temperature for llm_judgement
            max_retries: Retry attempts for llm_judgement
            extra_params: Extra completion params for llm_judgement
        """
        self.metric = metric
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.temperature = temperature
        self.max_retries = max_retries
        self.extra_params = extra_params or {}
        self._client = None  # Lazy initialization for LLM metrics

    def evaluate(self, results: List[TaskResult]) -> Dict[str, Any]:
        """
        Evaluate all results.
        
        Args:
            results: List of task results
            
        Returns:
            Evaluation summary with scores and details
        """
        evaluations = []
        scores = []
        
        for result in results:
            if not result.success:
                # Failed tasks get score 0
                eval_result = EvaluationResult(
                    task_id=result.task_id,
                    predicted=result.predicted_answer,
                    ground_truth=result.ground_truth or "",
                    score=0.0,
                    metric=self.metric,
                    details={"error": result.error}
                )
            elif result.ground_truth is None:
                # No ground truth available
                eval_result = EvaluationResult(
                    task_id=result.task_id,
                    predicted=result.predicted_answer,
                    ground_truth="",
                    score=0.0,
                    metric=self.metric,
                    details={"note": "No ground truth available"}
                )
            else:
                # Evaluate prediction
                score, details = self._evaluate_single(
                    result.predicted_answer,
                    result.ground_truth
                )
                eval_result = EvaluationResult(
                    task_id=result.task_id,
                    predicted=result.predicted_answer,
                    ground_truth=result.ground_truth,
                    score=score,
                    metric=self.metric,
                    details=details
                )
                scores.append(score)
            
            evaluations.append(eval_result)
        
        # Calculate summary statistics
        avg_score = sum(scores) / len(scores) if scores else 0.0
        perfect_matches = sum(1 for s in scores if s >= 0.99)
        
        return {
            "metric": self.metric,
            "total_tasks": len(results),
            "evaluated_tasks": len(scores),
            "average_score": avg_score,
            "perfect_matches": perfect_matches,
            "success_rate": len(scores) / len(results) if results else 0.0,
            "evaluations": [e.to_dict() for e in evaluations]
        }

    def _evaluate_single(self, predicted: str, ground_truth: str) -> tuple:
        """
        Evaluate single prediction.
        
        Returns:
            (score, details_dict)
        """
        metric_fn = self._get_metric_fn()
        return metric_fn(predicted, ground_truth)

    def _get_metric_fn(self) -> Callable:
        """Get the metric function based on config"""
        metrics = {
            "exact_match": self._exact_match,
            "f1_score": self._f1_score,
            "contains_answer": self._contains_answer,
            "numeric_match": self._numeric_match,
            "similarity": self._similarity,
            "llm_judgement": self._llm_judgement,
        }
        
        if self.metric not in metrics:
            raise ValueError(f"Unknown metric: {self.metric}")
        
        return metrics[self.metric]

    def _exact_match(self, predicted: str, ground_truth: str) -> tuple:
        """Exact match after normalization"""
        pred_norm = normalize_answer(predicted)
        gt_norm = normalize_answer(ground_truth)
        
        match = pred_norm == gt_norm
        score = 1.0 if match else 0.0
        
        return score, {
            "normalized_predicted": pred_norm,
            "normalized_ground_truth": gt_norm,
            "match": match
        }

    def _f1_score(self, predicted: str, ground_truth: str) -> tuple:
        """Token-level F1 score"""
        pred_tokens = normalize_answer(predicted).split()
        gt_tokens = normalize_answer(ground_truth).split()
        
        if not pred_tokens or not gt_tokens:
            return 0.0, {"precision": 0.0, "recall": 0.0, "f1": 0.0}
        
        pred_counter = Counter(pred_tokens)
        gt_counter = Counter(gt_tokens)
        
        # Count common tokens
        common = sum((pred_counter & gt_counter).values())
        
        precision = common / len(pred_tokens) if pred_tokens else 0.0
        recall = common / len(gt_tokens) if gt_tokens else 0.0
        
        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * precision * recall / (precision + recall)
        
        return f1, {"precision": precision, "recall": recall, "f1": f1}

    def _contains_answer(self, predicted: str, ground_truth: str) -> tuple:
        """Check if prediction contains ground truth"""
        pred_norm = normalize_answer(predicted)
        gt_norm = normalize_answer(ground_truth)
        
        contains = gt_norm in pred_norm
        score = 1.0 if contains else 0.0
        
        return score, {"contains": contains}

    def _numeric_match(self, predicted: str, ground_truth: str) -> tuple:
        """Compare numeric values with tolerance"""
        def extract_numbers(text: str) -> List[float]:
            numbers = re.findall(r'-?\d+\.?\d*', text)
            return [float(n) for n in numbers]
        
        pred_nums = extract_numbers(predicted)
        gt_nums = extract_numbers(ground_truth)
        
        if not pred_nums or not gt_nums:
            return 0.0, {"pred_numbers": pred_nums, "gt_numbers": gt_nums}
        
        # Check if any predicted number matches any ground truth number
        tolerance = 1e-6
        for p in pred_nums:
            for g in gt_nums:
                if abs(p - g) <= tolerance or (g != 0 and abs((p - g) / g) <= 0.01):
                    return 1.0, {
                        "matched_pred": p,
                        "matched_gt": g,
                        "pred_numbers": pred_nums,
                        "gt_numbers": gt_nums
                    }
        
        return 0.0, {"pred_numbers": pred_nums, "gt_numbers": gt_nums}

    def _similarity(self, predicted: str, ground_truth: str) -> tuple:
        """Semantic similarity using embeddings"""
        # Simple character-level similarity as fallback
        # In production, use embedding-based similarity
        pred_set = set(normalize_answer(predicted).lower())
        gt_set = set(normalize_answer(ground_truth).lower())
        
        if not pred_set or not gt_set:
            return 0.0, {}
        
        intersection = len(pred_set & gt_set)
        union = len(pred_set | gt_set)
        jaccard = intersection / union if union > 0 else 0.0
        
        return jaccard, {"jaccard_similarity": jaccard}

    def _llm_judgement(self, predicted: str, ground_truth: str) -> tuple:
        """Use LLM to judge correctness"""
        if self._client is None:
            self._client = create_openai_client(api_key=self.api_key, base_url=self.base_url)
        
        prompt = f"""You are an expert evaluator. Judge if the predicted answer is correct based on the ground truth.

Ground Truth Answer: {ground_truth}
Predicted Answer: {predicted}

Consider the following:
1. The predicted answer may be phrased differently but still be correct
2. Minor differences in formatting or punctuation should not affect correctness
3. The core information must match

Respond with ONLY a JSON object:
{{"correct": true/false, "reasoning": "brief explanation"}}
"""
        
        try:
            response = chat_completion(
                self._client,
                max_retries=self.max_retries,
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                **self.extra_params,
            )
            
            content = response.choices[0].message.content
            
            # Parse response
            try:
                result = json.loads(content)
                correct = result.get("correct", False)
                reasoning = result.get("reasoning", "")
            except json.JSONDecodeError:
                # Try to extract from text
                correct = "true" in content.lower() and "false" not in content.lower()
                reasoning = content
            
            score = 1.0 if correct else 0.0
            return score, {"correct": correct, "reasoning": reasoning}
            
        except Exception as e:
            return 0.0, {"error": str(e)}


def evaluate_results(
    results: List[TaskResult],
    metric: str = "exact_match",
    model_name: str = "gpt-4.1-2025-04-14",
    api_key: str = "",
    base_url: str = "",
    temperature: float = 0.0,
    max_retries: int = 3,
    extra_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convenience function to evaluate results.
    
    Args:
        results: List of task results
        metric: Evaluation metric
        model_name: Model for LLM-based evaluation
        api_key: API key from rollout config
        base_url: API base URL from rollout config
        temperature: Sampling temperature for llm_judgement
        max_retries: Retry attempts for llm_judgement
        extra_params: Extra completion params for llm_judgement
        
    Returns:
        Evaluation summary
    """
    evaluator = Evaluator(
        metric=metric,
        model_name=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        max_retries=max_retries,
        extra_params=extra_params,
    )
    return evaluator.evaluate(results)
