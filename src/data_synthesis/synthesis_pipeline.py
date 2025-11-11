"""
数据合成主Pipeline

整合trajectory采样、选择和QA合成的完整流程
"""

import json
import os
import bdb
import hashlib
from typing import List, Dict, Set

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from envs import (
    Environment,
    MathEnvironment,
    PythonEnvironment,
    RAGEnvironment,
    WebEnvironment,
    OSWorldEnvironment
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
    
    def __init__(self, config: SynthesisConfig, output_dir: str = "synthesis_results"):
        """
        初始化通用数据合成系统
        
        Args:
            config: 合成配置
            output_dir: 输出目录
        """
        self.config = config
        self.output_dir = output_dir
        
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
        
        # 初始化输出文件路径（在run时创建）
        self.qa_file_path = None
        self.traj_file_path = None
        
        # 已处理的source_id集合
        self.processed_source_ids: Set[str] = set()
    
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
        elif mode == "osworld" or mode == "gui":
            # OSWorld/GUI环境需要VM配置
            required_params = ['path_to_vm']
            missing = [p for p in required_params if p not in kwargs]
            if missing:
                raise ValueError(f"OSWorld环境需要提供以下参数: {', '.join(missing)}")
            from envs import OSWorldEnvironment
            return OSWorldEnvironment(**kwargs)
        else:
            raise ValueError(f"不支持的环境模式: {mode}")
    
    def _initialize_output_files(self):
        """初始化输出文件路径并创建输出目录"""
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 设置QA输出文件路径（固定文件名，支持断点续传）
        self.qa_file_path = os.path.join(
            self.output_dir, 
            f"synthesized_qa_{self.config.environment_mode}.jsonl"
        )
        
        # 设置trajectories输出文件路径（固定文件名，支持断点续传）
        self.traj_file_path = os.path.join(
            self.output_dir, 
            f"trajectories_{self.config.environment_mode}.jsonl"
        )
        
        print(f"💾 输出文件: {self.qa_file_path}")
        
        # 加载已处理的source_id
        self._load_processed_source_ids()
    
    def _generate_source_id(self, seed_data: str, seed_idx: int) -> str:
        """
        生成source的唯一标识
        格式: src_{index}_{hash}
        """
        # 使用seed内容的hash来保证唯一性
        content_hash = hashlib.md5(seed_data.encode('utf-8')).hexdigest()[:8]
        return f"src_{seed_idx:04d}_{content_hash}"
    
    def _load_processed_source_ids(self):
        """从已有的输出文件中加载已处理的source_id"""
        self.processed_source_ids.clear()
        
        # 从QA文件中读取已处理的source_id
        if os.path.exists(self.qa_file_path):
            try:
                with open(self.qa_file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            qa_dict = json.loads(line)
                            if "source_id" in qa_dict:
                                self.processed_source_ids.add(qa_dict["source_id"])
                
                if self.processed_source_ids:
                    print(f"🔄 发现 {len(self.processed_source_ids)} 个已处理的source，将跳过这些seed")
            except Exception as e:
                print(f"⚠️  读取已处理记录时出错: {e}")
                self.processed_source_ids.clear()
    
    def _save_qa_immediately(self, qa: SynthesizedQA):
        """立即将单个QA对追加保存到文件"""
        with open(self.qa_file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(qa.to_dict(), ensure_ascii=False) + "\n")
    
    def _save_trajectories_immediately(self, trajectories: List[Trajectory]):
        """立即将trajectories追加保存到文件"""
        with open(self.traj_file_path, "a", encoding="utf-8") as f:
            for traj in trajectories:
                f.write(json.dumps(traj.to_dict(), ensure_ascii=False) + "\n")
    
    def run(self, seeds: List[str]) -> List[SynthesizedQA]:
        """
        运行完整的数据合成pipeline
        
        Args:
            seeds: Seed数据列表（可以是任意类型：entity/problem/text/url等）
            
        Returns:
            合成的QA对列表
        """
        # 根据配置限制处理的seed数量
        if self.config.number_of_seed is not None:
            seeds = seeds[:self.config.number_of_seed]
        
        print(f"\n{'='*80}")
        print(f"🚀 通用Agent数据合成 Pipeline 启动")
        print(f"{'='*80}")
        print(f"环境模式: {self.config.environment_mode}")
        print(f"Seed说明: {self.config.seed_description or '(未指定)'}")
        print(f"可用工具: {[t['name'] for t in self.sampler.available_tools]}")
        print(f"总Seed数量: {len(seeds)}")
        print(f"模型: {self.config.model_name}")
        print(f"{'='*80}\n")
        
        # 初始化输出文件
        self._initialize_output_files()
        
        all_qas = []
        skipped_count = 0
        
        for seed_idx, seed_data in enumerate(seeds, 1):
            # 为每个seed生成唯一的source_id
            source_id = self._generate_source_id(seed_data, seed_idx)
            
            # 检查是否已处理
            if source_id in self.processed_source_ids:
                skipped_count += 1
                print(f"\n⏭️  跳过 Seed {seed_idx}/{len(seeds)} (已处理: {source_id})")
                continue
            
            print(f"\n\n{'#'*80}")
            print(f"处理 Seed {seed_idx}/{len(seeds)}")
            print(f"Source ID: {source_id}")
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
                    seed_data=seed_data,
                    source_id=source_id,
                    max_selected_traj=self.config.max_selected_traj
                )
                
                # Step 3: QA Synthesis
                print(f"\n✨ 步骤 3/3: QA Synthesis")
                for qa_idx, trajectory in enumerate(self.selected_trajectories):
                    qa = self.synthesizer.synthesize_qa(trajectory, qa_idx)
                    if qa:
                        all_qas.append(qa)
                        self.synthesized_qas.append(qa)
                        # 立即保存生成的QA对
                        self._save_qa_immediately(qa)
                
                # 立即保存该seed的所有trajectories
                if self.selected_trajectories:
                    self._save_trajectories_immediately(self.selected_trajectories)
                
                print(f"\n✅ Seed {seed_idx} 完成! 生成了 {len([qa for qa in all_qas if qa.source_id == source_id])} 个QA对")
                
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
        print(f"总Seed数量: {len(seeds)} 个")
        print(f"已跳过: {skipped_count} 个")
        print(f"新处理: {len(seeds) - skipped_count} 个")
        print(f"成功生成: {len(all_qas)} 个QA对")
        print(f"{'='*80}\n")
        
        return all_qas
    
    def save_results(self):
        """显示结果保存位置（QA对和trajectories已实时保存）"""
        if not self.qa_file_path:
            print("⚠️  警告: 没有运行过pipeline，无法保存结果")
            return
        
        print(f"💾 QA对已保存到: {self.qa_file_path}")
        print(f"💾 Trajectories已保存到: {self.traj_file_path}")


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
    synthesizer = GenericDataSynthesis(config=config, output_dir=args.output_dir)
    
    # 运行合成pipeline
    qas = synthesizer.run(seeds)
    
    # 保存结果（trajectories和统计信息，QA对已实时保存）
    synthesizer.save_results()
    
    print(f"\n✅ 全部完成! 共生成 {len(qas)} 个QA对")


if __name__ == "__main__":
    main()

