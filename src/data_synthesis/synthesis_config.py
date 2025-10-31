"""
数据合成配置管理模块
支持通过配置文件指定工具、示例QA和生成tips
"""

import json
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class SynthesisConfig:
    """数据合成配置类"""
    
    # 环境配置
    environment_mode: str = "web"  # web, math, python, rag等
    environment_kwargs: Dict[str, Any] = field(default_factory=dict)
    
    # 可用工具列表（如果为空，使用环境默认工具）
    available_tools: List[str] = field(default_factory=list)
    
    # QA示例（用于指导合成方向）
    qa_examples: List[Dict[str, str]] = field(default_factory=list)
    
    # Trajectory采样提示（引导agent探索方向和策略）
    sampling_tips: str = ""
    
    # QA合成提示（自然语言描述期望的数据特征）
    synthesis_tips: str = ""
    
    # Seed起点配置
    seed_description: str = ""  # 对seed的描述，用于生成更好的prompt（例如："实体名称"、"数学问题"、"URL链接"等）
    
    # 模型配置
    model_name: str = "gpt-4.1-2025-04-14"
    
    # Trajectory采样配置
    max_depth: int = 5
    branching_factor: int = 2
    depth_threshold: int = 3
    
    # Trajectory选择配置
    max_trajectories: int = 5
    min_depth: int = 2
    max_selected_traj: int = 3  # 每次选择的trajectory数量上限
    
    # 其他配置
    max_retries: int = 3
    
    # 并行处理配置
    max_workers: int = 1  # 并行处理的worker数量，1表示串行处理
    
    # Seed处理数量限制
    number_of_seed: Optional[int] = None  # 只处理前N个seed，None表示处理所有seed
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'SynthesisConfig':
        """从字典创建配置"""
        return cls(**config_dict)
    
    @classmethod
    def from_json(cls, json_path: str) -> 'SynthesisConfig':
        """从JSON文件加载配置"""
        with open(json_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'SynthesisConfig':
        """从YAML文件加载配置"""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "environment_mode": self.environment_mode,
            "environment_kwargs": self.environment_kwargs,
            "available_tools": self.available_tools,
            "qa_examples": self.qa_examples,
            "sampling_tips": self.sampling_tips,
            "synthesis_tips": self.synthesis_tips,
            "seed_description": self.seed_description,
            "model_name": self.model_name,
            "max_depth": self.max_depth,
            "branching_factor": self.branching_factor,
            "depth_threshold": self.depth_threshold,
            "max_trajectories": self.max_trajectories,
            "min_depth": self.min_depth,
            "max_selected_traj": self.max_selected_traj,
            "max_retries": self.max_retries,
            "max_workers": self.max_workers,
            "number_of_seed": self.number_of_seed
        }
    
    def to_json(self, json_path: str):
        """保存为JSON文件"""
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    def to_yaml(self, yaml_path: str):
        """保存为YAML文件"""
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, allow_unicode=True, default_flow_style=False)
    
    def validate(self) -> List[str]:
        """验证配置的有效性，返回错误列表"""
        errors = []
        
        if not self.environment_mode:
            errors.append("environment_mode不能为空")
        
        if self.max_depth < 1:
            errors.append("max_depth必须大于0")
        
        if self.branching_factor < 1:
            errors.append("branching_factor必须大于0")
        
        if self.max_trajectories < 1:
            errors.append("max_trajectories必须大于0")
        
        if self.max_selected_traj < 1:
            errors.append("max_selected_traj必须大于0")
        
        if self.min_depth < 1:
            errors.append("min_depth必须大于0")
        
        if self.min_depth > self.max_depth:
            errors.append("min_depth不能大于max_depth")
        
        return errors

