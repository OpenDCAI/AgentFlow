# -*- coding: utf-8 -*-
"""
Data Models for AgentFlow Environments

This module contains dataclass definitions for trajectory data structures
used across different environment types.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Union


@dataclass
class Observation:
    """观察数据（支持文本和图片）"""
    type: str  # "text" or "image"
    content: Union[str, bytes]  # 文本内容或图片数据
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外信息（如图片路径、尺寸等）


@dataclass
class TrajectoryStep:
    """单步轨迹"""
    step_id: int
    action: str  # 工具名称
    action_input: Dict[str, Any]  # 工具参数
    observations: List[Observation] = field(default_factory=list)  # 观察结果
    thought: str = ""  # LLM的思考过程（从assistant消息提取）
    result: str = ""  # 执行结果
    status: str = "success"  # "success" or "error"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TaskTrajectory:
    """任务完整轨迹"""
    task_id: str
    question: str
    steps: List[TrajectoryStep] = field(default_factory=list)
    final_answer: str = ""
    success: bool = True
    total_steps: int = 0
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)  # 如token数、耗时等
