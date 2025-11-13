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
            base_url=os.environ.get("OPENAI_API_URL")
            or os.environ.get("OPENAI_API_BASE")
            or os.environ.get("OPENAI_BASE_URL")
            or ""
        )
    
    def select_trajectories(self, 
                           nodes: Dict[str, TrajectoryNode],
                           root_id: str,
                           seed_data: str,
                           source_id: str,
                           max_selected_traj: int = None) -> List[Trajectory]:
        """从trajectory tree中选择高质量的完整链路"""
        # 如果没有指定max_selected_traj，使用配置中的值
        if max_selected_traj is None:
            max_selected_traj = self.config.max_selected_traj
        
        print(f"\n{'='*60}")
        print(f"开始选择 Trajectories (最多选择 {max_selected_traj} 条)")
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
        selected = self._score_and_select(candidate_paths, seed_data, source_id, max_selected_traj)
        
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
                        seed_data: str,
                        source_id: str,
                        max_selected: int) -> List[Trajectory]:
        """评分并选择最好的路径"""
        # 先计算所有路径的平均observation长度
        all_avg_lengths = []
        for path in paths:
            avg_length = sum(len(node.observation) for node in path) / len(path) if path else 0
            all_avg_lengths.append(avg_length)
        
        # 计算min和max用于归一化
        min_length = min(all_avg_lengths) if all_avg_lengths else 0
        max_length = max(all_avg_lengths) if all_avg_lengths else 1
        length_range = max_length - min_length if max_length > min_length else 1
        
        scored_paths = []
        for idx, path in enumerate(paths):
            score = self._score_path(path, all_avg_lengths[idx], min_length, length_range)
            scored_paths.append((score, idx, path))
        
        # 按分数排序
        scored_paths.sort(reverse=True, key=lambda x: x[0])
        
        # 选择top-k
        selected_trajectories = []
        for rank, (score, idx, path) in enumerate(scored_paths[:max_selected], 1):
            trajectory = Trajectory(
                trajectory_id=f"{source_id}_traj_{idx}",
                nodes=path,
                seed_data=seed_data,
                source_id=source_id,
                total_depth=len(path)
            )
            selected_trajectories.append(trajectory)
            print(f"  选择 Trajectory {rank}: ID={trajectory.trajectory_id}, 深度={len(path)}, 分数={score:.2f}")
        
        return selected_trajectories
    
    def _score_path(self, path: List[TrajectoryNode], 
                    avg_obs_length: float = None,
                    min_length: float = 0,
                    length_range: float = 1) -> float:
        """为路径打分"""
        # 深度得分
        depth_score = min(len(path) / 5.0, 1.0) * 40
        
        # 信息量得分 - 使用相对归一化
        if avg_obs_length is None:
            avg_obs_length = sum(len(node.observation) for node in path) / len(path) if path else 0
        normalized_length = (avg_obs_length - min_length) / length_range if length_range > 0 else 0
        info_score = normalized_length * 30
        
        # 多样性得分
        tool_names = set()
        for node in path:
            if node.action:
                tool_names.add(node.action.get("tool_name", ""))
        diversity_score = len(tool_names) / max(len(self.config.available_tools), 1) * 30
        
        total_score = depth_score + info_score + diversity_score
        return total_score

