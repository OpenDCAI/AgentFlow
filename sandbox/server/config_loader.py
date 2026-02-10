# sandbox/server/config_loader.py
"""
配置加载器

支持从 JSON 配置文件加载服务器配置和后端定义。
支持环境变量替换（${VAR} 或 ${VAR:-default}）。

使用示例:
```python
from sandbox.server.config_loader import ConfigLoader, load_config

# 方式1: 直接加载配置
config = load_config("config.json")

# 方式2: 使用加载器
loader = ConfigLoader()
loader.load("config.json")
server = loader.create_server()
server.run()

# 方式3: 从配置启动服务器
from sandbox.server.config_loader import create_server_from_config
server = create_server_from_config("config.json")
server.run()
```
"""

import os
import re
import json
import logging
import importlib
from pathlib import Path
from typing import Dict, Any, Optional, Type, List
from dataclasses import dataclass, field

logger = logging.getLogger("ConfigLoader")


# ============================================================================
# Environment Variable Processing
# ============================================================================

def expand_env_vars(value: Any) -> Any:
    """
    递归展开环境变量
    
    支持格式:
    - ${VAR} - 必须存在的环境变量
    - ${VAR:-default} - 带默认值的环境变量
    
    Args:
        value: 任意值（字符串会被处理）
        
    Returns:
        处理后的值
    """
    if isinstance(value, str):
        # 匹配 ${VAR} 或 ${VAR:-default}
        pattern = r'\$\{([^}:]+)(?::-([^}]*))?\}'
        
        def replace(match):
            var_name = match.group(1)
            default_value = match.group(2)
            env_value = os.environ.get(var_name)
            
            if env_value is not None:
                return env_value
            elif default_value is not None:
                return default_value
            else:
                # 保留原始占位符，让调用者决定如何处理
                logger.warning(f"Environment variable '{var_name}' not set and no default provided")
                return match.group(0)
        
        return re.sub(pattern, replace, value)
    
    elif isinstance(value, dict):
        return {k: expand_env_vars(v) for k, v in value.items()}
    
    elif isinstance(value, list):
        return [expand_env_vars(item) for item in value]
    
    return value


# ============================================================================
# Configuration Data Classes
# ============================================================================

@dataclass
class ServerConfig:
    """
    服务器配置
    
    注意: host 和 port 由 Sandbox(server_url=...) 指定，不在配置文件中设置
    """
    title: str = "Sandbox HTTP Service"
    description: str = ""
    session_ttl: int = 300
    cleanup_interval: int = 60
    log_level: str = "INFO"


@dataclass
class ResourceConfig:
    """资源配置"""
    name: str
    enabled: bool = True
    description: str = ""
    backend_class: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WarmupConfig:
    """预热配置"""
    enabled: bool = False
    resources: List[str] = field(default_factory=list)


@dataclass
class SecurityConfig:
    """安全配置"""
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit_enabled: bool = False
    requests_per_minute: int = 100
    auth_enabled: bool = False
    auth_type: str = "api_key"
    api_key: Optional[str] = None


@dataclass
class SandboxConfig:
    """完整的 Sandbox 配置"""
    server: ServerConfig = field(default_factory=ServerConfig)
    resources: Dict[str, ResourceConfig] = field(default_factory=dict)
    tools: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    warmup: WarmupConfig = field(default_factory=WarmupConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)


# ============================================================================
# Config Loader
# ============================================================================

