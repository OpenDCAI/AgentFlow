#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evaluate per-task JSON results (final answer + process score) using an LLM judge.
For BrowseComp-V³: input_dir should contain JSONs produced by run_rollout.py (or tool-based rollout).

Usage:
  python eval_rollout_results.py --input_dir results/gpt-4o --judge_model gpt-4o

Requires: OPENAI_API_KEY (and OPENAI_API_BASE if using a custom endpoint).
"""
import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Tuple

import openai

# 可选加载 .env（包含 OPENAI_API_KEY / OPENAI_API_BASE 等）
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover
    load_dotenv = None

# Use OPENAI_API_KEY and OPENAI_API_BASE from environment (or .env in CWD).


PROMPT_TEMPLATE_OLD = """You are a professional AI evaluation agent. Your task is to evaluate a model’s performance on multi-step reasoning tasks along two dimensions:

1. Correctness of the final answer.
2. Quality of the reasoning process.

You will be given the following input fields:

- Question: {question}

- Ground Truth (Reference Annotation):
  - Gold final answer: {gt_answer}
  - Ground-truth sub-goals: {formatted_sub_goals}
    Each ground-truth sub-goal includes a key_info field (critical facts or intermediate conclusions) that specifies the condition for that sub-goal to be considered achieved.

- Model Prediction:
  - Predicted final answer: {pred_answer}
  - Predicted sub-goals: {formatted_pred_subgoals}

Your evaluation must be based strictly on this provided information. Do not introduce external knowledge beyond what is necessary for consistency checking.

------------------------------------------------------------

EVALUATION RULES
------------------------------------------------------------

I. PROCESS SCORE (Reasoning Process Quality)

1. Ground-truth anchored evaluation:
   - The list of ground-truth sub-goals defines the authoritative set of sub-goals to be evaluated.
   - For each ground-truth sub-goal i, you must determine whether this sub-goal is achieved by searching over ALL predicted sub-goals.
   - The matching between ground-truth sub-goals and predicted sub-goals is content-based (by key_info), not position-based. The order of predicted sub-goals may differ from the ground truth.
   - The number of elements in subgoal_vector and subgoal_details MUST equal the number of ground-truth sub-goals.
   - If there are more predicted sub-goals than ground-truth sub-goals, these extra predicted sub-goals MUST NOT create additional entries in subgoal_vector or subgoal_details. However, you may still use them for anomaly detection (fabrication, contradictions, faulty logic).
2. Scoring each ground-truth sub-goal:
   For each ground-truth sub-goal G_i with its key_info:
   - ACHIEVED (1 point):
     - There exists at least one predicted sub-goal whose content correctly identifies and recovers the key_info of G_i (semantic equivalence is allowed).
     - The information is reasonable, does not involve fabricated facts, and does not conflict with any key_info in the ground truth.
   - NOT_ACHIEVED (0 points), if any of the following holds:
     - No predicted sub-goal correctly captures the key_info of G_i.
     - All candidate predicted sub-goals that mention related content contain clear fabrication or contradict the ground-truth key_info.
     - The prediction effectively omits this sub-goal (i.e., no predicted sub-goal provides the required key_info).
3. Process score calculation:
   - PROCESS_SCORE = (number of ACHIEVED ground-truth sub-goals) / (total number of ground-truth sub-goals).
   - You must also output a subgoal_vector such as [1,0,1,...], where each entry is 1 if the corresponding ground-truth sub-goal is ACHIEVED and 0 otherwise.
   - The length of subgoal_vector MUST equal the total number of ground-truth sub-goals.
   - subgoal_details MUST contain one entry per ground-truth sub-goal, in ground-truth order (index 1..N), describing whether that ground-truth sub-goal is achieved and why.

II. ANSWER CORRECTNESS (Final Answer)

Determine whether the model’s predicted final answer matches the ground-truth final answer:

- CORRECT:
  - The predicted final answer and the ground-truth final answer are equivalent in core meaning.
  - Differences in wording, format, or minor stylistic variations are allowed.

