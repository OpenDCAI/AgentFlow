# sandbox/__main__.py
"""
Sandbox 命令行入口

使用方式：

1. 启动服务器：
    python -m sandbox server                     # 默认使用 dev 配置
    python -m sandbox server --config dev        # 指定配置
    python -m sandbox server --config production
    python -m sandbox server --port 8080         # 指定端口
    python -m sandbox server --config dev --show # 显示配置

2. 验证配置（Strict Mode，用于 CI/CD）：
    python -m sandbox validate --config dev      # 验证单个配置
    python -m sandbox validate --all             # 验证所有配置
    python -m sandbox validate --all --strict    # 严格模式
    python -m sandbox validate --all --strict --exit-on-error  # CI/CD 模式
"""

import os
import sys
import argparse
import logging

# 确保可以导入 sandbox
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# 预定义配置文件
# ============================================================================

# 获取 sandbox 目录路径
SANDBOX_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PROFILES = {
    "dev": os.path.join(SANDBOX_DIR, "configs/profiles/dev.json"),
    "development": os.path.join(SANDBOX_DIR, "configs/profiles/dev.json"),
    "prod": os.path.join(SANDBOX_DIR, "configs/profiles/production.json"),
    "production": os.path.join(SANDBOX_DIR, "configs/profiles/production.json"),
    "minimal": os.path.join(SANDBOX_DIR, "configs/profiles/minimal.json"),
}


# ============================================================================
# Server 命令
# ============================================================================

# ============================================================================
# Validate 命令
# ============================================================================

def cmd_validate(args):
    """验证配置文件（Strict Mode）"""
    from sandbox.server.validator import (
        validate_config, 
        validate_all_configs, 
        print_validation_report
    )
    
    if args.all:
        # 验证所有配置
        results = validate_all_configs(strict=args.strict)
        
        if not results:
            print("❌ No config files found in profiles directory")
            sys.exit(1)
        
        all_valid = print_validation_report(results)
        
        if args.exit_on_error and not all_valid:
            sys.exit(1)
    
    elif args.config:
        # 验证单个配置
        config_path = args.config
        if config_path in CONFIG_PROFILES:
            config_path = CONFIG_PROFILES[config_path]
        
        result = validate_config(config_path, strict=args.strict)
        
        print(f"\n{result.summary()}\n")
        
        if args.exit_on_error and not result.is_valid:
            sys.exit(1)
    
    else:
        print("❌ Please specify --config or --all")
        sys.exit(1)


# ============================================================================
# Server 命令
# ============================================================================

def cmd_server(args):
    """启动服务器"""
    from sandbox.server.config_loader import ConfigLoader, create_server_from_config
    
    # 解析配置文件路径
    config_path = args.config
    if config_path in CONFIG_PROFILES:
        config_path = CONFIG_PROFILES[config_path]
    
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        print(f"\n可用的预设配置: {list(CONFIG_PROFILES.keys())}")
        sys.exit(1)
    
    # 加载配置
    loader = ConfigLoader()
    config = loader.load(config_path)
    
    # 显示配置
    if args.show:
        print("\n" + "=" * 60)
        print("📋 Sandbox Server Configuration")
        print("=" * 60)
        print(f"\n🏷️  Title: {config.server.title}")
        print(f"📁 Config: {config_path}")
        print(f"🔧 Session TTL: {config.server.session_ttl}s")
        print(f"📝 Log Level: {config.server.log_level}")
        
        print(f"\n📦 Resources ({len(config.resources)}):")
        for name, res in config.resources.items():
            status = "✅" if res.enabled else "❌"
            print(f"   {status} {name}: {res.description or res.backend_class}")
        
        apis = list(loader.raw_config.get('apis', {}).keys())
        print(f"\n🔌 API Tools: {apis}")
        
        if config.warmup.enabled:
            print(f"\n🔥 Warmup: {config.warmup.resources}")
        
        print("\n" + "=" * 60)
        return
    
    # 验证配置
    if args.validate:
        print(f"✅ Configuration is valid: {config_path}")
        return
    
    # 创建并启动服务器
    host = args.host
    port = args.port
    
    server = loader.create_server(host=host, port=port)
    
    print("\n" + "=" * 60)
    print("🚀 Sandbox Server Starting")
    print("=" * 60)
    print(f"\n   URL:     http://{host}:{port}")
    print(f"   Config:  {config_path}")
    print(f"   Title:   {config.server.title}")
    print(f"\n   Health:  http://{host}:{port}/health")
    print(f"   Docs:    http://{host}:{port}/docs")
    print("\n" + "=" * 60)
    print("\n按 Ctrl+C 停止服务器\n")
    
    server.run()


# ============================================================================
# 主入口
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        prog="python -m sandbox",
        description="Sandbox - HTTP Service for AI Agents"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # ========================================================================
    # server 子命令
    # ========================================================================
    server_parser = subparsers.add_parser(
        "server",
        help="Start Sandbox HTTP Server",
        description="Start the Sandbox HTTP server with specified configuration"
    )
    server_parser.add_argument(
        "--config", "-c",
        default="dev",
        help="Config profile (dev/prod/minimal) or path to config file (default: dev)"
    )
    server_parser.add_argument(
        "--host", "-H",
        default="0.0.0.0",
        help="Server bind address (default: 0.0.0.0)"
    )
    server_parser.add_argument(
        "--port", "-p",
        type=int,
        default=8080,
        help="Server port (default: 8080)"
    )
    server_parser.add_argument(
        "--validate",
        action="store_true",
        help="Only validate config, don't start server"
    )
    server_parser.add_argument(
        "--show",
        action="store_true",
        help="Show parsed configuration"
    )
    server_parser.set_defaults(func=cmd_server)
    
    # ========================================================================
    # validate 子命令
    # ========================================================================
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate configuration files (Strict Mode for CI/CD)",
        description="Validate backend_class paths, @tool decorators, and API tools registration"
    )
    validate_parser.add_argument(
        "--config", "-c",
        help="Config profile (dev/prod/minimal) or path to config file"
    )
    validate_parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Validate all config files in profiles directory"
    )
    validate_parser.add_argument(
        "--strict", "-s",
        action="store_true",
        help="Strict mode: treat warnings as errors"
    )
    validate_parser.add_argument(
        "--exit-on-error",
        action="store_true",
        help="Exit with non-zero code if validation fails (for CI/CD)"
    )
    validate_parser.set_defaults(func=cmd_validate)
    
    # ========================================================================
    # 解析参数
    # ========================================================================
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    
    # 执行对应命令
    args.func(args)


if __name__ == "__main__":
    main()

