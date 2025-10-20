"""
通用Agent数据合成模块

该模块实现了一个可配置的数据合成pipeline，可以适配任何环境和工具组合。
核心特性：
1. 工具无关的Trajectory采样
2. 基于示例和tips的QA合成
3. 完全可配置的探索策略
"""

# 数据模型
from .models import (
    TrajectoryNode,
    Trajectory,
    SynthesizedQA
)

# 配置
from .synthesis_config import SynthesisConfig

# 核心组件
from .trajectory_sampler import GenericTrajectorySampler
from .trajectory_selector import GenericTrajectorySelector
from .qa_synthesizer import GenericQASynthesizer

# 主Pipeline
from .synthesis_pipeline import GenericDataSynthesis, main

__all__ = [
    # 数据模型
    "TrajectoryNode",
    "Trajectory",
    "SynthesizedQA",
    
    # 配置
    "SynthesisConfig",
    
    # 核心组件
    "GenericTrajectorySampler",
    "GenericTrajectorySelector",
    "GenericQASynthesizer",
    
    # 主Pipeline
    "GenericDataSynthesis",
    "main",
]

__version__ = "1.0.0"