- INCORRECT:
  - The predicted final answer and the ground-truth final answer do not match in core meaning.
  - If multiple possible answers are acceptable according to the ground truth, treat the prediction as CORRECT only if it is semantically compatible with at least one acceptable answer.

III. EXCEPTION / ANOMALY OVERRIDE RULE

This rule is triggered only when the predicted final answer matches the ground-truth final answer.

When the final answer is correct, the system must additionally verify the validity of the reasoning process. The following anomaly rule is critical:

Even if the predicted final answer matches the ground-truth final answer, you MUST mark ANSWER_CORRECTNESS as INCORRECT (answer_correct = false) if any of the following anomaly conditions is detected in the reasoning process (including any predicted sub-goal, even beyond the ground-truth count):

1. Unsupported or Guess-based Answering:
   - The final answer is not derivable from the predicted sub-goals.
   - The predicted sub-goals neither logically support nor jointly entail the final answer, indicating that the answer is likely obtained via guessing, rather than evidence grounded in the annotated sub-goals.

2. Invalid Reasoning Path:
   - The final answer is correct, but the reasoning path formed by the predicted sub-goals is logically invalid, internally inconsistent, or self-contradictory, such that the conclusion cannot be legitimately inferred from the provided sub-goals.

3. Contradiction of key_info:
   - Any predicted sub-goal’s key information directly contradicts the ground-truth key_info for the corresponding sub-goal.

This override ensures that a correct final answer must be supported by a sound, non-fabricated reasoning process.

IV. CONFIDENCE LEVEL

You must output a confidence level describing how reliable your evaluation is, based on clarity and sufficiency of the information given:

- HIGH:
  - Evidence is clear and sufficient; sub-goal alignment and correctness judgments are straightforward.

- MEDIUM:
  - Some minor ambiguity exists (e.g., slightly unclear wording), but you can still make a reasonably stable judgment.

- LOW:
  - The ground truth and/or prediction are highly ambiguous, incomplete, or under-specified, making the evaluation unstable or speculative.

------------------------------------------------------------

OUTPUT SPECIFICATION
------------------------------------------------------------

You MUST output a single JSON object that conforms to the provided JSON schema. Do not include any additional text outside of this JSON object.

The JSON object must include:

- answer_correct (boolean):
  - true if ANSWER_CORRECTNESS is CORRECT and no anomaly override is triggered.
  - false otherwise.

- process_score (number in [0.0, 1.0]):
  - The PROCESS_SCORE value defined above.

- subgoal_vector (array of 0/1 integers):
  - Binary vector where each element corresponds to a ground-truth sub-goal, in order.
  - Length = number of ground-truth sub-goals.

- subgoal_details (array):
  - Each element is an object describing the evaluation of one ground-truth sub-goal.
  - One element per ground-truth sub-goal, with strictly aligned indices.

- anomaly_flag (boolean):
  - true if any anomaly (fabrication, faulty-logic success, contradiction of key_info) is detected.
  - false otherwise.

- anomaly_reason (string):
  - If anomaly_flag is true, concisely describe the anomaly.
  - If anomaly_flag is false, set this to "None".

- confidence (string):
  - One of "HIGH", "MEDIUM", or "LOW".

- judge_reasoning (string):
  - A concise but explicit explanation of why you reached this evaluation, referencing both process and final answer.

Your response must be valid JSON and satisfy the JSON schema given in the response_format configuration.
"""

PROMPT_TEMPLATE = """You are a professional AI evaluation agent. Your task is to evaluate a model’s performance on multi-step reasoning tasks along two dimensions:

1. Correctness of the final answer.
2. Quality of the reasoning process.

You will be given the following input fields:

- Question: {question}

- Ground Truth (Reference Annotation):
  - Gold final answer: {gt_answer}
  - Ground-truth sub-goals: {formatted_sub_goals}
    Each ground-truth sub-goal includes a key_info field (critical facts or intermediate conclusions) that specifies the condition for that sub-goal to be considered achieved.

- Model Prediction:
  - Predicted final answer: {pred_answer}
  - Predicted sub-goals: {formatted_pred_subgoals}

