"""
Sandbox Worker - adapter for using new sandbox with synthesis pipeline
"""

import sys
import os
import asyncio
from typing import List, Dict, Any, Optional
import pdb
import bdb

# Import from sandbox package
from sandbox import Sandbox

from .config import SynthesisConfig


class SandboxWorker:
    """Worker that uses the new sandbox for RAG synthesis"""

    def __init__(self, config: SynthesisConfig, worker_id: Optional[str] = None):
        """Initialize worker"""
        self.config = config
        self.worker_id = worker_id or f"worker_{os.getpid()}"

        # Create sandbox instance with simplified configuration
        self.sandbox = Sandbox(
            server_url=config.sandbox_server_url,
            worker_id=self.worker_id,
            auto_start_server=config.sandbox_auto_start,
            server_config_path=config.sandbox_config_path,
            timeout=config.sandbox_timeout,
            warmup_resources=config.resource_types if config.resource_types else None
        )

        self._started = False
        self._sessions_created = False

    async def start(self, create_sessions: bool = True) -> bool:
        """Start worker and sandbox"""
        if self._started:
            return True

        try:
            print(f"[Worker {self.worker_id}] Starting sandbox...")
            # Start sandbox (this will auto-start server, connect, and warmup resources)
            await self.sandbox.start()
            # Create sessions for required resources (optional)
            if create_sessions and self.config.resource_types:
                print(f"[Worker {self.worker_id}] Creating sessions for: {self.config.resource_types}")

                # Build resource configs dict
                resource_configs = {}
                for resource_type in self.config.resource_types:
                    # Get init config for this resource
                    init_config = self.config.resource_init_configs.get(resource_type, {})
                    # Extract content if it exists, otherwise use empty dict
                    resource_configs[resource_type] = init_config.get("content", {}) if init_config else {}

                # Create all sessions at once
                result = await self.sandbox.create_session(resource_configs)

                if result.get("status") in ("success", "partial"):
                    self._sessions_created = True
                    print(f"[Worker {self.worker_id}] ✅ Sessions created: {result.get('success')}/{result.get('total')}")
                else:
                    print(f"[Worker {self.worker_id}] ⚠️ Session creation failed: {result}")
                    return False

            self._started = True
            print(f"[Worker {self.worker_id}] ✅ Started successfully")
            return True

        except Exception as e:
            if isinstance(e, bdb.BdbQuit):
                raise e
            print(f"[Worker {self.worker_id}] ❌ Failed to start: {e}")
            import traceback
            traceback.print_exc()
            await self.stop()
            return False

    async def stop(self) -> None:
        """Stop worker and cleanup"""
        try:
            if self._sessions_created and self.config.resource_types:
                print(f"[Worker {self.worker_id}] Destroying sessions...")
                # Destroy all sessions at once
                await self.sandbox.destroy_session(self.config.resource_types)

            print(f"[Worker {self.worker_id}] Closing sandbox...")
            await self.sandbox.close()

            self._started = False
            self._sessions_created = False
            print(f"[Worker {self.worker_id}] ✅ Stopped")

        except Exception as e:
            print(f"[Worker {self.worker_id}] ⚠️ Error during stop: {e}")

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], **kwargs) -> Any:
        """Execute a tool via sandbox"""
        if not self._started:
            raise RuntimeError(f"Worker {self.worker_id} not started")
        try:
            result = await self.sandbox.execute(tool_name, parameters, **kwargs)
            return result
        except Exception as e:
            print(f"[Worker {self.worker_id}] ❌ Tool execution failed: {tool_name} - {e}")
            raise

    def execute_tool_sync(self, tool_name: str, parameters: Dict[str, Any], **kwargs) -> Any:
        """Synchronous wrapper for tool execution"""
        try:
            # Check if there's already a running event loop
            loop = asyncio.get_running_loop()
            # If we're in an event loop, we need to run in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.execute_tool(tool_name, parameters, **kwargs))
                return future.result()
        except RuntimeError:
            # No running loop - safe to use asyncio.run
            return asyncio.run(self.execute_tool(tool_name, parameters, **kwargs))

    def is_started(self) -> bool:
        """Check if worker is started"""
        return self._started
