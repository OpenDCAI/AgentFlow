"""
探索式GUI数据合成Pipeline

与synthesis_pipeline的核心区别：
1. 探索导向：从抽象seed出发自由探索，不预设任务
2. 发现总结：从探索轨迹中"发现"和"总结"出任务/QA
3. 丰富记录：保存完整的探索过程（截图、a11y树等）
"""

import json
import os
import hashlib
from typing import List, Dict, Set

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from envs import OSWorldEnvironment
from models import Trajectory, TrajectoryNode
from synthesis_config import SynthesisConfig
from exploration_sampler import GUIExplorationSampler
from trajectory_selector import GenericTrajectorySelector
from exploration_summarizer import ExplorationSummarizer


class ExplorationDataSynthesis:
    """
    探索式GUI数据合成主类
    
    工作流程：
    1. 探索采样：从抽象seed出发，在GUI环境中自由探索
    2. 轨迹选择：选择有价值的探索轨迹
    3. 总结提炼：从探索中发现和总结出任务/QA
    """
    
    def __init__(self, config: SynthesisConfig, output_dir: str = "exploration_results"):
        """
        初始化探索式数据合成系统
        
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
        
        # 确保是OSWorld环境
        if config.environment_mode.lower() not in ["osworld", "gui"]:
            raise ValueError(f"探索式合成只支持OSWorld环境，当前: {config.environment_mode}")
        
        # 创建OSWorld环境
        print(f"初始化 OSWorld Environment（探索模式）...")
        self.environment = self._create_osworld_environment()
        
        # 创建三个组件
        self.exploration_sampler = GUIExplorationSampler(
            environment=self.environment,
            config=config
        )
        
        self.trajectory_selector = GenericTrajectorySelector(config=config)
        
        self.summarizer = ExplorationSummarizer(config=config)
        
        # 存储结果
        self.exploration_trees: List[Dict] = []  # 完整的探索树
        self.selected_trajectories: List[Trajectory] = []
        self.synthesized_outputs: List[Dict] = []  # QA或Task
        
        # 初始化输出文件路径
        self.output_file_path = None
        self.exploration_trees_path = None
        
        # 已处理的source_id集合
        self.processed_source_ids: Set[str] = set()
    
    def _create_osworld_environment(self) -> OSWorldEnvironment:
        """创建OSWorld环境"""
        kwargs = self.config.environment_kwargs.copy()
        kwargs['model_name'] = self.config.model_name
        
        required_params = ['path_to_vm']
        missing = [p for p in required_params if p not in kwargs]
        if missing:
            raise ValueError(f"OSWorld环境需要提供以下参数: {', '.join(missing)}")
        
        return OSWorldEnvironment(**kwargs)
    
    def _initialize_output_files(self):
        """初始化输出文件路径"""
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 根据输出格式设置文件名
        if self.config.output_format == "task":
            self.output_file_path = os.path.join(
                self.output_dir,
                "exploration_tasks.jsonl"
            )
        else:
            self.output_file_path = os.path.join(
                self.output_dir,
                "exploration_qa.jsonl"
            )
        
        # 探索树保存路径
        self.exploration_trees_path = os.path.join(
            self.output_dir,
            "exploration_trees.jsonl"
        )
        
        print(f"💾 输出文件:")
        print(f"   数据: {self.output_file_path}")
        print(f"   探索树: {self.exploration_trees_path}")
        
        # 加载已处理的source_id
        self._load_processed_source_ids()
    
    def _load_processed_source_ids(self):
        """加载已处理的source_id（支持断点续传）"""
        self.processed_source_ids.clear()
        
        if os.path.exists(self.output_file_path):
            try:
                with open(self.output_file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            if "source_id" in data:
                                self.processed_source_ids.add(data["source_id"])
                
                if self.processed_source_ids:
                    print(f"🔄 发现 {len(self.processed_source_ids)} 个已处理的探索，将跳过")
            except Exception as e:
                print(f"⚠️  读取已处理记录时出错: {e}")
                self.processed_source_ids.clear()
    
    def _generate_source_id(self, exploration_seed: str, seed_idx: int) -> str:
        """生成source_id"""
        content_hash = hashlib.md5(exploration_seed.encode('utf-8')).hexdigest()[:8]
        return f"explore_{seed_idx:04d}_{content_hash}"
    
    def run(self, exploration_seeds: List[str]) -> List[Dict]:
        """
        运行探索式数据合成pipeline
        
        Args:
            exploration_seeds: 探索方向列表（抽象的）
            
        Returns:
            合成的数据列表（QA或Task）
        """
        # 限制处理数量
        if self.config.number_of_seed is not None:
            exploration_seeds = exploration_seeds[:self.config.number_of_seed]
        
        print(f"\n{'='*80}")
        print(f"🚀 探索式GUI数据合成 Pipeline 启动")
        print(f"{'='*80}")
        print(f"探索模式: {self.config.output_format}")
        print(f"探索方向数: {len(exploration_seeds)}")
        print(f"可用工具: {[t['name'] for t in self.exploration_sampler.available_tools]}")
        print(f"模型: {self.config.model_name}")
        print(f"{'='*80}\n")
        
        # 初始化输出文件
        self._initialize_output_files()
        
        # 启动环境（参考 run_osworld.py line 757）
        print("🔧 启动OSWorld环境...")
        self.environment.env_start()
        print("   ✓ 环境启动成功")
        
        all_outputs = []
        skipped_count = 0
        
        try:
            for seed_idx, exploration_seed in enumerate(exploration_seeds, 1):
                # 生成source_id
                source_id = self._generate_source_id(exploration_seed, seed_idx)
                
                # 检查是否已处理
                if source_id in self.processed_source_ids:
                    skipped_count += 1
                    print(f"\n⏭️  跳过探索 {seed_idx}/{len(exploration_seeds)} (已处理: {source_id})")
                    continue
                
                print(f"\n\n{'#'*80}")
                print(f"处理探索 {seed_idx}/{len(exploration_seeds)}")
                print(f"Source ID: {source_id}")
                print(f"探索方向: {exploration_seed}")
                print(f"{'#'*80}\n")
                
                try:
                    # 步骤1: 探索采样
                    print(f"\n🔍 步骤 1/3: 探索式Trajectory Sampling")
                    print(f"开始在GUI环境中自由探索...")
                    
                    # 获取任务输出目录（参考 run_osworld.py line 190）
                    task_output_dir = self.environment.get_task_output_dir(
                        self.output_dir, 
                        source_id, 
                        self.config.model_name
                    )
                    
                    if task_output_dir:
                        print(f"   任务输出目录: {task_output_dir}")
                    
                    # 初始化环境（重置VM状态）
                    # 探索模式不需要真实的evaluator，提供一个空的占位符
                    # 注意：evaluator 应该在 metadata 中（参考 desktop_env.py line 359）
                    # 使用 infeasible 函数作为占位符（metrics/__init__.py line 159）
                    dummy_task = {
                        "id": source_id,
                        "question": exploration_seed,
                        "config": [],  # 无初始化配置
                        "metadata": {
                            "evaluator": {
                                "func": "infeasible",
                                "result": [],
                                "expected": []
                            }
                        }
                    }
                    
                    # 初始化任务并获取初始观察（参考 run_osworld.py line 196）
                    initial_obs = self.environment.env_task_init(dummy_task)
                    
                    if initial_obs:
                        print(f"   ✓ 获得初始观察")
                    
                    # 执行探索
                    exploration_tree = self.exploration_sampler.sample_exploration_tree(
                        exploration_seed
                    )
                    
                    # 保存探索树
                    exploration_tree_file = os.path.join(
                        self.output_dir,
                        f"tree_{source_id}.json"
                    )
                    self.exploration_sampler.save_exploration_tree(
                        exploration_tree_file,
                        exploration_seed
                    )
                    
                    # 步骤2: 轨迹选择
                    print(f"\n🎯 步骤 2/3: Trajectory Selection")
                    selected_trajectories = self.trajectory_selector.select_trajectories(
                        nodes=exploration_tree,
                        root_id=self.exploration_sampler.root_id,
                        seed_data=exploration_seed,
                        source_id=source_id,
                        max_selected_traj=self.config.max_selected_traj
                    )
                    
                    print(f"   选出 {len(selected_trajectories)} 条有价值的轨迹")
                    
                    # 步骤3: 总结提炼
                    print(f"\n📝 步骤 3/3: 探索总结与提炼")
                    
                    for traj_idx, trajectory in enumerate(selected_trajectories):
                        if self.config.output_format == "task":
                            # 总结为任务
                            output = self.summarizer.summarize_to_task(trajectory, traj_idx)
                        else:
                            # 总结为QA
                            output = self.summarizer.summarize_to_qa(trajectory, traj_idx)
                        
                        if output:
                            output_dict = output.to_dict()
                            all_outputs.append(output_dict)
                            
                            # 立即保存
                            with open(self.output_file_path, "a", encoding="utf-8") as f:
                                f.write(json.dumps(output_dict, ensure_ascii=False) + "\n")
                    
                    print(f"\n✅ 探索 {seed_idx} 完成! 生成了 {len(selected_trajectories)} 个数据")
                    
                    # 结束任务（参考 run_osworld.py line 282-289）
                    try:
                        self.environment.env_task_end(
                            task_id=source_id,
                            task_output_dir=task_output_dir,
                            final_answer="exploration_completed"
                        )
                        print(f"   ✓ 任务 {source_id} 已清理")
                    except Exception as e:
                        print(f"   ⚠️  警告: 清理任务失败: {e}")
                    
                except Exception as e:
                    print(f"\n❌ 探索 {seed_idx} 失败: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    
                    # 尝试清理（参考 run_osworld.py finally块）
                    try:
                        # 尝试获取task_output_dir（如果失败则为None）
                        try:
                            cleanup_output_dir = self.environment.get_task_output_dir(
                                self.output_dir, 
                                source_id, 
                                self.config.model_name
                            )
                        except:
                            cleanup_output_dir = None
                        
                        self.environment.env_task_end(
                            task_id=source_id,
                            task_output_dir=cleanup_output_dir,
                            final_answer=""
                        )
                    except Exception as cleanup_error:
                        print(f"   ⚠️  警告: 清理失败: {cleanup_error}")
                    
                    continue
        
        finally:
            # 关闭环境（参考 run_osworld.py line 811-817）
            try:
                print(f"\n🧹 关闭OSWorld环境...")
                self.environment.env_close()
                print(f"   ✓ 环境关闭成功")
            except Exception as cleanup_error:
                print(f"   ⚠️  警告: 关闭环境失败: {cleanup_error}")
        
        print(f"\n\n{'='*80}")
        print(f"🎉 探索式数据合成完成!")
        print(f"{'='*80}")
        print(f"总探索数: {len(exploration_seeds)}")
        print(f"已跳过: {skipped_count}")
        print(f"新处理: {len(exploration_seeds) - skipped_count}")
        print(f"成功生成: {len(all_outputs)} 个数据")
        print(f"{'='*80}\n")
        
        return all_outputs


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="探索式GUI数据合成系统")
    
    parser.add_argument("--config", type=str, required=True,
                       help="配置文件路径")
    parser.add_argument("--seeds", type=str, required=True,
                       help="探索方向seed文件（JSON格式）")
    parser.add_argument("--output-dir", type=str, default="exploration_results",
                       help="输出目录")
    
    args = parser.parse_args()
    
    # 加载配置
    print(f"加载配置文件: {args.config}")
    if args.config.endswith('.json'):
        from synthesis_config import SynthesisConfig
        config = SynthesisConfig.from_json(args.config)
    else:
        raise ValueError("配置文件必须是 .json 格式")
    
    # 读取探索方向seeds
    print(f"读取探索方向: {args.seeds}")
    with open(args.seeds, "r", encoding="utf-8") as f:
        exploration_seeds = json.load(f)
        if not isinstance(exploration_seeds, list):
            raise ValueError("Seeds文件必须是字符串列表")
        if not all(isinstance(s, str) for s in exploration_seeds):
            raise ValueError("所有seed必须是字符串")
    
    print(f"加载了 {len(exploration_seeds)} 个探索方向")
    
    # 创建探索式合成系统
    synthesizer = ExplorationDataSynthesis(
        config=config,
        output_dir=args.output_dir
    )
    
    # 运行探索pipeline
    outputs = synthesizer.run(exploration_seeds)
    
    print(f"\n✅ 全部完成! 共生成 {len(outputs)} 个数据")


if __name__ == "__main__":
    main()