Your evaluation must be based strictly on this provided information. Do not introduce external knowledge beyond what is necessary for consistency checking.

------------------------------------------------------------

EVALUATION RULES
------------------------------------------------------------

EVALUATION PRIORITY:
1. First, evaluate answer_correct based solely on final answer comparison.
2. Second, calculate process_score based on sub-goal achievement.
3. Third, IF AND ONLY IF answer_correct is true, check for obvious anomalies for flagging (this does NOT change answer_correct).

I. ANSWER CORRECTNESS (Final Answer)

Determine whether the model’s predicted final answer matches the ground-truth final answer:

- CORRECT:
  - The predicted final answer and the ground-truth final answer are equivalent in core meaning.
  - Differences in wording, format, or minor stylistic variations are allowed.

- INCORRECT:
  - The predicted final answer and the ground-truth final answer do not match in core meaning.
  - If multiple possible answers are acceptable according to the ground truth, treat the prediction as CORRECT only if it is semantically compatible with at least one acceptable answer.

IMPORTANT: The answer_correct value is determined SOLELY by comparing the predicted final answer with the ground-truth final answer. Anomaly detection (Section III) does NOT affect this value.

II. PROCESS SCORE (Reasoning Process Quality)

1. Ground-truth anchored evaluation:
   - The list of ground-truth sub-goals defines the authoritative set of sub-goals to be evaluated.
   - For each ground-truth sub-goal i, you must determine whether this sub-goal is achieved by searching over ALL predicted sub-goals.
   - The matching between ground-truth sub-goals and predicted sub-goals is content-based (by key_info), not position-based. The order of predicted sub-goals may differ from the ground truth.
   - The number of elements in subgoal_vector and subgoal_details MUST equal the number of ground-truth sub-goals.
   - If there are more predicted sub-goals than ground-truth sub-goals, these extra predicted sub-goals MUST NOT create additional entries in subgoal_vector or subgoal_details. However, you may still use them for anomaly detection (fabrication, contradictions, faulty logic).
2. Scoring each ground-truth sub-goal:
   For each ground-truth sub-goal G_i with its key_info:
   - ACHIEVED (1 point):
     - There exists at least one predicted sub-goal whose content correctly identifies and recovers the key_info of G_i (semantic equivalence is allowed).
     - The information is reasonable, does not involve fabricated facts, and does not conflict with any key_info in the ground truth.
   - NOT_ACHIEVED (0 points), if any of the following holds:
     - No predicted sub-goal correctly captures the key_info of G_i.
     - All candidate predicted sub-goals that mention related content contain clear fabrication or contradict the ground-truth key_info.
     - The prediction effectively omits this sub-goal (i.e., no predicted sub-goal provides the required key_info).
3. Process score calculation:
   - PROCESS_SCORE = (number of ACHIEVED ground-truth sub-goals) / (total number of ground-truth sub-goals).
   - You must also output a subgoal_vector such as [1,0,1,...], where each entry is 1 if the corresponding ground-truth sub-goal is ACHIEVED and 0 otherwise.
   - The length of subgoal_vector MUST equal the total number of ground-truth sub-goals.
   - subgoal_details MUST contain one entry per ground-truth sub-goal, in ground-truth order (index 1..N), describing whether that ground-truth sub-goal is achieved and why.


III. ANOMALY DETECTION RULE (FOR HUMAN REVIEW)

⚠️ TRIGGER CONDITION: This rule applies ONLY when answer_correct is true (i.e., the predicted final answer matches the ground-truth final answer).

⚠️ CRITICAL CLARIFICATION: 
- Anomaly detection is for FLAGGING purposes only.
- anomaly_flag does NOT change the answer_correct value.
- answer_correct reflects only whether the final answer is correct.
- Flagged anomalies indicate cases that may need human review to verify the reasoning quality.

When the final answer is correct, perform a careful check for potential reasoning anomalies. However, you must be CONSERVATIVE and set anomaly_flag to true ONLY when there is CLEAR and UNMISTAKABLE evidence of severe issues.

