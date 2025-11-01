"""
数据模型定义

包含trajectory和QA合成中使用的所有数据类
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional


@dataclass
class TrajectoryNode:
    """Trajectory tree中的单个节点"""
    node_id: str
    observation: str
    intent: str
    action: Optional[Dict[str, Any]] = None
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    depth: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)


@dataclass
class Trajectory:
    """完整的trajectory链路"""
    trajectory_id: str
    nodes: List[TrajectoryNode]
    seed_data: str
    total_depth: int
    source_id: str = ""  # 添加source_id用于追溯到原始seed
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "trajectory_id": self.trajectory_id,
            "source_id": self.source_id,
            "seed_data": self.seed_data,
            "total_depth": self.total_depth,
            "nodes": [node.to_dict() for node in self.nodes]
        }


@dataclass
class SynthesizedQA:
    """合成的问答对"""
    question: str
    answer: str
    trajectory_id: str
    reasoning_steps: List[Dict[str, str]]
    source_id: str = ""  # 添加source_id用于追溯到原始seed
    qa_id: str = ""  # 添加qa_id作为QA的唯一标识
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)

