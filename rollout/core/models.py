"""
Data models for Rollout pipeline
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class BenchmarkItem:
    """Single benchmark task item"""
    id: str
    question: str
    answer: Optional[str] = None  # Ground truth answer (if available)
    kwargs: Dict[str, Any] = field(default_factory=dict)  # Additional kwargs to pass to tools (e.g., seed_path for doc tools)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BenchmarkItem':
        """Create from dictionary"""
        # Extract kwargs if present (for doc tools, this contains seed_path)
        kwargs = data.get("kwargs", {})
        if not isinstance(kwargs, dict):
            kwargs = {}
        
        # Exclude standard fields and kwargs from metadata
        excluded_fields = {"id", "task_id", "question", "query", "input", "answer", "ground_truth", "expected", "kwargs"}
        metadata = {k: v for k, v in data.items() if k not in excluded_fields}
        
        return cls(
            id=str(data.get("id", data.get("task_id", ""))),
            question=data.get("question", data.get("query", data.get("input", ""))),
            answer=data.get("answer", data.get("ground_truth", data.get("expected", None))),
            kwargs=kwargs,
            metadata=metadata
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            "id": self.id,
            "question": self.question,
        }
        if self.answer is not None:
            result["answer"] = self.answer
        if self.kwargs:
            result["kwargs"] = self.kwargs
        if self.metadata:
            result["metadata"] = self.metadata
        return result


@dataclass
class ToolCall:
    """Single tool call record"""
    tool_name: str
    parameters: Dict[str, Any]
    result: Any
    success: bool
    error: Optional[str] = None
    execution_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Message:
    """Single message in conversation"""
    role: str  # "system", "user", "assistant", "tool"
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None  # For tool messages

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (OpenAI compatible format)"""
        result = {"role": self.role, "content": self.content}
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        if self.name:
            result["name"] = self.name
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create from dictionary"""
        return cls(
            role=data.get("role", ""),
            content=data.get("content", ""),
            tool_calls=data.get("tool_calls"),
            tool_call_id=data.get("tool_call_id"),
            name=data.get("name")
        )


@dataclass
class Trajectory:
    """Complete conversation trajectory for a task"""
    task_id: str
    question: str
    messages: List[Message] = field(default_factory=list)
    tool_calls: List[ToolCall] = field(default_factory=list)
    final_answer: str = ""
    total_turns: int = 0
    success: bool = False
    error: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    execution_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "task_id": self.task_id,
            "question": self.question,
            "messages": [m.to_dict() for m in self.messages],
            "tool_calls": [tc.to_dict() for tc in self.tool_calls],
            "final_answer": self.final_answer,
            "total_turns": self.total_turns,
            "success": self.success,
            "error": self.error,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "execution_time_ms": self.execution_time_ms
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Trajectory':
        """Create from dictionary"""
        return cls(
            task_id=data.get("task_id", ""),
            question=data.get("question", ""),
            messages=[Message.from_dict(m) for m in data.get("messages", [])],
            tool_calls=[],  # Not reconstructing tool calls from dict
            final_answer=data.get("final_answer", ""),
            total_turns=data.get("total_turns", 0),
            success=data.get("success", False),
            error=data.get("error"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            execution_time_ms=data.get("execution_time_ms", 0.0)
        )


@dataclass
class TaskResult:
    """Result of a single task execution"""
    task_id: str
    question: str
    predicted_answer: str
    ground_truth: Optional[str] = None
    trajectory: Optional[Trajectory] = None
    success: bool = False
    error: Optional[str] = None
    score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            "task_id": self.task_id,
            "question": self.question,
            "predicted_answer": self.predicted_answer,
            "success": self.success,
        }
        if self.ground_truth is not None:
            result["ground_truth"] = self.ground_truth
        if self.trajectory:
            result["trajectory"] = self.trajectory.to_dict()
        if self.error:
            result["error"] = self.error
        if self.score is not None:
            result["score"] = self.score
        if self.metadata:
            result["metadata"] = self.metadata
        return result


@dataclass
class EvaluationResult:
    """Evaluation result for a single task"""
    task_id: str
    predicted: str
    ground_truth: str
    score: float
    metric: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class RolloutSummary:
    """Summary of a complete rollout run"""
    benchmark_name: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    average_score: float
    metric: str
    total_time_seconds: float
    results_file: str
    evaluation_file: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
