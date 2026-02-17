# sandbox/server/core/tool_executor.py
"""
Tool executor.

Responsible for tool execution logic by using references passed from Server.
The underlying structures (`_tools`, `_tool_name_index`, `_tool_resource_types`)
are owned by the Server class.

Tool mapping mechanism:
=======================

1. Tool registration
   - Tools are registered via `register_tool(name, func)` or `@tool` scanning.
   - Tool names support the "resource_type:action" format (e.g. "vm:screenshot").
   - Prefix is optional for stateless tools.

2. Tool mapping storage (3-layer structure, owned by Server)
   - `_tools: Dict[str, Callable]`
     Full-name map: `full_name -> function`
   - `_tool_name_index: Dict[str, List[str]]`
     Simple-name index: `simple_name -> [full_names]`
   - `_tool_resource_types: Dict[str, str]`
     Resource map: `full_name -> resource_type`

3. Tool resolution strategy (`resolve_tool`)
   a. Prefer exact match by full name.
   b. Fallback to simple-name index match.
   c. Return an error when no match is found.
"""

import time
import asyncio
import logging
import inspect
import traceback
from typing import Dict, Any, Optional, List, Callable, Tuple, TYPE_CHECKING

from .resource_router import ResourceRouter
from .decorators import scan_tools
from ..backends.error_codes import ErrorCode
from ..backends.response_builder import build_error_response, build_success_response

if TYPE_CHECKING:
    pass

logger = logging.getLogger("ToolExecutor")


