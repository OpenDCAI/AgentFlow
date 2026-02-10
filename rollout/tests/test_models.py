"""
Tests for Rollout data models
"""

import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rollout.core import (
    BenchmarkItem,
    Message,
    ToolCall,
    Trajectory,
    TaskResult,
    EvaluationResult
)


class TestBenchmarkItem:
    """Test BenchmarkItem model"""

    def test_basic_creation(self):
        """Test basic item creation"""
        item = BenchmarkItem(
            id="task_001",
            question="What is 2+2?",
            answer="4"
        )
        
        assert item.id == "task_001"
        assert item.question == "What is 2+2?"
        assert item.answer == "4"

    def test_from_dict_standard(self):
        """Test creating from standard dict format"""
        data = {
            "id": "task_001",
            "question": "What is the capital of France?",
            "answer": "Paris"
        }
        
        item = BenchmarkItem.from_dict(data)
        
        assert item.id == "task_001"
        assert item.question == "What is the capital of France?"
        assert item.answer == "Paris"

    def test_from_dict_alternative_keys(self):
        """Test creating from dict with alternative keys"""
        data = {
            "task_id": "task_002",
            "query": "What is Python?",
            "ground_truth": "A programming language"
        }
        
        item = BenchmarkItem.from_dict(data)
        
        assert item.id == "task_002"
        assert item.question == "What is Python?"
        assert item.answer == "A programming language"

    def test_to_dict(self):
        """Test converting to dict"""
        item = BenchmarkItem(
            id="task_001",
            question="Test question",
            answer="Test answer",
            metadata={"source": "test"}
        )
        
        data = item.to_dict()
        
        assert data["id"] == "task_001"
        assert data["question"] == "Test question"
        assert data["answer"] == "Test answer"
        assert data["metadata"]["source"] == "test"


class TestMessage:
    """Test Message model"""

    def test_basic_message(self):
        """Test basic message creation"""
        msg = Message(role="user", content="Hello")
        
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.tool_calls is None

    def test_message_with_tool_calls(self):
        """Test message with tool calls"""
        tool_calls = [
            {"id": "call_1", "function": {"name": "search", "arguments": "{}"}}
        ]
        msg = Message(role="assistant", content="", tool_calls=tool_calls)
        
        assert msg.tool_calls == tool_calls

    def test_to_dict(self):
        """Test converting to OpenAI-compatible dict"""
        msg = Message(role="assistant", content="Hello")
        data = msg.to_dict()
        
        assert data["role"] == "assistant"
        assert data["content"] == "Hello"
        assert "tool_calls" not in data

    def test_from_dict(self):
        """Test creating from dict"""
        data = {
            "role": "tool",
            "content": "Result",
            "tool_call_id": "call_1",
            "name": "search"
        }
        
        msg = Message.from_dict(data)
        
        assert msg.role == "tool"
        assert msg.content == "Result"
        assert msg.tool_call_id == "call_1"
        assert msg.name == "search"


class TestToolCall:
    """Test ToolCall model"""

    def test_successful_tool_call(self):
        """Test successful tool call"""
        tc = ToolCall(
            tool_name="web_search",
            parameters={"query": ["test"]},
            result={"results": [{"title": "Test"}]},
            success=True,
            execution_time_ms=150.5
        )
        
        assert tc.tool_name == "web_search"
        assert tc.success == True
        assert tc.execution_time_ms == 150.5

    def test_failed_tool_call(self):
        """Test failed tool call"""
        tc = ToolCall(
            tool_name="web_visit",
            parameters={"urls": ["http://invalid"]},
            result=None,
            success=False,
            error="Connection timeout"
        )
        
        assert tc.success == False
        assert tc.error == "Connection timeout"


class TestTrajectory:
    """Test Trajectory model"""

    def test_basic_trajectory(self):
        """Test basic trajectory creation"""
        traj = Trajectory(
            task_id="task_001",
            question="What is Python?",
            messages=[
                Message(role="user", content="What is Python?"),
                Message(role="assistant", content="Python is a programming language.")
            ],
            final_answer="Python is a programming language.",
            total_turns=1,
            success=True
        )
        
        assert traj.task_id == "task_001"
        assert len(traj.messages) == 2
        assert traj.success == True

    def test_to_dict(self):
        """Test trajectory serialization"""
        traj = Trajectory(
            task_id="task_001",
            question="Test",
            messages=[Message(role="user", content="Test")],
            final_answer="Answer",
            total_turns=1,
            success=True
        )
        
        data = traj.to_dict()
        
        assert data["task_id"] == "task_001"
        assert len(data["messages"]) == 1
        assert data["final_answer"] == "Answer"


class TestTaskResult:
    """Test TaskResult model"""

    def test_successful_result(self):
        """Test successful task result"""
        result = TaskResult(
            task_id="task_001",
            question="What is 2+2?",
            predicted_answer="4",
            ground_truth="4",
            success=True,
            score=1.0
        )
        
        assert result.success == True
        assert result.score == 1.0

    def test_failed_result(self):
        """Test failed task result"""
        result = TaskResult(
            task_id="task_002",
            question="Complex question",
            predicted_answer="",
            ground_truth="Expected answer",
            success=False,
            error="Max turns reached"
        )
        
        assert result.success == False
        assert result.error == "Max turns reached"


class TestEvaluationResult:
    """Test EvaluationResult model"""

    def test_evaluation_result(self):
        """Test evaluation result creation"""
        eval_result = EvaluationResult(
            task_id="task_001",
            predicted="Paris",
            ground_truth="Paris",
            score=1.0,
            metric="exact_match",
            details={"normalized_match": True}
        )
        
        assert eval_result.score == 1.0
        assert eval_result.metric == "exact_match"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
