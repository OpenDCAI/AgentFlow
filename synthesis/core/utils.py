import asyncio
import json
import re
import time
import xml.etree.ElementTree as ET
from typing import Any, Dict, Tuple, Type
import pdb

import openai


def create_openai_client(api_key: str, base_url: str) -> openai.OpenAI:
    if not api_key:
        raise ValueError("Missing api_key in synthesis config")
    if not base_url:
        raise ValueError("Missing base_url in synthesis config")
    return openai.OpenAI(api_key=api_key, base_url=base_url)


def extract_json_object(text: str) -> str:
    """Extract the first complete JSON object from text (forward scan)."""
    if not text:
        return text
    start = text.find("{")
    if start == -1:
        return text
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
                return text[start:i + 1]
    return text[start:]


def extract_xml_block(text: str, root_tag: str = "response") -> str:
    """Extract the first XML block with the given root tag."""
    if not text:
        return text
    pattern = rf"<{root_tag}\b[^>]*>.*?</{root_tag}>"
    match = re.search(pattern, text, flags=re.DOTALL)
    return match.group(0) if match else text


def parse_action_xml(text: str) -> Dict[str, Any]:
    """Parse XML into {intent, action:{tool_name, parameters}}."""
    def _find_tag(raw: str, tag: str) -> str:
        match = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", raw, flags=re.DOTALL)
        return (match.group(1).strip() if match else "")

    xml_text = extract_xml_block(text, root_tag="response")
    intent = ""
    tool_name = ""
    parameters: Dict[str, Any] = {}
    if "<response" in xml_text:
        root = ET.fromstring(xml_text)
        intent = (root.findtext("intent") or "").strip()
        action_el = root.find("action")
        if action_el is not None:
            tool_name = (action_el.findtext("tool_name") or "").strip()
            params_text = (action_el.findtext("parameters") or "").strip()
        else:
            tool_name = (root.findtext("tool_name") or "").strip()
            params_text = (root.findtext("parameters") or "").strip()
    else:
        intent = _find_tag(text, "intent")
        tool_name = _find_tag(text, "tool_name")
        params_text = _find_tag(text, "parameters")

    if params_text:
        try:
            parameters = json.loads(params_text)
        except Exception:
            parameters = {}
    return {
        "intent": intent,
        "action": {
            "tool_name": tool_name,
            "parameters": parameters
        }
    }


def chat_completion(
    client: openai.OpenAI,
    *,
    max_retries: int = 3,
    retry_wait: float = 0.5,
    retry_backoff: float = 2.0,
    retry_exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    **kwargs: Any
) -> Any:
    for attempt in range(max_retries + 1):
        try:
            return client.chat.completions.create(**kwargs)
        except retry_exceptions:
            if attempt >= max_retries:
                raise
            time.sleep(retry_wait * (retry_backoff ** attempt))


async def async_chat_completion(
    client: openai.OpenAI,
    *,
    max_retries: int = 3,
    retry_wait: float = 0.5,
    retry_backoff: float = 2.0,
    retry_exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    **kwargs: Any
) -> Any:
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
            await asyncio.sleep(retry_wait * (retry_backoff ** attempt))
