"""
Agent Runner - executes agent on tasks using sandbox tools

Handles multi-turn conversation with tool calling.
"""

import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
import bdb

# Import sandbox components directly to avoid server module dependencies
from sandbox import Sandbox, format_tool_result

from .config import RolloutConfig
from .models import (
    BenchmarkItem, Trajectory, Message, ToolCall, TaskResult
)
from .utils import (
    create_openai_client,
    async_chat_completion,
    extract_final_answer,
    convert_tool_schema_to_openai,
    format_tool_result_for_message
)


class AgentRunner:
    """
    Agent Runner that executes tasks using sandbox tools.
    
    Supports multi-turn conversation with tool calling through OpenAI API.
    """

    def __init__(self, config: RolloutConfig, worker_id: Optional[str] = None):
        """Initialize agent runner"""
        self.config = config
        self.worker_id = worker_id or f"runner_{int(time.time())}"
        
        # Create OpenAI client
        self.client = create_openai_client(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
        )
        
        # Sandbox instance (will be created in start())
        self.sandbox: Optional[Sandbox] = None
        
        # Tool schemas (OpenAI format)
        self.tool_schemas: List[Dict[str, Any]] = []
        
        # Local tool schemas for prompts
        self._local_tool_schemas: List[Dict[str, Any]] = []
        
        self._started = False

    async def start(self) -> bool:
        """Start the runner (initialize sandbox and load tools)"""
        if self._started:
            return True
        
        try:
            print(f"[Runner {self.worker_id}] Starting...")
            
            # Create sandbox instance
            self.sandbox = Sandbox(
                server_url=self.config.sandbox_server_url,
                worker_id=self.worker_id,
                auto_start_server=self.config.sandbox_auto_start,
                server_config_path=self.config.sandbox_config_path,
                timeout=self.config.sandbox_timeout,
                warmup_resources=self.config.resource_types if self.config.resource_types else None
            )
            
            # Start sandbox
            await self.sandbox.start()
            
            # Create sessions for required resources
            if self.config.resource_types:
                print(f"[Runner {self.worker_id}] Creating sessions for: {self.config.resource_types}")
                
                resource_configs = {}
                for resource_type in self.config.resource_types:
                    init_config = self.config.resource_init_configs.get(resource_type, {})
                    resource_configs[resource_type] = init_config.get("content", {}) if init_config else {}
                
                result = await self.sandbox.create_session(resource_configs)
                
                if result.get("status") not in ("success", "partial"):
                    print(f"[Runner {self.worker_id}] ⚠️ Session creation issue: {result}")
            
            # Load tool schemas
            await self._load_tool_schemas()
            
            self._started = True
            print(f"[Runner {self.worker_id}] ✅ Started successfully")
            print(f"[Runner {self.worker_id}] Available tools: {[t['function']['name'] for t in self.tool_schemas]}")
            return True
            
        except Exception as e:
            if isinstance(e, bdb.BdbQuit):
                raise
            print(f"[Runner {self.worker_id}] ❌ Failed to start: {e}")
            import traceback
            traceback.print_exc()
            await self.stop()
            return False

    async def stop(self) -> None:
        """Stop the runner and cleanup"""
        try:
            if self.sandbox:
                # Destroy sessions
                if self.config.resource_types:
                    await self.sandbox.destroy_session(self.config.resource_types)
                
                # Close sandbox
                await self.sandbox.close()
                self.sandbox = None
            
            self._started = False
            print(f"[Runner {self.worker_id}] ✅ Stopped")
            
        except Exception as e:
            print(f"[Runner {self.worker_id}] ⚠️ Error during stop: {e}")

    async def _load_tool_schemas(self) -> None:
        """Load tool schemas from sandbox or local definitions"""
        # Import local tool schemas
        from sandbox.tool_schemas import get_tool_schemas
        
        # Get schemas for allowed tools
        allowed_tools = self.config.available_tools if self.config.available_tools else None
        self._local_tool_schemas = get_tool_schemas(allowed_tools)
        
        # Convert to OpenAI format
        self.tool_schemas = [
            convert_tool_schema_to_openai(schema)
            for schema in self._local_tool_schemas
        ]

    async def run_task(self, task: BenchmarkItem) -> TaskResult:
        """
        Run agent on a single task.
        
        Args:
            task: Benchmark task item
            
        Returns:
            TaskResult with predicted answer and trajectory
        """
        if not self._started:
            raise RuntimeError("Runner not started. Call start() first.")
        
        print(f"\n{'='*60}")
        print(f"Task: {task.id}")
        print(f"Question: {task.question[:200]}...")
        print(f"{'='*60}")
        
        start_time = time.time()
        trajectory = Trajectory(
            task_id=task.id,
            question=task.question,
            start_time=datetime.now().isoformat()
        )
        
        try:
            # Build initial messages
            system_prompt = self.config.get_system_prompt()
            messages = [
                Message(role="system", content=system_prompt),
                Message(role="user", content=task.question)
            ]
            trajectory.messages = messages.copy()
            
            # Run conversation loop
            final_answer = await self._run_conversation(messages, trajectory)
            
            trajectory.final_answer = final_answer
            trajectory.success = True
            trajectory.end_time = datetime.now().isoformat()
            trajectory.execution_time_ms = (time.time() - start_time) * 1000
            
            print(f"✅ Task {task.id} completed")
            print(f"   Final answer: {final_answer[:100]}...")
            
            return TaskResult(
                task_id=task.id,
                question=task.question,
                predicted_answer=final_answer,
                ground_truth=task.answer,
                trajectory=trajectory if self.config.save_trajectories else None,
                success=True
            )
            
        except Exception as e:
            if isinstance(e, bdb.BdbQuit):
                raise
            
            trajectory.success = False
            trajectory.error = str(e)
            trajectory.end_time = datetime.now().isoformat()
            trajectory.execution_time_ms = (time.time() - start_time) * 1000
            
            print(f"❌ Task {task.id} failed: {e}")
            
            return TaskResult(
                task_id=task.id,
                question=task.question,
                predicted_answer="",
                ground_truth=task.answer,
                trajectory=trajectory if self.config.save_trajectories else None,
                success=False,
                error=str(e)
            )

    async def _run_conversation(
        self,
        messages: List[Message],
        trajectory: Trajectory
    ) -> str:
        """
        Run multi-turn conversation until completion.
        
        Returns final answer string.
        """
        turn_count = 0
        
        while turn_count < self.config.max_turns:
            # Prepare messages for API
            api_messages = [m.to_dict() for m in messages]
            
            # Get response from LLM
            response = await async_chat_completion(
                self.client,
                model=self.config.model_name,
                messages=api_messages,
                tools=self.tool_schemas if self.tool_schemas else None,
                max_retries=self.config.max_retries
            )
            
            assistant_message = response.choices[0].message
            
            # Convert to our Message format
            msg = Message(
                role="assistant",
                content=assistant_message.content or "",
                tool_calls=[tc.model_dump() for tc in assistant_message.tool_calls] if assistant_message.tool_calls else None
            )
            messages.append(msg)
            trajectory.messages.append(msg)
            trajectory.total_turns = turn_count + 1
            
            # Check if there are tool calls
            if assistant_message.tool_calls:
                # Execute tool calls
                for tool_call in assistant_message.tool_calls[:1]:  # Execute one at a time
                    tool_name = tool_call.function.name
                    try:
                        tool_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        tool_args = {}
                    
                    print(f"  Turn {turn_count}: 🔧 {tool_name}")
                    print(f"    Args: {json.dumps(tool_args, ensure_ascii=False)[:200]}...")
                    
                    # Execute tool
                    tool_result = await self._execute_tool(tool_name, tool_args)
                    
                    # Record tool call
                    tc = ToolCall(
                        tool_name=tool_name,
                        parameters=tool_args,
                        result=tool_result.get("data") if isinstance(tool_result, dict) else tool_result,
                        success=tool_result.get("code", 0) == 0 if isinstance(tool_result, dict) else True
                    )
                    trajectory.tool_calls.append(tc)
                    
                    # Format result for message
                    result_text = format_tool_result_for_message(tool_result)
                    print(f"    Result: {result_text[:200]}...")
                    
                    # Add tool result message
                    tool_msg = Message(
                        role="tool",
                        content=result_text,
                        tool_call_id=tool_call.id,
                        name=tool_name
                    )
                    messages.append(tool_msg)
                    trajectory.messages.append(tool_msg)
                
                turn_count += 1
                continue
            
            else:
                # No tool calls, this is the final response
                final_answer = assistant_message.content or ""
                return extract_final_answer(final_answer)
        
        # Max turns reached
        print(f"⚠️ Max turns ({self.config.max_turns}) reached")
        
        # Try to extract answer from last assistant message
        for msg in reversed(messages):
            if msg.role == "assistant" and msg.content:
                return extract_final_answer(msg.content)
        
        return "Max turns reached without answer"

    async def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a tool via sandbox"""
        if not self.sandbox:
            raise RuntimeError("Sandbox not initialized")
        
        try:
            result = await self.sandbox.execute(tool_name, parameters)
            return result
        except Exception as e:
            print(f"    ❌ Tool execution error: {e}")
            return {"code": -1, "message": str(e), "data": None}


class SyncAgentRunner:
    """Synchronous wrapper for AgentRunner"""
    
    def __init__(self, config: RolloutConfig, worker_id: Optional[str] = None):
        self._runner = AgentRunner(config, worker_id)
    
    def _run_async(self, coro):
        """Run async coroutine in sync context"""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    def start(self) -> bool:
        return self._run_async(self._runner.start())
    
    def stop(self) -> None:
        self._run_async(self._runner.stop())
    
    def run_task(self, task: BenchmarkItem) -> TaskResult:
        return self._run_async(self._runner.run_task(task))
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