Flag anomaly_flag as true ONLY in these cases:

1. Explicit Guessing or Unsupported Answering:
   - The prediction explicitly states guessing behavior (phrases like "I guess," "I'll try," "randomly choosing").
   - The final answer has absolutely zero connection to the reasoning provided in sub-goals.
   - There is no plausible logical path from the sub-goals to the answer.
   
   DO NOT flag if: The reasoning is weak but present, or the connection is unclear but possible.

2. Severe Factual Contradiction with Ground Truth:
   - A predicted sub-goal states a fact that directly, unmistakably contradicts a key_info in the ground-truth sub-goals.
   - Example of flaggable contradiction: Predicted says "Event occurred in 1990" but ground-truth key_info clearly states "Event occurred in 2000."
   - This must be a clear factual conflict, not a different interpretation or reasoning approach.
   
   DO NOT flag if: The prediction uses different reasoning, omits information, or has minor inconsistencies.

3. Logically Impossible Reasoning Chain:
   - The sub-goals contain statements that are internally contradictory in a way that makes the reasoning logically impossible.
   - Example: "X > Y and Y > Z, therefore X < Z" (violates transitivity).
   
   DO NOT flag if: The reasoning has gaps, is incomplete, or uses a suboptimal approach.

⚠️ WHEN IN DOUBT, DO NOT FLAG:
- If you are uncertain whether an anomaly exists, set anomaly_flag to false.
- Missing or incomplete reasoning is already captured by process_score.
- Different reasoning approaches are acceptable.
- The bar for flagging should be HIGH - only flag obvious, severe issues.

IV. CONFIDENCE LEVEL

You must output a confidence level describing how reliable your evaluation is, based on clarity and sufficiency of the information given:

- HIGH:
  - Evidence is clear and sufficient; sub-goal alignment and correctness judgments are straightforward.

- MEDIUM:
  - Some minor ambiguity exists (e.g., slightly unclear wording), but you can still make a reasonably stable judgment.

- LOW:
  - The ground truth and/or prediction are highly ambiguous, incomplete, or under-specified, making the evaluation unstable or speculative.

------------------------------------------------------------

OUTPUT SPECIFICATION
------------------------------------------------------------

You MUST output a single JSON object that conforms to the provided JSON schema. Do not include any additional text outside of this JSON object.

The JSON object must include:

- answer_correct (boolean):
  - true if the predicted final answer matches the ground-truth final answer in core meaning.
  - false if the predicted final answer does not match the ground-truth final answer.
  - NOTE: This value is NOT affected by anomaly_flag. It reflects only the final answer comparison.

- process_score (number in [0.0, 1.0]):
  - The PROCESS_SCORE value defined above.

- subgoal_vector (array of 0/1 integers):
  - Binary vector where each element corresponds to a ground-truth sub-goal, in order.
  - Length = number of ground-truth sub-goals.

- subgoal_details (array):
  - Each element is an object describing the evaluation of one ground-truth sub-goal.
  - One element per ground-truth sub-goal, with strictly aligned indices.

- anomaly_flag (boolean):
  - true if any anomaly (fabrication, faulty-logic success, contradiction of key_info) is detected.
  - false otherwise.

- anomaly_reason (string):
  - If anomaly_flag is true, concisely describe the anomaly.
  - If anomaly_flag is false, set this to "None".

- confidence (string):
  - One of "HIGH", "MEDIUM", or "LOW".

- judge_reasoning (string):
  - A concise but explicit explanation of why you reached this evaluation, referencing both process and final answer.

