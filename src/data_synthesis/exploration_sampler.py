"""
Exploration-based Trajectory Sampler for GUI Agent

与GenericTrajectorySampler的关键区别：
1. 探索式而非目标导向：从抽象seed出发自由探索，不是为了完成特定任务
2. 发现式学习：探索过程中发现有价值的功能和操作序列
3. 丰富的轨迹保存：每步保存截图、可访问性树、完整observation
4. 避免重复：记录已访问状态，避免无效重复探索
"""

import openai
import json
import os
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
import pdb
from models import TrajectoryNode
from synthesis_config import SynthesisConfig

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from envs import OSWorldEnvironment


class GUIExplorationSampler:
    """
    GUI探索式轨迹采样器
    
    特点：
    - 探索导向：不预设任务目标，自由探索界面
    - 状态感知：记录访问过的状态，避免重复
    - 丰富记录：保存完整的observation（截图+a11y树）
    - 价值发现：识别有价值的操作序列
    """
    
    def __init__(self, 
                 environment: OSWorldEnvironment,
                 config: SynthesisConfig):
        """
        初始化GUI探索采样器
        
        Args:
            environment: OSWorld环境实例
            config: 合成配置
        """
        self.environment = environment
        self.config = config
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_API_URL", os.environ.get("OPENAI_API_BASE", ""))
        )
        
        # 获取可用工具
        self.available_tools = self._get_available_tools()
        self.tool_descriptions = self._generate_tool_descriptions()
        
        # Trajectory tree存储
        self.nodes: Dict[str, TrajectoryNode] = {}
        self.root_id: Optional[str] = None
        
        # 探索状态追踪（避免重复）
        self.visited_states: Set[str] = set()  # 访问过的状态指纹
        self.visited_actions: Dict[str, int] = {}  # 执行过的动作计数
        
    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具信息"""
        tools = []
        
        if self.config.available_tools:
            tool_names = self.config.available_tools
            print(f"📋 从配置获取工具列表: {len(tool_names)} 个工具")
        else:
            tool_names = self.environment.list_tools()
            print(f"📋 从环境获取工具列表: {len(tool_names)} 个工具")
        
        # 获取所有已注册的工具（用于诊断）
        all_registered_tools = self.environment.list_tools()
        
        not_found_tools = []
        for tool_name in tool_names:
            tool = self.environment.get_tool(tool_name)
            if tool:
                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                })
            else:
                not_found_tools.append(tool_name)
        
        # 报告结果
        if tools:
            print(f"✅ 成功加载 {len(tools)} 个工具")
        else:
            print(f"❌ 警告：没有找到任何可用工具！")
        
        if not_found_tools:
            print(f"⚠️  以下工具未找到: {not_found_tools}")
            print(f"💡 可用的工具列表: {all_registered_tools}")
            print(f"💡 提示：OSWorld工具名称通常以 'desktop_' 开头")
        
        return tools
    
    def _generate_tool_descriptions(self) -> str:
        """生成工具描述文本"""
        if not self.available_tools:
            return "⚠️ 没有可用的工具。请检查配置文件中的 available_tools 列表。"
        
        descriptions = []
        
        for tool in self.available_tools:
            desc = f"\n{len(descriptions) + 1}. {tool['name']}: {tool['description']}\n"
            desc += "   Parameters:\n"
            
            for param in tool['parameters']:
                param_type = param['type']
                if param_type == 'array':
                    param_type = f"array of {param.get('array_type', 'string')}"
                
                required_str = " (required)" if param.get('required', False) else " (optional)"
                desc += f"   - {param['name']} ({param_type}){required_str}: {param['description']}\n"
            
            descriptions.append(desc)
        
        return "\n".join(descriptions)
    
    def sample_exploration_tree(self, exploration_seed: str) -> Dict[str, TrajectoryNode]:
        """
        从抽象seed出发进行探索式采样
        
        Args:
            exploration_seed: 探索方向描述（抽象的，例如"探索文本编辑器"）
            
        Returns:
            完整的探索轨迹树
        """
        print(f"\n{'='*60}")
        print(f"开始GUI探索式采样")
        print(f"探索方向: {exploration_seed}")
        print(f"环境模式: {self.environment.mode}")
        print(f"可用工具: {[t['name'] for t in self.available_tools]}")
        print(f"最大深度: {self.config.max_depth}, 分支因子: {self.config.branching_factor}")
        print(f"{'='*60}\n")
        
        # 清空状态追踪
        self.visited_states.clear()
        self.visited_actions.clear()
        
        # 创建root节点（初始观察）
        root_id = f"explore_d0_t0"
        
        # 获取初始observation（丰富的）
        initial_obs = self.environment.get_obs()
        initial_obs_formatted = self.environment.format_observation_by_type(
            initial_obs, 
            output_format="dict"
        )
        
        root_node = TrajectoryNode(
            node_id=root_id,
            observation=self._format_rich_observation(initial_obs_formatted),
            intent=f"开始探索: {exploration_seed}",
            action=None,
            parent_id=None,
            depth=0
        )
        
        # 保存初始状态指纹
        state_fingerprint = self._compute_state_fingerprint(initial_obs_formatted)
        self.visited_states.add(state_fingerprint)
        
        self.nodes[root_id] = root_node
        self.root_id = root_id
        
        print(f"✓ 初始状态已记录")
        print(f"  状态指纹: {state_fingerprint[:16]}...")
        
        # BFS探索
        self._explore_gui_tree(root_id, exploration_seed)
        
        print(f"\n✅ GUI探索采样完成!")
        print(f"   总节点数: {len(self.nodes)}")
        print(f"   最大深度: {max(node.depth for node in self.nodes.values())}")
        print(f"   访问过的状态: {len(self.visited_states)}")
        print(f"   不同动作类型: {len(self.visited_actions)}")
        
        return self.nodes
    
    def _explore_gui_tree(self, node_id: str, exploration_seed: str):
        """递归探索GUI树"""
        current_node = self.nodes[node_id]
        
        # 检查深度限制
        if current_node.depth >= self.config.max_depth:
            return
        
        print(f"\n🔍 探索节点 {node_id} (深度: {current_node.depth})")
        
        # 动态调整分支因子
        if current_node.depth >= self.config.depth_threshold:
            current_branching_factor = 1
            print(f"   ⚠️  深度 {current_node.depth} >= 阈值 {self.config.depth_threshold}，分支因子降为1")
        else:
            current_branching_factor = self.config.branching_factor
        
        # 对当前节点进行分支探索
        successful_branches = 0
        attempts = 0
        max_attempts = current_branching_factor * 3  # 允许多次尝试
        
        while successful_branches < current_branching_factor and attempts < max_attempts:
            attempts += 1
            
            try:
                # 生成探索动作（考虑已访问状态）
                action, intent, novelty_score = self._generate_exploration_action(
                    current_node, 
                    exploration_seed
                )


                
                if action is None:
                    print(f"   尝试 {attempts}: 无法生成有效动作，跳过")
                    continue
                
                # 检查动作是否过于重复
                action_key = self._get_action_key(action)
                if action_key in self.visited_actions and self.visited_actions[action_key] > 2:
                    print(f"   尝试 {attempts}: 动作 {action_key} 已执行过{self.visited_actions[action_key]}次，跳过")
                    continue
                
                # 执行动作获取observation
                tool_result = self._execute_action_and_get_observation(action)
                
                if tool_result is None:
                    print(f"   尝试 {attempts}: 动作执行失败，跳过")
                    continue
                
                observation_dict = tool_result['observation']
                
                # 计算新状态指纹
                state_fingerprint = self._compute_state_fingerprint(observation_dict)
                
                # 检查是否是新状态
                if state_fingerprint in self.visited_states:
                    print(f"   尝试 {attempts}: 状态重复，跳过")
                    continue
                
                # 记录新状态和动作
                self.visited_states.add(state_fingerprint)
                self.visited_actions[action_key] = self.visited_actions.get(action_key, 0) + 1
                
                # 创建新节点
                child_depth = current_node.depth + 1
                child_id = f"explore_d{child_depth}_t{len(self.nodes)}_b{successful_branches}"
                
                child_node = TrajectoryNode(
                    node_id=child_id,
                    observation=self._format_rich_observation(observation_dict),
                    intent=intent,
                    action=action,
                    parent_id=node_id,
                    depth=child_depth
                )
                
                self.nodes[child_id] = child_node
                current_node.children_ids.append(child_id)
                
                successful_branches += 1
                
                print(f"   ✓ 分支 {successful_branches}: 创建节点 {child_id}")
                print(f"     意图: {intent}")
                print(f"     动作: {action.get('tool_name', 'unknown')}")
                print(f"     新颖度: {novelty_score:.2f}")
                print(f"     状态指纹: {state_fingerprint[:16]}...")
                
                # 递归探索子节点
                self._explore_gui_tree(child_id, exploration_seed)
                
            except Exception as e:
                print(f"   ✗ 尝试 {attempts} 失败: {str(e)}")
                continue
    
    def _generate_exploration_action(
        self, 
        current_node: TrajectoryNode,
        exploration_seed: str
    ) -> Tuple[Optional[Dict[str, Any]], str, float]:
        """
        生成探索动作（考虑新颖性和价值）
        
        Returns:
            (action, intent, novelty_score)
        """
        # 构建历史路径
        history = self._build_history(current_node)
        
        # 构建探索prompt
        prompt = self._build_exploration_prompt(
            exploration_seed,
            history,
            current_node.observation
        )

        
        retry = 0
        while retry < self.config.max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.config.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8 + retry * 0.1,  # 探索模式用更高temperature
                    response_format={"type": "json_object"}
                )
                
                result = json.loads(response.choices[0].message.content)
                intent = result.get("intent", "")
                action = result.get("action", {})
                novelty_score = result.get("novelty_score", 0.5)
                
                # 验证动作格式
                if self._validate_action(action):
                    return action, intent, novelty_score
                
                retry += 1
                
            except Exception as e:
                print(f"      警告: 生成动作失败 (尝试 {retry + 1}): {str(e)}")
                retry += 1
        
        return None, "", 0.0
    
    def _build_exploration_prompt(
        self,
        exploration_seed: str,
        history: str,
        current_observation: str
    ) -> str:
        """构建探索prompt（强调发现和新颖性）"""
        
        prompt = f"""You are an intelligent GUI exploration agent. Your goal is to EXPLORE and DISCOVER interesting features and operations, not to complete a specific task.

