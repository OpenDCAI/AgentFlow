"""
Trajectory Sampler

Responsible for sampling trajectory tree starting from seed entity
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
    Generic Trajectory Sampler supporting arbitrary tool combinations
    """
    
    def __init__(self, 
                 environment: Environment,
                 config: SynthesisConfig):
        """
        Initialize Generic Trajectory Sampler
        
        Args:
            environment: Environment instance (any type)
            config: Synthesis configuration
        """
        self.environment = environment
        self.config = config
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_API_URL", os.environ.get("OPENAI_API_BASE", ""))
        )
        
        # Get available tools information
        self.available_tools = self._get_available_tools()
        self.tool_descriptions = self._generate_tool_descriptions()
        
        # Trajectory tree storage
        self.nodes: Dict[str, TrajectoryNode] = {}
        self.root_id: Optional[str] = None
        
    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Get available tools information from environment"""
        tools = []
        
        # If tools list is specified in config, only use these tools
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
        """Generate tool description text"""
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
    
    def sample_trajectory_tree(self, seed_data: str) -> Dict[str, TrajectoryNode]:
        """
        Sample trajectory tree starting from seed
        
        Args:
            seed_data: Starting point data (string, can be any content: entity name, URL, question description, text, etc.)
            
        Returns:
            Complete trajectory tree
        """
        print(f"\n{'='*60}")
        print(f"Starting Trajectory Tree Sampling")
        print(f"Seed Content: {seed_data}")
        print(f"Environment Mode: {self.environment.mode}")
        print(f"Available Tools: {[t['name'] for t in self.available_tools]}")
        print(f"Max Depth: {self.config.max_depth}, Branching Factor: {self.config.branching_factor}")
        print(f"{'='*60}\n")
        
        # Create root node
        # root_id format: node_d{depth}_t{total_nodes}_b{branch_number}
        root_id = f"d0_t0_b0"
        observation = f"Starting point: {seed_data}"
        if self.config.seed_description:
            observation = f"Starting point ({self.config.seed_description}): {seed_data}"
        
        root_node = TrajectoryNode(
            node_id=root_id,
            observation=observation,
            intent="Start exploration",
            action=None,
            parent_id=None,
            depth=0
        )
        
        self.nodes[root_id] = root_node
        self.root_id = root_id
        
        # BFS expand tree
        self._expand_tree(root_id, seed_data)
        
        print(f"\n✅ Trajectory Tree Sampling Completed!")
        print(f"   Total Nodes: {len(self.nodes)}")
        print(f"   Max Depth: {max(node.depth for node in self.nodes.values())}")
        
        return self.nodes
    
    def _expand_tree(self, node_id: str, seed_data: str):
        """Recursively expand trajectory tree"""
        current_node = self.nodes[node_id]
        
        # Check depth limit
        if current_node.depth >= self.config.max_depth:
            return
        
        print(f"\n🌳 Expanding node {node_id} (depth: {current_node.depth})")
        
        # Dynamically adjust branching factor based on depth
        if current_node.depth >= self.config.depth_threshold:
            current_branching_factor = 1
            print(f"   ⚠️  Depth {current_node.depth} >= threshold {self.config.depth_threshold}, branching factor reduced to 1")
        else:
            current_branching_factor = self.config.branching_factor
        
        # Sample branching_factor times for current node
        for branch_idx in range(current_branching_factor):
            try:
                # Generate next action and intent
                action, intent = self._generate_next_action(current_node, seed_data)
                
                if action is None:
                    print(f"   Branch {branch_idx + 1}: Unable to generate valid action, skipping")
                    continue
                
                # Execute action to get observation
                observation = self._execute_action(action)
                
                # Create new node
                # child_id format: node_d{depth}_t{total_nodes}_b{branch_number}
                child_depth = current_node.depth + 1
                total_nodes = len(self.nodes)
                child_id = f"d{child_depth}_t{total_nodes}_b{branch_idx}"
                child_node = TrajectoryNode(
                    node_id=child_id,
                    observation=observation,
                    intent=intent,
                    action=action,
                    parent_id=node_id,
                    depth=child_depth
                )
                
                self.nodes[child_id] = child_node
                current_node.children_ids.append(child_id)
                
                print(f"   ✓ Branch {branch_idx + 1}: Created node {child_id}")
                print(f"     Intent: {intent}")
                print(f"     Action: {action.get('tool_name', 'unknown')}")
                print(f"     Parameters: {action.get('parameters', {})}")
                print(f"     Observation: {observation[:100]}...")
                
                # Recursively expand child node
                self._expand_tree(child_id, seed_data)
                
            except Exception as e:
                if isinstance(e, bdb.BdbQuit):
                    raise e
                print(f"   ✗ Branch {branch_idx + 1} failed: {str(e)}")
                continue
    
    def _generate_next_action(self, 
                              current_node: TrajectoryNode, 
                              seed_data: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Generate next action and intent based on current state
        """
        # Build history trajectory
        history = self._build_history(current_node)
        
        # Build prompt (generic version, based on configuration)
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
                
                # Validate action format
                if self._validate_action(action):
                    return action, intent
                
                retry += 1
                
            except Exception as e:
                print(f"      Warning: Failed to generate action (attempt {retry + 1}): {str(e)}")
                retry += 1
        
        return None, ""
    
    def _build_action_generation_prompt(self, seed_data: str, history: str, current_observation: str) -> str:
        """Build action generation prompt (dynamically generated based on configuration)"""
        
        # Generic prompt template
        prompt = f"""You are an intelligent Agent using available tools for exploration and reasoning.

[Starting Point Information]
Content: {seed_data}"""
        
        if self.config.seed_description:
            prompt += f"\nDescription: {self.config.seed_description}"
        
        prompt += """

[Exploration Goal]
Based on the starting point content and available tools, conduct systematic exploration to collect and reason about valuable information.

"""
        
        # Add user-defined sampling tips
        if self.config.sampling_tips:
            prompt += f"""[Exploration Strategy and Focus]
{self.config.sampling_tips}

"""
        
        # Add history trajectory
        prompt += f"""Current History Trajectory:
{history}

Current Observation:
{current_observation}

"""
        
        # Add tool descriptions
        prompt += f"""Available Tools:
{self.tool_descriptions}

"""
        
        # Add QA examples (if any)
        if self.config.qa_examples:
            prompt += """Reference Examples (to understand expected data types):\n"""
            for i, example in enumerate(self.config.qa_examples[:2], 1):  # Show only first 2
                prompt += f"""
Example {i}:
Question: {example.get('question', '')}
Answer: {example.get('answer', '')}
"""
                if 'reasoning' in example:
                    prompt += f"Reasoning: {example['reasoning']}\n"
        
        # Add output format requirements
        prompt += """
Based on the current state and available tools, select an appropriate tool and parameters, and generate the next action and intent.

Return JSON format:
{
    "intent": "The intent and reason for executing this action",
    "action": {
        "tool_name": "tool name",
        "parameters": {parameter dictionary}
    }
}
"""
        
        return prompt
    
    def _validate_action(self, action: Dict[str, Any]) -> bool:
        """Validate whether action format is correct (generic version)"""
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
        """Execute action and return observation"""
        tool_name = action["tool_name"]
        parameters = action["parameters"]
        
        try:
            result = self.environment.execute_tool(tool_name, parameters)
            return result
        except Exception as e:
            return f"[Error] Action execution failed: {str(e)}"
    
    def _build_history(self, node: TrajectoryNode) -> str:
        """Build history trajectory from root to current node"""
        path = []
        current = node
        
        while current.parent_id is not None:
            path.append(current)
            current = self.nodes[current.parent_id]
        
        path.reverse()
        
        if not path:
            return "No history trajectory"
        
        history_str = ""
        for i, n in enumerate(path, 1):
            history_str += f"\nStep {i}:\n"
            history_str += f"  Intent: {n.intent}\n"
            if n.action:
                history_str += f"  Action: {n.action.get('tool_name', 'unknown')}\n"
            history_str += f"  Observation: {n.observation[:200]}...\n"
        
        return history_str

