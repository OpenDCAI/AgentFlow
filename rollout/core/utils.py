"""
Utility functions for Rollout pipeline
"""

import asyncio
import json
import re
import time
from typing import Any, Dict, List, Tuple, Type, Optional
import openai


def create_openai_client(api_key: str, base_url: str) -> openai.OpenAI:
    """Create OpenAI client from rollout config only."""
    if not api_key:
        raise ValueError("Missing api_key in rollout config")
    if not base_url:
        raise ValueError("Missing base_url in rollout config")
    return openai.OpenAI(api_key=api_key, base_url=base_url)


def chat_completion(
    client: openai.OpenAI,
    *,
    max_retries: int = 3,
    retry_wait: float = 0.5,
    retry_backoff: float = 2.0,
    retry_exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    **kwargs: Any
) -> Any:
    """Synchronous chat completion with retry logic"""
    for attempt in range(max_retries + 1):
        try:
            return client.chat.completions.create(**kwargs)
        except retry_exceptions as e:
            if attempt >= max_retries:
                raise
            wait_time = retry_wait * (retry_backoff ** attempt)
            print(f"⚠️ LLM call failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
            print(f"   Retrying in {wait_time:.1f}s...")
            time.sleep(wait_time)


async def async_chat_completion(
    client: openai.OpenAI,
    *,
    max_retries: int = 3,
    retry_wait: float = 0.5,
    retry_backoff: float = 2.0,
    retry_exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    **kwargs: Any
) -> Any:
    """Asynchronous chat completion with retry logic"""
    loop = asyncio.get_event_loop()
    for attempt in range(max_retries + 1):
        try:
            return await loop.run_in_executor(
                None,
                lambda: client.chat.completions.create(**kwargs)
            )
        except retry_exceptions as e:
            if attempt >= max_retries:
                raise
            wait_time = retry_wait * (retry_backoff ** attempt)
            print(f"⚠️ LLM call failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
            await asyncio.sleep(wait_time)


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON object from text"""
    if not text:
        return None
    
    # Try to find JSON in code blocks first
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find raw JSON object
    start = text.find("{")
    if start == -1:
        return None
    
    depth = 0
    in_string = False
    escape = False
    
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    return None
    
    return None


def extract_final_answer(text: str) -> str:
    """Extract final answer from assistant response"""
    if not text:
        return ""
    
    # Look for common answer patterns
    patterns = [
        r"(?:final answer|answer is|the answer is|answer:)\s*[:\-]?\s*(.+?)(?:\n|$)",
        r"(?:therefore|thus|so|hence),?\s+(?:the answer is\s+)?(.+?)(?:\.|$)",
        r"\*\*Answer\*\*:?\s*(.+?)(?:\n|$)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            answer = match.group(1).strip()
            # Clean up common suffixes
            answer = re.sub(r'\s*\.$', '', answer)
            return answer
    
    # If no pattern matched, return the last non-empty line (often the answer)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        return lines[-1]
    
    return text.strip()


def normalize_answer(answer: str) -> str:
    """Normalize answer for comparison"""
    if not answer:
        return ""
    
    # Convert to lowercase
    text = answer.lower().strip()
    
    # Remove common prefixes
    prefixes = ["the answer is", "answer:", "final answer:", "therefore,", "thus,", "so,"]
    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
    
    # Remove punctuation at the end
    text = re.sub(r'[.,;:!?]+$', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def load_benchmark_data(data_path: str) -> List[Dict[str, Any]]:
    """Load benchmark data from file (supports jsonl and json)"""
    items = []
    
    if data_path.endswith('.jsonl'):
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    items.append(json.loads(line))
    elif data_path.endswith('.json'):
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict) and 'data' in data:
                items = data['data']
            else:
                raise ValueError(f"Unsupported JSON structure in {data_path}")
    else:
        raise ValueError(f"Unsupported file format: {data_path}")
    
    return items


def format_tool_result_for_message(result: Any, max_length: int = 4000) -> str:
    """Format tool result for inclusion in conversation"""
    if isinstance(result, dict):
        # Handle sandbox response format
        if "data" in result:
            data = result.get("data", {})
            if isinstance(data, dict) and "result" in data:
                text = str(data["result"])
            else:
                text = json.dumps(data, ensure_ascii=False, indent=2)
        else:
            text = json.dumps(result, ensure_ascii=False, indent=2)
    elif isinstance(result, str):
        text = result
    else:
        text = str(result)
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length] + f"\n... (truncated, total {len(text)} chars)"
    
    return text


def convert_tool_schema_to_openai(tool_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Convert tool schema to OpenAI function calling format"""
    properties = {}
    required = []
    
    for param in tool_schema.get("parameters", []):
        param_name = param.get("name")
        param_type = param.get("type", "string")
        
        # Map types
        type_mapping = {
            "string": "string",
            "integer": "integer",
            "number": "number",
            "boolean": "boolean",
            "array": "array",
            "object": "object",
        }
        
        prop = {
            "type": type_mapping.get(param_type, "string"),
            "description": param.get("description", "")
        }
        
        if param_type == "array":
            prop["items"] = {"type": param.get("array_type", "string")}
        
        if "enum" in param:
            prop["enum"] = param["enum"]
        
        properties[param_name] = prop
        
        if param.get("required", False):
            required.append(param_name)
    
    return {
        "type": "function",
        "function": {
            "name": tool_schema.get("name"),
            "description": tool_schema.get("description", ""),
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    }


def get_timestamp() -> str:
    """Get current timestamp string"""
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d_%H%M%S")