class ConfigLoader:
    """
    配置加载器
    
    功能:
    - 从 JSON 文件加载配置
    - 环境变量替换
    - 动态加载后端类
    - 创建配置好的服务器实例
    
    加载流程:
    1. 加载并解析配置文件
    2. 展开环境变量
    3. 创建 HTTPServiceServer 实例
    4. 遍历 resources，动态加载并调用 server.load_backend()
    5. 遍历 apis，通过 @register_api_tool 装饰器自动注册无状态工具
    """
    
    def __init__(self):
        self.config: Optional[SandboxConfig] = None
        self.raw_config: Dict[str, Any] = {}
    
    def load(self, config_path: str) -> SandboxConfig:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            解析后的配置对象
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            self.raw_config = json.load(f)
        
        # 展开环境变量
        expanded = expand_env_vars(self.raw_config)
        
        # 解析各部分配置
        self.config = self._parse_config(expanded)
        
        logger.info(f"✅ Loaded config from {config_path}")
        logger.info(f"   - Server: {self.config.server.title}")
        logger.info(f"   - Resources: {list(self.config.resources.keys())}")
        
        return self.config
    
    def load_from_dict(self, config_dict: Dict[str, Any]) -> SandboxConfig:
        """从字典加载配置"""
        self.raw_config = config_dict
        expanded = expand_env_vars(config_dict)
        self.config = self._parse_config(expanded)
        return self.config
    
    def _parse_config(self, data: Dict[str, Any]) -> SandboxConfig:
        """解析配置字典为配置对象"""
        
        # 服务器配置 (host/port 由 Sandbox(server_url=...) 指定)
        server_data = data.get("server", {})
        server = ServerConfig(
            title=server_data.get("title", "Sandbox HTTP Service"),
            description=server_data.get("description", ""),
            session_ttl=server_data.get("session_ttl", 300),
            cleanup_interval=server_data.get("cleanup_interval", 60),
            log_level=server_data.get("log_level", "INFO")
        )
        
        # 资源配置
        resources: Dict[str, ResourceConfig] = {}
        for name, res_data in data.get("resources", {}).items():
            # 跳过注释字段
            if name.startswith("_"):
                continue
            
            resources[name] = ResourceConfig(
                name=name,
                enabled=res_data.get("enabled", True),
                description=res_data.get("description", ""),
                backend_class=res_data.get("backend_class"),
                config=res_data.get("config", {})
            )
        
        # 工具配置
        tools: Dict[str, Dict[str, Any]] = {}
        for name, tool_data in data.get("tools", {}).items():
            if name.startswith("_"):
                continue
            tools[name] = tool_data
        
        # 预热配置
        warmup_data = data.get("warmup", {})
        warmup = WarmupConfig(
            enabled=warmup_data.get("enabled", False),
            resources=warmup_data.get("resources", [])
        )
        
        # 安全配置
        security_data = data.get("security", {})
        rate_limit = security_data.get("rate_limit", {})
        auth = security_data.get("auth", {})
        security = SecurityConfig(
            allowed_origins=security_data.get("allowed_origins", ["*"]),
            rate_limit_enabled=rate_limit.get("enabled", False),
            requests_per_minute=rate_limit.get("requests_per_minute", 100),
            auth_enabled=auth.get("enabled", False),
            auth_type=auth.get("type", "api_key"),
            api_key=auth.get("api_key")
        )
        
        return SandboxConfig(
            server=server,
            resources=resources,
            tools=tools,
            warmup=warmup,
            security=security
        )
    
    def get_enabled_resources(self) -> Dict[str, ResourceConfig]:
        """获取所有启用的资源"""
        if not self.config:
            return {}
        return {
            name: res for name, res in self.config.resources.items()
            if res.enabled
        }
    
    def load_class(self, class_path: str) -> Type:
        """
        动态加载类
        
        Args:
            class_path: 类的完整路径，如 "sandbox.server.backends.resources.vm.VMBackend"
            
        Returns:
            类对象
        """
        try:
            module_path, class_name = class_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load class '{class_path}': {e}")
            raise

    def create_server(self, host: str = "0.0.0.0", port: int = 8080):
        """
        根据配置创建服务器实例

        加载流程:
        1. 创建 HTTPServiceServer 实例
        2. 遍历 resources，动态加载后端类并调用 server.load_backend()
        3. 遍历 apis，通过 @register_api_tool 装饰器自动注册无状态工具

        Args:
            host: 服务器绑定地址
            port: 服务器端口
        
        Returns:
            配置好的 HTTPServiceServer 实例
        """
        if not self.config:
            raise RuntimeError("No config loaded. Call load() first.")
        
        # 延迟导入避免循环依赖
        from .app import HTTPServiceServer
        from .backends.base import BackendConfig
        
        # 获取预热资源列表
        warmup_resources = self.get_warmup_resources()

        # 创建服务器 (host/port 由参数指定)
        server = HTTPServiceServer(
            host=host,
            port=port,
            title=self.config.server.title,
            session_ttl=self.config.server.session_ttl,
            warmup_resources=warmup_resources
        )
        
        # ====================================================================
        # 加载有状态后端（resources）
        # ====================================================================
        for name, res_config in self.get_enabled_resources().items():
            if res_config.backend_class:
                try:
                    # 动态加载后端类
                    backend_cls = self.load_class(res_config.backend_class)
                    
                    # 创建后端配置
                    backend_config = BackendConfig(
                        enabled=True,
                        default_config=res_config.config,
                        description=res_config.description
                    )
                    
                    # 实例化后端
                    backend = backend_cls(config=backend_config)
                    
                    # 使用新的 API 加载后端（自动反射扫描 @tool 标记）
                    registered = server.load_backend(backend)
                    
                    logger.info(f"✅ Loaded backend: {name} ({len(registered)} tools)")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to load backend '{name}': {e}")
            else:
                logger.warning(f"⚠️ Resource '{name}' has no backend_class, skipping")
        
        # ====================================================================
        # 加载无状态工具（apis）
        # ====================================================================
        apis_config = self.raw_config.get("apis", {})
        if apis_config:
            self._load_api_tools(server, apis_config)
        
        return server
    
    def _load_api_tools(self, server, apis_config: Dict[str, Any]):
        """
        加载无状态 API 工具
        
        新机制：
        - 工具通过 @register_api_tool 装饰器自注册
        - 每个工具指定自己读取的 config_key
        - 配置根据 config_key 从 apis 中提取并注入
        
        Args:
            server: HTTPServiceServer 实例
            apis_config: apis 配置字典
        """
        from .backends.tools import get_all_api_tools
        
        # 获取所有已注册的 API 工具
        api_tools = get_all_api_tools()
        
        if not api_tools:
            logger.info("📦 No API tools registered")
            return
        
        registered_count = 0
        
        for tool_name, tool_info in api_tools.items():
            try:
                # 获取该工具需要的配置
                tool_config = {}
                if tool_info.config_key:
                    tool_config = apis_config.get(tool_info.config_key, {})
                    # 跳过注释字段
                    if isinstance(tool_config, dict):
                        tool_config = {k: v for k, v in tool_config.items() if not k.startswith("_")}
                
                # 如果是 BaseApiTool 实例，先注入配置
                if hasattr(tool_info.func, 'set_config'):
                    tool_info.func.set_config(tool_config)
                    logger.debug(f"  📦 Injected config into {tool_name} instance")
                
                # 注册工具到 server
                server.register_api_tool(
                    name=tool_info.name,
                    func=tool_info.func,
                    config=tool_config,
                    description=tool_info.description,
                    hidden=tool_info.hidden
                )
                
                registered_count += 1
                config_info = f"(config_key={tool_info.config_key})" if tool_info.config_key else "(no config)"
                logger.debug(f"  ✅ Registered: {tool_name} {config_info}")
                
            except Exception as e:
                logger.error(f"❌ Failed to register API tool '{tool_name}': {e}")
        
        logger.info(f"✅ Loaded {registered_count} API tools")
    
    def get_warmup_resources(self) -> List[str]:
        """获取需要预热的资源列表"""
        if not self.config or not self.config.warmup.enabled:
            return []
        
        # 只返回启用的资源
        enabled = set(self.get_enabled_resources().keys())
        return [r for r in self.config.warmup.resources if r in enabled]


