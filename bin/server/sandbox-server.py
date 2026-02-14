#!/usr/bin/env python3
"""
Sandbox Server 启动脚本
可以在项目任何目录执行
"""

import sys
import argparse
import logging
from pathlib import Path

# 获取项目根目录
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# 添加项目根目录到 Python 路径，确保可导入 sandbox 包
sys.path.insert(0, str(PROJECT_ROOT))


def setup_logging(level: str = "INFO"):
    """配置日志"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def find_config_file(config_arg: str) -> Path:
    """
    查找配置文件

    仅支持：
    1. 绝对路径
    2. 相对路径（相对于当前工作目录）
    """
    config_path = Path(config_arg).expanduser()
    if not config_path.is_absolute():
        config_path = Path.cwd() / config_path

    if config_path.exists():
        return config_path

    raise FileNotFoundError(f"配置文件未找到: {config_path}")


def main():
    parser = argparse.ArgumentParser(
        description="启动 Sandbox Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --config /abs/path/to/dev.json
  %(prog)s --config ./configs/dev.json --port 8080
  %(prog)s --host 127.0.0.1 --port 9000
        """
    )

    parser.add_argument(
        "--config", "-c",
        type=str,
        required=True,
        help="配置文件路径（必填，支持绝对路径或相对路径）"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="服务器主机地址 (默认: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=18890,
        help="服务器端口 (默认: 18890)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="日志级别 (默认: INFO)"
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="显示配置信息后退出"
    )

    args = parser.parse_args()

    # 设置日志
    setup_logging(args.log_level)

    # 查找配置文件
    config_path = find_config_file(args.config)

    # 显示启动信息
    print("=" * 80)
    print("🚀 Sandbox Server 启动中...")
    print("=" * 80)
    print(f"📁 项目根目录: {PROJECT_ROOT}")
    print(f"⚙️  配置文件: {config_path}")
    print(f"🌐 服务地址: http://{args.host}:{args.port}")
    print(f"📊 日志级别: {args.log_level}")
    print("=" * 80)
    print()

    # 导入并创建服务器
    try:
        from sandbox.server.config_loader import ConfigLoader

        # 加载配置
        loader = ConfigLoader()
        config = loader.load(str(config_path))

        # 显示配置信息
        if args.show_config:
            print("\n📋 配置信息:")
            print(f"   服务器标题: {config.server.title}")
            print(f"   Session TTL: {config.server.session_ttl}s")
            print(f"\n   已启用的资源 ({len(loader.get_enabled_resources())}):")
            for name, res in loader.get_enabled_resources().items():
                print(f"     ✅ {name}: {res.description}")
            print()
            return

        # 创建服务器（使用标准方式）
        server = loader.create_server(host=args.host, port=args.port)

        # 启动服务器
        print("=" * 80)
        print(f"🌐 访问地址: http://{args.host}:{args.port}")
        print(f"📖 API 文档: http://{args.host}:{args.port}/docs")
        print(f"🔍 健康检查: http://{args.host}:{args.port}/health")
        print()
        print(f"💡 提示: 资源预热请在客户端配置 warmup_resources 参数")
        print(f"   例如: Sandbox(config=SandboxConfig(warmup_resources=['rag']))")
        print("=" * 80)
        print("\n⏳ 服务器正在启动中，请稍候...\n")

        # 使用标准的 server.run() 方法
        # 这会在正确的事件循环中运行，不会有 warmup 问题
        server.run()

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print(f"   请确保已安装所有依赖")
        print(f"   提示: 检查 PYTHONPATH 是否正确设置")
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
