"""
Trajectory选择器

负责从trajectory tree中选择高质量的完整链路
"""

import openai
import os
from typing import Dict, List

from models import TrajectoryNode, Trajectory
from synthesis_config import SynthesisConfig


class GenericTrajectorySelector:
    """
    通用Trajectory选择器
    """
    
    def __init__(self, config: SynthesisConfig):
        """初始化选择器"""
        self.config = config
        
        self.client = openai.OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_API_URL", os.environ.get("OPENAI_API_BASE", ""))
        )
    
    def select_trajectories(self, 
                           nodes: Dict[str, TrajectoryNode],
                           root_id: str,
                           seed_data: str) -> List[Trajectory]:
        """从trajectory tree中选择高质量的完整链路"""
        print(f"\n{'='*60}")
        print(f"开始选择 Trajectories")
        print(f"{'='*60}\n")
        
        # 1. 找到所有叶子节点
        leaf_nodes = [node for node in nodes.values() if not node.children_ids]
        print(f"找到 {len(leaf_nodes)} 个叶子节点")
        
        # 2. 筛选满足最小深度的叶子节点
        valid_leaves = [node for node in leaf_nodes if node.depth >= self.config.min_depth]
        print(f"满足最小深度({self.config.min_depth})的叶子节点: {len(valid_leaves)}")
        
        if not valid_leaves:
            print("⚠️  没有找到满足深度要求的trajectory")
            return []
        
        # 3. 从每个叶子节点回溯到根节点
        candidate_paths = []
        for leaf in valid_leaves:
            path = self._build_path_to_root(leaf, nodes, root_id)
            if path:
                candidate_paths.append(path)
        
        print(f"构建了 {len(candidate_paths)} 条候选路径")
        
        # 4. 评分并选择
        selected = self._score_and_select(candidate_paths, seed_data)
        
        print(f"\n✅ 选择了 {len(selected)} 条trajectories")
        
        return selected
    
    def _build_path_to_root(self, 
                           leaf: TrajectoryNode,
                           nodes: Dict[str, TrajectoryNode],
                           root_id: str) -> List[TrajectoryNode]:
        """从叶子节点回溯到根节点"""
        path = []
        current = leaf
        
        while current.node_id != root_id:
            path.append(current)
            if current.parent_id is None:
                break
            current = nodes[current.parent_id]
        
        path.reverse()
        return path
    
    def _score_and_select(self, 
                         paths: List[List[TrajectoryNode]],
                         seed_data: str) -> List[Trajectory]:
        """评分并选择最好的路径"""
        scored_paths = []
        
        for idx, path in enumerate(paths):
            score = self._score_path(path)
            scored_paths.append((score, idx, path))
        
        # 按分数排序
        scored_paths.sort(reverse=True, key=lambda x: x[0])
        
        # 选择top-k
        selected_trajectories = []
        for rank, (score, idx, path) in enumerate(scored_paths[:self.config.max_trajectories], 1):
            trajectory = Trajectory(
                trajectory_id=f"traj_{idx}",
                nodes=path,
                seed_data=seed_data,
                total_depth=len(path)
            )
            selected_trajectories.append(trajectory)
            print(f"  选择 Trajectory {rank}: 深度={len(path)}, 分数={score:.2f}")
        
        return selected_trajectories
    
    def _score_path(self, path: List[TrajectoryNode]) -> float:
        """为路径打分"""
        # 深度得分
        depth_score = min(len(path) / 5.0, 1.0) * 40
        
        # 信息量得分
        avg_obs_length = sum(len(node.observation) for node in path) / len(path) if path else 0
        info_score = min(avg_obs_length / 1000, 1.0) * 30
        
        # 多样性得分
        tool_names = set()
        for node in path:
            if node.action:
                tool_names.add(node.action.get("tool_name", ""))
        diversity_score = len(tool_names) / max(len(self.config.available_tools), 1) * 30
        
        total_score = depth_score + info_score + diversity_score
        return total_score

