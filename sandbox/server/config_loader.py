# sandbox/server/config_loader.py
"""
Configuration Loader

Supports loading server configuration and backend definitions from JSON config files.
Supports environment variable substitution (${VAR} or ${VAR:-default}).

Usage examples:
```python
from sandbox.server.config_loader import ConfigLoader, load_config

# Method 1: Load config directly
config = load_config("config.json")

# Method 2: Use loader
loader = ConfigLoader()
loader.load("config.json")
server = loader.create_server()
server.run()

# Method 3: Start server from config
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
    Recursively expand environment variables
    
    Supported formats:
    - ${VAR} - Environment variable that must exist
    - ${VAR:-default} - Environment variable with default value
    
    Args:
        value: Any value (strings will be processed)
        
    Returns:
        Processed value
    """
    if isinstance(value, str):
        # Match ${VAR} or ${VAR:-default}
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
                # Keep original placeholder, let caller decide how to handle
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
    Server configuration
    
    Note: host and port are specified by Sandbox(server_url=...), not set in config file
    """
    title: str = "Sandbox HTTP Service"
    description: str = ""
    session_ttl: int = 300
    cleanup_interval: int = 60
    log_level: str = "INFO"


@dataclass
class ResourceConfig:
    """Resource configuration"""
    name: str
    enabled: bool = True
    description: str = ""
    backend_class: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WarmupConfig:
    """Warmup configuration"""
    enabled: bool = False
    resources: List[str] = field(default_factory=list)


@dataclass
class SecurityConfig:
    """Security configuration"""
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit_enabled: bool = False
    requests_per_minute: int = 100
    auth_enabled: bool = False
    auth_type: str = "api_key"
    api_key: Optional[str] = None


@dataclass
class SandboxConfig:
    """Complete Sandbox configuration"""
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
    Configuration Loader
    
    Features:
    - Load configuration from JSON files
    - Environment variable substitution
    - Dynamic backend class loading
    - Create configured server instances
    
    Loading process:
    1. Load and parse config file
    2. Expand environment variables
    3. Create HTTPServiceServer instance
    4. Iterate through resources, dynamically load and call server.load_backend()
    5. Iterate through apis, automatically register stateless tools via @register_api_tool decorator
    """
    
    def __init__(self):
        self.config: Optional[SandboxConfig] = None
        self.raw_config: Dict[str, Any] = {}
    
    def load(self, config_path: str) -> SandboxConfig:
        """
        Load configuration file
        
        Args:
            config_path: Path to config file
            
        Returns:
            Parsed configuration object
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            self.raw_config = json.load(f)
        
        # Expand environment variables
        expanded = expand_env_vars(self.raw_config)
        
        # Parse each section of configuration
        self.config = self._parse_config(expanded)
        
        logger.info(f"✅ Loaded config from {config_path}")
        logger.info(f"   - Server: {self.config.server.title}")
        logger.info(f"   - Resources: {list(self.config.resources.keys())}")
        
        return self.config
    
    def load_from_dict(self, config_dict: Dict[str, Any]) -> SandboxConfig:
        """Load configuration from dictionary"""
        self.raw_config = config_dict
        expanded = expand_env_vars(config_dict)
        self.config = self._parse_config(expanded)
        return self.config
    
    def _parse_config(self, data: Dict[str, Any]) -> SandboxConfig:
        """Parse configuration dictionary into configuration object"""
        
        # Server configuration (host/port specified by Sandbox(server_url=...))
        server_data = data.get("server", {})
        server = ServerConfig(
            title=server_data.get("title", "Sandbox HTTP Service"),
            description=server_data.get("description", ""),
            session_ttl=server_data.get("session_ttl", 300),
            cleanup_interval=server_data.get("cleanup_interval", 60),
            log_level=server_data.get("log_level", "INFO")
        )
        
        # Resource configuration
        resources: Dict[str, ResourceConfig] = {}
        for name, res_data in data.get("resources", {}).items():
            # Skip comment fields
            if name.startswith("_"):
                continue
            
            resources[name] = ResourceConfig(
                name=name,
                enabled=res_data.get("enabled", True),
                description=res_data.get("description", ""),
                backend_class=res_data.get("backend_class"),
                config=res_data.get("config", {})
            )
        
        # Tool configuration
        tools: Dict[str, Dict[str, Any]] = {}
        for name, tool_data in data.get("tools", {}).items():
            if name.startswith("_"):
                continue
            tools[name] = tool_data
        
        # Warmup configuration
        warmup_data = data.get("warmup", {})
        warmup = WarmupConfig(
            enabled=warmup_data.get("enabled", False),
            resources=warmup_data.get("resources", [])
        )
        
        # Security configuration
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
        """Get all enabled resources"""
        if not self.config:
            return {}
        return {
            name: res for name, res in self.config.resources.items()
            if res.enabled
        }
    
    def load_class(self, class_path: str) -> Type:
        """
        Dynamically load class
        
        Args:
            class_path: Full path to class, e.g. "sandbox.server.backends.resources.vm.VMBackend"
            
        Returns:
            Class object
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
        Create server instance from configuration

        Loading process:
        1. Create HTTPServiceServer instance
        2. Iterate through resources, dynamically load backend classes and call server.load_backend()
        3. Iterate through apis, automatically register stateless tools via @register_api_tool decorator

        Args:
            host: Server bind address
            port: Server port
        
        Returns:
            Configured HTTPServiceServer instance
        """
        if not self.config:
            raise RuntimeError("No config loaded. Call load() first.")
        
        # Lazy import to avoid circular dependencies
        from .app import HTTPServiceServer
        from .backends.base import BackendConfig
        
        # Get warmup resource list
        warmup_resources = self.get_warmup_resources()

        # Create server (host/port specified by parameters)
        server = HTTPServiceServer(
            host=host,
            port=port,
            title=self.config.server.title,
            session_ttl=self.config.server.session_ttl,
            warmup_resources=warmup_resources
        )
        
        # ====================================================================
        # Load stateful backends (resources)
        # ====================================================================
        for name, res_config in self.get_enabled_resources().items():
            if res_config.backend_class:
                try:
                    # Dynamically load backend class
                    backend_cls = self.load_class(res_config.backend_class)
                    
                    # Create backend configuration
                    backend_config = BackendConfig(
                        enabled=True,
                        default_config=res_config.config,
                        description=res_config.description
                    )
                    
                    # Instantiate backend
                    backend = backend_cls(config=backend_config)
                    
                    # Load backend using new API (automatically scan @tool markers via reflection)
                    registered = server.load_backend(backend)
                    
                    logger.info(f"✅ Loaded backend: {name} ({len(registered)} tools)")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to load backend '{name}': {e}")
            else:
                logger.warning(f"⚠️ Resource '{name}' has no backend_class, skipping")
        
        # ====================================================================
        # Load stateless tools (apis)
        # ====================================================================
        apis_config = self.raw_config.get("apis", {})
        if apis_config:
            self._load_api_tools(server, apis_config)
        
        return server
    
    def _load_api_tools(self, server, apis_config: Dict[str, Any]):
        """
        Load stateless API tools
        
        New mechanism:
        - Tools self-register via @register_api_tool decorator
        - Each tool specifies its own config_key to read
        - Configuration is extracted from apis based on config_key and injected
        
        Args:
            server: HTTPServiceServer instance
            apis_config: apis configuration dictionary
        """
        from .backends.tools import get_all_api_tools
        
        # Get all registered API tools
        api_tools = get_all_api_tools()
        
        if not api_tools:
            logger.info("📦 No API tools registered")
            return
        
        registered_count = 0
        
        for tool_name, tool_info in api_tools.items():
            try:
                # Get configuration needed by this tool
                tool_config = {}
                if tool_info.config_key:
                    tool_config = apis_config.get(tool_info.config_key, {})
                    # Skip comment fields
                    if isinstance(tool_config, dict):
                        tool_config = {k: v for k, v in tool_config.items() if not k.startswith("_")}
                
                # If it's a BaseApiTool instance, inject config first
                if hasattr(tool_info.func, 'set_config'):
                    tool_info.func.set_config(tool_config)
                    logger.debug(f"  📦 Injected config into {tool_name} instance")
                
                # Register tool to server
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
        """Get list of resources that need warmup"""
        if not self.config or not self.config.warmup.enabled:
            return []
        
        # Only return enabled resources
        enabled = set(self.get_enabled_resources().keys())
        return [r for r in self.config.warmup.resources if r in enabled]


# ============================================================================
# Convenience Functions
# ============================================================================

def load_config(config_path: str) -> SandboxConfig:
    """
    Convenience function to load configuration file
    
    Args:
        config_path: Path to config file
        
    Returns:
        Parsed configuration object
    """
    loader = ConfigLoader()
    return loader.load(config_path)


def create_server_from_config(config_path: str, host: str = "0.0.0.0", port: int = 8080):
    """
    Create server from configuration file
    
    Args:
        config_path: Path to config file
        host: Server bind address
        port: Server port
        
    Returns:
        Configured HTTPServiceServer instance
        
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
    Get default configuration template
    
    Note: host/port are specified by Sandbox(server_url=...) or CLI --host/--port
    
    Returns:
        Default configuration dictionary
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
    """Command line entry point"""
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
    
    # Create and start server
    server = loader.create_server(host=args.host, port=args.port)
    print(f"🚀 Starting server on {args.host}:{args.port}")
    server.run()


if __name__ == "__main__":
    main()

