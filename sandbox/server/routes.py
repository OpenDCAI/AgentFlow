# sandbox/server/routes.py
"""
HTTP Routes Module

Extracts all HTTP route definitions into a separate file for Server to call.
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Import protocol for endpoints and models
from ..protocol import (
    HTTPEndpoints,
    ExecuteRequest, ExecuteBatchRequest,
    InitResourceRequest, InitBatchRequest, InitFromConfigRequest,
    WorkerDisconnectRequest,
)
from .backends.error_codes import ErrorCode
from .backends.response_builder import build_error_response, build_success_response

if TYPE_CHECKING:
    from .app import HTTPServiceServer

logger = logging.getLogger("Routes")


def register_routes(app: FastAPI, server: "HTTPServiceServer"):
    """
    Register all HTTP routes
    
    Args:
        app: FastAPI application instance
        server: HTTPServiceServer instance
    """
    
    # ========== Health Endpoints ==========
    
    @app.get(HTTPEndpoints.HEALTH)
    async def health_check():
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    
    @app.get(HTTPEndpoints.READY)
    async def readiness_check():
        all_sessions = await server.resource_router.list_all_sessions()
        total_sessions = sum(len(s) for s in all_sessions.values())
        return {
            "status": "ready",
            "tools_count": len(server._tools),
            "active_workers": len(all_sessions),
            "total_sessions": total_sessions
        }
    
    # ========== Execute Endpoints ==========
    
    @app.post(HTTPEndpoints.EXECUTE)
    async def execute_action(request: ExecuteRequest):
        """Execute action"""
        try:
            # Build kwargs, including all runtime parameters
            exec_kwargs = {
                "worker_id": request.worker_id,
                "timeout": request.timeout,
            }
            # If request contains trace_id, pass it in
            if hasattr(request, "trace_id") and request.trace_id:
                exec_kwargs["trace_id"] = request.trace_id
            
            result = await server.execute(
                action=request.action,
                params=request.params,
                **exec_kwargs
            )
            code = result.get("code", ErrorCode.UNEXPECTED_ERROR)
            if code == ErrorCode.SUCCESS:
                status_code = 200
            elif 4000 <= int(code) < 5000:
                status_code = 400
            else:
                status_code = 500
                logger.error(
                    "Execute action returned 500: code=%s tool=%s message=%s data=%s",
                    code,
                    result.get("tool"),
                    result.get("message"),
                    result.get("data"),
                )
            return JSONResponse(status_code=status_code, content=result)
        except Exception as e:
            import traceback
            logger.error(f"Execute action failed: {e}\n{traceback.format_exc()}")
            error_response = build_error_response(
                code=ErrorCode.UNEXPECTED_ERROR,
                message=str(e),
                tool=request.action,
                data={"traceback": traceback.format_exc()}
            )
            return JSONResponse(
                status_code=500,
                content=error_response
            )
    
    @app.post(HTTPEndpoints.EXECUTE_BATCH)
    async def execute_batch(request: ExecuteBatchRequest):
        """Execute batch actions"""
        try:
            # Build kwargs, including all runtime parameters
            exec_kwargs = {
                "worker_id": request.worker_id,
                "parallel": request.parallel,
                "stop_on_error": request.stop_on_error,
            }
            # If request contains trace_id, pass it in
            if hasattr(request, "trace_id") and request.trace_id:
                exec_kwargs["trace_id"] = request.trace_id
            
            result = await server.execute_batch(
                actions=request.actions,
                **exec_kwargs
            )

            code = result.get("code", ErrorCode.UNEXPECTED_ERROR)
            if code == ErrorCode.SUCCESS:
                status_code = 200
            elif code == ErrorCode.PARTIAL_FAILURE:
                status_code = 207
            elif 4000 <= int(code) < 5000:
                status_code = 400
            else:
                status_code = 500
                logger.error(
                    "Execute batch returned 500: code=%s tool=%s message=%s data=%s",
                    code,
                    result.get("tool"),
                    result.get("message"),
                    result.get("data"),
                )
            return JSONResponse(status_code=status_code, content=result)
        except Exception as e:
            import traceback
            logger.error(f"Execute batch failed: {e}\n{traceback.format_exc()}")
            error_response = build_error_response(
                code=ErrorCode.UNEXPECTED_ERROR,
                message=str(e),
                tool="batch:execute",
                data={"traceback": traceback.format_exc()}
            )
            return JSONResponse(
                status_code=500,
                content=error_response
            )
    
    # ========== Session/Status Endpoints ==========
    
    @app.post(HTTPEndpoints.HEARTBEAT)
    async def heartbeat(request: Request):
        """Heartbeat check"""
        start_time = asyncio.get_event_loop().time()
        data = await request.json()
        worker_id = data.get("worker_id")

        if not worker_id:
            response = build_error_response(
                code=ErrorCode.INVALID_REQUEST_FORMAT,
                message="worker_id required",
                tool="session:heartbeat",
                data={"worker_id": worker_id},
                execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                resource_type="session"
            )
            return JSONResponse(status_code=400, content=response)

        sessions = await server.resource_router.list_worker_sessions(worker_id)

        response = build_success_response(
            data={
                "worker_id": worker_id,
                "active_sessions": list(sessions.keys()),
                "timestamp": datetime.utcnow().isoformat()
            },
            tool="session:heartbeat",
            execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
            resource_type="session"
        )
        return JSONResponse(content=response)
    
    @app.post(HTTPEndpoints.STATUS)
    async def get_status(request: Request):
        """Get worker status"""
        start_time = asyncio.get_event_loop().time()
        data = await request.json()
        worker_id = data.get("worker_id")

        if not worker_id:
            response = build_error_response(
                code=ErrorCode.INVALID_REQUEST_FORMAT,
                message="worker_id required",
                tool="session:status",
                data={"worker_id": worker_id},
                execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                resource_type="session"
            )
            return JSONResponse(status_code=400, content=response)

        sessions = await server.resource_router.list_worker_sessions(worker_id)

        session_summary = {
            rt: {
                "session_id": info.get("session_id"),
                "status": info.get("status"),
                "created_at": info.get("created_at"),
                "last_activity": info.get("last_activity")
            }
            for rt, info in sessions.items()
        }

        response = build_success_response(
            data={
                "worker_id": worker_id,
                "active_resources": list(sessions.keys()),
                "sessions": session_summary,
                "tools_available": len(server._tools)
            },
            tool="session:status",
            execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
            resource_type="session"
        )
        return JSONResponse(content=response)
    
    @app.post("/api/v1/worker/disconnect")
    async def worker_disconnect(request: WorkerDisconnectRequest):
        """Worker disconnect"""
        start_time = asyncio.get_event_loop().time()
        count = await server.resource_router.destroy_worker_sessions(request.worker_id)
        response = build_success_response(
            data={
                "worker_id": request.worker_id,
                "sessions_cleaned": count
            },
            tool="session:disconnect",
            execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
            resource_type="session"
        )
        return JSONResponse(content=response)
    
    # ========== Session Management Endpoints ==========
    
    @app.post(HTTPEndpoints.SESSION_CREATE)
    async def create_session(request: Request):
        """Explicitly create Session"""
        start_time = asyncio.get_event_loop().time()
        data = await request.json()
        worker_id = data.get("worker_id")
        resource_type = data.get("resource_type")
        session_config = data.get("session_config", {})
        custom_name = data.get("custom_name")

        if not worker_id or not resource_type:
            response = build_error_response(
                code=ErrorCode.INVALID_REQUEST_FORMAT,
                message="worker_id and resource_type required",
                tool="session:create",
                data={"worker_id": worker_id, "resource_type": resource_type},
                execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                resource_type="session"
            )
            return JSONResponse(status_code=400, content=response)

        existing = await server.resource_router.get_session(worker_id, resource_type)
        if existing:
            response = build_success_response(
                data={
                    "status": "exists",
                    "session_id": existing.get("session_id"),
                    "session_name": existing.get("session_name"),
                    "resource_type": resource_type
                },
                tool="session:create",
                execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                resource_type="session",
                session_id=existing.get("session_id")
            )
            return JSONResponse(content=response)

        session_info = await server.resource_router.get_or_create_session(
            worker_id=worker_id,
            resource_type=resource_type,
            config=session_config,
            auto_created=False,
            custom_name=custom_name
        )

        data_payload = {
            "session_id": session_info.get("session_id"),
            "session_name": session_info.get("session_name"),
            "resource_type": resource_type,
            "session_status": session_info.get("status"),
            "error": session_info.get("error")
        }

        # Add compatibility mode information
        if session_info.get("compatibility_mode"):
            data_payload["compatibility_mode"] = True
            data_payload["compatibility_message"] = session_info.get("compatibility_message")

        if session_info.get("status") == "active":
            response = build_success_response(
                data=data_payload,
                tool="session:create",
                execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                resource_type="session",
                session_id=session_info.get("session_id")
            )
            return JSONResponse(content=response)

        response = build_error_response(
            code=ErrorCode.RESOURCE_NOT_INITIALIZED,
            message="Session creation failed",
            tool="session:create",
            data=data_payload,
            execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
            resource_type="session",
            session_id=session_info.get("session_id")
        )
        return JSONResponse(status_code=500, content=response)
    
    @app.post(HTTPEndpoints.SESSION_DESTROY)
    async def destroy_session(request: Request):
        """Explicitly destroy Session"""
        start_time = asyncio.get_event_loop().time()
        data = await request.json()
        worker_id = data.get("worker_id")
        resource_type = data.get("resource_type")

        if not worker_id or not resource_type:
            response = build_error_response(
                code=ErrorCode.INVALID_REQUEST_FORMAT,
                message="worker_id and resource_type required",
                tool="session:destroy",
                data={"worker_id": worker_id, "resource_type": resource_type},
                execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                resource_type="session"
            )
            return JSONResponse(status_code=400, content=response)

        destroyed_session = await server.resource_router.destroy_session(worker_id, resource_type)

        if destroyed_session:
            response = build_success_response(
                data={
                    "message": f"Session destroyed for {resource_type}",
                    "session_id": destroyed_session.get("session_id"),
                    "session_name": destroyed_session.get("session_name"),
                    "resource_type": resource_type
                },
                tool="session:destroy",
                execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                resource_type="session",
                session_id=destroyed_session.get("session_id")
            )
            return JSONResponse(content=response)

        response = build_error_response(
            code=ErrorCode.RESOURCE_NOT_INITIALIZED,
            message=f"No session found for {resource_type}",
            tool="session:destroy",
            data={"resource_type": resource_type},
            execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
            resource_type="session"
        )
        return JSONResponse(status_code=404, content=response)
    
    @app.post(HTTPEndpoints.SESSION_LIST)
    async def list_sessions(request: Request):
        """List all sessions for worker"""
        start_time = asyncio.get_event_loop().time()
        data = await request.json()
        worker_id = data.get("worker_id")

        if not worker_id:
            response = build_error_response(
                code=ErrorCode.INVALID_REQUEST_FORMAT,
                message="worker_id required",
                tool="session:list",
                data={"worker_id": worker_id},
                execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                resource_type="session"
            )
            return JSONResponse(status_code=400, content=response)

        sessions = await server.resource_router.list_worker_sessions(worker_id)

        session_list = [
            {
                "resource_type": rt,
                "session_id": info.get("session_id"),
                "session_name": info.get("session_name"),
                "status": info.get("status"),
                "auto_created": info.get("auto_created", False),
                "created_at": info.get("created_at"),
                "last_activity": info.get("last_activity"),
                "expires_at": info.get("expires_at")
            }
            for rt, info in sessions.items()
        ]

        response = build_success_response(
            data={
                "worker_id": worker_id,
                "sessions": session_list,
                "count": len(session_list)
            },
            tool="session:list",
            execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
            resource_type="session"
        )
        return JSONResponse(content=response)
    
    @app.post(HTTPEndpoints.SESSION_REFRESH)
    async def refresh_session(request: Request):
        """Refresh Session TTL (keep-alive)"""
        start_time = asyncio.get_event_loop().time()
        data = await request.json()
        worker_id = data.get("worker_id")
        resource_type = data.get("resource_type")

        if not worker_id:
            response = build_error_response(
                code=ErrorCode.INVALID_REQUEST_FORMAT,
                message="worker_id required",
                tool="session:refresh",
                data={"worker_id": worker_id},
                execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                resource_type="session"
            )
            return JSONResponse(status_code=400, content=response)

        # If resource_type is specified, only refresh that resource
        if resource_type:
            refreshed = await server.resource_router.refresh_session(worker_id, resource_type)
            if refreshed:
                session = await server.resource_router.get_session(worker_id, resource_type)
                response = build_success_response(
                    data={
                        "message": f"Session refreshed for {resource_type}",
                        "resource_type": resource_type,
                        "session_id": session.get("session_id") if session else None,
                        "expires_at": session.get("expires_at") if session else None
                    },
                    tool="session:refresh",
                    execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                    resource_type="session",
                    session_id=session.get("session_id") if session else None
                )
                return JSONResponse(content=response)
            response = build_error_response(
                code=ErrorCode.RESOURCE_NOT_INITIALIZED,
                message=f"No session found for {resource_type}",
                tool="session:refresh",
                data={"resource_type": resource_type},
                execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                resource_type="session"
            )
            return JSONResponse(status_code=404, content=response)

        # Refresh all sessions for this worker
        sessions = await server.resource_router.list_worker_sessions(worker_id)
        refreshed_count = 0
        results = {}

        for rt in sessions.keys():
            success = await server.resource_router.refresh_session(worker_id, rt)
            if success:
                refreshed_count += 1
                session = await server.resource_router.get_session(worker_id, rt)
                results[rt] = {
                    "status": "refreshed",
                    "expires_at": session.get("expires_at") if session else None
                }

        response = build_success_response(
            data={
                "message": f"Refreshed {refreshed_count} sessions",
                "worker_id": worker_id,
                "refreshed_count": refreshed_count,
                "details": results
            },
            tool="session:refresh",
            execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
            resource_type="session"
        )
        return JSONResponse(content=response)
    
    # ========== Init Endpoints ==========
    
    @app.post(HTTPEndpoints.INIT_RESOURCE)
    async def init_resource(request: InitResourceRequest):
        """Initialize resource"""
        start_time = asyncio.get_event_loop().time()
        try:
            session_info = await server.resource_router.get_or_create_session(
                worker_id=request.worker_id,
                resource_type=request.resource_type,
                config=request.init_config
            )
            data_payload = {
                "session_id": session_info.get("session_id"),
                "resource_type": request.resource_type,
                "session_status": session_info.get("status"),
                "error": session_info.get("error")
            }
            if session_info.get("status") == "active":
                response = build_success_response(
                    data=data_payload,
                    tool="init:resource",
                    execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                    resource_type="session",
                    session_id=session_info.get("session_id")
                )
                return JSONResponse(content=response)
            response = build_error_response(
                code=ErrorCode.RESOURCE_NOT_INITIALIZED,
                message="Resource initialization failed",
                tool="init:resource",
                data=data_payload,
                execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                resource_type="session",
                session_id=session_info.get("session_id")
            )
            return JSONResponse(status_code=500, content=response)
        except Exception as e:
            logger.error(f"Init resource failed: {e}")
            response = build_error_response(
                code=ErrorCode.UNEXPECTED_ERROR,
                message=str(e),
                tool="init:resource",
                data={"resource_type": request.resource_type},
                execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                resource_type="session"
            )
            return JSONResponse(status_code=500, content=response)
    
    @app.post(HTTPEndpoints.INIT_BATCH)
    async def init_batch(request: InitBatchRequest):
        """Batch initialize resources"""
        start_time = asyncio.get_event_loop().time()
        results = {}
        for resource_type, config in request.resource_configs.items():
            try:
                session_info = await server.resource_router.get_or_create_session(
                    worker_id=request.worker_id,
                    resource_type=resource_type,
                    config=config.get("content", config)
                )
                results[resource_type] = {
                    "status": "success" if session_info.get("status") == "active" else "error",
                    "session_id": session_info.get("session_id"),
                    "session_status": session_info.get("status"),
                    "error": session_info.get("error")
                }
            except Exception as e:
                results[resource_type] = {"status": "error", "message": str(e)}

        success_count = sum(1 for r in results.values() if r.get("status") == "success")
        total = len(results)
        data_payload = {
            "worker_id": request.worker_id,
            "results": results,
            "total": total,
            "success_count": success_count
        }

        if success_count == total:
            response = build_success_response(
                data=data_payload,
                tool="init:batch",
                execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                resource_type="session"
            )
            return JSONResponse(content=response)
        if success_count == 0:
            response = build_error_response(
                code=ErrorCode.ALL_REQUESTS_FAILED,
                message="All resources failed to initialize",
                tool="init:batch",
                data=data_payload,
                execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                resource_type="session"
            )
            return JSONResponse(status_code=500, content=response)
        response = build_error_response(
            code=ErrorCode.PARTIAL_FAILURE,
            message=f"{total - success_count} out of {total} resources failed",
            tool="init:batch",
            data=data_payload,
            execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
            resource_type="session"
        )
        return JSONResponse(status_code=207, content=response)
    
    @app.post(HTTPEndpoints.INIT_FROM_CONFIG)
    async def init_from_config(request: InitFromConfigRequest):
        """Initialize from config file"""
        start_time = asyncio.get_event_loop().time()
        try:
            if not os.path.exists(request.config_path):
                response = build_error_response(
                    code=ErrorCode.INVALID_REQUEST_FORMAT,
                    message=f"Config file not found: {request.config_path}",
                    tool="init:from_config",
                    data={"config_path": request.config_path},
                    execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                    resource_type="session"
                )
                return JSONResponse(status_code=404, content=response)

            with open(request.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            if request.override_params:
                for key, value in request.override_params.items():
                    if key in config:
                        if isinstance(config[key], dict) and isinstance(value, dict):
                            config[key].update(value)
                        else:
                            config[key] = value

            response = build_success_response(
                data={
                    "config_loaded": request.config_path,
                    "config": config
                },
                tool="init:from_config",
                execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                resource_type="session"
            )
            return JSONResponse(content=response)
        except Exception as e:
            logger.error(f"Init from config failed: {e}")
            response = build_error_response(
                code=ErrorCode.UNEXPECTED_ERROR,
                message=str(e),
                tool="init:from_config",
                data={"config_path": request.config_path},
                execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                resource_type="session"
            )
            return JSONResponse(status_code=500, content=response)
    
    # ========== Tools Endpoints ==========
    
    @app.get(HTTPEndpoints.TOOLS_LIST)
    async def list_tools(include_hidden: bool = False):
        """List all tools"""
        tools = server.list_tools(include_hidden=include_hidden)
        return JSONResponse(content={"tools": tools, "count": len(tools)})
    
    @app.get("/api/v1/tools/{tool_name}/schema")
    async def get_tool_schema(tool_name: str):
        """Get tool schema"""
        schema = server.get_tool_info(tool_name)
        if not schema:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": f"Tool not found: {tool_name}"}
            )
        return JSONResponse(content=schema)
    
    # ========== Warmup Endpoints ==========
    
    @app.post(HTTPEndpoints.WARMUP)
    async def warmup_backends(request: Request):
        """Warmup backend resources"""
        data = await request.json() if request.headers.get("content-length", "0") != "0" else {}
        backend_names = data.get("backends")  # None means warmup all backends
        
        # Use warmup method with error information
        detailed_results = await server.warmup_backends_with_errors(backend_names)
        
        # Extract simple success status (for backward compatibility)
        results = {name: info["success"] for name, info in detailed_results.items()}
        
        # Collect error information
        errors = {name: info["error"] for name, info in detailed_results.items() if info["error"]}
        
        all_success = all(results.values()) if results else True
        
        response = {
            "status": "success" if all_success else "partial_error",
            "results": results,
            "summary": server.get_warmup_status()["summary"]
        }
        
        # If there are errors, add detailed error information
        if errors:
            response["errors"] = errors
        
        return JSONResponse(content=response)
    
    @app.get(HTTPEndpoints.WARMUP_STATUS)
    async def warmup_status():
        """Get warmup status"""
        return JSONResponse(content=server.get_warmup_status())
    
    # ========== Server Control Endpoints ==========
    
    @app.post(HTTPEndpoints.SHUTDOWN)
    async def shutdown_server(request: Request):
        """Shutdown server"""
        data = await request.json() if request.headers.get("content-length", "0") != "0" else {}
        force = data.get("force", False)
        cleanup_sessions = data.get("cleanup_sessions", True)
        
        logger.info(f"Shutdown requested (force={force}, cleanup_sessions={cleanup_sessions})")
        
        # Cleanup all sessions
        cleaned_count = 0
        if cleanup_sessions:
            all_sessions = await server.resource_router.list_all_sessions()
            for worker_id in list(all_sessions.keys()):
                count = await server.resource_router.destroy_worker_sessions(worker_id)
                cleaned_count += count
            logger.info(f"Cleaned {cleaned_count} sessions before shutdown")
        
        # Schedule delayed shutdown (let response be sent to client first)
        async def delayed_shutdown():
            await asyncio.sleep(0.5)
            
            # Shutdown all backends, release GPU and other resources
            shutdown_errors = []
            for backend_name in server.list_backends():
                backend = server.get_backend(backend_name)
                if backend:
                    try:
                        logger.info(f"Shutting down backend: {backend_name}")
                        await backend.shutdown()
                        logger.info(f"Backend {backend_name} shutdown complete")
                    except Exception as e:
                        error_msg = f"Failed to shutdown {backend_name}: {e}"
                        logger.error(error_msg)
                        shutdown_errors.append(error_msg)
            
            if shutdown_errors:
                logger.warning(f"Shutdown completed with {len(shutdown_errors)} errors")
            else:
                logger.info("All backends shutdown successfully")
            
            logger.info("Server shutting down...")
            os._exit(0)
        
        asyncio.create_task(delayed_shutdown())
        
        return JSONResponse(content={
            "status": "success",
            "message": "Server shutdown initiated",
            "sessions_cleaned": cleaned_count
        })
