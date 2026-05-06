"""
QA Synthesizer - generates Q&A pairs from trajectories
"""

import json
import re
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

from .models import Trajectory, SynthesizedQA
from .config import SynthesisConfig
from .utils import chat_completion, create_openai_client, extract_json_object, extract_message_content


class QASynthesizer:
    """Synthesizes Q&A pairs from trajectories"""

    def __init__(self, config: SynthesisConfig):
        """Initialize QA synthesizer"""
        self.config = config

        self.client = create_openai_client(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
        )

    def synthesize_qa(self, trajectory: Trajectory, qa_index: int = 0) -> Optional[SynthesizedQA]:
        """Synthesize Q&A pair from trajectory"""
        print(f"\n🔧 Synthesizing QA pair - Trajectory: {trajectory.trajectory_id}")

        traj_description = self._format_trajectory(trajectory)
        max_attempts = 3
        last_failure_reason = ""

        for attempt in range(1, max_attempts + 1):
            prompt = self._build_prompt(trajectory, traj_description, last_failure_reason)
            request_kwargs = {
                "model": self.config.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7 + 0.1 * (attempt - 1),
                "response_format": {"type": "json_object"},
            }

            try:
                response = chat_completion(
                    self.client,
                    **request_kwargs
                )
            except Exception as e:
                if not self._is_json_mode_unsupported_error(e):
                    last_failure_reason = f"Synthesis exception: {str(e)}"
                    continue

                fallback_kwargs = dict(request_kwargs)
                fallback_kwargs.pop("response_format", None)
                try:
                    response = chat_completion(self.client, **fallback_kwargs)
                except Exception as fallback_error:
                    last_failure_reason = f"Synthesis exception: {str(fallback_error)}"
                    continue

            try:
                result = json.loads(extract_json_object(extract_message_content(response)))
            except Exception as e:
                last_failure_reason = f"Synthesis exception: {str(e)}"
                continue

            qa_obj, failure_reason = self._build_qa_from_result(result, trajectory, qa_index, attempt)
            if failure_reason or qa_obj is None:
                last_failure_reason = failure_reason or "Unknown validation failure."
                continue

            print(f"  ✓ Successfully synthesized QA pair")
            print(f"    QA ID: {qa_obj.qa_id}")
            print(f"    Question: {qa_obj.question}...")
            print(f"    Answer: {qa_obj.answer}...")
            return qa_obj

        print(f"  ✗ Synthesis failed after {max_attempts} attempts. Last reason: {last_failure_reason}")
        return None

    def _is_json_mode_unsupported_error(self, error: Exception) -> bool:
        """Detect provider/model errors for unsupported JSON mode calls."""
        error_payload = getattr(error, "body", {}) or {}
        error_info = error_payload.get("error", {}) if isinstance(error_payload, dict) else {}
        message = str(error_info.get("message") or error or "").lower()
        error_type = str(error_info.get("type") or "").lower()
        error_code = str(error_info.get("code") or "").lower()

        if any(token in value for value in (error_type, error_code) for token in ("rate_limit", "too_many_requests")):
            return False
        if not any(token in message for token in ("json mode", "json_object", "response_format")):
            return False
        if not any(token in message for token in ("not supported", "unsupported", "does not support")):
            return False
        if error_type and error_type not in ("invalid_request_error", "bad_request_error"):
            return error_code in ("unsupported_parameter", "unsupported_feature")
        return True

    def _build_qa_from_result(self,
                             result: Dict[str, Any],
                             trajectory: Trajectory,
                             qa_index: int,
                             attempt: int) -> Tuple[Optional[SynthesizedQA], Optional[str]]:
        """Validate response and build QA object"""
        if not isinstance(result, dict):
            return None, "Invalid response format."

        question = str(result.get("question", "")).strip()
        answer = str(result.get("answer", "")).strip()
        reasoning_steps = result.get("reasoning_steps", [])
        if not isinstance(reasoning_steps, list):
            reasoning_steps = []

        if not question or not answer:
            return None, "Empty question or answer."

        if self._answer_leaks_into_question(question, answer):
            return None, "Answer leakage: answer appears in question."

        if self._question_too_verbose(question):
            return None, "Question too verbose."

        if len(reasoning_steps) < 3:
            return None, "Missing/too-short reasoning_steps. Provide >=3 steps."

        qa_id = f"{trajectory.trajectory_id}_qa_{qa_index}"
        qa = SynthesizedQA(
            question=question,
            answer=answer,
            trajectory_id=trajectory.trajectory_id,
            source_id=trajectory.source_id,
            qa_id=qa_id,
            reasoning_steps=reasoning_steps,
            metadata={
                "seed_data": trajectory.seed_data,
                "seed_description": self.config.seed_description,
                "trajectory_depth": trajectory.total_depth,
                "synthesis_date": datetime.now().isoformat()
            }
        )
        return qa, None

    def _normalize_text(self, text: str) -> str:
        """Normalize text for containment checks"""
        t = str(text or "").strip().lower()
        t = re.sub(r"\s+", " ", t)
        return t

    def _answer_leaks_into_question(self, question: str, answer: str) -> bool:
        """Check if answer appears in question"""
        q = self._normalize_text(question)
        a = self._normalize_text(answer)
        if not q or not a:
            return False
        return a in q

    def _question_too_verbose(self, question: str, max_words: int = 85, max_chars: int = 500) -> bool:
        """Check if question is too verbose"""
        q = str(question or "").strip()
        if len(q) > max_chars:
            return True
        words = re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?", q)
        return len(words) > max_words

    def _build_prompt(self, trajectory: Trajectory, traj_description: str, last_failure_reason: str) -> str:
        """Build QA synthesis prompt"""
        prompt = f"""You are a data synthesis expert. Based on the following Agent's exploration trajectory, synthesize a high-quality Q&A pair.

【Starting Point Information】
Content: {trajectory.seed_data}"""

        if self.config.seed_description:
            prompt += f"\nDescription: {self.config.seed_description}"

        prompt += f"""

【Complete Exploration Trajectory】
{traj_description}

"""

        if self.config.synthesis_tips:
            prompt += f"""Data Synthesis Guidance:\n{self.config.synthesis_tips}\n\n"""

        if self.config.qa_examples:
            prompt += """Refer to the style and quality of the following examples:\n\n"""
            for i, example in enumerate(self.config.qa_examples, 1):
                prompt += f"""Example {i}:
Question: {example.get('question', '')}
Answer: {example.get('answer', '')}

"""

        prompt += """
Please synthesize a high-quality Q&A pair based on the trajectory:

## Question Requirements:
- The target answer must be a specific fact (name, date, location, count, yes/no).
- **DO NOT** ask "How", "Why", or "Describe" questions requiring long explanations.
- **Anti-shortcut**: Question MUST NOT contain the answer text.
- **Low-entrance, deep-reasoning**: Keep question to <=2 sentences; depth from multi-hop dependency chain.
- **Deep multi-hop (required)**: Question must require >=3 dependent hops to solve.
- Question should be natural and self-contained (don't mention "agent", "trajectory", "search results").

## Answer Requirements:
- **Extreme Brevity**: Answer MUST be <=1 sentence, ideally just a short phrase.
- **No Fluff**: No filler words like "According to..." or "The answer is...".
- **Groundedness**: Must be strictly derived from trajectory observations.


Return JSON EXACTLY in this schema:
{
  "question": "question text",
  "answer": "short phrase or single sentence",
  "reasoning_steps": [
    {"hop": 1, "fact": "intermediate fact", "evidence": "supporting snippet", "output": "intermediate entity"},
    {"hop": 2, "fact": "intermediate fact", "evidence": "supporting snippet", "output": "intermediate entity"},
    ...
    {"hop": n, "fact": "final derivation", "evidence": "supporting snippet", "output": "answer"}
  ]
}
"""

        if last_failure_reason:
            prompt += f"""

[Regeneration Required - Previous Output Rejected]
Reason: {last_failure_reason}
You MUST regenerate a NEW question/answer that fully satisfies the guidance.
"""

        return prompt

    def _format_trajectory(self, trajectory: Trajectory) -> str:
        """Format trajectory into readable text"""
        formatted = ""

        for i, node in enumerate(trajectory.nodes, 1):
            formatted += f"\nStep {i}:\n"
            formatted += f"  Intent: {node.intent}\n"

            if node.action:
                formatted += f"  Action: {node.action.get('tool_name', 'unknown')}\n"
                formatted += f"  Parameters: {json.dumps(node.action.get('parameters', {}), ensure_ascii=False)}\n"

            tool_name = ""
            try:
                tool_name = str(node.action.get("tool_name", "")) if node.action else ""
            except Exception:
                tool_name = ""

            max_chars = 800
            if tool_name == "write_distractor_docs":
                max_chars = 2200
            elif tool_name == "query_knowledge_base_dense":
                max_chars = 1600

            obs = str(node.observation or "")
            obs_preview = obs[:max_chars] + "..." if len(obs) > max_chars else obs
            formatted += f"  Observation: {obs_preview}\n"

        return formatted
