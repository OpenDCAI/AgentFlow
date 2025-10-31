"""
追溯工具 - 用于追溯QA到原始seed的工具函数

提供便捷的函数来追溯数据血统
"""

import json
from typing import Dict, List, Optional


class DataTracer:
    """数据追溯器 - 支持从QA追溯到Source"""
    
    def __init__(self, qa_file: str, trajectory_file: str):
        """
        初始化追溯器
        
        Args:
            qa_file: QA数据文件路径 (.jsonl)
            trajectory_file: Trajectory数据文件路径 (.json)
        """
        self.qa_file = qa_file
        self.trajectory_file = trajectory_file
        self._qa_cache = None
        self._trajectory_cache = None
    
    def _load_qas(self) -> List[Dict]:
        """加载所有QA数据"""
        if self._qa_cache is None:
            self._qa_cache = []
            with open(self.qa_file, 'r', encoding='utf-8') as f:
                for line in f:
                    self._qa_cache.append(json.loads(line))
        return self._qa_cache
    
    def _load_trajectories(self) -> List[Dict]:
        """加载所有Trajectory数据"""
        if self._trajectory_cache is None:
            with open(self.trajectory_file, 'r', encoding='utf-8') as f:
                self._trajectory_cache = json.load(f)
        return self._trajectory_cache
    
    def find_qa_by_id(self, qa_id: str) -> Optional[Dict]:
        """根据QA ID查找QA"""
        qas = self._load_qas()
        for qa in qas:
            if qa.get('qa_id') == qa_id:
                return qa
        return None
    
    def find_trajectory_by_id(self, trajectory_id: str) -> Optional[Dict]:
        """根据Trajectory ID查找Trajectory"""
        trajectories = self._load_trajectories()
        for traj in trajectories:
            if traj.get('trajectory_id') == trajectory_id:
                return traj
        return None
    
    def trace_qa_to_source(self, qa_id: str) -> Optional[Dict]:
        """
        从QA ID追溯到原始source
        
        Args:
            qa_id: QA的唯一标识
            
        Returns:
            包含完整追溯信息的字典，如果未找到则返回None
        """
        # 查找QA
        qa = self.find_qa_by_id(qa_id)
        if not qa:
            print(f"❌ 未找到QA: {qa_id}")
            return None
        
        print(f"✓ 找到QA: {qa['question'][:80]}...")
        
        # 查找Trajectory
        trajectory = self.find_trajectory_by_id(qa['trajectory_id'])
        if not trajectory:
            print(f"❌ 未找到Trajectory: {qa['trajectory_id']}")
            return None
        
        print(f"✓ 找到Trajectory: {trajectory['trajectory_id']}")
        print(f"  - 深度: {trajectory['total_depth']} 步")
        print(f"  - 节点数: {len(trajectory['nodes'])}")
        
        # 提取Source信息
        source_id = trajectory['source_id']
        seed_data = trajectory['seed_data']
        
        print(f"✓ 追溯到Source: {source_id}")
        print(f"  - 原始内容: {seed_data}")
        
        return {
            'qa': qa,
            'trajectory': trajectory,
            'source_id': source_id,
            'seed_data': seed_data
        }
    
    def get_qas_by_source(self, source_id: str) -> List[Dict]:
        """获取某个source生成的所有QA"""
        qas = self._load_qas()
        return [qa for qa in qas if qa.get('source_id') == source_id]
    
    def get_trajectories_by_source(self, source_id: str) -> List[Dict]:
        """获取某个source生成的所有trajectory"""
        trajectories = self._load_trajectories()
        return [t for t in trajectories if t.get('source_id') == source_id]
    
    def get_statistics(self) -> Dict:
        """获取数据统计信息"""
        qas = self._load_qas()
        trajectories = self._load_trajectories()
        
        # 统计每个source的数据量
        source_qa_count = {}
        source_traj_count = {}
        
        for qa in qas:
            source_id = qa.get('source_id', 'unknown')
            source_qa_count[source_id] = source_qa_count.get(source_id, 0) + 1
        
        for traj in trajectories:
            source_id = traj.get('source_id', 'unknown')
            source_traj_count[source_id] = source_traj_count.get(source_id, 0) + 1
        
        return {
            'total_qas': len(qas),
            'total_trajectories': len(trajectories),
            'total_sources': len(set(source_qa_count.keys())),
            'qas_per_source': source_qa_count,
            'trajectories_per_source': source_traj_count
        }
    
    def print_full_trace(self, qa_id: str):
        """打印完整的追溯链条"""
        print(f"\n{'='*80}")
        print(f"完整追溯链条: {qa_id}")
        print(f"{'='*80}\n")
        
        result = self.trace_qa_to_source(qa_id)
        if not result:
            return
        
        qa = result['qa']
        trajectory = result['trajectory']
        
        print(f"\n📝 QA层:")
        print(f"  ID: {qa['qa_id']}")
        print(f"  问题: {qa['question']}")
        print(f"  答案: {qa['answer'][:100]}...")
        print(f"  推理步骤: {len(qa.get('reasoning_steps', []))} 步")
        
        print(f"\n🛤️  Trajectory层:")
        print(f"  ID: {trajectory['trajectory_id']}")
        print(f"  深度: {trajectory['total_depth']}")
        print(f"  节点详情:")
        for i, node in enumerate(trajectory['nodes'][:3]):  # 只显示前3个节点
            print(f"    步骤 {i+1}:")
            print(f"      意图: {node['intent']}")
            if node.get('action'):
                print(f"      工具: {node['action'].get('tool_name', 'N/A')}")
            print(f"      观察: {node['observation'][:60]}...")
        if len(trajectory['nodes']) > 3:
            print(f"    ... 还有 {len(trajectory['nodes']) - 3} 个节点")
        
        print(f"\n🌱 Source层:")
        print(f"  ID: {result['source_id']}")
        print(f"  原始Seed: {result['seed_data']}")
        print(f"  元信息: {qa['metadata']}")
        
        print(f"\n{'='*80}\n")


def print_statistics(qa_file: str, trajectory_file: str):
    """打印数据统计信息"""
    tracer = DataTracer(qa_file, trajectory_file)
    stats = tracer.get_statistics()
    
    print(f"\n{'='*80}")
    print(f"数据统计")
    print(f"{'='*80}\n")
    print(f"总QA数: {stats['total_qas']}")
    print(f"总Trajectory数: {stats['total_trajectories']}")
    print(f"总Source数: {stats['total_sources']}")
    print(f"\n每个Source的数据量:")
    for source_id in stats['qas_per_source']:
        qa_count = stats['qas_per_source'].get(source_id, 0)
        traj_count = stats['trajectories_per_source'].get(source_id, 0)
        print(f"  {source_id}: {traj_count} trajectories → {qa_count} QAs")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("用法:")
        print("  追溯QA: python trace_utils.py <qa_file> <traj_file> <qa_id>")
        print("  统计: python trace_utils.py <qa_file> <traj_file>")
        sys.exit(1)
    
    qa_file = sys.argv[1]
    traj_file = sys.argv[2]
    
    if len(sys.argv) >= 4:
        # 追溯模式
        qa_id = sys.argv[3]
        tracer = DataTracer(qa_file, traj_file)
        tracer.print_full_trace(qa_id)
    else:
        # 统计模式
        print_statistics(qa_file, traj_file)