class ToolExecutor:
    """
    Tool executor.

    Responsibilities:
    - Execute tool functions.
    - Route by resource prefix to the right session.
    - Inject runtime parameters when needed.

    Data structures are passed from Server and referenced only.
    """
    
    def __init__(
        self,
        tools: Dict[str, Callable],
        tool_name_index: Dict[str, List[str]],
        tool_resource_types: Dict[str, str],
        resource_router: ResourceRouter,
        warmup_callback: Optional[Callable[[str], Any]] = None
    ):
        """
        Initialize the tool executor.

        Args:
            tools: Full-name to function map (by reference).
            tool_name_index: Simple-name to full-name list index (by reference).
            tool_resource_types: Full-name to resource-type map (by reference).
            resource_router: Resource router instance.
            warmup_callback: Optional warmup callback invoked before execution.
        """
        # Keep references to external data structures.
        self._tools = tools
        self._tool_name_index = tool_name_index
        self._tool_resource_types = tool_resource_types
        self._resource_router = resource_router
        self._warmup_callback = warmup_callback

    def _normalize_tool_name(self, action: str) -> str:
        """
        Normalize tool name variants to the canonical "resource:action" format.
        Supports:
        - "resource:action" (already canonical)
        - "resource.action" -> "resource:action"
        - "resource_action" -> "resource:action"
        - "resource-action" -> "resource:action"
        """
        if ":" in action:
            return action

        # Build a set of known resource prefixes from registered tool names.
        resource_prefixes = set()
        for full_name in self._tools.keys():
            if ":" in full_name:
                resource_prefixes.add(full_name.split(":", 1)[0])

        for sep in (".", "_", "-"):
            if sep in action:
                prefix, suffix = action.split(sep, 1)
                candidate = f"{prefix}:{suffix}"
                if prefix in resource_prefixes and candidate in self._tools:
                    return candidate

        return action
    
    def _resolve_tool(self, action: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Resolve tool name and return full name, simple name, and resource type.

        Lookup strategy:
        1. Exact match: treat `action` as full name.
        2. Index match: treat `action` as simple name.
           - Single candidate: return directly.
           - Multiple candidates: return None to force explicit prefix.

        Args:
            action: Action name, e.g. "vm:screenshot" or "screenshot".

        Returns:
            `(full_name, simple_name, resource_type)`, or `(None, None, None)` if not found.
        """
        # Strategy 1: exact full-name match.
        if action in self._tools:
            resource_type = self._tool_resource_types.get(action)
            simple_name = action.split(":")[-1] if ":" in action else action
            return action, simple_name, resource_type
        
        # Strategy 2: prefixed but not matched -> tool does not exist.
        if ":" in action:
            return None, None, None
        
        # Strategy 3: lookup as simple name in index.
        simple_name = action
        if simple_name in self._tool_name_index:
            candidates = self._tool_name_index[simple_name]
            
            if len(candidates) == 1:
                full_name = candidates[0]
                resource_type = self._tool_resource_types.get(full_name)
                return full_name, simple_name, resource_type
            
            elif len(candidates) > 1:
                # Multiple matches -> ambiguous.
                return None, simple_name, None
        
        return None, None, None

    async def execute(
        self, 
        action: str, 
        params: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute one tool action.

        Args:
            action: Action name, with or without resource prefix.
            params: Tool parameters.
            **kwargs: Runtime options.
                - worker_id (str): Worker ID (required)
                - timeout (int, optional): Timeout in seconds
                - trace_id (str, optional): Trace ID for log correlation
                - session_id (str, optional): Explicit session ID

        Returns:
            Execution result dictionary.
        """
        # Extract runtime parameters.
        worker_id = kwargs.get("worker_id")
        if not worker_id:
            raise ValueError("worker_id is required")
        timeout: Optional[int] = kwargs.get("timeout")
        trace_id: Optional[str] = kwargs.get("trace_id")
        
        start_time = time.time()
        tool_name = action  # Default for error reporting.
        is_temporary_session = False
        resource_type = None
        full_name = None

        logger.info(f"🔧 [ToolExecutor] Execute START: action={action}, worker_id={worker_id}, trace_id={trace_id}")

        def _elapsed_ms() -> float:
            return (time.time() - start_time) * 1000

        session_info = None
        try:
            # Normalize tool name variants to canonical format.
            action = self._normalize_tool_name(action)

            # Resolve tool name.
            full_name, simple_name, resource_type = self._resolve_tool(action)
            logger.info(f"   ↳ Resolved: full_name={full_name}, resource_type={resource_type}")
            
            # Verify tool exists.
            if not full_name:
                if action in self._tool_name_index and len(self._tool_name_index[action]) > 1:
                    candidates = self._tool_name_index[action]
                    return build_error_response(
                        code=ErrorCode.INVALID_REQUEST_FORMAT,
                        message=(
                            f"Ambiguous tool name '{action}'. Multiple matches: {candidates}. "
                            f"Please use full name with prefix."
                        ),
                        tool=action,
                        data={"candidates": candidates},
                        execution_time_ms=_elapsed_ms()
                    )
                return build_error_response(
                    code=ErrorCode.INVALID_REQUEST_FORMAT,
                    message=f"Tool not found: {action}",
                    tool=action,
                    data={"action": action},
                    execution_time_ms=_elapsed_ms()
                )
            
            func = self._tools[full_name]
            tool_name = simple_name or action
            
            # Warm up backend automatically when needed.
            if resource_type and self._warmup_callback:
                logger.info(f"   ↳ Warmup backend: {resource_type}")
                warmup_result = self._warmup_callback(resource_type)
                # Await coroutine result when callback is async.
                if asyncio.iscoroutine(warmup_result):
                    await warmup_result
                logger.info(f"   ↳ Warmup completed: {resource_type}")

            # Get or create session when resource type is present.
            session_info = None

            if resource_type:
                logger.info(f"   ↳ Getting session for resource_type={resource_type}")
                existing_session = await self._resource_router.get_session(worker_id, resource_type)

                if existing_session:
                    logger.info(f"   ↳ Using existing session: {existing_session.get('session_id')}")
                    session_info = existing_session
                else:
                    # Auto-create temporary session.
                    logger.info(f"   ↳ Creating temporary session for {resource_type}")
                    session_info = await self._resource_router.get_or_create_session(
                        worker_id=worker_id,
                        resource_type=resource_type,
                        auto_created=True
                    )
                    is_temporary_session = True  # Mark as temporary session.
                    logger.info(f"🔄 Auto-created temporary session for {resource_type} (worker: {worker_id})")
                
                if session_info.get("status") == "error":
                    return build_error_response(
                        code=ErrorCode.RESOURCE_NOT_INITIALIZED,
                        message=f"Resource initialization failed: {session_info.get('error')}",
                        tool=full_name,
                        data={"resource_type": resource_type, "details": session_info.get("error")},
                        execution_time_ms=_elapsed_ms(),
                        resource_type=resource_type,
                        session_id=session_info.get("session_id")
                    )
            
            # Auto-inject runtime parameters.
            sig = inspect.signature(func)
            has_var_keyword = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())

            def inject_if_missing(key, value):
                """Inject if missing and accepted by function signature."""
                if key not in params and value is not None:
                    if key in sig.parameters or has_var_keyword:
                        params[key] = value

            inject_if_missing("worker_id", worker_id)
            inject_if_missing("trace_id", trace_id)
            
            if session_info:
                inject_if_missing("session_id", session_info.get("session_id"))
                inject_if_missing("session_info", session_info)
            
            # Execute tool function.
            logger.info(f"   ↳ Executing tool function: {full_name}")
            result = func(**params)

            # Await coroutine results (including decorated async functions).
            if asyncio.iscoroutine(result):
                logger.info(f"   ↳ Awaiting async result...")
                if timeout:
                    result = await asyncio.wait_for(result, timeout=timeout)
                else:
                    result = await result
                logger.info(f"   ↳ Async result received")

            execution_time = (time.time() - start_time) * 1000
            logger.info(f"✅ [ToolExecutor] Execute COMPLETED: {action} in {execution_time:.2f}ms")

            # Destroy temporary session after execution.
            if is_temporary_session and resource_type:
                await self._resource_router.destroy_session(worker_id, resource_type)
                logger.info(f"🗑️ Destroyed temporary session for {resource_type} (worker: {worker_id})")
            elif resource_type and session_info:
                # For persistent sessions, only refresh TTL.
                logger.info(
                    "🔄 [ToolExecutor] Refresh session after action: %s (worker=%s, session_id=%s)",
                    full_name or tool_name,
                    worker_id,
                    session_info.get("session_id"),
                )
                await self._resource_router.refresh_session(worker_id, resource_type)

            # Validate new response format (must include `code`).
            if isinstance(result, dict) and "code" in result:
                # New format: return directly after filling meta fields.
                meta = result.get("meta") or {}
                if full_name and "tool" not in meta:
                    meta["tool"] = full_name
                if execution_time and "execution_time_ms" not in meta:
                    meta["execution_time_ms"] = execution_time
                if resource_type and "resource_type" not in meta:
                    meta["resource_type"] = resource_type
                if session_info and "session_id" not in meta:
                    meta["session_id"] = session_info.get("session_id")
                if is_temporary_session:
                    meta["temporary_session"] = True
                result["meta"] = meta
                return result

            return build_error_response(
                code=ErrorCode.UNEXPECTED_ERROR,
                message="Tool returned legacy response format; expected {code, message, data, meta}",
                tool=full_name or tool_name,
                data={"returned_type": type(result).__name__},
                execution_time_ms=execution_time,
                resource_type=resource_type,
                session_id=session_info.get("session_id") if session_info else None
            )
            
        except asyncio.TimeoutError:
            # Ensure temporary session cleanup on timeout.
            if is_temporary_session and resource_type:
                await self._resource_router.destroy_session(worker_id, resource_type)
            return build_error_response(
                code=ErrorCode.TIMEOUT_ERROR,
                message=f"Tool execution timed out after {timeout}s",
                tool=full_name or tool_name,
                data={"timeout": timeout},
                execution_time_ms=_elapsed_ms(),
                resource_type=resource_type,
                session_id=session_info.get("session_id") if session_info else None
            )
        except Exception as e:
            # Ensure temporary session cleanup on exceptions.
            if is_temporary_session and resource_type:
                try:
                    await self._resource_router.destroy_session(worker_id, resource_type)
                except Exception:
                    pass  # Cleanup failure should not mask the main error.
            logger.error(f"Tool execution failed: {tool_name} - {e}\n{traceback.format_exc()}")
            return build_error_response(
                code=ErrorCode.UNEXPECTED_ERROR,
                message=str(e),
                tool=full_name or tool_name,
                data={"traceback": traceback.format_exc()},
                execution_time_ms=_elapsed_ms(),
                resource_type=resource_type,
                session_id=session_info.get("session_id") if session_info else None
            )
    
    async def execute_batch(
        self,
        actions: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute multiple actions in batch.

        Args:
            actions: Action list; each item includes action/params/timeout.
            **kwargs: Runtime options.
                - worker_id (str): Worker ID (required)
                - parallel (bool): Run in parallel if True (default: False)
                - stop_on_error (bool): Stop on first failure in serial mode
                - trace_id (str, optional): Trace ID

        Returns:
            Batch execution result.
        """
        # Extract runtime parameters.
        worker_id = kwargs.get("worker_id")
        if not worker_id:
            raise ValueError("worker_id is required")
        parallel: bool = kwargs.get("parallel", False)
        stop_on_error: bool = kwargs.get("stop_on_error", True)
        trace_id: Optional[str] = kwargs.get("trace_id")
        
        start_time = time.time()
        results = []
        
        if parallel:
            tasks = [
                self.execute(
                    action=item.get("action", ""),
                    params=item.get("params", {}),
                    worker_id=worker_id,
                    timeout=item.get("timeout"),
                    trace_id=trace_id
                )
                for item in actions
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            processed_results = []
            for idx, r in enumerate(results):
                if isinstance(r, Exception):
                    action_name = actions[idx].get("action", "")
                    processed_results.append(
                        build_error_response(
                            code=ErrorCode.UNEXPECTED_ERROR,
                            message=str(r),
                            tool=action_name,
                            data={"action": action_name},
                            execution_time_ms=(time.time() - start_time) * 1000
                        )
                    )
                else:
                    processed_results.append(r)
            results = processed_results
        else:
            for item in actions:
                result = await self.execute(
                    action=item.get("action", ""),
                    params=item.get("params", {}),
                    worker_id=worker_id,
                    timeout=item.get("timeout"),
                    trace_id=trace_id
                )
                results.append(result)
                
                if stop_on_error and result.get("code") != ErrorCode.SUCCESS:
                    break
        
        success_count = sum(1 for r in results if r.get("code") == ErrorCode.SUCCESS)
        total = len(actions)
        executed = len(results)
        data = {
            "results": results,
            "total": total,
            "executed": executed,
            "success_count": success_count
        }

        execution_time_ms = (time.time() - start_time) * 1000

        if success_count == executed and executed == total:
            return build_success_response(
                data=data,
                tool="batch:execute",
                execution_time_ms=execution_time_ms
            )
        if success_count == 0:
            return build_error_response(
                code=ErrorCode.ALL_REQUESTS_FAILED,
                message="All actions failed",
                tool="batch:execute",
                data=data,
                execution_time_ms=execution_time_ms
            )
        return build_error_response(
            code=ErrorCode.PARTIAL_FAILURE,
            message=f"{executed - success_count} out of {executed} actions failed",
            tool="batch:execute",
            data=data,
            execution_time_ms=execution_time_ms
        )

