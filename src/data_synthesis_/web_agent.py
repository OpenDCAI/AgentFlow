"""
Web Agent Data Synthesis - 使用Web Agent生成训练数据

该模块实现了一个完整的数据合成pipeline，包含三个主要步骤：
1. Trajectory Sampling: 从seed实体开始，迭代生成动作和观察，形成trajectory tree
2. Trajectory Selection: 从trajectory tree中选择完整的链路
3. QA Synthesis: 基于选择的trajectory合成问答对
"""

import openai
import json
import os
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import sys
import pdb
import bdb

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from envs import WebEnvironment


@dataclass
class TrajectoryNode:
    """Trajectory tree中的单个节点，表示一个状态"""
    node_id: str
    observation: str  # 当前观察到的信息
    intent: str  # 产生这个节点的意图
    action: Optional[Dict[str, Any]] = None  # 产生这个节点的动作
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    depth: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)


@dataclass
class Trajectory:
    """完整的trajectory链路"""
    trajectory_id: str
    nodes: List[TrajectoryNode]
    seed_entity: str
    total_depth: int
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "trajectory_id": self.trajectory_id,
            "seed_entity": self.seed_entity,
            "total_depth": self.total_depth,
            "nodes": [node.to_dict() for node in self.nodes]
        }


@dataclass
class SynthesizedQA:
    """合成的问答对"""
    question: str
    answer: str
    trajectory_id: str
    reasoning_steps: List[Dict[str, str]]  # 包含每一步的action, intent, observation
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)