Your response must be valid JSON and satisfy the JSON schema given in the response_format configuration.
"""


RESPONSE_FORMAT_OLD = {
    "type": "json_schema",
    "json_schema": {
        "name": "multistep_reasoning_evaluation",
        "schema": {
            "type": "object",
            "properties": {
                "answer_correct": {
                    "type": "boolean",
                    "description": (
                        "True if the model's final answer is judged CORRECT and no anomaly override is triggered; "
                        "false otherwise."
                    ),
                },
                "process_score": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": (
                        "PROCESS_SCORE = (number of ACHIEVED ground-truth sub-goals) / (total number of ground-truth "
                        "sub-goals), computed after checking each ground-truth sub-goal against all predicted "
                        "sub-goals (order-independent matching)."
                    ),
                },
                "subgoal_vector": {
                    "type": "array",
                    "items": {"type": "integer", "enum": [0, 1]},
                    "description": (
                        "Binary vector for ground-truth sub-goals. Index i corresponds to the i-th ground-truth "
                        "sub-goal. 1 = ACHIEVED (at least one predicted sub-goal correctly recovers its key_info), 0 "
                        "= NOT_ACHIEVED. The length MUST equal the number of ground-truth sub-goals."
                    ),
                },
                "subgoal_details": {
                    "type": "array",
                    "description": (
                        "Detailed evaluation for each ground-truth sub-goal, in ground-truth order. The i-th element "
                        "describes the i-th ground-truth sub-goal. Matching to predicted sub-goals is content-based, "
                        "not position-based. Extra predicted sub-goals beyond the ground-truth count MUST NOT create "
                        "additional entries here."
                    ),
                    "items": {
                        "type": "object",
                        "properties": {
                            "subgoal_index": {
                                "type": "integer",
                                "minimum": 1,
                                "description": (
                                    "1-based index of the ground-truth sub-goal this entry refers to."
                                ),
                            },
                            "status": {
                                "type": "string",
                                "enum": ["ACHIEVED", "NOT_ACHIEVED"],
                                "description": (
                                    "Whether the ground-truth sub-goal is judged ACHIEVED (covered by at least one "
                                    "predicted sub-goal in terms of key_info) or NOT_ACHIEVED."
                                ),
                            },
                            "reason": {
                                "type": "string",
                                "description": (
                                    "One-sentence explanation referencing whether the key_info for this ground-truth "
                                    "sub-goal is correctly covered by any predicted sub-goal, missing, conflicting, or "
                                    "fabricated."
                                ),
                            },
                        },
                        "required": ["subgoal_index", "status", "reason"],
                        "additionalProperties": False,
                    },
                },
                "anomaly_flag": {
                    "type": "boolean",
                    "description": (
                        "True if any anomaly is detected in the reasoning process (fabricated facts, faulty-logic "
                        "success, contradiction of key_info in any predicted sub-goal); false otherwise."
                    ),
                },
                "anomaly_reason": {
                    "type": "string",
                    "description": (
                        "If anomaly_flag is true, briefly describe the anomaly. If false, set to 'None'."
                    ),
                },
                "confidence": {
                    "type": "string",
                    "enum": ["HIGH", "MEDIUM", "LOW"],
                    "description": (
                        "Confidence level of this evaluation, based on clarity and sufficiency of the given Ground "
                        "Truth and Prediction."
                    ),
                },
                "judge_reasoning": {
                    "type": "string",
                    "description": (
                        "A concise but explicit explanation of the evaluation decision, covering both process_score "
                        "and answer_correct, and referencing any anomalies if present."
                    ),
                },
            },
            "required": [
                "answer_correct",
                "process_score",
                "subgoal_vector",
                "subgoal_details",
                "anomaly_flag",
                "anomaly_reason",
                "confidence",
                "judge_reasoning",
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },
}

RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "multistep_reasoning_evaluation",
        "schema": {
            "type": "object",
            "properties": {
                "answer_correct": {
                    "type": "boolean",
                    "description": (
                        "True if the model's final answer is judged CORRECT; "
                        "false otherwise."
                    ),
                },
                "process_score": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": (
                        "PROCESS_SCORE = (number of ACHIEVED ground-truth sub-goals) / (total number of ground-truth "
                        "sub-goals), computed after checking each ground-truth sub-goal against all predicted "
                        "sub-goals (order-independent matching)."
                    ),
                },
                "subgoal_vector": {
                    "type": "array",
                    "items": {"type": "integer", "enum": [0, 1]},
                    "description": (
                        "Binary vector for ground-truth sub-goals. Index i corresponds to the i-th ground-truth "
                        "sub-goal. 1 = ACHIEVED (at least one predicted sub-goal correctly recovers its key_info), 0 "
                        "= NOT_ACHIEVED. The length MUST equal the number of ground-truth sub-goals."
                    ),
                },
                "subgoal_details": {
                    "type": "array",
                    "description": (
                        "Detailed evaluation for each ground-truth sub-goal, in ground-truth order. The i-th element "
                        "describes the i-th ground-truth sub-goal. Matching to predicted sub-goals is content-based, "
                        "not position-based. Extra predicted sub-goals beyond the ground-truth count MUST NOT create "
                        "additional entries here."
                    ),
                    "items": {
                        "type": "object",
                        "properties": {
                            "subgoal_index": {
                                "type": "integer",
                                "minimum": 1,
                                "description": (
                                    "1-based index of the ground-truth sub-goal this entry refers to."
                                ),
                            },
                            "status": {
                                "type": "string",
                                "enum": ["ACHIEVED", "NOT_ACHIEVED"],
                                "description": (
                                    "Whether the ground-truth sub-goal is judged ACHIEVED (covered by at least one "
                                    "predicted sub-goal in terms of key_info) or NOT_ACHIEVED."
                                ),
                            },
                            "reason": {
                                "type": "string",
                                "description": (
                                    "One-sentence explanation referencing whether the key_info for this ground-truth "
                                    "sub-goal is correctly covered by any predicted sub-goal, missing, conflicting, or "
                                    "fabricated."
                                ),
                            },
                        },
                        "required": ["subgoal_index", "status", "reason"],
                        "additionalProperties": False,
                    },
                },
                "anomaly_flag": {
                    "type": "boolean",
                    "description": (
                        "True if any anomaly is detected in the reasoning process (fabricated facts, faulty-logic "
                        "success, contradiction of key_info in any predicted sub-goal); false otherwise."
                    ),
                },
                "anomaly_reason": {
                    "type": "string",
                    "description": (
                        "If anomaly_flag is true, briefly describe the anomaly. If false, set to 'None'."
                    ),
                },
                "confidence": {
                    "type": "string",
                    "enum": ["HIGH", "MEDIUM", "LOW"],
                    "description": (
                        "Confidence level of this evaluation, based on clarity and sufficiency of the given Ground "
                        "Truth and Prediction."
                    ),
                },
                "judge_reasoning": {
                    "type": "string",
                    "description": (
                        "A concise but explicit explanation of the evaluation decision, covering both process_score "
                        "and answer_correct, and referencing any anomalies if present."
                    ),
                },
            },
            "required": [
                "answer_correct",
                "process_score",
                "subgoal_vector",
                "subgoal_details",
                "anomaly_flag",
                "anomaly_reason",
                "confidence",
                "judge_reasoning",
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },
}

def format_subgoals(gt_subgoals: List[Dict[str, Any]]) -> str:
    lines = []
    for sg in gt_subgoals or []:
        sid = sg.get("sg_id")
        desc = sg.get("description", "")
        key_info = sg.get("key_info", "")
        lines.append(f"- SG{sid}: {desc} | key_info: {key_info}")
    return "\n".join(lines) if lines else "无"


def format_pred_subgoals(pred_subgoals: List[str]) -> str:
    if not pred_subgoals:
        return "无"
    return "\n".join(f"- {s}" for s in pred_subgoals)


def qid_sort_key(qid: Any) -> Tuple[int, int, str]:
    if isinstance(qid, int):
        return (0, qid, str(qid))
    if isinstance(qid, str) and qid.isdigit():
        return (0, int(qid), qid)
    return (1, 0, str(qid))


def extract_final_verdict(text: str) -> Dict[str, Any]:
    """
    Parse the model output into the verdict dict.
    Priority:
      1) If already a dict, return it.
      2) Try direct json.loads on the whole string.
      3) Try to parse the last fenced ```json ...``` block.
      4) Try to parse the first {...} block.
    Otherwise return {}.
    """
    if isinstance(text, dict):
        return text

    if not text:
        return {}

    raw = text.strip()

    # 1) 直接整体解析
    try:
        return json.loads(raw)
    except Exception:
        pass

    # 2) fenced ```json ...```（取最后一个）
    fenced = list(
        re.finditer(r"```json\s*(\{.*?\})\s*```", raw, re.DOTALL | re.IGNORECASE)
    )
    for m in reversed(fenced):
        try:
            return json.loads(m.group(1))
        except Exception:
            continue

    # 3) 第一个 {...} 区块
    match = re.search(r"(\{.*\})", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    return {}


def evaluate_one(
    client: openai.OpenAI, judge_model: str, sample: Dict[str, Any]
) -> Dict[str, Any]:
    gt_subgoals = sample.get("ground_truth", {}).get("sub_goals") or []
    pred_subgoals = sample.get("prediction", {}).get("subgoals") or []
    prompt = PROMPT_TEMPLATE.format(
        question=sample.get("item", {}).get("question", ""),
        gt_answer=sample.get("ground_truth", {}).get("final_answer", ""),
        formatted_sub_goals=format_subgoals(gt_subgoals),
        pred_answer=sample.get("prediction", {}).get("final_answer", ""),
        formatted_pred_subgoals=format_pred_subgoals(pred_subgoals),
    )

    try:
        resp = client.responses.create(
            model=judge_model,
            input=[{"role": "user", "content": prompt}],
            response_format=RESPONSE_FORMAT,
        )
        content = resp.output_text
    except TypeError as exc:
        # Fallback for older SDKs where responses.create lacks response_format support.
        if "response_format" not in str(exc):
            raise
        chat_resp = client.chat.completions.create(
            model=judge_model,
            messages=[{"role": "user", "content": prompt}],
            response_format=RESPONSE_FORMAT,
        )
        content = chat_resp.choices[0].message.content or ""

    verdict = extract_final_verdict(content)

    return {
        "q_id": sample.get("execution", {}).get("q_id"),
        "model_name": sample.get("execution", {}).get("model_name"),
        "judge_model_name": judge_model,
        "tags": sample.get("item", {}).get("tags", {}),
        "score": {
            "final": 1.0 if verdict.get("answer_correct") else 0.0,
            "process": float(verdict.get("process_score") or 0.0),
        },
        "metadata": {
            "verdict": verdict,
            "judge_output": content,
        },
    }


def load_samples(input_dir: str) -> List[Dict[str, Any]]:
    """
    递归收集 input_dir 下的所有单任务 JSON（日志），并过滤掉非预期文件。
    """
    samples: List[Dict[str, Any]] = []
    for root, _, files in os.walk(input_dir):
        for fname in files:
            if not fname.endswith(".json"):
                continue
            fp = os.path.join(root, fname)
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and "execution" in data:
                    samples.append(data)
            except Exception as exc:
                print(f"[WARN] Skip {fp}: {exc}")
                continue
    # 按任务 ID 排序，便于浏览
    samples.sort(key=lambda s: qid_sort_key(s.get("execution", {}).get("q_id", "")))
    return samples


def load_existing_eval(
    eval_path: str,
) -> (Dict[str, Dict[str, Any]], List[Dict[str, Any]]):
    """
    读取已存在的 eval jsonl，返回 {qid: record} 与记录列表。
    """
    existing_index: Dict[str, Dict[str, Any]] = {}
    existing_records: List[Dict[str, Any]] = []
    if not os.path.exists(eval_path):
        return existing_index, existing_records
    with open(eval_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                qid = obj.get("q_id")
                if qid:
                    existing_index[qid] = obj
                    existing_records.append(obj)
            except Exception as exc:
                print(f"[WARN] Skip bad line in eval file: {exc}")
                continue
    return existing_index, existing_records


def main():
    parser = argparse.ArgumentParser(
        description="评估结果文件夹中的单任务 JSON，并输出 JSONL。"
    )
    parser.add_argument("--input_dir", required=True, help="包含单任务结果 JSON 的目录")
    parser.add_argument(
        "--judge_model", default="gpt-4o", help="评估用模型名称，默认 gpt-4o"
    )
    parser.add_argument(
        "--output_path",
        default=None,
        help="输出 JSONL 路径（默认: 自动命名为 eval_<model>.jsonl，保存在 input_dir 下）",
    )
    parser.add_argument(
        "--max_workers",
        type=int,
        default=4,
        help="并行评估的线程数（默认: 4）",
    )
    args = parser.parse_args()

    # Load .env from current working directory if present
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        if load_dotenv:
            load_dotenv(env_path)
        else:
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
            except Exception as exc:  # pragma: no cover
                print(f"[WARN] Failed to load .env manually: {exc}")
        print(f"[INFO] Loaded environment from {env_path}")

    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_API_BASE")
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not set. Set it in the environment or in .env", file=sys.stderr)
        sys.exit(1)
    if base_url:
        print(f"[INFO] Using base_url: {base_url}")
    client = openai.OpenAI(api_key=api_key, base_url=base_url) if base_url else openai.OpenAI(api_key=api_key)

    samples = load_samples(args.input_dir)
    total = len(samples)
    if not samples:
        print(f"[INFO] No samples found under {args.input_dir}")
        return

    # 自动推断模型名，用于默认输出文件名
    model_name = next(
        (s.get("execution", {}).get("model_name") for s in samples if s.get("execution", {})),  # type: ignore
        None,
    )
    safe_model = (
        "".join(
            [
                c if c.isalnum() or c in "-_." else "_"
                for c in (model_name or "unknown_model")
            ]
        )
        or "unknown_model"
    )

    output_path = args.output_path
    if output_path is None:
        base_dir = (
            args.input_dir
            if os.path.isdir(args.input_dir)
            else os.path.dirname(args.input_dir) or "."
        )
        output_path = os.path.join(base_dir, f"eval_{safe_model}.jsonl")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # 读取已有评测，构建去重索引
    existing_index, existing_records = load_existing_eval(output_path)

    print(f"[INFO] Loaded {total} samples from {args.input_dir}")
    to_evaluate: List[Dict[str, Any]] = []
    for sample in samples:
        qid = sample.get("execution", {}).get("q_id")
        if qid in existing_index:
            print(f"[INFO] Skip {qid} (already evaluated)")
            continue
        to_evaluate.append(sample)

    new_results: List[Dict[str, Any]] = []
    total_eval = len(to_evaluate)
    if total_eval:
        with open(output_path, "a", encoding="utf-8") as out_f:
            with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
                futures = {
                    executor.submit(evaluate_one, client, args.judge_model, sample): sample
                    for sample in to_evaluate
                }
                completed = 0
                for future in as_completed(futures):
                    sample = futures[future]
                    qid = sample.get("execution", {}).get("q_id")
                    try:
                        result = future.result()
                    except Exception as exc:
                        # 失败时仍落盘，标记 score 为 0
                        print(f"[WARN] Failed on {qid}: {exc}")
                        result = {
                            "q_id": qid,
                            "model_name": sample.get("execution", {}).get("model_name"),
                            "judge_model_name": args.judge_model,
                            "tags": sample.get("item", {}).get("tags", {}),
                            "score": {"final": 0.0, "process": 0.0},
                            "metadata": {"error": str(exc)},
                        }
                    completed += 1
                    print(f"[INFO] Evaluated {completed}/{total_eval} - {qid}")
                    new_results.append(result)
                    out_f.write(json.dumps(result, ensure_ascii=False) + "\n")
                    out_f.flush()

    # 重写 eval 文件：保留原有记录并附加新结果（按 q_id 排序）
    all_records = existing_records + new_results
    all_records.sort(key=lambda r: qid_sort_key(r.get("q_id", "")))
    with open(output_path, "w", encoding="utf-8") as out_f:
        for rec in all_records:
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(
        f"[INFO] Done. Results written to {output_path} (new: {len(new_results)}, total: {len(all_records)})"
    )


if __name__ == "__main__":
    main()
