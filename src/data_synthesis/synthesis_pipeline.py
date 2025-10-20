"""
数据合成主Pipeline

整合trajectory采样、选择和QA合成的完整流程
"""

import json
import os
import bdb
from typing import List, Dict
from datetime import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from envs import (
    Environment,
    MathEnvironment,
    PythonEnvironment,
    RAGEnvironment,
    WebEnvironment
)
from models import TrajectoryNode, Trajectory, SynthesizedQA
from synthesis_config import SynthesisConfig
from trajectory_sampler import GenericTrajectorySampler
from trajectory_selector import GenericTrajectorySelector
from qa_synthesizer import GenericQASynthesizer


class GenericDataSynthesis:
    """
    通用数据合成主类 - 支持所有环境和工具
    """
    
    def __init__(self, config: SynthesisConfig):
        """
        初始化通用数据合成系统
        
        Args:
            config: 合成配置
        """
        self.config = config
        
        # 验证配置
        errors = config.validate()
        if errors:
            raise ValueError(f"配置错误: {', '.join(errors)}")
        
        # 创建环境
        print(f"初始化 {config.environment_mode.upper()} Environment...")
        self.environment = self._create_environment()
        
        # 创建三个组件
        self.sampler = GenericTrajectorySampler(
            environment=self.environment,
            config=config
        )
        
        self.selector = GenericTrajectorySelector(config=config)
        
        self.synthesizer = GenericQASynthesizer(config=config)
        
        # 存储结果
        self.trajectory_tree: Dict[str, TrajectoryNode] = {}
        self.selected_trajectories: List[Trajectory] = []
        self.synthesized_qas: List[SynthesizedQA] = []
    
    def _create_environment(self) -> Environment:
        """根据配置创建相应的环境"""
        mode = self.config.environment_mode.lower()
        kwargs = self.config.environment_kwargs.copy()
        kwargs['model_name'] = self.config.model_name
        
        if mode == "web":
            return WebEnvironment(**kwargs)
        elif mode == "math":
            return MathEnvironment(**kwargs)
        elif mode == "python" or mode == "py":
            return PythonEnvironment(**kwargs)
        elif mode == "rag":
            if 'rag_index' not in kwargs:
                raise ValueError("RAG环境需要提供rag_index参数")
            return RAGEnvironment(**kwargs)
        else:
            raise ValueError(f"不支持的环境模式: {mode}")
    
    def run(self, seeds: List[str]) -> List[SynthesizedQA]:
        """
        运行完整的数据合成pipeline
        
        Args:
            seeds: Seed数据列表（可以是任意类型：entity/problem/text/url等）
            
        Returns:
            合成的QA对列表
        """
        print(f"\n{'='*80}")
        print(f"🚀 通用Agent数据合成 Pipeline 启动")
        print(f"{'='*80}")
        print(f"环境模式: {self.config.environment_mode}")
        print(f"Seed说明: {self.config.seed_description or '(未指定)'}")
        print(f"可用工具: {[t['name'] for t in self.sampler.available_tools]}")
        print(f"总Seed数量: {len(seeds)}")
        print(f"模型: {self.config.model_name}")
        print(f"{'='*80}\n")
        
        all_qas = []
        
        for seed_idx, seed_data in enumerate(seeds, 1):
            print(f"\n\n{'#'*80}")
            print(f"处理 Seed {seed_idx}/{len(seeds)}")
            print(f"内容: {seed_data}")
            print(f"{'#'*80}\n")
            
            try:
                # Step 1: Trajectory Sampling
                print(f"\n📊 步骤 1/3: Trajectory Sampling")
                self.trajectory_tree = self.sampler.sample_trajectory_tree(seed_data)
                
                # Step 2: Trajectory Selection
                print(f"\n🎯 步骤 2/3: Trajectory Selection")
                self.selected_trajectories = self.selector.select_trajectories(
                    nodes=self.trajectory_tree,
                    root_id=self.sampler.root_id,
                    seed_data=seed_data
                )
                
                # Step 3: QA Synthesis
                print(f"\n✨ 步骤 3/3: QA Synthesis")
                for trajectory in self.selected_trajectories:
                    qa = self.synthesizer.synthesize_qa(trajectory)
                    if qa:
                        all_qas.append(qa)
                        self.synthesized_qas.append(qa)
                
                print(f"\n✅ Seed {seed_idx} 完成! 生成了 {len([qa for qa in all_qas if qa.metadata.get('seed_data') == seed_data])} 个QA对")
                
            except Exception as e:
                if isinstance(e, bdb.BdbQuit):
                    raise e
                print(f"\n❌ Seed {seed_idx} 失败: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\n\n{'='*80}")
        print(f"🎉 数据合成完成!")
        print(f"{'='*80}")
        print(f"总共处理: {len(seeds)} 个 Seed")
        print(f"成功生成: {len(all_qas)} 个QA对")
        print(f"{'='*80}\n")
        
        return all_qas
    
    def save_results(self, output_dir: str = "synthesis_results"):
        """保存所有结果"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存QA对
        qa_file = os.path.join(output_dir, f"synthesized_qa_{self.config.environment_mode}_{timestamp}.jsonl")
        with open(qa_file, "w", encoding="utf-8") as f:
            for qa in self.synthesized_qas:
                f.write(json.dumps(qa.to_dict(), ensure_ascii=False) + "\n")
        
        print(f"💾 QA对已保存到: {qa_file}")
        
        # 保存trajectories
        traj_file = os.path.join(output_dir, f"trajectories_{self.config.environment_mode}_{timestamp}.json")
        with open(traj_file, "w", encoding="utf-8") as f:
            trajectories_data = [traj.to_dict() for traj in self.selected_trajectories]
            json.dump(trajectories_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Trajectories已保存到: {traj_file}")
        
        # 保存配置和统计
        stats_file = os.path.join(output_dir, f"statistics_{self.config.environment_mode}_{timestamp}.json")
        stats = {
            "config": self.config.to_dict(),
            "total_qas": len(self.synthesized_qas),
            "total_trajectories": len(self.selected_trajectories),
            "total_nodes": len(self.trajectory_tree),
            "avg_trajectory_depth": sum(t.total_depth for t in self.selected_trajectories) / len(self.selected_trajectories) if self.selected_trajectories else 0,
            "timestamp": timestamp
        }
        
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"💾 统计信息已保存到: {stats_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="通用Agent数据合成系统")
    
    parser.add_argument("--config", type=str, required=True,
                       help="配置文件路径 (.json 或 .yaml)")
    parser.add_argument("--seeds", type=str, required=True,
                       help="Seed数据JSON文件路径（支持任意类型的seed：entity/problem/text/url等）")
    parser.add_argument("--output-dir", type=str, default="synthesis_results",
                       help="输出目录")
    
    args = parser.parse_args()
    
    # 加载配置
    print(f"加载配置文件: {args.config}")
    if args.config.endswith('.json'):
        config = SynthesisConfig.from_json(args.config)
    elif args.config.endswith('.yaml') or args.config.endswith('.yml'):
        config = SynthesisConfig.from_yaml(args.config)
    else:
        raise ValueError("配置文件必须是 .json 或 .yaml 格式")
    
    # 读取seed数据（简单字符串列表）
    print(f"读取 seed 数据文件: {args.seeds}")
    with open(args.seeds, "r", encoding="utf-8") as f:
        seeds = json.load(f)
        if not isinstance(seeds, list):
            raise ValueError("Seed文件格式错误：必须是字符串列表，例如: [\"seed1\", \"seed2\", \"seed3\"]")
        if not all(isinstance(s, str) for s in seeds):
            raise ValueError("Seed文件格式错误：所有seed必须是字符串")
    
    print(f"加载了 {len(seeds)} 个 seed 数据")
    
    # 创建数据合成系统
    synthesizer = GenericDataSynthesis(config=config)
    
    # 运行合成pipeline
    qas = synthesizer.run(seeds)
    
    # 保存结果
    synthesizer.save_results(output_dir=args.output_dir)
    
    print(f"\n✅ 全部完成! 共生成 {len(qas)} 个QA对")


if __name__ == "__main__":
    main()

