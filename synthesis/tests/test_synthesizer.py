import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from synthesis.core.config import SynthesisConfig
from synthesis.core.models import Trajectory, TrajectoryNode
from synthesis.core.synthesizer import QASynthesizer


class FakeAPIError(Exception):
    def __init__(self, message, *, error_type=None, code=None):
        super().__init__(message)
        self.body = {
            "error": {
                "message": message,
                "type": error_type,
                "code": code,
            }
        }


def make_synthesizer(monkeypatch, fake_chat_completion):
    def fake_create_openai_client(api_key, base_url):
        return object()

    monkeypatch.setattr("synthesis.core.synthesizer.create_openai_client", fake_create_openai_client)
    monkeypatch.setattr("synthesis.core.synthesizer.chat_completion", fake_chat_completion)

    return QASynthesizer(
        SynthesisConfig(
            api_key="test-key",
            base_url="http://example.com",
            model_name="tencent/hy3-preview:free",
        )
    )


def make_trajectory():
    return Trajectory(
        trajectory_id="traj-1",
        source_id="source-1",
        seed_data="seed",
        total_depth=3,
        nodes=[
            TrajectoryNode(
                node_id="node-1",
                observation="museum stop located in Shanghai",
                intent="Find the final museum location",
            )
        ],
    )


def test_synthesize_qa_retries_without_response_format_when_json_mode_is_unsupported(monkeypatch):
    calls = []

    def fake_chat_completion(client, **kwargs):
        calls.append(kwargs)
        if "response_format" in kwargs:
            raise FakeAPIError(
                "This model does not support response_format=json_object.",
                error_type="invalid_request_error",
                code="unsupported_parameter",
            )
        content = """
        Here is the repaired payload:
        {
          "question": "Which city hosts the museum identified in the final step?",
          "answer": "Shanghai",
          "reasoning_steps": [
            {"hop": 1, "fact": "The route ends at a museum.", "evidence": "museum stop", "output": "museum"},
            {"hop": 2, "fact": "The museum is in Shanghai.", "evidence": "located in Shanghai", "output": "Shanghai museum"},
            {"hop": 3, "fact": "The host city is Shanghai.", "evidence": "Shanghai museum", "output": "Shanghai"}
          ]
        }
        Thanks.
        """
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
        )

    synthesizer = make_synthesizer(monkeypatch, fake_chat_completion)
    trajectory = make_trajectory()

    qa = synthesizer.synthesize_qa(trajectory)

    assert qa is not None
    assert qa.answer == "Shanghai"
    assert len(calls) == 2
    assert calls[0]["response_format"] == {"type": "json_object"}
    assert "response_format" not in calls[1]


def test_synthesize_qa_does_not_fallback_for_rate_limit_errors_even_if_message_mentions_response_format(monkeypatch):
    calls = []

    def fake_chat_completion(client, **kwargs):
        calls.append(kwargs)
        raise FakeAPIError(
            "Rate limit exceeded while validating response_format=json_object; this model does not support that combination right now.",
            error_type="rate_limit_error",
            code="rate_limit_exceeded",
        )

    synthesizer = make_synthesizer(monkeypatch, fake_chat_completion)

    qa = synthesizer.synthesize_qa(make_trajectory())

    assert qa is None
    assert len(calls) == 3
    assert all(call["response_format"] == {"type": "json_object"} for call in calls)


def test_synthesize_qa_recovers_after_empty_content_response(monkeypatch):
    calls = []

    def fake_chat_completion(client, **kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=None))]
            )

        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content="""
                        {
                          "question": "Which city hosts the museum identified in the final step?",
                          "answer": "Shanghai",
                          "reasoning_steps": [
                            {"hop": 1, "fact": "The route ends at a museum.", "evidence": "museum stop", "output": "museum"},
                            {"hop": 2, "fact": "The museum is in Shanghai.", "evidence": "located in Shanghai", "output": "Shanghai museum"},
                            {"hop": 3, "fact": "The host city is Shanghai.", "evidence": "Shanghai museum", "output": "Shanghai"}
                          ]
                        }
                        """
                    )
                )
            ]
        )

    synthesizer = make_synthesizer(monkeypatch, fake_chat_completion)

    qa = synthesizer.synthesize_qa(make_trajectory())

    assert qa is not None
    assert qa.answer == "Shanghai"
    assert len(calls) == 2
