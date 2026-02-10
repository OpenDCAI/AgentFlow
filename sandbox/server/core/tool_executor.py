# sandbox/server/core/tool_executor.py
"""
工具执行器

负责工具的执行逻辑，使用 Server 传入的数据结构引用。
数据结构（_tools, _tool_name_index, _tool_resource_types）保存在 Server 类中。

工具函数映射机制说明:
======================

1. 工具注册 (Tool Registration)
   - 工具通过 register_tool(name, func) 或 @tool 装饰器标记后扫描注册
   - 工具名称支持 "resource_type:action" 格式（如 "vm:screenshot"）
   - 前缀是可选的：无状态工具不需要前缀
   
2. 工具映射存储 (三层结构，保存在 Server 中)
   - _tools: Dict[str, Callable]  
     完整名称映射，存储 full_name -> function
     
   - _tool_name_index: Dict[str, List[str]]
     简单名称索引，存储 simple_name -> [full_names]
     
   - _tool_resource_types: Dict[str, str]
     资源类型映射，存储 full_name -> resource_type
   
3. 工具查找策略 (resolve_tool)
   a. 优先精确匹配：直接查找完整名称
   b. 简单名称匹配：通过索引查找
   c. 无匹配：返回错误
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
    工具执行器
    
    核心职责:
    - 执行工具函数
    - 根据资源类型前缀自动路由到对应 session
    - 处理参数注入
    
    数据结构由外部（Server）传入，本类只持有引用。
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
        初始化工具执行器
        
        Args:
            tools: 完整名称 -> 函数映射（引用）
            tool_name_index: 简单名称 -> 完整名称列表索引（引用）
            tool_resource_types: 完整名称 -> 资源类型映射（引用）
            resource_router: 资源路由器实例
            warmup_callback: 预热回调函数，用于在执行工具前自动预热后端
        """
        # 持有外部数据结构的引用
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
        """
        if ":" in action:
            return action

        # Build a set of known resource prefixes from registered tool names.
        resource_prefixes = set()
        for full_name in self._tools.keys():
            if ":" in full_name:
                resource_prefixes.add(full_name.split(":", 1)[0])

        for sep in (".", "_"):
            if sep in action:
                prefix, suffix = action.split(sep, 1)
                candidate = f"{prefix}:{suffix}"
                if prefix in resource_prefixes and candidate in self._tools:
                    return candidate

        return action
    
    def _resolve_tool(self, action: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        解析工具名称，返回完整名称、简单名称和资源类型
        
        查找策略:
        1. 精确匹配：action 直接作为完整名称查找
        2. 索引匹配：action 作为简单名称在索引中查找
           - 唯一匹配：直接返回（前缀可选）
           - 多个匹配：返回 None，拒绝执行（必须指定前缀）
        
        Args:
            action: 动作名称（可以是 "vm:screenshot" 或 "screenshot"）
            
        Returns:
            (full_name, simple_name, resource_type) 或 (None, None, None) 如果未找到
        """
        # 策略1: 精确匹配完整名称
        if action in self._tools:
            resource_type = self._tool_resource_types.get(action)
            simple_name = action.split(":")[-1] if ":" in action else action
            return action, simple_name, resource_type
        
        # 策略2: 带前缀但未直接匹配，说明工具不存在
        if ":" in action:
            return None, None, None
        
        # 策略3: 作为简单名称在索引中查找
        simple_name = action
        if simple_name in self._tool_name_index:
            candidates = self._tool_name_index[simple_name]
            
            if len(candidates) == 1:
                full_name = candidates[0]
                resource_type = self._tool_resource_types.get(full_name)
                return full_name, simple_name, resource_type
            
            elif len(candidates) > 1:
                # 多个匹配 - 存在歧义
                return None, simple_name, None
        
        return None, None, None

    async def execute(
        self, 
        action: str, 
        params: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行工具
        
        Args:
            action: 动作名称，支持带或不带资源类型前缀
            params: 参数
            **kwargs: 运行时参数
                - worker_id (str): Worker ID（必需）
                - timeout (int, optional): 超时时间
                - trace_id (str, optional): 追踪 ID，用于日志关联
                - session_id (str, optional): 指定使用的 session ID
            
        Returns:
            执行结果字典
        """
        # 提取运行时参数
        worker_id = kwargs.get("worker_id")
        if not worker_id:
            raise ValueError("worker_id is required")
        timeout: Optional[int] = kwargs.get("timeout")
        trace_id: Optional[str] = kwargs.get("trace_id")
        
        start_time = time.time()
        tool_name = action  # 默认值，用于错误报告
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

            # 解析工具名称
            full_name, simple_name, resource_type = self._resolve_tool(action)
            logger.info(f"   ↳ Resolved: full_name={full_name}, resource_type={resource_type}")
            
            # 检查是否找到工具
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
            
            # 自动预热后端（如果有资源类型且提供了预热回调）
            if resource_type and self._warmup_callback:
                logger.info(f"   ↳ Warmup backend: {resource_type}")
                warmup_result = self._warmup_callback(resource_type)
                # 如果返回的是协程，等待它
                if asyncio.iscoroutine(warmup_result):
                    await warmup_result
                logger.info(f"   ↳ Warmup completed: {resource_type}")

            # 获取或创建session（如果有资源类型）
            session_info = None

            if resource_type:
                logger.info(f"   ↳ Getting session for resource_type={resource_type}")
                existing_session = await self._resource_router.get_session(worker_id, resource_type)

                if existing_session:
                    logger.info(f"   ↳ Using existing session: {existing_session.get('session_id')}")
                    session_info = existing_session
                else:
                    # 自动创建临时 session
                    logger.info(f"   ↳ Creating temporary session for {resource_type}")
                    session_info = await self._resource_router.get_or_create_session(
                        worker_id=worker_id,
                        resource_type=resource_type,
                        auto_created=True
                    )
                    is_temporary_session = True  # 标记为临时 session
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
            
            # 自动注入参数
            sig = inspect.signature(func)
            has_var_keyword = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())

            def inject_if_missing(key, value):
                """如果参数不存在且函数签名允许（显式定义或有**kwargs），则注入"""
                if key not in params and value is not None:
                    if key in sig.parameters or has_var_keyword:
                        params[key] = value

            inject_if_missing("worker_id", worker_id)
            inject_if_missing("trace_id", trace_id)
            
            if session_info:
                inject_if_missing("session_id", session_info.get("session_id"))
                inject_if_missing("session_info", session_info)
            
            # 执行工具函数
            logger.info(f"   ↳ Executing tool function: {full_name}")
            result = func(**params)

            # 检查结果是否是协程（处理被装饰器包装的异步函数）
            if asyncio.iscoroutine(result):
                logger.info(f"   ↳ Awaiting async result...")
                if timeout:
                    result = await asyncio.wait_for(result, timeout=timeout)
                else:
                    result = await result
                logger.info(f"   ↳ Async result received")

            execution_time = (time.time() - start_time) * 1000
            logger.info(f"✅ [ToolExecutor] Execute COMPLETED: {action} in {execution_time:.2f}ms")

            # 如果是临时 session，执行完成后销毁
            if is_temporary_session and resource_type:
                await self._resource_router.destroy_session(worker_id, resource_type)
                logger.info(f"🗑️ Destroyed temporary session for {resource_type} (worker: {worker_id})")
            elif resource_type and session_info:
                # 非临时 session 只刷新存活时间
                logger.info(
                    "🔄 [ToolExecutor] Refresh session after action: %s (worker=%s, session_id=%s)",
                    full_name or tool_name,
                    worker_id,
                    session_info.get("session_id"),
                )
                await self._resource_router.refresh_session(worker_id, resource_type)

            # 检查工具返回的是否是新格式（包含 code 字段）
            if isinstance(result, dict) and "code" in result:
                # 新格式：直接返回，并补全必要元数据
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
            # 超时也要清理临时 session
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
            # 出错也要清理临时 session
            if is_temporary_session and resource_type:
                try:
                    await self._resource_router.destroy_session(worker_id, resource_type)
                except Exception:
                    pass  # 清理失败不影响错误返回
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
        批量执行工具
        
        Args:
            actions: 动作列表，每个元素包含 action, params, timeout
            **kwargs: 运行时参数
                - worker_id (str): Worker ID（必需）
                - parallel (bool): 是否并行执行，默认 False
                - stop_on_error (bool): 遇到错误是否停止，默认 True
                - trace_id (str, optional): 追踪 ID
            
        Returns:
            批量执行结果
        """
        # 提取运行时参数
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

