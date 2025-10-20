"""
Trajectory采样器

负责从seed实体出发，采样trajectory tree
"""

import openai
import json
import os
import bdb
from typing import Dict, List, Any, Optional, Tuple

from models import TrajectoryNode
from synthesis_config import SynthesisConfig

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from envs import Environment


class GenericTrajectorySampler:
    """
    通用Trajectory采样器，支持任意工具组合
    """
    
    def __init__(self, 
                 environment: Environment,
                 config: SynthesisConfig):
        """
        初始化通用Trajectory采样器
        
        Args:
            environment: 环境实例（任意类型）
            config: 合成配置
        """
        self.environment = environment
        self.config = config
        
        # 初始化OpenAI客户端
        self.client = openai.OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_API_URL", os.environ.get("OPENAI_API_BASE", ""))
        )
        
        # 获取可用工具信息
        self.available_tools = self._get_available_tools()
        self.tool_descriptions = self._generate_tool_descriptions()
        
        # Trajectory tree存储
        self.nodes: Dict[str, TrajectoryNode] = {}
        self.root_id: Optional[str] = None
        
    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """获取环境中的可用工具信息"""
        tools = []
        
        # 如果配置中指定了工具列表，只使用这些工具
        if self.config.available_tools:
            tool_names = self.config.available_tools
        else:
            tool_names = self.environment.list_tools()
        
        for tool_name in tool_names:
            tool = self.environment.get_tool(tool_name)
            if tool:
                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                })
        
        return tools
    
    def _generate_tool_descriptions(self) -> str:
        """生成工具描述文本"""
        descriptions = []
        
        for tool in self.available_tools:
            desc = f"\n{len(descriptions) + 1}. {tool['name']}: {tool['description']}\n"
            desc += "   参数:\n"
            
            for param in tool['parameters']:
                param_type = param['type']
                if param_type == 'array':
                    param_type = f"array of {param.get('array_type', 'string')}"
                
                required_str = " (必需)" if param.get('required', False) else " (可选)"
                desc += f"   - {param['name']} ({param_type}){required_str}: {param['description']}\n"
            
            descriptions.append(desc)
        
        return "\n".join(descriptions)
    
    def sample_trajectory_tree(self, seed_data: str) -> Dict[str, TrajectoryNode]:
        """
        从seed起点开始采样trajectory tree
        
        Args:
            seed_data: 起始点数据（字符串，可以是任意内容：实体名、URL、问题描述、文本等）
            
        Returns:
            完整的trajectory tree
        """
        print(f"\n{'='*60}")
        print(f"开始采样 Trajectory Tree")
        print(f"Seed内容: {seed_data}")
        print(f"环境模式: {self.environment.mode}")
        print(f"可用工具: {[t['name'] for t in self.available_tools]}")
        print(f"最大深度: {self.config.max_depth}, 分支因子: {self.config.branching_factor}")
        print(f"{'='*60}\n")
        
        # 创建根节点
        root_id = f"node_0_0"
        observation = f"起点: {seed_data}"
        if self.config.seed_description:
            observation = f"起点 ({self.config.seed_description}): {seed_data}"
        
        root_node = TrajectoryNode(
            node_id=root_id,
            observation=observation,
            intent="开始探索",
            action=None,
            parent_id=None,
            depth=0
        )
        
        self.nodes[root_id] = root_node
        self.root_id = root_id
        
        # BFS扩展tree
        self._expand_tree(root_id, seed_data)
        
        print(f"\n✅ Trajectory Tree采样完成!")
        print(f"   总节点数: {len(self.nodes)}")
        print(f"   最大深度: {max(node.depth for node in self.nodes.values())}")
        
        return self.nodes
    
    def _expand_tree(self, node_id: str, seed_data: str):
        """递归扩展trajectory tree"""
        current_node = self.nodes[node_id]
        
        # 检查深度限制
        if current_node.depth >= self.config.max_depth:
            return
        
        print(f"\n🌳 扩展节点 {node_id} (深度: {current_node.depth})")
        
        # 根据深度动态调整分支因子
        if current_node.depth >= self.config.depth_threshold:
            current_branching_factor = 1
            print(f"   ⚠️  深度 {current_node.depth} >= 阈值 {self.config.depth_threshold}，分支因子降为 1")
        else:
            current_branching_factor = self.config.branching_factor
        
        # 对当前节点进行branching_factor次采样
        for branch_idx in range(current_branching_factor):
            try:
                # 生成下一步的action和intent
                action, intent = self._generate_next_action(current_node, seed_data)
                
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
                self._expand_tree(child_id, seed_data)
                
            except Exception as e:
                if isinstance(e, bdb.BdbQuit):
                    raise e
                print(f"   ✗ 分支 {branch_idx + 1} 失败: {str(e)}")
                continue
    
    def _generate_next_action(self, 
                              current_node: TrajectoryNode, 
                              seed_data: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        基于当前状态生成下一步的action和intent
        """
        # 构建历史轨迹
        history = self._build_history(current_node)
        
        # 构建prompt（通用版本，基于配置）
        prompt = self._build_action_generation_prompt(seed_data, history, current_node.observation)
        
        retry = 0
        while retry < self.config.max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.config.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7 + retry * 0.1,
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
    
    def _build_action_generation_prompt(self, seed_data: str, history: str, current_observation: str) -> str:
        """构建动作生成的prompt（基于配置动态生成）"""
        
        # 通用prompt模板
        prompt = f"""你是一个智能Agent，正在使用可用工具进行探索和推理。

【起点信息】
内容: {seed_data}"""
        
        if self.config.seed_description:
            prompt += f"\n说明: {self.config.seed_description}"
        
        prompt += """

【探索目标】
根据起点内容和可用工具，进行系统性探索，收集和推理出有价值的信息。

"""
        
        # 添加用户自定义的sampling tips
        if self.config.sampling_tips:
            prompt += f"""【探索策略和重点】
{self.config.sampling_tips}

"""
        
        # 添加历史轨迹
        prompt += f"""当前历史轨迹:
{history}

当前观察:
{current_observation}

"""
        
        # 添加工具描述
        prompt += f"""可用工具:
{self.tool_descriptions}

"""
        
        # 添加QA示例（如果有）
        if self.config.qa_examples:
            prompt += """参考示例（了解期望的数据类型）:\n"""
            for i, example in enumerate(self.config.qa_examples[:2], 1):  # 只显示前2个
                prompt += f"""
示例 {i}:
问题: {example.get('question', '')}
答案: {example.get('answer', '')}
"""
                if 'reasoning' in example:
                    prompt += f"推理: {example['reasoning']}\n"
        
        # 添加输出格式要求
        prompt += """
请基于当前状态和可用工具，选择一个合适的工具和参数，生成下一步的动作和意图。

返回JSON格式:
{
    "intent": "执行这个动作的意图和理由",
    "action": {
        "tool_name": "工具名称",
        "parameters": {参数字典}
    }
}
"""
        
        return prompt
    
    def _validate_action(self, action: Dict[str, Any]) -> bool:
        """验证action格式是否正确（通用版本）"""
        if not isinstance(action, dict):
            return False
        
        tool_name = action.get("tool_name", "")
        parameters = action.get("parameters", {})
        
        # 检查工具是否可用
        available_tool_names = [t['name'] for t in self.available_tools]
        if tool_name not in available_tool_names:
            return False
        
        # 查找工具定义
        tool_def = None
        for t in self.available_tools:
            if t['name'] == tool_name:
                tool_def = t
                break
        
        if not tool_def:
            return False
        
        # 验证必需参数
        for param in tool_def['parameters']:
            if param.get('required', False):
                if param['name'] not in parameters:
                    return False
        
        return True
    
    def _execute_action(self, action: Dict[str, Any]) -> str:
        """执行动作并返回observation"""
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

