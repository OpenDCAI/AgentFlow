import sys
import asyncio
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from synthesis.core.config import SynthesisConfig
from synthesis.core.sampler import TrajectorySampler


class FakeWorker:
    async def execute_tool(self, tool_name, parameters, **kwargs):
        return {"tool_name": tool_name, "parameters": parameters, "kwargs": kwargs}


def test_sample_trajectory_recovers_after_empty_content_response(monkeypatch):
    responses = [
        SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=None))]),
        SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content="""
                        <response>
                          <intent>Search for the museum city</intent>
                          <tool_name>query_knowledge_base_dense</tool_name>
                          <parameters>{"query": "museum city"}</parameters>
                        </response>
                        """
                    )
                )
            ]
        ),
    ]
    calls = []

    def fake_create_openai_client(api_key, base_url):
        return object()

    async def fake_async_chat_completion(client, **kwargs):
        calls.append(kwargs)
        return responses.pop(0)

    async def fake_sleep(_):
        return None

    monkeypatch.setattr("synthesis.core.sampler.create_openai_client", fake_create_openai_client)
    monkeypatch.setattr("synthesis.core.sampler.async_chat_completion", fake_async_chat_completion)
    monkeypatch.setattr(
        "synthesis.core.sampler.get_tool_schemas",
        lambda available_tools=None: [
            {
                "name": "query_knowledge_base_dense",
                "description": "Searches knowledge base",
                "parameters": [{"name": "query", "type": "string", "required": True, "description": "query"}],
            }
        ],
    )
    monkeypatch.setattr("synthesis.core.sampler.asyncio.sleep", fake_sleep)

    sampler = TrajectorySampler(
        FakeWorker(),
        SynthesisConfig(
            api_key="test-key",
            base_url="http://example.com",
            model_name="test-model",
            max_depth=1,
            branching_factor=1,
        ),
    )

    nodes = asyncio.run(sampler.sample_trajectory_tree("seed"))

    assert len(nodes) == 2
    assert len(calls) == 2
    child_nodes = [node for node in nodes.values() if node.parent_id is not None]
    assert len(child_nodes) == 1
    assert child_nodes[0].action["tool_name"] == "query_knowledge_base_dense"


def test_sample_trajectory_retries_when_tool_name_is_missing(monkeypatch):
    responses = [
        SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content="""
                        <response>
                          <intent>Search for the museum city</intent>
                          <parameters>{"query": "museum city"}</parameters>
                        </response>
                        """
                    )
                )
            ]
        ),
        SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content="""
                        <response>
                          <intent>Search for the museum city</intent>
                          <tool_name>query_knowledge_base_dense</tool_name>
                          <parameters>{"query": "museum city"}</parameters>
                        </response>
                        """
                    )
                )
            ]
        ),
    ]
    calls = []

    def fake_create_openai_client(api_key, base_url):
        return object()

    async def fake_async_chat_completion(client, **kwargs):
        calls.append(kwargs)
        return responses.pop(0)

    async def fake_sleep(_):
        return None

    monkeypatch.setattr("synthesis.core.sampler.create_openai_client", fake_create_openai_client)
    monkeypatch.setattr("synthesis.core.sampler.async_chat_completion", fake_async_chat_completion)
    monkeypatch.setattr(
        "synthesis.core.sampler.get_tool_schemas",
        lambda available_tools=None: [
            {
                "name": "query_knowledge_base_dense",
                "description": "Searches knowledge base",
                "parameters": [{"name": "query", "type": "string", "required": True, "description": "query"}],
            }
        ],
    )
    monkeypatch.setattr("synthesis.core.sampler.asyncio.sleep", fake_sleep)

    sampler = TrajectorySampler(
        FakeWorker(),
        SynthesisConfig(
            api_key="test-key",
            base_url="http://example.com",
            model_name="test-model",
            max_depth=1,
            branching_factor=1,
        ),
    )

    nodes = asyncio.run(sampler.sample_trajectory_tree("seed"))

    assert len(nodes) == 2
    assert len(calls) == 2
    child_nodes = [node for node in nodes.values() if node.parent_id is not None]
    assert len(child_nodes) == 1
    assert child_nodes[0].action["tool_name"] == "query_knowledge_base_dense"
