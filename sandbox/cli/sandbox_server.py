#!/usr/bin/env python3
"""
Sandbox Server CLI entrypoint.
"""

import argparse
import logging
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def setup_logging(level: str = "INFO"):
    """配置日志"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def find_config_file(config_arg: str) -> Path:
    """
    查找配置文件

    支持：
    1. 绝对路径
    2. 相对路径（相对于当前目录）
    3. 配置文件名（在标准配置目录查找）
    """
    if os.path.isabs(config_arg):
        config_path = Path(config_arg)
        if config_path.exists():
            return config_path
        raise FileNotFoundError(f"配置文件未找到: {config_arg}")

    possible_paths = [
        Path(config_arg),  # 当前目录
        Path.cwd() / config_arg,  # 当前工作目录
        PROJECT_ROOT / config_arg,  # 项目根目录
        PROJECT_ROOT / "sandbox" / "sandbox" / "configs" / "profiles" / config_arg,
    ]

    for p in possible_paths:
        if p.exists():
            return p

    print(f"❌ 配置文件未找到: {config_arg}")
    print("   尝试过的位置:")
    for p in possible_paths:
        print(f"   - {p}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="启动 Sandbox Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                                    # 使用默认配置 (dev.json)
  %(prog)s --config dev.json                  # 使用开发配置
  %(prog)s --config production.json --port 8080
  %(prog)s --host 127.0.0.1 --port 9000
        """,
    )

    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default="dev.json",
        help="配置文件路径或名称 (默认: dev.json)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="服务器主机地址 (默认: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=18890,
        help="服务器端口 (默认: 18890)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="日志级别 (默认: INFO)",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="显示配置信息后退出",
    )

    args = parser.parse_args()
    setup_logging(args.log_level)

    config_path = find_config_file(args.config)

    print("=" * 80)
    print("🚀 Sandbox Server 启动中...")
    print("=" * 80)
    print(f"📁 项目根目录: {PROJECT_ROOT}")
    print(f"⚙️  配置文件: {config_path}")
    print(f"🌐 服务地址: http://{args.host}:{args.port}")
    print(f"📊 日志级别: {args.log_level}")
    print("=" * 80)
    print()

    try:
        from sandbox.server.config_loader import ConfigLoader

        loader = ConfigLoader()
        config = loader.load(str(config_path))

        if args.show_config:
            print("\n📋 配置信息:")
            print(f"   服务器标题: {config.server.title}")
            print(f"   Session TTL: {config.server.session_ttl}s")
            print(f"\n   已启用的资源 ({len(loader.get_enabled_resources())}):")
            for name, res in loader.get_enabled_resources().items():
                print(f"     ✅ {name}: {res.description}")
            print()
            return

        server = loader.create_server(host=args.host, port=args.port)

        print("=" * 80)
        print(f"🌐 访问地址: http://{args.host}:{args.port}")
        print(f"📖 API 文档: http://{args.host}:{args.port}/docs")
        print(f"🔍 健康检查: http://{args.host}:{args.port}/health")
        print()
        print("💡 提示: 资源预热请在客户端配置 warmup_resources 参数")
        print("   例如: Sandbox(config=SandboxConfig(warmup_resources=['rag']))")
        print("=" * 80)
        print("\n⏳ 服务器正在启动中，请稍候...\n")

        server.run()

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("   请确保已安装所有依赖")
        print("   提示: 检查 PYTHONPATH 是否正确设置")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

