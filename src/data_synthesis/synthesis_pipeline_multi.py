"""
数据合成主Pipeline

整合trajectory采样、选择和QA合成的完整流程
"""

import json
import os
import bdb
import hashlib
from typing import List, Dict, Tuple, Set
from concurrent.futures import ProcessPoolExecutor, as_completed
from threading import Lock

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
from models import TrajectoryNode, Trajectory, SynthesizedQA, SynthesizedTask
from synthesis_config import SynthesisConfig
from trajectory_sampler import GenericTrajectorySampler
from trajectory_selector import GenericTrajectorySelector
from qa_synthesizer import GenericQASynthesizer
from task_synthesizer import OSWorldTaskSynthesizer


def process_single_seed(
    seed_idx: int,
    seed_data: str, 
    config: SynthesisConfig
) -> Tuple[int, str, List[Dict], List[Dict], str]:
    """
    处理单个seed（用于并行处理）
    
    Args:
        seed_idx: seed索引
        seed_data: seed数据
        config: 合成配置
        
    Returns:
        (seed_idx, source_id, outputs_list, trajectories_list, error_msg)
        outputs_list可以是QA对或Task（取决于output_format配置）
    """
    source_id = _generate_source_id(seed_data, seed_idx)
    
    print(f"\n{'#'*80}")
    print(f"Worker处理 Seed {seed_idx}")
    print(f"Source ID: {source_id}")
    print(f"内容: {seed_data[:100]}{'...' if len(seed_data) > 100 else ''}")
    print(f"输出格式: {config.output_format}")
    print(f"{'#'*80}\n")
    
    try:
        # 创建环境和组件
        environment = _create_environment(config)
        
        sampler = GenericTrajectorySampler(
            environment=environment,
            config=config
        )
        
        selector = GenericTrajectorySelector(config=config)
        
        # 根据输出格式选择合成器
        if config.output_format == "task":
            synthesizer = OSWorldTaskSynthesizer(config=config)
            print(f"📦 使用OSWorld任务合成器")
        else:
            synthesizer = GenericQASynthesizer(config=config)
            print(f"📦 使用QA合成器")
        
        # Step 1: Trajectory Sampling
        print(f"\n📊 步骤 1/3: Trajectory Sampling")
        trajectory_tree = sampler.sample_trajectory_tree(seed_data)
        
        # Step 2: Trajectory Selection
        print(f"\n🎯 步骤 2/3: Trajectory Selection")
        selected_trajectories = selector.select_trajectories(
            nodes=trajectory_tree,
            root_id=sampler.root_id,
            seed_data=seed_data,
            source_id=source_id,
            max_selected_traj=config.max_selected_traj
        )
        
        # Step 3: 数据合成（QA或Task）
        if config.output_format == "task":
            print(f"\n✨ 步骤 3/3: OSWorld Task Synthesis")
            outputs = []
            for task_idx, trajectory in enumerate(selected_trajectories):
                task = synthesizer.synthesize_task(trajectory, task_idx)
                if task:
                    outputs.append(task.to_dict())
            output_type = "任务"
        else:
            print(f"\n✨ 步骤 3/3: QA Synthesis")
            outputs = []
            for qa_idx, trajectory in enumerate(selected_trajectories):
                qa = synthesizer.synthesize_qa(trajectory, qa_idx)
                if qa:
                    outputs.append(qa.to_dict())
            output_type = "QA对"
        
        trajectories_data = [traj.to_dict() for traj in selected_trajectories]
        
        print(f"\n✅ Seed {seed_idx} 完成! 生成了 {len(outputs)} 个{output_type}")
        
        return (seed_idx, source_id, outputs, trajectories_data, "")
        
    except Exception as e:
        error_msg = f"❌ Seed {seed_idx} 失败: {str(e)}"
        print(f"\n{error_msg}")
        import traceback
        traceback.print_exc()
        return (seed_idx, source_id, [], [], error_msg)


def _generate_source_id(seed_data: str, seed_idx: int) -> str:
    """生成source的唯一标识"""
    content_hash = hashlib.md5(seed_data.encode('utf-8')).hexdigest()[:8]
    return f"src_{seed_idx:04d}_{content_hash}"