【Exploration Direction】
{exploration_seed}

【Exploration Principles】
1. CURIOSITY: Try new actions, discover new UI elements and features
2. NOVELTY: Prefer actions that lead to new states you haven't seen
3. DIVERSITY: Explore different types of operations and UI areas
4. VALUE: Focus on discovering meaningful and useful operations

【Current Exploration History】
{history}

【Current UI State】
{current_observation[:1000]}...

【Available Tools】
{self.tool_descriptions}

【Visited Actions (to avoid repetition)】
Most used actions: {self._get_top_actions(5)}

【Your Task】
Based on the current UI state and exploration history, decide the NEXT EXPLORATORY ACTION.

Focus on:
- Discovering new UI elements (menus, buttons, options)
- Exploring different interaction patterns
- Finding hidden or advanced features
- Understanding the application's capabilities

Return JSON format:
{{
    "intent": "What you want to explore/discover (be specific)",
    "action": {{
        "tool_name": "tool name",
        "parameters": {{parameter dictionary}}
    }},
    "novelty_score": 0.0-1.0 (how novel/exploratory is this action)
}}
"""
        
        return prompt
    
    def _compute_state_fingerprint(self, observation_dict: Dict[str, Any]) -> str:
        """
        计算状态指纹（用于去重）
        
        基于可访问性树的内容生成指纹，避免重复访问相同状态
        """
        # 使用a11y树的内容作为状态标识
        a11y_content = observation_dict.get('text', '')
        
        # 截取关键部分（避免太长）
        key_content = a11y_content[:2000] if len(a11y_content) > 2000 else a11y_content
        
        # 生成hash
        fingerprint = hashlib.md5(key_content.encode('utf-8')).hexdigest()
        
        return fingerprint
    
    def _get_action_key(self, action: Dict[str, Any]) -> str:
        """获取动作的键（用于统计重复）"""
        tool_name = action.get('tool_name', '')
        params = action.get('parameters', {})
        
        # 简化参数表示
        param_str = json.dumps(params, sort_keys=True)[:50]
        
        return f"{tool_name}:{param_str}"
    
    def _get_top_actions(self, top_k: int = 5) -> str:
        """获取最常用的动作（用于提示避免）"""
        sorted_actions = sorted(
            self.visited_actions.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        top_actions = sorted_actions[:top_k]
        
        if not top_actions:
            return "None yet"
        
        return ", ".join([f"{action}({count}次)" for action, count in top_actions])
    
    def _format_rich_observation(self, observation_dict: Dict[str, Any]) -> str:
        """
        格式化丰富的observation（包含截图和a11y树的引用）
        
        注意：实际的截图和a11y树数据存储在observation_dict中，
        这里只保存文本描述+数据引用
        """
        text_content = observation_dict.get('text', '')
        has_image = 'image' in observation_dict and observation_dict['image']
        
        # 创建结构化的observation描述
        obs_parts = []
        
        if text_content:
            # 截断太长的文本
            if len(text_content) > 2000:
                obs_parts.append(f"[Accessibility Tree]\n{text_content[:2000]}...[truncated]")
            else:
                obs_parts.append(f"[Accessibility Tree]\n{text_content}")
        
        if has_image:
            obs_parts.append(f"[Screenshot] Available (base64, {len(observation_dict['image'])} chars)")
        
        obs_str = "\n\n".join(obs_parts)
        
        # 将完整的observation_dict存储在节点的metadata中
        # 这样可以在后续处理时访问原始数据
        return obs_str
    
    def _execute_action_and_get_observation(
        self, 
        action: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        执行动作并获取丰富的observation
        
        Returns:
            {
                'status': 'success'/'error',
                'response': str,
                'observation': {
                    'text': str,  # a11y tree
                    'image': str  # base64 screenshot
                }
            }
        """
        tool_name = action["tool_name"]
        parameters = action["parameters"]
        
        try:
            # 执行工具
            result_str = self.environment.execute_tool(tool_name, parameters)
            
            # 解析结果
            try:
                result = json.loads(result_str)
            except json.JSONDecodeError:
                result = {
                    'status': 'unknown',
                    'response': result_str,
                    'observation': {}
                }
            
            # 如果工具返回中包含observation，直接使用
            if 'observation' in result and result['observation']:
                return result
            
            # 否则，主动获取当前observation
            raw_obs = self.environment.get_obs()
            obs_dict = self.environment.format_observation_by_type(
                raw_obs,
                output_format="dict"
            )
            
            result['observation'] = obs_dict
            
            return result
            
        except Exception as e:
            print(f"      执行动作失败: {str(e)}")
            return None
    
    def _validate_action(self, action: Dict[str, Any]) -> bool:
        """验证动作格式"""
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
    
    def _build_history(self, node: TrajectoryNode) -> str:
        """构建历史路径"""
        path = []
        current = node
        
        while current.parent_id is not None:
            path.append(current)
            current = self.nodes[current.parent_id]
        
        path.reverse()
        
        if not path:
            return "刚开始探索，还没有历史记录"
        
        history_str = ""
        for i, n in enumerate(path, 1):
            history_str += f"\n步骤 {i}:\n"
            history_str += f"  意图: {n.intent}\n"
            if n.action:
                history_str += f"  动作: {n.action.get('tool_name', 'unknown')}\n"
            # 只包含observation的关键部分
            obs_preview = n.observation[:200] + "..." if len(n.observation) > 200 else n.observation
            history_str += f"  观察: {obs_preview}\n"
        
        return history_str
    
    def save_exploration_tree(self, output_path: str, exploration_seed: str):
        """
        保存完整的探索树（丰富格式）
        
        保存内容：
        - 每个节点的完整information
        - 截图（base64）
        - 可访问性树
        - 动作和intent
        - 轨迹关系
        """
        exploration_data = {
            "exploration_seed": exploration_seed,
            "timestamp": datetime.now().isoformat(),
            "total_nodes": len(self.nodes),
            "total_unique_states": len(self.visited_states),
            "action_statistics": dict(self.visited_actions),
            "tree_structure": {
                "root_id": self.root_id,
                "nodes": {}
            }
        }
        
        # 保存每个节点
        for node_id, node in self.nodes.items():
            node_data = {
                "node_id": node.node_id,
                "depth": node.depth,
                "parent_id": node.parent_id,
                "children_ids": node.children_ids,
                "intent": node.intent,
                "action": node.action,
                "observation": node.observation,  # 包含截图和a11y树的引用
            }
            
            exploration_data["tree_structure"]["nodes"][node_id] = node_data
        
        # 保存到文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(exploration_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 探索树已保存到: {output_path}")
        print(f"   节点数: {len(self.nodes)}")
        print(f"   唯一状态数: {len(self.visited_states)}")

