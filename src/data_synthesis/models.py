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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SynthesizedQA':
        """从字典创建实例"""
        return cls(**data)


@dataclass
class SynthesizedTask:
    """合成的OSWorld格式任务（可执行+可评估）"""
    id: str  # 任务ID
    question: str  # 任务指令
    config: List[Dict[str, Any]]  # 初始化配置
    evaluator: Dict[str, Any]  # 评估器配置
    trajectory_id: str  # 关联的轨迹ID
    source_id: str = ""  # 原始seed标识
    answer: Optional[float] = None  # 预期评估得分（可选）
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为OSWorld格式的字典"""
        result = {
            "id": self.id,
            "question": self.question,
            "config": self.config,
            "evaluator": self.evaluator
        }
        
        # answer字段仅在设置时包含
        if self.answer is not None:
            result["answer"] = self.answer
        
        # metadata单独存储（不包含在OSWorld标准格式中）
        if self.metadata:
            result["metadata"] = self.metadata
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SynthesizedTask':
        """从字典创建实例"""
        return cls(
            id=data["id"],
            question=data["question"],
            config=data.get("config", []),
            evaluator=data.get("evaluator", {}),
            trajectory_id=data.get("trajectory_id", ""),
            source_id=data.get("source_id", ""),
            answer=data.get("answer"),
            metadata=data.get("metadata", {})
        )