def _create_environment(config: SynthesisConfig):
    """根据配置创建相应的环境"""
    mode = config.environment_mode.lower()
    kwargs = config.environment_kwargs.copy()
    kwargs['model_name'] = config.model_name
    
    if mode == "web":
        from envs import WebEnvironment
        return WebEnvironment(**kwargs)
    elif mode == "math":
        from envs import MathEnvironment
        return MathEnvironment(**kwargs)
    elif mode == "python" or mode == "py":
        from envs import PythonEnvironment
        return PythonEnvironment(**kwargs)
    elif mode == "rag":
        if 'rag_index' not in kwargs:
            raise ValueError("RAG环境需要提供rag_index参数")
        from envs import RAGEnvironment
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
        
        # 根据输出格式选择合成器
        if config.output_format == "task":
            self.synthesizer = OSWorldTaskSynthesizer(config=config)
            print(f"使用OSWorld任务合成器（输出格式：task）")
        else:
            self.synthesizer = GenericQASynthesizer(config=config)
            print(f"使用QA合成器（输出格式：qa）")
        
        # 存储结果
        self.trajectory_tree: Dict[str, TrajectoryNode] = {}
        self.selected_trajectories: List[Trajectory] = []
        self.synthesized_qas: List[SynthesizedQA] = []  # QA格式
        self.synthesized_tasks: List[SynthesizedTask] = []  # Task格式
        
        # 初始化输出文件路径（在run时创建）
        self.qa_file_path = None
        self.traj_file_path = None
        
        # 已处理的source_id集合
        self.processed_source_ids: Set[str] = set()
        
        # 文件写入锁（用于并行处理时的线程安全）
        self.file_lock = Lock()
    
    def _create_environment(self) -> Environment:
        """根据配置创建相应的环境"""
        return _create_environment(self.config)
    
    def _initialize_output_files(self):
        """初始化输出文件路径并创建输出目录"""
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 根据输出格式设置文件路径
        if self.config.output_format == "task":
            # OSWorld任务格式
            self.qa_file_path = os.path.join(
                self.output_dir, 
                f"synthesized_tasks_{self.config.environment_mode}.jsonl"
            )
        else:
            # QA对格式
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
        print(f"💾 输出格式: {self.config.output_format}")
        
        # 加载已处理的source_id
        self._load_processed_source_ids()
    
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
    
    def _save_qa_immediately(self, qa_dict: Dict):
        """立即将单个QA对追加保存到文件（线程安全）"""
        with self.file_lock:
            with open(self.qa_file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(qa_dict, ensure_ascii=False) + "\n")
    
    def _save_trajectories_immediately(self, trajectories_data: List[Dict]):
        """立即将trajectories追加保存到文件（线程安全）"""
        with self.file_lock:
            with open(self.traj_file_path, "a", encoding="utf-8") as f:
                for traj in trajectories_data:
                    f.write(json.dumps(traj, ensure_ascii=False) + "\n")
    
    def run(self, seeds: List[str]) -> List[Dict]:
        """
        运行完整的数据合成pipeline（支持并行处理）
        
        Args:
            seeds: Seed数据列表（可以是任意类型：entity/problem/text/url等）
            
        Returns:
            合成的QA对字典列表
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
        print(f"并行度: {self.config.max_workers} workers")
        print(f"模型: {self.config.model_name}")
        print(f"{'='*80}\n")
        
        # 初始化输出文件
        self._initialize_output_files()
        
        all_qas = []
        all_trajectories = []
        skipped_count = 0
        
        # 如果并行度为1，使用串行处理
        if self.config.max_workers == 1:
            print("⚡ 使用串行处理模式")
            for seed_idx, seed_data in enumerate(seeds, 1):
                # 生成source_id并检查是否已处理
                source_id = _generate_source_id(seed_data, seed_idx)
                if source_id in self.processed_source_ids:
                    skipped_count += 1
                    print(f"\n⏭️  跳过 Seed {seed_idx}/{len(seeds)} (已处理: {source_id})")
                    continue
                
                result = process_single_seed(seed_idx, seed_data, self.config)
                seed_idx, source_id, qas, trajectories, error = result
                
                if error:
                    print(f"\n{error}")
                    continue
                
                # 保存QA对
                for qa_dict in qas:
                    all_qas.append(qa_dict)
                    self._save_qa_immediately(qa_dict)
                
                # 立即保存该seed的trajectories
                if trajectories:
                    self._save_trajectories_immediately(trajectories)
                
                # 保存trajectories到内存中
                all_trajectories.extend(trajectories)
                
        else:
            # 并行处理模式
            print(f"⚡ 使用并行处理模式（{self.config.max_workers} workers）")
            
            # 过滤掉已处理的seed
            seeds_to_process = []
            for seed_idx, seed_data in enumerate(seeds, 1):
                source_id = _generate_source_id(seed_data, seed_idx)
                if source_id in self.processed_source_ids:
                    skipped_count += 1
                    print(f"\n⏭️  跳过 Seed {seed_idx}/{len(seeds)} (已处理: {source_id})")
                else:
                    seeds_to_process.append((seed_idx, seed_data))
            
            if not seeds_to_process:
                print("\n所有seed都已处理，无需继续")
            else:
                with ProcessPoolExecutor(max_workers=self.config.max_workers) as executor:
                    # 提交所有任务
                    future_to_seed = {
                        executor.submit(process_single_seed, seed_idx, seed_data, self.config): (seed_idx, seed_data)
                        for seed_idx, seed_data in seeds_to_process
                    }
                    
                    # 收集结果（按完成顺序）
                    completed = 0
                    for future in as_completed(future_to_seed):
                        seed_idx, seed_data = future_to_seed[future]
                        completed += 1
                        
                        try:
                            result = future.result()
                            seed_idx, source_id, qas, trajectories, error = result
                            
                            if error:
                                print(f"\n{error}")
                                continue
                            
                            # 保存QA对
                            for qa_dict in qas:
                                all_qas.append(qa_dict)
                                self._save_qa_immediately(qa_dict)
                            
                            # 立即保存该seed的trajectories
                            if trajectories:
                                self._save_trajectories_immediately(trajectories)
                            
                            # 保存trajectories到内存中
                            all_trajectories.extend(trajectories)
                            
                            print(f"\n📊 进度: {completed}/{len(seeds_to_process)} seeds 已完成")
                            
                        except Exception as e:
                            print(f"\n❌ Seed {seed_idx} 处理失败: {str(e)}")
                            import traceback
                            traceback.print_exc()
        
        # 保存到实例变量（用于统计）
        self.synthesized_qas = [SynthesizedQA.from_dict(qa) for qa in all_qas]
        self.selected_trajectories = [Trajectory.from_dict(traj) for traj in all_trajectories]
        
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

