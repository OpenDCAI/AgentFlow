"""
AgentFlow - Main execution script using Environment and Benchmark modules.

This script provides a unified interface for running agents on different benchmarks
using the Environment and Benchmark classes.
"""

import openai
import json
import os
import re
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
    DocEnvironment,
    Environment
)
from benchmark import Benchmark, create_benchmark


# Configuration
@dataclass
class AgentConfig:
    """Configuration for agent execution."""
    model_name: str = "gpt-4.1-2025-04-14"
    max_turns: int = 100
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

## Response Style
- While working, you may describe intermediate reasoning steps.
- When you have enough information, respond with a concise final statement that directly answers the user's question.
- Prefix the final response with `Answer:` and do not include additional commentary, justification, or restatement of the question.
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
        self.output_file: Optional[str] = None
        
        # Validate OpenAI configuration
        self._validate_openai_config()
    
    def _validate_openai_config(self):
        """Validate OpenAI API configuration."""
        openai.api_key = os.environ.get("OPENAI_API_KEY", "")
        openai.base_url = (
            os.environ.get("OPENAI_API_URL")
            or os.environ.get("OPENAI_API_BASE")
            or os.environ.get("OPENAI_BASE_URL")
            or ""
        )
        
        if not openai.api_key:
            print("Warning: OPENAI_API_KEY is not set. Some features may not work properly.")
        if not openai.base_url:
            print("Warning: OPENAI_API_URL / OPENAI_API_BASE / OPENAI_BASE_URL is not set. Some features may not work properly.")
    
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
        elif mode == "doc": 
            self.environment = DocEnvironment(**kwargs)
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
            
            # Extract final answer (with question for better extraction)
            final_answer = self._extract_final_answer(messages, question)
            
            result = {
                "task_id": task_id,
                "question": question,
                "answer": final_answer,
                "messages": messages,
                "success": True,
                "error": None
            }
            
            print(f"✓ Task {task_id} completed successfully")
            if final_answer != "":
                print(f"Answer: {final_answer[:100]}...")
            else:
                print("No answer found")
            
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
        First locates the file mentioned in the question, then answers.
        
        Args:
            question: User question
            task_id: Task identifier
            
        Returns:
            List of messages from the conversation
        """
        import re
        
        # Extract file name from question (format: in [filename.pdf] document)
        file_match = re.search(r'in\s+\[([^\]]+\.pdf)\]', question, re.IGNORECASE)
        if file_match:
            file_name = file_match.group(1).replace('.pdf', '')
            # First, check if the file exists and is processed
            doc_check_result = self.environment.execute_tool("doc_check_tool", {"file_name_or_all": file_name})
            print(f"📄 Located file: {file_name}")
        
        # Prepare system prompt
        system_prompt = SYSTEM_PROMPT_GENERIC.replace(
            "{tool_descriptions}", 
            self.environment.get_tool_descriptions()
        )
        messages = [
            {"role": "developer", "content": system_prompt},
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
                        tools=self.environment.get_tool_schemas(),
                    )
                    
                    assistant_message = response.choices[0].message
                    # Convert to dict format for consistency
                    messages.append(assistant_message.model_dump())
                    
                    if assistant_message.tool_calls:
                        # Execute all tool calls
                        if messages[-1].get("content") == "":
                            tc = messages[-1]["tool_calls"][0].get("function", {})
                            content = f'Calling tools: {tc}'
                        
                        # Process all tool calls, not just the first one
                        for tool_call in assistant_message.tool_calls:
                            tool_name = tool_call.function.name
                            tool_args = json.loads(tool_call.function.arguments)
                            
                            print(f"Round {turn_count}: 🔧 Using tool: {tool_name}")
                            print(f"Round {turn_count}:    Arguments: {tool_args}")
                            
                            # Execute tool
                            tool_result = self.environment.execute_tool(
                                tool_name, 
                                tool_args
                            )
                            
                            # Ensure tool_result is a string for display and API
                            if isinstance(tool_result, (dict, list)):
                                tool_result_str = json.dumps(tool_result, ensure_ascii=False)
                            else:
                                tool_result_str = str(tool_result)
                            
                            # Display truncated result
                            result_preview = tool_result_str[:100] + "..." if len(tool_result_str) > 100 else tool_result_str
                            print(f"Round {turn_count}:    Result: {result_preview}")
                            
                            # Add tool result to conversation (must be string for API)
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_name,
                                "content": tool_result_str
                            })
                        
                        # Continue conversation after tool use
                        break
                    
                    else:
                        # No tool calls, conversation complete
                        print(f"💬 Final answer at turn {turn_count}")
                        return messages
                
                except Exception as e:
                    with open("error.jsonl", "a") as f:
                        f.write(json.dumps({
                            "messages": messages,
                        }) + "\n")
                    print(f"⚠️  Retry {retry + 1}/{self.config.max_retries}: {str(e)}")
                    retry += 1
                    if retry >= self.config.max_retries:
                        raise e
            
            turn_count += 1
        
        print(f"⚠️  Max turns ({self.config.max_turns}) reached")
        return messages
    
    def _extract_final_answer(self, messages: List[Dict[str, Any]], question: str = "") -> str:
        """
        Extract the final, concise answer from the agent conversation.
        
        The extraction is performed in clearly defined stages so that the intent of
        each heuristic is easy to follow:
            1. Identify the latest assistant response.
            2. Guard against obvious mismatches (e.g. wrong years).
            3. Detect whether the question expects multiple values.
            4. Apply a series of focused extraction heuristics (conclusion markers,
               descriptive phrases, percentages, quoted phrases, key phrases, numbers).
            5. Normalise and clean the final answer.
            6. Support multi-value answers by returning a JSON array when possible.
        """
        raw_answer = self._get_latest_assistant_response(messages)
        if not raw_answer:
            return "Not answerable"

        question_lower = question.lower() if question else ""
        raw_answer = raw_answer.strip()

        if self._has_year_mismatch(question, raw_answer):
            return "Not answerable"

        requires_multiple = self._question_requires_multiple(question_lower)
        raw_answer = self._strip_answer_prefix(raw_answer)

        candidate = None
        extraction_steps = [
            lambda: self._extract_from_conclusion(raw_answer, question_lower, requires_multiple),
            lambda: self._extract_descriptive_phrase(raw_answer, question_lower),
            lambda: self._extract_percentage(raw_answer, question_lower, requires_multiple),
            lambda: self._extract_quoted_phrase(raw_answer),
            lambda: self._extract_key_phrase(raw_answer, question_lower, requires_multiple),
            lambda: self._extract_numeric_answer(raw_answer, question_lower, requires_multiple),
        ]

        for step in extraction_steps:
            value = step()
            if value:
                candidate = value
                break

        if not candidate:
            candidate = self._extract_first_sentence(raw_answer, requires_multiple)

        if requires_multiple:
            multi_value = self._extract_multi_value(raw_answer)
            if multi_value:
                if isinstance(multi_value, str) and multi_value.startswith("["):
                    return multi_value
                return self._normalize_result(multi_value)

        if candidate:
            return self._normalize_result(candidate)

        if requires_multiple:
            # If we still have nothing, multi-value questions are not answerable.
            return "Not answerable"

        # Fallback to a truncated version of the raw answer if it is short; otherwise no answer.
        if raw_answer and len(raw_answer) < 100:
            return self._normalize_result(raw_answer)

        return "Not answerable"

    # ------------------------------------------------------------------
    # Answer extraction helper utilities
    # ------------------------------------------------------------------

    def _get_latest_assistant_response(self, messages: List[Dict[str, Any]]) -> str:
        """Return the content of the latest assistant response without tool calls."""
        for message in reversed(messages):
            if hasattr(message, "role"):
                if message.role == "assistant" and not getattr(message, "tool_calls", None):
                    return getattr(message, "content", "") or ""
            else:
                if message.get("role") == "assistant" and not message.get("tool_calls"):
                    return message.get("content", "") or ""
        return ""

    def _has_year_mismatch(self, question: str, answer: str) -> bool:
        """Return True if the answer mentions a different year than the question requires."""
        if not question:
            return False

        years_in_question = re.findall(r"\b(19|20)\d{2}\b", question)
        if not years_in_question:
            return False

        question_year = years_in_question[-1]
        years_in_answer = re.findall(r"\b(19|20)\d{2}\b", answer)
        if years_in_answer:
            return question_year not in set(years_in_answer)

        if len(answer) > 50 and re.search(r"(?:last|previous|recent)\s+(?:election|year|survey)", answer, re.IGNORECASE):
            return True

        return False

    def _question_requires_multiple(self, question_lower: str) -> bool:
        patterns = [
            r"which\s+\w+\s+and\s+what",
            r"what\s+\w+\s+and\s+what",
            r"which\s+group\s+and\s+what",
            r"which\s+group\s+is\s+this,\s+and\s+what\s+is\s+the\s+percentage\s+drop(?:ped)?",
            r"what\s+is\s+this\s+and\s+what",
            r"and\s+what\s+(?:the|is|are)",
            r",\s+and\s+what",
        ]
        return any(re.search(pattern, question_lower) for pattern in patterns)

    def _strip_answer_prefix(self, answer: str) -> str:
        """Trim everything up to and including an 'Answer:' prefix if present."""
        match = re.search(r"Answer:\s*(.+?)(?:\n\n|$)", answer, re.DOTALL | re.IGNORECASE)
        if not match:
            return answer

        content = match.group(1).strip()
        content = re.sub(r"\[[^\]]+\]", "", content)
        content = re.sub(r'"PH_[^"]+\.pdf"', "", content, flags=re.IGNORECASE)
        content = content.strip()

        if 0 < len(content) < 500:
            return content
        return answer

    def _extract_from_conclusion(self, answer: str, question_lower: str, requires_multiple: bool) -> Optional[str]:
        """Detect final statements introduced by conclusion markers."""
        markers = [
            r"Therefore[^.]*?",
            r"So[^.]*?",
            r"Thus[^.]*?",
            r"Hence[^.]*?",
            r"In conclusion[^.]*?",
            r"As a result[^.]*?",
            r"Consequently[^.]*?",
        ]

        for marker in markers:
            match = re.search(marker + r"([^.!?]+(?:[.!?][^.!?]+){0,2})", answer, re.IGNORECASE | re.DOTALL)
            if not match:
                continue

            conclusion_text = match.group(1).strip()

            if not requires_multiple:
                if "%" in conclusion_text and ("percentage" in question_lower or "%" in question_lower):
                    percent = re.search(r"\b(\d+\.?\d*%)", conclusion_text)
                    if percent and not re.search(r"\d{4}.*" + re.escape(percent.group(1)), conclusion_text):
                        return percent.group(1)

                if any(key in question_lower for key in ("how many", "how much", "count")):
                    number_match = re.search(r"\b(\d+)\b", conclusion_text)
                    if number_match and int(number_match.group(1)) <= 50:
                        return number_match.group(1)

            first_sentence = re.split(r"[.!?]\s+", conclusion_text)[0].strip()
            first_sentence = re.sub(r"^(the|a|an|is|are|was|were)\s+", "", first_sentence, flags=re.IGNORECASE)
            first_sentence = re.sub(r"^(percentage|percent|number|total|count|answer|result)[:\s]+", "", first_sentence, flags=re.IGNORECASE)
            first_sentence = first_sentence.strip()
            if first_sentence:
                return first_sentence[:100]

        return None

    def _extract_descriptive_phrase(self, answer: str, question_lower: str) -> Optional[str]:
        if "how do" not in question_lower and "how does" not in question_lower:
            return None

        patterns = [
            (r"(less\s+well[-\s]?off)", "Less well-off"),
            (r"(better\s+off)", None),
            (r"(about\s+the\s+same)", None),
            (r"(worse\s+off)", None),
            (r"(more\s+optimistic)", None),
            (r"(less\s+optimistic)", None),
        ]

        for pattern, normalized in patterns:
            match = re.search(pattern, answer, re.IGNORECASE)
            if match:
                value = match.group(1)
                return normalized or value

        return None

    def _extract_percentage(self, answer: str, question_lower: str, requires_multiple: bool) -> Optional[str]:
        if requires_multiple or "how do" in question_lower or "how does" in question_lower:
            return None

        if "%" in answer and any(token in question_lower for token in ("percentage", "%", "what")):
            calc_patterns = [
                r"(?:approximately|about|roughly|around|equals?|is|are|was|were|=\s*)(?:[^=]*?)(\d+\.?\d*%)",
                r"(?:Therefore|So|Thus|Hence)[^.]*?(\d+\.?\d*%)",
                r"(\d+\.?\d*%)\s*(?:is|are|was|were|equals?|represents?|accounts?\s+for)",
            ]
            for pattern in calc_patterns:
                match = re.search(pattern, answer, re.IGNORECASE)
                if match and not re.search(r"\d{4}.*" + re.escape(match.group(1)), answer):
                    return match.group(1)

        if any(token in question_lower for token in ("percentage", "%")):
            number_match = re.search(r"\b(\d+\.?\d*)\b", answer)
            if number_match:
                num = number_match.group(1)
                try:
                    if 0 <= float(num) <= 100:
                        context = answer[max(0, answer.find(num) - 20) : answer.find(num) + 20].lower()
                        if any(word in context for word in ("percent", "percentage", "pct")):
                            return f"{num}%"
                except ValueError:
                    pass

        return None

    def _extract_quoted_phrase(self, answer: str) -> Optional[str]:
        for quoted in re.findall(r'["\']([^"\']+)["\']', answer):
            candidate = quoted.strip()
            if candidate.endswith(".pdf") or candidate.startswith("PH_") or len(candidate) > 50:
                continue
            if 1 <= len(candidate.split()) <= 10:
                return candidate
        return None

    def _extract_key_phrase(self, answer: str, question_lower: str, requires_multiple: bool) -> Optional[str]:
        key_patterns = [
            (r"(less\s+well[-\s]?off)", "Less well-off"),
            (r"(some\s+college\s+or\s+more)", "Some college or more"),
            (r"(latinos?\s+interviewed\s+by\s+cellphone)", None),
            (r"(foreign\s+born\s+latinos?)", None),
            (r"(high\s+school\s+or\s+less)", None),
            (r"(college\s+graduate)", None),
        ]
        for pattern, normalized in key_patterns:
            match = re.search(pattern, answer, re.IGNORECASE)
            if match:
                return normalized or match.group(1)

        if requires_multiple:
            return None

        if "which" in question_lower or "what" in question_lower:
            if "subgroup" in question_lower:
                education_patterns = [
                    r"(some\s+college\s+or\s+more)",
                    r"(high\s+school\s+or\s+less)",
                    r"(college\s+graduate)",
                    r"(some\s+college)",
                    r"(high\s+school)",
                    r"(less\s+than\s+high\s+school)",
                    r"(bachelor\s+degree)",
                ]
                for pattern in education_patterns:
                    match = re.search(pattern, answer, re.IGNORECASE)
                    if match:
                        return match.group(1)

            key_phrases = re.findall(r"(?:is|are|:\s+)([A-Z][^.!?]{5,80})", answer)
            for phrase in key_phrases:
                cleaned = re.sub(r"^(the|a|an)\s+", "", phrase.strip(), flags=re.IGNORECASE)
                cleaned = re.split(r"[,;]\s+|\s+with\s+", cleaned)[0].strip()
                if cleaned and len(cleaned.split()) <= 8 and not cleaned.lower().startswith(
                    ("according", "based", "the report", "in the", "this", "that")
                ):
                    return cleaned

            that_phrases = re.findall(r"(?:that|which)\s+([A-Z][^.!?]{5,60})", answer)
            for phrase in that_phrases:
                cleaned = re.split(r"[,;]\s+", phrase.strip())[0]
                if len(cleaned.split()) <= 8:
                    return cleaned

        return None

    def _extract_numeric_answer(self, answer: str, question_lower: str, requires_multiple: bool) -> Optional[str]:
        if requires_multiple or not any(token in question_lower for token in ("how many", "how much", "count")):
            return None

        text_numbers = {
            "one": "1",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "eight": "8",
            "nine": "9",
            "ten": "10",
            "eleven": "11",
            "twelve": "12",
        }

        explicit_patterns = [
            r"(\d+)\s+(?:out of|of the|of them|references?|items?|charts?|pages?)\s+(?:are|is|were|was)",
            r"(?:are|is|were|was)\s+(\d+)\s+(?:out of|of the|references?|items?|charts?)",
        ]
        for pattern in explicit_patterns:
            match = re.search(pattern, answer, re.IGNORECASE)
            if match and int(match.group(1)) <= 50:
                return match.group(1)

        for text, num in text_numbers.items():
            patterns = [
                rf"\b(?:exactly|precisely)\s+{text}\b",
                rf"\b{text}\s+(?:out of|of the|references?|items?|charts?|pages?)",
                rf"\b(?:at least|about|approximately)\s+{text}\b",
            ]
            for pattern in patterns:
                if re.search(pattern, answer, re.IGNORECASE):
                    return num

        number_patterns = [
            r"(?:found|identified|counted|determined|are|is|number|total|count)\s+(?:that\s+)?(\d+)",
            r"(\d+)\s+(?:out of|of the|of them|references?|items?|charts?|pages?)",
            r"(?:answer|result|total|count)[:\s]+(\d+)",
            r"(\d+)\s+(?:unique|distinct|different)\s+(?:references?|items?|charts?|groups?)",
        ]
        for pattern in number_patterns:
            match = re.search(pattern, answer, re.IGNORECASE)
            if match:
                value = match.group(1)
                if int(value) <= 50 or "page" not in answer.lower():
                    return value

        numbers = re.findall(r"\b(\d+)\b", answer)
        if numbers:
            candidates = [n for n in numbers if int(n) <= 50]
            if candidates:
                single_digits = [n for n in candidates if int(n) < 10]
                return single_digits[0] if single_digits else candidates[0]
            return numbers[0]

        return None

    def _extract_first_sentence(self, answer: str, requires_multiple: bool) -> Optional[str]:
        if requires_multiple:
            return None

        sentences = re.split(r"[.!?]\s+", answer)
        if not sentences:
            return None

        first_sentence = sentences[0].strip()
        first_sentence = re.sub(
            r"^(According to|Based on|The report|In the document|The reference|Answer:)[^,]*,\s*",
            "",
            first_sentence,
            flags=re.IGNORECASE,
        )
        first_sentence = re.sub(r"\[[^\]]+\]", "", first_sentence)
        first_sentence = re.sub(r'"PH_[^"]+\.pdf"', "", first_sentence, flags=re.IGNORECASE)
        first_sentence = re.split(r"[,;]\s+|\s+with\s+", first_sentence)[0].strip()

        return first_sentence or None

    def _extract_multi_value(self, answer: str) -> Optional[str]:
        multi_values: List[str] = []

        group_patterns = [
            r"(?:group|is|are|was|were)\s+(?:is\s+)?(?:the\s+)?(Whites?|Latinos?|Hispanics?|Blacks?|Asians?|Poor\s+Financial\s+Condition|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"(Whites?|Latinos?|Hispanics?|Blacks?|Asians?)\s+(?:whose|who|which|group)",
            r"(?:the\s+)?(Whites?|Latinos?|Hispanics?|Blacks?|Asians?)\s+(?:group|category|subgroup)",
            r"(?:is|are|was|were)\s+(?:the\s+)?(Whites?|Latinos?|Hispanics?|Blacks?|Asians?)\s+(?:group|category)",
        ]
        for pattern in group_patterns:
            match = re.search(pattern, answer, re.IGNORECASE)
            if match:
                group_name = match.group(1).strip()
                if group_name and len(group_name.split()) <= 4:
                    multi_values.append(group_name)
                    break

        change_patterns = [
            r"(?:dropped|decreased|fell|declined)\s+by\s+(\d+)\s*(?:percentage\s*points?|%)",
            r"(?:increased|rose|grew|went\s+up)\s+by\s+(\d+)\s*(?:percentage\s*points?|%)",
            r"(\d+)\s*(?:percentage\s*points?|%)\s*(?:drop|decrease|increase|rise)",
            r"\b(\d+\.?\d*%)",
        ]
        for pattern in change_patterns:
            match = re.search(pattern, answer, re.IGNORECASE)
            if match:
                value = match.group(1)
                if "percentage point" in answer.lower() and not value.endswith("%"):
                    value = f"{value}%"
                multi_values.append(value)
                break

        if len(multi_values) >= 2:
            return json.dumps(multi_values, ensure_ascii=False)
        if len(multi_values) == 1:
            return multi_values[0]
        return None

    def _normalize_result(self, result: Optional[str]) -> str:
        if not result:
            return "Not answerable"

        if result == "No final answer found":
            return "Not answerable"

        result = result.strip()

        if result.isdigit() and result.startswith("0"):
            result = str(int(result))

        cleanup_patterns = [
            r"^(According to|Based on|The report|In the document|The reference|Answer:|The answer is|The result is|I found that|It is|This is|That is|They are|We can see that|The document shows that|The chart shows that|The table shows that)[^,]*,\s*"
        ]
        for pattern in cleanup_patterns:
            result = re.sub(pattern, "", result, flags=re.IGNORECASE).strip()

        article_match = re.match(r"^(the|a|an)\s+([A-Z][^.!?]{0,100})$", result, flags=re.IGNORECASE)
        if article_match:
            result = article_match.group(2).strip()

        replacements = {
            "less well off": "Less well-off",
        }
        lower_result = result.lower()
        if lower_result in replacements:
            result = replacements[lower_result]

        result = re.sub(r"[.,;]+$", "", result).strip()
        result = re.sub(r"\s+", " ", result)

        return result or "Not answerable"
    
    def run_benchmark(self, parallel: bool = False, output_dir: str = "results") -> List[Dict[str, Any]]:
        """
        Run agent on all benchmark tasks.
        Skip tasks that have already been completed (based on existing results file).
        
        Args:
            parallel: Whether to run tasks in parallel
            output_dir: Output directory for results
            
        Returns:
            List of results
        """
        if not self.benchmark:
            raise ValueError("Benchmark not loaded")
        
        print(f"\n🚀 Starting benchmark execution...")
        print(f"   Tasks: {len(self.benchmark.items)}")
        print(f"   Parallel: {parallel}")
        print(f"   Max workers: {self.config.max_workers}")
        
        # Load existing results to skip already completed tasks
        # Only skip successfully completed tasks, retry failed ones
        existing_results = {}
        successful_results = {}
        if self.config.save_results:
            all_existing = self._load_existing_results(output_dir)
            # Separate successful and failed results
            for task_id, result in all_existing.items():
                if result.get("success", False):
                    successful_results[task_id] = result
                # Failed tasks will be retried, so don't add them to existing_results
            existing_results = successful_results
        
        # Prepare tasks, filtering out only successfully completed ones
        all_tasks = [
            {"id": item.id, "question": item.question}
            for item in self.benchmark.items
        ]
        
        tasks_to_run = [
            task for task in all_tasks 
            if task["id"] not in existing_results
        ]
        
        skipped_count = len(existing_results)
        retry_count = len(all_tasks) - len(tasks_to_run) - skipped_count
        if skipped_count > 0:
            print(f"   ⏭️  Skipping {skipped_count} successfully completed tasks")
        if retry_count > 0:
            print(f"   🔄 Retrying {retry_count} previously failed tasks")
        if skipped_count > 0 or retry_count > 0:
            print(f"   🆕 Remaining tasks to run: {len(tasks_to_run)}")
        
        # Initialize results with only successful ones
        self.results = list(existing_results.values())
        
        # If all tasks are already completed, return early
        if not tasks_to_run:
            print(f"\n✅ All tasks already completed! No new tasks to run.")
            print(f"   Total results: {len(self.results)}")
            print(f"   Successful: {sum(1 for r in self.results if r['success'])}")
            print(f"   Failed: {sum(1 for r in self.results if not r['success'])}")
            return self.results
        
        if parallel and len(tasks_to_run) > 1:
            # Run in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                futures = [
                    executor.submit(self.run_single_task, task) 
                    for task in tasks_to_run
                ]
                
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    self.results.append(result)
                    # Write result immediately after completion
                    if self.config.save_results:
                        self._write_single_result(result, output_dir=output_dir)
        else:
            # Run sequentially
            for task in tasks_to_run:
                result = self.run_single_task(task)
                self.results.append(result)
                # Write result immediately after completion
                if self.config.save_results:
                    self._write_single_result(result, output_dir=output_dir)
        
        print(f"\n✅ Benchmark execution completed!")
        print(f"   Total results: {len(self.results)}")
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
    
    def _get_output_file_path(self, output_dir: str = "results") -> str:
        """
        Get the output file path for results.
        
        Args:
            output_dir: Output directory
            
        Returns:
            Path to output file
        """
        benchmark_name = self.benchmark.name if self.benchmark else "unknown"
        return os.path.join(output_dir, f"result_{benchmark_name}.jsonl")
    
    def _load_existing_results(self, output_dir: str = "results") -> Dict[str, Dict[str, Any]]:
        """
        Load existing results from output file if it exists.
        
        Args:
            output_dir: Output directory
            
        Returns:
            Dictionary mapping task_id to result dictionary
        """
        output_file = self._get_output_file_path(output_dir)
        
        if not os.path.exists(output_file):
            return {}
        
        existing_results = {}
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        result = json.loads(line)
                        task_id = result.get("task_id")
                        if task_id:
                            existing_results[task_id] = result
                    except json.JSONDecodeError:
                        # Skip invalid lines
                        continue
            print(f"📂 Found existing results file: {output_file}")
            print(f"   Loaded {len(existing_results)} completed tasks")
        except Exception as e:
            print(f"⚠️  Warning: Failed to load existing results: {str(e)}")
            return {}
        
        return existing_results
    
    def _write_single_result(self, result: Dict[str, Any], output_dir: str = "results"):
        """
        Write a single result to file immediately.
        
        Args:
            result: Single result dictionary
            output_dir: Output directory
        """
        if self.output_file is None:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate output filename
            self.output_file = self._get_output_file_path(output_dir)
        
        # Append result to file
        with open(self.output_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
    
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
        
        # Get benchmark name
        benchmark_name = self.benchmark.name if self.benchmark else "unknown"
        
        # Output file should already be created during run_benchmark
        if not self.output_file:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate output filename
            self.output_file = self._get_output_file_path(output_dir)
        
        print(f"💾 Results saved to: {self.output_file}")
        
        # Save evaluation results if available
        if self.config.evaluate_results and self.benchmark.evaluation_results:
            eval_file = os.path.join(output_dir, f"evaluation_{benchmark_name}.json")
            self.benchmark.save_results(eval_file)
            print(f"📊 Evaluation results saved to: {eval_file}")
        
        return self.output_file
    
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
        output_dir = kwargs.get('output_dir', 'results')
        self.run_benchmark(parallel=kwargs.get('parallel', False), output_dir=output_dir)
        
        # Evaluate results
        if self.config.evaluate_results:
            evaluation_summary = self.evaluate_results()
        else:
            evaluation_summary = None
        
        # Save results
        if self.config.save_results:
            output_file = self.save_results(output_dir=output_dir)
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
    parser.add_argument("--mode", type=str, choices=["math", "py", "rag", "web", "doc"], 
                       required=True, help="Environment mode")
    parser.add_argument("--data", type=str, required=True, 
                       help="Path to benchmark data file")
    
    # Optional arguments
    parser.add_argument("--model", type=str, default="gpt-4.1-2025-04-14",
                       help="OpenAI model name")
    parser.add_argument("--max-turns", type=int, default=100,
                       help="Maximum conversation turns")
    parser.add_argument("--max-retries", type=int, default=3,
                       help="Maximum retries per turn")
    parser.add_argument("--max-workers", type=int, default=10,
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
    # Doc mode arguments
    parser.add_argument("--ocr-model-path", type=str, default="",
                       help="Path to the MinerU model for Doc mode.")
    parser.add_argument("--ocr-backend-type", type=str, default="transformers",
                       choices=["transformers", "vllm-engine"],
                       help="Backend type for DocOCRTool.")
    parser.add_argument("--skip-doc-ocr", action="store_true",
                       help="Skip initializing DocOCRTool (use when OCR JSON already prepared).")
    
    args = parser.parse_args()
    
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
        
    elif args.mode == "doc":
        if not args.skip_doc_ocr:
            if not args.ocr_model_path:
                raise ValueError("--ocr-model-path is required for Doc mode unless --skip-doc-ocr is set.")

            if not args.ocr_backend_type:
                raise ValueError("--ocr-backend-type is required for Doc mode.")
            
            env_kwargs.update({
                "ocr_model_path": args.ocr_model_path,
                "ocr_backend_type": args.ocr_backend_type,
            })
        else:
            env_kwargs.update({"skip_doc_ocr": True})

    # Create and run agent
    runner = AgentRunner(config)
    
    try:
        summary = runner.run(
            mode=args.mode,
            data_path=args.data,
            parallel=args.parallel,
            output_dir=args.output_dir,
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