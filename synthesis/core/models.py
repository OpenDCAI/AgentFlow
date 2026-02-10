"""
Data models for RAG synthesis pipeline
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional


@dataclass
class TrajectoryNode:
    """Single node in a trajectory tree"""
    node_id: str
    observation: str
    intent: str
    action: Optional[Dict[str, Any]] = None
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    depth: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return asdict(self)


@dataclass
class Trajectory:
    """Complete trajectory chain"""
    trajectory_id: str
    nodes: List[TrajectoryNode]
    seed_data: str
    total_depth: int
    source_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "trajectory_id": self.trajectory_id,
            "source_id": self.source_id,
            "seed_data": self.seed_data,
            "total_depth": self.total_depth,
            "nodes": [node.to_dict() for node in self.nodes]
        }


@dataclass
class SynthesizedQA:
    """Synthesized question-answer pair"""
    question: str
    answer: str
    trajectory_id: str
    reasoning_steps: List[Dict[str, str]]
    source_id: str = ""
    qa_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SynthesizedQA':
        """Create instance from dictionary"""
        data = dict(data or {})
        data.pop("negative_aspect", None)
        return cls(**data)