class TrajectorySampler:
    """
    Trajectory采样器，负责从seed实体生成trajectory tree
    """
    
    def __init__(self, 
                 environment: WebEnvironment,
                 model_name: str = "gpt-4.1-2025-04-14",
                 max_depth: int = 5,
                 branching_factor: int = 2,
                 max_retries: int = 3,
                 depth_threshold: int = 3):
        """
        初始化Trajectory采样器
        
        Args:
            environment: Web环境实例
            model_name: LLM模型名称
            max_depth: 最大采样深度
            branching_factor: 每个节点的分支数（采样次数）
            max_retries: API调用最大重试次数
            depth_threshold: 深度阈值，超过此深度时branching_factor降为1
        """
        self.environment = environment
        self.model_name = model_name
        self.max_depth = max_depth
        self.branching_factor = branching_factor
        self.max_retries = max_retries
        self.depth_threshold = depth_threshold
        
        # 初始化OpenAI客户端
        self.client = openai.OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_API_URL", os.environ.get("OPENAI_API_BASE", ""))
        )
        
        # Trajectory tree存储
        self.nodes: Dict[str, TrajectoryNode] = {}
        self.root_id: Optional[str] = None
        
    def sample_trajectory_tree(self, seed_entity: str) -> Dict[str, TrajectoryNode]:
        """
        从seed实体开始采样trajectory tree
        
        Args:
            seed_entity: 起始实体（如人名、地名、概念等）
            
        Returns:
            完整的trajectory tree (node_id -> TrajectoryNode)
        """
        print(f"\n{'='*60}")
        print(f"开始采样 Trajectory Tree")
        print(f"Seed实体: {seed_entity}")
        print(f"最大深度: {self.max_depth}, 分支因子: {self.branching_factor}")
        print(f"{'='*60}\n")
        
        # 创建根节点
        root_id = f"node_0_0"
        root_node = TrajectoryNode(
            node_id=root_id,
            observation=f"起始实体: {seed_entity}",
            intent="开始探索实体相关信息",
            action=None,
            parent_id=None,
            depth=0
        )
        
        self.nodes[root_id] = root_node
        self.root_id = root_id
        
        # BFS扩展tree
        self._expand_tree(root_id, seed_entity)
        
        print(f"\n✅ Trajectory Tree采样完成!")
        print(f"   总节点数: {len(self.nodes)}")
        print(f"   最大深度: {max(node.depth for node in self.nodes.values())}")
        
        return self.nodes
    
    def _expand_tree(self, node_id: str, seed_entity: str):
        """
        递归扩展trajectory tree
        
        Args:
            node_id: 当前节点ID
            seed_entity: 原始实体
        """
        current_node = self.nodes[node_id]
        
        # 检查深度限制
        if current_node.depth >= self.max_depth:
            return
        
        print(f"\n🌳 扩展节点 {node_id} (深度: {current_node.depth})")
        
        # 根据深度动态调整分支因子
        if current_node.depth >= self.depth_threshold:
            current_branching_factor = 1
            print(f"   ⚠️  深度 {current_node.depth} >= 阈值 {self.depth_threshold}，分支因子降为 1")
        else:
            current_branching_factor = self.branching_factor
        
        # 对当前节点进行branching_factor次采样
        for branch_idx in range(current_branching_factor):
            try:
                # 生成下一步的action和intent
                action, intent = self._generate_next_action(current_node, seed_entity)
                
                if action is None:
                    print(f"   分支 {branch_idx + 1}: 无法生成有效动作，跳过")
                    continue
                
                # 执行action获取observation
                observation = self._execute_action(action)

                
                # 创建新节点
                child_id = f"node_{current_node.depth + 1}_{len(self.nodes)}"
                child_node = TrajectoryNode(
                    node_id=child_id,
                    observation=observation,
                    intent=intent,
                    action=action,
                    parent_id=node_id,
                    depth=current_node.depth + 1
                )
                
                self.nodes[child_id] = child_node
                current_node.children_ids.append(child_id)
                
                print(f"   ✓ 分支 {branch_idx + 1}: 创建节点 {child_id}")
                print(f"     Intent: {intent}")
                print(f"     Action: {action.get('tool_name', 'unknown')}")
                print(f"     Observation: {observation[:100]}...")
                
                # 递归扩展子节点
                self._expand_tree(child_id, seed_entity)
                
            except Exception as e:
                if isinstance(e, bdb.BdbQuit):
                    raise e
                print(f"   ✗ 分支 {branch_idx + 1} 失败: {str(e)}")
                continue
    
    def _generate_next_action(self, 
                              current_node: TrajectoryNode, 
                              seed_entity: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        基于当前状态生成下一步的action和intent
        
        Args:
            current_node: 当前节点
            seed_entity: 原始实体
            
        Returns:
            (action_dict, intent_string)
        """
        # 构建历史轨迹
        history = self._build_history(current_node)
        
        # 构建prompt
        prompt = f"""你是一个Web Agent，正在探索关于实体"{seed_entity}"的相关信息。

目标: 围绕实体"{seed_entity}"收集**具体的、可验证的、多维度的特征信息**，特别关注能够支持**multi-hop推理**的关系链信息：

**关键特征维度（优先收集关系链信息）**:

**高优先级 - 关系链信息（用于multi-hop推理）**:
- 人物关系: 创始人、领导者、核心团队成员及其背景
  * 这些人之前创立/参与过什么其他组织？
  * 他们有什么独特的经历或成就？
- 组织关系: 合作伙伴、投资方、母公司、子公司
  * 与哪些知名组织有关联？
  * 这些关联是如何形成的？
- 时间关系: 前身、演变历史、重要转折点
  * 从什么组织/概念演变而来？
  * 经历了哪些重大变化？
- 因果关系: 成立/发展的原因、影响、衍生成果
  * 为什么被创立？解决什么问题？
  * 产生了什么重要影响或衍生实体？

**中优先级 - 可量化特征**:
- 时间信息: 成立/诞生时间、重要时间节点、时期范围
- 地理信息: 位置、总部、起源地（包括这些地点的别称/特征）
- 规模/数量信息: 规模、数量、员工数、产品数等可量化的数据

**标准优先级 - 描述性特征**:
- 产品/作品: 具体的产品、项目、作品名称及其特点
- 特征描述: 独特的特点、风格、标志性元素
- 领域/类别: 所属行业、领域、分类

当前历史轨迹:
{history}

当前观察:
{current_node.observation}

请基于当前状态和已探索的信息，选择一个**尚未充分探索的维度**，生成下一步的动作和意图。

**探索策略（支持multi-hop推理）**:
- **优先探索关系链信息**: 人物背景、组织关联、前身演变、因果联系
- 寻找可以形成推理链的信息：
  * 例如：创始人 → 创始人的其他公司 → 那些公司的特征
  * 例如：投资方 → 投资方的特点 → 投资策略
  * 例如：产品 → 产品的用户规模 → 增长速度记录
- 收集中间实体的信息（可作为推理桥梁）
- 避免重复已有信息，选择新的关系角度
- 所有信息必须是具体的、可验证的

可用工具:
1. web_search: 搜索网络信息
   - 参数: queries (array of strings)
   - 适用于：获取概述信息、查找相关网页链接、搜索特定维度的信息
   
2. web_visit: 访问网页并提取内容
   - 参数: urls (array of strings), goal (string)
   - 适用于：深入了解特定网页的详细内容、提取具体数据

请以JSON格式返回，包含:
1. intent: 执行这个动作的意图和理由（说明探索哪个维度，为什么选择这个维度）
2. action: 动作详情
   - tool_name: 工具名称 (web_search 或 web_visit)
   - parameters: 工具参数

返回格式:
{{
    "intent": "意图描述",
    "action": {{
        "tool_name": "工具名称",
        "parameters": {{参数}}
    }}
}}
"""
        
        retry = 0
        while retry < self.max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7 + retry * 0.1,  # 重试时增加温度
                    response_format={"type": "json_object"}
                )
                
                result = json.loads(response.choices[0].message.content)
                intent = result.get("intent", "")
                action = result.get("action", {})
                
                # 验证action格式
                if self._validate_action(action):
                    return action, intent
                
                retry += 1
                
            except Exception as e:
                print(f"      警告: 生成动作失败 (尝试 {retry + 1}): {str(e)}")
                retry += 1
        
        return None, ""
    
    def _validate_action(self, action: Dict[str, Any]) -> bool:
        """验证action格式是否正确"""
        if not isinstance(action, dict):
            return False
        
        tool_name = action.get("tool_name", "")
        parameters = action.get("parameters", {})
        
        if tool_name not in ["web_search", "web_visit"]:
            return False
        
        if tool_name == "web_search":
            return "queries" in parameters and isinstance(parameters["queries"], list)
        
        if tool_name == "web_visit":
            return ("urls" in parameters and isinstance(parameters["urls"], list) and
                    "goal" in parameters and isinstance(parameters["goal"], str))
        
        return False
    
    def _execute_action(self, action: Dict[str, Any]) -> str:
        """
        执行动作并返回observation
        
        Args:
            action: 动作字典
            
        Returns:
            执行结果(observation)
        """
        tool_name = action["tool_name"]
        parameters = action["parameters"]
        
        try:
            result = self.environment.execute_tool(tool_name, parameters)
            return result
        except Exception as e:
            return f"[Error] 执行动作失败: {str(e)}"
    
    def _build_history(self, node: TrajectoryNode) -> str:
        """构建从根到当前节点的历史轨迹"""
        path = []
        current = node
        
        while current.parent_id is not None:
            path.append(current)
            current = self.nodes[current.parent_id]
        
        path.reverse()
        
        if not path:
            return "无历史轨迹"
        
        history_str = ""
        for i, n in enumerate(path, 1):
            history_str += f"\n步骤 {i}:\n"
            history_str += f"  意图: {n.intent}\n"
            if n.action:
                history_str += f"  动作: {n.action.get('tool_name', 'unknown')}\n"
            history_str += f"  观察: {n.observation[:200]}...\n"
        
        return history_str


class TrajectorySelector:
    """
    Trajectory选择器，从tree中选择高质量的链路
    """
    
    def __init__(self, 
                 model_name: str = "gpt-4.1-2025-04-14",
                 max_trajectories: int = 5,
                 min_depth: int = 2):
        """
        初始化选择器
        
        Args:
            model_name: LLM模型名称
            max_trajectories: 最多选择的trajectory数量
            min_depth: 最小深度要求
        """
        self.model_name = model_name
        self.max_trajectories = max_trajectories
        self.min_depth = min_depth
        
        self.client = openai.OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_API_URL", os.environ.get("OPENAI_API_BASE", ""))
        )
    
    def select_trajectories(self, 
                           nodes: Dict[str, TrajectoryNode],
                           root_id: str,
                           seed_entity: str) -> List[Trajectory]:
        """
        从trajectory tree中选择高质量的完整链路
        
        Args:
            nodes: 所有节点字典
            root_id: 根节点ID
            seed_entity: 原始实体
            
        Returns:
            选择的trajectory列表
        """
        print(f"\n{'='*60}")
        print(f"开始选择 Trajectories")
        print(f"{'='*60}\n")
        
        # 1. 找到所有叶子节点
        leaf_nodes = [node for node in nodes.values() if not node.children_ids]
        print(f"找到 {len(leaf_nodes)} 个叶子节点")
        
        # 2. 筛选满足最小深度的叶子节点
        valid_leaves = [node for node in leaf_nodes if node.depth >= self.min_depth]
        print(f"满足最小深度({self.min_depth})的叶子节点: {len(valid_leaves)}")
        
        if not valid_leaves:
            print("⚠️  没有找到满足深度要求的trajectory")
            return []
        
        # 3. 从每个叶子节点回溯到根节点，构建完整路径
        candidate_paths = []
        for leaf in valid_leaves:
            path = self._build_path_to_root(leaf, nodes, root_id)
            if path:
                candidate_paths.append(path)
        
        print(f"构建了 {len(candidate_paths)} 条候选路径")
        
        # 4. 评分并选择最好的trajectories
        selected = self._score_and_select(candidate_paths, seed_entity)
        
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
                         seed_entity: str) -> List[Trajectory]:
        """评分并选择最好的路径"""
        scored_paths = []
        
        for idx, path in enumerate(paths):
            score = self._score_path(path, seed_entity)
            scored_paths.append((score, idx, path))
        
        # 按分数排序
        scored_paths.sort(reverse=True, key=lambda x: x[0])
        
        # 选择top-k
        selected_trajectories = []
        for rank, (score, idx, path) in enumerate(scored_paths[:self.max_trajectories], 1):
            trajectory = Trajectory(
                trajectory_id=f"traj_{idx}",
                nodes=path,
                seed_entity=seed_entity,
                total_depth=len(path)
            )
            selected_trajectories.append(trajectory)
            print(f"  选择 Trajectory {rank}: 深度={len(path)}, 分数={score:.2f}")
        
        return selected_trajectories
    
    def _score_path(self, path: List[TrajectoryNode], seed_entity: str) -> float:
        """
        为路径打分
        
        评分标准:
        1. 深度 (越深越好，但有边际递减)
        2. 信息量 (observation的平均长度)
        3. 多样性 (使用不同工具)
        """
        # 深度得分 (边际递减)
        depth_score = min(len(path) / 5.0, 1.0) * 40
        
        # 信息量得分
        avg_obs_length = sum(len(node.observation) for node in path) / len(path) if path else 0
        info_score = min(avg_obs_length / 1000, 1.0) * 30
        
        # 多样性得分
        tool_names = set()
        for node in path:
            if node.action:
                tool_names.add(node.action.get("tool_name", ""))
        diversity_score = len(tool_names) / 2.0 * 30
        
        total_score = depth_score + info_score + diversity_score
        return total_score


class QASynthesizer:
    """
    QA合成器，基于trajectory生成问答对
    """
    
    def __init__(self, model_name: str = "gpt-4.1-2025-04-14"):
        """初始化QA合成器"""
        self.model_name = model_name
        
        self.client = openai.OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_API_URL", os.environ.get("OPENAI_API_BASE", ""))
        )
    
    def synthesize_qa(self, trajectory: Trajectory) -> Optional[SynthesizedQA]:
        """
        基于trajectory合成问答对
        
        Args:
            trajectory: 选中的trajectory
            
        Returns:
            合成的QA对
        """
        print(f"\n🔧 合成QA对 - Trajectory: {trajectory.trajectory_id}")
        
        # 构建trajectory描述
        traj_description = self._format_trajectory(trajectory)
        
        # 生成问答对
        prompt = f"""你是一个数据合成专家。基于以下Web Agent围绕特定实体的探索轨迹，请合成一个需要**multi-hop推理**的谜题式问答对。

探索的核心实体: {trajectory.seed_entity}

完整探索轨迹:
{traj_description}

请基于这条围绕"{trajectory.seed_entity}"的探索轨迹合成一个**需要multi-hop推理的谜题式问答对**:

## 1. **问题(Question)要求 - Multi-hop推理设计**:

### 什么是Multi-hop推理？
需要通过**多个逻辑跳跃**才能得到答案，每一步都基于前一步的结果。

### Multi-hop问题设计策略：

**策略A - 关系链推理**：
通过中间实体建立连接
- 例如："Please identify the organization co-founded by the entrepreneur who also founded Tesla and SpaceX, which released a viral AI chatbot in late 2022."
- 推理路径：找到"founded Tesla and SpaceX"的人 → Elon Musk → 找Elon Musk co-founded的AI组织 → OpenAI

**策略B - 属性推理链**：
通过属性组合逐步缩小范围
- 例如："What is the technology developed by the company located in the city known as the tech capital of the West Coast, founded by someone who previously led a startup accelerator?"
- 推理路径：West Coast tech capital → San Francisco → startup accelerator leader → Sam Altman → Sam Altman创立的公司 → OpenAI

**策略C - 时间序列推理**：
通过时间顺序的事件链
- 例如："Please identify the entity that emerged from a non-profit founded in the mid-2010s, underwent a structural change to include a capped-profit model, and then launched a product that broke user growth records in early 2023."
- 推理路径：mid-2010s非营利 → 结构转变 → capped-profit → 2023爆款产品 → OpenAI

**策略D - 因果推理链**：
通过因果关系连接
- 例如："What is the result of concerns about AI safety by tech leaders, which led to the founding of a research lab in San Francisco, that later developed the technology behind a chatbot used by millions?"
- 推理路径：AI safety concerns → research lab成立 → 开发技术 → chatbot → OpenAI

### 问题具体要求：
- **必须包含至少2个推理跳跃（hop）**
- 不要直接提到实体名称"{trajectory.seed_entity}"
- 使用3-5个相互关联的约束条件
- 约束条件应该形成逻辑链，不是独立的
- 将具体信息模糊化：
  * 时间："2015年" → "mid-2010s"
  * 人名："Sam Altman" → "a former president of Y Combinator"
  * 地点："San Francisco" → "a major West Coast tech hub"
  * 产品："ChatGPT" → "a conversational AI that reached 100M users in record time"
- 使用"Please identify..."、"What is..."或"Which [entity]..."开头

## 2. **答案(Answer)要求**:
   - **必须简短**：只写实体名称本身
   - 不要解释，不要额外描述
   - 格式：直接写实体名（如："OpenAI"、"Elon Musk"、"Quantum Computing"）

## 3. **推理步骤(Reasoning Steps)**:
   - 明确标注每个推理跳跃（hop）
   - 描述如何从一个线索推导到下一个
   - 展示多步探索和验证的完整过程

## Multi-hop示例：

**示例1 - 关系链（2-hop）**:
Question: "Please identify the AI research organization co-founded by the entrepreneur who previously co-founded the online payment company that merged with Confinity, and which later released a conversational AI tool that gained over 100 million users within two months."
Answer: "OpenAI"
- Hop 1: online payment company merged with Confinity → PayPal → co-founder → Elon Musk
- Hop 2: Elon Musk co-founded AI organization → released chatbot with 100M users → OpenAI

**示例2 - 属性链（3-hop）**:
Question: "What is the company founded in the city home to the Golden Gate Bridge, by someone who previously led a prominent startup accelerator, which developed the technology that powers a chat interface launched in late 2022?"
Answer: "OpenAI"
- Hop 1: Golden Gate Bridge city → San Francisco
- Hop 2: led startup accelerator in SF → Sam Altman
- Hop 3: Sam Altman founded company → chat interface 2022 → OpenAI

返回JSON格式:
{{
    "question": "Please identify/What is... [包含multi-hop推理链的描述]",
    "answer": "{trajectory.seed_entity}",
    "reasoning_steps": [
        {{
            "step": 1,
            "hop": "Hop 1: 从线索A推导到中间实体B",
            "intent": "步骤意图",
            "action": "采取的动作",
            "observation": "观察到的信息摘要"
        }},
        {{
            "step": 2,
            "hop": "Hop 2: 从中间实体B推导到目标答案",
            "intent": "步骤意图",
            "action": "采取的动作",
            "observation": "观察到的信息摘要"
        }},
        ...
    ]
}}

**关键要求**: 
- 问题必须需要至少2个推理跳跃（不能直接推导）
- 答案必须简短，只写实体名称
- 推理路径必须清晰，每个hop都有明确的逻辑
- 所有信息必须基于轨迹中的真实数据
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            qa = SynthesizedQA(
                question=result.get("question", ""),
                answer=result.get("answer", ""),
                trajectory_id=trajectory.trajectory_id,
                reasoning_steps=result.get("reasoning_steps", []),
                metadata={
                    "seed_entity": trajectory.seed_entity,
                    "trajectory_depth": trajectory.total_depth,
                    "synthesis_date": datetime.now().isoformat()
                }
            )
            
            print(f"  ✓ 成功合成QA对")
            print(f"    问题: {qa.question[:100]}...")
            print(f"    答案: {qa.answer[:100]}...")
            
            return qa
            
        except Exception as e:
            print(f"  ✗ 合成失败: {str(e)}")
            return None
    
    def _format_trajectory(self, trajectory: Trajectory) -> str:
        """格式化trajectory为可读文本"""
        formatted = ""
        
        for i, node in enumerate(trajectory.nodes, 1):
            formatted += f"\n步骤 {i}:\n"
            formatted += f"  意图: {node.intent}\n"
            
            if node.action:
                formatted += f"  动作: {node.action.get('tool_name', 'unknown')}\n"
                formatted += f"  参数: {json.dumps(node.action.get('parameters', {}), ensure_ascii=False)}\n"
            
            obs_preview = node.observation[:500] + "..." if len(node.observation) > 500 else node.observation
            formatted += f"  观察: {obs_preview}\n"
        
        return formatted


class WebAgentDataSynthesis:
    """
    Web Agent数据合成主类
    
    整合三个步骤:
    1. Trajectory Sampling
    2. Trajectory Selection
    3. QA Synthesis
    """
    
    def __init__(self,
                 model_name: str = "gpt-4.1-2025-04-14",
                 max_depth: int = 5,
                 branching_factor: int = 2,
                 max_trajectories: int = 5,
                 min_depth: int = 2,
                 depth_threshold: int = 3,
                 **env_kwargs):
        """
        初始化数据合成系统
        
        Args:
            model_name: LLM模型名称
            max_depth: Trajectory最大深度
            branching_factor: 每个节点的分支因子
            max_trajectories: 最多选择的trajectory数量
            min_depth: Trajectory最小深度
            depth_threshold: 深度阈值，超过此深度时branching_factor降为1
            **env_kwargs: WebEnvironment的额外配置
        """
        self.model_name = model_name
        
        # 创建Web环境
        print("初始化 Web Environment...")
        self.environment = WebEnvironment(model_name=model_name, **env_kwargs)
        
        # 创建三个组件
        self.sampler = TrajectorySampler(
            environment=self.environment,
            model_name=model_name,
            max_depth=max_depth,
            branching_factor=branching_factor,
            depth_threshold=depth_threshold
        )
        
        self.selector = TrajectorySelector(
            model_name=model_name,
            max_trajectories=max_trajectories,
            min_depth=min_depth
        )
        
        self.synthesizer = QASynthesizer(model_name=model_name)
        
        # 存储结果
        self.trajectory_tree: Dict[str, TrajectoryNode] = {}
        self.selected_trajectories: List[Trajectory] = []
        self.synthesized_qas: List[SynthesizedQA] = []
    
    def run(self, seed_entities: List[str]) -> List[SynthesizedQA]:
        """
        运行完整的数据合成pipeline
        
        Args:
            seed_entities: Seed实体列表
            
        Returns:
            合成的QA对列表
        """
        print(f"\n{'='*80}")
        print(f"🚀 Web Agent 数据合成 Pipeline 启动")
        print(f"{'='*80}")
        print(f"总Seed实体数: {len(seed_entities)}")
        print(f"模型: {self.model_name}")
        print(f"{'='*80}\n")
        
        all_qas = []
        
        for entity_idx, seed_entity in enumerate(seed_entities, 1):
            print(f"\n\n{'#'*80}")
            print(f"处理 Seed 实体 {entity_idx}/{len(seed_entities)}: {seed_entity}")
            print(f"{'#'*80}\n")
            
            try:
                # Step 1: Trajectory Sampling
                print(f"\n📊 步骤 1/3: Trajectory Sampling")
                self.trajectory_tree = self.sampler.sample_trajectory_tree(seed_entity)

                
                # Step 2: Trajectory Selection
                print(f"\n🎯 步骤 2/3: Trajectory Selection")
                self.selected_trajectories = self.selector.select_trajectories(
                    nodes=self.trajectory_tree,
                    root_id=self.sampler.root_id,
                    seed_entity=seed_entity
                )
                
                # Step 3: QA Synthesis
                print(f"\n✨ 步骤 3/3: QA Synthesis")
                for trajectory in self.selected_trajectories:
                    qa = self.synthesizer.synthesize_qa(trajectory)
                    if qa:
                        all_qas.append(qa)
                        self.synthesized_qas.append(qa)
                
                print(f"\n✅ Seed实体 {entity_idx} 完成! 生成了 {len(self.selected_trajectories)} 个QA对")
                
            except Exception as e:
                if isinstance(e, bdb.BdbQuit):
                    raise e
                print(f"\n❌ Seed实体 {entity_idx} 失败: {str(e)}")
                continue
        
        print(f"\n\n{'='*80}")
        print(f"🎉 数据合成完成!")
        print(f"{'='*80}")
        print(f"总共处理: {len(seed_entities)} 个Seed实体")
        print(f"成功生成: {len(all_qas)} 个QA对")
        print(f"{'='*80}\n")
        
        return all_qas
    
    def save_results(self, output_dir: str = "synthesis_results"):
        """
        保存所有结果
        
        Args:
            output_dir: 输出目录
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存QA对
        qa_file = os.path.join(output_dir, f"synthesized_qa_{timestamp}.jsonl")
        with open(qa_file, "w", encoding="utf-8") as f:
            for qa in self.synthesized_qas:
                f.write(json.dumps(qa.to_dict(), ensure_ascii=False) + "\n")
        
        print(f"💾 QA对已保存到: {qa_file}")
        
        # 保存trajectories
        traj_file = os.path.join(output_dir, f"trajectories_{timestamp}.json")
        with open(traj_file, "w", encoding="utf-8") as f:
            trajectories_data = [traj.to_dict() for traj in self.selected_trajectories]
            json.dump(trajectories_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Trajectories已保存到: {traj_file}")
        
        # 保存统计信息
        stats_file = os.path.join(output_dir, f"statistics_{timestamp}.json")
        stats = {
            "total_qas": len(self.synthesized_qas),
            "total_trajectories": len(self.selected_trajectories),
            "total_nodes": len(self.trajectory_tree),
            "avg_trajectory_depth": sum(t.total_depth for t in self.selected_trajectories) / len(self.selected_trajectories) if self.selected_trajectories else 0,
            "model_name": self.model_name,
            "timestamp": timestamp
        }
        
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"💾 统计信息已保存到: {stats_file}")


def main():
    """主函数 - 演示如何使用数据合成系统"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Web Agent 数据合成系统")
    
    parser.add_argument("--seed-entities", type=str, required=True,
                       help="Seed实体JSON文件路径，包含实体列表")
    parser.add_argument("--model", type=str, default="gpt-4.1-2025-04-14",
                       help="LLM模型名称")
    parser.add_argument("--max-depth", type=int, default=5,
                       help="Trajectory最大深度")
    parser.add_argument("--branching-factor", type=int, default=2,
                       help="每个节点的分支因子")
    parser.add_argument("--max-trajectories", type=int, default=5,
                       help="每个seed实体最多选择的trajectory数量")
    parser.add_argument("--min-depth", type=int, default=2,
                       help="Trajectory最小深度")
    parser.add_argument("--depth-threshold", type=int, default=3,
                       help="深度阈值，超过此深度时branching_factor降为1")
    parser.add_argument("--output-dir", type=str, default="synthesis_results",
                       help="输出目录")
    parser.add_argument("--web-search-top-k", type=int, default=3,
                       help="Web搜索返回结果数")
    
    args = parser.parse_args()
    
    # 读取seed实体
    print(f"读取 seed 实体文件: {args.seed_entities}")
    with open(args.seed_entities, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, list):
            seed_entities = data
        elif isinstance(data, dict) and "entities" in data:
            seed_entities = data["entities"]
        else:
            raise ValueError("Seed实体文件格式错误，应为实体列表或包含'entities'字段的字典")
    
    print(f"加载了 {len(seed_entities)} 个seed实体")
    
    # 创建数据合成系统
    synthesizer = WebAgentDataSynthesis(
        model_name=args.model,
        max_depth=args.max_depth,
        branching_factor=args.branching_factor,
        max_trajectories=args.max_trajectories,
        min_depth=args.min_depth,
        depth_threshold=args.depth_threshold,
        web_search_top_k=args.web_search_top_k
    )
    
    # 运行合成pipeline
    qas = synthesizer.run(seed_entities)
    
    # 保存结果
    synthesizer.save_results(output_dir=args.output_dir)
    
    print(f"\n✅ 全部完成! 共生成 {len(qas)} 个QA对")


if __name__ == "__main__":
    main()