# ============================================================================
# Convenience Functions
# ============================================================================

def load_config(config_path: str) -> SandboxConfig:
    """
    加载配置文件的便捷函数
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        解析后的配置对象
    """
    loader = ConfigLoader()
    return loader.load(config_path)


def create_server_from_config(config_path: str, host: str = "0.0.0.0", port: int = 8080):
    """
    从配置文件创建服务器
    
    Args:
        config_path: 配置文件路径
        host: 服务器绑定地址
        port: 服务器端口
        
    Returns:
        配置好的 HTTPServiceServer 实例
        
    Example:
        ```python
        server = create_server_from_config("config.json", host="0.0.0.0", port=8080)
        server.run()
        ```
    """
    loader = ConfigLoader()
    loader.load(config_path)
    return loader.create_server(host=host, port=port)


def get_default_config() -> Dict[str, Any]:
    """
    获取默认配置模板
    
    注意: host/port 由 Sandbox(server_url=...) 或 CLI --host/--port 指定
    
    Returns:
        默认配置字典
    """
    return {
        "server": {
            "title": "Sandbox HTTP Service",
            "session_ttl": 300
        },
        "resources": {},
        "apis": {},
        "warmup": {"enabled": False, "resources": []},
        "security": {"allowed_origins": ["*"]}
    }


# ============================================================================
# CLI Support
# ============================================================================

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Start Sandbox HTTP Service from config")
    parser.add_argument("config", help="Path to config JSON file")
    parser.add_argument("--host", default="0.0.0.0", help="Server bind address (default: 0.0.0.0)")
    parser.add_argument("--port", "-p", type=int, default=8080, help="Server port (default: 8080)")
    parser.add_argument("--validate", action="store_true", help="Only validate config, don't start")
    parser.add_argument("--show", action="store_true", help="Show parsed config")
    
    args = parser.parse_args()
    
    loader = ConfigLoader()
    config = loader.load(args.config)
    
    if args.show:
        print("\n📋 Parsed Configuration:")
        print(f"   Server: {config.server.title}")
        print(f"\n   Resources ({len(config.resources)}):")
        for name, res in config.resources.items():
            status = "✅" if res.enabled else "❌"
            print(f"     {status} {name}: {res.description}")
        print(f"\n   APIs: {list(loader.raw_config.get('apis', {}).keys())}")
        print(f"\n   Warmup: {config.warmup}")
        return
    
    if args.validate:
        print("✅ Configuration is valid")
        return
    
    # 创建并启动服务器
    server = loader.create_server(host=args.host, port=args.port)
    print(f"🚀 Starting server on {args.host}:{args.port}")
    server.run()


if __name__ == "__main__":
    main()

