"""
Simplified Trajectory Sampler for RAG synthesis
"""

import json
import hashlib
from typing import Dict, List, Optional, Any
import uuid
import bdb
import asyncio
from sandbox import format_tool_result
from .models import TrajectoryNode
from .config import SynthesisConfig
from .worker import SandboxWorker
from .utils import create_openai_client, parse_action_xml, async_chat_completion

# Import tool schemas from tools module
import sys
from pathlib import Path
# Add parent directory to path to import tools module
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
from tools import get_tool_schemas


class TrajectorySampler:
    """Samples trajectory trees by exploring with LLM + tools"""

    def __init__(self, worker: SandboxWorker, config: SynthesisConfig):
        """Initialize sampler"""
        self.worker = worker
        self.config = config

        # Initialize OpenAI client
        self.client = create_openai_client(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
        )

        # Tree storage
        self.nodes: Dict[str, TrajectoryNode] = {}
        self.root_id: Optional[str] = None

        # Available tools (will be populated after worker starts)
        self.available_tools: List[Dict[str, Any]] = []

        # Per-seed action de-duplication
        self._seed_used_action_signatures: set = set()
        self._seed_used_action_signatures_ordered: List[str] = []

    async def sample_trajectory_tree(
        self,
        seed_data: str,
        seed_kwargs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, TrajectoryNode]:
        """Sample a trajectory tree starting from seed data (async)"""
        if seed_kwargs is None:
            seed_kwargs = {}

        print(f"\n{'='*60}")
        print(f"Starting Trajectory Sampling")
        print(f"Seed: {seed_data[:100]}...")
        if seed_kwargs:
            print(f"Kwargs: {seed_kwargs}")
        print(f"{'='*60}\n")

        # Reset tree
        self.nodes = {}
        self.root_id = None
        self._seed_used_action_signatures.clear()
        self._seed_used_action_signatures_ordered.clear()

        # Store kwargs for use in action execution
        self.seed_kwargs = seed_kwargs

        # Load tool schemas from local tools module
        self.available_tools = get_tool_schemas(
            self.config.available_tools if self.config.available_tools else None
        )
        print(f"Available tools: {[t.get('name', 'unknown') for t in self.available_tools]}")

        # Create root node
        root_id = self._generate_node_id()
        root_node = TrajectoryNode(
            node_id=root_id,
            observation=f"Starting point: {seed_data}",
            intent="Initialize exploration",
            action=None,
            parent_id=None,
            children_ids=[],
            depth=0
        )
        self.nodes[root_id] = root_node
        self.root_id = root_id

        # Explore tree asynchronously
        await self._explore_node(root_node, seed_data)

        print(f"\n✅ Sampling complete. Total nodes: {len(self.nodes)}")
        return self.nodes

    async def _explore_node(self, node: TrajectoryNode, seed_data: str):
        """Explore from a node (async breadth-first for siblings)"""
        if node.depth >= self.config.max_depth:
            return

        # Determine how many children to create
        num_children = self.config.branching_factor if node.depth < self.config.depth_threshold else 1

        # Create tasks for all children at this level
        child_tasks = []
        for i in range(num_children):
            child_tasks.append(self._create_and_explore_child(node, seed_data))

        # Execute all children concurrently
        await asyncio.gather(*child_tasks, return_exceptions=True)

    async def _create_and_explore_child(self, parent_node: TrajectoryNode, seed_data: str):
        """Create and explore a single child node"""
        max_retries = 3
        retry_wait = 0.5
        intent = ""
        action: Optional[Dict[str, Any]] = None
        observation = ""
        for attempt in range(max_retries + 1):
            try:
                # Generate next action
                intent, action = await self._generate_next_action(parent_node, seed_data)
                if not action:
                    return

                # Execute action asynchronously
                observation = await self._execute_action(action)
                break
            except Exception as e:
                if attempt >= max_retries:
                    print(f"  ⚠️ Error exploring node: {e}")
                    return
                await asyncio.sleep(retry_wait * (2 ** attempt))

        # Create child node
        child_id = self._generate_node_id()
        child_node = TrajectoryNode(
            node_id=child_id,
            observation=observation,
            intent=intent,
            action=action,
            parent_id=parent_node.node_id,
            children_ids=[],
            depth=parent_node.depth + 1
        )

        self.nodes[child_id] = child_node
        parent_node.children_ids.append(child_id)

        node_index = len(self.nodes)
        action_data = action or {}
        print(
            f"\033[36m[#={node_index} Id={child_node.node_id} Depth={child_node.depth} "
            f"\033[33m{action_data.get('tool_name', 'unknown')}\033[36m]\033[0m:\n"
            f"{intent}"
        )
        print(f"\033[36m[params]:\n\033[0m {json.dumps(action_data.get('parameters', {}), ensure_ascii=False)}")
        preview = observation[:1000] + "...\n\n" if len(observation) > 1000 else observation
        print(f"\033[36m[output]:\n\033[0m {preview}")

        # Recursively explore this child
        await self._explore_node(child_node, seed_data)
        return

    async def _generate_next_action(self, node: TrajectoryNode, seed_data: str) -> tuple[str, Optional[Dict[str, Any]]]:
        """Generate next action using LLM (async)"""
        # Build context
        context = self._build_context(node, seed_data)

        # Build used actions block
        used_actions_block = self._format_used_actions_for_prompt()

        # Build prompt
        prompt = self._build_exploration_prompt(context, seed_data, used_actions_block)

        try:
            response = await async_chat_completion(
                self.client,
                model=self.config.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            content = response.choices[0].message.content
            result = parse_action_xml(content)
            intent = result.get("intent", "")
            action = result.get("action", {})

            if action and isinstance(action, dict):
                # Check for duplicate action
                sig = self._action_signature(action, intent=intent)
                if sig in self._seed_used_action_signatures:
                    print(f"  ⚠️ Duplicate action detected, skipping: {sig}")
                    return "", None
                # Record the action signature
                self._seed_used_action_signatures.add(sig)
                self._seed_used_action_signatures_ordered.append(sig)

            return intent, action

        except Exception as e:
            if isinstance(e, bdb.BdbQuit):
                raise e
            print(f"  ⚠️ LLM generation failed: {e}")
            return "", None

    async def _execute_action(self, action: Dict[str, Any]) -> str:
        """Execute an action via worker (async)"""
        tool_name = action.get("tool_name", "")
        parameters = action.get("parameters", {})
        try:
            # Execute tool asynchronously using worker's async method
            # Pass seed_kwargs to worker
            result = await self.worker.execute_tool(tool_name, parameters, **self.seed_kwargs)

            # Use format_tool_result to format the result for agent consumption
            # This handles the new sandbox response format automatically
            formatted_result = format_tool_result(result, verbose=False)
            return formatted_result
        except Exception as e:
            print(f"Error executing {tool_name}: {str(e)}")
            return f"Error executing {tool_name}: {str(e)}"

    def _build_context(self, node: TrajectoryNode, seed_data: str) -> str:
        """Build context from current path"""
        context = f"Starting point: {seed_data}\n\n"

        # Trace back to root
        path = []
        current = node
        while current.parent_id:
            path.append(current)
            current = self.nodes[current.parent_id]
        path.reverse()

        # Format path
        for i, n in enumerate(path, 1):
            context += f"Step {i}:\n"
            context += f"  Intent: {n.intent}\n"
            if n.action:
                context += f"  Action: {n.action.get('tool_name', 'unknown')}\n"
                context += f"  Parameters: {json.dumps(n.action.get('parameters', {}), ensure_ascii=False)}\n"
            obs_preview = n.observation[:500] + "..." if len(n.observation) > 500 else n.observation
            context += f"  Observation: {obs_preview}\n\n"

        return context

    def _build_exploration_prompt(self, context: str, seed_data: str, used_actions_block: str = "") -> str:
        """Build prompt for exploration"""
        # Generate detailed tool descriptions with parameters
        tool_descriptions = []
        for tool in self.available_tools:
            desc = f"\n{len(tool_descriptions) + 1}. {tool['name']}: {tool['description']}\n"
            desc += "   Parameters:\n"
            for param in tool.get("parameters", []):
                param_type = param.get("type", "string")
                if param_type == "array":
                    param_type = f"array of {param.get('array_type', 'string')}"
                required_str = " (required)" if param.get("required", False) else " (optional)"
                desc += f"   - {param['name']} ({param_type}){required_str}: {param.get('description', '')}\n"
            tool_descriptions.append(desc)

        tool_descriptions_str = "\n".join(tool_descriptions)

        system_instruction = "You are an intelligent Agent using available tools for exploration and reasoning."

        prompt = f"""{system_instruction}

[Starting Point Information]
Content: {seed_data}"""

        if self.config.seed_description:
            prompt += f"\nDescription: {self.config.seed_description}"

        prompt += """

[Exploration Goal]:
Based on the starting point content and available tools, conduct systematic exploration to collect and reason about valuable information.
Finally, I will synthesize a question and answer based on your collected information. Therefore, you should explore sufficient information for me.
"""
        if used_actions_block:
            prompt += f"""
[Already Explored Actions - Do NOT Repeat]:
The following tool calls (tool_name + parameters) have ALREADY been executed for this seed.
You MUST propose a NEW action that is NOT in this list or similar to them to increase the diversity of the exploration. Repeating any of them is strictly forbidden.
{used_actions_block}
"""

        if self.config.sampling_tips:
            prompt += f"""[Exploration Strategy and Focus]:
{self.config.sampling_tips}

"""

        prompt += f"""[Current History Trajectory]:
{context}

[Current Observation]:
{context.split('Observation:')[-1] if 'Observation:' in context else 'Starting exploration'}

[Available Tools]:
{tool_descriptions_str}

"""

        prompt += """
Based on the current state and available tools, select an appropriate tool and parameters, and generate the next action and intent.

IMPORTANT: Return ONLY a valid XML block without other words or markdown.
Format:
<intent>...</intent>
<tool_name>tool name</tool_name>
<parameters>{"param": "value"}</parameters>
"""
        return prompt

    def _generate_node_id(self) -> str:
        """Generate unique node ID"""
        return f"node_{uuid.uuid4().hex[:8]}"

    def _action_signature(self, action: Dict[str, Any], intent: Optional[str] = None) -> str:
        """
        Canonical signature for action de-duplication within a seed.
        Format: tool_name + canonicalized JSON(parameters)
        """
        tool_name = ""
        parameters: Any = {}
        try:
            tool_name = str(action.get("tool_name", ""))
            parameters = action.get("parameters", {}) if isinstance(action, dict) else {}
        except Exception:
            tool_name = ""
            parameters = {}

        def _shrink_obj(obj: Any, max_str_len: int = 160) -> Any:
            try:
                if isinstance(obj, str):
                    if len(obj) <= max_str_len:
                        return obj
                    h = hashlib.md5(obj.encode("utf-8")).hexdigest()[:10]
                    return f"<str:{len(obj)}:md5:{h}>"
                if isinstance(obj, dict):
                    return {str(k): _shrink_obj(v, max_str_len=max_str_len) for k, v in obj.items()}
                if isinstance(obj, list):
                    return [_shrink_obj(v, max_str_len=max_str_len) for v in obj]
                return obj
            except Exception:
                return str(obj)

        try:
            safe_params = _shrink_obj(parameters)
            params_str = json.dumps(safe_params, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        except Exception:
            params_str = str(parameters)

        return f"{tool_name}({params_str})"

    def _format_used_actions_for_prompt(self, max_items: int = 40, max_line_chars: int = 300) -> str:
        """Format executed actions list for inclusion in prompt (truncate to keep prompt bounded)."""
        if not self._seed_used_action_signatures_ordered:
            return "None yet."

        items = self._seed_used_action_signatures_ordered[-max_items:]
        lines = []
        for i, sig in enumerate(items, 1):
            s = sig
            if len(s) > max_line_chars:
                s = s[:max_line_chars] + "...(truncated)"
            lines.append(f"- {i}. {s}")

        omitted = len(self._seed_used_action_signatures_ordered) - len(items)
        if omitted > 0:
            lines.insert(0, f"(Showing last {len(items)} actions; {omitted} earlier actions omitted but still forbidden.)")

        return "\n".join(lines)
